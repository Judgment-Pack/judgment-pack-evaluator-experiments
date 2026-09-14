"""The in-toto layer's verification ceremony (adapter/SPEC.md section 5).

A study-written consumer ceremony using unmodified DSSE verification and unmodified Statement
validation. For every receipt the store holds, the layer expects one attestation and holds it,
in this order, to: (1) presence [consumer]; (2) the envelope parses [upstream] and its payload
type is the in-toto one [consumer]; (3) a signature under the pinned adapter key's id is
present [consumer selection] -- the key is handed in from the study's fixture, never read from
the cell -- and the reference implementation verifies it [upstream]; (4) the payload is a JSON
object of the pinned Statement type and predicate type [consumer], converted by the pinned
protobuf JSON mapping and validated by the in-toto-attestation bindings [upstream]; (5) each
subject re-digested against what it names [consumer] -- `match`, `mismatch`, `missing`, or
`unknown-subject` for a name or digest the ceremony does not recognise -- every outcome
retained in the statement's order. The layer passes when every attestation passes every step
and every subject matches. It reads no gateway key and runs no gateway code.

Run: python adapter/verify_attestation.py STORE_DIR ATTESTATIONS_DIR DECISIONS_DIR TRUSTED_PUBKEY_JSON
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from google.protobuf import json_format
from securesystemslib.dsse import Envelope
from securesystemslib.signer import SSlibKey
import in_toto_attestation.v1.statement_pb2 as statement_pb2
from in_toto_attestation.v1.statement import Statement

sys.path.insert(0, str(Path(__file__).resolve().parent))
from storewalk import presence, stored_receipts  # noqa: E402

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://judgment-pack.dev/attestation/gateway-receipt/v3"
PAYLOAD_TYPE = "application/vnd.in-toto+json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

DSSE_CODES = ("pass", "fail:missing-attestation", "fail:unparseable", "fail:payload-type", "fail:untrusted-key", "fail:signature")
STATEMENT_CODES = ("valid", "invalid:not-json", "invalid:not-object", "invalid:statement-type", "invalid:predicate-type", "invalid:bindings")
SUBJECT_OUTCOMES = ("match", "mismatch", "missing", "unknown-subject")


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
    """Step 5 for one subject: the shape is checked before any path is formed from it."""
    if not isinstance(subject, dict) or not isinstance(subject.get("digest"), dict):
        return "unknown-subject"
    name, digest = subject.get("name"), subject["digest"].get("sha256")
    if not isinstance(name, str) or not isinstance(digest, str) or not HEX64.fullmatch(digest):
        return "unknown-subject"
    if name == "artifact":
        path = Path(store) / "artifacts" / digest
        if not path.is_file():
            return "missing"
        return "match" if sha256_hex(path.read_bytes()) == digest else "mismatch"
    if name == "decision-record":
        return "match" if digest in record_candidates(decisions) else "missing"
    if name.startswith("cites/"):
        parts = name.split("/")
        if len(parts) != 3 or not parts[1] or not parts[2].isdigit():
            return "unknown-subject"
        _, session, index = parts
        path = Path(store) / "receipts" / session / (index + ".json")
        if not path.is_file():
            return "missing"
        return "match" if sha256_hex(path.read_bytes()) == digest else "mismatch"
    return "unknown-subject"


def validate_statement(statement):
    """Step 4's upstream part: the Statement as supplied, converted by the pinned protobuf JSON mapping (an unknown
    or mistyped member is refused by the mapping) and validated by the bindings' own rule."""
    pb = statement_pb2.Statement()
    json_format.ParseDict(statement, pb)
    Statement.copy_from_pb(pb).validate()


def verify_one(envelope_path, pubkey, store, decisions):
    out = {"attestation": str(envelope_path.name), "dsse": None, "statement": None, "subjects": []}
    raw_bytes = envelope_path.read_bytes()  # an I/O failure is not an outcome: it propagates and the observation aborts
    try:
        env = Envelope.from_dict(json.loads(raw_bytes.decode("utf-8")))
    except Exception:  # noqa: BLE001 -- the layer reports, it does not crash
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
    if not isinstance(statement, dict):
        out["statement"] = "invalid:not-object"
        return out
    if statement.get("_type") != STATEMENT_TYPE:
        out["statement"] = "invalid:statement-type"
        return out
    if statement.get("predicateType") != PREDICATE_TYPE:
        out["statement"] = "invalid:predicate-type"
        return out
    try:
        validate_statement(statement)
    except Exception:  # noqa: BLE001 -- the mapping's or the bindings' refusal
        out["statement"] = "invalid:bindings"
        return out
    out["statement"] = "valid"
    # every descriptor is checked and retained in order: a later descriptor with the same
    # name cannot erase an earlier failure (the reduced form keeps the first non-match)
    for s in statement["subject"]:
        out["subjects"].append([s.get("name") if isinstance(s.get("name"), str) else None, check_subject(s, store, decisions)])
    return out


def per_name(subjects):
    """The per-name outcome: the first outcome that is not `match` for that name, else `match`."""
    out = {}
    for name, outcome in subjects:
        if name not in out or (out[name] == "match" and outcome != "match"):
            out[name] = outcome
    return out


def attestation_passes(r):
    return r["dsse"] == "pass" and r["statement"] == "valid" and bool(r["subjects"]) and all(o == "match" for _, o in r["subjects"])


def trusted_key(path):
    """The pinned adapter public key, read from the study's fixture -- never from a cell."""
    public = json.loads(Path(path).read_text())
    return SSlibKey.from_dict(public["keyid"], {k: v for k, v in public.items() if k != "keyid"})


def verify(store, attestations, decisions, pubkey):
    results = []
    for session, stem, _ in stored_receipts(store):
        env_path = Path(attestations) / session / (stem + ".dsse.json")
        name = "%s/%s.dsse.json" % (session, stem)
        if presence(env_path) == "absent":
            results.append({"attestation": name, "dsse": "fail:missing-attestation", "statement": None, "subjects": []})
            continue
        r = verify_one(env_path, pubkey, store, decisions)
        r["attestation"] = name
        results.append(r)
    return {"pass": all(attestation_passes(r) for r in results), "attestations": results}


if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1], sys.argv[2], sys.argv[3], trusted_key(sys.argv[4])), indent=1))
