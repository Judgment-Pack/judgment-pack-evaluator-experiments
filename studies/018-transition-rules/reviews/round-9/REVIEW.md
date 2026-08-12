# Verdict

**Not freezable as written.**

The two requested core branches are substantially correct, but the round-8 change exposed reporting defects, and the frozen-reader audit found a nonfunctional composition gate plus several unresolved contradictions.

## Behavior-changing fixes

### `decide()`

The verdict predicate now widens R1 by exactly the registered class:

- Non-adjudicated cells take precedence as pipeline-invalid at [score.py:597](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:597).
- Divergent control gates take precedence next at [score.py:601](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:601).
- Only divergent endpoints or `registeredUndetected` cells then falsify R1 at [score.py:612](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:612).

Thus “whatever its role” is correct only after the registered pipeline/control precedence. A flagged control gate remains control-inconclusive; a flagged non-adjudicated cell remains pipeline-invalid.

However, integration is incomplete: [score.py:797](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:797) sets `endpointDivergences = len(causes)`. Causes now include the descriptive registered-undetected row, so the summary can report a non-endpoint as an endpoint divergence.

### `REGISTERED`

The successful-result path is correct:

- The only label assignment requires every freeze pin and `--include-holdout` at [score.py:735](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:735).
- The flagged path validates the nonempty stratum and evidence at [score.py:739](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:739).
- `adjudicate_holdout()` necessarily runs before results are published at [score.py:779](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:779).

No successful `REGISTERED` result can contain `holdout: null`, and a successful fully pinned flagged attempt cannot be mislabeled `PILOT`. Terminal/crashed attempts are unlabeled rather than falsely labeled.

The frozen descriptions remain incomplete: [PINS.json:5](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/PINS.json:5) and [score.py:11](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:11) still state only the pin requirement and omit mandatory holdout execution.

## Round-8 closure

| Item | Status |
|---|---|
| 1 | **Reject full closure.** `decide()` is correct, but `endpointDivergences` misreports the new non-endpoint cause at `score.py:797`. |
| 2 | **Rejected — blocker.** The purported composition gate is algebraically ineffective; see below. |
| 3 | **Rejected.** The main corrections landed, but [PREREGISTRATION.md:32](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/PREREGISTRATION.md:32) falsely says every refusal is chosen by the fold. Currency, configuration, duration, and citation refusals are not. [SPEC.md:93](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/SPEC.md:93) also says departure is queried only for `position-window`, while grandfather computes and publishes it at [transition.py:303](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/rule/transition.py:303). |
| 4 | **Closed.** The layer-versus-harness ordering is now accurately scoped at `SPEC.md:52–59`. |
| 5 | **Closed.** The governing scenario statement is correctly endpoint-scoped at `PREREGISTRATION.md:76–80`. |
| 6 | **Behavior closed; frozen description incomplete.** No successful label bypass remains, but `PINS.json:5` and `score.py:11–17` omit the holdout condition. |
| 7 | **Closed.** Exact binding and first post-citation departure are stated at `SPEC.md:144`. |
| 8 | **Rejected.** [README.md:41](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/README.md:41) and [build_fixtures.py:165](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:165) still call mint-time refusal a producer policy, despite no such policy existing. |
| 9 | **Closed.** The envelope at `MATRIX-HOLDOUT.json:4` clearly distinguishes the preserved reviewer notes from the governing first-post-citation rule. |
| 10 | **Rejected.** Stale claims remain at [PREREGISTRATION.md:99](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/PREREGISTRATION.md:99), [PREREGISTRATION.md:149](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/PREREGISTRATION.md:149), [MATRIX.json:279](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/MATRIX.json:279), and [MATRIX.json:314](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/MATRIX.json:314): aliases do affect execution/validity/R1, and terminal recording begins only after the marker. |
| 6a residual | **Rejected.** The exact `hook(context, spurious=5)` mutation is caught, but the universal static audit still skips `ast.Subscript` calls and `**mapping` arguments at [test_study.py:670](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:670) and [test_study.py:724](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:724). |
| 6b residual | **Closed.** The two-strata count is now derived at `test_study.py:484–486`. |
| Tripwire residual | **Reject strict closure.** Its docstring is honestly scoped at `test_study.py:570–580`, but the test name at [test_study.py:561](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/tests/test_study.py:561) still claims refusal precedes “any … write.” |

## Fresh frozen-reader findings

1. **BLOCKER — the composition gate does nothing.**  
   [run_verify.py:131](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/run_verify.py:131) returns the transition outcome in both branches. Current cells remain safe only because TRANSITION itself rejects non-adjudicable currency at `transition.py:225–229`. This contradicts the registered “extra condition” in `MATRIX.json:4`, and existing tests do not isolate composition from the TRANSITION gate.

2. **MAJOR — contradictory pipeline status.**  
   A non-adjudicated cell produces `R1 inconclusive - pipeline-invalid` at `score.py:597–600`, while the published result unconditionally carries `"pipelineInvalid": false` at [score.py:803](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/score.py:803).

3. **MAJOR — static holdout proof remains bypassable.**  
   For example, replacing `hook(context)` with `HOLDOUT_HOOKS[cell_id](context, spurious=5)` changes the AST callee to a `Subscript`; both audits skip it, and the error remains hidden until the registered attempt.

4. **MINOR — copied coverage descriptions remain false.**  
   [make_manifest.py:3](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/make_manifest.py:3) claims coverage of `registry/`, upstream records, and two vendored fixtures absent from its actual sets at line 22. [build_fixtures.py:87](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt018/studies/018-transition-rules/harness/build_fixtures.py:87) claims `build_payloads()` covers every registered cell although holdouts use a separate in-attempt constructor.

No additional locked-cell expected-outcome or structured-evidence mismatch was found.

Verification at clean `e7fbea2e`: Python 3.12.11, `48 passed`; whole-study and every fixture manifest passed; worktree remained clean. No holdout cell was executed.
