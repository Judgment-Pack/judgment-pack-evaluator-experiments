# Round-4 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 4 — the same different-vendor
reviewer as rounds 1 to 3. This is a confirmation pass.

Your round-3 verdict was `freezable after listed fixes`: one new BLOCKER (R3-1, holdout
adjudication comparing only layer outcome strings), one new MINOR (R3-2), and six
residuals. The maintainer accepted all of them and also withdrew an over-claim of their own
about what h09 guards. Dispositions are in PREREG-REVIEW.md; verbatim records in
reviews/round-1/ through reviews/round-3/.

The study, revised, at:
  <study worktree>/

The interpreter at <scratchpad>/venv/bin/python runs the suite offline.

Verify against the current files, one line each, citing the file:
- R3-1: is a structured-evidence expectation now registered for every one of your cells, in
  a file separate from your authored block (which must remain byte-for-byte), pinned at the
  freeze, and adjudicated as its own divergence channel? Are the registered values correct
  against your own construction text for each of h01..h09 — this is the part worth checking
  hardest, since a wrong value would be as bad as no value.
- R3-2: is the witness-3 claim narrowed correctly everywhere?
- R2-1 residual: is the combined regression committed and correct?
- R1-1 residual: does the prose now describe what the bootstrap actually does?
- R1-2 residual: does the dependency check refuse a missing module, a missing `__file__`,
  and a file the distribution does not own?
- R1-6 residual: does the pair floor count only schema-valid, pinned-attributed,
  same-series records?
- R1-9 residual: does the published detection matrix carry the evidence column, and does
  section 5 name the structured channels?
- R1-13 residual: does a mutation regression cover every registered seed label?

Then: any NEW material problem is a finding R4-<n> with severity, file/section, failure
mode, concrete fix. Please do not manufacture findings; a clean confirmation is a real
outcome. If you judge the preregistration ready to freeze, say so plainly.

Output, exactly:
- "## Confirmation" — the resolution lines.
- "## New findings" — R4-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
