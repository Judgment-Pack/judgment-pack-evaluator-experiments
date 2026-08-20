# End-to-end PILOT smoke — the transcript

The whole harness driven once, end to end, with **no codex call**: the stand-in
CLI seam (`STUDY_CLI_STANDIN`) answers the wrapper, the two engines are the real
pinned ones, and `harness/score.py` consumes what `harness/batch.py` wrote.

It is a **PILOT**. Every freeze pin in `harness/PINS.json` is null, the scorer
stamps `PILOT` into every output, and nothing below is citable as study data.
This file is a work record like `harness/SCAFFOLD.md` and is deleted at the
freeze; it carries **no timestamps**, so re-running the deterministic half
reproduces it byte for byte.

> **ARCHIVE NOTICE (round-2 finding R2-14). Sections 1–8 of this file are the
> SECOND-pass run record and their numbers are SUPERSEDED.** They were measured
> before the arm-A reference repair, against a 145-mutant arm-A corpus, a 105-row
> gold suite and a single cross-language τ cut. All three are gone: **X1 is
> retired, `e4.partition_x1()` no longer exists, and `e4.in_x1()` survives only
> as an explicitly NON-GATING measurement helper that nothing reads to decide
> anything** — the registered exclusion registry is empty (round-1 R1-2) — gold
> is 117 rows, and there are
> **two** integer cuts, one per language (round-1 R1-1). §9 below is the current
> pass and governs wherever the two disagree. Sections 1–8 are kept because a run
> record is evidence of what ran, not a claim about the tree; nothing in them may
> be read as describing the harness as it stands.

It found **three structural defects in `harness/score.py`** on its first run.
All three are FIXED, and section 8 is now the re-run that shows each one closed
in the numbers rather than in a claim. Every scorer item `harness/SCAFFOLD.md`
carried has landed with them (S6-S11), so this transcript is the second pass:
same apparatus, same twelve slots, a scorer that reads a slot the way the driver
writes one.

---

## 1. What was stood in, and what was not

| piece | in this smoke | why |
|---|---|---|
| the authoring CLI | `harness/tests/test_batch.py`'s `FAKE_CLI`, reached through `STUDY_CLI_STANDIN` and pinned by digest in the fixture registry | section 7: no model call outside a registered batch. The seam removes no gate — the wrapper hashes whatever it names against `codex.binarySha256` |
| the study root | a stand-in tree whose `harness/` is a **symlink to the committed harness**, with `012-policy-perturbation` and `014-openworkproof-binding` symlinked as siblings | the bytes that run are the committed bytes; only the path they are invoked by moves. The siblings are symlinked so `integrity.verify_chain()` runs for real rather than being stubbed as it is in `tests/test_batch.py` |
| the registry | a **fixture registry** with every freeze pin filled and the stand-in binary pinned — never the committed one | `require_freeze()` refuses a PILOT, correctly. N, the slot count, the block order, the tail and the 2700 s ceiling are the committed registry's, unchanged, so `check_registry()` runs for real |
| the frozen artifacts | the design tree's `gold.json`, `refA/MANIFEST.json`, `refB/MANIFEST.json`, the 145 JPS and 185 Rego mutants and the two references, copied into the registered positions | the registered documents do not exist pre-freeze; the scorer refuses to substitute from `design/`, so the smoke puts them where the freeze will |
| `jpack` 0.17.0, `opa` 1.19.0 | **the real pinned binaries**, verified fail-closed by `engines.Toolchain` | there is no stand-in for an engine here: the admission, E1, identity and kill all ran for real |
| the timeout | the stand-in exits **124** — `timeout(1)`'s own status — which is exactly what the wrapper's timeout branch reads | the ceiling cannot be driven by wall clock inside a registered-order batch: `check_registry()` refuses any registry naming a ceiling other than 2700 s, which is the guarantee working. The wall-clock ceiling IS covered, at a 2 s ceiling through the probe path, by `tests/test_batch.py::TimeoutCeiling` |

The twelve slots are `--runs 12` followed by `batch.py shortfall`, which is the
registered way to run less than the whole order. The registry cannot name
another N: `check_registry()` compares `batch.n` and `batch.slots` against the
driver's own constants and refuses, so a "mini registry" is unreachable by
construction and the shortfall declaration is the mechanism that exists instead.

## 2. The environment

```
PY=<the pinned CPython 3.12.11, by absolute path>
PINS=<the pinned-binary directory>
  $PINS/jpack/jpack                  sha256 42f35f7900bea6dfce215631b50729ab22dd347289e1bde3412604fb043a22e9
  $PINS/opa/opa_linux_amd64_static   sha256 1dd5c5591ff856f5e20a1d66bafae9511ddf3c5552ed3b5070c70b2b6580ee3f
  $PINS/opa/caps-filtered.json       sha256 06202a2e599b4389cd3c23b8cc11d5d9384f46860e575e1beb5e8ce99622261a
WT=<this worktree>/studies/019-authorship-across-representations
R=<a smoke root whose path carries no leak token>
```

The smoke root is drawn outside the worktree AND outside the agent scratchpad,
deliberately: the wrapper screens the scratch path it builds against
`leak_tokens.SCRATCH_TOKENS`, and both of those paths contain `judgment-pack`,
which is one of them. That is the screen working, not a defect —
`tests/test_batch.py::throwaway_root()` re-rolls for the same reason. `$R` for
this run is a plain `/tmp` directory whose name carries no token.

## 3. The harness suite

```
$ cd $WT/harness
$ JPACK_BIN=$PINS/jpack/jpack OPA_BIN=$PINS/opa/opa_linux_amd64_static \
  OPA_CAPS=$PINS/opa/caps-filtered.json PYTHONDONTWRITEBYTECODE=1 \
  $PY -m pytest tests -q -p no:cacheprovider
387 passed
```

All **twelve** `tests/test_score_pipeline.py` cases RAN (they skip by name when
the engines are unpinned or absent); nothing was skipped. The suite grew from
353 to 387 with the six scorer items: the scorer's slot cases moved onto the
DRIVER's fixtures as `tests/test_score_attempt.py::DriverBuiltSlots` (fourteen
cases built by `batch.stamp_slot()`/`refuse_slot()`/`seal_slot()` and read by
`score.read_slot()`), the Delta0 sweep and the unequal-N inversion took eleven
cases in `tests/test_score_stats.py` (including the one that matters: the
general form reproduces `OC-TABLE.md`'s c* and realised size at N = 30/50/100
EXACTLY, as the same rationals), the registered census stimulus took three, the
`engineSuppliedKill` member four, and the floor gate two — one that it holds
against both references over all 105 gold rows, one that it FAILS against a real
Rego mutant standing in for the arm-B reference, because a gate nothing can make
fail is the thing section 6 exists to prevent.

## 4. The fixture

```
$ $PY $SMOKE/build_smoke.py $R
derived matrix rows: d6c-40-100k, d6b-39-500k01-absent, d8-40-100k01
```

`build_smoke.py` (sha256
`e3b9ef584b3bfea8d693c05fa2ac960fb30b748508b582334a1933ab8e7bbcbf`) lives
outside the study tree and outside the manifest: it is a fixture builder, not
reviewed harness code.

The completions are **derived, never transcribed**:

* the three matrix rows are gold rows chosen greedily for mutant-witness
  coverage. *(Archived: this pass excluded X1 rows first, via the then-existing
  `e4.partition_x1()`. That predicate is gone and the exclusion registry is
  empty; the current builder excludes nothing.)*
* arm A's `MATRIX:` block is those three points with expectations read off the
  arm's **own reference pack**, and its `PACK:` block is that reference;
* arms B/C's `TESTS:` block is the same three points against the arm's own
  reference policy, one named `test_case_N` rule each — not the design pilot's
  partial-set rule, because a partial set that produces no entry for a
  mismatching case does not FAIL, and a suite that cannot fail is not an
  identity control.

That is what makes the identity control pass **by construction**: the smoke
tests the harness, not authorship.

| artifact | sha256 |
|---|---|
| `FIXTURE-PINS.json` | `4177d510801ff8f7f675fa81d5611b5f165141b736de0f116fa4e9b0163521dd` |
| derived `matrix.json` | `f90cf3b7c523ca6fd5c46bdcfe5e48716d9155859bf9609bbc046a754d2c258a` |
| derived `suite.rego` | `f940c49cd41b7f33e66fdac84f3e228810a49f0eadf236faf8c7dc2e53aedd1b` |
| stand-in CLI `plan.json` | `25fea31b135cbb69c14663f1bc7d9aa5cfbc250ac7d3966e860221a1704db2dc` |

Independent identity check of the derived suite against the reference policy,
before the batch:

```
$ $PINS/opa/opa_linux_amd64_static test \
    $R/studies/019-.../reference/refB/policy.rego $R/suite.rego \
    --capabilities $PINS/opa/caps-filtered.json
PASS: 3/3      (exit 0)
```

## 5. The batch

```
$ cd /tmp
$ HOME=$R/home PYTHONSAFEPATH=1 PYTHONDONTWRITEBYTECODE=1 \
  STUDY_CLI_STANDIN=$R/cli/codex \
  $PY $R/studies/019-.../harness/batch.py run \
      --scratch-parent $R/scratch --pins $R/FIXTURE-PINS.json --runs 12
001 A run-001: exit 0
002 B run-001: exit 0
003 C run-001: exit 0
004 B run-002: exit 0
005 C run-002: exit 0
006 A run-002: exit 0
007 C run-003: exit 0
008 A run-003: exit 12 (call-timeout)
009 B run-003: exit 0
010 C run-004: exit 0
011 B run-004: exit 0
012 A run-004: exit 0
batch: 12 slots this invocation (1 refused), 12 of 150 in the ledger
```

Everything a batch has to pass before its first call passed for real: the port
chain and the exact-set manifest through `verify_ported_bytes()`, the registry's
order expansion, all three arm prompt digests, the golden capture, the isolation
negative control's assent and record, and the CLI's own digest and version.

The four planned outcomes landed where they were planned:

| global | arm / slot | planned | wrapper | driver code |
|---|---|---|---|---|
| 1, 6, 12 | A run-001/002/004 | arm-A completion | exit 0 | — |
| 2, 4, 9 | B run-001/002/003 | arm-B/C completion | exit 0 | — |
| 3, 5, 7, 10 | C run-001…004 | arm-B/C completion | exit 0 | — |
| **8** | A run-003 | **timeout** | **exit 12** | **`call-timeout`** |
| **11** | B run-004 | **no marker block** | exit 0 | — (an authoring outcome, decided at scoring) |

The timeout slot is sealed with `CALL.json` carrying `timedOut: true`,
`timeoutSeconds: 2700`, `timeoutKillAfterSeconds: 60`, and a `REFUSAL.json`
whose `code` is `call-timeout`; the ledger record carries `wrapperExit: 12` and
`code: "call-timeout"`.

```
$ $PY $R/studies/019-.../harness/batch.py shortfall \
      --reason "end-to-end PILOT smoke: a twelve-slot prefix, not a batch" \
      --pins $R/FIXTURE-PINS.json
shortfall declared: 4 of 50 rounds, 12 of 150 slots completed
```

## 6. The scorer

```
$ HOME=$R/home JPACK_BIN=... OPA_BIN=... OPA_CAPS=... \
  PYTHONSAFEPATH=1 PYTHONDONTWRITEBYTECODE=1 \
  $PY $R/studies/019-.../harness/score.py \
      --attempt-root $R/attempt-001 --batch-root $R/studies/019-.../arms
tau cut: a run is high-kill iff it kills at least 77 of the 81 paired adequate mutants (tau = 19/20)
R1 inconclusive - control gate failed (PILOT)
```

| output | sha256 |
|---|---|
| `attempt-001/ATTEMPT.json` | `4f31e43c15a40f0fdab5c0d20ccdcfc7b113721d840329893cb52282133add39` |
| `attempt-001/RESULTS.json` | `8d0c0ce86571df22177362bfa67d2e14b7da70e91fa79cdc8679738d7913abeb` |
| `attempt-001/RESULTS.md` | `9ef77dc63d0f267c98430c6cbe85edb7058a150fc104a798aecf36813d8c7445` |

`ATTEMPT.json`'s `pinsRawSha256` is
`sha256:dccdfe58c6de40cec1e8f1af7294c694e8f048be0d92220df23aecbf9a7773d7` — the
**committed** registry, not the fixture. The fixture registry is the driver's;
the scorer reads the study's own, which is why the label is PILOT with all
eleven freeze pins named as unfilled.

**Rescoring is byte-identical**, including under a different parent with the same
attempt basename (the path-leak case `tests/test_score_attempt.py` also drives):

```
$ $PY .../score.py --attempt-root $R/second/parent/attempt-001 --batch-root ...
$ diff -r $R/attempt-001 $R/second/parent/attempt-001   # no output
```

What the run established, mechanically:

* **label** `PILOT`, eleven unfilled freeze pins listed;
* **terminality** `{present: 12, registered: 150, complete: false, declared: true}` —
  the short-batch XOR branch, exercised;
* **toolchain** both engine digests enforced against the pins, `problems: []`,
  and the null `opa.capabilitiesSha256` recorded under `unenforcedPins` rather
  than silently satisfied;
* **the capabilities canary** `refused: true` — the gate has power against the
  real binary;
* **pairing** 134 witness groups; 81 paired adequate JPS, 73 paired adequate
  Rego; **the τ cut derived at run time**: 77 of 81, `cutRate` 0.9506…;
* **the identity control passed on the reference-derived suites in every arm** —
  arm A through `jpack experimental evaluate`, arms B/C through `opa test`; zero
  identity failures, and no excluded-case member anywhere in the record *(X1 is
  retired; §4 registers no per-case filter and no per-run excluded-case count,
  and round-3 finding R3-9 removed the `x1Excluded`/`x1ExcludedCases` members
  and the report's "Excluded cases" column that were still publishing one)*;
* **the reference-vs-gold floor gate RAN** (S10): 105 rows against both
  references, `failureCount: 0`, `held: true`. It was `held: false` with the
  code `GATE-FLOOR-NOT-RUN` in the first pass, and it is a real evaluation now —
  `tests/test_score_pipeline.py` also drives it against a mutant standing in for
  the arm-B reference and gets `held: false` with the failing rows named, so the
  gate is shown to have power rather than shown to pass;
* **the registered census ran** (S6): stimulus `the gold-row input set (105 gold
  inputs)`, three per-arm records with their encodings, covering sets and
  pairwise-disagreement profiles, the §9 no-tradeoff note carried inside each
  record;
* **the engine-supplied split is published both ways** (S9): arm A's 41 listed
  mutants read from the frozen manifest — `killsIncluded {killed: 54, paired:
  243}` against `killsExcluded {killed: 27, paired: 129}` over its three runs —
  and arms B/C reporting an EMPTY registered class, the two columns equal,
  because the Rego ladder has no structural conflict detection;
* **the contrast is scored at UNEQUAL denominators** (S8): arm A admitted 3 runs
  and arm C 4, and the general unequal-N FM inversion returns `A-C: 0/3 vs 0/4,
  excludesZero false, INDETERMINATE` where the first pass refused with
  `FM-UNEQUAL-N`;
* **the interval endpoints are reported** (S7): `[-13/25, 63/100]`, exact
  rationals on the registered Δ₀ mesh (denominator 100), acceptance set
  contiguous, so no convex hull was taken;
* **E1 reported** — every admitted run but one reproduced all 105 gold rows in
  its own language; arm B's fourth slot is the planned no-marker completion and
  reaches no gold evaluation at all;
* **no refusals**: `RESULTS.json`'s `refusals` object is empty. Every one of the
  three the first pass published — `E5-STIMULUS-UNREGISTERED`,
  `E4-ENGINE-SUPPLIED-UNREGISTERED`, `FM-UNEQUAL-N` — is a computation now;
* **the decision table reached a terminal row**: row 2,
  `R1 inconclusive - control gate failed`, causes `golden-context` and
  `timeout-rate-within-cap`. Both causes are DIFFERENT from the first pass's and
  both are the fixes showing: `references-reproduce-gold` and `e1-floor` now
  hold on their own evidence, `golden-context` fails because the committed
  registry pins neither the capture nor the isolation-negative assent, and
  `timeout-rate-within-cap` fails because the batch's one real timeout is
  finally counted.

## 7. Cross-checks

**The port chain, two-sided, over every row including the new ones.**

```
$ $PY -c "import integrity; r = integrity.verify_chain(); print(len(r['rows']))"
7
```

Seven rows, each bound to the authority it has: six to Study 012's own
DESTINATION cells, one (`make_manifest.py`, from Study 014) to the recorded
commit's working file. `tests/test_ports_chain.py` holds this, and holds that a
row removed and a row added both refuse over a mutated copy whose registry pin
was rebuilt so the mutation is tested at the destination-set check rather than at
the digest gate one link earlier.

**The manifest and its exclusions.** `tests/test_manifest.py` — eight cases,
including the two ADR 0004 exclusions asserted while both files exist, the
linear-anchor exclusion of `harness/PINS.json`, the manifest not covering itself,
and (added here) the scorer package covered **module for module against the
directory** rather than against a list.

**The OC-table constants.** `e4lib/stats.py`'s calibration reproduces
`design/mutants/OC-TABLE.md` section 2 exactly, in rationals:

| N | `critical_level_at()` c* | OC-TABLE.md c* | realised size (code) | OC-TABLE.md |
|---|---|---|---|---|
| 30 | 30/7 | 30/7 | 0.0469 | 0.0469 |
| **50 (registered)** | **625/154** | **625/154** | **0.0488** | **0.0488** |
| 100 | 175/44 | 175/44 | 0.0496 | 0.0496 |

`FM_ALPHA = 1/20`, `MESH_DEN = 1000`, `TAU = 19/20`, `DELTA = 1/5` — the mesh and
the two-sided α the document pins.

**The X1 predicate — ARCHIVED, and nothing filters on it.** This cross-check
compared `e4.in_x1()` (what `score.py` then filtered with; it filters with
nothing now, and the predicate is retained only to measure) against the
predicate `design/gold/check_gold.py` enforces over the gold suite, on a shared
vector set of 840 points — the cross product of risk `{None, 0, 39, 40, 41, 55,
69, 70, 71, 100}`, spend `{None, 0.00, 99999.99, 100000.00, 100000.01,
500000.01, 3000000.00}`, country `{None, LOW, MEDIUM, HIGH}` and newVendor
`{None, yes, no}`, which straddles all three registered boundaries:

```
ARCHIVED transcript — X1 is retired; `partition_x1()` is gone and `in_x1()`
gates nothing
check_gold.py's four predicate lines are present verbatim
shared vector set: 840 points; agree 840; disagree 0
gold rows: 105; rows where the two differ or either says X1: none
```

## 8. The three structural defects, and the numbers that show them fixed

The first pass of this smoke found three defects in `harness/score.py`, each of
which changed what a published population IS. All three are fixed. What follows
is the FIRST pass's number beside the SECOND's, from the two `RESULTS.json`
files, because a fix nobody can see in a number is a claim.

### D-1 — absent slots entered every population as admitted runs — FIXED

`score.population()` partitioned on `slot["code"]` alone and never on
`slot["present"]`. A slot not on disk carried `code: None`, `None` is not an
apparatus code, so **every one of the 138 absent slots entered its arm's
denominator** and `score_run()` — reaching `extract_pair(slot["completion"] or
"", arm)` with `completion` still `None` — gave each of them `no-marker-block`.

| arm | first pass | this pass |
|---|---|---|
| A | `attempted 50, denominator 49` | `registered 50, absent 46, attempted 4, denominator 3` |
| B | `attempted 50, denominator 50` | `registered 50, absent 46, attempted 4, denominator 4` |
| C | `attempted 50, denominator 50` | `registered 50, absent 46, attempted 4, denominator 4` |

Twelve slots were on disk in both passes. E1 read `3/49`, `3/50`, `4/50` and the
registered floor "failed" as an artifact of the phantom runs; it reads `3/3`,
`3/4`, `4/4` now and the `e1-floor` gate HOLDS on the runs that exist.
`population()` also publishes `registered` and `absent` beside `attempted`, so
the prefix is a published fact rather than a subtraction a reader has to do.

### D-2 — a timeout was scored as `slot-shape` — FIXED

`read_slot()` tested for `REFUSAL.json` before it read `CALL.json` and returned
`slot-shape` for any slot carrying one. Global index 8 was classified
`call-timeout` by the driver and the scorer filed it `slot-shape`. Both codes are
on §1a's apparatus side, so no denominator moved — what moved was the CONTROL
GATE.

| | first pass | this pass |
|---|---|---|
| arm A's apparatus codes | `{"slot-shape": 1}` | `{"call-timeout": 1}` |
| `population.A.timeouts` | `0` | `1` |
| `timeout-rate-within-cap` | `held: true` | **`held: false`** |

The gate held vacuously over a batch that contained a timeout — exactly the
undercount `harness/PORTS.md`'s registered difference (2) says status 12 exists
to prevent. It fails now, on a real timeout, and appears in the decision's
`causes`. `read_slot()` reads the outcome through `batch.slot_outcome()`, which
is the driver's own reader and checks the code against `WRAPPER_CODES` rather
than taking it from the file.

### D-3 — the E2 table could not report a single authoring code — FIXED

`e2_profile()` counted `slot["code"]`, which `read_slot()` populated from the
WRAPPER's exit status — and every code the wrapper can produce is on the
apparatus side. The six-code table §5 makes a headline was structurally always
zero, and `admitted` counted clean EXITS rather than admitted ARTIFACTS.

| | first pass | this pass |
|---|---|---|
| arm B's E2 | `admitted 50/50`, every code `0` | `denominator 4, admitted 3`, `no-marker-block: 1` |
| the same run in `perArmRuns` | `no-marker-block` | `no-marker-block` |

Global index 11 (arm B run-004) carries a genuine no-marker completion. The two
tables in one `RESULTS.json` described the same run differently; they agree now,
because E2 counts the RUN records — the ones `score_run()` assigns §1a's
authoring codes to. `e2_profile()` also REFUSES an apparatus code on a run
record, so the population rule failing to exclude one is a refusal rather than an
E2 row, and it publishes `artifactAdmitted` beside `admitted` so neither count
has to stand in for the other.

### The two refusals D-1 and D-2 left unreachable, now reachable

SCAFFOLD S11 recorded that `read_slot()` could return neither
`golden-context-mismatch` nor a seal refusal. Both are reachable, and the seal
one is demonstrated here on this batch's own bytes:

```
$ cp -a $R/studies/019-.../arms $R/tamper
$ printf 'x' >> $R/tamper/C/authoring/run-002/completion.txt
$ ... score.py --attempt-root $R/attempt-tamper --batch-root $R/tamper
pipeline-invalid: pipeline-invalid before any run was scored
```

`RESULTS.json` is terminal at decision row 1, `R1 inconclusive - pipeline-invalid`,
naming the problem:

```
terminality: arm C run-002: .../SLOT-MANIFEST.json does not verify against the
slot it seals: the tree on disk is not the one the manifest lists.
```

One appended byte, in a slot the driver sealed, and the scoring refuses. Before
the fix that slot was scored. §2.9 seals every slot by a terminal manifest and
`read_slot()` never called `verify_seal_of()`.

`golden-context-mismatch` cannot fire in THIS smoke and the reason is a property
of the fixture, not a gap: the scorer reads the study's own registry, whose
`golden.sha256` is null pre-freeze, so there is no pin to bind a run's stamp
against. It is driven under a filled registry by
`tests/test_score_attempt.py::DriverBuiltSlots::test_the_golden_context_mismatch_code_is_reachable`,
which builds a slot through the driver with another capture's digest stamped
into its `CALL.json` and gets the apparatus code back.

### Rescoring is still byte-identical

```
$ $PY .../score.py --attempt-root $R/second/parent/attempt-001 --batch-root ...
$ diff -r $R/attempt-001 $R/second/parent/attempt-001   # no output
```

Two roots with the same basename under different parents, no diff — so nothing
the six items added is derived from a clock or from where the attempt lives. The
Δ₀ sweep is the one that had to be checked: exact integer arithmetic over a
registered mesh with a fixed bisection count, and it reproduces bit for bit.

## 9. Reproducing this (second pass)

The deterministic half — sections 3 and 7 — reproduces from the worktree alone.
Section 4 onward needs the two pinned binaries and the fixture builder. The
committed state this transcript was taken against:

| file | sha256 |
|---|---|
| `harness/PINS.json` | `dccdfe58c6de40cec1e8f1af7294c694e8f048be0d92220df23aecbf9a7773d7` |
| `harness/PORTS.md` | `3a494a33fd2ca439f9efb4c04ce1b5cacfa9706cc46469a744ace4e626c78ad2` |
| `harness/STUDY-MANIFEST.sha256` | `9207f22b6a0e98fab9d9a5aac2ad8ab67c22726e57130ff83bd2d43e64b54960` |
| `harness/integrity.py` | `d0dbca3a255a38fce383d5cd1bce8d85736d48da9d5e1a80f3f5740393dce3f8` |
| `harness/make_manifest.py` | `40cf9b4c4756e105bd2a2515941c732c0e73784f036e00ce006b9ed21d221e02` |
| `harness/score.py` | `0bae03a369296173ee12a0e0bcab2dba108ba13d558145e399a5ced1926d47ae` |
| `harness/e4lib/stats.py` | `e045ed9171ed00658659f93ad9e98b16602471b36d898b43a536aa091f7b22ca` |
| `harness/e4lib/census.py` | `e540d0ce171351c07899aa15204d7d5cc6a329df15c0662796aa627988913fda` |
| `harness/transcript_check.py` | `5d1090f6c116c49aba755cb6b8648696d8a67d03fd424dbc918650f78f4bd2ad` |
| `design/mutants/refA/MANIFEST.json` | `89e0bd7521f092095fef113922ea23c3ba859860581401ce6aa028c9a05aeb04` |
| `design/mutants/refB/MANIFEST.json` | `6ed203f66383e0411fafc7f52534fee3dd2d947ef4a8ef1b7bbd0b8e8b73bd40` |

`arms/BATCH.json` and `arms/SHORTFALL.json` carry the wrapper's own UTC stamps
and are therefore not digest-stable across runs; their digests are deliberately
not recorded here. Every scorer output above is.

---

## 10. Third pass — after the round-1 response (supersedes sections 1–9's numbers)

Sections 1–5 reproduce unchanged (same fixture builder path, same twelve slots, same four
planned outcomes: slot 8 `call-timeout`, slot 11 no-marker; pre-batch identity 3/3). The
scorer's behaviour from section 6 onward is superseded by the round-1 fixes, and the
re-run shows them:

- **R1-7 visible.** The declared-short batch no longer computes endpoints: the terminal
  line is `UNRESOLVED-BY-DESIGN - the batch was declared short (PILOT)`, with **no cuts
  printed, no contrast, no direction** — which is also R1-14's no-publication-below-a-gate
  rule doing its work. Section 6's `tau cut: … 77 of the 81` line cannot recur: the single
  cross-language cut was R1-1's defect, the cut layer is per-language now (JPS 66/69,
  Rego 59/62 at the current manifests, after the round-3 adequacy re-closure moved both
  paired denominators), and it is exercised by the suite
  (`tests/test_score_e4.py`) rather than by a short-batch smoke, which by design never
  reaches it.
- **Fail-closed guards visible in this very replay.** The shortfall invocation without
  `PYTHONSAFEPATH=1` was refused with the untracked-source-scan message (operator slip,
  kept in the record); an attempt scored before the shortfall declaration existed
  published `pipeline-invalid before any run was scored`.
- **Rescoring is byte-identical** into a second root (`diff -r`, empty), and no output
  file contains an absolute path.
- Suite of record for this pass: **575 passed, 0 failed** with the pinned engines
  (five declaration-refusal tests had asserted an earlier draft's message wording — the
  refusals themselves fired; fragments realigned to the scorer's actual messages, recorded
  as an integration slip).
- Output digests this pass: `RESULTS.json 4d9188e0cbecff2f…`, `ATTEMPT.json
  4b759749e947bbd0…` (differ from section 6's because the terminal row differs — that is
  the fix, not drift).
