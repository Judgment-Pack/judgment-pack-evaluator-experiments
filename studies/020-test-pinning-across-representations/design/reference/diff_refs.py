#!/usr/bin/env python3
"""Study 019 reference agreement diff (design-time tool).

Joins refA/results.jsonl (JPS) and refB/results.jsonl (Rego) on cell id, compares
(disposition, reasons-set), and prints divergences grouped by (A-verdict, B-verdict)
pattern with cell inputs echoed. Exit 1 on any divergence, 0 on full agreement.
"""
import json, sys, collections

BASE = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad/refbuild"

def load(path):
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out[r["id"]] = (r["disposition"], tuple(sorted(r["reasons"])))
    return out

cells = {c["id"]: c for c in json.load(open(f"{BASE}/cells.json"))}
a = load(f"{BASE}/refA/results.jsonl")
b = load(f"{BASE}/refB/results.jsonl")

missing_a = sorted(set(cells) - set(a))
missing_b = sorted(set(cells) - set(b))
if missing_a: print(f"MISSING from refA: {len(missing_a)} cells, e.g. {missing_a[:5]}")
if missing_b: print(f"MISSING from refB: {len(missing_b)} cells, e.g. {missing_b[:5]}")

groups = collections.defaultdict(list)
agree = 0
for cid in sorted(set(a) & set(b)):
    if a[cid] == b[cid]:
        agree += 1
    else:
        groups[(a[cid], b[cid])].append(cid)

total = len(set(a) & set(b))
print(f"compared {total} cells: {agree} agree, {total - agree} diverge, "
      f"{len(groups)} divergence patterns\n")

def fmt(v):
    d, r = v
    return d if not r else f"{d}{list(r)}"

for (va, vb), ids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    print(f"=== A={fmt(va)}  B={fmt(vb)}  ({len(ids)} cells) ===")
    for cid in ids[:6]:
        c = cells[cid]
        desc = ", ".join(f"{k}={c[k]}" for k in
                         ("sanctions", "country", "risk", "spend", "newVendor",
                          "critical", "prior", "finEvidence", "insurance"))
        print(f"  {cid}: {desc}")
    if len(ids) > 6:
        print(f"  ... and {len(ids) - 6} more")
    print()

sys.exit(0 if (total - agree) == 0 and not missing_a and not missing_b else 1)
