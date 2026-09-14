"""The binding layer: what the binding itself asserts, checked against the statement and the store.

The in-toto layer verifies an attestation as any in-toto consumer would; it does not know
what a gateway receipt is. The binding layer holds the attestation to the binding's own rule
(adapter/SPEC.md section 3): the predicate is exactly the receipt the store holds, byte for
byte; the artifact subject's digest is the predicate's `resultDigest`; for an action, the
decision-record subject's digest is the predicate's `decision.recordDigest`, and there is
exactly one `cites/<session>/<index>` subject per citation in the predicate, by multiplicity;
and every subject the statement carries is one of those names. It reads the store's receipt
files only to compare bytes; it verifies no signature and resolves no citation -- those are
the other two layers'.

Outcomes per attestation (section 3a, in precedence order): `pass`, or the first of
`fail:missing-attestation`, `fail:unreadable`, `fail:predicate-differs-from-store`,
`fail:artifact-subject-mismatch`, `fail:decision-subject-mismatch`, `fail:cites-subject-set`,
`fail:foreign-subject`. An I/O failure, or a path that is present but not a plain file, is
not an outcome: it propagates (the validity channel).

Run: python adapter/verify_binding.py STORE_DIR ATTESTATIONS_DIR
"""
import json
import re
import sys
from pathlib import Path

from securesystemslib.dsse import Envelope

sys.path.insert(0, str(Path(__file__).resolve().parent))
from storewalk import presence, stored_receipts  # noqa: E402

HEX64 = re.compile(r"^[0-9a-f]{64}$")
CODES = ("pass", "fail:missing-attestation", "fail:unreadable", "fail:predicate-differs-from-store", "fail:artifact-subject-mismatch",
         "fail:decision-subject-mismatch", "fail:cites-subject-set", "fail:foreign-subject")


def canonical_receipt_bytes(doc):
    """The store keeps receipts as the gateway wrote them; the binding compares documents, not whitespace."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_after_prefix(value):
    """The hex of a `sha256:<hex>` string, or None when the value is not of that shape."""
    if not isinstance(value, str) or not value.startswith("sha256:") or not HEX64.match(value[7:]):
        return None
    return value[7:]


def check_one(envelope_path, receipt_path):
    envelope_bytes, receipt_bytes = envelope_path.read_bytes(), receipt_path.read_bytes()  # an I/O failure propagates: it is not an outcome
    try:
        env = Envelope.from_dict(json.loads(envelope_bytes.decode("utf-8")))
        statement = json.loads(env.payload)
        stored = json.loads(receipt_bytes.decode("utf-8"))
    except Exception:  # noqa: BLE001 -- not parseable is one outcome
        return "fail:unreadable"
    # every shape is checked before any member is read (section 3a item 2)
    if not isinstance(statement, dict) or not isinstance(statement.get("subject"), list) or not isinstance(stored, dict):
        return "fail:unreadable"
    names = []
    for s in statement["subject"]:
        if not isinstance(s, dict) or not isinstance(s.get("name"), str) or not isinstance(s.get("digest"), dict) \
                or not isinstance(s["digest"].get("sha256"), str) or not HEX64.match(s["digest"]["sha256"]):
            return "fail:unreadable"
        names.append((s["name"], s["digest"]["sha256"]))
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        return "fail:unreadable"
    is_action = predicate.get("kind") == "action"
    action = predicate.get("action")
    if is_action:
        if not isinstance(action, dict) or not isinstance(action.get("decision"), dict) or not isinstance(action.get("cites"), list) \
                or not all(isinstance(c, dict) and isinstance(c.get("sessionId"), str) and isinstance(c.get("callIndex"), int)
                           and not isinstance(c.get("callIndex"), bool) for c in action["cites"]):
            return "fail:unreadable"
    # rule 1: the predicate is the stored receipt, as a document
    if canonical_receipt_bytes(predicate) != canonical_receipt_bytes(stored):
        return "fail:predicate-differs-from-store"
    by_name = {}
    for name, digest in names:
        by_name.setdefault(name, []).append(digest)
    # rule 2: exactly one artifact subject, the predicate's resultDigest
    if by_name.get("artifact") != [digest_after_prefix(predicate.get("resultDigest"))]:
        return "fail:artifact-subject-mismatch"
    allowed = {"artifact"}
    if is_action:
        # rule 3: exactly one decision-record subject, the predicate's recordDigest
        if by_name.get("decision-record") != [digest_after_prefix(action["decision"].get("recordDigest"))]:
            return "fail:decision-subject-mismatch"
        allowed.add("decision-record")
        # rule 3: the citation subjects are exactly one per citation entry, by multiplicity
        cited = ["cites/%s/%d" % (c["sessionId"], c["callIndex"]) for c in action["cites"]]
        present = [n for n, _ in names if n.startswith("cites/")]
        if sorted(present) != sorted(cited):
            return "fail:cites-subject-set"
        allowed |= set(cited)
    # rule 4: no subject under any other name (multiplicities were settled above)
    if any(n not in allowed for n, _ in names):
        return "fail:foreign-subject"
    return "pass"


def verify(store, attestations):
    results = []
    for session, stem, receipt_path in stored_receipts(store):
        env_path = Path(attestations) / session / (stem + ".dsse.json")
        name = "%s/%s.dsse.json" % (session, stem)
        code = "fail:missing-attestation" if presence(env_path) == "absent" else check_one(env_path, receipt_path)
        results.append({"attestation": name, "binding": code})
    return {"pass": all(r["binding"] == "pass" for r in results), "attestations": results}


if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1], sys.argv[2]), indent=1))
