# Deviations from the preregistration

Every departure from [`PREREGISTRATION.md`](PREREGISTRATION.md) is recorded here with its date and
reason. The preregistration itself is never edited after freeze. An empty table means the study ran
as preregistered.

| Date | Section | Deviation | Reason | Effect on the claim |
| --- | --- | --- | --- | --- |
| — | — | none yet | — | — |

## First prompt-arm execution (2026-08-06)

Arms A and A′ had never been run against a real model beyond a two-instance
pilot. They were run over the full 432-twin corpus on this date. Three
deviations from the registered design, all forced, all recorded before the
numbers were read:

1. **k = 1 in the first pass, superseded by k = 5.** The registered
   primary endpoint (H1, pass^k) requires k > 1; at k = 1 pass^k
   degenerates to accuracy. The first pass therefore measured secondary
   endpoints only and said so. The k = 5 run followed and is what
   `RESULTS-FIRST-PROMPT-ARMS.md` now reports.

   Two things surfaced while scoring it, both recorded because either
   could have produced a silently wrong headline:

   - The first k = 5 scoring still reported `trials per instance: 1-1` and
     a pass^k identical to accuracy. `score.py` sets k to the **minimum**
     trial count across conditions — correct for a paired comparison — and
     arm B still had only one trial, collapsing k to 1 for every arm. Arm
     B was re-run at k = 5 (37 seconds; it is deterministic) and the
     pairing then resolved correctly. Had this gone unnoticed, the k = 1
     accuracy would have been reported as the primary endpoint.
   - **Arm B's pass^k is 1.0 by construction**, because the evaluator is
     deterministic. H1 is therefore not a contest arm B can lose, and the
     +0.130 measures prompt-arm inconsistency rather than a stability win.
     The results document says so in its own section rather than leaving
     a reader to infer it.

2. **One model family, not two.** The design pools across Claude and
   Codex. No Anthropic credential was available in this environment, so
   arms A and A′ ran on the Codex backend (`gpt-5.6-sol`) only. A
   single-family result cannot stand in for the pooled endpoint, and no
   pooled claim is made.

3. **Arm B ran on `judgment-pack 0.2.0`, not the current runtime.** This
   was forced rather than chosen: `jpack 0.15.0` refuses the study's pack,
   because the pack declares `specVersion 0.1.0-draft` while the current
   evaluator implements the 0.2.0-draft contract, and JPS §11 makes the
   declared value exact. Re-declaring the pack to satisfy a newer
   evaluator would have been an edit to a study artifact mid-study, so the
   original binary was used instead — it is still published, and arm B
   reproduced its recorded result exactly. The drift itself is worth
   recording: a study artifact can fall out of its evaluator's conformance
   window while the study is still open.

## 2. The primary endpoint was first reported on the wrong population

**What happened.** The first k = 5 write-up reported "H1 passes,
B − A = +0.130 [0.076, 0.181]". The preregistration §2 registers H1 as
pass^k **on answerable instances**. The number reported was the composite
over all 432 twins, which pools the 216 answerable instances with the 216
manufactured-redaction ones. On the registered population the sign flips:
**B − A = −0.148 [−0.213, −0.088]**, McNemar p = 2.09 × 10⁻⁵ favouring A.

The post-run adversarial review caught it as its first blocker. Every
number was independently recomputed before the correction was accepted.

**Why it happened, stated plainly.** `score.py` intersects all shared twin
ids and never filters to `variant == "answerable"`. The scorer does not
enforce the registered population, and the author did not verify that the
population matched the endpoint before writing "passes". A preregistration
constrains what you may claim; it does not check that the claim was
computed on what it names. That check is manual and it was skipped.

**Consequences.** `RESULTS-FIRST-PROMPT-ARMS.md` was rewritten to lead
with the negative result. H1, H4, and H5 are all reported as not
supported. The earlier commit `a01d686` is left in history rather than
amended, so the error and its correction are both auditable.

## 3. Other departures recorded during the same review

- **The registered primary endpoint is not estimable from this execution.**
  It is defined as pooled across Claude and Codex; only Codex ran, and
  `score.py` has no cross-backend pooling operation. Everything reported
  is a Codex-only deviated analysis.
- **McNemar's test, committed in §5, is not implemented** in `score.py`,
  which provides only paired bootstrap intervals. It was computed by hand
  for the primary endpoint and reported; the omission is recorded here
  rather than left silent.
- **The shipped scorer bootstraps 432 twins independently** rather than
  resampling the 216 pair clusters. Pair-clustering the H2 interval gives
  [0.397, 0.505]; the conclusion is unchanged. Reported figures note which
  intervals are clustered.
- **`arm_b.py` can score a nonzero-exit run as a success.** It rejects a
  nonzero return code only when stdout is empty, and arm-B rows retain
  neither return code nor stderr, so the reported "0 engine refusals"
  cannot be audited from the retained JSONL. No retained envelope shows a
  refusal signal. Fixing the check and re-running the deterministic arm is
  filed as follow-up rather than performed under a result already
  corrected once.
