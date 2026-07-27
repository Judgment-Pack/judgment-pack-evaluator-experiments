# Interpretation decisions — A6, "Cancel flight"

## 1. "Otherwise" is a closure, and the closure is an explicit rule rather than a fallback

**Text:** *"Otherwise, flight can be cancelled if any of the following is true: ..."*

**Alternatives:** (a) four permitting rules plus `fallbackOutcome: cancellation-denied`;
(b) four permitting rules plus a fifth rule that fires when all four grounds are known false.

**Reading:** (b). "Otherwise ... if any of the following is true" is exhaustive — a reservation
with none of the four grounds must be denied — so a denial outcome is required either way. But a
`fallbackOutcome` fires whenever no rule contributes a candidate, including when a ground is
*unknown* rather than false (Core §8 step 10 explicitly says unknown-with-`ignore` rules do not
prevent the fallback). That would deny users because the agent failed to look something up. The
explicit closure rule `no-permitted-ground` is the conjunction of four negations, so it is `false`
when any ground is true, `true` only when all four are known false, and `unknown` when a ground is
undetermined and no other ground is true. `fallbackOutcome` is deliberately omitted; `no-match` is
kept in `escalation.triggers` as a net for a case this reasoning has missed.

## 2. `onUnknown`: `ignore` on the permitting rules, `escalate` on the closure rule

**Text:** *"flight can be cancelled if any of the following is true"* together with *"the agent must
make sure the rules apply before calling the API!"*

**Alternatives:** (a) `escalate` everywhere; (b) `ignore` everywhere; (c) the split above.

**Reading:** (c). (a) over-blocks: Core §8 step 7 makes an unknown `escalate` rule block even a
compatible true outcome, so not knowing the booking time would send a plainly-cancellable business
reservation to a human. The grounds are disjunctive — establishing one is sufficient, and the
policy never asks the agent to establish all four. (b) under-blocks: with every ground unknown the
pack would fall through to denial, contradicting the agent's duty to be sure. The split gives
exactly the intended three-valued behaviour: any established ground permits; all grounds known
absent denies; otherwise the decision is unresolved and a human is asked. Verified against the
evaluator (see FACTS-LEDGER.md scenario table).

## 3. "The flight is cancelled by airline" reads as *any segment*

**Text:** *"The flight is cancelled by airline"*.

**Alternatives:** (a) every flight in the reservation cancelled; (b) any flight in the reservation
cancelled; (c) the specific flight the user is complaining about.

**Reading:** (b), encoded as `/reservation/anySegmentCancelledByAirline`. A reservation may hold
several segments (round trip, connections) and the whole section decides about the reservation as
a unit. Requiring *all* segments to be cancelled would deny a user whose outbound leg the airline
cancelled, which is the paradigm case the ground exists for; the Refunds and Compensation section
confirms the any-reading by speaking of "cancelled flights **in a reservation**". (c) is rejected
because the pack has no per-segment request object.

## 4. "It is a business flight" reads as cabin class `business`

**Text:** *"It is a business flight"*.

**Alternatives:** (a) the trip is for business purposes; (b) the reservation's cabin class is
business.

**Reading:** (b). Domain Basic defines exactly three cabin classes and names one of them
`business`; nothing in the policy models trip purpose, and the surrounding bullets are all facts
the agent can read off the reservation. The Refunds and Compensation section reuses the same
phrasing ("flies business") alongside "(basic) economy", confirming the cabin reading. Because the
policy requires cabin class to be uniform across all flights of a reservation, a single
`/reservation/cabinClass` pointer is sufficient. Cited to both `policy-cancel-grounds` and
`policy-cabin-classes`.

## 5. "Covered by insurance" is a separate computed judgment, not the reason category

**Text:** *"The user has travel insurance and the reason for cancellation is covered by
insurance."*

**Alternatives:** (a) map the three obtainable reason categories directly onto coverage;
(b) read a distinct boolean that someone must decide.

**Reading:** (b). The only coverage definition in the policy is in Book flight — *"enables full
refund if the user needs to cancel the flight given health or weather reasons"* — and health and
weather are not among the three categories the cancel section asks the agent to obtain (change of
plan / airline cancelled flight / other reasons); both would be recorded as "other reasons". No
total function from category to coverage exists, so the pack reads
`/cancellation/reasonCoveredByInsurance` and the ledger records it as a computed fact that requires
applying the policy. Both conjuncts are kept as separate fact conditions inside an `all`, so that
an uninsured reservation makes the rule `false` (not `unknown`) regardless of the coverage fact.

## 6. "Within the last 24 hrs" is strict, measured in hours, threshold kept in the pack

**Text:** *"The booking was made within the last 24 hrs"*.

**Alternatives:** (a) a boolean `bookedWithinLast24Hours` computed outside the pack; (b) a numeric
elapsed-hours fact compared inside the pack with `less-than "24"`.

**Reading:** (b), with the boundary exclusive: a booking made exactly 24 hours ago is *not* within
the last 24 hours. (a) would hide the policy's own threshold inside a fact and make the computed
fact policy-interpreting rather than arithmetic. (b) keeps `24` visible in the pack and reduces the
computed fact to a subtraction. Cost: Core §2.2 requires the operand to be a decimal *string*, and
the reference evaluator returns `unknown` when the fact value is a JSON number, so
`/reservation/hoursSinceBooking` must be supplied as a decimal string — a portability hazard flagged
by Core §7.4 ("structural acceptance of an ordered condition does not imply executable support")
and recorded in the ledger.

## 7. The flown-portion clause is an escalate exception, not a rule

**Text:** *"If any portion of the flight has already been flown, the agent cannot help and transfer
is needed."*

**Alternatives:** (a) a rule producing a third outcome such as `transfer-to-human`; (b) an
exception with effect `escalate`.

**Reading:** (b). Core §6.7 and §8.1 are emphatic that escalation is not an outcome, and the policy
says the agent "cannot help" — there is no decision, only a handoff. Because the sentence stands
before the word "Otherwise", the transfer must outrank the permitting grounds; Core §8 step 4 gives
a true `escalate` exception precedence over forced outcomes and suppression, and step 5 makes the
result unresolved before rules matter. Verified: a flown business-cabin reservation booked an hour
ago yields `unresolved` / `exception-escalation` with a handoff, not `cancellation-permitted`. The
exception uses `onUnknown: escalate`: if the agent cannot tell whether a segment has been flown, it
must not proceed to cancel.

## 8. What counts as "already been flown"

**Text:** *"If any portion of the flight has already been flown ..."*

**Alternatives:** (a) the segment has departed (status `flying` or later); (b) the segment has
landed.

**Reading:** (b), and the ambiguity is pushed into the computed fact
`/reservation/anySegmentFlown` rather than resolved in the pack, because the pack has no access to
the underlying statuses. Domain Basic's status vocabulary (`available`, `delayed`, `on time`,
`flying`) contains no "flown" value and describes `flying` as "taken off but not landed", which
makes "flown" most naturally mean "landed". The ledger flags this as the policy-interpreting part
of that fact. A deployment that prefers reading (a) changes only how the fact is computed, not the
pack.

## 9. Identification inputs are required evidence, and their absence does **not** trigger a handoff

**Text:** *"First, the agent must obtain the user id and reservation id. - The user must provide
their user id. ... The agent must also obtain the reason for cancellation ..."*

**Alternatives:** (a) fact pointers with `equals` conditions; (b) required evidence requirements
with `missing-required-evidence` in `escalation.triggers`; (c) required evidence requirements with
that trigger omitted.

**Reading:** (c). The policy demands that these inputs be *obtained*, not that they hold any
particular value, which is precisely what a required evidence requirement expresses; a fact
condition would have to invent a truth test. `missing-required-evidence` is deliberately kept out of
the trigger list, because the preamble transfers to a human "if and only if the request cannot be
handled within the scope of your actions" — and collecting a user id, or locating a reservation id
with available tools, is squarely within scope. The evaluator confirms the intended shape: absent
`user-id` yields `unresolved` / `missing-required-evidence` with `handoff.state: "none"` — go
collect it, do not transfer. Note a consequence: supplying *no* evidence manifest at all yields
reason `unknown`, which does trigger a handoff.

## 10. Escalation triggers, and no `applicability` condition

**Text (context):** *"You should transfer the user to a human agent if and only if the request
cannot be handled within the scope of your actions."*

**Alternatives:** for triggers, (a) all five; (b) `unknown`, `conflict`, `no-match`. For scope,
(c) an `applicability` condition such as "the request is a cancellation request"; (d) none.

**Reading:** (b) and (d). `not-applicable` is unreachable without an applicability condition, and
`missing-required-evidence` is excluded per #9; the remaining three are exactly the states in which
the automated agent has run out of scope. `applicability` is omitted because the assigned section
states no scope precondition — inventing a request-type gate would add a fact pointer the policy
never mentions. The target is a human role rather than a queue or system, and the `message` carries
the literal transfer script the preamble prescribes.

## 11. The outcome is permissibility, not the cancellation itself

**Text:** *"the agent must make sure the rules apply before calling the API!"* and, from the
preamble, *"you must list the action details and obtain explicit user confirmation (yes) to
proceed."*

**Alternatives:** (a) outcomes named "cancel" / "do not cancel"; (b) outcomes named "cancellation
permitted" / "cancellation denied".

**Reading:** (b). Core §6.4 says an outcome is a declared result, not an authorization to act, and
the confirmation step sits between the policy check and the API call. The `cancellation-permitted`
description states explicitly that confirmation is still required. This keeps the pack answering
the assigned question — *may* this reservation be cancelled — rather than issuing an instruction.
