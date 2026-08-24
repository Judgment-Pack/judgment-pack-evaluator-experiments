"""Section 3.2(iv)'s registered code path, certified.

`harness/counterfactual_shift.py` computes the counterfactual per-member shift
— section 5.2's eighteen members on Study 019's batch with the flagged runs
coded `presence-idiom-unsound` — and this suite pins what makes that
computation trustworthy: the adapter is the fixture adapter, the recode is the
registered recode, the certified-counts gate discriminates (it refused the
power analysis's own first per-arm split), and the published JSON carries the
figures the script derives rather than figures someone typed.

The pinned-binary derivation itself (extract, `opa parse`, scan over the 60
admitted policies) is exercised by running the script, not by this suite: §7
forbids invoking the binary in CI, and what the suite CAN pin without it — the
gate, the recode, the adapter, the published bytes — is the part where a silent
defect would survive a successful run."""

import json
import os

import pytest

import counterfactual_shift as cs
from e4lib import e4
from e4lib import family

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)

#: `test_family.py`'s own registered lists, restated so a drift in either file
#: is a failure here rather than two suites quietly certifying two adapters.
EMPTY_SURVIVOR_RUNS = ("A/run-025", "A/run-046")
MISSING_VECTOR_RUNS = ("B/run-026", "B/run-027", "B/run-032", "B/run-036",
                       "C/run-035", "C/run-050")


@pytest.fixture(scope="session")
def batch():
    if not os.path.exists(cs.NINETEEN_RESULTS):
        pytest.skip("Study 019's frozen attempt is not beside this study")
    with open(cs.NINETEEN_RESULTS, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


@pytest.fixture(scope="session")
def corpus():
    return cs.load_corpus()


@pytest.fixture(scope="session")
def published():
    path = os.path.join(HARNESS, cs.OUTPUT_NAME)
    if not os.path.exists(path):
        pytest.skip("harness/%s has not been published" % cs.OUTPUT_NAME)
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# The adapter is the fixture adapter
# ---------------------------------------------------------------------------

def test_the_adapter_reproduces_the_fixture_defect_lists(batch, corpus):
    """`build_units()` with no recode must be `test_family.py`'s adapter: same
    three defect branches, same affected runs, same unit count. A divergence
    here means the shift was computed over a different reading of 019's batch
    than the one Reprint 1 was certified against."""
    adapter = cs.build_units(batch, corpus)
    assert adapter["repairedEmpty"] == EMPTY_SURVIVOR_RUNS
    assert adapter["missingVector"] == MISSING_VECTOR_RUNS
    # Eighteen, not twenty-four: 019 carries 24 coded records, but section
    # 5.2 pin 4's six (`unparseable-artifact` on the SUITE artifact, policy
    # admitted) carry a defective kill block and land in `missingVector`
    # above, so only the other eighteen have no kill block at all.
    assert len(adapter["noKillBlock"]) == 18
    assert len(adapter["units"]) == 114
    assert adapter["recoded"] == ()


def test_the_recode_preempts_the_kill_block(batch, corpus):
    """Section 3.2's registered semantics: the code lands at ADMISSION, before
    scoring, so a flagged run becomes a coded unit — identity false, no kill
    record — even though 019's record carries a passing identity control and a
    full kill block. `B/run-011` is such a run (flagged with six uses,
    `identityPass: true`, kill block present), so it discriminates: an
    implementation that merely zeroed the kill counts, or kept the run in the
    per-protocol population, fails here."""
    plain = dict((unit.run_id, unit)
                 for unit in cs.build_units(batch, corpus)["units"])
    assert plain["B/run-011"].carries_kill_record
    assert plain["B/run-011"].evaluated
    assert plain["B/run-011"].identity_pass
    recoded_adapter = cs.build_units(batch, corpus,
                                     recode_flagged=frozenset(["B/run-011"]))
    assert recoded_adapter["recoded"] == ("B/run-011",)
    recoded = dict((unit.run_id, unit) for unit in recoded_adapter["units"])
    unit = recoded["B/run-011"]
    assert not unit.carries_kill_record
    assert not unit.evaluated
    assert not unit.identity_pass
    assert unit.survivors == frozenset()
    assert unit.killed_paired == {}
    # And nothing else moved: every other unit is field-identical.
    for run_id, other in plain.items():
        if run_id == "B/run-011":
            continue
        mine = recoded[run_id]
        assert (mine.carries_kill_record, mine.evaluated, mine.identity_pass,
                mine.survivors, mine.killed_paired) == (
            other.carries_kill_record, other.evaluated, other.identity_pass,
            other.survivors, other.killed_paired)


# ---------------------------------------------------------------------------
# The certified-counts gate discriminates
# ---------------------------------------------------------------------------

def test_the_certified_gate_accepts_the_measured_split():
    cs.certify_counts({"B": {"admitted": 30, "flagged": 19},
                       "C": {"admitted": 30, "flagged": 13}})


def test_the_certified_gate_refused_the_first_printed_split():
    """The mutation check, with history as the mutant: the power analysis's
    first printing said B 15 / C 17, the gate refused it, and the correction
    note in `harness/POWER-PRESENCE-IDIOM.md` exists because this refusal
    fired. A gate that accepts those numbers cannot discriminate and this test
    fails."""
    with pytest.raises(cs.ShiftError, match="SHIFT-NOT-CERTIFIED"):
        cs.certify_counts({"B": {"admitted": 30, "flagged": 15},
                           "C": {"admitted": 30, "flagged": 17}})


def test_the_certified_gate_reads_the_denominator_too():
    with pytest.raises(cs.ShiftError, match="SHIFT-NOT-CERTIFIED"):
        cs.certify_counts({"B": {"admitted": 29, "flagged": 19},
                           "C": {"admitted": 30, "flagged": 13}})


# ---------------------------------------------------------------------------
# The published block carries what the script derives
# ---------------------------------------------------------------------------

def test_the_published_flagged_set_is_the_certified_partition(published):
    runs = published["recode"]["runs"]
    assert len(runs) == 32
    assert sum(1 for run in runs if run.startswith("B/")) == 19
    assert sum(1 for run in runs if run.startswith("C/")) == 13
    assert published["recode"]["code"] == "presence-idiom-unsound"
    census = published["detectorCensus"]
    assert len(census) == 60
    assert sorted(row["run"] for row in census if row["flagged"]) == \
        sorted(runs)


def test_the_published_members_are_internally_consistent(published):
    """Thirty-six rows (eighteen members, two contrasts), every shift the
    difference of its own two point estimates, and the reject flips exactly
    the two the computation found: A-C M2 and M5, the per-protocol L1 members.
    A hand-edited figure breaks the arithmetic; a re-run that lands elsewhere
    breaks the flips."""
    members = published["members"]
    assert len(members) == 36
    assert [row["id"] for row in members[:18]] == list(family.MEMBER_IDS)
    for row in members:
        assert abs(row["shift"] -
                   (row["counterfactual"] - row["unflagged"])) < 1e-12
    flips = sorted((row["contrast"], row["id"])
                   for row in members if row["rejectFlips"])
    assert flips == [("A-C", "M2"), ("A-C", "M5")]


def test_the_published_unflagged_column_is_reprint_one(published):
    """The unflagged side must be the certified reproduction, to the printed
    digit: M17 A-C is Reprint 1's +0.1275 and the F-2 anchor p-values are
    `family.py`'s own. If these move, the script's adapter has drifted from
    the fixture the family scorer was certified against."""
    rows = dict(((row["contrast"], row["id"]), row)
                for row in published["members"])
    assert round(rows[("A-C", "M17")]["unflagged"], 4) == 0.1275
    assert round(rows[("A-C", "M1")]["unflagged"], 4) == 0.1385
    assert round(rows[("A-C", "M3")]["pUnflagged"], 4) == 0.2462
    assert round(rows[("A-C", "M9")]["pUnflagged"], 4) == 0.8883


def test_the_itt_amplification_and_pp_attenuation_are_the_published_story(
        published):
    """The measured effect the preregistration's (iv) row now states: every
    ITT member's shift is positive in both contrasts, and every A-C
    per-protocol member's shift is negative. Descriptive, direction-free
    publication — but the SIGNS are what the (iv) row says, so they are pinned
    against a silent recomputation landing elsewhere."""
    for row in published["members"]:
        if row["population"] == "ITT":
            assert row["shift"] > 0, row
        elif row["contrast"] == "A-C":
            assert row["shift"] < 0, row


def test_publishing_over_the_existing_output_is_refused(published):
    """`--write` without `--force` over the committed JSON refuses before it
    resolves a binary, so a casual re-run cannot silently replace the
    published figures."""
    with pytest.raises(cs.ShiftError, match="SHIFT-EXISTS"):
        cs.main(["--write"])
