"""Clean-room mirror of the Study 010 vendor screening policy (POLICY.md).

The only input to this module was the bytes of POLICY.md. Each clause of that
text is cited below next to the code that implements it.

Policy text, verbatim in substance:

  P1. A vendor with a sanctions hit is **rejected**, regardless of anything
      else.
  P2. Absent a sanctions hit, a vendor registered in an embargoed country --
      **KP, IR, or SY** -- is **rejected**.
  P3. Absent a sanctions hit or an embargoed registration, a vendor whose
      risk score is **70 or above** goes to **manual review**.
  P4. Absent a sanctions hit or an embargoed registration, a vendor that
      **handles personal data** and whose risk score is **40 or above but
      below 70** goes to **manual review**.
  P5. Absent a sanctions hit or an embargoed registration, a vendor whose
      risk score is **below 70** is **cleared**, unless P4 applies -- that is,
      a vendor that does not handle personal data clears below 70, and a
      vendor that does handle personal data clears only below 40.

  Trailer. Risk scores are decimal strings and compare numerically.
  Registered countries are two-letter uppercase codes in the ISO 3166-1
  alpha-2 style; the policy consults no registry -- embargo-list membership is
  exact, case-sensitive string comparison against KP, IR, and SY, and any
  other two-letter code is a non-embargoed registration. The three outcomes
  are exhaustive over complete inputs; the policy takes no position on
  incomplete inputs.

Structure of the implementation:

  * ``EMBARGOED`` -- the embargo list from P2, exact and case-sensitive per
    the trailer ("exact, case-sensitive string comparison against KP, IR, and
    SY"). No registry lookup, no normalisation, no aliasing.
  * ``_risk`` -- the trailer's "risk scores are decimal strings and compare
    numerically", realised with ``decimal.Decimal`` so that comparison is
    exact decimal arithmetic. Binary floating point is never used, so
    boundary strings such as "39.999999999999999" and "70.00" land on the
    side the text puts them on.
  * ``verdict`` -- the clause cascade P1 -> P2 -> P3 -> P4 -> P5, in the
    precedence the text states through its "absent ..." preambles.

Boundaries, exactly as written:

  * P3 "70 or above"  -> ``risk >= 70`` (70 inclusive).
  * P4 "40 or above but below 70" -> ``40 <= risk < 70`` (40 inclusive, 70
    exclusive; 70 is already taken by P3, so the two never contend).
  * P5 "below 70" / "clears only below 40" -> the residual: everything the
    earlier clauses did not claim.

Purity: no I/O, no side effects, no globals mutated, no clock, no randomness.
Same input dict -> same string, always.
"""

from decimal import Decimal

__all__ = ["verdict", "EMBARGOED", "CLEAR", "MANUAL_REVIEW", "REJECT"]

# Outcome vocabulary. The policy names three outcomes -- clear, manual review,
# reject -- and the task fixes their spellings as these three strings.
CLEAR = "clear"
MANUAL_REVIEW = "manual-review"
REJECT = "reject"

# P2 + trailer: the embargo list is these three literals and nothing else;
# membership is exact and case-sensitive, with no registry consulted.
EMBARGOED = frozenset({"KP", "IR", "SY"})

# P3 boundary: "70 or above".
_MANUAL_REVIEW_FLOOR = Decimal(70)
# P4 lower boundary: "40 or above".
_PERSONAL_DATA_FLOOR = Decimal(40)


def _risk(raw):
    """Trailer: "Risk scores are decimal strings and compare numerically."

    Parsed with ``Decimal`` so the comparison is exact decimal arithmetic.
    ``float`` is refused outright: converting a decimal string through binary
    floating point can move a value across a boundary the policy states in
    decimal terms, which would be a divergence from the text.
    """
    if isinstance(raw, float):
        raise TypeError(
            "riskScore must be a decimal string; float would make the "
            "comparison inexact"
        )
    if isinstance(raw, Decimal):
        return raw
    if isinstance(raw, str) or isinstance(raw, int):
        # bool is a subclass of int, and is not a risk score.
        if isinstance(raw, bool):
            raise TypeError("riskScore must be a decimal string, not a bool")
        return Decimal(raw)
    raise TypeError("riskScore must be a decimal string")


def verdict(vendor):
    """Return "clear", "manual-review", or "reject" for one vendor record.

    ``vendor`` carries exactly the four facts the policy defines:
    ``sanctionsHit`` (bool), ``registeredCountry`` (uppercase two-letter
    string), ``handlesPersonalData`` (bool), ``riskScore`` (decimal string).

    The clause cascade below is the policy's own precedence: P1 is
    unconditional ("regardless of anything else"), P2 is guarded by "absent a
    sanctions hit", and P3/P4/P5 are each guarded by "absent a sanctions hit
    or an embargoed registration". Returning at the first clause that fires
    reproduces those guards exactly.
    """
    sanctions_hit = vendor["sanctionsHit"]
    registered_country = vendor["registeredCountry"]
    handles_personal_data = vendor["handlesPersonalData"]
    risk = _risk(vendor["riskScore"])

    # P1: "A vendor with a sanctions hit is rejected, regardless of anything
    # else." Nothing is consulted before this test, and nothing overrides it.
    if sanctions_hit:
        return REJECT

    # P2: "Absent a sanctions hit, a vendor registered in an embargoed country
    # -- KP, IR, or SY -- is rejected." Exact, case-sensitive membership per
    # the trailer; "any other two-letter code is a non-embargoed
    # registration", so no normalisation is applied to the input.
    if registered_country in EMBARGOED:
        return REJECT

    # P3: "... a vendor whose risk score is 70 or above goes to manual
    # review." 70 itself is inside this clause.
    if risk >= _MANUAL_REVIEW_FLOOR:
        return MANUAL_REVIEW

    # P4: "... a vendor that handles personal data and whose risk score is 40
    # or above but below 70 goes to manual review." Reaching this line already
    # establishes risk < 70 (P3 returned otherwise), so the upper bound is
    # carried by control flow; 40 is inside the clause, 70 is not.
    if handles_personal_data and risk >= _PERSONAL_DATA_FLOOR:
        return MANUAL_REVIEW

    # P5: "... a vendor whose risk score is below 70 is cleared, unless P4
    # applies -- that is, a vendor that does not handle personal data clears
    # below 70, and a vendor that does handle personal data clears only below
    # 40." Everything the clauses above did not claim is exactly that set: no
    # sanctions hit, non-embargoed registration, risk < 70, and either no
    # personal data or risk < 40.
    return CLEAR
