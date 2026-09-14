"""Bind a gateway store into in-toto attestations: one Statement per receipt, in a DSSE envelope.

The binding (adapter/SPEC.md): for every receipt in the store an in-toto Statement v1 whose
subjects are the things the receipt's own verifier resolves by digest -- the retained artifact
(`resultDigest`), and for an action receipt the decision record it claims (`recordDigest`) and
each receipt it cites (the cited receipt file's bytes) -- whose predicate type is the study's
registered URI and whose predicate is the receipt itself, verbatim as stored. The Statement is
serialized deterministically (sorted keys, no whitespace) and signed as a DSSE envelope with the
adapter's Ed25519 key. The adapter modifies neither the store nor the receipt: it composes.

The adapter key is derived from a fixed seed, so the binding of a given store is deterministic;
it is a study key, not a secret, and it is not the gateway's key -- the two trust roots stay
apart, which is part of what the study measures.

Run: python adapter/bind.py STORE_DIR OUT_DIR
"""
import hashlib
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from securesystemslib.dsse import Envelope
from securesystemslib.signer import CryptoSigner, SSlibKey

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://judgment-pack.dev/attestation/gateway-receipt/v3"
PAYLOAD_TYPE = "application/vnd.in-toto+json"
ADAPTER_KEY_SEED = hashlib.sha256(b"judgment-pack study 022 adapter key").digest()


def adapter_signer(seed=ADAPTER_KEY_SEED):
    private = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    public = SSlibKey.from_crypto(private.public_key())
    return CryptoSigner(private, public)


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def subjects_for(receipt, store):
    subjects = [{"name": "artifact", "digest": {"sha256": receipt["resultDigest"].split(":", 1)[1]}}]
    if receipt.get("kind") == "action":
        action = receipt["action"]
        subjects.append({"name": "decision-record", "digest": {"sha256": action["decision"]["recordDigest"].split(":", 1)[1]}})
        for c in action["cites"]:
            path = Path(store) / "receipts" / c["sessionId"] / ("%d.json" % c["callIndex"])
            subjects.append({"name": "cites/%s/%d" % (c["sessionId"], c["callIndex"]), "digest": {"sha256": sha256_hex(path.read_bytes())}})
    return subjects


def statement_for(receipt, store):
    return {"_type": STATEMENT_TYPE, "subject": subjects_for(receipt, store), "predicateType": PREDICATE_TYPE, "predicate": receipt}


def serialize(statement):
    return json.dumps(statement, sort_keys=True, separators=(",", ":")).encode()


def bind(store, out, signer=None):
    signer = signer or adapter_signer()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    public = dict(signer.public_key.to_dict(), keyid=signer.public_key.keyid)
    (out / "adapter.pubkey.json").write_text(json.dumps(public, sort_keys=True, indent=1) + "\n")
    receipts = Path(store) / "receipts"
    written = []
    for session in sorted(p for p in receipts.iterdir() if p.is_dir()):
        for f in sorted(session.glob("*.json"), key=lambda p: int(p.stem)):
            receipt = json.loads(f.read_text())
            env = Envelope(serialize(statement_for(receipt, store)), PAYLOAD_TYPE, {})
            env.sign(signer)
            target = out / session.name / (f.stem + ".dsse.json")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(env.to_dict(), sort_keys=True, indent=1) + "\n")
            written.append(str(target.relative_to(out)))
    return written


if __name__ == "__main__":
    print("\n".join(bind(sys.argv[1], sys.argv[2])))
