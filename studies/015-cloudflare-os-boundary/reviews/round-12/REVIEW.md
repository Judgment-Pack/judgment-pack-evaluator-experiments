# Round 12 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit 19a5bb8. Verdict:
**MERGEABLE AFTER LISTED FIXES** (2 MAJOR narrative attributions/qualifications, 2 MINOR
documentation residues; the freeze, the attempt's byte-for-byte reproducibility, and the
h04/h06 tracings all confirmed). Dispositions: PREREG-REVIEW.md round-12 section; fixes
landed as 610a5dd.

---

1. **R12-1 (major)** — **Offending:** `ANALYSIS.md`’s h08 table and discussion, plus `DEVIATIONS.md`, attribute h08’s closure to R6-2. **Contradiction:** the exact h08 fixture was already divergent after round 1: finding 11 rejected the applied report without an approved row, while finding 6 separately supplied the outcome-ambiguity rule. Round 6 recorded zero outcome drift and only changed the first diagnostic reached. **Proposed fix:** attribute h08’s closure primarily to round-1 finding 11, retain finding 6 for the ambiguity rule/inverse endpoint, and describe R6-2 as diagnostic stabilization only. Correct `ANALYSIS.md`, `DEVIATIONS.md`, and the commit message if history is retained.

2. **R12-2 (major)** — **Offending:** `PINS.json` and generated `DETECTION-MATRIX.md` say the holdout was “never executed before freeze”; `ANALYSIS.md` and README describe it too broadly as prospective. **Contradiction:** the recorded pre-freeze snapshot checks computed all 35 outcomes by directly invoking the layers. What remained prospective was formal scorer adjudication/publication and the externally authored, unrevised expectations—not outcome knowledge. The candid limitation in `ANALYSIS.md` does not fully cure the absolute frozen wording, especially under its registry-precedence rule. **Proposed fix:** preserve the frozen/generated files, append an explicit `DEVIATIONS.md` correction, give such corrections precedence over stale frozen prose, and narrow README/ANALYSIS to the true prospective width.

3. **R12-3 (minor)** — **Offending:** frozen `PREREGISTRATION.md` §6 says there are exactly two paths that produce no `RESULTS.json`, naming existing-root refusal and pre-freeze holdout inclusion. **Contradiction:** after freeze, registered execution without `--include-holdout` writes the attempt marker and exits before producing results. The holdout-mode refusal changes with freeze state and the exhaustive statement is stale. **Proposed fix:** document in `DEVIATIONS.md` that wrong holdout mode produces no results—include-holdout before freeze, omission after freeze—alongside the existing-root case.

4. **R12-4 (minor)** — **Offending:** frozen `adapter/SPEC.md` still labels itself DRAFT; README says the protocol remains draft “until frozen by merge” and describes the scorer as refusing holdout; the existing deviation records only part of this stale status text. **Contradiction:** commit `968a9f8` froze and registered the protocol before merge, and the registered scorer now requires and separately scores holdout. **Proposed fix:** add the frozen SPEC label to `DEVIATIONS.md`, update the README rows to reflect immutable registered status and the pre-freeze/post-freeze holdout behavior, and rerun the phrase guard.

mergeable after listed fixes

The freeze and attempt are mechanically sound: all four pins and the exact manifest match, the frozen suite passes, the registered rerun reproduces the attempt artifacts byte-for-byte, R1 and holdout accounting reconcile, h04 and h06 withstand code-level tracing, and both mechanical guards—including locator 92’s byte-identical passage—hold. The remaining issues are two material attribution/qualification overstatements and two documentation residues; correcting them requires narrative and deviation updates, not a protocol change or rerun.

CODEX-015-R12-DONE
