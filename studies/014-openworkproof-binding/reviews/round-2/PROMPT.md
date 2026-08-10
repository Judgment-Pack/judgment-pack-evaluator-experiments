# Round 2 prompt — disposition verification and holdout authorship

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-2 cross-vendor adversarial reviewer for Study 014
(`studies/014-openworkproof-binding/`). You wrote round 1 (verbatim in
`reviews/round-1/REVIEW.md`); the maintainer dispositioned all fourteen findings in
`PREREG-REVIEW.md` and implemented the rework (commit "Study 014 round 1: the chains go
through the real executor, and the ceremony stops trusting its own marker"). Your job now
has three parts, in order of importance.

## Part 1 — verify the dispositions landed as described

For each of R1-1..R1-14: read the disposition's Action column, then verify against the
current tree that it is actually true — not narrated. Attack the fixes the way you
attacked the original: e.g. does the executor path (R1-1) really use
`repo_tools.initialize_candidate_workspace` / `apply_patch_in_candidate_workspace` with
executor-produced evidence as the oracle, or is there still a fabricated seam? Does the
exact-set totality rule (R1-2) really make an unmarked `owp.apply_patch` fatal for a
null-action commitment — check `adapter/verify.py` and the `c15`/`d18` fixtures. Are the
pin/manifest hard-fails (R1-4) reachable before any adjudication in `score.py`, and can
`STUDY-MANIFEST.sha256` be regenerated to launder a drift? Is the byte-level JCS rule
(R1-8) enforced on BOTH the objective and the retained commitment? Do the per-code
reachability tests (R1-13) actually pin first-failure ordering? Mark each finding
RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED with a one-line reason; new defects you find
in the reworked code are new findings R2-<n> with severity.

Note the maintainer's recorded deviations in the round-1 rework (PREREG-REVIEW.md and
the commit message): `d18` is registered at `{owp: fail, binding:
fail:action-map-violation}` because upstream refuses a coherently-published second active
patch (three named refusal sites) — judge whether that registration is honest and whether
the deferred retry-episode route should be demanded before freeze.

## Part 2 — author the holdout stratum (this is the postdictivity remedy you demanded)

`harness/MATRIX-HOLDOUT.json` is an empty scaffold. Author 4–8 holdout cells, in the
exact cell schema of `harness/MATRIX.json` (id, category, variant, role, attackerCapability,
registeredAbsences, construction, expected {owp, binding, replay}, note), under these rules:

- Your cells, your expectations — the maintainer commits them VERBATIM with attribution
  and implements any builder hook they need WITHOUT executing them; the scorer's
  `--include-holdout` stays mechanically refused until the freeze; first execution is
  post-freeze and primary.
- Express constructions in terms of the transforms the builder already performs (read
  `harness/build_fixtures.py` and `harness/owpflow.py` for the vocabulary: artifact edits,
  tampered JSON transforms, resigned rebuilds with fixture keys, cross-execution swaps,
  commitment-field forgeries) or as precise byte-level transforms a maintainer can
  implement mechanically. Avoid constructions upstream refuses to publish (see the
  constructibility findings) unless the post-hoc tampered form is what you intend.
- Aim where the locked replication is weakest: combinations the maintainer did not
  register, the boundary between binding codes, the null-action/totality edges, the JCS
  byte rule, replay-tuple fields, or anything you suspect the implemented ceremony gets
  wrong. At least one cell should be one you genuinely expect might diverge from the
  maintainer's implementation. Include one holdout negative control if you see value.
- If you believe a registered code boundary is ambiguous for your cell, say what you
  expect AND what the ambiguity is — a holdout that exposes a specification gap is a
  finding, not a mistake.
- Output the complete MATRIX-HOLDOUT.json content (valid JSON) in a fenced block, with an
  attribution note naming reviewer tool/model/round.

## Part 3 — verdict

Answer: does the round-1 disposition set close the blockers? Is the study freezable once
your holdout cells land unexecuted and any Part-1 residuals close? One line:
`freezable as written` / `freezable after listed fixes` / `not freezable as written`.

Findings only; verify every claim against paths you actually read.
