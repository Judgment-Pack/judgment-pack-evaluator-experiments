# Pre-pilot effort sweep — 2026-08-24-effort-sweep

**`citable: false`. Outside every population.** PREREGISTRATION.md §2.1 registers this sweep as `n = 3/arm across three settings — 27 calls`, published in full. Nothing here is evidence for or against R1, and no setting is chosen by this file.

| what | value |
|---|---|
| registered settings | low, medium, high |
| per arm | 3 |
| call cap | 27 |
| per-call ceiling | 2700 s |
| budget | 72 h at N = 50/arm (batch.n) |
| model | `gpt-5.6-sol` |
| CLI | `codex-cli 0.145.0` |
| effort argument | `-c model_reasoning_effort=<tier>` |
| registry | `sha256:24e384246f6ac3948df12b6aaafedbf6e883783b3bbd4ed4ce08c1c51557104a` |

## M-24's witness resolution — the sweep's step zero

**Branch: `gate-5-extension`.**

transcript gate 5 is EXTENDED to this member, with the same turn-context-mismatch reason tag and the same apparatus-side classification, before the primary batch. The sweep publishes the branch; it does not amend the gate.

| occurrences | count |
|---|---|
| non-null, in `turn_context` (the gate-5 surface) | 2 |
| non-null, in another record type | 0 |
| present and NULL | 0 |


## Setting `low` — swept

| arm | run | duration s | completion bytes | reasoning tokens | exit | code | timed out |
|---|---|---|---|---|---|---|---|
| A | 1 | 203.4 | 33421 | 2524 | 0 | complete | no |
| B | 1 | 75.0 | 10391 | 483 | 0 | complete | no |
| C | 1 | 106.3 | 8016 | 3004 | 0 | complete | no |
| A | 2 | 197.3 | 38110 | 1409 | 0 | complete | no |
| B | 2 | 91.1 | 9654 | 791 | 0 | complete | no |
| C | 2 | 84.5 | 10294 | 918 | 0 | complete | no |
| A | 3 | 294.1 | 48822 | 3580 | 0 | complete | no |
| B | 3 | 77.4 | 10840 | 458 | 0 | complete | no |
| C | 3 | 81.4 | 10360 | 753 | 0 | complete | no |

| arm | mean duration s | completed calls |
|---|---|---|
| A | 231.6 | 3 |
| B | 81.2 | 3 |
| C | 90.8 | 3 |

Projected primary batch at N = 50/arm: **5.60 h** (budget 72 h).

## Setting `medium` — swept

| arm | run | duration s | completion bytes | reasoning tokens | exit | code | timed out |
|---|---|---|---|---|---|---|---|
| A | 1 | 328.6 | 38855 | 5327 | 0 | complete | no |
| B | 1 | 120.9 | 11165 | 1980 | 0 | complete | no |
| C | 1 | 92.0 | 10464 | 1188 | 0 | complete | no |
| A | 2 | 262.3 | 42313 | 3397 | 0 | complete | no |
| B | 2 | 134.7 | 12178 | 1657 | 0 | complete | no |
| C | 2 | 134.6 | 12223 | 2353 | 0 | complete | no |
| A | 3 | 304.8 | 41415 | 4314 | 0 | complete | no |
| B | 3 | 114.4 | 11368 | 1388 | 0 | complete | no |
| C | 3 | 110.3 | 11031 | 2070 | 0 | complete | no |

| arm | mean duration s | completed calls |
|---|---|---|
| A | 298.6 | 3 |
| B | 123.3 | 3 |
| C | 112.3 | 3 |

Projected primary batch at N = 50/arm: **7.42 h** (budget 72 h).

## Setting `high` — swept

| arm | run | duration s | completion bytes | reasoning tokens | exit | code | timed out |
|---|---|---|---|---|---|---|---|
| A | 1 | 456.8 | 44032 | 7093 | 0 | complete | no |
| B | 1 | 168.6 | 11825 | 5472 | 0 | complete | no |
| C | 1 | 147.7 | 12425 | 3106 | 0 | complete | no |
| A | 2 | 488.4 | 44061 | 7768 | 0 | complete | no |
| B | 2 | 193.7 | 13307 | 6314 | 0 | complete | no |
| C | 2 | 220.3 | 12741 | 5178 | 0 | complete | no |
| A | 3 | 355.6 | 48379 | 7539 | 0 | complete | no |
| B | 3 | 181.1 | 13010 | 4844 | 0 | complete | no |
| C | 3 | 153.9 | 12158 | 3624 | 0 | complete | no |

| arm | mean duration s | completed calls |
|---|---|---|
| A | 433.6 | 3 |
| B | 181.2 | 3 |
| C | 174.0 | 3 |

Projected primary batch at N = 50/arm: **10.95 h** (budget 72 h).


## Per-arm perfect and identity rates

Scored post-sweep by `harness/sweep_rates.py` (the driver registers that it computes no rate), through the registered scoring components: extract, admit with the presence-idiom guard live, the gold loop over 117 rows, and `referenceIdentity` with its registered pre-steps. **No kill quantity is computed**, by registered scope. `citable: false`, like everything in this file.

| setting | arm | perfect | identity | authoring codes |
|---|---|---|---|---|
| low | A | 0/3 | 3/3 | — |
| low | B | 2/3 | 2/3 | `opa-check-failed` |
| low | C | 0/3 | 1/3 | `presence-idiom-unsound`, `presence-idiom-unsound` |
| medium | A | 1/3 | 3/3 | — |
| medium | B | 2/3 | 1/3 | `opa-check-failed`, `unparseable-artifact` |
| medium | C | 2/3 | 2/3 | `opa-check-failed` |
| high | A | 1/3 | 3/3 | — |
| high | B | 1/3 | 1/3 | `presence-idiom-unsound`, `presence-idiom-unsound` |
| high | C | 3/3 | 1/3 | `unparseable-artifact` |
