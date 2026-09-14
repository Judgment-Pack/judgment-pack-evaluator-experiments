"""Harness tests for Study 022. Run from the study root, in the virtual environment that holds the pinned packages:
    python -m unittest discover -s harness/tests
The tests build the locked constructions only; no holdout cell is built here (PREREGISTRATION.md section 1a)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(STUDY / "adapter"))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402
import run_layers  # noqa: E402
import score  # noqa: E402
import bind  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

GATEWAY = os.environ.get("GATEWAY_BIN")
BASE = STUDY / "fixtures" / "baseline"
TRUSTED = verify_attestation.trusted_key(BASE / "attestations" / "adapter.pubkey.json")


def matrix_ids(name):
    return [c["id"] for c in score.load_matrix(STUDY / "harness" / name)]


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
                self.assertTrue(score.same_tree(Path(a) / cid, Path(b) / cid), cid)

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
                self.assertFalse(score.same_tree(base, constructions.build(cid, a)), cid)

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
            self.assertFalse(score.same_tree(a, b))

    def test_an_extra_directory_or_a_kind_change_is_not_the_same_tree(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(a) / "f").write_bytes(b"x")
            (Path(b) / "f").write_bytes(b"x")
            self.assertTrue(score.same_tree(a, b))
            (Path(b) / "__pycache__").mkdir()
            self.assertFalse(score.same_tree(a, b))

    def test_a_symbolic_link_is_refused(self):
        with tempfile.TemporaryDirectory() as a:
            (Path(a) / "f").write_bytes(b"x")
            os.symlink("f", Path(a) / "g")
            with self.assertRaises(RuntimeError):
                score.tree_map(a)
            with self.assertRaises(RuntimeError):
                run_layers.tree_digest(a)


class Binding(unittest.TestCase):
    def test_the_baseline_binding_is_deterministic_and_verifies(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            bind.bind(BASE / "store", a)
            bind.bind(BASE / "store", b)
            self.assertTrue(score.same_tree(a, b))
            r = verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)
            self.assertTrue(r["pass"], r)
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"])
            self.assertTrue(score.same_tree(a, BASE / "attestations"), "the committed attestations are the adapter's binding of the committed store")

    def test_the_adapter_key_is_the_pinned_one_and_the_fixture_file_carries_it(self):
        self.assertEqual(pinning.adapter_keyid(), pinning.load()["adapter"]["keyid"])
        self.assertEqual(pinning.trusted_pubkey_problems(pinning.load()), [])
        self.assertEqual(TRUSTED.keyid, pinning.load()["adapter"]["keyid"])


class Verifiers(unittest.TestCase):
    """Function-level tests of the round-1 fixes; they exercise the verifiers, not the holdout constructions."""

    def test_a_binding_under_a_foreign_key_is_untrusted_whatever_key_file_lies_beside_it(self):
        with tempfile.TemporaryDirectory() as a:
            bind.bind(BASE / "store", a, signer=constructions.foreign_signer())
            self.assertNotEqual(json.loads((Path(a) / "adapter.pubkey.json").read_text())["keyid"], TRUSTED.keyid)
            r = verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)
            self.assertFalse(r["pass"])
            self.assertEqual([x["dsse"] for x in r["attestations"]], ["fail:untrusted-key", "fail:untrusted-key"])
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"], "the binding layer reads no key")

    def test_the_key_file_beside_the_envelopes_is_not_consulted(self):
        with tempfile.TemporaryDirectory() as a:
            bind.bind(BASE / "store", a)
            (Path(a) / "adapter.pubkey.json").unlink()
            self.assertTrue(verify_attestation.verify(BASE / "store", a, BASE / "decisions", TRUSTED)["pass"])
            self.assertTrue(verify_binding.verify(BASE / "store", a)["pass"])

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

    def test_per_name_keeps_the_first_outcome_that_is_not_match(self):
        self.assertEqual(verify_attestation.per_name([["a", "match"], ["a", "missing"], ["a", "mismatch"], ["b", "match"]]), {"a": "missing", "b": "match"})
        self.assertEqual(verify_attestation.per_name([]), {})

    def test_malformed_payloads_get_codes_not_exceptions(self):
        from securesystemslib.dsse import Envelope
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p = constructions.envelope_path(cell, 1)
            cases = {
                b"[]": ("invalid:not-object", None),
                b"not json": ("invalid:not-json", None),
                bind.serialize({"_type": verify_attestation.STATEMENT_TYPE, "predicateType": verify_attestation.PREDICATE_TYPE, "subject": "no", "predicate": {"kind": "x"}}): ("invalid:bindings", None),
                bind.serialize({"_type": verify_attestation.STATEMENT_TYPE, "predicateType": verify_attestation.PREDICATE_TYPE, "subject": [{"name": "artifact", "digest": {"sha256": "0" * 64}}], "predicate": {}}): ("invalid:bindings", None),
                bind.serialize({"_type": verify_attestation.STATEMENT_TYPE, "predicateType": verify_attestation.PREDICATE_TYPE,
                                "subject": [{"name": "cites/x", "digest": {"sha256": "0" * 64}}, {"name": "cites/s2/0/1", "digest": {"sha256": "0" * 64}},
                                            {"name": "artifact", "digest": {"sha256": "0" * 64}}], "predicate": {"kind": "x"}}): ("valid", [["cites/x", "unknown-subject"], ["cites/s2/0/1", "unknown-subject"], ["artifact", "missing"]]),
                bind.serialize({"_type": verify_attestation.STATEMENT_TYPE, "predicateType": verify_attestation.PREDICATE_TYPE,
                                "subject": [{"name": "artifact", "digest": {"sha256": "0" * 64}, "extra": 1}], "predicate": {}}): ("invalid:bindings", None),
            }
            for payload, (statement_code, subjects) in cases.items():
                env = Envelope(payload, bind.PAYLOAD_TYPE, {})
                env.sign(bind.adapter_signer())
                p.write_text(json.dumps(env.to_dict()))
                r = verify_attestation.verify_one(p, TRUSTED, cell / "store", cell / "decisions")
                self.assertEqual(r["dsse"], "pass", payload)
                self.assertEqual(r["statement"], statement_code, payload)
                if subjects is not None:
                    self.assertEqual(r["subjects"], subjects)
                code = verify_binding.check_one(p, constructions.receipt_path(cell, 1))
                self.assertIn(code, verify_binding.CODES)
                self.assertNotEqual(code, "pass")

    def test_an_empty_subject_list_is_invalid_bindings_and_an_artifact_subject_mismatch(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            st = constructions.statement_of(cell, 1)
            st["subject"] = []
            constructions.resign(cell, 1, st)
            r = verify_attestation.verify_one(constructions.envelope_path(cell, 1), TRUSTED, cell / "store", cell / "decisions")
            self.assertEqual((r["dsse"], r["statement"]), ("pass", "invalid:bindings"))
            self.assertEqual(verify_binding.check_one(constructions.envelope_path(cell, 1), constructions.receipt_path(cell, 1)), "fail:artifact-subject-mismatch")

    def test_an_unreadable_file_is_not_an_outcome(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            p = constructions.envelope_path(cell, 1)
            p.unlink()
            p.mkdir()
            with self.assertRaises(OSError):
                verify_attestation.verify_one(p, TRUSTED, cell / "store", cell / "decisions")
            with self.assertRaises(OSError):
                verify_binding.check_one(p, constructions.receipt_path(cell, 1))


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
    return {"cell": cell.name, "cellSha256": run_layers.tree_digest(cell), "gateway": g, "intoto": i, "binding": b, "combined": "pass"}


class ObservationValidation(unittest.TestCase):
    def test_a_complete_observation_of_the_rebuilt_cell_has_no_problems(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = complete_observation(cell)
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, run_layers.tree_digest(cell)), [])

    def test_the_reviewers_synthetic_record_is_refused(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            o = {"cell": "pos-baseline", "cellSha256": run_layers.tree_digest(cell), "gateway": {"ok": True, "statuses": ["ok"], "findings": []},
                 "intoto": {"pass": True, "attestations": []}, "binding": {"pass": True, "attestations": []}, "combined": "pass"}
            problems = score.observation_problems(o, "pos-baseline", cell, run_layers.tree_digest(cell))
            self.assertTrue(any("statuses" in p for p in problems), problems)
            self.assertTrue(any("cover every stored receipt" in p for p in problems), problems)
            self.assertTrue(any("one per stored receipt" in p for p in problems), problems)

    def test_every_shortfall_is_a_problem(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            snap = run_layers.tree_digest(cell)
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
            def drop_attestation(o): o["intoto"]["attestations"].pop()
            def reorder(o): o["binding"]["attestations"].reverse()
            def bad_code(o): o["binding"]["attestations"][0]["binding"] = "fail:something-else"
            def bad_subject(o): o["intoto"]["attestations"][0]["subjects"] = {"artifact": "match"}
            def stale_snapshot(o): o["cellSha256"] = "0" * 64
            def other_cell(o): o["cell"] = "a01-artifact-edited"
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
            for fn in (flip_intoto, flip_binding, flip_gateway, flip_combined, bad_status, drop_finding, drop_attestation, reorder, bad_code,
                       bad_subject, stale_snapshot, other_cell, subjects_after_failed_statement, intoto_lie_with_consistent_combined,
                       binding_lie_with_consistent_combined, gateway_lie_with_consistent_combined):
                self.assertTrue(mutated(fn), fn.__name__)
            self.assertEqual(mutated(lambda o: None), [])


class Pins(unittest.TestCase):
    def test_a_wrong_gateway_binary_is_a_problem(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"not the gateway")
        self.assertTrue(any("gateway binary" in p for p in pinning.problems(pinning.load(), f.name)))

    def test_import_origins_are_checked(self):
        for name, module in (("securesystemslib", "securesystemslib"), ("in-toto-attestation", "in_toto_attestation"), ("cryptography", "cryptography"), ("protobuf", "google.protobuf")):
            self.assertEqual(pinning.import_origin_problems(name, module), [], name)
        self.assertTrue(pinning.import_origin_problems("securesystemslib", "json"), "a module outside the distribution's files is a problem")

    def test_the_dependency_and_interpreter_pins_are_enforced(self):
        pins = pinning.load()
        self.assertEqual(sorted(pins["intoto"]["packages"]), ["cryptography", "in-toto-attestation", "protobuf", "securesystemslib"])
        self.assertEqual(pins["harnessPython"]["version"], sys.version.split()[0])
        wrong = json.loads(json.dumps(pins))
        wrong["harnessPython"]["version"] = "0.0.0"
        self.assertTrue(any("interpreter" in p for p in pinning.problems(wrong, None)))

    def test_marker_validation(self):
        m = {"attemptId": "a" * 32, "attemptRoot": str(STUDY / "results" / "primary-attempt-001"), "label": "REGISTERED", "gatewaySha256": "x",
             "pinsRawSha256": pinning.raw_sha256(), "adapterKeyid": pinning.adapter_keyid(), "python": sys.version.split()[0],
             "cells": sorted(constructions.ALL_CELLS), "startedAt": "t"}
        self.assertEqual(score.marker_problems(m, "x", "REGISTERED"), [])
        self.assertTrue(score.marker_problems(dict(m, label="PILOT"), "x", "REGISTERED"))
        self.assertTrue(score.marker_problems(dict(m, cells=sorted(constructions.CELLS)), "x", "REGISTERED"), "a registered marker names both strata")
        self.assertTrue(score.marker_problems(dict(m, attemptRoot="/elsewhere"), "x", "REGISTERED"))
        self.assertTrue(score.marker_problems(dict(m, python="0.0.0"), "x", "REGISTERED"))
        self.assertTrue(score.marker_problems(dict(m, attemptId="z" * 32), "x", "REGISTERED"))
        pilot = dict(m, label="PILOT", attemptRoot="/anywhere", cells=sorted(constructions.CELLS))
        self.assertEqual(score.marker_problems(pilot, "x", "PILOT"), [], "a pilot may run anywhere, over the locked stratum")

    def test_a_registered_runner_refuses_another_root(self):
        r = subprocess.run([sys.executable, str(STUDY / "harness" / "run_attempt.py"), "--attempt-root", "/tmp/not-the-root", "--gateway", "/nonexistent"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("a registered attempt's root is", r.stderr)


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
    def test_the_gateway_layer_reads_a_verdict(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            g = run_layers.gateway_layer(GATEWAY, cell)
            self.assertTrue(g["ok"])
            o = run_layers.observe(GATEWAY, cell)
            self.assertEqual(score.observation_problems(o, "pos-baseline", cell, run_layers.tree_digest(cell)), [])

    def test_a_gateway_refusal_is_not_a_verdict(self):
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            import shutil
            shutil.rmtree(cell / "store" / "receipts")
            (cell / "store" / "receipts").write_text("not a directory")
            with self.assertRaises(RuntimeError):
                run_layers.gateway_layer(GATEWAY, cell)


if __name__ == "__main__":
    unittest.main()
