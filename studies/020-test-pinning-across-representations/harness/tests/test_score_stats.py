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


def test_the_vectors_are_port_controls_and_the_studys_n_is_the_registrys():
    """R1-16. This test's earlier form said 012's n = 50 row "is the row this
    study will actually read" — true of the port carry, false since §2.1's
    fill registered N = 60. The vectors certify the ported arithmetic against
    numbers a predecessor published; the study's own denominator has exactly
    one home, the registry, and this test binds the two facts apart."""
    assert 50 in stats.REGISTERED_VECTORS
    assert stats.clopper_pearson(50, 50)[1] == 1.0
    assert stats.clopper_pearson(0, 50)[0] == 0.0
    import json
    import os
    harness = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(harness, "PINS.json"), "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    assert pins["batch"]["n"] == 60
    # R2-6: the assertion this replaces (`not in (30, 25)`) could never fail
    # for any plausible N and was NON-DISCRIMINATING; the property it reached
    # for is that the registered N is not also a port-control vector.
    # MUTATION: add a 60 row to REGISTERED_VECTORS -> fails.
    assert pins["batch"]["n"] not in stats.REGISTERED_VECTORS, (
        "the registered N colliding with a port-control row would let the two "
        "meanings blur again")


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
    assert block["rate"] == 3 / 50
    empty = stats.rate_block(0, 0, "admitted runs")
    assert empty["rate"] is None and empty["ci95"] is None
    assert empty["denominator"] == "admitted runs"
    assert empty["ci95State"] == stats.CI_EMPTY


# --- ROUND-2 R2-12: no inferential quantity at or above row 3 ---------------

def test_a_rate_block_leaves_its_interval_uncomputed():
    """§5: "No inferential quantity is COMPUTED, let alone published, at or
    above row 3." The bounds used to be computed inside every endpoint before a
    single gate had been read."""
    block = stats.rate_block(3, 50, "admitted runs")
    assert block["ci95"] is None
    assert block["ci95State"] == stats.CI_PENDING


def test_intervals_are_filled_only_for_an_outcome_that_reaches_row_four():
    published = {"e4": {"A": {"highKillRate":
                              stats.rate_block(1, 2, "admitted runs")}},
                 "population": {"B": {"timeoutRate":
                                      stats.rate_block(0, 10, "attempted")}}}
    assert stats.fill_intervals(published, True) == 2
    block = published["e4"]["A"]["highKillRate"]
    assert block["ci95State"] == stats.CI_COMPUTED
    assert block["ci95"][0] < block["rate"] < block["ci95"][1]


def test_a_failed_gate_suppresses_every_marginal_interval():
    """THE REVIEWER'S R2-12 PROBE: a failed E1 gate with E4 1/2 returned
    `control-gate-failed` and still printed `[0.0126, 0.9874]`."""
    published = {"e4": {"A": {"highKillRate":
                              stats.rate_block(1, 2, "admitted runs")}}}
    assert stats.fill_intervals(published, False, "E1 floor breached") == 1
    block = published["e4"]["A"]["highKillRate"]
    assert block["ci95"] is None
    assert block["ci95State"] == stats.CI_SUPPRESSED
    assert block["ci95Suppressed"] == "E1 floor breached"
    assert block["count"] == 1 and block["trials"] == 2


def test_filling_twice_does_not_recompute_a_settled_block():
    published = {"r": stats.rate_block(1, 2, "runs")}
    assert stats.fill_intervals(published, True) == 1
    assert stats.fill_intervals(published, False, "late gate") == 0
    assert published["r"]["ci95State"] == stats.CI_COMPUTED


# --- PORT 2: the registered contrast ----------------------------------------

def test_the_ordering_statistic_is_exact_rational():
    """A float here could silently flip a decision, which is the reason
    oc_table.py's header gives for the whole construction."""
    table = stats.z2_table(4)
    assert isinstance(table[3][1], Fraction)
    assert table[3][1] == Fraction(8 * (3 - 1) ** 2, 4 * (8 - 4))
    # s = 0 and s = 2N force x = y: no difference, no evidence.
    assert table[0][0] == 0 and table[4][4] == 0


def test_the_critical_level_at_the_prototypes_n_reproduces():
    """`design/mutants/oc_table.py` (Study 019's) computes c* = 625/154 with
    realised size just under alpha at ITS N = 50; the port reproduces both.
    A source-study reproduction, not a claim about 020's registered N
    (R1-16)."""
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


def test_a_small_gap_at_the_prototypes_n_is_indeterminate():
    """Section 5 states plainly that "a true 0.25 gap can still return
    INDETERMINATE", so a one-run gap certainly must. n = 50 here is Study
    012's prototype row, not 020's registered N (R1-16, R2-6); the registered
    N has exactly one home, `harness/PINS.json`'s `batch.n`."""
    assert stats.excludes_zero(26, 25, 50)["excludesZero"] is False


def test_a_wide_gap_at_the_prototypes_n_decides():
    """ROUND-4 FINDING R4-4. This case used to be called "the pilot anchor" and cited
    A 1/5, C 5/5 as the pilot's fractions. Those figures are three pilot issues out of
    date — the current issue is arm A 1/5 and arm C 0/5, the opposite sign — and a
    statistics test has no business anchoring itself to a pilot at all: the arithmetic
    it exercises is 0.20 against 1.00 at n = 50 — an arithmetic case, not the
    registered N — which holds whatever any pilot says.
    Recast as the arithmetic boundary case it always was. The pilot's own fractions are
    asserted where they belong, against the pilot artifact, in
    `test_prereg_currency.py`."""
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


# --- §7 delta 2: the threshold is REMOVED, not disabled ---------------------

def test_no_tau_and_no_tau_cut_survive_in_the_statistics_module():
    """§7 delta 2, asserted by ABSENCE and by name.

    Study 019 registered tau = 0.95 over the paired adequate subset and derived
    the operative integer cut from it; §5.1 of Study 020 registers the primary
    endpoint with "**No cut, no τ, no dichotomy**". A threshold left in the
    module as a constant nobody calls is a threshold a later edit can call, so
    both the constant and the function are gone — and this test fails if either
    comes back, which is the only way an absence is enforceable."""
    assert not hasattr(stats, "TAU")
    assert not hasattr(stats, "tau_cut")
    source = open(stats.__file__, encoding="utf-8").read()
    # The names may appear ONLY inside the comment recording the removal, so the
    # comment lines are dropped before the source is searched: what the delta
    # removes is CODE, and a note saying so is the opposite of a regression.
    code = "\n".join(line for line in source.split("\n")
                     if not line.lstrip().startswith("#"))
    assert "TAU" not in code
    assert "tau_cut" not in code


def test_the_registered_constants_are_the_registered_values():
    """δ = 0.20 is carried and deliberately read by NOTHING: §5 registers it as
    "an interpretation and power quantity, not part of the decision rule", and a
    δ that leaked into `excludes_zero()` would be a second decision rule."""
    assert stats.DELTA == Fraction(1, 5)
    assert stats.FM_ALPHA == Fraction(1, 20)
    assert stats.ALPHA == Fraction(1, 40)      # one tail of the two-sided 95%
    assert stats.MESH_DEN == 1000
    import inspect
    assert "DELTA" not in inspect.getsource(stats.excludes_zero)


# --- S8: the general unequal-N inversion ------------------------------------

def test_the_equal_arm_slice_reproduces_the_prototypes_constants_exactly():
    """SCAFFOLD item S8's acceptance test, and the reason the general form is
    safe to register: `design/mutants/oc_table.py` published c* and the realised
    size at three N with the equal-arm closed form, and the general two-argument
    inversion must reproduce every one of them EXACTLY — not to four decimals,
    as the same rational."""
    for n, cstar, size in ((30, Fraction(30, 7), 0.0469),
                           (50, Fraction(625, 154), 0.0488),
                           (100, Fraction(175, 44), 0.0496)):
        general_star, general_size = stats.critical_level_at(n, n)
        assert general_star == cstar
        assert round(float(general_size), 4) == size
        # …and the one-argument spelling IS the n_A = n_C slice, not a second
        # implementation that agrees.
        assert stats.critical_level_at(n) == (general_star, general_size)


def test_the_general_z2_table_reduces_to_the_prototypes_closed_form():
    """The equal-arm cell 2N(x-y)^2 / ((x+y)(2N-x-y)), against the general
    N (x n_C - y n_A)^2 / (n_A n_C (x+y)(N-x-y)), over a whole small table."""
    n = 7
    general = stats.z2_table(n, n)
    for x in range(n + 1):
        for y in range(n + 1):
            s = x + y
            want = (Fraction(0) if s in (0, 2 * n)
                    else Fraction(2 * n * (x - y) ** 2, s * (2 * n - s)))
            assert general[x][y] == want, (x, y)


def test_unequal_arms_are_scored_rather_than_refused():
    """Section 5's registered construction, and what SCAFFOLD item S8 closed:
    apparatus exclusions leave unequal denominators, and the contrast is the
    general inversion rather than a refusal or an approximation."""
    result = stats.excludes_zero(6, 0, 6, 5)
    assert result["equalArms"] is False
    assert result["nLeft"] == 6 and result["nRight"] == 5
    assert result["excludesZero"] is True
    assert result["decision"] == stats.DECIDED_LEFT


def test_the_direction_at_unequal_arms_is_by_RATE_and_not_by_COUNT():
    """Two equal counts are two different rates when the arms differ, and the
    equal-N spelling `x != y` would have called this indeterminate for the wrong
    reason. The rate comparison is what the difference of proportions means."""
    result = stats.excludes_zero(5, 5, 50, 6)
    assert result["difference"] == pytest.approx(5 / 50 - 5 / 6)
    assert result["decision"] == stats.DECIDED_RIGHT


def test_the_tail_coefficients_are_palindromic_at_unequal_arms():
    """`sup_tail_numerator()` scans only half the mesh because the tail is
    symmetric under (x, y) -> (n_A-x, n_C-y). That symmetry is what makes the
    half scan sound at UNEQUAL arm sizes too, so it is asserted rather than
    inherited from the equal-arm case."""
    n_left, n_right = 6, 4
    table = stats.z2_table(n_left, n_right)
    cstar, _size, _evals = stats.critical_level(n_left, table, n_right)
    coefficients = stats.tail_coefficients(n_left, table, cstar, n_right)
    assert coefficients == coefficients[::-1]


# --- S7: the Delta0 sweep and the reported endpoints ------------------------

def test_the_sweep_and_the_decision_agree_at_the_one_delta_they_share():
    """The reported interval and the registered decision must not be two
    constructions: at Delta0 = 0 the sweep's statistic IS `z2_table()`'s cell,
    and its p-value crosses alpha exactly where the critical level does."""
    n_left, n_right = 6, 5
    table = stats.z2_table(n_left, n_right)
    for x, y in ((6, 0), (3, 3), (5, 1), (0, 5)):
        assert stats.fm_z2(x, n_left, y, n_right, Fraction(0)) == table[x][y]
        rejected = stats.fm_pvalue(x, y, n_left, n_right,
                                   Fraction(0)) <= stats.FM_ALPHA
        assert rejected is stats.excludes_zero(x, y, n_left,
                                               n_right)["excludesZero"]


def test_the_reported_endpoints_exist_and_are_exact_rationals():
    """SCAFFOLD item S7: section 10 commits to publishing every interval, so the
    endpoints are computed rather than refused — and they are mesh points of the
    registered Delta0 mesh, published as exact rationals with the mesh that
    produced them."""
    result = stats.interval_endpoints(6, 0, 6, 5)
    assert Fraction(result["lower"]) == Fraction(43, 100)
    assert Fraction(result["upper"]) == Fraction(1)
    assert result["deltaMeshDenominator"] == stats.FM_DELTA_MESH_DEN
    assert result["nuisanceMeshDenominator"] == stats.MESH_DEN
    assert result["mleBisections"] == stats.FM_MLE_BISECTIONS
    assert result["acceptanceContiguous"] is True
    assert result["reportedAsConvexHull"] is False


def test_an_interval_that_excludes_zero_reports_endpoints_that_exclude_zero():
    """The two readings are one construction, so they cannot disagree about the
    only question the decision asks."""
    n_left, n_right = 6, 5
    decision = stats.excludes_zero(6, 0, n_left, n_right)
    interval = stats.interval_endpoints(6, 0, n_left, n_right)
    assert decision["excludesZero"] is True
    assert Fraction(interval["lower"]) > 0


def test_an_indeterminate_contrast_reports_an_interval_straddling_zero():
    n_left, n_right = 6, 5
    decision = stats.excludes_zero(3, 3, n_left, n_right)
    interval = stats.interval_endpoints(3, 3, n_left, n_right)
    assert decision["excludesZero"] is False
    assert Fraction(interval["lower"]) <= 0 <= Fraction(interval["upper"])


def test_the_constrained_mle_is_the_pooled_proportion_at_delta_zero():
    """The closed form the decision uses, recovered by the sweep's own
    root-finder: at Delta0 = 0 the FM constrained MLE is the pooled rate, so the
    bisection must land on it to within its registered precision."""
    x, n_left, y, n_right = 4, 6, 1, 5
    left, right = stats.constrained_mle(x, n_left, y, n_right, Fraction(0))
    pooled = Fraction(x + y, n_left + n_right)
    assert left == right
    assert abs(left - pooled) < Fraction(1, 2 ** (stats.FM_MLE_BISECTIONS - 4))


def test_the_delta_mesh_divides_the_nuisance_mesh():
    """The endpoints stay exact integer arithmetic only because p_C and
    p_A = p_C + Delta0 are both points of the registered nuisance mesh."""
    assert stats.MESH_DEN % stats.FM_DELTA_MESH_DEN == 0
    with pytest.raises(stats.StatsError) as raised:
        stats.delta_tail_sup(stats.z2_table(2, 2), Fraction(0), 2, 2,
                             Fraction(1, 7))
    assert str(raised.value).startswith("FM-MESH-INCOMMENSURATE")


def test_a_count_out_of_range_refuses_before_the_sweep():
    with pytest.raises(stats.StatsError) as raised:
        stats.interval_endpoints(7, 0, 6, 5)
    assert str(raised.value).startswith("FM-NOT-A-COUNT")
