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
   are asserted separately.
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


def _answer_columns(t_low="40", t_high="70"):
    """Each landmark's ANSWER COLUMN — the registered mirror's verdict and the
    family's matching class indices over the 20 non-score combinations — keyed
    by the landmark. Two landmarks with different columns are two the six
    predicates answer differently, which is the whole of what a straddle
    means."""
    classes = _family()["mutations"]
    columns = {}
    for cell in integrity.grid(t_low, t_high):
        columns.setdefault(cell["riskScore"], []).append(
            (policy_mirror.verdict(cell, t_low, t_high),
             tuple(entry["index"] for entry in classes
                   if policy_mirror.predicate_matches(entry["predicate"],
                                                      cell))))
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
    """
    marks = integrity.landmarks("40", "70")
    assert len(marks) == 14
    for edge in NAMED_EDGES:
        assert edge in marks, (
            "§2.4 names %s as an edge the six predicates draw and the grid no "
            "longer holds it" % edge)

    columns = _answer_columns()
    for edge in NAMED_EDGES:
        below = marks[marks.index(edge) - 1]
        assert columns[edge] != columns[below], (
            "the grid answers %s and its neighbour %s identically, so nothing "
            "pins the inclusive/exclusive decision at that edge" % (edge, below))

    # Below an INCLUSIVE LOWER bound the 0.01 neighbour is the excluded point.
    assert 5 in _classes_at("39") and 5 not in _classes_at("38.99")
    # At an EXCLUSIVE UPPER bound the point AT the edge is itself the excluded
    # side, and the 0.01 point below it is the included one — the two cases
    # §2.4's withdrawn sentence had backwards.
    assert 2 in _classes_at("40.99") and 2 not in _classes_at("41")
    assert 1 in _classes_at("70.99") and 1 not in _classes_at("71")
    # …and what T_high + 0.01 buys: class 0 is `= T_high`, not `>= T_high`.
    assert 0 in _classes_at("70") and 0 not in _classes_at("70.01")
