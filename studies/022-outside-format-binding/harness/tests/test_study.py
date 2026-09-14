"""Harness tests for Study 022. Run from the study root: python -m unittest discover -s harness/tests
(in the virtual environment that holds the pinned in-toto packages)."""
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
import score  # noqa: E402
import bind  # noqa: E402
import verify_attestation  # noqa: E402
import verify_binding  # noqa: E402

GATEWAY = os.environ.get("GATEWAY_BIN")


class Constructions(unittest.TestCase):
    def test_every_registered_cell_has_a_construction_and_builds_deterministically(self):
        matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text())
        ids = {c["id"] for c in matrix["cells"]}
        self.assertEqual(ids, set(constructions.CELLS))
        self.assertEqual(len(matrix["cells"]), len(ids))
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

    def test_every_construction_but_the_baseline_changes_something(self):
        with tempfile.TemporaryDirectory() as a:
            base = constructions.build("pos-baseline", a)
            for cid in constructions.CELLS:
                if cid == "pos-baseline":
                    continue
                self.assertFalse(score.same_tree(base, constructions.build(cid, a)), cid)


class Binding(unittest.TestCase):
    def test_the_baseline_binding_is_deterministic_and_verifies(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            bind.bind(STUDY / "fixtures" / "baseline" / "store", a)
            bind.bind(STUDY / "fixtures" / "baseline" / "store", b)
            self.assertTrue(score.same_tree(a, b))
            r = verify_attestation.verify(STUDY / "fixtures" / "baseline" / "store", a, STUDY / "fixtures" / "baseline" / "decisions")
            self.assertTrue(r["pass"], r)
            self.assertTrue(verify_binding.verify(STUDY / "fixtures" / "baseline" / "store", a)["pass"])
            self.assertTrue(score.same_tree(a, STUDY / "fixtures" / "baseline" / "attestations"), "the committed attestations are the adapter's binding of the committed store")

    def test_the_adapter_key_is_the_pinned_one(self):
        self.assertEqual(pinning.adapter_keyid(), pinning.load()["adapter"]["keyid"])


class Reduction(unittest.TestCase):
    def test_reduction_keeps_only_the_first_failure_per_attestation(self):
        o = {"cell": "x", "gateway": {"ok": True, "statuses": ["ok"], "findings": []},
             "intoto": {"pass": False, "attestations": [{"attestation": "s2/0.dsse.json", "dsse": "pass", "statement": "valid", "subjects": {"artifact": "match"}},
                                                        {"attestation": "s2/1.dsse.json", "dsse": "fail:signature", "statement": None, "subjects": {}}]},
             "binding": {"pass": True, "attestations": [{"attestation": "s2/0.dsse.json", "binding": "pass"}, {"attestation": "s2/1.dsse.json", "binding": "pass"}]},
             "combined": "fail"}
        r = score.reduce_observation(o)
        self.assertEqual(r["intoto"], {"pass": False, "failures": {"s2/1.dsse.json": "fail:signature"}})
        self.assertEqual(r["binding"], {"pass": True, "failures": {}})

    def test_an_incomplete_observation_is_refused(self):
        self.assertFalse(score.observation_ok({"cell": "x"}, "x"))


class Pins(unittest.TestCase):
    def test_a_wrong_gateway_binary_is_a_problem(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"not the gateway")
        self.assertTrue(any("gateway binary" in p for p in pinning.problems(pinning.load(), f.name)))

    def test_marker_validation(self):
        m = {"attemptId": "a" * 32, "label": "REGISTERED", "gatewaySha256": "x", "pinsRawSha256": pinning.raw_sha256(), "adapterKeyid": pinning.adapter_keyid(),
             "cells": sorted(constructions.CELLS), "startedAt": "t"}
        self.assertEqual(score.marker_problems(m, "x", "REGISTERED"), [])
        self.assertTrue(score.marker_problems(dict(m, label="PILOT"), "x", "REGISTERED"))
        self.assertTrue(score.marker_problems(dict(m, cells=["pos-baseline"]), "x", "REGISTERED"))
        self.assertTrue(score.marker_problems(dict(m, attemptId="z" * 32), "x", "REGISTERED"))


@unittest.skipUnless(GATEWAY and Path(GATEWAY).is_file(), "set GATEWAY_BIN to the pinned gateway verifier")
class Layers(unittest.TestCase):
    def test_the_gateway_layer_reads_a_verdict(self):
        import run_layers
        with tempfile.TemporaryDirectory() as a:
            cell = constructions.build("pos-baseline", a)
            g = run_layers.gateway_layer(GATEWAY, cell)
            self.assertTrue(g["ok"])


if __name__ == "__main__":
    unittest.main()
