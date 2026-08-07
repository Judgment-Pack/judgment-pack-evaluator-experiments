#!/usr/bin/env python3
"""The exact interval, checked against values that do not come from this code.

The primary endpoint is a rate with a Clopper-Pearson 95% interval, computed as
PREREGISTRATION.md §4.3 registers it: exact rational binomial tails, math.comb,
and exactly 200 halvings with no early exit. The cases below are the six
registered test vectors at n = 50, the design brief's independent n = 10 case,
the closed forms of the two degenerate ends, the interval's own symmetry, and
the tail identity each bound claims to satisfy. A test that only compared the
code to itself would prove nothing.
"""
from __future__ import annotations
import inspect
import unittest
from fractions import Fraction

import score_rates

# PREREGISTRATION.md §4.3, n = 50, four decimals.
REGISTERED = {
    0: (0.0000, 0.0711),
    1: (0.0005, 0.1065),
    25: (0.3553, 0.6447),
    40: (0.6628, 0.8997),
    45: (0.7819, 0.9667),
    50: (0.9289, 1.0000),
}


class ClopperPearson(unittest.TestCase):

    def test_the_registered_test_vectors(self):
        for k, (lower, upper) in REGISTERED.items():
            got_lower, got_upper = score_rates.clopper_pearson(k, 50)
            self.assertEqual(round(got_lower, 4), lower, "lower bound at k=%d" % k)
            self.assertEqual(round(got_upper, 4), upper, "upper bound at k=%d" % k)

    def test_the_design_briefs_independent_case(self):
        lower, upper = score_rates.clopper_pearson(5, 10)
        self.assertEqual(round(lower, 4), 0.1871)
        self.assertEqual(round(upper, 4), 0.8129)

    def test_the_degenerate_ends_match_their_closed_forms(self):
        # k = n: P(X = n | p) = p^n = alpha at the lower bound; k = 0:
        # P(X = 0 | p) = (1-p)^n = alpha at the upper bound.
        for n in (1, 3, 13, 50):
            lower, upper = score_rates.clopper_pearson(0, n)
            self.assertEqual(lower, 0.0)
            self.assertAlmostEqual(upper, 1.0 - 0.025 ** (1.0 / n), places=9)
            lower, upper = score_rates.clopper_pearson(n, n)
            self.assertAlmostEqual(lower, 0.025 ** (1.0 / n), places=9)
            self.assertEqual(upper, 1.0)

    def test_the_interval_is_symmetric_under_success_failure_exchange(self):
        for n in (7, 13):
            for k in range(n + 1):
                lower, upper = score_rates.clopper_pearson(k, n)
                mirrored_lower, mirrored_upper = score_rates.clopper_pearson(n - k, n)
                self.assertAlmostEqual(lower, 1.0 - mirrored_upper, places=9)
                self.assertAlmostEqual(upper, 1.0 - mirrored_lower, places=9)

    def test_the_interval_contains_the_point_estimate_and_widens_with_less_data(self):
        for n in (5, 20):
            for k in range(n + 1):
                lower, upper = score_rates.clopper_pearson(k, n)
                self.assertLessEqual(lower, k / n)
                self.assertLessEqual(k / n, upper)
        wide = score_rates.clopper_pearson(5, 10)
        narrow = score_rates.clopper_pearson(25, 50)
        self.assertGreater(wide[1] - wide[0], narrow[1] - narrow[0])

    def test_a_bound_is_the_tail_root_it_claims_to_be(self):
        # The definition, not the implementation: at the lower bound the
        # chance of seeing k or more is alpha, to within one halving.
        lower, upper = score_rates.clopper_pearson(3, 11)
        self.assertAlmostEqual(
            float(score_rates._tail_ge(3, 11, Fraction(lower))), 0.025, places=9)
        self.assertAlmostEqual(
            float(score_rates._tail_le(3, 11, Fraction(upper))), 0.025, places=9)

    def test_the_tails_are_exact_rationals_not_floats(self):
        value = score_rates._tail_ge(1, 4, Fraction(1, 2))
        self.assertIsInstance(value, Fraction)
        self.assertEqual(value, Fraction(15, 16))
        self.assertEqual(score_rates._tail_le(4, 4, Fraction(1, 3)), Fraction(1))

    def test_nonsense_counts_refuse(self):
        with self.assertRaises(ValueError):
            score_rates.clopper_pearson(0, 0)
        with self.assertRaises(ValueError):
            score_rates.clopper_pearson(4, 3)
        with self.assertRaises(ValueError):
            score_rates.clopper_pearson(-1, 3)

    def test_rate_block_reports_a_rate_only_with_its_integers_and_interval(self):
        block = score_rates.rate_block(3, 4)
        self.assertEqual(block["count"], 3)
        self.assertEqual(block["trials"], 4)
        self.assertEqual(block["rate"], 0.75)
        self.assertEqual(len(block["ci95"]), 2)
        empty = score_rates.rate_block(0, 0)
        self.assertIsNone(empty["rate"])
        self.assertIsNone(empty["ci95"])


class ReviewTiers(unittest.TestCase):
    """§5's mapping, applied from thresholds registered before the batch.

    One criterion in one unit: the exact lower bound. The earlier draft
    conjoined `c_i >= 0.90` with `lower >= 0.80`, which made the operative
    cut in observed-coverage units a function of V — 0.92 at V=50, 0.933 at
    V=45, 0.95 at V=40 — while calling itself frozen. These cases pin the
    boundary in the unit the rule is stated in.
    """

    def tier(self, k, n, share=0.0):
        return score_rates.review_tier(score_rates.rate_block(k, n), share)

    def test_the_three_tiers_come_out_where_the_thresholds_put_them(self):
        self.assertEqual(self.tier(50, 50)["tier"], "LIGHT")
        self.assertEqual(self.tier(30, 50)["tier"], "STANDARD")
        self.assertEqual(self.tier(10, 50)["tier"], "FULL")
        # The bound decides, and it carries the sample size: 9 of 10 is a
        # higher point estimate than 46 of 50 and a much weaker one.
        self.assertEqual(self.tier(9, 10)["base"], "STANDARD")

    def test_the_registered_boundaries_at_fifty_valid_runs(self):
        # §5's table: LIGHT begins at k = 46 of 50 and STANDARD at k = 28.
        self.assertEqual(self.tier(46, 50)["base"], "LIGHT")
        self.assertEqual(self.tier(45, 50)["base"], "STANDARD")
        self.assertEqual(self.tier(28, 50)["base"], "STANDARD")
        self.assertEqual(self.tier(27, 50)["base"], "FULL")

    def test_the_operating_characteristics_are_the_ones_section_5_registers(self):
        # §5 commits these numbers before the data, computed with this study's
        # own machinery: at N = 50 a class whose true coverage is exactly the
        # old 0.90 threshold is called LIGHT less than half the time.
        characteristics = score_rates.light_operating_characteristics(
            50, [Fraction(17, 20), Fraction(9, 10), Fraction(19, 20), Fraction(99, 100)])
        self.assertEqual(characteristics["lightThresholdK"], 46)
        self.assertEqual(characteristics["lightThresholdRate"], 0.92)
        registered = {"17/20": 0.1121, "9/10": 0.4312, "19/20": 0.8964, "99/100": 0.9999}
        for probability, expected in registered.items():
            self.assertEqual(round(characteristics["probabilities"][probability], 4),
                             expected, probability)

    def test_the_mislabel_escalation_moves_exactly_one_step_and_full_is_terminal(self):
        self.assertEqual(self.tier(50, 50, share=0.2)["tier"], "STANDARD")
        self.assertEqual(self.tier(50, 50, share=0.19)["tier"], "LIGHT")
        self.assertEqual(self.tier(10, 50, share=0.5)["tier"], "FULL")

    def test_the_pipeline_rate_does_not_enter_a_tier_at_all(self):
        # Registered change from the draft: a high pipeline-invalid rate is one
        # stated caution over the batch, not a per-class escalation. It already
        # shrank V and widened every interval; charging it again would count
        # one event twice.
        self.assertEqual(len(inspect.signature(score_rates.review_tier).parameters), 2)
        self.assertEqual(self.tier(50, 50)["tier"], "LIGHT")

    def test_no_valid_run_means_no_tier_rather_than_a_default(self):
        self.assertIsNone(score_rates.review_tier(
            score_rates.rate_block(0, 0), None)["tier"])


class RowComposition(unittest.TestCase):
    """§5's row-level rule, which was not a total function.

    The classes are not disjoint, so "the class its facts fall in" left a row
    matching two classes of different depths undefined, and a row matching no
    class undefined as well. Two clauses close it, and they are code rather
    than prose so the gap cannot reopen.
    """

    def test_a_row_in_one_class_takes_that_class_tier(self):
        for tier in score_rates.TIERS:
            self.assertEqual(score_rates.row_review_tier([tier]), tier)

    def test_a_row_in_several_classes_takes_the_strictest(self):
        # The worked example from the review: a non-embargoed score-70 row
        # matches classes 0 and 1, and their tiers can differ.
        self.assertEqual(score_rates.row_review_tier(["STANDARD", "LIGHT"]), "STANDARD")
        self.assertEqual(score_rates.row_review_tier(["LIGHT", "FULL", "STANDARD"]),
                         "FULL")
        self.assertEqual(score_rates.row_review_tier(["LIGHT", "LIGHT"]), "LIGHT")

    def test_a_row_in_no_registered_class_takes_full(self):
        # This study measured six predicates; it says nothing about a row
        # outside all of them, and "nothing is known" reads as full review.
        self.assertEqual(score_rates.row_review_tier([]), "FULL")

    def test_a_tier_this_study_does_not_register_refuses(self):
        with self.assertRaises(score_rates.ScoreError):
            score_rates.row_review_tier(["NONE"])


class RegisteredIllustrations(unittest.TestCase):
    """The numbers §2.4 and §9 use to say what N = 50 buys.

    The reviewed draft printed 0.9209 at V = 45 and 0.9114 at V = 40 for a
    perfect class; solving p^V = 0.025 independently gives 0.9213 and 0.9119.
    The scorer was right and the prose was wrong, which is the direction that
    matters least and is still a registered claim the code does not support.
    """

    def prose(self) -> str:
        import os

        study = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        with open(os.path.join(study, "PREREGISTRATION.md"), "rb") as handle:
            return handle.read().decode("utf-8")

    def test_the_perfect_class_bounds_are_the_ones_the_code_computes(self):
        body = self.prose()
        for trials in (50, 45, 40):
            computed = "%.4f" % score_rates.lower_bound(trials, trials)
            self.assertIn(computed, body,
                          "§2.4/§9 do not carry the V=%d bound %s" % (trials, computed))
        for wrong in ("0.9209", "0.9114"):
            self.assertNotIn(wrong, body, "a superseded bound survives in the prose")

    def test_the_registered_v50_table_is_the_one_the_code_computes(self):
        body = self.prose()
        for k, (lower, upper) in REGISTERED.items():
            self.assertEqual(round(score_rates.lower_bound(k, 50), 4), lower)
            self.assertEqual(round(score_rates.upper_bound(k, 50), 4), upper)
        self.assertIn("k = 50 → [0.9289, 1.0000]", body)


if __name__ == "__main__":
    unittest.main()
