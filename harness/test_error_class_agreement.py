"""Tests for error_class_agreement.py that need neither evaluator.

The driver's verdicts are pure functions of what each implementation printed, so the cases that
matter most — an implementation that answers with a disposition, two that disagree, two that agree
with each other and not with the row — are tested here without building anything. The vendored rows
are held to their recorded digests, so a row's expectation cannot be edited in place.
"""
import hashlib
import json
import os
import unittest

import error_class_agreement as driver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGED = os.path.join(ROOT, driver.STAGED)
RELEASED = os.path.join(ROOT, "reference", "conformance-evaluation")

GO_ERROR = json.dumps(
    {"status": "error", "evaluationError": {"class": "malformed-input", "phase": "preflight"}}
)
PY_ERROR = json.dumps({"error": {"class": "malformed-input", "phase": "preflight"}})
DISPOSITION = json.dumps({"disposition": {"kind": "not-applicable"}})


class ReportOfTests(unittest.TestCase):
    def test_go_writes_its_error_to_stdout(self):
        self.assertEqual(
            ("error", "malformed-input", "preflight"),
            driver.report_of(GO_ERROR, GO_ERROR, "evaluationError"),
        )

    def test_python_writes_its_error_to_stderr_and_nothing_to_stdout(self):
        self.assertEqual(
            ("error", "malformed-input", "preflight"), driver.report_of("", PY_ERROR, "error")
        )

    def test_the_error_member_is_the_implementations_own_name_for_it(self):
        # Reading the Go envelope under the Python member name finds no error.
        self.assertEqual(("unparsed", None, None), driver.report_of(GO_ERROR, GO_ERROR, "error"))

    def test_a_disposition_is_not_an_error(self):
        self.assertEqual(
            ("disposition", None, None), driver.report_of(DISPOSITION, "", "error")
        )

    def test_a_disposition_together_with_an_error_is_reported_as_both(self):
        both = json.dumps(
            {"disposition": {"kind": "unresolved"}, "evaluationError": {"class": "malformed-input"}}
        )
        self.assertEqual("both", driver.report_of(both, both, "evaluationError")[0])

    def test_output_that_is_not_an_error_envelope_is_unparsed(self):
        for text in ("", "not json", "[]", "null", json.dumps({"error": "a string"}),
                     json.dumps({"error": {"class": 7}})):
            with self.subTest(text=text):
                self.assertEqual(("unparsed", None, None), driver.report_of(text, text, "error"))


class VerdictTests(unittest.TestCase):
    ERROR = ("error", "malformed-input", "preflight")

    def test_a_row_passes_when_both_refuse_and_all_three_classes_agree(self):
        self.assertIsNone(driver.verdict("malformed-input", self.ERROR, self.ERROR))

    def test_phase_is_never_part_of_the_verdict(self):
        other_phase = ("error", "malformed-input", "evaluation")
        no_phase = ("error", "malformed-input", None)
        self.assertIsNone(driver.verdict("malformed-input", self.ERROR, other_phase))
        self.assertIsNone(driver.verdict("malformed-input", no_phase, self.ERROR))

    def test_a_disposition_from_either_implementation_fails_the_row(self):
        answered = ("disposition", None, None)
        self.assertIn("go emitted a disposition", driver.verdict("malformed-input", answered, self.ERROR))
        self.assertIn("py emitted a disposition", driver.verdict("malformed-input", self.ERROR, answered))

    def test_an_error_that_comes_with_a_disposition_fails_the_row(self):
        both = ("both", "malformed-input", "preflight")
        self.assertIn("together with an error", driver.verdict("malformed-input", both, self.ERROR))

    def test_unreadable_output_fails_the_row(self):
        self.assertIn("could not be read", driver.verdict("malformed-input", self.ERROR, ("unparsed", None, None)))

    def test_implementations_that_disagree_fail_the_row(self):
        other = ("error", "unsupported-required-extension", "preflight")
        self.assertEqual(
            "the implementations report different classes",
            driver.verdict("malformed-input", self.ERROR, other),
        )

    def test_implementations_that_agree_against_the_row_fail_it_and_say_which(self):
        # The case a staged row exists to surface: the row may be the thing that is wrong.
        self.assertEqual(
            "both implementations agree with each other and not with the row",
            driver.verdict("unsupported-required-extension", self.ERROR, self.ERROR),
        )


class VendoredRowsTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(STAGED, "provenance.json")) as handle:
            self.provenance = json.load(handle)

    def test_every_vendored_file_has_its_recorded_digest_and_nothing_else_is_vendored(self):
        recorded = self.provenance["files"]
        present = set()
        for directory, _, names in os.walk(STAGED):
            for name in names:
                relative = os.path.relpath(os.path.join(directory, name), STAGED).replace(os.sep, "/")
                if relative not in ("provenance.json", "README.md"):
                    present.add(relative)
        self.assertEqual(set(recorded), present)
        for relative, digest in recorded.items():
            with self.subTest(file=relative), open(os.path.join(STAGED, relative), "rb") as handle:
                self.assertEqual(digest, hashlib.sha256(handle.read()).hexdigest())

    def test_the_rows_are_a_staged_file_and_not_a_corpus(self):
        with open(os.path.join(STAGED, "cases.json")) as handle:
            staged = json.load(handle)
        self.assertEqual("staged", staged["status"])
        self.assertNotIn("suiteVersion", staged)
        self.assertTrue(staged["cases"])
        for case in staged["cases"]:
            with self.subTest(case=case["id"]):
                self.assertIn("expectedErrorClass", case)
                self.assertNotIn("expectedDisposition", case)
                self.assertNotIn("expectedErrorPhase", case)
                self.assertTrue(os.path.isfile(os.path.join(STAGED, case["pack"])))

    def test_the_staged_copy_of_the_released_fixture_is_the_released_fixture(self):
        name = "data-request-intake-triage.json"
        with open(os.path.join(STAGED, "packs", name), "rb") as staged, \
                open(os.path.join(RELEASED, name), "rb") as released:
            self.assertEqual(released.read(), staged.read())


if __name__ == "__main__":
    unittest.main()
