"""Golden disposition capture — runs the PINNED evaluator over every case.

For each case in cases.json: evaluate (pack, facts, evidence) with $JPACK_BIN,
retain the full evaluation output bytes (run-invariant: the envelope carries no
timestamps), and compare the disposition against the case's registered
`expect`. The evaluator governs: a disagreement is a defect in the hand
derivation and must be resolved (and recorded) before freeze.

Writes goldens/<case>.evaluation.json (raw bytes) and goldens/EXPECT-CHECK.json.
Exit 1 on any disagreement or evaluation error so drift is loud.

Stdlib only. Run: JPACK_BIN=... python3 harness/make_goldens.py
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent


def evaluate(jpack, pack_path, facts, evidence):
    cmd = [jpack, "experimental", "evaluate", str(pack_path), "--facts", "-", "--format", "json"]
    evidence_path = None
    try:
        if evidence:
            handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
            json.dump(evidence, handle)
            handle.close()
            evidence_path = handle.name
            cmd += ["--evidence", evidence_path]
        proc = subprocess.run(cmd, input=json.dumps(facts).encode(), capture_output=True, timeout=60)
    finally:
        if evidence_path:
            os.unlink(evidence_path)
    return proc


def main():
    jpack = os.environ.get("JPACK_BIN")
    if not jpack:
        sys.exit("JPACK_BIN is not set")
    registry = json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())
    goldens = STUDY / "goldens"
    goldens.mkdir(exist_ok=True)
    report = []
    failures = 0
    for case in registry["cases"]:
        proc = evaluate(jpack, STUDY / "packs" / case["pack"], case["facts"], case["evidence"])
        entry = {"case": case["id"], "exit": proc.returncode}
        if proc.returncode != 0:
            entry["error"] = (proc.stdout or proc.stderr).decode("utf-8", "replace")
            entry["agrees"] = False
            failures += 1
            report.append(entry)
            continue
        (goldens / (case["id"] + ".evaluation.json")).write_bytes(proc.stdout)
        evaluation = json.loads(proc.stdout)
        disposition = evaluation["disposition"]
        expect = case["expect"]
        observed = {
            "kind": disposition["kind"],
            "outcomeId": disposition.get("outcomeId"),
            "reasons": disposition.get("reasons", []),
            "handoff": disposition["handoff"]["state"],
            "triggeredBy": disposition["handoff"].get("triggeredBy"),
            "handoffTarget": evaluation.get("handoffTarget"),
        }
        registered = {
            "kind": expect["kind"],
            "outcomeId": expect["outcomeId"],
            "reasons": expect["reasons"],
            "handoff": expect["handoff"],
            "triggeredBy": expect["triggeredBy"],
            "handoffTarget": expect["handoffTarget"],
        }
        entry["agrees"] = observed == registered
        if not entry["agrees"]:
            entry["registered"] = registered
            entry["observed"] = observed
            failures += 1
        report.append(entry)
    (goldens / "EXPECT-CHECK.json").write_text(json.dumps(
        {"jpack": jpack, "disagreements": failures, "cases": report},
        indent=2, sort_keys=True) + "\n")
    print("goldens: {} cases, {} disagreements".format(len(report), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
