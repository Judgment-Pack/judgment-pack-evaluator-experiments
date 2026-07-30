# Residue

## Conclusion

`relationships.graph.json` declares both decisions as nodes and **zero edges**. The Airline
Agent Policy states no sentence that makes either decision's *outcome* an input to the other,
and an edge in this graph format can carry nothing else.

What an edge can carry, per `bin/jpack experimental graph schema`:

- `fact`: when the upstream disposition is an outcome, **the outcome id itself** is written
  verbatim at a JSON Pointer in the downstream node's facts document; nothing else is written.
- `evidence`: an upstream outcome contributes `present` for a named evidence requirement the
  downstream pack declares.

The two packs' vocabularies do not meet on either channel:

- `a1` (Book flight) has outcomes `book-allowed` / `book-denied`. `a7` reads facts at
  `/request/compensationExplicitlyRequested`, `/user/membershipLevel`,
  `/reservation/hasTravelInsurance`, `/reservation/cabinClass`,
  `/complaint/aboutCancelledFlights`, `/complaint/aboutDelayedFlights`,
  `/complaint/wantsChangeOrCancel`, `/reservation/changeOrCancelCompleted`,
  `/reservation/passengerCount`, and declares one evidence requirement, `facts-confirmed` (an
  attestation that the *complaint's* facts were confirmed). Writing the string `book-allowed`
  at any of those pointers would state something the policy does not say and the pack does not
  mean — e.g. at `/reservation/passengerCount` it would satisfy `not-equals null` and let a
  certificate be sized on an outcome id; feeding `facts-confirmed` from a booking approval
  would let a booking gate stand in for confirming a complaint. Neither is a policy sentence.
- `a7` has outcomes `no-compensation` / `certificate-cancelled-flight` /
  `certificate-delayed-flight`. `a1` reads `/request/type`, `/booking/...`,
  `/user/membershipLevel`, and declares evidence requirements `user-id`, `trip-parameters`,
  `passenger-details`, `travel-insurance-offer`. No compensation outcome id is any of those,
  and injecting one at `/booking/payment/travelCertificateCount` would break a count test
  (`in [0, 1]`) and manufacture a denial.

So no edge would be a relationship the policy states; each entry below is left to the packs'
own facts and unknown handling instead. No pack was modified.

## Sentences relating these decisions that I could not represent as a declared relationship

### 1. Travel insurance bought at booking, and the refund half of a7's question

> - The travel insurance is 30 dollars per passenger and enables full refund if the user needs to cancel the flight given health or weather reasons.

(policy.md line 101, `## Book flight → Travel insurance`)

This is the one sentence in the Book flight section that reaches forward to money returned to
the user, and `a7`'s decision question is "Is the user owed a refund or compensation, and what
kind?". **What I did instead:** nothing in the graph. The refund this sentence names is the
Cancel flight refund, conditioned on a cancellation and its reason — neither of which is a
disposition of `a1` — and `a7` states it resolves only the compensation half and "never asserts
a refund", declaring no rule or evidence requirement for such an entitlement. An `a1 → a7` edge
could only deliver `book-allowed`, which asserts nothing about whether insurance was bought;
`a7` reads insurance as its own fact at `/reservation/hasTravelInsurance`, and it stays there.

### 2. Compensation eligibility turns on reservation attributes the Book flight section fixes

> Only compensate if the user is a silver/gold member or has travel insurance or flies business.

(policy.md line 161)

> Do not compensate if the user is regular member and has no travel insurance and flies (basic) economy.

(policy.md line 157)

Every operand — membership level, travel insurance, cabin class — is settled when the
reservation is booked. **What I did instead:** nothing in the graph. These sentences condition
compensation on *attributes of the reservation*, not on whether the booking decision allowed
the booking; the format's `fact` channel would write `book-allowed` where `a7` expects `true`,
`"business"`, or a membership level. Both sentences are already encoded inside `a7`
(`deny-ineligible`, exception `excluded-regular-uninsured-economy`) against its own facts, and
that is where they remain.

### 3. The certificate amount is sized by a passenger count the Book flight section bounds

> - If the user complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers.

(policy.md line 163)

> - If the user complains about delayed flights in a reservation and wants to change or cancel the reservation, the agent can offer a certificate as a gesture after confirming the facts and changing or cancelling the reservation, with the amount being $50 times the number of passengers.

(policy.md line 165)

read against

> - Each reservation can have at most five passengers.

(policy.md line 73, `## Book flight → Passengers`)

The multiplier `a7` uses is the passenger count `a1` constrains to 1..5. **What I did instead:**
nothing in the graph. This is a shared quantity, not an outcome hand-off: `a1`'s disposition
does not carry the count, and the count is not an evidence requirement of `a7`. `a7` reads it
at `/reservation/passengerCount` and escalates when it is unavailable, which is the pack's own
handling and needs no edge.

### 4. A single cabin class per reservation is what makes a7's cabin test well-formed

> - Cabin class must be the same across all the flights in a reservation.

(policy.md line 70, `## Book flight → Cabin`)

> - All passengers must fly the same flights in the same cabin.

(policy.md line 75, `## Book flight → Passengers`)

`a7` tests one `/reservation/cabinClass` for the whole reservation (and `a1`'s own baggage
rationale relies on the same uniformity). **What I did instead:** nothing in the graph. This is
a well-formedness premise the Book flight section supplies to a7's vocabulary, not an outcome
feeding an input; `a1` enforces it (`deny-cabin-class-not-uniform`) and `a7` presupposes it.
The format has no channel for "this pack's rule is why that pack's fact is single-valued".

### 5. A compensation certificate as a later booking's payment instrument

> - Each reservation can use at most one travel certificate, at most one credit card, and at most three gift cards.

(policy.md line 78, `## Book flight → Payment`)

> - The remaining amount of a travel certificate is not refundable.

(policy.md line 79)

The gesture `a7` grants is a travel certificate, and travel certificates are one of the payment
methods the Book flight section limits and declares non-refundable. **What I did instead:**
nothing in the graph. The policy never says the certificate offered as compensation is the
certificate tendered for a subsequent booking — that is an inference, not a stated
relationship — and an `a7 → a1` edge could only write `certificate-cancelled-flight` into a
count that `a1` tests with `in [0, 1]`, which would fabricate a `book-denied`.

## Considered and found not to relate these two decisions

- `> Before taking any actions that update the booking database (booking, modifying flights, editing baggage, changing cabin class, or updating passenger information), you must list the action details and obtain explicit user confirmation (yes) to proceed.` (line 7) and `> You should deny user requests that are against this policy.` (line 13) bind the agent across the whole policy; they relate each decision to the agent's conduct, not one decision to the other. `a1` says explicitly that preamble obligations are outside its scope.
- The Cancel flight and Modify flight sections mediate between insurance/booking facts and money returned (`> - The refund will go to original payment methods within 5 to 7 business days.`, line 152), but neither section is a pack in this project, so nothing in this room can carry that path.

## Note on the required `result` member

The format requires exactly one result node. With no edges, no ordering between the two nodes
exists to justify a choice: `result` names `book-flight` only because the member is mandatory,
and it is not a claim that the compensation decision is subordinate to, or derived from, the
booking decision. Every node's disposition is reported beside the headline, so naming either
one hides nothing.
