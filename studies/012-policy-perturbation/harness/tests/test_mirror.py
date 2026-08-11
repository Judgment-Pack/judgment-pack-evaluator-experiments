"""The registered mirror properties (§2.2 [D-14], §2.4, §6 C8 clause 6).

Four assertions, each named in the preregistration:

1. **Parameterization changes what the comparisons READ, nothing they
   DECIDE**: at (40, 70) the single registered module agrees with Study 010's
   locked `policy_mirror.py` on every cell of the landmark grid. The locked
   module is imported from Study 010 in place, at its locked digest — C1
   already binds those bytes, and this test refuses to run against drifted
   ones rather than compare against a copy.

2. **Every arm's verdict vector equals arm A's over its own grid** — the C8
   clause 6 equality, asserted here as well as enforced in
   `integrity.verify_arms()`, because a control that only runs inside the
   thing it controls is not independently exercised.

3. **The 14th landmark is load-bearing** (§2.4's negative control): a mutant
   family encoding class 5 as `[T_low - 2, T_low)` agrees with arm A's class
   vector on ALL 260 cells of the 13-landmark grid and DISAGREES on the
   14-landmark one. Verified both ways before the landmark was written into
   the registration; re-verified here so the grid cannot silently lose the
   cell that catches the mutant.

4. **Every edge the family names is straddled** (§2.4's corrected claim, round
   9, finding 11): for each of the five edges — `T_low - 1`, `T_low`,
   `T_low + 1`, `T_high`, `T_high + 1` — the grid holds the edge and an
   immediately adjacent landmark the family answers differently. Which side
   that neighbour is on is NOT uniform, which is what §2.4's earlier "a point
   0.01 to its excluded side" got wrong, so the straddle and the side facts
   are asserted separately. The comparison is over the family's CLASS column
   alone (round 10, finding 11): the mirror's verdict changes at `T_low` and
   `T_high` whatever the six predicates do, so folding it in would make the
   check vacuous at two of the five edges. That verdict edge set is pinned as
   its own fact instead.

5. **The family nests exactly where §2.3 says it does** (round 10, finding 4):
   over the whole grid, at EVERY arm's registered threshold pair, the ordered
   pairs of classes whose members are contained in one another are exactly
   `{(0, 1), (2, 3)}`. §2.3 has asserted that sentence since round 1 and no code
   or test read it; §5.4's joint arithmetic now turns on it, because containment
   between two classes orders their coverage indicators pathwise and makes
   independence between them unavailable at any nondegenerate marginals. The
   ONLY-two half matters as much as the two: adjacency (class 5 beside class 3)
   binds nothing, since different records in one run can witness disjoint
   classes, so a third containment appearing after a family edit would silently
   invalidate `score_rates.NESTED_CLASS_PAIRS` and every companion figure §5.4
   publishes.
"""
import copy
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
TEN = os.path.normpath(os.path.join(STUDY, "..", "010-blinded-oracle"))
sys.path.insert(0, HARNESS)

import integrity  # noqa: E402
import policy_mirror  # noqa: E402
import score_rates  # noqa: E402

TEN_MIRROR_SHA256 = "276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba"


def _ten_mirror():
    path = os.path.join(TEN, "harness", "policy_mirror.py")
    with open(path, "rb") as handle:
        data = handle.read()
    assert hashlib.sha256(data).hexdigest() == TEN_MIRROR_SHA256, (
        "Study 010's locked mirror has drifted; this test refuses to compare "
        "against unlocked bytes")
    spec = importlib.util.spec_from_file_location("ten_policy_mirror", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parameterized_mirror_agrees_with_010_at_its_pair():
    ten = _ten_mirror()
    for cell in integrity.grid("40", "70"):
        assert policy_mirror.verdict(cell, "40", "70") == ten.verdict(cell), cell


def test_every_arm_verdict_vector_equals_arm_a():
    vector_a = integrity.verdict_vector(*integrity.REGISTERED_PAIRS["A"])
    for arm, pair in integrity.REGISTERED_PAIRS.items():
        assert integrity.verdict_vector(*pair) == vector_a, arm


def test_no_defaults_on_the_thresholds():
    cell = integrity.grid("40", "70")[0]
    try:
        policy_mirror.verdict(cell)
    except TypeError:
        return
    raise AssertionError("verdict() accepted a call with no thresholds; a "
                         "silent default would label arm D at (40, 70)")


def _family(study=STUDY, arm="A"):
    with open(os.path.join(study, "arms", arm, "FAMILY.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _grid_13(t_low, t_high):
    """§2.4's previous, thirteen-landmark grid: the registered fourteen minus
    `T_low - 1 - 0.01` — rebuilt here so the negative control states exactly
    which cell the round-2 review added."""
    from decimal import Decimal
    low = Decimal(t_low)
    dropped = format(low - 1 - Decimal("0.01"), "f")
    return [cell for cell in integrity.grid(t_low, t_high)
            if cell["riskScore"] != dropped]


def _class_vector_over(cells, classes):
    return [tuple(entry["index"] for entry in classes
                  if policy_mirror.predicate_matches(entry["predicate"], cell))
            for cell in cells]


def test_the_fourteenth_landmark_catches_the_class5_mutant():
    real = _family()["mutations"]
    mutant = copy.deepcopy(real)
    entry = mutant[5]["predicate"]["riskScore"]
    assert entry.get("gte") == "39" and entry.get("lt") == "40", (
        "class 5's encoding moved; the mutant below no longer states "
        "[T_low - 2, T_low)")
    entry["gte"] = "38"

    thirteen = _grid_13("40", "70")
    assert len(thirteen) == 260
    assert (_class_vector_over(thirteen, mutant)
            == _class_vector_over(thirteen, real)), (
        "the mutant is supposed to survive the 13-landmark grid; if it no "
        "longer does, the negative control's premise has changed")

    fourteen = integrity.grid("40", "70")
    assert len(fourteen) == 280
    assert (_class_vector_over(fourteen, mutant)
            != _class_vector_over(fourteen, real)), (
        "the 14-landmark grid no longer distinguishes the [T_low-2, T_low) "
        "mutant: the landmark that exists to catch it is not doing so")


# --- §2.4's straddle claim, as a computed fact (round 9, finding 11) ---------

NAMED_EDGES = ("39", "40", "41", "70", "71")


def _class_columns(t_low="40", t_high="70"):
    """Each landmark's CLASS COLUMN — the family's matching class indices over
    the 20 non-score combinations — keyed by the landmark. Two landmarks with
    different columns are two the six predicates answer differently, which is
    the whole of what §2.4's straddle claim says. The mirror's verdict is
    deliberately NOT folded in: at `T_low` and at `T_high` the verdict alone
    changes, so a combined column would differ at those two edges whatever the
    six predicates did (round 10, finding 11)."""
    classes = _family()["mutations"]
    columns = {}
    for cell in integrity.grid(t_low, t_high):
        columns.setdefault(cell["riskScore"], []).append(
            tuple(entry["index"] for entry in classes
                  if policy_mirror.predicate_matches(entry["predicate"], cell)))
    return {score: tuple(column) for score, column in columns.items()}


def _verdict_columns(t_low="40", t_high="70"):
    """The same shape for the registered mirror's verdict: kept as its own
    fact, never as a substitute for the class column."""
    columns = {}
    for cell in integrity.grid(t_low, t_high):
        columns.setdefault(cell["riskScore"], []).append(
            policy_mirror.verdict(cell, t_low, t_high))
    return {score: tuple(column) for score, column in columns.items()}


def _classes_at(score):
    """The classes arm A's family puts one score in, at the combination §2.4's
    own worked reading uses: not sanctioned, registered in CA, personal data."""
    cell = {"sanctionsHit": False, "registeredCountry": "CA",
            "handlesPersonalData": True, "riskScore": score}
    return {entry["index"] for entry in _family()["mutations"]
            if policy_mirror.predicate_matches(entry["predicate"], cell)}


def test_every_named_edge_is_straddled_by_adjacent_landmarks():
    """§2.4's corrected claim as a computed fact (round 9, finding 11).

    For each of the five edges arm A's family names, the grid holds the edge
    AND an immediately adjacent landmark the family answers differently —
    which is what pins the inclusive/exclusive decision. Which side that
    neighbour is on is NOT uniform, so this asserts the straddle and then the
    two side facts separately: §2.4 used to say the 0.01 point was always on
    the excluded side, and at an exclusive upper bound it is the included one.

    The straddle is compared over the family's CLASS column ALONE. Round 9
    folded the mirror's verdict into the same column, which made the check
    vacuous at `T_low` and `T_high` — the verdict changes there whatever the
    six predicates do — so the verdict's own edge set is pinned below as its
    own separate fact (round 10, finding 11).
    """
    marks = integrity.landmarks("40", "70")
    assert len(marks) == 14
    for edge in NAMED_EDGES:
        assert edge in marks, (
            "§2.4 names %s as an edge the six predicates draw and the grid no "
            "longer holds it" % edge)

    columns = _class_columns()
    for edge in NAMED_EDGES:
        below = marks[marks.index(edge) - 1]
        assert columns[edge] != columns[below], (
            "the six predicates put %s and its neighbour %s in the same "
            "classes, so nothing pins the inclusive/exclusive decision at that "
            "edge" % (edge, below))

    # The mirror's own answers separate only two of the five edges — T_low (for
    # personal-data vendors) and T_high (for everyone). Asserted as an exact
    # set, and separately, because folding it into the column above is what let
    # those two edges pass on the verdict alone (round 10, finding 11).
    verdicts = _verdict_columns()
    assert {edge for edge in NAMED_EDGES
            if verdicts[edge] != verdicts[marks[marks.index(edge) - 1]]} == {
                "40", "70"}

    # Below an INCLUSIVE LOWER bound the 0.01 neighbour is the excluded point.
    assert 5 in _classes_at("39") and 5 not in _classes_at("38.99")
    # At an EXCLUSIVE UPPER bound the point AT the edge is itself the excluded
    # side, and the 0.01 point below it is the included one — the two cases
    # §2.4's withdrawn sentence had backwards.
    assert 2 in _classes_at("40.99") and 2 not in _classes_at("41")
    assert 1 in _classes_at("70.99") and 1 not in _classes_at("71")
    # …and what T_high + 0.01 buys: class 0 is `= T_high`, not `>= T_high`.
    assert 0 in _classes_at("70") and 0 not in _classes_at("70.01")


# --- §2.3's nesting, as a computed fact (round 10, finding 4) ----------------

def _class_members(arm, t_low, t_high) -> dict:
    """{class index: the set of grid cells that class's predicate matches},
    over that arm's own family and its registered grid. Sets, because the
    question below is a containment between two classes and not a count."""
    members = {}
    for entry in _family(arm=arm)["mutations"]:
        members[entry["index"]] = {
            index for index, cell in enumerate(integrity.grid(t_low, t_high))
            if policy_mirror.predicate_matches(entry["predicate"], cell)}
    return members


def test_the_family_nests_exactly_where_section_two_three_says_it_does():
    """§2.3: "they are **not disjoint** (0 nests in 1, 2 nests in 3, 5 is
    adjacent to 3)". Until round 10 that sentence was asserted nowhere in code.

    §5.4's joint arithmetic turns on it in both directions. Containment orders
    the two classes' coverage indicators pathwise — correctness is a property of
    the RECORD (§4.1), so a record witnessing the inner class in a run witnesses
    the outer one in that run with the same correctness bit — and independence
    between pathwise-ordered indicators is available at no nondegenerate
    marginals, which is what makes §5.4's layer 1 unavailable rather than merely
    doubtful. ADJACENCY imposes nothing at all, because different records in one
    run can witness disjoint classes. So the set of containments must be exactly
    the two, at every arm's registered pair: a third would invalidate
    `score_rates.NESTED_CLASS_PAIRS` and every containment-respecting figure
    §5.4 publishes, and a missing one would mean the classes had stopped nesting.

    A class with no members would be contained in everything vacuously, so the
    emptiness is refused here rather than allowed to manufacture a containment.
    """
    for arm, (t_low, t_high) in sorted(integrity.REGISTERED_PAIRS.items()):
        members = _class_members(arm, t_low, t_high)
        # `type(...) is int`, not `isinstance`: JSON `false` is an `int` in
        # Python and would arrive here as the dict key 0, so bare equality
        # would accept a boolean index (round 8, finding 8; round 11,
        # finding 11).
        assert sorted(members) == list(range(6)) and all(
            type(index) is int for index in members), arm
        assert all(members[index] for index in members), (
            "arm %s has an empty class over its own grid; containment would be "
            "vacuous for it" % arm)
        nested = {(inner, outer) for inner in members for outer in members
                  if inner != outer and members[inner] <= members[outer]}
        assert nested == set(score_rates.NESTED_CLASS_PAIRS), (
            "arm %s at (%s, %s) nests as %s; §2.3 registers %s and §5.4's "
            "companion figures are computed from it"
            % (arm, t_low, t_high, sorted(nested),
               sorted(score_rates.NESTED_CLASS_PAIRS)))
        # The nesting is STRICT — the inner class is not the outer one under
        # another name — which is what makes the merged indicator carry two
        # classes into §5.3's five-of-six and three-of-four counts.
        for inner, outer in sorted(nested):
            assert members[inner] < members[outer], (arm, inner, outer)
    # …and the groups §5.4's companion arithmetic sums over are what those pairs
    # leave: four groups of sizes 2, 2, 1, 1, derived from the constant rather
    # than written out beside it.
    assert score_rates.class_groups() == ((0, 1), (2, 3), (4,), (5,))
