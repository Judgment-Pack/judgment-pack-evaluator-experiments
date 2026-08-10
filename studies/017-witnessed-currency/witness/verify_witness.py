"""Layer WITNESS — sighting comparison over a presented registry view.

The prototype of RFC 0011 Unresolved #9's witness contract, at the lowest
possible commitment: a **sighting** is a witness key's signature over a
`{seriesId, head, position}` tuple it has observed; this layer compares a
presented snapshot against the retained sightings of the pinned witnesses.
Cross-verifier comparison is the same mechanism — an exchanged accepted head
IS a sighting — so one primitive models both the witness and the gossip
variant. It is a study registration, not a format proposal: no protocol, no
transport, no gossip semantics; sightings are retained bytes, and how they
would travel is out of scope.

Runs after Study 016's Layer CURRENCY (consumed as a digest-pinned unmodified
upstream) and records independently. Witnessing is **observability, not
prevention**: a conflict verdict here means a pinned witness attests a
different history — nothing is stopped, and what this layer cannot see is the
study's registered subject (collusion, partition, the retention horizon, a
fork after the sighted position).

Fail-closed in 016's discipline: strict duplicate-rejecting JSON, closed
schemas before any signature math, exception-bounded canonicalization,
registered size caps. One asymmetry, registered deliberately (design decision
D-3): an UNPINNED key's sighting is ignored-and-counted (it is untrusted
evidence, not a required input — the `neg-unpinned-conflict` control exhibits
the cost), while a sighting whose key-id label claims a PINNED witness but
fails verification is `witness-sighting-invalid` — the label can only cause
refusal, never acceptance.
"""

import base64
import hashlib
import json
import re

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Must equal the pinned Study 016 upstream's checkpoint domain — a harness
# test cross-checks this constant against the loaded module's.
DOMAIN_CHECKPOINT = "jps-study016-currency/checkpoint/1"
DOMAIN_SIGHTING = "jps-study017-witness/sighting/1"

MAX_SIGHTINGS_BYTES = 65_536
MAX_SIGHTINGS = 64

CODES = (
    "witness-unavailable",
    "witness-sighting-invalid",
    "witness-limits-exceeded",
    "snapshot-conflicts-with-witnessed-head",
    "snapshot-behind-witnessed-head",
)

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

WITNESSCONFIG_MEMBERS = {
    "witnessConfigVersion", "seriesId", "witnessKeys", "minimumSightings",
}
SIGHTINGS_DOC_MEMBERS = {"sightingsVersion", "sightings"}
SIGHTING_RECORD_MEMBERS = {"sighting", "witnessKeyId", "signature"}
SIGHTING_PAYLOAD_MEMBERS = {"sightingVersion", "seriesId", "head", "position"}


def result(verdict, code=None, detail=None):
    return {"verdict": verdict, "code": code, "detail": detail}


def _fail(code, detail=None):
    return result("fail", code, detail)


def _unavailable(detail):
    return result("unavailable", "witness-unavailable", detail)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _strict_json(data):
    def no_duplicates(pairs):
        members = {}
        for key, value in pairs:
            if key in members:
                raise ValueError("duplicate member name: %s" % key)
            members[key] = value
        return members
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)


def _canonical(domain, payload):
    return rfc8785.dumps({"domain": domain, "payload": payload})


def _witnessconfig_problem(config):
    if not isinstance(config, dict) or set(config) != WITNESSCONFIG_MEMBERS:
        return "witness configuration is not an object with exactly its four members"
    if config["witnessConfigVersion"] != "1":
        return "witness configuration is not version 1"
    if not isinstance(config["seriesId"], str) or not config["seriesId"]:
        return "no series is bound: witness pins are per-series"
    keys = config["witnessKeys"]
    if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
        return "witnessKeys is not a list of strings"
    if not _is_int(config["minimumSightings"]) or config["minimumSightings"] < 0:
        return "minimumSightings is not a non-negative integer"
    return None


def _sighting_record_problem(record):
    if not isinstance(record, dict) or set(record) != SIGHTING_RECORD_MEMBERS:
        return "record is not an object with exactly sighting/witnessKeyId/signature"
    payload = record["sighting"]
    if not isinstance(payload, dict) or set(payload) != SIGHTING_PAYLOAD_MEMBERS:
        return "sighting payload is not an object with exactly its four members"
    if payload["sightingVersion"] != "1":
        return "sighting is not version 1"
    if not isinstance(payload["seriesId"], str) or not payload["seriesId"]:
        return "sighting seriesId is not a non-empty string"
    if not isinstance(payload["head"], str) or not DIGEST_PATTERN.match(payload["head"]):
        return "sighting head is not a sha256-prefixed digest"
    if not _is_int(payload["position"]) or payload["position"] < 1:
        return "sighting position is not a positive integer"
    for member in ("witnessKeyId", "signature"):
        if not isinstance(record[member], str):
            return "record %s is not a string" % member
    return None


def _snapshot_digests(snapshot_bytes):
    """The presented view's checkpoint digests by position, recomputed.

    This layer owns content identity of the presented history, not its
    authority: signature validity under the currency authority is Layer
    CURRENCY's (independent) job, so only strict shape and digest
    recomputation happen here. Unusable input returns None — the layer then
    reports unavailable rather than guessing.
    """
    try:
        snapshot = _strict_json(snapshot_bytes)
        records = snapshot["checkpoints"]
        digests = []
        for record in records:
            canonical = _canonical(DOMAIN_CHECKPOINT, record["checkpoint"])
            digests.append("sha256:" + hashlib.sha256(canonical).hexdigest())
        if not digests:
            return None
        return digests
    except Exception:
        return None


def layer_witness(commitment, snapshot_bytes, witnessconfig_bytes, sightings_bytes):
    """The ordered ceremony (witness/SPEC.md section 2). First failure wins."""
    # 1. Pins and inputs.
    if witnessconfig_bytes is None:
        return _unavailable("witness configuration is absent")
    if not isinstance(witnessconfig_bytes, (bytes, bytearray)):
        return _unavailable("witness configuration input is not bytes")
    try:
        config = _strict_json(bytes(witnessconfig_bytes))
    except Exception as error:
        return _unavailable("witness configuration is not strict JSON: %s" % error)
    problem = _witnessconfig_problem(config)
    if problem is not None:
        return _unavailable(problem)
    pinned = {}
    for encoded in config["witnessKeys"]:
        try:
            raw = base64.b64decode(encoded, validate=True)
            key = Ed25519PublicKey.from_public_bytes(raw)
        except (ValueError, TypeError):
            return _unavailable("a pinned witness key is unreadable")
        pinned["ed25519:" + hashlib.sha256(raw).hexdigest()] = key

    if not isinstance(commitment, dict):
        return _unavailable("no conforming commitment to witness for")
    series_id = (commitment.get("judgment") or {}).get("packId")
    if not isinstance(series_id, str) or series_id != config["seriesId"]:
        return _unavailable(
            "the witness configuration binds a different series"
        )

    if sightings_bytes is None:
        return _unavailable("no retained sightings artifact")
    if len(sightings_bytes) > MAX_SIGHTINGS_BYTES:
        return _fail(
            "witness-limits-exceeded",
            "sightings exceed the registered byte limit (%d > %d)"
            % (len(sightings_bytes), MAX_SIGHTINGS_BYTES),
        )
    try:
        document = _strict_json(bytes(sightings_bytes))
    except Exception as error:
        return _unavailable("the retained sightings are not strict JSON: %s" % error)
    if not isinstance(document, dict) or set(document) != SIGHTINGS_DOC_MEMBERS:
        return _unavailable("sightings document is not an object with exactly its two members")
    if document["sightingsVersion"] != "1":
        return _unavailable("sightings document is not version 1")
    records = document["sightings"]
    if not isinstance(records, list):
        return _unavailable("sightings member is not a list")
    if len(records) > MAX_SIGHTINGS:
        return _fail(
            "witness-limits-exceeded",
            "sighting count exceeds the registered limit (%d > %d)"
            % (len(records), MAX_SIGHTINGS),
        )

    # 2. Validate every record; verify pinned-witness sightings; count and
    # skip unpinned ones (D-3: they can never cause acceptance, so ignoring
    # them costs only what the neg-unpinned-conflict control exhibits).
    valid = []
    ignored = 0
    for index, record in enumerate(records):
        problem = _sighting_record_problem(record)
        if problem is not None:
            return _fail(
                "witness-sighting-invalid",
                "sighting %d: %s" % (index + 1, problem),
            )
        key = pinned.get(record["witnessKeyId"])
        if key is None:
            ignored += 1
            continue
        try:
            canonical = _canonical(DOMAIN_SIGHTING, record["sighting"])
            key.verify(base64.b64decode(record["signature"], validate=True), canonical)
        except (InvalidSignature, ValueError, TypeError):
            return _fail(
                "witness-sighting-invalid",
                "sighting %d claims pinned witness %s but does not verify"
                % (index + 1, record["witnessKeyId"][:16]),
            )
        if record["sighting"]["seriesId"] == series_id:
            valid.append(record["sighting"])

    # 3. The enforcement clause, explicit.
    if len(valid) < config["minimumSightings"]:
        return _unavailable(
            "%d valid pinned sightings; the configuration requires %d"
            % (len(valid), config["minimumSightings"])
        )

    # 4. Comparison against the presented view — containment per sighting.
    digests = _snapshot_digests(bytes(snapshot_bytes)) if snapshot_bytes is not None else None
    if valid and digests is None:
        return _unavailable("the presented snapshot is unusable for comparison")
    for index, sighting in enumerate(valid):
        position = sighting["position"]
        if position > len(digests):
            return _fail(
                "snapshot-behind-witnessed-head",
                "a pinned witness attests position %d; the snapshot ends at %d"
                % (position, len(digests)),
            )
        if digests[position - 1] != sighting["head"]:
            return _fail(
                "snapshot-conflicts-with-witnessed-head",
                "a pinned witness attests a different head at position %d — "
                "the presented history is not the witnessed one" % position,
            )
    return result(
        "pass", None,
        "consistent with %d pinned sighting(s); %d unpinned ignored"
        % (len(valid), ignored),
    )
