# Round 3 prompt — confirmation pass

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-3 cross-vendor reviewer for Study 014
(`studies/014-openworkproof-binding/`). You wrote rounds 1 and 2 (verbatim under
`reviews/`); the maintainer implemented the round-2 closures (commit "Study 014 round 2:
the freeze gets an anchor, the holdout gets a path, and the reviewer gets the pen"). This
is a confirmation pass, not a fresh audit — but anything you find is still a finding.

1. For each round-2 finding R2-1..R2-9: RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED with
   a one-line reason, verified against the tree (not the narration). Priorities: is the
   freeze anchor (R2-1) genuinely outside the regenerable set — walk the exact chain from
   a hypothetical post-freeze code edit to the refusal; can the holdout path (R2-2)
   adjudicate correctly post-freeze while remaining refused now — and is
   `harness/MATRIX-HOLDOUT.json` still byte-identical to the block in your round-2 output
   (verify, don't trust); does the verdict-pair validation (R2-5) close the laundering you
   found; are the terminal-record paths (R2-6) actually exhaustive.
2. Verify your eight holdout cells landed verbatim and remain unexecuted (no
   `fixtures/holdout/` directory, no holdout entries in any pilot). Confirm the
   constructibility-finding rule in PREREGISTRATION §1a is one you accept for cells whose
   construction upstream refuses (h02 may be such a cell).
3. Read the d18 retry-probe result (MATRIX note + PREREGISTRATION §4a + the probe in
   `harness/tests/test_upstream_probes.py`) and say whether the recorded dead-end is
   correctly attributed.
4. State what remains between this draft and a freeze-ready PR, as a concrete checklist
   (the maintainer expects items like: fill the null pins at the freeze commit, remove
   DRAFT banners, name the freeze commit and the governing command, designate the primary
   attempt root). Add anything you require beyond that.
5. One-line verdict: `freezable as written` / `freezable after listed fixes` /
   `not freezable as written`.

Findings only; cite paths you read.
