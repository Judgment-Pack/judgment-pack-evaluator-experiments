"""Adjudicate the registered cells against the observations of one attempt.

Before any observation is read: the pins (harness/pins.py) against the tree, the environment
and the executing code; for a registered adjudication the root being scored is the literal
primary root; the attempt marker parsed and matched (root, label, gateway digest, pins digest,
adapter key id, interpreter, cell set); the attempt's cells rebuilt from the baseline by the
registered constructions and compared byte for byte (typed tree: paths, kinds, file digests);
the observations file bound to the attempt, the pinned gateway binary, the interpreter and the
trusted-key file and covering exactly the registered cells; each observation a complete,
self-consistent record of the three layers (shapes and vocabularies), bound to the rebuilt
cell's digest, and equal to what the pinned apparatus produces when the three layers are run
again over the rebuilt cell. Any shortfall is pipeline-invalid. Then the control gates (the
positive control passing all three layers, the negative control failing exactly where
registered), then every locked cell: the observed per-layer outcomes, reduced as
adapter/SPEC.md section 6 states, must equal the registered ones; any divergence in a locked
endpoint cell falsifies R1. The holdout stratum is adjudicated by the same comparison and
reported in its own section; it decides nothing.

Run: python harness/score.py --attempt-root DIR --gateway BIN [--include-holdout] [--pilot]
"""
import os
import sys

# --- the trusted bootstrap, run only when this file is the entry point of a process (harness/guard.py, PREREGISTRATION.md
# section 2); imported as a module by another harness process, this file inherits that process's established resolution ---
if __name__ == "__main__":
    # --- the trusted bootstrap, with os and sys alone (harness/guard.py, PREREGISTRATION.md section 2) ---
    # a fresh, empty bytecode-cache prefix of this process's own, whatever the environment inherited, and no writes
    sys.dont_write_bytecode = True
    for _attempt in range(10000):
        _d = os.path.join(os.environ.get("TMPDIR") or "/tmp", "study022-pycache-%d-%d" % (os.getpid(), _attempt))
        try:
            os.mkdir(_d, 0o700)
        except FileExistsError:
            continue
        sys.pycache_prefix = _d
        break
    else:
        raise SystemExit("refusing to start: no empty bytecode-cache prefix could be made under %s" % (os.environ.get("TMPDIR") or "/tmp"))
    _ORIGINAL_PATH = list(sys.path)
    _GUARD_DIR = os.path.dirname(os.path.realpath(__file__))
    _STUDY = os.path.dirname(_GUARD_DIR)
    # import resolution restricted to the interpreter's own library -- its pure-Python directory and its extension directory,
    # located from the os module the interpreter loaded at start-up; nothing else, in no inherited order -- until the guard
    # has verified everything else (the original path is judged as data by the guard, then a canonical path is set)
    _LIBRARY = os.path.dirname(os.path.realpath(os.__file__))
    sys.path[:] = [_LIBRARY, os.path.join(_LIBRARY, "lib-dynload")]
    import types  # noqa: E402 -- the interpreter's library

    # the trusted guard, compiled from its bytes by exact path: no module-name resolution, no cache
    _GUARD_FILE = os.path.join(_GUARD_DIR, "guard.py")
    with open(_GUARD_FILE, "rb") as _f:
        _code = compile(_f.read(), _GUARD_FILE, "exec")
    guard = types.ModuleType("guard")
    guard.__file__ = _GUARD_FILE
    exec(_code, guard.__dict__)
    sys.modules["guard"] = guard
    guard.establish(_STUDY, _ORIGINAL_PATH)  # puts the study roots on the import path when every check has passed

import tempfile  # noqa: E402

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402
import run_layers  # noqa: E402
from marker import marker_problems  # noqa: E402,F401
from trees import same_tree, tree_digest, typed_tree  # noqa: E402,F401
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "adapter"))
import storewalk  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
PRIMARY_ROOT = constructions.PRIMARY_ROOT
PILOT, REGISTERED = "PILOT", "REGISTERED"

# the gateway's finding vocabulary and shapes, as verify.go at the pinned commit emits them (its SPEC.md sections 1.4 and 4)
GATEWAY_STATUSES = frozenset(("artifact-mismatch", "artifact-missing", "authority-mismatch", "chain-broken", "citation-unresolved", "count-exceeds-seal",
                              "decision-record-mismatch", "key-mismatch", "malformed", "misfiled", "ok", "record-citation-malformed",
                              "record-citation-unresolved", "sealed-session-missing", "sequence-broken", "signature-mismatch", "tail-rollback",
                              "unregistered-session", "unsupported-version"))
RECORD_STATUSES = frozenset(("record-citation-malformed", "record-citation-unresolved"))
JOIN_STATUSES = frozenset(("citation-unresolved", "decision-record-mismatch"))
CHAIN_STATUSES = frozenset(("sequence-broken", "chain-broken"))
SESSION_STATUSES = frozenset(("unregistered-session", "sealed-session-missing", "tail-rollback", "count-exceeds-seal"))
COUNTED_STATUSES = frozenset(("tail-rollback", "count-exceeds-seal"))
SHA256_PREFIXED = re.compile(r"^sha256:[0-9a-f]{64}$")


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


def rebuild_cells(root, failures, cell_ids, unconstructed, tmp, registered=None):
    """Every expected cell present and byte for byte the registered construction; no other cell present. Returns
    {cell id: (rebuilt path, typed-tree digest)}. A holdout cell the runner recorded as unconstructed is expected absent."""
    rebuilt = {}
    for cid in cell_ids:
        kept = Path(root) / "cells" / cid
        if cid in unconstructed:
            if kept.exists() or kept.is_symlink():
                failures.append("cell %s is recorded unconstructed but is present" % cid)
            continue
        try:
            built = constructions.build(cid, tmp, registered)
        except Exception as e:  # noqa: BLE001 -- a construction that cannot be rebuilt is a validity failure, not a crash
            failures.append("cell %s cannot be rebuilt (%s)" % (cid, type(e).__name__))
            continue
        try:
            if not same_tree(built, kept):
                failures.append("cell %s is not the registered construction" % cid)
                continue
        except (OSError, RuntimeError) as e:
            failures.append("cell %s cannot be compared (%s)" % (cid, e))
            continue
        rebuilt[cid] = (built, tree_digest(built))
    cells_dir = Path(root) / "cells"
    present = set(p.name for p in cells_dir.iterdir()) if cells_dir.is_dir() else set()
    for extra in sorted(present - set(cell_ids)):
        failures.append("cell %s is not registered" % extra)
    return rebuilt


def finding_problem(f):
    """One gateway finding against the shapes verify.go emits: receipt findings by call index or by file, chain
    findings with a null call index, session findings (counted for the two seal-count statuses), record findings
    by record digest. Returns a problem string or None."""
    if not isinstance(f, dict) or not isinstance(f.get("status"), str) or f["status"] not in GATEWAY_STATUSES:
        return "a finding outside the gateway's vocabulary"
    keys = set(f)
    if "recordDigest" in f:
        if keys != {"recordDigest", "status"} or not isinstance(f["recordDigest"], str) or not SHA256_PREFIXED.fullmatch(f["recordDigest"]) \
                or f["status"] not in RECORD_STATUSES:
            return "a record finding of the wrong shape"
        return None
    if not isinstance(f.get("sessionId"), str):
        return "a session-scoped finding without a session id"
    if "file" in f:
        if keys != {"sessionId", "file", "status"} or not isinstance(f["file"], str) or f["status"] in RECORD_STATUSES | SESSION_STATUSES | CHAIN_STATUSES:
            return "a receipt finding by file of the wrong shape"
        return None
    if "callIndex" in f:
        if keys != {"sessionId", "callIndex", "status"}:
            return "a receipt finding of the wrong shape"
        ci = f["callIndex"]
        if ci is None:
            return None if f["status"] in CHAIN_STATUSES else "a null call index outside a chain finding"
        if isinstance(ci, bool) or not isinstance(ci, int) or ci < 0 or f["status"] in RECORD_STATUSES | SESSION_STATUSES | CHAIN_STATUSES:
            return "a receipt finding with a call index or status of the wrong shape"
        return None
    if f["status"] not in SESSION_STATUSES:
        return "a session finding with a status that is not a session status"
    if f["status"] in COUNTED_STATUSES:
        if keys != {"sessionId", "status", "have", "sealed"} or not all(isinstance(f[k], int) and not isinstance(f[k], bool) for k in ("have", "sealed")):
            return "a counted session finding of the wrong shape"
    elif keys != {"sessionId", "status"}:
        return "a session finding of the wrong shape"
    return None


def required_attestations(cell_dir):
    """One attestation per receipt file the cell's store holds, in the ceremony's order (the gateway's enumeration)."""
    return ["%s/%s.dsse.json" % (session, stem) for session, stem, _ in storewalk.stored_receipts(Path(cell_dir) / "store")]


def observation_problems(o, cid, cell_dir, snapshot):
    """Every way an observation falls short of a complete, self-consistent record of the three layers over the registered cell."""
    problems = []
    try:
        if o["cell"] != cid:
            problems.append("names another cell")
        if o.get("cellSha256") != snapshot:
            problems.append("was not made over the registered construction (snapshot digest differs)")
        g, i, b = o["gateway"], o["intoto"], o["binding"]
        stored = storewalk.stored_receipts(Path(cell_dir) / "store")
        required = ["%s/%s.dsse.json" % (session, stem) for session, stem, _ in stored]
        sessions = {session for session, _, _ in stored}
        # the gateway layer
        if not isinstance(g.get("ok"), bool) or not isinstance(g.get("findings"), list) or not isinstance(g.get("statuses"), list):
            problems.append("gateway record incomplete")
        else:
            for f in g["findings"]:
                p = finding_problem(f)
                if p:
                    problems.append("gateway finding %r: %s" % (f, p))
            if g["statuses"] != sorted({f.get("status") for f in g["findings"] if isinstance(f, dict)}):
                problems.append("gateway statuses are not the findings' statuses")
            # the gateway's rule (verify.go): ok is false exactly when some finding's status is not ok
            if g["ok"] != all(isinstance(f, dict) and f.get("status") == "ok" for f in g["findings"]):
                problems.append("gateway ok does not follow from its findings")
            # one receipt-level finding per stored receipt file (by call index outside the joins, or by file), each in a stored session
            receipt_level = [f for f in g["findings"] if isinstance(f, dict) and ("file" in f or (isinstance(f.get("callIndex"), int)
                             and not isinstance(f.get("callIndex"), bool) and f.get("status") not in JOIN_STATUSES))]
            if len(receipt_level) != len(required):
                problems.append("gateway receipt-level findings are not one per stored receipt file")
            if any(f.get("sessionId") not in sessions for f in receipt_level):
                problems.append("a gateway receipt finding names a session the store does not hold")
        # the in-toto layer
        if not isinstance(i.get("pass"), bool) or not isinstance(i.get("attestations"), list):
            problems.append("intoto record incomplete")
        else:
            if [a.get("attestation") for a in i["attestations"]] != required:
                problems.append("intoto records are not one per stored receipt in order")
            for a in i["attestations"]:
                if set(a) != {"attestation", "dsse", "statement", "subjects"} or a["dsse"] not in verify_attestation.DSSE_CODES:
                    problems.append("intoto record of the wrong shape or code: %r" % a.get("attestation"))
                    continue
                if a["dsse"] != "pass":
                    if a["statement"] is not None or a["subjects"] != []:
                        problems.append("statement or subjects recorded for an attestation whose envelope failed")
                    continue
                if a["statement"] not in verify_attestation.STATEMENT_CODES:
                    problems.append("statement code %r is not in the vocabulary" % a["statement"])
                elif a["statement"] != "valid":
                    if a["subjects"] != []:
                        problems.append("subjects recorded for an attestation whose statement was not valid")
                elif not isinstance(a["subjects"], list) or not all(isinstance(x, list) and len(x) == 2 and (x[0] is None or isinstance(x[0], str))
                                                                    and x[1] in verify_attestation.SUBJECT_OUTCOMES for x in a["subjects"]):
                    problems.append("subject outcomes of %s are not a list of [name, outcome]" % a["attestation"])
            if not problems and i["pass"] != all(verify_attestation.attestation_passes(a) for a in i["attestations"]):
                problems.append("intoto pass does not follow from its attestations")
        # the binding layer
        if not isinstance(b.get("pass"), bool) or not isinstance(b.get("attestations"), list):
            problems.append("binding record incomplete")
        else:
            if [a.get("attestation") for a in b["attestations"]] != required:
                problems.append("binding records are not one per stored receipt in order")
            for a in b["attestations"]:
                if set(a) != {"attestation", "binding"} or a["binding"] not in verify_binding.CODES:
                    problems.append("binding record of the wrong shape or code: %r" % a.get("attestation"))
            if b["pass"] != all(a.get("binding") == "pass" for a in b["attestations"]):
                problems.append("binding pass does not follow from its attestations")
        if o["combined"] not in ("pass", "fail") or o["combined"] != ("pass" if (g.get("ok") is True and i.get("pass") is True and b.get("pass") is True) else "fail"):
            problems.append("combined verdict does not follow from the layers")
    except (KeyError, TypeError, AttributeError, ValueError, OSError) as e:
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


def decide(locked_rows):
    """The decision from the locked stratum alone (PREREGISTRATION.md section 5): control gates first, then R1."""
    gates = [r["id"] for r in locked_rows if r["role"] == "control-gate" and r["verdict"] != "holds"]
    diverging = [r["id"] for r in locked_rows if r["role"] == "endpoint" and r["verdict"] == "diverges"]
    decision = "control-gate-failed" if gates else ("R1 holds" if not diverging else "R1 falsified")
    return decision, gates


def assemble(label, attempt_id, gateway_digest, holdout_included, validity, locked_rows, holdout_rows, unconstructed):
    """The adjudication record: the locked stratum decides; the holdout is reported beside it and decides nothing."""
    if validity:
        decision, gates = "pipeline-invalid", []
    else:
        decision, gates = decide(locked_rows)
    return {"label": label, "attemptId": attempt_id, "gatewaySha256": gateway_digest, "holdoutIncluded": holdout_included, "decision": decision,
            "validityFailures": validity, "gateFailures": gates, "cells": locked_rows,
            "holdout": {"cells": holdout_rows, "diverging": [r["id"] for r in holdout_rows if r["verdict"] == "diverges"],
                        "unconstructed": sorted(unconstructed), "note": "the reviewer's stratum: reported, deciding nothing"}}


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
    label = PILOT if args.pilot else REGISTERED
    # a registered adjudication reads its evidence from the literal primary root and nowhere else
    if not args.pilot and root.resolve() != PRIMARY_ROOT.resolve():
        sys.exit("refusing: a registered adjudication scores %s, not %s" % (PRIMARY_ROOT, root))
    if (root / "ADJUDICATION.json").exists():
        sys.exit("refusing: %s already holds an adjudication" % root)
    gateway = str(Path(args.gateway).resolve())  # the one file that is hashed and launched, here and in the recomputation
    pins = pinning.load()
    problems = pinning.problems(pins, gateway, require_all=not args.pilot)
    gateway_digest = pinning.sha256_file(gateway) if Path(gateway).is_file() else None
    marker = json.loads((root / "ATTEMPT.json").read_text()) if (root / "ATTEMPT.json").exists() else None
    problems += marker_problems(marker, gateway_digest, label, root)
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
    observed = {}
    with tempfile.TemporaryDirectory() as tmp:
        registered = None
        if holdout and any(cid not in unconstructed for cid in constructions.HOLDOUT_CELLS):
            try:
                registered = constructions.RegisteredContext(root, gateway)
            except Exception as e:  # noqa: BLE001 -- the runner built holdout cells under a context this scorer cannot re-establish
                validity.append("no registered context to rebuild the holdout cells: %s: %s" % (type(e).__name__, str(e)[:300]))
        rebuilt = rebuild_cells(root, validity, cell_ids, unconstructed, tmp, registered)
        obs_path = root / "OBSERVATIONS.json"
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
            if doc.get("trustedKeySha256") != pinning.sha256_file(pinning.TRUSTED_KEY_FILE):
                validity.append("the observations were made under another trusted key file")
            seen = [o.get("cell") for o in doc.get("cells", [])]
            if sorted(seen) != [c for c in cell_ids if c not in unconstructed] or len(seen) != len(set(seen)):
                validity.append("the observations do not cover exactly the registered cells once each")
            for o in doc.get("cells", []):
                cid = o.get("cell")
                if cid in rebuilt:
                    built, snapshot = rebuilt[cid]
                    for p in observation_problems(o, cid, built, snapshot):
                        validity.append("observation of %s: %s" % (cid, p))
                    # the record must be what the pinned apparatus produces over the registered construction, run again here
                    if run_layers.observe(gateway, built) != o:
                        validity.append("observation of %s is not what the pinned apparatus produces over the registered construction" % cid)
                observed[cid] = o
    # the executing code is classified again now that the recomputation has run, so a module imported late is held to the pins too
    for p in pinning.execution_problems(pins):
        validity.append("after the recomputation, the executing code is not the pinned code: %s" % p)
    rows, holdout_rows = [], []
    if not validity:
        rows = adjudicate(locked, observed)
        holdout_rows = adjudicate(holdout, observed, unconstructed) if holdout else []
        unobserved = [r["id"] for r in rows + holdout_rows if r["verdict"] == "unobserved"]
        if unobserved:
            validity.append("unobserved registered cells: %s" % ", ".join(unobserved[:3]))
    record = assemble(label, marker["attemptId"], gateway_digest, bool(holdout), validity, rows, holdout_rows, unconstructed)
    write_once(root, "ADJUDICATION.json", record)
    print("%s: %s (%d locked cells, %d diverge; holdout %d cells, %d diverge, %d unconstructed; %d validity failures, %d gate failures)" % (
        label, record["decision"], len(rows), sum(1 for r in rows if r["verdict"] == "diverges"), len(holdout_rows),
        len(record["holdout"]["diverging"]), len(unconstructed), len(validity), len(record["gateFailures"])))
    for v in validity[:6]:
        print("  ", v)


if __name__ == "__main__":
    main()
