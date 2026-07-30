# Residue — a3 (change cabin) × a7 (refunds and compensation)

`relationships.graph.json` declares both decisions and **no edges**. This file records why, and
records verbatim every policy sentence I found that relates the two decisions but that I could not
represent as a declared relationship.

## The two decisions, and the only coupling the format offers

- **a3** — "May the cabin be changed for this reservation, and if so is the price difference
  collected from or refunded to the user?" Applies only when `/request/type` is `change-cabin` and
  `/request/changesFlights` is `false`. Outcome ids: `deny`, `allow-collect-difference`,
  `allow-refund-difference`, `allow-no-money-movement`.
- **a7** — "Is the user owed a refund or compensation, and what kind?" Outcome ids:
  `no-compensation`, `certificate-cancelled-flight`, `certificate-delayed-flight`. Its own
  description states it "never asserts a refund".

A graph edge can carry exactly two things: the upstream **outcome id, verbatim as a string**, written
at a JSON Pointer in the downstream facts document; and **evidence availability** — `present` for any
upstream outcome, `unknown`/`absent` otherwise. Both forms are *outcome-agnostic*: they fire the same
way for `deny` as for `allow-refund-difference`.

Checked exhaustively in both directions:

- a3's five fact paths (`/request/type`, `/request/changesFlights`,
  `/request/appliesToAllFlightsInReservation`, `/reservation/anyFlightFlown`,
  `/pricing/priceDifferenceDirection`) and its two required evidence requirements (`user-id`,
  `reservation-id`) admit **none** of a7's three outcome ids as a meaningful value. a7 → a3 is also
  the wrong direction for every sentence below.
- a7's nine fact paths admit **none** of a3's four outcome ids as a meaningful value: every one of
  them tests a boolean, a membership level, a cabin class, or a passenger count.

So no honest edge exists, in either direction. Everything below is residue.

---

## R1. The delayed-flight certificate is ordered after a change to the reservation

**Verbatim (Refunds and Compensation, line 165):**

> If the user complains about delayed flights in a reservation and wants to change or cancel the
> reservation, the agent can offer a certificate as a gesture after confirming the facts and changing
> or cancelling the reservation, with the amount being $50 times the number of passengers.

This is the one sentence that puts a change to a reservation and the compensation decision inside a
single conditional, and a3 decides one species of change to a reservation. a7 encodes the ordering as
the fact `/reservation/changeOrCancelCompleted == true`, a precondition of
`grant-delayed-flight-certificate`.

**What I did instead: declared no edge, for three reasons.**

1. *Permission is not completion.* a3 answers whether the cabin **may** be changed and what money
   moves; the sentence requires that the change **has been carried out**. The policy itself puts a
   step between them that neither pack decides — "Before taking any actions that update the booking
   database (booking, modifying flights, editing baggage, changing cabin class, or updating passenger
   information), you must list the action details and obtain explicit user confirmation (yes) to
   proceed." An edge from a3's outcome to `changeOrCancelCompleted` would assert that the
   confirmation and the API call happened because the permission question resolved.
2. *The edge cannot tell `allow` from `deny`.* A fact edge writes whichever outcome id a3 produced,
   `deny` included, and an evidence edge reports `present` for any outcome at all. The sentence is
   conditional on the change actually having been made, and no edge can express that condition.
3. *Wired anyway, it inverts the sentence.* I built the edge
   (`a3 → a7`, fact `/reservation/changeOrCancelCompleted`) and it passes
   `experimental graph validate`. Evaluated, a3 resolving to `allow-refund-difference` injects the
   **string** `"allow-refund-difference"` where the rule tests `equals true`; the grant rule goes
   false and `deny-other-reason` fires, so the composite headline is `no-compensation` — precisely
   the opposite of what the sentence directs for a delayed-flight complaint whose change went
   through. A validating edge that reverses the sentence is worse than no edge.

The fact stays a caller input: whoever runs the graph supplies
`/reservation/changeOrCancelCompleted` for the a7 node after the change is actually executed.

## R2. The cabin-change refund falls inside a7's question but outside a7's document

**Verbatim (Modify flight > Change cabin, line 120; the grammatical slip is the policy's):**

> If the price after cabin change is lower than the original price, the user is should be refunded
> the difference.

a7's decision question is "Is the user owed a refund or compensation, and what kind?" This sentence
states a refund the user is owed — so it answers half of a7's question — yet it is encoded wholly in
a3, as the outcome `allow-refund-difference`. a7's own description declines the refund half: the
section "states no independent refund entitlement, so this pack resolves the compensation half of the
question and never asserts a refund."

**What I did instead:** declared no edge and recorded the overlap here. a7 declares no refund
outcome, no refund rule, and no input pointer that a refund determination could be written to, so
there is nothing for an edge to feed; the shared word "refund" in the two questions is a scope
overlap, not a data flow. A consumer needing the whole money answer must read **both** nodes'
dispositions, which the composite reports side by side — the `allow-refund-difference` outcome of the
`change-cabin` node is the refund answer, and `no-compensation` from the other node does not
contradict it.

## R3. Compensation eligibility is keyed to the cabin class that a3 may change

**Verbatim (Refunds and Compensation, lines 157 and 161):**

> Do not compensate if the user is regular member and has no travel insurance and flies (basic)
> economy.

> Only compensate if the user is a silver/gold member or has travel insurance or flies business.

**Verbatim (Modify flight > Change cabin, line 117):**

> In other cases, all reservations, including basic economy, can change cabin without changing the
> flights.

a7's exclusion and its eligibility gate both read the cabin class (`/reservation/cabinClass`), and a3
is the decision that may change it — a permitted economy→business change moves the user out of the
exclusion and inside the gate.

**What I did instead:** declared no edge, on two grounds. First, the policy nowhere says whether
"flies business" / "flies (basic) economy" is read against the cabin **as booked** or **as changed**;
an edge would silently settle a question the policy leaves open. Second, even if it were settled, a3
produces outcome ids, not cabin classes — no edge could write a value at `/reservation/cabinClass`
that a7's tests could read. The cabin class stays a caller input for the a7 node.

## R4. Confirming the facts is a7's own step and cannot be borrowed from a3

**Verbatim (Refunds and Compensation, line 159):**

> Always confirms the facts before offering compensation.

a7 makes this an evidence requirement (`facts-confirmed`), and a graph *evidence* edge is the one
mechanism that would let an a3 outcome satisfy a downstream requirement — the only structurally
available a3 → a7 edge in the whole format.

**What I did instead: declared no edge, and this is the coupling I most deliberately refused.** a7
defines `facts-confirmed` as an attestation that "the flights in it were in fact cancelled or delayed
as claimed, and the membership level, travel-insurance status, cabin class, and passenger count are
as recorded." a3 establishes none of that: it establishes a user id, a reservation id, whether any
flight has been flown, whether the change covers all segments, and the direction of a price
difference. I built the edge (`a3 → a7`, evidence `facts-confirmed`) to see what it would do; it
passes validation, and it flips a7's `grant-delayed-flight-certificate` from `escalate`-on-unknown to
granting a $50-per-passenger certificate, on the strength of a resolved cabin-change question, with
nobody having confirmed the delay, the membership level, the insurance, or the passenger count. The
attestation stays a per-node input, made by whoever actually confirmed the facts.

---

## Note on one choice the format forced

The schema requires exactly one `result` node. With no edges declared, neither decision is downstream
of the other, so the choice carries no policy content; I named `refunds-and-compensation` because it
is the later decision under R1's ordering, and naming it hides nothing — the composite reports every
node's disposition beside the headline. Consumers should read both.

## Verification

- `bin/jpack experimental graph validate relationships.graph.json --config jpack.json` → exit 0.
- The two probe graphs described in R1 and R4 were built, validated and evaluated only to establish
  the claims above; they are not deliverables and were deleted. The packs were not modified.
