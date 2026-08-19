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
