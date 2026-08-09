"""Deterministic Arm A deciders for the offline phase.

Neither is a model. The oracle proves the plumbing scores a correct decider as
correct; the adversary is the negative control: its registered wrong decisions must
produce the registered failing signals on these fixed cells (no wider
discrimination claim). A real
model decider (policy prose + facts) is the gated paid phase and is absent
from the offline pilots by design.

Deciders receive only the PUBLIC case view (id, pack, caseType) plus facts,
evidence, and the action map — never the registered expectation. The oracle
loads the expectation registry itself: it is a disclosed tautological positive
control, and this is the one place the answer key is allowed to be read.
"""

import json
import os


def _expect(case_id):
    study = os.environ["STUDY_DIR"]
    with open(os.path.join(study, "scenarios", "jps", "cases.json")) as f:
        registry = json.load(f)
    return next(c for c in registry["cases"] if c["id"] == case_id)["expect"]


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
    expect = _expect(case["id"])
    return {
        "disposition": _to_disposition(expect),
        "handoffTarget": expect.get("handoffTarget"),
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
