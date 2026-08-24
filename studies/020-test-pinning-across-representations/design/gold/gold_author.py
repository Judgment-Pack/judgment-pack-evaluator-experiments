#!/usr/bin/env python3
"""Study 019 gold suite v0 — authoring transport (DESIGN DRAFT).

The AUTHOR of every expectation is the maintainer side, deriving each row from the policy
prose by hand (v0 rows from POLICY-DRAFT.md v0.2; the v0.1 adequacy-gate section at the foot
of this file from v0.3, whose three clarifying sentences change no cell's verdict — see
cleanroom/DISPOSITION.md); this script is transport, not derivation — it only
assembles hand-written rows into gold.json. Expectations were NOT copied from the reference
implementations; the checker (check_gold.py) compares them against both engines afterward,
and any discrepancy is adjudicated in writing in GOLD-NOTES.md, never silently edited.

Row fields: inputs use the shared cell schema (null = the input is omitted from the engine
documents — unreadable / unreported); expect is {disposition, reasons (sorted set)};
cite lists governing clause(s) under the earliest-clause tie-break; note says why the row
exists.
"""
import json

# CITE-ORDER CORRECTION (2026-08-19, freeze ceremony; V7's mechanical derivation,
# verification/V7-COMPLETENESS.md): thirteen rows' cite lists led with a modifier (O1) or
# the U1 meta-clause where the registered ladder's earliest-clause tie-break — under the
# standing-clause dependence rule the majority of rows already followed (a clause whose
# readable conjuncts already decide it stands; V7 proved no total order reproduced the old
# lists) — derives the standing determination clause. The thirteen lists were reordered to
# lead with the derived governing clause, retaining the contributing clauses after it.
# INPUTS AND EXPECTATIONS ARE BYTE-UNTOUCHED: outcomes reproduce 117/117 from prose before
# and after; only cite order moved. Rows: o1-nv-d6c, o1-nv-40-0, o1-nv-40-100k,
# o1-nv-69-100k, the five x1r-* region rows, u1-ex1, u1-ex3, u1-spend-med-95, u1-country-2m.

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
row("o1-nv-d6c", "new vendor: D6c suspended, falls to D8", ["D8", "O1"], "review",
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
row("u1-ex1", "worked example 1: risk 95 rejects whatever the country", ["D3", "U1"],
    "reject", country=None, risk="95", spend="1000000.00")
row("u1-ex2", "worked example 2: unreadable spend straddles review and escalation",
    ["U1"], U, ["unknown"], country="HIGH", risk="50", spend=None)
row("u1-ex3", "worked example 3: O2 decides without the risk score", ["O2", "U1"],
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
row("u1-spend-med-95", "MEDIUM has no O3: rejection is uniform over spend", ["D3", "U1"],
    "reject", country="MEDIUM", risk="95", spend=None)
row("u1-risk-high-50k", "HIGH with small spend: review below 70, reject above", ["U1"],
    U, ["unknown"], country="HIGH", risk=None)
row("u1-two-unreadable-uniform", "prior action rejects under every completion", ["U1", "D5"],
    "reject", country=None, risk=None, prior="yes")

# =========================================================================================
# ==== gold v0.1 — ADEQUACY-GATE ADDITIONS (2026-08-15) ===================================
# =========================================================================================
# Why these rows exist: the pre-freeze adequacy gate (PREREGISTRATION.md §4) requires every
# mutant to be killed by gold or registered as dropped. `mutants/adequacy_search.py` swept a
# dense derived input space and reported, per empty-witness mutant, the inputs at which the
# mutant's scored surface differs from its arm's reference. THAT SEARCH SAYS ONLY WHERE TO
# LOOK. It never says what the policy requires there: every expectation below was derived by
# hand from POLICY-DRAFT.md and carries its clause citation, exactly as the v0 rows were, and
# no expectation was read off a mutant, a reference, or an engine. Where a derivation turned
# on a sentence rather than a numeral, the sentence is quoted in the row note.
#
# Two regions dominate the additions, which is where the v0 grid was thin:
#   (a) D6b's band ($500,000.01–$2,000,000.00) at its own edges and at the risk-40 edge,
#       across all three insurance states — v0 probed D6b only at risk 20 and spend $1M;
#   (b) the region O1 removes from D6c (new vendor, 40 ≤ risk < 70, LOW, spend ≤ $100,000.00)
#       at its four edges — v0 probed it at one interior point.
# Both are stated by the prose at clause granularity; neither needed a new reading of it.

# ---- (a) D6b's band: the risk-40 edge, all three insurance states ------------------------
# D6b's limbs open at "risk score below 40"; at risk exactly 40 no D6 limb applies (D6c needs
# spend up to $100,000.00), so D8's catch-all governs: "Every request with a CLEAR screening
# result that is not determined by D3–D7 ... is referred for review."
row("d8-low-40-500k01-ins-present", "risk 40 is outside every D6 limb: D8 governs, and the "
    "insurance state cannot change that (P1: the certificate 'is never required; it is "
    "consulted only by D6b')", ["D8"], "review", risk="40", spend="500000.01")
row("d8-low-40-500k01-ins-absent", "same cell, certificate absent: still D8, not D6b's "
    "enhanced-review limb, because D6b needs risk below 40", ["D8"], "review",
    risk="40", spend="500000.01", insurance="absent")
row("d8-low-40-500k01-ins-unreported", "same cell, availability unreported: D6b's unresolved "
    "limb is not reached either; D8 reviews", ["D8"], "review",
    risk="40", spend="500000.01", insurance=None)

# ---- (a) D6b's band at risk 39 (the band's upper risk edge), all three insurance states --
row("d6b-39-500k01-present", "D6b's lower spend edge at the risk band's upper edge: "
    "certificate available: approved", ["D6b"], "approve", risk="39", spend="500000.01")
row("d6b-39-500k01-absent", "same cell, certificate absent: enhanced review (D6b decides "
    "such requests; D8 does not reach them)", ["D6b"], "enhanced-review",
    risk="39", spend="500000.01", insurance="absent")
row("d6b-39-500k01-unreported", "same cell, availability unreported: unresolved as unknown",
    ["D6b"], U, ["unknown"], risk="39", spend="500000.01", insurance=None)

# ---- (a) D6a's spend edge under the two non-available insurance states -------------------
# "Risk score below 40 and requested spend up to and including $500,000.00: approved" — D6a
# reads no insurance state at all, so both cells approve.
row("d6a-500k-ins-absent", "spend exactly $500,000.00 is D6a, whose text consults no "
    "certificate: an absent certificate does not move it into D6b's enhanced-review limb",
    ["D6a"], "approve", spend="500000.00", insurance="absent")
row("d6a-500k-ins-unreported", "same edge with availability unreported: D6a still approves; "
    "only D6b's limb is unresolved on an unreported certificate", ["D6a"], "approve",
    spend="500000.00", insurance=None)

# ---- (a) D6b's upper spend edge ($2,000,000.00 inclusive) and the cent above it ----------
row("d6b-2m-absent", "spend exactly $2,000,000.00 is inside D6b (inclusive) with the "
    "certificate absent: enhanced review", ["D6b"], "enhanced-review",
    spend="2000000.00", insurance="absent")
row("d6b-2m-unreported", "the same inclusive edge with availability unreported: unresolved "
    "as unknown", ["D6b"], U, ["unknown"], spend="2000000.00", insurance=None)
row("d8-2m01-low-absent", "one cent above D6b's band in a LOW country: no D6 limb applies "
    "and O3 is HIGH-only, so D8 reviews whatever the certificate says", ["D8"], "review",
    spend="2000000.01", insurance="absent")
row("d8-2m01-low-unreported", "same cell with availability unreported: still D8", ["D8"],
    "review", spend="2000000.01", insurance=None)

# ---- (a) D6b's lower spend edge under the two non-available insurance states -------------
row("d6b-500k01-absent", "one cent above $500,000.00 with the certificate absent: D6b's "
    "enhanced-review limb", ["D6b"], "enhanced-review", spend="500000.01",
    insurance="absent")
row("d6b-500k01-unreported", "one cent above $500,000.00 with availability unreported: "
    "D6b's unresolved limb", ["D6b"], U, ["unknown"], spend="500000.01", insurance=None)

# ---- (a) D6b is LOW-only: the same band in a MEDIUM country ------------------------------
# D7 is the only MEDIUM approval clause and stops at $100,000.00; D6b's band does not exist
# in MEDIUM, so all three insurance states land on D8.
row("d8-med-500k01-present", "D6b is a LOW-country clause: in MEDIUM the same band is D8, "
    "certificate available", ["D8"], "review", country="MEDIUM", spend="500000.01")
row("d8-med-500k01-absent", "same MEDIUM cell, certificate absent: D8, not enhanced review",
    ["D8"], "review", country="MEDIUM", spend="500000.01", insurance="absent")
row("d8-med-500k01-unreported", "same MEDIUM cell, availability unreported: D8, not "
    "unresolved", ["D8"], "review", country="MEDIUM", spend="500000.01", insurance=None)

# ---- (b) the region O1 removes from D6c, at its four edges -------------------------------
# "For new vendors (yes), clause D6c does not apply; such requests fall to D8." The edges are
# D6c's own: risk at least 40 and below 70, spend up to and including $100,000.00.
row("o1-nv-40-0", "O1 at D6c's lower risk edge (risk exactly 40) and the spend floor",
    ["D8", "O1"], "review", newVendor="yes", risk="40", spend="0.00")
row("o1-nv-40-100k", "O1 at D6c's lower risk edge and its inclusive spend edge",
    ["D8", "O1"], "review", newVendor="yes", risk="40", spend="100000.00")
row("o1-nv-69-100k", "O1 at D6c's upper risk edge (69) and its inclusive spend edge",
    ["D8", "O1"], "review", newVendor="yes", risk="69", spend="100000.00")
row("d6a-nv-39-0", "risk 39 is D6a's band, which O1 does not touch: a new vendor is still "
    "approved", ["D6a"], "approve", newVendor="yes", risk="39", spend="0.00")
row("d8-nv-70-100k", "risk 70 is outside D6c's band before O1 is consulted: D8 governs",
    ["D8"], "review", newVendor="yes", risk="70", spend="100000.00")
row("d8-nv-40-100k01", "one cent above D6c's spend edge, so D6c never applied and O1 has "
    "nothing to suspend: D8", ["D8"], "review", newVendor="yes", risk="40",
    spend="100000.01")

# ---- U1 at O3's exclusive $2,000,000.00 edge with the country unreadable -----------------
# U1's test varies only the unreadable input. O3 begins ABOVE $2,000,000.00, so the same
# numeral answers differently on the two sides of the edge.
row("u1-country-2m01", "country unreadable one cent above O3's edge: HIGH escalates (O3) "
    "while LOW and MEDIUM review (D8) — the determinations differ", ["U1"], U, ["unknown"],
    country=None, risk="50", spend="2000000.01")
row("u1-country-2m", "country unreadable at O3's edge exactly: O3 needs spend above "
    "$2,000,000.00, so every readable country reviews under D8 — uniform, so U1 issues it",
    ["D8", "U1"], "review", country=None, risk="50", spend="2000000.00")

# ---- U1 against D6b's limbs (unreadable country, spend inside D6b's band) ----------------
# U1 varies only the unreadable input; "the same determination" means the same outcome, and
# an unresolved limb such as D6b's counts as an outcome for that test. D6b exists only in
# LOW, so an unreadable country puts D6b's answer beside D8's review in every one of these.
# (These three rows are also the adequacy gate's way of killing four cascade mutants by a
# differing determination rather than through the engine's structural conflict detection.)
row("u1-country-39-500k01-absent", "country unreadable in D6b's band with the certificate "
    "absent: LOW gives enhanced review, MEDIUM and HIGH give review (D7 stops at "
    "$100,000.00; risk 39 is below every rejection band) — the determinations differ",
    ["U1"], U, ["unknown"], country=None, risk="39", spend="500000.01", insurance="absent")
row("u1-country-39-500k01-present", "the same cell with the certificate available: LOW "
    "approves under D6b while MEDIUM and HIGH review", ["U1"], U, ["unknown"],
    country=None, risk="39", spend="500000.01")
row("u1-country-2m-absent", "country unreadable at D6b's inclusive top with the certificate "
    "absent: LOW gives enhanced review; HIGH does not escalate because O3 begins above "
    "$2,000,000.00, so HIGH and MEDIUM review", ["U1"], U, ["unknown"],
    country=None, spend="2000000.00", insurance="absent")

# ---- D1 inside O3's region ---------------------------------------------------------------
row("d1-match-o3-region", "O3 requires a CLEAR screening result; under MATCH the escalation "
    "does not arise and D1 rejects", ["D1"], "reject", sanctions="MATCH", country="HIGH",
    risk="50", spend="2000000.01")

# ---- the former X1 region, opened by the 2026-08-18 reference repair --------------------
# Until the repair (reference/refA/PACK-CHANGE-001.md, round-1 finding R1-2) this region was
# a registered exclusion class and gold was FORBIDDEN to carry a row in it. The repair made
# the arm-A reference answer the prose here, the exclusion registry is now empty, and these
# rows are the region's first gold coverage. Every expectation below is derived from the
# prose the same way as every other row — O1 removes D6c for a new vendor, no other
# determination clause reaches the 40-69 band, so D8 governs and U1's counterfactual is
# uniform over the unreadable member — and each was then reproduced, on the first run, by
# both pinned engines AND by the clean-room oracle.
row("x1r-low-spend-unreadable-40", "new vendor, LOW, risk at D6c's lower edge with the "
    "requested spend unreadable: O1 removes D6c and no other clause reaches the band, so "
    "every spend lands on D8 review and U1 issues it", ["D8", "O1", "U1"], "review",
    newVendor="yes", risk="40", spend=None)
row("x1r-low-spend-unreadable-69", "the same at D6c's upper edge with the insurance "
    "certificate absent: D6b needs risk below 40, so the certificate cannot change the "
    "determination either", ["D8", "O1", "U1"], "review",
    newVendor="yes", risk="69", spend=None, insurance="absent")
row("x1r-country-unreadable-100k", "new vendor at D6c's inclusive spend edge with the "
    "country risk unreadable: LOW is D6c removed by O1, MEDIUM is out of D7's reach at risk "
    "55, HIGH is out of D4's reach below 70 and O3 begins above $2,000,000.00 - every "
    "country reviews under D8", ["D8", "O1", "U1"], "review",
    newVendor="yes", risk="55", country=None, spend="100000.00")
# The adjacency control for the two rows above: it is NOT in the former X1 region, and it is
# what stops the repair's two region rules from being written any wider. With BOTH the
# country and the spend unreadable, HIGH x above $2,000,000.00 reaches O3's escalation while
# LOW x below $100,000.00 reaches D8's review, so the determinations differ and U1 says
# unknown. A repair that scoped its region on the risk band alone would answer review here
# and this row would fail.
row("x1r-adjacent-both-unreadable", "country AND spend unreadable for a new vendor in "
    "D6c's band: O3 escalates a HIGH country above $2,000,000.00 while a LOW country "
    "reviews, so the determinations differ and U1 leaves it unknown", ["U1", "O3"],
    U, ["unknown"], newVendor="yes", risk="55", country=None, spend=None)

# =========================================================================================
# ==== gold v0.2 — ROUND-3 ADEQUACY-GATE ADDITIONS (2026-08-18) ===========================
# =========================================================================================
# Why these rows exist: the arm-A reference repair (reference/refA/PACK-CHANGE-001.md,
# round-1 finding R1-2) regenerated the JPS mutant corpus, and 37 of the new mutants came
# out with an empty witness set. Review round 3 (finding R3-2) named that as the adequacy
# gate re-opening. `mutants/adequacy_search.py --search` swept the same dense 419,904-cell
# derived space over those 37 and found 11 of them distinguishable from the repaired
# reference somewhere. THE SEARCH SAYS ONLY *WHERE* TO LOOK. It never says what the policy
# requires there, and no expectation below was read off a mutant, a reference or an engine:
# each is derived by hand from POLICY-DRAFT.md v0.3 with its clause citation, and each
# row's note names the sentence it was derived from.
#
# All eleven live in ONE region, and it is the region the repair created: the two derived
# "region lemma" rules (`r-o1-wide-low`, `r-o1-wide-spend`) and the two D8 suppressions
# scoped to them. v0.1's grid probed that region only in a LOW country, because before the
# repair the arm-A reference could not answer it anywhere else. The rows below are its
# edges: the risk-band edges (40 and 69) and the D4 edge above it (70) in a MEDIUM, HIGH
# and unreadable country, the spend edge a cent above $100,000.00, and D6b's unreported
# limb for a new vendor.

# ---- the region lemma in a MEDIUM country: D6c and O1 are LOW-only, so D8 governs -------
# "Every request with a CLEAR screening result that is not determined by D3-D7 ... is
# referred for review." D7 is the only MEDIUM approval clause and it needs a risk score
# below 40; O1 removes nothing here, because the clause it suspends (D6c) is LOW-only.
row("d8-med-nv-40-100k", "a new vendor in a MEDIUM country at D6c's lower risk edge: D6c "
    "and O1 are both LOW-only and D7 needs risk below 40, so D8 reviews", ["D8"], "review",
    country="MEDIUM", risk="40", spend="100000.00", newVendor="yes")
row("d8-med-nv-69-100k", "the same at D6c's upper risk edge (69): still no MEDIUM clause "
    "reaches it, so D8 reviews", ["D8"], "review",
    country="MEDIUM", risk="69", spend="100000.00", newVendor="yes")
row("d8-med-nv-40-100k01", "the same one cent above D6c's spend ceiling: the ceiling is "
    "D6c's, D6c is LOW-only, and D8 reviews on either side of it in a MEDIUM country",
    ["D8"], "review", country="MEDIUM", risk="40", spend="100000.01", newVendor="yes")

# ---- the region lemma against D4, one point above the band ------------------------------
# "Where country risk is HIGH and the risk score is 70 or above, the request is rejected."
# Risk 70 is D4's inclusive edge and is OUTSIDE D6c's band (which ends below 70), so no
# review clause competes with it.
row("d4-high-nv-70-100k", "a new vendor in a HIGH country at D4's inclusive edge: D4 "
    "rejects, and being a new vendor changes nothing because O1 suspends only D6c",
    ["D4"], "reject", country="HIGH", risk="70", spend="100000.00", newVendor="yes")
row("d8-high-nv-39-100k", "a new vendor in a HIGH country one point below D6c's band: D4 "
    "begins at 70, O3 begins above $2,000,000.00, and no approval clause reaches a HIGH "
    "country, so D8 reviews", ["D8"], "review",
    country="HIGH", risk="39", spend="100000.00", newVendor="yes")

# ---- D6b's unreported limb for a new vendor ---------------------------------------------
# "If its availability is unreported, the case is unresolved as unknown." D6b is a D6 limb
# and D6 is not suspended by O1 — O1 names D6c alone.
row("d6b-nv-39-500k01-unreported", "D6b's unreported-certificate limb for a NEW vendor: O1 "
    "suspends D6c only, so D6b decides this request exactly as it does for any other vendor "
    "and the case is unresolved as unknown", ["D6b"], U, ["unknown"],
    risk="39", spend="500000.01", insurance=None, newVendor="yes")

# ---- U1 over an unreadable country at the region's two risk edges -----------------------
# These two are inside the region the retired X1 class used to forbid, and they are its risk
# edges: gold already carries the region's interior (`x1r-country-unreadable-100k`, risk 55).
# U1's counterfactual is uniform at both edges: LOW is D6c removed by O1 (D8), MEDIUM is out
# of D7's reach (D8), HIGH is out of D4's reach below 70 and O3 begins above $2,000,000.00
# (D8) - every readable country reviews, so U1 issues review.
row("x1r-country-unreadable-40", "new vendor, country unreadable, at D6c's lower risk edge "
    "with spend at D6c's inclusive ceiling: every readable country reviews under D8, so U1 "
    "issues review", ["D8", "O1", "U1"], "review",
    country=None, risk="40", spend="100000.00", newVendor="yes")
row("x1r-country-unreadable-69", "the same at D6c's upper risk edge (69)", ["D8", "O1", "U1"],
    "review", country=None, risk="69", spend="100000.00", newVendor="yes")

with open("gold.json", "w") as f:
    json.dump({"goldVersion": "0.2-draft", "policy": "POLICY-DRAFT.md v0.3",
               "rows": ROWS}, f, indent=1, sort_keys=True)
print(f"{len(ROWS)} gold rows written")
