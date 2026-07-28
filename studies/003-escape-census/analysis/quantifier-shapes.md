# Quantifier shapes — a post-hoc sub-classification of the 25 collection-quantification facts

**Status: unregistered re-analysis. Read the method note before reading the table.**

## Method, stated plainly

This file is the detailed per-fact table of a **post-hoc re-analysis** of `adjudicated.json`,
produced while drafting
[RFC 0008](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0008-bounded-collection-quantifiers.md).
It is:

- **not** preregistered — `PREREGISTRATION.md` registers no sub-classification of the device
  buckets; the deviation is recorded in `DEVIATIONS.md`;
- **adjudicated at a second pass**: two separate blinded model runs under author-written briefs
  ([`briefs.md`](briefs.md)), mutually blind and barred from any RFC draft text, classified all 25
  facts; their raw outputs are preserved unedited in
  [`shapes-classifier-1.json`](shapes-classifier-1.json) and
  [`shapes-classifier-2.json`](shapes-classifier-2.json), and the adjudication of every
  disagreement is in [`shapes-adjudicated.json`](shapes-adjudicated.json). Expressibility
  agreement was **25/25**; shape-bucket agreement 22/25. The shape column below is the
  **adjudicated** reading;
- still **not census-grade**: the taxonomy and both reader briefs were written by the RFC author
  after the census closed, and two model readers under one brief are less independent than two
  human experts. See [`README.md`](README.md) for the full method note.

The **blocker codes** and the **residue mapping** below are shape reader 1's multi-label
assignment, not adjudicated; reader 2's per-fact blocker notes (in the raw JSON) do not contradict
their direction. A terminology guard: the census's "classifiers" classified the *device* axis; this
analysis's "readers" classified the *shape* axis within one device bucket. They are different
passes by different agents.

**Inputs.** The 25 facts in [`../measurement/adjudicated.json`](../measurement/adjudicated.json) whose adjudicated `device` is
`collection-quantification`, across the 11 rooms producing at least one (A4 produced none). No fact
was added, removed, or re-deviced.

**Inter-rater caveat that bears directly on the denominator.** The census reports **0** fact-class
disagreements across 84 facts, but also **8 device disagreements** and **17 residue-set
differences** — and the *device* axis is the one this table sub-divides. Four of the 25 entered the
`collection-quantification` bucket only by adjudication, each flagged `judgment-call: true`:
`A5:/derived/changesPassengerCount` (C1: `arithmetic`), and `R1:/order/originalPaymentMethod/type`,
`R2:/request/newPaymentMethodDiffersFromOriginal`, `R4:/refund/destinationIsOriginalPaymentMethod`
(C1: `precedence-ordering`). Under census classifier 1's reading the bucket is **21, not 25** —
and the four contested facts are, under this analysis's adjudicated shapes, four of the seven
`other` rows.

## Shape definitions

| Shape | Definition |
| --- | --- |
| `element-predicate` | The test is a predicate over one element's own fields against authoring-time literals, AND-ed or OR-ed across the array. |
| `uniformity` | All elements must agree at a sub-path. The comparison target is a runtime value (another element), not a literal. |
| `cross-collection-membership` | Each element must be tested against a *second* runtime collection. |
| `pairwise-cross-list` | Elements of two runtime lists must be paired and the members of each pair compared with each other. |
| `count-and-cardinality` | The determination is a size of a (possibly filtered) collection, compared with a literal bound (`≤ 1 travel certificate`, `exactly one payment method`). |
| `other` | Neither a per-element predicate nor a literal-bounded size: an element *selected* by position or recency, a distinguished element compared across two lists, two sizes compared with each other, or the whole list classified into a value. |

## Blocker codes

| Code | Blocker |
| --- | --- |
| **A** | Element-local predicate insufficient — even given the array, the per-element test names something outside the element. |
| **B** | Join to a second collection. |
| **C** | Count or cardinality. |
| **D** | Ordinal selection — an element identified by position, recency, or "the original". |
| **E** | Intra-element field-vs-field comparison. |
| **F** | Whole-list classification emitting a value rather than a boolean. |

A fact may carry several. A fact reached by the proposed operators carries none.

## The 25

| # | Room : pointer | Shape | Blocked by | Reached by |
| ---: | --- | --- | --- | --- |
| 1 | `A1:/booking/cabinClassUniformAcrossFlights` | uniformity | A | `uniform` only |
| 2 | `A1:/booking/passengerCount` | count-and-cardinality | C | neither |
| 3 | `A1:/booking/allPassengersOnSameFlightsAndCabin` | uniformity | A | `uniform` only (weak — see note) |
| 4 | `A1:/booking/payment/travelCertificateCount` | count-and-cardinality | C | neither |
| 5 | `A1:/booking/payment/creditCardCount` | count-and-cardinality | C | neither |
| 6 | `A1:/booking/payment/giftCardCount` | count-and-cardinality | C | neither |
| 7 | `A1:/booking/payment/allMethodsInUserProfile` | cross-collection-membership | A, B | neither |
| 8 | `A2:/request/preservesOrigin` | other† | A, B, D | neither |
| 9 | `A2:/request/preservesDestination` | other† | A, B, D | neither |
| 10 | `A2:/request/preservesTripType` | other | A, F | neither |
| 11 | `A3:/request/appliesToAllFlightsInReservation` | cross-collection-membership | A, B | neither |
| 12 | `A5:/derived/changesPassengerCount` | other† | C | neither |
| 13 | `A6:/reservation/anySegmentCancelledByAirline` | **element-predicate** | — | bare `exists` |
| 14 | `A7:/reservation/passengerCount` | count-and-cardinality | C | neither |
| 15 | `R1:/order/originalPaymentMethod/type` | other | D, F | neither |
| 16 | `R2:/request/newPaymentMethodCount` | count-and-cardinality | C | neither |
| 17 | `R2:/request/newPaymentMethodDiffersFromOriginal` | other | D | neither |
| 18 | `R3:/modification/allNewItemsSameProduct` | pairwise-cross-list | A, B, E | neither |
| 19 | `R3:/modification/allNewItemsDifferentOption` | pairwise-cross-list | A, B, E | neither |
| 20 | `R3:/modification/allNewItemsAvailable` | **element-predicate** | — | bare `every` |
| 21 | `R4:/refund/destinationIsOriginalPaymentMethod` | other | D | neither |
| 22 | `R4:/refund/destinationIsExistingGiftCard` | cross-collection-membership | A, B | neither |
| 23 | `R5:/request/allExchangesWithinSameProduct` | pairwise-cross-list | A, B, E | neither |
| 24 | `R5:/request/allNewItemsAvailable` | **element-predicate** | — | bare `every` |
| 25 | `R5:/request/allNewItemsDifferentOption` | pairwise-cross-list | A, B, E | neither |

## Totals

| Shape | n |
| --- | ---: |
| element-predicate | 3 |
| uniformity | 2 |
| cross-collection-membership | 3 |
| pairwise-cross-list | 4 |
| count-and-cardinality | 6 |
| other | 7 |
| **total** | **25** |

Accounting identity: 3 + 2 + 3 + 4 + 6 + 7 = 25.

† Adjudicated rows — the two readers split on the shape bucket (never on expressibility); the
rationale for each is in [`shapes-adjudicated.json`](shapes-adjudicated.json). Rows 8 and 9 select
a *distinguished* element from each of two lists rather than iterating pairs; row 12 compares two
cardinalities with each other rather than against a literal bound.

Blocker tally across the 22 unreached facts, per shape reader 1's multi-label assignment (a fact
may carry several): **A 12, B 9, C 7, D 5, E 4, F 2.**

## Notes on individual rows

- **3 — `allPassengersOnSameFlightsAndCabin`** is the weakest `uniform` fit: the compared sub-value
  is a derived per-passenger itinerary that no stored field holds, so the operator helps only if the
  producer materialises it first and the comparison is deep JSON equality.
- **12 — `changesPassengerCount`** was the swing case for the count tally: shape reader 1 filed
  it with the counts (which would make 7); adjudication kept it in `other` because the comparison
  is size-against-size, not size-against-literal-bound. `RESULTS.md`'s "count-shaped (6)"
  therefore **stands as published**, in both count and composition. The fact is also one of the
  census's four device judgment calls above, so its very presence in the 25 is contested.
- **14 — `A7:/reservation/passengerCount`** is arguably mis-attributed to this device by the census.
  The A7 pack never quantifies over the passenger list; its only condition on the pointer is
  `not-equals null`, and the real loss there is value-carrying arithmetic.
- **13 — `A6:/reservation/anySegmentCancelledByAirline`** quantifies over per-segment records the
  reservation already carries ("Mechanical aggregation of per-segment records",
  `../rooms/A6/FACTS-LEDGER.md`). The ledger does note that airline-initiated cancellation is not one
  of the four per-date flight statuses in Domain Basic, so a real deployment reads it from whatever
  record carries it — but nothing must be *computed* onto the elements.
- **20, 24 — `allNewItemsAvailable`** need the producer to attach catalog availability onto each
  requested item before the array is handed over. That is data shaping, not condition language.

## What is *not* in this table

Two facts commonly assumed to be here are not, because their adjudicated device is
`state-sequencing`, not `collection-quantification`:

- `A6:/reservation/anySegmentFlown`
- `A3:/reservation/anyFlightFlown`

These are the facts behind the policy sentence *"If any portion of the flight has already been
flown, the agent cannot help and transfer is needed"* — RFC 0007's E6 sentence. Their adjudication
notes list existential quantification over segments as a **secondary** device, behind mapping the
status lifecycle (`available` / `delayed` / `on time` / `flying`) plus scheduled times onto the
policy word "flown". A bounded quantifier does not reach them.

## Residues bearing on a quantifier

Five residue entries across the 55 bear on this device. Their mapping to the shapes above:

| Room | Residue sentence | Adjudicated device | Shape | Reached by |
| --- | --- | --- | --- | --- |
| A1 | "collect the first name, last name, and date of birth for each passenger" | collection-quantification | per-element *evidence* check | neither — `evidence-present` reads no facts document and is element-invariant |
| A3 | "Cabin cannot be changed if any flight … has already been flown" | state-sequencing | outside the 25 | neither — lifecycle mapping plus date-time first |
| A3 | "Cabin class must remain the same across all the flights …" | collection-quantification | uniformity | `uniform` only, and only if the pack is also given the per-segment cabins it never reads today |
| R3 | "each item can be modified to an available new item of the same product but of different product option" | collection-quantification | 1 element-predicate + 2 pairwise-cross-list | **partly** — the availability conjunct only |
| R5 | "each item can be exchanged to an available new item of the same product but of different product option" | collection-quantification | 1 element-predicate + 2 pairwise-cross-list | **partly** — the availability conjunct only |

**Recount: 0 of the 5 are fully reached.** (Reader 1's raw JSON records 3 fully / 2 partly
prevented and 1 hit outside the 25; the recount here supersedes those three totals, not the
per-residue mapping.) Two (R3, R5) are partly reached by the bare quantifier —
one conjunct of three each. One (A3 uniformity) is partly reached by the optional `uniform`. Two
(A1, A3-flown) are not reached at all. Three of the five (A1, both A3 entries) correspond to no
fact inside the 25. Three name the missing device explicitly in the room residue files (A3 §1,
R3 §5, R5 §3).
