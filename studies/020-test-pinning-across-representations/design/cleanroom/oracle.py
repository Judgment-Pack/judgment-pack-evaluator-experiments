"""Executable oracle for the Vendor Approval Policy.

Implements: P1 (precondition), O3 and O2 (overrides), D1-D8 (determination
clauses) as modified by O1, and U1 (counterfactual test over unreadable
risk score / requested spend / country risk).

Interface (study convention):
    verdict(cell: dict) -> {"disposition": ..., "reasons": [...]}

Decimals are parsed with decimal.Decimal; floats are never used.
"""

from decimal import Decimal
from itertools import product

__all__ = ["verdict"]

# ---------------------------------------------------------------------------
# Constants drawn from the policy text
# ---------------------------------------------------------------------------

SPEND_100K = Decimal("100000.00")
SPEND_500K = Decimal("500000.00")
SPEND_2M = Decimal("2000000.00")
SPEND_MIN = Decimal("0.00")
SPEND_MAX = Decimal("10000000.00")
CENT = Decimal("0.01")

RISK_MIN = 0
RISK_MAX = 100

COUNTRY_DOMAIN = ("LOW", "MEDIUM", "HIGH")

# Readable domain of the risk score: "an integer from 0 to 100".
RISK_DOMAIN = tuple(Decimal(n) for n in range(RISK_MIN, RISK_MAX + 1))

# Readable domain of requested spend: "a US-dollar amount from 0 to
# 10,000,000.00 (cents precision)" -- 1,000,000,001 distinct values, too many
# to enumerate.  INTERVAL DECOMPOSITION (documented per study convention):
# every clause of this policy inspects the requested spend only through the
# three comparisons
#       spend <= $100,000.00      (D6c, D7)
#       spend <= $500,000.00      (D6a)
#       spend <= $2,000,000.00    (D6b)  /  spend > $2,000,000.00  (O3)
# and through no other spend-sensitive test.  The determination is therefore a
# function of which of the four cells the spend falls in:
#       [0.00, 100000.00], (100000.00, 500000.00],
#       (500000.00, 2000000.00], (2000000.00, 10000000.00]
# Two spends in the same cell agree on all three comparisons, hence yield the
# same outcome under every clause.  Quantifying over one representative per
# cell is therefore equivalent to quantifying over all 1,000,000,001 readable
# values.  We use both endpoints of each cell (8 probes) rather than one, so
# that an off-by-one in a threshold comparison would still be exercised.
SPEND_DOMAIN = (
    SPEND_MIN,
    SPEND_100K,
    SPEND_100K + CENT,
    SPEND_500K,
    SPEND_500K + CENT,
    SPEND_2M,
    SPEND_2M + CENT,
    SPEND_MAX,
)

# Outcome tuples: (disposition, tuple-of-reason-tokens)
_APPROVE = ("approve", ())
_REVIEW = ("review", ())
_ENHANCED = ("enhanced-review", ())
_REJECT = ("reject", ())
_UNRESOLVED_UNKNOWN = ("unresolved", ("unknown",))
_UNRESOLVED_NO_MATCH = ("unresolved", ("no-match",))
_UNRESOLVED_ESCALATION = ("unresolved", ("exception-escalation",))
_UNRESOLVED_MISSING = ("unresolved", ("missing-required-evidence",))


# ---------------------------------------------------------------------------
# Core evaluation: all of risk / spend / country readable
# ---------------------------------------------------------------------------


def _core(sanctions, critical, prior, new_vendor, insurance, country, risk, spend):
    """Apply O3, then O2, then D1-D8 (as modified by O1) to a fully readable case.

    P1 has already been satisfied (financial evidence available) by the caller.
    Returns an outcome tuple (disposition, reasons).
    """

    # --- O3: large exposure in a high-risk country -------------------------
    # "Where country risk is HIGH, the screening result is CLEAR, requested
    # spend is above $2,000,000.00, and financial evidence is available (P1),
    # no automated determination is issued".  O3 takes precedence over every
    # clause except P1, including O2 and D1-D8.
    if country == "HIGH" and sanctions == "CLEAR" and spend > SPEND_2M:
        return _UNRESOLVED_ESCALATION

    # --- O2: critical-supplier override ------------------------------------
    # "A critical supplier (yes) with a CLEAR screening result is never
    # approved or rejected automatically: the determination is review."  O2
    # takes precedence over every determination clause D1-D8; it never applies
    # on MATCH or UNKNOWN.  Unreported critical status is treated as no.
    if critical == "yes" and sanctions == "CLEAR":
        return _REVIEW

    # --- D1: sanctions match ------------------------------------------------
    if sanctions == "MATCH":
        return _REJECT

    # --- D2: unreported sanctions ------------------------------------------
    if sanctions == "UNKNOWN":
        return _UNRESOLVED_NO_MATCH

    # From here the screening result is CLEAR (D3-D8 apply only then).

    # --- D3: critical risk --------------------------------------------------
    if risk >= 90:
        return _REJECT

    # --- D4: elevated risk in a high-risk country --------------------------
    if country == "HIGH" and risk >= 70:
        return _REJECT

    # --- D5: prior enforcement action --------------------------------------
    # Unreported prior-enforcement status is treated as no.
    if prior == "yes":
        return _REJECT

    # D6 and D7 apply only to vendors with no recorded prior enforcement
    # action -- guaranteed by the D5 return above.

    # --- D6: approval, LOW-risk country ------------------------------------
    if country == "LOW":
        if risk < 40:
            if spend <= SPEND_500K:
                # D6a
                return _APPROVE
            if spend <= SPEND_2M:
                # D6b
                if insurance == "present":
                    return _APPROVE
                if insurance == "absent":
                    return _ENHANCED
                # unreported availability
                return _UNRESOLVED_UNKNOWN
            # spend above $2,000,000.00 in a LOW country: no D6 limb reaches
            # it, so it falls to D8.
        elif risk < 70:
            # D6c, subject to suspension under O1 for new vendors (yes);
            # unreported new-vendor status is treated as no.
            if spend <= SPEND_100K and new_vendor != "yes":
                return _APPROVE
            # Removed from D6c by O1 (or over the cap): falls to D8.

    # --- D7: approval, MEDIUM-risk country ---------------------------------
    elif country == "MEDIUM":
        if risk < 40 and spend <= SPEND_100K:
            return _APPROVE

    # --- D8: review ---------------------------------------------------------
    return _REVIEW


# ---------------------------------------------------------------------------
# Public entry point: P1, then U1's counterfactual test around _core
# ---------------------------------------------------------------------------


def verdict(cell):
    """Return the policy's outcome for one cell."""

    sanctions = cell.get("sanctions")
    country = cell.get("country")
    risk_raw = cell.get("risk")
    spend_raw = cell.get("spend")
    new_vendor = cell.get("newVendor")
    critical = cell.get("critical")
    prior = cell.get("prior")
    fin_evidence = cell.get("finEvidence")
    insurance = cell.get("insurance")

    # --- P1: financial evidence (applies first; displaced by nothing) ------
    # "No determination of any kind -- including a rejection -- may be issued
    # without financial evidence".  P1 does not depend on any unreadable
    # numeric input, so it is decided before U1 is consulted.
    if fin_evidence == "absent":
        return _emit(_UNRESOLVED_MISSING)
    if fin_evidence is None:
        return _emit(_UNRESOLVED_UNKNOWN)

    # --- U1: counterfactual test over the unreadable inputs ----------------
    # "if every readable value the unreadable input(s) could take would yield
    # the same determination under the clauses above, that determination is
    # issued; otherwise ... unresolved as unknown."
    risk_values = RISK_DOMAIN if risk_raw is None else (Decimal(risk_raw),)
    spend_values = SPEND_DOMAIN if spend_raw is None else (Decimal(spend_raw),)
    country_values = COUNTRY_DOMAIN if country is None else (country,)

    outcome = None
    for c_val, r_val, s_val in product(country_values, risk_values, spend_values):
        candidate = _core(
            sanctions,
            critical,
            prior,
            new_vendor,
            insurance,
            c_val,
            r_val,
            s_val,
        )
        if outcome is None:
            outcome = candidate
        elif candidate != outcome:
            # The readable assignments disagree: no determination is issued.
            return _emit(_UNRESOLVED_UNKNOWN)

    return _emit(outcome)


def _emit(outcome):
    disposition, reasons = outcome
    return {"disposition": disposition, "reasons": sorted(reasons)}
