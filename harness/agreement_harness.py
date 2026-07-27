#!/usr/bin/env python3
"""Cross-implementation agreement harness for RFC 0006.

Runs the SAME (pack, facts, evidence, supported-extensions) inputs through:
  A) the Go reference runtime:  judgment-pack experimental evaluate ... --format json
  B) the clean-room Python implementation:  python -m jps_evaluator ...

and diffs the dispositions. Agreement rows are evidence the RFC's prose pins the
semantics; divergence rows are candidate spec ambiguities (or bugs) and must be
adjudicated against the TEXT, never by making one implementation copy the other.

Usage: agreement_harness.py <go-binary> <python-repo-dir> <pack.json> <cases.json>
  cases.json: [{"name": ..., "facts": {...}, "evidence": {...}|null, "supported": [...]}, ...]
"""
import json
import subprocess
import sys
import tempfile
import os


def run_go(binary, pack_path, case):
    args = [binary, "experimental", "evaluate", pack_path, "--format", "json"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(case["facts"], f)
        facts_path = f.name
    args += ["--facts", facts_path]
    evidence_path = None
    if case.get("evidence") is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(case["evidence"], f)
            evidence_path = f.name
        args += ["--evidence", evidence_path]
    for ext in case.get("supported", []):
        args += ["--supported-extension", ext]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60)
    for p in (facts_path, evidence_path):
        if p:
            os.unlink(p)
    if proc.returncode != 0:
        return {"error": f"exit {proc.returncode}", "detail": (proc.stdout + proc.stderr)[:300]}
    return json.loads(proc.stdout).get("disposition")


def run_py(repo, pack_path, case):
    args = [sys.executable, "-m", "jps_evaluator", "--pack", pack_path]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(case["facts"], f)
        facts_path = f.name
    args += ["--facts", facts_path]
    evidence_path = None
    if case.get("evidence") is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(case["evidence"], f)
            evidence_path = f.name
        args += ["--evidence", evidence_path]
    for ext in case.get("supported", []):
        args += ["--supported-extension", ext]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=repo)
    for p in (facts_path, evidence_path):
        if p:
            os.unlink(p)
    if proc.returncode != 0 and not proc.stdout.strip():
        return {"error": f"exit {proc.returncode}", "detail": (proc.stdout + proc.stderr)[:300]}
    payload = json.loads(proc.stdout)
    return payload.get("disposition", payload)


def normalize(d):
    # Shape-tolerant: impl #1 emits handoff as {state, target}; impl #2 as a
    # bare string with no target echo (recorded divergence: the RFC's
    # disposition sketch underdetermines the concrete JSON shape). Core
    # semantics compared here: kind, outcomeId, reasons set, handoff state.
    if d is None or "error" in d:
        return d
    handoff = d.get("handoff")
    state = handoff.get("state") if isinstance(handoff, dict) else handoff
    return {
        "kind": d.get("kind"),
        "outcomeId": d.get("outcomeId") or None,
        "reasons": sorted(d.get("reasons") or []),
        "handoff": state,
    }


def main():
    go_binary, py_repo, pack_path, cases_path = sys.argv[1:5]
    cases = json.load(open(cases_path))
    agree, diverge = 0, []
    for case in cases:
        a = normalize(run_go(go_binary, pack_path, case))
        b = normalize(run_py(py_repo, pack_path, case))
        if a == b:
            agree += 1
            print(f"AGREE    {case['name']}: {a}")
        else:
            diverge.append(case["name"])
            print(f"DIVERGE  {case['name']}:\n  go: {a}\n  py: {b}")
    print(f"\n{agree}/{len(cases)} agree; divergences: {diverge or 'none'}")
    sys.exit(0 if not diverge else 1)


if __name__ == "__main__":
    main()
