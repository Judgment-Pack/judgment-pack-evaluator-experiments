"""Harness tests: the pieces that must hold before any cell is read.

Run from the study root: python -m unittest discover -s harness/tests
The ledger tests need the pinned runtime on PATH (or JPACK set); they are
skipped, and say so, when it is absent.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_ledgers  # noqa: E402
import plant  # noqa: E402
import replay  # noqa: E402
import score  # noqa: E402
import jp  # noqa: E402

STUDY = HERE.parent.parent
def pinned_runtime_present():
    """The ledger tests run only under the pinned runtime version, never another."""
    if shutil.which(jp.JPACK) is None and not Path(jp.JPACK).is_file():
        return False
    try:
        import subprocess
        out = subprocess.run([jp.JPACK, "version"], capture_output=True, text=True).stdout
    except OSError:
        return False
    pins = json.loads((HERE.parent / "PINS.json").read_text())
    return pins["jpack"]["version"] in out


HAVE_JPACK = pinned_runtime_present()


def profile(entries):
    """A profile carrying one threshold entry per (pointer, literal, below, at, above)."""
    return {"thresholds": [{"pointer": p, "literal": l, "origins": [{"origin": "o", "below": {"rows": b, "disagreeing": b},
                                                                       "at": {"rows": a, "disagreeing": a},
                                                                       "above": {"rows": v, "disagreeing": v}}]}
                           for (p, l, b, a, v) in entries]}


class SignatureRule(unittest.TestCase):
    def test_one_pointer_one_side_is_the_signature(self):
        self.assertTrue(replay.signature(profile([("/x", "10", 3, 0, 0)]))["lineMoved"])
        self.assertTrue(replay.signature(profile([("/x", "10", 0, 0, 2)]))["lineMoved"])

    def test_a_row_at_the_literal_breaks_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 0, 1, 0)]))["lineMoved"])
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 1, 0)]))["lineMoved"])

    def test_both_sides_break_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 2)]))["lineMoved"])

    def test_two_literals_of_one_pointer_read_per_pointer(self):
        # the moved literal is one-sided while the mirror literal is not: the signature holds
        self.assertTrue(replay.signature(profile([("/x", "10", 0, 1, 1), ("/x", "12", 2, 0, 0)]))["lineMoved"])

    def test_two_pointers_disagreeing_break_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 0), ("/y", "5", 1, 0, 0)]))["lineMoved"])

    def test_no_threshold_carries_none(self):
        self.assertFalse(replay.signature({"thresholds": []})["applicable"])
        self.assertFalse(replay.signature(None)["applicable"])

    def test_no_disagreement_is_not_a_signature(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 0, 0, 0)]))["lineMoved"])


class Intervals(unittest.TestCase):
    def test_clopper_pearson_known_values(self):
        lo, hi = score.clopper_pearson(0, 30)
        self.assertEqual(lo, 0.0); self.assertAlmostEqual(hi, 0.1157, places=3)
        lo, hi = score.clopper_pearson(30, 30)
        self.assertAlmostEqual(lo, 0.8843, places=3); self.assertEqual(hi, 1.0)
        lo, hi = score.clopper_pearson(15, 30)
        self.assertAlmostEqual(lo, 0.3130, places=3); self.assertAlmostEqual(hi, 0.6870, places=3)

    def test_empty_is_none(self):
        self.assertIsNone(score.clopper_pearson(0, 0))


class Planting(unittest.TestCase):
    def test_every_policy_yields_instances_and_moves_are_at_least_a_unit(self):
        for f in sorted((STUDY / "fixtures" / "policies").glob("*.pack.json")):
            pack = json.loads(f.read_text())
            inst = plant.instances(pack)
            self.assertTrue(inst, f.name)
            for i in inst:
                self.assertNotEqual(json.dumps(i["pack"], sort_keys=True), json.dumps(pack, sort_keys=True), i["site"])
        self.assertEqual(plant.moved("250000", "0.25"), "312500")
        self.assertEqual(plant.moved("250000", "-0.25"), "187500")
        self.assertEqual(plant.moved("1", "0.25"), "2")
        self.assertEqual(plant.moved("0", "-0.25"), "-1")
        self.assertEqual(plant.moved("42.50", "0.25"), "53.12")  # a quarter of 42.50 is 10.625: half-even at the authored precision


class Adjudication(unittest.TestCase):
    def cells(self):
        return {"p": [
            {"defect": "D1-00", "class": "D1", "ledger": "random-50-1", "caught": True, "signature": {"applicable": True, "lineMoved": True}},
            {"defect": "D1-00", "class": "D1", "ledger": "random-50-2", "caught": True, "signature": {"applicable": True, "lineMoved": False}},
            {"defect": "D1-00", "class": "D1", "ledger": "random-50-3", "caught": False, "signature": {"applicable": True, "lineMoved": False}},
        ]}

    def test_endpoints_observe_fractions(self):
        got = score.observe(self.cells(), {"policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught"})
        self.assertAlmostEqual(got["observed"], 2 / 3, places=3)
        got = score.observe(self.cells(), {"policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "lineMovedWhenCaught"})
        self.assertEqual(got["observed"], 0.5)

    def test_divergence_is_named(self):
        matrix = {"cells": [{"id": "c", "policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught", "expected": {"min": 1, "max": 1}}]}
        rows = score.adjudicate(matrix, self.cells())
        self.assertEqual(rows[0]["verdict"], "diverges")


@unittest.skipUnless(HAVE_JPACK, "the pinned runtime version is not on PATH; set JPACK")
class Ledgers(unittest.TestCase):
    def test_random_ledgers_are_deterministic_and_applicable(self):
        pack, base = build_ledgers.load_policy("sanctions-screening")
        with tempfile.TemporaryDirectory() as tmp:
            root = jp.project(tmp, "sanctions-screening", pack)
            a, _ = build_ledgers.random_ledger("sanctions-screening", pack, base, root, 5, 1)
            b, _ = build_ledgers.random_ledger("sanctions-screening", pack, base, root, 5, 1)
            self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
            self.assertEqual(len(a["cases"]), 5)

    def test_the_unplanted_pack_replays_its_own_ledger_clean(self):
        pack, base = build_ledgers.load_policy("sanctions-screening")
        with tempfile.TemporaryDirectory() as tmp:
            root = jp.project(tmp, "sanctions-screening", pack)
            ledger, _ = build_ledgers.random_ledger("sanctions-screening", pack, base, root, 8, 2)
        r = replay.replay("sanctions-screening", pack, ledger)
        self.assertFalse(r["caught"], r)


if __name__ == "__main__":
    unittest.main()
