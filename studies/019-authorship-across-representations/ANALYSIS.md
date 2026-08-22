# Analysis — Study 019, primary attempt (post-run; the preregistration governs)

**Attempt.** `results/primary-attempt-001`, the first invocation of the registered
governing command, run from the freeze commit
`51cae0225ea2e9e5679c8e496b39a62e93385278` under the pinned CPython 3.12.11 with
`--include-reviewer-set`; label **REGISTERED** (every freeze pin non-null, verified before
adjudication; `pipelineInvalid: false`). The batch: 150 of 150 registered slots present,
no shortfall declared, run over the registered multi-day window with three driver resumes,
all recorded in the ledger. This document is post-run analysis; the preregistration and
its pinned artifacts govern, and every number here is `RESULTS.json`'s.

## Verdicts

- **R1: inconclusive — control gate failed (`e1-floor`).** §5's decision table matched
  row 3 above every substantive row: the E1 floor (0.6 of admitted runs perfect against
  the 117-row gold suite) was breached in **all three arms** — A 0/38, B 8/37 (0.216),
  C 14/39 (0.359). Per the registered rule, **no contrast was computed, no interval, no
  direction**: "a direction computed and then withheld is a direction published," so none
  exists. R1 licenses nothing — not a JPS reading, not an OPA reading, not equivalence.
- **The sealed reviewer set (first execution, reported separately, moving nothing):**
  the cleanest signal of the attempt. Arm A's 34 identity-passing suites killed
  `rm-jps-03` **34/34** and killed `rm-jps-01` and `rm-jps-02` **0/34**; arms B and C
  killed `rm-rego-01` and `rm-rego-03` **universally** (26/26, 28/28) and `rm-rego-02`
  **never**. Three of the reviewer's six sealed mutants survive every authored test suite
  in their language — a registered, adversary-authored measurement of what run-authored
  suites do not pin, delivered exactly as designed.

## What the gate failure actually is

The E1 collapse is not one phenomenon; E3's registered taxonomy splits it:

- **Arm A failed by near-miss.** 346 row disagreements over 38×117 = 4,446 row
  evaluations — ≈ 7.8% row-level disagreement, ≈ 92% row accuracy — and **zero**
  ROW-ERRORs. At the registered all-117-rows bar, 92% row accuracy compounds to a
  per-run-perfect probability of roughly 0.92^117 ≈ 10⁻⁴: arm A's zero perfect runs are
  the strict bar amplifying a modest accuracy drop, not gross authoring failure. Its
  identity control still passed 34 of 36 admitted runs.
- **Arms B and C failed by fault as well as disagreement.** B: 1,579 disagreements plus
  **255 ROW-ERRORs** (runtime faults on gold inputs) ≈ 42% of row evaluations failing;
  C: 1,126 + 89 ≈ 27%. E2 corroborates: 7 unparseable artifacts and 4 `opa check`
  failures in B, 2 and 9 in C, against 2 no-marker blocks in A — authoring-validity
  failure classes the non-citable pilot never exhibited at all.

## The pilot/batch divergence (post-hoc, hypotheses labelled as such)

The calibration pilot (non-citable, 5 completed runs/arm) produced 15/15 perfect
artifacts on byte-identical prompts with the same pinned CLI and model name. The
registered batch produced 22 perfect in 114 admitted runs. That divergence is beyond
doubt; its cause is not adjudicable from retained bytes, and §2's own registration — *a
model name is not a digest* — bounds every hypothesis:

1. **Environment**: the pilot ran outside the registered isolation wrapper (operator
   HOME, user config); the batch ran inside it (fresh HOME, `env -i`,
   `--ignore-user-config`). The golden-context gate proves the batch's context was
   uniform; it cannot prove it was equivalent to the pilot's.
2. **Service-side drift**: six days separate pilot from batch behind the same pinned CLI
   digest and model name.
3. **Scale/sequence effects**: 150 sequential calls over a multi-day window with three
   resumes versus fifteen calls in an afternoon.

None of these is claimed; all are recorded. Discriminating them is future work the
program may or may not fund (§11).

## What this attempt does buy

Within its registered scope: the harness executed a REGISTERED attempt end to end —
every pin verified, the capabilities canary refused, engine execution clean, the
schedule matched, the population computed by the admission function alone, intervals
suppressed exactly where §5 forbids them, and the refusals published as refusals. E5's
census (descriptive, on its registered stimulus): arm A produced 28 distinct structural
encodings across 36 runs; B and C produced 9 across 30 each — the pack format's authors
spread over many more encodings than the Rego arms' converged ladder shape. No tradeoff
statement combining this with E4 is licensed (§9).

## Claims and non-claims

This attempt claims: the registered decision procedure reached row 3 and stopped;
authoring reliability in the registered environment fell far below the pilot's in all
three representations; three sealed reviewer mutants survive every authored suite. It
does not claim: any direction on R1; any component attribution within the bundled A−C
estimand; any cause for the pilot/batch divergence; anything about any representation's
merit for business judgments in general; that any policy or fact is true. Nothing in
this repository claims any JPS conformance. `CORRECTION-TARGETS.md`'s targets were
audited against this publication: none required correction, and `CORRECTION.md` records
that outcome affirmatively.
