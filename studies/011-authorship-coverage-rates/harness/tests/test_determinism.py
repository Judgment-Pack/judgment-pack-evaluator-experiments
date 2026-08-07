#!/usr/bin/env python3
"""Determinism: the same slots score to the same bytes.

A rate table that changed between two readings of the same evidence would be
unreadable as a result. The scorer therefore takes no clock and no randomness,
sorts everything it iterates, and rounds where it reports — and this test holds
it to that by scoring one slot tree twice into two output directories and
comparing RESULTS.json, RATES.md, and the optionally emitted record trees byte
for byte. It also checks the population filter is in code rather than in the
caller: a slot dropped from the tree changes the denominator, and nothing else
can.
"""
from __future__ import annotations
import json
import os
import shutil
import tempfile
import unittest

import fixtures
import score_rates

STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def walk(root: str) -> dict:
    """{relative path: bytes} for a whole output directory."""
    tree = {}
    for base, _, names in os.walk(root):
        for name in names:
            path = os.path.join(base, name)
            with open(path, "rb") as handle:
                tree[os.path.relpath(path, root)] = handle.read()
    return tree


class Determinism(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="s011-determinism-")
        self.addCleanup(shutil.rmtree, self.root, True)
        with open(os.path.join(STUDY, "harness", "PINS.json")) as handle:
            self.pins = json.load(handle)
        # A three-slot batch is terminal only against a registry that asks for
        # three: the scorer refuses an incomplete batch, and these fixtures are
        # a whole batch, not a truncated one.
        self.pins["batch"]["runs"] = 3
        self.pins_path = os.path.join(self.root, "PINS.json")
        with open(self.pins_path, "w") as handle:
            json.dump(self.pins, handle, indent=2)
        self.prompt = os.path.join(STUDY, "transcription", "PROMPT.txt")
        self.family = os.path.join(STUDY, "FAMILY.json")
        self.slots, self.golden = fixtures.build_tree(
            self.root, [fixtures.COMPLETION_A, fixtures.COMPLETION_B,
                        fixtures.COMPLETION_A], STUDY, self.pins)

    def score_into(self, name: str) -> str:
        out = os.path.join(self.root, name)
        code = score_rates.main(["score_rates.py", "score", "--slots", self.slots,
                                 "--pins", self.pins_path, "--family", self.family,
                                 "--prompt", self.prompt, "--golden", self.golden,
                                 "--out", out, "--emit-records", os.path.join(out, "records")])
        self.assertEqual(code, 0)
        return out

    def test_two_scorings_of_one_tree_are_byte_identical(self):
        first, second = self.score_into("out-1"), self.score_into("out-2")
        self.assertEqual(walk(first), walk(second))
        self.assertIn("RESULTS.json", os.listdir(first))
        self.assertIn("RATES.md", os.listdir(first))

    def test_the_results_carry_no_clock(self):
        results = json.load(open(os.path.join(self.score_into("out-3"), "RESULTS.json")))

        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield key
                    for nested in keys(value):
                        yield nested
            elif isinstance(node, list):
                for item in node:
                    for nested in keys(item):
                        yield nested

        for key in keys(results):
            self.assertNotIn("time", key.lower())
            self.assertNotIn("date", key.lower())
            self.assertNotIn("elapsed", key.lower())

    def test_the_denominator_is_the_valid_runs_and_nothing_else(self):
        results = score_rates.score(self.slots, self.pins_path, self.family,
                                    self.prompt, self.golden)
        self.assertEqual(results["population"]["valid"], 3)
        for entry in results["classes"]:
            self.assertEqual(entry["coverage"]["trials"], 3)
        # Break one slot: it leaves the denominator and takes its code with it.
        os.remove(os.path.join(self.slots, "run-002", "completion.txt"))
        results = score_rates.score(self.slots, self.pins_path, self.family,
                                    self.prompt, self.golden)
        self.assertEqual(results["population"]["valid"], 2)
        self.assertEqual(results["population"]["invalidCodes"], {"no-completion": 1})
        for entry in results["classes"]:
            self.assertEqual(entry["coverage"]["trials"], 2)
        # Class 0 was reached only by the run that just left the population.
        by_index = {entry["index"]: entry["coverage"]["count"] for entry in results["classes"]}
        self.assertEqual(by_index, {0: 0, 1: 2, 2: 0, 3: 2, 4: 2, 5: 0})

    def test_emitted_records_are_the_compiled_bytes(self):
        out = self.score_into("out-4")
        emitted = os.path.join(out, "records", "run-001")
        self.assertTrue(os.path.isfile(os.path.join(emitted, "RECORDS.md")))
        for case_id in fixtures.PROFILE_A["accepted"]:
            with open(os.path.join(emitted, "records", case_id + ".json"), "rb") as handle:
                record = json.loads(handle.read().decode("utf-8"))
            self.assertEqual(record["caseId"], case_id)


if __name__ == "__main__":
    unittest.main()
