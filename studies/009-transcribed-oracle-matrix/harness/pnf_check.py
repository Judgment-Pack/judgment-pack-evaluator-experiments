#!/usr/bin/env python3
"""The projection-normal-form check (PREREGISTRATION.md §7.3), third-revision
form: the rule is not merely shape-checked, it must BE the one registered
identity projection — canonically equal to REGISTERED_RULE — so nothing about
it is programmable at all. The structural checks below exist to make a
divergence fail with a named reason instead of a bare "not equal".

Under PNF the rule's basis is always [] and carries no information; the
fabrication gate, not basis, binds facts to bytes.
"""
from __future__ import annotations

REGISTERED_RULE = {
    "ruleVersion": "1",
    "clauses": [
        {
            "when": {"op": "always"},
            "claim": {
                "facts": [
                    {"pointer": "/vendor/sanctionsHit", "from": "/vendor/sanctionsHit"},
                    {"pointer": "/vendor/riskScore", "from": "/vendor/riskScore"},
                ],
                "evidence": {},
                "acquisitionStatus": "resolved",
            },
            "reason": "projection",
        }
    ],
}


class PNFError(Exception):
    pass


def check(rule: dict) -> None:
    if not isinstance(rule, dict):
        raise PNFError("the rule must be a JSON object")
    if set(rule) != {"ruleVersion", "clauses"}:
        raise PNFError("top-level members must be exactly ruleVersion/clauses (no parameters member at all)")
    if rule["ruleVersion"] != "1":
        raise PNFError('ruleVersion must be "1"')
    clauses = rule["clauses"]
    if not isinstance(clauses, list) or len(clauses) != 1:
        raise PNFError("PNF requires exactly one clause")
    clause = clauses[0]
    if not isinstance(clause, dict) or set(clause) != {"when", "claim", "reason"}:
        raise PNFError("clause members must be exactly when/claim/reason")
    if clause["when"] != {"op": "always"}:
        raise PNFError('PNF\'s one condition is exactly {"op": "always"}')
    if clause["reason"] != "projection":
        raise PNFError('the registered reason label is "projection"')
    claim = clause["claim"]
    if not isinstance(claim, dict) or set(claim) != {"facts", "evidence", "acquisitionStatus"}:
        raise PNFError("claim members must be exactly facts/evidence/acquisitionStatus")
    if rule != REGISTERED_RULE:
        raise PNFError("the rule is not the registered identity projection")
