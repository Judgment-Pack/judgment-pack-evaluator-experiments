# Round-7 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 7 — the same different-vendor
reviewer as rounds 1 to 6. This is a confirmation pass over the round-6 closures.

Your round-6 verdict was `freezable after listed fixes`: the R4-1(a) residual
(boolean-as-integer vector), R5-1 (registeredLabelRule enumerating five pins against a
six-pin gate), and R6-1 (anchorOrder claiming the manifest covers the evidence map while
the generator omitted it). The maintainer accepted all three. Dispositions are in
PREREG-REVIEW.md; verbatim records in reviews/round-1/ through reviews/round-6/.

The study at:
  <study worktree>/

The interpreter at <scratchpad>/venv/bin/python runs the suite offline.

Verify against the current files, one line each, citing the file:
- R4-1(a): does the regression now cover a count field set to a boolean and to a negative
  integer?
- R5-1: is every inventory in the pin registry and the preregistration complete — check
  all of them, not only the ones previously named?
- R6-1: does the generator genuinely include the evidence map, is the committed manifest
  regenerated to match, and does `studyManifest.covers` describe it?

Then: any NEW material problem is a finding R7-<n> with severity, file/section, failure
mode, concrete fix.

Finally, the freeze question, asked plainly. This preregistration has been through six
rounds. Two blockers you raised were reproduced by the maintainer before being fixed; your
nine holdout cells are committed byte-for-byte with their construction hooks verified
against your own construction text. The standard for freezing a preregistration is that
the registered claims are honest, the registered expectations cannot be chosen after
observation, and the apparatus does what the document says it does — not that the harness
is free of every imperfection a further round could find. Against that standard: is this
ready to freeze? If yes, say so plainly. If no, name specifically what remains and why it
is material at that standard rather than merely improvable.

Output, exactly:
- "## Confirmation" — the resolution lines.
- "## New findings" — R7-<n> findings, or the line "none".
- "## Freeze judgement" — a short paragraph answering the question above directly.
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
