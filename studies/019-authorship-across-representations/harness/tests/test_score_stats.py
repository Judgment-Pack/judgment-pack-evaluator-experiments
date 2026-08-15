"""The interval arithmetic, against the numbers a predecessor already published.

Two ports, two authorities. The Clopper-Pearson half answers to Study 012's
registered test vectors — reproducing a number 012 PRINTED is what makes this a
port rather than a rewrite. The contrast half answers to
`design/mutants/oc_table.py`, whose own header states the reduction the
registered decision rests on, and to the exact-arithmetic discipline both
sources impose: nothing a decision reads may be a float.
"""
from fractions import Fraction

import pytest

from e4lib import stats


# --- PORT 1: Study 012's registered vectors ---------------------------------

def test_the_registered_vectors_reproduce():
    """Every (n, k) Study 012 published, to the four decimals it published.

    This is the port's whole warrant. If the arithmetic here drifts from 012's,
    a number a previous study printed stops reproducing and the suite says so
    before anything is scored."""
    for n, rows in sorted(stats.REGISTERED_VECTORS.items()):
        for k, (low, high) in sorted(rows.items()):
            observed = stats.clopper_pearson(k, n)
            assert round(observed[0], 4) == low, (n, k, "lower")
            assert round(observed[1], 4) == high, (n, k, "upper")


def test_n_is_50_because_that_is_this_studys_denominator():
    """Section 2 registers N = 50 runs per arm, so 012's n = 50 row is not a
    control here — it is the row this study will actually read."""
    assert 50 in stats.REGISTERED_VECTORS
    assert stats.clopper_pearson(50, 50)[1] == 1.0
    assert stats.clopper_pearson(0, 50)[0] == 0.0


def test_the_degenerate_ends_are_pinned_not_bisected():
    for n in (1, 30, 50):
        assert stats.lower_bound(0, n) == 0.0
        assert stats.upper_bound(n, n) == 1.0


def test_the_bounds_are_monotone_in_k():
    lows = [stats.lower_bound(k, 50) for k in range(0, 51, 5)]
    highs = [stats.upper_bound(k, 50) for k in range(0, 51, 5)]
    assert lows == sorted(lows)
    assert highs == sorted(highs)


def test_a_count_that_is_not_a_count_refuses():
    with pytest.raises(stats.StatsError) as raised:
        stats.clopper_pearson(51, 50)
    assert str(raised.value).startswith("CP-NOT-A-COUNT")
    with pytest.raises(stats.StatsError) as raised:
        stats.clopper_pearson(0, 0)
    assert str(raised.value).startswith("CP-NO-TRIALS")


def test_probability_at_least_is_exact_rational():
    value = stats.probability_at_least(1, 2, Fraction(1, 3))
    assert isinstance(value, Fraction)
    assert value == Fraction(5, 9)


def test_rate_block_never_publishes_a_rate_without_its_denominator():
    block = stats.rate_block(3, 50, "admitted runs")
    assert block["denominator"] == "admitted runs"
    assert block["count"] == 3 and block["trials"] == 50
    assert block["ci95"][0] < block["rate"] < block["ci95"][1]
    empty = stats.rate_block(0, 0, "admitted runs")
    assert empty["rate"] is None and empty["ci95"] is None
    assert empty["denominator"] == "admitted runs"


# --- PORT 2: the registered contrast ----------------------------------------

def test_the_ordering_statistic_is_exact_rational():
    """A float here could silently flip a decision, which is the reason
    oc_table.py's header gives for the whole construction."""
    table = stats.z2_table(4)
    assert isinstance(table[3][1], Fraction)
    assert table[3][1] == Fraction(8 * (3 - 1) ** 2, 4 * (8 - 4))
    # s = 0 and s = 2N force x = y: no difference, no evidence.
    assert table[0][0] == 0 and table[4][4] == 0


def test_the_critical_level_at_the_registered_n_is_the_prototypes():
    """`design/mutants/oc_table.py` computes c* = 625/154 with realised size
    just under alpha at N = 50. The port reproduces both."""
    cstar, size = stats.critical_level_at(50)
    assert cstar == Fraction(625, 154)
    assert size <= stats.FM_ALPHA
    assert float(size) == pytest.approx(0.0487960, abs=1e-6)


def test_the_critical_level_is_memoised_and_stable():
    first = stats.critical_level_at(50)
    second = stats.critical_level_at(50)
    assert first == second
    assert first is second


def test_zero_exclusion_decides_direction_as_observed():
    """Section 1: "Direction is reported as observed" — the machinery reports
    which side is above and never presupposes it."""
    above = stats.excludes_zero(50, 10, 50)
    assert above["excludesZero"] and above["decision"] == stats.DECIDED_LEFT
    below = stats.excludes_zero(10, 50, 50)
    assert below["excludesZero"] and below["decision"] == stats.DECIDED_RIGHT
    assert above["difference"] == -below["difference"]


def test_an_equal_pair_is_always_indeterminate():
    """x == y is no difference at any N, and the registered rule licenses
    nothing there — not equivalence, not either direction's negation."""
    for k in (0, 1, 25, 49, 50):
        result = stats.excludes_zero(k, k, 50)
        assert result["decision"] == stats.INDETERMINATE
        assert result["excludesZero"] is False


def test_a_small_gap_at_the_registered_n_is_indeterminate():
    """Section 5 states plainly that "a true 0.25 gap can still return
    INDETERMINATE", so a one-run gap certainly must."""
    assert stats.excludes_zero(26, 25, 50)["excludesZero"] is False


def test_the_pilot_anchor_decides():
    """The pilot's high-kill fractions on the paired subset were A 1/5, C 5/5.
    At the registered N = 50 the same proportions are decisively apart, which is
    the operating point section 5's OC table calls power 1.00."""
    result = stats.excludes_zero(10, 50, 50)
    assert result["excludesZero"] and result["decision"] == stats.DECIDED_RIGHT


def test_the_decision_never_reads_a_float():
    """`criticalLevel` and `orderingStatistic` are published as exact rational
    STRINGS, so a reader can recompute the comparison the decision made."""
    result = stats.excludes_zero(40, 20, 50)
    assert "/" in result["criticalLevel"] or result["criticalLevel"].isdigit()
    assert Fraction(result["orderingStatistic"]) >= \
        Fraction(result["criticalLevel"])


def test_a_count_outside_the_arm_size_refuses():
    with pytest.raises(stats.StatsError) as raised:
        stats.excludes_zero(51, 10, 50)
    assert str(raised.value).startswith("FM-NOT-A-COUNT")
    with pytest.raises(stats.StatsError) as raised:
        stats.excludes_zero(None, 10, 50)
    assert str(raised.value).startswith("FM-NO-COUNT")


def test_the_offset_mesh_agrees_that_the_registered_mesh_is_fine_enough():
    """oc_table.py's own size check, carried: the realised size on an
    interleaved mesh sharing no point with the registered one stays at or under
    alpha, so MESH_DEN is not the thing holding the size down."""
    small = 8
    table = stats.z2_table(small)
    cstar, _size, _evals = stats.critical_level(small, table)
    coefficients = stats.tail_coefficients(small, table, cstar)
    best, total = stats.sup_tail_numerator(coefficients, small, offset=True)
    assert Fraction(best, total) <= stats.FM_ALPHA


def test_sup_le_alpha_is_an_integer_comparison():
    table = stats.z2_table(4)
    coefficients = stats.tail_coefficients(4, table, Fraction(10 ** 9))
    ok, size = stats.sup_le_alpha(coefficients, 4)
    assert ok is True and size == 0


# --- the tau cut ------------------------------------------------------------

def test_the_tau_cut_is_the_smallest_integer_reaching_tau():
    """Section 5's tau = 0.95 over a finite paired subset IS an integer
    threshold, and the integer is what decides runs."""
    for paired in range(1, 200):
        cut = stats.tau_cut(paired)
        assert Fraction(cut, paired) >= stats.TAU
        assert cut == 0 or Fraction(cut - 1, paired) < stats.TAU


def test_the_tau_cut_at_the_design_time_paired_count():
    """39 paired witness groups at the adequacy gate: 0.95 x 39 = 37.05, so the
    cut is 38 and 37/39 = 0.9487 is NOT high-kill. The float comparison and the
    integer cut agree here, which is the point of deriving the integer."""
    assert stats.tau_cut(39) == 38
    assert 37 / 39 < float(stats.TAU) <= 38 / 39


def test_the_registered_constants_are_the_registered_values():
    """δ = 0.20 is carried and deliberately read by NOTHING: §5 registers it as
    "an interpretation and power quantity, not part of the decision rule", and a
    δ that leaked into `excludes_zero()` would be a second decision rule."""
    assert stats.TAU == Fraction(19, 20)
    assert stats.DELTA == Fraction(1, 5)
    assert stats.FM_ALPHA == Fraction(1, 20)
    assert stats.ALPHA == Fraction(1, 40)      # one tail of the two-sided 95%
    assert stats.MESH_DEN == 1000
    import inspect
    assert "DELTA" not in inspect.getsource(stats.excludes_zero)


def test_an_empty_paired_subset_refuses_rather_than_dividing_by_zero():
    with pytest.raises(stats.StatsError) as raised:
        stats.tau_cut(0)
    assert str(raised.value).startswith("TAU-NO-PAIRED-SUBSET")


# --- what is owed, refusing rather than guessing ----------------------------

def test_the_interval_endpoints_refuse_by_name():
    """SCAFFOLD item S7. The DECISION is complete; the reported endpoints need
    the Delta0 sweep, and a plausible number nothing computed would be worse
    than a refusal."""
    with pytest.raises(stats.StatsError) as raised:
        stats.interval_endpoints(40, 20, 50)
    assert str(raised.value).startswith("FM-ENDPOINTS-UNPORTED")
