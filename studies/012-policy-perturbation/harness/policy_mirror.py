#!/usr/bin/env python3
"""The POLICY.md mirror (PREREGISTRATION.md §2, §4): the study's independent
statement of what the policy requires for a vendor, used to split accepted
records into H (concordant) and Q (discordant) and to build the expected
disposition tables. It never reads a pack; a divergence between this mirror
and pack C is exactly what regions_check.py exists to rule out before
anything is locked.

PORTED FROM Study 010's locked `harness/policy_mirror.py`
(276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba) with ONE
enumerated change, registered as [D-14] in §2.2 and published in
`harness/PORTS.md`: **the two threshold comparisons read `T_low` and `T_high`
from the arm's `ARM.json` instead of the literals 40 and 70.** The module is
otherwise line-for-line 010's.

Why one module and not five. Study 010's locked mirror encodes 40 and 70 as
literals and therefore cannot serve arm D, whose thresholds are 45 and 72. The
registered resolution is that exactly ONE mirror artifact exists, at one
destination digest, and each arm's behaviour is keyed to a file that is already
pinned by sha256 before any call (`arms/<X>/ARM.json`) rather than to unpinned
code. §6 C8 clause 6 runs the 280-cell landmark grid against this module at its
registered destination digest, instantiated at each arm's registered pair, and
requires every arm's verdict vector to equal arm A's elementwise.

Registered property, asserted by `harness/tests/test_mirror.py`: at
(T_low, T_high) = (40, 70) this module's `verdict()` agrees with Study 010's
locked module on every cell of the landmark grid — the parameterization changes
what the comparisons READ, and nothing about what they DECIDE.

There are no defaults on the threshold parameters. A caller that does not say
which arm it is scoring gets a TypeError, not arm A's numbers: a silent default
here would let a slot of arm D be labelled at (40, 70) with nothing refusing.
"""
from __future__ import annotations
from decimal import Decimal

EMBARGO = ("KP", "IR", "SY")


def verdict(vendor: dict, t_low, t_high) -> str:
    """The one outcome POLICY.md P1-P5 assigns to a schema-valid vendor, at
    this arm's registered thresholds."""
    if vendor["sanctionsHit"]:
        return "reject"
    if vendor["registeredCountry"] in EMBARGO:
        return "reject"
    score = Decimal(vendor["riskScore"])
    if score >= Decimal(t_high):
        return "manual-review"
    if vendor["handlesPersonalData"] and score >= Decimal(t_low):
        return "manual-review"
    return "clear"


def predicate_matches(predicate: dict, vendor: dict) -> bool:
    """Does a vendor fall in a FAMILY.json mutation's affected class?

    Unchanged from 010's locked bytes, and deliberately NOT parameterized: a
    predicate carries its own numbers, instantiated per arm by §2.3's schema in
    that arm's own `FAMILY.json`. Threading the arm's pair through here as well
    would give one class two sources of truth.
    """
    if vendor["sanctionsHit"] is not predicate["sanctionsHit"]:
        return False
    country = predicate["registeredCountry"]
    if country is not None:
        if country["kind"] == "not-embargoed":
            if vendor["registeredCountry"] in EMBARGO:
                return False
        elif country["kind"] == "equals":
            if vendor["registeredCountry"] != country["value"]:
                return False
        else:
            raise ValueError("unknown country predicate kind: %r" % country)
    personal = predicate["handlesPersonalData"]
    if personal is not None and vendor["handlesPersonalData"] is not personal:
        return False
    score = predicate["riskScore"]
    if score is not None:
        value = Decimal(vendor["riskScore"])
        if "eq" in score and value != Decimal(score["eq"]):
            return False
        if "gte" in score and value < Decimal(score["gte"]):
            return False
        if "lt" in score and value >= Decimal(score["lt"]):
            return False
    return True

