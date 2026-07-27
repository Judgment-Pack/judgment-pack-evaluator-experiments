# Residue — sentences of "## Book flight" not represented in `pack.json`

Scope: the assigned section only (`reference/policy.md` lines 63–101). Each sentence of the section
is accounted for below; the ones that made it into the pack unchanged are not repeated here.

## 1. Ordering of the intake steps

> "The agent must first obtain the user id from the user."

> "The agent should then ask for the trip type, origin, destination."

**Approximated.** The *obligations* survive as the required evidence requirements `user-id` and
`trip-parameters`, so a booking cannot resolve to `book-allowed` while either is absent. The
*ordering* ("first", "then") is lost: JPS 0.1.0-draft has no sequencing construct, rules carry no
priority (§6.5: "array order carries no priority meaning"), and an evidence requirement records only
presence. A pack that saw the user id supplied after the trip parameters cannot tell the difference.

## 2. Which passenger attributes were collected

> "The agent needs to collect the first name, last name, and date of birth for each passenger."

**Pushed into one evidence requirement.** `passenger-details` (required, kind `fact`) asserts that
the three attributes were collected for every passenger. The pack cannot check the three fields
separately, cannot check them per passenger, and cannot check that a date of birth is well-formed;
whoever answers the evidence manifest is making that judgment.

## 3. Non-refundability of a travel certificate remainder

> "The remaining amount of a travel certificate is not refundable."

**Left out.** This states how leftover value on a certificate is treated afterwards. It is not a
condition on whether the booking may be made, so no rule reads it. A pack answering a refund
question would need it. (An arguable alternative was a required "user was told the remainder is not
refundable" attestation; the section does not say the agent must disclose it, so inventing that
obligation was rejected.)

## 4. The free-bag table as a *derivation*

> "If the booking user is a regular member: 0 free checked bag for each basic economy passenger …"
> (and the eight further membership × cabin lines through "4 free checked bags for each business
> passenger")

**Represented, but inverted.** All nine combinations are encoded literally in
`deny-free-checked-bag-allowance-mismatch`, so nothing is lost from the table itself. What is lost
is direction: the format lets the pack *check* a proposed allowance, not *emit* one. The pack cannot
tell an agent "grant 3 free bags"; it can only reject a draft reservation whose
`/booking/baggage/freeCheckedBagsPerPassenger` disagrees with the table. The per-passenger scaling
("for each … passenger") is also only partly represented: the pack checks the per-passenger figure
and leaves the multiplication by passenger count inside the computed `extraCheckedBags`.

## 5. "Do not add checked bags that the user does not need."

**Pushed into a computed fact.** `/booking/baggage/onlyBagsUserRequested`. The sentence supplies no
test for "need", so the fact carries a judgment that the pack itself cannot make; flagged as such in
FACTS-LEDGER.md.

## 6. Cost statements read as booking terms, with their consequences dropped

> "Each extra baggage is 50 dollars."

> "The travel insurance is 30 dollars per passenger and enables full refund if the user needs to
> cancel the flight given health or weather reasons."

**Partly encoded.** The prices became deny rules (`deny-extra-baggage-fee-not-fifty`,
`deny-travel-insurance-price-not-thirty`), so a draft reservation priced differently is denied. The
clause "and enables full refund if the user needs to cancel the flight given health or weather
reasons" is **left out**: it describes a future cancellation entitlement, not a condition on making
this booking, and belongs to the Cancel flight decision. Neither the total collected nor the
existence of a charge is checked — only the unit prices.

## 7. "The agent should ask if the user wants to buy the travel insurance."

**Handled as required evidence**, `travel-insurance-offer` (kind `attestation`). Absence produces
`unresolved / missing-required-evidence` rather than a denial. This upgrades a "should" into a hard
precondition; see DECISIONS.md #5.

## Sentences of the section carried without loss

- "Cabin class must be the same across all the flights in a reservation." → `deny-cabin-class-not-uniform`
- "Each reservation can have at most five passengers." → `deny-more-than-five-passengers`
- "All passengers must fly the same flights in the same cabin." → `deny-passengers-not-on-same-flights-and-cabin`
- "Each reservation can use at most one travel certificate, at most one credit card, and at most three gift cards." → three deny rules
- "All payment methods must already be in user profile for safety reasons." → `deny-payment-method-not-in-user-profile`

(Each of these depends on a computed fact standing in for the underlying comparison; the encoding of
the *rule* is exact, the *inputs* are pre-chewed. See FACTS-LEDGER.md.)

**Residue count: 7 items** (2 left out entirely, 3 approximated/inverted, 2 pushed into a computed
fact or an evidence attestation).
