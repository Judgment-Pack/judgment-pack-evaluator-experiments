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

TWO ROWS ARE AHEAD OF THAT TEXT, and the prose lane owes them (round 1). The
table below carries FIVE rows: a declared short batch is `UNRESOLVED-BY-DESIGN`
above every substantive row (R1-7 — the driver and the scaffold already register
that price, and the scorer was scoring the prefix anyway), and
`engine-execution-clean` joins the control gates (R1-8 — a pinned engine that
refused on a frozen artifact adjudicates R1 in no direction). Until §5's own
bytes carry both, `tests/test_score_decision.py` reads the four rows the
registration does name and asserts the two new ones by their own registrations
(`harness/batch.py`'s `declare_shortfall()` and `harness/SCAFFOLD.md`).

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
    # `e1-floor` IS GONE, and its absence is the registered change rather than
    # an omission. Ruling M-23 (§5.7) is option (a) — no author-side control
    # gate — and §5.9 says it in terms: "There is no `e1-floor` row". The gate
    # was a MAX statistic whose stringency ran the wrong way in n, it spuriously
    # refused arm A with probability 1.3–6.1 % at 019-scale N even with a
    # perfect stimulus, and certifying P(fire) ≥ 0.95 would have needed ~2,926
    # degraded runs. An uncertified gate is not registered as if certified, so
    # E1 is fully descriptive here and the derived threshold survives only as
    # §2a.4's pre-freeze go/no-go.
    #
    # NEW IN 020, and it takes the vacated seat: C4's transfer gate (§2a.5),
    # which is TWO-SIDED. `calibration-invalid` reaches THIS row — the pilot is
    # suspect and a re-pilot is required under C5 — while C4's other outcome,
    # `pipeline-invalid`, reaches row 1 through `pipelineProblems`, because a
    # batch that is suspect is not a control that merely failed.
    "c4-transfer-gate",
    # ROUND-1 R1-8. A pinned engine that refused on a FROZEN study artifact —
    # a reference during the identity control, a manifest mutant during
    # mutation execution — is an apparatus failure, and the old code counted it
    # as a kill in one direction and as an identity failure in the other. It is
    # neither, so it adjudicates R1 in no direction: the gate holds only when
    # every scored invocation of this attempt returned an answer. OWED TO THE
    # PROSE LANE: §5 row 2's parenthetical and §6's gate list must name it.
    "engine-execution-clean",
)

# §1.3's CLOSED verdict vocabulary, registered here as data and NOT YET
# IMPLEMENTED by the table below — which is stated rather than glossed.
#
# 020 registers exactly two substantive verdicts, CLAIM and
# INDETERMINATE-BY-DISAGREEMENT, and registers that "the word UNSUPPORTED is not
# used anywhere in 020 for this rule; it reads as evidence of no effect, which
# INDETERMINATE explicitly is not". Both are verdicts of the EIGHTEEN-MEMBER
# intersection–union family (§5.2, §5.4): a CLAIM requires every member to agree
# in the sign of the A−C difference AND every member's own test to reject.
#
# The family scorer is §7's delta 5 and `harness/SCAFFOLD.md` item S4. It has
# not landed, so rows 4 and 5 below are still Study 019's single-contrast rows
# and still carry 019's verdict strings. That is a KNOWN GAP with the freeze
# gated on it, not a reading of §1.3, and
# `harness/tests/test_score_decision.py` asserts the gap in both directions so
# that closing it fails a test rather than passing silently.
REGISTERED_VERDICT_VOCABULARY = ("CLAIM", "INDETERMINATE-BY-DISAGREEMENT")
FAMILY_MEMBERS_REGISTERED = 18

# The E4 denominators §5's contrast is computed over must be POSITIVE for the
# contrast to be a statement about anything (round-1 R1-14: an arm with zero
# admitted runs passes E1's floor by definition, and the substantive row then
# reported INDETERMINATE with no interval in existence).
REGISTERED_MINIMUM_DENOMINATOR = 1

Row = collections.namedtuple("Row", "name verdict registered predicate")


def _pipeline_invalid(outcome):
    """Row 1. Any pin, schema or manifest failure, or an apparatus failure that
    makes the batch non-terminal."""
    return sorted(outcome.get("pipelineProblems") or [])


def _shortfall_declared(outcome):
    """Row 2. The batch was DECLARED short.

    `harness/batch.py`'s `declare_shortfall()` registers the price in advance —
    "under the stopping rule an incomplete batch, at any round and for any
    reason, yields `UNRESOLVED-BY-DESIGN` on every level verdict and no contrast
    at all" — and `harness/SCAFFOLD.md` says a shortfall declares rather than
    scores. Round-1 R1-7 found the scorer computing ordinary endpoints and
    contrasts over an arbitrary incomplete prefix on the strength of any JSON
    object at all, `{}` included, which is outcome-selective deletion with a
    declaration file as its only cost. The branch is a ROW now, above every
    substantive one and above the gates, because a prefix is not the registered
    population and no gate over it means anything.

    OWED TO THE PROSE LANE: §5's ordered rule must carry this row, in this
    position, with this verdict."""
    return list(outcome.get("shortfallDeclared") or [])


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
    """Row 4. The A-C interval excludes zero.

    A MISSING primary contrast decides nothing (round-1 R1-14). It used to fall
    through to the last row, which publishes a substantive `INDETERMINATE` —
    "the interval straddles zero" — over an attempt in which no interval was ever
    computed. An absent contrast is not a straddling one; the scorer is required
    to have refused above this row, and `decide()` asserts it."""
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

ROW_SHORTFALL_DECLARED = Row(
    name="shortfall-declared",
    verdict="UNRESOLVED-BY-DESIGN - the batch was declared short",
    registered="A declared short batch: every level verdict is "
               "UNRESOLVED-BY-DESIGN and no contrast is computed",
    predicate=_shortfall_declared)

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
ROWS = (ROW_PIPELINE_INVALID, ROW_SHORTFALL_DECLARED, ROW_CONTROL_GATE,
        ROW_PRIMARY_DECIDED, ROW_INDETERMINATE)

# The rows at or above which NO inferential quantity may be computed, let alone
# published (round-1 R1-14). `harness/score.py` evaluates the gate rows FIRST,
# and computes a contrast only when the outcome would reach `ROW_PRIMARY_DECIDED`
# — because "adjudicates R1 in neither direction" is not satisfied by computing a
# direction and then declining to act on it.
GATING_ROWS = (ROW_PIPELINE_INVALID, ROW_SHORTFALL_DECLARED, ROW_CONTROL_GATE)


class DecisionError(Exception):
    """A refusal about the decision rule itself."""


def gate_causes(outcome: dict) -> list:
    """Every cause on a gating row, in registered row order — empty exactly when
    the outcome is allowed to have a contrast computed for it at all.

    This is the ONE predicate `harness/score.py` asks before it computes
    anything inferential. It is derived from `GATING_ROWS` rather than written
    out, so a row added to the table above cannot be a row the scorer forgets to
    gate on."""
    causes = []
    for row in GATING_ROWS:
        causes.extend("%s: %s" % (row.name, cause)
                      for cause in row.predicate(outcome))
    return causes


def direction(contrast: dict) -> str:
    """The direction of a decided contrast, spelled in arms rather than in the
    contrast machinery's left/right.

    Section 1: "Direction is reported as observed; the design-phase pilot
    pointed B/C above A, and this registration deliberately does not presuppose
    it." So the direction is read off the observation and never assumed.

    IT IS READ OFF THE RATES, THROUGH THE STATISTICAL FUNCTION'S OWN `decision`
    FIELD (round-1 R1-13). It used to compare the raw COUNTS, which is the same
    thing only at equal denominators — and §1a makes unequal denominators the
    expected case, because apparatus exclusions leave them. The reviewer's
    permitted contrast is the whole of the argument: at 6/50 versus 5/6,
    `excludes_zero()` reports a difference of -0.7133 with the right arm far
    above the left, and comparing 6 > 5 reported "A above C" — the study's
    conclusion, reversed, on the registered decision's own numbers.
    `stats.excludes_zero()` already computes the comparison in exact
    `Fraction`s; this reads that answer instead of recomputing a worse one."""
    if not contrast.get("excludesZero"):
        return "none - INDETERMINATE"
    left, right = contrast["arms"]
    verdict = contrast.get("decision")
    if verdict == "left-above-right":
        return "%s above %s" % (left, right)
    if verdict == "right-above-left":
        return "%s above %s" % (right, left)
    raise DecisionError(
        "DECISION-DIRECTION-UNREADABLE a contrast that excludes zero carries "
        "the decision field %r, and the direction of a decided contrast is that "
        "field and nothing else" % (verdict,))


def decide(outcome: dict) -> dict:
    """Walk the table in registered order and return the first matching row.

    `outcome` carries `pipelineProblems`, `controlGates`, `contrasts` and —
    round-3 R3-8 — `secondaryRefusal`, the cause of an absent A-B once A-C has
    decided; every member is optional and an absent one is treated as the state
    that FAILS, never as the state that passes."""
    for row in ROWS:
        causes = row.predicate(outcome)
        if not causes:
            continue
        if row is ROW_INDETERMINATE \
                and (outcome.get("contrasts") or {}).get(CONTRAST_PRIMARY) is None:
            # Round-1 R1-14, the second scenario. The last row's verdict is a
            # SUBSTANTIVE one — the interval straddles zero — and reaching it
            # with no interval in existence publishes a measured null that
            # nothing measured. The scorer is required to have filed the
            # missing contrast as a pipeline problem above; if it did not, this
            # refuses rather than substituting the substantive row.
            raise DecisionError(
                "DECISION-NO-PRIMARY-CONTRAST no gating row matched and the "
                "registered primary contrast %s was never computed: the last "
                "row's INDETERMINATE is the statement that an interval straddles "
                "zero, and there is no interval" % CONTRAST_PRIMARY)
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
            refusal = outcome.get("secondaryRefusal")
            if secondary is None and not refusal:
                # ROUND-3 FINDING R3-8. An absent secondary used to be published
                # as a bare `result: null`, which reads as "not decided" and is
                # indistinguishable from "never computed". The registered
                # sequence is "A-C decided, THEN A-B likewise", so once the
                # primary has decided the secondary was REACHED: it either has a
                # result or has a stated cause. Refusing here is what stops a
                # scorer that dropped it silently — the round-3 scenario, in
                # which a secondary raising `FM-EMPTY-ARM` deleted the whole
                # contrast set — from publishing a decided row with a null
                # beside it and no reader able to tell which happened.
                raise DecisionError(
                    "DECISION-SECONDARY-UNEXPLAINED the primary contrast %s "
                    "decided, so the registered sequence reached %s, and it is "
                    "neither computed nor refused: an absent secondary must "
                    "carry its cause in `secondaryRefusal`"
                    % (CONTRAST_PRIMARY, CONTRAST_SECONDARY))
            record["secondary"] = {
                "contrast": CONTRAST_SECONDARY,
                "testedBecause": "A-C decided (fixed-sequence gatekeeping; FWER "
                                 "controlled at alpha, no further adjustment)",
                "result": None if secondary is None else direction(secondary),
                "refusal": refusal if secondary is None else None,
            }
        return record
    raise DecisionError(
        "DECISION-NOT-EXHAUSTIVE no row of section 5's ordered rule matched; the "
        "last row is registered to always match and this table's last row is %r"
        % ROW_INDETERMINATE.name)
