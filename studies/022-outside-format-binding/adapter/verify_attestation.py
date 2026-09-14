"""The in-toto layer's verification ceremony (adapter/SPEC.md section 5).

For every receipt the store holds, the layer expects one attestation and holds it, in this
order, to: (1) presence; (2) the DSSE payload type; (3) a signature by the pinned adapter key
-- the signature's key id must be the pinned one (`fail:untrusted-key`) and the reference
implementation must verify it (`fail:signature`); (4) the Statement's `_type` and the
registered predicate type; (5) the Statement's validity by the in-toto-attestation bindings;
(6) each subject re-digested against what it names -- the artifact under the store, the
decision record among the candidates the gateway's rule enumerates under the record
directory, a cited receipt's file -- `match`, `mismatch` or `missing`. The layer passes when
every attestation passes every step and every subject matches. It reads no gateway key and
runs no gateway code: what it can see is what an in-toto consumer can see.

Run: python adapter/verify_attestation.py STORE_DIR ATTESTATIONS_DIR DECISIONS_DIR
"""
import hashlib
import json
import sys
from pathlib import Path

from securesystemslib.dsse import Envelope
from securesystemslib.signer import SSlibKey
from in_toto_attestation.v1.resource_descriptor import ResourceDescriptor
from in_toto_attestation.v1.statement import Statement

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://judgment-pack.dev/attestation/gateway-receipt/v3"
PAYLOAD_TYPE = "application/vnd.in-toto+json"


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def record_candidates(decisions):
    """Every candidate the gateway's rule enumerates (SPEC.md section 4 step 6): each regular file whole, and for a .jsonl file additionally each line."""
    digests = set()
    root = Path(decisions)
    if not root.exists():
        return digests
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        data = p.read_bytes()
        digests.add(sha256_hex(data))
        if p.name.endswith(".jsonl"):
            for piece in data.split(b"\n"):
                piece = piece[:-1] if piece.endswith(b"\r") else piece
                if piece:
                    digests.add(sha256_hex(piece))
    return digests


def check_subject(subject, store, decisions):
    name, digest = subject.get("name"), subject.get("digest", {}).get("sha256")
    if name == "artifact":
        path = Path(store) / "artifacts" / str(digest)
        if not path.is_file():
            return "missing"
        return "match" if sha256_hex(path.read_bytes()) == digest else "mismatch"
    if name == "decision-record":
        return "match" if digest in record_candidates(decisions) else "missing"
    if isinstance(name, str) and name.startswith("cites/"):
        _, session, index = name.split("/", 2)
        path = Path(store) / "receipts" / session / (index + ".json")
        if not path.is_file():
            return "missing"
        return "match" if sha256_hex(path.read_bytes()) == digest else "mismatch"
    return "unknown-subject"


def verify_one(envelope_path, pubkey, store, decisions):
    out = {"attestation": str(envelope_path.name), "dsse": None, "statement": None, "subjects": {}}
    try:
        raw = json.loads(envelope_path.read_text())
        env = Envelope.from_dict(raw)
    except Exception as e:  # noqa: BLE001 -- the layer reports, it does not crash
        out["dsse"] = "fail:unparseable"
        return out
    if env.payload_type != PAYLOAD_TYPE:
        out["dsse"] = "fail:payload-type"
        return out
    if pubkey.keyid not in env.signatures:
        out["dsse"] = "fail:untrusted-key"
        return out
    try:
        env.verify([pubkey], 1)
    except Exception:  # noqa: BLE001
        out["dsse"] = "fail:signature"
        return out
    out["dsse"] = "pass"
    try:
        statement = json.loads(env.payload)
    except ValueError:
        out["statement"] = "invalid:not-json"
        return out
    if statement.get("_type") != STATEMENT_TYPE:
        out["statement"] = "invalid:statement-type"
        return out
    if statement.get("predicateType") != PREDICATE_TYPE:
        out["statement"] = "invalid:predicate-type"
        return out
    try:
        Statement([ResourceDescriptor(name=s["name"], digest=s["digest"]).pb for s in statement.get("subject", [])],
                  statement["predicateType"], statement.get("predicate")).validate()
    except Exception:  # noqa: BLE001
        out["statement"] = "invalid:bindings"
        return out
    out["statement"] = "valid"
    for s in statement.get("subject", []):
        out["subjects"][s.get("name")] = check_subject(s, store, decisions)
    return out


def verify(store, attestations, decisions):
    attestations = Path(attestations)
    public = json.loads((attestations / "adapter.pubkey.json").read_text())
    pubkey = SSlibKey.from_dict(public["keyid"], {k: v for k, v in public.items() if k != "keyid"})
    results = []
    receipts = Path(store) / "receipts"
    for session in sorted(p for p in receipts.iterdir() if p.is_dir()):
        for f in sorted(session.glob("*.json"), key=lambda p: int(p.stem)):
            env_path = attestations / session.name / (f.stem + ".dsse.json")
            if not env_path.is_file():
                results.append({"attestation": "%s/%s.dsse.json" % (session.name, f.stem), "dsse": "fail:missing-attestation", "statement": None, "subjects": {}})
                continue
            r = verify_one(env_path, pubkey, store, decisions)
            r["attestation"] = "%s/%s" % (session.name, r["attestation"])
            results.append(r)
    passed = all(r["dsse"] == "pass" and r["statement"] == "valid" and r["subjects"] and all(v == "match" for v in r["subjects"].values()) for r in results)
    return {"pass": passed, "attestations": results}


if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1], sys.argv[2], sys.argv[3]), indent=1))
