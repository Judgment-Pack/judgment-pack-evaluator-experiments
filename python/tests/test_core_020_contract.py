from __future__ import annotations

from copy import deepcopy
import importlib

import pytest

from jps_evaluator import (
    EvaluationInputError,
    PackNotConformantError,
    ResourceLimitError,
    UnsupportedExtensionError,
    canonicalize_disposition,
    evaluate,
)
from tests.pack_fixtures import base_pack


def required_extension_pack() -> dict:
    pack = base_pack()
    pack["metadata"] = {
        "requiredExtensions": ["com.example.required"],
    }
    pack["extensions"] = {
        "com.example.required": {"ignored": True},
    }
    return pack


def fact_rule(rule_id: str, outcome: str, path: str, *, on_unknown: str) -> dict:
    return {
        "id": rule_id,
        "description": rule_id,
        "when": {
            "op": "fact",
            "path": path,
            "operator": "equals",
            "value": True,
        },
        "outcome": outcome,
        "onUnknown": on_unknown,
    }


def test_020_pack_is_accepted_where_010_was_accepted():
    old = evaluate(base_pack(), {})
    pack = base_pack()
    pack["specVersion"] = "0.2.0-draft"
    assert evaluate(pack, {}) == old


def test_preflight_pack_failure_has_first_precedence():
    pack = required_extension_pack()
    pack["title"] = ""
    with pytest.raises(PackNotConformantError) as raised:
        evaluate(
            pack,
            {"not-json": object()},
            ["not-an-object"],
            supported_extensions=[],
            evaluation_work_limit=1,
        )
    assert raised.value.error_class == "pack-not-conformant"
    assert raised.value.phase == "preflight"


def test_preflight_facts_then_evidence_then_required_extensions():
    pack = required_extension_pack()

    with pytest.raises(EvaluationInputError, match="facts") as facts_error:
        evaluate(pack, {"not-json": object()}, ["not-an-object"])
    assert facts_error.value.error_class == "malformed-input"
    assert facts_error.value.phase == "preflight"

    with pytest.raises(EvaluationInputError, match="JSON object") as evidence_error:
        evaluate(pack, {}, ["not-an-object"])
    assert evidence_error.value.error_class == "malformed-input"
    assert evidence_error.value.phase == "preflight"

    with pytest.raises(UnsupportedExtensionError) as extension_error:
        evaluate(pack, {}, {})
    assert extension_error.value.error_class == "unsupported-required-extension"
    assert extension_error.value.phase == "preflight"


@pytest.mark.parametrize(
    "evidence,message",
    [
        ([], "JSON object"),
        ({"undeclared": "present"}, "undeclared"),
        ({"proof": "yes"}, "present.*absent.*unknown"),
    ],
)
def test_every_evidence_shape_violation_is_malformed_input(evidence, message):
    pack = base_pack()
    pack["evidenceRequirements"] = [
        {"id": "proof", "description": "Proof.", "required": False}
    ]
    with pytest.raises(EvaluationInputError, match=message) as raised:
        evaluate(pack, {}, evidence)
    assert raised.value.error_class == "malformed-input"
    assert raised.value.phase == "preflight"


def test_preflight_finishes_before_false_applicability_can_return():
    pack = base_pack()
    pack["applicability"] = {"op": "literal", "value": False}
    with pytest.raises(EvaluationInputError, match="undeclared"):
        evaluate(pack, {}, {"not-declared": "present"})


def test_omitted_evidence_is_the_implicit_empty_object():
    pack = base_pack()
    pack["evidenceRequirements"] = [
        {"id": "proof", "description": "Proof.", "required": True}
    ]
    assert evaluate(pack, {}) == evaluate(pack, {}, {})
    assert evaluate(pack, {})["reasons"] == ["unknown"]


def test_portable_disposition_members_sets_and_trigger_subset():
    pack = base_pack()
    pack["rules"] = [
        {
            "id": "true-a",
            "description": "True A.",
            "when": {"op": "literal", "value": True},
            "outcome": "outcome-a",
            "onUnknown": "ignore",
        },
        {
            "id": "true-b",
            "description": "True B.",
            "when": {"op": "literal", "value": True},
            "outcome": "outcome-b",
            "onUnknown": "ignore",
        },
        fact_rule("unknown-c", "outcome-c", "/missing", on_unknown="escalate"),
    ]
    pack["escalation"] = {
        "triggers": ["conflict"],
        "target": {"kind": "queue", "name": "Review"},
    }

    disposition = evaluate(pack, {})
    assert disposition == {
        "kind": "unresolved",
        "reasons": ["conflict", "unknown"],
        "handoff": {
            "state": "requested",
            "triggeredBy": ["conflict"],
        },
    }
    assert set(disposition) == {"kind", "reasons", "handoff"}
    assert "outcomeId" not in disposition


def test_outcome_disposition_has_outcome_id_and_empty_reasons():
    pack = base_pack()
    pack["rules"][0]["when"] = {"op": "literal", "value": True}
    disposition = evaluate(pack, {})
    assert disposition == {
        "kind": "outcome",
        "outcomeId": "outcome-a",
        "reasons": [],
        "handoff": {"state": "none"},
    }


def test_jcs_bytes_use_sorted_members_and_minimal_string_escapes():
    disposition = {
        "z": ["é"],
        "a": {"text": "\n/\b"},
    }
    assert canonicalize_disposition(disposition) == (
        b'{"a":{"text":"\\n/\\b"},"z":["\xc3\xa9"]}'
    )

    outcome = {
        "kind": "outcome",
        "outcomeId": "proceed",
        "reasons": [],
        "handoff": {"state": "none"},
    }
    assert canonicalize_disposition(outcome) == (
        b'{"handoff":{"state":"none"},"kind":"outcome",'
        b'"outcomeId":"proceed","reasons":[]}'
    )


def test_all_four_core_error_classes_and_phases():
    malformed_pack = base_pack()
    malformed_pack["unknownRootMember"] = True
    with pytest.raises(PackNotConformantError) as pack_error:
        evaluate(malformed_pack, {})

    with pytest.raises(EvaluationInputError) as input_error:
        evaluate(base_pack(), {}, [])

    with pytest.raises(UnsupportedExtensionError) as extension_error:
        evaluate(required_extension_pack(), {})

    work_pack = base_pack()
    work_pack["rules"] = [
        fact_rule("work", "outcome-a", "/value", on_unknown="ignore")
    ]
    with pytest.raises(ResourceLimitError) as resource_error:
        evaluate(work_pack, {"value": True}, evaluation_work_limit=1)

    assert [
        (error.value.error_class, error.value.phase)
        for error in (
            pack_error,
            input_error,
            extension_error,
            resource_error,
        )
    ] == [
        ("pack-not-conformant", "preflight"),
        ("malformed-input", "preflight"),
        ("unsupported-required-extension", "preflight"),
        ("resource-exhaustion", "evaluation"),
    ]


def test_unsupported_extension_precedes_evaluation_resource_exhaustion():
    pack = required_extension_pack()
    pack["rules"] = [
        fact_rule("work", "outcome-a", "/value", on_unknown="ignore")
    ]
    with pytest.raises(UnsupportedExtensionError):
        evaluate(pack, {"value": True}, evaluation_work_limit=1)


def test_collection_limit_is_resource_exhaustion_during_evaluation(monkeypatch):
    evaluator_module = importlib.import_module("jps_evaluator.evaluator")
    monkeypatch.setattr(evaluator_module, "MAX_EVALUATION_COLLECTION_ITEMS", 3)
    with pytest.raises(ResourceLimitError) as raised:
        evaluate(base_pack(), {})
    assert raised.value.error_class == "resource-exhaustion"
    assert raised.value.phase == "evaluation"


def test_pack_validation_covers_non_evaluation_schema_fields():
    pack = deepcopy(base_pack())
    pack["metadata"] = {
        "createdAt": "not-a-date-time",
    }
    with pytest.raises(PackNotConformantError, match="date-time"):
        evaluate(pack, {})
