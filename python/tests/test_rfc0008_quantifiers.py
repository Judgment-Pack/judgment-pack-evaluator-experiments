"""Conformance rows for the opt-in RFC 0008 aggregate prototype."""

from __future__ import annotations

from copy import deepcopy
import itertools

import pytest

from jps_evaluator import (
    EvaluationBudget,
    EvaluationInputError,
    ResourceLimitError,
    TriValue,
    evaluate,
    evaluate_condition,
    measure_condition_work,
)
from tests.pack_fixtures import base_pack


T = TriValue.TRUE
F = TriValue.FALSE
U = TriValue.UNKNOWN

OK = {"op": "fact", "path": "/ok", "operator": "equals", "value": True}


def aggregate(op, *, path="/items", where=OK):
    return {"op": op, "path": path, "where": deepcopy(where)}


def qeval(condition, facts, evidence=None, *, budget=None):
    return evaluate_condition(
        condition,
        facts,
        evidence,
        budget=budget,
        enable_rfc0008=True,
    )


def condition_pack(condition, *, on_unknown="ignore", fallback="outcome-b"):
    pack = base_pack()
    pack["rules"][0]["when"] = deepcopy(condition)
    pack["rules"][0]["onUnknown"] = on_unknown
    if fallback is not None:
        pack["fallbackOutcome"] = fallback
    return pack


@pytest.mark.parametrize(
    "condition,facts,expected",
    [
        (aggregate("exists"), {"items": [{"ok": False}, {"ok": True}, {"ok": False}]}, T),
        (aggregate("every"), {"items": [{"ok": True}, {"ok": True}, {"ok": True}]}, T),
        (aggregate("exists"), {"items": [{"ok": False}, {"ok": False}]}, F),
        (aggregate("every"), {"items": [{"ok": True}, {"ok": False}]}, F),
        (aggregate("exists"), {"items": [{}, {}]}, U),
        (aggregate("every"), {"items": [{}, {}]}, U),
    ],
)
def test_positive_negative_and_all_missing_rows(condition, facts, expected):
    assert qeval(condition, facts) is expected


def test_depth_two_every_of_exists_is_true():
    condition = aggregate(
        "every",
        path="/rows",
        where=aggregate(
            "exists",
            path="/cells",
            where={"op": "fact", "path": "", "operator": "equals", "value": True},
        ),
    )
    facts = {
        "rows": [
            {"cells": [False, True]},
            {"cells": [True]},
        ]
    }
    assert qeval(condition, facts) is T
    result = evaluate(condition_pack(condition), facts, enable_rfc0008=True)
    assert result["outcomeId"] == "outcome-a"


@pytest.mark.parametrize("op,expected", [("exists", F), ("every", T)])
def test_empty_array_values_are_pinned(op, expected):
    assert qeval(aggregate(op), {"items": []}) is expected


@pytest.mark.parametrize(
    "op,items,expected",
    [
        ("exists", [{}, {"ok": False}], U),
        ("exists", [{}, {"ok": True}], T),
        ("every", [{}, {"ok": True}], U),
        ("every", [{}, {"ok": False}], F),
    ],
)
def test_unknown_and_dominant_values_in_both_directions(op, items, expected):
    assert qeval(aggregate(op), {"items": items}) is expected
    assert qeval(aggregate(op), {"items": list(reversed(items))}) is expected


@pytest.mark.parametrize(
    "op,state,expected",
    [
        ("exists", "present", F),
        ("exists", "absent", F),
        ("every", "present", T),
        ("every", "absent", T),
    ],
)
def test_evidence_present_inside_where_does_not_override_empty_array(
    op, state, expected
):
    condition = aggregate(
        op,
        where={"op": "evidence-present", "evidenceRequirement": "proof"},
    )
    assert qeval(condition, {"items": []}, {"proof": state}) is expected


@pytest.mark.parametrize("value", [{}, "text", 12, None, True])
@pytest.mark.parametrize("op", ["exists", "every"])
def test_non_array_paths_are_unknown_for_both_quantifiers(op, value):
    assert qeval(aggregate(op), {"items": value}) is U


@pytest.mark.parametrize("op", ["exists", "every"])
def test_unresolved_aggregate_path_is_unknown(op):
    assert qeval(aggregate(op), {}) is U


@pytest.mark.parametrize(
    "op,items,expected",
    [
        ("exists", [{"ok": False}, {"ok": False}, {}], U),
        ("exists", [{}, {"ok": True}, {"ok": False}], T),
        ("every", [{"ok": True}, {"ok": True}, {}], U),
        ("every", [{}, {"ok": False}, {"ok": True}], F),
    ],
)
def test_ragged_rows_are_operator_explicit(op, items, expected):
    assert qeval(aggregate(op), {"items": items}) is expected


@pytest.mark.parametrize(
    "op,items",
    [
        ("exists", [{"ok": False}, {"ok": False}, {}]),
        ("every", [{"ok": True}, {"ok": True}, {}]),
    ],
)
@pytest.mark.parametrize(
    "on_unknown,expected_kind,expected_outcome",
    [
        ("ignore", "outcome", "outcome-b"),
        ("escalate", "unresolved", None),
    ],
)
def test_ragged_unknown_rows_show_on_unknown_disposition_divergence(
    op, items, on_unknown, expected_kind, expected_outcome
):
    result = evaluate(
        condition_pack(aggregate(op), on_unknown=on_unknown),
        {"items": items},
        enable_rfc0008=True,
    )
    assert result["kind"] == expected_kind
    if expected_outcome is None:
        assert result["reasons"] == ["unknown"]
    else:
        assert result["outcomeId"] == expected_outcome


@pytest.mark.parametrize(
    "op,element,expected",
    [
        ("exists", {"ok": True}, T),
        ("every", {"ok": True}, T),
        ("exists", {"ok": False}, F),
        ("every", {"ok": False}, F),
        ("exists", {}, U),
        ("every", {}, U),
    ],
)
def test_singleton_rows(op, element, expected):
    assert qeval(aggregate(op), {"items": [element]}) is expected


@pytest.mark.parametrize(
    "items,expected",
    [
        (["gold", "gold"], T),
        (["gold", "silver"], F),
    ],
)
def test_empty_fact_pointer_selects_scalar_element(items, expected):
    condition = aggregate(
        "every",
        where={"op": "fact", "path": "", "operator": "equals", "value": "gold"},
    )
    assert qeval(condition, {"items": items}) is expected


def test_empty_aggregate_path_selects_the_current_root_at_each_level():
    top_level = aggregate(
        "exists",
        path="",
        where={"op": "fact", "path": "", "operator": "equals", "value": "gold"},
    )
    assert qeval(top_level, ["silver", "gold"]) is T

    nested = aggregate(
        "every",
        path="/rows",
        where=aggregate(
            "exists",
            path="",
            where={"op": "fact", "path": "", "operator": "equals", "value": True},
        ),
    )
    assert qeval(nested, {"rows": [[False, True], [True]]}) is T


def test_inner_pointer_wins_on_outer_inner_collision():
    condition = aggregate(
        "every",
        where={
            "op": "fact",
            "path": "/status",
            "operator": "equals",
            "value": "inner",
        },
    )
    facts = {
        "status": "outer",
        "items": [{"status": "inner"}, {"status": "inner"}],
    }
    assert qeval(condition, facts) is T


def test_where_cannot_reach_an_outer_pointer():
    condition = aggregate(
        "exists",
        where={
            "op": "fact",
            "path": "/outer",
            "operator": "equals",
            "value": "wanted",
        },
    )
    assert qeval(condition, {"outer": "wanted", "items": [{}]}) is U


def test_nested_aggregate_path_cannot_reach_facts_root():
    condition = aggregate(
        "exists",
        where=aggregate("exists", path="/shared"),
    )
    facts = {"shared": [{"ok": True}], "items": [{}]}
    assert qeval(condition, facts) is U


def test_inner_where_replaces_outer_element_root():
    condition = aggregate(
        "every",
        where=aggregate(
            "every",
            path="/children",
            where={
                "op": "fact",
                "path": "/flag",
                "operator": "equals",
                "value": True,
            },
        ),
    )
    facts = {"items": [{"flag": True, "children": [{}]}]}
    assert qeval(condition, facts) is U


def test_root_is_restored_for_a_sibling_after_inner_aggregate():
    condition = aggregate(
        "every",
        where={
            "op": "all",
            "conditions": [
                aggregate(
                    "every",
                    path="/children",
                    where={
                        "op": "fact",
                        "path": "/ok",
                        "operator": "equals",
                        "value": True,
                    },
                ),
                {
                    "op": "fact",
                    "path": "/outerFlag",
                    "operator": "equals",
                    "value": True,
                },
            ],
        },
    )
    facts = {
        "items": [
            {"outerFlag": True, "children": [{"ok": True}]},
        ]
    }
    assert qeval(condition, facts) is T


def test_two_sibling_depth_two_aggregates_are_structurally_valid():
    condition = aggregate(
        "every",
        path="/groups",
        where={
            "op": "all",
            "conditions": [
                aggregate("exists", path="/left"),
                aggregate("exists", path="/right"),
            ],
        },
    )
    facts = {
        "groups": [
            {
                "left": [{"ok": True}],
                "right": [{"ok": False}, {"ok": True}],
            }
        ]
    }
    result = evaluate(condition_pack(condition), facts, enable_rfc0008=True)
    assert result["outcomeId"] == "outcome-a"


def _wrapped_third_aggregate(wrapper):
    third = {"op": "uniform", "path": "/third", "at": ""}
    if wrapper == "not":
        wrapped = {"op": "not", "condition": third}
    else:
        wrapped = {"op": wrapper, "conditions": [third]}
    return aggregate(
        "exists",
        path="/outer",
        where=aggregate("exists", path="/inner", where=wrapped),
    )


@pytest.mark.parametrize("wrapper", ["all", "any", "not"])
def test_boolean_wrappers_do_not_launder_depth_three(wrapper):
    pack = condition_pack(_wrapped_third_aggregate(wrapper))
    with pytest.raises(EvaluationInputError, match="aggregate depth 2"):
        evaluate(pack, {}, enable_rfc0008=True)


def test_uniform_counts_as_valid_depth_two_and_invalid_depth_three():
    valid = aggregate(
        "exists",
        path="/groups",
        where={"op": "uniform", "path": "/members", "at": "/v"},
    )
    facts = {"groups": [{"members": [{"v": 1}, {"v": 1}]}]}
    assert evaluate(
        condition_pack(valid), facts, enable_rfc0008=True
    )["outcomeId"] == "outcome-a"

    invalid = aggregate(
        "exists",
        path="/outer",
        where=aggregate(
            "exists",
            path="/inner",
            where={"op": "uniform", "path": "/members", "at": ""},
        ),
    )
    with pytest.raises(EvaluationInputError, match="aggregate depth 2"):
        evaluate(condition_pack(invalid), {}, enable_rfc0008=True)


@pytest.mark.parametrize(
    "at,members,expected",
    [
        ("", [{"a": [1]}, {"a": [1]}], T),
        ("", [{"a": [1]}, {"a": [2]}], F),
        ("/v", [{"v": None}, {"v": None}], T),
        ("/v", [{"v": [1, 2]}, {"v": [1, 2]}], T),
        ("/v", [{"v": [1, 2]}, {"v": [2, 1]}], F),
        ("/v", [{"v": {"a": 1, "b": 2}}, {"v": {"b": 2, "a": 1}}], T),
        ("/v", [{"v": 1}, {"v": 1}, {}], U),
        ("/v", [{"v": 1}, {"v": 2}, {}], F),
        ("/v", [{}], U),
    ],
)
def test_uniform_ordered_truth_table_and_recursive_equality(at, members, expected):
    condition = {"op": "uniform", "path": "/items", "at": at}
    for permutation in itertools.permutations(members):
        assert qeval(condition, {"items": list(permutation)}) is expected


def test_uniform_empty_array_is_true():
    condition = {"op": "uniform", "path": "/items", "at": "/v"}
    assert qeval(condition, {"items": []}) is T


def test_uniform_empty_path_selects_the_current_root_array():
    condition = {"op": "uniform", "path": "", "at": ""}
    assert qeval(condition, [{"v": 1}, {"v": 1}]) is T


@pytest.mark.parametrize("facts", [{}, {"items": {}}, {"items": None}])
def test_uniform_unresolved_or_non_array_path_is_unknown(facts):
    condition = {"op": "uniform", "path": "/items", "at": "/v"}
    assert qeval(condition, facts) is U


def test_uniform_at_is_member_relative_even_when_outer_value_exists():
    condition = {"op": "uniform", "path": "/items", "at": "/v"}
    assert qeval(condition, {"v": 1, "items": [{}, {}]}) is U


@pytest.mark.parametrize(
    "op,items",
    [
        ("exists", [{"ok": False}, {"ok": True}, {"ok": False}]),
        ("every", [{"ok": True}, {"ok": False}, {"ok": True}]),
    ],
)
def test_permutation_and_duplicate_invariance_at_disposition_level(op, items):
    pack = condition_pack(aggregate(op))
    baseline = evaluate(pack, {"items": items}, enable_rfc0008=True)
    for permutation in itertools.permutations(items):
        assert (
            evaluate(pack, {"items": list(permutation)}, enable_rfc0008=True)
            == baseline
        )
    duplicated = items + [deepcopy(items[0])]
    assert evaluate(pack, {"items": duplicated}, enable_rfc0008=True) == baseline


def test_rfc0008_is_rejected_without_explicit_opt_in():
    pack = condition_pack(aggregate("exists"))
    with pytest.raises(EvaluationInputError, match="enable_rfc0008=True"):
        evaluate(pack, {"items": [{"ok": True}]})


def test_low_level_opt_in_must_also_be_an_explicit_boolean():
    with pytest.raises(EvaluationInputError, match="must be a Boolean"):
        evaluate_condition(aggregate("exists"), {"items": []}, enable_rfc0008="yes")


def test_opted_in_disposition_keeps_experimental_no_claim_markers():
    result = evaluate(
        condition_pack(aggregate("exists")),
        {"items": [{"ok": True}]},
        enable_rfc0008=True,
    )
    assert result == {
        "kind": "outcome",
        "outcomeId": "outcome-a",
        "reasons": [],
        "handoff": "none",
        "experimental": True,
        "conformanceClaim": "none",
    }


def test_empty_every_can_gate_a_permissive_outcome():
    result = evaluate(
        condition_pack(aggregate("every")),
        {"items": []},
        enable_rfc0008=True,
    )
    assert result["kind"] == "outcome"
    assert result["outcomeId"] == "outcome-a"


def test_budget_error_is_identical_with_dominant_element_first_or_last():
    pack = condition_pack(aggregate("exists"))
    dominant_first = [{"ok": True}, {"ok": False}, {"ok": False}]
    dominant_last = list(reversed(dominant_first))
    for items in (dominant_first, dominant_last):
        with pytest.raises(ResourceLimitError, match="configured limit of 20"):
            evaluate(
                pack,
                {"items": items},
                enable_rfc0008=True,
                evaluation_work_limit=20,
            )


def test_boolean_subtrees_are_precharged_even_after_a_dominant_branch():
    condition = aggregate(
        "exists",
        where={
            "op": "any",
            "conditions": [
                {"op": "literal", "value": True},
                {
                    "op": "fact",
                    "path": "/large",
                    "operator": "equals",
                    "value": {"payload": "x" * 50},
                },
            ],
        },
    )
    facts = {"items": [{"large": {"payload": "x" * 50}}]}
    charge = measure_condition_work(condition, facts, enable_rfc0008=True)
    with pytest.raises(ResourceLimitError):
        qeval(condition, facts, budget=EvaluationBudget(charge - 1))


def test_ragged_nested_work_is_summed_per_element():
    condition = aggregate(
        "every",
        path="/rows",
        where=aggregate(
            "every",
            path="",
            where={"op": "literal", "value": True},
        ),
    )
    left = {"rows": [[], [1, 2, 3]]}
    right = {"rows": [[1], [2, 3]]}
    left_charge = measure_condition_work(condition, left, enable_rfc0008=True)
    right_charge = measure_condition_work(condition, right, enable_rfc0008=True)
    assert left_charge == right_charge


def test_sibling_aggregate_work_is_additive():
    left = aggregate("exists", path="/left")
    right = aggregate("every", path="/right")
    combined = {"op": "all", "conditions": [left, right]}
    facts = {
        "left": [{"ok": True}],
        "right": [{"ok": True}, {"ok": False}],
    }
    assert measure_condition_work(
        combined, facts, enable_rfc0008=True
    ) == 1 + measure_condition_work(
        left, facts, enable_rfc0008=True
    ) + measure_condition_work(
        right, facts, enable_rfc0008=True
    )


def test_failed_inner_pointer_resolution_still_has_a_preflight_charge():
    condition = aggregate(
        "every",
        where=aggregate("exists", path="/missing"),
    )
    no_outer_members = measure_condition_work(
        condition, {"items": []}, enable_rfc0008=True
    )
    one_failed_lookup = measure_condition_work(
        condition, {"items": [{}]}, enable_rfc0008=True
    )
    assert one_failed_lookup > no_outer_members


def test_uniform_deep_equality_is_charged_by_runtime_value_size():
    condition = {"op": "uniform", "path": "/items", "at": "/v"}
    scalar_charge = measure_condition_work(
        condition,
        {"items": [{"v": "x"}, {"v": "x"}]},
        enable_rfc0008=True,
    )
    composite_charge = measure_condition_work(
        condition,
        {
            "items": [
                {"v": {"payload": ["x" * 20]}},
                {"v": {"payload": ["x" * 20]}},
            ]
        },
        enable_rfc0008=True,
    )
    assert composite_charge > scalar_charge
