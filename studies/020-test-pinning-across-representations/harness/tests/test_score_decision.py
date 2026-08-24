"""§5.9's ordered decision rule, driven through EVERY row.

Study 018's round-8 finding 1 was a decision rule whose code and whose
registration disagreed about which cells adjudicate, and an if-ladder gave
nothing to enumerate. This module enumerates: a synthetic outcome is built for
each registered row, driven through `decide()`, and the row it lands on is
asserted to be the row the registration names — plus the ordering assertions
that say WHY the rows are in this order.

REBUILT FOR §7 DELTAS 2 AND 5. 019's substantive row read one binomial
contrast's zero-exclusion over a high-kill run count derived from tau = 0.95;
§5.1 registers "**No cut, no τ, no dichotomy**" and §5.9 row 4 reads the
eighteen-member family's two unanimities instead. The `e1-floor` row is gone
(§5.7, M-23 option (a)), the last row's verdict is
INDETERMINATE-BY-DISAGREEMENT, and C4's two-sided transfer outcome (§2a.5)
splits across rows 1 and 3. Every one of those is asserted below against the
registration's own bytes.

The registration's own text is read out of `PREREGISTRATION.md`'s bytes, not out
of a copy of it (Study 012's round-12 lesson: a test module that was a copy
checking a copy stayed green through a registration-only edit).
"""
import re

import pytest

from e4lib import decision


def gates(**overrides):
    state = {name: {"held": True} for name in decision.CONTROL_GATES}
    for name, held in overrides.items():
        state[name.replace("_", "-")] = {"held": held}
    return state


def family(claim=True, sign="+", arms=("A", "C"), members=None):
    """A synthetic family verdict in the shape §7 delta 5's `e4lib/family.py`
    produces: eighteen members, a common sign and the two unanimities.

    Eighteen is not decoration here. §5.2 makes membership append-only after
    registration precisely because §5.4's intersection-union logic makes a
    SMALLER family the anti-conservative direction, and `decide()` refuses a
    short one — so a fixture that produced seventeen would be testing a rule the
    registration does not have."""
    if members is None:
        # R1-8 moved this fixture onto the PRODUCTION shape: `family.verdict()`
        # publishes `members` as the registered ID STRINGS and a closed
        # `verdict` token, and `decision._family_claims()` now validates both,
        # so a fixture of eighteen ad-hoc dicts would be testing a laxer
        # contract than the one production meets.
        members = ["M%d" % (index + 1)
                   for index in range(decision.REGISTERED_FAMILY_SIZE)]
    return {"contrast": "%s-%s" % arms, "arms": list(arms), "members": members,
            "signUnanimous": claim, "allReject": claim, "sign": sign,
            "claim": claim,
            "verdict": "CLAIM" if claim else "INDETERMINATE-BY-DISAGREEMENT"}


# --- one case per registered row, in registered order -----------------------

def test_row_1_pipeline_invalid():
    verdict = decision.decide({"pipelineProblems": ["the pin registry is unreadable"],
                               "controlGates": gates(),
                               "family": {"A-C": family()}})
    assert verdict["row"] == "pipeline-invalid"
    assert verdict["rowIndex"] == 1
    assert verdict["verdict"] == "R1 inconclusive - pipeline-invalid"


def test_row_1_carries_c4s_pipeline_invalid_outcome(preregistration):
    """§2a.5's transfer gate is TWO-SIDED and the two sides land on different
    rows: "if any exact-equality row differs, the BATCH is suspect" is
    `pipeline-invalid` and reaches row 1; "if every exact-equality row holds and
    only band rows differ, the PILOT is suspect" is `calibration-invalid` and
    reaches row 3. One observable, two rows, because the two outcomes say
    different things about which artifact is wrong."""
    verdict = decision.decide({
        "pipelineProblems": ["C4 transfer gate: sandbox policy differs between "
                             "the pilot and the batch (pipeline-invalid)"],
        "controlGates": gates(), "family": {"A-C": family()}})
    assert verdict["row"] == "pipeline-invalid"
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert "or C4's pipeline-invalid outcome (§2a.5) → R1 inconclusive" in flat


def test_row_2_shortfall_declared_is_unresolved_by_design():
    """019's round-1 R1-7, carried. A declared short batch is DECLARED rather
    than scored, above every substantive row and above the gates: §5.9 row 2
    registers "no endpoint, no rate and no contrast is computed", and the scorer
    used to compute ordinary endpoints and contrasts over the prefix anyway."""
    verdict = decision.decide({
        "pipelineProblems": [],
        "shortfallDeclared": ["87 of 150 registered slots, declared: power cut"],
        "controlGates": gates(golden_context=False),
        "family": {"A-C": family()}})
    assert verdict["row"] == "shortfall-declared"
    assert verdict["rowIndex"] == 2
    assert verdict["verdict"] == \
        "UNRESOLVED-BY-DESIGN - the batch was declared short"


def test_row_3_control_gate_failed():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(golden_context=False),
                               "family": {"A-C": family()}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["rowIndex"] == 3
    assert verdict["causes"] == ["golden-context"]


def test_row_4_claims_only_on_both_unanimities():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(),
                               "family": {"A-C": family(),
                                          "A-B": family(arms=("A", "B"))}})
    assert verdict["row"] == "claim"
    assert verdict["rowIndex"] == 4
    assert verdict["verdict"] == "R1 = CLAIM - A above C"


def test_row_5_indeterminate_by_disagreement_is_the_last_row():
    verdict = decision.decide({"pipelineProblems": [],
                               "controlGates": gates(),
                               "family": {"A-C": family(claim=False)}})
    assert verdict["row"] == "indeterminate-by-disagreement"
    assert verdict["rowIndex"] == len(decision.ROWS)
    assert verdict["verdict"] == "INDETERMINATE-BY-DISAGREEMENT"


def test_sign_unanimity_alone_does_not_claim_and_neither_does_rejection_alone():
    """§5.9 row 4 registers a CONJUNCTION: "all eighteen agree in the sign …
    **and** all eighteen reject". §5.5's reprint 1 is the case that matters —
    on 019's batch A−B was unanimous in direction (18 positive) and only 8 of 18
    rejected, and A−C had 16 positive with 10 rejecting. Neither is a claim."""
    for signs, rejects in ((True, False), (False, True)):
        verdict = decision.decide({
            "pipelineProblems": [], "controlGates": gates(),
            "family": {"A-C": dict(family(claim=False),
                                   signUnanimous=signs, allReject=rejects,
                                   claim=False)}})
        assert verdict["row"] == "indeterminate-by-disagreement", (signs,
                                                                   rejects)


def test_eighteen_arbitrary_strings_do_not_adjudicate():
    """R1-8: the decision layer validates the EXACT registered id set and the
    closed verdict vocabulary independently of the scorer. Eighteen made-up
    names with a truthy claim used to pass."""
    forged = family()
    forged["members"] = ["X%d" % index for index in range(18)]
    with pytest.raises(decision.DecisionError,
                       match="NOT-THE-REGISTERED-SET"):
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": forged}})
    vocab = family()
    vocab["verdict"] = "TOTALLY-CONFIRMED"
    with pytest.raises(decision.DecisionError,
                       match="VERDICT-VOCABULARY"):
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": vocab}})
    torn = family()
    torn["claim"] = False
    with pytest.raises(decision.DecisionError, match="FAMILY-INCONSISTENT"):
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": torn}})


def test_a_short_family_is_refused_rather_than_adjudicated():
    """§5.2: membership is append-only after registration and "may never
    remove one", because under §5.4's intersection-union logic REMOVING a
    member is the anti-conservative direction — a seventeen-member family makes
    the claim EASIER. A verdict that arrives short is refused."""
    short = family()
    short["members"] = short["members"][:-1]
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": short}})
    assert str(raised.value).startswith("DECISION-FAMILY-SHRANK")
    assert "anti-conservative" in str(raised.value)


def test_every_row_is_reachable():
    """Exhaustive means every row matches something; ordered means no row is
    unreachable behind an earlier one that always fires."""
    reached = {
        decision.decide({"pipelineProblems": ["x"]})["row"],
        decision.decide({"pipelineProblems": [],
                         "controlGates": gates(golden_context=False)})["row"],
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": family(),
                                    "A-B": family(arms=("A", "B"))}})["row"],
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": family(claim=False)}})["row"],
        decision.decide({"shortfallDeclared": ["short"]})["row"],
    }
    assert reached == {row.name for row in decision.ROWS}


# --- the ordering, and what each ordering buys ------------------------------

def test_a_pipeline_failure_outranks_a_claiming_family():
    """A pipeline-invalid attempt has no population, so eighteen members
    computed over it are arithmetic on a set nobody can vouch for."""
    verdict = decision.decide({"pipelineProblems": ["terminality"],
                               "controlGates": gates(),
                               "family": {"A-C": family()}})
    assert verdict["row"] == "pipeline-invalid"


def test_a_control_gate_failure_outranks_a_claiming_family():
    """§5.9 row 3 adjudicates R1 "in neither direction". Reading the family
    first and then discarding it publishes a direction the registration says is
    not licensed."""
    verdict = decision.decide({
        "pipelineProblems": [],
        "controlGates": gates(capabilities_canary_refused=False),
        "family": {"A-C": family()}})
    assert verdict["row"] == "control-gate-failed"
    assert "capabilities-canary-refused" in verdict["causes"]


def test_an_unevaluated_gate_fails_rather_than_passing_quietly():
    """Study 012's round 9 found all 150 calls reachable with the isolation
    assent still null. §6: "A gate the scorer did not evaluate fails: an absent
    gate is not a gate that held."""
    partial = gates()
    del partial["golden-context"]
    verdict = decision.decide({"pipelineProblems": [], "controlGates": partial,
                               "family": {"A-C": family()}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["causes"] == ["golden-context (not evaluated)"]


def test_no_control_gates_at_all_fails_every_gate():
    verdict = decision.decide({"pipelineProblems": []})
    assert verdict["row"] == "control-gate-failed"
    assert len(verdict["causes"]) == len(decision.CONTROL_GATES)


def test_the_engine_execution_gate_is_a_registered_control_row():
    """019's round-1 R1-8 at the decision layer, and §6 extends it: a pinned
    engine that refused on a frozen artifact adjudicates R1 in NEITHER
    direction, and for 020 the gate "now covers E6's extra invocation too"."""
    assert "engine-execution-clean" in decision.CONTROL_GATES
    verdict = decision.decide({
        "pipelineProblems": [],
        "controlGates": gates(engine_execution_clean=False),
        "family": {"A-C": family()}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["causes"] == ["engine-execution-clean"]


def test_c4s_calibration_invalid_outcome_is_a_control_gate_row():
    """§2a.5's other side: every exact-equality row holds and only band rows
    differ, so the PILOT is suspect and a re-pilot under C5 is required. That
    adjudicates R1 in neither direction and is row 3, not row 1."""
    assert "c4-transfer-calibration" in decision.CONTROL_GATES
    verdict = decision.decide({
        "pipelineProblems": [],
        "controlGates": gates(**{"c4_transfer_calibration": False}),
        "family": {"A-C": family()}})
    assert verdict["row"] == "control-gate-failed"
    assert verdict["causes"] == ["c4-transfer-calibration"]


def test_there_is_no_e1_floor_row(preregistration):
    """§5.7, ruled 2026-08-23 (M-23, option (a)), and §5.9 row 3 in its own
    bytes: "There is no `e1-floor` row".

    019 adjudicated its attempt on this gate. The gate is a max statistic — it
    fires iff NO admitted run clears, so P(fire) = (1 − p)ⁿ and its stringency
    runs the wrong way in n, which differs by arm — and §5.7 derives both the
    1.3–6.1 % spurious refusal at 019-scale N and the ~2,926 degraded runs
    certification would need. An uncertified gate is not registered as if
    certified, so it is not a member here and cannot be silently satisfied."""
    assert "e1-floor" not in decision.CONTROL_GATES
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert "There is no e1-floor row (§5.7)" in flat
    assert "No author-side control gate" in flat


# --- 019's R1-14: nothing inferential below a gating row --------------------

def test_gate_causes_is_empty_exactly_when_the_family_may_be_evaluated():
    """The predicate `harness/score.py` asks before it computes anything
    inferential, derived from the table rather than written out."""
    clean = {"pipelineProblems": [], "shortfallDeclared": [],
             "controlGates": gates()}
    assert decision.gate_causes(clean) == []
    for outcome in ({"pipelineProblems": ["x"], "controlGates": gates()},
                    {"pipelineProblems": [], "shortfallDeclared": ["short"],
                     "controlGates": gates()},
                    {"pipelineProblems": [],
                     "controlGates": gates(golden_context=False)}):
        assert decision.gate_causes(outcome), outcome


def test_every_gating_row_is_a_row_of_the_table_and_precedes_every_other():
    assert decision.GATING_ROWS == decision.ROWS[:len(decision.GATING_ROWS)]
    assert decision.ROW_CLAIM not in decision.GATING_ROWS


def test_the_last_row_refuses_when_no_primary_family_was_ever_evaluated():
    """019's round-1 R1-14, second scenario, under the new last row: §5.9's
    INDETERMINATE-BY-DISAGREEMENT is the statement that eighteen members
    disagreed, and eighteen members that were never computed did not
    disagree."""
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "shortfallDeclared": [],
                         "controlGates": gates(), "family": {}})
    assert str(raised.value).startswith("DECISION-NO-PRIMARY-FAMILY")


# --- direction, and the fixed sequence --------------------------------------

def test_direction_is_the_common_sign_and_only_of_a_claiming_family():
    """§5.9 row 4: "direction the common sign". A verdict that does not claim
    has no common sign to report, and reporting one would publish a direction
    the last row says is not licensed."""
    assert decision.direction(family(sign="+")) == "A above C"
    assert decision.direction(family(sign="-")) == "C above A"
    assert decision.direction(family(claim=False)) == \
        "none - INDETERMINATE-BY-DISAGREEMENT"


def test_direction_refuses_a_claiming_family_with_no_common_sign():
    broken = family()
    broken["sign"] = None
    with pytest.raises(decision.DecisionError) as raised:
        decision.direction(broken)
    assert str(raised.value).startswith("DECISION-DIRECTION-UNREADABLE")


def test_direction_refuses_a_verdict_that_names_no_ordered_pair_of_arms():
    """"A above C" is a statement about an ordered pair, and 019's round-1 R1-13
    is why it is read off a named pair rather than reconstructed: comparing raw
    counts agrees with the rate comparison only at equal denominators, and §1a
    makes unequal denominators the expected case."""
    broken = family()
    broken["arms"] = ["A"]
    with pytest.raises(decision.DecisionError) as raised:
        decision.direction(broken)
    assert str(raised.value).startswith("DECISION-DIRECTION-UNREADABLE")


def test_direction_is_reported_as_observed_in_both_directions():
    secondary = family(arms=("A", "B"))
    above = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "family": {"A-C": family(sign="+"),
                                        "A-B": secondary}})
    below = decision.decide({"pipelineProblems": [], "controlGates": gates(),
                             "family": {"A-C": family(sign="-"),
                                        "A-B": secondary}})
    assert above["verdict"] == "R1 = CLAIM - A above C"
    assert below["verdict"] == "R1 = CLAIM - C above A"


def test_the_secondary_family_is_evaluated_only_because_the_primary_claimed():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "family": {"A-C": family(sign="-"),
                   "A-B": family(sign="-", arms=("A", "B"))}})
    assert verdict["secondary"]["contrast"] == "A-B"
    assert verdict["secondary"]["result"] == "B above A"
    assert "fixed-sequence gatekeeping" in verdict["secondary"]["testedBecause"]
    assert "spends no" in verdict["secondary"]["testedBecause"]


def test_an_indeterminate_primary_never_reports_a_secondary():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "family": {"A-C": family(claim=False),
                   "A-B": family(arms=("A", "B"))}})
    assert verdict["row"] == "indeterminate-by-disagreement"
    assert "secondary" not in verdict


def test_a_claiming_primary_with_no_secondary_computed_says_WHY():
    """019's round-3 finding R3-8, carried unchanged in force.

    It used to accept a bare `result: null` for an absent secondary, which is
    what let the scorer publish one: a refusal on A−B cleared the whole set, and
    the claiming row would have carried a null beside it that reads as "not
    decided" and is indistinguishable from "never computed". Once the primary
    claims, §5.9's sequence has REACHED the secondary, so it has a result or it
    has a cause."""
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "family": {"A-C": family()},
        "secondaryRefusal": "FM-EMPTY-ARM arm B has 0 admitted runs"})
    assert verdict["row"] == "claim"
    assert verdict["secondary"]["result"] is None
    assert verdict["secondary"]["refusal"].startswith("FM-EMPTY-ARM")


def test_a_claiming_primary_with_a_silently_absent_secondary_refuses():
    """The other half of the same rule: no cause, no verdict."""
    with pytest.raises(decision.DecisionError) as raised:
        decision.decide({"pipelineProblems": [], "controlGates": gates(),
                         "family": {"A-C": family()}})
    assert str(raised.value).startswith("DECISION-SECONDARY-UNEXPLAINED")


def test_a_computed_secondary_carries_no_refusal():
    verdict = decision.decide({
        "pipelineProblems": [], "controlGates": gates(),
        "family": {"A-C": family(), "A-B": family(arms=("A", "B"))},
        "secondaryRefusal": "this must not be read when the secondary exists"})
    assert verdict["secondary"]["result"] == "A above B"
    assert verdict["secondary"]["refusal"] is None


# --- the table against the registration's own bytes -------------------------

SECTION = re.compile(r"\n### 5\.9 Ordered, exhaustive decision rule.*?"
                     r"(?=\n## )", re.DOTALL)


def test_the_table_has_one_row_per_registered_numbered_row(preregistration):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, "§5 holds %d ordered decision rules" % len(found)
    numbered = re.findall(r"^\d+\. ", found[0], re.MULTILINE)
    # The assertion is exact in both directions: a row added to the table
    # without a numbered row in §5.9 fails here, and so does a numbered row in
    # §5.9 with no row behind it.
    assert len(numbered) == len(decision.ROWS)
    assert decision.ROWS[1] is decision.ROW_SHORTFALL_DECLARED
    flat = " ".join(found[0].replace("*", "").replace("`", "").split())
    assert ("A validated shortfall declaration (§1a) → UNRESOLVED-BY-DESIGN — "
            "no endpoint, no rate and no contrast is computed" in flat)


def test_every_registered_control_gate_is_named_in_the_registration(
        preregistration):
    """019's R1-8 prose half, carried and extended. The mapping is from the
    code's own tuple, so a gate added later without a prose edit fails here
    rather than at the attempt — and a gate REMOVED from the registration
    (`e1-floor`, §5.7) fails here too if it is left in the code."""
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    registered_in_prose = {
        "references-reproduce-gold":
            "both references reproduce gold imperfectly at attempt time",
        "capabilities-canary-refused": "the capabilities canary passes",
        "golden-context": "golden-context gate",
        "timeout-rate-within-cap": "per-arm timeout rate above cap",
        "engine-execution-clean": "engine-execution-clean",
        "c4-transfer-calibration": "C4's calibration-invalid outcome",
    }
    assert set(registered_in_prose) == set(decision.CONTROL_GATES)
    for gate, phrase in registered_in_prose.items():
        assert phrase in flat, "§5.9 row 3 does not name the gate %s" % gate
    assert "every scored engine invocation of the attempt returned an answer" \
        in flat
    assert "A gate the scorer did not evaluate fails" in flat


def test_the_registration_forbids_computing_a_contrast_above_the_gates(
        preregistration):
    """019's R1-14 prose half, and it is the ORDER that is registered: the
    scorer may not compute an inferential quantity at or above the gate rows,
    because "adjudicates R1 in neither direction" is not satisfied by computing
    a direction and then declining to act on it."""
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert ("No inferential quantity is computed, let alone published, at or "
            "above row 3" in flat)
    assert ("An absent primary contrast is not a disagreeing one and never "
            "reaches row 5" in flat)
    assert decision.REGISTERED_MINIMUM_DENOMINATOR >= 1
    assert "Each member's per-arm denominator must be positive" in flat


def test_the_last_registered_row_is_the_one_that_always_matches(preregistration):
    assert "last row always matches" in preregistration
    assert decision.ROWS[-1] is decision.ROW_INDETERMINATE
    assert decision.ROW_INDETERMINATE.predicate({}) == ["indeterminate"]


def test_the_last_row_licenses_nothing_and_triggers_nothing(preregistration):
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert ("Otherwise → INDETERMINATE-BY-DISAGREEMENT. No claim in any "
            "direction is licensed, and this row triggers nothing" in flat)
    assert decision.ROW_INDETERMINATE.verdict == "INDETERMINATE-BY-DISAGREEMENT"


def test_the_registered_alpha_and_family_size_are_the_registrations(
        preregistration):
    """§5.4 point 4: "α = 0.05 per member, two-sided, no correction". §5.2: the
    family is the crossing of three axes and has eighteen members. Both are read
    out of the registration rather than out of a comment."""
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert "α = 0.05 per member, two-sided, no correction" in flat
    assert "The registered sensitivity family — eighteen members" in flat
    assert decision.REGISTERED_ALPHA == 0.05
    assert decision.REGISTERED_FAMILY_SIZE == 18
    assert ("All eighteen family members agree in the sign of the A−C "
            "difference and all eighteen reject at two-sided α = 0.05" in flat)


def test_the_registered_contrast_order_is_a_c_then_a_b(preregistration):
    """The registration wraps its lines, so the prose is flattened before it is
    read — the same treatment `tests/test_partition.py` gives §1a."""
    flat = " ".join(preregistration.replace("*", "").replace("`", "").split())
    assert "The fixed sequence A−C → A−B spends no α" in flat
    assert "then A−B under the identical rule" in flat
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
