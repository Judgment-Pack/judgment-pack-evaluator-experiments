# Round 1 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed
(workspace-write scratch; study tree and pinned clone read by absolute path).
Study tree reviewed: commit bb1d1cb (the round began at ea9b292; one commit — the
holdout schema gate and stratum column, no adjudication logic — landed early in the
round and the reviewer's verdict names bb1d1cb explicitly).
Exit status 0; completion marker present. Verbatim output follows.

---

## 1. Verdict

**DO-NOT-FREEZE**

At evaluator commit `bb1d1cb288d03daa262c7c3f8bf9b505d1fe5851` and Cloudflare OS commit `b2a51b5426398c8353d9d4dd984bd525121ab5f2`, the preregistration has several protocol-level defects. Most importantly:

- the verifier does not independently verify the registered disposition→action map;
- `evidenceBacking` can be fabricated without a retained referent;
- the `cf` layer attributes study-authored orchestration to the platform;
- drain replay cannot establish historical auto-approval validity;
- registered simulation and ambiguous-commit fixtures are not source-reachable in the pinned MCP scenario;
- the holdout stratum is not currently constructible or independently scoreable.

These require changes to code, matrix semantics, and claims—not merely editorial clarification. I performed a static review only; I did not run tests, probes, pilots, scorers, or holdout constructions.

## 2. Findings

1. **Blocker — The exact disposition→action map is never independently verified.**

   Files/claim attacked: [adapter/SPEC.md, lines 115–179](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:115), [adapter/commitment.py, lines 96–137](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/commitment.py:96), [adapter/verify.py, lines 327–449](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:327), and README’s claim that green establishes that the recorded action was authorized.

   `verify.py` checks whether an action is null/non-null consistently with executability, then compares downstream records to the bridge-authored commitment. It never independently derives the canonical target and arguments from the retained facts and disposition. A bridge or coherent store writer can choose the wrong arguments, target, or action-kind tag, rebuild the commitment and both binding points, and obtain all-pass results.

   It also lacks totality/cardinality checks: a non-null authorized action can have no staged call while a report says `staged`; duplicate or additional relevant calls can escape because lookup selects one matching record.

   **Remedy:** independently derive the normative action from the retained JPS result and fixed map; verify target, action-kind scope, arguments, stage-time revision and simulation basis; and enforce report-dependent cardinality and uniqueness across staged calls, ledger rows, and effects.

2. **Blocker — `evidenceBacking` proves only the shape of an assertion, not its referent.**

   Files/claim attacked: [adapter/SPEC.md, lines 27–37 and 94–102](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:27), [adapter/SPEC.md, lines 219–232](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:219), [adapter/verify.py, lines 289–318](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:289), and [harness/build_fixtures.py, lines 363–373](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:363).

   The retained-record model contains no approval/observation artifact whose bytes can be checked against the backing digest. The verifier accepts `kind == "artifact"` plus a digest-shaped reference. It does not establish hexadecimal validity, existence, or preimage equality. Approval-record bytes—or arbitrary bytes—can therefore be hashed and relabeled as an artifact. This defeats the intended s04/o01 step-6 distinction.

   There is also a specification conflict: ceremony step 2 promises closed vocabularies and digest validation, while `commitment.py` deliberately leaves backing `kind` and `ref` open so later evidence-specific verdicts remain reachable.

   **Remedy:** retain a closed manifest of backing artifacts and verify every reference against actual retained bytes. Otherwise rename these fields “unverified backing assertions” and retract the claimed artifact-lineage protection.

3. **Blocker — The `cf` layer is selected upstream-function replay, not the platform’s executable enforcement surface.**

   Files/claim attacked: [PREREGISTRATION.md, lines 36–42 and 197–208](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREGISTRATION.md:36), [adapter/SPEC.md, lines 189–213](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:189), and [probes/ceremony.ts, lines 85–243](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/probes/ceremony.ts:85).

   `classifyTool` and `AutoApprovalDrainer` are genuine upstream functions. But the offline join, routing decisions, reset operation, fabricated apply callback, and emitted verdict codes are study-authored. The Durable Object enforcement path is never run. Calling the result the platform’s own executable policy surface lets `cf: pass` be mistaken for platform endorsement, including cells where `platformChecksEngaged` is empty.

   Moreover, “the platform performs no runtime schema validation” is too broad. The pinned RPC surface uses `@validateRpc()` around the actual submission path; the defensible claim is that it provides no offline verifier for the exported or modeled retained records.

   **Remedy:** rename this layer `upstream-policy-replay` or equivalent; call `[]` outcomes “not engaged,” not pass; describe `platformChecksEngaged` as checks replayed by the harness; and reserve platform-enforcement claims for an actual Durable Object run.

4. **Blocker — Reset-and-redrain is not a sound replay of historical auto-approval.**

   Files/claim attacked: [probes/ceremony.ts, lines 181–245](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/probes/ceremony.ts:181) versus pinned [auto-approval.ts, lines 51–93](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/auto-approval.ts:51) and [overseer.ts rule-removal path](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/overseer.ts:7759).

   Upstream drains then-current pending actions per gatekeeper, in ascending action order, and stops at the first manual gate. The harness resets only claimed-auto rows while preserving other rows in their final states and replaying current catalog, trust, and rule state.

   This creates both directions of error:

   - False negative: a lower-ID manual action blocked the queue, a higher-ID action was impossibly auto-applied, and the manual action was rejected later. Final-state replay ignores the historical blocker.
   - False positive: an action was legitimately auto-approved, then the user removed its rule or changed catalog/trust state. Replaying against current state rejects the valid historical decision.

   Cross-gatekeeper global ordering is not required by upstream; the unsoundness is temporal state within a gatekeeper.

   **Remedy:** retain pre-drain snapshots or an authenticated event sequence containing rule, catalog, trust, and queue state. Otherwise narrow the claim to “final-snapshot existential consistency,” not historical replay.

5. **Blocker — d01/d02 are not reachable through the registered concrete MCP scenario.**

   Files/claim attacked: [PREREGISTRATION.md, lines 107–114](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREGISTRATION.md:107), [harness/build_fixtures.py, lines 631–665](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:631), generic [gatekeeper.ts simulation support](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-shared/src/gatekeeper.ts:620), and concrete [MCP session.ts, lines 126–135](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/mcp-shared/src/session.ts:126).

   Generic Gatekeepers may simulate. The pinned MCP connector explicitly does not simulate queued calls. The study nevertheless gives the concrete `create_work_item` scenario simulated premises and outcomes. These are synthetic adapter records, not source-reachable Cloudflare MCP records.

   **Remedy:** add and pin a custom Gatekeeper that actually implements simulation, or move D into a clearly separate synthetic contract stratum and remove MCP-runtime implications.

6. **Blocker — m02’s outer action state contradicts pinned source semantics.**

   Files/claim attacked: [harness/build_fixtures.py, lines 681–686](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:681), pinned [action-store.ts, lines 152–170](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/mcp-shared/src/action-store.ts:152), and [overseer.ts, lines 2490–2498](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/overseer.ts:2490).

   For an MCP outcome-unknown timeout, the private MCP action becomes `failed`, non-retryable, and throws. The outer action is changed to `approved` only after the Gatekeeper call returns successfully. Therefore m02’s outer `approved`/`appliedAt` row with an outcome-unknown note is source-impossible. The real outer record remains pending; the informative failure state is private to the MCP ActionStore.

   The conceptual at-most-once boundary is real, but the fixture does not represent it. The matrix also lacks the inverse report endpoint: ambiguous evidence reported as definitively `applied`.

   **Remedy:** model outer pending plus retained private MCP failed/non-retryable state, and add an `applied-unproven → applied` overclaim endpoint.

7. **Blocker — The holdout stratum cannot currently satisfy its preregistered role.**

   Files/claim attacked: [harness/MATRIX-HOLDOUT.json](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/MATRIX-HOLDOUT.json), [harness/build_fixtures.py, lines 403–693](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:403), and [harness/score.py, lines 149–153 and 612–665](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/score.py:149).

   The builder hardcodes locked cells and has no holdout construction hooks. The scorer routes every nonbaseline cell to `fixtures/mutations/<id>` rather than a separate holdout fixture tree. Holdout validity failures enter the global `invalid` collection and can make locked R1 pipeline-invalid, contrary to the claim that the holdout is separately opened and reported. There is no independent holdout summary or verdict.

   The freeze refusal exists only in the official scoring route; direct layer calls remain possible. It should be described as an official-path guard, not proof that no one could execute the cases.

   The sibling Study 014 regime had already addressed separate holdout fixtures, constructibility, and independent holdout reporting. Study 015 regresses those controls.

   **Remedy:** add unexecuted construction hooks, static construction-coverage checks, a separate fixture directory and score object, and ensure holdout invalidity cannot alter locked R1. Enforce nonempty cells, reviewer attribution, disjoint IDs, and the top-level stratum/version.

8. **Major — The claimed validity gate does not include the registered typecheck.**

   Files/claim attacked: [PREREGISTRATION.md, lines 120–126 and 239–247](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREGISTRATION.md:120), [harness/score.py, lines 53–59 and 561–568](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/score.py:53), and [harness/tests/test_study.py, lines 120–122](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_study.py:120).

   `score.py` never invokes `typecheck.py`; typechecking occurs only as a pytest test. A directly published score can therefore call itself valid without the registered published-contract check. Pilot 1’s clean validity result despite predating later required resource fields demonstrates the gap.

   Type validity also does not establish source reachability. For example, the builder omits explicit false auto-approval values on manual rows, and some rejected-state timestamps do not match the actual state machine, even though the public API types make fields optional for compatibility.

   The recorded backend-typecheck deviation additionally needs its actual command and diagnostics. The pinned tree does contain the tracked `worker-configuration.d.ts` consumed by its `tsconfig`; “requires regeneration” is not established by the retained prose alone.

   **Remedy:** make typecheck a scorer precondition, stamp compiler/tool identity into the result, add state-machine/source-reachability validation, and retain exact backend command output.

9. **Major — R1 is a self-concordance endpoint and can hold while the composition is weak.**

   Files/claim attacked: [PREREGISTRATION.md, lines 30–65](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREGISTRATION.md:30), [harness/MATRIX.json](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/MATRIX.json), and the two pilots.

   The layers do not read matrix expectations, so validity/detection separation is structurally real. But one authorial system produced the normative map, fixture mutations, first-failure order, and expected codes. The locked cells mutate downstream representations while keeping the bridge-authored commitment honest; they do not challenge whether that commitment represents the right action.

   Both green pilots with zero expectation corrections establish determinism and live controls. They do not independently validate the platform interpretation or semantic oracle.

   The `attackerCapability` field is also too broad. Cells such as b02/b04/b05 depend on a store writer changing one downstream field while declining to coherently rebuild related records. A fully capable store writer can evade them, exactly as the coherent-rewrite ceiling admits. The field currently identifies an actor more than a capability envelope.

   **Remedy:** describe R1 as a locked regression endpoint only; report reviewer holdout outcomes separately and co-prominently; and register the exact mutation constraint instead of labeling it general `store` capability.

10. **Major — Modeled retention is disclosed, but later claims still flatter the stock platform.**

   Files/claim attacked: [adapter/SPEC.md, lines 27–49](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:27), PREREGISTRATION §3, and [overseer.ts public-action projection, lines 610–645](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/cloudflare-os/packages/workshop-backend/src/overseer.ts:610).

   The initial disclosures correctly identify `platform.json` and effects as modeled. But most B and D detections depend on staged calls, resource revisions, simulation bases, and effect attestations that stock Cloudflare OS does not export in its public action log.

   The concrete MCP private store does retain tool name, arguments, lifecycle, result/error, and retryability. The outer workspace action log instead exposes an opaque action identifier and strips private action/caller material. Neither supplies the modeled resource revision, commitment digest, effect attestation, or generic simulation state.

   **Remedy:** provide a per-field provenance table and a per-cell `modeledDependencies` declaration. Consistently call the target an instrumented bridge composition, and distinguish what can be learned from the stock public log, private MCP store, adapter records, and external effect instrumentation.

11. **Major — First-failure attribution suppresses failures; report-state semantics are largely unchecked.**

   Files/claim attacked: [adapter/SPEC.md, lines 219–280](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:219), [adapter/verify.py, lines 471–510](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/verify.py:471), and [harness/tests/test_reachability.py, lines 211–256](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/tests/test_reachability.py:211).

   The implementation broadly follows the specified map→reuse→target→arguments→revision→simulation→unbound ordering. But “exactly one layer” is produced by returning the first code, not by establishing that only one defect exists. Examples include s05’s handoff and report defects, and b05’s target plus argument defects.

   Only `effect-attested` is materially correlated with a retained effect. `none`, `staged`, `applied`, and `applied-unproven` are accepted without corresponding queue, ledger, effect, or ambiguity predicates. Free-text notes and additional fields are ignored.

   Reachability tests call layers directly and test selected combinations, not every ordered pair. `replay-unavailable` is not reachable through the integrated scorer when pin preflight invalidates first.

   **Remedy:** retain the primary code plus a suppressed-code list, or ensure every endpoint contains exactly one defect. Define closed predicates for every report state and narrow the reachability claim to what the tests actually demonstrate.

12. **Major — Several committed lineage fields are ornamental.**

   Files/claim attacked: [adapter/commitment.py, lines 299–324](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/commitment.py:299) and the “unchanged judgment tuple” claim in [adapter/SPEC.md, lines 88–93](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/adapter/SPEC.md:88).

   Pack bytes and evaluator disposition are checked, but parsed `packId`, `packVersion`, evaluator release, and envelope/tool version are not all cross-checked. `supportedExtensions` is sorted but duplicate values remain legal. The action-kind scope tag is not recomputed against the upstream action-kind construction.

   **Remedy:** validate every committed identity/release field against its retained source, enforce extension uniqueness, and derive the scope tag from the pinned platform rule.

13. **Major — Apparatus pinning and terminal-output claims exceed implementation.**

   Files/claim attacked: [harness/PINS.json](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/PINS.json), [harness/score.py, lines 499–516 and 653–667](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/score.py:499), and [probes/upstream-probes.ts](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/probes/upstream-probes.ts).

   The upstream commit, cleanliness, selected source digests, and Node identity are meaningfully checked. But not every non-null apparatus declaration is enforced: esbuild is self-reported rather than compared to a registered pin; pnpm/package/tool binary contents are not fully anchored; and the external pack identity relies on an internal manifest rather than an independently registered digest.

   The promise that every failure produces a terminal invalid artifact is false for unreadable `PINS.json`, which is parsed before attempt initialization, and for final non-atomic result writing. `upstream-probes.ts` defines a suite but is not wired into the scorer or CI as registered evidence.

   **Remedy:** distinguish enforced pins from descriptive metadata, hash executable tool inputs, independently anchor the external manifest, initialize attempt capture before parsing pins, write terminal results atomically, and either execute the upstream probe suite as a validity check or remove the implied coverage claim.

14. **Minor — Several freeze-text statements are factually stale.**

   Files/claim attacked: [harness/MATRIX.json, b05](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/MATRIX.json), [harness/build_fixtures.py, lines 611–623](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/harness/build_fixtures.py:611), and [PREREGISTRATION.md, lines 139–144](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7198b91a-6e6f-4860-bc24-273678edda94/scratchpad/evalexp-015/studies/015-cloudflare-os-boundary/PREREGISTRATION.md:139).

   b05 says the argument digest is updated, but the builder leaves the original commitment and lets target mismatch mask argument drift. The preregistration calls the endpoints six-category coverage even though M contains demonstration/descriptive rows rather than endpoints. At least one Overseer line citation for the opaque action key is stale.

   **Remedy:** reconcile every construction note with emitted fields, count endpoint categories accurately, and refresh pinned-source line citations.

## 3. Answers to [D-1]–[D-5]

**[D-1] No.** Calling `cf` the platform’s own executable policy layer is not defensible as written. It is a study-authored offline ceremony invoking two upstream functions. `cf: pass` with no engaged check is especially easy to read as platform endorsement. Rename the layer and make non-engagement an explicit non-pass state.

**[D-2] Conditionally defensible.** “Only `proceed` executes” is a legitimate adapter-owned policy for this scenario, but it is not inherent to JPS or Cloudflare OS. Several S/B attributions depend on that choice and must remain adapter-layer claims. A clarify-with-execution case should exist as a negative endpoint, not as an alternate valid mapping; holdout h01 supplies it.

**[D-3] The placement inside the judgment is not itself the problem.** The problem is that backing references have no retained preimage/existence oracle. s04/o01 can be defeated by hashing approval or arbitrary bytes and labeling the result `artifact`. A separately retained manifest would materially improve the design by establishing existence and preimage binding, though not authenticity.

**[D-4] Insufficient.** Direct reachability tests show that selected verdict-producing branches are live, but they are same-author checks, do not traverse the integrated scorer, and do not prove the locked controls independently exercise each layer. Add locked negative controls for binding and replay, invoke them through the official scorer, and narrow claims about exhaustive first-failure ordering.

**[D-5] The boundary is real; the registered row is not.** Cloudflare’s at-most-once/outcome-unknown condition is genuine, but m02’s outer approved record is source-impossible. Model the actual outer-pending/private-inner-failed trace and add the inverse overclaim endpoint where ambiguous evidence is reported as definitively applied.

## 4. Reviewer holdout stratum

These expectations predict the reviewed apparatus, not the outcomes a corrected verifier ought to produce. If pre-freeze fixes cause divergence, that divergence should remain a primary result; do not revise this JSON to follow the fix.

```json
{
  "matrixVersion": "1",
  "stratum": "reviewer-holdout",
  "note": "Authored by the Study 015 pre-freeze cross-vendor reviewer from static inspection only. No holdout construction was executed.",
  "reviewer": "OpenAI Codex — Study 015 pre-freeze adversarial review, 2026-08-09",
  "cells": [
    {
      "id": "h01-clarify-bound-execution",
      "category": "S-semantic-collapse",
      "variant": "bridge-behavior",
      "role": "endpoint",
      "attackerCapability": "bridge",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the registered clarify disposition used by b06. Instead of leaving the out-of-band execution unbound, place the canonical proceed action into the staged-call queue, rebuild the commitment with that non-null action, put the same commitment digest at both binding points, add a manually approved ledger row at resource revision 7, add the matching effect attestation, and report execution as effect-attested.",
      "expected": {
        "cf": "pass",
        "binding": "fail:action-map-violation",
        "replay": "pass"
      },
      "note": "Exercises clarify-with-bound-execution. It differs from b06 because the execution is fully bound to the bridge commitment."
    },
    {
      "id": "h02-approval-digest-laundered-as-artifact",
      "category": "S-semantic-collapse",
      "variant": "bridge-behavior",
      "role": "endpoint",
      "attackerCapability": "bridge",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the honest manual proceed case. Compute SHA-256 over the JCS bytes of the first approval-ledger record, use the resulting sha256 reference as evidenceBacking.sponsor with kind artifact, retain no sponsor artifact having those bytes, rebuild the commitment and both binding points, and otherwise retain the canonical staged call, ledger state, effect, and report.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "Predicted blind spot: the verifier checks the artifact label and digest shape but not existence or preimage."
    },
    {
      "id": "h03-coherent-argument-substitution",
      "category": "B-binding-integrity",
      "variant": "coherent-rebuild",
      "role": "endpoint",
      "attackerCapability": "store",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the honest manual proceed case. In the canonical action arguments, locate the lexicographically first JSON Pointer whose value is a string and replace that value with the literal someone-else-entirely. Recompute the JCS arguments digest, rebuild the commitment, update both commitment binding points, and make the staged call and manually approved ledger row carry the substituted arguments. Retain no effect and report execution as applied.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "All binding records agree with one another, but the action is no longer the registered deterministic action derived from the unchanged facts."
    },
    {
      "id": "h04-coherent-target-and-kind-substitution",
      "category": "B-binding-integrity",
      "variant": "coherent-rebuild",
      "role": "endpoint",
      "attackerCapability": "store",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the honest manual proceed case. Add a second gatekeeper and resource with a catalog entry for create_work_item. Change every target-bearing commitment, staged-call, and ledger field to that second gatekeeper/resource; change actionKindTag to the literal reviewer-forged-scope:create_work_item; rebuild the commitment and both binding points; retain canonical arguments and resource revision 7; retain no effect and report execution as applied.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "Predicted blind spot: target and action-kind semantics are checked only for downstream self-consistency, not derived from the unchanged facts or upstream scope rule."
    },
    {
      "id": "h05-phantom-staged-report",
      "category": "B-binding-integrity",
      "variant": "bridge-behavior",
      "role": "endpoint",
      "attackerCapability": "bridge",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the honest proceed judgment and retain its non-null canonical action commitment. Retain platform.json and ledger.json as present files but set stagedCalls and action records to empty arrays. Retain the commitment digest in report.json and report execution as staged.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "Predicted blind spot: report state staged is not required to have a corresponding staged call."
    },
    {
      "id": "h06-autoapproval-rule-removed-after-apply",
      "category": "M-annotation-trust",
      "variant": "environment",
      "role": "endpoint",
      "attackerCapability": "environment",
      "registeredAbsences": [],
      "platformChecksEngaged": [
        "classifyTool",
        "AutoApprovalDrainer"
      ],
      "construction": "Start from the honest auto-approved baseline after its action has been applied and effect-attested. Modify only the retained final platform snapshot by removing the matching auto-approval rule or tag; leave the tool catalog, action row, autoApproved flag, staged call, commitment, effect, and report unchanged.",
      "expected": {
        "cf": "fail:drain-order-violation",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "A legitimate historical approval becomes a replay failure because the ceremony uses current rule state rather than stage-time state."
    },
    {
      "id": "h07-drain-final-state-erases-manual-gate",
      "category": "B-binding-integrity",
      "variant": "coherent-rebuild",
      "role": "endpoint",
      "attackerCapability": "store",
      "registeredAbsences": [],
      "platformChecksEngaged": [
        "classifyTool",
        "AutoApprovalDrainer"
      ],
      "construction": "Start from the honest auto-approved baseline. On the same gatekeeper, prepend a lower-numbered action for a cataloged tool that requires manual approval. Give that lower action final state rejected with its resolution timestamp later than the higher action's claimed auto-approval timestamp. Leave the higher bound action autoApproved and effect-attested with the live matching rule. The lower rejected action has no commitment binding and no effect.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "Historically the drainer could not cross the lower pending manual gate. Reset replay leaves it rejected and therefore erases the obstruction."
    },
    {
      "id": "h08-outcome-unknown-reported-applied",
      "category": "M-annotation-trust",
      "variant": "bridge-behavior",
      "role": "endpoint",
      "attackerCapability": "bridge",
      "registeredAbsences": [],
      "platformChecksEngaged": [],
      "construction": "Start from the canonical manually staged proceed action with valid commitment binding. Leave its outer ledger row pending with no resolvedBy and no appliedAt, retain no effect attestation, and put the literal connector outcome unknown in the report note. Set report execution to applied rather than applied-unproven.",
      "expected": {
        "cf": "pass",
        "binding": "pass",
        "replay": "pass"
      },
      "note": "Supplies the missing applied-unproven-to-applied overclaim endpoint using the outer state that pinned source can actually retain after a thrown outcome-unknown failure."
    }
  ]
}
```

## 5. Checks found sound

- The Cloudflare OS clone is at the registered commit, and the key upstream facts were accurately identified: strict tool-trust classification, `readOnlyHint` bypass, per-gatekeeper ordered draining, manual-gate stopping, opaque outer action IDs, and the MCP at-most-once ambiguity.
- m01 is an honest demonstration of actual upstream `readOnlyHint` behavior. Its effect detection depends on modeled external attestation, but that dependency is visible.
- The coherent whole-store rewrite ceiling and unsigned-log limitation are explicitly registered. The defect is overbroad interpretation elsewhere, not concealment of the ceiling.
- SPEC §0 and PREREGISTRATION §3 do disclose that revisions, simulations, staged calls, and effects are modeled.
- The adapter-owned arguments digest is honestly distinguished from an upstream-native digest. The asymmetry with Study 014 is acknowledged; the missing protection is independent semantic derivation.
- Strict UTF-8 parsing, duplicate-key rejection, JCS canonicalization, domain-separated commitment hashing, and exact top-level commitment-field handling are sound foundations.
- Pinned-evaluator replay genuinely reruns the retained facts under the selected evaluator executable and compares the disposition.
- The layers do not consume matrix expectations, and registered absences are handled separately from layer verdicts. That part of validity/detection separation is real.
- The esbuild pivot and single `cloudflare:workers` stub seam are narrowly disclosed. The remaining issue is pin enforcement and the strength of the resulting claim, not hidden substitution.
- Both pilots are properly identified as pilots and demonstrate reproducible green behavior. Their evidentiary scope should remain limited to determinism and apparatus liveness.
- Study 013’s runtime integration and Study 015’s offline boundary experiment are meaningfully different regimes; the preregistration is right not to treat them as equivalent.

CODEX-015-R1-DONE
