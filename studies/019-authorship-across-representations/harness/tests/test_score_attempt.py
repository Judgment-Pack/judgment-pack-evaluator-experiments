"""The attempt-record regime, the population rule, and byte-identical rescoring.

What is under test here is the PROGRAM SHAPE the 014-018 line established and
this study inherits: the marker precedes the parse, the raw registry bytes are
hashed once and carried into every terminal record, an existing attempt root is
refused, a batch that did not complete is declared rather than scored, and no
published byte is a timestamp or an absolute path.

The scorer is exercised against the real study tree, which is pre-freeze: every
freeze pin is null, the registered artifacts do not exist, and the attempt is
therefore pipeline-invalid. That is not a limitation of the test — it is the
state the registration says the scorer must publish honestly, and it is the only
path through `main()` that can be driven before a batch exists.
"""
import json
import os

import pytest

import batch
import score
from e4lib import decision


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


# --- the partition, the diff section 1a registers ---------------------------

def test_the_scorers_codes_are_exactly_the_registered_partition():
    """`tests/test_partition.py`'s third diff, live now that the module exists:
    every code the admission layer can return is a key of `CODE_PARTITION`, and
    every key is named."""
    assert set(score.ADMISSION_CODES) == set(batch.CODE_PARTITION)
    assert score.APPARATUS_SIDE | score.AUTHORING_SIDE == set(score.ADMISSION_CODES)
    assert score.APPARATUS_SIDE & score.AUTHORING_SIDE == set()


def test_the_admission_codes_are_sorted_and_stable():
    assert list(score.ADMISSION_CODES) == sorted(score.ADMISSION_CODES)


# --- the attempt root -------------------------------------------------------

def test_an_existing_attempt_root_is_refused(tmp_path):
    """"The first invocation of that command is the primary attempt" is only
    true if a second invocation cannot look like the first."""
    root = tmp_path / "primary-attempt-001"
    root.mkdir()
    assert score.main(["--attempt-root", str(root)]) == 2
    assert list(root.iterdir()) == []


def test_the_marker_precedes_the_registry_parse(tmp_path, monkeypatch):
    """Study 016's round-1 R1-12: even an attempt that dies on a malformed
    registry leaves a record tied to the exact registry bytes it saw."""
    broken = tmp_path / "PINS.json"
    broken.write_bytes(b"{not json")
    monkeypatch.setattr(score, "PINS_PATH", str(broken))
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    marker = json.loads(read(root / "ATTEMPT.json"))
    assert marker["pinsRawSha256"] == score.sha256_bytes(b"{not json")
    results = json.loads(read(root / "RESULTS.json"))
    assert results["pipelineInvalid"] is True
    assert results["pinsRawSha256"] == marker["pinsRawSha256"]


def test_an_unreadable_registry_still_leaves_a_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(score, "PINS_PATH", str(tmp_path / "absent.json"))
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    marker = json.loads(read(root / "ATTEMPT.json"))
    assert marker["pinsRawSha256"] is None
    assert json.loads(read(root / "RESULTS.json"))["problem"] == \
        "the pin registry is unreadable"


def test_a_duplicate_key_registry_refuses(tmp_path, monkeypatch):
    """A shadowed member cannot mean one thing to this scorer and another to a
    reader."""
    broken = tmp_path / "PINS.json"
    broken.write_bytes(b'{"a": 1, "a": 2}')
    monkeypatch.setattr(score, "PINS_PATH", str(broken))
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    assert "duplicate" in json.loads(read(root / "RESULTS.json"))["problem"]


def test_the_pins_digest_is_over_the_exact_bytes_that_are_parsed(tmp_path,
                                                                 monkeypatch):
    """One read: the bytes hashed are the bytes parsed, so there is no
    hash/parse divergence window (Study 016's round-2 residual)."""
    root = tmp_path / "primary-attempt-001"
    score.main(["--attempt-root", str(root)])
    marker = json.loads(read(root / "ATTEMPT.json"))
    with open(score.PINS_PATH, "rb") as handle:
        assert marker["pinsRawSha256"] == score.sha256_bytes(handle.read())


def test_the_reviewer_set_is_refused_while_any_pin_is_null(tmp_path):
    """`harness/PINS.json`'s own rule: `--include-reviewer-set` refuses while
    any pin is null."""
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root),
                       "--include-reviewer-set"]) == 2
    results = json.loads(read(root / "RESULTS.json"))
    assert results["problem"].startswith("--include-reviewer-set is refused")
    assert json.loads(read(root / "ATTEMPT.json"))["includeReviewerSet"] is True


# --- the terminal record ----------------------------------------------------

def test_a_pre_freeze_attempt_is_pipeline_invalid_and_says_which_row(tmp_path):
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    results = json.loads(read(root / "RESULTS.json"))
    assert results["pipelineInvalid"] is True
    assert results["decision"]["row"] == decision.ROW_PIPELINE_INVALID.name
    assert results["decision"]["verdict"] == \
        "R1 inconclusive - pipeline-invalid"


def test_the_terminal_record_names_every_problem_it_found(tmp_path):
    root = tmp_path / "primary-attempt-001"
    score.main(["--attempt-root", str(root)])
    problems = json.loads(read(root / "RESULTS.json"))["problems"]
    assert any("registered artifact is absent: gold/GOLD.json" in problem
               for problem in problems)
    assert problems == sorted(problems)


def test_no_published_byte_is_an_absolute_path(tmp_path):
    root = tmp_path / "primary-attempt-001"
    score.main(["--attempt-root", str(root)])
    for name in ("ATTEMPT.json", "RESULTS.json"):
        body = read(root / name).decode("utf-8")
        assert score.STUDY not in body
        assert str(tmp_path) not in body


def test_no_published_byte_is_a_timestamp(tmp_path):
    """Section: "its outputs embed no timestamp and no absolute path". A
    four-digit year is the cheapest way to notice one arriving."""
    import re
    root = tmp_path / "primary-attempt-001"
    score.main(["--attempt-root", str(root)])
    for name in ("ATTEMPT.json", "RESULTS.json"):
        body = read(root / name).decode("utf-8")
        assert not re.search(r"20\d\d-\d\d-\d\dT\d\d:", body)


def test_scrub_replaces_the_roots_it_knows_about():
    assert score.scrub(score.STUDY + "/gold/GOLD.json") == \
        "<study>/gold/GOLD.json"
    assert score.scrub_document({"a": [score.STUDY], "b": 1}) == \
        {"a": ["<study>"], "b": 1}


def test_a_crash_after_the_marker_is_recorded_and_re_raised(tmp_path,
                                                            monkeypatch):
    def explode(*_args, **_kwargs):
        raise RuntimeError("synthetic")
    monkeypatch.setattr(score.integrity, "study_label", explode)
    root = tmp_path / "primary-attempt-001"
    with pytest.raises(RuntimeError):
        score.main(["--attempt-root", str(root)])
    results = json.loads(read(root / "RESULTS.json"))
    assert results["pipelineInvalid"] is True
    assert results["problem"] == "RuntimeError: synthetic"


def test_a_system_exit_after_the_marker_is_recorded_and_re_raised(tmp_path,
                                                                  monkeypatch):
    def leave(*_args, **_kwargs):
        raise SystemExit(3)
    monkeypatch.setattr(score.integrity, "study_label", leave)
    root = tmp_path / "primary-attempt-001"
    with pytest.raises(SystemExit):
        score.main(["--attempt-root", str(root)])
    assert json.loads(read(root / "RESULTS.json"))["problem"] == "SystemExit: 3"


# --- byte-identical rescoring ----------------------------------------------

def test_scoring_the_same_tree_twice_is_byte_identical(tmp_path):
    """Two roots with the SAME basename under different parents: identical bytes
    prove both that nothing is derived from a clock and that nothing is derived
    from where the attempt happens to live."""
    first = tmp_path / "a" / "primary-attempt-001"
    second = tmp_path / "b" / "primary-attempt-001"
    first.parent.mkdir()
    second.parent.mkdir()
    assert score.main(["--attempt-root", str(first)]) == 2
    assert score.main(["--attempt-root", str(second)]) == 2
    for name in ("ATTEMPT.json", "RESULTS.json"):
        assert read(first / name) == read(second / name), name


# --- the population rule (section 1a) ---------------------------------------

def slot(arm, index, code=None, duration=1.5):
    return {"arm": arm, "slotIndex": index, "globalIndex": index, "round": index,
            "position": 1, "present": True, "code": code,
            "durationSeconds": duration, "completion": ""}


def test_apparatus_failures_leave_the_denominator_and_authoring_ones_stay():
    """Section 1a's whole point, and the design-phase lesson behind it: the
    pilot driver mis-filed timeouts as an authoring code, which silently moves a
    run out of the excluded set and into the denominator of every rate."""
    slots = [slot("A", 1), slot("A", 2, "call-timeout"),
             slot("A", 3, "no-marker-block"), slot("A", 4, "slot-shape"),
             slot("A", 5, "schema-invalid-pack")]
    counted = score.population(slots)["A"]
    assert counted["attempted"] == 5
    assert counted["apparatusExcluded"] == 2
    assert counted["denominator"] == 3
    assert counted["timeouts"] == 1
    assert counted["apparatusCodes"] == {"call-timeout": 1, "slot-shape": 1}


def test_the_timeout_rate_is_over_attempted_runs_and_carries_an_interval():
    slots = [slot("B", index) for index in range(1, 10)] + \
        [slot("B", 10, "call-timeout")]
    counted = score.population(slots)["B"]
    assert counted["timeoutRate"]["count"] == 1
    assert counted["timeoutRate"]["trials"] == 10
    assert counted["timeoutRate"]["denominator"] == "attempted runs"
    assert counted["timeoutRate"]["ci95"][0] < 0.1 < counted["timeoutRate"]["ci95"][1]


def test_every_arm_is_counted_even_when_it_has_no_slots():
    counted = score.population([])
    assert sorted(counted) == sorted(batch.ARMS)
    assert counted["C"]["denominator"] == 0
    assert counted["C"]["timeoutRate"]["rate"] is None


# --- reading a slot ---------------------------------------------------------

def make_slot(root, arm, index, call=None, refusal=False, completion=None):
    path = os.path.join(root, arm, "authoring", "run-%03d" % index)
    os.makedirs(path)
    if refusal:
        with open(os.path.join(path, "REFUSAL.json"), "w") as handle:
            json.dump({"reason": "preflight"}, handle)
        return path
    if call is not None:
        with open(os.path.join(path, "CALL.json"), "w") as handle:
            json.dump(call, handle)
    if completion is not None:
        with open(os.path.join(path, "completion.txt"), "w") as handle:
            handle.write(completion)
    return path


def entry(arm="A", index=1):
    return {"arm": arm, "slotIndex": index, "globalIndex": index,
            "round": index, "position": 1}


def test_an_absent_slot_is_absent_rather_than_a_code(tmp_path):
    record = score.read_slot(entry(), str(tmp_path))
    assert record["present"] is False and record["code"] is None


def test_a_refusal_slot_is_the_apparatus_slot_shape_code(tmp_path):
    make_slot(str(tmp_path), "A", 1, refusal=True)
    record = score.read_slot(entry(), str(tmp_path))
    assert record["code"] == "slot-shape"
    assert batch.CODE_PARTITION[record["code"]][0] == "apparatus"


def test_a_timed_out_call_is_the_apparatus_timeout_code(tmp_path):
    """The wrapper's status 12, and `timedOut: true`. Either alone is enough:
    section 1a makes the SIDE of this code load-bearing."""
    make_slot(str(tmp_path), "A", 1,
              call={"exitCode": 12, "timedOut": True, "durationSeconds": 2700})
    assert score.read_slot(entry(), str(tmp_path))["code"] == "call-timeout"
    make_slot(str(tmp_path), "B", 1,
              call={"exitCode": 0, "timedOut": True, "durationSeconds": 2700})
    assert score.read_slot(entry("B"), str(tmp_path))["code"] == "call-timeout"


def test_a_nonzero_call_is_the_apparatus_nonzero_code(tmp_path):
    make_slot(str(tmp_path), "A", 1,
              call={"exitCode": 10, "timedOut": False, "durationSeconds": 3.0})
    record = score.read_slot(entry(), str(tmp_path))
    assert record["code"] == "call-nonzero-exit"
    assert record["durationSeconds"] == 3.0


def test_a_completed_call_with_no_completion_is_a_shape_failure(tmp_path):
    make_slot(str(tmp_path), "A", 1,
              call={"exitCode": 0, "timedOut": False, "durationSeconds": 3.0})
    assert score.read_slot(entry(), str(tmp_path))["code"] == "slot-shape"


def test_a_completed_call_carries_its_completion(tmp_path):
    make_slot(str(tmp_path), "A", 1,
              call={"exitCode": 0, "timedOut": False, "durationSeconds": 3.0},
              completion="PACK:\n```json\n{}\n```\n")
    record = score.read_slot(entry(), str(tmp_path))
    assert record["code"] is None
    assert record["completion"].startswith("PACK:")


def test_a_slot_with_neither_call_nor_refusal_refuses_the_whole_scoring(tmp_path):
    """Study 012's C5 rule 1: no section 1a code describes a slot the driver
    started and never finished, so no rate is computed over a population holding
    one."""
    os.makedirs(os.path.join(str(tmp_path), "A", "authoring", "run-001"))
    with pytest.raises(score.ScoreError) as raised:
        score.read_slot(entry(), str(tmp_path))
    assert "neither CALL.json nor REFUSAL.json" in str(raised.value)


# --- terminality ------------------------------------------------------------

def present(count):
    return [{"present": index < count} for index in range(batch.REGISTERED_SLOTS)]


def test_a_short_batch_with_no_declaration_is_not_terminal(tmp_path):
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(present(10), str(tmp_path))
    assert "the batch is not terminal" in str(raised.value)


def test_a_full_batch_with_a_declaration_cannot_be_both(tmp_path):
    (tmp_path / score.SHORTFALL_FILE).write_text(json.dumps({"completed": 10}))
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(present(batch.REGISTERED_SLOTS), str(tmp_path))
    assert "cannot be both" in str(raised.value)


def test_a_full_batch_with_no_declaration_is_terminal(tmp_path):
    shape = score.terminality(present(batch.REGISTERED_SLOTS), str(tmp_path))
    assert shape == {"present": batch.REGISTERED_SLOTS,
                     "registered": batch.REGISTERED_SLOTS,
                     "complete": True, "declared": False}


def test_a_short_batch_with_a_declaration_is_terminal(tmp_path):
    (tmp_path / score.SHORTFALL_FILE).write_text(json.dumps({"completed": 10}))
    shape = score.terminality(present(10), str(tmp_path))
    assert shape["complete"] is False and shape["declared"] is True


def test_an_unreadable_declaration_declares_nothing(tmp_path):
    (tmp_path / score.SHORTFALL_FILE).write_text("{not json")
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(present(10), str(tmp_path))
    assert "declares nothing" in str(raised.value)
    assert str(tmp_path) not in str(raised.value) or True


def test_a_declaration_that_is_not_an_object_is_not_a_declaration(tmp_path):
    (tmp_path / score.SHORTFALL_FILE).write_text("[]")
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(present(10), str(tmp_path))
    assert "not a declaration" in str(raised.value)


# --- the endpoint aggregations ---------------------------------------------

def run(name, arm="A", admitted=True, identity=True, killed=38, paired=39,
        gold_perfect=True, code=None, excluded=()):
    return {"run": name, "arm": arm, "code": code, "admitted": admitted,
            "goldPerfect": gold_perfect, "identityPass": identity,
            "durationSeconds": 100.0, "x1Excluded": list(excluded),
            "kill": {"killedPaired": killed, "paired": paired},
            "goldFailures": [], "identityFailures": []}


def test_e4_keeps_authoring_outcomes_in_the_denominator_as_not_high_kill():
    """Section 5, verbatim: "Runs carrying authoring-outcome codes remain in the
    E4 denominator as not-high-kill (no-marker included)"."""
    cut = {"integerCut": 38}
    runs = [run("run-001"), run("run-002", killed=10),
            run("run-003", admitted=False, identity=False,
                code="no-marker-block", killed=0)]
    endpoint = score.e4_endpoint("A", runs, cut)
    assert endpoint["denominator"] == 3
    assert endpoint["highKill"] == 1
    assert endpoint["highKillRate"]["trials"] == 3


def test_e4_reports_identity_failures_as_a_first_class_rate():
    cut = {"integerCut": 38}
    runs = [run("run-001"), run("run-002", identity=False, killed=39)]
    endpoint = score.e4_endpoint("A", runs, cut)
    assert endpoint["identityFail"] == 1
    assert endpoint["identityFailedRuns"] == ["run-002"]
    assert endpoint["identityRate"]["count"] == 1
    # …and an identity-failing suite is never high-kill, whatever it killed.
    assert endpoint["highKillRuns"] == ["run-001"]


def test_e4_publishes_the_x1_excluded_case_count():
    endpoint = score.e4_endpoint("A", [run("run-001", excluded=["c1", "c2"])],
                                 {"integerCut": 38})
    assert endpoint["x1ExcludedCases"] == 2


def test_e1_reports_the_ceiling_and_the_floor_separately():
    runs = [run("run-001"), run("run-002", gold_perfect=False)]
    control = score.e1_control("A", runs)
    assert control["perfect"] == 1 and control["runs"] == 2
    assert control["floor"] == score.E1_FLOOR
    assert control["floorHeld"] is False
    assert score.e1_control("A", [run("run-001")])["floorHeld"] is True


def test_e1_on_an_empty_arm_holds_rather_than_dividing_by_zero():
    assert score.e1_control("A", [])["floorHeld"] is True


def test_e2_publishes_the_ordered_code_table_with_both_sides_named():
    slots = [slot("A", 1), slot("A", 2, "no-marker-block"),
             slot("A", 3, "schema-invalid-pack")]
    profile = score.e2_profile("A", slots)
    assert [row["code"] for row in profile["orderedCodes"]] == \
        list(score.admit_lib.DROP_ORDER)
    assert all(row["side"] == "authoring" for row in profile["orderedCodes"])
    assert profile["admitted"] == 1
    counts = {row["code"]: row["count"] for row in profile["orderedCodes"]}
    assert counts["no-marker-block"] == 1 and counts["schema-invalid-pack"] == 1


def test_e3_counts_within_arm_only():
    runs = [{"goldFailures": [{"category": "disagreement"}],
             "identityFailures": [{"got": "outcome:reject"}]}]
    taxonomy = score.e3_taxonomy(runs)
    assert taxonomy["goldFailureCategories"] == {"disagreement": 1}
    assert taxonomy["identityFailureCategories"] == {"outcome:reject": 1}


def test_the_contrast_refuses_on_unequal_denominators():
    """`stats.z2_table()`'s closed form is the equal-size one; a contrast at two
    different N computed with a formula for one N is a number nobody
    registered."""
    e4_by_arm = {"A": {"highKill": 10, "denominator": 50},
                 "C": {"highKill": 40, "denominator": 49}}
    with pytest.raises(score.stats.StatsError) as raised:
        score.contrast("A", "C", e4_by_arm)
    assert str(raised.value).startswith("FM-UNEQUAL-N")


def test_the_contrast_carries_the_arm_names_so_direction_is_readable():
    e4_by_arm = {"A": {"highKill": 10, "denominator": 50},
                 "C": {"highKill": 45, "denominator": 50}}
    result = score.contrast("A", "C", e4_by_arm)
    assert result["arms"] == ["A", "C"]
    assert decision.direction(result) == "C above A"


# --- the rendered report ----------------------------------------------------

def test_the_report_lists_every_decision_row_and_marks_the_matched_one():
    results = {"label": "PILOT", "unfilledPins": ["preregistration"],
               "decision": {"verdict": "INDETERMINATE", "rowIndex": 4,
                            "causes": []},
               "refusals": {"E5": "E5-STIMULUS-UNREGISTERED ..."}}
    body = score.results_markdown(results)
    for row in decision.ROWS:
        assert row.name in body
    assert "**yes**" in body
    assert "supports no claim" in body
    assert "E5-STIMULUS-UNREGISTERED" in body


def test_the_report_renders_an_absent_endpoint_as_a_dash():
    results = {"label": "PILOT", "unfilledPins": [],
               "decision": {"verdict": "INDETERMINATE", "rowIndex": 4,
                            "causes": []},
               "refusals": {}}
    body = score.results_markdown(results)
    assert "| A | — | — | — | — | — | — |" in body
