"""Tests for the reference derivation-rule implementation (SPEC.md).

The corpus replay is the fidelity anchor: every case's expected claim was
cross-checked to reproduce studies 006/007's original derive_payload on the
claim (facts, evidence availability, acquisition status, reason). The unit
tests pin the op semantics a clean-room second implementation must match.
"""

import json
import glob
import os
import unittest

import derive

HERE = os.path.dirname(os.path.abspath(__file__))
RULE = json.load(open(os.path.join(HERE, "rules", "screening.rule.json")))


class CorpusReplay(unittest.TestCase):
    def _rule(self, case):
        if isinstance(case["rule"], dict):
            return case["rule"]
        with open(os.path.join(HERE, case["rule"])) as handle:
            return json.load(handle)

    def test_every_corpus_case_matches_its_frozen_claim_or_rejects(self):
        cases = sorted(glob.glob(os.path.join(HERE, "corpus", "*.json")))
        self.assertGreaterEqual(len(cases), 21)
        for path in cases:
            with open(path) as handle:
                case = json.load(handle)
            name = os.path.basename(path)
            rule, artifact, params = self._rule(case), case["artifact"], case.get("params", {})
            if case.get("reject"):
                with self.assertRaises(derive.RuleError, msg="%s must reject" % name):
                    derive.derive(rule, artifact, params)
            else:
                got = derive.derive(rule, artifact, params)
                self.assertEqual(
                    derive.canon(got), derive.canon(case["expected"]),
                    "corpus case %s derived a different claim" % name,
                )


class Pointers(unittest.TestCase):
    def test_get_and_absent(self):
        doc = {"a": {"b": [10, 20]}, "n": None}
        self.assertEqual(derive.get(doc, "/a/b/1"), 20)
        self.assertIs(derive.get(doc, "/a/b/9"), derive._ABSENT)
        self.assertIs(derive.get(doc, "/missing"), derive._ABSENT)
        self.assertIsNone(derive.get(doc, "/n"))            # present null, not absent
        self.assertIs(derive.get(doc, "/n/x"), derive._ABSENT)  # descend into non-container

    def test_escaping(self):
        self.assertEqual(derive.get({"a/b": {"~x": 1}}, "/a~1b/~0x"), 1)


class Ops(unittest.TestCase):
    def _true(self, cond, art, params=None):
        return derive._evaluate(cond, art, params or {}, set())

    def test_equals_is_json_typed(self):
        self.assertTrue(self._true({"op": "equals", "field": "/s", "to": "found"}, {"s": "found"}))
        self.assertFalse(self._true({"op": "equals", "field": "/s", "to": 1}, {"s": True}))   # bool != number
        self.assertFalse(self._true({"op": "equals", "field": "/s", "to": "1"}, {"s": 1}))     # string != number
        self.assertTrue(self._true({"op": "equals", "field": "/s", "to": 1}, {"s": 1}))

    def test_is_true_is_strict(self):
        self.assertTrue(self._true({"op": "isTrue", "field": "/x"}, {"x": True}))
        for weird in (1, "true", "True", None):
            self.assertFalse(self._true({"op": "isTrue", "field": "/x"}, {"x": weird}))

    def test_is_decimal_string(self):
        for good in ("0", "2", "84000"):
            self.assertTrue(self._true({"op": "isDecimalString", "field": "/c"}, {"c": good}))
        for bad in ("02", "-1", "1.0", "", 2, True):
            self.assertFalse(self._true({"op": "isDecimalString", "field": "/c"}, {"c": bad}))

    def test_fresh_within_boundaries(self):
        params = {"asOf": "2026-07-30T12:00:00Z", "maxAge": 3600}
        cond = {"op": "freshWithin", "field": "/t", "asOf": "asOf", "maxAge": "maxAge"}
        self.assertTrue(self._true(cond, {"t": "2026-07-30T12:00:00Z"}, params))   # age 0
        self.assertTrue(self._true(cond, {"t": "2026-07-30T11:00:00Z"}, params))   # age = maxAge
        self.assertFalse(self._true(cond, {"t": "2026-07-30T10:59:59Z"}, params))  # age > maxAge
        self.assertFalse(self._true(cond, {"t": "2026-07-30T12:00:01Z"}, params))  # negative age (future)
        self.assertFalse(self._true(cond, {"t": "not-a-time"}, params))            # unparseable
        self.assertFalse(self._true(cond, {"t": "2026-07-30 12:00:00Z"}, params))  # wrong format (space)

    def test_short_circuit_reads_are_path_sensitive(self):
        # all short-circuits: /b is not read when /a is already false.
        reads = set()
        derive._evaluate({"op": "all", "of": [
            {"op": "equals", "field": "/a", "to": "no"},
            {"op": "exists", "field": "/b"}]}, {"a": "yes", "b": 1}, {}, reads)
        self.assertEqual(reads, {"/a"})


class Instant(unittest.TestCase):
    def test_epoch(self):
        self.assertEqual(derive.instant("1970-01-01T00:00:00Z"), 0)
        self.assertEqual(derive.instant("2026-07-30T12:00:00Z"), 1785412800)
        self.assertIsNone(derive.instant("2026-13-01T00:00:00Z"))  # bad month
        self.assertIsNone(derive.instant("2026-07-30T12:00:00"))   # no Z
        self.assertIsNone(derive.instant(5))


class Errors(unittest.TestCase):
    def _reject(self, rule, artifact=None, params=None):
        with self.assertRaises(derive.RuleError):
            derive.derive(rule, artifact or {}, params or {})

    def test_bad_rule_shapes(self):
        self._reject({"ruleVersion": "2", "clauses": [{"when": {"op": "always"}, "claim": {"acquisitionStatus": "unknown"}}]})
        self._reject({"ruleVersion": "1", "clauses": []})
        self._reject({"ruleVersion": "1", "clauses": [{"when": {"op": "exists", "field": "/x"}, "claim": {"acquisitionStatus": "unknown"}}]})  # no final always
        self._reject({"ruleVersion": "1", "clauses": [{"when": {"op": "nope"}, "claim": {"acquisitionStatus": "unknown"}}]})
        self._reject({"ruleVersion": "1", "parameters": {"p": "weird"}, "clauses": [{"when": {"op": "always"}, "claim": {"acquisitionStatus": "unknown"}}]})
        self._reject({"ruleVersion": "1", "clauses": [{"when": {"op": "always"}, "claim": {"acquisitionStatus": "maybe"}}]})

    def test_matched_claim_reading_absent_field_is_error(self):
        rule = {"ruleVersion": "1", "clauses": [
            {"when": {"op": "always"},
             "claim": {"facts": [{"pointer": "/f", "from": "/missing"}], "acquisitionStatus": "resolved"},
             "reason": "r"}]}
        self._reject(rule, {})

    def test_claim_outside_canon_domain_is_error(self):
        rule = {"ruleVersion": "1", "clauses": [
            {"when": {"op": "always"},
             "claim": {"facts": [{"pointer": "/f", "from": "/x"}], "acquisitionStatus": "resolved"},
             "reason": "r"}]}
        self._reject(rule, {"x": 1.5})  # a float copied into the claim


if __name__ == "__main__":
    unittest.main()
