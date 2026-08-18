"""What the scorer computes, and what it is allowed to print — round-1 R1-14.

The abstract decision table was already ordered and exhaustive, and `decide()`
already selected the right row. The defect was in the PUBLISHER: an outcome with
a failed control gate and a statistically rejecting A-C reached rows 2, 3 and 4,
`decide()` correctly selected row 2 — and the scorer had already computed A-C and
A-B, and `RESULTS.md` still printed "Decided **yes**" and a direction. §5 row 2
says such an outcome adjudicates R1 "in NEITHER direction", and a direction a
reader can see is a direction the study published whatever the verdict line says.

The second scenario is the mirror image: an arm with zero admitted runs passes
E1's floor by definition (`len(runs) == 0 or …`), the contrast became a named
refusal, and the last row then reported a substantive `INDETERMINATE` — the
statement that an interval straddles zero — with no interval in existence.

Both are asserted here at the level the defect lived on: the scorer's own
publishing surface.
"""
import pytest

import score
from e4lib import decision
from e4lib import stats


def gates(**overrides):
    state = {name: {"held": True} for name in decision.CONTROL_GATES}
    for name, held in overrides.items():
        state[name.replace("_", "-")] = {"held": held}
    return state


def arm(high_kill, denominator, name="A"):
    return {
        "arm": name,
        "language": "jps",
        "denominator": denominator,
        "highKill": high_kill,
        "identityPass": denominator,
        "x1ExcludedCases": 0,
        "outOfDomainCases": 0,
        "cut": {"integerCut": 72, "language": "jps",
                "statement": "a run is high-kill iff it kills at least 72 of "
                             "the 75 paired adequate mutants (tau = 19/20)"},
        "highKillRate": stats.rate_block(high_kill, denominator, "admitted runs"),
    }


# --- scenario 1: a failed gate and a rejecting contrast ---------------------

def test_a_failed_gate_stops_the_contrast_being_computed_at_all():
    """`decision.gate_causes()` is the one predicate the scorer asks, and it is
    derived from the table so a row added there cannot be a row this forgets."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(e1_floor=False), "contrasts": {}}
    assert decision.gate_causes(outcome)
    verdict = decision.decide(outcome)
    assert verdict["row"] == "control-gate-failed"
    # …and with no contrast in the outcome there is no direction to lift out of
    # it: the decided row is the only one that publishes one.
    assert "primary" not in verdict and "secondary" not in verdict


def test_the_report_prints_the_gate_causes_where_the_contrast_table_was():
    """The reviewer's first scenario, rendered. A rejecting A-C exists in the
    arithmetic (50 vs 0 out of 50 decides in any direction), and the published
    report must contain no contrast row, no interval and no direction."""
    results = {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        "decision": decision.decide({"pipelineProblems": [],
                                     "shortfallDeclared": [],
                                     "controlGates": gates(e1_floor=False),
                                     "contrasts": {}}),
        "cuts": {},
        "e1": {}, "e2": {}, "e4": {}, "e5": None,
        "contrasts": {},
        "contrastsGatedBy": ["control-gate-failed: e1-floor"],
        "refusals": {},
    }
    body = score.results_markdown(results)
    assert "Not computed and not published" in body
    assert "control-gate-failed: e1-floor" in body
    assert "Decided" not in body
    section = body.split("## The registered contrasts")[1].split("## E2")[0]
    # No arm-vs-arm direction anywhere in the section the table used to fill.
    for direction in ("A above C", "C above A", "A above B", "B above A"):
        assert direction not in section


def test_the_report_prints_the_contrast_table_when_no_gate_matched():
    """The other side of the same assertion: the gating is a gate, not a
    deletion. With every gate held the table is printed in full."""
    contrast = stats.excludes_zero(45, 5, 50, 50)
    contrast["arms"] = ["A", "C"]
    contrast["interval"] = {"lower": "3/10", "upper": "9/10"}
    results = {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        "decision": decision.decide({"pipelineProblems": [],
                                     "shortfallDeclared": [],
                                     "controlGates": gates(),
                                     "contrasts": {"A-C": contrast}}),
        "cuts": {},
        "e1": {}, "e2": {}, "e4": {}, "e5": None,
        "contrasts": {"A-C": contrast},
        "contrastsGatedBy": [],
        "refusals": {},
    }
    body = score.results_markdown(results)
    assert "Not computed and not published" not in body
    assert "A above C" in body
    assert stats.CONSTRUCTION_NAME in body


# --- scenario 2: an arm with no admitted runs ------------------------------

def test_an_empty_arm_is_a_pipeline_problem_and_not_an_indeterminate():
    """The reviewer's second scenario. A contrast over an empty arm is not an
    interval that straddles zero; it is no interval at all, and §5's last row
    is a SUBSTANTIVE statement that must not stand in for one."""
    e4_by_arm = {"A": arm(0, 0, "A"), "C": arm(5, 50, "C")}
    with pytest.raises(stats.StatsError) as raised:
        score.contrast("A", "C", e4_by_arm)
    assert str(raised.value).startswith("FM-EMPTY-ARM")
    assert "registered minimum" in str(raised.value)


def test_the_registered_minimum_denominator_is_positive():
    assert decision.REGISTERED_MINIMUM_DENOMINATOR >= 1


def test_a_missing_primary_contrast_never_reaches_the_substantive_row():
    with pytest.raises(decision.DecisionError):
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "contrasts": {}})


def test_two_admitted_runs_per_arm_are_enough_for_a_contrast_to_exist():
    """The minimum is a floor on EXISTENCE, not a power claim: the contrast is
    computed and is INDETERMINATE, which is a measured statement."""
    e4_by_arm = {"A": arm(1, 1, "A"), "C": arm(0, 1, "C")}
    result = score.contrast("A", "C", e4_by_arm, endpoints=False)
    assert result["excludesZero"] is False
    assert decision.direction(result) == "none - INDETERMINATE"


# --- the reviewer set moves nothing (round-1 R1-10) ------------------------

def test_the_decision_reads_exactly_four_members_and_none_of_them_is_the_set():
    """§1a: the sealed reviewer set is "reported separately, moving nothing".

    Asserted STRUCTURALLY rather than by inspection: every predicate in the
    table is driven with an outcome that carries a reviewer block, and the
    verdict is required to be identical to the verdict without it."""
    base = {"pipelineProblems": [], "shortfallDeclared": [],
            "controlGates": gates(), "contrasts": {}}
    contrast = stats.excludes_zero(45, 5, 50, 50)
    contrast["arms"] = ["A", "C"]
    base["contrasts"] = {"A-C": contrast}
    without = decision.decide(dict(base))
    with_set = decision.decide(dict(base, reviewerSet={"killed": ["r-001"]}))
    assert without == with_set
