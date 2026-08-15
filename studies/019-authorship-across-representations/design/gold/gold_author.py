#!/usr/bin/env python3
"""Study 019 gold suite v0 — authoring transport (DESIGN DRAFT).

The AUTHOR of every expectation is the maintainer side, deriving each row from the policy
prose (POLICY-DRAFT.md v0.2) by hand; this script is transport, not derivation — it only
assembles hand-written rows into gold.json. Expectations were NOT copied from the reference
implementations; the checker (check_gold.py) compares them against both engines afterward,
and any discrepancy is adjudicated in writing in GOLD-NOTES.md, never silently edited.

Row fields: inputs use the shared cell schema (null = the input is omitted from the engine
documents — unreadable / unreported); expect is {disposition, reasons (sorted set)};
cite lists governing clause(s) under the earliest-clause tie-break; note says why the row
exists.
"""
import json

BASE = {"sanctions": "CLEAR", "country": "LOW", "risk": "20", "spend": "50000.00",
        "newVendor": "no", "critical": "no", "prior": "no",
        "finEvidence": "present", "insurance": "present"}

ROWS = []

def row(rid, note, cite, disposition, reasons=(), **deltas):
    inputs = dict(BASE)
    inputs.update(deltas)
    ROWS.append({"id": rid, "inputs": inputs,
                 "expect": {"disposition": disposition, "reasons": sorted(reasons)},
                 "cite": list(cite), "note": note})

U = "unresolved"

# ---- P1: the evidence precondition ------------------------------------------------------
row("p1-absent", "absent financial evidence blocks everything", ["P1"], U,
    ["missing-required-evidence"], finEvidence="absent")
row("p1-unreported", "unreported availability is unknown, a different reason", ["P1"], U,
    ["unknown"], finEvidence=None)
row("p1-absent-match", "P1 precedes even a sanctions-match rejection", ["P1"], U,
    ["missing-required-evidence"], finEvidence="absent", sanctions="MATCH")
row("p1-absent-escalation-region", "reason purity: no exception-escalation leaks in", ["P1"], U,
    ["missing-required-evidence"], finEvidence="absent", country="HIGH", risk="50",
    spend="3000000.00")
row("p1-unreported-escalation-region", "same cell, unreported availability", ["P1"], U,
    ["unknown"], finEvidence=None, country="HIGH", risk="50", spend="3000000.00")
row("p1-unreported-d2", "P1 precedes D2 as well", ["P1"], U, ["unknown"],
    finEvidence=None, sanctions="UNKNOWN")

# ---- D1 / D2: the sanctions gate --------------------------------------------------------
row("d1-match", "sanctions MATCH rejects", ["D1"], "reject", sanctions="MATCH")
row("d1-match-bare", "MATCH decides with every other fact input missing", ["D1"], "reject",
    sanctions="MATCH", country=None, risk=None, spend=None, newVendor=None, critical=None,
    prior=None, insurance=None)
row("d1-match-critical", "O2 never applies under MATCH", ["D1"], "reject",
    sanctions="MATCH", critical="yes")
row("d2-unknown", "unreported screening: no clause matches", ["D2"], U, ["no-match"],
    sanctions="UNKNOWN")
row("d2-unknown-bare", "no-match, not unknown, with numerics missing too", ["D2"], U,
    ["no-match"], sanctions="UNKNOWN", country=None, risk=None, spend=None)
row("d2-unknown-critical", "O2 never applies under UNKNOWN screening", ["D2"], U,
    ["no-match"], sanctions="UNKNOWN", critical="yes")

# ---- D3 / D4: risk rejections and the 89/90 and 69/70 boundaries ------------------------
row("d3-low-90", "risk 90 rejects everywhere", ["D3"], "reject", risk="90")
row("d8-low-89", "risk 89 in LOW only reviews", ["D8"], "review", risk="89")
row("d3-med-90", "risk 90 rejects in MEDIUM", ["D3"], "reject", country="MEDIUM", risk="90")
row("d4-high-70", "HIGH rejection begins at exactly 70", ["D4"], "reject",
    country="HIGH", risk="70")
row("d8-high-69", "risk 69 in HIGH reviews", ["D8"], "review", country="HIGH", risk="69")
row("d4-high-89", "risk 89 in HIGH still D4", ["D4"], "reject", country="HIGH", risk="89")
row("d3-high-90", "at 90 in HIGH both reject; earliest clause (D3) governs", ["D3"],
    "reject", country="HIGH", risk="90")

# ---- D5: prior enforcement --------------------------------------------------------------
row("d5-low-approve-region", "prior action rejects inside an approval region", ["D5"],
    "reject", prior="yes")
row("d5-med", "prior action rejects in MEDIUM too", ["D5"], "reject",
    country="MEDIUM", prior="yes")
row("d5-unreported", "unreported prior status is treated as no", ["D6a"], "approve",
    prior=None)
row("d3-over-d5", "risk 95 with prior action: both reject; earliest (D3) governs", ["D3"],
    "reject", risk="95", prior="yes")
row("d5-d6b-absent", "prior action beats the enhanced-review branch", ["D5"], "reject",
    spend="1000000.00", insurance="absent", prior="yes")

# ---- D6a and its boundaries -------------------------------------------------------------
row("d6a-39-50k", "risk 39: the low band's upper edge", ["D6a"], "approve", risk="39")
row("d6a-500k", "spend exactly 500,000.00 is still D6a", ["D6a"], "approve",
    spend="500000.00")
row("d6a-ins-absent", "insurance is not consulted outside D6b", ["D6a"], "approve",
    insurance="absent")
row("d6a-0-0", "domain floor: risk 0, spend 0.00", ["D6a"], "approve",
    risk="0", spend="0.00")

# ---- D6b: the insurance tri-state and the 500k / 2M boundaries --------------------------
row("d6b-500k01", "one cent above 500,000.00 enters D6b", ["D6b"], "approve",
    spend="500000.01")
row("d6b-2m", "spend exactly 2,000,000.00 is inside D6b (inclusive)", ["D6b"], "approve",
    spend="2000000.00")
row("d8-2m01-low", "one cent above 2M in LOW falls to review", ["D8"], "review",
    spend="2000000.01")
row("d6b-1m-present", "insurance available: approve", ["D6b"], "approve",
    spend="1000000.00")
row("d6b-1m-absent", "insurance absent: enhanced review, decided by D6b", ["D6b"],
    "enhanced-review", spend="1000000.00", insurance="absent")
row("d6b-1m-unreported", "insurance availability unreported: unresolved as unknown",
    ["D6b"], U, ["unknown"], spend="1000000.00", insurance=None)

# ---- D6c and the 39/40 and 100k boundaries ----------------------------------------------
row("d6c-40-50k", "risk exactly 40 leaves D6a for D6c", ["D6c"], "approve", risk="40")
row("d6c-40-100k", "spend exactly 100,000.00 is inside D6c", ["D6c"], "approve",
    risk="40", spend="100000.00")
row("d8-40-100k01", "one cent above 100,000.00 leaves D6c", ["D8"], "review",
    risk="40", spend="100000.01")
row("d6c-69-100k", "risk 69: D6c's upper edge", ["D6c"], "approve",
    risk="69", spend="100000.00")
row("d8-70-low", "risk 70 in LOW: no approval clause reaches it", ["D8"], "review",
    risk="70", spend="100000.00")
row("d8-40-500k", "mid-band risk with D6a-sized spend: review", ["D8"], "review",
    risk="40", spend="500000.00")

# ---- D7 and MEDIUM ----------------------------------------------------------------------
row("d7-39-100k", "MEDIUM approval at both upper edges", ["D7"], "approve",
    country="MEDIUM", risk="39", spend="100000.00")
row("d8-40-med", "risk 40 in MEDIUM: no approval clause", ["D8"], "review",
    country="MEDIUM", risk="40", spend="100000.00")
row("d8-39-100k01-med", "one cent above 100,000.00 in MEDIUM: review", ["D8"], "review",
    country="MEDIUM", risk="39", spend="100000.01")
row("d7-0-0", "MEDIUM domain floor", ["D7"], "approve",
    country="MEDIUM", risk="0", spend="0.00")

# ---- D8 general -------------------------------------------------------------------------
row("d8-high-mid", "HIGH below the rejection band: review", ["D8"], "review",
    country="HIGH", risk="50")

# ---- O1: first-engagement suspension ----------------------------------------------------
row("o1-nv-d6c", "new vendor: D6c suspended, falls to D8", ["O1", "D8"], "review",
    newVendor="yes", risk="50")
row("o1-nv-d6a", "O1 touches only D6c: D6a still approves a new vendor", ["D6a"],
    "approve", newVendor="yes")
row("o1-nv-unreported", "unreported new-vendor status is treated as no", ["D6c"],
    "approve", newVendor=None, risk="50")
row("o1-nv-med", "O1 does not reach D7", ["D7"], "approve",
    newVendor="yes", country="MEDIUM")

# ---- O2: critical-supplier override -----------------------------------------------------
row("o2-reject-region", "critical supplier: review even at risk 95", ["O2"], "review",
    critical="yes", risk="95")
row("o2-approve-region", "critical supplier: never auto-approved", ["O2"], "review",
    critical="yes")
row("o2-unreported", "unreported critical status is treated as no", ["D6a"], "approve",
    critical=None)
row("o2-over-d5", "O2 beats the prior-enforcement rejection", ["O2"], "review",
    critical="yes", prior="yes")
row("o2-over-d4", "O2 beats the HIGH-country rejection", ["O2"], "review",
    critical="yes", country="HIGH", risk="70")
row("o2-d6b-absent", "O2 beats the enhanced-review branch", ["O2"], "review",
    critical="yes", spend="1000000.00", insurance="absent")

# ---- O3: large exposure in a high-risk country ------------------------------------------
row("o3-2m01", "one cent above 2M in HIGH escalates", ["O3"], U,
    ["exception-escalation"], country="HIGH", risk="50", spend="2000000.01")
row("o3-3m", "the escalation region proper", ["O3"], U, ["exception-escalation"],
    country="HIGH", risk="50", spend="3000000.00")
row("d8-high-2m", "spend exactly 2M in HIGH does not escalate", ["D8"], "review",
    country="HIGH", risk="50", spend="2000000.00")
row("o3-over-o2", "O3 beats O2", ["O3"], U, ["exception-escalation"],
    country="HIGH", risk="50", spend="3000000.00", critical="yes")
row("o3-over-d3", "O3 beats even a critical-risk rejection", ["O3"], U,
    ["exception-escalation"], country="HIGH", risk="95", spend="3000000.00")
row("o3-over-d5", "O3 beats the prior-enforcement rejection", ["O3"], U,
    ["exception-escalation"], country="HIGH", risk="50", spend="3000000.00", prior="yes")
row("o3-risk-unreadable", "O3 reads no risk score; it decides without one", ["O3"], U,
    ["exception-escalation"], country="HIGH", risk=None, spend="3000000.00")
row("d8-low-3m", "no escalation outside HIGH: large LOW spend is review", ["D8"],
    "review", spend="3000000.00")

# ---- U1: unreadable numerics (all outside the registered X1 exclusion) ------------------
row("u1-ex1", "worked example 1: risk 95 rejects whatever the country", ["U1", "D3"],
    "reject", country=None, risk="95", spend="1000000.00")
row("u1-ex2", "worked example 2: unreadable spend straddles review and escalation",
    ["U1"], U, ["unknown"], country="HIGH", risk="50", spend=None)
row("u1-ex3", "worked example 3: O2 decides without the risk score", ["U1", "O2"],
    "review", critical="yes", risk=None, spend="100.00")
row("u1-ex4", "worked example 4: critical supplier, O3 not excludable", ["U1"], U,
    ["unknown"], critical="yes", country=None, risk=None, spend=None)
row("u1-risk-low-50k", "risk spans approve and review bands: unknown", ["U1"], U,
    ["unknown"], risk=None)
row("u1-risk-prior", "prior action rejects at every risk value: uniform", ["U1", "D5"],
    "reject", risk=None, prior="yes")
row("u1-country-20-50k", "country spans approve (LOW/MEDIUM) and review (HIGH)", ["U1"],
    U, ["unknown"], country=None)
row("u1-country-95-3m", "country spans rejection and escalation", ["U1"], U, ["unknown"],
    country=None, risk="95", spend="3000000.00")
row("u1-spend-low-20", "spend spans approve bands and review above 2M", ["U1"], U,
    ["unknown"], spend=None)
row("u1-spend-high-95", "even risk 95 in HIGH: escalation above 2M keeps it open",
    ["U1"], U, ["unknown"], country="HIGH", risk="95", spend=None)
row("u1-spend-med-95", "MEDIUM has no O3: rejection is uniform over spend", ["U1", "D3"],
    "reject", country="MEDIUM", risk="95", spend=None)
row("u1-risk-high-50k", "HIGH with small spend: review below 70, reject above", ["U1"],
    U, ["unknown"], country="HIGH", risk=None)
row("u1-two-unreadable-uniform", "prior action rejects under every completion", ["U1", "D5"],
    "reject", country=None, risk=None, prior="yes")

with open("gold.json", "w") as f:
    json.dump({"goldVersion": "0-draft", "policy": "POLICY-DRAFT.md v0.2",
               "rows": ROWS}, f, indent=1, sort_keys=True)
print(f"{len(ROWS)} gold rows written")
