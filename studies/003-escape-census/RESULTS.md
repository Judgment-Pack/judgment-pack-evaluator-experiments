# Study 003 results — the escape census

Computed from [`measurement/adjudicated.json`](measurement/adjudicated.json) exactly as
preregistered. Encoders were hypothesis-blind (neutral briefs, isolated rooms); classification was a
separate pass by two independent classifiers with adjudication. All 12 packs validate at exit 0.

## The preregistered numbers

| Metric | Value |
| --- | --- |
| **D1 (primary): decisions with ≥ 1 prepared determination** | **12 / 12 = 100%** |
| D2: prepared determinations ÷ all prepared facts | 40 / 58 = 69% |
| D2′: prepared determinations ÷ all facts read | 40 / 84 = 48% |
| D3: residue sentences (could not be represented) | 55 |
| Inter-rater: fact-class disagreements | **0** |
| Inter-rater: device disagreements / residue-set differences | 8 / 17 |

Per decision:

| Room | Facts read | Prepared | Determinations | Residues |
| --- | ---: | ---: | ---: | ---: |
| A1 book flight | 16 | 13 | 9 | 9 |
| A2 change flights | 5 | 4 | 3 | 2 |
| A3 change cabin | 5 | 3 | 3 | 5 |
| A4 baggage/insurance | 4 | 2 | 2 | 2 |
| A5 change passengers | 3 | 1 | 1 | 1 |
| A6 cancel flight | 6 | 6 | 4 | 6 |
| A7 refunds/compensation | 9 | 7 | 4 | 5 |
| R1 cancel pending order | 6 | 2 | 1 | 2 |
| R2 modify payment | 6 | 5 | 3 | 5 |
| R3 modify items | 8 | 6 | 4 | 9 |
| R4 return order | 8 | 3 | 2 | 2 |
| R5 exchange order | 8 | 6 | 4 | 7 |

## Finding 1 — the escape is universal in this frame, because inputs are collections

**Every one of the 12 decisions required at least one prepared determination.** The registered
predictor's escape-free clause ("decisions whose conditions are entirely scalar-fact comparisons
encode with zero prepared determinations") was not so much falsified as **vacuous: no such decision
exists in either policy.** Real requests arrive as collections — passengers, payment methods, flight
segments, order items — and the moment a policy says *all*, *any*, *each*, or *how many* about one
of them, the conclusion must be prepared outside the pack.

## Finding 2 — one device dominates: quantification, 25 of 40

| Device forcing the determination | Count |
| --- | ---: |
| **collection-quantification** | **25 (63%)** |
| arithmetic | 6 |
| materiality | 4 |
| state-sequencing | 4 |
| date-time | 1 |

The registered device-family prediction (arithmetic + date-time + quantification) covered 32/40 =
80% — directionally right, but with the **wrong lead**: Study 001 made arithmetic look like the
main culprit; at census scale it is a minor player and quantification is the phenomenon.

Within the 25, the constructs are not uniform, and this matters for any remedy:

- **∃/∀-shaped (~19):** "any segment cancelled by the airline", "all items available", "all
  passengers on the same flights", "all exchanges within the same product", uniformity tests. A
  bounded existential/universal condition over an array-valued pointer would express these.
- **Count-shaped (6):** "at most one travel certificate / three gift cards", passenger counts,
  "exactly one payment method". These need `count(filter(...))` compared to a limit — meaningfully
  more language than a quantifier, and a real step toward the query-language non-goal.

> **Amendment, 2026-07-27 — the "~19" estimate is withdrawn.** That figure was estimated from shape
> names, not from a per-fact reading. A later per-fact re-analysis of the same 25 facts
> ([`analysis/`](analysis/): two separate blinded model runs, adjudicated; expressibility
> agreement 25/25) finds that a bounded ∃/∀ condition over an array-valued pointer expresses
> **3**, and **5** with an additional all-equal-at-a-sub-path operator. The remaining 20 need
> joins, counts, ordinal selection, fact-to-fact comparison, or whole-list classification. The
> **count-shaped (6)** figure above stands, in count and composition. The re-analysis is post-hoc
> and unregistered — recorded in `DEVIATIONS.md`, not census-grade — and the proposal it informs is
> [RFC 0008](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0008-bounded-collection-quantifiers.md).

## Finding 3 — the A6 replication: measurement method changes the count

A6 blind-re-encoded Study 002's exact decision ("may this reservation be cancelled?"). Study 002's
single-author self-report found **1** prepared determination; the census's blind encoder plus
two-classifier adjudication found **4** (status-lifecycle mapping → `anySegmentFlown`, the
hours-since-booking date-time computation, the any-segment-cancelled quantification, and the
insurance-coverage materiality judgment).

Same decision, same policy text, same format. The difference is measurement: a single author
classifying their own ledger under-counts against independent adjudicated classification. **Study
002's headline ("1 determination") should be read as a floor, and cross-study comparisons of
absolute counts should be treated with caution.** The inter-rater data here supports the boundary
itself: the two independent classifiers had **zero** fact-class disagreements across all 84 facts.

## Finding 4 — the residues name gap families the taxonomy didn't

55 sentences could not be represented. `state-sequencing` (21) is the largest bucket but the least
alarming: most are agent-procedure obligations ("first obtain the user id, then…") that a decision
format arguably should not hold. The **`other` bucket (19)** is where the open category earned its
place — recurring families, several matching RFC 0007's previously *unevidenced* candidate areas:

- **Deontic gradation** — "should" vs "must" both become hard preconditions; the format has one
  strength of obligation.
- **Forward entitlements / cross-decision references** — "insurance enables full refund if…"
  belongs to the Cancel decision; there is no way for one pack to reference another's outcome.
- **Derivation vs check** — the baggage-allowance table can be encoded to *reject* a stated
  allowance but cannot *state* one; the format checks values, it never emits them.
- **Terminality** — "even a human agent cannot modify the number of passengers": no way to say
  an outcome is final and not escalatable.
- **Speech-act duties** — "remind the customer…": the pack can require an attestation of the
  answer, not the performance of the reminder.

## What this licenses, and what it does not

- **For the expansion question:** the evidence is now concentrated. Collection quantification is
  the single largest cause of determination escape (25 of 40). ~~A bounded ∃/∀ condition over
  array-valued facts addresses (~19 of 40) with no arithmetic implied.~~ **Amended 2026-07-27:** a
  per-fact re-analysis ([`analysis/`](analysis/) — two separate blinded model runs, adjudicated,
  unregistered) puts the bounded quantifier's reach at **3 of the 25**,
  or 5 with an all-equal operator — so *the size of the cause is not the size of the remedy*.
  Whether that is enough to license the addition is now
  [RFC 0008](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0008-bounded-collection-quantifiers.md)'s
  own open question. The count-shaped constructs should still be *named and deferred* — they are
  the slippery slope the non-goals warn about. Everything else stays a preparation-layer concern.
- **Rates are frame-relative.** 12 decisions from two policies by one benchmark team. The 100% D1
  says "collections are everywhere in this corpus", not "in all policy".
- **No efficacy claim**, as ever: this measures what the format can hold, not whether packs help.

## Reproducing

Rooms (packs, ledgers, residues, decision logs): [`rooms/`](rooms/). Raw classifier outputs and the
adjudication with per-disagreement notes: [`measurement/`](measurement/). Every pack:
`judgment-pack spec validate rooms/<id>/pack.json` → exit 0.
