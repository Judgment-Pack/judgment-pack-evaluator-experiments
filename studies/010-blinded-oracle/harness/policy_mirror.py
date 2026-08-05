#!/usr/bin/env python3
"""The POLICY.md mirror (PREREGISTRATION.md §2, §4): the study's independent
statement of what the policy requires for a vendor, used to split accepted
records into H (concordant) and Q (discordant) and to build the expected
disposition tables. It never reads a pack; a divergence between this mirror
and pack C is exactly what regions_check.py exists to rule out before
anything is locked.
"""
from __future__ import annotations
from decimal import Decimal

EMBARGO = ("KP", "IR", "SY")


def verdict(vendor: dict) -> str:
    """The one outcome POLICY.md P1-P5 assigns to a schema-valid vendor."""
    if vendor["sanctionsHit"]:
        return "reject"
    if vendor["registeredCountry"] in EMBARGO:
        return "reject"
    score = Decimal(vendor["riskScore"])
    if score >= 70:
        return "manual-review"
    if vendor["handlesPersonalData"] and score >= 40:
        return "manual-review"
    return "clear"


def predicate_matches(predicate: dict, vendor: dict) -> bool:
    """Does a vendor fall in a FAMILY.json mutation's affected class?"""
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
