"""Deterministic-repeatability check: N fresh Arm B runs must agree byte-for-byte.

Compares, per case and across runs: the raw jpack evaluation bytes retained in
the trajectory note (the envelope carries no timestamps, so the pinned binary
must reproduce them exactly) and the structured action. Writes REPEAT.json.

Stdlib only. Env: FORGE_VENV_PY, JPACK_BIN.
Run: python3 harness/repeat_check.py --pilot-root <dir> [--repeats 3]
"""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent


def run_arm_b(pilot_root, name):
    out = Path(pilot_root) / name
    cmd = [os.environ["FORGE_VENV_PY"], str(STUDY / "harness" / "run_forge.py"),
           "--pack", str(STUDY / "scenarios" / "jps" / "cohort2.yaml"),
           "--agent-module", "arm_b", "--agents-dir", str(STUDY / "agents"),
           "--out", str(out), "--run-id", "run-001", "--tags", "cohort2"]
    env = dict(os.environ, STUDY_DIR=str(STUDY))
    subprocess.run(cmd, capture_output=True, env=env, check=False)
    return out


def digest_run(out):
    digests = {}
    for path in sorted((Path(out) / "runs" / "run-001" / "artifacts").glob("*.json")):
        artifact = json.loads(path.read_text())
        note = next((s.get("content") for s in artifact.get("trajectory") or []
                     if s.get("type") == "note"), "")
        action = json.dumps(((artifact.get("output") or {}).get("structured") or {})
                            .get("action"), sort_keys=True)
        digests[path.stem] = {
            "evaluation_sha256": hashlib.sha256(note.encode()).hexdigest(),
            "action_sha256": hashlib.sha256(action.encode()).hexdigest(),
        }
    return digests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    all_digests = []
    for i in range(args.repeats):
        out = run_arm_b(args.pilot_root, "repeat-{:02d}".format(i + 1))
        all_digests.append(digest_run(out))
    identical = all(d == all_digests[0] for d in all_digests[1:])
    report = {"repeats": args.repeats, "identical": identical, "digests": all_digests[0]}
    if not identical:
        report["all"] = all_digests
    path = Path(args.pilot_root) / "REPEAT.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("repeatability:", "identical across {} runs".format(args.repeats)
          if identical else "DRIFT DETECTED")
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
