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
