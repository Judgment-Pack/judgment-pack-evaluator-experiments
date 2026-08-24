"""E4 — the X1 filter, the pairing rule, the identity control and the tau cut.

The X1 predicate gets its own block, because section 4 makes it an exclusion
class AND a registered inexpressibility result: a filter that is a condition
inside a loop is a filter nobody can check against the registration, and a
filter that disagrees with `design/gold/check_gold.py` means gold contains a row
the scorer would have excluded.
"""
import json
import os

import pytest

from e4lib import e4

_STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- X1, the registered exclusion class -------------------------------------
#
# Section 4: {new vendor yes; risk in [40,70); LOW country with spend
# unreadable, or country unreadable with spend <= 100,000.00}.

def signature(**overrides):
    base = {"risk": None, "spend": None, "sanctions": "CLEAR", "country": "LOW",
            "newVendor": "yes", "critical": "no", "prior": "no",
            "finEvidence": "present", "insurance": "present"}
    base.update(overrides)
    return base


def test_the_low_country_unreadable_spend_limb_is_x1():
    assert e4.in_x1(signature(risk="40", country="LOW", spend=None))
    assert e4.in_x1(signature(risk="69", country="LOW", spend=None))


def test_the_unreadable_country_small_spend_limb_is_x1():
    assert e4.in_x1(signature(risk="55", country=None, spend="100000.00"))
    assert e4.in_x1(signature(risk="55", country=None, spend="0.01"))


def test_the_spend_cap_is_inclusive_and_the_next_cent_is_outside():
    assert e4.in_x1(signature(risk="55", country=None, spend="100000.00"))
    assert not e4.in_x1(signature(risk="55", country=None, spend="100000.01"))


def test_the_risk_band_is_closed_below_and_open_above():
    assert not e4.in_x1(signature(risk="39", country="LOW", spend=None))
    assert e4.in_x1(signature(risk="40", country="LOW", spend=None))
    assert e4.in_x1(signature(risk="69", country="LOW", spend=None))
    assert not e4.in_x1(signature(risk="70", country="LOW", spend=None))


def test_an_established_vendor_is_never_in_x1():
    assert not e4.in_x1(signature(risk="55", newVendor="no", country="LOW",
                                  spend=None))


def test_an_unreadable_risk_is_not_in_a_band():
    """The class is defined over a risk BAND, and a point with no readable risk
    is not in a band — the same reading `design/gold/check_gold.py` enforces
    over the gold suite, which is why the two cannot disagree about what is
    excluded."""
    assert not e4.in_x1(signature(risk=None, country="LOW", spend=None))
    assert not e4.in_x1(signature(risk="not a number", country="LOW",
                                  spend=None))


def test_a_readable_low_country_spend_is_outside_x1():
    assert not e4.in_x1(signature(risk="55", country="LOW", spend="50000.00"))


def test_a_high_country_with_unreadable_spend_is_outside_x1():
    assert not e4.in_x1(signature(risk="55", country="HIGH", spend=None))


def test_the_x1_numbers_are_the_prose_numbers():
    assert str(e4.X1_RISK_FLOOR) == "40"
    assert str(e4.X1_RISK_CEILING) == "70"
    assert str(e4.X1_SPEND_CAP) == "100000.00"
    assert e4.X1_LOW_COUNTRY == "LOW"


def test_a_json_number_reaches_the_predicate_without_a_float_round_trip():
    """Authored matrix cases may carry JSON numbers rather than decimal
    strings; `Decimal(str(v))` reads them exactly."""
    assert e4.in_x1(signature(risk=55, country=None, spend=100000.00)) is True
    assert e4.in_x1(signature(risk=55, country=None, spend=100000.01)) is False


def test_the_registered_exclusion_registry_is_empty_and_excludes_nothing():
    """ROUND-1 R1-2's consequence in this module. X1 was retired when the arm-A
    reference was repaired, and `cert_offgold.py`'s own registry is empty — so
    the exclusion machinery is kept, the registry is data, and the per-run
    excluded count §4 publishes is a MEASURED ZERO rather than a filter nobody
    applied. `in_x1()` survives as the retired predicate and gates nothing."""
    assert e4.REGISTERED_EXCLUSION_CLASSES == {}
    was_x1 = ("c1", {}, {}, ("outcome", "review", ()), True,
              signature(risk="55", country="LOW", spend=None))
    ordinary = ("c2", {}, {}, ("outcome", "approve", ()), True,
                signature(risk="10", country="LOW", spend="1.00"))
    scored, excluded = e4.partition_excluded([was_x1, ordinary])
    assert [case[0] for case in scored] == ["c1", "c2"]
    assert excluded == []
    # The predicate still answers, so "the repair moved exactly these cells"
    # stays re-measurable.
    assert e4.in_x1(was_x1[5]) is True


def test_partition_excluded_applies_a_registered_class_once(monkeypatch):
    """And when a class IS registered, it is applied in one place, so identity
    and kill see the same case set by construction."""
    monkeypatch.setattr(e4, "REGISTERED_EXCLUSION_CLASSES",
                        {"X9": lambda sig: sig.get("country") == "LOW"})
    inside = ("c1", {}, {}, None, True, signature(country="LOW"))
    outside = ("c2", {}, {}, None, True, signature(country="HIGH"))
    scored, excluded = e4.partition_excluded([inside, outside])
    assert [case[0] for case in scored] == ["c2"]
    assert excluded == ["c1"]


# --- the alignment map ------------------------------------------------------

def test_align_expected_keeps_only_the_scored_surface():
    """Section 5 puts `handoff` and `trace[]` outside every endpoint, so they
    are not read at all — no later filter can forget to drop them."""
    aligned = e4.align_expected({
        "kind": "outcome", "outcomeId": "review",
        "handoff": {"state": "pending", "target": "committee"},
        "trace": [{"rule": "r-d3"}]})
    assert aligned == ("outcome", "review", ())


def test_align_expected_sorts_reasons_as_a_set():
    aligned = e4.align_expected({"kind": "unresolved",
                                 "reasons": ["unknown", "no-match"]})
    assert aligned == ("unresolved", None, ("no-match", "unknown"))


def test_an_unreadable_expectation_is_none_rather_than_a_guess():
    assert e4.align_expected(None) is None
    assert e4.align_expected({"kind": "something-else"}) is None
    assert e4.align_expected("outcome") is None


# --- the mutant sets and the pairing ----------------------------------------

@pytest.fixture
def mutant_tree(tmp_path):
    """A miniature registry pair with the shapes the real manifests carry."""
    jps_dir = tmp_path / "jps"
    rego_dir = tmp_path / "rego"
    jps_dir.mkdir()
    rego_dir.mkdir()
    jps = [
        {"id": "m-a-001", "validates": True, "witnessSet": ["g2", "g1"],
         "notAdequate": False, "class": "operator-flip"},
        {"id": "m-a-002", "validates": True, "witnessSet": ["g3"],
         "notAdequate": False, "class": "boundary-shift"},
        {"id": "m-a-003", "validates": True, "witnessSet": [],
         "notAdequate": True, "class": "outcome-swap"},
        {"id": "m-a-004", "validates": False, "witnessSet": [],
         "notAdequate": True, "class": "dropped"},
    ]
    rego = {"mutants": [
        {"id": "m-b-001", "status": "valid", "file": "m-b-001.rego",
         "witnessSet": ["g1", "g2"], "notAdequate": False,
         "mutationClass": "operator-flip"},
        {"id": "m-b-002", "status": "valid", "file": "m-b-002.rego",
         "witnessSet": ["g4"], "notAdequate": False,
         "mutationClass": "guard-deletion"},
        {"id": "m-b-003", "status": "valid", "file": "m-b-003.rego",
         "witnessSet": [], "notAdequate": True, "mutationClass": "default-swap"},
    ]}
    for entry in jps:
        (jps_dir / (entry["id"] + ".json")).write_text("{}")
    for entry in rego["mutants"]:
        (rego_dir / entry["file"]).write_text("package study\n")
    jps_manifest = tmp_path / "MANIFEST-jps.json"
    rego_manifest = tmp_path / "MANIFEST-rego.json"
    jps_manifest.write_text(json.dumps(jps))
    rego_manifest.write_text(json.dumps(rego))
    return (str(jps_manifest), str(rego_manifest), str(jps_dir), str(rego_dir))


def test_load_mutants_keeps_manifest_order_and_valid_mutants_only(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    assert [record["id"] for record in mutants["jps"]] == \
        ["m-a-001", "m-a-002", "m-a-003"]
    assert [record["id"] for record in mutants["rego"]] == \
        ["m-b-001", "m-b-002", "m-b-003"]


def test_load_mutants_sorts_the_witness_set_so_pairing_is_order_free(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    assert mutants["jps"][0]["witnessSet"] == ["g1", "g2"]
    assert mutants["jps"][0]["witnessKey"] == ("g1", "g2")


def test_a_missing_mutant_file_refuses(mutant_tree, tmp_path):
    jps_manifest, rego_manifest, jps_dir, rego_dir = mutant_tree
    (tmp_path / "jps" / "m-a-002.json").unlink()
    with pytest.raises(e4.E4Error) as raised:
        e4.load_mutants(jps_manifest, rego_manifest, jps_dir, rego_dir)
    assert str(raised.value).startswith("E4-MISSING-MUTANT")


def test_a_witness_set_disagreeing_with_not_adequate_refuses(tmp_path,
                                                             mutant_tree):
    jps_manifest, rego_manifest, jps_dir, rego_dir = mutant_tree
    broken = json.loads(open(jps_manifest).read())
    broken[0]["notAdequate"] = True
    open(jps_manifest, "w").write(json.dumps(broken))
    with pytest.raises(e4.E4Error) as raised:
        e4.load_mutants(jps_manifest, rego_manifest, jps_dir, rego_dir)
    assert str(raised.value).startswith("E4-WITNESS-DISAGREEMENT")


def test_pairing_is_identical_sorted_witness_sets(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    table, paired = e4.build_pairing(mutants)
    assert paired["jps"] == {"m-a-001"}
    assert paired["rego"] == {"m-b-001"}
    row = [entry for entry in table if entry["witnessSet"] == ["g1", "g2"]][0]
    assert row["countedInPairedSubset"] is True


def test_the_empty_witness_group_is_degenerate_and_never_pairs(mutant_tree):
    """Section 4: "the empty witness set is degenerate and never pairs" — it
    pairs on the ABSENCE of a discriminating gold row rather than on a shared
    one."""
    mutants = e4.load_mutants(*mutant_tree)
    table, paired = e4.build_pairing(mutants)
    empty = [entry for entry in table if entry["witnessCount"] == 0][0]
    assert empty["paired"] is True
    assert empty["degenerate"] is True
    assert empty["countedInPairedSubset"] is False
    assert "m-a-003" not in paired["jps"]


def test_unpairable_adequate_mutants_are_published(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    assert e4.unpairable(mutants, paired) == {"jps": ["m-a-002"],
                                              "rego": ["m-b-002"]}


def test_the_engine_supplied_list_refuses_when_no_manifest_member_exists(
        mutant_tree):
    """SCAFFOLD item S9's remaining guard. An EMPTY registered class and a
    MISSING member are different facts: returning an empty list from a manifest
    that says nothing would publish "0 engine-supplied kills" and satisfy
    section 4 in form only."""
    mutants = e4.load_mutants(*mutant_tree)
    with pytest.raises(e4.E4Error) as raised:
        e4.engine_supplied_ids(mutants, "jps")
    assert str(raised.value).startswith("E4-ENGINE-SUPPLIED-UNREGISTERED")


def _remark_jps(mutant_tree, markings):
    """Rewrite the JPS manifest's `engineSuppliedKill` members and reload."""
    jps_manifest, rego_manifest, jps_dir, rego_dir = mutant_tree
    records = json.loads(open(jps_manifest).read())
    for record, marking in zip([r for r in records if r["validates"]], markings):
        if marking is not _ABSENT:
            record["engineSuppliedKill"] = marking
    open(jps_manifest, "w").write(json.dumps(records))
    return e4.load_mutants(jps_manifest, rego_manifest, jps_dir, rego_dir)


_ABSENT = object()


def test_the_engine_supplied_list_is_read_when_every_record_is_marked(
        mutant_tree):
    """A COMPLETE Boolean census is what section 4's class is computed from."""
    mutants = _remark_jps(mutant_tree, [True, False, False])
    assert e4.engine_supplied_ids(mutants, "jps") == ["m-a-001"]


@pytest.mark.parametrize("markings,why", [
    ([True, _ABSENT, False],
     "one true and one MISSING — the reviewer's R2-10 construction"),
    ([True, False, _ABSENT], "the last record is silent"),
    ([True, None, False], "a null is not a Boolean"),
    ([True, "false", False],
     "the STRING 'false' is truthy and used to be COUNTED IN"),
    ([True, 0, False], "a numeric marking is not a Boolean"),
    ([1, 0, 0], "1/0 are not Booleans"),
])
def test_a_partial_or_mistyped_engine_supplied_census_refuses(mutant_tree,
                                                              markings, why):
    """ROUND-2 R2-10, and the old refusal fired only when EVERY record was
    unmarked — so a manifest marking one mutant and leaving the next silent was
    accepted and published a class computed from a partial census, which is the
    "0 from an absence" the refusal exists to prevent, one record at a time. And
    the marking was read for truthiness, so the string `"false"` counted a mutant
    INTO the class."""
    mutants = _remark_jps(mutant_tree, markings)
    with pytest.raises(e4.E4Error) as raised:
        e4.engine_supplied_ids(mutants, "jps")
    assert str(raised.value).startswith("E4-ENGINE-SUPPLIED-INCOMPLETE"), why


def test_an_all_false_marking_is_an_empty_registered_class_and_not_a_refusal(
        mutant_tree, tmp_path):
    """Arm B's case, and the reason the distinction is load-bearing: the Rego
    ladder has no structural conflict detection, so its engine-supplied class is
    EMPTY. A manifest that records `engineSuppliedKill: false` on every mutant
    has stated that; one with no member has stated nothing."""
    jps_manifest, rego_manifest, jps_dir, rego_dir = mutant_tree
    document = json.loads(open(rego_manifest).read())
    for mutant in document["mutants"]:
        mutant["engineSuppliedKill"] = False
    open(rego_manifest, "w").write(json.dumps(document))
    mutants = e4.load_mutants(jps_manifest, rego_manifest, jps_dir, rego_dir)
    assert e4.engine_supplied_ids(mutants, "rego") == []


def test_the_committed_mutant_manifests_carry_the_registered_member(
        study, requires_artifact):
    """SCAFFOLD item S9, closed, against the DESIGN manifests the freeze copies
    into `mutants/MANIFEST-*.json`: arm A's marking is
    `design/mutants/refA/REGISTRY.json`'s conflict-only list, cell for cell, and
    arm B carries the member with an empty class and its reason."""
    requires_artifact("design/mutants/refA/REGISTRY.json",
                      "design/mutants/refA/MANIFEST.json",
                      "design/mutants/refB/MANIFEST.json",
                      "design/mutants/adequacy_engine_supplied.json")
    design = os.path.join(study, "design", "mutants")
    registry = json.loads(open(os.path.join(design, "refA",
                                            "REGISTRY.json")).read())
    manifest = json.loads(open(os.path.join(design, "refA",
                                            "MANIFEST.json")).read())
    marked = sorted(m["id"] for m in manifest if m["engineSuppliedKill"])
    # ROUND-1 R1-11's consequence, and the binding MOVED with it. The marking
    # used to be `REGISTRY.json`'s `conflictOnlyMutants`, which is computed over
    # each mutant's GOLD WITNESSES; the round-1 dense census over the whole
    # registered domain is the authority now, and it is what the manifest
    # carries. `REGISTRY.json`'s list is the pre-census artifact and is not what
    # the scorer reads.
    census = json.loads(open(os.path.join(design,
                                          "adequacy_engine_supplied.json")).read())
    assert marked == sorted(census["engineSuppliedKillTrue"])
    assert isinstance(registry["conflictOnlyMutants"], list)
    assert all("engineSuppliedKill" in m for m in manifest)
    rego = json.loads(open(os.path.join(design, "refB",
                                        "MANIFEST.json")).read())
    assert all("engineSuppliedKill" in m for m in rego["mutants"])
    assert not any(m["engineSuppliedKill"] for m in rego["mutants"])
    # Arm B's class is EMPTY and the manifest SAYS so: the member is on every
    # mutant and the note gives the construction reason. An empty registered
    # class and a missing member are different facts, which is the whole of
    # what `engine_supplied_ids()` refuses on.
    assert "no structural conflict detection" in rego["engineSuppliedKillNote"]


# --- the run-level endpoint -------------------------------------------------

def test_kill_rates_carry_three_named_denominators(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": e4.KILLED, "m-a-002": e4.SURVIVED,
                           "m-a-003": e4.KILLED},
                          mutants["jps"], paired["jps"])
    assert rates["killedAdequate"] == 1 and rates["adequate"] == 2
    assert rates["killedPaired"] == 1 and rates["paired"] == 1
    assert rates["killedNotAdequate"] == 1 and rates["notAdequate"] == 1
    assert rates["survivorsPaired"] == []


def test_a_refused_mutant_is_scored_neither_way_and_stays_in_the_denominator(
        mutant_tree):
    """ROUND-1 R1-8's enforcing test at the rate layer. An engine refusal on a
    frozen mutant is not the suite distinguishing it (that would let a transient
    apparatus failure make a weak suite high-kill) and not a survivor either
    (nothing was asked). It stays in the denominator — so a refusal can never
    inflate a rate by shrinking it — and it is published by id."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": e4.REFUSED, "m-a-002": e4.SURVIVED,
                           "m-a-003": e4.SURVIVED},
                          mutants["jps"], paired["jps"])
    assert rates["killedPaired"] == 0
    assert rates["paired"] == 1                      # the denominator is intact
    assert rates["survivorsPaired"] == []            # and it is not a survivor
    assert rates["refusedPaired"] == ["m-a-001"]
    assert rates["refusedAll"] == ["m-a-001"]


def test_kill_rates_split_the_paired_subset_on_the_engine_supplied_list(
        mutant_tree):
    """Section 4: those kills are "reported both included and excluded". The
    split happens once, where the kill of each mutant is known — reconstructing
    it from an aggregate afterwards is not possible."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": e4.KILLED, "m-a-002": e4.SURVIVED,
                           "m-a-003": e4.KILLED},
                          mutants["jps"], paired["jps"],
                          engine_supplied=["m-a-001"])
    assert rates["killedPaired"] == 1 and rates["paired"] == 1
    assert rates["killedPairedExcludingEngineSupplied"] == 0
    assert rates["pairedExcludingEngineSupplied"] == 0
    assert rates["killedEngineSupplied"] == 1 and rates["engineSupplied"] == 1
    # …and with no list the two columns are the same numbers, so a language
    # with an empty registered class reports one honest column twice.
    plain = e4.kill_rates({"m-a-001": e4.KILLED}, mutants["jps"], paired["jps"])
    assert plain["killedPairedExcludingEngineSupplied"] == plain["killedPaired"]
    assert plain["pairedExcludingEngineSupplied"] == plain["paired"]


def test_the_high_kill_cut_is_stated_with_the_arithmetic_that_produced_it():
    cut = e4.high_kill_cut(39)
    assert cut["integerCut"] == 38
    assert cut["tau"] == "19/20"
    assert cut["cutReachable"] is True
    assert "38 of the 39" in cut["statement"]


def test_is_high_kill_reads_the_integer_cut():
    assert e4.is_high_kill(38, 39, 38) is True
    assert e4.is_high_kill(37, 39, 38) is False


# --- R1-1: one cut per language, from its own denominator -------------------

def test_the_cut_is_derived_per_language_at_the_real_current_counts(
        requires_artifact):
    """ROUND-1 R1-1's enforcing test, on the counts the repaired corpus actually
    has — READ FROM THE COMMITTED MANIFESTS rather than written down here.

    ROUND-3 R3-2 is why they are read: the counts were 75 JPS / 65 Rego when
    this test was written and are 69 / 62 after the adequacy repair, and a
    literal pair here would have made the repair fail an arithmetic test that
    has nothing to do with it. What R1-1 is about is that there are TWO cuts,
    each from its own denominator, and that the other language's cut is
    unreachable — properties of the rule, not of the numbers.

    The blocker was that ONE cut was derived from the JPS count and handed to
    every arm while each arm's kill denominator stayed language-specific: the
    single-cut scorer would have judged a Rego suite against the JPS cut, out of
    a smaller possible total, so a PERFECT B/C suite could never be high-kill
    and the primary endpoint was impossible for two of the three arms."""
    requires_artifact("design/mutants/refA/MANIFEST.json",
                      "design/mutants/refB/MANIFEST.json")
    design = os.path.join(_STUDY, "design", "mutants")
    mutants = e4.load_mutants(os.path.join(design, "refA", "MANIFEST.json"),
                              os.path.join(design, "refB", "MANIFEST.json"),
                              os.path.join(design, "refA"),
                              os.path.join(design, "refB"))
    _pairing, paired = e4.build_pairing(mutants)
    n_jps, n_rego = len(paired["jps"]), len(paired["rego"])
    assert n_jps > n_rego > 0, (n_jps, n_rego)
    cuts = e4.high_kill_cuts(paired)
    ceil95 = lambda n: -(-19 * n // 20)
    assert cuts["jps"]["pairedAdequateMutants"] == n_jps
    assert cuts["jps"]["integerCut"] == ceil95(n_jps)
    assert cuts["rego"]["pairedAdequateMutants"] == n_rego
    assert cuts["rego"]["integerCut"] == ceil95(n_rego)
    assert cuts["jps"]["integerCut"] != cuts["rego"]["integerCut"]
    assert cuts["jps"]["language"] == "jps"
    assert cuts["rego"]["language"] == "rego"
    # Each cut is reachable by a perfect suite of its OWN language...
    assert e4.is_high_kill(n_rego, n_rego, cuts["rego"]["integerCut"]) is True
    assert e4.is_high_kill(n_jps, n_jps, cuts["jps"]["integerCut"]) is True
    # ...and the JPS cut is not reachable at the Rego denominator at all, which
    # is the defect stated as an assertion rather than as a comment.
    with pytest.raises(e4.E4Error) as raised:
        e4.is_high_kill(n_rego, n_rego, cuts["jps"]["integerCut"])
    assert str(raised.value).startswith("E4-CUT-UNREACHABLE")


def test_a_cut_above_its_own_denominator_refuses_at_derivation(monkeypatch):
    """The assertion the reviewer asked for, at the place the cut is made: no
    cut is published that its run's denominator cannot reach."""
    from fractions import Fraction
    from e4lib import stats
    monkeypatch.setattr(stats, "TAU", Fraction(21, 20))
    with pytest.raises(e4.E4Error) as raised:
        e4.high_kill_cut(65)
    assert str(raised.value).startswith("E4-CUT-UNREACHABLE")


# --- R1-6: total matrixVersion-2 schema validation --------------------------

@pytest.mark.parametrize("payload,why", [
    ("[]", "the document is a list"),
    ('{"matrixVersion": "2", "cases": [null]}', "a case is null"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": "LOW"}}]}',
     "facts.vendor is a string"),
    ('{"cases": []}', "matrixVersion is absent"),
    ('{"matrixVersion": 1, "cases": []}', "matrixVersion is not 2"),
    ('{"matrixVersion": 2, "cases": []}',
     "the JSON NUMBER 2 is not the registered spelling (round-2 R2-6)"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": "unresolved", "reasons": 1}}]}',
     "reasons is a number and used to raise TypeError (round-2 R2-6)"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": "unresolved", "reasons": [1]}}]}',
     "reasons is a list of non-strings"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": "outcome", "outcomeId": 7}}]}',
     "outcomeId is a number"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": 2}}]}', "kind is a number"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": "outcome", "outcomeId": "a", '
     '"handoff": "none"}}]}', "handoff is a string"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedDisposition": {"kind": "outcome", "outcomeId": "a"}, '
     '"expectedErrorClass": "malformed-input"}]}',
     "both registered expectation forms in one case"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedErrorClass": 3}]}', "expectedErrorClass is a number"),
    ('{"matrixVersion": "2", "cases": [{"facts": {"vendor": {}}, '
     '"expectedHandoffTarget": "Front desk"}]}',
     "expectedHandoffTarget is a string"),
    ('{"matrixVersion": "2", "cases": {}}', "cases is not a list"),
    ('{"matrixVersion": "2", "cases": [{"evidenceAvailability": 3}]}',
     "evidenceAvailability is a number"),
    ('{"matrixVersion": "2", "cases": [{"expectedDisposition": []}]}',
     "expectedDisposition is a list"),
    ("not json at all", "the block is not JSON"),
])
def test_every_author_controlled_shape_failure_is_a_matrix_error(tmp_path,
                                                                 payload, why):
    """ROUND-1 R1-6's enforcing test, on the reviewer's own three payloads and
    six more.

    Each of these used to raise `AttributeError`/`TypeError` out of
    `load_matrix()`, past a caller that caught only `ValueError`, into the outer
    handler that publishes pipeline-invalid and re-raises — so ONE author's
    malformed matrix invalidated the entire primary attempt. §1a registers the
    opposite: unparseable or schema-invalid author output stays in the
    denominator as a counted authoring outcome."""
    path = tmp_path / "matrix.json"
    path.write_text(payload)
    with pytest.raises(e4.MatrixError) as raised:
        e4.load_matrix(str(path))
    assert str(raised.value).startswith("E4-MATRIX-SCHEMA"), why
    assert isinstance(raised.value, e4.E4Error)


def test_a_matrix_error_is_not_the_outer_exception_path(tmp_path):
    """The distinction the finding turns on: `MatrixError` is about the AUTHOR
    and every other exception out of this module is about the apparatus."""
    path = tmp_path / "matrix.json"
    path.write_text("[]")
    try:
        e4.load_matrix(str(path))
    except e4.MatrixError:
        pass
    except Exception:                                    # pragma: no cover
        raise AssertionError("an author-controlled shape raised something else")


def test_load_matrix_marks_unreadable_cases_rather_than_dropping_them(tmp_path):
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps({"matrixVersion": "2", "cases": [
        {"id": "ok", "facts": {"vendor": {"riskScore": "10"}},
         "expectedDisposition": {"kind": "outcome", "outcomeId": "approve"}},
        {"id": "no-facts",
         "expectedDisposition": {"kind": "outcome", "outcomeId": "approve"}},
        {"facts": {"vendor": {}}},
    ]}))
    cases, note = e4.load_matrix(str(path))
    assert note == {"matrixVersion": "2", "caseCount": 3}
    assert [case[0] for case in cases] == ["ok", "no-facts", "case[2]"]
    assert [case[4] for case in cases] == [True, False, False]


def test_case_signature_reads_the_naming_appendix_members(tmp_path):
    sig = e4.case_signature(
        {"vendor": {"riskScore": "55", "requestedSpend": "1.00",
                    "countryRisk": "LOW", "newVendor": "yes"}},
        {"financial-evidence": "present"})
    assert sig["risk"] == "55" and sig["spend"] == "1.00"
    assert sig["country"] == "LOW" and sig["newVendor"] == "yes"
    assert sig["finEvidence"] == "present" and sig["insurance"] is None


def test_identity_and_kill_agree_about_unreadable_cases(monkeypatch):
    """An unreadable case FAILS identity (it is what the author emitted) and
    can KILL nothing — the two rules are different and both are registered."""
    from e4lib import engines
    monkeypatch.setattr(engines, "eval_pack",
                        lambda *a, **k: ("outcome", "approve", ()))
    cases = [("bad", {}, {}, None, False, {}),
             ("good", {}, {}, ("outcome", "approve", ()), True, {})]
    ok, failures = e4.identity_arm_a(None, "ref", cases, "/tmp")
    assert ok is False and [entry["case"] for entry in failures] == ["bad"]
    outcome, detail = e4.kill_arm_a(None, "mutant", cases, "/tmp")
    assert outcome == e4.SURVIVED and detail == {}


def test_a_reference_that_refuses_is_an_apparatus_refusal_not_a_zero(monkeypatch):
    """ROUND-1 R1-8, the reference side. An engine refusal on the FROZEN
    reference used to fail the identity control, which scores a correct suite
    zero for an apparatus failure."""
    from e4lib import engines
    monkeypatch.setattr(engines, "eval_pack",
                        lambda *a, **k: ("ROW-ERROR", "engine-timeout", ()))
    cases = [("c1", {}, {}, ("outcome", "approve", ()), True, {})]
    with pytest.raises(e4.ExecutionRefusal) as raised:
        e4.identity_arm_a(None, "ref", cases, "/tmp")
    assert str(raised.value).startswith("E4-IDENTITY-ENGINE-REFUSED")


def test_a_mutant_that_refuses_is_not_a_kill(monkeypatch):
    """ROUND-1 R1-8, the mutant side. "A refusal on a mutant counts as
    disagreement" is what let a transient apparatus failure make a weak suite
    high-kill."""
    from e4lib import engines
    monkeypatch.setattr(engines, "eval_pack",
                        lambda *a, **k: ("ROW-ERROR", "non-json-payload", ()))
    cases = [("c1", {}, {}, ("outcome", "approve", ()), True, {})]
    outcome, detail = e4.kill_arm_a(None, "mutant", cases, "/tmp")
    assert outcome == e4.REFUSED
    assert detail["got"] == "ROW-ERROR:non-json-payload"


def test_kill_short_circuits_at_the_first_disagreement(monkeypatch):
    from e4lib import engines
    seen = []

    def evaluate(_tools, _path, facts, _evidence, _workdir):
        seen.append(facts["id"])
        return ("outcome", "reject", ())
    monkeypatch.setattr(engines, "eval_pack", evaluate)
    cases = [("c1", {"id": "c1"}, {}, ("outcome", "approve", ()), True, {}),
             ("c2", {"id": "c2"}, {}, ("outcome", "approve", ()), True, {})]
    outcome, detail = e4.kill_arm_a(None, "mutant", cases, "/tmp")
    assert outcome == e4.KILLED and detail["case"] == "c1"
    assert seen == ["c1"]


def _test_record(status, code=0):
    return {"status": status, "exitCode": code, "tests": 1,
            "failed": [], "errored": []}


def test_the_rego_identity_and_kill_read_the_result_document(monkeypatch):
    """ROUND-1 R1-8, arms B/C. The old rule was "nonzero kills", and at
    v1.19.0 a compile failure, a load failure and the harness's own timeout are
    all nonzero — so every one of them killed every mutant it touched, and every
    one of them failed identity for a correct suite."""
    from e4lib import engines
    monkeypatch.setattr(engines, "opa_test",
                        lambda *a, **k: _test_record(engines.TEST_PASS))
    assert e4.identity_arm_rego(None, "ref", "suite", "/tmp")[0] is True
    assert e4.kill_arm_rego(None, "mutant", "suite", "/tmp")[0] == e4.SURVIVED

    monkeypatch.setattr(engines, "opa_test",
                        lambda *a, **k: _test_record(engines.TEST_FAILED, 2))
    assert e4.identity_arm_rego(None, "ref", "suite", "/tmp")[0] is False
    outcome, record = e4.kill_arm_rego(None, "mutant", "suite", "/tmp")
    assert outcome == e4.KILLED and record["exitCode"] == 2


def test_every_non_assertion_outcome_is_a_refusal_in_both_roles(monkeypatch):
    from e4lib import engines
    for status in (engines.TEST_ERRORED, engines.TEST_INVOCATION_REFUSED,
                   engines.TEST_TIMEOUT, engines.TEST_UNREADABLE):
        monkeypatch.setattr(engines, "opa_test",
                            lambda *a, _s=status, **k: _test_record(_s, 1))
        # Against the reference: an identity control that cannot be decided.
        with pytest.raises(e4.ExecutionRefusal) as raised:
            e4.identity_arm_rego(None, "ref", "suite", "/tmp")
        assert str(raised.value).startswith("E4-IDENTITY-ENGINE-REFUSED")
        # Against a mutant: neither killed nor survived.
        assert e4.kill_arm_rego(None, "m", "suite", "/tmp")[0] == e4.REFUSED


# ==========================================================================
# §7's DELTA 1 — the survivor-vector schema, and the token collision it fixes
# ==========================================================================
#
# Study 019's scorer had three outcome tokens (killed, survived, refused) and a
# fourth STATE it had no token for: a mutant never evaluated at all, because the
# run failed the identity control before the kill loop ran. `kill_rates({}, …)`
# then produced `killedPaired: 0` with `survivorsPaired: []`, which is
# BYTE-IDENTICAL to the record of a suite that killed every paired mutant. Two
# arm-A runs of 019 (`run-025`, `run-046`) scored a perfect 33/33 having killed
# nothing, and the collision moves the group-level ITT A−C contrast from
# +0.19112 to +0.13849 — magnitude 0.0526, a 38 % shift, and it LOWERS A−C.
#
# §5.2 registers the repair as a day-one requirement and §7's delta 1 states it:
# "the scorer emits an explicit per-mutant survivor vector for every admitted
# run and never encodes 'nothing evaluated' and 'everything killed' with the
# same token; `survivorsPaired: []` with `killedPaired: 0` is refused at write
# time rather than read as 33/33. A harness test drives both refusals, and the
# mutation check is required: break the refusal, confirm the test fails."


def _mutants(count=3):
    return [{"id": "m%d" % index, "notAdequate": False}
            for index in range(1, count + 1)]


def _paired(count=3):
    return {"m%d" % index for index in range(1, count + 1)}


class TheEmptySurvivorTrap:
    """Namespaced by a plain class so the collision's cases read together."""


def test_nothing_evaluated_and_everything_killed_are_two_documents():
    """THE regression, stated as the two records the collision made one.

    The assertion is not that either block is 'right' — it is that a reader
    cannot mistake one for the other, which is the property Study 019's schema
    did not have."""
    nothing = e4.unevaluated_kill_block(_mutants(), _paired(), (),
                                        "the identity control was not decided")
    everything = e4.kill_rates({name: e4.KILLED for name in _paired()},
                               _mutants(), _paired(), (), evaluated=True)
    assert nothing != everything
    # Both have an EMPTY survivor list, which is exactly why the list alone
    # cannot be the schema.
    assert nothing["survivorsPaired"] == everything["survivorsPaired"] == []
    # …and every member that distinguishes them.
    assert nothing["killedPaired"] == 0 and everything["killedPaired"] == 3
    assert nothing["killsEvaluated"] is False
    assert everything["killsEvaluated"] is True
    assert nothing["evaluatedPaired"] == 0 and everything["evaluatedPaired"] == 3
    assert sorted(nothing["notEvaluatedPaired"]) == ["m1", "m2", "m3"]
    assert everything["notEvaluatedPaired"] == []
    assert [token for _identifier, token in nothing["survivorVector"]] == \
        [e4.NOT_EVALUATED] * 3
    assert [token for _identifier, token in everything["survivorVector"]] == \
        [e4.KILLED] * 3


def test_a_survivor_vector_is_emitted_for_every_admitted_run():
    """§7's delta 1's first clause. Every paired-adequate mutant carries its own
    token, in the manifest's order, whatever the run's identity outcome."""
    for block in (e4.unevaluated_kill_block(_mutants(), _paired()),
                  e4.kill_rates({"m1": e4.KILLED, "m2": e4.SURVIVED,
                                 "m3": e4.REFUSED}, _mutants(), _paired())):
        assert [name for name, _token in block["survivorVector"]] == \
            ["m1", "m2", "m3"]
        for member in e4.KILL_BLOCK_REQUIRED:
            assert member in block, member
        e4.validate_kill_block(block)


def test_the_ambiguous_shape_is_refused_at_write_time():
    """The registered refusal, driven at the exact document §5.2 names: no
    survivors, no kills, nothing recorded as not-evaluated, over a non-empty
    paired denominator."""
    block = e4.kill_rates({}, _mutants(), _paired(), (), evaluated=True)
    block["notEvaluatedPaired"] = []
    block["evaluatedPaired"] = 3
    block["survivorVector"] = [[name, e4.SURVIVED] for name in ("m1", "m2", "m3")]
    block["survivorsPaired"] = []
    with pytest.raises(e4.E4Error) as caught:
        e4.validate_kill_block(block)
    assert "E4-KILL-VECTOR-DISAGREES" in str(caught.value)
    # …and the shape with nothing at all in it.
    bare = dict(block, survivorVector=[], evaluatedPaired=0,
                notEvaluatedPaired=[], killsEvaluated=False)
    with pytest.raises(e4.E4Error) as caught:
        e4.validate_kill_block(bare)
    assert "E4-KILL-VECTOR-SHORT" in str(caught.value)


def test_the_019_shape_is_refused_by_name():
    """The literal block Study 019's scorer wrote at two of its five sites —
    `{"killedPaired": 0, "paired": n}`, with no survivor member and no
    `caseCount` — which is §5.2's definition-4 defect and this one at once."""
    with pytest.raises(e4.E4Error) as caught:
        e4.validate_kill_block({"killedPaired": 0, "paired": 3})
    assert "E4-KILL-BLOCK-INCOMPLETE" in str(caught.value)


def test_the_naive_coverage_reading_can_no_longer_score_a_perfect_run():
    """The consequence, in the reader's terms. A coverage set computed as "the
    classes with no survivor" scores the not-evaluated block 3/3 — which is what
    happened on 019 — and the same computation over `survivorVector` scores it
    0/3, because a not-evaluated mutant is neither killed nor survived."""
    nothing = e4.unevaluated_kill_block(_mutants(), _paired())
    naive = len(_paired()) - len(nothing["survivorsPaired"])
    assert naive == 3, "the naive reading is what §5.2 says it is"
    corrected = sum(1 for _name, token in nothing["survivorVector"]
                    if token == e4.KILLED)
    assert corrected == 0


def test_every_disagreement_between_the_counts_and_the_vector_refuses():
    """Four refusals, one case each, so a validator that had lost one of them
    fails here rather than passing a block nobody can read."""
    good = e4.kill_rates({"m1": e4.KILLED, "m2": e4.SURVIVED,
                          "m3": e4.REFUSED}, _mutants(), _paired())
    for mutate, expected in (
            (lambda b: b.update(killedPaired=2), "E4-KILL-VECTOR-DISAGREES"),
            (lambda b: b.update(survivorsPaired=[]), "E4-KILL-VECTOR-DISAGREES"),
            (lambda b: b.update(evaluatedPaired=1), "E4-KILL-CENSUS"),
            (lambda b: b.update(killsEvaluated=False),
             "E4-KILL-EVALUATED-CONTRADICTION"),
            (lambda b: b.update(
                survivorVector=[["m1", "invented"], ["m2", e4.SURVIVED],
                                ["m3", e4.REFUSED]]),
             "E4-KILL-VECTOR-TOKEN")):
        block = json.loads(json.dumps(good))
        mutate(block)
        with pytest.raises(e4.E4Error) as caught:
            e4.validate_kill_block(block)
        assert expected in str(caught.value), expected


def test_breaking_the_refusal_makes_the_regression_fail():
    """§7's delta 1 requires the mutation check by name: break the refusal,
    confirm the test fails.

    The mutation is the refusal's own condition — the branch that names the
    collision — removed. Under it the ambiguous document validates, and the case
    above stops discriminating."""
    block = e4.kill_rates({}, _mutants(), _paired(), (), evaluated=False)
    block["notEvaluatedPaired"] = []
    block["evaluatedPaired"] = 0
    block["survivorVector"] = []
    block["paired"] = 3
    original = e4.validate_kill_block

    def mutated(candidate, where="a kill block"):
        """`validate_kill_block()` with the ambiguity branch removed."""
        if (candidate["paired"] and not candidate["survivorsPaired"]
                and not candidate["killedPaired"]
                and not candidate["notEvaluatedPaired"]):
            return candidate
        return original(candidate, where)

    # The control first: the real validator refuses this document.
    with pytest.raises(e4.E4Error):
        original(block)
    # …and the mutant accepts it, which is what makes the case above a test.
    assert mutated(block) is block


# ==========================================================================
# §7's DELTA 4 — TWO identity relations, and only one of them gates
# ==========================================================================


def test_the_two_relations_are_named_separately():
    """M-13, §1.2: "`referenceIdentity` and `ownPolicyIdentity` are two named
    relations in the scorer, never one field with two meanings." The names are
    constants, and which one GATES is a constant too — so "the gate is the
    reference relation" is something a test can read rather than a sentence a
    reader has to trust."""
    assert e4.IDENTITY_RELATIONS == ("referenceIdentity", "ownPolicyIdentity")
    assert e4.GATING_IDENTITY_RELATION == "referenceIdentity"
    assert e4.OWN_POLICY_RELATION not in (e4.GATING_IDENTITY_RELATION,)


def test_the_own_policy_record_says_it_gates_nothing():
    record = e4.own_policy_identity_arm_a(None, None, [], "/tmp")
    assert record["relation"] == "ownPolicyIdentity"
    assert record["gates"] is False
    assert record["evaluated"] is False and record["pass"] is None
    assert "no admitted artifact" in record["note"]


def test_no_decision_path_reads_the_own_policy_relation():
    """The registered NON-GATING property, as a property of the SOURCE rather
    than as a sentence. §1.2: the score "gates nothing"; §5.1: it "conditions
    R1's construct statement" and adjudicates nothing.

    Read out of the modules that decide: the ordered decision table, the control
    gates and the contrast. A future edit that made a verdict read E6 would fail
    here, which a prose ceiling would not."""
    import ast
    import score
    from e4lib import decision
    for module in (decision, score):
        with open(module.__file__, "rb") as handle:
            tree = ast.parse(handle.read().decode("utf-8"))
        reads = [node for node in ast.walk(tree)
                 if isinstance(node, ast.Constant)
                 and node.value == "ownPolicyIdentity"]
        if module is decision:
            assert reads == [], (
                "the ordered decision rule must not name E6 at all")
    # In the scorer the name appears only where E6 is BUILT and PUBLISHED, never
    # inside the decision, the gates or the contrast.
    with open(score.__file__, "rb") as handle:
        source = handle.read().decode("utf-8")
    tree = ast.parse(source)
    owners = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Constant) and \
                    inner.value == "ownPolicyIdentity":
                owners.add(node.name)
    # The four sites are all CONSTRUCTION or PUBLICATION: the per-run record's
    # default and its two arms (`score_run`, `_identity_and_kill`), the block
    # that builds the per-arm aggregate (`own_policy_identity_block`) and the
    # E4 endpoint that publishes that block beside the relation which does gate
    # (`e4_endpoint`). None of them is a verdict, a gate or a contrast.
    assert owners <= {"own_policy_identity_block", "score_run",
                      "_identity_and_kill", "e4_endpoint"}, sorted(owners)
    for name in ("decide", "contrast", "control_gates", "registered_contrasts"):
        function = getattr(score, name, None) or getattr(decision, name, None)
        if function is None:
            continue
        import inspect
        assert "ownPolicyIdentity" not in inspect.getsource(function), name


def test_the_gate_is_the_reference_relation_and_the_scorer_reads_that_one():
    """The other half: the per-protocol population and every rate that reports
    an identity pass read `referenceIdentityPass`, and nothing reads a member
    called `identityPass` any more — a name with two meanings is what M-13
    registers against."""
    import score
    with open(score.__file__, "rb") as handle:
        source = handle.read().decode("utf-8")
    assert '"identityPass"' not in source
    assert '"referenceIdentityPass"' in source
