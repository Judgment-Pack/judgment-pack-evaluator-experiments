import json
import tempfile
import unittest
from pathlib import Path

from harness import study
from harness.synthetic_mcp import Server, digest, rotate


class StudyFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = study.study_cases()
        cls.scenarios = study.scenario_map(cls.document)

    def test_frozen_fixtures_validate(self):
        self.assertEqual(study.validate_fixtures(), [])
        self.assertEqual(len(study.trial_order()), 48)

    def test_arm_delta_is_only_semantic_identifier(self):
        for scenario in self.document["scenarios"]:
            prose = study.source_guidance(scenario, "P")
            semantic = study.source_guidance(scenario, "S")
            self.assertEqual(prose["source"], semantic["source"]["description"])
            self.assertEqual(prose["hint"], semantic["hint"])
            self.assertEqual(semantic["sourceRef"], semantic["source"]["id"])

    def test_preregistered_rotations_and_opaque_names(self):
        for scenario in self.document["scenarios"]:
            keys = [tool["key"] for tool in scenario["tools"]]
            self.assertEqual([tool["key"] for tool in rotate(scenario["tools"], 0)], keys)
            self.assertEqual(
                [tool["key"] for tool in rotate(scenario["tools"], 1)],
                keys[1:] + keys[:1],
            )
            self.assertEqual(
                [tool["key"] for tool in rotate(scenario["tools"], 2)],
                keys[-1:] + keys[:-1],
            )
            for repetition in study.REPETITIONS:
                catalog = study.opaque_catalog(scenario, repetition)
                self.assertEqual(
                    [row["name"] for row in catalog],
                    ["source_%s" % chr(ord("a") + index) for index in range(len(keys))],
                )

    def test_prompt_treatment_is_rendered_once(self):
        scenario = self.scenarios["S01"]
        prose = study.render_prompt(self.document, scenario, "P")
        semantic = study.render_prompt(self.document, scenario, "S")
        self.assertNotIn("{{REQUEST}}", prose)
        self.assertNotIn("{{SOURCE_GUIDANCE}}", prose)
        self.assertNotIn(scenario["source"]["id"], prose)
        self.assertIn(scenario["source"]["id"], semantic)


class SyntheticMcpTests(unittest.TestCase):
    def test_receipt_precedes_result_and_uses_fixture_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.jsonl"
            server = Server(
                str(study.CASES_PATH), "S01", 0, "test-cell", str(receipt)
            )
            response = server.call_tool(
                "source_a", {"legal_name": "Northwind Analytics Ltd"}
            )
            self.assertFalse(response["isError"])
            rows = study.read_jsonl(receipt)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["toolKey"], "ofac-exact")
            scenario = study.scenario_map(study.study_cases())["S01"]
            self.assertEqual(rows[0]["resultSha256"], digest(scenario["tools"][0]["result"]))
            self.assertEqual(response["structuredContent"], scenario["tools"][0]["result"])

    def test_invalid_arguments_do_not_create_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.jsonl"
            server = Server(
                str(study.CASES_PATH), "S01", 0, "test-cell", str(receipt)
            )
            response = server.call_tool("source_a", {"name": "wrong"})
            self.assertTrue(response["isError"])
            self.assertFalse(receipt.exists())


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.document = study.study_cases()
        self.scenarios = study.scenario_map(self.document)

    @staticmethod
    def write_json(path, value):
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def valid_final(self, scenario):
        expected = scenario["expected"]
        return {
            "facts": expected["facts"],
            "evidenceAvailability": expected["evidenceAvailability"],
            "acquisitionStatus": expected["acquisitionStatus"],
            "sourceId": (
                scenario["source"]["id"]
                if expected["acquisitionStatus"] == "resolved"
                else None
            ),
            "explanation": "Synthetic test.",
        }

    def make_receipts(self, scenario):
        result = []
        for index, key in enumerate(scenario["expected"]["toolKeys"], start=1):
            tool = next(tool for tool in scenario["tools"] if tool["key"] == key)
            result.append(
                {
                    "cellId": "test",
                    "callIndex": index,
                    "toolName": "source_a",
                    "toolKey": key,
                    "provides": tool["provides"],
                    "arguments": {"legal_name": "Northwind Analytics Ltd"},
                    "sideEffect": tool["sideEffect"],
                    "resultSha256": digest(tool["result"]),
                }
            )
        return result

    def score_success(self, directory, scenario_id="S01", arm="P"):
        scenario = self.scenarios[scenario_id]
        for row in self.make_receipts(scenario):
            with (directory / "receipt.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row) + "\n")
        (directory / "events.jsonl").write_text("", encoding="utf-8")
        self.write_json(directory / "final.json", self.valid_final(scenario))
        row = {
            "cellId": "test",
            "scenarioId": scenario_id,
            "arm": arm,
            "repetition": 0,
        }
        return study.score_cell(
            row, scenario, directory, self.document["request"]["legalName"]
        )

    def test_exact_receipt_and_mapping_succeed(self):
        with tempfile.TemporaryDirectory() as raw:
            result = self.score_success(Path(raw))
        self.assertTrue(result["E1"])
        self.assertTrue(result["E2"])
        self.assertTrue(result["E3"])

    def test_malformed_output_fails_mapping(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            scenario = self.scenarios["S01"]
            for row in self.make_receipts(scenario):
                (directory / "receipt.jsonl").write_text(
                    json.dumps(row) + "\n", encoding="utf-8"
                )
            (directory / "events.jsonl").write_text("", encoding="utf-8")
            (directory / "final.json").write_text("not json\n", encoding="utf-8")
            row = {
                "cellId": "test",
                "scenarioId": "S01",
                "arm": "P",
                "repetition": 0,
            }
            result = study.score_cell(
                row, scenario, directory, self.document["request"]["legalName"]
            )
        self.assertFalse(result["E1"])
        self.assertFalse(result["E3"])
        self.assertFalse(result["finalValid"])

    def test_mutation_and_wrong_arguments_fail_primary(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            scenario = self.scenarios["S08"]
            write_tool = next(
                tool for tool in scenario["tools"] if tool["sideEffect"] == "write"
            )
            receipt = {
                "toolKey": write_tool["key"],
                "arguments": {"legal_name": "Northwind Analytics"},
                "sideEffect": "write",
            }
            self.write_json(directory / "receipt.jsonl", receipt)
            (directory / "events.jsonl").write_text("", encoding="utf-8")
            self.write_json(directory / "final.json", self.valid_final(scenario))
            row = {
                "cellId": "test",
                "scenarioId": "S08",
                "arm": "S",
                "repetition": 0,
            }
            result = study.score_cell(
                row, scenario, directory, self.document["request"]["legalName"]
            )
        self.assertFalse(result["E1"])
        self.assertFalse(result["argumentsCorrect"])
        self.assertEqual(result["mutatingCalls"], 1)

    def test_protocol_violation_detection_deduplicates_lifecycle(self):
        events = [
            {
                "type": "item.started",
                "item": {"id": "1", "type": "command_execution"},
            },
            {
                "type": "item.completed",
                "item": {"id": "1", "type": "command_execution"},
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "2",
                    "type": "mcp_tool_call",
                    "server": "source_harness",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "3",
                    "type": "mcp_tool_call",
                    "server": "other",
                },
            },
        ]
        self.assertEqual(
            study.protocol_violations(events), ["shell", "undeclared-mcp"]
        )

    def test_summary_arithmetic_and_registered_prediction(self):
        scored = []
        for row in study.trial_order():
            value = {
                **row,
                "E1": row["arm"] == "S",
                "E2": True,
                "E3": True,
                "mutatingCalls": 0,
                "absenceConfusion": False,
                "protocolViolations": [],
            }
            scored.append(value)
        summary = study.summarize(scored)
        self.assertEqual(summary["byArm"]["P"]["E1"], {"successes": 0, "total": 24})
        self.assertEqual(summary["byArm"]["S"]["E1"], {"successes": 24, "total": 24})
        self.assertEqual(summary["byArm"]["P"]["E4"]["total"], 9)
        self.assertEqual(summary["byArm"]["S"]["E5"]["total"], 6)
        self.assertEqual(summary["byArm"]["P"]["E6"]["total"], 3)
        self.assertTrue(summary["predictionHit"])


if __name__ == "__main__":
    unittest.main()
