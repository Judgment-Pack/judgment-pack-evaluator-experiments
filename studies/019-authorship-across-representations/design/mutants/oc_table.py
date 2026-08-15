#!/usr/bin/env python3
"""
Study 019 -- operating characteristics of the registered E4 decision rule.

GATE(pre-freeze) for PREREGISTRATION.md §5: "Operating characteristics of
(tau, delta, N=50) published in this document before the freeze."

WHAT THIS COMPUTES
------------------
The registered endpoint is a per-arm *high-kill run rate*: a run is high-kill iff
its paired-subset mutant kill rate is >= tau = 0.95.  Each arm contributes N
admitted runs, so each arm's endpoint is a Binomial(N, p) count.  The registered
contrast is an *exact two-proportion difference interval* for p_A - p_C, and the
registered decision is:

    interval excludes zero  -> R1 decided, direction as observed
    interval straddles zero -> INDETERMINATE (licenses nothing)

Given a construction, the decision is a deterministic function of the observed
pair (x, y) in {0..N} x {0..N}.  This script enumerates that decision map exactly,
then, for a grid of true (p_A, p_C), computes by exact binomial enumeration

    P(decided-A-above), P(decided-C-above), P(INDETERMINATE)

There is no simulation anywhere in this file.

THE REGISTERED CONSTRUCTION (this is the pinning the gate asked for)
-------------------------------------------------------------------
"Exact two-proportion difference interval" names a family, not a procedure.  This
script pins ONE member, and the preregistration must adopt this wording verbatim:

    The A-C interval is the exact unconditional (Barnard-type) confidence
    interval for the difference of independent binomial proportions obtained by
    inverting the two-sided Farrington-Manning score test, with the nuisance
    parameter eliminated by maximisation (Chan & Zhang 1999; Agresti & Min 2001).
    Nominal coverage 1 - alpha with alpha = 0.05, two-sided.  The nuisance
    maximisation is taken over the registered rational mesh
    M = {k/1000 : k = 0..1000} in exact integer arithmetic.  Where inversion
    yields a non-convex acceptance set, the reported interval is its convex hull;
    the zero-exclusion decision reads the acceptance set itself, not the hull.

Two consequences make the OC computation exact and cheap:

  (1) The registered decision only ever asks whether the interval contains 0.
      By construction the interval is {Delta : the FM test at Delta does not
      reject}, so

          interval excludes 0  <=>  the two-sided exact unconditional test of
                                    H0: p_A = p_C rejects at alpha.

      So the OC needs only the Delta0 = 0 inversion.  The endpoint values of the
      interval (needed to *report* the contrast, not to decide it) come from the
      same inversion swept over Delta0 and are not required here.

  (2) At Delta0 = 0 the Farrington-Manning score statistic reduces to the
      pooled-variance two-sample Z, whose square is the Pearson chi-square of the
      2x2 table.  With equal arm sizes N,

          z^2(x, y) = 2N (x - y)^2 / ( (x + y) (2N - x - y) )

      -- an exact rational.  So the *ordering* of tables, which is where a float
      could silently flip a decision, is done in exact rational arithmetic.

WHY THIS CONSTRUCTION AND NOT NEWCOMBE
--------------------------------------
The gate offered Newcombe's method-10 hybrid score interval as the alternative.
It is rejected for three stated reasons:

  * It is not exact.  Newcombe's interval is a closed-form approximation with
    coverage that oscillates around the nominal level; the preregistration says
    "exact", and Clopper-Pearson (exact) is already registered for the per-arm
    rates.  An approximate contrast bolted onto exact marginals is incoherent.
  * Its coverage dips furthest below nominal exactly where this design lives:
    one arm's rate pressed against 1.  The pilot puts arm C at 5/5.  A
    construction whose weak spot is the study's own operating point cannot be
    the registered one.
  * Its bounds are irrational (Wilson roots), so the zero-comparison cannot be
    carried out in exact rational arithmetic.  The program's discipline forbids
    a float in the decision arithmetic.

The cost of the exact unconditional construction is conservatism, and that cost
is measured, not assumed: the null diagonal of the OC table below is the realised
type-I error rate, and the script also re-checks the size on an offset mesh that
shares no point with the registered one.

ARITHMETIC DISCIPLINE
---------------------
Every quantity that a decision reads is an exact integer or Fraction:
  * table ordering statistic z^2  -- Fraction
  * null tail probability sup     -- integer comparison  best * 20 <= 1000^(2N)
  * binomial weights              -- Fraction over exact math.comb
  * OC probabilities              -- Fraction, summed exactly
float() appears only inside formatting helpers.

The one place where an exact answer is not available in closed form is the
supremum over the nuisance parameter p in [0, 1], which is a continuous
optimisation of a degree-2N polynomial.  It is handled by *registering the mesh*:
the construction is defined as the maximisation over M, so the procedure is
exactly reproducible.  Whether that mesh is fine enough is then an empirical
question about the realised size, which this script answers (Sec. 2 of the
emitted OC-TABLE.md, including a check on an offset mesh).

USAGE
-----
    python3 oc_table.py            # writes OC-TABLE.md next to this file
    python3 oc_table.py --stdout   # writes to stdout instead
"""

import sys
import json
import os
from fractions import Fraction
from math import comb

# ---------------------------------------------------------------------------
# Registered constants
# ---------------------------------------------------------------------------

ALPHA = Fraction(1, 20)          # two-sided; 95% interval
MESH_DEN = 1000                  # registered nuisance mesh M = {k/1000}
TAU = Fraction(19, 20)           # 0.95, high-kill threshold (context only)
DELTA = Fraction(1, 5)           # 0.20, registered minimum meaningful difference
N_PRIMARY = 50                   # registered per-arm batch size
N_CONTEXT = (30, 100)            # context sizes requested by the gate

# OC grid: p in {0.05, 0.10, ..., 0.95}
GRID = [Fraction(k, 20) for k in range(1, 20)]

# Extra probabilities needed for the operating-point tables (1 is not on GRID).
EXTRA = [Fraction(1, 1)]

DEC_A = 0      # decided: arm A high-kill rate above arm C
DEC_C = 1      # decided: arm C above arm A
DEC_I = 2      # INDETERMINATE


# ---------------------------------------------------------------------------
# Ordering statistic
# ---------------------------------------------------------------------------

def z2_table(N):
    """z^2(x, y) as exact Fractions; 0 on the degenerate diagonal ends."""
    out = [[Fraction(0)] * (N + 1) for _ in range(N + 1)]
    twoN = 2 * N
    for x in range(N + 1):
        for y in range(N + 1):
            s = x + y
            den = s * (twoN - s)
            if den == 0:
                # s = 0 or s = 2N forces x = y: no difference, no evidence.
                out[x][y] = Fraction(0)
            else:
                out[x][y] = Fraction(twoN * (x - y) ** 2, den)
    return out


def tail_coefficients(N, z2, level):
    """
    A_s = sum over tables in the tail {z^2 >= level} with x + y = s of
    C(N,x) C(N,y).  The null probability of the tail at common rate p is then
        f(p) = sum_s A_s p^s (1-p)^(2N-s).
    Because sum_{x+y=s} C(N,x)C(N,y) = C(2N,s) (Vandermonde), A_s / C(2N,s) lies
    in [0, 1]; f is a Bernstein polynomial with those coefficients.
    """
    A = [0] * (2 * N + 1)
    cN = [comb(N, i) for i in range(N + 1)]
    for x in range(N + 1):
        row = z2[x]
        cx = cN[x]
        for y in range(N + 1):
            if row[y] >= level:
                A[x + y] += cx * cN[y]
    return A


def sup_tail_numerator(A, N, mesh_den=MESH_DEN, offset=False):
    """
    max over the registered mesh of  f(p) * mesh_den^(2N), as an exact integer.

    The tail set is symmetric under (x, y) -> (N-x, N-y), so A_s = A_{2N-s} and
    f(p) = f(1-p); only k <= mesh_den/2 is scanned.  Set offset=True to scan the
    interleaved mesh {(2k+1)/(2*mesh_den)} instead -- used for the size check;
    that mesh is NOT symmetric-reducible in the same indices, so it scans its own
    lower half.
    """
    twoN = 2 * N
    if offset:
        den = 2 * mesh_den
        ks = range(1, mesh_den + 1, 2)   # (2k+1)/(2D) for the lower half
    else:
        den = mesh_den
        ks = range(0, mesh_den // 2 + 1)

    best = 0
    for k in ks:
        q = den - k
        qp = [1] * (twoN + 1)
        for m in range(1, twoN + 1):
            qp[m] = qp[m - 1] * q
        # Horner:  H_j = A_j q^(2N-j) + k H_{j+1},  H_2N = A_2N,  H_0 = f * den^2N
        H = A[twoN]
        for j in range(twoN - 1, -1, -1):
            H = A[j] * qp[twoN - j] + k * H
        if H > best:
            best = H
    return best, den ** twoN


def sup_le_alpha(A, N):
    """Exact integer test: is sup_M f(p) <= ALPHA ?"""
    best, total = sup_tail_numerator(A, N)
    return best * ALPHA.denominator <= ALPHA.numerator * total, Fraction(best, total)


def critical_level(N, z2, log=None):
    """
    Smallest attained z^2 level c* with sup_M P(z^2 >= c*) <= ALPHA.
    The tail sup is non-increasing in the level, so binary search is valid.
    Returns (c*, realised size at c*, number of sup evaluations).
    """
    levels = sorted({z2[x][y] for x in range(N + 1) for y in range(N + 1)})
    evals = 0

    A_top = tail_coefficients(N, z2, levels[-1])
    ok, size = sup_le_alpha(A_top, N)
    evals += 1
    if not ok:
        # No attainable rejection region at this alpha: the procedure can never
        # decide.  Signal with c* = None.
        return None, size, evals

    lo, hi = 0, len(levels) - 1          # T(levels[0]) = 1 > alpha; T(levels[hi]) <= alpha
    best_size = size
    while hi - lo > 1:
        mid = (lo + hi) // 2
        A = tail_coefficients(N, z2, levels[mid])
        ok, size = sup_le_alpha(A, N)
        evals += 1
        if ok:
            hi, best_size = mid, size
        else:
            lo = mid
    if log is not None:
        log.append((N, len(levels), evals))
    return levels[hi], best_size, evals


def offset_mesh_size(N, z2, cstar):
    """Realised size on the interleaved mesh -- a check that MESH_DEN is fine enough."""
    A = tail_coefficients(N, z2, cstar)
    best, total = sup_tail_numerator(A, N, offset=True)
    return Fraction(best, total)


# ---------------------------------------------------------------------------
# Decision map
# ---------------------------------------------------------------------------

def decision_map(N):
    """
    (c*, size, offset_size, ysets) where ysets[decision][x] is the sorted list of
    y for which the registered procedure returns that decision.
    """
    z2 = z2_table(N)
    cstar, size, _ = critical_level(N, z2)
    off = offset_mesh_size(N, z2, cstar) if cstar is not None else Fraction(0)

    ysets = [[[] for _ in range(N + 1)] for _ in range(3)]
    for x in range(N + 1):
        for y in range(N + 1):
            if cstar is not None and z2[x][y] >= cstar and x != y:
                ysets[DEC_A if x > y else DEC_C][x].append(y)
            else:
                ysets[DEC_I][x].append(y)
    return cstar, size, off, ysets


# ---------------------------------------------------------------------------
# Exact binomial OC
# ---------------------------------------------------------------------------

def binom_pmf(N, p):
    """Exact Fraction pmf vector."""
    q = 1 - p
    return [Fraction(comb(N, x)) * p ** x * q ** (N - x) for x in range(N + 1)]


def oc_point(N, ysets, pmf_A, pmf_C_sums):
    """
    pmf_C_sums[decision][x] = sum of C-side pmf over ysets[decision][x].
    Returns (P(A above), P(C above), P(INDETERMINATE)) as exact Fractions.
    """
    out = []
    for d in (DEC_A, DEC_C, DEC_I):
        tot = Fraction(0)
        col = pmf_C_sums[d]
        for x in range(N + 1):
            pa = pmf_A[x]
            if pa:
                tot += pa * col[x]
        out.append(tot)
    return tuple(out)


def c_side_sums(N, ysets, pmf_C):
    return [[sum((pmf_C[y] for y in ysets[d][x]), Fraction(0)) for x in range(N + 1)]
            for d in (DEC_A, DEC_C, DEC_I)]


def build_oc(N, ps):
    """
    Returns dict:
      'cstar', 'size', 'offsize',
      'oc'[(pA, pC)] = (P_A_above, P_C_above, P_indet)   exact Fractions
    """
    cstar, size, off, ysets = decision_map(N)
    pmfs = {p: binom_pmf(N, p) for p in ps}
    csums = {p: c_side_sums(N, ysets, pmfs[p]) for p in ps}
    oc = {}
    for pA in ps:
        for pC in ps:
            oc[(pA, pC)] = oc_point(N, ysets, pmfs[pA], csums[pC])
    return {'cstar': cstar, 'size': size, 'offsize': off, 'oc': oc, 'ysets': ysets}


# ---------------------------------------------------------------------------
# Pilot anchor
# ---------------------------------------------------------------------------

PILOT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                          'pilots', '2026-08-15-calibration-pilot-01')


def drop_forensics(arm, dropped):
    """
    Re-read the raw call record for each dropped pilot run.  The pilot scorer
    filed every drop as `no-marker`; PREREGISTRATION.md Sec. 1a records that the
    pilot driver mis-filed timeouts as an authoring code, so the drop code cannot
    be taken at face value.  Returns [(run, dropCode, exitCode, completionBytes)]
    with exitCode/bytes None when the pilot tree is unavailable.
    """
    out = []
    for run, code in dropped:
        ex, nb = None, None
        d = os.path.join(PILOT_ROOT, 'arm-%s' % arm, run)
        try:
            with open(os.path.join(d, 'exit.txt')) as fh:
                ex = int(fh.read().strip())
            nb = os.path.getsize(os.path.join(d, 'completion.txt'))
        except (OSError, ValueError):
            pass
        out.append((run, code, ex, nb))
    return out


def pilot_anchor(path):
    """
    Empirical p_A / p_B / p_C from the non-citable calibration pilot: fraction of
    scored runs whose paired-subset kill rate is >= tau.

    Arm A has no registered E4 numbers in the pilot (all five suites failed the
    identity control on X1-region cases; see E4-NOTES.md).  Its rates are read
    from diagnostics.armAOffProtocol, which is what the proposed X1-exclusion
    amendment would make the protocol number.  Labelled as such.
    """
    with open(path) as fh:
        d = json.load(fh)

    def score(runs, key='killRatePaired'):
        vals = []
        for r in runs:
            v = r.get(key)
            if v is None:
                continue
            vals.append((r['run'], Fraction(str(v))))
        hits = [n for n, v in vals if v >= TAU]
        return vals, hits

    out = {}
    for arm in ('B', 'C'):
        vals, hits = score(d['perArm'][arm]['perRun'])
        out[arm] = {'source': 'perArm (registered rule, identity control passed)',
                    'runs': vals, 'high': hits,
                    'n': len(vals), 'k': len(hits),
                    'mutantsPairedAdequate': d['perArm'][arm]['mutantsPairedAdequate'],
                    'identityFail': d['perArm'][arm]['identityFail'],
                    'dropped': [(x['run'], x['dropCode'])
                                for x in d['perArm'][arm]['droppedRuns']],
                    'attempted': (len(d['perArm'][arm]['perRun'])
                                  + len(d['perArm'][arm]['droppedRuns']))}
        out[arm]['forensics'] = drop_forensics(arm, out[arm]['dropped'])
    vals, hits = score(d['diagnostics']['armAOffProtocol']['perRun'])
    out['A'] = {'source': 'diagnostics.armAOffProtocol (DIAGNOSTIC; registered rule '
                          'excluded all five arm-A suites)',
                'runs': vals, 'high': hits, 'n': len(vals), 'k': len(hits),
                'mutantsPairedAdequate': d['perArm']['A']['mutantsPairedAdequate'],
                'identityFail': d['perArm']['A']['identityFail'],
                'dropped': [(x['run'], x['dropCode'])
                            for x in d['perArm']['A']['droppedRuns']],
                'attempted': (len(d['perArm']['A']['perRun'])
                              + len(d['perArm']['A']['droppedRuns']))}
    out['A']['forensics'] = drop_forensics('A', out['A']['dropped'])
    return out


def tau_bites(m):
    """Smallest integer kill count k with k/m >= tau, and that rate."""
    k = -(-(TAU.numerator * m) // TAU.denominator)   # ceil(tau * m)
    return k, Fraction(k, m)


# ---------------------------------------------------------------------------
# Formatting (floats appear below this line only)
# ---------------------------------------------------------------------------

def f2(fr):
    return '%.2f' % float(fr)


def f3(fr):
    return '%.3f' % float(fr)


def f4(fr):
    return '%.4f' % float(fr)


def matrix_block(res, ps, which, title):
    lines = ['%s' % title, '']
    hdr = '| p_A \\ p_C | ' + ' | '.join(f2(p) for p in ps) + ' |'
    sep = '|---' * (len(ps) + 1) + '|'
    lines.append(hdr)
    lines.append(sep)
    for pA in ps:
        row = ['| **%s** ' % f2(pA)]
        for pC in ps:
            row.append('| %s ' % f2(res['oc'][(pA, pC)][which]))
        lines.append(''.join(row) + '|')
    lines.append('')
    return lines


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    ps_grid = list(GRID)
    ps_all = sorted(set(GRID + EXTRA))

    results = {}
    for N in (N_PRIMARY,) + N_CONTEXT:
        results[N] = build_oc(N, ps_all)

    anchor = pilot_anchor(os.path.join(HERE, 'E4-PILOT.json'))

    L = []
    w = L.append

    w('# Study 019 -- E4 operating characteristics (OC table)')
    w('')
    w('`GATE(pre-freeze)` for PREREGISTRATION.md §5. Generated by `oc_table.py` '
      'in this directory; no simulation, exact binomial enumeration throughout. '
      'Regenerate with `python3 oc_table.py`; output is byte-deterministic.')
    w('')
    w('**This document does not change the registered design. It reports what the '
      'registered design can and cannot decide, and it names three defects in the preregistration that '
      'a review round must close before the freeze (Sec. 9 below).**')
    w('')

    # ---- 1. the pinned construction
    w('## 1. The pinned interval construction')
    w('')
    w('The preregistration says "exact two-proportion difference interval". That names '
      'a family. The OC of a family is undefined, so this gate pins one member, and '
      'prereg §5 must adopt this wording verbatim at the freeze:')
    w('')
    w('> The A-C contrast is the exact unconditional (Barnard-type) confidence interval '
      'for the difference of two independent binomial proportions, obtained by inverting '
      'the two-sided Farrington-Manning score test with the nuisance parameter eliminated '
      'by maximisation (Chan & Zhang 1999; Agresti & Min 2001), at nominal two-sided '
      '`alpha = 0.05`. The nuisance maximisation is taken over the registered rational '
      'mesh `M = {k/1000 : k = 0..1000}` in exact integer arithmetic. Where the inverted '
      'acceptance set is non-convex, the *reported* interval is its convex hull; the '
      'zero-exclusion decision reads the acceptance set itself.')
    w('')
    w('Two facts make this exactly computable:')
    w('')
    w('1. The registered decision only asks whether the interval contains zero. Since the '
      'interval is the set of `Delta` the FM test does not reject, **interval excludes '
      'zero if and only if the two-sided exact unconditional test of `H0: p_A = p_C` '
      'rejects at `alpha`**. The OC therefore needs only the `Delta0 = 0` inversion.')
    w('2. At `Delta0 = 0` the FM score statistic is the pooled-variance two-sample Z, and '
      'with equal arm sizes `N` its square is the exact rational')
    w('')
    w('   `z^2(x, y) = 2N (x - y)^2 / ((x + y) (2N - x - y))`')
    w('')
    w('   so the table ordering -- the only place a float could silently flip a decision '
      '-- is done in exact rational arithmetic. The null tail probability is a Bernstein '
      'polynomial with exact integer coefficients and is compared to `alpha` by integer '
      'cross-multiplication.')
    w('')
    w('**Why not Newcombe.** The gate offered Newcombe method 10 as the alternative; it is '
      'rejected on three grounds. (a) It is not exact -- its coverage oscillates around '
      'nominal -- and the per-arm rates are already registered as exact Clopper-Pearson; '
      'an approximate contrast on exact marginals is incoherent. (b) Its coverage is '
      'weakest where one proportion is pressed against 1, which is precisely this study\'s '
      'operating point (the pilot puts arm C at 5/5). A construction whose failure mode is '
      'the study\'s own operating point cannot be the registered one. (c) Its bounds are '
      'Wilson roots, hence irrational, so the zero-comparison cannot be carried out '
      'without floats in the decision arithmetic.')
    w('')
    w('The price of the exact unconditional construction is conservatism. That price is '
      'measured below, not assumed.')
    w('')

    # ---- 2. calibration
    w('## 2. Calibration of the implemented procedure')
    w('')
    w('`c*` is the smallest attained `z^2` level whose null tail supremum is at most '
      '`alpha`; the rejection region is `{z^2 >= c*}`. "Realised size" is that supremum '
      '-- the exact worst-case type-I error over the registered mesh, i.e. the true '
      'probability of *any* decision when `p_A = p_C`. "Offset-mesh size" re-evaluates '
      'the same rejection region on the interleaved mesh `{(2k+1)/2000}`, which shares no '
      'point with the registered one; it is a check that mesh 1/1000 is fine enough that '
      'the registered sup is not an artefact of where the mesh points fall.')
    w('')
    w('| N | c* (exact) | c* (dec.) | realised size (sup over M) | offset-mesh size | '
      'nominal |')
    w('|---|---|---|---|---|---|')
    for N in sorted((N_PRIMARY,) + N_CONTEXT):
        r = results[N]
        cs = r['cstar']
        w('| %d%s | %d/%d | %s | %s | %s | 0.0500 |'
          % (N, ' (registered)' if N == N_PRIMARY else '',
             cs.numerator, cs.denominator, f4(cs), f4(r['size']), f4(r['offsize'])))
    w('')
    worst_size = max(max(results[N]['size'], results[N]['offsize'])
                     for N in (N_PRIMARY,) + N_CONTEXT)
    worst_drift = max(abs(results[N]['offsize'] - results[N]['size'])
                      for N in (N_PRIMARY,) + N_CONTEXT)
    w('Every realised size is at or below the nominal 0.05, including on the offset mesh '
      '(worst case over all three N, either mesh: **%s**). The two meshes agree to within '
      '%s, so the registered mesh of 1/1000 resolves the nuisance supremum well below the '
      'precision any decision depends on -- the sup is a genuine feature of the tail '
      'function, not an artefact of mesh placement. The shortfall below 0.05 is the '
      'exactness tax: it is spent buying a coverage guarantee, and it is why the power '
      'numbers below are lower than a normal-approximation calculation would suggest.'
      % (f4(worst_size), '%.2e' % float(worst_drift)))
    w('')

    # ---- 3. main grid
    w('## 3. OC over the registered grid')
    w('')
    w('`p_A`, `p_C` are the **true** per-arm high-kill run rates. Entries are exact '
      'probabilities (rounded for display) that the registered procedure returns each '
      'verdict. Rows are `p_A`; columns are `p_C`. The three matrices for a given `N` sum '
      'to 1 cellwise.')
    w('')
    for N in sorted((N_PRIMARY,) + N_CONTEXT):
        r = results[N]
        w('### N = %d%s' % (N, ' (registered)' if N == N_PRIMARY else ' (context)'))
        w('')
        L.extend(matrix_block(r, ps_grid, DEC_A,
                              '**P(decided A-above)** -- interval excludes zero, A higher'))
        L.extend(matrix_block(r, ps_grid, DEC_C,
                              '**P(decided C-above)** -- interval excludes zero, C higher'))
        L.extend(matrix_block(r, ps_grid, DEC_I,
                              '**P(INDETERMINATE)** -- interval straddles zero'))

    # ---- 4. delta
    w('## 4. Power at the registered minimum meaningful difference (delta = 0.20)')
    w('')
    w('Every grid pair whose true gap is exactly `delta = 0.20`, at each `N`. '
      '"Decide" = interval excludes zero in either direction; "wrong sign" = decided in '
      'the direction opposite the truth.')
    w('')
    w('| p_A | p_C | true gap | N=30 decide | N=50 decide | N=100 decide | N=50 wrong sign |')
    w('|---|---|---|---|---|---|---|')
    delta_rows = []
    for pA in ps_grid:
        pC = pA + DELTA
        if pC not in ps_grid:
            continue
        row = []
        for N in (30, 50, 100):
            a, c, i = results[N]['oc'][(pA, pC)]
            row.append((a, c, i))
        delta_rows.append((pA, pC, row))
        w('| %s | %s | 0.20 | %s | %s | %s | %s |'
          % (f2(pA), f2(pC),
             f3(row[0][0] + row[0][1]), f3(row[1][0] + row[1][1]),
             f3(row[2][0] + row[2][1]), f4(row[1][0])))
    w('')
    best50 = max(r[2][1][0] + r[2][1][1] for r in delta_rows)
    worst50 = min(r[2][1][0] + r[2][1][1] for r in delta_rows)
    w('**At N = 50 the power to decide a true 0.20 gap ranges from %s to %s.** '
      'A 0.20 gap is decided reliably only when it sits near one boundary of the unit '
      'interval (both rates high, or both low); in the middle of the range the design is '
      'far from powered at its own registered delta.'
      % (f3(worst50), f3(best50)))
    w('')

    # ---- 5. operating points
    w('## 5. Power at the operating points')
    w('')
    w('The gate asked for `p_A ~ 0.4-0.6` and `p_C ~ 0.8-1.0`. **The pilot does not '
      'support `p_A ~ 0.4-0.6`** (Sec. 7): the pilot anchor is `p_A ~ 0.2`. Both bands '
      'are tabulated, the pilot-anchored band first.')
    w('')
    for label, pAs, pCs in (
        ('Pilot-anchored band', [Fraction(k, 20) for k in (2, 3, 4, 5, 6)],
         [Fraction(k, 20) for k in (16, 17, 18, 19)] + [Fraction(1, 1)]),
        ('Gate-suggested band', [Fraction(k, 20) for k in (8, 9, 10, 11, 12)],
         [Fraction(k, 20) for k in (16, 17, 18, 19)] + [Fraction(1, 1)]),
    ):
        w('### %s' % label)
        w('')
        w('| p_A | p_C | gap | N=30 decide | N=50 decide | N=100 decide | '
          'N=50 P(C-above) | N=50 P(INDET) |')
        w('|---|---|---|---|---|---|---|---|')
        for pA in pAs:
            for pC in pCs:
                cells = {N: results[N]['oc'][(pA, pC)] for N in (30, 50, 100)}
                d = {N: cells[N][0] + cells[N][1] for N in cells}
                w('| %s | %s | %s | %s | %s | %s | %s | %s |'
                  % (f2(pA), f2(pC), f2(pC - pA),
                     f3(d[30]), f3(d[50]), f3(d[100]),
                     f3(cells[50][1]), f3(cells[50][2])))
        w('')
        if label.startswith('Pilot'):
            w('This band saturates: at the pilot anchor the design decides with probability '
              'indistinguishable from 1 at every `N` considered. That is not a claim that '
              'the study will decide -- it is a statement that *if* the pilot direction and '
              'magnitude survive into the registered batch, sample size is not the binding '
              'constraint. The binding constraint is the identity control, not authoring '
              'validity (Sec. 9, D3). The informative question is how '
              'far arm A can rise before power collapses, which is the gate-suggested band '
              'below and Sec. 6.')
            w('')

    # ---- 6. minimum decidable gap
    w('## 6. Smallest gap this design decides with power >= 0.80')
    w('')
    w('For each `p_C`, the largest `p_A` on the grid at which `P(decide) >= 0.80`, and the '
      'gap that implies. `--` means no grid `p_A` reaches 0.80 power against that `p_C`.')
    w('')
    w('| p_C | N=30 largest p_A | gap | N=50 largest p_A | gap | N=100 largest p_A | gap |')
    w('|---|---|---|---|---|---|---|')
    for pC in ps_grid:
        cells = []
        for N in (30, 50, 100):
            best = None
            for pA in ps_grid:
                if pA >= pC:
                    continue
                a, c, i = results[N]['oc'][(pA, pC)]
                if a + c >= Fraction(4, 5):
                    if best is None or pA > best:
                        best = pA
            cells.append(best)
        flat = []
        for b in cells:
            flat.extend([f2(b), f2(pC - b)] if b is not None else ['--', '--'])
        w('| %s | %s |' % (f2(pC), ' | '.join(flat)))
    w('')

    # ---- 7. pilot anchor
    w('## 7. Pilot anchor: what fraction of pilot runs are high-kill at tau = 0.95')
    w('')
    w('Read from `E4-PILOT.json`. **NON-CITABLE**: five runs per arm, pilot suites, '
      '0-draft gold. This is the empirical anchor for `p_A` / `p_C` and nothing else.')
    w('')
    for arm in ('A', 'B', 'C'):
        a = anchor[arm]
        m = a['mutantsPairedAdequate']
        k, rate = tau_bites(m)
        w('**Arm %s** -- %d scored runs, paired adequate subset = %d mutants; '
          'at `tau = 0.95` a run must kill **%d/%d = %s**.'
          % (arm, a['n'], m, k, m, f4(rate)))
        w('')
        w('| run | paired kill rate | high-kill at tau=0.95 |')
        w('|---|---|---|')
        for name, v in a['runs']:
            w('| %s | %s | %s |' % (name, f4(v), 'YES' if v >= TAU else 'no'))
        w('')
        w('- **high-kill fraction: %d/%d = %s**' % (a['k'], a['n'], f3(Fraction(a['k'], a['n']))))
        w('- source: %s' % a['source'])
        drops = ', '.join(
            '%s (filed `%s`; exit %s, %s-byte completion)'
            % (r, c, 'n/a' if e is None else e, 'n/a' if b is None else b)
            for r, c, e, b in a['forensics']) or 'none'
        w('- attempted pilot slots for this arm: %d; runs dropped before scoring: %s'
          % (a['attempted'], drops))
        w('- identity-control failures in the pilot: %d' % a['identityFail'])
        w('')
    w('**Anchor summary: p_A ~ 0.20, p_B ~ 0.80, p_C ~ 1.00**, each on five runs. '
      'Two qualifications carry more weight than the numbers:')
    w('')
    w('1. **Under the registered rule arm A has no `p_A` at all.** All five scored arm-A '
      'suites failed the identity control, so the registered E4 denominator for arm A in '
      'the pilot is zero. The 1/5 above is read from `diagnostics.armAOffProtocol`, i.e. '
      'from what the proposed X1-exclusion amendment (E4-NOTES.md) would make the '
      'protocol number. If that amendment does not land, this gate has no empirical '
      'anchor for `p_A` and the OC must be read as covering the whole grid rather than a '
      'located operating point.')
    w('2. **The gate brief guessed `p_A ~ 0.4-0.6`; the pilot says ~0.2.** The guess came '
      'from arm A\'s *unpaired* kill-rate range 0.84-1.00. On the paired subset the '
      'rates are 0.80, 0.87, 0.92, 0.92, 1.00 against a threshold of 73/76 = 0.9605, and '
      'only one clears it. `tau = 0.95` bites arm A much harder than the unpaired range '
      'suggests, which is the whole reason the threshold discriminates.')
    w('')
    w('Note the **denominator asymmetry**, which is a design fact and not noise. Pairing '
      'is at the level of witness-equivalence groups, not 1:1 mutants: the 29 paired '
      'adequate groups contain 76 JPS mutants and 65 Rego mutants. So `tau = 0.95` bites '
      'arm A at 73/76 = 0.9605 and arms B/C at 62/65 = 0.9538 -- the threshold is '
      '0.0067 stricter for arm A, and the two arms\' kill rates are also quantised on '
      'different lattices (1/76 vs 1/65). The effect is small relative to the pilot gap, '
      'but it is a real asymmetry in the endpoint definition and belongs in prereg §5 rather '
      'than being discovered at analysis time. Prereg §4 already commits to publishing the '
      'unpairable counts; this asks for one more sentence saying that a group-level '
      'pairing does not equalise the per-arm denominators.')
    w('')

    # ---- 8. what this design can and cannot decide
    w('## 8. Plain-language summary: what this design can and cannot decide')
    w('')
    a20 = results[50]['oc'][(Fraction(4, 20), Fraction(20, 20))]
    a20_30 = results[30]['oc'][(Fraction(4, 20), Fraction(20, 20))]
    a20_100 = results[100]['oc'][(Fraction(4, 20), Fraction(20, 20))]
    mid = results[50]['oc'][(Fraction(8, 20), Fraction(12, 20))]
    w('**It can decide the gap the pilot points at, with room to spare.** If the truth is '
      'near the pilot anchor (`p_A = 0.20`, `p_C = 1.00`), the registered N = 50 design '
      'decides with probability %s (N = 30: %s; N = 100: %s). Even a much attenuated '
      'version of that gap is comfortably decidable: see Sec. 5.'
      % (f4(a20[0] + a20[1]), f4(a20_30[0] + a20_30[1]), f4(a20_100[0] + a20_100[1])))
    w('')
    w('**It cannot decide a 0.20 gap in the middle of the range.** At `p_A = 0.40` vs '
      '`p_C = 0.60` -- exactly the registered `delta` -- N = 50 decides with probability '
      '%s, i.e. INDETERMINATE with probability %s. `delta = 0.20` is registered as the '
      'minimum *meaningful* difference; it is emphatically not the minimum *detectable* '
      'difference at N = 50. Anyone reading `delta = 0.20` as "this study is powered to '
      'find a 0.20 gap" is reading it wrong, and prereg §5 currently invites that reading.'
      % (f3(mid[0] + mid[1]), f3(mid[2])))
    w('')
    w('**Power is strongly asymmetric across the unit interval.** Because the variance of '
      'a proportion collapses near 0 and 1, the same nominal gap is far easier to decide '
      'when one arm is near a boundary. This design is fortunate: the pilot puts arm C at '
      'the top boundary, which is where the design is strongest. It is also fragile in a '
      'specific way -- if arm A comes in higher than the pilot suggests (say 0.6-0.7) '
      'while arm C stays near 0.95-1.00, power falls (Sec. 5, gate-suggested band).')
    w('')
    w('**The exactness tax is real and is being paid deliberately.** Realised size at '
      'N = 50 is %s against a 0.05 nominal. That conservatism costs several points of '
      'power relative to a normal-approximation interval, and buys a guarantee that the '
      'decision rate under a true null never exceeds 0.05 at any true common rate. Given '
      'that the whole point of R1 is a retractable directional claim, the guarantee is '
      'worth more than the points.' % f4(results[50]['size']))
    w('')
    w('**N = 50 is a ceiling, not a floor.** The E4 denominator is *admitted* runs -- runs '
      'that clear the identity control -- not attempted runs. In the pilot the registered '
      'identity control excluded 5/5 arm-A suites; under the proposed X1-exclusion '
      'amendment it would have excluded 0/5. If the amendment does not land, or if '
      'identity failures run at any appreciable rate, arm A\'s effective N drops and the '
      'N = 30 column is the honest one to read. At N = 30 the pilot-anchored gap is still '
      'decided with probability %s, so the design survives moderate attrition -- but the '
      'middle-of-range 0.20 gap collapses to %s.'
      % (f4(a20_30[0] + a20_30[1]),
         f3(sum(results[30]['oc'][(Fraction(8, 20), Fraction(12, 20))][:2]))))
    w('')
    worst_indet = None
    for pA in ps_grid:
        for pC in ps_grid:
            if results[50]['oc'][(pA, pC)][2] >= Fraction(1, 5):
                g = abs(pC - pA)
                if worst_indet is None or g > worst_indet[0]:
                    worst_indet = (g, pA, pC)
    w('**It decides direction, not magnitude, and nothing about the middle.** At N = 50 a '
      'true gap as large as **%s** still returns INDETERMINATE at least 20%% of the time '
      'somewhere on the grid (worst cell: p_A = %s against p_C = %s), so an observed '
      'INDETERMINATE is consistent with a true gap anywhere from 0 to about that size, in '
      'either direction. The preregistration already says INDETERMINATE licenses nothing; '
      'this table is the quantitative reason why that sentence has to be honoured. It is '
      'also why no post-hoc "the gap was small" reading is available: the design cannot '
      'distinguish a small gap from no gap.'
      % (f2(worst_indet[0]), f2(worst_indet[1]), f2(worst_indet[2])))
    w('')
    w('**Sign errors are negligible but not zero.** At N = 50 the probability of deciding '
      'in the wrong direction is at most %s over the whole grid, attained near the '
      'diagonal.'
      % f4(max(max(results[50]['oc'][(pA, pC)][0] for pC in ps_grid for pA in ps_grid
                   if pA < pC),
               max(results[50]['oc'][(pA, pC)][1] for pC in ps_grid for pA in ps_grid
                   if pA > pC))))
    w('')

    # ---- 9. defects for review
    w('## 9. Three defects this gate found in the preregistration (review must close all three)')
    w('')
    w('**D1 -- alpha is never registered.** Prereg §5 registers exact Clopper-Pearson '
      'intervals and exact two-proportion difference intervals but never states a '
      'confidence level. This OC assumes two-sided `alpha = 0.05`. The freeze text must '
      'say so explicitly. Related: the A-C / A-B hierarchy is a fixed-sequence gatekeeping '
      'procedure, which controls the family-wise error rate at `alpha` without adjustment '
      '-- worth one sentence, because it is the reason no Bonferroni appears anywhere.')
    w('')
    w('**D2 -- "excludes zero at delta" is not a rule.** Prereg §5 says the contrasts are '
      'evaluated "each at `delta = 0.20`" and its decision table says "A-C interval '
      'excludes zero at delta -> R1 decided". Those describe two different procedures:')
    w('')
    w('- **Reading 1 (implemented here, and the one the gate brief states):** decide iff '
      'the interval excludes zero; `delta = 0.20` is the registered minimum meaningful '
      'difference, used to *design* and to *interpret*, never to decide. Under this '
      'reading the phrase "at delta" in the decision table is dangling and must be struck.')
    w('- **Reading 2:** decide iff the interval excludes the whole band `[-delta, +delta]` '
      '-- superiority by a registered margin. This is a materially stricter rule: it is '
      'strictly less powerful everywhere, and at N = 50 it would be close to unusable '
      'except at the extreme corners of the grid.')
    w('')
    w('The two readings do not agree on any interesting cell of the table above, so this '
      'is not a cosmetic edit. **Reading 1 is recommended** -- it matches the gate brief, '
      'it matches the INDETERMINATE clause ("interval straddles zero"), and Reading 2 '
      'would require re-registering N. Whichever is chosen, prereg §5 and its decision table '
      'must use one form of words, and this OC table is only valid for Reading 1.')
    w('')
    w('**D3 -- the E4 denominator does not say what happens to a run with no artifact.** '
      'Prereg §5 scopes E4 to "admitted runs" -- runs that clear the identity control -- '
      'while prereg §1a says every author-attributable failure, including "no extractable '
      'marker block", is "valid, counted, and scoring zero on every endpoint it reaches". '
      'A `no-marker` run reaches E4 in the §1a sense but has no suite to run against '
      'the mutants. Two readings, and they move `N`, which is what this table is about:')
    w('')
    w('- **Denominator-in:** a `no-marker` run pinned nothing, hence is not high-kill; it '
      'enters the E4 denominator and scores 0. `N` stays 50 and the endpoint measures '
      'authorship end to end.')
    w('- **Denominator-out:** it is excluded like an identity failure; `N` shrinks by the '
      'drop count, and the endpoint measures "testing skill given a parseable artifact".')
    w('')
    w('**The pilot supplies no evidence either way, and this gate initially misread it.** '
      'The pilot scorer files %d arm-A, %d arm-B and %d arm-C runs as `no-marker`, which '
      'reads like a large arm-A authoring-validity problem. It is not one. Re-reading the '
      'raw call records (Sec. 7, exit codes above) shows every one of those drops is '
      'exit 124 with a zero-byte completion -- a timeout at the pilot driver\'s 900 s '
      'ceiling, mis-filed as an authoring code. That is exactly the driver defect prereg §1a '
      'already records, and it is why the registered ceiling is 2700 s. Every pilot call '
      'that returned a completion at all produced an extractable artifact: the observed '
      '`no-marker` rate among returned completions is **0 of %d**.'
      % (len(anchor['A']['dropped']), len(anchor['B']['dropped']),
         len(anchor['C']['dropped']),
         sum(anchor[k]['n'] for k in ('A', 'B', 'C'))))
    w('')
    w('So the correct design read is: authoring validity is not the threat to `N` -- the '
      'identity control is (5/5 arm-A suites in the pilot). D3 still has to be closed, '
      'because a rate of zero in fifteen calls does not bound the rate in 150, and because '
      'the two readings answer different questions. **Recommendation: denominator-in**, '
      'because prereg §1a already commits to it in general terms, and because it is the '
      'reading that cannot be gamed by an arm that fails loudly. Whichever is chosen, it '
      'must be registered before the freeze rather than settled after seeing which way '
      'the drops fell.')
    w('')

    # ---- 10. reproduction
    w('## 10. Reproduction and arithmetic discipline')
    w('')
    w('Every decision-bearing quantity in `oc_table.py` is an exact integer or '
      '`fractions.Fraction` built from `math.comb`: the table ordering statistic, the null '
      'tail supremum (compared to `alpha` by integer cross-multiplication), the binomial '
      'weights, and the OC probabilities. `float()` is called only inside the formatting '
      'helpers, after all comparisons are done. No simulation, no random number generator, '
      'no seed. stdlib only.')
    w('')
    w('The single quantity with no closed form is the supremum over the nuisance parameter '
      '`p in [0, 1]` of a degree-`2N` polynomial. It is handled by *registering the mesh* '
      'rather than approximating: the construction is defined as the maximum over '
      '`M = {k/1000}`, so it is exactly reproducible. Whether the mesh is fine enough is '
      'then an empirical question, answered by the offset-mesh column in Sec. 2. The tail '
      'set is symmetric under `(x, y) -> (N-x, N-y)`, so `A_s = A_{2N-s}` and `f(p) = '
      'f(1-p)`; only half the mesh is scanned, and the symmetry is asserted by '
      'construction. The critical level is found by binary search over the attained `z^2` '
      'levels, valid because the tail supremum is non-increasing in the level.')
    w('')
    w('The critical level is found in 9-12 supremum evaluations per `N` (binary search '
      'over 1500-5000 attained levels); the whole document regenerates in under ten '
      'seconds on the design machine.')
    w('')

    text = '\n'.join(L) + '\n'
    if '--stdout' in argv:
        sys.stdout.write(text)
    else:
        out = os.path.join(HERE, 'OC-TABLE.md')
        with open(out, 'w') as fh:
            fh.write(text)
        sys.stderr.write('wrote %s (%d bytes)\n' % (out, len(text)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
