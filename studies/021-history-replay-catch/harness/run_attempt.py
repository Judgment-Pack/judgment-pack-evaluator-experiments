"""The governing runner: one registered attempt, created exclusively, marked first.

Creates the attempt root (refusing one that exists, whatever it holds), writes
ATTEMPT.json before anything else -- the runtime's version and digest, the
raw digest of harness/PINS.json as parsed, the reserved seeds and sizes, the
policies -- then builds every ledger with the reserved seeds, plants every
defect, replays every cell with the unplanted gate, and scores with the
holdout. A crash anywhere after the marker leaves the marker and everything
written so far; the root is then spent, and a second attempt needs a new root
named by a deviation.

Run: python harness/run_attempt.py --attempt-root results/primary-attempt-001
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

import secrets

import attempt
import build_ledgers
import jp

STUDY = Path(__file__).resolve().parent.parent
HARNESS = STUDY / "harness"
POLICIES = ("data-request-intake-triage", "expense-approval", "sanctions-screening", "vendor-onboarding")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--pilot", action="store_true", help="label PILOT and draw seeds 1-30 instead of the reserved ones")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    digest = jp.binary_digest()
    if not args.pilot:
        # a registered attempt starts only under complete, matching pins:
        # nothing is drawn from the reserved seeds before that is known
        problems = attempt.pin_problems(attempt.load_pins(), digest, require_all=True)
        if problems:
            sys.exit("refusing a registered attempt:\n  " + "\n  ".join(problems))
    try:
        root.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        sys.exit("refusing: %s exists; an attempt root is used once" % root)
    seed_base = 1 if args.pilot else build_ledgers.RESERVED_SEEDS[0]
    attempt_id = secrets.token_hex(16)
    (root / "ATTEMPT.json").write_text(json.dumps({
        "attemptId": attempt_id, "attemptRoot": str(root), "startedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "label": attempt.PILOT_LABEL if args.pilot else attempt.REGISTERED_LABEL, "jpackVersion": jp.runtime_version(), "jpackDigest": digest,
        "pinsRawSha256": attempt.pins_raw_sha256(), "seeds": [seed_base, seed_base + 29], "sizes": list(build_ledgers.SIZES),
        "policies": list(POLICIES)}, indent=1))
    py = sys.executable
    for policy in POLICIES:
        build = [py, str(HARNESS / "build_ledgers.py"), policy, "--n", *map(str, build_ledgers.SIZES), "--seeds", "30", "--seed-base", str(seed_base), "--out", str(root)]
        if not args.pilot:
            build.append("--reserved")
        subprocess.run(build, check=True)
        subprocess.run([py, str(HARNESS / "plant.py"), policy, "--out", str(root), "--attempt-id", attempt_id], check=True)
        subprocess.run([py, str(HARNESS / "replay.py"), policy, "--ledgers", str(root / policy), "--defects", str(root / policy / "defects"),
                        "--out", str(root / policy / "cells.json"), "--policy-pack", str(STUDY / "fixtures" / "policies" / (policy + ".pack.json")),
                        "--attempt-id", attempt_id], check=True)
    score = [py, str(HARNESS / "score.py"), "--attempt-root", str(root), "--include-holdout"]
    if args.pilot:
        score.append("--pilot")
    subprocess.run(score, check=True)


if __name__ == "__main__":
    main()
