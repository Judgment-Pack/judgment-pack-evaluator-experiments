"""Harness mechanics and controls — deterministic, offline, no network.

These tests check the machinery, not the matrix: the commitment's digest and the
canonical disposition bytes, that the verdict vocabulary in `adapter/SPEC.md`
section 5 is exactly the vocabulary the code can produce and classify
(PREREGISTRATION section 6), the disclosed controls, and that the frozen fixtures
are what the builder produces. Adjudicating the registered expectations is the
scorer's job, not a test's.

Run: JPACK_BIN=... OWP_SOURCE=... <venv>/bin/python -m pytest harness/tests -q
"""

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import commitment  # noqa: E402
import score  # noqa: E402
import verify  # noqa: E402

FIXTURES = STUDY / "fixtures"
BASELINE = FIXTURES / "baseline"
MATRIX = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
PINS = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))

NEGATIVE_CONTROLS = (
    "neg-signature",
    "neg-evidence-digest",
    "neg-parent-ref",
    "neg-action-param",
)


def jpack_bin():
    path = os.environ.get("JPACK_BIN")
    if not path or not Path(path).is_file():
        pytest.skip("JPACK_BIN is unset: the ceremony needs the pinned evaluator")
    if verify.sha256_file(path) != PINS["jpack"]["binarySha256"]:
        pytest.skip("JPACK_BIN does not match the pinned binary digest")
    return path


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
# 2. the canonical disposition bytes
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


# --------------------------------------------------------------------------
# 3. the verdict vocabulary cannot drift from the counting
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
        verdict.split("fail:")[1]
        for verdict in score.BINDING_VERDICTS
        if verdict.startswith("fail:")
    }
    classified_replay = {
        verdict.split("fail:")[1]
        for verdict in score.REPLAY_VERDICTS
        if verdict.startswith("fail:")
    }
    assert classified_binding == spec["binding"]
    assert classified_replay == spec["replay"]
    assert score.classify("replay", "fail:replay-refused:pack-not-conformant")
    assert not score.classify("binding", "fail:invented-code")


# --------------------------------------------------------------------------
# 4-6. the disclosed controls
# --------------------------------------------------------------------------

def test_positive_control_passes_every_layer():
    result = run_cell("pos-baseline")
    assert result["owp"]["verdict"] == "pass", result["owp"]["detail"]
    assert result["binding"]["verdict"] == "pass", result["binding"]["detail"]
    assert result["replay"]["verdict"] == "pass", result["replay"]["detail"]
    assert result["combined"] == "pass"


@pytest.mark.parametrize("cell_id", NEGATIVE_CONTROLS)
def test_negative_controls_fail_the_owp_layer(cell_id):
    result = run_cell(cell_id)
    assert result["owp"]["verdict"] == "fail", result["owp"]["detail"]


def test_unsigned_metadata_carriage_is_green_to_owp_and_unbound_to_the_adapter():
    result = run_cell("m28-unsigned-metadata-carriage")
    assert result["owp"]["verdict"] == "pass", result["owp"]["detail"]
    assert result["binding"]["verdict"] == "fail:commitment-objective-missing"


# --------------------------------------------------------------------------
# 7. the frozen fixtures are what the builder produces
# --------------------------------------------------------------------------

def rebuild(cell_ids):
    """Rebuild named cells into a temporary tree and return their manifests."""
    if not os.environ.get("OWP_SOURCE"):
        pytest.skip("OWP_SOURCE is unset: fixture construction needs the pinned clone")
    binary = jpack_bin()
    import build_fixtures

    work_root = Path(tempfile.mkdtemp(prefix="study014-rebuild-"))
    try:
        judgments = work_root / "judgments"
        judgments.mkdir()
        pack_bytes = build_fixtures.PACK_PATH.read_bytes()
        executable_digest = "sha256:" + verify.sha256_file(binary)
        base = build_fixtures.decide(
            binary,
            judgments,
            pack_bytes,
            build_fixtures.FACTS_BASE,
            build_fixtures.EVIDENCE_PRESENT,
        )
        candidates = {
            "pos-baseline": build_fixtures.commitment_for(base, executable_digest),
            "a04-commitment-packdigest-resigned": build_fixtures.commitment_for(
                base,
                executable_digest,
                overrides={
                    "packDigest": "sha256:"
                    + hashlib.sha256(b"study-014/wrong-pack").hexdigest()
                },
            ),
        }
        manifests = {}
        for cell_id in cell_ids:
            payload = build_fixtures.flow_cell(
                work_root,
                base,
                candidates[cell_id],
                salt=cell_id,
                owp_source=os.environ["OWP_SOURCE"],
            )
            directory = work_root / cell_id
            build_fixtures.write_cell(directory, payload)
            manifests[cell_id] = (directory / verify.MANIFEST_NAME).read_text()
        return manifests
    finally:
        shutil.rmtree(work_root, ignore_errors=True)


def test_build_is_deterministic_for_a_flow_and_a_resigned_cell():
    cell_ids = ("pos-baseline", "a04-commitment-packdigest-resigned")
    manifests = rebuild(cell_ids)
    for cell_id in cell_ids:
        frozen = (cell_directory(cell_id) / verify.MANIFEST_NAME).read_text()
        assert manifests[cell_id] == frozen, cell_id


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
    expectation = next(
        cell["expected"] for cell in MATRIX["cells"] if cell["id"] == cell_id
    )
    assert score.pipeline_problems(cell_directory(cell_id), expectation) == []
