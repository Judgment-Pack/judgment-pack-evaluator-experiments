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
from unittest import mock

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
        self.prompt = os.path.join(STUDY, "transcription", "PROMPT.txt")
        self.family = os.path.join(STUDY, "FAMILY.json")
        self.slots, self.golden = fixtures.build_tree(
            self.root, [fixtures.COMPLETION_A, fixtures.COMPLETION_B,
                        fixtures.COMPLETION_A], STUDY, self.pins)
        # §3.2 step 3 and §2.6: the capture's digest and the preregistration's
        # freeze digest are both in the registry before anything is scored, and
        # the scorer refuses while either is null.
        self.pins["golden"]["sha256"] = score_rates.file_digest(self.golden)
        self.pins["preregistration"]["sha256"] = score_rates.file_digest(
            os.path.join(STUDY, "PREREGISTRATION.md"))
        with open(self.pins_path, "w") as handle:
            json.dump(self.pins, handle, indent=2)
        # §2.6: these slots are scored through the registered interface against
        # a stand-in study, so they name that study's registry — the wrapper
        # stamps the registry the run was actually made under, and a slot
        # stamped with any other one is `registry-mismatch`.
        self.registry = fixtures.stamp_registry(self.pins_path, *[
            os.path.join(self.slots, name) for name in sorted(os.listdir(self.slots))])

    def score_into(self, name: str) -> str:
        """The registered command, run against a stand-in study.

        There is no `--out` and no writer parameter: the tables go to the study
        root and nowhere else, so that scoring always leaves the marker the
        driver refuses new slots on (§2.4). A determinism test must not write
        into the committed study — whose golden pin is still null — so it
        REBINDS the module constants that name the stand-in study's registry,
        golden capture and root, and then runs the real command. That rebinding
        is the escape §7 says no check inside a file can refuse; it is used
        here to stand up a stand-in study, and `test_batch.py` is where the
        claim that no argument or flag can redirect the command is tested."""
        out = os.path.join(self.root, name)
        with mock.patch.multiple(
                score_rates, STUDY=out, REGISTRY_OF_RECORD=self.pins_path,
                REGISTERED_FAMILY=self.family, REGISTERED_PROMPT=self.prompt,
                REGISTERED_GOLDEN=self.golden):
            self.assertEqual(score_rates.main(
                ["score_rates.py", "score", "--slots", self.slots,
                 "--emit-records", os.path.join(out, "records")]), 0)
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
                                    self.prompt, self.golden,
                                    registry_sha256=self.registry)
        self.assertEqual(results["population"]["valid"], 3)
        for entry in results["classes"]:
            self.assertEqual(entry["coverage"]["trials"], 3)
        # Break one slot: it leaves the denominator and takes its code with it.
        os.remove(os.path.join(self.slots, "run-002", "completion.txt"))
        results = score_rates.score(self.slots, self.pins_path, self.family,
                                    self.prompt, self.golden,
                                    registry_sha256=self.registry)
        self.assertEqual(results["population"]["valid"], 2)
        self.assertEqual(results["population"]["invalidCodes"], {"no-completion": 1})
        for entry in results["classes"]:
            self.assertEqual(entry["coverage"]["trials"], 2)
        # Class 0 was reached only by the run that just left the population.
        by_index = {entry["index"]: entry["coverage"]["count"] for entry in results["classes"]}
        self.assertEqual(by_index, {0: 0, 1: 2, 2: 0, 3: 2, 4: 2, 5: 0})

    def test_the_published_intervals_are_exactly_the_registered_scope(self):
        """§4.3's frozen scope, asserted rather than left to two readings.

        The reviewed draft named the six primary rates, the all-six rate and
        S8, while the scorer also computed intervals for the raw, Q and Q-only
        intersections. Both are defensible; only one can be the registered
        scope, and it is now the wider one — those three ARE rates over the
        same V, and publishing a rate without its interval invites reading a
        point estimate as precise."""
        results = score_rates.score(self.slots, self.pins_path, self.family,
                                    self.prompt, self.golden,
                                    registry_sha256=self.registry)
        expected = set()
        for entry in results["classes"]:
            for member in ("coverage", "rawIntersection", "qIntersection",
                           "qOnlyIntersection"):
                expected.add(("classes", entry["index"], member))
                self.assertIsNotNone(entry[member]["ci95"], member)
        expected.add(("coverageBreadth", "allSix"))
        expected.add(("population", "pipelineInvalidRate"))
        self.assertIsNotNone(results["coverageBreadth"]["allSix"]["ci95"])
        self.assertIsNotNone(results["population"]["pipelineInvalidRate"]["ci95"])
        # Record-level pooled quantities carry none: records inside one
        # completion are not independent trials (§4.4 S5).
        self.assertNotIn("ci95", results["labelAccuracy"])
        found = set()

        def walk(node, path=()):
            if isinstance(node, dict):
                if "ci95" in node:
                    found.add(path)
                for key, value in node.items():
                    walk(value, path + (key,))
            elif isinstance(node, list):
                for index, item in enumerate(node):
                    walk(item, path + (index,))

        walk(results)
        self.assertEqual(len(found), len(expected),
                         "intervals are published at %r" % sorted(found))

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
