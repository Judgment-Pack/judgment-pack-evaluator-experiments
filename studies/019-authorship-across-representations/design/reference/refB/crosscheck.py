#!/usr/bin/env python3
"""refB self-check: an independent Python model of the same reading of the prose,
plus a densified U1 quantification, diffed against the OPA results.

Two things are being checked:
  1. that policy.rego says what this build intends (mechanical-typo catcher);
  2. that the eight risk / eight spend / three country candidates really do stand in
     for the whole domain -- the Python model re-runs U1 over ALL 101 risk values and a
     much denser spend sample, and must agree with the Rego result on every cell.
"""
import json
import os
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
D = Decimal

DENSE_RISK = list(range(0, 101))
DENSE_SPEND = [D(x) for x in [
    "0", "0.01", "1.00", "99999.99", "100000.00", "100000.01", "250000.00",
    "499999.99", "500000.00", "500000.01", "1000000.00", "1999999.99",
    "2000000.00", "2000000.01", "5000000.00", "9999999.99", "10000000.00",
]]
DENSE_COUNTRY = ["LOW", "MEDIUM", "HIGH"]

APPROVE = ("approve", [])
REVIEW = ("review", [])
ENH = ("enhanced-review", [])
REJECT = ("reject", [])
ESC = ("unresolved", ["exception-escalation"])
UNK = ("unresolved", ["unknown"])
NOMATCH = ("unresolved", ["no-match"])
MISSING = ("unresolved", ["missing-required-evidence"])


def determine(cell, risk, spend, country):
    san, fin, ins = cell["sanctions"], cell["finEvidence"], cell["insurance"]
    if san == "CLEAR" and country == "HIGH" and spend > D("2000000.00") and fin == "present":
        return ESC                                            # O3
    if san == "CLEAR" and cell["critical"] == "yes":
        return REVIEW                                         # O2
    if san == "MATCH":
        return REJECT                                         # D1
    if san == "UNKNOWN":
        return NOMATCH                                        # D2
    if san != "CLEAR":
        return NOMATCH                                        # backstop
    if risk >= 90:
        return REJECT                                         # D3
    if country == "HIGH" and risk >= 70:
        return REJECT                                         # D4
    if cell["prior"] == "yes":
        return REJECT                                         # D5
    if country == "LOW" and risk < 40 and spend <= D("500000.00"):
        return APPROVE                                        # D6a
    if country == "LOW" and risk < 40 and D("500000.00") < spend <= D("2000000.00"):
        return APPROVE if ins == "present" else (ENH if ins == "absent" else UNK)  # D6b
    if (country == "LOW" and 40 <= risk < 70 and spend <= D("100000.00")
            and cell["newVendor"] != "yes"):
        return APPROVE                                        # D6c as modified by O1
    if country == "MEDIUM" and risk < 40 and spend <= D("100000.00"):
        return APPROVE                                        # D7
    return REVIEW                                             # D8


def decide(cell, dense=False):
    fin = cell["finEvidence"]
    if fin == "absent":
        return MISSING                                        # P1
    if fin is None:
        return UNK                                            # P1
    spend = None if cell["spend"] is None else D(cell["spend"])
    risk = None if cell["risk"] is None else int(cell["risk"])
    country = cell["country"]
    if (cell["sanctions"] == "CLEAR" and country == "HIGH"
            and spend is not None and spend > D("2000000.00")):
        return ESC                                            # O3
    if cell["sanctions"] == "CLEAR" and cell["critical"] == "yes":
        return REVIEW                                         # O2
    rs = DENSE_RISK if dense else [0, 39, 40, 69, 70, 89, 90, 100]
    sps = DENSE_SPEND if dense else [D(x) for x in
                                     ["0", "100000.00", "100000.01", "500000.00",
                                      "500000.01", "2000000.00", "2000000.01", "10000000.00"]]
    rs = [risk] if risk is not None else rs
    sps = [spend] if spend is not None else sps
    cs = [country] if country is not None else DENSE_COUNTRY
    got = {json.dumps(determine(cell, r, s, c), sort_keys=True) for r in rs for s in sps for c in cs}
    if len(got) == 1:
        return tuple(json.loads(got.pop()))                   # U1 singleton
    return UNK                                                # U1 otherwise


def main():
    cells = json.load(open(os.path.join(HERE, "..", "cells.json")))
    rego = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(HERE, "results.jsonl"))}
    diffs_model, diffs_dense = [], []
    for c in cells:
        want = decide(c, dense=False)
        wantd = decide(c, dense=True)
        got = rego[c["id"]]
        if [want[0], list(want[1])] != [got["disposition"], got["reasons"]]:
            diffs_model.append((c["id"], want, got))
        if wantd != want:
            diffs_dense.append((c["id"], want, wantd))
    print("cells=%d rego-vs-python-model diffs=%d sparse-vs-dense-U1 diffs=%d"
          % (len(cells), len(diffs_model), len(diffs_dense)))
    for d in diffs_model[:10]:
        print("MODEL DIFF", d)
    for d in diffs_dense[:10]:
        print("DENSE DIFF", d)
    return 1 if (diffs_model or diffs_dense) else 0


if __name__ == "__main__":
    raise SystemExit(main())
