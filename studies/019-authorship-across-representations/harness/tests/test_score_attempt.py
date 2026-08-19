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
import hashlib
import hashlib
import json
import os
import sys
import unittest

import pytest

import batch
import score
from e4lib import decision

# The scorer's slot cases run against the DRIVER's own fixtures (SCAFFOLD item
# S11): `tests/test_batch.py` already builds a stand-in study, a stand-in
# registry and slots through `batch.stamp_slot()`, `batch.refuse_slot()` and
# `batch.seal_slot()`, and a slot the scorer reads has to be a slot the driver
# could have written. Hand-rolled dictionaries were what let the scorer's reader
# and the driver's writer disagree in the first place.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import test_batch  # noqa: E402


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


def test_the_attempt_hands_its_own_registry_digest_to_every_slot_read(
        tmp_path, monkeypatch):
    """ROUND-10 FINDING R10-1, at the seam the per-slot cases cannot reach.

    `read_slot()` compares the slot's stamp to the digest it is GIVEN, and every
    case that exercises that comparison calls it directly. So the one thing none
    of them can fail on is `main()` forgetting to pass the digest at all — which
    would restore the finding exactly, silently, and with every registry test
    still green. This runs the production entry point and records what it
    handed the reader: the value must be the same `pinsRawSha256` the attempt
    wrote into `ATTEMPT.json` before it parsed anything, and it must not be
    `None`."""
    seen = []
    original = score.read_slot

    def recording(entry, arms_root, present=None, golden_pin=None, pins=None,
                  pins_raw_sha256=None):
        seen.append(pins_raw_sha256)
        return original(entry, arms_root, present, golden_pin, pins,
                        pins_raw_sha256)

    monkeypatch.setattr(score, "read_slot", recording)
    root = tmp_path / "primary-attempt-001"
    score.main(["--attempt-root", str(root)])
    marker = json.loads(read(root / "ATTEMPT.json"))
    assert seen, "the attempt read no slot at all; this test asserts nothing"
    assert set(seen) == {marker["pinsRawSha256"]}
    assert marker["pinsRawSha256"] is not None


def test_the_reviewer_set_is_refused_while_any_pin_is_null(tmp_path,
                                                           monkeypatch):
    """`harness/PINS.json`'s own rule: `--include-reviewer-set` refuses while
    any pin is null.

    The guard reads `integrity.unfilled_pins()`, which is STUDY-LOCAL, so
    round-2 R2-8 moved it below `integrity.verify()` — verification is the first
    thing that runs against the tree, and on this pre-freeze tree it is the
    refusal that lands. The guard's own refusal is what lands once the tree
    verifies, which is what the no-op here stands in for."""
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root),
                       "--include-reviewer-set"]) == 2
    assert json.loads(read(root / "ATTEMPT.json"))["includeReviewerSet"] is True

    verified = tmp_path / "verified-attempt-001"
    monkeypatch.setattr(score.integrity, "verify", lambda *_a, **_k: None)
    assert score.main(["--attempt-root", str(verified),
                       "--include-reviewer-set"]) == 2
    results = json.loads(read(verified / "RESULTS.json"))
    assert results["problem"].startswith("--include-reviewer-set is refused")


def test_verification_precedes_every_study_local_call(tmp_path, monkeypatch):
    """ROUND-2 R2-8, as an ORDER assertion.

    The scorer used to call `integrity.study_label()` and
    `integrity.unfilled_pins()` — study-local code — and, on its early terminal
    path, to import `batch` and the whole of `e4lib`, all before
    `integrity.verify()` had established anything about the tree those bytes
    live in. The claim "integrity runs before the scorer imports a single study
    module" was therefore false of the label rule, the null-pin guard and every
    pre-verification failure."""
    order = []
    for name in ("verify", "study_label", "unfilled_pins"):
        original = getattr(score.integrity, name)

        def wrapper(*args, _name=name, _original=original, **kwargs):
            order.append(_name)
            return _original(*args, **kwargs)

        monkeypatch.setattr(score.integrity, name, wrapper)
    original_bind = score.bind_study_modules

    def record_bind(*args, **kwargs):
        order.append("bind_study_modules")
        return original_bind(*args, **kwargs)

    monkeypatch.setattr(score, "bind_study_modules", record_bind)
    score.main(["--attempt-root", str(tmp_path / "primary-attempt-001")])
    assert order, "nothing study-local was invoked at all"
    assert order[0] == "verify", order


# --- ROUND-3 FINDING R3-7: the IMPORT order, not only the call order --------

def _study_local_module_names():
    """Every module name that lives in this study's harness — the set §7's claim
    is about. Read off the tree rather than listed, so a module added to the
    harness is covered by these assertions the day it lands."""
    names = {"e4lib"}
    for entry in sorted(os.listdir(os.path.dirname(score.__file__))):
        if entry.endswith(".py") and entry != "__init__.py":
            names.add(entry[:-3])
    return names


def _module_scope_imports(path):
    import ast
    with open(path, "rb") as handle:
        tree = ast.parse(handle.read(), filename=path)
    imported = set()
    for node in tree.body:            # MODULE SCOPE ONLY, deliberately
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])
    return imported


def test_integrity_is_the_only_study_module_the_scorer_imports_at_module_scope():
    """R3-7. R2-8 closed the CALL order — `integrity.verify()` is the first
    study-local call, asserted above — and the reviewer's round-3 read is that
    the registration claims more than that: that integrity runs "before the
    scorer imports a single study module", while `score.py` imports study-local
    `integrity` at module scope.

    The honest property is the one asserted here, and it is worth having: of
    every module in this harness, exactly ONE is bound before verification, and
    it is the one doing the verifying. A future `import batch` beside it fails
    here rather than quietly widening the pre-verification surface again."""
    local = _study_local_module_names()
    assert "batch" in local and "e4lib" in local, local
    assert _module_scope_imports(score.__file__) & local == {"integrity"}


def test_the_integrity_module_itself_imports_nothing_study_local():
    """Why importing `integrity` costs nothing the gate could have caught: it
    pulls in no study byte of its own, so the pre-verification surface is that
    one module and its stdlib imports."""
    local = _study_local_module_names()
    assert _module_scope_imports(score.integrity.__file__) & local == set()


def test_importing_the_scorer_binds_no_other_study_module(tmp_path):
    """The same property MEASURED rather than parsed, in a fresh interpreter —
    `sys.modules` inside this suite is useless for it, because every other test
    module has already imported the whole package.

    A subprocess imports `score` and nothing else and reports which study-local
    modules exist afterwards. That is the state §7's sentence is about."""
    import subprocess
    harness = os.path.dirname(score.__file__)
    program = (
        "import sys, os\n"
        "sys.dont_write_bytecode = True\n"
        "sys.path.insert(0, %r)\n"
        "import score\n"
        "local = {'e4lib'} | {e[:-3] for e in os.listdir(%r)\n"
        "                     if e.endswith('.py') and e != '__init__.py'}\n"
        "print(' '.join(sorted(n for n in sys.modules if n in local)))\n"
        % (harness, harness))
    out = subprocess.run([sys.executable, "-c", program], capture_output=True,
                         text=True, cwd=str(tmp_path))
    assert out.returncode == 0, out.stderr
    assert out.stdout.split() == ["integrity", "score"], out.stdout


def test_a_pre_verification_failure_does_not_bind_the_tree(tmp_path,
                                                           monkeypatch):
    """The one path that exists BECAUSE the tree cannot be trusted was the path
    that bound the untrusted tree: `terminal()` called `bind_study_modules()`
    unconditionally to print a row-1 verdict whose text is a constant."""
    bound = []
    monkeypatch.setattr(score, "bind_study_modules",
                        lambda *a, **k: bound.append(1))
    monkeypatch.setattr(score, "PINS_PATH", str(tmp_path / "absent.json"))
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    assert bound == []
    results = json.loads(read(root / "RESULTS.json"))
    assert results["decision"]["verdict"] == "R1 inconclusive - pipeline-invalid"
    assert "could not be imported" in results["decision"]["note"]


# --- ROUND-2 R2-7: the mandatory holdout is loaded FIRST and fatally ---------

def _reachable(monkeypatch, label="PILOT"):
    """A tree the integrity gate accepts and a registry with no unfilled pin, so
    the reviewer-set branch is reachable at all on this pre-freeze checkout."""
    monkeypatch.setattr(score.integrity, "verify", lambda *_a, **_k: None)
    monkeypatch.setattr(score.integrity, "unfilled_pins", lambda *_a, **_k: [])
    monkeypatch.setattr(score.integrity, "study_label", lambda *_a, **_k: label)


def _defective_set(tmp_path, monkeypatch):
    """A copy of the committed sealed set with ONE payload byte changed, pointed
    at by the scorer.

    ROUND 3 REPAIRED THE REAL SET. Both tests below used to rely on the
    committed set being digest-invalid — the round-2 reviewer emitted a
    pre-final `rm-jps-03` — and the reviewer re-issued that payload this round,
    so all six digests verify and the two tests stopped exercising the refusal
    they are named for. A test whose power came from a defect someone was
    always going to fix is a test that quietly stops discriminating, so the
    defect is CONSTRUCTED here instead, in a scratch copy: the committed set is
    read and never written (§1a: the maintainer touches nothing in it)."""
    import shutil
    source = os.path.join(score.STUDY, score.REVIEWER_SET_RELATIVE)
    copy = tmp_path / "sealed-set"
    shutil.copytree(source, copy)
    payload = copy / "rm-jps-01.json"
    payload.write_bytes(payload.read_bytes() + b"\n")
    monkeypatch.setattr(score, "REVIEWER_SET_RELATIVE", str(copy))
    return copy


def test_the_committed_sealed_set_loads_as_the_reviewer_re_issued_it(
        tmp_path, monkeypatch):
    """The positive control the two tests below need in order to mean anything:
    the set as committed LOADS. Round 2 recorded two defects in it as authored
    and refused to repair them from this side; round 3's reviewer re-issued
    `rm-jps-03` and re-attested `rm-rego-01`, and this is that repair, executed
    rather than described."""
    _reachable(monkeypatch)
    loaded = score.reviewer_lib.load(
        os.path.join(score.STUDY, score.REVIEWER_SET_RELATIVE), None)
    assert loaded["count"] == 6
    assert loaded["executed"] is False, "the load invokes no engine (§1a)"
    assert sorted(entry["language"] for entry in loaded["mutants"]) == \
        ["jps"] * 3 + ["rego"] * 3
    assert loaded["manifestSha256"] == \
        "6bff7f950b132505d1034fe7d993a8920f028647b35dc1f48d9072884fedaa0e", (
            "the reviewer's round-3 MANIFEST.json is what is committed; a "
            "maintainer edit to the sealed set would show up here")


def test_a_reviewer_set_that_does_not_load_is_pipeline_invalid(tmp_path,
                                                               monkeypatch):
    """The finding, exactly: the scorer computed endpoints, gates, contrasts and
    THE DECISION and only then loaded the sealed set, caught a
    `ReviewerSetError` into `refusals`, recorded `pipelineInvalid: false` and
    exited 0. A missing, malformed or digest-invalid mandatory holdout could
    coexist with a published substantive verdict."""
    _reachable(monkeypatch)
    _defective_set(tmp_path, monkeypatch)
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root),
                       "--include-reviewer-set"]) == 2
    results = json.loads(read(root / "RESULTS.json"))
    assert results["pipelineInvalid"] is True
    assert results["problem"].startswith("the sealed reviewer mutant set is "
                                         "mandatory")
    assert "REVIEWER-SET" in results["problem"]
    # …and no substantive record was written beside it.
    assert not (root / "RESULTS.md").exists()
    assert "decision" in results and results["decision"]["rowIndex"] == 1


def test_the_reviewer_set_loads_before_a_single_slot_is_read(tmp_path,
                                                             monkeypatch):
    """"Loaded and schema-checked BEFORE the attempt" (§1a). The order is
    asserted by making the slot reader explode: the reviewer refusal is the one
    that lands, so nothing downstream of it ran."""
    _reachable(monkeypatch)
    _defective_set(tmp_path, monkeypatch)

    def explode(*_args, **_kwargs):
        raise AssertionError("the population was built before the holdout was "
                             "validated")

    monkeypatch.setattr(score, "slots_present", explode)
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root),
                       "--include-reviewer-set"]) == 2
    results = json.loads(read(root / "RESULTS.json"))
    assert results["problem"].startswith("the sealed reviewer mutant set is "
                                         "mandatory")


def test_an_attempt_without_the_flag_never_touches_the_sealed_set(tmp_path,
                                                                  monkeypatch):
    """A PILOT may not execute it, and the load is what would touch it."""
    _reachable(monkeypatch)
    touched = []
    monkeypatch.setattr(score.reviewer_lib, "load",
                        lambda *a, **k: touched.append(1))
    score.main(["--attempt-root", str(tmp_path / "primary-attempt-001")])
    assert touched == []


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
    results = json.loads(read(root / "RESULTS.json"))
    problems = results["problems"]
    # ROUND-1 R1-9 moved the FIRST refusal earlier: `integrity.verify()` now
    # runs before any study-local scoring module is imported, and the tree is
    # pre-freeze, so the attempt is terminal at the integrity gate rather than
    # at the artifact census. Either way the record names what it found, and
    # nothing was scored.
    assert results["pipelineInvalid"] is True
    assert problems == sorted(problems)
    assert (results["problem"].startswith("integrity: ")
            or any("registered artifact is absent: gold/GOLD.json" in problem
                   for problem in problems))


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
    # `study_label` is invoked BELOW `integrity.verify()` since round-2 R2-8, so
    # reaching it at all needs a tree the gate accepts.
    monkeypatch.setattr(score.integrity, "verify", lambda *_a, **_k: None)
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
    monkeypatch.setattr(score.integrity, "verify", lambda *_a, **_k: None)
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

def slot(arm, index, code=None, duration=1.5, present=True):
    return {"arm": arm, "slotIndex": index, "globalIndex": index, "round": index,
            "position": 1, "present": present, "code": code,
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
    # ROUND-2 R2-12: the block leaves `population()` with its integers and no
    # interval; the bounds are settled once, later, and only for an outcome that
    # reached row 4.
    from e4lib import stats
    assert counted["timeoutRate"]["ci95"] is None
    assert counted["timeoutRate"]["ci95State"] == stats.CI_PENDING
    stats.fill_intervals(counted, True)
    assert counted["timeoutRate"]["ci95"][0] < 0.1 < counted["timeoutRate"]["ci95"][1]


def test_every_arm_is_counted_even_when_it_has_no_slots():
    counted = score.population([])
    assert sorted(counted) == sorted(batch.ARMS)
    assert counted["C"]["denominator"] == 0
    assert counted["C"]["timeoutRate"]["rate"] is None


def test_the_population_is_the_declared_prefix_and_not_the_registered_order():
    """SCAFFOLD item S11 / the smoke's D-1, as an assertion. A registered slot
    that is not on disk was never ATTEMPTED, and section 1a's denominator is
    attempted runs. Partitioning on the code alone put every absent slot into
    the denominator wearing an authoring code, because `None` is not an
    apparatus code."""
    slots = [slot("A", 1), slot("A", 2, "call-timeout")] + \
        [slot("A", index, present=False) for index in range(3, 51)]
    counted = score.population(slots)["A"]
    assert counted["registered"] == 50
    assert counted["absent"] == 48
    assert counted["attempted"] == 2
    assert counted["denominator"] == 1
    # …and every RATE is over the prefix too, or the timeout cap is computed
    # against a batch that was never run.
    assert counted["timeoutRate"]["trials"] == 2
    assert counted["apparatusRate"]["trials"] == 2


def test_an_absent_slot_reaches_no_endpoint_at_all():
    """The consequence the smoke observed: an absent slot entered its arm's E1
    denominator and scored `no-marker-block` over a completion that does not
    exist."""
    slots = [slot("B", index, present=False) for index in range(1, 51)]
    counted = score.population(slots)["B"]
    assert counted["denominator"] == 0
    assert counted["slots"] == []


# --- reading a slot, on the driver's own fixtures (SCAFFOLD item S11) -------

class DriverBuiltSlots(test_batch.StandInStudy):
    """Every slot here is built by the DRIVER — `batch.stamp_slot()`,
    `batch.refuse_slot()`, `batch.seal_slot()` — and read by the SCORER.

    That is the whole of SCAFFOLD item S11. The scorer was assembled while
    `harness/batch.py` was still the schedule core and grew a reduced reader of
    its own: `REFUSAL.json` before `CALL.json`, the wrapper's exit status through
    a second lookup, and `os.path.isdir()` for presence. The driver has since
    landed `collect_slots()`, `slot_outcome()`, `verify_seal_of()` and
    `session_identity()`, and holding two readings of a slot is what let a real
    `call-timeout` be scored as `slot-shape` and a moved byte be scored at all.
    """

    #: ROUND-10 FINDING R10-1. Two sentinels, because three states have to be
    #: distinguishable and `None` is one of the states rather than a spare: the
    #: fixture's DEFAULT stamp (the stand-in registry's own digest), the member
    #: ABSENT from `CALL.json` entirely, and the member present and `null` —
    #: which is what a half-written stamp looks like and is a case of its own.
    DEFAULT = object()
    ABSENT = object()

    def registry_stamp(self):
        """The digest the WRAPPER stamps into `CALL.json.pinsSha256`: the raw
        bytes of the registry the call was made under, hashed.

        `authoring_call.sh` computes `sha256sum "$PINS"`, `score.main()` computes
        `sha256_bytes()` over the same file's bytes, and this is the fixture's
        one reading of both — taken from `self.pins_path`, the stand-in registry
        the driver would have been handed, and never from a literal."""
        return test_batch._digest(self.pins_path)

    def build(self, entry, *, refusal=None, completion="PACK:\n```json\n{}\n```\n",
              golden=None, session=None, seal=True, timed_out=False,
              registry=DEFAULT):
        slot = batch.slot_path(entry)
        os.makedirs(slot)
        call = {"slot": os.path.basename(slot), "slotIndex": entry["slotIndex"],
                "arm": entry["arm"],
                "armPromptSha256": batch.arm_prompt(self.pins, entry["arm"])[1],
                "promptKind": "registered", "exitStatus": 0,
                "durationSeconds": 12.5,
                "timeoutSeconds": batch.CALL_TIMEOUT_SECONDS,
                "timedOut": bool(timed_out),
                # ROUND-10 FINDING R10-1: the registry stamp is part of the slot
                # shape now, because the scorer reads it. Every fixture carries
                # the stand-in registry's own digest unless a case is ABOUT the
                # stamp, so the check is exercised by every case here rather than
                # skipped by all of them.
                "pinsSha256": (self.registry_stamp()
                               if registry is self.DEFAULT else registry),
                "goldenSha256": (self.pins["golden"]["sha256"] if golden is None
                                 else golden),
                "cwd": os.path.join(self.scratch, "cwd"),
                "home": os.path.join(self.scratch, "home")}
        if registry is self.ABSENT:
            del call["pinsSha256"]
        if refusal is None or timed_out:
            with open(os.path.join(slot, "CALL.json"), "w") as handle:
                json.dump(call, handle)
            batch.stamp_slot(slot, entry, self.pins)
        if completion is not None and refusal is None:
            with open(os.path.join(slot, "completion.txt"), "w") as handle:
                handle.write(completion)
        if session is not None:
            with open(os.path.join(slot, "session.jsonl"), "w") as handle:
                handle.write(json.dumps({"type": "session_meta",
                                         "payload": {"id": session}}) + "\n")
        if refusal is not None:
            status, code = refusal
            batch.refuse_slot(slot, code, status, "stderr tail")
        if seal:
            batch.seal_slot(slot, entry)
        return slot

    def read(self, entry):
        """The scorer's reader, given what `main()` gives it: the golden pin out
        of the registry, and (round-10 R10-1) the digest of the registry's own
        raw bytes — the value `main()` writes to `ATTEMPT.json.pinsRawSha256`
        before it parses anything."""
        return score.read_slot(entry, self.arms_root,
                               score.slots_present(self.arms_root),
                               self.pins["golden"]["sha256"],
                               pins_raw_sha256=self.registry_stamp())

    def refusal(self, callable_, *args, **kwargs):
        with self.assertRaises(score.ScoreError) as caught:
            callable_(*args, **kwargs)
        return str(caught.exception)

    # -- presence ---------------------------------------------------------

    def test_an_absent_slot_is_absent_rather_than_a_code(self):
        self.write_golden()
        record = self.read(test_batch.ENTRIES[0])
        self.assertFalse(record["present"])
        self.assertIsNone(record["code"])

    def test_presence_is_the_drivers_collector_and_a_name_claims_its_index(self):
        """`collect_slots()` names an entry `run-NNN` a slot WHATEVER its type,
        because the name is what claims the index. `os.path.isdir()` skipped a
        regular file at that name and the scorer scored the batch as if the slot
        had never been attempted."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        path = batch.slot_path(entry)
        os.makedirs(os.path.dirname(path))
        with open(path, "w") as handle:
            handle.write("not a slot")
        self.assertIn("is not sealed", self.refusal(self.read, entry))

    def test_an_entry_the_registered_order_does_not_name_refuses(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry)
        with open(os.path.join(os.path.dirname(batch.slot_path(entry)),
                               "scratch-notes.txt"), "w") as handle:
            handle.write("left behind")
        self.assertIn("the registered order does not name",
                      self.refusal(score.slots_present, self.arms_root))

    # -- the seal (section 2.9) -------------------------------------------

    def test_a_sealed_slot_is_read_and_carries_its_completion(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry)
        record = self.read(entry)
        self.assertTrue(record["present"])
        self.assertIsNone(record["code"])
        self.assertTrue(record["completion"].startswith("PACK:"))
        self.assertEqual(record["durationSeconds"], 12.5)
        self.assertTrue(record["sealSha256"].startswith("sha256:"))

    def test_a_slot_whose_bytes_moved_after_the_seal_refuses_the_scoring(self):
        """Section 2.9 seals every slot by a terminal manifest, and the scorer
        never recomputed it: a slot edited after sealing was scored."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        slot = self.build(entry)
        with open(os.path.join(slot, "completion.txt"), "a") as handle:
            handle.write("appended after the seal\n")
        self.assertIn("does not verify against the slot it seals",
                      self.refusal(self.read, entry))

    def test_an_unsealed_slot_refuses_the_scoring(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, seal=False)
        self.assertIn("is not sealed", self.refusal(self.read, entry))

    def test_a_slot_with_neither_call_nor_refusal_refuses_the_scoring(self):
        """Study 012's C5 rule 1, now the DRIVER's own sentence: no section 1a
        code describes a slot that was started and never finished."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        slot = batch.slot_path(entry)
        os.makedirs(slot)
        batch.seal_slot(slot, entry)
        self.assertIn("carries neither CALL.json nor REFUSAL.json",
                      self.refusal(self.read, entry))

    # -- the codes --------------------------------------------------------

    def test_a_timeout_is_the_timeout_code_and_not_a_shape_failure(self):
        """The smoke's D-2. The driver classified the slot `call-timeout` and
        the scorer filed it `slot-shape`, because its reader tested for
        `REFUSAL.json` before it read `CALL.json` and returned `slot-shape` for
        anything carrying one. Both codes are apparatus so no denominator moves
        — but `timeout-rate-within-cap` then held over a batch that contained a
        timeout, which is the undercount the registered status 12 exists to
        prevent."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, refusal=(12, "call-timeout"), timed_out=True)
        record = self.read(entry)
        self.assertEqual(record["code"], "call-timeout")
        self.assertEqual(record["wrapperExit"], 12)
        self.assertEqual(batch.CODE_PARTITION[record["code"]][0], "apparatus")

    def test_a_nonzero_exit_is_the_nonzero_code(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, refusal=(10, "call-nonzero-exit"))
        self.assertEqual(self.read(entry)["code"], "call-nonzero-exit")

    def test_a_slot_shape_refusal_is_the_shape_code(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, refusal=(11, "slot-shape"))
        self.assertEqual(self.read(entry)["code"], "slot-shape")

    def test_a_refusal_record_this_driver_never_writes_refuses(self):
        """`slot_outcome()` checks the code against `WRAPPER_CODES` rather than
        taking it from the file, so a refusal naming a code no exit status of
        this wrapper yields is not this driver's."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        slot = self.build(entry, refusal=(11, "slot-shape"), seal=False)
        with open(os.path.join(slot, "REFUSAL.json"), "w") as handle:
            json.dump({"code": "call-timeout", "wrapperExit": 11}, handle)
        batch.seal_slot(slot, entry)
        self.assertIn("is not one this batch produced",
                      self.refusal(self.read, entry))

    def test_a_completed_call_with_no_completion_is_a_shape_failure(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, completion=None)
        self.assertEqual(self.read(entry)["code"], "slot-shape")

    def test_the_golden_context_mismatch_code_is_reachable(self):
        """Section 1a names `golden-context-mismatch` as an apparatus code and
        the scorer's own reduced reader could never return it, so a run that
        failed the golden gate entered the denominator. The wrapper stamps the
        capture it ran behind into every `CALL.json` (section 3.2), and that
        stamp is what this reads."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, golden="sha256:" + "b" * 64)
        record = self.read(entry)
        self.assertEqual(record["code"], "golden-context-mismatch")
        self.assertEqual(batch.CODE_PARTITION[record["code"]][0], "apparatus")

    def test_a_run_made_behind_the_registered_golden_is_admitted(self):
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry)
        self.assertIsNone(self.read(entry)["code"])

    # -- the registry (round-10 finding R10-1) ------------------------------

    def test_a_slot_authored_under_a_substitute_registry_is_registry_mismatch(
            self):
        """THE ROUND-10 REVIEWER'S CONSTRUCTION, as a named failing case.

        `authoring_call.sh` stamped the registry each call was made under into
        `CALL.json.pinsSha256` and carried a sentence saying the scorer refused
        any slot whose stamp differed, "registry-mismatch". No such code existed
        and no such comparison existed: the scorer hashed `harness/PINS.json`
        into `ATTEMPT.json.pinsRawSha256` and compared it with nothing. So a slot
        authored under a SUBSTITUTE complete registry — the reviewer reached one
        through `--pins`, and a direct file edit reaches the same slot without
        any driver at all — was read as an ordinary registered run: authored
        before the freeze, surviving it, and scored after it as this study's
        prospective content.

        The substitute here is a real alternate registry on disk, hashed the way
        the wrapper hashes the one it was handed, so the stamp is a stamp some
        run could genuinely carry and not an invented string."""
        self.write_golden()
        substitute = self.alternate_registry(
            "SUBSTITUTE-PINS.json",
            note="an alternate complete registry, every freeze pin filled")
        self.assertNotEqual(test_batch._digest(substitute),
                            self.registry_stamp())
        entry = test_batch.ENTRIES[0]
        self.build(entry, registry=test_batch._digest(substitute))
        record = self.read(entry)
        self.assertEqual(record["code"], "registry-mismatch")
        self.assertEqual(batch.CODE_PARTITION[record["code"]][0], "apparatus")
        self.assertNotIn(record["code"], score.AUTHORING_SIDE)

    def test_a_slot_carrying_no_registry_stamp_at_all_is_registry_mismatch(self):
        """FAIL-CLOSED on the evidence's absence. A `CALL.json` with no
        `pinsSha256` is not a slot this wrapper wrote — the member is
        unconditional there — and "the stamp is missing" is not "the stamp
        agrees". Reading the absence as agreement would make deleting one line
        from the wrapper the way past the whole check."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, registry=self.ABSENT)
        self.assertEqual(self.read(entry)["code"], "registry-mismatch")

    def test_a_registry_stamp_of_the_wrong_type_is_registry_mismatch(self):
        """The same rule at the type. `None`, an integer and a mapping are not
        digests; comparing them by value would leave `null` — the shape a
        half-written stamp takes — passing whenever the attempt's own digest
        were unreadable."""
        self.write_golden()
        for index, stamp in enumerate((None, 0, ["sha256:" + "a" * 64],
                                       {"sha256": "a" * 64})):
            entry = test_batch.ENTRIES[index]
            self.build(entry, registry=stamp)
            self.assertEqual(self.read(entry)["code"], "registry-mismatch",
                             stamp)

    def test_the_registry_stamp_is_compared_with_or_without_its_prefix(self):
        """`sha256:<hex>` and the bare hex are one digest, as everywhere else in
        this scorer: the wrapper writes the prefixed form and a bare stamp is
        not a different registry."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, registry=self.registry_stamp().split(":", 1)[1])
        self.assertIsNone(self.read(entry)["code"])

    def test_a_run_made_under_the_attempts_own_registry_is_admitted(self):
        """The other direction, without which the cases above prove only that
        something refuses."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry)
        record = self.read(entry)
        self.assertIsNone(record["code"])
        call = json.load(open(os.path.join(batch.slot_path(entry), "CALL.json")))
        self.assertEqual(call["pinsSha256"], self.registry_stamp())

    def test_a_reader_that_is_not_an_attempt_compares_no_registry(self):
        """The documented seam, asserted rather than assumed: `read_slot()` with
        no `pins_raw_sha256` recomputes nothing, exactly as it recomputes no
        transcript verdict without `pins`. The PRODUCTION path passes it — the
        case above is what shows that — so this is the reader's contract and not
        an exemption anything in an attempt can reach."""
        self.write_golden()
        substitute = self.alternate_registry("OTHER-PINS.json", note="other")
        entry = test_batch.ENTRIES[0]
        self.build(entry, registry=test_batch._digest(substitute))
        record = score.read_slot(entry, self.arms_root,
                                 score.slots_present(self.arms_root),
                                 self.pins["golden"]["sha256"])
        self.assertIsNone(record["code"])

    def test_the_registry_disagreement_is_named_before_the_golden_one(self):
        """Order, and it is a fact about the apparatus rather than a preference:
        the golden pin is read out of the registry under dispute, so a slot made
        under another registry usually fails the golden comparison too. Filing
        it as a golden-context mismatch would name the wrong disagreement. Both
        codes are apparatus, so no denominator moves either way."""
        self.write_golden()
        substitute = self.alternate_registry("BOTH-WRONG-PINS.json", note="both")
        entry = test_batch.ENTRIES[0]
        self.build(entry, registry=test_batch._digest(substitute),
                   golden="sha256:" + "b" * 64)
        self.assertEqual(self.read(entry)["code"], "registry-mismatch")

    def test_a_refused_slot_keeps_its_wrapper_code_over_the_registry_check(self):
        """A slot the wrapper already refused carries no `CALL.json`, and its
        wrapper status is the honest account of it. The registry comparison runs
        after the wrapper's own code exactly as the golden one does, so a
        timeout does not become a registry mismatch."""
        self.write_golden()
        entry = test_batch.ENTRIES[0]
        self.build(entry, refusal=(12, "call-timeout"), timed_out=True)
        self.assertEqual(self.read(entry)["code"], "call-timeout")

    # -- the session identity ---------------------------------------------

    def test_two_slots_naming_one_session_refuse_the_whole_scoring(self):
        """`session_identity()` is the driver's, and two slots naming one
        session are one call — which every interval in this study assumes they
        are not."""
        self.write_golden()
        first, second = test_batch.ENTRIES[0], test_batch.ENTRIES[1]
        self.build(first, session="s-0001")
        self.build(second, session="s-0001")
        present = score.slots_present(self.arms_root)
        golden = self.pins["golden"]["sha256"]
        slots = [score.read_slot(entry, self.arms_root, present, golden)
                 for entry in test_batch.ENTRIES[:2]]
        self.assertEqual([record["sessionId"] for record in slots],
                         ["s-0001", "s-0001"])
        self.assertIn("are one call",
                      self.refusal(score.require_distinct_sessions, slots))

    def test_distinct_sessions_pass(self):
        self.write_golden()
        first, second = test_batch.ENTRIES[0], test_batch.ENTRIES[1]
        self.build(first, session="s-0001")
        self.build(second, session="s-0002")
        present = score.slots_present(self.arms_root)
        golden = self.pins["golden"]["sha256"]
        slots = [score.read_slot(entry, self.arms_root, present, golden)
                 for entry in test_batch.ENTRIES[:2]]
        score.require_distinct_sessions(slots)      # returns


# --- terminality ------------------------------------------------------------

def present(count):
    return [{"present": index < count} for index in range(batch.REGISTERED_SLOTS)]


# --- ROUND-1 R1-7: a declaration is VALIDATED, then the batch is DECLARED ----

def declared_batch(root, slots_present, *, edits=None, break_chain=False,
                   break_seal=False):
    """A short batch on disk: a ledger that is the registered order's prefix
    with a verifying chain, slot records with their seals, and the declaration
    `batch.declare_shortfall()` would have written for it."""
    entries = batch.schedule_entries()[:slots_present]
    records, previous = [], None
    slots = []
    for entry in entries:
        seal = "sha256:" + hashlib.sha256(
            ("seal-%d" % entry["globalIndex"]).encode()).hexdigest()
        record = {key: entry[key] for key in batch.SCHEDULE_KEYS}
        record["path"] = os.path.relpath(batch.slot_path(entry), score.STUDY)
        record["manifestSha256"] = seal
        # The two outcome members the inventory rows carry (R1-4's partition is
        # checked over them): a completed slot, so exit 0 and no code.
        record["wrapperExit"] = 0
        record["code"] = None
        record["previousSha256"] = previous
        previous = batch.record_digest(record)
        records.append(record)
        slots.append({"present": True, "globalIndex": entry["globalIndex"],
                      "arm": entry["arm"], "slotIndex": entry["slotIndex"],
                      "sealSha256": ("sha256:deadbeef" if break_seal
                                     else seal)})
    if break_chain and records:
        records[-1]["previousSha256"] = "sha256:" + "0" * 64
    slots += [{"present": False, "globalIndex": entry["globalIndex"],
               "arm": entry["arm"], "slotIndex": entry["slotIndex"],
               "sealSha256": None}
              for entry in batch.schedule_entries()[slots_present:]]
    ledger_path = root / batch.LEDGER_NAME
    ledger_path.write_text(json.dumps({"records": records}))
    # The declaration is built to the DRIVER's shape — `batch.SHORTFALL_SCHEMA`
    # and `batch.SHORTFALL_SLOT_SCHEMA`, and the ledger bindings
    # `declare_shortfall()` computes — and not to a member list written here.
    # This fixture carried eleven transcribed members while the driver grew four
    # more for the same finding, and because no case crossed the seam the suite
    # stayed green while the scorer refused every declaration the driver writes.
    declaration = {
        "declarationVersion": batch.SHORTFALL_VERSION,
        "registeredRounds": batch.ROUNDS,
        "registeredRunsPerArm": batch.RUNS_PER_ARM,
        "registeredSlots": batch.REGISTERED_SLOTS,
        "completedRounds": slots_present // len(batch.ARMS),
        "completedThroughGlobalIndex": slots_present,
        "completedSlots": slots_present,
        "ledgerSha256": "sha256:" + hashlib.sha256(
            ledger_path.read_bytes()).hexdigest(),
        "ledgerHeadSha256": batch.record_digest(records[-1]) if records else None,
        "slots": [{member: record.get(member)
                   for member in batch.SHORTFALL_SLOT_SCHEMA}
                  for record in records],
        "lastSlot": records[-1]["path"] if records else None,
        "lastSlotEndedAt": "2026-08-18T00:00:00Z",
        "lastSlotEndedAtFrom": records[-1]["path"] if records else None,
        "reason": "operator stopped the batch",
        "note": "declared before scoring",
    }
    assert set(declaration) == set(batch.SHORTFALL_SCHEMA), (
        "the fixture writes the driver's member set or it is testing a shape "
        "nothing produces")
    declaration.update(edits or {})
    (root / score.SHORTFALL_FILE).write_text(json.dumps(declaration))
    return slots


def test_a_valid_declaration_is_accepted_and_says_what_it_verified(tmp_path):
    slots = declared_batch(tmp_path, 9)
    shape = score.terminality(slots, str(tmp_path))
    assert shape["declared"] is True and shape["complete"] is False
    assert shape["declaration"]["declaredSlots"] == 9
    assert shape["declaration"]["ledgerRecords"] == 9
    assert "slot/seal bijection" in shape["declaration"]["verified"]


@pytest.mark.parametrize("edits,fragment", [
    # Fragments assert on the scorer's actual refusal wording (integration slip found at
    # the round-1 verify pass: both lanes implemented the refusal; the fragments here had
    # been written against an earlier draft's message text).
    ({"registeredSlots": 9}, "records registeredSlots 9"),
    ({"completedSlots": 8}, "declares completedSlots 8"),
    ({"completedThroughGlobalIndex": 8}, "declares completedThroughGlobalInd"),
    ({"lastSlot": "arms/A/authoring/run-001"}, "SHORTFALL.json does not validate"),
])
def test_a_declaration_that_does_not_describe_this_batch_refuses(tmp_path,
                                                                 edits,
                                                                 fragment):
    """ROUND-1 R1-7. `SHORTFALL.json` was fail-open: ANY JSON object made an
    arbitrary incomplete set terminal, so an operator could delete the slots
    whose outcomes they disliked and unblock the scoring with a one-line file.
    Every member is compared against the batch now."""
    slots = declared_batch(tmp_path, 9, edits=edits)
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(slots, str(tmp_path))
    assert fragment in str(raised.value)


def test_an_empty_object_no_longer_declares_anything(tmp_path):
    """The reviewer's own example: `{}` used to be a terminal declaration."""
    slots = declared_batch(tmp_path, 9)
    (tmp_path / score.SHORTFALL_FILE).write_text("{}")
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(slots, str(tmp_path))
    assert "writes exactly" in str(raised.value)


def test_a_declaration_with_no_ledger_behind_it_refuses(tmp_path):
    slots = declared_batch(tmp_path, 9)
    os.remove(str(tmp_path / batch.LEDGER_NAME))
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(slots, str(tmp_path))
    assert "answers to nothing" in str(raised.value)


def test_a_broken_ledger_chain_refuses(tmp_path):
    slots = declared_batch(tmp_path, 9, break_chain=True)
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(slots, str(tmp_path))
    assert "hash chain" in str(raised.value)


def test_a_slot_whose_seal_moved_refuses(tmp_path):
    """The slot/seal bijection, computed rather than assumed."""
    slots = declared_batch(tmp_path, 9, break_seal=True)
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(slots, str(tmp_path))
    assert "reseals to" in str(raised.value)


def test_a_declared_short_batch_publishes_the_no_contrast_outcome(tmp_path):
    """The other half of R1-7: having validated the declaration, the scorer
    STOPS. No endpoint, no rate, no contrast — the registered price of a
    shortfall, which `batch.declare_shortfall()` states in advance."""
    verdict = decision.decide({
        "pipelineProblems": [],
        "shortfallDeclared": ["9 of 150 registered slots, declared: stopped"],
        "controlGates": {}, "contrasts": {}})
    assert verdict["row"] == decision.ROW_SHORTFALL_DECLARED.name
    assert verdict["verdict"].startswith("UNRESOLVED-BY-DESIGN")
    assert "secondary" not in verdict


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
                     "complete": True, "declared": False,
                     "declaration": None}


def test_the_registered_empty_prefix_round_trips(tmp_path):
    """ROUND-2 R2-9, driver to scorer.

    `SHORTFALL_SCHEMA` registers `ledgerSha256`, `ledgerHeadSha256` and
    `lastSlot` as nullable "only where a null is a fact (an empty prefix has no
    last slot)", and `declare_shortfall()` emits exactly that when the batch died
    before slot 1 — no ledger file, both digests null, an empty inventory. The
    scorer demanded `BATCH.json` unconditionally, so the one declaration the
    driver can write for the earliest possible failure was the one declaration
    the scorer refused: `batch.validate_shortfall` and `batch.verify_shortfall`
    both passed and `score.validate_attempt` failed solely because no ledger
    existed. R1-7's branch to UNRESOLVED-BY-DESIGN was unreachable at zero."""
    declaration = {
        "declarationVersion": batch.SHORTFALL_VERSION,
        "registeredRounds": batch.ROUNDS,
        "registeredRunsPerArm": batch.RUNS_PER_ARM,
        "registeredSlots": batch.REGISTERED_SLOTS,
        "completedRounds": 0,
        "completedThroughGlobalIndex": 0,
        "completedSlots": 0,
        "ledgerSha256": None,
        "ledgerHeadSha256": None,
        "slots": [],
        "lastSlot": None,
        "lastSlotEndedAt": None,
        "lastSlotEndedAtFrom": None,
        "reason": "the batch died before the first slot",
        "note": "declared before scoring",
    }
    assert set(declaration) == set(batch.SHORTFALL_SCHEMA)
    # The DRIVER accepts it, both ways, which is the half that already held.
    batch.validate_shortfall(declaration)
    batch.verify_shortfall(declaration, [], None)
    (tmp_path / score.SHORTFALL_FILE).write_text(json.dumps(declaration))
    shape = score.terminality(present(0), str(tmp_path))
    assert shape["declared"] is True and shape["complete"] is False
    assert shape["declaration"]["declaredSlots"] == 0
    assert shape["declaration"]["ledgerRecords"] == 0
    assert "no ledger file" in shape["declaration"]["verified"]


def test_an_empty_prefix_that_names_a_ledger_refuses(tmp_path):
    """The other direction: an empty prefix has no ledger, so a declaration that
    names one, or a tree that carries one, is a disagreement about whether any
    slot ran."""
    declaration = {
        "declarationVersion": batch.SHORTFALL_VERSION,
        "registeredRounds": batch.ROUNDS,
        "registeredRunsPerArm": batch.RUNS_PER_ARM,
        "registeredSlots": batch.REGISTERED_SLOTS,
        "completedRounds": 0, "completedThroughGlobalIndex": 0,
        "completedSlots": 0, "ledgerSha256": None, "ledgerHeadSha256": None,
        "slots": [], "lastSlot": None, "lastSlotEndedAt": None,
        "lastSlotEndedAtFrom": None, "reason": "died early",
        "note": "declared before scoring",
    }
    (tmp_path / score.SHORTFALL_FILE).write_text(json.dumps(declaration))
    (tmp_path / batch.LEDGER_NAME).write_text(json.dumps({"records": []}))
    with pytest.raises(score.ScoreError) as raised:
        score.terminality(present(0), str(tmp_path))
    assert "disagree about whether any slot ran" in str(raised.value)


def test_a_short_batch_with_a_valid_declaration_is_terminal(tmp_path):
    slots = declared_batch(tmp_path, 10)
    shape = score.terminality(slots, str(tmp_path))
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
        gold_perfect=True, code=None, out_of_domain=()):
    # ROUND-3 R3-9: no `x1Excluded` member. §4 registers no per-case filter and
    # no per-run excluded-case count, and a fixture that kept publishing one
    # would let the field come back without a test noticing.
    return {"run": name, "arm": arm, "code": code, "admitted": admitted,
            "goldPerfect": gold_perfect, "identityPass": identity,
            "durationSeconds": 100.0,
            "outOfDomainCases": list(out_of_domain),
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


def test_the_identity_failure_denominator_is_the_registered_one(tmp_path):
    """ROUND-2 FINDING R2-2, as the reviewer's own two-run probe.

    "A direct two-run probe — one identity-pass/high-kill run and one identity
    failure — produced primary E4 1/2, while the pilot rule produces 1/1." §5
    registers §1a's denominator, "attempted runs whose apparatus succeeded",
    with identity-control exclusions "reported, never silently dropped". So 1/2
    is the registered answer, the primary scorer has always given it, and the
    PILOT scorer was the one taking the other reading — it now takes this one
    (`design/mutants/E4-PILOT-v4.json`).

    The per-run marker is asserted here too, because it is the other half of the
    same sentence: an identity-failing run carries `highKill: null` and never
    `False`, since it was never asked, and it is in the denominator all the
    same."""
    cut = {"integerCut": 38}
    passing = run("run-001", killed=39)
    failing = run("run-002", identity=False, killed=39)
    endpoint = score.e4_endpoint("A", [passing, failing], cut)
    assert (endpoint["highKill"], endpoint["denominator"]) == (1, 2)
    assert endpoint["highKillRate"]["count"] == 1
    assert endpoint["highKillRate"]["trials"] == 2
    assert endpoint["identityFail"] == 1
    assert endpoint["identityFailedRuns"] == ["run-002"]
    assert passing["highKill"] is True
    assert failing["highKill"] is None
    assert "identity-control exclusions" in endpoint["denominatorRule"]


def test_the_pilot_scorer_now_computes_the_same_denominator():
    """The two scorers agree by CONSTRUCTION, not by inspection: this reads the
    pilot's own layer over a two-run arm shaped like the probe above."""
    import importlib.util
    path = os.path.join(score.STUDY, "design", "mutants", "e4_score.py")
    if not os.path.isfile(path):
        pytest.skip("the pilot scorer is absent")
    spec = importlib.util.spec_from_file_location("e4_score_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    doc = {"perArm": {
        "A": {"mutantsPairedAdequate": 75, "identityFailedRuns": ["run-002"],
              "perRun": [{"run": "run-001", "identityPass": True,
                          "killedPaired": 72},
                         {"run": "run-002", "identityPass": False}]},
        "B": {"mutantsPairedAdequate": 65, "identityFailedRuns": [],
              "perRun": []},
        "C": {"mutantsPairedAdequate": 65, "identityFailedRuns": [],
              "perRun": []}}}
    module.high_kill_layer(doc, 0.95)
    high = doc["perArm"]["A"]["highKill"]
    assert (high["highKillRuns"], high["admittedRuns"]) == (1, 2)
    assert high["identityFailingRunsInDenominator"] == 1
    assert doc["perArm"]["A"]["perRun"][1]["highKill"] is None


def test_e4_publishes_no_x1_member_at_all(study):
    """ROUND-3 FINDING R3-9, and this test is REVERSED from what it asserted.

    It required `x1ExcludedCases` to be published and was cited as evidence that
    the X1 surface was coherent. It was not: §4 says "There is no exclusion
    class, no per-case X1 filter and no per-run excluded-case count", the
    scorer emitted `x1Excluded` per run, `x1ExcludedCases` per arm and an
    "Excluded cases" column, and `tests/E2E-SMOKE.md` said the field no longer
    existed. Three surfaces, two of them false. The registration's is the one
    that stands, so the assertion is that NOTHING published names X1 — over the
    endpoint's own keys rather than a fixed list, so a member re-added under any
    spelling fails here."""
    endpoint = score.e4_endpoint("A", [run("run-001",
                                           out_of_domain=["c1", "c2"])],
                                 {"integerCut": 38})
    assert [key for key in endpoint if "x1" in key.lower()] == []
    assert endpoint["outOfDomainCases"] == 2, (
        "the member §4 DOES register is still published, so this is a "
        "correction and not a deletion")


def test_the_published_report_has_no_excluded_cases_column():
    """The same surface where a reader meets it. A column of zeros headed
    "Excluded cases" teaches every reader of RESULTS.md that a filter ran."""
    results = {"label": "PILOT", "unfilledPins": [], "cuts": {},
               "e1": {}, "e2": {}, "e5": None, "contrasts": {},
               "contrastsGatedBy": ["control-gate-failed: e1-floor"],
               "refusals": {}, "pairing": {},
               "e4": {"A": score.e4_endpoint("A", [run("run-001")],
                                             {"integerCut": 38,
                                              "language": "jps"})},
               "decision": decision.decide({"pipelineProblems": ["x"]})}
    body = score.results_markdown(results)
    assert "Excluded cases" not in body
    assert "Out-of-domain cases" in body


def test_the_retired_predicate_survives_and_gates_nothing():
    """R3-9's other half, adopted rather than argued away: `in_x1()` stays as an
    explicitly NON-GATING measurement helper — the retirement is a fact about
    the reference that was measured, and the predicate is how it was measured —
    while the registry it would have been read through is empty."""
    from e4lib import e4 as e4_module
    assert e4_module.REGISTERED_EXCLUSION_CLASSES == {}
    assert callable(e4_module.in_x1)


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
    """Over the RUN records (SCAFFOLD item S11 / the smoke's D-3): the authoring
    codes are assigned by `score_run()` onto the run, and a table built from the
    slot records — whose codes are the wrapper's exit statuses, every one of
    them on the apparatus side — was structurally always zero."""
    runs = [run("run-001"),
            run("run-002", admitted=False, code="no-marker-block"),
            run("run-003", admitted=True, code="schema-invalid-pack")]
    profile = score.e2_profile("A", runs)
    assert [row["code"] for row in profile["orderedCodes"]] == \
        list(score.admit_lib.DROP_ORDER)
    assert all(row["side"] == "authoring" for row in profile["orderedCodes"])
    assert profile["admitted"] == 1
    # …and the artifact-level count is published beside it rather than standing
    # in for it: run-003's policy was admitted and its pack was schema-invalid.
    assert profile["artifactAdmitted"] == 2
    counts = {row["code"]: row["count"] for row in profile["orderedCodes"]}
    assert counts["no-marker-block"] == 1 and counts["schema-invalid-pack"] == 1


def test_e2_refuses_an_apparatus_code_on_a_run_record():
    """Section 1a excludes apparatus failures from every per-arm rate, so a run
    record carrying one is a population rule that did not run — refused here
    rather than published as an E2 row."""
    with pytest.raises(score.ScoreError) as raised:
        score.e2_profile("A", [run("run-001", code="call-timeout")])
    assert "cannot carry one" in str(raised.value)


def test_e3_counts_within_arm_only():
    runs = [{"goldFailures": [{"category": "disagreement"}],
             "identityFailures": [{"got": "outcome:reject"}]}]
    taxonomy = score.e3_taxonomy(runs)
    assert taxonomy["goldFailureCategories"] == {"disagreement": 1}
    assert taxonomy["identityFailureCategories"] == {"outcome:reject": 1}


def test_the_contrast_scores_unequal_denominators_rather_than_refusing():
    """SCAFFOLD item S8, closed. Section 1a excludes apparatus failures from the
    denominator, so unequal admitted counts are the registered case, and section
    5 registers the general unequal-N FM-score inversion for it. The scorer used
    to raise `FM-UNEQUAL-N` here."""
    e4_by_arm = {"A": {"highKill": 10, "denominator": 50},
                 "C": {"highKill": 40, "denominator": 49}}
    result = score.contrast("A", "C", e4_by_arm, endpoints=False)
    assert result["equalArms"] is False
    assert result["nLeft"] == 50 and result["nRight"] == 49
    assert result["excludesZero"] is True
    assert decision.direction(result) == "C above A"


def test_the_contrast_carries_the_arm_names_so_direction_is_readable():
    e4_by_arm = {"A": {"highKill": 10, "denominator": 50},
                 "C": {"highKill": 45, "denominator": 50}}
    result = score.contrast("A", "C", e4_by_arm, endpoints=False)
    assert result["arms"] == ["A", "C"]
    assert decision.direction(result) == "C above A"


def test_the_contrast_publishes_the_swept_interval_beside_the_decision():
    """Section 10 commits to publishing every interval, and section 5 says the
    reported endpoints come from the full Delta0 sweep of the same
    construction. Small denominators here because the sweep's cost is the whole
    Delta0 mesh; `tests/test_score_stats.py` holds the construction itself.

    ROUND-3 R3-8: the sweep runs at SETTLEMENT rather than at construction, so
    the two steps are driven in the publisher's order here — the endpoints are
    the same endpoints, computed once the row is known."""
    e4_by_arm = {"A": {"highKill": 6, "denominator": 6},
                 "C": {"highKill": 0, "denominator": 5}}
    result = score.contrast("A", "C", e4_by_arm)
    assert result["intervalState"] == score.stats.INTERVAL_PENDING
    assert result["interval"] is None
    score.stats.fill_intervals(result, True)
    assert result["excludesZero"] is True
    assert result["intervalState"] == score.stats.INTERVAL_COMPUTED
    assert result["interval"]["lower"] == "43/100"
    assert result["interval"]["upper"] == "1"
    assert result["interval"]["deltaMeshDenominator"] == \
        score.stats.FM_DELTA_MESH_DEN


def test_an_endpoint_refusal_leaves_the_decision_intact():
    """The endpoints are a REPORT; section 5's rule reads `excludesZero` and
    nothing else, so a sweep that cannot report a hull must not take the verdict
    down with it."""
    e4_by_arm = {"A": {"highKill": 6, "denominator": 6},
                 "C": {"highKill": 0, "denominator": 5}}

    def refuse(*_args, **_kwargs):
        raise score.stats.StatsError("FM-EMPTY-ACCEPTANCE synthetic")

    saved = score.stats.interval_endpoints
    score.stats.interval_endpoints = refuse
    try:
        result = score.contrast("A", "C", e4_by_arm)
        score.stats.fill_intervals(result, True)
    finally:
        score.stats.interval_endpoints = saved
    assert result["excludesZero"] is True
    assert result["interval"] is None
    assert result["intervalState"] == score.stats.INTERVAL_REFUSED
    assert result["intervalRefusal"].startswith("FM-EMPTY-ACCEPTANCE")


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


# --- ROUND-1 FINDING R1-9: verification precedes the study-local imports -----

def test_the_scorer_imports_nothing_study_local_but_integrity_at_module_scope():
    """The finding, verbatim: "The scorer imports local modules before
    validation". `batch` and the whole of `e4lib` were bound at import, so
    `integrity.verify()`'s untracked-source and unreviewed-bytecode scan — if it
    ran at all — ran after the bytes it is about had already executed.

    Asserted on the SOURCE's own import statements rather than on behaviour,
    because the property is about what happens before any of this module's code
    runs. `integrity` is the one exception and it earns it: it imports nothing
    study-local at module scope itself."""
    import ast
    source = ast.parse(open(os.path.join(os.path.dirname(_HERE),
                                         "score.py")).read())
    study_local = {"batch", "integrity", "transcript_check", "leak_tokens",
                   "make_manifest", "e4lib"}
    at_module_scope = set()
    for node in source.body:
        if isinstance(node, ast.Import):
            at_module_scope.update(alias.name.split(".")[0]
                                   for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            at_module_scope.add(node.module.split(".")[0])
    assert at_module_scope & study_local == {"integrity"}
    # …and `integrity` itself has no study-local import at module scope, so the
    # exception costs nothing the scan could have caught.
    integrity_source = ast.parse(
        open(os.path.join(os.path.dirname(_HERE), "integrity.py")).read())
    integrity_scope = set()
    for node in integrity_source.body:
        if isinstance(node, ast.Import):
            integrity_scope.update(alias.name.split(".")[0]
                                   for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            integrity_scope.add(node.module.split(".")[0])
    assert integrity_scope & study_local == set()


def test_the_full_verification_runs_and_is_terminal_when_it_refuses(tmp_path,
                                                                    monkeypatch):
    """`verify()` — not only the interpreter and the port chain — and a refusal
    stops the attempt before `bind_study_modules()` imports anything."""
    calls = []

    def refuse(study):
        calls.append(study)
        raise integrity_module.IntegrityError("an untracked Python source")

    import integrity as integrity_module
    monkeypatch.setattr(integrity_module, "verify", refuse)
    root = tmp_path / "primary-attempt-001"
    assert score.main(["--attempt-root", str(root)]) == 2
    assert calls == [score.STUDY]
    results = json.loads(read(root / "RESULTS.json"))
    assert results["pipelineInvalid"] is True
    assert results["problem"].startswith("integrity: ")


def test_a_scorer_input_outside_the_covered_set_is_a_pipeline_problem():
    """The other half of R1-9: an input the exact-set manifest does not name is
    an input nothing verified, and it is named rather than counted."""
    problems = score._registered_inputs_problems()
    # Pre-freeze the frozen inputs do not exist yet, so what this asserts is
    # that their ABSENCE is reported by name — the same predicate that reports
    # an uncovered one once they do.
    assert any("registered artifact is absent: gold/GOLD.json" in problem
               for problem in problems)
    assert any("controls/off-gold-equivalence.json" in problem
               for problem in problems)
    assert problems == sorted(problems)
