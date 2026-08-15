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


def test_row_2_control_gate_failed():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(e1_floor=False),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["rowIndex"] == 2
    assert verdict["causes"] == ["e1-floor"]


def test_row_3_decided():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["row"] == "decided"
    assert verdict["rowIndex"] == 3
    assert verdict["verdict"] == "R1 decided - A above C"


def test_row_4_indeterminate_is_the_last_row_and_always_matches():
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
                         "contrasts": {"A-C": contrast(50, 0)}})["row"],
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "contrasts": {}})["row"],
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


# --- direction, and the fixed sequence --------------------------------------

def test_direction_is_reported_as_observed_in_both_directions():
    above = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "contrasts": {"A-C": contrast(50, 0)}})
    below = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "contrasts": {"A-C": contrast(0, 50)}})
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


def test_a_decided_primary_with_no_secondary_computed_says_so():
    verdict = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                               "contrasts": {"A-C": contrast(50, 0)}})
    assert verdict["secondary"]["result"] is None


def test_direction_of_an_undecided_contrast_is_never_a_direction():
    assert decision.direction(contrast(25, 25)) == "none - INDETERMINATE"


# --- the table against the registration's own bytes -------------------------

SECTION = re.compile(r"\n\*\*Ordered, exhaustive decision rule\*\*.*?"
                     r"(?=\n## )", re.DOTALL)


def test_the_table_has_one_row_per_registered_numbered_row(preregistration):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, "section 5 holds %d ordered decision rules" % len(found)
    numbered = re.findall(r"^\d+\. ", found[0], re.MULTILINE)
    assert len(numbered) == len(decision.ROWS)


def test_the_last_registered_row_is_the_one_that_always_matches(preregistration):
    assert "last row always matches" in preregistration
    assert decision.ROWS[-1] is decision.ROW_INDETERMINATE
    assert decision.ROW_INDETERMINATE.predicate({}) == ["indeterminate"]


def test_indeterminate_licenses_nothing(preregistration):
    assert "An INDETERMINATE outcome licenses nothing" in preregistration
    assert decision.ROW_INDETERMINATE.verdict == "INDETERMINATE"


def test_the_registered_contrast_order_is_a_c_then_a_b(preregistration):
    """The registration wraps its lines, so the prose is flattened before it is
    read — the same treatment `tests/test_partition.py` gives section 1a."""
    flat = " ".join(preregistration.split())
    assert "tested **A−C first, then A−B** as fixed-sequence gatekeeping" in flat
    assert decision.CONTRAST_ORDER == ("A-C", "A-B")
    assert decision.CONTRAST_PRIMARY == "A-C"


def test_a_table_whose_last_row_stopped_matching_refuses(monkeypatch):
    """The exhaustiveness guarantee is asserted, not assumed: if the last row's
    predicate ever stopped being the constant true, `decide()` refuses rather
    than falling off the end with no verdict."""
    broken = decision.ROW_INDETERMINATE._replace(predicate=lambda outcome: [])
    monkeypatch.setattr(decision, "ROWS", decision.ROWS[:-1] + (broken,))
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "controlGates": gates()})
    assert str(raised.value).startswith("DECISION-NOT-EXHAUSTIVE")
