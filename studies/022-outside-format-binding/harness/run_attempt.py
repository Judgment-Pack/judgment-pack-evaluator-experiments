"""The governing runner: one attempt, created exclusively, marked first.

Holds the pins (every pin non-null and matching for a registered attempt), creates the root
exclusively, writes ATTEMPT.json before anything else, builds every registered cell from the
baseline, runs the three layers over every cell, and scores with the holdout.

Run: python harness/run_attempt.py --attempt-root results/primary-attempt-001 --gateway BIN
"""
import argparse
import datetime
import json
import secrets
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
HARNESS = STUDY / "harness"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--gateway", required=True)
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    pins = pinning.load()
    problems = pinning.problems(pins, args.gateway, require_all=not args.pilot)
    if problems:
        sys.exit("refusing to start:\n  " + "\n  ".join(problems))
    try:
        root.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        sys.exit("refusing: %s exists; an attempt root is used once" % root)
    attempt_id = secrets.token_hex(16)
    (root / "ATTEMPT.json").write_text(json.dumps({
        "attemptId": attempt_id, "attemptRoot": str(root), "startedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "label": "PILOT" if args.pilot else "REGISTERED", "gatewaySha256": pinning.sha256_file(args.gateway), "pinsRawSha256": pinning.raw_sha256(),
        "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0], "cells": sorted(constructions.CELLS)}, indent=1))
    for cid in sorted(constructions.CELLS):
        constructions.build(cid, root / "cells")
    subprocess.run([sys.executable, str(HARNESS / "run_layers.py"), "--cells", str(root / "cells"), "--gateway", args.gateway,
                    "--out", str(root / "OBSERVATIONS.json"), "--attempt-id", attempt_id], check=True)
    score = [sys.executable, str(HARNESS / "score.py"), "--attempt-root", str(root), "--gateway", args.gateway]
    holdout = json.loads((HARNESS / "MATRIX-HOLDOUT.json").read_text())
    if (holdout if isinstance(holdout, list) else holdout.get("cells")) or not args.pilot:
        # a registered attempt always includes the holdout (and the scorer refuses an empty one); a pilot includes it once it exists
        score.append("--include-holdout")
    if args.pilot:
        score.append("--pilot")
    subprocess.run(score, check=True)


if __name__ == "__main__":
    main()
