# Residue

## Conclusion

`relationships.graph.json` declares **two nodes and zero edges**. The Airline Agent
Policy states no relationship between these two decisions that the graph format can
carry, so every policy sentence that connects them is residue and is recorded below.

The two decisions are:

- `book-flight` → pack `a1`, "May this booking be made?" — a gate on a *proposed* new
  reservation, applicable only when `/request/type` equals `book-flight`.
- `cancel-flight` → pack `a6`, "May this reservation be cancelled?" — a gate on an
  *existing* reservation.

Why no edge is declarable. An edge in this format carries exactly one thing: the
upstream node's **outcome id**, written verbatim at a JSON Pointer in the downstream
facts document, or turned into `present`/`unknown`/`absent` for a downstream evidence
requirement. `a1`'s outcome ids are `book-allowed` and `book-denied`; `a6`'s are
`cancellation-permitted` and `cancellation-denied`. Every connection the policy draws
between booking and cancellation runs through *shared attributes of the reservation*
(its created time, its cabin class, whether insurance was bought, which payment
methods were used), never through the *outcome* of the booking-permissibility
decision. `a6` reads those attributes as its own facts —
`/reservation/hoursSinceBooking`, `/reservation/cabinClass`,
`/reservation/hasTravelInsurance`, `/cancellation/reasonCoveredByInsurance`,
`/reservation/anySegmentCancelledByAirline`, `/reservation/anySegmentFlown` — and none
of them is answered by "the booking was permitted". Nothing in the policy makes a
cancellation decision depend on whether the booking *ought to have been allowed*, and
nothing makes a booking decision depend on a cancellation.

I verified that the tool would not have caught a fabricated edge. A probe graph with
`{"from": "book", "to": "cancel", "fact": "/reservation/hasTravelInsurance",
"evidence": {"id": "reservation-id"}}` passed
`experimental graph validate` at exit 0 — `validate` does not read the downstream pack
for a fact feed, so an invented pointer is accepted. Evaluating that probe showed what
the edge actually does: it injected the string `"book-allowed"` at
`/reservation/hasTravelInsurance`, which made `a6`'s `insured-and-reason-covered` rule
evaluate `false` — an insured reservation reported as uninsured — and it asserted
`reservation-id: present` from an outcome that states nothing about any reservation id.
The probe was deleted. A validating edge that misstates the policy is worse than a
recorded absence, so the graph declares none.

## Sentences relating these two decisions that I could not represent

### 1. Insurance bought at booking is a cancellation ground (statement of coverage)

> - The travel insurance is 30 dollars per passenger and enables full refund if the user needs to cancel the flight given health or weather reasons.

*(policy.md, "## Book flight" → "Travel insurance")*

**What I did instead:** nothing in the graph. This sentence sits in the Book flight
section (`a1`'s scope) but its operative half governs cancellation (`a6`). It cannot be
an edge because `a1`'s outcome does not report whether insurance was purchased —
`book-allowed` is returned both for a reservation with insurance and for one without
(`a1` only checks that, *if* purchased, the price is 30 dollars per passenger, and that
the offer was made). Left where it already is: `a6` carries this sentence as its own
source `policy-insurance-coverage` and reads the state as its own fact
`/reservation/hasTravelInsurance`.

### 2. The insurance ground itself

> - The user has travel insurance and the reason for cancellation is covered by insurance.

*(policy.md, "## Cancel flight", fourth paragraph bullets)*

**What I did instead:** nothing in the graph. This is the cancellation-side half of
residue 1 — a ground whose truth was fixed by a decision the booking flow made. Left to
`a6`'s rule `insured-and-reason-covered`, which reads both conjuncts as facts supplied
with the cancellation request.

### 3. The 24-hour ground refers back to the booking event

> - The booking was made within the last 24 hrs

*(policy.md, "## Cancel flight", fourth paragraph bullets)*

**What I did instead:** nothing in the graph. The sentence relates a cancellation ground
to the booking, but what it needs is the booking's *created time*, not the booking
decision's outcome, and an edge can carry only the outcome id. Left to `a6`'s rule
`booked-within-24-hours`, which reads `/reservation/hoursSinceBooking`.

### 4. The business-cabin ground refers back to the cabin chosen at booking

> - It is a business flight

*(policy.md, "## Cancel flight", fourth paragraph bullets)*

**What I did instead:** nothing in the graph. The cabin class is settled at booking —
`a1` enforces that it is uniform across the reservation — and the cancellation ground
reads that settled value. The value itself is not an outcome id, so no edge can carry
it. Left to `a6`'s rule `business-cabin`, reading `/reservation/cabinClass`.

### 5. Booking-time payment rule bearing on what a cancellation refunds

> - The remaining amount of a travel certificate is not refundable.

*(policy.md, "## Book flight" → "Payment")*

**What I did instead:** nothing in the graph. The sentence is a booking-section rule
about refunds, and refunds arise on cancellation. Neither pack decides refund amounts:
`a1` counts payment instruments, `a6` decides permissibility only and says in its
`cancellation-permitted` description that refunds go to the original payment methods.
There is no downstream input for an edge to feed, so the sentence is unencoded by both
packs and recorded here.

### 6. The refund goes to methods established at booking

> - The refund will go to original payment methods within 5 to 7 business days.

*(policy.md, "## Cancel flight" → "Refund")*

**What I did instead:** nothing in the graph. "Original payment methods" are the ones
`a1` constrains at booking (at most one travel certificate, one credit card, three gift
cards, all already in the user profile), so the sentence does link the two decisions —
but as shared reservation state, not as an outcome feed. `a6` carries it as the source
`policy-cancel-refund` and as prose in its `cancellation-permitted` outcome; nothing in
the graph.

### 7. The two decisions are named as parallel capabilities

> As an airline agent, you can help users **book**, **modify**, or **cancel** flight reservations.

*(policy.md, preamble)*

**What I did instead:** nothing in the graph, and this sentence is the reason the graph
has no edges rather than an unstated one. It relates booking and cancellation only by
listing them as sibling capabilities of one agent; it states no order and no dependency
between them, which is exactly what an edge would assert.

## A schema requirement that is not a policy claim

The schema requires a `result` node. With no edges there is no composite and therefore
no headline; I named `cancel-flight` because it is the later decision in the lifecycle,
and **that choice asserts nothing about a relationship**. `experimental graph explain`
confirms the two nodes are planned as independent steps, and
`experimental graph evaluate` would report each node's own disposition with the other's
beside it.

## Sentences I considered and judged not to relate these two decisions

Recorded so the judgment is auditable, not as residue:

- "Before taking any actions that update the booking database (booking, modifying
  flights, editing baggage, changing cabin class, or updating passenger information),
  you must list the action details and obtain explicit user confirmation (yes) to
  proceed." — a preamble obligation that binds each decision separately; it does not
  make one an input to the other. (Cancellation is not in its list.)
- "- The user cannot add insurance after initial booking." — relates Book flight to
  Modify flight, not to Cancel flight; the Modify decision is not a node here.
- "If any portion of the flight has already been flown, the agent cannot help and
  transfer is needed." — internal to `a6` (its `portion-already-flown` exception);
  says nothing about booking.
- "You should transfer the user to a human agent if and only if the request cannot be
  handled within the scope of your actions." — applies to both decisions'
  escalation blocks independently; not a feed between them.
- The "## Refunds and Compensation" rules — they relate cancelled and delayed flights
  to compensation, a decision no pack in this project declares (`jpack.json` declares
  only `a1` and `a6`).
