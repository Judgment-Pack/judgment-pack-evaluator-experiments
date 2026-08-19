"""`design/mutants/regenerate.py` — the reproducibility command's own guards.

ROUND-2 FINDING R2-11, both halves, each with the regression the finding asked
for.

**The closure check read the wrong root.** `--check` regenerates into a scratch
copy and byte-compares, and then called `undispositioned(DESIGN)` — the
COMMITTED tree. The fail-closed condition therefore described bytes the run had
not produced. The reviewer stated the consequence exactly: *once the committed
tree happens to be green, a newly generated empty-witness mutant can evade the
supposed fail-closed check.* `test_a_scratch_only_empty_witness_mutant_fails_the_check`
builds that situation — a green committed tree, a scratch tree the chain gives
one undispositioned empty-witness mutant — and requires the run to name them.
Run against the pre-fix code it reports **zero** undispositioned mutants in both
arms while two exist in the tree the run built, which is the evasion itself and
is what makes this a regression rather than a restatement. The assertion that
does the work is therefore on the reported LIST, not on the exit status: the
exit status is also red there, but only because the fixture's bytes moved.

**A single-arm record was committed and read as the complete check.** The
committed `REGENERATION-CHECK.json` covered arm B only, with `pass: false`, while
the round-1 disposition described a complete passing check. `pass` now requires
both arms, the record stamps which arms it covers, and `--check` refuses to write
the committed record for a single arm at all.

These tests never run the real generators: `run_chain` is the seam, and standing
it in is what lets the closure logic be exercised in milliseconds against a tree
built for the purpose. What the real chain does is the byte-comparison's job and
is recorded in `design/mutants/REGENERATION-CHECK.json`.
"""
import importlib.util
import json
import os
import sys

import pytest


def _load_by_path(name, path):
    """Import a `design/` script without leaving a `__pycache__` behind.

    `integrity.verify_bytecode()` refuses stale bytecode caches, and a test that
    manufactures one under `design/mutants/` would hand the scorer a refusal it
    did not earn. Loading with bytecode writing suppressed keeps the tree the
    integrity scan sees exactly as the freeze will see it."""
    written = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = written


def _study():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


@pytest.fixture()
def regen():
    """The module under test, loaded by path — `design/` is not importable."""
    path = os.path.join(_study(), "design", "mutants", "regenerate.py")
    return _load_by_path("_s019_regenerate", path)


def _write(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, sort_keys=True)
        handle.write("\n")


def _fake_design(root, undispositioned_a=(), undispositioned_b=()):
    """A minimal design tree of the shape `regenerate.py` reads and compares.

    Arm A's manifest is a bare list, arm B's is an object under `mutants` —
    the two real shapes, because `undispositioned()` reads them differently and
    a fixture that flattened them would test a tree the command never sees.
    """
    mutants = os.path.join(root, "mutants")
    _write(os.path.join(mutants, "adequacy_engine_supplied.json"), {"records": []})

    def record(identifier, undispositioned):
        entry = {"id": identifier, "notAdequate": True}
        if not undispositioned:
            entry["adequacy"] = {"disposition": "dropped", "mechanism": "fixture"}
        return entry

    arm_a = [record("m-a-001", False)]
    arm_a += [record(i, True) for i in undispositioned_a]
    _write(os.path.join(mutants, "refA", "MANIFEST.json"), arm_a)
    _write(os.path.join(mutants, "refA", "REGISTRY.json"), {"conflictOnlyMutants": []})
    _write(os.path.join(mutants, "refA", "m-a-001.json"), {"id": "m-a-001"})

    arm_b = [record("m-b-001", False)]
    arm_b += [record(i, True) for i in undispositioned_b]
    _write(os.path.join(mutants, "refB", "MANIFEST.json"), {"mutants": arm_b})
    with open(os.path.join(mutants, "refB", "m-b-001.rego"), "w",
              encoding="utf-8") as handle:
        handle.write("package study\n")
    return root


# --- the closure check reads the tree the run produced ----------------------

def test_undispositioned_reads_the_root_it_is_given(regen, tmp_path):
    """The unit property the `--check` path depends on. Two trees, different
    closures; the function must answer about the one it is handed."""
    committed = _fake_design(str(tmp_path / "committed"))
    scratch = _fake_design(str(tmp_path / "scratch"),
                           undispositioned_a=["m-a-777"],
                           undispositioned_b=["m-b-888"])
    assert regen.undispositioned(committed) == {"A": [], "B": []}
    assert regen.undispositioned(scratch) == {"A": ["m-a-777"], "B": ["m-b-888"]}


def test_a_scratch_only_empty_witness_mutant_fails_the_check(regen, tmp_path,
                                                             monkeypatch):
    """R2-11's named scenario, end to end through `main()`.

    The committed tree is GREEN — every empty-witness mutant dispositioned — so
    the pre-fix `undispositioned(DESIGN)` would have reported nothing and stamped
    `pass: true`. The stand-in chain gives the SCRATCH tree one undispositioned
    empty-witness mutant per arm, exactly as a newly generated corpus could. The
    run must fail closed and name them.
    """
    design = _fake_design(str(tmp_path / "design"))
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    monkeypatch.setattr(regen, "DESIGN", design)
    monkeypatch.setattr(regen, "HERE", str(report_dir))
    monkeypatch.setattr(regen, "COPY_TREES", ["mutants"])

    def chain(arm, root, jobs, env):
        """Stands in for the generators: emits one empty-witness mutant that
        exists only in the regenerated tree."""
        if arm == "A":
            path = os.path.join(root, "mutants", "refA", "MANIFEST.json")
            records = json.load(open(path, encoding="utf-8"))
            records.append({"id": "m-a-999", "notAdequate": True})
            _write(path, records)
        else:
            path = os.path.join(root, "mutants", "refB", "MANIFEST.json")
            payload = json.load(open(path, encoding="utf-8"))
            payload["mutants"].append({"id": "m-b-999", "notAdequate": True})
            _write(path, payload)

    monkeypatch.setattr(regen, "run_chain", chain)
    monkeypatch.setattr("sys.argv", ["regenerate.py", "--arm", "both", "--check"])

    assert regen.main() == 1, (
        "a scratch-only empty-witness mutant must fail the check; reading the "
        "committed tree's closure is R2-11")
    written = json.load(open(os.path.join(str(report_dir),
                                          "REGENERATION-CHECK.json"),
                             encoding="utf-8"))
    assert written["undispositionedEmptyWitnessMutants"] == {"A": ["m-a-999"],
                                                             "B": ["m-b-999"]}
    assert written["adequacyStampPresent"] == {"A": False, "B": False}
    assert written["pass"] is False
    assert written["closureEvaluatedUnder"] == "regenerated scratch tree"


# --- a record must speak for both arms --------------------------------------

def test_a_single_arm_report_can_never_pass(regen):
    """The committed record was arm B only and was read as the whole check."""
    rows = [{"arm": "B", "path": "mutants/refB/MANIFEST.json", "identical": True}]
    report = regen.build_report(["B"], rows, {"B": []})
    assert report["byteIdentical"] is True, "arm B did reproduce"
    assert report["coversBothArms"] is False
    assert report["armsCovered"] == {"A": False, "B": True}
    assert report["pass"] is False, (
        "reproduction on one arm is not the regeneration claim")


def test_both_arms_reproduced_and_closed_is_the_only_passing_shape(regen):
    rows = [{"arm": "A", "path": "a", "identical": True},
            {"arm": "B", "path": "b", "identical": True}]
    assert regen.build_report(["A", "B"], rows, {"A": [], "B": []})["pass"] is True
    assert regen.build_report(["A", "B"], rows,
                              {"A": ["m-a-1"], "B": []})["pass"] is False
    differing = rows[:1] + [{"arm": "B", "path": "b", "identical": False}]
    assert regen.build_report(["A", "B"], differing,
                              {"A": [], "B": []})["pass"] is False


def test_a_single_arm_check_does_not_write_the_committed_record(regen, tmp_path,
                                                                monkeypatch):
    """The stronger half of the same rule: a partial record cannot reach the
    tree at all, so nobody can read one as complete again."""
    design = _fake_design(str(tmp_path / "design"))
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    monkeypatch.setattr(regen, "DESIGN", design)
    monkeypatch.setattr(regen, "HERE", str(report_dir))
    monkeypatch.setattr(regen, "COPY_TREES", ["mutants"])
    monkeypatch.setattr(regen, "run_chain", lambda *a, **k: None)
    monkeypatch.setattr("sys.argv", ["regenerate.py", "--arm", "B", "--check"])
    regen.main()
    assert not os.path.exists(os.path.join(str(report_dir),
                                           "REGENERATION-CHECK.json"))


# --- the committed record is the one this study cites ------------------------

def test_the_committed_record_covers_both_arms_and_states_its_closure_root():
    """The artifact itself, not the code. Round 2 read a B-only record; whatever
    the adequacy gate's state, the committed record must at least cover both
    arms and say which tree its closure was evaluated under."""
    path = os.path.join(_study(), "design", "mutants", "REGENERATION-CHECK.json")
    record = json.load(open(path, encoding="utf-8"))
    assert record["coversBothArms"] is True, (
        "the committed regeneration record is partial")
    assert record["armsCovered"] == {"A": True, "B": True}
    assert record["closureEvaluatedUnder"] == "regenerated scratch tree"
    assert record["byteIdentical"] is True, (
        "the reproducibility claim is `byteIdentical`, and it is red")
