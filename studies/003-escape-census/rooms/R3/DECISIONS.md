# Interpretation decisions — R3, "May these items be modified?"

Each entry: the text at issue, the readings available, the reading taken, and why.

---

## 1. The parent section's `pending` precondition is inside this pack's scope

**Text.** Assigned subsection, sentence 5: *"**For a pending order**, each item can be modified to
an available new item…"* Parent section: *"An order can only be modified if its status is
'pending', and you should check its status before taking the action."*

**Alternatives.**
(a) Encode only the six sentences under `### Modify items`; treat the status gate as another pack's
business, since the assignment says "the rest of the policy is context".
(b) Encode the status gate here.

**Reading taken: (b).** Sentence 5 of the assigned subsection is itself conditioned on "For a
pending order", so the status precondition is *stated inside the assigned text*, not merely
inherited. A pack that answers "May these items be modified?" without checking status would answer
`allow` for a delivered order, which the section's own first clause forbids. The parent sentence is
cited as a distinct source (`policy-modify-pending-status`) so a reader can see the borrowing.

---

## 2. The status string `pending (items modifed)` is reproduced verbatim, typo included

**Text.** *"will change the order status to 'pending (items modifed)'"* — the policy misspells
"modified".

**Alternatives.** (a) Encode `"pending (items modified)"` (corrected). (b) Encode
`"pending (items modifed)"` (verbatim). (c) Encode both via `in`.

**Reading taken: (b).** The brief is to encode what the policy says, not what a sensible policy
would say. This string is a literal database value that downstream systems will compare against; the
policy is the authority on its spelling, and silently "fixing" it would make the rule never fire
against a system that follows the policy literally. Recorded here so the mismatch is visible if the
underlying system turns out to spell it correctly. Option (c) was rejected because accepting both
spellings hides which one is real.

---

## 3. A second modification attempt is a **deny**, not an escalation to a human

**Text.** *"This action can only be called once… The agent will not be able to modify or cancel the
order anymore."* Global policy: *"You should transfer the user to a human agent if and only if the
request cannot be handled within the scope of your actions."* and *"You should deny user requests
that are against this policy."*

**Alternatives.**
(a) `escalate` exception when `/order/status == "pending (items modifed)"`: "will not be able to" is
a statement of **incapacity**, and the global rule says incapacity ⇒ transfer.
(b) Deny rule: "can only be called once" is a **prohibition**, and the global rule says requests
against the policy are denied.

**Reading taken: (b).** "This action can only be called once" is a constraint on the *tool*, not on
the agent's authority — a human agent receiving the transfer would face the same single-use tool and
could do nothing more. Transferring would therefore satisfy the letter of "cannot be handled within
the scope of your actions" while producing no benefit to the user, and the global rule's "if and
only if" cuts against gratuitous transfers. The question this pack answers is "May these items be
modified?", and for an already-modified order the answer is a definite no.

**Consequence.** The assigned subsection contains **no case that must go to a human**. The
`escalation` object is therefore wired only to the resolution-model reasons (`unknown`, `conflict`,
`no-match`, `missing-required-evidence`) — the states in which the pack genuinely cannot answer —
and no `escalate` exception is declared. See #4 and #5.

---

## 4. `onUnknown: escalate` on the allow rule; `onUnknown: ignore` on every deny rule

**Text.** *"So you must confirm all the details are correct and be cautious before taking this
action."* and *"you should check its status before taking the action."*

**Alternatives.**
(a) `ignore` everywhere plus a `deny` fallback: any unknown fact silently becomes a denial.
(b) `escalate` everywhere: any unknown fact blocks resolution, including when a definite violation
is already present.
(c) `escalate` on the allow rule only; `ignore` on the deny rules.

**Reading taken: (c).**

- Approving is the irreversible move ("The agent will not be able to modify or cancel the order
  anymore"), so it must never rest on an undetermined precondition. `escalate` makes an unknown
  block both the allow outcome and any fallback (§8.7).
- The policy nowhere authorises denying a request *because the agent has not looked something up*;
  it tells the agent to look it up. So a deny rule whose own trigger fact is unknown must contribute
  nothing — `ignore` — rather than fire.
- (b) was rejected because JPS `all` uses **strong** three-valued conjunction: with (c), a definite
  violation makes the allow rule `false` even while other facts are unknown, so the matching deny
  rule still resolves the case cleanly. Verified: `allNewItemsSameProduct: false` with the gift-card
  coverage fact absent still yields `deny-item-modification`, whereas all-facts-clean-but-one-unknown
  yields `unresolved / unknown` with a handoff request.
- (a) was rejected because it converts "I don't know yet" into "no", which is the opposite of "be
  cautious": it would let the agent close out a request it never actually checked.

---

## 5. No `fallbackOutcome`

**Alternatives.** (a) `fallbackOutcome: deny-item-modification` — safe-by-default. (b) No fallback;
an uncovered case produces `unresolved / no-match`, which the `escalation` object routes to a human.

**Reading taken: (b).** The deny rules are written as the exact negations of the allow rule's
conjuncts, so `no-match` can only arise from an authoring gap, not from a policy-recognised
situation. Silently absorbing an authoring gap into a plausible-looking "deny" would make the pack
look complete when it is not. Routing it to a human is both honest and consistent with #4's
principle that the pack must not manufacture an answer it does not have. Note this is *not* an
appeal to "the policy says transfer" — the policy says no such thing here (see #3); it is a
statement that the pack has no answer.

---

## 6. The payment method is an **evidence requirement** with `required: false`

**Text.** *"The user must provide a payment method to pay or receive refund of the price
difference."*

**Alternatives.**
(a) A plain fact, e.g. `/payment/methodProvided == true`.
(b) Evidence requirement with `required: true`.
(c) Evidence requirement with `required: false`, tested by explicit `evidence-present` conditions.

**Reading taken: (c).** "The user must provide…" is literally a proof obligation on the requester,
which is what an evidence requirement is for (§6.2), so (a) understates it. But (b) is wrong on the
spec's own definition: `required` means *"whether absence prevents normal resolution"*, and here
absence does **not** prevent resolution — it **determines** it. A user who has named no payment
method gets a clean, correct `deny` ("not as things stand"), not an unresolved case sent to a human.
With (b) the evaluator would emit `missing-required-evidence` and block, which would send routine
"you still need to tell me how to pay" cases to a human agent — exactly what the global "if and only
if" transfer rule prohibits. `missing-required-evidence` is nevertheless left in
`escalation.triggers` so that a future required requirement is not silently unrouted.

An explicitly `"unknown"` evidence state still escalates, via the allow rule's `onUnknown` (#4).
Verified: `absent` → `deny`, `unknown` → `unresolved / unknown` + handoff.

---

## 7. "Enough balance to cover the price difference" is vacuously satisfied on a refund

**Text.** *"The user must provide a payment method to pay **or receive refund of** the price
difference. If the user provides a gift card, it must have enough balance to cover the price
difference."*

**Alternatives.**
(a) Require gift-card balance ≥ |price difference| in both directions.
(b) Require gift-card balance ≥ price difference only when the difference is positive (the user
owes money); impose no balance requirement when the difference is zero or negative (the gift card
is *receiving* the refund).

**Reading taken: (b), folded into the computed fact's definition.** "Cover" presupposes a cost to be
covered. When the new items are cheaper, the gift card gains value; demanding that it already hold
that value would block a strictly beneficial modification and has no support in the text. Reading
(a) would also make the immediately preceding sentence's "or receive refund of" inoperative for
gift cards.

Because the pack cannot compute the difference or compare two runtime values, this reading lives in
the *definition* of `/payment/giftCardBalanceCoversPriceDifference` (documented in
FACTS-LEDGER.md), not in the pack's conditions. That is a real weakness: a consumer that supplies
this fact under reading (a) would get answers the pack cannot distinguish from correct ones.

Corollary: the gift-card conjunct is written as `any[isGiftCard == false, coversDifference == true]`
rather than as a bare `coversDifference == true`, so that a non-gift-card payment method is not
required to carry a coverage verdict at all. In `facts.example.json` that field is `null` and the
allow rule still evaluates `true`.

---

## 8. "Same product" means same product id; "different product option" means the option sets are not identical

**Text.** *"each item can be modified to an available new item of the same product but of different
product option. There cannot be any change of product types, e.g. modify shirt to shoe."*

**Alternatives for "same product".** (a) Same `product_id`. (b) Same product *name*. (c) Same
loosely-defined "product type" (the second sentence's wording), e.g. same category.

**Alternatives for "different product option".** (d) At least one option value differs. (e) Every
option value differs. (f) The new item id differs from the original item id.

**Readings taken: (a) and (d).** The domain section defines a product as having a "unique product
id" and a "list of variants", and defines a variant item by "information about the value of the
product options for this item" — so product identity is the product id, and option identity is the
option-value map. The shirt/shoe sentence is an illustration of (a), not a separate looser test:
shirts and shoes are different products, and reading "product type" as a broader category would
permit changing one shirt product into a different shirt product, which "the same product" plainly
forbids. Reading (e) is unsupportable for single-option products and would forbid a pure size
change. Reading (f) is too weak — two distinct item ids under the same product must differ in
options anyway, so (f) collapses into (d) in practice but would also admit a hypothetical duplicate
variant.

Both readings are discharged **outside** the pack, inside the computed facts
`/modification/allNewItemsSameProduct` and `/modification/allNewItemsDifferentOption`, because JPS
`0.1.0-draft` has no quantifier over the substitution list.

---

## 9. An unconfirmed item list yields `deny`, not a third outcome

**Text.** *"In particular, remember to remind the customer to confirm they have provided all the
items they want to modify."*

**Alternatives.** (a) A third outcome such as `not-yet` / `await-confirmation`. (b) `deny`.

**Reading taken: (b).** The pack's question is "May these items be modified?" asked at the moment
just before the single-use tool call. Until the customer has confirmed the list is complete, the
answer at that moment is no — the section is emphatic that a premature call cannot be undone. A
third outcome would be a more informative *product* but would introduce a distinction the policy
does not draw: the section states one condition, not a state machine. The temporal nuance ("no, not
yet" versus "no, never") is left to the outcome description and the deny rule's rationale.

Consequence: `deny-when-item-list-not-confirmed-complete` uses `not-equals true` rather than
`equals false`, so an explicit `false` and a present-but-non-boolean value both deny, while an
*absent* pointer stays `unknown` and is caught by the allow rule's `onUnknown: escalate` (#4).

---

## 10. Applicability is gated on the requested action

**Alternatives.** (a) Omit `applicability` (pack applies always). (b) Gate on
`/request/action == "modify-order-items"`.

**Reading taken: (b).** The retail policy contains five distinct decisions over the same order
records; without a gate this pack would return `deny` for a cancellation request on a delivered
order, which is not its question to answer. `not-applicable` is deliberately **excluded** from
`escalation.triggers`: a pack that simply does not apply is not a reason to grab a human. Verified:
`action: "cancel-order"` → `not-applicable`, handoff `none`.

---

## 11. Escalation target names the global transfer tool

`escalation.target` is `human-role` / *"Human retail agent (transfer_to_human_agents)"*, taken from
the global policy's transfer instruction. The assigned subsection names no target of its own; per
#3 it names no mandatory handoff either. The target exists solely to give the unresolved states from
#4/#5/#6 a destination, and per §6.7/§8.1 it is handoff *configuration*, not an outcome — the pack
still reports `unresolved` in those cases rather than a decision.
