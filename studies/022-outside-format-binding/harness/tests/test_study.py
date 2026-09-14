"""Harness tests for Study 022. Run from the study root, in the virtual environment that holds the pinned packages:
    python -m unittest discover -s harness/tests
The tests build the locked constructions only. Three tests in class Verifiers perform, on a copy of the baseline, the
edits the reviewer's holdout cells h01, h02 and h06 specify and assert the adapter layers' outcomes (disclosed in
PREREGISTRATION.md section 1a); no holdout cell is built through harness/cells.py here."""
import os
import sys

# the bytecode policy, with os and sys alone, before any other import (harness/guard.py, PREREGISTRATION.md section 2);
# run with PYTHONPYCACHEPREFIX set (README) so that this module too is compiled from its source
sys.dont_write_bytecode = True
if not sys.pycache_prefix:
    for _attempt in range(10000):
        _d = os.path.join(os.environ.get("TMPDIR") or "/tmp", "study022-pycache-%d-%d" % (os.getpid(), _attempt))
        try:
            os.mkdir(_d, 0o700)
            sys.pycache_prefix = _d
            break
        except FileExistsError:
            continue
_HARNESS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HARNESS)
import guard  # noqa: E402
guard.establish(os.path.dirname(_HARNESS))

import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402
import run_attempt  # noqa: E402
import run_layers  # noqa: E402
import score  # noqa: E402
import trees  # noqa: E402
import bind  # noqa: E402
import storewalk  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

GATEWAY = os.environ.get("GATEWAY_BIN")
BASE = STUDY / "fixtures" / "baseline"
TRUSTED = verify_attestation.trusted_key(BASE / "attestations" / "adapter.pubkey.json")
STATEMENT_HEAD = {"_type": verify_attestation.STATEMENT_TYPE, "predicateType": verify_attestation.PREDICATE_TYPE}


def matrix_ids(name):
    return [c["id"] for c in score.load_matrix(STUDY / "harness" / name)]


def signed_envelope(payload):
    from securesystemslib.dsse import Envelope
    env = Envelope(payload, bind.PAYLOAD_TYPE, {})
    env.sign(bind.adapter_signer())
    return json.dumps(env.to_dict())


class Registry(unittest.TestCase):
    def test_the_locked_matrix_and_the_locked_constructions_are_the_same_set(self):
        ids = matrix_ids("MATRIX.json")
        self.assertEqual(set(ids), set(constructions.CELLS))
        self.assertEqual(len(ids), len(set(ids)))

    def test_the_holdout_matrix_and_the_holdout_constructions_are_the_same_set_and_disjoint(self):
        ids = matrix_ids("MATRIX-HOLDOUT.json")
        self.assertEqual(set(ids), set(constructions.HOLDOUT_CELLS))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(set(constructions.CELLS) & set(constructions.HOLDOUT_CELLS))
        self.assertEqual(set(constructions.ALL_CELLS), set(constructions.CELLS) | set(constructions.HOLDOUT_CELLS))
        for cid in constructions.HOLDOUT_CELLS:
            self.assertTrue(callable(constructions.HOLDOUT_CELLS[cid]), cid)  # a construction exists; it is not called here

    def test_every_matrix_row_has_the_registered_members(self):
        for name in ("MATRIX.json", "MATRIX-HOLDOUT.json"):
            for c in score.load_matrix(STUDY / "harness" / name):
                for k in ("id", "role", "attackerCapability", "expected", "ownership", "structure", "reason"):
                    self.assertIn(k, c, (name, c.get("id")))
                self.assertEqual(sorted(c["expected"]), ["binding", "combined", "gateway", "intoto"], c["id"])


class Constructions(unittest.TestCase):
    def test_every_locked_cell_builds_deterministically(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for cid in constructions.CELLS:
                constructions.build(cid, a)
                constructions.build(cid, b)
                self.assertTrue(trees.same_tree(Path(a) / cid, Path(b) / cid), cid)

    def test_a_cell_root_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as a:
            constructions.build("pos-baseline", a)
            with self.assertRaises(FileExistsError):
                constructions.build("pos-baseline", a)

    def test_every_locked_construction_but_the_baseline_changes_something(self):
        with tempfile.TemporaryDirectory() as a:
            base = constructions.build("pos-baseline", a)
            for cid in constructions.CELLS:
                if cid == "pos-baseline":
                    continue
                self.assertFalse(trees.same_tree(base, constructions.build(cid, a)), cid)

    def test_a_holdout_cell_is_not_built_without_a_registered_context(self):
        with tempfile.TemporaryDirectory() as a:
            for cid in constructions.HOLDOUT_CELLS:
                with self.assertRaises(RuntimeError):
                    constructions.build(cid, a)
                with self.assertRaises(RuntimeError):
                    constructions.build(cid, a, registered=object())
                self.assertFalse((Path(a) / cid).exists(), "nothing is copied before the refusal")
            with self.assertRaises(RuntimeError):
                constructions.RegisteredContext(a, GATEWAY or "/nonexistent")  # not the literal root
            forged = object.__new__(constructions.RegisteredContext)
            with self.assertRaisesRegex(RuntimeError, "not a validated registered context"):
                constructions.build(next(iter(constructions.HOLDOUT_CELLS)), a, registered=forged)
            forged.root, forged.gateway, forged.marker = constructions.PRIMARY_ROOT.resolve(), Path(GATEWAY or "/nonexistent"), {}
            with self.assertRaisesRegex(RuntimeError, "no validated registered attempt"):  # populated: validated from disk, not trusted
                constructions.build(next(iter(constructions.HOLDOUT_CELLS)), a, registered=forged)
            forged.check = lambda: None  # an instance-level stand-in for the method: the builder never calls the object's method
            with self.assertRaisesRegex(RuntimeError, "no validated registered attempt"):
                constructions.build(next(iter(constructions.HOLDOUT_CELLS)), a, registered=forged)

            class Impostor(constructions.RegisteredContext):
                def __init__(self):
                    self.root, self.gateway, self.marker = constructions.PRIMARY_ROOT.resolve(), Path("/nonexistent"), {}

                def check(self):
                    return None
            with self.assertRaisesRegex(RuntimeError, "constructed only inside the registered attempt"):
                constructions.build(next(iter(constructions.HOLDOUT_CELLS)), a, registered=Impostor())
            self.assertEqual(os.listdir(a), [], "nothing is copied before the refusal")
            r = subprocess.run([sys.executable, str(STUDY / "harness" / "cells.py"), a, next(iter(constructions.HOLDOUT_CELLS))], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("holdout cell", r.stderr)

    def test_c01_is_a_coherent_chain_under_the_gateway_prefix(self):
        from cryptography.hazmat.primitives.asymmetric import ed25519
        import hashlib
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("c01-store-reminted-other-gateway-key", a)
            public = ed25519.Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"022 other gateway").digest()).public_key()
            docs = [json.loads(constructions.receipt_path(cell, i).read_text()) for i in (0, 1)]
            for doc in docs:
                core = {k: v for k, v in doc.items() if k != "signature"}
                # the gateway's signing prefix as its SPEC.md section 1.2a states it, spelled here so the constant cannot drift with it
                public.verify(bytes.fromhex(doc["signature"]), b"judgment-pack-gateway/receipt/3:" + json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
            self.assertEqual(docs[1]["prevSignature"], docs[0]["signature"])
            self.assertEqual(docs[1]["action"]["cites"][0]["signature"], docs[0]["signature"])
            self.assertEqual(docs[0]["keyId"], docs[1]["keyId"])
            self.assertEqual((cell / "registry.jsonl").read_bytes(), (BASE / "registry.jsonl").read_bytes())


class RegisteredContextValidation(unittest.TestCase):
    def test_the_context_requires_a_complete_marker_and_matching_pins(self):
        saved = constructions.PRIMARY_ROOT
        with tempfile.TemporaryDirectory() as a:
            root = Path(a) / "primary-attempt-001"
            root.mkdir()
            constructions.PRIMARY_ROOT = root
            try:
                gateway = Path(a) / "gateway"
                gateway.write_bytes(b"stand-in")
                with self.assertRaisesRegex(RuntimeError, "no readable attempt marker"):
                    constructions.RegisteredContext(root, gateway)
                (root / "ATTEMPT.json").write_text(json.dumps({"label": "REGISTERED", "attemptId": "not-a-real-attempt", "attemptRoot": str(root)}))
                with self.assertRaisesRegex(RuntimeError, "marker lacks") as cm:
                    constructions.RegisteredContext(root, gateway)
                self.assertIn("is not pinned", str(cm.exception), "null freeze pins refuse a registered context before the freeze")
                self.assertIn("gateway binary's digest", str(cm.exception))
                # the positive path, with the pins stood in for (they are null before the freeze): the marker must be whole and matched
                original = pinning.problems
                pinning.problems = lambda pins, gateway_binary, require_all=False: []
                try:
                    marker = {"attemptId": "a" * 32, "attemptRoot": str(root), "label": "REGISTERED", "gatewaySha256": pinning.sha256_file(gateway),
                              "pinsRawSha256": pinning.raw_sha256(), "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0],
                              "cells": sorted(constructions.ALL_CELLS), "startedAt": "t"}
                    (root / "ATTEMPT.json").write_text(json.dumps(marker))
                    ctx = constructions.RegisteredContext(root, gateway)
                    ctx.check()
                    self.assertEqual(constructions.validate_registered_attempt(root, gateway), marker)
                    (root / "ATTEMPT.json").write_text(json.dumps(dict(marker, attemptId="b" * 3)))
                    with self.assertRaisesRegex(RuntimeError, "attempt id"):  # the builder's validation reads the disk, not the object
                        ctx.check()
                    (root / "ATTEMPT.json").write_text("{}")
                    with self.assertRaisesRegex(RuntimeError, "marker lacks"):
                        constructions.validate_registered_attempt(root, gateway)
                    (root / "ATTEMPT.json").write_text("null")  # the round-5 route: a file that reads as None
                    with self.assertRaisesRegex(RuntimeError, "no attempt marker"):
                        constructions.validate_registered_attempt(root, gateway)
                    forged = object.__new__(constructions.RegisteredContext)
                    forged.root, forged.gateway = root, gateway
                    with self.assertRaisesRegex(RuntimeError, "no attempt marker"):
                        constructions.build(next(iter(constructions.HOLDOUT_CELLS)), a, registered=forged)
                    self.assertFalse(any(p.is_dir() and p.name in constructions.HOLDOUT_CELLS for p in Path(a).iterdir()), "nothing copied")
                    (root / "ATTEMPT.json").write_text(json.dumps(dict(marker, cells=sorted(constructions.CELLS))))
                    with self.assertRaisesRegex(RuntimeError, "cell set"):
                        constructions.RegisteredContext(root, gateway)
                    with self.assertRaisesRegex(RuntimeError, "literal|constructed only"):
                        constructions.RegisteredContext(Path(a), gateway)
                finally:
                    pinning.problems = original
            finally:
                constructions.PRIMARY_ROOT = saved


class TreeComparison(unittest.TestCase):
    def test_same_size_same_mtime_different_bytes_is_not_the_same_tree(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(a) / "f").write_bytes(b"abc")
            (Path(b) / "f").write_bytes(b"abd")
            os.utime(Path(a) / "f", (1000, 1000))
            os.utime(Path(b) / "f", (1000, 1000))
            self.assertFalse(trees.same_tree(a, b))

    def test_an_empty_directory_changes_the_tree_and_its_digest(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(a) / "f").write_bytes(b"x")
            (Path(b) / "f").write_bytes(b"x")
            self.assertTrue(trees.same_tree(a, b))
            self.assertEqual(trees.tree_digest(a), trees.tree_digest(b))
            (Path(b) / "receipts" / "s9").mkdir(parents=True)
            self.assertFalse(trees.same_tree(a, b))
            self.assertNotEqual(trees.tree_digest(a), trees.tree_digest(b))

    def test_a_symbolic_link_or_a_non_regular_entry_is_refused_root_included(self):
        with tempfile.TemporaryDirectory() as a:
            (Path(a) / "d").mkdir()
            (Path(a) / "d" / "f").write_bytes(b"x")
            os.symlink("f", Path(a) / "d" / "g")
            with self.assertRaises(RuntimeError):
                trees.typed_tree(Path(a) / "d")
            os.unlink(Path(a) / "d" / "g")
            os.mkfifo(Path(a) / "d" / "p")
            with self.assertRaises(RuntimeError):
                trees.tree_digest(Path(a) / "d")
            os.unlink(Path(a) / "d" / "p")
            os.symlink("d", Path(a) / "link")
            with self.assertRaises(RuntimeError):
                trees.typed_tree(Path(a) / "link")
            self.assertTrue(trees.same_tree(Path(a) / "d", Path(a) / "d"))


class Binding(unittest.TestCase):
    def test_the_baseline_binding_is_deterministic_and_verifies(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            bind.bind(BASE / "store", a)
            bind.bind(BASE / "store", b)
            self.assertTrue(trees.same_tree(a, b))
            r = verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)
            self.assertTrue(r["pass"], r)
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"])
            self.assertTrue(trees.same_tree(a, BASE / "attestations"), "the committed attestations are the adapter's binding of the committed store")

    def test_the_adapter_key_is_the_pinned_one_and_the_fixture_file_carries_it_by_id_and_material(self):
        pins = pinning.load()
        self.assertEqual(pinning.adapter_keyid(), pins["adapter"]["keyid"])
        self.assertEqual(pinning.trusted_pubkey_problems(pins), [])
        self.assertEqual(TRUSTED.keyid, pins["adapter"]["keyid"])
        genuine = json.loads((BASE / "attestations" / "adapter.pubkey.json").read_text())
        foreign = constructions.foreign_signer().public_key
        with tempfile.TemporaryDirectory() as a:
            p = Path(a) / "k.json"
            p.write_text(json.dumps(dict(genuine, keyval={"public": foreign.keyval["public"]})))  # the right id, foreign material
            self.assertTrue(any("material" in x for x in pinning.trusted_pubkey_problems(pins, p)))
            p.write_text(json.dumps(dict(genuine, keyid=foreign.keyid)))  # the right material, another id
            self.assertTrue(any("key id" in x for x in pinning.trusted_pubkey_problems(pins, p)))


class Verifiers(unittest.TestCase):
    """Function-level tests of the round-1 fixes on the adapter layers. The first, second and fifth perform the edits the
    reviewer's h01, h02 and h06 specify on a copy of the baseline (pretested at the adapter-layer level: PREREGISTRATION.md 1a)."""

    def test_a_binding_under_a_foreign_key_is_untrusted_whatever_key_file_lies_beside_it(self):
        with tempfile.TemporaryDirectory() as a:
            bind.bind(BASE / "store", a, signer=constructions.foreign_signer())
            self.assertNotEqual(json.loads((Path(a) / "adapter.pubkey.json").read_text())["keyid"], TRUSTED.keyid)
            r = verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)
            self.assertFalse(r["pass"])
            self.assertEqual([x["dsse"] for x in r["attestations"]], ["fail:untrusted-key", "fail:untrusted-key"])
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"], "the binding layer reads no key")

    def test_a_duplicated_subject_name_keeps_the_earlier_failure_and_breaks_multiplicity(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            st = constructions.statement_of(cell, 1)
            st["subject"].insert(0, {"name": "cites/s2/0", "digest": {"sha256": "0" * 64}})
            constructions.resign(cell, 1, st)
            r = verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions", TRUSTED)
            one = r["attestations"][1]
            self.assertEqual(one["statement"], "valid")
            self.assertEqual(one["subjects"][0], ["cites/s2/0", "mismatch"])
            self.assertEqual(verify_attestation.per_name(one["subjects"])["cites/s2/0"], "mismatch")
            self.assertFalse(verify_attestation.attestation_passes(one))
            self.assertEqual(verify_binding.verify(cell / "store", cell / "attestations")["attestations"][1]["binding"], "fail:cites-subject-set")

    def test_the_key_file_beside_the_envelopes_is_not_consulted(self):
        with tempfile.TemporaryDirectory() as a:
            bind.bind(BASE / "store", a)
            (Path(a) / "adapter.pubkey.json").unlink()
            self.assertTrue(verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)["pass"])
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"])

    def test_per_name_keeps_the_first_outcome_that_is_not_match(self):
        self.assertEqual(verify_attestation.per_name([["a", "match"], ["a", "missing"], ["a", "mismatch"], ["b", "match"]]), {"a": "missing", "b": "match"})
        self.assertEqual(verify_attestation.per_name([]), {})

    def test_an_empty_subject_list_is_invalid_bindings_and_an_artifact_subject_mismatch(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            st = constructions.statement_of(cell, 1)
            st["subject"] = []
            constructions.resign(cell, 1, st)
            r = verify_attestation.verify_one(constructions.envelope_path(cell, 1), TRUSTED, cell / "store", cell / "decisions")
            self.assertEqual((r["dsse"], r["statement"]), ("pass", "invalid:bindings"))
            self.assertEqual(verify_binding.check_one(constructions.envelope_path(cell, 1), constructions.receipt_path(cell, 1)), "fail:artifact-subject-mismatch")

    def test_malformed_payloads_get_the_specified_codes_not_exceptions(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p = constructions.envelope_path(cell, 1)
            receipt = constructions.receipt_path(cell, 1)
            stored = json.loads(receipt.read_text())
            good_subjects = json.loads(bind.serialize(constructions.statement_of(cell, 1)))["subject"]
            cases = [
                (b"[]", "invalid:not-object", None, "fail:unreadable"),
                (b"not json", "invalid:not-json", None, "fail:unreadable"),
                (bind.serialize(dict(STATEMENT_HEAD, subject="no", predicate=stored)), "invalid:bindings", None, "fail:unreadable"),
                (bind.serialize(dict(STATEMENT_HEAD, subject=[{"name": "artifact", "digest": {"sha256": 5}}], predicate=stored)), "invalid:bindings", None, "fail:unreadable"),
                (bind.serialize(dict(STATEMENT_HEAD, subject=[{"name": "artifact", "digest": {"sha256": "0" * 64}}], predicate={})), "invalid:bindings", None, "fail:predicate-differs-from-store"),
                # an unknown descriptor member alone (the predicate is complete) is refused by the mapping
                (bind.serialize(dict(STATEMENT_HEAD, subject=good_subjects + [{"name": "artifact", "digest": {"sha256": "0" * 64}, "extra": 1}], predicate=stored)), "invalid:bindings", None, "fail:artifact-subject-mismatch"),
                # a `content` member, base64 text as the JSON mapping defines it, is accepted as supplied
                (bind.serialize(dict(STATEMENT_HEAD, subject=[dict(good_subjects[0], content="AAEC")] + good_subjects[1:], predicate=stored)), "valid", [[s["name"], "match"] for s in good_subjects], "pass"),
                # unknown names and a malformed digest are outcomes, never exceptions; the binding then judges the names
                (bind.serialize(dict(STATEMENT_HEAD, subject=[{"name": "cites/x", "digest": {"sha256": "0" * 64}}, {"name": "cites/s2/0/1", "digest": {"sha256": "0" * 64}},
                                                             {"name": "artifact", "digest": {"sha256": "x"}}], predicate=stored)), "valid",
                 [["cites/x", "unknown-subject"], ["cites/s2/0/1", "unknown-subject"], ["artifact", "unknown-subject"]], "fail:unreadable"),
                (bind.serialize(dict(STATEMENT_HEAD, subject=good_subjects + [{"name": "other", "digest": {"sha256": "0" * 64}}], predicate=stored)), "valid",
                 [[s["name"], "match"] for s in good_subjects] + [["other", "unknown-subject"]], "fail:foreign-subject"),
            ]
            for payload, statement_code, subjects, binding_code in cases:
                p.write_text(signed_envelope(payload))
                r = verify_attestation.verify_one(p, TRUSTED, cell / "store", cell / "decisions")
                self.assertEqual(r["dsse"], "pass", payload)
                self.assertEqual(r["statement"], statement_code, payload)
                if subjects is not None:
                    self.assertEqual(r["subjects"], subjects, payload)
                self.assertEqual(verify_binding.check_one(p, receipt), binding_code, payload)

    def test_a_trailing_newline_is_not_a_digest_anywhere(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p, receipt = constructions.envelope_path(cell, 1), constructions.receipt_path(cell, 1)
            st = constructions.statement_of(cell, 1)
            for name in ("artifact", "cites/s2/0"):
                doc = json.loads(json.dumps(st))
                for s in doc["subject"]:
                    if s["name"] == name:
                        s["digest"]["sha256"] += "\n"
                p.write_text(signed_envelope(bind.serialize(doc)))
                r = verify_attestation.verify_one(p, TRUSTED, cell / "store", cell / "decisions")
                self.assertEqual(r["statement"], "valid")
                self.assertEqual(verify_attestation.per_name(r["subjects"])[name], "unknown-subject", name)
                self.assertEqual(verify_binding.check_one(p, receipt), "fail:unreadable", name)
        self.assertIsNone(verify_binding.digest_after_prefix("sha256:" + "a" * 64 + "\n"))
        self.assertIsNotNone(score.finding_problem({"recordDigest": "sha256:" + "a" * 64 + "\n", "status": "record-citation-malformed"}))
        self.assertIsNone(score.finding_problem({"recordDigest": "sha256:" + "a" * 64, "status": "record-citation-malformed"}))

    def test_nested_predicate_shapes_get_a_code_in_the_binding_layer(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p, receipt = constructions.envelope_path(cell, 1), constructions.receipt_path(cell, 1)
            st = constructions.statement_of(cell, 1)
            for edit in (lambda d: d.__setitem__("action", "x"), lambda d: d["action"].__setitem__("decision", "x"), lambda d: d["action"].__setitem__("cites", [None]),
                         lambda d: d["action"].__setitem__("cites", [{"sessionId": "s2", "callIndex": "0"}])):
                doc = json.loads(json.dumps(st))
                edit(doc["predicate"])
                receipt.write_text(json.dumps(doc["predicate"], sort_keys=True, separators=(",", ":")))  # predicate and store agree, both malformed
                p.write_text(signed_envelope(bind.serialize(doc)))
                self.assertEqual(verify_binding.check_one(p, receipt), "fail:unreadable")

    def test_a_repeated_citation_with_two_matching_subjects_passes_the_binding(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p, receipt = constructions.envelope_path(cell, 1), constructions.receipt_path(cell, 1)
            st = constructions.statement_of(cell, 1)
            st["predicate"]["action"]["cites"].append(dict(st["predicate"]["action"]["cites"][0]))
            st["subject"].append(dict([s for s in st["subject"] if s["name"].startswith("cites/")][0]))
            receipt.write_text(json.dumps(st["predicate"], sort_keys=True, separators=(",", ":")))
            p.write_text(signed_envelope(bind.serialize(st)))
            self.assertEqual(verify_binding.check_one(p, receipt), "pass")
            del st["subject"][-1]
            p.write_text(signed_envelope(bind.serialize(st)))
            self.assertEqual(verify_binding.check_one(p, receipt), "fail:cites-subject-set")

    def test_a_present_non_file_at_an_attestation_path_is_not_an_outcome(self):
        for make in (lambda p: p.mkdir(), lambda p: os.symlink("0.dsse.json", p)):
            with tempfile.TemporaryDirectory() as a:
                cell = constructions.build("pos-baseline", a)
                p = constructions.envelope_path(cell, 1)
                p.unlink()
                make(p)
                with self.assertRaises(OSError):
                    verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions", TRUSTED)
                with self.assertRaises(OSError):
                    verify_binding.verify(cell / "store", cell / "attestations")
                p.unlink() if p.is_symlink() else p.rmdir()
                self.assertEqual(verify_binding.verify(cell / "store", cell / "attestations")["attestations"][1]["binding"], "fail:missing-attestation")

    def test_receipts_are_enumerated_as_the_gateway_enumerates(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            (cell / "store" / "receipts" / "s2" / "notes.txt").write_text("x")
            (cell / "store" / "receipts" / "s2" / "dir.json").mkdir()
            self.assertEqual([(s, stem) for s, stem, _ in storewalk.stored_receipts(cell / "store")], [("s2", "0"), ("s2", "1")])
            (cell / "store" / "receipts" / "s2" / "x.json").write_text("{}")
            self.assertEqual([stem for _, stem, _ in storewalk.stored_receipts(cell / "store")], ["0", "1", "x"])
            os.mkfifo(cell / "store" / "receipts" / "s2" / "p.json")
            with self.assertRaises(OSError):
                storewalk.stored_receipts(cell / "store")


class Reduction(unittest.TestCase):
    def test_reduction_keeps_only_the_first_failure_per_attestation_and_per_name(self):
        o = {"cell": "x", "gateway": {"ok": True, "statuses": ["ok"], "findings": []},
             "intoto": {"pass": False, "attestations": [
                 {"attestation": "s2/0.dsse.json", "dsse": "pass", "statement": "valid", "subjects": [["artifact", "match"]]},
                 {"attestation": "s2/1.dsse.json", "dsse": "fail:signature", "statement": None, "subjects": []},
                 {"attestation": "s2/2.dsse.json", "dsse": "pass", "statement": "valid", "subjects": [["cites/s2/0", "mismatch"], ["artifact", "match"], ["cites/s2/0", "match"]]}]},
             "binding": {"pass": True, "attestations": [{"attestation": "s2/0.dsse.json", "binding": "pass"}, {"attestation": "s2/1.dsse.json", "binding": "pass"}]},
             "combined": "fail"}
        r = score.reduce_observation(o)
        self.assertEqual(r["intoto"], {"pass": False, "failures": {"s2/1.dsse.json": "fail:signature", "s2/2.dsse.json": {"cites/s2/0": "mismatch"}}})
        self.assertEqual(r["binding"], {"pass": True, "failures": {}})


def complete_observation(cell):
    """A complete, self-consistent observation of the baseline cell without the gateway binary."""
    i = verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions", TRUSTED)
    b = verify_binding.verify(cell / "store", cell / "attestations")
    g = {"ok": True, "findings": [{"callIndex": 0, "sessionId": "s2", "status": "ok"}, {"callIndex": 1, "sessionId": "s2", "status": "ok"}], "statuses": ["ok"]}
    return {"cell": cell.name, "cellSha256": trees.tree_digest(cell), "gateway": g, "intoto": i, "binding": b, "combined": "pass"}


class ObservationValidation(unittest.TestCase):
    def test_a_complete_observation_of_the_rebuilt_cell_has_no_problems(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            self.assertEqual(score.observation_problems(complete_observation(cell), "pos-baseline", cell, trees.tree_digest(cell)), [])

    def test_the_reviewers_synthetic_record_is_refused(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = {"cell": "pos-baseline", "cellSha256": trees.tree_digest(cell), "gateway": {"ok": True, "statuses": ["ok"], "findings": []},
                 "intoto": {"pass": True, "attestations": []}, "binding": {"pass": True, "attestations": []}, "combined": "pass"}
            problems = score.observation_problems(o, "pos-baseline", cell, trees.tree_digest(cell))
            self.assertTrue(any("statuses" in p for p in problems), problems)
            self.assertTrue(any("one per stored receipt file" in p for p in problems), problems)
            self.assertTrue(any("one per stored receipt in order" in p for p in problems), problems)

    def test_every_shortfall_is_a_problem(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            snap = trees.tree_digest(cell)
            good = complete_observation(cell)

            def mutated(fn):
                o = json.loads(json.dumps(good))
                fn(o)
                return score.observation_problems(o, "pos-baseline", cell, snap)

            def flip_intoto(o): o["intoto"]["pass"] = False
            def flip_binding(o): o["binding"]["pass"] = False
            def flip_gateway(o): o["gateway"]["ok"] = False
            def flip_combined(o): o["combined"] = "fail"
            def bad_status(o): o["gateway"]["statuses"] = ["ok", "artifact-mismatch"]
            def drop_finding(o): o["gateway"]["findings"].pop()
            def invented_session(o): o["gateway"]["findings"][1]["sessionId"] = "s9"
            def status_outside_vocabulary(o):  # a consistent lie: only the vocabulary refuses it
                o["gateway"]["findings"][1]["status"] = "fine"; o["gateway"]["statuses"] = ["fine", "ok"]; o["gateway"]["ok"] = False; o["combined"] = "fail"
            def extra_receipt_finding(o): o["gateway"]["findings"].append({"callIndex": 2, "sessionId": "s2", "status": "ok"})
            def record_finding_with_session(o): o["gateway"]["findings"].append({"recordDigest": "sha256:" + "a" * 64, "sessionId": "s2", "status": "record-citation-malformed"}); o["gateway"]["ok"] = False; o["gateway"]["statuses"] = ["ok", "record-citation-malformed"]; o["combined"] = "fail"
            def drop_attestation(o): o["intoto"]["attestations"].pop()
            def reorder(o): o["binding"]["attestations"].reverse()
            def bad_code(o): o["binding"]["attestations"][0]["binding"] = "fail:something-else"
            def bad_subject(o): o["intoto"]["attestations"][0]["subjects"] = {"artifact": "match"}
            def stale_snapshot(o): o["cellSha256"] = "0" * 64
            def other_cell(o): o["cell"] = "a01-artifact-edited"
            def int_as_bool(o): o["intoto"]["pass"] = 1
            def int_as_bool_gateway(o): o["gateway"]["ok"] = 1
            def extra_record_member(o): o["binding"]["attestations"][0]["note"] = "x"
            def subjects_after_failed_statement(o):
                o["intoto"]["attestations"][0]["statement"] = "invalid:bindings"
                o["intoto"]["pass"] = False
                o["combined"] = "fail"
            def intoto_lie_with_consistent_combined(o):
                o["intoto"]["pass"] = False
                o["combined"] = "fail"
            def binding_lie_with_consistent_combined(o):
                o["binding"]["pass"] = False
                o["combined"] = "fail"
            def gateway_lie_with_consistent_combined(o):
                o["gateway"]["ok"] = False
                o["combined"] = "fail"
            for fn in (flip_intoto, flip_binding, flip_gateway, flip_combined, bad_status, drop_finding, extra_receipt_finding, invented_session,
                       status_outside_vocabulary, record_finding_with_session, drop_attestation, reorder, bad_code, bad_subject, stale_snapshot,
                       other_cell, int_as_bool, int_as_bool_gateway, extra_record_member, subjects_after_failed_statement,
                       intoto_lie_with_consistent_combined, binding_lie_with_consistent_combined, gateway_lie_with_consistent_combined):
                self.assertTrue(mutated(fn), fn.__name__)
            self.assertEqual(mutated(lambda o: None), [])

    def test_a_record_finding_of_the_gateways_shape_is_accepted(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = complete_observation(cell)
            o["gateway"]["findings"].append({"recordDigest": "sha256:" + "a" * 64, "status": "record-citation-malformed"})
            o["gateway"]["ok"], o["gateway"]["statuses"], o["combined"] = False, ["ok", "record-citation-malformed"], "fail"
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, trees.tree_digest(cell)), [])
            self.assertIsNone(score.finding_problem({"sessionId": "s2", "status": "tail-rollback", "have": 1, "sealed": 2}))
            self.assertIsNone(score.finding_problem({"sessionId": "s2", "callIndex": None, "status": "sequence-broken"}))
            self.assertIsNone(score.finding_problem({"sessionId": "s2", "file": "x.json", "status": "malformed"}))
            self.assertIsNotNone(score.finding_problem({"sessionId": "s2", "callIndex": None, "status": "ok"}))
            self.assertIsNotNone(score.finding_problem({"sessionId": "s2", "status": "tail-rollback"}))
            self.assertIsNotNone(score.finding_problem({"recordDigest": "abc", "status": "record-citation-malformed"}))

    def test_a_well_formed_record_that_is_not_the_apparatus_output_is_refused_by_recomputation(self):
        # the invented-subject record the round-2 review constructed: complete in shape, wrong in content
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = complete_observation(cell)
            o["intoto"]["attestations"][1]["subjects"] = [["invented", "match"]]
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, trees.tree_digest(cell)), [], "shape alone accepts it")
            i = verify_attestation.verify(cell / "store", cell / "attestations", cell / "decisions", TRUSTED)
            self.assertNotEqual(i, o["intoto"], "the recomputed layer differs; the scorer refuses on that")


class Decision(unittest.TestCase):
    def test_the_locked_stratum_alone_decides_and_the_holdout_reports_apart(self):
        locked = [{"id": "pos-baseline", "role": "control-gate", "verdict": "holds"}, {"id": "a01", "role": "endpoint", "verdict": "holds"}]
        holdout = [{"id": "h01", "role": "endpoint", "verdict": "diverges"}, {"id": "h02", "role": "endpoint", "verdict": "unconstructed", "error": "x"}]
        r = score.assemble("REGISTERED", "a" * 32, "g", True, [], locked, holdout, {"h02": "x"})
        self.assertEqual(r["decision"], "R1 holds")
        self.assertEqual(r["holdout"]["diverging"], ["h01"])
        self.assertEqual(r["holdout"]["unconstructed"], ["h02"])
        locked[1]["verdict"] = "diverges"
        self.assertEqual(score.assemble("REGISTERED", "a" * 32, "g", True, [], locked, holdout, {})["decision"], "R1 falsified")
        locked[0]["verdict"] = "diverges"
        self.assertEqual(score.assemble("REGISTERED", "a" * 32, "g", True, [], locked, holdout, {})["decision"], "control-gate-failed")
        self.assertEqual(score.assemble("REGISTERED", "a" * 32, "g", True, ["bad"], locked, holdout, {})["decision"], "pipeline-invalid")


class Pins(unittest.TestCase):
    def test_a_wrong_gateway_binary_is_a_problem(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"not the gateway")
        self.assertTrue(any("gateway binary" in p for p in pinning.problems(pinning.load(), f.name)))

    def test_execution_identity_classifies_every_loaded_module(self):
        import types
        pins = pinning.load()
        self.assertEqual(pinning.execution_problems(pins), [])
        self.assertIn("google._upb._message", sys.modules, "the protobuf backend in use is loaded and covered")
        import types
        genuine = sys.modules["securesystemslib.dsse"]
        fake = types.ModuleType("securesystemslib.planted")
        fake.__file__ = "/elsewhere/planted.py"
        sys.modules["securesystemslib.planted"] = fake
        try:
            self.assertTrue(any("planted" in p and "outside" in p for p in pinning.execution_problems(pins)), "an outside origin under a pinned name")
            fake.__file__, fake.__spec__, fake.__loader__ = genuine.__file__, None, object()
            self.assertTrue(any("planted" in p and "loaded by" in p for p in pinning.execution_problems(pins)), "another loader class on a pinned file")
            fake.__loader__ = genuine.__loader__
            fake.__cached__ = "/elsewhere/__pycache__/dsse.cpython-38.pyc"
            self.assertTrue(any("planted" in p and "cache" in p for p in pinning.execution_problems(pins)), "a cache read beside a source")
            # a stand-in of another type carrying _module is not unwrapped: it is judged by its own origin
            fake.__cached__, fake.__file__, fake.__loader__ = None, "/elsewhere/proxy.py", None
            fake._module = genuine
            self.assertTrue(any("planted" in p and "outside" in p for p in pinning.execution_problems(pins)))
            del sys.modules["securesystemslib.planted"]
            shadow = types.ModuleType("json")  # an in-memory stand-in for a library module under a pinned name is refused too
            shadow.__file__ = str(STUDY / "harness" / "json.py")
            shadow.__loader__ = genuine.__loader__
            saved_json = sys.modules["json"]
            sys.modules["json"] = shadow
            try:
                self.assertTrue(any(p.startswith("json ") for p in pinning.execution_problems(pins)), "a study-tree origin that is not a registered module")
            finally:
                sys.modules["json"] = saved_json
        finally:
            sys.modules.pop("securesystemslib.planted", None)
        self.assertEqual(pinning.execution_problems(pins), [])
        with tempfile.TemporaryDirectory() as a:
            saved = sys.pycache_prefix
            try:
                sys.pycache_prefix = a
                (Path(a) / "x.pyc").write_bytes(b"")
                self.assertTrue(any("must be empty" in p for p in pinning.execution_problems(pins)))
                sys.pycache_prefix = None
                self.assertTrue(any("no bytecode-cache prefix" in p for p in pinning.execution_problems(pins)))
            finally:
                sys.pycache_prefix = saved
        from unittest.mock import Mock
        genuine_statement = sys.modules["in_toto_attestation.v1.statement"]
        proxy = Mock(wraps=genuine_statement)  # the round-4 stand-in: a library-class object wrapping a pinned module
        proxy.Statement.copy_from_pb.return_value.validate.return_value = None
        sys.modules["in_toto_attestation.v1.planted"] = proxy
        try:
            self.assertTrue(any("planted" in p and "not a module" in p for p in pinning.execution_problems(pins)), "a Mock under a pinned name is refused")
        finally:
            del sys.modules["in_toto_attestation.v1.planted"]
        from importlib.machinery import ModuleSpec
        route1 = Mock(wraps=genuine_statement)  # the round-5 route: a stand-in posing as a namespace package
        route1.__file__ = None
        route1.__spec__ = ModuleSpec(genuine_statement.__name__, loader=None, is_package=True)
        route1.__spec__.submodule_search_locations = [str(Path(genuine_statement.__file__).parent)]
        route2 = Mock(spec=genuine_statement, wraps=genuine_statement)  # the other: isinstance(module) true through __class__
        route2.__file__, route2.__spec__, route2.__loader__, route2.__cached__ = (genuine_statement.__file__, genuine_statement.__spec__,
                                                                                    genuine_statement.__loader__, genuine_statement.__cached__)
        for stand_in in (route1, route2):
            self.assertTrue(isinstance(stand_in, types.ModuleType) or stand_in.__spec__.submodule_search_locations)
            sys.modules["in_toto_attestation.v1.planted"] = stand_in
            try:
                self.assertTrue(any("planted" in p and "not a module" in p for p in pinning.execution_problems(pins)), "a Mock is not a module by its real type")
            finally:
                del sys.modules["in_toto_attestation.v1.planted"]
        genuine_openssl, genuine_lib = sys.modules["_openssl"], sys.modules["_openssl.lib"]
        for name, stand_in in (("_openssl", types.ModuleType("_openssl")), ("_openssl.lib", object()), ("_openssl.lib", Mock(spec=genuine_lib))):
            sys.modules[name] = stand_in
            try:
                self.assertTrue(any(p.startswith(name + " ") for p in pinning.execution_problems(pins)), "an object under an originless name is admitted by identity only")
            finally:
                sys.modules[name] = genuine_openssl if name == "_openssl" else genuine_lib
        self.assertEqual(pinning.execution_problems(pins), [])
        import typing
        self.assertIs(sys.modules["typing.io"], typing.io)  # typing's own two objects pass, by identity
        self.assertEqual(pinning.execution_problems(pins), [])
        sys.modules["typing.io"] = Mock()  # the name alone grants nothing
        try:
            self.assertTrue(any(p.startswith("typing.io is not a module") for p in pinning.execution_problems(pins)))
        finally:
            sys.modules["typing.io"] = typing.io

        class Carrier:  # an object that is not a module, of a class from outside the interpreter's library
            __module__ = "securesystemslib.dsse"
        sys.modules["securesystemslib.carried"] = Carrier()
        ghost = types.ModuleType("securesystemslib.ghost")  # a module with no file and no loader, under a pinned name
        sys.modules["securesystemslib.ghost"] = ghost
        try:
            problems = pinning.execution_problems(pins)
            self.assertTrue(any("carried" in p and "not a module" in p for p in problems), problems)
            self.assertTrue(any("ghost" in p and "no file origin" in p for p in problems), problems)
        finally:
            del sys.modules["securesystemslib.carried"], sys.modules["securesystemslib.ghost"]
        library_shadow = types.ModuleType("cryptography.planted")  # a pinned name loaded from the interpreter's library
        library_shadow.__file__ = os.path.join(os.path.dirname(os.__file__), "planted.py")
        library_shadow.__loader__ = sys.modules["json"].__loader__
        sys.modules["cryptography.planted"] = library_shadow
        try:
            self.assertTrue(any("planted" in p and "interpreter's library" in p for p in pinning.execution_problems(pins)))
        finally:
            del sys.modules["cryptography.planted"]
        os.environ["PYTHONPATH"] = "/elsewhere"
        try:
            self.assertNotIn("PYTHONPATH", run_attempt.child_env())
            self.assertEqual(run_attempt.child_env()["PYTHONPYCACHEPREFIX"], sys.pycache_prefix)
        finally:
            del os.environ["PYTHONPATH"]
        wrong = json.loads(json.dumps(pins))
        wrong["harnessPython"]["implementation"] = "PyPy"
        self.assertTrue(any("interpreter is CPython" in p for p in pinning.execution_problems(wrong)))
        wrong = json.loads(json.dumps(pins))
        del wrong["intoto"]["packages"]["cffi"]
        self.assertTrue(any("cffi is installed" in p and "not pinned" in p for p in pinning.execution_problems(wrong)))

    def test_the_guard_refuses_shadows_and_foreign_import_paths(self):
        with tempfile.TemporaryDirectory() as a:
            study = Path(a)
            for d in ("adapter", "harness", "harness/tests"):
                (study / d).mkdir(parents=True)
            (study / "harness" / "cells.py").write_text("")
            self.assertEqual(guard.shadow_problems(str(study)), [])
            (study / "harness" / "json.pyc").write_bytes(b"")
            (study / "adapter" / "fast.cpython-38-x86_64-linux-gnu.so").write_bytes(b"")
            (study / "harness" / "os.py").write_text("")
            (study / "harness" / "securesystemslib.py").write_text("")
            (study / "adapter" / "pkg").mkdir()
            os.symlink("cells.py", study / "harness" / "link.py")
            problems = guard.shadow_problems(str(study))
            for needle in ("json.pyc", "fast.cpython", "os.py shadows", "securesystemslib.py shadows", "adapter/pkg is a directory", "link.py is a symbolic link"):
                self.assertTrue(any(needle in p for p in problems), (needle, problems))
            self.assertEqual(guard.path_problems(str(STUDY)), [])
            sys.path.append("/elsewhere/injected")
            try:
                self.assertTrue(any("injected" in p for p in guard.path_problems(str(STUDY))))
            finally:
                sys.path.remove("/elsewhere/injected")
            os.environ["PYTHONPATH"] = "/elsewhere"
            try:
                self.assertTrue(any("PYTHONPATH" in p for p in guard.path_problems(str(STUDY))))
            finally:
                del os.environ["PYTHONPATH"]
            with self.assertRaises(SystemExit):
                guard.establish(str(study))

    def test_the_environment_scan_refuses_unrecorded_entries(self):
        self.assertEqual(guard.environment_problems(), [], "the pinned environment holds nothing unrecorded")
        with tempfile.TemporaryDirectory() as a:
            site = Path(a) / "site-packages"
            (site / "pkg").mkdir(parents=True)
            (site / "pkg" / "__init__.py").write_text("")
            (site / "pkg" / "mod.py").write_text("")
            (site / "pkg-1.0.dist-info").mkdir()
            (site / "pkg-1.0.dist-info" / "METADATA").write_text("Metadata-Version: 2.1\nName: pkg\nVersion: 1.0\n\n")
            (site / "pkg-1.0.dist-info" / "RECORD").write_text("pkg/__init__.py,sha256=x,0\npkg/mod.py,sha256=x,0\npkg-1.0.dist-info/METADATA,,\n"
                                                                 "pkg-1.0.dist-info/RECORD,,\n\"pkg/odd,name.py\",sha256=x,0\n../../bin/tool,sha256=x,0\n")
            (site / "pkg" / "odd,name.py").write_text("")
            (site / "pkg" / "__pycache__").mkdir()
            (site / "pkg" / "__pycache__" / "mod.cpython-38.pyc").write_bytes(b"")
            saved_path, saved_prefix = list(sys.path), sys.prefix
            sys.path.append(str(site))
            sys.prefix = a
            try:
                self.assertEqual(guard.environment_problems(), [])
                (site / "pkg" / "mod").mkdir()  # the round-4 route: a package directory the import system prefers to mod.py
                (site / "pkg" / "mod" / "__init__.py").write_text("")
                problems = guard.environment_problems()
                self.assertTrue(any(p.endswith("mod is a directory no installed distribution records a file under") for p in problems), problems)
                self.assertTrue(any("mod/__init__.py is not a file" in p for p in problems), problems)
                (site / "pkg" / "extra.py").write_text("")
                (site / "hook.pth").write_text("")
                (site / "loose.pyc").write_bytes(b"")
                os.symlink("pkg", site / "alias")
                (site / "zz_overlay-0.dist-info").mkdir()  # the round-5 route: a second metadata directory claiming the same name
                (site / "zz_overlay-0.dist-info" / "METADATA").write_text("Metadata-Version: 2.1\nName: Pkg\nVersion: 0\n\n")
                (site / "zz_overlay-0.dist-info" / "RECORD").write_text("pkg/__init__.py,sha256=x,0\npkg/mod/__init__.py,sha256=x,0\nzz_overlay-0.dist-info/RECORD,,\nzz_overlay-0.dist-info/METADATA,,\n")
                problems = guard.environment_problems()
                self.assertTrue(any("claims the distribution name 'pkg'" in p for p in problems), problems)
                self.assertTrue(any("mod/__init__.py is not a file" in p for p in problems), "the overlay's record grants nothing")
                dists, inventory_problems = pinning.inventory()
                self.assertTrue(any("two metadata directories claim the distribution name 'pkg'" in p for p in inventory_problems), inventory_problems)
                self.assertNotIn("pkg", dists, "a duplicated name supplies neither hashing nor ownership")
                shutil.rmtree(site / "zz_overlay-0.dist-info")
                os.unlink(site / "pkg" / "mod.py")
                os.symlink("../hook.pth", site / "pkg" / "mod.py")  # a recorded path that is now a link elsewhere
                problems = guard.environment_problems()
                for needle in ("extra.py is not a file", "hook.pth is not a file", "loose.pyc is not a file", "alias is a symbolic link", "pkg/mod.py is a symbolic link"):
                    self.assertTrue(any(needle in p for p in problems), (needle, problems))
                with self.assertRaisesRegex(SystemExit, "installed distribution"):
                    guard.establish(str(STUDY))
                # the same refusal at check time, through the pins
                self.assertTrue(any("no installed distribution records" in p for p in pinning.execution_problems(pinning.load())))
            finally:
                sys.path[:] = saved_path
                sys.prefix = saved_prefix
        self.assertEqual(guard.site_problems(), [])
        sys.modules["sitecustomize"] = __import__("types").ModuleType("sitecustomize")
        try:
            self.assertTrue(guard.site_problems())
        finally:
            del sys.modules["sitecustomize"]

    def test_the_execution_check_is_repeated_after_the_layers_ran(self):
        # the layer runner refuses to write observations when the code that ran the layers is not the pinned code
        original = run_layers.pinning.execution_problems
        run_layers.pinning.execution_problems = lambda pins: ["late problem"]
        saved = sys.argv
        with tempfile.TemporaryDirectory() as a:
            cells_dir = Path(a) / "cells"
            constructions.build("pos-baseline", cells_dir)
            fake = Path(a) / "gateway"
            fake.write_text('#!/bin/sh\nprintf \'{"ok":true,"findings":[{"callIndex":0,"sessionId":"s2","status":"ok"},{"callIndex":1,"sessionId":"s2","status":"ok"}]}\'\n')
            fake.chmod(0o755)
            sys.argv = ["run_layers.py", "--cells", str(cells_dir), "--gateway", str(fake), "--out", str(Path(a) / "obs.json")]
            try:
                with self.assertRaisesRegex(RuntimeError, "late problem"):
                    run_layers.main()
                self.assertFalse((Path(a) / "obs.json").exists())
            finally:
                run_layers.pinning.execution_problems = original
                sys.argv = saved

    def test_names_normalize_as_pep_503_and_an_empty_name_grants_nothing(self):
        for raw in ("Foo.Bar", "foo--bar", "foo__bar", "FOO_.-bar"):
            self.assertEqual(guard.normalized(raw), "foo-bar", raw)
            self.assertEqual(pinning.normalized(raw), "foo-bar", raw)
        with tempfile.TemporaryDirectory() as a:
            site = Path(a) / "site-packages"
            for dist, name in (("a-1.dist-info", "Foo.Bar"), ("b-1.dist-info", "foo--bar"), ("c-1.dist-info", "")):
                (site / dist).mkdir(parents=True)
                (site / dist / "METADATA").write_text("Metadata-Version: 2.1\nName: %s\nVersion: 1\n\n" % name)
                (site / dist / "RECORD").write_text("%s/METADATA,,\n%s/RECORD,,\nplanted_%s.py,sha256=x,0\n" % (dist, dist, dist[0]))
                (site / ("planted_%s.py" % dist[0])).write_text("")
            saved_path, saved_prefix = list(sys.path), sys.prefix
            sys.path.append(str(site))
            sys.prefix = a
            try:
                problems = guard.environment_problems()
                self.assertTrue(any("b-1.dist-info claims the distribution name 'foo-bar'" in p for p in problems), problems)
                self.assertTrue(any("c-1.dist-info declares no distribution name" in p for p in problems), problems)
                self.assertTrue(any("planted_b.py is not a file" in p for p in problems), "an equivalent name grants nothing")
                self.assertTrue(any("planted_c.py is not a file" in p for p in problems), "an empty name grants nothing")
                dists, inventory_problems = pinning.inventory()
                self.assertTrue(any("two metadata directories claim the distribution name 'foo-bar'" in p for p in inventory_problems), inventory_problems)
                self.assertTrue(any("declares no distribution name" in p for p in inventory_problems), inventory_problems)
                self.assertNotIn("foo-bar", dists)
            finally:
                sys.path[:] = saved_path
                sys.prefix = saved_prefix

    def test_package_bytes_are_authenticated_before_any_import(self):
        from importlib import metadata
        self.assertEqual(guard.package_problems(str(STUDY)), [], "the real environment hashes to its pins, by the guard's own computation")
        # the guard's digest is the digest harness/pins.py computes
        dists, _ = pinning.inventory()
        pins = pinning.load()
        for name, dist in dists.items():
            root = str(Path(dist._path).parent)
            self.assertEqual(guard._package_digest(root, str(Path(dist._path) / "RECORD")), pinning.package_digest(dist)[1], name)
            self.assertEqual(pinning.package_digest(dist)[1], pins["intoto"]["packages"][[k for k in pins["intoto"]["packages"] if pinning.normalized(k) == name][0]]["installedDigest"])
        with tempfile.TemporaryDirectory() as a:
            site = Path(a) / "site-packages"
            (site / "pkg").mkdir(parents=True)
            (site / "pkg" / "__init__.py").write_text("VALUE = 1\n")
            (site / "pkg-1.0.dist-info").mkdir()
            (site / "pkg-1.0.dist-info" / "METADATA").write_text("Metadata-Version: 2.1\nName: pkg\nVersion: 1.0\n\n")
            (site / "pkg-1.0.dist-info" / "RECORD").write_text("pkg/__init__.py,sha256=x,0\npkg-1.0.dist-info/METADATA,,\npkg-1.0.dist-info/RECORD,,\n")
            digest = guard._package_digest(str(site), str(site / "pkg-1.0.dist-info" / "RECORD"))
            fake_pins = {"intoto": {"packages": {"pkg": {"version": "1.0", "installedDigest": digest}}}}
            self.assertEqual(guard.package_problems(str(STUDY), fake_pins, [str(site)]), [])
            # the round-6 arrangement: a recorded initializer altered in place, metadata and RECORD unchanged
            with open(site / "pkg" / "__init__.py", "a") as f:
                f.write("import pins as _p\n")
            problems = guard.package_problems(str(STUDY), fake_pins, [str(site)])
            self.assertTrue(any("pkg" in p and "do not hash to the pinned digest" in p for p in problems), problems)
            (site / "pkg" / "__init__.py").write_text("VALUE = 1\n")
            self.assertTrue(any("not pinned" in p for p in guard.package_problems(str(STUDY), {"intoto": {"packages": {}}}, [str(site)])))
            self.assertTrue(any("is not installed" in p for p in guard.package_problems(str(STUDY), {"intoto": {"packages": {"other": {"installedDigest": "x"}}}}, [str(site)])))
            self.assertTrue(any("no pinned digest" in p for p in guard.package_problems(str(STUDY), {"intoto": {"packages": {"pkg": {"installedDigest": None}}}}, [str(site)])))
            # a fresh-process equivalent: the guard, pointed at that environment alone, refuses before anything could be imported
            saved_path, saved_prefix = list(sys.path), sys.prefix
            sys.path[:] = [e for e in saved_path if not e.startswith(saved_prefix)] + [str(site)]
            sys.prefix = a
            with open(site / "pkg" / "__init__.py", "a") as f:
                f.write("import pins as _p\n")
            try:
                with self.assertRaisesRegex(SystemExit, "hash|not pinned|installed"):
                    guard.establish(str(STUDY))
            finally:
                sys.path[:] = saved_path
                sys.prefix = saved_prefix

    def test_study_modules_are_authenticated_against_the_manifest_before_import(self):
        import make_manifest
        self.assertEqual(guard.study_module_problems(str(STUDY)), [])
        with tempfile.TemporaryDirectory() as a:
            study = Path(a)
            for d in ("adapter", "harness", "harness/tests", "fixtures/baseline"):
                (study / d).mkdir(parents=True)
            (study / "harness" / "cells.py").write_text("X = 1\n")
            (study / "adapter" / "SPEC.md").write_text("spec\n")
            (study / "harness" / "STUDY-MANIFEST.sha256").write_text(make_manifest.render(study))
            pins = {"freeze": {"studyManifest": None}, "intoto": {"packages": {}}}
            self.assertEqual(guard.study_module_problems(str(study), pins), [])
            (study / "harness" / "cells.py").write_text("X = 2\n")
            self.assertTrue(any("harness/cells.py does not hash" in p for p in guard.study_module_problems(str(study), pins)))
            (study / "harness" / "cells.py").write_text("X = 1\n")
            (study / "harness" / "extra.py").write_text("")
            self.assertTrue(any("harness/extra.py is a study module the manifest does not list" in p for p in guard.study_module_problems(str(study), pins)))
            (study / "harness" / "extra.py").unlink()
            pinned = dict(pins, freeze={"studyManifest": "0" * 64})
            self.assertTrue(any("freeze pin" in p for p in guard.study_module_problems(str(study), pinned)))
            import hashlib
            pinned = dict(pins, freeze={"studyManifest": hashlib.sha256((study / "harness" / "STUDY-MANIFEST.sha256").read_bytes()).hexdigest()})
            self.assertEqual(guard.study_module_problems(str(study), pinned), [])

    def test_the_manifest_refuses_an_importable_non_source_file(self):
        import make_manifest
        with tempfile.TemporaryDirectory() as a:
            study = Path(a)
            for d in ("adapter", "harness", "harness/tests", "fixtures/baseline"):
                (study / d).mkdir(parents=True)
            (study / "harness" / "cells.py").write_text("")
            (study / "adapter" / "SPEC.md").write_text("")
            self.assertIn("harness/cells.py", make_manifest.covered_paths(study))
            (study / "harness" / "__pycache__").mkdir()
            (study / "harness" / "__pycache__" / "cells.cpython-38.pyc").write_bytes(b"")  # never consulted; not covered, not refused
            self.assertNotIn("harness/__pycache__/cells.cpython-38.pyc", make_manifest.covered_paths(study))
            (study / "harness" / "json.pyc").write_bytes(b"")
            with self.assertRaisesRegex(SystemExit, "importable"):
                make_manifest.covered_paths(study)

    def test_the_dependency_and_interpreter_pins_are_enforced(self):
        pins = pinning.load()
        self.assertEqual(sorted(pins["intoto"]["packages"]), ["cffi", "cryptography", "in-toto-attestation", "protobuf", "pycparser", "securesystemslib", "typing_extensions"])
        from importlib import metadata
        self.assertEqual(sorted(d.metadata["Name"] for d in metadata.distributions()), sorted(pins["intoto"]["packages"]), "the environment holds exactly the pinned distributions")
        self.assertEqual(pins["harnessPython"]["version"], sys.version.split()[0])
        wrong = json.loads(json.dumps(pins))
        wrong["harnessPython"]["version"] = "0.0.0"
        self.assertTrue(any("interpreter" in p for p in pinning.problems(wrong, None)))

    def test_marker_validation(self):
        root = STUDY / "results" / "primary-attempt-001"
        m = {"attemptId": "a" * 32, "attemptRoot": str(root), "label": "REGISTERED", "gatewaySha256": "x",
             "pinsRawSha256": pinning.raw_sha256(), "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0],
             "cells": sorted(constructions.ALL_CELLS), "startedAt": "t"}
        self.assertEqual(score.marker_problems(m, "x", "REGISTERED", root), [])
        self.assertTrue(score.marker_problems(m, "x", "REGISTERED", "/elsewhere"), "the marker's root must be the root being scored")
        self.assertTrue(score.marker_problems(dict(m, label="PILOT"), "x", "REGISTERED", root))
        self.assertTrue(score.marker_problems(dict(m, cells=sorted(constructions.CELLS)), "x", "REGISTERED", root), "a registered marker names both strata")
        self.assertTrue(score.marker_problems(dict(m, attemptRoot="/elsewhere"), "x", "REGISTERED", "/elsewhere"), "a registered root is the literal one")
        self.assertTrue(score.marker_problems(dict(m, python="0.0.0"), "x", "REGISTERED", root))
        self.assertTrue(score.marker_problems(dict(m, attemptId="z" * 3), "x", "REGISTERED", root))
        pilot = dict(m, label="PILOT", attemptRoot="/anywhere", cells=sorted(constructions.CELLS))
        self.assertEqual(score.marker_problems(pilot, "x", "PILOT", "/anywhere"), [], "a pilot may run anywhere, over the locked stratum")
        self.assertTrue(score.marker_problems(pilot, "x", "PILOT", "/elsewhere"))

    def test_a_registered_runner_and_scorer_refuse_another_root(self):
        for script in ("run_attempt.py", "score.py"):
            r = subprocess.run([sys.executable, str(STUDY / "harness" / script), "--attempt-root", "/tmp/not-the-root", "--gateway", "/nonexistent"],
                               capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0, script)
            self.assertIn("results/primary-attempt-001", r.stderr, script)

    def test_the_terminal_record_is_written_once_and_a_failure_to_write_is_reported(self):
        with tempfile.TemporaryDirectory() as a:
            run_attempt.terminal(Path(a), {"decision": "pipeline-invalid"})
            self.assertEqual(json.loads((Path(a) / "ADJUDICATION.json").read_text())["decision"], "pipeline-invalid")
            import io
            from contextlib import redirect_stderr
            buf = io.StringIO()
            with redirect_stderr(buf):
                run_attempt.terminal(Path(a), {"decision": "other"})
            self.assertIn("could not be written", buf.getvalue())
            self.assertEqual(json.loads((Path(a) / "ADJUDICATION.json").read_text())["decision"], "pipeline-invalid")


class GatewayExit(unittest.TestCase):
    def test_the_gateway_argument_is_resolved_to_one_file_not_searched_on_path(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            here, elsewhere = Path(a) / "here", Path(a) / "elsewhere"
            here.mkdir()
            elsewhere.mkdir()
            (here / "gateway").write_text('#!/bin/sh\nprintf \'{"ok":true,"findings":[{"callIndex":0,"sessionId":"s2","status":"ok"}]}\'\n')
            (elsewhere / "gateway").write_text('#!/bin/sh\nprintf \'{"ok":false,"findings":[{"callIndex":0,"sessionId":"s2","status":"key-mismatch"}]}\'\n')
            for p in (here / "gateway", elsewhere / "gateway"):
                p.chmod(0o755)
            cwd, path = os.getcwd(), os.environ.get("PATH", "")
            os.chdir(here)
            os.environ["PATH"] = str(elsewhere)
            try:
                self.assertEqual(run_layers.resolved_gateway("gateway"), here / "gateway")
                self.assertTrue(run_layers.gateway_layer("gateway", cell)["ok"], "the file in the working directory, never the one PATH would find")
                self.assertEqual(pinning.sha256_file(run_layers.resolved_gateway("gateway")), pinning.sha256_file(here / "gateway"))
                with self.assertRaises(RuntimeError):
                    run_layers.resolved_gateway("no-such-gateway")
            finally:
                os.chdir(cwd)
                os.environ["PATH"] = path

    def test_a_nonzero_exit_is_no_verdict_even_with_a_verdict_on_stdout(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            fake = Path(a) / "fake-gateway"
            fake.write_text('#!/bin/sh\nprintf \'{"ok":true,"findings":[{"callIndex":0,"sessionId":"s2","status":"ok"}]}\'\nexit 2\n')
            fake.chmod(0o755)
            with self.assertRaises(RuntimeError):
                run_layers.gateway_layer(str(fake), cell)
            fake.write_text('#!/bin/sh\nprintf \'{"ok":true,"findings":[{"callIndex":0,"sessionId":"s2","status":"ok"}]}\'\nexit 0\n')
            self.assertTrue(run_layers.gateway_layer(str(fake), cell)["ok"])


@unittest.skipUnless(GATEWAY and Path(GATEWAY).is_file(), "set GATEWAY_BIN to the pinned gateway verifier")
class Layers(unittest.TestCase):
    def test_the_gateway_layer_reads_a_verdict_and_the_observation_is_reproducible(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            g = run_layers.gateway_layer(GATEWAY, cell)
            self.assertTrue(g["ok"])
            o = run_layers.observe(GATEWAY, cell)
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, trees.tree_digest(cell)), [])
            self.assertEqual(run_layers.observe(GATEWAY, cell), o)

    def test_a_duplicated_receipt_finding_is_refused_only_by_recomputation(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = run_layers.observe(GATEWAY, cell)
            o["gateway"]["findings"] = [dict(o["gateway"]["findings"][0]), dict(o["gateway"]["findings"][0])]
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, trees.tree_digest(cell)), [], "the shape is a legitimate one (a misfiled copy repeats a call index)")
            self.assertNotEqual(run_layers.observe(GATEWAY, cell), o, "the recomputation is what refuses it")

    def test_a_tampered_well_formed_observation_is_pipeline_invalid_end_to_end(self):
        """The reviewer's round-2 probe through the real pipeline: a pilot runs, its observations are re-shaped into a
        well-formed lie (an invented subject name), and the scorer refuses by recomputation."""
        with tempfile.TemporaryDirectory() as a:
            root = Path(a) / "pilot"
            subprocess.run([sys.executable, str(STUDY / "harness" / "run_attempt.py"), "--attempt-root", str(root), "--gateway", GATEWAY, "--pilot"],
                           check=True, capture_output=True, env=run_attempt.child_env())
            first = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(first["decision"], "R1 holds")
            (root / "ADJUDICATION.json").unlink()
            doc = json.loads((root / "OBSERVATIONS.json").read_text())
            first_observations = json.loads(json.dumps(doc))
            target = [o for o in doc["cells"] if o["cell"] == "pos-baseline"][0]
            target["intoto"]["attestations"][1]["subjects"] = [["invented", "match"]]
            (root / "OBSERVATIONS.json").write_text(json.dumps(doc, indent=1))
            r = subprocess.run([sys.executable, str(STUDY / "harness" / "score.py"), "--attempt-root", str(root), "--gateway", GATEWAY, "--pilot"],
                               capture_output=True, text=True, env=run_attempt.child_env())
            self.assertEqual(r.returncode, 0, r.stderr)
            second = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(second["decision"], "pipeline-invalid")
            self.assertTrue(any("not what the pinned apparatus produces" in v for v in second["validityFailures"]), second["validityFailures"])
            # the scorer resolves a relative gateway argument to one file in its working directory; a same-named decoy on PATH is never launched
            (root / "ADJUDICATION.json").unlink()
            (root / "OBSERVATIONS.json").write_text(json.dumps(first_observations, indent=1))
            here, decoy = Path(a) / "here", Path(a) / "decoy"
            here.mkdir()
            decoy.mkdir()
            shutil.copy2(GATEWAY, here / "gateway")
            (decoy / "gateway").write_text('#!/bin/sh\nprintf \'{"ok":true,"findings":[]}\'\n')
            (decoy / "gateway").chmod(0o755)
            env = dict(run_attempt.child_env(), PATH=str(decoy))
            r = subprocess.run([sys.executable, str(STUDY / "harness" / "score.py"), "--attempt-root", str(root), "--gateway", "gateway", "--pilot"],
                               capture_output=True, text=True, env=env, cwd=str(here))
            self.assertEqual(r.returncode, 0, r.stderr)
            third = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(third["decision"], "R1 holds", third["validityFailures"][:3])

    def test_a_gateway_refusal_is_not_a_verdict(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            shutil.rmtree(cell / "store" / "receipts")
            (cell / "store" / "receipts").write_text("not a directory")
            with self.assertRaises(RuntimeError):
                run_layers.gateway_layer(GATEWAY, cell)

    def test_a_failure_after_the_marker_leaves_a_terminal_record(self):
        with tempfile.TemporaryDirectory() as a:
            root = Path(a) / "attempt"
            original = run_attempt.constructions.build

            def failing(cid, out_root, registered=None):
                raise RuntimeError("construction failed on purpose")
            run_attempt.constructions.build = failing
            saved = sys.argv
            sys.argv = ["run_attempt.py", "--attempt-root", str(root), "--gateway", GATEWAY, "--pilot"]
            try:
                with self.assertRaises(RuntimeError):
                    run_attempt.main()
            finally:
                run_attempt.constructions.build = original
                sys.argv = saved
            marker = json.loads((root / "ATTEMPT.json").read_text())
            record = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(record["decision"], "pipeline-invalid")
            self.assertEqual(record["attemptId"], marker["attemptId"])
            self.assertIn("construction failed on purpose", record["validityFailures"][0])


if __name__ == "__main__":
    unittest.main()
