# Round 7 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit 5695211. Verdict: DO-NOT-FREEZE
(R6-4/6/7 RESOLVED; R6-1/2/3/5 NOT RESOLVED with named residue; new R7-1..3 BLOCKER,
R7-4..5 MAJOR). Dispositions: PREREG-REVIEW.md round-7 section; fixes landed as 97f550c.

---

R6-1 — NOT RESOLVED: Named sites were repaired, but living surfaces still assert causal/source-produced histories (`SPEC.md:490`, `build_fixtures.py:319-325`, PREREGISTRATION D-5), while `SPEC.md:597` and `verify.py:115` newly assert `retryable:true` despite §9 saying retryability is asserted nowhere.

R6-2 — NOT RESOLVED: The contradictory-green construction now refuses, and pending+committed is correctly admitted while every report state refuses; however, the matrix omits the symmetric pending+rejected crash window, and the five-state vocabulary cannot represent an ordinary bound rejection.

R6-3 — NOT RESOLVED: The duplicate 1/1.0 case, Boolean, −0, unsafe boundary, and Node ledger-join uniqueness behave correctly, but a lone JSON `1.0` is rejected by Python and accepted by Node; the new duplicate test masks that divergence and its Node batch omits the claimed Boolean case.

R6-4 — RESOLVED: `autoApproved:false` plus the retained witness now returns `drain-order-violation`, and key-presence validation refuses explicit-null `appliedAt`, `resolvedBy`, and `autoApproved` fields.

R6-5 — NOT RESOLVED: Calendar, sub-millisecond, overflow, equality, and pack-metadata handling are repaired, but Python’s `\d` plus `.match(...$)` accepts Unicode digits and a trailing LF that Node rejects, so the canonical grammar remains non-identical.

R6-6 — RESOLVED: The coherent-other-tool reproduction passes, b05 remains byte- and outcome-unchanged, and the tested label/tag contradiction refuses as `binding-reuse`.

R6-7 — RESOLVED: Top-level Markdown is now genuinely candidate input, disabling the exclusion adds exactly README and DEVIATIONS, and the manifest remains exactly 60 paths.

R7-1 — BLOCKER — Offending: `SPEC.md:575-607` and `verify.py:123-127` exclude pending+rejected and give rejected no report state. Contradiction: `action-store.ts:209` persists rejection before `overseer.ts:7729-7732` updates the outer row, permitting the same crash split as committed; ordinary completed rejection is also unreportable. Proposed fix: admit pending+rejected at lifecycle, add a rejected/refused report state, and regress both histories.

R7-2 — BLOCKER — Offending: Python `_platform_id()` rejects a lone parsed `1.0`, while Node `Number.isSafeInteger(JSON.parse("1.0"))` accepts it. Contradiction: SPEC promises one identity definition on both sides. Proposed fix: normalize safe integral JSON numbers consistently or enforce lexical integer tokens on both sides, with lone-number and exponent regressions.

R7-3 — BLOCKER — Offending: Python’s timestamp regex accepts Unicode decimal digits and final LF; a manual-approval construction consequently gives binding `pass` and upstream `not-engaged`. Contradiction: only exact ASCII `Date.toISOString()` form is registered. Proposed fix: use `[0-9]` and `fullmatch()`, then regress both forms.

R7-4 — MAJOR — Offending: `ceremony.ts:559-589` inserts a replay key for an empty witness and then rejects because no ledger claim key exists. Contradiction: an empty witness claims no application and can replay coherently. Proposed fix: compare per-gatekeeper lists with absence treated as empty and regress an engaged empty pass.

R7-5 — MAJOR — Offending: `verify.py:556-561` skips absent/empty tags and validates only the tool suffix, so empty or foreign-scope tags on coherent other-tool rows pass. Contradiction: pinned `actionKindFor` emits a nonempty, deployment-derived complete tag and green claims internal consistency. Proposed fix: require the tag and compare its full derived value.

do not freeze

Zero-drift otherwise holds: both `{id, expected}` projections match `dc4bc91`, b05 and the authored holdout are unchanged, and since `a7ac228` only m02’s report and cell manifest changed under fixtures, with the corresponding study manifest update. The three extra ledger annotations and SPEC↔code sync test are sound, as are the committed crash-window admission and banner chronology; the sync test proves only internal agreement, and the rejected-state gap and “all fixed” banner claim are not acceptable given the source and executable counterexamples above.

CODEX-015-R7-DONE
