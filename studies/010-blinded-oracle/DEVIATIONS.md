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
prompt (`dry7`, `dry8`, 2026-08-06).

**Exact inventory of every capture made with the registered prompt**, and
what each retains — the post-run review's finding 1 corrected an earlier
claim that the pilots were "retained in full":

| Capture | Prompt | Assistant output began | Retained |
| --- | --- | --- | --- |
| `pilots/dry7` | registered | yes, seen by the operator | `completion.txt`, compiled `records/` only |
| `pilots/dry8` | registered | yes, seen by the operator | `completion.txt`, compiled `records/` only |
| the registered run | registered | yes | everything: `CALL.json`, `session.jsonl`, `context.json`, `stdout.raw`, `stderr.raw`, `completion.txt` |

Neither pilot retains a transcript, `CALL.json`, or context digests, so
their invocation provenance and independence are **operator-reported, not
transcript-verifiable**, and nothing here establishes that these three are
the exhaustive set of registered-prompt runs. `ANALYSIS.md` states the
coverage claim at that strength.

Separately, five captures were made with **trivial probe prompts** (not the
registered prompt) while validating the wrapper's configuration — two of
them, from the final fresh-`HOME` configuration, produced
`transcription/GOLDEN-CONTEXT.json`. The pre-prompt context does not
depend on the prompt, which is why it can be pinned at all; the three
registered-prompt runs above each reproduced the golden capture exactly,
which is the evidence that pinning it was sound.

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

## 2. Two attempts to edit locked files after the lock, both refused

**What happened.** Applying the post-run review's corrections, the
maintainer edited three files that the protocol lock pins:
`PREREGISTRATION.md` (§4's description of the golden capture),
`transcription/GOLDEN-CONTEXT.json` (its note), and `PREREG-REVIEW.md`
(appending the post-run review to it). `study.py validate` refused
immediately — `locked input drifted: PREREGISTRATION.md` — and all three
were reverted to their locked bytes before anything was committed.

**Why it is recorded rather than quietly fixed.** The preregistration says
it is never edited after the lock and that corrections go here. The
maintainer edited it anyway, out of habit, while writing up a review whose
whole subject was overclaiming. The lock caught it in one command. That is
the mechanism working on its author, which is the only interesting kind of
test it gets, and hiding it would make this file useless for its purpose.

**Consequences.** The post-run review lives in its own
`ADVERSARIAL-REVIEW.md`, not appended to the locked `PREREG-REVIEW.md`
(Study 009's pattern, which should have been followed from the start).
Two corrections that would have belonged in locked files are recorded
instead in `ADVERSARIAL-REVIEW.md` and here:

- `GOLDEN-CONTEXT.json`'s note and `PREREGISTRATION.md` §4 describe the
  golden capture as coming from "two independent real runs of the
  registered invocation". Those two captures used **trivial probe
  prompts**, not the registered prompt. The pre-prompt context precedes
  the prompt and does not depend on it — that is precisely why it can be
  pinned — and the three registered-prompt runs each reproduced the
  capture exactly. The claim the file makes is sound; its wording is
  imprecise, and it stays imprecise because the bytes are frozen.
