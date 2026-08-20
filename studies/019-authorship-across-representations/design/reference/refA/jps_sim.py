#!/usr/bin/env python3
"""A Python re-implementation of JPS Core 0.2.0-draft SS7/SS8 as the pinned
runtime (jpack 0.17.0, internal/evaluation/{condition,resolve}.go) implements
it. Used ONLY to enumerate onUnknown assignments cheaply; every reported
result for the final pack comes from the pinned binary, and the simulator is
checked against the binary cell-for-cell over the whole grid.
"""

from decimal import Decimal
import re

T, F, U = "true", "false", "unknown"
DECIMAL = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")


def _resolve(doc, pointer):
    """RFC 6901 over the small subset the grid uses."""
    if pointer == "":
        return doc, True
    node = doc
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and token in node:
            node = node[token]
        else:
            return None, False
    return node, True


def _decimal(value):
    if isinstance(value, str) and DECIMAL.match(value):
        return Decimal(value)
    return None


ORDERED = {"greater-than", "greater-than-or-equal", "less-than", "less-than-or-equal"}


def _tri(flag):
    return T if flag else F


def evaluate(node, facts, evidence):
    op = node.get("op")
    if op == "literal":
        return _tri(bool(node["value"]))
    if op == "all":
        saw_unknown = False
        for child in node["conditions"]:
            verdict = evaluate(child, facts, evidence)
            if verdict == F:
                return F
            if verdict == U:
                saw_unknown = True
        return U if saw_unknown else T
    if op == "any":
        saw_unknown = False
        for child in node["conditions"]:
            verdict = evaluate(child, facts, evidence)
            if verdict == T:
                return T
            if verdict == U:
                saw_unknown = True
        return U if saw_unknown else F
    if op == "not":
        verdict = evaluate(node["condition"], facts, evidence)
        return {T: F, F: T, U: U}[verdict]
    if op == "evidence-present":
        return evidence.get(node["evidenceRequirement"], U)
    if op == "fact":
        value, resolved = _resolve(facts, node["path"])
        if not resolved:
            return U
        operator, operand = node["operator"], node["value"]
        if operator in ORDERED:
            left, right = _decimal(value), _decimal(operand)
            if left is None or right is None:
                return U
            if operator == "greater-than":
                return _tri(left > right)
            if operator == "greater-than-or-equal":
                return _tri(left >= right)
            if operator == "less-than":
                return _tri(left < right)
            return _tri(left <= right)
        if operator == "equals":
            return _tri(value == operand)
        if operator == "not-equals":
            return _tri(value != operand)
        if operator == "in":
            return _tri(any(value == item for item in operand))
        return U
    return U


def profile(pack, facts, evidence):
    """Everything about one (pack-structure, inputs) pair that is independent of
    the onUnknown assignment: the step-2 evidence reason, each exception's
    verdict, the suppression set implied by the true suppressions, and each
    rule's verdict. Evaluating an assignment against a profile is then pure
    bookkeeping, which is what makes a 2048-assignment sweep cheap."""
    reasons = set()
    required_false = required_unknown = False
    for requirement in pack.get("evidenceRequirements", []):
        if not requirement.get("required"):
            continue
        state = evidence.get(requirement["id"], U)
        if state == F:
            required_false = True
        elif state == U:
            required_unknown = True
    if required_false:
        reasons.add("missing-required-evidence")
    elif required_unknown:
        reasons.add("unknown")

    exceptions = []
    for exception in pack.get("exceptions", []):
        exceptions.append((exception, evaluate(exception["when"], facts, evidence)))
    rules = []
    for rule in pack["rules"]:
        rules.append((rule, evaluate(rule["when"], facts, evidence)))
    return {"base_reasons": reasons, "exceptions": exceptions, "rules": rules}


def resolve_profile(pack, prof, rule_unknown, exception_unknown):
    """SS8 steps 2-10 over a profile, with the onUnknown assignment supplied as
    two id -> "ignore"|"escalate" maps."""
    reasons = set(prof["base_reasons"])
    suppressed, forced = set(), set()
    direct_escalation = False
    for exception, verdict in prof["exceptions"]:
        if verdict == U:
            if exception_unknown.get(exception["id"], exception["onUnknown"]) == "escalate":
                reasons.add("unknown")
        elif verdict == T:
            effect = exception["effect"]
            if effect == "suppress-rule":
                suppressed.add(exception["targetRule"])
            elif effect == "force-outcome":
                forced.add(exception["outcome"])
            elif effect == "escalate":
                direct_escalation = True
                reasons.add("exception-escalation")
    if len(forced) > 1:
        reasons.add("conflict")
    if reasons:
        return ("unresolved", frozenset(reasons))
    if len(forced) == 1:
        return ("outcome", next(iter(forced)))

    candidates = set()
    for rule, verdict in prof["rules"]:
        if rule["id"] in suppressed:
            continue
        if verdict == T:
            candidates.add(rule["outcome"])
        elif verdict == U:
            if rule_unknown.get(rule["id"], rule["onUnknown"]) == "escalate":
                reasons.add("unknown")
    if len(candidates) > 1:
        reasons.add("conflict")
    if reasons:
        return ("unresolved", frozenset(reasons))
    if len(candidates) == 1:
        return ("outcome", next(iter(candidates)))
    if "fallbackOutcome" in pack:
        return ("outcome", pack["fallbackOutcome"])
    return ("unresolved", frozenset({"no-match"}))


def evaluate_cell(pack, facts, evidence, rule_unknown=None, exception_unknown=None):
    prof = profile(pack, facts, evidence)
    return resolve_profile(pack, prof, rule_unknown or {}, exception_unknown or {})
