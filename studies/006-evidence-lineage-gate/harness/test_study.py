import copy
import json
import tempfile
import unittest
from pathlib import Path

from harness import study
from harness.acquisition_gateway import Gateway
from harness.common import digest, load_json, pretty, verify_attestation


class FixtureTests(unittest.TestCase):
    def test_fixtures_and_order_validate(self):
        self.assertEqual(study.validate_fixtures(), [])
        self.assertEqual(len(study.trial_order()), 24)
        self.assertEqual(
            study.trial_order()[0],
            {"cellId": "r01-s01", "repetition": 0, "scenarioId": "S01"},
        )
        self.assertEqual(
            study.trial_order()[-1],
            {"cellId": "r03-s08", "repetition": 2, "scenarioId": "S08"},
        )

    def test_every_frozen_expected_mapping_is_derived(self):
        document = study.cases()
        binding = load_json(study.BINDING_PATH)
        for scenario in document["scenarios"]:
            derived = study.derive_payload(
                scenario["payload"],
                document["request"]["legalName"],
                document["asOf"],
                binding["maxAgeSeconds"],
            )
            for member in ("facts", "evidenceAvailability", "acquisitionStatus"):
                self.assertEqual(
                    derived[member],
                    scenario["expected"][member],
                    "%s %s" % (scenario["id"], member),
                )

    def test_prompt_has_no_unexpanded_placeholders(self):
        rendered = study.render_prompt(
            study.cases(), load_json(study.BINDING_PATH)
        )
        self.assertNotIn("{{", rendered)
        self.assertIn("org.example.input-source.us-ofac.entity-screening", rendered)
        self.assertNotIn("fixture-key", rendered)


class GatewayAndVerifierTests(unittest.TestCase):
    def setUp(self):
        self.document = study.cases()
        self.binding = load_json(study.BINDING_PATH)
        self.key = study.KEY_PATH.read_bytes().strip()

    def issue(self, directory, scenario_id="S01", legal_name=None):
        gateway = Gateway(
            study.CASES_PATH,
            study.BINDING_PATH,
            study.KEY_PATH,
            scenario_id,
            0,
            "test-cell",
            directory,
        )
        response = gateway.call_tool(
            "acquire_screening",
            {
                "legal_name": legal_name
                or self.document["request"]["legalName"]
            },
        )
        self.assertFalse(response["isError"])
        return response["structuredContent"]

    def test_gateway_persists_artifact_and_attested_receipt(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result = self.issue(store)
            artifact_path = study.digest_path(
                store, "artifacts", result["provenance"]["artifactDigest"]
            )
            receipt_path = study.digest_path(
                store, "receipts", result["provenance"]["receiptDigest"]
            )
            self.assertTrue(artifact_path.exists())
            self.assertTrue(receipt_path.exists())
            self.assertEqual(digest(load_json(artifact_path)), result["provenance"]["artifactDigest"])
            receipt = load_json(receipt_path)
            self.assertEqual(digest(receipt), result["provenance"]["receiptDigest"])
            self.assertTrue(verify_attestation(receipt, self.key))

    def test_good_candidate_verifies(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result = self.issue(store)
            candidate = study.candidate_from_gateway(
                result, self.document, self.binding
            )
            self.assertEqual(study.validate_candidate(candidate), [])
            self.assertEqual(
                study.verify_candidate(
                    candidate, store, self.document, self.binding, self.key
                ),
                [],
            )

    def test_fact_mutation_is_syntax_valid_but_lineage_invalid(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result = self.issue(store)
            candidate = study.candidate_from_gateway(
                result, self.document, self.binding
            )
            candidate["facts"]["screening"]["matchCount"] = "2"
            candidate["lineage"]["factClaims"][0]["value"] = "2"
            self.assertEqual(study.validate_candidate(candidate), [])
            errors = study.verify_candidate(
                candidate, store, self.document, self.binding, self.key
            )
            self.assertTrue(any(item.startswith("mapping:") for item in errors))
            self.assertTrue(any(item.startswith("claim:") for item in errors))

    def test_artifact_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result = self.issue(store)
            candidate = study.candidate_from_gateway(
                result, self.document, self.binding
            )
            artifact_path = study.digest_path(
                store, "artifacts", result["provenance"]["artifactDigest"]
            )
            payload = load_json(artifact_path)
            payload["recordId"] = "tampered"
            artifact_path.write_text(pretty(payload), encoding="utf-8")
            errors = study.verify_candidate(
                candidate, store, self.document, self.binding, self.key
            )
            self.assertIn("artifact: content digest mismatch", errors)

    def test_receipt_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result = self.issue(store)
            candidate = study.candidate_from_gateway(
                result, self.document, self.binding
            )
            receipt_path = study.digest_path(
                store, "receipts", result["provenance"]["receiptDigest"]
            )
            receipt = load_json(receipt_path)
            receipt["retrievedAt"] = "2026-07-30T15:01:00Z"
            receipt_path.write_text(pretty(receipt), encoding="utf-8")
            errors = study.verify_candidate(
                candidate, store, self.document, self.binding, self.key
            )
            self.assertIn("receipt: content digest mismatch", errors)
            self.assertIn("receipt: gateway attestation mismatch", errors)

    def test_invalid_arguments_create_no_store(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            gateway = Gateway(
                study.CASES_PATH,
                study.BINDING_PATH,
                study.KEY_PATH,
                "S01",
                0,
                "test-cell",
                store,
            )
            response = gateway.call_tool("acquire_screening", {"name": "wrong"})
            self.assertTrue(response["isError"])
            self.assertFalse((store / "receipt.jsonl").exists())


class ScoringHelpersTests(unittest.TestCase):
    def test_protocol_violation_detection(self):
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
                    "server": "acquisition_gateway",
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

    def test_evaluation_receipt_detects_output_mutation(self):
        key = study.KEY_PATH.read_bytes().strip()
        candidate = {
            "facts": {"screening": {"matchCount": "0"}},
            "evidenceAvailability": {"screening-record": "present"},
            "lineage": {"receiptDigest": "sha256:" + "0" * 64},
        }
        output = {
            "disposition": {
                "kind": "outcome",
                "outcomeId": "clear",
                "reasons": [],
                "handoff": {"state": "none"},
            }
        }
        receipt = study.issue_evaluation_receipt(output, candidate, "test", key)
        self.assertEqual(study.verify_evaluation_handoff(output, receipt, key), [])
        mutated = copy.deepcopy(output)
        mutated["disposition"]["outcomeId"] = "match"
        self.assertIn(
            "evaluation-output: disposition digest mismatch",
            study.verify_evaluation_handoff(mutated, receipt, key),
        )


if __name__ == "__main__":
    unittest.main()
