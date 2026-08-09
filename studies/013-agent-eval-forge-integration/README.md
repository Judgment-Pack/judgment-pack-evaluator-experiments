# Study 013 — can an independently developed agent-regression harness see the judgment/integration boundary?

**Status: preregistration frozen by the merge of pull request #PRNUM (three
cross-vendor review rounds recorded in PREREG-REVIEW.md); the registered
primary attempt has not yet run.** Everything under `pilots/` is pre-freeze
harness validation, labeled as such, and supports no claim beyond "the
machinery works". No model has been called; the study so far is entirely
deterministic and offline.

## The question

An agent that acts on an organizational decision can fail in two places: inside
the judgment (the rule, threshold, exception, or evidence semantics that produce
the disposition) or around it (the fact wiring, the disposition handling, the
tool invocation). The deterministic judgment contract claims to make the first
kind of failure testable in isolation. This study drives both kinds of failure,
one at a time, through an independently developed agent-regression harness —
[Agent Eval Forge](https://github.com/deghosal-2026/agent-eval-forge), pinned at
`8925cac`, MIT, no JPS lineage — and asks which detection layer catches each:

- **J** — the judgment layer's own tooling: `jpack packs test` over an instance
  matrix, and the pinned evaluator's refusals;
- **F** — the external harness's deterministic scorers (tool trace, arguments,
  blocked tools), reached through a study driver;
- **G** — the study gate: disposition-vs-golden and action-vs-expectation
  diffs on completed artifacts (pins and completeness are a separate global
  validity channel, not a detection layer).

A second, deliberately unforced question: how much of the upstream harness's own
scenario suite contains a judgment question at all. The registered answer from
classification (CLASSIFICATION.md): **none of the 28 upstream scenarios does** —
12 test integration machinery, 14 test capabilities orthogonal to both, 2 are
deferral-shaped but conversational. That is an author-judgment census about applicability, not an adjudicated
empirical endpoint, and not a failure of either system.

## What this study is not

- No model or operational efficacy claim. Study 001's negative result on the
  answerable-only endpoint stands untouched; nothing here re-litigates it. The
  Arm A deciders in the offline phase are scripted stand-ins (an oracle and a
  registered adversary) used as positive and negative harness controls — they
  say nothing about model behavior, and the pilot numbers are fixed-cell
  concordance on the registered mutation set, not detection rates. A
  model-mediated Arm A is a gated, paid phase that runs only after the freeze
  and explicit approval.
- Not a conformance claim, under §3.4 or otherwise, and not an endorsement of
  Agent Eval Forge as a release gate — UPSTREAM.md records four confirmed
  defects (never-nonzero exit codes, status-blind scoring, status-flip-only
  regression detection, unwired tool stubs) that this study routes around
  without modifying upstream.
- Not a caller-obligation claim: JPS Core binds no caller. The execution mapper
  here (disposition → act/record/review, with a protected tool that must not
  fire on non-actionable dispositions) is the **study's** integration contract.

## Layout

- `PREREGISTRATION.md` — draft; governs once frozen by merge
- `CLASSIFICATION.md` — all 28 upstream scenarios, categorized, with scorer ground truth
- `UPSTREAM.md` — Agent Eval Forge architecture findings, defects, provenance
- `upstream/` — pinned upstream bytes (2 scenario packs, 24 fixtures, LICENSE, manifest)
- `packs/` — byte-pinned JPS packs (4 evaluation-corpus packs + 2 valid-document
  exception examples from runtime v0.16.0), used unchanged
- `scenarios/jps/` — `cases.json` (the registry: 21 cases, all 10 required case
  types) and generated cohort-2 artifacts
- `scenarios/mutations/` — `MATRIX.json` (registered detection expectations),
  `MATRIX-HOLDOUT.json` (four reviewer-authored prospective cells, verbatim,
  never executed pre-freeze), 11 mutated packs (M1–M6, M15a, h01–h04), all
  labeled defective
- `agents/` — the shared shell (one integration contract for every arm),
  deciders, 20 mutant entries, cohort-1 baseline
- `harness/` — `PINS.json`, `integrity.py`, `generate.py`, `mutate_packs.py`,
  `make_goldens.py`, `run_forge.py` (driver inside the Forge venv), `gate.py`
  (orchestrator + adjudicator), `repeat_check.py`, `tests/`
- `goldens/` — pinned-evaluator output per case + `EXPECT-CHECK.json`
  (21/21 agreement between hand-derived expectations and the evaluator)
- `jpack-project/` — the J-layer regression surface (instance matrix, 21 rows)
- `pilots/` — retained pilot batch: three arms, 16 mutations, cohort-1 runs,
  `ADJUDICATION.json` (0 divergences from MATRIX.json), `ARMS.json`,
  `REPEAT.json` (3 runs byte-identical)

## Reproduce the pilot

```sh
python3.12 -m unittest discover -s harness/tests        # offline invariants
FORGE_VENV_PY=<venv>/bin/python JPACK_BIN=<pinned jpack> \
  FORGE_CLONE=<pinned checkout> \
  python3.12 harness/gate.py --pilot-root pilots/<nonexistent-dir>
```

One gate invocation orchestrates everything: integrity refusal, the three
arms, all 16 mutations, both upstream packs, the three-run repeat check, and
the two-channel adjudication (validity + detection) with its verdict. The
pilot root must be a fresh directory — attempts are immutable.

The Forge venv is CPython 3.11.13 with the pinned clone installed editable;
the harness runs under CPython 3.12.11; the evaluator is the released v0.16.0
binary verified against the release `checksums.txt` (a tag build reproduces
its exact digest — the build is reproducible). `harness/PINS.json` records
every digest. Retained pilot batches (one per harness iteration): pilot-01 through
pilot-05, individually named in PREREGISTRATION.md §3 — identical endpoints
on the sixteen original cells in every batch. The four reviewer-authored holdout cells (MATRIX-HOLDOUT.json) are
never executed pre-freeze; the gate refuses --include-holdout while the
preregistration is a DRAFT.

Nothing in this repository claims any JPS conformance.
