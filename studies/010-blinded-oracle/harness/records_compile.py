#!/usr/bin/env python3
"""The frozen stdout-to-records compiler (PREREGISTRATION.md §4): raw
authoring stdout in, record files and RECORDS.md out, with no operator
judgment anywhere in between.

Extraction: the single JSON array from the first `[` to its matching `]`,
found by parsing, not bracket counting — everything before and after is
retained in the raw stream but ignored. Admission: an element is accepted
iff it matches the closed record schema exactly; there is no repair of any
kind. Every source index is accounted for in RECORDS.md as either its
accepted caseId or a stable drop code:

  schema        - not the closed record object shape (members, types)
  decimal-form  - riskScore is not a canonical decimal string
  country-form  - registeredCountry is not an uppercase ISO-alpha-2 shape
  id-form       - caseId is not kebab-case
  outcome-value - decision.outcome is not one of the three outcomes
  duplicate-id  - a previously accepted element already claimed the caseId

`compile` writes records/ and RECORDS.md; `verify` regenerates both from the
retained raw stdout and requires byte equality with what is on disk.

Usage: records_compile.py compile|verify <raw-stdout-file>
"""
from __future__ import annotations
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)

RECORDS_DIR = os.path.join(STUDY, "records")
RECORDS_MD = os.path.join(STUDY, "RECORDS.md")

DECIMAL = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$")
COUNTRY = re.compile(r"^[A-Z]{2}$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
OUTCOMES = ("clear", "manual-review", "reject")

RECORD_MEMBERS = {"caseId", "vendor", "decision"}
VENDOR_MEMBERS = {"legalName", "sanctionsHit", "registeredCountry",
                  "handlesPersonalData", "riskScore"}
DECISION_MEMBERS = {"outcome", "decidedBy", "decidedAt"}


class CompileError(Exception):
    pass


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def extract_array(raw: str) -> tuple[list, tuple[int, int]]:
    """(the array, its [start, end) span): the parseable JSON array spanning
    the most characters; ties go to the earliest. Deterministic and
    judgment-free: scan `[` occurrences left to right, parse each candidate
    with a strict decoder that rejects duplicate object keys anywhere, keep
    the widest span. A `[` inside prose either fails to parse (skipped) or
    parses as a short bracketed aside that any real record array out-spans.
    Nothing is repaired.
    """
    decoder = json.JSONDecoder(object_pairs_hook=_refuse_duplicate_keys)
    best, best_span = None, None
    start = raw.find("[")
    while start >= 0:
        try:
            decoded, end = decoder.raw_decode(raw, start)
        except ValueError:
            decoded, end = None, start
        if isinstance(decoded, list) and (best_span is None or end - start > best_span[1] - best_span[0]):
            best, best_span = decoded, (start, end)
        start = raw.find("[", start + 1)
    if best is None:
        raise CompileError("the raw stream contains no parseable JSON array")
    return best, best_span


def classify(element, seen: set) -> tuple[str, str]:
    """(caseId, "") when accepted, ("", drop code) when dropped."""
    if not isinstance(element, dict) or set(element) != RECORD_MEMBERS \
            or not isinstance(element.get("vendor"), dict) \
            or not isinstance(element.get("decision"), dict) \
            or set(element["vendor"]) != VENDOR_MEMBERS \
            or set(element["decision"]) != DECISION_MEMBERS:
        return "", "schema"
    vendor, decision = element["vendor"], element["decision"]
    if not isinstance(element["caseId"], str) or not isinstance(vendor["legalName"], str) \
            or not isinstance(vendor["sanctionsHit"], bool) \
            or not isinstance(vendor["registeredCountry"], str) \
            or not isinstance(vendor["handlesPersonalData"], bool) \
            or not isinstance(vendor["riskScore"], str) \
            or not isinstance(decision["outcome"], str) \
            or not isinstance(decision["decidedBy"], str) \
            or not isinstance(decision["decidedAt"], str):
        return "", "schema"
    if not DECIMAL.match(vendor["riskScore"]):
        return "", "decimal-form"
    if not COUNTRY.match(vendor["registeredCountry"]):
        return "", "country-form"
    if not KEBAB.match(element["caseId"]) or element["caseId"].startswith("k-"):
        return "", "id-form"
    if decision["outcome"] not in OUTCOMES:
        return "", "outcome-value"
    if element["caseId"] in seen:
        return "", "duplicate-id"
    return element["caseId"], ""


def compile_records(raw: str) -> tuple[dict, list, tuple[int, int, int]]:
    """({caseId: record}, ledger rows of (index, caseId-or-empty, drop
    code), (span start, span end, stream length))."""
    array, span = extract_array(raw)
    accepted: dict = {}
    ledger = []
    for index, element in enumerate(array):
        case_id, drop = classify(element, set(accepted))
        if case_id:
            accepted[case_id] = element
        ledger.append((index, case_id, drop))
    return accepted, ledger, (span[0], span[1], len(raw))


def records_md(ledger: list, accepted: dict, span: tuple[int, int, int]) -> str:
    lines = [
        "# Compiled records — the authoring ledger",
        "",
        "Every element of the authored array, in source order: accepted as its",
        "caseId, or dropped with a stable code (records_compile.py's docstring",
        "names them). Regenerable byte-for-byte from the retained completion.",
        "",
        "Selected array span: characters %d-%d of %d; everything outside the"
        % span,
        "span was retained and ignored.",
        "",
        "| # | caseId | disposition |",
        "|---|--------|-------------|",
    ]
    for index, case_id, drop in ledger:
        if case_id:
            record = accepted[case_id]
            lines.append("| %d | `%s` | accepted: %s, %s, personal=%s, score \"%s\", outcome %s |" % (
                index, case_id,
                "sanctioned" if record["vendor"]["sanctionsHit"] else "unsanctioned",
                record["vendor"]["registeredCountry"],
                str(record["vendor"]["handlesPersonalData"]).lower(),
                record["vendor"]["riskScore"], record["decision"]["outcome"]))
        else:
            lines.append("| %d | — | dropped: %s |" % (index, drop))
    lines.append("")
    return "\n".join(lines)


def render(accepted: dict, ledger: list, span: tuple[int, int, int]) -> dict:
    """{relative path: bytes} for everything the compiler owns."""
    files = {"RECORDS.md": records_md(ledger, accepted, span).encode()}
    for case_id, record in accepted.items():
        body = json.dumps(record, indent=2, sort_keys=True) + "\n"
        files[os.path.join("records", case_id + ".json")] = body.encode()
    return files


def cmd_compile(raw_path: str) -> None:
    raw = open(raw_path, encoding="utf-8").read()
    accepted, ledger, span = compile_records(raw)
    if os.path.isdir(RECORDS_DIR) and os.listdir(RECORDS_DIR):
        raise CompileError("records/ already holds files; the compiler never overwrites")
    os.makedirs(RECORDS_DIR, exist_ok=True)
    for relative, body in render(accepted, ledger, span).items():
        with open(os.path.join(STUDY, relative), "wb") as handle:
            handle.write(body)
    print("compiled: %d accepted, %d dropped" % (
        len(accepted), len(ledger) - len(accepted)))


def cmd_verify(raw_path: str) -> None:
    raw = open(raw_path, encoding="utf-8").read()
    accepted, ledger, span = compile_records(raw)
    for relative, body in render(accepted, ledger, span).items():
        on_disk = open(os.path.join(STUDY, relative), "rb").read()
        if on_disk != body:
            raise CompileError("%s is not what the retained completion compiles to" % relative)
    present = set(name for name in os.listdir(RECORDS_DIR) if name.endswith(".json"))
    if present != {case_id + ".json" for case_id in accepted}:
        raise CompileError("records/ holds files the retained completion does not compile to")
    print("verify: ok (%d records regenerate byte-for-byte)" % len(accepted))


def main(argv: list) -> int:
    if len(argv) != 3 or argv[1] not in ("compile", "verify"):
        print("usage: records_compile.py compile|verify <raw-stdout-file>", file=sys.stderr)
        return 2
    try:
        (cmd_compile if argv[1] == "compile" else cmd_verify)(argv[2])
    except (CompileError, ValueError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
