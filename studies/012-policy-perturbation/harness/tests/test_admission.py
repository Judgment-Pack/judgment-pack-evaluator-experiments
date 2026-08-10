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

Three round-6 dispositions land here too, each a code that named no run or a
refusal that was not one:

  * **finding 5** — an absent or `null` identity member is `call-unreadable`,
    over a sealed population and at the guard itself;
  * **finding 7** — an array the ported compiler's strict decoder refuses is
    `compile-refused` and not §3.3's authoring-empty row, with a no-array
    completion beside it as the control;
  * **finding 8** — a malformed ledger record refuses the whole scoring at the
    read, and the registered command reports a refusal rather than a traceback.

Nothing here touches the committed tree, reaches a network or runs a CLI.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import shutil

import pytest

import batch
import fixtures
import records_compile
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
#
# S10 is RAW (round 10, finding 7) — label irrelevant, exactly as S1 is — so for
# arms A, B, C and E, which all carry arm A's own FAMILY.json, this table is
# EXPECTED_PLACEMENT_K above and not EXPECTED_PRIMARY_K. Arm E's class 2 is where
# that shows: the mislabelled record placed inside the class counts here. Arm D's
# row is unchanged and so are the other three columns, because those corpora
# quarantine nothing (q = 0 in EXPECTED_CENSUS below), and where Q is empty the
# raw and the label-filtered answers coincide.
EXPECTED_OLD_EDGE_K = {
    "A": [1, 1, 1, 1, 1, 1],
    "B": [2, 2, 2, 2, 2, 2],
    "C": [2, 2, 2, 2, 2, 2],
    "D": [0, 0, 0, 2, 2, 0],
    "E": [0, 1, 1, 1, 1, 0],
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


def test_two_slots_sharing_MALFORMED_session_bytes_lose_the_LATER_one(pins, study):
    """Round 7, finding 5: the copy that used to stop being a copy by being
    unreadable.

    §3.3 defines `session-reused` on "the slot's `session.jsonl` BYTES, session
    id, or the identifying members of its `CALL.json`" — and the bytes need no
    parser. `slot_identity()` computed the digest and parsed the transcript
    inside ONE `try`, so a session that is not JSON discarded the digest with
    the parse, and two slots holding byte-identical malformed transcripts were
    each refused `transcript-refused`: two copies of one call, both counted as
    two separate failures, with nothing recording that they were the same bytes.

    The precedence is §3.3's own table order, which `admit()` evaluates in:
    `session-reused` sits above `transcript-refused` in it, and `admit()`
    returns the reuse before it runs the transcript binding. So the later slot
    is named a COPY even though its transcript would also refuse — the more
    exact statement about why it is out of the denominator.

    The mutation runs before the seal, so both slots are sealed over the bytes
    they hold and the seal is not what this fixture is about.
    """
    malformed = b'{"type": "session_meta", "payload": {"id": "s-1"\n'

    def break_session(slot: str) -> None:
        with open(os.path.join(slot, "session.jsonl"), "wb") as handle:
            handle.write(malformed)

    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        # Registered call order, first round: B, C, A, D, E.
        specs = [{} for _ in range(5)]
        specs[0] = {"mutate": break_session}                # arm B, index 1
        specs[4] = {"mutate": break_session}                # arm E, index 5
        population.build(specs)
        results = population.score_runs()
        assert results["seal"]["verified"] is True
        earlier = results["byKey"][("B", "run-001")]
        later = results["byKey"][("E", "run-001")]
        assert earlier["globalIndex"] < later["globalIndex"]
        assert earlier["code"] == "transcript-refused"
        assert later["code"] == "session-reused"
        assert "share the retained transcript bytes" in later["detail"]
        assert score_rates.CODE_PARTITION[later["code"]] == "pipeline-invalid"
        # The identity itself: the digest survives the parse failure, and only
        # the parsed members are null.
        identity = score_rates.slot_identity(
            os.path.join(population.arms_root, "B", "authoring", "run-001"))
        assert identity["sessionSha256"] == \
            "sha256:" + hashlib.sha256(malformed).hexdigest()
        assert identity["sessionId"] is None
        assert identity["callIdentity"] is not None
        # The three slots that were left alone are still valid, so the fixture
        # is about these two and not about a scoring that refused everything.
        for key in (("C", "run-001"), ("A", "run-001"), ("D", "run-001")):
            assert results["byKey"][key]["valid"], key
    finally:
        shutil.rmtree(root, True)


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

    S10 is raw here as everywhere (round 10, finding 7), and this fixture's
    answer does not depend on that: arm D's corpora quarantine no record, so
    the raw and the label-filtered readings coincide. The reading that DOES
    depend on it is the next test's.
    """
    _population, _specs, results = scored
    row = results["byKey"][("D", "run-001")]
    assert row["oldEdgeClasses"] == fixtures.FULL_OLD_EDGE_FROM_D == [3, 4]
    for arm in fixtures.ARMS:
        assert [entry["oldEdge"]["count"] for entry in results["arms"][arm]["classes"]] \
            == EXPECTED_OLD_EDGE_K[arm], arm
    for index in score_rates.NARROW_NUMERIC_CLASSES:
        assert results["arms"]["D"]["classes"][index]["oldEdge"]["count"] == 0


def test_old_edge_cross_scoring_sees_a_record_the_arms_own_mirror_quarantines(
        pins, study):
    """Round 10, finding 7: S10 is placement, so it is LABEL IRRELEVANT.

    The scorer intersected arm A's predicates with H — the records this arm's
    own mirror labels correctly — which made the one shape §5.3 (ii)'s second
    outcome names invisible to the only endpoint registered to see it. An arm D
    that reproduced 40 and 70 *and labelled by them* has every such record
    quarantined under its own (45, 72) mirror: old class 2 was unreachable that
    way altogether and old classes 0 and 1 reachable only through records that
    handle personal data, a nuisance variable this study never registered.

    The corpus below is exactly that arm D: three records at the baseline's
    edges, labelled by the baseline's rule. Raw, it reaches five of arm A's six
    classes; under the H filter it reached one, and that one only because
    `clear` at 39.5 is `clear` under both pairs. It runs through `score_run()`
    and not through the synthetic-row helper, because the helper takes an
    old-edge class list directly and would exercise no filter at all.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        # Registered call order, first round: B, C, A, D, E.
        specs = [{} for _ in range(5)]
        specs[3] = {"answer": fixtures.completion(fixtures.old_labelled_records(
            *fixtures.arm_pair(population.arms_root, "A")))}
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("D", "run-001")]
        assert row["valid"] and row["accepted"] == 3
        # Two of the three are Q under D's own mirror — the placed-and-old-
        # labelled records — and the fixture is worthless if they are not.
        assert row["h"] == 1 and row["q"] == 2
        assert row["oldEdgeClasses"] == fixtures.OLD_LABELLED_FROM_D \
            == [0, 1, 2, 3, 5]
        # The finding itself, frozen: the same corpus under the pre-fix
        # expression — arm A's predicates intersected with H — published class
        # 5 alone, and four of the five were lost. Recomputed here with the
        # scorer's own two functions rather than asserted from memory, so the
        # counterfactual is a computation and not a claim about an old commit.
        accepted = {record["caseId"]: record
                    for record in results["recordsByArm"]["D"]["run-001"]}
        definition = population.definitions()["D"]
        high, _quarantine = score_rates.split_records(accepted,
                                                      definition["tLow"],
                                                      definition["tHigh"])
        assert [entry["index"] for entry in definition["oldEdgeClasses"]
                if score_rates.class_members(accepted, high,
                                             entry["predicate"])] \
            == fixtures.OLD_LABELLED_FROM_D_UNDER_THE_H_FILTER == [5]
        # And the arm's OWN family is untouched by any of this: at (45, 72)
        # only the 70 lands in a class of D's, and it is quarantined there.
        assert row["coveredClasses"] == [] and row["rawClasses"] == [3]
    finally:
        shutil.rmtree(root, True)


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


def test_a_symlink_added_after_the_seal_breaks_the_seal(pins, study):
    """Round 7, finding 3: the entry that used to pass the seal and then buy a
    denominator change.

    Both manifest implementations listed regular files only, so a symlink
    created after `seal_slot()` left the recomputed list identical, the three
    bindings holding and `verify_seal()` returning None — and §3.3's lstat-first
    rule then scored that slot `slot-symlink`, moving it out of `V_X` and into
    `I_X` with `sealed` still true. §2.9 registers that exact outcome as the one
    a seal exists to prevent: "It is *not* handled by moving the slot into
    `V_X`'s complement, which would let an alteration buy exactly the
    denominator change that produces the verdict."

    The seal now covers every ENTRY, so the addition breaks it and §2.9's real
    consequence follows — the WHOLE batch is unresolved, every level verdict is
    `UNRESOLVED-BY-DESIGN` and no contrast is reported, so the alteration buys
    no verdict at all. What it does NOT do is take the slot's own §3.3 code
    away: the tree really does hold a symlink, `slot-symlink` is a registered
    per-slot outcome, and §3.3's partition table (which
    `test_partition_parity.py` diffs against the scorer's) is not this fixture's
    to withdraw. The seal is what makes that code cost nothing.

    The control is the same population without the symlink: it seals, and the
    difference between the two scorings is the whole confirmatory surface.
    """
    def add_symlink(slot: str) -> None:
        os.symlink("stdout.raw", os.path.join(slot, "stdout.link"))

    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        specs[2] = {"break_seal": add_symlink}              # arm A's run-001
        population.build(specs)
        results = population.score()
        assert results["seal"]["verified"] is False
        assert results["seal"]["chainFailure"] is None, (
            "the chain must still verify: this fixture is about the MANIFEST")
        failures = results["seal"]["manifestFailures"]
        assert [(entry["arm"], entry["slot"]) for entry in failures] \
            == [("A", "run-001")]
        assert "not the bytes it was sealed over" in failures[0]["detail"]
        # The consequence is the WHOLE batch's, asserted with `complete` held
        # true so the unresolved verdict is the SEAL's and not the stopping
        # rule's — the same way the fixture above separates the two.
        verdicts = score_rates.compute_verdicts(
            results["arms"], results["trials"], True,
            results["seal"]["verified"])
        assert verdicts["resolved"] is False
        assert verdicts["contrasts"] is None
        for arm in fixtures.ARMS:
            for endpoint in score_rates.LEVEL_ENDPOINTS:
                assert set(verdicts["levels"][arm][endpoint]) == \
                    {score_rates.UNRESOLVED}
        assert verdicts["decisionRow"]["row"] == 1
        assert "manifest" in verdicts["unresolvedReason"]
        # The slot keeps its own §3.3 code, and the code buys nothing: with the
        # batch unresolved there is no verdict for a denominator to produce.
        assert results["byKey"][("A", "run-001")]["code"] == "slot-symlink"
    finally:
        shutil.rmtree(root, True)
    # The control: the same population, no symlink, seals.
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        assert population.score_runs()["seal"]["verified"] is True
    finally:
        shutil.rmtree(root, True)


def test_renaming_the_sealed_slot_and_linking_to_it_breaks_the_seal(pins, study):
    """Round 8, finding 4: the move that survived round 7's every-entry seal.

    Round 7 sealed every entry BENEATH the slot and never `lstat`ed the
    `run-NNN` directory itself, so the whole of it could be evaded one level up.
    Rename the sealed slot, plant a symlink at its old path, and every entry the
    manifest lists is byte-identical through the link — the recomputed list
    matched, the list digest matched, the ledger's manifest digest matched, and
    `verify_seal()` returned None. §3.3's lstat-first rule then scored the slot
    `slot-symlink`, moving it out of `V_X` into `I_X` with the batch still
    `sealed`: the denominator change §2.9 registers as the one thing a post-seal
    alteration must never buy, taken at the one path round 7 left unsealed.

    Three assertions, and they are the three §2.9 makes. The seal BREAKS, and
    breaks at the altered slot alone. The population is unchanged — the slot is
    still on disk, still recorded, still counted, and the ledger's chain still
    verifies — so what the move bought is not a smaller denominator but an
    unresolved batch: every level verdict `UNRESOLVED-BY-DESIGN` and no
    contrast, which is a verdict no alteration can aim at. And the honest
    population is the control: undo the move and the same tree seals again, so
    the refusal is the move's and not the fixture's.

    The renamed directory is placed OUTSIDE the arms tree, because a sibling
    inside `authoring/` would be an unexpected entry and the assertion here is
    about the seal rather than about `collect_slots()`.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        honest = population.score_runs()
        assert honest["seal"]["verified"] is True

        slot = population.slots[2]                          # arm A's run-001
        moved = os.path.join(root, "renamed-run-001")
        os.rename(slot, moved)
        os.symlink(moved, slot)
        assert os.path.islink(slot)
        assert os.path.isfile(os.path.join(slot, "CALL.json")), (
            "the link must resolve: the point is that every entry BENEATH the "
            "slot is unchanged through it")

        broken = population.score()
        assert broken["seal"]["verified"] is False
        assert broken["seal"]["chainFailure"] is None, (
            "the chain must still verify: this fixture is about the MANIFEST")
        failures = broken["seal"]["manifestFailures"]
        assert [(entry["arm"], entry["slot"]) for entry in failures] \
            == [("A", "run-001")]
        assert "not the bytes it was sealed over" in failures[0]["detail"]
        # No denominator moved: the slot is present, recorded and counted
        # exactly as it was, and the ledger is the one the driver wrote.
        assert broken["counts"] == honest["counts"]
        assert broken["prefix"] == honest["prefix"]
        assert broken["ledger"] == honest["ledger"]
        assert set(broken["byKey"]) == set(honest["byKey"])
        assert broken["unexpected"] == honest["unexpected"]
        # What it bought instead: the WHOLE batch, with `complete` held true so
        # the unresolved verdict is the SEAL's and not the stopping rule's.
        verdicts = score_rates.compute_verdicts(
            broken["arms"], broken["trials"], True, broken["seal"]["verified"])
        assert verdicts["resolved"] is False
        assert verdicts["contrasts"] is None
        for arm in fixtures.ARMS:
            for endpoint in score_rates.LEVEL_ENDPOINTS:
                assert set(verdicts["levels"][arm][endpoint]) == \
                    {score_rates.UNRESOLVED}
        assert "manifest" in verdicts["unresolvedReason"]
        # The slot keeps its own §3.3 code — the entry at that path really is a
        # symlink — and the code buys nothing, because there is no verdict for a
        # denominator to produce.
        assert broken["byKey"][("A", "run-001")]["code"] == "slot-symlink"

        # The control is the same bytes: remove the link, put the directory
        # back, and the honest population scores.
        os.unlink(slot)
        os.rename(moved, slot)
        restored = population.score_runs()
        assert restored["seal"]["verified"] is True
        assert restored["seal"]["manifestFailures"] == []
        assert restored["counts"] == honest["counts"]
        assert restored["byKey"][("A", "run-001")]["valid"] is True
    finally:
        shutil.rmtree(root, True)


def test_the_seal_records_every_entry_and_the_driver_and_scorer_agree():
    """The seal's own shape, on a tree holding one of everything (round 7,
    finding 3).

    §2.9 as amended records EVERY directory entry: regular files by path, byte
    length and sha256 as before, and every non-regular or non-file entry by path
    and a type marker. Both halves are asserted here — that a symlink, a
    directory and a FIFO each produce a typed row, and that the driver's
    `slot_files()` and the scorer's `manifest_files()` produce the SAME rows,
    because the study's guarantee is that the scorer recomputes what the driver
    sealed rather than agreeing with it by construction.

    An empty directory is in the list too. It carries no bytes, so nothing else
    in the seal would notice it, and "any post-seal addition breaks the seal"
    has to mean any.

    Round 8, finding 4 adds the row for the slot ROOT at path `.`, on both
    sides. The exhaustive `by_path` comparison below is what holds the two
    implementations to the same list: a root row on one side only would fail
    the equality above it as well.
    """
    root = fixtures.throwaway_root()
    try:
        slot = os.path.join(root, "run-001")
        os.makedirs(os.path.join(slot, "nested"))
        os.makedirs(os.path.join(slot, "empty"))
        with open(os.path.join(slot, "stdout.raw"), "wb") as handle:
            handle.write(b"two bytes\n")
        with open(os.path.join(slot, "nested", "inner.raw"), "wb") as handle:
            handle.write(b"")
        os.symlink("stdout.raw", os.path.join(slot, "stdout.link"))
        os.symlink("nowhere", os.path.join(slot, "dangling.link"))
        os.mkfifo(os.path.join(slot, "pipe"))
        rows = batch.slot_files(slot)
        assert rows == score_rates.manifest_files(slot)
        assert batch.files_digest(rows) == score_rates.manifest_digest(rows)
        by_path = {row[0]: row[1:] for row in rows}
        assert by_path == {
            # The slot ROOT, at the one relative path no entry beneath it can
            # take (round 8, finding 4).
            ".": [-1, "type:directory"],
            "stdout.raw": [10, hashlib.sha256(b"two bytes\n").hexdigest()],
            "nested": [-1, "type:directory"],
            "nested/inner.raw": [0, hashlib.sha256(b"").hexdigest()],
            "empty": [-1, "type:directory"],
            "stdout.link": [-1, "type:symlink"],
            "dangling.link": [-1, "type:symlink"],
            "pipe": [-1, "type:fifo"],
        }
        # The FIFO was sealed and never opened: an `open()` on one blocks
        # forever, and a seal that hung would be a worse failure than one that
        # missed the entry.
        assert batch.NON_FILE_LENGTH == score_rates.NON_FILE_LENGTH == -1
    finally:
        shutil.rmtree(root, True)


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
# The same collapse AT §5.1's cut rather than under it (round 10, finding 2):
# `low_threshold(30) == 3`, so an arm that reached each narrow class in three of
# its thirty runs still reads LOW and still confirms. Every other confirming
# fixture uses k = 0, which is why no test ever contradicted §4.6's old row-1
# cell — "none was placed at the boundary" — and why the cell survived nine
# rounds. LOW bounds placement at three of thirty; it does not zero it.
PLACEMENT_COLLAPSE_AT_THE_CUT = [(3, 3), (3, 3), (3, 3), (30, 30), (30, 30),
                                 (3, 3)]
# The same records, still at the boundary, with the labels gone: the primary
# collapses and the placement does not (§4.6's *label collapse*).
LABEL_COLLAPSE = [(0, 30), (0, 30), (0, 30), (30, 30), (30, 30), (0, 30)]
# Round 11, finding 5: `nP < 3` is not `nP = 0`. Classes 0 and 1 place nothing
# at all — a genuine placement collapse — while 2 and 5 place everything and
# label none of it. Row 6 still fires, and the sentence beside it has to be true
# of the arm it fires on.
MIXED_LABEL_COLLAPSE = [(0, 0), (0, 0), (0, 30), (30, 30), (30, 30), (0, 30)]
# …and the floor the new wording names: *not LOW* is not HIGH, so a class the
# row calls "still at the boundary" may be reached in four of thirty runs
# against arm A's thirty. `nP` is 0 here and the records are barely there.
MID_LABEL_COLLAPSE = [(0, 4), (0, 4), (0, 4), (30, 30), (30, 30), (0, 4)]
# Class 4 — the embargo-membership class, which names no numeric boundary —
# goes to zero in arm E: not a literal effect, and row 2 withdraws every other
# reading of arm E before the gate is even consulted. Arm A is PERFECT here, so
# this fixture reads COLLAPSE as well as LOW — which is why it never contradicted
# the round-9 contrast form, and why round 11's two fixtures below are the pair
# that tests the rule rather than the arm.
CLASS4_COLLAPSE = [(30, 30)] * 4 + [(0, 0)] + [(30, 30)]
# Round 11, finding 1: arm A not HIGH on class 4, and the SAME arm E collapse
# there. The registered rule was a §5.2 contrast — arm E reading COLLAPSE on
# class 4 — and a contrast against a baseline that is not HIGH is INDETERMINATE
# and never COLLAPSE, so row 2 stopped firing, rows 4 and 5 were both let
# through beneath it, and this pair published row 5 CONFIRMED on the pre-fix
# bytes for an arm E that reached the embargo class in none of its thirty runs.
# Arms B and C still reach TRACKING on five of six — a class arm A is not HIGH
# on can never be TRACKING, and five is the gate — so the same arm-A shortfall
# that disabled row 2 spends exactly the gate's whole tolerance and nothing
# upstream catches it.
A_NO_EMBARGO = [(30, 30)] * 4 + [(15, 15)] + [(30, 30)]
E_EMBARGO_GONE = [(0, 0), (0, 0), (0, 0), (30, 30), (0, 0), (0, 0)]
# The same failure AT §5.1's two cuts rather than under them, which is the shape
# a real batch produces: arm A reached class 4 in 26 of 30 runs — one short of
# `high_threshold(30) == 27`, L = 0.6928 — and arm E in 3, exactly
# `low_threshold(30)`, U = 0.2653. A single stray miss in the baseline is the
# whole of what it takes.
A_EMBARGO_NEAR_MISS = [(30, 30)] * 4 + [(26, 26)] + [(30, 30)]
E_EMBARGO_AT_THE_CUT = [(0, 0), (0, 0), (0, 0), (30, 30), (3, 3), (0, 0)]
# The degenerate arm E round 9's finding 2 names: the placement collapse and the
# ceiling, class 4 intact — and class 3, the interior review band, gone with the
# four narrow classes. Every accepted record is then a non-sanctioned SY
# registration the mirror labels before it reads the score, so the arm exercised
# neither threshold, and row 5's fifth conjunct is what stops it confirming: arm
# E reads LOW on class 3 (round 10, finding 3 — the conjunct is a level verdict
# on arm E, so it refuses this arm whatever arm A did on that class). Class 4 is
# at (30, 30) here, well clear of the four-of-thirty floor row 2's LOW verdict
# fires below (round 13, finding 2).
INTERIOR_COLLAPSE = [(0, 0), (0, 0), (0, 0), (0, 0), (30, 30), (0, 0)]
# Arm A, HIGH on five classes and NOT on class 3 (round 10, finding 3). The
# round-9 conjunct was a CONTRAST, and a contrast against a baseline that is not
# HIGH is INDETERMINATE and never COLLAPSE — so this arm A plus the degenerate
# arm E above satisfied the conjunct VACUOUSLY and published row 5 CONFIRMED,
# with a `why` asserting arm E "does not read COLLAPSE on class 3" about an arm
# that covered class 3 in none of its thirty runs. Arms B and C still reach
# TRACKING on five of six, because a class arm A is not HIGH on can never be
# TRACKING and five is the gate — so nothing upstream catches it.
A_NO_INTERIOR = [(30, 30), (30, 30), (30, 30), (0, 0), (30, 30), (30, 30)]
# Round 11, finding 3: arm A at §5.1's HIGH cut on class 0 (`k_raw = 27`) with
# ONE of those slots' class-0 records mislabelled, so `k_H = 26` and the primary
# level is MID while the S1 level is HIGH. The placement contrast still
# collapses on that class and the primary contrast does not — which is how
# `nP ≤ nC`, registered as an implication, is separated by a single record. Arms
# B and C still reach TRACKING on five of six, so the gate does not remove the
# case and the batch that shows it publishes CONFIRMED.
A_ONE_MISLABEL = [(26, 27), (30, 30), (30, 30), (30, 30), (30, 30), (30, 30)]

# Each scenario: the pattern per arm, whether the batch is complete and sealed,
# the registered pattern counts, and the row §5.3's table must return.
DECISION_SCENARIOS = (
    {"why": "an incomplete batch: the stopping rule [D-21] returns no verdict",
     "arms": {}, "complete": False, "sealed": True,
     "row": 1, "publishedAs": score_rates.UNRESOLVED},
    {"why": "a seal that does not verify (§2.9), on an otherwise complete batch",
     "arms": {}, "complete": True, "sealed": False,
     "row": 1, "publishedAs": score_rates.UNRESOLVED},
    {"why": "arm E reads LOW on class 4, against a perfect arm A: the reading "
            "the rule was written for, and the one the contrast form also saw",
     "arms": {"E": CLASS4_COLLAPSE}, "complete": True, "sealed": True,
     "row": 2, "publishedAs": "E-DEGRADED-GENERALLY",
     "counts": {"nP": 0, "nC": 0, "nH": 4},
     "embargoLow": True, "embargoContrast": "COLLAPSE"},
    # Round 11, finding 1: the same arm E with arm A not HIGH on class 4. Under
    # the registered contrast form the class-4 contrast read INDETERMINATE, row
    # 2 did not fire, the control gate passed at five of six and this scenario
    # published row 5 CONFIRMED — verified on the pre-fix bytes. Row 2 is arm
    # E's own level now, so it refuses the arm whatever arm A did, and the two
    # scenarios here are a test of the rule rather than of the arm.
    {"why": "arm E reads LOW on class 4 with arm A at MID there: the contrast "
            "form was INDETERMINATE and gated nothing, and arm E's own level "
            "still withdraws every other reading of it",
     "arms": {"A": A_NO_EMBARGO, "E": E_EMBARGO_GONE},
     "complete": True, "sealed": True,
     "row": 2, "publishedAs": "E-DEGRADED-GENERALLY",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling",
     "confirmsR1": True,
     "embargoLow": True, "embargoContrast": "INDETERMINATE"},
    # …and at the two cuts themselves, which is the realistic form: arm A one
    # short of the HIGH cut on class 4 and arm E exactly at the LOW cut. The
    # published `why` names arm A's level, because §5.3 (iv) registers that the
    # withdrawal holds here and the attribution does not.
    {"why": "arm A 26 of 30 on class 4 — one short of the HIGH cut — and arm E "
            "3 of 30, exactly at the LOW cut: row 2 fires on arm E's own level "
            "where the contrast form published CONFIRMED",
     "arms": {"A": A_EMBARGO_NEAR_MISS, "E": E_EMBARGO_AT_THE_CUT},
     "complete": True, "sealed": True,
     "row": 2, "publishedAs": "E-DEGRADED-GENERALLY",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling",
     "confirmsR1": True,
     "embargoLow": True, "embargoContrast": "INDETERMINATE",
     "embargoBaseline": "MID"},
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
    # Round 10, finding 2: the same confirming outcome AT §5.1's LOW cut rather
    # than under it. Three of thirty runs place an accepted record in each
    # narrow class, the level is still LOW, the placement contrast is still
    # PLACEMENT-COLLAPSE and `|Q| = 0` still holds — so row 5 fires with
    # boundary records demonstrably present, which is the concrete fact §4.6's
    # old row-1 cell denied when it said none was placed at the boundary.
    {"why": "arm E placement-collapses on all four at the LOW cut itself — "
            "three of thirty runs per class — with its labels at the ceiling: "
            "the CONFIRMED pattern, with boundary records present",
     "arms": {"E": PLACEMENT_COLLAPSE_AT_THE_CUT},
     "complete": True, "sealed": True,
     "row": 5, "publishedAs": "CONFIRMED",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling"},
    # Round 9, finding 2: the same pattern with class 3 gone too. §4.6 still
    # reads a PLACEMENT collapse at the ceiling — `|Q| = 0` cannot see whether
    # any accepted record exercised a threshold — and row 5's fifth conjunct
    # refuses it, so the table's last row does. The row-5 scenario above keeps
    # class 3 at (30, 30) and keeps confirming, which is what makes this pair a
    # test of the conjunct and not of the pattern.
    {"why": "arm E placement-collapses on all four with its labels at the "
            "ceiling, and class 3 collapses with them: every accepted record "
            "is decided before the score is read, and row 5's class-3 conjunct "
            "refuses it",
     "arms": {"E": INTERIOR_COLLAPSE}, "complete": True, "sealed": True,
     "row": 7, "publishedAs": "INDETERMINATE",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling",
     "confirmsR1": True, "interiorLow": True},
    # Round 10, finding 3: the SAME degenerate arm E, with arm A not HIGH on
    # class 3. Under round 9's contrast form the class-3 contrast was
    # INDETERMINATE rather than COLLAPSE, the conjunct passed vacuously and this
    # scenario published row 5 CONFIRMED — verified on the pre-fix bytes, with
    # arms B and C left at PERFECT and the gate passing at five of six. The
    # conjunct is a level verdict on arm E now, so it refuses the arm whatever
    # arm A did, and the pair above and below this line is a test of that.
    {"why": "the degenerate arm E again, with arm A not HIGH on class 3: the "
            "round-9 contrast was INDETERMINATE and the conjunct passed "
            "vacuously, and arm E's own level refuses it",
     "arms": {"A": A_NO_INTERIOR, "E": INTERIOR_COLLAPSE},
     "complete": True, "sealed": True,
     "row": 7, "publishedAs": "INDETERMINATE",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "PLACEMENT collapse", "labels": "at the ceiling",
     "confirmsR1": True, "interiorLow": True,
     "interiorContrast": "INDETERMINATE"},
    # The same placement collapse with the labels gone: §4.6's SECOND row, the
    # one round 3 found unreachable. "At least one accepted record was
    # mislabelled" is published under §4.6's comprehension-collapse NAME — which
    # names the explanation the reading makes available and not a proposition
    # the rule establishes, and which since round 11 finding 4 says so in the
    # gloss it travels with — and it does not confirm R1, so row 5 does not fire
    # and the table's last row does.
    {"why": "arm E placement-collapses on all four while its S5 labels are "
            "degraded: §4.6's comprehension-collapse reading, and R1 is not "
            "confirmed",
     "arms": {"E": PLACEMENT_COLLAPSE}, "mislabelled": {"E": (3, 4)},
     "complete": True, "sealed": True,
     "row": 7, "publishedAs": "INDETERMINATE",
     "counts": {"nP": 4, "nC": 4, "nH": 0},
     "reading": "comprehension collapse", "labels": "degraded"},
    {"why": "the records are still at the boundary on all four and the labels "
            "are not",
     "arms": {"E": LABEL_COLLAPSE}, "complete": True, "sealed": True,
     "row": 6, "publishedAs": "LABEL-COLLAPSE-ONLY",
     "counts": {"nP": 0, "nC": 4, "nH": 0},
     "reading": "label collapse", "labels": "degraded"},
    # Round 11, finding 5: the two row-6 arms the fixture above never reached.
    # `nP < 3` is a bound and not a zero, and *not LOW* is not HIGH — so the
    # sentence row 6 publishes has to be true of an arm with two genuine
    # placement collapses among the four, and of one whose records are at the
    # boundary in four of thirty runs.
    {"why": "two narrow classes place nothing at all and two lose only their "
            "labels: row 6 fires at nP = 2, not nP = 0",
     "arms": {"E": MIXED_LABEL_COLLAPSE}, "complete": True, "sealed": True,
     "row": 6, "publishedAs": "LABEL-COLLAPSE-ONLY",
     "counts": {"nP": 2, "nC": 4, "nH": 0},
     "reading": "label collapse", "labels": "degraded"},
    {"why": "row 6 with placement MID at four of thirty on every narrow class: "
            "nP = 0 and the records are barely at the boundary",
     "arms": {"E": MID_LABEL_COLLAPSE}, "complete": True, "sealed": True,
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
        # §4.6's reading confirms on its own row; §5.3's row 5 is a conjunction
        # that also reads class 3 (round 9, finding 2), so a scenario can carry
        # a confirming reading and still not be row 5 — and it says so, rather
        # than letting `confirmsR1` be read off the row.
        assert verdicts["reading"]["confirmsR1"] is scenario.get(
            "confirmsR1", scenario["row"] == 5)
    if scenario.get("interiorLow"):
        # The conjunct fired for its own reason, and the reason is arm E's own
        # LEVEL (round 10, finding 3) — not the contrast against arm A, which
        # is INDETERMINATE rather than COLLAPSE in the scenario where arm A is
        # not HIGH on class 3 and which therefore refused nothing there. The
        # published `why` says which conjunct refused the row.
        assert verdicts["levels"]["E"]["primary"][score_rates.INTERIOR_CLASS] \
            == "LOW"
        assert "reads LOW on class %d" % score_rates.INTERIOR_CLASS \
            in row["why"]
        if "interiorContrast" in scenario:
            # …and the contrast the round-9 form read is named, so the vacuity
            # is a stated fact of the fixture rather than a claim in a comment.
            interior = {entry["index"]: entry for entry in
                        verdicts["contrasts"]["E"]}[score_rates.INTERIOR_CLASS]
            assert interior["contrast"] == scenario["interiorContrast"]
    if scenario.get("embargoLow"):
        # Round 11, finding 1: row 2 fired for its own reason too, and the
        # reason is arm E's own LEVEL on class 4 — not the contrast against arm
        # A, which is INDETERMINATE rather than COLLAPSE wherever arm A is not
        # HIGH there and which therefore withdrew nothing in the two scenarios
        # that publish CONFIRMED on the pre-fix bytes. The published `why` names
        # both levels, because §5.3 (iv) registers that the withdrawal holds on
        # arm E's level alone while the attribution needs the baseline.
        embargo = score_rates.EMBARGO_CLASS
        assert verdicts["levels"]["E"]["primary"][embargo] == "LOW"
        assert "arm E reads LOW on class %d" % embargo in row["why"]
        assert "arm A reads %s there" \
            % verdicts["levels"]["A"]["primary"][embargo] in row["why"]
        if "embargoContrast" in scenario:
            contrast = {entry["index"]: entry for entry in
                        verdicts["contrasts"]["E"]}[embargo]
            assert contrast["contrast"] == scenario["embargoContrast"]
        if "embargoBaseline" in scenario:
            assert verdicts["levels"]["A"]["primary"][embargo] \
                == scenario["embargoBaseline"]
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


def test_decision_row_refuses_contrasts_without_the_levels_row_five_reads(
        arm_blocks, pins):
    """Round 10, finding 3: row 5's fifth conjunct is a LEVEL verdict on arm E,
    so `decision_row()` needs the levels as well as the contrasts.

    A caller that supplied one and not the other would silently lose the
    conjunct — which is exactly how the round-9 contrast form lost it, by
    reading a class-3 verdict that goes INDETERMINATE whenever arm A is not
    HIGH. Refused rather than downgraded, in the same shape as the §4.6 reading
    guard beside it: a caller error is not a data condition.
    """
    blocks = {arm: arm_blocks(arm, PERFECT if arm != "E" else PLACEMENT_COLLAPSE)
              for arm in fixtures.ARMS}
    verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"], True,
                                            True)
    arguments = (True, True, verdicts["contrasts"], verdicts["gate"],
                 verdicts["patternCounts"])
    # The whole call is what confirms; each half alone refuses.
    assert score_rates.decision_row(*arguments, verdicts["reading"],
                                    verdicts["levels"])["row"] == 5
    with pytest.raises(score_rates.ScoreError) as caught:
        score_rates.decision_row(*arguments, verdicts["reading"])
    assert type(caught.value) is score_rates.ScoreError
    assert "no §5.1 levels" in str(caught.value)
    assert "class %d" % score_rates.INTERIOR_CLASS in str(caught.value)
    with pytest.raises(score_rates.ScoreError) as caught:
        score_rates.decision_row(*arguments, None, verdicts["levels"])
    assert "no §4.6 reading" in str(caught.value)


def test_rows_four_and_five_cannot_both_hold(arm_blocks, pins):
    """§5.3's own registered note: `k_H ≤ k_raw` per class, so a class with E's
    primary HIGH has E's placement HIGH too and cannot be a placement collapse.
    With four classes, `nH ≥ 3` and `nP ≥ 3` are incompatible — and the order
    is stated anyway, because a decision table with an unreachable ambiguity is
    still a decision table with an ambiguity.

    That note reads arm E's own two endpoints and is arm-A-independent, which is
    why it survives round 11's finding 3. The second assertion here did not: it
    was `nP <= nC`, and every iteration made arm A PERFECT, so the fixture
    supplied the only premise that assertion could fail without. Arm A is
    carried over both patterns now — one at the ceiling, one taxed by a single
    mislabelled record — and what is asserted is the implication that is true:
    a placement collapse carries the primary collapse on the classes where arm A
    reads HIGH on the PRIMARY. The test below is the class the taxed arm A
    removes from that premise.
    """
    exercised = skipped = 0
    for baseline in (PERFECT, A_ONE_MISLABEL):
        for pattern in (PERFECT, PLACEMENT_COLLAPSE, LABEL_COLLAPSE, HALF):
            blocks = {arm: arm_blocks(arm, PERFECT if arm != "E" else pattern)
                      for arm in fixtures.ARMS}
            blocks["A"] = arm_blocks("A", baseline)
            verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"],
                                                    True, True)
            counts = verdicts["patternCounts"]
            assert not (counts["nH"] >= score_rates.PATTERN_MINIMUM
                        and counts["nP"] >= score_rates.PATTERN_MINIMUM)
            # …and the placement contrast implies the primary one on a class
            # where arm A reads HIGH on the primary, which is the whole of what
            # `k_H ≤ k_raw` gives (round 11, finding 3).
            e_rows = {row["index"]: row for row in verdicts["contrasts"]["E"]}
            for index in score_rates.NARROW_NUMERIC_CLASSES:
                if (e_rows[index]["placementContrast"]
                        != score_rates.PLACEMENT_CONTRAST_TABLE[0][1]):
                    continue
                if verdicts["levels"]["A"]["primary"][index] == "HIGH":
                    exercised += 1
                    assert (e_rows[index]["contrast"]
                            == score_rates.CONTRAST_TABLE[0][1])
                else:
                    skipped += 1
    # The premise is neither vacuous nor universal: seven classes across the
    # eight batches satisfy it, and the one the taxed baseline removes is the
    # one the old unconditional assertion was wrong about.
    assert (exercised, skipped) == (7, 1)


def test_the_placement_contrast_does_not_imply_the_primary_one(arm_blocks, pins):
    """Round 11, finding 3: `k_H ≤ k_raw` orders each arm's OWN two endpoints,
    so PLACEMENT-COLLAPSE carries COLLAPSE only where arm A reads HIGH on the
    PRIMARY too. §5.2 registered the implication unconditionally until this
    round, and one mislabelled record in one of arm A's thirty slots separates
    the two counts.

    Nothing upstream removes the case: arm A is HIGH on the other five classes,
    so arms B and C still reach TRACKING on five of six, the control gate passes
    and the batch publishes decision row 5 CONFIRMED with `nP` ABOVE `nC`. The
    scorer is right and the sentence was wrong — no verdict here is miscomputed,
    and none is repaired by moving a threshold (§5's opening).
    """
    blocks = {arm: arm_blocks(arm, PERFECT if arm != "E" else PLACEMENT_COLLAPSE)
              for arm in fixtures.ARMS}
    blocks["A"] = arm_blocks("A", A_ONE_MISLABEL)
    verdicts = score_rates.compute_verdicts(blocks, pins["batch"]["n"],
                                            True, True)
    # The baseline's own two endpoints separate on class 0 and nowhere else.
    assert verdicts["levels"]["A"]["placement"][0] == "HIGH"
    assert verdicts["levels"]["A"]["primary"][0] == "MID"
    assert verdicts["levels"]["A"]["primary"][1:] == ["HIGH"] * 5
    rows = {row["index"]: row for row in verdicts["contrasts"]["E"]}
    assert (rows[0]["placementContrast"]
            == score_rates.PLACEMENT_CONTRAST_TABLE[0][1])
    assert rows[0]["contrast"] == score_rates.CONTRAST_TABLE[2][1]
    counts = verdicts["patternCounts"]
    assert counts == {"nP": 4, "nC": 3, "nH": 0}
    assert counts["nP"] > counts["nC"]
    # …and the batch that shows it confirms, so this is not a corner the
    # decision table removes before anybody reads the two counts.
    assert verdicts["gate"]["passed"] is True
    assert verdicts["decisionRow"]["row"] == 5
    assert verdicts["decisionRow"]["publishedAs"] == "CONFIRMED"


# --- §5.3 (ii)'s three outcomes for arm D, at known integers ----------------
#
# Arm D's own-keyed pattern when its narrow numeric classes collapse under its
# OWN family, and the two S10 old-edge patterns that separate the three
# outcomes: records at the old edges (40, 70), or at neither pair, or — round
# 11, finding 8 — at D's OWN pair with the labels gone, which reads the same on
# both keyings and is the case row 3's gloss must not claim to exclude.
D_NARROW_COLLAPSE = [(0, 0), (0, 0), (0, 0), (30, 30), (30, 30), (0, 0)]
D_OLD_EDGES_HELD = [30, 30, 30, 30, 30, 30]
D_OLD_EDGES_GONE = [0, 0, 0, 30, 30, 0]
# Round 12, finding 2: arm D's missing equivalent of
# `PLACEMENT_COLLAPSE_AT_THE_CUT`. Every row-3 fixture above sits at k = 0 on
# all four narrow numeric classes on both keyings, which is why no test ever
# contradicted the gloss's "no coverage … and no placement". Here the row fires
# at §5.1's cut instead of under it — classes 0, 1 and 2 reached three times of
# thirty, `low_threshold(30)` exactly — and with narrow class 5 reached in
# EVERY run on both keyings, which the row's three-of-four minimum permits. The
# cell has to be true of this arm too: LOW bounds both keyings, it does not
# zero either.
D_NARROW_COLLAPSE_AT_THE_CUT = [(3, 3), (3, 3), (3, 3), (30, 30), (30, 30),
                                (30, 30)]
D_OLD_EDGES_AT_THE_CUT = [3, 3, 3, 30, 30, 30]
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
    {"why": "no coverage at either pair, at k = 0 on all four narrow numeric "
            "classes: a general degradation, published as one",
     "pattern": D_NARROW_COLLAPSE, "oldEdge": D_OLD_EDGES_GONE,
     "publishedAs": "GENERAL-DEGRADATION",
     "counts": {"newKeyedHigh": 0, "newKeyedLow": 4, "oldKeyedHigh": 0,
                "oldKeyedLow": 4, "tracking": 2, "narrowMinimum": 3,
                "classes": 6}},
    # Round 11, finding 8: the SAME row, the SAME counts — and an arm D whose
    # records are all at its own (45, 72) in every run, mislabelled. The primary
    # is correctly-labelled coverage, so it reads LOW; D's classes are disjoint
    # from arm A's, so S10 reads LOW too. The counts below are identical to the
    # scenario above, which is exactly the point: row 3 cannot tell these two
    # populations apart, so its gloss may not say the records went nowhere.
    {"why": "the labels are gone and the records are at D's own pair: row 3 "
            "again, at counts indistinguishable from the row above",
     "pattern": LABEL_COLLAPSE, "oldEdge": D_OLD_EDGES_GONE,
     "publishedAs": "GENERAL-DEGRADATION",
     "counts": {"newKeyedHigh": 0, "newKeyedLow": 4, "oldKeyedHigh": 0,
                "oldKeyedLow": 4, "tracking": 2, "narrowMinimum": 3,
                "classes": 6}},
    # Round 12, finding 2: row 3 a THIRD time, at §5.1's cut rather than under
    # it and on three of the four narrow classes rather than all four. The two
    # scenarios above are both at k = 0 everywhere, so the row's gloss could
    # say "no coverage" and "no placement" for eleven rounds without a fixture
    # contradicting it. This arm reaches each of classes 0, 1 and 2 three times
    # of thirty on both keyings and class 5 in every run on both, and the row
    # still fires — which is the arm the cell's bound has to be true of.
    {"why": "row 3 at §5.1's cut and on three of the four narrow classes: "
            "classes 0, 1 and 2 reached three times of thirty on both keyings "
            "and class 5 reached in every run on both, so the row fires while "
            "one narrow class reads HIGH on each side",
     "pattern": D_NARROW_COLLAPSE_AT_THE_CUT,
     "oldEdge": D_OLD_EDGES_AT_THE_CUT,
     "publishedAs": "GENERAL-DEGRADATION",
     "counts": {"newKeyedHigh": 1, "newKeyedLow": 3, "oldKeyedHigh": 1,
                "oldKeyedLow": 3, "tracking": 3, "narrowMinimum": 3,
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
                         ids=["%d-%s" % (index, entry["publishedAs"])
                              for index, entry in enumerate(D_SCENARIOS)])
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

    Round 11, finding 8: two scenarios now fire ROW 3 at identical counts from
    populations that are not alike at all — one whose records reached neither
    threshold pair, one whose records all reached D's own and were mislabelled.
    The row is right about both and its gloss was false of the second; the pair
    is fixtured so the sentence cannot drift back.
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
    # Round 11, finding 8: the residual round 10 disclosed, in integers. Row 3
    # fires at the counts above on an arm D whose records ARE at its own (45,
    # 72) — S1 placement HIGH on every narrow numeric class — with the labels
    # gone, so the correctly-labelled primary reads LOW and S10 reads LOW under
    # arm A's disjoint predicates. The row cannot separate this arm from the one
    # above it, which is why its gloss now points at D's own placement rates
    # instead of claiming the records went nowhere.
    if scenario["pattern"] is LABEL_COLLAPSE:
        levels = verdicts["levels"]["D"]
        for index in score_rates.NARROW_NUMERIC_CLASSES:
            assert levels["placement"][index] == "HIGH", index
            assert levels["primary"][index] == "LOW", index
    # Round 12, finding 2: the same row at §5.1's cut, and what the gloss may
    # therefore not call a zero. Three narrow classes are reached three times of
    # thirty on each keying — `low_threshold(30)`, so LOW and not absent — and
    # the fourth is reached in every run on both, which the three-of-four
    # minimum allows. Both halves of the withdrawn "no coverage … no placement"
    # are false of this arm, and the row fires on it all the same.
    if scenario["pattern"] is D_NARROW_COLLAPSE_AT_THE_CUT:
        levels = verdicts["levels"]["D"]
        cut = score_rates.low_threshold(pins["batch"]["n"])
        assert cut == 3
        for index in (0, 1, 2):
            assert levels["primary"][index] == "LOW", index
            assert levels["oldEdge"][index] == "LOW", index
        assert levels["primary"][5] == "HIGH"
        assert levels["oldEdge"][5] == "HIGH"
        assert outcome["row"] == 3
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


# --- §2.8's one UTC calendar day, computed (round 10, finding 9) -------------
#
# The rule is registered — "all 150 slots are begun and completed within one UTC
# calendar day; spilling past midnight is a `DEVIATIONS.md` entry, not a
# stopping rule" — and nothing computed it, while `RESULTS.json`'s `cell` note
# published "one model, one day" and [D-10]'s confirmation sentence rested on
# the same conjunct. The three tests below are the three ways the property
# fails, and NONE refuses: a refusal would convert a registered non-stopping
# deviation into a stopping condition. The published block on an honest
# population is asserted on the writer's own document in
# `test_batch.py::test_the_published_schedule_carries_the_computed_utc_day`.
#
# Round 11, finding 6: TRUNCATION is the third way, and it is the one round 10
# left uncovered — the rule is over all 150 slots, so `complete` is an argument
# and the two tests above it pass True deliberately, to keep proving the reason
# they were written for.


def test_a_batch_that_crosses_midnight_is_published_and_not_refused(pins, study):
    """A slot begun at 23:59:30 and ended at 00:00:12 the next day.

    Both dates are published, `crossedMidnight` is true, one day is NOT
    established — and the slot is a VALID run in its arm's denominator, with
    its coverage counted, which is the point of the test. §2.8 makes this a
    `DEVIATIONS.md` entry and not a stopping rule, so a scorer that refused it
    would destroy a complete batch over a recorded deviation.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        # Registered call order, first round: B, C, A, D, E.
        specs = [{} for _ in range(5)]
        specs[3] = {"call": {"startedAt": "2026-08-07T23:59:30Z",
                             "endedAt": "2026-08-08T00:00:12Z"}}
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("D", "run-001")]
        assert row["utcDates"] == ["2026-08-07", "2026-08-08"]
        # Not refused, not moved out of anything, and still S8's duration.
        assert row["valid"] and row["code"] is None
        assert row["coveredClasses"] == [0, 1, 2, 3, 4, 5]
        assert row["wallClockSeconds"] == 42
        # Completeness supplied DELIBERATELY: this test is about the midnight
        # half, so the False below proves the crossing and not the truncation
        # (round 11, finding 6).
        block = score_rates.utc_day(results["runs"], True)
        assert block["dates"] == ["2026-08-07", "2026-08-08"]
        assert block["slotsWithoutReadableStamps"] == 0
        assert block["crossedMidnight"] is True
        assert block["oneDayEstablished"] is False
    finally:
        shutil.rmtree(root, True)


def test_a_slot_that_stamped_no_clock_withholds_the_one_day_property(pins,
                                                                     study):
    """The other failure, and why the block carries three members and not one
    flag: a slot whose stamps the scorer cannot read.

    `call_identity_defect()` owns `startedAt`, the working directory and the
    isolated home, so a missing `endedAt` is not a refusal — the slot is valid
    and counted, and the wrapper writes `CALL.json` after the call returns, so a
    tail whose wrapper refused at preflight stamps no clock at all. Under a
    single `crossedMidnight` boolean that reads False and looks like compliance.
    Here the dates are published as computed, the undated slot is COUNTED, and
    one day is reported as not established — §2.8's own idiom for a truncated
    batch's transition census.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        specs[3] = {"call": {"endedAt": None}}
        population.build(specs)
        results = population.score_runs()
        row = results["byKey"][("D", "run-001")]
        assert row["valid"] and row["code"] is None
        assert row["utcDates"] == [] and row["wallClockSeconds"] is None
        for slot in (("B", "run-001"), ("C", "run-001"), ("A", "run-001")):
            assert results["byKey"][slot]["utcDates"] == ["2026-08-07"], slot
        # Complete, again deliberately, so the withheld property below is the
        # unreadable stamp and nothing else (round 11, finding 6).
        block = score_rates.utc_day(results["runs"], True)
        assert block["dates"] == ["2026-08-07"]
        assert block["slotsWithoutReadableStamps"] == 1
        # The establishable positive stays False; the withheld negative is what
        # moves. One boolean could not say both.
        assert block["crossedMidnight"] is False
        assert block["oneDayEstablished"] is False
    finally:
        shutil.rmtree(root, True)


def test_a_truncated_batch_establishes_no_one_day_property(pins, study):
    """Round 11, finding 6: the third way, and the one nothing covered.

    Every stamp is readable and every slot is on one date — the two failures
    above are both absent — and the batch is five slots of the registered 150.
    §2.8 registers the rule over all 150 and registers a truncated batch's
    properties as *published as computed, reported as not established*, so the
    date set and the undated count are published and the property is withheld.
    Before this, the same block published `complete: false` and
    `oneDayEstablished: true` eight lines apart in one dict literal.

    `crossedMidnight` deliberately does NOT take the conjunct: a prefix that
    crossed midnight crossed it, and withholding that would hide a recorded
    deviation behind a truncation.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        results = population.score_runs()
        block = score_rates.utc_day(results["runs"], False)
        assert block["dates"] == ["2026-08-07"]
        assert block["slotsWithoutReadableStamps"] == 0
        assert block["crossedMidnight"] is False
        assert block["oneDayEstablished"] is False
        # The same rows over a complete batch establish it, so the prefix is
        # what withheld it and not the population's stamps.
        assert score_rates.utc_day(results["runs"],
                                   True)["oneDayEstablished"] is True
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
    which call produced it, whatever Python can do with the value.

    **This case previously asserted that `{}` has no defect, and that assertion
    enshrined the bug round 6's finding 5 names**: it is corrected here rather
    than accommodated. `call.get()` exempted absent members and JSON `null`
    alike, no later gate owns `startedAt`, and an absent member agrees with
    every other absent one — so the exemption was a hole in §3.3's rule, not a
    narrower reading of it. The registered rule is that all three identifying
    members are PRESENT and are the strings the wrapper wrote.
    """
    honest = {"startedAt": "2026-08-07T09:00:00Z", "cwd": "/tmp/scratch",
              "home": "/tmp/home"}
    assert score_rates.call_identity_defect(honest) is None
    # Absence and `null` are the two spellings of the same missing evidence, and
    # each of the three members answers for itself.
    for member in score_rates.CALL_IDENTITY_MEMBERS:
        absent = dict(honest)
        absent.pop(member)
        defect = score_rates.call_identity_defect(absent)
        assert defect is not None and member in defect, member
        nulled = score_rates.call_identity_defect(dict(honest, **{member: None}))
        assert nulled is not None and member in nulled, member
    assert score_rates.call_identity_defect({}) is not None
    for member, value in (("startedAt", 1723), ("cwd", {"path": "/tmp"}),
                          ("home", ["/tmp/home"]), ("startedAt", True)):
        defect = score_rates.call_identity_defect(dict(honest, **{member: value}))
        assert defect is not None and member in defect, (member, value)
    assert score_rates.CALL_IDENTITY_MEMBERS == ("startedAt", "cwd", "home")


# Two completions the ported compiler's strict decoder refuses and a permissive
# one accepts: the exact boundary `records_compile.extract_array()` names in its
# own docstring — "duplicate object keys and non-JSON constants disqualify a
# candidate". Both hold an ARRAY; neither holds a parseable one.
DUPLICATE_KEY_ARRAY = (fixtures.PREAMBLE
                       + '[{"caseId": "acme-ltd", "caseId": "acme-ltd"}]'
                       + fixtures.TRAILER)
NAN_ARRAY = fixtures.PREAMBLE + '[{"riskScore": NaN}]' + fixtures.TRAILER


def test_an_array_the_compiler_refuses_is_compile_refused_not_authoring_empty(
        pins, study):
    """Round 6, finding 7: `compile-refused` was a registered outcome no run
    could be given, and the runs it should have named were being scored VALID.

    §3.3 registers `compile-refused` as "the compiler failed other than by
    finding no array", and 011 §3.3 registers the line it is the other side of:
    the no-parseable-array refusal is authoring-empty and valid, every other
    compiler error is pipeline-invalid. `extract_array()` catches every decoder
    `ValueError` per candidate, so an array with duplicate object keys and an
    array carrying `NaN` both arrived at the scorer as the no-array
    `CompileError` — and landed in the denominator as authoring outcomes, when
    what failed was the transport of a machine-readable answer.

    The third slot is the control: a completion with no array at all is still
    §3.3's own row, valid and covering nothing, which is what the distinction
    has to leave alone to be a distinction.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        # Registered call order, first round: B, C, A, D, E.
        specs[2] = {"answer": fixtures.COMPLETION_EMPTY}   # arm A: no array
        specs[3] = {"answer": DUPLICATE_KEY_ARRAY}         # arm D
        specs[4] = {"answer": NAN_ARRAY}                   # arm E
        population.build(specs)
        results = population.score_runs()
        for slot, expected in ((("D", "run-001"), "duplicate object keys"),
                               (("E", "run-001"), "non-JSON constant")):
            row = results["byKey"][slot]
            assert row["code"] == "compile-refused", (slot, row["code"])
            assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
            assert not row["valid"], slot
            # A pipeline-invalid run carries no authoring surface at all — the
            # compile never produced one — which is the whole difference from
            # the authoring-empty row it used to be scored as.
            assert "authoringEmpty" not in row, slot
            assert expected in row["detail"], (slot, row["detail"])
        # The control, unmoved: no array is still the partition's valid row.
        empty = results["byKey"][("A", "run-001")]
        assert empty["valid"] and empty["code"] is None
        assert empty["authoringEmpty"] and empty["noParseableArray"]
        assert empty["coveredClasses"] == []
        assert results["seal"]["verified"]
    finally:
        shutil.rmtree(root, True)


def test_the_compile_refusal_boundary_is_the_ported_compilers_own(study):
    """The same rule at the bytes, and the guarantee that the two decoders it is
    drawn between are the PORT's and not a second copy of it.

    `strict_decode_refusal()` differs from `records_compile.extract_array()`'s
    decoder in exactly the hooks that make the port strict, so a change to the
    port's strictness moves this boundary with it rather than leaving the
    scorer deciding `compile-refused` by a rule the compiler no longer has.
    """
    assert score_rates._STRICT_DECODER.object_pairs_hook \
        is records_compile._refuse_duplicate_keys
    assert score_rates._STRICT_DECODER.parse_constant \
        is records_compile._refuse_constants
    for decoder in (score_rates._STRICT_DECODER, score_rates._ARRAY_SHAPE_DECODER):
        assert decoder.parse_int is records_compile.JsonNumber
        assert decoder.parse_float is records_compile.JsonNumber
    # An array the strict decoder refuses, either way it can refuse one.
    for raw in (DUPLICATE_KEY_ARRAY, NAN_ARRAY):
        assert score_rates.strict_decode_refusal(raw) is not None
        with pytest.raises(records_compile.CompileError):
            records_compile.compile_records(raw)
    # …and everything §3.3 leaves on the authoring-empty side: prose, a
    # bracketed aside that opens no array, and an array that never closes.
    for raw in (fixtures.COMPLETION_EMPTY,
                "The office filed [7 of them] and reproduces none.",
                'Here is the list:\n\n[{"caseId": "acme-ltd"'):
        assert score_rates.strict_decode_refusal(raw) is None, raw
        with pytest.raises(records_compile.CompileError):
            records_compile.compile_records(raw)
    # A completion the compiler ACCEPTS reaches neither: the boundary is only
    # consulted where the compile already failed, and it agrees there.
    honest = fixtures.completion(fixtures.full_records(
        *fixtures.arm_pair(os.path.join(study, "arms"), "A")))
    assert records_compile.compile_records(honest)[0]


def test_an_absent_or_null_identity_member_is_call_unreadable(pins, study):
    """Round 6, finding 5, over a sealed population rather than over the guard
    alone: a slot whose `CALL.json` never records `startedAt`, and one that
    records it as JSON `null`, are both `call-unreadable`.

    Neither slot could be refused before. `call.get()` returned `None` for both,
    the guard exempted `None`, and no other gate reads `startedAt` — so an
    independently sealed slot with no start clock scored VALID and entered every
    rate. The two spellings are built differently on purpose: the null is a
    member the writer set, and the absence is the member removed from the file
    BEFORE the seal, so the slot is sealed over what it holds and the refusal is
    about the call record and not about the manifest.
    """
    def drop_started_at(slot):
        path = os.path.join(slot, "CALL.json")
        with open(path) as handle:
            call = json.load(handle)
        del call["startedAt"]
        with open(path, "w") as handle:
            json.dump(call, handle, indent=2)

    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        specs = [{} for _ in range(5)]
        # Registered call order, first round: B, C, A, D, E.
        specs[2] = {"mutate": drop_started_at}      # arm A's first slot
        specs[3] = {"call": {"cwd": None}}          # arm D's first slot
        population.build(specs)
        results = population.score_runs()
        for slot, member in ((("A", "run-001"), "startedAt"), (("D", "run-001"), "cwd")):
            row = results["byKey"][slot]
            assert row["code"] == "call-unreadable", (slot, row["code"])
            assert score_rates.CODE_PARTITION[row["code"]] == "pipeline-invalid"
            assert member in row["detail"], (slot, row["detail"])
            assert not row["valid"], slot
        # The seal covers both mutations, so neither refusal is §2.9's, and the
        # three honest slots of the same batch are still scored.
        assert results["seal"]["verified"]
        for slot in (("B", "run-001"), ("C", "run-001"), ("E", "run-001")):
            assert results["byKey"][slot]["valid"], slot
        # …and the population pass keeps what it can read of each of them: the
        # unreadable identity is dropped and the session evidence is not, so a
        # copy of either slot is still caught by the two members that remain.
        for arm in ("A", "D"):
            identity = score_rates.slot_identity(
                os.path.join(population.arms_root, arm, "authoring", "run-001"))
            assert identity["callIdentity"] is None
            assert identity["sessionSha256"] and identity["sessionId"]
    finally:
        shutil.rmtree(root, True)


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


# --- C5: a malformed ledger refuses, and says so (round 6, finding 8) --------

def test_a_malformed_ledger_record_refuses_the_whole_scoring(pins, study):
    """C5 registers that a malformed ledger refuses the whole scoring through
    the registered path, and `load_ledger()` checked only that `records` was a
    list. `{"records": [null]}` therefore reached `schedule_key()`, which called
    `.get` on `None` and raised a bare `AttributeError` out of a function
    `main()` does not catch: a traceback where the registration promises a
    refusal, and an exit a reader cannot tell from a crashed scorer.

    Each shape below is checked at the READ, before a slot is opened, and each
    refusal names the record and the member. The honest ledger the same
    population wrote is the control — a check that refused everything would
    pass every case here and refuse the study.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        path = os.path.join(population.arms_root, "BATCH.json")
        with open(path) as handle:
            honest = json.load(handle)
        assert score_rates.load_ledger(population.arms_root) == honest["records"]
        first = honest["records"][0]
        no_arm = {key: value for key, value in first.items() if key != "arm"}
        cases = (
            ([None], "is None"),
            (["run-001"], "is 'run-001'"),
            ([[first]], "is ["),
            ([no_arm] + honest["records"][1:], "arm"),
            ([dict(first, round="1")] + honest["records"][1:], "round"),
            ([dict(first, globalIndex=True)] + honest["records"][1:], "globalIndex"),
            ([dict(first, position=None)] + honest["records"][1:], "position"),
        )
        for records, needle in cases:
            with open(path, "w") as handle:
                json.dump(dict(honest, records=records), handle, indent=2)
            with pytest.raises(score_rates.ScoreError) as caught:
                score_rates.load_ledger(population.arms_root)
            assert needle in str(caught.value), (needle, str(caught.value))
            # `main()` catches `ScoreError` and nothing else, so the TYPE of the
            # exception is what separates a refusal from a traceback.
            assert type(caught.value) is score_rates.ScoreError, needle
    finally:
        shutil.rmtree(root, True)


def test_a_ledger_that_is_not_readable_json_refuses_the_whole_scoring(pins, study):
    """Round 7, finding 6: the READ, not just the records.

    Round 6 type-checked every record and left the file itself unguarded, so a
    `BATCH.json` that is not JSON — or that shadows a member with a duplicate
    key, which parses in a permissive reader and not in this one — raised the
    loader's bare `ValueError` out of a `main()` that catches `ScoreError` and
    nothing else. C5 registers a malformed ledger as a refusal of the whole
    scoring through the registered path, and a traceback is not that path.

    The honest ledger the same population wrote is the control, so a check that
    refused everything could not pass this.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        path = os.path.join(population.arms_root, "BATCH.json")
        with open(path) as handle:
            honest = handle.read()
        assert score_rates.load_ledger(population.arms_root)
        for body, needle in ((honest[:len(honest) // 2], "JSON"),
                             ("", "JSON"),
                             ('{"records": [], "records": []}',
                              "duplicate object keys")):
            with open(path, "w") as handle:
                handle.write(body)
            with pytest.raises(score_rates.ScoreError) as caught:
                score_rates.load_ledger(population.arms_root)
            assert needle in str(caught.value), (needle, str(caught.value))
            assert type(caught.value) is score_rates.ScoreError, needle
    finally:
        shutil.rmtree(root, True)


def test_a_shortfall_declaration_that_is_not_an_object_refuses(pins, study):
    """The other half of round 7's finding 6, on §2.8's declaration.

    `SHORTFALL.json` was read with no guard at all: a file that is not JSON
    raised the loader's `ValueError`, and one holding `[]` was not `None`, so
    it passed every test in `terminality()` and reached `check_population()`'s
    `shortfall.get(...)` as an `AttributeError`. Both are malformed population
    records, both are C5 rule 5's, and both now refuse where the registration
    says the scoring refuses.

    A short batch with an honest declaration is the control: it is exactly the
    population every other fixture in this file scores.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        slots = {arm: score_rates.collect_slots(
            score_rates.slots_root(population.arms_root, arm))[0]
            for arm in fixtures.ARMS}
        total = len(population.schedule)
        honest = score_rates.terminality(population.arms_root, slots, total)
        assert isinstance(honest, dict)
        path = os.path.join(population.arms_root, "SHORTFALL.json")
        for body, needle in (("[]", "declaration object"),
                             ('"a short batch"', "declaration object"),
                             ("{not json", "JSON"),
                             ('{"completedSlots": 5, "completedSlots": 5}',
                              "duplicate object keys")):
            with open(path, "w") as handle:
                handle.write(body)
            with pytest.raises(score_rates.ScoreError) as caught:
                score_rates.terminality(population.arms_root, slots, total)
            assert needle in str(caught.value), (needle, str(caught.value))
            assert type(caught.value) is score_rates.ScoreError, needle
        # …and the whole scoring refuses through the same path, which is where
        # the `AttributeError` used to come out.
        with open(path, "w") as handle:
            handle.write("[]")
        with pytest.raises(score_rates.ScoreError):
            population.score_runs()
    finally:
        shutil.rmtree(root, True)


def test_the_registered_command_reports_a_refusal_and_not_a_traceback(monkeypatch,
                                                                      capsys):
    """The other half of finding 8, at `main()`: the registered command turns a
    `ScoreError` into `refused: …` and exit 1, and lets everything else through.

    That asymmetry is why the type matters. The malformed ledger used to raise
    an `AttributeError` from inside `schedule_key()`, and this shows what the
    operator got for it — the second half of this case fails if `main()` ever
    starts swallowing arbitrary exceptions, which would hide a scorer bug behind
    the same word the registration uses for a refusal.
    """
    def refuse(records_dir=None):
        raise score_rates.ScoreError(
            "arms/BATCH.json's record 1 is None and a ledger record is a JSON "
            "object")

    def crash(records_dir=None):
        raise AttributeError("'NoneType' object has no attribute 'get'")

    monkeypatch.setattr(score_rates, "score_registered", refuse)
    assert score_rates.main(["score_rates.py", "score"]) == 1
    assert capsys.readouterr().err.startswith("refused: arms/BATCH.json's record 1")
    monkeypatch.setattr(score_rates, "score_registered", crash)
    with pytest.raises(AttributeError):
        score_rates.main(["score_rates.py", "score"])


# --- C5's population rules the fixtures stand on ----------------------------

def test_the_scoring_refuses_before_it_reads_a_slot(pins_path, study):
    """§6 C5 / §2.10: the preconditions bind the study's own committed
    artifacts — the ported bytes, the registered interpreter, the golden pin
    and the freeze digest — and they are not satisfied in the committed tree
    until their registered moments arrive (§3.2, §2.10 [D-20]).

    So no population, fixture or real, can be scored through the registered
    interface until the capture is taken and the freeze is recorded, and the
    fixtures above enter `score()`'s sequence at the line after this gate.

    Round 10, finding 5: the refusal is NAMED, because an unnamed one was read
    as coverage of something it never reached. What actually stops the scoring
    here is the FIRST precondition the committed tree fails — the golden
    capture is not a file in the tree yet — which is many checks above §6 C7's
    recorded control. The scorer's C7 gate has its own case below, over a
    population that gets past this line.
    """
    with pytest.raises(score_rates.ScoreError) as caught:
        score_rates.verify_preconditions(pins_path, score_rates.REGISTERED_ARMS,
                                         score_rates.REGISTERED_GOLDEN)
    assert "no golden context" in str(caught.value)


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

    The scan walks a SET of readers (round 9, finding 4): `check_population()`
    reads the declaration for C5 rule 5, and `_declares_no_slot_ran()` reads
    three more members of it to admit the empty prefix's absent ledger. A
    misspelling in either one would make every honest short batch — or every
    honest zero-slot batch — refuse, which is the defect this test exists to
    prevent. The set is asserted non-empty at both ends, so a renamed helper
    cannot silently drop out of the scan and leave it passing over nothing.
    """
    readers = {"check_population", "_declares_no_slot_ran"}
    read = {}
    for node in ast.walk(ast.parse(_source(score_rates.__file__))):
        if isinstance(node, ast.FunctionDef) and node.name in readers:
            read[node.name] = _declaration_members(node)
    written = set()
    for node in ast.walk(ast.parse(_source(batch.__file__))):
        if isinstance(node, ast.FunctionDef) and node.name == "declare_shortfall":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Dict):
                    written |= {key.value for key in inner.keys
                                if isinstance(key, ast.Constant)}
    assert set(read) == readers, (
        "score_rates.py defines %r of the declaration's readers %r: a renamed "
        "reader drops out of this scan and takes its members with it"
        % (sorted(read), sorted(readers)))
    for name, members in read.items():
        assert members, "%s() reads no member of SHORTFALL.json" % name
    assert written, "declare_shortfall() writes no SHORTFALL.json members"
    every = set().union(*read.values())
    assert every <= written, (
        "batch.py declare_shortfall() writes %r and score_rates.py's readers "
        "read %r: a shortfall declared by the driver cannot satisfy C5 rule 5 "
        "or admit an empty batch, so every honest short batch refuses"
        % (sorted(written), sorted(every - written)))


def _declaration_members(function: ast.FunctionDef) -> set:
    """The `SHORTFALL.json` members one reader reads, off its own syntax.

    Two shapes, because the two readers are written differently and neither
    should have to be rewritten to be scanned: the literal argument of a
    `shortfall.get("...")`, and — when `.get()` is handed a loop variable —
    the literal names the loop walks. `_declares_no_slot_ran()` checks its
    three integer members in one loop and its three null members in one
    comprehension, and a scan that saw only literal arguments would have read
    nothing there and passed over an empty set.
    """
    literals, variables = set(), set()
    for inner in ast.walk(function):
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) \
                and inner.func.attr == "get" \
                and isinstance(inner.func.value, ast.Name) \
                and inner.func.value.id == "shortfall" and inner.args:
            argument = inner.args[0]
            if isinstance(argument, ast.Constant):
                literals.add(argument.value)
            elif isinstance(argument, ast.Name):
                variables.add(argument.id)
    for inner in ast.walk(function):
        if not isinstance(inner, (ast.For, ast.comprehension)):
            continue
        if not isinstance(inner.target, ast.Name) or inner.target.id not in variables:
            continue
        if isinstance(inner.iter, (ast.Tuple, ast.List)):
            literals |= {element.value for element in inner.iter.elts
                         if isinstance(element, ast.Constant)}
    return literals


# --- §2.8's short prefixes, through score() itself (round 9, finding 4) ------
#
# The driver creates `arms/<X>/authoring/` with that arm's FIRST slot, so a
# batch that dies inside round 1 leaves the arms it never reached with no root
# at all — and a batch that dies before its first slot finished leaves no
# `BATCH.json` either, because the driver writes the ledger inside the run
# loop. §2.8 [D-21] promises that "any incomplete batch, at any round, for any
# reason" is published descriptively, and the scorer refused all five of those
# prefixes. The fixtures concealed it: `build_arms_root()` used to pre-create
# the five authoring roots, so no fixture population was ever the tree a real
# crash leaves.


def _stand_in_registry(root: str, golden: str) -> str:
    """The committed registry, copied beside a fixture population with the
    pins §2.10, §3.2 and §6 C7 leave null until their registered moments: this
    population's own golden capture, the real preregistration's digest, and the
    assent the control ran under.

    Everything else is the committed registry's — N, the slot count, the
    registered call order, the five arms' pinned digests — so the population
    below goes through the REAL `verify_preconditions()` and not a relaxed one.
    """
    with open(score_rates.REGISTRY_OF_RECORD) as handle:
        pins = json.load(handle)
    pins["golden"]["sha256"] = score_rates.file_digest(golden)
    pins["freeze"]["preregistrationSha256"] = score_rates.file_digest(
        os.path.join(STUDY, "PREREGISTRATION.md"))
    pins["isolationNegative"]["assent"] = "granted"
    path = os.path.join(root, "PINS.json")
    with open(path, "w") as handle:
        json.dump(pins, handle, indent=2)
    return path


def _record_negative_control(root: str, golden: str, **edits) -> str:
    """§6 C7's retained verdict, at a throwaway stand-in for its canonical path.

    WRITTEN rather than run, exactly as `test_batch.py`'s
    `record_negative_control()` writes it — the control's own behaviour is
    tested against the real command there. The scorer re-checks the record
    before it reads a slot (round 9, finding 3), so a population that reaches
    `score()` has to carry one, and the canonical path is [D-23]'s: the
    constant moves, no flag supplies it.

    Round 10, finding 5: the members are the REAL writer's eleven, not the five
    an earlier draft wrote, so a fixture population is scored over a record
    `batch.capture_isolation_negative()` could actually have left. `edits`
    replaces members whole, which is how the damage rows below are built.
    """
    out = os.path.join(root, "controls-isolation-negative")
    os.makedirs(out, exist_ok=True)
    verdict = {"control": "C7 — the isolation gate's power",
               "registeredExpectation": "the golden match FAILS",
               "registeredOutcomes": list(score_rates.C7_OUTCOMES),
               "outcome": "refused",
               "message": "the golden pre-prompt context was not reproduced",
               "wrapperExit": 0,
               "wrapperCode": None,
               "goldenSha256": score_rates.file_digest(golden),
               "deletedByCode": {"session.jsonl": "sha256:" + "0" * 64},
               "assent": "granted",
               "retention": "This file and a stripped CALL.json are always "
                            "retained, and context.json whenever the call "
                            "produced a comparable context."}
    verdict.update(edits)
    with open(os.path.join(out, "VERDICT.json"), "w") as handle:
        json.dump(verdict, handle, indent=2)
    return out


def _score_prefix(population, root: str, monkeypatch) -> dict:
    """`score_rates.score()` itself over a fixture population — the scorer's
    OWN ordering, which is what this case is about.

    The library override (§2.10, §7) is the registry these slots really name,
    so `cell.registryOverride` stays non-null and `_write_outputs()` could
    never publish the document. `score()` takes no population argument beyond
    the root, so nothing here relaxes a check: the ported bytes, the registered
    interpreter, the mirror, the arms and the schedule are all the committed
    study's.
    """
    monkeypatch.setattr(score_rates, "REGISTERED_ISOLATION_NEGATIVE",
                        _record_negative_control(root, population.golden))
    return score_rates.score(
        population.arms_root, _stand_in_registry(root, population.golden),
        population.golden,
        registry_sha256=score_rates.file_digest(score_rates.REGISTRY_OF_RECORD))


@pytest.mark.parametrize("prefix", [0, 1, 2, 3, 4, 5])
def test_every_prefix_of_round_one_publishes_the_descriptive_surface(prefix, pins,
                                                                     study,
                                                                     monkeypatch):
    """§2.8 [D-21], for the five prefixes it could not reach: "any incomplete
    batch, at any round, for any reason, is descriptive-only" (round 9,
    finding 4).

    Round 1 of the registered order is B, C, A, D, E, so a prefix of length
    k < 5 leaves 5−k arms with no `authoring/` root, and the zero prefix leaves
    no ledger either. Each of those used to refuse before terminality was even
    read — the operator of a batch that died in round 1, which is where an
    unproven pipeline dies, saw `arms/A/authoring is not a directory` and had
    no registered way to publish what §2.8 promises.

    The tree is asserted to be the one the DRIVER leaves before it is scored,
    because that is the whole defect: a fixture that made the five roots in
    advance passed every prefix here and proved nothing.

    What "publishes" reaches, and its ceiling (round 10, finding 12): the three
    BODIES the writer writes are all rendered here — the `RESULTS.json`
    serialization, the `RATES.md` page and the `CENSUS.md` page — but the
    WRITER is asserted to REFUSE this document rather than to publish it. A
    fixture's scoring carries the library override, so nothing built here may
    publish, and a test named for publication must not appear to.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(prefix)], ledger=prefix > 0)
        schedule = score_rates.registered_schedule()
        reached = [entry["arm"] for entry in schedule[:prefix]]
        for arm in fixtures.ARMS:
            assert os.path.isdir(
                score_rates.slots_root(population.arms_root, arm)) \
                == (arm in reached), arm
        assert os.path.isfile(os.path.join(population.arms_root, "BATCH.json")) \
            == (prefix > 0)

        results = _score_prefix(population, root, monkeypatch)

        assert results["schedule"]["complete"] is False
        assert results["schedule"]["perArmCounts"] == {
            arm: reached.count(arm) for arm in fixtures.ARMS}
        assert results["schedule"]["roundsCompleted"] == prefix // 5
        assert results["schedule"]["ledgerRecords"] == prefix
        # [D-21]: no verdict of any kind, and no contrast at all.
        for arm in fixtures.ARMS:
            for endpoint in score_rates.LEVEL_ENDPOINTS:
                assert results["verdicts"]["levels"][arm][endpoint] == \
                    [score_rates.UNRESOLVED] * 6, (arm, endpoint)
        assert results["verdicts"]["contrasts"] is None
        assert results["verdicts"]["resolved"] is False
        # …and the headline names the round count rather than implying a batch.
        page = score_rates.render_markdown(results)
        assert "**%d of 30 rounds completed.**" % (prefix // 5) in page

        # §2.8 promises the batch is "published as slots, rates, intervals and
        # census — the whole descriptive surface", and the writer publishes it
        # as three BODIES, not as an object: `json.dumps(…, sort_keys=True)`,
        # `render_markdown()` and `census.render_markdown()`. Only the second
        # was reached here, so a prefix that scored and would not serialise —
        # or a census renderer that assumed a non-empty population, which the
        # zero prefix is for all five arms — was outside the test that names
        # publication (round 10, finding 12).
        assert json.loads(
            json.dumps(results, indent=2, sort_keys=True)) == results
        census_page = score_rates._census().render_markdown(results["census"])
        if prefix == 0:
            assert "Record set: 0 valid runs, 0 accepted records" in census_page
        for body in (page, census_page):
            for header, rows in fixtures.markdown_tables(body):
                for row in rows:
                    if any("\\" in cell for cell in row):
                        continue
                    assert len(row) == len(header), (header, row)

        # The writer itself stays out of a fixture's reach, and that is the
        # point rather than a gap: this population's cell carries the library
        # override (§2.10, §7), so the one thing that publishes refuses it.
        # `STUDY` is moved FIRST, so the refusal is asserted with no path into
        # the committed tree even if the writer's checks were ever reordered.
        monkeypatch.setattr(score_rates, "STUDY", root)
        with pytest.raises(score_rates.ScoreError) as caught:
            score_rates._write_outputs(results, population.arms_root)
        assert "as an override" in str(caught.value)
        assert not os.path.exists(os.path.join(root, "RESULTS.json"))
    finally:
        shutil.rmtree(root, True)


def test_the_scorer_refuses_a_control_record_that_is_not_this_studys(pins, study,
                                                                    monkeypatch):
    """§6 C7's gate on the SCORER's side, over a population that reaches it.

    Round 10, finding 5: the scorer's C7 block had no negative coverage at all.
    The test cited for it — `test_the_scoring_refuses_before_it_reads_a_slot`,
    named as that coverage in its own docstring and in `fixtures.py` — refuses
    on the golden capture being absent from the committed tree, which is many
    checks above C7, so the block below `if not os.path.isfile(c7_path)` had
    never been executed by anything but the happy path.

    `_score_prefix()`'s machinery is what makes this reachable: a stand-in
    registry supplies the golden pin, the freeze digest and the assent, and
    `REGISTERED_ISOLATION_NEGATIVE` moves to a written record. The first
    assertion is the half that proves the rest arrives — an undamaged record
    scores — and every row after it is a record this study's driver could not
    have left, refused by the same rule `test_batch.py` puts on the driver.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        registry = _stand_in_registry(root, population.golden)
        monkeypatch.setattr(score_rates, "REGISTERED_ISOLATION_NEGATIVE",
                            _record_negative_control(root, population.golden))
        record = os.path.join(score_rates.REGISTERED_ISOLATION_NEGATIVE,
                              "VERDICT.json")

        def score():
            return score_rates.score(
                population.arms_root, registry, population.golden,
                registry_sha256=score_rates.file_digest(
                    score_rates.REGISTRY_OF_RECORD))

        def write(body: str) -> None:
            with open(record, "w") as handle:
                handle.write(body)

        def rewrite(**edits):
            _record_negative_control(root, population.golden, **edits)

        assert score()["schedule"]["ledgerRecords"] == 5

        for name, damage in (
                ("absent", lambda: os.unlink(record)),
                ("unreadable", lambda: write("{\n")),
                ("duplicate keys",
                 lambda: write('{"outcome": "refused", "outcome": "matched"}')),
                ("not an object", lambda: write('["refused"]')),
                ("unregistered outcome", lambda: rewrite(outcome="skipped")),
                ("another assent", lambda: rewrite(assent="withheld")),
                ("another golden",
                 lambda: rewrite(goldenSha256="sha256:" + "1" * 64)),
                # …and the three shape members, so the driver's gate and this
                # one refuse the same records (round 10, finding 5).
                ("another registration",
                 lambda: rewrite(registeredOutcomes=["refused", "matched"])),
                ("deletions that are not an object",
                 lambda: rewrite(deletedByCode=["session.jsonl"])),
                ("a boolean exit status", lambda: rewrite(wrapperExit=True))):
            damage()
            with pytest.raises(score_rates.ScoreError) as caught:
                score()
            assert "VERDICT.json" in str(caught.value), name
            assert type(caught.value) is score_rates.ScoreError, name
    finally:
        shutil.rmtree(root, True)


def test_a_missing_root_the_prefix_reached_refuses_and_names_the_arm(pins, study):
    """The tolerance is not a hole: an arm the prefix DID reach may not lose
    its root.

    C5 rule 2 gets there first and says it better — the ledger still records
    that arm's slot, the slot is gone with the root, and the refusal names the
    slot rather than the arm — which is exactly why the rule-4 guard below is
    the belt and this is the braces. A population whose arm E root is removed
    is not an arm the prefix has not reached; it is a slot that was created and
    removed, and no rate is computed over one.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([{} for _ in range(5)])
        assert population.score_runs()["counts"]["E"] == 1
        shutil.rmtree(score_rates.slots_root(population.arms_root, "E"))
        with pytest.raises(score_rates.ScoreError) as caught:
            population.score_runs()
        assert "arms/E/authoring/run-001" in str(caught.value)
        assert type(caught.value) is score_rates.ScoreError
    finally:
        shutil.rmtree(root, True)


def test_a_missing_root_with_no_declaration_refuses_at_rule_four(pins, study):
    """C5 rule 4's own guard, at the one shape rule 2 cannot reach: no slot, no
    ledger record naming one, and no `SHORTFALL.json` either.

    A missing root is an arm the prefix has not reached, and "the prefix has
    not reached it" is a statement about a DECLARED short batch. With no
    declaration there is no such statement, so the empty arm is an arm dropped
    from the population, and the refusal says which arm and how many slots the
    prefix derives for it.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([], ledger=False)
        os.remove(os.path.join(population.arms_root, "SHORTFALL.json"))
        slots = {arm: [] for arm in fixtures.ARMS}
        with pytest.raises(score_rates.ScoreError) as caught:
            score_rates.check_population(population.arms_root, slots, [],
                                         population.schedule, None)
        message = str(caught.value)
        assert "arm A has no authoring/ root" in message
        assert "derives 0 slot(s) for it" in message
        assert "no SHORTFALL.json declares a short batch" in message
        # …and the same population WITH the declaration is admitted, so the
        # refusal above is about the missing declaration and not about the
        # missing root.
        declaration = fixtures.declare_shortfall(population.arms_root, [], 0)
        assert score_rates.check_population(population.arms_root, slots, [],
                                            population.schedule,
                                            declaration)["counts"] == \
            {arm: 0 for arm in fixtures.ARMS}
    finally:
        shutil.rmtree(root, True)


def test_the_empty_batch_is_admitted_only_by_a_declaration_that_no_slot_ran(pins,
                                                                           study):
    """The absent `BATCH.json` is admitted for the empty prefix and for nothing
    else (round 9, finding 4).

    The declaration is read member by member: zero rounds, zero through global
    index zero, zero slots, and no last slot and no clock to name. A
    declaration that says a slot ran, a population with a slot in it, and the
    JSON `false` that `== 0` would have accepted are all refused — the bool
    exclusion is the same house rule the ledger's own type checks use, because
    `isinstance(True, int)` is True in Python.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([], ledger=False)
        arms_root = population.arms_root
        path = os.path.join(arms_root, "SHORTFALL.json")
        with open(path) as handle:
            honest = json.load(handle)
        assert score_rates.load_ledger(arms_root, honest, 0) == []
        # (a) the declaration says a slot ran.
        cases = [
            dict(honest, completedThroughGlobalIndex=1),
            dict(honest, completedRounds=1),
            dict(honest, completedSlots=1),
            dict(honest, lastSlot="arms/B/authoring/run-001"),
            dict(honest, lastSlotEndedAt="2026-08-09T00:00:00Z"),
            dict(honest, lastSlotEndedAtFrom="arms/B/authoring/run-001"),
            # (b) the bool trap: JSON `false` is an int in Python and `== 0`.
            dict(honest, completedThroughGlobalIndex=False),
            dict(honest, completedRounds=False),
            dict(honest, completedSlots=False),
            # (c) a member missing altogether, and no declaration at all.
            {key: value for key, value in honest.items()
             if key != "completedSlots"},
            None,
        ]
        for declaration in cases:
            assert score_rates._declares_no_slot_ran(declaration) is False, \
                declaration
            with pytest.raises(score_rates.ScoreError) as caught:
                score_rates.load_ledger(arms_root, declaration, 0)
            assert "no ledger at" in str(caught.value)
            assert type(caught.value) is score_rates.ScoreError
        # (d) an honest zero declaration with a slot actually present: the
        # ledger is required again, because the batch is no longer empty.
        os.makedirs(os.path.join(arms_root, "B", "authoring", "run-001"))
        with pytest.raises(score_rates.ScoreError) as caught:
            score_rates.load_ledger(arms_root, honest, 1)
        assert "no ledger at" in str(caught.value)
        # …and the single-argument call, which is what a caller holding no
        # declaration is entitled to, still refuses.
        with pytest.raises(score_rates.ScoreError):
            score_rates.load_ledger(arms_root)
    finally:
        shutil.rmtree(root, True)


def test_an_authoring_root_that_is_present_and_not_a_directory_still_refuses(pins,
                                                                            study):
    """`collect_slots()` distinguishes ABSENT from present-but-not-a-directory,
    and only the first is an empty population.

    `lexists`, not `exists`: a DANGLING symlink at the authoring root is
    something that was created and broken — a tree that lost its slots — and it
    refuses with the message it always had. A symlink to a real directory keeps
    its old behaviour for the same reason `isdir` has always followed one.
    """
    root = fixtures.throwaway_root()
    try:
        population = fixtures.Population(root, study, pins)
        population.build([], ledger=False)
        arm_root = score_rates.slots_root(population.arms_root, "A")
        assert score_rates.collect_slots(arm_root) == ([], [])
        elsewhere = os.path.join(root, "somewhere-else")
        os.makedirs(elsewhere)
        for make in (lambda: open(arm_root, "w").close(),
                     lambda: os.symlink(os.path.join(root, "gone"), arm_root)):
            make()
            with pytest.raises(score_rates.ScoreError) as caught:
                score_rates.collect_slots(arm_root)
            assert "is not a directory" in str(caught.value)
            assert type(caught.value) is score_rates.ScoreError
            os.remove(arm_root)
        os.symlink(elsewhere, arm_root)
        assert score_rates.collect_slots(arm_root) == ([], [])
    finally:
        shutil.rmtree(root, True)


def _source(path: str) -> str:
    with open(path.replace(".pyc", ".py"), "rb") as handle:
        return handle.read().decode("utf-8")
