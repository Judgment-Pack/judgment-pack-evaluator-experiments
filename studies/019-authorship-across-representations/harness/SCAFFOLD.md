# Scaffold — what this harness is, and precisely what remains

This file is the honest half of the port. `harness/PORTS.md` says what was
taken and what changed; this says what has **not** been built, by name, with
the source it comes from and the order the remaining work has to happen in.
It is deliberately **outside** the study manifest (`harness/make_manifest.py`
covers `harness/*.py`, `harness/*.sh` and the registered documents, not this
file): it is a work record that will be appended to and then deleted at the
freeze, and ADR 0004's argument about appendable files applies to it exactly.

**Superseded by V1/V2 below: the harness can now run a batch end to end, and
has.** The wrapper, the schedule, the driver's calling half, the isolation
controls and the scorer all exist and are tested, and a twelve-slot PILOT smoke
has been driven through all of them against the real pinned engines with the
authoring CLI stood in (`harness/tests/E2E-SMOKE.md`). What that smoke found is
V3: three structural defects in the scorer's population rule, none of them
fixed. The state today, said plainly: every freeze pin in `harness/PINS.json` is
null, `integrity.study_label()` returns `PILOT`, and **no authoring call has
been made** — no model has been asked anything by this study.

## What exists and is tested

| file | state | tests |
|---|---|---|
| `harness/authoring_call.sh` | complete port, five registered differences | `tests/test_batch.py` (T1 landed) |
| `harness/batch.py` | schedule core, timeout constants, §1a code partition, and the whole calling half (D1–D8, G1–G2) | `tests/test_schedule.py` (13), `tests/test_partition.py` (6), `tests/test_batch.py` |
| `harness/integrity.py` | partial: chain, interpreter, unreviewed-bytes gate, label rule, manifest check | `tests/test_pins.py` (8) |
| `harness/transcript_check.py` | complete port; `LEAK_TOKENS` is design-time | none yet — **T2** below |
| `harness/make_manifest.py` | complete port, ADR 0004 applied | `tests/test_manifest.py` (8) |
| `harness/score.py` | **assembled** — the single publisher: attempt record, terminality, population rule, E1/E2/E3/E4, the decision table | `tests/test_score_attempt.py` (43) |
| `harness/e4lib/stats.py` | ported by digest: Clopper–Pearson + the FM contrast (Reading 1) | `tests/test_score_stats.py` (22) |
| `harness/e4lib/extract.py` | assembled: the registered marker rule | `tests/test_score_extract.py` (12) |
| `harness/e4lib/admit.py` | assembled: §1a's SIX authoring codes, arm-structural enforced | `tests/test_score_admit.py` (22) |
| `harness/e4lib/engines.py` | assembled: two-engine layer, binaries fail-closed, capabilities canary | `tests/test_score_engines.py` (15) |
| `harness/e4lib/e4.py` | assembled: X1 filter, pairing, identity, kill, the τ cut | `tests/test_score_e4.py` (31) |
| `harness/e4lib/census.py` | ported: 012's census machinery; stimulus refuses | `tests/test_score_census.py` (15) |
| `harness/e4lib/decision.py` | assembled from the 015–018 shape as an ordered table | `tests/test_score_decision.py` (19) |
| — | the assembled pipeline against the REAL pinned engines | `tests/test_score_pipeline.py` (10, skipped without the pins) |
| `harness/PINS.json` | every freeze pin null; toolchain blocks resolved and marked; `ownPorts` re-pinned (V1) | `tests/test_pins.py` (8) |
| `harness/PORTS.md` | **seven** rows, two-sided, machine-read, plus the assembled-module lineage table | `tests/test_ports_chain.py` (7), `integrity.verify_chain()` |
| — | the whole harness end to end, no codex call, real engines | `tests/E2E-SMOKE.md` (transcript, not a suite) |

The scorer's own ten modules contribute 195 passing tests under CPython
3.12.11 — 185 deterministic, plus the 10 in `tests/test_score_pipeline.py`,
which run against the real pinned `jpack` and `opa` when
`JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` hash to the pins and SKIP by name otherwise
(§7: the engines are never invoked in CI). `tests/test_partition.py`'s last
test, written skipping since the scaffold, is a live assertion now.

**Superseded by V1.** `tests/test_manifest.py`'s exact-set assertion PASSES
(`PREREGISTRATION.md`'s move and the missing `harness/e4lib/` glob were the two
reasons it failed, and M1 item 4 closed both), `integrity.verify_chain()` PASSES
over all seven rows, and `verify_interpreter()`, `study_label()` and
`unfilled_pins()` pass against the committed tree. `integrity.verify()` as a
whole still refuses — for **T3** alone now. The whole suite is **353 passing**
under CPython 3.12.11, and the ten `tests/test_score_pipeline.py` cases RUN
rather than skip when `JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` are the pinned binaries.

What the pipeline suite established against the pinned binaries, so that it is
written down rather than remembered: the reference pack admits through the real
`jpack spec validate`; all 105 gold rows reproduce in BOTH languages; the arm-A
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

**V2 — the end-to-end smoke ran green through the apparatus.** Twelve slots
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

**V3 — three STRUCTURAL defects in `harness/score.py`, none of them fixed.**
Each changes what a published population is, so each is a review decision and not
an integration repair. `E2E-SMOKE.md` section 8 has the evidence.

* **V3a — absent slots enter every population as admitted runs.**
  `population()` partitions on `slot["code"]` and never on `slot["present"]`; an
  absent slot has `code: None`, which is not an apparatus code, so all 138 absent
  slots entered their arms' denominators and `score_run()` gave each one
  `no-marker-block` from a `None` completion. Observed denominators 49/50/50 over
  a twelve-slot batch. `terminality()` computes `present` correctly and nothing
  downstream reads it. §2.8 scores a declared short batch over the PREFIX.
* **V3b — a timeout is scored as `slot-shape`.** `read_slot()` tests for
  `REFUSAL.json` before it reads `CALL.json` and returns `slot-shape` for any
  slot carrying one. The driver classified the slot `call-timeout`, `CALL.json`
  carries `timedOut: true`, and the scorer disagreed. Both codes are apparatus so
  no denominator moves — but `timeouts` counted 0 and the control gate
  `timeout-rate-within-cap` held over a batch that contained a timeout, which is
  the undercount `PORTS.md`'s registered difference (2) says status 12 exists to
  prevent.
* **V3c — the E2 table cannot report a single authoring code.** `e2_profile()`
  counts `slot["code"]`, which `read_slot()` populates from the wrapper's exit
  status, and every code the wrapper can produce is on the apparatus side; the
  authoring codes are assigned later onto the RUN record. So the six-code table
  §5 makes a headline is structurally always zero, and `admitted` counts clean
  exits rather than admitted artifacts. Demonstrated on a real slot whose
  completion genuinely carried no marker.

All three are S11's gap with consequences attached, and S11's remedy — reduce
`read_slot()` to the driver's own readers (`collect_slots()`, `slot_outcome()`,
`verify_seal_of()`, `session_identity()`, `C7_OUTCOMES`) and move the population
onto the prefix — is what closes them. **S11 is now blocking rather than
tidying**, and is promoted into step 1 of the freeze-fill procedure below.

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
held. **Still owed:** the floor gate itself — that BOTH REFERENCES reproduce
every gold row at attempt time — is registered as control gate
`references-reproduce-gold` and is currently stamped `held: true` with a note.
It must actually run `design/gold/check_gold.py`'s floor gate against the frozen
`gold/GOLD.json` and the two frozen references before the freeze; a gate that
reports its own success is not a gate. Tracked as **S10**.

**S6 — E5, the census — PORTED, and its STIMULUS REFUSES.** Study 012's
`harness/census.py` now has the sixth `PORTS.md` row, and the machinery
(`cover_greedily`, the renderers, the distinct-whole-run grouping) is carried
verbatim with the enumerated change list in that row. What is NOT available is
the stimulus: §9 states that "the census's expressiveness rows and these rates
live on different stimuli: no tradeoff statement combining them is licensed", so
the census grid is registered to be something other than the gold grid and no
such grid is registered yet. `census.registered_stimulus()` raises
`E5-STIMULUS-UNREGISTERED`; `harness/score.py` publishes that refusal in its R2
section rather than running the census on the nearest grid to hand, which would
manufacture exactly the statement §9 forbids. **Owed before the freeze: register
and pin a census stimulus.**

**S7 — the FM interval ENDPOINTS are not ported.** `stats.excludes_zero()`
computes Reading 1 — the Δ₀ = 0 inversion — exactly, and that is the whole of
what §5's decision reads. Reporting the interval's endpoints needs the same
inversion swept over Δ₀ with the Farrington–Manning constrained MLEs at each Δ₀
and the convex hull taken where the acceptance set is non-convex, none of which
is in `design/mutants/oc_table.py`. `stats.interval_endpoints()` raises
`FM-ENDPOINTS-UNPORTED`. §10 commits to publishing every interval, so this is
owed before the freeze.

**S8 — the contrast has no unequal-N inversion.** `stats.z2_table()`'s closed
form is the equal-arm-size one, which is what §2's N = 50 per arm registers —
but §1a excludes apparatus failures from the denominator, so unequal admitted
counts are a real possibility. `score.contrast()` REFUSES with `FM-UNEQUAL-N`
rather than approximating. Two ways to close it, and the choice is a
registration decision rather than a coding one: register the unequal-N FM
inversion, or register a rule that truncates both arms to a common denominator
(which throws away runs and needs its own justification). Neither is registered
today.

**S9 — the engine-supplied-kill list is not in the registries.** §4 registers 35
(now 41) arm-A mutants "listed in the registries" whose kills are achievable
only through the engine's structural conflict detection, "reported both included
and excluded". The marking exists only as a `⚠conflict-only` glyph in
`design/mutants/ADEQUACY.md`'s prose table; neither `refA/MANIFEST.json` nor
`refB/MANIFEST.json` carries a machine-readable member.
`e4.engine_supplied_ids()` reads an `engineSuppliedKill` member and raises
`E4-ENGINE-SUPPLIED-UNREGISTERED` when no mutant carries one — returning an
empty list would publish "0 engine-supplied kills" and satisfy §4 in form only.
**Owed before the freeze: the manifests grow the member.**

**S10 — the reference-vs-gold floor gate does not run yet.** See S5. It is
wired as control gate `references-reproduce-gold` with `held: false` and the
code `GATE-FLOOR-NOT-RUN`, so a complete batch lands on §5's row 2 until the
gate actually runs — a gate that reported its own success would be the failure
§6 exists to prevent, so it fails closed rather than passing quietly.

**S11 — the scorer and the landed driver hold two readings of a slot.** The
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

Both are refusals the partition already names and the scorer cannot yet reach.
Owed before the freeze: `score.read_slot()` reduces to the driver's readers,
and `tests/test_score_attempt.py`'s slot cases move onto the driver's fixtures.

**Updated by the verification pass (V3): this item is BLOCKING, not tidying.**
The end-to-end smoke reached all three consequences for real — an absent slot
scored as an admitted no-marker run (V3a), a real timeout filed as `slot-shape`
with the timeout control gate holding vacuously over it (V3b), and an E2 table
that cannot report any authoring code at all (V3c). The remedy is unchanged and
now has a third part: `read_slot()` reduces to the driver's readers, the
population is taken over the declared PREFIX rather than over the registered
order, and `e2_profile()` reads the RUN records that carry the authoring codes
rather than the slot records that cannot.

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

**G3 — `LEAK_TOKENS`, re-derived** (`GATE(pre-freeze)`). The list in
`harness/transcript_check.py` is design-time. It must be derived from the
frozen policy prose and the naming appendix, committed with a checker that
shows it has power on mutated inputs — the same standard §3 already applies to
the sufficiency and policy-content checkers — and the derivation itself
committed so the list is reproducible rather than curated.

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

**T2 — `transcript_check` cases.** None of this study's own; 012's suite covers
the check logic, and what is new here is the token list (G3) and the three-arm
label.

**T3 — the tree must be clean before `integrity.verify()` can pass.**
`verify_bytecode()` scans the WHOLE study tree and refuses (a) any untracked
`.py` source and (b) any `.pyc` that the running interpreter did not produce
from the source beside it. Today `design/` holds several untracked Python
sources (`design/mutants/adequacy_search.py`, `design/mutants/oc_table.py`,
`design/reference/cert_offgold.py`, `design/reference/refA/*.py`) and several
`__pycache__` trees from a 3.8 interpreter. **Commit the design sources and
delete every `__pycache__`** — and run the harness under the pinned 3.12 with
`PYTHONSAFEPATH=1`, which is also what `_refuse_unsafe_import_path()` requires.

**T4 — pytest writes bytecode.** Run the suite with `PYTHONDONTWRITEBYTECODE=1`
(or `-p no:cacheprovider`), or T3's refusal returns after every test run.

## C — CI

Add one job to `.github/workflows/ci.yml`, modelled on `study-012-harness`
(the file's own idiom: pinned action SHAs, `python-version: "3.12"`, pip-install
pytest, `working-directory: studies/019-authorship-across-representations`):

```
  study-019-harness:
    name: Study 019 · deterministic harness
    ...
      - run: python harness/integrity.py     # the port chain and the manifest
      - run: python -m pytest harness/tests -q
```

**The batch never runs in CI** (§7), and neither does anything that invokes
`codex`, `jpack` or `opa`: the CI job runs the deterministic controls only. Do
not add the job until T3 is done, or the integrity step fails on the untracked
design sources.

## F — the freeze-fill procedure, in order

Each step fills exactly one link, and every link is checkable before the next.

0. **Close M1** — **DONE** (V1). The registry, the registered port set and the
   manifest glob have caught up; `verify_chain()` passes over all seven rows and
   the exact-set manifest describes its tree, so every digest below now means
   something.
0b. **Close S11** — the scorer's population rule. It is here, ahead of the
   gates, because V3 established that it changes every published denominator and
   two control gates: no number produced before it is closed describes the batch
   it was computed from.
1. **Close the pre-freeze gates** the preregistration marks `GATE(pre-freeze)`:
   the mutant adequacy gate, the off-gold equivalence certificate, the
   clean-room re-run against the frozen prose, the OC table for (τ, δ, N = 50),
   and this file's S, G and T items — S6 (register a census stimulus), S7 (the
   Δ₀ sweep for the reported interval endpoints), S8 (the unequal-N inversion,
   or a registered common-denominator rule), S9 (the `engineSuppliedKill`
   manifest member) and S10 (make the reference-vs-gold floor gate actually
   run) are the five the scorer refuses on today.
2. **Land the registered documents**: `policy/POLICY.md` (the frozen copy of
   the design draft), `gold/GOLD.json`, `mutants/MANIFEST-*.json`,
   `reference/REFERENCE-*.md`, `controls/off-gold-equivalence.json`,
   `arms/<ARM>/PROMPT.txt`. `make_manifest.py --freeze` refuses while any
   registered document is still pending, so this step is checkable rather than
   remembered.
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
