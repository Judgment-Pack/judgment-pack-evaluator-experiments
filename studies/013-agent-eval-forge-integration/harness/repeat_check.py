"""Deterministic-repeatability check: exactly 3 fresh Arm B runs, byte-identical.

The registered cardinality (3) is enforced here AND validated by the gate from
REPEAT.json's content (review round 2, finding R2-1): any other value refuses.
Each run must contain the exact 21 scheduled case ids, every artifact
completed, an acceptable driver exit, and zero scorer errors before it is
digested — N failed runs can never count as "identical" (round 1, finding 1).

Per case and across runs, the raw jpack evaluation bytes retained in the
trajectory note (the envelope carries no timestamps) and the structured action
must agree exactly.

Stdlib only. Env: FORGE_VENV_PY, JPACK_BIN, STUDY_DIR.
Run: python3 harness/repeat_check.py --pilot-root <dir> --repeats 3
"""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
REPEATS = 3


def run_arm_b(pilot_root, name):
    out = Path(pilot_root) / name
    cmd = [os.environ["FORGE_VENV_PY"], str(STUDY / "harness" / "run_forge.py"),
           "--pack", str(STUDY / "scenarios" / "jps" / "cohort2.yaml"),
           "--agent-module", "arm_b", "--agents-dir", str(STUDY / "agents"),
           "--out", str(out), "--run-id", "run-001", "--tags", "cohort2"]
    env = dict(os.environ, STUDY_DIR=str(STUDY))
    proc = subprocess.run(cmd, capture_output=True, env=env)
    return out, proc.returncode


def inspect_run(out, name, driver_exit, expected_ids):
    """Validate one repeat run and return (detail, digests)."""
    run_dir = Path(out) / "runs" / "run-001"
    paths = sorted((run_dir / "artifacts").glob("*.json"))
    artifact_ids = [p.stem for p in paths]
    if sorted(artifact_ids) != sorted(expected_ids):
        raise SystemExit("repeat run {} artifact ids differ from schedule".format(name))
    scores = json.loads((run_dir / "scores.json").read_text())
    score_ids = sorted(scores.get("scenario_scores") or {})
    if score_ids != sorted(expected_ids):
        raise SystemExit("repeat run {} score ids differ from schedule".format(name))
    scorer_errors = (scores.get("study") or {}).get("scorer_errors") or []
    digests = {}
    for path in paths:
        artifact = json.loads(path.read_text())
        if artifact.get("status") != "completed":
            raise SystemExit("repeat run {} artifact not completed: {}".format(
                name, path.stem))
        note = next((s.get("content") for s in artifact.get("trajectory") or []
                     if s.get("type") == "note"), "")
        action = json.dumps(((artifact.get("output") or {}).get("structured") or {})
                            .get("action"), sort_keys=True)
        digests[path.stem] = {
            "evaluation_sha256": hashlib.sha256(note.encode()).hexdigest(),
            "action_sha256": hashlib.sha256(action.encode()).hexdigest(),
        }
    detail = {"name": name, "artifact_ids": artifact_ids, "score_ids": score_ids,
              "all_completed": True, "driver_exit": driver_exit,
              "scorer_errors": len(scorer_errors),
              "safety_violations": scores.get("safety_violations") or []}
    return detail, digests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--repeats", type=int, default=REPEATS)
    args = parser.parse_args()
    if args.repeats != REPEATS:
        raise SystemExit("the registered repeat cardinality is exactly {}".format(REPEATS))
    expected_ids = [c["id"] for c in json.loads(
        (STUDY / "scenarios" / "jps" / "cases.json").read_text())["cases"]]
    details, all_digests = [], []
    for i in range(REPEATS):
        name = "repeat-{:02d}".format(i + 1)
        out, driver_exit = run_arm_b(args.pilot_root, name)
        detail, digests = inspect_run(out, name, driver_exit, expected_ids)
        details.append(detail)
        all_digests.append(digests)
    identical = all(d == all_digests[0] for d in all_digests[1:])
    report = {"repeats": REPEATS, "identical": identical, "runs": details,
              "digests": all_digests[0]}
    if not identical:
        report["all"] = all_digests
    (Path(args.pilot_root) / "REPEAT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("repeatability:", "identical across {} runs".format(REPEATS)
          if identical else "DRIFT DETECTED")
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
