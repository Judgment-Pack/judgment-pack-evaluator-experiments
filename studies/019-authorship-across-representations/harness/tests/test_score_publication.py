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
        # No `x1ExcludedCases`: round-3 R3-9 retired it from the published
        # shape, and a fixture that still carries it is a fixture that would
        # hide its return.
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
    secondary = stats.excludes_zero(45, 40, 50, 50)
    secondary["arms"] = ["A", "B"]
    results = {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        # Round-3 R3-8: a decided primary REACHES the secondary, so an outcome
        # that carries neither a secondary nor a cause for its absence is one
        # `decide()` now refuses. The fixture carries the secondary.
        "decision": decision.decide({"pipelineProblems": [],
                                     "shortfallDeclared": [],
                                     "controlGates": gates(),
                                     "contrasts": {"A-C": contrast,
                                                   "A-B": secondary}}),
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
    secondary = stats.excludes_zero(45, 40, 50, 50)
    secondary["arms"] = ["A", "B"]
    base["contrasts"] = {"A-C": contrast, "A-B": secondary}
    without = decision.decide(dict(base))
    with_set = decision.decide(dict(base, reviewerSet={"killed": ["r-001"]}))
    assert without == with_set


# --- ROUND-2 R2-12: no marginal interval above row 4 either -----------------

def _published(gate_state, contrasts=None):
    """The publisher's own two steps, in the order `main()` runs them: the gate
    rows first, then the interval settlement, then the report."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gate_state, "contrasts": contrasts or {}}
    causes = decision.gate_causes(outcome)
    results = {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        "decision": decision.decide(outcome),
        "cuts": {},
        "e1": {}, "e2": {}, "e4": {"A": arm(1, 2)}, "e5": None,
        "contrasts": outcome["contrasts"],
        "contrastsGatedBy": causes,
        "refusals": {},
    }
    licensed = not causes
    reason = None if licensed else "; ".join(causes)
    settled = stats.fill_intervals(results, licensed, reason)
    return results, settled, score.results_markdown(results)


def test_a_failed_gate_publishes_no_marginal_interval():
    """THE REVIEWER'S R2-12 PROBE. §5: "No inferential quantity is computed, let
    alone published, at or above row 3." A failed-E1-gate probe with E4 1/2
    returned `control-gate-failed` and still printed `[0.0126, 0.9874]`.
    Contrast and direction suppression held, which is narrower than the
    prohibition."""
    results, settled, body = _published(gates(e1_floor=False))
    assert results["decision"]["row"] == "control-gate-failed"
    assert settled == 1
    block = results["e4"]["A"]["highKillRate"]
    assert block["ci95"] is None
    assert block["ci95State"] == stats.CI_SUPPRESSED
    assert "0.0126" not in body and "0.9874" not in body
    # The COUNTS are still published: a suppressed interval is not a withheld
    # observation, and a reader can still see 1 of 2.
    assert block["count"] == 1 and block["trials"] == 2


def test_an_outcome_that_reaches_the_substantive_rows_publishes_its_interval():
    """The other direction, so the suppression is a rule and not a removal."""
    # The real shape, from the real construction, so the report renders it.
    straddling = {decision.CONTRAST_PRIMARY: stats.excludes_zero(1, 1, 2, 2)}
    straddling[decision.CONTRAST_PRIMARY]["arms"] = ["A", "C"]
    results, settled, body = _published(gates(), straddling)
    assert not results["contrastsGatedBy"]
    assert settled == 1
    block = results["e4"]["A"]["highKillRate"]
    assert block["ci95State"] == stats.CI_COMPUTED
    assert block["ci95"][0] < block["rate"] < block["ci95"][1]
    assert "0.0126" in body and "0.9874" in body


# --- ROUND-3 FINDING R3-8: the LATE secondary failure -----------------------

def _sequence(e4_by_arm, gate_state=None):
    """`main()`'s own steps, in `main()`'s order and through `main()`'s own
    function: gate rows, the registered contrast sequence, the decision, then
    the interval settlement. Round-2's R2-12 helper above stops at the marginal
    blocks; this one exists because R3-8 lives in the ORDER."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gate_state or gates(), "contrasts": {}}
    refusals = {}
    causes = decision.gate_causes(outcome)
    contrasts = score.registered_contrasts(e4_by_arm, outcome, refusals, causes)
    outcome["contrasts"] = contrasts
    verdict = decision.decide(outcome)
    licensed = not causes and not outcome["pipelineProblems"]
    reason = None if licensed else "; ".join(causes + outcome["pipelineProblems"])
    results = {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        "decision": verdict,
        "cuts": {}, "e1": {}, "e2": {}, "e4": e4_by_arm, "e5": None,
        "contrasts": contrasts,
        "contrastsGatedBy": causes,
        "refusals": refusals,
    }
    settled = stats.fill_intervals(results, licensed, reason)
    return results, refusals, settled


# The reviewer's R3-8 population, verbatim: "With gates initially clear,
# A = 5/5, C = 0/5, and B = 0/0, A−C eagerly computes its interval endpoints;
# then A−B raises `FM-EMPTY-ARM`, contrasts are cleared, and the final row is
# pipeline-invalid."
def _r3_8_arms():
    return {"A": arm(5, 5, "A"), "B": arm(0, 0, "B"), "C": arm(0, 5, "C")}


def test_a_late_secondary_failure_leaves_the_decided_primary_standing():
    """THE REVIEWER'S R3-8 PROBE.

    The primary A−C is a real comparison over two full arms and it decides. The
    secondary A−B cannot exist, because B has no admitted run at all. Sharing
    one `except` made that delete the primary, file itself under the primary's
    name, and land the whole attempt on row 1 — so an attempt that measured a
    difference published `pipeline-invalid` instead of it.

    §5's decided row registers the sequence as conditional: "A−C interval
    excludes zero -> R1 decided, direction as observed; then A−B likewise"."""
    results, refusals, _settled = _sequence(_r3_8_arms())
    assert results["decision"]["row"] == "decided"
    assert results["decision"]["rowIndex"] == 4
    assert results["decision"]["primary"] == {"A-C": "A above C"}
    assert results["decision"]["secondary"]["result"] is None
    assert "FM-EMPTY-ARM" in results["decision"]["secondary"]["refusal"]
    assert "FM-EMPTY-ARM" in refusals["contrastSecondary"]
    # …and the primary is not deleted along with it.
    assert set(results["contrasts"]) == {"A-C"}


def test_a_decided_primary_with_a_silently_absent_secondary_refuses():
    """The safeguard the fix rests on. A bare `result: null` reads as "not
    decided" and is indistinguishable from "never computed", so once the primary
    has decided the secondary must carry either a result or a cause."""
    primary = stats.excludes_zero(5, 0, 5, 5)
    primary["arms"] = ["A", "C"]
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(),
                         "contrasts": {"A-C": primary}})
    assert str(raised.value).startswith("DECISION-SECONDARY-UNEXPLAINED")


def test_no_contrast_endpoint_is_computed_before_the_row_is_known():
    """R3-8's first half, at the level the prohibition is written on. §5: "No
    inferential quantity is COMPUTED, let alone published, at or above row 3" —
    and a Delta0 sweep that has run cannot be un-run by clearing the dict it
    landed in. So the contrast leaves `contrast()` with its endpoints PENDING
    and `stats.fill_intervals()` settles them after `decide()` has chosen the
    row."""
    e4_by_arm = {"A": arm(5, 5, "A"), "C": arm(0, 5, "C")}
    built = score.contrast("A", "C", e4_by_arm)
    assert built["interval"] is None
    assert built["intervalState"] == stats.INTERVAL_PENDING
    assert built["excludesZero"] is True, "the DECISION is fixed here, not later"


def test_a_gate_that_fails_suppresses_the_contrast_endpoints_too():
    """The settlement is licensed by the same predicate the marginal blocks
    are. A failed gate means the contrast is never built at all; a PRIMARY that
    refuses means the pending contrast never exists either — so the assertion
    that bites is on a run where the row is known late: gates held, primary
    decided, secondary refused, endpoints computed for the primary only."""
    results, _refusals, settled = _sequence(_r3_8_arms())
    primary = results["contrasts"]["A-C"]
    assert primary["intervalState"] == stats.INTERVAL_COMPUTED
    assert primary["interval"]["lower"] and primary["interval"]["upper"]
    # One marginal block per arm with a POSITIVE denominator — A and C; B's is
    # `undefined-over-an-empty-denominator` and was never pending — plus the one
    # contrast that exists.
    assert settled == 3
    assert results["e4"]["B"]["highKillRate"]["ci95State"] == stats.CI_EMPTY
    body = score.results_markdown(results)
    assert "A above C" in body


def test_a_suppressed_outcome_settles_its_pending_contrast_as_suppressed():
    """The other direction: a pending contrast reaching the settlement under a
    failed gate is SUPPRESSED with its cause, never silently left null."""
    pending = stats.excludes_zero(5, 0, 5, 5)
    pending["arms"] = ["A", "C"]
    pending["interval"] = None
    pending["intervalState"] = stats.INTERVAL_PENDING
    node = {"contrasts": {"A-C": pending}}
    assert stats.fill_intervals(node, False, "e1-floor") == 1
    assert pending["intervalState"] == stats.INTERVAL_SUPPRESSED
    assert pending["intervalSuppressed"] == "e1-floor"
    assert pending["interval"] is None


def test_an_endpoint_sweep_that_refuses_leaves_the_decision_intact():
    """§5 reads `excludesZero` and nothing else, so a refused REPORT is not a
    refused decision — asserted through the settlement path now that the sweep
    runs there."""
    pending = stats.excludes_zero(1, 0, 1, 1)
    pending["arms"] = ["A", "C"]
    pending["interval"] = None
    pending["intervalState"] = stats.INTERVAL_PENDING
    saved = stats.interval_endpoints

    def refuse(*_args, **_kwargs):
        raise stats.StatsError("FM-EMPTY-ACCEPTANCE nothing to sweep")

    stats.interval_endpoints = refuse
    try:
        stats.fill_intervals({"contrasts": {"A-C": pending}}, True)
    finally:
        stats.interval_endpoints = saved
    assert pending["intervalState"] == stats.INTERVAL_REFUSED
    assert pending["intervalRefusal"].startswith("FM-EMPTY-ACCEPTANCE")
    assert pending["excludesZero"] is False or pending["excludesZero"] is True
    assert "decision" in pending
