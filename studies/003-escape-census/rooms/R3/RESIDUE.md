# Residue — R3, "Modify pending order → Modify items"

Every sentence of the assigned subsection, quoted verbatim, with what happened to it. Sentences
that are fully represented in `pack.json` are marked **represented** and are not residue; the
residue count at the bottom counts only the sentences (or sentence clauses) that could not be
represented.

The assigned subsection is the six-sentence block under `### Modify items` (policy.md lines
110–114). One sentence from the parent `## Modify pending order` section is also discussed, because
sentence 5 of the subsection reaches back into it.

---

## 1

> "This action can only be called once, and will change the order status to 'pending (items modifed)'."

**Split.**

- *"This action can only be called once"* — **represented**, as rule `deny-when-items-already-modified`
  (`/order/status equals "pending (items modifed)"` → deny). The once-only limit is observable only
  through the status the previous call left behind, which is exactly what this sentence says the
  call leaves behind.
- *"and will change the order status to 'pending (items modifed)'"* — **RESIDUE: left out.** This is
  a statement about the *effect* of executing the action, not a condition on whether it may be
  taken. JPS Core outcomes are declared results and explicitly not authorizations to perform an
  external action or descriptions of state mutation (§6.4), so there is nowhere in the pack to put
  a post-condition. It survives only as prose inside the `deny-when-items-already-modified`
  rationale and the `policy-modify-items-once` source excerpt.

## 2

> "The agent will not be able to modify or cancel the order anymore."

**RESIDUE: left out (carried as rationale only).**

Two things make this unrepresentable here. First, it is a statement about the agent's future
capability, not a condition on the present decision. Second, half of it is about a *different*
decision — whether the order may be **cancelled** — which belongs to the `## Cancel pending order`
pack, not this one. The modify half is the justification for rule
`deny-when-items-already-modified` and for that rule's phrasing, and it is quoted verbatim in the
`policy-modify-items-once` source citation, but the pack asserts nothing about cancellation.

See DECISIONS #3 for why this sentence's "will not be able to" was read as grounds for a **deny**
rather than for an `escalate` exception.

## 3

> "So you must confirm all the details are correct and be cautious before taking this action."

**RESIDUE: approximated / partly pushed into the resolution model.**

- *"you must confirm all the details are correct"* — approximated by the shape of the pack rather
  than by any single condition: `allow-when-all-conditions-met` is a strong conjunction of every
  stated precondition, and it carries `onUnknown: escalate`, so the allow outcome is produced only
  when every detail is affirmatively established and never when one is merely undetermined. That is
  the closest machine-readable analogue of "confirm all the details are correct", but it is weaker
  than the text: the policy addresses the agent's diligence in an open-ended way ("all the
  details"), while the pack can only enumerate the details the subsection happens to name.
- *"and be cautious"* — **left out.** A disposition of the agent, with no truth condition and no
  outcome. Not representable in any JPS construct. It is recorded in the
  `policy-modify-items-caution` source excerpt and it motivated two design choices logged in
  DECISIONS (#4 escalate-on-unknown for the allow rule, #5 no fallback outcome).

## 4

> "In particular, remember to remind the customer to confirm they have provided all the items they want to modify."

**Split.**

- *"remember to remind the customer"* — **RESIDUE: left out.** This is a conversational obligation
  on the agent (say a thing to the user), not a condition on whether the modification is permitted.
  A Judgment Pack decides a question; it does not script dialogue, and §6.1 forbids embedding
  prompts.
- *"to confirm they have provided all the items they want to modify"* — **represented**, as the
  requester fact `/modification/customerConfirmedItemListComplete`, required by
  `allow-when-all-conditions-met` and negated by `deny-when-item-list-not-confirmed-complete`. The
  pack therefore captures the *result* of the reminder but not the duty to issue it.

## 5

> "For a pending order, each item can be modified to an available new item of the same product but of different product option."

**Represented, with the quantifier pushed into computed facts.**

The status gate ("For a pending order") is rule `deny-when-order-not-pending` plus the
`/order/status equals "pending"` conjunct of the allow rule. The three item-level tests are the
computed facts `/modification/allNewItemsAvailable`, `/modification/allNewItemsSameProduct`, and
`/modification/allNewItemsDifferentOption`, each backed by a deny rule.

**Partial residue:** the word *"each"* is a universal quantifier over the requested substitutions,
and JPS `0.1.0-draft` fact conditions address a single JSON Pointer with no iteration, `forall`, or
array-mapping operator. The quantification is therefore not in the pack at all — it has been
**pushed into computed facts**, whose definitions in FACTS-LEDGER.md carry the "for every pair"
obligation. A consumer that fed the pack a per-item boolean instead of an all-items boolean would
get a silently wrong answer, and the pack cannot detect that.

## 6

> "There cannot be any change of product types, e.g. modify shirt to shoe."

**Represented** (as the negative form of the same-product test): rule
`deny-when-product-type-changes` on `/modification/allNewItemsSameProduct equals false`.

**Partial residue:** the example *"e.g. modify shirt to shoe"* is illustrative and is not encoded;
nothing in the pack distinguishes a shirt from a shoe. The pack relies entirely on the computed
fact's definition of "same product" (same product id — see DECISIONS #8), and the policy never
defines "product type" as against "product". The gap between those two words is not represented.

## 7

> "The user must provide a payment method to pay or receive refund of the price difference."

**Represented**, as evidence requirement `payment-method-for-difference`, tested by an
`evidence-present` conjunct in the allow rule and by rule
`deny-when-no-payment-method-provided`.

**Partial residue:** the sentence's *"to pay or receive refund of"* — i.e. that the same supplied
method serves both directions depending on the sign of the price difference — is not represented.
The pack does not model the price difference or its sign at all; it only asks whether a method was
supplied. The sign question resurfaces inside the computed gift-card fact (DECISIONS #7).

## 8

> "If the user provides a gift card, it must have enough balance to cover the price difference."

**Represented**, as the `any[isGiftCard == false, giftCardBalanceCoversPriceDifference == true]`
conjunct of the allow rule and as rule `deny-when-gift-card-balance-insufficient`.

**Partial residue:** *"enough balance to cover the price difference"* is a numeric comparison
between two runtime values (gift card balance, computed price difference). JPS fact conditions
compare a pointer to a literal only, and §2.2/§7.4 additionally decline to assign portable ordering
to decimal strings. The comparison has therefore been **pushed into a computed fact**,
`/payment/giftCardBalanceCoversPriceDifference`. The arithmetic that produces the price difference
is likewise outside the pack.

---

## Parent-section sentence relied on but not owned by this assignment

> "An order can only be modified if its status is 'pending', and you should check its status before taking the action."

Encoded (rule `deny-when-order-not-pending`, source `policy-modify-pending-status`) because
sentence 5 of the assigned subsection opens with "For a pending order" and is unintelligible
without it. See DECISIONS #1. The clause *"and you should check its status before taking the
action"* is **residue: left out** — it is an instruction about *when* the agent must perform a
lookup, i.e. about procedure, and the pack expresses only that the status must be `pending`, not
that it must have been re-read recently.

---

## Residue count

**8** items could not be fully represented:

1. S1b — "will change the order status to 'pending (items modifed)'" (post-condition) — left out.
2. S2 — "The agent will not be able to modify or cancel the order anymore." — left out, carried as rationale.
3. S3a — "you must confirm all the details are correct" — approximated by strong conjunction + `onUnknown: escalate`.
4. S3b — "and be cautious" — left out.
5. S4a — "remember to remind the customer" — left out (conversational duty).
6. S5/S6 — "each item …" universal quantification, and the shirt/shoe product-type illustration — pushed into computed facts.
7. S7 — "to pay or receive refund of the price difference" (direction of the difference) — left out.
8. S8 — "enough balance to cover the price difference" numeric comparison — pushed into a computed fact.

Plus one parent-section clause ("you should check its status before taking the action") left out.
