# Residue

What `relationships.graph.json` declares: three nodes — `change-flights` (pack `a2`, may the
flights be changed?), `cancel-flight` (pack `a6`, may this reservation be cancelled?),
`refund-compensation` (pack `a7`, is the user owed a refund or compensation?) — an explicitly
empty `edges` array, and `refund-compensation` as the result node. It passes
`bin/jpack experimental graph validate relationships.graph.json --config jpack.json` (exit 0).

**No edge is declared.** The policy does state a relationship between these decisions, so the
empty `edges` array is not a claim that the decisions are independent; it is a statement that the
relationship the policy states is not of the shape this format's edge can carry. This format's
edge carries exactly two things: an upstream node's **outcome id, written verbatim as a fact** at
a pointer in the downstream node's facts document, and/or an upstream node's **having produced an
outcome at all**, contributed as `present` for a named evidence requirement of the downstream
pack. The relationship the policy states is between a **completed action** and a decision, and
neither channel can carry it. The sentences are recorded below, verbatim, with what I did instead
and with the tool output that settled each rejection.

---

## Item 1 — the delayed-flight certificate is conditional on the change or cancellation

> - If the user complains about delayed flights in a reservation and wants to change or cancel the reservation, the agent can offer a certificate as a gesture after confirming the facts and changing or cancelling the reservation, with the amount being $50 times the number of passengers.

(`policy.md` line 165, Refunds and Compensation.)

This is the one sentence that makes one of these decisions conditional on another: `a7`'s
`certificate-delayed-flight` outcome requires that the reservation actually was changed (`a2`'s
subject) or cancelled (`a6`'s subject). `a7` already encodes the condition, as the fact
`/reservation/changeOrCancelCompleted` on `grant-delayed-flight-certificate` and inside
`deny-other-reason`.

**What I did instead.** I declared no edge and left `/reservation/changeOrCancelCompleted` as a
caller-supplied fact of the `refund-compensation` node, exactly as `a7` wrote it. The dependency
is stated in prose in the graph's `description` and in all three nodes' `description` members, and
it is stated here. A consumer composing these three packs must supply that fact from the record of
what the agent actually did; the graph does not and cannot derive it.

**Why no edge.** Three independent reasons, each checked against the tool:

1. *The fact channel carries an outcome id, and the pointer wants `true`.* An edge
   `a6 → a7` at `/reservation/changeOrCancelCompleted` validates, so the error would not be
   caught by validation — but it inverts the sentence. Evaluated with an upstream that resolved
   to `cancellation-permitted`:

   ```
   fact /reservation/changeOrCancelCompleted <- cancel-flight: injected cancellation-permitted
   trace: rule deny-other-reason: true outcome=no-compensation
   trace: rule grant-delayed-flight-certificate: false
   ```

   The injected string is never `equals true`, so the edge would permanently falsify the
   delayed-flight grant and permanently satisfy the closed-list denial: the certificate this
   sentence authorises could never be offered through the composed graph. Declaring the edge
   would be worse than declaring nothing.

2. *These packs decide permission; the sentence conditions on performance.* `a2` says of itself
   that it "does not authorise any call to the booking API"; `a6` says it "does not perform the
   cancellation". Their outcomes `change-permitted` and `cancellation-permitted` mean the rules
   allow the action, not that the booking database was updated — and the preamble puts an
   explicit user confirmation between the two. So even a hypothetical boolean-typed edge would
   assert something neither upstream pack decides. The gap here is in the encoding of the
   decisions, not only in the graph format.

3. *"change **or** cancel" is a disjunction over two upstream decisions, and one pointer takes
   one edge.* Feeding both `a2` and `a6` into the single input the sentence gates on is refused:

   ```
   JPS-GRAPH-EDGE-DUPLICATE-FACT /edges/1/fact: A second edge feeds the fact pointer
   "/reservation/changeOrCancelCompleted" of node "compensation"; one pointer has one feeding
   edge, and a merge rule is a semantics nobody declared.
   ```

   There is no fan-in or disjunction in the format, so even a well-typed channel could represent
   only half of the sentence. (`a2` also carries `applicability` on `/request/type` equals
   `change-flights`, so in a cancellation scenario `a2` is not applicable and an edge from it
   would inject nothing at all: `not injected (the upstream disposition is not an outcome)`.)

**One further alternative considered and rejected.** The evidence channel — an edge
`a6 → a7` feeding `a7`'s `facts-confirmed` requirement — validates and does affect the outcome:

```
evidence facts-confirmed <- cancel-flight: present
```

I rejected it. It asserts that because `a6` reached any outcome, the compensation facts are
confirmed; `a7` defines `facts-confirmed` as covering the delay or cancellation as claimed, the
membership level, the insurance status, the cabin class and the passenger count, none of which
`a6` establishes (the probe above resolved `a6` on an airline cancellation alone). The error would
also run in the permissive direction: `facts-confirmed` present is what unlocks both grant rules.
An edge that manufactures an attestation is not a way to record a sentence about sequencing.

---

## Item 2 — the cancelled-flight certificate and the airline-cancellation ground

> - If the user complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers.

(`policy.md` line 163, Refunds and Compensation.)

This sentence states no dependency between the decisions — it does not make the certificate
conditional on the cancellation decision — but it does put the same world-fact under two
decisions: "the airline cancelled a flight in this reservation" is `a6`'s
`/reservation/anySegmentCancelledByAirline` (a ground on which cancellation is permitted) and
`a7`'s `/complaint/aboutCancelledFlights`. A reader may expect the composition to keep those two
consistent. It does not.

**What I did instead.** Nothing declared. Each node's facts are supplied independently and the
format has no shared-fact channel: an edge carries an outcome id, not a caller's fact, so one
world-fact cannot be declared once and fanned out to two nodes. The two pointers are recorded here
as a consistency obligation on whoever assembles the inputs document. The same applies to
`/reservation/hasTravelInsurance` and `/reservation/cabinClass`, which `a6` reads as cancellation
grounds and `a7` reads as its eligibility gate.

---

## Item 3 — always confirm the facts

> Always confirms the facts before offering compensation.

(`policy.md` line 159, Refunds and Compensation.)

Named here because it is the sentence the rejected evidence edge of item 1 would have
misrepresented, and because it is the only place in these three packs where a decision's evidence
could have been fed from another decision.

**What I did instead.** Left it entirely inside `a7`, as its `facts-confirmed` evidence
requirement supplied by the caller. No edge asserts it, so the composed graph never treats another
pack's disposition as the confirmation this sentence demands.

---

## Item 4 — the cancellation refund, against `a7`'s question

> - The refund will go to original payment methods within 5 to 7 business days.

(`policy.md` line 152, Cancel flight › Refund.)

`a7`'s question is "Is the user owed a refund or compensation, and what kind?", but `a7` states
that the section it encodes "states no independent refund entitlement, so this pack resolves the
compensation half of the question and never asserts a refund". The refund half of `a7`'s question
is answered inside `a6`, in the `cancellation-permitted` outcome's own description. That is a
relationship between the two packs' scopes — one pack answers part of another's stated question.

**What I did instead.** Nothing declared, and nothing can be: the format's edge feeds a
downstream pack's inputs, and there is no channel for "the refund half of this question is
resolved by that node." Recorded here so the overlap is visible to whoever reads the composite,
where `a6` and `a7` will both appear to speak about refunds.

---

## Considered and not recorded as residue

These sentences relate a decision to an action or an obligation rather than relating two of these
three decisions, so there is nothing for an edge to carry:

- line 7 (list the action details and obtain explicit user confirmation before a booking-database
  update), line 13 (deny requests against the policy) and line 15 (transfer if and only if out of
  scope): cross-cutting obligations that sit downstream of each decision individually; `a2`, `a6`
  and `a7` each already carry them in their outcome descriptions or escalation blocks.
- line 141 ("If any portion of the flight has already been flown, the agent cannot help and
  transfer is needed") and line 149 (the API checks no cancellation rule): internal to `a6`,
  which encodes them as the `portion-already-flown` exception and as escalation.
- lines 155, 157, 161 and 167 (no proactive offer, the regular/uninsured/economy exclusion, the
  eligibility gate, the closed list of grounds): internal to `a7`.
- line 131 ("If the flights are changed, the user needs to provide a single gift card or credit
  card for payment or refund method"): a genuine dependency on `a2`, but on a payment-method
  decision that no pack in this project encodes; `a7` is the compensation-gesture decision and is
  not that pack.
