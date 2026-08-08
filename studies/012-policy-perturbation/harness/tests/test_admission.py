#!/usr/bin/env python3
"""§6 C4's registered fixtures, end to end through the real scorer.

Every fixture below is a slot in a PREFIX of §2.8's registered call order, built
by `fixtures.build_slot()`, sealed by `batch.seal_slot()` and recorded by
`batch.ledger_record()` — the driver's own machinery, so a manifest or a chain
the two modules read differently fails here rather than agreeing with itself —
and then scored by `score_rates.check_population()`, `session_reuse()`,
`verify_seal()`, `score_run()`, `score_arm()` and `compute_verdicts()`, in
`score()`'s own order.

`registered_fixtures()` builds the list C4 names, one entry per slot, each
carrying its expected outcome in the same committed module as the fixture (and
`EXPECTED_CODES` restates the whole map; a test requires the two to agree):

  1. arm B's prompt bytes inside arm A's tree            -> `arm-mismatch`
  2. `arm` stamp and `armPromptSha256` disagree          -> `arm-mismatch`
  3. one admissible slot per arm, all five prompt digests
  4. a same-arm slot copied to another index in its arm  -> `schedule-mismatch`
     (and the ledger-slot bijection refuses the whole scoring)
  5. a recorded (globalIndex, round, position, arm) that
     is not the registered order's                       -> `schedule-mismatch`
  6. two slots sharing session bytes                     -> `session-reused`
  7. a `SLOT-MANIFEST.json` that disagrees with its bytes -> the WHOLE scoring
     UNRESOLVED-BY-DESIGN with no contrast, and the altered slot still in `V_X`
  8. a synthetic population at known integers exercising every row of §5.3's
     decision table (`test_the_decision_table_rows_all_fire_at_known_integers`)

together with C4's earlier list — one element per drop code, a class reached
only by a mislabelled record, a class reached by no record, an `authoring-empty`
and a `pipeline-invalid` run at known `k` and `n`, a synthetic arm at (45, 72)
reproducing the six classes at the shifted edges, and a synthetic arm covering
the new-keyed classes and not the old-keyed ones (S10 at a known answer).

Two round-4 dispositions land here:

  * **finding 6** — §5.3 (ii)'s arm-D scenarios drive the REGISTERED condition
    for `COVERAGE-FOLLOWS-THE-NUMBERS` (new-keyed HIGH on at least three of the
    four narrow numeric classes, old-keyed not HIGH-patterned), including the
    two cases that condition and the code's earlier all-six-TRACKING rule
    disagree about;
  * **finding 9** — `coveredNothing` is the empty covered-class set, and the two
    runs the finding names are built and scored: a correctly labelled record
    outside all six predicates, and an all-Q class-reaching run.

Nothing here touches the committed tree, reaches a network or runs a CLI.
"""
from __future__ import annotations
import ast
import os
import shutil

import pytest

import batch
import fixtures
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))


# --- C4's fifteen registered slots, and what each one must score -------------

def registered_fixtures(population) -> list:
    """Three rounds of §2.8's registered call order — global indices 1…15, five
    arms interleaved exactly as the batch interleaves them — with one C4
    fixture per slot and its expected outcome beside it.

    A function rather than a constant because three of the fixtures name paths
    inside the throwaway root: the shared scratch and home two slots must
    record to share a call's evidence (fixture 6), and the source of the
    same-arm copy (fixture 4, in its own population below).
    """
    shared_cwd = os.path.join(population.root, "shared-scratch")
    shared_home = os.path.join(population.root, "shared-home")
    partial = fixtures.completion(fixtures.partial_records(
        *fixtures.arm_pair(population.arms_root, "E")))
    drops = fixtures.completion(fixtures.drop_records())
    return [
        # g1  B/run-001 — an honest slot, and the one the golden is taken from.
        {"why": "honest arm B run", "expect": None, "spec": {}},
        # g2  C/run-001 — honest, and the EARLIER of the two slots that share a
        # call's evidence: it keeps its place in the denominator (fixture 6).
        {"why": "the earlier of the two slots sharing session bytes",
         "expect": None,
         "spec": {"cwd": shared_cwd, "home": shared_home,
                  "session_id": fixtures.SESSION_ID % 999}},
        # g3  A/run-001 — C4 fixture 1: arm B's prompt bytes inside arm A's
        # tree. The stamps are honest (arm A, A's prompt digest); the BYTES are
        # another arm's, which is what §3.1 gate 2 and §3.3 call `arm-mismatch`
        # rather than `transcript-refused` or `context-mismatch`.
        {"why": "C4 fixture 1: arm B's prompt bytes in arm A's tree",
         "expect": "arm-mismatch", "spec": {"prompt_arm": "B"}},
        # g4  D/run-001 — the (45, 72) arm, whose records reproduce the same six
        # classes at the shifted edges.
        {"why": "arm D at (45, 72): the six classes at the shifted edges",
         "expect": None, "spec": {}},
        # g5  E/run-001 — C4 fixture 5: the recorded (globalIndex, round,
        # position, arm) is not what §2.8 assigns to this slot.
        {"why": "C4 fixture 5: a recorded schedule position that is not the "
                "registered one",
         "expect": "schedule-mismatch",
         "spec": {"call": {"globalIndex": 55, "round": 11, "position": 5}}},
        # g6  D/run-002 — §3.3's authoring-empty run: admissible evidence, no
        # parseable array. VALID, in every denominator, covering nothing.
        {"why": "authoring-empty: valid, counted, covering nothing",
         "expect": None, "spec": {"answer": fixtures.COMPLETION_EMPTY}},
        # g7  E/run-002 — a pipeline-invalid run at a known k and n.
        {"why": "pipeline-invalid: the wrapper's own non-zero exit",
         "expect": "call-nonzero-exit",
         "spec": {"exit_status": 3, "completion_file": False}},
        # g8  C/run-002 — C4 fixture 6: the LATER of the two slots sharing a
        # call's evidence. Same session bytes, same session id, same recorded
        # working directory and isolated home as g2.
        {"why": "C4 fixture 6: the later slot sharing session bytes",
         "expect": "session-reused",
         "spec": {"cwd": shared_cwd, "home": shared_home,
                  "session_id": fixtures.SESSION_ID % 999}},
        # g9  A/run-002 — C4 fixture 2: the `arm` stamp says A and the
        # `armPromptSha256` is arm B's, so the run does not say which policy
        # text it was made with.
        {"why": "C4 fixture 2: the arm stamp and the arm-prompt digest disagree",
         "expect": "arm-mismatch",
         "spec": {"call": {"armPromptSha256": fixtures.file_digest(
             fixtures.arm_prompt_path(population.arms_root, "B"))}}},
        # g10 B/run-002 — one element per drop code, in the compiler's own
        # check order. Valid: dropping records is an authoring outcome.
        {"why": "one element per drop code", "expect": None,
         "spec": {"answer": drops}},
        # g11 E/run-003 — the mislabel fixture: class 2 is reached ONLY by a
        # mislabelled record and classes 0 and 5 are reached by no record.
        {"why": "a class reached only by a mislabelled record, and two classes "
                "reached by none",
         "expect": None, "spec": {"answer": partial}},
        # g12…g15 — the rest of round 3, honest, so every arm holds at least one
        # admissible slot and all five registered prompt digests meet the
        # arm-keyed terminal-prompt gate (C4 fixture 3).
        {"why": "honest arm D run", "expect": None, "spec": {}},
        {"why": "honest arm A run", "expect": None, "spec": {}},
        {"why": "honest arm C run", "expect": None, "spec": {}},
        {"why": "honest arm B run", "expect": None, "spec": {}},
    ]


# The verdict every one of the fifteen slots must receive, keyed by (arm, slot)
# so the expectation is readable without counting global indices. Registered
# here, in the same committed module as the fixtures (§6 C4).
EXPECTED_CODES = {
    ("A", "run-001"): "arm-mismatch",        # fixture 1
    ("A", "run-002"): "arm-mismatch",        # fixture 2
    ("A", "run-003"): None,
    ("B", "run-001"): None,
    ("B", "run-002"): None,                  # the drop-code completion
    ("B", "run-003"): None,
    ("C", "run-001"): None,
    ("C", "run-002"): "session-reused",      # fixture 6
    ("C", "run-003"): None,
    ("D", "run-001"): None,                  # (45, 72)
    ("D", "run-002"): None,                  # authoring-empty
    ("D", "run-003"): None,
    ("E", "run-001"): "schedule-mismatch",   # fixture 5
    ("E", "run-002"): "call-nonzero-exit",
    ("E", "run-003"): None,                  # the mislabel completion
}

# Each arm's population arithmetic over the fifteen slots, at the registered
# N = 30 — intent-to-treat, so an invalid slot stays in the denominator and
# covers nothing (§4.2 [D-24]).
EXPECTED_POPULATION = {
    "A": {"scheduled": 3, "valid": 1, "invalid": 2, "authoringEmpty": 0},
    "B": {"scheduled": 3, "valid": 3, "invalid": 0, "authoringEmpty": 0},
    "C": {"scheduled": 3, "valid": 2, "invalid": 1, "authoringEmpty": 0},
    "D": {"scheduled": 3, "valid": 3, "invalid": 0, "authoringEmpty": 1},
    "E": {"scheduled": 3, "valid": 1, "invalid": 2, "authoringEmpty": 0},
}
# Per-class k on the PRIMARY endpoint (correctly-labelled coverage), per arm.
EXPECTED_PRIMARY_K = {
    "A": [1, 1, 1, 1, 1, 1],
    "B": [2, 2, 2, 2, 2, 2],
    "C": [2, 2, 2, 2, 2, 2],
    "D": [2, 2, 2, 2, 2, 2],
    "E": [0, 1, 0, 1, 1, 0],          # the partial completion alone
}
# S1's raw placement k: `H(r) ⊆ A(r)`, so this is never below the primary, and
# arm E's class 2 is where they come apart — a record placed inside the class
# with the wrong label.
EXPECTED_PLACEMENT_K = {
    "A": [1, 1, 1, 1, 1, 1],
    "B": [2, 2, 2, 2, 2, 2],
    "C": [2, 2, 2, 2, 2, 2],
    "D": [2, 2, 2, 2, 2, 2],
    "E": [0, 1, 1, 1, 1, 0],
}
# S10's old-edge cross-scoring: every arm but D is keyed at (40, 70) already, so
# its old-edge k is its own; arm D's records sit at 45 and 72 and reach NONE of
# arm A's four narrow numeric classes. Class 3 is A's 30-wide [40, 70) band,
# which D's 45 and 60 fall inside, and class 4 names no number at all.
EXPECTED_OLD_EDGE_K = {
    "A": [1, 1, 1, 1, 1, 1],
    "B": [2, 2, 2, 2, 2, 2],
    "C": [2, 2, 2, 2, 2, 2],
    "D": [0, 0, 0, 2, 2, 0],
    "E": [0, 1, 0, 1, 1, 0],
}
# §4.5's census over each arm's VALID runs: the records it saw and the distinct
# probes per class over the H records (X1).
EXPECTED_CENSUS = {
    "A": {"runs": 1, "records": 7, "h": 7, "q": 0,
          "probes": [1, 2, 1, 2, 1, 1]},
    "B": {"runs": 3, "records": 15, "h": 15, "q": 0,
          "probes": [1, 2, 1, 2, 1, 1]},
    "C": {"runs": 2, "records": 14, "h": 14, "q": 0,
          "probes": [1, 2, 1, 2, 1, 1]},
    "D": {"runs": 3, "records": 14, "h": 14, "q": 0,
          "probes": [1, 2, 1, 2, 1, 1]},
    "E": {"runs": 1, "records": 5, "h": 4, "q": 1,
          "probes": [0, 1, 0, 1, 1, 0]},
}


@pytest.fixture(scope="module")
def scored(pins, study):
    """C4's fifteen slots, built once and scored once.

    Once, because §4.3's exact interval is 200 halvings in rationals and a
    scoring computes about 220 of them; the fixtures that need no rate use
    `score_runs()` and pay none of it.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = registered_fixtures(population)
        population.build([entry["spec"] for entry in specs])
        yield population, specs, population.score()
    finally:
        shutil.rmtree(root, True)


# --- C4 fixtures 1, 2, 5, 6, and the codes the rest of the list must produce --

def test_every_registered_fixture_scores_its_registered_outcome(scored):
    """The whole fifteen-slot verdict map at once, so a fixture that stopped
    being the fixture it was registered as cannot hide behind a test that only
    looks at the slot it cares about."""
    population, specs, results = scored
    # The outcome registered BESIDE each fixture and the keyed table above are
    # one registration: a plan that drifted from the table would otherwise be
    # two expectations, and the reader would have no way to tell which is the
    # registered one.
    beside_the_fixture = {(entry["arm"], "run-%03d" % entry["slotIndex"]):
                          spec["expect"]
                          for entry, spec in zip(population.entries, specs)}
    assert beside_the_fixture == EXPECTED_CODES
    assert len(specs) == len(EXPECTED_CODES) == 15
    got = {key: row["code"] for key, row in results["byKey"].items()}
    assert got == EXPECTED_CODES


def test_another_arms_prompt_bytes_are_arm_mismatch_and_nothing_else(scored):
    """C4 fixture 1, stated as the three codes it must NOT be.

    The stamps are honest here: the CALL.json names arm A and carries arm A's
    prompt digest, so the stamp checks pass and the bytes are what refuse. A
    scorer that reported `transcript-refused` would name the cause the evidence
    does not establish, and one that reported `context-mismatch` would name a
    retained-context defect that is not there.
    """
    _population, _specs, results = scored
    row = results["byKey"][("A", "run-001")]
    assert row["code"] == "arm-mismatch"
    assert row["code"] not in ("context-mismatch", "transcript-refused")
    assert "arm B's registered prompt bytes" in row["detail"]
    assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"


def test_a_disagreeing_arm_stamp_and_prompt_digest_are_arm_mismatch(scored):
    """C4 fixture 2: the two halves of the arm stamp must agree with each
    other, or the run does not say which policy text it was made with."""
    _population, _specs, results = scored
    row = results["byKey"][("A", "run-002")]
    assert row["code"] == "arm-mismatch"
    assert "the arm stamp and the prompt digest disagree" in row["detail"]


def test_a_slot_out_of_the_registered_order_is_schedule_mismatch(scored):
    """C4 fixture 5. The arm is right and the prompt digest is right —
    `arm-mismatch` cannot see this — and §2.8's order is what does."""
    _population, _specs, results = scored
    row = results["byKey"][("E", "run-001")]
    assert row["code"] == "schedule-mismatch"
    assert "registered call order assigns" in row["detail"]


def test_two_slots_sharing_session_bytes_lose_the_LATER_one(scored):
    """C4 fixture 6, including which of the two leaves the denominator: the
    later one on the REGISTERED SCHEDULE, not the later one in a directory
    listing (§3.3)."""
    _population, _specs, results = scored
    earlier = results["byKey"][("C", "run-001")]
    later = results["byKey"][("C", "run-002")]
    assert earlier["code"] is None and earlier["valid"]
    assert later["code"] == "session-reused"
    assert "share the retained transcript bytes" in later["detail"]
    assert earlier["globalIndex"] < later["globalIndex"]


def test_every_arm_has_an_admissible_slot_at_its_own_prompt_digest(scored):
    """C4 fixture 3: the arm-keyed terminal-prompt gate is exercised at ALL
    FIVE registered prompt digests, before the batch rather than on slot 1.

    011 could note that its one registered prompt first met the ported gate on
    batch slot 1; with five prompts under an interleaved order, an off-by-one
    in the driver's arm sequence would place slots in the wrong tree silently.
    """
    population, _specs, results = scored
    admitted = {}
    for (arm, slot), row in results["byKey"].items():
        if row["valid"]:
            admitted.setdefault(arm, []).append(slot)
    assert sorted(admitted) == list(fixtures.ARMS)
    digests = set()
    for arm, slots in admitted.items():
        for slot in slots:
            call = score_rates.load_json(os.path.join(
                population.arms_root, arm, "authoring", slot, "CALL.json"))
            assert call["arm"] == arm
            digests.add(call["armPromptSha256"])
    registered = {fixtures.file_digest(
        fixtures.arm_prompt_path(population.arms_root, arm))
        for arm in fixtures.ARMS}
    assert len(registered) == 5, "two arms share a prompt: the gate is not keyed"
    assert digests == registered


# --- C4's earlier list: drops, mislabels, empty classes, the two run kinds ----

def test_the_drop_code_element_set_produces_the_registered_histogram(scored):
    """One element per drop code, in the compiler's own check order, so a
    reordered or skipped check shows up as a changed histogram."""
    _population, _specs, results = scored
    row = results["byKey"][("B", "run-002")]
    assert row["valid"] and row["code"] is None
    assert row["dropCodes"] == fixtures.DROP_HISTOGRAM
    assert row["accepted"] == len(fixtures.DROP_PROFILE["accepted"])
    assert row["coveredClasses"] == fixtures.DROP_PROFILE["covered"]
    # The one surviving element is correctly labelled and satisfies no class
    # predicate, so this run reached no class (round 4, finding 9).
    assert row["h"] == 1 and row["coveredNothing"] is True


def test_the_mislabel_fixture_reaches_a_class_only_through_Q(scored):
    """A class reached ONLY by a mislabelled record, and two classes reached by
    no record at all — the two shapes §4.6's S1/S2 table is about."""
    _population, _specs, results = scored
    row = results["byKey"][("E", "run-003")]
    assert row["valid"]
    assert row["coveredClasses"] == fixtures.PARTIAL_PROFILE["covered"]
    assert row["rawClasses"] == fixtures.PARTIAL_PROFILE["raw"]
    assert row["qClasses"] == fixtures.PARTIAL_PROFILE["qIntersection"]
    assert row["qOnlyClasses"] == fixtures.PARTIAL_PROFILE["qOnly"]
    for index in fixtures.PARTIAL_PROFILE["unreached"]:
        assert index not in row["rawClasses"]
        assert row["classMembers"][str(index)] == {"h": [], "q": []}


def test_the_accepted_ids_are_the_registered_ones(scored):
    """C4's first sentence: the expected output is "accepted ids, drop codes,
    H/Q membership, per-class coverage, and the census counts", registered in
    the same committed module. The ids are the compiler's own output, taken
    from the records the scorer carried into the census rather than from a
    second compilation of the same bytes."""
    _population, _specs, results = scored
    accepted = {(arm, slot): sorted(record["caseId"] for record in records)
                for arm, runs in results["recordsByArm"].items()
                for slot, records in runs.items()}
    assert accepted[("D", "run-001")] == fixtures.FULL_PROFILE["accepted"]
    assert accepted[("E", "run-003")] == fixtures.PARTIAL_PROFILE["accepted"]
    assert accepted[("B", "run-002")] == fixtures.DROP_PROFILE["accepted"]
    assert accepted[("D", "run-002")] == []          # the authoring-empty run
    # H/Q membership, id by id, where it is the point: the mislabel class.
    partial = results["byKey"][("E", "run-003")]
    assert partial["classMembers"]["2"] == {"h": [], "q": ["mislabelled-at-low"]}
    assert partial["classMembers"]["4"] == {"h": ["embargoed-syria"], "q": []}
    assert results["byKey"][("D", "run-001")]["classMembers"] \
        == fixtures.FULL_PROFILE["members"]


def test_an_authoring_empty_run_is_valid_and_covers_nothing(scored):
    """§3.3: excluding it would condition every rate on the author having
    succeeded — and in this study it would score a perturbation that makes the
    author fail outright as if it had never been tried."""
    _population, _specs, results = scored
    row = results["byKey"][("D", "run-002")]
    assert row["valid"] and row["code"] is None
    assert row["authoringEmpty"] and row["noParseableArray"]
    assert row["accepted"] == 0 and row["coveredClasses"] == []
    assert results["arms"]["D"]["population"]["authoringEmpty"] == 1


def test_the_population_arithmetic_is_intent_to_treat_at_a_known_k_and_n(scored):
    """C4's "at known `k` and `n`": every rate's denominator is the registered
    N = 30 whatever an arm's valid count, and a pipeline-invalid slot counts as
    covering nothing rather than leaving the denominator (§4.2)."""
    _population, _specs, results = scored
    n = results["trials"]
    assert n == 30
    for arm in fixtures.ARMS:
        block = results["arms"][arm]
        expected = EXPECTED_POPULATION[arm]
        assert {key: block["population"][key] for key in expected} == expected, arm
        assert block["population"]["pipelineInvalidRate"]["count"] == expected["invalid"]
        assert block["population"]["pipelineInvalidRate"]["trials"] == n
        assert [row["primary"]["count"] for row in block["classes"]] \
            == EXPECTED_PRIMARY_K[arm], arm
        assert [row["placement"]["count"] for row in block["classes"]] \
            == EXPECTED_PLACEMENT_K[arm], arm
        assert set(row["primary"]["trials"] for row in block["classes"]) == {n}
        assert set(row["perProtocol"]["trials"] for row in block["classes"]) \
            == {expected["valid"]}
        # The per-protocol floor: below V_X = 11 no arm here can read HIGH, and
        # §5.1 registers UNRESOLVED-BY-DESIGN rather than a table of MIDs.
        assert block["population"]["perProtocolFloorMet"] is False


def test_the_shifted_edge_arm_reproduces_the_six_classes(scored):
    """C4: a synthetic arm at (45, 72) whose records reproduce the same six
    classes at the shifted edges, so the arm parameterization is exercised
    rather than assumed."""
    population, _specs, results = scored
    low, high = fixtures.arm_pair(population.arms_root, "D")
    assert (str(low), str(high)) == ("45", "72")
    row = results["byKey"][("D", "run-001")]
    assert row["coveredClasses"] == fixtures.FULL_PROFILE["covered"] == [0, 1, 2, 3, 4, 5]
    assert row["classMembers"] == fixtures.FULL_PROFILE["members"]
    assert row["q"] == 0 and row["h"] == row["accepted"] == 7


def test_the_shifted_edge_arm_covers_none_of_the_old_narrow_classes(scored):
    """C4: a synthetic arm covering the new-keyed classes and not the old-keyed
    ones, so S10's cross-scoring is exercised at a known answer.

    §5.3 (ii) predicts exactly this shape and says why it is not a falsifier:
    arm A's class 3 is a 30-wide band that most of D's own band lies inside,
    and class 4 names no numeric boundary at all.
    """
    _population, _specs, results = scored
    row = results["byKey"][("D", "run-001")]
    assert row["oldEdgeClasses"] == fixtures.FULL_OLD_EDGE_FROM_D == [3, 4]
    for arm in fixtures.ARMS:
        assert [entry["oldEdge"]["count"] for entry in results["arms"][arm]["classes"]] \
            == EXPECTED_OLD_EDGE_K[arm], arm
    for index in score_rates.NARROW_NUMERIC_CLASSES:
        assert results["arms"]["D"]["classes"][index]["oldEdge"]["count"] == 0


def test_the_census_counts_are_the_registered_ones(scored):
    """C4 requires the census counts to be registered beside the fixtures too,
    and the census is a registered secondary (§4.5), so it is asserted on the
    same population rather than on a second derivation of it."""
    _population, _specs, results = scored
    # Arm A's one admissible slot is the full completion, so its census IS the
    # profile registered beside that fixture, member for member.
    arm_a = results["census"]["A"]
    assert arm_a["population"]["records"] == fixtures.FULL_CENSUS["records"]
    assert arm_a["population"]["h"] == fixtures.FULL_CENSUS["h"]
    assert arm_a["population"]["q"] == fixtures.FULL_CENSUS["q"]
    assert [row["records"] for row in arm_a["x1"]["classes"]] \
        == fixtures.FULL_CENSUS["recordsPerClass"]
    assert [row["probes"] for row in arm_a["x1"]["classes"]] \
        == fixtures.FULL_CENSUS["probesPerClass"]
    for arm in fixtures.ARMS:
        block = results["census"][arm]
        expected = EXPECTED_CENSUS[arm]
        assert block["population"]["runs"] == expected["runs"], arm
        assert block["population"]["records"] == expected["records"], arm
        assert block["population"]["h"] == expected["h"], arm
        assert block["population"]["q"] == expected["q"], arm
        assert [row["probes"] for row in block["x1"]["classes"]] \
            == expected["probes"], arm
    # X6's sentinel table is arm E's alone (§4.5), and no other arm carries one.
    assert results["census"]["E"]["x6"] is not None
    assert all(results["census"][arm]["x6"] is None
               for arm in fixtures.ARMS if arm != "E")


# --- C4 fixture 4: the same-arm copy ----------------------------------------

def test_a_same_arm_copy_at_another_index_is_schedule_mismatch(pins, study):
    """C4 fixture 4, first half: right arm, right prompt digest, right
    registry — so `arm-mismatch` cannot see it — and the slot's own record of
    where it sits in §2.8's order is what does.

    The copy is made BEFORE the seal, so the manifest covers the copied bytes
    and the refusal is the schedule check's rather than §2.9's.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        source = os.path.join(population.arms_root, "A", "authoring", "run-001")

        def copy_over(slot: str) -> None:
            shutil.rmtree(slot)
            shutil.copytree(source, slot)

        # Nine slots: round 1 (B, C, A, D, E) and round 2 through arm A's
        # second slot, which is where the copy lands.
        specs = [{} for _ in range(9)]
        specs[8] = {"mutate": copy_over}
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("A", "run-002")]
        assert row["code"] == "schedule-mismatch"
        assert row["globalIndex"] == 9
        assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
        # …and the slot it was copied FROM is untouched and still counted.
        assert results["byKey"][("A", "run-001")]["valid"]
    finally:
        shutil.rmtree(root, True)


def test_a_slot_with_no_ledger_record_refuses_the_whole_scoring(pins, study):
    """C4 fixture 4, second half: the ledger and the slot set are in bijection
    or no rate is computed at all (§3.3, C5 rule 2).

    A same-arm copy that the ledger never recorded is exactly the slot that a
    per-slot code would leave in a denominator, so this refusal is the whole
    scoring's rather than that slot's.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        source = os.path.join(population.arms_root, "A", "authoring", "run-001")
        shutil.copytree(source, os.path.join(os.path.dirname(source), "run-002"))
        with pytest.raises(score_rates.ScoreError) as caught:
            population.score_runs()
        assert "no ledger record" in str(caught.value)
        assert "A/run-002" in str(caught.value)
    finally:
        shutil.rmtree(root, True)


# --- C4 fixture 7: the seal, and what a broken one costs ---------------------

def test_a_broken_seal_does_not_move_the_slot_out_of_its_denominator(pins, study):
    """C4 fixture 7, first half. §2.9's consequence is code and not a sentence:
    a slot whose recomputed manifest disagrees with the ledger is NOT marked
    invalid, because a code that moved one slot out of `V_X` would hand an
    alteration precisely the denominator change that produces the verdict it
    was made to produce.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)

        def alter_after_sealing(slot: str) -> None:
            with open(os.path.join(slot, "stderr.raw"), "wb") as handle:
                handle.write(b"one byte the seal did not cover\n")

        specs = [{} for _ in range(5)]
        specs[2] = {"break_seal": alter_after_sealing}      # arm A's run-001
        population.build(specs)
        results = population.score_runs()
        assert results["seal"]["verified"] is False
        assert results["seal"]["chainFailure"] is None, (
            "the chain must still verify: this fixture is about the MANIFEST")
        failures = results["seal"]["manifestFailures"]
        assert [(entry["arm"], entry["slot"]) for entry in failures] \
            == [("A", "run-001")]
        assert "not the bytes it was sealed over" in failures[0]["detail"]
        # The altered slot is demonstrably NOT moved out of V_X: it is valid,
        # it carries no code, and the other four are untouched.
        altered = results["byKey"][("A", "run-001")]
        assert altered["valid"] and altered["code"] is None
        assert all(row["valid"] for row in results["runs"])
    finally:
        shutil.rmtree(root, True)


def test_a_broken_seal_makes_the_whole_scoring_unresolved_with_no_contrast(scored):
    """C4 fixture 7, second half, on a batch that is otherwise complete — so
    the refusal is the SEAL's and not the stopping rule's.

    Both calls run over the same arm blocks and differ only in `sealed`, which
    is what makes the assertion about §2.9 rather than about incompleteness.
    """
    _population, _specs, results = scored
    blocks = results["arms"]
    n = results["trials"]
    sealed = score_rates.compute_verdicts(blocks, n, True, True)
    broken = score_rates.compute_verdicts(blocks, n, True, False)
    assert sealed["resolved"] is True and sealed["contrasts"] is not None
    assert broken["resolved"] is False
    assert broken["contrasts"] is None
    assert broken["gate"] is None
    for arm in fixtures.ARMS:
        for endpoint in score_rates.LEVEL_ENDPOINTS:
            assert set(broken["levels"][arm][endpoint]) == {score_rates.UNRESOLVED}
    assert broken["decisionRow"]["row"] == 1
    assert broken["decisionRow"]["publishedAs"] == score_rates.UNRESOLVED
    assert "manifest" in broken["decisionRow"]["why"]
    assert "manifest" in broken["unresolvedReason"]


# --- C4 fixture 8: every row of §5.3's decision table, at known integers -----
#
# A pattern is (k_H, k_raw) per class over one arm's 30 scheduled slots: the
# first k_H slots cover the class with a correctly-labelled record and the
# first k_raw place a record inside it whatever the label, so `H(r) ⊆ A(r)`
# holds row by row and `k_H <= k_raw` holds by construction.
PERFECT = [(30, 30)] * 6
HALF = [(15, 15)] * 6
# Arm B misses two classes half the time: MID on two, so TRACKING on four of
# six, one short of the five §5.3 (iii) requires. The gate is a gate.
GATE_SHORT = [(15, 15), (15, 15)] + [(30, 30)] * 4
# Arm E's four narrow numeric classes go to zero on BOTH endpoints: the
# placement collapse §5.3 (i) predicts, and the only pattern that confirms R1.
PLACEMENT_COLLAPSE = [(0, 0), (0, 0), (0, 0), (30, 30), (30, 30), (0, 0)]
# The same records, still at the boundary, with the labels gone: the primary
# collapses and the placement does not (§4.6's *label collapse*).
LABEL_COLLAPSE = [(0, 30), (0, 30), (0, 30), (30, 30), (30, 30), (0, 30)]
# Class 4 — the embargo-membership class, which names no numeric boundary —
# collapses in arm E: not a literal effect, and row 2 withdraws every other
# reading of arm E before the gate is even consulted.
CLASS4_COLLAPSE = [(30, 30)] * 4 + [(0, 0)] + [(30, 30)]

# Each scenario: the pattern per arm, whether the batch is complete and sealed,
# the registered pattern counts, and the row §5.3's table must return.
DECISION_SCENARIOS = (
    {"why": "an incomplete batch: the stopping rule [D-21] returns no verdict",
     "arms": {}, "complete": False, "sealed": True,
     "row": 1, "publishedAs": score_rates.UNRESOLVED},
    {"why": "a seal that does not verify (§2.9), on an otherwise complete batch",
     "arms": {}, "complete": True, "sealed": False,
     "row": 1, "publishedAs": score_rates.UNRESOLVED},
    {"why": "arm E reads COLLAPSE on class 4",
     "arms": {"E": CLASS4_COLLAPSE}, "complete": True, "sealed": True,
     "row": 2, "publishedAs": "E-DEGRADED-GENERALLY",
     "counts": {"nP": 0, "nC": 0, "nH": 4}},
    {"why": "arm B TRACKING on four of six: the control gate fails",
     "arms": {"B": GATE_SHORT}, "complete": True, "sealed": True,
     "row": 3, "publishedAs": "CONTROLS-FAILED",
     "counts": {"nP": 0, "nC": 0, "nH": 4}, "gate": {"B": 4, "C": 6}},
    {"why": "arm E HIGH on all four narrow numeric classes: R1's prediction "
            "did not occur",
     "arms": {}, "complete": True, "sealed": True,
     "row": 4, "publishedAs": "R1-UNSUPPORTED",
     "counts": {"nP": 0, "nC": 0, "nH": 4}},
    {"why": "arm E placement-collapses on all four with its labels at the "
            "ceiling: the CONFIRMED pattern",
     "arms": {"E": PLACEMENT_COLLAPSE}, "complete": True, "sealed": True,
     "row": 5, "publishedAs": "CONFIRMED",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling"},
    # The same placement collapse with the labels gone: §4.6's SECOND row, the
    # one round 3 found unreachable. "The author could not derive or apply the
    # values" is a comprehension collapse, it is published as one, and it does
    # not confirm R1 — so row 5 does not fire and the table's last row does.
    {"why": "arm E placement-collapses on all four while its S5 labels are "
            "degraded: §4.6's comprehension collapse, and R1 is not confirmed",
     "arms": {"E": PLACEMENT_COLLAPSE}, "mislabelled": {"E": (3, 4)},
     "complete": True, "sealed": True,
     "row": 7, "publishedAs": "INDETERMINATE",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "comprehension collapse", "labels": "degraded"},
    {"why": "the records are still at the boundary and the labels are not",
     "arms": {"E": LABEL_COLLAPSE}, "complete": True, "sealed": True,
     "row": 6, "publishedAs": "LABEL-COLLAPSE-ONLY",
     "counts": {"nP": 0, "nC": 4, "nH": 0},
     "reading": "label collapse", "labels": "degraded"},
    {"why": "arm E MID on every class: §5.4 says this is what a PARTIAL "
            "anchoring effect looks like at N = 30",
     "arms": {"E": HALF}, "complete": True, "sealed": True,
     "row": 7, "publishedAs": "INDETERMINATE",
     "counts": {"nP": 0, "nC": 0, "nH": 0}},
)


@pytest.fixture(scope="module")
def arm_blocks(pins):
    """`score_arm()` over synthetic rows at known integers, memoized per (arm,
    pattern) because each block costs 44 exact intervals.

    The arm definitions are the study's own committed artifacts at their pinned
    digests, read through `score_rates.load_arm()` — so a scenario is scored
    against the six real predicates of a real arm, and only the per-slot
    counting the other fixtures exercise on real bytes is short-circuited.
    """
    definitions = {arm: score_rates.load_arm(score_rates.REGISTERED_ARMS, arm,
                                             pins["arms"][arm])
                   for arm in fixtures.ARMS}
    for arm in fixtures.ARMS:
        definitions[arm]["oldEdgeClasses"] = definitions["A"]["classes"]
    schedule = score_rates.registered_schedule()
    cache = {}

    def block(arm: str, pattern, mislabelled=(), old_edge=None) -> dict:
        """One arm's block at a pattern of `(k_H, k_raw)` per class.

        `mislabelled` names classes that carry a Q record in every row on top of
        the ones the pattern already implies, which is what moves §4.6's S5
        branch off the ceiling; `old_edge` is the per-class `k` under ARM A's
        predicates (S10) and defaults to the arm's own coverage, which is what
        it is for every arm keyed at (40, 70) and is not for arm D.
        """
        key = (arm, tuple(pattern), tuple(mislabelled),
               None if old_edge is None else tuple(old_edge))
        if key not in cache:
            entries = [entry for entry in schedule if entry["arm"] == arm]
            assert len(entries) == pins["batch"]["n"]
            rows = []
            for index, entry in enumerate(entries):
                covered = [c for c, (k_h, _) in enumerate(pattern) if index < k_h]
                raw = [c for c, (_, k_raw) in enumerate(pattern) if index < k_raw]
                # A class reached raw and not in H holds a mislabelled record by
                # construction, so the row carries one: `H(r) ⊆ A(r)` is not the
                # only thing the fixture owes the scorer — the Q count that
                # difference implies is S5's input (round 3, finding 9).
                q_only = [c for c in raw if c not in covered]
                quarantined = sorted(set(mislabelled) | set(q_only))
                old = (covered if old_edge is None
                       else [c for c, k in enumerate(old_edge) if index < k])
                rows.append(fixtures.synthetic_row(arm, entry, covered=covered,
                                                   raw=raw, q=quarantined,
                                                   q_only=q_only, old_edge=old))
            computed = score_rates.score_arm(arm, definitions[arm],
                                             pins["batch"]["n"], rows, {}, [])
            computed.pop("census")
            cache[key] = computed
        return cache[key]

    return block


@pytest.mark.parametrize("scenario", DECISION_SCENARIOS,
                         ids=[str(entry["row"]) + "-" + entry["publishedAs"]
                              for entry in DECISION_SCENARIOS])
def test_the_decision_table_rows_all_fire_at_known_integers(scenario, arm_blocks,
                                                            pins):
    """C4 fixture 8: "a table whose gate rows never fire in any test is a table
    nobody has run".

    Every row of §5.3's decision table, including 1, 2, 3 and 6, from a
    synthetic population at known integers — and the counts `nP`, `nC` and `nH`
    the scorer derived from those integers are asserted beside the row, so a
    row that fired for the wrong reason is a failure and not a pass.
    """
    mislabelled = scenario.get("mislabelled", {})
    blocks = {arm: arm_blocks(arm, scenario["arms"].get(arm, PERFECT),
                              mislabelled.get(arm, ()))
              for arm in fixtures.ARMS}
    verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"],
                                            scenario["complete"],
                                            scenario["sealed"])
    row = verdicts["decisionRow"]
    assert (row["row"], row["publishedAs"]) == (scenario["row"],
                                                scenario["publishedAs"])
    assert row["condition"] == score_rates.DECISION_TABLE[row["row"] - 1]["condition"]
    if "counts" in scenario:
        assert verdicts["patternCounts"] == scenario["counts"]
    # §4.6's reading, beside the row and never instead of it (round 3,
    # finding 9): the branch the S5 cut put arm E on, and the row of §4.6's
    # table its integers fall on.
    if "reading" in scenario:
        assert verdicts["reading"]["publishedAs"] == scenario["reading"]
        assert verdicts["reading"]["labels"] == scenario["labels"]
        assert row["reading"] == scenario["reading"]
        assert verdicts["labelBranches"]["E"]["branch"] == scenario["labels"]
        assert verdicts["reading"]["confirmsR1"] is (scenario["row"] == 5)
    if "gate" in scenario:
        assert verdicts["gate"]["arms"] == scenario["gate"]
        assert verdicts["gate"]["passed"] is False
        assert verdicts["gate"]["shortfall"] == ["B"]
    if scenario["row"] == 1:
        # Rows 1's two causes both withdraw the whole confirmatory surface —
        # §4.6's reading and §5.3 (ii)'s arm-D outcome included, because both
        # are read off level verdicts that row 1 makes UNRESOLVED-BY-DESIGN.
        assert verdicts["contrasts"] is None
        assert verdicts["patternCounts"] == {"nP": None, "nC": None, "nH": None}
        assert verdicts["reading"] is None and verdicts["armD"] is None
        # The S5 branch is a statement about the records, not about the rule,
        # so it is published either way.
        assert set(verdicts["labelBranches"]) == set(fixtures.ARMS)
    else:
        assert verdicts["resolved"] is True
        assert verdicts["gate"] is not None
        assert verdicts["armD"]["publishedAs"] in [
            entry["publishedAs"] for entry in score_rates.D_OUTCOME_TABLE]
    if scenario["row"] == 2:
        # §5.3 (iv): every other reading of arm E is withdrawn in favour of the
        # class-4 collapse — published with that fact attached, not deleted.
        assert verdicts["reading"]["withdrawn"] is True


def test_rows_four_and_five_cannot_both_hold(arm_blocks, pins):
    """§5.3's own registered note: `k_H ≤ k_raw` per class, so a class with E's
    primary HIGH has E's placement HIGH too and cannot be a placement collapse.
    With four classes, `nH ≥ 3` and `nP ≥ 3` are incompatible — and the order
    is stated anyway, because a decision table with an unreachable ambiguity is
    still a decision table with an ambiguity."""
    for pattern in (PERFECT, PLACEMENT_COLLAPSE, LABEL_COLLAPSE, HALF):
        blocks = {arm: arm_blocks(arm, PERFECT if arm != "E" else pattern)
                  for arm in fixtures.ARMS}
        counts = score_rates.compute_verdicts(blocks, pins["batch"]["n"],
                                              True, True)["patternCounts"]
        assert not (counts["nH"] >= score_rates.PATTERN_MINIMUM
                    and counts["nP"] >= score_rates.PATTERN_MINIMUM)
        # …and the placement contrast implies the primary one, class by class.
        assert counts["nP"] <= counts["nC"]


# --- §5.3 (ii)'s three outcomes for arm D, at known integers ----------------
#
# Arm D's own-keyed pattern when its narrow numeric classes collapse under its
# OWN family, and the two S10 old-edge patterns that separate the three
# outcomes: records at the old edges (40, 70) or at neither pair.
D_NARROW_COLLAPSE = [(0, 0), (0, 0), (0, 0), (30, 30), (30, 30), (0, 0)]
D_OLD_EDGES_HELD = [30, 30, 30, 30, 30, 30]
D_OLD_EDGES_GONE = [0, 0, 0, 30, 30, 0]
# Round 4, finding 6: the registered condition for the first outcome is
# new-keyed HIGH on the narrow numeric classes with the old-keyed levels NOT
# HIGH-patterned — it says nothing about the non-narrow classes. Arm D HIGH on
# all four narrow classes and MID on class 3 satisfies it, and reads TRACKING on
# five contrasts rather than six, which the code's earlier all-six rule refused.
D_NARROW_HELD_CLASS_THREE_MID = [(30, 30), (30, 30), (30, 30), (15, 15),
                                 (30, 30), (30, 30)]

D_SCENARIOS = (
    {"why": "arm D's new-keyed verdicts are HIGH on all four narrow numeric "
            "classes and its old-keyed ones are not HIGH-patterned: coverage "
            "follows the numbers — and it still does with class 3's contrast "
            "INDETERMINATE, which the registered condition says nothing about",
     "pattern": D_NARROW_HELD_CLASS_THREE_MID, "oldEdge": D_OLD_EDGES_GONE,
     "publishedAs": "COVERAGE-FOLLOWS-THE-NUMBERS",
     "counts": {"newKeyedHigh": 4, "newKeyedLow": 0, "oldKeyedHigh": 0,
                "oldKeyedLow": 4, "tracking": 5, "narrowMinimum": 3,
                "classes": 6}},
    {"why": "arm D's new-keyed verdicts are LOW on the narrow numeric classes "
            "while its old-keyed ones are HIGH: the model reproduced 40 and 70 "
            "against a text that says 45 and 72",
     "pattern": D_NARROW_COLLAPSE, "oldEdge": D_OLD_EDGES_HELD,
     "publishedAs": "OLD-EDGE-PREFERENCE",
     "counts": {"newKeyedHigh": 0, "newKeyedLow": 4, "oldKeyedHigh": 4,
                "oldKeyedLow": 0, "tracking": 2, "narrowMinimum": 3,
                "classes": 6}},
    {"why": "neither threshold pair: a general degradation, published as one",
     "pattern": D_NARROW_COLLAPSE, "oldEdge": D_OLD_EDGES_GONE,
     "publishedAs": "GENERAL-DEGRADATION",
     "counts": {"newKeyedHigh": 0, "newKeyedLow": 4, "oldKeyedHigh": 0,
                "oldKeyedLow": 4, "tracking": 2, "narrowMinimum": 3,
                "classes": 6}},
    # The case the old-keyed exclusion exists for, and the one the earlier code
    # published as the first outcome: arm D tracks arm A on all six classes AND
    # its records reach the old edges too, so both keyings read HIGH. That is
    # not "coverage follows the numbers" — the numbers do not separate the two
    # threshold pairs at all — and §5.3 (ii) names no outcome for it.
    {"why": "new-keyed and old-keyed both HIGH-patterned: the records cover "
            "both threshold pairs, which the registered exclusion refuses to "
            "call coverage following D's numbers",
     "pattern": PERFECT, "oldEdge": D_OLD_EDGES_HELD,
     "publishedAs": "D-INDETERMINATE",
     "counts": {"newKeyedHigh": 4, "newKeyedLow": 0, "oldKeyedHigh": 4,
                "oldKeyedLow": 0, "tracking": 6, "narrowMinimum": 3,
                "classes": 6}},
)


@pytest.mark.parametrize("scenario", D_SCENARIOS,
                         ids=[entry["publishedAs"] for entry in D_SCENARIOS])
def test_arm_ds_registered_outcomes_all_fire_at_known_integers(scenario,
                                                               arm_blocks, pins):
    """Round 3, finding 10: §5.3 (ii) registers three outcomes for arm D and
    the scorer computed none of them, publishing marginal old-edge levels and
    aggregating outcomes for arm E alone.

    Round 4, finding 6: the scenarios drive the REGISTERED condition for the
    first outcome — new-keyed HIGH on at least three of the four narrow numeric
    classes with the old-keyed levels not HIGH-patterned — rather than the code's
    stricter invention (all six contrasts TRACKING, the old-keyed levels never
    consulted). The first and last scenarios are the two the two rules disagree
    about, in opposite directions.

    Each row fires here from a synthetic population at known integers, and the
    counts the scorer derived are asserted beside the outcome so a row that
    fired for the wrong reason is a failure and not a pass.
    """
    blocks = {arm: arm_blocks(arm, PERFECT) for arm in fixtures.ARMS}
    blocks["D"] = arm_blocks("D", scenario["pattern"], (), scenario["oldEdge"])
    verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"], True, True)
    outcome = verdicts["armD"]
    assert outcome["publishedAs"] == scenario["publishedAs"]
    assert outcome["counts"] == scenario["counts"]
    assert outcome["condition"] == \
        score_rates.D_OUTCOME_TABLE[outcome["row"] - 1]["condition"]
    # The old-edge preference publishes BOTH registered explanations and
    # asserts neither; the other rows carry none.
    if scenario["publishedAs"] == "OLD-EDGE-PREFERENCE":
        assert len(outcome["explanations"]) == 2
        assert outcome["separates"] == score_rates.D_OLD_EDGE_NOTE
    else:
        assert outcome["explanations"] == [] and outcome["separates"] is None
    # The first scenario's point, stated rather than left to a count: a class
    # OUTSIDE the four narrow numeric ones reads INDETERMINATE, and §5.3 (ii)'s
    # condition — stated over the narrow classes and the old-keyed levels —
    # holds anyway. The earlier all-six-TRACKING rule published D-INDETERMINATE
    # here (round 4, finding 6).
    if scenario["pattern"] is D_NARROW_HELD_CLASS_THREE_MID:
        contrasts = {row["index"]: row["contrast"]
                     for row in verdicts["contrasts"]["D"]}
        assert contrasts[3] == "INDETERMINATE"
        assert all(contrasts[index] == "TRACKING"
                   for index in score_rates.NARROW_NUMERIC_CLASSES)
    # Arm D's outcome adjudicates nothing about R1: the decision-table row is
    # what it would have been without arm D in the batch at all.
    assert verdicts["decisionRow"]["row"] == 4        # arm E is PERFECT here


# --- §3.3's authoring-empty row, narrowed, and S3's denominators -------------

def _arm_d_shapes(population) -> list:
    """A twelve-slot prefix of the registered order in which ARM D holds all
    three shapes §3.3 distinguishes: an array every element of which is
    dropped, an array whose only record this arm's mirror quarantines, and no
    parseable array at all.

    Twelve because the registered order gives arm D its three slots at global
    indices 4, 6 and 12 — one per shape, in one arm, so the published counts
    are a statement about one denominator.
    """
    low, high = fixtures.arm_pair(population.arms_root, "D")
    # Every element dropped: `drop_records()` without its accepted first
    # element and without the duplicate that only duplicates it.
    all_dropped = fixtures.completion(fixtures.drop_records()[1:-1])
    # One accepted record, quarantined by the mirror: the array parses, the
    # compiler accepts it, and no class is reached in H.
    all_quarantined = fixtures.completion(
        fixtures.quarantined_only_records(low, high))
    specs = [{} for _ in range(12)]
    specs[3] = {"answer": all_dropped}            # D/run-001
    specs[5] = {"answer": all_quarantined}        # D/run-002
    specs[11] = {"answer": fixtures.COMPLETION_EMPTY}   # D/run-003
    return specs


@pytest.fixture(scope="module")
def authoring_shapes(pins, study):
    """The twelve-slot population above, built and scored once."""
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build(_arm_d_shapes(population))
        yield population, population.score_runs()
    finally:
        shutil.rmtree(root, True)


def test_authoring_empty_is_the_partition_row_and_not_the_wider_quantity(
        authoring_shapes):
    """Round 3, finding 13: §3.3 reserves `authoring-empty` for a completion
    with NO PARSEABLE ARRAY, and the scorer also set it for a parseable array
    every element of which was dropped and for one whose records were all
    mislabelled. Those are real authoring outcomes and they are published — as
    `coveredNothing`, under their own name, where no reader takes them for
    §3.3's row.
    """
    _population, results = authoring_shapes
    dropped = results["byKey"][("D", "run-001")]
    quarantined = results["byKey"][("D", "run-002")]
    empty = results["byKey"][("D", "run-003")]
    # All three are VALID: none of them is a pipeline failure (§4.2 [D-24]).
    for row in (dropped, quarantined, empty):
        assert row["valid"] and row["code"] is None
        assert row["coveredClasses"] == [] and row["coveredNothing"] is True
    # …and exactly one of them is §3.3's row.
    assert [row["authoringEmpty"] for row in (dropped, quarantined, empty)] \
        == [False, False, True]
    assert [row["noParseableArray"] for row in (dropped, quarantined, empty)] \
        == [False, False, True]
    # The shapes are what they claim to be: an array that parsed and lost every
    # element, and an array whose one record the mirror quarantined.
    assert dropped["accepted"] == 0 and dropped["dropped"] == 6
    assert quarantined["accepted"] == 1 and quarantined["h"] == 0 \
        and quarantined["q"] == 1
    assert empty["accepted"] == 0 and empty["dropped"] == 0


def _covered_nothing_shapes(population) -> list:
    """One round of the registered call order — B, C, A, D, E — carrying the two
    shapes round 4's finding 9 names, in two different arms.

    Arm A's slot holds a single accepted record its own mirror labels correctly
    and no class predicate admits; arm E's holds a single accepted record its
    own mirror quarantines whose predicates put it in classes 2 and 3. Both
    reached no class. The first is the case the old formula got wrong; the
    second is the case whose ANSWER is unchanged and whose REASON is not.
    """
    specs = [{} for _ in range(5)]
    specs[2] = {"answer": fixtures.completion(fixtures.LABELLED_NO_CLASS)}
    specs[4] = {"answer": fixtures.completion(fixtures.quarantined_only_records(
        *fixtures.arm_pair(population.arms_root, "E")))}
    return specs


@pytest.fixture(scope="module")
def covered_nothing_shapes(pins, study):
    """The five-slot population above, built and scored once."""
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build(_covered_nothing_shapes(population))
        yield population, population.score_runs()
    finally:
        shutil.rmtree(root, True)


def test_covered_nothing_is_the_empty_covered_class_set(covered_nothing_shapes):
    """Round 4, finding 9: the published surface defines `coveredNothing` as a
    valid run that reached no class, and the scorer computed `empty or not
    accepted or not high` — which asks whether the run held any correctly
    labelled record, a different question with a different answer.

    Arm A's slot is where the two questions disagree: one accepted record, in H,
    satisfying no class predicate. Its covered-class set is empty and the old
    formula called it a covering run.

    Arm E's slot is the other case the finding names, and the registered surface
    is what says what it is: coverage is over H — a class is reached when a
    record this arm's mirror labelled CORRECTLY satisfies its predicate — so a
    run whose only record is quarantined covers nothing even though it reaches
    classes 2 and 3 in the raw (S1) and Q (S2) senses, which are published as
    their own members beside it. `coveredNothing` is true there too.
    """
    _population, results = covered_nothing_shapes
    labelled = results["byKey"][("A", "run-001")]
    profile = fixtures.LABELLED_NO_CLASS_PROFILE
    assert labelled["valid"] and labelled["code"] is None
    assert labelled["accepted"] == len(profile["accepted"])
    assert labelled["h"] == len(profile["h"]) == 1 and labelled["q"] == 0
    assert labelled["coveredClasses"] == profile["covered"] == []
    assert labelled["rawClasses"] == profile["raw"] == []
    assert labelled["coveredNothing"] is True
    # §3.3's own row is untouched by this: the array parsed (round 3, finding 13).
    assert labelled["authoringEmpty"] is False and labelled["dropCodes"] == {}

    quarantined = results["byKey"][("E", "run-001")]
    q_profile = fixtures.QUARANTINED_ONLY_PROFILE
    assert quarantined["valid"] and quarantined["accepted"] == 1
    assert quarantined["h"] == 0 and quarantined["q"] == 1
    assert quarantined["coveredClasses"] == q_profile["covered"] == []
    assert quarantined["rawClasses"] == q_profile["raw"] == [2, 3]
    assert quarantined["qClasses"] == q_profile["qIntersection"] == [2, 3]
    assert quarantined["coveredNothing"] is True
    assert quarantined["authoringEmpty"] is False

    # And the identity the member now has, over every valid run in the batch:
    # `coveredNothing` is the empty covered-class set and nothing else.
    for row in results["runs"]:
        if row["valid"]:
            assert row["coveredNothing"] is (row["coveredClasses"] == []), row["slot"]


def test_both_counts_are_published_over_the_same_valid_runs(authoring_shapes,
                                                            pins):
    """The published pair, over arm D's three valid runs: one authoring-empty
    by §3.3's row, three that reached no class at all."""
    population, results = authoring_shapes
    block = score_rates.score_arm("D", population.definitions()["D"],
                                  pins["batch"]["n"],
                                  [row for row in results["runs"]
                                   if row["arm"] == "D"],
                                  results["recordsByArm"]["D"], [])
    assert block["population"]["valid"] == 3
    assert block["population"]["authoringEmpty"] == 1
    assert block["population"]["coveredNothing"] == 3
    assert "`authoringEmpty` is §3.3's partition row" in block["population"]["note"]


def test_the_s3_surface_is_over_one_denominator_and_names_it(authoring_shapes,
                                                             pins):
    """Round 3, finding 14: S3's distribution iterated the rows present while
    its mean and all-six rate divided by N, so a twelve-slot prefix published a
    distribution totalling 2 beside a rate over 30 and nothing said which was
    which. One denominator now — N, intent-to-treat — with the scheduled slots
    the batch never executed counted as `absent` in the 0 bucket and named.
    """
    population, results = authoring_shapes
    n = pins["batch"]["n"]
    definitions = population.definitions()
    for arm, present, covering in (("B", 2, 2), ("D", 3, 0)):
        block = score_rates.score_arm(arm, definitions[arm], n,
                                      [row for row in results["runs"]
                                       if row["arm"] == arm],
                                      results["recordsByArm"][arm], [])
        breadth = block["coverageBreadth"]
        assert breadth["trials"] == n and breadth["denominator"] == "N"
        assert breadth["present"] == present
        assert breadth["absent"] == n - present
        # Every quantity in the block is over that one denominator.
        assert sum(breadth["distribution"].values()) == n
        assert breadth["allSix"]["trials"] == n
        assert breadth["allSix"]["count"] == covering
        assert breadth["distribution"]["6"] == covering
        assert breadth["distribution"]["0"] == n - covering
        assert breadth["mean"] == covering * 6 / n
        assert "%d" % breadth["absent"] in breadth["note"]


# --- the rendered tables, over the surfaces round 3 added --------------------

def _renderable(blocks: dict, verdicts: dict, pins: dict) -> dict:
    """The results shape `render_markdown()` reads, around real `score_arm()`
    blocks and real verdicts.

    The cell and the schedule are the only synthesized members: they are the
    provenance header, not an arithmetic surface, and every number the tables
    below print comes from the blocks and the verdicts.
    """
    return {
        "schedule": {"roundsCompleted": pins["batch"]["n"],
                     "registeredRoundsTotal": pins["batch"]["n"],
                     "complete": True},
        "seal": {"verified": True, "manifestFailures": [], "chainFailure": None},
        "cell": {"model": pins["codex"]["model"], "cli": pins["codex"]["version"],
                 "binarySha256": pins["codex"]["binarySha256"],
                 "mirrorSha256": None, "goldenSha256": None,
                 "preregistrationSha256": None,
                 "arms": {arm: {"perturbation": blocks[arm]["perturbation"],
                                "tLow": blocks[arm]["thresholds"]["tLow"],
                                "tHigh": blocks[arm]["thresholds"]["tHigh"],
                                "policySha256": None, "promptSha256": None,
                                "familySha256": None}
                          for arm in fixtures.ARMS}},
        "arms": blocks,
        "crossArm": {"invalidCodes": {},
                     "validCounts": {arm: blocks[arm]["population"]["valid"]
                                     for arm in fixtures.ARMS},
                     "validCountSpread": 0, "validCountCaution": False},
        "verdicts": verdicts,
        "runs": [],
    }


def test_the_rendered_tables_carry_the_surfaces_round_three_added(arm_blocks,
                                                                  pins):
    """`RATES.md` is the scorer's rendering, so a member computed and never
    rendered is a member no reader sees: §4.6's reading and S5 branch, §5.3
    (ii)'s arm-D outcome, the narrowed authoring-empty count beside
    `coveredNothing`, and S3's named denominator all have to reach the page.
    """
    blocks = {arm: arm_blocks(arm, PERFECT) for arm in fixtures.ARMS}
    blocks["E"] = arm_blocks("E", PLACEMENT_COLLAPSE)
    # Arm D at the shape §5.3 (ii) predicts: HIGH under its own family and its
    # records NOT at the old edges. The default old-edge coverage is the arm's
    # own, which is right for the four arms keyed at (40, 70) and wrong for D —
    # and a D reading HIGH under both keyings is D-INDETERMINATE, not the first
    # outcome (round 4, finding 6).
    blocks["D"] = arm_blocks("D", PERFECT, (), D_OLD_EDGES_GONE)
    verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"], True, True)
    page = score_rates.render_markdown(_renderable(blocks, verdicts, pins))
    assert "| arm | N | I_X | V_X | rho_X = I_X/N | 95% CI | authoring-empty | " \
           "covered nothing | caution |" in page
    assert "coverage breadth (S3)" in page and "never executed), mean" in page
    assert "§4.6's reading of arm E (S1 placement against S5 labels): " \
           "**PLACEMENT collapse**" in page
    assert "| arm | S5 label accuracy | branch (§4.6) |" in page
    assert "| A | 1.0000 (H 30 / Q 0) | at the ceiling |" in page
    assert "### Arm D's registered outcome (§5.3 (ii))" in page
    assert "**COVERAGE-FOLLOWS-THE-NUMBERS**" in page
    assert "**CONFIRMED**" in page
    # Every markdown table on the page is rectangular: a column added to a
    # header and not to its rows is how a rendering drifts silently. Rows
    # carrying an ESCAPED pipe are skipped — `|H|/(|H|+|Q|)` is one cell in
    # markdown and seven to a splitter that reads `|` literally, and the
    # splitter is the fixtures' table reader, not the page.
    for header, rows in fixtures.markdown_tables(page):
        for row in rows:
            if any("\\" in cell for cell in row):
                continue
            assert len(row) == len(header), (header, row)


# --- C6's credential evidence, as two booleans ------------------------------

def test_a_string_credential_flag_is_isolation_unproven(pins, study):
    """Round 3, finding 18: §6 C6 requires `credentialRemoved` exactly when
    `credentialCopied`, and the check coerced the copy flag with `bool()`.
    `bool("false")` is True, so a slot recording the STRING "false" beside
    `credentialRemoved: true` agreed with itself and was admitted — a live
    credential on disk, recorded as removed, in a valid run's denominator.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        # The reviewer's own case, verbatim: a string that is truthy and reads
        # as its own opposite.
        specs[2] = {"call": {"credentialCopied": "false",
                             "credentialRemoved": True}}
        # And the shape a coercion also lets through in the other direction: an
        # integer 1 is not a boolean either.
        specs[3] = {"call": {"credentialCopied": 1, "credentialRemoved": 1}}
        population.build(specs)
        results = population.score_runs()
        for slot in (("A", "run-001"), ("D", "run-001")):
            row = results["byKey"][slot]
            assert row["code"] == "isolation-unproven", slot
            assert "two booleans" in row["detail"]
            assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
        # The honest slots in the same batch record two real booleans and are
        # admitted, so the check refuses a shape and not the fixture.
        assert results["byKey"][("B", "run-001")]["valid"]
        assert results["byKey"][("C", "run-001")]["valid"]
    finally:
        shutil.rmtree(root, True)


# --- malformed slot evidence: one slot's refusal, never the score's end ------

def test_a_malformed_call_identity_member_refuses_its_own_slot(pins, study):
    """Round 5, finding 6: a slot recording `startedAt: []`.

    `session_reuse()` runs over the whole population BEFORE any slot is
    admitted, and it put arbitrary `CALL.json` member values in a dict key. That
    slot raised `TypeError: unhashable type: 'list'` out of a population-level
    pass with no per-slot catch, so NOTHING was scored — in any arm — and §3.3's
    promise that malformed slot evidence becomes that slot's own refusal was not
    kept. The value is checked now instead of hashed, and the slot is refused
    `call-unreadable` (`score_rates.call_identity_defect()` says why that code
    and not `scorer-error`).

    The malformed slot's OTHER identity evidence still holds the population to
    cross-slot uniqueness: arm E's slot here carries arm A's session id, and it
    is refused `session-reused` as the later slot on the registered schedule. A
    fix that simply dropped an unreadable slot out of the uniqueness pass would
    have handed a copied slot a way to stop being a copy.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        shared = fixtures.SESSION_ID % 777
        specs = [{} for _ in range(5)]
        # Registered call order, first round: B, C, A, D, E.
        specs[2] = {"call": {"startedAt": []}, "session_id": shared}
        specs[4] = {"session_id": shared}
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("A", "run-001")]
        assert row["code"] == "call-unreadable"
        assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
        assert "startedAt" in row["detail"]
        # The score exists at all, which is the finding: every other slot in
        # every other arm was scored, and two of them are valid runs.
        assert len(results["runs"]) == 5
        assert results["byKey"][("E", "run-001")]["code"] == "session-reused"
        for slot in (("B", "run-001"), ("C", "run-001"), ("D", "run-001")):
            assert results["byKey"][slot]["valid"], slot
        # The population pass keeps what it can read of the malformed slot: the
        # session bytes and the session id are still published to the
        # uniqueness check, and only the unreadable member is dropped.
        identity = score_rates.slot_identity(
            os.path.join(population.arms_root, "A", "authoring", "run-001"))
        assert identity["callIdentity"] is None
        assert identity["sessionSha256"] and identity["sessionId"] == shared
    finally:
        shutil.rmtree(root, True)


def test_the_identity_guard_is_about_the_registered_type_not_about_hashing(pins):
    """The same check on the shapes a crash would never have found: an integer
    start clock and an object working directory are both hashable, so the old
    code took them into the uniqueness comparison as if they were the strings
    §3.3 registers. A slot whose own identity cannot be read is not evidence of
    which call produced it, whatever Python can do with the value."""
    honest = {"startedAt": "2026-08-07T09:00:00Z", "cwd": "/tmp/scratch",
              "home": "/tmp/home"}
    assert score_rates.call_identity_defect(honest) is None
    # Absent members are not malformed ones: a slot that records none of the
    # three has no identity to compare and is refused, if at all, by the check
    # that owns the member (`home` is `isolation-unproven`'s).
    assert score_rates.call_identity_defect({}) is None
    for member, value in (("startedAt", 1723), ("cwd", {"path": "/tmp"}),
                          ("home", ["/tmp/home"]), ("startedAt", True)):
        defect = score_rates.call_identity_defect(dict(honest, **{member: value}))
        assert defect is not None and member in defect, (member, value)
    assert score_rates.CALL_IDENTITY_MEMBERS == ("startedAt", "cwd", "home")


def test_an_undecodable_completion_is_completion_unreadable(pins, study):
    """Round 5, finding 7: §3.3 registers `completion-unreadable` as reachable,
    and no run could be given it.

    The transcript binding reads `completion.txt` to check it against the
    transcript's last assistant message, and that read is what a completion of
    invalid UTF-8 fails first. The decode raised a `UnicodeDecodeError` — a
    `ValueError` — which `admit()` catches beside the ported gate's own
    refusals, so the run scored `transcript-refused`: the pipeline-invalid
    histogram named the transcript for a fact about the completion file.

    The bytes below are written BEFORE the seal, so the slot is sealed over what
    it holds and the refusal is about the completion and not about the manifest.
    """
    def undecodable(slot):
        with open(os.path.join(slot, "completion.txt"), "wb") as handle:
            handle.write(b'[{"caseId": "\xff\xfe-not-utf-8"}]')

    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        specs[3] = {"mutate": undecodable}          # arm D's first slot
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("D", "run-001")]
        assert row["code"] == "completion-unreadable"
        assert row["code"] != "transcript-refused"
        assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
        assert "not decodable UTF-8" in row["detail"]
        # The seal is intact, so nothing here is the §2.9 alteration case.
        assert results["seal"]["verified"]
        for slot in (("A", "run-001"), ("B", "run-001"), ("C", "run-001"),
                     ("E", "run-001")):
            assert results["byKey"][slot]["valid"], slot
    finally:
        shutil.rmtree(root, True)


# --- C5's population rules the fixtures stand on ----------------------------

def test_the_scoring_refuses_before_it_reads_a_slot(pins_path, study):
    """§6 C5 / §2.10: the preconditions bind the study's own committed
    artifacts — the ported bytes, the registered interpreter, the golden pin
    and the freeze digest — and three of those are `null` in the registry until
    their registered moments arrive (§3.2, §2.10 [D-20]).

    So no population, fixture or real, can be scored through the registered
    interface until the capture is taken and the freeze is recorded, and the
    fixtures above enter `score()`'s sequence at the line after this gate.
    """
    with pytest.raises(score_rates.ScoreError):
        score_rates.verify_preconditions(pins_path, score_rates.REGISTERED_ARMS,
                                         score_rates.REGISTERED_GOLDEN)


def test_the_population_root_and_the_registry_are_derived_not_supplied():
    """[D-23]: there is no `--slots`, and the canonical `arms/` root and the
    registry of record are both resolved from the harness's own location. A
    supplied root could be a copy with a slot removed or a duplicated arm, and
    every per-slot check would still pass."""
    assert score_rates.SCORE_FLAGS == ("--emit-records",)
    assert "--slots" in score_rates.WITHDRAWN_FLAGS
    assert "--pins" in score_rates.WITHDRAWN_FLAGS
    assert score_rates.REGISTERED_ARMS == os.path.join(STUDY, "arms")
    assert score_rates.REGISTRY_OF_RECORD == os.path.join(STUDY, "harness",
                                                          "PINS.json")


def test_the_declared_shortfall_the_driver_writes_is_the_one_the_scorer_reads():
    """§6 C5 rule 5: when a shortfall is declared, the declared prefix equals
    the ledger's prefix, slot for slot — the scorer's own check, over the
    declaration the DRIVER writes.

    The two modules implement one registered rule, so they have to name the
    same member: §2.8 registers the declaration's contents ("the exact
    completed prefix of the registered schedule") and not its JSON spelling,
    which is precisely why a test has to hold the writer and the reader
    together. The member names are read off both sources rather than restated.
    """
    read = set()
    for node in ast.walk(ast.parse(_source(score_rates.__file__))):
        if isinstance(node, ast.FunctionDef) and node.name == "check_population":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) \
                        and inner.func.attr == "get" \
                        and isinstance(inner.func.value, ast.Name) \
                        and inner.func.value.id == "shortfall" \
                        and inner.args and isinstance(inner.args[0], ast.Constant):
                    read.add(inner.args[0].value)
    written = set()
    for node in ast.walk(ast.parse(_source(batch.__file__))):
        if isinstance(node, ast.FunctionDef) and node.name == "declare_shortfall":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Dict):
                    written |= {key.value for key in inner.keys
                                if isinstance(key, ast.Constant)}
    assert read, "check_population() reads no member of SHORTFALL.json"
    assert written, "declare_shortfall() writes no SHORTFALL.json members"
    assert read <= written, (
        "batch.py declare_shortfall() writes %r and score_rates.py "
        "check_population() reads %r: a shortfall declared by the driver cannot "
        "satisfy C5 rule 5, so every honest short batch refuses"
        % (sorted(written), sorted(read - written)))


def _source(path: str) -> str:
    with open(path.replace(".pyc", ".py"), "rb") as handle:
        return handle.read().decode("utf-8")
