# Deviations and corrections — Study 015

Live from the first draft. Before the freeze this file records protocol-relevant changes of
course; after the freeze it is the only place corrections may land — the preregistration is never
edited again.

## Withdrawn findings

- **The backend-typecheck finding is WITHDRAWN (round 1, finding 8).** An earlier draft recorded,
  in four places, that holding fixtures to the server-side `ActionRecord` was "not reproducible
  from the committed tree" because the backend typechecks only against a wrangler-regenerated
  `worker-configuration.d.ts`, and used that as the stated justification for holding records to
  the published contract layer instead. The claim is false. `worker-configuration.d.ts` is
  tracked at the pin (`git ls-files packages/workshop-backend/worker-configuration.d.ts`), and

      cd packages/workshop-backend && node scripts/build-format-blueprints.mjs
      node ../../node_modules/.pnpm/typescript@5.9.3/node_modules/typescript/bin/tsc \
        -p tsconfig.json --noEmit

  exits 0 with zero diagnostics and leaves the tracked tree clean (the generated file is
  git-ignored). The earlier attempt failed for an apparatus reason of the study's own making: the
  codegen step had not been run, and a hand-written transient tsconfig had mis-anchored the
  ambient types. `harness/typecheck.py` now binds the real server-side types with no field
  stripped, running the codegen step first. The lesson is the one already on the books from
  Study 008: a premise about the environment was written into the record without being verified
  against source, and a reviewer caught it.

## Round-2 corrections (pre-freeze)

- **The registered scenario was not source-reachable, and is re-rendered.** The earlier scenario
  (bare endpoint `https://tracker.example/mcp`, trust `vetted`, tool `create_work_item`, tag
  `jps-tracker:create_work_item`, short hand-written prose, no `awaitDecision`) is emitted by no
  pinned connector. The generic MCP connector hardwires `const TRUST: ServerTrust = "byo"`
  (`gatekeeper-mcp/src/mcp.ts:77`) with no deployment knob, so an auto-approvable write exists
  only on the **MCP Portal** with `MCP_PORTAL_TRUST_ANNOTATIONS=true`. The study now registers
  that connector and re-renders every identifier at its real shapes: resource
  `https://tracker.example/mcp#server=tracker`, wire tool `tracker_create_work_item`, action-kind
  tag `mcp-portal%3A…%3Aportal-tracker:tracker_create_work_item` (double-encoded, because the
  portal's scope tag is itself encoded and `actionKindFor` encodes it again), and action records
  whose title and description come from the pinned `describeCall`, with `awaitDecision: true` and
  an explicit `autoApprovable` boolean as `session.ts:126-135` submits.
- **`simulationBasis` and `simulation-basis-invalid` are removed entirely.** Round 1 kept them "as
  defence in depth"; round 2 showed that was source-inconsistent, and once the basis became a
  derived field its only reachable value was empty, so the verdict code could no longer fire. A
  field with one reachable value and a code that cannot fire are exactly the unreachable prose the
  protocol forbids. The hazard is recorded analytically (PREREGISTRATION §4c).
- **One registered expectation was corrected against an observed run.** `neg-mcp-byo-autoapply`
  was registered `binding: pass` on the reasoning that a byo commitment binds a byo store
  consistently. Once `serverTrust` moved from contextual to derived — because the map, not the
  store, fixes the tier — that cell's binding layer correctly reports `target-mismatch`, and the
  registered expectation now says so. This is the **first** registry correction in the study
  driven by an observed run rather than by review or source verification; the change was predicted
  from the code change and then confirmed, and the cell is a control gate, not an endpoint.
- **`neg-drain-skip`'s obstruction was fabricated and is rebuilt.** It previously made a manual
  gate by omitting `autoApprovable` on a tool the connector would have marked auto-approvable.
  The obstruction is now a different, unannotated tool (`tracker_close_work_item`) that the pinned
  classifier genuinely refuses to auto-approve on any tier.
- **A probe the study claimed did not exist.** A scripted edit adding two source-fact probes
  silently failed to apply (its anchor had been renamed by an earlier edit), so
  `test_upstream_probes.py` documented coverage that `upstream-probes.ts` did not have, and a
  commit message asserted it. Round 2 caught it. The probes now exist and run; the lesson recorded
  is that a scripted edit must be verified against the file afterwards, not assumed.

## Pre-freeze self-audit (before round 3 reported)

An adversarial self-audit of the twice-rebuilt tree, run in parallel with round 3 and using the
same standard the reviewers use, found seventeen defects introduced or left by the churn. The
load-bearing ones, all fixed before round 3's report was read:

- **A functional hole in the round-2 repair.** Subject identity for the cardinality check was
  derived from the *authorized action*, which is `None` under every non-executable disposition —
  so the check silently disabled itself on the whole inaction half of the map, where the map
  authorizes zero calls and any subject call is the violation. Round 2's own attack shape
  survived there. Subject identity now comes from the retained facts alone, and a regression
  test constructs the attack.
- **A tautological probe, and six documents citing it.** The check named "the adapter's
  reproduction of the tag rule agrees with upstream" compared upstream's `actionKindFor` against
  an inline TypeScript restatement of upstream's own one-line body — it asserted `f(x) == f(x)`
  and never touched the adapter, while `commitment.py`, `SPEC.md`, `build_fixtures.py`, two
  tests and `PREREG-REVIEW.md` all cited it as the guarantee. The real comparison now lives in
  `test_study.py`, calls the pinned function through the runner over adversarial inputs
  (spaces, slashes, non-ASCII, already-encoded strings), and the six claims are corrected. This
  is the second time this study has claimed a check it did not have; the first is recorded above.
- **The SPEC's own §1 example was the withdrawn scenario** — bare endpoint, `create_work_item`,
  `jps-tracker:create_work_item` — in a document that says three sections later that exactly that
  triple is emitted by no connector. It was also schema-invalid under the study's own validator.
- **Three fixture-fidelity defects of the class round 2 blocked.** `m02` and holdout `h08`
  carried `autoApprovable: false` on a vetted, non-destructive, idempotent tool, which
  `classifyTool` makes `true`; `describeCall` was fed a server name and endpoint the portal
  cannot supply (its `serverName` is a `${server} / ${id}` scope label, and the endpoint it
  passes is the bare one, not the `#server=` resource URL); and `m01`'s observation prose was
  hand-written where the read path submits the connector's own.
- **An undeclared modeled dependency.** `observedCalls[].toolName` is the sole reason `m01`'s
  upstream layer engages at all, and stock Cloudflare OS does not retain it structurally. It now
  has a provenance row and a registry term, and `m01` declares it.
- Plus the endpoint-category count (M annotation-trust contributes no endpoint), the mapping
  numbering in the registry, and three dangling references to the removed simulation field.

## Registry changes before the freeze

- **`d01-dependent-simulated-write` is withdrawn** (round 1, finding 5). The construction — a
  dependent write staged against a simulated-but-unapproved premise — is not source-reachable in
  the registered MCP scenario: the pinned connector simulates nothing and sets
  `awaitDecision: true` on every write. The hazard is recorded as an analytic limitation
  (PREREGISTRATION §4c) rather than as a green or red cell. `simulationBasis` and
  `simulation-basis-invalid` remain registered as defence in depth and reachable by test.
  **Superseded at round 2:** both were removed entirely (see *Round-2 corrections* above),
  so this sentence records the round-1 decision only. Round 5 (R4-6) found the two
  statements read as a contradiction with nothing marking which is current; this note is
  the correction, and the current state is that neither the field nor the code exists.
- **`m02-ambiguous-commit` is rebuilt** (round 1, finding 6): its earlier fixture showed the
  outer workspace record `approved` with an `appliedAt` stamp, which the platform cannot produce
  for a throwing apply. The fixture now carries the trace the pinned source can actually retain.
  **Corrected at round 7 (R6-1 residue):** "the trace the pinned source can actually retain"
  claims of a modeled store the source-reachability PREREGISTRATION §9 registers as not
  established. The cell is a construction the source's paths admit; nothing shows the platform
  produced it.
- **Four cells added**: `neg-binding-control` and `neg-replay-control` (layer liveness through
  the official scorer), `a04-judgment-identity-forged` and `b07-stage-revision-mismatch` (two
  commitments that round 1 found were carried and never checked).
- The registry moves to `matrixVersion` 2 with an extended per-cell schema
  (`mutationConstraint`, `modeledDependencies`, `upstreamChecksReplayed`) and the layer key
  `cf`→`upstream` with `not-engaged` as a distinct outcome. It moves again to
  **`matrixVersion` 3** at the round-2 rebuild — no schema change; the bump marks the
  re-rendering of every identifier at the portal's real shapes — and 3 is what the
  registry in the tree carries.
- **The holdout was migrated mechanically, never revised.** The reviewer's authored file is
  preserved byte-for-byte at `reviews/round-1/MATRIX-HOLDOUT.authored.json`. The migration
  re-keys the layer and field names and, for cells registering no replayed checks, translates the
  authored `pass` to `not-engaged` (the reviewed apparatus reported non-engagement as pass). A
  harness test asserts nothing else differs.
- **The effect-attestation schema changed, and 23 cells regenerated** (round 5, findings 4 and 6;
  decisions D1/D3/E). Twenty-one `platform.json` files changed for the schema alone: the effect's
  `gatekeeperId`/`action` pair moved inside a `source` union, `staged-call` in twenty of them and
  `read-path` in `m01`, whose store names no staged call for it *(round 7, R6-1 residue: the
  earlier wording, "whose effect never came from a staged call", read the union arm as a fact
  about the world rather than as what the store says of itself)*. Two `ledger.json` files
  changed for prose: `b04` and `h04` now carry the second deployment's own `describeCall` output
  (title, description bytes and printed endpoint) and its denormalized resource title, instead of
  the first portal's prose beside the second portal's structural fields. Nothing else moved: no
  commitment, no report, no staged call, no expectation in either registry, and the reviewer's
  authored holdout file is byte-preserved. A before/after snapshot of all three layer outcomes
  over all 35 cells, computed by direct layer calls, showed zero drift.
- **`o01-observation-as-evidence`'s upstream expectation changed `not-engaged`→`pass`** with the
  round-5 rebuild: its rebuilt observation genuinely engages `classifyTool`, so the upstream
  layer now has something to replay. Construction-aligned, not an observed-run correction —
  recorded here because round 5 (finding 6) asked that the protocol-relevant registry change be
  named where registry changes are named. The holdout's h03/h04 expectations did not change.

## Round-5 rescope (pre-freeze)

Round 5's structural finding is accepted in the direction it named first: the claims narrow to
what the apparatus is, rather than the apparatus growing a trusted retention boundary or live
connector-row capture (the other convergence path it offered — declined here because the line's
posture is offline-first and the boundary map does not need it). Concretely:

- **PREREGISTRATION §9 gains four registered non-claims** — no source-reachability for retained
  histories (the cells adjudicate selected, mostly synthetic constructions), no effect causation
  (matched, never caused), no closed inventory (closed over what the store retains, not what the
  platform would have written), no real private connector record (the retained flattened
  `connectorOutcome` scalar, never a recovered private row).
- **README's green-ceremony paragraph carries the same ceiling**, and its "the shape that
  connector actually emits" became "a synthetic reconstruction from source, not a captured
  emission" — the round-5 wording finding, fixed at the surface readers actually read.
- Bridge-authored, unsigned modeled fields are constructions of the study; no cell treats them
  as proof of source history, and the wording that suggested otherwise is corrected by the
  source-of-truth sweep round 5 asked for (**G** under *Apparatus items closed*, applied in the
  same rescope rather than deferred to round 6).

### Apparatus items closed at the round-5 rescope

Each is a decision recorded before implementation; none changes a registered expectation.
Through C8 a rebuild of both strata reproduced every frozen fixture byte-for-byte. The D and E
items below change fixture bytes by construction — a schema change and a regenerated deployment
— and what changed, in which cells, is recorded under *Registry changes before the freeze*; a
before/after snapshot of all three layer outcomes over all 35 cells, taken by direct layer calls,
showed zero drift.

- **C1 — a record resolved before the witness instant is registered, not refused.** Exclusion
  from that pass's queue is legitimate history, and SPEC §5 (upstream step 2) now says so
  instead of leaving the acceptance implicit.
- **C4 — the queue boundary is registered as strict `resolved < at`.** Equality reads as
  not-yet-resolved at the witness and keeps the row in the queue, which is the reading the
  registered baseline relies on. Behaviour unchanged; no fixture churn.
- **C3 — timestamps are strict RFC 3339 on both sides.** A serialized `Date` always is one, so
  a parseable near-miss (bare date, space separator, unqualified local time, `:60` leap second)
  is refused rather than compared: `ledger-lifecycle-invalid` in the binding layer,
  `drain-order-violation` in the replay. **Narrowed at the round-6 fixes (R6-5):** strict RFC
  3339 is neither strict enough nor the same grammar twice — it admits offsets and any fraction
  width, one side finished with `Date.parse` and the other with `float`. The registered form is
  now the single serialized-`Date` form; see *Round-6 fixes* below.
- **C5 — an `approved` action row must carry an `autoApproved` boolean**, since the one approve
  chokepoint takes it as a required argument and persists it either way. The decision also
  called for the builder to attach the boolean to *every* approved row and for `o01`/`m01` to be
  regenerated; that part is **withdrawn as source-impossible**. The only approved rows lacking
  the flag are the two `type: "observation"` records, which upstream writes with none of the
  resolution fields (`overseer.ts:2688`, `:2859`) and whose server-side type has no such member
  at all — the pinned compiler rejects it (`error TS2353`). Attaching it would have manufactured
  exactly the class of unproducible fixture this study refuses, so the check is scoped to action
  rows and no fixture byte changed.
- **C6 — an `autoApproved` value of any kind outside `approved` is refused**, `false` as firmly
  as `true`: nothing but the approve chokepoint ever writes the flag.
- **C2 — attribution compares the whole author tuple.** Actor type, id and display name are the
  complete `AiChatAuthorInfo`; the drain replay compares all three against what the pinned
  drainer passed, and the binding layer holds every resolver to that shape.
- **C7 — the drain witness is validated at store load.** It was cast, never checked, so a
  malformed witness could reach the replay and slip past the attribution comparison. Its field
  set is now closed like the commitment's, and a witness that is not that shape is
  `retained-store-unreadable` — an apparatus verdict, never a detection.
- **B2/B3 — the governed inventory is fail-closed.** Two silent `continue`s are gone: a
  wrong-tool staged call sharing an approved row's join identity no longer erases that row from
  the inventory, and a row that cannot be classified at all (unretained gatekeeper, no resource
  anywhere, a denormalized resource its own gatekeeper contradicts) is refused under
  `binding-reuse` rather than discarded.
- **B4 — duplicate identities are refused on both sides.** Duplicate gatekeeper ids, ledger ids
  and staged-call join identities gave one store two readings (this side resolved the first
  duplicate, the node replay's `Map` the last). Upstream assigns both ids from monotonic
  counters, so neither reading may be preferred: `binding-reuse` here,
  `classification-refused` there.
- **B5 — the step-10 identity wording is corrected.** Inventory scope is the governed tool and
  resource; the *bound call's* arguments are compared by digest at step 12. The sentence that
  said scope included "exact arguments" contradicted both the implementation and round 4's own
  disposition.
- **C8 — the ambiguity trace is described as the flattened scalar it is.** SPEC's report
  vocabulary, the §0a provenance row and `m02`'s registry construction no longer narrate a
  private connector row: what is retained is the `connectorOutcome` scalar, and the private
  row, its retryability and its error detail are not.
- **D1 — `describe()` takes a registered DEPLOYMENT, not the first portal's constants.** A
  deployment is the scope label, bare endpoint, scoped resource URL, upstream server id and
  denormalized resource title a record inherits from the binding it was staged through; both
  portals are now registered as complete deployments and the description cache is keyed by
  deployment. `describeCall` prints the *calling* host's own server name and endpoint
  (`session.ts:110-117`), so prose generated for one deployment cannot appear on a record staged
  through another.
- **D3 — `b04` and `h04` are regenerated on the second deployment's own prose.** Their
  descriptions previously named the first portal beside the second portal's structural fields, a
  tuple no host can emit; the regenerated rows carry the second deployment's title, description
  bytes, endpoint and denormalized resource title. The holdout's authored expectations are
  untouched, and `reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved: holdout
  fixtures are builder products and this is a construction repair, not an adjudication.
- **E1/E2 — an effect attestation states its provenance as a closed union.** Round 4 gave each
  effect a staged-call identity to join on; round 5 found that identity fabricated on cells that
  stage nothing. The `source` member is now `staged-call` (with the claimed `gatekeeperId` and
  `action`), `read-path`, or `out-of-band`, validated for shape at store load —
  `retained-store-unreadable`, folded into the existing gate, no new verdict code. Only a
  `staged-call` source is joined to the bound call; at this decision the other arms were
  counted against the same cap and matched against nothing — **narrowed by G0 below**, which
  refuses them outright wherever the map authorizes an executable action. `m01`'s effect
  becomes `read-path`, which is what its
  construction always said it was, and `b06` still *claims* a staged call against a store holding
  none — that contradiction is the cell, and it fails on the count exactly as before. SPEC §0a
  and step 15 now state the union and that the join establishes agreement between two retained
  records, never causation (PREREGISTRATION §9).
- **D2/F3 — the whole description is compared, in both strata, unconditionally.** For every
  action row the retained title and description bytes are regenerated by the pinned
  `describeCall` from the deployment the row names, the tool the retained catalog holds and the
  arguments the retained staged call carries; the action-kind tag and label are compared against
  that deployment's own scope tag. The condition previously compared no prose, skipped the
  holdout, and checked the label only where the tag already matched the first deployment's — the
  mask that let `b04` through. The two cells whose construction deliberately disagrees (`b02`'s
  prose, `h04`'s forged tag) are asserted to DIFFER, quoting the registry, so the exceptions
  cannot decay into a skip. What this establishes is coherence between a row's prose and the
  deployment it names, not that the deployment is real.
- **F1 — the `BINDING_CHECKS` test is renamed to what it checks.** It holds three registry facts:
  the SPEC's numbered order is the implemented order, the SPEC names every code each check can
  return, and the reachability suite constructs a minimal condition for each. It claims no
  semantic equivalence between the prose and the implementation — the old name did, and round 5
  found the body comparing labels.
- **F2 — the SPEC's gate list is three, and the derivation moved under the guard.** The document
  said two gates while `_load_context` also returned `retained-store-unreadable`; it now names
  all three. The §4 derivation moved out of context load into the check that reads it, so every
  reading that can fail on its inputs happens inside the per-check guard. No outcome changed.
- **G0 — an effect that names no staged call is refused, not exempted.** E1/E2 left the union's
  `read-path` and `out-of-band` arms counted against the cap and matched against nothing. Inside
  the governed inventory that is too generous: where the map authorizes an executable action,
  every approved bound application is already spoken for by the cap, so an effect the store's own
  attestation sources elsewhere is unaccounted for. Step 15 refuses it on the existing
  `unbound-execution` code — no new verdict code, one branch in the existing path — and SPEC
  step 15 states it. Where the map authorizes nothing the zero-authorization clause refuses
  first, which is why this changes no registered outcome: `m01` and `b06` are both inaction
  cells. Confirmed rather than assumed — a before/after snapshot of all three layer outcomes and
  every suppressed code over all 35 cells, by direct layer calls, showed zero drift. Three
  regression tests: both non-staged arms under an authorization (asserting the diagnostic, so
  neither can pass by the arithmetic it exists to bypass), and the ordering that makes `m01` and
  `b06` unaffected.
- **G — one source-of-truth sweep, after the claims narrowed (round 5, finding 7).** The
  governing documents are brought to the apparatus in one pass rather than round by round:
  inventory scope is the governed tool and resource everywhere it is described; registered
  identifiers are "synthetically reconstructed at the shape the connector's source defines"
  rather than what it "actually emits"; `m02` and the connector-outcome vocabulary narrate the
  flattened scalar and never a private row; holdout isolation is stated as "holdout cell
  outcomes do not enter R1's arithmetic" with the shared attempt-scope gates named beside it;
  evidence backing is retained-preimage consistency with no capture implied, in the
  preregistration, `commitment.py` and the verifier's own diagnostics; and the pin and typecheck
  absolutes are replaced by the `enforcement` map's SCORER/CI/DESCRIPTIVE classes and by the
  typecheck's real surface (ledger records and auto-approval rules). `PREREG-REVIEW.md` — the one
  living ledger — carries current statuses for R4-2, R4-3, R4-5, R4-6 and round 5. Stated counts
  were recomputed against the tree; the drift found was the README's "six families" against the
  registry's five endpoint categories, and the registry's `matrixVersion` 3 recorded here as 2.
  No expectation, no fixture byte and no verdict code changed.
- **H — the appendable files are outside the freeze set by construction (ADR 0004).**
  `make_manifest.py` names `DEVIATIONS.md` and `README.md` in `EXCLUDED_DOCUMENTS` and filters on
  it, and a harness test asserts both files exist, neither is covered, and the constant names
  them. The exclusion was already implicit — the manifest lists registered documents explicitly
  and no glob reaches a top-level `.md` — so `STUDY-MANIFEST.sha256` is unchanged; what changes is
  that it is now deliberate and guarded. **Corrected at the round-6 fixes (R6-7):** "already
  implicit" was the defect, not a reassurance — with no candidate reaching a top-level `.md` the
  filter met neither name and deleting the constant produced the identical manifest, so the
  safeguard and its test were tautological. The candidate population now includes them; see
  *Round-6 fixes* below. This file is the one place a post-freeze correction may
  land, so covering it would make the first genuine deviation break the anchor it exists to
  protect. `PINS.json`'s `studyManifest` records the exclusion beside its `covers` list.

## Round-6 fixes (pre-freeze)

Round 6 accepted the round-5 rescope's direction and found two different failures on top of it:
the sweep had not reached every surface (R6-1, R6-7), and the claim the rescope put in its place
— that a green ceremony means the retained store is internally consistent — was false on
executable paths (R6-2 through R6-6). All seven findings are dispositioned in
`PREREG-REVIEW.md`; the protocol-relevant changes are recorded here.

**No registered expectation changed in either stratum, and no verdict code was added.** A
before/after snapshot of all three layer outcomes, every published `suppressed` code and every
upstream engagement list, over all 35 cells and by direct layer calls, showed **zero drift** —
which is the point, because R6-2, R6-3, R6-4, R6-5 and R6-6 all change adjudication paths.

- **R6-1 — the rescope's surfaces are brought to the rescope's decision.** Causal language is
  gone from the verifier's comment at the effect join, from the regression's name
  (`..._catches_substituted_causation` → `..._catches_a_claimed_source_that_is_not_the_bound_call`)
  and from `MATRIX.json`'s `m01` construction and note, which now say what that cell
  demonstrates: an offline replay of the pinned functions over a modeled retained store, in
  which `classifyTool` agrees the annotated tool is a read and the binding layer's governed-effect
  inventory is the only layer that objects to the retained attestation. Every retryability
  assertion about `m02` is gone — from its `report.json` note, the builder comment,
  PREREGISTRATION's D-5, and (as an annotation, since history rows are not rewritten)
  `PREREG-REVIEW.md`'s round-1 row 6. Five superseded rows in the living ledger gained explicit
  correction notes, which that file had promised and not delivered.
- **R6-2 — the retained outcome fields are one registered matrix, derived from source.** SPEC §5
  gains *Retained outcome compatibility*: which flattened `connectorOutcome` scalar can stand
  beside which outer lifecycle state, and which report state may claim it of the bound call, with
  the pinned-source citation for every row. `approved` admits only `committed`; `rejected` only
  `rejected`; `pending` admits `pending`, `failed` and `outcome-unknown`, and `committed` through
  the crash window between the connector's own save and the outer put — admitted deliberately,
  because refusing a producible history is not the repair. Enforced in the existing
  `ledger-lifecycle-invalid` (the store half, every action row of every cell) and
  `report-state-unsupported` (the claim half), with one regression per scalar and no new verdict
  code. Two now-unreachable branches were deleted rather than left as prose the matrix had
  already made dead. The reviewer's own reproduction — baseline plus `connectorOutcome: rejected`
  plus `execution: applied` — is one of the five regressions.
- **R6-3 — both layers settle what an identity is before either keys on one.** Every id and join
  component must be a non-Boolean integer in `[1, 2^53-1]`. The old asymmetry was real and
  produced two verdicts for one store: `repr(1.0) != repr(1)` here, `String(1.0) === String(1)`
  there. `storeAmbiguity()` also gains the ledger's own `(gatekeeperId, action)` identities, which
  the binding layer had checked since round 5 and the node side never had.
- **R6-4 — the drain check reads its witnesses before deciding it has nothing to do.**
  `not-engaged` now requires both an empty claim set and no retained witness, which makes the
  reverse accounting at the end of that function reachable for the first time. Lifecycle-only
  members (`appliedAt`, `resolvedBy`, `autoApproved`) are read by key presence, so an explicit
  `autoApproved: null` is refused as the member the chokepoint never writes there.
- **R6-5 — one serialized instant form, checked against every fixture first.** Every timestamp
  the ceremony's grammar reads, in all 35 cells, is already the canonical
  `YYYY-MM-DDTHH:mm:ss.sssZ`; the only non-conforming stamps in the tree are two JPS pack
  metadata fields inside `pack.json` (`sources[0].publishedAt`, `metadata.createdAt`), which the
  ceremony hashes and never parses. That form is therefore registered and enforced identically on
  both sides — same regex, same integer calendar check, and the validated **string** as the
  instant, since the form is fixed-width UTC and lexicographic order is chronological order. No
  `Date.parse`, no `float`, and nothing left that can raise: the `OverflowError` the reviewer
  reached came from a store-load path outside the per-check guard, and a regression now asserts
  that same construction returns an apparatus verdict. **This forced no fixture regeneration**,
  which was the reason for checking before choosing.
- **R6-6 — the governed inventory is the governed tool and resource, from the row's own record.**
  Membership now requires the row's `description.actionKind.label` to be the governed tool as well
  as its resource to be the governed resource. Target-tool rows still stay governed when a joined
  staged call contradicts them (round 5's B2/B3 repair, unchanged, and `b05` is unaffected in
  either direction); coherently different-tool rows are out of scope as different-resource rows
  are; a row with no label or with a label its own action-kind tag contradicts is refused rather
  than dropped. The reviewer's reproduction — a coherent `tracker_close_work_item` approval and
  matching call on the governed resource, falsely refused as `binding-reuse` — is a regression
  that now asserts a **pass**.
- **R6-7 — the appendable-file exclusion is real rather than implicit.** `make_manifest.py`'s
  candidate population now globs every top-level `*.md`, so `DEVIATIONS.md` and `README.md` are
  removed by the filter instead of never having been candidates, and a new protocol document is
  covered the moment it is written. The test disables the constant and asserts both files enter
  the manifest, and that they are the only difference it makes. `H` above recorded that the
  exclusion was "already implicit"; that was the defect, and this is its repair. The manifest's
  path set is unchanged at 60 entries.

### Fixture bytes changed at the round-6 fixes

Exactly one artifact, in one cell, plus the two manifests that cover it:

- `fixtures/mutations/m02-ambiguous-commit/report.json` — the report `note` loses the words "and
  not retryable" (R6-1). The private connector row's retryability is not retained by this cell and
  is registered as asserted nowhere (PREREGISTRATION §9), so the honest bridge's own note may not
  assert it either. Digest `1dac5dab…` → `5b1326ef…`.
- `fixtures/mutations/m02-ambiguous-commit/MANIFEST.sha256` — regenerated for that one line; the
  other eight artifact digests are unchanged.
- `harness/STUDY-MANIFEST.sha256` — regenerated. Its path set is unchanged; the digests that move
  are that cell manifest and the source and document files this block edits.

No other fixture byte in either stratum changed: no commitment, no ledger, no platform store, no
evaluation envelope, no other report, and `reviews/round-1/MATRIX-HOLDOUT.authored.json` is
byte-preserved. `MATRIX.json` changed in two prose fields of `m01` (`construction`, `note`) and in
no `expected` value; `MATRIX-HOLDOUT.json` is untouched.

## Round-7 fixes (pre-freeze)

Round 7 confirmed the rescope's direction a second time and found no new overclaim in the scope.
What it found is that **four of round 6's five executable repairs were asymmetric**: each was
derived on one side of a symmetry the pinned source has two of, and enforced only there. One of
two crash windows. The value a JSON number reads back as, rather than the token it was written
with. One regex dialect's defaults taken for the registered grammar. One direction of a
two-directional list comparison. A fifth finding compared an action-kind tag by suffix where the
connector emits a whole one, and a sixth found the round-6 causal sweep repaired at the sites it
named and nowhere else. All nine items are dispositioned in `PREREG-REVIEW.md`; the
protocol-relevant changes are recorded here.

**No registered expectation changed in either stratum, and no verdict code was added.** R7-1
grows one vocabulary — the report's `execution` field gains `rejected` — and nothing else: the
binding layer still runs nineteen ordered checks over 23 codes, and the SPEC's report table is
now read back by a sync test, as its compatibility matrix has been since round 6. A before/after
snapshot of all three layer outcomes, every published `suppressed` code and every upstream
engagement list, over all 35 cells and by direct layer calls, showed **zero drift** — which is
the point, because R7-1, R7-2, R7-3 and R7-5 all change adjudication paths.

**The survey R7-1 required, before it was enforced.** Admitting a history and adding a report
state can only ever turn a refusal into a pass, so both were surveyed across all 35 cells first,
with a STOP rule if either moved a registered cell. No cell holds a `pending` outer row joined to
a `rejected` connector outcome; no cell claims `execution: "rejected"`. The two `rejected` outer
rows in the tree (`neg-drain-skip` id 1, `h07` id 1) are obstruction calls, already admitted, and
are not the bound call the report table speaks of.

- **R7-1 — the reject side of the queue is as producible, and as reportable, as the apply side.**
  The lifecycle admits `pending`+`rejected` for exactly the reason round 6 admitted
  `pending`+`committed`: each connector path persists its own record before the outer row is
  written — `action-store.ts:196` saves `applied` before `apply` returns, `action-store.ts:209`
  writes `rejected` before `overseer.ts:7729-7732` updates the outer row — so a Durable Object
  that dies in either window leaves that pair retained. Round 6 derived the window on one path
  and transcribed it to the other as its mirror image, which it is not. And the *gap* round 6
  registered rather than papered over — a bound call the approver refused, describable by no
  report state — is withdrawn: leaving the most ordinary history this queue produces
  unrepresentable means a bridge reports it falsely or not at all, which is the failure mode
  every round of this review has killed somewhere else. `rejected` is a value of the report's
  `execution` field, requires the outer rejected row exactly as `applied` requires the outer
  approved one, and adds no verdict code.
- **R7-2 — one identity definition, written as a token.** Round 6 settled identity on the value
  each language reads back, which is two rules: `JSON.parse("1.0")` is `1` and
  `Number.isSafeInteger` accepts it, while `json.loads("1.0")` is a `float` and is refused. Its
  four regressions could not see this, because all four appended a *duplicate* id, which refuses
  on both sides for an unrelated reason. An identity is now what the store *wrote*: a plain
  digit-only integer lexeme — no sign, no `.`, no exponent, not a Boolean — that reads back
  inside `[1, 2^53-1]`. This side keeps each number's token through `json.loads`'s `parse_int`
  and `parse_float` hooks, applied to `ledger.json` and `platform.json` alone so no other
  retained artifact is parsed through a number type it never needed; the node side reads the same
  token from `JSON.parse`'s reviver `context.source` (Node 22) and replaces any non-integer token
  with a value that is not a number and cannot alias one in any key the checks build. A Node
  build without source access makes the runner refuse the cell as `unavailable` — an apparatus
  verdict — rather than substitute a weaker rule. Regressed with **lone** `1.0` and `1e0` on both
  sides through the runner; the node batch also gains the Boolean case R6-3's disposition claimed
  and did not carry.
- **R7-3 — the instant grammar is the same grammar, not the same regex text.** Python's `\d` is
  Unicode-aware and its `$` matches before a final newline; JavaScript's are neither. A stamp
  written in Arabic-Indic digits and a stamp with a trailing LF therefore passed the binding layer
  and were refused upstream — one store, two verdicts, and a manual-approval construction that
  came out binding-`pass` and upstream-`not-engaged`. The class is spelled `[0-9]` and the match
  is `fullmatch()`. Both stamps are regressed on both sides. **This forced no fixture
  regeneration:** every timestamp the grammar reads in all 35 cells is ASCII and unterminated,
  which round 6 had already established file by file.
- **R7-4 — the drain's reverse accounting compares lists, not keys.** It is now one comparison
  over every gatekeeper either side mentions, with absence read as the empty list. Round 6 wrote
  it as two loops whose second asked whether a witness's gatekeeper appeared among the ledger's
  claims at all, so a witness that applied nothing still inserted its key and was then refused for
  claiming an application it does not claim. An engaged witness over a queue the pinned drainer
  leaves alone — which is what a manual-approval history produces — replays coherently and passes,
  as a node-batch regression.
- **R7-5 — the action-kind tag is required and compared whole.** `actionKindFor` (`tools.ts:94`)
  derives the tag from the calling deployment's scope tag and the tool name, so a row on the
  governed resource has exactly one tag its own label can stand beside, and `adapter/commitment.py`
  already owns that derivation. Round 6 compared only the suffix after the last literal colon and
  skipped the comparison outright when the tag was absent or empty, so a coherent other-tool row
  could carry another deployment's scope, or no tag at all, and still classify. `b04` and `h04`
  are rows of the second deployment and leave the governed inventory before the tag is read, so
  their registered outcomes do not move.
- **R6-1 residue — the causal sweep is applied to the claim, not to a list of sites.** Round 6's
  repair reached the four locations round 6 named and left the same sentence three lines away:
  `SPEC.md`'s step 15 still said an effect was "produced by" an unretained call, the builder's
  attestation comment still called a source "the staged call it came from", and PREREGISTRATION
  D-5 still called a modeled cell "the trace the pinned source can actually retain". The
  retryability repair was worse than incomplete — it *introduced* two new `retryable: true`
  assertions, in `SPEC.md`'s `pending` derivation and the matching comment in `verify.py`, about
  a field PREREGISTRATION §9 registers as asserted nowhere. Both are removed; the matrix speaks
  of `callMayHaveTakenEffect` as the pinned source's own flag and never as a retryability claim
  of ours. The causal reading is swept across every living surface — the three named sites plus
  `build_fixtures.py`'s union docstring and its `m01` comment — and two superseded rows of this
  ledger that carry it are annotated rather than rewritten, as the ledger's own rule requires.

**The lesson this round records, because it is the same one twice.** Round 6 fixed the sites a
reviewer named; round 7 found the identical claim a few lines away, four times over, in four
different families. Enumerating what a reviewer reached produces a repair that is true where it
was applied and false everywhere else — and, in `pending`'s crash window, a repair that reads as
a *derivation from source* while covering only the half of the source the reviewer's
reproduction happened to touch. The rule taken forward: derive the invariant from the pinned
source's own symmetry, then check every place the source is symmetric.

### Fixture bytes changed at the round-7 fixes

**None.** No commitment, no ledger, no platform store, no evaluation envelope, no report, no
evidence artifact and no cell manifest changed in either stratum, and
`reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved. `MATRIX-HOLDOUT.json` and
everything under `reviews/` and `pilots/` are untouched. `MATRIX.json` is unchanged — round 7
touched no cell's construction or note, and no `expected` value in either registry moved.
`harness/STUDY-MANIFEST.sha256` is regenerated: its path set is unchanged at 60 entries, and the
digests that move are exactly the source and document files this block edits.

One causal-language site sits outside what this commit may touch: `MATRIX-HOLDOUT.json`'s `h08`
note says "the outer state that pinned source can actually retain", which is the same claim
PREREGISTRATION D-5 was corrected for. The holdout registry is the reviewer's own artifact and is
not edited here; it is recorded so the next round can dispose of it.

## Round-8 fixes (pre-freeze)

Round 8 confirmed that round 7's four symmetries are closed on both sides and that three of its
five dispositions hold as written. What it found is a **third** recurrence of the withdrawn-claim
class on living surfaces, and two governing accounts of the pinned source that are false against
the source — one of them inside the comment block that derives the opposite. All items are
dispositioned in `PREREG-REVIEW.md`; the protocol-relevant changes are recorded here.

**No registered expectation changed in either stratum, no verdict code was added, and no
vocabulary member moved.** A before/after snapshot of all three layer outcomes, every published
`suppressed` code and every upstream engagement list, over all 35 cells and by direct layer calls,
showed **zero drift** — which is the point, because R8-3 changes an adjudication path.

- **R8-1 — the withdrawn-claim class becomes machinery.** The three named sites are repaired to
  describe only what the apparatus locally registers: PREREGISTRATION D-5 now says `m02`'s
  rebuilt cell is a tuple the SPEC §5 compatibility matrix admits, and says nothing about how the
  retained bytes came to be there; `SPEC.md`'s step 15 says `m01`'s retained attestation *names*
  the read path as its source; the `rejected` paragraph and the `pending` bullet speak of tuples
  the matrix admits, with the bold registration that **admitting a pair records what the ceremony
  will not refuse and never that a store came to hold it that way** (§9); and the completed-
  rejection helper and both crash-window docstrings in `test_reachability.py` say the same. The
  guard is `test_living_surfaces_carry_no_withdrawn_claims`, which scans seven withdrawn phrase
  classes — `can actually retain`, `actually emits`, `took effect`, `produced by`, `caused by`,
  `retryab`, `the effect happens` — over a **derived** population: every top-level `*.md` except
  the two narrating ledgers, `adapter/*.md`, every `probes/**/*.ts`, the comments and string
  literals of every `adapter/*.py`, `harness/*.py` and `harness/tests/*.py`, and every string in
  `harness/MATRIX.json`. Text is scanned whitespace-normalized, so a phrase broken across a line
  wrap is still found. Seven allowlist entries license one passage each — §9's three
  registrations, the README's restatement of one of them, §0a's retained-record table row, and
  `m02`'s construction in the registry and in the builder — each anchored to its own passage and
  each carrying its justification; an entry that stops matching fails the test, so a repaired
  site cannot leave a licence behind.
- **R8-2 — the reject path is ordered, not atomic.** `verify.py:92-93` said the inner and outer
  rejections happen "in the same transaction", which contradicts the reject-side crash window
  derived from the same two locations further down the same comment block. The source is
  unambiguous:
  `action-store.ts:209` writes `rejected`, and `overseer.ts:7729-7732` updates the outer row after
  the awaited call returns. The comment now states that ordering and cites the same two locations
  the matrix row cites.
- **R8-3 — the identity rule reaches the witness's own identities.** R7-2 moved identity onto the
  written token and applied it to the store's gatekeeper, ledger and staged-call identities. The
  drain witness was not in that set, so `ceremony.ts` sorted on `witness.pass` unvalidated: a
  witness written `"pass": 1.0` or `"pass": 1e0` arrived as a `NonIntegerLexeme`, `a.pass - b.pass`
  returned `NaN`, the sort silently did nothing, and the cell came out `pass` with
  `AutoApprovalDrainer` engaged — over bytes the binding layer refuses as
  `retained-store-unreadable`. `witnessIdentityProblem()` now holds every identity a witness
  claims — its pass, its gatekeeper id, every applied action id, and every rule's gatekeeper id,
  which is exactly the set `_drain_witness_problem` validates — to `platformId` before anything
  sorts, keys or replays on it. Four regressions: both tokens on the binding side and both through
  the runner. The two layers keep their own vocabularies (`retained-store-unreadable` there,
  `drain-order-violation` here); what is registered is that neither reads a store the other
  refuses.
- **R8-4 — a citation.** `verify.py:169` named "R7-5 of the same family, filed R7-3"; the item is
  the R6-5 residue, filed R7-3.
- **The `h08` note stands, by ruling.** `MATRIX-HOLDOUT.json`'s `h08` note carries the same
  withdrawn phrasing PREREGISTRATION D-5 was corrected for, and the round-7 block above recorded
  it for the next round to dispose of. Round 8 ruled that it must **not** be repaired: the note is
  reviewer prose promised verbatim, not migration-authored prose, so editing the working copy
  would violate PREREGISTRATION §1a's authorship instruction (`:77-84`) and would be caught by
  `test_holdout_expectations_match_the_authored_file_modulo_the_recorded_migration`, which asserts
  every authored note byte-equal. The disposition is this entry. The phrase guard therefore does
  not scan `MATRIX-HOLDOUT.json`, and its docstring records that exclusion beside the others —
  `DEVIATIONS.md` and `PREREG-REVIEW.md`, which must quote the claims they record as withdrawn,
  and `reviews/` and `pilots/`, which are verbatim history this study may not edit at all.

**The lesson this round records, because it is the same one three times.** Round 6 fixed the sites
a reviewer named. Round 7 found the identical claim a few lines away and swept "every living
surface" — by hand, against a list it wrote down. Round 8 found it again, in two of the same files.
A sweep performed by reading is a list whether or not it is written as one, and a list cannot close
a class: it closes the instances someone happened to see, and the class regenerates at the next
edit. The rule taken forward: when the same class of defect survives two repairs, stop repairing
instances and write the check — with the population derived rather than enumerated (R6-7's lesson,
which this reuses), and with every exception named, anchored and justified in the test itself, so
the exceptions are reviewable and a stale one fails.

### Fixture bytes changed at the round-8 fixes

**None.** No commitment, no ledger, no platform store, no evaluation envelope, no report, no
evidence artifact and no cell manifest changed in either stratum, and
`reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved. `MATRIX-HOLDOUT.json` and
everything under `reviews/` and `pilots/` are untouched. `MATRIX.json` is unchanged — the phrase
guard licenses `m02`'s construction rather than requiring it to move, and no `expected` value in
either registry moved. `harness/STUDY-MANIFEST.sha256` is regenerated: its path set is unchanged
at 60 entries, and the digests that move are exactly the source and document files this block
edits.

## Round-9 fixes (pre-freeze)

Round 9 confirmed round 8's other three dispositions and its `h08` ruling, and returned two
blockers: the guard round 8 wrote to close the withdrawn-claim class is porous in four separate
ways and the class is still on live surfaces, and the tree at `6d0fdd5` cannot pass its own
manifest gate. Both are dispositioned in `PREREG-REVIEW.md`; the protocol-relevant changes are
recorded here.

**No registered expectation changed in either stratum, no verdict code was added, and no
vocabulary member moved.** A before/after snapshot of all three layer outcomes, every published
`suppressed` code and every upstream engagement list, over all 35 cells and by direct layer calls,
showed **zero drift** — a fifth consecutive round, and this block touches no adjudication path at
all: it is prose, tests and a manifest.

- **R9-1a — the nine passages.** The five ranges round 9 named carry nine passages, repaired to
  say only what this apparatus registers. `verify.py`'s `pending` bullet no longer says a crash
  leaves a pair retained or that round 7 refused something producible; it says the two connector
  paths write their own record before the outer row, that between those two writes the pair is
  one this study registers no rule against, and — in the same words §9 uses — that admitting a
  pair records what the ceremony will not refuse and never that a store came to hold it that way.
  The `rejected` paragraph speaks of an ordinary tuple the matrix admits rather than of what a
  queue produces. `_check_ledger_lifecycle`'s summary line and its closing sentence, and
  `_connector_outcome_problems`'s docstring, say the registered matrix admits rather than what a
  pinned source can write or produce. SPEC §5's witness paragraph and the matching comment in
  `ceremony.ts` say an engaged witness accounting for no application beside rows that claim none
  is a record this ceremony accepts, and drop the drainer's behavior entirely.
- **R9-1b — the backstop, mechanically.** Four repairs, each to a way a phrase could hide rather
  than to a phrase. **F-strings:** CPython 3.12 (PEP 701) no longer emits an f-string as one
  `STRING` token, so a claim written inside one was invisible to a `COMMENT`/`STRING` reader; the
  extractor now reads `FSTRING_MIDDLE`, drops the delimiters, and therefore also joins the two
  halves either side of a replacement field. **Markers:** `#`, `//`, block-comment rails, bullets,
  headings and quote marks are stripped per line, so `... pair` on one line and `retained` on the
  next read as one sentence instead of as `pair # retained`. **String values:** a literal is read
  through `ast.literal_eval`, so its quotes cannot break a phrase and two adjacent literals join.
  **Runs:** prose is grouped into runs of consecutive lines and runs are joined by a break
  character no pattern can cross — the same change that closes the wrap also has to stop the
  scanner inventing a phrase from two passages that are not one, and a control test asserts two
  comments five lines apart do not join. **Licences:** each entry now registers an exact
  occurrence count at its anchor. Round 9 found the ±400-character window wide enough for a new
  claim written beside a licensed passage to inherit its licence; the count refuses the extra
  occurrence by arithmetic. Twelve entries, one of which covers three occurrences and says which
  three.
- **R9-1c — the backstop is rescoped, because the honest scope is the narrow one.** Two stems are
  added — `can actually` (which subsumes round 7's `can actually retain` and round 9's `can
  actually write`) and `\bproducible\b` (word-bounded, so `reproducible` is not swept in) — plus
  one gapped pattern for `leaves … retained`. The stems that would close the *rest* of the class
  are **not** added and will not be: `admits` and a bare `produces` are this apparatus's own
  registered vocabulary — the matrix admits tuples, evaluators produce dispositions — and a
  backstop that refuses the language the study is written in is a backstop that gets deleted.
  So the test says what it is. Its docstring names it a **lexical backstop over formulations
  already found and repaired**, states that it is not a semantic check and does not decide
  whether a new sentence asserts a withdrawn claim, and hands semantic completeness back to the
  review loop, which has been carrying it all along. `HISTORICAL_FORMULATIONS` makes that
  auditable rather than rhetorical: all 21 formulations rounds 6 through 9 quoted as offending,
  each marked with the phrase class that reaches it or with `None` and the reason — 12 reached,
  9 not. `ROUND_NINE_REPAIRS` does the same for this block's own nine passages: 3 refused by the
  hardened list before repair, 6 not. Both counts are themselves asserted, so widening a stem
  fails the suite until the numbers here are restated. 37 new tests, 198 in the suite.
- **R9-2 — the manifest, in this commit.** `harness/STUDY-MANIFEST.sha256` is regenerated after
  the ledger and banner edits above, not before them, so the commit that changes manifest-covered
  documents is the commit that carries their digests.

**The lesson this round records, first half: a list of phrases is still a list.** Round 8's rule
was "when the same class survives two repairs, stop repairing instances and write the check". The
check was written, and round 9 walked around it four times — twice by wording and twice by
representation. The rule survives, with the correction round 9 forced: a lexical check cannot
close a semantic class, and the failure mode is not porosity, it is a check whose docstring claims
the class while its code holds a list. What a mechanical guard is *for* is making a known defect
unrepeatable; what it must then say is that this is all it does. Coverage that is written down and
counted is worth more than coverage that is implied, because the implied kind is what let three
rounds believe the class was closed.

**And the second half: the record-filing commit is not exempt.** Every fix block in this loop
regenerated the manifest before committing. `6d0fdd5` — the one commit written by hand, to file a
verbatim review record — edited `PREREG-REVIEW.md`, which the manifest covers, and skipped the
step. The tree then failed the exact-set precondition the scorer runs before anything is
adjudicated, which would have made a registered run terminal-invalid, and it stayed that way
until a reviewer ran the suite. The rule taken forward: manifest regeneration belongs to the
*edit*, not to the *kind of work*, and the commits that carry the study's own history are the
ones most likely to be made outside the discipline they record.

### Fixture bytes changed at the round-9 fixes

**None.** No commitment, no ledger, no platform store, no evaluation envelope, no report, no
evidence artifact and no cell manifest changed in either stratum, and
`reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved. `MATRIX-HOLDOUT.json` and
everything under `reviews/` and `pilots/` are untouched. `MATRIX.json` is unchanged — no cell's
construction, note or `expected` value moved, and `m02`'s construction keeps the licence it
already had. `harness/STUDY-MANIFEST.sha256` is regenerated: its path set is unchanged at 60
entries, and the digests that move are exactly the documents and sources this block edits, plus
`PREREG-REVIEW.md`, whose digest `6d0fdd5` left stale.

## Round-10 fix (pre-freeze)

Round 10 confirmed R9-2 resolved, confirmed round 9's nine prose repairs and all four mechanical
repairs sound, ruled on both dispositions round 9 asked it to rule on — the backstop's registered
narrowness is **acceptable**, `verify.py`'s source-level constraint sentences are **lawful** —
and returned one blocker against the licences themselves. It is dispositioned in
`PREREG-REVIEW.md`; the protocol-relevant change is recorded here.

**No registered expectation changed in either stratum, no verdict code was added, and no
vocabulary member moved.** A before/after snapshot of all three layer outcomes, every published
`suppressed` code and every upstream engagement list, over all 35 cells and by direct layer calls,
showed **zero drift** — a sixth consecutive round, and this block is one test file and a
manifest, so the snapshot is trivially zero and is run anyway because a streak that skips the
easy rounds is not a streak.

- **R10-1 — licences become fingerprints.** Round 9's licence was `(surface, phrase, anchor,
  occurrences)`: a match was licensed if the anchor sat within ±400 characters and the total came
  to the registered number. Round 10 broke it in one edit. Section 0a's retained-record row names
  the private connector's outcome field three times in one sentence, so its licence registered
  three; delete one of those three and write a sentence of the withdrawn class into the same row,
  inside the same anchor window, and the total is still three. The adjudicator returned
  `([], [])` on a surface that had just gained a forbidden formulation. Each licensed
  **occurrence** now registers a fingerprint — `(surface, phrase, locator, passage,
  justification)` — where the passage is the exact whitespace-normalized prose around the match,
  clipped to the run it lives in and to ±120 characters either side, so it neither spans a run
  break nor grows with the file. A match is licensed only when some entry no earlier match has
  claimed carries its surface, its phrase, its locator **and** a byte-equal passage; an entry
  nothing matches is dead, and dead fails too, so a repaired site cannot leave a stale licence
  behind. Twelve entries become fourteen fingerprints, the three-occurrence licence becoming
  three with a justification each, and the ±400-character window is deleted along with the count
  it stood in for.
- **R10-1 — the attack is the regression.** The reviewer's edit is held verbatim in
  `SUBSTITUTION_ATTACK` and run against the whole adjudicator over a copy of `adapter/SPEC.md`
  mutated in memory — the tree is never written, and every other surface is read as it stands, so
  what runs is the guard rather than a unit of it. The test asserts the count is three before and
  three after, which is the property that made the attack invisible, and then that the guard
  returns three unlicensed occurrences and three dead fingerprints. The other direction is
  asserted in the same block: the unmutated tree returns `([], [])`, which means every one of the
  fourteen fingerprints is live. A second test hands the adjudicator one fingerprint's own match
  four ways — with a different locator, with a changed passage, twice over, and not at all —
  refused, refused, refused, dead. Two new tests, 199 in the suite; the 21-row historical table,
  its 12/9 split and the asserted coverage arithmetic are untouched.
- **R10-1 — the claim is rewritten to the size of the mechanism.** The guard's docstring said
  reintroduction of a known formulation was *mechanically impossible*. Fingerprints do not say
  that and neither does the docstring now: a licensed occurrence of a known phrase cannot change
  its registered locator or its exact normalized ±120-character passage, and cannot be joined by a
  second without `WITHDRAWN_CLAIM_FINGERPRINTS` being restated. Semantic novelty is the review
  loop's, exactly as round 9's rescope and round 10's Ruling 1 both say. (Round 10's block wrote
  those two clauses as "cannot move to another line, cannot change the sentence around it", which
  claims more than the mechanism does; the wording above is R11-1's correction, recorded under
  *Round-11 fix* below.)

**The lesson this round records: a count is not an identity, and this study already had the
finding.** R5-1 is on its own record at round 5: a governed call carrying a foreign commitment
digest satisfied `len(subject_calls) == authorized == 1` while sitting outside the bound set, and
the fix was to match the inventory by identity rather than by arithmetic. Round 9 then answered a
licence-shadowing blocker with arithmetic — not in the ceremony, where the lesson had been
learned, but in a test, where nobody was reading for it — and round 10 ran the same
delete-one/add-one substitution against it and it passed. The rule taken forward: a guard written
against a class of *thing* must register the things, not how many of them there are; and the
first place to look for the defect you have just written down is the apparatus you wrote it down
with.

### Fixture bytes changed at the round-10 fix

**None.** No commitment, no ledger, no platform store, no evaluation envelope, no report, no
evidence artifact and no cell manifest changed in either stratum, and
`reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved. `MATRIX-HOLDOUT.json` and
everything under `reviews/` and `pilots/` are untouched. `MATRIX.json` is unchanged — `m02`'s
construction keeps the licence it already had, now as a fingerprint, and no cell's construction,
note or `expected` value moved. No source module and no document outside the ledgers and banners
is edited at all: the block is `harness/tests/test_study.py`, this file, `PREREG-REVIEW.md`,
`PREREGISTRATION.md`, `README.md` and the manifest. `harness/STUDY-MANIFEST.sha256` is
regenerated: its path set is unchanged at 60 entries, and exactly three digest lines move —
`PREREG-REVIEW.md`, `PREREGISTRATION.md` and `harness/tests/test_study.py`, the three edited
files the manifest covers. This file and `README.md` are the two documents it deliberately
excludes.

## Round-11 fix (pre-freeze)

Round 11 confirmed R10-1 resolved by execution — all fourteen fingerprints match exactly one
standing occurrence, the held attack yields three unlicensed occurrences and three dead
fingerprints, and changed locator, changed passage, duplication, deletion and banner-shift
reconvergence all behave as designed — and returned no blocker. Its verdict is **freezable after
listed fixes**, the first in this loop that is not DO-NOT-FREEZE, and the one listed fix is a
claim-scope correction. It is dispositioned in `PREREG-REVIEW.md`; the protocol-relevant change is
recorded here.

**No registered expectation changed in either stratum, no verdict code was added, and no
vocabulary member moved.** A before/after snapshot of all three layer outcomes, every published
`suppressed` code and every upstream engagement list, over all 35 cells and by direct layer calls,
showed **zero drift** — a seventh consecutive round, and this block is tests and prose, so the
snapshot is trivially zero and is run anyway, for the same reason as last round: a streak that
skips the easy rounds is not a streak.

- **R11-1 — the claim is cut to the two fields the adjudicator reads.** Round 10's fix left the
  guard describing itself in the vocabulary of lines and sentences: a licensed occurrence "cannot
  move to another line, cannot change the sentence around it". The mechanism does neither of those
  things. It compares four fields, and the two that vary are an *extracted locator* and a
  *normalized passage*. Round 11 demonstrated both gaps on this tree: rewrapping the licensed
  occurrence in `harness/tests/test_study.py`'s own docstring from physical line 1295 to 1296
  keeps locator 1293, because the locator belongs to the token and not to the line; and editing
  the same `README.md` sentence 151 normalized characters away from its match keeps the passage
  byte-equal, because the passage stops at `PASSAGE_RADIUS` either side. Every statement of the
  guarantee — the fingerprint table's own comment, the backstop's docstring, the regression's
  docstring, the round-10 row in `PREREG-REVIEW.md` and the round-10 entry above — now says what
  the mechanism does: a licensed occurrence cannot change its registered locator or its exact
  normalized ±120-character passage, and cannot be joined by a second without
  `WITHDRAWN_CLAIM_FINGERPRINTS` being restated. Nothing about the mechanism changed; only what is
  claimed for it.
- **R11-1 — the regression is described as the thing it runs.** The four-way test hands the
  adjudicator match tuples directly — it does not edit a source file and never did — so its
  docstring now says so, and its two locals are renamed from `moved` and `rewritten` to
  `other_locator` and `other_passage`, which is what they hold. The backstop's *what it does NOT
  claim* paragraph gains the residue the two demonstrations measure: a docstring rewrap that keeps
  the token's locator, and an edit further out than `PASSAGE_RADIUS`, are both outside what a
  fingerprint refuses, and both sit with the review loop where semantic novelty already sits. The
  assertions themselves are unchanged, the fourteen fingerprints keep their passages, and the
  suite stays at 199.
- **R11-1 — the ledger rule is followed while the claim is corrected.** `PREREG-REVIEW.md` says
  an earlier row keeps its words and gains a note rather than being rewritten. The round-10 row
  and the round-10 entry above therefore carry the corrected clause *and* the sentence they
  originally wrote, marked as claiming more than the mechanism does, so the record shows the
  overstatement and its correction rather than only the corrected text.

**The lesson this round records: a mechanism's description is a claim, and it drifts upward.**
Round 10's fix was sound and its sentence about the fix was not — it reached for the reader's
mental model (lines, sentences) instead of the comparison's own fields (locator, passage), and in
doing so promised a guarantee two demonstrations break in a minute. The rule taken forward: state
a guard's guarantee in the vocabulary of what the guard compares, and if the honest statement is
smaller than the intuitive one, the difference is the part that belongs to the review loop and
must be written down as such.

### Fixture bytes changed at the round-11 fix

**None.** No commitment, no ledger, no platform store, no evaluation envelope, no report, no
evidence artifact and no cell manifest changed in either stratum, and
`reviews/round-1/MATRIX-HOLDOUT.authored.json` is byte-preserved. `MATRIX-HOLDOUT.json` and
everything under `reviews/` and `pilots/` are untouched, and `MATRIX.json` is unchanged — no
cell's construction, note or `expected` value moved, and `m02`'s fingerprint keeps its passage and
its locator. No source module and no document outside the ledgers and banners is edited: the block
is `harness/tests/test_study.py`, this file, `PREREG-REVIEW.md`, `PREREGISTRATION.md`, `README.md`
and the manifest. Six registered fingerprint locators move and are reconverged in this commit: the
four on `PREREGISTRATION.md` (`406`→`408`, `408`→`410`, `413`→`415`, `158`→`160`) and the one on
`README.md` (`86`→`92`), because the status banners above them grew; and the self-referential one
— the licensed `producible` in `test_study.py`'s own docstring — from `1293` to `1304`, because the
prose edits above it are eleven lines longer. All six keep a byte-identical passage, which is the
check that says each move is a rewrap and not a rewrite. The coupling is the design and not an
inconvenience: a table that pins locators has to be restated whenever a pinned line moves,
including when the file doing the pinning is one of the files that moved.
`harness/STUDY-MANIFEST.sha256` is
regenerated: its path set is unchanged at 60 entries, and exactly three digest lines move —
`PREREG-REVIEW.md`, `PREREGISTRATION.md` and `harness/tests/test_study.py`. This file and
`README.md` are the two documents the manifest deliberately excludes.

## Registered attempt (post-freeze)

The registered primary attempt ran against the frozen tree at `968a9f8` and is published at
`results/primary-attempt-001/` — `ATTEMPT.json`, `RESULTS.json`, `DETECTION-MATRIX.md` and
`ANALYSIS.md`. It carries `attemptLabel: "REGISTERED"` and `includeHoldout: true`; both are
mechanical, since the label follows the non-null preregistration digest in `PINS.json` and the
scorer refuses a REGISTERED attempt that omits the holdout. **R1 holds**: 27 locked cells
adjudicated, 19 endpoint cells with zero divergences, all six control gates as registered, zero
pipeline-invalid cells and zero validity records. The holdout is scored separately and its verdict
is **`holdout divergent`**: 7 of 8 cells diverge and `h01` is concordant. No expectation, no
fixture byte, no verdict code and no registry moved; the attempt only reads the frozen tree.

**One correction to the frozen text, recorded because this is the only place it may land.**
`PREREGISTRATION.md`'s own status banner reads "**Round 12 has not run**, and the freeze waits on
its confirmation", and its status line still says DRAFT. The freeze happened at `968a9f8` on round
11's *freezable after listed fixes* verdict with that fix landed, and round 12 did not run. The
banner is therefore superseded by the commit that froze the file it sits in, and it is not edited
— the preregistration is never edited again, which is the whole point of the anchor. Every other
sentence of that document governs unchanged; this one is stale in exactly one respect, that the
confirmation round it waits on was not taken before the freeze. What was *reviewed* is unaffected:
eleven rounds ran against this apparatus, all of them dispositioned in `PREREG-REVIEW.md`.

Four things the attempt surfaced are recorded here rather than left to the analysis alone. None of
them changes a registered expectation, and none is a correction to the preregistration.

- **`h06` diverges onto a registered acceptance, and it is reported as a divergence.** The
  reviewer authored `upstream: fail:drain-order-violation` and the frozen apparatus returns `pass`
  with both pinned functions engaged. The acceptance is the one SPEC §5, upstream step 2 registers
  in the sentence that names this exact history — the replay is against a stage-time witness
  rather than a final snapshot, because a rule hard-deleted with no tombstone would make a lawful
  historical apply replay as a violation — and the change is round 1, finding 4, disposed in
  `PREREG-REVIEW.md`. The cell's fixture retains the rule in the witness while the final snapshot
  carries `autoApproveTags: []`, and the drain replay is seeded from `witness.rules`
  (`probes/ceremony.ts:546-548`); no adjudicated check reads the retained `autoApproveTags` at
  all. The equality boundary registered at decisions C1/C4 is load-bearing for this row: the
  approved row's resolution stamp is exactly the witness instant, so it stays in the queue. The
  price is registered in the same place and is not withdrawn by this result: the witness is
  self-asserted, a writer who adds a matching rule to it launders an auto-approval, and
  `drain-order-violation` is consistency with that witness and never historical lawfulness (D-7).
  So this is a documented semantic choice made after the expectations were authored — **not** an
  open blind spot, and **not** an expectation that was met.
- **`h04`'s refusal is at a gate, not on the mechanism it was authored against.** The adjudicated
  code is `commitment-schema-invalid` on `action.toolName`, which aborts the binding layer before
  any numbered check runs, so the derivation oracle the reviewer's note targets never ran on this
  cell. The literal it trips is a product of round 2's scenario re-render, which is recorded above;
  the authored expectations were untouched and the authored file stays byte-preserved. The replay
  layer's `unavailable` on the same cell follows from the same gate and is an apparatus verdict,
  never a detection (SPEC §5). Recorded so no later reader counts `h04` as evidence about step 8.
- **`h05` and `h08` return one code through two different repairs.** `h05` fails the `staged`
  predicate's bound-call conjunct, which exists because of round 1, finding 11; `h08` fails the
  rounds 6–7 retained-outcome compatibility matrix (R6-2), which its own diagnostic cites.
  Attributing both to the later work would overstate what the compatibility matrix closed.
- **`results/` is outside both mechanical guards.** The whole-study manifest's candidate
  population and the phrase guard's derived population each reach top-level documents, the SPEC,
  the adapter, the harness, the probes and the locked registry, and neither recurses into an
  attempt directory. `ANALYSIS.md` is therefore held to PREREGISTRATION §9 by authorship and
  review rather than by machinery. This is a consequence of the manifest's exact-set design
  (attempt outputs are products, not registered inputs) and is recorded, not repaired.

`README.md` gains the result: its status banner goes from DRAFT to frozen-and-run, and a
**Results** section above *How it relates* summarizes both strata and points at `ANALYSIS.md`. Two
stale facts in the same file are corrected while it is open — the layout table said "six review
rounds" where eleven have run, and the *Running* block showed the pre-freeze scorer invocation
without `--include-holdout`, which the frozen tree refuses for a REGISTERED attempt. The banner is
rewritten line-for-line at its previous length so that `README.md`'s registered phrase-guard
fingerprint keeps its locator (`92`) and its byte-identical passage; the round-11 block above
records the same coupling from the other direction. `README.md` and this file are the two
documents the manifest deliberately excludes, so `harness/STUDY-MANIFEST.sha256` is unchanged and
`make_manifest.py --check` exits 0 against the frozen digests.

## Apparatus

- **Probe toolchain (pre-freeze, apparatus only).** The probe layer was designed to run under
  upstream's own vitest; vitest's native rollup binary requires glibc ≥ 2.32 and this host
  provides 2.31. The runner instead bundles each probe entrypoint with the pinned clone's own
  esbuild and executes it under the pinned node. Same pinned sources, same aliases, same single
  injected seam; esbuild and typescript are now themselves pinned and enforced.

## Pilots

Four attempt records are retained under `pilots/`: `build-pilot-01` and `build-pilot-02` predate
the round-1 rebuild and are kept as the record of the apparatus round 1 reviewed;
`rebuild-pilot-03` is the post-round-1 apparatus; `rebuild-pilot-04` is the post-round-2
apparatus. Exactly one registry expectation has been corrected against an observed run, named
above (`neg-mcp-byo-autoapply`); every other change was driven by review or by source
verification.
