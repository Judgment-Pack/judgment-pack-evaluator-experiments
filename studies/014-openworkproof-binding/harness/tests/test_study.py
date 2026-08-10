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
import importlib.machinery
import json
import os
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

import build_fixtures  # noqa: E402
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


def test_an_escaped_lone_surrogate_is_refused_as_non_i_json():
    """R2-4: JSON, but not I-JSON — and it must not reach the canonicalizer."""
    raw = json.dumps(GOLDEN_COMMITMENT, separators=(",", ":"), ensure_ascii=True)
    raw = raw.replace("expense-approval", "expense-\\ud800approval", 1).encode("utf-8")
    with pytest.raises(commitment.CommitmentSchemaError) as error:
        commitment.parse_commitment_bytes(raw)
    assert "surrogate" in str(error.value)


def test_every_canonicalization_failure_maps_to_the_registered_error():
    """R2-4: `rfc8785`'s own exception never escapes the parse path."""
    with pytest.raises(commitment.CommitmentSchemaError):
        commitment.canonical_bytes({"objective": "expense-\ud800approval"})
    with pytest.raises(commitment.CommitmentSchemaError):
        commitment.commitment_bytes({"a": "\udfff"})
    with pytest.raises(commitment.CommitmentSchemaError):
        commitment.commitment_digest({"a": "\udfff"})
    assert issubclass(commitment.CommitmentEncodingError, commitment.CommitmentSchemaError)


def test_a_lone_surrogate_objective_is_schema_invalid_not_a_crash(tmp_path):
    """The mapped error, end to end on the binding layer (h02's expectation)."""
    directory = tmp_path / "surrogate"
    shutil.copytree(BASELINE, directory)
    bundle = json.loads((directory / "bundle.json").read_text(encoding="utf-8"))
    objective = bundle["work_order"]["objective"]
    bundle["work_order"]["objective"] = objective.replace(
        "expense-approval", "expense-\\ud800approval", 1
    )
    assert bundle["work_order"]["objective"] != objective
    (directory / "bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    record = verify.layer_binding(verify.Cell(directory))
    assert record["code"] == "commitment-schema-invalid"


def test_supported_extensions_are_a_set_not_a_multiset():
    """R2-8: SPEC section 1 states set semantics; duplicates are schema-invalid."""
    mutated = json.loads(json.dumps(GOLDEN_COMMITMENT))
    mutated["judgment"]["supportedExtensions"] = [
        "https://example.com/ext/unused",
        "https://example.com/ext/unused",
    ]
    with pytest.raises(commitment.CommitmentSchemaError) as error:
        commitment.validate_commitment(mutated)
    assert "duplicate" in str(error.value)
    single = json.loads(json.dumps(GOLDEN_COMMITMENT))
    single["judgment"]["supportedExtensions"] = ["https://example.com/ext/unused"]
    assert commitment.validate_commitment(single) is single
    spec = (STUDY / "adapter" / "SPEC.md").read_text(encoding="utf-8")
    assert "MUST be unique" in spec


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


def test_holdout_stratum_is_the_landed_attributed_reviewer_registry():
    """The reviewer authored it at round 2; it landed verbatim and unexecuted."""
    assert HOLDOUT["stratum"] == "reviewer-holdout"
    assert HOLDOUT["status"] == "AUTHORED-UNEXECUTED"
    assert "must remain unexecuted until the preregistration freezes" in HOLDOUT["note"]
    assert "reported separately" in HOLDOUT["note"]
    assert len(HOLDOUT["cells"]) == 8
    assert [cell["id"] for cell in HOLDOUT["cells"]] == list(
        build_fixtures.HOLDOUT_IDS
    )
    for cell in HOLDOUT["cells"]:
        assert cell["author"], cell["id"]


def test_no_holdout_fixture_has_been_built(tmp_path):
    """Pre-freeze the holdout is a specification, not an artifact tree."""
    for cell in HOLDOUT["cells"]:
        assert not score.holdout_cell_directory(cell["id"]).exists(), cell["id"]
    assert not (FIXTURES / "holdout").exists()


# --- R2-2 guards: schema, disjointness, and both mechanical refusals ------

def test_the_holdout_registry_validates_as_pure_json():
    """Schema validation reads the committed JSON and nothing else — no builds."""
    assert score.holdout_problems(HOLDOUT) == []


def test_the_holdout_validator_requires_attribution():
    mutated = json.loads(json.dumps(HOLDOUT))
    del mutated["cells"][0]["author"]
    problems = score.holdout_problems(mutated)
    assert any("missing required fields" in problem for problem in problems)


def test_the_holdout_validator_refuses_an_empty_stratum():
    problems = score.holdout_problems(dict(HOLDOUT, cells=[]))
    assert any("not a passing holdout" in problem for problem in problems)


def test_holdout_ids_are_disjoint_from_the_locked_stratum():
    locked = {cell["id"] for cell in MATRIX["cells"]}
    holdout = {cell["id"] for cell in HOLDOUT["cells"]}
    assert locked & holdout == set()
    collided = json.loads(json.dumps(HOLDOUT))
    collided["cells"][0]["id"] = "pos-baseline"
    problems = score.holdout_problems(collided)
    assert any("collide with the locked stratum" in problem for problem in problems)


def test_holdout_scoring_is_refused_while_the_preregistration_is_draft(tmp_path):
    assert PINS["preregistration"]["sha256"] is None, (
        "this test describes the pre-freeze state"
    )
    with pytest.raises(SystemExit) as error:
        score.run(tmp_path / "holdout-attempt", include_holdout=True)
    assert "--include-holdout is refused" in str(error.value)
    assert "preregistration digest" in str(error.value)
    assert not (tmp_path / "holdout-attempt").exists()


def test_holdout_scoring_is_refused_while_its_own_digest_is_null(tmp_path, monkeypatch):
    """Frozen preregistration is not enough: the holdout pin has to be filled."""
    assert PINS["matrixHoldout"]["sha256"] is None
    frozen = json.loads(json.dumps(PINS))
    frozen["preregistration"]["sha256"] = "00" * 32
    monkeypatch.setattr(score, "preflight_pins", lambda: frozen)
    with pytest.raises(SystemExit) as error:
        score.run(tmp_path / "holdout-attempt", include_holdout=True)
    assert "matrixHoldout digest" in str(error.value)
    assert not (tmp_path / "holdout-attempt").exists()


def test_holdout_building_is_refused_while_the_preregistration_is_draft():
    refusal = build_fixtures.holdout_refusal(PINS)
    assert refusal is not None and "--holdout is refused" in refusal
    with pytest.raises(SystemExit) as error:
        build_fixtures.main(["--holdout"])
    assert "--holdout is refused" in str(error.value)


def test_every_holdout_cell_has_an_unexecuted_builder_hook():
    """The hooks exist so the holdout is buildable, not so it is built."""
    for cell in HOLDOUT["cells"]:
        assert cell["id"] in build_fixtures.HOLDOUT_BUILDERS, cell["id"]
        assert callable(build_fixtures.HOLDOUT_BUILDERS[cell["id"]])


def test_a_constructibility_refusal_is_a_record_not_an_exception():
    """A construction upstream refuses is a finding, never a crash (R2-2)."""
    refusal = build_fixtures.ConstructibilityRefusal("h02-objective-lone-surrogate", "why")
    assert refusal.as_record() == {
        "cell": "h02-objective-lone-surrogate",
        "finding": "constructibility-refusal",
        "detail": "why",
    }
    assert not isinstance(refusal, BaseException)


def test_the_holdout_stratum_is_published_as_its_own_section(tmp_path):
    """The post-freeze path, exercised without executing a single holdout cell.

    Every holdout fixture is deliberately absent pre-freeze, so this adjudicates
    the stratum in exactly the state it is in: eight constructibility findings.
    What it asserts is the *separation* — a holdout summary of its own, a second
    table in the published matrix, and no holdout row anywhere in the locked
    stratum's counts or in the R1 verdict.
    """
    holdout = score.adjudicate_holdout(HOLDOUT, jpack_bin(), None, [])
    assert holdout["stratum"] == "reviewer-holdout"
    assert holdout["summary"] == "holdout inconclusive — pipeline-invalid"
    assert holdout["cells"] == 8 and holdout["adjudicated"] == 0
    assert sorted(holdout["pipelineInvalidCells"]) == sorted(build_fixtures.HOLDOUT_IDS)
    # h08 is the stratum's own control gate, evaluated inside the stratum.
    gate = next(
        row for row in holdout["rows"] if row["cell"] == "h08-semantic-facts-remint-control"
    )
    assert gate["role"] == "control-gate"

    locked = {
        "study": "014-openworkproof-binding",
        "stratum": "locked-replication",
        "attemptLabel": "PILOT",
        "verdict": score.VERDICT_HOLDS,
        "detection": {"rows": []},
        "holdout": holdout,
    }
    root = tmp_path / "published"
    score.write_outputs(root, locked, [], holdout)
    published = (root / "DETECTION-MATRIX.md").read_text(encoding="utf-8")
    assert "## Locked-replication stratum" in published
    assert "## Reviewer-holdout stratum" in published
    assert "h01-retained-commitment-noncanonical" in published
    written = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
    assert written["verdict"] == score.VERDICT_HOLDS, "the R1 verdict is untouched"
    assert written["detection"]["rows"] == []
    assert written["holdout"]["summary"].startswith("holdout ")


def test_an_absent_holdout_fixture_is_not_adjudicated_with_a_constructibility_note():
    validity = []
    row = score.adjudicate_cell(
        HOLDOUT["cells"][0],
        jpack_bin(),
        None,
        validity,
        directory=score.holdout_cell_directory(HOLDOUT["cells"][0]["id"]),
        scope="holdout",
    )
    assert row["status"] == score.NOT_ADJUDICATED
    assert row["stratum"] == "holdout"
    assert any("constructibility finding" in problem for problem in row["problems"])
    assert validity and validity[0]["stratum"] == "holdout"


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


# --- R2-1: the freeze is anchored outside the regenerable set -------------

def test_the_pin_registry_carries_the_round_two_anchors():
    assert "sha256" in PINS["studyManifest"]
    assert "sha256" in PINS["matrixHoldout"]
    assert PINS["openworkproof"]["installedPackageDigest"]


def test_the_installed_package_digest_is_enforced_and_matches():
    assert (
        score.installed_package_digest()
        == PINS["openworkproof"]["installedPackageDigest"]
    )
    broken = json.loads(json.dumps(PINS))
    broken["openworkproof"]["installedPackageDigest"] = "ab" * 32
    assert any(
        "installed openworkproof package does not match" in problem
        for problem in score.pin_problems(broken, jpack_bin())
    )
    missing = json.loads(json.dumps(PINS))
    missing["openworkproof"].pop("installedPackageDigest")
    assert any(
        "no installed openworkproof package digest" in problem
        for problem in score.pin_problems(missing, jpack_bin())
    )


def test_the_installed_package_digest_is_sensitive_to_a_package_byte(tmp_path, monkeypatch):
    """Not a declaration: the value moves when the installed bytes move."""
    import importlib.util

    real = importlib.util.find_spec("openworkproof")
    staged = tmp_path / "openworkproof"
    shutil.copytree(Path(real.origin).parent, staged)
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        lambda name: importlib.machinery.ModuleSpec(
            name, None, origin=str(staged / "__init__.py")
        ),
    )
    assert score.installed_package_digest() == PINS["openworkproof"][
        "installedPackageDigest"
    ]
    (staged / "policy.py").write_bytes((staged / "policy.py").read_bytes() + b"\n")
    assert score.installed_package_digest() != PINS["openworkproof"][
        "installedPackageDigest"
    ]


def test_the_vendored_pack_bytes_are_enforced_unconditionally():
    assert verify.sha256_file(score.PACK_PATH) == PINS["pack"]["sha256"]
    broken = json.loads(json.dumps(PINS))
    broken["pack"]["sha256"] = "cd" * 32
    assert any(
        "vendored pack bytes do not match" in problem
        for problem in score.pin_problems(broken, jpack_bin())
    )


def test_a_pinned_study_manifest_digest_is_enforced_once_filled():
    filled = json.loads(json.dumps(PINS))
    filled["studyManifest"]["sha256"] = verify.sha256_file(make_manifest.MANIFEST_PATH)
    assert score.pin_problems(filled, jpack_bin()) == []
    laundered = json.loads(json.dumps(PINS))
    laundered["studyManifest"]["sha256"] = "ef" * 32
    assert any(
        "harness/STUDY-MANIFEST.sha256" in problem
        for problem in score.pin_problems(laundered, jpack_bin())
    )


def test_a_pinned_holdout_digest_is_enforced_once_filled():
    filled = json.loads(json.dumps(PINS))
    filled["matrixHoldout"]["sha256"] = verify.sha256_file(
        STUDY / "harness" / "MATRIX-HOLDOUT.json"
    )
    assert score.pin_problems(filled, jpack_bin()) == []
    broken = json.loads(json.dumps(PINS))
    broken["matrixHoldout"]["sha256"] = "ef" * 32
    assert any(
        "harness/MATRIX-HOLDOUT.json" in problem
        for problem in score.pin_problems(broken, jpack_bin())
    )


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


# --- R2-6: nothing fails silently, and nothing is written non-atomically --

def test_the_attempt_marker_lands_before_pins_are_parsed(tmp_path, monkeypatch):
    """An unreadable PINS.json must still leave a marker AND a terminal record."""
    root = tmp_path / "pins-unreadable"
    real = Path.read_text

    def refuse(self, *args, **kwargs):
        if self.name == "PINS.json":
            raise OSError("PINS.json is unreadable in this test")
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", refuse)
    results = score.run(root)
    monkeypatch.undo()
    assert (root / "ATTEMPT.json").is_file()
    assert results["verdict"] == score.VERDICT_INVALID
    written = json.loads((root / "RESULTS.json").read_text())
    assert any(
        "outside cell adjudication" in record["problem"]
        for record in written["validity"]["records"]
    )


@pytest.mark.parametrize(
    "target", ["pin_problems", "matrix_problems", "installed_package_digest"]
)
def test_a_gate_or_provenance_crash_still_persists_a_terminal_record(
    tmp_path, monkeypatch, target
):
    root = tmp_path / ("crash-" + target)

    def explode(*_args, **_kwargs):
        raise RuntimeError("%s exploded in this test" % target)

    monkeypatch.setattr(score, target, explode)
    results = score.run(root)
    assert results["verdict"] == score.VERDICT_INVALID
    assert (root / "ATTEMPT.json").is_file()
    assert (root / "RESULTS.json").is_file()
    assert (root / "DETECTION-MATRIX.md").is_file()
    written = json.loads((root / "RESULTS.json").read_text())
    assert any(
        "exploded in this test" in record["problem"]
        for record in written["validity"]["records"]
    )


def test_a_finalization_crash_still_persists_a_terminal_record(tmp_path, monkeypatch):
    """The promise round 2 found unkept: `write_outputs` was outside the catch."""
    jpack_bin()
    root = tmp_path / "finalization"
    calls = []
    real = score.write_outputs

    def explode_once(attempt_root, results, rows, holdout=None):
        calls.append(results["verdict"])
        if len(calls) == 1:
            raise RuntimeError("publication exploded in this test")
        return real(attempt_root, results, rows, holdout)

    monkeypatch.setattr(score, "write_outputs", explode_once)
    results = score.run(root)
    assert results["verdict"] == score.VERDICT_INVALID
    written = json.loads((root / "RESULTS.json").read_text())
    assert any(
        "publication exploded" in record["problem"]
        for record in written["validity"]["records"]
    )


def test_every_output_write_is_atomic(tmp_path, monkeypatch):
    """A partial write must never be observable at the published path."""
    seen = []
    real_replace = os.replace

    def record(source, destination, *args, **kwargs):
        seen.append(Path(destination).name)
        return real_replace(source, destination, *args, **kwargs)

    monkeypatch.setattr(os, "replace", record)
    jpack_bin()
    root = tmp_path / "atomic"
    score.run(root)
    assert {"ATTEMPT.json", "RESULTS.json", "DETECTION-MATRIX.md"} <= set(seen)

    target = tmp_path / "partial.json"
    target.write_text("original", encoding="utf-8")
    monkeypatch.undo()

    def boom(*_args, **_kwargs):
        raise RuntimeError("write exploded mid-stream")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(RuntimeError):
        score.atomic_write_text(target, "replacement")
    assert target.read_text(encoding="utf-8") == "original"
    assert sorted(item.name for item in tmp_path.iterdir() if item.is_file()) == [
        "partial.json"
    ]


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
