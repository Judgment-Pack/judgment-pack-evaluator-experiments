# Review round 3 — prompt (verbatim)

You are the cross-vendor adversarial reviewer required by this program's interim review
regime (RFC 0009): a non-Anthropic model reviewing a preregistration before its freeze.
Your findings will be committed verbatim and dispositioned one by one in writing; the
freeze cannot happen until a round of this review returns exactly `freezable as written`.

The study is `studies/020-test-pinning-across-representations/` in this repository — an
instrument repair on Study 019, reviewed by you in round 1 (2026-08-24, `DO NOT FREEZE`,
R1-1 … R1-23) and round 2 (2026-08-25, `DO NOT FREEZE`, 11 BLOCKER / 7 MAJOR / 1 MINOR,
R2-1 … R2-19). **The maintainer has written a disposition on every round-2 finding and
closed the round; this round reviews the RESPONDED tree.** (A first launch of this round on 2026-09-02 at 20:26 UTC, with the prompt committed at `4e1a073f`, was refused by the provider's content classifier after reading and returned no review; this prompt is that one with its verification wording made plainer, substance unchanged.) Your job is threefold: verify
each of the nineteen dispositions against the bytes it claims, adjudicate the five
maintainer rulings registered FOR this round, and — because the holdout-input and
pilot/attempt blockers you named are repaired — author the fresh sealed reviewer mutant
set.

## Read

- `PREREG-REVIEW.md` — the round-2 disposition table is the response; read every row.
- `reviews/round-2/REVIEW.md` — your own findings, for what each disposition answers.
- `PREREGISTRATION.md` — the amended draft (third revision, post-round-2), completely.
  Every round-2 amendment is MARKED in place with its finding id; a figure that moved is
  printed beside the figure it replaced.
- The files this response added or rebuilt: `harness/e4lib/transfer.py` (the C4 transfer
  gate), `harness/e4lib/dispersion.py` (exact χ² intervals), `harness/pilot_analysis.py`
  (the post-pilot pass: `C4-REFERENCE.json`, `PILOT-DISPERSION.json`),
  `harness/tests/pilot_fixture.py` (the sealed-pilot builder), and the amended
  `harness/e4lib/family.py` (one universe; `MixedUniverseRefused`; the complete report
  with its Tier D `alternatives`), `harness/score.py` (`results_document()`,
  `reconciled_population()`, `familyReports`, `scoring_context()`, the C4 wiring),
  `harness/batch.py` (the sealed / chained / terminal pilot, `abandon`, the derived
  witness note), `calibration/derive_floor.py` (`validate_declaration()`, the reconciled
  `validate_record()`), `harness/pilot_rates.py`, `harness/sweep_rates.py`,
  `harness/make_manifest.py` (the ledger authentication and the analysis-artifact gate),
  `harness/integrity.py` (23 freeze pins; `_evidence_lines()`),
  `harness/counterfactual_shift.py` (the pinned estimand; two agreeing authorities),
  `harness/e4lib/engines.py` and `harness/e4lib/reviewer.py` (the typed no-answer
  boundary; the tri-state identity), and the whole of `harness/tests/`.
- `harness/PINS.json`, `harness/PORTS.md`, `harness/SCAFFOLD.md`,
  `harness/POWER-PRESENCE-IDIOM.md`, `harness/COUNTERFACTUAL-SHIFT.json` (regenerated
  once, under the registered estimand), `DEVIATIONS.md`, `CORRECTION-TARGETS.md`,
  `verification/V8-ASYMMETRY-LEDGER.md`, `README.md`.
- Study 019 is beside this study and FROZEN; the sweep evidence is under `sweeps/`.

## Adjudicate — the rulings registered for this round

1. **R2-2 — the estimand, re-ruled NATIVE-FOR-BOTH.** §5.2's F-1 block is re-ruled: each
   L2c member's outcome and its offset are weighted by the same language-native
   denominators; `harness/PINS.json`'s `family.outcomeWeighting` / `offsetWeighting`
   carry it; `family.py` refuses a mixed seat. The move: M16 +0.2323 → +0.1920,
   M17 +0.1275 → +0.0839, M18 +0.0911 → +0.0476 (A−C), verdict unchanged, included
   column unchanged (its native and shared denominators coincide). The hybrid is
   published SUPERSEDED as Tier D beside shared-for-both. Is the ruling coherent, is the
   residual it cites (+0.043552 / +0.042584 per unit) what the corpus computes, and is
   §5.5's Reprint 1b the right way to carry a moved reprint figure?
2. **R2-10 — the pilot denominator.** 21 attempts per arm, the 12 SCORED calls the
   apparatus-clean ones, an arm still short at the cap ABORTS. Confirm the declaration
   (0.20 on `identityFloor`) was not the defect and that the amended population shape
   (`attempted` / `calls` / `apparatusExcluded`) is one partition everywhere it is read.
3. **R2-12 — terminal first pilot.** §2a.6's re-pilot promise is struck (it named no
   reachable state); a label with NO completed call may be abandoned by `batch.py
   abandon --label` after a `DEVIATIONS.md` entry, retained, never deleted. Sound?
4. **R2-13 — the dispersion re-derivation.** `pilot_analysis.py` scores the pilot's
   apparatus-clean slots through the ONE scoring path and publishes σ, df, the exact χ²
   95 % interval and MDE at the pilot's n and the registered N; §5.6's 019 table stays as
   the labelled prior and the pilot table stands beside it. Recount the χ² factors
   ([0.7387, 1.5477] at df 15; [0.8066, 1.3163] at df 33) and the no-peek gate.
5. **R2-11(A) — two band rows.** §2a.5's reasoning-token band is dropped (the self-report
   branch is not taken under M-24's resolution); duration and completion-bytes bands
   [0.80, 1.25] stand, ratio pilot ÷ batch over the executed-call cohort, exact rows
   two-sided (row 1 on an exact mismatch, row 3 on a band miss). Confirm the routing.

## Verify against source, not trust

- **Every disposition row** against the tree: does the claimed fix exist, does the named
  test exist AND discriminate — the response claims a mutation check for every safeguard
  and records the mutation in the test's docstring; spot-check by reading the test against the mechanism it guards — and does anything in the row overstate what landed? Two items are declared
  STILL OWED rather than closed (§5.2's per-member analysis-set table, SCAFFOLD S10 — ruled 2026-09-02 to fill from the terminal pilot's measured apparatus-clean rates, so it stays owed until the pilot; and the sealed set); a third owed item you find is a finding.
- **The pilot ledger authentication** (`make_manifest.pilot_ledger_problems()`): check that a pilot record the gate must refuse is refused, and that a lawful one is accepted.
  `harness/tests/pilot_fixture.py` builds sealed pilots; read its cases against the gate.
- **The C4 gate end to end**: the eight exact rows, the two bands, the cohort, the
  reference document's validation, the two-sided routing into `decision.py`'s table.
- **The one-universe family**: recompute the six L2c members under all three readings
  from `harness/COUNTERFACTUAL-SHIFT.json`'s inputs or the fixture adapter; check the
  hybrid alternative reproduces Reprint 1 to the digit and that the registered rows are
  §5.5's Reprint 1b; check no decision reads an alternative.
- **The reconciled population** (`score.reconciled_population()`): batch-time and
  scoring-time apparatus by name, one denominator, `ScoreError` on disagreement.
- **The currency pass**: every cell round 2 named (R2-4, R2-6, R2-14, R2-17, R2-18,
  R2-19) against its machine source; the tests that now bind them.
- **The regenerated counterfactual**: the file names the estimand it was computed under;
  one descriptive cell changed sign (M18's adjusted shift, +0.015) and §3.2(iv) says so.
- **The evidence-walk entry check** (`integrity._evidence_lines()`): the three pinned digests do not move, and every non-regular or empty entry is refused by name.
- Every count and figure the amended registration asserts, against the artifact that
  carries it.

## Scrutinise

The standing lenses still apply (the population rule, the eighteen-member family, the
fill as a registration event, gate 5, the guard, the two identities, cross-arm fairness,
the corrections regime, the frozen-reader standard). Apply them to the AMENDED tree — in
particular: is every call the pilot machinery can spend one the registration permits,
can a NO-GO or calibration-invalid state reach the freeze or the primary attempt's
substantive rows, and does any disposition quietly change a registered quantity without
a marked amendment?

## This round's third job: author the sealed reviewer mutant set

You stated in rounds 1 and 2 that you are prepared. Author it now, in your review output —
it will be committed byte-for-byte with attribution under `controls/reviewer-mutants/`
(the registry's `reviewerMutantSet.path`) and sealed: the digest of its `MANIFEST.json`
becomes the `reviewerMutantSet` freeze pin; first execution is at the primary attempt
under the mandatory `--include-reviewer-set`; scored "as authored"; published
separately; it moves nothing in R1 (§4.3).

Requirements (the loader `harness/e4lib/reviewer.py` enforces the schema — read it):
- 6–10 mutants total, both languages represented, each a SINGLE semantic edit to the
  frozen reference (`reference/refA/pack.json` for `jps`, `reference/refB/policy.rego` for
  `rego`), chosen by YOU for what run-authored suites are likely to miss — do not reuse
  the registered generators' classes mechanically.
- For each: a complete payload file emitted as a fenced block with an exact filename
  (`rm-jps-01.json`, `rm-rego-01.rego`, …; ids `rm-<language>-NN` bound to the record's
  `language`), valid under its language's checker (validate them yourself with the
  pinned binaries), plus one sentence in prose on what it probes.
- A `MANIFEST.json` fenced block: `{"reviewerSetVersion": 1, "mutants": [{"id",
  "language" ("jps"|"rego"), "file", "sha256"}]}` — `reviewerSetVersion` a JSON integer,
  exactly those four members per record, the sha256 you computed over each payload's
  exact bytes.
- Any predictions you wish to register (which suites will miss which mutant, expected
  witness behaviour) go in your review prose, dated, as YOUR registered statements — the
  program scores predicted-vs-observed separately and neither side is edited afterward.

## Output

Numbered findings `R3-<n>`: severity BLOCKER / MAJOR / MINOR, file/section, a
one-paragraph failure mode, and a concrete fix. For each round-2 finding whose
disposition you verified, say so in one line each (grouped is fine): HOLDS, or the R3
finding it spawned; a disposition you could not verify is a finding. Then the sealed
set. Then one line, exactly one of: `freezable as written`, `freezable after listed
fixes`, `DO NOT FREEZE`. Cite the file you read for every claim.
