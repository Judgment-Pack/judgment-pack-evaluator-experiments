"""Layer CURRENCY — the offline consumer step over a pinned registry snapshot.

RFC 0011 section 2, prototyped: given (a) the judgment commitment extracted from
the *verified* chain, (b) retained snapshot bytes, and (c) a trust configuration
holding the verifier's out-of-band pins, decide membership of the commitment's
`(packVersion, packDigest)` in the series' supported set at the snapshot's
position. Ordered, fail-closed, offline; no clock exists anywhere in this
module, and `effectiveFrom` is never read.

The verdict is deliberately narrow: a failure is "not current at the pinned
snapshot" and never "this decision was stale when used" (registry/SPEC.md
section 3; RFC 0011 R-7).

Fail-closed means every input lands in the registered vocabulary (round-1
R1-3): snapshot bytes are parsed by a duplicate-member-rejecting strict JSON
reader; every record is schema-checked — types, closed member sets, digest and
signature formats — *before* any canonicalization; canonicalization and
signature verification are exception-bounded; registered size limits refuse
oversized input before unbounded work (R1-7 / RFC 0011 R-13); and a malformed
trust configuration refuses rather than degrading (a broken `minimumHeadPin`
is never read as "no pin").

Signer identity is what a single pinned key can actually establish (R1-6): a
signature either verifies under the pinned authority key or it does not.
`authorityKeyId` is an unauthenticated routing label — it is compared and
reported in `detail`, never trusted for attribution, and a wrong signer is
indistinguishable from a corrupted signature to this verifier. One code,
`snapshot-signature-invalid`, covers both, and the SPEC records the
indistinguishability as a property of the trust model.

Everything is recomputed from the snapshot bytes: stored digests are checked
against recomputation, signatures are verified under the *pinned* key only,
and the writer (`registry/checkpoint.py`) is never imported.
"""

import base64
import hashlib
import json
import re

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN_CHECKPOINT = "jps-study016-currency/checkpoint/1"
DOMAIN_SNAPSHOT = "jps-study016-currency/snapshot/1"

# Registered resource limits (RFC 0011 R-13): refusal above any of them is the
# registered outcome `snapshot-limits-exceeded`, checked before unbounded work.
MAX_SNAPSHOT_BYTES = 1_048_576
MAX_CHECKPOINTS = 1_024
MAX_SUPPORTED_SET = 512

# The exhaustive layer vocabulary. registry/SPEC.md section 4 is the governing
# table; a harness test diffs it against this tuple and constructs a minimal
# condition for every member.
CODES = (
    "currency-unavailable",
    "snapshot-signature-invalid",
    "snapshot-chain-inconsistent",
    "binding-rebound",
    "snapshot-limits-exceeded",
    "snapshot-behind-pinned-minimum-head",
    "series-unknown-at-snapshot",
    "not-current-at-snapshot",
)

EVENTS = ("add", "retire", "reinstate")

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

CHECKPOINT_REQUIRED = {
    "checkpointVersion", "sequence", "seriesId", "event", "packVersion",
    "effectiveFrom", "previousCheckpointDigest",
}
RECORD_MEMBERS = {"checkpoint", "checkpointDigest", "authorityKeyId", "signature"}
SNAPSHOT_MEMBERS = {"snapshotVersion", "checkpoints", "attestation"}
ATTESTATION_MEMBERS = {"payload", "authorityKeyId", "signature"}
ATTESTATION_PAYLOAD_MEMBERS = {"snapshotVersion", "head", "position"}
TRUSTCONFIG_MEMBERS = {
    "trustConfigVersion", "seriesId", "authorityPublicKey", "genesisHead",
    "minimumHeadPin",
}
MINIMUM_MEMBERS = {"head", "position"}


def result(verdict, code=None, detail=None):
    return {"verdict": verdict, "code": code, "detail": detail}


def _fail(code, detail=None):
    return result("fail", code, detail)


def _unavailable(detail):
    return result("unavailable", "currency-unavailable", detail)


def _is_int(value):
    """A JSON integer: bool is excluded deliberately (True == 1 in Python)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _strict_json(data):
    """Duplicate-member-rejecting parse of exact UTF-8 bytes."""
    def no_duplicates(pairs):
        members = {}
        for key, value in pairs:
            if key in members:
                raise ValueError("duplicate member name: %s" % key)
            members[key] = value
        return members
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)


def _canonical(domain, payload):
    """JCS of the domain envelope; exception-bounded by every caller."""
    return rfc8785.dumps({"domain": domain, "payload": payload})


def _sha256_prefixed(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _verify_under_pinned(key, pinned_id, record_key_id, signature_b64,
                         domain, payload, what):
    """Pass/fail under the pinned key alone (R1-6). Returns None on success.

    The record's `authorityKeyId` is unauthenticated; it is reported in the
    detail for legibility but a mismatch is never its own code — a wrong
    signer and a corrupted signature are indistinguishable here.
    """
    label = ""
    if record_key_id != pinned_id:
        label = " (record labels an unpinned key id — label is unauthenticated)"
    try:
        canonical = _canonical(domain, payload)
    except Exception as error:
        return _fail(
            "snapshot-chain-inconsistent",
            "%s payload is not canonicalizable: %s" % (what, error),
        )
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, TypeError):
        return _fail(
            "snapshot-signature-invalid",
            "%s signature is not valid base64%s" % (what, label),
        )
    try:
        key.verify(signature, canonical)
    except InvalidSignature:
        return _fail(
            "snapshot-signature-invalid",
            "%s does not verify under the pinned authority key%s" % (what, label),
        )
    return None


# --------------------------------------------------------------------------
# schema validation — closed shapes, checked before any crypto or folding
# --------------------------------------------------------------------------

def _trustconfig_problem(trustconfig):
    if not isinstance(trustconfig, dict):
        return "trust configuration is absent or not an object"
    if trustconfig.get("trustConfigVersion") != "1":
        return "trust configuration is not version 1"
    unknown = set(trustconfig) - TRUSTCONFIG_MEMBERS
    if unknown:
        return "trust configuration carries unknown members: %s" % ", ".join(sorted(unknown))
    if not isinstance(trustconfig.get("seriesId"), str) or not trustconfig["seriesId"]:
        return "no series is bound: the pins are per-series (Core section 10 forbids inferring authority), so a configuration without seriesId cannot authorize any check"
    if not isinstance(trustconfig.get("authorityPublicKey"), str):
        return "no authority key is pinned for this series"
    genesis = trustconfig.get("genesisHead")
    if not isinstance(genesis, str) or not DIGEST_PATTERN.match(genesis):
        return ("no genesis head is pinned: below the genesis pin this verifier "
                "is trust-on-first-use and refuses to call anything current")
    minimum = trustconfig.get("minimumHeadPin", None)
    if minimum is not None:
        if not isinstance(minimum, dict) or set(minimum) != MINIMUM_MEMBERS:
            return "minimumHeadPin is malformed: it must be null or {head, position}"
        if not isinstance(minimum.get("head"), str) or not DIGEST_PATTERN.match(minimum["head"]):
            return "minimumHeadPin.head is not a sha256-prefixed digest"
        if not _is_int(minimum.get("position")) or minimum["position"] < 1:
            return "minimumHeadPin.position is not a positive integer"
    return None


def _checkpoint_record_problem(record):
    if not isinstance(record, dict) or set(record) != RECORD_MEMBERS:
        return "record is not an object with exactly checkpoint/checkpointDigest/authorityKeyId/signature"
    payload = record["checkpoint"]
    if not isinstance(payload, dict):
        return "checkpoint payload is not an object"
    members = set(payload)
    missing = CHECKPOINT_REQUIRED - members
    if missing:
        return "checkpoint payload lacks %s" % ", ".join(sorted(missing))
    unknown = members - CHECKPOINT_REQUIRED - {"packDigest"}
    if unknown:
        return "checkpoint payload carries unknown members %s" % ", ".join(sorted(unknown))
    if payload["checkpointVersion"] != "1":
        return "checkpoint version is not 1"
    if payload["event"] not in EVENTS:
        return "checkpoint event is not add/retire/reinstate"
    if not _is_int(payload["sequence"]) or payload["sequence"] < 1:
        return "checkpoint sequence is not a positive integer"
    for member in ("seriesId", "packVersion", "effectiveFrom"):
        if not isinstance(payload[member], str) or not payload[member]:
            return "checkpoint %s is not a non-empty string" % member
    previous = payload["previousCheckpointDigest"]
    if previous is not None and (
        not isinstance(previous, str) or not DIGEST_PATTERN.match(previous)
    ):
        return "previousCheckpointDigest is neither null nor a sha256-prefixed digest"
    if (payload["event"] == "add") != ("packDigest" in members):
        return "packDigest is carried exactly on add events"
    if "packDigest" in members and (
        not isinstance(payload["packDigest"], str)
        or not DIGEST_PATTERN.match(payload["packDigest"])
    ):
        return "packDigest is not a sha256-prefixed digest"
    for member in ("checkpointDigest", "authorityKeyId", "signature"):
        if not isinstance(record[member], str):
            return "record %s is not a string" % member
    if not DIGEST_PATTERN.match(record["checkpointDigest"]):
        return "checkpointDigest is not a sha256-prefixed digest"
    return None


def _attestation_problem(attestation):
    if not isinstance(attestation, dict) or set(attestation) != ATTESTATION_MEMBERS:
        return "attestation is not an object with exactly payload/authorityKeyId/signature"
    payload = attestation["payload"]
    if not isinstance(payload, dict) or set(payload) != ATTESTATION_PAYLOAD_MEMBERS:
        return "attestation payload is not an object with exactly snapshotVersion/head/position"
    if payload["snapshotVersion"] != "1":
        return "attestation payload snapshotVersion is not 1"
    if not isinstance(payload["head"], str) or not DIGEST_PATTERN.match(payload["head"]):
        return "attestation head is not a sha256-prefixed digest"
    if not _is_int(payload["position"]) or payload["position"] < 1:
        return "attestation position is not a positive integer"
    for member in ("authorityKeyId", "signature"):
        if not isinstance(attestation[member], str):
            return "attestation %s is not a string" % member
    return None


# --------------------------------------------------------------------------
# the fold
# --------------------------------------------------------------------------

def fold_supported(payloads, series_id):
    """The supported set of `series_id` after folding `payloads` in order.

    Returns `(supported, problem)`. Bindings are immutable once added and
    `add` never reactivates (round-1 R1-13): a later `add` of an already
    bound version is `binding-rebound` when the digest differs and an
    inconsistent history when it is the same — `reinstate` is the only
    re-entry event. Retiring a non-current version and reinstating a
    non-retired one are inconsistent histories. The supported set is bounded
    by MAX_SUPPORTED_SET (`limit` problem).
    """
    supported = {}
    retired = {}
    bindings = {}
    for payload in payloads:
        if payload["seriesId"] != series_id:
            continue
        version = payload["packVersion"]
        event = payload["event"]
        if event == "add":
            digest = payload["packDigest"]
            if version in bindings:
                if bindings[version] != digest:
                    return None, "binding-rebound"
                return None, (
                    "add for an already bound version %s: reinstate is the "
                    "re-entry event" % version
                )
            bindings[version] = digest
            supported[version] = digest
            if len(supported) > MAX_SUPPORTED_SET:
                return None, "limit"
        elif event == "retire":
            if version not in supported:
                return None, "retire for a version that is not current: %s" % version
            retired[version] = supported.pop(version)
        else:  # reinstate
            if version not in retired:
                return None, "reinstate for a version that is not retired: %s" % version
            supported[version] = retired.pop(version)
    return supported, None


# --------------------------------------------------------------------------
# the ceremony
# --------------------------------------------------------------------------

def layer_currency(commitment, snapshot_bytes, trustconfig_bytes):
    """The ordered ceremony (registry/SPEC.md section 3). First failure wins.

    All three inputs are what the cell retains: the parsed commitment from the
    verified chain's signed binding point, the snapshot bytes, and the trust
    configuration BYTES — parsed here, strictly, so a duplicate-member or
    otherwise malformed configuration refuses at this layer rather than being
    laundered through a lax reader upstream (round-2 residual of R1-3).
    """
    # 1. The out-of-band pins: series binding, authority key, genesis head.
    #    A malformed configuration refuses; it never degrades to "no pin".
    if snapshot_bytes is not None and not isinstance(snapshot_bytes, (bytes, bytearray)):
        return _unavailable("snapshot input is not bytes")
    if trustconfig_bytes is None:
        return _unavailable("trust configuration is absent")
    if not isinstance(trustconfig_bytes, (bytes, bytearray)):
        return _unavailable("trust configuration input is not bytes")
    try:
        trustconfig = _strict_json(bytes(trustconfig_bytes))
    except Exception as error:
        return _unavailable("trust configuration is not strict JSON: %s" % error)
    problem = _trustconfig_problem(trustconfig)
    if problem is not None:
        return _unavailable(problem)
    try:
        raw_key = base64.b64decode(trustconfig["authorityPublicKey"], validate=True)
        pinned = Ed25519PublicKey.from_public_bytes(raw_key)
    except (ValueError, TypeError):
        return _unavailable("the pinned authority key is unreadable")
    pinned_id = "ed25519:" + hashlib.sha256(raw_key).hexdigest()

    # 2. The commitment tuple, bound to the configured series.
    if not isinstance(commitment, dict):
        return _unavailable("no conforming commitment to check currency for")
    judgment = commitment.get("judgment") or {}
    series_id = judgment.get("packId")
    member = (judgment.get("packVersion"), judgment.get("packDigest"))
    if not isinstance(series_id, str) or not all(isinstance(m, str) for m in member):
        return _unavailable("the commitment carries no complete identity tuple")
    if series_id != trustconfig["seriesId"]:
        return _unavailable(
            "the trust configuration binds a different series: the pins are "
            "per-series and confer no authority over %s" % series_id
        )

    # 3. The snapshot artifact: size limit, strict parse, closed schema.
    if snapshot_bytes is None:
        return _unavailable("no retained registry snapshot")
    if len(snapshot_bytes) > MAX_SNAPSHOT_BYTES:
        return _fail(
            "snapshot-limits-exceeded",
            "snapshot exceeds the registered byte limit (%d > %d)"
            % (len(snapshot_bytes), MAX_SNAPSHOT_BYTES),
        )
    try:
        snapshot = _strict_json(snapshot_bytes)
    except Exception as error:
        return _fail(
            "snapshot-chain-inconsistent",
            "the retained snapshot is not strict JSON: %s" % error,
        )
    if not isinstance(snapshot, dict) or set(snapshot) != SNAPSHOT_MEMBERS:
        return _fail(
            "snapshot-chain-inconsistent",
            "snapshot is not an object with exactly snapshotVersion/checkpoints/attestation",
        )
    if snapshot["snapshotVersion"] != "1":
        return _fail("snapshot-chain-inconsistent", "snapshot is not version 1")
    records = snapshot["checkpoints"]
    if not isinstance(records, list) or not records:
        return _fail("snapshot-chain-inconsistent", "snapshot carries no checkpoints")
    if len(records) > MAX_CHECKPOINTS:
        return _fail(
            "snapshot-limits-exceeded",
            "snapshot exceeds the registered checkpoint limit (%d > %d)"
            % (len(records), MAX_CHECKPOINTS),
        )
    problem = _attestation_problem(snapshot["attestation"])
    if problem is not None:
        return _fail("snapshot-chain-inconsistent", problem)
    for index, record in enumerate(records):
        problem = _checkpoint_record_problem(record)
        if problem is not None:
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d: %s" % (index + 1, problem),
            )

    # 4. Signatures, under the pinned key alone.
    attestation = snapshot["attestation"]
    failure = _verify_under_pinned(
        pinned, pinned_id, attestation["authorityKeyId"], attestation["signature"],
        DOMAIN_SNAPSHOT, attestation["payload"], "snapshot head attestation",
    )
    if failure is not None:
        return failure
    digests = []
    for index, record in enumerate(records):
        failure = _verify_under_pinned(
            pinned, pinned_id, record["authorityKeyId"], record["signature"],
            DOMAIN_CHECKPOINT, record["checkpoint"], "checkpoint %d" % (index + 1),
        )
        if failure is not None:
            return failure
        recomputed = _sha256_prefixed(_canonical(DOMAIN_CHECKPOINT, record["checkpoint"]))
        if record["checkpointDigest"] != recomputed:
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d: stored digest does not match its recomputation"
                % (index + 1),
            )
        digests.append(recomputed)

    # 5. Structural chain: contiguous sequence, linkage, genesis pin, head.
    payloads = [record["checkpoint"] for record in records]
    for index, payload in enumerate(payloads):
        if payload["sequence"] != index + 1:
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d carries sequence %r" % (index + 1, payload["sequence"]),
            )
        expected_previous = None if index == 0 else digests[index - 1]
        if payload["previousCheckpointDigest"] != expected_previous:
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d does not bind its predecessor" % (index + 1),
            )
    if digests[0] != trustconfig["genesisHead"]:
        return _fail(
            "snapshot-chain-inconsistent",
            "the history does not extend the pinned genesis head",
        )
    payload = attestation["payload"]
    if payload["head"] != digests[-1] or payload["position"] != len(records):
        return _fail(
            "snapshot-chain-inconsistent",
            "the head attestation does not describe this checkpoint list",
        )

    # 6. The recency floor, when the caller provisions one. This is a PIN, not
    # verifier-maintained state (round-1 R1-5): the layer holds no storage and
    # returns no state update; a production verifier would persist its last
    # accepted head and supply it here. Containment, not position arithmetic —
    # a same-length different fork also refuses.
    minimum = trustconfig.get("minimumHeadPin", None)
    if minimum is not None:
        position = minimum["position"]
        if position > len(digests) or digests[position - 1] != minimum["head"]:
            return _fail(
                "snapshot-behind-pinned-minimum-head",
                "the snapshot does not contain the pinned minimum head at its position",
            )

    # 7. Fold, then membership — the verdict is membership at this snapshot,
    # nothing more.
    supported, problem = fold_supported(payloads, series_id)
    if problem == "binding-rebound":
        return _fail(
            "binding-rebound",
            "the history rebinds a version to a different digest",
        )
    if problem == "limit":
        return _fail(
            "snapshot-limits-exceeded",
            "the supported set exceeds the registered limit (%d)" % MAX_SUPPORTED_SET,
        )
    if problem is not None:
        return _fail("snapshot-chain-inconsistent", problem)
    if not any(payload["seriesId"] == series_id for payload in payloads):
        return _fail(
            "series-unknown-at-snapshot",
            "the snapshot carries no events for this series",
        )
    version, digest = member
    if supported.get(version) == digest:
        return result("pass", None, "current at snapshot position %d" % len(records))
    return _fail(
        "not-current-at-snapshot",
        "(%s, %s) is not in the supported set at snapshot position %d"
        % (version, digest, len(records)),
    )
