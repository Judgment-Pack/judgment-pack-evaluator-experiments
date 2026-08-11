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

**§2.6's member split, pinned here as well.** §2.6 registers `FAMILY.json`'s
whole member list — what this study reads (`embargoList`, and per mutation
`index`, `title`, `predicate`, `predicateProse` and `patch`) and what is inert
in it (`familyVersion`, `pack`, `note`, and per mutation `violatedClause`,
`underD` and `reasonsUnderD`, 010's plant-and-evaluate vocabulary) — and the
three tests closing the C2 block below bind that registration to the bytes
(round 9, finding 8). A fourth test beside them carries §2.6's other register
of inherited bytes, the arms' shared policy preamble: its process assertions
are in every arm's stimulus and byte-identical in all five, which is what
"inherited and non-differential, not inert" means and is why that register and
the inert one are not interchangeable (round 11, finding 9).

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
    """The byte-exact comparison C2 registers, in Study 011's own form
    (`011/harness/tests/test_controls.py:337`) — §6 C2 registers that 011's C2
    "runs unchanged", so this sorts members as 011 does. It distinguishes
    `"70"` from `70` and `true` from `1`, which is what a preimage comparison
    has to do here (arm index 3's preimage is a JSON boolean, and plain `==`
    would accept `1` for it). It does NOT distinguish two objects with the same
    members in another order: `sort_keys=True` normalizes member order, JSON
    object order is not a value distinction, and §6 C2 registers no order
    claim. An earlier form of this docstring said it did; no family carries an
    object-valued preimage, so nothing ever turned on it (round 11,
    finding 11)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def contiguous_indexes(mutations) -> bool:
    """§6 C2's index clause, type-strict. `type(...) is int` and not
    `isinstance`, because JSON `false` is an `int` in Python:
    `[false, true, 2, 3, 4, 5] == list(range(6))` is True, so ordinary equality
    would accept a family whose first two indexes are booleans. This is the
    house rule the ledger's own type checks use, in the form
    `integrity.py`'s clause 6 already carries (round 8, finding 8)."""
    indexes = [entry["index"] for entry in mutations]
    return indexes == list(range(6)) and all(
        type(index) is int for index in indexes)


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
    assert contiguous_indexes(family(arm)["mutations"]), (
        "arm %s's family indexes are not the contiguous INTEGERS 0-5 (a JSON "
        "false is not an index; round 8, finding 8)" % arm)


def test_the_index_clause_refuses_a_boolean_index():
    """The assertion this helper replaced passed on `[false, true, 2, 3, 4, 5]`
    under ordinary equality. `integrity.py`'s clause 6 already refuses such a
    family before any run, so nothing was exposed; this pins the control's own
    words to what it checks (round 11, finding 11)."""
    assert contiguous_indexes([{"index": index} for index in range(6)])
    assert not contiguous_indexes(
        [{"index": json.loads("false")}, {"index": json.loads("true")}]
        + [{"index": index} for index in (2, 3, 4, 5)])


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
    assert contiguous_indexes(mutations)
    assert integrity.class_vector(mutations, *perturbed) \
        == integrity.class_vector(family(BASELINE_ARM)["mutations"], *baseline)
    # The grid is 280 cells and not a handful: an equality over an empty or
    # truncated grid would pass without saying anything.
    assert len(integrity.grid(*perturbed)) == 280


# §2.6: the whole member list, split into what this study reads and what it
# does not. The inert set is 010's plant-and-evaluate vocabulary, retained
# because arm A's bytes are 010's lock (§6 C9) and one generator makes all five.
FAMILY_MEMBERS = ("familyVersion", "pack", "note", "embargoList", "mutations")
MUTATION_MEMBERS = ("index", "title", "patch", "violatedClause", "predicate",
                    "predicateProse", "underD", "reasonsUnderD")
INERT_MUTATION_MEMBERS = ("violatedClause", "underD", "reasonsUnderD")
ALL_ARMS = ("A", "B", "C", "D", "E")


@pytest.mark.parametrize("arm", ALL_ARMS)
def test_every_familys_members_are_the_set_2_6_registers(arm):
    """§2.6 registers the whole member list, not only §2.3's six predicates: a
    reviewer attesting the §2.10 tree manifest is attesting these bytes, so a
    member the registration does not name fails here rather than being noticed
    by a reader of the JSON."""
    document = family(arm)
    assert tuple(document) == FAMILY_MEMBERS
    for mutation in document["mutations"]:
        assert tuple(mutation) == MUTATION_MEMBERS


@pytest.mark.parametrize("arm", ALL_ARMS)
def test_the_inert_mutation_members_change_no_class(arm):
    """The inert members carry no weight, demonstrated rather than asserted:
    strip them and the class vector over that arm's own 280-cell grid — the
    only thing any control computes from a family — is unchanged."""
    full = family(arm)["mutations"]
    stripped = [{key: value for key, value in mutation.items()
                 if key not in INERT_MUTATION_MEMBERS} for mutation in full]
    pair = integrity.REGISTERED_PAIRS[arm]
    assert integrity.class_vector(stripped, *pair) \
        == integrity.class_vector(full, *pair)


def test_no_harness_source_outside_the_generator_names_the_inert_members():
    """§2.6's "read by nothing", checked at the strength source text can carry.

    Scanned: `familyVersion` and the three inert mutation members, whose names
    are unambiguous. NOT scanned, and the gap is stated rather than papered
    over: `pack` and `note` are ordinary words elsewhere in this harness
    (`struct.pack` in integrity.py, the `note` member of PINS.json and of the
    slot manifest in fixtures.py), so a name scan cannot separate them and
    their non-use rests on the registration and on review. `arm_assembly.py`
    is excluded because it WRITES these members, and this file because it
    names them. A source scan is not a proof of non-use — a reflective read
    would pass it — and this test is registered at that strength.
    """
    names = ("familyVersion",) + INERT_MUTATION_MEMBERS
    hits = []
    for root, _dirs, files in os.walk(HARNESS):
        if "__pycache__" in root:
            continue
        for name in sorted(files):
            if not name.endswith(".py") or name in ("arm_assembly.py",
                                                    os.path.basename(__file__)):
                continue
            path = os.path.join(root, name)
            with open(path, "rb") as handle:
                text = handle.read().decode("utf-8")
            hits += [(os.path.relpath(path, STUDY), member)
                     for member in names if member in text]
    assert not hits, (
        "§2.6 registers these members as read by nothing, and they appear in "
        "%r" % (hits,))


# §2.6: the two process assertions the arms inherit from Study 010's preamble,
# quoted here as §2.6 quotes them. Flattened before the search, because the
# stimulus hard-wraps them across lines.
INHERITED_PROCESS_ASSERTIONS = (
    "Every other artifact in this study is checked against this text",
    "a divergence between a pack and this text is a pack bug",
)


def flatten(text: str) -> str:
    return " ".join(text.split())


def commission_prompts(arm: str) -> list:
    """C10's clean-room commission prompts for one arm — every attempt rather
    than attempt 1 alone, because §7 requires a fresh reader after any
    re-authoring and any later attempt inlines the same policy."""
    root = os.path.join(STUDY, "analysis", "mirror2-attempts", arm)
    return [os.path.join(root, attempt, "prompt.txt")
            for attempt in sorted(os.listdir(root))
            if os.path.isfile(os.path.join(root, attempt, "prompt.txt"))]


def test_the_inherited_preamble_is_in_every_stimulus_and_differs_in_none(pins):
    """§2.6 registers the preamble's inherited process assertions as
    **non-differential, not inert**, and the difference between those two words
    is what this test demonstrates.

    IN THE STIMULUS: both assertions §2.6 quotes reach every population this
    study hands a policy to — the record author, through all five
    `arms/<X>/PROMPT.txt`, and C10's clean-room readers, through their
    commission prompts. That is why "inert" would be the wrong register: the
    `FAMILY.json` members above are inert because nothing reads them, and this
    prose is read in every one of the calls this study scores.

    DIFFERENTIAL IN NONE: the parsed preamble is ONE value across the five arms
    and hashes to `harness/PINS.json`'s `assembledPreamble` — the equality C8
    clause 4 checks both ways — so it is constant by construction and can enter
    no §5.2 contrast (round 11, finding 9).
    """
    for arm in ALL_ARMS:
        paths = ([os.path.join(STUDY, "arms", arm, "PROMPT.txt")]
                 + commission_prompts(arm))
        assert len(paths) >= 2, (
            "arm %s has no C10 commission prompt to check the preamble in" % arm)
        for path in paths:
            with open(path, "rb") as handle:
                body = flatten(handle.read().decode("utf-8"))
            for sentence in INHERITED_PROCESS_ASSERTIONS:
                assert sentence in body, (
                    "%s does not carry %r, which §2.6 registers as inherited "
                    "prose that is in the stimulus"
                    % (os.path.relpath(path, STUDY), sentence))
    preambles = set()
    for arm in ALL_ARMS:
        with open(os.path.join(STUDY, "arms", arm, "POLICY.md"), "rb") as handle:
            preambles.add(integrity.parse_policy(handle.read())[0])
    assert len(preambles) == 1, (
        "the preamble is not one value across the five arms, so §2.6's "
        "non-differential register is false of the bytes")
    assert "sha256:" + hashlib.sha256(
        preambles.pop().encode("utf-8")).hexdigest() \
        == pins["assembledPreamble"]["sha256"], (
        "the assembled preamble does not hash to the pin C8 clause 4 checks")


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
