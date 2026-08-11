# Round-2 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 018 (transition rules over cited
registry state) in judgment-pack-evaluator-experiments, round 2 — the same different-vendor
reviewer as round 1. You returned DO NOT FREEZE with thirteen findings; the maintainer
accepted all of them and revised the study. Verbatim findings and written dispositions are
in reviews/round-1/ and PREREG-REVIEW.md. This round has two jobs: confirmation, and — per
your own closing line — authoring the reviewer holdout set.

The study, revised, at: <study worktree>/
Study 016's frozen tree and Study 017 are alongside it; RFC 0011 is at <spec worktree>/rfcs/.
The interpreter at <scratchpad>/venv/bin/python runs the suite offline.

PART 1 — confirmation. For each of R1-1..R1-13: RESOLVED / PARTIALLY RESOLVED / NOT
RESOLVED, verified against the current files rather than the dispositions, one line each
with the file you checked. Please prioritise:
- R1-1: is a rule now evaluated only over an authenticated membership answer, and can any
  input still compose to `usable` over a snapshot the registry rejected? Try to find one.
- R1-2: is membership at each cited prefix genuinely the pinned upstream's fold? Re-run
  your reinstatement and never-bound-digest cases, and look for any remaining divergence
  between this layer's notion of support and the upstream's.
- R1-3: is the holdout path retargeted to this study's fields throughout — schema,
  comparison, output names, divergence channels?
- R1-4/R1-5: are the rule and code names now precise about what the evidence establishes?
- R1-8/R1-9: are both byte-identical duplicates registered and excluded from the endpoint
  count, and is the remaining endpoint set free of further hidden duplication?
- R1-10: does the published matrix render rule evidence, and does R1's wording match what
  decide() actually counts?

Then: any NEW material problem is a finding R2-<n> with severity, file/section, failure
mode, concrete fix. Do not manufacture findings.

PART 2 — the reviewer holdout set. Author 6 to 10 cells, yours alone, to be committed
verbatim with attribution into harness/MATRIX-HOLDOUT.json and never executed before the
freeze; their structured expectations go in a separate file so your block stays
byte-for-byte. Requirements:
- Constructible from the registered apparatus alone: the pinned Study 016 registry writer
  (any events, positions, keys), this study's rule/citation.py (any citation head, any rule
  configuration), synthetic commitment tuples, and deterministic byte edits of retained
  files. No network, no clock, no new upstream seams.
- Each cell: id (h01, h02, ...), category, variant, role, attackerCapability
  (none/tamper/full-keys), registeredAbsences, a construction description precise enough to
  implement mechanically, the expected outcome for BOTH layers (currency codes from Study
  016's registry/SPEC.md, transition codes from rule/SPEC.md), the expected
  citedPosition/retiredAtPosition (each an integer or null), and a one-line rationale.
- At least one all-pass control showing the registered refusals are not brittleness.
- Prioritise where you judge the revised apparatus least settled: the currency gate, the
  upstream fold over multi-cycle histories, the window semantics after the rename, the
  per-series discipline, and the interaction between registered absences and rules that do
  not read the citation.

Output, exactly:
- "## Confirmation" — the thirteen resolution lines.
- "## New findings" — R2-<n> findings, or the line "none".
- "## Holdout set (authored by the round-2 reviewer)" — one JSON code block:
  {"reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2", "cells": [ ... ]}
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
