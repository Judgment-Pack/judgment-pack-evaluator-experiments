# Interpretation decisions — A7 Refunds and Compensation

## 1. "Only compensate if ..." is a necessary condition on every compensation outcome

**Text.** *"Only compensate if the user is a silver/gold member or has travel insurance or flies
business."*

**Alternatives.**
(a) Necessary condition: no compensation outcome may be produced unless the disjunction holds.
(b) Sufficient condition: a silver/gold member, or an insured user, or a business flyer, gets
    compensation.
(c) A standalone default rule that grants nothing but merely "opens" compensation.

**Reading: (a).** "Only ... if" is the standard English marker for a necessary condition, and (b)
would contradict the preceding "do not proactively offer" sentence — it would compensate a gold
member who never asked. So the disjunction appears as a conjunct in both grant rules, and its
negation is an independent denial rule (`deny-ineligible`).

## 2. The exclusion sentence and the eligibility sentence are logically redundant — I encoded both anyway

**Text.** *"Do not compensate if the user is regular member and has no travel insurance and flies
(basic) economy."* against *"Only compensate if the user is a silver/gold member or has travel
insurance or flies business."*

Given the Domain Basics (exactly three membership levels, exactly three cabin classes), "regular AND
no insurance AND (basic) economy" is precisely the negation of "silver/gold OR insurance OR
business". The two sentences say the same thing.

**Alternatives.**
(a) Encode only the eligibility disjunction and treat the exclusion as commentary.
(b) Encode both — the exclusion as an exception with `force-outcome: no-compensation`, the
    eligibility disjunction inside the rules.
(c) Encode only the exclusion.

**Reading: (b).** Each sentence gets a citable home, which is the point of `sourceRefs`, and there
is no behavioural cost: the exception forces exactly the outcome the rules would otherwise reach, so
the two can never disagree. The redundancy is also a hedge — if the domain ever grew a fourth cabin
class or membership tier, the two sentences would come apart and the pack would show the divergence
rather than silently picking one.

**Note on "(basic) economy".** I read the parenthesis as "basic economy or economy", i.e. both
cabins, matching the domain note that *"basic economy is its own class, completely distinct from
economy"*. The alternative reading — that it means only "basic economy" — would make the exclusion
narrower than the negation of the eligibility sentence and put the two sentences in direct conflict
for a regular uninsured economy passenger. The both-cabins reading is the only one that keeps the
section coherent.

## 3. The delayed-flight certificate requires the change or cancellation to have actually happened

**Text.** *"If the user complains about delayed flights in a reservation **and wants to change or
cancel the reservation**, the agent can offer a certificate as a gesture **after confirming the
facts and changing or cancelling the reservation**, ..."*

**Alternatives.**
(a) The wish alone is the trigger; "after changing or cancelling" is procedural advice about when in
    the conversation to say it.
(b) Both are preconditions: the user must want it, *and* the modification must have been carried
    out, before the certificate outcome is available.

**Reading: (b).** The sentence names the two things twice, in the condition ("wants to") and in the
timing clause ("after ... changing or cancelling"). Reading (a) makes the second mention pure
surplus. (b) also matches the section's overall posture, which is to withhold gestures until facts
are settled. Consequence: `/complaint/wantsChangeOrCancel` and `/reservation/changeOrCancelCompleted`
are separate conjuncts, and a delayed-flight complainant whose change has not yet been executed gets
`no-compensation` at that moment — the pack is intended to be re-evaluated after the modification.

## 4. Cancelled and delayed complaints are independent booleans, and a complaint that is both escalates

**Text.** The two grant sentences, which price the same reservation at $100/passenger and
$50/passenger respectively.

**Alternatives.**
(a) One enumerated fact `/complaint/type` with values `cancelled` / `delayed` / `other`, forcing the
    classifier to pick one — no conflict is ever possible, but the pack silently inherits whatever
    tie-break the classifier used.
(b) Two independent booleans; if both are true, the two grant rules name different outcomes, §8
    step 8 records `conflict`, and the configured escalation hands off to a human.
(c) Two booleans plus a hard-coded precedence (e.g. cancelled beats delayed).

**Reading: (b).** The section gives no precedence rule and no combination rule, so (c) would be me
inventing policy. (a) hides the same invention inside a fact. (b) is the only option that makes the
gap visible: a reservation that suffered both a cancellation and a delay is a case the section does
not price, and *"You should transfer the user to a human agent if and only if the request cannot be
handled within the scope of your actions"* is exactly the right disposal. Verified: this case
produces `unresolved` with reason `conflict` and a handoff request.

## 5. `onUnknown` is split — `escalate` on the grant rules, `ignore` on the denial rules and the exception

**Text.** *"Always confirms the facts before offering compensation."* plus *"Do not proactively
offer a compensation unless the user explicitly asks for one."*

**Alternatives.**
(a) `ignore` everywhere: any unavailable fact falls through to `fallbackOutcome: no-compensation`.
    Maximally conservative, never bothers a human — but silently denies a possibly-entitled user and
    leaves no trace of the fact that anything was unknown.
(b) `escalate` everywhere: any unavailable fact goes to a human. Turns the ordinary case of a user
    who never mentioned compensation into a transfer, because the denial rules would then be unknown
    on the same missing facts.
(c) Split: `escalate` on the two grant rules, `ignore` on `deny-not-requested`, `deny-ineligible`,
    `deny-other-reason` and the exclusion exception.

**Reading: (c).** An unavailable fact on a grant path means the agent literally cannot do what the
policy tells it to do — it can neither confirm the facts nor multiply by a passenger count it does
not have — and that is "cannot be handled within the scope of your actions". An unavailable fact on
a denial path cannot manufacture an entitlement, so ignoring it and letting the fallback deny is
safe. §7.1's strong conjunction makes this cheap in practice: a user who never asked for
compensation makes `/request/compensationExplicitlyRequested == true` false, which makes the whole
grant `all` **false**, not unknown, so the dominant case never escalates. Verified against a
facts document containing only a membership level and a `false` request flag: `no-compensation`, no
handoff.

Consequence worth stating plainly: because `escalate` blocks the fallback (§8 step 7), a missing
membership level or a missing passenger count on an otherwise-granting case produces `unresolved`
rather than `no-compensation`. That is the intended trade.

## 6. `escalation.triggers` is `["unknown", "conflict"]` and nothing else

**Alternatives.** Include `no-match` and `not-applicable` as belt-and-braces.

**Reading: neither can occur in this pack** — `fallbackOutcome` is set, so §8 step 10 never yields
`no-match`, and `applicability` is omitted, so §6/§8 step 1 never yields `not-applicable`. Listing
dead triggers would advertise handoff behaviour the pack cannot produce. `missing-required-evidence`
is likewise excluded because the single evidence requirement is `required: false` by design (see
DECISIONS #7).

## 7. `facts-confirmed` is `required: false` and consumed only by the grant rules

**Text.** *"Always confirms the facts before offering compensation."*

**Alternatives.**
(a) `required: true`. §8 step 2/5 then makes *every* evaluation without a confirmation attestation
    `unresolved`/`missing-required-evidence`, including cases where the answer is an easy "no".
(b) `required: false`, referenced by `evidence-present` inside the two grant rules only.

**Reading: (b).** The sentence conditions *offering*, not deciding. Under (a), a caller who simply
wants to know whether a regular economy passenger qualifies would be forced into a handoff. Under
(b), the attestation gates exactly what the sentence gates. Verified: with the attestation
explicitly `absent`, an otherwise-qualifying gold-member cancelled-flight complaint resolves to
`no-compensation` rather than to a certificate.

## 8. `/reservation/passengerCount` is gated with `not-equals null` rather than an ordered comparison

**Alternatives.**
(a) `{"operator": "greater-than-or-equal", "value": "1"}`. Semantically nicer, but §2.2 and §7.4 are
    explicit that this draft "assigns no portable ordering to those decimal strings" and that
    structural acceptance of an ordered condition "does not imply executable support" — a conforming
    evaluator is free to return `unknown`, which under `onUnknown: escalate` would escalate every
    grant.
(b) `not-equals null`, which under §7.4's type-preserving equality is `true` for any present
    non-null value and `unknown` for an unresolvable pointer.
(c) Do not read the passenger count at all; leave the multiplier purely descriptive.

**Reading: (b).** It is portable, and it does the one job that matters: stop the pack from naming a
certificate outcome whose amount cannot be computed. (c) would let the pack say "offer a certificate
of $100 x ?" which is not a usable answer.

## 9. Outcome amounts live in outcome descriptions and an optional namespaced extension

Core outcomes are labels, not computed values. I put the multipliers in the outcome `description`
and in an optional `io.onword.compensation` extension (`instrument`, `amountPerPassengerUsd`,
`formula`). It is deliberately **not** listed in `metadata.requiredExtensions`: per §9 an optional
extension must not change Core semantics, and a consumer that ignores it still gets the amount from
the human-readable description. Declaring it required would make the pack "structurally readable but
not fully interpretable" for every consumer that has not heard of it, for no semantic gain.

## 10. The compensation instrument is a certificate, not a refund to the original payment method

Both grant sentences say *"offer a certificate as a gesture"*. I did not model any interaction with
*"The remaining amount of a travel certificate is not refundable."* (## Book flight) or with the
5-7-business-day refund route (## Cancel flight), because those are outside the assigned section.
The outcomes therefore name a certificate and only a certificate.

## 11. Cabin class is read once, at reservation level

*"flies business"* and *"flies (basic) economy"* are per-reservation, not per-segment, because
*"Cabin class must be the same across all the flights in a reservation"* (## Book flight) and
*"Cabin class must remain the same across all the flights in the same reservation"* (## Modify
flight). So a single `/reservation/cabinClass` pointer is sufficient and no per-flight
reconciliation is needed. This is the one place where I leaned on the context sections, and only to
establish that a simpler encoding is safe.
