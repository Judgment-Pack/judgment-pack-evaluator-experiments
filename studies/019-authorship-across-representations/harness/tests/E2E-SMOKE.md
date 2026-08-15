# End-to-end PILOT smoke — the transcript

The whole harness driven once, end to end, with **no codex call**: the stand-in
CLI seam (`STUDY_CLI_STANDIN`) answers the wrapper, the two engines are the real
pinned ones, and `harness/score.py` consumes what `harness/batch.py` wrote.

It is a **PILOT**. Every freeze pin in `harness/PINS.json` is null, the scorer
stamps `PILOT` into every output, and nothing below is citable as study data.
This file is a work record like `harness/SCAFFOLD.md` and is deleted at the
freeze; it carries **no timestamps**, so re-running the deterministic half
reproduces it byte for byte.

It found **three structural defects in `harness/score.py`**, all in section 8.
Read that section before reading any number above it.

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

The smoke root is drawn outside the worktree deliberately: the wrapper screens
the scratch path it builds against `leak_tokens.SCRATCH_TOKENS`, and this
checkout's own path contains `judgment-pack`, which is one of them. That is the
screen working, not a defect — `tests/test_batch.py::throwaway_root()` re-rolls
for the same reason.

## 3. The harness suite

```
$ cd $WT/harness
$ JPACK_BIN=$PINS/jpack/jpack OPA_BIN=$PINS/opa/opa_linux_amd64_static \
  OPA_CAPS=$PINS/opa/caps-filtered.json PYTHONDONTWRITEBYTECODE=1 \
  $PY -m pytest tests -q -p no:cacheprovider
353 passed
```

All ten `tests/test_score_pipeline.py` cases RAN (they skip by name when the
engines are unpinned or absent); nothing was skipped.

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
  coverage, with X1 rows excluded first — the same predicate `e4.partition_x1()`
  applies at scoring time, so the suite is not built out of cases the filter
  would drop;
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
| `FIXTURE-PINS.json` | `ffef1ed0e4e15e2a0e4918cb44a1343257ff077f88d8bf095cff85fc66dfd29a` |
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
| `attempt-001/ATTEMPT.json` | `387bd84793cef54c15edcf102d6577d988dfce1b7512dd7d66831cd4beac002a` |
| `attempt-001/RESULTS.json` | `484f37f6dad1b27ed9fe62d37b42ece1d8e956c73fdbd2ec4ed5d8d6a9efb552` |
| `attempt-001/RESULTS.md` | `d8a63b10f5c0b8123f896c82bd7d5139be4006d82763995cada3422225322fc1` |

`ATTEMPT.json`'s `pinsRawSha256` is
`sha256:1673a97c4cc339b70aa30f5398b40fe1b7e04f37440f7fae617a71e2f7ed76db` — the
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
  arm A through `jpack experimental evaluate` over three cases, arms B/C through
  `opa test`; zero identity failures, zero X1-excluded cases;
* **kill rates computed over the paired subset** — 18 of 81 paired adequate JPS
  mutants from arm A's three-case matrix, 17 of 73 paired adequate Rego mutants
  from the B/C suite (with `killedAdequate` 24/128 and 44/150 on the own-language
  denominators, each carrying its denominator's name);
* **E1 reported** — every admitted run reproduced all 105 gold rows in its own
  language (`goldPerfect: true` for all ten real admitted runs);
* **three refusals published rather than estimated**: `E5-STIMULUS-UNREGISTERED`,
  `E4-ENGINE-SUPPLIED-UNREGISTERED`, and `FM-UNEQUAL-N` (arm A admitted a
  different number of runs from arm C, and the registered contrast's closed form
  is the equal-size one — SCAFFOLD item S8, reached for real);
* **the decision table reached a terminal row**: row 2,
  `R1 inconclusive - control gate failed`, causes
  `references-reproduce-gold` (S10, fails closed), `golden-context` (null pin in
  the committed registry) and `e1-floor`.

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

**The X1 predicate.** `e4.in_x1()` (what `score.py` filters with) against the
predicate `design/gold/check_gold.py` enforces over the gold suite, on a shared
vector set of 840 points — the cross product of risk `{None, 0, 39, 40, 41, 55,
69, 70, 71, 100}`, spend `{None, 0.00, 99999.99, 100000.00, 100000.01,
500000.01, 3000000.00}`, country `{None, LOW, MEDIUM, HIGH}` and newVendor
`{None, yes, no}`, which straddles all three registered boundaries:

```
check_gold.py's four predicate lines are present verbatim
shared vector set: 840 points; agree 840; disagree 0
gold rows: 105; rows where the two differ or either says X1: none
```

## 8. What the smoke found — three structural defects in `harness/score.py`

None of these is fixed here. Each changes what a published population IS, so
each is a review decision and not an integration repair.

### D-1 — absent slots enter every population as admitted runs

`score.population()` partitions on `slot["code"]` alone and never on
`slot["present"]`. `read_slot()` returns `present: False, code: None` for a slot
that is not on disk, `None` is not an apparatus code, so **every one of the 138
absent slots entered its arm's denominator**, and `score_run()` — reaching
`extract_pair(slot["completion"] or "", arm)` with `completion` still `None` —
gave each of them `no-marker-block`.

Observed: arm A `attempted: 50, denominator: 49`; arms B and C `50`. Twelve slots
were on disk. E1 read 3/49, 3/50 and 4/50 and the registered floor "failed" as an
artifact of the phantom runs.

`terminality()` computes `present` correctly and declares the batch short —
nothing downstream reads it. §2.8's rule is that a declared short batch is scored
over the PREFIX; §1a's denominator is "attempted runs", and a slot that was never
attempted is not one. The driver already knows this: `batch.collect_slots()`,
`slots_on_disk()` and `reconcile_ledger()` are the readers SCAFFOLD item S11 says
`read_slot()` must reduce to.

### D-2 — a timeout is scored as `slot-shape`

`read_slot()` tests for `REFUSAL.json` **before** it reads `CALL.json`, and
returns `slot-shape` for any slot that carries one. Global index 8 was classified
`call-timeout` by the driver (ledger record and `REFUSAL.json` `code`), and
`CALL.json` carries `timedOut: true` — and the scorer filed it as `slot-shape`.

Both codes are on §1a's apparatus side, so no denominator moves. What moves is
the **control gate**: `population()["timeouts"]` counted 0, and
`timeout-rate-within-cap` reported `held: true` over a batch that contained a
timeout. That is exactly the undercount `harness/PORTS.md`'s registered
difference (2) says status 12 exists to prevent — "undercounting it would let a
batch pass a cap it breached" — reintroduced one layer up, in the reader.

`read_slot()` also cannot return `golden-context-mismatch`, which SCAFFOLD S11
already records; this is the same gap with a second consequence.

### D-3 — the E2 table cannot report a single authoring code

`e2_profile()` counts `slot["code"]`, which `read_slot()` populates from the
WRAPPER's exit status — and every code the wrapper can produce is on the
apparatus side. The authoring codes are assigned later, by `score_run()`, onto
the RUN record. So `orderedCodes` is a table of six authoring codes that is
**structurally always zero**, and its `admitted` count is the number of slots
that exited cleanly rather than the number of artifacts that were admitted.

Independent of D-1 and demonstrated by a real slot: global index 11 (arm B
run-004) carried a genuine no-marker completion, `perArmRuns` records it as
`no-marker-block`, and arm B's E2 published `admitted 50/50` with every code at
zero. §5 makes E2 a headline, not a footnote; two tables in one `RESULTS.json`
describing the same runs differently is not a presentational problem.

---

## 9. Reproducing this

The deterministic half — sections 3 and 7 — reproduces from the worktree alone.
Section 4 onward needs the two pinned binaries and the fixture builder. The
committed state this transcript was taken against:

| file | sha256 |
|---|---|
| `harness/PINS.json` | `1673a97c4cc339b70aa30f5398b40fe1b7e04f37440f7fae617a71e2f7ed76db` |
| `harness/PORTS.md` | `ac30409813dde5918d127ccc163800c3a8a17cda9148f2922a9b83cdcd8ed5f8` |
| `harness/STUDY-MANIFEST.sha256` | `09f8c6e67de47d3a1864c1cbb2b786d5ee8b8e92581eb4fc02a33b83b8123c97` |
| `harness/integrity.py` | `d0dbca3a255a38fce383d5cd1bce8d85736d48da9d5e1a80f3f5740393dce3f8` |
| `harness/make_manifest.py` | `40cf9b4c4756e105bd2a2515941c732c0e73784f036e00ce006b9ed21d221e02` |

`arms/BATCH.json` and `arms/SHORTFALL.json` carry the wrapper's own UTC stamps
and are therefore not digest-stable across runs; their digests are deliberately
not recorded here. Every scorer output above is.
