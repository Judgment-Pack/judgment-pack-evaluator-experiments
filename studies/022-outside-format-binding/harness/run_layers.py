"""Run the three layers over every cell of an attempt root and write the observations.

Per cell: the gateway layer (the pinned `gateway verify` binary over the cell's store, registry,
authority and decision records, the corpus public key on stdin) as `ok` and the findings'
statuses; the in-toto layer (adapter/verify_attestation.py); the binding layer
(adapter/verify_binding.py). The combined verdict is `pass` only when all three pass.

Run: python harness/run_layers.py --cells DIR --gateway BIN --out FILE
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
    _ORIGINAL_PATH = list(sys.path)
    _GUARD_DIR = os.path.dirname(os.path.realpath(__file__))
    _STUDY = os.path.dirname(_GUARD_DIR)
    # import resolution restricted to the interpreter's library and the virtual environment until the guard has verified the study roots
    sys.path[:] = [_e for _e in sys.path if _e and (os.path.realpath(_e).startswith(os.path.realpath(sys.base_prefix) + os.sep)
                                                     or os.path.realpath(_e).startswith(os.path.realpath(sys.prefix) + os.sep))]
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
import hashlib  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "adapter"))
from trees import tree_digest  # noqa: E402
import pins as pinning  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

STUDY = HERE.parent
PUBKEY = STUDY / "fixtures" / "baseline" / "gateway.pubkey"
AUTHORITY = (STUDY / "fixtures" / "baseline" / "AUTHORITY").read_text().strip()


TRUSTED_KEY = STUDY / "fixtures" / "baseline" / "attestations" / "adapter.pubkey.json"


def resolved_gateway(binary):
    """The one file that is hashed and launched: an absolute path, never a name for the shell or PATH to resolve."""
    path = Path(binary).resolve()
    if not path.is_file():
        raise RuntimeError("the gateway verifier %s is not a file" % path)
    return path


def gateway_layer(binary, cell):
    binary = resolved_gateway(binary)
    proc = subprocess.run([str(binary), "verify", str(cell / "store"), str(cell / "registry.jsonl"), AUTHORITY, "--decision-records", str(cell / "decisions")],
                          input=PUBKEY.read_bytes(), capture_output=True)
    # SPEC.md section 4.1: a verifier that exits non-zero gave no verdict, whatever stdout holds
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError("gateway verify gave no verdict for %s (exit %d): %s" % (cell.name, proc.returncode, proc.stderr.decode(errors="replace")[:300]))
    report = json.loads(proc.stdout)
    findings = report.get("findings", [])
    return {"ok": report.get("ok"), "findings": findings,
            "statuses": sorted({f.get("status") for f in findings}),
            "byReceipt": {("%s/%s" % (f.get("sessionId"), f.get("callIndex", f.get("file")))): f.get("status") for f in findings if "callIndex" in f or "file" in f},
            "session": sorted({f.get("status") for f in findings if "callIndex" not in f and "file" not in f})}


def observe(binary, cell):
    snapshot = tree_digest(cell)
    g = gateway_layer(binary, cell)
    i = verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions", verify_attestation.trusted_key(TRUSTED_KEY))
    b = verify_binding.verify(cell / "store", cell / "attestations")
    if tree_digest(cell) != snapshot:
        raise RuntimeError("the cell %s changed while it was being observed" % cell.name)
    return {"cell": cell.name, "cellSha256": snapshot, "gateway": g, "intoto": i, "binding": b,
            "combined": "pass" if (g["ok"] is True and i["pass"] and b["pass"]) else "fail"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--gateway", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--attempt-id", default=None)
    args = ap.parse_args()
    gateway = resolved_gateway(args.gateway)
    cells = sorted(p for p in Path(args.cells).iterdir() if p.is_dir())
    observations = [observe(gateway, c) for c in cells]
    # the executing code is classified again now that every layer has run, so a module imported late is held to the pins too
    late = pinning.execution_problems(pinning.load())
    if late:
        raise RuntimeError("after the layers ran, the executing code is not the pinned code:\n  " + "\n  ".join(late))
    with open(args.out, "x") as f:
        f.write(json.dumps({"attemptId": args.attempt_id, "gatewaySha256": hashlib.sha256(gateway.read_bytes()).hexdigest(),
                            "python": sys.version.split()[0], "trustedKeySha256": hashlib.sha256(TRUSTED_KEY.read_bytes()).hexdigest(), "cells": observations}, indent=1))
    for o in observations:
        print("%-40s gateway ok=%-5s %s | intoto %s | binding %s | %s" % (o["cell"], o["gateway"]["ok"], o["gateway"]["statuses"], "pass" if o["intoto"]["pass"] else "FAIL", "pass" if o["binding"]["pass"] else "FAIL", o["combined"]))


if __name__ == "__main__":
    main()
