# Study 001 -- policy representation: scored results

Paired design over 216 instances shared by every condition (0 of them redacted twins). Analysis population: `answerable`. Trials per instance: 5-5. Intervals are 95% percentile intervals from 2000 paired bootstrap resamples of 216 `twin` clusters (seed 20260806). Baseline: `A::codex::gpt-5.6-sol`.

## Accuracy and consistency

| condition | accuracy | 95% CI | pass^k | 95% CI | parse-ok rate | engine-refusal rate |
|---|---:|---|---:|---|---:|---:|
| `A::codex::gpt-5.6-sol` | 0.781 | [0.725, 0.833] | 0.727 | [0.667, 0.787] | 1.000 | 0.000 |
| `Aprime::codex::gpt-5.6-sol` | 0.778 | [0.718, 0.833] | 0.778 | [0.718, 0.833] | 1.000 | 0.000 |
| `B::mock::judgment-pack-runtime` | 0.579 | [0.509, 0.644] | 0.579 | [0.509, 0.644] | 1.000 | 0.000 |

## Citation quality vs gold `relevant_rules`

| condition | precision | recall | F1 | 95% CI (F1) | micro F1 |
|---|---:|---:|---:|---|---:|
| `A::codex::gpt-5.6-sol` | 0.787 | 0.224 | 0.309 | [0.282, 0.339] | 0.308 |
| `Aprime::codex::gpt-5.6-sol` | 0.694 | 0.167 | 0.244 | [0.225, 0.263] | 0.246 |
| `B::mock::judgment-pack-runtime` | 0.615 | 0.120 | 0.192 | [0.173, 0.209] | 0.196 |

## Escalation on redacted twins (full 2x2) -- NOT ESTIMABLE on this analysis set

**This analysis set (`population: answerable`, 216 instances) contains no redacted (should-escalate) instance, so one row of the 2x2 is empty and precision, recall and F1 are undefined on it.** They are printed as `n/a`, never as 0.000, here and in the paired differences below; H2 is not estimable on this set. The counts are still counts and are still shown: the should-not-but-did column is the false-escalation count that PREREGISTRATION.md section 6 names as H2's explicit cost criterion.

| condition | should & did | should-not but did | should but did not | neither | precision | recall | F1 | 95% CI (F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `A::codex::gpt-5.6-sol` | 0 | 12 | 0 | 1068 | n/a | n/a | n/a | n/a |
| `Aprime::codex::gpt-5.6-sol` | 0 | 51 | 0 | 1029 | n/a | n/a | n/a | n/a |
| `B::mock::judgment-pack-runtime` | 0 | 300 | 0 | 780 | n/a | n/a | n/a | n/a |

## Paired differences vs baseline `A::codex::gpt-5.6-sol`

| condition | d accuracy | 95% CI | P(d>0) | d pass^k | 95% CI | d citation F1 | 95% CI | d escalation F1 | 95% CI |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| `Aprime::codex::gpt-5.6-sol` | -0.003 | [-0.036, 0.030] | 0.430 | 0.051 | [0.009, 0.093] | -0.065 | [-0.092, -0.039] | n/a | n/a |
| `B::mock::judgment-pack-runtime` | -0.202 | [-0.262, -0.146] | 0.000 | -0.148 | [-0.213, -0.088] | -0.117 | [-0.154, -0.082] | n/a | n/a |

## McNemar's exact test on the pass^k indicator

PREREGISTRATION.md section 5 registers "McNemar's test for paired binary outcomes"; the exact two-sided form and the pass^k indicator as the binary are implementation choices recorded in DEVIATIONS.md section 4. The registered primary contrast is B vs A on the answerable population; every other row below is exploratory and unadjusted. The paired binary outcome is whether a condition got *all* k trials right on an instance; only instances the two conditions disagree about carry information, and the p is the exact two-sided binomial probability under an even split of them.

| condition vs baseline | baseline only correct | condition only correct | discordant | exact two-sided p |
|---|---:|---:|---:|---:|
| `Aprime::codex::gpt-5.6-sol` | 5 | 16 | 21 | 0.0266 |
| `B::mock::judgment-pack-runtime` | 44 | 12 | 56 | 2.088e-05 |
