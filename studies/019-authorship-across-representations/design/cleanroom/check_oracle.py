#!/usr/bin/env python3
"""Clean-room oracle agreement check: oracle vs gold, and oracle vs refA over the grid.
Run from this directory. Exit nonzero on any unexpected divergence (X1-class cells are
expected divergences and are counted separately; the design grid contains none)."""
import json, sys, importlib.util, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("oracle", os.path.join(HERE, "oracle.py"))
oracle = importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
gold = json.load(open(os.path.join(HERE, "..", "gold", "gold.json")))
cells = json.load(open(os.path.join(HERE, "..", "reference", "cells.json")))
refA = {}
with open(os.path.join(HERE, "..", "reference", "refA", "results.jsonl")) as f:
    for line in f:
        r = json.loads(line); refA[r["id"]] = (r["disposition"], tuple(sorted(r["reasons"])))
bad = 0
for row in gold["rows"]:
    v = oracle.verdict(dict(row["inputs"]))
    got = (v["disposition"], tuple(sorted(v["reasons"])))
    want = (row["expect"]["disposition"], tuple(sorted(row["expect"]["reasons"])))
    if got != want:
        print(f"GOLD DIVERGE {row['id']}: gold={want} oracle={got}"); bad += 1
x1 = 0
for c in cells:
    inp = {k: c[k] for k in ("sanctions","country","risk","spend","newVendor","critical","prior","finEvidence","insurance")}
    v = oracle.verdict(dict(inp))
    got = (v["disposition"], tuple(sorted(v["reasons"])))
    if got != refA[c["id"]]:
        rr = inp["risk"]
        in_x1 = (inp["newVendor"] == "yes" and rr is not None and 40 <= int(rr) < 70
                 and ((inp["country"] == "LOW" and inp["spend"] is None)
                      or (inp["country"] is None and inp["spend"] is not None
                          and float(inp["spend"]) <= 100000.00)))
        if in_x1: x1 += 1
        else:
            print(f"GRID DIVERGE {c['id']}: refA={refA[c['id']]} oracle={got}"); bad += 1
print(f"gold rows {len(gold['rows'])}, grid cells {len(cells)}, X1-class {x1}, unexpected divergences {bad}")
sys.exit(1 if bad else 0)
