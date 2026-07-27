# Interpretation decisions — R1 "Cancel pending order"

Numbered choices made while encoding policy.md §"Cancel pending order" (lines 86–92) as
`pack.json`. Each entry: the text at issue, the alternatives, the reading chosen, and why.

## 1. Refund timing is outcome identity, not prose

**Text.** "the total will be refunded via the original payment method immediately if it is gift
card, otherwise in 5 to 7 business days."

**Alternatives.** (a) One `cancel-order` outcome, refund timing described in its `description`.
(b) Two outcomes distinguishing the refund channel.

**Chosen.** (b): `cancel-refund-immediately` and
`cancel-refund-in-five-to-seven-business-days`.

**Why.** The sentence makes a real distinction that a downstream caller must act on differently,
and it turns on a fact (`/order/originalPaymentMethod/type`) the pack already has to read to be
faithful. Encoding it as outcome identity keeps the distinction machine-visible instead of
demoting it to residue. The two rules are mutually exclusive (`equals` vs `not-equals`
`"gift_card"`), so they can never both fire and produce a `conflict`.

## 2. "Not confirmed yet" is its own outcome, not a denial and not a handoff

**Text.** "The user needs to confirm the order id and the reason ... for cancellation." /
"After user confirmation, the order status will be changed to 'cancelled'".

**Alternatives.** (a) Treat a missing confirmation as a denial. (b) Let it fall through to
`no-match` → `unresolved` → human handoff. (c) A distinct `request-user-confirmation` outcome.

**Chosen.** (c).

**Why.** (a) misstates the policy — nothing about an unconfirmed request is *impermissible*; the
user simply has not been asked yet. (b) would transfer routine conversations to a human, which
line 24 forbids ("transfer ... if and only if the request cannot be handled within the scope of
your actions") — collecting a confirmation is squarely within scope. (c) states the actual
position: pending order, cancellation still available, one interactional step outstanding.

## 3. A non-pending order is denied, not escalated

**Text.** "An order can only be cancelled if its status is 'pending'."

**Alternatives.** (a) `deny-cancellation`. (b) Escalate, since the user wants something the agent
cannot do.

**Chosen.** (a).

**Why.** Line 22 says "You should deny user requests that are against this policy", and line 24
restricts transfer to requests that "cannot be handled within the scope of your actions". Refusing
to cancel a delivered order *is* an in-scope answer, so a denial is the faithful result. (Any
follow-on request such as a return is a different decision and a different pack.)

## 4. `onUnknown` per rule

**Chosen.** `escalate` on `cancel-pending-original-gift-card`,
`cancel-pending-original-not-gift-card`, `deny-status-not-pending`, and
`await-confirmation-of-order-id-and-reason`; `ignore` on `deny-unacceptable-reason`.

**Why.** Every escalating rule reads `/order/status`, and the policy makes the status check
mandatory before acting — so an undeterminable status must block, never silently produce a
candidate. The two cancel rules additionally gate a database mutation and a refund; approving
either on incomplete data is the worst available error, so an unknown original-payment-method type
must block as well (verified: absent `/order/originalPaymentMethod/type` → `unresolved`/`unknown`).

`deny-unacceptable-reason` is the exception. Under §8 step 7, an unknown escalating rule blocks
*everything*, including other rules' clear results. If the reason is undeterminable but the status
is plainly `delivered`, the correct answer is still a denial; with `escalate` that clear denial
would be swallowed by an `unknown`. And an undeterminable reason is not evidence of an
*unacceptable* reason, so ignoring it loses nothing: the cancel rules already block whenever the
reason cannot be established. Verified: status `delivered` + reason absent → `deny-cancellation`.

## 5. "Not yet provided" is modelled as `false`/`null`, never as a missing pointer

**Chosen.** `/request/orderIdConfirmedByUser` and `/request/reasonConfirmedByUser` are booleans
that are `false` before the user confirms; `/request/cancellationReason` is `null` when no reason
was given. A missing pointer means "the runtime could not determine this", which is a different
condition entirely.

**Why.** Conflating "the user has not said yes yet" with "unknown" would push ordinary
mid-conversation states into `unresolved`/handoff. Keeping them distinct lets rule 5 answer
`request-user-confirmation` while genuine gaps in the facts document still escalate. Verified: all
confirmations `false` and reason `null` → `request-user-confirmation`, no handoff.

## 6. Applicability guard on `/request/action`

**Chosen.** `applicability` = `/request/action equals "cancel_order"`.

**Alternatives.** Omit applicability (Core then treats it as `true`).

**Why.** The section heading scopes its rules to cancellation requests, and this pack's rules would
otherwise offer opinions about return or exchange requests that touch a pending order. The guard
costs one requester fact and makes the pack self-delimiting. It also keeps sibling packs for the
other sections composable.

## 7. Confirmation of the order id is a boolean, not an id comparison

**Text.** "The user needs to confirm the order id".

**Alternatives.** (a) `/request/orderIdConfirmedByUser` boolean. (b) Compare a user-stated
`/request/orderId` with the record's `/order/orderId` for equality.

**Chosen.** (a).

**Why.** The policy describes an *interactional* act — the user confirming which order is meant —
not a string-matching computation. (b) would also silently change the fact's provenance: it makes
the pack the thing that decides whether two ids match, and it cannot represent "the user has not
said anything yet" at all. A deployment that wants (b) can compute the boolean that way; the
ledger's `requester` classification would then need re-examination.

## 8. Reason enum uses the exact policy strings

**Chosen.** The `in` list is `["no longer needed", "ordered by mistake"]` — the two strings the
policy prints, verbatim, lowercase.

**Why.** The policy enumerates them as literal reason values, so the pack compares literals rather
than inventing codes such as `NO_LONGER_NEEDED`. Any other value, including `null`, falls out of
the `in` test as `false`.

## 9. Where free-text normalisation would move the reason fact to `computed`

**Chosen.** `/request/cancellationReason` is classified `requester` in the ledger, with an explicit
caveat.

**Why.** The policy's own model is that the agent offers the two acceptable reasons and the user
confirms one, so the value is stated directly. But if a deployment instead lets the user say "I
changed my mind, it's too expensive" and maps that onto the enum, that mapping is an application
of the policy's own acceptability judgement — exactly the boundary the census cares about — and the
fact becomes `computed` for that deployment. Recorded in the ledger rather than hidden.

## 10. "The original payment method" is a computed fact

**Text.** "the total will be refunded via the original payment method immediately if it is gift
card".

**Why.** The order record stores a *payment history* (line 72), not an "original payment method"
field, and users have several payment methods on their profile (lines 36–39). Producing
`/order/originalPaymentMethod/type` requires selecting the initial charge out of the payment
history — deciding what counts as "the original" payment when refunds or adjustments are also
present — and then resolving that method id to a type. That is a derivation with an interpretive
step, not a lookup, so the ledger marks it `computed` and says precisely what must be done.

## 11. "Check its status before taking the action" is a required evidence requirement

**Alternatives.** (a) Rely on the `/order/status` fact alone. (b) Add a required evidence
requirement `order-status-check` in addition to the fact.

**Chosen.** (b).

**Why.** The sentence contains two obligations: a *substantive* one (only pending orders may be
cancelled) and a *procedural* one (the status must actually have been checked, and checked before
acting). The fact carries the first; only the evidence machinery carries the second, and it gives
the runtime a place to say "I never looked". Verified: `order-status-check: absent` →
`unresolved`/`missing-required-evidence` with a handoff request, even when the facts document
happens to contain a status.

## 12. Escalation triggers exclude `not-applicable`

**Chosen.** `triggers: [missing-required-evidence, unknown, conflict, no-match]`, target
human-role "Human agent (transfer_to_human_agents)", message quoting line 24's required handoff
phrasing.

**Why.** A request that is not a cancellation request is not a failure of this pack and must not
drag a human in; it simply belongs to another decision. The other four reasons all mean "this pack
cannot answer", which is precisely line 24's condition for transfer. Note the escalation object is
handoff *configuration*, not an outcome (§6.7) — the pack never "decides" to transfer.

## 13. No `fallbackOutcome`

**Chosen.** Omitted.

**Why.** The rule set already covers the pending / non-pending × confirmed / unconfirmed ×
acceptable / unacceptable space, so any `no-match` that does occur is a genuine gap in the
encoding. A fallback would convert that gap into a confident answer. Leaving it out routes gaps to
`unresolved` → human, which matches line 24.

## 14. No exceptions used

**Why.** The section states conditions, not typed carve-outs from its own rules. Adding a
`suppress-rule` or `force-outcome` exception would have meant inventing policy. The one nearby
rule that *looks* like a carve-out — "Modify items ... will change the order status to 'pending
(items modified)'. The agent will not be able to modify or cancel the order anymore" (line 110) —
is outside the assigned section and needs no special handling here: that status is not `"pending"`,
so `deny-status-not-pending` already denies it.

## 15. Generic policy obligations deliberately left out of this pack

**Text (all outside the assigned section).** Authentication by email or name + zip (line 10); one
user per conversation and denial of other-user requests (line 14); "list the action details and
obtain explicit user confirmation (yes)" before any database update (line 16); one tool call at a
time (line 20); "Generally, you can only take action on pending or delivered orders" (line 82).

**Chosen.** Not encoded. The brief scopes this pack to the "Cancel pending order" section, and each
of these is a cross-cutting obligation that belongs either to a session-level pack or to every
sibling pack equally; duplicating them here would double-count them in the census.

**Partial exception.** Line 16's confirmation requirement is *also* stated inside the assigned
section ("The user needs to confirm the order id and the reason", "After user confirmation"), so
the confirmation booleans are encoded from the section's own wording. The additional line-16
obligation to *list the action details* first is not represented — it is a procedural duty of the
agent, not a condition on whether cancellation is permitted. Order ownership is likewise not
checked here, so a caller must not treat this pack as an authorisation check for who is asking.
