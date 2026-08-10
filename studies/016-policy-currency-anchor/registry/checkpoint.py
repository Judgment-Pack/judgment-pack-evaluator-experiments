"""Deterministic writer for the study's pack-version currency registry.

This is the study's prototype of RFC 0011 section 1: an append-only, hash-chained,
independently signed log of add/retire/reinstate lifecycle events over a pack
series, plus a signed head attestation over any prefix ("snapshot"). It is a
study registration, not a format proposal: nothing here lands in JPS, the
runtime, or the gateway, and the registered schema binds this study only
(registry/SPEC.md section 1).

Build-path only. The verification path (`registry/verify_currency.py`) shares
the canonicalization helpers below but recomputes every digest and signature
from the snapshot bytes themselves; it never trusts a writer-supplied value.

Determinism: authority keys derive from fixed seeds, `effectiveFrom` values are
caller-supplied constants, and JCS (RFC 8785, the `rfc8785` package — the same
canonicalization OWP signs over and JPS Core section 8.3 defines for
dispositions) decides every signed byte. Building twice yields identical bytes.
"""

import base64
import hashlib
import json

import rfc8785
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DOMAIN_CHECKPOINT = "jps-study016-currency/checkpoint/1"
DOMAIN_SNAPSHOT = "jps-study016-currency/snapshot/1"

EVENTS = ("add", "retire", "reinstate")

CHECKPOINT_FIELDS = (
    "checkpointVersion",
    "sequence",
    "seriesId",
    "event",
    "packVersion",
    "packDigest",
    "effectiveFrom",
    "previousCheckpointDigest",
)


class RegistryBuildError(RuntimeError):
    """A registry history could not be constructed as specified."""


def canonical_bytes(domain, payload):
    """The signed bytes: JCS over a domain-separated envelope, OWP style."""
    return rfc8785.dumps({"domain": domain, "payload": payload})


def sha256_prefixed(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# authority keys (study-minted, fixed seeds — a trust root, stated as such)
# --------------------------------------------------------------------------

def private_key(seed_label):
    seed = hashlib.sha256(seed_label.encode("utf-8")).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key_b64(key):
    raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")


def key_id(key):
    raw = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return "ed25519:" + hashlib.sha256(raw).hexdigest()


AUTHORITY_SEED = "study-016/currency-authority/1"
FOREIGN_SEED = "study-016/foreign-authority/1"


# --------------------------------------------------------------------------
# checkpoints and snapshots
# --------------------------------------------------------------------------

def build_checkpoint(key, *, sequence, series_id, event, pack_version,
                     pack_digest=None, effective_from, previous):
    """One signed lifecycle event, hash-chained to its predecessor."""
    if event not in EVENTS:
        raise RegistryBuildError("unknown event: %r" % (event,))
    if (event == "add") != (pack_digest is not None):
        raise RegistryBuildError(
            "packDigest is carried exactly on add events (event %r)" % (event,)
        )
    payload = {
        "checkpointVersion": "1",
        "sequence": sequence,
        "seriesId": series_id,
        "event": event,
        "packVersion": pack_version,
        "effectiveFrom": effective_from,
        "previousCheckpointDigest": previous,
    }
    if pack_digest is not None:
        payload["packDigest"] = pack_digest
    signed = canonical_bytes(DOMAIN_CHECKPOINT, payload)
    return {
        "checkpoint": payload,
        "checkpointDigest": sha256_prefixed(signed),
        "authorityKeyId": key_id(key),
        "signature": base64.b64encode(key.sign(signed)).decode("ascii"),
    }


def build_registry(key, events):
    """A whole history from `(event, seriesId, version[, digest[, effectiveFrom]])` dicts."""
    records = []
    previous = None
    for index, entry in enumerate(events, start=1):
        record = build_checkpoint(
            key,
            sequence=index,
            series_id=entry["seriesId"],
            event=entry["event"],
            pack_version=entry["packVersion"],
            pack_digest=entry.get("packDigest"),
            effective_from=entry.get("effectiveFrom", "2026-01-01T00:00:00Z"),
            previous=previous,
        )
        records.append(record)
        previous = record["checkpointDigest"]
    return records


def snapshot_of(key, records, position=None):
    """A signed snapshot over the first `position` checkpoints (default: all)."""
    if position is None:
        position = len(records)
    if not 1 <= position <= len(records):
        raise RegistryBuildError("snapshot position %r out of range" % (position,))
    prefix = records[:position]
    head = prefix[-1]["checkpointDigest"]
    payload = {"snapshotVersion": "1", "head": head, "position": position}
    signed = canonical_bytes(DOMAIN_SNAPSHOT, payload)
    return {
        "snapshotVersion": "1",
        "checkpoints": prefix,
        "attestation": {
            "payload": payload,
            "authorityKeyId": key_id(key),
            "signature": base64.b64encode(key.sign(signed)).decode("ascii"),
        },
    }


def snapshot_bytes(snapshot):
    return json.dumps(snapshot, indent=2, ensure_ascii=False).encode("utf-8")


def trustconfig_bytes(*, authority_public_key, genesis_head,
                      persisted_minimum_head=None):
    """The verifier's out-of-band pins, as retained cell bytes."""
    document = {
        "trustConfigVersion": "1",
        "authorityPublicKey": authority_public_key,
        "genesisHead": genesis_head,
        "persistedMinimumHead": persisted_minimum_head,
    }
    return json.dumps(document, indent=2, ensure_ascii=False).encode("utf-8")
