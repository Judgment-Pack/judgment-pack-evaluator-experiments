# Round 2 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed,
static review only (the reviewer ran no tests, probes, compiler, builder or scorer).
Study tree reviewed at commit e038060. Verdict: DO-NOT-FREEZE.

A first launch of this round stalled before reading anything (the CLI blocked on an open
stdin) and was killed and relaunched with stdin closed; the transcript below is the
relaunched run, and the commit it reviewed is the one named above.

---

## 1. Verdict

**DO-NOT-FREEZE**

The rebuild contains real improvements, but the preregistration still has multiple freeze blockers:

- an accepted history can contain an additional unauthorized action;
- the registered MCP baseline is not reachable through either pinned MCP connector;
- the stage-time witness cannot establish historical drain lawfulness;
- evidence laundering is merely moved into the retained artifact store;
- holdout failures can still invalidate R1, while a registered publication can omit the holdout entirely.

Static review only. I ran no tests, probes, compiler, builder, or scorer. I authored no round-2 holdout cells.

## 2. Audit of the 14 round-1 dispositions

| # | Audit | Reason |
|---|---|---|
| 1 | **wrong** | The five derived fields are checked, but `serverTrust` and `simulationBasis` are wrongly contextual even though this scenario fixes them as `vetted` and `[]`. More decisively, cardinality considers only calls carrying the selected digest, so an additional same-subject call with another or no digest can pass. |
| 2 | **partial** | Missing or mismatched preimages now fail. But storing the approval-record bytes themselves under the evidence requirement makes the same laundering attack pass; the verifier proves only name→bytes→digest consistency. |
| 3 | **partial** | `not-engaged` is a substantive new outcome, the layer rename is real, and the `@validateRpc()` correction is source-accurate. README nevertheless says an unresolved judgment “passes the platform’s own live checks,” and the claim that no action-log export exists is false. |
| 4 | **wrong** | `appliedAt` really is a resolution stamp on approve and reject, but the witness replay is neither historical nor equivalent to the pinned drainer. It trusts forgeable rules/times, cannot model `continue`, apply failures, mid-pass rule changes, or single-flight reruns, and still reclassifies against untimestamped catalog/trust state. The study is wrong to say the reviewer’s catalog/trust concern was eliminated from the apparatus overall. |
| 5 | **partial** | Withdrawing `d01` is source-correct: MCP does not simulate. But `awaitDecision:true` does not suspend auto-eligible writes, and keeping nonempty `simulationBasis` acceptable is source-inconsistent. The surviving ID `d02-simulated-as-committed` is also stale. |
| 6 | **partial** | Moving the outer record to `pending` is correct. The fixture does not retain the actual inner MCP `failed`/`retryable:false` row, only an asserted enum, and the new predicate still accepts source-impossible outer/inner combinations. |
| 7 | **wrong** | Separate fixture and result collections exist, but shared typechecking, global gates, and the batched upstream runner still let holdout faults invalidate R1. After freeze, the scorer can publish `REGISTERED` R1 with `holdout not run`. |
| 8 | **real**, narrowly | Static source confirms `worker-configuration.d.ts` is tracked and referenced by the backend tsconfig. The scorer invokes a real server-side `ActionRecord`/`AutoApproveTagRecord` typecheck. This does not establish state-machine reachability or type every retained record, as adjacent prose claims. |
| 9 | **partial** | R1 is now honestly called regression-only and mutation constraints exist. Several constraints are factually incomplete and are checked only for nonempty prose; equal holdout prominence is not enforced. |
| 10 | **partial** | The provenance table is a material improvement, but it does not cover every consumed datum and misstates some observability/use. Catalog/trust timing and negative-evidence dependencies remain unregistered. |
| 11 | **partial** | Post-gate checks run and suppressed codes are visible. Only the first code is registered and adjudicated, so order still selects the headline finding and disappearance of a suppressed failure cannot falsify R1. Several supposedly closed report predicates are open. |
| 12 | **partial** | Pack/evaluator identity checks and duplicate-extension rejection are real. The generic `actionKindFor` encoding is reproduced correctly, but it is fed an invented `jps-tracker` scope that neither concrete MCP connector emits; label and ledger resource corroboration are also missing. |
| 13 | **partial** | Toolchain checks, independent corpus digests, early attempt creation, atomic output, and CI probe wiring are real. “Every non-null pin is enforced” and “every failure path produces RESULTS” remain false, and the wired probe does not test the MCP session claims attributed to it. |
| 14 | **partial** | The original b05/count/opaque-key edits are substantive, but new stale text remains: `PREREG-REVIEW.md:13` says five majors instead of six; `DEVIATIONS.md:61` says four pilots although three exist; and the reject `appliedAt` citation is `overseer.ts:7730`, not `:7729`. |

The three claimed source reversals resolve as follows:

- **Row 4:** the narrow source fact is right—`AutoApprovalDrainer` reads persisted descriptions and rules, not catalog/trust. The study’s broader claim that catalog/trust were over-collected is wrong because its separate `classificationCheck` still replays current, untimestamped catalog/trust.
- **Row 5:** the study is right that the MCP connector does not simulate, so withdrawing `d01` was necessary. Its universal suspension wording is too broad for auto-eligible writes.
- **Row 8:** the study’s earlier “backend typecheck is not reproducible” finding was wrong. The tracked worker configuration and committed codegen/typecheck structure support the withdrawal.

## 3. New findings

1. **Blocker — the central oracle accepts an additional unauthorized action.**

   Exact code: `adapter/verify.py:241-247`, `621-636`, `766-775`; claim: `PREREG-REVIEW.md:23` and `PREREGISTRATION.md:199-207`.

   `bound_calls` selects only calls whose `commitmentDigest` equals the current commitment. `binding-reuse` counts only those calls and their records. `unbound-execution` then returns success whenever any legitimate `applied_bound` exists.

   Starting from the valid baseline, add a second same-subject staged call and approved ledger row after the witnessed pass, with its digest absent or different. The original bound action keeps `applied_bound` nonempty. The extra call is ignored by derivation, target, arguments, revision, and reuse checks; its effect is masked by the legitimate action. A manual second approval need not engage the upstream classifier or drainer. Replay is unchanged. All three layers can therefore accept two executions under a map authorizing exactly one.

   In addition, `serverTrust` and `simulationBasis` are placed in `CONTEXTUAL_ACTION_FIELDS` at `adapter/commitment.py:154-167`. In this registered scenario both are derivable: trust is fixed as vetted and MCP’s basis is necessarily empty. A manually approved history coherently rewritten around `serverTrust:"byo"` passes; so does a nonempty basis backed by a synthetic approved premise.

   **Remedy:** identify relevant calls and effects independently of the supplied digest and enforce a unique call→ledger→effect lineage for the judged subject. Derive `serverTrust:"vetted"` and `simulationBasis:[]`; leave only the actual stage revision contextual. Also corroborate the stock ledger `resourceUrl`, action-kind label, and identifier uniqueness.

2. **Blocker — the registered baseline is not source-reachable through a pinned MCP connector.**

   Exact files: `adapter/commitment.py:28-35,149-167`; `harness/build_fixtures.py:119-127,166-198,317-323`; upstream `gatekeeper-mcp/src/mcp.ts:73-77,390-410`; `gatekeeper-mcp-portal/src/portal.ts:482-484,538-543`; `mcp-shared/src/session.ts:110-139`.

   The registered tuple is:

   - bare `https://tracker.example/mcp`;
   - trust `vetted`;
   - tool `create_work_item`;
   - action tag `jps-tracker:create_work_item`.

   Neither pinned connector emits it:

   - Generic MCP can use the bare endpoint, but its trust is always `byo` and its scope is `mcp:${endpointTag(endpoint)}`.
   - MCP Portal may be configured `vetted`, but its resource is portal-scoped, its tag begins `mcp-portal:…`, and its tools are portal/server scoped.

   The action-kind probe calls the generic helper directly with the invented `jps-tracker` scope; it bypasses both connector scope constructors.

   Every MCP write also constructs deterministic `describeCall` prose and explicitly adds `awaitDecision:true`, `autoApprovable:<boolean>`, and the connector-derived action kind. The fixtures instead use invented short prose, omit `awaitDecision`, omit explicit false values, and use the impossible tag. `neg-drain-skip` is especially invalid: it turns the same vetted, non-destructive, idempotent `create_work_item` tool with a live rule into a fabricated manual gate by omitting `autoApprovable`.

   Structural TypeScript compatibility cannot establish these generation and lifecycle invariants.

   **Remedy:** choose and register one concrete connector/configuration. Construct or statically validate descriptions, resource URL, trust, tool name, scope tag, and lifecycle fields through that connector’s pinned path. Rebuild the drain control with a genuinely non-auto-approvable tool.

3. **Blocker — the stage-time witness cannot prove historical drain lawfulness.**

   Exact code: `probes/ceremony.ts:59-75,214-358`; pinned `auto-approval.ts:25-93`; claim: `adapter/SPEC.md:246-258`.

   The witness is unsigned instrumentation supplied by the same retained-store writer being attacked. Adding a matching rule to `witness.rules` launders an autoapproval performed with no rule; stock state leaves no contradictory residue.

   The replay is also not equivalent to upstream:

   - upstream snapshots pending actions, reads each rule live, rechecks fresh state and may `continue`;
   - an apply callback can throw and lawfully stop the pass;
   - concurrent drain requests set the single-flight rerun flag;
   - rules and records can change while an earlier apply awaits.

   The harness instead gives each witness one timestamp and one static rule set, creates a fresh drainer for every witness, and uses an always-successful callback. It cannot reproduce any of those cases.

   `pendingAt()` compounds this:

   - invalid dates silently exclude records;
   - no `createdAt`/`appliedAt` ordering or lifecycle invariants are validated;
   - a source-impossible pending row with an old `appliedAt` erases an obstruction;
   - resolved legacy rows without `appliedAt` remain pending forever;
   - equality is ambiguous because the code uses `appliedAt >= at`, while fixtures set `at` equal to the action’s own resolution stamp.

   Finally, the callback ignores `rule.enabledBy`, so a forged `resolvedBy` attribution passes even though upstream persists the rule enabler.

   **Remedy:** retain an independently anchored append-only event trace containing pass-start queue, rule/catalog/trust state, fresh-state reads, apply results, attribution, and rerun events. Otherwise narrow the verdict to existential consistency with a self-asserted witness and abandon historical-lawfulness/store-attacker claims.

4. **Blocker — evidence laundering moved into `evidence-artifacts.json`.**

   Exact code: `adapter/commitment.py:247-285`; `adapter/verify.py:487-553`; claim: `adapter/SPEC.md:129-137`.

   The repair correctly rejects a digest with no retained preimage. It does not distinguish captured evidence from arbitrary bytes.

   Put the JCS approval-record bytes themselves under `sponsor-endorsement` in `evidence-artifacts.json`, set the backing kind to `artifact`, and hash those bytes. Every implemented check passes. This directly contradicts `verify.py:490-493`, which says hashing approval bytes and relabelling them fails.

   The caveats about authenticity, sufficiency, and truth are useful, but “lineage” and “what was captured” remain too strong. What is established is only store-internal requirement-key→bytes→digest consistency.

   **Remedy:** either rename and narrow the property to retained-preimage consistency, retract the semantic approval/observation-as-evidence detection claim, or bind independently authenticated acquisition/type metadata outside bridge/store control.

5. **Blocker — the holdout is neither isolated nor mandatory.**

   Exact code: `harness/score.py:213-226,670-769,777-860`; `harness/typecheck.py:88-103`; `harness/tests/test_study.py:201-208`; claims: `PREREGISTRATION.md:61-64,251-253`.

   Four independent defects remain:

   - The typecheck unconditionally scans `fixtures/holdout`, even when `--include-holdout` is false.
   - Holdout schema/fixture problems feed global `gate_problems` and terminal R1 invalidity.
   - Locked and holdout cells share one upstream-runner batch; a holdout-caused crash invalidates the attempt globally.
   - Once the preregistration digest is filled, omitting `--include-holdout` still produces a `REGISTERED` R1 verdict with `holdout not run`.

   The separation test merely searches source text for later disjoint row lists and misses the shared preconditions. The holdout version check also accepts any truthy value rather than the required version.

   Holdout construction is mostly faithful, and the `cf`→`upstream`/empty-check `pass`→`not-engaged` migration is defensible. However h08 is not purely mechanical: the authored prose placed the literal unknown outcome only in the report note, while `build_fixtures.py:875-885` additionally sets the new structured `connectorOutcome` field—the exact signal that causes the repaired verifier to diverge. That adaptation may be reasonable, but it is outcome-favoring and must not be described as part of the documented mechanical migration.

   **Remedy:** run locked validation/typecheck/upstream replay independently and publish R1 before entering a separate holdout phase whose faults affect only its own verdict. Require holdout inclusion for every registered publication. Disclose study-authored fixture adaptations separately from reviewer-authored prose and expectations.

6. **Major — the new report predicates still admit source-impossible histories.**

   Exact code: `adapter/verify.py:809-902`; `harness/build_fixtures.py:744-757`; claim: `adapter/SPEC.md:333-345`.

   - `applied` accepts missing, `pending`, or `failed` connector outcomes; it rejects only `outcome-unknown`.
   - `applied-unproven` requires neither an outer ledger record nor outer `pending` state.
   - `staged` permits a private staged call with no outer record, although MCP discards staging when `submitAction` fails.
   - The fixture does not retain the actual private MCP row with `state:"failed"`, `retryable:false`, and error; it retains only a free `connectorOutcome` enum on the modeled call.

   Consequently, the old impossible outer-approved/outcome-unknown history still passes if its report is changed to `applied-unproven`.

   **Remedy:** retain and join the actual private connector record. Require committed connector + approved outer row for `applied`; failed/non-retryable outcome-unknown + unresolved outer pending row for `applied-unproven`; and an MCP-consistent outer pending record for `staged`.

7. **Major — SPEC §0a is not a field-by-field provenance table.**

   Exact claim: `adapter/SPEC.md:48-83`.

   | Datum row | Audit |
   |---|---|
   | Tool name | **Understated as instrumentation.** The outer record preserves exact `description.actionKind.label = toolName`, as well as the tag and prose. |
   | Arguments | **Sound.** Outer visibility is rendered/truncated prose; the MCP store retains exact `args_json`; canonical digesting is adapter instrumentation. |
   | Stage/apply revisions | **Sound.** Both are instrumentation here. |
   | Commitment carrier | **Sound.** Wholly instrumentation. |
   | Simulation basis | **Source description sound**, but for this connector the only reachable value is empty; accepting nonempty values is not. |
   | Connector outcome/retryability | **Partial.** The MCP store has real state/retryability/error fields, but fixtures retain only an uncorroborated flattened enum. |
   | External effect attestation | **Sound.** Wholly instrumentation. |
   | Drain witness | **Correctly labelled instrumentation**, but the row understates its many self-asserted fields and evidentiary limitations. |
   | Approval identity / `autoApproved` | **Stock provenance correct; use claim wrong.** `autoApproved` is read, but `resolvedBy` is deleted before replay and never adjudicated. |
   | Lifecycle state | **Sound.** Three outer states versus five connector states. |
   | Evidence artifacts | **Soundly labelled non-platform instrumentation.** |

   Missing entirely are `createdAt`, `appliedAt`, `autoApprovable`, ledger/action identifiers, catalog annotations, `serverTrust`, observed routing records, and witness time/applied IDs/gatekeeper presence. Catalog and trust are particularly important because `classificationCheck` reads current, untimestamped values, allowing later drift to launder or falsely reject historical classification.

   Registry provenance is also incomplete: `d02` and `m02` depend on the completeness and emptiness of the effect-attestation store but omit `effectAttestation`; holdout cells have no modeled dependencies; and `drainSnapshot` is stale terminology for the witness.

   **Remedy:** enumerate every consumed field, its precise temporal meaning, and whether it is server-retained, client-published, connector-private, or instrumented. Register negative-evidence/completeness dependencies and a study-authored provenance sidecar for holdout fixtures.

8. **Major — platform-endorsement and runtime claims have reappeared.**

   Exact claims: `README.md:38-49,65-76,82-85`; `adapter/SPEC.md:27-30`.

   `not-engaged` itself is substantive and correctly implemented: a pass row engages at least one real upstream function; a no-check row says `not-engaged`.

   But README says an unresolved judgment “passes the platform’s own live checks.” The Durable Object path never runs. The defensible statement is that the two offline-replayed functions do not object.

   The claim that there is “no action-log export anywhere” is also false. Pinned `workshop-shared/src/api.ts:1422-1424` exposes `listActions()`, implemented at `overseer.ts:7548-7555` by projecting all stored actions. What is absent is a signed, complete, offline-verifiable server-record export.

   README also says every retained record is held to `ActionRecord`; `typecheck.py` checks ledger records and final autoapprove rules, not staged calls, connector outcomes, witnesses, gatekeeper catalogs, simulations, or effects.

   **Remedy:** use “offline-replayed functions,” narrow the export claim, and state the exact typecheck surface. Rename `d02-simulated-as-committed` and retract “every must-not is a registered cell” now that the simulation row is analytic only.

9. **Major — suppressed publication, new controls, and mutation constraints do not prove the registered claims.**

   Exact code: `adapter/verify.py:936-980`; `harness/score.py:904-913`; `harness/MATRIX.json:129-180,568-591`; `harness/build_fixtures.py:510-533,696-708`.

   Publishing suppressed codes fixes concealment, but not order dependence:

   - R1 compares only the registered first code.
   - Expected suppressed sets are not registered.
   - A suppressed detector can disappear without a divergence.
   - Details for suppressed codes are discarded.

   The two new controls are also weaker than described:

   - `neg-binding-control` appends a newline, exercising only the commitment-schema gate. The entire derivation/cardinality body could be dead and this control would still pass.
   - `neg-replay-control` meaningfully proves evaluator refusal, but also fails binding and its mutation constraint falsely says no other artifact changes; commitment, staged carrier, and report carrier are rebuilt.

   Other constraints are prose-only and inaccurate. For example, b05 changes arguments in addition to tool/action kind. The test checks only that each constraint string is nonempty.

   The new verdict codes have direct same-author reachability cases, and the implemented list matches the stated order. However derivation occurs in `_load_context` before the guarded check loop; semantically malformed but parseable facts can raise and become pipeline-invalid instead of the registered `action-derivation-mismatch`.

   **Remedy:** register and compare full failure sets, or make endpoint fixtures single-defect. Replace the binding control with a schema-valid coherent action substitution. Register machine-readable permitted JSON pointers and mechanically diff fixtures against named bases. Move derivation into the guarded check.

10. **Major — pin and terminal-output absolutes remain false.**

    Exact claims: `harness/PINS.json:3-35`; `PREREGISTRATION.md:270-278,310-318`; code: `harness/score.py:209-300,636-678`.

    Non-null values such as `cloudflareOs.pnpmVersion` and the jpack archive digest are not compared by the scorer. They may be enforced by installation instructions or CI, but that is not “every non-null pin.”

    The pre-freeze holdout refusal deliberately creates no `RESULTS.json`, and an existing attempt root exits before `ATTEMPT.json`, contradicting “every failure path persists a terminal pipeline-invalid RESULTS.”

    `test_upstream_probes.py:7-11` also says the wired probe demonstrates MCP no-simulation/`awaitDecision`; `upstream-probes.ts` tests neither session nor connector.

    **Remedy:** classify every registry member as scorer-enforced, CI-enforced, or descriptive. Narrow the output promise or write explicit terminal refusal artifacts. Correct the probe coverage description.

11. **Minor — retained text remains internally inconsistent.**

    Exact files:

    - `PREREG-REVIEW.md:13`: five majors should be six.
    - `DEVIATIONS.md:61`: three pilot directories exist, not four.
    - `PREREGISTRATION.md:52-55` versus `DEVIATIONS.md:61-64`: distinguish “expectations could have been corrected” from the claim that none actually were.
    - `adapter/SPEC.md:255`: rejection sets `appliedAt` at pinned `overseer.ts:7730`; line 7729 sets the state.

    **Remedy:** correct before freeze and regenerate all affected pins/manifests.

## 4. Decision register

**[D-6] Yes on ownership; no on claimed coverage.** The SPEC and preregistration clearly state that the map is adapter-owned, not a JPS or platform property. But README’s green summary says the full recorded action is derived, while only five of eight members are; trust and simulation basis are merely made self-consistent with attacker-controlled store values. Fix the split and the “live checks” wording.

**[D-7] No.** The witness is clearly labelled instrumentation globally, but that provenance disclosure does not make it historically sound. Locked metadata calls it a snapshot, holdout cells omit per-cell dependencies, and the replay cannot support lawfulness against the registered store attacker or pinned concurrency semantics.

**[D-8] Remove `simulationBasis` from this scenario, or derive it as necessarily empty.** A generalized field that accepts source-impossible nonempty values is harmful defense-in-depth. Preserve the hazard analytically until a separately registered, source-reachable simulating connector exists.

## 5. Checked and found sound

- The narrow runtime-validation correction is right: `ApprovalQueueImpl` carries `@validateRpc()` at pinned `overseer.ts:9428`.
- Withdrawing the simulated-dependent-write `d01` endpoint is correct because the MCP session performs no simulation.
- `appliedAt` is genuinely a resolution stamp set on both approval and rejection.
- The direction of the m02 correction—outer pending after a throwing ambiguous MCP apply—is source-correct.
- `not-engaged` is mechanically distinct from `pass`, and its explanation in the published matrix is clear.
- The holdout expectation migration is exactly the documented key renames plus empty-check `pass`→`not-engaged`; preserving the authored file was done correctly.
- The 27-cell, 19-endpoint, six-control counts are correct.
- Post-gate binding checks do run, and suppressed codes are published in JSON and Markdown.
- Pack/evaluator identity corroboration, duplicate-extension rejection, strict commitment parsing, and generic `actionKindFor` escaping are implemented.
- The scorer really invokes the server-side ledger/rule typecheck; the problem is its semantic and stated scope, not that it is fake.
- Independent pack and conformance-case digests, toolchain comparisons, early attempt creation, and atomic output code are present.
- Retained pilots are clearly labelled as pilots and support no frozen claim.
- Matrix expectations are not read by the layer implementations.

CODEX-015-R2-DONE
tokens used
415,520
