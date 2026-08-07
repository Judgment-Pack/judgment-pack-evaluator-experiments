#!/usr/bin/env python3
"""The counting control: a synthetic completion with a coverage profile known
by construction, run through the ported compiler, the ported mirror, and the
scorer's class arithmetic.

This is the brief's control (b). If the counting code miscounts, the study's
whole output is a number nobody can check; here the answer is fixed in
fixtures.PROFILE_A before any code runs — which records are accepted, which are
dropped and why, which are H and which Q, and exactly which of the six classes
each set reaches. The classes are not disjoint (0 ⊂ 1, and 2 ⊂ 3), so a
profile that only tested membership one class at a time would miss the overlap
this fixture puts back in.
"""
from __future__ import annotations
import os
import unittest

import fixtures
import policy_mirror
import records_compile
import score_rates

STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CompilerAndClassifier(unittest.TestCase):

    def setUp(self):
        pins = score_rates.load_json(os.path.join(STUDY, "harness", "PINS.json"))
        self.classes = score_rates.load_family(os.path.join(STUDY, "FAMILY.json"),
                                               pins["family"]["sha256"])
        accepted, ledger, span = records_compile.compile_records(fixtures.COMPLETION_A)
        self.accepted, self.ledger, self.span = accepted, ledger, span

    def test_the_fixture_compiles_to_the_expected_records(self):
        self.assertEqual(sorted(self.accepted), fixtures.PROFILE_A["accepted"])
        drops = {}
        for _, case_id, drop in self.ledger:
            if not case_id:
                drops[drop] = drops.get(drop, 0) + 1
        self.assertEqual(drops, fixtures.PROFILE_A["dropCodes"])
        # The array wins extraction over the bracketed aside in the preamble.
        self.assertEqual(self.span[2], len(fixtures.COMPLETION_A))
        self.assertGreater(self.span[0], 0)

    def test_h_and_q_are_the_expected_split(self):
        high, quarantine = score_rates.split_records(self.accepted)
        self.assertEqual(high, fixtures.PROFILE_A["h"])
        self.assertEqual(quarantine, fixtures.PROFILE_A["q"])
        # Q is discordance, spelled out: the mirror and the record disagree.
        record = self.accepted["aurora-payments-eu"]
        self.assertEqual(policy_mirror.verdict(record["vendor"]), "manual-review")
        self.assertEqual(record["decision"]["outcome"], "clear")

    def test_each_class_holds_exactly_the_records_the_profile_names(self):
        high, quarantine = score_rates.split_records(self.accepted)
        for entry in self.classes:
            expected = fixtures.PROFILE_A["members"][str(entry["index"])]
            self.assertEqual(
                score_rates.class_members(self.accepted, high, entry["predicate"]),
                expected["h"], "class %d H membership" % entry["index"])
            self.assertEqual(
                score_rates.class_members(self.accepted, quarantine, entry["predicate"]),
                expected["q"], "class %d Q membership" % entry["index"])

    def test_the_second_fixture_adds_exactly_the_boundary_class(self):
        accepted, _, _ = records_compile.compile_records(fixtures.COMPLETION_B)
        self.assertEqual(sorted(accepted), fixtures.PROFILE_B["accepted"])
        high, _ = score_rates.split_records(accepted)
        covered = [entry["index"] for entry in self.classes
                   if score_rates.class_members(accepted, high, entry["predicate"])]
        self.assertEqual(covered, fixtures.PROFILE_B["covered"])
        # The added record sits at exactly 70, which is class 0 AND class 1:
        # coverage is per-predicate non-emptiness, not a partition.
        self.assertEqual(accepted["stonebridge-logistics"]["vendor"]["riskScore"], "70")

    def test_every_drop_code_is_reachable_and_lands_where_it_should(self):
        accepted, ledger, _ = records_compile.compile_records(fixtures.COMPLETION_DROPS)
        drops = {}
        for _, case_id, drop in ledger:
            if not case_id:
                drops[drop] = drops.get(drop, 0) + 1
        self.assertEqual(drops, fixtures.DROP_HISTOGRAM)
        self.assertEqual(sorted(accepted), ["ridgeline-supplies"])

    def test_a_completion_with_no_array_is_an_authoring_outcome(self):
        # §3.3: the compiler refuses, and that refusal is authoring-empty
        # (valid, covering nothing) rather than a pipeline failure. The
        # scorer's admit() applies that rule; here the refusal itself.
        with self.assertRaises(records_compile.CompileError):
            records_compile.compile_records(fixtures.COMPLETION_EMPTY)

    def test_study_010s_retained_completion_reproduces_its_published_profile(self):
        """C3, the replication control: this study's counting code must mean
        what its predecessor's did, on the bytes 010 actually retained."""
        pins = score_rates.load_json(os.path.join(STUDY, "harness", "PINS.json"))
        replication = pins["replication"]
        completion = os.path.normpath(os.path.join(STUDY, replication["path"]))
        self.assertEqual(score_rates.file_digest(completion), replication["sha256"])
        accepted, _, _ = records_compile.compile_records(
            records_compile.read_completion(completion))
        high, quarantine = score_rates.split_records(accepted)
        expected = replication["expected"]
        self.assertEqual(len(accepted), expected["accepted"])
        self.assertEqual(len(high), expected["h"])
        self.assertEqual(len(quarantine), expected["q"])
        self.assertEqual(
            [len(score_rates.class_members(accepted, high, entry["predicate"]))
             for entry in self.classes], expected["hClassCounts"])
        self.assertEqual(
            [len(score_rates.class_members(accepted, quarantine, entry["predicate"]))
             for entry in self.classes], expected["qClassCounts"])

    def test_the_family_is_read_at_its_pinned_digest_only(self):
        with self.assertRaises(score_rates.ScoreError):
            score_rates.load_family(os.path.join(STUDY, "FAMILY.json"),
                                    "sha256:" + "0" * 64)

    def test_the_mirror_is_the_reference_semantics_on_the_policy_boundaries(self):
        # Not a fixture claim: POLICY.md P1-P5, read off the mirror at the
        # values the classes live on.
        def vendor(sanctions, country, personal, score):
            return {"sanctionsHit": sanctions, "registeredCountry": country,
                    "handlesPersonalData": personal, "riskScore": score}
        self.assertEqual(policy_mirror.verdict(vendor(True, "NL", False, "0")), "reject")
        self.assertEqual(policy_mirror.verdict(vendor(False, "SY", False, "1")), "reject")
        self.assertEqual(policy_mirror.verdict(vendor(False, "NL", False, "70")),
                         "manual-review")
        self.assertEqual(policy_mirror.verdict(vendor(False, "NL", False, "69.9")), "clear")
        self.assertEqual(policy_mirror.verdict(vendor(False, "NL", True, "40")),
                         "manual-review")
        self.assertEqual(policy_mirror.verdict(vendor(False, "NL", True, "39.99")), "clear")


if __name__ == "__main__":
    unittest.main()
