# DECISIONS — A5 "May the passengers be modified?"

Assigned section, verbatim and complete:

> **Change passengers:**
> - The user can modify passengers but cannot modify the number of passengers.
> - Even a human agent cannot modify the number of passengers.

Two sentences. Everything below is an interpretation choice forced by encoding them.

---

## 1. What counts as "the assigned section"

**Text.** The assignment names *Modify flight -> Change passengers*. The `Modify flight` section
also opens with an identification preamble ("First, the agent must obtain the user id and
reservation id…"), and the document preamble carries a global gate ("Before taking any actions that
update the booking database (booking, modifying flights, editing baggage, changing cabin class, or
**updating passenger information**), you must list the action details and obtain explicit user
confirmation (yes) to proceed.").

**Alternatives.** (a) Encode only the two Change-passengers bullets. (b) Also encode the
`Modify flight` identification preamble as a guard. (c) Also encode the global confirmation gate,
since it names "updating passenger information" explicitly.

**Chosen: (a).** The brief says the rest of the policy is context and to encode only this decision.
Both (b) and (c) are cross-cutting preconditions that apply identically to the cabin, baggage and
flight-change packs; duplicating them into this pack would make the same obligation appear N times
across the census with N slightly different encodings.

**Why it is still safe.** Neither omitted rule can turn a refusal into a permission — they are both
*additional* gates on acting. To keep that visible to a consumer, the `allow-passenger-modification`
outcome description states in prose that it "is not an authorization to call the booking-update API,
which remains subject to the policy's separate identification and explicit-user-confirmation
requirements."

## 2. Scope of "modify passengers" — which passenger attributes?

**Text.** "The user can modify passengers…"

**Alternatives.** (a) Only corrections to the details of the *same* human beings (fix a misspelled
name, fix a date of birth). (b) Any change to the passenger records, including replacing one
traveller with a different person, as long as the count holds.

**Chosen: (b), the literal reading.** The sentence says "modify passengers", not "correct passenger
details", and it states exactly one limit — the number. Reading in an unstated identity constraint
would be writing a sensible policy rather than encoding this one. Consequence, encoded and
deliberate: swapping Aarav Ahmed for Noah Ahmed on a three-passenger booking is **permitted** by
this pack. The example facts exercise precisely that case so the reading is visible rather than
buried.

## 3. "cannot modify the number of passengers" — refusal, not escalation

**Text.** "…cannot modify the number of passengers." + "Even a human agent cannot modify the number
of passengers."

**Alternatives.** (a) Outcome = refuse, terminal. (b) Outcome = escalate to a human, since the agent
cannot do it. (c) Refuse, but offer transfer on request.

**Chosen: (a).** The document's transfer rule is "transfer if and only if the request cannot be
handled within the scope of your actions", which alone would argue for (b). The second bullet exists
solely to close that door: a human agent has no more power here than the automated agent, so a
transfer would consume a human and still end in refusal. Encoded as the `force-outcome` exception
`count-change-not-overridable`, which under §8 step 6 produces the refusal *without evaluating the
normal rules*, plus an outcome description stating the refusal must not be transferred.

## 4. Keeping both a rule and an exception for the count bar

The rule `deny-count-change` and the exception `count-change-not-overridable` fire on the same fact
and name the same outcome, so the exception makes the rule unreachable in practice.

**Alternatives.** (a) Rule only — loses the "not overridable" force. (b) Exception only — the count
bar then has no rule, and the first policy bullet is only half-represented in `rules`.
(c) Keep both, one per bullet.

**Chosen: (c).** Each bullet gets its own representation with its own `sourceRefs`
(`policy-change-passengers-user` for the rule, `policy-change-passengers-human` for the exception),
which is what makes the citation trail auditable. §8 step 4 makes them compatible (same outcome), so
the redundancy is inert, not a `conflict`.

## 5. `onUnknown: escalate` everywhere

**Alternatives.** (a) `ignore` on both rules and the exception. (b) `escalate` on both rules and the
exception.

**Chosen: (b).** Both rules and the exception key off the single fact
`/derived/changesPassengerCount`. If that fact is unavailable, *nothing* in the pack is decidable —
the pack cannot tell a name correction from a passenger deletion. With `ignore` the run would fall
through to `no-match` (there is no fallback), which is also unresolved but discards the reason: a
reader of the trace would see "the pack matched nothing" instead of "the pack did not know". §8
explicitly notes `escalate` "records reason `unknown` and blocks both a candidate outcome and the
fallback", which is the honest description of this state. The escalation `message` tells the human
what they may do (clarify the roster) and what they still may not do (change the count).

## 6. No `fallbackOutcome`

**Alternatives.** (a) Fall back to `allow-passenger-modification`. (b) Fall back to
`refuse-passenger-count-change`. (c) No fallback.

**Chosen: (c).** (a) would permit an unclassified passenger change — the failure mode the second
bullet is most concerned about. (b) would silently refuse changes the first bullet permits. The
policy supplies no default for "we could not tell", so the pack supplies none and lets the result
stay `unresolved`.

## 7. No basic-economy restriction on passenger changes

**Text.** "Basic economy flights cannot be modified" appears under *Change flights*. *Change cabin*
then says "all reservations, **including basic economy**, can change cabin without changing the
flights."

**Alternatives.** (a) Read the basic-economy bar as a restriction on the whole `Modify flight`
section. (b) Read it as scoped to its own subsection.

**Chosen: (b).** The drafters demonstrably scope restrictions per subsection — the cabin subsection
would not need to say "including basic economy" if the bar were local to flight changes only by
accident. *Change passengers* is silent, so no cabin-class condition is encoded. The example facts
use a `basic_economy` reservation on purpose, so this reading is exercised, not assumed.

## 8. No flown-segment restriction

**Text.** "Cabin cannot be changed if any flight in the reservation has already been flown" — stated
under *Change cabin* only. *Cancel flight* likewise states its own flown-segment bar. *Change
passengers* states none.

**Chosen:** none encoded. Same reasoning as §7: where this policy wants a flown-segment condition it
writes one. Noted as a live risk — this is the reading with the largest gap between "what the text
says" and "what an operator probably wants" — but the brief is to encode the text.

## 9. Direction of the count change is not distinguished

"Modify the number of passengers" covers both adding and removing. One boolean, no add/remove
branch, no per-direction outcome. The five-passenger cap from *Book flight* is therefore also not
encoded: a count change is already barred, so the cap can never bind here.

## 10. No evidence requirements; inputs modelled as facts

**Alternatives.** (a) Declare the current roster and the requested roster as
`evidenceRequirements` with `required: true`. (b) Model everything as facts.

**Chosen: (b).** Core §7.5 states that this draft "does not define an evidence-manifest interchange
format", and §7.5 makes `evidence-present` `unknown` when a runtime cannot determine manifest
completeness. A `required: true` evidence requirement would therefore risk a permanent
`missing-required-evidence` block in a conforming runtime for inputs that are, in substance, plain
facts. Consequently there is no `evidence.example.json` and
`missing-required-evidence` is not among the escalation triggers.

## 11. Applicability, and why `not-applicable` is not an escalation trigger

Applicability is `all[ /request/action == "modify-reservation", /request/subject == "passengers" ]`.
A cabin change or a cancellation therefore yields a terminal `not-applicable` result rather than an
answer. `not-applicable` is deliberately **excluded** from `escalation.triggers`: a request this
pack does not cover is not thereby beyond the agent's scope — a sibling pack covers it — and the
policy's transfer rule fires only when the request "cannot be handled within the scope of your
actions".
