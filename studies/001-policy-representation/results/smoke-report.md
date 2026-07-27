# Study 001 -- policy representation: scored results

Paired design over 16 instances shared by every condition (8 of them redacted twins). Trials per instance: 2-2. Intervals are 95% percentile intervals from 500 paired bootstrap resamples of the instance set (seed 20260727). Baseline: `A::mock::mock/deterministic-v1`.

## Accuracy and consistency

| condition | accuracy | 95% CI | pass^k | 95% CI | parse-ok rate | engine-refusal rate |
|---|---:|---|---:|---|---:|---:|
| `A::mock::mock/deterministic-v1` | 0.312 | [0.156, 0.500] | 0.188 | [0.030, 0.375] | 0.969 | 0.000 |
| `Aprime::mock::mock/deterministic-v1` | 0.250 | [0.062, 0.438] | 0.188 | [0.000, 0.375] | 0.938 | 0.000 |
| `B::mock::judgment-pack-runtime` | 0.500 | [0.250, 0.750] | 0.500 | [0.250, 0.750] | 1.000 | 0.000 |

## Citation quality vs gold `relevant_rules`

| condition | precision | recall | F1 | 95% CI (F1) | micro F1 |
|---|---:|---:|---:|---|---:|
| `A::mock::mock/deterministic-v1` | 0.057 | 0.015 | 0.023 | [0.006, 0.046] | 0.030 |
| `Aprime::mock::mock/deterministic-v1` | 0.073 | 0.016 | 0.026 | [0.006, 0.050] | 0.030 |
| `B::mock::judgment-pack-runtime` | 0.562 | 0.101 | 0.170 | [0.094, 0.248] | 0.189 |

## Escalation on redacted twins (full 2x2)

Recall alone is not reported: an always-escalate agent scores recall 1.0 and must be visible as such through precision and F1.

| condition | should & did | should-not but did | should but did not | neither | precision | recall | F1 | 95% CI (F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `A::mock::mock/deterministic-v1` | 1 | 2 | 15 | 14 | 0.333 | 0.062 | 0.105 | [0.000, 0.320] |
| `Aprime::mock::mock/deterministic-v1` | 0 | 1 | 16 | 15 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] |
| `B::mock::judgment-pack-runtime` | 8 | 6 | 8 | 10 | 0.571 | 0.500 | 0.533 | [0.182, 0.824] |

## Paired differences vs baseline `A::mock::mock/deterministic-v1`

| condition | d accuracy | 95% CI | P(d>0) | d pass^k | 95% CI | d citation F1 | 95% CI | d escalation F1 | 95% CI |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| `Aprime::mock::mock/deterministic-v1` | -0.062 | [-0.219, 0.062] | 0.140 | 0.000 | [-0.188, 0.188] | 0.003 | [-0.023, 0.030] | -0.105 | [-0.320, 0.000] |
| `B::mock::judgment-pack-runtime` | 0.188 | [-0.156, 0.531] | 0.816 | 0.312 | [-0.062, 0.625] | 0.147 | [0.073, 0.219] | 0.428 | [-0.016, 0.800] |
