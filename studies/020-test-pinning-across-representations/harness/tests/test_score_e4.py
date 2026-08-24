"""E4 — the X1 filter, the pairing rule, the two identity relations, the
survivor vector, the per-language denominators and the coverage rule.

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


def test_the_committed_mutant_manifests_carry_the_registered_member(study):
    """SCAFFOLD item S9, closed, against the DESIGN manifests the freeze copies
    into `mutants/MANIFEST-*.json`: arm A's marking is
    `design/mutants/refA/REGISTRY.json`'s conflict-only list, cell for cell, and
    arm B carries the member with an empty class and its reason."""
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


# --- §7 delta 1: the survivor vector, and the token collision ---------------

def test_the_survivor_vector_is_total_over_the_paired_denominator(mutant_tree):
    """§5.1: "The scorer emits an explicit per-mutant survivor vector for every
    admitted run". Total means one entry per paired-adequate mutant, in manifest
    order, each carrying that mutant's own outcome — so the record says what
    happened to every mutant rather than listing the ones that survived."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": e4.KILLED}, mutants["jps"], paired["jps"])
    assert [entry["id"] for entry in rates["survivorVector"]] == ["m-a-001"]
    assert rates["survivorVector"][0]["outcome"] == e4.KILLED
    assert len(rates["survivorVector"]) == rates["paired"]
    assert rates["evaluatedPaired"] == 1


def test_nothing_evaluated_and_everything_killed_are_different_bytes(
        mutant_tree):
    """§5.2's Fact 1, as an assertion rather than as a warning.

    Two arm-A runs of 019 (`run-025`, `run-046`, both identity-failing) carried
    `survivorsPaired: []` with `killedPaired: 0`. Read naively — "no survivors,
    therefore everything killed" — they score a perfect 33/33 having killed
    nothing, and correcting that single collision moved 019's group-level ITT
    A−C contrast from +0.19112 to +0.13849.

    The two states are told apart HERE, in the bytes: the vector's outcomes are
    `not-evaluated` in one and `killed` in the other, and `evaluatedPaired`
    names the difference in one integer."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    nothing = e4.kill_rates({}, mutants["jps"], paired["jps"])
    everything = e4.kill_rates({"m-a-001": e4.KILLED}, mutants["jps"],
                               paired["jps"])
    # 019's two published members are IDENTICAL between the two states…
    assert nothing["survivorsPaired"] == everything["survivorsPaired"] == []
    assert nothing["killedPaired"] == 0
    # …and the vector is not.
    assert nothing["survivorVector"][0]["outcome"] == e4.NOT_EVALUATED
    assert everything["survivorVector"][0]["outcome"] == e4.KILLED
    assert nothing["evaluatedPaired"] == 0
    assert everything["evaluatedPaired"] == 1


def test_the_empty_survivor_record_is_refused_at_write_time(mutant_tree):
    """§7 delta 1: "`survivorsPaired: []` with `killedPaired: 0` is refused at
    write time rather than read as 33/33". The refusal is at the WRITE, not at
    the read, because a reader who has to know about the trap is a reader who
    can forget about it."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    run = {"run": "run-001", "admitted": True, "suitePresent": True,
           "caseCount": 4,
           "kill": e4.kill_rates({}, mutants["jps"], paired["jps"])}
    with pytest.raises(e4.SurvivorSchemaError) as raised:
        e4.require_survivor_schema(run)
    assert str(raised.value).startswith("E4-SURVIVOR-EMPTY")
    assert "0.0526" in str(raised.value)


def test_a_kill_block_without_the_vector_is_refused(mutant_tree):
    """The vector is the SCHEMA, not an annotation on it: a hand-built kill
    block — which is exactly how 019's no-suite and unparseable-suite paths
    wrote theirs — carries no vector and is refused rather than published."""
    run = {"run": "run-002", "admitted": True, "suitePresent": True,
           "caseCount": 0, "kill": {"killedPaired": 0, "paired": 62}}
    with pytest.raises(e4.SurvivorSchemaError) as raised:
        e4.require_survivor_schema(run)
    assert str(raised.value).startswith("E4-SURVIVOR-SCHEMA")


def test_an_admitted_run_with_a_suite_carries_casecount(mutant_tree):
    """§5.2's pinned definition 4 and §7 delta 1. 019's six runs that carried a
    kill block with neither `survivorsPaired` nor `caseCount` — B
    run-026/027/032/036 and C run-035/050, arm A zero — cannot recur, because
    the write refuses rather than the analysis imputing."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    kill = e4.kill_rates({"m-a-001": e4.KILLED}, mutants["jps"], paired["jps"])
    run = {"run": "run-003", "admitted": True, "suitePresent": True,
           "kill": kill}
    with pytest.raises(e4.SurvivorSchemaError) as raised:
        e4.require_survivor_schema(run)
    assert str(raised.value).startswith("E4-CASECOUNT-ABSENT")
    # 0 is a number and passes; an absence is what is refused.
    run["caseCount"] = 0
    assert e4.require_survivor_schema(run) is run


def test_a_run_with_no_suite_at_all_needs_no_casecount(mutant_tree):
    """The other side of the same rule: §5.2 pins `caseCount` = 0 for a suite
    that parses to no cases, and a run that emitted no suite is a different
    state. The schema tells them apart with `suitePresent` rather than writing
    0 for both, which would make the covariate a function of the missingness."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    kill = e4.kill_rates({"m-a-001": e4.KILLED}, mutants["jps"], paired["jps"])
    run = {"run": "run-004", "admitted": True, "suitePresent": False,
           "kill": kill}
    assert e4.require_survivor_schema(run) is run


# --- §7 delta 2: the per-language machinery, WITHOUT a threshold ------------

def test_no_threshold_survives_anywhere_in_the_e4_module():
    """§7 delta 2, and §5.1's "**No cut, no τ, no dichotomy**", asserted by
    ABSENCE and by name.

    019's `is_high_kill()`, `high_kill_cut()` and `high_kill_cuts()` are gone.
    They are not kept and disabled: a predicate left in the module is a
    predicate a later edit can call, and the delta's whole content is that
    there is no threshold for a registered decision path to read."""
    for name in ("is_high_kill", "high_kill_cut", "high_kill_cuts", "TAU"):
        assert not hasattr(e4, name), name
    code = "\n".join(line for line in open(e4.__file__, encoding="utf-8")
                     if not line.lstrip().startswith("#"))
    for token in ("is_high_kill", "high_kill_cut", "tau_cut", "integerCut"):
        assert token not in code, token


def test_no_registered_decision_path_reads_a_cut():
    """§7 delta 2's own sentence: "A harness test asserts **no registered
    decision path reads a cut**."

    The decision path is not a file, it is a REACHABILITY: §5.9's rows, the
    predicates they are made of, and the publisher's route into them. This
    walks the table's own rows — so a row added later is covered without this
    test being edited — and reads the source of every predicate and of the two
    functions that drive them, then the publisher's family entry point."""
    import inspect
    from e4lib import decision
    import score

    sources = [inspect.getsource(row.predicate) for row in decision.ROWS]
    sources += [inspect.getsource(decision.decide),
                inspect.getsource(decision.gate_causes),
                inspect.getsource(decision.direction),
                inspect.getsource(score.registered_family),
                inspect.getsource(score.e4_endpoint)]
    for token in ("cut", "tau", "highKill", "high_kill", "threshold"):
        for source in sources:
            code = "\n".join(line for line in source.split("\n")
                             if not line.lstrip().startswith("#"))
            # Docstrings are prose about the registration and may NAME the
            # thing that was removed; what may not appear is a read of one.
            code = code.replace('"""', "\x00").split("\x00")
            executable = "".join(code[::2])
            assert token not in executable, (token, source[:80])


def test_the_two_denominators_stay_separate_at_the_real_current_counts():
    """019's round-1 R1-1, kept as the property it actually was.

    R1-1 was not "a threshold existed". It was that ONE number derived from the
    JPS subset was applied to a Rego run whose subset was smaller, so a PERFECT
    B/C suite could not reach it and the primary endpoint was impossible for two
    of the three arms. 020 keeps the two denominators separate and publishes
    both, and removes the single number entirely — so the shape of R1-1 has
    nowhere to recur.

    The counts are READ FROM THE COMMITTED MANIFESTS rather than written here
    (019's round-3 R3-2: they were 75/65 before the adequacy repair and 69/62
    after, and a literal pair would have made the repair fail an arithmetic test
    that has nothing to do with it)."""
    design = os.path.join(_STUDY, "design", "mutants")
    mutants = e4.load_mutants(os.path.join(design, "refA", "MANIFEST.json"),
                              os.path.join(design, "refB", "MANIFEST.json"),
                              os.path.join(design, "refA"),
                              os.path.join(design, "refB"))
    _pairing, paired = e4.build_pairing(mutants)
    n_jps, n_rego = len(paired["jps"]), len(paired["rego"])
    assert n_jps > n_rego > 0, (n_jps, n_rego)
    block = e4.paired_denominators(paired)
    assert block["jps"]["pairedAdequateMutants"] == n_jps
    assert block["rego"]["pairedAdequateMutants"] == n_rego
    assert block["jps"]["language"] == "jps"
    assert block["rego"]["language"] == "rego"
    # Each language's lattice is its OWN 1/n and never the other's.
    assert block["jps"]["lattice"] == 1 / n_jps
    assert block["rego"]["lattice"] == 1 / n_rego
    assert block["jps"]["lattice"] != block["rego"]["lattice"]
    # No member of either block is a threshold, by name or by shape.
    for language in ("jps", "rego"):
        assert set(block[language]) == {"language", "pairedAdequateMutants",
                                        "lattice", "statement"}


def test_an_empty_denominator_reports_no_lattice_rather_than_dividing():
    assert e4.paired_denominators({"jps": set()})["jps"]["lattice"] is None


def test_the_shared_classes_publish_the_membership_imbalance(mutant_tree):
    """§5.2's Fact 2 and §5.8's mandatory publication: unequal per-class member
    counts are what make the native mutant level structurally biased BETWEEN
    languages, so the imbalance is counted whether or not any member reads it.
    On 019's corpus it is 20 of 33 classes."""
    mutants = e4.load_mutants(*mutant_tree)
    table, _paired = e4.build_pairing(mutants)
    shared = e4.shared_classes(table)
    assert shared["count"] == 1                      # only g1|g2 pairs here
    assert shared["classes"][0]["jpsCount"] == 1
    assert shared["classes"][0]["regoCount"] == 1
    assert shared["classes"][0]["equalMembership"] is True
    assert shared["unequalCount"] == 0


# --- §5.2's coverage rule ---------------------------------------------------

def test_a_class_is_covered_only_when_all_its_members_are_killed(mutant_tree):
    """§5.2's pinned definition 1, in code: "A run covers class g iff its suite
    kills **all** of g's members in the run's own language."

    Both readings are computed and their agreement is published, because §5.2
    registers `gall == gany` as a STATED FACT with a condition (88 of 88
    checkable runs), and a fact registered as such has to stay checkable on
    020's own batch rather than being assumed forward."""
    mutants = e4.load_mutants(*mutant_tree)
    table, _paired = e4.build_pairing(mutants)
    classes = e4.shared_classes(table)["classes"]
    covered = e4.coverage_classes({"m-a-001": e4.KILLED}, classes, "jps")
    assert covered["coveredCount"] == 1
    assert covered["allEqualsAny"] is True
    survived = e4.coverage_classes({"m-a-001": e4.SURVIVED}, classes, "jps")
    assert survived["coveredCount"] == 0
    assert survived["unevaluatedClasses"] == []


def test_an_unevaluated_class_is_not_a_covered_one_and_says_so(mutant_tree):
    """The same distinction the survivor vector draws one level down: a class
    nothing was asked about is reported as unevaluated, not as uncovered — the
    two are different states and §5.2's Fact 1 is what collapsing them costs."""
    mutants = e4.load_mutants(*mutant_tree)
    table, _paired = e4.build_pairing(mutants)
    classes = e4.shared_classes(table)["classes"]
    block = e4.coverage_classes({}, classes, "jps")
    assert block["coveredCount"] == 0
    assert block["unevaluatedClasses"] == ["g1|g2"]


# --- §7 delta 4: ownPolicyIdentity is a SECOND NAMED RELATION ---------------

def test_the_two_identity_relations_are_named_and_distinct():
    """§7 delta 4: "`referenceIdentity` and `ownPolicyIdentity` are two named
    relations in the scorer, never one field with two meanings."

    Named here as constants and asserted distinct, so a scorer cannot write one
    under the other's name — which is the whole of the delta: 019 had one
    `identityPass` member and the population "runs whose suite is consistent
    with their own policy" was therefore invisible."""
    assert e4.REFERENCE_IDENTITY == "referenceIdentity"
    assert e4.OWN_POLICY_IDENTITY == "ownPolicyIdentity"
    assert e4.IDENTITY_RELATIONS == (e4.REFERENCE_IDENTITY,
                                     e4.OWN_POLICY_IDENTITY)
    assert len(set(e4.IDENTITY_RELATIONS)) == 2


def test_own_policy_identity_names_its_relation_and_gates_nothing():
    """§5.1: E6 is "Published per run and per arm; gates nothing; conditions
    R1's construct statement". The block says so in its own bytes, so a reader
    of a published record cannot mistake it for a control."""
    class _Tools(object):
        pass

    class _Engines(object):
        TEST_PASS = "pass"
        TEST_SUITE_STATUSES = ("pass", "failed")

        @staticmethod
        def opa_test(tools, policy, suite, workdir):
            return {"status": "pass", "exitCode": 0}

    import e4lib.e4 as module
    saved = module.engines
    module.engines = _Engines()
    try:
        block = module.own_policy_identity(_Tools(), "B", "policy.rego", None,
                                           "suite.rego", "/tmp")
    finally:
        module.engines = saved
    assert block["relation"] == e4.OWN_POLICY_IDENTITY
    assert block["pass"] is True
    assert "gates" in block and "nothing" in block["gates"]


def test_own_policy_identity_refuses_on_an_engine_refusal_rather_than_failing():
    """§6, as amended for 020: `engine-execution-clean` "now covers E6's extra
    invocation too". A pinned engine that could not run is an apparatus failure
    and adjudicates R1 in no direction — recording it as `pass: false` would
    put an apparatus fact into a published per-arm rate."""
    class _Engines(object):
        TEST_PASS = "pass"
        TEST_SUITE_STATUSES = ("pass", "failed")

        @staticmethod
        def opa_test(tools, policy, suite, workdir):
            return {"status": "compile-error", "exitCode": 1}

    import e4lib.e4 as module
    saved = module.engines
    module.engines = _Engines()
    try:
        with pytest.raises(e4.ExecutionRefusal) as raised:
            module.own_policy_identity(None, "C", "policy.rego", None,
                                       "suite.rego", "/tmp")
    finally:
        module.engines = saved
    assert str(raised.value).startswith("E6-OWN-POLICY-ENGINE-REFUSED")


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
