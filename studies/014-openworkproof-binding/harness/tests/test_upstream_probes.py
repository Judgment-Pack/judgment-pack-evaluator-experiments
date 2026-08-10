"""Focused probes of the upstream mechanisms three matrix cells cannot reach.

Round 1 established that `e21`, `f23` and `f25` do not exercise the refusals they
are named for: `e21` trips grant identity/digest consistency against the issuance
receipt before any window logic, and `f23`/`f25` trip prefix adjacency before any
exact-parent logic. Those cells are re-registered as generic upstream-corruption
controls, and the named mechanisms are demonstrated here instead, by calling the
pinned package's own functions directly. These probes are not matrix cells, are
not adjudicated, and support no R1 claim: they answer "does the mechanism the cell
was named for exist and fire", and nothing else.

Run: JPACK_BIN=... OWP_SOURCE=... <venv>/bin/python -m pytest harness/tests -q
"""

import copy
import json
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

import pytest

from conftest import STUDY, owp_source  # noqa: E402

sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

BASELINE = STUDY / "fixtures" / "baseline"


def bundle():
    return json.loads((BASELINE / "bundle.json").read_text(encoding="utf-8"))


def models(raw):
    """The baseline bundle rebuilt into upstream's own models."""
    from openworkproof.models import ACTION_RECEIPT_ADAPTER, CapabilityGrant, WorkOrder

    work_order = WorkOrder.model_validate(raw["work_order"])
    receipts = tuple(
        ACTION_RECEIPT_ADAPTER.validate_python(item) for item in raw["receipts"]
    )
    grants = tuple(
        CapabilityGrant.model_validate(item)
        for item in sorted(raw["effective_grants"], key=lambda i: i["grant_id"])
    )
    attempts = tuple(
        CapabilityGrant.model_validate(item)
        for item in sorted(raw["grant_attempts"], key=lambda i: i["digest"])
    )
    return work_order, receipts, grants, attempts


def keyed(grants, attribute="grant_id"):
    """Upstream's replay entry points take grants as mappings, not sequences."""
    return {getattr(grant, attribute): grant for grant in grants}


def executing_index(raw):
    for index, receipt in enumerate(raw["receipts"]):
        if receipt.get("tool_name") == "owp.apply_patch":
            return index
    raise AssertionError("baseline bundle carries no executing receipt")


def grant_issuance_index(raw, subject_agent_id):
    grant_ids = {
        grant["grant_id"]
        for grant in raw["effective_grants"]
        if grant["subject_agent_id"] == subject_agent_id
    }
    for index, receipt in enumerate(raw["receipts"]):
        if receipt.get("issued_grant_id") in grant_ids:
            return index
    raise AssertionError("baseline bundle carries no issuance for " + subject_agent_id)


# --------------------------------------------------------------------------
# (b) exact-parent-set refusal — the mechanism f23 and f25 are named for
# --------------------------------------------------------------------------

def test_causal_replay_refuses_a_wrong_parent():
    """The mechanism `f23` is named for, reached directly."""
    from openworkproof.composition import (
        AuthorizationCausalityError,
        replay_authorization_causality,
    )

    raw = bundle()
    baseline_work_order, baseline_receipts, _, _ = models(raw)
    replay_authorization_causality(baseline_work_order, baseline_receipts)

    mutated = copy.deepcopy(raw)
    receipt = mutated["receipts"][executing_index(mutated)]
    verifier = mutated["receipts"][grant_issuance_index(mutated, "verifier")]
    receipt["parent_receipt_ids"] = sorted(
        {verifier["receipt_id"], receipt["parent_receipt_ids"][-1]},
        key=lambda item: next(
            candidate["sequence"]
            for candidate in mutated["receipts"]
            if candidate["receipt_id"] == item
        ),
    )
    work_order, receipts, _, _ = models(mutated)
    with pytest.raises(AuthorizationCausalityError) as error:
        replay_authorization_causality(work_order, receipts)
    assert "causal parents failed exact historical replay" in str(error.value)


def test_causal_replay_refuses_a_parent_superset():
    """The mechanism `f25` is named for: exact equality refuses supersets too."""
    from openworkproof.composition import (
        AuthorizationCausalityError,
        replay_authorization_causality,
    )

    mutated = copy.deepcopy(bundle())
    receipt = mutated["receipts"][executing_index(mutated)]
    verifier = mutated["receipts"][grant_issuance_index(mutated, "verifier")]
    sequence = {
        item["receipt_id"]: item["sequence"] for item in mutated["receipts"]
    }
    receipt["parent_receipt_ids"] = sorted(
        set(receipt["parent_receipt_ids"]) | {verifier["receipt_id"]},
        key=lambda item: sequence[item],
    )
    work_order, receipts, _, _ = models(mutated)
    with pytest.raises(AuthorizationCausalityError) as error:
        replay_authorization_causality(work_order, receipts)
    assert "causal parents failed exact historical replay" in str(error.value)


# --------------------------------------------------------------------------
# (a) grant-window replay refusal — the mechanism e21 is named for
# --------------------------------------------------------------------------

def test_policy_replay_refuses_a_call_outside_its_grant_window():
    """The mechanism `e21` is named for, reached at the branch that owns it.

    Round 2 found the earlier version of this probe false attribution: it moved
    the executed call one day past the grant's expiry, which is also one day past
    the WorkOrder deadline (every delegated grant expires exactly there), so the
    *WorkOrder*-window branch raised `Grant call binding failed semantic replay`
    before the grant-authority window was ever consulted.

    The rebuilt construction moves the grant instead and keeps the call where it
    was. The executed instant stays strictly inside the WorkOrder window; the
    grant is validly re-signed by its issuer with a strictly later `valid_from`
    that is still `<= expires_at`, so it remains internally consistent. The only
    predicate left to fail is the grant's own charge-authority window, and the
    probe asserts both halves: the grant-authority message fires, and the
    WorkOrder-window message does not.
    """
    from openworkproof.composition import replay_authorization_causality
    from openworkproof.policy import AuthorizationPolicyError, replay_authorization_policy
    from openworkproof.signing import sign_payload

    sys.path.insert(0, str(STUDY / "harness"))
    import owpflow

    raw = bundle()
    work_order, receipts, grants, attempts = models(raw)
    causal_state = replay_authorization_causality(work_order, receipts)
    replay_authorization_policy(
        work_order, keyed(grants), keyed(attempts, "digest"), receipts, causal_state
    )

    developer_grant = next(
        grant for grant in grants if grant.subject_agent_id == "developer"
    )
    executed = receipts[executing_index(raw)]
    # The premise the probe depends on: the executed instant is inside the
    # WorkOrder window, so the earlier branch cannot be what fires.
    assert work_order.issued_at <= executed.occurred_at <= work_order.deadline
    assert (
        work_order.issued_at
        <= executed.nested_claim.requested_at
        <= work_order.deadline
    )

    later_valid_from = executed.occurred_at + timedelta(seconds=25)
    assert later_valid_from < developer_grant.expires_at, (
        "the narrowed grant window must stay internally consistent"
    )
    stamp = later_valid_from.strftime("%Y-%m-%dT%H:%M:%SZ")

    keys = owpflow.role_keys()
    mutated = copy.deepcopy(raw)
    for index, document in enumerate(mutated["effective_grants"]):
        if document["subject_agent_id"] != "developer":
            continue
        narrowed = copy.deepcopy(document)
        narrowed["valid_from"] = stamp
        mutated["effective_grants"][index] = sign_payload(
            "capability-grant", narrowed, keys["Manager"][0]
        )
        break
    else:  # pragma: no cover - the baseline always carries a developer grant
        raise AssertionError("baseline bundle carries no developer grant")

    work_order, receipts, grants, attempts = models(mutated)
    causal_state = replay_authorization_causality(work_order, receipts)
    with pytest.raises(AuthorizationPolicyError) as error:
        replay_authorization_policy(
            work_order, keyed(grants), keyed(attempts, "digest"), receipts, causal_state
        )
    message = str(error.value)
    assert "Grant charge authority failed semantic replay" in message
    assert "Grant call binding failed semantic replay" not in message, (
        "the WorkOrder-window branch fired instead of the grant-authority branch"
    )


# --------------------------------------------------------------------------
# (c) out-of-window publication refusal — why e21 has to be post-hoc at all
# --------------------------------------------------------------------------

def test_publication_refuses_an_execution_after_the_work_order_deadline(source):
    """The live path will not construct the attack `e21` describes.

    Publication demands `occurred_at == clock()` and `occurred_at <= deadline`,
    and every delegated grant expires exactly at the deadline, so an executing
    call outside its authorization window cannot be published at all. That is why
    `e21` exists only as a post-hoc substitution.
    """
    import owpflow
    from commitment import ACTION_PATH, action_patch_bytes

    facts = {
        "expense": {
            "type": "employee-expense",
            "amount": "250.00",
            "category": "travel",
            "activeInvestigation": False,
        }
    }
    directory = Path(tempfile.mkdtemp(prefix="study014-probe-"))
    with pytest.raises(Exception) as error:
        owpflow.run_flow(
            directory,
            objective="Apply a deterministic patch and verify it.",
            patch_bytes=action_patch_bytes(facts),
            target_paths=[ACTION_PATH],
            patch_occurred_at="2026-01-03T00:00:00Z",
            salt="probe-outside-window",
            owp_source=source,
        )
    assert "does not extend the authority tip" in str(error.value)


# --------------------------------------------------------------------------
# (d) the retry episode — is a second active patch publishable at all? (R2-3)
# --------------------------------------------------------------------------

PROBE_FACTS = {
    "expense": {
        "type": "employee-expense",
        "amount": "250.00",
        "category": "travel",
        "activeInvestigation": False,
    }
}


def _snapshot_stub(request):
    """The same execution-snapshot stand-in the builder uses (offline probe)."""
    from openworkproof.repo_tools import CandidateExecutionSnapshot, ExecutionSnapshotPlan

    return CandidateExecutionSnapshot(
        head_commit=request.expected_head_commit,
        workspace_manifest_digest=request.expected_workspace_manifest_digest,
        plan=ExecutionSnapshotPlan(
            files=(),
            read_only=True,
            owner_uid=65532,
            owner_gid=65532,
            atime_unix_seconds=0,
            mtime_unix_seconds=0,
            clear_extended_attributes=True,
            clear_posix_acls=True,
            clear_file_capabilities=True,
        ),
    )


def test_the_retry_route_to_a_second_active_patch_dead_ends(source):
    """`d18`'s deferred construction, driven to its end on the live path.

    Round 2 refused to let the retry route be registered as an assumed OWP-pass
    construction on the strength of a code reading. This probe drives it:
    first patch -> failing verifier run -> `owp.rollback_patch` ->
    `owp.start_retry` -> second `owp.repo_read` -> second `owp.apply_patch`,
    through the pinned package's own entry points, and asserts whichever outcome
    is true.

    The study's own developer grant carries exactly three tool calls — the read,
    the patch and the rollback — so a probe run on it would only ever rediscover
    `QUOTA_EXHAUSTED`, a fixture-configuration answer to a protocol question. The
    probe therefore widens that one grant (`owpflow.DEVELOPER_QUOTA`) and nothing
    else, so what refuses is the protocol.

    Recorded outcome at this commit: the rollback and the retry consumption both
    publish; the second `owp.repo_read` does **not**, because publication demands
    the retry receipt be among the new receipt's causal parents while a read's
    protocol parent set is its grant issuance alone; and a second
    `owp.apply_patch` that *does* name the retry tip publishes but then fails
    causal replay. No live-path second active patch survives verification.
    """
    import json as _json
    from unittest import mock

    import openworkproof.evidence as evidence
    import openworkproof.mcp_server as mcp_server
    import owpflow
    from commitment import ACTION_PATH, action_patch_bytes
    from openworkproof import repo_tools
    from openworkproof.composition import (
        AuthorizationCausalityError,
        replay_authorization_causality,
    )
    from openworkproof.models import (
        AgentRequest,
        RepoReadArguments,
        TestResultEvidence,
        request_arguments_digest,
    )
    from openworkproof.policy import (
        AuthorizationLedgerPrefix,
        CommittedEvidence,
        ProspectiveExecutionFacts,
        derive_authorization_context,
    )
    from openworkproof.repo_tools import ReplayCheckpoint
    from openworkproof.signing import sign_payload

    upstream = owpflow.load_upstream(source)
    m2 = upstream["m2"]
    mcp = upstream["mcp"]
    keys = owpflow.role_keys()
    now = owpflow.fixed_now()
    salt = "retry-episode-probe"
    entropy = owpflow.DeterministicEntropy(salt)
    root = Path(tempfile.mkdtemp(prefix="study014-retry-probe-"))

    with mock.patch("secrets.token_hex", entropy.token_hex), mock.patch.object(
        repo_tools, "prepare_candidate_execution_snapshot", _snapshot_stub
    ):
        archive = owpflow.source_archive(upstream)
        document = owpflow.work_order_document(
            upstream, objective="Apply a deterministic patch and verify it.",
            archive=archive,
        )
        work_order = owpflow.signed_work_order(upstream, document, keys)
        parsed = owpflow.parsed_source(upstream, work_order, archive)
        case = owpflow._case(
            upstream,
            root,
            work_order,
            keys,
            now,
            salt=salt,
            parsed=parsed,
            developer_quota={"tool_calls": 6, "repair_rounds": 0},
        )
        source_checkpoint = case["checkpoint"]

        owpflow._repo_read(
            upstream, case, keys, now, salt=salt, context_source_digest="b" * 64
        )
        owpflow._publish_action_patch(
            upstream,
            case,
            keys,
            now,
            salt=salt,
            patch_bytes=action_patch_bytes(PROBE_FACTS),
            target_paths=[ACTION_PATH],
            context_source_digest="b" * 64,
            occurred_at=owpflow.PATCH_OCCURRED_AT,
            parents=owpflow.patch_parent_ids(case),
        )
        first_patch = case["patch_receipt"]

        # 1. a failing verifier run puts the work order in needs_rework.
        case["context"] = m2._refresh_context(case, case["checkpoint"], now)
        request, arguments, facts = m2._verifier_run_tests_request(
            case, case["checkpoint"], keys, now
        )
        case["request"], case["arguments"], case["facts"] = request, arguments, facts
        failure = mcp._execute_run_tests_case(
            case,
            case["ledger_path"].parent,
            keys,
            mcp._FakeRunTestsExecutionDriver(actual_exit_code=1),
            context=case["context"],
            request=request,
            request_arguments=arguments,
            execution_facts=facts,
            candidate_snapshot_request=mcp._run_tests_snapshot_request(
                case, case["ledger_path"].parent
            ),
            now=now,
        )
        assert failure.state_after == "needs_rework"

        # 2. the rollback of the active patch.
        receipts, grants, attempts = upstream["chain"]._grant_replay_inputs(
            case["ledger_path"], case["work_order"]
        )
        committed = []
        for receipt in receipts:
            for reference in receipt.evidence_refs:
                payload = (
                    case["evidence_root"] / reference.path.removeprefix("evidence/")
                ).read_bytes()
                committed.append(
                    CommittedEvidence(reference=reference, payload=payload)
                )
        failure_payload = next(
            item.payload
            for item in committed
            if item.reference in failure.evidence_refs
        )
        checkpoint = ReplayCheckpoint(
            files=case["checkpoint"].files,
            head_commit=case["checkpoint"].head_commit,
            workspace_manifest=case["checkpoint"].workspace_manifest,
            workspace_manifest_digest=case["checkpoint"].workspace_manifest_digest,
            verified_test_results=(
                TestResultEvidence.model_validate_json(failure_payload),
            ),
        )
        context = derive_authorization_context(
            case["work_order"],
            AuthorizationLedgerPrefix(
                effective_grants=tuple(
                    sorted(grants.values(), key=lambda item: item.grant_id)
                ),
                grant_attempts=tuple(
                    sorted(attempts.values(), key=lambda item: item.digest)
                ),
                receipts=receipts,
            ),
            tuple(committed),
            checkpoint,
            now,
        )
        rollback_arguments = {
            "target_patch_receipt_id": first_patch.receipt_id,
            "target_patch_digest": first_patch.digest,
            "before_commit": checkpoint.head_commit,
        }
        developer = keys["Developer"][1]
        rollback_request = AgentRequest.model_validate(
            sign_payload(
                "agent-request",
                {
                    "claim_type": "agent-request",
                    "work_order_digest": case["work_order"].digest,
                    "grant_id": case["developer"].grant_id,
                    "actor_id": developer["subject_id"],
                    "actor_key_id": developer["key_id"],
                    "tool_name": "owp.rollback_patch",
                    "arguments_digest": request_arguments_digest(
                        "owp.rollback_patch", rollback_arguments
                    ),
                    "nonce": owpflow.nonce(salt, "rollback"),
                    "requested_at": owpflow.PATCH_REQUESTED_AT,
                    "authentication_method": "agent_signature",
                    "model_id": "model",
                    "model_version": "1",
                    "prompt_template_digest": "a" * 64,
                    "context_source_digest": "b" * 64,
                },
                keys["Developer"][0],
            )
        )
        rollback = mcp_server.execute_rollback(
            case["ledger_path"],
            evidence_root=case["evidence_root"],
            context=context,
            request=rollback_request,
            execution_facts=ProspectiveExecutionFacts(
                execution_context_id="3" * 64,
                container_instance_id_digest="4" * 64,
                controller_id=keys["Sidecar"][1]["key_id"],
            ),
            sidecar_private_key=keys["Sidecar"][0],
            handler=mcp_server.make_candidate_rollback_handler(
                workspace=case["workspace"],
                failure_target_patch_receipt_id=first_patch.receipt_id,
                failure_target_patch_receipt_digest=first_patch.digest,
                before_commit=checkpoint.head_commit,
                before_manifest_digest=checkpoint.workspace_manifest_digest,
                parent_commit=source_checkpoint.head_commit,
                parent_manifest_digest=source_checkpoint.workspace_manifest_digest,
            ),
            clock=lambda: now,
        )
        assert rollback.execution_status == "succeeded"

        # 3. the retry consumption — upstream's own repair-round episode.
        root_grant = case["root"]
        role = next(
            name
            for name in owpflow.ROLES
            if keys[name][1]["key_id"] == root_grant.subject_key_id
        )
        retry_arguments = {
            "grant_id": root_grant.grant_id,
            "metric": "repair_rounds",
            "amount": 1,
        }
        retry = evidence.start_retry(
            case["ledger_path"],
            request=AgentRequest.model_validate(
                sign_payload(
                    "agent-request",
                    {
                        "claim_type": "agent-request",
                        "work_order_digest": case["work_order"].digest,
                        "grant_id": root_grant.grant_id,
                        "actor_id": root_grant.subject_agent_id,
                        "actor_key_id": root_grant.subject_key_id,
                        "tool_name": "owp.start_retry",
                        "arguments_digest": request_arguments_digest(
                            "owp.start_retry", retry_arguments
                        ),
                        "nonce": owpflow.nonce(salt, "start-retry"),
                        "requested_at": owpflow.PATCH_REQUESTED_AT,
                        "authentication_method": "agent_signature",
                        "model_id": "model",
                        "model_version": "1",
                        "prompt_template_digest": "a" * 64,
                        "context_source_digest": "b" * 64,
                    },
                    keys[role][0],
                )
            ),
            sidecar_private_key=keys["Sidecar"][0],
            evidence_root=case["evidence_root"],
            clock=lambda: now,
        )
        assert retry.state_after == "retrying"

        # 4. the second repo_read: unpublishable. Publication requires the tip
        #    (the retry receipt) among the parents; a read's protocol parent set
        #    is its grant issuance alone, and upstream computes that set itself.
        case["checkpoint"] = source_checkpoint
        case["context"] = m2._refresh_context(case, source_checkpoint, now)
        read_arguments = RepoReadArguments(path="src/wrap.py")
        read_request = owpflow._agent_request(
            case,
            keys,
            role="Developer",
            tool_name="owp.repo_read",
            arguments=read_arguments,
            nonce_value=owpflow.nonce(salt, "second-repo-read"),
            context_source_digest="b" * 64,
            requested_at=owpflow.PATCH_REQUESTED_AT,
        )
        with pytest.raises(Exception) as error:
            mcp_server.execute_repo_read(
                case["ledger_path"],
                evidence_root=case["evidence_root"],
                context=case["context"],
                request=read_request,
                request_arguments=read_arguments,
                execution_facts=ProspectiveExecutionFacts(
                    execution_context_id="1" * 64,
                    container_instance_id_digest="2" * 64,
                    controller_id=keys["Sidecar"][1]["key_id"],
                ),
                sidecar_private_key=keys["Sidecar"][0],
                candidate_runtime_root=case["workspace"].worktree,
                handler=mcp_server.make_repo_pipeline_read_handler(),
                clock=lambda: now,
            )
        assert "does not extend the authority tip" in str(error.value)
        assert "QUOTA_EXHAUSTED" not in str(error.value), (
            "the probe must not be answering a quota question"
        )

        # 5. a second apply_patch that DOES name the retry tip publishes — and
        #    the published chain then fails causal replay, which is the end of
        #    the route. Both halves are asserted, because either alone would
        #    overstate what upstream refuses.
        alternate = _json.loads(_json.dumps(PROBE_FACTS))
        alternate["expense"]["amount"] = "90.00"
        case["previous_receipt"] = retry
        sequence = {
            item.receipt_id: item.sequence
            for item in (case["developer_issuance"], case["repo_read_receipt"], retry)
        }
        parents = tuple(
            sorted(
                (
                    case["developer_issuance"].receipt_id,
                    case["repo_read_receipt"].receipt_id,
                    retry.receipt_id,
                ),
                key=lambda item: sequence[item],
            )
        )
        second_patch = owpflow._publish_action_patch(
            upstream,
            case,
            keys,
            now,
            salt=salt,
            patch_bytes=action_patch_bytes(alternate),
            target_paths=[ACTION_PATH],
            context_source_digest="b" * 64,
            occurred_at=owpflow.PATCH_OCCURRED_AT,
            parents=parents,
            ordinal=2,
            nonce_label="second-apply-patch",
        )
        assert second_patch.tool_name == "owp.apply_patch"

        receipts, _, _ = upstream["chain"]._grant_replay_inputs(
            case["ledger_path"], case["work_order"]
        )
        with pytest.raises(AuthorizationCausalityError) as error:
            replay_authorization_causality(case["work_order"], receipts)
        assert "causal parents failed exact historical replay" in str(error.value)
