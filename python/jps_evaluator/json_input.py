"""Strict JSON loading and exact JSON-number support."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

from .errors import EvaluationInputError


MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
MAX_NESTING_DEPTH = 128
MAX_JSON_ITEMS = 200_000
MAX_STRING_CHARACTERS = 1024 * 1024
MAX_NUMBER_CHARACTERS = 4_096

_JSON_NUMBER_RE = re.compile(
    r"^(?P<sign>-)?(?P<integer>0|[1-9][0-9]*)"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?:[eE](?P<exponent>[+-]?[0-9]+))?$"
)


@dataclass(frozen=True)
class ExactJSONNumber:
    """A JSON number represented exactly as a normalized base-ten integer and exponent."""

    lexeme: str
    sign: int
    digits: str
    exponent: int

    @classmethod
    def parse(cls, lexeme: str) -> "ExactJSONNumber":
        if not isinstance(lexeme, str):
            raise EvaluationInputError("a JSON-number token must be text")
        match = _JSON_NUMBER_RE.fullmatch(lexeme)
        if match is None:
            raise EvaluationInputError(f"invalid JSON number {lexeme!r}")

        integer = match.group("integer")
        fraction = match.group("fraction") or ""
        coefficient = (integer + fraction).lstrip("0")
        if not coefficient:
            return cls(lexeme=lexeme, sign=0, digits="0", exponent=0)

        exponent_text = match.group("exponent")
        try:
            exponent = int(exponent_text) if exponent_text is not None else 0
        except ValueError as exc:
            raise EvaluationInputError(
                "JSON-number exponent is too large to represent"
            ) from exc
        exponent -= len(fraction)

        trailing_zeroes = len(coefficient) - len(coefficient.rstrip("0"))
        if trailing_zeroes:
            coefficient = coefficient[:-trailing_zeroes]
            exponent += trailing_zeroes

        sign = -1 if match.group("sign") else 1
        return cls(lexeme=lexeme, sign=sign, digits=coefficient, exponent=exponent)

    def compare(self, other: "ExactJSONNumber") -> int:
        """Return -1, 0, or 1 using exact mathematical ordering."""

        if self.sign != other.sign:
            return -1 if self.sign < other.sign else 1
        if self.sign == 0:
            return 0

        magnitude = self._compare_magnitude(other)
        return magnitude if self.sign > 0 else -magnitude

    def _compare_magnitude(self, other: "ExactJSONNumber") -> int:
        self_place = len(self.digits) + self.exponent
        other_place = len(other.digits) + other.exponent
        if self_place != other_place:
            return -1 if self_place < other_place else 1

        width = max(len(self.digits), len(other.digits))
        left = self.digits.ljust(width, "0")
        right = other.digits.ljust(width, "0")
        if left == right:
            return 0
        return -1 if left < right else 1


def _reject_constant(token: str) -> None:
    raise EvaluationInputError(f"{token!r} is not a JSON value")


def _parse_json_number_token(token: str) -> ExactJSONNumber:
    if len(token) > MAX_NUMBER_CHARACTERS:
        raise EvaluationInputError(
            f"JSON-number token exceeds {MAX_NUMBER_CHARACTERS} characters"
        )
    return ExactJSONNumber.parse(token)


def _unique_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationInputError(f"duplicate JSON object member {key!r}")
        result[key] = value
    return result


def strict_loads(text: str, *, source: str = "JSON input") -> Any:
    """Load one complete JSON text, rejecting duplicates and retaining exact numbers."""

    if not isinstance(text, str):
        raise EvaluationInputError(f"{source} must be supplied as text")
    if len(text.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise EvaluationInputError(f"{source} exceeds {MAX_DOCUMENT_BYTES} bytes")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_int=_parse_json_number_token,
            parse_float=_parse_json_number_token,
            parse_constant=_reject_constant,
        )
    except EvaluationInputError:
        raise
    except json.JSONDecodeError as exc:
        raise EvaluationInputError(
            f"{source} is malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except RecursionError as exc:
        raise EvaluationInputError(f"{source} exceeds the nesting limit") from exc
    return normalize_json(value, source=source)


def load_json_file(path: str | Path) -> Any:
    """Read and strictly decode a size-bounded UTF-8 JSON file."""

    path_text = str(path)
    try:
        with open(path, "rb") as handle:
            payload = handle.read(MAX_DOCUMENT_BYTES + 1)
    except OSError as exc:
        raise EvaluationInputError(f"cannot read {path_text!r}: {exc}") from exc
    if len(payload) > MAX_DOCUMENT_BYTES:
        raise EvaluationInputError(f"{path_text!r} exceeds {MAX_DOCUMENT_BYTES} bytes")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvaluationInputError(f"{path_text!r} is not UTF-8 JSON text") from exc
    return strict_loads(text, source=path_text)


def normalize_json(value: Any, *, source: str = "JSON input") -> Any:
    """Validate the Python value as bounded JSON and normalize all numbers exactly."""

    count = [0]
    try:
        return _normalize_json(value, source=source, depth=0, count=count)
    except RecursionError as exc:
        raise EvaluationInputError(f"{source} exceeds the nesting limit") from exc


def _normalize_json(value: Any, *, source: str, depth: int, count: list[int]) -> Any:
    if depth > MAX_NESTING_DEPTH:
        raise EvaluationInputError(f"{source} exceeds nesting depth {MAX_NESTING_DEPTH}")
    count[0] += 1
    if count[0] > MAX_JSON_ITEMS:
        raise EvaluationInputError(f"{source} exceeds {MAX_JSON_ITEMS} JSON values/members")

    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        _check_string(value, source)
        return value
    if isinstance(value, ExactJSONNumber):
        return _parse_json_number_token(value.lexeme)
    if isinstance(value, int):
        try:
            token = str(value)
        except ValueError as exc:
            raise EvaluationInputError(f"{source} contains an oversized integer") from exc
        return _parse_json_number_token(token)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise EvaluationInputError(f"{source} contains a non-finite number")
        return ExactJSONNumber.parse(repr(value))
    if isinstance(value, list):
        return [
            _normalize_json(item, source=source, depth=depth + 1, count=count)
            for item in value
        ]
    if isinstance(value, dict):
        count[0] += len(value)
        if count[0] > MAX_JSON_ITEMS:
            raise EvaluationInputError(
                f"{source} exceeds {MAX_JSON_ITEMS} JSON values/members"
            )
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise EvaluationInputError(f"{source} contains a non-string object member name")
            _check_string(key, source)
            result[key] = _normalize_json(
                item, source=source, depth=depth + 1, count=count
            )
        return result
    raise EvaluationInputError(
        f"{source} contains non-JSON value of type {type(value).__name__}"
    )


def _check_string(value: str, source: str) -> None:
    if len(value) > MAX_STRING_CHARACTERS:
        raise EvaluationInputError(
            f"{source} contains text exceeding {MAX_STRING_CHARACTERS} characters"
        )
