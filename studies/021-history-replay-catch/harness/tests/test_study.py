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
    """A profile carrying one threshold entry per (pointer, literal, below, at, above), for origin "o"."""
    return {"thresholds": [{"pointer": p, "literal": l, "origins": [{"origin": "o", "below": {"rows": b, "disagreeing": b},
                                                                       "at": {"rows": a, "disagreeing": a},
                                                                       "above": {"rows": v, "disagreeing": v}}]}
                           for (p, l, b, a, v) in entries]}


class SignatureRule(unittest.TestCase):
    def test_one_pointer_one_side_is_the_signature(self):
        self.assertTrue(replay.signature(profile([("/x", "10", 3, 0, 0)]), 3)["lineMoved"])
        self.assertTrue(replay.signature(profile([("/x", "10", 0, 0, 2)]), 2)["lineMoved"])

    def test_an_unplaced_mismatch_breaks_it(self):
        # three rows mismatched, two placed below: the third sits in no bucket
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 0)]), 3)["lineMoved"])
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 0)]))["lineMoved"])

    def test_a_row_at_the_literal_breaks_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 0, 1, 0)]), 1)["lineMoved"])
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 1, 0)]), 3)["lineMoved"])

    def test_both_sides_break_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 2)]), 4)["lineMoved"])

    def test_two_literals_of_one_pointer_read_per_pointer(self):
        # the moved literal is one-sided while the mirror literal is not: the signature holds
        self.assertTrue(replay.signature(profile([("/x", "10", 0, 1, 1), ("/x", "12", 2, 0, 0)]), 2)["lineMoved"])

    def test_two_pointers_disagreeing_break_it(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 2, 0, 0), ("/y", "5", 1, 0, 0)]), 2)["lineMoved"])

    def test_no_threshold_carries_none(self):
        # the runtime omits `thresholds` for a pack that draws no line; the pack must draw none
        sig = replay.signature({"agreement": []}, 2, expected=0)
        self.assertFalse(sig["applicable"])
        self.assertEqual(sig["thresholdEntries"], 0)
        with self.assertRaises(RuntimeError):
            replay.signature({"agreement": []}, 2, expected=1)
        with self.assertRaises(RuntimeError):
            replay.signature(profile([("/x", "10", 1, 0, 0)]), 1, expected=2)

    def test_expected_thresholds_counts_distinct_ordered_literals(self):
        packs = {f.name: json.loads(f.read_text()) for f in (STUDY / "fixtures" / "policies").glob("*.pack.json")}
        self.assertEqual(replay.expected_thresholds(packs["data-request-intake-triage.pack.json"]), 0)
        self.assertEqual(replay.threshold_boundaries(packs["vendor-onboarding.pack.json"]), {("/engagement/annualSpendUsd", "250000")})
        self.assertEqual(replay.expected_thresholds(packs["vendor-onboarding.pack.json"]), 1)  # two sites, one literal
        self.assertEqual(replay.expected_thresholds(packs["expense-approval.pack.json"]), 1)
        self.assertEqual(replay.expected_thresholds(packs["sanctions-screening.pack.json"]), 1)

    def test_no_disagreement_is_not_a_signature(self):
        self.assertFalse(replay.signature(profile([("/x", "10", 0, 0, 0)]), 0)["lineMoved"])


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


class RegisteredCells(unittest.TestCase):
    def test_every_registered_defect_is_one_the_planter_yields(self):
        matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text())
        ids = {}
        for f in sorted((STUDY / "fixtures" / "policies").glob("*.pack.json")):
            pack = json.loads(f.read_text())
            ids[f.name.replace(".pack.json", "")] = {"%s-%02d" % (i["class"], k) for k, i in enumerate(plant.instances(pack))}
        for c in matrix["cells"]:
            self.assertIn(c["policy"], ids)
            self.assertIn(c["defect"], ids[c["policy"]], c["id"])
            self.assertLessEqual(c["expected"]["min"], c["expected"]["max"], c["id"])
            self.assertIn(c["endpoint"], ("caught", "lineMovedWhenCaught"), c["id"])

    def test_cell_ids_are_unique(self):
        matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text())
        ids = [c["id"] for c in matrix["cells"]]
        self.assertEqual(len(ids), len(set(ids)))


class Adjudication(unittest.TestCase):
    def cells(self, caught=20, moved=10):
        out = []
        for seed in range(101, 131):
            k = seed - 101
            out.append({"defect": "D1-00", "class": "D1", "site": "s", "ledger": "random-50-%d" % seed, "caught": k < caught,
                        "signature": {"applicable": True, "lineMoved": k < moved}})
        return {"p": out}

    def test_endpoints_observe_fractions_over_the_complete_set(self):
        got = score.observe(self.cells(), {"policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught"})
        self.assertAlmostEqual(got["observed"], 20 / 30, places=3)
        got = score.observe(self.cells(), {"policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "lineMovedWhenCaught"})
        self.assertEqual(got["observed"], 0.5)

    def test_an_incomplete_set_is_unobserved_never_holds(self):
        partial = {"p": self.cells()["p"][:3]}
        cell = {"id": "c", "policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught", "expected": {"min": 0, "max": 1}}
        self.assertEqual(score.adjudicate([cell], partial)[0]["verdict"], "unobserved")
        self.assertEqual(score.adjudicate([cell], {})[0]["verdict"], "unobserved")

    def test_allows_no_caught_needs_the_complete_set_with_no_catch(self):
        cell = {"id": "c", "policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "lineMovedWhenCaught",
                "expected": {"min": 1, "max": 1, "allowsNoCaught": True}}
        self.assertEqual(score.adjudicate([cell], self.cells(caught=0, moved=0))[0]["verdict"], "holds")
        self.assertEqual(score.adjudicate([cell], {"p": self.cells(caught=0)["p"][:5]})[0]["verdict"], "unobserved")

    def test_divergence_is_named(self):
        cell = {"id": "c", "policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught", "expected": {"min": 1, "max": 1}}
        self.assertEqual(score.adjudicate([cell], self.cells())[0]["verdict"], "diverges")

    def test_a_dropped_instance_is_the_control_result_not_missing_evidence(self):
        cell = {"id": "c", "policy": "p", "defect": "D1-00", "stratum": "random", "n": 50, "endpoint": "caught", "expected": {"min": 1, "max": 1}}
        self.assertEqual(score.adjudicate([cell], {}, {"p": {"D1-00"}})[0]["verdict"], "dropped")

    def test_a_holdout_array_loads_as_cells(self):
        holdout = score.load_matrix(STUDY / "harness" / "MATRIX-HOLDOUT.json")
        self.assertTrue(isinstance(holdout, list) and holdout, "the reviewer's holdout must be a non-empty array")
        for c in holdout:
            self.assertIn(c["endpoint"], ("caught", "lineMovedWhenCaught"))

    def test_the_signature_table_counts_threshold_free_catches_as_none(self):
        cells = {"p": [{"defect": "D6-00", "class": "D6", "site": "s", "ledger": "literal", "caught": True, "signature": {"applicable": False}}]}
        _, sigs = score.aggregate(cells)
        row = [r for r in sigs if r["defect"] == "D6-00"][0]
        self.assertEqual((row["caught"], row["lineMoved"], row["noThreshold"], row["rate"]), (1, 0, 1, 0.0))


class SignatureEvidence(unittest.TestCase):
    def test_incomplete_signature_evidence_is_refused(self):
        self.assertFalse(score.signature_evidence_ok({"applicable": True}, 3))
        self.assertFalse(score.signature_evidence_ok({"applicable": False}, 3))
        self.assertTrue(score.signature_evidence_ok({"applicable": False, "thresholdEntries": 0}, 3, boundaries=set()))
        self.assertFalse(score.signature_evidence_ok({"applicable": False, "thresholdEntries": 0}, 3, boundaries={("/x", "10")}))
        good = replay.signature(profile([("/x", "10", 3, 0, 0)]), 3, expected=1, origins={"o"})
        self.assertTrue(score.signature_evidence_ok(good, 3, boundaries={("/x", "10")}, origins={"o"}, ledger_rows=3))
        self.assertFalse(score.signature_evidence_ok(dict(good, lineMoved=False), 3, boundaries={("/x", "10")}, origins={"o"}, ledger_rows=3), "a recorded verdict must agree with its own counts")
        # declared count without the retained entries; a foreign boundary; a foreign origin; counts beyond the ledger
        self.assertFalse(score.signature_evidence_ok({"applicable": True, "thresholdEntries": 1, "lineMoved": False, "placed": False, "disagreeing": {}}, 3, boundaries={("/x", "10")}, origins={"o"}))
        self.assertFalse(score.signature_evidence_ok(good, 3, boundaries={("/y", "999")}, origins={"o"}, ledger_rows=3))
        self.assertFalse(score.signature_evidence_ok(good, 3, boundaries={("/x", "10")}, origins={"other"}, ledger_rows=3))
        self.assertFalse(score.signature_evidence_ok(good, 3, boundaries={("/x", "10")}, origins={"o"}, ledger_rows=2))
        with self.assertRaises(RuntimeError):
            replay.signature({"thresholds": [{"pointer": "/x", "literal": "10", "origins": []}]}, 1, expected=1, origins={"o"})

    def cases(self, values):
        return [{"id": "r%d" % i, "origin": "o", "facts": {"x": v}} for i, v in enumerate(values)]

    def test_threshold_evidence_must_agree_with_the_ledger(self):
        cases = self.cases(["5", "10", "12"])  # one below, one at, one above 10
        good = profile([("/x", "10", 1, 0, 0)])
        good["thresholds"][0]["origins"][0] = {"origin": "o", "below": {"rows": 1, "disagreeing": 1}, "at": {"rows": 1, "disagreeing": 0}, "above": {"rows": 1, "disagreeing": 0}}
        sig = replay.signature(good, 1, expected=1, origins={"o"}, cases=cases)
        self.assertTrue(sig["lineMoved"])
        self.assertTrue(score.signature_evidence_ok(sig, 1, boundaries={("/x", "10")}, origins={"o"}, ledger_rows=3, cases=cases))
        # zeroed disagreements against a replay that mismatched one row: impossible
        zeroed = json.loads(json.dumps(good)); zeroed["thresholds"][0]["origins"][0]["below"]["disagreeing"] = 0
        with self.assertRaises(RuntimeError):
            replay.signature(zeroed, 1, expected=1, origins={"o"}, cases=cases)
        forged = json.loads(json.dumps(sig)); forged["thresholds"][0]["origins"][0]["below"]["disagreeing"] = 0
        forged["disagreeing"] = {}; forged["lineMoved"] = False; forged["placed"] = False
        self.assertFalse(score.signature_evidence_ok(forged, 1, boundaries={("/x", "10")}, origins={"o"}, ledger_rows=3, cases=cases))
        # bucket rows that are not the ledger's comparable rows
        wrong = json.loads(json.dumps(good)); wrong["thresholds"][0]["origins"][0]["above"]["rows"] = 2
        with self.assertRaises(RuntimeError):
            replay.signature(wrong, 1, expected=1, origins={"o"}, cases=cases)

    def test_expected_buckets_place_only_decimal_strings(self):
        cases = self.cases(["5", 7, "abc", "10", None, "11"])
        self.assertEqual(replay.expected_buckets(cases, "/x", "10"), {"o": {"below": 1, "at": 1, "above": 1}})

    def test_a_missing_profile_fails_the_replay(self):
        with self.assertRaises(RuntimeError):
            replay.signature(None, 1, expected=0)
        with self.assertRaises(RuntimeError):
            replay.signature({}, 1, expected=1)

    def test_the_attempt_id_is_hexadecimal(self):
        import attempt
        m = AttemptMarker().marker(attemptId="z" * 32)
        self.assertTrue(attempt.marker_problems(m, "sha256:x", "REGISTERED"))


class AttemptMarker(unittest.TestCase):
    def marker(self, **over):
        import attempt
        m = {"attemptId": "a" * 32, "label": "REGISTERED", "jpackVersion": "jpack 0.21.0", "jpackDigest": "sha256:x",
             "pinsRawSha256": attempt.pins_raw_sha256(), "seeds": [101, 130], "sizes": [5, 10, 20, 50],
             "policies": list(attempt.POLICIES), "startedAt": "t"}
        m.update(over)
        return m

    def test_a_matching_registered_marker_has_no_problem(self):
        import attempt
        self.assertEqual(attempt.marker_problems(self.marker(), "sha256:x", "REGISTERED"), [])

    def test_a_pilot_marker_is_not_a_registered_one(self):
        import attempt
        self.assertTrue(attempt.marker_problems(self.marker(label="PILOT"), "sha256:x", "REGISTERED"))
        self.assertTrue(attempt.marker_problems(self.marker(seeds=[1, 30]), "sha256:x", "REGISTERED"))
        self.assertTrue(attempt.marker_problems(self.marker(jpackDigest="sha256:y"), "sha256:x", "REGISTERED"))
        self.assertTrue(attempt.marker_problems(self.marker(pinsRawSha256="0" * 64), "sha256:x", "REGISTERED"))
        self.assertTrue(attempt.marker_problems(None, "sha256:x", "REGISTERED"))

    def test_the_scorer_refuses_a_root_without_a_marker(self):
        import subprocess
        root = tempfile.mkdtemp()
        proc = subprocess.run([sys.executable, str(HERE.parent / "score.py"), "--attempt-root", root, "--pilot"], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("refusing", proc.stderr)


class ReservedSeeds(unittest.TestCase):
    def test_reserved_draws_need_a_valid_registered_attempt(self):
        import subprocess
        proc = subprocess.run([sys.executable, str(HERE.parent / "build_ledgers.py"), "sanctions-screening", "--n", "5", "--seeds", "30",
                               "--seed-base", "101", "--reserved", "--out", tempfile.mkdtemp()], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("valid registered attempt", proc.stderr)

    def test_the_builder_refuses_reserved_seeds_without_the_flag(self):
        import subprocess
        proc = subprocess.run([sys.executable, str(HERE.parent / "build_ledgers.py"), "sanctions-screening", "--n", "5", "--seeds", "30",
                               "--seed-base", "101", "--out", tempfile.mkdtemp()], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("reserved", proc.stderr)
        proc = subprocess.run([sys.executable, str(HERE.parent / "build_ledgers.py"), "sanctions-screening", "--n", "5", "--seeds", "5",
                               "--seed-base", "101", "--reserved", "--out", tempfile.mkdtemp()], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("exactly", proc.stderr)

    def test_the_runner_refuses_an_existing_root(self):
        import subprocess
        root = tempfile.mkdtemp()
        proc = subprocess.run([sys.executable, str(HERE.parent / "run_attempt.py"), "--attempt-root", root, "--pilot"], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("used once", proc.stderr)


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
        pack, base = build_ledgers.load_policy("vendor-onboarding")
        with tempfile.TemporaryDirectory() as tmp:
            root = jp.project(tmp, "vendor-onboarding", pack)
            ledger, _ = build_ledgers.random_ledger("vendor-onboarding", pack, base, root, 8, 3)
        for c in ledger["cases"]:
            self.assertNotEqual(c["expectedDisposition"].get("kind"), "not-applicable")

    def test_the_unplanted_pack_replays_its_own_ledger_clean(self):
        pack, base = build_ledgers.load_policy("sanctions-screening")
        with tempfile.TemporaryDirectory() as tmp:
            root = jp.project(tmp, "sanctions-screening", pack)
            ledger, _ = build_ledgers.random_ledger("sanctions-screening", pack, base, root, 8, 2)
        r = replay.replay("sanctions-screening", pack, ledger)
        self.assertFalse(r["caught"], r)


if __name__ == "__main__":
    unittest.main()
