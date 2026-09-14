# Analysis — Study 021 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command from
the freeze commit (`1255f7aa`, the squash-merge of PR #105) plus the single post-freeze pin
commit that `DEVIATIONS.md` names; CPython 3.12.11; the runtime the judgment-pack
release **v0.21.0** as published for linux/amd64 (`jpack` digest
`sha256:5e307176d22e350f6619b2f760fee843db115f2c9d7e4bb188168846e59d4f35`, verified against the
release's checksums); label `REGISTERED`, attempt id `f2284e59b2f2e5e5c368bcf4a5f1b74f`. Fully offline: the
runtime binary and the interpreter only, no model and no external component anywhere. Every
freeze pin, the runtime's digest and the whole-study manifest were held before the marker was
written; every ledger was rebuilt byte for byte under the pinned runtime and every signature
record reconstructed and compared before anything was aggregated. This document is post-run
analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **R1 (locked and holdout together, as registered)**: `R1 holds (REGISTERED)` — 131 registered
  cells, 131 adjudicated, **0 divergent**, 0 pipeline-invalid, every control gate green (G1: each
  unplanted pack mismatches no row on any of its 121 ledgers; G2: every defect instance a valid
  pack, none dropped, every cell against every ledger; G3: every random ledger deterministic in
  its seed).
- **The reviewer's holdout (first execution)**: 8/8 cells hold — six literal-ledger cells the
  reviewer registered as exact counts (a signature that must be carried, a threshold-free
  catch, an at-row, a mirror, a two-sided site) and two random-stratum catch intervals at
  n = 20, all landing where the reviewer wrote them.
- **The structural account**: all 29 cells registered *undetected* held (nothing the ledger
  cannot see was caught), all 24 cells registered as *necessarily masquerading* held (every
  caught replicate carried the line-moved signature), and both cells registered as carrying
  *no* signature held.

## What replayed history buys a draft — the catch

Pooling each defect class over its instances (the harness's per-instance curves, with exact
95% Clopper–Pearson intervals, are in the tables below):

| class | what was planted | literal ledger (count) | random, n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|---|
| D1 | a threshold moved | 3/4 | 0.24 | 0.43 | 0.51 | 0.63 |
| D2 | a comparison flipped across the line | 4/4 | 0.25 | 0.46 | 0.58 | 0.69 |
| D3 | a boundary flipped (≤ ↔ <) | 3/4 | 0.14 | 0.22 | 0.26 | 0.25 |
| D4 | a two-sided site altered | 4/4 | 0.57 | 0.71 | 0.77 | 0.80 |
| D5 | a rule's outcome swapped | 8/9 | 0.37 | 0.49 | 0.68 | 0.78 |
| D6 | a guard's evidence condition changed | 5/13 | 0.08 | 0.15 | 0.24 | 0.34 |
| D7 | a rule silenced or its outcome changed | 15/19 | 0.18 | 0.28 | 0.42 | 0.53 |
| D8 | an exception removed | 3/3 | 0.87 | 0.91 | 1.00 | 1.00 |
| D9 | the fallback changed | 1/3 | 0.11 | 0.33 | 0.56 | 0.79 |

Three readings, each one the registration said in advance and each confirmed cell by cell:

- **A ledger drawn at the policy's lines catches most of what is planted at them.** The
  literal ledger — one case at each literal the pack draws, on each side of it — caught 46 of
  the 63 literal cells; what it missed is exactly what the registration said no ledger of
  dispositions can see: a rule masked by an exception at the same literal (S1), a rule whose
  outcome is the fallback and that fires alone (S2), a boundary flip on a pointer no case sits
  exactly on. Every one of those 29 registered non-detections held, on both strata.
- **A ledger drawn at random over the domains catches by volume**, and the curves rise with n
  as registered — from a quarter to two thirds for a moved line, from a tenth to four fifths
  for a changed fallback — except where the defect lives on a set of measure zero: a boundary
  flip (D3) is caught only where the pointer's domain is small enough that a random draw
  lands on the line (`sanctions-screening`: 17/30 at n = 5 rising to 30/30 at n = 50) and all
  but never on the wide domains (`vendor-onboarding`'s two instances 0/30 at every n;
  `expense-approval`'s 0/30 at every n but 2/30 at n = 20), each as registered.
- **What no history catches** is the pack's account of itself where the dispositions agree
  either way: the masked guards and the fallback-valued rules above. The ledger is the pack's
  own word about the cases it saw; a defect that changes no disposition on any case leaves it
  unchanged, and the registration named each such site from the pack's text before the run.

## What the profile can and cannot tell — the masquerade

Among the caught replicates, the fraction whose profile carries the **line-moved signature**
(one pointer disagreeing, one-sided at some literal, every mismatched row placed):

| class | literal | random, n=5 | n=10 | n=20 | n=50 | threshold-free caught cells (n=50) |
|---|---|---|---|---|---|---|
| D1 moved line | 3/3 | 1.00 | 1.00 | 1.00 | 1.00 | 0 |
| D2 comparison flipped | 3/4 | 0.50 | 0.49 | 0.57 | 0.64 | 0 |
| D3 boundary flipped | 0/3 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| D4 two-sided site | 1/4 | 0.46 | 0.32 | 0.18 | 0.08 | 0 |
| D5 outcome swapped | 5/8 | 0.58 | 0.47 | 0.44 | 0.44 | 59 of 211 |
| D6 evidence guard | 3/5 | 0.62 | 0.56 | 0.52 | 0.46 | 71 of 132 |
| D7 rule silenced | 11/15 | 0.80 | 0.81 | 0.69 | 0.57 | 51 of 303 |
| D8 exception removed | 1/3 | 0.62 | 0.63 | 0.67 | 0.67 | 30 of 90 |
| D9 fallback changed | 0/1 | 0.90 | 0.80 | 0.76 | 0.73 | 19 of 71 |

- **A moved line always carries its signature** (D1: every caught replicate on every ledger),
  which is what the signature was built for, and **a boundary flip never does** (D3: the
  disagreeing rows sit *at* the literal, which the signature's one-sided condition excludes) —
  both as registered.
- **A defect on one side of a threshold masquerades as a moved line, and must**: on the 24
  registered one-sided sites (cells at n = 50) every caught replicate carried the signature, because on one side
  of a line a swapped outcome and a line moved to the far end are the same observation. The
  profile reports observations; the question, not the profile, is what cannot separate them.
- **A two-sided defect stops masquerading as the ledger grows** (D4: 0.46 at n = 5 falling
  to 0.08 at n = 50): once cases on both sides of the line disagree, the one-sided condition
  fails and the reader is not told the line moved. The same mechanism shows in D7's fall from
  0.80 to 0.57.
- **Where the pack draws no line, the profile carries nothing**: every caught cell of the
  `data-request-intake-triage` pack is threshold-free, and a reader of its profile sees a
  mismatch and no signature at all — neither a moved line nor its masquerade.

## Claims and non-claims

What is claimed: on these four packs, under the pinned runtime, replaying a ledger of
dispositions made under the unplanted pack catches a planted mechanical defect at the rates
tabulated, misses exactly the sites the registration named as invisible to dispositions, and
the profile's threshold report carries the line-moved signature exactly where the registration
said it must and never where it said it cannot. R1 is a conformance result: 131 registered
expectations, derived from the packs' text and the runtime's ADR-0034 before the run, all met.

What is not claimed (§8–§9 of the preregistration): nothing about any model's drafting;
nothing about whether a caught defect would be *understood* as one by a reader; nothing about
real histories — the literal and random generators are two distributions among many, and a
real history is neither; nothing about the runtime's correctness beyond the pinned binary's
behaviour on these inputs; and nothing beyond these four packs, which are a census of a demo.
The masquerades are the question's, not the profile's: the profile reported what was there.

## The holdout

| cell | the reviewer's expectation | observed | verdict |
|---|---|---|---|
| `h01-expense-d7-00-literal-signature` | 1 (the literal ledger's catch carries the signature) | 1 | holds |
| `h02-expense-d6-03-literal-no-threshold` | 0 (caught, threshold-free) | 0 | holds |
| `h03-vendor-d8-23-literal-at-row` | 0 (an at-row defeats the signature) | 0 | holds |
| `h04-vendor-d2-17-literal-mirror` | 1 (a mirrored guard: signature) | 1 | holds |
| `h05-triage-d8-13-literal-no-threshold` | 0 | 0 | holds |
| `h06-sanctions-d4-04-literal-two-sides` | 0 (two sides: no signature) | 0 | holds |
| `h07-triage-d6-05-random-20-catch` | [0.25, 0.75] | 0.47 | holds |
| `h08-vendor-d6-04-random-20-catch` | [0, 0.25] | 0.07 | holds |

## The full tables

Generated from `results/primary-attempt-001/CATCH-RATES.json` and `SIGNATURE.json`; per
instance the random stratum's exact 95% Clopper–Pearson interval, the literal stratum a count
with no interval, and the class-pooled rows as the harness reports them with their reference
intervals (no coverage claim).

### Per class, stratum and n (instance rows pooled)

| class | stratum | n | cells | caught | catch rate | signature among caught | threshold-free among caught |
|---|---|---|---|---|---|---|---|
| D1 | literal | — | 4 | 3 | 0.75 | 3/3 = 1.00 | 0/3 |
| D1 | random | 5 | 120 | 29 | 0.24 | 29/29 = 1.00 | 0/29 |
| D1 | random | 10 | 120 | 52 | 0.43 | 52/52 = 1.00 | 0/52 |
| D1 | random | 20 | 120 | 61 | 0.51 | 61/61 = 1.00 | 0/61 |
| D1 | random | 50 | 120 | 76 | 0.63 | 76/76 = 1.00 | 0/76 |
| D2 | literal | — | 4 | 4 | 1.00 | 3/4 = 0.75 | 0/4 |
| D2 | random | 5 | 120 | 30 | 0.25 | 15/30 = 0.50 | 0/30 |
| D2 | random | 10 | 120 | 55 | 0.46 | 27/55 = 0.49 | 0/55 |
| D2 | random | 20 | 120 | 70 | 0.58 | 40/70 = 0.57 | 0/70 |
| D2 | random | 50 | 120 | 83 | 0.69 | 53/83 = 0.64 | 0/83 |
| D3 | literal | — | 4 | 3 | 0.75 | 0/3 = 0.00 | 0/3 |
| D3 | random | 5 | 120 | 17 | 0.14 | 0/17 = 0.00 | 0/17 |
| D3 | random | 10 | 120 | 26 | 0.22 | 0/26 = 0.00 | 0/26 |
| D3 | random | 20 | 120 | 31 | 0.26 | 0/31 = 0.00 | 0/31 |
| D3 | random | 50 | 120 | 30 | 0.25 | 0/30 = 0.00 | 0/30 |
| D4 | literal | — | 4 | 4 | 1.00 | 1/4 = 0.25 | 0/4 |
| D4 | random | 5 | 120 | 68 | 0.57 | 31/68 = 0.46 | 0/68 |
| D4 | random | 10 | 120 | 85 | 0.71 | 27/85 = 0.32 | 0/85 |
| D4 | random | 20 | 120 | 92 | 0.77 | 17/92 = 0.18 | 0/92 |
| D4 | random | 50 | 120 | 96 | 0.80 | 8/96 = 0.08 | 0/96 |
| D5 | literal | — | 9 | 8 | 0.89 | 5/8 = 0.62 | 2/8 |
| D5 | random | 5 | 270 | 99 | 0.37 | 57/99 = 0.58 | 18/99 |
| D5 | random | 10 | 270 | 133 | 0.49 | 63/133 = 0.47 | 21/133 |
| D5 | random | 20 | 270 | 183 | 0.68 | 81/183 = 0.44 | 43/183 |
| D5 | random | 50 | 270 | 211 | 0.78 | 92/211 = 0.44 | 59/211 |
| D6 | literal | — | 13 | 5 | 0.38 | 3/5 = 0.60 | 2/5 |
| D6 | random | 5 | 390 | 32 | 0.08 | 20/32 = 0.62 | 12/32 |
| D6 | random | 10 | 390 | 59 | 0.15 | 33/59 = 0.56 | 26/59 |
| D6 | random | 20 | 390 | 93 | 0.24 | 48/93 = 0.52 | 45/93 |
| D6 | random | 50 | 390 | 132 | 0.34 | 61/132 = 0.46 | 71/132 |
| D7 | literal | — | 19 | 15 | 0.79 | 11/15 = 0.73 | 4/15 |
| D7 | random | 5 | 570 | 101 | 0.18 | 81/101 = 0.80 | 17/101 |
| D7 | random | 10 | 570 | 157 | 0.28 | 127/157 = 0.81 | 9/157 |
| D7 | random | 20 | 570 | 238 | 0.42 | 165/238 = 0.69 | 32/238 |
| D7 | random | 50 | 570 | 303 | 0.53 | 172/303 = 0.57 | 51/303 |
| D8 | literal | — | 3 | 3 | 1.00 | 1/3 = 0.33 | 1/3 |
| D8 | random | 5 | 90 | 78 | 0.87 | 48/78 = 0.62 | 30/78 |
| D8 | random | 10 | 90 | 82 | 0.91 | 52/82 = 0.63 | 30/82 |
| D8 | random | 20 | 90 | 90 | 1.00 | 60/90 = 0.67 | 30/90 |
| D8 | random | 50 | 90 | 90 | 1.00 | 60/90 = 0.67 | 30/90 |
| D9 | literal | — | 3 | 1 | 0.33 | 0/1 = 0.00 | 0/1 |
| D9 | random | 5 | 90 | 10 | 0.11 | 9/10 = 0.90 | 1/10 |
| D9 | random | 10 | 90 | 30 | 0.33 | 24/30 = 0.80 | 6/30 |
| D9 | random | 20 | 90 | 50 | 0.56 | 38/50 = 0.76 | 10/50 |
| D9 | random | 50 | 90 | 71 | 0.79 | 52/71 = 0.73 | 19/71 |

### Catch-rate curves per instance (random stratum; exact 95% Clopper–Pearson) and the literal ledger's count


### data-request-intake-triage

| defect | site | literal (1 ledger) | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|---|
| D5-10 | `rules/0:decline-redirect->proceed` | 0/1 | 3/30 = 0.10 [0.02, 0.27] | 3/30 = 0.10 [0.02, 0.27] | 12/30 = 0.40 [0.23, 0.59] | 16/30 = 0.53 [0.34, 0.72] |
| D5-11 | `rules/1:clarify-return->proceed` | 1/1 | 13/30 = 0.43 [0.25, 0.63] | 17/30 = 0.57 [0.37, 0.75] | 25/30 = 0.83 [0.65, 0.94] | 30/30 = 1.00 [0.88, 1.00] |
| D5-12 | `rules/2:proceed->clarify-return` | 1/1 | 2/30 = 0.07 [0.01, 0.22] | 1/30 = 0.03 [0.00, 0.17] | 6/30 = 0.20 [0.08, 0.39] | 13/30 = 0.43 [0.25, 0.63] |
| D6-04 | `rules/2/when[0]` | 1/1 | 2/30 = 0.07 [0.01, 0.22] | 5/30 = 0.17 [0.06, 0.35] | 10/30 = 0.33 [0.17, 0.53] | 17/30 = 0.57 [0.37, 0.75] |
| D6-05 | `rules/2/when[1]` | 0/1 | 5/30 = 0.17 [0.06, 0.35] | 7/30 = 0.23 [0.10, 0.42] | 14/30 = 0.47 [0.28, 0.66] | 25/30 = 0.83 [0.65, 0.94] |
| D6-06 | `rules/2/when[2]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D6-07 | `rules/2/when[3]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-00 | `rules/0/when` | 1/1 | 8/30 = 0.27 [0.12, 0.46] | 5/30 = 0.17 [0.06, 0.35] | 15/30 = 0.50 [0.31, 0.69] | 18/30 = 0.60 [0.41, 0.77] |
| D7-01 | `rules/1/when/conditions/0` | 1/1 | 5/30 = 0.17 [0.06, 0.35] | 2/30 = 0.07 [0.01, 0.22] | 5/30 = 0.17 [0.06, 0.35] | 7/30 = 0.23 [0.10, 0.42] |
| D7-02 | `rules/1/when/conditions/1[0]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-03 | `rules/1/when/conditions/1[1]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-08 | `rules/2/when/conditions/0` | 1/1 | 2/30 = 0.07 [0.01, 0.22] | 1/30 = 0.03 [0.00, 0.17] | 6/30 = 0.20 [0.08, 0.39] | 13/30 = 0.43 [0.25, 0.63] |
| D7-09 | `rules/2/when/conditions/1` | 1/1 | 2/30 = 0.07 [0.01, 0.22] | 1/30 = 0.03 [0.00, 0.17] | 6/30 = 0.20 [0.08, 0.39] | 13/30 = 0.43 [0.25, 0.63] |
| D8-13 | `exceptions/0:force->escalate` | 1/1 | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D9-14 | `fallbackOutcome:clarify-return->proceed` | 0/1 | 1/30 = 0.03 [0.00, 0.17] | 6/30 = 0.20 [0.08, 0.39] | 10/30 = 0.33 [0.17, 0.53] | 19/30 = 0.63 [0.44, 0.80] |

### expense-approval

| defect | site | literal (1 ledger) | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|---|
| D1-06 | `rules/1/when/conditions/0` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 4/30 = 0.13 [0.04, 0.31] | 6/30 = 0.20 [0.08, 0.39] | 16/30 = 0.53 [0.34, 0.72] |
| D2-07 | `rules/1/when/conditions/0` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 6/30 = 0.20 [0.08, 0.39] | 10/30 = 0.33 [0.17, 0.53] | 22/30 = 0.73 [0.54, 0.88] |
| D3-08 | `rules/1/when/conditions/0` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 2/30 = 0.07 [0.01, 0.22] | 0/30 = 0.00 [0.00, 0.12] |
| D4-09 | `rules/1/when/conditions/0` | 1/1 | 12/30 = 0.40 [0.23, 0.59] | 24/30 = 0.80 [0.61, 0.92] | 27/30 = 0.90 [0.73, 0.98] | 30/30 = 1.00 [0.88, 1.00] |
| D5-13 | `rules/0:deny->reimburse` | 1/1 | 26/30 = 0.87 [0.69, 0.96] | 29/30 = 0.97 [0.83, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D5-14 | `rules/1:reimburse->deny` | 1/1 | 7/30 = 0.23 [0.10, 0.42] | 16/30 = 0.53 [0.34, 0.72] | 23/30 = 0.77 [0.58, 0.90] | 29/30 = 0.97 [0.83, 1.00] |
| D6-03 | `rules/1/when[0]` | 1/1 | 5/30 = 0.17 [0.06, 0.35] | 14/30 = 0.47 [0.28, 0.66] | 21/30 = 0.70 [0.51, 0.85] | 29/30 = 0.97 [0.83, 1.00] |
| D6-04 | `rules/1/when[1]` | 1/1 | 17/30 = 0.57 [0.37, 0.75] | 25/30 = 0.83 [0.65, 0.94] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D6-05 | `rules/1/when[2]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-00 | `rules/0/when[0]` | 1/1 | 11/30 = 0.37 [0.20, 0.56] | 19/30 = 0.63 [0.44, 0.80] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D7-01 | `rules/0/when[1]` | 1/1 | 13/30 = 0.43 [0.25, 0.63] | 20/30 = 0.67 [0.47, 0.83] | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] |
| D7-02 | `rules/0/when[2]` | 1/1 | 16/30 = 0.53 [0.34, 0.72] | 25/30 = 0.83 [0.65, 0.94] | 27/30 = 0.90 [0.73, 0.98] | 30/30 = 1.00 [0.88, 1.00] |
| D7-10 | `rules/1/when/conditions/1/condition[0]` | 1/1 | 6/30 = 0.20 [0.08, 0.39] | 13/30 = 0.43 [0.25, 0.63] | 23/30 = 0.77 [0.58, 0.90] | 29/30 = 0.97 [0.83, 1.00] |
| D7-11 | `rules/1/when/conditions/1/condition[1]` | 1/1 | 7/30 = 0.23 [0.10, 0.42] | 13/30 = 0.43 [0.25, 0.63] | 20/30 = 0.67 [0.47, 0.83] | 28/30 = 0.93 [0.78, 0.99] |
| D7-12 | `rules/1/when/conditions/1/condition[2]` | 1/1 | 9/30 = 0.30 [0.15, 0.49] | 14/30 = 0.47 [0.28, 0.66] | 20/30 = 0.67 [0.47, 0.83] | 30/30 = 1.00 [0.88, 1.00] |
| D9-15 | `fallbackOutcome:review->reimburse` | 1/1 | 5/30 = 0.17 [0.06, 0.35] | 14/30 = 0.47 [0.28, 0.66] | 21/30 = 0.70 [0.51, 0.85] | 29/30 = 0.97 [0.83, 1.00] |

### sanctions-screening

| defect | site | literal (1 ledger) | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|---|
| D1-01 | `rules/1/when` | 1/1 | 17/30 = 0.57 [0.37, 0.75] | 26/30 = 0.87 [0.69, 0.96] | 29/30 = 0.97 [0.83, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D2-02 | `rules/1/when` | 1/1 | 15/30 = 0.50 [0.31, 0.69] | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D3-03 | `rules/1/when` | 1/1 | 17/30 = 0.57 [0.37, 0.75] | 26/30 = 0.87 [0.69, 0.96] | 29/30 = 0.97 [0.83, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D4-04 | `rules/1/when` | 1/1 | 25/30 = 0.83 [0.65, 0.94] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D5-05 | `rules/0:clear->match` | 1/1 | 15/30 = 0.50 [0.31, 0.69] | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D5-06 | `rules/1:match->clear` | 1/1 | 27/30 = 0.90 [0.73, 0.98] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D7-00 | `rules/0/when` | 1/1 | 15/30 = 0.50 [0.31, 0.69] | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |

### vendor-onboarding

| defect | site | literal (1 ledger) | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|---|
| D1-11 | `rules/1/when/conditions/5` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D1-16 | `exceptions/1/when` | 1/1 | 12/30 = 0.40 [0.23, 0.59] | 22/30 = 0.73 [0.54, 0.88] | 26/30 = 0.87 [0.69, 0.96] | 30/30 = 1.00 [0.88, 1.00] |
| D2-12 | `rules/1/when/conditions/5` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 2/30 = 0.07 [0.01, 0.22] | 1/30 = 0.03 [0.00, 0.17] |
| D2-17 | `exceptions/1/when` | 1/1 | 15/30 = 0.50 [0.31, 0.69] | 21/30 = 0.70 [0.51, 0.85] | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] |
| D3-13 | `rules/1/when/conditions/5` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D3-18 | `exceptions/1/when` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D4-14 | `rules/1/when/conditions/5` | 1/1 | 1/30 = 0.03 [0.00, 0.17] | 1/30 = 0.03 [0.00, 0.17] | 5/30 = 0.17 [0.06, 0.35] | 6/30 = 0.20 [0.08, 0.39] |
| D4-19 | `exceptions/1/when` | 1/1 | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D5-20 | `rules/0:request-info->approve` | 1/1 | 5/30 = 0.17 [0.06, 0.35] | 8/30 = 0.27 [0.12, 0.46] | 22/30 = 0.73 [0.54, 0.88] | 27/30 = 0.90 [0.73, 0.98] |
| D5-21 | `rules/1:approve->request-info` | 1/1 | 1/30 = 0.03 [0.00, 0.17] | 1/30 = 0.03 [0.00, 0.17] | 5/30 = 0.17 [0.06, 0.35] | 6/30 = 0.20 [0.08, 0.39] |
| D6-02 | `rules/1/when[0]` | 1/1 | 0/30 = 0.00 [0.00, 0.12] | 3/30 = 0.10 [0.02, 0.27] | 8/30 = 0.27 [0.12, 0.46] | 9/30 = 0.30 [0.15, 0.49] |
| D6-03 | `rules/1/when[1]` | 1/1 | 2/30 = 0.07 [0.01, 0.22] | 2/30 = 0.07 [0.01, 0.22] | 8/30 = 0.27 [0.12, 0.46] | 13/30 = 0.43 [0.25, 0.63] |
| D6-04 | `rules/1/when[2]` | 0/1 | 1/30 = 0.03 [0.00, 0.17] | 3/30 = 0.10 [0.02, 0.27] | 2/30 = 0.07 [0.01, 0.22] | 9/30 = 0.30 [0.15, 0.49] |
| D6-05 | `rules/1/when[3]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D6-06 | `rules/1/when[4]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D6-07 | `rules/1/when[5]` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-00 | `rules/0/when/conditions/0` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-01 | `rules/0/when/conditions/1` | 0/1 | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D7-08 | `rules/1/when/conditions/0` | 1/1 | 1/30 = 0.03 [0.00, 0.17] | 1/30 = 0.03 [0.00, 0.17] | 5/30 = 0.17 [0.06, 0.35] | 6/30 = 0.20 [0.08, 0.39] |
| D7-09 | `rules/1/when/conditions/1` | 1/1 | 1/30 = 0.03 [0.00, 0.17] | 1/30 = 0.03 [0.00, 0.17] | 5/30 = 0.17 [0.06, 0.35] | 6/30 = 0.20 [0.08, 0.39] |
| D7-10 | `rules/1/when/conditions/2` | 1/1 | 1/30 = 0.03 [0.00, 0.17] | 1/30 = 0.03 [0.00, 0.17] | 5/30 = 0.17 [0.06, 0.35] | 6/30 = 0.20 [0.08, 0.39] |
| D7-15 | `exceptions/0/when` | 1/1 | 4/30 = 0.13 [0.04, 0.31] | 13/30 = 0.43 [0.25, 0.63] | 13/30 = 0.43 [0.25, 0.63] | 27/30 = 0.90 [0.73, 0.98] |
| D8-22 | `exceptions/0:force->escalate` | 1/1 | 20/30 = 0.67 [0.47, 0.83] | 22/30 = 0.73 [0.54, 0.88] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D8-23 | `exceptions/1:escalate->force` | 1/1 | 28/30 = 0.93 [0.78, 0.99] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D9-24 | `fallbackOutcome:request-info->approve` | 0/1 | 4/30 = 0.13 [0.04, 0.31] | 10/30 = 0.33 [0.17, 0.53] | 19/30 = 0.63 [0.44, 0.80] | 23/30 = 0.77 [0.58, 0.90] |

### Signature table per instance: among the caught cells, the fraction carrying the line-moved signature (threshold-free caught cells counted apart)


### data-request-intake-triage

| defect | literal | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|
| D5-10 | no catch | 0/3 = 0.00 [0.00, 0.71] (3 threshold-free) | 0/3 = 0.00 [0.00, 0.71] (3 threshold-free) | 0/12 = 0.00 [0.00, 0.26] (12 threshold-free) | 0/16 = 0.00 [0.00, 0.21] (16 threshold-free) |
| D5-11 | 0/1 (1 threshold-free) | 0/13 = 0.00 [0.00, 0.25] (13 threshold-free) | 0/17 = 0.00 [0.00, 0.20] (17 threshold-free) | 0/25 = 0.00 [0.00, 0.14] (25 threshold-free) | 0/30 = 0.00 [0.00, 0.12] (30 threshold-free) |
| D5-12 | 0/1 (1 threshold-free) | 0/2 = 0.00 [0.00, 0.84] (2 threshold-free) | 0/1 = 0.00 [0.00, 0.97] (1 threshold-free) | 0/6 = 0.00 [0.00, 0.46] (6 threshold-free) | 0/13 = 0.00 [0.00, 0.25] (13 threshold-free) |
| D6-04 | 0/1 (1 threshold-free) | 0/2 = 0.00 [0.00, 0.84] (2 threshold-free) | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/10 = 0.00 [0.00, 0.31] (10 threshold-free) | 0/17 = 0.00 [0.00, 0.20] (17 threshold-free) |
| D6-05 | no catch | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/7 = 0.00 [0.00, 0.41] (7 threshold-free) | 0/14 = 0.00 [0.00, 0.23] (14 threshold-free) | 0/25 = 0.00 [0.00, 0.14] (25 threshold-free) |
| D6-06 | no catch | no catch | no catch | no catch | no catch |
| D6-07 | no catch | no catch | no catch | no catch | no catch |
| D7-00 | 0/1 (1 threshold-free) | 0/8 = 0.00 [0.00, 0.37] (8 threshold-free) | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/15 = 0.00 [0.00, 0.22] (15 threshold-free) | 0/18 = 0.00 [0.00, 0.19] (18 threshold-free) |
| D7-01 | 0/1 (1 threshold-free) | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/2 = 0.00 [0.00, 0.84] (2 threshold-free) | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/7 = 0.00 [0.00, 0.41] (7 threshold-free) |
| D7-02 | no catch | no catch | no catch | no catch | no catch |
| D7-03 | no catch | no catch | no catch | no catch | no catch |
| D7-08 | 0/1 (1 threshold-free) | 0/2 = 0.00 [0.00, 0.84] (2 threshold-free) | 0/1 = 0.00 [0.00, 0.97] (1 threshold-free) | 0/6 = 0.00 [0.00, 0.46] (6 threshold-free) | 0/13 = 0.00 [0.00, 0.25] (13 threshold-free) |
| D7-09 | 0/1 (1 threshold-free) | 0/2 = 0.00 [0.00, 0.84] (2 threshold-free) | 0/1 = 0.00 [0.00, 0.97] (1 threshold-free) | 0/6 = 0.00 [0.00, 0.46] (6 threshold-free) | 0/13 = 0.00 [0.00, 0.25] (13 threshold-free) |
| D8-13 | 0/1 (1 threshold-free) | 0/30 = 0.00 [0.00, 0.12] (30 threshold-free) | 0/30 = 0.00 [0.00, 0.12] (30 threshold-free) | 0/30 = 0.00 [0.00, 0.12] (30 threshold-free) | 0/30 = 0.00 [0.00, 0.12] (30 threshold-free) |
| D9-14 | no catch | 0/1 = 0.00 [0.00, 0.97] (1 threshold-free) | 0/6 = 0.00 [0.00, 0.46] (6 threshold-free) | 0/10 = 0.00 [0.00, 0.31] (10 threshold-free) | 0/19 = 0.00 [0.00, 0.18] (19 threshold-free) |

### expense-approval

| defect | literal | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|
| D1-06 | 1/1 | no catch | 4/4 = 1.00 [0.40, 1.00] | 6/6 = 1.00 [0.54, 1.00] | 16/16 = 1.00 [0.79, 1.00] |
| D2-07 | 1/1 | no catch | 6/6 = 1.00 [0.54, 1.00] | 10/10 = 1.00 [0.69, 1.00] | 22/22 = 1.00 [0.85, 1.00] |
| D3-08 | 0/1 | no catch | no catch | 0/2 = 0.00 [0.00, 0.84] | no catch |
| D4-09 | 0/1 | 12/12 = 1.00 [0.74, 1.00] | 18/24 = 0.75 [0.53, 0.90] | 11/27 = 0.41 [0.22, 0.61] | 2/30 = 0.07 [0.01, 0.22] |
| D5-13 | 1/1 | 19/26 = 0.73 [0.52, 0.88] | 6/29 = 0.21 [0.08, 0.40] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D5-14 | 1/1 | 7/7 = 1.00 [0.59, 1.00] | 16/16 = 1.00 [0.79, 1.00] | 23/23 = 1.00 [0.85, 1.00] | 29/29 = 1.00 [0.88, 1.00] |
| D6-03 | 0/1 (1 threshold-free) | 0/5 = 0.00 [0.00, 0.52] (5 threshold-free) | 0/14 = 0.00 [0.00, 0.23] (14 threshold-free) | 0/21 = 0.00 [0.00, 0.16] (21 threshold-free) | 0/29 = 0.00 [0.00, 0.12] (29 threshold-free) |
| D6-04 | 1/1 | 17/17 = 1.00 [0.80, 1.00] | 25/25 = 1.00 [0.86, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D6-05 | no catch | no catch | no catch | no catch | no catch |
| D7-00 | 1/1 | 11/11 = 1.00 [0.72, 1.00] | 13/19 = 0.68 [0.43, 0.87] | 14/30 = 0.47 [0.28, 0.66] | 4/30 = 0.13 [0.04, 0.31] |
| D7-01 | 1/1 | 11/13 = 0.85 [0.55, 0.98] | 11/20 = 0.55 [0.32, 0.77] | 12/28 = 0.43 [0.24, 0.63] | 5/30 = 0.17 [0.06, 0.35] |
| D7-02 | 1/1 | 15/16 = 0.94 [0.70, 1.00] | 19/25 = 0.76 [0.55, 0.91] | 18/27 = 0.67 [0.46, 0.83] | 1/30 = 0.03 [0.00, 0.17] |
| D7-10 | 1/1 | 6/6 = 1.00 [0.54, 1.00] | 13/13 = 1.00 [0.75, 1.00] | 23/23 = 1.00 [0.85, 1.00] | 29/29 = 1.00 [0.88, 1.00] |
| D7-11 | 1/1 | 7/7 = 1.00 [0.59, 1.00] | 13/13 = 1.00 [0.75, 1.00] | 20/20 = 1.00 [0.83, 1.00] | 28/28 = 1.00 [0.88, 1.00] |
| D7-12 | 1/1 | 9/9 = 1.00 [0.66, 1.00] | 14/14 = 1.00 [0.77, 1.00] | 20/20 = 1.00 [0.83, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D9-15 | 0/1 | 5/5 = 1.00 [0.48, 1.00] | 14/14 = 1.00 [0.77, 1.00] | 19/21 = 0.90 [0.70, 0.99] | 29/29 = 1.00 [0.88, 1.00] |

### sanctions-screening

| defect | literal | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|
| D1-01 | 1/1 | 17/17 = 1.00 [0.80, 1.00] | 26/26 = 1.00 [0.87, 1.00] | 29/29 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D2-02 | 0/1 | 0/15 = 0.00 [0.00, 0.22] | 0/28 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D3-03 | 0/1 | 0/17 = 0.00 [0.00, 0.20] | 0/26 = 0.00 [0.00, 0.13] | 0/29 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D4-04 | 0/1 | 16/25 = 0.64 [0.43, 0.82] | 8/30 = 0.27 [0.12, 0.46] | 1/30 = 0.03 [0.00, 0.17] | 0/30 = 0.00 [0.00, 0.12] |
| D5-05 | 1/1 | 15/15 = 1.00 [0.78, 1.00] | 28/28 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D5-06 | 0/1 | 10/27 = 0.37 [0.19, 0.58] | 4/30 = 0.13 [0.04, 0.31] | 1/30 = 0.03 [0.00, 0.17] | 0/30 = 0.00 [0.00, 0.12] |
| D7-00 | 1/1 | 15/15 = 1.00 [0.78, 1.00] | 28/28 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |

### vendor-onboarding

| defect | literal | n=5 | n=10 | n=20 | n=50 |
|---|---|---|---|---|---|
| D1-11 | no catch | no catch | no catch | no catch | no catch |
| D1-16 | 1/1 | 12/12 = 1.00 [0.74, 1.00] | 22/22 = 1.00 [0.85, 1.00] | 26/26 = 1.00 [0.87, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D2-12 | 1/1 | no catch | no catch | 2/2 = 1.00 [0.16, 1.00] | 1/1 = 1.00 [0.03, 1.00] |
| D2-17 | 1/1 | 15/15 = 1.00 [0.78, 1.00] | 21/21 = 1.00 [0.84, 1.00] | 28/28 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D3-13 | no catch | no catch | no catch | no catch | no catch |
| D3-18 | 0/1 | no catch | no catch | no catch | no catch |
| D4-14 | 1/1 | 1/1 = 1.00 [0.03, 1.00] | 1/1 = 1.00 [0.03, 1.00] | 5/5 = 1.00 [0.48, 1.00] | 6/6 = 1.00 [0.54, 1.00] |
| D4-19 | 0/1 | 2/30 = 0.07 [0.01, 0.22] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] | 0/30 = 0.00 [0.00, 0.12] |
| D5-20 | 1/1 | 5/5 = 1.00 [0.48, 1.00] | 8/8 = 1.00 [0.63, 1.00] | 22/22 = 1.00 [0.85, 1.00] | 27/27 = 1.00 [0.87, 1.00] |
| D5-21 | 1/1 | 1/1 = 1.00 [0.03, 1.00] | 1/1 = 1.00 [0.03, 1.00] | 5/5 = 1.00 [0.48, 1.00] | 6/6 = 1.00 [0.54, 1.00] |
| D6-02 | 1/1 | no catch | 3/3 = 1.00 [0.29, 1.00] | 8/8 = 1.00 [0.63, 1.00] | 9/9 = 1.00 [0.66, 1.00] |
| D6-03 | 1/1 | 2/2 = 1.00 [0.16, 1.00] | 2/2 = 1.00 [0.16, 1.00] | 8/8 = 1.00 [0.63, 1.00] | 13/13 = 1.00 [0.75, 1.00] |
| D6-04 | no catch | 1/1 = 1.00 [0.03, 1.00] | 3/3 = 1.00 [0.29, 1.00] | 2/2 = 1.00 [0.16, 1.00] | 9/9 = 1.00 [0.66, 1.00] |
| D6-05 | no catch | no catch | no catch | no catch | no catch |
| D6-06 | no catch | no catch | no catch | no catch | no catch |
| D6-07 | no catch | no catch | no catch | no catch | no catch |
| D7-00 | no catch | no catch | no catch | no catch | no catch |
| D7-01 | no catch | no catch | no catch | no catch | no catch |
| D7-08 | 1/1 | 1/1 = 1.00 [0.03, 1.00] | 1/1 = 1.00 [0.03, 1.00] | 5/5 = 1.00 [0.48, 1.00] | 6/6 = 1.00 [0.54, 1.00] |
| D7-09 | 1/1 | 1/1 = 1.00 [0.03, 1.00] | 1/1 = 1.00 [0.03, 1.00] | 5/5 = 1.00 [0.48, 1.00] | 6/6 = 1.00 [0.54, 1.00] |
| D7-10 | 1/1 | 1/1 = 1.00 [0.03, 1.00] | 1/1 = 1.00 [0.03, 1.00] | 5/5 = 1.00 [0.48, 1.00] | 6/6 = 1.00 [0.54, 1.00] |
| D7-15 | 1/1 | 4/4 = 1.00 [0.40, 1.00] | 13/13 = 1.00 [0.75, 1.00] | 13/13 = 1.00 [0.75, 1.00] | 27/27 = 1.00 [0.87, 1.00] |
| D8-22 | 1/1 | 20/20 = 1.00 [0.83, 1.00] | 22/22 = 1.00 [0.85, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D8-23 | 0/1 | 28/28 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] | 30/30 = 1.00 [0.88, 1.00] |
| D9-24 | no catch | 4/4 = 1.00 [0.40, 1.00] | 10/10 = 1.00 [0.69, 1.00] | 19/19 = 1.00 [0.82, 1.00] | 23/23 = 1.00 [0.85, 1.00] |

### Class-pooled rows as the harness reports them (reference intervals, no coverage claim)

| class | policy | stratum | n | caught/cells | rate | reference interval |
|---|---|---|---|---|---|---|
| D5 | data-request-intake-triage | literal | — | 2/3 | 0.67 | — |
| D5 | data-request-intake-triage | random | 5 | 18/90 | 0.20 | — |
| D5 | data-request-intake-triage | random | 10 | 21/90 | 0.23 | — |
| D5 | data-request-intake-triage | random | 20 | 43/90 | 0.48 | — |
| D5 | data-request-intake-triage | random | 50 | 59/90 | 0.66 | — |
| D6 | data-request-intake-triage | literal | — | 1/4 | 0.25 | — |
| D6 | data-request-intake-triage | random | 5 | 7/120 | 0.06 | — |
| D6 | data-request-intake-triage | random | 10 | 12/120 | 0.10 | — |
| D6 | data-request-intake-triage | random | 20 | 24/120 | 0.20 | — |
| D6 | data-request-intake-triage | random | 50 | 42/120 | 0.35 | — |
| D7 | data-request-intake-triage | literal | — | 4/6 | 0.67 | — |
| D7 | data-request-intake-triage | random | 5 | 17/180 | 0.09 | — |
| D7 | data-request-intake-triage | random | 10 | 9/180 | 0.05 | — |
| D7 | data-request-intake-triage | random | 20 | 32/180 | 0.18 | — |
| D7 | data-request-intake-triage | random | 50 | 51/180 | 0.28 | — |
| D8 | data-request-intake-triage | literal | — | 1/1 | 1.00 | — |
| D8 | data-request-intake-triage | random | 5 | 30/30 | 1.00 | — |
| D8 | data-request-intake-triage | random | 10 | 30/30 | 1.00 | — |
| D8 | data-request-intake-triage | random | 20 | 30/30 | 1.00 | — |
| D8 | data-request-intake-triage | random | 50 | 30/30 | 1.00 | — |
| D9 | data-request-intake-triage | literal | — | 0/1 | 0.00 | — |
| D9 | data-request-intake-triage | random | 5 | 1/30 | 0.03 | — |
| D9 | data-request-intake-triage | random | 10 | 6/30 | 0.20 | — |
| D9 | data-request-intake-triage | random | 20 | 10/30 | 0.33 | — |
| D9 | data-request-intake-triage | random | 50 | 19/30 | 0.63 | — |
| D1 | expense-approval | literal | — | 1/1 | 1.00 | — |
| D1 | expense-approval | random | 5 | 0/30 | 0.00 | — |
| D1 | expense-approval | random | 10 | 4/30 | 0.13 | — |
| D1 | expense-approval | random | 20 | 6/30 | 0.20 | — |
| D1 | expense-approval | random | 50 | 16/30 | 0.53 | — |
| D2 | expense-approval | literal | — | 1/1 | 1.00 | — |
| D2 | expense-approval | random | 5 | 0/30 | 0.00 | — |
| D2 | expense-approval | random | 10 | 6/30 | 0.20 | — |
| D2 | expense-approval | random | 20 | 10/30 | 0.33 | — |
| D2 | expense-approval | random | 50 | 22/30 | 0.73 | — |
| D3 | expense-approval | literal | — | 1/1 | 1.00 | — |
| D3 | expense-approval | random | 5 | 0/30 | 0.00 | — |
| D3 | expense-approval | random | 10 | 0/30 | 0.00 | — |
| D3 | expense-approval | random | 20 | 2/30 | 0.07 | — |
| D3 | expense-approval | random | 50 | 0/30 | 0.00 | — |
| D4 | expense-approval | literal | — | 1/1 | 1.00 | — |
| D4 | expense-approval | random | 5 | 12/30 | 0.40 | — |
| D4 | expense-approval | random | 10 | 24/30 | 0.80 | — |
| D4 | expense-approval | random | 20 | 27/30 | 0.90 | — |
| D4 | expense-approval | random | 50 | 30/30 | 1.00 | — |
| D5 | expense-approval | literal | — | 2/2 | 1.00 | — |
| D5 | expense-approval | random | 5 | 33/60 | 0.55 | — |
| D5 | expense-approval | random | 10 | 45/60 | 0.75 | — |
| D5 | expense-approval | random | 20 | 53/60 | 0.88 | — |
| D5 | expense-approval | random | 50 | 59/60 | 0.98 | — |
| D6 | expense-approval | literal | — | 2/3 | 0.67 | — |
| D6 | expense-approval | random | 5 | 22/90 | 0.24 | — |
| D6 | expense-approval | random | 10 | 39/90 | 0.43 | — |
| D6 | expense-approval | random | 20 | 51/90 | 0.57 | — |
| D6 | expense-approval | random | 50 | 59/90 | 0.66 | — |
| D7 | expense-approval | literal | — | 6/6 | 1.00 | — |
| D7 | expense-approval | random | 5 | 62/180 | 0.34 | — |
| D7 | expense-approval | random | 10 | 104/180 | 0.58 | — |
| D7 | expense-approval | random | 20 | 148/180 | 0.82 | — |
| D7 | expense-approval | random | 50 | 177/180 | 0.98 | — |
| D9 | expense-approval | literal | — | 1/1 | 1.00 | — |
| D9 | expense-approval | random | 5 | 5/30 | 0.17 | — |
| D9 | expense-approval | random | 10 | 14/30 | 0.47 | — |
| D9 | expense-approval | random | 20 | 21/30 | 0.70 | — |
| D9 | expense-approval | random | 50 | 29/30 | 0.97 | — |
| D1 | sanctions-screening | literal | — | 1/1 | 1.00 | — |
| D1 | sanctions-screening | random | 5 | 17/30 | 0.57 | — |
| D1 | sanctions-screening | random | 10 | 26/30 | 0.87 | — |
| D1 | sanctions-screening | random | 20 | 29/30 | 0.97 | — |
| D1 | sanctions-screening | random | 50 | 30/30 | 1.00 | — |
| D2 | sanctions-screening | literal | — | 1/1 | 1.00 | — |
| D2 | sanctions-screening | random | 5 | 15/30 | 0.50 | — |
| D2 | sanctions-screening | random | 10 | 28/30 | 0.93 | — |
| D2 | sanctions-screening | random | 20 | 30/30 | 1.00 | — |
| D2 | sanctions-screening | random | 50 | 30/30 | 1.00 | — |
| D3 | sanctions-screening | literal | — | 1/1 | 1.00 | — |
| D3 | sanctions-screening | random | 5 | 17/30 | 0.57 | — |
| D3 | sanctions-screening | random | 10 | 26/30 | 0.87 | — |
| D3 | sanctions-screening | random | 20 | 29/30 | 0.97 | — |
| D3 | sanctions-screening | random | 50 | 30/30 | 1.00 | — |
| D4 | sanctions-screening | literal | — | 1/1 | 1.00 | — |
| D4 | sanctions-screening | random | 5 | 25/30 | 0.83 | — |
| D4 | sanctions-screening | random | 10 | 30/30 | 1.00 | — |
| D4 | sanctions-screening | random | 20 | 30/30 | 1.00 | — |
| D4 | sanctions-screening | random | 50 | 30/30 | 1.00 | — |
| D5 | sanctions-screening | literal | — | 2/2 | 1.00 | — |
| D5 | sanctions-screening | random | 5 | 42/60 | 0.70 | — |
| D5 | sanctions-screening | random | 10 | 58/60 | 0.97 | — |
| D5 | sanctions-screening | random | 20 | 60/60 | 1.00 | — |
| D5 | sanctions-screening | random | 50 | 60/60 | 1.00 | — |
| D7 | sanctions-screening | literal | — | 1/1 | 1.00 | — |
| D7 | sanctions-screening | random | 5 | 15/30 | 0.50 | — |
| D7 | sanctions-screening | random | 10 | 28/30 | 0.93 | — |
| D7 | sanctions-screening | random | 20 | 30/30 | 1.00 | — |
| D7 | sanctions-screening | random | 50 | 30/30 | 1.00 | — |
| D1 | vendor-onboarding | literal | — | 1/2 | 0.50 | — |
| D1 | vendor-onboarding | random | 5 | 12/60 | 0.20 | — |
| D1 | vendor-onboarding | random | 10 | 22/60 | 0.37 | — |
| D1 | vendor-onboarding | random | 20 | 26/60 | 0.43 | — |
| D1 | vendor-onboarding | random | 50 | 30/60 | 0.50 | — |
| D2 | vendor-onboarding | literal | — | 2/2 | 1.00 | — |
| D2 | vendor-onboarding | random | 5 | 15/60 | 0.25 | — |
| D2 | vendor-onboarding | random | 10 | 21/60 | 0.35 | — |
| D2 | vendor-onboarding | random | 20 | 30/60 | 0.50 | — |
| D2 | vendor-onboarding | random | 50 | 31/60 | 0.52 | — |
| D3 | vendor-onboarding | literal | — | 1/2 | 0.50 | — |
| D3 | vendor-onboarding | random | 5 | 0/60 | 0.00 | — |
| D3 | vendor-onboarding | random | 10 | 0/60 | 0.00 | — |
| D3 | vendor-onboarding | random | 20 | 0/60 | 0.00 | — |
| D3 | vendor-onboarding | random | 50 | 0/60 | 0.00 | — |
| D4 | vendor-onboarding | literal | — | 2/2 | 1.00 | — |
| D4 | vendor-onboarding | random | 5 | 31/60 | 0.52 | — |
| D4 | vendor-onboarding | random | 10 | 31/60 | 0.52 | — |
| D4 | vendor-onboarding | random | 20 | 35/60 | 0.58 | — |
| D4 | vendor-onboarding | random | 50 | 36/60 | 0.60 | — |
| D5 | vendor-onboarding | literal | — | 2/2 | 1.00 | — |
| D5 | vendor-onboarding | random | 5 | 6/60 | 0.10 | — |
| D5 | vendor-onboarding | random | 10 | 9/60 | 0.15 | — |
| D5 | vendor-onboarding | random | 20 | 27/60 | 0.45 | — |
| D5 | vendor-onboarding | random | 50 | 33/60 | 0.55 | — |
| D6 | vendor-onboarding | literal | — | 2/6 | 0.33 | — |
| D6 | vendor-onboarding | random | 5 | 3/180 | 0.02 | — |
| D6 | vendor-onboarding | random | 10 | 8/180 | 0.04 | — |
| D6 | vendor-onboarding | random | 20 | 18/180 | 0.10 | — |
| D6 | vendor-onboarding | random | 50 | 31/180 | 0.17 | — |
| D7 | vendor-onboarding | literal | — | 4/6 | 0.67 | — |
| D7 | vendor-onboarding | random | 5 | 7/180 | 0.04 | — |
| D7 | vendor-onboarding | random | 10 | 16/180 | 0.09 | — |
| D7 | vendor-onboarding | random | 20 | 28/180 | 0.16 | — |
| D7 | vendor-onboarding | random | 50 | 45/180 | 0.25 | — |
| D8 | vendor-onboarding | literal | — | 2/2 | 1.00 | — |
| D8 | vendor-onboarding | random | 5 | 48/60 | 0.80 | — |
| D8 | vendor-onboarding | random | 10 | 52/60 | 0.87 | — |
| D8 | vendor-onboarding | random | 20 | 60/60 | 1.00 | — |
| D8 | vendor-onboarding | random | 50 | 60/60 | 1.00 | — |
| D9 | vendor-onboarding | literal | — | 0/1 | 0.00 | — |
| D9 | vendor-onboarding | random | 5 | 4/30 | 0.13 | — |
| D9 | vendor-onboarding | random | 10 | 10/30 | 0.33 | — |
| D9 | vendor-onboarding | random | 20 | 19/30 | 0.63 | — |
| D9 | vendor-onboarding | random | 50 | 23/30 | 0.77 | — |
