# Round-3 prompt (verbatim)

```
You are the interim-review-regime reviewer for Study 016 in
judgment-pack-evaluator-experiments, round 3 (the same different-vendor reviewer as
rounds 1 and 2). This is a confirmation pass. Your round-2 verdict was `freezable after
listed fixes`: 7 partially-resolved residuals, one new minor (R2-1), and you authored the
10-cell holdout stratum. The maintainer closed every residual, accepted R2-1, and landed
your cells verbatim; dispositions are in PREREG-REVIEW.md (Round 2 section).

The study, revised again, at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt016/studies/016-policy-currency-anchor/

Study 014's frozen tree is one directory up; spec RFC 0011 and its review record at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/spec-main/rfcs/

Toolchain (read-only sandbox; execution optional):
  JPACK_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/jpack-0.17.0/jpack
  OWP_SOURCE=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/OpenWorkProof
  Python venv: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/venv/bin/python

For each residual, verified against the current files (not the disposition prose), one
line each — RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED with the file you checked:

- R1-1: harness/upstream014.py — absolute-path loading only, no sys.path additions, no
  bare imports of 014 names, collision refusal, per-load verification.
- R1-2: no stale identifiers or rollback claims outside OWP's own tool name and
  explanatory "not a rollback" prose (PREREGISTRATION.md, README.md,
  harness/build_fixtures.py).
- R1-3: registry/verify_currency.py parses trust-configuration BYTES strictly at the
  layer; harness/run_verify.py passes raw bytes; duplicate-member configuration refuses.
- R1-4: harness/score.py _fork_structure — attestations verified under the enforced
  pinned authority key; no reliance on unauthenticated key-id labels.
- R1-7: harness/tests/test_registry.py — exact-at-limit vectors for all three limits,
  one-past siblings refusing.
- R1-11: the holdout machinery — build_fixtures.HoldoutAttemptContext gating (impossible
  to execute while any freeze pin is null), in-attempt construction, stamps and
  post-adjudication integrity, separate reporting; the empty-stratum refusal; and that
  NOTHING has executed the stratum (pilots' RESULTS.json holdout member is null; no
  holdout bytes under fixtures/).
- R1-12: single-read PINS (marker hashes the same bytes that are parsed);
  harness/PINS.json prose accurate.
- R1-15: README.md reliance and membership-at-snapshot wording.
- R2-1: PREREGISTRATION.md §1a says 22.
- Holdout landing: harness/MATRIX-HOLDOUT.json carries your ten cells VERBATIM with
  attribution — diff them against your round-2 output; any alteration of your registered
  expectations or constructions is a finding of the highest severity.

Then: any NEW material problem the revision introduced is a finding R3-<n> with severity
BLOCKER / MAJOR / MINOR, file/section, failure mode, concrete fix. Materiality bar: this
is a study preregistration about to freeze; do not manufacture findings, and weigh
whether a residual is load-bearing for the registered claims. A clean confirmation is a
real outcome.

Output, exactly:
- "## Confirmation" — the ten resolution lines above.
- "## New findings" — R3-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
