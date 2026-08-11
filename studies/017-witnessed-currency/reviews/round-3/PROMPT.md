# Round-3 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for Study 017 (witnessed currency) in the
judgment-pack-evaluator-experiments repository, round 3 — the same different-vendor
reviewer as rounds 1 and 2. This is a confirmation pass.

Your round-2 verdict was `freezable after listed fixes`: one new BLOCKER (R2-1, the
series-scoping case you reproduced), one new MINOR (R2-2), and nine partially-resolved
residuals from round 1. The maintainer accepted all of them, reproduced R2-1 locally
before fixing it, and landed your nine holdout cells verbatim with their construction
machinery. The dispositions are in PREREG-REVIEW.md; the verbatim records are in
reviews/round-1/ and reviews/round-2/.

The study, revised, at:
  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt017/studies/017-witnessed-currency/

Study 016's frozen tree is one directory up. The interpreter at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/venv/bin/python runs the suite
offline.

PART 1 — confirmation, one line each, verified against the current files rather than the
disposition prose, citing the file you checked:
- R2-1: is attribution for enforcement now scoped to same-series records everywhere it
  matters? Re-run your case. Check whether any other path lets a record outside the
  configured series influence an outcome.
- R2-2 and the R1-8 residual: are the cell count and every identifier in the governing
  document consistent with the pinned 18-cell matrix?
- R1-1 residual: does the bootstrap actually precede the study and third-party imports,
  and are unchecked-hash caches now compared? Is `__main__` genuinely exempt?
- R1-2 residual: is the imported-module origin check sound, and is the undigested-contents
  limitation stated honestly rather than claimed closed?
- R1-3 residual: can the bound mapping still be mutated?
- R1-6 residual: are cross-cell series equality and the real floor test correct?
- R1-9 residual: are the structured fields registered, adjudicated as their own divergence
  channel, and published?
- R1-13 and R1-15 residuals: label mutation regression present; the registered SPEC wording
  narrowed.
- The holdout landing: are your nine cells byte-identical to what you authored in round 2,
  with attribution? Any alteration of your registered expectations or constructions is a
  finding of the highest severity. Is the machinery genuinely unable to run before the
  freeze, and is the stratum still unexecuted (the pilots' holdout member null, no holdout
  bytes under fixtures/)?

PART 2 — please also sanity-check the construction hooks the maintainer wrote for your
cells against your registered constructions: for each of h01..h09, does the implemented
hook build what your construction text describes? A hook that builds something else would
make your registered expectation unfalsifiable, so mismatches are material findings. You
may reason from the code alone; do not execute the stratum.

Then: any NEW material problem the revision introduced is a finding R3-<n> with severity
BLOCKER / MAJOR / MINOR, file/section, failure mode, concrete fix. Please do not
manufacture findings; a clean confirmation is a real outcome.

Output, exactly:
- "## Confirmation" — the resolution lines.
- "## Hook check" — one line per holdout cell h01..h09: MATCHES / MISMATCH with what differs.
- "## New findings" — R3-<n> findings, or the line "none".
- One line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
