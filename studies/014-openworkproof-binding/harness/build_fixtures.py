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

Run:
    JPACK_BIN=... OWP_SOURCE=... python harness/build_fixtures.py [--out DIR] [--force]
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


def write_cell(directory, payload):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in verify.CELL_FILES:
        target = directory / name
        if name in payload and payload[name] is not None:
            target.write_bytes(payload[name])
        elif target.is_file():
            target.unlink()
    (directory / verify.MANIFEST_NAME).write_text(
        verify.manifest_text(directory), encoding="utf-8"
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
    # recorded in harness/owpflow.py), so the extra unbound execution is inserted
    # post-hoc and re-signed with the Sidecar key alone - the same shape e21, f23
    # and f25 already use, and the OWP-layer refusal is registered, not hidden.
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
    """Insert a second, unbound `owp.apply_patch` receipt after the real one.

    The insert is the same execution again — same patch bytes, same committed
    evidence, same arguments digest — under a fresh receipt id and nonce, chained
    to the real executing receipt and re-signed with the Sidecar key alone, with
    its request's `context_source_digest` left unbound. That keeps the evidence
    set coherent while the chain carries two action-class receipts for one
    commitment. A live second round is refused by upstream three ways over (see
    `harness/owpflow.py`), so the OWP layer is expected to refuse this too; the
    binding layer's surplus arm is what the cell is registered for.
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(STUDY / "fixtures"))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args(argv)

    jpack_bin = os.environ.get("JPACK_BIN")
    if not jpack_bin or not Path(jpack_bin).is_file():
        raise SystemExit("JPACK_BIN must point at the pinned evaluator")
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    if verify.sha256_file(jpack_bin) != pins["jpack"]["binarySha256"]:
        raise SystemExit("JPACK_BIN does not match the pinned binary digest")

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
