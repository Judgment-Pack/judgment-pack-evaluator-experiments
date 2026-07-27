# Interpretation decisions — A1 "Book flight"

## 1. Scope: the assigned section only, not the policy preamble

**Text.** The assignment names "## Book flight" and says the rest is context. The preamble
nevertheless contains two statements that bear directly on "May this booking be made?":
"Before taking any actions that update the booking database (booking, …), you must list the action
details and obtain explicit user confirmation (yes) to proceed", and, under Domain Basic → Flight,
"If the status is delayed or on time, the flight has not taken off, **cannot be booked**" /
"If the status is flying … cannot be booked".

**Alternatives.** (a) Encode the Book flight section only. (b) Also encode the confirmation gate and
the flight-status bookability gate, since a booking that fails either may not be made.

**Chosen: (a).** The assignment scopes the decision to one section, and importing constraints from
elsewhere would make this pack incomparable with the sibling packs that encode those sections.

**Consequence, stated plainly.** `book-allowed` therefore means "the Book flight section is
satisfied", not "call the booking API". The outcome description says so, and the flight's bookable
status and the explicit-confirmation gate are *not* checked by this pack. A deployment must apply
them separately.

## 2. Outcome vocabulary: allow / deny, with escalation kept off the outcome list

**Text.** The section states requirements ("must", "can have at most", "must already be") without
naming a result. The preamble supplies the disposition of a violation ("You should deny user
requests that are against this policy") and the transfer rule ("transfer … if and only if the
request cannot be handled within the scope of your actions").

**Alternatives.** (a) Two outcomes `book-allowed` / `book-denied`. (b) Add a third outcome
`transfer-to-human`. (c) Allow only, with everything else unresolved.

**Chosen: (a).** §6.7 is explicit that escalation "is not itself an outcome", so a transfer outcome
would misuse the format. Handoff is configured in the `escalation` object and reached through
`unresolved` results. Nothing in the Book flight section names a case that must go to a human, so no
`escalate` exception exists in the pack; the escalation object exists only to route the generated
reasons `missing-required-evidence`, `unknown`, `conflict`, `no-match`.

## 3. Rule shape: one allow rule that is the conjunction of the negated deny rules

**Alternatives.** (a) Deny rules only, `onUnknown: escalate`, `fallbackOutcome: book-allowed`.
(b) One allow rule (`onUnknown: escalate`) plus one deny rule per requirement
(`onUnknown: ignore`), no fallback.

**Chosen: (b),** at the cost of writing each condition twice. Under (a), §8 step 7 says an unknown
rule with `onUnknown: escalate` "blocks both a candidate outcome and the fallback", so a booking
with a *known* violation (six passengers) plus one unrelated unavailable fact would come back
`unresolved` instead of denied. Under (b) the allow rule goes false as soon as any requirement is
violated, the matching deny rule fires, and the unknown one is ignored — verified: six passengers
with `allMethodsInUserProfile` missing yields `book-denied`. Because the allow condition is exactly
the negation of every deny condition, "allow is false" always implies some deny rule is true, so no
`fallbackOutcome` is declared and a `no-match` result would signal a coverage bug rather than
silently allow or deny.

## 4. `onUnknown`: escalate on the allow rule, ignore on every deny rule

**Reading.** An unverified requirement must never be read as a satisfied requirement, so the only
rule that can produce permission escalates on unknown. A deny rule whose condition is unknown is
*not* evidence of a violation, so it is ignored — and it cannot cause a false allow, because the
same unknown also makes the allow rule unknown. Net effect: unavailable facts produce
`unresolved / unknown` and a handoff request, never a permission.

## 5. The insurance offer and the trip parameters are required evidence, though the text says "should"

**Text.** "The agent should ask if the user wants to buy the travel insurance." / "The agent should
then ask for the trip type, origin, destination."

**Alternatives.** (a) `required: false` (declared but inert). (b) `required: true`. (c) A deny rule
for "did not ask".

**Chosen: (b).** (c) is wrong — failing to ask yet is not a violation by the *user* and denial is
the wrong disposition. (a) would make the sentence unrepresented in substance. (b) yields
`unresolved / missing-required-evidence`, i.e. "cannot conclude that this booking may be made",
which is the honest state of an intake that has not finished. The `escalation.message` warns that
merely uncollected information should be collected from the user rather than transferred, because
the policy transfers "if and only if the request cannot be handled within the scope of your
actions".

## 6. "At most N" encoded as membership in an explicit set, not as an ordered comparison

**Text.** "at most five passengers", "at most one travel certificate", "at most one credit card",
"at most three gift cards".

**Alternatives.** (a) `less-than-or-equal` with the decimal-string operands `"5"`, `"1"`, `"3"`.
(b) `in [1,2,3,4,5]`, `in [0,1]`, `in [0,1,2,3]`.

**Chosen: (b).** §2.2 and §7.4 warn that this draft "assigns no portable ordering to those decimal
strings" and that structural acceptance of an ordered condition "does not imply executable support",
and the operand would be a string while the fact is a JSON number. Enumerating the admissible counts
is exact for these small bounds and portable. Side effect, deliberate: `in [1,2,3,4,5]` also denies a
zero-passenger reservation, which the section presupposes but never states.

## 7. The checked-bag table encoded as nine literal rule branches rather than one derived fact

**Alternatives.** (a) A single computed fact `freeBagAllowanceCorrect: true|false`. (b) Nine
membership × cabin branches inside `deny-free-checked-bag-allowance-mismatch`, comparing the
reservation's `freeCheckedBagsPerPassenger` against the table.

**Chosen: (b).** (a) would hide the whole policy inside a fact whose producer must apply the policy —
the exact failure mode the ledger asks to expose. (b) keeps the table auditable in the pack and
leaves only a draft-reservation number as input. The branch set assumes one cabin class per
reservation, which the section itself guarantees ("All passengers must fly the same flights in the
same cabin", "Cabin class must be the same across all the flights").

## 8. The two prices ($50 per extra bag, $30 per passenger insurance) treated as booking terms

**Alternatives.** (a) Residue — they are pricing information, not permission conditions. (b) Deny
rules that fire when the draft reservation prices these differently.

**Chosen: (b),** guarded so they only bite when they apply (`extraCheckedBags != 0`;
`travelInsurance.purchased == true`). A reservation that charges other amounts is not the
reservation the section describes, so "may this booking be made *as proposed*" is no. Logged as a
genuine judgment call: reading (a) is defensible and would move two rules into RESIDUE.md.

## 9. Applicability keyed on the request type

`/request/type == "book-flight"` delimits the pack, matching the policy's own division into book /
modify / cancel flows. `not-applicable` is deliberately **not** an escalation trigger: a cancel
request is another pack's business, not a reason to fetch a human.

## 10. Fact vocabulary is pre-chewed on purpose

Most inputs are booleans and counts (`cabinClassUniformAcrossFlights`, `travelCertificateCount`, …)
rather than the raw reservation object. JPS 0.1.0-draft conditions cannot iterate a list, count
members, or compare elements pairwise, so any per-segment or per-passenger requirement must arrive
already reduced. The cost is recorded honestly: 12 of 16 pointers are `computed`, and the two that
require applying policy judgment rather than arithmetic (`onlyBagsUserRequested`,
`freeCheckedBagsPerPassenger`) are called out in FACTS-LEDGER.md.
