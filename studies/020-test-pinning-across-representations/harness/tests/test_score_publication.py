"""What the scorer computes, and what it is allowed to print — 019's R1-14 and
R2-12, carried onto 020's family row.

The abstract decision table was already ordered and exhaustive, and `decide()`
already selected the right row. The defect was in the PUBLISHER: an outcome with
a failed control gate and a statistically rejecting A−C reached the substantive
row's arithmetic anyway, and `RESULTS.md` printed "Decided **yes**" and a
direction. §5.9 row 3 says such an outcome adjudicates R1 "in NEITHER
direction", and a direction a reader can see is a direction the study published
whatever the verdict line says.

R2-12 is the same prohibition one level down: a failed-gate probe still printed
a marginal Clopper–Pearson interval, and §5.9's sentence is "No inferential
quantity is computed, let alone published, at or above row 3" — not "no
contrast".

REBUILT FOR §7 DELTAS 2 AND 5. The substantive row no longer reads a binomial
contrast over a high-kill count (§5.1: "No cut, no τ, no dichotomy"); it reads
the eighteen-member family's two unanimities, and the family scorer is a
separate module (§7 delta 5). What is asserted here is therefore the
PUBLISHER's behaviour around that module — including its absence, which §5.4
makes a pipeline problem rather than a smaller family.
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


def arm(covered, denominator, name="A"):
    """One arm's E4 block in 020's published shape.

    No `highKill`, no `cut` and no `highKillRate`: §7 delta 2 removed the
    threshold, and a fixture that still carried one would hide its return. What
    the block does carry is the ITT denominator, the per-protocol denominator,
    both identity relations and the per-run coverage counts — the inputs the
    family scorer weights."""
    return {
        "arm": name,
        "language": "jps",
        "denominator": denominator,
        "perProtocolDenominator": denominator,
        "referenceIdentityPass": denominator,
        "ownPolicyIdentityPass": denominator,
        "bothIdentitiesPass": denominator,
        "coverageCounts": [covered] * denominator,
        "sharedClassCount": 33,
        "outOfDomainCases": 0,
        "pairedDenominator": {"language": "jps", "pairedAdequateMutants": 69,
                              "lattice": 1 / 69.0, "statement": "…"},
        "identityRate": stats.rate_block(denominator, denominator,
                                         "admitted runs"),
        "ownPolicyIdentityRate": stats.rate_block(denominator, denominator,
                                                  "admitted runs"),
    }


def family(claim=True, sign="+", arms=("A", "C")):
    # R1-8 moved the decision layer onto the production verdict shape (closed
    # `verdict` token, exact registered id set), so this fixture carries both;
    # the per-member dicts stay because the PUBLICATION renders their columns.
    return {"contrast": "%s-%s" % arms, "arms": list(arms),
            "members": [{"id": "M%d" % (index + 1), "level": "L1",
                         "engine": "incl", "population": "ITT",
                         "adjustment": None, "n": "38/37/39",
                         "difference": 0.1 if sign == "+" else -0.1,
                         "p": 0.001, "rejects": True}
                        for index in range(decision.REGISTERED_FAMILY_SIZE)],
            "signUnanimous": claim, "allReject": claim, "sign": sign,
            "claim": claim,
            "verdict": "CLAIM" if claim else "INDETERMINATE-BY-DISAGREEMENT"}


def _runs():
    """One admitted run per arm, in the shape `family.unit_from_kill_record()`
    reads: a run id, an identity verdict, a `caseCount` and a `kill` block."""
    return {name: [{"run": "run-001", "referenceIdentityPass": True,
                    "caseCount": 12,
                    "kill": {"survivorsPaired": [], "killedPaired": 33}}]
            for name in ("A", "B", "C")}


def _context():
    return {"pairing": [], "engineSupplied": {"jps": [], "rego": []}}


def results_for(verdict, gated_by, family_verdicts, e4=None):
    return {
        "label": "PILOT",
        "unfilledPins": ["studyManifest"],
        "decision": verdict,
        "pairedDenominators": {}, "sharedClasses": {"count": 33,
                                                    "unequalCount": 20},
        "e1": {}, "e2": {}, "e4": e4 or {}, "e5": None,
        "family": family_verdicts,
        "familyGatedBy": gated_by,
        "refusals": {},
    }


# --- scenario 1: a failed gate and a claiming family ------------------------

def test_a_failed_gate_stops_the_family_being_evaluated_at_all():
    """`decision.gate_causes()` is the one predicate the scorer asks, and it is
    derived from the table so a row added there cannot be a row this forgets."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(golden_context=False), "family": {}}
    assert decision.gate_causes(outcome)
    verdict = decision.decide(outcome)
    assert verdict["row"] == "control-gate-failed"
    # …and with no family in the outcome there is no direction to lift out of
    # it: the claiming row is the only one that publishes one.
    assert "primary" not in verdict and "secondary" not in verdict


def test_the_publisher_refuses_to_evaluate_the_family_above_a_gating_row():
    """`registered_family()` is the publisher's own entry point, and the
    refusal is recorded rather than the evaluation being skipped silently."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(golden_context=False), "family": {}}
    refusals = {}
    causes = decision.gate_causes(outcome)
    verdicts = score.registered_family({}, {}, {}, outcome, refusals, causes)
    assert verdicts == {}
    assert "not computed" in refusals["family"]
    assert "neither direction" in refusals["family"]


def test_the_report_prints_the_gate_causes_where_the_family_table_was():
    """The reviewer's first scenario, rendered. The published report must
    contain no member row, no p-value and no direction."""
    results = results_for(
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(golden_context=False),
                         "family": {}}),
        ["control-gate-failed: golden-context"], {})
    body = score.results_markdown(results)
    assert "Not computed and not published" in body
    assert "control-gate-failed: golden-context" in body
    section = body.split("## The registered family")[1].split("## E2")[0]
    # No arm-vs-arm direction, no verdict and no member row anywhere in the
    # section the table used to fill. (The DECISION table above it prints every
    # registered row's text with "matched: no" beside it, which is the rule
    # being published rather than a result — so the assertion is scoped to the
    # section that would carry the finding.)
    for direction in ("A above C", "C above A", "A above B", "B above A"):
        assert direction not in section
    assert "CLAIM" not in section
    assert "| M1 |" not in section


def test_the_report_prints_the_family_table_when_no_gate_matched():
    """The other side of the same assertion: the gating is a gate, not a
    deletion. With every gate held the eighteen members are printed in full —
    §5.2: "Every member is published whatever the verdict."""
    verdicts = {"A-C": family(), "A-B": family(arms=("A", "B"))}
    results = results_for(
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "family": verdicts}),
        [], verdicts)
    body = score.results_markdown(results)
    assert "Not computed and not published" not in body
    assert "A above C" in body
    assert body.count("| M18 |") == 2          # both contrasts' member tables
    assert "intersection–union" in body


def test_the_report_publishes_every_member_even_when_the_family_disagrees():
    """§5.2's append-only rule exists because dropping a member is the
    anti-conservative direction, and §5.8 registers "the published quantity set
    is identical in every branch". A disagreeing family still prints eighteen
    rows."""
    verdicts = {"A-C": family(claim=False)}
    results = results_for(
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "family": verdicts}),
        [], verdicts)
    body = score.results_markdown(results)
    assert "INDETERMINATE-BY-DISAGREEMENT" in body
    assert body.count("| M18 |") == 1


# --- §7 delta 5's absence is a pipeline problem, not a smaller family -------

def test_an_absent_family_module_is_a_named_pipeline_problem():
    """§5.4's intersection–union logic makes a SMALLER family the
    anti-conservative direction, so the publisher does not proceed on the
    members that happen to be importable — it files the absence on row 1."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(), "family": {}}
    refusals = {}
    saved = score.family_module
    score.family_module = lambda: None
    try:
        verdicts = score.registered_family({}, _runs(), _context(), outcome,
                                           refusals, [])
    finally:
        score.family_module = saved
    assert verdicts == {}
    assert "e4lib/family.py is absent" in refusals["family"]
    assert outcome["pipelineProblems"]
    assert "eighteen-member" in outcome["pipelineProblems"][0]
    # …and the attempt lands on row 1 rather than on the substantive last row.
    assert decision.decide(outcome)["row"] == "pipeline-invalid"


def test_a_family_evaluation_that_raises_never_reaches_the_substantive_row():
    """019's R1-14, second scenario, in 020's shape: §5.9's last row is the
    statement that eighteen members disagreed, and a family that raised did not
    disagree."""
    class _Raising(object):
        @staticmethod
        def build_corpus(*_args, **_kwargs):
            return object()

        @staticmethod
        def unit_from_kill_record(*_args, **_kwargs):
            return object()

        @staticmethod
        def family_report(*_args, **_kwargs):
            raise ValueError("the pooled coverage marginal is empty")

    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(), "family": {}}
    refusals = {}
    saved = score.family_module
    score.family_module = lambda: _Raising
    try:
        verdicts = score.registered_family({}, _runs(), _context(), outcome,
                                           refusals, [])
    finally:
        score.family_module = saved
    assert verdicts == {}
    assert "ValueError" in refusals["family"]
    assert decision.decide(outcome)["row"] == "pipeline-invalid"


def test_a_secondary_that_raises_leaves_the_claiming_primary_standing():
    """019's round-3 finding R3-8, carried onto the family row. The primary is a
    real comparison over two full arms and it claims; the secondary cannot be
    evaluated. Sharing one `except` made that delete the primary and land the
    whole attempt on row 1 — an attempt that measured a difference publishing
    `pipeline-invalid` instead of it."""
    class _SecondaryRaises(object):
        @staticmethod
        def build_corpus(*_args, **_kwargs):
            return object()

        @staticmethod
        def unit_from_kill_record(*_args, **_kwargs):
            return object()

        @staticmethod
        def family_report(_units, _corpus, _left, right, *_a, **_k):
            if right == "B":
                raise ValueError("FM-EMPTY-ARM arm B has 0 admitted runs")
            block = family()
            return {"verdict": block, "members": block["members"]}

    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(), "family": {}}
    refusals = {}
    saved = score.family_module
    score.family_module = lambda: _SecondaryRaises
    try:
        verdicts = score.registered_family({}, _runs(), _context(), outcome,
                                           refusals, [])
    finally:
        score.family_module = saved
    outcome["family"] = verdicts
    verdict = decision.decide(outcome)
    assert verdict["row"] == "claim"
    assert verdict["primary"] == {"A-C": "A above C"}
    assert verdict["secondary"]["result"] is None
    assert "FM-EMPTY-ARM" in verdict["secondary"]["refusal"]
    assert "FM-EMPTY-ARM" in refusals["familySecondary"]
    # …and the primary is not deleted along with it.
    assert set(verdicts) == {"A-C"}


def test_the_registered_minimum_denominator_is_positive():
    assert decision.REGISTERED_MINIMUM_DENOMINATOR >= 1


def test_a_missing_primary_family_never_reaches_the_substantive_row():
    with pytest.raises(decision.DecisionError):
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "family": {}})


# --- the reviewer set moves nothing (019's R1-10) --------------------------

def test_the_decision_reads_exactly_four_members_and_none_of_them_is_the_set():
    """§1a: the sealed reviewer set is "reported separately, moving nothing".

    Asserted STRUCTURALLY rather than by inspection: the table is driven with an
    outcome that carries a reviewer block, and the verdict is required to be
    identical to the verdict without it."""
    base = {"pipelineProblems": [], "shortfallDeclared": [],
            "controlGates": gates(),
            "family": {"A-C": family(), "A-B": family(arms=("A", "B"))}}
    without = decision.decide(dict(base))
    with_set = decision.decide(dict(base, reviewerSet={"killed": ["r-001"]}))
    assert without == with_set


# --- R2-12: no marginal interval above row 3 either ------------------------

def _published(gate_state, family_verdicts=None):
    """The publisher's own two steps, in the order `main()` runs them: the gate
    rows first, then the interval settlement, then the report."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gate_state, "family": family_verdicts or {}}
    causes = decision.gate_causes(outcome)
    results = results_for(decision.decide(outcome), causes,
                          outcome["family"], e4={"A": arm(1, 2)})
    licensed = not causes
    reason = None if licensed else "; ".join(causes)
    settled = stats.fill_intervals(results, licensed, reason)
    return results, settled, score.results_markdown(results)


def test_a_failed_gate_publishes_no_marginal_interval():
    """THE REVIEWER'S R2-12 PROBE, retargeted at a rate 020 still publishes.

    §5.9: "No inferential quantity is computed, let alone published, at or above
    row 3." The probe's original subject was E4's high-kill rate, which §7 delta
    2 removed; the identity rate is a marginal Clopper–Pearson block on the same
    publishing path and the prohibition is the same."""
    results, settled, body = _published(gates(golden_context=False))
    assert results["decision"]["row"] == "control-gate-failed"
    assert settled == 2                      # identity and ownPolicyIdentity
    block = results["e4"]["A"]["identityRate"]
    assert block["ci95"] is None
    assert block["ci95State"] == stats.CI_SUPPRESSED
    assert "0.1581" not in body
    # The COUNTS are still published: a suppressed interval is not a withheld
    # observation, and a reader can still see 2 of 2.
    assert block["count"] == 2 and block["trials"] == 2


def test_an_outcome_that_reaches_the_substantive_rows_publishes_its_interval():
    """The other direction, so the suppression is a rule and not a removal."""
    verdicts = {"A-C": family(claim=False)}
    results, settled, _body = _published(gates(), verdicts)
    assert not results["familyGatedBy"]
    assert settled == 2
    block = results["e4"]["A"]["identityRate"]
    assert block["ci95State"] == stats.CI_COMPUTED
    assert block["ci95"][0] <= block["rate"] <= block["ci95"][1]


# --- the interval settlement's own contract --------------------------------

def test_a_suppressed_pending_block_settles_as_suppressed_with_its_cause():
    """A pending block reaching the settlement under a failed gate is
    SUPPRESSED with its cause, never silently left null."""
    block = stats.rate_block(3, 10, "admitted runs")
    node = {"e4": {"A": {"identityRate": block}}}
    assert stats.fill_intervals(node, False, "golden-context") == 1
    assert block["ci95State"] == stats.CI_SUPPRESSED
    assert block["ci95"] is None


def test_an_empty_denominator_settles_as_empty_rather_than_as_an_interval():
    block = stats.rate_block(0, 0, "admitted runs")
    node = {"e4": {"B": {"identityRate": block}}}
    stats.fill_intervals(node, True)
    assert block["ci95State"] == stats.CI_EMPTY


# --- ROUND-2 R2-1 STEP 7: one population, reconciled --------------------------

def _counted(arm_cells):
    counted = {}
    for name, (attempted, batch_apparatus) in arm_cells.items():
        counted[name] = {
            "registered": attempted, "absent": 0, "attempted": attempted,
            "apparatusExcluded": batch_apparatus,
            "denominator": attempted - batch_apparatus,
            "apparatusCodes": ({"call-timeout": batch_apparatus}
                               if batch_apparatus else {}),
            "timeouts": batch_apparatus,
            "timeoutRate": stats.rate_block(batch_apparatus, attempted,
                                            "attempted runs"),
            "apparatusRate": stats.rate_block(batch_apparatus, attempted,
                                              "attempted runs"),
            "slots": [],
        }
    return counted


def test_the_published_population_counts_the_scoring_time_refusals_too():
    """R2-1's fourth mechanism: `population()` partitions the SLOT records,
    every endpoint strips the runs the scorer coded `engine-invocation-
    refused`, and the published `population[arm]["denominator"]` disagreed
    with `e2`/`e4`'s by exactly the number of scoring-time refusals — which
    §1a's amended table names as apparatus. Arm B: five attempted, no batch-
    time apparatus, ONE scoring-time refusal.

    MUTATION: publish the raw `counted` projection again — every assertion
    but `preScoringDenominator` fails."""
    counted = _counted({"A": (5, 0), "B": (5, 0), "C": (5, 1)})
    scoring = {"A": [], "B": [{"run": "run-003", "refusal": "opa-refused"}],
               "C": []}
    runs = {"A": [{}] * 5, "B": [{}] * 4, "C": [{}] * 4}
    e2 = {arm: {"denominator": len(runs[arm])} for arm in runs}
    e4 = {arm: {"denominator": len(runs[arm])} for arm in runs}
    population = score.reconciled_population(counted, scoring, runs, e2, e4)
    b = population["B"]
    assert b["denominator"] == 4
    assert b["scoringApparatusExcluded"] == 1
    assert b["batchApparatusExcluded"] == 0
    assert b["apparatusExcluded"] == 1
    assert b["apparatusRate"] == stats.rate_block(1, 5, "attempted runs")
    assert b["apparatusRate"] != counted["B"]["apparatusRate"]
    assert b["preScoringDenominator"] == 5
    assert b["scoringApparatusRefusals"] == scoring["B"]
    # arm C: the batch-time half and the scoring-time half add.
    assert population["C"]["apparatusExcluded"] == 1
    assert population["C"]["denominator"] == 4
    for arm in runs:
        assert population[arm]["denominator"] == e2[arm]["denominator"] \
            == e4[arm]["denominator"]


def test_a_population_whose_endpoints_disagree_is_not_published():
    """The invariant is a refusal, not a warning: an endpoint that counted the
    population differently from the reconciled block aborts the attempt
    before a document exists.

    MUTATION: downgrade the `ScoreError` to a warning — this test fails
    because the call returns."""
    counted = _counted({"A": (5, 0), "B": (5, 0), "C": (5, 0)})
    scoring = {"A": [], "B": [{"run": "run-003", "refusal": "x"}], "C": []}
    runs = {"A": [{}] * 5, "B": [{}] * 4, "C": [{}] * 5}
    e2 = {arm: {"denominator": len(runs[arm])} for arm in runs}
    e4 = dict(e2)
    e4["B"] = {"denominator": 5}                  # counted the refusal in
    with pytest.raises(score.ScoreError, match="POPULATION-UNRECONCILED arm B"):
        score.reconciled_population(counted, scoring, runs, e2, e4)


# --- ROUND-2 R2-3: the family's complete report reaches the document ----------

def _report(name="A-C"):
    """A family report in `family_report()`'s published shape, small."""
    member = {"id": "M16", "level": "L2c", "engine": "excluded",
              "population": "ITT", "adjustment": None, "n": "38/37/39",
              "difference": 0.19197, "p": 0.0044, "rejects": True,
              "sigma": 0.29649, "mde": 0.1893, "interval": [0.05, 0.33]}
    return {
        "contrast": name,
        "estimand": {"outcomeWeighting": "native", "offsetWeighting": "native",
                     "universe": "single", "ruledBy": "round-2 R2-2"},
        "members": [member],
        "verdict": {"positive": 1, "rejecting": 1, "verdict": "CLAIM"},
        "dropAPole": [{"poleDropped": "L1", "membersLeft": 1, "positive": 1,
                       "rejecting": 1, "verdict": "CLAIM", "members": ["M16"]}],
        "offsets": {"excluded/ITT/native": {
            "value": -0.00554, "column": "excluded", "population": "ITT",
            "weighting": "native", "predicate": "kill-record",
            "registered": True, "tier": "registered"}},
        "alternatives": [{"label": "hybrid (outcome native / offset shared)",
                          "status": "SUPERSEDED", "tier": "D", "member": False,
                          "reason": "superseded", "outcomeWeighting": "native",
                          "offsetWeighting": "shared",
                          "verdict": {"positive": 1, "rejecting": 1,
                                      "verdict": "CLAIM"},
                          "members": [dict(member, difference=0.2323)]}],
        "refusedCells": [{"population": "ITT", "adjustment": "ANCOVA",
                          "reason": "covert change of population"}],
        "refusedCellTierD": {
            "composition": {"population": "complete-case",
                            "perArm": {"A": 30, "B": 31, "C": 32},
                            "droppedPerArm": {"A": 8, "B": 6, "C": 7}},
            "quantities": [{"level": "L2c", "engine": "excluded",
                            "adjustedDifference": 0.04}]},
        "corpus": {"sharedClasses": {"excluded": 29, "included": 33},
                   "nativeDenominators": {"excluded": {"jps": 60, "rego": 55},
                                          "included": {"jps": 69, "rego": 64}},
                   "sharedDenominators": {"excluded": {"jps": 29, "rego": 29},
                                          "included": {"jps": 33, "rego": 33}}},
    }


SECTION_MARKS = ("Reprint 2, drop-a-pole", "null offsets under every reading",
                 "Tier D alternative: hybrid", "refused cells",
                 "Tier D disclosure beside the refusal", "corpus denominators",
                 "Estimand (A-C): outcome weighting **native**")


def test_the_report_prints_the_complete_family_report_below_the_guard():
    """R2-3 (b): σ, MDE and the BCa interval on every reprint row, then the
    drop-a-pole table, the offsets with the registered one marked, the Tier D
    alternatives, the refused cell with its disclosure, and the corpus
    denominators — all of it, when no gate matched."""
    verdict = decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                               "controlGates": gates(),
                               "family": {"A-C": family(),
                                          "A-B": family(arms=("A", "B"))}})
    results = results_for(verdict, [], {"A-C": family()})
    results["familyReports"] = {"A-C": _report()}
    results["family"]["A-C"]["members"] = _report()["members"]
    body = score.results_markdown(results)
    for mark in SECTION_MARKS:
        assert mark in body, mark
    assert "| 0.2965 | 0.1893 | [0.0500, 0.3300] |" in body
    assert "| excluded/ITT/native | excluded | ITT | native | kill-record | " \
           "-0.0055 | **yes** |" in body
    assert "| 0.2323 |" in body                     # the superseded hybrid row


def test_nothing_of_the_family_report_prints_above_a_gating_row():
    """R2-3 (b) under R1-14: the sections are under the SAME guard as the
    reprint. A document that carries a report AND a gating cause prints the
    causes and none of the report.

    MUTATION: move `_family_report_markdown()` out of the `else:` — the
    marks appear."""
    outcome = {"pipelineProblems": [], "shortfallDeclared": [],
               "controlGates": gates(references_reproduce_gold=False),
               "family": {"A-C": family()}}
    causes = decision.gate_causes(outcome)
    assert causes
    results = results_for(decision.decide(outcome), causes, outcome["family"])
    results["familyReports"] = {"A-C": _report()}
    body = score.results_markdown(results)
    assert "Not computed and not published" in body
    for mark in SECTION_MARKS:
        assert mark not in body, mark
    assert "0.19197" not in body and "0.1920" not in body


def test_the_document_publishes_the_same_report_objects_the_decision_read():
    """R2-3 (a): `familyReports` in the document is the object
    `registered_family()` stored on the outcome — not a copy, not a
    recomputation — so the rows a reader sees and the rows the verdict was
    computed from are one evaluation."""
    report = _report()
    outcome = {"pipelineProblems": [], "familyReports": {"A-C": report}}
    # arm B: two attempted, one refused at scoring time — the document's
    # population must be the RECONCILED block (R2-1 STEP 7), not the raw
    # slot-side projection, which would print 2.
    document = score.results_document(
        attempt_root="/x/attempt-1", label="PILOT", unfilled=[],
        outcome=outcome, pins_raw_sha256="0" * 64,
        tools=type("T", (), {"record": staticmethod(lambda: {})})(),
        c4=None, shape={}, counted=_counted({"A": (1, 0), "B": (2, 0),
                                             "C": (1, 0)}),
        scoring_apparatus={"A": [], "B": [{"run": "run-002", "refusal": "x"}],
                           "C": []}, pairing=[],
        paired_ids={"jps": [], "rego": []}, mutants={"jps": [], "rego": []},
        denominators={},
        shared={}, e1={}, e2={a: {"denominator": 1} for a in "ABC"}, e3={},
        e4_by_arm={a: {"denominator": 1} for a in "ABC"}, e5=None,
        family={}, gate_causes=[], gates=gates(), refusals={},
        per_arm_runs={a: [{}] for a in "ABC"}, reviewer_set=None,
        verdict={"verdict": "x", "causes": [], "rowIndex": 6},
        interval_licence=False, suppression="fixture")
    assert document["familyReports"]["A-C"] is report
    assert document["population"]["A"]["denominator"] == 1
    assert document["population"]["B"]["denominator"] == 1
    assert document["population"]["B"]["scoringApparatusExcluded"] == 1
    assert document["population"]["B"]["preScoringDenominator"] == 2
    assert document["pipelineInvalid"] is False


def test_an_outcome_above_a_gating_row_carries_no_family_report():
    """The other side: `registered_family()` is never called above a gating
    row (R1-14), so `familyReports` is EMPTY there rather than absent or
    stale — `results_document()` reads it with a default."""
    outcome = {"pipelineProblems": ["row-1"]}
    document = score.results_document(
        attempt_root="/x/attempt-1", label="PILOT", unfilled=[],
        outcome=outcome, pins_raw_sha256="0" * 64,
        tools=type("T", (), {"record": staticmethod(lambda: {})})(),
        c4=None, shape={}, counted=_counted({"A": (1, 0), "B": (1, 0),
                                             "C": (1, 0)}),
        scoring_apparatus={"A": [], "B": [], "C": []}, pairing=[],
        paired_ids={"jps": [], "rego": []}, mutants={"jps": [], "rego": []},
        denominators={},
        shared={}, e1={}, e2={a: {"denominator": 1} for a in "ABC"}, e3={},
        e4_by_arm={a: {"denominator": 1} for a in "ABC"}, e5=None,
        family={}, gate_causes=["row-1"], gates=gates(), refusals={},
        per_arm_runs={a: [{}] for a in "ABC"}, reviewer_set=None,
        verdict={"verdict": "x", "causes": ["row-1"], "rowIndex": 1},
        interval_licence=False, suppression="row-1")
    assert document["familyReports"] == {}
    assert document["pipelineInvalid"] is True
