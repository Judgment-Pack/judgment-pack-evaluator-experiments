# DECISIONS — A4 "May baggage/insurance be modified?"

Assigned text (verbatim, `reference/policy.md`, "Modify flight" → "Change baggage and insurance"):

> Change baggage and insurance:
> - The user can add but not remove checked bags.
> - The user cannot add insurance after initial booking.

Two bullets, two verbs, and a great deal of silence. Every choice below is about that silence.

---

## 1. The pack decides one requested change at a time, not a whole conversation

**Text.** The subsection speaks of "the user can add" / "the user cannot add" — individual acts, not
a bundle.

**Alternatives.** (a) One evaluation per request, where a single request may touch both bags and
insurance. (b) One evaluation per requested change, selected by `/request/target`.

**Chosen: (b).** Under (a), a user who asks to add a bag *and* add insurance makes two true rules
name two different outcomes; §8 step 8 turns that into `conflict` → unresolved → a human transfer,
which the policy plainly does not intend (the agent should add the bag and refuse the insurance).
The format has one outcome per evaluation, so the honest fix is to narrow the unit of decision.
`applicability` therefore requires `/request/target` ∈ {`checked-bags`, `travel-insurance`}, and a
mixed request is evaluated twice. Documented in `description` and in the decision `intent`.

## 2. "remove" includes a per-passenger reduction even when the reservation total is unchanged

**Text.** "The user can add but not remove checked bags."

**Alternatives.** (a) Compare only the reservation-wide total. (b) Treat a reduction for *any*
passenger as a removal, even if another passenger gains a bag.

**Chosen: (b).** Baggage is held per passenger (the booking section allocates free bags per
passenger). Moving a bag from passenger A to passenger B removes a checked bag from A. Reading (a)
would let a removal through under cover of arithmetic. (b) is the conservative reading of a
prohibition. This interpretation lives inside the computed fact
`/request/checkedBags/effect`, and the fact ledger flags it as policy-interpreting.

## 3. A request that both adds and removes is classified as a removal, and denied

**Alternatives.** (a) Approve the add and deny the remove (two outcomes — impossible here, see #1).
(b) Deny the whole thing. (c) Escalate.

**Chosen: (b).** The request as stated is partly against the policy, and the preamble says "You
should deny user requests that are against this policy." Denying is also recoverable: the user can
restate the request as a pure addition, which the pack then permits.

## 4. No `fallbackOutcome`; anything in scope that matches no rule is `no-match` → human

**Text.** The subsection authorizes exactly one thing and forbids exactly one thing. It says nothing
about, e.g., a baggage request that changes nothing, or a re-statement of the current baggage count.

**Alternatives.** (a) `fallbackOutcome: deny…` — deny by default. (b) Invent a
`no-change-required` outcome. (c) No fallback, so §8 step 10 yields `unresolved` with reason
`no-match`, which `escalation.triggers` routes to a human.

**Chosen: (c).** (a) manufactures a prohibition the text does not contain; (b) manufactures an
outcome the text does not contain. (c) says exactly what is true — this subsection does not decide
that case — and the preamble's transfer rule ("if and only if the request cannot be handled within
the scope of your actions") is the policy's own answer for it.

## 5. Removing existing travel insurance is escalated, not denied and not permitted

**Text.** "The user cannot add insurance after initial booking." Nothing about removal or refund of
insurance.

**Alternatives.** (a) Deny — nothing authorizes the agent to do it. (b) Permit — nothing forbids it.
(c) Escalate.

**Chosen: (c)**, encoded as the explicit exception `insurance-removal-out-of-scope` with effect
`escalate` rather than left to the `no-match` path of #4, because it is a foreseeable, nameable case
and deserves its own trace entry and its own citation. (a) reads a prohibition into silence; (b)
reads an authorization into silence, and insurance is a paid product whose removal implies a refund
question the subsection never opens. The preamble's "if and only if" transfer test fits: the agent
has no rule for it.

## 6. "after initial booking" means "on an existing reservation", full stop

**Text.** "The user cannot add insurance after initial booking."

**Alternatives.** (a) A grace period — e.g. still the same conversation, or within 24 hours of
booking (the cancellation section does use a 24-hour window). (b) Any moment once the reservation
exists.

**Chosen: (b).** The sentence names an event ("initial booking"), not a window; the 24-hour window
appears only under "Cancel flight" and is not imported here. Encoded structurally rather than as a
timestamp comparison: `applicability` requires `/request/phase == "post-booking-modification"`, so
the pack simply does not apply to insurance purchased during booking (that is the "Book flight"
section's business).

## 7. Asking to "add" insurance to a reservation that already has it is not a denial

The computed fact reports `no-change` in that case, so `add-insurance-denied` is false and the
result is `no-match` → human (per #4). Refusing a user who already has what they asked for would be
a misleading denial, and inventing an "already satisfied" outcome would exceed the text.

## 8. The basic-economy restriction is *not* applied to baggage or insurance

**Text.** "Basic economy flights cannot be modified" appears under "Change flights", a sibling
subsection. The policy shows it knows how to extend a restriction across subsections when it wants
to: "In other cases, all reservations, including basic economy, can change cabin".

**Chosen:** treat the restriction as local to flight changes. The pack has no cabin-class condition,
so a basic-economy passenger may add checked bags. The alternative — reading "basic economy cannot
be modified" as a blanket rule over the whole "Modify flight" section — is defensible in isolation
but is contradicted by the cabin subsection's explicit carve-in and would silently import a rule my
assigned section does not state.

## 9. The "already flown" restriction is likewise not imported

"Cabin cannot be changed if any flight in the reservation has already been flown" is stated for
cabin only. The assigned subsection sets no time bound on baggage changes, so the pack sets none.
Flagged here because a sensible policy probably would bound it; the instruction is to encode what
the text says.

## 10. Allowance and pricing are out of scope

The free checked-bag allowance table and "Each extra baggage is 50 dollars" live under "Book
flight". The assigned subsection is silent about how many bags may be added and what they cost, so
the pack decides permissibility only and says so in the `permit-add-checked-bags` description. No
rule caps the number of added bags.

## 11. The confirmation duty is recorded, not encoded as a condition

The preamble requires listing action details and obtaining explicit "yes" before "editing baggage".
That is a precondition for *execution*, and §6.4 is explicit that an outcome "is not an
authorization to perform an external action". Making confirmation a condition of
`permit-add-checked-bags` would conflate "may this be done" with "may this be done right now", and
an unconfirmed request would fall to `no-match` → human transfer, which is wrong (the correct
behaviour is to ask the user again). It is carried in the outcome description instead.

## 12. `onUnknown: escalate` on all three rules

The policy repeatedly insists the agent verify before calling the API ("The API does not check these
for the agent, so the agent must make sure the rules apply before calling the API!") and transfers
whatever it cannot handle. If the pack cannot tell whether a change is an increase or a decrease, it
must neither approve nor deny. `ignore` would let an unknown quietly become "no candidate" and, with
no fallback, still reach a human — but it would erase the reason. `escalate` records `unknown`
explicitly. Note that each rule guards its `/request/…/effect` test behind a `target` equality test
inside `all`, so an absent pointer for the *other* target is harmless (§7.1: `all` is false if any
child is false).

## 13. The escalate exception uses `onUnknown: ignore`

If `/request/insurance/effect` is unknown on an insurance request, `add-insurance-denied` already
escalates (#12). Setting the exception to `escalate` as well would add a second, redundant blocking
reason for the same missing datum without changing the destination.

## 14. `escalation.triggers` deliberately omits `not-applicable`

A `not-applicable` result means the request is an initial booking, a flight change, a cabin change,
or a passenger change — another section's decision, not a human's. Triggers are
`missing-required-evidence`, `unknown`, `conflict`, `no-match`. The mandated handoff line is carried
verbatim in `escalation.message`.

## 15. The evidence requirement is `required: false`

`current-reservation-record` is genuinely needed for a baggage decision, but §8 step 2 checks
required evidence *globally*, before rules. Marking it required would emit
`missing-required-evidence` on requests that do not need it. It is declared, referenced from the
rules that consume it (`evidenceRequirementRefs`), and left non-required; its absence surfaces
naturally as an `unknown` computed fact, which escalates via #12.

## 16. Two distinct denial outcomes rather than one generic `deny`

`deny-remove-checked-bags` and `deny-add-insurance` cite different sentences and require different
explanations to the user. Rules are mutually exclusive by construction (#1), so distinct outcomes
create no conflict risk.
