# Calibration pilot 01 (2026-08-15) — NON-CITABLE

Harness-validation and difficulty-calibration pilot; supports no claim. Driver:
design/pilot/pilot_run.py (design-time, not the registered harness). 5 slots/arm at a
900s ceiling (slots 001-005) + re-runs at 2700s (slots 006-010 for arm A, 006 for B/C)
after every 900s slot in arm A — and one each in B/C — timed out (exit 124, empty
completion; the scorer mis-filed these as `no-marker`, a driver defect recorded for the
registered harness: timeouts are apparatus outcomes with their own code, never authoring
outcomes).

## Read of record (completed calls only)

- E1 (perfect gold agreement, 76 rows): arm A 5/5, arm B 5/5, arm C 5/5 — **all arms at
  ceiling** at this stimulus difficulty.
- Durations: arm A 1559-2408s per call; arms B/C 624-1101s. The one-UTC-day batch rule
  cannot hold at N=50/arm; the preregistration must register a multi-day window.
- Run-authored test suites: arm A 35-49 matrix rows/run touching 11-12/12 boundary
  literals; arms B/C 1-4 test rules/run (caveat: a Rego test rule can be table-driven,
  so rule count understates assertions; literals do appear in their bodies). The
  discriminating variance visible in this pilot lives on the test surface, not policy
  correctness.
