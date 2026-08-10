"""Deterministic writer for witness sightings. Build path only.

A sighting is a witness key's signature over `{seriesId, head, position}` —
the study's prototype of one clause of RFC 0011 Unresolved #9's witness
contract. The verifier (`witness/verify_witness.py`) never imports this
module and recomputes everything from bytes.
"""

import base64
import json

import rfc8785

DOMAIN_SIGHTING = "jps-study017-witness/sighting/1"

AUTHORITY_SEED = "study-017/currency-authority/1"
WITNESS_1_SEED = "study-017/witness-1/1"       # the colluding role in the matrix
WITNESS_2_SEED = "study-017/witness-2/1"       # the honest role
WITNESS_3_SEED = "study-017/witness-unpinned/1"  # never pinned by any cell


def build_sighting(key, key_id, *, series_id, head, position):
    payload = {
        "sightingVersion": "1",
        "seriesId": series_id,
        "head": head,
        "position": position,
    }
    signed = rfc8785.dumps({"domain": DOMAIN_SIGHTING, "payload": payload})
    return {
        "sighting": payload,
        "witnessKeyId": key_id,
        "signature": base64.b64encode(key.sign(signed)).decode("ascii"),
    }


def sightings_bytes(records):
    return json.dumps(
        {"sightingsVersion": "1", "sightings": records},
        indent=2, ensure_ascii=False,
    ).encode("utf-8")


def witnessconfig_bytes(*, series_id, witness_keys, minimum_sightings):
    return json.dumps(
        {
            "witnessConfigVersion": "1",
            "seriesId": series_id,
            "witnessKeys": witness_keys,
            "minimumSightings": minimum_sightings,
        },
        indent=2, ensure_ascii=False,
    ).encode("utf-8")
