# Scaffold — what this harness is, and precisely what remains

This file is the honest half of the port. `harness/PORTS.md` says what was
taken and what changed; this says what has **not** been built, by name, with
the source it comes from and the order the remaining work has to happen in.
It is deliberately **outside** the study manifest (`harness/make_manifest.py`
covers `harness/*.py`, `harness/*.sh` and the registered documents, not this
file): it is a work record that will be appended to and then deleted at the
freeze, and ADR 0004's argument about appendable files applies to it exactly.

**Superseded by V1/V2/V4 below: the harness runs a batch end to end, and the
three defects the first smoke found are fixed.** The wrapper, the schedule, the
driver's calling half, the isolation controls and the scorer all exist and are
tested, and the twelve-slot PILOT smoke has been driven through all of them
twice against the real pinned engines with the authoring CLI stood in
(`harness/tests/E2E-SMOKE.md`). **Every scorer item below — S6, S7, S8, S9, S10,
S11 — and G3's residual has LANDED**; the scorer publishes no refusal at all on
the smoke batch. **T3 and section C have since landed too** (round-4 finding
R4-6, which found this sentence still claiming T3 was owed): the design sources
are committed, no `__pycache__` survives, and the `study-019-harness` job is in
`.github/workflows/ci.yml`. **Nothing in this file is owed any more**; what
remains is section F's freeze-fill, which is the ceremony's and not the
harness's. The state today, said plainly: every
freeze pin in `harness/PINS.json` is null, `integrity.study_label()` returns
`PILOT`, and **no authoring call has been made** — no model has been asked
anything by this study.

## What exists and is tested

| file | state | tests |
|---|---|---|
| `harness/authoring_call.sh` | complete port, five registered differences | `tests/test_batch.py` (T1 landed) |
| `harness/batch.py` | schedule core, timeout constants, §1a code partition, and the whole calling half (D1–D8, G1–G2) | `tests/test_schedule.py` (13), `tests/test_partition.py` (6), `tests/test_batch.py` |
| `harness/integrity.py` | partial: chain, interpreter, unreviewed-bytes gate, label rule, manifest check | `tests/test_pins.py` (8) |
| `harness/transcript_check.py` | complete port; `LEAK_TOKENS` **is** `leak_tokens.SCREEN_TOKENS` (G3 residual LANDED) | `tests/test_leak_tokens.py` (30) |
| `harness/make_manifest.py` | complete port, ADR 0004 applied | `tests/test_manifest.py` (8) |
| `harness/score.py` | **assembled** — the single publisher: attempt record, terminality, the PREFIX population rule (S11), E1/E2/E3/E4/E5, the floor gate (S10), the decision table | `tests/test_score_attempt.py` (57) |
| `harness/e4lib/stats.py` | ported by digest: Clopper–Pearson, the general unequal-N FM contrast (S8) and the Δ₀ sweep (S7) | `tests/test_score_stats.py` (34) |
| `harness/e4lib/extract.py` | assembled: the registered marker rule | `tests/test_score_extract.py` (12) |
| `harness/e4lib/admit.py` | assembled: §1a's SIX authoring codes, arm-structural enforced | `tests/test_score_admit.py` (22) |
| `harness/e4lib/engines.py` | assembled: two-engine layer, binaries fail-closed, capabilities canary | `tests/test_score_engines.py` (15) |
| `harness/e4lib/e4.py` | assembled: pairing, identity, kill with the engine-supplied split (S9), the per-language τ cuts. **No X1 filter — the registered exclusion registry is EMPTY** (round-1 R1-2) | `tests/test_score_e4.py` (34) |
| `harness/e4lib/census.py` | ported: 012's census machinery; the §5 stimulus is registered and READ (S6) | `tests/test_score_census.py` (16) |
| `harness/e4lib/decision.py` | assembled from the 015–018 shape as an ordered table | `tests/test_score_decision.py` (19) |
| — | the assembled pipeline against the REAL pinned engines | `tests/test_score_pipeline.py` (12, skipped without the pins) |
| `harness/PINS.json` | every freeze pin null; toolchain blocks resolved and marked; `ownPorts` re-pinned (V1) | `tests/test_pins.py` (8) |
| `harness/PORTS.md` | **seven** rows, two-sided, machine-read, plus the assembled-module lineage table | `tests/test_ports_chain.py` (7), `integrity.verify_chain()` |
| — | the whole harness end to end, no codex call, real engines | `tests/E2E-SMOKE.md` (transcript, not a suite) |

The scorer's own ten modules contribute 227 passing tests under CPython
3.12.11 — 215 deterministic, plus the 12 in `tests/test_score_pipeline.py`,
which run against the real pinned `jpack` and `opa` when
`JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` hash to the pins and SKIP by name otherwise
(§7: the engines are never invoked in CI). `tests/test_partition.py`'s last
test, written skipping since the scaffold, is a live assertion now.

**Superseded by V1.** `tests/test_manifest.py`'s exact-set assertion PASSES
(`PREREGISTRATION.md`'s move and the missing `harness/e4lib/` glob were the two
reasons it failed, and M1 item 4 closed both), `integrity.verify_chain()` PASSES
over all seven rows, and `verify_interpreter()`, `study_label()` and
`unfilled_pins()` pass against the committed tree. `integrity.verify()` as a
whole still refuses — for **T3** alone now. The whole suite is **387 passing**
under CPython 3.12.11 (353 at V1; the six scorer items added 34), and the twelve
`tests/test_score_pipeline.py` cases RUN rather than skip when
`JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` are the pinned binaries.

What the pipeline suite established against the pinned binaries, so that it is
written down rather than remembered: the reference pack admits through the real
`jpack spec validate`; every gold row reproduces in BOTH languages (the suite reads
the committed suite, 117 rows at this revision); the arm-A
identity control passes on a matrix drawn from gold; `opa test` passes the
reference against the reference suite and the same suite kills a real Rego
mutant; the `time.now_ns` canary is refused with `rego_type_error`; and the
`v0-syntax` discriminator fires on a real v0 policy (`rego_parse_error` under
v1, exit 0 under `--v0-compatible`) while a type error files as
`opa-check-failed`.

---

## V — the verification pass, and the three defects it found

A verification pass ran the whole suite, then drove the harness end to end
against the real pinned engines with the authoring CLI stood in. The transcript
is `harness/tests/E2E-SMOKE.md` — commands, digests, no timestamps. Three things
came out of it, in the order they matter.

**V1 — M1 is CLOSED.** Points 1–4 all landed, in the registered order
(`PORTS.md` before `PINS.json`, the manifest before the pin over it):
`integrity.REQUIRED_PORTS` registers **seven** destinations;
`integrity.TIER1_TWELVE_PATHS` maps `harness/e4lib/stats.py` to 012's
`harness/score_rates.py` and `harness/e4lib/census.py` to 012's
`harness/census.py`, both tier-1; `make_manifest.manifest_entries()` globs
`harness/e4lib/*.py`; `harness/STUDY-MANIFEST.sha256` is regenerated (33
entries) and `ownPorts.sha256` re-pinned over the rewritten `PORTS.md`.
`integrity.verify_chain()` now PASSES over all seven rows and
`tests/test_manifest.py`'s exact-set assertion passes. Two test modules carry
the new behaviour rather than leaving it to the tree: **`tests/test_ports_chain.py`**
(new — the exact destination set, the two scorer rows' tier-1 binding, every row
verified two-sided, and a row removed and a row added each refusing over a
mutated copy whose registry pin was rebuilt) and a new case in
`tests/test_manifest.py` asserting the scorer package is covered **module for
module against the directory**. The suite is **353 passing**, with all ten
`tests/test_score_pipeline.py` cases RUNNING against the pinned binaries.
`integrity.verify()` as a whole still refuses, now for **T3's reason alone**.

**V2 — the end-to-end smoke ran green through the apparatus.** **ARCHIVED RUN RECORD,
second pass.** The corpus numbers in this paragraph were measured against the
PRE-REPAIR arm-A reference and its 145-mutant corpus, and every one of them has since
moved: the current figures are in `harness/tests/E2E-SMOKE.md` §9 (third pass) and are
recomputed from the artifacts by `tests/test_prereg_currency.py`. In particular the
single cross-language τ cut recorded below was round-1 finding R1-1's defect — there
are two integer cuts now, one per language. The paragraph is left as written because
it is a record of a run, not a claim about the tree. Twelve slots
through the real wrapper and the real driver (`--runs 12` plus a shortfall
declaration — the registry cannot name another N, and `check_registry()`
refusing one is the guarantee working), then the scorer over the batch. What was
established mechanically: the label is PILOT and `pinsRawSha256` is the
COMMITTED registry's; the short-batch XOR branch of `terminality()`; both engine
digests enforced with the null capabilities pin recorded as unenforced; the
capabilities canary refused against the real binary; 134 witness groups, 81
paired adequate JPS and 73 paired adequate Rego, and the τ cut derived at run
time as 77 of 81; the identity control passing on the reference-derived suites in
every arm; kill rates computed over the paired subset; E1 reporting; the three
registered refusals (`E5-STIMULUS-UNREGISTERED`,
`E4-ENGINE-SUPPLIED-UNREGISTERED`, `FM-UNEQUAL-N` — S6, S9 and S8 all reached for
real); the decision table reaching terminal row 2; and rescoring **byte-identical**
under a different parent with the same attempt basename.

**V3 — three STRUCTURAL defects in `harness/score.py`. ALL THREE ARE FIXED
(V4).** Each changed what a published population is, so each was a review
decision and not an integration repair. `E2E-SMOKE.md` section 8 now carries the
first pass's number beside the second's for each one.

* **V3a — absent slots entered every population as admitted runs.**
  `population()` partitioned on `slot["code"]` and never on `slot["present"]`;
  an absent slot has `code: None`, which is not an apparatus code, so all 138
  absent slots entered their arms' denominators and `score_run()` gave each one
  `no-marker-block` from a `None` completion. Observed denominators 49/50/50
  over a twelve-slot batch. **Fixed:** `population()` takes the arm's slots that
  are PRESENT and publishes `registered`, `absent` and `attempted` beside the
  denominator. The smoke reads `registered 50, absent 46, attempted 4` in every
  arm, and E1 reads 3/3, 3/4, 4/4 where it read 3/49, 3/50, 4/50.
* **V3b — a timeout was scored as `slot-shape`.** `read_slot()` tested for
  `REFUSAL.json` before it read `CALL.json`. Both codes are apparatus so no
  denominator moved — but `timeouts` counted 0 and the control gate
  `timeout-rate-within-cap` held over a batch that contained a timeout.
  **Fixed:** the outcome comes from `batch.slot_outcome()`. The smoke reads
  `apparatusCodes {"call-timeout": 1}`, `timeouts: 1`, and
  `timeout-rate-within-cap held: false` as a decision cause.
* **V3c — the E2 table could not report a single authoring code.**
  `e2_profile()` counted `slot["code"]`, which is the wrapper's exit status, and
  every code the wrapper can produce is on the apparatus side. **Fixed:** E2
  counts the RUN records, refuses an apparatus code on one, and publishes
  `artifactAdmitted` beside `admitted`. The smoke reads arm B
  `no-marker-block: 1` where it read every code at zero.

**V4 — the closeout pass: S6–S11 and G3's residual all LANDED.** In the
registered order — S11 first, because it changes every published denominator —
then S6, S7, S8, S9, S10, G3. Each landed as a COMPUTATION and not as the
removal of a guard, and the smoke re-ran green through the whole apparatus with
an EMPTY `refusals` object: `E5-STIMULUS-UNREGISTERED`,
`E4-ENGINE-SUPPLIED-UNREGISTERED` and `FM-UNEQUAL-N` are all numbers now. The
suite is 387 passing, all twelve pipeline cases running against the pinned
binaries; rescoring is byte-identical under a different parent with the same
attempt basename; and a slot with one byte appended after its seal takes the
whole scoring to decision row 1, pipeline-invalid.

## M — what the new ports moved, and what has to move after them

**M1 — CLOSED (see V1). What follows is the record of what it required.**
`harness/PORTS.md` grew two rows (`e4lib/stats.py`, `e4lib/census.py`) in the
registered order — step 6 below says "`PORTS.md` before `PINS.json`, always" —
and four things must now follow it, none of them optional and none of them
silent:

1. `harness/PINS.json`'s `ownPorts.sha256`, which pins this file and no longer
   matches. `verify_chain()` refuses on it today.
2. `integrity.REQUIRED_PORTS`, which registers the destination set as EXACTLY
   five files and must become seven — it exists so that a deleted row refuses
   rather than quietly dropping a check, and an added row must be as loud.
3. `integrity.TIER1_TWELVE_PATHS`, which must map `harness/e4lib/stats.py` to
   Study 012's `harness/score_rates.py` and `harness/e4lib/census.py` to 012's
   `harness/census.py` — both are tier-1 rows, because 012's own PORTS.md
   publishes a destination cell for each and those cells are what the source
   side answers to.
4. `harness/make_manifest.py`'s `manifest_entries()`, which globs
   `harness/*.py`, `harness/*.sh` and `harness/tests/*.py` and therefore covers
   **none of `harness/e4lib/`**. Seven reviewed sources outside the exact-set
   manifest is exactly the hole ADR 0004's manifest exists to close, so the glob
   must grow a `harness/e4lib/*.py` entry and `harness/STUDY-MANIFEST.sha256`
   must be regenerated (step 7 below), before `studyManifest.sha256` is filled.

None of this is a defect the scorer hides: `harness/score.py` files a
`verify_chain()` refusal as a pipeline problem, and a pipeline problem is row 1
of §5's decision rule — the attempt is pipeline-invalid and adjudicates nothing.

## S — the scorer, assembled from the design prototypes — **LANDED**

S1–S6 are built, with three named refusals carried forward as S6, S7 and S9
below. What follows records what each item became and what it still owes.

The scorer is one file (`harness/score.py`), because the preregistration's
governing invocation is one command and "the scorer is the only publisher".
Its parts already exist as design prototypes and must be ported into it with a
two-sided `PORTS.md` row each — the prototypes are working code, not sketches,
and re-authoring them from memory would throw away the only artifacts that have
been run against the real engines.

**S1 — `harness/score.py` — DONE.** The argument surface is
`--attempt-root` plus `--batch-root` and `--include-reviewer-set`; an existing
attempt root is refused; the label is `integrity.study_label()`'s and is stamped
into every output; `terminality()` declares a short batch rather than scoring it
(Study 012 §2.8's rule, ported); the Clopper–Pearson intervals are
`e4lib/stats.py`'s and reproduce Study 012's registered vectors to the four
decimals 012 printed. `ADMISSION_CODES` is built from `batch.CODE_PARTITION`
rather than written out, so it cannot drift from it, and
`tests/test_partition.py`'s last test is a live assertion now rather than a
skip. No output embeds a timestamp or an absolute path: `score.scrub()` runs at
the writer, so a refusal added later cannot reintroduce a path leak, and
`tests/test_score_attempt.py` scores the same tree twice into two roots with the
same basename under different parents and diffs the bytes.

**S2 — extraction and admission — DONE, with the reconciliation made.** The
pilot's three codes became §1a's six, and the split is by WHICH CHECK REFUSED
rather than by a judgement about the artifact. The one piece with no prototype
is the `v0-syntax` discriminator, and it is built to be mechanical: at v1.19.0
both a v0 policy and a garbled one surface as `rego_parse_error`, and the
messages that distinguish them are upstream's prose, which this study does not
publish — so the discriminator is a SECOND compilation of the same bytes under
`opa check --v0-compatible`. Bytes that fail under v1 and compile under v0 are
v0 syntax by the compiler's own reading. Verified against the pinned binary
while the module was written; both branches are driven in
`tests/test_score_admit.py`. `ARM_REACHABLE_CODES` makes §5's arm-structural
rule an enforced refusal rather than an unlikely event.

**S3 — the two-engine execution layer — DONE.** Every flag is carried verbatim
and `tests/test_score_engines.py` asserts the argv rather than running it (§7
forbids invoking the engines in CI). New and load-bearing: `Toolchain` resolves
`JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` to real paths, hashes them, and REFUSES on any
mismatch with a non-null pin before the first subprocess — §2's stated hazard is
that the operator's PATH carries jpack v0.10.0. A NULL pin (today,
`opa.capabilitiesSha256`) is recorded in `unenforcedPins` rather than silently
satisfied. `capabilities_canary()` carries the probe's three lines in the
reviewed source, so the gate cannot be defanged by editing a fixture, and its
record says `refused` rather than `passed` because §5 spells the FAILURE as
"capabilities canary passes".

**S4 — the E4 machinery — DONE, with one refusal (S9).** Pairing, the identity
control, kill and the aggregation are `e4_score.py`'s. Added: `in_x1()` as a
named predicate with its own test block, asserted against the same three numbers
`design/gold/check_gold.py` enforces over the gold suite — including that an
UNREADABLE risk is not in the band, so gold cannot contain a row the filter
would have excluded; `partition_x1()` applied once so identity and kill see the
same case set by construction; the identity control as a first-class per-arm
rate; and `stats.tau_cut()`, which derives §5's operative INTEGER cut from the
paired count at run time and which the scorer prints. δ = 0.20 is carried as
`stats.DELTA` and is deliberately read by nothing: §5 registers it as "an
interpretation and power quantity, not part of the decision rule".

**S5 — the E1 gold control — DONE as the per-run endpoint.** `score_run()`
evaluates every gold row against the admitted policy artifact in both languages
and `e1_control()` publishes the rate, the registered 0.60 floor and whether it
held. The floor gate itself — that BOTH REFERENCES reproduce every gold row at
attempt time — was owed as **S10** and is **LANDED**.

**S6 — E5, the census — LANDED.** Study 012's
`harness/census.py` now has the sixth `PORTS.md` row, and the machinery
(`cover_greedily`, the renderers, the distinct-whole-run grouping) is carried
verbatim with the enumerated change list in that row. The stimulus was the open half, and §5 now
registers one: "Registered census stimulus: the gold-row input set (the gold
inputs; disagreement profiles are computed over exactly these cells, closing the
§9 joint-reading concern about unstated stimuli)".
`census.registered_stimulus(rows, digest)` reads it from the frozen gold suite
as IDS AND ORDER ONLY — no gold expectation reaches a census number, because the
census is not scored against an oracle — and refuses `E5-STIMULUS-EMPTY` or
`E5-STIMULUS-DUPLICATE-CELLS` on a suite that is not a stimulus. §9 is
unchanged and still governs: E4's stimulus is the mutant set against each run's
own authored suite, and `STIMULUS_LABEL` plus the no-tradeoff note travel inside
every record so a reader of one table cannot lose which grid it is over. The
vectors `harness/score.py` hands it are the SAME evaluation E1 makes over the
same cells, computed once in one pass, so the two endpoints cannot disagree
about what a run answered. The smoke censused all three arms.

**S7 — the FM interval ENDPOINTS — LANDED.** `stats.excludes_zero()` computes
Reading 1 — the Δ₀ = 0 inversion — exactly, and that is still the whole of what
§5's decision reads. `stats.interval_endpoints()` now sweeps Δ₀ with the same
construction and reports the acceptance set's convex hull, so §10's commitment
to publish every interval is met. Two things are REGISTERED so the sweep is
exactly reproducible rather than approximately right, and both are stated in the
record the scorer publishes:

* **the Δ₀ mesh**, `FM_DELTA_MESH_DEN = 100`. Every attainable per-arm rate
  difference at N = 50 is a multiple of 1/50 and therefore a mesh point, and
  `MESH_DEN = 1000` is a multiple of 100, so `p_C` and `p_A = p_C + Δ₀` are both
  points of the registered NUISANCE mesh and the whole supremum stays exact
  integer arithmetic. The reported endpoints are mesh points: the interval is the
  hull of the ACCEPTED MESH POINTS, an inner approximation refined to 1/100, and
  `interval_endpoints()["construction"]` says so.
* **the constrained-MLE bisection**, `FM_MLE_BISECTIONS = 48`. The restricted
  log-likelihood is concave, so its derivative's numerator — an integer cubic
  built by polynomial multiplication rather than a transcribed expansion —
  changes sign at most once, and the MLE is located by a FIXED number of
  halvings with the sign taken in exact integer arithmetic. Study 012 registered
  the same discipline for the Clopper–Pearson bisection, for the same reason: no
  libm, no tolerance, no seed, the same bits on any platform. Farrington and
  Manning's trigonometric closed form is deliberately not used — it needs
  `cos`/`acos`, and a libm call in the ordering of tables is what this program's
  arithmetic discipline forbids.

`fm_z2()` at Δ₀ = 0 returns `z2_table()`'s own cell arithmetic, so the reported
interval and the registered decision are one construction and cannot disagree at
the Δ₀ they share; `tests/test_score_stats.py` asserts it. The smoke published
`[-13/25, 63/100]`.

**S8 — the general unequal-N inversion — LANDED.** The choice was a
registration decision and §5 made it: "Because apparatus exclusions can leave
unequal per-arm denominators, the registered construction is the general
unequal-N FM-score inversion (the OC table's equal-N closed form is its
N_A = N_C slice)". The alternative — truncating both arms to a common
denominator — throws away runs and is NOT registered.

`z2_table()`, `tail_coefficients()`, `sup_tail_numerator()`, `sup_le_alpha()`,
`critical_level()`, `critical_level_at()` and `excludes_zero()` all take two arm
sizes, `n_right` defaulting to `n_left`. At Δ₀ = 0 the constrained MLE is the
pooled proportion in closed form whatever the arm sizes are, so the general
statistic is the exact rational `N (x·n_C − y·n_A)² / (n_A·n_C·(x+y)·(N−x−y))`
and both arms still share ONE nuisance rate — which is why the tail is still one
Bernstein polynomial and the half-mesh scan is still sound (the tail is symmetric
under (x,y) → (n_A−x, n_C−y); the suite asserts the palindrome at UNEQUAL sizes
rather than inheriting it). The zero-exclusion predicate becomes `z² > 0` rather
than `x != y`: the same set at equal arm sizes, the correct one at unequal ones,
where two equal counts are two different rates.

The acceptance test is the one that makes it safe to register: at
N_A = N_C = 30, 50 and 100 the general form reproduces `OC-TABLE.md`'s published
c* and realised size **exactly, as the same rationals** — 30/7, 625/154, 175/44 —
not to the four decimals the document printed. `score.contrast()`'s
`FM-UNEQUAL-N` refusal is gone; the smoke as recorded scored A−C at 3 versus 4 (an
archived second-pass number; see the V2 note above).

**S9 — the engine-supplied-kill list — LANDED, then RE-MEASURED.** §4 registered 35,
then 41, and the dense census over the full derived space (round-1 R1-11) makes the
current number **27** — the 41 was gold-witness-scoped and wrong by fourteen. The count
below is read from the manifests by `tests/test_prereg_currency.py`, not from this file.
What §4 registers is arm-A
mutants "listed in the registries" whose kills are achievable only through the
engine's structural conflict detection, "reported both included and excluded".
The marking lived only as a `⚠conflict-only` glyph in
`design/mutants/ADEQUACY.md`'s prose table; both manifests carry it as a
machine-readable member now.

* `design/mutants/refA/MANIFEST.json` — every mutant carries
  `engineSuppliedKill`, true for exactly the ids the dense census confirms (27 at this
  revision; `design/mutants/refA/REGISTRY.json`'s `conflictOnlyMutants` was the
  superseded gold-witness-scoped list). The class is MEASURED, never re-derived from
  prose, and the currency suite recomputes the count from the manifest.
* `design/mutants/refB/MANIFEST.json` — the registry carries no Rego analog, and
  that is recorded EXPLICITLY rather than left as silence: every mutant carries
  `engineSuppliedKill: false` and a top-level `engineSuppliedKillClass` states
  that arm B's engine-supplied class is EMPTY, with its reason (the Rego ladder
  has no structural conflict detection, which is the same asymmetry
  `refA/REGISTRY.json`'s `conflictNote` states from the other side).

An EMPTY registered class and a MISSING member are different facts and the code
keeps them apart: `e4.engine_supplied_ids()` returns `[]` for the first and still
raises `E4-ENGINE-SUPPLIED-UNREGISTERED` for the second. `e4.kill_rates()` splits
the paired subset once, where each mutant's kill is known, and
`score.engine_supplied_block()` publishes both columns per arm with a reduced
integer cut marked descriptive — the DECISION reads the included column, because
§5 registers the endpoint over the paired adequate subset entire.

**S10 — the reference-vs-gold floor gate — LANDED, and it RUNS.** It was wired
as control gate `references-reproduce-gold` with `held: false` and the code
`GATE-FLOOR-NOT-RUN`, failing closed rather than passing quietly.
`score.references_reproduce_gold()` is `design/gold/check_gold.py`'s clause (5)
executed at attempt time, through the same two invocations every other number in
an attempt is produced by (`engines.eval_pack()` and `engines.eval_rego()` carry
that file's flags verbatim — `harness/PORTS.md` records it as one of the three
sources of `e4lib/engines.py`), and `held` is true only when both references
reproduced every gold row. The gate is shown to have POWER as well as to pass:
`tests/test_score_pipeline.py` drives it against a real Rego mutant standing in
for the arm-B reference and requires `held: false` with the failing rows and the
reference named. The smoke as recorded ran 105 rows, 0 failures, `held: true`; gold has
since grown to 117 rows and the gate reads whatever the committed suite carries.

**S11 — the scorer and the driver held two readings of a slot — LANDED.** The
scorer was assembled while `harness/batch.py` was still the schedule core, so
`score.read_slot()` reads a slot with its own reduced rule: `REFUSAL.json` or
`CALL.json`, the wrapper's exit status through `batch.WRAPPER_EXIT_MEANINGS`,
and `completion.txt`. The driver has since landed D1–D8, and with them
`batch.collect_slots()`, `batch.slot_outcome()`, `batch.verify_seal_of()`,
`batch.session_identity()` and `batch.C7_OUTCOMES` — which are richer and are
the driver's own authority on what a slot is. `SHORTFALL_FILE` is already bound
to `batch.SHORTFALL_NAME` rather than spelled twice, but the rest is not
reconciled, and two of the consequences are concrete rather than stylistic:

* **the seal is not verified.** §2.9 seals every slot by a terminal manifest;
  `score.read_slot()` never calls `verify_seal_of()`, so a slot whose bytes
  moved after sealing is currently scored rather than refused.
* **the C7 golden-context outcome is not read.** `golden-context-mismatch` is
  an apparatus code in `CODE_PARTITION` and `read_slot()` can never return it,
  so a run that failed the golden gate would enter the denominator.

**The remedy, in all three parts, has landed.**

1. **`read_slot()` reduces to the driver's readers.** Presence comes from
   `batch.collect_slots()` through `score.slots_present()` — so an entry named
   `run-NNN` claims its index whatever its type, and an entry the registered
   order does not name refuses by name rather than being ignored; the seal comes
   from `batch.verify_seal_of()`, so a slot whose bytes moved after sealing takes
   the whole scoring to decision row 1 (demonstrated on the smoke's own bytes
   with one appended character); the outcome comes from `batch.slot_outcome()`,
   which validates the refusal code against `WRAPPER_CODES` and is why a
   `call-timeout` can no longer become a `slot-shape`; the session id comes from
   `batch.session_identity()`, and `score.require_distinct_sessions()` refuses a
   population in which two slots name one call. `golden-context-mismatch` is
   REACHABLE: the wrapper stamps the capture it ran behind into every
   `CALL.json` (§3.2) and the scorer compares that stamp with the registry's
   `golden.sha256`. §6 C7's registered outcome set is read from
   `batch.C7_OUTCOMES` and the control record's shape from
   `batch.c7_record_shape_problems()` — the one function both gates read — so
   `golden_context_gate()` requires the capture pinned, the assent recorded, and
   the negative control on record with outcome `refused`, which is the only
   outcome that shows the allowlist has power.
2. **The population is the declared PREFIX.** `population()` counts the arm's
   slots that are PRESENT and publishes `registered`, `absent` and `attempted`
   beside the denominator, so the prefix is a published fact rather than a
   subtraction.
3. **`e2_profile()` reads the RUN records.** It refuses an apparatus code on a
   run record — the population rule failing to exclude one is a refusal, not an
   E2 row — and publishes `artifactAdmitted` beside `admitted`.

`tests/test_score_attempt.py`'s slot cases have moved onto the DRIVER's
fixtures: `DriverBuiltSlots` extends `tests/test_batch.py`'s `StandInStudy` and
builds every slot through `batch.stamp_slot()`, `batch.refuse_slot()` and
`batch.seal_slot()`, because a slot the scorer reads has to be a slot the driver
could have written — hand-rolled dictionaries were what let the two readings
diverge in the first place.

## G — the golden context and the isolation controls

**G1 — the golden-context capture.** Port Study 012 `harness/batch.py`
`capture_slots()` (1832–1856), `capture_identity()` (1857–1874),
`require_distinct_sessions()` (1875–1898), `capture_golden()` (1899–2013),
`next_attempt()` (2014–2029), `run_capture()` (2030–2078), plus
`golden_path_for()` (871–878) and `require_golden()` (879–910). With them come
`transcription/PROBE-PROMPT.txt` and the captured
`transcription/GOLDEN-CONTEXT.json`, and the `probePrompt` and `golden` pins.
Two agreeing captures from two distinct calls is the floor, and the identity
members (`sessionSha256`, `sessionId`, `callIdentity`) are what make "two
calls" mean two calls.

**G2 — the isolation negative control.** Port `capture_isolation_negative()`
(2079–2235) and `require_isolation_negative()` (911–987), with the
`isolationNegative.assent` member — the name the registry uses — and the
redaction list `C7_REDACTED`. The control is a precondition of the **batch**,
not of its own command: Study 012's round 9 found all 150 calls reachable with
the assent still null.

**G3 — `LEAK_TOKENS`, re-derived — LANDED.** `harness/leak_tokens.py` derives
the policy vocabulary from the stimulus slice the source marks off for itself by
three registered rules, publishes every drop with its reason, and demonstrates
power (`check_power()`, `check_rederivation()`, `check_negative_corpus()`). The
RESIDUAL — that `harness/transcript_check.py` still carried its own design-time
tuple, so the study screened transcripts with one list and scratch paths with
another — is closed: `transcript_check.LEAK_TOKENS` **is**
`leak_tokens.SCREEN_TOKENS`, the same object the wrapper reads under its other
name `leak_tokens.SCRATCH_TOKENS`. The screen is the union of the derived policy
half and `leak_tokens.INSTRUMENT_TOKENS`, which is named as design-time on
purpose — the stimulus by construction says nothing about jpack, the
preregistration or the mutant machinery — and is separately power-checked by the
new `check_instrument_power()`: the instrument half ALONE must catch strictly
fewer stimulus witnesses than the derived half, and the union must lose none, so
the screen's policy power provably comes from the prose. `design_time_gap()`
stops being a to-do list and becomes a standing assertion (nothing derived is
missing from the screen; everything extra is exactly the instrument list), which
`tests/test_leak_tokens.py` holds. The freeze's re-derivation against
`policy/POLICY.md` now moves BOTH screens at once.

## D — the driver's calling half (deferred from `harness/batch.py`)

Every item is a Study 012 `harness/batch.py` line range, to be ported by
copy-and-edit with a `PORTS.md` change list. The destination digest of
`harness/batch.py` moves when they land, and `PINS.json`'s `ownPorts` moves
with `PORTS.md`.

| id | piece | 012 lines |
|---|---|---|
| D1 | `check_registry()` and `verify_ported_bytes()` | 638–741 |
| D2 | `preflight()` and `require_freeze()` | 742–870 |
| D3 | `invoke()`, `stamp_slot()`, `refuse_slot()` | 988–1124 |
| D4 | slot files, `files_digest()`, `seal_slot()` | 1125–1284 |
| D5 | ledger records, chain, prefix, `write_ledger()` | 1285–1488 |
| D6 | `verify_seal_of()`, `slot_outcome()`, `slots_on_disk()`, `reconcile_ledger()` | 1489–1719 |
| D7 | `run_batch()` | 1720–1831 |
| D8 | shortfall: `completed_rounds()`, `last_slot_clock()`, `declare_shortfall()`, the `main()` argument surface | 2236–2507 |

Two edits are already known to be owed inside these ranges, and are recorded
now so the port does not have to rediscover them:

* the atomic-write temporary is a **registered constant path**
  (`arms/BATCH.json.partial` in 012) and must be named in `PINS.json`'s freeze
  exclusion list, because a `mkstemp` name cannot be an exclusion entry;
* the wrapper's exit statuses now include **12**, so every place 012 mapped
  10/11 to a code needs the third branch — `batch.WRAPPER_EXIT_MEANINGS` is the
  single table to read it from.

## T — tests and tree hygiene owed

**T1 — the wrapper's own suite.** Study 012's `tests/test_batch.py` drives the
real wrapper against a stand-in study (`fixtures.standin_study()`: the
committed wrapper reached through a symlink, a symlinked harness, a `git init`
so the worktree checks see production's shape) and a stand-in CLI. Port the
fixtures and the wrapper cases; the four registered differences each need one:
the arm-keyed prompt-digest refusal, **the timeout ceiling firing and producing
exit 12 with `timedOut: true` in `CALL.json`**, the null-model refusal, and the
`harness/` location leaving every path guard intact. The middle two were
smoke-tested by hand while the port was made — a stand-in study, a stand-in CLI
and a 2 s ceiling produced exit 12 with the ceiling and the grace stamped, and a
nulled `codex.model` refused before anything was called — which is evidence and
not a suite: nothing in the repository re-runs it.

**T2 — `transcript_check` cases — COVERED.** None of the check logic's own;
012's suite covers that and this port changes none of it. What is new here is the
token list, and `tests/test_leak_tokens.py` (30 cases) holds it: the derivation,
the admissibility drops, both power demonstrations, the negative corpus, and —
since G3's residual landed — that `transcript_check.LEAK_TOKENS` IS
`leak_tokens.SCREEN_TOKENS` and no second tuple survives in that file.

**T3 — the tree must be clean before `integrity.verify()` can pass. LANDED.**
`verify_bytecode()` scans the WHOLE study tree and refuses (a) any untracked
`.py` source and (b) any `.pyc` that the running interpreter did not produce
from the source beside it. `design/` used to hold several untracked Python
sources (`design/mutants/adequacy_search.py`, `design/mutants/oc_table.py`,
`design/reference/cert_offgold.py`, `design/reference/refA/*.py`) and several
`__pycache__` trees from a 3.8 interpreter. All of them are committed, every
`__pycache__` is gone, and `harness/integrity.py` passes under the pinned
CPython 3.12.11 with `PYTHONSAFEPATH=1` — which is what
`_refuse_unsafe_import_path()` requires and what the CI job below exports.
Keep running the harness that way; the item is closed, not the requirement.

**T4 — pytest writes bytecode.** Run the suite with `PYTHONDONTWRITEBYTECODE=1`
(or `-p no:cacheprovider`), or T3's refusal returns after every test run.

## C — CI — LANDED

`study-019-harness` is in `.github/workflows/ci.yml`, after `study-018-harness`
and before the general `python` matrix, in the file's own idiom: pinned action
SHAs copied from the sibling study jobs (`actions/checkout@3d3c42e5…`,
`actions/setup-python@5fda3b95…`), a fixed CI runtime named to the patch —
`python-version: "3.12.11"` rather than `"3.12"` — which makes this job
reproducible and refuses nothing. The registry registers the CPython **3.12
series** and `verify_interpreter()` compares implementation and series only; the
running patch level is reported and not required (Study 012's round 3, finding
20), and the sentence this paragraph used to carry — that the registry records
the patch and the scorer refuses anything else — was false when it was written
and is round-6 finding **R6-4**. The job pip-installs only pytest
(the harness, the design generators and the controls are stdlib-only), and runs
with `working-directory: studies/019-authorship-across-representations`:

```
      - run: python harness/integrity.py     # the port chain and the manifest
      - run: python -m pytest harness/tests -q
```

`integrity.py` runs with `PYTHONSAFEPATH: "1"` (it refuses without it) and both
steps with `PYTHONDONTWRITEBYTECODE: "1"` (T4 — a test run that writes bytecode
would break the integrity step on the next run).

**The batch never runs in CI** (§7), and neither does anything that invokes
`codex`, `jpack` or `opa`: the CI job runs the deterministic controls only, and
the matrix adjudication is an ATTEMPT, not a test. `tests/test_score_pipeline.py`
skips itself there by design, because the pinned binaries are absent and it
refuses to run against unpinned ones. The job was added only after T3, whose
untracked design sources would have failed the integrity step.
`harness/tests/test_prereg_currency.py` asserts the job exists and keeps its
shape, so deleting this scaffold at freeze does not take the requirement with
it.

## F — the freeze-fill procedure, in order

Each step fills exactly one link, and every link is checkable before the next.

0. **Close M1** — **DONE** (V1). The registry, the registered port set and the
   manifest glob have caught up; `verify_chain()` passes over all seven rows and
   the exact-set manifest describes its tree, so every digest below now means
   something.
0b. **Close S11** — **DONE** (V4). The scorer's population rule was here, ahead
   of the gates, because V3 established that it changes every published
   denominator and two control gates: no number produced before it was closed
   described the batch it was computed from.
1. **Close the pre-freeze gates** the preregistration marks `GATE(pre-freeze)`:
   the mutant adequacy gate, the off-gold equivalence certificate, the
   clean-room re-run against the frozen prose, and the OC table for
   (τ, δ, N = 50). This file's S and G items are **DONE** (V4) — S6 the
   registered census stimulus, S7 the Δ₀ sweep, S8 the general unequal-N
   inversion, S9 the `engineSuppliedKill` manifest member, S10 the floor gate
   actually running, G3's residual the single leak list — and the scorer
   publishes no refusal on the smoke batch. **T3 and section C are also DONE**
   (round-4 finding R4-6): the design sources are committed, no `__pycache__`
   survives, `integrity.py` passes under the pinned 3.12.11, and the
   `study-019-harness` CI job is in the workflow. What remains under this step
   is the gate work itself, not the tree.
2. **Land the registered documents AND the registered payload SETS**:
   `policy/POLICY.md` (the frozen copy of the design draft), `gold/GOLD.json`,
   `mutants/MANIFEST-*.json`, `reference/REFERENCE-*.md`,
   `reference/refA/pack.json`, `reference/refB/policy.rego`,
   `controls/off-gold-equivalence.json`, `arms/<ARM>/PROMPT.txt` — and the two
   payload trees the MANIFESTs point at, **`mutants/jps/*.json` and
   `mutants/rego/*.rego`**, whose files each carry a per-file hash.
   `make_manifest.py --freeze` refuses while any registered document **or any
   registered payload set** is still pending, so this step is checkable rather
   than remembered. Round-5 finding **R5-6** is why the sets are named here: the
   gate walked the documents only, so a freeze over a tree with both payload
   roots absent returned success and wrote a manifest with zero mutant payload
   entries — the scorer refuses that tree, but only at attempt time, which is
   after the anchor it was supposed to gate.
2b. **Land the pre-freeze obligations other documents declare** — round-7
   finding **R7-9**. Three artifacts were required before the freeze by documents
   in this tree and were named by no pin, no registered-document entry and no
   step here, so the ceremony could complete without any of them:
   - **`CORRECTION-TARGETS.md`** — §10 of the preregistration pins the
     `CORRECTION.md` targets (verbatim wording, venue, URL and retrieval date)
     before the freeze. One target per claim this study may have to correct, each
     with all four fields.
   - **`verification/V7-COMPLETENESS.md`** — `design/POLICY-DRAFT.md`'s V7: the
     completeness argument re-derived mechanically over the gold grid, asserting
     exactly one governing clause per cell under the earliest-clause tie-break,
     with the former X1 region asserted **covered** rather than excluded.
   - **`verification/V8-ASYMMETRY-LEDGER.md`** — the same document's V8: the
     asymmetry ledger re-derived from the two reference implementations, with its
     final balance stated.

   All three are `REGISTERED_DOCUMENTS` in `harness/make_manifest.py`, so
   `--check` names each while it is absent and `--freeze` refuses. Withdrawing
   one is a decision that deletes the obligation from the document declaring it,
   in the same commit — not a quiet omission from the registered set.
3. **Assemble the arm prompts deterministically** and fill
   `arms.<ARM>.promptSha256` (the `matrixA/B/C` freeze pins) and
   `promptBytes`. The wrapper's prompt-digest gate reads exactly these members.
4. **Capture the golden context** (G1) and fill `probePrompt.sha256` and
   `golden.sha256`; run the isolation negative control (G2) under recorded
   assent and fill `isolationNegative.assent`.
5. **Fill the artifact pins**: `policyProse`, `goldSuite`, `mutantManifests`,
   `references.A/B`, `offGoldCertificate`, and the toolchain members that are
   still null (`opa.capabilitiesSha256`, `jpack.reproducibleBuildAttestation`,
   `codex.model`).
5b. **Validate and pin the SEALED REVIEWER SET** — round-7 finding **R7-8**, and
   it is a real gate gap rather than a wording one. `reviewerMutantSet.sha256` is
   one of the eighteen pins `integrity.study_label()` requires for `REGISTERED`;
   it is null; and every step above filled a different pin and then this list
   claimed the label. The step, in order:
   1. run the non-executing loader over the set —
      `e4lib/reviewer.py`'s `load(root)` — which validates
      `reviewerSetVersion`, the registered manifest members, the cardinality,
      every record's members and every payload's own digest, and executes
      nothing;
   2. take the digest of the sealed manifest:
      `sha256(controls/reviewer-mutants/MANIFEST.json)`, which
      `harness/make_manifest.py` prints as a pending pin with exactly that
      source, and `harness/integrity.py` names in `PIN_SOURCES`;
   3. write it to `reviewerMutantSet.sha256` in `harness/PINS.json`.

   `make_manifest.py --check` reports the pin while it is null or disagrees with
   the manifest on disk, and `--freeze` refuses on it, so the ceremony cannot
   complete without this step. The set's payload closure — every file the sealed
   manifest names present, no unnamed file beside it, and the study manifest
   covering exactly that set — is checked with the two mutant corpora's.
6. **Regenerate `harness/PORTS.md`'s destination digests** for every file the
   remaining ports touched, then re-pin `ownPorts.sha256`. `PORTS.md` before
   `PINS.json`, always: the registry pins the ports table and never the reverse.
7. **Run `make_manifest.py --freeze`**, then fill `studyManifest.sha256` with
   the manifest's digest. The manifest covers neither itself nor `PINS.json`
   (linear anchor), so this is one pass.
8. **Fill `preregistration.sha256`** with the digest of the reviewed
   `PREREGISTRATION.md`, last of the freeze pins — after it,
   `integrity.study_label()` returns `REGISTERED` and
   `unfilled_pins()` is empty. Verify with `harness/integrity.py`: any null pin
   still prints the PILOT label and names the pin.
9. **Open the freeze PR.** The freeze commit is its squash-merge commit on
   `main`; record it in `freeze.commit` in the first post-freeze commit, which
   is also when this file is deleted.

Order note, learned from Study 014's round 2 and carried in the registry's own
`anchorOrder`: the manifest must be regenerated **before** the registry is
pinned, and the registry must never be covered by the manifest. Any other
order needs a SHA-256 fixed point.
