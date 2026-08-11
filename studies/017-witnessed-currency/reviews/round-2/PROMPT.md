# Round-2 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 2 — the same different-vendor
reviewer as round 1. Study 017 is a determinism-and-cryptography experiment about the
LIMITS of a signed version-history comparison mechanism.

In round 1 you returned DO NOT FREEZE with fifteen findings. The maintainer accepted all
of them, reproduced your R1-4 case locally before accepting it, and revised the study. The
verbatim findings and the written dispositions are in PREREG-REVIEW.md and
reviews/round-1/. This round has two jobs: a confirmation pass, and — per your own closing
line in round 1 — authoring the reviewer holdout set.

The study, revised, at:
  <study worktree>/

Study 016's frozen tree is one directory up; spec RFC 0011 (with both merged amendments)
is at <scratchpad>/spec-wt/rfcs/0011-judgment-currency-anchor.md. The interpreter at <scratchpad>/venv/bin/python runs the
whole suite offline.

PART 1 — confirmation. For each of R1-1..R1-15: RESOLVED / PARTIALLY RESOLVED / NOT
RESOLVED, verified against the current files rather than the disposition prose, one line
each with the file you checked. Please prioritise:
- R1-4: is a record now associated with a witness by signature verification everywhere it
  matters — both in witness/verify_witness.py and in the scorer's pair check? Re-run the
  record-identity case you described in round 1, and check whether a record's
  self-declared identity field can still influence any outcome. Are the remaining
  situations — a record absent from the retained set, a record that verifies under no
  pinned key, a record signed by a key that was never pinned — registered honestly, and
  does `requiredWitnesses` bound them the way the study claims?
- R1-1: does the bytecode-cache comparison cover what it needs to, and is scoping it to
  `importlib.util.cache_from_source` a sound choice rather than a way of making the test
  pass?
- R1-3: can the bound digest mapping still differ from the stamped bytes on any path?
- R1-6: do the five pair invariants hold, and does a non-validating pair really make the
  attempt pipeline-invalid?
- R1-9 / R1-10 / R1-11: structured fields published; recency as configured policy with both
  arms; precedence independent of retained order.

Then: any NEW material problem the revision introduced is a finding R2-<n> with severity
BLOCKER / MAJOR / MINOR, file/section, a description of the failure mode, and a concrete
fix. Please do not manufacture findings; a clean confirmation is a real outcome.

PART 2 — the reviewer holdout set. Author 6 to 10 cells, yours alone, to be committed
verbatim with attribution into harness/MATRIX-HOLDOUT.json and never executed before the
freeze. The maintainer implements construction hooks that the scorer drives inside the
attempt, and your registered expectations are what the first-ever execution is scored
against. Requirements:
- Constructible from the registered apparatus alone: the pinned Study 016 registry writer
  (build_registry / build_checkpoint / snapshot_of with any events, positions, keys), this
  study's witness/sighting.py (any witness key, head, position; any witness configuration
  with witnessKeys / minimumSightings / requiredWitnesses / recencyPolicy), synthetic
  commitment tuples, and deterministic byte edits of retained files. No network, no clock,
  no new upstream seams.
- Each cell: id (h01, h02, ...), category, variant (none/registry/config/sightings/
  tampered), role, attackerCapability (none/tamper/authority-key/witness-key/delivery —
  the registered vocabulary for which inputs the construction requires), registeredAbsences
  (normally []), a construction description precise enough to implement mechanically, the
  expected outcome for BOTH layers (currency/witness — outcome strings exactly as
  MATRIX.json uses them, currency codes from Study 016's registry/SPEC.md, witness codes
  from witness/SPEC.md section 3), and a one-line rationale.
- At least one all-pass control that would show the registered detections are not
  brittleness, in the spirit of Study 016's h10.
- Please prioritise the areas you judge least settled: the association loop, the
  enforcement clauses interacting (minimumSightings vs requiredWitnesses vs series
  scoping), the precedence rule, the structured fields, the two recency arms, and the
  boundary between the two layers.

Output, exactly:
- "## Confirmation" — the fifteen resolution lines.
- "## New findings" — R2-<n> findings, or the line "none".
- "## Holdout set (authored by the round-2 reviewer)" — a single JSON code block:
  {"reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2", "cells": [ ... ]}
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
