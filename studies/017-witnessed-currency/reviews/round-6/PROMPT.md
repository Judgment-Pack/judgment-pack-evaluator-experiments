# Round-6 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 6 — the same different-vendor
reviewer as rounds 1 to 5. This is a confirmation pass over the round-5 closures.

Your round-5 verdict was `freezable after listed fixes`: the R4-1 residuals (partial
evidence entries silently dropping a divergence channel; the builder leg of the gate
regression exercising only one pin), the R1-9 residual (the matrix regression checking
shape rather than content), and R5-1 (two inventories omitting the evidence map). The
maintainer accepted all of them. Dispositions are in PREREG-REVIEW.md; verbatim records in
reviews/round-1/ through reviews/round-5/.

The study, revised, at:
  <study worktree>/

The interpreter at <scratchpad>/venv/bin/python runs the suite offline.

Verify against the current files, one line each, citing the file:
- R4-1(a): does evidence validation require every registered cell, exactly the three
  fields, with correct types, and is any defect terminal? Does the regression actually
  exercise a dropped field, a wrong type, a boolean-as-integer and a missing cell?
- R4-1(b): does the builder gate now read a patchable registry, and does the regression
  null each of the six pins in turn against the builder's own gate?
- R1-9: does the regression compare every witness row's rendered triple against
  RESULTS.json, and assert every cell is rendered?
- R5-1: are both inventories now complete?

Then: any NEW material problem is a finding R6-<n> with severity, file/section, failure
mode, concrete fix. Please do not manufacture findings; a clean confirmation is a real
outcome.

This study has now had five rounds. If you judge the preregistration ready to freeze, say
so plainly. If you do not, say exactly what remains and why it is material to a
preregistration rather than to production software — the standard here is that the
registered claims are honest and the registered expectations cannot be chosen after
observation, not that the harness is flawless.

Output, exactly:
- "## Confirmation" — the resolution lines.
- "## New findings" — R6-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
