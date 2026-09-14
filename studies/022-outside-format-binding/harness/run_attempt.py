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
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
HARNESS = STUDY / "harness"


PRIMARY_ROOT = STUDY / "results" / "primary-attempt-001"


def terminal(root, payload):
    """The terminal record of a failed attempt after the marker, written once; if it cannot be written, say so."""
    try:
        with open(root / "ADJUDICATION.json", "x") as f:
            f.write(json.dumps(payload, indent=1))
    except OSError as e:
        print("the terminal record could not be written: %s" % e, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--gateway", required=True)
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    if not args.pilot and root.resolve() != PRIMARY_ROOT.resolve():
        sys.exit("refusing: a registered attempt's root is %s" % PRIMARY_ROOT)
    pins = pinning.load()
    problems = pinning.problems(pins, args.gateway, require_all=not args.pilot)
    if problems:
        sys.exit("refusing to start:\n  " + "\n  ".join(problems))
    try:
        root.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        sys.exit("refusing: %s exists; an attempt root is used once" % root)
    # a pilot builds and observes the locked stratum alone; the holdout is constructed inside the registered attempt
    cell_ids = sorted(constructions.ALL_CELLS) if not args.pilot else sorted(constructions.CELLS)
    attempt_id = secrets.token_hex(16)
    marker = {"attemptId": attempt_id, "attemptRoot": str(root.resolve()), "startedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "label": "PILOT" if args.pilot else "REGISTERED", "gatewaySha256": pinning.sha256_file(args.gateway), "pinsRawSha256": pinning.raw_sha256(),
              "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0], "cells": cell_ids}
    (root / "ATTEMPT.json").write_text(json.dumps(marker, indent=1))
    unconstructed = {}
    try:
        for cid in cell_ids:
            if cid in constructions.HOLDOUT_CELLS:
                # a holdout construction is first built here; one that raises is recorded and its partial tree removed,
                # and the locked stratum is unaffected (PREREGISTRATION.md section 1a)
                try:
                    constructions.build(cid, root / "cells")
                except Exception as e:  # noqa: BLE001
                    shutil.rmtree(root / "cells" / cid, ignore_errors=True)
                    unconstructed[cid] = "%s: %s" % (type(e).__name__, str(e)[:300])
            else:
                constructions.build(cid, root / "cells")
        if not args.pilot:
            (root / "HOLDOUT-CONSTRUCTION.json").write_text(json.dumps({"failed": unconstructed}, indent=1))
        subprocess.run([sys.executable, str(HARNESS / "run_layers.py"), "--cells", str(root / "cells"), "--gateway", args.gateway,
                        "--out", str(root / "OBSERVATIONS.json"), "--attempt-id", attempt_id], check=True)
        score = [sys.executable, str(HARNESS / "score.py"), "--attempt-root", str(root), "--gateway", args.gateway]
        if not args.pilot:
            score.append("--include-holdout")
        if args.pilot:
            score.append("--pilot")
        subprocess.run(score, check=True)
    except BaseException as e:  # noqa: BLE001 -- every terminal path after the marker is recorded
        terminal(root, {"label": marker["label"], "attemptId": attempt_id, "decision": "pipeline-invalid",
                        "validityFailures": ["the attempt failed after the marker: %s: %s" % (type(e).__name__, str(e)[:300])], "gateFailures": [], "cells": [],
                        "holdout": {"cells": [], "diverging": [], "note": "not reached"}})
        raise


if __name__ == "__main__":
    main()
