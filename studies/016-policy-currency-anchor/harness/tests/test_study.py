"""Study-level integrity: pins, vocabulary sync, identity groups, determinism.

The toolchain-dependent tests FAIL when `JPACK_BIN`/`OWP_SOURCE` are absent —
they never skip (014 convention: a suite that silently skips its determinism
checks reads as green while checking nothing).
"""

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
import upstream014
import verify_currency

STUDY = Path(__file__).resolve().parent.parent.parent


def test_study014_sources_match_their_pins():
    assert upstream014.problems() == []


def test_shared_names_resolve_to_the_right_study():
    upstream014.load(build=True)
    resolved = {
        name: Path(importlib.util.find_spec(name).origin).resolve()
        for name in ("score", "build_fixtures", "run_verify", "verify", "commitment",
                     "owpflow", "verify_currency", "checkpoint")
    }
    study014 = upstream014.STUDY_014
    for name in ("score", "build_fixtures", "run_verify"):
        assert STUDY in resolved[name].parents, name
    for name in ("verify", "commitment", "owpflow"):
        assert study014 in resolved[name].parents, name
    for name in ("verify_currency", "checkpoint"):
        assert STUDY in resolved[name].parents, name


def test_spec_table_matches_declared_codes():
    """registry/SPEC.md section 4 is the governing vocabulary; nothing drifts."""
    spec = (STUDY / "registry" / "SPEC.md").read_text(encoding="utf-8")
    table = re.findall(r"^\| `([a-z0-9-]+)` \|", spec, flags=re.MULTILINE)
    assert sorted(table) == sorted(verify_currency.CODES)


def test_matrix_expectations_use_only_registered_outcomes():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        for layer, expected in cell["expected"].items():
            if expected in ("pass", "unavailable"):
                continue
            if layer == "owp":
                assert expected == "fail", cell["id"]
                continue
            assert expected.startswith("fail:"), cell["id"]
            code = expected.split(":", 1)[1]
            if layer == "currency":
                assert code in verify_currency.CODES, cell["id"]


def test_matrix_schema_and_frozen_id_set():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.matrix_schema_problems(matrix) == []


def test_registered_undetected_cells_expect_all_pass():
    """D-3 as rescoped at round 1: one RU endpoint, one RU descriptive row."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    flagged = {c["id"]: c for c in matrix["cells"] if c.get("registeredUndetected")}
    assert sorted(flagged) == ["cur-split-view-a", "cur-workorder-remint-accepted"]
    assert flagged["cur-split-view-a"]["role"] == "endpoint"
    assert flagged["cur-workorder-remint-accepted"]["role"] == "descriptive"
    for cell in flagged.values():
        assert all(v == "pass" for v in cell["expected"].values()), cell["id"]


def test_pins_registry_is_consistent():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    for member in score.FREEZE_PINS:
        assert member in pins, member
        assert pins[member].get("sha256") is None, (
            "%s is already pinned in a DRAFT tree" % member
        )
    assert pins["jpack"]["version"] == "0.17.0"
    assert pins["harnessPython"]["version"] == "3.12.11"


def test_fixture_manifests_verify():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cell["id"])
        assert directory.is_dir(), cell["id"]
        assert run_verify.manifest_problems(directory) == [], cell["id"]
        assert run_verify.required_file_problems(directory, cell) == [], cell["id"]


def test_registered_identity_groups_hold():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.identity_group_problems(matrix) == {}


def test_vendored_packs_match_their_pins():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    for slot in ("v1", "v2"):
        pack = pins["packs"][slot]
        path = STUDY / pack["path"]
        assert score.sha256_file(path) == pack["sha256"], slot


def test_rebuild_is_deterministic_and_matches_committed_bytes(
    jpack_bin, owp_source, tmp_path
):
    """One rebuild, compared file-by-file against the committed fixtures."""
    import os
    environment = dict(os.environ, JPACK_BIN=jpack_bin, OWP_SOURCE=owp_source)
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "build_fixtures.py"),
         "--out", str(tmp_path / "fixtures")],
        capture_output=True, text=True, env=environment,
    )
    assert completed.returncode == 0, completed.stderr
    committed = STUDY / "fixtures" / "cells"
    rebuilt = tmp_path / "fixtures" / "cells"
    committed_files = sorted(
        p.relative_to(committed).as_posix() for p in committed.rglob("*") if p.is_file()
    )
    rebuilt_files = sorted(
        p.relative_to(rebuilt).as_posix() for p in rebuilt.rglob("*") if p.is_file()
    )
    assert committed_files == rebuilt_files
    for relative in committed_files:
        assert (committed / relative).read_bytes() == (rebuilt / relative).read_bytes(), relative


def test_split_view_pair_structure_is_validated_from_bytes():
    """R1-4 (round-2 residual): the fork report is derived and AUTHENTICATED —
    both attestations verify under the enforced pinned authority key; the
    unauthenticated key-id labels play no part."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    structure = score._fork_structure(matrix["pairs"]["split-view"], pins)
    assert structure["validated"] is True
    assert structure["checks"] == {
        "sameGenesisRecord": True,
        "bothAttestationsVerifyUnderPinnedAuthority": True,
        "samePerSeriesTrustPins": True,
        "samePosition": True, "differentHeads": True,
    }


def test_scorer_is_deterministic_and_control_gates_hold(jpack_bin, tmp_path):
    """Two pilot scorer runs: byte-identical outputs, all control gates green."""
    import os
    environment = dict(os.environ, JPACK_BIN=jpack_bin)
    outputs = []
    for name in ("attempt-a", "attempt-b"):
        completed = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "score.py"),
             "--attempt-root", str(tmp_path / name)],
            capture_output=True, text=True, env=environment,
        )
        assert completed.returncode == 0, completed.stderr
        raw = (tmp_path / name / "RESULTS.json").read_text(encoding="utf-8")
        outputs.append(raw.replace(name, "attempt-x"))
        results = json.loads(raw)
        assert results["pipelineInvalid"] is False
        assert results["label"] == "PILOT"
        for cid, record in results["cells"].items():
            if record["role"] == "control-gate":
                assert record["adjudicated"] and not record["divergent"], cid
    assert outputs[0] == outputs[1]


def test_holdout_registry_schema_and_hooks():
    """The reviewer's cells validate and every cell has a construction hook —
    which is all a pre-freeze test may touch: the stratum is never executed
    before the freeze, and the context gate below enforces exactly that."""
    holdout = json.loads(
        (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
    )
    assert score.holdout_schema_problems(holdout) == []
    assert sorted(c["id"] for c in holdout["cells"]) == sorted(build_fixtures.HOLDOUT_HOOKS)
    assert holdout["reviewer"].startswith("codex-cli")
    roles = [c["role"] for c in holdout["cells"]]
    assert "control-gate" in roles


def test_holdout_construction_refuses_pre_freeze():
    """No context: refused. A forged context: refused while any freeze pin is
    null — so nothing can execute the stratum before the freeze."""
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(None, STUDY / "nowhere", [])
    forged = build_fixtures.HoldoutAttemptContext(
        attempt_root=str(STUDY), pins_raw_sha256="0" * 64,
        preregistration_sha256="0" * 64, matrix_holdout_sha256="0" * 64,
    )
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(forged, STUDY / "nowhere", [])
    problems = build_fixtures.holdout_context_problems(forged)
    assert any("freeze pin" in problem for problem in problems)


def test_no_holdout_bytes_under_fixtures():
    """Holdout artifacts are attempt-local only; fixtures/ never carries them."""
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


def test_holdout_refused_while_freeze_pins_null(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "score.py"),
         "--attempt-root", str(tmp_path / "holdout-early"), "--include-holdout"],
        capture_output=True, text=True,
    )
    assert completed.returncode == 2
    results = json.loads(
        (tmp_path / "holdout-early" / "RESULTS.json").read_text(encoding="utf-8")
    )
    assert results["pipelineInvalid"] is True
    assert "refused" in results["problem"]
    marker = json.loads(
        (tmp_path / "holdout-early" / "ATTEMPT.json").read_text(encoding="utf-8")
    )
    assert marker["pinsRawSha256"] == results["pinsRawSha256"]
    assert marker["pinsRawSha256"] is not None


def test_scorer_records_attempt_before_pins_parse(tmp_path, monkeypatch):
    """A malformed pin registry still leaves a recorded attempt."""
    import os
    root = tmp_path / "marker"
    broken = tmp_path / "PINS.json"
    broken.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(score, "PINS_PATH", broken)
    with pytest.raises(BaseException):
        score.main(["--attempt-root", str(root)])
    assert (root / "ATTEMPT.json").is_file()
    assert (root / "RESULTS.json").is_file()
