"""Experimental RFC 0006 evaluator with opt-in RFC 0008 aggregates."""

from .conditions import (
    DEFAULT_EVALUATION_WORK_LIMIT,
    EvaluationBudget,
    TriValue,
    compare_decimal_strings,
    evaluate_condition,
    is_decimal_string,
    json_equal,
    measure_condition_work,
    resolve_pointer,
    strong_all,
    strong_any,
    tri_not,
)
from .errors import (
    EvaluationError,
    EvaluationInputError,
    PointerResolutionError,
    PointerSyntaxError,
    ResourceLimitError,
    UnsupportedExtensionError,
)
from .evaluator import evaluate
from .json_input import ExactJSONNumber, load_json_file, normalize_json, strict_loads

__all__ = [
    "DEFAULT_EVALUATION_WORK_LIMIT",
    "EvaluationBudget",
    "EvaluationError",
    "EvaluationInputError",
    "ExactJSONNumber",
    "PointerResolutionError",
    "PointerSyntaxError",
    "ResourceLimitError",
    "TriValue",
    "UnsupportedExtensionError",
    "compare_decimal_strings",
    "evaluate",
    "evaluate_condition",
    "is_decimal_string",
    "json_equal",
    "load_json_file",
    "normalize_json",
    "measure_condition_work",
    "resolve_pointer",
    "strict_loads",
    "strong_all",
    "strong_any",
    "tri_not",
]
