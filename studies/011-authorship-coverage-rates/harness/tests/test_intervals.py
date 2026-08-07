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
    """§5's mapping, applied from thresholds registered before the batch."""

    def tier(self, k, n, share=0.0, pipeline=0.0):
        return score_rates.review_tier(score_rates.rate_block(k, n), share, pipeline)

    def test_the_three_tiers_come_out_where_the_thresholds_put_them(self):
        self.assertEqual(self.tier(50, 50)["tier"], "LIGHT")
        self.assertEqual(self.tier(30, 50)["tier"], "STANDARD")
        self.assertEqual(self.tier(10, 50)["tier"], "FULL")
        # A high rate with an interval that does not clear 0.80 is not LIGHT:
        # the bound, not the point estimate, decides.
        self.assertEqual(self.tier(9, 10)["base"], "STANDARD")

    def test_each_escalation_moves_exactly_one_step_and_full_is_terminal(self):
        self.assertEqual(self.tier(50, 50, share=0.2)["tier"], "STANDARD")
        self.assertEqual(self.tier(50, 50, pipeline=0.1)["tier"], "STANDARD")
        self.assertEqual(self.tier(50, 50, share=0.2, pipeline=0.1)["tier"], "FULL")
        self.assertEqual(self.tier(10, 50, share=0.5, pipeline=0.5)["tier"], "FULL")

    def test_no_valid_run_means_no_tier_rather_than_a_default(self):
        self.assertIsNone(score_rates.review_tier(
            score_rates.rate_block(0, 0), None, None)["tier"])


if __name__ == "__main__":
    unittest.main()
