"""Protocol-integrity suite: vocabulary sync, registry schema, manifests, refusals.

The reachability of every registered verdict code (and first-failure ordering) lives in
`test_reachability.py`; this file owns everything that must hold before any cell runs.
"""

import json

import pytest

import make_manifest
import score
import typecheck
import verify
from conftest import STUDY, load_json


# ---------------------------------------------------------------------------
# vocabulary sync — SPEC section 5 vs the code vs the scorer
# ---------------------------------------------------------------------------

def spec_text():
    return (STUDY / "adapter" / "SPEC.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("code", verify.CF_CODES + verify.BINDING_CODES + verify.REPLAY_CODES)
def test_every_registered_code_is_in_the_spec(code):
    assert "`%s`" % code in spec_text(), code


def test_spec_code_tables_are_exactly_the_registered_vocabulary():
    # The SPEC's section 5 numbered code entries and its replay code list must equal the
    # registered vocabulary exactly — the vocabulary cannot grow or shrink in prose alone.
    import re

    section = spec_text().split("## 5. The verification ceremony", 1)[1]
    cf_section = section.split("### Layer `binding`", 1)[0]
    binding_section = section.split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    replay_section = section.split("### Layer `replay`", 1)[1].split(
        "### Report vocabulary", 1
    )[0]
    numbered = re.compile(r"^\d+\.\s+`([a-z0-9-]+)`", re.MULTILINE)
    assert set(numbered.findall(cf_section)) == set(verify.CF_CODES)
    binding_codes = set(numbered.findall(binding_section))
    # step 3 carries two codes on one numbered line
    binding_codes |= {
        token
        for token in re.findall(r"`([a-z0-9-]+)`", binding_section)
        if token in verify.BINDING_CODES
    }
    assert binding_codes == set(verify.BINDING_CODES)
    replay_codes = {
        token
        for token in re.findall(r"`(replay-[a-z0-9-]+)`", replay_section)
    }
    assert replay_codes == set(verify.REPLAY_CODES)


def test_scorer_vocabulary_is_derived_from_verify():
    assert set(score.LAYER_OUTCOMES["cf"]) == {"pass", "unavailable"} | {
        "fail:" + code for code in verify.CF_CODES
    }
    assert set(score.LAYER_OUTCOMES["binding"]) == {"pass"} | {
        "fail:" + code for code in verify.BINDING_CODES
    }
    assert set(score.LAYER_OUTCOMES["replay"]) == {"pass", "unavailable"} | {
        "fail:" + code for code in verify.REPLAY_CODES
    }


def test_execution_states_match_spec():
    for state in verify.EXECUTION_STATES:
        assert '"%s"' % state in spec_text() or "*%s*" % state in spec_text() or (
            "`%s`" % state
        ) in spec_text() or state in spec_text()


# ---------------------------------------------------------------------------
# registry and manifests
# ---------------------------------------------------------------------------

def test_matrix_is_schema_clean():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    assert score.matrix_problems(registry) == []


def test_matrix_layer_attribution_is_single_layer():
    # PREREGISTRATION section 7: no endpoint cell registers a multi-layer detection.
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        if cell["role"] != "endpoint":
            continue
        failing = [
            layer for layer, outcome in cell["expected"].items() if outcome != "pass"
        ]
        assert len(failing) == 1, (cell["id"], failing)


def test_holdout_scaffold_shape():
    holdout = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert holdout["stratum"] == "reviewer-holdout"
    assert isinstance(holdout["cells"], list)


def test_study_manifest_is_exact(cfos_source):
    del cfos_source  # fixtures exist independently; env asserted by the fixture
    assert make_manifest.manifest_problems() == []


def test_every_fixture_manifest_is_exact():
    roots = [STUDY / "fixtures" / "baseline"] + sorted(
        (STUDY / "fixtures" / "mutations").iterdir()
    )
    for root in roots:
        assert verify.manifest_problems(root) == [], root.name


def test_fixture_typecheck_is_clean(cfos_source):
    del cfos_source
    assert typecheck.typecheck_problems() == []


# ---------------------------------------------------------------------------
# refusals and validity separation
# ---------------------------------------------------------------------------

def test_holdout_refused_while_preregistration_digest_is_null(tmp_path):
    pins = load_json(STUDY / "harness" / "PINS.json")
    assert pins["preregistration"]["sha256"] is None or isinstance(
        pins["preregistration"]["sha256"], str
    )
    if pins["preregistration"]["sha256"] is None:
        with pytest.raises(SystemExit):
            score.run(tmp_path / "attempt", include_holdout=True)
        assert not (tmp_path / "attempt").exists()


def test_scorer_refuses_an_existing_attempt_root(tmp_path):
    (tmp_path / "attempt").mkdir()
    with pytest.raises(SystemExit):
        score.run(tmp_path / "attempt")


def test_engagement_drift_is_not_adjudicated(jpack_bin, tmp_path):
    """A cf report whose engaged set differs from the registry is validity, not detection."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    fake_verdicts = {
        "cells": {
            "pos-baseline": {
                "verdict": "pass",
                "code": None,
                "detail": None,
                "engaged": ["classifyTool"],  # registry says both checks engage
            }
        }
    }
    validity = []
    row = score.adjudicate_cell(cell, jpack_bin, tmp_path, fake_verdicts, validity)
    assert row["status"] == score.NOT_ADJUDICATED
    assert any("engagement" in item["problem"] for item in validity)
    assert row["divergences"] == []


def test_registered_absences_authority_is_the_cell_field():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    cell["registeredAbsences"] = ["report"]
    problems = score.pipeline_problems(STUDY / "fixtures" / "baseline", cell)
    assert "registered absence is present: report.json" in problems


def test_layer_functions_never_read_the_matrix():
    # The layers must not know their expectations: no layer module imports the registry.
    source = (STUDY / "adapter" / "verify.py").read_text(encoding="utf-8")
    assert "MATRIX" not in source


def test_probe_sources_never_read_the_matrix():
    # Comments may mention the registry (to say they never read it); code may not.
    for path in sorted((STUDY / "probes").rglob("*.ts")):
        code_lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith(("//", "*", "/*"))
        ]
        assert "MATRIX" not in "\n".join(code_lines), path.name
