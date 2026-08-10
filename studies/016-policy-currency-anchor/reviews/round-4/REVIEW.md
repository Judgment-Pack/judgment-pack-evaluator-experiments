# Round-4 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-10. Verdict: **freezable after listed fixes** (5/6 RESOLVED; R1-15 NOT RESOLVED; 1 new MINOR).

## Confirmation

- R1-1 — RESOLVED — `harness/upstream014.py:86-120,132-191` strips Study 014 paths after each module load and refuses late module collisions without overwriting them.
- R1-2 — RESOLVED — `harness/build_fixtures.py:8-26` contains corrected remint terminology and the accurate one-cell/two-readings identity account.
- R1-7 — RESOLVED — `harness/tests/test_registry.py:246-282` tests exactly `MAX_SNAPSHOT_BYTES + 1` and deterministically requires `pass` at exactly `MAX_CHECKPOINTS`.
- R1-11 — RESOLVED — `harness/build_fixtures.py:492-521,717-735` wraps every `HOLDOUT_HOOKS` callable with context verification before construction.
- R1-15 — NOT RESOLVED — `README.md:5-10` still positively describes a version “no longer in force,” outside an explicit disavowal; replace it with the snapshot-supported-set formulation promised by `PREREG-REVIEW.md:81`.
- R3-1 — RESOLVED — `harness/STUDY-MANIFEST.sha256` matches the exact set computed by `harness/make_manifest.py:42-93` (`--check` exits 0), and `harness/tests/test_study.py:104-109` provides the standing freshness assertion.

## New findings

- R4-1 — MINOR — `harness/build_fixtures.py:4-14`, construction inventory: it says four chains and omits `neg-replay`, despite constructing that fifth chain at `harness/build_fixtures.py:318-336,356` and registering five chains at `PREREGISTRATION.md:142-156,328-331`; the frozen builder documentation would conceal the REPLAY aliveness chain. Fix: change four to five and add the `neg-replay` inventory entry.

freezable after listed fixes
