#!/usr/bin/env python3
"""§6 C2 and §6 C3 clause 1 — the two registered controls the port left
unimplemented (round 3 finding 6).

**C2, family/pack coherence, for the arms where it is available.** For arms A,
B, C and E — every arm at (40, 70) — Study 011's C2 runs unchanged against
Study 010's pack C, read in place at its pinned digest: every mutation's
`patch` preimage must be present byte-exact at its JSON pointer, the six
`index` members must be contiguous 0-5, and every mutation applied to pack C
must CHANGE it.

For arm **D** that clause is not available, and [D-6] registers what replaces
it rather than leaving a control silently unrun: pack C encodes 40 and 70, so
D's preimages at 45 and 72 are not in it. This file asserts BOTH halves of that
posture — that the pack-side clause really is unavailable (the preimages that
are missing are named, so "unavailable" is a demonstrated fact and not a
sentence), and that D's family coheres with D's MIRROR through §2.4's landmark
grid, which is `harness/integrity.py`'s clause-6 equality asserted directly
here for D. Nothing else vouches for D's family, and [D-6] says so.

**C3 clause 1, the counting.** The ported compiler, mirror and class arithmetic
are run over Study 010's retained `completion.txt` and must reproduce 010's
published profile exactly: `accepted = 16`, `|H| = 16`, `|Q| = 0`, H ∩ class
counts `(2, 2, 2, 4, 1, 1)`, Q ∩ class counts all zero. The numbers below are
transcribed from PREREGISTRATION.md §6 C3; the INPUT is bound to a digest, and
`harness/PINS.json` carries no `replication` member of its own, so the digest
comes from Study 011's registry — the file this study pins at
`pinnedFrom.pins.sha256` and §6 C1 tier 2 already answers to. That is checked
here before it is read, so the expected input is bound to an authority rather
than to a hex string someone typed into a test.

Both controls read Study 010's tree (C2 the pack, C3 the completion) and Study
011's registry; all three are read in place and never written. No evaluator
runs, no pack is evaluated, and this study plants nothing: C2 bounds what a
*patch* can mean, not what a predicate can.
"""
from __future__ import annotations
import hashlib
import json
import os

import pytest

import integrity
import records_compile
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
TEN = os.path.normpath(os.path.join(STUDY, "..", "010-blinded-oracle"))
ELEVEN = os.path.normpath(os.path.join(STUDY, "..", "011-authorship-coverage-rates"))

# §6 C2: pack C is Study 010's correct pack, named as 010's own lock names it.
PACK_INPUT = "packs/vendor-screening-correct.pack.json"
# The (40, 70) arms — every arm C2's pack-side clause is available for. Arm D
# is the exception [D-6] registers, and it has its own tests below.
PACK_ARMS = ("A", "B", "C", "E")
BASELINE_ARM = "A"
PERTURBED_ARM = "D"

# §6 C3 clause 1, transcribed from PREREGISTRATION.md. Study 010 published this
# profile; a port that agreed with itself and not with it would pass nothing.
PUBLISHED_PROFILE = {
    "accepted": 16,
    "h": 16,
    "q": 0,
    "hClassCounts": [2, 2, 2, 4, 1, 1],
    "qClassCounts": [0, 0, 0, 0, 0, 0],
}


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def load(path: str):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


# --- C2 ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def pack():
    """Study 010's pack C, read in place at the digest 010's own
    `PROTOCOL-LOCK.json` locks it to. The lock is the authority; this file does
    not carry a second copy of the pack's digest, because a control checked
    against a number written beside it is a control checked against itself."""
    lock = load(os.path.join(TEN, "PROTOCOL-LOCK.json"))
    path = os.path.join(TEN, PACK_INPUT)
    assert digest(path) == lock["lockedInputs"][PACK_INPUT], (
        "Study 010's %s is not at its locked digest: C2 reads the pack 010 locked "
        "and no other bytes" % PACK_INPUT)
    return load(path)


def family(arm: str) -> dict:
    return load(os.path.join(STUDY, "arms", arm, "FAMILY.json"))


def resolve(document, pointer: str):
    """RFC 6901, the subset the families use: object members and array indexes,
    no escapes needed by these pointers. Raises where the pointer does not
    resolve, which is itself an outcome the D tests read."""
    node = document
    for token in pointer.split("/")[1:]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def assign(document, pointer: str, value) -> None:
    node = document
    tokens = pointer.split("/")[1:]
    for token in tokens[:-1]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    last = tokens[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


def canonical(value) -> str:
    """The byte-exact comparison C2 registers, in the form that distinguishes
    `"70"` from `70` and `{"a": 1, "b": 2}` from a different dict with the same
    members in another order."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@pytest.mark.parametrize("arm", PACK_ARMS)
def test_every_patch_preimage_is_present_byte_exact_in_pack_c(arm, pack):
    for mutation in family(arm)["mutations"]:
        for patch in mutation["patch"]:
            found = resolve(pack, patch["path"])
            assert canonical(found) == canonical(patch["old"]), (
                "arm %s's mutation %d: pack C holds %r at %s and the family's "
                "preimage is %r — the patch describes a pack that is not this one"
                % (arm, mutation["index"], found, patch["path"], patch["old"]))


@pytest.mark.parametrize("arm", PACK_ARMS)
def test_the_six_indexes_are_contiguous(arm):
    assert [mutation["index"] for mutation in family(arm)["mutations"]] == list(range(6))


@pytest.mark.parametrize("arm", PACK_ARMS)
def test_every_mutation_actually_changes_pack_c(arm, pack):
    """010's gate ran two clauses and this is the second: a patch whose result
    equals pack C plants nothing, so the class it names would be the class of a
    defect that does not exist. It needs only the pack bytes and the patch — no
    evaluator — which is why C2 keeps it in a study that evaluates nothing."""
    for mutation in family(arm)["mutations"]:
        patched = json.loads(json.dumps(pack))
        for patch in mutation["patch"]:
            assign(patched, patch["path"], patch["new"])
        assert patched != pack, (
            "arm %s's mutation %d does not change pack C" % (arm, mutation["index"]))


def test_arm_ds_pack_side_clause_is_not_available_and_the_gap_is_named(pack):
    """[D-6]'s first half, demonstrated rather than asserted: pack C encodes 40
    and 70, so the preimages arm D's family names at 45 and 72 are not in it.

    The test names the mutations whose preimages are absent, so a future edit
    that quietly moved arm D back onto (40, 70) — which would make the pack-side
    clause available again and this posture unnecessary — fails here instead of
    leaving a registered exception in place for a study that no longer needs it.
    """
    missing = []
    for mutation in family(PERTURBED_ARM)["mutations"]:
        for patch in mutation["patch"]:
            try:
                found = resolve(pack, patch["path"])
            except (KeyError, IndexError, ValueError):
                missing.append((mutation["index"], patch["path"], None))
                continue
            if canonical(found) != canonical(patch["old"]):
                missing.append((mutation["index"], patch["path"], found))
    assert [row[0] for row in missing] == [1, 2, 5], (
        "arm D's preimages absent from pack C are %r; [D-6] registers the pack-side "
        "clause as unavailable for D because pack C encodes (40, 70) and D's family "
        "is written at (45, 72)" % (missing,))
    # …and the reason is the thresholds, not a mistyped pointer: every pointer
    # resolves, and what it resolves to is 010's number where D's is the shifted
    # one.
    assert all(found is not None for _, _, found in missing)
    assert sorted(set(found for _, _, found in missing)) == ["40", "70"]


def test_arm_ds_family_coheres_with_arm_ds_mirror_over_the_landmark_grid():
    """[D-6]'s second half, and the whole of what vouches for arm D's family:
    §2.4's 280-cell landmark grid, which is `harness/integrity.py`'s C8 clause 6
    equality — asserted here directly for D rather than left inside a function
    whose failure would be reported as an arm-artifact defect.

    Two vectors, elementwise, at each arm's OWN pair: the mirror's verdict over
    the grid, and the tuple of family classes each cell matches. Equality means
    D's six classes are the same six classes at D's edges as A's are at A's, so
    "D's family is coherent with D's mirror" is a computed fact over 280 cells
    and not a claim about how the family was written.
    """
    pairs = {arm: pair for arm, pair in integrity.REGISTERED_PAIRS.items()}
    baseline = pairs[BASELINE_ARM]
    perturbed = pairs[PERTURBED_ARM]
    assert perturbed != baseline, "arm D is the perturbed-edge arm (§2.3)"
    assert integrity.verdict_vector(*perturbed) == integrity.verdict_vector(*baseline)
    mutations = family(PERTURBED_ARM)["mutations"]
    assert [mutation["index"] for mutation in mutations] == list(range(6))
    assert integrity.class_vector(mutations, *perturbed) \
        == integrity.class_vector(family(BASELINE_ARM)["mutations"], *baseline)
    # The grid is 280 cells and not a handful: an equality over an empty or
    # truncated grid would pass without saying anything.
    assert len(integrity.grid(*perturbed)) == 280


# --- C3 clause 1 ------------------------------------------------------------

@pytest.fixture(scope="module")
def replication(pins):
    """Study 011's `replication` member — the retained Study 010 completion's
    path and digest — read out of the registry this study pins.

    `harness/PINS.json` carries no replication member of its own, so the input's
    authority is 011's registry, which this study pins at
    `pinnedFrom.pins.sha256` and §6 C1 verifies before any call. The pin is
    re-checked here because these numbers are read out of that file: a control
    whose expected input came from an unverified copy of another study's
    registry would be a control over whatever that copy said.
    """
    path = os.path.join(ELEVEN, "harness", "PINS.json")
    assert digest(path) == pins["pinnedFrom"]["pins"]["sha256"], (
        "Study 011's harness/PINS.json is not the file this study pins at "
        "pinnedFrom.pins.sha256 (§6 C1 tier 2)")
    member = load(path)["replication"]
    assert member["expected"] == PUBLISHED_PROFILE, (
        "Study 011's registry records the profile %r and §6 C3 clause 1 registers "
        "%r: the two studies replicate one published number or neither does"
        % (member["expected"], PUBLISHED_PROFILE))
    return member


def test_study_010s_retained_completion_reproduces_its_published_profile(
        pins, replication):
    """§6 C3 clause 1: this study's counting code must mean what its
    predecessor's did, on the bytes Study 010 actually retained.

    The compiler, the mirror and the class arithmetic are the ported ones, run
    at arm A's registered pair — 010's own (40, 70), and the arm whose
    `FAMILY.json` §6 C1 tier 1 binds to 010's lock — through the scorer's own
    `load_arm()`, so the classes are the ones a scoring would use and not a
    second reading of the same file.
    """
    completion_path = os.path.normpath(os.path.join(STUDY, replication["path"]))
    assert digest(completion_path) == replication["sha256"], (
        "%s is not the retained completion Study 011's registry pins: C3 replicates "
        "a published number over the bytes that produced it"
        % os.path.relpath(completion_path, STUDY))
    definition = score_rates.load_arm(os.path.join(STUDY, "arms"), BASELINE_ARM,
                                      pins["arms"][BASELINE_ARM])
    assert (str(definition["tLow"]), str(definition["tHigh"])) == ("40", "70"), (
        "C3 clause 1 replays Study 010's completion at Study 010's own pair")
    accepted, _ledger, _span = records_compile.compile_records(
        records_compile.read_completion(completion_path))
    high, quarantine = score_rates.split_records(accepted, definition["tLow"],
                                                 definition["tHigh"])
    expected = replication["expected"]
    assert len(accepted) == expected["accepted"]
    assert len(high) == expected["h"]
    assert len(quarantine) == expected["q"]
    assert [len(score_rates.class_members(accepted, high, entry["predicate"]))
            for entry in definition["classes"]] == expected["hClassCounts"]
    assert [len(score_rates.class_members(accepted, quarantine, entry["predicate"]))
            for entry in definition["classes"]] == expected["qClassCounts"]
