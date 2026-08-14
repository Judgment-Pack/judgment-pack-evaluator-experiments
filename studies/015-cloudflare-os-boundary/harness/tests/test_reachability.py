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


def test_ledger_lifecycle_invalid_pending_with_a_resolution_stamp(cell_copy):
    """The shape round 4 tabulated: pending, yet already resolved."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "pending"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_resolved_without_a_stamp(cell_copy):
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0].pop("appliedAt")
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_auto_approved_rejection(cell_copy):
    """The platform has no automatic rejection."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "rejected"
    ledger[0]["autoApproved"] = True
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_auto_approval_flag_on_a_rejection(cell_copy):
    """Round 5: `false` is as impossible as `true` outside an approval — nothing but the
    approve chokepoint ever writes the flag."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "rejected"
    ledger[0]["autoApproved"] = False
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_approval_without_an_autoapproved_boolean(cell_copy):
    """The chokepoint takes `autoApproved` as a required argument and always persists it."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0].pop("autoApproved")
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_non_rfc3339_timestamp(cell_copy):
    """A serialized `Date` is a strict RFC 3339 date-time; a parseable near-miss is not."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01 00:31:00Z"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_partial_resolver(cell_copy):
    """`AiChatAuthorInfo` is a complete triple; an id alone is not a resolver."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["resolvedBy"] = {"id": "governor@example.invalid"}
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


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


def test_unbound_execution_catches_substituted_causation(cell_copy):
    """Round 4's decisive construction: correct cardinality, wrong cause.

    One bound approved call, one retained effect — but the effect was produced by a
    different, unretained call with the same tuple. Counting alone cannot tell the two
    histories apart, so the attestation names the staged call it came from and the
    ceremony joins on that name.
    """
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"][0]["action"] = 99
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "unbound-execution"


def test_unbound_execution_catches_a_changed_argument_governed_effect(cell_copy):
    """The effect inventory is scoped by the governed tool and resource, not by the
    derived arguments — round 4 found a changed-argument effect sat outside it."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    extra = json.loads(json.dumps(platform["effects"][0]))
    extra["arguments"] = dict(extra["arguments"], requestType="something-else")
    platform["effects"].append(extra)
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "unbound-execution"


def test_binding_reuse_catches_an_unbound_call_filling_the_cap(cell_copy):
    """Round 5: counting is not enough — the governed call must BE the bound one.

    A single governed call carrying no commitment digest satisfied
    `len(subject) == authorized == 1` while sitting outside `bound_calls`, so every
    target, argument, revision and report check skipped it.
    """
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0].pop("commitmentDigest")
    platform["effects"] = []
    dump_json(cell / "platform.json", platform)
    report = load_json(cell / "report.json")
    report["execution"] = "none"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "binding-reuse"


def test_retained_store_unreadable_on_a_malformed_drain_witness(cell_copy):
    """Round 5: the witness was cast, never checked, so a malformed one reached the replay."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["drainWitnesses"][0]["rules"][0]["enabledBy"] = "governor@example.invalid"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "retained-store-unreadable"


def test_binding_reuse_on_duplicate_gatekeeper_ids(cell_copy):
    """Two gatekeepers with one id gave the store two readings — Python took the first,
    the node replay's `Map` the last. Neither may be preferred."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["gatekeepers"].append(
        dict(json.loads(json.dumps(platform["gatekeepers"][0])), serverTrust="byo")
    )
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_on_duplicate_ledger_ids(cell_copy):
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    twin = json.loads(json.dumps(ledger[0]))
    twin["action"] = 12
    ledger.append(twin)
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"].append(dict(platform["stagedCalls"][0], action=12))
    dump_json(cell / "platform.json", platform)
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_counts_a_governed_row_a_wrong_tool_call_used_to_erase(cell_copy):
    """Round 5, R4-1: under inaction, a wrong-tool staged call sharing an approved row's
    join identity made the inventory discard that otherwise governed approval."""
    cell = cell_copy("b06-unbound-execution")
    platform = load_json(cell / "platform.json")
    platform["effects"] = []
    platform["stagedCalls"] = [
        {
            "gatekeeperId": 1,
            "action": 11,
            "toolName": cmt.SECOND_TOOL,
            "arguments": {},
            "resourceRevisionAtStage": "rev-7",
            "connectorOutcome": "committed",
        }
    ]
    dump_json(cell / "platform.json", platform)
    row = json.loads(
        json.dumps(load_json(STUDY / "fixtures" / "baseline" / "ledger.json")[0])
    )
    row["id"] = 1
    row["action"] = 11
    dump_json(cell / "ledger.json", [row])
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_an_unclassifiable_approved_row(cell_copy):
    """A degraded orphan — an approved row on a gatekeeper the store does not retain —
    was discarded rather than refused."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    orphan = json.loads(json.dumps(ledger[0]))
    orphan["id"] = 2
    orphan["action"] = 77
    orphan["gatekeeperId"] = 9
    orphan.pop("resourceUrl")
    ledger.append(orphan)
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_catches_an_orphan_governed_application(cell_copy):
    """An approved governed ledger row with no staged call used to be invisible."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    orphan = json.loads(json.dumps(ledger[0]))
    orphan["id"] = 2
    orphan["action"] = 77
    ledger.append(orphan)
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


def test_upstream_refuses_ambiguous_stores_and_partial_attribution(cell_copy, cfos_source):
    """Round 5's node-side repairs, in one batched runner invocation.

    Each condition is a state the platform cannot write, and each used to be resolved
    silently: a duplicate id by preferring the last one the `Map` saw, a near-miss
    timestamp by `Date.parse` accepting it, and a forged resolver name by comparing only
    the resolver's id.
    """
    del cfos_source
    cells = []

    duplicate = cell_copy("pos-baseline")
    platform = load_json(duplicate / "platform.json")
    platform["gatekeepers"].append(
        dict(json.loads(json.dumps(platform["gatekeepers"][0])), serverTrust="byo")
    )
    dump_json(duplicate / "platform.json", platform)
    cells.append(("duplicate-gatekeeper-id", duplicate))

    stamped = cell_copy("neg-drain-skip")
    ledger = load_json(stamped / "ledger.json")
    ledger[0]["createdAt"] = "2026-08-01 00:01:00Z"
    dump_json(stamped / "ledger.json", ledger)
    cells.append(("non-rfc3339-created-at", stamped))

    renamed = cell_copy("s02-unknown-auto-applied")
    ledger = load_json(renamed / "ledger.json")
    ledger[0]["resolvedBy"]["name"] = "Someone Else"
    dump_json(renamed / "ledger.json", ledger)
    cells.append(("resolver-name-substituted", renamed))

    verdicts = cf_runner.ceremony(cells)["cells"]
    assert verdicts["duplicate-gatekeeper-id"]["code"] == "classification-refused"
    assert verdicts["non-rfc3339-created-at"]["code"] == "drain-order-violation"
    assert verdicts["resolver-name-substituted"]["code"] == "drain-order-violation"


def test_upstream_apparatus_self_report_matches_pins(upstream_verdicts):
    pins = load_json(STUDY / "harness" / "PINS.json")
    apparatus = upstream_verdicts["apparatus"]
    assert apparatus["cloneCommit"] == pins["cloudflareOs"]["commit"]
    assert apparatus["cloneTrackedClean"] is True
    assert apparatus["probedFiles"] == pins["cloudflareOs"]["probedFiles"]
    assert apparatus["nodeVersion"] == pins["harnessNode"]["version"]
