# Verdict

**Not freezable as written.**

No remaining defect appears to change the 22 locked outcomes or the intended primary R1 verdict. However, two frozen contracts remain false, and round-9 Major 3 is not fully closed.

## Blocking findings

1. **Composition is no longer a no-op, but its registered semantics remain incomplete.**

   [run_verify.py:146](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/run_verify.py:146) gives non-adjudicable currency unconditional precedence, so:

   ```text
   compose(non-adjudicable, not-usable:...) == unavailable
   ```

   But [MATRIX.json:4](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/MATRIX.json:4) says a TRANSITION refusal remains `not-usable` “adjudicable currency or not,” and that composition can only take `usable` away.

   The isolation test covers non-adjudicable+usable and adjudicable+refusal, but omits non-adjudicable+refusal at [test_study.py:948](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:948) and [test_study.py:959](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:959)—exactly the quadrant the layer makes unreachable.

2. **Round-9 Major 3 remains open.**

   The reported `Subscript`, `*sequence`, and `**mapping` bypasses are fixed. But the audit explicitly skips `ast.Attribute` and other callee forms at [test_study.py:731](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:731).

   For example, adding `spurious=5` to `registry.build_registry(...)` at [build_fixtures.py:361](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:361) passes the audit. Every pre-freeze runtime test stops at the preceding context gate, while the registered attempt would produce `harness-error`. `hook.__call__(context, spurious=5)` is another bypass.

   This contradicts both “Every holdout call site must bind” at [test_study.py:643](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:643) and the universal disposition at [PREREG-REVIEW.md:483](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/PREREG-REVIEW.md:483).

3. **The standalone TRANSITION fold-failure contract is false.**

   [SPEC.md:83](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/SPEC.md:83) and [SPEC.md:119](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/SPEC.md:119) promise `unavailable` when history fails to fold cleanly. Instead:

   - `_ever_supported` returns immediately after an early supported prefix at [transition.py:179](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/transition.py:179).
   - `_departure_after` uses `None` for both later fold failure and no departure at [transition.py:195](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/transition.py:195).
   - The caller can consequently return an ordinary refusal or `usable` at [transition.py:306](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/transition.py:306).

   The composed ceremony masks this because CURRENCY has already folded the full history successfully. This is precisely the upstream-guarantee shape requested.

## Round-9 closure accounting

| Item | Judgment |
|---|---|
| Blocker 1 / R8-2 | **Reject full closure.** Extraction and the main impossible input are fixed, but the omitted cross-product contradicts `MATRIX.json`. |
| Major 2 | **Closed in code** at [score.py:815](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:815). No regression isolates successful pipeline-invalid serialization. |
| Major 3 / R8-6a | **Rejected**, as above. |
| Minor 4 | **Closed** at [make_manifest.py:3](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/make_manifest.py:3) and [build_fixtures.py:87](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:87). |
| R8-1 | **Closed in code** at [score.py:799](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:799), but the result-summary split lacks an exposing regression. |
| R8-3 | **Closed** at [PREREGISTRATION.md:31](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/PREREGISTRATION.md:31) and [SPEC.md:90](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/SPEC.md:90). |
| R8-4, R8-5, R8-7, R8-9, R8-6b | **Closed.** Their ordering scope, endpoint scope, departure definition, holdout envelope, and derived stratum count remain accurate. |
| R8-6 | **Closed** at [PINS.json:5](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/PINS.json:5) and [score.py:9](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:9). |
| R8-8 | **Closed** at [README.md:41](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/README.md:41) and [build_fixtures.py:170](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:170). |
| R8-10 | **Closed.** The global matrix envelope and preregistration accurately explain alias execution, validity, R1 effect, and marker-scoped terminal recording. |
| Tripwire residual | **Closed** at [test_study.py:561](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:561). |

Other deletion-undetected safeguards exist but are not current outcome defects:

- `_gated()` at [build_fixtures.py:491](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:491) is tested only with real hooks that recheck context downstream.
- The `frozen` conjunct in the label predicate at [score.py:737](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:737) is masked by the mandatory null-pin refusal at line 742.
- The output-containment guard at [build_fixtures.py:516](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:516) has no valid-context/outside-root isolation test.

## Frozen-reader audit and stopping

The 22 locked outcomes and registered evidence fields reconcile with pilot 10. Counts, six citation absences, both identity groups, and the four-cell exact-difference claim are consistent. The holdout still has exactly the three preregistered divergences—h03, h05, and h08. I found no additional registered-outcome mismatch.

For the stopping questions:

- **(a)** No current registered outcome or intended primary R1 report changes. **Yes**, frozen readers are still misled by the composition and fold-failure contracts, and the holdout-audit closure is overstated.
- **(b)** The three blockers above are surgical and isolation-testable; a constrained correction pass is more likely to fix them than churn. The remaining defense-in-depth mutation gaps are the opposite: exhaustively chasing every redundant guard or AST spelling would be churn.

Therefore, **not freezable as written**. After those three targeted corrections, I would stop broad review rather than begin another open-ended sabotage audit.

Worktree remained clean at `9258bf91`; no holdout cell was executed. I could not rerun the pinned Python suite under the managed read-only environment, so I am not claiming a fresh test count.
