#!/usr/bin/env python3
"""Sufficiency and fairness check for the arm B / arm C prompt materials (Study 019).

Three independent assertions:

1. **Sufficiency.** Every Rego construct that the frozen reference implementation
   `reference/refB/policy.rego` actually uses is documented in `rego-excerpt.md`. Each
   construct has (a) a detector that decides whether the reference uses it, and (b) an
   anchor comment that must be present in the excerpt. Constructs marked `always` must be
   documented whether or not the reference happens to use them (they are named in the
   registered derivation rule).

2. **Policy-content prohibition** (the same prohibition arm A's check applies to arm A's
   materials; `POLICY_CONTENT_BANLIST` and `REGISTERED_IDENTIFIER_BANLIST` below are the
   shared lists and are importable). The prompt materials teach the language and the
   required output form; they must never leak the policy's solution structure. Tier 2
   (`POLICY_CONTENT_BANLIST`) is banned in every arm-B/C material. Tier 1
   (`REGISTERED_IDENTIFIER_BANLIST`) is the set of identifiers the shared naming appendix
   already publishes to every arm: allowed in the result-contract materials, banned in the
   language reference, which must stay language-only.

3. **Derivation and fairness integrity.** `contract-b.md` is exactly what `deformalize.py`
   emits from `convention-c.md`; the two arm suffixes are byte-identical outside their
   embedded contract/convention; and each suffix embeds its file verbatim.

Usage:
    python3 check_sufficiency.py [--opa /path/to/opa]

With `--opa`, every ```rego block in `rego-excerpt.md` is additionally compiled with the
pinned binary, so the reference cannot document a construct with an example that does not
parse.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE.parent.parent
REFERENCE = DESIGN / "reference" / "refB" / "policy.rego"

EXCERPT = HERE / "rego-excerpt.md"
CONVENTION = HERE / "convention-c.md"
CONTRACT = HERE / "contract-b.md"
SUFFIX_B = HERE / "suffix-b.md"
SUFFIX_C = HERE / "suffix-c.md"

CONTRACT_MATERIALS = [CONVENTION, CONTRACT, SUFFIX_B, SUFFIX_C]
ALL_MATERIALS = [EXCERPT] + CONTRACT_MATERIALS

# --------------------------------------------------------------------------------------
# Tier 2: policy content. Banned in every arm material, every arm. Shared with arm A.
# --------------------------------------------------------------------------------------
POLICY_CONTENT_BANLIST: list[tuple[str, str]] = [
    # Clause labels from the policy prose.
    (r"\b(?:P1|D1|D2|D3|D4|D5|D6[abc]?|D7|D8|O1|O2|O3|U1)\b", "clause label"),
    # Domain vocabulary of the stimulus.
    (r"(?i)\bvendors?\b", "domain noun"),
    (r"(?i)\bsanctions?\b", "domain noun"),
    (r"(?i)\bscreening\b", "domain noun"),
    (r"(?i)\bspend\b", "domain noun"),
    (r"(?i)\binsurance\b", "domain noun"),
    (r"(?i)\bcertificate\b", "domain noun"),
    (r"(?i)\bsuppliers?\b", "domain noun"),
    (r"(?i)\benforcement\b", "domain noun"),
    (r"(?i)\bonboard", "domain noun"),
    (r"(?i)\bfinancial\b", "domain noun"),
    (r"(?i)\baudited\b", "domain noun"),
    (r"(?i)\bcountry risk\b", "domain noun"),
    (r"(?i)\brisk scores?\b", "domain noun"),
    (r"(?i)\bcompliance desk\b", "routing target"),
    (r"vendor-compliance-desk", "routing target"),
    # Registered input identifiers (in the naming appendix; not needed in these materials).
    (r"\briskScore\b|\brequestedSpend\b|\bsanctionsStatus\b|\bcountryRisk\b", "input id"),
    (r"\bnewVendor\b|\bcriticalSupplier\b|\bpriorEnforcement\b", "input id"),
    (r"financial-evidence|insurance-certificate", "input id"),
    # Input state literals.
    (r"\b(?:CLEAR|MATCH|UNKNOWN|LOW|MEDIUM|HIGH)\b", "input state literal"),
    # Threshold values.
    (r"\b(?:40|70|90)\b", "threshold numeral"),
    (r"\b(?:100000|500000|2000000|10000000)(?:\.\d+)?\b", "threshold numeral"),
    (r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", "threshold numeral (grouped)"),
    (r"\$\s?\d", "currency amount"),
]

# --------------------------------------------------------------------------------------
# Tier 1: identifiers the shared naming appendix already gives every arm. Allowed in the
# result-contract materials; banned in the language reference.
# --------------------------------------------------------------------------------------
REGISTERED_IDENTIFIER_BANLIST: list[tuple[str, str]] = [
    (r"(?i)\b(?:approved?|reviews?|reject(?:ed|ion)?)\b", "determination id"),
    (r"enhanced-review", "determination id"),
    (r"(?i)\bunresolved\b", "unresolved kind"),
    (r"missing-required-evidence|no-match|exception-escalation", "ground token"),
    (r"(?i)\bunknown\b", "ground token"),
    (r"(?i)\bescalat", "ground token"),
    (r"(?i)\b(?:disposition|reasons)\b", "contract field name"),
]

# --------------------------------------------------------------------------------------
# Sufficiency table: construct id -> (anchor required in the excerpt, detector, always?)
# Detectors run against the reference module with comment lines stripped, so that prose in
# the reference's comments can never stand in for real usage.
# --------------------------------------------------------------------------------------
Detector = object


def _re(pattern: str):
    rx = re.compile(pattern, re.MULTILINE)
    return lambda src: rx.search(src) is not None


def _function_else_ladder(src: str) -> bool:
    """True if some function definition is followed by an `else` rung."""
    head = re.compile(r"^[a-z_][\w]*\([^)]*\)\s*:=")
    lines = [ln for ln in src.splitlines() if ln.strip()]
    for i, line in enumerate(lines):
        if not head.match(line):
            continue
        for later in lines[i + 1:]:
            stripped = later.lstrip()
            if stripped.startswith("else ") or stripped.startswith("} else"):
                return True
            if re.match(r"^[a-z_][\w]*", later) and (":=" in later or " if " in later):
                break
    return False


CONSTRUCTS: list[tuple[str, str, object, bool]] = [
    # (construct id, anchor, detector, always-required)
    ("package-declaration", "package-declaration", _re(r"^package\s+[a-z]"), True),
    ("import-statement", "import-statement", _re(r"^import\s+"), True),
    ("comments", "comments", None, True),  # detector added below (needs raw source)
    ("scalar-values", "scalar-values", _re(r"\bnull\b"), True),
    ("composite-object", "composite-object", _re(r':=\s*\{\s*"'), True),
    ("composite-array", "composite-array", _re(r":=\s*\["), True),
    ("composite-set", "composite-set", _re(r"\{\w+\s*\|"), True),
    ("assignment-local", "assignment-local", _re(r"^\s+[a-z_]\w*\s*:="), True),
    ("comparison-operators", "comparison-operators", _re(r"(==|!=|<=|>=|<|>)"), True),
    (
        "complete-rule-no-body",
        "complete-rule-no-body",
        _re(r"^[a-z_]\w*\s*:=(?!.*\bif\b).*$"),
        True,
    ),
    ("complete-rule-if-body", "complete-rule-if-body", _re(r"^[a-z_]\w*\s*:=.*\bif\b\s*\{"), True),
    ("if-keyword", "if-keyword", _re(r"\bif\b\s*\{"), True),
    ("default-rule", "default-rule", _re(r"^default\s+\w+\s*:="), True),
    ("else-rule-ladder", "else-rule-ladder", _re(r"^\s*(?:\}\s*)?else\s*:=.*\bif\b"), True),
    (
        "else-without-body",
        "else-without-body",
        _re(r"^\s*(?:\}\s*)?else\s*:=(?!.*\bif\b).*$"),
        True,
    ),
    ("function-definition", "function-definition", _re(r"^[a-z_]\w*\([^)]*\)\s*:="), True),
    ("function-else-ladder", "function-else-ladder", _function_else_ladder, True),
    ("set-comprehension", "set-comprehension", _re(r"\{\s*\w+\s*\|"), True),
    ("some-in", "some-in", _re(r"\bsome\s+\w+\s+in\b"), True),
    ("membership-in", "membership-in", _re(r"(?<!some )\b\w+\s+in\s+\w"), True),
    ("object-get", "object-get", _re(r"\bobject\.get\s*\("), True),
    ("count", "count", _re(r"\bcount\s*\("), True),
    ("undefined-and-default", "undefined-and-default", None, True),
    ("evaluation-order", "evaluation-order", None, True),
]


def strip_comments(src: str) -> str:
    out = []
    for line in src.splitlines():
        if line.lstrip().startswith("#"):
            continue
        out.append(re.sub(r"\s#.*$", "", line))
    return "\n".join(out)


def rego_blocks(markdown: str) -> list[str]:
    return re.findall(r"^```rego\n(.*?)^```", markdown, re.DOTALL | re.MULTILINE)


def section(text: str, name: str) -> str:
    begin, end = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
    if begin not in text or end not in text:
        raise AssertionError(f"missing region {name}")
    return text.split(begin, 1)[1].split(end, 1)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opa", help="path to the pinned opa binary; also parse examples")
    args = parser.parse_args(argv)

    failures: list[str] = []
    notes: list[str] = []

    raw_reference = REFERENCE.read_text(encoding="utf-8")
    reference = strip_comments(raw_reference)
    excerpt = EXCERPT.read_text(encoding="utf-8")

    # ---- 1. sufficiency ---------------------------------------------------------------
    used, unused = [], []
    for cid, anchor, detector, always in CONSTRUCTS:
        if cid == "comments":
            is_used = any(ln.lstrip().startswith("#") for ln in raw_reference.splitlines())
        elif detector is None:
            is_used = False
        else:
            is_used = detector(reference)
        (used if is_used else unused).append(cid)
        if not (is_used or always):
            continue
        if f"<!-- construct: {anchor} -->" not in excerpt:
            why = "used by the reference" if is_used else "required by the derivation rule"
            failures.append(f"[sufficiency] construct {cid!r} ({why}) has no anchor in {EXCERPT.name}")
    notes.append(f"constructs detected in the reference: {len(used)}/{len(CONSTRUCTS)}")
    notes.append("documented but not used by the reference: " + (", ".join(unused) or "none"))

    # ---- 2. prohibition ---------------------------------------------------------------
    def scan(path: Path, banlist, label: str) -> None:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, kind in banlist:
                m = re.search(pattern, line)
                if m:
                    failures.append(
                        f"[{label}] {path.name}:{lineno} contains {kind} {m.group(0)!r}"
                    )

    for path in ALL_MATERIALS:
        scan(path, POLICY_CONTENT_BANLIST, "policy-content")
    scan(EXCERPT, REGISTERED_IDENTIFIER_BANLIST, "language-only")

    # ---- 3. derivation and fairness integrity -----------------------------------------
    sys.path.insert(0, str(HERE))
    import deformalize  # noqa: E402  (local module, imported after path setup)

    rendered = deformalize.render(deformalize.extract_schema(CONVENTION.read_text("utf-8")))
    if rendered != CONTRACT.read_text(encoding="utf-8"):
        failures.append(f"[derivation] {CONTRACT.name} is not the current output of deformalize.py")

    b, c = SUFFIX_B.read_text(encoding="utf-8"), SUFFIX_C.read_text(encoding="utf-8")
    try:
        for region in ("SHARED:1", "SHARED:2"):
            if section(b, region) != section(c, region):
                failures.append(f"[fairness] suffix region {region} differs between arms B and C")
        if section(b, "EMBED").strip("\n") != CONTRACT.read_text("utf-8").strip("\n"):
            failures.append("[fairness] suffix-b.md does not embed contract-b.md verbatim")
        if section(c, "EMBED").strip("\n") != CONVENTION.read_text("utf-8").strip("\n"):
            failures.append("[fairness] suffix-c.md does not embed convention-c.md verbatim")
    except AssertionError as exc:
        failures.append(f"[fairness] {exc}")

    for name, text in (("suffix-b.md", b), ("suffix-c.md", c)):
        for marker in ("POLICY:", "TESTS:"):
            if marker not in text:
                failures.append(f"[format] {name} never states the {marker!r} marker")

    # ---- optional: parse every example --------------------------------------------------
    if args.opa:
        blocks = rego_blocks(excerpt)
        notes.append(f"rego example blocks in the excerpt: {len(blocks)}")
        with tempfile.TemporaryDirectory() as tmp:
            for i, block in enumerate(blocks):
                src = block if block.lstrip().startswith("package ") else f"package example\n\n{block}"
                path = Path(tmp) / f"block_{i}.rego"
                path.write_text(src, encoding="utf-8")
                proc = subprocess.run(
                    [args.opa, "check", str(path)], capture_output=True, text=True
                )
                if proc.returncode != 0:
                    failures.append(
                        f"[examples] block {i} does not compile: {proc.stderr.strip().splitlines()[:2]}"
                    )

    for note in notes:
        print(f"note: {note}")
    if failures:
        print(f"\nFAIL ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nPASS: sufficiency, policy-content prohibition, and derivation integrity all hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
