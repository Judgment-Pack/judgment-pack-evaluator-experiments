The preregistration is **not freezable yet**. Pilot-04’s happy path verifies as claimed—25/25 passing validity rows, 16 original mutations, zero divergences, `R1 holds`, provenance present, and no holdouts—but several registered failure-path guarantees remain unenforced.

## 1. Round-2 freeze-checklist confirmation

| Item | Status | Evidence |
|---|---|---|
| Exact artifact-and-score equality everywhere | **STILL OPEN** | Ordinary and cohort-1 runs compare both sets in [gate.py](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:104). Repeats compare only artifact filenames: [repeat_check.py](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/repeat_check.py:39) reads `scores.json` but never checks `scenario_scores` IDs; gate revalidation checks only `case_ids` and does not require exactly three detail records. Pilot-04 happens to have exact sets in all 24 executed runs, but the gate does not enforce that for repeats. |
| Unreadable outputs become validity rows, never crashes | **STILL OPEN** | `run.json` is never read ([gate.py:91](/tmp/claude-1000/-home-onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:91)); packs-test stdout is unconditionally JSON-parsed and its process exit ignored ([gate.py:199](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:199)), with unwrapped calls at lines 385 and 405. Structurally invalid scores can also enter `loaded` before validation completes and crash later adjudication. |
| Mandatory identities, exact interpreters, clean pinned Forge checkout | **STILL OPEN** | Presence, digests, and exact 3.12.11/3.11.13 versions are enforced in [integrity.py:113](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/integrity.py:113) and lines 163–184. But the clean `FORGE_CLONE` is not proven to be the editable source imported by `FORGE_VENV_PY`; an unrelated clean clone at the pin can pass while the venv imports a different dirty checkout. `git status`’s return code is also ignored. |
| Provenance stamped into the attempt | **CLOSED** for successful attempts | The six registered fields are written by [gate.py:248](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:248) and present in [pilot-04 ADJUDICATION.json:3713](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/pilots/2026-08-09-offline-pilot-04/ADJUDICATION.json:3713). This does not cure the unbound Forge clone or incomplete manifest below. |
| Nonexistent root, early marking, no partial-rerun mode | **CLOSED** | Existing roots are refused, then `ATTEMPT.json` is written before integrity ([gate.py:263](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:263)). No governing `--skip-runs` option remains. |
| Integrity recorded as a terminal validity row | **STILL OPEN** | The row is appended first, but registry/matrix parsing and `provenance()` happen before the integrity-failure adjudication is written ([gate.py:279](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:279)). Missing `JPACK_BIN` makes `provenance()` raise `KeyError`; malformed causal JSON can likewise prevent any terminal record. |
| G is disposition/action comparison only | **CLOSED** | Operational G is limited accordingly in [gate.py:183](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:183). Current definitions agree in [PREREGISTRATION.md:22](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/PREREGISTRATION.md:22), README, and MATRIX. Historical review text correctly remains unchanged. |
| Exact registered cohort-1 judge-unscored set | **STILL OPEN** | `JUDGE_METRICS` is only a metric-name whitelist ([gate.py:67](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:67)). Lines 118–127 inspect actual entries but never compare against an exact registered `(scenario, metric)` set. Missing judge metrics or numerically scored judge metrics pass; error matching is substring-based rather than exact. |
| Census, rows 5–6, decider wording | **CLOSED** | RQ2 is a pre-specified, non-adjudicated author judgment ([PREREGISTRATION.md:67](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/PREREGISTRATION.md:67)); rows 5–6 explicitly acknowledge that the shell lacks an extraction stage ([CLASSIFICATION.md:27](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/CLASSIFICATION.md:27)); the adversary is only a fixed-cell negative control ([deciders.py:3](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/agents/deciders.py:3)). |
| RQ3 opaque-handle amendment | **CLOSED** | [PREREGISTRATION.md:83](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/PREREGISTRATION.md:83) requires the amendment before any model call, mandates opaque non-answer-bearing handles, and forbids `caseType`, expectations, and goldens. |

R2 findings:

- **R2-1 — STILL OPEN.** Three is hard-coded, but gate-side validation neither requires three named detail records nor checks repeat score IDs.
- **R2-2 — CLOSED.** Missing/incomplete mutation artifacts become `adjudicated: false` before J/F/G ([gate.py:411](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:411)).
- **R2-3 — CLOSED.** `F_requires_blocking`, all failed metrics, counted metrics, and `{name, passed, blocking}` are retained.
- **R2-4 — CLOSED.** The three literals are centralized, quoted exactly, and unit-tested.
- **R2-5 — STILL OPEN again.** [PREREGISTRATION.md:165](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/PREREGISTRATION.md:165) and README still say three pilots and stop at pilot-03, although pilot-04 now exists.

The offline suite passes 15/15 under the available Python 3.8.20, and current pack/upstream/declared study-manifest hashes verify. That is not an exact-pinned-environment test attestation, and the manifest’s declared coverage is incomplete.

## 2. Holdout packaging verification

| Item | Status | Evidence |
|---|---|---|
| Reviewer JSON verbatim, attributed, expectations unedited | **CLOSED** | `MATRIX-HOLDOUT.json` is byte-for-byte identical to round-2 review lines 75–192; `cmp` returned 0. SHA-256: `b887db4160f7e79c382e7756b3de19aa08b084e8f14242d7a1b8ea478f6c9ade`. |
| Four fixtures equal source plus registered edit and documentary prefix only | **CLOSED for the current bytes** | Independent structural comparison found exactly two differences per fixture: the registered pointer replacement and `description`. No other semantic field differs. |
| Thin agent entries | **CLOSED** | `mut_h01.py`–`mut_h04.py` each delegate to the shared shell with the corresponding pack override; the common behavior is in [mutants.py:127](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/agents/mutants.py:127). |
| Merge only with `--include-holdout`; refuse while DRAFT | **CLOSED in the current draft** | Conditional merge, collision check, and exact tag schedule are at [gate.py:224](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:224); refusal precedes root creation. Freeze caveat: the gate searches the entire preregistration for uppercase `DRAFT`, so both occurrences at lines 3 and 33 must disappear. |
| Static fixture-vs-spec test proves exact agreement | **STILL OPEN** | [test_study.py:175](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/tests/test_study.py:175) checks only that the destination pointer equals `to`. Arbitrary extra edits elsewhere would pass. It must reconstruct the source, assert `from`, apply exactly one replacement and the exact prefix, then compare the whole document. |
| Holdout registry covered by integrity/provenance | **STILL OPEN** | [integrity.py:31](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/integrity.py:31) includes only `MATRIX.json`. `MATRIX-HOLDOUT.json` is absent from the 114-line manifest, yet `check_study_manifest()` returns no error. Therefore expectation-only edits are not bound by attempt provenance. The preregistration also incorrectly calls it a 106-entry manifest. |
| No h01–h04 execution artifact | **CLOSED** | No h-run, golden, jpack-project output, result, or h-agent bytecode exists. Pilot-04 has `includeHoldout: false` and only the original 16 mutation keys. Every commit reachable from this branch was searched; no historical pilot/golden/jpack/result execution artifact exists. |
| R1 accommodates h02 and h04 without weakening falsifiability | **CLOSED** | [PREREGISTRATION.md:36](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/PREREGISTRATION.md:36) makes per-cell equality governing, names h02/h04 as exceptions only to descriptive tendencies, and says any divergence in either direction falsifies R1. |
| Replication/holdout strata reported separately | **STILL OPEN** | The gate merely places `holdout: true` on nonempty divergence rows and emits one aggregate verdict ([gate.py:441](/tmp/claude-1000/-home/onword-repo-judgment-pack/judgment-pack-runtime/aa6c2e1b-6627-4273-9ea2-6377a9b17a60/scratchpad/exp-013/studies/013-agent-eval-forge-integration/harness/gate.py:441)). A zero-divergence holdout run has no holdout-stratum result. Moreover, prereg lines 58–65 call the “exact” fixed-cell endpoint already observed, and §5 calls aggregate success a locked replication, misclassifying the prospective cells. |

## 3. Freeze verdict

**No — not freezable.**

1. **R3-1 — BLOCKER — validity/adjudication is not total.**  
   Validate `run.json`; type-check scores/artifacts before adding them to `loaded`; wrap packs-test execution, exit, and JSON parsing; and emit an explicit invalidity row for every failure. On integrity failure, write a minimal terminal adjudication before parsing any registry/matrix or computing fallible provenance. Add negative tests for every missing/malformed output.

2. **R3-2 — BLOCKER — repeat equality remains under-enforced.**  
   Put artifact IDs and score IDs into every repeat detail; require exactly `repeat-01` through `repeat-03`; compare both sets to all 21 IDs; and recheck completion, scorer errors, driver exit, and exit/safety consistency in the gate.

3. **R3-3 — BLOCKER — cohort-1 judge unscoring is not exactly registered.**  
   Register the exact 40 expected `(scenario, metric)` pairs, compare actual errored pairs for exact equality, require the error to equal `judge not configured`, and reject missing, scored, silently unscored, or extra pairs.

4. **R3-4 — BLOCKER — the clean Forge source identity can be bypassed.**  
   Resolve the `evalforge` source imported by `FORGE_VENV_PY` and require it to be the same checkout as `FORGE_CLONE`; check command return codes and clean status there. Check the Forge interpreter implementation as well as its version, and stamp that verified source/interpreter identity.

5. **R3-5 — BLOCKER — holdout expectations are not integrity-bound.**  
   Add `MATRIX-HOLDOUT.json`—and preferably the causally read preregistration status—to `MANIFEST_GLOBS`, regenerate the manifest, and remove or correct the hard-coded count. Strengthen the fixture test to whole-document source-plus-one-edit equality.

6. **R3-6 — MAJOR — the two epistemic strata are not implemented end-to-end.**  
   Add explicit replication and holdout summaries containing scheduled/adjudicated counts, divergences, and a per-stratum result under one global validity result. Revise §§1 and 5 so only the original 16 cells are a locked replication; h01–h04 remain prospective.

7. **R3-7 — MAJOR — the eventual freeze transaction and current provenance prose need correction.**  
   Before freezing:

   - name pilot-04 in PREREGISTRATION and README;
   - replace “the freeze re-runs everything” with post-freeze primary-run wording;
   - retain the round-3 prompt, this review, and dispositions;
   - remove both uppercase `DRAFT` occurrences or replace the brittle substring check;
   - name the freeze commit unambiguously;
   - register one literal nonexistent primary root, e.g. `results/primary-attempt-001`;
   - make the governing command include `JPACK_BIN`, `FORGE_VENV_PY`, `FORGE_CLONE`, CPython 3.12.11, `--include-holdout`, and that root;
   - demonstrate the static suite and integrity checks in the exact pinned environment;
   - keep the freeze commit clean and free of any primary or h01–h04 execution result.

No files were modified; the worktree remains clean.