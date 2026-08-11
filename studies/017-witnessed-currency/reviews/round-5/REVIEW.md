# Round-5 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-11. Verdict: **freezable after listed fixes** (1 RESOLVED, 2 PARTIALLY RESOLVED, 1 new MINOR).

> Note: the reviewer's citations were emitted as links to absolute worktree paths; they are
> normalized here to bare file references. The finding prose is otherwise verbatim.

## Confirmation

- R4-1 — PARTIALLY RESOLVED — The scorer enumerates all six freeze pins, names each null offender, terminates for a missing map or uncovered cell ID, carries/rechecks the evidence digest, and the builder enumerates all six pins. However, an entry missing one of the three evidence fields silently drops that divergence channel; additionally, the scorer regression genuinely isolates each pin, but the builder leg runs once against the all-null live registry and checks only `matrixHoldoutEvidence`, so it does not exercise every builder pin individually. Require exact per-cell evidence-field validation and a one-null-at-a-time builder regression. ([score.py:115], [score.py:614], [score.py:650], [score.py:811], [score.py:827], [build_fixtures.py:313], [test_study.py:264])
- R1-9 — PARTIALLY RESOLVED — The published matrix has well-formed six-column rows containing all three evidence values, but the regression only checks every row’s pipe count and that any row contains `compared=` and `attributed=`; it does not explicitly require `unattributed=`, cover every witness row, or verify actual values. Strengthen it to compare every rendered triple with `RESULTS.json`. ([DETECTION-MATRIX.md:6], [score.py:720], [test_study.py:289])
- R1-1 residual — RESOLVED — The pin-registry note, upstream-loader docstring, and cache-test docstring now all distinguish accepted equivalent caches from import-eligible divergent caches. ([PINS.json:3], [upstream016.py:73], [test_study.py:113])

## New findings

- R5-1 — MINOR — `PREREGISTRATION.md` companion-artifact inventory and `harness/PINS.json` registry prose: both purportedly exhaustive inventories still omit `MATRIX-HOLDOUT-EVIDENCE.json`/`matrixHoldoutEvidence`, contradicting the actual six-pin gate and leaving the essential structured-expectation registry’s governing status misstated. Change “Three” to “Four,” add the evidence-map link, and add `matrixHoldoutEvidence` to both PINS enumerations. ([PREREGISTRATION.md:11], [PINS.json:3], [PINS.json:5])

freezable after listed fixes
