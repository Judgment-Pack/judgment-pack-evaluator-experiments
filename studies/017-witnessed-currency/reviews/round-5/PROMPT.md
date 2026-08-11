# Round-5 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 5 — the same different-vendor
reviewer as rounds 1 to 4. This is a confirmation pass over the round-4 closures.

Your round-4 verdict was `freezable after listed fixes`: one new BLOCKER (R4-1, the
freeze-pin gating of the holdout), R1-9 NOT RESOLVED (the detection matrix's header/row
mismatch), and the R1-1 prose residual. The maintainer accepted all of them. Dispositions
are in PREREG-REVIEW.md; verbatim records in reviews/round-1/ through reviews/round-4/.

The study, revised, at:
  <study worktree>/

The interpreter at <scratchpad>/venv/bin/python runs the suite offline.

Verify against the current files, one line each, citing the file:
- R4-1: does `--include-holdout` now refuse while ANY freeze pin is null, naming the
  offenders? Is a missing or incompletely covering evidence map terminal? Is the evidence
  digest carried in the holdout context and re-verified there? Does the builder's own gate
  enumerate every pin? Is the one-null-pin-at-a-time regression correct — does it actually
  exercise each pin rather than passing for an unrelated reason?
- R1-9: does the published detection matrix now carry the three evidence values in
  well-formed rows, and does the regression assert both column shape and content?
- R1-1 residual: are all three statements narrowed?

Then: any NEW material problem is a finding R5-<n> with severity, file/section, failure
mode, concrete fix. Please do not manufacture findings; a clean confirmation is a real
outcome. If you judge the preregistration ready to freeze, say so plainly — and if you do
not, say exactly what remains.

Output, exactly:
- "## Confirmation" — the resolution lines.
- "## New findings" — R5-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
