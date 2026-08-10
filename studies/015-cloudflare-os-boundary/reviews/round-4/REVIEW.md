# Round 4 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed,
static review only. Study tree reviewed at commit de872dc. Verdict: DO-NOT-FREEZE.

A first launch of this round was killed by the maintainer's own process-cleanup command
(a `pkill` pattern that matched its own command line) before it read anything; the
transcript retained is the clean relaunch.

---

## 1. Verdict: DO-NOT-FREEZE

Round 3’s repairs are substantive but incomplete. The study still has three implementation/fixture blockers and one claim-level blocker:

- The authorization oracle does not inventory all governed calls, ledger applications, and effects over the same tool/resource scope.
- The lifecycle and report predicates accept source-impossible histories while claiming strict or closed predicates.
- Several locked and prospective-holdout fixtures are not producible through the registered Portal deployment.
- The study expressly claims lineage that its tuple/cardinality ceremony cannot establish.

This matters especially because R1 is only a locked regression endpoint. The prospective content is the eight-cell holdout, and at least `h03` and `h04` are not constructed as authored. Twenty-seven familiar cells can establish exact regression concordance, but not the broader completeness, source-reachability, or lineage language that remains in the record.

Static review only. I executed no code, probes, tests, builders, compilers, or scorers; edited no files; and authored no round-4 holdout cells. The existing eight do not cover several bypasses below, but these now-known defects should first become ordinary regression tests rather than outcome-bearing holdout predictions.

## 2. Audit of round 3’s six dispositions

- **R3-1 — partial.** `subject_calls` genuinely scopes ordinary staged calls by tool and resolved resource, independent of digest, arguments, and executability (`adapter/verify.py:249-277`). Thus an additional normal changed-argument call is counted, and an ordinary call under inaction is refused.

  The rest of the governed activity does not share that scope:

  - Effects are still filtered by the exact derived arguments (`verify.py:306-319`). Under inaction, an effect against the governed tool/resource with changed arguments is invisible to `unbound-execution`; under the baseline, a second changed-argument effect hides behind the one canonical effect.
  - Approved applications are counted only by joining records to retained subject calls (`verify.py:714-725`). A manual-approved governed ledger row with no staged call is ignored.
  - Under an executable disposition, one governed call and approved row carrying no or another commitment digest satisfies cardinality one, while `_bound_pair` is empty and all target/argument checks skip. With no canonical effect, a report of `none` passes.
  - A well-formed second gatekeeper pointing at the same governed resource is counted, but duplicate gatekeeper IDs are not refused. Python resolves the first matching gatekeeper (`verify.py:321-325`), while the TypeScript layer’s `Map` keeps the last (`probes/ceremony.ts:133-136`), permitting inconsistent scope resolution.
  - A joined row may render different arguments, endpoint, or action in its title/description; those strings are never corroborated.
  - `adapter/SPEC.md:342-346` still says subject identity includes exact arguments, contradicting both the disposition and current call-scoping code.
  - The claimed two attack-shape regressions do not exist. `test_reachability.py:288-303` is an unlabelled same-argument twin, and `:306-338` is canonical-argument inaction. Neither constructs the changed-argument twin claimed at `PREREG-REVIEW.md:116`.

- **R3-2 — partial.** Duplicate `(gatekeeperId, action)` pairs are refused within staged calls and within ledger action rows (`verify.py:684-700`). For the single digest-bound pair, ledger `resourceUrl`, action-kind tag, and a present label are checked (`:737-765`).

  This is not uniqueness or corroboration “on every path that matters.” Ledger `id` and gatekeeper IDs are not unique-checked; there is no staged-call↔ledger-row bijection; orphan and unbound rows receive no target corroboration; and the full rendered description is unchecked. The no-call→effect-lineage limitation appears only in `PREREG-REVIEW.md:117,125`. It is absent from the normative contract and contradicted by `PREREGISTRATION.md:353-355` and the causal “account for them” wording in `SPEC.md:353-356`.

- **R3-3 — partial.** The primary reconstruction now supplies the right kinds of `describeCall` inputs: Portal’s two-part scope label and its bare endpoint. `b05`’s destructive tool is correctly non-auto-approvable, and `m02`/`h08` correctly classify the canonical vetted/idempotent tool as auto-approvable.

  Exact equivalence is not established. `tracker portal / tracker` requires unregistered `MCP_PORTAL_NAME` and upstream display-name inputs; `resourceTitle:"Tracker"` requires an undeclared workspace `setTitle` override. More importantly, `b01`, `b04`, `o01`, `h03`, and `h04` contain joined-record or path shapes the registered deployment cannot produce, detailed below.

- **R3-4 — partial.** The exact old obstruction-erasure shape, `pending` plus `appliedAt`, is refused when a drain witness for that gatekeeper is actually replayed. A resolved row without `appliedAt`, invalid dates, and resolution-before-creation are similarly refused. Missing `resolvedBy` fails for a well-formed witnessed auto-approval whose rule supplies an enabler ID.

  And yes: `adapter/SPEC.md:300-311` now contains the promised normative paragraph. It explicitly states that the witness is self-asserted, admits rule-insertion laundering, and names throwing apply, mid-pass rule changes, fresh-state `continue`, and single-flight reruns.

  “Strict lifecycle equivalence” is nevertheless false. Upstream writes approval fields together at `overseer.ts:2481-2498` and rejection fields together at `:7727-7732`; `pendingAt` checks only `state ↔ appliedAt`.

  | Ledger shape | Ceremony treatment |
  |---|---|
  | `pending` + `appliedAt` | Refused during an engaged same-gatekeeper replay; accepted without examination when no `autoApproved:true` row engages the drain. |
  | `approved`/`rejected` without `appliedAt` | Same: refused only on an engaged replay. |
  | Resolved row with `appliedAt < witness.at` | Excluded from the reconstructed queue. |
  | `pending` + `resolvedBy`, no `appliedAt` | Included; the impossible attribution is not rejected. |
  | `pending` + `autoApproved:true` + matching `resolvedBy`, no `appliedAt` | Included, replayed, and accepted with a matching witness, although upstream could not leave that final state. |
  | `rejected` + `autoApproved:true` + matching attribution + `appliedAt >= witness.at` | Included and accepted; replay changes its temporary copy to approved but never compares that with the retained final rejection. |
  | Same `resolvedBy.id`, different valid name/type | Accepted because only `.id` is compared. |
  | Parseable but non-RFC-3339 timestamps | Accepted via permissive `Date.parse`. |
  | `appliedAt == witness.at` | Treated as pending; the baseline depends on this equality without normatively defining its instant semantics. |

  A witness rule lacking an enabler ID also disables mandatory attribution because both checks are conditional on `expected !== undefined`; witness objects are neither runtime-schema-validated nor covered by the fixture typecheck. `SPEC.md:291-293` still calls attacker-supplied timestamps “immutable” and reconstruction “sound.”

- **B4 residual — partial, not fixed.** `SPEC.md:43,142-146` and the substantive verifier caveat at `verify.py:520-531` now state retained-preimage consistency accurately. However, capture/lineage language remains in `PREREGISTRATION.md:353-355,393-395`, `commitment.py:260-285`, and verifier diagnostics at `verify.py:389,543,556`.

- **B5 residual — partial; the “declared” portion is wrong where it matters.** Separate runner batches, row collections, and verdict objects are real, and frozen runs cannot omit the holdout. But `MATRIX-HOLDOUT.json` is still unconditionally pinned and hashed, the whole-study manifest includes it, both registries share one parse scope, and publication occurs only after holdout processing (`score.py:692-744,909`; `make_manifest.py:24-45`). A malformed or mismatched holdout artifact can therefore suppress R1 publication. The alleged holdout-only typecheck calls `typecheck_problems(include_holdout=True)`, which scans baseline, locked mutations, and holdout together (`typecheck.py:88-109`).

  Treating those as attempt-scope preconditions is defensible, but then `PREREGISTRATION.md:63-64` and `score.py:22-25` must say only that holdout cell outcomes do not enter the R1 calculation—not that nothing in the holdout can affect R1 or its publication.

## 3. Decisions on the two open limitations

1. **No unique call→effect lineage — (iii), fatal to claims made elsewhere as currently written.**

   Correct cardinality can coexist with substituted causation:

   1. Bound call A has one approved outer row but produces no effect.
   2. An out-of-band or no-longer-retained call B invokes the same resource/tool/arguments.
   3. The one retained effect attestation describes B’s tuple but carries no call or ledger identity.

   `applied_bound` is one, `matching_effects` is one, and `unbound-execution` accepts at `verify.py:831-847`. The retained bytes cannot distinguish this history from A causing the effect.

   Narrow R1 concordance does not require causal lineage; it could freeze with this as category (i) after an explicit non-claim. But the current record says “binding and lineage” (`PREREGISTRATION.md:353-355`), says approved applications “account for” effects (`SPEC.md:353-356`; `verify.py:824-826`), and describes authorization through an exact mediator (`MATRIX.json:565`). Either add an identity-bearing call→outer-row→private-result→effect join, or normatively state that the ceremony proves only tuple equality plus aggregate cardinality and remove causal verbs.

2. **Fixtures bypass the real connector path — (ii), must be fixed before freezing as instantiated.**

   The direct call is not inherently disqualifying. Pinned `session.ts:110-135` transparently passes `host.serverName`, `host.endpoint`, catalog tool, arguments, mode, and classification source to pure `describeCall`, then adds fixed fields. For this study’s offline-record claims, exact mechanical reconstruction can suffice without executing a live facet/session.

   Current reconstruction is not exact:

   - The bare endpoint is correct.
   - The label formula is correct, but the exact configured Portal name and upstream display name are not registered.
   - `resourceTitle:"Tracker"` is not the connector default and needs an undeclared `setTitle("Tracker")`.
   - Fresh manual approvals omit `autoApproved:false`, although the current approval path always stores it.
   - `b01` and `h03` stage changed arguments but retain prose generated from canonical arguments.
   - `b04`/`h04` use another endpoint and server scope while retaining `tracker_create_work_item`; the Portal permits one endpoint per deployment and server scope `other` cannot expose a `tracker_…` tool. They also reuse the primary description/tag.
   - `o01` hand-writes an observation that none of the registered Portal observation paths emits.
   - Rejected obstruction calls retain the synthetic flattened outcome `committed` rather than the private connector’s rejected state.

   Therefore direct construction is sufficient only after registering exact deployment/name/title inputs, validating scope and classification per call, comparing the entire generated description, and correcting the joined traces. The governing documents must also replace “actually emits” with “synthetically reconstructed from registered inputs” and scope source-faithfulness to baseline/unmutated fields; intentional forgeries such as `h04` obviously cannot be connector-emitted.

## 4. Numbered findings

1. **Blocker — the governed-action inventory is not closed.**  
   Exact code: `adapter/verify.py:249-319,661-847`. Claims: `PREREG-REVIEW.md:116`; `adapter/SPEC.md:342-356`.

   Changed-argument effects, orphan approved ledger applications, a sole non-bound governed call/application, and duplicate-gatekeeper resolution can all evade the intended authorization relationship. Remedy: form independent tool/resource-scoped inventories for calls, ledger applications, and effects; require zero of each under inaction and exactly one uniquely bound derived call/row under execution; refuse unjoinable applications and non-authorized arguments; validate unique gatekeeper and ledger IDs.

2. **Blocker — lifecycle and report predicates remain source-incomplete.**  
   Exact code: `probes/ceremony.ts:229-267,312-400`; `adapter/verify.py:922-965`. Claims: `adapter/SPEC.md:291-311,384-400`.

   In addition to the accepted lifecycle shapes above, `staged` permits a private staged call with no outer row even though MCP discards the private action when `submitAction` fails; `applied` accepts absent, pending, or failed connector outcomes; and `applied-unproven` requires neither an unresolved outer pending row nor any outer row. `m02` claims a retained failed/non-retryable private record but retains only a flattened `connectorOutcome` enum.

   Remedy: globally validate current-source lifecycle tuples before the drain’s early return, validate witness schemas/RFC timestamps, compare full attribution and retained final state, and either retain/join the real private connector row or withdraw source-state reachability claims for these enums.

3. **Blocker — locked and holdout constructions contain incidental impossible fields.**  
   Exact construction: `harness/build_fixtures.py:191-227,707-739,754-765,848-920`. Claims: `MATRIX.json:436-487,542-565`; `MATRIX-HOLDOUT.json:47,63`; `PREREGISTRATION.md:130-135`.

   `b01`, `b04`, and `o01` are not the bridge-only traces their constraints claim; `h03` and `h04` are not the reviewer-authored constructions. This is especially serious because the holdout is the study’s only prospective stratum.

   Remedy: regenerate each row from its own tool/arguments/target; use valid same-Portal server scopes and corresponding wire tools; create a real observation route; emit current-path lifecycle fields including `autoApproved:false`; correct frozen bytes and manifests without changing reviewer-authored expectations.

4. **Blocker — the declared lineage limitation contradicts governing claims.**  
   Exact claims: `PREREGISTRATION.md:353-355`; `SPEC.md:353-356`; `MATRIX.json:565`; implementation `verify.py:306-319,824-847`.

   The one-for-one substituted-effect construction passes. Remedy: either add stable effect identity or register a normative causal-lineage non-claim in PREREGISTRATION, SPEC, README, report semantics, and matrix prose.

5. **Major — holdout isolation is narrower than advertised.**  
   Exact code: `harness/score.py:692-760,791-814,909`; `harness/make_manifest.py:24-45`; claims `PREREGISTRATION.md:63-64` and `score.py:22-25`.

   Cell-level results are separated; artifact loading, pinning, manifest validity, and publication are not. Remedy: either isolate registries/manifests/publication completely, or explicitly qualify the guarantee to R1’s arithmetic and disclose attempt-scope invalidation.

6. **Major — evidence, provenance, pin, and typecheck absolutes remain false.**  
   Exact claims include `PREREGISTRATION.md:89-95,112-114,141-149,353-355`; `README.md:69-73,103,107`; `PINS.json:3,23,26`; `SPEC.md:73`.

   The implementation establishes retained-preimage consistency, not capture. Catalog annotations and trust are not stock outer-log fields. The typecheck covers ledger records and final auto-approval rules, not every retained record. The enforcement classification omits multiple pin leaves and is not consumed by the scorer. `PINS.json` still says no action-log export exists despite upstream `listActions()` at `overseer.ts:7548-7555`. `d02` and `m02` depend on absence/completeness of effect attestations but omit `effectAttestation` from `modeledDependencies`.

   Remedy: reconcile every claim with the exact surface; mechanically validate an exhaustive pin classification; register negative/completeness dependencies; and narrow the export claim to absence of a signed, complete, offline-verifiable export.

7. **Major — churn tests and registries assert less than their names claim.**  
   Exact examples:

   - `test_reachability.py:288-338` does not contain the claimed changed-argument regression.
   - `test_study.py:311-349` checks prefixes and field presence, ignores holdout/observations/full descriptions, and only checks the label if the tag already equals the expected primary tag—masking `b04`.
   - `test_study.py:368-380` detects positive use of effects but misses cells relying on their absence.
   - `MATRIX.json:161` says no other artifact changes in `neg-replay-control`, while the builder also changes commitment and binding/report carriers.
   - `README.md:26-32` says 19 endpoints span six families; the corrected governing count is five endpoint categories.
   - `README.md:88-91` claims every boundary “must not” is a cell despite the withdrawn simulated-write row now being analytic-only.
   - README status mentions only round 1, and `DEVIATIONS.md:101-106` simultaneously says `simulationBasis` was removed and remains registered.
   - `adapter/commitment.py:68` leaves unused `BACKING_KINDS`.

   Remedy: replace shape/string meta-tests with exact per-call reconstruction and accepted-bypass regressions; mechanically enforce mutation pointers and dependency completeness; then perform a full terminology/status/dead-code pass.

## 5. Checked and found sound

- The upstream clone is at the registered `b2a51b5426398c8353d9d4dd984bd525121ab5f2` pin.
- Ordinary inaction and changed-argument staged calls are now within call scope.
- Duplicate staged/ledger join pairs are refused, and bound-row structural resource/tag/label corroboration is real.
- Exact-tuple surplus effects are now counted rather than treated existentially.
- The old pending-plus-resolution-stamp obstruction is refused on an engaged replay.
- Missing attribution for a well-formed witnessed auto-approval is refused.
- SPEC §5 contains the full promised self-witness limitation paragraph.
- Primary Portal endpoint forwarding, scoped resource grammar, wire-tool prefix, action-kind derivation, and current classifier values are correct, conditional on registering the exact deployment names.
- `implementsRevert:false`, `awaitDecision:true`, and explicit `autoApprovable` are the correct action-description fields.
- The evidence verifier correctly enforces retained requirement-keyed preimage existence and digest equality.
- The server-side TypeScript check is real for its actual scope: ledger `ActionRecord`s and final `AutoApproveTagRecord`s.
- Locked and holdout upstream runner batches and row/verdict collections are separate, and a frozen run cannot silently omit the holdout.
- The static counts are correct: 27 locked cells = 19 endpoints, 6 controls, 1 demonstration, and 1 descriptive row.
- R1 is correctly described in PREREGISTRATION as a locked regression endpoint, not a prospective prediction; R2 is correctly only a matrix restatement.
- The disposition→action map is clearly adapter-owned rather than a JPS or platform authorization rule.

## 6. What a reader may legitimately conclude if this freezes as-is

A reader may conclude only that the frozen apparatus reproduces its registered per-layer outputs on 27 selected, largely synthetic constructions; that the commitment’s derived fields agree with the retained judgment for the single digest-bound canonical call; that requirement-keyed retained bytes hash to their declared digests; and that two pinned upstream policy functions were replayed offline over study-selected records. A reader may not conclude that every governed execution was uniquely authorized, that an attested effect came from the approved call, that every trace is producible by the registered Portal path, that retained lifecycle history is source-lawful, that the holdout cannot suppress R1 publication, that every pin/record is enforced/typechecked, or that the cells exhaust the boundary analysis.

CODEX-015-R4-DONE