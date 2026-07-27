# RESIDUE — A4

Assigned section, in full:

> Change baggage and insurance:
> - The user can add but not remove checked bags.
> - The user cannot add insurance after initial booking.

No sentence was dropped. Both are represented by rules in `pack.json`. Two of them are only
*partly* representable inside the pack, because the operative distinction each one draws cannot be
written as a JPS condition; the residue is that displaced fragment, listed below.

---

## 1. "The user can add but not remove checked bags."

**Represented by:** `add-checked-bags-permitted` → `permit-add-checked-bags`, and
`remove-checked-bags-denied` → `deny-remove-checked-bags`.

**Displaced fragment:** the words *add* and *remove* themselves.

**What I did instead:** pushed into the computed fact `/request/checkedBags/effect`.

**Why it could not stay in the pack.** "Add" and "remove" are relations between the requested
baggage configuration and the reservation's stored one. A JPS `fact` condition compares exactly one
JSON Pointer against a literal value (§7.4); there is no pointer-to-pointer comparison and no
arithmetic. "requested count > recorded count" is therefore not expressible. The pack can only read
a pre-computed verdict string.

Two sub-questions the sentence leaves open are consequently answered *outside* the pack, by whoever
computes that string:

- whether "remove" is measured reservation-wide or per passenger (I chose per passenger as well —
  DECISIONS.md §2);
- what a request that simultaneously adds and removes counts as (I chose "removal" → denied —
  DECISIONS.md §3).

Both are policy interpretation, not arithmetic, and both are flagged as such in FACTS-LEDGER.md.

## 2. "The user cannot add insurance after initial booking."

**Represented by:** `add-insurance-denied` → `deny-add-insurance`, scoped by `applicability`.

**Displaced fragment:** the word *add*.

**What I did instead:** pushed into the computed fact `/request/insurance/effect`, which must decide
whether a request counts as an addition at all — specifically, whether asking for insurance the
reservation already carries is an "add" (I chose no — DECISIONS.md §7).

**What stayed in the pack:** the temporal qualifier "after initial booking" is *not* displaced. It
is encoded structurally as `applicability` requiring `/request/phase == "post-booking-modification"`,
so an initial-booking insurance purchase yields `not-applicable` rather than a denial.

## 3. The heading, "Change baggage and insurance:"

**Represented by:** the pack's `applicability` restricting `/request/target` to `checked-bags` or
`travel-insurance`, and by the decision `question`.

Listed only for completeness; it is a label, not a rule.

---

## Not residue, but worth recording: the section's silences

These are not sentences I failed to encode — they are cases the section never addresses. Each is
routed to a human rather than guessed at, and each is argued in DECISIONS.md:

- removing or cancelling existing travel insurance → escalate exception `insurance-removal-out-of-scope` (§5);
- a baggage or insurance request that changes nothing → `no-match` → escalate (§4, §7);
- whether the basic-economy modification ban reaches baggage → held not to (§8), so no condition encodes it;
- whether an already-flown flight blocks a baggage change → the section sets no time bound, so neither does the pack (§9);
- how many bags may be added and at what price → "Book flight" material, outside this decision (§10);
- the preamble's explicit-confirmation duty for "editing baggage" → an execution precondition, carried in the outcome description rather than as a rule condition (§11).
