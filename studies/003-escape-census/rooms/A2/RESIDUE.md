# Residue — A2

Assigned section: **Modify flight → Change flights** of `reference/policy.md` (lines 109–113).
The subsection has four sentences; each is listed below.

---

**1.** > "Basic economy flights cannot be modified."

Fully represented. Encoded as the exception `basic-economy-not-modifiable`
(`when /reservation/cabinClass equals "basic economy"` → `force-outcome: change-denied`,
`onUnknown: escalate`). Using the exception machinery rather than a rule means the carve-out
short-circuits before the shape rules run, so a basic economy reservation is denied even when a
`preserves*` fact is missing — which matches the sentence's unconditional wording.

---

**2.** > "Other reservations can be modified without changing the origin, destination, and trip type."

Fully represented, but **split across the pack and three computed facts**.

- The permission half is the rule `permit-shape-preserving-change` → `change-permitted`.
- The prohibition half (the policy grants permission only for shape-preserving changes, and the
  preamble says "You should deny user requests that are against this policy") is the rule
  `deny-itinerary-shape-change` → `change-denied`, written as the exact three-valued negation of
  the permit condition so the two can never both be true or both be false.
- The word "Other" is represented by the exception firing first, so the rules only ever decide for
  non-basic-economy reservations.
- The comparison work behind "without changing the origin, destination, and trip type" is **pushed
  into three computed facts** (`/request/preservesOrigin`, `/request/preservesDestination`,
  `/request/preservesTripType`). The pack cannot express "compare the proposed itinerary's
  turnaround airport with the reservation's", so whoever assembles the facts document performs that
  policy-term interpretation. See FACTS-LEDGER.md for exactly what each requires.

---

**3.** > "Some flight segments can be kept, but their prices will not be updated based on the current price."

**Not represented as a condition or outcome — approximated as rationale text.** The sentence does
two things, neither of which is a gate on the assigned question:

- it *permits* keeping segments, which the pack already covers (keeping segments never changes
  origin, destination, or trip type, so it never blocks `change-permitted`); and
- it fixes the *price* of a kept segment at its original price. Pricing is downstream of "may the
  flights be changed?" and the pack declares no monetary outcome, so this half is carried only as
  provenance: source `policy-kept-segment-pricing` is cited by
  `permit-shape-preserving-change`, whose `rationale` states that kept segments keep their original
  prices. A pack that answered "what does this change cost?" would have to encode it properly.

---

**4.** > "The API does not check these for the agent, so the agent must make sure the rules apply before calling the API!"

**Partly represented; partly outside the format.**

- "The agent must make sure the rules apply" is encoded twice: as the required evidence requirement
  `verified-reservation-record` (absence yields `missing-required-evidence` and a handoff rather
  than a decision), and as `onUnknown: escalate` on both rules and on the exception, so an
  unconfirmed fact can never fall through to a permit.
- "The API does not check these for the agent" is a statement about the tool surface, and
  "before calling the API" is sequencing of an external action. Judgment Pack Core §6.4 says an
  outcome "is a declared result, not an authorization to perform an external action", so neither
  can be represented; the `change-permitted` outcome description says in prose that it is an
  eligibility result and that confirmation and payment still precede the write.

---

## Residue count

**2 sentences with residue** (sentence 3, mostly left out as out-of-question pricing; sentence 4,
partly unrepresentable as external-action sequencing). Sentences 1 and 2 are fully represented,
with sentence 2's comparison work delegated to computed facts.
