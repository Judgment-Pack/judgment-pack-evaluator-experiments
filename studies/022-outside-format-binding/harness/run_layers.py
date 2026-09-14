"""Run the three layers over every cell of an attempt root and write the observations.

Per cell: the gateway layer (the pinned `gateway verify` binary over the cell's store, registry,
authority and decision records, the corpus public key on stdin) as `ok` and the findings'
statuses; the in-toto layer (adapter/verify_attestation.py); the binding layer
(adapter/verify_binding.py). The combined verdict is `pass` only when all three pass.

Run: python harness/run_layers.py --cells DIR --gateway BIN --out FILE
"""
import sys
import tempfile

# before any study or pinned-package import: no bytecode read from beside the sources, none written (harness/pins.py)
sys.dont_write_bytecode = True
if not sys.pycache_prefix:
    sys.pycache_prefix = tempfile.mkdtemp(prefix="study022-pycache-")

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "adapter"))
from trees import tree_digest  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

STUDY = HERE.parent
PUBKEY = STUDY / "fixtures" / "baseline" / "gateway.pubkey"
AUTHORITY = (STUDY / "fixtures" / "baseline" / "AUTHORITY").read_text().strip()


TRUSTED_KEY = STUDY / "fixtures" / "baseline" / "attestations" / "adapter.pubkey.json"


def gateway_layer(binary, cell):
    proc = subprocess.run([binary, "verify", str(cell / "store"), str(cell / "registry.jsonl"), AUTHORITY, "--decision-records", str(cell / "decisions")],
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
    cells = sorted(p for p in Path(args.cells).iterdir() if p.is_dir())
    observations = [observe(args.gateway, c) for c in cells]
    with open(args.out, "x") as f:
        f.write(json.dumps({"attemptId": args.attempt_id, "gatewaySha256": hashlib.sha256(Path(args.gateway).read_bytes()).hexdigest(),
                            "python": sys.version.split()[0], "trustedKeySha256": hashlib.sha256(TRUSTED_KEY.read_bytes()).hexdigest(), "cells": observations}, indent=1))
    for o in observations:
        print("%-40s gateway ok=%-5s %s | intoto %s | binding %s | %s" % (o["cell"], o["gateway"]["ok"], o["gateway"]["statuses"], "pass" if o["intoto"]["pass"] else "FAIL", "pass" if o["binding"]["pass"] else "FAIL", o["combined"]))


if __name__ == "__main__":
    main()
