# Round 9 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit 6d0fdd5. Verdict: DO-NOT-FREEZE
(R8-2/3/4 + h08 RESOLVED; R8-1 NOT RESOLVED -> R9-1 BLOCKER guard porosity + live prose;
R9-2 BLOCKER stale manifest from the hand-made record-filing commit).
Dispositions: PREREG-REVIEW.md round-9 section; fixes landed as cb48421.

---

R8-1 — NOT RESOLVED: The five repaired passages, including `SPEC.md:465` and `verify.py:1247`, are corrected, but the guard still misses withdrawn source-reachability prose and multiple evasion classes; see R9-1.
R8-2 — RESOLVED: The comment accurately records the connector-store write preceding the awaited outer-row update.
R8-3 — RESOLVED: Every numeric identity claimed by a witness is validated before sorting, keying, or replay; `pass:1.0` and `pass:1e0` refuse on both sides. The differing registered layer-local codes are acceptable.
R8-4 — RESOLVED: The reference now correctly names the R6-5 residue filed as R7-3.
h08 — RESOLVED: The note remains byte-identical to the authored holdout, and `DEVIATIONS.md` contains the required disposition; the equality test passes.
R9-1 — BLOCKER — Offending: the guard in `test_study.py:320-557` and live prose including `verify.py:124-149,883-905,964-970`, `SPEC.md:351-353`, and `ceremony.ts:670-673`. Contradiction: §9 disclaims source-reachable retained histories, yet semantic/morphological variants such as “paths admit,” “produces/producible,” “can produce/can actually write,” and “leaves … retained” evade all seven phrases; CPython 3.12 f-strings and phrases split across comments or adjacent strings also evade extraction, while the ±400-character licence window can shadow another occurrence. Proposed fix: repair the live claims, add adversarial mutation tests covering historical formulations and representations, parse f-string/string content and contiguous comments correctly, bind licences to exact expected occurrences, and describe the guard as only a lexical backstop unless its narrower scope is intended.
R9-2 — BLOCKER — Offending: `6d0fdd5` changed manifest-covered `PREREG-REVIEW.md` without regenerating `STUDY-MANIFEST.sha256`. Contradiction: the exact-set manifest is a scorer precondition, and HEAD fails `test_study_manifest_is_exact`, making a registered run terminal-invalid. Proposed fix: regenerate the manifest after all round-9 manifest-covered edits, confirm only intended digest lines move, and rerun the suite.
do not freeze
Under the pinned runtimes, the identity regressions pass and the full suite reaches 160 passed with the stale-manifest test as its sole genuine failure. Zero-drift also holds: both registries’ `{id, expected}` projections match `dc4bc91`, the fixture tree is identical to `3730d0b`, and the authored holdout is unchanged. The remaining issues are not wording preferences: R8-1’s claimed class closure is demonstrably porous and misses current contradictory prose, while HEAD cannot pass its own pre-adjudication integrity gate.

CODEX-015-R9-DONE
