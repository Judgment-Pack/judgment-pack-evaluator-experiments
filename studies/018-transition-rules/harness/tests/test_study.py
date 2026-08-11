"""Study-level integrity: pins, vocabulary sync, pair machinery, determinism."""

import dataclasses
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import build_fixtures
import run_verify
import score
import upstream016
import transition

STUDY = Path(__file__).resolve().parent.parent.parent


def test_study016_sources_match_their_pins():
    assert upstream016.problems() == []


def test_matrix_schema_and_frozen_id_set():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.matrix_schema_problems(matrix) == []


def test_pins_registry_is_consistent():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    values = {m: (pins.get(m) or {}).get("sha256") for m in score.FREEZE_PINS}
    if any(v is None for v in values.values()):
        assert all(v is None for v in values.values()), values
    else:
        for member, relative in score.PINNED_DIGEST_MEMBERS:
            assert values[member] == score.sha256_file(STUDY / relative), member
    assert pins["harnessPython"]["version"] == "3.12.11"


def test_fixture_manifests_verify():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cell["id"])
        assert directory.is_dir(), cell["id"]
        assert run_verify.manifest_problems(directory) == [], cell["id"]
        assert run_verify.required_file_problems(directory, cell) == [], cell["id"]


def test_no_bytecode_caches_shadow_pinned_source():
    """Round-1 R1-1: a .py digest does not describe what ran if a divergent
    cache is loaded instead; an equivalent cache is accepted."""
    assert score.bytecode_cache_problems() == []


def test_registered_dependencies_are_enforced():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    assert score.dependency_problems(pins) == []
    broken = json.loads(json.dumps(pins))
    broken["dependencies"]["versions"]["rfc8785"] = "0.0.0-not-installed"
    assert score.dependency_problems(broken) != []


def test_upstream_pins_are_bound_from_stamped_bytes():
    """Round-1 R1-3: the loader uses the mapping the attempt stamps."""
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    bound = upstream016.bind_pins(pins["study016"]["files"])
    assert bound == pins["study016"]["files"]
    with pytest.raises(upstream016.Upstream016Error):
        upstream016.bind_pins({"registry/verify_currency.py": "0" * 64})


def test_study_manifest_is_fresh():
    import make_manifest
    assert make_manifest.verify_problems() == []


def test_rebuild_is_deterministic_and_matches_committed_bytes(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "build_fixtures.py"),
         "--out", str(tmp_path / "fixtures")],
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    committed = STUDY / "fixtures" / "cells"
    rebuilt = tmp_path / "fixtures" / "cells"
    committed_files = sorted(p.relative_to(committed).as_posix()
                             for p in committed.rglob("*") if p.is_file())
    rebuilt_files = sorted(p.relative_to(rebuilt).as_posix()
                           for p in rebuilt.rglob("*") if p.is_file())
    assert committed_files == rebuilt_files
    for relative in committed_files:
        assert (committed / relative).read_bytes() == (rebuilt / relative).read_bytes(), relative


def test_scorer_is_deterministic_and_control_gates_hold(tmp_path):
    outputs = []
    for name in ("attempt-a", "attempt-b"):
        completed = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "score.py"),
             "--attempt-root", str(tmp_path / name)],
            capture_output=True, text=True,
        )
        assert completed.returncode == 0, completed.stderr
        raw = (tmp_path / name / "RESULTS.json").read_text(encoding="utf-8")
        outputs.append(raw.replace(name, "attempt-x"))
        results = json.loads(raw)
        assert results["pipelineInvalid"] is False
        pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
        frozen = all((pins.get(m) or {}).get("sha256") is not None
                     for m in score.FREEZE_PINS)
        assert results["label"] == ("REGISTERED" if frozen else "PILOT")
        for cid, record in results["cells"].items():
            if record["role"] == "control-gate":
                assert record["adjudicated"] and not record["divergent"], cid
    assert outputs[0] == outputs[1]


def test_scorer_refuses_existing_attempt_root(tmp_path):
    root = tmp_path / "occupied"
    root.mkdir()
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "score.py"),
         "--attempt-root", str(root)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 2
    assert "already exists" in completed.stderr


def test_holdout_refused_while_freeze_pins_null(tmp_path, monkeypatch):
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    for member in score.FREEZE_PINS:
        pins.setdefault(member, {})["sha256"] = None
    nulled = tmp_path / "PINS.json"
    nulled.write_text(json.dumps(pins, indent=2), encoding="utf-8")
    monkeypatch.setattr(score, "PINS_PATH", nulled)
    root = tmp_path / "holdout-early"
    assert score.main(["--attempt-root", str(root), "--include-holdout"]) == 2
    results = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
    assert results["pipelineInvalid"] is True
    assert "refused" in results["problem"]
    marker = json.loads((root / "ATTEMPT.json").read_text(encoding="utf-8"))
    assert marker["pinsRawSha256"] == results["pinsRawSha256"]
    assert marker["pinsRawSha256"] is not None


def test_scorer_records_attempt_before_pins_parse(tmp_path, monkeypatch):
    root = tmp_path / "marker"
    broken = tmp_path / "PINS.json"
    broken.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(score, "PINS_PATH", broken)
    with pytest.raises(BaseException):
        score.main(["--attempt-root", str(root)])
    assert (root / "ATTEMPT.json").is_file()
    assert (root / "RESULTS.json").is_file()


def test_spec_vocabulary_matches_the_evaluator():
    """rule/SPEC.md section 4 is the governing table."""
    spec = (STUDY / "rule" / "SPEC.md").read_text(encoding="utf-8")
    table = re.findall(r"^\| `([a-z0-9-]+)` \|", spec, flags=re.MULTILINE)
    assert sorted(table) == sorted(transition.CODES)


def test_matrix_expectations_use_only_registered_outcomes():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    ns = upstream016.load()
    for cell in matrix["cells"]:
        for layer, expected in cell["expected"].items():
            if expected in ("pass", "usable", "unavailable"):
                continue
            head, _, code = expected.partition(":")
            assert code, cell["id"]
            if layer == "transition":
                assert head == "not-usable" and code in transition.CODES, cell["id"]
            else:
                assert head == "fail" and code in ns.verify_currency.CODES, cell["id"]


def test_the_registered_divergence_is_real():
    """The study's positive result, asserted structurally: the four div-* cells
    share commitment, snapshot and trust configuration, and differ only in the
    rule configuration — so their differing outcomes are the rule's doing."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in matrix["cells"] if c["id"].startswith("div-")]
    assert len(ids) == 4
    # Round-1 R1-12: assert the EXACT difference set, citation included.
    shared = {}
    for cid in ids:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        for name in build_fixtures.CELL_FILES:
            path = directory / name
            shared.setdefault(name, set()).add(
                score.sha256_file(path) if path.is_file() else None)
    differing = {name for name, digests in shared.items() if len(digests) > 1}
    assert differing == {"ruleconfig.json"}, differing
    assert len(shared["ruleconfig.json"]) == 4


def test_backdated_citation_is_byte_identical_to_the_honest_cell():
    """The boundary exhibit: identical bytes, so no rule over this evidence can
    separate honest reliance from a chosen-early citation."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.identity_group_problems(matrix) == {}
    a = build_fixtures.cell_directory(STUDY / "fixtures", "div-grandfather-on-cited-support")
    b = build_fixtures.cell_directory(STUDY / "fixtures", "bnd-backdated-citation")
    for name in build_fixtures.CELL_FILES:
        assert (a / name).is_file() == (b / name).is_file(), name
        if (a / name).is_file():
            assert (a / name).read_bytes() == (b / name).read_bytes(), name


def test_holdout_machinery_lands_with_the_reviewer_cells():
    """The round-2 reviewer's cells and their construction machinery land
    together and are NEVER executed before the freeze (the 014/016/017 regime).

    This test asserts everything about the stratum that can be checked without
    constructing a single byte: every registered cell has a hook, every hook
    refuses outside a valid post-freeze context, and every cell carries exactly
    this study's structured-evidence fields. Whether a hook builds what its
    construction text says is adjudicated by the first execution — which is the
    whole of what the stratum is for — and a hook that fails there is recorded
    as `harness-error`, not silently dropped.
    """
    import score
    holdout = json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8"))
    assert holdout["reviewer"], "the stratum must carry its reviewer attribution"
    ids = [cell["id"] for cell in holdout["cells"]]
    assert ids == ["h%02d" % n for n in range(1, 11)]
    assert not score.holdout_schema_problems(holdout)

    # every cell is constructible in principle, and nothing is constructible now
    assert set(build_fixtures.HOLDOUT_HOOKS) == set(ids)
    for cell_id in ids:
        with pytest.raises(build_fixtures.HoldoutRefused):
            build_fixtures.HOLDOUT_HOOKS[cell_id](None)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(None, STUDY / "fixtures", holdout["cells"])

    # the structured expectations are complete, separate, and this study's
    evidence = score.holdout_evidence_expectations()
    assert not score.holdout_evidence_problems(holdout, evidence)
    assert set(evidence) == set(ids)
    for cell in holdout["cells"]:
        assert set(cell["expected"]) == {"currency", "transition"}
        assert "expectedRuleEvidence" not in cell, (
            "structured expectations belong in MATRIX-HOLDOUT-EVIDENCE.json so the "
            "reviewer's block stays byte-for-byte as authored")


def test_holdout_construction_is_gated_on_every_freeze_pin(tmp_path, monkeypatch):
    """The stratum executes only after the freeze. Each pin is nulled in turn —
    in a temporary registry, so this holds identically before and after the
    freeze — and the gate must refuse naming that pin. A gate that omits one of
    the pins it added is the 017 round-2 class of defect.
    """
    import hashlib

    def sha256_file(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    real = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    filled = {"sha256": "f" * 64}
    for member in score.FREEZE_PINS:
        assert member in real, "a freeze pin the gate names is missing from PINS.json"

    def context_for(pins):
        raw = (json.dumps(pins, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        pins_path = tmp_path / "PINS.json"
        pins_path.write_bytes(raw)
        monkeypatch.setattr(build_fixtures, "PINS_PATH", pins_path)
        return build_fixtures.HoldoutAttemptContext(
            attempt_root=str(tmp_path),
            pins_raw_sha256=hashlib.sha256(raw).hexdigest(),
            preregistration_sha256=sha256_file(STUDY / "PREREGISTRATION.md"),
            matrix_holdout_sha256=sha256_file(STUDY / "harness" / "MATRIX-HOLDOUT.json"),
            matrix_holdout_evidence_sha256=sha256_file(
                STUDY / "harness" / "MATRIX-HOLDOUT-EVIDENCE.json"))

    # all six filled: the gate has nothing to say about the pins
    everything = dict(real, **{member: filled for member in score.FREEZE_PINS})
    assert not build_fixtures.holdout_context_problems(context_for(everything))

    for member in score.FREEZE_PINS:
        one_null = dict(everything, **{member: {"sha256": None}})
        problems = build_fixtures.holdout_context_problems(context_for(one_null))
        assert any(member in problem for problem in problems), (
            "the gate does not refuse while %s is null" % member)

    # a context whose digests disagree with the live files is refused
    for field in ("pins_raw_sha256", "preregistration_sha256",
                  "matrix_holdout_sha256", "matrix_holdout_evidence_sha256"):
        context = context_for(everything)
        tampered = dataclasses.replace(context, **{field: "0" * 64})
        assert build_fixtures.holdout_context_problems(tampered)


def test_transition_refuses_over_an_unauthenticated_snapshot():
    """Round-1 R1-1: a rule is evaluated only over an authenticated membership
    answer, and the composed verdict can never be usable without one."""
    import transition
    directory = build_fixtures.cell_directory(STUDY / "fixtures",
                                              "neg-currency-unauthenticated")
    outcome = run_verify.verify_cell(directory)
    assert outcome["currency"]["outcome"].startswith("fail:snapshot-")
    assert outcome["transition"]["outcome"] == "unavailable"
    assert outcome["combined"] != "usable"
    for bad in ("unavailable", "fail:snapshot-signature-invalid", "fail:binding-rebound"):
        assert bad not in transition.ADJUDICABLE_CURRENCY


def test_membership_comes_from_the_pinned_upstream_fold():
    """Round-1 R1-2: lifecycle semantics are the upstream's by construction.

    2.0.0 is retired at position 4 and reinstated at 5, and a never-bound
    digest must never be supported at any position — the two cases the
    hand-rolled tracker got wrong.
    """
    import transition
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key("study-018/currency-authority/1")
    history = registry.build_registry(authority, [
        build_fixtures.event("add", "1.0.0", build_fixtures.DIGEST_A),
        build_fixtures.event("add", "2.0.0", build_fixtures.DIGEST_B),
        build_fixtures.event("retire", "1.0.0"),
        build_fixtures.event("retire", "2.0.0"),
        build_fixtures.event("reinstate", "2.0.0")])
    payloads = [record["checkpoint"] for record in history]
    fold = ns.verify_currency.fold_supported
    series = build_fixtures.SERIES_ID
    real = ("2.0.0", build_fixtures.DIGEST_B)
    never_bound = ("2.0.0", "sha256:" + "b" * 64)
    assert transition._supported_at(payloads, series, real, 2, fold) is True
    assert transition._supported_at(payloads, series, real, 4, fold) is False
    assert transition._supported_at(payloads, series, real, 5, fold) is True
    for position in range(1, 6):
        assert transition._supported_at(payloads, series, never_bound, position, fold) is False
    assert transition._left_position(payloads, series, real, fold) == 4
