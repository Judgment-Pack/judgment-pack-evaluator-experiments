# Analysis — Study 014 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command
from the freeze commit (`76241e73`, the squash-merge of PR #49), CPython 3.12.11,
jpack v0.16.0 (`7c11ebef…9325`), OpenWorkProof `8eeca6f` tracked-clean, label
`REGISTERED`. Every pin and the whole-study manifest verified before adjudication;
post-adjudication integrity intact with zero mismatches. This document is post-run
analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **Locked replication (R1)**: `R1 holds (REGISTERED)` — 39 cells, 39 adjudicated,
  32 endpoint, **0 endpoint-divergent**, 0 pipeline-invalid, all control gates green,
  the demonstration and descriptive rows as registered.
- **Reviewer holdout (first execution)**: **concordant — 8/8 adjudicated, 0 divergent,
  0 pipeline-invalid**. All eight cells were constructed inside the attempt on their
  first-ever execution and landed exactly as the cross-vendor reviewer registered them
  at round 2, before any of them existed.

## What the holdout's first execution established

The holdout stratum is the study's only prospective evidence, and it is the reviewer's,
not the maintainer's:

- `h01`/`h06` (artifact edits): the byte-level rules fire on exactly the registered
  codes — a single appended newline on the retained commitment is
  `commitment-schema-invalid`; a cross-execution retained envelope is
  `disposition-digest-mismatch-retained`.
- `h02` (lone-surrogate signed objective): constructible after all — OpenWorkProof signs
  it — and the binding layer returns the registered schema code rather than crashing,
  with replay correctly `unavailable` (no conforming commitment exists to replay).
- `h03` (duplicate supported-extensions): the reviewer's deliberate implementation trap.
  The set-semantics rule (round-2 finding R2-8) is what catches it; without that fix
  this cell would have diverged, exactly as the reviewer predicted when authoring it.
- `h04`/`h05` (replay-tuple members): replay alone catches an implicit-empty evidence
  substitution (`replay-disposition-mismatch`) and an `evaluatorSpecVersion` forgery
  (`replay-spec-version-mismatch`) while binding stays green — the replay layer carries
  weight the digests alone cannot.
- `h07` (self-consistent wrong action): commitment and receipt agree with each other and
  the chain is fully valid; only the registered disposition→action map refuses it
  (`action-map-violation`). This is the sharpest form of the study's thesis: agreement
  between attacker-controlled records is not authorization.
- `h08` (semantic remint control): a coherently rebound whitespace-only change passes
  all three layers — the composition permits legitimate re-decision, so the detections
  above are not artifacts of brittleness.

## Detection ownership (R2, descriptive)

As registered: OpenWorkProof's unchanged verifier owns tamper-after-signing,
causal-chain, authorization-window and evidence-set integrity (every F-cell, the
tampered D/A variants, e19, e21); the adapter's binding layer alone sees judgment-side
substitutions in validly re-signed chains (the resigned A/B/D cells, c10–c12, c15, d18,
e20, h01, h03, h06, h07); deterministic replay under the pinned tuple alone sees
outcome and tuple forgeries whose retained artifacts are internally consistent (c13,
c14, e23, h04, h05); and the two registered expected-undetected cells (e18 currency,
e22 policy rollback) passed all layers — the boundary stands: no chain-internal
evidence can see them, and detecting them would require an anchor outside the chain.

## Claims and non-claims

Within the registered scenarios, mutation set and holdout set, the composition — an
independently developed execution-verification protocol at a pinned commit, its verifier
unchanged, plus a registered thin adapter and deterministic JPS replay — detected every
registered substitution of judgment artifact, inputs, disposition and executed action,
offline, from retained artifacts and the work order's pinned keys, with every detection
attributed to exactly one layer. The locked stratum is a replication of observed
behaviour; the holdout stratum is prospective and reviewer-authored.

Non-claims, unchanged from the preregistration (§9): no policy or fact truth; a JPS
disposition is not authorization; no JPS conformance; no OpenWorkProof security audit or
endorsement; no coverage beyond the registered cells; no generalization beyond this
protocol, commit, pack, action encoding and machine; the trust roots are the work
order's six study-minted keys, the pinned jpack executable, the adapter code, and the
retained artifact store. Binding/lineage, not truth.
