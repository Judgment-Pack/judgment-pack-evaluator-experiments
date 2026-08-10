"""Per-code reachability: a minimal condition for every registered verdict code, asserting
the exact code — and probes of the first-failure ordering, so no registered code can be
unreachable prose and no ordering claim can drift from the implementation
(PREREGISTRATION section 6).

Binding and replay conditions are constructed by mutating copies of frozen LOCKED
fixtures and calling the layer functions directly (the layers see no manifests and no
expectations). The two upstream codes are reached through the real node runner over the
frozen negative controls, batched into one ceremony invocation.

No reviewer-holdout fixture is read here. Round 1 asked for reachability to be shown
through the integrated scorer as well as by direct layer calls; the locked negative
controls `neg-binding-control` and `neg-replay-control` carry that, and the scorer's own
attempt exercises them on every run.
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


def test_evidence_backing_invalid_without_a_retained_preimage(cell_copy):
    """A digest-shaped reference with no retained artifact is an assertion, not lineage."""
    cell = cell_copy("pos-baseline")
    artifacts = load_json(cell / "evidence-artifacts.json")
    artifacts.pop("sponsor-endorsement")
    dump_json(cell / "evidence-artifacts.json", artifacts)
    assert binding(cell)["code"] == "evidence-backing-invalid"


def test_evidence_backing_invalid_when_the_artifact_does_not_hash_to_its_digest(cell_copy):
    cell = cell_copy("pos-baseline")
    artifacts = load_json(cell / "evidence-artifacts.json")
    import base64

    artifacts["sponsor-endorsement"] = {
        "base64": base64.b64encode(b"different bytes entirely").decode("ascii")
    }
    dump_json(cell / "evidence-artifacts.json", artifacts)
    assert binding(cell)["code"] == "evidence-backing-invalid"


def test_judgment_identity_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell, lambda c: c["judgment"].__setitem__("packVersion", "9.9.9")
    )
    assert binding(cell)["code"] == "judgment-identity-mismatch"


def test_judgment_identity_mismatch_on_duplicate_extensions(cell_copy):
    cell = cell_copy("pos-baseline")
    rebuild_commitment(
        cell,
        lambda c: c["judgment"].__setitem__("supportedExtensions", ["x", "x"]),
    )
    assert binding(cell)["code"] == "judgment-identity-mismatch"


def test_retained_store_unreadable(cell_copy):
    cell = cell_copy("pos-baseline")
    (cell / "platform.json").write_bytes(b"[not an object]")
    assert binding(cell)["code"] == "retained-store-unreadable"


def test_action_derivation_mismatch_on_substituted_arguments(cell_copy):
    """The verifier's independent oracle: a coherently rebuilt store cannot save this."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    substituted = dict(platform["stagedCalls"][0]["arguments"])
    substituted["requestType"] = "someone-else-entirely"
    digest = cmt.arguments_digest(substituted)
    new_digest = rebuild_commitment(
        cell, lambda c: c["action"].__setitem__("argumentsDigest", digest)
    )
    platform["stagedCalls"][0]["arguments"] = substituted
    platform["stagedCalls"][0]["commitmentDigest"] = new_digest
    platform["effects"] = []
    dump_json(cell / "platform.json", platform)
    report = load_json(cell / "report.json")
    report["commitmentDigest"] = new_digest
    report["execution"] = "applied"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "action-derivation-mismatch"


def test_action_derivation_mismatch_on_substituted_target(cell_copy):
    cell = cell_copy("pos-baseline")
    new_digest = rebuild_commitment(
        cell, lambda c: c["action"].__setitem__("actionKindTag", "forged:create_work_item")
    )
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["commitmentDigest"] = new_digest
    dump_json(cell / "platform.json", platform)
    ledger = load_json(cell / "ledger.json")
    ledger[0]["description"]["actionKind"] = {
        "tag": "forged:create_work_item",
        "label": "create_work_item",
    }
    dump_json(cell / "ledger.json", ledger)
    report = load_json(cell / "report.json")
    report["commitmentDigest"] = new_digest
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "action-derivation-mismatch"


def test_stage_revision_mismatch(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["resourceRevisionAtStage"] = "rev-99"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "stage-revision-mismatch"


def test_report_state_unsupported_phantom_staged(cell_copy):
    """A report state must be supported by the store, not merely well-spelled."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"] = []
    platform["effects"] = []
    platform["drainWitnesses"] = []
    dump_json(cell / "platform.json", platform)
    dump_json(cell / "ledger.json", [])
    report = load_json(cell / "report.json")
    report["execution"] = "staged"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "report-state-unsupported"


def test_report_state_unsupported_unknown_outcome_reported_applied(cell_copy):
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["connectorOutcome"] = "outcome-unknown"
    platform["effects"] = []
    dump_json(cell / "platform.json", platform)
    report = load_json(cell / "report.json")
    report["execution"] = "applied"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "report-state-unsupported"


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
    platform["gatekeepers"][0]["serverTrust"] = "byo"
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


def test_binding_reuse_catches_an_unlabelled_second_subject_call(cell_copy):
    """Round 2's blocker 1: a surplus call carrying no commitment digest was invisible."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    twin = json.loads(json.dumps(platform["stagedCalls"][0]))
    twin["action"] = 12
    twin.pop("commitmentDigest")
    platform["stagedCalls"].append(twin)
    dump_json(cell / "platform.json", platform)
    ledger = load_json(cell / "ledger.json")
    row = json.loads(json.dumps(ledger[0]))
    row["id"] = 2
    row["action"] = 12
    ledger.append(row)
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_catches_a_subject_call_under_an_inaction_commitment(cell_copy):
    """The same attack on the *inaction* half of the map.

    A pre-freeze self-audit found that subject identity was derived from the authorized
    action, which is `None` under every non-executable disposition — so the whole
    subject-cardinality check silently disabled itself exactly where the map authorizes
    zero calls. Subject identity now comes from the retained facts alone.
    """
    cell = cell_copy("b06-unbound-execution")
    facts = json.loads((cell / "facts.json").read_bytes())
    platform = load_json(cell / "platform.json")
    platform["effects"] = []
    platform["stagedCalls"] = [
        {
            "gatekeeperId": 1,
            "action": 11,
            "toolName": cmt.ACTION_TOOL,
            "arguments": cmt.action_arguments(facts),
            "resourceRevisionAtStage": "rev-7",
            "connectorOutcome": "committed",
        }
    ]
    platform["world"] = {"resourceRevisionAtApply": {"1:11": "rev-7"}}
    dump_json(cell / "platform.json", platform)
    ledger = load_json(cell / "ledger.json")
    row = json.loads(
        json.dumps(load_json(STUDY / "fixtures" / "baseline" / "ledger.json")[0])
    )
    row["id"] = 1
    row["action"] = 11
    ledger.append(row)
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


def test_unbound_execution_counts_surplus_effects(cell_copy):
    """A second attested effect must not hide behind one legitimate application."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"].append(json.loads(json.dumps(platform["effects"][0])))
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "unbound-execution"


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
# upstream codes — one batched real-runner invocation over the frozen controls
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def upstream_verdicts(cfos_source):
    del cfos_source
    cells = [
        ("neg-mcp-byo-autoapply",
         STUDY / "fixtures" / "mutations" / "neg-mcp-byo-autoapply"),
        ("neg-drain-skip", STUDY / "fixtures" / "mutations" / "neg-drain-skip"),
        ("pos-baseline", STUDY / "fixtures" / "baseline"),
    ]
    return cf_runner.ceremony(cells)


def test_upstream_classification_refused(upstream_verdicts):
    record = upstream_verdicts["cells"]["neg-mcp-byo-autoapply"]
    assert record["verdict"] == "fail" and record["code"] == "classification-refused"


def test_upstream_drain_order_violation(upstream_verdicts):
    record = upstream_verdicts["cells"]["neg-drain-skip"]
    assert record["verdict"] == "fail" and record["code"] == "drain-order-violation"


def test_upstream_order_classification_before_drain(upstream_verdicts):
    # neg-mcp fails classification without the drain replay ever engaging.
    record = upstream_verdicts["cells"]["neg-mcp-byo-autoapply"]
    assert record["engaged"] == ["classifyTool"]


def test_upstream_baseline_replays_both_and_passes(upstream_verdicts):
    record = upstream_verdicts["cells"]["pos-baseline"]
    assert record["verdict"] == "pass"
    assert record["engaged"] == ["classifyTool", "AutoApprovalDrainer"]


def test_upstream_apparatus_self_report_matches_pins(upstream_verdicts):
    pins = load_json(STUDY / "harness" / "PINS.json")
    apparatus = upstream_verdicts["apparatus"]
    assert apparatus["cloneCommit"] == pins["cloudflareOs"]["commit"]
    assert apparatus["cloneTrackedClean"] is True
    assert apparatus["probedFiles"] == pins["cloudflareOs"]["probedFiles"]
    assert apparatus["nodeVersion"] == pins["harnessNode"]["version"]
