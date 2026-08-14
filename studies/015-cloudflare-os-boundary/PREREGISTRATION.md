# Preregistration — Study 015: the judgment/staged-action boundary under a governed-agent platform

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing thereafter.**
Ten review rounds have run and all ten returned DO-NOT-FREEZE; round 5's structural rescope —
the claims narrowed to what the apparatus is, plus the source-of-truth sweep it asked for — is
applied, round 6's five blockers and two majors are fixed, round 7's three blockers, two majors
and four named residues are fixed, round 8's three blockers, one minor and three named
residues are fixed with its ruling adopted, round 9's two blockers are fixed, and round 10's
one blocker is fixed with both of its rulings adopted
([`DEVIATIONS.md`](DEVIATIONS.md), "Round-5 rescope", "Round-6 fixes", "Round-7 fixes",
"Round-8 fixes", "Round-9 fixes" and "Round-10 fix"). **Round 11 has not run**, and the freeze
waits on its confirmation.

**Nothing has run under a freeze.** Everything executed during harness development lands under
`pilots/`, is labeled harness validation, and supports no claim. After the freeze this file is
never edited; corrections go to [`DEVIATIONS.md`](DEVIATIONS.md).

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (retained-record model and provenance table, commitment
schema, binding points, disposition→action map, and the verification ceremony with its exact
verdict codes and ordering), [`harness/MATRIX.json`](harness/MATRIX.json) (the machine-readable
locked-replication cell registry) and [`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json)
(the reviewer-authored holdout stratum). Where prose here and those artifacts could diverge, the
pinned artifacts govern and the divergence is a deviation.

## 1. Question

Cloudflare OS ships an open, inspectable governed-agent platform whose Gatekeeper contract stages
external side effects into an approval queue: capability introduction, observation-aware sharing,
human and automatic approval, deferred effects, and an unsigned per-workspace action log. Its
action policy today is a connector-author Boolean plus a per-Gatekeeper user opt-in, and its own
source anticipates richer action descriptions and a future policy engine. A JPS disposition is
none of those things: it is a portable, deterministic judgment with explicit unknown, conflict,
and escalation. When a bridge carries the one into the other, the published boundary analysis for
this class of platform names five collapses a bridge must not perform and several bindings it
must add. This study makes those requirements executable and attempts to falsify them.

**R1 (primary, retractable, a locked regression endpoint):** for every adjudicated **endpoint**
cell in the registered locked-replication matrix, the observed per-layer detection outcome
(upstream-policy replay / adapter binding / pinned-evaluator replay, plus the derived combined
verdict) equals the per-cell registered expectation. R1's standing is exactly that of a locked
regression suite over behaviour the maintainer has already observed: it can be falsified by a
regression, and it is **not** a prospective prediction and must never be reported as one. The
prospective content of this study is the holdout stratum (§1a), which is reported separately and
with equal prominence.

**R2 (secondary, descriptive):** the detection-ownership map — which failures the platform's own
replayed policy functions catch, which only the adapter's binding catches, which only
pinned-evaluator replay catches, and which nothing catches. R2 is a restatement of the matrix by
category, not an independent endpoint. Its central content is registered in advance by the
per-cell `upstreamChecksReplayed` field and the `not-engaged` outcome: for most semantic cells
the platform's policy functions have nothing to decide, because no field of theirs carries a
disposition. The study measures that rather than assuming it.

The study attempts to falsify the bridge, not to demonstrate compatibility. A cell caught by no
layer that was registered as detectable falsifies R1 and is reported with the same prominence as
a pass.

## 1a. Two strata

- **Locked replication** (`harness/MATRIX.json`, 27 cells, `matrixVersion` 3). Expectations were
  corrected freely against pilot observations *before* the freeze; the registered run is a
  conformance replication, falsifiable by regression, never readable as a prediction. Every
  pilot is retained under `pilots/` and every correction is named in `DEVIATIONS.md`.
- **Reviewer holdout** (`harness/MATRIX-HOLDOUT.json`, 8 cells). Authored by the pre-freeze
  cross-vendor reviewer from static inspection, committed verbatim with attribution (the
  authored file is preserved byte-for-byte at `reviews/round-1/MATRIX-HOLDOUT.authored.json`),
  and **never adjudicated before the freeze**: `harness/score.py --include-holdout` refuses
  mechanically while `harness/PINS.json`'s `preregistration.sha256` is null, and a harness test
  asserts the refusal. The fixtures are *constructed* before the freeze — the scorer's gate
  requires them to exist — but construction computes no verdict. Holdout results are scored into
  a separate object with its own verdict and its own validity records: **holdout cell outcomes do
  not enter R1's arithmetic**, which is the exact guarantee and is asserted structurally by a
  harness test. It is *not* a claim that nothing in the holdout can affect R1's publication.
  Registry parsing, pin enforcement, the whole-study manifest and the publication step itself are
  attempt-scope preconditions shared by both strata, so a malformed holdout artifact can make the
  whole attempt inconclusive — including R1. Round 4 (R4-5) is right that treating those as
  attempt-scope is defensible only if the guarantee is stated at this width, and it is.

  The reviewer's instruction governs their interpretation: these expectations predict the
  **reviewed** apparatus, and are never revised to follow a fix. Several of them predict blind
  spots that the post-round-1 repairs are intended to close, so divergence there is the intended
  primary result. The only change made to the authored file was a mechanical schema migration
  (layer key `cf`→`upstream`, field `platformChecksEngaged`→`upstreamChecksReplayed`, and for
  cells registering no replayed checks the authored `pass`→`not-engaged`, since the reviewed
  apparatus reported non-engagement as pass); the migration is recorded in the file itself and a
  test asserts that nothing else changed.

The fixture builder and the binding verifier share one commitment/digest implementation
(`adapter/commitment.py`), so the locked stratum has no independent mutation oracle — the same
standing limitation Study 014 recorded, inherited knowingly.

## 2. Apparatus and pins

- **Cloudflare OS** at commit `b2a51b5426398c8353d9d4dd984bd525121ab5f2` (Apache-2.0; no tagged
  release exists — the pin is the only available behavioral baseline), cloned read-only and
  located via `CFOS_SOURCE`, **source unmodified**. Dependencies come from upstream's own
  `pnpm-lock.yaml` (digest pinned) via `pnpm install --frozen-lockfile --ignore-scripts`.
  The pinned code the study executes: `classifyTool` and its helpers
  (`packages/mcp-shared/src/tools.ts`), `AutoApprovalDrainer`
  (`packages/workshop-backend/src/auto-approval.ts`), upstream's own mock Durable Object storage
  (`packages/workshop-backend/__tests__/mock-storage.ts`) and `createTypedStorage`
  (`packages/typed-storage/src/index.ts`). The pinned types the retained **ledger records and
  auto-approval rules** are held to — that is the whole typechecked surface; staged calls, drain
  witnesses, catalogs and effect attestations are instrumentation with no upstream type to be
  held to — are the **server-side** `ActionRecord` and `AutoApproveTagRecord`
  (`packages/workshop-backend/src/overseer.ts`), checked by the clone's own TypeScript under the
  backend package's own tsconfig after its one committed codegen step
  (`harness/typecheck.py`). Per-file digests in `harness/PINS.json`; the probe runner
  self-reports the clone commit, tracked-tree cleanliness, node/esbuild/typescript identity and
  every probed file's digest per attempt, and the scorer enforces the report against the pins.
- **The one injected seam:** `cloudflare:workers` is aliased to a study stub whose only used
  runtime export is an inert `tracing` object, because `auto-approval.ts` constructs a logger on
  the observability path. Nothing on any adjudicated code path reads the stub's behavior.
- **The probe toolchain:** every probe entrypoint is bundled by the pinned clone's own esbuild
  and run under the pinned node; the fixture typecheck uses the clone's own typescript. All
  three identities are pinned and enforced. Upstream's vitest path is unusable on this apparatus
  (its native rollup binary needs a newer glibc than the host provides) — recorded, and
  immaterial: the bundled modules are the same pinned sources either way.
- **jpack** v0.16.0 release binary, archive `sha256 1a12503c…ed59`, binary `sha256 7c11ebef…9325`
  — the same pins Studies 013 and 014 froze, including 013's reproducible-build corroboration.
  Located via `JPACK_BIN`, digest-checked before every use.
- **Baseline pack**: `data-request-intake-triage` — the specification's own conformance-corpus
  pack, vendored byte-for-byte and anchored to its own registered digest, not merely to the study
  manifest. Every fixture's facts and evidence-availability documents are verbatim cases from the
  same corpus's seed manifest (also digest-anchored), so every disposition the study binds is one
  the specification registers, not one the study authored.
- Interpreter, node, venv, and every other pin: `harness/PINS.json`. Every member carries an
  explicit `enforcement` class, and the class is the claim: **SCORER** members are compared
  against the live artefact by `harness/score.py` before anything is adjudicated and a mismatch
  is terminal pipeline-invalidity; **CI** members are enforced by the workflow's install steps;
  **DESCRIPTIVE** members are recorded provenance the scorer does not check. Round 2 found the
  earlier blanket "every pin is enforced" false, and §8 lists the classes member by member.
- `harness/STUDY-MANIFEST.sha256` is the exact-set whole-study manifest, verified before any cell
  is adjudicated.

## 3. Scenario (deterministic, no models, no network)

The registered deployment is the pinned **MCP Portal** connector
(`packages/gatekeeper-mcp-portal/`) with `MCP_PORTAL_TRUST_ANNOTATIONS=true`. Round 2 established
that no other choice is available: the generic MCP connector hardwires `trust = "byo"` with no
deployment knob, and `classifyTool` requires `vetted`, so a vetted, auto-approvable write exists
**only** on the portal. A workspace binds it to a tracker endpoint
(`https://tracker.example/mcp#server=tracker`) carrying tool `tracker_create_work_item`
(annotations: not read-only, not destructive, idempotent). The bridge under test evaluates the
triage pack over a conformance-case fact set; disposition `proceed` authorizes exactly one staged
`tracker_create_work_item` call on that exact Gatekeeper, whose arguments derive
deterministically from the retained facts (`adapter/SPEC.md` §4); every other disposition
authorizes inaction. Every identifier in every fixture — resource URL, wire tool name, the
double-encoded action-kind tag, and each action record's field set including its
`describeCall`-generated prose, `awaitDecision: true` and explicit `autoApprovable` boolean — is
**synthetically reconstructed from registered inputs at the shape that connector's source
defines**, with the prose and the action-kind tag generated by the pinned functions themselves
over inputs this study registers. Nothing was captured from a running deployment, and no claim is
made that the pinned platform's own execution paths would have produced a given retained history
(§9). An earlier draft used a bare endpoint, an invented scope tag and short hand-written prose;
none of it was
producible, and `DEVIATIONS.md` records the correction. The staged call binds the
commitment at staging time and the published report binds it at report time. Auto-approval
follows the platform's own two-signal rule: the author verdict on the action plus a user-enabled
rule for the action kind. All clocks in fixtures are fixed constants; fixture construction is a
one-time act and the frozen bytes, not the builder, are what the study scores.

**What is modeled, stated plainly.** `adapter/SPEC.md` §0a is the registered, field-by-field
provenance table: for each datum the ceremony reads, whether stock Cloudflare OS retains it in
the outer workspace log, in the concrete connector's private store, or not at all. The workspace
queue lifecycle and gatekeeper-side store are harness-modeled records — the platform's Durable
Object never runs — and most of what the B and D families depend on (canonical arguments,
resource revisions, the commitment carrier, effect attestations, the drain witness) is
instrumentation a *retaining* deployment could keep, not something the platform ships. Per cell,
`modeledDependencies` names exactly which. `ledger.json` uses the platform's own server-side
record shape and is held to it mechanically.

An earlier draft of this section said the tool name and arguments "never appear in the log".
That was wrong and is corrected: for the MCP path both reach the outer log as sanitized,
truncated prose inside `description`, and the tool name additionally appears structurally inside
`description.actionKind.tag`. What is absent is anything structured, canonical, or digestible —
which is the claim the study actually needs.

The platform behaviors the study executes are the two its contract makes executable outside the
Durable Object: MCP tool classification and the auto-approval drain, both run as pinned upstream
code. The submit-time eligibility predicate and the apply chokepoint are welded to the Durable
Object (`overseer.ts:2868-2911`, `2481-2509`) and are **not** exercised; the drain carries an
independent copy of the same two-signal eligibility rule and upstream's own unit suite exercises
the drainer exactly this way. Runtime behavior of the platform is out of scope entirely —
detection here is post-hoc provability from retained artifacts.

## 4. Cells

27 cells in `harness/MATRIX.json`: 1 positive control, 5 negative controls, 19 endpoint mutation
cells across **five** endpoint categories (A judgment-artifact ×4, S semantic-collapse ×6,
O observation-evidence ×1, B binding-integrity ×7, D deferred-execution ×1), 1 demonstration
(`m01-readonly-bypass`) and 1 descriptive boundary (`m02-ambiguous-commit`). The six control-gate
rows are validity gates on the apparatus and count toward nothing. The sixth category,
M annotation-trust, contributes **no endpoint** — its two cells are exactly the demonstration and
the descriptive boundary, which is the point of registering them as such.

The S family is the published boundary analysis's five forbidden mappings, one cell each
(`s01` unresolved→rejected, `s02` unknown staged and auto-applied, `s03` operational failure
retconned as epistemic unknown, `s04` approval-as-evidence, plus `o01` observation-as-evidence),
with `s05` (handoff dropped) and `s06` (not-applicable executed) completing the disposition
space. The A family covers artifact drift, coherent disposition and executable forgery, and
carried-but-unchecked judgment identity. The B family exercises the decision-to-staged-action
binding profile violation by violation: reuse, argument drift, stage-time and apply-time revision
mismatch, gatekeeper substitution, action-kind substitution, unbound execution. `d02` carries the
callback-versus-commit distinction.

### 4a. Registered per-cell fields

Beyond its expectation, every locked cell registers `role`, `variant`, `attackerCapability`,
`mutationConstraint` (exactly what the constructor was permitted to touch — §4b),
`registeredAbsences` (artifact names whose absence the registry authorizes; the vocabulary
exists so absence-validity can never be inferred from an expected verdict),
`upstreamChecksReplayed` (which pinned policy functions the construction actually reaches — the
registered visibility of every `not-engaged` outcome), and `modeledDependencies` (every datum the
cell leans on that stock Cloudflare OS does not retain).

### 4b. Threat model — and why capability alone is not the registered fact

The capability vocabulary is `none`, `bridge` (the bridge itself stages, applies, claims or maps
something the committed disposition does not authorize — most semantic cells, because the
analysis's collapses are bridge behaviours rather than attacks), `store` (the retained store is
edited afterwards, sloppily or coherently), `environment` (the world moves), and `out-of-band`
(an effect reaches the resource with no queue record).

Round 1 found that a capability label alone overstates several cells: `b02`, `b04` and `b05`
depend on a store writer changing one downstream field *while declining* to coherently rebuild
the related records, and a fully capable store writer could evade them exactly as the ceiling
below admits. Every cell therefore registers a `mutationConstraint` stating precisely what its
construction was permitted to touch, and no cell's detection may be read as holding against a
more capable adversary than it actually faced.

**The registered ceiling.** Every retained record in this study is unsigned, because the platform
provides no signing surface for action records and no carrier for a signed commitment. A party
that can rewrite the *entire* retained store coherently — envelope, commitment, ledger, platform
store, artifacts and report together, around a disposition the retained inputs genuinely produce
— presents a consistent history this ceremony accepts. What the layers catch is internal
inconsistency (binding), an action that is not the one the map derives from the judgment
(binding's derivation oracle, which a coherent rebuild does *not* escape), input/output forgery
that replay can recompute away (replay), and claims the platform's own policy code refuses
(upstream). Catching a fully coherent rewrite requires an anchor outside the store — a
transparency log, a signed carrier, a reviewed-set lock analogue — which the platform does not
offer at the pin and which is out of scope here.

### 4c. Analytic limitations (not empirical rows)

**Decision currency** — "a newer pack version has since been activated" — is not store-internal,
admits no fixture distinct from the baseline, and is recorded as an analytic limitation, not a
row (Study 014 §4c's finding, unchanged by anything this platform ships).

**Dependent simulated writes** are not constructible in the registered scenario. The generic
Gatekeeper contract suggests simulation but does not require it, and the pinned MCP connectors
take the contract's own opt-out: they simulate nothing (`mcp-shared/src/session.ts:131-133`). So
the hazard the boundary analysis names — B staged against A's fiction, A then rejected — cannot
arise for this deployment. Five other pinned connectors do implement simulation, so the hazard is
real for the platform and simply absent here.

Because a simulation basis could only ever be empty for this connector, the field is **not in the
commitment schema at all** and there is no verdict code for it: a field with one reachable value
carries no information, and a code that cannot fire is the unreachable prose §6 forbids. An
earlier draft kept both "as defence in depth"; round 2 was right that this was
source-inconsistent, and both are gone (`DEVIATIONS.md`).

A related correction: `awaitDecision: true`, which the connector sets on every write, does **not**
suspend the agent's turn unconditionally — it suspends only when the action is not auto-eligible
at submit time (`overseer.ts:2905`), and the registered baseline (vetted, rule enabled,
`autoApprovable: true`) is precisely the case that does not suspend. An earlier draft said
otherwise. What forecloses the hazard is the absence of simulation, not suspension.

**A fully consistent re-decision** — an insider re-runs the whole decision over different facts
and rebuilds coherently — is the same ceiling as §4b and is likewise out of scope.

## 5. Endpoints and decision rule

Per cell the scorer records three independent layer outcomes and the derived combined verdict
(pass iff no layer objects; `not-engaged` is not an objection), then compares the 4-tuple against
the registered expectation. Adjudication is on the registered **code** alone: each layer returns
`{verdict, code, detail}` and the detail string never enters a comparison. Divergence in either
direction is a divergence. Where a construction carries more than one binding defect, every
further failing code is published as `suppressed` beside the adjudicated one.

Ordered, exhaustive, over the **locked** stratum, per registered attempt:

1. Any locked cell **pipeline-invalid** (§6), or any freeze-integrity mismatch (§2) →
   `R1 inconclusive — pipeline-invalid`; terminal for that attempt; no rerun replaces it.
2. Else, any **control-gate** row diverging → `R1 inconclusive — control gate failed`.
3. Else, zero divergences across the **endpoint** cells → `R1 holds`.
4. Else → `R1 falsified`, with every divergence listed.

`demonstration` (`m01`) and `descriptive` (`m02`) rows are adjudicated and published but count
toward nothing. The holdout stratum is scored separately into its own object with its own
verdict (`holdout concordant` / `holdout divergent` / `holdout inconclusive`) and is reported
with equal prominence in the published matrix.

The scorer (`harness/score.py`) is the only thing that publishes; its argument surface is the
attempt root plus `--include-holdout`. Adjudication is deterministic recomputation from frozen
bytes; no output embeds a timestamp or an absolute path, every published file is written
atomically, and running the scorer twice on the same frozen tree must be byte-identical.

## 6. Validity channel (separate from detection)

**Pipeline-invalid** (excluded from adjudication, counted separately, never a detection): a cell
whose fixture fails its own manifest check; an artifact absent when the cell's
`registeredAbsences` did not authorize it, or present when it did; a layer outcome outside the
registered vocabulary; a replayed-check set that differs from the registered
`upstreamChecksReplayed`; a crash of the harness itself as opposed to an outcome from a layer; a
fixture record that fails the pinned-types typecheck; any freeze-integrity or pin mismatch under
§2, including the upstream runner's clone-integrity and toolchain self-report.

Three properties, all mechanical:

- **Validity and detection are independent.** Permitted absences are read from the cell's own
  `registeredAbsences` field and from nothing else.
- **Nothing fails silently, with two stated exceptions.** `ATTEMPT.json` is written before
  anything else runs — including before the pin registry is parsed — and every failure path that
  reaches adjudication persists a terminal pipeline-invalid `RESULTS.json`. The two paths that
  deliberately do not are usage refusals rather than attempts: an attempt root that already
  exists (the scorer exits before creating anything, so no record is overwritten), and a
  pre-freeze `--include-holdout` (the marker is written, nothing is published). Round 2 found the
  earlier unqualified promise was false; this is the corrected statement.
- **The registered typecheck is a scorer precondition**, not merely a test: a published score
  cannot call itself valid without it.

The exhaustive verdict-code vocabulary lives in `adapter/SPEC.md` §5. Harness tests diff the SPEC
against the codes the implementation declares and the scorer classifies, assert that the SPEC's
numbered binding order **is** the implemented order, and construct a minimal condition for every
registered code asserting the exact code. Two locked negative controls (`neg-binding-control`,
`neg-replay-control`) additionally exercise the binding and replay layers through the official
scorer on every attempt, so layer liveness does not rest on direct layer calls alone.

The pre-freeze holdout refusal guards the official publication route. It is not a claim that no
one could invoke a layer function directly; it is a claim about what this study publishes.

## 7. Controls and counting integrity

- Positive control: the untouched baseline must pass all three layers.
- `neg-mcp-byo-autoapply` and `neg-mcp-nonidempotent-autoapply` must fail the upstream layer
  through the pinned classifier's own trust-tier and annotation branches; `neg-drain-skip` must
  fail it through the pinned drainer replayed against a stage-time witness. Together they prove
  the upstream layer's two functions are alive on exactly the branches `s02` needs to pass
  through, so `s02`'s registered upstream-pass cannot be an artifact of a dead layer.
- `neg-binding-control` and `neg-replay-control` prove the binding and replay layers are alive
  and refusing, through the scorer.
- `m01` is a disclosed designed demonstration of the platform's own documented annotation-trust
  tradeoff; `m02` is a registered boundary whose all-pass row means "no offline layer can prove
  commit", not "nothing is wrong".
- Layer attribution is a design property of the families and is asserted mechanically: no
  endpoint cell registers a multi-layer detection.
- No silent exclusions: every registered cell appears in the output with an outcome or
  NOT-ADJUDICATED. The scorer refuses an attempt directory that already exists.

## 8. What is enforced, what is recorded, what is not prevented

Enforced by machinery: fixture manifests; the whole-study exact-set manifest; every pin the pin
registry's own `enforcement` map classes as SCORER (protocol digests when filled, the `jpack`
binary digest, the vendored pack and conformance-case digests, interpreter version, `pip freeze`
digest, node/esbuild/typescript identity, clone commit and cleanliness, probed-file digests) —
members classed CI or DESCRIPTIVE are not scorer-checked and the registry says which are which,
because round 2 found the earlier blanket "every non-null pin" claim was false; the frozen cell-id set and per-cell schema for both
strata; the holdout's non-emptiness, attribution, id-disjointness and fixture existence; the
SPEC/code vocabulary sync, per-code reachability, and SPEC/implementation order equality; the
pre-freeze holdout refusal; the fixture typecheck against the pinned server-side types; upstream
bytes never vendored (clone-only); missing `CFOS_SOURCE` or `JPACK_BIN` failing the determinism
tests rather than skipping them; atomic publication.

Recorded, not enforced: the `cloudflare:workers` stub seam (observability path only); the harness
node version differing from upstream CI's own pin; the modeled status of `platform.json` and of
effect attestations (SPEC §0a, per-cell `modeledDependencies`); that the builder and verifier
share one commitment implementation, so the locked stratum has no independent mutation oracle.

Not prevented: a fully coherent rewrite of the unsigned retained store (§4b's ceiling); any
attack on the platform's actual runtime, which never runs here.

## 9. What this study cannot show

No policy truth and no fact truth — binding and internal consistency, not truth;
`evidenceBacking` digests assert **retained-preimage consistency** and nothing more (the store
holds bytes under the requirement id that hash to the committed digest), never that those bytes
were captured from the named source, never lineage, and never that an artifact is authentic,
sufficient, or true —
nothing here inspects one, and a bridge that stores approval bytes under the requirement id and
calls them an artifact passes (SPEC §1, `evidenceBacking`). No authorization from judgment: an
`approve`-family outcome is not a capability, a Gatekeeper grant, or a release of a staged
effect, and the map's "authorizes" is the adapter's own contract, not the platform's. No claim
about Cloudflare OS runtime behavior — the Durable Object, the submit gate, the apply chokepoint,
sharing, observers and the agent loop never execute; findings about them are findings about the
pinned *contract and source*, exercised where executable and typechecked where not. No claim
that the platform performs no validation: it validates its live RPC boundary, and the study's
claim is narrower and stated exactly (SPEC §0). No security audit of Cloudflare OS and no
endorsement; the platform's own TODOs are load-bearing context, not findings. No claim that the
platform *should* adopt this binding profile, and no claim about Cloudflare's managed products,
which are outside the pinned open-source baseline. No JPS conformance claim. No
prospective-prediction claim for the locked stratum (§1a). No coverage claim beyond the
registered cells; no general interoperability claim beyond: this platform contract at this
commit, this pack, this action encoding, this machine, one adapter written by the JPS side. No
"zero trust": the verifier trusts the pinned clone, the pinned jpack binary, the adapter code,
and the retained store as retained — enumerated, finite, and honest. And no claim that a
detection here would have *prevented* anything at runtime: detection is post-hoc provability, the
platform applies effects on its own authority, and nothing in this study sits on that path.

Four more, added at round 5 and load-bearing (they are the difference between what this apparatus
does and what a reader might wish it did). **No source-reachability claim for retained
histories:** the lifecycle rows, staged calls, ledger records, and connector outcomes the cells
adjudicate are selected, mostly synthetic constructions of the retained store's shape —
internally consistent where the cell requires it — and nothing here shows that a given retained
history could have been produced by the pinned platform's own execution paths. **No effect
causation:** an attested effect matching a bound call's identity is *matched*, never shown to
have been caused by that call; effect attestations are modeled records (SPEC §0a) and carry no
causal proof. **No closed inventory:** the binding checks close the inventories they define over
the records the store retains; they do not show the store retained everything the platform would
have written. **No real private connector record:** where a cell speaks of a connector outcome it
speaks of the retained flattened `connectorOutcome` scalar, never a recovered private row —
retryability, error detail, and every private field beyond the scalar are absent by construction
and asserted nowhere.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence, every
registered-boundary confirmation, both strata, and any cell caught by neither system — the last
with the same prominence as a pass, because a precise map of what the composition cannot bind is
the study's most useful possible output.

## Decision register

Round 1 (`reviews/round-1/`, verdict DO-NOT-FREEZE, 7 blockers and 6 majors) is dispositioned in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md). The questions it answered:

- [D-1] **Answered by change.** The layer is renamed `upstream` and described as the platform's
  policy *functions replayed offline by this harness*; non-engagement is now its own outcome
  (`not-engaged`) rather than a pass, and every claim of platform endorsement is withdrawn.
- [D-2] **Answered.** The map still executes only `proceed`, but it now names its target
  explicitly so the verifier can re-derive the authorized action; the map is stated to be
  adapter-owned policy, and the reviewer's clarify-with-bound-execution case lives in the
  holdout.
- [D-3] **Answered by change.** `evidenceBacking` stays inside the judgment, but the evidence
  artifacts are now retained and every backing digest must have a retained preimage — a
  digest-shaped reference no longer satisfies it. What that buys is retained-preimage
  consistency, never proof that the retained bytes were captured from the named source (§9).
- [D-4] **Answered by change.** Two locked negative controls now exercise the binding and replay
  layers through the official scorer, alongside the per-code reachability suite.
- [D-5] **Answered by change.** `m02`'s fixture was refused at round 1 as source-impossible and is
  rebuilt to a store whose retained tuple the compatibility matrix registered in SPEC §5 admits:
  the outer workspace record stays `pending` beside a flattened `connectorOutcome` scalar of
  `outcome-unknown`, a pair that matrix gives exactly one supportable report state,
  `applied-unproven`. The
  private connector row and every field of it beyond that scalar are not retained and are asserted
  nowhere (§9). The inverse overclaim is the reviewer's own holdout cell. *(Corrected twice. At the
  round-7 fixes (R6-1 residue) this row still called the rebuilt cell the trace the pinned source
  itself keeps; at the round-8 fixes (R8-1) the replacement still called it a trace that source's
  own paths admit. Both are source-reachability claims about a modeled store, and §9 registers
  source-reachability as **not** established. What the row says now is what the apparatus checks:
  a locally registered tuple, and nothing about how the bytes came to be there.)*

Open for the next round:

- [D-6] The derivation oracle makes the map the verifier's own; a deployment whose map differs
  would need a different oracle. Is the map's status as adapter-owned policy stated clearly
  enough that no reader takes it for a JPS or platform property?
- [D-7] **Answered, narrowed.** The witness is self-asserted instrumentation supplied by the same
  store under examination, so `drain-order-violation` is a claim about **consistency with that
  witness**, never about historical lawfulness — a store writer who adds a rule to the witness
  launders an auto-approval, and the study says so in SPEC §5 and in the probe itself. What the
  check still buys is that the *queue* is reconstructed from the ledger's own immutable
  timestamps, so an obstruction cannot be erased by resolving it later.
- [D-8] **Answered by removal.** `simulationBasis` and its verdict code are gone; the hazard is
  recorded analytically in §4c.
