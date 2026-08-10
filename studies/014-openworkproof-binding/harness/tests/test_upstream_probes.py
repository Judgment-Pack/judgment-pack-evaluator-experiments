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
    """The mechanism `e21` is named for, reached directly.

    The grant is left exactly as issued (which is what keeps identity/digest
    consistency satisfied) and the executed call is moved instead, so the only
    thing left to refuse is `grant.valid_from <= requested_at <= occurred_at <=
    grant.expires_at`.
    """
    from openworkproof.composition import replay_authorization_causality
    from openworkproof.policy import AuthorizationPolicyError, replay_authorization_policy

    raw = bundle()
    work_order, receipts, grants, attempts = models(raw)
    causal_state = replay_authorization_causality(work_order, receipts)
    replay_authorization_policy(
        work_order, keyed(grants), keyed(attempts, "digest"), receipts, causal_state
    )

    developer_grant = next(
        grant for grant in grants if grant.subject_agent_id == "developer"
    )
    outside = developer_grant.expires_at + timedelta(days=1)
    stamp = outside.strftime("%Y-%m-%dT%H:%M:%SZ")

    mutated = copy.deepcopy(raw)
    receipt = mutated["receipts"][executing_index(mutated)]
    receipt["occurred_at"] = stamp
    receipt["nested_claim"]["requested_at"] = stamp
    work_order, receipts, grants, attempts = models(mutated)
    causal_state = replay_authorization_causality(work_order, receipts)
    with pytest.raises(AuthorizationPolicyError) as error:
        replay_authorization_policy(
            work_order, keyed(grants), keyed(attempts, "digest"), receipts, causal_state
        )
    assert "Grant call binding failed semantic replay" in str(error.value)


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
