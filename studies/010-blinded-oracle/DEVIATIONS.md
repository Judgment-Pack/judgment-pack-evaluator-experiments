# Deviations

Everything that departed from the preregistration, or that a reader needs
in order to weigh the result, recorded as it happened.

## 1. Two pilot runs of the registered prompt preceded the registered run

**What happened.** Revision 6 rewrote the authoring wrapper — a fresh
`HOME` and `CODEX_HOME`, zero retries, and the golden-context match — and
the preregistration allows exactly one authoring call with no retry. A
wrapper defect would therefore have consumed the study's single attempt.
Before the registered run, the wrapper was exercised end to end **twice**
in throwaway repositories against the real model with the registered
prompt (`dry7`, `dry8`, 2026-08-06). Both are retained in full alongside
this study's evidence.

That was the right engineering call and it paid for itself immediately:
the second rehearsal caught a Rekor upload defect — the client signs one
body and re-posts it on retry, so a lost response makes every retry
conflict with the entry it just created — which would have failed the
registered run at publication, unrecoverably. The fix (resolve a 409 to
the entry it conflicts with) is in the locked harness.

**What it costs.** The operator saw two record sets drawn from the same
prompt and model before the registered call. Both produced 16 records, all
16 policy-concordant, and both covered **all six** mutation classes with
identical per-class counts (1, 2, 1, 5, 1, 1). So at execution time the
operator had strong evidence that the registered run would also cover
every class, and therefore that E1 would resolve to `caught` whichever
index the beacon drew.

**What that does and does not damage.** It does not touch the mechanism
claims: authorship is still the model's, the publication clock is still
the log's, and the drawn index still comes from a beacon that had not
occurred when the records were published — none of which the operator's
foreknowledge can move. What it damages is §6's registration of E1 as
**uncertain**. That word was true when it was written and was no longer
fully true when the study ran. A reader should treat the registered E1
result as confirmatory rather than exploratory, and should weigh the
pilots as what they are: two additional samples, reported in
`ANALYSIS.md` beside the registered one.

**Why the study was run anyway.** The maintainer's judgment, recorded
here for the reader to disagree with: the coverage profile — which classes
independently authored records actually reach — is the finding this line
needs, and three samples of it are worth more than one. The alternative,
discarding the pilots and claiming a clean single draw, would have been
false. The alternative of re-registering with an unseen prompt would test
a prompt nobody intends to use.
