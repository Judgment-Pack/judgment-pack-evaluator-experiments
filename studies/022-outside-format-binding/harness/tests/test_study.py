"""Harness tests for Study 022. Run from the study root, in the virtual environment that holds the pinned packages:
    python -m unittest discover -s harness/tests
The tests build the locked constructions only. Three tests in class Verifiers perform, on a copy of the baseline, the
edits the reviewer's holdout cells h01, h02 and h06 specify and assert the adapter layers' outcomes (disclosed in
PREREGISTRATION.md section 1a); no holdout cell is built through harness/cells.py here."""
import sys
import tempfile

# the study's bytecode policy (PREREGISTRATION.md section 2), before any study or pinned-package import
sys.dont_write_bytecode = True
if not sys.pycache_prefix:
    sys.pycache_prefix = tempfile.mkdtemp(prefix="study022-pycache-")

import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
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
                constructions.RegisteredContext(a)  # not the literal root
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

    def test_import_origins_and_execution_identity_are_checked(self):
        pins = pinning.load()
        self.assertEqual(pinning.execution_problems(pins), [])
        for name, module in pinning.PACKAGE_MODULES:
            self.assertEqual(pinning.import_origin_problems(name, module), [], name)
        self.assertTrue(pinning.import_origin_problems("securesystemslib", "json"), "a module outside the distribution's files is a problem")
        # a module claiming to be part of a pinned package but loaded from elsewhere, from a cache, or by another loader
        import types
        fake = types.ModuleType("securesystemslib.planted")
        fake.__file__ = "/elsewhere/planted.py"
        sys.modules["securesystemslib.planted"] = fake
        try:
            self.assertTrue(any("planted" in p for p in pinning.execution_problems(pins)))
            genuine = sys.modules["securesystemslib.dsse"]
            fake.__file__, fake.__spec__ = genuine.__file__, None
            fake.__loader__ = object()
            self.assertTrue(any("planted" in p and "loaded by" in p for p in pinning.execution_problems(pins)))
            fake.__loader__ = genuine.__loader__
            fake.__cached__ = "/elsewhere/__pycache__/dsse.cpython-38.pyc"
            self.assertTrue(any("planted" in p and "cache" in p for p in pinning.execution_problems(pins)))
        finally:
            del sys.modules["securesystemslib.planted"]
        self.assertEqual(pinning.execution_problems(pins), [])
        with tempfile.TemporaryDirectory() as a:
            saved = sys.pycache_prefix
            try:
                sys.pycache_prefix = a
                (Path(a) / "x.pyc").write_bytes(b"")
                self.assertTrue(any("must be empty" in p for p in pinning.execution_problems(pins)))
                sys.pycache_prefix = None
                self.assertTrue(any("no bytecode cache prefix" in p for p in pinning.execution_problems(pins)))
            finally:
                sys.pycache_prefix = saved
        wrong = json.loads(json.dumps(pins))
        wrong["harnessPython"]["implementation"] = "PyPy"
        self.assertTrue(any("interpreter is CPython" in p for p in pinning.execution_problems(wrong)))

    def test_the_dependency_and_interpreter_pins_are_enforced(self):
        pins = pinning.load()
        self.assertEqual(sorted(pins["intoto"]["packages"]), ["cryptography", "in-toto-attestation", "protobuf", "securesystemslib"])
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
                           check=True, capture_output=True, env=run_attempt.CHILD_ENV)
            first = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(first["decision"], "R1 holds")
            (root / "ADJUDICATION.json").unlink()
            doc = json.loads((root / "OBSERVATIONS.json").read_text())
            target = [o for o in doc["cells"] if o["cell"] == "pos-baseline"][0]
            target["intoto"]["attestations"][1]["subjects"] = [["invented", "match"]]
            (root / "OBSERVATIONS.json").write_text(json.dumps(doc, indent=1))
            r = subprocess.run([sys.executable, str(STUDY / "harness" / "score.py"), "--attempt-root", str(root), "--gateway", GATEWAY, "--pilot"],
                               capture_output=True, text=True, env=run_attempt.CHILD_ENV)
            self.assertEqual(r.returncode, 0, r.stderr)
            second = json.loads((root / "ADJUDICATION.json").read_text())
            self.assertEqual(second["decision"], "pipeline-invalid")
            self.assertTrue(any("not what the pinned apparatus produces" in v for v in second["validityFailures"]), second["validityFailures"])

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
