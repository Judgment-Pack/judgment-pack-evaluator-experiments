# The witness sighting — schema, ceremony, and the Layer WITNESS contract

Status: REGISTERED with the Study 017 preregistration (the digest in
`harness/PINS.json` governs after the freeze). This document is the registered
contract of the study's witness prototype: the sighting schema, the witness
configuration, and the ordered comparison ceremony. It prototypes one clause
structure of RFC 0011 Unresolved #9's witness contract at the lowest possible
commitment — **a study registration, not a format proposal**: no protocol, no
transport, no gossip semantics, and no producer or consumer outside this study
is bound by it.

Layer CURRENCY is Study 016's frozen `registry/verify_currency.py`, consumed
as a digest-pinned unmodified upstream and never edited; Layer WITNESS is the
one added step. Vocabulary as in 016: JCS is RFC 8785 (`rfc8785`), digests are
SHA-256, signatures Ed25519, domains OWP-style.

## 1. The sighting and the witness configuration

A **sighting** is a witness key's signature over a history head it has
observed:

```json
{
  "sighting": {"sightingVersion": "1",
               "seriesId": "https://example.com/judgment-packs/witnessed-policy",
               "head": "sha256:<64 lowercase hex>", "position": 2},
  "witnessKeyId": "ed25519:<64 lowercase hex>",
  "signature": "<base64>"
}
```

Signed bytes: `JCS({"domain": "jps-study017-witness/sighting/1", "payload":
<sighting>})`. A cross-verifier exchange is the same primitive: an accepted
head, exchanged, IS a sighting — one mechanism models both the witness and the
gossip variant. Retained sightings travel as
`{"sightingsVersion": "1", "sightings": [ <records> ]}`.

The **witness configuration** is per-series verifier state, separate from the
currency trust configuration (the frozen 016 schema is closed and is not
touched):

```json
{"witnessConfigVersion": "1", "seriesId": "…",
 "witnessKeys": ["<base64 raw Ed25519 public key>", …],
 "minimumSightings": 1}
```

`minimumSightings` is the **enforcement clause** of the witness contract made
explicit: how many valid pinned sightings must exist before the verifier will
call a view witnessed at all. With `0`, an empty comparison is vacuously
consistent — a registered boundary, not a defect.

## 2. The Layer WITNESS ceremony

Ordered, fail-closed, offline; first failure wins; runs after Layer CURRENCY
and records independently. Registered caps: `MAX_SIGHTINGS_BYTES` 65536,
`MAX_SIGHTINGS` 64 (`witness-limits-exceeded` above either).

1. **Pins and inputs.** Well-formed version-1 witness configuration whose
   `seriesId` equals the commitment's `packId`; readable pinned keys; a
   retained sightings artifact — else `witness-unavailable`.
2. **Per-record validation.** Strict duplicate-rejecting parse; closed
   schemas before any signature math. For each record: a sighting verified
   under a pinned key is **valid** (kept if its series matches); a sighting
   whose key id is **unpinned is ignored and counted** (design decision D-3 —
   it is untrusted evidence, not a required input; the
   `neg-unpinned-conflict` control measures the cost, and the asymmetry is
   safe because the label can only cause refusal, never acceptance); a
   sighting claiming a **pinned** witness that fails verification is
   `witness-sighting-invalid` — fail-closed, never silently dropped.
3. **Enforcement.** Fewer valid sightings than `minimumSightings` →
   `witness-unavailable` (never a pass, never a detection).
4. **Comparison — containment per sighting.** The presented snapshot's
   checkpoint digests are recomputed from its bytes (content identity only;
   authority-signature validity is Layer CURRENCY's independent job). For
   each valid sighting, in retained order: position beyond the snapshot's
   end → `snapshot-behind-witnessed-head` (the witness recency floor — the
   sighting doubles as prior-acceptance state across parties); a different
   digest at the sighted position → `snapshot-conflicts-with-witnessed-head`
   (a pinned witness attests a different history). All consistent → pass,
   with the valid/ignored counts recorded in detail.

**What a verdict means, exactly.** A conflict means one pinned witness
attests a different history — *observability, not prevention*: nothing is
stopped, no view is proven the true one, and which of the two histories is
"right" is exactly what a single conflicting pair cannot say. A pass means
*consistency with the retained sightings of the pinned witnesses* — nothing
more: a colluding witness restores silence while satisfying every clause
(`wit-collusion-*`, the registered exhibit); an empty comparison is vacuous
(`wit-partition-vacuous`); a sighting anchors only the prefix it names
(`wit-retention-horizon`). Witnessing states history consistency, never
currency, correctness, or truth.

## 3. The verdict vocabulary (exhaustive)

| Code | Meaning |
|---|---|
| `witness-unavailable` | a required input or pin is absent or malformed, the configuration binds a different series, or fewer valid pinned sightings exist than `minimumSightings` requires — fail-closed, never a pass |
| `witness-sighting-invalid` | a record is malformed, or a sighting claiming a pinned witness does not verify under it — tampered retained evidence refuses rather than dropping |
| `witness-limits-exceeded` | the sightings artifact exceeds a registered cap — refused before unbounded work |
| `snapshot-conflicts-with-witnessed-head` | a pinned witness attests a different head at a position inside the presented history — the split view made observable |
| `snapshot-behind-witnessed-head` | a pinned witness attests a longer history than the presented view — the witness recency floor |

## 4. What each layer owns (and what none does)

- **CURRENCY** (frozen 016, unchanged) owns membership at the pinned snapshot
  and the registry artifact's integrity under the per-series pins.
- **WITNESS** owns consistency of the presented history with the retained
  sightings of the pinned witnesses, and the integrity of the sightings
  artifact itself.
- **Nothing** owns: witness independence (`wit-collusion-*` — the same key
  satisfying the enforcement clause for contradictory views); comparison
  actually happening (`wit-partition-vacuous`); coverage above the sighted
  horizon (`wit-retention-horizon`); and everything 016 registered as
  nothing's. Each has a registered cell whose outcome states it.

Ceiling, both layers, stated once and meant: binding/lineage, not truth —
witnessing adds *which histories the pinned witnesses attest having seen*,
and nothing else.
