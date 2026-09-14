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
import filecmp
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
REGISTERED, PILOT = "REGISTERED", "PILOT"


def load_matrix(path):
    doc = json.loads(Path(path).read_text())
    return doc if isinstance(doc, list) else doc.get("cells", [])


def reduce_observation(o):
    """The comparable form of an observation, as adapter/SPEC.md section 6 defines it."""
    intoto = {}
    for a in o["intoto"]["attestations"]:
        if a["dsse"] != "pass":
            intoto[a["attestation"]] = a["dsse"]
        elif a["statement"] != "valid":
            intoto[a["attestation"]] = a["statement"]
        elif any(v != "match" for v in a["subjects"].values()):
            intoto[a["attestation"]] = {k: v for k, v in a["subjects"].items() if v != "match"}
    binding = {a["attestation"]: a["binding"] for a in o["binding"]["attestations"] if a["binding"] != "pass"}
    return {"gateway": {"ok": o["gateway"]["ok"], "statuses": o["gateway"]["statuses"]},
            "intoto": {"pass": o["intoto"]["pass"], "failures": intoto},
            "binding": {"pass": o["binding"]["pass"], "failures": binding},
            "combined": o["combined"]}


def marker_problems(marker, gateway_digest, label):
    problems = []
    if not isinstance(marker, dict):
        return ["no attempt marker"]
    for key in ("attemptId", "label", "gatewaySha256", "pinsRawSha256", "adapterKeyid", "cells", "startedAt"):
        if key not in marker:
            problems.append("marker lacks %s" % key)
    if problems:
        return problems
    if marker["label"] != label:
        problems.append("marker label is %s, not %s" % (marker["label"], label))
    if marker["gatewaySha256"] != gateway_digest:
        problems.append("marker's gateway digest is not this binary's")
    if marker["pinsRawSha256"] != pinning.raw_sha256():
        problems.append("marker's pins digest is not the current harness/PINS.json's")
    if marker["adapterKeyid"] != pinning.adapter_keyid():
        problems.append("marker's adapter key id is not the pinned key's")
    if sorted(marker["cells"]) != sorted(constructions.CELLS):
        problems.append("marker's cell set is not the registered constructions")
    if not isinstance(marker["attemptId"], str) or not re.fullmatch(r"[0-9a-f]{32}", marker["attemptId"]):
        problems.append("marker attempt id is not a 32-hex token")
    return problems


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(same_tree(Path(a) / d, Path(b) / d) for d in cmp.common_dirs)


def cells_are_the_registered_constructions(root, failures):
    with tempfile.TemporaryDirectory() as tmp:
        for cid in constructions.CELLS:
            built = constructions.build(cid, tmp)
            kept = Path(root) / "cells" / cid
            if not kept.is_dir():
                failures.append("cell %s is missing" % cid)
            elif not same_tree(built, kept):
                failures.append("cell %s is not the registered construction" % cid)
    present = {p.name for p in (Path(root) / "cells").iterdir() if p.is_dir()} if (Path(root) / "cells").is_dir() else set()
    for extra in sorted(present - set(constructions.CELLS)):
        failures.append("cell %s is not registered" % extra)


def observation_ok(o, cid):
    try:
        return (o["cell"] == cid and isinstance(o["gateway"]["ok"], bool) and isinstance(o["gateway"]["findings"], list)
                and isinstance(o["gateway"]["statuses"], list) and isinstance(o["intoto"]["pass"], bool) and isinstance(o["intoto"]["attestations"], list)
                and isinstance(o["binding"]["pass"], bool) and isinstance(o["binding"]["attestations"], list)
                and o["combined"] in ("pass", "fail")
                and o["combined"] == ("pass" if (o["gateway"]["ok"] and o["intoto"]["pass"] and o["binding"]["pass"]) else "fail")
                and all(a["dsse"] is not None and ("subjects" in a) for a in o["intoto"]["attestations"])
                and all(isinstance(a.get("binding"), str) for a in o["binding"]["attestations"]))
    except (KeyError, TypeError):
        return False


def adjudicate(matrix_cells, observed):
    rows = []
    for cell in matrix_cells:
        o = observed.get(cell["id"])
        if o is None:
            rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "verdict": "unobserved"})
            continue
        got = reduce_observation(o)
        expected = cell["expected"]
        verdict = "holds" if got == expected else "diverges"
        rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "verdict": verdict, "expected": expected, "observed": got})
    return rows


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
    validity = []
    cells_are_the_registered_constructions(root, validity)
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
        seen = [o.get("cell") for o in doc.get("cells", [])]
        if sorted(seen) != sorted(constructions.CELLS) or len(seen) != len(set(seen)):
            validity.append("the observations do not cover exactly the registered cells once each")
        for o in doc.get("cells", []):
            if not observation_ok(o, o.get("cell")):
                validity.append("the observation of %s is not a complete record" % o.get("cell"))
                break
            observed[o["cell"]] = o
    matrix = load_matrix(STUDY / "harness" / "MATRIX.json") + holdout
    rows, gates, decision = [], [], "pipeline-invalid"
    if not validity:
        rows = adjudicate(matrix, observed)
        unobserved = [r["id"] for r in rows if r["verdict"] == "unobserved"]
        if unobserved:
            validity.append("unobserved registered cells: %s" % ", ".join(unobserved[:3]))
        else:
            gates = [r["id"] for r in rows if r["role"] == "control-gate" and r["verdict"] != "holds"]
            diverging = [r["id"] for r in rows if r["role"] == "endpoint" and r["verdict"] == "diverges"]
            decision = "control-gate-failed" if gates else ("R1 holds" if not diverging else "R1 falsified")
    with open(root / "ADJUDICATION.json", "x") as f:
        f.write(json.dumps({"label": PILOT if args.pilot else REGISTERED, "attemptId": marker["attemptId"], "gatewaySha256": gateway_digest,
                            "holdoutIncluded": bool(holdout), "decision": decision, "validityFailures": validity, "gateFailures": gates, "cells": rows}, indent=1))
    print("%s: %s (%d cells, %d diverge, %d validity failures, %d gate failures)" % (PILOT if args.pilot else REGISTERED, decision, len(rows),
          sum(1 for r in rows if r["verdict"] == "diverges"), len(validity), len(gates)))
    for v in validity[:6]:
        print("  ", v)


if __name__ == "__main__":
    main()
