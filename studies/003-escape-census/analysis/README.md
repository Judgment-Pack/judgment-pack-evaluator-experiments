# Post-hoc analysis — shape sub-classification of the 25 quantification determinations

**This is a secondary, post-hoc analysis. It is not part of the preregistered census.** The
preregistration fixed the device taxonomy (arithmetic, date-time, collection-quantification, …) but
not any sub-structure within a device. This analysis was run after publication, while drafting a
specification RFC for a bounded collection quantifier, to answer a question the census tables
cannot: **of the 25 `collection-quantification` determinations, how many would a bounded
`exists`/`every` condition actually express?**

## Why it exists — a published number was wrong

[`RESULTS.md`](../RESULTS.md) Finding 2 originally estimated "**∃/∀-shaped (~19)**" of the 25, and
RFC 0007 question D repeated it. That estimate came from the classifiers' device notes read at
census speed, not from testing each fact against the semantics a quantifier condition would
actually have. This analysis re-reads each fact at that finer grain. The estimate does not survive:
**3 of 25** are expressible by a bare element-rooted `exists`/`every`, **2 more** by a dedicated
all-elements-equal (`uniform`) operator, and **20 of 25 are not expressible by any bounded
quantifier** — they need joins, counts, ordinal selection, fact-to-fact comparison, or value
emission. The corrections to RESULTS.md and RFC 0007 cite this directory.

## Method

- **Unit:** the 25 facts in [`../measurement/adjudicated.json`](../measurement/adjudicated.json)
  with device `collection-quantification`. For each, the reader consults the producing room's
  `FACTS-LEDGER.md` and `pack.json`.
- **Shape taxonomy (fixed in the classifier brief):** `element-predicate` ·
  `uniformity` · `cross-collection-membership` · `pairwise-cross-list` · `count` ·
  `cardinality-exact` · `other (described)`.
- **Expressibility judgment (strict):** `exists-every` — expressible by a bounded quantifier whose
  inner predicate is a §7 condition tree seeing only the element as document root, comparisons
  against literals only; `uniform` — expressible by an all-elements-equal-at-sub-path operator;
  `neither` — with the specific blocker named.
- **Two independent classifiers**, mutually blind, each blind to the RFC draft and to this
  directory; separate model contexts. Raw outputs preserved unedited:
  [`shapes-classifier-1.json`](shapes-classifier-1.json),
  [`shapes-classifier-2.json`](shapes-classifier-2.json).
- **Adjudication:** [`shapes-adjudicated.json`](shapes-adjudicated.json) records both readings per
  fact, the adjudicated shape, and the rationale for every disagreement.
- **Detailed table:** [`quantifier-shapes.md`](quantifier-shapes.md) renders the 25 rows with
  per-fact blocker codes and the residue mapping (the blocker and residue columns are reader 1's
  assignment, not adjudicated), collapsing `count` and `cardinality-exact` into one
  `count-and-cardinality` bucket.

## Result

| Measure | Value |
| --- | ---: |
| Expressibility agreement between classifiers | **25 / 25** |
| Shape-bucket agreement | 22 / 25 |
| Expressible with bare `exists`/`every` (element-rooted, literal comparisons) | **3** |
| Expressible with a dedicated `uniform` operator | 2 |
| Not expressible by any bounded quantifier | **20** |

The three `exists-every` cases: `A6:/reservation/anySegmentCancelledByAirline`,
`R3:/modification/allNewItemsAvailable`, `R5:/request/allNewItemsAvailable`. The two `uniform`
cases: `A1:/booking/cabinClassUniformAcrossFlights`, `A1:/booking/allPassengersOnSameFlightsAndCabin`
(the latter only if the producer materializes and canonicalizes each passenger's itinerary — a
data-preparation cost the operator does not remove).

Adjudicated shape distribution: element-predicate 3 · uniformity 2 · cross-collection-membership 3 ·
pairwise-cross-list 4 · count 5 · cardinality-exact 1 · other 7. The three shape disagreements
(both A2 `preserves*` facts and A5 `changesPassengerCount`) are shape-bucket boundary calls; none
affects expressibility.

The dominant blockers, counted across the 22 cases not reached by a bare quantifier (a fact may
have several): an element-local predicate being insufficient in the first place, joins to a second
collection, count/cardinality tests, ordinal selection of a distinguished element ("the original
payment method", "the outbound leg"), fact-to-fact comparison (§7 compares a pointer against a
literal only), and constructs that must emit a value rather than test one.

## Honest limits

Two model classifiers with the same instructions are less independent than two human experts; they
may share systematic blind spots. The expressibility judgment embeds one reading of §7's semantics
(element-rooted scope, literal-only comparisons); a differently-scoped quantifier proposal would
move cases between buckets — which is precisely the design information the RFC needs. The
adjudicator wrote the classifier brief; the raw outputs are preserved so the adjudication can be
re-derived or disputed.
