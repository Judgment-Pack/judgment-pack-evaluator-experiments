"""Per-code reachability: a minimal condition for every registered verdict code, asserting
the exact code — and probes of the first-failure ordering, so no registered code can be
unreachable prose and no ordering claim can drift from the implementation
(PREREGISTRATION section 6).

Binding and replay conditions are constructed by mutating copies of frozen fixtures and
calling the layer functions directly (the layers see no manifests and no expectations).
The two cf codes are reached through the real node runner over the frozen negative
controls, batched into one ceremony invocation.
"""

import json

import pytest

import cf_runner
import commitment as cmt
import verify
from conftest import STUDY, dump_json, load_json


def binding(cell_dir):
    return verify.layer_binding(verify.Cell(cell_dir))


def rebuild_commitment(cell_dir, mutate):
    """Load, mutate, re-canonicalize, and rewrite the cell's commitment coherently."""
    document = json.loads((cell_dir / "commitment.json").read_bytes())
    mutate(document)
    (cell_dir / "commitment.json").write_bytes(cmt.commitment_bytes(document))
    return cmt.commitment_digest(document)


# ---------------------------------------------------------------------------
# binding codes
# ---------------------------------------------------------------------------

def test_commitment_missing(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "commitment.json").unlink()
    assert binding(cell)["code"] == "commitment-missing"


def test_commitment_schema_invalid_noncanonical(cell_copy):
    cell = cell_copy("pos-baseline")
    raw = (cell / "commitment.json").read_bytes()
    (cell / "commitment.json").write_bytes(raw + b"\n")
    assert binding(cell)["code"] == "commitment-schema-invalid"


def test_commitment_schema_invalid_duplicate_member(cell_copy):
    cell = cell_copy("pos-baseline")
    raw = (cell / "commitment.json").read_bytes()
    body = raw[:-1] + b',"commitmentVersion":"1"}'
    (cell / "commitment.json").write_bytes(body)
    assert binding(cell)["code"] == "commitment-schema-invalid"


def test_pack_artifact_missing(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "pack.json").unlink()
    assert binding(cell)["code"] == "pack-artifact-missing"


def test_pack_digest_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "pack.json").write_bytes((cell / "pack.json").read_bytes() + b" ")
    assert binding(cell)["code"] == "pack-digest-mismatch"


def test_facts_digest_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "facts.json").write_bytes((cell / "facts.json").read_bytes() + b" ")
    assert binding(cell)["code"] == "facts-digest-mismatch"


def test_evidence_digest_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "evidence.json").write_bytes((cell / "evidence.json").read_bytes() + b" ")
    assert binding(cell)["code"] == "evidence-digest-mismatch"


def test_disposition_digest_mismatch_retained(cell_copy):
    cell = cell_copy("pos-baseline")
    envelope = load_json(cell / "evaluation.json")
    envelope["disposition"]["reasons"] = ["edited"]
    dump_json(cell / "evaluation.json", envelope)
    assert binding(cell)["code"] == "disposition-digest-mismatch-retained"


def test_evidence_backing_invalid_missing_entry(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell, lambda c: c["judgment"]["evidenceBacking"].pop("intake-form")
    )
    assert binding(cell)["code"] == "evidence-backing-invalid"


def test_evidence_backing_invalid_nonartifact_kind(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell,
        lambda c: c["judgment"]["evidenceBacking"].__setitem__(
            "intake-form", {"kind": "approval-record", "ref": "ledger:1"}
        ),
    )
    assert binding(cell)["code"] == "evidence-backing-invalid"


def test_action_map_violation_null_action_under_proceed(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(cell, lambda c: c.__setitem__("action", None))
    assert binding(cell)["code"] == "action-map-violation"


def _duplicate_bound_call(cell):
    """Second staged call + approved ledger record bound to the same digest."""
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"].append(dict(platform["stagedCalls"][0], action=12))
    platform["world"]["resourceRevisionAtApply"]["1:12"] = "rev-7"
    dump_json(cell / "platform.json", platform)
    ledger = load_json(cell / "ledger.json")
    twin = json.loads(json.dumps(ledger[0]))
    twin["id"] = 2
    twin["action"] = 12
    ledger.append(twin)
    dump_json(cell / "ledger.json", ledger)


def test_binding_reuse(cell_copy):
    cell = cell_copy("pos-baseline")
    _duplicate_bound_call(cell)
    assert binding(cell)["code"] == "binding-reuse"


def test_target_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["gatekeepers"][0]["resourceUrl"] = "https://elsewhere.example/mcp"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "target-mismatch"


def test_argument_drift(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["arguments"]["requestType"] = "tampered"
    # Keep the attested effect aligned with the staged call so the drift is isolated.
    platform["effects"][0]["arguments"]["requestType"] = "tampered"
    dump_json(cell / "platform.json", platform)
    result = binding(cell)
    assert result["code"] == "argument-drift"


def test_revision_drift(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["world"]["resourceRevisionAtApply"]["1:11"] = "rev-99"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "revision-drift"


def test_simulation_basis_invalid(cell_copy):
    cell = cell_copy("d01-dependent-simulated-write")
    platform = load_json(cell / "platform.json")
    platform["simulations"] = []
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "simulation-basis-invalid"


def test_unbound_execution(cell_copy):
    # b06's frozen fixture is already the minimal condition; assert it from the layer
    # directly so the code's reachability does not rest on the scorer.
    assert binding(STUDY / "fixtures" / "mutations" / "b06-unbound-execution")[
        "code"
    ] == "unbound-execution"


def test_handoff_dropped(cell_copy):
    assert binding(STUDY / "fixtures" / "mutations" / "s05-handoff-dropped")[
        "code"
    ] == "handoff-dropped"


def test_commit_overclaim(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"] = []
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "commit-overclaim"


def test_report_misattribution(cell_copy):
    cell = cell_copy("pos-baseline")
    report = load_json(cell / "report.json")
    report["decision"]["outcomeId"] = "clarify-return"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "report-misattribution"


def test_report_missing_is_misattribution(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "report.json").unlink()
    assert binding(cell)["code"] == "report-misattribution"


# ---------------------------------------------------------------------------
# first-failure ordering probes
# ---------------------------------------------------------------------------

def test_order_schema_before_pack_digest(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "commitment.json").write_bytes(
        (cell / "commitment.json").read_bytes() + b"\n"
    )
    (cell / "pack.json").write_bytes((cell / "pack.json").read_bytes() + b" ")
    assert binding(cell)["code"] == "commitment-schema-invalid"


def test_order_pack_before_facts(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "pack.json").write_bytes((cell / "pack.json").read_bytes() + b" ")
    (cell / "facts.json").write_bytes((cell / "facts.json").read_bytes() + b" ")
    assert binding(cell)["code"] == "pack-digest-mismatch"


def test_order_backing_before_action_map(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell,
        lambda c: (
            c["judgment"]["evidenceBacking"].__setitem__(
                "intake-form", {"kind": "observation-record", "ref": "ledger:1"}
            ),
            c.__setitem__("action", None),
        ),
    )
    assert binding(cell)["code"] == "evidence-backing-invalid"


def test_order_target_before_argument(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["gatekeepers"][0]["serverTrust"] = "byo"
    platform["stagedCalls"][0]["arguments"]["requestType"] = "tampered"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "target-mismatch"


def test_order_reuse_before_target(cell_copy):
    cell = cell_copy("pos-baseline")
    _duplicate_bound_call(cell)
    platform = load_json(cell / "platform.json")
    platform["gatekeepers"][0]["serverTrust"] = "byo"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "binding-reuse"


# ---------------------------------------------------------------------------
# replay codes
# ---------------------------------------------------------------------------

def replay(cell_dir, jpack_bin, tmp_path):
    return verify.layer_replay(verify.Cell(cell_dir), jpack_bin, tmp_path)


def test_replay_unavailable(tmp_path):
    result = replay(STUDY / "fixtures" / "baseline", None, tmp_path)
    assert result["code"] == "replay-unavailable"


def test_replay_executable_mismatch(jpack_bin, tmp_path):
    result = replay(
        STUDY / "fixtures" / "mutations" / "a03-evaluator-digest-forged",
        jpack_bin,
        tmp_path,
    )
    assert result["code"] == "replay-executable-mismatch"


def test_replay_refused(cell_copy, jpack_bin, tmp_path):
    cell = cell_copy("pos-baseline")
    facts = b"{not json"
    (cell / "facts.json").write_bytes(facts)
    rebuild_commitment(
        cell,
        lambda c: c["judgment"].__setitem__(
            "factsDigest", cmt.sha256_prefixed(facts)
        ),
    )
    result = replay(cell, jpack_bin, tmp_path)
    assert result["code"] == "replay-refused"


def test_replay_spec_version_mismatch(cell_copy, jpack_bin, tmp_path):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell,
        lambda c: c["judgment"].__setitem__("evaluatorSpecVersion", "0.1.0-draft"),
    )
    result = replay(cell, jpack_bin, tmp_path)
    assert result["code"] == "replay-spec-version-mismatch"


def test_replay_disposition_mismatch(jpack_bin, tmp_path):
    result = replay(
        STUDY / "fixtures" / "mutations" / "a02-disposition-forged", jpack_bin, tmp_path
    )
    assert result["code"] == "replay-disposition-mismatch"


# ---------------------------------------------------------------------------
# cf codes — one batched real-runner invocation over the frozen negative controls
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cf_verdicts(cfos_source):
    del cfos_source
    cells = [
        ("neg-mcp-byo-autoapply",
         STUDY / "fixtures" / "mutations" / "neg-mcp-byo-autoapply"),
        ("neg-drain-skip", STUDY / "fixtures" / "mutations" / "neg-drain-skip"),
        ("pos-baseline", STUDY / "fixtures" / "baseline"),
    ]
    return cf_runner.ceremony(cells)


def test_cf_classification_refused(cf_verdicts):
    record = cf_verdicts["cells"]["neg-mcp-byo-autoapply"]
    assert record["verdict"] == "fail" and record["code"] == "classification-refused"


def test_cf_drain_order_violation(cf_verdicts):
    record = cf_verdicts["cells"]["neg-drain-skip"]
    assert record["verdict"] == "fail" and record["code"] == "drain-order-violation"


def test_cf_order_classification_before_drain(cf_verdicts):
    # neg-mcp fails classification without the drain replay ever engaging.
    record = cf_verdicts["cells"]["neg-mcp-byo-autoapply"]
    assert record["engaged"] == ["classifyTool"]


def test_cf_baseline_engages_both_and_passes(cf_verdicts):
    record = cf_verdicts["cells"]["pos-baseline"]
    assert record["verdict"] == "pass"
    assert record["engaged"] == ["classifyTool", "AutoApprovalDrainer"]


def test_cf_apparatus_self_report_matches_pins(cf_verdicts):
    pins = load_json(STUDY / "harness" / "PINS.json")
    apparatus = cf_verdicts["apparatus"]
    assert apparatus["cloneCommit"] == pins["cloudflareOs"]["commit"]
    assert apparatus["cloneTrackedClean"] is True
    assert apparatus["probedFiles"] == pins["cloudflareOs"]["probedFiles"]
    assert apparatus["nodeVersion"] == pins["harnessNode"]["version"]
