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

## Round 2 — 2026-08-09

**Reviewer:** codex-cli 0.145.0, model `gpt-5.6-sol`, reasoning effort
`ultra`, read-only sandbox. Prompt: `reviews/round-2/PROMPT.md`; verbatim
output: `reviews/round-2/REVIEW.md`. **Result: round-1 verification 9
RESOLVED / 9 PARTIALLY RESOLVED / 0 NOT RESOLVED; five new findings
(R2-1 MAJOR, R2-2 MAJOR, R2-3 MINOR, R2-4 MINOR, R2-5 NOTE); four holdout
mutation cells authored (h01–h04); freeze checklist delivered; verdict:
freezable only once residuals close and holdouts land unexecuted.** The
reviewer independently verified pilot-03's two-channel shape, including
byte-comparing the three masked cells' traces against goldens.

Dispositions (all implemented in this pass; pilot-04 is the first batch under
the round-2 harness: 25/25 validity rows, 0 divergences, verdict "R1 holds",
provenance stamped, holdouts absent):

| Item | Disposition | Where |
|------|-------------|-------|
| Round-1 residual: exact score-set equality; unreadable outputs as validity rows | **Accepted.** `check_validity` asserts scenario_scores keys = scheduled set; every load is wrapped — an unreadable run becomes an invalid validity row, never a pre-record crash. | harness/gate.py |
| Residual: mandatory identities; exact interpreters; clean pinned checkout | **Accepted.** `JPACK_BIN`/`FORGE_VENV_PY`/`FORGE_CLONE` are mandatory; harness Python must equal the pinned 3.12.11 exactly; the venv interpreter must equal 3.11.13; `FORGE_CLONE` must sit at the pinned commit with a clean tree. | harness/integrity.py |
| Residual: identities stamped into the attempt | **Accepted.** ADJUDICATION.json carries a provenance block (evaluator digest, Forge commit, freeze digest, interpreter, PINS digest, manifest digest). | harness/gate.py |
| Residual: root marking; no partial-rerun mode | **Accepted.** The root must be nonexistent; ATTEMPT.json is written before integrity; `--skip-runs` is removed entirely. | harness/gate.py |
| Residual: integrity as a recorded validity row | **Accepted.** Integrity runs first and lands as validity row 1; an integrity failure yields a terminal, recorded, pipeline-invalid adjudication. | harness/gate.py |
| Residual: G defined as disposition/action only, everywhere | **Accepted.** PREREGISTRATION §1/§4, MATRIX comment, and README all now scope G to completed-artifact disposition/action comparison. | docs |
| Residual: cohort-1 judge-unscored set registered and asserted | **Accepted.** `JUDGE_METRICS` is a registered constant; upstream validity asserts errored pairs are exactly the declared judge metrics with the registered error, zero deterministic errors, zero silent unscoring. | harness/gate.py |
| Residual: census wording; rows 5–6; decider claim | **Accepted.** README and CLASSIFICATION now say pre-specified author judgment; rows 5–6 drop the nonexistent Arm B normalization equivalence; the adversary is described as a fixed-cell negative control. | README.md, CLASSIFICATION.md, agents/deciders.py |
| Residual: answer-bearing ids/caseType reach a future model | **Accepted (amendment route, offered by the reviewer).** RQ3's pre-call amendment MUST define an opaque, non-answer-bearing case-handle mapping and withhold caseType; the expectation boundary stays enforced in code. | PREREGISTRATION.md §1 |
| R2-1 repeat cardinality | **Accepted.** Exactly 3 is enforced in repeat_check.py (refuses other values) and re-validated by the gate from REPEAT.json content: per-run exact case ids, completeness, driver exits, scorer errors. | harness/repeat_check.py, harness/gate.py |
| R2-2 incomplete artifacts and F | **Accepted.** Missing/incomplete cells are NOT-ADJUDICATED (never true/false), listed in `notAdjudicated`, and the batch is invalid via the validity channel. | harness/gate.py |
| R2-3 blocking-F self-audit | **Accepted.** Cells retain `F_requires_blocking`, `F_failed_metrics_all`, and `F_counted_metrics`, each metric as {name, passed, blocking}. | harness/gate.py |
| R2-4 verdict literals | **Accepted.** Three literals defined once in gate.py, quoted exactly in §5, asserted by a unit test. | harness/gate.py, PREREGISTRATION.md, harness/tests |
| R2-5 pilot provenance text | **Accepted.** Prereg §3 and README name all three retained batches and their toolchains. | docs |
| Holdouts h01–h04 | **Accepted, committed verbatim with attribution and unedited expectations.** Fixture bytes derive mechanically from the registered pointer edits (static generation); thin agent entries generated; the gate merges MATRIX-HOLDOUT only under `--include-holdout`, which is mechanically refused while the prereg is a DRAFT (verified: refusal fires before any directory is created); tests statically verify fixture-vs-spec agreement, schedule equality, and the absence of any h-cell execution artifact. R1(a)'s blanket sentence is narrowed per the reviewer's instruction: per-cell registrations govern; h02 and h04 are registered exceptions and their expectations were not touched. | scenarios/mutations/MATRIX-HOLDOUT.json, harness/mutate_packs.py, harness/gate.py, PREREGISTRATION.md §1, harness/tests |
| Freeze checklist item 4 (strata) | **Accepted.** Two epistemic strata (locked replication vs prospective holdouts) are defined in §1 and reported separately (holdout divergences flagged in their own stratum) under one validity result. | PREREGISTRATION.md, harness/gate.py |
| Standing non-claim (009/010 lineage) | **Accepted.** Added to §6. | PREREGISTRATION.md |

Open for round 3: confirm the residuals are closed and the holdout packaging
matches the authored intent; then the freeze checklist's mechanics items
(DRAFT→frozen wording, freeze commit naming, fresh primary root designation)
land in the freeze PR itself.

## Round 3 — 2026-08-09

**Reviewer:** codex-cli 0.145.0, model `gpt-5.6-sol`, reasoning effort
`ultra`, read-only sandbox. Prompt: `reviews/round-3/PROMPT.md`; verbatim
output: `reviews/round-3/REVIEW.md`. **Result: confirmation pass — pilot-04's
happy path verified as claimed and the holdout packaging verified byte-exact
(MATRIX-HOLDOUT.json cmp-identical to the round-2 authorship, sha256
b887db41…), but five blockers (R3-1..R3-5) and two majors (R3-6, R3-7) on
failure-path totality and stratum reporting. Verdict: not freezable yet.**

Dispositions (all implemented; pilot-05 is the first batch under the round-3
gate: pipeline-valid, 0 divergences, replication stratum 118/118 adjudicated
"holds", holdout stratum "not-scheduled", verdict "R1 holds"):

| # | Disposition | Where |
|---|-------------|-------|
| R3-1 | **Accepted.** The gate is total: safe per-field provenance; a terminal recorded adjudication exists on every path (integrity failure writes it before registry/matrix parsing; registry/matrix failure is its own validity row); run.json checked; scores/artifacts shape-validated before entering `loaded`; packs-test wrapped (crash/unparsable output → "unavailable" status → invalidity row, affected cells not-adjudicated). Negative tests added (provenance without env, missing outputs, unreadable REPEAT.json). | harness/gate.py, harness/tests |
| R3-2 | **Accepted.** Repeat details now carry artifact_ids, score_ids, all_completed, driver_exit, safety_violations; repeat_check refuses any cardinality but 3 and asserts both id sets per run; the gate re-validates REPEAT.json content: exactly repeat-01..repeat-03, both id sets equal to the full schedule, completion, scorer errors, exit/safety consistency. | harness/repeat_check.py, harness/gate.py |
| R3-3 | **Accepted.** The exact 40 (scenario, metric) judge-unscored pairs are registered in `scenarios/upstream-expected-unscored.json` (generated once from the pinned upstream bytes, committed, manifested) with the exact error string `judge not configured`; the gate asserts exact pair equality and flags scored, silent, missing, or extra pairs. | harness/generate.py, harness/gate.py |
| R3-4 | **Accepted.** Integrity resolves the venv's imported `evalforge` source (realpath) and requires it to BE `FORGE_CLONE`; git return codes are checked; the venv interpreter implementation is checked (CPython) in addition to its exact version. | harness/integrity.py |
| R3-5 | **Accepted.** `MATRIX-HOLDOUT.json`, `upstream-expected-unscored.json`, and `PREREGISTRATION.md` (causally read by the gate's DRAFT guard) joined the manifest globs (117 entries); hard-coded manifest counts removed from prose; the fixture test now reconstructs source + exactly one registered edit + the documentary prefix and asserts whole-document equality. | harness/integrity.py, harness/tests, PREREGISTRATION.md |
| R3-6 | **Accepted.** Strata are end-to-end: ADJUDICATION.json carries per-stratum scheduled/adjudicated/divergence counts and a per-stratum result (holds / falsified / incomplete / not-scheduled) under one global validity result; §1 and §5 scope "locked replication" to the sixteen original cells only, with the holdout stratum claimed as prospective. | harness/gate.py, PREREGISTRATION.md |
| R3-7 | **Accepted (pre-freeze part); remainder is the freeze PR's content by design.** Done now: pilot batches individually named through pilot-05; "the freeze re-runs everything" replaced with post-freeze-primary-attempt wording; round-3 prompt/review retained with these dispositions; the DRAFT guard matches the status line pattern (`Status: DRAFT`), not a bare substring. Deferred to the freeze PR, per the reviewer's own checklist: removing the DRAFT status lines, naming the freeze commit, designating the literal primary root (e.g. `results/primary-attempt-001`), stating the governing command with all three identities and `--include-holdout`, and demonstrating the static suite in the exact pinned environment at the freeze commit. | PREREGISTRATION.md, README.md, reviews/round-3/ |

Open for round 4 (if the reviewer wants one) or the freeze PR review: confirm
R3-1..R3-6 are closed in code and that the freeze-PR text satisfies the
checklist's transaction items.
