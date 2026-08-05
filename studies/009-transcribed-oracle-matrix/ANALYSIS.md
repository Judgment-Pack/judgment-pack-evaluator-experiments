# Analysis — read this before the numbers

**Every registered prediction hit, and that is the weakest fact about this
study.** The preregistration's own dependency map (§9) says why: given the
`validate`-asserted patch binding, the complete disposition tables, and a
faithful pipeline, E2's and E3's mismatch sets are *entailed* by the fixture
construction. The endpoints could only have failed if the pipeline were
unfaithful — a gate defect, an acquisition defect, a table error, an
evaluator surprise. So what the clean run establishes is exactly and only:

1. **The pipeline is faithful end to end.** Twelve records went through
   attested acquisition (one session, recomputed argument digests, artifact
   bytes canonically equal to the frozen records), projection-normal-form
   derivation, complete-row admission (every emitted row byte-equal to its
   reconstruction from the verified artifact), the pinned runtime's own
   matrix comparison on both CLI and MCP surfaces — and nothing leaked,
   drifted, or was reinterpreted anywhere.
2. **The witness exists.** On identical facts, the expectation stream bound
   to the verified record artifacts surfaced the planted encoding defect
   (three boundary rows mismatching under D, exactly as registered) that the
   evaluator-copied stream structurally could not (P-A: the circular arm
   reported a complete, zero-mismatch run over the same defective pack).
3. **The suite can fail.** Both calibration controls mismatched under both
   packs, exactly as registered — a suite that cannot fail is not a suite.

What it does not establish is everything §11 lists: nothing about real
recorded human decisions, nothing about unknown defects, no rates, one
constructed defect chosen with full knowledge of both oracles. E2 minus its
entailment is evidence about the *mechanism*, not about discovery — the
discovery question is Study 010's, registered in §1.

One deviation occurred (DEVIATIONS.md §1): attempt 1 crashed on a harness
module-shadowing defect before any evaluation, the fix was re-frozen, and
attempt 2 — the first to reach `DONE` — is the primary scored here. The
crashed attempt is retained.

The E5 leg is worth one sentence of its own: the suite ran over the MCP
`experimental_test_packs` surface with a payload equal to the CLI's modulo
the registered field list — the consumer loop runtime issue #74 shipped for
this line, closed by the pipeline it was shipped for.
