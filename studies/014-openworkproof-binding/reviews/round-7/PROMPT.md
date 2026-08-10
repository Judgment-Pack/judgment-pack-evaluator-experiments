# Round 7 prompt — confirmation of the post-round-6 pin fix

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-7 cross-vendor reviewer for Study 014
(`studies/014-openworkproof-binding/`). Round 6 closed `freezable as written`. After it,
CI exposed one defect the maintainer fixed and disclosed (commit "Study 014: the
dependency pin names the set, not the machine"): the `pipFreezeSha256` pin hashed raw
`pip freeze` output — which embeds the OpenWorkProof install path and the test-tool
roster — so pin enforcement could only pass on the machine that minted it. It is now
`lockedDependencyDigest`: the hash-checked lockfile's packages resolved to
`name==version` through `importlib.metadata` in the running interpreter.

This is a single-change confirmation pass:

1. Verify the change is exactly what is claimed and nothing more: diff-read
   `harness/score.py` (`locked_dependency_digest`, `canonical_dependency_name`, the
   `pin_problems` member rename), `harness/PINS.json` (member rename + note), and the two
   preregistration wording updates. Confirm no registered cell, expectation, schema,
   verdict code, ceremony step, fixture byte, or holdout byte changed
   (`harness/MATRIX-HOLDOUT.json` must still be sha256 `3668d677…`).
2. Judge the computation: does the locked-set digest still catch every drift that
   matters (a locked package missing, at a different version), and is anything real lost
   versus the freeze hash (path and tool-roster sensitivity being the discarded parts)?
   Is the PEP 503 normalization correct? Any laundering path introduced?
3. Anything material is R7-<n> with severity.
4. One-line verdict: `freezable as written` / `freezable after listed fixes` /
   `not freezable as written`.

Findings only; cite paths you read.
