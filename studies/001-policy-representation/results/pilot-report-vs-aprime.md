# Study 001 -- policy representation: scored results

Paired design over 432 instances shared by every condition (216 of them redacted twins). Trials per instance: 1-1. Intervals are 95% percentile intervals from 2000 paired bootstrap resamples of the instance set (seed 20260806). Baseline: `Aprime::codex::gpt-5.6-sol`.

## Accuracy and consistency

| condition | accuracy | 95% CI | pass^k | 95% CI | parse-ok rate | engine-refusal rate |
|---|---:|---|---:|---|---:|---:|
| `A::codex::gpt-5.6-sol` | 0.414 | [0.368, 0.461] | 0.414 | [0.368, 0.461] | 1.000 | 0.000 |
| `Aprime::codex::gpt-5.6-sol` | 0.424 | [0.377, 0.470] | 0.424 | [0.377, 0.470] | 1.000 | 0.000 |
| `B::mock::judgment-pack-runtime` | 0.502 | [0.456, 0.549] | 0.502 | [0.456, 0.549] | 1.000 | 0.000 |

## Citation quality vs gold `relevant_rules`

| condition | precision | recall | F1 | 95% CI (F1) | micro F1 |
|---|---:|---:|---:|---|---:|
| `A::codex::gpt-5.6-sol` | 0.777 | 0.216 | 0.300 | [0.280, 0.321] | 0.307 |
| `Aprime::codex::gpt-5.6-sol` | 0.682 | 0.161 | 0.237 | [0.221, 0.253] | 0.242 |
| `B::mock::judgment-pack-runtime` | 0.597 | 0.117 | 0.186 | [0.174, 0.199] | 0.194 |

## Escalation on redacted twins (full 2x2)

Recall alone is not reported: an always-escalate agent scores recall 1.0 and must be visible as such through precision and F1.

| condition | should & did | should-not but did | should but did not | neither | precision | recall | F1 | 95% CI (F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `A::codex::gpt-5.6-sol` | 5 | 1 | 211 | 215 | 0.833 | 0.023 | 0.045 | [0.009, 0.088] |
| `Aprime::codex::gpt-5.6-sol` | 15 | 11 | 201 | 205 | 0.577 | 0.069 | 0.124 | [0.069, 0.186] |
| `B::mock::judgment-pack-runtime` | 92 | 60 | 124 | 156 | 0.605 | 0.426 | 0.500 | [0.436, 0.561] |

## Paired differences vs baseline `Aprime::codex::gpt-5.6-sol`

| condition | d accuracy | 95% CI | P(d>0) | d pass^k | 95% CI | d citation F1 | 95% CI | d escalation F1 | 95% CI |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| `A::codex::gpt-5.6-sol` | -0.009 | [-0.035, 0.014] | 0.195 | -0.009 | [-0.035, 0.014] | 0.063 | [0.042, 0.085] | -0.079 | [-0.135, -0.029] |
| `B::mock::judgment-pack-runtime` | 0.079 | [0.030, 0.125] | 1.000 | 0.079 | [0.030, 0.125] | -0.051 | [-0.067, -0.036] | 0.376 | [0.303, 0.444] |
