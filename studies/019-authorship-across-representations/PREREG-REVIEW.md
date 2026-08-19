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
| R3-4 | MAJOR | **Accepted, and the pilot now says something new.** The pilot path consumes the harness's own domain/identity code — one path, not two. E4-PILOT-v4, re-issued through it: arm C identity drops from 5/5 to **1/5** — four pilot runs authored out-of-domain cases, all omitting the screening result the registered domain closure requires (three also passed a term with no vendor member). Arm A 5/5, mean paired 0.878, high-kill 1/5; arm B 5/5, 0.897, 0/5; arm C one admitted run, 0.806. Published prominently, old beside new; byte-identical on a second full scoring. The domain closure's bite on real authored suites is now a measured design fact, not a surprise waiting for the batch. |
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

**Pending — no R4 finding has been dispositioned yet.**
