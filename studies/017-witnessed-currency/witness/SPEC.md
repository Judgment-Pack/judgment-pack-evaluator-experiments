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
 "minimumSightings": 1,
 "requiredWitnesses": ["<base64 raw Ed25519 public key>", …],
 "recencyPolicy": "ignore" | "refuse-behind"}
```

`minimumSightings` **counts** and `requiredWitnesses` **names**: the first is the
enforcement clause as a floor on how much attributed evidence must exist, the
second a floor on *whose*. With `minimumSightings: 0` an empty comparison is
vacuously consistent — a registered boundary, not a defect, and the structured
`comparisonPerformed` field is what says so. `recencyPolicy` decides whether a
sighting beyond the presented history's end refuses; it is explicit configured
policy, never an implicit promotion of any sighting to prior-acceptance state
(round-1 R1-10), and Study 016 applies its analogous refusal only under an
explicitly provisioned `minimumHeadPin`.

## 2. The Layer WITNESS ceremony

Ordered, fail-closed, offline; runs after Layer CURRENCY and records
independently. Registered caps: `MAX_SIGHTINGS_BYTES` 65536, `MAX_SIGHTINGS` 64.

1. **Pins and inputs.** Every input is type-checked before use; a well-formed
   version-1 witness configuration whose `seriesId` equals the commitment's
   `packId`, readable pinned keys, and a retained sightings artifact — else
   `witness-unavailable`.
2. **Schema, then attribution BY VERIFICATION.** Each record is checked against
   the closed schema first; a defect is `witness-sighting-invalid`, fail-closed,
   before any signature math. Each surviving record is then verified against
   **every pinned key in turn**: one that verifies is *attributed* to that key
   and enters the comparison; one that verifies under none is *unattributed* —
   counted, reported, never a comparison input and never a refusal. The record's
   own `witnessKeyId` is descriptive and routes nothing. (The draft routed on
   that unauthenticated label; the round-1 reviewer showed a relabelled honest
   record was thereby ignored and a detected conflict became a pass — R1-4,
   preserved as the standing control `neg-relabel-attack`.)
3. **Enforcement.** Fewer attributed sightings for the series than
   `minimumSightings` → `witness-unavailable`. A key named in
   `requiredWitnesses` with no verifying record → `witness-required-absent`.
4. **Comparison.** With zero attributed sightings the layer returns `pass` with
   `comparisonPerformed: false` — nothing was compared, and the structured field
   is what carries that, not the verdict and not free text (round-1 R1-9).
   Otherwise the presented snapshot's checkpoint digests are recomputed from its
   bytes (content identity only; authority-signature validity is Layer
   CURRENCY's independent job) and **every** attributed sighting is examined —
   never a first-hit scan, so the unsigned retained order cannot decide the
   outcome (round-1 R1-11). A registered precedence then selects the code:
   `snapshot-conflicts-with-witnessed-head` (a different digest at a position
   inside the presented history) outranks `snapshot-behind-witnessed-head` (a
   position beyond its end, reported only under `recencyPolicy: refuse-behind`).

**What a verdict means, exactly.** A conflict means one pinned witness recorded a
different history — *observability, not prevention*: nothing is stopped, neither
view is proven the true one, and which is "right" is precisely what a single
conflicting pair cannot say. A pass means *consistency with the attributed
records that reached this verifier* — nothing more.

**What suppression costs, stated plainly.** Whoever controls which records reach
the verifier can drop the conflicting one, alter its signature so it attributes
to nobody, or re-sign its payload under a fresh key. All three yield a pass; the
first leaves no trace at all and the second leaves only an `unattributedSightings`
count, which is not a detection. `requiredWitnesses` converts a specific
witness's absence into a refusal, but refuses on *absence of evidence* and cannot
distinguish suppression from outage or from a witness that never observed the
series. A corrupted record from a pinned witness and a genuine record from an
unpinned one are indistinguishable here, which is why no fail-closed rule can be
built on the label claiming whose record it is.

## 3. The verdict vocabulary (exhaustive)

| Code | Meaning |
|---|---|
| `witness-unavailable` | a required input or pin is absent or malformed, the configuration binds a different series, or fewer attributed sightings exist than `minimumSightings` requires — fail-closed, never a pass |
| `witness-sighting-invalid` | a record violates the closed schema — the only path to this code; a record that merely fails to verify is unattributed, not invalid |
| `witness-required-absent` | a key named in `requiredWitnesses` contributed no verifying record — a refusal on absence of evidence, which cannot say why |
| `witness-limits-exceeded` | the sightings artifact exceeds a registered cap — refused before unbounded work |
| `snapshot-conflicts-with-witnessed-head` | a pinned witness attests a different head at a position inside the presented history — the split view made observable |
| `snapshot-behind-witnessed-head` | an attributed witness records a position beyond the presented history's end, under `recencyPolicy: refuse-behind` only — and a deliberate audit of an older snapshot refuses identically |

## 4. What each layer owns (and what none does)

- **CURRENCY** (frozen 016, unchanged) owns membership at the pinned snapshot
  and the registry artifact's integrity under the per-series pins.
- **WITNESS** owns consistency of the presented history with the retained
  sightings of the pinned witnesses, and the integrity of the sightings
  artifact itself.
- **Nothing** owns: non-collusion (`wit-collusion-*` — the same key satisfying
  every implemented clause for contradictory views); delivery
  (`wit-suppression-omitted`, `wit-suppression-corrupted`); whether a comparison
  happened at all beyond what `comparisonPerformed` reports
  (`wit-zero-sightings-vacuous`); coverage above the position a record names
  (`wit-prefix-coverage`); the difference between a stale presentation and a
  deliberate historical audit (`wit-recency-refused` / `wit-historical-audit`);
  and everything Study 016 registered as nothing's. Each has a registered cell
  whose outcome states it.

Ceiling, both layers, stated once and meant: binding/lineage, not truth —
witnessing adds *which histories the pinned witnesses attest having seen*,
and nothing else.
