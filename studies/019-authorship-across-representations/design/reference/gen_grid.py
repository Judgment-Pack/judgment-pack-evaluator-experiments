#!/usr/bin/env python3
"""Study 019 reference-build grid generator (design-time tool, deterministic).

Emits cells.json: a list of cells, each a flat dict; a null value means the input is
OMITTED from the engine's input documents (unreadable / unreported). Values for risk and
spend are canonical decimal strings (risk scale 0, spend scale 2); the Rego projection
converts them to JSON numbers.
"""
import json, hashlib

SANCTIONS = ["CLEAR", "MATCH", "UNKNOWN"]
COUNTRY = ["LOW", "MEDIUM", "HIGH", None]
RISK = ["20", "39", "40", "50", "69", "70", "89", "90", "95", None]
SPEND = ["50000.00", "100000.00", "100000.01", "500000.00", "500000.01",
         "2000000.00", "2000000.01", "3000000.00", None]
TRI = {"newVendor": ["yes", "no", None], "critical": ["yes", "no", None],
       "prior": ["yes", "no", None]}
EV = ["present", "absent", None]

cells = []

def add(sanctions, country, risk, spend, newVendor, critical, prior, fin, ins):
    cells.append({
        "sanctions": sanctions, "country": country, "risk": risk, "spend": spend,
        "newVendor": newVendor, "critical": critical, "prior": prior,
        "finEvidence": fin, "insurance": ins,
    })

# Part 1 — core numeric grid: overrides all "no", evidence present, insurance present.
for s in SANCTIONS:
    for c in COUNTRY:
        for r in RISK:
            for sp in SPEND:
                add(s, c, r, sp, "no", "no", "no", "present", "present")

# Part 2 — full tri-state cross at six representative bases (sanctions CLEAR).
BASES = [
    ("LOW", "20", "50000.00"),      # D6a approve region
    ("LOW", "50", "50000.00"),      # D6c approve region (O1-sensitive)
    ("LOW", "20", "1000000.00"),    # D6b region (insurance-sensitive)
    ("HIGH", "50", "3000000.00"),   # O3 escalation region
    ("HIGH", "95", "1000000.00"),   # D3/D4 reject region
    ("MEDIUM", "20", "50000.00"),   # D7 approve region
]
for (c, r, sp) in BASES:
    for nv in TRI["newVendor"]:
        for cr in TRI["critical"]:
            for pr in TRI["prior"]:
                for fe in EV:
                    for ic in EV:
                        add("CLEAR", c, r, sp, nv, cr, pr, fe, ic)

# Part 3 — targeted interaction cells the panel flagged.
EXTRA = [
    # MATCH with everything else missing (P1-first, then D1)
    ("MATCH", None, None, None, None, None, None, "present", None),
    ("MATCH", None, None, None, None, None, None, "absent", None),
    ("MATCH", None, None, None, None, None, None, None, None),
    # sanctions UNKNOWN with unreadable numerics (D2 vs U1)
    ("UNKNOWN", None, None, None, "no", "no", "no", "present", "present"),
    # U1 worked examples
    ("CLEAR", None, "95", "1000000.00", "no", "no", "no", "present", "present"),
    ("CLEAR", "HIGH", "50", None, "no", "no", "no", "present", "present"),
    ("CLEAR", "LOW", None, "100.00", "no", "yes", "no", "present", "present"),
    # O2 x O3 (critical + large HIGH exposure)
    ("CLEAR", "HIGH", "50", "3000000.00", "no", "yes", "no", "present", "present"),
    # P1 x O3 (evidence absent + escalation region)
    ("CLEAR", "HIGH", "50", "3000000.00", "no", "no", "no", "absent", "present"),
    ("CLEAR", "HIGH", "50", "3000000.00", "no", "no", "no", None, "present"),
    # O2 with unreadable numerics
    ("CLEAR", None, None, None, "no", "yes", "no", "present", "present"),
    # D5 vs D6 exclusion
    ("CLEAR", "LOW", "20", "50000.00", "no", "no", "yes", "present", "present"),
    ("CLEAR", "LOW", "20", "50000.00", "no", "no", None, "present", "present"),
    # O1 x O2 same-verdict governance cell
    ("CLEAR", "LOW", "50", "50000.00", "yes", "yes", "no", "present", "present"),
    # O3 boundary exactness at 2M (inclusive D6b side is LOW; HIGH side)
    ("CLEAR", "HIGH", "50", "2000000.00", "no", "no", "no", "present", "present"),
    ("CLEAR", "HIGH", "50", "2000000.01", "no", "no", "no", "present", "present"),
]
for row in EXTRA:
    add(*row)

# Deduplicate (parts overlap), stable order, content-addressed ids.
seen, out = set(), []
for c in cells:
    key = json.dumps(c, sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    cid = "g" + hashlib.sha256(key.encode()).hexdigest()[:10]
    out.append({"id": cid, **c})

with open("cells.json", "w") as f:
    json.dump(out, f, indent=0, sort_keys=True)
print(f"{len(out)} cells")
