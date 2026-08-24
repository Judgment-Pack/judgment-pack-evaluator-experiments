#!/usr/bin/env python3
"""Mechanically de-formalize arm C's result contract into arm B's informal prose.

Study 019, arms B and C. `contract-b.md` is the output of this script; committing both
makes the derivation checkable. The point of the derivation is that arm B's contract states
the *same field names and allowed values* as arm C's schema and nothing more: every piece of
machine-checkable structure (the schema itself, the JSON Schema keywords, the registered
default rule, and every prescriptive convention in convention-c.md) is dropped, and what
survives is rendered as English sentences.

Usage:
    python3 deformalize.py                 # write contract-b.md next to this script
    python3 deformalize.py --stdout        # print the rendering instead
    python3 deformalize.py --check         # exit 1 if contract-b.md is stale

The renderer handles exactly the JSON Schema vocabulary used by the source block and
refuses anything else, so a change to the schema that this script cannot faithfully
de-formalize fails loudly instead of being silently dropped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "convention-c.md"
TARGET = HERE / "contract-b.md"

SCHEMA_MARKER = "<!-- SCHEMA:result-contract -->"

# Deliberately says nothing about what this file was derived FROM: the assembler strips HTML
# comments before a prompt is shown, but if that ever regressed, an arm-B author must still
# learn nothing about arm C's materials from this line. Full provenance is in the docstring.
GENERATED_BANNER = "<!-- GENERATED FILE. Do not edit by hand; regenerate with deformalize.py. -->"

# JSON Schema keywords this renderer knows how to speak. Anything else is a hard error.
ALLOWED_ROOT = {
    "$schema",
    "title",
    "type",
    "additionalProperties",
    "required",
    "properties",
    "allOf",
}
ALLOWED_PROPERTY = {"type", "enum", "items"}
ALLOWED_ITEMS = {"type", "enum"}
ALLOWED_CONDITION = {"const", "not"}
ALLOWED_CONSEQUENT = {"minItems", "maxItems"}


class DerivationError(RuntimeError):
    pass


def extract_schema(text: str) -> dict:
    """Pull the fenced JSON block that follows the schema marker."""
    idx = text.find(SCHEMA_MARKER)
    if idx < 0:
        raise DerivationError(f"marker {SCHEMA_MARKER!r} not found in {SOURCE.name}")
    fence = re.compile(r"^```json[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)
    match = fence.search(text, idx)
    if match is None:
        raise DerivationError("no fenced ```json block after the schema marker")
    return json.loads(match.group(1))


def _reject_unknown(where: str, obj: dict, allowed: set[str]) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise DerivationError(f"unsupported schema keyword(s) in {where}: {unknown}")


def _quoted_list(values: list[str], conjunction: str) -> str:
    quoted = [f'"{v}"' for v in values]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + f" {conjunction} " + quoted[-1]


def _noun(name: str) -> str:
    """How a field is referred to in prose. Field names are used verbatim."""
    return name


def render_properties(schema: dict) -> list[str]:
    sentences: list[str] = []
    required = schema.get("required", [])
    for name, spec in schema["properties"].items():
        _reject_unknown(f"property {name!r}", spec, ALLOWED_PROPERTY)
        obligation = "must have" if name in required else "may have"
        if spec.get("type") == "string" and "enum" in spec:
            sentences.append(
                f"It {obligation} a {_noun(name)} field, and its value is one of "
                f"{_quoted_list(spec['enum'], 'or')}."
            )
        elif spec.get("type") == "array":
            items = spec.get("items", {})
            _reject_unknown(f"items of {name!r}", items, ALLOWED_ITEMS)
            if "enum" in items:
                sentences.append(
                    f"It {obligation} a {_noun(name)} field, which is a list whose entries "
                    f"are drawn from {_quoted_list(items['enum'], 'and')}."
                )
            else:
                raise DerivationError(f"array property {name!r} has no enumerated items")
        else:
            raise DerivationError(f"cannot de-formalize property {name!r}: {spec}")
    return sentences


def render_closure(schema: dict) -> list[str]:
    if schema.get("additionalProperties") is False:
        names = list(schema["properties"])
        return [f"It has no fields other than {_quoted_list(names, 'and')}."]
    return []


def _condition_prose(cond: dict) -> tuple[str, str]:
    """Return (field, English description of the condition on it)."""
    props = cond.get("properties")
    if not props or len(props) != 1:
        raise DerivationError(f"cannot de-formalize condition: {cond}")
    field, test = next(iter(props.items()))
    _reject_unknown(f"condition on {field!r}", test, ALLOWED_CONDITION)
    if "const" in test:
        return field, f'is "{test["const"]}"'
    if "not" in test:
        inner = test["not"]
        _reject_unknown(f"negated condition on {field!r}", inner, ALLOWED_CONDITION)
        if "const" in inner:
            return field, f'is anything other than "{inner["const"]}"'
    raise DerivationError(f"cannot de-formalize condition on {field!r}: {test}")


def _consequent_prose(then: dict) -> tuple[str, str]:
    props = then.get("properties")
    if not props or len(props) != 1:
        raise DerivationError(f"cannot de-formalize consequent: {then}")
    field, test = next(iter(props.items()))
    _reject_unknown(f"consequent on {field!r}", test, ALLOWED_CONSEQUENT)
    if test.get("maxItems") == 0:
        return field, "is empty"
    if test.get("minItems") == 1:
        return field, "has at least one entry"
    raise DerivationError(f"cannot de-formalize consequent on {field!r}: {test}")


def render_conditionals(schema: dict) -> list[str]:
    sentences: list[str] = []
    for clause in schema.get("allOf", []):
        _reject_unknown("allOf clause", clause, {"if", "then"})
        cond_field, cond = _condition_prose(clause["if"])
        cons_field, cons = _consequent_prose(clause["then"])
        sentences.append(
            f"When the {_noun(cond_field)} {cond}, the {_noun(cons_field)} list {cons}."
        )
    return sentences


def render(schema: dict) -> str:
    _reject_unknown("the schema root", schema, ALLOWED_ROOT)
    if schema.get("type") != "object":
        raise DerivationError("the result contract root must be an object schema")
    title = schema.get("title", "result")

    body = [f"Your policy must produce a {title} object."]
    body += render_properties(schema)
    body += render_conditionals(schema)
    body += render_closure(schema)

    lines = [
        GENERATED_BANNER,
        "",
        "# What your policy must produce (arm B)",
        "",
        " ".join(body),
        "",
        "Use those field names and those values exactly as spelled here.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true", help="print instead of writing")
    parser.add_argument("--check", action="store_true", help="fail if the output is stale")
    args = parser.parse_args(argv)

    try:
        schema = extract_schema(SOURCE.read_text(encoding="utf-8"))
        rendered = render(schema)
    except DerivationError as exc:
        print(f"deformalize: {exc}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(rendered)
        return 0
    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != rendered:
            print(f"deformalize: {TARGET.name} is stale; re-run deformalize.py", file=sys.stderr)
            return 1
        print(f"deformalize: {TARGET.name} matches the schema in {SOURCE.name}")
        return 0

    TARGET.write_text(rendered, encoding="utf-8")
    print(f"deformalize: wrote {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
