"""Offline study-harness tests — stdlib unittest, no network, no venv, no jpack.

Run: python3 -m unittest discover -s harness/tests -v
"""

import json
import os
import sys
import unittest
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "agents"))
sys.path.insert(0, str(STUDY / "harness"))
os.environ.setdefault("STUDY_DIR", str(STUDY))

import shell  # noqa: E402
from generate import expected_action, scenario_for, SHORT  # noqa: E402


def registry():
    return json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())


class TestCases(unittest.TestCase):
    def test_case_invariants(self):
        reg = registry()
        ids = [c["id"] for c in reg["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 21)
        for case in reg["cases"]:
            expect = case["expect"]
            if expect["kind"] == "outcome":
                self.assertIsNotNone(expect["outcomeId"], case["id"])
                self.assertEqual(expect["reasons"], [], case["id"])
            else:
                self.assertIsNone(expect["outcomeId"], case["id"])
                self.assertTrue(expect["reasons"], case["id"])
            if expect["handoff"] == "requested":
                self.assertTrue(expect["triggeredBy"], case["id"])
            else:
                self.assertIsNone(expect["triggeredBy"], case["id"])
            self.assertIn(case["pack"], reg["packActionMaps"])
            self.assertIn(case["pack"], SHORT)

    def test_goldens_agree_and_complete(self):
        reg = registry()
        check = json.loads((STUDY / "goldens" / "EXPECT-CHECK.json").read_text())
        self.assertEqual(check["disagreements"], 0)
        for case in reg["cases"]:
            self.assertTrue(
                (STUDY / "goldens" / (case["id"] + ".evaluation.json")).exists(),
                case["id"])


class TestMapper(unittest.TestCase):
    ACTION_MAP = {"go": "execute:launch", "stop": "record"}

    def map(self, disposition, target=None):
        return shell.map_disposition_to_action("c1", disposition, target, self.ACTION_MAP)

    def test_outcome_execute(self):
        action = self.map({"kind": "outcome", "outcomeId": "go", "reasons": [],
                           "handoff": {"state": "none"}})
        self.assertEqual(action["tool"], "execute_decision")
        self.assertEqual(action["args"]["action"], "launch")

    def test_outcome_record(self):
        action = self.map({"kind": "outcome", "outcomeId": "stop", "reasons": [],
                           "handoff": {"state": "none"}})
        self.assertEqual(action["tool"], "record_decision")

    def test_unresolved_without_handoff_abstains(self):
        action = self.map({"kind": "unresolved", "reasons": ["conflict"],
                           "handoff": {"state": "none"}})
        self.assertEqual(action["tool"], "record_decision")
        self.assertEqual(action["args"]["kind"], "unresolved")

    def test_requested_handoff_always_reviews(self):
        for kind in ("unresolved", "not-applicable", "outcome"):
            disposition = {"kind": kind, "reasons": ["unknown"],
                           "handoff": {"state": "requested", "triggeredBy": ["unknown"]}}
            if kind == "outcome":
                disposition["outcomeId"] = "go"
                disposition["reasons"] = []
            action = self.map(disposition, {"kind": "queue", "name": "Q"})
            self.assertEqual(action["tool"], "open_review", kind)
            self.assertEqual(action["args"]["target"], "Q")

    def test_missing_target_is_unspecified(self):
        action = self.map({"kind": "unresolved", "reasons": ["exception-escalation"],
                           "handoff": {"state": "requested",
                                       "triggeredBy": ["exception-escalation"]}})
        self.assertEqual(action["args"]["target"], "unspecified")

    def test_error_never_acts(self):
        action = shell.error_action("c1", "pack-not-conformant")
        self.assertEqual(action["tool"], "record_decision")
        self.assertEqual(action["args"]["kind"], "error")


class TestScenarios(unittest.TestCase):
    def test_cohort2_yaml_matches_generator(self):
        reg = registry()
        text = (STUDY / "scenarios" / "jps" / "cohort2.yaml").read_text()
        body = json.loads("\n".join(
            line for line in text.splitlines() if not line.startswith("#")))
        self.assertEqual(len(body["scenarios"]), 21)
        by_id = {s["id"]: s for s in body["scenarios"]}
        for case in reg["cases"]:
            scenario = by_id[case["id"]]
            regenerated = scenario_for(case, reg["packActionMaps"][case["pack"]])
            self.assertEqual(scenario, regenerated, case["id"])
            action = expected_action(case, reg["packActionMaps"][case["pack"]])
            disallowed = [t["name"] for t in scenario["disallowed_tools"]]
            if action["tool"] == "execute_decision":
                self.assertEqual(disallowed, [], case["id"])
            else:
                self.assertEqual(disallowed, ["execute_decision"], case["id"])

    def test_matrix_references_are_valid(self):
        reg = registry()
        ids = {c["id"] for c in reg["cases"]}
        tags = {c["id"]: "pack-" + SHORT[c["pack"]] for c in reg["cases"]}
        matrix = json.loads(
            (STUDY / "scenarios" / "mutations" / "MATRIX.json").read_text())["mutations"]
        for name, spec in matrix.items():
            selected = set(spec["tags"].split(","))
            for case_id, reg_case in spec["cases"].items():
                self.assertIn(case_id, ids, name)
                self.assertIn(tags[case_id], selected, (name, case_id))
                if reg_case.get("change") != "unchanged" and not str(
                        reg_case.get("change", "")).startswith("unchanged"):
                    for layer in "JFG":
                        self.assertIn(layer, reg_case, (name, case_id))
            entry = STUDY / "agents" / (spec["agent_module"] + ".py")
            self.assertTrue(entry.exists(), name)

    def test_mutated_packs_exist_and_are_labeled(self):
        packs_dir = STUDY / "scenarios" / "mutations" / "packs"
        names = sorted(p.name for p in packs_dir.glob("*.json"))
        self.assertEqual(len(names), 11)  # 7 maintainer cells + 4 holdouts
        for path in packs_dir.glob("*.json"):
            doc = json.loads(path.read_text())
            self.assertIn("STUDY 013 MUTATED FIXTURE", doc["description"], path.name)


class TestHoldouts(unittest.TestCase):
    """Static checks only — the holdouts must never EXECUTE before the freeze."""

    def holdout(self):
        return json.loads(
            (STUDY / "scenarios" / "mutations" / "MATRIX-HOLDOUT.json").read_text())

    def test_holdout_structure_and_schedule(self):
        reg = registry()
        ids = {c["id"] for c in reg["cases"]}
        tags = {c["id"]: "pack-" + SHORT[c["pack"]] for c in reg["cases"]}
        doc = self.holdout()
        self.assertIn("author", doc)
        self.assertEqual(sorted(doc["mutations"]), ["h01", "h02", "h03", "h04"])
        for name, spec in doc["mutations"].items():
            selected = set(spec["tags"].split(","))
            scheduled = {cid for cid, tag in tags.items() if tag in selected}
            self.assertEqual(set(spec["cases"]), scheduled, name)
            self.assertTrue(
                (STUDY / "agents" / (spec["agent_module"] + ".py")).exists(), name)
            fixture = STUDY / "scenarios" / "mutations" / "packs" / spec["fixture"]
            self.assertTrue(fixture.exists(), name)
            for cid, cell in spec["cases"].items():
                self.assertIn(cid, ids, name)
                for layer in "JFG":
                    self.assertIn(layer, cell, (name, cid))

    def test_holdout_fixture_is_source_plus_exactly_one_edit(self):
        """Whole-document equality (round 3): reconstruct source + the single
        registered pointer edit + the documentary prefix; any other edit fails."""
        import copy
        for name, spec in self.holdout()["mutations"].items():
            ms = spec["mutation_spec"]
            source = json.loads((STUDY / "packs" / ms["source_pack"]).read_text())
            reconstructed = copy.deepcopy(source)
            node = reconstructed
            parts = [p.replace("~1", "/").replace("~0", "~")
                     for p in ms["json_pointer"].split("/")[1:]]
            for part in parts[:-1]:
                node = node[int(part)] if isinstance(node, list) else node[part]
            key = int(parts[-1]) if isinstance(node, list) else parts[-1]
            self.assertEqual(node[key], ms["from"], name)
            node[key] = ms["to"]
            reconstructed["description"] = (
                "[STUDY 013 MUTATED FIXTURE — DEFECTIVE ON PURPOSE: "
                "reviewer-authored holdout {}: {} {} -> {}] {}".format(
                    name, ms["json_pointer"], json.dumps(ms["from"]),
                    json.dumps(ms["to"]), source.get("description", "")))
            fixture = json.loads(
                (STUDY / "scenarios" / "mutations" / "packs" / spec["fixture"]).read_text())
            self.assertEqual(fixture, reconstructed, name)

    def test_no_holdout_execution_artifacts(self):
        self.assertEqual(sorted((STUDY / "pilots").glob("*/h0*")), [])
        self.assertEqual(sorted((STUDY / "goldens").glob("h0*")), [])


class TestVerdictLiterals(unittest.TestCase):
    def test_prereg_quotes_gate_literals(self):
        import gate
        text = (STUDY / "PREREGISTRATION.md").read_text()
        for literal in (gate.VERDICT_INVALID, gate.VERDICT_HOLDS,
                        gate.VERDICT_FALSIFIED):
            self.assertIn(literal, text, literal)


class TestGateTotality(unittest.TestCase):
    """Negative tests (round 3, R3-1): no input may prevent a recorded verdict."""

    def test_provenance_is_total_without_environment(self):
        import gate
        saved = {k: os.environ.pop(k, None) for k in ("JPACK_BIN", "FORGE_CLONE")}
        try:
            doc = gate.provenance()
            self.assertIsNone(doc["jpackSha256"])
            self.assertIsNone(doc["forgeCommit"])
            self.assertEqual(doc["harnessPython"].count("."), 2)
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v

    def test_load_run_raises_cleanly_on_missing_output(self):
        import tempfile
        import gate
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(Exception):
                gate.load_run(tmp)

    def test_check_repeat_unreadable_is_invalid_row(self):
        import tempfile
        import gate
        with tempfile.TemporaryDirectory() as tmp:
            row = gate.check_repeat(tmp, ["a"])
            self.assertFalse(row["valid"])

    def test_upstream_unscored_pairs_registered(self):
        registered = json.loads(
            (STUDY / "scenarios" / "upstream-expected-unscored.json").read_text())
        self.assertEqual(registered["error"], "judge not configured")
        self.assertEqual(sum(len(v) for v in registered["pairs"].values()), 40)


if __name__ == "__main__":
    unittest.main()
