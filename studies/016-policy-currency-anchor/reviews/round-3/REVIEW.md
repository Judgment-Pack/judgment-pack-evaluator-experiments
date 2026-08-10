# Round-3 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-10. Verdict: **freezable after listed fixes** (4 residuals partially resolved, 1 new MAJOR; holdout landing confirmed byte-identical).

## Confirmation

- R1-1 — PARTIALLY RESOLVED — `harness/upstream014.py:86-167` provides absolute-path loading and per-load verification, but lines 159-164 still mutate `sys.path`; executing `../014-openworkproof-binding/adapter/verify.py:44` and `harness/build_fixtures.py:49-55` leaves 014 paths installed, and late module collisions are overwritten rather than refused.
- R1-2 — PARTIALLY RESOLVED — `PREREGISTRATION.md`, `README.md`, and `harness/build_fixtures.py:303-385` correct the remint terminology, but `harness/build_fixtures.py:21-23` retains the removed `cur-older-snapshot-unpinned` identifier and obsolete identity claim.
- R1-3 — RESOLVED — `registry/verify_currency.py:302-325` strictly parses trust-configuration bytes, `harness/run_verify.py:84-88` passes raw bytes, and `harness/tests/test_registry.py:113-122` covers duplicate configuration members.
- R1-4 — RESOLVED — `harness/score.py:390-460` verifies both attestations under the enforced pinned authority key and does not rely on `authorityKeyId` labels.
- R1-7 — PARTIALLY RESOLVED — `harness/tests/test_registry.py:252-296` adds all three at-limit cases and +1 checkpoint/set refusals, but the byte refusal at lines 246-249 is `MAX_SNAPSHOT_BYTES + 2`, and the 1024-checkpoint case permits a semantic failure instead of requiring pass.
- R1-11 — PARTIALLY RESOLVED — `harness/build_fixtures.py:493-522,730-764` and `harness/score.py:528-640` gate the official route, construct inside the attempt, stamp/re-hash, and report separately, but every exposed `HOLDOUT_HOOKS` callable at `build_fixtures.py:558-723` ignores its context and can construct payloads while pins are null; pilot 03 has `holdout: null`, while pilots 01–02 omit that member, and no holdout fixture bytes exist.
- R1-12 — RESOLVED — `harness/score.py:755-784` hashes and parses the same single PINS read, all current terminal/success records carry `pinsRawSha256`, and `harness/PINS.json:4` describes it accurately.
- R1-15 — PARTIALLY RESOLVED — `README.md:5-18` fixes reliance and the research question, but lines 9-10 retain the exact “no longer in force” formulation.
- R2-1 — RESOLVED — `PREREGISTRATION.md:68-72` says 22, matching §4 and the 22 cells in `harness/MATRIX.json`.
- Holdout landing — RESOLVED — `reviews/round-2/REVIEW.md:30-196` and `harness/MATRIX-HOLDOUT.json:5-168` have byte-identical reviewer attribution and ten-cell content; no construction or expectation was altered.

## New findings

- R3-1 — MAJOR — `harness/STUDY-MANIFEST.sha256:2`, whole-study anchor: the manifest records the pre-round-2 `PREREG-REVIEW.md` digest `ac219f5…`, while the current file hashes `88875d9…`; `harness/make_manifest.py --check` consequently fails, and `harness/score.py:317-320` will terminal-refuse registered attempts once the manifest pin is filled. Regenerate the manifest after all final review-record edits, verify it, then pin its final digest during freeze.

freezable after listed fixes
