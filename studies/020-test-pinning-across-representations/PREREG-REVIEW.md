# Pre-freeze review record — Study 020

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here. The freeze requires a final round verdict of exactly
`freezable as written`.

**The round-state block, and what reads it (ADR 0005, decision 2 — registered for this study
from day one rather than adopted mid-regime as it was in Study 019).** The lifecycle of a
round is DATA, held once, here, in the fenced JSON block below: per round its number, its
state (`complete`, `awaiting-review`, `awaiting-response`), the verdict it returned, its
severity counts and its finding-id range. **Two** front doors — `README.md` and
`PREREGISTRATION.md` — each carry ONE sentence rendered from this block by
`harness/render_round_status.py`, and the currency suite requires that rendered string of each
of them VERBATIM. (Study 019 had three front doors; its third, `design/POLICY-DRAFT.md`, has no
020 analogue, because 020's policy prose is ported frozen rather than drafted here.) The block
itself is cross-checked STRUCTURALLY against the tree: the `reviews/round-N/` directories, each
verbatim review's finding ids, and this record's own disposition tables and severity columns.
The prose tables below stay for human readers and are **not parsed for their meaning** — the
truth of free prose rests where it rests in every predecessor study, on review. Run
`harness/render_round_status.py --write` when the block moves; the ceremony commit is then
mechanical.

**Two registered facts about the block's OPENING state — both now history, kept because they
explain shapes the parser still carries (R1-23: their present-tense forms outlived the states
they described).**

1. **The block opened EMPTY of rounds, and that was a legal state here.** Study 019's renderer
   refuses a zero-round block (`the block registers no rounds`) because 019 first wrote its
   block after round 1 already existed; **020's port permits and renders the empty-of-rounds
   block** — the shape this record actually held until round 1 opened 2026-08-24 — and the
   relaxation is now exercised synthetically by the currency suite while the live block carries
   its rounds. Every other refusal in that parser — duplicate members at every depth, closed
   object shapes, the closed verdict vocabulary bound to the review prompt's output line, the
   single-open-round rule, 1..N contiguity, and the marker-span reading — ports unchanged. The
   change is registered in `PREREGISTRATION.md` §7, delta 10.
2. **The rendered sentences were hand-written before the harness port, marked for mechanical
   regeneration — and the first act of the port WAS `render_round_status.py --write`, which
   reported `nothing moved`**: the hand-written sentences were already byte-identical to the
   rendered ones. They have been machine-produced ever since, the currency suite holds them
   verbatim, and the `GATE(pre-freeze)` that they stop being hand-written is CLOSED.

<!-- ROUND-STATE-BLOCK
{
 "blockVersion": 1,
 "rounds": [
  {
   "number": 1,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 13,
    "MAJOR": 9,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 23
   }
  },
  {
   "number": 2,
   "state": "awaiting-response",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 11,
    "MAJOR": 7,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 19
   }
  }
 ]
}
ROUND-STATE-BLOCK -->

## Rounds

| Round | State | Verdict | BLOCKER | MAJOR | MINOR | Findings |
|---|---|---|---|---|---|---|
| 1 | complete | DO NOT FREEZE | 13 | 9 | 1 | R1-1 … R1-23 |
| 2 | awaiting-response | DO NOT FREEZE | 11 | 7 | 1 | R2-1 … R2-19 |

**Round 1 opened 2026-08-24** on the filled draft (the sweep run, §2.1 filled at `low` /
N = 60, the gate-5 extension landed, the rates published): `reviews/round-1/PROMPT.md`
committed verbatim, this block moved to `awaiting-review`, both front doors re-rendered.
Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
sandbox, invoked over this repository checkout with the prompt's bytes on stdin.

**Round 1 returned 2026-08-24, the same day: `DO NOT FREEZE`, 13 BLOCKER / 9 MAJOR /
1 MINOR (R1-1 … R1-23)**, committed verbatim at `reviews/round-1/REVIEW.md`. The reviewer
independently reconciled the whole port chain (46 rows, 382 artifacts), the sweep ledgers
and every §2.1 figure, and the study's registered counts before finding against the tree —
the verdict is carried by the findings, not by drift in what was checked. The reviewer is
prepared to author the fresh sealed mutant set in a later round and authored none in this
one. Dispositions follow below as the maintainer's written response; the round closes when
every finding carries one.

**Round 1 CLOSED 2026-08-25: a written disposition stands on every one of the 23 findings.**
Twenty-two CONFIRMED and one PARTIALLY CONFIRMED (R1-3 — the mechanism held on verification,
the remedy over-reached, and the fix is the predicate split its disposition records), every
fix landed and mutation-checked; three maintainer rulings registered PROSPECTIVELY and owed to
round 2's adjudication (R1-4's hybrid estimand, R1-9's amended criterion, R1-15's holdout
exemption); R1-17's calibration instrument built complete — sealed deriver, `batch.py pilot`,
the §2a.4(2) declaration (0.20 on the identity floor), and the freeze gate's record
validation — with the pilot deliberately NOT run: per the finding's own remedy the completed
instrument goes to round 2 before any pilot call. Round 2 re-reviews the responded tree.

**Round 2 opened 2026-08-25** on the responded tree (all 23 round-1 dispositions written,
the calibration instrument complete, the §2a.4(2) declaration registered):
`reviews/round-2/PROMPT.md` committed verbatim, this block moved to `awaiting-review`, both
front doors re-rendered. Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning
effort ultra, read-only sandbox, invoked over this repository checkout with the prompt's
bytes on stdin. The round's charge: verify every disposition against the bytes it claims,
adjudicate the three prospective rulings (R1-4, R1-9, R1-15), and review the R1-17
instrument before any pilot call is spent.

**Round 2 returned 2026-08-25, the same day: `DO NOT FREEZE`, 11 BLOCKER / 7 MAJOR /
1 MINOR (R2-1 … R2-19)**, committed verbatim at `reviews/round-2/REVIEW.md`. The rulings:
R1-9 and R1-15 BLESSED, R1-4 REFUSED (the §5.2 estimand question reopens — R2-2). Eleven
round-1 dispositions verified outright; the rest carry named residuals. The pilot remains
unspent — R2-7 through R2-13 are about the pilot machinery and must land first.

## Dispositions

*(One section per round, one written maintainer disposition per finding, landing here when the
round's review does. A round is CLOSED when a written disposition per finding is on the record;
a round whose prompt is committed while its review has not landed is open in the other
direction. The lifecycle is a state read from the round's own artifacts and compared to the
block member-by-member; exactly one round — the highest — may be open.)*

## Round 1 — 2026-08-24

**`DO NOT FREEZE`, 13 BLOCKER / 9 MAJOR / 1 MINOR.** The verbatim review is
`reviews/round-1/REVIEW.md`; the reviewer independently reconciled the port chain, the sweep
ledgers, the §2.1 figures and every registered count before finding, and is prepared to author
the sealed mutant set in a later round. Dispositions land row by row below; a placeholder cell
is a finding the maintainer has not yet answered, and the round stays open until none remains.

| Finding | Severity | Disposition |
|---|---|---|
| R1-1 | BLOCKER | CONFIRMED, with the verified sharpening that no published figure was yet contaminated (the sweep emitted none of the affected codes — the defect was latent). FIXED at the source and typed end to end: `engines.invocation_refusal()` names the three no-answer classes, `jpack_json()` returns the typed refusal, a timed-out or garbage `opa check` raises, admission and E1 route `engines.EngineError` to the new apparatus code `engine-invocation-refused` (registered in §1a's amended table; `unreadable-output-shape` RETIRED with a marked note — every state that produced it was the engine failing to answer), the run leaves every population via the scorer's partition, `scoringApparatus` publishes it per arm, §6's amended gate scans the exclusions, and `sweep_rates.py` propagates the refusal as its own member. Kill-path semantics deliberately unchanged (a mutant provoking a refusal stays a ROW-ERROR signal). Enforced by the rewritten `test_score_admit.py` no-answer cases, `test_score_engines.py`'s typed ROW-ERROR case, and `test_score_reviewer_integration.py::test_an_unanswered_engine_excludes_the_run_and_fails_the_gate`. |
| R1-2 | BLOCKER | CONFIRMED — and verified WORSE than filed: the refusal fired on the registered nothing-evaluated record that every no-suite / no-cases / out-of-domain / identity-failure path produces, so one such admitted run hard-aborted the whole attempt. FIXED vector-authoritative: `require_survivor_schema()` accepts the total not-evaluated record and refuses genuine vector/aggregate inconsistency in any direction (killedPaired off the vector's count, survivorsPaired off its SURVIVED entries, evaluatedPaired off its evaluated count — the genuinely impossible state). §7 delta 1 carries the marked amendment. Enforced by `test_score_e4.py::test_the_total_not_evaluated_record_is_accepted_as_the_itt_zero_state` (the old test's exact inverse) and `::test_vector_aggregate_inconsistency_is_what_refuses_now`. |
| R1-3 | BLOCKER | PARTIALLY CONFIRMED on verification — the mechanism exactly (019 gated mutant execution on identity; the adapter synthesized total survival), the remedy over-broad (the recode moves exactly four member figures and no decision; 019's published ITT offsets are obtainable ONLY with the two runs in the marginal, −0.04846 = −0.04956 × 88/90 to every digit). FIXED as a predicate split: `Unit` carries `carries_kill_record` and `evaluated` (`scoreable` deleted), `offset()` takes the predicate, both ITT readings publish side by side, both adapters build the runs as carrying-but-not-evaluated with the inference asserted, and §5.2 carries the marked correction OF 019 with the four moved figures. Enforced by `test_family.py::test_the_two_never_evaluated_runs_are_honest_bytes_now` (the old `len(shifted)==36` pin passes under both codings and could not discriminate). |
| R1-4 | BLOCKER | CONFIRMED — no ruling existed and production ran a hybrid. RULED by the maintainer 2026-08-24: the hybrid IS the registered estimand (native outcome, shared offset), the only reading reproducing every §5.5 reprint; ruling text in §5.2 beside M-16(d), recorded at the code in `family.py`'s F-1 note, alternatives published Tier D (the pooled-vacuous ITT cell re-measured to −0.00554 under R1-3's honest units, noted). Round 2 verifies the ruling. |
| R1-5 | BLOCKER | CONFIRMED both halves. `PINS.json` gains the `family` block (permutation B/seed transcribed and test-bound to the module constants; BCa 10000 @ seed 13 registered 2026-08-24 pre-computation), `score.py` threads the pair into every `family_report()` call via the context, and `bca_interval()` resamples/jackknifes ALL arms for an adjusted statistic (the arms the statistic reads; unadjusted keeps the contrast pair). Enforced by `test_family.py::test_the_registered_stream_parameters_live_in_the_registry`, which drives both schemes and asserts `resampledArms`. |
| R1-6 | MAJOR | CONFIRMED. The six ANCOVA p-values are scheme-reproducible, not byte-reproducible (F-2; the generating stream is not in 019's tree and cannot be recovered). Marked scope note added to §5.5 printing BOTH streams for all six in both contrasts; every "to the printed digit" claim in the tree (§3.2(iv) fill, POWER-PRESENCE-IDIOM.md) now carries the scope. No downstream decision reads the affected digits. |
| R1-7 | MAJOR | CONFIRMED. `family.refused_cell_tier_d()` publishes the six ITT×ANCOVA quantities (three levels × two columns) over the artifact-bearing complete-case population with its per-arm composition, in every `family_report()` under `refusedCellTierD`, Tier D, read by no decision, while the member-level refusal stands. Enforced by `test_family.py::test_the_refused_cell_is_disclosed_in_six_tier_d_rows` (its L1/included figure pinned at this disclosure's own first computation, −0.01531). |
| R1-8 | MAJOR | CONFIRMED. `family.verdict()` now refuses extra ids, axis-relabelled rows, and rows whose stated sign/rejects disagree with their own difference/p (recomputed, fail-shut); `decision._family_claims()` validates the exact registered id set, the closed verdict token, the sign vocabulary and claim/verdict coherence independently. Fixtures moved onto the production shape. Enforced by `test_family.py`'s three refusal tests and `test_score_decision.py::test_eighteen_arbitrary_strings_do_not_adjudicate`. |
| R1-9 | BLOCKER | CONFIRMED — 39/39-of-parseable is not the registered 40/40, and substituting `unparseable-artifact` receipt for detector sensitivity blurred exactly what the finding says. RULED by the maintainer 2026-08-24 (the finding's own second branch): the criterion is AMENDED PROSPECTIVELY in §3.2 — (i-a) the detector flags its registered operating set exactly (n/n over admitted policies), (i-b) every in-class retained run receives a registered authoring code (40/40), (ii) 0/22 unchanged — the condition an admission-level detector could ever have met on this corpus, since the fortieth policy is refused by the parser before any detector can see it. Because the amendment postdates the first measurement it certifies NOTHING by itself: the re-run certification under R1-10's repaired detector was EXECUTED 2026-08-24 and meets it fresh (39/39, 178 uses, 0/22, recorded in `POWER-PRESENCE-IDIOM.md`'s re-certification section), and §3.2 registers the fallback in the amendment's own sentence — if round 2 refuses the criterion, the kill switch flips false and the guard demotes to Tier D. Round 2 adjudicates. |
| R1-10 | BLOCKER | CONFIRMED, all three defect classes, each then MEASURED LATENT on the certified corpus after repair. FIXED in `presence_idiom.py`: `_ref_path_resolved()` resolves statically-bound probe flags (the `k := "riskScore"; k in input.vendor` false negative) and statically-bound dynamic tails (`input[member]`); non-string scalar probes classify as lawful value-membership rather than flagged (the `5 in {"x": 5}` false positive that could zero-score a valid policy through admission). The full five-quantity certification was RE-RUN under the repaired detector (§3.2's re-cert paragraph; `POWER-PRESENCE-IDIOM.md`): every certified figure reproduces exactly — 39/39 flagged runs, 178 uses, B 19 / C 13 with the set-identity digest, 0/22, 0/392 lawful, 29 unclassified — and the corpus is measured to contain zero non-string scalar probes and zero statically-bound flagged probes, so the repairs change classifications only off-corpus. The third measured ceiling (the numeric-key trap outside the non-string-probe class) is published in §3.2 beside the two originals rather than discovered later. Enforced by `test_score_presence_idiom.py`'s three adversarial AST-constructor tests, one per defect class, each mutation-checked against the repair it certifies. |
| R1-11 | MAJOR | CONFIRMED both halves. The gate now authenticates IDENTITY, not aggregates: `PINS.json`'s `presenceIdiomGuard.recertification` pins `CERTIFIED_FLAGGED_SHA256` — the digest of the sorted certified flagged run-ID set — and `counterfactual_shift.py`'s `certify_identity()` refuses to publish when the re-derived flagged set's digest differs (a same-count member swap now refuses; the aggregate B 19 / C 13 check stands behind it as a second fence). The docstring's stale B 15 / C 17 split and the false all-24-lack-kill-blocks claim are corrected from the measured facts (six carry them), and the `PINS.json` recode note is reworded to the run-record vocabulary with the publication-vocabulary boundary marked. Enforced by `test_counterfactual_shift.py::test_a_same_arm_substitution_passes_the_counts_and_fails_the_identity` — the finding's own attack: one flagged run swapped for a same-arm substitute passes the counts gate and the identity gate refuses. |
| R1-12 | BLOCKER | CONFIRMED all three parts. Gate 5 is fail-CLOSED now: under a filled pin at least one non-null matching witness is required (zero witnesses refuse as `turn-context-mismatch`, apparatus), a non-string witness value refuses as malformed rather than raising TypeError, and a malformed nested level is an absent path; the wrapper's `reasoningEffortWitnessed` is a MEASUREMENT of this call's own retained transcript, never a fiat stamp, with the gate as the authority. Stand-in transcripts carry the member as real ones do. Enforced by the flipped `test_a_null_effort_member_is_no_witness_and_a_filled_pin_refuses`, the new `test_a_non_string_effort_witness_is_malformed_not_a_crash`, and the driver E2E suite running against witnessing stand-ins. |
| R1-13 | BLOCKER | CONFIRMED by production repro (zero scored runs in every arm). The rename LANDED: `score.py` writes `referenceIdentityPass`/`referenceIdentityFailures`/`referenceIdentityFailureCount` at every site; `reviewer.execute()` validates its input records fatally (missing or mistyped members are drift, never a silent skip), derives the eligible set independently and refuses a short execution, and marks `attempted` at entry with `executed` only on completion so an aborted execution is distinguishable and unrepeatable. Vocabulary boundaries marked in `sweep_rates.py` and `counterfactual_shift.py` (published/019 bytes keep 019's spelling). Enforced by `test_score_reviewer_integration.py` — a REAL `score_run()` output through `reviewer.execute()` with the pinned engines, the test that could not have passed before. |
| R1-14 | MAJOR | CONFIRMED all three parts. E6 runs in its own refusal scope (`e6EngineRefused`/`e6Refusal`; a refusal can no longer overwrite the completed reference result and kill vector), §6's gate scans E6's list by name, §1.2/§7's "one extra engine invocation" claims are amended to the measured exposure (arm A once per readable case; B/C one `opa test` plus one adjudication per reported failure), and E6's published rate divides by the runs E6 actually answered for with the not-asked count printed beside it. |
| R1-15 | BLOCKER | CONFIRMED (the code implemented §4.3 silently; §6 said otherwise). RULED by the maintainer 2026-08-24: holdout invocations are EXEMPT from `engine-execution-clean` and purely descriptive — refusals publish in the holdout's own record and cannot gate the attempt; §6 amended prospectively with the ruling and its reason (reviewer-authored bytes must not hold a veto over the study). Round 2 verifies. |
| R1-16 | BLOCKER | CONFIRMED. Completed at every named site: §2's schedule fill and §5.2's analysis-set direction read N = 60; `stats.py`'s docstring and vector comment demote the n = 50 row to a port control with the study's N registry-held (R1-16 correction notes in place); `test_score_stats.py` binds `PINS.batch.n == 60` and renames its N-claims to the prototype's; `DEVIATIONS.md`'s unmarked N = 50 sentence is marked; the registry's order note records the 60-round re-derivation with the 50-round carry as history. |
| R1-17 | BLOCKER | CONFIRMED — the instrument was owed in full. LANDED, all four remedy parts. (1) **The declaration**: `calibration.minimumViable = 0.20` on `minimumViableBasis = "identityFloor"`, the maintainer's §2a.4(2) ruling 2026-08-25 with the exposure rationale registered in §2a.4's fill (identity-basis because §5.7 makes arm A's imperfection a reported result, so a perfect-basis minimum aborts by design; 0.20 ⇔ ≥6/12 per arm, ~6% priced false-abort at 019's identity rates vs ~19% at the next rung, collapse at 1/3 caught w.p. 0.82; abort is study-death under M-9, so the gate catches collapse and §2a.6's recomputed dispersion table owns thin-but-alive arms). (2) **The sealed derivation**: `calibration/derive_floor.py` — both per-arm floors by the exact one-sided 95% CP rule through `e4lib/stats.py`'s primitives at §2a.1's alpha (NOT `stats.lower_bound()`, whose two-sided edge gives 0.735 where the registered table says 0.779 — `test_pilot.py` binds the three n=12 outputs to the table's bytes), `validate_record()` as the ONE reading of the record contract, go/no-go comparing DERIVED against DECLARED and choosing neither. (3) **The calibration command**: `batch.py pilot` under the new wrapper label `PIN_LABEL=PILOT` (§2a.2 amendment records the landed spellings) — 12/arm interleaved A-first into `calibration/<UTC date>-pilot/arm-<ARM>/run-NNN`, citable false, NO effort exemption, publish-after-every-call, refusing while the declaration is null (§2a.4(2)'s ordering ENFORCED) and refusing a second pilot (§2a.6); `pilot_rates.py` publishes `PILOT-RATES.json` through `sweep_rates.score_slot()`'s one scoring mirror, validated by the sealed deriver at publication. (4) **The freeze gate validates**: `make_manifest.calibration_record_problems()` — schema and counts through the sealed deriver, one pinned label, output digest match, `derivedFloor` reproduced by the rule, and GO required (a freeze over NO-GO is M-9's abort ignored). 48 tests in `tests/test_pilot.py`. The pilot has NOT run; per the finding's last sentence the completed instrument goes to round 2 before any pilot call. |
| R1-18 | BLOCKER | CONFIRMED — a precommitment the maintainer may rewrite post-freeze precommits nothing. FIXED in the covered direction: `CORRECTION-TARGETS.md` is back in `REGISTERED_DOCUMENTS` and the exact-set manifest (freezes with the tree; `pending_documents()` refuses while absent), `UNCOVERED_PRE_FREEZE_DOCUMENTS` is EMPTY with the category retained and its emptiness asserted, and the appendable half is the new `CORRECTION-TARGETS-LOG.md` — venue/status changes land there append-only, excluded exactly as the review record is (its `EXCLUDED_DOCUMENTS` reason cites this finding). §7 delta 11 and the `PORTS.md` make_manifest cell are amended to the covered reading (the cell's internal contradiction was R1-22's item and is resolved the same way). Enforced by `test_manifest.py::test_the_correction_target_register_is_covered_and_its_log_is_not`. |
| R1-19 | MAJOR | CONFIRMED — the fill's evidence was unauthenticated at freeze while `sweeps/` stayed manifest-exempt. FIXED by the finding's second branch (register a canonical tree digest, preserving the future-sweep permission): `PINS.json`'s `sweep.evidenceTrees` pins one canonical digest per evidence tree — `2026-08-24-effort-sweep` 96c36b79…, `refused-attempt-01` 3bf31aaa…, `refused-attempt-02` 732c5054… — each computed over the sorted relative-path/byte-digest pairs of the complete tree, and `integrity.verify_sweep_evidence()`, wired into `verify()`, recomputes them so the scorer's integrity gate now refuses mutation, addition, or deletion under any NAMED tree while an unnamed future sweep directory stays permitted. The manifest continues to cover no byte under `sweeps/` (ADR 0004's exact set is unchanged); authentication runs through the registry pin instead, which the freeze anchors. Enforced by `test_sweep_rates.py::test_the_sweep_evidence_trees_verify_and_tampering_refuses` — mutate, add, and delete each refuse; an unnamed tree does not. |
| R1-20 | MAJOR | CONFIRMED — and the correction was wrong, not the original. `codex debug models --bundled` (the build-owned catalog) reproduces the pre-sweep figures exactly (max 3/8, defaults low×1/medium×7); the first correction had recounted a mutable post-call cache. Correction-of-correction in §2.1 restores the original figures with the provenance lesson ("build-owned means --bundled"), `sweep.settingsProvenance` carries the same restoration, and the load-bearing facts (universal four; gpt-5.6-sol default low) held through every version. |
| R1-21 | MAJOR | CONFIRMED. The corrected table is APPENDED to `design/BRIEF.md` as a marked correction section (historical bytes untouched, per the fix's own instruction), with the ~1% budget headroom consequence stated; `CORRECTION-TARGETS.md` records the venue. |
| R1-22 | MAJOR | CONFIRMED — the chain was clean and the prose was not, which is the worse failure for a document whose job is describing deltas. Every named cell REWRITTEN FROM THE ACTUAL DIFF: the engines row names `opa_parse_tree()` (not `opa_parse()`) and describes the three formerly "byte-identical" cells from their real inequalities; the score row's false function names and its landed/owed inversions (the reference-identity rename HAS landed; the family/threshold deltas HAD landed) are corrected; the make_manifest cell's kept-and-removed contradiction over `CORRECTION-TARGETS.md` is resolved in R1-18's covered direction; the delta-table row 11 agrees with the cell it summarizes; and the test rows publishing unequal digests no longer say byte-identical. `ownPorts` and the manifest recomputed LAST, per the finding's own instruction and ADR 0005's anchor order. The structural lesson is banked where the next port will hit it: the verifier checks digests, so prose cells are claims — this round's currency tests now read the landed-item phrases out of `PORTS.md` itself (`test_prereg_currency.py`'s landed-list updated with the amended delta-11 phrase). |
| R1-23 | MINOR | CONFIRMED. Every named site fixed: both front-door headers defer to the rendered sentence (revision ordinals kept for the cross-check); PREREG-REVIEW's "two registered facts" recast as the opening-state history they are; README's DEVIATIONS line names the operational record; `PINS.json`'s note reads the filled design-time pins and the open round; `integrity.py`'s freeze-pin comment counts eighteen with the two-move story (model left, censusStimulusCount arrived). |

## Round 2 — 2026-08-25

**`DO NOT FREEZE`, 11 BLOCKER / 7 MAJOR / 1 MINOR (R2-1 … R2-19).** The verbatim review is
`reviews/round-2/REVIEW.md`. The three prospective rulings are adjudicated in the review's own
opening: **R1-9's amended criterion is BLESSED** (the guard does not flip to Tier D; its
carriers and switch test still owe repair — R2-4) and **R1-15's holdout exemption is BLESSED**;
**R1-4's hybrid estimand ruling is REFUSED** (R2-2: the hybrid reproduces §5.5's history but
violates §5.2's own de-biasing requirement — the maintainer must pick one coherent universe or
prospectively replace the criterion). The reviewer independently reproduced the calibration
ladder and the declaration's pricing arithmetic to ten digits, verified eleven round-1
dispositions outright, and reconciled every registered count it re-derived (gold 117, mutants
183/185, off-gold 236,196 cells, sweep 27/27, ports 46 rows / 382 artifacts). It remains
prepared to author the fresh sealed mutant set once the holdout-input and pilot/attempt
blockers are repaired, and authored none this round. Dispositions land row by row below; a
placeholder cell is a finding the maintainer has not yet answered, and the round stays open
until none remains.

| Finding | Severity | Disposition |
|---|---|---|
| R2-1 | BLOCKER | — |
| R2-2 | BLOCKER | — |
| R2-3 | MAJOR | — |
| R2-4 | MAJOR | — |
| R2-5 | BLOCKER | — |
| R2-6 | BLOCKER | — |
| R2-7 | BLOCKER | — |
| R2-8 | BLOCKER | — |
| R2-9 | BLOCKER | — |
| R2-10 | BLOCKER | — |
| R2-11 | BLOCKER | — |
| R2-12 | BLOCKER | — |
| R2-13 | BLOCKER | — |
| R2-14 | MAJOR | — |
| R2-15 | MAJOR | — |
| R2-16 | MAJOR | — |
| R2-17 | MAJOR | — |
| R2-18 | MAJOR | — |
| R2-19 | MINOR | — |
