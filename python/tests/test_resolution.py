from __future__ import annotations

from copy import deepcopy

import pytest

from jps_evaluator import (
    EvaluationInputError,
    PackNotConformantError,
    UnsupportedExtensionError,
    evaluate,
)
from tests.pack_fixtures import base_pack


def true_rule(rule_id, outcome):
    return {
        "id": rule_id,
        "description": rule_id,
        "when": {"op": "literal", "value": True},
        "outcome": outcome,
        "onUnknown": "ignore",
    }


def exception(exception_id, effect, **fields):
    return {
        "id": exception_id,
        "description": exception_id,
        "when": {"op": "literal", "value": True},
        "effect": effect,
        "onUnknown": "ignore",
        **fields,
    }


def test_conflicting_true_rules_are_never_tie_broken():
    pack = base_pack()
    pack["rules"] = [true_rule("rule-a", "outcome-a"), true_rule("rule-b", "outcome-b")]
    result = evaluate(pack, {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["conflict"]


def test_multiple_true_rules_for_same_outcome_are_compatible():
    pack = base_pack()
    pack["rules"] = [true_rule("rule-a", "outcome-a"), true_rule("rule-b", "outcome-a")]
    result = evaluate(pack, {})
    assert result["kind"] == "outcome"
    assert result["outcomeId"] == "outcome-a"
    assert result["reasons"] == []


def test_unknown_and_conflicting_rules_retain_both_reasons():
    pack = base_pack()
    pack["rules"] = [
        true_rule("rule-a", "outcome-a"),
        true_rule("rule-b", "outcome-b"),
        {
            "id": "rule-c",
            "description": "Unknown blocker.",
            "when": {
                "op": "fact",
                "path": "/missing",
                "operator": "equals",
                "value": True,
            },
            "outcome": "outcome-c",
            "onUnknown": "escalate",
        },
    ]
    result = evaluate(pack, {})
    assert result["kind"] == "unresolved"
    assert set(result["reasons"]) == {"unknown", "conflict"}


def test_unknown_ignore_allows_fallback_but_unknown_escalate_blocks_it():
    pack = base_pack()
    pack["fallbackOutcome"] = "outcome-b"
    pack["rules"][0]["when"] = {
        "op": "fact",
        "path": "/missing",
        "operator": "equals",
        "value": True,
    }
    assert evaluate(pack, {})["outcomeId"] == "outcome-b"
    pack["rules"][0]["onUnknown"] = "escalate"
    result = evaluate(pack, {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["unknown"]


def test_no_match_without_fallback():
    result = evaluate(base_pack(), {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["no-match"]
    assert result["handoff"] == {"state": "none"}


def test_suppression_removes_rule_and_force_bypasses_normal_rules():
    pack = base_pack()
    pack["rules"] = [true_rule("rule-a", "outcome-a"), true_rule("rule-b", "outcome-b")]
    pack["exceptions"] = [
        exception("suppress-a", "suppress-rule", targetRule="rule-a")
    ]
    assert evaluate(pack, {})["outcomeId"] == "outcome-b"

    pack["exceptions"].append(
        exception("force-c", "force-outcome", outcome="outcome-c")
    )
    assert evaluate(pack, {})["outcomeId"] == "outcome-c"


def test_conflicting_forced_outcomes_block_and_request_configured_handoff():
    pack = base_pack()
    pack["exceptions"] = [
        exception("force-a", "force-outcome", outcome="outcome-a"),
        exception("force-b", "force-outcome", outcome="outcome-b"),
    ]
    pack["escalation"] = {
        "triggers": ["conflict"],
        "target": {"kind": "human-role", "name": "Reviewer"},
    }
    result = evaluate(pack, {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["conflict"]
    assert result["handoff"] == {
        "state": "requested",
        "triggeredBy": ["conflict"],
    }


def test_direct_exception_escalation_requests_handoff_without_configuration():
    pack = base_pack()
    pack["exceptions"] = [exception("direct", "escalate")]
    result = evaluate(pack, {})
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["exception-escalation"]
    assert result["handoff"] == {
        "state": "requested",
        "triggeredBy": ["exception-escalation"],
    }


def test_missing_evidence_does_not_prevent_exception_reason_inspection():
    pack = base_pack()
    pack["evidenceRequirements"] = [
        {"id": "proof", "description": "Proof.", "required": True}
    ]
    pack["exceptions"] = [
        {
            "id": "unknown-exception",
            "description": "Unknown exception.",
            "when": {
                "op": "fact",
                "path": "/missing",
                "operator": "equals",
                "value": True,
            },
            "effect": "force-outcome",
            "outcome": "outcome-a",
            "onUnknown": "escalate",
        }
    ]
    result = evaluate(pack, {}, {"proof": "absent"})
    assert set(result["reasons"]) == {"missing-required-evidence", "unknown"}


def test_unsupported_required_extension_is_an_error_and_optional_is_inert():
    pack = base_pack()
    pack["metadata"] = {"requiredExtensions": ["com.example.required"]}
    pack["extensions"] = {
        "com.example.required": {"op": "literal", "value": True},
        "com.example.optional": {
            "rules": [true_rule("hostile-rule", "outcome-c")]
        },
    }
    with pytest.raises(UnsupportedExtensionError):
        evaluate(pack, {})
    result = evaluate(pack, {}, supported_extensions=["com.example.required"])
    assert result["kind"] == "unresolved"
    assert result["reasons"] == ["no-match"]


def test_outcome_id_is_forbidden_on_non_outcome_and_disposition_has_only_core_members():
    result = evaluate(base_pack(), {})
    assert "outcomeId" not in result
    assert set(result) == {"kind", "reasons", "handoff"}


def test_malformed_pack_condition_is_an_explicit_error():
    pack = base_pack()
    pack["rules"][0]["when"] = {
        "op": "fact",
        "path": "not-a-pointer",
        "operator": "equals",
        "value": True,
    }
    with pytest.raises(PackNotConformantError, match="Pointer"):
        evaluate(pack, {})


@pytest.mark.parametrize(
    "mutation",
    [
        lambda pack: pack["rules"][0].update({"onUnknown": []}),
        lambda pack: pack.update({"applicability": None}),
        lambda pack: pack.update({"fallbackOutcome": None}),
        lambda pack: pack.update({"escalation": None}),
    ],
)
def test_malformed_evaluation_fields_never_leak_python_type_errors(mutation):
    pack = base_pack()
    mutation(pack)
    with pytest.raises(PackNotConformantError):
        evaluate(pack, {})
