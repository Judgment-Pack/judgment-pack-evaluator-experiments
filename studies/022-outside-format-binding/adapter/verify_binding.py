"""The binding layer: what the binding itself asserts, checked against the statement and the store.

The in-toto layer verifies an attestation as any in-toto consumer would; it does not know
what a gateway receipt is. The binding layer holds the attestation to the binding's own rule
(adapter/SPEC.md section 3): the predicate is exactly the receipt the store holds, byte for
byte; the artifact subject's digest is the predicate's `resultDigest`; for an action, the
decision-record subject's digest is the predicate's `decision.recordDigest`, and there is
exactly one `cites/<session>/<index>` subject per citation in the predicate and no other;
and every subject the statement carries is one of those. It reads the store's receipt files
only to compare bytes; it verifies no signature and resolves no citation -- those are the
other two layers'.

Outcomes per attestation: `pass`, or `fail:<code>` for the first rule broken:
`predicate-differs-from-store`, `artifact-subject-mismatch`, `decision-subject-mismatch`,
`cites-subject-set`, `foreign-subject`, `missing-attestation`, `unreadable`.

Run: python adapter/verify_binding.py STORE_DIR ATTESTATIONS_DIR
"""
import json
import sys
from pathlib import Path

from securesystemslib.dsse import Envelope


def canonical_receipt_bytes(doc):
    """The store keeps receipts as the gateway wrote them; the binding compares documents, not whitespace."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def check_one(envelope_path, receipt_path):
    try:
        env = Envelope.from_dict(json.loads(envelope_path.read_text()))
        statement = json.loads(env.payload)
        stored = json.loads(receipt_path.read_text())
    except Exception:  # noqa: BLE001
        return "fail:unreadable"
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict) or canonical_receipt_bytes(predicate) != canonical_receipt_bytes(stored):
        return "fail:predicate-differs-from-store"
    subjects = {s.get("name"): s.get("digest", {}).get("sha256") for s in statement.get("subject", [])}
    if subjects.get("artifact") != str(predicate.get("resultDigest", "")).split(":", 1)[-1]:
        return "fail:artifact-subject-mismatch"
    expected = {"artifact"}
    if predicate.get("kind") == "action":
        action = predicate.get("action", {})
        if subjects.get("decision-record") != str(action.get("decision", {}).get("recordDigest", "")).split(":", 1)[-1]:
            return "fail:decision-subject-mismatch"
        expected.add("decision-record")
        cited = {"cites/%s/%s" % (c.get("sessionId"), c.get("callIndex")) for c in action.get("cites", [])}
        if {n for n in subjects if isinstance(n, str) and n.startswith("cites/")} != cited:
            return "fail:cites-subject-set"
        expected |= cited
    if set(subjects) != expected:
        return "fail:foreign-subject"
    return "pass"


def verify(store, attestations):
    results = []
    receipts = Path(store) / "receipts"
    for session in sorted(p for p in receipts.iterdir() if p.is_dir()):
        for f in sorted(session.glob("*.json"), key=lambda p: int(p.stem)):
            env_path = Path(attestations) / session.name / (f.stem + ".dsse.json")
            name = "%s/%s.dsse.json" % (session.name, f.stem)
            results.append({"attestation": name, "binding": check_one(env_path, f) if env_path.is_file() else "fail:missing-attestation"})
    return {"pass": all(r["binding"] == "pass" for r in results), "attestations": results}


if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1], sys.argv[2]), indent=1))
