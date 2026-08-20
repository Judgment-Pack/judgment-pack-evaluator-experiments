#!/usr/bin/env python3
"""Study 019 — Rego reference (refB): project the shared grid and evaluate it.

Per cell:
  * build the engine input document TEXTUALLY, so the canonical decimal strings for
    riskScore / requestedSpend appear as unquoted JSON numbers with their exact digits.
    OPA parses JSON numbers as exact big rationals, so no float round-trip happens here
    and none happens inside OPA either.
  * a null cell value means the member is OMITTED from the input document entirely
    (unreadable numeric / unreadable country / unreported status / unreported evidence
    availability).
  * evaluate data.study.decision with the pinned binary + filtered capabilities.

Outputs (in refB/):
  inputs/<id>.json   the exact input document handed to OPA
  raw.jsonl          {"id", "rc", "value"|"error", "stdout_head"} for every cell
  results.jsonl      {"id", "disposition", "reasons"} in cells.json order
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.abspath(os.path.join(HERE, "..", ".."))
PINS = os.path.join(SCRATCH, "pins", "opa")
OPA = os.path.join(PINS, "opa_linux_amd64_static")
CAPS = os.path.join(PINS, "caps-filtered.json")
CELLS = os.path.join(HERE, "..", "cells.json")
POLICY = os.path.join(HERE, "policy.rego")
INDIR = os.path.join(HERE, "inputs")

# cell key -> (input document path, JSON kind)
VENDOR_FIELDS = [
    ("risk", "riskScore", "number"),
    ("spend", "requestedSpend", "number"),
    ("sanctions", "sanctionsStatus", "string"),
    ("country", "countryRisk", "string"),
    ("newVendor", "newVendor", "string"),
    ("critical", "criticalSupplier", "string"),
    ("prior", "priorEnforcement", "string"),
]
EVIDENCE_FIELDS = [
    ("finEvidence", "financial-evidence"),
    ("insurance", "insurance-certificate"),
]

DISPOSITIONS = {"approve", "review", "enhanced-review", "reject", "unresolved"}
REASON_TOKENS = {"missing-required-evidence", "unknown", "no-match", "exception-escalation"}


def render_input(cell):
    """Build the input document text. Numbers are emitted as raw digit strings."""
    vend = []
    for key, member, kind in VENDOR_FIELDS:
        val = cell.get(key)
        if val is None:
            continue  # OMITTED member
        if kind == "number":
            # canonical decimal string -> unquoted JSON number, digits verbatim
            vend.append('    "%s": %s' % (member, val))
        else:
            vend.append('    "%s": %s' % (member, json.dumps(val)))
    ev = []
    for key, member in EVIDENCE_FIELDS:
        val = cell.get(key)
        if val is None:
            continue  # OMITTED member
        ev.append('    "%s": %s' % (member, json.dumps(val)))
    return (
        "{\n"
        '  "vendor": {\n' + ",\n".join(vend) + ("\n" if vend else "") + "  },\n"
        '  "evidence": {\n' + ",\n".join(ev) + ("\n" if ev else "") + "  }\n"
        "}\n"
    )


def evaluate(cell):
    cid = cell["id"]
    path = os.path.join(INDIR, cid + ".json")
    with open(path, "w") as fh:
        fh.write(render_input(cell))
    env = dict(os.environ)
    env["TZ"] = "UTC"
    proc = subprocess.run(
        [
            OPA, "eval",
            "--format", "json",
            "--fail",
            "--strict-builtin-errors",
            "--capabilities", CAPS,
            "--timeout", "10s",
            "--data", POLICY,
            "--input", path,
            "data.study.decision",
        ],
        capture_output=True, text=True, env=env, cwd=HERE,
    )
    rec = {"id": cid, "rc": proc.returncode}
    if proc.returncode != 0:
        rec["error"] = {"stderr": proc.stderr.strip(), "stdout": proc.stdout.strip()[:2000]}
        return rec
    try:
        out = json.loads(proc.stdout)
        rec["value"] = out["result"][0]["expressions"][0]["value"]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = {"parse": repr(exc), "stdout": proc.stdout.strip()[:2000]}
    return rec


def main():
    with open(CELLS) as fh:
        cells = json.load(fh)
    os.makedirs(INDIR, exist_ok=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "12"))) as pool:
        recs = list(pool.map(evaluate, cells))

    errors, results = [], []
    for cell, rec in zip(cells, recs):
        if "error" in rec:
            errors.append(rec)
            continue
        val = rec["value"]
        disp = val.get("disposition")
        reasons = sorted(val.get("reasons", []))
        assert disp in DISPOSITIONS, (rec["id"], disp)
        if disp == "unresolved":
            assert reasons and set(reasons) <= REASON_TOKENS, (rec["id"], reasons)
        else:
            assert reasons == [], (rec["id"], reasons)
        results.append({"id": rec["id"], "disposition": disp, "reasons": reasons})

    with open(os.path.join(HERE, "raw.jsonl"), "w") as fh:
        for rec in recs:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    with open(os.path.join(HERE, "results.jsonl"), "w") as fh:
        for row in results:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    print("cells=%d results=%d errors=%d" % (len(cells), len(results), len(errors)))
    for e in errors[:20]:
        print("ERROR", e["id"], json.dumps(e.get("error"))[:400])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
