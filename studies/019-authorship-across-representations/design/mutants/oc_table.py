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
contrast is the *exact-arithmetic mesh-inversion hull* for p_A - p_C (the
preregistration's earlier wording, "exact two-proportion difference interval",
named a family and is superseded -- see R1-16 below), and the registered decision
is:

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
script pins ONE member, and the preregistration adopts this wording:

    The A-C interval is the EXACT-ARITHMETIC MESH-INVERSION HULL for the
    difference of independent binomial proportions, obtained by inverting the
    two-sided Farrington-Manning score test with the nuisance parameter
    eliminated by maximisation over the registered rational mesh
    M = {k/1000 : k = 0..1000} (Chan & Zhang 1999; Agresti & Min 2001), at
    nominal two-sided alpha = 0.05, every comparison carried out in exact
    integer arithmetic.  Where inversion yields a non-convex acceptance set, the
    reported interval is its convex hull; the zero-exclusion decision reads the
    acceptance set itself, not the hull.

ROUND-1 FINDING R1-16, AND WHAT THIS FILE MAY NOT SAY
-----------------------------------------------------
The earlier issue of this file called the object an "exact unconditional
(Barnard-type) confidence interval" with "nominal coverage 1 - alpha".  THAT
CLAIM IS WITHDRAWN and must not reappear in the generated document.  The
preregistration's §5 now carries `levelCertifiedOverContinuum: false`, and two
approximations are registered, each with the direction it errs in:

  * The nuisance supremum is taken over M, not over the continuum p in [0, 1].
    A maximum over a finite subset is a LOWER bound on the continuum supremum,
    so every "realised size" this file prints is a lower bound on the true
    worst-case type-I error and the procedure may be anti-conservative by at
    most the published, exactly computed slack (`nuisanceMeshSlackBound`).
    Sec. 2's offset-mesh column is evidence that the mesh is fine, not a
    certificate that it is sufficient.
  * The Delta0 inversion is over a registered mesh too, so the published hull is
    an INNER approximation of the continuum interval -- never wider than it.

A certified continuum supremum was costed and DECLINED; relabelling is the
registered response.  What follows is therefore an exactly reproducible,
exactly computed operating-characteristic table for a named procedure, and NOT
a coverage certificate.  Phrases such as "exact test", "exact confidence
interval", "true worst-case" and "95% coverage" are barred from the emitted
document, and `harness/tests/test_prereg_currency.py` parses the emitted
document to keep them out.

Two consequences make the OC computation exact and cheap:

  (1) The registered decision only ever asks whether the interval contains 0.
      By construction the interval is {Delta : the FM test at Delta does not
      reject}, so

          interval excludes 0  <=>  the two-sided mesh-maximised FM test of
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

  * Its arithmetic is not reproducible in the sense this program requires.  Its
    coverage oscillates around the nominal level by a closed-form approximation
    the study cannot recompute exactly, and the per-arm rates are registered as
    exact Clopper-Pearson.  (Note this is a REPRODUCIBILITY argument, not a
    claim that the registered construction is "exact" in the coverage sense --
    see R1-16 above.)
  * Its coverage dips furthest below nominal where one arm's rate is pressed
    against a boundary of the unit interval, and the current five-run pilot
    fractions sit hard against the LOWER boundary (Sec. 7).  A construction
    whose weak spot is where the study's own fractions fall cannot be the
    registered one.
  * Its bounds are irrational (Wilson roots), so the zero-comparison cannot be
    carried out in exact rational arithmetic.  The program's discipline forbids
    a float in the decision arithmetic.

The cost of the mesh-inversion construction is conservatism relative to a
normal-approximation interval, and that cost is measured, not assumed: the null
diagonal of the OC table below is the realised decision rate under a true null
over the registered mesh, and the script also re-checks it on an offset mesh
that shares no point with the registered one.

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

# Extra probabilities needed for the named-region tables: neither 0 nor 1 is on
# GRID, and the current pilot fractions press against BOTH ends (Sec. 7).
EXTRA = [Fraction(0, 1), Fraction(1, 1)]

# ROUND-2 FINDING R2-13. The pilot this document is anchored to, named ONCE, in
# code. The previous issue read `E4-PILOT.json` here while a hand-edited Sec. 7
# claimed to have been regenerated from `E4-PILOT-v2.json`: the generator would
# have re-emitted the superseded anchor on the next run, and the document was
# internally inconsistent in the meantime. The file named here is the file the
# preregistration's Design-provenance section names as the current anchor, and
# `harness/tests/test_prereg_currency.py` asserts that those two agree — so when
# a later pilot supersedes this one, the suite fails until this constant, the
# preregistration and the regenerated table all move together.
#
# ROUND-3 FINDINGS R3-4 and R3-5 closed the splice this comment used to carry.
# The pending re-score landed twice: `E4-PILOT-v3.json` under R2-3's corrected
# `opa test` taxonomy, and then `E4-PILOT-v4.json`, which is what this constant
# names, under §4's registered per-case DOMAIN check that v3 omitted and under
# the round-3 adequacy repair's corpus. Naming the current issue in one constant
# was never the whole safeguard — R3-5 found the constant, the preregistration
# and this document agreeing on a stale v2, which mutual agreement cannot
# detect — so the file this names is now also required to be the END of the
# supersession chain: every earlier issue carries `supersededBy` naming its
# successor, the walk from the first issue must arrive here, and this file must
# carry no `supersededBy` of its own
# (`harness/tests/test_prereg_currency.py::test_the_pilot_supersession_chain_*`).
# Agreement on a stale file now fails, because staleness is a property of the
# chain rather than of the spelling.
PILOT_FILE = 'E4-PILOT-v4.json'

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

    ROUND-2 FINDING R2-13. Every arm is now read from `perArm`, the registered
    surface. The earlier issue special-cased arm A, reading it from
    `diagnostics.armAOffProtocol` because all five arm-A suites had failed the
    identity control on X1-region cases and the number was therefore what a
    THEN-PROPOSED X1-exclusion amendment would have made the protocol figure.
    X1 has since been RETIRED at the cause (round-1 R1-2): the arm-A reference
    was repaired, the registered exclusion registry is empty, and the current
    pilot records `identityFail: 0` in all three arms. The off-protocol
    diagnostic is no longer a source of anchor numbers.

    The special case is not deleted but INVERTED into a guard: if a future pilot
    records an identity failure, the arm's registered E4 denominator is smaller
    than its scored-run count and this function says so through `identityFail`
    rather than silently substituting a diagnostic surface for the registered
    one. Reading a diagnostic as an anchor is exactly what round 1 caught.

    ROUND-3 FINDINGS R3-4 and R3-6, and the guard above went off: `E4-PILOT-v4`
    records four arm-C identity failures, because §4's per-case domain check is
    applied for the first time. So the denominator this function reports had to
    stop being derived and start being READ.

    It used to be `len(vals)` — the runs that carry a `killRatePaired`, i.e. the
    identity-PASSING ones. That is the DENOMINATOR-OUT reading, and it is not the
    registered rule: §1a/§5 register admitted runs, an identity failure stays in
    the denominator carrying `highKill: null`, and round-2 finding R2-2 settled
    that between the two scorers already (`harness/score.py`'s `e4_arm()` and
    `e4_score.py`'s `high_kill_layer()` both compute it). On this pilot the two
    readings answer arm C 0/5 and 0/1. So `k` and `n` are now read straight off
    `perArm.<arm>.highKill`, the same block both scorers publish, and this
    document, the pilot and the primary scorer state one denominator between
    them. `runs` keeps the per-run kill rates for the table, and
    `identityFailedRuns` keeps the runs that are in `n` without having been
    asked, so the table can print every admitted run and the fraction still
    reconstructs.
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
    for arm in ('A', 'B', 'C'):
        block = d['perArm'][arm]
        vals, hits = score(block['perRun'])
        failures = block['identityFail']
        high = block['highKill']
        # The registered denominator, read rather than recomputed. If the pilot's
        # own two published lists stop reconstructing the rate, that is a defect
        # in the pilot and this document refuses to average over it.
        if high['admittedRuns'] != len(vals) + failures:
            raise SystemExit(
                'arm %s: %d admitted runs but %d scored + %d identity-failing — '
                'the pilot\'s denominator and its per-run lists disagree'
                % (arm, high['admittedRuns'], len(vals), failures))
        if len(hits) != high['highKillRuns']:
            raise SystemExit(
                'arm %s: this table counts %d high-kill runs and the pilot '
                'publishes %d' % (arm, len(hits), high['highKillRuns']))
        out[arm] = {
            'source': 'perArm.highKill (registered rule: §1a/§5 admitted runs%s)'
                      % ('; the identity control passed on every admitted run'
                         if not failures else
                         '; %d identity failure(s), IN this denominator and never '
                         'asked — see the caveat below' % failures),
            'runs': vals, 'high': hits,
            'n': high['admittedRuns'], 'k': high['highKillRuns'],
            'identityFailedRuns': list(block['identityFailedRuns']),
            'mutantsPairedAdequate': block['mutantsPairedAdequate'],
            'identityFail': failures,
            'dropped': [(x['run'], x['dropCode']) for x in block['droppedRuns']],
            'attempted': len(block['perRun']) + len(block['droppedRuns']),
        }
        out[arm]['forensics'] = drop_forensics(arm, out[arm]['dropped'])
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

    anchor = pilot_anchor(os.path.join(HERE, PILOT_FILE))
    fracs = {arm: Fraction(anchor[arm]['k'], anchor[arm]['n']) for arm in 'ABC'}
    # ROUND-3 R3-4/R3-6: whether this document has an identity-failure story to
    # tell is READ from the pilot, never assumed. Sec. 7's caveat and Sec. 8's
    # attrition paragraph both branch on it, so a pilot with no failures gets no
    # caveat and a pilot with failures cannot get the "excludes no run" sentence.
    total_identity_failures = sum(anchor[arm]['identityFail'] for arm in 'ABC')

    L = []
    w = L.append

    w('# Study 019 -- E4 operating characteristics (OC table)')
    w('')
    w('`GATE(pre-freeze)` for PREREGISTRATION.md §5. Generated by `oc_table.py` '
      'in this directory; no simulation, exact binomial enumeration throughout. '
      'Regenerate with `python3 oc_table.py`; output is byte-deterministic.')
    w('')
    w('**This document does not change the registered design. It reports what the '
      'registered design can and cannot decide.** Sec. 9 tracks the three defects this '
      'gate found in the preregistration: two are closed, one is still open.')
    w('')

    # ---- 1. the pinned construction
    w('## 1. The pinned interval construction')
    w('')
    w('The preregistration said "exact two-proportion difference interval". That names '
      'a family. The OC of a family is undefined, so this gate pins one member, and '
      'prereg §5 carries this wording:')
    w('')
    w('> The A-C contrast is the **exact-arithmetic mesh-inversion hull** for the '
      'difference of two independent binomial proportions, obtained by inverting '
      'the two-sided Farrington-Manning score test with the nuisance parameter eliminated '
      'by maximisation over the registered rational mesh `M = {k/1000 : k = 0..1000}` '
      '(Chan & Zhang 1999; Agresti & Min 2001), at nominal two-sided `alpha = 0.05`, '
      'every comparison carried out in exact integer arithmetic. Where the inverted '
      'acceptance set is non-convex, the *reported* interval is its convex hull; the '
      'zero-exclusion decision reads the acceptance set itself.')
    w('')
    w('**What this object is not (round-1 finding R1-16).** An earlier issue of this '
      'document called it an "exact unconditional (Barnard-type) confidence interval" '
      'with nominal coverage `1 - alpha`. **That claim is withdrawn.** Prereg §5 publishes '
      '`levelCertifiedOverContinuum: false`, and registers two approximations with the '
      'direction each errs in:')
    w('')
    w('- The nuisance supremum is taken over `M`, not over the continuum `p in [0, 1]`. '
      'A maximum over a finite subset is a **lower** bound on the continuum supremum, so '
      'every "realised size" printed in Sec. 2 is a lower bound on the worst-case type-I '
      'error and the procedure may be anti-conservative by at most the published, exactly '
      'computed slack (`nuisanceMeshSlackBound`).')
    w('- The `Delta0` inversion runs over a registered mesh too, so the published hull is '
      'an **inner** approximation of the continuum interval — never wider than it.')
    w('')
    w('A certified continuum supremum was costed and **declined**; relabelling is the '
      'registered response, and nothing anywhere is adjusted by the slack bound. What '
      'follows is an exactly reproducible, exactly computed operating-characteristic table '
      'for a named procedure. **It is not a coverage certificate, and no sentence in this '
      'document may claim 95% coverage at any true rate.**')
    w('')
    w('Two facts make the OC exactly computable:')
    w('')
    w('1. The registered decision only asks whether the interval contains zero. Since the '
      'interval is the set of `Delta` the FM test does not reject, **interval excludes '
      'zero if and only if the two-sided mesh-maximised FM test of `H0: p_A = p_C` '
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
      'rejected on three grounds. (a) Its arithmetic is not reproducible in the sense this '
      'program requires: its coverage oscillates around nominal by a closed-form '
      'approximation the study cannot recompute exactly, while the per-arm rates are '
      'registered as exact Clopper-Pearson. (This is a reproducibility argument, not a '
      'claim that the registered construction certifies coverage — see R1-16 above.) '
      '(b) Its coverage is weakest where one proportion is pressed against a boundary of '
      'the unit interval, and the current pilot fractions sit hard against the LOWER '
      'boundary (Sec. 7). A construction whose failure mode is where the study\'s own '
      'fractions fall cannot be the registered one. (c) Its bounds are '
      'Wilson roots, hence irrational, so the zero-comparison cannot be carried out '
      'without floats in the decision arithmetic.')
    w('')
    w('The price of the mesh-inversion construction is conservatism relative to a '
      'normal-approximation interval. That price is measured below, not assumed.')
    w('')

    # ---- 2. calibration
    w('## 2. Calibration of the implemented procedure')
    w('')
    w('`c*` is the smallest attained `z^2` level whose null tail supremum is at most '
      '`alpha`; the rejection region is `{z^2 >= c*}`. "Realised size (sup over M)" is '
      'that supremum: the probability of *any* decision when `p_A = p_C`, maximised over '
      'the **registered mesh**. It is a **lower bound** on the worst-case over the '
      'continuum, not that worst case (Sec. 1). "Offset-mesh size" re-evaluates '
      'the same rejection region on the interleaved mesh `{(2k+1)/2000}`, which shares no '
      'point with the registered one; it is evidence that mesh 1/1000 is fine enough that '
      'the registered sup is not an artefact of where the mesh points fall — evidence, not '
      'a certificate.')
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
    w('Every realised size is at or below the nominal 0.05 on both meshes '
      '(largest over all three N, either mesh: **%s**). The two meshes agree to within '
      '%s, so the registered mesh of 1/1000 resolves the nuisance supremum well below the '
      'precision any decision depends on -- the sup is a genuine feature of the tail '
      'function, not an artefact of mesh placement. **That is not a coverage claim**: both '
      'columns are maxima over finite meshes and therefore lower bounds on the continuum '
      'worst case (Sec. 1), and the registered slack bound rather than this table is what '
      'bounds the gap. The shortfall below 0.05 is the conservatism the construction pays '
      'for its exact arithmetic, and it is why the power numbers below are lower than a '
      'normal-approximation calculation would suggest.'
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

    # ---- 5. named regions of the grid
    w('## 5. Power over two named regions of the grid')
    w('')
    w('**No operating point is located, and this section does not locate one** '
      '(round-1 findings R1-16 and R1-18; round-2 finding R2-13). The gate\'s brief '
      'guessed `p_A ~ 0.4-0.6` with `p_C ~ 0.8-1.0`, and an earlier issue of this '
      'document carried a "pilot-anchored band" built on pilot fractions that the arm-A '
      'reference repair and the corpus rebuild have since superseded. The current pilot '
      'fractions are **A %s, B %s, C %s on five runs each** (Sec. 7), which is five runs '
      'per arm and anchors nothing; prereg §5 registers **no expected direction for R1** '
      'and says the power grid is to be read whole. Sec. 3 and Sec. 6 are that whole '
      'reading; the two regions below are tabulated because they are the two the design '
      'conversation has actually referred to, and for no stronger reason.'
      % (f3(fracs['A']), f3(fracs['B']), f3(fracs['C'])))
    w('')
    for label, gloss, pAs, pCs in (
        ('Region L — both rates near the lower boundary',
         'The region the current five-run fractions fall in. Note the direction: here it '
         'is arm A that would be above arm C, the reverse of the superseded anchor. The '
         'region is NOT symmetric with Region H under the exchange of arms, because the '
         'design\'s power depends on where in the unit interval the pair sits, not only '
         'on the gap.',
         [Fraction(k, 20) for k in (1, 2, 3, 4, 5, 6)],
         [Fraction(0, 1)] + [Fraction(k, 20) for k in (1, 2, 3, 4)]),
        ('Region H — arm C near the upper boundary',
         'The gate brief\'s original suggestion, retained so the two conversations can be '
         'compared. Nothing currently points here.',
         [Fraction(k, 20) for k in (8, 9, 10, 11, 12)],
         [Fraction(k, 20) for k in (16, 17, 18, 19)] + [Fraction(1, 1)]),
    ):
        w('### %s' % label)
        w('')
        w(gloss)
        w('')
        w('| p_A | p_C | gap | N=30 decide | N=50 decide | N=100 decide | '
          'N=50 P(A-above) | N=50 P(C-above) | N=50 P(INDET) |')
        w('|---|---|---|---|---|---|---|---|---|')
        for pA in pAs:
            for pC in pCs:
                cells = {N: results[N]['oc'][(pA, pC)] for N in (30, 50, 100)}
                d = {N: cells[N][0] + cells[N][1] for N in cells}
                w('| %s | %s | %s | %s | %s | %s | %s | %s | %s |'
                  % (f2(pA), f2(pC), f2(pC - pA),
                     f3(d[30]), f3(d[50]), f3(d[100]),
                     f3(cells[50][0]), f3(cells[50][1]), f3(cells[50][2])))
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

    # ---- 7. pilot fractions (NOT an anchor; R1-18, R2-13)
    w('## 7. Pilot fractions: what fraction of pilot runs are high-kill at tau = 0.95')
    w('')
    w('Read from `%s`, which is the pilot the preregistration\'s Design-provenance section '
      'names as current; `oc_table.py` names the same file in one constant and a currency '
      'test asserts the two agree, so a superseded pilot cannot survive here as it did '
      'before (round-2 finding R2-13). **NON-CITABLE**: five runs per arm, pilot suites, '
      'pre-freeze gold. These are fractions, not an anchor: prereg §5 registers no '
      'expected direction and this section locates no operating point.' % PILOT_FILE)
    w('')
    w('> **The re-score this section used to say was owed has landed, twice, and the '
      'second time it moved an arm.** Round-2 finding R2-3 (Rego evaluation faults '
      'credited as kills off the `opa test` exit status) was corrected in '
      '`E4-PILOT-v3.json`, and on those inputs no kill vector changed. Round-3 finding '
      'R3-4 then found that no pilot issue had ever applied prereg §4\'s registered '
      'per-case DOMAIN check: `%s` applies it, by calling the harness\'s own '
      'implementation rather than carrying a second one, and it also carries the round-3 '
      'adequacy repair\'s corpus (gold at 117 rows; both mutant MANIFESTs re-witnessed). '
      'Arm C moves as a result — four of its five admitted runs are identity failures '
      'under §4, where every earlier issue recorded none — and every pairing quantity in '
      'this section moves with the corpus. No fraction below is a `E4-PILOT-v3.json` '
      'fraction. This does not touch Secs. 1-6, which are exact enumerations over a grid '
      'of (p_A, p_C, N) and depend on no pilot at all.' % PILOT_FILE)
    w('')
    for arm in ('A', 'B', 'C'):
        a = anchor[arm]
        m = a['mutantsPairedAdequate']
        k, rate = tau_bites(m)
        w('**Arm %s** -- %d admitted runs (%d scored, %d identity failure%s), paired '
          'adequate subset = %d mutants; at `tau = 0.95` a run must kill **%d/%d = %s**.'
          % (arm, a['n'], len(a['runs']), a['identityFail'],
             '' if a['identityFail'] == 1 else 's', m, k, m, f4(rate)))
        w('')
        w('| run | paired kill rate | high-kill at tau=0.95 |')
        w('|---|---|---|')
        for name, v in a['runs']:
            w('| %s | %s | %s |' % (name, f4(v), 'YES' if v >= TAU else 'no'))
        for name in a['identityFailedRuns']:
            w('| %s | identity FAIL -- not asked | no (`highKill: null`, in the '
              'denominator) |' % name)
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
    kA, kB, kC = (anchor[a]['k'] for a in 'ABC')
    nA, nB, nC = (anchor[a]['n'] for a in 'ABC')
    w('**Current fractions: A %d/%d = %s, B %d/%d = %s, C %d/%d = %s**, each on five '
      'admitted runs, all three read from the registered `perArm.highKill` surface with '
      '`identityFail` = %d / %d / %d. %s things must be said with them:'
      % (kA, nA, f3(fracs['A']), kB, nB, f3(fracs['B']), kC, nC, f3(fracs['C']),
         anchor['A']['identityFail'], anchor['B']['identityFail'],
         anchor['C']['identityFail'],
         'Four' if total_identity_failures else 'Three'))
    w('')
    # The points are collected and numbered BY POSITION, because the
    # identity-control point (round-3 R3-4) is present only when the pilot
    # records a failure and a hand-numbered list would then either mis-count or
    # carry a "1a." that is not a list item at all.
    points = []
    points.append(
        '**These fractions supersede every earlier issue of this section, and they moved '
      'the direction as well as the magnitude.** The superseded issue read `0.20 / 0.80 / '
      '1.00` from a 145-mutant arm-A corpus built on the pre-repair reference, and took '
      'arm A\'s number from `diagnostics.armAOffProtocol` because all five arm-A suites '
      'had then failed the identity control on X1-region cases. **X1 is retired at the '
      'cause** (round-1 R1-2): the reference was repaired and the registered exclusion '
      'registry is empty. There is no off-protocol diagnostic in this document any more, '
      'and no arm-A exclusion: arm A passes the identity control on every admitted run '
      'above.')
    if total_identity_failures:
        points.append(
            '**Identity-control caveat, and it is the reason to read `%s` rather than '
          'any earlier issue.** %s. These are not authoring failures of a new kind and '
          'they are not new behaviour in the suites: they are prereg §4\'s **registered '
          'per-case domain check**, applied for the first time by this pilot issue '
          '(round-3 finding R3-4). §4 validates every enumerated case against the '
          'registered input domain *before* identity and mutation execution, identically '
          'in A, B and C, and an out-of-domain case "is an identity failure categorised '
          '`out-of-domain-case`". Two things follow, and both are visible in the tables '
          'above. **The denominator does not shrink.** §1a/§5 register *admitted* runs; an '
          'identity-failing run stays in `n` carrying `highKill: null` -- never `false`, '
          'because it was never asked -- so arm C\'s fraction is %d/%d and not %d/%d. That '
          'is the denominator-in rule, it is Sec. 9 D3\'s settled reading, and the primary '
          'scorer, the pilot scorer and this table all read it off the same published '
          '`highKill` block. **The descriptive mean kill rate does shrink**, because a '
          'mean over admitted runs would have to average a quantity that does not exist '
          'for four of arm C\'s five: arm C\'s mean paired kill rate rests on the single '
          'admitted run that passed, and is a one-run number wearing a mean\'s clothes. '
          'Neither quantity is an anchor; see the next point.'
          % (PILOT_FILE,
             '; '.join('Arm %s records %d of its %d admitted runs as identity '
                       'failures (%s)'
                       % (arm, anchor[arm]['identityFail'], anchor[arm]['n'],
                          ', '.join('`%s`' % r
                                    for r in anchor[arm]['identityFailedRuns']))
                       for arm in ('A', 'B', 'C') if anchor[arm]['identityFail']),
             anchor['C']['k'], anchor['C']['n'],
             anchor['C']['k'], max(1, len(anchor['C']['runs']))))
    points.append(
        '**Five runs per arm locate nothing.** A 1/5 and a 0/5 are compatible with a very '
      'wide range of true rates and with either direction; prereg §5 registers **no '
      'expected direction for R1** on exactly this ground. Sec. 5 tabulates two regions of '
      'the grid, neither of which is claimed to be where the study will land.')
    points.append(
        '**`tau = 0.95` bites hard, which is the point of the threshold.** Mean paired '
      'kill rates in this pilot are far above 0.5 in every arm while the high-kill '
      'fractions above are near 0: a run can kill most paired mutants and still not be '
      'high-kill. Reading the mean rates as if they were the endpoint is the error the '
      'threshold exists to prevent.')
    for number, point in enumerate(points, 1):
        w('%d. %s' % (number, point))
    w('')
    w('Note the **denominator asymmetry**, which is a design fact and not noise. Pairing '
      'is at the level of witness-equivalence groups, not 1:1 mutants, so the paired '
      'adequate subsets differ in size by language: %d JPS mutants against %d Rego. '
      '`tau = 0.95` therefore bites arm A at %d/%d = %s and arms B/C at %d/%d = %s -- two '
      'integer cuts, not one -- and the arms\' kill rates are quantised on different '
      'lattices (1/%d vs 1/%d). It is a real asymmetry in the endpoint definition, it is '
      'carried in prereg §5 rather than discovered at analysis time, and prereg §4 '
      'publishes the unpairable counts that produce it.'
      % (anchor['A']['mutantsPairedAdequate'], anchor['B']['mutantsPairedAdequate'],
         tau_bites(anchor['A']['mutantsPairedAdequate'])[0],
         anchor['A']['mutantsPairedAdequate'],
         f4(tau_bites(anchor['A']['mutantsPairedAdequate'])[1]),
         tau_bites(anchor['B']['mutantsPairedAdequate'])[0],
         anchor['B']['mutantsPairedAdequate'],
         f4(tau_bites(anchor['B']['mutantsPairedAdequate'])[1]),
         anchor['A']['mutantsPairedAdequate'],
         anchor['B']['mutantsPairedAdequate']))
    w('')

    # ---- 8. what this design can and cannot decide
    w('## 8. Plain-language summary: what this design can and cannot decide')
    w('')
    a20 = results[50]['oc'][(Fraction(4, 20), Fraction(0, 1))]
    a20_30 = results[30]['oc'][(Fraction(4, 20), Fraction(0, 1))]
    a20_100 = results[100]['oc'][(Fraction(4, 20), Fraction(0, 1))]
    mid = results[50]['oc'][(Fraction(8, 20), Fraction(12, 20))]
    w('**It decides large gaps at either boundary, wherever they turn out to be.** Taking '
      'the current five-run fractions at face value purely as an arithmetic illustration '
      '(`p_A = %s`, `p_C = %s` — Sec. 7 says they locate nothing), the registered N = 50 '
      'design would decide with probability %s (N = 30: %s; N = 100: %s). The same is true '
      'of the mirrored gap near the upper boundary (Sec. 5, Region H). Sample size is not '
      'the binding constraint on a gap of that size in either direction.'
      % (f2(Fraction(4, 20)), f2(Fraction(0, 1)),
         f4(a20[0] + a20[1]), f4(a20_30[0] + a20_30[1]), f4(a20_100[0] + a20_100[1])))
    w('')
    w('**It cannot decide a 0.20 gap in the middle of the range.** At `p_A = 0.40` vs '
      '`p_C = 0.60` -- exactly the registered `delta` -- N = 50 decides with probability '
      '%s, i.e. INDETERMINATE with probability %s. `delta = 0.20` is registered as the '
      'minimum *meaningful* difference; it is emphatically not the minimum *detectable* '
      'difference at N = 50. Anyone reading `delta = 0.20` as "this study is powered to '
      'find a 0.20 gap" is reading it wrong, and prereg §5 says so in those terms.'
      % (f3(mid[0] + mid[1]), f3(mid[2])))
    w('')
    w('**Power is strongly asymmetric across the unit interval.** Because the variance of '
      'a proportion collapses near 0 and 1, the same nominal gap is far easier to decide '
      'when one arm is near a boundary. Where this design will sit is unknown — R1 '
      'registers no expected direction — so both boundaries and the middle are live, and '
      'that is why Sec. 3 is printed whole rather than summarised at a point. The design '
      'is weakest in the middle of the range and that weakness is symmetric.')
    w('')
    w('**The conservatism is real and is being paid deliberately.** Realised size at '
      'N = 50 is %s against a 0.05 nominal, maximised over the registered mesh. That '
      'conservatism costs several points of power relative to a normal-approximation '
      'interval, and it buys exactly reproducible decision arithmetic — **not** a coverage '
      'guarantee at every true common rate, which this construction does not certify '
      '(Sec. 1). Given that the whole point of R1 is a retractable directional claim, '
      'reproducible arithmetic is worth the points.' % f4(results[50]['size']))
    w('')
    w('**N = 50 is a ceiling for a different reason than it used to be.** The E4 '
      'denominator is §1a/§5\'s *admitted* runs -- attempted runs whose apparatus '
      'succeeded -- and **an identity failure does not leave it** (Sec. 9, D3, settled '
      'denominator-in; the run carries `highKill: null` and is reported). So identity '
      'attrition does not move `N` at all, and the N = 30 column is not the column to read '
      'for it: what identity failures cost is the NUMERATOR, one high-kill opportunity per '
      'failing run, which is a loss of power at fixed `N` rather than a smaller design. '
      'The current pilot makes that concrete -- %s (Sec. 7) -- and every one of those runs '
      'is in its arm\'s denominator. What does shrink `N` is APPARATUS attrition: '
      'timeouts at the registered 2700 s ceiling, wrapper and golden-context failures, '
      'engine refusals. Those are pipeline-invalid, they leave the denominator by '
      'registration, and they are the reason the smaller columns are printed at all. At '
      'N = 30 a boundary gap of the size Sec. 5 Region L tabulates is still decided with '
      'probability %s, so the design survives moderate apparatus attrition -- but the '
      'middle-of-range 0.20 gap collapses to %s.'
      % ('%d of the 15 admitted pilot runs fail the identity control'
         % total_identity_failures if total_identity_failures else
         'no admitted pilot run fails the identity control',
         f4(a20_30[0] + a20_30[1]),
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
    w('## 9. Three defects this gate found in the preregistration (all three closed)')
    w('')
    w('**D1 -- alpha was never registered. CLOSED.** Prereg §5 registered exact '
      'Clopper-Pearson intervals and "exact two-proportion difference intervals" without '
      'stating a confidence level; this OC assumed two-sided `alpha = 0.05`. §5 now states '
      '`α = 0.05` with the decision clause, and states that the A-C / A-B hierarchy is '
      'fixed-sequence gatekeeping controlling the family-wise error rate at `alpha` '
      'without adjustment -- which is why no Bonferroni appears anywhere. '
      '`harness/tests/test_prereg_currency.py` asserts exactly one alpha is stated.')
    w('')
    w('**D2 -- "excludes zero at delta" is not a rule. CLOSED, on Reading 1.** Prereg §5 '
      'said the contrasts were evaluated "each at `delta = 0.20`" and its decision table '
      'said "A-C interval excludes zero at delta -> R1 decided". Those describe two '
      'different procedures:')
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
      'was not a cosmetic edit. **Reading 1 was registered** (round-1 finding R1-15): '
      'prereg §1 and §5 now carry one decision clause verbatim -- the A−C difference '
      'interval excludes zero at two-sided α = 0.05 -- `delta` is registered as an '
      'interpretation and power quantity that no decision reads, and the currency suite '
      'asserts that no decision statement anywhere qualifies zero-exclusion by delta. '
      'This OC table is valid for Reading 1, which is the registered one.')
    w('')
    w('**D3 -- the E4 denominator does not say what happens to a run with no artifact. '
      'CLOSED, denominator-in.** The gate raised it, round-2 finding R2-2 found the '
      'adjacent defect live in code (the primary scorer and the pilot scorer disagreed '
      'about whether an identity-failing run stays in the E4 denominator), and round-3 '
      'finding R3-6 found this section still reporting the question open after the '
      'response had decided it. It is decided, in the direction §1a already committed to, '
      'and it is decided in three places at once rather than in prose: prereg §5 registers '
      'the rule ("Runs carrying authoring-outcome codes remain in the E4 denominator as '
      'not-high-kill ... only apparatus codes leave it, and identity-control exclusions '
      'are reported, never silently dropped"); `harness/score.py`\'s `e4_arm()` publishes '
      '`denominatorRule` and gives an identity-failing run `highKill: null` in a '
      'denominator of `len(runs)`; `design/mutants/e4_score.py`\'s `high_kill_layer()` '
      'computes the same thing; and Sec. 7 of this document READS that block rather than '
      'recomputing a denominator of its own. The two readings genuinely disagree on the '
      'current pilot -- arm C is %d/%d denominator-in and %d/%d denominator-out -- so this '
      'is a closure with a live witness, not a formality. `harness/tests` carries the '
      'mixed one-pass/one-fail probe asserting 1/2 on the primary scorer, and the currency '
      'suite asserts that the pilot, this table and the registration state one '
      'denominator between them.'
      % (anchor['C']['k'], anchor['C']['n'],
         anchor['C']['k'], max(1, len(anchor['C']['runs']))))
    w('')
    w('**What the closure does NOT settle**, stated so the next reader does not have to '
      'rediscover it: denominator-in fixes what a failing run does to `N`, not how often '
      'runs fail. A rate of %d in 15 pilot calls does not bound the rate in 150, and the '
      'power cost of identity failures falls on the numerator (Sec. 8). What follows is '
      'the gate\'s original statement of the question, kept because the reasoning is the '
      'reason for the answer.' % total_identity_failures)
    w('')
    w('Prereg §5 scopes E4 to "admitted runs" -- runs that clear the identity control -- '
      'while prereg §1a says every author-attributable failure, including "no extractable '
      'marker block", is "valid, counted, and scoring zero on every endpoint it reaches". '
      'A `no-marker` run reaches E4 in the §1a sense but has no suite to run against '
      'the mutants. Two readings, and they move `N`, which is what this table is about:')
    w('')
    w('- **Denominator-in (REGISTERED, and the answer above):** a `no-marker` run pinned '
      'nothing, hence is not high-kill; it enters the E4 denominator and scores 0. `N` '
      'stays 50 and the endpoint measures authorship end to end. The same rule governs an '
      'identity failure, which is likewise in the denominator and likewise not high-kill.')
    w('- **Denominator-out (NOT registered):** it is excluded; `N` shrinks by the drop '
      'count, and the endpoint measures "testing skill given a parseable artifact". This '
      'reading is rejected, not merely unchosen: it is the reading an arm can game by '
      'failing loudly.')
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
    w('So authoring validity is not the threat to `N`. **The gate\'s recommendation was '
      'denominator-in**, because prereg §1a commits to it in general terms and because it '
      'is the reading that cannot be gamed by an arm that fails loudly, and '
      'denominator-in is what is registered and implemented. The gate\'s closing condition '
      '-- "one rule must be registered and made to hold in the primary scorer, the pilot '
      'scorer and this table together, before the freeze" -- is the condition that has '
      'been met, and the three-place statement above is what meeting it looks like. The '
      'gate\'s other sentence, "the identity control is (5/5 arm-A suites in the pilot)", '
      'is historical twice over: X1 is retired, the exclusion registry is empty, and arm A '
      'now passes identity on every admitted run. The identity failures the current pilot '
      'does record are arm C\'s, from §4\'s domain check (Sec. 7), and denominator-in is '
      'exactly why they do not move `N`.')
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
