# Pre-freeze review record — Study 019

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here. The freeze requires a final round verdict of exactly
`freezable as written`.

## Round 1 — 2026-08-17

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, invoked over the repository worktree with the committed prompt on stdin.
- Clean HEAD read: `bf96915` (the round-1 prompt commit; working tree clean).
- Verbatim record: [`reviews/round-1/PROMPT.md`](reviews/round-1/PROMPT.md),
  [`reviews/round-1/REVIEW.md`](reviews/round-1/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 11 BLOCKER, 8 MAJOR, 1 MINOR (R1-1 … R1-20).
- Holdout: the reviewer states it is prepared to author the sealed reviewer mutant set in
  the designated later round, and authored none in this round.
- Reviewer verifications that PASSED and are part of this record: the seven two-sided
  PORTS rows recomputed and accepted (R1-20); the FM constants, equal-N critical levels,
  δ-power range, pilot-anchor power, unequal-N score formula, and the 48-step bisection
  all reproduced (R1-16); gold/grid/off-gold headline counts recomputed and confirmed
  (R1-19); references/oracle reproduce 105/105 and 2,540/2,540 outside X1 (R1-19).

### Dispositions (written 2026-08-18, after the response landed at `f00d097`)

Every disposition cites the test or artifact that enforces it; the response's suite of
record is **575 passed, 0 failed** with the pinned engines, and the 12-slot smoke re-ran
green with the fixes visible in its numbers (`harness/tests/E2E-SMOKE.md` §9).

| # | Sev | Disposition |
|---|---|---|
| R1-1 | BLOCKER | **Accepted, and this one could have decided R1 by arithmetic.** Cuts are per-language, derived from each language's own paired denominator in exact integers with `cut ≤ N` asserted (currently 72/75 JPS, 62/65 Rego at τ=0.95); identity-failing suites record `highKill: null`, never false. Enforced by `tests/test_score_e4.py` with the real current counts; pilot rescored (`design/mutants/E4-PILOT-v2.json`). |
| R1-2 | BLOCKER | **Accepted in part, and the premise corrected by measurement.** The probe construction the finding proposed is provably impossible (every Core connective is monotone in the information order, so a contradictory pair is never true) — but the finding's core claim stood: the inexpressibility was never a theorem. A region-scoped repair (`design/reference/refA/PACK-CHANGE-001.md`) realizes the prose on all 72 cells with zero collateral change over 236,196; **X1 is retired**. Enforced by the reissued certificate (0 divergences, `retired-x1-regression` record), `check_gold.py`'s empty exclusion registry that fails when the retired region is unwitnessed, and gold falsifier `x1r-adjacent-both-unreadable`. |
| R1-3 | BLOCKER | **Accepted, and closed at the cause rather than narrowed.** With X1 retired the registered exclusion set is empty in every consumer, so there is no asymmetric filter to apply; case-level domain validation is symmetric (arm A schema-total, B/C case inputs extracted mechanically from the test AST); the sanctions-absent stratum stays input-domain closure, not a second class. The certificate's class check is vacuous-true only at zero divergences. |
| R1-4 | BLOCKER | **Accepted, and it was a live hole.** Pre-call and post-call wrapper failures carry distinct statuses; every non-null code must be in the partition or the attempt refuses as pipeline-invalid; the finding's `set -e` post-call path is a named test case. `tests/test_batch.py` covers every wrapper exit path through the stand-in. |
| R1-5 | BLOCKER | **Accepted.** Full transcript binding runs on every scored slot with reasons mapped by cause — author protocol violations retained as authoring zeros, prompt/context/log corruption excluded as apparatus — with adversarial transcript tests on both branches. |
| R1-6 | BLOCKER | **Accepted.** Total matrixVersion-2 schema and domain validation; the finding's exact payloads (`[]`, `{"cases":[null]}`, string vendor) are test cases landing on the registered authoring code; the outer exception path is reserved for apparatus. |
| R1-7 | BLOCKER | **Accepted, and the smoke shows it.** The declaration schema, ledger chain, slot/seal bijection and registered prefix are validated on both sides; a declared-short batch branches to `UNRESOLVED-BY-DESIGN` with no endpoint computed (E2E-SMOKE §9); tampering tests refuse (`tests/test_score_attempt.py` — whose expected message fragments were realigned to the scorer's actual wording, recorded as an integration slip). |
| R1-8 | BLOCKER | **Accepted, including the taxonomy claim against our own notes.** Kills come only from machine-readable assertion failures (or scored-surface disagreement in arm A); mutant-side engine failures route to refusal, reference-side to identity apparatus refusal; nothing keys on exit codes, and the `opa test` exit taxonomy was re-verified against the pinned binary and corrected where our documents had it wrong (§2 of the preregistration carries the verified mapping). |
| R1-9 | BLOCKER | **Accepted.** `integrity.verify()`/`verify_manifest()` run before study-local imports are trusted; the manifest covers every scorer input with per-file hashes (mutant payloads, references, certificate, gold); `FREEZE_PINS` is complete (capabilities, model, golden, probe, isolation assent, attestation, reviewer set) with null→PILOT asserted pin-by-pin. |
| R1-10 | BLOCKER | **Accepted, and the omission was structural.** `--include-reviewer-set` is in the governing invocation and mandatory for REGISTERED, two-sided (REGISTERED without the flag refuses; the flag with any null pin refuses); loader validates without executing pre-attempt; the set executes exactly once at the primary attempt and publishes separately. |
| R1-11 | MAJOR | **Accepted, and the class was wrong by fourteen.** The dense census over the full space is now the only writer of `engineSuppliedKill` (27 true, was 41 gold-witness-scoped); the finding's worked example is among 20 engine-confirmed reclassifications; every valid record in both manifests carries the Boolean, with arm B's class registered explicitly empty. |
| R1-12 | MAJOR | **Accepted, and the byte-check caught a real defect.** `design/mutants/regenerate.py --check` regenerates end-to-end into a scratch copy and byte-compares; its first run exposed an absolute path embedded in an OPA error payload (fixed by scrubbing); now 186/186 and 371/372→identical, failing closed on undispositioned empties. |
| R1-13 | BLOCKER | **Accepted.** Direction comes from exact rates via the statistics layer; the finding's 6/50-vs-5/6 tuple is a named regression test. |
| R1-14 | MAJOR | **Accepted.** Publication is decision-gated: no contrast computation or printing below a failed gate row, positive registered minima, missing contrast lands on rows 1/2; both of the finding's scenarios are test cases, and the smoke's terminal row demonstrates the gate (§9). |
| R1-15 | MAJOR | **Accepted.** The residual "at the registered δ" is gone from §1; §1 and §5 agree verbatim that no decision anywhere reads δ. |
| R1-16 | MAJOR | **Accepted in the labeling branch.** What the study publishes is named an `exact-arithmetic mesh-inversion hull` with `levelCertifiedOverContinuum: false` and the inner-approximation direction stated; the exact-95%-CI claim is withdrawn rather than defended. Certifying the continuum stays open as possible future work, not a claim. |
| R1-17 | MAJOR | **Accepted as a registration decision (maintainer, 2026-08-18).** The A−C estimand is the bundled representation-plus-convention treatment; every formality-only claim is deleted and §1/§5/§9 prohibit component attribution within the bundle. B stands as the result-shape-only floor. |
| R1-18 | MAJOR | **Accepted, and the disclosure was owed.** The Design provenance section now states the pilot identity-control episode in full (all five arm-A suites failed the registered control; the quoted rates were off-protocol) and its repair; `E4-PILOT-v2.json` is the only cited pilot read (A 0.888 / B 0.902 / C 0.855; high-kill 1/5, 0/5, 0/5); R1 registers **no expected direction** and τ is stated as pilot-chosen and unanchored. The superseded artifacts are bannered, not deleted. |
| R1-19 | MAJOR | **Accepted.** Systematic state refresh across the preregistration and PINS prose; the counts the preregistration states are now read from the artifacts by `tests/test_prereg_currency.py`, so drift fails the suite instead of waiting for a reviewer. |
| R1-20 | MINOR | **Accepted.** The stale PORTS.md prose cells are corrected (seven ports, no "must grow"); the verified table cells are untouched. |

**Post-revision state.** Response landed as commits `f00d097` (269 files) plus this
record; suite 575/575 with pins; smoke third pass green with byte-identical rescoring; the
off-gold certificate reissued at 0/236,196; gold at 109 rows; the preregistration at its
third major revision with no expected direction registered for R1.

**Known-imperfect at this round's close, recorded rather than fixed:** the prose lane's
two server-error deaths mean its peripheral sweep (SCAFFOLD status lines, study README
wording) was finished inline by the maintainer and has had no independent read; the
E4-PILOT-v2 anchor rests on five suites per arm; and the OC table's power grid is now
deliberately unanchored to any operating point. Round 2 should read all three with intent.

## Round 2 — 2026-08-18

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as round 1.
- Clean HEAD read: `2c5f706` (the round-2 prompt commit; working tree clean).
- Verbatim record: [`reviews/round-2/PROMPT.md`](reviews/round-2/PROMPT.md),
  [`reviews/round-2/REVIEW.md`](reviews/round-2/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 7 BLOCKER, 7 MAJOR (R2-1 … R2-14).
- Disposition verification, the round's first job: **4 of 20 round-1 dispositions HOLD
  outright** (R1-4, R1-13, R1-15, R1-20, each verified against its cited test); the other
  16 spawned the R2 findings — in the pattern the program's history predicts: the fix
  holds where round 1 pointed, the generalization does not. Representative: the manifest
  was stale on the tree the round read (R2-1 — the maintainer's own post-verification
  commits re-staled it, which is precisely the defect class R1-9's fix exists to catch at
  attempt time, and precisely why `test_prereg_currency.py`-style enforcement must extend
  to the manifest); real OPA evaluation faults still enter kills on one path (R2-3);
  transcript verdicts are sealed but not consumed by population scoring (R2-5).

### The sealed reviewer mutant set — authored this round

Committed byte-for-byte as emitted, with attribution, under
[`controls/reviewer-mutants/`](controls/reviewer-mutants/): six single-edit mutants
(3 JPS, 3 Rego) plus the reviewer's `MANIFEST.json`, with its predictions registered in
the review prose (REVIEW.md, dated this round). **Two defects in the set as authored,
recorded rather than repaired, per the neither-side-edits rule:**

1. `rm-jps-03.json` does not hash to its manifest digest AND is refused by the pinned
   validator (`JPS-STRUCTURE-DECIMAL-OPERAND` at
   `/rules/12/…/conditions/1/value`) — the emitted bytes are evidently a pre-final draft
   of a payload the reviewer validated and hashed in its final form.
2. `rm-rego-01.rego` is valid but does not hash to its manifest digest (attestation
   error only; all four other payloads match their digests exactly and validate).

Neither payload nor manifest was edited by the maintainer. The set as it stands would be
refused by the loader (`e4lib/reviewer.py`) — correctly. **Round 3 asks the reviewer to
re-issue its own `rm-jps-03` payload and re-attest both digests**; the maintainer touches
nothing in the set.

### Dispositions

**Pending — no R2 finding has been dispositioned yet.**
