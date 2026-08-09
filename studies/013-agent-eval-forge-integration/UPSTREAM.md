# Agent Eval Forge — upstream findings (pinned at 8925cac, 2026-08-08)

Everything below was verified by execution against the pinned commit — install,
CLI, test suite, offline runs — not read off the README. License MIT
(© 2026 Debashish Ghosal). The study uses upstream unmodified.

## What it is

A framework-agnostic agent-evaluation harness, Python 3.11+, ~31.5k LOC.
Scenario packs in YAML; a versioned, whitelisted invocation payload (verified:
`expected`/`metrics` structurally cannot reach the agent); adapters (python
module, subprocess, http, langgraph, pydantic-ai); pydantic run artifacts with
lossless JSON round-trip; 30 registered scorers (15 deterministic + 4
deterministic security pattern-matchers + 11 LLM-judge; a MockJudge exists);
baseline/comparison machinery; 687 passing tests. The pack loader, runner,
payload builder, artifact recording, and deterministic scorers are genuinely
good and are the layers this study builds on.

## Confirmed defects the study routes around (none patched upstream)

- **D1 — `evalforge run` never exits non-zero.** Measured exit 0 with a safety
  violation (`exit_code: 4` inside scores.json) and with `--ci`. Only
  `evalforge test run` honours exit codes. → The study driver owns exit codes.
- **D2 — scoring never consults `artifact.status`.** An agent that crashed on
  all 20 scenarios scored "12 passed, 8 warned, 0 failed". → The driver asserts
  per-artifact completeness before any score is interpreted, and additionally
  refuses on deterministic scorer errors (upstream treats `passed: null` as
  neutral). This guard caught a real bug in the study's own scorer during the
  pilots — the failure mode is not hypothetical.
- **D3 — regression detection is status-flip only.** A 0.75 → 0.00 score drop
  reports `"unchanged"`; `overall_score_delta` gates nothing; the documented
  snapshot compare mode is unreachable (no writer for `score_snapshot`).
  → The study gate computes its own diffs.
- **D4 — tool interception is not wired.** `ToolStub` has no call sites;
  `--fixtures` only stamps payload/env flags; the agent under test self-serves
  fixtures on the honour system. → Both arms share one tool layer in
  `agents/shell.py`, and the gate audits trajectories.

## Behaviors that shaped scenario authoring

- `expected.criteria` (rubrics) are **dead text** — no code reads them; judge
  prompts use hardcoded per-metric criteria and never see the trajectory. All
  cohort-2 expectations therefore live on the deterministic surface:
  `expected.trace` (+`args_match: subset`), `required_tools`,
  `disallowed_tools`, schema key-presence.
- `zero_disallowed_actions` is blocking and works — it carries invariant I1's
  Forge-side detection. The hybrid `policy_adherence` path is unusable offline
  (with no judge the gate never runs and the metric errors).
- The `exact_match` alias silently runs `tool_correctness`; no exact-match
  scorer exists. Avoided entirely.
- Metric names are validated against a 69-name allowlist of which 39 have no
  scorer. The study's `approval_boundary_adherence` deliberately claims an
  allowlisted, unregistered name and registers a real scorer for it at
  driver-import time — upstream mechanism, no upstream change.
- Severity model: non-blocking metric failures make a scenario **warn**, and
  per-scenario score is an unweighted mean (`Metric.weight` is dead). Measured
  consequence: a wrong fee charged with the right tool shape is a *warn*, not
  a failure — a CI gate keyed on Forge scenario status would pass it. The
  study counts detection at metric level and lets blocking safety scorers
  drive status.
- CLI `python:module.func` is broken as documented (only `python:<module>`
  with a function literally named `run` works); `evalforge init` scaffolds a
  pack its own loader rejects; the repo's own CI eval job is broken twice
  over. The study bypasses the CLI via the library API.
- Determinism: seeds never reach agents, the PYTHONHASHSEED freeze is a no-op,
  and fixture use is unenforced — reproducibility in this study comes from the
  deterministic shell, the pinned evaluator, and `repeat_check.py`
  (three fresh Arm B runs byte-identical), not from upstream machinery.

## Provenance

The entire codebase (345 files, 12 documented milestones, full OSS governance
furniture) arrived in a single initial commit dated 2026-08-02; there are two
substantive human commits and five bot commits in total, one author, and PR
numbers (#245–#249) far exceeding the commit count — consistent with a
squash-published, largely AI-assisted drop. Field-test reports are dated on or
before the initial commit. Consequences for this study's claims:
"independently developed" holds in the sense that matters (no JPS lineage —
no reference to judgment packs anywhere in the tree), but the harness is not
field-hardened, and its scenario suite cannot be treated as an independent
sample of real agent workloads. Both caveats are registered as threats to
validity.
