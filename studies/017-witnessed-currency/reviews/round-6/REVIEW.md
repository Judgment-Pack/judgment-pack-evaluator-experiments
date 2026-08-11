# Round-6 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-11. Verdict: **freezable after listed fixes** (2 RESOLVED, 1 PARTIALLY RESOLVED, 1 NOT RESOLVED, 1 new MINOR).

> Note: citations normalized from absolute worktree links to bare file references; the
> finding prose is otherwise verbatim.

## Confirmation

- R4-1(a) — PARTIALLY RESOLVED — validation is exact and terminal, but the regression sets `comparisonPerformed=1`, testing integer-as-boolean rather than boolean-as-integer; set an integer count field to `True`. ([score.py:614–645], [score.py:861–869], [test_study.py:297–311])
- R4-1(b) — RESOLVED — the builder reads patchable `PINS_PATH`, and its own gate is exercised with each of the six pins individually null. ([build_fixtures.py:54], [build_fixtures.py:306–320], [test_study.py:264–294])
- R1-9 — RESOLVED — every result cell must have exactly one witness row containing its complete rendered triple, and the renderer emits all three fields. ([test_study.py:314–338], [score.py:747–765])
- R5-1 — NOT RESOLVED — the four-artifact preregistration inventory and main pin note are complete, but `registeredLabelRule` still claims to enumerate every freeze pin while omitting `matrixHoldoutEvidence`; add it to that list. ([PREREGISTRATION.md:11–19], [PINS.json:3–5])

## New findings

- R6-1 — MINOR — `harness/PINS.json` §`anchorOrder` falsely says the whole-study manifest covers the holdout evidence map, while the generator and actual manifest omit it; the independent evidence pin prevents postselection, but the registered integrity claim is not honest. Add the map to `DOCUMENTS`, regenerate the manifest, and update `studyManifest.covers`. ([PINS.json:4,49–52,63], [make_manifest.py:22–30], [STUDY-MANIFEST.sha256:23–24])

freezable after listed fixes
