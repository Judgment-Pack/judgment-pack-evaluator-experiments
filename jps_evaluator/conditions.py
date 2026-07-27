"""Three-valued condition interpretation pinned by RFC 0006."""

from __future__ import annotations

from enum import Enum
import re
from typing import Any, Iterable, Mapping

from .errors import (
    EvaluationInputError,
    PointerError,
    PointerResolutionError,
    PointerSyntaxError,
    ResourceLimitError,
)
from .json_input import ExactJSONNumber


MAX_CONDITION_EVALUATIONS = 200_000

_DECIMAL_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_ARRAY_INDEX_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
_ORDERED_OPERATORS = {
    "greater-than",
    "greater-than-or-equal",
    "less-than",
    "less-than-or-equal",
}


class TriValue(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class EvaluationBudget:
    """Shared condition-work counter for one evaluation."""

    __slots__ = ("remaining",)

    def __init__(self, limit: int = MAX_CONDITION_EVALUATIONS) -> None:
        self.remaining = limit

    def consume(self) -> None:
        self.remaining -= 1
        if self.remaining < 0:
            raise ResourceLimitError(
                f"evaluation exceeds {MAX_CONDITION_EVALUATIONS} condition evaluations"
            )


def strong_all(values: Iterable[TriValue]) -> TriValue:
    values = tuple(values)
    if any(value is TriValue.FALSE for value in values):
        return TriValue.FALSE
    if all(value is TriValue.TRUE for value in values):
        return TriValue.TRUE
    return TriValue.UNKNOWN


def strong_any(values: Iterable[TriValue]) -> TriValue:
    values = tuple(values)
    if any(value is TriValue.TRUE for value in values):
        return TriValue.TRUE
    if all(value is TriValue.FALSE for value in values):
        return TriValue.FALSE
    return TriValue.UNKNOWN


def tri_not(value: TriValue) -> TriValue:
    if value is TriValue.TRUE:
        return TriValue.FALSE
    if value is TriValue.FALSE:
        return TriValue.TRUE
    return TriValue.UNKNOWN


def is_decimal_string(value: Any) -> bool:
    return isinstance(value, str) and _DECIMAL_RE.fullmatch(value) is not None


def compare_decimal_strings(left: Any, right: Any) -> int | None:
    """Compare two grammar-conforming decimal strings, or return None if incomparable."""

    if not is_decimal_string(left) or not is_decimal_string(right):
        return None
    return ExactJSONNumber.parse(left).compare(ExactJSONNumber.parse(right))


def resolve_pointer(document: Any, pointer: str) -> Any:
    """Resolve RFC 6901 JSON Pointer or raise a precise pointer error."""

    tokens = _pointer_tokens(pointer)
    current = document
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                raise PointerResolutionError(f"object member {token!r} does not exist")
            current = current[token]
            continue
        if isinstance(current, list):
            if _ARRAY_INDEX_RE.fullmatch(token) is None:
                raise PointerResolutionError(f"{token!r} is not a valid array index")
            # Evaluator collections are bounded, so a longer token cannot resolve.
            if len(token) > len(str(max(len(current) - 1, 0))) + 1:
                raise PointerResolutionError(f"array index {token!r} is out of bounds")
            try:
                index = int(token)
            except ValueError as exc:
                raise PointerResolutionError(f"array index {token!r} is too large") from exc
            if index >= len(current):
                raise PointerResolutionError(f"array index {token!r} is out of bounds")
            current = current[index]
            continue
        raise PointerResolutionError("pointer attempts to traverse a scalar value")
    return current


def _pointer_tokens(pointer: str) -> list[str]:
    if not isinstance(pointer, str):
        raise PointerSyntaxError("JSON Pointer must be a string")
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise PointerSyntaxError("non-empty JSON Pointer must begin with '/'")
    return [_decode_pointer_token(token) for token in pointer[1:].split("/")]


def _decode_pointer_token(token: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(token):
        character = token[index]
        if character != "~":
            result.append(character)
            index += 1
            continue
        if index + 1 >= len(token) or token[index + 1] not in {"0", "1"}:
            raise PointerSyntaxError("JSON Pointer contains an invalid '~' escape")
        result.append("~" if token[index + 1] == "0" else "/")
        index += 2
    return "".join(result)


def evaluate_condition(
    condition: Any,
    facts: Any,
    evidence: Mapping[str, str] | None = None,
    *,
    budget: EvaluationBudget | None = None,
) -> TriValue:
    """Interpret one condition. Malformed/unsupported low-level shapes produce unknown."""

    if budget is None:
        budget = EvaluationBudget()
    budget.consume()
    evidence = evidence or {}

    if not isinstance(condition, dict):
        return TriValue.UNKNOWN
    op = condition.get("op")
    if not isinstance(op, str):
        return TriValue.UNKNOWN

    if op == "literal":
        value = condition.get("value")
        if not isinstance(value, bool):
            return TriValue.UNKNOWN
        return TriValue.TRUE if value else TriValue.FALSE

    if op in {"all", "any"}:
        children = condition.get("conditions")
        if not isinstance(children, list) or not children:
            return TriValue.UNKNOWN
        values = (
            evaluate_condition(child, facts, evidence, budget=budget) for child in children
        )
        return strong_all(values) if op == "all" else strong_any(values)

    if op == "not":
        if "condition" not in condition:
            return TriValue.UNKNOWN
        return tri_not(
            evaluate_condition(condition["condition"], facts, evidence, budget=budget)
        )

    if op == "evidence-present":
        requirement = condition.get("evidenceRequirement")
        if not isinstance(requirement, str):
            return TriValue.UNKNOWN
        state = evidence.get(requirement, "unknown")
        if state == "present":
            return TriValue.TRUE
        if state == "absent":
            return TriValue.FALSE
        return TriValue.UNKNOWN

    if op != "fact":
        return TriValue.UNKNOWN
    path = condition.get("path")
    operator = condition.get("operator")
    if not isinstance(path, str) or not isinstance(operator, str) or "value" not in condition:
        return TriValue.UNKNOWN
    try:
        selected = resolve_pointer(facts, path)
    except PointerError:
        return TriValue.UNKNOWN

    operand = condition["value"]
    if operator in {"equals", "not-equals"}:
        equal = json_equal(selected, operand)
        if equal is None:
            return TriValue.UNKNOWN
        if operator == "not-equals":
            equal = not equal
        return TriValue.TRUE if equal else TriValue.FALSE

    if operator == "in":
        if not isinstance(operand, list) or not operand:
            return TriValue.UNKNOWN
        saw_unknown = False
        for candidate in operand:
            equal = json_equal(selected, candidate)
            if equal is True:
                return TriValue.TRUE
            if equal is None:
                saw_unknown = True
        return TriValue.UNKNOWN if saw_unknown else TriValue.FALSE

    if operator in _ORDERED_OPERATORS:
        comparison = compare_decimal_strings(selected, operand)
        if comparison is None:
            return TriValue.UNKNOWN
        matches = {
            "greater-than": comparison > 0,
            "greater-than-or-equal": comparison >= 0,
            "less-than": comparison < 0,
            "less-than-or-equal": comparison <= 0,
        }[operator]
        return TriValue.TRUE if matches else TriValue.FALSE

    return TriValue.UNKNOWN


def json_equal(left: Any, right: Any) -> bool | None:
    """Type-preserving, exact JSON equality; None means equality is indeterminate."""

    left_kind = _json_kind(left)
    right_kind = _json_kind(right)
    if "invalid" in {left_kind, right_kind}:
        return None
    if left_kind != right_kind:
        return False

    if left_kind in {"null", "boolean", "string"}:
        return left == right
    if left_kind == "number":
        left_number = _as_exact_number(left)
        right_number = _as_exact_number(right)
        if left_number is None or right_number is None:
            return None
        return left_number.compare(right_number) == 0
    if left_kind == "array":
        if len(left) != len(right):
            return False
        for left_item, right_item in zip(left, right):
            equal = json_equal(left_item, right_item)
            if equal is not True:
                return equal
        return True
    if left_kind == "object":
        if left.keys() != right.keys():
            return False
        for key in left:
            equal = json_equal(left[key], right[key])
            if equal is not True:
                return equal
        return True
    return None


def _json_kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (ExactJSONNumber, int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return "object"
    return "invalid"


def _as_exact_number(value: Any) -> ExactJSONNumber | None:
    if isinstance(value, ExactJSONNumber):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        try:
            return ExactJSONNumber.parse(str(value))
        except (ValueError, EvaluationInputError, ResourceLimitError):
            return None
    if isinstance(value, float):
        try:
            return ExactJSONNumber.parse(repr(value))
        except (ValueError, EvaluationInputError, ResourceLimitError):
            return None
    return None
