#!/usr/bin/env python3
"""The completion-to-records compiler, ported from Study 010 (harness/PORTS.md
records the source digest and every change): a transcript-bound completion in,
record files and RECORDS.md out, with no operator judgment anywhere in between.

Study 011 runs this once per authoring run, over that run's retained
completion bytes, and keeps the result in memory: there is no committed
records/ tree here, because every run has its own. What it deliberately does
NOT do, and 010 did: own a single study-wide records/ directory, or decide
anything about coverage — the caller passes an output root, and the mirror
does the classifying.

Extraction: the parseable JSON array spanning the most characters (ties to
the earliest), scanned by strict parsing — duplicate object keys and
non-JSON constants disqualify a candidate; everything outside the selected
span is retained but ignored, and its offsets are recorded. Admission: an
element is accepted iff it passes, in this registered order, each check —
the first failure's code is the drop code; there is no repair of any kind:

  schema         - not the closed record object shape (members, types)
  decimal-form   - riskScore is not a canonical decimal string
  country-form   - registeredCountry is not two uppercase ASCII letters
  id-form        - caseId is not kebab-case, or claims the reserved k- prefix
  outcome-value  - decision.outcome is not one of the three outcomes
  timestamp-form - decision.decidedAt is not YYYY-MM-DDTHH:MM:SSZ
  duplicate-id   - a previously ACCEPTED element already claimed the caseId

`compile` writes records/ and RECORDS.md beneath the given output root;
`verify` regenerates both from the retained completion bytes and requires
byte equality and the exact file set, nothing extra, all regular files.

Usage: records_compile.py compile|verify <completion-file> <output-root>
"""
from __future__ import annotations
import json
import os
import re
import sys

DECIMAL = re.compile(r"(0|[1-9][0-9]*)(\.[0-9]*[1-9])?")
COUNTRY = re.compile(r"[A-Z]{2}")
KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
OUTCOMES = ("clear", "manual-review", "reject")

def _is_utc_timestamp(value: str) -> bool:
    """YYYY-MM-DDTHH:MM:SSZ AND a real calendar instant: the prompt asks
    for ISO 8601 UTC, so the shape check enforces the calendar too."""
    if not TIMESTAMP.fullmatch(value):
        return False
    import datetime
    try:
        datetime.datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]),
                          int(value[11:13]), int(value[14:16]), int(value[17:19]))
    except ValueError:
        return False
    return True


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


class JsonNumber:
    """A JSON number literal, kept unconverted. Not a str, not an int: the
    record schema requires strings, and this type satisfies neither the
    string checks nor any arithmetic the compiler never performs."""

    __slots__ = ("literal",)

    def __init__(self, literal: str):
        self.literal = literal

    def __repr__(self) -> str:
        return "JsonNumber(%s)" % self.literal


def _refuse_constants(value):
    # NaN/Infinity are Python-decoder extensions, not JSON; a candidate
    # containing them is not a JSON array and must not win extraction.
    raise ValueError("non-JSON constant %r" % value)


def extract_array(raw: str) -> tuple[list, tuple[int, int]]:
    """(the array, its [start, end) span): the parseable JSON array spanning
    the most characters; ties go to the earliest. Deterministic and
    judgment-free: scan `[` occurrences left to right, parse each candidate
    with a strict decoder that rejects duplicate object keys anywhere, keep
    the widest span. A `[` inside prose either fails to parse (skipped) or
    parses as a short bracketed aside that any real record array out-spans.
    Nothing is repaired.
    """
    # Numbers become JsonNumber tokens, never Python ints/floats: the
    # host's integer-string digit limit cannot change WHICH array is
    # selected, and — because JsonNumber is not a str — a JSON number
    # still fails the schema wherever a JSON string is required.
    decoder = json.JSONDecoder(object_pairs_hook=_refuse_duplicate_keys,
                               parse_constant=_refuse_constants,
                               parse_int=JsonNumber, parse_float=JsonNumber)
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
    if not DECIMAL.fullmatch(vendor["riskScore"]):
        return "", "decimal-form"
    if not COUNTRY.fullmatch(vendor["registeredCountry"]):
        return "", "country-form"
    if not KEBAB.fullmatch(element["caseId"]) or element["caseId"].startswith("k-"):
        return "", "id-form"
    if decision["outcome"] not in OUTCOMES:
        return "", "outcome-value"
    if not _is_utc_timestamp(decision["decidedAt"]):
        return "", "timestamp-form"
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


def read_completion(raw_path: str) -> str:
    """Byte-exact read: no newline translation, so spans and equality track
    the transcript-bound completion bytes."""
    return open(raw_path, "rb").read().decode("utf-8")


def cmd_compile(raw_path: str, out_root: str) -> None:
    raw = read_completion(raw_path)
    accepted, ledger, span = compile_records(raw)
    records_dir = os.path.join(out_root, "records")
    if os.path.isdir(records_dir) and os.listdir(records_dir):
        raise CompileError("records/ already holds files; the compiler never overwrites")
    os.makedirs(records_dir, exist_ok=True)
    for relative, body in render(accepted, ledger, span).items():
        with open(os.path.join(out_root, relative), "wb") as handle:
            handle.write(body)
    print("compiled: %d accepted, %d dropped" % (
        len(accepted), len(ledger) - len(accepted)))


def cmd_verify(raw_path: str, out_root: str) -> None:
    raw = read_completion(raw_path)
    accepted, ledger, span = compile_records(raw)
    records_dir = os.path.join(out_root, "records")
    records_md_path = os.path.join(out_root, "RECORDS.md")
    for relative, body in render(accepted, ledger, span).items():
        on_disk = open(os.path.join(out_root, relative), "rb").read()
        if on_disk != body:
            raise CompileError("%s is not what the retained completion compiles to" % relative)
    # The directory must hold EXACTLY the compiled record files — no extra
    # entries of any name or type.
    present = set(os.listdir(records_dir))
    expected = {case_id + ".json" for case_id in accepted}
    if present != expected:
        raise CompileError("records/ holds entries the retained completion does not compile to: %s"
                           % sorted(present ^ expected))
    for name in present:
        path = os.path.join(records_dir, name)
        if os.path.islink(path) or not os.path.isfile(path):
            raise CompileError("records/%s is not a regular file" % name)
    for path, label in ((records_md_path, "RECORDS.md"), (records_dir, "records/")):
        if os.path.islink(path):
            raise CompileError("%s is a symlink" % label)
    print("verify: ok (%d records regenerate byte-for-byte)" % len(accepted))


def main(argv: list) -> int:
    if len(argv) != 4 or argv[1] not in ("compile", "verify"):
        print("usage: records_compile.py compile|verify <completion-file> <output-root>",
              file=sys.stderr)
        return 2
    try:
        (cmd_compile if argv[1] == "compile" else cmd_verify)(argv[2], argv[3])
    except (CompileError, ValueError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
