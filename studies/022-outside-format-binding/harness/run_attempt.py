"""The governing runner: one attempt, created exclusively, marked first.

Holds the pins (every pin non-null and matching for a registered attempt), creates the root
exclusively, writes ATTEMPT.json before anything else, builds every registered cell from the
baseline, runs the three layers over every cell, and scores with the holdout.

Run: python harness/run_attempt.py --attempt-root results/primary-attempt-001 --gateway BIN
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

import argparse  # noqa: E402
import datetime  # noqa: E402
import json  # noqa: E402
import secrets  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402

STUDY = Path(__file__).resolve().parent.parent
HARNESS = STUDY / "harness"


PRIMARY_ROOT = constructions.PRIMARY_ROOT


def child_env():
    """The children's environment: this process's, without PYTHONPATH and without any cache prefix (each child makes its own
    fresh, empty prefix before importing anything), with bytecode writing disabled from the start."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONPYCACHEPREFIX")}
    env.update(PYTHONDONTWRITEBYTECODE="1")
    return env


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
    gateway = str(Path(args.gateway).resolve())  # the one file that is hashed and launched, here and in every child
    pins = pinning.load()
    problems = pinning.problems(pins, gateway, require_all=not args.pilot)
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
              "label": "PILOT" if args.pilot else "REGISTERED", "gatewaySha256": pinning.sha256_file(gateway), "pinsRawSha256": pinning.raw_sha256(),
              "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0], "cells": cell_ids}
    (root / "ATTEMPT.json").write_text(json.dumps(marker, indent=1))
    unconstructed = {}
    try:
        # the holdout's only construction context: the marker just written, at the literal root, validated whole; if the
        # validation cannot be established, every holdout cell is recorded unconstructed and the locked stratum proceeds
        registered = None
        if not args.pilot:
            try:
                registered = constructions.RegisteredContext(root, gateway)
            except Exception as e:  # noqa: BLE001
                unconstructed = {cid: "no registered context: %s: %s" % (type(e).__name__, str(e)[:300]) for cid in constructions.HOLDOUT_CELLS}
        for cid in cell_ids:
            if cid in constructions.HOLDOUT_CELLS:
                if cid in unconstructed:
                    continue
                # a holdout construction is first built here; one that raises is recorded and its partial tree removed,
                # and the locked stratum is unaffected (PREREGISTRATION.md section 1a)
                try:
                    constructions.build(cid, root / "cells", registered)
                except Exception as e:  # noqa: BLE001
                    shutil.rmtree(root / "cells" / cid, ignore_errors=True)
                    unconstructed[cid] = "%s: %s" % (type(e).__name__, str(e)[:300])
            else:
                constructions.build(cid, root / "cells")
        if not args.pilot:
            (root / "HOLDOUT-CONSTRUCTION.json").write_text(json.dumps({"failed": unconstructed}, indent=1))
        late = pinning.execution_problems(pins)
        if late:
            raise RuntimeError("after the cells were built, the executing code is not the pinned code:\n  " + "\n  ".join(late))
        subprocess.run([sys.executable, str(HARNESS / "run_layers.py"), "--cells", str(root / "cells"), "--gateway", gateway,
                        "--out", str(root / "OBSERVATIONS.json"), "--attempt-id", attempt_id], check=True, env=child_env())
        score = [sys.executable, str(HARNESS / "score.py"), "--attempt-root", str(root), "--gateway", gateway]
        if not args.pilot:
            score.append("--include-holdout")
        if args.pilot:
            score.append("--pilot")
        subprocess.run(score, check=True, env=child_env())
    except BaseException as e:  # noqa: BLE001 -- every terminal path after the marker is recorded
        terminal(root, {"label": marker["label"], "attemptId": attempt_id, "decision": "pipeline-invalid",
                        "validityFailures": ["the attempt failed after the marker: %s: %s" % (type(e).__name__, str(e)[:300])], "gateFailures": [], "cells": [],
                        "holdout": {"cells": [], "diverging": [], "note": "not reached"}})
        raise


if __name__ == "__main__":
    main()
