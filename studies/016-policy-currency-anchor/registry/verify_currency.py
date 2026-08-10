"""Layer CURRENCY — the offline consumer step over a pinned registry snapshot.

RFC 0011 section 2, prototyped: given (a) the judgment commitment extracted from
the *verified* chain, (b) retained snapshot bytes, and (c) a trust configuration
holding the verifier's out-of-band pins, decide membership of the commitment's
`(packVersion, packDigest)` in the series' supported set at the snapshot's
position. Ordered, fail-closed, offline; no clock exists anywhere in this
module, and `effectiveFrom` is never read.

The verdict is deliberately narrow: a failure is "not current at the pinned
snapshot" and never "this decision was stale when used" — a legitimate decision
audited after its version retired reads identically to a genuine stale reuse
(registry/SPEC.md section 3; RFC 0011 R-7).

Everything is recomputed from the snapshot bytes: stored digests are checked
against recomputation, signatures are verified under the *pinned* key only, and
the writer (`registry/checkpoint.py`) is never imported.
"""

import base64
import hashlib
import json

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN_CHECKPOINT = "jps-study016-currency/checkpoint/1"
DOMAIN_SNAPSHOT = "jps-study016-currency/snapshot/1"

# The exhaustive layer vocabulary. registry/SPEC.md section 4 is the governing
# table; a harness test diffs it against this tuple and constructs a minimal
# condition for every member.
CODES = (
    "currency-unavailable",
    "snapshot-authority-unpinned",
    "snapshot-signature-invalid",
    "snapshot-chain-inconsistent",
    "binding-rebound",
    "snapshot-older-than-accepted-head",
    "series-unknown-at-snapshot",
    "not-current-at-snapshot",
)

EVENTS = ("add", "retire", "reinstate")

CHECKPOINT_REQUIRED = {
    "checkpointVersion", "sequence", "seriesId", "event", "packVersion",
    "effectiveFrom", "previousCheckpointDigest",
}


def result(verdict, code=None, detail=None):
    return {"verdict": verdict, "code": code, "detail": detail}


def _fail(code, detail=None):
    return result("fail", code, detail)


def _unavailable(detail):
    return result("unavailable", "currency-unavailable", detail)


def _canonical(domain, payload):
    return rfc8785.dumps({"domain": domain, "payload": payload})


def _sha256_prefixed(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _pinned_key(trustconfig):
    raw = base64.b64decode(trustconfig["authorityPublicKey"], validate=True)
    key = Ed25519PublicKey.from_public_bytes(raw)
    return key, "ed25519:" + hashlib.sha256(raw).hexdigest()


def _verify_signed(key, pinned_id, record_key_id, signature_b64, signed_bytes,
                   what):
    """Key-identity first, then the signature math — the codes turn on which."""
    if record_key_id != pinned_id:
        return _fail(
            "snapshot-authority-unpinned",
            "%s is signed under an unpinned authority key" % what,
        )
    try:
        key.verify(base64.b64decode(signature_b64, validate=True), signed_bytes)
    except (InvalidSignature, ValueError, TypeError):
        return _fail(
            "snapshot-signature-invalid",
            "%s signature does not verify under the pinned key" % what,
        )
    return None


def _checkpoint_shape_problem(record):
    if not isinstance(record, dict):
        return "checkpoint record is not an object"
    payload = record.get("checkpoint")
    if not isinstance(payload, dict):
        return "checkpoint payload is not an object"
    missing = CHECKPOINT_REQUIRED - set(payload)
    if missing:
        return "checkpoint payload lacks %s" % ", ".join(sorted(missing))
    unknown = set(payload) - CHECKPOINT_REQUIRED - {"packDigest"}
    if unknown:
        return "checkpoint payload carries unknown members %s" % ", ".join(sorted(unknown))
    if payload.get("checkpointVersion") != "1":
        return "checkpoint version is not 1"
    if payload.get("event") not in EVENTS:
        return "checkpoint event is not add/retire/reinstate"
    if (payload["event"] == "add") != ("packDigest" in payload):
        return "packDigest is carried exactly on add events"
    for member in ("signature", "authorityKeyId", "checkpointDigest"):
        if not isinstance(record.get(member), str):
            return "checkpoint record lacks %s" % member
    return None


def fold_supported(payloads, series_id):
    """The supported set of `series_id` after folding `payloads` in order.

    Returns `(supported, bindings, problem)`. `bindings` maps version to the
    digest it was ever bound to — bindings are immutable once added, across
    retirement, so a later add rebinding a version is `binding-rebound` rather
    than an ordinary history defect. Any other illegal transition (retiring a
    version that is not current, reinstating one that is not retired, adding a
    `(version, digest)` that is already current) is a `problem` string.
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
            if version in bindings and bindings[version] != digest:
                return None, bindings, "binding-rebound"
            if version in supported:
                return None, bindings, (
                    "add for a version that is already current: %s" % version
                )
            bindings[version] = digest
            supported[version] = digest
            retired.pop(version, None)
        elif event == "retire":
            if version not in supported:
                return None, bindings, (
                    "retire for a version that is not current: %s" % version
                )
            retired[version] = supported.pop(version)
        else:  # reinstate
            if version not in retired:
                return None, bindings, (
                    "reinstate for a version that is not retired: %s" % version
                )
            supported[version] = retired.pop(version)
    return supported, bindings, None


def layer_currency(commitment, snapshot_bytes, trustconfig):
    """The ordered ceremony (registry/SPEC.md section 3). First failure wins."""
    # 1. The two out-of-band pins. No pins, no safe verdict — never a pass.
    if not isinstance(trustconfig, dict) or trustconfig.get("trustConfigVersion") != "1":
        return _unavailable("trust configuration is absent or not version 1")
    if not isinstance(trustconfig.get("authorityPublicKey"), str):
        return _unavailable("no authority key is pinned for this series")
    if not isinstance(trustconfig.get("genesisHead"), str):
        return _unavailable(
            "no genesis head is pinned: below the genesis pin this verifier "
            "is trust-on-first-use and refuses to call anything current"
        )
    try:
        pinned, pinned_id = _pinned_key(trustconfig)
    except (ValueError, TypeError):
        return _unavailable("the pinned authority key is unreadable")

    # 2. The commitment tuple and the snapshot artifact.
    if not isinstance(commitment, dict):
        return _unavailable("no conforming commitment to check currency for")
    judgment = commitment.get("judgment") or {}
    series_id = judgment.get("packId")
    member = (judgment.get("packVersion"), judgment.get("packDigest"))
    if not isinstance(series_id, str) or not all(isinstance(m, str) for m in member):
        return _unavailable("the commitment carries no complete identity tuple")
    if snapshot_bytes is None:
        return _unavailable("no retained registry snapshot")
    try:
        snapshot = json.loads(snapshot_bytes.decode("utf-8"))
    except Exception:
        return _unavailable("the retained registry snapshot is unreadable")
    if not isinstance(snapshot, dict) or snapshot.get("snapshotVersion") != "1":
        return _unavailable("the retained registry snapshot is not version 1")

    # 3. The head attestation, under the pinned key alone.
    attestation = snapshot.get("attestation")
    if not isinstance(attestation, dict) or not isinstance(
        attestation.get("payload"), dict
    ):
        return _fail("snapshot-chain-inconsistent", "attestation is absent or malformed")
    failure = _verify_signed(
        pinned, pinned_id,
        attestation.get("authorityKeyId"),
        attestation.get("signature", ""),
        _canonical(DOMAIN_SNAPSHOT, attestation["payload"]),
        "snapshot head attestation",
    )
    if failure is not None:
        return failure

    # 4. Every checkpoint signature, in sequence order.
    records = snapshot.get("checkpoints")
    if not isinstance(records, list) or not records:
        return _fail("snapshot-chain-inconsistent", "snapshot carries no checkpoints")
    payloads = []
    for index, record in enumerate(records):
        problem = _checkpoint_shape_problem(record)
        if problem is not None:
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d: %s" % (index + 1, problem),
            )
        signed = _canonical(DOMAIN_CHECKPOINT, record["checkpoint"])
        failure = _verify_signed(
            pinned, pinned_id,
            record["authorityKeyId"], record["signature"], signed,
            "checkpoint %d" % (index + 1),
        )
        if failure is not None:
            return failure
        if record["checkpointDigest"] != _sha256_prefixed(signed):
            return _fail(
                "snapshot-chain-inconsistent",
                "checkpoint %d: stored digest does not match its recomputation"
                % (index + 1),
            )
        payloads.append(record["checkpoint"])

    # 5. Structural chain: contiguous sequence, linkage, genesis pin, head.
    digests = [record["checkpointDigest"] for record in records]
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
    if payload.get("head") != digests[-1] or payload.get("position") != len(records):
        return _fail(
            "snapshot-chain-inconsistent",
            "the head attestation does not describe this checkpoint list",
        )

    # 6. The recency floor, when the verifier persists one. Prefix containment,
    # not mere position: a same-length different fork must also refuse.
    minimum = trustconfig.get("persistedMinimumHead")
    if isinstance(minimum, dict):
        position = minimum.get("position")
        head = minimum.get("head")
        if (
            not isinstance(position, int)
            or position < 1
            or position > len(digests)
            or digests[position - 1] != head
        ):
            return _fail(
                "snapshot-older-than-accepted-head",
                "the snapshot does not contain the persisted minimum accepted head",
            )

    # 7. Fold, then membership — the verdict is membership at this snapshot,
    # nothing more.
    supported, _, problem = fold_supported(payloads, series_id)
    if problem == "binding-rebound":
        return _fail(
            "binding-rebound",
            "the history rebinds a version to a different digest",
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
