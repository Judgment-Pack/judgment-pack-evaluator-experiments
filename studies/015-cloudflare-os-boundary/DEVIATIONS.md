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
- **`m02-ambiguous-commit` is rebuilt** (round 1, finding 6): its earlier fixture showed the
  outer workspace record `approved` with an `appliedAt` stamp, which the platform cannot produce
  for a throwing apply. The fixture now carries the trace the pinned source can actually retain.
- **Four cells added**: `neg-binding-control` and `neg-replay-control` (layer liveness through
  the official scorer), `a04-judgment-identity-forged` and `b07-stage-revision-mismatch` (two
  commitments that round 1 found were carried and never checked).
- The registry moves to `matrixVersion` 2 with an extended per-cell schema
  (`mutationConstraint`, `modeledDependencies`, `upstreamChecksReplayed`) and the layer key
  `cf`→`upstream` with `not-engaged` as a distinct outcome.
- **The holdout was migrated mechanically, never revised.** The reviewer's authored file is
  preserved byte-for-byte at `reviews/round-1/MATRIX-HOLDOUT.authored.json`. The migration
  re-keys the layer and field names and, for cells registering no replayed checks, translates the
  authored `pass` to `not-engaged` (the reviewed apparatus reported non-engagement as pass). A
  harness test asserts nothing else differs.
- **The effect-attestation schema changed, and 23 cells regenerated** (round 5, findings 4 and 6;
  decisions D1/D3/E). Twenty-one `platform.json` files changed for the schema alone: the effect's
  `gatekeeperId`/`action` pair moved inside a `source` union, `staged-call` in twenty of them and
  `read-path` in `m01`, whose effect never came from a staged call. Two `ledger.json` files
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
  as proof of source history, and any wording that suggested otherwise is in scope for the
  round-5/6 source-of-truth sweep.

### Apparatus items closed at round 5/6

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
  `drain-order-violation` in the replay.
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
  `staged-call` source is joined to the bound call; the other arms are counted against the same
  cap and matched against nothing. `m01`'s effect becomes `read-path`, which is what its
  construction always said it was, and `b06` still *claims* a staged call against a store holding
  none — that contradiction is the cell, and it fails on the count exactly as before. SPEC §0a
  and step 15 now state the union and that the join establishes agreement between two retained
  records, never causation (PREREGISTRATION §9).

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
