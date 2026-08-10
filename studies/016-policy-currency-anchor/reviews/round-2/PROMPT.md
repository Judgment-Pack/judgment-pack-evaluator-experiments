# Round-2 prompt (verbatim)

```
You are the interim-review-regime reviewer for Study 016 in
judgment-pack-evaluator-experiments, round 2 (the same different-vendor reviewer as round
1). You wrote round 1; its verbatim findings R1-1..R1-15 are in
reviews/round-1/REVIEW.md and the maintainer's dispositions are in PREREG-REVIEW.md. The
maintainer accepted all fifteen (several with the narrowed remedy your finding offered)
and revised the study. This round has two jobs: a confirmation pass, and — per your own
closing line in round 1 — authoring the reviewer holdout stratum.

The study under review, revised, at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt016/studies/016-policy-currency-anchor/

Study 014's frozen tree is one directory up; spec RFC 0011 and its review record are at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/spec-main/rfcs/

Toolchain, if you want to execute anything (read-only sandbox; optional):
  JPACK_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/jpack-0.17.0/jpack
  OWP_SOURCE=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/OpenWorkProof
  Python venv: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/venv/bin/python

PART 1 — confirmation. For each of R1-1..R1-15: RESOLVED / PARTIALLY RESOLVED / NOT
RESOLVED, verified against the current files (not the disposition prose), one line each
with the file you checked. Priorities:
- R1-1: does harness/upstream014.py now verify each LOADED module's resolved origin and
  bytes on every load, and refuse pre-existing sys.modules entries?
- R1-2: is the remint row descriptive, renamed, and is every rollback claim gone?
- R1-3: run registry/verify_currency.py through your round-1 attack inputs if you wish —
  duplicate members, signed version-2 attestation payload, malformed minimumHeadPin,
  non-canonicalizable values, boolean integers. Does everything land in the registered
  vocabulary?
- R1-4: is the fork validated structurally from bytes in harness/score.py, is the
  impossibility wording narrowed everywhere, and is the stateful arm registered?
- R1-6: is signer attribution honest now (one code; label in detail only)?
- R1-9: is the byte-identical endpoint pair collapsed to one adjudicated cell with two
  registered readings?
- R1-11/R1-12: empty-holdout refusal; pinsRawSha256 in the marker and every terminal
  record; SystemExit terminal-recorded.

Then: any NEW material problem the revision introduced is a finding R2-<n> with severity
BLOCKER / MAJOR / MINOR, file/section, failure mode, concrete fix. Do not manufacture
findings; a clean confirmation is a real outcome.

PART 2 — the reviewer holdout stratum. Author 6 to 10 cells, yours alone. They will be
committed verbatim with attribution into harness/MATRIX-HOLDOUT.json, never executed
before the freeze; the maintainer implements construction hooks the scorer drives inside
the attempt (014's section 1a machinery), and your registered expectations are what the
first-ever execution is scored against. Requirements:

- Each cell must be constructible from the study's registered apparatus alone: the five
  built chains (baseline, successor, remint, neg-replay, neg-owp), the registry writer
  (registry/checkpoint.py: build_checkpoint/build_registry/snapshot_of with any events,
  positions, and either study key), trust configurations (any seriesId, pins,
  minimumHeadPin), and deterministic byte edits of retained artifacts. No new upstream
  seams, no network, no clock.
- Each cell: an id (h01, h02, ...), category, variant (registry/config/chain/artifact/
  tampered/resigned/none), role, attackerCapability (none/tamper/authority-key/full-keys),
  registeredAbsences (normally []), a construction description precise enough to
  implement mechanically with the tools above, the expected outcome for ALL FOUR layers
  (owp/binding/replay/currency — outcome strings exactly as MATRIX.json uses them, and
  currency codes exactly from registry/SPEC.md section 4), and a one-line rationale.
- At least one cell must be a holdout control in the spirit of 014's h08: a construction
  expected to pass everything, proving the detections are not brittleness.
- Aim your cells where you expect the apparatus is weakest: the first-failure ordering,
  the fold's lifecycle rules, the interplay between the currency layer and the three
  chain layers, the trust-configuration schema, the limits, the identity/pair machinery.
  A cell whose registered expectation turns out wrong at first execution is exactly what
  the stratum exists to surface.

Output, exactly:
- "## Confirmation" — the fifteen resolution lines.
- "## New findings" — R2-<n> findings, or the line "none".
- "## Holdout stratum (authored by the round-2 reviewer)" — a single JSON code block:
  {"reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2", "cells": [ ... ]}
  with cells in the exact per-cell schema above.
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every confirmation and finding.
```
