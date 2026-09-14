"""Run the three layers over every cell of an attempt root and write the observations.

Per cell: the gateway layer (the pinned `gateway verify` binary over the cell's store, registry,
authority and decision records, the corpus public key on stdin) as `ok` and the findings'
statuses; the in-toto layer (adapter/verify_attestation.py); the binding layer
(adapter/verify_binding.py). The combined verdict is `pass` only when all three pass.

Run: python harness/run_layers.py --cells DIR --gateway BIN --out FILE
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "adapter"))
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

STUDY = HERE.parent
PUBKEY = STUDY / "fixtures" / "baseline" / "gateway.pubkey"
AUTHORITY = (STUDY / "fixtures" / "baseline" / "AUTHORITY").read_text().strip()


def gateway_layer(binary, cell):
    proc = subprocess.run([binary, "verify", str(cell / "store"), str(cell / "registry.jsonl"), AUTHORITY, "--decision-records", str(cell / "decisions")],
                          input=PUBKEY.read_bytes(), capture_output=True)
    if not proc.stdout.strip():
        raise RuntimeError("gateway verify produced no verdict for %s: %s" % (cell.name, proc.stderr.decode(errors="replace")[:300]))
    report = json.loads(proc.stdout)
    findings = report.get("findings", [])
    return {"ok": report.get("ok"), "findings": findings,
            "statuses": sorted({f.get("status") for f in findings}),
            "byReceipt": {("%s/%s" % (f.get("sessionId"), f.get("callIndex", f.get("file")))): f.get("status") for f in findings if "callIndex" in f or "file" in f},
            "session": sorted({f.get("status") for f in findings if "callIndex" not in f and "file" not in f})}


def observe(binary, cell):
    g = gateway_layer(binary, cell)
    i = verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions")
    b = verify_binding.verify(cell / "store", cell / "attestations")
    return {"cell": cell.name, "gateway": g, "intoto": i, "binding": b,
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
        f.write(json.dumps({"attemptId": args.attempt_id, "gatewaySha256": hashlib.sha256(Path(args.gateway).read_bytes()).hexdigest(), "cells": observations}, indent=1))
    for o in observations:
        print("%-40s gateway ok=%-5s %s | intoto %s | binding %s | %s" % (o["cell"], o["gateway"]["ok"], o["gateway"]["statuses"], "pass" if o["intoto"]["pass"] else "FAIL", "pass" if o["binding"]["pass"] else "FAIL", o["combined"]))


if __name__ == "__main__":
    main()
