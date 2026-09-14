"""Adjudicate the registered cells against the observations of one attempt.

Before any observation is read: the pins (harness/pins.py) against the tree and the
environment; the attempt marker parsed and matched (label, gateway digest, pins digest,
adapter key id, cell set); the attempt's cells rebuilt from the baseline by the registered
constructions and compared byte for byte; the observations file bound to the pinned gateway
binary and covering exactly the registered cells, each observation complete. Any shortfall is
pipeline-invalid. Then the control gates (the positive control passing all three layers, the
negative control failing exactly where registered), then every registered cell: the observed
per-layer outcomes, reduced as adapter/SPEC.md section 6 states, must equal the registered
ones; any divergence falsifies R1.

Run: python harness/score.py --attempt-root DIR --gateway BIN [--include-holdout] [--pilot]
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402
import run_layers  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "adapter"))
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
REGISTERED, PILOT = "REGISTERED", "PILOT"


def load_matrix(path):
    doc = json.loads(Path(path).read_text())
    return doc if isinstance(doc, list) else doc.get("cells", [])


def reduce_observation(o):
    """The comparable form of an observation, as adapter/SPEC.md section 6 defines it: per attestation the
    first failure; subjects reduced per name to the first outcome that is not `match`."""
    intoto = {}
    for a in o["intoto"]["attestations"]:
        if a["dsse"] != "pass":
            intoto[a["attestation"]] = a["dsse"]
        elif a["statement"] != "valid":
            intoto[a["attestation"]] = a["statement"]
        else:
            named = verify_attestation.per_name(a["subjects"])
            # a valid statement with no subject outcome does not pass (SPEC.md section 6) and reduces to an empty map
            if not a["subjects"] or any(v != "match" for v in named.values()):
                intoto[a["attestation"]] = {k: v for k, v in named.items() if v != "match"}
    binding = {a["attestation"]: a["binding"] for a in o["binding"]["attestations"] if a["binding"] != "pass"}
    return {"gateway": {"ok": o["gateway"]["ok"], "statuses": o["gateway"]["statuses"]},
            "intoto": {"pass": o["intoto"]["pass"], "failures": intoto},
            "binding": {"pass": o["binding"]["pass"], "failures": binding},
            "combined": o["combined"]}


def marker_problems(marker, gateway_digest, label):
    problems = []
    if not isinstance(marker, dict):
        return ["no attempt marker"]
    for key in ("attemptId", "attemptRoot", "label", "gatewaySha256", "pinsRawSha256", "adapterKeyid", "python", "cells", "startedAt"):
        if key not in marker:
            problems.append("marker lacks %s" % key)
    if problems:
        return problems
    if marker["label"] != label:
        problems.append("marker label is %s, not %s" % (marker["label"], label))
    if marker["python"] != sys.version.split()[0]:
        problems.append("marker's interpreter %s is not this interpreter %s" % (marker["python"], sys.version.split()[0]))
    if label == REGISTERED and Path(marker["attemptRoot"]).resolve() != (STUDY / "results" / "primary-attempt-001").resolve():
        problems.append("a registered attempt's root is results/primary-attempt-001, not %s" % marker["attemptRoot"])
    if marker["gatewaySha256"] != gateway_digest:
        problems.append("marker's gateway digest is not this binary's")
    if marker["pinsRawSha256"] != pinning.raw_sha256():
        problems.append("marker's pins digest is not the current harness/PINS.json's")
    if marker["adapterKeyid"] != pinning.adapter_keyid():
        problems.append("marker's adapter key id is not the pinned key's")
    expected_cells = sorted(constructions.ALL_CELLS) if label == REGISTERED else sorted(constructions.CELLS)
    if sorted(marker["cells"]) != expected_cells:
        problems.append("marker's cell set is not the registered constructions (%s)" % ("locked and holdout" if label == REGISTERED else "locked"))
    if not isinstance(marker["attemptId"], str) or not re.fullmatch(r"[0-9a-f]{32}", marker["attemptId"]):
        problems.append("marker attempt id is not a 32-hex token")
    return problems


def tree_map(root):
    """Every entry under a tree by relative path: 'd' for a directory, or the file's SHA-256; a symbolic link is refused."""
    out = {}
    for p in sorted(Path(root).rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            raise RuntimeError("symbolic link in %s: %s" % (root, rel))
        out[rel] = "d" if p.is_dir() else pinning.sha256_file(p)
    return out


def same_tree(a, b):
    """Byte-for-byte equality of two trees: the same paths, the same kinds, the same file bytes."""
    return tree_map(a) == tree_map(b)


def cells_are_the_registered_constructions(root, failures, cell_ids, unconstructed=()):
    """Every expected cell present and byte for byte the registered construction; no other cell present. Returns the
    rebuilt cells' digests. A holdout cell the runner recorded as unconstructed is expected absent and is not rebuilt."""
    digests = {}
    with tempfile.TemporaryDirectory() as tmp:
        for cid in cell_ids:
            kept = Path(root) / "cells" / cid
            if cid in unconstructed:
                if kept.exists():
                    failures.append("cell %s is recorded unconstructed but is present" % cid)
                continue
            try:
                built = constructions.build(cid, tmp)
            except Exception as e:  # noqa: BLE001 -- a construction that cannot be rebuilt is a validity failure, not a crash
                failures.append("cell %s cannot be rebuilt (%s)" % (cid, type(e).__name__))
                continue
            if not kept.is_dir():
                failures.append("cell %s is missing" % cid)
            elif not same_tree(built, kept):
                failures.append("cell %s is not the registered construction" % cid)
            digests[cid] = run_layers.tree_digest(built)
    present = {p.name for p in (Path(root) / "cells").iterdir() if p.is_dir()} if (Path(root) / "cells").is_dir() else set()
    for extra in sorted(present - set(cell_ids)):
        failures.append("cell %s is not registered" % extra)
    return digests


def required_attestations(cell_dir):
    """One attestation per receipt file the cell's store holds, in the ceremony's order."""
    names = []
    receipts = Path(cell_dir) / "store" / "receipts"
    for session in sorted(p for p in receipts.iterdir() if p.is_dir()):
        for f in sorted(session.glob("*.json"), key=lambda p: int(p.stem)):
            names.append("%s/%s.dsse.json" % (session.name, f.stem))
    return names


def observation_problems(o, cid, cell_dir, snapshot):
    """Every way an observation falls short of a complete record of the three layers over the registered cell."""
    problems = []
    try:
        if o["cell"] != cid:
            problems.append("names another cell")
        if o.get("cellSha256") != snapshot:
            problems.append("was not made over the registered construction (snapshot digest differs)")
        g, i, b = o["gateway"], o["intoto"], o["binding"]
        if not isinstance(g["ok"], bool) or not isinstance(g["findings"], list):
            problems.append("gateway record incomplete")
        else:
            statuses = sorted({f.get("status") for f in g["findings"]})
            if g["statuses"] != statuses:
                problems.append("gateway statuses are not the findings' statuses")
            if not all(isinstance(f.get("status"), str) and isinstance(f.get("sessionId"), str) for f in g["findings"]):
                problems.append("a gateway finding is not a finding")
            # the gateway's rule (verify.go): ok is false exactly when some finding's status is not ok
            if g["ok"] != all(f.get("status") == "ok" for f in g["findings"]):
                problems.append("gateway ok does not follow from its findings")
            # the gateway emits one finding per receipt file it read (by callIndex, or by file when unreadable), plus session findings
            per_receipt = [f for f in g["findings"] if "callIndex" in f or "file" in f]
            if len(per_receipt) < len(required_attestations(cell_dir)):
                problems.append("gateway findings do not cover every stored receipt")
        required = required_attestations(cell_dir)
        for layer, key, codes, ok_code in ((i, "dsse", verify_attestation.DSSE_CODES, None), (b, "binding", verify_binding.CODES, None)):
            names = [a.get("attestation") for a in layer["attestations"]]
            if names != required:
                problems.append("%s records are not one per stored receipt in order" % key)
            for a in layer["attestations"]:
                if a.get(key) not in codes:
                    problems.append("%s code %r is not in the vocabulary" % (key, a.get(key)))
        for a in i["attestations"]:
            if a["dsse"] == "pass":
                if a.get("statement") not in verify_attestation.STATEMENT_CODES:
                    problems.append("statement code %r is not in the vocabulary" % a.get("statement"))
                if a["statement"] == "valid":
                    if not isinstance(a["subjects"], list) or not all(isinstance(x, list) and len(x) == 2 and x[1] in verify_attestation.SUBJECT_OUTCOMES for x in a["subjects"]):
                        problems.append("subject outcomes of %s are not a list of [name, outcome]" % a["attestation"])
                elif a["subjects"]:
                    problems.append("subjects recorded for an attestation whose statement was not valid")
            elif a.get("statement") is not None or a.get("subjects"):
                problems.append("statement or subjects recorded for an attestation whose envelope failed")
        if i["pass"] != all(verify_attestation.attestation_passes(a) for a in i["attestations"]):
            problems.append("intoto pass does not follow from its attestations")
        if b["pass"] != all(a["binding"] == "pass" for a in b["attestations"]):
            problems.append("binding pass does not follow from its attestations")
        if o["combined"] != ("pass" if (g["ok"] and i["pass"] and b["pass"]) else "fail"):
            problems.append("combined verdict does not follow from the layers")
    except (KeyError, TypeError, AttributeError, ValueError) as e:
        problems.append("not a complete record (%s)" % type(e).__name__)
    return problems


def adjudicate(matrix_cells, observed, unconstructed=None):
    rows = []
    for cell in matrix_cells:
        o = observed.get(cell["id"])
        if unconstructed and cell["id"] in unconstructed:
            rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "verdict": "unconstructed", "error": unconstructed[cell["id"]]})
            continue
        if o is None:
            rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "verdict": "unobserved"})
            continue
        got = reduce_observation(o)
        expected = cell["expected"]
        verdict = "holds" if got == expected else "diverges"
        rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "verdict": verdict, "expected": expected, "observed": got})
    return rows


def write_once(root, name, payload):
    with open(Path(root) / name, "x") as f:
        f.write(json.dumps(payload, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--gateway", required=True)
    ap.add_argument("--include-holdout", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    if (root / "ADJUDICATION.json").exists():
        sys.exit("refusing: %s already holds an adjudication" % root)
    pins = pinning.load()
    problems = pinning.problems(pins, args.gateway, require_all=not args.pilot)
    gateway_digest = pinning.sha256_file(args.gateway) if Path(args.gateway).is_file() else None
    marker = json.loads((root / "ATTEMPT.json").read_text()) if (root / "ATTEMPT.json").exists() else None
    problems += marker_problems(marker, gateway_digest, PILOT if args.pilot else REGISTERED)
    if problems:
        sys.exit("refusing to adjudicate %s:\n  " % root + "\n  ".join(problems))
    holdout = load_matrix(STUDY / "harness" / "MATRIX-HOLDOUT.json") if args.include_holdout else []
    if args.include_holdout and not holdout:
        sys.exit("refusing: --include-holdout with an empty holdout matrix")
    if not args.pilot and not holdout:
        sys.exit("refusing: a registered adjudication includes the holdout")
    locked = load_matrix(STUDY / "harness" / "MATRIX.json")
    cell_ids = sorted(constructions.ALL_CELLS) if holdout else sorted(constructions.CELLS)
    if holdout and {c["id"] for c in holdout} != set(constructions.HOLDOUT_CELLS):
        sys.exit("refusing: the holdout matrix and the holdout constructions are not the same set")
    if {c["id"] for c in locked} != set(constructions.CELLS):
        sys.exit("refusing: the locked matrix and the locked constructions are not the same set")
    if set(constructions.CELLS) & set(constructions.HOLDOUT_CELLS):
        sys.exit("refusing: the two strata share a cell id")
    validity = []
    # a holdout construction that raised inside the registered attempt is recorded by the runner and reported, not adjudicated
    unconstructed = {}
    if (root / "HOLDOUT-CONSTRUCTION.json").exists():
        unconstructed = json.loads((root / "HOLDOUT-CONSTRUCTION.json").read_text()).get("failed", {})
        for cid in unconstructed:
            if cid not in constructions.HOLDOUT_CELLS:
                validity.append("cell %s is recorded unconstructed but is not a holdout cell" % cid)
    snapshots = cells_are_the_registered_constructions(root, validity, cell_ids, unconstructed)
    obs_path = root / "OBSERVATIONS.json"
    observed = {}
    if not obs_path.exists():
        validity.append("no observations")
    else:
        doc = json.loads(obs_path.read_text())
        if doc.get("attemptId") != marker["attemptId"]:
            validity.append("the observations are not this attempt's")
        if doc.get("gatewaySha256") != gateway_digest:
            validity.append("the observations were made with another gateway binary")
        if doc.get("python") != marker["python"]:
            validity.append("the observations were made under another interpreter")
        if doc.get("trustedKeySha256") != pinning.sha256_file(STUDY / "fixtures" / "baseline" / "attestations" / "adapter.pubkey.json"):
            validity.append("the observations were made under another trusted key file")
        seen = [o.get("cell") for o in doc.get("cells", [])]
        if sorted(seen) != [c for c in cell_ids if c not in unconstructed] or len(seen) != len(set(seen)):
            validity.append("the observations do not cover exactly the registered cells once each")
        for o in doc.get("cells", []):
            cid = o.get("cell")
            if cid in snapshots:
                for p in observation_problems(o, cid, root / "cells" / cid, snapshots[cid]):
                    validity.append("observation of %s: %s" % (cid, p))
            observed[cid] = o
    rows, holdout_rows, gates, decision = [], [], [], "pipeline-invalid"
    if not validity:
        rows = adjudicate(locked, observed)
        holdout_rows = adjudicate(holdout, observed, unconstructed) if holdout else []
        unobserved = [r["id"] for r in rows + holdout_rows if r["verdict"] == "unobserved"]
        if unobserved:
            validity.append("unobserved registered cells: %s" % ", ".join(unobserved[:3]))
        else:
            gates = [r["id"] for r in rows if r["role"] == "control-gate" and r["verdict"] != "holds"]
            diverging = [r["id"] for r in rows if r["role"] == "endpoint" and r["verdict"] == "diverges"]
            # the locked stratum alone decides R1; the holdout reports beside it
            decision = "control-gate-failed" if gates else ("R1 holds" if not diverging else "R1 falsified")
    write_once(root, "ADJUDICATION.json", {"label": PILOT if args.pilot else REGISTERED, "attemptId": marker["attemptId"], "gatewaySha256": gateway_digest,
                                           "holdoutIncluded": bool(holdout), "decision": decision, "validityFailures": validity, "gateFailures": gates,
                                           "cells": rows, "holdout": {"cells": holdout_rows, "diverging": [r["id"] for r in holdout_rows if r["verdict"] == "diverges"],
                                                                      "unconstructed": sorted(unconstructed), "note": "the reviewer's stratum: reported, deciding nothing"}})
    print("%s: %s (%d locked cells, %d diverge; holdout %d cells, %d diverge; %d validity failures, %d gate failures)" % (
        PILOT if args.pilot else REGISTERED, decision, len(rows), sum(1 for r in rows if r["verdict"] == "diverges"), len(holdout_rows),
        sum(1 for r in holdout_rows if r["verdict"] == "diverges"), len(validity), len(gates)))
    for v in validity[:6]:
        print("  ", v)


if __name__ == "__main__":
    main()
