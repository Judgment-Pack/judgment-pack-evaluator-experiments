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


CODES = ("pass", "fail:missing-attestation", "fail:unreadable", "fail:predicate-differs-from-store", "fail:artifact-subject-mismatch",
         "fail:decision-subject-mismatch", "fail:cites-subject-set", "fail:foreign-subject")


def check_one(envelope_path, receipt_path):
    envelope_bytes, receipt_bytes = envelope_path.read_bytes(), receipt_path.read_bytes()  # an I/O failure propagates: it is not an outcome
    try:
        env = Envelope.from_dict(json.loads(envelope_bytes.decode("utf-8")))
        statement = json.loads(env.payload)
        stored = json.loads(receipt_bytes.decode("utf-8"))
        if not isinstance(statement, dict) or not isinstance(statement.get("subject"), list) or not isinstance(stored, dict):
            return "fail:unreadable"
        names = []
        for s in statement["subject"]:
            if not isinstance(s, dict) or not isinstance(s.get("name"), str) or not isinstance(s.get("digest"), dict) or not isinstance(s["digest"].get("sha256"), str):
                return "fail:unreadable"
            names.append((s["name"], s["digest"]["sha256"]))
    except Exception:  # noqa: BLE001
        return "fail:unreadable"
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict) or canonical_receipt_bytes(predicate) != canonical_receipt_bytes(stored):
        return "fail:predicate-differs-from-store"
    by_name = {}
    for name, digest in names:
        by_name.setdefault(name, []).append(digest)
    if by_name.get("artifact") != [str(predicate.get("resultDigest", "")).split(":", 1)[-1]]:
        return "fail:artifact-subject-mismatch"
    expected = {"artifact"}
    if predicate.get("kind") == "action":
        action = predicate.get("action", {}) if isinstance(predicate.get("action"), dict) else {}
        if by_name.get("decision-record") != [str((action.get("decision") or {}).get("recordDigest", "")).split(":", 1)[-1]]:
            return "fail:decision-subject-mismatch"
        expected.add("decision-record")
        cited = ["cites/%s/%s" % (c.get("sessionId"), c.get("callIndex")) for c in (action.get("cites") or [])]
        present = [n for n, _ in names if n.startswith("cites/")]
        # exactly one subject per citation, named by it: multiplicity counts, not only the set of names
        if sorted(present) != sorted(cited):
            return "fail:cites-subject-set"
        expected |= set(cited)
    if [n for n, _ in names] and sorted(n for n, _ in names) != sorted(expected):
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
