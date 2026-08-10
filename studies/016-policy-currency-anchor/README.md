# Study 016 — the policy-currency anchor: what a signed pack-version registry catches, and where it must fail

**Status: DRAFT. Nothing is frozen and nothing has run under a freeze.**

Study 013 asked whether the application that acts on a judgment respects it at runtime
(behavior). Study 014 asked whether a third party can prove, offline, which judgment
authorized which executed action (provenance/binding) — and registered, in its §4c, a class
nothing chain-internal can see: a decision carried under a pack version that is no longer in
force. [RFC 0011](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md)
is the design record for the missing anchor. This study operationalizes it at the lowest
possible commitment and asks:

> Within the registered cells, can a hash-chained, independently signed, offline-verifiable
> pack-version currency registry — consumed as **one added step** over Study 014's unchanged
> three-layer ceremony — detect a decision carried under a retired pack version, refuse
> invalid and replayed registry state, correctly **accept** what is out of its scope, and
> fail **exactly where a single-operator signed registry must fail**?

The expected-undetected cells are the point, not a concession. Three boundaries are
registered as results in advance:

- **Authorization-contract rollback** (`cur-authz-rollback-accepted`): Study 014's e22
  construction — an identical judgment commitment under a different, validly signed work
  order — must pass all four layers, because the tuple `(packId, packVersion, packDigest)`
  is unchanged. The anchor addresses pack-version staleness only (RFC 0011 R-1).
- **Split-view equivocation** (`cur-split-view-a/b`): one authority, one pinned genesis, two
  internally valid contradictory histories. Each run verifies cleanly on its own; the
  contradiction exists only across the pair, which no single offline verifier can see. This
  is the empirical case for transparency-log / witness / cross-signing governance —
  preserved as a finding, never fixed.
- **The freshness floor** (`cur-older-snapshot-unpinned` and the byte-identical
  `dem-freshness-*` pair): the verdict is membership at a pinned snapshot, never "stale when
  used" — exhibited as registered byte-identities, not argued.

## Shape

- **Chains**: four, built through Study 014's frozen machinery consumed as a pinned
  unmodified upstream (`harness/upstream014.py` enforces every source digest) under the
  jpack v0.17.0 replay tuple. Layers OWP / BINDING / REPLAY are Study 014's frozen adapter,
  unchanged; OpenWorkProof (pinned commit `8eeca6f`, package digest byte-identical to
  014's) is never modified.
- **Registry**: a minimal deterministic prototype inside this study
  ([`registry/SPEC.md`](registry/SPEC.md)) — signed add/retire/reinstate checkpoints,
  hash-chained, with signed snapshot heads; an offline verifier whose whole trust is two
  out-of-band pins (authority key + genesis head) plus an optional persisted minimum head.
  **A study registration, not a format proposal**: nothing lands in JPS, the runtime, or
  the gateway.
- **Cells**: a cell is `(chain, retained artifacts, registry snapshot, trust
  configuration)`. Most cells share the baseline chain's bytes and vary only the signed
  registry state — the move that makes currency observable where 014's §4c could not: the
  world-that-moved is itself a retained, signed, pinned artifact.

## Layout

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — governing document (DRAFT until frozen).
- [`registry/`](registry/) — the registered schema/ceremony (`SPEC.md`), the writer, and
  the offline currency verifier.
- [`harness/`](harness/) — pins, matrices, fixture builder, four-layer runner, scorer,
  deterministic tests.
- [`fixtures/`](fixtures/) — vendored packs and the 20 frozen cells.
- `pilots/` — pre-freeze execution, labeled harness validation, non-citable.
- `results/` — absent until a registered post-freeze attempt.

Independent open-source project this study builds on:
[OpenWorkProof](https://github.com/dengyier/OpenWorkProof) (Apache-2.0 per its LICENSE;
packaging metadata inconsistently declares MIT — recorded as found), consumed exactly as
Study 014 consumes it, unmodified at the same pinned commit. Not affiliated with Judgment
Pack — that independence is the point.

Nothing in this repository claims any JPS conformance.
