#!/usr/bin/env python3
"""Study 019 — DESIGN-TIME TUNING TARGET, NOT THE STUDY ORACLE.

A direct, readable Python transcription of contest policy draft v0.1
(P1, D1-D8, O1-O3, U1) as prose, written to tune the arm-A reference pack.

  *** THIS FILE IS NOT THE STUDY'S ORACLE. ***
  The study's oracle is the clean-room second implementation plus the
  hand-authored gold rows (BRIEF SS4.3). This module is a maintainer's aid:
  it is written by the same person who writes the pack, so agreement between
  the two is evidence of internal consistency only, never of correctness.
  Nothing here may be cited as gold.

Result shape (shared with the engine projection):
    ("outcome", "<outcome id>")            e.g. ("outcome", "approve")
    ("unresolved", frozenset({...tokens})) e.g. ("unresolved", {"unknown"})

Input cell shape (the shared grid, refbuild/cells.json):
    sanctions   "CLEAR" | "MATCH" | "UNKNOWN"          (never unreadable)
    country     "LOW" | "MEDIUM" | "HIGH" | None       (None = unreadable)
    risk        decimal string, scale 0 | None
    spend       decimal string, scale 2 | None
    newVendor   "yes" | "no" | None                    (None = unreported)
    critical    "yes" | "no" | None
    prior       "yes" | "no" | None
    finEvidence "present" | "absent" | None            (None = unreported)
    insurance   "present" | "absent" | None
"""

from decimal import Decimal
from itertools import product

# ---------------------------------------------------------------------------
# U1's counterfactual substitution domain.
#
# U1 asks whether "every readable value the unreadable input(s) could take
# would yield the same determination". The readable domains are infinite-ish
# (101 risk values, 1,000,000,001 spend values), so we substitute a finite set
# of representatives. The representatives below are sound because every clause
# of the policy reads risk and spend ONLY through comparisons against the six
# declared thresholds, so the determination is a constant function on each
# interval those thresholds cut out; picking any point of each interval
# therefore decides the whole interval, and picking BOTH endpoints of each
# interval additionally makes the choice robust to an off-by-one in the
# interval algebra (a mis-stated inclusivity shows up as a disagreement
# between an interval's two endpoints rather than being silently skipped).
#
#   risk thresholds: 40 (D6a/D6b/D7 "<40", D6c ">=40"), 70 (D6c "<70",
#     D4 ">=70"), 90 (D3 ">=90"), over the declared domain [0, 100].
#     intervals: [0,39] [40,69] [70,89] [90,100]
#     representatives: 0,39   40,69   70,89   90,100      -> 8 values
#
#   spend thresholds: 100,000.00 (D6c/D7 "<="), 500,000.00 (D6a "<=",
#     D6b ">"), 2,000,000.00 (D6b "<=", O3 ">"), over [0.00, 10,000,000.00]
#     at cents precision.
#     intervals: [0, 100000.00] (100000.00, 500000.00]
#                (500000.00, 2000000.00] (2000000.00, 10000000.00]
#     representatives: 0.00,100000.00  100000.01,500000.00
#                      500000.01,2000000.00  2000000.01,10000000.00
#     -> 8 values. Note 2,000,000.00 is inclusive in D6b and exclusive in O3;
#     both senses are exercised by the pair (2000000.00, 2000000.01).
#
#   country risk is a 3-valued enum: substitute all three.
#
# No other input is substitutable: U1's own parenthetical excludes the
# screening result, the evidence availabilities, and the yes/no statuses,
# whose unreported states are governed by D2, P1, O1, O2 and D5 directly.
# ---------------------------------------------------------------------------
RISK_REPS = ["0", "39", "40", "69", "70", "89", "90", "100"]
SPEND_REPS = ["0.00", "100000.00", "100000.01", "500000.00",
              "500000.01", "2000000.00", "2000000.01", "10000000.00"]
COUNTRY_REPS = ["LOW", "MEDIUM", "HIGH"]

APPROVE = ("outcome", "approve")
REVIEW = ("outcome", "review")
ENHANCED = ("outcome", "enhanced-review")
REJECT = ("outcome", "reject")


def _unres(*tokens):
    return ("unresolved", frozenset(tokens))


MISSING_EVIDENCE = _unres("missing-required-evidence")
UNKNOWN = _unres("unknown")
NO_MATCH = _unres("no-match")
ESCALATION = _unres("exception-escalation")


def decide(cell):
    """Top of the ladder: P1, then U1's counterfactual, then the readable ladder."""
    # --- P1 (precondition; no override displaces it) -----------------------
    # "No determination of any kind -- including a rejection -- may be issued
    #  without financial evidence: no other clause of this policy applies
    #  unless financial evidence is available."
    if cell["finEvidence"] == "absent":
        return MISSING_EVIDENCE
    if cell["finEvidence"] is None:
        return UNKNOWN

    # --- U1 (unreadable risk / spend / country) ---------------------------
    # "if every readable value the unreadable input(s) could take would yield
    #  the same determination under the clauses above, that determination is
    #  issued; otherwise ... unresolved as unknown."
    #
    # Read as: substitute jointly over every unreadable input; if the results
    # agree, issue the agreed result; else unresolved as unknown. "The same
    # determination" is generalized to "the same RESULT" so that the rule is
    # total over cells whose substitutions all land on the same unresolved
    # ground (e.g. HIGH + spend $3M + risk unreadable is O3 escalation for
    # every risk value; U1's own gloss -- "a determination issued by a clause
    # that does not depend on the unreadable input stands" -- is the same
    # thought). Where the substitutions disagree at all, the answer is
    # unresolved as unknown, which is exactly U1's "otherwise" branch.
    axes = []
    if cell["risk"] is None:
        axes.append(("risk", RISK_REPS))
    if cell["spend"] is None:
        axes.append(("spend", SPEND_REPS))
    if cell["country"] is None:
        axes.append(("country", COUNTRY_REPS))
    if axes:
        results = set()
        for combo in product(*[values for _, values in axes]):
            probe = dict(cell)
            for (name, _), value in zip(axes, combo):
                probe[name] = value
            results.add(_readable(probe))
            if len(results) > 1:
                return UNKNOWN
        return results.pop()

    return _readable(cell)


def _readable(cell):
    """The ladder over a cell whose risk, spend and country are all readable,
    with financial evidence available. Order of application: O3, then O2,
    then D1-D8 as modified by O1."""
    sanctions = cell["sanctions"]
    country = cell["country"]
    risk = Decimal(cell["risk"])
    spend = Decimal(cell["spend"])
    clear = sanctions == "CLEAR"

    # --- O3 (takes precedence over every clause except P1) -----------------
    # "Where country risk is HIGH, the screening result is CLEAR, requested
    #  spend is above $2,000,000.00, and financial evidence is available (P1),
    #  no automated determination is issued: the case is escalated ... and is
    #  unresolved on the ground of escalation."
    if country == "HIGH" and clear and spend > Decimal("2000000.00"):
        return ESCALATION

    # --- O2 (takes precedence over every determination clause D1-D8) -------
    # "A critical supplier (yes) with a CLEAR screening result is never
    #  approved or rejected automatically: the determination is review ...
    #  never applies when the screening result is MATCH or UNKNOWN ... An
    #  unreported critical-supplier status is treated as no."
    if cell["critical"] == "yes" and clear:
        return REVIEW

    # --- D1 / D2 -----------------------------------------------------------
    if sanctions == "MATCH":
        return REJECT                     # D1
    if sanctions == "UNKNOWN":
        return NO_MATCH                   # D2: no determination clause applies

    # --- D3-D8 apply only when the screening result is CLEAR ---------------
    if risk >= 90:
        return REJECT                     # D3
    if country == "HIGH" and risk >= 70:
        return REJECT                     # D4
    if cell["prior"] == "yes":            # D5 (unreported prior = no)
        return REJECT

    # D6/D7 apply only to vendors with no recorded prior enforcement action.
    if country == "LOW":
        if risk < 40 and spend <= Decimal("500000.00"):
            return APPROVE                # D6a
        if (risk < 40 and Decimal("500000.00") < spend <= Decimal("2000000.00")):
            # D6b: available -> approve; absent -> enhanced review (D6b
            # decides such requests, D8 does not reach them); unreported
            # availability -> unresolved as unknown.
            if cell["insurance"] == "present":
                return APPROVE
            if cell["insurance"] == "absent":
                return ENHANCED
            return UNKNOWN
        if 40 <= risk < 70 and spend <= Decimal("100000.00"):
            # D6c, subject to suspension under O1: for new vendors (yes) D6c
            # does not apply and such requests fall to D8. Unreported
            # new-vendor status is treated as no.
            if cell["newVendor"] == "yes":
                return REVIEW             # D8, via O1
            return APPROVE
    elif country == "MEDIUM":
        if risk < 40 and spend <= Decimal("100000.00"):
            return APPROVE                # D7

    # --- D8 -----------------------------------------------------------------
    return REVIEW


def to_result_row(cell_id, result):
    kind, payload = result
    if kind == "outcome":
        return {"id": cell_id, "disposition": payload, "reasons": []}
    return {"id": cell_id, "disposition": "unresolved", "reasons": sorted(payload)}


if __name__ == "__main__":
    import json
    import sys

    cells = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else "prose_results.jsonl"
    with open(out, "w") as handle:
        for cell in cells:
            handle.write(json.dumps(to_result_row(cell["id"], decide(cell)),
                                    sort_keys=True) + "\n")
    print(f"{len(cells)} cells -> {out}")
