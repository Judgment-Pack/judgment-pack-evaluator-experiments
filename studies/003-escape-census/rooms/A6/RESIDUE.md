# Residue — A6, "Cancel flight" section

Every sentence of the assigned section, quoted verbatim, that the pack does not represent as a
condition, rule, exception, or outcome. Sentences fully represented in `pack.json` are not listed
here (they are: the flown-portion transfer sentence, the four permitted-ground bullets, and the
"Otherwise, flight can be cancelled if any of the following is true" closure).

## 1. Reservation-id lookup assistance

> "If the user doesn't know their reservation id, the agent should help locate it using available
> tools."

**Left out.** This is a procedural instruction about how to obtain an input, not a condition on
whether cancellation is permitted. The pack represents only the obligation that the reservation id
be obtained, as the required evidence requirement `reservation-id`; the lookup duty survives as
prose in that requirement's `description` ("Supplied by the user, or located by the agent with
available tools when the user does not know it"), where no evaluator will act on it.

## 2. Provenance constraint on the user id

> "The user must provide their user id."

**Approximated.** The pack represents that a user id is required (`user-id`, `required: true`) but
cannot represent *who* supplied it: JPS 0.1.0-draft evidence requirements carry no provenance or
authenticity model, and `evidence-present` is a bare tri-state. A runtime that satisfies the
requirement with an id the agent inferred rather than one the user stated would still evaluate to
`present`. The constraint survives only as prose in the requirement description.

## 3. Enumeration of the cancellation reason categories

> "The agent must also obtain the reason for cancellation (change of plan, airline cancelled
> flight, or other reasons)"

**Partly represented, partly approximated.** The obligation to obtain a reason is the required
evidence requirement `cancellation-reason`. The three-way categorisation is *not* enforced: no rule
reads a `reasonCategory` pointer, because no outcome in this section turns on the category as such.
The category matters only through the insurance ground, and there it is subsumed into the computed
fact `/cancellation/reasonCoveredByInsurance` (see FACTS-LEDGER.md). A reservation cancelled on a
reason outside the three listed categories would not be caught by the pack.

## 4. The agent's verification duty

> "The API does not check that cancellation rules are met, so the agent must make sure the rules
> apply before calling the API!"

**Approximated, via `onUnknown`.** This is a statement about the surrounding system, not a
condition on the reservation, and there is nothing in Core to bind a pack outcome to a subsequent
API call. Its operative content — the agent bears the burden of being sure — is encoded indirectly
by giving the closure rule `no-permitted-ground` `onUnknown: escalate`, so that an undetermined
ground blocks resolution instead of being silently treated as absent. That is a translation of the
sentence's spirit, not of its text.

## 5. Refund destination and timing

> "The refund will go to original payment methods within 5 to 7 business days."

**Pushed into an outcome description.** This is a consequence of a permitted cancellation, not a
condition on whether cancellation is permitted, and the assigned decision question is only "may
this reservation be cancelled?". It is recorded in the `cancellation-permitted` outcome's
`description` and cited as `policy-cancel-refund`, but nothing evaluates it. Encoding refund
routing would require a second decision pack.

## 6. The "First, the agent must obtain..." ordering

> "First, the agent must obtain the user id and reservation id."

**Approximated.** The obligation is represented (two required evidence requirements); the word
"First", i.e. the sequencing of collection before any other step, is not. Core has no ordering
construct, and §8's resolution model inspects required evidence before rules only as an internal
artifact of the algorithm, not as a representable author intent.
