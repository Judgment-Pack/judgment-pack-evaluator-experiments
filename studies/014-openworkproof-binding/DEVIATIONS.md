# Deviations — Study 014

Deviations from the frozen preregistration land here with a reason and a date — never by
editing the preregistration, the registered matrices, or the adapter SPEC. The one entry
below is not a preregistration deviation: the registration held, and a post-run analysis
sentence had drifted from it. It is recorded here because corrections are made visibly, not
silently.

## 2026-08-10 — ANALYSIS.md corrected to match the frozen registration

`ANALYSIS.md`'s "Detection ownership" section stated that "the two registered
expected-undetected cells (e18 currency, e22 policy rollback) passed all layers." That
sentence contradicted the frozen artifacts it summarizes, in two ways:

- **e18 is not a cell.** It was removed from the matrix during round 3 of the pre-freeze
  review (`PREREG-REVIEW.md`, disposition R1-10) and recorded as an analytic limitation in
  `PREREGISTRATION.md` §4c, because it has no fixture distinct from baseline — currency is
  not observable in a retained chain. Nothing named e18 was registered or scored, so
  describing it as a "registered cell that passed all layers" was wrong.
- **e22 is a descriptive cell, not an endpoint.** `e22-workorder-rollback` carries role
  `descriptive` and `registeredUndetected: true`; it passed all layers as registered, but it
  is excluded from the R1 endpoint and is not an "expected-undetected endpoint cell."

The frozen preregistration, `MATRIX.json`, `MATRIX-HOLDOUT.json`, `adapter/SPEC.md`, and the
primary-attempt results were all correct; only the post-run `ANALYSIS.md` prose drifted from
them. The sentence is corrected in place — e22 described accurately, e18 named as the §4c
analytic limitation — with a pointer to this entry. No registered artifact changes, and R1's
verdict ("R1 holds" in both strata) is unaffected. Found during preparation of spec RFC 0011,
whose cross-vendor review flagged the sentence.
