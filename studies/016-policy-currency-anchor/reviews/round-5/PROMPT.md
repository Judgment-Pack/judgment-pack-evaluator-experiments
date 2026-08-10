# Round-5 prompt (verbatim)

```
You are the interim-review-regime reviewer for Study 016 in
judgment-pack-evaluator-experiments, round 5 (the same different-vendor reviewer as
rounds 1-4). This is a final confirmation pass over the two round-4 closures. Your
round-4 verdict was `freezable after listed fixes`: R1-15 (one remaining positive "no
longer in force" in README.md) and R4-1 (the builder docstring's four-chain inventory
omitting neg-replay). Dispositions in PREREG-REVIEW.md (Round 4 section).

The study at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt016/studies/016-policy-currency-anchor/

Verify against current files, one line each — RESOLVED / PARTIALLY RESOLVED / NOT
RESOLVED with the file checked:

- R1-15: README.md carries no positive "no longer in force"; the study tree's only
  remaining occurrence is the preregistration's explicit disavowal.
- R4-1: harness/build_fixtures.py's docstring inventories five chains including
  neg-replay, matching PREREGISTRATION.md.
- The whole-study manifest is fresh (harness/make_manifest.py --check exits 0).

Then: any NEW material problem is a finding R5-<n> with severity, file/section, failure
mode, concrete fix. Materiality bar: a study preregistration about to freeze; a clean
confirmation is a real outcome. Do not manufacture findings.

Output, exactly:
- "## Confirmation" — the three resolution lines.
- "## New findings" — R5-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
