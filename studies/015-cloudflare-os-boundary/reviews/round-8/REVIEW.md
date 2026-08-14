# Round 8 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit e78ff3e. Verdict: DO-NOT-FREEZE
(R7-3/4/5 RESOLVED; R6-1r/R7-1/R7-2 functionally closed with named residue; new R8-1..3
BLOCKER, R8-4 MINOR; h08 ruling: the note stands, DEVIATIONS-only disposition).
Dispositions: PREREG-REVIEW.md round-8 section; fixes landed as 99b5832.

---

R6-1r — NOT RESOLVED: retryability assertions were removed, but source-reachability/effect-causation language remains or was reintroduced in `PREREGISTRATION.md:438-446`, `adapter/SPEC.md:537,595-650`, and `test_reachability.py:372-393`.

R7-1 — NOT RESOLVED: pending+rejected, the `rejected` report state, zero-cell survey, and completed-rejection enforcement all work, but `verify.py:92-93` still falsely says inner and outer rejection occur “in the same transaction,” contradicting the cited crash window.

R7-2 — NOT RESOLVED: lone gatekeeper `1.0`/`1e0` now refuse on both sides and missing source access returns `unavailable`; however, witness `pass:1.0` and `pass:1e0` produce binding `retained-store-unreadable` while upstream passes with both checks engaged.

R7-3 — RESOLVED: `[0-9]` plus `fullmatch()` makes valid/Unicode-digit/trailing-LF acceptance `[true,false,false]` in both runtimes.

R7-4 — RESOLVED: the engaged coherent empty witness passes with `AutoApprovalDrainer` engaged.

R7-5 — RESOLVED: absent, empty, and foreign-scope tags refuse through full commitment-derived comparison; b04/h04 remain outside that inventory and their registered projections are unchanged.

h08 RULING — The note must stand and be dispositioned only in `DEVIATIONS.md`. It is reviewer prose promised verbatim, not migration-authored prose; changing the working copy would violate `PREREGISTRATION.md:77-84`, the round-1 authorship instruction, and the enforced note-equality test.

R8-1 — BLOCKER — Offending: the source-reachability and “nothing took effect” passages named under R6-1r. Contradiction: §9 disclaims source-reachable histories, effect causation, and closed inventory. Proposed fix: describe only locally registered tuple compatibility and retained attestations, then sweep all living round-7 prose.

R8-2 — BLOCKER — Offending: `adapter/verify.py:92-93`. Contradiction: `action-store.ts:209` persists rejection before the awaited outer update at `overseer.ts:7727-7732`. Proposed fix: replace “same transaction” with the actual store-before-outer sequence.

R8-3 — BLOCKER — Offending: `ceremony.ts:472` sorts `witness.pass` without validating it via `platformId`. Contradiction: SPEC calls it a pass identity and Python enforces the lexical rule. Proposed fix: validate every witness identity before replay and regress lone `pass:1.0` and `pass:1e0`.

R8-4 — MINOR — Offending: `verify.py:169` says “R7-5 … filed R7-3.” Proposed fix: correct it to the R6-5 residue/R7-3 reference.

do not freeze

The otherwise strong evidence holds: the suite passed 157 tests, the source pin and both trees are clean, all 35 fixtures contain zero pending+rejected pairs and zero `execution:"rejected"` reports, both registries’ `{id, expected}` projections match `dc4bc91`, no fixture bytes changed since `3730d0b`, and the authored holdout remains byte-identical. The three blocker residues nevertheless leave one real cross-layer acceptance divergence and two governing source accounts internally false.

CODEX-015-R8-DONE
