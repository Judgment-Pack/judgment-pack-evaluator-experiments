# Deviations and corrections — Study 015

Live from the first draft. Before the freeze this file records protocol-relevant changes
of course; after the freeze it is the only place corrections may land — the
preregistration is never edited again.

## Pre-freeze record

- **Probe toolchain pivot (pre-freeze, apparatus only).** The probe layer was designed to
  run under upstream's own vitest; vitest's native rollup binary requires glibc ≥ 2.32
  and the apparatus host provides 2.31. The runner instead bundles each probe entrypoint
  with the pinned clone's own esbuild and executes it under the pinned node. Same pinned
  sources, same aliases, same single injected seam; recorded in `harness/PINS.json`
  (`importNote`) and PREREGISTRATION §2.
- **Fixture typecheck scope (pre-freeze, apparatus finding).** Holding ledger records to
  the server-side `ActionRecord` type directly is not reproducible from the committed
  upstream tree: the backend graph typechecks only against a wrangler-regenerated
  `worker-configuration.d.ts`. The gate holds records to the published contract
  (`ActionLogEntry` and member types, the two server-only fields stripped and stated)
  instead, and the finding is recorded in `harness/PINS.json`
  (`backendTypecheckFinding`) and `harness/typecheck.py`.
- **Build pilots.** `pilots/2026-08-09-build-pilot-01` ran before ledger records carried
  `resourceTitle`/`resourceUrl` (added for contract fidelity when the typecheck gate
  landed); `build-pilot-02` is the same registry over the rebuilt fixtures. Both
  pilot attempts adjudicated every cell exactly as registered; no registry expectation
  has been corrected against a pilot observation so far. Both are retained in full.
