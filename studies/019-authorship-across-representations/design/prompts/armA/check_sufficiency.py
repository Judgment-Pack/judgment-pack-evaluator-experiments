#!/usr/bin/env python3
"""Freeze test for the arm A prompt materials.

Two independent assertions, both mechanical:

  (1) SUFFICIENCY (excerpt parity, BRIEF.md section 3): every language construct the frozen
      arm A reference pack uses must appear in the arm A excerpt. The pack JSON is walked;
      object member names are collected as constructs, and the values of the enumerated
      keyword positions (op, operator, effect, onUnknown, evidenceRequirements[].kind,
      escalation.triggers[], escalation.target.kind) are collected as keywords. Free-text
      values -- ids, descriptions, pointer paths, outcome ids, fact-condition operands -- are
      deliberately NOT collected: they are policy content, and requiring them in the excerpt
      is what this file's second half forbids. A fixed list of additional constructs the
      registered derivation rule names (required true/false, fallbackOutcome's neutral
      documentation, the disposition shape, the matrixVersion-2 matrix shape, the reason
      vocabulary) is checked alongside them.

  (2) LANGUAGE-ONLY: the excerpt must name no policy content. The stimulus is the policy
      prose; an excerpt that leaks the policy's own vocabulary, thresholds, or solution
      structure would make arm A's prompt a different task from arms B and C.

Exit status 0 when both hold, 1 otherwise. Run with no arguments.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE.parent.parent  # .../design
EXCERPT = HERE / "jps-excerpt.md"
REFERENCE_PACK = DESIGN / "reference" / "refA" / "pack.json"

# --- (1) constructs collected from the reference pack ------------------------------------

# Value positions whose contents are language keywords rather than policy content.
KEYWORD_MEMBERS = {"op", "operator", "effect", "onUnknown"}


def collect(node, path, members: set[str], keywords: set[str]) -> None:
    """Walk the pack, collecting member names and enumerated keyword values."""
    if isinstance(node, dict):
        for key, val in node.items():
            members.add(key)
            if key in KEYWORD_MEMBERS and isinstance(val, str):
                keywords.add(val)
            # evidenceRequirements[].kind and escalation.target.kind are both enumerated.
            if key == "kind" and isinstance(val, str):
                keywords.add(val)
            if key == "triggers" and isinstance(val, list):
                keywords.update(t for t in val if isinstance(t, str))
            if key == "required" and isinstance(val, bool):
                keywords.add(f'"required": {json.dumps(val)}')
            collect(val, path + [key], members, keywords)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            collect(item, path + [str(i)], members, keywords)


# Constructs the registered derivation rule names in addition to whatever the pack happens to
# use: members that must be documented precisely because the reference does NOT use them, plus
# the evaluation vocabulary and the matrix shape the arm's second artifact needs.
EXTRA_REQUIRED = [
    # available-but-optional root members, documented neutrally
    "fallbackOutcome",
    "applicability",
    "sources",
    "literal",
    "not-equals",
    "in",
    # evidence-availability tri-state (§8.2)
    "present",
    "absent",
    # reason vocabulary (§8)
    "missing-required-evidence",
    "unknown",
    "no-match",
    "conflict",
    "not-applicable",
    "exception-escalation",
    # disposition shape (§8.3)
    "kind",
    "outcomeId",
    "reasons",
    "handoff",
    "state",
    "requested",
    "triggeredBy",
    # error classes (§8.4)
    "pack-not-conformant",
    "malformed-input",
    "unsupported-required-extension",
    "resource-exhaustion",
    # matrix shape (matrixVersion 2)
    "matrixVersion",
    "cases",
    "facts",
    "evidenceAvailability",
    "expectedDisposition",
    "expectedErrorClass",
    "expectedErrorPhase",
    "expectedHandoffTarget",
    # decimal-string semantics and pointer resolution
    "decimal",
    "JSON Pointer",
    "RFC 6901",
]

# --- (2) policy content the excerpt must not name -----------------------------------------

FORBIDDEN_CASE_INSENSITIVE = [
    "vendor",
    "sanction",
    "country",
    "insurance",
    "enforcement",
    "compliance",
    "riskScore",
    "requestedSpend",
    "criticalSupplier",
    "newVendor",
    "priorEnforcement",
    "countryRisk",
    "sanctionsStatus",
    "critical supplier",
    "risk score",
    "enhanced review",
    "screening",
    "spend",
    "onboarding",
]

# Policy literals. Words are matched case-sensitively so that ordinary English ("no-match",
# "a low value") cannot trip the check while the policy's own tokens do.
FORBIDDEN_CASE_SENSITIVE = [
    "CLEAR",
    "MATCH",
    "LOW",
    "MEDIUM",
    "HIGH",
    "enhanced-review",
]

# Numeric literals of the policy: the three risk thresholds and the three spend thresholds,
# in every spelling the policy or a pack could use.
FORBIDDEN_PATTERNS = [
    r"\b40\b",
    r"\b70\b",
    r"\b90\b",
    r"\b40\.00\b",
    r"\b70\.00\b",
    r"\b90\.00\b",
    r"100000",
    r"500000",
    r"2000000",
    r"10000000",
    r"100,000",
    r"500,000",
    r"2,000,000",
    r"10,000,000",
]


def main() -> int:
    if not EXCERPT.is_file():
        print(f"FAIL: excerpt not found: {EXCERPT}")
        return 1
    if not REFERENCE_PACK.is_file():
        print(f"FAIL: reference pack not found: {REFERENCE_PACK}")
        return 1

    excerpt = EXCERPT.read_text(encoding="utf-8")
    pack = json.loads(REFERENCE_PACK.read_text(encoding="utf-8"))

    members: set[str] = set()
    keywords: set[str] = set()
    collect(pack, [], members, keywords)

    required = sorted(members | keywords) + EXTRA_REQUIRED
    missing = [tok for tok in required if tok not in excerpt]

    leaks: list[str] = []
    lowered = excerpt.lower()
    for tok in FORBIDDEN_CASE_INSENSITIVE:
        if tok.lower() in lowered:
            leaks.append(f"{tok!r} (case-insensitive)")
    for tok in FORBIDDEN_CASE_SENSITIVE:
        if tok in excerpt:
            leaks.append(f"{tok!r} (case-sensitive)")
    for pat in FORBIDDEN_PATTERNS:
        m = re.search(pat, excerpt)
        if m:
            leaks.append(f"{m.group(0)!r} (matched /{pat}/)")

    print(f"excerpt:        {EXCERPT}")
    print(f"reference pack: {REFERENCE_PACK}")
    print(
        f"constructs required: {len(required)} "
        f"({len(members)} member names + {len(keywords)} enumerated keywords "
        f"+ {len(EXTRA_REQUIRED)} registered extras)"
    )
    print("member names collected:  " + ", ".join(sorted(members)))
    print("enumerated keywords:     " + ", ".join(sorted(keywords)))

    ok = True
    if missing:
        ok = False
        print(f"\nFAIL (sufficiency): {len(missing)} construct(s) absent from the excerpt:")
        for tok in missing:
            print(f"  - {tok}")
    else:
        print("\nPASS (sufficiency): every construct the reference pack uses appears in the excerpt.")

    if leaks:
        ok = False
        print(f"\nFAIL (language-only): {len(leaks)} policy token(s) present in the excerpt:")
        for tok in leaks:
            print(f"  - {tok}")
    else:
        print("PASS (language-only): the excerpt names no policy content.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
