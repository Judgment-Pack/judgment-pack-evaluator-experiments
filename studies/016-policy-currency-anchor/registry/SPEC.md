# The currency registry — schema, ceremony, and the Layer CURRENCY contract

Status: REGISTERED with the Study 016 preregistration (the digest in
`harness/PINS.json` governs after the freeze; this revision incorporates the
round-1 review dispositions, `PREREG-REVIEW.md`). This document is the
registered contract of the study's registry prototype: the checkpoint and
snapshot schema, the verifier's trust configuration, the ordered verification
ceremony, and the exhaustive verdict vocabulary. It operationalizes RFC 0011
§§1–2 at the lowest possible commitment — **it is a study registration, not a
format proposal**: nothing here lands in JPS, the reference runtime, or the
gateway, and no producer or consumer outside this study is bound by it.

Vocabulary: "JCS" is RFC 8785 canonical JSON, computed by the `rfc8785`
package — the same canonicalization OpenWorkProof signs over and JPS Core §8.3
defines for dispositions. All digests are SHA-256; `sha256:`-prefixed where the
runtime convention applies. Signatures are Ed25519. Domain separation follows
OWP's style so no registry digest can collide with an OWP protocol digest or
the Study 014 commitment digest.

## 1. The checkpoint record

One signed lifecycle **event** over a pack series — the registry is an
append-only event history, never a table of "the current version" (RFC 0011
R-8).

```json
{
  "checkpoint": {
    "checkpointVersion": "1",
    "sequence": 3,
    "seriesId": "https://example.com/judgment-packs/expense-approval",
    "event": "retire",
    "packVersion": "0.1.0",
    "effectiveFrom": "2026-02-01T00:00:00Z",
    "previousCheckpointDigest": "sha256:<64 lowercase hex>"
  },
  "checkpointDigest": "sha256:<64 lowercase hex>",
  "authorityKeyId": "ed25519:<64 lowercase hex>",
  "signature": "<base64>"
}
```

- `event` ∈ {`add`, `retire`, `reinstate`}. `packDigest` (`sha256:` over the
  exact pack file bytes — the runtime convention Study 014 adopted, an
  expedient while RFC 0001's digest scheme is unsettled, RFC 0011 §0) is
  carried **exactly on `add` events**.
- Lifecycle rules the fold enforces (round-1 R1-13): a `(packVersion,
  packDigest)` binding is immutable once added, across retirement — a later
  `add` of an already-bound version is `binding-rebound` when the digest
  differs and an inconsistent history when it is the same; **`reinstate` is
  the only re-entry event**. Retiring a non-current version and reinstating a
  non-retired one are inconsistent histories.
- `sequence` is 1-based and contiguous; `previousCheckpointDigest` is the
  predecessor's `checkpointDigest`, `null` exactly on sequence 1. The genesis
  checkpoint's digest is the out-of-band **genesis pin**.
- `effectiveFrom` is **carried and never compared** (decision D-5): no clock
  exists anywhere in the ceremony, and no verdict reads this field. It records
  the authority's assertion for human audit only.
- Signed bytes: `JCS({"domain": "jps-study016-currency/checkpoint/1",
  "payload": <checkpoint>})`. `checkpointDigest` is SHA-256 over those bytes;
  the stored value is convenience and the verifier recomputes it.
  `authorityKeyId` is `"ed25519:" + sha256hex(raw public key)` and is
  **unauthenticated** — see §3 on what that means for attribution.

The registry states which versions an authority asserts in force. It does
**not** state that a decision was correct, that facts were true, or that an
action was authorized — binding/lineage, not truth.

## 2. The snapshot and the trust configuration

A **snapshot** is a checkpoint prefix plus a signed head attestation:

```json
{
  "snapshotVersion": "1",
  "checkpoints": [ <checkpoint records, sequence order> ],
  "attestation": {
    "payload": {"snapshotVersion": "1", "head": "sha256:…", "position": 3},
    "authorityKeyId": "ed25519:…",
    "signature": "<base64>"
  }
}
```

`head` is the last checkpoint's digest and `position` its sequence; the
attestation is signed over `JCS({"domain": "jps-study016-currency/snapshot/1",
"payload": …})`, and its payload's own `snapshotVersion` is checked (a signed
version-2 payload does not pass a version-1 ceremony).

The **trust configuration** is the verifier's out-of-band state — pins, not
artifacts of the chain or the registry:

```json
{
  "trustConfigVersion": "1",
  "seriesId": "https://example.com/judgment-packs/expense-approval",
  "authorityPublicKey": "<base64 raw Ed25519 public key> | null",
  "genesisHead": "sha256:… | null",
  "minimumHeadPin": {"head": "sha256:…", "position": 3} | null
}
```

- **The pins are per-series** (round-1 R1-10; RFC 0011 R-9): Core §10 forbids
  inferring authority from a series URL, so `seriesId` states exactly which
  series these pins confer authority over, and a commitment for any other
  series is refused as `currency-unavailable` — the configuration does not
  cover it.
- The minimal trust for a fresh verifier is **two pins**: the authority key
  trusted for the series, and a genesis head accepted as real. Below the
  genesis pin the verifier is trust-on-first-use, and with either pin null it
  must refuse to call anything current (`currency-unavailable` — fail-closed,
  never a pass).
- **`minimumHeadPin` is caller-provisioned prior-acceptance state, not
  verifier-persisted storage** (round-1 R1-5): this layer holds no storage and
  returns no state update. The cells that use it register it as the state a
  sequential production verifier would have persisted after accepting an
  earlier snapshot; a durable high-water lifecycle (atomic persistence,
  update-on-accept) is future work and is not claimed. A malformed member —
  anything other than `null` or `{head, position}` with a well-formed digest
  and positive integer — refuses as `currency-unavailable`; it never degrades
  to "no pin".

## 3. The Layer CURRENCY ceremony

Ordered, fail-closed, offline; first failure wins. Inputs: the judgment
commitment extracted from the **signed binding point** of the already-verified
chain (Study 014 `adapter/SPEC.md` §5 — layers OWP/BINDING/REPLAY run first
and unchanged; each layer records independently for attribution), the retained
snapshot bytes, and the trust configuration. Fail-closed means every input
lands in the registered vocabulary (round-1 R1-3): duplicate-member-rejecting
strict JSON, closed schemas checked before any canonicalization or signature
math, exception-bounded canonicalization, and registered size limits (round-1
R1-7; RFC 0011 R-13) — `MAX_SNAPSHOT_BYTES` 1 MiB, `MAX_CHECKPOINTS` 1024,
`MAX_SUPPORTED_SET` 512 — chosen so every limit is independently reachable —
refusing before unbounded work.

1. **Pins.** Well-formed version-1 trust configuration with a bound series, a
   pinned authority key, and a pinned genesis head, else `currency-unavailable`.
2. **Inputs.** A conforming commitment whose `packId` equals the configured
   `seriesId` (else `currency-unavailable` — per-series pins confer no
   authority elsewhere), and present snapshot bytes.
3. **Snapshot artifact.** Byte limit; strict parse; exact closed schema for
   the snapshot object, the attestation (including its payload's
   `snapshotVersion`), and every checkpoint record — types, member sets,
   digest formats — all before any signature is checked. Defects:
   `snapshot-limits-exceeded` or `snapshot-chain-inconsistent`.
4. **Signatures, under the pinned key alone** (round-1 R1-6). Every signature
   — attestation and each checkpoint — either verifies under the pinned
   authority key or the snapshot fails `snapshot-signature-invalid`. The
   record's `authorityKeyId` is an unauthenticated label: it is compared and
   reported in `detail` for legibility, but **a wrong signer and a corrupted
   signature are indistinguishable to a single-pinned-key offline verifier**,
   and the vocabulary says so by giving them one code. Stored checkpoint
   digests are recomputed; a mismatch is `snapshot-chain-inconsistent`.
5. **Structure.** Contiguous 1-based sequence; each record binds its
   predecessor's digest; the first record's digest equals the pinned genesis
   head; the attestation describes exactly this list (head and position).
   Any violation: `snapshot-chain-inconsistent`.
6. **The recency floor.** If `minimumHeadPin` is provisioned, the snapshot
   must **contain** the pinned head at its pinned position (prefix
   containment, so a same-length different fork also refuses), else
   `snapshot-behind-pinned-minimum-head`.
7. **Fold and membership.** Fold the series' events to its supported set at
   the snapshot position under the §1 lifecycle rules (`binding-rebound` /
   `snapshot-chain-inconsistent` / `snapshot-limits-exceeded` on violation).
   A snapshot with no events for the series is `series-unknown-at-snapshot` —
   never-registered is not retired (decision D-4). Membership passes;
   non-membership is `not-current-at-snapshot`.

**What the verdict means, exactly.** A failure at step 7 is "this
`(version, digest)` is not in the supported set **at the pinned snapshot's
position**" — membership against one signed assertion by one pinned
authority, and nothing more. It is **not** "this decision was stale when
used": a decision legitimately made and acted on while its version was
current, audited after retirement, reads identically to a genuine stale reuse
(the `dem-freshness-*` byte-identity group exhibits this). A pass is **not**
"current right now": nothing here holds a notion of *now* — the attestation
carries a position, not a time — and a retirement above the pinned snapshot is
invisible. And a single operator holding both the signing key and the history
can show **a fresh, stateless, per-series-pinned verifier given exactly one
view** either of two contradictory valid histories (`cur-split-view-*`) —
that narrowly-stated impossibility (round-1 R1-4) is the registered case for
transparency-log-style governance; the stateful arm
(`cur-split-view-b-stateful`) shows prior-acceptance state converting the
silence into a refusal, so what the fresh verifier lacks is exactly state.

## 4. The verdict vocabulary (exhaustive)

Layer outcome strings are `pass`, `fail:<code>`, or `unavailable` (the pair
verdict `unavailable`/`currency-unavailable`, definitionally). A harness test
diffs this table against `registry/verify_currency.py`'s declared codes and
the scorer's classification, and constructs a minimal condition for every
code, asserting the exact code and the first-failure ordering.

| Code | Meaning |
|---|---|
| `currency-unavailable` | a required input or out-of-band pin is absent or malformed: no well-formed trust configuration, no bound series or a commitment for a different series, no authority key, no genesis head, a malformed `minimumHeadPin`, no conforming commitment tuple, or no snapshot artifact — fail-closed, never a pass |
| `snapshot-signature-invalid` | a signature — head attestation or checkpoint — does not verify under the pinned authority key. Covers both a corrupted signature and a different signer: the two are indistinguishable to this verifier, and the unauthenticated key-id label appears in detail only |
| `snapshot-chain-inconsistent` | strict-parse, schema, digest-recomputation, sequence, predecessor-linkage, genesis, head-attestation, or fold-transition defect — the artifact is not one authenticated append-only prefix |
| `binding-rebound` | the history rebinds a version to a different digest — refused even under the authority's own valid signature |
| `snapshot-limits-exceeded` | the snapshot, its checkpoint list, or the folded supported set exceeds a registered resource limit — refused before unbounded work (RFC 0011 R-13) |
| `snapshot-behind-pinned-minimum-head` | the snapshot does not contain the caller-provisioned minimum head at its position — prefix containment, so an older snapshot and a same-length different fork both refuse |
| `series-unknown-at-snapshot` | the snapshot carries no events for the configured series — an empty answer, distinct from a retirement |
| `not-current-at-snapshot` | the `(version, digest)` is not in the series' supported set at the snapshot position — the whole verdict, nothing more |

## 5. What each layer owns (and what none does)

- **OWP** owns everything Study 014 registered: signature validity,
  causal-chain integrity, authorization, policy-predicate arithmetic over
  asserted execution facts, evidence-set exactness, request-replay protection.
- **BINDING / REPLAY** own the judgment commitment and its deterministic
  recomputation, unchanged from Study 014's registered contract (each proven
  alive under this study's toolchain by its own negative control, round-1
  R1-8).
- **CURRENCY** owns membership of the committed pack version at a pinned
  registry snapshot, and the integrity of the registry artifact itself under
  the per-series pins.
- **Nothing** owns: authorization-contract currency
  (`cur-workorder-remint-accepted`: an unchanged commitment tuple under an
  alternative, equally valid work order is accepted — a remint, not a
  rollback, since OWP has no contract ordering; the receipt protocol's class,
  not pack currency's; RFC 0011 R-1); cross-view consistency for a fresh
  stateless verifier (`cur-split-view-*`); the gap between a pinned snapshot
  and the world above it (`cur-concurrent-set`'s registered second reading,
  and the freshness group). Each has a registered cell or reading whose
  outcome states it.

Ceiling, all four layers, stated once and meant: binding/lineage, not truth —
the registry adds *which version an authority asserted in force at a pinned
snapshot position*, and nothing else.
