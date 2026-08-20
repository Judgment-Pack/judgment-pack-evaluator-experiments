"""The registered marker rule — extraction, and nothing else.

ASSEMBLED FROM the design prototype `design/pilot/pilot_run.py`
(sha256 `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295`),
lines 81-86 (`ARM_MARKERS`) and 181-216 (`extract_block()`), carried with their
arithmetic unchanged. `harness/PORTS.md` carries the two-sided row.

The rule, from PREREGISTRATION.md section 3: "Artifact extraction is the
registered marker rule (`PACK:`/`MATRIX:` for A, `POLICY:`/`TESTS:` for B/C;
fenced block immediately following; last occurrence governs)." Three properties
of that sentence are load-bearing and are asserted by `tests/test_score.py`:

* **last occurrence governs** — an author that emits a draft and then a final
  block is scored on the final one, and a scorer that took the first would
  score a draft;
* **immediately following, modulo blank lines** — prose between the marker and
  the fence means the marker does not govern that fence, and the search
  continues to an earlier marker;
* **the info string is the expected language or empty** — a ```python block
  under `POLICY:` is not a Rego policy, and admitting it would file a language
  error as a policy defect.

Authoring is single-shot with no repair (section 3), so this module never
rewrites, trims or re-fences anything. It returns the block or the reason there
is none, and the reason is the section 1a code `no-marker-block`.
"""
from __future__ import annotations

import re

# arm -> (scored marker, scored language, secondary marker, secondary language).
# The SCORED artifact is the policy artifact (E1's subject); the SECONDARY is the
# authored test suite (E4's subject). Both are extracted by the same rule, and
# arm A's pair is named by the JPS spec's own vocabulary while B/C's is named by
# OPA's — the asymmetry is in the representations, not in the rule.
ARM_MARKERS = {
    "A": ("PACK", "json", "MATRIX", "json"),
    "B": ("POLICY", "rego", "TESTS", "rego"),
    "C": ("POLICY", "rego", "TESTS", "rego"),
}

# The one code this module can produce. It is section 1a's, spelled as section
# 1a spells it — `batch.CODE_PARTITION` is the authority and
# `tests/test_score.py` diffs this against it.
NO_MARKER = "no-marker-block"

FENCE_RE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$")


def extract_block(text: str, marker: str, lang: str) -> tuple:
    """Return `(block_text, None)` or `(None, NO_MARKER)`.

    The registered rule: the LAST line equal to `<marker>:` that is followed,
    after optional blank lines, by a fenced block whose info string is `lang` or
    empty. The block ends at the next closing fence. A marker whose fence never
    closes does not govern — the search falls back to an earlier marker rather
    than inventing a terminator, because an unterminated fence is an artifact
    the author did not finish emitting and repairing it would be repair."""
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines)
              if line.strip() == marker + ":"]
    for index in reversed(starts):
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip() == "":
            cursor += 1
        if cursor >= len(lines):
            continue
        fence = FENCE_RE.match(lines[cursor])
        if not fence:
            continue
        info = fence.group(1).lower()
        if info not in ("", lang):
            continue
        body, cursor, closed = [], cursor + 1, False
        while cursor < len(lines):
            if lines[cursor].strip() == "```":
                closed = True
                break
            body.append(lines[cursor])
            cursor += 1
        if not closed:
            continue
        return "\n".join(body) + "\n", None
    return None, NO_MARKER


def extract_pair(text: str, arm: str) -> dict:
    """Both of an arm's artifacts under one call, so a caller cannot extract the
    policy under one rule and the suite under another.

    New here, not in the prototype: the prototype extracted the secondary block
    inline inside its scoring loop, which is why its `secondaryArtifact` record
    said `present` while the file on disk was absent (`e4_score.py`'s
    `missingSuites` exists to catch exactly that). Returning both from one
    function makes the pair the unit and the record a description of what this
    function returned."""
    if arm not in ARM_MARKERS:
        raise KeyError("arm %r is not one of %s"
                       % (arm, ", ".join(sorted(ARM_MARKERS))))
    marker, lang, secondary_marker, secondary_lang = ARM_MARKERS[arm]
    policy, policy_why = extract_block(text, marker, lang)
    suite, suite_why = extract_block(text, secondary_marker, secondary_lang)
    return {
        "arm": arm,
        "policyMarker": marker,
        "policyLanguage": lang,
        "policy": policy,
        "policyCode": policy_why,
        "suiteMarker": secondary_marker,
        "suiteLanguage": secondary_lang,
        "suite": suite,
        "suiteCode": suite_why,
        "suiteBytes": 0 if suite is None else len(suite.encode("utf-8")),
        "policyBytes": 0 if policy is None else len(policy.encode("utf-8")),
    }
