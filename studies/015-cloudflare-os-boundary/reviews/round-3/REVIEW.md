# Round 3 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed,
static review only. Study tree reviewed at commit 08cae95. Verdict: DO-NOT-FREEZE.

**Timing note, material to reading this review.** A pre-freeze adversarial self-audit ran
in parallel with this round and independently found several of the same defects; its fixes
landed in commit adefe9b while this reviewer was still reading 08cae95. Where a finding
below was already closed by that commit, the disposition table says so and names the
convergence — two independent adversarial passes reaching the same defect is evidence
about the defect, not an excuse.

---

## 1. Verdict: DO-NOT-FREEZE

The rebuild contains real work, but it does not close the central authorization, connector-faithfulness, drain-witness, or holdout-isolation defects. Several round-3 dispositions describe fixes more strongly than the implementation supports.

Static review only. I ran no tests, probes, compiler, builder, runner, or scorer, and authored no round-3 holdout cells. Paths below are relative to `studies/015-cloudflare-os-boundary/` unless identified as upstream.

## 2. Audit of the 11 round-2 dispositions

| Row | Audit | Reason |
|---|---|---|
| B1 | **partial** | `serverTrust` is genuinely derived, and exact-subject surplus calls/effects are counted for executable dispositions. But `subject_calls` is empty whenever the map authorizes no action, differently-rendered or changed-argument actions remain outside the subject filter, and no unique call→ledger→effect lineage exists. The central oracle can still accept unauthorized execution. |
| B2 | **partial** | The Portal resource URL, wire-tool convention, double-encoded tag, and deployment trust switch are substantially correct. The `describeCall` context is invented, several `autoApprovable` values contradict the pinned classifier, and multiple locked/holdout fixtures remain impossible Portal traces. |
| B3 | **partial** | The verdict name and some commentary now narrow the claim to a self-asserted witness. `pendingAt` still accepts contradictory lifecycle rows, attribution remains optional, and SPEC §5 does not contain the laundering/concurrency limitations the disposition says it contains. |
| B4 | **partial** | The verifier comment correctly admits laundering and implements retained-preimage hashing. SPEC, PREREGISTRATION, and `commitment.py` still use the stronger “captured artifact,” “lineage,” and “what was captured” language. |
| B5 | **partial** | Separate runner batches, a distinct holdout verdict, and mandatory inclusion after freezing are real. Global pin/manifest/parse gates can still erase R1, the holdout typecheck is neither holdout-only nor a precondition, and the h08 adaptation is not registered where executable claims require it. |
| M6 | **partial** | Rejecting `applied` with `outcome-unknown` is real and the disposition admits the missing private-row join. Other source-impossible report states still pass, while matrix prose claims data the fixture does not retain. |
| M7 | **partial** | Several provenance rows were added, but catalog/trust provenance is misstated, `observedCalls` is missing, negative effect-store dependencies remain undeclared, and `drainSnapshot` survives. |
| M8 | **wrong** | It says the claims were narrowed everywhere. The disproved action-log, “every retained record,” live/platform, and exact typecheck-surface claims remain in governing documents and code comments. |
| M9 | **partial** | Some limitations are now admitted and two regressions exist. Mutation constraints are still not mechanically enforced and one is factually false; tests mainly assert strings or field shapes, not the advertised properties. |
| M10 | **wrong** | An enforcement classification map was added, but it is incomplete and not consumed by the scorer. “Every pin” and “every non-null pin” absolutes remain in README, PREREGISTRATION, and `score.py`. |
| M11 | **partial** | The headline counts were corrected, but the rejected `overseer.ts:7729` citation survives in two current files, and churn introduced or retained several other stale Portal/simulation/status statements. |

The three round-1 dispositions that round 2 marked wrong—rows 1, 4, and 7—are not fully repaired:

- Row 1 received substantive changes, but the authorization/cardinality oracle still has accepted bypasses.
- Row 4 was mainly re-described. The narrower witness still accepts contradictory source states and optional attribution.
- Row 7 gained separate batches and mandatory inclusion, but holdout faults still flow through global gates and can suppress R1.

## 3. New findings

### 1. Blocker — zero-action histories still bypass subject cardinality

Exact code: `adapter/verify.py:248-279,636-660,799-822`. Claims: `PREREG-REVIEW.md:79`; `adapter/SPEC.md:323-327`.

`Context.subject_calls` returns an empty list whenever `derived is None`, which is every inaction disposition. A coherent accepted history can therefore retain:

1. a valid clarify/unresolved/not-applicable judgment with a null action commitment;
2. a staged call to the registered resource/tool with no commitment digest or another digest;
3. a manually approved ledger record for that call;
4. no matching effect attestation and `execution: none`.

The action-map, cardinality, target, arguments, report, and upstream checks all ignore that call. This is authorization cardinality zero with an executed action, not merely a labeling discrepancy.

For executable dispositions, a second call with changed arguments also falls outside the exact-arguments subject filter; its effect is likewise excluded from `matching_effects`.

Remedy: derive an authorization scope independently of whether the disposition produces an action. Inventory all retained calls, applications, and effects within that scope and enforce cardinality zero or one against the actual authorization.

### 2. Blocker — action identity and execution attribution remain unbound

Exact code: `adapter/verify.py:285-321,721-747,799-822`. Claim: `adapter/SPEC.md:62`.

`records_for` joins only on `(gatekeeperId, action)`. Effects contain no call or ledger identity, and `unbound-execution` compares aggregate counts. It cannot establish which call caused an effect.

The verifier also does not corroborate:

- ledger `resourceUrl`;
- `description.actionKind.label`;
- rendered `describeCall` arguments against structured staged arguments;
- the full `ActionDescription`;
- unique gatekeeper/action identifiers.

A store writer can retain canonical structured arguments while rendering a different resource or argument set into the ledger description. An approved canonical application plus a substituted effect can satisfy the aggregate count without unique lineage.

Remedy: enforce identifier uniqueness and a unique call→outer record→connector result→effect relationship. Validate the complete connector-produced description, structural resource, tag and label against the same staged call.

### 3. Blocker — the Portal scenario is still not connector-produced

Exact study code: `harness/build_fixtures.py:68,353-376`; `fixtures/baseline/ledger.json:16-17`. Claims: `PREREGISTRATION.md:130-135`; `adapter/SPEC.md:224-234`; `README.md:66-69`; `harness/MATRIX.json:4`.

Pinned upstream:

- `gatekeeper-mcp-portal/src/portal.ts:322-330,494-500,557-560`
- `mcp-shared/src/session.ts:110-135`

The builder calls upstream `describeCall` with:

- `serverName = "tracker"`;
- `endpoint = "https://tracker.example/mcp#server=tracker"`.

The actual Portal supplies a two-part scope label, `<configured portal name> / <upstream display name>`, as `serverName`, and supplies the bare configured endpoint to `describeCall`. Consequently, the baseline title, bold server heading, and fragment-bearing endpoint prose are byte-for-byte impossible for the registered Portal path. `resourceTitle: "Tracker"` additionally requires an unregistered workspace title override.

The weak “connector-shaped” test at `harness/tests/test_study.py:278-297` checks prefixes, suffixes, types, and field presence, not actual description bytes. `probes/upstream-probes.ts:197-217` still tests the old `jps-tracker` generic-encoding example rather than the Portal construction path.

There are further classifier contradictions:

- `m02` sets `autoApprovable:false` at `build_fixtures.py:816` for the canonical vetted, non-destructive, idempotent tool, which the pinned classifier makes true.
- `h08` repeats that contradiction at `build_fixtures.py:947`.
- `b05` leaves `autoApprovable:true` for a destructive tool.
- `b04` and `h04` use a bare second resource with Portal trust/tool fields; the Portal rejects unscoped grants.

The trust switch itself is real: `MCP_PORTAL_TRUST_ANNOTATIONS=true` can produce `vetted`. A real deployment must also configure `MCP_PORTAL_URL` and deterministic display-name metadata, which the study does not register.

Remedy: register the complete Portal deployment configuration and construct descriptions through its actual facet/session path. Regenerate every fixture and assert full description bytes plus exact classification fields.

### 4. Blocker — the narrowed drain oracle still accepts contradictory source states

Exact code: `probes/ceremony.ts:233-245,368-380`. Claim: `PREREG-REVIEW.md:81`; `adapter/SPEC.md:280-292`.

`pendingAt` accepts a record whose state is `pending` but which already has `appliedAt`. Depending on the timestamp, it then excludes that record from the reconstructed pending queue. That is precisely the source-impossible obstruction-erasure defect round 2 identified.

Attribution comparison fails only when both the expected and claimed identifiers are present. Deleting `resolvedBy` can therefore pass instead of failing.

SPEC §5 still calls timestamp reconstruction “sound” and does not state the self-witness laundering, throwing-apply, mid-pass rule-change, `fresh`-recheck, or single-flight limitations that the disposition attributes to it.

Remedy: enforce strict lifecycle equivalence, timestamp format and ordering, explicit equality semantics, and mandatory attribution for witnessed automatic resolutions. Put the complete existential/self-asserted limitation in normative SPEC §5 and remove “immutable” or “sound” language about attacker-supplied history.

### 5. Blocker — holdout faults can still erase the locked result

Exact code:

- `harness/score.py:606-628,669-741,908`
- `harness/make_manifest.py:24-45`
- `harness/typecheck.py:88-109`

Claims: `PREREG-REVIEW.md:83`; `PREREGISTRATION.md:61-64,335-336`.

The scorer:

- hashes `MATRIX-HOLDOUT.json` before the separate holdout phase;
- parses locked and holdout registries in one exception scope;
- applies global pin and whole-study-manifest gates;
- includes the holdout registry and holdout manifests in that global manifest;
- publishes nothing until after holdout processing.

An invalid holdout registry or manifest can therefore trigger global terminal invalidity and publish zero locked rows. Because frozen execution requires `--include-holdout`, this path cannot be avoided.

The holdout typecheck also is not the claimed independent precondition:

- `include_holdout=True` checks baseline, locked mutations, and holdout together;
- the holdout runner executes before this typecheck;
- failed holdout typechecking does not prevent per-cell holdout adjudication from being populated.

The isolation tests at `harness/tests/test_study.py:174-183,207-214` search for selected source strings and do not exercise these control-flow properties.

Remedy: give locked and holdout separate registries, manifests, pin gates, exact typecheck scopes, runner phases, and publication sinks. Finalize and durably preserve R1 before loading any holdout-controlled input.

### 6. Blocker — three prospective holdout constructions are not faithful joined traces

Exact files:

- `harness/MATRIX-HOLDOUT.json:47,63,133-142`
- `reviews/round-1/MATRIX-HOLDOUT.authored.json`
- `harness/build_fixtures.py:868-905,944-951`

Defects:

- **h03:** the authored construction says staged call and ledger row carry substituted arguments. The builder substitutes only structured staged arguments; ledger prose remains rendered from the canonical arguments.
- **h04:** the second resource is an impossible bare-resource/Portal hybrid, while its description still names the original endpoint. The fixture also changes the authored `create_work_item` tool to `tracker_create_work_item` without registering that scenario migration.
- **h08:** the fixture sets connector-derived `autoApprovable:false`, although the pinned classifier produces true. A missing user rule is enough to leave the action pending; falsifying the connector field is unnecessary and source-impossible.

The structured `connectorOutcome` added to h08 is disclosed only in `PREREG-REVIEW.md`. The current registry still describes the migration as mechanical, and `build_holdout` claims the fixtures are built exactly as authored.

Remedy: correct the joined traces without altering the reviewer-authored expectations. Add a frozen study-authored adaptation sidecar for every non-mechanical Portal or schema migration.

### 7. Major — evidence semantics remain stronger than retained-preimage consistency

The caveat in `adapter/verify.py:519-533` is accurate. Governing prose is not:

- `adapter/SPEC.md:43,134-142` says “captured evidence artifacts” and “lineage”;
- `PREREGISTRATION.md:350-354` says the digests assert “what was captured”;
- `adapter/commitment.py:259-284` repeats captured-artifact semantics.

The implementation establishes only requirement key → retained bytes → digest. A bridge can store approval-record bytes under an evidence requirement, label them an artifact, and pass.

Remedy: consistently use “retained requirement-keyed preimage consistency.” Remove capture, acquisition, provenance, and lineage implications unless independently anchored metadata is added.

### 8. Major — `simulationBasis` was removed from the commitment but not from the retained-store boundary

The active commitment schema and registered fixtures genuinely remove `simulationBasis`. However, `adapter/verify.py:361-371` accepts `platform.json` without a closed staged-call schema, while `probes/ceremony.ts:474-485` merely casts parsed JSON. A legacy staged call carrying `simulationBasis`, or a top-level `simulations` collection, is silently accepted and ignored.

Current documentation is contradictory:

- `README.md:20-25` still includes simulation basis in the commitment;
- `DEVIATIONS.md:42-46` says it was removed;
- `DEVIATIONS.md:66-71` says it remains registered and reachable;
- `d02-simulated-as-committed` remains a stale identifier.

Remedy: validate a closed Portal staged-call schema and reject legacy simulation fields. Reconcile README, DEVIATIONS, registry IDs, and analytic-only limitation wording.

### 9. Major — report predicates still admit source-impossible histories

Exact code: `adapter/verify.py:897-940`; construction: `harness/MATRIX.json:690-713`.

`applied` still accepts missing, `pending`, or `failed` connector outcomes. `applied-unproven` does not require an unresolved outer pending row. `staged` permits no outer record.

The m02 prose says a failed, non-retryable private connector action is retained, but the fixture contains only a flattened `connectorOutcome` enum—no private row, retryability, error, or joined state.

Remedy: retain and join the actual private connector record, or explicitly withdraw every source-state-reachability claim and describe these as instrumentation-only enums.

### 10. Major — provenance, pin, and typecheck claims remain incomplete

Examples:

- `adapter/SPEC.md:73` classifies catalog annotations and trust as stock outer-log fields, but upstream `ActionRecord` contains neither.
- `classificationCheck` consumes `platform.observedCalls` at `probes/ceremony.ts:165-172`, but SPEC §0a and m01’s modeled dependencies omit it.
- d02 and m02 depend on completeness/absence of effects but omit `effectAttestation`.
- `drainSnapshot` remains in registry vocabulary.
- `harness/PINS.json:3` says every member is classified, but numerous leaf members—including connector/env, path, manifest, and source-unmodified fields—are absent from the map.
- `harness/score.py:208-304` hard-codes enforcement and does not consume or cross-check that map.
- “Every pin” or “every non-null pin” survives at `README.md:104`, `PREREGISTRATION.md:112-114`, and `score.py:27-35,208-209`.
- “Every retained record” survives at `README.md:108`, `PREREGISTRATION.md:89-93`, `PINS.json:23`, and `typecheck.py:1`. Actual typechecking covers ledger records and final auto-approval rules only.
- `PINS.json:26` still says no action-log export exists, despite upstream `listActions()`.

Remedy: define and mechanically enforce an exhaustive leaf-path classification; enumerate every consumed datum and negative/completeness dependency; state the exact typecheck surface everywhere.

### 11. Major — churn has left weak tests, false constraints, and stale claims

- `_load_context` calls `derived_action` outside the guarded binding-check loop at `adapter/verify.py:398-400`; structurally malformed but parseable facts can raise globally rather than yield a registered derivation failure.
- `neg-replay-control` says no other artifact changes at `harness/MATRIX.json:156-180`, while `build_fixtures.py:587-598` also changes the commitment, staged carrier, and report carrier.
- The mutation-constraint tests require prose to be nonempty; they do not mechanically diff registered JSON pointers.
- The Portal test checks shapes, not source equality.
- The holdout-isolation tests inspect source strings, not dataflow or failure behavior.
- `adapter/SPEC.md:113-120` retains the old bare resource, old tool, and `jps-tracker` tag in its normative schema example.
- `harness/build_fixtures.py:215-217` and `probes/ceremony.ts:229-232` still cite `overseer.ts:7729`; the assignment is at line 7730.
- README status records round 1 but omits the second DO-NOT-FREEZE and rebuild.
- README/MATRIX claim Portal is the only pinned connector with any auto-approvable write. Pinned Google Docs writes are a counterexample. The defensible statement is only that Portal is the one of the two MCP connectors that can auto-approve this annotated MCP write.

Remedy: replace textual/meta-tests with behavioral or exact static invariants, mechanically enforce mutations and connector generation, guard derivation, and perform a complete terminology/citation pass.

## 4. Checked and found sound

- The upstream clone is at the registered `b2a51b5…` commit and was unmodified.
- `MCP_PORTAL_TRUST_ANNOTATIONS=true` genuinely makes Portal trust `vetted`; this is reachable deployment configuration.
- The registered scoped resource URL, `tracker_` wire-tool prefix, and double-encoded Portal action-kind tag follow the pinned constructors.
- `implementsRevert:false`, `awaitDecision:true`, explicit `autoApprovable`, and action-kind fields are the correct submitted field set.
- `neg-drain-skip` now uses a genuinely non-auto-approvable second tool.
- `serverTrust` is genuinely derived.
- `simulationBasis` is absent from the commitment schema, active verdict vocabulary, and registered fixtures; the commitment schema rejects it as an extra action field.
- Retained-preimage existence and digest equality are implemented correctly for the narrowed property.
- For a successfully loaded context, the SPEC’s numbered binding-check order matches `BINDING_CHECKS`.
- `not-engaged` is distinct from `pass`, and the two named upstream policy functions are replayed rather than presented as a live Durable Object invocation.
- Locked and holdout runner calls are separate batches; the initial locked typecheck excludes holdout; post-freeze omission of `--include-holdout` is refused.
- Static registry counts are correct: 27 locked cells, comprising 19 endpoints, 6 controls, 1 demonstration, and 1 descriptive row. The 8 holdout IDs/directories are disjoint.
- h01, h02, h05, h06, and h07 are materially faithful to the authored holdout prose.
- The four pilots are retained as historical pilots rather than represented as frozen evidence.
- The pin-classification map is a useful addition even though it is incomplete and not machinery-driving.

## 5. What a reader may conclude if this freezes as-is

If a later registered run passes, a reader may conclude only that the study’s code reproduces registered outputs on its selected constructions; that the commitment’s derived fields agree with the retained judgment for the digest-bound canonical call; that retained requirement-keyed bytes hash to declared digests; and that two pinned upstream policy functions were invoked offline over study-selected records.

A reader may not conclude that:

- all executed actions were uniquely authorized;
- an effect belongs to the authorized call;
- the retained histories are producible by the pinned Portal;
- a historical drain was lawful;
- evidence was captured from, or has lineage to, the named source;
- every retained record was typechecked;
- every pin was enforced;
- holdout failures cannot affect R1;
- the 27 cells cover every stated boundary “must not”;
- or the results generalize beyond the registered constructions and capability envelopes.

CODEX-015-R3-DONE
tokens used
340,165
