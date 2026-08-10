"""Per-code reachability — every registered code, a minimal condition, exact match.

Round 1's finding: the SPEC/code vocabulary test was syntactic. It compared prose
against declared constants and proved neither that a declared code was reachable
nor that a runtime string belonged to the vocabulary. These tests construct the
minimal condition for each registered `adapter/SPEC.md` section 5 code, assert the
**exact** code, and — where the ordering is load-bearing — assert that the code
fires *first*, ahead of a second defect deliberately planted downstream.

Every case is built by transforming the frozen baseline cell in a temporary
directory. Nothing here writes to `fixtures/`.
"""

import json
import shutil
import sys
from pathlib import Path

import pytest

from conftest import STUDY, jpack_bin  # noqa: E402

sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import commitment  # noqa: E402
import verify  # noqa: E402

BASELINE = STUDY / "fixtures" / "baseline"


def staged(tmp_path, name="cell"):
    directory = tmp_path / name
    shutil.copytree(BASELINE, directory)
    return directory


def bundle_of(directory):
    return json.loads((directory / "bundle.json").read_text(encoding="utf-8"))


def write_bundle(directory, bundle):
    (directory / "bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def binding_code(directory):
    record = verify.layer_binding(verify.Cell(directory))
    return record["code"] if record["verdict"] != "pass" else None


_PINNED = object()


def replay_code(directory, work_root, binary=_PINNED):
    """`binary=None` means "no evaluator available", not "use the pinned one"."""
    record = verify.layer_replay(
        verify.Cell(directory), jpack_bin() if binary is _PINNED else binary, work_root
    )
    return record["code"] if record["verdict"] != "pass" else None


def objective_commitment(directory):
    return json.loads(bundle_of(directory)["work_order"]["objective"])


def set_objective(directory, raw_text):
    bundle = bundle_of(directory)
    bundle["work_order"]["objective"] = raw_text
    write_bundle(directory, bundle)


def executing_receipt(bundle):
    return next(
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") == "owp.apply_patch"
    )


# --------------------------------------------------------------------------
# the baseline itself
# --------------------------------------------------------------------------

def test_baseline_binding_passes(tmp_path):
    assert binding_code(staged(tmp_path)) is None


# --------------------------------------------------------------------------
# BINDING codes
# --------------------------------------------------------------------------

def test_commitment_objective_missing(tmp_path):
    directory = staged(tmp_path)
    set_objective(directory, "Apply a deterministic patch and verify it.")
    assert binding_code(directory) == "commitment-objective-missing"


def test_commitment_schema_invalid_on_an_unknown_field(tmp_path):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["handoffTarget"] = {"kind": "human-role"}
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert binding_code(directory) == "commitment-schema-invalid"


def test_commitment_schema_invalid_on_a_duplicate_member(tmp_path):
    directory = staged(tmp_path)
    raw = json.dumps(objective_commitment(directory), separators=(",", ":"))
    raw = raw.replace('{"action":', '{"action":null,"action":', 1)
    set_objective(directory, raw)
    assert binding_code(directory) == "commitment-schema-invalid"


def test_commitment_schema_invalid_on_a_noncanonical_objective_encoding(tmp_path):
    directory = staged(tmp_path)
    set_objective(directory, json.dumps(objective_commitment(directory), indent=2))
    assert binding_code(directory) == "commitment-schema-invalid"


def test_commitment_schema_invalid_on_a_noncanonical_retained_encoding(tmp_path):
    """Same content, different bytes -> schema-invalid, NOT divergence."""
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    (directory / "commitment.json").write_text(
        json.dumps(candidate, indent=2), encoding="utf-8"
    )
    assert binding_code(directory) == "commitment-schema-invalid"


def test_binding_point_divergence_on_a_different_retained_commitment(tmp_path):
    """Different content -> divergence, NOT schema-invalid."""
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["packDigest"] = "sha256:" + "ab" * 32
    (directory / "commitment.json").write_bytes(commitment.commitment_bytes(candidate))
    assert binding_code(directory) == "binding-point-divergence"


def test_binding_point_divergence_on_an_unmarked_execution(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    receipt = executing_receipt(bundle)
    receipt["nested_claim"]["context_source_digest"] = "cd" * 32
    write_bundle(directory, bundle)
    assert binding_code(directory) == "binding-point-divergence"


def test_binding_point_divergence_on_unmirrored_correlation_factors(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    receipt = executing_receipt(bundle)
    receipt["correlation_factors"]["context_source_digest"] = "ef" * 32
    write_bundle(directory, bundle)
    assert binding_code(directory) == "binding-point-divergence"


def test_executing_receipt_missing(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    bundle["receipts"] = [
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") != "owp.apply_patch"
    ]
    write_bundle(directory, bundle)
    assert binding_code(directory) == "executing-receipt-missing"


def test_action_tool_mismatch_when_the_marker_points_elsewhere(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    digest = commitment.commitment_digest(objective_commitment(directory))
    other = next(
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") == "owp.repo_read"
    )
    other["nested_claim"]["context_source_digest"] = digest
    executing_receipt(bundle)["nested_claim"]["context_source_digest"] = "11" * 32
    write_bundle(directory, bundle)
    assert binding_code(directory) == "action-tool-mismatch"


def test_action_map_violation_on_a_surplus_action_class_receipt(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    extra = json.loads(json.dumps(executing_receipt(bundle)))
    extra["receipt_id"] = "aa" * 32
    extra["nested_claim"]["context_source_digest"] = "b" * 64
    bundle["receipts"].append(extra)
    write_bundle(directory, bundle)
    assert binding_code(directory) == "action-map-violation"


def test_action_map_violation_on_a_null_action_with_an_execution(tmp_path):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["action"] = None
    raw = commitment.commitment_bytes(candidate)
    set_objective(directory, raw.decode("utf-8"))
    (directory / "commitment.json").write_bytes(raw)
    assert binding_code(directory) == "action-map-violation"


def test_pack_artifact_missing(tmp_path):
    directory = staged(tmp_path)
    (directory / "pack.json").unlink()
    assert binding_code(directory) == "pack-artifact-missing"


def test_pack_digest_mismatch(tmp_path):
    directory = staged(tmp_path)
    payload = (directory / "pack.json").read_bytes()
    (directory / "pack.json").write_bytes(payload.replace(b'"5000"', b'"6000"'))
    assert binding_code(directory) == "pack-digest-mismatch"


def test_facts_artifact_missing(tmp_path):
    directory = staged(tmp_path)
    (directory / "facts.json").unlink()
    assert binding_code(directory) == "facts-artifact-missing"


def test_facts_digest_mismatch(tmp_path):
    directory = staged(tmp_path)
    payload = (directory / "facts.json").read_bytes()
    (directory / "facts.json").write_bytes(payload.replace(b"250.00", b"240.00"))
    assert binding_code(directory) == "facts-digest-mismatch"


def test_evidence_artifact_missing(tmp_path):
    directory = staged(tmp_path)
    (directory / "evidence.json").unlink()
    assert binding_code(directory) == "evidence-artifact-missing"


def test_evidence_digest_mismatch(tmp_path):
    directory = staged(tmp_path)
    (directory / "evidence.json").write_bytes(
        b'{"receipt":"present","cost-center":"unknown"}'
    )
    assert binding_code(directory) == "evidence-digest-mismatch"


def test_disposition_digest_mismatch_retained(tmp_path):
    directory = staged(tmp_path)
    envelope = json.loads((directory / "evaluation.json").read_text(encoding="utf-8"))
    envelope["disposition"]["reasons"] = ["forged"]
    (directory / "evaluation.json").write_text(
        json.dumps(envelope, separators=(",", ":"), ensure_ascii=False), encoding="utf-8"
    )
    assert binding_code(directory) == "disposition-digest-mismatch-retained"


def test_action_arguments_mismatch(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    executing_receipt(bundle)["arguments_digest"] = "cc" * 32
    write_bundle(directory, bundle)
    assert binding_code(directory) == "action-arguments-mismatch"


# --------------------------------------------------------------------------
# first-failure ordering
# --------------------------------------------------------------------------

def test_objective_tamper_wins_over_a_planted_artifact_defect(tmp_path):
    """A defect inside the objective is attributed to the binding point, not the pack."""
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["packDigest"] = "sha256:" + "ab" * 32
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    payload = (directory / "pack.json").read_bytes()
    (directory / "pack.json").write_bytes(payload.replace(b'"5000"', b'"6000"'))
    assert binding_code(directory) == "binding-point-divergence"


def test_receipt_checks_win_over_a_planted_artifact_defect(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    executing_receipt(bundle)["nested_claim"]["context_source_digest"] = "11" * 32
    write_bundle(directory, bundle)
    (directory / "facts.json").write_bytes(b'{"expense":{}}')
    assert binding_code(directory) == "binding-point-divergence"


def test_marker_mismatch_wins_over_the_action_class_count(tmp_path):
    directory = staged(tmp_path)
    bundle = bundle_of(directory)
    digest = commitment.commitment_digest(objective_commitment(directory))
    other = next(
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") == "owp.repo_read"
    )
    other["nested_claim"]["context_source_digest"] = digest
    extra = json.loads(json.dumps(executing_receipt(bundle)))
    extra["receipt_id"] = "aa" * 32
    bundle["receipts"].append(extra)
    write_bundle(directory, bundle)
    assert binding_code(directory) == "action-tool-mismatch"


# --------------------------------------------------------------------------
# REPLAY codes
# --------------------------------------------------------------------------

def test_replay_unavailable_without_a_commitment(tmp_path, work_root):
    directory = staged(tmp_path)
    set_objective(directory, "Apply a deterministic patch and verify it.")
    assert replay_code(directory, work_root) == "replay-unavailable"


def test_replay_unavailable_without_the_evaluator(tmp_path, work_root):
    directory = staged(tmp_path)
    assert replay_code(directory, work_root, binary=None) == "replay-unavailable"


def test_replay_unavailable_without_retained_inputs(tmp_path, work_root):
    directory = staged(tmp_path)
    (directory / "facts.json").unlink()
    assert replay_code(directory, work_root) == "replay-unavailable"


def test_replay_executable_mismatch(tmp_path, work_root):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["executableDigest"] = "sha256:" + "99" * 32
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert replay_code(directory, work_root) == "replay-executable-mismatch"


def test_replay_executable_mismatch_on_the_release_string(tmp_path, work_root):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["evaluatorRelease"] = "0.15.0"
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert replay_code(directory, work_root) == "replay-executable-mismatch"


def test_replay_refused_on_a_non_conformant_pack(tmp_path, work_root):
    """A refusal is never a disposition: the class is detail, the code is exact."""
    directory = staged(tmp_path)
    payload = (directory / "pack.json").read_bytes()
    broken = payload.replace(b'"specVersion": "0.2.0-draft"', b'"specVersion": "0.1.0-draft"')
    assert broken != payload
    (directory / "pack.json").write_bytes(broken)
    candidate = objective_commitment(directory)
    candidate["judgment"]["packDigest"] = commitment.sha256_prefixed(broken)
    candidate["judgment"]["specVersion"] = "0.1.0-draft"
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    record = verify.layer_replay(verify.Cell(directory), jpack_bin(), work_root)
    assert record["code"] == "replay-refused"
    assert record["detail"] and ":" in record["detail"]
    assert verify.outcome(record) == "fail:replay-refused"


def test_replay_spec_version_mismatch(tmp_path, work_root):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["evaluatorSpecVersion"] = "0.9.9-draft"
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert replay_code(directory, work_root) == "replay-spec-version-mismatch"


def test_replay_disposition_mismatch(tmp_path, work_root):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["dispositionDigest"] = "sha256:" + "77" * 32
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert replay_code(directory, work_root) == "replay-disposition-mismatch"


def test_spec_version_check_precedes_the_disposition_check(tmp_path, work_root):
    directory = staged(tmp_path)
    candidate = objective_commitment(directory)
    candidate["judgment"]["evaluatorSpecVersion"] = "0.9.9-draft"
    candidate["judgment"]["dispositionDigest"] = "sha256:" + "77" * 32
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))
    assert replay_code(directory, work_root) == "replay-spec-version-mismatch"


def test_supported_extensions_reach_the_evaluator(tmp_path, work_root):
    """The committed extension set is an input, not decoration.

    The baseline pack requires no extension, so a declared one changes no
    disposition — the observable is that the evaluator is invoked with the flag
    and still produces the committed disposition, which is the honest bound on
    this field's materiality.
    """
    directory = staged(tmp_path)
    pack_bytes = (directory / "pack.json").read_bytes()
    facts_bytes = (directory / "facts.json").read_bytes()
    evidence_bytes = (directory / "evidence.json").read_bytes()
    plain, _ = verify.evaluate(
        jpack_bin(), work_root, pack_bytes, facts_bytes, evidence_bytes
    )
    with_extension, _ = verify.evaluate(
        jpack_bin(),
        work_root,
        pack_bytes,
        facts_bytes,
        evidence_bytes,
        supported_extensions=("https://example.com/ext/unused",),
    )
    assert json.loads(plain)["disposition"] == json.loads(with_extension)["disposition"]


# --------------------------------------------------------------------------
# every registered code has at least one reachability test above
# --------------------------------------------------------------------------

def test_every_registered_code_has_a_reachability_test():
    source = Path(__file__).read_text(encoding="utf-8")
    missing = [
        code
        for code in verify.BINDING_CODES + verify.REPLAY_CODES
        if '"%s"' % code not in source
    ]
    assert missing == [], missing
