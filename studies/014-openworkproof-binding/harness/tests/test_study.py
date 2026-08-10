"""Harness mechanics and controls — deterministic, offline, no network.

These tests check the machinery, not the matrix: the commitment's digest and the
canonical disposition bytes, that the verdict vocabulary in `adapter/SPEC.md`
section 5 is exactly the vocabulary the code can produce and classify, the
disclosed controls, the registry schema, the freeze machinery, and that the
frozen fixtures are what the builder produces. Adjudicating the registered
expectations is the scorer's job, not a test's.

Nothing here skips: a missing `JPACK_BIN` or `OWP_SOURCE` is a failure.

Run: JPACK_BIN=... OWP_SOURCE=... <venv>/bin/python -m pytest harness/tests -q
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from conftest import STUDY, jpack_bin, owp_source  # noqa: E402

sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import commitment  # noqa: E402
import make_manifest  # noqa: E402
import score  # noqa: E402
import verify  # noqa: E402

FIXTURES = STUDY / "fixtures"
BASELINE = FIXTURES / "baseline"
MATRIX = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
HOLDOUT = json.loads(
    (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
)
PINS = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))

NEGATIVE_CONTROLS = (
    "neg-signature",
    "neg-evidence-digest",
    "neg-parent-ref",
    "neg-action-param",
)


def cell_directory(cell_id):
    return score.cell_directory(cell_id)


def run_cell(cell_id):
    binary = jpack_bin()
    work_root = Path(tempfile.mkdtemp(prefix="study014-test-"))
    try:
        return verify.verify_cell(cell_directory(cell_id), binary, work_root)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)


# --------------------------------------------------------------------------
# 1. the commitment digest, against a fixed vector
# --------------------------------------------------------------------------

GOLDEN_COMMITMENT = {
    "commitmentVersion": "1",
    "judgment": {
        "packId": "https://example.com/judgment-packs/expense-approval",
        "packVersion": "0.1.0",
        "packDigest": "sha256:" + "11" * 32,
        "specVersion": "0.2.0-draft",
        "evaluatorSpecVersion": "0.2.0-draft",
        "evaluatorRelease": "0.16.0",
        "executableDigest": "sha256:" + "22" * 32,
        "factsDigest": "sha256:" + "33" * 32,
        "evidenceDigest": "sha256:" + "44" * 32,
        "supportedExtensions": [],
        "dispositionDigest": "sha256:" + "55" * 32,
    },
    "action": {"toolName": "owp.apply_patch", "argumentsDigest": "66" * 32},
}
GOLDEN_DIGEST = "13f6fa88cbe6b179f1b34f14f5c80e476f37ed1f155cac5502944002250a3e5a"


def test_commitment_digest_golden_vector():
    assert commitment.commitment_digest(GOLDEN_COMMITMENT) == GOLDEN_DIGEST


def test_commitment_digest_is_field_sensitive():
    mutated = json.loads(json.dumps(GOLDEN_COMMITMENT))
    mutated["judgment"]["factsDigest"] = "sha256:" + "77" * 32
    assert commitment.commitment_digest(mutated) != GOLDEN_DIGEST


def test_commitment_schema_refuses_unknown_fields():
    mutated = json.loads(json.dumps(GOLDEN_COMMITMENT))
    mutated["judgment"]["handoffTarget"] = {"kind": "human-role"}
    with pytest.raises(commitment.CommitmentSchemaError):
        commitment.validate_commitment(mutated)


# --------------------------------------------------------------------------
# 2. the JCS boundary is byte-level (R1-8 canonicalization vectors)
# --------------------------------------------------------------------------

CANONICAL_GOLDEN = commitment.commitment_bytes(GOLDEN_COMMITMENT)


def test_canonical_bytes_round_trip():
    parsed = commitment.parse_commitment_bytes(CANONICAL_GOLDEN)
    assert parsed == GOLDEN_COMMITMENT
    assert commitment.canonical_encoding_problem(CANONICAL_GOLDEN, parsed) is None


def test_duplicate_member_names_are_refused():
    raw = CANONICAL_GOLDEN.replace(
        b'"commitmentVersion":"1"', b'"commitmentVersion":"1","commitmentVersion":"2"'
    )
    assert raw != CANONICAL_GOLDEN
    with pytest.raises(commitment.CommitmentSchemaError) as error:
        commitment.parse_commitment_bytes(raw)
    assert "duplicate" in str(error.value)


def test_invalid_utf8_is_refused():
    with pytest.raises(commitment.CommitmentSchemaError) as error:
        commitment.parse_commitment_bytes(CANONICAL_GOLDEN[:-1] + b"\xff")
    assert "UTF-8" in str(error.value) or "JSON" in str(error.value)


def test_whitespace_encoding_parses_but_is_not_canonical():
    raw = json.dumps(GOLDEN_COMMITMENT, indent=2).encode("utf-8")
    parsed = commitment.parse_commitment_bytes(raw)
    assert parsed == GOLDEN_COMMITMENT
    assert commitment.canonical_encoding_problem(raw, parsed) is not None


def test_key_order_encoding_parses_but_is_not_canonical():
    reordered = {
        "action": GOLDEN_COMMITMENT["action"],
        "judgment": GOLDEN_COMMITMENT["judgment"],
        "commitmentVersion": "1",
    }
    raw = json.dumps(reordered, separators=(",", ":")).encode("utf-8")
    parsed = commitment.parse_commitment_bytes(raw)
    assert parsed == GOLDEN_COMMITMENT
    assert commitment.canonical_encoding_problem(raw, parsed) is not None


def test_unicode_escape_encoding_parses_but_is_not_canonical():
    raw = json.dumps(GOLDEN_COMMITMENT, separators=(",", ":"), ensure_ascii=True)
    raw = raw.replace("expense-approval", "expense\\u002dapproval").encode("utf-8")
    parsed = commitment.parse_commitment_bytes(raw)
    assert parsed == GOLDEN_COMMITMENT
    assert commitment.canonical_encoding_problem(raw, parsed) is not None


def test_non_minimal_number_encoding_is_refused_by_the_schema():
    """The commitment's value space is strings, arrays and null — no numbers.

    A non-minimal number can therefore only appear as an unknown field, and the
    schema refuses it. The vector is registered anyway so a future schema that
    admits a number cannot quietly admit `1.0` as well.
    """
    raw = CANONICAL_GOLDEN.replace(b'"commitmentVersion":"1"', b'"commitmentVersion":1.0')
    parsed = commitment.parse_commitment_bytes
    with pytest.raises(commitment.CommitmentSchemaError):
        parsed(raw)


# --------------------------------------------------------------------------
# 3. the canonical disposition bytes
# --------------------------------------------------------------------------

def test_disposition_canonical_bytes_are_the_envelope_member_bytes():
    envelope_bytes = (BASELINE / "evaluation.json").read_bytes()
    envelope = json.loads(envelope_bytes.decode("utf-8"))
    canonical = commitment.disposition_canonical_bytes(envelope)
    assert canonical in envelope_bytes, "JCS output is not the emitted member bytes"
    marker = b'"disposition":'
    start = envelope_bytes.index(marker) + len(marker)
    assert envelope_bytes[start:start + len(canonical)] == canonical
    retained = json.loads((BASELINE / "commitment.json").read_bytes().decode("utf-8"))
    assert (
        "sha256:" + hashlib.sha256(canonical).hexdigest()
        == retained["judgment"]["dispositionDigest"]
    )


def test_the_retained_baseline_commitment_is_canonical_bytes():
    raw = (BASELINE / "commitment.json").read_bytes()
    parsed = commitment.parse_commitment_bytes(raw)
    assert commitment.canonical_encoding_problem(raw, parsed) is None


# --------------------------------------------------------------------------
# 4. the verdict vocabulary cannot drift from the counting
# --------------------------------------------------------------------------

def spec_codes():
    """The codes of the SPEC section 5 tables, by layer."""
    text = (STUDY / "adapter" / "SPEC.md").read_text(encoding="utf-8")
    binding_block = text.split("**Layer BINDING**")[1].split("**Layer REPLAY**")[0]
    replay_block = text.split("**Layer REPLAY**")[1]
    codes = {}
    for layer, block in (("binding", binding_block), ("replay", replay_block)):
        found = []
        for line in block.splitlines():
            if not line.startswith("| `"):
                continue
            first_column = line.split("|")[1]
            for token in re.findall(r"`([^`]+)`", first_column):
                found.append(token.split(":<")[0])
        codes[layer] = set(found)
    return codes


def test_spec_and_code_vocabularies_are_identical():
    spec = spec_codes()
    assert spec["binding"] == set(verify.BINDING_CODES)
    assert spec["replay"] == set(verify.REPLAY_CODES)


def test_scorer_classifies_exactly_the_spec_vocabulary():
    spec = spec_codes()
    classified_binding = {
        outcome.split("fail:")[1]
        for outcome in score.BINDING_OUTCOMES
        if outcome.startswith("fail:")
    }
    classified_replay = {
        outcome.split("fail:")[1]
        for outcome in score.REPLAY_OUTCOMES
        if outcome.startswith("fail:")
    }
    assert classified_binding == spec["binding"]
    assert classified_replay == spec["replay"]


def test_outcome_never_carries_detail():
    decorated = verify.result("fail", "replay-refused", "pack-not-conformant: refused")
    assert verify.outcome(decorated) == "fail:replay-refused"
    assert verify.outcome(verify.result("unavailable", "replay-unavailable", "x")) == (
        "unavailable"
    )
    assert verify.outcome(verify.result("pass")) == "pass"
    assert verify.outcome(verify.result("fail", None, "upstream said no")) == "fail"


# --------------------------------------------------------------------------
# 5. the disclosed controls
# --------------------------------------------------------------------------

def test_positive_control_passes_every_layer():
    result = run_cell("pos-baseline")
    assert result["owp"]["outcome"] == "pass", result["owp"]["detail"]
    assert result["binding"]["outcome"] == "pass", result["binding"]["detail"]
    assert result["replay"]["outcome"] == "pass", result["replay"]["detail"]
    assert result["combined"] == "pass"


@pytest.mark.parametrize("cell_id", NEGATIVE_CONTROLS)
def test_negative_controls_fail_the_owp_layer(cell_id):
    result = run_cell(cell_id)
    assert result["owp"]["outcome"] == "fail", result["owp"]["detail"]


def test_unsigned_metadata_carriage_is_green_to_owp_and_unbound_to_the_adapter():
    result = run_cell("m28-unsigned-metadata-carriage")
    assert result["owp"]["outcome"] == "pass", result["owp"]["detail"]
    assert result["binding"]["outcome"] == "fail:commitment-objective-missing"


# --------------------------------------------------------------------------
# 6. the registry schema and the two strata
# --------------------------------------------------------------------------

def test_matrix_matches_the_frozen_cell_set_and_schema():
    assert score.matrix_problems(MATRIX) == []
    assert len(MATRIX["cells"]) == 39


def test_role_partition_is_the_registered_one():
    roles = {}
    for cell in MATRIX["cells"]:
        roles.setdefault(cell["role"], []).append(cell["id"])
    assert sorted(roles["control-gate"]) == sorted(("pos-baseline",) + NEGATIVE_CONTROLS)
    assert roles["demonstration"] == ["m28-unsigned-metadata-carriage"]
    assert roles["descriptive"] == ["e22-workorder-rollback"]
    assert len(roles["endpoint"]) == 39 - 5 - 1 - 1


def test_registered_absences_are_independent_of_expectations():
    for cell in MATRIX["cells"]:
        absent = score.registered_absences(cell)
        if cell["id"] == "a05-pack-artifact-missing":
            assert absent == {"pack.json"}
        else:
            assert absent == set(), cell["id"]


def test_e18_is_no_longer_registered_anywhere():
    ids = [cell["id"] for cell in MATRIX["cells"]]
    assert not any(item.startswith("e18") for item in ids)
    assert not (FIXTURES / "mutations" / "e18-stale-decision-currency").exists()
    prereg = (STUDY / "PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "Analytic limitations" in prereg


def test_holdout_stratum_is_an_empty_attributed_scaffold():
    assert HOLDOUT["stratum"] == "reviewer-holdout"
    assert HOLDOUT["cells"] == []
    assert "never executed" in HOLDOUT["note"]


def test_holdout_is_refused_while_the_preregistration_is_draft(tmp_path):
    assert PINS["preregistration"]["sha256"] is None, (
        "this test describes the pre-freeze state"
    )
    with pytest.raises(SystemExit) as error:
        score.run(tmp_path / "holdout-attempt", include_holdout=True)
    assert "--include-holdout is refused" in str(error.value)
    assert not (tmp_path / "holdout-attempt").exists()


# --------------------------------------------------------------------------
# 7. freeze machinery
# --------------------------------------------------------------------------

def test_study_manifest_covers_the_registered_set_and_verifies():
    assert make_manifest.manifest_problems() == []
    covered = make_manifest.manifest_entries()
    for required in (
        "PREREGISTRATION.md",
        "PREREG-REVIEW.md",
        "adapter/SPEC.md",
        "adapter/commitment.py",
        "adapter/verify.py",
        "harness/MATRIX.json",
        "harness/MATRIX-HOLDOUT.json",
        "harness/PINS.json",
        "harness/owpflow.py",
        "harness/build_fixtures.py",
        "harness/score.py",
        "fixtures/baseline/MANIFEST.sha256",
    ):
        assert required in covered, required
    manifests = [item for item in covered if item.endswith("MANIFEST.sha256")]
    assert len(manifests) == len(MATRIX["cells"])


def test_pins_are_enforced_and_the_live_environment_matches():
    assert score.pin_problems(PINS, jpack_bin()) == []


def test_a_wrong_pin_makes_the_attempt_terminally_invalid(tmp_path):
    """The scorer must refuse to adjudicate, and must still leave a record."""
    broken = json.loads(json.dumps(PINS))
    broken["harnessPython"]["version"] = "3.0.0"
    problems = score.pin_problems(broken, jpack_bin())
    assert any("interpreter is" in problem for problem in problems)


def test_terminal_invalid_record_is_persisted(tmp_path):
    root = tmp_path / "terminal"
    results = score.terminal_invalid(root, "PILOT", ["synthetic failure"], {})
    assert results["verdict"] == score.VERDICT_INVALID
    assert (root / "RESULTS.json").is_file()
    assert (root / "DETECTION-MATRIX.md").is_file()
    written = json.loads((root / "RESULTS.json").read_text())
    assert written["validity"]["records"][0]["problem"] == "synthetic failure"


def test_attempt_marker_lands_before_any_cell_runs(tmp_path, monkeypatch):
    root = tmp_path / "marker"

    def explode(*_args, **_kwargs):
        raise RuntimeError("cells must not run in this test")

    monkeypatch.setattr(score, "adjudicate_cell", explode)
    score.run(root)
    assert (root / "ATTEMPT.json").is_file()
    marker = json.loads((root / "ATTEMPT.json").read_text())
    assert marker["marker"] == "written before any cell ran"
    written = json.loads((root / "RESULTS.json").read_text())
    assert written["verdict"] == score.VERDICT_INVALID


# --------------------------------------------------------------------------
# 8. manifest integrity of every committed cell
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cell_id", [cell["id"] for cell in MATRIX["cells"]])
def test_every_registered_cell_is_present_and_manifested(cell_id):
    directory = cell_directory(cell_id)
    assert directory.is_dir(), cell_id
    assert verify.manifest_problems(directory) == []


@pytest.mark.parametrize("cell_id", [cell["id"] for cell in MATRIX["cells"]])
def test_no_cell_is_incomplete_in_an_unregistered_way(cell_id):
    cell = next(item for item in MATRIX["cells"] if item["id"] == cell_id)
    assert score.pipeline_problems(cell_directory(cell_id), cell) == []


def test_an_unregistered_absence_is_not_adjudicated(tmp_path):
    cell = next(item for item in MATRIX["cells"] if item["id"] == "pos-baseline")
    staged = tmp_path / "baseline"
    shutil.copytree(BASELINE, staged)
    (staged / "facts.json").unlink()
    problems = score.pipeline_problems(staged, cell)
    assert any("unregistered missing artifact: facts.json" in item for item in problems)


def test_an_out_of_vocabulary_outcome_is_not_adjudicated():
    observed = {
        "owp": verify.result("pass"),
        "binding": {"verdict": "fail", "code": "invented-code", "detail": None,
                    "outcome": "fail:invented-code"},
        "replay": verify.result("pass"),
    }
    for name in ("owp", "replay"):
        observed[name]["outcome"] = verify.outcome(observed[name])
    problems = score.vocabulary_problems("synthetic", observed)
    assert problems and "invented-code" in problems[0]


# --------------------------------------------------------------------------
# 9. determinism: every cell rebuilt, and the scorer run twice
# --------------------------------------------------------------------------

def test_every_frozen_fixture_is_what_the_builder_produces(source):
    """Rebuild ALL cells into a clean tree and byte-compare every manifest."""
    binary = jpack_bin()
    import build_fixtures

    out_root = Path(tempfile.mkdtemp(prefix="study014-rebuild-"))
    work_root = Path(tempfile.mkdtemp(prefix="study014-rebuild-work-"))
    try:
        payloads = build_fixtures.build_payloads(binary, work_root, source)
        registered = [cell["id"] for cell in MATRIX["cells"]]
        assert sorted(payloads) == sorted(registered)
        for cell_id in registered:
            directory = build_fixtures.cell_directory(out_root, cell_id)
            build_fixtures.write_cell(directory, payloads[cell_id])
            rebuilt = (directory / verify.MANIFEST_NAME).read_text()
            frozen = (cell_directory(cell_id) / verify.MANIFEST_NAME).read_text()
            assert rebuilt == frozen, cell_id
    finally:
        shutil.rmtree(out_root, ignore_errors=True)
        shutil.rmtree(work_root, ignore_errors=True)


def test_the_scorer_is_byte_identical_across_two_runs(tmp_path):
    jpack_bin()
    first = tmp_path / "attempt-a"
    second = tmp_path / "attempt-b"
    score.run(first)
    score.run(second)
    for name in ("ATTEMPT.json", "RESULTS.json", "DETECTION-MATRIX.md"):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_no_scorer_output_embeds_an_absolute_path(tmp_path):
    jpack_bin()
    root = tmp_path / "attempt-paths"
    score.run(root)
    for name in ("ATTEMPT.json", "RESULTS.json", "DETECTION-MATRIX.md"):
        text = (root / name).read_text(encoding="utf-8")
        assert str(tmp_path) not in text, name
        assert str(STUDY) not in text, name


# --------------------------------------------------------------------------
# 10. the environment is required, not optional
# --------------------------------------------------------------------------

def test_missing_owp_source_fails_rather_than_skips(monkeypatch):
    monkeypatch.delenv("OWP_SOURCE", raising=False)
    with pytest.raises(AssertionError) as error:
        owp_source()
    assert "OWP_SOURCE is unset" in str(error.value)


def test_missing_jpack_bin_fails_rather_than_skips(monkeypatch):
    monkeypatch.delenv("JPACK_BIN", raising=False)
    with pytest.raises(AssertionError) as error:
        jpack_bin()
    assert "JPACK_BIN is unset" in str(error.value)


def test_ci_pins_the_exact_interpreter_and_stages_the_clone():
    workflow = STUDY.parent.parent / ".github" / "workflows" / "ci.yml"
    if not workflow.is_file():
        pytest.fail("the CI workflow is not where the study expects it: %s" % workflow)
    text = workflow.read_text(encoding="utf-8")
    job = text.split("study-014")[1]
    assert '"%s"' % PINS["harnessPython"]["version"] in job, (
        "the study-014 job does not pin the exact interpreter"
    )
    assert "OWP_SOURCE" in job, "the study-014 job does not stage OWP_SOURCE"
