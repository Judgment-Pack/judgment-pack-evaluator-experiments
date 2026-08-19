# Pre-freeze review record — Study 019

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here. The freeze requires a final round verdict of exactly
`freezable as written`.

**The round-state block, and what reads it (round-7 findings R7-2 … R7-4, R7-7, and the
registered decision recorded in the round-7 section below).** The lifecycle of a round is
DATA, held once, here, in the fenced JSON block below: per round its number, its state
(`complete`, `awaiting-review`, `awaiting-response`), the verdict it returned, its severity
counts and its finding-id range. Three front doors — `README.md`, `PREREGISTRATION.md` and
`design/POLICY-DRAFT.md` — each carry ONE sentence rendered from this block by
`harness/render_round_status.py`, and `harness/tests/test_prereg_currency.py` requires that
rendered string of each of them VERBATIM. The block itself is cross-checked STRUCTURALLY
against the tree: the `reviews/round-N/` directories, each verbatim review's finding ids,
and this record's own disposition tables and severity columns. The prose tables below stay
for human readers and are no longer parsed for their meaning — the truth of free prose rests
where it rests in every predecessor study, on review. Run
`harness/render_round_status.py --write` when the block moves; the ceremony commit is then
mechanical.

<!-- ROUND-STATE-BLOCK
{
 "blockVersion": 1,
 "rounds": [
  {
   "number": 1,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 11,
    "MAJOR": 8,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 20
   }
  },
  {
   "number": 2,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 7,
    "MAJOR": 7
   },
   "findings": {
    "first": 1,
    "last": 14
   }
  },
  {
   "number": 3,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 3,
    "MAJOR": 6,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 10
   }
  },
  {
   "number": 4,
   "state": "complete",
   "verdict": "FREEZABLE AFTER LISTED FIXES",
   "severities": {
    "BLOCKER": 0,
    "MAJOR": 4,
    "MINOR": 2
   },
   "findings": {
    "first": 1,
    "last": 6
   }
  },
  {
   "number": 5,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 1,
    "MAJOR": 5,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 7
   }
  },
  {
   "number": 6,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 1,
    "MAJOR": 4,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 6
   }
  },
  {
   "number": 7,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 2,
    "MAJOR": 6,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 9
   }
  },
  {
   "number": 8,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 3,
    "MAJOR": 4,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 8
   }
  },
  {
   "number": 9,
   "state": "complete",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 2,
    "MAJOR": 4,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 7
   }
  },
  {
   "number": 10,
   "state": "awaiting-review",
   "verdict": null,
   "severities": null,
   "findings": null
  }
 ]
}
ROUND-STATE-BLOCK -->

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

### Dispositions (written 2026-08-18, after the response landed; suite of record 669/669
with the pinned engines after the final manifest/ownPorts reconciliation)

| # | Sev | Disposition |
|---|---|---|
| R2-1 | BLOCKER | **Accepted, both halves.** The manifest is regenerated last and now double-gated: a stale manifest fails the suite itself (`test_prereg_currency.py::test_the_committed_manifest_is_current_with_the_tree`) instead of waiting for a reviewer. The regeneration record is re-run green at 372/372 across both arms with `armsCovered` stamped, and a single-arm check can no longer write the committed record. |
| R2-2 | BLOCKER | **Accepted, in the direction the registration requires.** The primary scorer held the registered denominator rule; the pilot layer disagreed and was changed to match it — never the reverse. `denominatorRule` is published, identity failures carry `highKill: null`, and the reviewer's two-run probe is a verbatim test asserting 1/2. |
| R2-3 | BLOCKER | **Accepted for the path; corrected on the pilot claim.** The fault path was real and is closed: every reported `opa test` failure is adjudicated by a strict-builtin re-query (`engines.evaluation_fault()`), faults refuse rather than kill, unreadable adjudications fail closed, all engine-tested. On the claim that the *current pilot* credits faults as kills: `E4-PILOT-v3.json`, regenerated under the corrected semantics, is numerically identical to v2 — the leak existed and no pilot suite happened to exercise it. Recorded as found, not rounded in either direction. |
| R2-4 | BLOCKER | **Accepted, both constructions.** Presence is decided by key membership (explicit null refused in both wire forms, 5 axes tested), and enumeration is per `with input as` term with resolution through bindings and call sites — the decoy-literal certification path is deleted, and the reviewer's decoy suite is a named engine-backed test. All ten real pilot suites still enumerate under the per-term rule. |
| R2-5 | BLOCKER | **Accepted, and it surfaced a second defect.** The scorer recomputes the transcript verdict from sealed bytes through the driver's own binding and files its registered code; an unclassified refusal terminates. Found while fixing: author protocol violations wrote no completion and were being filed as apparatus `slot-shape` — deleted from the very denominators §3's no-tools rule exists to police. An authoring verdict now outranks a missing completion; seven adversarial-transcript cases enforce both. |
| R2-6 | BLOCKER | **Accepted, both directions.** The loader accepts exactly the matrix the prompt instructs (string `"2"`, refusal naming the integer misreading), and every nested member is typed so the reviewer's `reasons: 1` lands on the authoring code instead of a `TypeError`. A pinned-parser test reads the assertion out of the arm-A instructions and loads a real pilot matrix. |
| R2-7 | BLOCKER | **Accepted.** The loader enforces the authored schema (cardinality, both languages, exact members, filename-extension consistency) and real-path containment closing the absolute-path escape; set load/validate precedes any endpoint and failure is terminal — proven against the really-committed digest-defective set. |
| R2-8 | MAJOR | **Accepted, with the residue stated in code rather than prose.** `integrity.verify()` is now the first study-local call (order-asserted by test), and a pre-verification failure no longer binds the tree. The honest limit is written where it lives: the scorer and integrity module execute before either can check anything — a gate against drift, not a root of trust. |
| R2-9 | MAJOR | **Accepted.** The registered empty-prefix representation round-trips driver-to-scorer, and an empty declaration over a tree that carries a ledger refuses. |
| R2-10 | MAJOR | **Accepted.** `engineSuppliedKill` is fail-closed: strict booleans on every valid record, partial or mistyped censuses refuse by name, and the test that tolerated partial marking is reversed. |
| R2-11 | MAJOR | **Accepted.** The closure check reads the tree under check; the reviewer's scratch-only empty-witness scenario is the regression, asserted on the reported list. |
| R2-12 | MAJOR | **Accepted in the code-side option.** No interval is computed anywhere until the outcome has passed the gate rows; blocked intervals publish their cause, and the reviewer's probe interval is asserted absent from the failed-gate output. |
| R2-13 | MAJOR | **Accepted, at the generator.** `oc_table.py` itself no longer emits the withdrawn exactness vocabulary, reads the current pilot file through one constant, and rebuilds its anchor section from the registered surface — so regeneration can no longer resurrect a corrected claim. |
| R2-14 | MAJOR | **Accepted.** The README states the registered question, the bundle prohibition, the two DO-NOT-FREEZE verdicts, and the no-direction registration; the X1 and formality-only residuals are swept from every reader-facing file with the sweep's grep list recorded, and README claims are now themselves under test. |

**Also found and fixed by the response, not by the review:** `opa test --format json`
does not order its result list, which made the pilot regeneration nondeterministic —
adjudication and error lists are now sorted, v3 verified byte-identical across two full
regenerations. Recorded so the determinism claim stays measured rather than assumed.

**Post-revision state.** Suite 669/669 with pins after the final reconciliation (the
three failures both lanes deliberately left for the maintainer's ordered
manifest/ownPorts step). The sealed reviewer set remains exactly as authored, defects and
all — its repair is the reviewer's, in round 3.

## Round 3 — 2026-08-18

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape.
- Verbatim record: [`reviews/round-3/PROMPT.md`](reviews/round-3/PROMPT.md),
  [`reviews/round-3/REVIEW.md`](reviews/round-3/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 3 BLOCKER, 6 MAJOR, 1 MINOR (R3-1 … R3-10).
- Disposition verification: **7 of 14 round-2 dispositions hold** (several
  execution-qualified — the reviewer's read-only sandbox cannot run writable-tree tests);
  six over-claim, spawning the R3 findings. The three blockers, plainly: **R3-1** the
  round-2 record's "suite of record 669/669" is false *for the committed tree* — the
  maintainer's own dispositions edit re-staled the manifest a third time (the structural
  cause: `PREREG-REVIEW.md` is appendable by design yet manifest-covered — the exact
  ADR 0004 class, whose root fix belongs to the response); **R3-2** the round-2 "adequacy:
  accepted, both halves" over-claimed — the reference repair regenerated the mutant
  corpora and left **71 new empty-witness mutants (37 JPS, 34 Rego) undispositioned**, so
  the adequacy gate is genuinely re-open and the regeneration record's `pass:false` says
  so; **R3-3** mixed OPA failure lists stop adjudicating at the first genuine assertion
  failure, so a fault later in the list still kills — with the existing test blessing the
  early stop.
- **The sealed set is repaired, by the reviewer, as the record required**: the re-issued
  `rm-jps-03.json` (16,700 bytes) hashes to the reviewer's *original* round-2 attestation
  — establishing that the round-2 digest was correct and the pasted payload was a
  pre-final draft — validates against the pinned jpack, and per the reviewer's dated
  statement preserves the registered probe intent exactly (optional insurance made
  globally required, nothing else). The corrected `MANIFEST.json` re-attests all six
  payloads; **all six digests now verify**, and `rm-rego-01`'s attestation is corrected to
  its emitted bytes. The maintainer extracted both byte-for-byte; nothing else in the set
  changed.

### Dispositions

(Written 2026-08-19, after the response landed. Suite of record 708/708 with the pinned
engines, `manifest_problems()` empty re-checked after the suite, the regeneration record
independently re-run to `pass: true` at 375/375, and the whole response verified from the
reconciled tree. This table is appended to a manifest-excluded record — the R3-1 fix —
so writing it stales nothing.)

| # | Sev | Disposition |
|---|---|---|
| R3-1 | BLOCKER | **Accepted at the root.** `PREREG-REVIEW.md` is excluded from the manifest's covered set by named constant with an asserting test, per ADR 0004 — the record is appendable by design and can no longer stale the manifest, which had now bitten three times. The final reconciliation regenerated the manifest last; `manifest_problems()` is empty after the suite ran. |
| R3-2 | BLOCKER | **Accepted; the cascade re-ran end to end.** All 71 empty-witness mutants of the repaired corpus disposed: 8 new prose-derived gold rows (gold 109 → 117, every row's note naming its deriving sentence; both engines and the clean-room oracle reproduce 117/117 on the first run) kill 11; 26 + 34 registered drops with mechanisms, zero undispositioned. The arm-A drop table was re-derived rather than re-keyed — three surviving ids named different edits, and one old drop (`m-a-088`) is in fact killable and now killed. The adequacy stamp moved inside the regeneration chain, so the defect class that let a stale DROPS table survive a corpus regeneration is closed structurally; `--check` is green at 375/375 for the first time in its history. New drop class `subsumed-region-lemma` (9 mutants) recorded as the X1 repair's measured price. Two prose flags raised and recorded, not resolved (A5: one kill rests on the literal "O1 suspends D6c and only D6c" reading; A6: the region lemma is entailed but never stated). |
| R3-3 | BLOCKER | **Accepted.** Every reported failure is adjudicated; any evaluation fault or unreadable adjudication refuses the invocation regardless of genuine assertion failures elsewhere; the early-stop blessing test is reversed, and the reviewer's mixed two-failure probe runs in both lexical orders. |
| R3-4 | MAJOR | **Accepted, and the pilot now says something new.** The pilot path consumes the harness's own domain/identity code — one path, not two. E4-PILOT-v4, re-issued through it: arm C identity drops from 5/5 to **1/5** — four pilot runs authored out-of-domain cases, all omitting the screening result the registered domain closure requires (three also passed a term with no vendor member). Arm A 5/5, mean paired 0.878, high-kill 1/5; arm B 5/5, 0.897, 0/5; arm C **five admitted runs, one of them identity-passing** — 0.806 is that one run's paired rate, and arm C's high-kill fraction is 0/5 over the five (corrected 2026-08-19 under round-4 finding R4-4; this row previously reported the identity-passing cohort's size as though it were the admitted one). Published prominently, old beside new; byte-identical on a second full scoring. The domain closure's bite on real authored suites is now a measured design fact, not a surprise waiting for the batch. |
| R3-5 | MAJOR | **Accepted.** Reciprocal supersession: every superseded pilot issue names its successor, v4 names what it supersedes, and the currency test walks the chain (single terminus, no forks, no cycles, reciprocity) instead of matching spelling. |
| R3-6 | MAJOR | **Accepted.** The OC generator reads its denominator off the pilot's published `highKill` block; the D3 question is closed denominator-in; the identity-attrition language is gone; one test asserts the mixed 1/2 rule semantically across scorer, pilot, and OC. |
| R3-7 | MAJOR | **Accepted.** §7's import-before-integrity sentence is withdrawn for the honest bootstrap limitation — the scorer and integrity module execute before either can check anything, a gate against drift, not a root of trust — and the clause is frozen by a test that re-derives it from `score.py`'s own imports. |
| R3-8 | MAJOR | **Accepted.** §10 and §5 reconciled: what exists is published; a blocked contrast is published as blocked, with its cause; the late secondary-contrast residual lands on the registered row and is tested. |
| R3-9 | MAJOR | **Accepted (code half in the response's code lane).** The README/currency tests that tolerated contradictory X1 output fields are tightened to fail on the contradictions they tolerated, and the documents now pass the tightened tests. |
| R3-10 | MINOR | **Accepted.** Both status headers rewritten under exact latest-round/revision tests; this record's round count and open-round state are themselves under test. |

**Also recorded from the response, beyond the findings:** the adequacy lane's OOM
diagnosis (14 concurrent OPA sweeps; the runner now reports exit status and the
killed-process signature), and one known-imperfect left deliberately: `regenerate.py`'s
`build_report` note is imprecise about the adequacy stamp's derivation and was not edited
because editing it would make the committed record unreproducible by its own generator —
it is rewritten at the next full `--check`.

## Round 4 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as rounds 1–3.
- Clean HEAD read: the round-4 prompt commit; working tree clean.
- Verbatim record: [`reviews/round-4/PROMPT.md`](reviews/round-4/PROMPT.md),
  [`reviews/round-4/REVIEW.md`](reviews/round-4/REVIEW.md).
- Verdict: **FREEZABLE AFTER LISTED FIXES** — the first non-DO-NOT-FREEZE verdict of the
  regime. 0 BLOCKER, 4 MAJOR, 2 MINOR (R4-1 … R4-6).
- Round-3 disposition verification: 7 hold, 2 partial (R3-2's lemma description and class
  attribution — R4-1/R4-2; R3-6's OC header — R4-5), 1 fails (R3-10: the front doors
  still call round 3 open after the table landed — R4-3).
- Prose flags A5/A6: the reviewer's reasoned answer is that **neither requires a prose
  amendment** — the recorded flags plus both-engine and clean-room-oracle agreement are
  sufficient for a frozen reader, and "A5/A6 add nothing" to the freeze-distance list.
- The reviewer's complete freeze-distance list, in dependency order, is quoted verbatim
  in the review and adopted as the response plan: (1) R4-1/R4-2 corrected at the adequacy
  source with the cascade re-run; (2) pilot and OC reissued, R4-4/R4-5 generator fixes,
  preregistration updated only after the derived surfaces settle; (3) R4-3/R4-6 —
  stable headers, the Study 019 CI job, stale lifecycle claims reconciled, and a fresh
  full pinned suite (708/708 is not to be reused); (4) the registered operational gates
  against the final prose: the clean-room re-run and the freeze-commit off-gold
  certificate.

### Dispositions

(Written 2026-08-19, after the response landed. The suite of record is stated at the
end of this section, freshly run from the settled tree: the round-3 count of 708/708 is
**not** reused, on the reviewer's instruction and for the reason R4-3 gives — a suite
count describes the tree it ran on, and this response changed the tree after it.)

**Corrected 2026-08-19 under round-5 finding R5-1, in place and marked.** The sentence
above promised a suite of record at the end of this section and the section ended without
one; no count for the round-4 response is recorded here, and none is added now, because
none would be true. The reviewer's own controlled run over the round-4 commit collected
**723 tests: 697 passed, 25 engine-backed tests skipped for absent pinned binaries, and 1
failed** — the lifecycle test, on the `__pycache__` the response had committed — so the
tree this section describes did not have a passing suite and `integrity.py` refused it on
a fresh checkout. The round-5 response's count, over the tree that carries the R5-1 fix,
is at the end of the round-5 section below.

| # | Sev | Disposition |
|---|---|---|
| R4-1 | MAJOR | **Accepted, and the lemma is now described by its own measurement.** The finding is exactly right: `m-a-183` holds — no cell's ANSWER changes — but "0 live-edit cells" was never what was measured. Deleting a rule removes its trace entry, so the edit is live at **419,904 of 419,904** cells, and the three metrics that matter are now published separately and everywhere: **419,904 trace-live cells; 0 scored-surface differences** (primary transcription, and the second independent one in `adequacy_crosscheck.json`); **120 pinned-jpack samples, 0 differences**. Corrected at the GENERATOR — `adequacy_search.py`'s `DROPS` entry, which is the source the stamped `refA/MANIFEST.json` mechanism is written from — then restamped and re-run, never hand-edited in the generated manifest. Enforced by three cross-artifact tests in `test_prereg_currency.py`: no drop mechanism and no ADEQUACY.md sentence may claim zero live cells where `adequacy_drops.json` measured more (a window search, not a banned string — the false sentence was spelled two different ways), and the deletion lemma's description must carry all three measured numbers, each read out of the artifact at test time. |
| R4-2 | MAJOR | **Accepted, and the attribution is now derived rather than asserted.** Nine is the class; six is the repair's marginal price. The three the reviewer names reproduce exactly: current `m-a-017`, `m-a-077`, `m-a-079` are the pre-repair `m-a-017`, `m-a-067`, `m-a-069`, dropped then as `same-outcome-overlap`. `adequacy_search.py --region-lemma-price` derives the split from the stamped manifest's edits and the committed 2026-08-15 table, **matched by edit rather than by id** (ids do not carry across the repair — the hazard round 3 was caught by), writes `adequacy_region_lemma_price.json`, and runs **inside the regeneration chain**, so drift in either input fails `regenerate.py --check`. The boundary over-claim is corrected with it: an edit is invisible only while the cells it moves stay inside a region another rule already answers `review`, and the one that leaves it — `m-a-076`, risk 40 → 39, into D6a's approval region — is killed. `ADEQUACY.md`, `PREREGISTRATION.md` §4/§9 and `POLICY-DRAFT.md`'s V8 row all carry gross-and-marginal now; two tests re-derive the split independently and a third forbids the "every boundary edit is invisible" claim in any of them. |
| R4-3 | MAJOR | **Accepted, and the test that failed is the one that was too weak.** R3-10's tests asserted the round COUNT and the ABSENCE of a stale "round N's findings are open" — so "all three returned DO NOT FREEZE" survived a fourth round with a different verdict, and the preregistration header could name a round without describing it. Both headers are rewritten from the record's final state, and the state testing is extended to **both** of them and made positive: every distinct verdict on the record must appear in both headers; both must name the latest round; a dispositioned round may not be called open in either; an **undispositioned** round must be called open in both; and the record's own round sections may not carry the "no R*N* finding has been dispositioned yet" sentence beside a disposition table. The full pinned suite was run only after this table and the header rewrite landed. |
| R4-4 | MINOR | **Accepted, at the generator, and the numbers are read off the arm now.** Five arm-C runs are admitted; one passed. The v4 banner is rebuilt from `perArm.C` — `"%(admitted)d runs, of which %(identityPass)d passed"` — so the cohort sizes cannot be spelled wrong again, and it states plainly that the identity counts are over the admitted cohort and the kill rates over the passing one. `pilot_anchor()`'s "the current pilot records identityFail: 0 in all three arms" is corrected (it described v3) and the two cohorts are defined in its docstring without numbers. The obsolete statistics test is recast as the arithmetic boundary case it always was, with its former "pilot anchor" framing and the three-issues-stale A 1/5, C 5/5 figures removed. `E4-PILOT-v4.json` was regenerated from the corrected generator: **the only leaf that changed is `supersedingBanner`** — every measured value is byte-identical — so v4 is corrected in place and remains the terminus; no supersession event occurred and the chain is untouched. The stale sentence in this record's own R3-4 row is corrected above, in place, with the correction marked. |
| R4-5 | MINOR | **Accepted, at the generator, and the state is now parsed rather than banned.** `oc_table.py` carries one defect register (`DEFECTS`), and the opening summary, §9's heading and each entry's bold lead-in are all rendered from it — so the two surfaces cannot disagree, and if a defect is ever reopened the opening paragraph says so without anybody remembering to edit it. The retained D3 question moves into `### D3 as the gate originally put it -- ARCHIVED`, stated wholly in the past tense and headed "Nothing in this subsection is open". `OC-TABLE.md` regenerated. The currency test now parses the D1–D3 statuses out of the document and compares them to the generator's register and to what both surfaces say, instead of excluding two exact phrasings the document had already got past. |
| R4-6 | MAJOR | **Accepted; the registered enforcement now exists.** `study-019-harness` is in `.github/workflows/ci.yml` between Study 018's job and the general Python matrix, in the file's idiom: the workflow's own pinned action SHAs, the interpreter `3.12.11` (corrected 2026-08-19 under round-5 finding R5-5: this row said `PINS.json` records the patch level and it does not — the registry pins the CPython **3.12 series** and `verify_interpreter()` compares implementation and series only, by Study 012's round-3 finding 20, so the exact patch in CI fixes the runner for reproducibility and refuses nothing), pytest-only install, `working-directory: studies/019-authorship-across-representations`, `python harness/integrity.py` under `PYTHONSAFEPATH=1` and `python -m pytest harness/tests -q`, both under `PYTHONDONTWRITEBYTECODE=1` (T4), and a comment stating in the file that the matrix adjudication is an ATTEMPT, never a test, and never runs there. A test asserts the job and its shape, so deleting the scaffold at freeze does not take the requirement with it. The stale lifecycle claims are reconciled at all four places the reviewer names — `SCAFFOLD.md` (T3 and §C marked LANDED; "T3 alone remains" withdrawn), `batch.py`'s tripwire docstring, `PINS.json` (the scorer is assembled; the gold note said 109 rows for a 117-row suite) and `e4lib/census.py` (its §5 quotation elides the row count rather than restating it) — and a test asserts both the absence of those claims and the tree condition they were about: no untracked Python source, no `__pycache__`. |

**Post-revision state.** The adequacy cascade re-ran end to end: `regenerate.py --arm both
--check` is **376/376 byte-identical** with `pass: true` and 0 undispositioned
empty-witness mutants in both arms (375 before; the extra file is the new derived
`adequacy_region_lemma_price.json`, which is inside the chain rather than beside it). The
two-way drop registry is unchanged at 60 empty-witness / 60 registered / 0 unregistered /
0 stale; the stamped manifests, arm A's REGISTRY and the pairing report are byte-identical
to their committed selves apart from `m-a-183`'s corrected mechanism. `OC-TABLE.md` and
`E4-PILOT-v4.json` were regenerated from their corrected generators.

**Also closed, from round 3's known-imperfect list rather than from a finding:**
`regenerate.py`'s `build_report` note said the adequacy stamp was something "this command
may not invent", which round 3 left alone because editing it would have made the committed
record unreproducible by its own generator. This response re-runs the full `--check`, which
is the moment round 3 named for the rewrite, so the note is corrected in the same run that
rewrites the record.

**Known-imperfect at this round's close, recorded rather than fixed:** the pilot
regeneration is not covered by a test (it costs three minutes of pinned-OPA time per run),
so its determinism is a measured fact from this response's two runs and not a standing
assertion; and `adequacy_region_lemma_price.json`'s pre-repair half is derived from a
markdown table in `ADEQUACY.md`, which is a committed record but not a machine artifact —
the parse is strict and fails loudly, and that is the whole of its protection.

## Round 5 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as rounds 1–4.
- Clean HEAD read: the round-5 prompt commit.
- Verbatim record: [`reviews/round-5/PROMPT.md`](reviews/round-5/PROMPT.md),
  [`reviews/round-5/REVIEW.md`](reviews/round-5/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 1 BLOCKER, 5 MAJOR, 1 MINOR (R5-1 … R5-7). The verdict
  regressed from round 4's `freezable after listed fixes`, and the blocker is the
  maintainer's own commit hygiene: a bytecode file (`harness/__pycache__/…pyc`) was
  committed with the round-4 response — written by a post-suite `manifest_problems()`
  import that ran without the no-bytecode flag, after the tree-condition test had already
  passed — so `integrity.py` refuses committed HEAD and the 723/723 claim does not
  describe it. The remaining findings are residuals of the round-4 fixes: guards binding
  one claim but not its sibling (R5-2), header enforcement not per-round (R5-3), one
  internally false generator sentence (R5-4), CI enforcement not robust to the scaffold's
  registered deletion (R5-5), `--freeze` not walking the payload-set globs (R5-6), and
  the POLICY-DRAFT lifecycle prose round 4 explicitly ordered reconciled (R5-7).
- Round-4 disposition verification: 1 holds (R4-5), 4 partial, 1 fails (R4-6).

### Dispositions

(Written 2026-08-19, after the response landed. Every python invocation in this response —
pytest, the manifest check, integrity, the generators — ran under `PYTHONDONTWRITEBYTECODE=1`,
because R5-1 exists precisely because one post-suite import did not.)

| # | Sev | Disposition |
|---|---|---|
| R5-1 | BLOCKER | **Accepted; the commit is the finding and the class is closed four ways.** Reproduced first: `git archive HEAD` of the study into a scratch tree and `integrity.py` refuses it — `harness/__pycache__/make_manifest.cpython-312.pyc: stale stamp`. It passed in the working tree only because the cache happened to be fresh against the mtime of the source beside it, which is the property no checkout after the writing machine's own can have; the validating gate is the right rule for a working tree and the wrong one for the index. The cache is `git rm --cached`-ed and deleted, and `git ls-files` over the whole study tree confirms it was the only one. **(a)** `tests/test_manifest.py::test_the_committed_study_tree_tracks_no_bytecode` reads `git ls-files`, so it binds the INDEX — the retained R4-6 test walks the WORKING TREE, which is a different claim and the one that passed while the `.pyc` sat in HEAD. **(b)** The study root gains the repository's house `.gitignore` (`__pycache__/`, `.pytest_cache/`) — studies 011–018 all carry exactly it; 019 did not, which is how an ordinary `git add -A` staged one — asserted by test against the house pattern. **(c)** `make_manifest.tracked_bytecode()` reports it as a manifest problem and `--freeze` refuses on it, and `integrity.verify_bytecode()` refuses a TRACKED cache unconditionally, before any freshness question. Both read the index, so a cache deleted from disk and left committed is still refused — that case is a named test. **(d)** §7's `GATE(pre-freeze)` sentence, which said the stale caches "must be committed", is rewritten and is now on the stale-lifecycle register. Mutation-checked in both directions: an index-reading check made to walk the working tree fails the new test, and the pre-fix `pending`/problem paths fail it too. |
| R5-2 | MAJOR | **Accepted, and the finding is exactly right about which number was bound.** The measurements are correct and unchanged; what was missing was the binding. The positive lemma guard required the live-cell count and the engine sample size and nothing else, so replacing both reader surfaces with seven scored and seven engine differences passed all three R4-1 tests. It now reads **five** values out of `adequacy_drops.json`, `adequacy_search.json` and `adequacy_crosscheck.json` at test time and binds them in both directions: no block about `m-a-183` on either surface may state a difference count the measurement denies (the seven-difference mutation now fails by name), and at least one block on each surface must carry the whole description — the trace-live count, the scored surface identical on BOTH transcriptions, and zero differences over the pinned-engine sample — with the search done per PARAGRAPH rather than per fixed-width window, because the sentence that carries the three metrics is longer than the window was. On R4-2's half: the "second independent re-derivation" was a document-wide search for nine and six that skipped any document not quoting the class, so "nine marginal, none pre-existing" plus an unrelated six passed. Each of the three registered surfaces is now required to state the split in its ROLES — the marginal count attributed to the repair, the pre-existing count withheld from it — parsed by adjacency inside the sentences that state the class size, with every role statement in the document checked and not just one; and `ADEQUACY.md` must name all six marginal ids and all three pre-existing ones with their pre-repair ids, read from the derived artifact. Both of the reviewer's mutations fail; no prose needed changing, which is the finding's own point. |
| R5-3 | MAJOR | **Accepted, per round and per finding.** `_round_records()` now parses each round's registered finding set from the record's own verdict line — whose severity counts and id range are two independent statements of the same number — and cross-checks it against the ids the round's verbatim `reviews/round-N/REVIEW.md` carries; all five rounds agree three ways. A round counts as dispositioned only when its disposition-id set EQUALS its finding set, so the reviewer's two-finding round with one row is an open round and the headers must say so. Verdicts are no longer required merely to occur: both headers are parsed for affirmative `round(s) N returned <verdict>` clauses, ranges and lists expanded, and the resulting map must equal the record's — a synthetic round repeating an earlier verdict without being named fails. The round set is also derived from the `reviews/` directory and compared to the record, so a round can enter neither surface silently. |
| R5-4 | MINOR | **Accepted, at the generator, and it was three sentences of one mistake.** `pilot_anchor()`'s docstring called the anchor a fraction of "scored runs" (the denominator-OUT reading round 3 removed from the code), said zero identity failures were true of no arm while A and B record zero, and said an identity failure makes the registered denominator SMALLER than the identity-passing count when it makes it larger. All three corrected, and the arithmetic stated once in the form that cannot be spelled wrong — ADMITTED = IDENTITY-PASSING + IDENTITY FAILURES — beside the current pilot's own three rows: **A 5 admitted, 0 identity failures, 5 identity-passing; B 5 admitted, 0 identity failures, 5 identity-passing; C 5 admitted, 4 identity failures, 1 identity-passing**. That sentence is REBUILT from `E4-PILOT-v4.json` by `tests/test_prereg_currency.py` and required verbatim, so a reissued pilot moves it or fails the suite, and each of the three false sentences is separately forbidden against what the artifact says. `OC-TABLE.md` regenerated from the corrected generator: **byte-identical**, as expected — the defect was in the docstring, not in a rendered line. |
| R5-5 | MAJOR | **Accepted, all three residuals.** (1) The lifecycle guard opened `SCAFFOLD.md` unconditionally and the scaffold's own step 9 deletes it in the first post-freeze commit, so the registered freeze broke the test that enforces the scaffold's closed items. The register is now data, with `SCAFFOLD.md` named as the one file deleted at the freeze; a new test applies the register to a scratch post-freeze tree with the scaffold removed, then proves it still bites on what remains and still fails on an UNREGISTERED disappearance. (2) The job test was raw substring matching and a comment-only fake passed it. `ci.yml` is now PARSED — comments stripped, `jobs:` mapping read, steps and their `env` blocks read — and the job must define a runner, a single setup-python whose version is a patch of the registered series, and exactly one step for each of the two commands with the right `working-directory` and the right environment. The reviewer's own mutation is a test: the real job commented out in its entirety no longer parses as a job, while every substring the old test looked for survives it. The requirement lives entirely in a test that reads `ci.yml` and no other file, so the scaffold's deletion cannot take it. (3) The exact-patch rationale was false — `PINS.json` registers the CPython **3.12 series** and `verify_interpreter()` compares implementation and series only (Study 012's round-3 finding 20 keeps the patch reported and not required). The workflow comment now says what is true: 3.12.11 fixes the CI runner for reproducibility and refuses nothing. A test reads the registry's `python` member and fails if the workflow claims an enforcement the registry does not carry — including if a patch level is ever registered, which moves both together. The R4-6 row above is corrected in place and marked. |
| R5-6 | MAJOR | **Accepted, at the gate rather than at the scorer.** `pending_documents()` walks `REGISTERED_PAYLOAD_SETS` now, and a set is pending while its root is ABSENT or its glob is EMPTY — two different mistakes, reported separately, both blocking. The reviewer's residual is a test over a scratch tree: every registered document present, both mutant payload roots absent, `--freeze` refuses and writes nothing; roots created and left empty, `--freeze` still refuses; roots filled, `--freeze` succeeds and the written manifest carries the payloads file by file. Mutation-checked by removing the payload half of `pending_documents()`, which fails three tests. `SCAFFOLD.md`'s freeze-fill step 2 names both payload trees explicitly, and a test asserts it does — skipping only once the scaffold is deleted, which is its registered lifecycle. |
| R5-7 | MAJOR | **Accepted, and the recurrence is why it is now derived rather than reconciled.** `POLICY-DRAFT.md` said two review rounds had run and both had returned DO NOT FREEZE — through rounds 3, 4 and 5, and after round 4 explicitly ordered it reconciled. The paragraph now states five rounds with the per-round verdicts, and it is under the header machinery: the COUNT is derived from the `reviews/` directory and the VERDICTS are parsed by the same affirmative-attribution parser the two front doors are held to, then compared to the record. Its "Still open for gold authoring" heading is reconciled too — gold IS authored; V7 and V8 are the verification items that remain, and the heading says that now. `PREREGISTRATION.md` §7's 375/375 is corrected to **376/376** and the count is read out of `REGENERATION-CHECK.json` at test time, in both of the forms the document uses it. |

**Post-revision state, and the suite of record.** The full pinned suite, run last from the
settled tree — after every disposition, header, prose, ports and manifest edit — is
**739 passed, 0 failed, 0 skipped** with `JPACK_BIN`, `OPA_BIN` and `OPA_CAPS` on the
pinned binaries, so the 25 engine-backed tests the reviewer's sandbox had to skip ran here.
The round-4 count of 723 is not reused, for the reason R4-3 gives and R5-1 proves. Order of
the reconciliation: code and prose first, then `harness/PORTS.md`'s two destination digests
(`integrity.py`, `make_manifest.py` — the two ported files this response edited), then
`ownPorts.sha256`, then `make_manifest.py` LAST; `integrity.py` returns clean at 7 ported
files and `manifest_problems()` is empty re-checked after the suite, under
`PYTHONDONTWRITEBYTECODE=1`. `OC-TABLE.md` regenerated byte-identical from its corrected
generator.

**The R5-1 verification, stated as it was run.** The failure was reproduced before it was
fixed: `git archive HEAD` of the study into a scratch tree, where `integrity.py` refuses
with `harness/__pycache__/make_manifest.cpython-312.pyc: stale stamp` — the round-4 tree as
any checkout but the writing machine's own sees it. The same archive of the corrected tree
verifies. `git ls-files` over the study is clean of `__pycache__`, `.pyc` and `.pyo`, and
the tracked-cache refusals are mutation-checked: an index-reading check rewritten to walk
the working tree fails the new test, which is the whole distinction the finding turns on.

**Known-imperfect at this round's close, recorded rather than fixed:** the two front doors'
verdict attribution is parsed from an English clause shape (`round(s) N returned <verdict>`)
— a header that states the same mapping in some other form would fail a true statement, and
the answer if that ever happens is to widen the parser rather than to loosen it; and
`POLICY-DRAFT.md`'s V7 and V8 remain open verification items, now labelled as such rather
than as gold authoring, which is a heading correction and not a closure.

## Round 6 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as all rounds.
- Clean HEAD read: the round-6 prompt commit (`33a3eed` + the prompt commit).
- Verbatim record: [`reviews/round-6/PROMPT.md`](reviews/round-6/PROMPT.md),
  [`reviews/round-6/REVIEW.md`](reviews/round-6/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 1 BLOCKER, 4 MAJOR, 1 MINOR (R6-1 … R6-6).
- The blocker (R6-1) has three parts, two of them the maintainer's process and one
  structural: the round-5 response's `ci.yml` correction was left unstaged by the
  maintainer's study-path-only commit, so HEAD carries the false interpreter rationale
  its own test forbids; and the per-round lifecycle test defines a completed round by raw
  directory equality, so the act of committing a round's prompt — required by the regime
  before the reviewer reads — makes HEAD red by construction. The reviewer's fresh
  `git archive HEAD` suite: 736/3/0 against the recorded 739/0/0.
- R6-2 … R6-6: the currency guards remain defeasible where they parse prose — negated
  verdict sentences accepted, blank/PENDING disposition cells counted, a `if: false` CI
  job passing the shape test, sentinel payloads satisfying the freeze closure, and a
  truncated-document guard that never reads the heading it protects.
- Round-5 disposition verification: R5-4 holds; R5-1 holds for bytecode with the class
  regressed one level up; the rest partial or failing on HEAD.

### Dispositions

(Written 2026-08-19, after the response landed. Every python invocation in this response —
pytest, the manifest check, integrity, the generators — ran under `PYTHONDONTWRITEBYTECODE=1`.)

**The method this round changed, stated once because it is the answer to five of the six
findings.** The reviewer has now defeated a prose-parsing currency guard three rounds
running: R4-1's window, R5-2's noun-anchored count, R5-3's clause shape, R5-7's truncated
read. The lesson is not that the regexes were too narrow. It is that a POSITIVE attestation
must not be a search over free prose at all. So wherever a guard attested something this
round, the guarded sentence became a machine-readable form the document reproduces from
data — the lemma's three outcomes, the class split, the round's state — and where a guard
still reads prose it reads a STRUCTURED surface (the disposition table's cells, a workflow's
parsed job, a heading line) with a shape requirement and enclosing-negation rejection.
Window searches are retained for BANNED-claim detection only, where a false negative costs
a missed offender rather than a false attestation.

| # | Sev | Disposition |
|---|---|---|
| R6-1 | BLOCKER | **Accepted in all three parts, and the third is a defect in the model rather than in the tree.** (a) The round-5 response's `ci.yml` correction was left unstaged by a study-path-only `git add`; it is committed with the round-6 record at `10b0f66`, which is why the false-rationale test the reviewer saw fail is green at the HEAD this response answers. (b) The suite of record is re-established by the archive method below and reported both ways. (c) The structural half: `_round_records()` decided a round was completed by raw directory equality against `reviews/`, so the regime's own opening move — commit round N's PROMPT, then let the reviewer read committed HEAD — made HEAD red by construction, and no wording of the front doors could have made it green. A round is now a STATE read from its four artifacts (prompt, verbatim review, record section, per-finding disposition cells): `complete`, `awaiting-review` (prompt only), `awaiting-response` (review landed, dispositions incomplete), or `malformed`. The lifecycle rule is that the rounds are 1..N contiguous, every round below N is COMPLETE, and N may additionally be in one of the two open states — so a round-opening commit is green when it carries the prompt and the open-state sentence in both front doors, and `_OPEN_STATE_SENTENCES` is where that sentence is registered. Nothing about a completed round is weakened; the requirements on completed rounds are strictly stronger than round 5's, because a pending cell is no longer a disposition (R6-3). `test_a_prompt_only_round_reads_as_open_and_not_as_a_broken_tree` builds the round-opening tree and runs the whole reading over it; `test_exactly_one_round_may_be_open_and_it_must_be_the_highest` is the lifecycle rule itself. |
| R6-2 | MAJOR | **Accepted, both halves, and rebuilt by restructuring rather than by widening.** The measurement half: `m-a-183`'s three outcomes now travel as ONE labelled clause — `MEASURED — trace-live cells: … ; scored-surface differences (primary transcription): 0; scored-surface differences (second transcription): 0; pinned-engine differences: 0 of 120 sampled cells` — which `_measured_clause()` RENDERS from `adequacy_drops.json` and `adequacy_crosscheck.json` at test time and requires verbatim on both reader surfaces. `ADEQUACY.md` carries it, and on the generated surface it is stamped through `adequacy_search.py`'s `DROPS` table, so `refA/MANIFEST.json` was re-stamped by `--manifests` (one line of the manifest changed; the transform is deterministic and touched nothing else). A measurement that moves now moves the required sentence, which is the property a search can never have. The negative sweep is kept and widened to the two elliptical spellings the reviewer used — a count after a preposition ("0 from the second … transcription", "0 over the 120 …") and a count after a label — so a seven written any of four ways fails. The role half: the split travels as the labelled line `Gross class size: 9; marginal to the X1 repair: 6; already unkillable before it: 3`, rendered by `_split_price_line()` from `adequacy_region_lemma_price.json` and required verbatim on all three registered surfaces; the prose sweep is now DOCUMENT-WIDE (a false role claim need not mention the class size), reads the claim from the ROLE outwards rather than from a number forwards (a number-first reading is non-overlapping and the reviewer's "every one of the seven …" would have consumed its match at `one` and discarded the claim), and judges negation over the enclosing CLAUSE — an affirmative claim must state the true number and a NEGATED one must not deny it, which is what makes "six are not the repair's marginal price" a failure rather than something skipped. `were already` left the role vocabulary: it matched a sentence about a different class, and a vocabulary that needs sentence scoping cannot be swept document-wide. Both of the reviewer's constructions are named tests. |
| R6-3 | MAJOR | **Accepted, and the false positive is the serious half.** A header that DENIES the record's verdicts satisfied the test whose whole purpose is to make the header state them; that is not a narrow clause shape, it is a guard that reads a denial as an assertion. `_header_verdict_map()` now works per sentence and rejects any attribution in a sentence carrying a negation — with the verdict PHRASES removed before the negation scan, because `DO NOT FREEZE` carries a `not` that means the opposite of a denial. `test_a_negated_verdict_sentence_is_not_an_attribution` runs the real header (which must still parse) and three negations of its own attribution clause (which must attribute nothing). The disposition-cell half: the table is parsed as a STRUCTURED surface — leading pipe, three cells, closing pipe — and a row whose disposition cell is empty, `PENDING`, a dash, or shorter than a written disposition is a PENDING ROW, not a disposition; stripping the row's pipe characters off both ends — the obvious reading — is called out in the code as the one that must not be used, because it eats BOTH trailing pipes of a row whose third cell is empty and turns it into a two-cell line — which reads as no row at all, so the finding stays undispositioned and the round stays open, fail-closed in the right direction. The severity column is now a fourth statement of the round's finding count and is compared to the verdict line's. The reviewer's construction is `test_a_pending_or_blank_disposition_cell_is_not_a_disposition`, which mutates the real record five ways and requires the round to reopen each time. The lifecycle half is R6-1's. |
| R6-4 | MAJOR | **Accepted, and swept rather than corrected in place.** R5-5 corrected the false patch-pin rationale in `ci.yml` because `ci.yml` was the file the reviewer named, and left the same claim standing in `SCAFFOLD.md` — the page an operator reads at the freeze. The class is the CLAIM, not the file, so the check is a sweep with a derived scope: every live text surface of the study plus the workflow, discovered by walk, with the verbatim reviews and the append-only record out of scope by construction (a history must be able to quote a claim in order to record its correction). The rule is structural: the registry records a SERIES and no patch, so no true sentence needs to name the registry — or `verify_interpreter()` — and a full patch level together, and one that does is claiming an enforcement that does not exist. Claim units are paragraphs in Markdown prose, own-line for table rows, headings and every non-prose file, which is what stops a whole workflow reading as one sentence. `SCAFFOLD.md`'s §C paragraph is rewritten to what is true and names the finding. On the workflow: `_disabling_conditions()` forbids `if` and `continue-on-error` at the job level and on every step, and `test_the_registered_ci_job_carries_no_condition_that_disables_it` runs all four mutations — job-level `if: false`, job-level `continue-on-error`, step-level `if: false` on the suite step, step-level `continue-on-error` on the integrity step — against the real workflow and requires each to be reported. |
| R6-5 | MAJOR | **Accepted; the closure is exact and derived from the manifests.** `payload_closure_problems()` reads both frozen mutant MANIFESTs, derives the expected payload filename per record by the same rule `e4lib/e4.py`'s `load_mutants()` uses — `<id>.json` for arm A, the record's own `file` for arm B — over EVERY record and not only the valid ones (arm B's dropped mutant has a payload on disk, and `test_the_expected_payload_names_are_the_ones_the_scorer_opens` asserts both corpora close that way in the design tree), and requires a bijection with the directory AND with the covered set. A named payload that is absent, a file the manifest does not name, and a covered set that is not exactly that set are three separate problems; all three are reported by `--check` and all three refuse `--freeze`. The reviewer's own sentinel construction is now a test that must REFUSE: `test_one_sentinel_per_payload_glob_does_not_close_the_freeze` builds the tree R5-6's residual test deliberately built, shows that R5-6's gate is satisfied by it, and requires the freeze to refuse it in both directions before repairing the closure and freezing successfully. |
| R6-6 | MINOR | **Accepted; the guard read 300 lines of a document and banned a string in the other 700.** The R5-7 heading check truncated `POLICY-DRAFT.md` at its first `---`, which is above every section it was protecting. The document is now read whole, and the ban is moved onto a STRUCTURED surface rather than a window: the stale text is forbidden on any HEADING LINE, and the corrected heading is required verbatim — so the recorded sentence that says what the heading used to say is a sentence, and the heading is a heading. `test_restoring_the_stale_gold_authoring_heading_fails_the_guard` restores the stale heading and asserts both that the guard finds it and that the truncated read cannot, which is the whole content of the finding. The recorded judgment R6-6 explicitly does not reopen — V7 and V8 remain genuine verification work — stands unchanged. |

**Post-revision state, and the suite of record — by the ARCHIVE method, which is the
convention from here on.** ROUND-6 FINDING R6-1 is the second round running in which a
suite-of-record claim failed to describe committed HEAD, and both times the working-tree run
was true of the working tree and false of every checkout of it. A working-tree run cannot
establish that property, so from this round on the suite of record is run from a
RECONSTRUCTION of the tree, and every future claim of a suite of record must name the method
that produced it. The procedure, run exactly as written here:

1. copy the repository's index to a TEMPORARY index (`GIT_INDEX_FILE`), so nothing below
   touches the real one;
2. `git add -A` the study path and `.github/workflows/ci.yml` into that temporary index —
   this is what makes the reconstruction the CURRENT TREE STATE (tracked plus staged plus
   unstaged modifications) rather than HEAD, and it is exactly the step whose omission was
   R6-1(a);
3. `git write-tree` on the temporary index, `git archive` that tree object, extract;
4. `git init` and `git add -A` inside the extraction, because the index-reading checks
   (`tracked_bytecode()`, the untracked-source tripwire) must have an index to read;
5. run `integrity.py` under `PYTHONSAFEPATH=1`, `make_manifest.py --check`, and the full
   suite with `JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` on the pinned binaries, all under
   `PYTHONDONTWRITEBYTECODE=1`. The reconstruction is a scratch tree and is discarded with
   whatever caches the run leaves in it; the working-tree run beside it is made with
   `-p no:cacheprovider`, so neither run leaves a byte behind in the real tree — which is
   SCAFFOLD item T4 and, one level up, the R5-1 blocker.

Both counts, as required: **751 passed, 0 failed, 0 skipped** in the working tree and **751
passed, 0 failed, 0 skipped** from the reconstruction, with `JPACK_BIN`, `OPA_BIN` and
`OPA_CAPS` on the pinned binaries in both, so the engine-backed tests a sandbox has to skip
ran here. In the reconstruction `integrity.py` verifies 7 ported files on CPython 3.12.11
and `make_manifest.py --check` reports no problem — only the eleven registered documents
that are pending pre-freeze. The suite grew from round 5's 739 by the twelve round-6 tests
named in the dispositions above. The reconstruction's tree object is printed by the
procedure at run time and is deliberately NOT transcribed into this paragraph: a tree
cannot contain the sentence that names its own hash, which is the linear-anchor rule this
study already applies to the manifest and the registry. Order of the reconciliation: code
and prose first, then the design corpus re-derivation below, then `harness/PORTS.md`'s
destination digest for the one ported file this response edited (`make_manifest.py`), then
`ownPorts.sha256`, then `STUDY-MANIFEST.sha256` LAST.

**The design corpus, re-derived rather than hand-patched.** R6-2's labelled clause reaches
`refA/MANIFEST.json` through `adequacy_search.py`'s `DROPS` table, so the manifest was
re-stamped by `adequacy_search.py --manifests` (exactly one line of the manifest moved) and
the whole end-to-end chain was then re-run under `regenerate.py --arm both --check` against
the pinned engines: **376/376 byte-identical**, both arms covered, the undispositioned
empty-witness census empty on both sides, and `REGENERATION-CHECK.json` itself regenerated
byte-identical to the committed record — so the one prose line that moved moved through the
generator, and nothing else in the corpus moved with it.

**Known-imperfect at this round's close, recorded rather than fixed:** the two front doors'
verdict attribution is still parsed from an English clause shape (`round(s) N returned
<verdict>`), now with enclosing-negation rejection — a header that states the true mapping in
some other form, or that carries an unrelated negation in the same sentence as its
attribution, will fail a true statement, and the answer if that happens is to widen the
parser rather than to loosen it (this round already moved one sentence in `POLICY-DRAFT.md`
for exactly that reason); the disposition-cell reading treats any cell shorter than 24
characters as a placeholder, which is a length heuristic and not a semantic one; and V7 and
V8 in `POLICY-DRAFT.md` remain open verification items, unchanged by R6-6, which was about
the heading that describes them.

## Round 7 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as all rounds.
- Verbatim record: [`reviews/round-7/PROMPT.md`](reviews/round-7/PROMPT.md),
  [`reviews/round-7/REVIEW.md`](reviews/round-7/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 2 BLOCKER, 6 MAJOR, 1 MINOR (R7-1 … R7-9).
- R7-1: the open-round model's live trial failed on the maintainer's own ceremony — the
  prompt-only commit did not carry the front-door open-state sentence the model requires,
  so the lifecycle tests were red on the commit whose greenness the prompt asserted. The
  commit discipline is amended: EVERY commit, including prompt and record commits, is
  archive-verified before push. R7-8: the freeze runbook fills no reviewer-set pin — a
  real gate gap. R7-9: further registered pre-freeze obligations (CORRECTION.md targets
  among them) sit outside the freeze gate.
- R7-2 … R7-7: the fourth consecutive round of currency-parser bypasses (polarity,
  duplicate round identities, quoted YAML keys, alternative manifest shapes, non-heading
  headings). **Registered maintainer decision (2026-08-19, recorded here before the
  response lands):** the English-semantics guard layer is descoped, not escalated. The
  program's own pattern — counts and states derived from artifacts, prose rendered from
  data — replaces it: round state, verdict maps, and measured attestations move into
  machine-readable blocks that the documents render and the tests compare to the
  artifacts structurally; window-searches survive only for banned specific false claims;
  and the truth of free prose rests where it rests in every predecessor study — on
  review, not on a test suite parsing English. This is a return to the regime's baseline
  (ADR 0004: navigation is not where claims live), undoing this study's own
  over-engineering, and it is recorded as a decision so round 8 reviews the decision
  rather than discovering it.
- Round-6 disposition verification: R6-1/R6-3 fail (the live trial), the rest partial.

### Dispositions

(Written 2026-08-19 at round close. Suite of record 757/757, working tree and archive
reconstruction both, under the registered method. The descope this round executes was
registered in this record before the response ran; what it deleted is itemized in the
response report and summarized in R7-2/R7-3's rows.)

| # | Sev | Disposition |
|---|---|---|
| R7-1 | BLOCKER | **Accepted, both halves.** The live trial failed because the ceremony asked a human to hand-write state the model requires; the ceremony is now mechanical — `harness/render_round_status.py --write` regenerates the one rendered sentence on all three front doors from the record's machine-readable block, and the commit discipline archive-verifies every commit, ceremony commits included. |
| R7-2 | MAJOR | **Accepted by descope, registered before the response.** Polarity analysis around the MEASURED clause is deleted, not repaired: the clause is required verbatim (exact substring, count-checked) on both surfaces and rendered from the measurement artifacts; a document that quotes-and-denies its own attestation is review's to catch, as it is in every predecessor study. The banned-claim sweeps for historically caught false numbers stay. |
| R7-3 | MAJOR | **Accepted by descope.** The verdict-attribution and open-state sentence parsers are deleted with the rest of the English-semantics layer; round state, verdicts, and counts live in the ROUND-STATE-BLOCK, cross-checked structurally against the reviews directories, the verbatim reviews' finding ids, and the disposition tables — and the placeholder rule is a literal set, not a length heuristic. |
| R7-4 | MAJOR | **Accepted.** Duplicate round identities refuse: a non-canonical directory is reported as non-canonical and as a collision, and can never displace the canonical round — including the listdir-ordering case the first draft of the fix got wrong and the enforcing test now pins. |
| R7-5 | MAJOR | **Accepted.** The CI guard refuses-on-unparseable: any construct outside its strict grammar is a problem, never a skip; the reviewer's quoted-key constructions and a merge-key variant are named cases, and the real job parses clean. |
| R7-6 | MAJOR | **Accepted.** Payload manifests accept exactly the scorer's canonical shapes, mirrored from the loader itself, with the alternative shape a named refusal that says which mistake was made. |
| R7-7 | MINOR | **Accepted.** The heading guard is a Markdown-heading guard on the whole document; the restored-stale-heading construction is a named failing case. |
| R7-8 | BLOCKER | **Accepted; the gate now names the pin.** The freeze runbook fills `reviewerMutantSet.sha256` from the sealed set's manifest digest, and `--freeze` refuses while it is null — the value the ceremony will pin is recorded in the response report. |
| R7-9 | MAJOR | **Accepted; every declared obligation is in the gate.** The registered-documents set now includes the three that do not exist yet — `CORRECTION-TARGETS.md` and the `verification/` V7 and V8 artifacts — so the freeze is blocked until they are authored, alongside the other pending obligations `--check` counts (15 at this close). |

**Post-revision state.** The English-semantics guard layer is gone (13 tests and their
machinery deleted, 20 structural tests added, net suite 751 → 757); the front doors carry
one rendered sentence each; the freeze gate enumerates its obligations. The reviewer's
past bypass constructions that survive as named cases are structural, not semantic. The round stays OPEN in the
block above (`awaiting-response`) and the three front doors say so in the rendered
sentence, which is the live trial R7-1 found failing: the round-opening commit is green
under the open-round model only when the model's own sentence is on the front doors, and
`harness/render_round_status.py --write` is what puts it there at round-open and at
round-close, so a ceremony commit is mechanical rather than remembered.

**What the response has landed while the round is open**, so a reader of this record is not
told less than the tree shows:

- the descope itself — the round-state block above, the renderer, the three rendered
  sentences, and the deletion of every guard that adjudicated English semantics
  (R7-2, R7-3, R7-4, R7-7, and the standing arms race);
- the structural fixes that are not descope: the CI-job reading refuses on any construct
  its grammar does not recognise, with the reviewer's quoted `"if": false` as a named case
  (R7-5), and the payload manifests accept exactly the arm-specific shape `e4lib/e4.py`
  reads, with the swapped shapes and non-string ids as named refusals (R7-6);
- the freeze-gate wiring: the sealed reviewer set is inside the payload closure and its pin
  is reported with its source and refuses the freeze while null, and the runbook carries the
  step that fills it (R7-8); `CORRECTION-TARGETS.md`, `verification/V7-COMPLETENESS.md` and
  `verification/V8-ASYMMETRY-LEDGER.md` are registered documents that the gate names and
  refuses without, and the documents that declare those obligations now name the artifacts
  that discharge them (R7-9).

**Known-imperfect at this point, recorded rather than fixed, because it is what the descope
DECIDES rather than what it overlooks:** a front door may reproduce the rendered sentence
and contradict it in the next paragraph, a disposition cell may say
`PENDING — maintainer response to follow` in words the literal placeholder set does not
carry, and a surface may reproduce a measured clause and then argue against it. None of
these is caught by a test any more. That is the registered decision: the truth of free prose
rests on review, and four rounds of evidence say a suite that tries to hold it instead
produces false accepts, false rejects, and a widening parser that the next round defeats.

## Round 8 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as all rounds.
- Verbatim record: [`reviews/round-8/PROMPT.md`](reviews/round-8/PROMPT.md),
  [`reviews/round-8/REVIEW.md`](reviews/round-8/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 3 BLOCKER, 4 MAJOR, 1 MINOR (R8-1 … R8-8).
- **The descope decision is upheld on its merits**, in the reviewer's own words: the
  regime requires recorded review, written dispositions and the exact final verdict, "not
  a test that adjudicates arbitrary English"; returning free-prose truth to review while
  retaining rendered exact strings, artifact comparisons and targeted bans "is therefore
  correct." The findings are against the structural replacement's completeness, not the
  decision.
- Round-7 disposition verification: R7-2/5/6 hold, R7-4 holds narrowly, the rest partial
  with residuals enumerated as this round's findings.
- R8-1 is the regime's own arithmetic: an open round cannot be the final round; it closes
  by this ceremony completing and a later round returning the exact words.

### Dispositions

(Written 2026-08-19 at round close. Suite of record 780/780, working tree and archive
reconstruction both, the reconstruction's tree hash byte-identical to the index. Thirteen
single-point mutation checks run against the new safeguards; one deliberate redundancy —
the liveness helper applied at both record-section and disposition-row reading — cannot be
discriminated by any single-point mutation, and the record says so rather than claiming
otherwise.)

| # | Sev | Disposition |
|---|---|---|
| R8-1 | BLOCKER | **Accepted as the regime's own statement; no change.** An open round is not a final round; it closes by this ceremony completing and a later round returning the exact words. One corollary assertion added, labelled not-a-gate: the freeze verdict is in the closed vocabulary and no round has returned it, so a future round that does forces a deliberate revisit. |
| R8-2 | BLOCKER | **Accepted.** The freeze path calls the sealed set's own loader — schema, cardinality, languages, filenames, digests — from `--check`, `--freeze`, and the new `--freeze-gates`; the rehearsal tree carries a real sealed set so the rehearsal survives the real gates; four tampering constructions are named refusals including the reviewer's payload-replacement. |
| R8-3 | BLOCKER | **Accepted.** The verdict vocabulary is closed to the review prompt's own output contract; the block, the review's final line, and the tree-derived state must agree on every declared member — flipping a verdict in the real record's block now fails two tests. |
| R8-4 | MAJOR | **Accepted.** The block parser refuses duplicate keys at every depth, surplus members at every level, and mistyped members — readable-two-ways JSON is a refusal, not a choice. |
| R8-5 | MAJOR | **Accepted.** Duplicate finding ids refuse with the round marked malformed; disposition rows and record sections are read through one fence- and comment-aware liveness helper, with the reviewer's commented-out-table construction a named case. |
| R8-6 | MAJOR | **Accepted.** One marker-span reading serves both the checker and the writer: exactly one pair, in order, enclosing exactly the rendered sentence; a malformed pair refuses without touching bytes — the old partition's destructive path is itself asserted gone. |
| R8-7 | MINOR | **Accepted.** Heading scanning shares the liveness helper; fenced and commented `#` lines are not headings, and the Setext lookahead is preserved by line-count-stable filtering. |
| R8-8 | MAJOR | **Accepted; the promise from the brief is wired.** `harness/grid_gate.py` runs the registered domain, fixed-scale, and project→re-serialize→byte-equal assertions over every grid in the tree from `--check`, `--freeze`, and `--freeze-gates`; it holds over the real 117-row grid and refuses seeded scale loss, exponent forms, and range violations. |

**Post-revision state.** Suite 757 → 780 (23 new tests, all green both ways); the freeze
gate now exercises its own loaders and the grid gate; fifteen pending ceremony
obligations, unchanged and enumerated.

## Round 9 — 2026-08-19

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, same invocation shape as all rounds. **First attempt produced no verdict**: the
  reviewer's provider flagged the session for "possible cybersecurity risk" after 282,252
  tokens — a false positive on the study's adversarial-testing vocabulary — and the run
  exited without output. The retry, same committed prompt byte-for-byte, completed. Both
  attempts are part of this round's history.
- Verbatim record: [`reviews/round-9/PROMPT.md`](reviews/round-9/PROMPT.md),
  [`reviews/round-9/REVIEW.md`](reviews/round-9/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 2 BLOCKER, 4 MAJOR, 1 MINOR (R9-1 … R9-7).
- **The scope ruling (maintainer decision, user-ratified 2026-08-19, taken on this
  round's evidence):** across rounds 5–9 the registered surface took no findings while
  the review-support apparatus — a layer no predecessor study carried — absorbed nearly
  all of them and grew with every response. The apparatus is now registered in §4b for
  what it demonstrably is: drift detection under an honest operator, in this record's own
  round-2 words "a gate against drift, not a root of trust." Registered-surface findings
  keep full gate force; apparatus-hardening findings are recorded in
  `harness/ADVISORIES.md` (appendable, manifest-excluded) and do not gate.

### Dispositions

(Written 2026-08-19 at round close. Suite of record 800/800 expected at the close commit,
archive-verified; the response's own verification ran 799/799 both ways before the R9-1
fix added its test.)

| # | Sev | Disposition |
|---|---|---|
| R9-1 | BLOCKER | **Accepted — registered surface, outside the ruling.** The freeze-authorizing reading is byte-exact: the review's final line must be the verdict as registered, no case folding, no indentation forgiveness; near-miss renditions are named as near-misses and authorize nothing. Enforced by `test_a_near_miss_verdict_line_does_not_authorize`. |
| R9-2 | BLOCKER | **Accepted — registered surface.** The freeze refuses while any attempt root exists: the registered root, any entry under `results/`, and any indexed path there, with dangling-symlink semantics; the constant is asserted equal to the driver's own root rather than being a second spelling. Mutation-checked both ways. |
| R9-3 | MAJOR | **Recorded advisory under the §4b ruling** (`harness/ADVISORIES.md`): Python's numeric equality admits `1.0` where the block schema means `1`. |
| R9-4 | MAJOR | **Accepted — registered surface (the sealed set's registration).** Ids bind to `rm-<language>-NN` exactly, anchored `\A…\Z` — the finding's own suggested `$`-anchored pattern is too wide in Python, verified by construction — with the language segment bound to the record and duplicate-key refusal on the sealed manifest. Fifteen tests including the reviewer's all-renamed construction. |
| R9-5 | MAJOR | **Recorded advisory** — liveness-helper indentation edges. |
| R9-6 | MAJOR | **Recorded advisory** — marker-span Markdown context. |
| R9-7 | MINOR | **Recorded advisory** — render write-loop atomicity. |

**Post-revision state.** The two-tier threat model is registered (§4b, §7); the advisory
register exists and is excluded from the covered set by named constant with its asserting
test; the freeze gate gains the prior-attempt refusal. Round 10 is asked for its verdict
on the registered surface under the declared threat model.
