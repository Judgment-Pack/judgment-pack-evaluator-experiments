"""Layer WITNESS — sighting comparison over a presented registry view.

The prototype of RFC 0011 Unresolved #9's witness contract, at the lowest
possible commitment: a **sighting** is a witness key's signature over a
`{seriesId, head, position}` tuple it has observed; this layer compares a
presented snapshot against the retained sightings of the pinned witnesses.
It is a study registration, not a format proposal: no protocol, no transport,
no gossip semantics. The schema *could* encode a head exchanged between
verifiers, but only under a separately specified authentication, role,
acceptance and delivery contract that this study does not define (round-1
R1-15).

Runs after Study 016's Layer CURRENCY (a digest-pinned unmodified upstream)
and records independently. Witnessing is **observability, not prevention**.

**Routing is by verification, never by label** (round-1 R1-4, a confirmed
attack on the previous design). Each record is checked against every pinned
witness key: a record that verifies under one is *attributed* to it and enters
the comparison; a record that verifies under none is *unattributed* — counted
and reported, never a comparison input and never a refusal. The record's own
`witnessKeyId` is descriptive only. The previous design routed on that
unauthenticated label, which let a relabelled honest record be ignored and
turned a detected conflict into a pass.

Closing that channel does not close **suppression**, and the study registers
the residue rather than hiding it: whoever controls which sightings reach the
verifier can drop a conflicting record, corrupt its signature, or re-sign its
payload under a fresh key — all three land in the same unattributed bucket or
in no bucket at all, and none is distinguishable from a witness that simply
never spoke. `minimumSightings` counts; `requiredWitnesses` names. Neither can
tell silence from suppression.

Fail-closed in 016's discipline: strict duplicate-rejecting JSON, closed
schemas and type checks before any signature math, exception-bounded
conversions and canonicalization, registered size caps, and an
order-independent precedence over all valid sightings.
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
    "witness-required-absent",
    "snapshot-conflicts-with-witnessed-head",
    "snapshot-behind-witnessed-head",
)

# Registered, order-independent precedence over all valid sightings (round-1
# R1-11): a conflict inside the presented history outranks a sighting beyond
# its end, whatever order the unsigned retained list happens to carry.
PRECEDENCE = ("snapshot-conflicts-with-witnessed-head",
              "snapshot-behind-witnessed-head")

RECENCY_POLICIES = ("ignore", "refuse-behind")

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

WITNESSCONFIG_MEMBERS = {
    "witnessConfigVersion", "seriesId", "witnessKeys", "minimumSightings",
    "requiredWitnesses", "recencyPolicy",
}
SIGHTINGS_DOC_MEMBERS = {"sightingsVersion", "sightings"}
SIGHTING_RECORD_MEMBERS = {"sighting", "witnessKeyId", "signature"}
SIGHTING_PAYLOAD_MEMBERS = {"sightingVersion", "seriesId", "head", "position"}


def result(verdict, code=None, detail=None, **fields):
    """Layer record. `comparisonPerformed` and the counts are REGISTERED
    structured fields, not free text (round-1 R1-9): a pass after zero
    comparisons must be machine-distinguishable from a pass after a
    sighting-backed one."""
    record = {"verdict": verdict, "code": code, "detail": detail,
              "comparisonPerformed": False, "validSightings": 0,
              "unattributedSightings": 0}
    record.update(fields)
    return record


def _fail(code, detail=None, **fields):
    return result("fail", code, detail, **fields)


def _unavailable(detail, **fields):
    return result("unavailable", "witness-unavailable", detail, **fields)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_bytes(value):
    return isinstance(value, (bytes, bytearray))


def _strict_json(data):
    def no_duplicates(pairs):
        members = {}
        for key, value in pairs:
            if key in members:
                raise ValueError("duplicate member name: %s" % key)
            members[key] = value
        return members
    return json.loads(bytes(data).decode("utf-8"), object_pairs_hook=no_duplicates)


def _canonical(domain, payload):
    return rfc8785.dumps({"domain": domain, "payload": payload})


def _key_id(raw):
    return "ed25519:" + hashlib.sha256(raw).hexdigest()


def _witnessconfig_problem(config):
    if not isinstance(config, dict) or set(config) != WITNESSCONFIG_MEMBERS:
        return "witness configuration is not an object with exactly its six members"
    if config["witnessConfigVersion"] != "1":
        return "witness configuration is not version 1"
    if not isinstance(config["seriesId"], str) or not config["seriesId"]:
        return "no series is bound: witness pins are per-series"
    for member in ("witnessKeys", "requiredWitnesses"):
        value = config[member]
        if not isinstance(value, list) or not all(isinstance(k, str) for k in value):
            return "%s is not a list of strings" % member
    if not _is_int(config["minimumSightings"]) or config["minimumSightings"] < 0:
        return "minimumSightings is not a non-negative integer"
    if config["recencyPolicy"] not in RECENCY_POLICIES:
        return "recencyPolicy is not one of %s" % ", ".join(RECENCY_POLICIES)
    if not set(config["requiredWitnesses"]) <= set(config["witnessKeys"]):
        return "requiredWitnesses names a key that is not pinned"
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

    Content identity only: authority-signature validity over the snapshot is
    Layer CURRENCY's independent job. Returns None when the artifact cannot be
    used for comparison at all.
    """
    try:
        snapshot = _strict_json(snapshot_bytes)
        digests = [
            "sha256:" + hashlib.sha256(
                _canonical(DOMAIN_CHECKPOINT, record["checkpoint"])
            ).hexdigest()
            for record in snapshot["checkpoints"]
        ]
        return digests or None
    except Exception:
        return None


def layer_witness(commitment, snapshot_bytes, witnessconfig_bytes, sightings_bytes):
    """The ordered ceremony (witness/SPEC.md section 2)."""
    # 1. Pins and inputs — every conversion type-checked before use (R1-12).
    if not _is_bytes(witnessconfig_bytes):
        return _unavailable("witness configuration is absent or not bytes")
    try:
        config = _strict_json(witnessconfig_bytes)
    except Exception as error:
        return _unavailable("witness configuration is not strict JSON: %s" % error)
    problem = _witnessconfig_problem(config)
    if problem is not None:
        return _unavailable(problem)

    pinned = []
    for encoded in config["witnessKeys"]:
        try:
            raw = base64.b64decode(encoded, validate=True)
            pinned.append((encoded, _key_id(raw), Ed25519PublicKey.from_public_bytes(raw)))
        except (ValueError, TypeError):
            return _unavailable("a pinned witness key is unreadable")

    if not isinstance(commitment, dict):
        return _unavailable("no conforming commitment to witness for")
    judgment = commitment.get("judgment")
    if not isinstance(judgment, dict):
        return _unavailable("the commitment carries no judgment object")
    series_id = judgment.get("packId")
    if not isinstance(series_id, str) or series_id != config["seriesId"]:
        return _unavailable("the witness configuration binds a different series")

    if not _is_bytes(sightings_bytes):
        return _unavailable("no retained sightings artifact")
    if len(sightings_bytes) > MAX_SIGHTINGS_BYTES:
        return _fail("witness-limits-exceeded",
                     "sightings exceed the registered byte limit (%d > %d)"
                     % (len(sightings_bytes), MAX_SIGHTINGS_BYTES))
    try:
        document = _strict_json(sightings_bytes)
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
        return _fail("witness-limits-exceeded",
                     "sighting count exceeds the registered limit (%d > %d)"
                     % (len(records), MAX_SIGHTINGS))

    # 2. Schema first (fail-closed), then attribution BY VERIFICATION (R1-4).
    valid = []
    attributed_keys = set()
    unattributed = 0
    for index, record in enumerate(records):
        problem = _sighting_record_problem(record)
        if problem is not None:
            return _fail("witness-sighting-invalid",
                         "sighting %d: %s" % (index + 1, problem))
        try:
            canonical = _canonical(DOMAIN_SIGHTING, record["sighting"])
            signature = base64.b64decode(record["signature"], validate=True)
        except Exception:
            unattributed += 1
            continue
        owner = None
        for encoded, key_id, key in pinned:
            try:
                key.verify(signature, canonical)
            except (InvalidSignature, ValueError, TypeError):
                continue
            owner = encoded
            break
        if owner is None:
            unattributed += 1
            continue
        # Series scoping FIRST (round-2 R2-1, reproduced): a verifying record
        # for an unrelated series must not satisfy a per-series named-witness
        # floor. Attribution for enforcement counts only same-series records.
        if record["sighting"]["seriesId"] != series_id:
            continue
        attributed_keys.add(owner)
        valid.append(record["sighting"])

    counts = {"validSightings": len(valid), "unattributedSightings": unattributed}

    # 3. Enforcement clauses: a count, and (optionally) named witnesses.
    if len(valid) < config["minimumSightings"]:
        return _unavailable(
            "%d attributed sightings for this series; the configuration requires %d"
            % (len(valid), config["minimumSightings"]), **counts)
    missing = [k for k in config["requiredWitnesses"] if k not in attributed_keys]
    if missing:
        return _fail("witness-required-absent",
                     "%d required witness(es) contributed no verifying record — "
                     "indistinguishable from a witness that never spoke" % len(missing),
                     **counts)

    # 4. Comparison over ALL valid sightings; registered precedence decides the
    # code, so the unsigned retained order cannot (R1-11).
    if not valid:
        return result("pass", None,
                      "no comparison performed: zero attributed sightings",
                      comparisonPerformed=False, **counts)
    digests = _snapshot_digests(snapshot_bytes) if _is_bytes(snapshot_bytes) else None
    if digests is None:
        return _unavailable("the presented snapshot is unusable for comparison", **counts)

    findings = {}
    for sighting in valid:
        position = sighting["position"]
        if position > len(digests):
            if config["recencyPolicy"] == "refuse-behind":
                findings.setdefault(
                    "snapshot-behind-witnessed-head",
                    "an attributed witness records position %d; the presented history "
                    "ends at %d. Under recencyPolicy=refuse-behind this is refused; the "
                    "sighting carries no proof that its history extends this one, so a "
                    "deliberate audit of an older snapshot refuses identically"
                    % (position, len(digests)))
            continue
        if digests[position - 1] != sighting["head"]:
            findings.setdefault(
                "snapshot-conflicts-with-witnessed-head",
                "an attributed witness records a different head at position %d — the "
                "presented history is not the one that witness recorded" % position)
    for code in PRECEDENCE:
        if code in findings:
            return _fail(code, findings[code], comparisonPerformed=True, **counts)
    return result("pass", None,
                  "consistent with %d attributed sighting(s); %d unattributed record(s) "
                  "ignored" % (len(valid), unattributed),
                  comparisonPerformed=True, **counts)
