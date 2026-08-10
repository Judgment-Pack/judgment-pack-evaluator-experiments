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
from openworkproof.repo_tools import git_blob_oid

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


class CommitmentEncodingError(CommitmentSchemaError):
    """The bytes carry a conforming commitment in a non-canonical encoding."""


def jcs(value):
    """RFC 8785 canonical bytes."""
    return rfc8785.dumps(value)


def canonical_bytes(value):
    """JCS bytes with every canonicalization failure mapped to the schema error.

    `rfc8785.dumps` raises its own `CanonicalizationError` on input JSON that is
    not I-JSON — most importantly a string carrying an unpaired surrogate, which
    `json.loads` will happily produce from a `\\uD800` escape. Round 2 found that
    exception escaping the registered failure path, so every canonicalization on
    the parse path goes through here and lands as `commitment-schema-invalid`.
    """
    try:
        return jcs(value)
    except CommitmentSchemaError:
        raise
    except Exception as error:
        raise CommitmentEncodingError(
            "value is not canonicalizable under RFC 8785: %s: %s"
            % (type(error).__name__, error)
        ) from error


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


def action_file_bytes(facts):
    """The exact bytes of the file the action creates.

    Canonical OWP patch text: the JCS bytes of the action document plus the one
    terminating newline `repo_tools._canonical_patch_text` requires of every
    touched file.
    """
    return jcs(action_document(facts)) + b"\n"


def action_patch_bytes(facts, *, path=ACTION_PATH):
    """The exact patch byte template — OWP's canonical create-file patch.

        diff --git a/<path> b/<path>
        new file mode 100644
        index 0000000000000000000000000000000000000000..<git blob oid>
        --- /dev/null
        +++ b/<path>
        @@ -0,0 +1 @@
        +<JCS bytes of the action document>

    Every line is required by `repo_tools.parse_patch_phase_a`: the Git file
    header, the `new file mode` line, the zero-to-blob index line whose right
    object id is `git_blob_oid` of the created content, the `/dev/null` old
    header, and a hunk whose ranges are `-0,0 +1`. The created content carries
    its terminating newline (OWP refuses a touched file without one), so the
    old "\\ No newline at end of file" trailer is gone. A deterministic function
    of the retained facts and the target path, and nothing else.
    """
    content = action_file_bytes(facts)
    encoded = path.encode("utf-8")
    return (
        b"diff --git a/" + encoded + b" b/" + encoded + b"\n"
        b"new file mode 100644\n"
        b"index " + b"0" * 40 + b".." + git_blob_oid(content).encode("ascii") + b"\n"
        b"--- /dev/null\n"
        b"+++ b/" + encoded + b"\n"
        b"@@ -0,0 +1 @@\n"
        b"+" + content
    )


def action_arguments(facts, *, target_paths=None, patch=None):
    """The OWP `ApplyPatchArguments` payload for the canonical action document.

    The declared target paths and the patch's own derived paths must agree —
    `parse_patch_phase_a` refuses a patch whose sections do not equal the
    declared set — so when no explicit patch is supplied the bytes are derived
    for the declared path itself.
    """
    paths = list(target_paths) if target_paths else [ACTION_PATH]
    payload = action_patch_bytes(facts, path=paths[0]) if patch is None else patch
    return {
        "target_paths": paths,
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
    return canonical_bytes(envelope_disposition(envelope))


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
    return canonical_bytes(commitment)


def commitment_digest(commitment):
    """SPEC section 2: sha256 hex over the domain-separated JCS payload."""
    return sha256_hex(
        canonical_bytes({"domain": COMMITMENT_DOMAIN, "payload": commitment})
    )


def _no_duplicate_keys(pairs):
    """`object_pairs_hook` that refuses duplicate member names (RFC 8785 / I-JSON).

    `json.loads` silently keeps the last duplicate, so two conforming consumers
    can assign different semantics to the same signed document. Refusing here is
    what makes the cross-vendor "exact judgment" claim mean anything.
    """
    seen = set()
    for name, _ in pairs:
        if name in seen:
            raise CommitmentSchemaError("commitment object has a duplicate member: " + name)
        seen.add(name)
    return dict(pairs)


def _surrogate_problem(value):
    """The first non-I-JSON string in a parsed document, or None.

    RFC 8785 canonicalizes Unicode *scalar* values; a JSON document may still
    escape a lone surrogate (`"\\uD800"`), which `json.loads` decodes into a
    Python string no UTF-8 encoder will accept. Such a document is JSON but not
    I-JSON, it has no canonical form, and round 2 found it reaching the JCS
    encoder as an uncaught exception. It is refused at parse time instead.
    """
    if isinstance(value, str):
        for character in value:
            if 0xD800 <= ord(character) <= 0xDFFF:
                return (
                    "commitment carries an unpaired surrogate (U+%04X) and is "
                    "therefore not I-JSON" % ord(character)
                )
        return None
    if isinstance(value, dict):
        for name, item in value.items():
            problem = _surrogate_problem(name) or _surrogate_problem(item)
            if problem is not None:
                return problem
        return None
    if isinstance(value, list):
        for item in value:
            problem = _surrogate_problem(item)
            if problem is not None:
                return problem
    return None


def parse_commitment_bytes(raw):
    """Strictly parse commitment bytes: UTF-8, no duplicate keys, version 1.

    Encoding is *not* checked here — `canonical_encoding_problem` owns the
    byte-level rule, so a caller can tell a non-canonical encoding of the right
    commitment (`commitment-schema-invalid`) from a different commitment
    (`binding-point-divergence`). Strings that are not sequences of Unicode
    scalar values *are* refused here: they have no canonical encoding at all, so
    the byte-level rule has nothing to compare against.
    """
    if isinstance(raw, str):
        raise CommitmentSchemaError("commitment must be parsed from exact bytes")
    if not isinstance(raw, (bytes, bytearray)):
        raise CommitmentSchemaError("commitment must be exact bytes")
    try:
        text = bytes(raw).decode("utf-8")
    except UnicodeDecodeError as error:
        raise CommitmentSchemaError("commitment bytes are not valid UTF-8") from error
    try:
        candidate = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except CommitmentSchemaError:
        raise
    except Exception as error:
        raise CommitmentSchemaError("commitment does not parse as JSON") from error
    if (
        not isinstance(candidate, dict)
        or candidate.get("commitmentVersion") != COMMITMENT_VERSION
    ):
        raise CommitmentSchemaError("object is not a version 1 commitment")
    problem = _surrogate_problem(candidate)
    if problem is not None:
        raise CommitmentEncodingError(problem)
    return candidate


def canonical_encoding_problem(raw, candidate):
    """None when `raw` is exactly the canonical JCS bytes of `candidate`.

    A candidate that cannot be canonicalized at all raises
    `CommitmentEncodingError` (a `CommitmentSchemaError`) rather than escaping
    as an untyped canonicalizer exception.
    """
    if bytes(raw) == canonical_bytes(candidate):
        return None
    return "commitment bytes are not the canonical JCS encoding of their own content"


def parse_commitment(text):
    """Parse commitment text carried in `WorkOrder.objective` (a JSON string).

    The signed bytes are the objective's UTF-8 encoding; strictness and the
    byte-level canonical check are the caller's, in that order.
    """
    if isinstance(text, str):
        return parse_commitment_bytes(text.encode("utf-8"))
    return parse_commitment_bytes(text)


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
    if len(set(extensions)) != len(extensions):
        raise CommitmentSchemaError(
            "judgment.supportedExtensions is a set: duplicate members are invalid"
        )

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
