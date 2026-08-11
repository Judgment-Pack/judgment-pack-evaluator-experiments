"""Study-level integrity: pins, vocabulary sync, pair machinery, determinism."""

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
import verify_witness

STUDY = Path(__file__).resolve().parent.parent.parent


def test_study016_sources_match_their_pins():
    assert upstream016.problems() == []


def test_shared_names_resolve_to_the_right_study():
    upstream016.load(build=True)
    resolved = {
        name: Path(importlib.util.find_spec(name).origin).resolve()
        for name in ("score", "build_fixtures", "run_verify", "verify_witness",
                     "sighting", "verify_currency", "checkpoint")
    }
    for name in ("score", "build_fixtures", "run_verify", "verify_witness", "sighting"):
        assert STUDY in resolved[name].parents, name
    for name in ("verify_currency", "checkpoint"):
        assert upstream016.STUDY_016 in resolved[name].parents, name


def test_spec_table_matches_declared_codes():
    spec = (STUDY / "witness" / "SPEC.md").read_text(encoding="utf-8")
    table = re.findall(r"^\| `([a-z0-9-]+)` \|", spec, flags=re.MULTILINE)
    assert sorted(table) == sorted(verify_witness.CODES)


def test_matrix_expectations_use_only_registered_outcomes():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    ns = upstream016.load()
    for cell in matrix["cells"]:
        for layer, expected in cell["expected"].items():
            if expected in ("pass", "unavailable"):
                continue
            assert expected.startswith("fail:"), cell["id"]
            code = expected.split(":", 1)[1]
            if layer == "witness":
                assert code in verify_witness.CODES, cell["id"]
            else:
                assert code in ns.verify_currency.CODES, cell["id"]


def test_matrix_schema_and_frozen_id_set():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.matrix_schema_problems(matrix) == []


def test_registered_undetected_cells_expect_all_pass():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    flagged = {c["id"]: c for c in matrix["cells"] if c.get("registeredUndetected")}
    assert sorted(flagged) == [
        "wit-collusion-a", "wit-collusion-b", "wit-historical-audit",
        "wit-prefix-coverage", "wit-suppression-corrupted",
        "wit-suppression-omitted", "wit-zero-sightings-vacuous",
    ]
    for cell in flagged.values():
        assert cell["role"] == "endpoint", cell["id"]
        assert all(v == "pass" for v in cell["expected"].values()), cell["id"]


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


def test_collusion_pair_structure_is_validated_from_bytes():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    structure = score._collusion_structure(matrix["pairs"]["collusion"], pins)
    assert structure["validated"] is True
    assert structure["checks"] == {
        "oneRecordFromTheSameKeyInEachCell": True,
        "bothSightingsVerifyUnderThatKey": True,
        "keyPinnedInBothConfigurations": True,
        "bothSatisfyTheEnforcementFloor": True,
        "eachHeadMatchesItsOwnPresentedView": True,
        "samePosition": True, "differentHeads": True,
    }


def test_no_bytecode_caches_shadow_pinned_source():
    """Round-1 R1-1: a .py digest does not describe what ran if a cache is
    loaded instead, so the scorer refuses while any cache exists."""
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
