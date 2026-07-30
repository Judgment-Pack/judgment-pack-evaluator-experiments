import copy
import json
import tempfile
import unittest
from pathlib import Path

from harness import study
from harness.acquisition_gateway import Gateway
from harness.common import digest, load_json, pretty, verify_attestation


class FixtureAndSchemaTests(unittest.TestCase):
    def test_frozen_copies_and_order_validate(self):
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

    def test_transport_schema_uses_only_registered_subset(self):
        schema = load_json(study.RESPONSE_SCHEMA_PATH)
        self.assertEqual(study.transport_schema_errors(schema), [])
        serialized = json.dumps(schema)
        for keyword in (
            '"$schema"',
            '"$id"',
            '"pattern"',
            '"maxItems"',
            '"uniqueItems"',
            '"const"',
        ):
            self.assertNotIn(keyword, serialized)

    def test_prompt_is_frozen_and_qualification_is_non_efficacy(self):
        rendered = study.render_prompt(
            study.cases(), load_json(study.BINDING_PATH)
        )
        self.assertNotIn("{{", rendered)
        self.assertIn("Northwind Analytics Ltd", rendered)
        qualification = study.QUALIFICATION_PROMPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("Northwind", qualification)
        self.assertNotIn("OFAC", qualification)
        self.assertNotIn("matchCount", qualification)


class GatewayAndLoweringTests(unittest.TestCase):
    def setUp(self):
        self.document = study.cases()
        self.binding = load_json(study.BINDING_PATH)
        self.key = study.KEY_PATH.read_bytes().strip()
        self.transport = load_json(study.RESPONSE_SCHEMA_PATH)

    def issue(self, directory, scenario_id="S01"):
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
            {"legal_name": self.document["request"]["legalName"]},
        )
        self.assertFalse(response["isError"])
        return response["structuredContent"]

    def candidate(self, directory, scenario_id="S01"):
        result = self.issue(directory, scenario_id)
        return result, study.candidate_from_gateway(
            result, self.document, self.binding
        )

    def test_gateway_persists_artifact_and_attested_receipt(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result, _ = self.candidate(store)
            artifact_path = study.digest_path(
                store, "artifacts", result["provenance"]["artifactDigest"]
            )
            receipt_path = study.digest_path(
                store, "receipts", result["provenance"]["receiptDigest"]
            )
            self.assertEqual(
                digest(load_json(artifact_path)),
                result["provenance"]["artifactDigest"],
            )
            receipt = load_json(receipt_path)
            self.assertEqual(digest(receipt), result["provenance"]["receiptDigest"])
            self.assertTrue(verify_attestation(receipt, self.key))

    def test_good_candidate_passes_transport_and_semantic_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            _, candidate = self.candidate(store)
            self.assertEqual(
                study.validate_transport(candidate, self.transport), []
            )
            self.assertEqual(study.validate_candidate(candidate), [])
            self.assertEqual(
                study.verify_candidate(
                    candidate, store, self.document, self.binding, self.key
                ),
                [],
            )

    def test_duplicate_pointer_passes_transport_but_fails_semantic_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            _, candidate = self.candidate(store)
            pointers = candidate["lineage"]["evidenceClaim"]["basisPointers"]
            pointers.append(pointers[0])
            self.assertEqual(
                study.validate_transport(candidate, self.transport), []
            )
            self.assertIn(
                "syntax: evidence claim is invalid",
                study.validate_candidate(candidate),
            )

    def test_excess_fact_claim_passes_transport_but_fails_semantic_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            _, candidate = self.candidate(store)
            candidate["lineage"]["factClaims"].append(
                copy.deepcopy(candidate["lineage"]["factClaims"][0])
            )
            self.assertEqual(
                study.validate_transport(candidate, self.transport), []
            )
            self.assertIn(
                "syntax: factClaims is invalid", study.validate_candidate(candidate)
            )

    def test_invalid_digest_passes_transport_but_fails_semantic_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            _, candidate = self.candidate(store)
            candidate["lineage"]["receiptDigest"] = "not-a-digest"
            self.assertEqual(
                study.validate_transport(candidate, self.transport), []
            )
            self.assertIn(
                "syntax: receiptDigest is invalid",
                study.validate_candidate(candidate),
            )

    def test_fact_mutation_is_rejected_by_lineage(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            _, candidate = self.candidate(store)
            candidate["facts"]["screening"]["matchCount"] = "2"
            candidate["lineage"]["factClaims"][0]["value"] = "2"
            errors = study.verify_candidate(
                candidate, store, self.document, self.binding, self.key
            )
            self.assertTrue(any(error.startswith("mapping:") for error in errors))
            self.assertTrue(any(error.startswith("claim:") for error in errors))

    def test_artifact_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            store = Path(raw)
            result, candidate = self.candidate(store)
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


class RunnerAndScorerTests(unittest.TestCase):
    def test_protocol_and_tool_detection(self):
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
        self.assertEqual(study.tool_event_count(events), 3)

    def test_token_usage_is_mechanical(self):
        events = [
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 10,
                    "cached_input_tokens": 4,
                    "output_tokens": 3,
                },
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 2, "output_tokens": 1},
            },
        ]
        self.assertEqual(
            study.token_usage(events),
            {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 4},
        )

    def test_summary_arithmetic_and_prediction(self):
        rows = []
        for row in study.trial_order():
            rows.append(
                {
                    **row,
                    "M1": True,
                    "M2": True,
                    "M3": True,
                    "protocolViolations": [],
                    "tokenUsage": {"input_tokens": 1},
                }
            )
        summary = study.summarize_rows(rows)
        self.assertEqual(summary["M2"], {"successes": 24, "total": 24})
        self.assertEqual(summary["M4"], {"successes": 18, "total": 18})
        self.assertEqual(summary["M5"]["successes"], 3)
        self.assertTrue(summary["predictionHit"])
        for row in rows[:5]:
            row["M2"] = False
            row["M3"] = False
        self.assertFalse(study.summarize_rows(rows)["predictionHit"])

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
