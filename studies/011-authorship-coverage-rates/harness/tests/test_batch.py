#!/usr/bin/env python3
"""The batch driver end to end, against a stand-in CLI.

The real wrapper runs: the same bash, the same `env -i` scrub, the same fresh
HOME and CODEX_HOME per run, the same binary-digest check (the stand-in's
digest is pinned in a test registry, so the check passes because it was
satisfied, not because it was skipped), the same slot retention, and the real
§3.2 recapture with the probe prompt. Only the binary is a stand-in, and it
never reaches a network or a model.

What this proves that a unit test cannot: that a failing run terminates its own
slot with a refusal record and the batch CONTINUES — the registered difference
from Study 010 — that an admissible run whose completion holds no array is
counted as a valid authoring-empty run rather than dropped, and that the slots
the wrapper writes are the slots the scorer reads, all the way to the rate
table.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import unittest

import batch
import fixtures
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))

# Plan: two probe captures for the golden recapture, then the batch — two
# identical completions, one that also reaches the boundary class, one that
# holds no array at all, and one failure.
PLAN = [
    {"completion": "ready"},
    {"completion": "ready"},
    {"completion": fixtures.COMPLETION_A},
    {"completion": fixtures.COMPLETION_B},
    {"completion": fixtures.COMPLETION_A},
    {"completion": fixtures.COMPLETION_EMPTY},
    {"completion": fixtures.COMPLETION_A, "exit": 3},
]
BATCH_RUNS = 5


class Batch(unittest.TestCase):

    def setUp(self):
        import shutil
        import tempfile
        self.root = tempfile.mkdtemp(prefix="s011-batch-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.scratch = os.path.join(self.root, "scratch")
        os.makedirs(self.scratch)
        self.cli = fixtures.write_fake_cli(os.path.join(self.root, "cli"), PLAN,
                                           sys.executable, HERE)
        with open(os.path.join(STUDY, "harness", "PINS.json")) as handle:
            pins = json.load(handle)
        pins["codex"]["binarySha256"] = batch._digest(self.cli)
        pins["codex"]["version"] = "codex-cli 0.145.0-fake"
        pins["batch"]["runs"] = BATCH_RUNS
        self.pins_path = os.path.join(self.root, "PINS.json")
        with open(self.pins_path, "w") as handle:
            json.dump(pins, handle, indent=2)
        self.pins = pins
        self.captures = os.path.join(self.root, "recapture")
        self.slots = os.path.join(self.root, "authoring")
        self.golden = os.path.join(self.root, "GOLDEN-CONTEXT.json")

    def run_batch(self, slots: str, extra=()):
        return batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--slots", slots, "--pins", self.pins_path,
                           "--cli-override", self.cli] + list(extra))

    def capture(self, extra=()):
        return batch.main(["batch.py", "capture", "--scratch-parent", self.scratch,
                           "--captures", self.captures, "--out", self.golden,
                           "--pins", self.pins_path, "--cli-override", self.cli]
                          + list(extra))

    def score(self):
        return score_rates.score(self.slots, self.pins_path,
                                 os.path.join(STUDY, "FAMILY.json"),
                                 os.path.join(STUDY, "transcription", "PROMPT.txt"),
                                 self.golden)

    def recapture_then_batch(self):
        """The registered order: capture, agree, then the batch."""
        self.assertEqual(self.capture(), 0)
        self.assertEqual(self.run_batch(self.slots), 0)

    def test_a_dry_run_creates_nothing(self):
        self.assertEqual(self.run_batch(self.slots, ["--runs", "3", "--dry-run"]), 0)
        self.assertFalse(os.path.exists(self.slots))

    def unpinned_cli(self) -> str:
        other = fixtures.write_fake_cli(os.path.join(self.root, "cli2"), PLAN,
                                        sys.executable, HERE)
        with open(other, "a") as handle:
            handle.write("# a different binary\n")
        return other

    def test_a_cli_that_is_not_the_pinned_one_never_reaches_a_call(self):
        code = batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--slots", self.slots, "--pins", self.pins_path,
                           "--cli-override", self.unpinned_cli(), "--runs", "1"])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(self.slots))

    def test_the_wrapper_checks_the_digest_itself_not_only_the_driver(self):
        # The operator can run one call by hand; the pin has to hold there too.
        environment = dict(os.environ)
        environment["PYTHON_BIN"] = sys.executable
        completed = subprocess.run(
            ["bash", os.path.join(STUDY, "transcription", "authoring_call.sh"),
             self.scratch, os.path.join(self.slots, "run-001"), self.pins_path,
             self.unpinned_cli()],
            capture_output=True, text=True, env=environment)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the pinned", completed.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "run-001")))

    def test_the_recapture_uses_the_probe_prompt_and_agrees_with_itself(self):
        self.assertEqual(self.capture(), 0)
        golden = json.load(open(self.golden))
        self.assertEqual(golden["capturedFrom"], ["capture-001", "capture-002"])
        self.assertTrue(golden["entries"])
        for name in golden["capturedFrom"]:
            call = json.load(open(os.path.join(self.captures, name, "CALL.json")))
            self.assertEqual(call["promptKind"], "probe")
            self.assertEqual(call["promptSha256"], self.pins["probePrompt"]["sha256"])
        # The registered prompt never ran: no capture answered with records.
        for name in golden["capturedFrom"]:
            with open(os.path.join(self.captures, name, "completion.txt")) as handle:
                self.assertEqual(handle.read(), "ready")

    def test_a_registered_capture_is_never_rewritten(self):
        self.assertEqual(self.capture(), 0)
        self.assertEqual(batch.main(["batch.py", "capture-golden", "--slots",
                                     self.captures, "--out", self.golden]), 1)

    def test_the_slots_are_the_shape_the_scorer_reads(self):
        self.recapture_then_batch()
        for name in ("run-001", "run-002", "run-003", "run-004"):
            slot = os.path.join(self.slots, name)
            for retained in ("CALL.json", "stdout.raw", "stderr.raw", "session.jsonl",
                             "context.json", "completion.txt"):
                self.assertTrue(os.path.isfile(os.path.join(slot, retained)),
                                "%s/%s" % (name, retained))
        call = json.load(open(os.path.join(self.slots, "run-001", "CALL.json")))
        self.assertEqual(call["model"], self.pins["codex"]["model"])
        self.assertEqual(call["binarySha256"], self.pins["codex"]["binarySha256"])
        self.assertEqual(call["promptKind"], "registered")
        self.assertEqual(call["slotIndex"], 1)
        self.assertTrue(call["homeIsolated"] and call["environmentScrubbed"])
        # Isolation, demonstrated per run: the isolated home held nothing but
        # the credential (or nothing at all where none exists to copy).
        self.assertLessEqual(call["isolatedHomeEntriesBefore"], 1)

    def test_a_failing_run_is_refused_and_the_batch_continues(self):
        self.recapture_then_batch()
        self.assertEqual(sorted(os.listdir(self.slots)),
                         ["BATCH.json"] + ["run-00%d" % index
                                           for index in range(1, BATCH_RUNS + 1)])
        refusal = json.load(open(os.path.join(self.slots, "run-005", "REFUSAL.json")))
        self.assertEqual(refusal["code"], "call-nonzero-exit")
        self.assertEqual(refusal["wrapperExit"], 10)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "run-005", "completion.txt")))
        ledger = json.load(open(os.path.join(self.slots, "BATCH.json")))
        self.assertEqual([row["code"] for row in ledger["runs"]],
                         [None, None, None, None, "call-nonzero-exit"])

    def test_a_retained_slot_is_never_rewritten(self):
        self.recapture_then_batch()
        self.assertEqual(self.run_batch(self.slots), 1)

    def test_an_incomplete_batch_is_not_scorable_until_the_shortfall_is_declared(self):
        self.assertEqual(self.capture(), 0)
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        with self.assertRaises(score_rates.ScoreError):
            self.score()
        self.assertEqual(batch.main(["batch.py", "shortfall", "--slots", self.slots,
                                     "--pins", self.pins_path, "--reason",
                                     "the stand-in CLI batch was cut short on purpose"]), 0)
        results = self.score()
        self.assertEqual(results["population"]["slots"], 2)
        self.assertEqual(results["population"]["shortfall"], BATCH_RUNS - 2)
        self.assertIn("cut short", results["population"]["shortfallDeclaration"]["reason"])

    def test_the_scored_rates_are_the_profile_the_fixtures_fix(self):
        self.recapture_then_batch()
        results = self.score()
        population = results["population"]
        self.assertEqual(population["slots"], BATCH_RUNS)
        self.assertEqual(population["valid"], 4)
        self.assertEqual(population["invalid"], 1)
        self.assertEqual(population["invalidCodes"], {"call-nonzero-exit": 1})
        self.assertEqual(population["pipelineInvalidRate"]["rate"], 0.2)
        self.assertEqual(population["authoringEmpty"], 1)
        self.assertEqual(population["unexpectedEntries"], [])
        self.assertEqual(population["shortfall"], 0)

        expected = {0: 1, 1: 3, 2: 0, 3: 3, 4: 3, 5: 0}
        for entry in results["classes"]:
            block = entry["coverage"]
            self.assertEqual(block["trials"], 4)
            self.assertEqual(block["count"], expected[entry["index"]],
                             "class %d coverage" % entry["index"])
        raw = {entry["index"]: entry["rawIntersection"]["count"] for entry in results["classes"]}
        self.assertEqual(raw, {0: 1, 1: 3, 2: 3, 3: 3, 4: 3, 5: 0})
        q_only = {entry["index"]: entry["qOnlyIntersection"]["count"]
                  for entry in results["classes"]}
        self.assertEqual(q_only, {0: 0, 1: 0, 2: 3, 3: 0, 4: 0, 5: 0})
        q_any = {entry["index"]: entry["qIntersection"]["count"] for entry in results["classes"]}
        self.assertEqual(q_any, {0: 0, 1: 0, 2: 3, 3: 3, 4: 0, 5: 0})
        # S2's mislabel share: class 2 was reached in three runs and never by
        # a correctly-labelled record, so the share is 1.0 and §5 escalates.
        shares = {entry["index"]: entry["mislabelShare"] for entry in results["classes"]}
        self.assertEqual(shares[2], 1.0)
        self.assertEqual(shares[3], 0.0)
        self.assertEqual(shares[5], 0.0)

        # 3/4 with an exact interval, and the drift sequence in run order.
        one = [entry for entry in results["classes"] if entry["index"] == 1][0]
        self.assertEqual(one["coverage"]["rate"], 0.75)
        self.assertEqual(round(one["coverage"]["ci95"][0], 4), 0.1941)
        self.assertEqual(round(one["coverage"]["ci95"][1], 4), 0.9937)
        self.assertEqual(one["drift"]["sequence"], [1, 1, 1, 0])

        self.assertEqual(results["coverageBreadth"]["distribution"],
                         {"0": 1, "1": 0, "2": 0, "3": 2, "4": 1, "5": 0, "6": 0})
        self.assertEqual(results["coverageBreadth"]["allSix"]["count"], 0)
        self.assertEqual(results["labelAccuracy"]["h"], 13)
        self.assertEqual(results["labelAccuracy"]["q"], 3)
        self.assertEqual(results["labelAccuracy"]["rate"], 0.8125)
        self.assertEqual(results["records"]["acceptedTotal"], 16)
        self.assertEqual(results["records"]["droppedTotal"], 6)
        self.assertEqual(results["records"]["dropCodes"],
                         {"decimal-form": 3, "duplicate-id": 3})
        self.assertEqual(results["distinctOutputs"]["distinctCompletions"], 3)
        self.assertEqual(results["distinctOutputs"]["largestIdenticalGroup"], 2)
        self.assertEqual([row["slot"] for row in results["runs"]],
                         ["run-00%d" % index for index in range(1, BATCH_RUNS + 1)])
        self.assertEqual([row["coveredClasses"] for row in results["runs"][:4]],
                         [[1, 3, 4], [0, 1, 3, 4], [1, 3, 4], []])
        self.assertTrue(results["runs"][3]["authoringEmpty"])
        self.assertTrue(results["runs"][3]["noParseableArray"])
        self.assertTrue(results["runs"][3]["valid"])
        self.assertFalse(results["runs"][4]["valid"])

    def test_the_report_renders_every_class_run_and_tier(self):
        self.recapture_then_batch()
        report = score_rates.render_markdown(self.score())
        for entry in ("run-001", "run-005", "call-nonzero-exit", "Clopper-Pearson",
                      "authoring-empty", "FULL", "Byte-lineage, not truth"):
            self.assertIn(entry, report)
        self.assertEqual(report.count("| 0 | no sanctions hit"), 1)


if __name__ == "__main__":
    unittest.main()
