"""The registered constructions: each cell is the baseline with one stated edit.

A cell is built from the committed baseline (store, registry, decision records, and the
attestations the adapter binds from the baseline store) by exactly one construction named
here, deterministically. The constructions are the registered threat model's rows: what a
party who can reach the store, the book, or the attestations -- with or without the
adapter's key -- can do, and what each layer then sees.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "adapter"))
import bind  # noqa: E402

BASELINE = HERE.parent / "fixtures" / "baseline"


def read_json(p):
    return json.loads(Path(p).read_text())


def write_json(p, doc):
    Path(p).write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n")


def receipt_path(cell, index):
    return cell / "store" / "receipts" / "s2" / ("%d.json" % index)


def envelope_path(cell, index):
    return cell / "attestations" / "s2" / ("%d.dsse.json" % index)


def resign(cell, index, statement, signer=None):
    """Rebuild an attestation validly from a (possibly altered) statement, with the adapter's key unless another is given."""
    from securesystemslib.dsse import Envelope
    env = Envelope(bind.serialize(statement), bind.PAYLOAD_TYPE, {})
    env.sign(signer or bind.adapter_signer())
    envelope_path(cell, index).write_text(json.dumps(env.to_dict(), sort_keys=True, indent=1) + "\n")


def statement_of(cell, index):
    from securesystemslib.dsse import Envelope
    env = Envelope.from_dict(read_json(envelope_path(cell, index)))
    return json.loads(env.payload)


def edit_receipt_in_store(cell, index, member_path, value):
    """Edit a signed member of a stored receipt (the bytes the gateway signed), leaving the attestation as bound."""
    p = receipt_path(cell, index)
    doc = json.loads(p.read_text())
    node = doc
    for k in member_path[:-1]:
        node = node[k]
    node[member_path[-1]] = value
    p.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":")))


# --- constructions -----------------------------------------------------------

def pos_baseline(cell):
    pass


def a01_artifact_edited(cell):
    """The action's retained response bytes are changed in the store."""
    receipt = read_json(receipt_path(cell, 1))
    digest = receipt["resultDigest"].split(":", 1)[1]
    p = cell / "store" / "artifacts" / digest
    p.write_bytes(p.read_bytes().replace(b'"approved"', b'"rejected"'))


def a02_cited_receipt_member_edited(cell):
    """A signed member of the cited acquisition receipt is changed in the store."""
    edit_receipt_in_store(cell, 0, ["acquisition", "endpoint"], "warehouse.example:443")


def a03_cited_receipt_removed(cell):
    receipt_path(cell, 0).unlink()


def a04_decision_record_rewritten(cell):
    p = cell / "decisions" / "audit" / "evaluations.jsonl"
    p.write_bytes(p.read_bytes().replace(b'"outcomeId":"approve"', b'"outcomeId":"reject"'))


def a05_registry_seal_removed(cell):
    (cell / "registry.jsonl").write_text("")


def a06_receipt_appended_after_seal(cell):
    """A third receipt is appended to the sealed session in the store, a copy of the second under index 2 -- without an attestation."""
    shutil.copy(receipt_path(cell, 1), receipt_path(cell, 2))


def a07_action_member_edited(cell):
    """A signed member of the action receipt itself is changed in the store; the attestation keeps the original."""
    edit_receipt_in_store(cell, 1, ["action", "decision", "packDigest"], "sha256:" + "f" * 64)


def b01_envelope_payload_edited(cell):
    """The attestation's payload is altered without re-signing."""
    p = envelope_path(cell, 1)
    env = read_json(p)
    import base64
    payload = base64.b64decode(env["payload"])
    altered = payload.replace(b"gateway:corpus", b"gateway:corpuz")
    assert altered != payload, "the construction must change the payload"
    env["payload"] = base64.b64encode(altered).decode()
    write_json(p, env)


def foreign_signer():
    """A key that is not the adapter's, derived from its own fixed seed so the construction is deterministic."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from securesystemslib.signer import CryptoSigner, SSlibKey
    private = ed25519.Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"judgment-pack study 022 foreign key").digest())
    return CryptoSigner(private, SSlibKey.from_crypto(private.public_key()))


def b02_envelope_resigned_foreign_key(cell):
    """The action's attestation is rebuilt and signed with a key that is not the adapter's."""
    resign(cell, 1, statement_of(cell, 1), foreign_signer())


def b03_subject_swapped_resigned(cell):
    """Holding the adapter's key: the action's artifact subject is pointed at the acquisition's artifact and the statement re-signed."""
    st = statement_of(cell, 1)
    other = read_json(receipt_path(cell, 0))["resultDigest"].split(":", 1)[1]
    for s in st["subject"]:
        if s["name"] == "artifact":
            s["digest"]["sha256"] = other
    resign(cell, 1, st)


def b04_predicate_type_changed_resigned(cell):
    st = statement_of(cell, 1)
    st["predicateType"] = "https://slsa.dev/provenance/v1"
    resign(cell, 1, st)


def b05_statement_type_changed_resigned(cell):
    st = statement_of(cell, 1)
    st["_type"] = "https://in-toto.io/Statement/v0.1"
    resign(cell, 1, st)


def b06_attestation_deleted(cell):
    envelope_path(cell, 1).unlink()


def b07_payload_type_changed(cell):
    p = envelope_path(cell, 1)
    env = read_json(p)
    env["payloadType"] = "application/json"
    write_json(p, env)


def b08_predicate_receipt_edited_resigned(cell):
    """Holding the adapter's key: the predicate's copy of the action receipt is altered (packDigest) and re-signed; the store is untouched."""
    st = statement_of(cell, 1)
    st["predicate"]["action"]["decision"]["packDigest"] = "sha256:" + "f" * 64
    resign(cell, 1, st)


def b09_cited_subject_dropped_resigned(cell):
    """Holding the adapter's key: the action's cited-receipt subject is removed and the statement re-signed."""
    st = statement_of(cell, 1)
    st["subject"] = [s for s in st["subject"] if not s["name"].startswith("cites/")]
    resign(cell, 1, st)


def c01_store_reminted_other_gateway_key(cell):
    """A store minted under another gateway key, its attestations bound afresh by the adapter: the adapter's key holds, the gateway's does not."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    import base64
    # re-sign both receipts under a different Ed25519 key, keeping every other member; the gateway's keyId is the
    # first 32 hex of sha256(public key), as SPEC.md section 1.2 defines it
    private = ed25519.Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"022 other gateway").digest())
    public = private.public_key().public_bytes_raw()
    key_id = hashlib.sha256(public).hexdigest()[:32]
    prev = None
    for index in (0, 1):
        p = receipt_path(cell, index)
        doc = json.loads(p.read_text())
        doc["keyId"] = key_id
        doc["prevSignature"] = prev
        core = {k: v for k, v in doc.items() if k != "signature"}
        canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        prefix = b"judgment-pack-gateway-receipt-v3:"
        sig = private.sign(prefix + canon).hex()
        doc["signature"] = sig
        prev = sig
        p.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    shutil.rmtree(cell / "attestations")
    bind.bind(cell / "store", cell / "attestations")


def neg_dsse_signature_flipped(cell):
    """Control: one signature byte of the action's attestation is flipped -- the reference verifier must refuse it."""
    p = envelope_path(cell, 1)
    env = read_json(p)
    sig = env["signatures"][0]["sig"]
    env["signatures"][0]["sig"] = ("0" if sig[0] != "0" else "1") + sig[1:]
    write_json(p, env)


CELLS = {
    "pos-baseline": pos_baseline,
    "a01-artifact-edited": a01_artifact_edited,
    "a02-cited-receipt-member-edited": a02_cited_receipt_member_edited,
    "a03-cited-receipt-removed": a03_cited_receipt_removed,
    "a04-decision-record-rewritten": a04_decision_record_rewritten,
    "a05-registry-seal-removed": a05_registry_seal_removed,
    "a06-receipt-appended-after-seal": a06_receipt_appended_after_seal,
    "a07-action-member-edited": a07_action_member_edited,
    "b01-envelope-payload-edited": b01_envelope_payload_edited,
    "b02-envelope-resigned-foreign-key": b02_envelope_resigned_foreign_key,
    "b03-subject-swapped-resigned": b03_subject_swapped_resigned,
    "b04-predicate-type-changed-resigned": b04_predicate_type_changed_resigned,
    "b05-statement-type-changed-resigned": b05_statement_type_changed_resigned,
    "b06-attestation-deleted": b06_attestation_deleted,
    "b07-payload-type-changed": b07_payload_type_changed,
    "b08-predicate-receipt-edited-resigned": b08_predicate_receipt_edited_resigned,
    "b09-cited-subject-dropped-resigned": b09_cited_subject_dropped_resigned,
    "c01-store-reminted-other-gateway-key": c01_store_reminted_other_gateway_key,
    "neg-dsse-signature-flipped": neg_dsse_signature_flipped,
}


def build(cell_id, out_root):
    cell = Path(out_root) / cell_id
    if cell.exists():
        raise FileExistsError(cell)
    shutil.copytree(BASELINE, cell)
    CELLS[cell_id](cell)
    return cell


if __name__ == "__main__":
    for cid in sys.argv[2:] or CELLS:
        print(build(cid, sys.argv[1]))
