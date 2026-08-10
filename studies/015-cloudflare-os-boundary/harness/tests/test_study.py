"""Protocol-integrity suite: vocabulary sync, registry schema, manifests, refusals.

Per-code reachability and first-failure ordering live in `test_reachability.py`; this
file owns everything that must hold before any cell runs.

Nothing here adjudicates a reviewer-holdout fixture. The holdout may be *constructed*
before the freeze — the scorer's gate requires the fixtures to exist — but no layer
verdict is computed over one until the preregistration is frozen, so every condition
below is built from locked fixtures or from the registry alone.
"""

import json
import re

import pytest

import commitment as cmt
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


ALL_CODES = verify.UPSTREAM_CODES + verify.BINDING_CODES + verify.REPLAY_CODES


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_registered_code_is_in_the_spec(code):
    assert "`%s`" % code in spec_text(), code


def test_spec_code_tables_are_exactly_the_registered_vocabulary():
    section = spec_text().split("## 5. The verification ceremony", 1)[1]
    upstream_section = section.split("### Layer `binding`", 1)[0]
    binding_section = section.split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    replay_section = section.split("### Layer `replay`", 1)[1].split(
        "### Report vocabulary", 1
    )[0]
    numbered = re.compile(r"^\d+\.\s+`([a-z0-9-]+)`", re.MULTILINE)
    assert set(numbered.findall(upstream_section)) == set(verify.UPSTREAM_CODES)
    binding_codes = {
        token
        for token in re.findall(r"`([a-z0-9-]+)`", binding_section)
        if token in verify.BINDING_CODES
    }
    assert binding_codes == set(verify.BINDING_CODES)
    replay_codes = set(re.findall(r"`(replay-[a-z0-9-]+)`", replay_section))
    assert replay_codes == set(verify.REPLAY_CODES)


def test_spec_binding_order_is_the_implemented_order():
    """The SPEC's numbered binding steps are the order the checks actually run in."""
    section = spec_text().split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    spec_order = []
    for line in section.splitlines():
        match = re.match(r"^\d+\.\s+`([a-z0-9-]+)`", line.strip())
        if match:
            spec_order.append(match.group(1))
    implemented = [label.split("/")[0] for label, _ in verify.BINDING_CHECKS]
    assert spec_order == implemented


def test_scorer_vocabulary_is_derived_from_verify():
    assert set(score.LAYER_OUTCOMES["upstream"]) == {
        "pass",
        "not-engaged",
        "unavailable",
    } | {"fail:" + code for code in verify.UPSTREAM_CODES}
    assert set(score.LAYER_OUTCOMES["binding"]) == {"pass"} | {
        "fail:" + code for code in verify.BINDING_CODES
    }
    assert set(score.LAYER_OUTCOMES["replay"]) == {"pass", "unavailable"} | {
        "fail:" + code for code in verify.REPLAY_CODES
    }


def test_execution_states_and_connector_outcomes_are_in_the_spec():
    text = spec_text()
    for state in verify.EXECUTION_STATES + verify.CONNECTOR_OUTCOMES:
        assert "`%s`" % state in text, state


def test_not_engaged_is_not_a_pass_anywhere_in_the_scorer():
    """`not-engaged` must be its own outcome, never folded into pass in the vocabulary."""
    assert "not-engaged" in score.LAYER_OUTCOMES["upstream"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["binding"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["replay"]


# ---------------------------------------------------------------------------
# registry and manifests
# ---------------------------------------------------------------------------

def test_matrix_is_schema_clean():
    assert score.matrix_problems(load_json(STUDY / "harness" / "MATRIX.json")) == []


def test_matrix_layer_attribution_is_single_layer_for_endpoints():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        if cell["role"] != "endpoint":
            continue
        failing = [
            layer
            for layer, outcome in cell["expected"].items()
            if outcome not in ("pass", "not-engaged")
        ]
        assert len(failing) == 1, (cell["id"], failing)


def test_every_endpoint_registers_a_mutation_constraint():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        assert cell["mutationConstraint"].strip(), cell["id"]


def test_holdout_is_authored_disjoint_and_constructed():
    holdout = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert score.holdout_problems(holdout) == []
    assert holdout["reviewer"]
    assert len(holdout["cells"]) >= 4


def test_holdout_expectations_match_the_authored_file_modulo_the_recorded_migration():
    """The reviewer's expectations are never revised — only mechanically re-keyed."""
    authored = load_json(STUDY / "reviews" / "round-1" / "MATRIX-HOLDOUT.authored.json")
    migrated = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert migrated.get("schemaMigration")
    by_id = {cell["id"]: cell for cell in migrated["cells"]}
    assert set(by_id) == {cell["id"] for cell in authored["cells"]}
    for cell in authored["cells"]:
        after = by_id[cell["id"]]
        assert after["construction"] == cell["construction"]
        assert after["note"] == cell["note"]
        assert after["upstreamChecksReplayed"] == cell["platformChecksEngaged"]
        assert after["expected"]["binding"] == cell["expected"]["binding"]
        assert after["expected"]["replay"] == cell["expected"]["replay"]
        expected_upstream = cell["expected"]["cf"]
        if not cell["platformChecksEngaged"] and expected_upstream == "pass":
            expected_upstream = "not-engaged"
        assert after["expected"]["upstream"] == expected_upstream


def test_study_manifest_is_exact():
    assert make_manifest.manifest_problems() == []


def test_every_fixture_manifest_is_exact():
    roots = [STUDY / "fixtures" / "baseline"]
    for parent in ("mutations", "holdout"):
        roots.extend(sorted((STUDY / "fixtures" / parent).iterdir()))
    for root in roots:
        assert verify.manifest_problems(root) == [], root.name


def test_fixture_typecheck_is_clean(cfos_source):
    del cfos_source
    assert typecheck.typecheck_problems() == []


def test_typecheck_is_a_scorer_precondition():
    """A published score may not call itself valid without the registered typecheck."""
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "typecheck.typecheck_problems()" in source


# ---------------------------------------------------------------------------
# refusals and validity separation
# ---------------------------------------------------------------------------

def test_holdout_refused_while_preregistration_digest_is_null(tmp_path):
    pins = load_json(STUDY / "harness" / "PINS.json")
    if pins["preregistration"]["sha256"] is None:
        with pytest.raises(SystemExit):
            score.run(tmp_path / "attempt", include_holdout=True)
        # The refusal is recorded, not silent: the attempt marker is written before
        # anything is read, and nothing was adjudicated or published.
        assert (tmp_path / "attempt" / "ATTEMPT.json").is_file()
        assert not (tmp_path / "attempt" / "RESULTS.json").exists()


def test_scorer_refuses_an_existing_attempt_root(tmp_path):
    (tmp_path / "attempt").mkdir()
    with pytest.raises(SystemExit):
        score.run(tmp_path / "attempt")


def test_holdout_invalidity_cannot_change_r1():
    """Structural: the two strata are adjudicated into disjoint collections."""
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "holdout_validity = []" in source
    assert 'sink = holdout_validity if is_holdout else validity' in source
    # R1's inputs are drawn from `rows`, which only ever receives locked cells.
    assert 'invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]' in source
    assert '(holdout_rows if is_holdout else rows).append(row)' in source


def test_replay_set_drift_is_not_adjudicated(jpack_bin, tmp_path):
    """An upstream report whose replayed set differs from the registry is validity."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    verdicts = {
        "cells": {
            "pos-baseline": {
                "verdict": "pass",
                "code": None,
                "detail": None,
                "engaged": ["classifyTool"],  # the registry says both are replayed
            }
        }
    }
    validity = []
    row = score.adjudicate_cell(cell, jpack_bin, tmp_path, verdicts, validity)
    assert row["status"] == score.NOT_ADJUDICATED
    assert any("upstreamChecksReplayed" in item["problem"] for item in validity)
    assert row["divergences"] == []


def test_registered_absences_authority_is_the_cell_field():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    cell["registeredAbsences"] = ["report"]
    problems = score.pipeline_problems(STUDY / "fixtures" / "baseline", cell)
    assert "registered absence is present: report.json" in problems


def test_layer_functions_never_read_the_matrix():
    assert "MATRIX" not in (STUDY / "adapter" / "verify.py").read_text(encoding="utf-8")


def test_probe_sources_never_read_the_matrix():
    for path in sorted((STUDY / "probes").rglob("*.ts")):
        code_lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith(("//", "*", "/*"))
        ]
        assert "MATRIX" not in "\n".join(code_lines), path.name


# ---------------------------------------------------------------------------
# the adapter's reproduction of the platform's own rule
# ---------------------------------------------------------------------------

def test_action_kind_tag_matches_the_platform_rule():
    # The literal the pinned `actionKindFor` produces for the registered scope and tool;
    # `probes/upstream-probes.ts` asserts the same equality against upstream itself.
    assert cmt.action_kind_tag() == "jps-tracker:create_work_item"


def test_derived_action_fields_are_disjoint_from_contextual_ones():
    assert not set(cmt.DERIVED_ACTION_FIELDS) & set(cmt.CONTEXTUAL_ACTION_FIELDS)
    assert set(cmt.DERIVED_ACTION_FIELDS) | set(cmt.CONTEXTUAL_ACTION_FIELDS) == set(
        cmt.ACTION_FIELDS
    )


def test_suppressed_codes_are_published_for_multi_defect_cells(jpack_bin, tmp_path):
    """s05 carries a second defect by construction; it must be published, not hidden."""
    del jpack_bin, tmp_path
    result = verify.layer_binding(
        verify.Cell(STUDY / "fixtures" / "mutations" / "s05-handoff-dropped")
    )
    assert result["code"] == "handoff-dropped"
    assert "report-misattribution" in result["suppressed"]


def test_matrix_modeled_dependencies_are_registered_where_used():
    """Any cell whose construction leans on a modeled datum must declare it."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        directory = score.cell_directory(cell)
        platform = json.loads((directory / "platform.json").read_text(encoding="utf-8"))
        declared = set(cell["modeledDependencies"])
        if platform.get("effects"):
            assert "effectAttestation" in declared, cell["id"]
        if platform.get("drainWitnesses"):
            assert "drainSnapshot" in declared, cell["id"]
        if platform.get("stagedCalls"):
            assert "stagedCallArguments" in declared, cell["id"]
