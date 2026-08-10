# Round 6 prompt — confirmation of the round-5 closures

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-6 cross-vendor reviewer for Study 014
(`studies/014-openworkproof-binding/`). You wrote rounds 1–5 (verbatim under `reviews/`);
the maintainer implemented the round-5 closures (commit "Study 014 round 5: every import
accounted for, every route gated, every stamp re-checked").

1. For each of R5-1..R5-4: RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED, tree-verified,
   one line each. Two deliberate narrowings are argued in the tree and need your explicit
   accept/reject: (a) the PEP 3147 `__pycache__` exemption in the shadow classifier
   (docstring + PREREGISTRATION §2 + a dedicated test; residual stated: a cache entry
   executed in place of the digest-checked source beside it) — the maintainer's stated
   alternative is a source-only loader for the five pinned helpers; (b) the
   attempt-context gate is structural, not cryptographic (stated in code + prereg) — it
   removes the accidental route, not a determined insider. Also note: `publish_holdout`
   remains ungated because it cannot drive a hook — accept or demand symmetry.
2. Anything new is R6-<n> with severity, weighed for materiality against what this study
   is: a deterministic offline harness whose threat model already grants the insider all
   six fixture keys.
3. One-line verdict: `freezable as written` (freezable once the freeze-PR mechanical
   items — banners, freeze-commit naming, pin filling in a non-circular order, governing
   invocation, clean freeze commit — are performed) / `freezable after listed fixes` /
   `not freezable as written`.

Findings only; cite paths you read.
