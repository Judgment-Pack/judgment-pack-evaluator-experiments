from __future__ import annotations

import pytest

from jps_evaluator import EvaluationInputError, TriValue, evaluate, evaluate_condition
from tests.pack_fixtures import base_pack


@pytest.mark.parametrize(
    "evidence,result",
    [
        ({"proof": "present"}, TriValue.TRUE),
        ({"proof": "absent"}, TriValue.FALSE),
        ({"proof": "unknown"}, TriValue.UNKNOWN),
        ({}, TriValue.UNKNOWN),
    ],
)
def test_evidence_present_tri_state(evidence, result):
    condition = {"op": "evidence-present", "evidenceRequirement": "proof"}
    assert evaluate_condition(condition, {}, evidence) is result


def required_pack():
    pack = base_pack()
    pack["evidenceRequirements"] = [
        {"id": "proof-a", "description": "A", "required": True},
        {"id": "proof-b", "description": "B", "required": True},
    ]
    pack["fallbackOutcome"] = "outcome-a"
    return pack


def test_omitted_evidence_object_makes_required_evidence_unknown():
    result = evaluate(required_pack(), {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["unknown"]


def test_absent_required_evidence_dominates_unknown_required_evidence():
    result = evaluate(
        required_pack(), {}, {"proof-a": "absent", "proof-b": "unknown"}
    )
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["missing-required-evidence"]


def test_undeclared_evidence_key_is_input_error():
    with pytest.raises(EvaluationInputError, match="undeclared"):
        evaluate(required_pack(), {}, {"other": "present"})


@pytest.mark.parametrize("state", ["yes", True, None, []])
def test_invalid_evidence_state_is_input_error(state):
    with pytest.raises(EvaluationInputError):
        evaluate(required_pack(), {}, {"proof-a": state})
