# Round 5 prompt — confirmation of the round-4 closures

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-5 cross-vendor reviewer for Study 014
(`studies/014-openworkproof-binding/`). You wrote rounds 1–4 (verbatim under `reviews/`);
the maintainer implemented the round-4 closures (commit "Study 014 round 4: the holdout
binds to its attempt, and a refusal must come from upstream's own frame").

1. For each of R4-1..R4-5: RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED, tree-verified,
   one line each. Priorities: does the shadow-import guard actually cover the enumeration
   git produces (untracked without exclude-standard; directory-shaped entries), and is the
   post-import origin check anchored to importlib.metadata rather than sys.path? Is the
   attempt-local holdout subtree genuinely immutable and its digests genuinely stamped?
   Can any route still reach the hooks outside the scorer's attempt machinery? Is the
   upstream-frame refusal rule sound (frame file inside the installed package), and do
   interruptions now reach the terminal-record-and-reraise path? Verify h-hooks remain
   unexecuted and `harness/MATRIX-HOLDOUT.json` byte-identical.
2. Anything new you find is R5-<n> with severity — but weigh materiality: this study
   freezes a deterministic offline harness, not a production service.
3. One-line verdict: `freezable as written` (freezable once freeze-PR mechanical items —
   banners, freeze-commit naming, pin filling, governing invocation, clean freeze commit
   — are performed) / `freezable after listed fixes` / `not freezable as written`.

Findings only; cite paths you read.
