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
        "sameSeriesAcrossCells": True,
        "oneRecordFromTheSameKeyInEachCell": True,
        "bothSightingsVerifyUnderThatKey": True,
        "keyPinnedInBothConfigurations": True,
        "bothSatisfyTheEnforcementFloor": True,
        "eachHeadMatchesItsOwnPresentedView": True,
        "samePosition": True, "differentHeads": True,
    }


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


def test_holdout_evidence_expectations_cover_every_cell():
    """Round-3 R3-1: the reviewer's structured values are registered separately
    (their block stays byte-for-byte) and every cell has one."""
    holdout = json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8"))
    evidence = score.holdout_evidence_expectations()
    assert sorted(evidence) == sorted(c["id"] for c in holdout["cells"])
    for cid, fields in evidence.items():
        assert set(fields) == {"comparisonPerformed", "validSightings",
                               "unattributedSightings"}, cid
        assert isinstance(fields["comparisonPerformed"], bool), cid


def test_every_registered_seed_label_is_enforced(monkeypatch):
    """Round-3 residual of R1-13: mutate each registered label in turn."""
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    assert score.pin_problems(pins) == []
    for label in ("authoritySeedLabel", "witness1SeedLabel", "witness2SeedLabel",
                  "witness3SeedLabel"):
        broken = json.loads(json.dumps(pins))
        broken["witnessAuthority"][label] = "study-017/mutated/1"
        assert score.pin_problems(broken) != [], label


def test_foreign_series_record_satisfies_no_floor():
    """Round-3 residual of R2-1: the combined regression the reviewer asked for
    — a required witness's record for another series satisfies neither the
    count floor nor the named-witness floor, and is never compared."""
    import sighting as sg
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key(sg.AUTHORITY_SEED)
    w2 = registry.private_key(sg.WITNESS_2_SEED)
    records = registry.build_registry(authority, [{
        "event": "add", "seriesId": build_fixtures.SERIES_ID,
        "packVersion": "1.0.0", "packDigest": build_fixtures.DIGEST_A,
        "effectiveFrom": build_fixtures.T1}])
    snapshot = registry.snapshot_bytes(registry.snapshot_of(authority, records))
    foreign = sg.build_sighting(w2, registry.key_id(w2),
                                series_id=build_fixtures.OTHER_SERIES_ID,
                                head=records[0]["checkpointDigest"], position=1)
    commitment = json.loads(build_fixtures.commitment_bytes().decode("utf-8"))
    public = registry.public_key_b64(w2)
    import verify_witness as vw
    required = vw.layer_witness(commitment, snapshot, sg.witnessconfig_bytes(
        series_id=build_fixtures.SERIES_ID, witness_keys=[public],
        minimum_sightings=0, required_witnesses=[public]),
        sg.sightings_bytes([foreign]))
    assert (required["verdict"], required["code"]) == ("fail", "witness-required-absent")
    counted = vw.layer_witness(commitment, snapshot, sg.witnessconfig_bytes(
        series_id=build_fixtures.SERIES_ID, witness_keys=[public],
        minimum_sightings=1), sg.sightings_bytes([foreign]))
    assert (counted["verdict"], counted["code"]) == ("unavailable", "witness-unavailable")
    assert counted["validSightings"] == 0 and counted["comparisonPerformed"] is False


def test_holdout_registry_schema_and_hooks():
    """Pre-freeze this is all a test may touch: the stratum is never executed
    before the freeze, and the context gate below is what enforces that."""
    holdout = json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8"))
    assert score.holdout_schema_problems(holdout) == []
    assert sorted(c["id"] for c in holdout["cells"]) == sorted(build_fixtures.HOLDOUT_HOOKS)
    assert holdout["reviewer"].startswith("codex-cli")
    assert "control-gate" in [c["role"] for c in holdout["cells"]]


def test_holdout_construction_refuses_without_valid_context():
    """No context, or a forged one, refuses at EVERY exposed hook — the
    scorer's gate is not the only gate."""
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(None, STUDY / "nowhere", [])
    forged = build_fixtures.HoldoutAttemptContext(
        attempt_root=str(STUDY), pins_raw_sha256="0" * 64,
        preregistration_sha256="0" * 64, matrix_holdout_sha256="0" * 64,
        matrix_holdout_evidence_sha256="0" * 64)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(forged, STUDY / "nowhere", [])
    assert any("does not match" in p for p in build_fixtures.holdout_context_problems(forged))
    for hook in build_fixtures.HOLDOUT_HOOKS.values():
        with pytest.raises(build_fixtures.HoldoutRefused):
            hook(forged)


def test_every_freeze_pin_individually_gates_the_holdout(tmp_path, monkeypatch):
    """Round-4 R4-1: one null pin at a time — each must refuse the stratum."""
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    for member in score.FREEZE_PINS:
        filled = json.loads(json.dumps(pins))
        for other in score.FREEZE_PINS:
            filled.setdefault(other, {})["sha256"] = "0" * 64
        filled[member]["sha256"] = None
        registry = tmp_path / (member + "-PINS.json")
        registry.write_text(json.dumps(filled, indent=2), encoding="utf-8")
        monkeypatch.setattr(score, "PINS_PATH", registry)
        root = tmp_path / ("attempt-" + member)
        assert score.main(["--attempt-root", str(root), "--include-holdout"]) == 2
        results = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
        assert results["pipelineInvalid"] is True
        assert member in results["problem"], member
    # and the builder's own gate refuses for the same reason
    problems = build_fixtures.holdout_context_problems(
        build_fixtures.HoldoutAttemptContext(
            attempt_root=str(STUDY), pins_raw_sha256="0" * 64,
            preregistration_sha256="0" * 64, matrix_holdout_sha256="0" * 64,
            matrix_holdout_evidence_sha256="0" * 64))
    assert any("matrixHoldoutEvidence" in problem for problem in problems)


def test_detection_matrix_publishes_the_evidence_column(tmp_path):
    """Round-4 R1-9: header and rows must agree, with the values rendered."""
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "score.py"),
         "--attempt-root", str(tmp_path / "matrix-shape")],
        capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    text = (tmp_path / "matrix-shape" / "DETECTION-MATRIX.md").read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| ") and "---" not in line]
    assert rows and all(row.count("|") == 7 for row in rows), "column shape"
    assert any("compared=" in row and "attributed=" in row for row in rows)


def test_no_holdout_bytes_under_fixtures():
    for cell_id in build_fixtures.HOLDOUT_HOOKS:
        assert not (STUDY / "fixtures" / "cells" / cell_id).exists()


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
