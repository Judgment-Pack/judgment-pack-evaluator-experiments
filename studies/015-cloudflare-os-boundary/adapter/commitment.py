"""The staged-action commitment — construction, digest, and the canonical staged call.

Implements adapter/SPEC.md sections 1, 2 and 4. Nothing here verifies anything;
`adapter/verify.py` owns the ceremony. The one canonicalization is RFC 8785 JCS, computed
by the `rfc8785` package — the bytes JPS Core section 8.3 defines for a disposition.

Unlike Study 014's counterpart there is no upstream-native digest to reuse: the platform's
action record carries prose and an opaque integer, never arguments, so the arguments digest
below is adapter-owned by necessity and the SPEC says so.

Import path: `sys.path.insert(0, <study>/adapter)`; runs under the study venv.
"""

import hashlib
import json

import rfc8785

COMMITMENT_VERSION = "1"
COMMITMENT_DOMAIN = "jps-cloudflare-os-binding/commitment/1"
ARGUMENTS_DOMAIN = "jps-cloudflare-os-binding/arguments/1"

# The one executable action of the SPEC section 4 map. Every member here is part of the
# *registered map*, not of the store: the verifier re-derives them from the retained
# judgment alone and compares, so a bridge that commits a different target, tool, or
# arguments is caught even when every downstream record agrees with its own commitment
# (`action-derivation-mismatch`).
GATEKEEPER_ID = 1
# The registered deployment is the pinned **MCP Portal** connector with
# `MCP_PORTAL_TRUST_ANNOTATIONS=true`. Round 2 established that the earlier scenario was
# not producible by any pinned connector: the generic MCP connector hardwires
# `trust = "byo"` (gatekeeper-mcp/src/mcp.ts:77) so no write on it can ever be
# auto-approvable, and the portal is the only connector that can be `vetted`
# (gatekeeper-mcp-portal/src/config.ts:34-36). Every identifier below is therefore the
# shape that connector actually emits, not a scenario-local placeholder.
PORTAL_ENDPOINT = "https://tracker.example/mcp"
UPSTREAM_SERVER_ID = "tracker"
RESOURCE_URL = "%s#server=%s" % (PORTAL_ENDPOINT, UPSTREAM_SERVER_ID)
SERVER_TRUST = "vetted"
# The portal's wire tool names are `<upstream server id>_<tool>`.
ACTION_TOOL = "tracker_create_work_item"
SECOND_TOOL = "tracker_close_work_item"

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
    "evidenceBacking",
)
ACTION_FIELDS = (
    "gatekeeperId",
    "resourceUrl",
    "serverTrust",
    "toolName",
    "actionKindTag",
    "argumentsDigest",
    "boundResourceRevision",
)
COMMITMENT_FIELDS = ("commitmentVersion", "judgment", "action")
BACKING_KINDS = ("artifact",)

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
# section 4 — the canonical staged call
# --------------------------------------------------------------------------

def action_arguments(facts):
    """The `create_work_item` arguments — a deterministic function of the retained facts."""
    request = facts["request"]
    return {
        "kind": "provision-intake",
        "requestType": request["type"],
        "source": "jps-triage",
    }


def arguments_digest(arguments, *, tool_name=ACTION_TOOL):
    """SPEC section 1's adapter-owned arguments digest (domain-separated JCS)."""
    return sha256_hex(
        jcs({"domain": ARGUMENTS_DOMAIN, "toolName": tool_name, "arguments": arguments})
    )


def executable(disposition):
    """The SPEC section 4 rule: only outcome/proceed with handoff none executes."""
    handoff = disposition.get("handoff") or {}
    return (
        disposition.get("kind") == "outcome"
        and disposition.get("outcomeId") == "proceed"
        and handoff.get("state") == "none"
    )


# `encodeURIComponent`'s unreserved set (RFC 2396 mark characters plus alphanumerics) —
# the platform's `actionKindFor` builds its tag with that exact escaping, so the adapter
# reproduces the rule rather than trusting a value the store hands it. A probe against
# the pinned `actionKindFor` asserts this function agrees with upstream
# (`probes/upstream-probes.ts`); a divergence is an apparatus failure, not a detection.
_URI_UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.!~*'()"
)


def encode_uri_component(value):
    encoded = []
    for byte in value.encode("utf-8"):
        character = chr(byte)
        if character in _URI_UNRESERVED:
            encoded.append(character)
        else:
            encoded.append("%%%02X" % byte)
    return "".join(encoded)


def endpoint_of_resource_url(resource_url):
    """`scope.ts:endpointOfResourceUrl` — the endpoint with its fragment stripped."""
    return resource_url.split("#", 1)[0]


def endpoint_tag(resource_url=RESOURCE_URL):
    """`scope.ts:endpointTag` — the encoded whole-endpoint identity."""
    return encode_uri_component(endpoint_of_resource_url(resource_url))


def action_scope_tag(resource_url=RESOURCE_URL, server_id=UPSTREAM_SERVER_ID):
    """The portal connector's own scope tag (`portal.ts:541-543`)."""
    return "mcp-portal:%s:portal-%s" % (endpoint_tag(resource_url), server_id)


def action_kind_tag(scope_tag=None, tool_name=ACTION_TOOL):
    """The platform's own action-kind tag rule, reproduced (tools.ts `actionKindFor`).

    Note the double encoding this produces in practice: the scope tag already contains a
    percent-encoded endpoint, and `actionKindFor` encodes the whole scope tag again. The
    resulting tag is ugly and exactly what the connector emits; a probe asserts the
    reproduction against upstream.
    """
    if scope_tag is None:
        scope_tag = action_scope_tag()
    return "%s:%s" % (encode_uri_component(scope_tag), encode_uri_component(tool_name))


# The members of the action object the SPEC section 4 map *determines* — re-derivable by
# the verifier from the retained judgment and the registered map, with no reference to
# any record the bridge or the store wrote.
#
# Round 2 found `serverTrust` was wrongly listed as contextual: the registered scenario
# fixes the trust tier, so treating it as store-supplied let a coherent rewrite move it.
# `simulationBasis` is gone from the schema entirely — the registered connector cannot
# produce a non-empty basis, so a field that could only ever be empty was carrying no
# information and its verdict code could not fire (PREREGISTRATION section 4c).
DERIVED_ACTION_FIELDS = (
    "gatekeeperId",
    "resourceUrl",
    "serverTrust",
    "toolName",
    "actionKindTag",
    "argumentsDigest",
)
# The one member that is genuinely contextual: the revision the resource stood at when
# the action was staged. No map determines it; it is checked against the retained store
# (`stage-revision-mismatch`, `revision-drift`).
CONTEXTUAL_ACTION_FIELDS = ("boundResourceRevision",)


def derived_action(disposition, facts):
    """The SPEC section 4 map applied to a judgment: the determined action, or None.

    Returns only `DERIVED_ACTION_FIELDS`. This is the verifier's independent oracle for
    *which* action the judgment authorized; `authorized_action` below is the builder's
    full object, which adds the contextual member.
    """
    if not executable(disposition):
        return None
    return {
        "gatekeeperId": GATEKEEPER_ID,
        "resourceUrl": RESOURCE_URL,
        "serverTrust": SERVER_TRUST,
        "toolName": ACTION_TOOL,
        "actionKindTag": action_kind_tag(),
        "argumentsDigest": arguments_digest(action_arguments(facts)),
    }


def authorized_action(disposition, facts, *, bound_resource_revision,
                      action_kind_tag_override=None):
    """The full authorized action object, or None for a commitment to inaction."""
    derived = derived_action(disposition, facts)
    if derived is None:
        return None
    action = dict(derived)
    if action_kind_tag_override is not None:
        action["actionKindTag"] = action_kind_tag_override
    action["serverTrust"] = SERVER_TRUST
    action["boundResourceRevision"] = bound_resource_revision
    return action


# --------------------------------------------------------------------------
# sections 1-2 — the commitment object and its digest
# --------------------------------------------------------------------------

def envelope_disposition(envelope):
    """The `disposition` member value of an evaluator envelope (parsed JSON)."""
    if not isinstance(envelope, dict) or "disposition" not in envelope:
        raise CommitmentSchemaError("evaluator envelope carries no disposition")
    return envelope["disposition"]


def disposition_canonical_bytes(envelope):
    """The section 8.3 canonical disposition bytes of an evaluator envelope."""
    return jcs(envelope_disposition(envelope))


def disposition_digest(envelope):
    return sha256_prefixed(disposition_canonical_bytes(envelope))


def evidence_backing(evidence, artifacts):
    """The SPEC section 1 `evidenceBacking` map for a claim set.

    `artifacts` maps requirement id -> the captured artifact's exact bytes. Every
    requirement claimed `present` must have one; nothing else may. The digests are
    checkable because the artifact bytes themselves are retained (`evidence-artifacts.json`)
    — a backing digest with no retained preimage is a bare assertion, and the ceremony
    refuses it.
    """
    backing = {}
    for requirement, availability in (evidence or {}).items():
        if availability != "present":
            continue
        if requirement not in artifacts:
            raise CommitmentSchemaError(
                "no captured artifact for present claim: " + requirement
            )
        backing[requirement] = {
            "kind": "artifact",
            "digest": sha256_prefixed(artifacts[requirement]),
        }
    return backing


def artifacts_document(artifacts):
    """The retained captured-artifact store: requirement -> base64 of exact bytes."""
    import base64

    return {
        requirement: {"base64": base64.b64encode(payload).decode("ascii")}
        for requirement, payload in sorted(artifacts.items())
    }


def decode_artifacts(document):
    """Decode a retained artifact store; returns requirement -> exact bytes.

    Raises `CommitmentSchemaError` on any entry that is not a decodable base64 member,
    so an undecodable store is a validity problem rather than a silent miss.
    """
    import base64
    import binascii

    if not isinstance(document, dict):
        raise CommitmentSchemaError("evidence-artifacts must be an object")
    decoded = {}
    for requirement, entry in document.items():
        if (
            not isinstance(requirement, str)
            or not isinstance(entry, dict)
            or tuple(sorted(entry)) != ("base64",)
            or not isinstance(entry["base64"], str)
        ):
            raise CommitmentSchemaError(
                "evidence-artifacts entry is malformed: %r" % (requirement,)
            )
        try:
            decoded[requirement] = base64.b64decode(entry["base64"], validate=True)
        except (binascii.Error, ValueError) as error:
            raise CommitmentSchemaError(
                "evidence-artifacts entry is not valid base64: " + requirement
            ) from error
    return decoded


def build_commitment(
    *,
    pack_bytes,
    facts_bytes,
    evidence_bytes,
    envelope,
    executable_digest,
    backing,
    action,
    supported_extensions=(),
    pack_document=None,
):
    """Build the SPEC section 1 commitment from retained bytes and the envelope."""
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
            "evidenceBacking": dict(backing),
        },
        "action": None if action is None else dict(action),
    }


def commitment_bytes(commitment):
    """The canonical JCS text of `commitment.json` (SPEC section 3)."""
    return jcs(commitment)


def commitment_digest(commitment):
    """SPEC section 2: sha256 hex over the domain-separated JCS payload."""
    return sha256_hex(jcs({"domain": COMMITMENT_DOMAIN, "payload": commitment}))


def _no_duplicate_keys(pairs):
    """`object_pairs_hook` that refuses duplicate member names (RFC 8785 / I-JSON)."""
    seen = set()
    for name, _ in pairs:
        if name in seen:
            raise CommitmentSchemaError("commitment object has a duplicate member: " + name)
        seen.add(name)
    return dict(pairs)


def parse_commitment_bytes(raw):
    """Strictly parse commitment bytes: UTF-8, no duplicate keys, version 1.

    Encoding is *not* checked here — `canonical_encoding_problem` owns the byte-level
    rule, so a caller can tell a non-canonical encoding of the right commitment from a
    different commitment.
    """
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
    return candidate


def canonical_encoding_problem(raw, candidate):
    """None when `raw` is exactly the canonical JCS bytes of `candidate`."""
    if bytes(raw) == jcs(candidate):
        return None
    return "commitment bytes are not the canonical JCS encoding of their own content"


def validate_commitment(candidate):
    """Enforce SPEC section 1: exact field sets, closed vocabularies, digest shapes.

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
    backing = judgment["evidenceBacking"]
    if not isinstance(backing, dict):
        raise CommitmentSchemaError("judgment.evidenceBacking must be an object")
    for requirement, entry in backing.items():
        # Schema admits any carried backing shape ({kind} plus digest or ref); whether the
        # backing is *acceptable* — kind "artifact" with a digest, corresponding exactly to
        # the present claims — is the ceremony's `evidence-backing-invalid` step, so the
        # designed confusions (approval-record, observation-record) attribute there and
        # never to schema validity. See adapter/SPEC.md section 5, binding step 6.
        if not isinstance(requirement, str) or not requirement:
            raise CommitmentSchemaError("evidenceBacking has a non-string requirement id")
        if not isinstance(entry, dict) or not set(entry) <= {"kind", "digest", "ref"}:
            raise CommitmentSchemaError(
                "evidenceBacking." + requirement + " is not a backing object"
            )
        if not isinstance(entry.get("kind"), str) or not entry["kind"]:
            raise CommitmentSchemaError(
                "evidenceBacking." + requirement + ".kind must be a non-empty string"
            )

    action = candidate["action"]
    if action is None:
        return candidate
    if not isinstance(action, dict):
        raise CommitmentSchemaError("action must be an object or null")
    if tuple(sorted(action)) != tuple(sorted(ACTION_FIELDS)):
        raise CommitmentSchemaError("action field set is not section 1's")
    if not isinstance(action["gatekeeperId"], int) or isinstance(action["gatekeeperId"], bool):
        raise CommitmentSchemaError("action.gatekeeperId must be an integer")
    for field in ("resourceUrl", "actionKindTag", "boundResourceRevision"):
        if not isinstance(action[field], str) or not action[field]:
            raise CommitmentSchemaError("action." + field + " must be a non-empty string")
    if action["serverTrust"] not in ("vetted", "byo"):
        raise CommitmentSchemaError("action.serverTrust is out of vocabulary")
    if action["toolName"] != ACTION_TOOL:
        raise CommitmentSchemaError("action.toolName is not the executable tool literal")
    if not _is_hex64(action["argumentsDigest"]):
        raise CommitmentSchemaError("action.argumentsDigest is not bare 64-hex")
    return candidate
