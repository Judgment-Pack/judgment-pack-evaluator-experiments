# Round 4 prompt — final confirmation

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the round-4 cross-vendor reviewer for Study 014
(`studies/014-openworkproof-binding/`). You wrote rounds 1–3 (verbatim under `reviews/`);
the maintainer implemented the round-3 closures (commit "Study 014 round 3: the anchor
becomes a line, and constructibility becomes a record"). This is intended as the final
confirmation before the freeze PR.

1. For each unchecked item of your round-3 freeze-ready checklist items 1–9: closed or
   not, tree-verified, one line each. Priorities: walk the linearized anchor
   (manifest excludes PINS and fixtures/holdout; PINS pins the manifest; REGISTERED
   demands every freeze pin non-null) — is it initializable now, and does any laundering
   path survive? Verify the h01/h06 hooks are byte-copy + registered-edit-only WITHOUT
   executing them. Verify constructibility semantics (only captured upstream refusal is a
   finding), the attempt-scoped construction, the upstream-helper pinning, the ordering
   coverage's exemption list, and the terminal paths.
2. Confirm `harness/MATRIX-HOLDOUT.json` is still byte-identical to your round-2
   authorship and unexecuted (no fixtures/holdout, no holdout rows in any pilot).
3. Note the recorded behavior change: a refused `--include-holdout` now leaves a
   terminal-record attempt directory (marker-first rule). Acceptable?
4. If anything remains, list it as R4-<n> findings with severity. Checklist items 10–14
   (banners, freeze commit naming, pin filling, governing invocation, clean freeze
   commit) remain freeze-PR content — confirm the split or object.
5. One-line verdict: `freezable as written` (meaning: freezable once the freeze-PR
   mechanical items 10–14 are performed) / `freezable after listed fixes` /
   `not freezable as written`.

Findings only; cite paths you read.
