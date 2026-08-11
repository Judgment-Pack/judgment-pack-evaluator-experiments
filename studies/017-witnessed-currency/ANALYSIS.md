# Analysis — Study 017 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command
from the freeze commit (`8ab3193`, the squash-merge of PR #57), CPython 3.12.11,
`cryptography` 49.0.0, `rfc8785` 0.1.4, label `REGISTERED`. Fully offline: no evaluator
binary, no external clone. Every pin, the whole-study manifest, the bytecode-cache
bootstrap and the six freeze pins verified before adjudication; holdout
post-adjudication integrity intact across all 63 stamped files. This document is post-run
analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **Locked replication (R1)**: `R1 holds (REGISTERED)` — 18 cells, 18 adjudicated, 13
  endpoint, **0 endpoint-divergent**, 0 pipeline-invalid, all five control gates green,
  and the collusion pair's equivocation structurally validated from retained bytes.
- **Reviewer holdout (first execution)**: **concordant — 9/9 constructed inside the
  attempt, 9/9 adjudicated, 0 divergent**, every registered structured triple
  (`comparisonPerformed`, `validSightings`, `unattributedSightings`) matching as
  registered. All nine cells were authored by the cross-vendor reviewer at review round 2
  and had never been executed by anyone.

## What one attributed record buys

The payoff cell is the point of the study and it landed as registered:
`wit-split-view-caught` presents a fork whose two branches Layer CURRENCY cannot separate
— both keep the committed version in the supported set, so currency passes on either —
and **one attributed record of a sibling head** makes it observable
(`snapshot-conflicts-with-witnessed-head`). Its internal control is
`wit-zero-sightings-vacuous`, whose bytes differ only in the sighting set and which passes
with `comparisonPerformed: false`. That difference is the whole of what a sighting buys,
measured rather than argued.

This is the same **threat class** Study 016 registered as silent to a fresh, stateless
verifier. It is not a replay of 016's cells: different series, no receipt layers, and both
fork branches add rather than retire. No claim of replicating 016's run is made here.

## What it does not buy — the registered boundaries, all confirmed

Seven registered-undetected cells passed exactly as registered, and each isolates a
different clause of the witness contract RFC 0011 Unresolved #9 names:

- **Non-collusion** (`wit-collusion-a`/`-b`): one pinned key recorded contradictory heads
  at the same position across the pair, each run internally valid and satisfying every
  *implemented* clause. The scorer recomputed the contradiction from the retained bytes —
  same key by signature, pinned in both configurations, both meeting their floors, each
  head matching its own presented view, same position, different heads. The mechanism
  implements no non-collusion clause, and these cells are why one may be required. They
  measure no organisational property, and this study claims none.
- **Delivery control** (`wit-suppression-omitted`, `wit-suppression-corrupted`): whoever
  controls which records reach the verifier can drop the conflicting one or alter it so it
  attributes to nobody. Both pass. The corrupted case leaves an
  `unattributedSightings: 1` count and nothing more — a count is not a detection.
  `wit-required-witness-absent` bounds them: naming a witness converts a satisfied count
  into a refusal, but refuses on *absence of evidence* and cannot distinguish suppression
  from outage or from a witness that never observed the series.
- **Comparison actually happening** (`wit-zero-sightings-vacuous`, against
  `-enforced`): an empty retained set is vacuously consistent at `minimumSightings: 0` and
  a fail-closed refusal at `1`. No cause is attributed to the emptiness.
- **Coverage** (`wit-prefix-coverage`): a record constrains only the position it names;
  the divergence above it is invisible.
- **The recency policy's cost** (`wit-historical-audit` against `wit-recency-refused`,
  identical bytes under both policies): a deliberate audit of an older snapshot and a stale
  presentation are the same input, so `refuse-behind` refuses both and `ignore` accepts
  both. Only the configured policy decides; the verifier cannot tell them apart.

`cur-retired-interplay` closes the layer boundary: a witnessed, consistent view can still
carry a version outside the supported set — witnessing states history consistency, never
currency, and neither states usability, which RFC 0011 §2a places outside both.

## What the holdout's first execution established

The holdout is the study's only prospective evidence, and it is the reviewer's:

- `h01` (key-id labels swapped between two honest records): both still attributed, both
  required witnesses present, `pass` — the association is by signature, and the descriptive
  label moves nothing. This is the round-1 defect's inverse, registered by the reviewer
  before the fix was confirmed.
- `h02` (a valid record from an unpinned key relabelled with a required witness's key id):
  `witness-required-absent`, with `validSightings: 1, unattributedSightings: 1` — the
  relabel neither admits the record nor satisfies the floor it names.
- `h03`/`h04` (floor interactions): a count floor above the attributed evidence is
  `unavailable`; a satisfied count with a required witness absent is
  `witness-required-absent` — the two clauses are independent and ordered as registered.
- `h05`/`h06` (identical bytes, both recency policies): `pass` under `ignore`,
  `snapshot-behind-witnessed-head` under `refuse-behind`.
- `h07` (a beyond-end record and a conflicting in-range record, retained in that order,
  under `refuse-behind`): the conflict wins — the registered precedence holds against the
  unsigned retained order.
- `h08` (an authority signature altered in the snapshot): `currency` fails,
  `witness` passes — the layers fail independently, exactly as their contracts say.
- `h09` (a pinned witness's record for a *foreign* series, floors zero and empty): `pass`
  with `comparisonPerformed: false, validSightings: 0` — the mirror image of the round-2
  blocker, where the same construction under a named floor must refuse. Both directions
  are now pinned by a cell the maintainer did not author.

## Claims and non-claims

Within the registered cells, a minimal sighting-comparison step — one witness key's
signature over an observed registry head, consumed as one added layer over Study 016's
frozen verifier — made a registered split view observable from a single attributed record,
and failed exactly where the registered contract clause was absent: under a witness
signing per audience, under control of delivery, without a comparison, above the position
a record names, and between a stale presentation and a deliberate historical audit.

Non-claims, unchanged from the preregistration (§9): **no interoperability claim of any
kind** — nothing here is independently developed, and this study may never be cited as
evidence that witnessing works between real parties. No claim about witness independence
as an organisational property. No prevention: observability at best, conditional on every
clause of a contract this study names and only partially instantiates. No transport,
discovery, retention-policy or incentive claims. No real-time anything; no policy or fact
truth; everything Study 016 registered as nothing's remains nothing's. Trust roots,
enumerated: the study-minted authority and witness keys, the pinned Study 016 modules,
this study's witness code, the registered dependencies (whose *contents* are not
digest-pinned), and the retained artifact store. Binding/lineage, not truth — witnessing
adds *which histories the pinned witnesses recorded having seen*, and nothing else.
