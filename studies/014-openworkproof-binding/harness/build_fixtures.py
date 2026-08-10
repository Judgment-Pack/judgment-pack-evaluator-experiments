"""One-time deterministic fixture construction for every registered cell.

Builds `fixtures/baseline/` and `fixtures/mutations/<cell-id>/` from
`harness/MATRIX.json`: for each cell a retained artifact set (pack bytes, facts
bytes, evidence bytes, the evaluator envelope, the commitment document), an
OpenWorkProof acceptance bundle, and a SHA-256 manifest.

Two construction families, exactly as the matrix registers them:

  resigned / flow cells   a complete nine-step chain rebuilt with the study's six
                          fixture keys (an insider holding every key), so the OWP
                          chain stays cryptographically valid;
  tampered / artifact     deterministic byte transforms of an already-built cell
                          (signatures left stale, or a retained artifact edited
                          after the decision).

Determinism: fixed keys, fixed clocks, caller-supplied nonces, and a build-time
`secrets.token_hex` patch (see `harness/owpflow.py`). Running this twice from
scratch yields byte-identical trees; a harness test asserts it.

The reviewer-authored holdout stratum has builder hooks here too (`--holdout`),
implemented but never executed: the flag is refused mechanically while
`PINS.json` carries a null preregistration digest, exactly as the scorer refuses
`--include-holdout`.

Run:
    JPACK_BIN=... OWP_SOURCE=... python harness/build_fixtures.py [--out DIR] [--force]
    JPACK_BIN=... OWP_SOURCE=... python harness/build_fixtures.py --holdout   # post-freeze
"""

import argparse
import base64
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import owpflow  # noqa: E402
import verify  # noqa: E402
from commitment import (  # noqa: E402
    ACTION_PATH,
    ACTION_TOOL,
    action_arguments,
    action_arguments_digest,
    action_patch_bytes,
    authorized_action,
    build_commitment,
    commitment_bytes,
    commitment_digest,
    envelope_disposition,
    sha256_prefixed,
)

PACK_PATH = STUDY / "fixtures" / "minimal-expense-approval.pack.json"
MATRIX_PATH = STUDY / "harness" / "MATRIX.json"

FACTS_BASE = (
    b'{"expense":{"type":"employee-expense","amount":"250.00",'
    b'"category":"travel","activeInvestigation":false}}'
)
FACTS_ALT = (
    b'{"expense":{"type":"employee-expense","amount":"90.00",'
    b'"category":"office-supplies","activeInvestigation":false}}'
)
FACTS_REJECT = (
    b'{"expense":{"type":"employee-expense","amount":"250.00",'
    b'"category":"personal","activeInvestigation":false}}'
)
FACTS_NOT_APPLICABLE = (
    b'{"expense":{"type":"vendor-invoice","amount":"250.00",'
    b'"category":"travel","activeInvestigation":false}}'
)
FACTS_240 = (
    b'{"expense":{"type":"employee-expense","amount":"240.00",'
    b'"category":"travel","activeInvestigation":false}}'
)
FACTS_2500 = (
    b'{"expense":{"type":"employee-expense","amount":"2500.00",'
    b'"category":"travel","activeInvestigation":false}}'
)
FACTS_MANUAL_REVIEW = (
    b'{"expense":{"type":"employee-expense","amount":"7500.00",'
    b'"category":"travel","activeInvestigation":false}}'
)
EVIDENCE_PRESENT = b'{"receipt":"present","cost-center":"present"}'
EVIDENCE_ABSENT = b'{"receipt":"absent","cost-center":"present"}'

GENERIC_OBJECTIVE = "Apply a deterministic patch and verify it."

FORGED_APPROVE = {
    "handoff": {"state": "none"},
    "kind": "outcome",
    "outcomeId": "approve",
    "reasons": [],
}
FORGED_UNKNOWN = {
    "handoff": {"state": "requested", "triggeredBy": ["unknown"]},
    "kind": "unresolved",
    "reasons": ["unknown"],
}


class BuildError(RuntimeError):
    """A cell could not be constructed as registered."""


# --------------------------------------------------------------------------
# judgments
# --------------------------------------------------------------------------

def decide(jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes):
    """One pinned evaluation; the retained envelope is the emitted bytes."""
    stdout, returncode = verify.evaluate(
        jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes
    )
    if returncode != 0 or not stdout:
        raise BuildError("the evaluator refused a fixture decision")
    envelope = json.loads(stdout.decode("utf-8"))
    if "disposition" not in envelope:
        raise BuildError("the evaluator produced no disposition")
    return {
        "pack": pack_bytes,
        "facts": facts_bytes,
        "evidence": evidence_bytes,
        "envelope_bytes": stdout,
        "envelope": envelope,
        "disposition": envelope["disposition"],
    }


def commitment_for(decision, executable_digest, *, action="derive", overrides=None,
                   envelope=None):
    """Build a SPEC section 1 commitment, with the study's registered forgeries."""
    envelope = decision["envelope"] if envelope is None else envelope
    facts = json.loads(decision["facts"].decode("utf-8"))
    if action == "derive":
        action_value = authorized_action(envelope_disposition(envelope), facts)
    elif action == "force":
        action_value = {
            "toolName": ACTION_TOOL,
            "argumentsDigest": action_arguments_digest(action_arguments(facts)),
        }
    elif action == "none":
        action_value = None
    else:
        action_value = action
    candidate = build_commitment(
        pack_bytes=decision["pack"],
        facts_bytes=decision["facts"],
        evidence_bytes=decision["evidence"],
        envelope=envelope,
        executable_digest=executable_digest,
        supported_extensions=(),
        action=action_value,
    )
    if overrides:
        candidate["judgment"].update(overrides)
    return candidate


def forged_envelope(decision, disposition):
    """The retained envelope with its disposition member replaced (C13, C14)."""
    envelope = copy.deepcopy(decision["envelope"])
    envelope["disposition"] = copy.deepcopy(disposition)
    return envelope


def envelope_bytes_for(envelope):
    """Compact envelope bytes in the evaluator's own shape (no re-indentation)."""
    return json.dumps(envelope, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------

def payload_for(decision, candidate, bundle, *, envelope_bytes=None):
    return {
        "pack.json": decision["pack"],
        "facts.json": decision["facts"],
        "evidence.json": decision["evidence"],
        "evaluation.json": decision["envelope_bytes"] if envelope_bytes is None
        else envelope_bytes,
        "commitment.json": commitment_bytes(candidate),
        "bundle.json": json.dumps(bundle, indent=2, ensure_ascii=False).encode("utf-8"),
    }


def flow_cell(work_root, decision, candidate, *, salt, objective=None,
              patch_facts=None, target_paths=None, binding_point="apply_patch",
              bind=True, binding_digest=None, envelope_bytes=None,
              owp_source=None, **flow_kwargs):
    """Build one validly signed chain and return its cell payload.

    The patch is derived for the declared target path itself: OWP's parser
    refuses any patch whose derived section paths differ from the declared
    target set, so a cell that moves the target moves the patch's own Git
    header, blob object id and hunk with it.
    """
    facts = json.loads((patch_facts or decision["facts"]).decode("utf-8"))
    paths = list(target_paths or [ACTION_PATH])
    directory = Path(tempfile.mkdtemp(prefix="study014-flow-", dir=str(work_root)))
    bundle = owpflow.run_flow(
        directory,
        objective=commitment_bytes(candidate).decode("utf-8")
        if objective is None
        else objective,
        patch_bytes=action_patch_bytes(facts, path=paths[0]),
        target_paths=paths,
        binding_digest=(
            binding_digest
            if binding_digest is not None
            else (commitment_digest(candidate) if bind else None)
        ),
        binding_point=binding_point if (bind or binding_digest) else None,
        salt=salt,
        owp_source=owp_source,
        **flow_kwargs
    )
    return payload_for(decision, candidate, bundle, envelope_bytes=envelope_bytes)


def bundle_of(payload):
    return json.loads(payload["bundle.json"].decode("utf-8"))


def with_bundle(payload, bundle):
    out = dict(payload)
    out["bundle.json"] = json.dumps(bundle, indent=2, ensure_ascii=False).encode("utf-8")
    return out


def executing_receipt(bundle):
    for receipt in bundle["receipts"]:
        if receipt.get("tool_name") == ACTION_TOOL:
            return receipt
    raise BuildError("bundle carries no executing receipt")


def evidence_entry(bundle, path):
    for entry in bundle["committed_evidence"]:
        if entry["reference"]["path"] == path:
            return entry
    raise BuildError("bundle carries no committed evidence at " + path)


def flip_character(value, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    """Change exactly one character of a token, deterministically."""
    first = value[0]
    index = alphabet.index(first) if first in alphabet else 0
    return alphabet[(index + 1) % len(alphabet)] + value[1:]


def atomic_write_bytes(path, payload):
    """Write through a same-directory temp file + rename.

    Deliberately duplicated from `harness/score.py` rather than imported: the
    scorer imports the builder (post-freeze holdout construction runs inside the
    attempt), so the builder must not import the scorer back.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix="." + path.name + ".", dir=str(path.parent)
    )
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def write_cell(directory, payload):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in verify.CELL_FILES:
        target = directory / name
        if name in payload and payload[name] is not None:
            atomic_write_bytes(target, payload[name])
        elif target.is_file():
            target.unlink()
    atomic_write_bytes(
        directory / verify.MANIFEST_NAME,
        verify.manifest_text(directory).encode("utf-8"),
    )


# --------------------------------------------------------------------------
# the build
# --------------------------------------------------------------------------

def build_payloads(jpack_bin, work_root, owp_source):
    """Every registered cell's payload, keyed by cell id."""
    executable_digest = "sha256:" + verify.sha256_file(jpack_bin)
    pack_bytes = PACK_PATH.read_bytes()
    judgments = Path(tempfile.mkdtemp(prefix="study014-jps-", dir=str(work_root)))

    base = decide(jpack_bin, judgments, pack_bytes, FACTS_BASE, EVIDENCE_PRESENT)
    alt = decide(jpack_bin, judgments, pack_bytes, FACTS_ALT, EVIDENCE_PRESENT)
    rejected = decide(jpack_bin, judgments, pack_bytes, FACTS_REJECT, EVIDENCE_PRESENT)
    absent = decide(jpack_bin, judgments, pack_bytes, FACTS_BASE, EVIDENCE_ABSENT)
    inapplicable = decide(
        jpack_bin, judgments, pack_bytes, FACTS_NOT_APPLICABLE, EVIDENCE_PRESENT
    )
    manual_review = decide(
        jpack_bin, judgments, pack_bytes, FACTS_MANUAL_REVIEW, EVIDENCE_PRESENT
    )
    if manual_review["disposition"].get("outcomeId") != "manual-review":
        raise BuildError("the manual-review fixture facts do not produce manual-review")

    base_commitment = commitment_for(base, executable_digest)
    alt_commitment = commitment_for(alt, executable_digest)
    cells = {}

    def flow(cell_id, decision, candidate, **kwargs):
        cells[cell_id] = flow_cell(
            work_root,
            decision,
            candidate,
            salt=cell_id,
            owp_source=owp_source,
            **kwargs
        )
        return cells[cell_id]

    # ---- positive control -------------------------------------------------
    baseline = flow("pos-baseline", base, base_commitment)

    # ---- negative controls (tampered bytes, stale signatures) -------------
    bundle = bundle_of(baseline)
    bundle["acceptance_receipt"]["signature"] = flip_character(
        bundle["acceptance_receipt"]["signature"]
    )
    cells["neg-signature"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    entry = evidence_entry(bundle, "evidence/patch-result/01.json")
    payload = bytearray(base64.b64decode(entry["payload_b64"]))
    payload[-2] = payload[-2] ^ 0x01
    entry["payload_b64"] = base64.b64encode(bytes(payload)).decode("ascii")
    entry["payload_sha256"] = hashlib.sha256(bytes(payload)).hexdigest()
    cells["neg-evidence-digest"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    executing_receipt(bundle)["parent_receipt_ids"].pop()
    cells["neg-parent-ref"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    executing_receipt(bundle)["request_arguments"]["target_paths"] = [
        "decision-actions/disburse-elsewhere.json"
    ]
    cells["neg-action-param"] = with_bundle(baseline, bundle)

    # ---- A: the judgment artifact ----------------------------------------
    drifted = pack_bytes.replace(b'"5000"', b'"6000"')
    if drifted == pack_bytes:
        raise BuildError("pack threshold edit did not apply")
    cells["a01-pack-bytes-drift"] = dict(baseline, **{"pack.json": drifted})

    versioned = pack_bytes.replace(b'"version": "0.1.0"', b'"version": "0.2.0"')
    if versioned == pack_bytes:
        raise BuildError("pack version edit did not apply")
    cells["a02-pack-version-substitution"] = dict(baseline, **{"pack.json": versioned})

    substituted = pack_bytes.replace(
        b'"id": "https://example.com/judgment-packs/expense-approval"',
        b'"id": "https://example.com/judgment-packs/expense-approval-alt"',
    )
    if substituted == pack_bytes:
        raise BuildError("pack id edit did not apply")
    cells["a03-pack-substitution-compatible"] = dict(
        baseline, **{"pack.json": substituted}
    )

    wrong_pack_digest = "sha256:" + hashlib.sha256(b"study-014/wrong-pack").hexdigest()
    bundle = bundle_of(baseline)
    objective = bundle["work_order"]["objective"]
    bundle["work_order"]["objective"] = objective.replace(
        base_commitment["judgment"]["packDigest"], wrong_pack_digest
    )
    if bundle["work_order"]["objective"] == objective:
        raise BuildError("objective pack digest edit did not apply")
    cells["a04-commitment-packdigest-tampered"] = with_bundle(baseline, bundle)

    flow(
        "a04-commitment-packdigest-resigned",
        base,
        commitment_for(
            base, executable_digest, overrides={"packDigest": wrong_pack_digest}
        ),
    )

    cells["a05-pack-artifact-missing"] = dict(baseline, **{"pack.json": None})

    # ---- B: the facts ------------------------------------------------------
    cells["b06-fact-edit-same-disposition"] = dict(baseline, **{"facts.json": FACTS_240})
    cells["b07-facts-doc-substituted"] = dict(baseline, **{"facts.json": FACTS_REJECT})
    cells["b08-same-disposition-different-facts"] = dict(
        baseline, **{"facts.json": FACTS_ALT}
    )
    flow(
        "b09-factsdigest-field-wrong",
        base,
        commitment_for(
            base,
            executable_digest,
            overrides={"factsDigest": sha256_prefixed(FACTS_ALT)},
        ),
    )

    # ---- C: the disposition ------------------------------------------------
    flow("c10-reject-executed", rejected, commitment_for(rejected, executable_digest,
                                                         action="force"))
    flow("c11-unresolved-executed", absent, commitment_for(absent, executable_digest,
                                                           action="force"))
    flow(
        "c12-handoff-requested-executed",
        inapplicable,
        commitment_for(inapplicable, executable_digest, action="force"),
    )

    forged = forged_envelope(rejected, FORGED_APPROVE)
    flow(
        "c13-outcome-forged",
        rejected,
        commitment_for(rejected, executable_digest, envelope=forged),
        envelope_bytes=envelope_bytes_for(forged),
    )

    forged = forged_envelope(absent, FORGED_UNKNOWN)
    flow(
        "c14-reasons-forged",
        absent,
        commitment_for(absent, executable_digest, envelope=forged),
        envelope_bytes=envelope_bytes_for(forged),
        bind=False,
    )

    # c15: an honest manual-review disposition, an honest null action, and an
    # execution that simply omits the marker. Only structural discovery over the
    # action class sees it.
    flow(
        "c15-manual-review-unbound-execution",
        manual_review,
        commitment_for(manual_review, executable_digest),
        bind=False,
    )

    # ---- D: the action -----------------------------------------------------
    bundle = bundle_of(baseline)
    executing_receipt(bundle)["tool_name"] = "owp.repo_read"
    cells["d15-tool-tampered"] = with_bundle(baseline, bundle)

    flow("d15-tool-resigned", base, base_commitment, binding_point="repo_read")

    alt_patch = action_patch_bytes(json.loads(FACTS_ALT.decode("utf-8")))
    bundle = bundle_of(baseline)
    entry = evidence_entry(bundle, "evidence/patch-input/01.diff")
    entry["payload_b64"] = base64.b64encode(alt_patch).decode("ascii")
    entry["payload_sha256"] = hashlib.sha256(alt_patch).hexdigest()
    cells["d16-argument-tampered"] = with_bundle(baseline, bundle)

    flow(
        "d16-argument-resigned",
        base,
        base_commitment,
        target_paths=["decision-actions/disburse-other.json"],
    )

    bundle = bundle_of(baseline)
    entry = evidence_entry(bundle, "evidence/patch-input/01.diff")
    tampered_patch = base64.b64decode(entry["payload_b64"]).replace(
        b'"250.00"', b'"2500.00"'
    )
    entry["payload_b64"] = base64.b64encode(tampered_patch).decode("ascii")
    entry["payload_sha256"] = hashlib.sha256(tampered_patch).hexdigest()
    cells["d17-amount-tampered"] = with_bundle(baseline, bundle)

    flow("d17-amount-resigned", base, base_commitment, patch_facts=FACTS_2500)

    # d18: the surplus arm of exact-set totality. A second live patch round is
    # not constructible at this commit (three independent upstream refusals,
    # recorded in harness/owpflow.py; the deferred retry route dead-ends as
    # well, per the retry-episode probe), so the extra execution is a CLONE of
    # the executing receipt inserted post-hoc with the outer envelope alone
    # re-signed - the same shape e21, f23 and f25 already use. Upstream refuses
    # it at the nested-claim/outer mismatch, and that refusal is registered.
    cells["d18-approve-extra-execution"] = with_bundle(
        baseline, extra_execution_bundle(bundle_of(baseline))
    )

    # ---- E: replay and drift ----------------------------------------------
    # e18 (stale decision currency) left the matrix at round 1: no fixture
    # distinct from the baseline can observe it, so it is an analytic limitation
    # in the preregistration rather than an empirical row.
    bundle = bundle_of(baseline)
    bundle["work_order"] = rebound_work_order(bundle["work_order"])
    cells["e19-decision-rebound"] = with_bundle(baseline, bundle)

    # e20: the authorization-time point is coherent (objective, retained
    # artifacts and retained commitment are all X); only the executing request's
    # marker names a different valid commitment Z, and the chain is re-signed
    # around it. The objective comparison therefore passes and the divergence
    # surfaces where the second binding point actually looks.
    flow(
        "e20-execution-point-divergence",
        base,
        base_commitment,
        binding_digest=commitment_digest(alt_commitment),
    )

    # E21 as registered (an executing call whose occurred_at is after its grant's
    # expires_at) is not constructible through the live path: OWP requires every
    # delegated grant to expire exactly at the work order deadline and refuses to
    # publish a receipt whose occurred_at exceeds that deadline. The closest
    # constructible form moves the executing grant's window instead, validly
    # re-signed by its issuer, so the executed call falls outside it. Recorded.
    bundle = bundle_of(baseline)
    bundle["effective_grants"] = [
        rewindowed_grant(grant) if grant["subject_agent_id"] == "developer" else grant
        for grant in bundle["effective_grants"]
    ]
    cells["e21-outside-window"] = with_bundle(baseline, bundle)

    flow(
        "e22-workorder-rollback",
        base,
        base_commitment,
        work_order_updates={
            "quota_ceiling": {"tool_calls": 200, "repair_rounds": 2},
            "acceptance_criteria": "The fixed verifier exits with status zero.",
        },
    )

    flow(
        "e23-executable-digest-forged",
        base,
        commitment_for(
            base,
            executable_digest,
            overrides={
                "executableDigest": "sha256:"
                + hashlib.sha256(b"study-014/wrong-executable").hexdigest(),
                "evaluatorRelease": "0.15.0",
            },
        ),
    )

    # ---- F: the causal chain ----------------------------------------------
    # F23 and F25 as registered (a validly published chain whose executing receipt
    # names the wrong parent set) are not constructible through the live path:
    # publication replays causality and demands the exact protocol parent set.
    # Both are therefore built by re-signing the executing receipt alone with the
    # Sidecar key, which leaves that receipt validly signed and the chain's
    # downstream adjacency stale. Recorded.
    bundle = bundle_of(baseline)
    verifier_issuance = grant_issuance_for(bundle, "verifier")
    developer_issuance = grant_issuance_for(bundle, "developer")
    replace_receipt(
        bundle,
        ACTION_TOOL,
        lambda raw: raw.__setitem__(
            "parent_receipt_ids",
            ordered_parents(
                bundle,
                [
                    verifier_issuance["receipt_id"],
                    raw["parent_receipt_ids"][-1],
                ],
            ),
        ),
    )
    cells["f23-wrong-parent-decision"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    removed = [
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") != "owp.repo_read"
    ]
    if len(removed) == len(bundle["receipts"]):
        raise BuildError("no mid-chain receipt to remove")
    bundle["receipts"] = removed
    cells["f24-parent-receipt-removed"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    verifier_issuance = grant_issuance_for(bundle, "verifier")
    replace_receipt(
        bundle,
        ACTION_TOOL,
        lambda raw: raw.__setitem__(
            "parent_receipt_ids",
            ordered_parents(
                bundle,
                list(raw["parent_receipt_ids"]) + [verifier_issuance["receipt_id"]],
            ),
        ),
    )
    cells["f25-extra-parent-inserted"] = with_bundle(baseline, bundle)

    second = flow_cell(
        work_root,
        alt,
        alt_commitment,
        salt="second-execution",
        owp_source=owp_source,
    )
    second_bundle = bundle_of(second)

    bundle = bundle_of(baseline)
    foreign = next(
        receipt
        for receipt in second_bundle["receipts"]
        if receipt.get("tool_name") == "owp.repo_read"
    )
    bundle["receipts"] = [
        foreign if receipt.get("tool_name") == "owp.repo_read" else receipt
        for receipt in bundle["receipts"]
    ]
    cells["f26-cross-execution-receipt"] = with_bundle(baseline, bundle)

    bundle = bundle_of(baseline)
    foreign_evidence = evidence_entry(second_bundle, "evidence/patch-input/01.diff")
    entry = evidence_entry(bundle, "evidence/patch-input/01.diff")
    entry["payload_b64"] = foreign_evidence["payload_b64"]
    entry["payload_sha256"] = foreign_evidence["payload_sha256"]
    cells["f27-cross-execution-evidence"] = with_bundle(baseline, bundle)

    # ---- M: the disclosed demonstration -----------------------------------
    unsigned = flow_cell(
        work_root,
        base,
        base_commitment,
        salt="m28-unsigned-metadata-carriage",
        objective=GENERIC_OBJECTIVE,
        bind=False,
        owp_source=owp_source,
    )
    bundle = bundle_of(unsigned)
    bundle["metadata"]["judgment_commitment"] = base_commitment
    cells["m28-unsigned-metadata-carriage"] = with_bundle(unsigned, bundle)

    return cells


def grant_issuance_for(bundle, subject_agent_id):
    """The grant-issued receipt that issued the named subject's grant."""
    grant_ids = {
        grant["grant_id"]
        for grant in bundle["effective_grants"]
        if grant["subject_agent_id"] == subject_agent_id
    }
    for receipt in bundle["receipts"]:
        if receipt.get("issued_grant_id") in grant_ids:
            return receipt
    raise BuildError("bundle carries no issuance for " + subject_agent_id)


def ordered_parents(bundle, receipt_ids):
    """Parent ids in protocol order: by the parents' own receipt sequence."""
    sequence = {receipt["receipt_id"]: receipt["sequence"] for receipt in bundle["receipts"]}
    return sorted(set(receipt_ids), key=lambda item: sequence[item])


def replace_receipt(bundle, tool_name, mutate):
    """Mutate one receipt in place and re-sign it with the Sidecar key."""
    from openworkproof.signing import sign_payload

    keys = owpflow.role_keys()
    for index, receipt in enumerate(bundle["receipts"]):
        if receipt.get("tool_name") == tool_name:
            raw = copy.deepcopy(receipt)
            mutate(raw)
            bundle["receipts"][index] = sign_payload(
                "action-receipt", raw, keys["Sidecar"][0]
            )
            return bundle["receipts"][index]
    raise BuildError("bundle carries no receipt for " + tool_name)


def extra_execution_bundle(bundle):
    """Clone the executing receipt into a second, unbound action-class receipt.

    The insert is the same execution again — same patch bytes, same committed
    evidence, same arguments digest, the same nested `AgentRequest` — under a
    fresh receipt id, nonce and sequence, chained to the real executing receipt,
    with `context_source_digest` overwritten to an unbound value in *both* the
    nested claim and the correlation factors, and the **outer envelope alone**
    re-signed with the Sidecar key.

    What that leaves behind is the cell's true mechanism, and the registry says
    so: the Developer's signature over the nested request is stale and
    `nested_claim_digest` still names the original request, so upstream refuses
    at model integrity ("outer Agent receipt does not match nested claim")
    before it reaches any signature, causality or single-active-patch check. The
    OWP-layer refusal is registered rather than engineered away; the binding
    layer's surplus arm — two action-class receipts under one commitment — is
    what the cell is registered for. A live second round is refused by upstream
    three ways over, and the deferred retry route dead-ends too (see
    `harness/owpflow.py` and the retry-episode probe in `harness/tests/`).
    """
    from openworkproof.models import ACTION_RECEIPT_ADAPTER
    from openworkproof.signing import sign_payload

    keys = owpflow.role_keys()
    original = executing_receipt(bundle)
    index = bundle["receipts"].index(original)
    parsed = ACTION_RECEIPT_ADAPTER.validate_python(original)

    raw = copy.deepcopy(original)
    raw["receipt_id"] = hashlib.sha256(
        b"study-014/d18/extra-execution/" + original["receipt_id"].encode("ascii")
    ).hexdigest()
    raw["nonce"] = hashlib.sha256(
        b"study-014/d18/extra-nonce/" + original["nonce"].encode("ascii")
    ).hexdigest()
    raw["sequence"] = original["sequence"] + 1
    raw["previous_receipt_digest"] = parsed.digest
    raw["parent_receipt_ids"] = [original["receipt_id"]]
    raw["nested_claim"] = copy.deepcopy(original["nested_claim"])
    raw["nested_claim"]["context_source_digest"] = "b" * 64
    raw["correlation_factors"] = copy.deepcopy(original["correlation_factors"])
    raw["correlation_factors"]["context_source_digest"] = "b" * 64
    signed = sign_payload("action-receipt", raw, keys["Sidecar"][0])
    bundle["receipts"] = (
        bundle["receipts"][: index + 1] + [signed] + bundle["receipts"][index + 1 :]
    )
    return bundle


def rewindowed_grant(document):
    """The executing grant, validly re-signed with a window the call falls outside."""
    from openworkproof.signing import sign_payload

    keys = owpflow.role_keys()
    raw = copy.deepcopy(document)
    raw["valid_from"] = "2026-01-01T00:00:30Z"
    return sign_payload("capability-grant", raw, keys["Manager"][0])


def rebound_work_order(document):
    """A different, validly signed work order: generic objective, later deadline."""
    from openworkproof.signing import sign_payload

    keys = owpflow.role_keys()
    raw = copy.deepcopy(document)
    raw["objective"] = GENERIC_OBJECTIVE
    raw["deadline"] = "2026-01-03T00:00:00Z"
    raw["retention_until"] = "2026-01-03T01:00:00Z"
    # The model binds the root grant template's expiry to the deadline; a rebound
    # work order has to stay a valid work order for the receipts' own
    # work_order_digest binding to be the operative catch.
    raw["root_grant_template"]["expires_at"] = raw["deadline"]
    return sign_payload("work-order", raw, keys["Maintainer"][0])


def cell_directory(out_root, cell_id):
    if cell_id == "pos-baseline":
        return Path(out_root) / "baseline"
    return Path(out_root) / "mutations" / cell_id


def holdout_cell_directory(out_root, cell_id):
    return Path(out_root) / "holdout" / cell_id


# --------------------------------------------------------------------------
# the reviewer-authored holdout stratum — implemented, NEVER run pre-freeze
# --------------------------------------------------------------------------
#
# These hooks exist so that the holdout is a buildable specification rather than
# a promise, and they are gated by the same mechanical guard the scorer uses:
# `--holdout` is refused while `PINS.json`'s `preregistration.sha256` is null.
# Nothing in this repository has executed them. Each hook takes the shared build
# context and either returns a cell payload, returns a `ConstructibilityRefusal`
# carrying the verbatim upstream error (a registered construction upstream
# declines to publish is a finding under PREREGISTRATION section 1a), or raises
# `BuildError` when a harness precondition is not met (which is a validity
# problem, never a finding). Whichever it is, `build_holdout_records` persists a
# `CONSTRUCTION.json` beside the cell, so absence never has to be interpreted.
#
# Two of the hooks are *artifact* constructions — `h01` and `h06` register "copy
# the baseline byte-for-byte and change exactly one retained document". They read
# the frozen cell bytes off disk and never re-run a flow: a rebuild under a new
# salt would change every signed nonce and every entropy draw, which is not the
# cell the reviewer authored.

HOLDOUT_IDS = (
    "h01-retained-commitment-noncanonical",
    "h02-objective-lone-surrogate",
    "h03-duplicate-supported-extension",
    "h04-implicit-empty-evidence-replay",
    "h05-evaluator-spec-version-only",
    "h06-cross-execution-evaluation-artifact",
    "h07-self-consistent-wrong-action",
    "h08-semantic-facts-remint-control",
)

# h02's objective is JSON but not I-JSON: the six ASCII bytes `\uD800` inside a
# string. Python's own UTF-8 encoder refuses the decoded value, so the WorkOrder
# may not be signable at all — which is the exact case the try/report shape below
# exists for.
LONE_SURROGATE_ESCAPE = "\\uD800"


class ConstructibilityRefusal:
    """A registered holdout construction **upstream** refused to produce.

    Carried out of the builder as a value, not an exception: the preregistration
    records such a refusal as a constructibility finding attached to the cell.

    Round 3 narrowed what may become one. A refusal is only a finding when the
    builder genuinely attempted the registered construction and captured the
    upstream error it hit, so `upstream_error` is **required** and is stored
    verbatim (`detail` is the narrative around it, and never replaces it). A
    harness precondition that is not met — an unbuilt source cell, a missing
    builder hook, an edit whose target string is gone — is not a refusal and
    raises `BuildError` instead, which is recorded as `harness-error` and is a
    validity problem rather than a finding.
    """

    def __init__(self, cell_id, detail, upstream_error, error_type=None):
        self.cell_id = cell_id
        self.detail = detail
        self.upstream_error = upstream_error
        self.error_type = error_type

    def as_record(self):
        return {
            "cell": self.cell_id,
            "finding": "constructibility-refusal",
            "detail": self.detail,
            "upstreamError": self.upstream_error,
            "upstreamErrorType": self.error_type,
        }

    def __repr__(self):  # pragma: no cover - diagnostic only
        return "ConstructibilityRefusal(%r, %r, %r)" % (
            self.cell_id,
            self.detail,
            self.upstream_error,
        )


# --------------------------------------------------------------------------
# per-cell construction records
# --------------------------------------------------------------------------
#
# Round 3's finding: the round-2 builder *printed* refusal details and the
# scorer treated every absent holdout fixture — never built, deleted, aborted —
# as a constructibility finding. Absence alone proves nothing. Each holdout cell
# now gets a persisted `CONSTRUCTION.json` beside it, written atomically, and the
# scorer adjudicates from that record rather than from the shape of the tree.

CONSTRUCTION_RECORD_NAME = "CONSTRUCTION.json"
CONSTRUCTION_STATUSES = ("built", "refused", "harness-error")

# The builder's own sources. `builderVersionDigest` in every record says which
# builder produced it, so a record cannot be silently carried across a builder
# change.
BUILDER_SOURCES = (
    "harness/build_fixtures.py",
    "harness/owpflow.py",
    "adapter/commitment.py",
    "adapter/verify.py",
)


def builder_version_digest():
    """SHA-256 over the builder's own source files: `path \\0 bytes \\0`, sorted."""
    digest = hashlib.sha256()
    for relative in sorted(BUILDER_SOURCES):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((STUDY / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def construction_record(cell_id, status, *, upstream=None, harness_error=None,
                        detail=None, builder_digest=None):
    """One cell's construction outcome, in the shape the scorer adjudicates."""
    if status not in CONSTRUCTION_STATUSES:
        raise BuildError("unknown construction status: %r" % (status,))
    record = {
        "cell": cell_id,
        "status": status,
        "builderVersionDigest": builder_digest or builder_version_digest(),
    }
    if detail is not None:
        record["detail"] = detail
    if status == "refused":
        # Verbatim, not paraphrased: this string is the evidence that upstream —
        # not the harness — declined the registered construction.
        record["upstreamError"] = upstream.upstream_error
        record["upstreamErrorType"] = upstream.error_type
        record["detail"] = upstream.detail
    if status == "harness-error":
        record["harnessError"] = harness_error
    return record


def harness_error_text(error):
    return "%s: %s" % (type(error).__name__, error)


def write_construction_record(directory, record):
    """Persist one cell's construction record atomically."""
    atomic_write_bytes(
        Path(directory) / CONSTRUCTION_RECORD_NAME,
        (json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )


def _holdout_context(jpack_bin, work_root, owp_source):
    """Everything the hooks share: the pinned decisions and the baseline cell."""
    executable_digest = "sha256:" + verify.sha256_file(jpack_bin)
    pack_bytes = PACK_PATH.read_bytes()
    judgments = Path(tempfile.mkdtemp(prefix="study014-holdout-jps-", dir=str(work_root)))
    base = decide(jpack_bin, judgments, pack_bytes, FACTS_BASE, EVIDENCE_PRESENT)
    return {
        "jpack_bin": jpack_bin,
        "work_root": work_root,
        "owp_source": owp_source,
        "judgments": judgments,
        "pack_bytes": pack_bytes,
        "executable_digest": executable_digest,
        "base": base,
        "base_commitment": commitment_for(base, executable_digest),
    }


def frozen_cell_payload(cell_id):
    """The FROZEN bytes of an already-built cell, read back from `fixtures/`.

    Round 3's holdout-construction finding: `h01` and `h06` register an *artifact*
    edit — "copy baseline byte-for-byte, change exactly one retained document" —
    and the round-2 hooks instead rebuilt a fresh signed chain under a new salt,
    which changes every signed nonce and every entropy draw. A cell whose signed
    bytes differ from the baseline is not the cell the reviewer authored.

    So the artifact hooks start here: the committed cell's own bytes, read from
    disk, never re-derived. `write_cell` then regenerates the per-cell manifest
    and nothing else. Returns None when the source cell is not built, which the
    caller turns into a constructibility refusal rather than a crash.
    """
    directory = cell_directory(STUDY / "fixtures", cell_id)
    if not directory.is_dir():
        return None
    payload = {}
    for name in verify.CELL_FILES:
        path = directory / name
        payload[name] = path.read_bytes() if path.is_file() else None
    if payload.get("bundle.json") is None:
        return None
    return payload


def holdout_h01(context):
    """h01 — one 0x0a appended to the retained commitment document only.

    Baseline bytes copied verbatim; `commitment.json` is the only file that
    differs, by exactly one trailing newline. No flow is run and no salt exists,
    so every signed byte in `bundle.json` is the baseline's.
    """
    payload = frozen_cell_payload("pos-baseline")
    if payload is None:
        raise BuildError(
            "the baseline cell is not built, so there are no baseline bytes to "
            "copy byte-for-byte"
        )
    if payload.get("commitment.json") is None:
        raise BuildError("the baseline cell retains no commitment document to append to")
    return dict(payload, **{"commitment.json": payload["commitment.json"] + b"\n"})


def holdout_h02(context):
    """h02 — a signed objective whose decoded string carries a lone surrogate.

    The objective is the baseline commitment text with `expense-approval`
    replaced by `expense-\\uD800approval` in its escaped form, so the signed
    bytes are ASCII JSON that no I-JSON consumer may accept. Upstream may refuse
    to sign or even to model-validate it; that refusal is reported, not raised.
    """
    canonical = commitment_bytes(context["base_commitment"]).decode("utf-8")
    objective = canonical.replace(
        "expense-approval", "expense-" + LONE_SURROGATE_ESCAPE + "approval"
    )
    if objective == canonical:
        raise BuildError(
            "the baseline commitment text no longer carries the substring the "
            "registered construction edits"
        )
    try:
        payload = flow_cell(
            context["work_root"],
            context["base"],
            context["base_commitment"],
            salt="h02",
            objective=objective,
            binding_digest=commitment_digest(context["base_commitment"]),
            owp_source=context["owp_source"],
        )
    except Exception as error:
        return ConstructibilityRefusal(
            "h02-objective-lone-surrogate",
            "OpenWorkProof refused to publish a work order whose objective is "
            "not I-JSON",
            str(error),
            type(error).__name__,
        )
    return payload


def holdout_h03(context):
    """h03 — a full rebuild whose commitment repeats one supported extension."""
    duplicate = [
        "https://example.com/ext/unused",
        "https://example.com/ext/unused",
    ]
    candidate = commitment_for(
        context["base"],
        context["executable_digest"],
        overrides={"supportedExtensions": duplicate},
    )
    try:
        return flow_cell(
            context["work_root"],
            context["base"],
            candidate,
            salt="h03",
            owp_source=context["owp_source"],
        )
    except Exception as error:
        return ConstructibilityRefusal(
            "h03-duplicate-supported-extension",
            "the chain could not be rebuilt around a duplicate supported extension",
            str(error),
            type(error).__name__,
        )


def holdout_h04(context):
    """h04 — Core's implicit-empty evidence case: no evidence document at all."""
    decision = dict(context["base"], evidence=None)
    candidate = commitment_for(decision, context["executable_digest"])
    payload = flow_cell(
        context["work_root"],
        decision,
        candidate,
        salt="h04",
        owp_source=context["owp_source"],
    )
    return dict(payload, **{"evidence.json": None})


def holdout_h05(context):
    """h05 — evaluatorSpecVersion alone forged; every other field honest."""
    candidate = commitment_for(
        context["base"],
        context["executable_digest"],
        overrides={"evaluatorSpecVersion": "0.9.9-draft"},
    )
    return flow_cell(
        context["work_root"],
        context["base"],
        candidate,
        salt="h05",
        owp_source=context["owp_source"],
    )


def holdout_h06(context):
    """h06 — the retained evaluator envelope swapped in from `c10`.

    Same discipline as `h01`: the baseline cell's frozen bytes copied verbatim,
    with `evaluation.json` replaced by `c10-reject-executed`'s frozen envelope
    bytes and nothing else touched. No flow, no salt, no re-signing.
    """
    payload = frozen_cell_payload("pos-baseline")
    if payload is None:
        raise BuildError(
            "the baseline cell is not built, so there are no baseline bytes to "
            "copy byte-for-byte"
        )
    foreign = cell_directory(STUDY / "fixtures", "c10-reject-executed") / "evaluation.json"
    if not foreign.is_file():
        raise BuildError(
            "the registered source cell c10-reject-executed is not built, so its "
            "evaluator envelope cannot be swapped in"
        )
    return dict(payload, **{"evaluation.json": foreign.read_bytes()})


def holdout_h07(context):
    """h07 — a self-consistent execution of a target the map does not authorize.

    The commitment's `argumentsDigest` is recomputed from the alternate target's
    own arguments, so receipt and commitment agree and the failure has to land
    on the section 4 map rather than on `action-arguments-mismatch`.
    """
    target = ["decision-actions/disburse-other.json"]
    facts = json.loads(context["base"]["facts"].decode("utf-8"))
    arguments = action_arguments(facts, target_paths=target)
    candidate = commitment_for(
        context["base"],
        context["executable_digest"],
        action={
            "toolName": ACTION_TOOL,
            "argumentsDigest": action_arguments_digest(arguments),
        },
    )
    try:
        return flow_cell(
            context["work_root"],
            context["base"],
            candidate,
            salt="h07",
            target_paths=target,
            owp_source=context["owp_source"],
        )
    except Exception as error:
        return ConstructibilityRefusal(
            "h07-self-consistent-wrong-action",
            "the alternate action target could not be executed through the "
            "upstream patch executor",
            str(error),
            type(error).__name__,
        )


def holdout_h08(context):
    """h08 — the holdout's own control: a whitespace remint, coherently rebound."""
    facts = FACTS_BASE + b"\n"
    decision = decide(
        context["jpack_bin"],
        context["judgments"],
        context["pack_bytes"],
        facts,
        EVIDENCE_PRESENT,
    )
    candidate = commitment_for(decision, context["executable_digest"])
    return flow_cell(
        context["work_root"],
        decision,
        candidate,
        salt="h08",
        owp_source=context["owp_source"],
    )


HOLDOUT_BUILDERS = {
    "h01-retained-commitment-noncanonical": holdout_h01,
    "h02-objective-lone-surrogate": holdout_h02,
    "h03-duplicate-supported-extension": holdout_h03,
    "h04-implicit-empty-evidence-replay": holdout_h04,
    "h05-evaluator-spec-version-only": holdout_h05,
    "h06-cross-execution-evaluation-artifact": holdout_h06,
    "h07-self-consistent-wrong-action": holdout_h07,
    "h08-semantic-facts-remint-control": holdout_h08,
}


def build_holdout_payloads(jpack_bin, work_root, owp_source, cell_ids=None):
    """Every holdout cell's payload or constructibility refusal, keyed by id.

    Never called before the freeze: `main()` refuses `--holdout` while
    `PINS.json` carries a null preregistration digest.
    """
    context = _holdout_context(jpack_bin, work_root, owp_source)
    payloads = {}
    for cell_id in cell_ids or HOLDOUT_IDS:
        builder = HOLDOUT_BUILDERS.get(cell_id)
        if builder is None:
            raise BuildError("no holdout builder is registered for %s" % cell_id)
        payloads[cell_id] = builder(context)
    return payloads


def build_holdout_records(jpack_bin, work_root, owp_source, cell_ids=None):
    """Drive every holdout hook and return `(payloads, records)`.

    One record per requested cell, always — `built`, `refused` (upstream said
    no, verbatim) or `harness-error` (this builder failed, which is a validity
    problem and never a constructibility finding). A crash in one hook does not
    stop the others, and a crash building the shared context marks every cell,
    because in that case nothing was genuinely attempted.
    """
    cell_ids = list(cell_ids or HOLDOUT_IDS)
    digest = builder_version_digest()
    payloads = {}
    records = {}
    try:
        context = _holdout_context(jpack_bin, work_root, owp_source)
    except BaseException as error:  # noqa: BLE001 - recorded, then reported
        for cell_id in cell_ids:
            records[cell_id] = construction_record(
                cell_id,
                "harness-error",
                harness_error=harness_error_text(error),
                detail="the shared holdout build context could not be prepared, "
                "so this construction was never attempted",
                builder_digest=digest,
            )
        return payloads, records

    for cell_id in cell_ids:
        builder = HOLDOUT_BUILDERS.get(cell_id)
        if builder is None:
            records[cell_id] = construction_record(
                cell_id,
                "harness-error",
                harness_error="no holdout builder is registered for this cell",
                builder_digest=digest,
            )
            continue
        try:
            outcome = builder(context)
        except BaseException as error:  # noqa: BLE001 - recorded, then reported
            # An *uncaught* exception is this harness failing, not upstream
            # refusing: only a hook that wrapped a known upstream call and kept
            # its message may return a refusal.
            records[cell_id] = construction_record(
                cell_id,
                "harness-error",
                harness_error=harness_error_text(error),
                builder_digest=digest,
            )
            continue
        if isinstance(outcome, ConstructibilityRefusal):
            records[cell_id] = construction_record(
                cell_id, "refused", upstream=outcome, builder_digest=digest
            )
            continue
        payloads[cell_id] = outcome
        records[cell_id] = construction_record(
            cell_id, "built", builder_digest=digest
        )
    return payloads, records


def publish_holdout(out_root, cell_ids, payloads, records):
    """Write every holdout cell directory and its construction record.

    A cell that was not built still gets its directory and its
    `CONSTRUCTION.json`: the scorer must be able to tell a captured upstream
    refusal from an unexplained absence, and it cannot do that from the shape of
    the tree.
    """
    for cell_id in cell_ids:
        directory = holdout_cell_directory(out_root, cell_id)
        if cell_id in payloads:
            write_cell(directory, payloads[cell_id])
        else:
            # No artifacts, and no stale ones left behind from an earlier run.
            if directory.is_dir():
                shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)
        write_construction_record(directory, records[cell_id])
    return records


def holdout_refusal(pins):
    """The mechanical pre-freeze guard on `--holdout`, or None once frozen."""
    if (pins.get("preregistration") or {}).get("sha256") is None:
        return (
            "--holdout is refused: harness/PINS.json carries a null "
            "preregistration digest, so the preregistration is still DRAFT and "
            "the reviewer-authored holdout stratum may not be built"
        )
    return None


def construct_holdout(jpack_bin, out_root, owp_source, cell_ids):
    """Build and publish the holdout stratum; return the per-cell records.

    The one entry point the scorer's post-freeze path calls, so construction and
    adjudication run under the same attempt machinery rather than in two
    disconnected commands.
    """
    work_root = Path(tempfile.mkdtemp(prefix="study014-holdout-"))
    try:
        payloads, records = build_holdout_records(
            jpack_bin, work_root, owp_source, cell_ids
        )
    finally:
        shutil.rmtree(work_root, ignore_errors=True)
    publish_holdout(out_root, cell_ids, payloads, records)
    return records


def build_holdout(jpack_bin, out_root, force, owp_source):
    """Write the holdout cells, persisting every construction outcome."""
    registry = json.loads(
        (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
    )
    registered = [cell["id"] for cell in registry["cells"]]
    existing = [
        cell_id
        for cell_id in registered
        if holdout_cell_directory(out_root, cell_id).is_dir()
    ]
    if existing and not force:
        raise SystemExit(
            "holdout fixtures already exist under %s; pass --force to rebuild"
            % (Path(out_root) / "holdout")
        )
    records = construct_holdout(jpack_bin, out_root, owp_source, registered)
    built = [item for item in records.values() if item["status"] == "built"]
    print(
        "built %d of %d holdout cells under %s (a CONSTRUCTION.json is written for "
        "every cell, built or not)" % (len(built), len(registered), out_root)
    )
    for cell_id in registered:
        record = records[cell_id]
        if record["status"] == "refused":
            print(
                "  constructibility refusal %s: %s [upstream: %s]"
                % (cell_id, record["detail"], record["upstreamError"])
            )
        elif record["status"] == "harness-error":
            print("  HARNESS ERROR %s: %s" % (cell_id, record["harnessError"]))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(STUDY / "fixtures"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--holdout",
        action="store_true",
        help="build harness/MATRIX-HOLDOUT.json's cells (refused before the freeze)",
    )
    arguments = parser.parse_args(argv)

    jpack_bin = os.environ.get("JPACK_BIN")
    if not jpack_bin or not Path(jpack_bin).is_file():
        raise SystemExit("JPACK_BIN must point at the pinned evaluator")
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    if verify.sha256_file(jpack_bin) != pins["jpack"]["binarySha256"]:
        raise SystemExit("JPACK_BIN does not match the pinned binary digest")

    if arguments.holdout:
        refusal = holdout_refusal(pins)
        if refusal is not None:
            raise SystemExit(refusal)
        return build_holdout(jpack_bin, Path(arguments.out), arguments.force,
                             os.environ.get("OWP_SOURCE"))

    out_root = Path(arguments.out)
    existing = sorted((out_root / "mutations").glob("*")) if out_root.is_dir() else []
    if (existing or (out_root / "baseline").is_dir()) and not arguments.force:
        raise SystemExit(
            "fixtures already exist under %s; pass --force to rebuild" % out_root
        )

    registry = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    registered = [cell["id"] for cell in registry["cells"]]

    work_root = Path(tempfile.mkdtemp(prefix="study014-build-"))
    try:
        payloads = build_payloads(jpack_bin, work_root, os.environ.get("OWP_SOURCE"))
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    missing = [cell_id for cell_id in registered if cell_id not in payloads]
    unregistered = [cell_id for cell_id in payloads if cell_id not in registered]
    if missing or unregistered:
        raise SystemExit(
            "cell set does not match the registry: missing=%s unregistered=%s"
            % (missing, unregistered)
        )

    for cell_id in registered:
        write_cell(cell_directory(out_root, cell_id), payloads[cell_id])
    print("built %d cells under %s" % (len(registered), out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
