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
import shutil

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


def test_ledger_lifecycle_invalid_non_platform_timestamp(cell_copy):
    """Every retained instant is a serialized `Date`; a parseable near-miss is not one."""
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


# -- round 6: the retained outcome compatibility matrix, one condition per scalar -------
#
# SPEC section 5 registers the flattened `connectorOutcome`, the outer lifecycle state and
# the report state as one derived matrix. Both halves are enforced on existing codes: the
# store half under `ledger-lifecycle-invalid`, the claim half under
# `report-state-unsupported`. Each of the five scalars gets a condition.

def _connector_outcome(cell, outcome):
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["connectorOutcome"] = outcome
    dump_json(cell / "platform.json", platform)


def test_lifecycle_refuses_a_rejected_outcome_beside_an_approved_row(cell_copy):
    """Round 6's reproduction, exactly: the reviewer took the baseline to a complete green
    result by changing only `connectorOutcome` to `rejected` and the report to `applied`.

    The connector's `reject` proceeds only from `pending` and throws for every other state
    (`action-store.ts:201-211`), and the outer row is set `rejected` in the same call
    (`overseer.ts:7707-7732`), so `rejected` beside an `approved` row is a pair the
    platform cannot have retained.
    """
    cell = cell_copy("pos-baseline")
    _connector_outcome(cell, "rejected")
    report = load_json(cell / "report.json")
    report["execution"] = "applied"
    dump_json(cell / "report.json", report)
    result = binding(cell)
    assert result["code"] == "ledger-lifecycle-invalid"
    assert "rejected" in result["detail"]


def test_lifecycle_refuses_a_pending_outcome_beside_an_approved_row(cell_copy):
    """`approved` is written only after the dispatch returned, so the private row cannot
    still be waiting to be sent."""
    cell = cell_copy("pos-baseline")
    _connector_outcome(cell, "pending")
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_lifecycle_refuses_a_failed_outcome_beside_an_approved_row(cell_copy):
    """A determinate failure throws out of `applyAction`, so the chokepoint's
    `record.state = "approved"` is never reached (`overseer.ts:2490-2497`)."""
    cell = cell_copy("pos-baseline")
    _connector_outcome(cell, "failed")
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_report_state_refuses_a_committed_outcome_claimed_unproven(cell_copy):
    """`applied-unproven` is the ambiguity state, never a default and never a place to
    file a determinate outcome — the claim half of the same matrix."""
    cell = cell_copy("pos-baseline")
    report = load_json(cell / "report.json")
    report["execution"] = "applied-unproven"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "report-state-unsupported"


def test_report_state_refuses_an_unknown_outcome_claimed_merely_staged(cell_copy):
    """The understatement in the other direction: a dispatch whose result was never
    observed may have landed, so reporting it as still queued hides the ambiguity that
    `applied-unproven` exists to name."""
    cell = cell_copy("m02-ambiguous-commit")
    report = load_json(cell / "report.json")
    report["execution"] = "staged"
    dump_json(cell / "report.json", report)
    assert binding(cell)["code"] == "report-state-unsupported"


# -- round 6: identities are settled before anything is keyed on them ------------------

def _second_gatekeeper_with_id(cell, raw_id):
    """Append a second retained gatekeeper carrying `raw_id`, written as raw JSON.

    The literal matters: `-0` and `1.0` are distinct JSON tokens that read back as one
    Python value and as two JavaScript values (or the reverse), which is exactly the
    cross-language aliasing round 6 (R6-3) found.
    """
    platform = load_json(cell / "platform.json")
    twin = json.loads(json.dumps(platform["gatekeepers"][0]))
    twin["id"] = "@@ID@@"
    platform["gatekeepers"].append(twin)
    text = json.dumps(platform, indent=2, ensure_ascii=False) + "\n"
    (cell / "platform.json").write_text(text.replace('"@@ID@@"', raw_id), encoding="utf-8")


def test_binding_reuse_refuses_a_float_gatekeeper_id_aliasing_an_integer(cell_copy):
    """The reviewer's alias: a second gatekeeper with `id: 1.0` used to survive uniqueness
    here (`repr(1.0) != repr(1)`) while the node side stringified both to `"1"` and
    refused — one store, two verdicts."""
    cell = cell_copy("pos-baseline")
    _second_gatekeeper_with_id(cell, "1.0")
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_a_boolean_gatekeeper_id(cell_copy):
    """`true` is an `int` subclass here and coerces to 1 in JavaScript."""
    cell = cell_copy("pos-baseline")
    _second_gatekeeper_with_id(cell, "true")
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_a_negative_zero_gatekeeper_id(cell_copy):
    """`-0` is the same value as `0` here and a distinct one in JavaScript, where it
    stringifies to `"0"`; the platform assigns neither, so both sides refuse it."""
    cell = cell_copy("pos-baseline")
    _second_gatekeeper_with_id(cell, "-0")
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_an_id_past_the_javascript_safe_integer_boundary(cell_copy):
    """Past 2^53-1 a JSON number no longer round-trips through V8, so it is not an
    identity the platform can have assigned or read back."""
    cell = cell_copy("pos-baseline")
    _second_gatekeeper_with_id(cell, "9007199254740992")
    assert binding(cell)["code"] == "binding-reuse"


# -- round 6: lifecycle-only members are read by key presence --------------------------

def test_ledger_lifecycle_invalid_on_an_explicit_null_autoapproved(cell_copy):
    """Round 6 (R6-4): `entry.get("autoApproved") is not None` accepted an explicit null on
    a pending row, although the chokepoint writes that member nowhere but an approval."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "pending"
    ledger[0].pop("appliedAt")
    ledger[0].pop("resolvedBy")
    ledger[0]["autoApproved"] = None
    dump_json(cell / "ledger.json", ledger)
    result = binding(cell)
    assert result["code"] == "ledger-lifecycle-invalid"
    assert "autoApproved" in result["detail"]


# -- round 6: one serialized instant form, and a total parse ---------------------------

def test_ledger_lifecycle_invalid_on_an_impossible_calendar_date(cell_copy):
    """`2026-02-29` is digit-shaped and not a date; `Date.parse` used to normalize it to
    March 1 on the node side rather than refuse it."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["appliedAt"] = "2026-02-29T00:31:00.000Z"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_below_the_millisecond_boundary(cell_copy):
    """A serialized `Date` carries exactly three fraction digits. Sub-millisecond
    neighbours are not stamps the platform writes, and the node side collapsed `.0004Z`
    and `.0005Z` onto one instant rather than refusing both."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.0004Z"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_a_valid_shaped_extreme_fraction_returns_a_verdict_rather_than_raising(cell_copy):
    """Totality, at the exact site round 6 (R6-5) found: the witness's own instant was
    parsed through `float` at store load, *outside* the per-check guard, so an extreme
    valid-shaped fraction raised `OverflowError` out of the layer instead of producing an
    apparatus verdict. The grammar admits three digits and nothing computes."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["drainWitnesses"][0]["at"] = "2026-08-01T00:31:00." + "9" * 400 + "Z"
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "retained-store-unreadable"


# -- round 6: the inventory is the governed tool AND resource --------------------------

def test_a_coherent_other_tool_approval_is_out_of_the_governed_inventory(cell_copy):
    """Round 6 (R6-6)'s reciprocal: the inventory was resource-only, so a coherent
    `tracker_close_work_item` approval and its matching call on the governed resource were
    counted against the create-work-item authorization and refused as `binding-reuse`.

    The row is classified by its OWN retained action-kind label, so a coherently different
    tool is out of scope exactly as a different resource is, and the cell is green. The
    other direction — a target-tool row a wrong-tool call disagrees with — stays governed,
    which `test_binding_reuse_counts_a_governed_row_a_wrong_tool_call_used_to_erase`
    holds.
    """
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    other = json.loads(json.dumps(ledger[0]))
    other["id"] = 2
    other["action"] = 12
    other["autoApproved"] = False
    other["description"]["actionKind"] = {
        "tag": cmt.action_kind_tag(tool_name=cmt.SECOND_TOOL),
        "label": cmt.SECOND_TOOL,
    }
    ledger.append(other)
    dump_json(cell / "ledger.json", ledger)
    platform = load_json(cell / "platform.json")
    call = json.loads(json.dumps(platform["stagedCalls"][0]))
    call["action"] = 12
    call["toolName"] = cmt.SECOND_TOOL
    call.pop("commitmentDigest")
    platform["stagedCalls"].append(call)
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["verdict"] == "pass"


def test_binding_reuse_refuses_a_governed_row_whose_label_its_own_tag_contradicts(
    cell_copy,
):
    """Unclassifiable, not silently dropped: `actionKindFor` builds the tag from the tool
    (`tools.ts:94`), so a row whose tag and label name different tools records two
    different actions to two different readers and can be classified as neither."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["description"]["actionKind"]["label"] = cmt.SECOND_TOOL
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


# -- round 7: the reject side of every symmetry round 6 built on the apply side ---------
#
# R7-1. Round 6 registered one crash window and one determinate resolution. The pinned
# source has two of each, written the same way: `action-store.ts:196` saves `applied`
# before `applyAction` returns, `action-store.ts:209` writes `rejected` before
# `overseer.ts:7729-7732` updates the outer row. So the lifecycle admits both pairs, the
# report may claim neither over its crash window, and `rejected` is a report state.


def _codes(result):
    """Every code a failing layer record published — adjudicated and suppressed alike."""
    return [] if result["verdict"] == "pass" else [result["code"]] + result["suppressed"]


def _crash_window(cell, outcome):
    """The outer row the workspace never wrote: the connector resolved, the ledger pending."""
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "pending"
    for member in ("appliedAt", "resolvedBy", "autoApproved"):
        ledger[0].pop(member, None)
    dump_json(cell / "ledger.json", ledger)
    _connector_outcome(cell, outcome)


def _completed_rejection(cell):
    """A completed rejection, written as the registered matrix admits one.

    The bound call is `rejected` on both sides of the flatten and the report claims that
    state, which is the one tuple SPEC section 5 pairs with a `rejected` scalar. The
    retained effect attestation goes with it: an attestation matched to a call the store
    also records as refused is a different tuple, and the matrix is what decides either.
    """
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "rejected"
    ledger[0].pop("autoApproved", None)
    dump_json(cell / "ledger.json", ledger)
    platform = load_json(cell / "platform.json")
    platform["stagedCalls"][0]["connectorOutcome"] = "rejected"
    platform["effects"] = []
    dump_json(cell / "platform.json", platform)
    report = load_json(cell / "report.json")
    report["execution"] = "rejected"
    dump_json(cell / "report.json", report)


def test_lifecycle_admits_the_apply_side_crash_window(cell_copy):
    """`committed` beside a `pending` row is a pair round 6 registered as admissible;
    nothing had ever asserted that the check agrees."""
    cell = cell_copy("pos-baseline")
    _crash_window(cell, "committed")
    assert "ledger-lifecycle-invalid" not in _codes(binding(cell))


def test_lifecycle_admits_the_reject_side_crash_window(cell_copy):
    """The same window on the other path, which round 6 refused as impossible (R7-1). The
    connector writes the rejection at `action-store.ts:209` and the outer row is updated
    afterwards at `overseer.ts:7729-7732`, so that write order rules this pair out no more
    than it rules out the apply-side one."""
    cell = cell_copy("pos-baseline")
    _crash_window(cell, "rejected")
    assert "ledger-lifecycle-invalid" not in _codes(binding(cell))


def test_a_completed_rejection_is_reportable_and_green(cell_copy):
    """The gap round 6 registered and round 7 declined to keep: with no `rejected` report
    state, this store — internally consistent in every field — could be described only
    falsely or not at all."""
    cell = cell_copy("pos-baseline")
    _completed_rejection(cell)
    assert binding(cell)["verdict"] == "pass"


def test_report_state_refuses_a_rejected_claim_over_the_crash_window(cell_copy):
    """Adding the state does not make it a free-text claim: `rejected` requires the outer
    row the workspace writes, so the reject-side crash window supports the history and not
    the claim — symmetrically with `applied` over the apply-side window."""
    cell = cell_copy("pos-baseline")
    _completed_rejection(cell)
    ledger = load_json(cell / "ledger.json")
    ledger[0]["state"] = "pending"
    for member in ("appliedAt", "resolvedBy"):
        ledger[0].pop(member, None)
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "report-state-unsupported"


# -- round 7: one identity definition, on the token rather than the read-back value ------


def _sole_gatekeeper_id_literal(cell, raw_id):
    """Rewrite the ONE retained gatekeeper's id as a raw JSON token.

    Round 6's identity regressions all appended a *second* gatekeeper, which refuses on
    both sides as a duplicate whatever the token is — so they could not see that a lone
    `1.0` was refused here and accepted by the node runner (R7-2). A lone value is the
    condition.
    """
    platform = load_json(cell / "platform.json")
    platform["gatekeepers"][0]["id"] = "@@ID@@"
    text = json.dumps(platform, indent=2, ensure_ascii=False) + "\n"
    (cell / "platform.json").write_text(text.replace('"@@ID@@"', raw_id), encoding="utf-8")


def test_binding_reuse_refuses_a_lone_float_identity(cell_copy):
    """`JSON.parse("1.0")` is `1` and `Number.isSafeInteger` accepts it; the registered
    identity is the token, and `1.0` is not one."""
    cell = cell_copy("pos-baseline")
    _sole_gatekeeper_id_literal(cell, "1.0")
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_a_lone_exponent_identity(cell_copy):
    """Same value, same acceptance on the node side, same refusal here: `1e0`."""
    cell = cell_copy("pos-baseline")
    _sole_gatekeeper_id_literal(cell, "1e0")
    assert binding(cell)["code"] == "binding-reuse"


# -- round 7: the instant grammar is ASCII and total, on both sides ---------------------


def test_ledger_lifecycle_invalid_on_a_unicode_digit_stamp(cell_copy):
    """Python's `\\d` is Unicode-aware, so Arabic-Indic digits satisfied a grammar
    registered as the ASCII output of `toISOString()` — a form no `Date` serializes and
    the node side already refused (R7-3)."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.٠٠٠Z"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


def test_ledger_lifecycle_invalid_on_a_trailing_newline_stamp(cell_copy):
    """Python's `$` matches before a final newline and JavaScript's does not, so a stamp
    with a trailing `\\n` passed here and was refused there (R7-3)."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.000Z\n"
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "ledger-lifecycle-invalid"


# -- round 7: the action-kind tag is required and compared whole ------------------------


def test_binding_reuse_refuses_a_governed_row_with_no_action_kind_tag(cell_copy):
    """Round 6 skipped the comparison when the tag was absent or empty, so a governed row
    could be classified on an unchecked label alone; the pinned connector submits a
    deployment-derived tag on every record it stages (R7-5)."""
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["description"]["actionKind"].pop("tag")
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


def test_binding_reuse_refuses_a_foreign_scope_tag_on_a_governed_row(cell_copy):
    """The other half: round 6 compared only the suffix after the last literal colon, so a
    row on the governed resource could carry another deployment's scope entirely and still
    classify — a tag no host staging this call can emit."""
    import build_fixtures

    other = build_fixtures.OTHER_PORTAL
    cell = cell_copy("pos-baseline")
    ledger = load_json(cell / "ledger.json")
    ledger[0]["description"]["actionKind"]["tag"] = cmt.action_kind_tag(
        cmt.action_scope_tag(other["resourceUrl"], other["serverId"]),
        cmt.ACTION_TOOL,
    )
    dump_json(cell / "ledger.json", ledger)
    assert binding(cell)["code"] == "binding-reuse"


# -- round 8: the identity rule reaches the witness's own identities too ----------------


def _witness_pass_literal(cell, raw_pass):
    """Rewrite the sole retained witness's `pass` as a raw JSON token.

    The same construction `_sole_gatekeeper_id_literal` uses, aimed at the one identity
    round 7's repair did not reach: R7-2 moved the rule onto the token for the gatekeeper's
    id, and the witness's pass number went on being whatever `JSON.parse` returned (R8-3).
    """
    platform = load_json(cell / "platform.json")
    platform["drainWitnesses"][0]["pass"] = "@@PASS@@"
    text = json.dumps(platform, indent=2, ensure_ascii=False) + "\n"
    (cell / "platform.json").write_text(
        text.replace('"@@PASS@@"', raw_pass), encoding="utf-8"
    )


def test_store_unreadable_on_a_lone_float_witness_pass(cell_copy):
    """The binding side already refused this; the value of the row is the pair it makes
    with the node-side batch below, over the same bytes."""
    cell = cell_copy("pos-baseline")
    _witness_pass_literal(cell, "1.0")
    assert binding(cell)["code"] == "retained-store-unreadable"


def test_store_unreadable_on_a_lone_exponent_witness_pass(cell_copy):
    cell = cell_copy("pos-baseline")
    _witness_pass_literal(cell, "1e0")
    assert binding(cell)["code"] == "retained-store-unreadable"


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
    """The at-most-once overclaim, isolated to the report.

    Round 6 (R6-2) moved the store-internal half of this construction to
    `ledger-lifecycle-invalid`: an `approved` outer row can only stand beside `committed`,
    because the chokepoint writes `approved` after the connector call returns. So the
    overclaim is built on the cell whose store really is the ambiguity — outer `pending`,
    scalar `outcome-unknown` — and nothing but the report is mutated.
    """
    cell = cell_copy("m02-ambiguous-commit")
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


def test_unbound_execution_catches_a_claimed_source_that_is_not_the_bound_call(cell_copy):
    """Round 4's decisive construction, restated as what it checks: correct cardinality,
    disagreeing retained records.

    One bound approved call, one retained effect — but the effect's attestation claims a
    staged-call identity the store does not hold as the bound approved call. Counting
    alone cannot tell that store from the compliant one, so the attestation carries the
    provenance its writer claims and the ceremony joins on that claim. The join settles
    agreement between two retained records and nothing about what caused the effect
    (PREREGISTRATION section 9, "no effect causation").
    """
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"][0]["source"]["action"] = 99
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "unbound-execution"


def test_retained_store_unreadable_on_a_malformed_effect_source(cell_copy):
    """Round 5: the effect's provenance is a closed union, checked at store load.

    A source outside the union is not a detection about the bridge — it is a store this
    apparatus cannot read, exactly like a malformed drain witness.
    """
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"][0]["source"] = {"kind": "hearsay"}
    dump_json(cell / "platform.json", platform)
    assert binding(cell)["code"] == "retained-store-unreadable"


def test_unbound_execution_refuses_an_unstaged_effect_under_an_authorization(cell_copy):
    """The union's other arms name no staged call, and inside the governed inventory that
    is the failure, not an exemption.

    Exactly one effect against exactly one approved bound application, so the cap is
    satisfied and the count clause cannot fire — but the store's own attestation says the
    effect came from the read path, which is not the application the map authorized. The
    detail is asserted so this cannot pass by the arithmetic it is here to bypass.
    """
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    assert len(platform["effects"]) == 1
    platform["effects"][0]["source"] = {"kind": "read-path"}
    dump_json(cell / "platform.json", platform)
    found = binding(cell)
    assert found["code"] == "unbound-execution"
    assert "'read-path' provenance" in found["detail"]


def test_unbound_execution_refuses_an_out_of_band_effect_under_an_authorization(cell_copy):
    """The same for the union's third arm: `out-of-band` names no call either."""
    cell = cell_copy("pos-baseline")
    platform = load_json(cell / "platform.json")
    platform["effects"][0]["source"] = {"kind": "out-of-band"}
    dump_json(cell / "platform.json", platform)
    found = binding(cell)
    assert found["code"] == "unbound-execution"
    assert "'out-of-band' provenance" in found["detail"]


def test_unstaged_effects_still_refuse_on_the_count_under_no_authorization(cell_copy):
    """Where the map authorizes nothing, the zero-authorization clause refuses first.

    That ordering is why this fix changes no registered outcome: `m01`'s read-path effect
    and `b06`'s claimed-but-unretained staged call are both inaction cells, and both are
    refused before the union is consulted at all.
    """
    for cell_id in ("m01-readonly-bypass", "b06-unbound-execution"):
        found = binding(cell_copy(cell_id))
        assert found["code"] == "unbound-execution"
        assert "no approved action record bound to this commitment" in found["detail"]


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
    cells.append(("near-miss-created-at", stamped))

    renamed = cell_copy("s02-unknown-auto-applied")
    ledger = load_json(renamed / "ledger.json")
    ledger[0]["resolvedBy"]["name"] = "Someone Else"
    dump_json(renamed / "ledger.json", ledger)
    cells.append(("resolver-name-substituted", renamed))

    verdicts = cf_runner.ceremony(cells)["cells"]
    assert verdicts["duplicate-gatekeeper-id"]["code"] == "classification-refused"
    assert verdicts["near-miss-created-at"]["code"] == "drain-order-violation"
    assert verdicts["resolver-name-substituted"]["code"] == "drain-order-violation"


def _variant(tmp_path, name, cell_id="pos-baseline"):
    """A named copy of a frozen locked cell — one batch invocation carries many of them,
    so each needs its own directory (`cell_copy` keys on the cell id alone)."""
    source = (
        STUDY / "fixtures" / "baseline"
        if cell_id == "pos-baseline"
        else STUDY / "fixtures" / "mutations" / cell_id
    )
    target = tmp_path / name
    shutil.copytree(source, target)
    return target


def test_upstream_refuses_alias_identities_contradicted_witnesses_and_near_misses(
    tmp_path, cfos_source
):
    """Round 6's node-side repairs, in one batched runner invocation.

    Three families, and each used to end somewhere other than a refusal: an identity the
    two layers read differently (R6-3), a witness the check never looked at because the
    ledger claimed nothing (R6-4), and a stamp `Date.parse` normalized or collapsed
    instead of refusing (R6-5). The equality half of the registered `resolved < at`
    boundary is `pos-baseline` itself, which passes above; the half below it is here.
    """
    del cfos_source
    cells = []

    alias = _variant(tmp_path, "float-gatekeeper-id")
    _second_gatekeeper_with_id(alias, "1.0")
    cells.append(("float-gatekeeper-id", alias))

    boundary = _variant(tmp_path, "unsafe-gatekeeper-id")
    _second_gatekeeper_with_id(boundary, "9007199254740992")
    cells.append(("unsafe-gatekeeper-id", boundary))

    negative_zero = _variant(tmp_path, "negative-zero-gatekeeper-id")
    _second_gatekeeper_with_id(negative_zero, "-0")
    cells.append(("negative-zero-gatekeeper-id", negative_zero))

    # R6-3's disposition claimed four constructions here and carried three; round 7 (R6-3
    # residue) found the Boolean missing. `true` coerces to 1 in JavaScript and is an `int`
    # subclass in Python, so it is the one alias both languages produce on their own.
    boolean = _variant(tmp_path, "boolean-gatekeeper-id")
    _second_gatekeeper_with_id(boolean, "true")
    cells.append(("boolean-gatekeeper-id", boolean))

    joined = _variant(tmp_path, "duplicate-ledger-join-identity")
    ledger = load_json(joined / "ledger.json")
    twin = json.loads(json.dumps(ledger[0]))
    twin["id"] = 2
    ledger.append(twin)  # the same (gatekeeperId, action) — never checked on this side
    dump_json(joined / "ledger.json", ledger)
    cells.append(("duplicate-ledger-join-identity", joined))

    contradicted = _variant(tmp_path, "witness-the-ledger-contradicts")
    ledger = load_json(contradicted / "ledger.json")
    ledger[0]["autoApproved"] = False
    dump_json(contradicted / "ledger.json", ledger)
    cells.append(("witness-the-ledger-contradicts", contradicted))

    calendar = _variant(tmp_path, "impossible-calendar-witness")
    platform = load_json(calendar / "platform.json")
    platform["drainWitnesses"][0]["at"] = "2026-02-29T00:31:00.000Z"
    dump_json(calendar / "platform.json", platform)
    cells.append(("impossible-calendar-witness", calendar))

    submillisecond = _variant(tmp_path, "sub-millisecond-boundary")
    ledger = load_json(submillisecond / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.0004Z"
    dump_json(submillisecond / "ledger.json", ledger)
    platform = load_json(submillisecond / "platform.json")
    platform["drainWitnesses"][0]["at"] = "2026-08-01T00:31:00.0005Z"
    dump_json(submillisecond / "platform.json", platform)
    cells.append(("sub-millisecond-boundary", submillisecond))

    earlier = _variant(tmp_path, "resolved-strictly-before-the-witness")
    ledger = load_json(earlier / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:30:00.000Z"
    dump_json(earlier / "ledger.json", ledger)
    cells.append(("resolved-strictly-before-the-witness", earlier))

    verdicts = cf_runner.ceremony(cells)["cells"]
    for cell_id in (
        "float-gatekeeper-id",
        "unsafe-gatekeeper-id",
        "negative-zero-gatekeeper-id",
        "boolean-gatekeeper-id",
        "duplicate-ledger-join-identity",
    ):
        assert verdicts[cell_id]["code"] == "classification-refused", cell_id
    for cell_id in (
        "witness-the-ledger-contradicts",
        "impossible-calendar-witness",
        "sub-millisecond-boundary",
        "resolved-strictly-before-the-witness",
    ):
        assert verdicts[cell_id]["code"] == "drain-order-violation", cell_id


def test_upstream_reads_lone_identity_tokens_stamps_and_an_empty_witness(
    tmp_path, cfos_source
):
    """Round 7's node-side repairs, in one batched runner invocation.

    Each condition is one this runner used to answer differently from the binding layer
    over the same retained bytes — which is the defect, whichever side is right. The first
    three are refusals this side did not make; the last is a refusal it made and should
    not have.

    The identity pairs are LONE values, not duplicates. Round 6's constructions appended a
    second gatekeeper, so both sides refused them as ambiguous stores and the divergence in
    what an identity *is* stayed invisible (R7-2).
    """
    del cfos_source
    cells = []

    lone_float = _variant(tmp_path, "lone-float-identity")
    _sole_gatekeeper_id_literal(lone_float, "1.0")
    cells.append(("lone-float-identity", lone_float))

    lone_exponent = _variant(tmp_path, "lone-exponent-identity")
    _sole_gatekeeper_id_literal(lone_exponent, "1e0")
    cells.append(("lone-exponent-identity", lone_exponent))

    unicode_digits = _variant(tmp_path, "unicode-digit-stamp")
    ledger = load_json(unicode_digits / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.٠٠٠Z"
    dump_json(unicode_digits / "ledger.json", ledger)
    cells.append(("unicode-digit-stamp", unicode_digits))

    trailing_newline = _variant(tmp_path, "trailing-newline-stamp")
    ledger = load_json(trailing_newline / "ledger.json")
    ledger[0]["appliedAt"] = "2026-08-01T00:31:00.000Z\n"
    dump_json(trailing_newline / "ledger.json", ledger)
    cells.append(("trailing-newline-stamp", trailing_newline))

    # A manual approval beside a drain pass that found nothing to do: no rule was in force,
    # the pinned drainer applies nothing, and the witness records exactly that. Round 6's
    # reverse accounting asked whether the witness's gatekeeper appeared among the ledger's
    # claims rather than whether the two lists agreed, so this coherent pass was refused for
    # claiming an application it does not claim (R7-4).
    empty_witness = _variant(tmp_path, "engaged-empty-witness")
    ledger = load_json(empty_witness / "ledger.json")
    ledger[0]["autoApproved"] = False
    dump_json(empty_witness / "ledger.json", ledger)
    platform = load_json(empty_witness / "platform.json")
    platform["autoApproveTags"] = []
    for witness in platform["drainWitnesses"]:
        witness["appliedActionIds"] = []
        witness["rules"] = []
    dump_json(empty_witness / "platform.json", platform)
    cells.append(("engaged-empty-witness", empty_witness))

    verdicts = cf_runner.ceremony(cells)["cells"]
    for cell_id in ("lone-float-identity", "lone-exponent-identity"):
        assert verdicts[cell_id]["code"] == "classification-refused", cell_id
    for cell_id in ("unicode-digit-stamp", "trailing-newline-stamp"):
        assert verdicts[cell_id]["code"] == "drain-order-violation", cell_id
    coherent = verdicts["engaged-empty-witness"]
    assert coherent["verdict"] == "pass", coherent
    assert "AutoApprovalDrainer" in coherent["engaged"], coherent


def test_upstream_holds_the_witness_to_the_same_identity_rule(tmp_path, cfos_source):
    """Round 8 (R8-3): the identity repair had not reached the witness's own identities.

    A witness written `"pass": 1.0` or `"pass": 1e0` arrived at `witnesses.sort((a, b) =>
    a.pass - b.pass)` as a `NonIntegerLexeme`, so the comparator returned `NaN`, the sort
    did nothing, and the cell came out `pass` with `AutoApprovalDrainer` engaged — over
    bytes the binding layer refuses as `retained-store-unreadable` (the two rows above).
    That is one store with two readings, which is the R7-2 defect surviving at the one
    identity R7-2's repair did not cover.

    Each layer keeps its own vocabulary — the binding layer calls an unreadable store
    unreadable, this one refuses the pass it cannot order — and the registered property is
    that neither reads the store where the other refuses it.
    """
    del cfos_source
    cells = []
    for name, raw in (("witness-pass-float", "1.0"), ("witness-pass-exponent", "1e0")):
        variant = _variant(tmp_path, name)
        _witness_pass_literal(variant, raw)
        cells.append((name, variant))

    verdicts = cf_runner.ceremony(cells)["cells"]
    for cell_id, _ in cells:
        assert verdicts[cell_id]["code"] == "drain-order-violation", cell_id


def test_upstream_apparatus_self_report_matches_pins(upstream_verdicts):
    pins = load_json(STUDY / "harness" / "PINS.json")
    apparatus = upstream_verdicts["apparatus"]
    assert apparatus["cloneCommit"] == pins["cloudflareOs"]["commit"]
    assert apparatus["cloneTrackedClean"] is True
    assert apparatus["probedFiles"] == pins["cloudflareOs"]["probedFiles"]
    assert apparatus["nodeVersion"] == pins["harnessNode"]["version"]
