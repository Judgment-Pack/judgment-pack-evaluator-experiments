# Pre-freeze review record

Cross-vendor adversarial review of PREREGISTRATION.md, per the interim review
regime. Each round records the reviewer identity, the verbatim prompt and
output (retained under `reviews/round-N/`), and a per-finding maintainer
disposition, implemented before the next round.

## Round 1 — 2026-08-09

**Reviewer:** codex-cli 0.145.0, model `gpt-5.6-sol`, reasoning effort
`ultra`, read-only sandbox, working directory = this study. Prompt:
`reviews/round-1/PROMPT.md`; verbatim output: `reviews/round-1/REVIEW.md`.
**Result: 18 findings (4 BLOCKER, 12 MAJOR, 2 MINOR). Verdict: not freezable
as written; freezable as a tightly scoped deterministic replication once 1–4
land and 5–16 are resolved. No direct endpoint collision with Study 012
found.**

All 18 findings were implemented in the same pass (pilot-03 is the first
batch under the reworked harness: pipeline-valid, 0 divergences, verdict
R1-holds). Dispositions:

| # | Sev | Disposition | Where |
|---|-----|-------------|-------|
| 1 | BLOCKER | **Accepted.** Gate gained a validity channel: scheduled-set equality per run, completeness, scorer errors, driver-exit consistency (4 iff safety; 3/5 always invalid), all recorded in `ADJUDICATION.json` with a global `pipelineValid` and a verdict field. Repeat check refuses runs that are not 21 completed artifacts. | harness/gate.py, harness/repeat_check.py |
| 2 | BLOCKER | **Accepted.** Integrity now verifies: the Forge venv freeze byte-for-byte against retained `harness/forge-freeze.txt` and its sha256 against PINS (the freeze line pins the editable install's commit `8925cac`), the harness interpreter (series enforced), mutated packs against a fresh temp-dir derivation, and a 106-entry `STUDY-MANIFEST.sha256` over every causal study file (agents, harness, cases, MATRIX, generated fixtures, goldens, jpack-project, vendored upstream). | harness/integrity.py, harness/PINS.json |
| 3 | BLOCKER | **Accepted.** §5 rewritten: an invalid primary attempt is terminal ("R1 inconclusive — pipeline-invalid"), computable divergences are still reported, reruns never replace the primary, and the gate refuses a non-empty pilot root (attempts immutable). | PREREGISTRATION.md §4–5, harness/gate.py |
| 4 | BLOCKER | **Accepted.** R1(c) is adjudicated: MATRIX cells where a protected action fires carry `F_requires_blocking: true`; the gate counts F there only when a failed metric has `blocking == true`. | scenarios/mutations/MATRIX.json, harness/gate.py, PREREGISTRATION.md §1 |
| 5 | MAJOR | **Accepted.** The post-freeze run is registered as a locked replication under the frozen protocol, not fresh prospective evidence; stated in §1 under "Epistemic status". Reviewer-authored holdout mutations remain an option for round 2 if the reviewer wants prospective cells. | PREREGISTRATION.md §1 |
| 6 | MAJOR | **Accepted.** `mutate_packs.py --out`; integrity derives into a temp directory and compares the exact filename set and bytes; the committed tree is never written during verification. | harness/mutate_packs.py, harness/integrity.py |
| 7 | MAJOR | **Accepted.** Completeness, scorer errors, and integrity live exclusively in the validity channel; G adjudicates only completed artifacts (disposition/action comparisons). | harness/gate.py, PREREGISTRATION.md §4 |
| 8 | MAJOR | **Accepted.** Real bug confirmed against the release binary: the envelope is `evaluationError.class`, not `error.class`. Shell fixed, refusal class retained in structured output, and evaluator refusal is an explicit second J source; pilot-03 m15a artifacts record `pack-not-conformant`. | agents/shell.py, harness/gate.py |
| 9 | MAJOR | **Accepted.** Pristine Arm B clean-per-case is an enforced validity precondition recorded in `ADJUDICATION.json`; detection is thereby relative to a verified-clean paired baseline. | harness/gate.py |
| 10 | MAJOR | **Accepted.** Non-independence disclosed in §2: goldens are a self-regression reference, the oracle a tautological positive control, F and G share the study-owned mapper as expectation source; F+G agreement is named shared-source concordance, and Forge is credited as external scoring machinery, not an independent action oracle. | PREREGISTRATION.md §2, §6 |
| 11 | MAJOR | **Accepted.** The three cells are re-described as "masked under the registered disposition/action projection"; MATRIX notes that the mutated evaluator traces differ from golden traces and are retained. | scenarios/mutations/MATRIX.json, PREREGISTRATION.md §1 |
| 12 | MAJOR | **Accepted.** Gate orchestrates cohort 1 and the repeat check in the single documented invocation; cohort 1's endpoint is narrowed to a Forge load/run/artifact/score smoke test with exact 20+8 id assertion, completed artifacts, zero deterministic scorer errors, and judge metrics enumerated as expected-unscored. | harness/gate.py, PREREGISTRATION.md §4, README.md |
| 13 | MAJOR | **Accepted.** RQ2 and CLASSIFICATION.md are labeled a pre-specified author judgment with chronology recorded but not independently enforceable; not an adjudicated endpoint. | PREREGISTRATION.md §1, CLASSIFICATION.md |
| 14 | MAJOR | **Partially accepted.** The defect was the category definition's wording, not the assignments: `integration_only` is redefined as machinery of the general agent loop (analogous concerns), with the overstated "Arm B depends on" phrasing corrected in place. Rows and tally stand under the corrected definition. | CLASSIFICATION.md |
| 15 | MAJOR | **Accepted.** "No efficacy" strengthened to "no model or operational efficacy"; R1 characterized as fixed-cell signal concordance with no sensitivity/detection-rate generalization; subjective endorsements replaced with measured properties. | PREREGISTRATION.md §1/§6, README.md, UPSTREAM.md |
| 16 | MAJOR | **Accepted.** Deciders now receive only the sanitized public case view (enforced in code; the oracle reads the registry itself as a disclosed control). RQ3's endpoint renamed to decision agreement with the pinned evaluator; the pre-call amendment must pin model, prompt fixtures by digest, parameters, SDK/retry, and failure policy. | agents/shell.py, agents/deciders.py, PREREGISTRATION.md §1 |
| 17 | MINOR | **Accepted.** caseType relabels: `4b-just-above-threshold`, `6b-fact-unknown`, `6c-number-not-decimal-string`; artifacts regenerated. | scenarios/jps/cases.json |
| 18 | MINOR | **Accepted.** CLASSIFICATION cites the vendored `upstream/` paths and names the upstream-repo paths explicitly. | CLASSIFICATION.md |

Residual noted for round 2: the reviewer's closing caution — the shared
009/010 defect-family lineage must never be used to synthesize a
probe-diversity or detection-power claim — is adopted as a standing non-claim.
Reviewer-authored holdout mutation cells remain on offer.
