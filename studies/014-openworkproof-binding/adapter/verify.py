"""The three-layer verification ceremony — adapter/SPEC.md section 5.

Ordered, fail-closed, offline. Each layer runs and records independently so the
detection matrix can attribute; the combined verdict is pass iff every layer
passes. Inputs: one cell directory (the acceptance bundle plus the retained
artifact set) and the pinned `jpack` executable. Nothing else — no network, no
ledger, no state.

  Layer OWP     `openworkproof.acceptance.verify_acceptance_bundle`, unchanged,
                called as a library function with its inputs reconstructed from
                the bundle JSON and its public keys taken from the work order's
                own key bindings. Any exception is a layer failure with the
                message recorded (the upstream demo script's discarded booleans
                are why the library function is called directly).
  Layer BINDING adapter checks over the raw bundle JSON, first failure wins.
                Parses dicts rather than models so a bundle OWP would refuse is
                still adjudicated.
  Layer REPLAY  deterministic recomputation with the pinned binary under the
                commitment's own replay tuple.

The commitment REPLAY and BINDING work from is the one at the signed
authorization-time binding point (`WorkOrder.objective`); a chain that carries no
commitment there has nothing to replay, which is why M28 and E19 report
`unavailable` rather than a disposition comparison.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from commitment import (  # noqa: E402
    CommitmentSchemaError,
    authorized_action,
    commitment_digest,
    disposition_digest,
    envelope_disposition,
    parse_commitment,
    sha256_prefixed,
    validate_commitment,
)

CELL_FILES = (
    "bundle.json",
    "commitment.json",
    "pack.json",
    "facts.json",
    "evidence.json",
    "evaluation.json",
)
MANIFEST_NAME = "MANIFEST.sha256"

BINDING_CODES = (
    "commitment-objective-missing",
    "commitment-schema-invalid",
    "binding-point-divergence",
    "executing-receipt-missing",
    "executing-receipt-ambiguous",
    "pack-artifact-missing",
    "pack-digest-mismatch",
    "facts-artifact-missing",
    "facts-digest-mismatch",
    "evidence-artifact-missing",
    "evidence-digest-mismatch",
    "disposition-digest-mismatch-retained",
    "action-tool-mismatch",
    "action-arguments-mismatch",
    "action-map-violation",
)
REPLAY_CODES = (
    "replay-executable-mismatch",
    "replay-unavailable",
    "replay-refused",
    "replay-disposition-mismatch",
)


# --------------------------------------------------------------------------
# cell plumbing
# --------------------------------------------------------------------------

def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest_text(directory):
    """`sha256  name` for every cell file present, sorted by name."""
    directory = Path(directory)
    lines = []
    for name in sorted(CELL_FILES):
        path = directory / name
        if path.is_file():
            lines.append("%s  %s" % (sha256_file(path), name))
    return "\n".join(lines) + "\n"


def manifest_problems(directory):
    """Manifest integrity: listed files present and matching, no unlisted files."""
    directory = Path(directory)
    manifest = directory / MANIFEST_NAME
    if not manifest.is_file():
        return ["manifest is absent"]
    problems = []
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        listed[name] = digest
    for name, digest in sorted(listed.items()):
        path = directory / name
        if not path.is_file():
            problems.append("listed file is absent: " + name)
        elif sha256_file(path) != digest:
            problems.append("listed file does not match its digest: " + name)
    for name in sorted(CELL_FILES):
        if (directory / name).is_file() and name not in listed:
            problems.append("present file is not listed: " + name)
    return problems


class Cell:
    """One frozen cell directory. Absent artifacts read as None, never as an error."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.name = self.directory.name

    def read(self, name):
        path = self.directory / name
        return path.read_bytes() if path.is_file() else None

    def json(self, name):
        payload = self.read(name)
        if payload is None:
            return None
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return None


def jpack_digest(jpack_bin):
    return "sha256:" + sha256_file(jpack_bin)


def jpack_release(jpack_bin):
    """The evaluator's reported release, or None when it cannot be asked."""
    try:
        completed = subprocess.run(
            [str(jpack_bin), "--version"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        return None
    parts = completed.stdout.strip().split()
    return parts[-1] if parts else None


def evaluate(jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes):
    """Run the pinned evaluator over retained bytes; return (envelope bytes, exit)."""
    work_dir = Path(work_dir)
    pack_path = work_dir / "pack.json"
    facts_path = work_dir / "facts.json"
    pack_path.write_bytes(pack_bytes)
    facts_path.write_bytes(facts_bytes)
    command = [
        str(jpack_bin),
        "experimental",
        "evaluate",
        str(pack_path),
        "--facts",
        str(facts_path),
        "--format",
        "json",
    ]
    if evidence_bytes is not None:
        evidence_path = work_dir / "evidence.json"
        evidence_path.write_bytes(evidence_bytes)
        command.extend(["--evidence", str(evidence_path)])
    completed = subprocess.run(command, capture_output=True, timeout=300)
    return completed.stdout, completed.returncode


# --------------------------------------------------------------------------
# Layer OWP
# --------------------------------------------------------------------------

def layer_owp(cell):
    bundle = cell.json("bundle.json")
    if bundle is None:
        return {"verdict": "unavailable", "detail": "bundle is unreadable"}
    try:
        import base64

        import openworkproof.acceptance as acceptance
        from openworkproof.models import (
            ACTION_RECEIPT_ADAPTER,
            AcceptanceReceipt,
            CapabilityGrant,
            CompositionReport,
            EvidenceRef,
            WorkOrder,
        )
        from openworkproof.policy import CommittedEvidence
        from openworkproof.signing import decode_and_verify_key_binding

        work_order = WorkOrder.model_validate(bundle["work_order"])
        public_keys = {
            binding.key_id: decode_and_verify_key_binding(binding)
            for binding in work_order.key_bindings
        }
        grants = tuple(
            CapabilityGrant.model_validate(item)
            for item in sorted(bundle["effective_grants"], key=lambda i: i["grant_id"])
        )
        attempts = tuple(
            CapabilityGrant.model_validate(item)
            for item in sorted(bundle["grant_attempts"], key=lambda i: i["digest"])
        )
        receipts = tuple(
            ACTION_RECEIPT_ADAPTER.validate_python(item) for item in bundle["receipts"]
        )
        reports = tuple(
            CompositionReport.model_validate(item)
            for item in bundle["composition_reports"]
        )
        acceptance_receipt = AcceptanceReceipt.model_validate(
            bundle["acceptance_receipt"]
        )
        committed = tuple(
            CommittedEvidence(
                reference=EvidenceRef.model_validate(item["reference"]),
                payload=base64.b64decode(item["payload_b64"]),
            )
            for item in bundle["committed_evidence"]
        )
        acceptance.verify_acceptance_bundle(
            work_order=work_order,
            report=reports[-1],
            effective_grants=grants,
            grant_attempts=attempts,
            receipts=receipts,
            committed_evidence=committed,
            acceptance_receipt=acceptance_receipt,
            public_keys=public_keys,
            reports=reports,
        )
    except Exception as error:
        return {
            "verdict": "fail",
            "detail": "%s: %s" % (type(error).__name__, error),
        }
    return {"verdict": "pass", "detail": None}


# --------------------------------------------------------------------------
# Layer BINDING
# --------------------------------------------------------------------------

def _fail(code, detail=None):
    return {"verdict": "fail:" + code, "detail": detail}


def commitment_at_binding_point(cell):
    """The commitment carried by `WorkOrder.objective`, or None."""
    bundle = cell.json("bundle.json")
    if not isinstance(bundle, dict):
        return None
    objective = (bundle.get("work_order") or {}).get("objective")
    if not isinstance(objective, str):
        return None
    try:
        return parse_commitment(objective)
    except CommitmentSchemaError:
        return None


def layer_binding(cell):
    bundle = cell.json("bundle.json")
    if not isinstance(bundle, dict):
        return _fail("commitment-objective-missing", "bundle is unreadable")

    objective = (bundle.get("work_order") or {}).get("objective")
    if not isinstance(objective, str):
        return _fail("commitment-objective-missing", "objective is not a string")
    try:
        candidate = parse_commitment(objective)
    except CommitmentSchemaError as error:
        return _fail("commitment-objective-missing", str(error))
    try:
        validate_commitment(candidate)
    except CommitmentSchemaError as error:
        return _fail("commitment-schema-invalid", str(error))

    digest = commitment_digest(candidate)
    retained = cell.json("commitment.json")
    if retained != candidate:
        return _fail(
            "binding-point-divergence",
            "retained commitment document is not the objective commitment",
        )

    judgment = candidate["judgment"]
    action = candidate["action"]
    matches = [
        receipt
        for receipt in bundle.get("receipts", [])
        if isinstance(receipt, dict)
        and receipt.get("event_type") == "tool_call"
        and isinstance(receipt.get("nested_claim"), dict)
        and receipt["nested_claim"].get("context_source_digest") == digest
    ]
    if action is None:
        if matches:
            return _fail(
                "action-map-violation",
                "commitment authorizes no action yet a receipt carries its digest",
            )
        executing = None
    elif not matches:
        return _fail("executing-receipt-missing", "no receipt carries the commitment digest")
    elif len(matches) > 1:
        return _fail(
            "executing-receipt-ambiguous",
            "%d receipts carry the commitment digest" % len(matches),
        )
    else:
        executing = matches[0]
        if executing.get("correlation_factors", {}).get("context_source_digest") != digest:
            return _fail(
                "binding-point-divergence",
                "receipt correlation factors do not mirror the request binding",
            )

    pack_bytes = cell.read("pack.json")
    if pack_bytes is None:
        return _fail("pack-artifact-missing", "retained pack bytes are absent")
    if sha256_prefixed(pack_bytes) != judgment["packDigest"]:
        return _fail("pack-digest-mismatch", "retained pack bytes are not the committed pack")
    pack = cell.json("pack.json")
    if not isinstance(pack, dict) or (
        pack.get("id") != judgment["packId"]
        or pack.get("version") != judgment["packVersion"]
        or pack.get("specVersion") != judgment["specVersion"]
    ):
        return _fail("pack-digest-mismatch", "retained pack identity is not the committed one")

    facts_bytes = cell.read("facts.json")
    if facts_bytes is None:
        return _fail("facts-artifact-missing", "retained facts bytes are absent")
    if sha256_prefixed(facts_bytes) != judgment["factsDigest"]:
        return _fail("facts-digest-mismatch", "retained facts bytes are not the committed facts")

    evidence_bytes = cell.read("evidence.json")
    committed_evidence_digest = judgment["evidenceDigest"]
    if committed_evidence_digest is None:
        if evidence_bytes is not None:
            return _fail(
                "evidence-digest-mismatch",
                "commitment declares no evidence document yet one is retained",
            )
    elif evidence_bytes is None:
        return _fail("evidence-artifact-missing", "retained evidence bytes are absent")
    elif sha256_prefixed(evidence_bytes) != committed_evidence_digest:
        return _fail(
            "evidence-digest-mismatch",
            "retained evidence bytes are not the committed evidence",
        )

    envelope = cell.json("evaluation.json")
    if not isinstance(envelope, dict):
        return _fail(
            "disposition-digest-mismatch-retained",
            "retained evaluator envelope is unreadable",
        )
    try:
        retained_disposition_digest = disposition_digest(envelope)
    except CommitmentSchemaError as error:
        return _fail("disposition-digest-mismatch-retained", str(error))
    if retained_disposition_digest != judgment["dispositionDigest"]:
        return _fail(
            "disposition-digest-mismatch-retained",
            "retained disposition is not the committed disposition",
        )

    if action is not None:
        if executing.get("tool_name") != action["toolName"]:
            return _fail(
                "action-tool-mismatch",
                "executed tool %r is not the committed tool" % executing.get("tool_name"),
            )
        if executing.get("arguments_digest") != action["argumentsDigest"]:
            return _fail(
                "action-arguments-mismatch",
                "executed arguments are not the committed arguments",
            )
        facts = json.loads(facts_bytes.decode("utf-8"))
        derived = authorized_action(envelope_disposition(envelope), facts)
        if derived != action:
            return _fail(
                "action-map-violation",
                "the section 4 map does not authorize the executed action",
            )
    return {"verdict": "pass", "detail": None}


# --------------------------------------------------------------------------
# Layer REPLAY
# --------------------------------------------------------------------------

def layer_replay(cell, jpack_bin, work_dir):
    candidate = commitment_at_binding_point(cell)
    if candidate is None:
        return {
            "verdict": "unavailable",
            "detail": "replay-unavailable: no commitment at the signed binding point",
        }
    try:
        validate_commitment(candidate)
    except CommitmentSchemaError as error:
        return {
            "verdict": "unavailable",
            "detail": "replay-unavailable: " + str(error),
        }
    judgment = candidate["judgment"]

    if jpack_bin is None or not Path(jpack_bin).is_file():
        return {
            "verdict": "unavailable",
            "detail": "replay-unavailable: the pinned evaluator is not available",
        }
    if jpack_digest(jpack_bin) != judgment["executableDigest"]:
        return {
            "verdict": "fail:replay-executable-mismatch",
            "detail": "executable digest is not the recorded one",
        }
    release = jpack_release(jpack_bin)
    if release != judgment["evaluatorRelease"]:
        return {
            "verdict": "fail:replay-executable-mismatch",
            "detail": "evaluator release %r is not the recorded %r"
            % (release, judgment["evaluatorRelease"]),
        }

    pack_bytes = cell.read("pack.json")
    facts_bytes = cell.read("facts.json")
    evidence_bytes = cell.read("evidence.json")
    if pack_bytes is None or facts_bytes is None:
        return {
            "verdict": "unavailable",
            "detail": "replay-unavailable: retained pack or facts bytes are absent",
        }
    if judgment["evidenceDigest"] is not None and evidence_bytes is None:
        return {
            "verdict": "unavailable",
            "detail": "replay-unavailable: retained evidence bytes are absent",
        }
    if judgment["evidenceDigest"] is None:
        evidence_bytes = None

    stdout, returncode = evaluate(
        jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes
    )
    try:
        envelope = json.loads(stdout.decode("utf-8"))
    except Exception:
        return {
            "verdict": "fail:replay-refused:unreadable",
            "detail": "the evaluator produced no readable envelope (exit %d)" % returncode,
        }
    error = envelope.get("evaluationError")
    if error is not None or "disposition" not in envelope:
        error_class = (error or {}).get("class", "unclassified")
        return {
            "verdict": "fail:replay-refused:" + str(error_class),
            "detail": "the evaluator refused the retained inputs",
        }
    if disposition_digest(envelope) != judgment["dispositionDigest"]:
        return {
            "verdict": "fail:replay-disposition-mismatch",
            "detail": "recomputed disposition is not the committed disposition",
        }
    return {"verdict": "pass", "detail": None}


# --------------------------------------------------------------------------
# the ceremony
# --------------------------------------------------------------------------

def verify_cell(cell_dir, jpack_bin, work_dir):
    """Run the three layers independently and derive the combined verdict."""
    cell = Cell(cell_dir)
    owp = layer_owp(cell)
    binding = layer_binding(cell)
    replay = layer_replay(cell, jpack_bin, work_dir)
    combined = (
        "pass"
        if owp["verdict"] == "pass"
        and binding["verdict"] == "pass"
        and replay["verdict"] == "pass"
        else "fail"
    )
    return {
        "cell": cell.name,
        "owp": owp,
        "binding": binding,
        "replay": replay,
        "combined": combined,
    }
