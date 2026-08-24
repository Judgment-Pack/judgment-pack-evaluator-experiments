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
   "state": "awaiting-response",
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
  }
 ]
}
ROUND-STATE-BLOCK -->

## Rounds

| Round | State | Verdict | BLOCKER | MAJOR | MINOR | Findings |
|---|---|---|---|---|---|---|
| 1 | awaiting-response | DO NOT FREEZE | 13 | 9 | 1 | R1-1 … R1-23 |

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
| R1-1 | BLOCKER | — |
| R1-2 | BLOCKER | — |
| R1-3 | BLOCKER | PARTIALLY CONFIRMED on verification — the mechanism exactly (019 gated mutant execution on identity; the adapter synthesized total survival), the remedy over-broad (the recode moves exactly four member figures and no decision; 019's published ITT offsets are obtainable ONLY with the two runs in the marginal, −0.04846 = −0.04956 × 88/90 to every digit). FIXED as a predicate split: `Unit` carries `carries_kill_record` and `evaluated` (`scoreable` deleted), `offset()` takes the predicate, both ITT readings publish side by side, both adapters build the runs as carrying-but-not-evaluated with the inference asserted, and §5.2 carries the marked correction OF 019 with the four moved figures. Enforced by `test_family.py::test_the_two_never_evaluated_runs_are_honest_bytes_now` (the old `len(shifted)==36` pin passes under both codings and could not discriminate). |
| R1-4 | BLOCKER | CONFIRMED — no ruling existed and production ran a hybrid. RULED by the maintainer 2026-08-24: the hybrid IS the registered estimand (native outcome, shared offset), the only reading reproducing every §5.5 reprint; ruling text in §5.2 beside M-16(d), recorded at the code in `family.py`'s F-1 note, alternatives published Tier D (the pooled-vacuous ITT cell re-measured to −0.00554 under R1-3's honest units, noted). Round 2 verifies the ruling. |
| R1-5 | BLOCKER | CONFIRMED both halves. `PINS.json` gains the `family` block (permutation B/seed transcribed and test-bound to the module constants; BCa 10000 @ seed 13 registered 2026-08-24 pre-computation), `score.py` threads the pair into every `family_report()` call via the context, and `bca_interval()` resamples/jackknifes ALL arms for an adjusted statistic (the arms the statistic reads; unadjusted keeps the contrast pair). Enforced by `test_family.py::test_the_registered_stream_parameters_live_in_the_registry`, which drives both schemes and asserts `resampledArms`. |
| R1-6 | MAJOR | CONFIRMED. The six ANCOVA p-values are scheme-reproducible, not byte-reproducible (F-2; the generating stream is not in 019's tree and cannot be recovered). Marked scope note added to §5.5 printing BOTH streams for all six in both contrasts; every "to the printed digit" claim in the tree (§3.2(iv) fill, POWER-PRESENCE-IDIOM.md) now carries the scope. No downstream decision reads the affected digits. |
| R1-7 | MAJOR | CONFIRMED. `family.refused_cell_tier_d()` publishes the six ITT×ANCOVA quantities (three levels × two columns) over the artifact-bearing complete-case population with its per-arm composition, in every `family_report()` under `refusedCellTierD`, Tier D, read by no decision, while the member-level refusal stands. Enforced by `test_family.py::test_the_refused_cell_is_disclosed_in_six_tier_d_rows` (its L1/included figure pinned at this disclosure's own first computation, −0.01531). |
| R1-8 | MAJOR | CONFIRMED. `family.verdict()` now refuses extra ids, axis-relabelled rows, and rows whose stated sign/rejects disagree with their own difference/p (recomputed, fail-shut); `decision._family_claims()` validates the exact registered id set, the closed verdict token, the sign vocabulary and claim/verdict coherence independently. Fixtures moved onto the production shape. Enforced by `test_family.py`'s three refusal tests and `test_score_decision.py::test_eighteen_arbitrary_strings_do_not_adjudicate`. |
| R1-9 | BLOCKER | — |
| R1-10 | BLOCKER | — |
| R1-11 | MAJOR | — |
| R1-12 | BLOCKER | — |
| R1-13 | BLOCKER | — |
| R1-14 | MAJOR | — |
| R1-15 | BLOCKER | CONFIRMED (the code implemented §4.3 silently; §6 said otherwise). RULED by the maintainer 2026-08-24: holdout invocations are EXEMPT from `engine-execution-clean` and purely descriptive — refusals publish in the holdout's own record and cannot gate the attempt; §6 amended prospectively with the ruling and its reason (reviewer-authored bytes must not hold a veto over the study). Round 2 verifies. |
| R1-16 | BLOCKER | CONFIRMED. Completed at every named site: §2's schedule fill and §5.2's analysis-set direction read N = 60; `stats.py`'s docstring and vector comment demote the n = 50 row to a port control with the study's N registry-held (R1-16 correction notes in place); `test_score_stats.py` binds `PINS.batch.n == 60` and renames its N-claims to the prototype's; `DEVIATIONS.md`'s unmarked N = 50 sentence is marked; the registry's order note records the 60-round re-derivation with the 50-round carry as history. |
| R1-17 | BLOCKER | — |
| R1-18 | BLOCKER | — |
| R1-19 | MAJOR | — |
| R1-20 | MAJOR | CONFIRMED — and the correction was wrong, not the original. `codex debug models --bundled` (the build-owned catalog) reproduces the pre-sweep figures exactly (max 3/8, defaults low×1/medium×7); the first correction had recounted a mutable post-call cache. Correction-of-correction in §2.1 restores the original figures with the provenance lesson ("build-owned means --bundled"), `sweep.settingsProvenance` carries the same restoration, and the load-bearing facts (universal four; gpt-5.6-sol default low) held through every version. |
| R1-21 | MAJOR | CONFIRMED. The corrected table is APPENDED to `design/BRIEF.md` as a marked correction section (historical bytes untouched, per the fix's own instruction), with the ~1% budget headroom consequence stated; `CORRECTION-TARGETS.md` records the venue. |
| R1-22 | MAJOR | — |
| R1-23 | MINOR | CONFIRMED. Every named site fixed: both front-door headers defer to the rendered sentence (revision ordinals kept for the cross-check); PREREG-REVIEW's "two registered facts" recast as the opening-state history they are; README's DEVIATIONS line names the operational record; `PINS.json`'s note reads the filled design-time pins and the open round; `integrity.py`'s freeze-pin comment counts eighteen with the two-move story (model left, censusStimulusCount arrived). |
