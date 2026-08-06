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

1. **k = 1 in the first pass.** The registered primary endpoint (H1,
   pass^k on answerable instances) requires k > 1; at k = 1 pass^k
   degenerates to accuracy. The first pass therefore measures only
   secondary endpoints, and `RESULTS-FIRST-PROMPT-ARMS.md` says so at the
   top rather than reporting accuracy as if it were the primary. A k = 5
   run followed.

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
