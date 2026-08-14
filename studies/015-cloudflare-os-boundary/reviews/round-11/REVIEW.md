# Round 11 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit 7bd0804. Verdict:
**FREEZABLE AFTER LISTED FIXES** — the study's first non-DO-NOT-FREEZE verdict
(R10-1 RESOLVED; one MAJOR, R11-1, claim-scope wording). The listed fix landed as
06e85f6; dispositions in PREREG-REVIEW.md round-11 section.

---

R10-1 — RESOLVED: All 14 unique five-field fingerprints match exactly one standing occurrence, producing `([], [])`. The held attack preserves the `retryab` count at 3→3 but yields exactly three unlicensed occurrences and three dead fingerprints, including the injected sentence. Changed locator/passage, duplication, deletion, and banner-shift reconvergence behave as designed.

R11-1 — MAJOR — Offending: `test_study.py:358-359,899-904,999-1020`, `PREREG-REVIEW.md:429`, and `DEVIATIONS.md:736-744`. Contradiction: the text says an occurrence cannot move to another line or change its surrounding sentence, but the mechanism fixes only its extracted locator and normalized ±120-character passage. Rewrapping the licensed Python-docstring occurrence from physical line 1295 to 1296 retains locator 1293 and passes; editing the same README sentence 151 normalized characters after `caused by` also passes. The synthetic regression changes a supplied locator/passage tuple, not arbitrary source line/sentence placement. Proposed fix: replace the line/sentence claims with “cannot change its registered locator or exact normalized ±120-character passage,” and describe the regression accordingly; reconverge locators and regenerate the manifest if the edits shift lines.

freezable after listed fixes

The substitution vulnerability itself is closed, expectations remain unchanged from `dc4bc91`, fixtures remain unchanged from `3730d0b`, and the two commits have the recorded scope. The native sandbox run passed 190 tests with nine blocked solely by the known `spawnSync git EPERM`; all 199 passed when that status-zero sandbox artifact was neutralized. No apparatus expansion is needed—only the listed claim-scope correction before freezing.

CODEX-015-R11-DONE
