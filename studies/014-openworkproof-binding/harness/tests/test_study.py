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
    """Pre-freeze the holdout is a specification, not an artifact tree.

    Round 4 moved the artifacts inside the attempt, so this looks in both places:
    the shared subtree that no longer exists at all, and every attempt directory
    this repository has published.
    """
    assert not (FIXTURES / "holdout").exists()
    attempts = sorted((STUDY / "pilots").glob("*")) if (STUDY / "pilots").is_dir() else []
    assert attempts, "the pilots directory is where published attempts live"
    for attempt in attempts:
        assert not score.holdout_fixture_root(attempt).exists(), attempt.name
        for cell in HOLDOUT["cells"]:
            assert not score.holdout_cell_directory(attempt, cell["id"]).exists(), (
                attempt.name,
                cell["id"],
            )


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


def assert_refused_but_recorded(root, error, needle):
    """A refusal still leaves a marked attempt and a terminal record (R3)."""
    assert "--include-holdout is refused" in str(error.value)
    assert needle in str(error.value)
    marker = json.loads((root / "ATTEMPT.json").read_text())
    assert marker["includeHoldout"] is True
    written = json.loads((root / "RESULTS.json").read_text())
    assert written["verdict"] == score.VERDICT_INVALID
    assert any(
        "terminated before it could publish" in record["problem"]
        for record in written["validity"]["records"]
    )
    assert not score.holdout_fixture_root(root).exists(), (
        "the refusal must build nothing"
    )
    assert not (FIXTURES / "holdout").exists(), "and nothing outside the attempt"


def test_holdout_scoring_is_refused_while_the_preregistration_is_draft(tmp_path):
    assert PINS["preregistration"]["sha256"] is None, (
        "this test describes the pre-freeze state"
    )
    root = tmp_path / "holdout-attempt"
    with pytest.raises(SystemExit) as error:
        score.run(root, include_holdout=True)
    assert_refused_but_recorded(root, error, "preregistration digest")


def test_holdout_scoring_is_refused_while_its_own_digest_is_null(tmp_path, monkeypatch):
    """Frozen preregistration is not enough: the holdout pin has to be filled."""
    assert PINS["matrixHoldout"]["sha256"] is None
    frozen = json.loads(json.dumps(PINS))
    frozen["preregistration"]["sha256"] = "00" * 32
    monkeypatch.setattr(score, "preflight_pins", lambda: frozen)
    root = tmp_path / "holdout-attempt"
    with pytest.raises(SystemExit) as error:
        score.run(root, include_holdout=True)
    assert_refused_but_recorded(root, error, "matrixHoldout digest")


def test_the_marker_precedes_pins_under_the_holdout_flag(tmp_path, monkeypatch):
    """R3: malformed PINS under `--include-holdout` used to exit before the marker."""
    root = tmp_path / "holdout-unreadable-pins"
    real = Path.read_text

    def refuse(self, *args, **kwargs):
        if self.name == "PINS.json":
            raise OSError("PINS.json is unreadable in this test")
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", refuse)
    with pytest.raises(SystemExit) as error:
        score.run(root, include_holdout=True)
    monkeypatch.undo()
    assert (root / "ATTEMPT.json").is_file()
    assert_refused_but_recorded(root, error, "preregistration digest")


def test_holdout_construction_is_refused_while_any_freeze_pin_is_null(tmp_path):
    """The scorer's construction step carries the guard itself, not by assumption.

    Called directly with the live (unfrozen) registry: it must refuse before it
    imports the builder, so no hook can run. Nothing is constructed here.
    """
    with pytest.raises(score.PipelineInvalid) as error:
        score.construct_holdout(tmp_path, HOLDOUT, PINS, jpack_bin())
    assert "refused while these freeze pins are null" in str(error.value)
    assert not score.holdout_fixture_root(tmp_path).exists()
    assert not (FIXTURES / "holdout").exists()
    assert not (tmp_path / "CONSTRUCTION.json").exists()


# --- R4-3: the builder has no holdout route of its own --------------------

def test_the_builder_has_no_holdout_command_line_route():
    """R4-3: the standalone route is gone, not merely guarded.

    A guarded flag was still a way to write holdout bytes post-freeze with no
    attempt marker, no terminal record and no complete freeze gates. The hooks
    stay; the command does not, so the scorer's attempt machinery is the only
    thing that can reach them.
    """
    import ast

    source = (STUDY / "harness" / "build_fixtures.py").read_text(encoding="utf-8")
    added = {
        node.args[0].value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and getattr(node.func, "attr", None) == "add_argument"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    }
    assert added == {"--out", "--force"}, sorted(added)
    for gone in ("build_holdout", "holdout_refusal"):
        assert not hasattr(build_fixtures, gone), gone
    with pytest.raises(SystemExit) as error:
        build_fixtures.main(["--holdout"])
    assert error.value.code == 2, "argparse refuses the flag as unrecognised"
    assert not (FIXTURES / "holdout").exists()


def test_the_only_holdout_construction_entry_point_is_the_scorers():
    """`construct_holdout` stays, reachable from the scorer and nowhere else."""
    assert callable(build_fixtures.construct_holdout)
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "build_fixtures.construct_holdout(" in source


def test_every_holdout_cell_has_an_unexecuted_builder_hook():
    """The hooks exist so the holdout is buildable, not so it is built."""
    for cell in HOLDOUT["cells"]:
        assert cell["id"] in build_fixtures.HOLDOUT_BUILDERS, cell["id"]
        assert callable(build_fixtures.HOLDOUT_BUILDERS[cell["id"]])


def test_a_constructibility_refusal_is_a_record_not_an_exception():
    """A construction upstream refuses is a finding, never a crash (R2-2)."""
    refusal = build_fixtures.ConstructibilityRefusal(
        "h02-objective-lone-surrogate", "why", "upstream said no", "ValueError"
    )
    assert refusal.as_record() == {
        "cell": "h02-objective-lone-surrogate",
        "finding": "constructibility-refusal",
        "detail": "why",
        "upstreamError": "upstream said no",
        "upstreamErrorType": "ValueError",
    }
    assert not isinstance(refusal, BaseException)


# --- R4-4: a refusal must be upstream's, in type AND in raising frame -----

def upstream_error():
    """A real exception raised *inside* the installed package, with its frame."""
    from openworkproof import repo_tools

    raw = b"not a patch\n"
    try:
        repo_tools.parse_patch_phase_a(
            raw,
            expected_patch_digest="sha256:" + "00" * 32,
            expected_patch_size_bytes=len(raw),
            declared_target_paths=["src/wrap.py"],
        )
    except Exception as error:  # noqa: BLE001 - the point of the helper
        return error
    raise AssertionError("upstream accepted a patch this test needs it to refuse")


def test_the_upstream_refusal_types_come_from_the_installed_package():
    """Collected from the package itself, not transcribed into this harness."""
    from openworkproof.acceptance import AcceptanceTransactionError
    from openworkproof.composition import AuthorizationCausalityError
    from openworkproof.policy import AuthorizationPolicyError
    from openworkproof.repo_tools import PatchError

    types = build_fixtures.upstream_refusal_types()
    for required in (
        AcceptanceTransactionError,
        AuthorizationCausalityError,
        AuthorizationPolicyError,
        PatchError,
        ValueError,
    ):
        assert required in types, required
    own = [item for item in types if item.__module__.startswith("openworkproof")]
    assert len(own) > 20, "the collection walked the package's own modules"
    assert all(issubclass(item, BaseException) for item in types)
    assert KeyboardInterrupt not in types and SystemExit not in types


def test_a_harness_side_error_is_never_a_constructibility_refusal():
    """R4-4: the type alone proves nothing — this `ValueError` is the harness's."""
    try:
        raise ValueError("the harness failed while preparing the construction")
    except ValueError as error:
        harness_side = error
    assert isinstance(harness_side, build_fixtures.upstream_refusal_types())
    assert build_fixtures.upstream_refusal("h-synthetic", "why", harness_side) is None
    frame = build_fixtures.raising_frame_file(harness_side)
    assert frame == Path(__file__).resolve()


def test_an_exception_raised_inside_the_installed_package_is_a_refusal():
    """R4-4: type + raising frame inside the installed package, both satisfied."""
    error = upstream_error()
    root = verify.installed_package_root()
    frame = build_fixtures.raising_frame_file(error)
    assert root == frame.parent or root in frame.parents, frame
    refusal = build_fixtures.upstream_refusal("h-synthetic", "narrative", error)
    assert isinstance(refusal, build_fixtures.ConstructibilityRefusal)
    assert refusal.upstream_error == str(error)
    assert refusal.error_type == type(error).__name__
    assert refusal.detail == "narrative"


def test_a_harness_failure_in_a_hook_is_recorded_as_a_harness_error(monkeypatch):
    """End to end: a hook that fails harness-side is a validity problem.

    No registered hook runs — a synthetic one stands in, and the shared build
    context is stubbed, so nothing is constructed and no holdout cell is touched.
    """
    monkeypatch.setattr(build_fixtures, "_holdout_context", lambda *a, **k: {})

    def hook(_context):
        raise ValueError("a temporary file could not be written")

    monkeypatch.setitem(build_fixtures.HOLDOUT_BUILDERS, "h-synthetic", hook)
    payloads, records = build_fixtures.build_holdout_records(
        jpack_bin(), None, None, ["h-synthetic"]
    )
    assert payloads == {}
    assert records["h-synthetic"]["status"] == "harness-error"
    assert "ValueError" in records["h-synthetic"]["harnessError"]
    assert "upstreamError" not in records["h-synthetic"]


def test_a_captured_upstream_refusal_in_a_hook_is_recorded_as_refused(monkeypatch):
    """The other half: an exception from inside the package is a finding."""
    monkeypatch.setattr(build_fixtures, "_holdout_context", lambda *a, **k: {})

    def hook(_context):
        refusal = build_fixtures.upstream_refusal(
            "h-synthetic", "upstream declined the registered construction",
            upstream_error(),
        )
        assert refusal is not None
        return refusal

    monkeypatch.setitem(build_fixtures.HOLDOUT_BUILDERS, "h-synthetic", hook)
    payloads, records = build_fixtures.build_holdout_records(
        jpack_bin(), None, None, ["h-synthetic"]
    )
    assert payloads == {}
    record = records["h-synthetic"]
    assert record["status"] == "refused"
    assert record["upstreamErrorType"] == "PatchError"
    assert record["upstreamError"]


@pytest.mark.parametrize("hook_name", ["holdout_h02", "holdout_h03", "holdout_h07"])
def test_every_catching_hook_routes_through_the_refusal_test(hook_name):
    """R4-4, structurally: no hook may mint a refusal from a bare `except`.

    The hooks stay unexecuted before the freeze, so this reads their bodies: a
    hook that catches must hand the exception to `upstream_refusal` and re-raise
    when it comes back None. A direct `ConstructibilityRefusal(...)` inside a
    handler — the round-3 shape — fails here.
    """
    import ast

    source = (STUDY / "harness" / "build_fixtures.py").read_text(encoding="utf-8")
    body = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == hook_name
    )
    handlers = [node for node in ast.walk(body) if isinstance(node, ast.ExceptHandler)]
    assert handlers, hook_name
    for handler in handlers:
        assert isinstance(handler.type, ast.Name) and handler.type.id == "Exception", (
            "a hook may not catch BaseException"
        )
        called = {
            getattr(node.func, "id", getattr(node.func, "attr", None))
            for node in ast.walk(handler)
            if isinstance(node, ast.Call)
        }
        assert "upstream_refusal" in called, hook_name
        assert "ConstructibilityRefusal" not in called, hook_name
        assert any(isinstance(node, ast.Raise) for node in ast.walk(handler)), hook_name


# --- R4-5: an interruption is not a construction outcome ------------------

@pytest.mark.parametrize("interruption", [KeyboardInterrupt, SystemExit])
def test_construction_never_swallows_an_interruption(monkeypatch, interruption):
    """R4-5: both construction catches are `Exception`, so these propagate."""
    def interrupt(*_args, **_kwargs):
        raise interruption("interrupted in this test")

    monkeypatch.setattr(build_fixtures, "_holdout_context", interrupt)
    with pytest.raises(interruption):
        build_fixtures.build_holdout_records(jpack_bin(), None, None, ["h-synthetic"])

    monkeypatch.setattr(build_fixtures, "_holdout_context", lambda *a, **k: {})
    monkeypatch.setitem(build_fixtures.HOLDOUT_BUILDERS, "h-synthetic", interrupt)
    with pytest.raises(interruption):
        build_fixtures.build_holdout_records(jpack_bin(), None, None, ["h-synthetic"])


def test_an_interruption_inside_construction_lands_the_scorers_terminal_record(
    tmp_path, monkeypatch
):
    """R4-5, end to end: the scorer records the attempt and re-raises.

    The freeze gates are stubbed open so the construction step is reached at all,
    and the shared build context raises `KeyboardInterrupt` — so no hook runs and
    nothing is built. What is asserted is that the interruption travelled all the
    way out to the scorer's terminal path instead of being recorded as eight
    cells' worth of `harness-error`.
    """
    jpack_bin()
    frozen = json.loads(json.dumps(PINS))
    for member in score.FREEZE_PIN_MEMBERS:
        frozen[member]["sha256"] = "00" * 32
    monkeypatch.setattr(score, "preflight_pins", lambda: frozen)
    monkeypatch.setattr(score, "unfilled_freeze_pins", lambda pins: [])

    def interrupt(*_args, **_kwargs):
        raise KeyboardInterrupt("interrupted inside construction")

    monkeypatch.setattr(build_fixtures, "_holdout_context", interrupt)
    root = tmp_path / "interrupted-construction"
    with pytest.raises(KeyboardInterrupt):
        score.run(root, include_holdout=True)
    written = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
    assert written["verdict"] == score.VERDICT_INVALID
    assert any(
        "terminated before it could publish" in record["problem"]
        and "KeyboardInterrupt" in record["problem"]
        for record in written["validity"]["records"]
    )
    assert not score.holdout_fixture_root(root).exists()
    assert not (root / "CONSTRUCTION.json").exists()
    assert not (FIXTURES / "holdout").exists()


# --- R3: constructibility is adjudicated from a persisted record ----------

@pytest.mark.parametrize("hook", ["holdout_h01", "holdout_h06"])
def test_the_artifact_hooks_copy_frozen_bytes_and_run_no_flow(hook):
    """h01/h06 register an artifact edit, so they must not rebuild a chain.

    Proved structurally, because the hooks stay **unexecuted** before the freeze:
    the hook's own body is parsed and every function it calls is compared against
    what an artifact construction is allowed to do. A hook that re-signed a chain
    would call `flow_cell` (or reach the shared build context) and fail here. The
    round-2 hooks did exactly that, under a fresh salt.
    """
    import ast

    source = (STUDY / "harness" / "build_fixtures.py").read_text(encoding="utf-8")
    body = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == hook
    )
    called = {
        getattr(node.func, "id", getattr(node.func, "attr", None))
        for node in ast.walk(body)
        if isinstance(node, ast.Call)
    }
    assert "frozen_cell_payload" in called, "an artifact hook starts from frozen bytes"
    forbidden = {"flow_cell", "run_flow", "_holdout_context", "decide", "commitment_for"}
    assert called & forbidden == set(), sorted(called & forbidden)


def test_frozen_cell_payload_returns_the_committed_bytes_verbatim():
    """The helper both artifact hooks start from: a byte-for-byte read, no build.

    Reads locked-stratum fixtures only; nothing holdout is constructed here.
    """
    payload = build_fixtures.frozen_cell_payload("pos-baseline")
    assert payload is not None
    for name in verify.CELL_FILES:
        path = BASELINE / name
        assert payload[name] == (path.read_bytes() if path.is_file() else None), name
    assert build_fixtures.frozen_cell_payload("h-never-built") is None


def test_a_construction_record_is_written_for_every_outcome(tmp_path):
    """Built, refused and harness-error all persist a record. No hooks run here."""
    digest = build_fixtures.builder_version_digest()
    refusal = build_fixtures.ConstructibilityRefusal("h02", "narrative", "verbatim", "IOError")
    records = {
        "built-cell": build_fixtures.construction_record("built-cell", "built"),
        "refused-cell": build_fixtures.construction_record(
            "refused-cell", "refused", upstream=refusal
        ),
        "broken-cell": build_fixtures.construction_record(
            "broken-cell", "harness-error", harness_error="BuildError: no baseline"
        ),
    }
    assert records["refused-cell"]["upstreamError"] == "verbatim"
    assert records["broken-cell"]["harnessError"].startswith("BuildError")
    assert all(item["builderVersionDigest"] == digest for item in records.values())

    payloads = {"built-cell": {name: b"x" for name in verify.CELL_FILES}}
    # The publication root is the attempt's own holdout subtree (R4-2), so the
    # cell directories sit directly under it and nowhere near `fixtures/`.
    build_fixtures.publish_holdout(tmp_path, list(records), payloads, records)
    for cell_id in records:
        written = json.loads(
            (
                tmp_path / cell_id / build_fixtures.CONSTRUCTION_RECORD_NAME
            ).read_text(encoding="utf-8")
        )
        assert written == records[cell_id], cell_id
    assert (tmp_path / "built-cell" / verify.MANIFEST_NAME).is_file()
    assert not (tmp_path / "refused-cell" / verify.MANIFEST_NAME).exists()
    assert not (FIXTURES / "holdout").exists()


@pytest.mark.parametrize(
    "status,expect_finding,needle",
    [
        ("refused", True, "upstream refused"),
        ("harness-error", False, "failed inside this harness"),
        ("absent", False, "carries no construction record"),
        ("uncaptured", False, "carries no upstream error"),
    ],
)
def test_only_a_captured_upstream_refusal_is_a_constructibility_finding(
    tmp_path, status, expect_finding, needle
):
    """R3: absence, a crash, and an unevidenced refusal are validity problems."""
    directory = tmp_path / "cell"
    directory.mkdir()
    if status == "refused":
        record = build_fixtures.construction_record(
            "h02",
            "refused",
            upstream=build_fixtures.ConstructibilityRefusal(
                "h02", "narrative", "OpenWorkProof said no", "ValueError"
            ),
        )
    elif status == "harness-error":
        record = build_fixtures.construction_record(
            "h02", "harness-error", harness_error="BuildError: no baseline"
        )
    elif status == "uncaptured":
        record = {"cell": "h02", "status": "refused", "upstreamError": ""}
    else:
        record = None
    if record is not None:
        build_fixtures.write_construction_record(directory, record)

    problems, finding = score.construction_problems("h02", directory)
    assert problems and any(needle in problem for problem in problems)
    assert (finding is not None) == expect_finding
    if expect_finding:
        assert finding["upstreamError"] == "OpenWorkProof said no"
        assert "OpenWorkProof said no" in problems[0]

    validity = []
    row = score.adjudicate_cell(
        HOLDOUT["cells"][0], jpack_bin(), None, validity,
        directory=directory, scope="holdout",
    )
    assert row["status"] == score.NOT_ADJUDICATED
    assert row["divergences"] == []
    assert ("constructibility" in row) == expect_finding
    assert all(record["stratum"] == "holdout" for record in validity)
    assert all(("finding" in record) == expect_finding for record in validity)


def test_a_built_record_hands_the_cell_to_the_ordinary_ceremony(tmp_path):
    """`status: built` must not short-circuit anything — the cell is adjudicated."""
    directory = tmp_path / "built"
    shutil.copytree(BASELINE, directory)
    build_fixtures.write_construction_record(
        directory, build_fixtures.construction_record("h-synthetic", "built")
    )
    assert score.construction_problems("h-synthetic", directory) == (None, None)
    work_root = tmp_path / "work"
    work_root.mkdir()
    validity = []
    cell = json.loads(json.dumps(HOLDOUT["cells"][0]))
    cell["expected"] = {"owp": "pass", "binding": "pass", "replay": "pass"}
    row = score.adjudicate_cell(
        cell, jpack_bin(), work_root, validity,
        directory=directory, scope="holdout",
    )
    assert row["status"] == "adjudicated", row["problems"]
    assert row["divergences"] == []


def test_the_holdout_stratum_is_published_as_its_own_section(tmp_path):
    """The post-freeze path, exercised without executing a single holdout cell.

    Every holdout fixture is deliberately absent pre-freeze, so this adjudicates
    the stratum in exactly the state it is in: eight constructibility findings.
    What it asserts is the *separation* — a holdout summary of its own, a second
    table in the published matrix, and no holdout row anywhere in the locked
    stratum's counts or in the R1 verdict.
    """
    holdout = score.adjudicate_holdout(tmp_path / "unbuilt", HOLDOUT, jpack_bin(), None, [])
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


# --- R4-2: the holdout bytes are attempt-local and attempt-bound ----------

def frozen_pins():
    """A PINS copy with every freeze pin filled. Used to reach guarded paths."""
    frozen = json.loads(json.dumps(PINS))
    for member in score.FREEZE_PIN_MEMBERS:
        frozen[member]["sha256"] = "00" * 32
    return frozen


def test_holdout_construction_writes_inside_the_attempt_and_stamps_digests(
    tmp_path, monkeypatch
):
    """R4-2: the bytes live in the attempt, and the attempt says which bytes.

    The builder entry point is stubbed — no registered hook runs and nothing
    upstream is driven — with a stand-in that writes one built cell and one
    unbuilt cell exactly where the scorer tells it to. What is asserted is the
    location and the binding: `<attempt>/holdout-fixtures/<id>/`, and a digest of
    every per-cell manifest and construction record in the attempt's own record.
    """
    attempt = tmp_path / "attempt"
    attempt.mkdir()
    seen = {}

    def stub(binary, out_root, owp_source, cell_ids):
        seen["out_root"] = Path(out_root)
        records = {}
        for index, cell_id in enumerate(cell_ids):
            directory = Path(out_root) / cell_id
            directory.mkdir(parents=True)
            if index == 0:
                (directory / "bundle.json").write_bytes(b"{}\n")
                (directory / verify.MANIFEST_NAME).write_text(
                    verify.manifest_text(directory), encoding="utf-8"
                )
                records[cell_id] = build_fixtures.construction_record(cell_id, "built")
            else:
                records[cell_id] = build_fixtures.construction_record(
                    cell_id, "harness-error", harness_error="not attempted in this test"
                )
            build_fixtures.write_construction_record(directory, records[cell_id])
        return records

    monkeypatch.setattr(build_fixtures, "construct_holdout", stub)
    published = score.construct_holdout(attempt, HOLDOUT, frozen_pins(), jpack_bin())

    assert seen["out_root"] == attempt / "holdout-fixtures"
    assert published["fixtureRoot"] == score.HOLDOUT_FIXTURE_DIRECTORY
    cell_ids = [cell["id"] for cell in HOLDOUT["cells"]]
    digests = published["fixtureDigests"]
    assert sorted(digests) == sorted(cell_ids)
    for index, cell_id in enumerate(cell_ids):
        directory = score.holdout_cell_directory(attempt, cell_id)
        assert directory.is_dir()
        record = directory / score.CONSTRUCTION_RECORD_NAME
        assert digests[cell_id]["constructionSha256"] == verify.sha256_file(record)
        manifest = directory / verify.MANIFEST_NAME
        if index == 0:
            assert digests[cell_id]["manifestSha256"] == verify.sha256_file(manifest)
        else:
            assert digests[cell_id]["manifestSha256"] is None
            assert not manifest.exists()
    written = json.loads(
        (attempt / score.CONSTRUCTION_RECORD_NAME).read_text(encoding="utf-8")
    )
    assert written["fixtureDigests"] == digests
    assert not (FIXTURES / "holdout").exists(), "nothing is written outside the attempt"


def test_the_attempt_record_publishes_the_holdout_fixture_digests(tmp_path, monkeypatch):
    """R4-2: the digests reach `RESULTS.json`, not only `CONSTRUCTION.json`.

    Construction and holdout adjudication are both stubbed, so no holdout cell is
    built and none is adjudicated; the locked stratum runs normally underneath.
    """
    jpack_bin()
    canned = {
        "study": "014-openworkproof-binding",
        "stratum": "reviewer-holdout",
        "fixtureRoot": score.HOLDOUT_FIXTURE_DIRECTORY,
        "builderVersionDigest": build_fixtures.builder_version_digest(),
        "records": [],
        "fixtureDigests": {
            "h01-retained-commitment-noncanonical": {
                "manifestSha256": "ab" * 32,
                "constructionSha256": "cd" * 32,
            }
        },
    }
    monkeypatch.setattr(score, "preflight_pins", frozen_pins)
    monkeypatch.setattr(score, "unfilled_freeze_pins", lambda pins: [])
    monkeypatch.setattr(score, "construct_holdout", lambda *a, **k: canned)
    monkeypatch.setattr(
        score, "adjudicate_holdout", lambda *a, **k: score.holdout_summary([])
    )
    root = tmp_path / "digest-stamped"
    results = score.run(root, include_holdout=True)
    assert results["holdout"]["fixtureDigests"] == canned["fixtureDigests"]
    assert results["holdout"]["fixtureRoot"] == score.HOLDOUT_FIXTURE_DIRECTORY
    written = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
    assert written["holdout"]["fixtureDigests"] == canned["fixtureDigests"]


def test_an_absent_holdout_fixture_is_a_validity_problem_not_a_finding(tmp_path):
    """R3: absence proves nothing, so it may not be credited as a finding."""
    validity = []
    row = score.adjudicate_cell(
        HOLDOUT["cells"][0],
        jpack_bin(),
        None,
        validity,
        directory=score.holdout_cell_directory(tmp_path, HOLDOUT["cells"][0]["id"]),
        scope="holdout",
    )
    assert row["status"] == score.NOT_ADJUDICATED
    assert row["stratum"] == "holdout"
    assert "constructibility" not in row
    assert any("carries no construction record" in problem for problem in row["problems"])
    assert validity and validity[0]["stratum"] == "holdout"
    assert all("finding" not in record for record in validity)


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
        "harness/owpflow.py",
        "harness/build_fixtures.py",
        "harness/score.py",
        "fixtures/baseline/MANIFEST.sha256",
    ):
        assert required in covered, required
    manifests = [item for item in covered if item.endswith("MANIFEST.sha256")]
    assert len(manifests) == len(MATRIX["cells"])


# --- R3: the anchor is linear, so the manifest excludes two things -------

def test_the_study_manifest_does_not_cover_the_pin_registry():
    """The round-2 cycle, closed: PINS pins the manifest, so it is not inside it."""
    covered = make_manifest.manifest_entries()
    assert "harness/PINS.json" not in covered
    assert "harness/PINS.json" in make_manifest.EXCLUDED_DOCUMENTS
    assert "harness/STUDY-MANIFEST.sha256" not in covered, (
        "the manifest must not cover itself either"
    )
    # And the registry says which manifest digest it pins.
    assert PINS["studyManifest"]["path"] == "harness/STUDY-MANIFEST.sha256"


def test_the_study_manifest_excludes_holdout_fixtures(tmp_path, monkeypatch):
    """The exclusion is now a guard: nothing writes under `fixtures/holdout/`.

    Round 4 moved holdout construction into the attempt, so the subtree does not
    exist at all and attempt directories were never covered by this manifest.
    The exclusion stays so that re-introducing a shared holdout tree cannot
    invalidate the frozen exact set — or quietly enter it — which is what this
    synthesizes and then removes.
    """
    assert make_manifest.EXCLUDED_FIXTURE_ROOTS == ("fixtures/holdout",)
    holdout = FIXTURES / "holdout" / "h99-synthetic"
    assert not (FIXTURES / "holdout").exists(), "no holdout fixture lives under fixtures/"
    holdout.mkdir(parents=True)
    try:
        (holdout / verify.MANIFEST_NAME).write_text("00  bundle.json\n", encoding="utf-8")
        assert "fixtures/holdout/h99-synthetic/MANIFEST.sha256" not in (
            make_manifest.manifest_entries()
        )
        assert make_manifest.manifest_problems() == [], (
            "a newly built holdout fixture must not invalidate the frozen manifest"
        )
    finally:
        shutil.rmtree(FIXTURES / "holdout")


def test_registered_requires_every_freeze_pin(tmp_path):
    """R3: a frozen preregistration alone must not authorize a REGISTERED run."""
    assert score.attempt_label(PINS) == "PILOT"
    assert set(score.unfilled_freeze_pins(PINS)) == set(score.FREEZE_PIN_MEMBERS)

    partly = json.loads(json.dumps(PINS))
    partly["preregistration"]["sha256"] = "00" * 32
    assert score.attempt_label(partly) == "PILOT", (
        "the preregistration digest alone must not make an attempt REGISTERED"
    )
    for member in score.FREEZE_PIN_MEMBERS:
        one_null = {name: {"sha256": "00" * 32} for name in score.FREEZE_PIN_MEMBERS}
        one_null[member] = {"sha256": None}
        assert score.attempt_label(one_null) == "PILOT", member
    filled = {name: {"sha256": "00" * 32} for name in score.FREEZE_PIN_MEMBERS}
    assert score.attempt_label(filled) == "REGISTERED"


def test_a_pilot_attempt_is_labelled_pilot_in_its_marker(tmp_path):
    jpack_bin()
    root = tmp_path / "labelled"
    results = score.run(root)
    assert results["attemptLabel"] == "PILOT"
    assert json.loads((root / "ATTEMPT.json").read_text())["attemptLabel"] == "PILOT"


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


# --- R3: the last terminal paths ------------------------------------------

@pytest.mark.parametrize("include_holdout", [False, True])
def test_the_marker_precedes_pins_under_every_flag(tmp_path, monkeypatch, include_holdout):
    """The marker is written before PINS is read, whichever way the scorer is run."""
    root = tmp_path / ("marker-first-%s" % include_holdout)
    seen = []
    real_write = score.atomic_write_text
    real_preflight = score.preflight_pins

    def record_write(path, text):
        seen.append(Path(path).name)
        return real_write(path, text)

    def record_preflight():
        seen.append("PINS-read")
        return real_preflight()

    monkeypatch.setattr(score, "atomic_write_text", record_write)
    monkeypatch.setattr(score, "preflight_pins", record_preflight)
    try:
        score.run(root, include_holdout=include_holdout)
    except SystemExit:
        pass  # the pre-freeze holdout refusal; the ordering is what is asserted
    assert seen[0] == "ATTEMPT.json", seen[:3]
    assert "PINS-read" in seen and seen.index("ATTEMPT.json") < seen.index("PINS-read")


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, SystemExit])
def test_an_interruption_lands_a_terminal_record_and_is_re_raised(
    tmp_path, monkeypatch, interruption
):
    """R3: `SystemExit`/`KeyboardInterrupt` escaped the catch entirely."""
    root = tmp_path / ("interrupted-" + interruption.__name__)

    def interrupt(*_args, **_kwargs):
        raise interruption("interrupted in this test")

    monkeypatch.setattr(score, "adjudicate_cell", interrupt)
    with pytest.raises(interruption):
        score.run(root)
    assert (root / "ATTEMPT.json").is_file()
    written = json.loads((root / "RESULTS.json").read_text())
    assert written["verdict"] == score.VERDICT_INVALID
    assert any(
        "terminated before it could publish" in record["problem"]
        and interruption.__name__ in record["problem"]
        for record in written["validity"]["records"]
    )


def test_a_marker_write_failure_is_reported_and_nothing_else_is_attempted(
    tmp_path, monkeypatch, capsys
):
    """The one failure with nowhere to record itself: it must still be loud."""
    root = tmp_path / "no-marker"

    def explode(*_args, **_kwargs):
        raise OSError("the marker write exploded in this test")

    monkeypatch.setattr(score, "atomic_write_text", explode)
    monkeypatch.setattr(
        score, "write_outputs", lambda *a, **k: pytest.fail("nothing else may run")
    )
    with pytest.raises(SystemExit) as error:
        score.run(root)
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "the attempt marker could not be written" in captured.err
    assert "nothing further was attempted" in captured.err
    assert not (root / "RESULTS.json").exists()


def test_a_fallback_publication_failure_is_reported_non_silently(
    tmp_path, monkeypatch, capsys
):
    """The atomic write failing *inside* the catch used to end the attempt silently."""
    root = tmp_path / "fallback-fails"
    real_write = score.atomic_write_text

    def marker_only(path, text):
        # The marker still lands; the terminal record's own write is what fails.
        if Path(path).name == "ATTEMPT.json":
            return real_write(path, text)
        raise OSError("every publication write explodes in this test")

    def explode(*_args, **_kwargs):
        raise RuntimeError("the gate exploded in this test")

    monkeypatch.setattr(score, "atomic_write_text", marker_only)
    monkeypatch.setattr(score, "pin_problems", explode)
    with pytest.raises(OSError):
        score.run(root)
    captured = capsys.readouterr()
    assert "terminal pipeline-invalid record could not be published" in captured.err
    assert "the problems it would have recorded were" in captured.err
    assert "the gate exploded in this test" in captured.err


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

# --- R3: OWP_SOURCE is pinned, not merely present -------------------------

def test_the_pinned_clone_is_the_one_the_builder_imports(source):
    """The live clone satisfies commit, cleanliness and every helper digest."""
    import owpflow

    assert owpflow.upstream_problems(source) == []
    helpers = PINS["openworkproof"]["upstreamHelpers"]
    assert helpers["commit"] == PINS["openworkproof"]["commit"]
    assert set(helpers["files"]) == set(owpflow.UPSTREAM_HELPER_FILES)
    for name, digest in helpers["files"].items():
        assert verify.sha256_file(Path(source) / name) == digest, name


@pytest.mark.parametrize(
    "mutate,needle",
    [
        (lambda pins: pins["openworkproof"]["upstreamHelpers"].__setitem__(
            "commit", "0" * 40), "pinned"),
        (lambda pins: pins["openworkproof"]["upstreamHelpers"]["files"].__setitem__(
            "tests/conftest.py", "ab" * 32),
         "does not match its digest"),
        (lambda pins: pins["openworkproof"]["upstreamHelpers"]["files"].pop(
            "tests/test_receipt_chain.py"), "unpinned"),
        (lambda pins: pins["openworkproof"]["upstreamHelpers"]["files"].__setitem__(
            "tests/test_policy.py", "ab" * 32), "does not import"),
        (lambda pins: pins["openworkproof"].__setitem__("upstreamHelpers", {}),
         "pins no upstream helper file digests"),
    ],
)
def test_an_unpinned_or_drifted_clone_is_refused(source, mutate, needle):
    """Each check stands on its own: any one failing refuses the build."""
    import owpflow

    broken = json.loads(json.dumps(PINS))
    mutate(broken)
    problems = owpflow.upstream_problems(source, broken)
    assert any(needle in problem for problem in problems), problems


def test_a_dirty_clone_is_refused(source, monkeypatch):
    """Modified tracked files refuse; untracked paths are deliberately ignored."""
    import owpflow

    real = owpflow._git

    def dirty(root, *arguments):
        if arguments[:1] == ("status",):
            return " M tests/conftest.py\n?? build/\n"
        return real(root, *arguments)

    monkeypatch.setattr(owpflow, "_git", dirty)
    problems = owpflow.upstream_problems(source)
    assert any("modified tracked files" in problem for problem in problems)
    assert not any("build/" in problem for problem in problems)

    def untracked_only(root, *arguments):
        if arguments[:1] == ("status",):
            return "?? build/\n?? notes.txt\n"
        return real(root, *arguments)

    monkeypatch.setattr(owpflow, "_git", untracked_only)
    assert owpflow.upstream_problems(source) == []


# --- R4-1: untracked is not harmless under a prepended import root --------

def test_an_import_capable_untracked_path_under_an_import_root_is_refused(
    source, tmp_path, monkeypatch
):
    """R4-1: `<clone>/tests` goes on `sys.path`, so untracked inverts there.

    The shadow is staged in a temporary tree, never in the pinned clone, and the
    classifier is asked about it directly; the refusal itself is then exercised
    against the real clone with the untracked listing monkeypatched.
    """
    import owpflow

    assert owpflow.IMPORT_ROOTS == ("tests",)
    (tmp_path / "tests" / "openworkproof").mkdir(parents=True)
    (tmp_path / "tests" / "openworkproof" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "tests" / "openworkproof" / "signing.py").write_text("", encoding="utf-8")
    (tmp_path / "tests" / "data").mkdir()
    (tmp_path / "tests" / "data" / "notes.txt").write_text("", encoding="utf-8")
    (tmp_path / "build" / "lib" / "openworkproof").mkdir(parents=True)
    (tmp_path / "build" / "lib" / "openworkproof" / "__init__.py").write_text(
        "", encoding="utf-8"
    )
    listing = [
        "tests/openworkproof/__init__.py",
        "tests/openworkproof/signing.py",
        "tests/data/notes.txt",
        "build/lib/openworkproof/__init__.py",
    ]
    shadows = owpflow.import_shadow_paths(tmp_path, listing)
    assert shadows == ["tests/openworkproof/__init__.py", "tests/openworkproof/signing.py"]

    # A directory-shaped untracked entry (git names it once, so the `*.py` rule
    # above never sees inside it) is caught by the `__init__.py` rule.
    assert owpflow.import_shadow_paths(tmp_path, ["tests/openworkproof"]) == [
        "tests/openworkproof/"
    ]
    assert owpflow.import_shadow_paths(tmp_path, ["tests/data"]) == []

    monkeypatch.setattr(owpflow, "_untracked_paths", lambda root: listing)
    problems = owpflow.upstream_problems(source)
    assert any("import-capable untracked paths" in problem for problem in problems)
    assert any("tests/openworkproof/__init__.py" in problem for problem in problems)
    assert not any("build/lib" in problem for problem in problems)


def test_git_reports_a_shadow_even_when_it_is_ignored(tmp_path):
    """The listing is `--others` without `--exclude-standard`, and it matters.

    Staged in a throwaway repository, never in the pinned clone: an ignored
    shadow is still an importable shadow, and the ignore rule that hides it can
    live in `.git/info/exclude`, which no tracked-file check can see.
    """
    import owpflow

    repository = tmp_path / "clone"
    (repository / "tests").mkdir(parents=True)
    (repository / "tests" / "conftest.py").write_text("", encoding="utf-8")
    for arguments in (
        ["init", "-q"],
        ["add", "tests/conftest.py"],
        ["-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-qm", "x"],
    ):
        subprocess.run(["git", "-C", str(repository)] + arguments, check=True,
                       capture_output=True)
    (repository / ".git" / "info" / "exclude").write_text(
        "tests/openworkproof/\n", encoding="utf-8"
    )
    (repository / "tests" / "openworkproof").mkdir()
    (repository / "tests" / "openworkproof" / "__init__.py").write_text(
        "", encoding="utf-8"
    )

    assert subprocess.run(
        ["git", "-C", str(repository), "status", "--porcelain"],
        capture_output=True, text=True,
    ).stdout == "", "the shadow is invisible to the cleanliness check"
    untracked = owpflow._untracked_paths(repository)
    assert "tests/openworkproof/__init__.py" in untracked
    assert owpflow.import_shadow_paths(repository, untracked) == [
        "tests/openworkproof/__init__.py"
    ]


def test_the_live_clone_carries_untracked_paths_but_no_import_shadow(source):
    """The check is scoped, not blanket: this clone has an untracked package.

    `build/lib/openworkproof/` is untracked and import-capable in shape, and is
    never on `sys.path` — so it is exactly the case the round-3 rule was written
    for, and it must keep passing.
    """
    import owpflow

    untracked = owpflow._untracked_paths(source)
    assert untracked, "the pinned clone is expected to carry untracked build output"
    assert any(item.startswith("build/") and item.endswith(".py") for item in untracked)
    assert owpflow.import_shadow_paths(source, untracked) == []
    assert owpflow.upstream_problems(source) == []


def test_an_unreadable_untracked_listing_is_itself_a_refusal(source, monkeypatch):
    """If git cannot answer, the import roots are unproven — that is a refusal."""
    import owpflow

    monkeypatch.setattr(owpflow, "_untracked_paths", lambda root: None)
    problems = owpflow.upstream_problems(source)
    assert any("untracked paths could not be read" in problem for problem in problems)


def test_the_loaded_openworkproof_must_be_the_installed_package(tmp_path, monkeypatch):
    """R4-1's second half: whatever `sys.path` did, the module must be the pin."""
    import types

    import owpflow

    assert owpflow.loaded_package_problems() == []

    shadow = tmp_path / "openworkproof"
    shadow.mkdir()
    (shadow / "__init__.py").write_text("", encoding="utf-8")
    fake = types.ModuleType("openworkproof")
    fake.__file__ = str(shadow / "__init__.py")
    monkeypatch.setitem(sys.modules, "openworkproof", fake)
    problems = owpflow.loaded_package_problems()
    assert any(
        "outside the installed package directory" in problem for problem in problems
    )
    monkeypatch.undo()

    drifted = json.loads(json.dumps(PINS))
    drifted["openworkproof"]["installedPackageDigest"] = "ab" * 32
    problems = owpflow.loaded_package_problems(drifted)
    assert any("no longer matches its pinned digest" in problem for problem in problems)

    unpinned = json.loads(json.dumps(PINS))
    unpinned["openworkproof"].pop("installedPackageDigest")
    problems = owpflow.loaded_package_problems(unpinned)
    assert any("carries no installed openworkproof package digest" in problem
               for problem in problems)


def test_load_upstream_refuses_a_package_that_is_not_the_installed_one(
    source, monkeypatch
):
    """The post-import check is a refusal to build, not a note in a log."""
    import owpflow

    monkeypatch.setattr(owpflow, "_UPSTREAM", {})
    monkeypatch.setattr(
        owpflow, "loaded_package_problems", lambda *a, **k: ["synthetic shadow"]
    )
    before = list(sys.path)
    with pytest.raises(owpflow.FlowError) as error:
        owpflow.load_upstream(source)
    assert "is not the pinned installed one" in str(error.value)
    assert "synthetic shadow" in str(error.value)
    assert sys.path == before, "a refused import must not leave its roots on sys.path"
    assert owpflow._UPSTREAM == {}, "and must not register the helpers it loaded"


def test_the_installed_package_pin_has_one_implementation(source):
    """The builder re-verifies the pin the scorer enforces, from the same code."""
    import owpflow

    assert (
        verify.installed_package_digest()
        == score.installed_package_digest()
        == PINS["openworkproof"]["installedPackageDigest"]
    )
    root = verify.installed_package_root()
    assert verify.installed_package_digest(root=root) == score.installed_package_digest()
    assert owpflow.loaded_package_problems() == []


def test_load_upstream_refuses_before_it_imports_anything(tmp_path, monkeypatch):
    """The refusal is a refusal to build, not a warning printed on the way in."""
    import owpflow

    monkeypatch.setattr(owpflow, "_UPSTREAM", {})
    monkeypatch.setattr(
        owpflow, "upstream_problems", lambda root, pins=None: ["synthetic drift"]
    )
    before = list(sys.path)
    with pytest.raises(owpflow.FlowError) as error:
        owpflow.load_upstream(str(tmp_path))
    assert "not the pinned one" in str(error.value)
    assert "synthetic drift" in str(error.value)
    assert sys.path == before, "a refused clone must not reach sys.path"


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
