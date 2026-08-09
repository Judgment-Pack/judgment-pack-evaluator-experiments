"""The judgment commitment — construction, digest, and the canonical action document.

Implements adapter/SPEC.md sections 1, 2 and 4. Nothing here verifies anything;
`adapter/verify.py` owns the ceremony. Two canonicalizations meet in this file and
they are the same one: RFC 8785 JCS, computed by the `rfc8785` package — the bytes
JPS Core section 8.3 defines for a disposition and the bytes OpenWorkProof signs.

The one OWP-native field (`action.argumentsDigest`) is computed by OWP's own
`request_arguments_digest`, imported from the installed package, so the commitment
carries the receipt's own bound value with no translation.

Import path: `sys.path.insert(0, <study>/adapter)`; runs under the study venv.
"""

import hashlib
import json

import rfc8785
from openworkproof.models import request_arguments_digest

COMMITMENT_VERSION = "1"
COMMITMENT_DOMAIN = "jps-openworkproof-binding/commitment/1"

# The one executable tool of the section 4 map, in OWP's closed tool vocabulary.
ACTION_TOOL = "owp.apply_patch"
# The file the canonical action document adds. Also the apply-patch target path,
# so the executed OWP argument names exactly the file the patch bytes create.
ACTION_PATH = "decision-actions/disburse.json"

JUDGMENT_FIELDS = (
    "packId",
    "packVersion",
    "packDigest",
    "specVersion",
    "evaluatorSpecVersion",
    "evaluatorRelease",
    "executableDigest",
    "factsDigest",
    "evidenceDigest",
    "supportedExtensions",
    "dispositionDigest",
)
ACTION_FIELDS = ("toolName", "argumentsDigest")
COMMITMENT_FIELDS = ("commitmentVersion", "judgment", "action")

_HEX = "0123456789abcdef"


class CommitmentSchemaError(ValueError):
    """A candidate object does not satisfy SPEC section 1."""


def jcs(value):
    """RFC 8785 canonical bytes."""
    return rfc8785.dumps(value)


def sha256_hex(payload):
    return hashlib.sha256(payload).hexdigest()


def sha256_prefixed(payload):
    """The judgment-pack runtime's digest convention: `sha256:` + hex of exact bytes."""
    return "sha256:" + sha256_hex(payload)


def _is_hex64(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _HEX for character in value)
    )


def _is_prefixed_digest(value):
    return isinstance(value, str) and value.startswith("sha256:") and _is_hex64(value[7:])


# --------------------------------------------------------------------------
# section 4 — the canonical action document and its patch bytes
# --------------------------------------------------------------------------

def action_document(facts):
    """The disbursement instruction derived from the retained facts (SPEC section 4)."""
    expense = facts["expense"]
    return {
        "action": "disburse-expense",
        "amount": expense["amount"],
        "category": expense["category"],
        "currency": "USD",
    }


def action_patch_bytes(facts, *, path=ACTION_PATH):
    """The exact patch byte template: a unified diff adding one file whose content
    is the JCS bytes of the canonical action document, with no trailing newline.

        --- /dev/null
        +++ b/<path>
        @@ -0,0 +1 @@
        +<JCS bytes>
        \\ No newline at end of file

    A deterministic function of the retained facts and nothing else.
    """
    content = jcs(action_document(facts))
    return (
        b"--- /dev/null\n"
        b"+++ b/" + path.encode("utf-8") + b"\n"
        b"@@ -0,0 +1 @@\n"
        b"+" + content + b"\n"
        b"\\ No newline at end of file\n"
    )


def action_arguments(facts, *, target_paths=None, patch=None):
    """The OWP `ApplyPatchArguments` payload for the canonical action document."""
    payload = action_patch_bytes(facts) if patch is None else patch
    return {
        "target_paths": list(target_paths) if target_paths else [ACTION_PATH],
        "patch_digest": sha256_hex(payload),
        "patch_size_bytes": len(payload),
    }


def action_arguments_digest(arguments, *, tool_name=ACTION_TOOL):
    """OWP's own agent-arguments digest, from the installed package."""
    return request_arguments_digest(tool_name, arguments)


def authorized_action(disposition, facts, *, target_paths=None, patch=None):
    """The SPEC section 4 map: the authorized action, or None for inaction.

    Total over the disposition space: only `kind=outcome` + `outcomeId=approve`
    + `handoff.state=none` authorizes the canonical action document.
    """
    handoff = disposition.get("handoff") or {}
    executable = (
        disposition.get("kind") == "outcome"
        and disposition.get("outcomeId") == "approve"
        and handoff.get("state") == "none"
    )
    if not executable:
        return None
    arguments = action_arguments(facts, target_paths=target_paths, patch=patch)
    return {
        "toolName": ACTION_TOOL,
        "argumentsDigest": action_arguments_digest(arguments),
    }


# --------------------------------------------------------------------------
# sections 1-2 — the commitment object and its digest
# --------------------------------------------------------------------------

def envelope_disposition(envelope):
    """The `disposition` member value of an evaluator envelope (parsed JSON)."""
    if not isinstance(envelope, dict) or "disposition" not in envelope:
        raise CommitmentSchemaError("evaluator envelope carries no disposition")
    return envelope["disposition"]


def disposition_canonical_bytes(envelope):
    """The section 8.3 canonical disposition bytes of an evaluator envelope.

    The evaluator emits its compact `--format json` envelope with the disposition
    already canonical; re-serializing the parsed member with JCS reproduces those
    bytes exactly for the section 8.3 value space (objects, arrays, strings).
    """
    return jcs(envelope_disposition(envelope))


def disposition_digest(envelope):
    return sha256_prefixed(disposition_canonical_bytes(envelope))


def build_commitment(
    *,
    pack_bytes,
    facts_bytes,
    evidence_bytes,
    envelope,
    executable_digest,
    supported_extensions=(),
    action=None,
    pack_document=None,
):
    """Build the SPEC section 1 commitment from retained bytes and the envelope.

    `evidence_bytes` is None when no evidence-availability document was supplied
    (Core section 8.2's implicit-empty case); `evidenceDigest` is then null.
    `action` is the SPEC section 4 action object or None (commitment to inaction).
    """
    pack = json.loads(pack_bytes.decode("utf-8")) if pack_document is None else pack_document
    return {
        "commitmentVersion": COMMITMENT_VERSION,
        "judgment": {
            "packId": pack["id"],
            "packVersion": pack["version"],
            "packDigest": sha256_prefixed(pack_bytes),
            "specVersion": pack["specVersion"],
            "evaluatorSpecVersion": envelope["evaluatorSpecVersion"],
            "evaluatorRelease": envelope["tool"]["version"],
            "executableDigest": executable_digest,
            "factsDigest": sha256_prefixed(facts_bytes),
            "evidenceDigest": (
                None if evidence_bytes is None else sha256_prefixed(evidence_bytes)
            ),
            "supportedExtensions": sorted(supported_extensions),
            "dispositionDigest": disposition_digest(envelope),
        },
        "action": None if action is None else dict(action),
    }


def commitment_bytes(commitment):
    """The compact JCS text bound into `WorkOrder.objective` (SPEC section 3)."""
    return jcs(commitment)


def commitment_digest(commitment):
    """SPEC section 2: sha256 hex over the domain-separated JCS payload."""
    return sha256_hex(jcs({"domain": COMMITMENT_DOMAIN, "payload": commitment}))


def parse_commitment(text):
    """Parse commitment JSON text; raises CommitmentSchemaError when it is not one."""
    try:
        candidate = json.loads(text)
    except Exception as error:
        raise CommitmentSchemaError("commitment does not parse as JSON") from error
    if not isinstance(candidate, dict) or candidate.get("commitmentVersion") != COMMITMENT_VERSION:
        raise CommitmentSchemaError("object is not a version 1 commitment")
    return candidate


def validate_commitment(candidate):
    """Enforce SPEC section 1: exact field set, closed vocabularies, digest shapes.

    Unknown fields are refused at every level.
    """
    if not isinstance(candidate, dict):
        raise CommitmentSchemaError("commitment must be an object")
    if tuple(sorted(candidate)) != tuple(sorted(COMMITMENT_FIELDS)):
        raise CommitmentSchemaError("commitment field set is not section 1's")
    if candidate["commitmentVersion"] != COMMITMENT_VERSION:
        raise CommitmentSchemaError("unsupported commitmentVersion")

    judgment = candidate["judgment"]
    if not isinstance(judgment, dict):
        raise CommitmentSchemaError("judgment must be an object")
    if tuple(sorted(judgment)) != tuple(sorted(JUDGMENT_FIELDS)):
        raise CommitmentSchemaError("judgment field set is not section 1's")
    for field in ("packId", "packVersion", "specVersion", "evaluatorSpecVersion",
                  "evaluatorRelease"):
        if not isinstance(judgment[field], str) or not judgment[field]:
            raise CommitmentSchemaError("judgment." + field + " must be a non-empty string")
    for field in ("packDigest", "executableDigest", "factsDigest", "dispositionDigest"):
        if not _is_prefixed_digest(judgment[field]):
            raise CommitmentSchemaError("judgment." + field + " is not a sha256 digest")
    if judgment["evidenceDigest"] is not None and not _is_prefixed_digest(
        judgment["evidenceDigest"]
    ):
        raise CommitmentSchemaError("judgment.evidenceDigest is not a sha256 digest or null")
    extensions = judgment["supportedExtensions"]
    if not isinstance(extensions, list) or any(
        not isinstance(item, str) for item in extensions
    ):
        raise CommitmentSchemaError("judgment.supportedExtensions must be a string array")
    if list(extensions) != sorted(extensions):
        raise CommitmentSchemaError("judgment.supportedExtensions must be sorted")

    action = candidate["action"]
    if action is None:
        return candidate
    if not isinstance(action, dict):
        raise CommitmentSchemaError("action must be an object or null")
    if tuple(sorted(action)) != tuple(sorted(ACTION_FIELDS)):
        raise CommitmentSchemaError("action field set is not section 1's")
    if action["toolName"] != ACTION_TOOL:
        raise CommitmentSchemaError("action.toolName is not an executable tool literal")
    if not _is_hex64(action["argumentsDigest"]):
        raise CommitmentSchemaError("action.argumentsDigest is not bare 64-hex")
    return candidate
