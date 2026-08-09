# AMENDMENT — RQ3: the model-mediated Arm A (registered before any model call)

**Registered by commit: this file, the prompt template inside
`harness/rq3_run.py`, the policy-prose fixtures, and the opaque handle map
are committed and pushed BEFORE the first model call; the authoring slots'
timestamps and the commit order make that verifiable. PREREGISTRATION.md is
frozen and untouched; this amendment adds RQ3's registered analysis exactly
as §RQ3 requires. Maintainer approval of the spend and the model choice
(codex `gpt-5.6-sol`, reasoning effort ultra) was given explicitly.**

## Pins

- Decider: codex-cli 0.145.0, binary sha256
  `a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14`,
  model `gpt-5.6-sol`, `model_reasoning_effort="ultra"`, sandbox read-only,
  `--skip-git-repo-check`, executed in an EMPTY temporary working directory
  per call — the model can read no repository bytes; opacity is mechanical.
  No sampling parameters beyond effort are exposed by the CLI; run-to-run
  variation is part of the measurement.
- Prompt template: embedded in `harness/rq3_run.py` (manifest-bound);
  sha256 of the template string:
  `a72bcd29712a6e33e927b7b0ac4254b0bf02ea99d0957d7d79e8779ad708d401`.
- Policy prose fixtures (authored by the maintainer as faithful renderings
  of the six pinned packs — rendering fidelity is a registered threat, and
  the prose is quoted verbatim to the model):
  - direct.md: `2aee3156fb200073d70b3b7fa60f9fe62d0e1212bf00482dc023f3dea3c6a180`
  - fee.md: `53357445cb2258cf7958d98f79ddef563909f7548befaac17c67adfa45040c18`
  - partial.md: `5d2541700c3e176394ebffeb5ee3909cdab1b4ab217fa8913431f0e26fa43c56`
  - triage.md: `d9bcff0f367d50db046d9db7d97e5666019b966aea4a6bdb02a1cd6e9d178447`
  - xforce.md: `797cca886ad1f546c6381a6b2ff2ee8b2e03a35a50bb3d6a47d7c19f2e508bbe`
  - xsuppress.md: `7cb701f10a26950b8b9f41038d17b466b5f9d95af70ff366a8cbe9f9e2c9b510`
- Opaque handles: `scenarios/rq3/HANDLES.json`, sha256
  `d3cb77b6d5d80da1918165471b04645f15d8c045f0da0b25a36878e01fb0c6ad` — handles are `case-NN` in
  sha256(case-id) order; the model never sees case ids or caseType labels
  (frozen-prereg requirement).
- Repetitions: exactly 3 per case, 21 cases, 63 calls. Slots are immutable;
  a resumed calls stage skips only completed slots.

## Two-stage design

Model calls happen OUTSIDE Forge with full retention per slot (PROMPT.md,
CALL.json with argv + exit codes + prompt digest, last-message.txt,
stdout.raw, stderr.raw, decision.json). Forge then runs cohort2.yaml with
`agents/arm_a_codex.py` deterministically replaying the retained decisions —
same 21 scenarios, same fixtures, same deterministic scorers as every other
arm. `agents/shell.py` gained one additive branch (a decider error abstains
via the evaluation-error path); RQ1 is closed, its primary attempt untouched.

## Failure rules

One retry on a nonzero codex exit (transport). Non-JSON or schema-invalid
output is model behavior: recorded as `model-failure`, no retry, and counted
as disagreement and as its own tally (intent to treat — no slot is excluded).

## Registered endpoints (descriptive; no efficacy claim is available)

Per repetition and pooled: (1) **agreement** with the pinned evaluator's
golden disposition on (kind, outcomeId, sorted reasons, handoff.state) —
`triggeredBy` and the configured target are excluded from primary agreement;
(2) **target agreement** as a separate secondary count; (3) **false
approvals** (protected tool fired where the registered expected action is
not execute); (4) correct abstention and correct handoff counts;
(5) model-failure count. Secondary: exact Clopper–Pearson 95% CI on pooled
agreement over 63 trials, intent-to-treat. Reference: Arm B's primary
attempt is 21/21 by construction (it IS the evaluator). Cells of prior
interest, stated before the calls: f01 (conflict at the exact threshold),
f02 (decimal-scale), f05 (JSON-number → undecidable), t04/t09
(unknown-vs-absent evidence), p02 (blocked with no configured destination —
the sharpest silent-approval risk).

## Disclosures

The RQ3 model vendor is the same vendor as the study's cross-vendor
preregistration reviewer (three rounds, retained). Those are different
roles — the reviewer audited the protocol, the model is the system under
test — but the coincidence is disclosed, and no amendment-specific review
round was sought from that vendor for exactly this reason; the amendment's
reviewability rests on this registration preceding all calls, byte-pinned.
The policy prose was authored by the maintainer with Claude's assistance
(the implementation assistant), which is the other side of the same
disclosure. Neither vendor sits in the scoring path: all scoring is
deterministic and golden-referenced.

## What RQ3 cannot show (restating the frozen non-claims)

No efficacy, no model ranking, no generalization beyond these 21 cases,
these prose renderings, this one model at this one effort on these days.
The endpoint is agreement with the pinned evaluator, not correctness.
