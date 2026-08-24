"""Section 5's ordered decision rule, driven through EVERY row.

Study 018's round-8 finding 1 was a decision rule whose code and whose
registration disagreed about which cells adjudicate, and an if-ladder gave
nothing to enumerate. This module enumerates: a synthetic outcome is built for
each registered row, driven through `decide()`, and the row it lands on is
asserted to be the row the registration names — plus the ordering assertions
that say WHY the rows are in this order.

The registration's own text is read out of `PREREGISTRATION.md`'s bytes, not out
of a copy of it (Study 012's round-12 lesson: a test module that was a copy
checking a copy stayed green through a registration-only edit).
"""
import re

import pytest

from e4lib import decision
from e4lib import stats


def gates(**overrides):
    state = {name: {"held": True} for name in decision.CONTROL_GATES}
    for name, held in overrides.items():
        state[name.replace("_", "-")] = {"held": held}
    return state


def contrast(left, right, arms=("A", "C")):
    result = stats.excludes_zero(left, right, 50)
    result["arms"] = list(arms)
    return result


# --- one case per registered row, in registered order -----------------------

def test_row_1_pipeline_invalid():
    verdict = decision.decide({"pipelineProblems": ["the pin registry is unreadable"],
                               "controlGates": gates(),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "pipeline-invalid"
    assert verdict["rowIndex"] == 1
    assert verdict["verdict"] == "R1 inconclusive - pipeline-invalid"


def test_row_2_shortfall_declared_is_unresolved_by_design():
    """ROUND-1 R1-7's enforcing test. A declared short batch is DECLARED rather
    than scored, above every substantive row and above the gates: the driver
    registers that price in `declare_shortfall()` and the scaffold repeats it,
    and the scorer used to compute ordinary endpoints and contrasts over the
    prefix anyway."""
    verdict = decision.decide({
        "pipelineProblems": [],
        "shortfallDeclared": ["87 of 150 registered slots, declared: power cut"],
        "controlGates": gates(c4_transfer_gate=False),
        "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "shortfall-declared"
    assert verdict["rowIndex"] == 2
    assert verdict["verdict"] == \
        "UNRESOLVED-BY-DESIGN - the batch was declared short"


def test_row_3_control_gate_failed():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(c4_transfer_gate=False),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["rowIndex"] == 3
    assert verdict["causes"] == ["c4-transfer-gate"]


def test_row_4_decided():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(),
                               "contrasts": {"A-C": contrast(50, 0),
                                             "A-B": contrast(50, 40,
                                                             arms=("A", "B"))}})
    assert verdict["row"] == "decided"
    assert verdict["rowIndex"] == 4
    assert verdict["verdict"] == "R1 decided - A above C"


def test_row_5_indeterminate_is_the_last_row_and_always_matches():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(),
                               "contrasts": {"A-C": contrast(25, 25)}})
    assert verdict["row"] == "indeterminate"
    assert verdict["rowIndex"] == len(decision.ROWS)
    assert verdict["verdict"] == "INDETERMINATE"


def test_every_row_is_reachable():
    """Exhaustive means every row matches something; ordered means no row is
    unreachable behind an earlier one that always fires."""
    reached = {
        decision.decide({"pipelineProblems": ["x"]})["row"],
        decision.decide({"pipelineProblems": [],
                         "controlGates": gates(golden_context=False)})["row"],
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "contrasts": {"A-C": contrast(50, 0),
                                       "A-B": contrast(50, 40,
                                                       arms=("A", "B"))}})["row"],
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "contrasts": {"A-C": contrast(25, 25)}})["row"],
        decision.decide({"shortfallDeclared": ["short"]})["row"],
    }
    assert reached == {row.name for row in decision.ROWS}


# --- the ordering, and what each ordering buys ------------------------------

def test_a_pipeline_failure_outranks_a_decided_contrast():
    """A pipeline-invalid attempt has no population, so a contrast computed over
    it is arithmetic on a set nobody can vouch for."""
    verdict = decision.decide({"pipelineProblems": ["terminality"],
                               "controlGates": gates(),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "pipeline-invalid"


def test_a_control_gate_failure_outranks_a_decided_contrast():
    """Section 5 row 2 adjudicates R1 "in neither direction". Reading the
    contrast first and then discarding it publishes a direction the
    registration says is not licensed."""
    verdict = decision.decide({
        "pipelineProblems": [],
        "controlGates": gates(capabilities_canary_refused=False),
        "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "control-gate-failed"
    assert "capabilities-canary-refused" in verdict["causes"]


def test_an_unevaluated_gate_fails_rather_than_passing_quietly():
    """Study 012's round 9 found all 150 calls reachable with the isolation
    assent still null. A control nobody evaluated is not a control that held."""
    partial = gates()
    del partial["golden-context"]
    verdict = decision.decide({"pipelineProblems": [], "controlGates": partial,
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["causes"] == ["golden-context (not evaluated)"]


def test_no_control_gates_at_all_fails_every_gate():
    verdict = decision.decide({"pipelineProblems": []})
    assert verdict["row"] == "control-gate-failed"
    assert len(verdict["causes"]) == len(decision.CONTROL_GATES)


def test_the_engine_execution_gate_is_a_registered_control_row():
    """ROUND-1 R1-8's enforcing test at the decision layer. A pinned engine that
    refused on a frozen artifact adjudicates R1 in NEITHER direction, so it is a
    control gate and not a number."""
    assert "engine-execution-clean" in decision.CONTROL_GATES
    verdict = decision.decide({
        "pipelineProblems": [],
        "controlGates": gates(engine_execution_clean=False),
        "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["causes"] == ["engine-execution-clean"]


# --- R1-14: nothing inferential below a gating row --------------------------

def test_gate_causes_is_empty_exactly_when_a_contrast_may_be_computed():
    """The predicate `harness/score.py` asks before it computes anything
    inferential, derived from the table rather than written out."""
    clean = {"pipelineProblems": [], "shortfallDeclared": [],
             "controlGates": gates()}
    assert decision.gate_causes(clean) == []
    for outcome in ({"pipelineProblems": ["x"], "controlGates": gates()},
                    {"pipelineProblems": [], "shortfallDeclared": ["short"],
                     "controlGates": gates()},
                    {"pipelineProblems": [],
                     "controlGates": gates(c4_transfer_gate=False)}):
        assert decision.gate_causes(outcome), outcome


def test_every_gating_row_is_a_row_of_the_table_and_precedes_every_other():
    assert decision.GATING_ROWS == decision.ROWS[:len(decision.GATING_ROWS)]
    assert decision.ROW_PRIMARY_DECIDED not in decision.GATING_ROWS


def test_the_last_row_refuses_when_no_primary_contrast_was_ever_computed():
    """ROUND-1 R1-14, second scenario: an arm with zero admitted runs passed
    E1's floor by definition, the contrast became a refusal, and the last row
    then published a substantive INDETERMINATE — "the interval straddles zero" —
    over an attempt in which no interval existed."""
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "contrasts": {}})
    assert str(raised.value).startswith("DECISION-NO-PRIMARY-CONTRAST")


# --- R1-13: the direction is the RATES', not the counts' --------------------

def test_direction_reads_the_statistical_functions_decision_field():
    """ROUND-1 R1-13's enforcing test, on the reviewer's own tuple.

    At 6/50 versus 5/6 the exact inversion reports a difference of -0.7133 with
    the RIGHT arm far above the left and excludes zero; comparing the raw counts
    reports 6 > 5 and therefore "A above C" — the study's conclusion, reversed,
    on the registered decision's own numbers. §1a makes unequal denominators the
    expected case, so this is not a corner."""
    result = stats.excludes_zero(6, 5, 50, 6)
    result["arms"] = ["A", "C"]
    assert result["excludesZero"] is True
    assert result["left"] > result["right"]          # the counts say A
    assert result["difference"] < 0                  # the rates say C
    assert round(result["difference"], 4) == -0.7133
    assert decision.direction(result) == "C above A"


def test_direction_refuses_a_decided_contrast_with_no_decision_field():
    broken = {"excludesZero": True, "arms": ["A", "C"], "left": 6, "right": 5,
              "decision": None}
    with pytest.raises(decision.DecisionError) as raised:
        decision.direction(broken)
    assert str(raised.value).startswith("DECISION-DIRECTION-UNREADABLE")


# --- direction, and the fixed sequence --------------------------------------

def test_direction_is_reported_as_observed_in_both_directions():
    secondary = contrast(50, 40, arms=("A", "B"))
    above = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "contrasts": {"A-C": contrast(50, 0),
                                           "A-B": secondary}})
    below = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "contrasts": {"A-C": contrast(0, 50),
                                           "A-B": secondary}})
    assert above["verdict"] == "R1 decided - A above C"
    assert below["verdict"] == "R1 decided - C above A"


def test_the_secondary_contrast_is_tested_only_because_the_primary_decided():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "contrasts": {"A-C": contrast(0, 50),
                      "A-B": contrast(0, 45, arms=("A", "B"))}})
    assert verdict["secondary"]["contrast"] == "A-B"
    assert verdict["secondary"]["result"] == "B above A"
    assert "fixed-sequence gatekeeping" in verdict["secondary"]["testedBecause"]


def test_an_indeterminate_primary_never_reports_a_secondary():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "contrasts": {"A-C": contrast(25, 25),
                      "A-B": contrast(0, 50, arms=("A", "B"))}})
    assert verdict["row"] == "indeterminate"
    assert "secondary" not in verdict


def test_a_decided_primary_with_no_secondary_computed_says_WHY():
    """ROUND-3 FINDING R3-8, and this test is STRENGTHENED rather than kept.

    It used to accept a bare `result: null` for an absent secondary, which is
    what let the scorer publish one: `FM-EMPTY-ARM` on A-B cleared the whole
    contrast set, and the decided row would have carried a null beside it that
    reads as "not decided" and is indistinguishable from "never computed". Once
    the primary decides, §5's sequence has REACHED the secondary, so it has a
    result or it has a cause."""
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "contrasts": {"A-C": contrast(50, 0)},
        "secondaryRefusal": "FM-EMPTY-ARM arm B has 0 admitted runs"})
    assert verdict["row"] == "decided"
    assert verdict["secondary"]["result"] is None
    assert verdict["secondary"]["refusal"].startswith("FM-EMPTY-ARM")


def test_a_decided_primary_with_a_silently_absent_secondary_refuses():
    """The other half of the same rule: no cause, no verdict."""
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "contrasts": {"A-C": contrast(50, 0)}})
    assert str(raised.value).startswith("DECISION-SECONDARY-UNEXPLAINED")


def test_a_computed_secondary_carries_no_refusal():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "contrasts": {"A-C": contrast(50, 0),
                      "A-B": contrast(50, 40, arms=("A", "B"))},
        "secondaryRefusal": "this must not be read when the secondary exists"})
    assert verdict["secondary"]["result"] == "A above B"
    assert verdict["secondary"]["refusal"] is None


def test_direction_of_an_undecided_contrast_is_never_a_direction():
    assert decision.direction(contrast(25, 25)) == "none - INDETERMINATE"


# --- the table against the registration's own bytes -------------------------

SECTION = re.compile(r"\n### 5\.9 Ordered, exhaustive decision rule.*?(?=\n## )",
                     re.DOTALL)


def unquoted(text):
    """One line, with blockquote markers removed.

    R1's own sentences live inside a `>` block, so a flatten that only collapsed
    whitespace would assert the QUOTING rather than the words — and the words
    are what is registered."""
    return " ".join(line.lstrip("> ") for line in text.splitlines()).replace(
        "  ", " ")


def test_the_table_has_one_row_per_registered_numbered_row(preregistration):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, "§5 holds %d ordered decision rules" % len(found)
    numbered = re.findall(r"^\d+\. ", found[0], re.MULTILINE)
    # Exact in both directions: a row added to the table without a numbered row
    # in §5.9 fails here, and so does a numbered row in §5.9 with no row behind
    # it. 020 registers FIVE, the same count as 019 and not the same five —
    # the `e1-floor` row is gone (M-23) and C4's two outcomes have taken seats
    # in rows 1 and 3.
    assert len(numbered) == len(decision.ROWS) == 5
    assert decision.ROWS[1] is decision.ROW_SHORTFALL_DECLARED
    flat = " ".join(found[0].split())
    assert ("2. A validated shortfall declaration (§1a) → UNRESOLVED-BY-DESIGN "
            "— no endpoint, no rate and no contrast is computed" in flat)


def test_the_abolished_gate_is_absent_from_the_table_and_from_the_prose(
        preregistration):
    """M-23 / §5.7, as a two-sided assertion. `e1-floor` was Study 019's row-3
    cause and the one its attempt actually failed on; 020 registers no
    author-side gate at all, and §5.9 says "There is no `e1-floor` row". A gate
    the registration abolished and the code still carries is a decision path the
    registration denies."""
    flat = " ".join(preregistration.split())
    assert "**There is no `e1-floor` row** (§5.7)." in flat
    assert "e1-floor" not in decision.CONTROL_GATES
    assert not any("e1" in gate for gate in decision.CONTROL_GATES)
    # …and E1 is registered as fully descriptive in its place.
    assert "**There is no E1 floor and no author-side control gate** (§5.7)" \
        in flat


def test_every_registered_control_gate_is_named_in_the_registration(
        preregistration):
    """The mapping is from the CODE's own tuple, so a gate added later without a
    prose edit fails here rather than at the attempt. 020's tuple differs from
    019's in exactly two places and both are registered changes: `e1-floor` is
    gone (M-23) and `c4-transfer-gate` is new (§2a.5)."""
    flat = " ".join(preregistration.split())
    registered_in_prose = {
        "references-reproduce-gold":
            "both references reproduce gold imperfectly at attempt time",
        "capabilities-canary-refused": "the capabilities canary passes",
        "golden-context": "golden-context gate",
        "timeout-rate-within-cap": "per-arm timeout rate above cap",
        "c4-transfer-gate": "**C4's `calibration-invalid` outcome**",
        "engine-execution-clean": "`engine-execution-clean`",
    }
    assert set(registered_in_prose) == set(decision.CONTROL_GATES)
    for gate, phrase in registered_in_prose.items():
        assert phrase in flat, "§5.9 row 3 does not name the gate %s" % gate
    assert "every scored engine invocation of the attempt returned an answer" in flat
    assert "**A gate the scorer did not evaluate fails**" in flat


def test_c4_is_two_sided_and_its_two_outcomes_reach_two_rows(preregistration):
    """§2a.5: "If every exact-equality row holds and only band rows differ, the
    pilot is suspect and the outcome is `calibration-invalid`, requiring a
    re-pilot under C5; if any exact-equality row differs, the batch is suspect
    and the outcome is `pipeline-invalid`." Two outcomes, two rows, and the
    table has to keep them apart: a suspect BATCH is not a control that merely
    failed."""
    flat = " ".join(preregistration.split())
    assert "**C4 is two-sided.**" in flat
    assert "or C4's `pipeline-invalid` outcome (§2a.5)** → R1 inconclusive" in flat
    assert "**C4's `calibration-invalid` outcome** → R1 inconclusive" in flat
    invalid = decision.decide({
        "pipelineProblems": ["C4 transfer gate: pipeline-invalid"],
        "controlGates": gates(), "contrasts": {"A-C": contrast(50, 0)}})
    assert invalid["row"] == "pipeline-invalid"
    calibration = decision.decide({
        "pipelineProblems": [], "controlGates": gates(c4_transfer_gate=False),
        "contrasts": {"A-C": contrast(50, 0)}})
    assert calibration["row"] == "control-gate-failed"


def test_the_registration_forbids_computing_a_contrast_above_the_gates(
        preregistration):
    """The ORDER is what is registered: the scorer may not compute an
    inferential quantity at or above the gate rows, because "adjudicates R1 in
    neither direction" is not satisfied by computing a direction and then
    declining to act on it."""
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert ("No inferential quantity is computed, let alone published, at or "
            "above row 3" in flat)
    assert ("An absent primary contrast is not a disagreeing one and never "
            "reaches row 5" in flat)
    assert decision.REGISTERED_MINIMUM_DENOMINATOR >= 1
    assert ("Each member's per-arm denominator must be positive" in flat)


def test_the_last_registered_row_is_the_one_that_always_matches(preregistration):
    assert "last row always matches" in preregistration
    assert decision.ROWS[-1] is decision.ROW_INDETERMINATE
    assert decision.ROW_INDETERMINATE.predicate({}) == ["indeterminate"]


def test_indeterminate_licenses_no_negation(preregistration):
    """019's sentence was "an INDETERMINATE outcome licenses nothing". 020's is
    stronger and is quoted from 019 §5 verbatim inside its own R1: it licenses
    no NEGATION — "not equivalence, not either direction's negation, and it
    triggers nothing"."""
    flat = " ".join(unquoted(preregistration).split())
    assert "**An INDETERMINATE outcome licenses no negation**" in flat
    assert ("not equivalence, not either direction's negation, and it triggers "
            "nothing" in flat)
    assert "**No claim in any direction is licensed, and this row triggers "\
        "nothing.**" in flat


def test_the_registered_contrast_order_is_a_c_then_a_b(preregistration):
    flat = " ".join(unquoted(preregistration).split())
    assert "Fixed sequence: **A−C, then A−B**." in flat
    assert ("The A−B step is evaluated under the identical eighteen-member "
            "unanimity rule and is reached only if the A−C step returns a "
            "claim." in flat)
    assert decision.CONTRAST_ORDER == ("A-C", "A-B")
    assert decision.CONTRAST_PRIMARY == "A-C"


def test_the_closed_verdict_vocabulary_is_registered_and_is_NOT_YET_IMPLEMENTED(
        preregistration):
    """THE KNOWN GAP, asserted in both directions so that closing it fails a
    test rather than passing silently.

    §1.3 closes the substantive verdict vocabulary to CLAIM and
    INDETERMINATE-BY-DISAGREEMENT, and both are verdicts of the EIGHTEEN-MEMBER
    intersection–union family. The family scorer is §7's delta 5 and
    `harness/SCAFFOLD.md` item S4; it has not landed, so rows 4 and 5 are still
    Study 019's single-contrast rows carrying 019's verdict strings.

    What is asserted: the registration closes the vocabulary; the module records
    it; the TABLE does not yet produce it; and `SCAFFOLD.md` names the gap. When
    S4 lands, the third assertion fails — which is the point of writing it."""
    flat = " ".join(preregistration.split())
    assert ("There is exactly one verdict vocabulary: CLAIM or "
            "INDETERMINATE-BY-DISAGREEMENT." in flat)
    assert "The word **UNSUPPORTED is not used anywhere in 020**" in flat
    assert decision.REGISTERED_VERDICT_VOCABULARY == \
        ("CLAIM", "INDETERMINATE-BY-DISAGREEMENT")
    assert decision.FAMILY_MEMBERS_REGISTERED == 18
    produced = {row.verdict for row in decision.ROWS}
    assert not (produced & set(decision.REGISTERED_VERDICT_VOCABULARY)), (
        "the table now produces a registered verdict: §7's delta 5 has landed "
        "and this test must be rebuilt against the family rule")
    import os
    scaffold = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "SCAFFOLD.md")
    with open(scaffold, "rb") as handle:
        owed = handle.read().decode("utf-8")
    assert "S4" in owed and "family scorer" in owed
    assert "INDETERMINATE-BY-DISAGREEMENT" in owed


def test_a_table_whose_last_row_stopped_matching_refuses(monkeypatch):
    """The exhaustiveness guarantee is asserted, not assumed: if the last row's
    predicate ever stopped being the constant true, `decide()` refuses rather
    than falling off the end with no verdict."""
    broken = decision.ROW_INDETERMINATE._replace(predicate=lambda outcome: [])
    monkeypatch.setattr(decision, "ROWS", decision.ROWS[:-1] + (broken,))
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "controlGates": gates()})
    assert str(raised.value).startswith("DECISION-NOT-EXHAUSTIVE")
