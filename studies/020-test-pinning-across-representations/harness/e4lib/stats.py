"""The interval arithmetic — two ports, one file, both by digest.

PORT 1 (the per-arm rates). Study 012's `harness/score_rates.py`
(sha256 `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336`, the
digest Study 012's own `harness/PORTS.md` records for it): `ALPHA`,
`BISECTIONS`, `_tail_ge`, `_tail_le`, `_bisect`, `clopper_pearson`,
`lower_bound`, `upper_bound`, `rate_block`, `probability_at_least` and
`REGISTERED_VECTORS` — carried byte-for-byte in their arithmetic. Ported rather
than re-derived because a re-derived interval is a second implementation of a
published number, and Study 012 published its n = 50 row, which is exactly this
study's per-arm denominator (PREREGISTRATION.md section 2 "Batch shape": N = 50
runs/arm). The enumerated changes are in `harness/PORTS.md`; they are: the
module's docstring, the removal of `HIGH_CUT`/`LOW_CUT`/`high_threshold()`/
`low_threshold()` (Study 012's section 5.1 review-depth cuts, which name nothing
here), and everything below the PORT 2 banner.

PORT 2 (the contrast). This study's `design/mutants/oc_table.py`
(sha256 `4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131`),
whose header is the registered construction PREREGISTRATION.md section 5 adopts
verbatim:

    The A-C interval is the exact unconditional (Barnard-type) confidence
    interval for the difference of independent binomial proportions obtained by
    inverting the two-sided Farrington-Manning score test, with the nuisance
    parameter eliminated by maximisation. Nominal coverage 1 - alpha with
    alpha = 0.05, two-sided. The nuisance maximisation is taken over the
    registered rational mesh M = {k/1000 : k = 0..1000} in exact integer
    arithmetic.

`z2_table()`, `tail_coefficients()`, `sup_tail_numerator()`, `sup_le_alpha()`
and `critical_level()` are that file's, carried. What is added here is the
single entry point the decision rule reads, `excludes_zero()`, and the
memoisation that makes it cheap to call twice (A-C, then A-B) at one N.

**Reading 1, and what it does NOT give you.** oc_table.py's own header states
the reduction the registered decision rests on: the interval is
{Delta : the FM test at Delta does not reject}, so it excludes zero exactly
when the two-sided exact unconditional test of H0: p_A = p_C rejects at alpha,
and at Delta0 = 0 the FM score reduces to the pooled-variance two-sample Z. So
the DECISION needs only the Delta0 = 0 inversion, which is what
`excludes_zero()` computes exactly. The reported interval ENDPOINTS need the
same inversion swept over Delta0, which is not ported: `interval_endpoints()`
refuses with a named code rather than returning a number nothing computed
(harness/SCAFFOLD.md item S7).

Arithmetic discipline, from both sources: every quantity a decision reads is an
exact integer or `Fraction`. `float` appears in the Clopper-Pearson bounds
(Study 012's registered 200-halving bisection, whose fixed iteration count and
exact comparison give the same bits on any platform) and in formatting, and
nowhere in the contrast.

WHAT THE CONTRAST IS, AND WHAT IT IS NOT — ROUND-1 FINDING R1-16
----------------------------------------------------------------
The reviewer's finding was that the reported interval "is not established as an
exact 95% confidence interval over the continuous binomial parameter space", and
offered two remedies: certify the continuum, or relabel. **This study relabels,
and states the direction of the approximation.** Certification was costed and
rejected on the arithmetic: the Bernstein bound below makes the mesh error
`N / (2 * mesh_den)`, so a certified continuum supremum at N = 100 needs a mesh
of denominator ~50,000 to leave a thousandth of slack under `alpha = 0.05` — and
that is 25,000 exact evaluations of a degree-100 Bernstein polynomial per level,
inside a binary search, inside a 201-point `Delta0` sweep. The honest artifact is
the one that says what it computed.

The name of the object this module returns is therefore the

    **exact-arithmetic mesh-inversion hull**

and never "the exact 95% confidence interval". Two approximations, each named,
each with its direction stated:

1. **The nuisance supremum is taken over the mesh M = {k/MESH_DEN}, not over
   [0, 1].** A mesh maximum is a LOWER bound on the continuum maximum, so the
   realised size this module reports is a lower bound on the procedure's true
   size: the test may be ANTI-CONSERVATIVE — its true size can exceed
   `FM_ALPHA`, and the hull can under-cover — by at most the slack
   `mesh_slack_bound()` computes. That function is not a fudge factor and
   nothing is adjusted by it; it is a published bound on how wrong the label
   could be, and it is reported inside every contrast record.
2. **The `Delta0` inversion is over the mesh M_D = {j/FM_DELTA_MESH_DEN}.** The
   reported endpoints are the hull of the ACCEPTED MESH POINTS, an INNER
   approximation to the continuum acceptance set: the reported hull can be
   NARROWER than the continuum interval, never wider. This one does not touch
   the decision, which reads the `Delta0 = 0` inversion — an exact mesh point —
   and nothing else.

Neither approximation is new here; both were in the code and the second was
already labelled. What changes is that the artifact no longer calls the result an
exact confidence interval, and that the first approximation is quantified.
OWED TO THE PROSE LANE: §5's "exact unconditional (FM-score) two-proportion
difference intervals" and §10's "all intervals" must adopt this name and carry
the direction with it.
"""
from __future__ import annotations

import math
from fractions import Fraction

# --- PORT 1: Study 012's registered interval --------------------------------

ALPHA = Fraction(1, 40)          # one tail of a two-sided 95% interval
BISECTIONS = 200                 # fixed; no early exit, no tolerance

# Study 012's section 4.3 registered test vectors, carried as DATA so a harness
# test can diff them against a published table rather than against a
# re-derivation of the code that produced them. The n = 50 row is this study's
# own per-arm denominator; n = 30 and n = 25 are Study 012's, retained as port
# controls against numbers a predecessor already published — if this port drifts
# from 012's arithmetic, a number 012 printed stops reproducing here.
REGISTERED_VECTORS = {
    30: {0: (0.0000, 0.1157), 1: (0.0008, 0.1722), 2: (0.0082, 0.2207),
         3: (0.0211, 0.2653), 4: (0.0376, 0.3072), 15: (0.3130, 0.6870),
         26: (0.6928, 0.9624), 27: (0.7347, 0.9789), 28: (0.7793, 0.9918),
         29: (0.8278, 0.9992), 30: (0.8843, 1.0000)},
    25: {0: (0.0000, 0.1372), 1: (0.0010, 0.2035), 2: (0.0098, 0.2603),
         3: (0.0255, 0.3122), 12: (0.2780, 0.6869), 22: (0.6878, 0.9745),
         23: (0.7397, 0.9902), 24: (0.7965, 0.9990), 25: (0.8628, 1.0000)},
    50: {0: (0.0000, 0.0711), 1: (0.0005, 0.1065), 25: (0.3553, 0.6447),
         40: (0.6628, 0.8997), 45: (0.7819, 0.9667), 50: (0.9289, 1.0000)},
}


class StatsError(Exception):
    """A refusal in the arithmetic itself, with a named code as its first word."""


def _tail_ge(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), summed in ascending j as exact
    rationals: math.comb is exact, and a double is an exact binary rational,
    so nothing here rounds."""
    q = 1 - p
    total = Fraction(0)
    for j in range(k, n + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _tail_le(k: int, n: int, p: Fraction) -> Fraction:
    """P(X <= k) for X ~ Binomial(n, p)."""
    q = 1 - p
    total = Fraction(0)
    for j in range(0, k + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _bisect(predicate) -> float:
    """The crossing point of a monotone predicate — true on [0, root), false
    after — found by EXACTLY 200 halvings of [0, 1] in IEEE-754 doubles. A
    fixed iteration count and an exact comparison mean the same inputs give
    the same bits on any platform: no libm, no tolerance, no seed."""
    low, high = 0.0, 1.0
    for _ in range(BISECTIONS):
        middle = (low + high) / 2.0
        if predicate(middle):
            low = middle
        else:
            high = middle
    return low


def clopper_pearson(k: int, n: int) -> tuple:
    """The exact (Clopper-Pearson) 95% interval for k successes in n trials.

    The bounds are the p values that make the observed count exactly as
    extreme as alpha/2 allows: the lower bound solves P(X >= k | p) = alpha
    (increasing in p), the upper solves P(X <= k | p) = alpha (decreasing in
    p), with the degenerate ends pinned at 0 and 1.

    "Exact" is doing more work than it can carry, and Study 012's section 4.3
    said so; PREREGISTRATION.md section 8 says it again for this study. The
    arithmetic is exact rationals with no libm, and the COVERAGE is exact only
    conditional on the runs of an arm being independent Bernoulli trials with a
    constant success probability. Section 8 records that this design cannot
    rule out provider-side cross-session state, which would break both halves
    of that model. Every interval this study publishes is an exact interval for
    a model this design cannot verify."""
    if n <= 0:
        raise StatsError("CP-NO-TRIALS an interval needs at least one trial")
    if not 0 <= k <= n:
        raise StatsError("CP-NOT-A-COUNT k=%d is not a count out of n=%d" % (k, n))
    return lower_bound(k, n), upper_bound(k, n)


def lower_bound(k: int, n: int) -> float:
    """The interval's lower bound alone, so a caller that needs one root does
    not pay for the other."""
    return 0.0 if k == 0 else _bisect(lambda p: _tail_ge(k, n, Fraction(p)) < ALPHA)


def upper_bound(k: int, n: int) -> float:
    return 1.0 if k == n else _bisect(lambda p: _tail_le(k, n, Fraction(p)) > ALPHA)


def probability_at_least(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), exactly. Same arithmetic as the
    interval: math.comb and Fractions, no libm and no rounding."""
    return _tail_ge(k, n, p)


# The three states of a published rate block's interval. Section 5: "No
# inferential quantity is computed, let alone published, at or above row 3."
CI_PENDING = "not-computed-yet"
CI_COMPUTED = "computed"
CI_EMPTY = "undefined-over-an-empty-denominator"
CI_SUPPRESSED = "not-computed-control-gate-failed"

# The same four states for a CONTRAST's reported interval endpoints
# (round-3 finding R3-8). They are spelled separately from the `CI_*` names
# because the two objects are settled by the same walker but are different
# quantities: `CI_*` is one arm's marginal Clopper-Pearson interval and
# `INTERVAL_*` is the difference interval's Delta0 sweep.
INTERVAL_PENDING = "not-computed-yet"
INTERVAL_COMPUTED = "computed"
INTERVAL_SUPPRESSED = "not-computed-control-gate-failed"
INTERVAL_REFUSED = "refused"


def rate_block(k: int, n: int, denominator: str) -> dict:
    """The reported shape for one proportion: the integers, the point estimate,
    the exact interval, and the NAME of the denominator it is over. Never a
    rate without its denominator, and never a bound a reader cannot recompute
    from the integers (Study 012 section 4.7; PREREGISTRATION.md section 10's
    publication commitment repeats it for every rate this study publishes).

    THE INTERVAL IS NOT COMPUTED HERE (round-2 finding R2-12). §5 says no
    inferential quantity is COMPUTED, let alone published, at or above row 3, and
    the marginal Clopper-Pearson bounds were computed inside every endpoint
    before any gate had been evaluated and printed unconditionally afterwards —
    a failed-E1 probe returned `control-gate-failed` and still published
    `[0.0126, 0.9874]`. Contrast and direction suppression held, which is
    narrower than the prohibition. So the block leaves with its integers and its
    rate and an interval in the `not-computed-yet` state; `fill_intervals()`
    computes the bounds once, later, and only for an outcome that reaches row 4.
    Nothing recomputes a rate: a suppressed interval and a published one are the
    same counts."""
    if n <= 0:
        return {"count": k, "trials": n, "denominator": denominator,
                "rate": None, "ci95": None, "ci95State": CI_EMPTY}
    return {"count": k, "trials": n, "denominator": denominator,
            "rate": k / n, "ci95": None, "ci95State": CI_PENDING}


def _is_pending_block(node) -> bool:
    return (isinstance(node, dict) and node.get("ci95State") == CI_PENDING
            and isinstance(node.get("count"), int)
            and isinstance(node.get("trials"), int))


def _is_pending_contrast(node) -> bool:
    """ROUND-3 FINDING R3-8. A contrast whose endpoints have not been computed
    yet, recognised by the same idiom as a pending rate block: the state member
    plus the integers the settlement needs, so a dict that merely mentions the
    word is not settled by accident."""
    return (isinstance(node, dict)
            and node.get("intervalState") == INTERVAL_PENDING
            and all(isinstance(node.get(member), int)
                    for member in ("left", "right", "nLeft", "nRight")))


def settle_contrast(node, licensed: bool, reason: str = None) -> None:
    """Settle ONE pending contrast's reported endpoints, in place.

    ROUND-3 FINDING R3-8, and it is why the endpoints are not computed where the
    contrast is built. The reviewer's scenario: gates initially clear, A = 5/5,
    C = 0/5, B = 0/0. The primary A−C contrast computed its endpoints eagerly;
    the secondary A−B then raised `FM-EMPTY-ARM`; the contrasts were cleared and
    the attempt landed on row 1. So an inferential quantity had been COMPUTED
    for an outcome whose final row was pipeline-invalid — and §5 prohibits the
    computation, not only the printing ("No inferential quantity is computed,
    let alone published, at or above row 3").

    A sweep cannot be un-run, so the fix is not to run it until the row is
    known. `harness/score.py` builds every contrast with its endpoints PENDING,
    the decision walks the ordered table, and this settles the endpoints
    afterwards — computed only for an outcome that reached the substantive row,
    suppressed with its cause otherwise. An endpoint sweep that refuses is still
    only a report: `excludesZero` is already fixed and §5's rule reads that and
    nothing else."""
    if not licensed:
        node["interval"] = None
        node["intervalState"] = INTERVAL_SUPPRESSED
        node["intervalSuppressed"] = reason
        return
    try:
        node["interval"] = interval_endpoints(
            node["left"], node["right"], node["nLeft"], node["nRight"])
        node["intervalState"] = INTERVAL_COMPUTED
    except StatsError as error:
        node["interval"] = None
        node["intervalState"] = INTERVAL_REFUSED
        node["intervalRefusal"] = str(error)


def fill_intervals(node, licensed: bool, reason: str = None) -> int:
    """Walk a published structure and settle every pending inferential quantity.

    `licensed` is "the ordered decision rule reached row 4": the gate rows were
    evaluated first and none of them matched. When it is false nothing is
    computed at all — the state becomes `not-computed-control-gate-failed` and
    carries the reason, so a reader sees an interval that was withheld rather
    than an interval that does not exist. Returns how many blocks it settled.

    TWO KINDS OF BLOCK, one walker (round-3 R3-8). A pending rate block is one
    arm's marginal interval; a pending CONTRAST is the difference interval's
    Delta0 sweep, which used to be computed where the contrast was built —
    before the run's final row was known. Both are settled here, once, after the
    decision, so neither can be computed for an outcome that never reaches the
    substantive rows."""
    settled = 0
    if isinstance(node, dict):
        if _is_pending_block(node):
            if licensed:
                low, high = clopper_pearson(node["count"], node["trials"])
                node["ci95"] = [low, high]
                node["ci95State"] = CI_COMPUTED
            else:
                node["ci95State"] = CI_SUPPRESSED
                node["ci95Suppressed"] = reason
            return 1
        if _is_pending_contrast(node):
            settle_contrast(node, licensed, reason)
            settled += 1
        for value in node.values():
            settled += fill_intervals(value, licensed, reason)
    elif isinstance(node, list):
        for item in node:
            settled += fill_intervals(item, licensed, reason)
    return settled


# --- PORT 2: the registered contrast (design/mutants/oc_table.py) -----------

FM_ALPHA = Fraction(1, 20)       # two-sided; the 95% difference interval
MESH_DEN = 1000                  # the registered nuisance mesh M = {k/1000}
# §7 delta 2: TAU IS REMOVED, not disabled. Study 019 registered
# tau = 0.95 over the paired adequate subset and `tau_cut()` derived the
# operative integer cut from it; §5.1 of Study 020 registers the primary
# endpoint with "No cut, no tau, no dichotomy", so there is no threshold for
# a decision path to read and no constant here for one to be reconstructed
# from. `harness/tests/test_score_stats.py` asserts the absence by name.
DELTA = Fraction(1, 5)           # 0.20, the minimum meaningful difference

# The three answers `excludes_zero()` distinguishes, named so a caller cannot
# confuse "A above C" with "decided" (PREREGISTRATION.md section 5: an interval
# straddling zero is INDETERMINATE and licenses nothing).
DECIDED_LEFT = "left-above-right"
DECIDED_RIGHT = "right-above-left"
INDETERMINATE = "indeterminate"

# The one name this study publishes for the object below (round-1 R1-16).
CONSTRUCTION_NAME = "exact-arithmetic mesh-inversion hull"


def mesh_slack_bound(n_left: int, n_right: int,
                     mesh_den: int = MESH_DEN) -> Fraction:
    """A bound on how far the MESH supremum can fall below the CONTINUUM one.

    The null tail probability at Delta0 = 0 is one Bernstein polynomial in the
    shared nuisance rate, `f(p) = sum_s a_s C(N,s) p^s (1-p)^(N-s)` with
    `N = n_A + n_C` and every `a_s` in [0, 1] (it is the fraction of tables at
    that margin that lie in the tail). Bernstein's derivative identity gives
    `f'(p) = N sum_s (a_{s+1} - a_s) B_{s,N-1}(p)`, and a convex combination of
    numbers of modulus at most one has modulus at most one, so `|f'| <= N`
    everywhere. A grid of spacing `1/mesh_den` therefore misses the continuum
    maximum by at most `N / (2 * mesh_den)`.

    Exact, and deliberately crude: it is a HONEST CEILING on the label's error,
    not an estimate of it. Nothing is corrected by it — the value is published
    beside the realised size so a reader can see how far "alpha = 0.05" could be
    from the truth, which is the whole of what round-1 R1-16 asks for once
    certification has been declined."""
    return Fraction(n_left + n_right, 2 * mesh_den)


def z2_table(n_left: int, n_right: int = None) -> list:
    """z^2(x, y) at Delta0 = 0 as exact Fractions; 0 on the degenerate ends.

    At Delta0 = 0 the Farrington-Manning score statistic reduces to the
    pooled-variance two-sample Z, whose square is the Pearson chi-square of the
    2x2 table. The constrained MLE under p_A = p_C is the POOLED proportion
    (x + y) / (n_A + n_C) — a closed form, exactly rational — so at Delta0 = 0
    the whole construction is exact with no root-finding anywhere:

        z^2(x, y) = N (x n_C - y n_A)^2 / (n_A n_C (x + y) (N - x - y)),
        N = n_A + n_C

    SCAFFOLD item S8: the equal-N form 2N(x-y)^2 / ((x+y)(2N-x-y)) that the
    design prototype `design/mutants/oc_table.py` carries is the n_A = n_C slice
    of this, and `harness/tests/test_score_stats.py` asserts that the general
    form reproduces the prototype's registered constants at n_A = n_C = 50
    exactly. The general form is registered because section 1a excludes
    apparatus failures from the denominator and unequal admitted counts are
    therefore a real possibility; approximating that case with a formula for one
    N would be a number nobody registered.

    The ORDERING of tables is where a float could silently flip a decision, so
    it is done here and only here."""
    n_right = n_left if n_right is None else n_right
    total = n_left + n_right
    out = [[Fraction(0)] * (n_right + 1) for _ in range(n_left + 1)]
    for x in range(n_left + 1):
        for y in range(n_right + 1):
            s = x + y
            den = n_left * n_right * s * (total - s)
            if den == 0:
                # s = 0 or s = N forces both proportions equal (0 and 0, or 1
                # and 1): no difference, no evidence.
                out[x][y] = Fraction(0)
            else:
                out[x][y] = Fraction(total * (x * n_right - y * n_left) ** 2,
                                     den)
    return out


def tail_coefficients(n_left: int, z2: list, level: Fraction,
                      n_right: int = None) -> list:
    """A_s = sum over tables in the tail {z^2 >= level} with x + y = s of
    C(n_A,x) C(n_C,y).

    At Delta0 = 0 BOTH arms share the nuisance rate p, so the null probability
    of the tail is f(p) = sum_s A_s p^s (1-p)^(N-s) with N = n_A + n_C — one
    Bernstein polynomial in one variable, whatever the two arm sizes are. That
    is what makes the unequal-N inversion as cheap and as exact as the equal-N
    one."""
    n_right = n_left if n_right is None else n_right
    A = [0] * (n_left + n_right + 1)
    c_left = [math.comb(n_left, i) for i in range(n_left + 1)]
    c_right = [math.comb(n_right, i) for i in range(n_right + 1)]
    for x in range(n_left + 1):
        row = z2[x]
        cx = c_left[x]
        for y in range(n_right + 1):
            if row[y] >= level:
                A[x + y] += cx * c_right[y]
    return A


def sup_tail_numerator(A: list, n_left: int, mesh_den: int = MESH_DEN,
                       offset: bool = False, n_right: int = None) -> tuple:
    """max over the registered mesh of f(p) * mesh_den^N, as an exact integer,
    with N = n_A + n_C.

    The tail set is symmetric under (x, y) -> (n_A-x, n_C-y) — that map negates
    the difference of proportions and sends the pooled rate to its complement,
    so z^2 is invariant — hence A_s = A_{N-s} and f(p) = f(1-p); only
    k <= mesh_den/2 is scanned. `offset=True` scans the interleaved mesh
    instead — the size check that says whether MESH_DEN is fine enough."""
    twoN = n_left + (n_left if n_right is None else n_right)
    if offset:
        den = 2 * mesh_den
        ks = range(1, mesh_den + 1, 2)
    else:
        den = mesh_den
        ks = range(0, mesh_den // 2 + 1)
    best = 0
    for k in ks:
        q = den - k
        qp = [1] * (twoN + 1)
        for m in range(1, twoN + 1):
            qp[m] = qp[m - 1] * q
        # Horner: H_j = A_j q^(2N-j) + k H_{j+1}, H_2N = A_2N, H_0 = f * den^2N
        H = A[twoN]
        for j in range(twoN - 1, -1, -1):
            H = A[j] * qp[twoN - j] + k * H
        if H > best:
            best = H
    return best, den ** twoN


def sup_le_alpha(A: list, n_left: int, n_right: int = None) -> tuple:
    """Exact INTEGER test: is sup_M f(p) <= FM_ALPHA? No division, so no float
    ever stands between the mesh and the decision."""
    best, total = sup_tail_numerator(A, n_left, n_right=n_right)
    return best * FM_ALPHA.denominator <= FM_ALPHA.numerator * total, \
        Fraction(best, total)


def critical_level(n_left: int, z2: list, n_right: int = None) -> tuple:
    """Smallest attained z^2 level c* with sup_M P(z^2 >= c*) <= FM_ALPHA.

    The tail sup is non-increasing in the level, so binary search is valid.
    Returns (c*, the realised size at c*, the number of sup evaluations); c* is
    None when no attainable rejection region exists at this alpha, in which
    case the procedure can never decide and every table is INDETERMINATE."""
    n_right = n_left if n_right is None else n_right
    levels = sorted({z2[x][y] for x in range(n_left + 1)
                     for y in range(n_right + 1)})
    evals = 0
    A_top = tail_coefficients(n_left, z2, levels[-1], n_right)
    ok, size = sup_le_alpha(A_top, n_left, n_right)
    evals += 1
    if not ok:
        return None, size, evals
    lo, hi = 0, len(levels) - 1
    best_size = size
    while hi - lo > 1:
        mid = (lo + hi) // 2
        A = tail_coefficients(n_left, z2, levels[mid], n_right)
        ok, size = sup_le_alpha(A, n_left, n_right)
        evals += 1
        if ok:
            hi, best_size = mid, size
        else:
            lo = mid
    return levels[hi], best_size, evals


_CRITICAL_CACHE = {}


def critical_level_at(n_left: int, n_right: int = None) -> tuple:
    """`critical_level()` memoised on N — (c*, realised size). New here, not in
    the prototype: the registered contrasts are tested twice at one N (A-C
    first, then A-B, PREREGISTRATION.md section 5's fixed-sequence
    gatekeeping), and the second call must read the same c* as the first rather
    than recompute a number that could differ if anything above ever became
    non-deterministic."""
    n_right = n_left if n_right is None else n_right
    key = (n_left, n_right)
    if key not in _CRITICAL_CACHE:
        if n_left <= 0 or n_right <= 0:
            raise StatsError("FM-NO-TRIALS a contrast needs at least one trial per arm")
        cstar, size, _evals = critical_level(n_left, z2_table(n_left, n_right),
                                             n_right)
        _CRITICAL_CACHE[key] = (cstar, size)
    return _CRITICAL_CACHE[key]


def excludes_zero(x: int, y: int, n_left: int, n_right: int = None) -> dict:
    """READING 1 of the registered contrast: does the exact unconditional
    difference interval for p_left - p_right exclude zero, and in which
    direction?

    `x` and `y` are the two arms' high-kill counts out of `n_left` and
    `n_right`. The returned `decision` is one of `DECIDED_LEFT`,
    `DECIDED_RIGHT`, `INDETERMINATE`; `excludesZero` is the decision rule's own
    predicate, so a caller never has to re-derive it from the direction.

    UNEQUAL ARM SIZES ARE REGISTERED (SCAFFOLD item S8, closed). Section 5:
    "Because apparatus exclusions can leave unequal per-arm denominators, the
    registered construction is the general unequal-N FM-score inversion (the OC
    table's equal-N closed form is its N_A = N_C slice)". `n_right` defaults to
    `n_left`, which is that slice, and the design prototype's registered
    constants are reproduced there exactly.

    The zero-exclusion predicate is stated as `z^2 > 0` rather than as
    `x != y`: at unequal arm sizes two EQUAL counts are two different rates, and
    two different counts can be one rate. At n_left = n_right the two spellings
    agree exactly, so the equal-N behaviour is unchanged."""
    if x is None or y is None:
        raise StatsError("FM-NO-COUNT a contrast needs two counts")
    n_right = n_left if n_right is None else n_right
    if not 0 <= x <= n_left or not 0 <= y <= n_right:
        raise StatsError("FM-NOT-A-COUNT (%r, %r) are not two counts out of "
                         "(%r, %r)" % (x, y, n_left, n_right))
    cstar, size = critical_level_at(n_left, n_right)
    z2 = z2_table(n_left, n_right)[x][y]
    decided = cstar is not None and z2 >= cstar and z2 > 0
    if not decided:
        decision = INDETERMINATE
    else:
        decision = (DECIDED_LEFT if Fraction(x, n_left) > Fraction(y, n_right)
                    else DECIDED_RIGHT)
    return {
        "n": n_left if n_left == n_right else None,
        "nLeft": n_left,
        "nRight": n_right,
        "equalArms": n_left == n_right,
        "left": x,
        "right": y,
        "difference": float(Fraction(x, n_left) - Fraction(y, n_right)),
        "decision": decision,
        "excludesZero": decided,
        "criticalLevel": None if cstar is None else str(cstar),
        "orderingStatistic": str(z2),
        "realisedSize": None if cstar is None else float(size),
        "realisedSizeExact": None if cstar is None else str(size),
        "alpha": str(FM_ALPHA),
        "meshDenominator": MESH_DEN,
        # Round-1 R1-16, published with every contrast rather than in a note.
        "constructionName": CONSTRUCTION_NAME,
        "levelCertifiedOverContinuum": False,
        "nuisanceMeshSlackBound": str(mesh_slack_bound(n_left, n_right)),
        "approximationDirection":
            "the nuisance supremum is over the mesh M = {k/%d} and is therefore "
            "a LOWER bound on the continuum supremum: the realised size reported "
            "here is a lower bound on the procedure's true size, so the "
            "procedure may be anti-conservative (true size above alpha, "
            "under-coverage) by at most nuisanceMeshSlackBound. Nothing is "
            "adjusted by that bound; it is published so the label's error is "
            "visible" % MESH_DEN,
        "construction": "%s: the two-sided Farrington-Manning score test "
                        "inverted in exact integer arithmetic with the nuisance "
                        "eliminated by maximisation over the registered rational "
                        "mesh; Reading 1 (the Delta0 = 0 inversion, which is what "
                        "the zero-exclusion decision reads). NOT an exact 95%% "
                        "confidence interval over the continuous parameter space "
                        "— see approximationDirection" % CONSTRUCTION_NAME,
    }


# --- the Delta0 sweep: the REPORTED interval endpoints (SCAFFOLD item S7) ---
#
# The decision reads only the Delta0 = 0 inversion above, where the constrained
# MLE is the pooled proportion and everything is closed-form rational. The
# REPORTED endpoints need the same inversion at every Delta0, where the
# constrained MLEs solve a cubic. Two things are registered here so that the
# sweep is exactly reproducible rather than approximately right:
#
#   * the Delta0 MESH. The reported interval is the convex hull of the accepted
#     set intersected with M_D = {j/FM_DELTA_MESH_DEN : j = -D..D}. At
#     FM_DELTA_MESH_DEN = 100 every attainable per-arm rate difference at the
#     registered N = 50 (a multiple of 1/50) is itself a mesh point, and
#     MESH_DEN = 1000 is a multiple of it, so p_C and p_A = p_C + Delta0 are
#     both points of the registered NUISANCE mesh and the tail probability stays
#     exact integer arithmetic.
#   * the constrained-MLE BISECTION. The log-likelihood restricted to
#     p_A - p_C = Delta0 is concave, so its derivative's numerator (an integer
#     cubic) changes sign at most once; the MLE is located by exactly
#     FM_MLE_BISECTIONS halvings of the feasible interval with the sign taken in
#     exact INTEGER arithmetic. A fixed iteration count and an exact comparison
#     give the same bits on any platform — the same discipline Study 012
#     registered for the Clopper-Pearson bisection (`_bisect` above), and for the
#     same reason: no libm, no tolerance, no seed.
FM_DELTA_MESH_DEN = 100
FM_MLE_BISECTIONS = 48


def _poly_mul(left, right):
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                out[i + j] += a * b
    return out


def _poly_add(left, right, scale=1):
    size = max(len(left), len(right))
    out = [Fraction(0)] * size
    for i, a in enumerate(left):
        out[i] += a
    for i, b in enumerate(right):
        out[i] += scale * b
    return out


def score_cubic(x: int, n_left: int, y: int, n_right: int,
                delta: Fraction) -> list:
    """Integer coefficients (ascending powers of p = p_A) of the cubic whose
    root in the feasible interior is the Farrington-Manning constrained MLE.

    With p_C = p_A - Delta0 the restricted log-likelihood is

        x log p + (n_A - x) log(1-p) + y log(p-D) + (n_C - y) log(1-p+D)

    and multiplying its derivative by the positive product
    p (1-p) (p-D) (1-p+D) clears every denominator, leaving a cubic. It is built
    by polynomial multiplication rather than by a transcribed expansion, and
    then scaled to INTEGER coefficients so the sign at a dyadic rational is an
    integer comparison."""
    p1 = [Fraction(1), Fraction(-1)]              # 1 - p
    p2 = [-delta, Fraction(1)]                    # p - D
    p3 = [Fraction(1) + delta, Fraction(-1)]      # 1 - p + D
    p4 = [Fraction(0), Fraction(1)]               # p
    poly = _poly_mul(_poly_mul(p1, p2), p3)
    poly = [x * c for c in poly]
    poly = _poly_add(poly, _poly_mul(_poly_mul(p4, p2), p3), -(n_left - x))
    poly = _poly_add(poly, _poly_mul(_poly_mul(p4, p1), p3), y)
    poly = _poly_add(poly, _poly_mul(_poly_mul(p4, p1), p2), -(n_right - y))
    scale = 1
    for coefficient in poly:
        scale = scale * coefficient.denominator // math.gcd(
            scale, coefficient.denominator)
    return [int(coefficient * scale) for coefficient in poly]


def _feasible(delta: Fraction) -> tuple:
    """The interval p_A may live in when p_C = p_A - Delta0 is also a
    probability."""
    return max(Fraction(0), delta), min(Fraction(1), Fraction(1) + delta)


def constrained_mle(x: int, n_left: int, y: int, n_right: int,
                    delta: Fraction) -> tuple:
    """`(p_A, p_C)`, the Farrington-Manning constrained MLEs under
    p_A - p_C = Delta0, as exact dyadic rationals.

    Bisection, not a closed form: Farrington and Manning's trigonometric
    solution of the cubic needs `cos`/`acos`, and a libm call in the ordering of
    tables is exactly what this study's arithmetic discipline forbids. The
    concavity of the restricted likelihood makes bisection valid, and the
    boundary cases fall out of it without a special branch — a derivative that
    never changes sign drives the bracket to the end it points at."""
    lo, hi = _feasible(delta)
    if lo == hi:
        return lo, lo - delta
    coefficients = score_cubic(x, n_left, y, n_right, delta)
    span = hi - lo
    den = span.denominator * lo.denominator
    lo_num = int(lo * den)
    step_num = int(span * den)          # hi = (lo_num + step_num) / den
    low, high = 0, 1 << FM_MLE_BISECTIONS
    scale = 1 << FM_MLE_BISECTIONS
    for _ in range(FM_MLE_BISECTIONS):
        middle = (low + high) // 2
        numerator = lo_num * scale + step_num * middle
        denominator = den * scale
        value = 0
        for power, coefficient in enumerate(coefficients):
            value += coefficient * numerator ** power * \
                denominator ** (len(coefficients) - 1 - power)
        if value > 0:
            low = middle
        else:
            high = middle
    p_left = Fraction(lo_num * scale + step_num * low, den * scale)
    return p_left, p_left - delta


def fm_z2(x: int, n_left: int, y: int, n_right: int, delta: Fraction):
    """The Farrington-Manning score statistic squared at Delta0, exactly.

    `math.inf` for the degenerate case a constrained model on the boundary
    produces — zero variance with a non-zero numerator, which arises only at
    Delta0 = +-1 — so that the ordering of tables is total and the tail is
    well-defined without a special case downstream."""
    if delta == 0:
        # The closed form, and the one the DECISION reads: `z2_table()`'s own
        # cell arithmetic, so the sweep and the decision cannot disagree about
        # the one Delta0 they share.
        return _z2_pooled(x, n_left, y, n_right)
    p_left, p_right = constrained_mle(x, n_left, y, n_right, delta)
    numerator = (Fraction(x, n_left) - Fraction(y, n_right) - delta) ** 2
    variance = (p_left * (1 - p_left) / n_left
                + p_right * (1 - p_right) / n_right)
    if variance == 0:
        return Fraction(0) if numerator == 0 else math.inf
    return numerator / variance


def _z2_pooled(x: int, n_left: int, y: int, n_right: int) -> Fraction:
    total = n_left + n_right
    s = x + y
    den = n_left * n_right * s * (total - s)
    if den == 0:
        return Fraction(0)
    return Fraction(total * (x * n_right - y * n_left) ** 2, den)


def fm_z2_table(n_left: int, n_right: int, delta: Fraction) -> list:
    return [[fm_z2(x, n_left, y, n_right, delta) for y in range(n_right + 1)]
            for x in range(n_left + 1)]


def _tail_runs(table: list, level, n_left: int, n_right: int) -> list:
    """Per x, the maximal runs of consecutive y in the tail {z^2 >= level}.

    Runs rather than a membership test per mesh point: the tail is fixed once
    per Delta0 and the nuisance sup then scans a thousand mesh points over it,
    so summing a run through a prefix total is the difference between a
    thousand row scans and a thousand additions."""
    runs = []
    for x in range(n_left + 1):
        row, current, spans = table[x], None, []
        for y in range(n_right + 1):
            if row[y] >= level:
                current = (current[0], y) if current else (y, y)
            elif current:
                spans.append(current)
                current = None
        if current:
            spans.append(current)
        runs.append(spans)
    return runs


def delta_tail_sup(table: list, level, n_left: int, n_right: int,
                   delta: Fraction, mesh_den: int = MESH_DEN) -> Fraction:
    """sup over the registered nuisance mesh of P(z^2 >= level | Delta0), exact.

    The nuisance is p_C on the mesh M = {k/mesh_den}; p_A is p_C + Delta0, which
    is a point of the same mesh because `FM_DELTA_MESH_DEN` divides `mesh_den`.
    Every quantity below is an integer over the common denominator
    mesh_den^(n_A + n_C), so the whole supremum is exact integer arithmetic and
    no float stands between the mesh and the reported endpoint."""
    if mesh_den % delta.denominator:
        raise StatsError(
            "FM-MESH-INCOMMENSURATE Delta0 %s is not a point of the registered "
            "nuisance mesh with denominator %d" % (delta, mesh_den))
    shift = delta.numerator * (mesh_den // delta.denominator)
    runs = _tail_runs(table, level, n_left, n_right)
    comb_left = [math.comb(n_left, i) for i in range(n_left + 1)]
    comb_right = [math.comb(n_right, i) for i in range(n_right + 1)]
    best = 0
    for k in range(max(0, -shift), min(mesh_den, mesh_den - shift) + 1):
        u = k + shift
        left = [comb_left[i] * u ** i * (mesh_den - u) ** (n_left - i)
                for i in range(n_left + 1)]
        right = [comb_right[j] * k ** j * (mesh_den - k) ** (n_right - j)
                 for j in range(n_right + 1)]
        prefix = [0] * (n_right + 2)
        for j in range(n_right + 1):
            prefix[j + 1] = prefix[j] + right[j]
        total = 0
        for i in range(n_left + 1):
            spans = runs[i]
            if not spans or not left[i]:
                continue
            weight = 0
            for start, stop in spans:
                weight += prefix[stop + 1] - prefix[start]
            total += left[i] * weight
        if total > best:
            best = total
    return Fraction(best, mesh_den ** (n_left + n_right))


def fm_pvalue(x: int, y: int, n_left: int, n_right: int,
              delta: Fraction) -> Fraction:
    """The exact unconditional p-value for H0: p_A - p_C = Delta0.

    Equivalent to the critical-level construction the decision uses — the tail
    sup is non-increasing in the level and the observed statistic is an attained
    level, so `p <= alpha` and `z^2 >= c*` name the same rejection region — and
    stated as a p-value here because a SWEEP wants one sup per Delta0 rather
    than a binary search over levels at each."""
    table = fm_z2_table(n_left, n_right, delta)
    return delta_tail_sup(table, table[x][y], n_left, n_right, delta)


def interval_endpoints(x: int, y: int, n_left: int, n_right: int = None,
                       mesh_den: int = FM_DELTA_MESH_DEN) -> dict:
    """The REPORTED interval endpoints, by sweeping Delta0 (SCAFFOLD item S7).

    The registered construction is "the interval is {Delta : the FM test at
    Delta does not reject}", reported as its CONVEX HULL where the acceptance
    set is non-convex. This sweeps the registered Delta0 mesh, keeps the
    accepted points, and reports the hull's endpoints as exact rationals with
    the mesh that produced them and whether the accepted set was contiguous.

    PREREGISTRATION.md section 10 commits to publishing every interval, and this
    is that publication. It is a REPORT and not a decision: the zero-exclusion
    verdict is `excludes_zero()`'s and reads the acceptance set at Delta0 = 0
    itself, exactly, never the hull."""
    n_right = n_left if n_right is None else n_right
    if not 0 <= x <= n_left or not 0 <= y <= n_right:
        raise StatsError("FM-NOT-A-COUNT (%r, %r) are not two counts out of "
                         "(%r, %r)" % (x, y, n_left, n_right))
    accepted = []
    for j in range(-mesh_den, mesh_den + 1):
        delta = Fraction(j, mesh_den)
        if fm_pvalue(x, y, n_left, n_right, delta) > FM_ALPHA:
            accepted.append(j)
    if not accepted:
        raise StatsError(
            "FM-EMPTY-ACCEPTANCE no point of the registered Delta0 mesh "
            "(denominator %d) is accepted for (%d/%d, %d/%d): the interval is "
            "narrower than the mesh and no endpoint may be reported from it"
            % (mesh_den, x, n_left, y, n_right))
    lower, upper = Fraction(accepted[0], mesh_den), Fraction(accepted[-1],
                                                             mesh_den)
    contiguous = accepted == list(range(accepted[0], accepted[-1] + 1))
    return {
        "lower": str(lower),
        "upper": str(upper),
        "lowerFloat": float(lower),
        "upperFloat": float(upper),
        "acceptedPoints": len(accepted),
        "acceptanceContiguous": contiguous,
        "reportedAsConvexHull": not contiguous,
        "deltaMeshDenominator": mesh_den,
        "nuisanceMeshDenominator": MESH_DEN,
        "mleBisections": FM_MLE_BISECTIONS,
        "alpha": str(FM_ALPHA),
        "constructionName": CONSTRUCTION_NAME,
        "levelCertifiedOverContinuum": False,
        "nuisanceMeshSlackBound": str(mesh_slack_bound(n_left, n_right)),
        "approximationDirection":
            "TWO approximations, both one-directional. (1) The Delta0 inversion "
            "is over M_D = {j/%d}, so these endpoints are the hull of the "
            "ACCEPTED MESH POINTS — an INNER approximation: the reported hull "
            "can be narrower than the continuum acceptance set, never wider. "
            "(2) The nuisance supremum is over M = {k/%d} and is a LOWER bound "
            "on the continuum supremum, so the nominal level may be "
            "anti-conservative by at most nuisanceMeshSlackBound. Neither "
            "affects the zero-exclusion decision, which reads the exact "
            "Delta0 = 0 inversion" % (mesh_den, MESH_DEN),
        "construction": "%s: the acceptance set {Delta0 in M_D : the two-sided "
                        "Farrington-Manning score test at Delta0 does not "
                        "reject at alpha}, nuisance eliminated by maximisation "
                        "over the registered rational mesh, reported as the "
                        "convex hull of that set. NOT an exact 95%% confidence "
                        "interval over the continuous parameter space — see "
                        "approximationDirection" % CONSTRUCTION_NAME,
    }
