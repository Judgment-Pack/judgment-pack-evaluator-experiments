# Round-4 prompt (verbatim)

```
You are the interim-review-regime reviewer for Study 016 in
judgment-pack-evaluator-experiments, round 4 (the same different-vendor reviewer as
rounds 1-3). This is a confirmation pass over the round-3 closures. Your round-3 verdict
was `freezable after listed fixes`: four residuals (R1-1, R1-2, R1-7, R1-11, R1-15 —
five items) and one new MAJOR (R3-1, the stale study manifest). The maintainer closed
all of them; dispositions are in PREREG-REVIEW.md (Round 3 section).

The study at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt016/studies/016-policy-currency-anchor/

Study 014's frozen tree is one directory up; spec RFC 0011 at
.../spec-main/rfcs/. Toolchain (read-only sandbox; execution optional):
  JPACK_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/jpack-0.17.0/jpack
  OWP_SOURCE=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/OpenWorkProof
  Python venv: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/venv/bin/python

Verify against current files, one line each — RESOLVED / PARTIALLY RESOLVED / NOT
RESOLVED with the file checked:

- R1-1: harness/upstream014.py — 014 sys.path entries stripped immediately after every
  load; late sys.modules collisions refused, never overwritten.
- R1-2: harness/build_fixtures.py docstring — no stale identifiers or obsolete identity
  claims.
- R1-7: harness/tests/test_registry.py — the one-past byte vector is exactly MAX+1; the
  at-limit checkpoint vector requires pass deterministically.
- R1-11: harness/build_fixtures.py — every HOLDOUT_HOOKS callable verifies its own
  context before constructing anything.
- R1-15: README.md — no "no longer in force" outside explicit disavowal.
- R3-1: harness/STUDY-MANIFEST.sha256 fresh against the current tree
  (harness/make_manifest.py --check exits 0), and manifest freshness is a standing suite
  assertion.

Then: any NEW material problem is a finding R4-<n> with severity, file/section, failure
mode, concrete fix. Materiality bar: a study preregistration about to freeze; a clean
confirmation is a real outcome. Do not manufacture findings.

Output, exactly:
- "## Confirmation" — the six resolution lines.
- "## New findings" — R4-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
