"""E4 — the X1 filter, the pairing rule, the identity control and the tau cut.

The X1 predicate gets its own block, because section 4 makes it an exclusion
class AND a registered inexpressibility result: a filter that is a condition
inside a loop is a filter nobody can check against the registration, and a
filter that disagrees with `design/gold/check_gold.py` means gold contains a row
the scorer would have excluded.
"""
import json

import pytest

from e4lib import e4


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


def test_partition_x1_applies_the_filter_once_for_identity_and_kill():
    inside = ("c1", {}, {}, ("outcome", "review", ()), True,
              signature(risk="55", country="LOW", spend=None))
    outside = ("c2", {}, {}, ("outcome", "approve", ()), True,
               signature(risk="10", country="LOW", spend="1.00"))
    scored, excluded = e4.partition_x1([inside, outside])
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


def test_the_engine_supplied_list_is_read_when_the_manifest_carries_it(
        mutant_tree, tmp_path):
    jps_manifest, rego_manifest, jps_dir, rego_dir = mutant_tree
    marked = json.loads(open(jps_manifest).read())
    marked[0]["engineSuppliedKill"] = True
    marked[1]["engineSuppliedKill"] = False
    open(jps_manifest, "w").write(json.dumps(marked))
    mutants = e4.load_mutants(jps_manifest, rego_manifest, jps_dir, rego_dir)
    assert e4.engine_supplied_ids(mutants, "jps") == ["m-a-001"]


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
    import os
    design = os.path.join(study, "design", "mutants")
    registry = json.loads(open(os.path.join(design, "refA",
                                            "REGISTRY.json")).read())
    manifest = json.loads(open(os.path.join(design, "refA",
                                            "MANIFEST.json")).read())
    marked = sorted(m["id"] for m in manifest if m["engineSuppliedKill"])
    assert marked == sorted(registry["conflictOnlyMutants"])
    assert len(marked) == 41          # section 4's "now 41"
    assert all("engineSuppliedKill" in m for m in manifest)
    rego = json.loads(open(os.path.join(design, "refB",
                                        "MANIFEST.json")).read())
    assert all("engineSuppliedKill" in m for m in rego["mutants"])
    assert not any(m["engineSuppliedKill"] for m in rego["mutants"])
    assert rego["engineSuppliedKillClass"]["registered"] is True
    assert rego["engineSuppliedKillClass"]["members"] == []
    assert "no structural conflict detection" in \
        rego["engineSuppliedKillClass"]["reason"]


# --- the run-level endpoint -------------------------------------------------

def test_kill_rates_carry_three_named_denominators(mutant_tree):
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": True, "m-a-002": False, "m-a-003": True},
                          mutants["jps"], paired["jps"])
    assert rates["killedAdequate"] == 1 and rates["adequate"] == 2
    assert rates["killedPaired"] == 1 and rates["paired"] == 1
    assert rates["killedNotAdequate"] == 1 and rates["notAdequate"] == 1
    assert rates["survivorsPaired"] == []


def test_kill_rates_split_the_paired_subset_on_the_engine_supplied_list(
        mutant_tree):
    """Section 4: those kills are "reported both included and excluded". The
    split happens once, where the kill of each mutant is known — reconstructing
    it from an aggregate afterwards is not possible."""
    mutants = e4.load_mutants(*mutant_tree)
    _table, paired = e4.build_pairing(mutants)
    rates = e4.kill_rates({"m-a-001": True, "m-a-002": False, "m-a-003": True},
                          mutants["jps"], paired["jps"],
                          engine_supplied=["m-a-001"])
    assert rates["killedPaired"] == 1 and rates["paired"] == 1
    assert rates["killedPairedExcludingEngineSupplied"] == 0
    assert rates["pairedExcludingEngineSupplied"] == 0
    assert rates["killedEngineSupplied"] == 1 and rates["engineSupplied"] == 1
    # …and with no list the two columns are the same numbers, so a language
    # with an empty registered class reports one honest column twice.
    plain = e4.kill_rates({"m-a-001": True}, mutants["jps"], paired["jps"])
    assert plain["killedPairedExcludingEngineSupplied"] == plain["killedPaired"]
    assert plain["pairedExcludingEngineSupplied"] == plain["paired"]


def test_the_high_kill_cut_is_stated_with_the_arithmetic_that_produced_it():
    cut = e4.high_kill_cut(39)
    assert cut["integerCut"] == 38
    assert cut["tau"] == "19/20"
    assert "38 of the 39" in cut["statement"]


def test_is_high_kill_reads_the_integer_cut():
    assert e4.is_high_kill(38, 39, 38) is True
    assert e4.is_high_kill(37, 39, 38) is False


def test_load_matrix_marks_unreadable_cases_rather_than_dropping_them(tmp_path):
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps({"matrixVersion": 2, "cases": [
        {"id": "ok", "facts": {"vendor": {"riskScore": "10"}},
         "expectedDisposition": {"kind": "outcome", "outcomeId": "approve"}},
        {"id": "no-facts",
         "expectedDisposition": {"kind": "outcome", "outcomeId": "approve"}},
        {"facts": {"vendor": {}}},
    ]}))
    cases, note = e4.load_matrix(str(path))
    assert note == {"matrixVersion": 2, "caseCount": 3}
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
    killed, case_id = e4.kill_arm_a(None, "mutant", cases, "/tmp")
    assert killed is False and case_id is None


def test_kill_short_circuits_at_the_first_disagreement(monkeypatch):
    from e4lib import engines
    seen = []

    def evaluate(_tools, _path, facts, _evidence, _workdir):
        seen.append(facts["id"])
        return ("outcome", "reject", ())
    monkeypatch.setattr(engines, "eval_pack", evaluate)
    cases = [("c1", {"id": "c1"}, {}, ("outcome", "approve", ()), True, {}),
             ("c2", {"id": "c2"}, {}, ("outcome", "approve", ()), True, {})]
    killed, case_id = e4.kill_arm_a(None, "mutant", cases, "/tmp")
    assert killed is True and case_id == "c1"
    assert seen == ["c1"]


def test_the_rego_identity_and_kill_read_the_exit_code(monkeypatch):
    from e4lib import engines
    monkeypatch.setattr(engines, "opa_test", lambda *a, **k: (0, "pass"))
    assert e4.identity_arm_rego(None, "ref", "suite", "/tmp")[0] is True
    assert e4.kill_arm_rego(None, "mutant", "suite", "/tmp")[0] is False
    monkeypatch.setattr(engines, "opa_test", lambda *a, **k: (1, "test-failure"))
    assert e4.identity_arm_rego(None, "ref", "suite", "/tmp")[0] is False
    killed, detail = e4.kill_arm_rego(None, "mutant", "suite", "/tmp")
    assert killed is True and detail["class"] == "test-failure"
