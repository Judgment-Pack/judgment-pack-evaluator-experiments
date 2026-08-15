# Scaffold — what this harness is, and precisely what remains

This file is the honest half of the port. `harness/PORTS.md` says what was
taken and what changed; this says what has **not** been built, by name, with
the source it comes from and the order the remaining work has to happen in.
It is deliberately **outside** the study manifest (`harness/make_manifest.py`
covers `harness/*.py`, `harness/*.sh` and the registered documents, not this
file): it is a work record that will be appended to and then deleted at the
freeze, and ADR 0004's argument about appendable files applies to it exactly.

**Nothing here can run a batch.** The wrapper is complete and the schedule is
derived and tested, but the driver's calling half, the scorer and every control
are absent. The state today, said plainly: every freeze pin in
`harness/PINS.json` is null, `integrity.study_label()` returns `PILOT`, and no
authoring call has been made.

## What exists and is tested

| file | state | tests |
|---|---|---|
| `harness/authoring_call.sh` | complete port, four registered differences | none yet — **T1** below |
| `harness/batch.py` | partial: schedule core, timeout constants, §1a code partition | `tests/test_schedule.py` (13), `tests/test_partition.py` (6) |
| `harness/integrity.py` | partial: chain, interpreter, unreviewed-bytes gate, label rule, manifest check | `tests/test_pins.py` (8) |
| `harness/transcript_check.py` | complete port; `LEAK_TOKENS` is design-time | none yet — **T2** below |
| `harness/make_manifest.py` | complete port, ADR 0004 applied | `tests/test_manifest.py` (8) |
| `harness/PINS.json` | every freeze pin null; toolchain blocks resolved and marked | `tests/test_pins.py` |
| `harness/PORTS.md` | five rows, two-sided, machine-read | `integrity.verify_chain()` |

34 tests pass and 1 skips (the scorer skeleton, S1) under CPython 3.12.11.
`integrity.verify_chain()`, `verify_interpreter()`, `verify_manifest()` and
`study_label()` all pass against the committed tree. `integrity.verify()` as a
whole currently REFUSES, correctly, for the reason in **T3**.

---

## S — the scorer, assembled from the design prototypes

The scorer is one file (`harness/score.py`), because the preregistration's
governing invocation is one command and "the scorer is the only publisher".
Its parts already exist as design prototypes and must be ported into it with a
two-sided `PORTS.md` row each — the prototypes are working code, not sketches,
and re-authoring them from memory would throw away the only artifacts that have
been run against the real engines.

**S1 — `harness/score.py` skeleton.** `--attempt-root results/primary-attempt-001`;
refuse if the attempt root exists; read the label from
`integrity.study_label()` and stamp it into every output; terminality (a batch
that did not complete is declared, not scored); exact rational
Clopper–Pearson intervals with registered test vectors; no timestamp and no
absolute path in any output. Source for the interval code and the terminality
discipline: Study 012 `harness/score_rates.py`
(`f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336`) — port by
digest, do not re-derive. **`ADMISSION_CODES` must be exactly
`batch.CODE_PARTITION`'s keys**; `tests/test_partition.py`'s last test is
written and skipping, and becomes a real assertion the moment the module lands.

**S2 — extraction and admission**, from `design/pilot/pilot_run.py`:
`ARM_MARKERS` (lines 81–86), `extract_block()` (181–216), `admit_arm_a()`
(242–275), `admit_arm_rego()` (276–315). One reconciliation is owed and is not
mechanical: the pilot's `DROP_ORDER` has **three** codes
(`no-marker`, `unparseable`, `invalid-artifact`) and §1a registers **six**
authoring outcomes — `invalid-artifact` splits into `schema-invalid-pack`,
`opa-check-failed`, `v0-syntax` and `unreadable-output-shape` depending on
which check refused. The split has to be made in the admission layer and its
codes diffed against `CODE_PARTITION`, or the E2 table will publish a coarser
partition than the one §1a registers.

**S3 — the two-engine execution layer**, from `design/pilot/pilot_run.py`
`eval_arm_a()` (347–376), `eval_arm_rego()` (377–414), `render_rego_input()`
(328–346), `facts_documents()` (316–327), `clean_env()` (232–241). The
invocation flags are pinned by `design/TOOLCHAIN-NOTES.md` and must be carried
verbatim: `opa eval --format json --fail --strict-builtin-errors --capabilities
<file> --timeout <t>` under `env -i` with `TZ=UTC` and a per-run exclusive
directory; `opa exec` does **not** accept `--capabilities` at v1.19.0. The
capabilities file is generated from the pinned binary with the registered
denylist and its digest fills `pins.opa.capabilitiesSha256`; the `time.now_ns`
canary must be refused, and that refusal is re-verified at attempt time as a
control gate.

**S4 — the E4 machinery**, from `design/mutants/e4_score.py`: `load_mutants()`
(152–194), `build_pairing()` (195–231), `align_expected()` (232–245),
`identity_arm_a()` (310–322), `kill_arm_a()` (323–336), `opa_test()`
(337–374), `case_signature()` (375–384), `oracle_verdict()` (425–442),
`reference_divergence()` (443–481), `score_arm()` (556–654). With it come the
registered pieces that are not in the prototype: the X1 filter with the
per-run excluded-case count published, the identity control reported as a
first-class per-arm rate, τ = 0.95, δ = 0.20, the hierarchical A−C then A−B
order, the INDETERMINATE row, and the 35 engine-supplied-kill mutants reported
both included and excluded.

**S5 — the E1 gold control**, from `design/gold/check_gold.py` (152 lines,
whole): structure, X1 exclusion, boundary witnesses, clause coverage, plus the
floor gate that both references reproduce every gold row at attempt time.

**S6 — E5, the interpretive-spread census.** §5 registers it as "012's census
machinery, ported", and **it is not ported yet**: Study 012's
`harness/census.py` (`911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea`)
owes this study a sixth `PORTS.md` row. Do not write a new census.

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

1. **Close the pre-freeze gates** the preregistration marks `GATE(pre-freeze)`:
   the mutant adequacy gate, the off-gold equivalence certificate, the
   clean-room re-run against the frozen prose, the OC table for (τ, δ, N = 50),
   and this file's S, G and T items.
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
