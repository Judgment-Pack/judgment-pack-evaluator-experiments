"""Section 5.6's dispersion interval, exact to double precision and without
scipy — the arithmetic `harness/pilot_analysis.py` publishes beside each
member's recomputed sigma (round-2 finding R2-13).

An unbiased pooled within-arm SD on df degrees of freedom has
df·s²/σ² ~ χ²_df, so the two-sided 95 % interval for σ is

    [ s·sqrt(df / χ²_{0.975, df}),  s·sqrt(df / χ²_{0.025, df}) ].

The chi-square quantiles come from the regularized lower incomplete gamma
function P(df/2, x/2) — series for x < a + 1, Lentz continued fraction
otherwise (Numerical Recipes' `gammp`/`gammq`, transcribed) — inverted by
bisection to IEEE double. Nothing here is fitted or tabulated; the two
pinned checks in `tests/test_pilot_analysis.py` (df 15 → [0.7387, 1.5477],
df 33 → [0.8066, 1.3163]) are what bind this arithmetic to the figures the
round-2 plan computed independently.
"""
from __future__ import annotations

import math

LEVEL = 0.95


def _series(a: float, x: float) -> float:
    total = term = 1.0 / a
    n = a
    for _ in range(10000):
        n += 1.0
        term *= x / n
        total += term
        if abs(term) < abs(total) * 1e-16:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _continued_fraction(a: float, x: float) -> float:
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def regularized_lower_gamma(a: float, x: float) -> float:
    """P(a, x), the regularized lower incomplete gamma function."""
    if x < 0.0 or a <= 0.0:
        raise ValueError("P(a, x) needs a > 0 and x >= 0")
    if x == 0.0:
        return 0.0
    if x < a + 1.0:
        return _series(a, x)
    return 1.0 - _continued_fraction(a, x)


def chi_square_cdf(x: float, df: int) -> float:
    return regularized_lower_gamma(df / 2.0, x / 2.0)


def chi_square_quantile(probability: float, df: int) -> float:
    """The x with P(χ²_df <= x) = probability, by bisection to double
    precision. df must be a positive integer."""
    if not isinstance(df, int) or isinstance(df, bool) or df < 1:
        raise ValueError("df must be a positive integer, not %r" % (df,))
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie strictly in (0, 1)")
    low, high = 0.0, max(10.0, 4.0 * df)
    while chi_square_cdf(high, df) < probability:
        high *= 2.0
    for _ in range(300):
        mid = (low + high) / 2.0
        if mid == low or mid == high:
            break
        if chi_square_cdf(mid, df) < probability:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def sigma_factors(df: int, level: float = LEVEL) -> tuple:
    """(lower, upper) multipliers of s for the two-sided `level` interval."""
    alpha = 1.0 - level
    upper_q = chi_square_quantile(1.0 - alpha / 2.0, df)
    lower_q = chi_square_quantile(alpha / 2.0, df)
    return (math.sqrt(df / upper_q), math.sqrt(df / lower_q))


def sigma_interval(sigma: float, df: int, level: float = LEVEL) -> list:
    low, high = sigma_factors(df, level)
    return [sigma * low, sigma * high]
