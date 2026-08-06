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
