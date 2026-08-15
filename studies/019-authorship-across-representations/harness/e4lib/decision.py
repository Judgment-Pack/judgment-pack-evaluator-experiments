"""Section 5's ordered decision rule, as an ordered exhaustive table.

ASSEMBLED FROM the program shape Studies 015-018 carry (`decide()` in
`studies/018-transition-rules/harness/score.py`, lines 599-620), generalised
from that line's if-ladder to a TABLE for one reason: Study 018's round-8
finding 1 was a decision rule whose code and whose registration disagreed about
which cells adjudicate, and the ladder gave nothing to enumerate. Here the rule
is data — one named constant per registered row, in registered order — and
`tests/test_score.py` drives a synthetic outcome through EVERY row and asserts
that the row it lands on is the row the registration names.

PREREGISTRATION.md section 5, verbatim:

    Ordered, exhaustive decision rule (first matching row; last row always
    matches):
    1. Any pin/schema/manifest failure, or apparatus failure making the batch
       non-terminal -> R1 inconclusive - pipeline-invalid.
    2. Any control-gate failure (reference-vs-gold imperfect at attempt time;
       capabilities canary passes; golden-context gate; per-arm timeout rate >
       cap; E1 floor breached) -> R1 inconclusive - control gate failed.
    3. A-C interval excludes zero -> R1 decided, direction as observed; then A-B
       likewise.
    4. Otherwise -> INDETERMINATE; no claim in any direction is licensed.

Three properties this module is built to make checkable rather than believed:

* **Exhaustive.** `ROW_INDETERMINATE`'s predicate is the constant true, and
  `decide()` asserts that the last row matched when no earlier one did. A rule
  that can fall off the end is a rule with an unregistered outcome.
* **Ordered, and the order is the registration's.** `ROWS` is the tuple; a row
  moved is a diff in one place. Row 2 is above row 3 because a control-gate
  failure "adjudicates R1 in neither direction" — reading the contrast first
  and then discarding it is not the same rule, because it publishes a direction
  the registration says is not licensed.
* **Fixed-sequence gatekeeping, inside row 3.** A-C is tested first and A-B is
  tested only if A-C decided; section 5 controls FWER at alpha that way and
  registers no further adjustment. `decide()` therefore returns the A-B result
  only when A-C decided, and says so in the record rather than leaving a reader
  to notice an absent member.

INDETERMINATE licenses nothing — not equivalence, not either direction's
negation (section 1's R1, section 5's last row, and section 9). The verdict
strings below are the only ones this study publishes, so an outcome cannot be
described in prose the registration does not carry.
"""
from __future__ import annotations

import collections

# The two contrasts, in the registered order they are tested in.
CONTRAST_PRIMARY = "A-C"
CONTRAST_SECONDARY = "A-B"
CONTRAST_ORDER = (CONTRAST_PRIMARY, CONTRAST_SECONDARY)

# The registered control gates (section 5 row 2, section 6). Named here so the
# scorer cannot invent a gate and so an absent gate is a missing key rather than
# a silently-passing one.
CONTROL_GATES = (
    "references-reproduce-gold",
    "capabilities-canary-refused",
    "golden-context",
    "timeout-rate-within-cap",
    "e1-floor",
)

Row = collections.namedtuple("Row", "name verdict registered predicate")


def _pipeline_invalid(outcome):
    """Row 1. Any pin, schema or manifest failure, or an apparatus failure that
    makes the batch non-terminal."""
    return sorted(outcome.get("pipelineProblems") or [])


def _control_gate(outcome):
    """Row 2. Any registered control gate not held.

    An ABSENT gate fails: section 6 puts the gates "above every substantive
    row", and a gate the scorer did not evaluate is not a gate that held.
    Study 012's round 9 found all 150 calls reachable with the isolation assent
    still null — an unevaluated control reads as satisfied unless something
    makes absence a failure."""
    gates = outcome.get("controlGates") or {}
    failed = []
    for name in CONTROL_GATES:
        state = gates.get(name)
        if state is None:
            failed.append("%s (not evaluated)" % name)
        elif not state.get("held"):
            failed.append(name)
    return failed


def _primary_decided(outcome):
    """Row 3. The A-C interval excludes zero."""
    contrast = (outcome.get("contrasts") or {}).get(CONTRAST_PRIMARY)
    if contrast is None:
        return []
    return [CONTRAST_PRIMARY] if contrast.get("excludesZero") else []


def _always(outcome):
    """Row 4. The last row always matches — that is what makes the table
    exhaustive, and `decide()` asserts it."""
    return ["indeterminate"]


ROW_PIPELINE_INVALID = Row(
    name="pipeline-invalid",
    verdict="R1 inconclusive - pipeline-invalid",
    registered="Any pin/schema/manifest failure, or apparatus failure making "
               "the batch non-terminal",
    predicate=_pipeline_invalid)

ROW_CONTROL_GATE = Row(
    name="control-gate-failed",
    verdict="R1 inconclusive - control gate failed",
    registered="Any control-gate failure (reference-vs-gold imperfect at "
               "attempt time; capabilities canary passes; golden-context gate; "
               "per-arm timeout rate > cap; E1 floor breached)",
    predicate=_control_gate)

ROW_PRIMARY_DECIDED = Row(
    name="decided",
    verdict="R1 decided",
    registered="A-C interval excludes zero -> R1 decided, direction as "
               "observed; then A-B likewise",
    predicate=_primary_decided)

ROW_INDETERMINATE = Row(
    name="indeterminate",
    verdict="INDETERMINATE",
    registered="Otherwise -> INDETERMINATE; no claim in any direction is "
               "licensed",
    predicate=_always)

# The table. Order IS the rule.
ROWS = (ROW_PIPELINE_INVALID, ROW_CONTROL_GATE, ROW_PRIMARY_DECIDED,
        ROW_INDETERMINATE)


class DecisionError(Exception):
    """A refusal about the decision rule itself."""


def direction(contrast: dict) -> str:
    """The direction of a decided contrast, spelled in arms rather than in the
    contrast machinery's left/right.

    Section 1: "Direction is reported as observed; the design-phase pilot
    pointed B/C above A, and this registration deliberately does not presuppose
    it." So the direction is read off the counts and never assumed."""
    if not contrast.get("excludesZero"):
        return "none - INDETERMINATE"
    left, right = contrast["arms"]
    return "%s above %s" % ((left, right) if contrast["left"] > contrast["right"]
                            else (right, left))


def decide(outcome: dict) -> dict:
    """Walk the table in registered order and return the first matching row.

    `outcome` carries `pipelineProblems`, `controlGates` and `contrasts`; every
    member is optional and an absent one is treated as the state that FAILS,
    never as the state that passes."""
    for row in ROWS:
        causes = row.predicate(outcome)
        if not causes:
            continue
        record = {
            "row": row.name,
            "rowIndex": ROWS.index(row) + 1,
            "verdict": row.verdict,
            "registeredText": row.registered,
            "causes": causes,
        }
        if row is ROW_PRIMARY_DECIDED:
            contrasts = outcome.get("contrasts") or {}
            primary = contrasts[CONTRAST_PRIMARY]
            record["verdict"] = "R1 decided - %s" % direction(primary)
            record["primary"] = {CONTRAST_PRIMARY: direction(primary)}
            # Fixed-sequence gatekeeping: A-B is tested SECOND and only because
            # A-C decided. Reported with that condition attached, so no reader
            # can lift the secondary contrast out of the sequence that controls
            # its error rate.
            secondary = contrasts.get(CONTRAST_SECONDARY)
            record["secondary"] = {
                "contrast": CONTRAST_SECONDARY,
                "testedBecause": "A-C decided (fixed-sequence gatekeeping; FWER "
                                 "controlled at alpha, no further adjustment)",
                "result": None if secondary is None else direction(secondary),
            }
        return record
    raise DecisionError(
        "DECISION-NOT-EXHAUSTIVE no row of section 5's ordered rule matched; the "
        "last row is registered to always match and this table's last row is %r"
        % ROW_INDETERMINATE.name)
