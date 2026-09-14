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
PRIMARY_ROOT = HERE.parent / "results" / "primary-attempt-001"


class RegisteredContext:
    """The only context in which a holdout cell is constructed: a validated registered attempt at the literal primary
    root (PREREGISTRATION.md section 1a) -- every pin non-null and matching (harness/pins.py, the executing code
    included), the marker complete and matched (harness/marker.py) against the gateway binary given. Constructing one
    runs the whole validation; `check()` re-reads the marker before any construction."""

    def __init__(self, root, gateway):
        import marker as marking
        import pins as pinning
        root, gateway = Path(root).resolve(), Path(gateway).resolve()
        problems = []
        if root != PRIMARY_ROOT.resolve():
            problems.append("a holdout cell is constructed only for the registered attempt at %s" % PRIMARY_ROOT)
        problems += pinning.problems(pinning.load(), str(gateway), require_all=True)
        try:
            marker = json.loads((root / "ATTEMPT.json").read_text())
        except (OSError, ValueError) as e:
            marker, problems = None, problems + ["no readable attempt marker at %s (%s)" % (root, type(e).__name__)]
        if marker is not None:
            problems += marking.marker_problems(marker, pinning.sha256_file(gateway) if gateway.is_file() else None, "REGISTERED", root)
        if problems:
            raise RuntimeError("no validated registered attempt at %s:\n  %s" % (root, "\n  ".join(problems)))
        self.root, self.gateway, self.marker, self.attempt_id = root, gateway, marker, marker["attemptId"]

    def check(self):
        """Before a construction: the context is whole, its root is the literal one, and the marker on disk is the one validated."""
        try:
            root, marker = self.root, self.marker
        except AttributeError:
            raise RuntimeError("not a validated registered context")
        if root != PRIMARY_ROOT.resolve() or json.loads((root / "ATTEMPT.json").read_text()) != marker:
            raise RuntimeError("the registered attempt's marker at %s is not the one validated" % root)


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


RECEIPT_PREFIX_V3 = b"judgment-pack-gateway/receipt/3:"


def gateway_canon(core):
    """The gateway's canonical form for the members it signs (SPEC.md section 1.1): code-point order, compact, raw UTF-8."""
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def c01_store_reminted_other_gateway_key(cell):
    """A coherent receipt chain re-signed under another gateway key -- keyId, chain and citation all its own --
    presented against the unchanged trusted corpus registry, its attestations bound afresh by the adapter."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    private = ed25519.Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"022 other gateway").digest())
    public = private.public_key().public_bytes_raw()
    key_id = hashlib.sha256(public).hexdigest()[:32]
    prev = None
    signatures = {}
    for index in (0, 1):
        p = receipt_path(cell, index)
        doc = json.loads(p.read_text())
        doc["keyId"] = key_id
        doc["prevSignature"] = prev
        if doc.get("kind") == "action":
            for c in doc["action"]["cites"]:
                c["signature"] = signatures[(c["sessionId"], c["callIndex"])]
        core = {k: v for k, v in doc.items() if k != "signature"}
        sig = private.sign(RECEIPT_PREFIX_V3 + gateway_canon(core)).hex()
        doc["signature"] = sig
        signatures[("s2", index)] = sig
        prev = sig
        p.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
        # the construction validates its own chain: the signature verifies under the foreign key with the gateway's prefix
        private.public_key().verify(bytes.fromhex(sig), RECEIPT_PREFIX_V3 + gateway_canon(core))
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


# --- the reviewer's holdout constructions, implemented verbatim from harness/MATRIX-HOLDOUT.json ---

def h01_foreign_key_file_and_envelopes(cell):
    """Call bind.bind(cell / 'store', cell / 'attestations', signer=foreign_signer()): the key file beside the envelopes and both envelopes are the foreign key's; no gateway input changes."""
    bind.bind(cell / "store", cell / "attestations", signer=foreign_signer())


def h02_duplicate_citation_subject_bad_first(cell):
    """Insert {'name': 'cites/s2/0', 'digest': {'sha256': '0' * 64}} at index 0 of the action statement's subjects, keep the originals in order, re-sign."""
    st = statement_of(cell, 1)
    st["subject"].insert(0, {"name": "cites/s2/0", "digest": {"sha256": "0" * 64}})
    resign(cell, 1, st)


def h03_unreferenced_record_malformed_cites(cell):
    """Write exactly b'{"cites":null}\n' to the new regular file decisions/audit/h03.json; every baseline file unchanged."""
    (cell / "decisions" / "audit" / "h03.json").write_bytes(b'{"cites":null}\n')


def h04_action_tail_removed_orphan_kept(cell):
    """Delete only the action receipt; keep its attestation, both artifacts, the registry and the book."""
    receipt_path(cell, 1).unlink()


def h05_jsonl_crlf_and_empty_lines(cell):
    """The book's bytes change while its one non-empty record candidate is preserved: CRLF endings and empty lines around it."""
    p = cell / "decisions" / "audit" / "evaluations.jsonl"
    data = p.read_bytes()
    assert data.endswith(b"\n") and data.count(b"\n") == 1
    p.write_bytes(b"\r\n" + data[:-1] + b"\r\n\r\n")


def h06_empty_subject_list_resigned(cell):
    """The action statement's subject list emptied and the statement re-signed with the adapter's key."""
    st = statement_of(cell, 1)
    st["subject"] = []
    resign(cell, 1, st)


HOLDOUT_CELLS = {
    "h01-foreign-key-file-and-envelopes": h01_foreign_key_file_and_envelopes,
    "h02-duplicate-citation-subject-bad-first": h02_duplicate_citation_subject_bad_first,
    "h03-unreferenced-record-malformed-cites": h03_unreferenced_record_malformed_cites,
    "h04-action-tail-removed-orphan-kept": h04_action_tail_removed_orphan_kept,
    "h05-jsonl-crlf-and-empty-lines": h05_jsonl_crlf_and_empty_lines,
    "h06-empty-subject-list-resigned": h06_empty_subject_list_resigned,
}

ALL_CELLS = dict(CELLS, **HOLDOUT_CELLS)


def build(cell_id, out_root, registered=None):
    """Build one cell from the baseline. A holdout cell requires a validated RegisteredContext: the registered attempt is its
    first construction through this guarded builder (pretesting at the adapter layer is disclosed in PREREGISTRATION.md section 1a)."""
    if cell_id in HOLDOUT_CELLS:
        if not isinstance(registered, RegisteredContext):
            raise RuntimeError("holdout cell %s is constructed only inside the registered attempt (PREREGISTRATION.md section 1a)" % cell_id)
        registered.check()
    cell = Path(out_root) / cell_id
    if cell.exists():
        raise FileExistsError(cell)
    shutil.copytree(BASELINE, cell)
    ALL_CELLS[cell_id](cell)
    return cell


if __name__ == "__main__":
    for cid in sys.argv[2:] or CELLS:
        if cid in HOLDOUT_CELLS:
            sys.exit("refusing: %s is a holdout cell; it is constructed only inside the registered attempt" % cid)
        print(build(cid, sys.argv[1]))
