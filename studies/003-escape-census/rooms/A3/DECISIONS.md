# DECISIONS — A3 "May the cabin be changed?"

Numbered interpretation choices made while encoding **Modify flight → Change cabin** of
`reference/policy.md` as a JPS `0.1.0-draft` pack.

---

## 1. "already been flown" means "has taken off", including a flight still in the air

**Text.** "Cabin cannot be changed if any flight in the reservation has already been flown."

**Alternatives.**
(a) *Flown* = has taken off, i.e. status `flying` **or** already landed.
(b) *Flown* = has landed, i.e. completed; a flight currently `flying` would not count.
(c) *Flown* = scheduled departure time is in the past, regardless of status.

**Reading chosen.** (a).

**Why.** The Domain Basic section defines the status vocabulary in exactly these terms: "If the
status is **flying**, the flight has taken off but not landed." The word the policy reuses is
"flown", the past participle of the same verb it uses for "taken off". Reading (b) would let a user
change the cabin of a segment while the aircraft is airborne, which the restriction is plainly
meant to prevent. Reading (c) ignores `delayed`, which the domain says means the flight has *not*
taken off. The consequence is that the pack cannot read this from records directly — see
`FACTS-LEDGER.md`, where `/reservation/anyFlightFlown` is marked **computed** and explicitly
flagged as requiring interpretation of the policy term.

---

## 2. The already-flown case is a **denial**, not a transfer to a human

**Text.** "Cabin cannot be changed if any flight in the reservation has already been flown."

**Alternatives.**
(a) Outcome `deny`: the agent refuses the cabin change.
(b) Escalate: transfer to a human agent, by analogy with the Cancel flight section, which says
"If any portion of the flight has already been flown, the agent cannot help and transfer is
needed."

**Reading chosen.** (a).

**Why.** The two sections use deliberately different language for the same trigger. Cancel flight
says the agent "cannot help and transfer is needed"; Change cabin says the cabin "cannot be
changed". Denying a request *is* within the scope of the agent's actions — the preamble says "You
should deny user requests that are against this policy" and restricts transfer to the case where
"the request cannot be handled within the scope of your actions". Importing the cancel-flight
transfer into the cabin subsection would be reading in a sentence that is not there.

---

## 3. Single-segment cabin changes are denied, not silently widened to the whole reservation

**Text.** "Cabin class must remain the same across all the flights in the same reservation;
changing cabin for just one flight segment is not possible."

**Alternatives.**
(a) Outcome `deny` when the request covers fewer than all segments.
(b) Treat a single-segment request as a request to change every segment and proceed.

**Reading chosen.** (a).

**Why.** "is not possible" is a prohibition on the request as made. Silently widening the request
would change its price consequence without the user's agreement, and the preamble requires the
agent to "list the action details and obtain explicit user confirmation (yes) to proceed" before
touching the booking database. The agent can of course re-ask the user for a whole-reservation
change; that is a new request and a new evaluation of this pack.

---

## 4. The two prohibitions are encoded as `force-outcome` **exceptions**, the price clauses as rules

**Text.** Bullet 1 states a prohibition; bullet 2 begins "**In other cases**, all reservations,
including basic economy, can change cabin…".

**Alternatives.**
(a) Exceptions with effect `force-outcome: deny` for bullets 1 and 3; rules for bullets 4 and 5.
(b) Five plain rules, with each allow rule repeating "not flown AND covers all segments" inside its
`when`.

**Reading chosen.** (a).

**Why.** "In other cases" is the policy's own way of saying that bullet 2 is the general permission
and bullet 1 is carved out of it — which is exactly the shape of a typed exception. Under §8 of the
core spec a compatible forced outcome is produced without evaluating normal rules, so the allow
rules do not have to restate the prohibitions, and two `force-outcome` exceptions naming the same
outcome (`deny`) are compatible rather than a `conflict`. Design (b) is behaviourally equivalent but
duplicates each prohibition three times, so any future edit could desynchronise them.

---

## 5. Equal prices get their own outcome, `allow-no-money-movement`

**Text.** Bullet 4 is conditioned on "higher than the original price"; bullet 5 on "lower than the
original price".

**Alternatives.**
(a) A third allow outcome for the equal-price case: permitted, no money moves.
(b) No rule at all for equal prices, so the case falls through to `no-match` and escalates.
(c) A `fallbackOutcome` of `allow-no-money-movement`.

**Reading chosen.** (a).

**Why.** Bullet 2 grants the permission unconditionally in "other cases"; bullets 4 and 5 only
attach a money consequence. When neither money clause fires, the permission still stands, so the
honest answer to "may the cabin be changed?" is yes with nothing to pay or refund — not "I don't
know" (b). Option (c) was rejected because a fallback would also catch *unmodelled* price
situations (e.g. a currency the pricing step could not compare), quietly answering "permitted, no
money moves" for cases the policy never addressed. An explicit `equal` condition fails loudly
instead.

---

## 6. `applicability` requires a cabin-change request that does not change flights

**Text.** "In other cases, all reservations, including basic economy, can change cabin **without
changing the flights**."

**Alternatives.**
(a) Applicability conjunct `/request/changesFlights == false`, so a combined flight+cabin request is
`not-applicable` to this pack.
(b) A `deny` rule for combined requests.
(c) Ignore the clause as merely descriptive.

**Reading chosen.** (a).

**Why.** The clause describes the shape of the transaction this subsection governs. A request that
also changes flights is governed by the *Change flights* subsection (which has its own basic-economy
prohibition and its own payment rule), and this pack was scoped to Change cabin only. Answering
`not-applicable` routes the question to the right body of rules; a `deny` (b) would wrongly assert
that the combined request is forbidden, which the policy nowhere says.

`not-applicable` is deliberately **not** in `escalation.triggers`: it means "ask a different pack",
not "fetch a human".

---

## 7. Basic economy is encoded by the *absence* of a condition

**Text.** "In other cases, **all** reservations, **including basic economy**, can change cabin…"

**Alternatives.**
(a) No cabin-class condition anywhere in the pack.
(b) An explicit rule or exception mentioning basic economy.

**Reading chosen.** (a).

**Why.** The clause is an express non-restriction, written to head off the reader's memory of
"Basic economy flights cannot be modified" in the *Change flights* subsection. Since this pack
encodes only Change cabin, the *Change flights* prohibition is not in it, and the correct encoding
of "including basic economy" is that no rule, exception, or applicability condition reads the
reservation's current or requested cabin class at all. This is recorded so that a later editor does
not "helpfully" add one.

---

## 8. Identification is modelled as **required evidence**, not as facts

**Text.** "First, the agent must obtain the user id and reservation id. - The user must provide
their user id. - If the user doesn't know their reservation id, the agent should help locate it
using available tools." (Modify flight preamble, the immediate parent of the assigned subsection.)

**Alternatives.**
(a) Two required `evidenceRequirement`s (`user-id`, `reservation-id`).
(b) Two fact pointers with equality conditions.
(c) Omit as out of the assigned subsection.

**Reading chosen.** (a).

**Why.** These are proof obligations whose *absence prevents normal resolution* — the core spec's
own definition of a required evidence requirement — rather than propositions the rules test. The
sentence sits in the preamble of the section the assigned subsection belongs to and applies to every
modification including a cabin change, so (c) would drop a precondition that genuinely gates this
decision. `missing-required-evidence` is in `escalation.triggers` only so the state is visible; in
practice the agent's first move is to ask the user, not to transfer.

---

## 9. `onUnknown: escalate` everywhere

**Alternatives.**
(a) `escalate` on both exceptions and all three rules.
(b) `ignore` on the allow rules, so an unknown price direction falls through to `no-match`.

**Reading chosen.** (a).

**Why.** Every fact this pack reads is material: an unknown `anyFlightFlown` could mask a
prohibition, an unknown segment scope could mask a prohibition, and an unknown price direction means
the agent cannot state what the user owes or is owed. Under §8 an `ignore` would erase the unknown
from the decision and, here, would still end in an unresolved `no-match` — so (b) produces the same
handoff with a less diagnostic reason. `escalate` retains the reason `unknown` and the contributing
rule ids in the trace.

There is deliberately **no** `fallbackOutcome`: no reading of the subsection supplies a default
answer for a case none of its five bullets covers.

---

## 10. Price comparison is a fact enumeration, not an ordered decimal condition

**Text.** "If the price after cabin change is higher than the original price…" / "…lower than the
original price…"

**Alternatives.**
(a) One computed fact `/pricing/priceDifferenceDirection` ∈ {`higher`, `lower`, `equal`}, tested
with `equals`.
(b) A decimal-string difference tested with `greater-than "0"` / `less-than "0"`.

**Reading chosen.** (a).

**Why.** §2.2 and §7.4 of the core spec are explicit that "this draft nevertheless assigns no
portable ordering to those decimal strings" and that "structural acceptance of an ordered condition
does not imply executable support". Encoding the comparison as an ordered condition would make the
pack's meaning depend on an evaluator's undocumented local behaviour. Pushing the comparison into a
computed fact keeps the pack portable and makes the arithmetic visible in the facts ledger, where it
belongs.

---

## 11. The user-confirmation gate and the modify-flight payment rule are left out

**Text.** Preamble: "Before taking any actions that update the booking database (booking, modifying
flights, editing baggage, changing cabin class, or updating passenger information), you must list
the action details and obtain explicit user confirmation (yes) to proceed."
Modify flight → Payment: "If the flights are changed, the user needs to provide a single gift card
or credit card for payment or refund method."

**Alternatives.**
(a) Leave both out of the pack.
(b) Add `user-confirmation` as required evidence.
(c) Add a payment-method rule for the collect/refund outcomes.

**Reading chosen.** (a).

**Why.** The confirmation sentence is a global execution gate, not part of the Change cabin
subsection, and the pack's question is "may the cabin be changed?", not "may I call the API now?".
Folding it in (b) would conflate permission with authorisation and would make the pack answer
`unresolved` for a change that is plainly permitted but not yet confirmed.
The Payment bullet excludes itself by its own terms: it fires only "if the **flights** are changed",
and this pack's applicability requires that the flights are *not* changed. The result is a real gap
in the source policy — a cabin change can require a payment or a refund with no stated rule about
which payment method to use — and it is recorded in `RESIDUE.md` rather than papered over.
