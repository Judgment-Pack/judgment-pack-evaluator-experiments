# Study 001 -- policy representation: scored results

Paired design over 432 instances shared by every condition (216 of them redacted twins). Trials per instance: 5-5. Intervals are 95% percentile intervals from 2000 paired bootstrap resamples of the instance set (seed 20260806). Baseline: `A::codex::gpt-5.6-sol`.

## Accuracy and consistency

| condition | accuracy | 95% CI | pass^k | 95% CI | parse-ok rate | engine-refusal rate |
|---|---:|---|---:|---|---:|---:|
| `A::codex::gpt-5.6-sol` | 0.402 | [0.356, 0.450] | 0.373 | [0.326, 0.419] | 1.000 | 0.000 |
| `Aprime::codex::gpt-5.6-sol` | 0.420 | [0.373, 0.468] | 0.417 | [0.370, 0.465] | 1.000 | 0.000 |
| `B::mock::judgment-pack-runtime` | 0.502 | [0.456, 0.549] | 0.502 | [0.456, 0.549] | 1.000 | 0.000 |

## Citation quality vs gold `relevant_rules`

| condition | precision | recall | F1 | 95% CI (F1) | micro F1 |
|---|---:|---:|---:|---|---:|
| `A::codex::gpt-5.6-sol` | 0.780 | 0.217 | 0.302 | [0.284, 0.322] | 0.304 |
| `Aprime::codex::gpt-5.6-sol` | 0.679 | 0.164 | 0.239 | [0.225, 0.253] | 0.245 |
| `B::mock::judgment-pack-runtime` | 0.597 | 0.117 | 0.186 | [0.174, 0.199] | 0.194 |

## Escalation on redacted twins (full 2x2)

Recall alone is not reported: an always-escalate agent scores recall 1.0 and must be visible as such through precision and F1.

| condition | should & did | should-not but did | should but did not | neither | precision | recall | F1 | 95% CI (F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `A::codex::gpt-5.6-sol` | 26 | 12 | 1054 | 1068 | 0.684 | 0.024 | 0.047 | [0.014, 0.087] |
| `Aprime::codex::gpt-5.6-sol` | 67 | 51 | 1013 | 1029 | 0.568 | 0.062 | 0.112 | [0.062, 0.171] |
| `B::mock::judgment-pack-runtime` | 460 | 300 | 620 | 780 | 0.605 | 0.426 | 0.500 | [0.436, 0.561] |

## Paired differences vs baseline `A::codex::gpt-5.6-sol`

| condition | d accuracy | 95% CI | P(d>0) | d pass^k | 95% CI | d citation F1 | 95% CI | d escalation F1 | 95% CI |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| `Aprime::codex::gpt-5.6-sol` | 0.018 | [-0.003, 0.040] | 0.951 | 0.044 | [0.021, 0.069] | -0.063 | [-0.080, -0.046] | 0.065 | [0.022, 0.117] |
| `B::mock::judgment-pack-runtime` | 0.100 | [0.047, 0.151] | 1.000 | 0.130 | [0.076, 0.181] | -0.116 | [-0.142, -0.092] | 0.453 | [0.382, 0.518] |
