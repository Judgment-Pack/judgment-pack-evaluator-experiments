# DECISIONS — R2, "May this order's payment method be modified?"

Numbered interpretation choices made while encoding **Modify pending order → Modify payment**.

---

## 1. Whether the parent section's status gate belongs in this pack

**Text.** "An order can only be modified if its status is 'pending', and you should check its status
before taking the action." (`## Modify pending order`)

**Alternatives.**
(a) Encode only the four sentences physically inside `### Modify payment`; treat the status gate as
someone else's decision (a "may this order be modified at all?" pack).
(b) Include the status gate, because `### Modify payment` is a subsection of `## Modify pending
order` and inherits its precondition.

**Chosen: (b).** The assignment names the section as "Modify pending order → Modify payment", and
the subsection is unreadable on its own — it never says which orders it applies to. The heading
"Modify **pending** order" is itself part of the precondition. Encoded as
`permit-single-different-funded-method`'s first conjunct and as the standalone
`deny-order-not-pending` rule.

**Consequence.** A status of `pending (items modified)` (produced by the sibling `### Modify items`
subsection) is denied by the same rule, without this pack needing to know that subsection exists.

---

## 2. Two outcomes, not a "transfer to human" outcome

**Text.** The subsection states one permission and its conditions; the global policy says "You
should deny user requests that are against this policy" and "You should transfer the user to a
human agent if and only if the request cannot be handled within the scope of your actions."

**Alternatives.**
(a) Three outcomes: permitted / denied / transfer-to-human.
(b) Two outcomes plus the format's `escalation` object.

**Chosen: (b).** JPS §6.7 is explicit that escalation "is not itself an outcome" and does not "turn
a condition into an outcome". Modelling the transfer as an outcome would misuse the format. The
`escalation` object carries the transfer target and the literal handoff script from the global
policy in its `message`.

---

## 3. Which escalation triggers fire

**Alternatives.** All five triggers, versus a subset.

**Chosen:** `unknown`, `conflict`, `no-match`.

- `unknown` — an undeterminable fact means the agent cannot decide within its scope; the policy's
  "you should not make up any information" forbids guessing, so a human takes it.
- `conflict` — unreachable by construction (the permit rule and every deny rule are mutually
  exclusive), retained as a safety net.
- `no-match` — also unreachable when all facts are known, retained as a safety net. No
  `fallbackOutcome` is declared, so a genuine no-match surfaces as unresolved rather than being
  silently converted into a denial.
- `not-applicable` — **excluded.** If the request is not a payment-method change, this pack simply
  has nothing to say; that is not a reason to transfer a caller to a human.
- `missing-required-evidence` — **excluded**, and moot given decision 4.

---

## 4. User confirmation as non-blocking evidence, not a rule condition

**Text.** "After user confirmation, the order status will be kept as 'pending'."

**Alternatives.**
(a) `evidenceRequirements[].required: true` — absence blocks resolution entirely.
(b) A third outcome, "permitted once confirmed", gated on `evidence-present`.
(c) `required: false`, referenced by the permit rule, with the confirmation obligation carried in
    the permitted outcome's `description`.

**Chosen: (c).** Under (a), JPS §8 step 2/5 makes *every* result unresolved until confirmation
arrives — including the clear denials. That would force the agent to ask a user to confirm a change
it is about to refuse, which is worse than useless. (b) is faithful but invents an outcome the
policy does not name, and `evidence-present` returns `unknown` whenever the runtime cannot prove
its manifest is complete (§7.5), which would escalate confirmed-but-unprovable cases to a human.

The decision question is a **permission** question ("May this be modified?"), and confirmation is a
procedural precondition to *executing* a permitted change — it is stated in the global policy
section, which is out of scope here, and appears in this subsection only as a temporal clause about
after-effects. So the pack answers "permitted", and the outcome description carries the obligation:
"The agent must still list the action details and obtain the user's explicit 'yes' before
executing." Recorded in RESIDUE.md as an approximation.

---

## 5. `onUnknown`: escalate on the permit rule, ignore on the deny rules

**Alternatives.** Uniform `escalate` (any unknown fact goes to a human), uniform `ignore`, or split.

**Chosen: split.** Granting a permission on incomplete information is exactly the failure the
policy's "you should not make up any information" is aimed at, so the permit rule escalates when
any of its conjuncts is unknown.

Uniform `escalate` would over-escalate: with `/order/status = "delivered"` known and the gift-card
balance unavailable, `deny-order-not-pending` is already decisively true, yet
`deny-gift-card-balance-insufficient` would be unknown and (per §8 step 7) would block the correct
denial. With `ignore` on the deny rules, a decisive denial survives unrelated unknowns, while an
unknown that actually matters still leaves the permit rule unknown and escalates.

---

## 6. "a single payment method different from the original" read as two conjuncts

**Text.** "The user can only choose a single payment method different from the original payment
method."

**Alternatives.**
(a) One requirement: the chosen method must differ from the original ("single" is filler).
(b) Two requirements: exactly one method may be named (no splitting the total across methods),
    **and** that method must differ from the original.

**Chosen: (b).** "Single" is doing work — the sibling `### Modify items` and `## Return delivered
order` sections likewise speak of "a payment method" in the singular, and the store's model allows a
user to hold several. Reading "single" as a cardinality constraint is the only reading under which
the word is not redundant. Encoded as `/request/newPaymentMethodCount == 1` plus
`/request/newPaymentMethodDiffersFromOriginal == true`, with a separate deny rule for each so the
agent can say which one failed.

---

## 7. "different from the original payment method" is a computed comparison, not two facts

The condition language compares one JSON Pointer against a literal; it cannot compare two pointers.
"Different from the original" is inherently a two-sided comparison, so it must arrive pre-computed
as `/request/newPaymentMethodDiffersFromOriginal`. Same for the gift-card test
(`/request/newGiftCardCoversOrderTotal`), which compares a balance against an order total whose
value is not known at authoring time. Both are recorded as `computed` in FACTS-LEDGER.md. Neither
requires interpreting the policy — they are an identifier equality check and a numeric comparison.

The raw ingredients (`/order/originalPaymentMethodId`, `/order/totalAmount`) appear in
`facts.example.json` for traceability but are deliberately **not** read by any condition, so they are
not ledger rows.

---

## 8. The gift-card balance test gates gift cards only

**Text.** "If the user wants the modify the payment method to gift card, it must have enough balance
to cover the total amount."

**Alternatives.**
(a) Require funding proof for every method (a credit card must also have available credit).
(b) Apply the test only when the requested method is a gift card.

**Chosen: (b)** — the literal reading. The permit rule uses
`any(not(type == "gift_card"), coversOrderTotal == true)`, so for a paypal account or a credit card
the funding fact is never consulted and its absence never blocks or escalates. Reading (a) would
invent a solvency check the policy never states.

---

## 9. "enough balance to cover the total amount" reads as the *order* total

"The total amount" is not further qualified. The two candidate referents are the order total and a
price difference; the price-difference reading belongs to `### Modify items` and `## Exchange
delivered order`, which say "the price difference" explicitly. A payment-method swap re-charges the
whole order, so the order total is the only coherent referent. Named
`newGiftCardCoversOrderTotal` to make the reading visible in the fact name.

---

## 10. Applicability scopes the pack to payment-method change requests

`applicability` is `/request/type == "modify-order-payment-method"`. Without it the pack would
appear to answer address changes and item changes, which are governed by sibling subsections that
this room does not encode. A `not-applicable` result is terminal (§8 step 1) and deliberately does
not trigger a handoff (decision 3).

---

## 11. Deliberately out of scope

These constrain the same real-world action but sit outside the assigned section, so they are not
encoded and are not residue:

- Global: authenticate the user before anything; one user per conversation; "list the action details
  and obtain explicit user confirmation" (see decision 4); the transfer script (carried only as
  `escalation.message` text).
- `## Generic action rules`: "Exchange or modify order tools can only be called once per order." A
  second payment-method change on the same order would be blocked by this, not by anything in
  `### Modify payment`. Not encoded; flagged here so a downstream integrator does not assume this
  pack covers it.
