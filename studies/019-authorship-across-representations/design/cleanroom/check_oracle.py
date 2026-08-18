#!/usr/bin/env python3
"""Clean-room oracle agreement check: oracle vs gold, and oracle vs refA over the grid.
Run from this directory. Exit nonzero on ANY divergence: the registered exclusion-class
set is empty since X1 was retired on 2026-08-18 (round-1 finding R1-2;
reference/refA/PACK-CHANGE-001.md), so no divergence is expected any more and none is
excused. The retired X1 predicate is kept as a non-gating census line."""
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
REGISTERED_EXCLUSIONS = {}   # name -> predicate(inputs); EMPTY since X1 was retired

def retired_x1(i):
    r = i["risk"]
    return (i["newVendor"] == "yes" and r is not None and 40 <= int(r) < 70
            and ((i["country"] == "LOW" and i["spend"] is None)
                 or (i["country"] is None and i["spend"] is not None
                     and float(i["spend"]) <= 100000.00)))

excused = 0
retired_region_rows = sum(1 for row in gold["rows"] if retired_x1(row["inputs"]))
for c in cells:
    inp = {k: c[k] for k in ("sanctions","country","risk","spend","newVendor","critical","prior","finEvidence","insurance")}
    v = oracle.verdict(dict(inp))
    got = (v["disposition"], tuple(sorted(v["reasons"])))
    if got != refA[c["id"]]:
        hit = [n for n, p in REGISTERED_EXCLUSIONS.items() if p(inp)]
        if hit:
            excused += 1
        else:
            print(f"GRID DIVERGE {c['id']}: refA={refA[c['id']]} oracle={got}"); bad += 1
print(f"gold rows {len(gold['rows'])} ({retired_region_rows} inside the retired X1 region), "
      f"grid cells {len(cells)}, registered exclusion classes {len(REGISTERED_EXCLUSIONS)}, "
      f"excused divergences {excused}, unexpected divergences {bad}")
sys.exit(1 if bad else 0)
