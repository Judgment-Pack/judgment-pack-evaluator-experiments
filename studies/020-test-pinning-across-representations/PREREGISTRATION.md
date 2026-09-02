# Preregistration — Study 020: test pinning across representations

**Status: DRAFT, second revision (post-round-1), under review. Not frozen. Nothing citable
has run; the review record's state is the rendered sentence below and only there (R1-23 —
this header once said "no review round is on the record" beside a sentence saying
otherwise).** The cross-vendor review rounds will be recorded in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md), each verbatim under `reviews/`, and that record's
round-state block is the single machine-readable source for round counts, verdicts and open
state (ADR 0005). The rendered sentence below is this header's ONLY statement of them. Every
execution before the freeze is a PILOT and supports no claim, and `integrity.study_label()`
says so while any freeze pin is null. Items marked `GATE(pre-freeze)` are the freeze
ceremony's enumerated work; items marked `TODO(prereg)` are values that cannot exist yet, each
with the event that produces it named beside it. **This study is an instrument repair on
Study 019 and inherits its machinery by port** (§7); where 020 departs from 019 the departure
is registered here rather than discovered in review.

<!-- round-status:begin -->
ROUND STATUS (rendered from PREREG-REVIEW.md's round-state block by harness/render_round_status.py; edit the block, never this sentence): 2 review rounds are on the record, 2 have returned a verdict — rounds 1-2 returned DO NOT FREEZE — and round 2 is open, awaiting the maintainer's written disposition per finding.
<!-- round-status:end -->

> **On the sentence above — the gate is CLOSED.** `harness/render_round_status.py` is 019
> machinery and ported with the rest of the harness (§7, delta 10). The sentence between the
> markers was hand-written to be byte-identical to what the block in `PREREG-REVIEW.md`
> renders, and it was marked here for mechanical regeneration at harness-port time. **The
> first act of the port was `render_round_status.py --write`, and it reported `nothing
> moved`**: the hand-written sentence was already byte-identical to the rendered one on both
> front doors. The sentence is machine-produced from here on and the currency suite requires
> the rendered string of both front doors verbatim. A hand-written status sentence is exactly
> the failure mode ADR 0005 registers against; it was tolerated only while the renderer did not
> exist in this tree, and it no longer is.

---

## The footing, stated first

On 2026-08-22 the maintainer ruled **M-1 = BOTH** (`design/RULINGS.md`). Study 020 registers on
a **two-tier footing**, and every sentence in this document belongs to exactly one tier.

**Tier C (confirmatory-by-robustness)** carries the study's one confirmatory sentence, R1
(§1.3), and decides only where **every member of the pre-declared eighteen-member sensitivity
family** (§5.2) agrees in the sign of the A−C difference *and* each member's own test excludes
zero. The family spans exactly the analytic choices that were still open at the moment 019's
arm-labelled quantities entered the design record — estimand level, engine-supplied-kill
column, analysis population, and covariate adjustment — with **both poles of every axis
retained**. Because the verdict requires unanimity across the whole family, no single choice
made after the direction became known can manufacture it.

**Tier D (direction-aware)** carries everything else: 019's known direction, stated openly with
its provenance (§0.2), used for power planning, apparatus design and interpretation, and every
descriptive quantity. **Every Tier D table carries the standing clause, carried verbatim from
019 §5's R1-15 discipline: *descriptive; published as an interpretation quantity that no
decision reads.***

**Tier D MAY** (a) plan power — N, pilot N, effort pin — against magnitudes and dispersions
honestly informed by 019; (b) interpret, after Tier C reports, saying per member whether 020's
directions agree with 019's, with both sets of figures printed; (c) shape apparatus —
analysis-set disposition, missing-data rule, the scorer's survivor-vector requirement, all
functions of *how many runs score*, not of which arm wins; (d) name the risk — every place a
design choice is known to move the contrast is disclosed with its magnitude (estimand level
0.059 at identity-passing; adjustment 0.0247 at group level; population 0.098 at group level
between identity-passing and the §1a denominator; engine column 0.0056 at group level,
per-protocol).

**Tier D MAY NOT** (a) write any confirmatory sentence — no Tier D quantity adjudicates R1 or
enters the decision table, and an INDETERMINATE Tier C outcome licenses no negation; (b) select
a Tier C family member — membership is fixed by §5.1's arm-blind admission test and is
append-only; (c) fix a threshold, cut, floor or trim — any threshold in 020 is derived by a
committed rule, never chosen against an arm-labelled rate; (d) be reported without its tier
label.

**Why the leak does not reach Tier C — the argument is structural, not epistemic.** Three
properties carry it and all three are registered: (1) requiring every member to reject at
α = 0.05 is an **intersection–union** test, whose size is **≤ α** over the union null with no
multiplicity correction (§5.4) — adding members can only reduce size; (2) membership is derived
arm-blind (§5.1) and is **append-only** after registration — a maintainer may **add** a member,
which is monotone toward INDETERMINATE, never remove one, and an addition requires a
`DEVIATIONS.md` entry with the pre-addition verdict published beside the post-addition one;
(3) **every member is published whatever the verdict** — unanimity is not a filter over what
gets reported. What the argument does *not* by itself neutralise is the choice **of** family,
which is why §5.5's honesty tables are mandatory reprints rather than an appendix.

---

## 0. Design provenance (disclosed, because it shaped the registered claims)

### 0.1 The design record, and the rulings this document implements

This draft was preceded by a design phase whose artifacts live under `design/`:
`design/BRIEF.md` v2 (every figure re-derived from 019's frozen artifacts, **no new model
calls**), `design/PANEL-FINDINGS.md`, and `design/RULINGS.md` — the twelve maintainer rulings
of 2026-08-23 and the M-14 forensic verdict appended to them. **Where this document and the
brief disagree, the rulings govern; where the rulings are silent, the brief governs.**

**M-15 is satisfied as a precondition, not promised.** The ruling was *publish first*: 019's R2
amendment — the arm-labelled quantities, their provenance, and the standing no-decision-reads-
them clause — lands on 019's record **before** this preregistration is drafted. It has landed:
`studies/019-authorship-across-representations/ANALYSIS.md`, "R2 amendment (2026-08-23) — the
arm-labelled descriptives, published because they are already on the record". *A direction
computed and then withheld is a direction published*; the record was made honest before
anything registered on top of it.

### 0.2 The prior, stated once, in full — and it is not one direction

From 019's registered batch, corrected scorer throughout (§5.2's empty-survivor rule):

| cohort | level | A | B | C | A−C | A−B |
|---|---|---|---|---|---|---|
| artifact-bearing, all (36/30/30) | mutant | 0.60628 | 0.59032 | 0.61613 | **−0.00985** | +0.01596 |
| identity-passing (34/26/28) | mutant | 0.64194 | 0.68114 | 0.66014 | −0.01819 | −0.03920 |
| identity-passing (34/26/28) | group, 33 shared | 0.61765 | 0.59907 | 0.57684 | **+0.04081** | +0.01858 |
| identity-passing (34/26/28) | symmetrised mutant | 0.67333 | 0.66148 | 0.63877 | +0.03456 | +0.01185 |
| §1a admitted, ITT-114 (38/37/39) | group, 33 shared | 0.55263 | 0.42097 | 0.41414 | **+0.13849** | +0.13167 |

*Descriptive; published as an interpretation quantity that no decision reads.* At the mutant
level — the level 019 registered and scored — **A is below C**. At the group level — the level
020's family centres on — **A is above C**, and on the identity-passing cohort that difference
clears α = 0.05 (exact two-sided label permutation, 20,000 draws, seed 11: p = 0.0213) while
the mutant-level one does not (p = 0.4578). **Provenance: the design phase, not the study.**
None of it was produced by 019's registered decision procedure, which stopped at decision row 3
with `control-gate-failed: e1-floor` and computed no contrast.

**020 registers no expected direction, anywhere.** §1.3's R1 is a two-sided unanimity rule whose
claimed direction, if any, is the family's common sign as observed. No section of this document
states a hypothesis about which arm is higher.

### 0.3 The honesty test this footing has to pass

019's own batch **could not have passed Tier C**. On the eighteen registered members the A−C
contrast splits **16 positive / 2 negative** and only **10 of 18 reject** at α = 0.05. That
verdict is robust to dropping any single pole of any axis — with **one exception**, printed
here and reprinted in full in §5.5: dropping the per-protocol pole, leaving an ITT-only family,
would have produced a **CLAIM** on 019, and §5.6 shows that an ITT-only family rejects
**66–68 % of the time under a null in which coverage is identical and only authoring validity
differs**. The per-protocol pole is what stops Tier C from calling an OPA-toolchain failure rate
a representation effect. That is the single most load-bearing fact behind this registration, and
it is why family membership is registered before the batch and is append-only afterwards.

### 0.4 The five 019 instrument defects 020 exists to repair

019 froze at `51cae02`, ran 150 registered slots, and stopped at decision row 3. On the record:
an unattainable primary cut (E4 τ = 19/20, `highKillRate.count` = 0 in all three arms); a
control floor calibrated on a population the registered condition never reproduced (E1); a
pilot that measured a different compute condition (§2a.1); an author-side gate whose power was
never computed (§5.7); and a scorer schema that encodes "nothing evaluated" and "everything
killed" with the same token (§5.2, §7). Each has a registered repair below, and each repair is
named where it is argued rather than asserted in a list.

## The freeze and the primary attempt

The freeze commit is the squash-merge commit of the freeze PR on `main` — named by reference
because a squash hash cannot exist before the merge. At the freeze, every pin in
`harness/PINS.json` is filled; `results/primary-attempt-001` must not exist, and the scorer
refuses if it does. The governing invocation, run once from the freeze commit under the pinned
interpreter, is:

    <the CPython PINS.json pins> harness/score.py --attempt-root results/primary-attempt-001 --include-reviewer-set

The first invocation of that command is the primary attempt, crash and all. The scorer is the
only publisher; its outputs embed no timestamp and no absolute path. `--include-reviewer-set` is
part of the governing invocation and is mandatory for a REGISTERED attempt: a REGISTERED label
without the flag refuses, and the flag while any freeze pin is null also refuses,
`reviewerMutantSet.sha256` being one of those pins. There is exactly one primary attempt, so
there is exactly one execution of the set (§4).

**The freeze gates permit and require a `calibration/` subtree.** 019's `DEVIATIONS.md` D-2
records that `manifest_problems()` refused any tree containing prior authoring, which would make
020's registered pilot un-runnable at freeze time. 020's gate **permits and requires**
`calibration/` at freeze while still refusing any `results/primary-attempt-*` — written into the
gate *and its test* before the first pilot call. `GATE(pre-freeze)`.

## 1. Question, and what the endpoint measures

### 1.1 The question, carried verbatim from Study 019 §1

> Within the registered JPS-expressible policy fragment, under single-shot authorship, does the
> representation a model authors in change **what its accompanying test suite pins down** —
> compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a prescribed
> judgment convention (arm C)?

**What A−C is a contrast between (the registered estimand, carried from 019 §1).** Arm C is not
arm B plus formality. Arm B receives a **result-shape-only floor contract**: a prose inventory
of the result fields and their permitted values, mechanically de-formalized from C's schema, and
nothing else. Arm C receives **the full prescribed judgment convention**: that same result shape
as a JSON Schema, plus five substantive conventions — a registered default decision, totality,
explicit precedence, unresolved handling, and grounds behaviour (§3). **A−C therefore compares
the pack format against Rego-plus-the-full-convention, as bundles.** The registered treatment is
the bundle, the estimand is the bundle's effect, and **no attribution of any part of an A−C
result to any component of the bundle — representation, result schema, or any individual
convention — is licensed** by this design (§9). A−B is the same comparison against the floor
contract, and B−C is not a registered contrast at all. **Why A−C is first:** C is the live
alternative architecture; A−C is the comparison the program would act on. B is the floor.

### 1.2 The measured construct: witness-input coverage against the shared reference

**M-18 / M-26, ruled 2026-08-23: rename.** R1's sentence names the measured construct, and it is
this:

> **The registered construct is *witness-input coverage against the shared reference*: the
> fraction of the shared witness classes a run's authored suite reaches, where a run covers
> class *g* iff its suite kills all of *g*'s members in the run's own language.**

*"Test-pinning power" survives in this document only as motivation prose — the phrase names why
the program cares, never what is measured. No headline, no decision sentence and no published
quantity uses the old name.*

**Fact 1 — kill reduces to witness-class coverage, and the reduction has a condition.** Derived
from 019's frozen manifests, not asserted: for every one of the **88** runs that carry a
non-degenerate survivor vector, `killedPaired` equals **exactly** the summed member count of the
witness classes the run covers — **88 of 88, zero mismatches** — and `gall == gany` in **88 of
88**. A run is therefore fully described, language-neutrally, by the subset S of the 33 shared
classes its suite reaches; every candidate endpoint in §5.2's family is a weighted count over S
and the members differ only in weights. **Assertions never enter.** Greedy hitting-set over the
51 distinct witness inputs behind the 33 shared classes reaches 33/33 with **21** gold inputs,
against authored suites of 16–25 cases.

> **The condition is registered with the fact.** Fact 1 holds **conditional on the identity
> control passing** — specifically on `referenceIdentity` (§1.2's next paragraph and §4). It is
> not claimed of identity-failing runs, and the two degenerate empty-survivor runs of §5.2 are
> exactly where a naive reading of the same schema produces a perfect score from nothing
> evaluated. **The checkable denominator is 88, not the 114 the design panel and both v2 drafts
> asserted**: only 90 of 019's runs carry a survivor vector at all, and two of those are
> degenerate.

**M-13, ruled 2026-08-23 as recommended: the suite-against-own-policy score, and the registered
change to what "identity" means.** 019 had one identity relation. **020 registers two, named
separately, and says which one gates:**

- **`referenceIdentity`** — the 019 control, unchanged: every case whose inputs are in the
  registered domain agrees with the arm's **unmutated reference** on the scored surface. This is
  the relation that defines the per-protocol population pole (§5.2) and the condition of Fact 1.
- **`ownPolicyIdentity`** — new, and the substance of M-13: the same suite evaluated against the
  run's **own authored policy** — one extra engine EXPOSURE per run, whose invocation count is
  arm- and case-dependent (measured, R1-14: arm A evaluates the own pack once per readable case;
  arms B/C run one `opa test` plus one strict adjudication per reported failure). Its per-run
  score is a
  **reported quantity** (E6, §5.1) that **gates nothing**.

**R1's construct statement is conditioned on it.** The endpoint measures pinning **against the
shared reference**, not against the policy each suite accompanies; `ownPolicyIdentity` is what
makes that severance visible instead of merely disclosed, and R1's claim sentence (§1.3) carries
the qualifier **and** the reported score. **This is a registered change to what "identity" means
in this program and is named as such.** The registered decision on which relation gates is
argued rather than defaulted: `referenceIdentity` keeps the gate because moving the gate to the
conjunction would move every per-protocol member's population and would make §5.6's dispersion
figures inapplicable at registration time; the conjunction's composition is published as a Tier D
population disposition so a reader can see exactly what the alternative would have done. The
residual is a registered ceiling (§11.10).

**Effective support, stated wherever the estimand is defined.** Five of the 33 shared classes —
`d8-2m01-low`, `d8-2m01-low-absent`, `d8-70-low`, `d8-low-40-500k01-ins-absent`, `d8-low-89`,
each a single-witness `d8` boundary input — were covered by **no run in either language** across
all 88 identity-passing 019 runs. Both arms' floors are displaced downward by a fixed
5/33 = 0.1515 and no member can exceed **28/33**.

### 1.3 R1 — the decision sentence

> **R1 (primary, retractable; confirmatory-by-robustness).**
>
> *Within the registered JPS-expressible policy fragment, under single-shot authorship, arm A's
> mean **witness-input coverage against the shared reference** differs from arm C's — **claimed
> if and only if all eighteen registered family members (§5.2) agree in the sign of the A−C
> difference and each member's own two-sided permutation test rejects H₀ at α = 0.05.** The
> claimed direction is that common sign. The endpoint is coverage against the shared reference,
> not against the policy each suite accompanies, and the per-run `ownPolicyIdentity` score (§1.2,
> E6) is published beside every figure this sentence reads.*
>
> *If the members do not agree in sign, or if any member's test fails to reject, R1 returns
> **INDETERMINATE-BY-DISAGREEMENT** and the study makes no confirmatory statement about A vs C.
> **An INDETERMINATE outcome licenses no negation** (019 §5, verbatim) — not equivalence, not
> either direction's negation, and it triggers nothing. All eighteen point estimates, all
> eighteen p-values, all eighteen per-arm n and the full agreement table are published in every
> outcome.*
>
> *Fixed sequence: **A−C, then A−B**. The A−B step is evaluated under the identical eighteen-member
> unanimity rule and is reached only if the A−C step returns a claim.*

**There is exactly one verdict vocabulary: CLAIM or INDETERMINATE-BY-DISAGREEMENT.** The word
**UNSUPPORTED is not used anywhere in 020** for this rule; it reads as evidence of no effect,
which INDETERMINATE explicitly is not.

**No δ, no τ, no cut, no dichotomy, and no registered direction.** Tier C registers no threshold
of any kind, so it has no attainability problem — there is no τ that can be unattainable, which
is the property that killed 019's E4. **No replacement attainability machinery is registered** —
no probe, no refusal branch, no τ anywhere, including in Tier D, where the full coverage
distribution is published instead of any dichotomy. The argument for a continuous endpoint is
that it has no cut to place, discards no information, and cannot produce 019's `0 / 0 / 0`; **no
cross-scale comparison is made anywhere in this document**.

### 1.4 R2 (secondary, descriptive)

The failure map and the whole Tier D battery (§5.8): per-class coverage profiles, engine-supplied
vs assertion kills, the E1 report and its two strata, `caseCount` as a construct quantity, the
corpus-structure publications, authoring latency and validity profiles, and the interpretive-
spread census. **R2 is never adjudicated and never falsifies**, and every table in it carries the
Tier D standing clause.

## 1a. Population and prospective content

No locked-replication stratum and no reviewer-holdout stratum: this is an authorship-rate study
in the 011/012/019 line, and its prospective content is the post-freeze registered batch — no
authoring run exists at freeze time. Reviewer-authored prospective content lives in the **fresh
sealed reviewer mutant set** (§4). The calibration pilot, the pre-pilot effort sweep and the
smoke are non-citable and outside every population.

**Population rule, enforced in code (the Study 001/011 lesson).** The denominator of every
per-arm rate is attempted runs whose **apparatus** succeeded. Apparatus failures — slot shape,
call nonzero-exit, call timeout at the registered ceiling, pre-call refusal, post-call wrapper
failure, golden-context mismatch, binary digest mismatch, registry mismatch, transcript refusal,
pinned-engine invocation produced no answer during scoring — are pipeline-invalid, excluded, and
reported with their own rate and interval. Every failure
attributable to what the author emitted is an **authoring outcome**: valid, counted, and scoring
zero on every endpoint it reaches. The registered authoring-outcome codes are:

| code | arms it can reach | meaning |
|---|---|---|
| `no-marker-block` | A, B, C | no extractable marker block |
| `unparseable-artifact` | A, B, C | artifact present, case structure not enumerable |
| `schema-invalid-pack` | A | pack fails the pinned schema |
| `opa-check-failed` | B, C | `opa check` refuses the authored policy |
| `v0-syntax` | B, C | Rego v0 syntax under a v1-pinned invocation |
| `author-protocol-violation` | A, B, C | transcript shows a tool use or a turn after the registered prompt |
| **`presence-idiom-unsound`** | **B, C** | **new in 020 — §3.2's registered presence-idiom guard fires** |

> **AMENDED, 2026-08-24 (round-1 finding R1-1, marked).** This table's first printing carried a
> seventh admission code, `unreadable-output-shape` ("result shape outside the registered
> surface", A/B/C). Every state that produced it — a validator timeout, a jpack exit the binary
> itself declares an invocation failure (3/4/5), an `opa check` that rendered no readable error
> document — is the pinned engine FAILING TO ANSWER, which is an apparatus event: the engine
> said nothing about the author's artifact, so no authoring code may be read off it. The code is
> RETIRED; those states raise `engines.EngineError` out of admission (and out of E1, where a
> timed-out evaluation of the authored policy was likewise filed as an authored gold failure),
> the scorer files the run under the new apparatus code `engine-invocation-refused`, the run
> leaves every population, `scoringApparatus` publishes it per arm with its refusal class, and
> §6's `engine-execution-clean` gate reads the exclusions — so an unanswered invocation can
> gate the attempt but can never move a rate. An evaluator's OWN error document about the
> authored artifact remains an authored gold failure, exactly as before: the line is drawn at
> whether the engine answered, not at whether the answer was pleasant.

The E4 population adds one further registered step: the identity control (`referenceIdentity`,
§4), whose exclusions are reported, not silent. A harness test diffs this prose partition table
against the scorer's code partition and against every code `admit()` can return.

**The partition is closed over what the harness can emit, and closed fail-shut.** Every wrapper
exit status maps to a complete slot or to one apparatus code above; every refusal of the
transcript binding maps to one code above, by cause; and a code the partition does not name — or
an exit status the wrapper does not register — **refuses the whole attempt as pipeline-invalid**
rather than being materialized, sealed, ledgered and then silently counted. Exhaustiveness is
checked at import and enforced at every write.

**Every scored slot was made under the registry this attempt reads.** The wrapper stamps the pin
registry each call ran under into that call's retained `CALL.json`; the scorer hashes the
registry it is itself about to trust, records that digest in `ATTEMPT.json`, and requires every
admitted slot's stamp to equal it. A slot whose stamp differs, or carries no stamp at all, is
`registry-mismatch` — apparatus, excluded, reported. **Registered as a day-one consequence
(019 D-1/D-3, panel #22):** any post-freeze registry re-pin invalidates every slot recorded
before it, so either the scorer's registry check reads a semantic subset rather than the raw file
digest, **or** a repair halts and restarts rather than resumes. 020 registers the second: a
registry re-pin **halts and restarts the batch**, and the abandoned slots are published with their
codes.

**Terminality, and what a declared shortfall costs.** The registered batch is the registered slot
count and the registered population is that batch. A batch that does not complete may be
**declared short**, and the declaration is a schema carrying evidence rather than a note: the
registered prefix it stopped at, the ledger's own digest and chain head, and one row per slot with
its place in the registered call order, its seal digest, its wrapper exit and its §1a code. The
scorer **re-validates that declaration against the batch on disk** and refuses a declaration that
does not describe this batch. A validated declaration is **terminal and not scored**: every level
verdict is `UNRESOLVED-BY-DESIGN`, no endpoint, no rate and no contrast is computed, and §5.9's
ordered rule reaches that row above every substantive one.

## 2. Apparatus and pins

All pins null until the freeze; the scorer labels any run PILOT while any pin is null. Ported
pins carry 019's resolved values and are re-verified fail-closed at run time.

- **jpack** v0.17.0: archive sha256 `4046a101…` verified against the release `checksums.txt`;
  binary sha256 `42f35f79…`; reproducible-build attestation at freeze. Verdicts and error classes
  read from the JSON payload only. The operator PATH binary must never be invoked.
- **OPA** v1.19.0: asset `opa_linux_amd64_static` sha256 `1dd5c559…` verified against the
  published per-asset checksum; **no reproducible-build claim exists** — the pin is against the
  published artifact, stated here. Rego v1 pinned in prompt and invocation. Capabilities file
  generated from the pinned binary with the registered denylist; the `time.now_ns` canary must be
  refused. The `opa test` exit taxonomy is carried verbatim from 019 in all three branches (exit 0
  every test passed; exit 2 at least one test FAILED; exit 1 the invocation never got as far as
  running tests). **No verdict and no kill is read from an exit code.**
- **Authoring stack**: codex-cli, binary sha256 pinned; model named by explicit flag at batch
  time. Full 011/012/019 isolation discipline: fresh HOME/CODEX_HOME, `env -i`, golden
  pre-prompt-context capture from two agreeing probes, isolation negative control under recorded
  operator assent, credential copy deleted on seal and traps.
- **Interpreter**: CPython, implementation and series pinned, exact version recorded; runbooks
  name it by absolute path.
- **Prompts**: assembled deterministically from the frozen policy prose, the naming appendix and
  the arm materials; each arm's assembled prompt pinned by sha256 at freeze. The call wrapper
  refuses on prompt digest mismatch. Byte sizes published. The B→C delta is prompt material, not
  formatting: it is part of the registered bundle (§1.1, §3) and is published beside every result.
- **Batch shape**: sequential, never parallel; arm-interleaved first-order carryover-balanced
  schedule for three arms, **re-derived at 020's registered round count and asserted by a harness
  test**. 019's `batch.py` hard-codes `SEQUENCES = 6`, `ROUNDS = 50`, `RUNS_PER_ARM = 50`,
  `REGISTERED_SLOTS = 150` and a two-element `TAIL`, and `derive_order()`'s docstring records the
  registered floor (1, 1) as the cached answer to a search **at 50 rounds**; at any other round
  count that assertion is wrong by construction. **FILLED, 2026-08-24 — the schedule at the
  registered N = 60/arm** (§2.1's fill: the sweep supplied the operability evidence and the
  prices, and the named rule chose the condition): `batch.order` / `batch.n` = 60 /
  `batch.slots` = 180, re-derived at 60 rounds by `derive_order()`'s exhaustive search — ten
  whole Williams blocks, NO tail (60 divides by 6), attained position spread 0 and
  directed-transition spread 1, no self-successions — asserted by `harness/tests/
  test_schedule.py` against the REGISTRY's published spreads. The 50-round port carry it
  replaces (8 blocks + a two-sequence tail, spreads (1, 1)) is recorded in the registry's own
  order note as history.
- **Registered batch window**: stated **once**, here, as three consecutive UTC calendar days, with
  a test that no other document in this tree states a different one (019's D-4 filed a deviation
  against a rule 019 did have; the defect was duplicated constants, not the rule).
- **Per-call timeout ceiling: 2700 s**, an apparatus bound; timeouts are pipeline-invalid, and a
  per-arm timeout rate above the registered cap (10 % of slots) is a control-gate failure
  adjudicating R1 in neither direction.
- **Disk and retention, registered**: a free-space precondition checked at driver start **and
  before each slot**; a retention rule for the scratch parent (the wrapper makes two directories
  per slot); and a total budget — 019's 149 retained slots occupy 86 MB in-tree (arm-A slots
  ~660 KB, arm-B/C ~20 KB), so ~249 slots project to roughly 140–160 MB plus scratch.

### 2.1 The compute condition is NOT committed, and the sweep is the registered decider

**M-8 / M-20, ruled 2026-08-23: the sweep decides, and the two are decided together.** The
compute condition is the one thing 019's retained evidence cannot decide, and **no condition is
committed by this document**. What is registered is the procedure that chooses it and the price
of every branch.

**The pre-pilot effort sweep, registered.** `n = 3/arm across three settings — 27 calls`, run
through the registered apparatus (`harness/authoring_call.sh` + `harness/batch.py` under
`--sweep`, never outside the harness), published in full, `citable: false`, outside every
population. The registered compute condition — **the `codex.reasoningEffort` value and N
together** — is chosen from the sweep's result and priced at the sweep's own observed durations.

**Dual pricing, printed rather than caveated.** On one admission cohort throughout, 019's
registered executed-call slot-triple is **199 / 75 / 75 s = 349 s = 5.82 min**; the pilot-like
triple, on the completed cohort, is **1660.184 + 803.042 + 624.114 s = 3087.34 s = 51.46 min**,
i.e. **8.85×**. A swept setting at pilot-like durations therefore costs 8.85× its registered line:

| line | calls | wall clock, registered condition | wall clock, pilot-like durations |
|---|---|---|---|
| pre-pilot effort sweep, 3 settings × 3/arm | 27 | 0.87 h | 7.72 h |
| pilot, 12/arm (C1–C5) | 36 | 1.16 h | 10.29 h |
| D-1/D-2 smoke (real exec, stand-in binary permitted) | ~6 | ~0.19 h | ~1.72 h |
| primary batch, N = 60/arm | 180 | 5.82 h | 51.46 h (2.14 d) |
| **total at N = 60, no author-side gate (M-23 = a)** | **~249** | **~8.05 h** | **~71.2 h** |

> **CORRECTION (pre-freeze, found by the fill's verification pass, 2026-08-24).** This table
> first printed the sweep row as 0.29 h / 2.57 h and the smoke row as 0.06 h / 0.51 h — each a
> threefold understatement: both rows divided calls by nine instead of by three (27 calls are
> NINE round-triples, not three), while the pilot and batch rows used the correct basis. The
> corrected totals are ~8.05 h and **~71.2 h** — the pilot-like branch leaves roughly 1 %
> headroom against the 72 h budget, not the ~10 % the first printing implied. The observed
> sweep corroborates the corrected basis: it cost 1.44 h, 1.65× the corrected registered-
> condition row and 5× the erroneous one. The xhigh-exclusion paragraph below quoted the
> erroneous 2.57 h and is corrected with the same note.

The N = 60 rows are **priced illustrations of one branch, not a registered N.** M-13's
`ownPolicyIdentity` invocation adds one **engine** call per run — no authoring call, no line in
this table, and its cost is bounded by the pinned engine's per-invocation ceiling.

> **FILLED, 2026-08-24 — the registered compute condition: `codex.reasoningEffort = low`,
> per-arm N = 60.** The sweep ran 27/27 under the registered label with zero apparatus codes,
> zero timeouts and no per-setting abort (two earlier invocations were preflight-refused in
> full by the wrapper with zero spend, for operator error; `DEVIATIONS.md`'s operational record
> and `sweeps/refused-attempt-0{1,2}-*/` carry them). The full per-setting table — per-arm
> durations, completion bytes, `reasoning_output_tokens`, and the per-arm perfect and identity
> rates — is published at `sweeps/2026-08-24-effort-sweep/SWEEP.md`. The rates are the one
> quantity the driver's own registration forbids it computing; they were scored post-sweep by
> `harness/sweep_rates.py` — a covered, tested publisher authored after the sweep to discharge
> this fill's registered obligation, with per-slot detail in `SWEEP-RATES.json` and **no kill
> quantity computed, by registered scope** (an endpoint-adjacent figure over n = 3 has no
> registered use before the pilot). The per-arm means, reprinted (triples computed from the
> ledger's unrounded means, then rounded once):
>
> | setting | A mean s | B mean s | C mean s | round triple s | batch at N = 60 | perfect (A/B/C) | identity (A/B/C) |
> |---|---|---|---|---|---|---|---|
> | low | 231.6 | 81.2 | 90.8 | 403.5 | 6.72 h | 0/3 · 2/3 · 0/3 | 3/3 · 2/3 · 1/3 |
> | medium | 298.6 | 123.3 | 112.3 | 534.2 | 8.90 h | 1/3 · 2/3 · 2/3 | 3/3 · 1/3 · 2/3 |
> | high | 433.6 | 181.2 | 174.0 | 788.7 | 13.15 h | 1/3 · 1/3 · 3/3 | 3/3 · 1/3 · 1/3 |
>
> **The rule that chose the setting, named: the operable-condition-match rule.** Choose the
> pinned model's own catalog default tier — the only tier condition-matched to Study 019's
> batch (§2a.6: pinning a HIGHER effort demotes §5.6's dispersion figures from calibration to
> prior; the catalog records `low` as `gpt-5.6-sol`'s `default_reasoning_level`, the tier 019's
> batch implicitly ran at — a catalog inference, not a witnessed fact of 019, exactly as
> `codex.modelNote` records) — PROVIDED the sweep shows that tier operable: all nine of its
> calls complete under the apparatus ceiling with no apparatus code, and the projected batch at
> the registered N fits the 72 h budget. If the default tier fails operability, step upward to
> the first tier that passes — N unchanged, the same budget check applied at each step — taking
> §2a.6's dispersion demotion (and the loss of condition-match the demotion prices) as the
> recorded cost; if NO swept tier passes, the sweep has chosen nothing, no pilot runs, and the
> study halts pre-pilot with the sweep published as its record. `low` passed operability — 9/9
> complete, max call 294.1 s against the 2700 s ceiling, 6.72 h projected at N = 60 — so the
> rule chose **`low`** without reaching either fallback branch.
>
> **When the rule was named, stated plainly.** §2.1 registered pre-sweep that "the chosen
> setting is named with the rule that chose it" — at fill time, not before the sweep. This rule
> is therefore NAMED AFTER the durations and rates existed, and the fill does not pretend
> otherwise. What bounds the operator's hand is not the rule's date but its inputs: a
> registered fact that predates the sweep (§2a.6's condition-match adjudication), a measured
> catalog fact that predates the sweep (the swept-set paragraphs above), and the sweep's
> operability columns (codes, timeouts, durations). Its operability reading is STRICTER than
> the registered abort rule (any apparatus code, not only a first-arm-A ceiling breach) and
> binds nothing retroactively, because all 27 calls were clean under both readings.
>
> **What the rule deliberately does not read.** It does not read the published perfect or
> identity rates: at n = 3/arm those rates cannot support a quality-ranked choice, and a tier
> chosen because its three runs looked good would be the picked-not-swept condition this
> section's swept-set paragraph exists to forbid. One registered decision DOES read rates at
> the chosen condition with this sweep on the record, and it is named rather than denied:
> §2a.4(2)'s minimum viable derived value is declared by the maintainer after the sweep and
> before the pilot — its registered window — so its declarant has seen this table; the review
> round audits the declared number against exactly that exposure. The rates otherwise stand as
> **Tier D description, `citable: false`, outside every population, licensing no direction and
> steering no later decision**: each setting authored at least one gold-perfect run in some
> arm; §3.2's presence-idiom guard **fired in fresh authoring** (four B/C runs across `low` and
> `high` carry `presence-idiom-unsound`, the code's first live firings outside 019's
> retrospective); and at `low`, arm A's profile — 0/3 gold-perfect beside 3/3 identity — has
> the same shape as its 019 near-miss anatomy (0/38 perfect at that batch's bar), an
> observation about a 3-run cell, not a comparison of rates across unequal denominators. The
> 12/arm calibration pilot at the chosen condition (§2a) is the registered instrument for
> rate-based calibration.
>
> **N = 60, and why.** The branch the registration itself prices and certifies: §5.6's Tier C
> size simulation (2,000 replicates; Tier C 0.002 / 0.001 / 0.000 under its three null
> channels) is stated at **N = 60/arm**, as are its observed-validity-gap power ladder's
> central column, §2.1's dual-pricing table and §5.2's realised-n arithmetic illustration — so
> the registered batch runs at the N its own operating characteristics were demonstrated at,
> rather than at a count no simulation in this document prices. (The first draft of this fill
> registered N = 50, 019's round count, on the claim that §5.6's figures were computed there;
> the pre-commit verification pass refuted that claim — §5.6 simulates at N = 60 — and this
> fill was corrected before any registration carried the wrong count.) The sweep's role for N
> is the budget check: at `low`'s observed round triple (403.5 s) the batch prices at
> **6.72 h, 9.3 % of the 72 h budget**, inside the three-UTC-day window with an order of
> magnitude to spare. `harness/PINS.json`'s `batch` block accordingly flips from PORT CARRY to
> REGISTERED at n = 60 / slots = 180, with the order re-derived at 60 rounds by the registered
> search — ten whole Williams blocks, no tail, attained spreads (0, 1), a strictly cleaner
> balance than the 50-round carry it replaces — and `sweep.chosenSetting` carries the choice
> as data. The ledger's own projection lines print the batch at the THEN-CARRIED `batch.n` =
> 50 (5.60 h at `low`), exactly as `budgetProjectionNote` registers; the registered figure is
> this fill's, at 60.
>
> **Re-priced at the chosen setting's own observed durations** (superseding the corrected
> table above's 019-triple illustration):
>
> | line | calls | wall clock at `low`'s observed means |
> |---|---|---|
> | pre-pilot effort sweep (SPENT, all three settings, observed) | 27 | 1.44 h |
> | pilot, 12/arm (C1–C5) | 36 | 1.34 h |
> | D-1/D-2 smoke | ~6 | ~0.22 h |
> | primary batch, N = 60/arm | 180 | 6.72 h |
> | **total** | **~249** | **~9.7 h** |
>
> **The §2a.6 branch this choice takes:** `low` is not "a higher reasoning effort", so 019's
> batch REMAINS condition-matched and §5.6's dispersion figures remain a calibration; the
> pilot's own re-derivation (§2a.6's TODO) still runs and republishes the MDE table at the
> registered N = 60 before the freeze. The condition 019 could not prove is now pinned AND
> witnessed: every sweep call's `CALL.json` stamps the tier, and the witness resolution below
> makes the stamp checkable at gate 5.

**Per-setting abort rule, registered before the sweep.** A setting whose **first** arm-A call
exceeds **2700 s** (the registered per-call ceiling) is aborted after that call; a setting whose
per-arm mean duration projects a primary batch beyond **72 h** at the registered N branch is
recorded as **out of budget** and is not swept further. Aborted settings are published with the
call that aborted them. The sweep's total is capped at **27 calls**; the cap is not raised by a
deviation without a `DEVIATIONS.md` entry naming the reason and republishing the price.

**The three swept settings, registered 2026-08-24, before the sweep — the maintainer's decision.**
The sweep's registered shape (`3 settings × 3/arm`) names a cardinality and no members, and a set
whose members are chosen after the durations are seen is not a swept set but a picked one. The
three settings are therefore registered here, dated, before the first sweep call:

> **The swept set is the pinned CLI's own named reasoning-effort tiers `low`, `medium`, `high`,
> in that order.**

Measured against the pinned binary rather than asserted, on 2026-08-24, with no model call:

- `codex exec --help` at `codex-cli 0.145.0`, digest `sha256:a2a05daf…` (`codex.binarySha256`),
  names **no reasoning-effort flag at all**. The only spelling the pinned CLI accepts is the
  config override **`-c model_reasoning_effort=<tier>`** — `-c` is the argv flag and
  `model_reasoning_effort` is a `ConfigToml` field of this build. This resolved the *spelling*
  half at registration time; the *witness* half needed a call, and the sweep's step zero
  supplied it (the fill below).
- `codex debug models` renders the build's own model catalog offline. Over its **eight** models the
  tier vocabulary is `low`, `medium`, `high`, `xhigh`, `max`, `ultra`; the four universally
  supported ones are **`low`, `medium`, `high`, `xhigh`** (8/8 each), while `max` is absent from
  five models and `ultra` from six. The swept set is the **three lowest of that universally
  supported four**, so it survives whichever model `codex.model` is eventually pinned to.
- Every model's own `default_reasoning_level` lies **inside** that set — `low` for `gpt-5.6-sol`,
  the model Study 019's batch ran, and `medium` for the other seven. The set therefore contains
  the default 019's batch implicitly ran at, and extends from it monotonically upward in cost.

> **CORRECTION OF A CORRECTION (round-1 finding R1-20, 2026-08-24).** These figures were
> registered correctly, then "corrected" wrongly, and are now restored with their provenance
> stated. The pre-sweep registration printed `max` absent from five (3/8 support) and defaults
> `medium` for the other seven — TRUE of `codex debug models --bundled`, the catalog baked into
> the pinned binary and the only build-owned reading. The fill's verification pass recounted via
> plain `codex debug models`, which renders a mutable post-call model CACHE, got 4/8 and
> `medium` ×6 + `high` ×1, and a first correction note replaced the true figures with the
> cache's. R1-20 caught it; the bundled recount confirms the original text, this note replaces
> the erroneous correction at the same prominence, and the lesson is registered where the next
> reader needs it: **a catalog figure claimed as build-owned must come from `--bundled`.** The
> load-bearing facts held through every version — all eight models expose the four swept tiers,
> and `gpt-5.6-sol` defaults to `low`. `harness/PINS.json`'s `sweep.settingsProvenance` carries
> the same restoration.

**Why the set stops below `xhigh`, stated rather than implied.** `xhigh` is as available as the
three swept tiers, so its exclusion is a **budget** decision and not an availability one, and it
is registered as such: the dual-pricing table above (as corrected) already puts a 27-call sweep
at 7.72 h and an `N = 60` batch at 51.46 h *at pilot-like durations under the default effort*, and a fourth tier
above `high` adds nine more calls to a sweep whose own abort rule is written for the case where
the tiers already registered run long. `xhigh`, `max` and `ultra` are therefore **not swept**, and
are reachable only by a `DEVIATIONS.md` entry naming the reason and republishing the price, under
the cap clause immediately above — the same clause that governs raising the 27-call cap, because
reaching a costlier tier is the same act as buying more calls. `max` and `ultra` carry the further
defect of partial catalog support — `ultra` absent from most models, `max` from half — so a sweep
over them would not be a sweep the model pin is free to move within.

**What this registered, and what it did not.** It named the swept SET, which had to exist before
the sweep could run. It did **not** name the chosen condition: that stayed open — the
`codex.reasoningEffort` value and the per-arm N together, both outputs of the sweep — until the
sweep ran and the fill above closed it by the named rule.
Naming three tiers is not choosing one, and the record keeps the two moments distinct.

**Where the set is carried, and the mode's name.** The set is `harness/PINS.json`'s
`sweep.settings` and `harness/batch.py`'s `SWEEP_SETTINGS`; `harness/tests/test_sweep.py` binds
both spellings to this paragraph, so a set edited in one place and not the others fails the suite.
The mode this section calls `--sweep` is the driver subcommand **`harness/batch.py sweep`** — the
subcommand form every other mode of this driver takes — and `PIN_LABEL=SWEEP` is what that mode
claims at the wrapper. The sweep writes under **`sweeps/<UTC date>-effort-sweep/<setting>/arm-<ARM>/run-NNN`**,
outside `arms/` by construction, so R10-1's prior-authoring freeze gate — which derives its paths
from the driver's own `arms/` constants — does not see the sweep's slots and needs no exclusion
list to not see them.

**M-25, ruled as drafted: the sweep's pin state.** `authoring_call.sh:203` refuses while
`codex.model` is null, and `registeredLabelRule` names design-time-resolved pins as checked
*whether or not the freeze has happened* — so a sweep that must run **before** the effort value
exists is either refused or unenforced. Registered: **a distinct `--sweep` label that exempts
`codex.reasoningEffort` alone from the null check**, with each sweep call's setting stamped into
its `CALL.json`, the sweep's outputs `citable: false`, and the exemption **written into the gate
and its test before the first sweep call**. Running the sweep outside the harness is rejected on
sight: that is the 019 failure exactly. `codex.model` and `codex.reasoningEffort` are registered
as **design-time-resolved pins, not freeze pins**; `registeredLabelRule` is restated with the new
member and its null-⇒-PILOT test, moved out of §7's ported-unchanged list, and driven in
`harness/tests/test_pins.py` pin by pin.

**M-24, ruled as drafted: the witness-resolution step, and what the pin can and cannot prove.**
`PINS.json` gains `codex.reasoningEffort` beside `model` / `version` / `binarySha256`; the wrapper
passes it explicitly and `CALL.json` stamps it. **There is no transcript witness to bind it to
today**: 019's `session.jsonl` carries exactly one `turn_context` record whose payload names
`model` and no effort member, and the only occurrence of `reasoning_effort` anywhere is an
override slot holding `null` — against which gate 5's membership idiom (`transcript_check.py`'s `turn-context-mismatch` clauses; a line span cited here before the fill was stale for 020's copy) would refuse every
call. Registered instead: **a witness-resolution step at pin time, run before the sweep**, which
sets the flag and inspects the resulting `session.jsonl` for a non-null member naming the effort.

- **If one exists**, transcript gate 5 is extended to it with the same `turn-context-mismatch`
  reason tag and the same **apparatus-side** classification.
- **If none exists**, the effort pin **is registered as a `CALL.json` self-report where no
  transcript witness exists, with `reasoning_output_tokens` entering C4 as a band. A pin nobody
  can check is a recorded intention, and this preregistration says so.** The condition is
  *asserted by the wrapper and not independently witnessed*, and that sentence travels with every
  published record of the condition. 019's medians, for the band's calibration: **A 2067.5** over
  48 runs, **B 502.5** over 38, **C 696** over 39.

> **The witness-resolution outcome — BOTH HALVES CLOSED.** The FLAG'S SPELLING half is
> **CLOSED, 2026-08-24**: the pinned CLI exposes no reasoning-effort flag, and the registered
> spelling is the config override `-c model_reasoning_effort=<tier>`, carried as
> `codex.reasoningEffortFlag` (`-c`) and `codex.reasoningEffortConfigKey`
> (`model_reasoning_effort`) so the wrapper still reads it from the registry and still refuses to
> guess it. The WITNESS half is **CLOSED, 2026-08-24 — branch `gate-5-extension`**, resolved as
> registered: step zero of the sweep, over the FIRST sweep call's own retained transcript
> (`sweeps/2026-08-24-effort-sweep/low/arm-A/run-001/session.jsonl`,
> `sha256:78983d57099d078231622b24005ea28e7daeaee96c7c99c16ceeb53cc785cb01`). The
> `turn_context` record carries TWO non-null members naming the effort —
> `collaboration_mode.settings.reasoning_effort: "low"` and top-level `effort: "low"` — with
> zero null occurrences and zero occurrences outside `turn_context`. The registered resolution
> is run-001's, exactly as the step registers; the 26 sibling transcripts are retained beside
> it, each carrying the same members with its own setting's tier, re-derivable by any reader
> from the published slots (and re-derived exhaustively by this fill's verification pass —
> a check on retained bytes, not a second resolution). The effort pin is therefore NOT a self-report, and the
> corresponding gate-5 change lands with this fill, before the primary batch, exactly as
> registered: `harness/transcript_check.py`'s gate 5 binds `codex.reasoningEffort` beside the
> model and the cwd — by path, over both witnessed spellings, over EVERY `turn_context`, with
> the same `turn-context-mismatch` reason tag and the same apparatus-side classification, and
> with a member PRESENT-AND-NULL (019's actual shape) being neither a witness nor a mismatch,
> mirroring the sweep step's own null-is-not-a-witness rule. The self-report band
> (`reasoning_output_tokens` into C4) is NOT taken and stands as the registered
> branch-not-taken. One citation correction travels with this fill: the pre-resolution text
> above cited `transcript_check.py:603-608`, a line span true of 019's copy and stale in
> 020's (the port note shifted the module by nine lines); the published `SWEEP.json` note
> carries the same stale span as immutable published bytes, and `DEVIATIONS.md`'s operational
> record notes it — the clause is the gate's `turn-context-mismatch` membership idiom,
> wherever it sits.

## 2a. Calibration under registered conditions — C1 to C5

### 2a.1 Why 019's pilot cannot be reused: the differences are five, not three

019's `design/pilot/pilot_run.py` called codex with **no `env=`**, no `-m`, no
`--ignore-user-config` — inheriting the operator's `$HOME`, `~/.codex/config.toml` and
`$HOME/.agents` skills, none of which are recorded — while passing `env=clean_env(workdir)` to
*every* engine call: **the engines were isolated; the model call was not.** Five recorded
differences: `--ignore-user-config` (absent → present); `-m <model>` (absent → pinned); sandbox
(**read-only → workspace-write**); `--skip-git-repo-check`/`--color never` (present → absent);
environment isolation (none → fresh `$HOME`, `env -i`, isolated `CODEX_HOME`, recorded
`isolatedHomeInventory`). The sandbox difference is the one most directly tied to the test-row
gap — a read-only sandbox cannot write or execute the suite it is drafting.

Three eliminations, each re-derived: **prompt bytes are not the cause** (three matched
`sha256sum` pairs); **N is not the cause** (P(pilot 5/5) is 4.72 × 10⁻⁴ for B and 5.96 × 10⁻³ for
C; for arm A the registered rate is 0/38, and the rule-of-three 95 % upper bound 3/38 is a bound,
not a p-value); **gold growth is not the cause** (the pilot's 76 ids are a strict subset of the
117 with no shared row's expectation changed, and restricting every registered run to those 76
rows gives perfect counts A 0/36, B 8/30, C 14/30 — identical in every arm). The mechanism is a
tight inference from converging observables, **not a measurement**: the pilot's `CALL.json`
carries no `model`, no `binarySha256`, no `cli`, and no `session.jsonl` exists pilot-side at all.
**019's pilot compute condition is unrecoverable**, and service-side drift over 2026-08-15 →
2026-08-21 cannot be excluded for the same reason. *"Recover pilot-like behaviour" is withdrawn
as an objective* — the pilot's defining property was that isolation was absent, and targeting a
condition characterised by missing isolation is not a coherent goal.

**An independent second defect: 5/5 never licensed 0.60.** 019 §5 justified its E1 floor with
"pilot 15/15", which is the **pooled** figure; the floor was applied **per arm**, where the
evidence was 5/5, whose exact one-sided 95 % Clopper–Pearson lower bound is **0.549 — below the
0.60 it was cited to support**. Two independent calibration errors, either sufficient alone to
produce a `control-gate-failed` attempt.

| n | clean sweep | one miss | two misses |
|---|---|---|---|
| 5 | **0.549** | 0.343 | 0.189 |
| 8 | 0.688 | 0.529 | 0.400 |
| 10 | 0.741 | 0.606 | 0.493 |
| **12** | **0.779** | **0.661** | 0.562 |
| 15 | 0.819 | 0.721 | 0.637 |

### 2a.2 C1 — one driver, and the pilot's pin state registered as a difference

`design/pilot/pilot_run.py` is **deleted, not ported**. The pre-freeze pilot runs through
`harness/authoring_call.sh` and `harness/batch.py` under a `--calibration` mode. **The registered
differences between the pilot and the primary batch are exactly four**, and they are enumerated
here so a fifth cannot be discovered later: output under `calibration/<label>/`; the pilot slot
count; `citable: false`; and the pin state (§2.1's design-time-resolved rule). Pilot N: **12/arm**
(CP lower bound 0.779 on a clean sweep, from the table above).

**AMENDED (round 1, R1-17) — the mode's landed spellings.** The `--calibration` mode registered
above is the driver subcommand **`harness/batch.py pilot`**, claiming **`PIN_LABEL=PILOT`** at the
wrapper — the registered labels are now PRIMARY, SWEEP and PILOT, and the wrapper's PILOT branch
shares every effort rule with PRIMARY (no exemption, no threaded setting: the fourth registered
difference is the design-time pin-state rule *applying*, not relaxing) while anchoring slots at
`calibration/<UTC date>-pilot/arm-<ARM>/run-NNN` and stamping `citable: false`. The driver
publishes `PILOT.json`/`PILOT.md` after every call and computes no rate; the per-arm counts are
computed post-hoc by `harness/pilot_rates.py` through the registered scoring components (the
§2.1 rates scope: **no kill quantity**, by construction — a scope that binds `pilot_rates.py`,
the go/no-go's publisher; §2a.6's post-pilot analysis pass computes per-run kill records under a
closed no-peek schema, round 2) and published as
`calibration/<label>/PILOT-RATES.json` — the record validated by the sealed
`calibration/derive_floor.py`'s own `validate_record()` at publication AND at the freeze gate
(`make_manifest.calibration_record_problems()`), so the producer and the go/no-go's consumer
cannot drift apart. `batch.py pilot` refuses while `calibration.minimumViable` or
`calibration.minimumViableBasis` is undeclared — §2a.4(2)'s ordering, enforced rather than
promised — and refuses a second pilot under §2a.6's one-pilot rule. The wrapper's `PILOT` and
`integrity.study_label()`'s `PILOT` deliberately coincide: a calibration-pilot call is a call
under a registry whose freeze pins are null, and a state where the two spellings disagreed would
be a pilot running after the freeze, which this section's ceremony order forbids.

**AMENDED (round 2, R2-10) — the pilot slot count names two numbers.** "Pilot N: 12/arm" above
is read as **12 apparatus-clean calls per arm, drawn under a registered attempt cap of
21/arm (63 attempts)** — at most 21 attempts per arm. The 12 is the denominator §2a.1's table
prices the derived floor at, and it was never a different number; what the first printing left
implicit was that an apparatus refusal inside those 12 was counted as a Bernoulli failure. At
Study 019's own per-arm apparatus rates the probability that all three arms reach 12 clean calls
within 12 attempts is ≈ 0.0001, so a fixed-12 denominator made §2a.4(2)'s 0.20 gate fire on
apparatus noise about half the time (the reviewer's ≈ 52 % figure) — study death by design.
Under the amended rule every attempt is retained, sealed and published with its §1a code; the
scored 12 are the apparatus-clean ones (§1a's population rule, "attempted runs whose apparatus
succeeded", applied to the pilot exactly as to the batch); and an arm still short of 12 clean at
the cap **publishes no rates and is a `DEVIATIONS.md` event** — under M-9 the study ABORTS
rather than descopes. The cap is 21 because P(all three arms reach 12 clean) is 0.95 there —
the study's own α — at 019's rates (0.68 at 18, 0.90 at 20, 0.995 at 24); its cost at `low`'s
observed means is ≈ 2.35 h against the 1.34 h the §2.1 budget rows carry, and §2.1's budget note
records the difference. Nothing about the declaration moves: 0.20, `identityFloor`, ≥ 6/12, the
≈ 6 % pricing and the 0.82 catch probability all stand, because they were always correct for the
population §1a registers and 019 published (34/38, 26/37, 28/39). The driver's order is an
A-first round robin over the arms that still need a clean call (`batch.pilot_next_entry()`),
derived from the ledger's own codes so the freeze gate can RECONSTRUCT it rather than compare
it to a constant.

**AMENDED (round 2, R2-8) — the pilot runs the batch's per-slot finalization, and the golden
capture precedes it.** The driver's duties enumerated above stopped at "publishes
`PILOT.json`/`PILOT.md` after every call"; the wrapper delegates the refusal record, the
schedule stamps, the transcript binding and the seal to its driver, and a pilot that skipped
them was a FIFTH difference from the batch. So `batch.py pilot` runs, for every attempt and in
the batch's order, `refuse_slot` → `stamp_slot` → `bind_transcript` (completed calls only) →
`seal_slot` → a chained `ledger_record`, and `PILOT.json` is written atomically as a hash chain
in schedule order with a header mirroring `arms/BATCH.json`'s. Two consequences are registered
with it. (i) **The golden-context capture is a precondition of the pilot**, not only of the
batch: the binding's gate 4 (the golden pre-prompt context) runs unconditionally, so a pilot
bound with no capture would file every slot as unreadable apparatus, and "binds gates 1, 2, 3
and 5 but not 4" would be the fifth difference this section forbids by name. The isolation
negative control remains a precondition of the batch alone. (ii) **Every call's `pinsSha256`
reconciles to the ledger header's**, which records the digest of the registry the pilot ran
under — not to the registry at freeze time, because this section's own ceremony edits the
registry after the pilot (label, N and output digest go in). `harness/pilot_rates.py` reads the
sealed slots through the primary path's pre-scoring order (seal, wrapper outcome, registry
stamp, golden stamp, recomputed transcript binding, completion presence) before it scores; an
author protocol violation — for which the wrapper writes no completion by design — is COUNTED
under its authoring code and scores zero, never filed as the apparatus code `slot-shape`. What
"validating a registered pilot output" means at the freeze gate (R2-7) is therefore: the ledger
is the driver's; its records are the round robin replayed from their own codes and its chain
verifies; every slot's seal recomputes to the record's digest; no slot exists that the ledger
does not name; every completed slot's sealed `CALL.json` carries the scheduled arm, slot index,
`PILOT` label, `citable: false`, the header's registry and golden digests, the pinned arm prompt
and the pinned reasoning effort; and the counts record's rows are exactly the ledger's slots,
with each per-arm cell reconciled to its rows and any embedded verdict equal to its own
recomputation. `calibration/derive_floor.py` was edited before the pilot ran to carry the
row-reconciliation half of that contract; the pre-pilot edit is lawful under §2a.4(1) ("sealed
before the pilot runs") and is recorded in `DEVIATIONS.md`'s operational record.

### 2a.3 C2 — pin the compute condition, bind it, register what the binding proves

Registered in §2.1: the pin, the wrapper flag, the `CALL.json` stamp, the witness-resolution step,
and M-24's self-report branch with its band.

### 2a.4 C3 — derive the go/no-go, do not choose it

House precedent is SCAFFOLD item G3: `leak_tokens.py` derives its screen mechanically and then
proves the derived list has power. Applied here:

1. **A committed `calibration/derive_floor.py`, sealed before the pilot runs**, emitting any
   threshold from the pilot's own per-arm counts by an exact Clopper–Pearson rule, with **no human
   number entering**.
2. **A minimum viable value declared in advance**, below which the study does not freeze. Under
   M-9's ruling the below-minimum branch **aborts** rather than descopes.
   > **FILLED, 2026-08-25 (round 1, R1-17) — the declaration.** **`calibration.minimumViable =
   > 0.20`, bound to the IDENTITY floor (`minimumViableBasis = "identityFloor"`)** — the
   > maintainer's declaration, made after the sweep fixed the compute condition (§2.1: `low`)
   > and before any pilot call, with `batch.py pilot` refusing to spend a call while the
   > registry did not carry it. **Why the identity floor and not the perfect floor:** §5.7
   > registers arm A's imperfection as a REPORTED RESULT (019: A 0/38 perfect), so a
   > perfect-rate minimum over all arms would abort by design — the declaration would
   > contradict the registration's own stance; identity-passing is what feeds the per-protocol
   > population (§5.2), which is the instrument this gate protects. **Why 0.20:** GO requires
   > the derived floor to reach 0.20 in every arm, which at n = 12 means **≥ 6/12**
   > identity-passing (6/12 floors at 0.245; 5/12 floors at 0.181 and fails). Priced before
   > the pilot: at 019's registered identity rates (A 0.895 / B 0.703 / C 0.718) the three-arm
   > false-abort risk is ≈ 6 %, against ≈ 19 % at the next rung (≥ 7/12, min 0.30); a true
   > rate of 1/3 — the C arm's swept n = 3 point at `low` — is caught with probability 0.82,
   > and 1/4 with 0.95. The abort is study-death under M-9 (no descope), so the gate is set to
   > catch COLLAPSE; thin-but-alive arms are the business of §2a.6's recomputed dispersion
   > table, a separate pre-freeze instrument. The declared pair lives beside its provenance in
   > `PINS.json`'s `calibration` block, is read by `calibration/derive_floor.py`'s go/no-go
   > and by the freeze gate's record validation, and no post-batch row reads it (item 3
   > below).
3. **The threshold's seat is a pre-freeze go/no-go, and only that.** Under M-23 (§5.7) there is no
   author-side control gate on the batch, so no post-batch row reads this value.

**C3(iii)'s degradation control is not registered as a batch control.** 019's proposed
reference-side degradation **provably cannot fail the gate it certifies** (re-derived:
`retired_x1` selects exactly 5 of 117 rows; under repair-removed gold the per-arm best runs score
2 / 5 / 5 = 0.9829 / 0.9573 / 0.9573 and the existence gate **holds in all three arms**, with arm
A *unchanged* because the degradation makes arm A's dominant failure mode correct). The retarget
to a stimulus-side degradation (shared prose header, prompt assembly, naming appendix) is
registered **conditionally**: it exists only in a branch where an author-side gate is
reinstated — which M-23 = (a) forecloses, and which the brief's own cost table prices at +180
authoring calls. Reinstatement requires a `DEVIATIONS.md` entry, publication of the computed
per-arm miss-count shift **before** the pilot runs, budgeting as authoring calls, and either
running at the batch's realised n or stating the arithmetic gap per §5.7.

### 2a.5 C4 — the transfer gate, at decision row 1, two-sided, with derived bands

A condition mismatch is an apparatus fact, not evidence about the arms, and 019's
`control-gate-failed: e1-floor` verdict actively misleads on this — it reads as *the arms are bad
at the task*. Bands are derived from **within-condition** dispersion (bootstrapping medians-of-12
from 019's registered batch, 4,000 resamples, seed 3, executed calls only), never chosen:
duration spans [0.930, 1.083] / [0.960, 1.080] / [0.920, 1.067]; completion bytes
[0.926, 1.106] / [0.917, 1.059] / [0.941, 1.043]; `reasoning_output_tokens`
[0.857, 1.169] / [0.846, 1.193] / [0.727, 1.177]. Registered bands are ~2.5× the measured span
for the two rows with demonstrated power and ~2.7× for the reasoning-token row, set **before** the
pilot from this dispersion.

| Observable | Source | Band | Power against the 019 mismatch |
|---|---|---|---|
| model, CLI version, binary sha256, reasoning effort | `CALL.json`; `session.jsonl` `turn_context` where a witness exists (§2.1) | exact equality | **none** — the 019 pilot `CALL.json` records none of them |
| sandbox policy, `codexHomeIsolated`, `environmentScrubbed`, isolation inventory | `CALL.json` | exact equality | **none** pilot-side in 019; **descriptive** for any 019 comparison, **gating** for 020's own pilot |
| per-arm median call duration | `CALL.json` `startedAt`/`endedAt`, executed calls only | [0.80×, 1.25×] | **fires**: 8.3–10.7× |
| per-arm median completion bytes | `completion.txt`, same cohort | [0.80×, 1.25×] | **fires**: 0.53–0.67× |
| per-arm median `reasoning_output_tokens` | `session.jsonl` | [0.65×, 1.55×] | cannot be evaluated against 019 (no pilot `session.jsonl`); registered for 020 |

**C4 is two-sided.** *If every exact-equality row holds and only band rows differ, the pilot is
suspect and the outcome is `calibration-invalid`, ~~requiring a re-pilot under C5~~; if any
exact-equality row differs, the batch is suspect and the outcome is `pipeline-invalid`.* Both
outcomes are recorded with the rows that produced them. **AMENDED (round 2, R2-12):** the
struck clause named no reachable state — `calibration-invalid` is observable only during the
primary attempt, of which there is exactly one — so the outcome is recorded with the rows that
produced it and reaches §5.9 row 3, which is terminal. The two-sided ROUTING is untouched.

**AMENDED (round 2, R2-11) — the gate now exists, and four things the table left implicit are
registered.** The gate was in `decision.CONTROL_GATES` and produced by nothing, so every attempt
would have failed as "not evaluated" and neither branch above could occur. It is produced now:
`harness/e4lib/transfer.py` reads both sides through ONE reader, `harness/pilot_analysis.py`
publishes the pilot side as **`calibration/<label>/C4-REFERENCE.json`** after the pilot and
before the freeze (pinned at **`calibration.c4ReferenceSha256`**, a freeze pin), and
`harness/score.py` reads the batch side from every present executed slot at attempt time,
compares, publishes `transferGate` in every outcome, and routes: an unequal exact row (or a side
that disagrees with itself) is `pipeline-invalid` at row 1, with the band rows still computed
and published; otherwise an out-of-band or unevaluable band cell is `calibration-invalid` at
row 3; otherwise the gate holds. An absent, unpinned or non-validating reference is itself a
row-1 problem — §6: a gate the scorer did not evaluate fails. The four registrations: **(i) two
band rows, not three** (maintainer ruling on R2-11(A)): the `reasoning_output_tokens` row above
is ~~[0.65×, 1.55×]~~ struck as a gating row, because §2.1's M-24 fill registered the
self-report band as NOT taken once the witness resolution landed on the gate-5-extension branch
and the two sentences contradicted each other; the per-arm token median is still published on
both sides as a descriptive quantity that no gate reads. **(ii) The cohort** is executed calls
only — a slot whose wrapper wrote a `CALL.json` with a resolvable duration — which is
`design/BRIEF.md`'s own cohort (the exit-126 records carried `durationSeconds: null` and were
outside the 199 / 75 / 75 s triple). **(iii) The median** at even n is the mean of the two
middles, stated because the pilot's n is 12. **(iv) The ratio** is pilot ÷ batch and the band is
closed at both ends, so 019's mismatch reads 1660.184 / 199 = 8.34× exactly as the power column
prints it. The eight exact rows are `model`, CLI version, binary sha256, reasoning effort (each
from `CALL.json`; the transcript witness is gate 5's business per slot), sandbox policy (the
`--sandbox` argv token), `codexHomeIsolated`, `environmentScrubbed`, and the sorted isolation
inventory.

### 2a.6 C5 — one pilot, sealed, terminal

The pilot runs once; label, N and output digest go into `PINS.json` before the primary attempt
— and, **AMENDED (round 2)**, so do the two post-pilot analysis artifacts' digests
(`calibration.c4ReferenceSha256`, `calibration.dispersionSha256`), and **all five calibration
members are FREEZE PINS** read by `integrity.study_label()`: this sentence was enforced by no
label rule before round 2, and a REGISTERED attempt was reachable with every one of them null.
**There is no second pilot.** A `calibration-invalid` outcome at C4 is terminal under §5.9 row 3,
exactly as any control-gate failure is.

> **AMENDED (round 2, R2-12) — the first printing's rule, struck and kept for the record.** It
> read: *~~A second pilot requires a `DEVIATIONS.md` entry naming the reason, and then the
> derived threshold is the maximum over all pilots and the transfer bands are the tightest over
> all pilots, with every pilot's rates published side by side. Re-piloting is monotone in
> strictness.~~* It named no reachable state: `calibration-invalid` is observable only at score
> time; §"The freeze and the primary attempt" registers exactly one primary attempt; and
> `make_manifest.prior_attempt_problems()` refuses re-freezing any tree carrying an entry under
> `results/`. A promise with no reachable state is worse than no promise — it made C4's
> two-sidedness read as a recoverable branch when it is terminal on both sides — so the promise
> is removed rather than the machinery built.
>
> **And one sentence added, for the state that was unrecoverable by typo.** A pilot label under
> which **no call completed** — every attempt wrapper-refused, or no ledger at all — spent nothing
> and is not the one pilot: it is ABANDONED by `batch.py abandon --label <label>` after a
> `DEVIATIONS.md` entry names it, and the tree is retained under `calibration/abandoned-<label>/`,
> never deleted. The driver refuses to abandon a label holding even one completed call; the
> freeze gate skips abandoned trees in the one-pilot count and refuses one that hides a
> completed call.

**Pinning effort undermines the dispersion calibration, and the adjudication is registered.** If
020 pins a higher reasoning effort, 019's batch is no longer condition-matched and §5.6's
dispersion figures become a **prior, not a calibration**. Registered: pin the effort explicitly,
and **re-derive the dispersion from the pilot at the pinned effort**; 019's SDs are a fallback
prior and are labelled as one wherever they appear.

> **LANDED (round 2, R2-13; maintainer ruling: implement, shared pass, σ stands beside the
> prior).** `harness/pilot_analysis.py` — the same post-pilot pass that publishes the C4
> reference — scores the apparatus-clean pilot slots through `score.score_run()`, the ONE scoring
> path, builds units exactly as `score.registered_family()` does, and publishes
> **`calibration/<label>/PILOT-DISPERSION.json`** (pinned at `calibration.dispersionSha256`, a
> freeze pin): for each of the eighteen registered members, σ on its registered basis (pooled
> within-arm, N − k; residual, N − 4, for the adjusted members), the degrees of freedom, the exact
> two-sided 95 % χ² interval for σ (`e4lib/dispersion.py`), and the MDE at the pilot's own n and
> at the registered N (each arm's realised n derived from the pilot's own membership fraction for
> that member's population — a size, not a direction). **It computes no contrast, no test and no
> direction**: it never calls `family.score_member()` or `family.family_report()`, its schema is
> closed, and a no-peek gate refuses publication — and the freeze — if any member at any depth is
> a difference, sign, p-value, rejection, interval, mean, contrast, verdict or claim. §2a.2's
> "no kill quantity, by construction" is scoped to `pilot_rates.py`, the go/no-go's publisher;
> this pass necessarily computes per-run kill records, and the closed no-peek schema is what
> makes that not a peek. **§5.6's 019 table stays as published, labelled the fallback prior; the
> recomputed table is appended to §5.6 from this file's bytes by the ceremony, with df and
> interval per row, and stands BESIDE the prior rather than replacing it** — the pilot estimate is
> materially less precise (χ² factors [0.739, 1.548] at the per-protocol floor against
> [0.876, 1.171] on 019's 88 runs), and "recomputed" is not "better". The registered planning
> statements of §5.6 (the binding MDE ≈ 0.165; 80 %-powered against ≈ 2 / ≈ 9 classes) therefore
> stand on the prior and are reprinted beside the pilot's figures, not replaced by them. The
> ceremony step is: pilot → `pilot_rates.py --write` → `pilot_analysis.py --write` → pin the
> three digests → freeze.

## 3. Arms and prompt materials

### 3.1 Ported unchanged from Study 019

| Arm | Artifact pair | Suffix materials |
|-----|---------------|------------------|
| A | Judgment Pack (specVersion 0.2.0-draft) + matrixVersion-2 test matrix | full spec + schema verbatim; task instructions |
| B | Rego v1 policy + opa test file | full OPA doc pages verbatim; **result-shape-only floor contract**; task instructions |
| C | Rego v1 policy + opa test file | same doc pages; **the full prescribed judgment convention** (the same result shape as a JSON Schema, PLUS five substantive conventions: a registered default decision, totality, explicit precedence, unresolved handling, grounds behaviour); task instructions |

Shared header, byte-identical: the policy prose and the naming appendix. Excerpt parity is
full-verbatim, not curated. `deformalize.py` generates B's contract from C's schema and
byte-equality with the generator's output is a freeze test. **No formality-only claim about the
B/C difference appears anywhere in this registration.** Authoring is **single-shot, no tools, no
repair**; artifact extraction is the registered marker rule. System boundary: in-system = what
the pinned binary does at evaluation time; out-of-system = anything requiring an authoring loop.

**M-4, adopted: 020 does not repair the stimulus.** The seven construct rows' lemma cost is the
finding (§4.2); repairing it silently changes the estimand, and stating the region lemma in the
prose would edit the byte-identical shared header and therefore the treatment in all three arms.
If the maintainer wants it, it is a separate registered study with its own pilot.

### 3.2 The presence-idiom guard (M-14), and why it is not prose

**The M-14 forensic verdict, 2026-08-23, is the reason this section exists.** A focused read of
019's `arms/B/authoring/run-011/` against a perfect arm-B run found neither candidate mechanism
but a third, proven both ways: **one Rego language-semantics error — `"key" in object` tests
values, not keys — is the arm-B/C E1 collapse.** The presence test gating U1
(`"riskScore" in input.vendor`) is false even when the member is present, so every input is judged
unreadable, the candidate sweep fires on every row, and the grid almost never collapses to a
singleton → `unresolved:[unknown]`. Evidence, bidirectional: run-011 reproduces `RESULTS.json`
exactly (31/86/0); repairing only that operator takes it to 117/117 and, across all 40 affected
runs, makes 26 perfect and improves 32; mutating the correct idiom out of 8 perfect runs collapses
**8/8** to the exact observed signature including the `eval_conflict_error` pattern.
Discriminator: **40 of 76 B+C policies use bare-object `in` → zero perfect; all 22 perfect runs
avoid it.** The ROW-ERRORs are the same bug's conflict face (B 94 %, C 100 % — and C's 89 are a
single run), not a second mechanism. Counterfactual E1 under this one repair: **B 0.267 → 0.800,
C 0.467 → 0.767 — both hold the 0.6 floor.**

**More prose is demonstrated ineffective, and that is measured, not argued.** Neither of 020's
planned repairs touches this: the wire-form contract was already stated and followed, **and the
prompt's bundled Rego reference already flags the exact trap (`"foo" in {"foo": 1} # false`) yet
it fired in 40 of 76 runs.** A guard that consists of more words in the prompt is therefore
registered *out*: the empirical rate of the bundled warning is 40/76 ≈ 0.53 failures despite the
warning, and 020 will not register a control whose only demonstrated operating point is that one.

**Registered decision: the guard is at ADMISSION level, in the scorer, and it is a detector — not
a repair, not an exclusion, and not a prompt edit.**

- **What it does.** `harness/e4lib/presence_idiom.py` (new; §7) parses each admitted arm-B/arm-C
  policy under `opa parse --format json` and flags any `in` term whose right operand is, on the
  syntax tree, an **object** (or a reference resolving to an object member of `input`) rather than
  a set or array. A run the detector flags receives the registered authoring-outcome code
  **`presence-idiom-unsound`** (§1a's table, E2's ordered table): **valid, counted, and scoring
  zero on every endpoint it reaches, exactly as the other authoring codes do.**
- **What it does not do.** It does not rewrite the operator (that would change the authored
  artifact, i.e. the treatment); it does not exclude the run (that would delete an authoring
  outcome); it does not gate the batch; and it emits no prompt-side text. Single-shot authorship
  admits no repair loop, so an "author-checklist" variant of this guard is a prose variant and is
  rejected on the measured ground above.
- **Why admission and not engine level.** An engine-level guard would have to change what the
  pinned OPA binary does, which is out of the registered system boundary (§3.1) and would break the
  binary digest pin. The admission layer is where 020 already classifies what the author emitted.
- **The registered arm asymmetry, and its ceiling.** The code is structurally unreachable in arm A:
  arm A's format has no analogous single-operator trap on this surface. **This is registered as a
  ceiling (§11.11), not repaired.** Arm A's own near-miss profile in 019 (92 % row accuracy, zero
  faults) stands **unexplained** by this mechanism and is published as Tier D material —
  descriptive, direction-free, and no decision reads it.

**The obligation, and it is a freeze gate — SATISFIED for all five of (i)–(v).**
`GATE(pre-freeze)`: **the guard is registered with its own power analysis, computed and published
before the freeze.**

> **The registration condition, AMENDED 2026-08-24 (round-1 finding R1-9; ruled by the
> maintainer; PENDING round-2 review, and if round 2 refuses the amendment the kill switch
> flips false and the guard demotes to Tier D).** The original condition read: if the detector
> cannot meet (i) and (ii) exactly — 40/40 and 0/22 — the guard is not registered at all. The
> measurement is 39/39 on every policy the pinned parser accepts and 32/32 on the registered
> operating set, with the fortieth in-class policy (`B run-040`) refused by `opa check` before
> any admission-level detector can see it. R1-9 is right that receipt of SOME authoring code is
> not detector sensitivity, and the round-1 power analysis blurred that. The amended condition,
> stated prospectively and to be applied to the re-run certification (R1-10's detector repairs
> force a full re-run of all five quantities): **(i-a) the detector flags every in-class policy
> in its registered operating set (the admitted policies) exactly — n/n; (i-b) every in-class
> retained run receives a registered authoring code from the admission chain — 40/40, the
> detector's code or an earlier one; (ii) 0/22 perfect runs flagged, unchanged.** The amendment
> is the condition an admission-level detector could ever have met on this corpus — a policy
> the parser refuses is structurally unreachable, by the same §3.2 order that makes the guard a
> detector and not a repair — and it is registered AFTER the first measurement was seen, which
> is why it does not certify anything by itself: the re-run certification under R1-10's
> repaired detector must meet it fresh, and round 2 must bless the criterion, before the
> switch's `registered: true` stands. **The fresh run is EXECUTED (2026-08-24, recorded in
> `harness/POWER-PRESENCE-IDIOM.md`'s re-certification section): the repaired detector
> reproduces every certified figure exactly — 39/39, 178 uses, B 19 / C 13 with the pinned
> set-identity digest, 0/22, 0/392, zero non-string probes in the corpus — so (i-a), (i-b)
> and (ii) hold under the amendment, all three R1-10 defects measured latent, and only
> round 2's blessing remains outstanding.** The analysis is mechanical and its inputs already exist in 019's frozen tree,
so it was an obligation with a deadline rather than a hope; it has been executed and is published
at `harness/POWER-PRESENCE-IDIOM.md`, with the numbers reprinted in the filled entry below and
`harness/PINS.json`'s `presenceIdiomGuard` block carrying the verdict as data. (iv) was the last
to fill: it was blocked on the family scorer (§7 delta 5) and is now computed by the registered
script `harness/counterfactual_shift.py`. It must report, at minimum: (i) **sensitivity** — the detector run over 019's 76 retained
B+C policies must fire on the 40 that use bare-object `in`; (ii) **specificity** — it must fire on
**none** of the 22 perfect runs; (iii) the **false-positive rate on lawful `in` uses** (over sets
and arrays) across the same 76 policies and across both reference implementations; (iv) the
**counterfactual per-member shift** on 019's batch — every one of §5.2's eighteen members
recomputed with the flagged runs coded `presence-idiom-unsound`, published beside the unflagged
figures, so the code's effect on the family is a measured quantity rather than an assumption; and
(v) a **mutation check** in the program's standing discipline: break the detector, confirm the
test that certifies it fails, and label any assertion that cannot discriminate.

> **FILLED — all five of the presence-idiom guard's power-analysis numbers.** The detector exists
> (`harness/e4lib/presence_idiom.py`), it was run over Study 019's retained arm-B/arm-C
> policies with the pinned binary, and the analysis is published in full at
> **`harness/POWER-PRESENCE-IDIOM.md`**, which is a registered document (`harness/
> make_manifest.py`) and a `CORRECTION-TARGETS.md` entry.
>
> **The kill switch did NOT fire and the guard IS registered.** `harness/PINS.json`'s
> `presenceIdiomGuard.registered` carries that verdict as data, and
> `harness/e4lib/admit.py`'s `guard_is_registered()` — fail-shut toward not-registered — is the
> only code that reads it.
>
> | | result |
> |---|---|
> | **(i) sensitivity** | **40/40 in-class runs receive an authoring code.** The in-class set was re-derived from the policy SOURCE BYTES by an independent oracle sharing no code and no input representation with the detector, and it is 40 of the 76 — arm B 21, arm C 19 — reproducing M-14's discriminator by a method M-14 did not use. The detector flags **39/39** of the policies the pinned parser accepts and **32/32** of the admitted policies, the population §3.2 registers it to run over; the fortieth (`B run-040`) is refused by the parser and receives the earlier registered code `unparseable-artifact`. Agreement with the oracle is exact at the USE level too: 178 flagged uses against 178, with zero per-run count mismatches over all 73 parseable policies. |
> | **(ii) specificity** | **0/22 perfect runs flagged**, in every population; all 22 parse and all 22 are admitted. |
> | **(iii) false positives on lawful `in`** | **0/392 lawful uses, 0/15 over sets and arrays** — the two forms this section names. 599 membership terms were read over the 73 parseable policies: 248 presence tests (178 flagged, 38 lawful over set-returning calls, 3 over non-object names, 29 unclassified — 178 + 38 + 3 + 29 = 248) and 351 iterations and bindings, none flagged. 29 uses are UNCLASSIFIED and none is flagged: an unresolvable name is reported, never guessed at. |
> | **(iv) counterfactual per-member shift** | **COMPUTED** by the registered script `harness/counterfactual_shift.py` (reproduced by `harness/tests/test_counterfactual_shift.py`; full 36-row table in `harness/COUNTERFACTUAL-SHIFT.json`). The flagged set is **derived, then gated**: the script re-runs the certified detector over the 60 admitted 019 policies and refuses to publish off the certified counts — **32 of 60, arm B 19 of 30, arm C 13 of 30** (this document first printed the split as B 15 / C 17; that was unmeasured arithmetic, the gate refused it, and the correction note in `harness/POWER-PRESENCE-IDIOM.md` §(iv) records the reconciliation — every other certified figure stands). The recode is the registered one: identity false, no kill record, exactly as the other authoring codes present. **Measured effect (A–C), REGENERATED round 2 under the registered estimand (R2-2, native-for-both; the file names the estimand it was computed under):** every ITT member amplified (+0.168 … +0.210), every unadjusted PP member attenuated (−0.031 … −0.006), PP/ANCOVA within ±0.015 (−0.008 … +0.015 — M18, L2c/excl, is the one adjusted member whose shift is now POSITIVE; the first printing, under the superseded hybrid, had all six adjusted shifts in −0.008 … −0.002); exactly two α = 0.05 decisions flip, **M2 and M5** (L1/PP, both columns: p 0.0213 → 0.3483), from reject to not-reject — unchanged. A–B: ITT +0.246 … +0.303, PP \|shift\| ≤ 0.020. The unflagged column reproduces the REGISTERED reading — fifteen of Reprint 1's rows to the printed digit for every point estimate and unadjusted p-value, to the decision boundary for the six ANCOVA p-values per §5.5's marked R1-6 scope note, and the three excluded-column L2c rows at the figures §5.2's F-1 re-ruling states (M17 A–C +0.0839) — pinning the script's adapter to the fixture adapter. The effect is **direction-heterogeneous by population** — ITT away from the null, unadjusted PP toward it — so no single-direction story about the guard's effect is licensed. The JSON is manifest-covered since round 2 (R2-16). |
> | **(v) mutation check** | Break the detector by dropping the object-type branch: flagged runs fall **39/39 → 23/39** and flagged uses 178 → 83, so condition (i) fails and the certifying measurement discriminates. Driven in CI as `harness/tests/test_score_presence_idiom.py::test_breaking_the_object_branch_makes_the_sensitivity_case_fail`. **One assertion was found not to discriminate and was rebuilt** — its first version patched a function the scan does not call — and the finding is recorded in the published analysis. |
>
> **Three measured ceilings are published with it**, rather than discovered later (the third
> — the numeric-key trap outside the non-string-probe class — added by the R1-10
> re-certification): a presence
> test over a FUNCTION PARAMETER is not detected (2 runs of the 76, both non-perfect, so the
> semantic class may be 42 rather than 40 — the analysis does not count them, because moving
> the boundary after seeing which side the runs fell on is the choice §5.2's admission test
> forbids); and the detector's alias map over-approximates scope, which costs nothing on this
> corpus and is measured rather than assumed.

## 4. Oracle, references, mutants, and the input domain

### 4.1 Ported by digest, no design change

Gold bytes and `check_gold.py`'s census (**117 rows**, sha256 `1ca1e5dd…`, both engines reproduce
every row, clean-room oracle 117/117 and 2,540/2,540); both reference packs and
`references-reproduce-gold` (117/117); the mutant corpora and `ADEQUACY.md`; the witness tables
and the pairing rule; the registered input domain with its symmetric per-arm case enumeration;
`leak_tokens.py`; the transcript gates other than gate 5; the identity control's
`referenceIdentity` relation; the off-gold equivalence certificate (**exactly 0 divergences over
236,196 cells**); X1's retirement and its permanent `retired-x1-regression` validation record; and
the `DEVIATIONS.md` machinery. **Pairing, re-derived from the two manifests by identical sorted
witness set and reproducing `RESULTS.json.pairing` exactly: 33 shared non-degenerate witness
classes, 69 paired adequate JPS, 62 paired adequate Rego.** The registered exclusion registry is
**empty**, and an unclassified divergence blocks the freeze rather than being filtered.

`GATE(pre-freeze)`: the registered clean-room build re-runs against the frozen prose; divergences
get written dispositions; unsettleable rows route to the ambiguity stratum mechanically.

### 4.2 The seven construct rows — kept in gold, split into two strata, outside every gate

**M-3 (revised), adopted.** The seven rows are two mechanically distinguishable classes, verified
against source:

- **S1 — five rows, derived-encoding cost.** `design/gold/check_gold.py::retired_x1` selects
  exactly `x1r-low-spend-unreadable-40`, `x1r-low-spend-unreadable-69`,
  `x1r-country-unreadable-100k`, `x1r-country-unreadable-40`, `x1r-country-unreadable-69` —
  committed, V7-certified, matching `verification/V7-COMPLETENESS.md` §3.4 assertion A6.
  Mechanism V8-09: expressing it costs a derived region lemma the prose never states; arms B/C
  need no such lemma. Signed `B/C-favorable`. **A cost row, not a fragment boundary.**
- **S2 — two rows, reason accumulation.** `p1-absent-escalation-region` and
  `p1-unreported-escalation-region` both return false under `retired_x1`, so they are outside S1's
  region and cannot require the region lemma. Their arm-A signature is exact and unanimous over
  019's 36 artifact-bearing runs: expected `unresolved:[missing-required-evidence]`, got
  `unresolved:[exception-escalation,missing-required-evidence]` on **35/35** failing runs; expected
  `unresolved:[unknown]`, got `unresolved:[exception-escalation,unknown]` on **35/35**. That is
  V8-10's inert O3 conjunct, whose guarding conjunct **is** stated in the prose.

Both strata are **scored and published per arm, outside every gate**. Nothing in the frozen
artifact chain moves. What narrows is the E1 *descriptive* support, to 110 rows, on grounds known
in advance to favour one arm's profile — so **both strata rates are published per arm with E1's
prominence**, and §11.7 says plainly that the support was chosen on a known arm asymmetry. It is
necessary, not sufficient: perfect-on-110 is **A 3/36, B 8/30, C 14/30**.

> **TODO(prereg) — S2's mechanical membership predicate.** S1's is committed and certified today.
> S2's is *the arm-A reference's answer depends on an exception conjunct entailed by another
> clause's guard*, which `design/mutants/ADEQUACY.md` already mechanizes on the **Rego** side as
> `entailed-guard`; the predicate must be **lifted to the JPS side and its extension published
> before the freeze**. **Registered sub-decision: if it cannot be lifted before the freeze, S2 is
> dropped and the two `p1-*` rows stay in the undifferentiated support.** A declared stratum must
> not be registered as a mechanical one.

### 4.3 What does not carry: the reviewer mutant set

019's reviewer mutant set is **spent** — `PINS.json`'s `reviewerMutantSet.note` records "first
executed at the primary attempt" and `RESULTS.json.reviewerSet.perArm` publishes the outcome per
run. **020 registers a fresh sealed reviewer set**: authored during review rounds, committed
verbatim, freeze-pinned by digest, validated without execution before the attempt, first executed
at the primary attempt under the mandatory `--include-reviewer-set`, executed exactly once, scored
"as authored", published in its own section, and reaching no member the decision reads. No
reviewer mutant is paired, enters a witness group, or moves any registered quantity. 019's set is
kept only as a published comparison.

## 4b. Threat model — which surface is gated, and which is recorded

**Registered here because 019's twelve review rounds proved it has to be** (ADR 0005, decision 3).

**(a) The REGISTERED surface — reviewed adversarially, freeze-gated.** This preregistration; the
frozen policy prose; the gold suite; both mutant corpora and their manifests; both reference
implementations; the off-gold equivalence certificate; the three arm prompts; the fresh sealed
reviewer mutant set; and the harness's scoring, driver, integrity, pins and manifest chain —
`harness/score.py` and `harness/e4lib/` (including the new `presence_idiom.py` and the family
scorer), `harness/batch.py`, `harness/transcript_check.py`, `harness/integrity.py`,
`harness/grid_gate.py`, `harness/PINS.json` and `harness/make_manifest.py`. A finding against any
of them is answered — with a mechanism and a test that fails when the mechanism is removed — or
the freeze does not happen. **No finding against this surface may be filed as an advisory.**

**(b) The REVIEW-SUPPORT APPARATUS — registered purpose: drift detection under an honest
operator.** The currency suite, `harness/render_round_status.py`, and the ceremony's procedural
documents exist to catch a document that has fallen out of step with the tree. That is a real and
repeatedly useful property. What it is **not**, and cannot be made into by hardening, is a root of
trust against a maintainer attacking their own record: integrity is **"a gate against drift, not a
root of trust"**, and every check in the review-support layer is weaker than that one — code the
maintainer runs, over documents the maintainer writes, checking properties the maintainer
registered, in a repository the maintainer controls.

**Consequence, registered.** A finding whose only reachable exploit requires the maintainer to edit
the record they are attesting is RECORDED as an open advisory in `harness/ADVISORIES.md` — with
its severity as the reviewer returned it, its file cites, and the reviewer's proposed fix,
unadopted and named as such — and is **not** a freeze gate. Recording is not dismissal: the
register is appendable, excluded from the exact-set manifest by named constant with an asserting
test (ADR 0004), and published with the study. No file that is covered leaves the covered set for
this: coverage answers "may these bytes move after the freeze" while this section answers "what
must a finding against them do".

## 5. Endpoints, the family, and the decision rule

### 5.1 The endpoint set

Scored surface: **kind + outcomeId + reasons (as sorted sets)** under the registered alignment map
(two axes: run-level admission; row-level
APPROVE/REVIEW/ENHANCED-REVIEW/REJECT/UNRESOLVED(reason-set)/ROW-ERROR(class)). `handoff` and
`trace[]` are outside every endpoint; `applicability` is forbidden by the appendix and asserted at
admission.

- **E4 (primary): witness-input coverage against the shared reference.** Per admitted run: the
  suite passes `referenceIdentity`; then the run's coverage set S over the 33 shared classes is
  computed, and each of §5.2's eighteen members is a weighted count over S. **No cut, no τ, no
  dichotomy.** **The scorer emits an explicit per-mutant survivor vector for every admitted run and
  must never encode "nothing evaluated" and "everything killed" with the same token** (§5.2's
  empty-survivor rule; registered as a day-one requirement, §7). Runs carrying authoring-outcome
  codes remain in the ITT members' denominators scoring 0; only apparatus codes leave. **Each
  member's per-arm denominator must be positive**; a contrast over an empty arm is not
  INDETERMINATE, it is not computed at all, and the outcome falls to the rows above.
- **E1 (reported, fully descriptive): per-run perfect gold agreement** on the policy artifact, ITT
  denominator, published on the 117-row support and on the 110-row support with S1 and S2 named
  (§4.2). **There is no E1 floor and no author-side control gate** (§5.7). 019's finding — *arm A
  never achieves perfect gold agreement, and the mechanism is a derived lemma the prose never
  states* — is a reported result here, not a study-killer. The exclusive disposition table 020
  reports per arm is 019's, re-derived and mutually exclusive:

  | Arm | ITT | no scorable artifact | collapsed ≥ 50 misses | intermediate 1–49 | perfect |
  |---|---|---|---|---|---|
  | A | 38 | 2 (`no-marker-block` 2) | 0 | 36 (2–15) | 0 |
  | B | 37 | 7 (`opa-check-failed` 4 + `unparseable-artifact` 3) | 20 (86–104) | 2 (2–13) | 8 |
  | C | 39 | 9 (`opa-check-failed` 9) | 13 (86–104) | 3 (2–13) | 14 |

  *Descriptive; published as an interpretation quantity that no decision reads.* "Collapsed" is a
  cohort label, not a registered category; arms B and C are **strongly bimodal, with 2 and 3
  intermediate runs** — not "perfect or 86–104".
- **E2: authoring-validity profile** — §1a's ordered code table with apparatus codes separated,
  same denominator, headline not footnote. **The table carries `presence-idiom-unsound` (§3.2)**,
  with its per-arm count published whether or not it ever fires.
- **E3: row-level failure taxonomy** on E1 failures and identity failures, with `u1-*` and the two
  `p1-*` region rows as named categories; arm-structural categories within-arm-only, enforced in
  the scorer.
- **E5: interpretive-spread census** — per-arm distinct structural encodings and pairwise-
  disagreement profiles over the frozen gold-row input set, the count freeze-pinned in `PINS.json`.
- **E6 (new, reported): `ownPolicyIdentity`** — the per-run score of the authored suite against the
  run's own authored policy (§1.2, M-13; exposure as measured there, R1-14). **Published per run
  and per arm; gates nothing; conditions R1's construct statement.** The conjunction
  `referenceIdentity ∧ ownPolicyIdentity` is published as a Tier D population disposition, so the
  population 020 did **not** register is visible beside the one it did.
- Latency and artifact-size distributions per arm: descriptive, published.

### 5.2 The registered sensitivity family — eighteen members

#### The admission test (arm-blind by construction)

An analytic choice is a **family axis** iff:

| | Criterion |
|---|---|
| **(i)** | **Openness.** The choice was still open at the moment 019's arm-labelled quantities entered the design record. |
| **(ii)** | **Both poles defensible.** Each pole is a defensible answer to §1.1's question. An axis with one indefensible pole is a correctness question, not a robustness question. |
| **(iii)** | **No known structural bias.** Neither pole is provably biased under a true null by a quantity computable from the frozen corpus alone. Where one is, it enters **in its de-biased form**, and the raw form is published in Tier D. |

All three read the design record's chronology, §1.1's wording, and the frozen manifests. **None
reads an arm-labelled outcome.** A fourth criterion the design drafts carried — *"the axis is
outcome-determinative on 019's batch"* — is **withdrawn and is not registered**: it selected
membership from the leaked direction, and under the intersection–union logic of §5.4 *removing*
members is the anti-conservative direction.

#### Two structural facts, both derived from the manifests

**Fact 1** is stated with the construct in §1.2, with its identity-pass condition and its 88-run
denominator.

> **The empty-survivor trap, registered as a day-one scorer requirement.** Two arm-A runs of 019
> (`run-025`, `run-046`, both identity-failing) carry `survivorsPaired: []` **with
> `killedPaired: 0`**. Read naively — "no survivors ⇒ everything killed" — they score a perfect
> 33/33 when they killed nothing. On 019 this single schema trap moves the group-level ITT A−C
> contrast from **+0.19112 (naive) to +0.13849 (corrected)** — magnitude **0.0526**, a 38 % shift,
> and note the direction: correcting the trap **lowers** A−C. **020's scorer emits an explicit
> per-mutant survivor vector for every admitted run and never encodes "nothing evaluated" and
> "everything killed" with the same token.** Every figure in this document uses the corrected
> reading.

**Fact 2 — the native mutant-level estimand is structurally biased between languages.** Of the 33
shared classes, **20 have unequal member counts across languages** (13 JPS-heavier, 7 Rego-heavier;
extremes `d7-39-100k` 6 JPS vs 3 Rego, and the four-input `d1-match|…` class 1 JPS vs 4 Rego).
Under a true null — both arms drawing coverage sets from the same distribution — the expected A−C
contrast of a level with weights w^A, w^C is `offset = Σ_g π_g · (w^A_g − w^C_g)`, π_g the pooled
coverage marginal of class g:

| level | weights w^A_g / w^C_g | offset at 019's pooled coverage profile | worst case |
|---|---|---|---|
| **L2 — native mutant** (019's registered quantity) | \|J_g\|/69 vs \|R_g\|/62 | **−0.0496** (per-protocol) / −0.0485 (ITT) | 0.5400 |
| **L2, engine-excluded** | \|J^ex_g\|/57 vs \|R_g\|/55 | −0.0492 / −0.0481 | 0.5046 |
| **L2, engine-excluded — REGISTERED weights, AMENDED round 2 (R2-2)** | \|J^ex_g\|/57 vs \|R_g\|/62 (native: an exclusion that removes no Rego mutant leaves Rego's own denominator unmoved) | **−0.00567** (per-protocol) / **−0.00554** (ITT) | — |
| **L1 — group**, weight 1/33 each | 1/33 vs 1/33 | **0 by construction** | 0 |
| **L3 — symmetrised mutant**, w_g = (\|J_g\|+\|R_g\|)/131 | identical in both arms | **0 by construction** | 0 |

−0.0496 is larger than any representation effect this study plausibly seeks, so L2 fails criterion
(iii) in its raw form — and by criterion (iii) it enters **de-biased, not removed**:

> **L2c, registered definition.** Per-run outcome = the native-denominator paired kill fraction;
> then **off̂ is subtracted from every arm-A run's outcome that carries a kill record**, where
> off̂ = Σ_g π̂_g(w^A_g − w^C_g) and π̂ is the pooled, **arm-label-free** coverage marginal over the
> kill-record-carrying runs of that member's own analysis population. Runs with no kill record
> score 0 in both arms and take no offset. On 019: off̂ = −0.04956 (per-protocol,
> engine-included), −0.04846 (ITT), −0.04922 / −0.04813 excluded-column.
>
> **AMENDED (round 2, R2-2; the F-1 re-ruling below).** The weights w^A_g, w^C_g in off̂ are the
> SAME native denominators the outcome uses — one universe. On 019 that leaves the
> engine-included figures exactly as printed (all 33 included classes are shared, so the native
> and shared denominators coincide there) and moves the excluded column to **−0.00567**
> (per-protocol) / **−0.00554** (ITT); the −0.04922 / −0.04813 above are the shared-denominator
> reading, published beside the registered one as Tier D by `family_report()`'s offsets block.
>
> **PREDICATE CORRECTION — of Study 019, marked, 2026-08-24 (round-1 finding R1-3; no verdict
> and no α = 0.05 decision moves).** This definition's first printing said "scoreable" and
> "unscoreable", one word carrying two facts. Study 019's scorer gated mutant execution on the
> identity control, so its two identity-failing admitted runs (`A/run-025`, `A/run-046`)
> EVALUATED NO MUTANT — yet their frozen records carry a kill block, and 019's published ITT
> offsets are obtainable ONLY with those two runs inside the marginal (measured:
> −0.04846 = −0.04956 × 88/90 to every digit). The registered reading above — the marginal and
> the subtraction select on CARRYING A KILL RECORD — is therefore 019's own, reproduces every
> §5.5 reprint, and stands. The evaluation-corrected reading (marginal over the 88 runs that
> actually evaluated a mutant) is published beside it by `family_report()`
> (`included/ITT −0.04956`, `excluded/ITT −0.04922`; both per-protocol marginals are the same
> set under either predicate), and under it exactly four member figures of 019's Reprint 1
> move, none across a decision boundary:
>
> | member | as published (kill-record) | evaluation-corrected |
> |---|---|---|
> | M13, A−C | +0.1463 (p 0.0210) | +0.1448 (p 0.0240) |
> | M16, A−C | +0.2323 (p 0.0008) | +0.2308 (p 0.0010) |
> | M13, A−B | +0.1416 | +0.1401 |
> | M16, A−B | +0.2276 | +0.2261 |
>
> **RECOMPUTED (round 2; the R2-2 re-ruling, and a repair).** The table above was TRANSCRIBED:
> `member_outcomes()` hard-coded the subtraction set to the kill-record predicate while only the
> marginal took the argument, so the evaluation-corrected column could not be produced by the
> registered scorer. The predicate is threaded through both now (`e4lib/family.py`,
> `test_family.py::test_the_predicate_threads_through_the_subtraction_set_too`), and the table
> under the REGISTERED estimand, computed rather than asserted, is:
>
> | member | registered (kill-record) | evaluation-corrected |
> |---|---|---|
> | M13, A−C | +0.1463 (p 0.0210) | +0.1448 (p 0.0239) |
> | M16, A−C | +0.1920 (p 0.0044) | +0.1918 (p 0.0044) |
> | M13, A−B | +0.1416 (p 0.0296) | +0.1401 (p 0.0331) |
> | M16, A−B | +0.1873 (p 0.0060) | +0.1871 (p 0.0060) |
>
> M13 is unchanged from the first printing because the included column is one universe already;
> M16's two readings now differ by 0.0002 rather than 0.0015 because the native excluded-column
> marginal is an order of magnitude smaller than the shared one. Neither reading crosses a
> decision boundary. The M13 A−C evaluation-corrected p prints 0.0239 here and 0.0240 above:
> the same stream, the first printing rounded from a transcription.
>
> `e4lib/family.py`'s `Unit` now carries the two predicates separately (`carries_kill_record`,
> `evaluated`), `offset()` takes the predicate as an argument, and the fixture adapter builds
> the two runs as carrying-but-not-evaluated instead of synthesizing an all-survivor vector
> that asserted an evaluation which never happened. This is a correction OF Study 019's
> vocabulary published by 020's reprint discipline, not a failure of the reprint: the
> registered default reproduces 019 exactly, and the corrected reading is a second computation
> beside it.

**M-16(d), ruled: the three L2c ceilings are accepted as registered ceilings, in the brief's own
words** — π̂ on the per-protocol population is estimated on a post-treatment-selected cohort
(arm-label-free, but not treatment-free); off̂'s estimation variance is not propagated into the
member's test; and for the adjusted members the offset is subtracted from unit outcomes *before*
the ANCOVA, so the adjusted contrast inherits it linearly. **L3's presence beside L2c is the
mitigation**: L3 needs no estimated offset and is unbiased for *any* π (§11.9).

> **F-1, RULED 2026-08-24 (round-1 finding R1-4; the maintainer decision `harness/e4lib/family.py`'s
> finding F-1 demanded, now on the record).** The registered estimand is the HYBRID the L2c
> definition above already describes, ruled explicitly rather than left implied: each member's
> OUTCOME is the language-native paired kill fraction (native denominators — Rego `/62` in the
> excluded column, because an exclusion that removes no Rego mutant leaves Rego's own denominator
> unmoved), and L2c's OFFSET weights are the SHARED-class denominators (`57/55`), because the
> offset is a shared-support de-biasing term and computing it over support one arm cannot reach
> would import exactly the vacuity it exists to remove. Two facts carried the ruling: this is the
> only reading under which every §5.5 reprint figure reproduces (the registered Tier D anchors),
> and the offset's role is structural correction, not outcome measurement, so the two sides of
> the hybrid answer different questions and may lawfully use different weights. The two
> single-universe alternatives are PUBLISHED beside it rather than erased — shared-for-both, and
> native-for-both in both sub-readings (−0.00567 / −0.00554 pooled-vacuous — the ITT cell as
> measured under R1-3's honest units; +0.03795 / +0.03711
> marginal-over-29) — by `family_report()`'s offsets block, so a reader can see what the ruling
> chose against. `harness/e4lib/family.py`'s F-1 note records the ruling at the code; round 2
> verifies it.

> **F-1, RE-RULED (round-2 finding R2-2, REFUSING the round-1 ruling; maintainer decision
> 2026-08-26: NATIVE-FOR-BOTH).** Round 2 verified the hybrid and refused it: de-biasing a
> native-weighted outcome with a shared-weighted offset leaves a residual that is computable
> from the frozen corpus alone under a true null — **+0.043552 (per-protocol) / +0.042584
> (ITT) per subtracted unit in the excluded column, 7.7× the raw native bias of −0.00567** —
> which is precisely what criterion (iii) forbids a member to carry. The registered estimand is
> therefore ONE universe: each L2c member's outcome and its offset are both weighted by the
> language-native denominators (Rego `/62` in the excluded column, JPS `/57`), and the reading is
> registered in `harness/PINS.json` (`family.outcomeWeighting` / `family.offsetWeighting`, both
> `native`), read from there by `harness/score.py` and `harness/counterfactual_shift.py`, and
> enforced at the member seat: `e4lib/family.py` refuses a seat whose two weightings differ
> (`MixedUniverseRefused`, beside the ITT × ANCOVA refusal). What moves on 019, all excluded
> column, none across a decision boundary: **M16 +0.2323 → +0.1920 (p 0.0008 → 0.0044),
> M17 +0.1275 → +0.0839 (p < 0.0001 → 0.0018), M18 +0.0911 → +0.0476 (p 0.0002 → 0.0125)**;
> A−B M16 +0.2276 → +0.1873 (p 0.0014 → 0.0060), M17 +0.1065 → +0.0629 (p < 0.0001 → 0.0102),
> M18 +0.1105 → +0.0669 (p 0.0002 → 0.0005). The included column is unchanged (all 33 of its
> classes are shared, so its native and shared denominators coincide and M13–M15 reproduce to
> the digit). **The verdict does not move: A−C 16 positive / 2 negative, 10 of 18 reject —
> INDETERMINATE-BY-DISAGREEMENT; A−B 18 positive, 8 of 18 reject; Reprint 2's nine rows are
> identical.** M16's dispersion tightens (σ 0.29826 → 0.29649; MDE at 019's n 0.1905 → 0.1893);
> the per-protocol members' σ is offset-invariant. The two readings the ruling chose against are
> PUBLISHED, complete — every row, the verdict, the drop-a-pole table — as Tier D by
> `family_report()`'s `alternatives` block: the hybrid (native outcome / shared offset, 019's
> reading, **SUPERSEDED**; it remains the reading under which every §5.5 reprint reproduces, and
> is retained for exactly that reason) and shared-for-both (**ALTERNATIVE**; 8 of 18 reject on
> A−C, 6 on A−B). Round 1's ruling above is retained as written and superseded by this block.

#### The eighteen members

The family is the crossing **{L1, L3, L2c} × {engine-included, engine-excluded} ×
{ITT-unadjusted, PP-unadjusted, PP-adjusted}**, with **both poles of every axis retained**.

- **Level axis, three poles.** L1 group (a class is one unit); L3 symmetrised mutant; L2c de-biased
  native mutant (019's registered quantity, made unbiased). All three are defensible answers to
  §1.1 and they are genuinely different estimands.
- **Engine-supplied-kill axis, two poles.** Excluding engine-supplied kills drops **12 of 69 paired
  JPS mutants and 0 of 62 paired Rego**, taking the shared class set from **33 to 29** and the
  JPS/Rego paired totals to 57/55. The exclusion is entirely one-sided, which is an **arm-blind**
  reason it could matter. Both columns are members.
- **Population × adjustment, three cells.** ITT = every §1a admitted run, a run with no scorable
  suite scoring 0. Per-protocol = `referenceIdentity`-passing runs. Adjustment = ANCOVA on
  `caseCount`, pinned below.

**The two cells registered *out* of the family, argued rather than dropped.**

1. **ITT × ANCOVA.** `caseCount` is undefined for a run with no parseable suite. Imputing 0 makes
   the covariate a near-deterministic function of the ITT-vs-per-protocol distinction itself, so
   adjusting for it partially undoes the very zero-filling the ITT pole exists to impose — a covert
   change of population, not an adjustment. On 019, with `caseCount = 0` imputed, the ITT
   group-level A−C moves from **+0.1385 to −0.0201** and pooled within-arm SD collapses from
   **0.25427 to 0.09652**. The six quantities are published in Tier D with this sentence attached.
   *A naive implementation instead silently drops the covariate-less runs and reproduces the
   artifact-bearing complete-case cell exactly — a hidden collapse of the family. **The scorer must
   refuse rather than fall back**, and a harness test drives that refusal.*
2. **Artifact-bearing complete-case as a third population pole.** A population defined by "carries
   a survivor vector" admits runs that *failed* the identity control — which the per-protocol pole
   exists to exclude and the ITT pole includes wholesale. It is neither, and it is registered out on
   criterion (ii). Its composition on 019 is disclosed in Tier D: the per-protocol set plus exactly
   the two empty-survivor runs.

#### Definitions pinned before the freeze

1. **Coverage rule.** A run covers class g iff its suite kills **all** of g's members in the run's
   own language. The any/all question is **not a live choice**: `gall == gany` in **88 of 88**
   checkable runs, and Fact 1 shows this is structural for `referenceIdentity`-passing runs. The
   equivalence **and its condition** are registered as a stated fact, not as a sub-decision.
2. **ANCOVA pinned to the byte.** Pooled *within-arm* slope estimated over **all three arms**
   jointly; adjusted difference evaluated at the grand covariate mean. On 019 at L1/per-protocol:
   slope **b = +0.02332**, arm covariate means A 20.882 / B 21.000 / C 19.821, adjusted means
   A 0.6106 / B 0.5893 / C 0.5945. The two-arm-only slope variant gives A−C = +0.0185 against the
   three-arm +0.0161 — immaterial there, decisive as a registration matter. **Pin the three-arm
   form; publish the pairwise variant in Tier D.**
3. **Balance registered on means with a test**, with a stated threshold and a registered non-claim
   if it fails. A median-based balance claim is **not** registered.
4. **`caseCount` = 0** for a suite that parses to no cases, with the per-arm count of such runs
   published before the freeze and the complete-case variant published beside it. 020's scorer
   emits `caseCount` for every admitted run with a suite; 019's six runs that carried a `kill` block
   with neither `survivorsPaired` nor `caseCount` (B `run-026/027/032/036`, C `run-035/050`; arm A
   zero — **exactly the same six runs under both defects**) cannot recur.
5. **Analysis-set arithmetic registered per member** before the freeze; each member's per-arm n is
   published whether or not R1 fires.

   > **TODO(prereg) — each member's registered per-arm n.** A function of N (§2.1) and of the
   > realised-n arithmetic below. **N resolved 2026-08-24 (§2.1's fill: 50/arm), so this TODO is
   > UNBLOCKED**; the arithmetic is applied at the registered N = 60 in the §5 analysis-set pass and this entry
   > fills before the freeze — deliberately not in the same edit as the condition, so the §5
   > numbers land in one reviewed pass rather than scattered.

**Realised-n arithmetic, shown rather than asserted, at the illustrative N = 60 branch.** Derived
from 019's `population.*.apparatusCodes` (A: `registry-mismatch` 9, `slot-shape` 2,
`transcript-refused` 1; B: `slot-shape` 11, `post-call-failure` 1, `transcript-refused` 1; C:
`slot-shape` 11) and the conditional artifact-plus-identity rates A 34/38 = 0.895, B 26/37 = 0.703,
C 28/39 = 0.718: with `slot-shape` pre-paid, arm A is 1 − 10/50 = 0.80 → 48 admitted → ≈ **43**
scoreable; arm B 0.96 → 57.6 → ≈ **40**; arm C 1.00 → 60 → ≈ **43**. With `registry-mismatch` also
repaired, arm A is 0.98 → 58.8 → ≈ **53**. **Without that repair arm A projects to ~43, not 50.**

#### Membership is append-only after registration

After the freeze a maintainer may **add** a member — monotone toward INDETERMINATE under §5.4's
intersection–union logic — and may **never remove one**. An addition requires a `DEVIATIONS.md`
entry and the **pre-addition verdict is published beside the post-addition one**. Every member is
published whatever the verdict.

### 5.3 The per-member test — one scheme, stated precisely

- **Unadjusted members.** Exact two-sided permutation test on the difference in means, permuting
  arm labels within the two-arm subset. Exact under the sharp null of no unit-level effect.
  **20,000 permutations**, seed pinned in `PINS.json`, Monte-Carlo p in the (count+1)/(B+1) form.
- **Adjusted members.** The unit's **whole record** (outcome and `caseCount`) travels with the
  permuted label; **4,000 permutations**, same seed rule. This is exact under the **strong** sharp
  null — the arm changes neither the suite's coverage nor its size — and it is *not* an exact test
  of "no effect on Y given `caseCount`". **Freedman–Lane residual permutation is not registered and
  is not a cure**: no covariate-adjusted permutation scheme achieves exactness for that null with a
  treatment-affected covariate, and registering two schemes in one document was itself a defect. The
  family contains the unadjusted members precisely so that the weaker guarantee is never
  load-bearing alone.
- **Every table names its method and its B.** Where a normal-theory surrogate is used (only in
  §5.6's simulation) it is labelled as such.
- **The word "exact" is used only of a permutation null distribution, never of an interval.**
  Inverting to an interval needs a location-shift model, and the outcome is bounded, lattice-valued
  (1/33 = 0.0303), with per-arm SDs differing by 24 % on 019. **Intervals are Tier D**: BCa
  bootstrap, per member, coverage stated as approximate, **no decision reads them**.

### 5.4 α handling — intersection–union

1. **No multiplicity correction is applied, and none is needed.** The claim's alternative is
   H₁⁺ = {every member's difference > 0} (symmetrically H₁⁻); its null is a **union**. An IU test
   requiring every member to reject at level α has size **≤ α**, attained only in the
   least-favourable configuration where one member sits exactly at zero. For a *directional* claim,
   two-sided p < 0.05 plus a sign is a one-sided level-0.025 test, so the family-wise type-I rate
   for a signed R1 is **≤ 0.025**. Bonferroni would be not merely unnecessary but wrong.
2. **Realised size is far below the bound** — §5.6 puts it at **0.002** at N = 60/arm under a global
   null.
3. **The price is paid entirely in power**: power ≤ min over members.
4. **α = 0.05 per member, two-sided, no correction** (M-19). Lowering α costs power multiplicatively
   across eighteen members and buys nothing the IU bound does not already give.
5. **The fixed sequence A−C → A−B spends no α.**

### 5.5 The mandatory reprints (M-21)

**Ruled 2026-08-23: the honesty table is a mandatory reprint in the preregistration.** It is
reprinted here in full, in the body and not an appendix, together with the two tables that make it
readable. All three are **arm-labelled by design, under Tier D** — *descriptive; published as an
interpretation quantity that no decision reads.* Unadjusted members: label permutation, B = 20,000,
seed 11. Adjusted members: whole-record permutation, B = 4,000, seed 11. Corrected scorer
throughout.

**Reprint 1 — the eighteen members on 019's batch.**

| id | level | engine | population | adj | n (A/B/C) | **A−C** | p | **A−B** | p |
|---|---|---|---|---|---|---|---|---|---|
| M1 | L1 | incl | ITT | — | 38/37/39 | **+0.1385** | **0.0137** | +0.1317 | **0.0229** |
| M2 | L1 | incl | PP | — | 34/26/28 | **+0.0408** | **0.0213** | +0.0186 | 0.2957 |
| M3 | L1 | incl | PP | ANCOVA | 34/26/28 | +0.0161 | 0.2309 | +0.0213 | 0.1110 |
| M4 | L1 | excl | ITT | — | 38/37/39 | **+0.1576** | **0.0137** | +0.1498 | **0.0229** |
| M5 | L1 | excl | PP | — | 34/26/28 | **+0.0464** | **0.0213** | +0.0211 | 0.2957 |
| M6 | L1 | excl | PP | ANCOVA | 34/26/28 | +0.0183 | 0.2309 | +0.0243 | 0.1110 |
| M7 | L3 | incl | ITT | — | 38/37/39 | **+0.1438** | **0.0210** | +0.1376 | **0.0319** |
| M8 | L3 | incl | PP | — | 34/26/28 | +0.0346 | 0.1569 | +0.0118 | 0.6133 |
| M9 | L3 | incl | PP | ANCOVA | 34/26/28 | **−0.0026** | 0.8823 | +0.0160 | 0.3077 |
| M10 | L3 | excl | ITT | — | 38/37/39 | **+0.1694** | **0.0165** | +0.1615 | **0.0259** |
| M11 | L3 | excl | PP | — | 34/26/28 | +0.0469 | 0.0871 | +0.0199 | 0.4434 |
| M12 | L3 | excl | PP | ANCOVA | 34/26/28 | +0.0053 | 0.7881 | +0.0245 | 0.1577 |
| M13 | L2c | incl | ITT | — | 38/37/39 | **+0.1463** | **0.0210** | +0.1416 | **0.0296** |
| M14 | L2c | incl | PP | — | 34/26/28 | +0.0314 | 0.1991 | +0.0104 | 0.6570 |
| M15 | L2c | incl | PP | ANCOVA | 34/26/28 | **−0.0036** | 0.8263 | +0.0142 | 0.3779 |
| M16 | L2c | excl | ITT | — | 38/37/39 | **+0.2323** | **0.0008** | +0.2276 | **0.0014** |
| M17 | L2c | excl | PP | — | 34/26/28 | **+0.1275** | **< 0.0001** | +0.1065 | **< 0.0001** |
| M18 | L2c | excl | PP | ANCOVA | 34/26/28 | **+0.0911** | **0.0002** | +0.1105 | **0.0002** |

> **A−C: direction unanimity FAILS (16 positive, 2 negative). Test unanimity FAILS (10 of 18
> reject).**
> **Tier C's verdict on 019's batch: INDETERMINATE-BY-DISAGREEMENT.**
> A−B is unanimous in direction (18 positive) but only 8 of 18 reject — and it is unreachable
> anyway, gated behind A−C.

> **REPRODUCTION SCOPE, marked 2026-08-24 (round-1 finding R1-6; `e4lib/family.py` finding
> F-2 is the measurement).** The registered scorer reproduces this table's every point
> estimate, every n, the twelve unadjusted p-values to the printed digit, every reject /
> not-reject decision at α = 0.05, the 16/2 sign split and all of Reprint 2 — and does NOT
> reproduce the six ANCOVA p-values to the digit, because 019's generating script is not in
> its tree and the residual is a different Monte-Carlo stream under the same scheme. Both
> value sets, at the registered B = 4,000: M3/M6 print 0.2309 above and the scorer computes
> **0.2462**; M9 0.8823 / **0.8883**; M12 0.7881 / **0.7891**; M15 0.8263 / **0.8395**; the
> A−B column's M3/M6 0.1110 / **0.1107**, M9 0.3077 / **0.3062**, M12 0.1577 / **0.1647**,
> M15 0.3779 / **0.3809**; M18 is exact in both contrasts. Every claim in this study that a
> figure "reproduces to the printed digit" is scoped by this note: it holds for the point
> estimates and the unadjusted scheme, and for the six ANCOVA p-values it means
> decision-boundary agreement with the scorer's own stream printed beside 019's.
>
> **SCOPE EXTENDED (round 2, R2-2).** Reprint 1 is 019's reading — the hybrid estimand of
> round 1's F-1 ruling — and since the re-ruling the registered scorer reproduces it through
> the SUPERSEDED Tier D `alternatives` block of `family_report()`, not through the member rows.
> The member rows under the registered estimand reproduce fifteen of the eighteen to the digit
> and move the three excluded-column L2c members to the figures below.

**Reprint 1b — the three rows that move under the registered estimand (round 2, R2-2;
native-for-both). Reprint 1 above is retained as 019's own reading, SUPERSEDED as estimand.**

| id | level | engine | population | adj | n (A/B/C) | **A−C** | p | **A−B** | p |
|---|---|---|---|---|---|---|---|---|---|
| M16 | L2c | excl | ITT | — | 38/37/39 | **+0.1920** | **0.0044** | +0.1873 | **0.0060** |
| M17 | L2c | excl | PP | — | 34/26/28 | **+0.0839** | **0.0018** | +0.0629 | **0.0102** |
| M18 | L2c | excl | PP | ANCOVA | 34/26/28 | **+0.0476** | **0.0125** | +0.0669 | **0.0005** |

> **The verdict line is unchanged**: A−C 16 positive / 2 negative, 10 of 18 reject —
> INDETERMINATE-BY-DISAGREEMENT; A−B 18 positive, 8 of 18 reject, unreachable behind A−C.
> Reprint 2 below is identical row for row under either reading. The three rows here and the
> fifteen above are what `harness/COUNTERFACTUAL-SHIFT.json`'s unflagged column reproduces.

**Reprint 2 — the drop-a-pole table, and the one exception.** Dropping every member carrying a
given pole and re-evaluating:

| pole dropped | members left | positive | reject | verdict |
|---|---|---|---|---|
| L1 | 12 | 10 | 6 | INDETERMINATE |
| L3 | 12 | 11 | 8 | INDETERMINATE |
| L2c | 12 | 11 | 6 | INDETERMINATE |
| engine-included | 9 | 9 | 6 | INDETERMINATE |
| engine-excluded | 9 | 7 | 4 | INDETERMINATE |
| ITT | 12 | 10 | 4 | INDETERMINATE |
| **per-protocol** | **6** | **6** | **6** | **CLAIM** |
| adjusted | 12 | 12 | 9 | INDETERMINATE |
| unadjusted | 6 | 4 | 1 | INDETERMINATE |

**Read the one exception.** An ITT-only family would have claimed on 019 — and §5.6 shows that ITT
members reject **66–68 % of the time under a null in which coverage is identical and only authoring
validity differs**. The per-protocol pole is not decoration; it is the guard that keeps an
OPA-toolchain failure rate from being reported as a representation effect. **This is why the family
is registered before the batch and is append-only afterwards.**

**Reprint 3 — the single-choice ledger: what a one-member registration could have licensed.** Tier D
continuity rows on 019's *own registered* quantity (raw L2, no offset correction), same methods:

| population | engine | adjustment | A−C | p |
|---|---|---|---|---|
| ITT §1a | incl | — | +0.1004 | 0.1068 |
| ITT §1a (`caseCount` = 0 imputed) | incl | ANCOVA | **−0.0805** | **0.0007** |
| ITT §1a | excl | — | **+0.1867** | **0.0050** |
| ITT §1a (`caseCount` = 0 imputed) | excl | ANCOVA | +0.0030 | 0.9205 |
| per-protocol | incl | — | −0.0182 | 0.4578 |
| per-protocol | incl | ANCOVA | **−0.0532** | **0.0012** |
| per-protocol | excl | — | **+0.0783** | **0.0031** |
| per-protocol | excl | ANCOVA | **+0.0419** | **0.0227** |

**Two of these reject at α = 0.05 in opposite directions, one at p = 0.0007.** Any single-member
registration drawn from this set is a coin whose face the design phase had already seen. **019's
registered quantity is published here with its structural offset (−0.0496) attached, never
without it.**

### 5.6 Operating characteristics — size and power, supplied rather than asserted

Script `oc18.py`, seed **20200822**, registered specification: pool = the 88 identity-passing 019
runs with arm labels destroyed, each contributing (coverage set over the 33 shared classes,
`caseCount`); a replicate draws N runs iid with replacement per arm; each drawn run is scoreable
with probability p_arm, otherwise it scores 0 on the ITT members and is dropped from the
per-protocol members; an effect is imposed as **θ additional covered classes** for arm A's
scoreable runs, drawn without replacement from that run's uncovered classes with probability
proportional to the pooled coverage marginal π, so the five never-covered classes are unreachable
and the attainable ceiling stays 28/33; the suite-size-only alternative instead tilts arm A's draws
toward larger `caseCount` (weights ∝ exp(0.8·(c − c̄))) with θ = 0; tests are normal-theory
surrogates for the registered permutation tests; L2c's offset is recomputed from each replicate's
own pooled marginal. Tier C fires iff all eighteen agree in sign and all eighteen have p < 0.05.

**Size, N = 60/arm, 2,000 replicates:**

| scenario | per-member rejection | **Tier C** |
|---|---|---|
| **Global null** — equal validity 0.80, θ = 0 | all eighteen 0.036–0.052 | **0.002** |
| **Authoring-validity-only null** — A 0.895 vs C 0.718, coverage identical, θ = 0 | **ITT members 0.660–0.678**; per-protocol 0.036–0.051 | **0.001** |
| **Suite-size-only alternative** — equal validity, size tilt, θ = 0 | **PP-unadjusted 0.986–0.998**; PP-adjusted 0.019–0.067; ITT 0.138–0.165 | **0.000** |
| **True coverage effect** θ = 3, equal validity | PP members 0.999–1.000; ITT 0.251–0.351 | 0.248 |

The authoring-validity channel alone **cannot** produce a Tier C claim (0.001), and neither can the
suite-size channel (0.000) — and each of those channels alone *would* have produced a claim under a
one-member registration drawn from the ledger above.

**Power, 1,000 replicates per cell, IU rejection rate.** Under equal authoring validity (0.80 both
arms): θ = 2 → 0.129 (N=60) / 0.236 (120) / 0.315 (200); θ = 4 → 0.368 / 0.610 / 0.836; θ = 6 →
0.578 / 0.860 / 0.976; θ = 8 → 0.720 / 0.956 / 0.996. Under 019's observed validity gap (A 0.895 /
C 0.718): θ = 1 → 0.127 (N=40) / 0.246 (60) / 0.356 (80); θ = 2 → 0.581 / **0.797** / 0.918; θ = 3 →
0.821 / **0.955** / 0.985; θ = 4 → 0.908 / 0.987 / 1.000.

**Four consequences, stated here rather than discovered:**

1. **Which member binds depends on the regime.** Under equal validity the ITT members bind; under
   019's gap the ITT members become the *easiest* — they reject two-thirds of the time under a null
   — and the per-protocol members bind.
2. **Power under the gap is partly spurious and is labelled so.** Tier C's 0.797 at θ = 2, N = 60 is
   a conjunction in which six of eighteen members are near-automatically satisfied by a channel that
   is **not** the construct; the honest reading is that in that regime Tier C is effectively a
   twelve-member test on the per-protocol members — and size under the same gap is still 0.001,
   because those twelve hold it.
3. **The honest headline for N.** At N = 60/arm with all apparatus repairs, Tier C is 80 %-powered
   against a coverage effect of roughly **2 classes if 019's validity gap persists** and roughly
   **9 classes (θ ≈ 0.27 in group-fraction units) if it does not. 020 cannot know in advance which
   regime it is in.**
4. **Against 019's own observed configuration, Tier C is unpowered at every N.** M9 and M15 are
   negative point estimates with the family's other sixteen positive; if that configuration is the
   truth, P(all eighteen agree in sign) → 0 as N grows. **The registered planning statement is: *if
   the truth resembles 019, Tier C returns INDETERMINATE with probability → 1*, and 020 commits to
   publishing exactly that.**

**Dispersion and minimum detectable effect, per member** — pooled within-arm SD, unbiased (N − k;
residual N − 4 for the adjusted members), all arm-blind; MDE = 2.8016 · σ · √(1/n_A + 1/n_C) at
two-sided α = 0.05, 80 % power. **These are 019 figures and are a labelled fallback prior until the
pilot re-derives them at the pinned effort (§2a.6).** **AMENDED (round 2, R2-13):** the
re-derivation is `harness/pilot_analysis.py`'s `PILOT-DISPERSION.json`, and its eighteen rows —
σ, df, the exact χ² 95 % interval, MDE at the pilot's n and at the registered N — are APPENDED
below this table by the ceremony once the pilot has run, and stand beside it. This table is
retained as published; no figure in it moves.

| id | σ | MDE @ 019 n | MDE @ N=60, slot-shape cured | MDE @ N=60, + registry cure | MDE @ N=100 |
|---|---|---|---|---|---|
| M1 L1/incl/ITT | 0.25427 | 0.1624 | 0.1379 | 0.1306 | 0.1013 |
| M4 L1/excl/ITT | 0.28934 | 0.1848 | 0.1570 | 0.1486 | 0.1152 |
| M7 L3/incl/ITT | 0.28439 | 0.1816 | 0.1543 | 0.1461 | 0.1133 |
| M10 L3/excl/ITT | **0.32159** | **0.2054** | **0.1745** | **0.1652** | **0.1281** |
| M13 L2c/incl/ITT | 0.28966 | 0.1850 | 0.1571 | 0.1488 | 0.1153 |
| M16 L2c/excl/ITT | 0.29826 | 0.1905 | 0.1618 | 0.1532 | 0.1188 |
| M2 L1/incl/PP | 0.06938 | 0.0496 | 0.0419 | 0.0399 | 0.0309 |
| M5 L1/excl/PP | 0.07895 | 0.0564 | 0.0477 | 0.0454 | 0.0352 |
| M8 L3/incl/PP | 0.09397 | 0.0672 | 0.0568 | 0.0540 | 0.0418 |
| M11 L3/excl/PP | 0.10516 | 0.0752 | 0.0635 | 0.0605 | 0.0468 |
| M14 L2c/incl/PP | 0.09040 | 0.0646 | 0.0546 | 0.0520 | 0.0402 |
| M17 L2c/excl/PP | 0.09479 | 0.0678 | 0.0573 | 0.0545 | 0.0422 |
| M3 L1/incl/PP/anc | **0.05068** | 0.0362 | 0.0306 | 0.0291 | 0.0226 |
| M6 L1/excl/PP/anc | 0.05767 | 0.0412 | 0.0348 | 0.0332 | 0.0257 |
| M9 L3/incl/PP/anc | 0.06114 | 0.0437 | 0.0369 | 0.0352 | 0.0272 |
| M12 L3/excl/PP/anc | 0.06849 | 0.0490 | 0.0414 | 0.0394 | 0.0305 |
| M15 L2c/incl/PP/anc | 0.06049 | 0.0432 | 0.0365 | 0.0348 | 0.0269 |
| M18 L2c/excl/PP/anc | 0.06420 | 0.0459 | 0.0388 | 0.0369 | 0.0286 |

> **M16 under the registered estimand (round 2, R2-2; this table stays as published).** The
> row above is 019's hybrid reading. Under native-for-both M16's σ is **0.29649** and its MDE at
> 019's n **0.1893** (the three N-columns scale by the same ratio: 0.1608 / 0.1523 / 0.1181);
> M13's and every per-protocol member's σ are unchanged, the per-protocol members' because the
> offset is subtracted from every arm-A unit of that population and a constant shift leaves a
> within-arm variance alone. The size-and-power simulation above (`oc18.py`) recomputed L2c's
> offset from each replicate's own pooled marginal under the SHARED weights of the reading then
> registered; it is not re-run here, it stays a labelled prior, and §2a.6's pilot dispersion
> pass (R2-13) is the registered re-derivation at the pinned effort.

σ across the family spans **0.0507 to 0.3216 — a factor of 6.3**. **Tier C's precision is the ITT
members' precision**: at N = 60/arm with every apparatus repair the binding MDE is **≈ 0.165** — for
M4 that is ≈ 4.9 of 33 witness classes; for M10 the units are mutant-multiplicity weights and
**must not be multiplied by 33** to yield a class count. The ITT members' variance is dominated by a
point mass of exact zeros — a real property of the treatment that no apparatus repair removes.

### 5.7 No author-side control gate (M-23, option (a))

**Ruled 2026-08-23: option (a) — no author-side gate.** 019's E1 existence gate ("at least one
admitted run reaches agreement ≥ x") is a **max statistic**: it fires iff *no* admitted run clears,
so P(fire) = (1 − p)ⁿ and its stringency runs the **wrong way** in n, which differs by arm.

| per-run clear rate | n=12 | n=34 | n=43 | n=50 | n=60 |
|---|---|---|---|---|---|
| 0.0833 (019 arm A, **undegraded**) | 0.352 | **0.052** | **0.024** | **0.013** | **0.005** |
| 0.040 (2× degradation) | 0.613 | 0.250 | 0.173 | 0.130 | 0.086 |
| 0.020 (4×) | 0.785 | 0.503 | 0.419 | 0.364 | 0.298 |
| 0.010 (8×) | 0.886 | 0.711 | 0.649 | 0.605 | 0.547 |

Two facts decide it. **(a)** The gate spuriously refuses arm A with probability **1.3–6.1 %** at
019-scale N *even with a perfect stimulus*. **(b)** To certify **P(fire) ≥ 0.95** at N = 50 the
degraded per-run clear rate must be ≤ **0.001025**, and bounding a rate that low by observation
needs, by rule of three, **~2,926 degraded runs** (~162 h at 199 s/call); at N = 60, ~3,511.
**The existence gate cannot be empirically certified at any affordable n** — that is a property of a
max statistic over a stochastic authoring process, not a criticism of the control.

**The registered reason for (a), stated in full.** The program's standing *mutation-check every
safeguard test* lesson says a safeguard that cannot be shown to fail must be labelled as one. **The
common-mode threat the existence gate names is a byte threat, and byte threats are caught
deterministically**: 020 pins `arms.<arm>.promptSha256`, the policy prose, the golden context and
both reference digests, and `references-reproduce-gold` holds 117/117 on both references. Those
gates fire with **probability 1** against corrupted prose, broken prompt assembly and a wrong naming
appendix. The existence gate would add a 1.3–6.1 % spurious-refusal risk and **no certified
detection power** on top of them. **An uncertified gate is not registered as if certified.**
Consequently E1 is fully descriptive (§5.1), the `e1-floor` row leaves the decision table (§5.9),
and the derived threshold survives only as C3's pre-freeze go/no-go (§2a.4).

### 5.8 Tier D — the registered descriptive battery

Published in full **whatever Tier C returns**, every table carrying *descriptive; published as an
interpretation quantity that no decision reads*:

- **The full estimand grid** — per-arm means at every analysis set × level × adjustment cell,
  corrected scorer, both slope-pooling conventions.
- **The single-choice ledger and the ITT × ANCOVA cells**, with the covert-population sentence
  attached (§5.2).
- **The eighteen point estimates, eighteen p-values, eighteen per-arm n, eighteen BCa intervals and
  the drop-a-pole table** — the published quantity set is **identical in every branch**, registered
  so the outcome cannot change what is reported.
- **Corpus structure:** pairing (33 / 69 / 62); single-witness fractions of the paired subset (28 of
  69 JPS, 20 of 62 Rego); union ceilings (exactly **8 paired mutants per language survive every
  identity-passing run**, so union kill is 61/69 and 54/62 and the union **class** ceiling is
  **28/33 in both languages**); the **five never-covered classes by name** with their sixteen
  mutants; the coverage distribution (identity-passing, 88 runs:
  `{12:1, 13:2, 15:1, 16:3, 17:6, 18:8, 19:12, 20:17, 21:21, 22:9, 23:7, 25:1}`, range 12–25,
  exactly one run reaching 25); the **per-class member-count imbalance table in full** (20 of 33
  unequal), which is a **mandatory** publication; the engine-supplied-kill column both ways; and the
  hitting-set result (21 of 51 distinct inputs reach 33/33).
- **`caseCount` as a construct quantity, not adjusted away:** it is measured on the authored artifact
  and is therefore **post-treatment**, and how many cases a representation leads an author to write
  is part of the construct. Published: the mediation decomposition (total effect, the `caseCount`
  path, the residual direct effect), the per-arm distribution, the within-arm slope at all three
  estimand levels, the balance test on means, and the missing-data disposition.
- **E1's descriptive battery:** the exclusive table of §5.1, per-run perfect agreement rate, the full
  row-agreement distribution, the same two on the 110-row support with S1 and S2 named, the E3
  taxonomy with `u1-*` and the two `p1-*` rows as named categories, and the Lee-style trimming bounds
  (trim fraction 19.8 %, k = 7 of 34 arm-A runs; A−C bounds **[+0.0236, +0.0629]** at L1 and
  **[+0.0166, +0.0672]** at L3) — published as diagnosis, **never as a Tier C member**, because the
  trim fraction is read off arm-labelled validity rates.
- **The M-14 mechanism battery:** the presence-idiom detector's per-arm counts, the arm-A/arm-B
  asymmetry note, and arm A's unexplained near-miss profile (92 % row accuracy, zero faults) — all
  direction-free, and **no decision reads any of it**.
- **`ownPolicyIdentity` (E6)** per run and per arm, and the composition of the conjunction population
  020 did not register.

### 5.9 Ordered, exhaustive decision rule (first matching row; last row always matches)

1. Any pin/schema/manifest failure, or apparatus failure making the batch non-terminal, **or C4's
   `pipeline-invalid` outcome (§2a.5)** → R1 inconclusive — pipeline-invalid.
2. A validated shortfall declaration (§1a) → UNRESOLVED-BY-DESIGN — no endpoint, no rate and no
   contrast is computed.
3. Any control-gate failure — both references reproduce gold imperfectly at attempt time; the
   capabilities canary passes; golden-context gate; `engine-execution-clean`; per-arm timeout rate
   above cap; **C4's `calibration-invalid` outcome** → R1 inconclusive — control gate failed.
   **There is no `e1-floor` row** (§5.7).
4. **All eighteen family members agree in the sign of the A−C difference and all eighteen reject at
   two-sided α = 0.05** → R1 = **CLAIM**, direction the common sign; then A−B under the identical
   rule.
5. Otherwise → **INDETERMINATE-BY-DISAGREEMENT**. **No claim in any direction is licensed, and this
   row triggers nothing.**

**No inferential quantity is computed, let alone published, at or above row 3.** A control-gate
failure adjudicates R1 in neither direction, and computing a contrast and then discarding it is not
that rule: the gate rows are evaluated first, the family is evaluated only for an outcome that would
reach row 4, and no direction and no A−B result is exposed otherwise. An **absent** primary contrast
is not a disagreeing one and never reaches row 5.

## 6. Validity channel (separate from detection)

Control gates, above every substantive row: both references reproduce gold 100 % at attempt time;
the off-gold equivalence certificate is current at the freeze commit; the OPA capabilities canary is
refused; the golden-context gate holds with the isolation negative control on record; **every scored
engine invocation of the attempt returned an answer** (`engine-execution-clean` — a pinned engine
that timed out, failed to compile or refused on a *frozen* study artifact is an apparatus failure,
and it is neither a kill nor an identity failure; **AMENDED 2026-08-24, R1-1: the gate's scan also
covers invocations on the AUTHOR'S artifact during admission and E1** — an engine that never
answered there files the run under `engine-invocation-refused` (§1a's amended table), the run
leaves every population, and the exclusion reaches this gate through `scoringApparatus`, so an
unanswered invocation can gate the attempt but can never move a rate — and this covers E6's extra
invocation too —
**with ONE registered exemption, ruled 2026-08-24 on round-1 finding R1-15: the sealed reviewer
holdout's invocations are EXEMPT from this gate and purely descriptive.** §4.3 registers that the
holdout moves nothing, and a pinned-engine refusal inside reviewer-authored prospective content is
published in the holdout's own record — scored "as authored", refusals listed beside kills — and
can neither gate nor invalidate the primary attempt; letting it would hand reviewer-authored bytes
a veto over the study, which is exactly what "moves nothing" was registered to prevent. The
exemption is the ruling §4.3 and this sentence had left implicit, and round 2 verifies it);
every binary digest matches its pin; the schedule matches the registered plan; **the C4 transfer gate
holds two-sided** (§2a.5). **A gate the scorer did not evaluate fails**: an absent gate is not a gate
that held. Manifest failures, unregistered absences, and enforcement failures are NOT-ADJUDICATED —
never detections.

## 7. Harness — 019's machinery inherited by port, and the deltas the rulings force

**The port is by digest under the `PORTS.md` discipline** (two-sided table; `integrity.py` verifies
the source study's lock first). Ported with no design change: the call wrapper, the three-arm batch
driver, the golden-context capture, the isolation negative control, the transcript binding and its
gates other than gate 5, the integrity chain, the single-publisher scorer's admit/ordered-codes/
terminality machinery, the exact rational Clopper–Pearson with its registered test vectors, the
per-language admission layer, the two-engine execution layer, the alignment map, the registered
input domain with its symmetric per-arm case enumeration, the mutant/kill machinery with
`referenceIdentity`, `leak_tokens.py`, and the `DEVIATIONS.md` machinery.

**Integrity is a gate against drift, not a root of trust, and the bootstrap is stated rather than
glossed.** `integrity` is the only study-local module the scorer imports at module scope, it imports
no study-local module itself, and `integrity.verify()` is the first study-local call the scorer
makes. What that cannot be is a proof that the checker is the checker the manifest describes. The
exact-set manifest covers every byte the scorer executes and every payload it reads; the manifest is
scoped per ADR 0004, with `DEVIATIONS.md`, `README.md`, `PREREG-REVIEW.md`, `CORRECTION-TARGETS.md`
(named while absent, refusing `--freeze` on it) and `harness/ADVISORIES.md` excluded by named
constant, each with an asserting test. **Anchor order is linear and one-directional (ADR 0005):
covered files → manifest → the registry pins the manifest → the commit anchors the registry.** The
manifest is regenerated **last** in every reconciliation. **Suite-of-record claims are
archive-verified (ADR 0005, decision 1):** a "N passed" claim is made only of a commit, after
`git archive <commit> | tar -x` into a fresh directory, `git init && git add -A` inside it, then the
full suite under the registered interpreter — **before push, ceremony and prompt-only commits
included.**

**The registered deltas, each with its day-one work item.**

1. **The scorer's survivor-vector schema — the token collision is fixed.** The scorer **emits an
   explicit per-mutant survivor vector for every admitted run** and **never encodes "nothing
   evaluated" and "everything killed" with the same token**. It also emits `caseCount` for every
   admitted run with a suite. A harness test drives the refusals, and the mutation check is
   required: break the refusal, confirm the test fails.

   > **AMENDED, 2026-08-24 (round-1 finding R1-2, marked).** This delta's first wording kept
   > 019's refusal condition — `survivorsPaired: []` with `killedPaired: 0` refuses at write
   > time — which was right for 019's records (no vector, so that state IS the collision) and
   > wrong once this delta's own vector exists: with a total, registered-vocabulary vector on
   > every record, that aggregate state is exactly what the REGISTERED nothing-was-evaluated
   > record looks like (`evaluatedPaired: 0`), it arises on the most common production paths
   > (no suite, no cases, out-of-domain, identity failure), and refusing it hard-aborted the
   > attempt one such admitted run in. The write gate now holds the VECTOR authoritative and
   > refuses genuine inconsistency between vector and aggregates in any direction —
   > `killedPaired` off the vector's count, `survivorsPaired` off its SURVIVED entries,
   > `evaluatedPaired` off its evaluated count (the genuinely impossible state the old guard
   > was reaching for). The total not-evaluated record is ACCEPTED as the registered ITT-zero
   > state. The token collision stays fixed — by the vector, which is where this delta fixed
   > it all along.
2. **Per-language cuts machinery: retained, with no threshold on top of it.** The machinery that
   keeps each language's paired-adequate denominator and lattice separate is **kept** — it computes
   and publishes both denominators (69 JPS / 62 Rego included, 57 / 55 excluded), both lattices and
   the shared-class count (33 included, 29 excluded), and 019's R1-1 lesson (one cut derived from
   the JPS count and applied to every arm) must remain structurally impossible. What is **removed**
   is the threshold arm: no τ, no integer cut, no `highKill` member, no reachability assertion,
   because there is no cut to assert. A harness test asserts **no registered decision path reads a
   cut**.
3. **The new admission code.** `harness/e4lib/presence_idiom.py` and the `presence-idiom-unsound`
   code, wired into `admit()`, §1a's partition table, E2's ordered table and the partition-diff test
   (§3.2). Gated on §3.2's pre-freeze power analysis.
4. **The `ownPolicyIdentity` invocation.** One extra engine EXPOSURE per admitted run (invocation
   count arm- and case-dependent as §1.2 measures it, R1-14), routed through the same
   `engine-execution-clean` control (§6) via its own refusal member (`e6EngineRefused`), so an E6
   refusal can neither overwrite a completed `referenceIdentity` result nor hide from the gate.
   `referenceIdentity` and `ownPolicyIdentity` are two named relations in the scorer, never one
   field with two meanings, and E6's published rate divides by the runs E6 actually answered for,
   with the not-asked count printed beside it.
5. **The family scorer.** New: the eighteen members, L2c's offset estimator, the two permutation
   schemes with their pinned B and seed, the IU verdict, the drop-a-pole table, the BCa intervals,
   and the **refusal** rather than fallback on the ITT × ANCOVA cell (§5.2).
6. **`registeredLabelRule`** — restated with `codex.reasoningEffort`, the null-⇒-PILOT test and the
   `--sweep` exemption (§2.1); **moved out of the ported-unchanged list** and driven in
   `harness/tests/test_pins.py` pin by pin.
7. **The batch schedule** — re-derived at the registered round count with the new attained position
   spread published and `batch.order` / `batch.n` / `batch.slots` re-pinned (§2). `test_schedule.py`'s
   50-round assertion is wrong by construction at any other N and is rebuilt, not patched.
8. **The freeze gate's `calibration/` rule** — permit and require the subtree, still refuse any
   `results/primary-attempt-*`; written into the gate and its test before the first pilot call.
9. **A fresh sealed reviewer mutant set** (§4.3).
10. **`render_round_status.py` ports with the harness, with one registered change.** 019's
    `parse_block()` refuses a block registering **zero** rounds, because 019 first wrote the block
    after round 1 existed. **020 opens its review record before any round runs**, so the port
    **permits the empty-of-rounds block** and renders it (`0 review rounds are on the record …`);
    every other refusal — duplicate members at every depth, closed object shapes, the closed verdict
    vocabulary bound to the review prompt's output line, the single-open-round rule, contiguity, and
    the marker-span reading — is ported unchanged. `SURFACES` narrows to **two** front doors,
    `README.md` and `PREREGISTRATION.md`; 019's third (`design/POLICY-DRAFT.md`) is not a 020 front
    door because 020's policy prose is ported frozen rather than drafted here. The first act of the
    port is `--write`, which replaces this document's hand-written sentence with a rendered one.
11. **`DEVIATIONS.md` is outside the freeze set** — carried from Study 018's lesson and from ADR
    0004's rule, with an asserting test. (R1-18 settled a claim made in this delta's name that
    this text never carried: `CORRECTION-TARGETS.md` is COVERED and freezes with the tree — §10's
    amended sentence governs — and only `CORRECTION-TARGETS-LOG.md` shares `DEVIATIONS.md`'s
    appendable status.)
12. **`design/pilot/pilot_run.py` is deleted, not ported** (§2a.2).
13. **D-1's smoke is restated** as *"a real exec at the registered prompt bytes, stand-in binary
    permitted"* — D-1's failure was `/usr/bin/env: Argument list too long` at `exec`, which a
    stand-in binary reproduces exactly — with D-2's stand-in-**study** smoke preserved and its real
    calls in §2.1's budget.

**Deterministic regeneration of the mutant corpora** is claimed by
`design/mutants/regenerate.py --arm both --check`, ported with its three registered properties: the
committed record covers **both** arms, the fail-closed adequacy census is evaluated **under the
regenerated tree**, and the adequacy stamp is **inside** the regeneration chain. CI runs the
deterministic controls only; the batch never runs in CI.

## 8. What is enforced, what is recorded, what is not prevented

**Enforced:** pins, digests, population membership, the registered input-domain check on every arm's
enumerated cases, `referenceIdentity`, the extraction rule, the schedule, the transcript binding on
every completed slot, the C4 transfer gate, the survivor-vector schema, and the presence-idiom
detector — whose §3.2 power analysis has been executed and CERTIFIES it (40/40 in-class runs coded,
0/22 perfect runs flagged, 0/392 lawful `in` uses), so the conditional is discharged and the code
`presence-idiom-unsound` is registered.

**Recorded:** durations, token counts including `reasoning_output_tokens`, per-case diagnostics,
every completion verbatim, the sweep's full per-setting table, the pilot's rates, and `E6`.

**Not prevented, stated plainly:** provider-side cross-session state (the independence premise behind
every interval is unclosable from retained bytes); an operator running and discarding an unrecorded
batch; the model having seen public Rego corpora at pretraining (§9); **and the reasoning-effort
condition itself if the witness-resolution step finds no transcript member — in that branch the pin
is a recorded intention, asserted by the wrapper and not independently witnessed (§2.1, §11.5).**
Nothing in the retained artifacts proves the published slots are all the invocations that occurred;
integrity rests on ledger discipline and re-runnability.

## 9. What this study cannot show

**A−C is a bundled treatment and nothing inside the bundle is separable** (§1.1, §3). Arm C differs
from arm B in representation-adjacent *formality* **and** in substantive *content*, and the arms'
prompt exposures differ in bytes as well. **No A−C or A−B result licenses any statement about which
component of the bundle produced it** — not "the pack format wins", not "the schema is what
matters", not "the convention is doing the work". The registered claim is about the bundles as
authored, and a component-attribution study is a different design. This non-claim is carried
verbatim in force from 019 and is not weakened by the change of endpoint.

**No Tier D quantity decides anything.** Every descriptive quantity in this study — 019's known
direction, the eighteen-member reprints, the single-choice ledger, the estimand grid, the corpus
structure, `caseCount`'s mediation decomposition, the Lee bounds, E1, E2, E3, E5, E6, the presence-
idiom counts and arm A's unexplained near-miss profile — is published under the standing clause
*descriptive; published as an interpretation quantity that no decision reads*, and **an
INDETERMINATE Tier C outcome licenses no negation.** A split family is not evidence of no effect,
**no member is promoted after the fact** — there is no primary specification, there is a family, and
the study may not report "on the primary specification the effect was significant" — and the split's
arm-blind diagnosis (which axis carries it) is a Tier D finding, not R1.

**What a Tier C claim would and would not assert.** When the family is unanimous, R1 asserts: *within
the registered fragment, under single-shot authorship, arm A's suites cover a different fraction of
the shared witness classes than arm C's — and the difference is present whether or not authoring
failures are counted, whether or not suite size is held fixed, whether classes are weighted equally,
by mutant multiplicity, or by de-biased native denominators, and whether or not engine-supplied kills
are excluded.* That conjunction **is** the claim; it is the only thing the tier licenses. Tier C
cannot rescue a design whose members answer materially different questions — criterion (ii) is the
only guard, and it is a judgement, not an arithmetic.

Everything is measured **within the JPS-expressible fragment, selected by arm A's expressive envelope
and no other criterion** (Study 003: 12/12 real decisions escape the pack); nothing generalizes to
business judgments at large. Single-shot authorship only; no outcome speaks to tooled authoring
workflows, nor to the deferred fourth-arm prevalence control. One model, one prompt per arm, one
policy family, one batch window. **No direction of any result separates representation quality from
training familiarity**: the public Rego corpus is vast, the JPS corpus is this program, and both
directions are reported as confounded. Coverage measures agreement-anchored mutation detection over
registered single-edit mutants — not test quality at large, not defect rates in production, and (for
the engine-supplied column) partly the engine's structural checks rather than authored assertions,
reported both ways. **The mutant space inherits the arm-A reference's shape**: nine `r-o1-review`
mutants change no cell's answer and no suite in any arm can detect them. A coverage rate is bounded
by what the reference makes observable. The gold suite is two authors deep plus a clean-room check
that shares the gold author's model lineage. The census's expressiveness rows and these rates live on
different stimuli: **no tradeoff statement combining them is licensed** (a `CORRECTION-TARGETS.md`
target).

**The standing program ceiling, restated because it binds this study too.** This program measures
**binding, lineage and expressiveness — never truth.** Nothing here measures whether any policy or
any fact is true, nothing here is evidence that a decision was correct, and **nothing in this study
claims JPS conformance.**

## 10. Publication commitment

All eighteen point estimates, all eighteen p-values, all eighteen per-arm n, all eighteen BCa
intervals, the agreement table, the drop-a-pole table, the single-choice ledger with its structural
offset attached, the full estimand grid, every identity-failure and out-of-domain-case count, every
authoring code including `presence-idiom-unsound`, both group counts, both denominators and both
lattices, E1's two strata, E6, the sweep's full per-setting table, the pilot's rates and the transfer
gate's rows are **published whichever way they land, with a pass's prominence**, and **the published
quantity set is identical in every branch of §5.9** — registered so that the outcome cannot change
what is reported.

**What "all quantities" means, and the one thing this commitment does not promise.** Every quantity
that EXISTS is published whichever way it lands, and nothing is withheld for being unflattering. It
is **not** a promise that a family evaluation exists in every outcome, because §5.9 forbids computing
one above row 3: an outcome that reaches a gate row has **no** A−C or A−B evaluation to publish, and
the record says so by naming the row and the cause rather than by printing an endpoint. A blocked
evaluation is published as blocked, with its cause, in the same record and with the same prominence.
The rule is ordered rather than conditional, so it holds for a gate failure discovered LATE as well
as early. **Publishing a number the registered rule says must not be computed is not a stronger
publication commitment; it is a violation of §5.9 wearing one.** An INDETERMINATE-BY-DISAGREEMENT R1
is reported with the same prominence as a CLAIM — and §5.6(4) commits the study to publishing "if the
truth resembles 019, Tier C returns INDETERMINATE" as a *planned*, not a disappointing, outcome.

**Correction targets are a registered document, pinned before the freeze.** `CORRECTION.md` targets —
**verbatim wording, venue, URL, retrieval date** — are pinned before the freeze in the registered
document **`CORRECTION-TARGETS.md`**, in Study 019's pattern (019 round-7 finding R7-9: the obligation
was once declared in a publication section and enforced nowhere, so the ceremony could complete
without it). It is named in `harness/make_manifest.py`, **which names it while it is absent and
refuses `--freeze` on it**, and the freeze runbook carries the step that lands it. **AMENDED
2026-08-24 (R1-18): the register is COVERED by the exact-set manifest and freezes with the
tree** — its first registration excluded it as appendable, and a precommitment the maintainer
may rewrite post-freeze precommits nothing; post-freeze venue or status changes append to
`CORRECTION-TARGETS-LOG.md`, which is the appendable half. `GATE(pre-freeze)`.
020's targets must include, at minimum: the R1 verdict sentence `ANALYSIS.md` will publish (quoted
verbatim from the scorer's published `verdict` member, whose vocabulary is the closed
CLAIM / INDETERMINATE-BY-DISAGREEMENT pair plus §5.9's gate rows); the study-index and repo-root index
rows; this study's README round-status sentence; **the presence-idiom guard's published power
analysis (§3.2)**; **the pre-pilot sweep's published table and the compute condition chosen from it
(§2.1)**; and the Tier D reprints of §5.5, which are quoted from a superseded study's batch and are
correctable only by a `DEVIATIONS.md` entry once frozen. A correction lands in the SAME file at the
SAME prominence, and for a corrected or retracted R1 additionally as a banner at the head of
`ANALYSIS.md` and an entry in `DEVIATIONS.md`, which is freeze-excluded precisely so it can receive
one. **A correction is written in every branch, including "no correction needed" being visibly
audited.**

## 11. Registered ceilings — what 020 will not be able to show

Every §9 ceiling of Study 019 continues to bind verbatim. These bind further, and each is registered
here rather than discovered in the results.

1. **The endpoint is witness-input coverage against the shared reference** — not pinning power, and
   not pinning against the policy each suite accompanies (Fact 1, §1.2). E6 reports the severance; it
   does not repair it.
2. **Effective support is 28 of 33 classes**, and both arms' floors are displaced downward by
   5/33 = 0.1515. No member can exceed 28/33.
3. **Tier C is conservative against a real total effect that runs through suite size (M-22, ruled
   accepted and printed).** Requiring the adjusted member to agree means that **if the representation
   effect operates *through* `caseCount` — which is part of the construct, since how many cases a
   representation leads an author to write is itself an effect of the representation — Tier C returns
   INDETERMINATE on a real total effect.** That is a **designed property, accepted in advance, and
   printed here rather than discovered in results**; the alternative — dropping the adjusted members —
   hands the verdict back to a single contaminated choice, and §5.6 shows a suite-size-only channel
   rejecting 98.6–99.8 % of the unadjusted per-protocol members.
4. **Tier C's power depends on a quantity 020 cannot know in advance** (the per-arm authoring-validity
   rate), and in the regime where it looks powered, six of eighteen members are near-automatically
   satisfied by a channel that is not the construct (§5.6).
5. ~~The reasoning-effort pin may be a recorded intention, not a verified condition~~ **RETIRED
   BY MEASUREMENT, 2026-08-24** (§2.1, M-24): the sweep's witness-resolution step found the
   effort named non-null in `turn_context` and gate 5 now binds the pin against the transcript,
   so the ceiling's condition — no witness exists — measured false. It is struck rather than
   deleted so the record shows a registered ceiling can retire only by the registered
   resolution step, never by editing. What remains true and is NOT retired: the pin binds the
   REQUESTED tier; no transcript member proves what the service did with it beyond the
   reasoning-token counts it returned.
6. **019's pilot compute condition is unrecoverable**, so no transfer gate can be evaluated against it
   on the model, isolation or reasoning-token rows; service-side drift over 2026-08-15 → 2026-08-21
   cannot be excluded (§2a.1).
7. **The E1 descriptive support was narrowed to 110 rows on grounds known in advance to favour one
   arm's profile.** Both strata rates are published per arm with E1's prominence (§4.2).
8. **The all-rule attainability asymmetry is not repaired** — only the weighting asymmetry is. Under
   the all-members rule an arm-A suite must kill six mutants to score the `d7-39-100k` unit where an
   arm-C suite kills three, and the offset formula assumes π_g is common to both arms, which unequal
   member counts and unequal per-class difficulty deny. **V8-22 stays live in the asymmetry ledger,
   and a new ledger row is registered for group-size imbalance.**
9. **L2c's offset is estimated**, on a coverage marginal computed over a post-treatment-selected
   cohort, with its estimation variance not propagated, and for the adjusted members it is subtracted
   before the ANCOVA so the adjusted contrast inherits it linearly (M-16(d), §5.2).
10. **`identityPass` has changed meaning, and the residual is named** (M-13, §1.2). 020 registers two
    relations and gates on `referenceIdentity` alone, so the per-protocol populations and §5.6's
    dispersion figures remain applicable. **Had the gate moved to the conjunction, every per-protocol
    member's population would have moved with it** and §5.6 would have to be re-derived; a later
    deviation that moves the gate carries exactly that obligation.
11. **The presence-idiom guard is arm-asymmetric by construction** (§3.2). `presence-idiom-unsound` is
    structurally unreachable in arm A, because arm A's format has no analogous single-operator trap on
    this surface; arm A's own near-miss profile in 019 (92 % row accuracy, zero faults) stands
    **unexplained** by any mechanism 020 registers. The guard is a detector over one language's known
    trap, not a symmetric control.
12. **No author-side control gate exists** (M-23, §5.7), so 020 has **no** certified detection power
    against an author-side stimulus regression beyond the deterministic digest pins. That is a
    deliberate trade — an uncertifiable gate with a 1.3–6.1 % spurious-refusal rate is worse than
    none — and it is a ceiling, not a strength.
13. **`caseCount` is post-treatment and is not adjusted away.** The adjusted members estimate a
    controlled direct effect, not the total effect §1.1 asks about; both poles are required to agree,
    which is ceiling 3 read from the other side.

## 12. What we would do with each outcome (NOT a registered commitment)

Discussion only; no observed result obligates any of it. **If Tier C returns a CLAIM**, the direction
is the family's common sign and the claim is the conjunction of §9's sentence — the program then has
a robustness-anchored reading of the pack format's testing story, still bundled, still inside the
fragment. **If Tier C returns INDETERMINATE-BY-DISAGREEMENT** — the outcome §5.6(4) says is likely if
the truth resembles 019 — the result is *not* a null: it is a measured disagreement, published with
the axis that carries it, and the study's yield is Tier D's descriptive battery plus a repaired
instrument. Whether that yield is worth the spend is a programme judgement that belongs to the
maintainer and is deliberately not decided in this document. **In every branch**, the bundled estimand
(§1.1, §9) means the next artifact cannot start from a component attribution this study did not make,
and the standing ceiling means it cannot start from a claim about truth.
