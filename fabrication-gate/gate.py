"""Receipt-required admission gate (ADR-0002 item 3): the capstone that wires
the attestation core (item 1) and the portable derivation rule (item 2) into
layer 5, admission.

The gate's one job is to make the facts and evidence a pack evaluates be
*exactly* the derivation over the bytes a named authority attested for the
acquisition -- and nothing a caller supplies. That closes the one failure mode
studies 005-007 saw a model reach a wrong DECISION through rather than a
rejected envelope: `not_found` acquired, then a fabricated `matchCount: "0"`
authored into the facts. Under this gate the model cannot author the fact
(the derivation is mechanical), cannot tamper the retained bytes (attestation
catches it), and cannot forge a receipt (no key), so the fabricated fact has no
path to evaluation.

It guarantees byte-lineage, not truth: an admitted fact derives from bytes the
authority attested, not that those bytes are correct.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "acquisition-proxy"))
sys.path.insert(0, os.path.join(_HERE, "..", "derivation-rule"))

import attest   # item 1: attestation store + verify
import derive   # item 2: portable derivation rule


class GateError(Exception):
    """The acquisition is not admissible: the store does not verify, the named
    acquisition is missing, or its artifact is not the attested bytes."""


def _receipt(store_root, session_id, call_index):
    path = os.path.join(store_root, "receipts", session_id, "%d.json" % call_index)
    if not os.path.exists(path):
        raise GateError("no attested acquisition at %s/%d" % (session_id, call_index))
    with open(path, "rb") as handle:
        return json.loads(handle.read())


def _artifact_bytes(store_root, result_digest):
    path = os.path.join(store_root, "artifacts", result_digest.split(":", 1)[1])
    if not os.path.exists(path):
        raise GateError("attested artifact missing for %s" % result_digest)
    with open(path, "rb") as handle:
        return handle.read()


def admit(store_root, key, session_id, call_index, rule, params, expected_authority=None):
    """Return the derived claim that may reach evaluation for one attested
    acquisition, or raise GateError. The returned claim's facts, evidence
    availability, and acquisition status ARE the evaluator's input -- a caller
    supplies nothing.

    The gate verifies the whole attestation store first (HMAC over every
    receipt, each artifact re-digested, the per-session chain), so a tampered or
    forged store is refused before any derivation. It then applies the
    derivation rule (item 2) to the exact attested bytes."""
    ok, findings = attest.verify(store_root, key, expected_authority)
    if not ok:
        raise GateError("attestation store does not verify: %r" % findings)
    receipt = _receipt(store_root, session_id, call_index)
    artifact = json.loads(_artifact_bytes(store_root, receipt["resultDigest"]).decode("utf-8"))
    claim = derive.derive(rule, artifact, params)
    return {
        "facts": claim["facts"],
        "evidenceAvailability": claim["evidenceAvailability"],
        "acquisitionStatus": claim["acquisitionStatus"],
        "reason": claim["reason"],
        "lineage": {
            "sessionId": receipt["sessionId"],
            "callIndex": receipt["callIndex"],
            "authority": receipt["authority"],
            "resultDigest": receipt["resultDigest"],
            "basis": claim["basis"],
        },
    }
