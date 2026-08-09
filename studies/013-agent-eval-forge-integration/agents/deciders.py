"""Deterministic Arm A deciders for the offline phase.

Neither is a model. The oracle proves the plumbing scores a correct decider as
correct; the adversary proves the harness discriminates — every registered
metric that should catch a wrong decision must catch the adversary. A real
model decider (policy prose + facts) is the gated paid phase and is absent
from the offline pilots by design.
"""


def _to_disposition(expect):
    d = {
        "kind": expect["kind"],
        "reasons": list(expect["reasons"]),
        "handoff": {"state": expect["handoff"]},
    }
    if expect["handoff"] == "requested":
        d["handoff"]["triggeredBy"] = list(expect["triggeredBy"])
    if expect["kind"] == "outcome":
        d["outcomeId"] = expect["outcomeId"]
    return d


def oracle(case, facts, evidence, action_map):
    """Emits the registered expected disposition for the case (harness validation only)."""
    return {
        "disposition": _to_disposition(case["expect"]),
        "handoffTarget": case["expect"].get("handoffTarget"),
    }


def adversary(case, facts, evidence, action_map):
    """Always 'approves': picks the pack's first execute-mapped outcome.

    Registered wrong behavior — false approvals on every non-execute case,
    wrong outcome on record cases. The harness must catch all of it.
    """
    outcome = sorted(o for o, m in action_map.items() if m.startswith("execute:"))[0]
    return {
        "disposition": {"kind": "outcome", "outcomeId": outcome, "reasons": [], "handoff": {"state": "none"}},
        "handoffTarget": None,
    }
