from __future__ import annotations

import itertools

import pytest

from jps_evaluator import (
    PointerResolutionError,
    PointerSyntaxError,
    TriValue,
    compare_decimal_strings,
    evaluate_condition,
    is_decimal_string,
    json_equal,
    resolve_pointer,
    strict_loads,
    strong_all,
    strong_any,
    tri_not,
)
from jps_evaluator.errors import EvaluationInputError


T = TriValue.TRUE
F = TriValue.FALSE
U = TriValue.UNKNOWN


@pytest.mark.parametrize(
    "left,right,all_result,any_result",
    [
        (T, T, T, T),
        (T, F, F, T),
        (T, U, U, T),
        (F, T, F, T),
        (F, F, F, F),
        (F, U, F, U),
        (U, T, U, T),
        (U, F, F, U),
        (U, U, U, U),
    ],
)
def test_strong_three_valued_binary_tables(left, right, all_result, any_result):
    assert strong_all([left, right]) is all_result
    assert strong_any([left, right]) is any_result


@pytest.mark.parametrize("value,result", [(T, F), (F, T), (U, U)])
def test_three_valued_not(value, result):
    assert tri_not(value) is result


def test_condition_tree_uses_strong_logic():
    condition = {
        "op": "all",
        "conditions": [
            {"op": "fact", "path": "/missing", "operator": "equals", "value": 1},
            {"op": "literal", "value": False},
        ],
    }
    assert evaluate_condition(condition, {}) is F


def test_non_string_operator_is_unknown_at_low_level():
    assert evaluate_condition({"op": []}, {}) is U


@pytest.mark.parametrize(
    "value",
    ["0", "-0", "1", "-1", "10.25", "-0.001", "999999999999999999999"],
)
def test_decimal_grammar_accepts_only_pinned_forms(value):
    assert is_decimal_string(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "+1",
        "01",
        "-01",
        ".1",
        "1.",
        "1e2",
        "NaN",
        "Infinity",
        1,
    ],
)
def test_decimal_grammar_rejections(value):
    assert not is_decimal_string(value)


@pytest.mark.parametrize(
    "left,right,result",
    [
        ("1", "1.00", 0),
        ("-0", "0.0", 0),
        ("-2", "-1.99", -1),
        ("100.001", "100", 1),
        ("999999999999999999999999", "1000000000000000000000000", -1),
    ],
)
def test_decimal_mathematical_comparison(left, right, result):
    assert compare_decimal_strings(left, right) == result


def test_ordered_condition_requires_two_decimal_strings():
    condition = {
        "op": "fact",
        "path": "/amount",
        "operator": "greater-than",
        "value": "1",
    }
    assert evaluate_condition(condition, {"amount": "2"}) is T
    assert evaluate_condition(condition, {"amount": 2}) is U
    assert evaluate_condition(condition, {"amount": "2e0"}) is U


def test_pointer_root_objects_arrays_and_escapes():
    document = {"": "empty", "a/b": {"~key": [10, 20]}}
    assert resolve_pointer(document, "") is document
    assert resolve_pointer(document, "/") == "empty"
    assert resolve_pointer(document, "/a~1b/~0key/1") == 20


@pytest.mark.parametrize("pointer", ["missing-slash", "/bad~", "/bad~2escape"])
def test_pointer_syntax_errors(pointer):
    with pytest.raises(PointerSyntaxError):
        resolve_pointer({}, pointer)


@pytest.mark.parametrize("pointer", ["/items/01", "/items/-", "/items/2", "/scalar/x"])
def test_pointer_runtime_traversal_errors(pointer):
    with pytest.raises(PointerResolutionError):
        resolve_pointer({"items": ["a", "b"], "scalar": 1}, pointer)


def test_unresolved_pointer_condition_is_unknown():
    condition = {
        "op": "fact",
        "path": "/items/2",
        "operator": "equals",
        "value": "x",
    }
    assert evaluate_condition(condition, {"items": ["x"]}) is U


def test_type_preserving_recursive_json_equality_and_exact_numbers():
    values = strict_loads(
        '{"one":1,"onePointZero":1.0,"huge":1e999999,"object":{"b":2,"a":[true,null]}}'
    )
    assert json_equal(values["one"], values["onePointZero"]) is True
    assert json_equal(values["one"], True) is False
    assert json_equal(values["one"], "1") is False
    assert json_equal(
        values["object"], {"a": [True, None], "b": 2.0}
    ) is True
    assert json_equal(values["huge"], strict_loads("10e999998")) is True


def test_in_uses_type_preserving_equality():
    condition = {
        "op": "fact",
        "path": "/value",
        "operator": "in",
        "value": [None, "1", 2],
    }
    assert evaluate_condition(condition, {"value": 2.0}) is T
    assert evaluate_condition(condition, {"value": 1}) is F


def test_duplicate_json_member_is_an_explicit_input_error():
    with pytest.raises(EvaluationInputError, match="duplicate"):
        strict_loads('{"same": 1, "same": 2}')
