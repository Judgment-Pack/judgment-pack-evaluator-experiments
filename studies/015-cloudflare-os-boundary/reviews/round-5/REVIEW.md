# Round 5 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed,
static review only. Study tree reviewed at commit b193df3. Verdict: DO-NOT-FREEZE.

---

## 1. Verdict: DO-NOT-FREEZE

Static review only; I did not run the scorer, builders, probes, or tests.

The present record does not actually claim all six round-4 findings closed: R4-2 is “mostly fixed,” R4-5 and R4-6 remain “open,” and the text below the table says R4-3 still needs exact deployment inputs and full-description comparison. It explicitly says the study should not freeze. [PREREG-REVIEW.md:142](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREG-REVIEW.md:142)

More importantly, four substantive blockers remain: governed calls can still evade binding, effect identity does not prove causation, lifecycle/report predicates remain source-incomplete, and the second-portal fixtures remain impossible.

## 2. Audit of round 4’s dispositions

### R4-1 — partial

The repair is real for changed-argument effects, surplus effects, duplicate staged/ledger join identities, and a pristine orphan approved row. Applications now start from the ledger.

The inventory is nevertheless not closed:

- Under `proceed`, one governed call with no or a foreign commitment digest passes the cap because `len(subject_calls) == authorized == 1`. Since it is not in `bound_calls`, target, arguments, revisions, and report-state checks skip it; `execution:"none"` accepts it. [verify.py:249](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:249) [verify.py:736](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:736) [verify.py:804](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:804)
- That call can carry changed arguments or use a unique second gatekeeper. Because it is unbound, the checks that would detect those substitutions never run.
- Under inaction, a wrong-tool staged call sharing an approved row’s identity causes `governed_applications` to discard that otherwise governed row. An orphan with a missing/forged action-kind tag is also discarded rather than refused. [verify.py:346](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:346)
- Gatekeeper IDs and ledger `id`s are not required to be unique. Python resolves the first duplicate gatekeeper, while the TypeScript replay’s `Map` retains the last. [verify.py:377](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:377) [ceremony.ts:133](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/probes/ceremony.ts:133)
- SPEC step 10 still says scope includes exact arguments, contradicting both the implementation and the R4 disposition’s tool/resource scope. [SPEC.md:351](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:351)

### R4-2 — partial

The new `ledger-lifecycle-invalid` check is live and applies to every binding cell, but only five of round 4’s nine shapes are now refused:

| Round-4 shape | Current result |
|---|---|
| 1. `pending` + `appliedAt` | Refused |
| 2. `approved`/`rejected` without `appliedAt` | Refused |
| 3. Resolved with `appliedAt < witness.at` | Still accepted and excluded from that queue; not inherently invalid alone |
| 4. `pending` + `resolvedBy`, no `appliedAt` | Refused |
| 5. `pending` + `autoApproved:true` + resolver, no `appliedAt` | Refused |
| 6. `rejected` + `autoApproved:true` + stamp/resolver | Refused |
| 7. Same resolver ID but different valid name/type | Still accepted; only `.id` is compared |
| 8. Parseable non-RFC-3339 timestamps | Still accepted |
| 9. `appliedAt == witness.at` | Still accepted and treated as pending; baseline relies on equality |

The implementation also accepts two newly obvious source-impossible tuples: `approved` without any `autoApproved` value, and `rejected` with `autoApproved:false`. Upstream’s approval chokepoint always persists the required Boolean; rejection never does. [verify.py:462](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:462) [overseer.ts:2486](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/overseer.ts:2486)

The two open remedies are mentioned in the retrospective review, but not where readers rely on them:

- Witness JSON is cast rather than schema-validated, and typechecking covers only ledger rows and final rules. The normative SPEC does not disclose that malformed witnesses can bypass attribution comparisons.
- “Flattened enum” occurs only in `PREREG-REVIEW.md`. SPEC and MATRIX instead call `m02` an honest retained private failed/non-retryable trace, although its fixture contains only `connectorOutcome:"outcome-unknown"`—no private row, retryability, error, or independent join. [SPEC.md:411](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:411) [MATRIX.json:694](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/MATRIX.json:694)

### R4-3 — partial

Several repairs are genuine:

- `b01` and `h03` now render their changed arguments in ledger prose.
- `h03` matches the reviewer-authored construction.
- `o01` is a genuine read-path observation matching `session.ts`’s `authorizeObservation(described)` path.
- Obstruction fixtures now carry `rejected`.
- Approved manual rows centrally receive `autoApproved:false`.
- `h03` and `h04` expectations were not changed; the authored-expectation comparison still enforces that. [test_study.py:137](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_study.py:137)

But `b04`/`h04` are not faithful second deployments. `Builder.describe()` hard-codes the primary portal server name and endpoint, including in its cache key’s effective inputs. Both second-deployment calls therefore retain `resourceUrl=https://other-tracker.example/...` while their prose still says `tracker portal / tracker` and `Endpoint: https://tracker.example/mcp`. [build_fixtures.py:375](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:375) [b04 ledger.json:4](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/fixtures/mutations/b04-gatekeeper-substituted/ledger.json:4) [h04 ledger.json:4](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/fixtures/holdout/h04-coherent-target-and-kind-substitution/ledger.json:4)

Pinned `session.ts` supplies the current host’s own `serverName` and endpoint, so this tuple cannot be emitted by the asserted second deployment. It also violates h04’s authored requirement to change every target-bearing ledger field. Exact portal names, upstream display names, and workspace title overrides remain unregistered.

### R4-4 — partial

The literal wrong-identity mutation is now refused: changing the effect’s action from 11 to 99 produces `unbound-execution`. Instrumentation status is stated in SPEC’s provenance table and step 15.

That does not close substituted causation. For history “A was approved, B caused the effect,” the attestation writer can label B’s effect with A’s `(gatekeeperId, action)`. The fields are unsigned, untyped, and uncorroborated by a private connector result or independently trusted attester. The verifier then proves only that the attestation asserts A’s identity, not that A caused the effect. [verify.py:936](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:936) [SPEC.md:362](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:362)

The regression test proves rejection of an asserted mismatching label; it does not prove that the asserted matching label came from the producer. Calling this a “causal join” and claiming “binding and lineage” remains unjustified.

### R4-5 — real as an open disposition, not closed

The remaining absolute is still false. Holdout rows do not enter R1 arithmetic, but registered publication requires the holdout; its registry parse, digest pin, and fixture manifests are shared attempt gates. A malformed holdout can suppress R1 publication. [score.py:22](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/score.py:22) [score.py:673](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/score.py:673)

The test named `test_holdout_invalidity_cannot_change_r1` only searches for row-routing substrings; it does not exercise those shared gates. [test_study.py:207](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_study.py:207)

### R4-6 — real as an open disposition, not closed

The absolutes remain false:

- README says every pin is enforced and every retained record typechecked; enforcement is hard-coded for selected pin fields, while typechecking covers ledger records and auto-approval rules only. [README.md:103](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/README.md:103) [typecheck.py:64](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/typecheck.py:64)
- PINS says there is no action-log export anywhere, despite upstream `listActions()`. The defensible claim is “no signed, complete, offline-verifiable export.” [PINS.json:26](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/PINS.json:26) [overseer.ts:7548](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/overseer.ts:7548)
- PREREGISTRATION and `commitment.py` still describe retained bytes as what was “captured”; hashing a retained preimage does not prove a capture event.
- DEVIATIONS says `simulationBasis` was removed and later says it remains registered. [DEVIATIONS.md:101](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/DEVIATIONS.md:101)

## 3. Numbered findings

1. **BLOCKER — the commitment carrier is optional on the sole authorized call.**  
   Exact claim: R4-1 says every governed call is inventoried and bound. Current code enforces only an upper bound of one subject call under `proceed`; it does not require that call to carry the commitment digest. Remedy: if an executable action has any in-scope call, require exactly one and require it to be the unique digest-bound call; make `none` inspect governed inventories; fail closed on ambiguous calls/applications; enforce unique gatekeeper, ledger, and private-action identities.

2. **BLOCKER — the effect identity is forgeable in the only way that matters.**  
   Exact claim: SPEC says the pair turns arithmetic into causation. It is actually an unauthenticated assertion in modeled `platform.json`; effect records are not schema-validated or typechecked. Remedy: introduce an independently trustworthy identity-bearing capture/private-result record, or replace all causal/lineage claims with “the retained attestation asserts this identity.”

3. **BLOCKER — lifecycle and report state are not source-closed.**  
   Exact claim: SPEC says every accepted lifecycle tuple and report predicate is platform-producible. `applied` rejects only `outcome-unknown`, so an approved outer row plus `connectorOutcome:"rejected"`, `"failed"`, `"pending"`, or absent supports `applied`; the new `rejected` value on the actual obstruction calls is unbound and therefore never validated. [verify.py:1009](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:1009) Remedy: retain and schema-check the real private `StoredAction`, join it to the outer row, enforce a complete private/outer/report state matrix, parse strict RFC-3339 instants, define equality, and validate complete resolver attribution.

4. **BLOCKER — the prospective h04 fixture remains incidentally impossible.**  
   Exact claim: R4-3 says h04 faithfully moves every target-bearing field to a second Portal deployment. Its description embeds the first deployment’s target. Remedy: parameterize `describe()` by complete deployment configuration, register both portal configurations and workspace title overrides, regenerate b04/h04, and compare complete generated description bytes in both strata. The authored h03/h04 expectations need not change.

5. **MAJOR — test names overstate what is established.**  
   The nineteen numbered `BINDING_CHECKS` labels do match SPEC order; that part is real. But the test compares labels, not effective semantics. SPEC says there are two pre-check gates, while `_load_context` adds `retained-store-unreadable` and can call `derived_action` before the per-check exception guard. [verify.py:388](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:388) [test_study.py:62](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_study.py:62)

   Likewise, `test_registered_scenario_is_connector_shaped` excludes holdout, never compares full prose, and checks the action-kind label only if the retained tag already equals its primary expected tag—precisely masking b04. [test_study.py:311](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_study.py:311)

6. **MAJOR — new fields include dead or contradictory data.**  
   `b06` and `m01` effects now claim staged-call identity `1/11` even though b06 declares no staged call anywhere and m01 is explicitly a read-path event. Those fields are dead because `unbound-execution` returns on zero authorization before examining identity. [build_fixtures.py:273](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:273) Remedy: define a validated provenance union—bound staged call versus read-path/out-of-band source—instead of fabricating a staged identity for every effect.

   The locked `o01` expectation legitimately changed from upstream `not-engaged` to `pass` because its rebuilt observation now engages `classifyTool`; h03/h04 expectations did not change. That is construction-aligned, not hidden drift, but the protocol-relevant registry change should be recorded in DEVIATIONS.

7. **MAJOR — the governing documents still contradict implementation and one another.**  
   This includes exact-arguments versus tool/resource inventory scope, “actual connector emissions” versus synthetic reconstruction, real private-row language versus a flattened scalar, holdout isolation, capture provenance, pin/typecheck absolutes, and PREREG-REVIEW simultaneously marking R4-3 fixed and its deeper remedy open. Remedy: after the structural claims are narrowed, perform a single source-of-truth sweep across PREREGISTRATION, SPEC, MATRIX, PINS, README, DEVIATIONS, diagnostics, and test names.

## 4. Convergent or structural

There has been real local convergence: several malformed ledger tuples are now rejected, changed-argument effects and pristine orphans are counted, fixture arguments improved, and the literal wrong effect identity fails.

The study is nevertheless **structural as currently claimed**. The recurring failure is treating bridge-authored, unsigned modeled fields as proof of source history: a commitment label becomes binding, a flattened enum becomes a private connector row, and a self-asserted pair becomes causation. Another round of tuple and cardinality patches cannot make those fields independently authoritative. The study can converge only through a material scope change—withdraw causal/source-reachability claims and describe internal retained-store consistency—or by introducing an actual trusted retention boundary and real connector-row/effect capture. This is not a same-commit wording cleanup.

## 5. What a reader may legitimately conclude if it freezes as-is

A reader may conclude that this frozen apparatus compares registered outcomes over a selected collection of mostly synthetic retained-store constructions; that, for well-formed digest-bound calls, it performs substantial internal consistency checks against a deterministic disposition-to-action map; that retained evidence bytes are checked against their recorded digests; and that two pinned Cloudflare OS policy functions are replayed offline where registered. They may not conclude that the inventory is closed, that accepted lifecycle or connector traces are source-reachable, that an attested effect was caused by its named call, that the real private connector record was retained, that every retained record or pin is mechanically enforced, that holdout material cannot suppress R1 publication, or that anything describes live Cloudflare OS runtime behavior.

CODEX-015-R5-DONE