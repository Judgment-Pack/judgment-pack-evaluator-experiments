# Interpretation decisions — A2

## 1. "Basic economy flights" means the reservation's cabin class is basic economy

**Text:** "Basic economy flights cannot be modified."

**Alternatives:** (a) per-segment — block only the segments booked in basic economy;
(b) per-reservation — block the whole reservation when its cabin is basic economy.

**Reading:** (b). Domain Basic and Book flight both state that cabin class is uniform across a
reservation ("Cabin class must be the same across all the flights in a reservation"), and Change
cabin repeats it. A reservation therefore has exactly one cabin, so "basic economy flights" and
"basic economy reservation" are coextensive. Encoded as one lookup, `/reservation/cabinClass`,
rather than an aggregation over segments.

**Why:** (a) would require a fact the domain model cannot produce (a mixed-cabin reservation is
not constructible under this policy), and would make the pointer computed for no gain.

## 2. Basic economy is an overriding exception, not a rule

**Text:** "Basic economy flights cannot be modified. **Other** reservations can be modified
without…"

**Alternatives:** (a) a third rule `when cabin == basic economy → change-denied`;
(b) `exceptions[].effect: force-outcome`.

**Reading:** (b). The word "Other" makes the second sentence the general rule and the first a
carve-out that removes reservations from it entirely.

**Why:** under the §8 resolution model this is also the only encoding that behaves correctly.
With (a), a basic economy reservation whose `preservesOrigin` fact is missing would leave the
shape rules `unknown`; with `onUnknown: escalate` (decision 6) that unknown blocks resolution and
the case escalates instead of being denied. A `force-outcome` exception resolves at step 6 before
rules are evaluated, so "cannot be modified" really is unconditional. Verified: basic economy plus
a missing `preserves*` fact still yields `change-denied`.

## 3. Requests that would change origin, destination, or trip type are denied, not escalated

**Text:** "Other reservations can be modified without changing the origin, destination, and trip
type." Preamble: "You should deny user requests that are against this policy." /
"You should transfer the user to a human agent if and only if the request cannot be handled within
the scope of your actions."

**Alternatives:** (a) escalate — a human might be able to re-route the trip;
(b) deny — the request is against the policy; (c) no outcome at all (the section only grants
permission, it never prohibits).

**Reading:** (b). The sentence is a bounded grant of permission; a request outside the bound is
against the policy, and the preamble's default for that is denial. The transfer clause is "if and
only if the request cannot be handled", and denying is handling it.

**Why:** (c) would leave the pack unable to answer "no" for the commonest failure mode, which
defeats the point of a pre-API check. (a) reads the transfer clause as covering anything the agent
cannot grant, which the "if and only if" wording rules out.

## 4. The deny rule is the exact negation of the permit rule

**Alternatives:** (a) `any[ preservesOrigin == false, preservesDestination == false,
preservesTripType == false ]`; (b) `not(all[…])`; (c) no deny rule, use
`fallbackOutcome: change-denied`.

**Reading:** (b).

**Why:** with (a), a fact present but not Boolean (say `null`, or a string) makes both rules false
and the disposition falls to `no-match` — a silent gap. (b) makes the two rules provably
exhaustive and mutually exclusive under three-valued logic: `conflict` and `no-match` become
unreachable, and any non-`true` value lands on deny, the conservative side demanded by "the agent
must make sure the rules apply before calling the API". (c) behaves identically to (b) at runtime
but a `fallbackOutcome` carries no description, rationale, or `sourceRefs`, so the denial would be
uncited. `no-match` is still declared as an escalation trigger as a net.

## 5. The question is about a *proposed* change, so the facts describe the proposal

**Text:** the assigned question is "May the flights in this reservation be changed?", but the
policy's condition is "without changing the origin, destination, and trip type".

**Alternatives:** (a) read the question as reservation-only eligibility (then only cabin class
matters, and origin/destination/trip type are unencodable); (b) read it as "may this reservation's
flights be changed *as requested*".

**Reading:** (b). `decision.question` keeps the assigned wording verbatim; `decision.intent` and
the pack `description` make the proposal-relative scope explicit, and the three `/request/…`
pointers are named for the proposal rather than the reservation.

**Why:** (a) would drop half the assigned section. The policy's only substantive constraint on a
flight change is a property of the proposed itinerary, so a pack that ignores the proposal cannot
answer the question the section governs.

## 6. `onUnknown: escalate` everywhere

**Text:** "The API does not check these for the agent, so the agent must make sure the rules apply
before calling the API!"

**Alternatives:** (a) `ignore` on the permit rule and `escalate` on the deny rule (an unknown then
falls through to denial); (b) `escalate` on all three rules and the exception; (c) `ignore`
throughout with a `change-denied` fallback.

**Reading:** (b).

**Why:** the exclamation-marked warning is the strongest sentence in the section and it demands
positive confirmation, not a guess in either direction. Silently denying on unknown data (a)/(c)
is wrong too: it produces a confident "no" to the customer on the basis of a fact nobody looked
up, and the pack would be unable to distinguish "the policy forbids this" from "we don't know".
Escalation keeps that distinction visible: `unresolved [unknown]` with a handoff to a human agent.

## 7. A required evidence requirement models "the agent must make sure"

**Alternatives:** (a) no evidence requirements — rely on `onUnknown: escalate` alone;
(b) a required `verified-reservation-record`.

**Reading:** (b), `required: true`, `kind: fact`, referenced by both rules.

**Why:** `onUnknown` only catches facts that are *absent*. It cannot catch facts that are present
but were taken from the customer's description instead of the booking system — precisely the
failure the policy warns about, since the API will not catch it either. A required evidence
requirement makes "I actually looked at the record" a first-class precondition: `absent` yields
`missing-required-evidence` and a handoff, never a decision.

## 8. Applicability is gated on the request being a flight change

**Alternatives:** (a) omit `applicability` (the pack is always applicable);
(b) gate on `/request/type == "change-flights"`.

**Reading:** (b), with `not-applicable` deliberately **excluded** from `escalation.triggers`.

**Why:** the surrounding policy has four other decisions (book, change cabin, change baggage,
cancel) that share the same reservation facts, and a pack that answered "may the flights be
changed?" for a cancellation request would be actively misleading. Excluding `not-applicable` from
the triggers is the point of decision 3's "if and only if": a request this pack does not cover is
not thereby a request the agent cannot handle, so it must not transfer to a human.

## 9. The "Modify flight" preamble (user id / reservation id) is not encoded

**Text:** "First, the agent must obtain the user id and reservation id. — The user must provide
their user id. — If the user doesn't know their reservation id, the agent should help locate it
using available tools."

**Alternatives:** (a) encode as two required evidence requirements;
(b) leave out as belonging to the parent section, not the assigned subsection.

**Reading:** (b).

**Why:** the assignment scopes me to the Change flights subsection and calls the rest context.
These sentences are identification preconditions shared with Cancel flight and the other Modify
subsections; they belong in an intake pack, and duplicating them here would misattribute them to
the Change flights rules. The `verified-reservation-record` evidence requirement presupposes that
a reservation has been identified, which is as far as I go. Flagged here rather than in
RESIDUE.md because RESIDUE.md covers the assigned section only.

## 10. The "Payment" bullet under Modify flight is not encoded

**Text:** "If the flights are changed, the user needs to provide a single gift card or credit card
for payment or refund method. The payment method must already be in user profile for safety
reasons."

**Alternatives:** (a) encode it as a further condition on `change-permitted` — it is conditioned
on exactly this decision ("if the flights are changed"); (b) leave out as a separate subsection.

**Reading:** (b), with the constraint acknowledged in the `change-permitted` outcome description
("the agent must still list the action details, obtain explicit user confirmation, and settle
payment or refund before the booking database is updated").

**Why:** the bullet sits under a sibling `Payment:` heading, and grammatically it is a consequence
of the change being permitted, not a precondition for permitting it — the user is asked for a card
*because* the change is going ahead. Folding it into the permit condition would make a customer
with no eligible card receive "your flights may not be changed", which the policy does not say.

## 11. Already-flown segments do not block a flight change

**Text:** Change cabin says "Cabin cannot be changed if any flight in the reservation has already
been flown"; Cancel flight says "If any portion of the flight has already been flown, the agent
cannot help and transfer is needed." Change flights says nothing.

**Alternatives:** (a) carry the flown-segment bar across into flight changes as an escalation —
it is surely what a sensible airline policy would do; (b) encode only what the assigned section
says.

**Reading:** (b). No flown-segment fact appears in the pack.

**Why:** the brief is to encode faithfully what the section says, not what a sensible policy would
say, and the author demonstrably knew how to write this bar — twice, in adjacent sections, with
two different consequences (refusal vs. transfer). Its absence from Change flights is a
deliberate-looking silence, and picking one of the two neighbouring consequences would be
inventing policy. Recording it as a known gap for the policy owner is the honest move; note that
Change flights bullet 3 explicitly contemplates keeping segments, which sits awkwardly with a
flown-segment bar.
