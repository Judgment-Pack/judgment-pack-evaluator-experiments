# The currency registry — schema, ceremony, and the Layer CURRENCY contract

Status: REGISTERED with the Study 016 preregistration (the digest in
`harness/PINS.json` governs after the freeze). This document is the registered
contract of the study's registry prototype: the checkpoint and snapshot schema,
the verifier's trust configuration, the ordered verification ceremony, and the
exhaustive verdict vocabulary. It operationalizes RFC 0011 §§1–2 at the lowest
possible commitment — **it is a study registration, not a format proposal**:
nothing here lands in JPS, the reference runtime, or the gateway, and no
producer or consumer outside this study is bound by it.

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
  carried **exactly on `add` events**; a `(packVersion, packDigest)` binding is
  immutable once added, across retirement — rebinding is `binding-rebound`,
  refused even under the authority's own valid signature.
- `sequence` is 1-based and contiguous; `previousCheckpointDigest` is the
  predecessor's `checkpointDigest`, `null` exactly on sequence 1. The genesis
  checkpoint's digest is the out-of-band **genesis pin**.
- `effectiveFrom` is **carried and never compared** (decision D-5): no clock
  exists anywhere in the ceremony, and no verdict reads this field. It records
  the authority's assertion for human audit only.
- Signed bytes: `JCS({"domain": "jps-study016-currency/checkpoint/1",
  "payload": <checkpoint>})`. `checkpointDigest` is SHA-256 over those bytes;
  the stored value is convenience and the verifier recomputes it.
  `authorityKeyId` is `"ed25519:" + sha256hex(raw public key)`.

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
"payload": …})`.

The **trust configuration** is the verifier's out-of-band state — pins, not
artifacts of the chain or the registry:

```json
{
  "trustConfigVersion": "1",
  "authorityPublicKey": "<base64 raw Ed25519 public key> | null",
  "genesisHead": "sha256:… | null",
  "persistedMinimumHead": {"head": "sha256:…", "position": 3} | null
}
```

The minimal trust for a fresh verifier is **two pins**: the authority key
trusted for the series, and a genesis head accepted as real. Below the genesis
pin the verifier is trust-on-first-use, and with either pin null it must
refuse to call anything current (`currency-unavailable` — fail-closed, never a
pass). `persistedMinimumHead` is optional verifier state; the matrix registers
both arms of what its presence decides.

## 3. The Layer CURRENCY ceremony

Ordered, fail-closed, offline; first failure wins. Inputs: the judgment
commitment extracted from the **signed binding point** of the already-verified
chain (Study 014 `adapter/SPEC.md` §5 — layers OWP/BINDING/REPLAY run first
and unchanged; each layer records independently for attribution), the retained
snapshot bytes, and the trust configuration. `seriesId := judgment.packId`;
the membership candidate is `(judgment.packVersion, judgment.packDigest)`.

1. **Pins.** Trust configuration present with a pinned authority key and a
   pinned genesis head, else `currency-unavailable`.
2. **Inputs.** A conforming commitment with a complete identity tuple and a
   readable version-1 snapshot, else `currency-unavailable`.
3. **Head attestation.** `authorityKeyId` equal to the pinned key's id, else
   `snapshot-authority-unpinned`; signature valid over the canonical
   attestation bytes, else `snapshot-signature-invalid`. Key identity is
   checked before signature math — the codes turn on which failed.
4. **Checkpoints.** For each record in order: schema shape, key id, signature,
   and stored-digest recomputation (same two codes as step 3;
   `snapshot-chain-inconsistent` for shape and digest defects).
5. **Structure.** Contiguous 1-based sequence; each record binds its
   predecessor's digest; the first record's digest equals the pinned genesis
   head; the attestation describes exactly this list (head and position).
   Any violation: `snapshot-chain-inconsistent`.
6. **Recency floor.** If `persistedMinimumHead` is configured, the snapshot
   must **contain** the persisted head at its persisted position (prefix
   containment, so a same-length different fork also refuses), else
   `snapshot-older-than-accepted-head`.
7. **Fold and membership.** Fold the series' events to its supported set at
   the snapshot position: `add` inserts an immutable `(version, digest)`
   binding, `retire` removes a current version, `reinstate` restores a retired
   one. A rebinding `add` is `binding-rebound`; any other illegal transition
   (retiring a non-current version, reinstating a non-retired one, re-adding a
   current one) is `snapshot-chain-inconsistent`. A snapshot with no events
   for the series is `series-unknown-at-snapshot` — never-registered is not
   retired (decision D-4). Membership passes; non-membership is
   `not-current-at-snapshot`.

**What the verdict means, exactly.** A failure at step 7 is "this
`(version, digest)` is not in the supported set **at the pinned snapshot's
position**" — one dated assertion by one pinned authority. It is **not**
"this decision was stale when used": a decision legitimately made and acted on
while its version was current, audited after retirement, reads identically to
a genuine stale reuse (the `dem-freshness-*` byte-identity pair exhibits
this). And a pass is **not** "current right now": a retirement above the
snapshot is invisible (`cur-older-snapshot-unpinned`), real-time staleness
needs a notion of *now* that JPS and this ceremony deliberately refuse to
hold, and a single operator holding both the signing key and the history can
show a fresh two-pin verifier either of two contradictory valid histories
(`cur-split-view-*`) — the registered case for transparency-log-style
governance, preserved as a finding.

## 4. The verdict vocabulary (exhaustive)

Layer outcome strings are `pass`, `fail:<code>`, or `unavailable` (the pair
verdict `unavailable`/`currency-unavailable`, definitionally). A harness test
diffs this table against `registry/verify_currency.py`'s declared codes and
the scorer's classification, and constructs a minimal condition for every
code, asserting the exact code and the first-failure ordering.

| Code | Meaning |
|---|---|
| `currency-unavailable` | a required input or out-of-band pin is absent: no authority key, no genesis head, no conforming commitment tuple, or no readable snapshot — fail-closed, never a pass |
| `snapshot-authority-unpinned` | the attestation or a checkpoint is signed under a key that is not the pinned authority |
| `snapshot-signature-invalid` | a signature under the pinned key id does not verify |
| `snapshot-chain-inconsistent` | shape, digest, sequence, predecessor-linkage, genesis, head-attestation, or fold-transition defect — the history is not one authenticated append-only prefix |
| `binding-rebound` | the history rebinds a version to a different digest — refused even under the authority's own valid signature |
| `snapshot-older-than-accepted-head` | the snapshot does not contain the verifier's persisted minimum accepted head at its position |
| `series-unknown-at-snapshot` | the snapshot carries no events for the commitment's series |
| `not-current-at-snapshot` | the `(version, digest)` is not in the series' supported set at the snapshot position — the whole verdict, nothing more |

## 5. What each layer owns (and what none does)

- **OWP** owns everything Study 014 registered: signature validity,
  causal-chain integrity, authorization, policy-predicate arithmetic over
  asserted execution facts, evidence-set exactness, request-replay protection.
- **BINDING / REPLAY** own the judgment commitment and its deterministic
  recomputation, unchanged from Study 014's registered contract.
- **CURRENCY** owns membership of the committed pack version at a pinned
  registry snapshot, and the integrity of the registry artifact itself under
  the two out-of-band pins.
- **Nothing** owns: authorization-contract currency (`cur-authz-rollback-*`:
  an unchanged commitment tuple under a rolled-back work order is accepted —
  the receipt protocol's class, not pack currency's; RFC 0011 R-1);
  cross-view consistency of a single-operator registry (`cur-split-view-*`);
  staleness above the snapshot (`cur-older-snapshot-unpinned`, and the
  freshness pair). Each has a registered cell whose outcome states it.

Ceiling, all four layers, stated once and meant: binding/lineage, not truth —
the registry adds *which version an authority asserted in force at a pinned
point*, and nothing else.
