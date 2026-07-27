# RESIDUE — A3 "May the cabin be changed?"

Sentences of the assigned section (**Modify flight → Change cabin**) that `pack.json` does not
carry in full, quoted verbatim, with what was done instead. Five entries, plus two adjacent
sentences from outside the assigned subsection that bear on the decision and were deliberately not
encoded.

---

## 1. The meaning of "flown" is pushed into a computed fact

> "Cabin cannot be changed if any flight in the reservation has already been flown."

**Represented:** the prohibition itself, as exception `refuse-when-a-flight-has-been-flown`
(`force-outcome: deny`, `onUnknown: escalate`).

**Not represented — pushed into a computed fact:** the word *flown*. The pack reads a single Boolean
`/reservation/anyFlightFlown` and has no way to state, check, or version the definition behind it.
The domain vocabulary the records actually carry is `available` / `delayed` / `on time` / `flying`
plus scheduled times; deciding which of those amount to "flown" is an interpretation of the policy
performed before the pack runs (DECISIONS #1, and flagged as policy-interpreting in
`FACTS-LEDGER.md`). Two deployments could disagree about a segment that is airborne right now and
both would validate against this pack.

Also not represented: the quantifier "any flight in the reservation" is collapsed into the same
Boolean. The pack cannot say *which* segment was flown, so a `deny` it produces carries no citable
segment.

---

## 2. The bare permission cannot be stated without a price consequence

> "In other cases, all reservations, including basic economy, can change cabin without changing the
> flights."

**Represented:** "In other cases" as the two `force-outcome` exceptions carving out of the general
permission; "all reservations, including basic economy" as the deliberate *absence* of any condition
reading cabin class anywhere in the pack (DECISIONS #7); "without changing the flights" as the
`applicability` conjunct `/request/changesFlights == false` (DECISIONS #6).

**Approximated:** this sentence grants permission *unconditionally* in the non-carved-out cases, but
the pack has no outcome meaning "permitted" on its own — every allow outcome bundles a money
consequence, because bullets 4 and 5 are the only things the subsection says next. So when
`/pricing/priceDifferenceDirection` is unavailable the pack answers `unresolved` and hands off, even
though the policy plainly permits the change. A pack that separated "may it be changed?" from "what
does it cost?" into two decisions would carry this sentence exactly; a single-decision pack answering
the assigned question cannot.

**Not machine-checkable:** "including basic economy" is encoded only by an omission. Nothing in the
document prevents a later editor from adding a basic-economy gate, and no validator would object.

---

## 3. The uniformity invariant is only enforced indirectly

> "Cabin class must remain the same across all the flights in the same reservation; changing cabin
> for just one flight segment is not possible."

**Represented:** the second clause, as exception `refuse-when-change-does-not-cover-all-segments`.

**Pushed into a computed fact:** the first clause. The pack never reads the requested cabin class or
the per-segment cabin classes at all. It reads one Boolean,
`/request/appliesToAllFlightsInReservation`, and trusts that a request covering every segment
necessarily leaves the cabin uniform. That holds only if the request names *one* target cabin; a
malformed request asking for business on the outbound and economy on the return covers all segments
and would slip past this exception. The invariant is therefore asserted by the fact producer, not
checked by the pack.

---

## 4 and 5. The amount of the difference is not carried

> "If the price after cabin change is higher than the original price, the user is required to pay
> for the difference."

> "If the price after cabin change is lower than the original price, the user is should be refunded
> the difference."

**Represented:** the two conditions and their directions, as rules
`collect-difference-when-new-price-higher` and `refund-difference-when-new-price-lower`, resolving to
outcomes `allow-collect-difference` and `allow-refund-difference`.

**Left out — the quantity.** "The difference" is a monetary amount, and JPS `0.1.0-draft` has no
decimal type marker and no way for an outcome to carry a computed value; §2.2 says exact decimal
quantities outside ordered fact-condition operands "require a future profile or declared extension".
The pack therefore names *what must happen* (collect / refund) but not *how much*, and the ordered
comparison itself is done outside the pack as `/pricing/priceDifferenceDirection` (DECISIONS #10).
The agent must recompute the amount to act on either outcome.

**Left out — silence on equal prices.** Neither bullet covers a cabin change whose new price equals
the original. The pack supplies an outcome for it, `allow-no-money-movement`, reasoning that bullet 2
still grants the permission and neither money clause fires. That outcome is an inference, not a
sentence of the policy (DECISIONS #5).

*(The garbled "the user is should be refunded" is quoted as written; it is read as "the user should
be refunded".)*

---

## Adjacent sentences deliberately not encoded

Not part of the assigned subsection, but they bear directly on a cabin change and their omission is
a choice rather than an oversight (DECISIONS #11).

> "Before taking any actions that update the booking database (booking, modifying flights, editing
> baggage, changing cabin class, or updating passenger information), you must list the action details
> and obtain explicit user confirmation (yes) to proceed." *(global preamble)*

**Left out.** It is an execution gate on the API call, not a condition on whether the change is
permitted, and the pack answers "may the cabin be changed?". Encoding it as required evidence would
make a plainly permitted change come back `unresolved` merely because the user has not yet said yes.

> "If the flights are changed, the user needs to provide a single gift card or credit card for
> payment or refund method. The payment method must already be in user profile for safety reasons."
> *(Modify flight → Payment)*

**Left out — and it exposes a gap in the source policy.** The bullet excludes itself by its own
terms: it fires only "if the **flights** are changed", while this pack applies only when they are
not. Yet `allow-collect-difference` and `allow-refund-difference` both move money. The Change cabin
subsection says nothing about which payment method that money moves through, so the pack says
nothing either rather than importing the flight-change rule by analogy.
