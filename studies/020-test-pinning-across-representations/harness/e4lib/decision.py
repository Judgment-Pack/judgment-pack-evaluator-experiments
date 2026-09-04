"""§5.9's ordered exhaustive decision rule, as an ordered exhaustive table.

WHAT THIS FILE DOES
-------------------
Holds PREREGISTRATION.md §5.9's five rows as DATA, in registered order, and
walks them first-match-wins. Each row is a named constant with the
registration's own text beside it, so a row moved or a verdict reworded is a
diff in one place, and `harness/tests/test_score_decision.py` drives a synthetic
outcome through EVERY row and asserts the row it lands on is the row the
registration names.

DELIBERATELY DOES NOT DO
------------------------
* **Reads no cut, no threshold and no interval** (§7 delta 2, §5.1's "No cut,
  no τ, no dichotomy"). 019's substantive row read one binomial contrast's
  zero-exclusion over a high-kill run count derived from tau = 0.95. 020's
  substantive row reads the eighteen-member family's two unanimities and
  nothing else. `tests/test_score_decision.py` asserts that no registered
  decision path here reads a cut, by name.
* **Computes nothing.** The family's members, offsets, permutation p-values and
  BCa intervals are `e4lib/family.py`'s (§7 delta 5); this file reads the
  verdict that module produced and never re-derives one.
* **Carries no `e1-floor` row** (§5.7, M-23 option (a); §5.9 row 3's "There is
  no `e1-floor` row"). The author-side existence gate is not registered, so it
  is not a member of `CONTROL_GATES` and cannot be silently satisfied by an
  absence.

ASSEMBLED FROM the program shape Studies 015-018 carry (`decide()` in
`studies/018-transition-rules/harness/score.py`, lines 599-620), generalised
from that line's if-ladder to a TABLE for one reason: Study 018's round-8
finding 1 was a decision rule whose code and whose registration disagreed about
which cells adjudicate, and the ladder gave nothing to enumerate.

PREREGISTRATION.md §5.9, verbatim:

    Ordered, exhaustive decision rule (first matching row; last row always
    matches)

    1. Any pin/schema/manifest failure, or apparatus failure making the batch
       non-terminal, or C4's `pipeline-invalid` outcome (§2a.5) -> R1
       inconclusive - pipeline-invalid.
    2. A validated shortfall declaration (§1a) -> UNRESOLVED-BY-DESIGN - no
       endpoint, no rate and no contrast is computed.
    3. Any control-gate failure - both references reproduce gold imperfectly at
       attempt time; the capabilities canary passes; golden-context gate;
       `engine-execution-clean`; per-arm timeout rate above cap; C4's
       `calibration-invalid` outcome -> R1 inconclusive - control gate failed.
       There is no `e1-floor` row (§5.7).
    4. All eighteen family members agree in the sign of the A-C difference and
       all eighteen reject at two-sided alpha = 0.05 -> R1 = CLAIM, direction
       the common sign; then A-B under the identical rule.
    5. Otherwise -> INDETERMINATE-BY-DISAGREEMENT. No claim in any direction is
       licensed, and this row triggers nothing.

Three properties this module is built to make checkable rather than believed:

* **Exhaustive.** `ROW_INDETERMINATE`'s predicate is the constant true, and
  `decide()` asserts that the last row matched when no earlier one did. A rule
  that can fall off the end is a rule with an unregistered outcome.
* **Ordered, and the order is the registration's.** `ROWS` is the tuple; a row
  moved is a diff in one place. The gate rows are above the substantive one
  because a control-gate failure "adjudicates R1 in neither direction", and
  §5.9 says so twice: "No inferential quantity is computed, let alone
  published, at or above row 3."
* **Fixed-sequence gatekeeping, inside row 4.** A-C is tested first and A-B
  only if A-C CLAIMED; §5.4 point 5 registers that the fixed sequence spends no
  alpha. `decide()` therefore returns the A-B result only when A-C claimed, and
  says so in the record rather than leaving a reader to notice an absent member.

INDETERMINATE-BY-DISAGREEMENT licenses nothing — not equivalence, not either
direction's negation (§1.3's R1, §5.9's last row "this row triggers nothing",
and §9). The verdict strings below are the only ones this study publishes, so an
outcome cannot be described in prose the registration does not carry.
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
# §5.9 row 3's list, verbatim, plus §2a.5's C4 outcome. `e1-floor` IS NOT HERE:
# §5.7 rules the author-side existence gate out (M-23 option (a)) and §5.9 row 3
# says "There is no `e1-floor` row" in its own bytes.
CONTROL_GATES = (
    "references-reproduce-gold",
    "capabilities-canary-refused",
    "golden-context",
    "timeout-rate-within-cap",
    # §2a.5's transfer gate, two-sided: `calibration-invalid` (every
    # exact-equality row holds and only band rows differ -> the PILOT is
    # suspect) lands HERE, on row 3; `pipeline-invalid` (an exact-equality row
    # differs -> the BATCH is suspect) lands on row 1, in
    # `_pipeline_invalid()`'s problems. One observable, two rows, because the
    # two outcomes say different things about which artifact is wrong.
    "c4-transfer-calibration",
    # ROUND-1 R1-8. A pinned engine that refused on a FROZEN study artifact —
    # a reference during the identity control, a manifest mutant during
    # mutation execution — is an apparatus failure, and the old code counted it
    # as a kill in one direction and as an identity failure in the other. It is
    # neither, so it adjudicates R1 in no direction: the gate holds only when
    # every scored invocation of this attempt returned an answer. OWED TO THE
    # PROSE LANE: §5 row 2's parenthetical and §6's gate list must name it.
    "engine-execution-clean",
)

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


# §5.4 point 4: two-sided alpha per member, no correction. The IU test's size
# is <= alpha and is attained only in the least-favourable configuration; for a
# DIRECTIONAL claim, two-sided p < 0.05 plus a sign is a one-sided level-0.025
# test, so the family-wise type-I rate for a signed R1 is <= 0.025.
REGISTERED_ALPHA = 0.05
# §5.2: eighteen members, and membership is append-only after registration. The
# number is asserted rather than assumed because under §5.4's intersection-union
# logic REMOVING a member is the anti-conservative direction — a family scorer
# that silently produced seventeen would make the claim EASIER.
REGISTERED_FAMILY_SIZE = 18


def _family_claims(outcome):
    """Row 4. All eighteen members agree in the sign of the A-C difference AND
    all eighteen reject at two-sided alpha = 0.05.

    THE ROW READS TWO UNANIMITIES AND NOTHING ELSE. It does not read an
    interval (§5.3: "The word 'exact' is used only of a permutation null
    distribution, never of an interval... Intervals are Tier D... no decision
    reads them"), and it does not read a cut (§5.1: "No cut, no τ, no
    dichotomy"; §7 delta 2).

    A MISSING primary family decides nothing (019's round-1 R1-14, carried
    unchanged in force). It used to fall through to the last row, which
    publishes a substantive verdict — 020's is
    INDETERMINATE-BY-**DISAGREEMENT** — over an attempt in which no member was
    ever computed. Eighteen members that were never computed did not disagree;
    §5.9 says "An absent primary contrast is not a disagreeing one and never
    reaches row 5", the scorer is required to have refused above this row, and
    `decide()` asserts it.

    The family size is checked here rather than trusted: a verdict carrying
    fewer than the registered eighteen is refused, because §5.2 makes
    membership append-only precisely so that the family cannot shrink between
    registration and adjudication."""
    verdict = (outcome.get("family") or {}).get(CONTRAST_PRIMARY)
    if verdict is None:
        return []
    members = verdict.get("members") or []
    if len(members) < REGISTERED_FAMILY_SIZE:
        raise DecisionError(
            "DECISION-FAMILY-SHRANK the registered family is %d members (§5.2, "
            "append-only after registration) and the %s verdict carries %d: "
            "under §5.4's intersection-union rule a SMALLER family is the "
            "anti-conservative direction, so a short family is refused rather "
            "than adjudicated"
            % (REGISTERED_FAMILY_SIZE, CONTRAST_PRIMARY, len(members)))
    # R1-8: the EXACT registered id set, the closed verdict token, and a sign
    # from the closed vocabulary — eighteen arbitrary strings and a truthy
    # claim member must not adjudicate anything.
    from . import family as _family
    named = [member.get("id") if isinstance(member, dict) else member
             for member in members]
    if sorted(str(name) for name in named) != sorted(_family.MEMBER_IDS):
        raise DecisionError(
            "DECISION-FAMILY-NOT-THE-REGISTERED-SET the %s verdict names %s "
            "where the registration names %s; the decision layer validates "
            "the membership independently of the scorer that produced it"
            % (CONTRAST_PRIMARY, sorted(str(name) for name in named),
               sorted(_family.MEMBER_IDS)))
    if verdict.get("verdict") not in (_family.CLAIM, _family.INDETERMINATE):
        raise DecisionError(
            "DECISION-FAMILY-VERDICT-VOCABULARY %r is not in the closed "
            "vocabulary" % (verdict.get("verdict"),))
    if verdict.get("sign") not in ("+", "-", "none"):
        raise DecisionError(
            "DECISION-FAMILY-SIGN-VOCABULARY %r is not in the closed "
            "vocabulary" % (verdict.get("sign"),))
    if bool(verdict.get("claim")) != (verdict.get("verdict") == _family.CLAIM):
        raise DecisionError(
            "DECISION-FAMILY-INCONSISTENT claim %r beside verdict %r"
            % (verdict.get("claim"), verdict.get("verdict")))
    if not verdict.get("claim"):
        return []
    return ["all %d members agree in sign (%s) and all %d reject at two-sided "
            "alpha = %s" % (len(members), verdict.get("sign"), len(members),
                            REGISTERED_ALPHA)]


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
    registered="Any control-gate failure - both references reproduce gold "
               "imperfectly at attempt time; the capabilities canary passes; "
               "golden-context gate; engine-execution-clean; per-arm timeout "
               "rate above cap; C4's calibration-invalid outcome. There is no "
               "e1-floor row (§5.7)",
    predicate=_control_gate)

ROW_CLAIM = Row(
    name="claim",
    verdict="R1 = CLAIM",
    registered="All eighteen family members agree in the sign of the A-C "
               "difference and all eighteen reject at two-sided alpha = 0.05 "
               "-> R1 = CLAIM, direction the common sign; then A-B under the "
               "identical rule",
    predicate=_family_claims)

ROW_INDETERMINATE = Row(
    name="indeterminate-by-disagreement",
    verdict="INDETERMINATE-BY-DISAGREEMENT",
    registered="Otherwise -> INDETERMINATE-BY-DISAGREEMENT. No claim in any "
               "direction is licensed, and this row triggers nothing",
    predicate=_always)

# The table. Order IS the rule.
ROWS = (ROW_PIPELINE_INVALID, ROW_SHORTFALL_DECLARED, ROW_CONTROL_GATE,
        ROW_CLAIM, ROW_INDETERMINATE)

# The rows at or above which NO inferential quantity may be computed, let alone
# published (§5.9, in its own bytes). `harness/score.py` evaluates the gate rows
# FIRST, and evaluates the family only when the outcome would reach `ROW_CLAIM`
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


def direction(verdict: dict) -> str:
    """The direction of a CLAIMING family verdict, spelled in arms rather than
    in the family machinery's sign.

    §1.3: direction is reported as observed and never presupposed — §0.2 states
    the prior in full and states that it is not one direction.

    IT IS READ OFF THE COMMON SIGN, and only off a verdict that claims. §5.9
    row 4 registers "direction the common sign", which exists only when all
    eighteen members agree; a verdict that does not claim has no direction to
    report, and reporting one would publish a direction §5.9's last row says is
    not licensed. Study 019's round-1 R1-13 is the reason this reads a computed
    field rather than recomputing a comparison: its predecessor compared raw
    COUNTS, which agrees with the rate comparison only at equal denominators,
    and §1a makes unequal denominators the expected case.

    `arms` is the ordered pair the family evaluated, so "+" means the LEFT arm
    is above the right one and the naming is the family's, not this file's."""
    if not verdict.get("claim"):
        return "none - INDETERMINATE-BY-DISAGREEMENT"
    arms = verdict.get("arms")
    if not isinstance(arms, (list, tuple)) or len(arms) != 2:
        raise DecisionError(
            "DECISION-DIRECTION-UNREADABLE a claiming family verdict carries "
            "the arms %r, and a direction is a statement about an ordered pair "
            "of arms" % (arms,))
    left, right = arms
    sign = verdict.get("sign")
    if sign == "+":
        return "%s above %s" % (left, right)
    if sign == "-":
        return "%s above %s" % (right, left)
    raise DecisionError(
        "DECISION-DIRECTION-UNREADABLE a family verdict that CLAIMS carries "
        "the common sign %r, and §5.9 row 4 registers the direction as the "
        "common sign and nothing else" % (sign,))


def decide(outcome: dict) -> dict:
    """Walk the table in registered order and return the first matching row.

    `outcome` carries `pipelineProblems`, `shortfallDeclared`, `controlGates`,
    `family` and — 019's round-3 R3-8 — `secondaryRefusal`, the cause of an
    absent A-B once A-C has claimed; every member is optional and an absent one
    is treated as the state that FAILS, never as the state that passes."""
    for row in ROWS:
        causes = row.predicate(outcome)
        if not causes:
            continue
        if row is ROW_INDETERMINATE \
                and (outcome.get("family") or {}).get(CONTRAST_PRIMARY) is None:
            # 019's round-1 R1-14, second scenario, carried unchanged in force.
            # The last row's verdict is a SUBSTANTIVE one — the eighteen
            # members disagreed — and reaching it with no member in existence
            # publishes a disagreement that nothing measured. §5.9: "An absent
            # primary contrast is not a disagreeing one and never reaches row
            # 5." The scorer is required to have filed the missing family as a
            # pipeline problem above; if it did not, this refuses rather than
            # substituting the substantive row.
            raise DecisionError(
                "DECISION-NO-PRIMARY-FAMILY no gating row matched and the "
                "registered primary family %s was never evaluated: the last "
                "row's INDETERMINATE-BY-DISAGREEMENT is the statement that "
                "eighteen members disagreed, and no member exists"
                % CONTRAST_PRIMARY)
        record = {
            "row": row.name,
            "rowIndex": ROWS.index(row) + 1,
            "verdict": row.verdict,
            "registeredText": row.registered,
            "causes": causes,
        }
        if row is ROW_CLAIM:
            verdicts = outcome.get("family") or {}
            primary = verdicts[CONTRAST_PRIMARY]
            record["verdict"] = "R1 = CLAIM - %s" % direction(primary)
            record["primary"] = {CONTRAST_PRIMARY: direction(primary)}
            # Fixed-sequence gatekeeping: A-B is tested SECOND and only because
            # A-C claimed. §5.4 point 5 registers that the fixed sequence spends
            # no alpha. Reported with that condition attached, so no reader can
            # lift the secondary family out of the sequence.
            secondary = verdicts.get(CONTRAST_SECONDARY)
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
                    "DECISION-SECONDARY-UNEXPLAINED the primary family %s "
                    "claimed, so the registered sequence reached %s, and it is "
                    "neither computed nor refused: an absent secondary must "
                    "carry its cause in `secondaryRefusal`"
                    % (CONTRAST_PRIMARY, CONTRAST_SECONDARY))
            record["secondary"] = {
                "contrast": CONTRAST_SECONDARY,
                "testedBecause": "A-C claimed (fixed-sequence gatekeeping; "
                                 "§5.4 point 5: the fixed sequence spends no "
                                 "alpha, and no further adjustment is "
                                 "registered)",
                "result": None if secondary is None else direction(secondary),
                "refusal": refusal if secondary is None else None,
            }
        return record
    raise DecisionError(
        "DECISION-NOT-EXHAUSTIVE no row of section 5's ordered rule matched; the "
        "last row is registered to always match and this table's last row is %r"
        % ROW_INDETERMINATE.name)
