"""Study 008 harness tests. Deterministic; no model, no network."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study  # noqa: E402
from study import S007, RULE_PATH, load, portable, s007  # noqa: E402


class Inputs(unittest.TestCase):
    def test_twenty_four_cells(self):
        self.assertEqual(len(study.cells()), 24)

    def test_each_cell_has_exactly_one_receipt_and_artifact(self):
        for cell_id in study.cells():
            inputs = study.cell_inputs(cell_id)
            self.assertTrue(inputs["receiptDigest"].startswith("sha256:"))
            self.assertTrue(inputs["artifactDigest"].startswith("sha256:"))

    def test_digests_come_from_the_store_not_the_model(self):
        # r03-s02 is Study 007's one-nibble transcription loss: the model's claimed
        # receipt digest must differ from the store's, and the harness must use the
        # store's.
        inputs = study.cell_inputs("r03-s02")
        claimed = inputs["modelFinal"]["lineage"]["receiptDigest"]
        self.assertNotEqual(claimed, inputs["receiptDigest"])
        self.assertEqual(s007.digest(inputs["receipt"]), inputs["receiptDigest"])


class Arms(unittest.TestCase):
    def setUp(self):
        self.document = load(S007 / "fixtures" / "cases.json")
        self.binding = load(S007 / "fixtures" / "binding-lock.json")
        self.rule = load(RULE_PATH)

    def test_arms_differ_only_in_claim_and_basis(self):
        for cell_id in study.cells():
            inputs = study.cell_inputs(cell_id)
            _, b_env = study.arm_b(inputs, self.document, self.binding)
            _, c_env = study.arm_c(inputs, self.document, self.binding, self.rule)
            for field in ("sourceRef",):
                self.assertEqual(b_env[field], c_env[field])
            for field in ("receiptDigest", "artifactDigest"):
                self.assertEqual(b_env["lineage"][field], c_env["lineage"][field])

    def test_rule_is_applied_unchanged_for_every_cell(self):
        # One rule, no per-cell branching: the same rule object derives all 24.
        reasons = set()
        for cell_id in study.cells():
            inputs = study.cell_inputs(cell_id)
            derived, _ = study.arm_c(inputs, self.document, self.binding, self.rule)
            reasons.add(derived["reason"])
        self.assertEqual(reasons, {"resolved", "absent", "unknown", "subject", "freshness", "type"})

    def test_injected_text_reaches_no_fact(self):
        inputs = study.cell_inputs("r03-s02")  # S02 carries untrustedRecordText
        self.assertIn("untrustedRecordText", inputs["payload"])
        derived, envelope = study.arm_c(inputs, self.document, self.binding, self.rule)
        self.assertEqual(derived["facts"], {"screening": {"matchCount": "2"}})
        self.assertNotIn("untrustedRecordText", json.dumps(envelope))


class Reproducibility(unittest.TestCase):
    def test_relative_common_dir_resolves_against_study_not_cwd(self):
        """The discriminating test: a plain checkout reports --git-common-dir
        relative to STUDY. Resolving it against the process cwd yields the wrong
        repository. (This test file may itself live in a worktree, where git
        reports an absolute path, so the relative case is supplied directly.)"""
        import os
        original = os.getcwd()
        try:
            os.chdir("/")
            resolved = study._resolve_common_dir("../../.git")
            self.assertEqual(resolved, (Path(study.STUDY) / ".." / ".." / ".git").resolve())
            self.assertNotEqual(resolved, Path("/.git"))
        finally:
            os.chdir(original)

    def test_absolute_common_dir_is_left_alone(self):
        self.assertEqual(study._resolve_common_dir("/tmp/x/.git"), Path("/tmp/x/.git"))

    def test_sibling_repos_resolve_from_any_working_directory(self):
        """git reports --git-common-dir relative to where it ran, so resolving it
        against the process cwd made the study runnable from one directory only.
        A third party must be able to run it from anywhere."""
        import os
        original = os.getcwd()
        for where in ("/", str(Path(study.STUDY).parent), str(study.EXPERIMENT)):
            try:
                os.chdir(where)
                study._bind_sibling_repos()
                self.assertTrue(study.s007.runtime_binary().exists(),
                                "runtime binary unresolved from cwd %s" % where)
            finally:
                os.chdir(original)


class Scoring(unittest.TestCase):
    def test_score_recomputes_from_retained_files(self):
        results_path = study.STUDY / "RESULTS.json"
        if not results_path.exists():
            self.skipTest("run `study.py run` and `score` first")
        results = load(results_path)
        for endpoint in ("D1_armC_admitted", "D2_armC_claim_equals_expected",
                         "D3_armC_basis_equals_armB_basis", "D5_armA_losses_recovered"):
            self.assertIn(endpoint, results)
            self.assertLessEqual(results[endpoint]["value"], results[endpoint]["of"])


if __name__ == "__main__":
    unittest.main()
