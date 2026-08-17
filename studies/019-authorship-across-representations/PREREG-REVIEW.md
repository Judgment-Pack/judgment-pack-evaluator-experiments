# Pre-freeze review record — Study 019

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here. The freeze requires a final round verdict of exactly
`freezable as written`.

## Round 1 — 2026-08-17

- Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
  sandbox, invoked over the repository worktree with the committed prompt on stdin.
- Clean HEAD read: `bf96915` (the round-1 prompt commit; working tree clean).
- Verbatim record: [`reviews/round-1/PROMPT.md`](reviews/round-1/PROMPT.md),
  [`reviews/round-1/REVIEW.md`](reviews/round-1/REVIEW.md).
- Verdict: **DO NOT FREEZE** — 11 BLOCKER, 8 MAJOR, 1 MINOR (R1-1 … R1-20).
- Holdout: the reviewer states it is prepared to author the sealed reviewer mutant set in
  the designated later round, and authored none in this round.
- Reviewer verifications that PASSED and are part of this record: the seven two-sided
  PORTS rows recomputed and accepted (R1-20); the FM constants, equal-N critical levels,
  δ-power range, pilot-anchor power, unequal-N score formula, and the 48-step bisection
  all reproduced (R1-16); gold/grid/off-gold headline counts recomputed and confirmed
  (R1-19); references/oracle reproduce 105/105 and 2,540/2,540 outside X1 (R1-19).

### Dispositions

**Pending — no finding has been dispositioned yet.** Dispositions land here one per
finding, each citing the test that enforces its fix, before round 2 reads the tree.
(Recorded now rather than implied later, per the program's own lesson that dispositions
written as complete while residuals are live are the dominant late-round failure mode.)
