"""The family scorer, driven against Study 019's frozen batch as a FIXTURE.

WHAT THIS FILE DOES
-------------------
PREREGISTRATION.md section 5.5 is a mandatory reprint: it states, in the
registration itself, what the eighteen registered members give **on Study 019's
data**. That makes 019's frozen `results/primary-attempt-001/RESULTS.json` an
oracle with published answers, and this file is the reproduction. It rebuilds
the corpus from 020's own frozen mutant manifests, rebuilds every unit from
019's per-run kill records, and asserts:

  * Reprint 1 — all eighteen A-C point estimates, all eighteen A-B point
    estimates, all eighteen per-arm n, and every p-value the scheme fixes;
  * Reprint 2 — all nine drop-a-pole rows, membersLeft/positive/rejecting/
    verdict;
  * Reprint 3 — the single-choice ledger's raw-L2 rows that this module can
    compute;
  * section 5.2's Fact 1 (88 of 88), Fact 2's imbalance table, both offset
    columns, the naive/corrected pair, the ANCOVA pin and the ITT x ANCOVA
    Tier D quantities;
  * section 5.6's sigma column and its MDE-at-019-n column, all eighteen rows;
  * section 5.8's corpus-structure publications that are family quantities.

It also drives every refusal `e4lib/family.py` registers. Section 7 delta 1
says the mutation check is required in the registered text, and the program's
standing lesson is that a passing test is not evidence: `MUTATIONS` at the foot
of this file names, for each refusal, the exact edit that must break it and the
test that must then fail. Those were run by hand at authoring time and the
results are recorded there.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
- **It does not make the fixture a control.** 019's batch is a STIMULUS here,
  not evidence for any 020 claim. Nothing in this file asserts anything about
  arms, effects or directions as facts about the world; it asserts that this
  implementation reproduces numbers a registration already published.
- **It does not repair 019's data silently.** The two runs section 5.2 names
  (`run-025`, `run-046`) and the six section 5.2 pin 4 names carry 019's two
  scorer defects. The adapter routes each through a NAMED repair and then
  asserts that the repair applied to exactly those runs and no others — so the
  guard is demonstrated firing on real bytes, which is stronger than a
  synthetic case and is why the synthetic cases are here too rather than
  instead.
- **It does not invent a BCa pin.** `bca_interval()` is exercised with a
  resample count and seed chosen HERE, in a test, and both are asserted to be
  absent from the registration; the test asserts the REFUSAL is what a caller
  gets by default.
- It does not run an engine, a model, or `score.py`. It imports one module.
"""
import json
import math
import os

import pytest

from e4lib import e4
from e4lib import family

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
#: The source study, resolved the way `harness/integrity.py` resolves it. There
#: is one sibling, not two.
NINETEEN = os.path.normpath(
    os.path.join(STUDY, "..", "019-authorship-across-representations"))
NINETEEN_RESULTS = os.path.join(
    NINETEEN, "results", "primary-attempt-001", "RESULTS.json")

#: 019's `perArmRuns` run ids are NOT unique: 114 records carry 40 distinct
#: `run` values, because the slot numbering restarts per arm. Every id below is
#: therefore `ARM/run`, and the adapter keys units the same way — a fixture that
#: keyed on `run` alone would silently pull three runs out of three arms every
#: time it named one. Reported as a port finding.
#: Section 5.2's Fact-1 box names these two ARM-A runs by their bare id.
EMPTY_SURVIVOR_RUNS = ("A/run-025", "A/run-046")
#: Section 5.2 pin 4 names these six: a `kill` block with neither
#: `survivorsPaired` nor `caseCount` — "B `run-026/027/032/036`, C
#: `run-035/050`; arm A zero - exactly the same six runs under both defects."
MISSING_VECTOR_RUNS = ("B/run-026", "B/run-027", "B/run-032", "B/run-036",
                       "C/run-035", "C/run-050")


# ---------------------------------------------------------------------------
# The fixture: 020's frozen corpus, 019's frozen batch
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def corpus():
    mutants = e4.load_mutants(
        os.path.join(STUDY, "mutants", "MANIFEST-jps.json"),
        os.path.join(STUDY, "mutants", "MANIFEST-rego.json"),
        os.path.join(STUDY, "mutants", "jps"),
        os.path.join(STUDY, "mutants", "rego"))
    table, _ = e4.build_pairing(mutants)
    supplied = dict((language, e4.engine_supplied_ids(mutants, language))
                    for language in family.LANGUAGES)
    return family.build_corpus(table, supplied)


@pytest.fixture(scope="session")
def batch():
    if not os.path.exists(NINETEEN_RESULTS):
        pytest.skip("Study 019's frozen attempt is not beside this study; the "
                    "family reproduction has no oracle to read")
    with open(NINETEEN_RESULTS, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


@pytest.fixture(scope="session")
def adapter(corpus, batch):
    """019's per-run records -> `family.Unit`s, with both defects named.

    Every departure from a straight read is recorded in the returned block and
    asserted against the registration's own list of affected runs."""
    units = []
    repaired_empty = []
    missing_vector = []
    no_kill_block = []
    for record in batch["perArmRuns"]:
        run_id = "%s/%s" % (record["arm"], record["run"])
        kill = record.get("kill")
        if kill is None:
            no_kill_block.append(run_id)
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), None, corpus))
            continue
        try:
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), kill, corpus))
            continue
        except family.EmptySurvivorAmbiguity:
            # Section 5.2's Fact-1 defect. `killedPaired: 0` is unambiguous on
            # its own: nothing was killed, so every paired mutant survived.
            assert kill.get("killedPaired") == 0, run_id
            repaired_empty.append(run_id)
            language = family.ARM_LANGUAGE[record["arm"]]
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"),
                {"survivorsPaired": corpus.paired_members(language),
                 "killedPaired": 0,
                 "killedPairedExcludingEngineSupplied": 0}, corpus))
        except family.FamilyError as refusal:
            # Section 5.2 pin 4's defect: a kill block with no survivor vector
            # at all. There is nothing to reconstruct from, so the run is
            # unscoreable, scores 0 in the ITT members and takes no offset.
            assert "FAMILY-NO-SURVIVOR-VECTOR" in str(refusal), run_id
            missing_vector.append(run_id)
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), None, corpus))
    return {"units": tuple(units), "repairedEmpty": tuple(repaired_empty),
            "missingVector": tuple(missing_vector),
            "noKillBlock": tuple(no_kill_block)}


@pytest.fixture(scope="session")
def units(adapter):
    return adapter["units"]


@pytest.fixture(scope="session")
def report_ac(units, corpus):
    return family.family_report(units, corpus, "A", "C")


@pytest.fixture(scope="session")
def report_ab(units, corpus):
    return family.family_report(units, corpus, "A", "B")


def _rows(report):
    return dict((row["id"], row) for row in report["members"])


# ---------------------------------------------------------------------------
# Section 5.2's structural facts, and section 5.8's corpus publications
# ---------------------------------------------------------------------------

def test_the_two_columns_are_the_registered_shape(corpus):
    """Section 5.2: 33 shared classes / 69 JPS / 62 Rego included; the exclusion
    "drops 12 of 69 paired JPS mutants and 0 of 62 paired Rego, taking the
    shared class set from 33 to 29 and the JPS/Rego paired totals to 57/55"."""
    assert len(corpus.column_indices("included")) == 33
    assert len(corpus.column_indices("excluded")) == 29
    assert corpus.shared_denominator("jps", "included") == 69
    assert corpus.shared_denominator("rego", "included") == 62
    assert corpus.shared_denominator("jps", "excluded") == 57
    assert corpus.shared_denominator("rego", "excluded") == 55
    assert corpus.symmetrised_denominator("included") == 131
    assert corpus.symmetrised_denominator("excluded") == 112


def test_the_native_denominator_is_not_the_shared_one_in_the_excluded_column(
        corpus):
    """FINDING F-1, pinned as a test so it cannot be lost.

    The Rego engine-supplied class is registered EMPTY, so an exclusion removes
    no Rego mutant and the language's own paired denominator stays 62 — while
    the SHARED denominator falls to 55 because four whole classes leave and
    take seven Rego members with them. Section 5.2's Fact-2 row names `/62` and
    publishes an offset computed with `/55`. Both numbers exist here, under two
    names, and neither is silently the answer."""
    assert corpus.native_denominator("jps", "included") == 69
    assert corpus.native_denominator("rego", "included") == 62
    assert corpus.native_denominator("jps", "excluded") == 57
    assert corpus.native_denominator("rego", "excluded") == 62
    assert corpus.shared_denominator("rego", "excluded") == 55
    assert corpus.native_denominator("rego", "excluded") \
        != corpus.shared_denominator("rego", "excluded")


def test_the_member_count_imbalance_table_is_the_registered_one(corpus):
    """Section 5.2 Fact 2: "**20 have unequal member counts across languages**
    (13 JPS-heavier, 7 Rego-heavier; extremes `d7-39-100k` 6 JPS vs 3 Rego, and
    the four-input `d1-match|...` class 1 JPS vs 4 Rego)"."""
    unequal = []
    for index in corpus.column_indices("included"):
        jps = len(corpus.members(index, "jps", "included"))
        rego = len(corpus.members(index, "rego", "included"))
        if jps != rego:
            unequal.append((jps, rego, corpus.classes[index]["witnessSet"]))
    assert len(unequal) == 20
    assert sum(1 for jps, rego, _ in unequal if jps > rego) == 13
    assert sum(1 for jps, rego, _ in unequal if jps < rego) == 7
    assert (6, 3, ("d7-39-100k",)) in unequal
    assert (1, 4, ("d1-match", "d1-match-bare", "d1-match-critical",
                   "d1-match-o3-region")) in unequal
    # Section 5.2 calls it "the four-input `d1-match|...` class", which is a
    # description, not a uniqueness claim: five classes carry four witnesses and
    # the d1-match one is the extreme in the Rego-heavier direction.
    four_input = [row for row in unequal if len(row[2]) == 4]
    assert len(four_input) == 4
    assert min(jps - rego for jps, rego, _ in unequal) == -3


def test_both_defects_of_019_fire_on_exactly_the_runs_the_prereg_names(adapter):
    """Section 7 delta 1's refusal, demonstrated on real frozen bytes.

    The empty-survivor guard is not a synthetic safeguard: run over 019's 114
    admitted runs it refuses `run-025` and `run-046` and nothing else, which is
    exactly the pair section 5.2's Fact-1 box names. The second guard refuses
    the six runs section 5.2 pin 4 names and nothing else. 18 runs carry no kill
    block at all, and 24 = 18 + 6 is the unscoreable count."""
    assert adapter["repairedEmpty"] == EMPTY_SURVIVOR_RUNS
    assert tuple(sorted(adapter["missingVector"])) == MISSING_VECTOR_RUNS
    assert len(adapter["noKillBlock"]) == 18


def test_fact_one_holds_on_every_scoreable_run(units, corpus, batch):
    """Section 5.2 Fact 1: kill reduces to witness-class coverage, 88 of 88.

    `unit_from_kill_record()` asserts this on every unit it builds, in both
    columns, so the fixture loading at all is the check; this test states the
    denominator the registration states."""
    scoreable = [unit for unit in units if unit.scoreable]
    assert len(scoreable) == 90
    identity_passing = [unit for unit in scoreable if unit.identity_pass]
    assert len(identity_passing) == 88
    checked = 0
    for unit in identity_passing:
        derived = sum(len(corpus.members(i, unit.language, "included"))
                      for i in unit.covered(corpus, "included"))
        assert derived == unit.killed_paired["included"], unit.run_id
        checked += 1
    assert checked == 88


def test_the_coverage_distribution_is_the_registered_one(units, corpus):
    """Section 5.8: "the coverage distribution (identity-passing, 88 runs:
    `{12:1, 13:2, 15:1, 16:3, 17:6, 18:8, 19:12, 20:17, 21:21, 22:9, 23:7,
    25:1}`, range 12-25, exactly one run reaching 25)"."""
    counts = {}
    for unit in units:
        if not (unit.scoreable and unit.identity_pass):
            continue
        size = len(unit.covered(corpus, "included"))
        counts[size] = counts.get(size, 0) + 1
    assert counts == {12: 1, 13: 2, 15: 1, 16: 3, 17: 6, 18: 8, 19: 12,
                      20: 17, 21: 21, 22: 9, 23: 7, 25: 1}
    assert sum(counts.values()) == 88
    assert counts[25] == 1


def test_the_union_ceilings_are_the_registered_ones(units, corpus):
    """Section 5.8: "exactly **8 paired mutants per language survive every
    identity-passing run**, so union kill is 61/69 and 54/62 and the union
    **class** ceiling is **28/33 in both languages**", and "the five
    never-covered classes by name with their sixteen mutants"."""
    for language, total in (("jps", 69), ("rego", 62)):
        universe = set(corpus.paired_members(language))
        survivors = set(universe)
        covered = set()
        for unit in units:
            if not (unit.scoreable and unit.identity_pass):
                continue
            if unit.language != language:
                continue
            reached = unit.covered(corpus, "included")
            covered.update(i for i in reached
                           if corpus.members(i, language, "included"))
            for index in reached:
                survivors -= set(corpus.members(index, language, "included"))
        assert len(survivors) == 8, language
        assert total - len(survivors) == {"jps": 61, "rego": 54}[language]
        assert len(covered) == 28, language
    never = set(corpus.column_indices("included"))
    for unit in units:
        if unit.scoreable and unit.identity_pass:
            never -= set(unit.covered(corpus, "included"))
    assert len(never) == 5
    assert sum(len(corpus.members(i, "jps", "included"))
               + len(corpus.members(i, "rego", "included"))
               for i in never) == 16


# ---------------------------------------------------------------------------
# Section 5.2's offset estimator
# ---------------------------------------------------------------------------

def test_the_registered_offsets_reproduce_in_all_four_columns(units, corpus):
    """Section 5.2's L2c definition: "On 019: off^ = -0.04956 (per-protocol,
    engine-included), -0.04846 (ITT), -0.04922 / -0.04813 excluded-column."

    All four are the SHARED-denominator reading (finding F-1) and all four come
    out to the last published digit. The ITT figures differ from the
    per-protocol ones only because the ITT population's scoreable set is 90 runs
    and the per-protocol population's is 88 — finding F-3."""
    assert round(family.offset(units, corpus, "included", "PP"), 5) == -0.04956
    assert round(family.offset(units, corpus, "included", "ITT"), 5) == -0.04846
    assert round(family.offset(units, corpus, "excluded", "PP"), 5) == -0.04922
    assert round(family.offset(units, corpus, "excluded", "ITT"), 5) == -0.04813


def test_the_other_reading_of_the_offset_is_ill_posed_and_is_shown_to_be(
        units, corpus):
    """FINDING F-1, quantified — and it is worse than a disagreement.

    Section 5.2's Fact-2 row says the engine-excluded weights are
    `|J^ex_g|/57 vs |R_g|/62` and publishes offset -0.0492 in the same row. That
    row is not merely a different reading: taken literally it is ILL-POSED,
    because the exclusion empties arm A's side of four classes and arm A then
    has no measurable coverage on them at all. The marginal can pool arm A's
    VACUOUS coverage of those four, or restrict itself to the 29 classes both
    languages can still be scored on, and the two answers differ in sign:

        registered (shared denominators)   -0.04922 (PP)  -0.04813 (ITT)
        native, vacuous coverage pooled    -0.00567 (PP)  -0.00805 (ITT)
        native, marginal over the 29       +0.03795 (PP)  +0.03711 (ITT)

    Three values for one registered symbol. The included column is unaffected:
    there the two denominators coincide and every reading agrees."""
    assert round(family.offset(units, corpus, "included", "PP", "native"), 5) \
        == -0.04956
    assert round(family.offset(units, corpus, "included", "ITT", "native"), 5) \
        == -0.04846
    assert round(family.offset(units, corpus, "excluded", "PP", "native"), 5) \
        == -0.00567
    assert round(family.offset(units, corpus, "excluded", "ITT", "native"), 5) \
        == -0.00805
    # The third value, computed through the public API so the disclosure is a
    # measurement rather than a sentence.
    for population, expected in (("PP", 0.03795), ("ITT", 0.03711)):
        scoreable = [unit for unit in family.population_units(units, population)
                     if unit.scoreable]
        indices = corpus.column_indices("excluded")
        table = corpus.weights("L2c", "excluded", "native")
        counts = dict((i, 0) for i in indices)
        for unit in scoreable:
            for index in unit.covered(corpus, "excluded"):
                if index in counts:
                    counts[index] += 1
        size = float(len(scoreable))
        restricted = math.fsum((counts[i] / size) * (table[i][0] - table[i][1])
                               for i in indices)
        assert round(restricted, 5) == expected, population
        assert restricted > 0.0 > family.offset(units, corpus, "excluded",
                                                population)


def test_the_offset_reads_no_arm_label(units, corpus):
    """Section 5.2: pi^ is "the pooled, **arm-label-free** coverage marginal".

    Swapping the two Rego arms' labels cannot move the offset, because the
    marginal pools the population's scoreable runs regardless of arm. The swap
    is B <-> C rather than a three-way rotation because a unit's LANGUAGE is a
    function of its arm: moving a JPS run into a Rego arm would change what its
    survivor vector means, which is a different corpus, not a relabelling."""
    swap = {"A": "A", "B": "C", "C": "B"}
    relabelled = []
    for unit in units:
        clone = family.Unit(unit.run_id, swap[unit.arm], unit.scoreable,
                            unit.identity_pass, unit.case_count,
                            unit.survivors, unit.killed_paired)
        relabelled.append(clone)
    assert [unit.arm for unit in relabelled] != [unit.arm for unit in units]
    for column in family.COLUMNS:
        for population in ("ITT", "PP"):
            assert (family.offset(units, corpus, column, population)
                    == family.offset(relabelled, corpus, column, population))


# ---------------------------------------------------------------------------
# Section 5.5 Reprint 1 — the eighteen members
# ---------------------------------------------------------------------------

#: Section 5.5 Reprint 1, transcribed: id -> (A-C, p, A-B, p).
REPRINT_ONE = {
    "M1": (+0.1385, 0.0137, +0.1317, 0.0229),
    "M2": (+0.0408, 0.0213, +0.0186, 0.2957),
    "M3": (+0.0161, 0.2309, +0.0213, 0.1110),
    "M4": (+0.1576, 0.0137, +0.1498, 0.0229),
    "M5": (+0.0464, 0.0213, +0.0211, 0.2957),
    "M6": (+0.0183, 0.2309, +0.0243, 0.1110),
    "M7": (+0.1438, 0.0210, +0.1376, 0.0319),
    "M8": (+0.0346, 0.1569, +0.0118, 0.6133),
    "M9": (-0.0026, 0.8823, +0.0160, 0.3077),
    "M10": (+0.1694, 0.0165, +0.1615, 0.0259),
    "M11": (+0.0469, 0.0871, +0.0199, 0.4434),
    "M12": (+0.0053, 0.7881, +0.0245, 0.1577),
    "M13": (+0.1463, 0.0210, +0.1416, 0.0296),
    "M14": (+0.0314, 0.1991, +0.0104, 0.6570),
    "M15": (-0.0036, 0.8263, +0.0142, 0.3779),
    "M16": (+0.2323, 0.0008, +0.2276, 0.0014),
    "M17": (+0.1275, None, +0.1065, None),   # published as "< 0.0001"
    "M18": (+0.0911, 0.0002, +0.1105, 0.0002),
}

#: Section 5.5 Reprint 1's cell shape, member by member.
REPRINT_ONE_SHAPE = {
    "M1": ("L1", "included", "ITT", None), "M2": ("L1", "included", "PP", None),
    "M3": ("L1", "included", "PP", "ANCOVA"),
    "M4": ("L1", "excluded", "ITT", None), "M5": ("L1", "excluded", "PP", None),
    "M6": ("L1", "excluded", "PP", "ANCOVA"),
    "M7": ("L3", "included", "ITT", None), "M8": ("L3", "included", "PP", None),
    "M9": ("L3", "included", "PP", "ANCOVA"),
    "M10": ("L3", "excluded", "ITT", None),
    "M11": ("L3", "excluded", "PP", None),
    "M12": ("L3", "excluded", "PP", "ANCOVA"),
    "M13": ("L2c", "included", "ITT", None),
    "M14": ("L2c", "included", "PP", None),
    "M15": ("L2c", "included", "PP", "ANCOVA"),
    "M16": ("L2c", "excluded", "ITT", None),
    "M17": ("L2c", "excluded", "PP", None),
    "M18": ("L2c", "excluded", "PP", "ANCOVA"),
}


def test_the_family_is_the_registered_eighteen_in_the_registered_order():
    """Section 5.2: "the crossing **{L1, L3, L2c} x {engine-included,
    engine-excluded} x {ITT-unadjusted, PP-unadjusted, PP-adjusted}**, with
    **both poles of every axis retained**" — eighteen cells, and section 5.5
    numbers them M1..M18 in this order."""
    assert len(family.MEMBERS) == 18
    assert family.MEMBER_IDS == tuple("M%d" % n for n in range(1, 19))
    for member in family.MEMBERS:
        level, column, population, adjustment = REPRINT_ONE_SHAPE[member.id]
        assert member.level == level
        assert member.column == column
        assert member.population == population
        assert (("ANCOVA" if member.adjusted else None)) == adjustment
    assert set(m.level for m in family.MEMBERS) == {"L1", "L3", "L2c"}
    assert set(m.column for m in family.MEMBERS) == {"included", "excluded"}


def test_every_member_carries_the_registered_permutation_budget():
    """Section 5.3 / section 5.5: unadjusted B = 20,000; adjusted B = 4,000;
    seed 11 for both."""
    for member in family.MEMBERS:
        assert member.permutations == (4000 if member.adjusted else 20000)
    assert family.PERMUTATIONS_UNADJUSTED == 20000
    assert family.PERMUTATIONS_ADJUSTED == 4000
    assert family.PERMUTATION_SEED == 11
    assert family.ALPHA == 0.05


def test_the_eighteen_per_arm_denominators_reproduce(report_ac):
    """Reprint 1's n column: 38/37/39 for every ITT member, 34/26/28 for every
    per-protocol member. Section 5.2 states the same pair in prose."""
    for row in report_ac["members"]:
        expected = ({"A": 38, "B": 37, "C": 39} if row["population"] == "ITT"
                    else {"A": 34, "B": 26, "C": 28})
        assert row["n"] == expected, row["id"]


def test_the_eighteen_a_minus_c_point_estimates_reproduce(report_ac):
    """THE PRIMARY REPRODUCTION. Reprint 1's A-C column, to the last published
    digit, for all eighteen members."""
    rows = _rows(report_ac)
    for member_id, expected in sorted(REPRINT_ONE.items()):
        assert round(rows[member_id]["difference"], 4) == expected[0], member_id


def test_the_eighteen_a_minus_b_point_estimates_reproduce(report_ab):
    """Reprint 1's A-B column, all eighteen. Reached here as a computation, not
    as a result: section 5.9 gates A-B behind an A-C claim, and on 019 A-C does
    not claim."""
    rows = _rows(report_ab)
    for member_id, expected in sorted(REPRINT_ONE.items()):
        assert round(rows[member_id]["difference"], 4) == expected[2], member_id


def test_the_twelve_unadjusted_p_values_reproduce_exactly(report_ac, report_ab):
    """Section 5.3's unadjusted scheme, fixed to the last digit.

    Twenty-four published p-values (twelve members x two contrasts) reproduce
    exactly under `random.Random(11)`, repeated `shuffle()` of one persistent
    payload list, the two-sided `|d*| >= |d_obs|` count and `(count+1)/(B+1)`.
    That is what identifies the scheme; finding F-2 is that the same stream does
    not reproduce the adjusted six."""
    ac, ab = _rows(report_ac), _rows(report_ab)
    checked = 0
    for member in family.MEMBERS:
        if member.adjusted:
            continue
        expected = REPRINT_ONE[member.id]
        if expected[1] is None:                     # M17, published "< 0.0001"
            assert ac[member.id]["p"] < 0.0001
            assert ab[member.id]["p"] < 0.0001
        else:
            assert round(ac[member.id]["p"], 4) == expected[1], member.id
            assert round(ab[member.id]["p"], 4) == expected[3], member.id
        checked += 1
    assert checked == 12


def test_the_six_adjusted_p_values_agree_in_every_decision_but_not_every_digit(
        report_ac, report_ab):
    """FINDING F-2, pinned rather than papered over.

    The adjusted members' Monte-Carlo p-values differ from Reprint 1's in the
    third decimal — the generating script is not in the tree, so the residual is
    a different B = 4,000 stream, not a different estimator. What must hold, and
    does, is that every reject/not-reject decision at alpha = 0.05 agrees, which
    is the only thing section 5.9 row 4 reads. The observed gaps are asserted
    here so that a future change to the scheme cannot hide inside them."""
    ac, ab = _rows(report_ac), _rows(report_ab)
    gaps = []
    for member in family.MEMBERS:
        if not member.adjusted:
            continue
        expected = REPRINT_ONE[member.id]
        for row, published in ((ac[member.id], expected[1]),
                               (ab[member.id], expected[3])):
            assert (row["p"] < family.ALPHA) == (published < family.ALPHA), \
                member.id
            gaps.append(abs(row["p"] - published))
    assert len(gaps) == 12
    assert max(gaps) < 0.02


def test_the_eighteen_sigmas_and_mdes_reproduce(report_ac):
    """Section 5.6's dispersion table: sigma and "MDE @ 019 n", all eighteen
    rows, pooled within-arm and unbiased (N - k), residual N - 4 for the
    adjusted members, MDE = 2.8016 * sigma * sqrt(1/n_A + 1/n_C)."""
    expected = {
        "M1": (0.25427, 0.1624), "M4": (0.28934, 0.1848),
        "M7": (0.28439, 0.1816), "M10": (0.32159, 0.2054),
        "M13": (0.28966, 0.1850), "M16": (0.29826, 0.1905),
        "M2": (0.06938, 0.0496), "M5": (0.07895, 0.0564),
        "M8": (0.09397, 0.0672), "M11": (0.10516, 0.0752),
        "M14": (0.09040, 0.0646), "M17": (0.09479, 0.0678),
        "M3": (0.05068, 0.0362), "M6": (0.05767, 0.0412),
        "M9": (0.06114, 0.0437), "M12": (0.06849, 0.0490),
        "M15": (0.06049, 0.0432), "M18": (0.06420, 0.0459),
    }
    rows = _rows(report_ac)
    assert len(expected) == 18
    for member_id, (sigma, mde) in sorted(expected.items()):
        assert round(rows[member_id]["sigma"], 5) == sigma, member_id
        assert round(rows[member_id]["mde"], 4) == mde, member_id


# ---------------------------------------------------------------------------
# Section 5.5 Reprint 2, and the verdict
# ---------------------------------------------------------------------------

def test_the_verdict_on_019s_batch_is_the_registered_one(report_ac):
    """Section 5.5: "**A-C: direction unanimity FAILS (16 positive, 2
    negative). Test unanimity FAILS (10 of 18 reject).** Tier C's verdict on
    019's batch: INDETERMINATE-BY-DISAGREEMENT."
    """
    block = report_ac["verdict"]
    assert block["memberCount"] == 18
    assert block["members"] == list(family.MEMBER_IDS)
    assert block["claim"] is False
    assert block["sign"] == "none"
    assert block["arms"] == ["A", "C"]
    assert block["positive"] == 16
    assert block["negative"] == 2
    assert block["rejecting"] == 10
    assert block["signUnanimous"] is False
    assert block["allReject"] is False
    assert block["verdict"] == family.INDETERMINATE
    assert block["direction"] == "none"
    negatives = sorted(row["id"] for row in report_ac["members"]
                       if row["sign"] < 0)
    assert negatives == ["M15", "M9"]


def test_the_a_minus_b_step_is_unanimous_in_direction_and_still_short(report_ab):
    """Section 5.5: "A-B is unanimous in direction (18 positive) but only 8 of
    18 reject - and it is unreachable anyway, gated behind A-C."
    """
    block = report_ab["verdict"]
    assert block["positive"] == 18
    assert block["rejecting"] == 8
    assert block["signUnanimous"] is True
    assert block["allReject"] is False
    assert block["verdict"] == family.INDETERMINATE
    assert block["claim"] is False
    assert block["sign"] == "+"
    assert block["arms"] == ["A", "B"]


def test_the_drop_a_pole_table_reproduces_row_for_row(report_ac):
    """Section 5.5 Reprint 2, all nine rows, including "the one exception":
    an ITT-only family (per-protocol dropped) would have CLAIMED on 019."""
    expected = [
        ("L1", 12, 10, 6, family.INDETERMINATE),
        ("L3", 12, 11, 8, family.INDETERMINATE),
        ("L2c", 12, 11, 6, family.INDETERMINATE),
        ("engine-included", 9, 9, 6, family.INDETERMINATE),
        ("engine-excluded", 9, 7, 4, family.INDETERMINATE),
        ("ITT", 12, 10, 4, family.INDETERMINATE),
        ("per-protocol", 6, 6, 6, family.CLAIM),
        ("adjusted", 12, 12, 9, family.INDETERMINATE),
        ("unadjusted", 6, 4, 1, family.INDETERMINATE),
    ]
    actual = [(row["poleDropped"], row["membersLeft"], row["positive"],
               row["rejecting"], row["verdict"])
              for row in report_ac["dropAPole"]]
    assert actual == expected


# ---------------------------------------------------------------------------
# Section 5.2's pinned definitions, and Reprint 3
# ---------------------------------------------------------------------------

def test_the_ancova_is_pinned_to_the_byte(units, corpus):
    """Section 5.2 pin 2: "On 019 at L1/per-protocol: slope **b = +0.02332**,
    arm covariate means A 20.882 / B 21.000 / C 19.821, adjusted means A 0.6106
    / B 0.5893 / C 0.5945." Three-arm pooled slope, grand covariate mean."""
    member = family.MEMBERS_BY_ID["M3"]
    rows = family.member_outcomes(member, units, corpus)
    fit = family.ancova(rows)
    assert round(fit["slope"], 5) == 0.02332
    assert round(fit["armCovariateMeans"]["A"], 3) == 20.882
    assert round(fit["armCovariateMeans"]["B"], 3) == 21.000
    assert round(fit["armCovariateMeans"]["C"], 3) == 19.821
    assert round(fit["adjustedMeans"]["A"], 4) == 0.6106
    assert round(fit["adjustedMeans"]["B"], 4) == 0.5893
    assert round(fit["adjustedMeans"]["C"], 4) == 0.5945


def test_the_two_arm_slope_variant_is_the_tier_d_number(units, corpus):
    """Section 5.2 pin 2: "The two-arm-only slope variant gives A-C = +0.0185
    against the three-arm +0.0161 - immaterial there, decisive as a
    registration matter. **Pin the three-arm form; publish the pairwise variant
    in Tier D.**" The pairwise variant is `ancova()` over the two-arm rows."""
    member = family.MEMBERS_BY_ID["M3"]
    rows = family.member_outcomes(member, units, corpus)
    two_arm = [row for row in rows if row[0] in ("A", "C")]
    assert round(family.adjusted_difference(rows, "A", "C"), 4) == 0.0161
    assert round(family.adjusted_difference(two_arm, "A", "C"), 4) == 0.0185


def test_the_empty_survivor_trap_moves_the_contrast_by_the_registered_amount(
        units, corpus, adapter):
    """Section 5.2's Fact-1 box: "this single schema trap moves the group-level
    ITT A-C contrast from **+0.19112 (naive) to +0.13849 (corrected)** -
    magnitude **0.0526** ... correcting the trap **lowers** A-C."

    The naive reading is reconstructed here by doing exactly what the trap does:
    treating an empty survivor vector as "everything killed". It is built by
    hand, in a test, and never by `family.py`."""
    member = family.MEMBERS_BY_ID["M1"]
    corrected = family.unadjusted_difference(
        family.member_outcomes(member, units, corpus), "A", "C")
    assert round(corrected, 5) == 0.13849
    naive_rows = []
    trapped = set(adapter["repairedEmpty"])
    assert trapped == set(EMPTY_SURVIVOR_RUNS)
    size = len(corpus.column_indices("included"))
    for unit in units:
        if unit.run_id in trapped:
            value = 1.0                       # the trap: no survivors => 33/33
        elif unit.scoreable:
            value = len(unit.covered(corpus, "included")) / float(size)
        else:
            value = 0.0
        naive_rows.append((unit.arm, value, unit.case_count))
    naive = family.unadjusted_difference(naive_rows, "A", "C")
    assert round(naive, 5) == 0.19112
    assert round(naive - corrected, 4) == 0.0526


def test_the_itt_ancova_tier_d_quantities_reproduce(units, corpus):
    """Section 5.2: "with `caseCount = 0` imputed, the ITT group-level A-C moves
    from **+0.1385 to -0.0201** and pooled within-arm SD collapses from
    **0.25427 to 0.09652**."

    These are the six Tier D quantities the refused cell is published as. They
    are computed HERE, by hand, from an explicitly imputed covariate — which is
    the point: `family.py` refuses to compute them as a MEMBER, and Tier D
    publishes them with section 5.2's covert-population sentence attached."""
    member = family.MEMBERS_BY_ID["M1"]
    rows = family.member_outcomes(member, units, corpus)
    imputed = [(arm, value, 0 if covariate is None else covariate)
               for arm, value, covariate in rows]
    assert round(family.unadjusted_difference(rows, "A", "C"), 4) == 0.1385
    assert round(family.adjusted_difference(imputed, "A", "C"), 4) == -0.0201
    assert round(family.pooled_within_arm_sd(rows), 5) == 0.25427
    assert round(family.residual_sd(imputed), 5) == 0.09652


def test_the_single_choice_ledgers_raw_l2_rows_reproduce(units, corpus):
    """Section 5.5 Reprint 3: 019's own registered quantity, raw L2, no offset.
    The four unadjusted rows are the ones this module computes directly."""
    expected = {("ITT", "included"): 0.1004, ("ITT", "excluded"): 0.1867,
                ("PP", "included"): -0.0182, ("PP", "excluded"): 0.0783}
    for (population, column), value in sorted(expected.items()):
        rows = [(unit.arm,
                 family.raw_outcome(unit, corpus, "L2c", column, "native"),
                 unit.case_count)
                for unit in family.population_units(units, population)]
        assert round(family.unadjusted_difference(rows, "A", "C"), 4) == value


def test_the_offset_is_taken_by_the_arm_a_runs_that_carry_a_kill_record(
        units, corpus):
    """FINDING F-3, pinned. Reprint 1's M13 (+0.1463) and M16 (+0.2323) are
    reproducible only if the ITT offset is estimated over the 90 runs carrying a
    kill record and subtracted from the 36 arm-A runs that carry one — not from
    the 34 that also pass the identity control. Section 5.2's "unscoreable runs
    ... take no offset" is therefore about the 24 runs with no kill record."""
    carrying = [unit for unit in units if unit.scoreable]
    assert len(carrying) == 90
    assert len([unit for unit in carrying if unit.arm == "A"]) == 36
    assert len([unit for unit in carrying if unit.identity_pass]) == 88
    member = family.MEMBERS_BY_ID["M13"]
    rows = family.member_outcomes(member, units, corpus)
    shifted = [value for arm, value, _ in rows if arm == "A" and value != 0.0]
    assert len(shifted) == 36


# ---------------------------------------------------------------------------
# The refusals — one test each, every one mutation-checked (see MUTATIONS)
# ---------------------------------------------------------------------------

def test_the_itt_ancova_cell_is_refused_and_never_falls_back(units, corpus):
    """Section 5.2: "**The scorer must refuse rather than fall back**, and a
    harness test drives that refusal."

    The refusal must arrive BEFORE any number exists. The check below is that
    the refusal does not coincide with the complete-case cell: a fallback
    implementation would silently return M2's rows, so the test asserts the
    exception, not merely that the two differ."""
    forged = family.Member("M-ITT-ANCOVA", "L1", "included", "ITT", True)
    with pytest.raises(family.IttAncovaRefused) as caught:
        family.member_outcomes(forged, units, corpus)
    assert "FAMILY-ITT-ANCOVA-REFUSED" in str(caught.value)
    assert ("ITT", True) in family.REFUSED_CELLS
    with pytest.raises(family.IttAncovaRefused):
        family.extend_family([forged])


def test_the_empty_survivor_encoding_is_refused_at_read_time(corpus):
    """Section 7 delta 1: `survivorsPaired: []` with `killedPaired: 0` is
    refused rather than read as 33/33."""
    with pytest.raises(family.EmptySurvivorAmbiguity) as caught:
        family.unit_from_kill_record(
            "run-synthetic", "A", False, 21,
            {"survivorsPaired": [], "killedPaired": 0,
             "killedPairedExcludingEngineSupplied": 0}, corpus)
    assert "FAMILY-EMPTY-SURVIVOR-AMBIGUOUS" in str(caught.value)
    honest = family.unit_from_kill_record(
        "run-synthetic", "A", True, 21,
        {"survivorsPaired": [], "killedPaired": 69,
         "killedPairedExcludingEngineSupplied": 57}, corpus)
    assert len(honest.covered(corpus, "included")) == 33


def test_a_kill_block_with_no_survivor_vector_is_refused(corpus):
    """Section 5.1: the scorer "emits an explicit per-mutant survivor vector for
    every admitted run"; a block without one is 019's second defect and cannot
    be read as an absence of survivors."""
    with pytest.raises(family.FamilyError) as caught:
        family.unit_from_kill_record("run-synthetic", "B", True, 12,
                                     {"killedPaired": 40}, corpus)
    assert "FAMILY-NO-SURVIVOR-VECTOR" in str(caught.value)


def test_an_empty_arm_denominator_is_refused_not_called_indeterminate(
        units, corpus):
    """Section 5.1: "**Each member's per-arm denominator must be positive**; a
    contrast over an empty arm is not INDETERMINATE, it is not computed at all,
    and the outcome falls to the rows above."
    """
    without_c = [unit for unit in units if unit.arm != "C"]
    with pytest.raises(family.EmptyArmDenominator) as caught:
        family.score_member(family.MEMBERS_BY_ID["M1"], without_c, corpus,
                            "A", "C")
    assert "FAMILY-EMPTY-ARM" in str(caught.value)
    assert family.INDETERMINATE not in str(caught.value)


def test_a_short_family_cannot_be_given_a_verdict(report_ac):
    """Section 5.2: a maintainer "may **never remove one**", and removal moves
    the intersection-union test toward CLAIM. A verdict over seventeen members
    is refused, not warned about — and the seventeen chosen here are the ones
    that WOULD have claimed, so the test fails loudly if the refusal is lost."""
    rows = [row for row in report_ac["members"]
            if row["id"] not in ("M3", "M6", "M8", "M9", "M11", "M12", "M14",
                                 "M15")]
    assert len(rows) == 10
    assert all(row["rejects"] and row["sign"] > 0 for row in rows)
    with pytest.raises(family.MembershipError) as caught:
        family.verdict(rows)
    assert "FAMILY-MEMBERSHIP-INCOMPLETE" in str(caught.value)


def test_membership_is_append_only(units, corpus):
    """Section 5.2: additions are permitted, removals are not, and an addition
    is monotone toward INDETERMINATE."""
    addition = family.Member("M19", "L1", "included", "PP", False)
    extended = family.extend_family([addition])
    assert len(extended) == 19
    assert extended[:18] == family.MEMBERS
    with pytest.raises(family.MembershipError):
        family.extend_family([family.MEMBERS_BY_ID["M1"]])


def test_a_bca_interval_without_a_pin_is_refused(units, corpus):
    """Section 5.3 registers "BCa bootstrap, per member, coverage stated as
    approximate" and pins neither B nor a seed, and `PINS.json` carries no
    family member. The default is a refusal, not a chosen number.

    The 200 resamples below are a NUMBER CHOSEN IN THIS TEST to prove the code
    path runs. It is not a registration and nothing publishes it."""
    member = family.MEMBERS_BY_ID["M2"]
    rows = family.member_outcomes(member, units, corpus)
    with pytest.raises(family.IntervalUnpinned) as caught:
        family.bca_interval(rows, "A", "C", member.adjusted)
    assert "FAMILY-BCA-UNPINNED" in str(caught.value)
    block = family.bca_interval(rows, "A", "C", member.adjusted,
                               resamples=200, seed=1)
    assert block["lower"] <= block["point"] <= block["upper"]
    assert block["coverage"] == "approximate"
    assert "exact" not in block["method"]


# ---------------------------------------------------------------------------
# Section 4.2.4's identical-in-every-branch rule
# ---------------------------------------------------------------------------

def _shape(node):
    if isinstance(node, dict):
        return dict((key, _shape(value)) for key, value in sorted(node.items()))
    if isinstance(node, list):
        return [_shape(item) for item in node]
    return type(node).__name__


def test_the_published_quantity_set_is_identical_in_every_branch(
        units, corpus, report_ac):
    """Brief section 4.2.4 / section 5.8: "the published quantity set is
    **identical in every branch**, registered so the outcome cannot change what
    is reported."

    A synthetic batch that CLAIMS is built by shifting every arm-A unit's
    coverage to the ceiling, and its report is compared with 019's
    INDETERMINATE one structurally: same keys, same members, same tables, same
    types, everything present. The only difference permitted is the values."""
    forced = []
    for unit in units:
        if unit.arm == "A" and unit.scoreable:
            forced.append(family.Unit(unit.run_id, unit.arm, True,
                                      unit.identity_pass, unit.case_count,
                                      (), {}))
        else:
            forced.append(unit)
    claiming = family.family_report(forced, corpus, "A", "C")
    assert claiming["verdict"]["verdict"] == family.CLAIM
    assert claiming["verdict"]["direction"] == "positive"
    assert report_ac["verdict"]["verdict"] == family.INDETERMINATE
    assert _shape(claiming) == _shape(report_ac)
    assert ([row["id"] for row in claiming["members"]]
            == [row["id"] for row in report_ac["members"]]
            == list(family.MEMBER_IDS))
    assert ([row["poleDropped"] for row in claiming["dropAPole"]]
            == [row["poleDropped"] for row in report_ac["dropAPole"]])
    assert sorted(claiming["offsets"]) == sorted(report_ac["offsets"])


def test_the_report_publishes_both_readings_of_the_offset(report_ac):
    """Finding F-1's disclosure obligation: the block carries both readings in
    both columns and both populations, and names which one produced the members."""
    assert len(report_ac["offsets"]) == 8
    assert report_ac["offsetReadingUsed"] == "shared"
    assert report_ac["outcomeWeightingUsed"] == "native"
    assert report_ac["corpus"]["sharedClasses"] == {"included": 33,
                                                    "excluded": 29}


def test_the_report_names_the_refused_cell_whatever_the_verdict(report_ac):
    """Section 5.2's two argued-out cells are part of the published record; the
    ITT x ANCOVA one appears in every report as a refusal with its reason."""
    refused = report_ac["refusedCells"]
    assert len(refused) == 1
    assert refused[0]["population"] == "ITT"
    assert refused[0]["adjustment"] == "ANCOVA"
    assert "covert change of population" in refused[0]["reason"]


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_a_members_p_value_does_not_depend_on_what_ran_before_it(units, corpus):
    """Every test seeds its own `random.Random`, so scoring M2 alone and
    scoring it inside the family give the same count to the integer."""
    member = family.MEMBERS_BY_ID["M2"]
    first = family.score_member(member, units, corpus, "A", "C")
    second = family.score_member(member, units, corpus, "A", "C")
    assert first["permutationCount"] == second["permutationCount"]
    assert first["p"] == second["p"]
    assert first["difference"] == second["difference"]


def test_unit_order_does_not_move_a_point_estimate(units, corpus):
    """The point estimates are `math.fsum` totals over fixed class orderings, so
    reversing the unit order cannot move a published figure."""
    member = family.MEMBERS_BY_ID["M13"]
    forward = family.unadjusted_difference(
        family.member_outcomes(member, units, corpus), "A", "C")
    backward = family.unadjusted_difference(
        family.member_outcomes(member, tuple(reversed(units)), corpus),
        "A", "C")
    assert forward == backward


# ---------------------------------------------------------------------------
# The mutation record — section 7 delta 1: "the mutation check is required"
# ---------------------------------------------------------------------------

#: Each row is (refusal, the edit that must break it, the test that must then
#: fail). Every row below was RUN: the mutant was written, `py_compile`d, the
#: named test was watched to FAIL, `e4lib/family.py` was restored and its
#: sha256 re-checked against the pre-mutation digest
#: `5b1858b01208e6b963b3208685cd37a79e3a53562e636ee4a73aca5938e4e9d5`. All
#: seven runs discriminated. `NON_DISCRIMINATING` below records the one edit
#: that does NOT, because a safeguard that cannot be shown to fail must be
#: labelled as one rather than left looking checked.
MUTATIONS = (
    ("FAMILY-ITT-ANCOVA-REFUSED",
     "e4lib/family.py: REFUSED_CELLS = ()",
     "test_the_itt_ancova_cell_is_refused_and_never_falls_back"),
    ("FAMILY-EMPTY-SURVIVOR-AMBIGUOUS",
     "e4lib/family.py: unit_from_kill_record(), the derived-vs-recorded "
     "comparison becomes `if False:`",
     "test_the_empty_survivor_encoding_is_refused_at_read_time, "
     "test_both_defects_of_019_fire_on_exactly_the_runs_the_prereg_names"),
    ("FAMILY-NO-SURVIVOR-VECTOR",
     "e4lib/family.py: unit_from_kill_record(), both refusals replaced by "
     "`survivors = kill.get('survivorsPaired') or []`",
     "test_a_kill_block_with_no_survivor_vector_is_refused"),
    ("FAMILY-EMPTY-ARM",
     "e4lib/family.py: EVERY `raise EmptyArmDenominator(` becomes an "
     "assignment - see NON_DISCRIMINATING for why one site is not enough",
     "test_an_empty_arm_denominator_is_refused_not_called_indeterminate"),
    ("FAMILY-MEMBERSHIP-INCOMPLETE",
     "e4lib/family.py: verdict(), `missing = []`",
     "test_a_short_family_cannot_be_given_a_verdict"),
    ("FAMILY-BCA-UNPINNED",
     "e4lib/family.py: bca_interval(), defaults become `resamples=2000, "
     "seed=11`",
     "test_a_bca_interval_without_a_pin_is_refused"),
)

#: THE ONE EDIT THAT DOES NOT DISCRIMINATE, recorded rather than hidden.
#: Neutralising `score_member()`'s zero-denominator loop alone leaves the test
#: PASSING, because `unadjusted_difference()` and `_mean()` refuse the same
#: condition one and two layers down. The guard is defence in depth and the
#: test cannot tell which layer answered; only removing every layer makes it
#: fail. Anyone tightening this test should assert WHICH layer raised.
NON_DISCRIMINATING = (
    ("FAMILY-EMPTY-ARM",
     "e4lib/family.py: score_member(), `if counts.get(arm, 0) < 0:`",
     "test_an_empty_arm_denominator_is_refused_not_called_indeterminate",
     "still passes - the refusal arrives from unadjusted_difference()/_mean()"),
)


def test_every_registered_refusal_has_a_mutation_row():
    """The standing lesson, enforced: a refusal with no recorded mutation check
    is a safeguard nobody has shown can fail."""
    codes = set(row[0] for row in MUTATIONS)
    assert codes == {"FAMILY-ITT-ANCOVA-REFUSED",
                     "FAMILY-EMPTY-SURVIVOR-AMBIGUOUS",
                     "FAMILY-NO-SURVIVOR-VECTOR",
                     "FAMILY-EMPTY-ARM",
                     "FAMILY-MEMBERSHIP-INCOMPLETE",
                     "FAMILY-BCA-UNPINNED"}
    for code, mutation, tests in MUTATIONS:
        assert mutation.startswith("e4lib/family.py:")
        for name in tests.split(", "):
            assert name.strip() in globals(), name
    for code, mutation, name, outcome in NON_DISCRIMINATING:
        assert code in codes
        assert name in globals(), name
        assert "still passes" in outcome
    assert math.isclose(family.ALPHA, 0.05)
