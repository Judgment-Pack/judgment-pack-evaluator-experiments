# Analysis — Study 016 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command
from the freeze commit (`2877e29`, the squash-merge of PR #55), CPython 3.12.11,
jpack v0.17.0 (`42f35f79…22e9`, digest-checked), OpenWorkProof `8eeca6f` tracked-clean,
label `REGISTERED`. Every pin and the whole-study manifest verified before adjudication;
holdout post-adjudication integrity intact across all 100 stamped files. This document is
post-run analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **Locked replication (R1)**: `R1 holds (REGISTERED)` — 22 cells, 22 adjudicated,
  11 endpoint, **0 endpoint-divergent**, 0 pipeline-invalid, all eight control gates
  green, the demonstration and descriptive rows as registered, and the split-view pair's
  fork structurally validated from bytes (authenticated under the pinned authority key)
  with contradictory adjudicated verdicts.
- **Reviewer holdout (first execution)**: **concordant — 10/10 constructed (`built`),
  10/10 adjudicated, 0 divergent, 0 pipeline-invalid**. All ten cells were constructed
  inside the attempt on their first-ever execution and landed exactly as the
  cross-vendor reviewer registered them at review round 2, before any of them existed.

## What the holdout's first execution established

The holdout stratum is the study's only prospective evidence, and it is the reviewer's,
not the maintainer's:

- `h01` (duplicate trust-configuration member): strict configuration parsing refuses
  (`currency-unavailable`) even where last-wins parsing would have preserved baseline
  semantics — the round-2 residual closure carries weight, and a malformed pin never
  degrades to "no pin".
- `h02` (boolean where the attested position's integer belongs): the closed schema
  refused (`snapshot-chain-inconsistent`) **before** the now-stale attestation signature
  could claim the failure — the schema-before-signature ordering is real, not prose.
- `h03` (minimum head pin naming a sibling prefix, over a history that also rebinds):
  the recency floor won first-failure attribution
  (`snapshot-behind-pinned-minimum-head`) before the fold could reach the rebind — the
  registered step order held under competing defects.
- `h04` (rebind of a still-active version): binding immutability applies while a version
  is current, not only across retirement (`binding-rebound`).
- `h05` (forged replay tuple + retired version on one chain): REPLAY and CURRENCY failed
  **independently** (`replay-executable-mismatch` / `not-current-at-snapshot`) — layer
  attribution survives coexisting failures.
- `h06` (successor chain against a v0.1.0-only registry): the currency layer read the
  committed identity from the chain's signed binding point, not from cell plumbing
  (`not-current-at-snapshot` for the successor tuple).
- `h07`/`h08`/`h09` (the three exact-at-limit boundaries): a supported set at exactly
  512, a checkpoint list at exactly 1024, and a snapshot at exactly 1 MiB each verify —
  the registered limits are inclusive at the boundary and refuse only strictly above.
- `h10` (every authority key-id label swapped to the foreign key, no signed byte
  touched): all four layers pass — the holdout's designed brittleness control: the
  explicitly unauthenticated labels drive nothing, and the detections above are not
  label-matching artifacts.

## Detection ownership (R2, descriptive)

As registered: OpenWorkProof's unchanged verifier, and Study 014's frozen binding and
replay layers, own what they owned there — each proven alive under this study's v0.17.0
toolchain by its own negative control (`neg-owp-alive`, `neg-binding-alive`,
`neg-replay-alive`). The currency layer alone sees registry state: retired-version reuse
(`cur-retired-reuse`, the core positive result — the same chain bytes as the positive
control, refused purely because the signed world moved), invalid, replayed,
chain-broken, and rebound registry state, the unknown series, and the unpinned-genesis
refusal.

And, with the same standing, what **nothing** catches — the three registered boundary
results, each confirmed exactly as registered:

- **The work-order remint** (`cur-workorder-remint-accepted`, descriptive): an identical
  judgment commitment under an alternative, equally valid work order passes all four
  layers. A pack-version registry cannot see it — the tuple it keys on is unchanged
  (RFC 0011 R-1's boundary, now measured rather than argued).
- **The split view** (`cur-split-view-a/b` + the stateful arm): one authority, one
  pinned genesis, two internally valid contradictory histories; each run is individually
  correct and no code in either reveals the fork to a fresh, stateless, per-series-pinned
  verifier — while `cur-split-view-b-stateful` shows the identical presentation refused
  by prefix containment the moment prior-acceptance state exists. The silence is exactly
  statelessness; what would make split views observable in general is the
  transparency-log / witness / cross-signing direction RFC 0011 leaves unresolved.
- **The freshness floor** (`cur-concurrent-set`'s registered second reading and the
  byte-identical `dem-freshness-*` group): the verdict is membership at the pinned
  snapshot, and provably cannot distinguish a legitimately-used-then-audited decision
  from a genuine stale reuse, nor a withheld newer snapshot from a world that genuinely
  stopped.

## Claims and non-claims

Within the registered cells, a minimal hash-chained, independently signed pack-version
currency registry — consumed as one added fail-closed step over Study 014's unchanged
three-layer ceremony — detected reuse of a pack version retired at the pinned snapshot
and refused every registered invalid-registry state, offline, from retained artifacts
and out-of-band pins alone; and the same apparatus, unmodified, **accepted** the
registered out-of-scope and above-its-ceiling constructions, establishing empirically
where a single-operator signed registry stops. The locked stratum is a replication of
observed behaviour; the holdout stratum is prospective and reviewer-authored.

Non-claims, unchanged from the preregistration (§9): no policy or fact truth — the
registry states which versions an authority asserts in force, never that anything is
true or correct; no real-time staleness (every verdict is membership at a pinned
snapshot); no authorization-contract currency; no equivocation resistance — its absence
for the fresh stateless verifier is the finding; no trust from nothing; no format
proposal and no interoperability claim for the registry (one study-registered schema,
written and consumed by the same project — RFC 0011's Implementation section names the
stronger evidence, a consumer step built by the receipt protocol's author, and this
study is not it); no claim about OpenWorkProof beyond Study 014's; no JPS conformance.
The registry authority is the study, and the trust roots are enumerated in the
preregistration. Binding/lineage, not truth.
