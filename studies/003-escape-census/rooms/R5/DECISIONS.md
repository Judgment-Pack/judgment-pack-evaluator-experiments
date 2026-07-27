# Interpretation decisions — R5 "Exchange delivered order"

## 1. Three outcomes, not two

**Text.** "After user confirmation, the order status will be changed to 'exchange requested'..." plus the global "Before taking any action that updates the database (cancel, modify, return, exchange), you must list the action details and obtain explicit user confirmation (yes) to proceed."

**Alternatives.** (a) Two outcomes, permit/deny, treating an unconfirmed request as a denial. (b) Two outcomes, treating an unconfirmed request as unresolved → transfer to a human. (c) Three outcomes, adding `await-user-confirmation`.

**Chosen: (c).** An unconfirmed request is neither "against this policy" (so (a) is wrong — the agent should ask, not refuse) nor outside the agent's scope (so (b) is wrong — the policy transfers "if and only if the request cannot be handled within the scope of your actions", and asking for confirmation is squarely in scope). The policy therefore supports a third, distinct disposition: *do not touch the database yet; collect the confirmation.*

## 2. Denial grounds encoded as `force-outcome` exceptions, not as rules

**Alternatives.** (a) Six deny **rules** all naming `exchange-denied`. (b) Six `force-outcome` **exceptions** naming `exchange-denied`.

**Chosen: (b).** Under §8 a forced outcome is produced at step 6 *without evaluating normal rules*, so a denial cleanly preempts `r-await-confirmation`. With (a), an order that is both non-delivered *and* unconfirmed would make a deny rule and the await rule simultaneously true, producing `conflict` → unresolved → an unwarranted human transfer. Verified: "status `pending` + both confirmations absent" resolves to `exchange-denied`. Multiple `force-outcome` effects naming the *same* outcome are explicitly compatible (§8 step 4), so the six exceptions never conflict with each other.

## 3. `onUnknown`

**Chosen.** `r-permit-exchange`: **escalate**. All six exceptions and `r-await-confirmation`: **ignore**.

**Why.** The permit rule is the only path that authorizes a database write, and the policy says "You should not make up any information or knowledge or procedures not provided by the user or the tools" and "you should check its status before taking the action." An undetermined precondition must therefore never produce a permission; `escalate` makes any unknown conjunct block resolution and, via `escalation.triggers`, request the human transfer the policy prescribes for what the agent cannot handle. The deny exceptions use `ignore` because an *undetermined* violation should not by itself force a refusal — the permit rule already blocks, so the case still reaches a human rather than silently passing. `r-await-confirmation` uses `ignore` for the same reason: unknown evidence is already caught by the permit rule.

## 4. `applicability` = request type, not order status

**Alternatives.** (a) `applicability`: order status is `delivered`; (b) `applicability`: the request is an exchange-of-delivered-order request.

**Chosen: (b).** Under (a), a request to exchange a *pending* order would come back `not-applicable`, i.e. "this pack has nothing to say", when the policy plainly has something to say: refuse. "An order can only be exchanged if its status is 'delivered'" is a substantive prohibition, so it belongs in a denial branch, not in scope-gating. `applicability` instead carries the assignment's own boundary: this pack answers exchange questions, not returns, cancellations or modifications.

## 5. No `fallbackOutcome`

**Alternatives.** (a) `fallbackOutcome: exchange-denied`; (b) `fallbackOutcome: await-user-confirmation`; (c) none.

**Chosen: (c).** The six exceptions plus the permit rule cover every *well-typed* combination of the inputs, so a `no-match` result can only arise from a malformed or out-of-vocabulary fact (verified: `allNewItemsAvailable: "no"` → `no-match`). Defaulting such a case to any outcome would be a guess; leaving it `unresolved` routes it to a human, which is what the policy prescribes for cases the agent cannot handle.

## 6. Escalation triggers: `unknown`, `conflict`, `no-match` only

**Alternatives.** All five triggers, versus only the reachable and appropriate ones.

**Chosen: three.** `not-applicable` is excluded deliberately — a user asking about a *return* is not a case that "cannot be handled within the scope of your actions"; it is simply outside this pack, and transferring them would violate the "if and only if" in the transfer rule. `missing-required-evidence` is excluded because both evidence requirements are declared `required: false` (see #7), so the reason is unreachable; listing an unreachable trigger would misdescribe the configuration.

## 7. Confirmations modelled as evidence with `required: false`

**Alternatives.** (a) Boolean facts. (b) Evidence requirements with `required: true`. (c) Evidence requirements with `required: false` + explicit `evidence-present` conditions.

**Chosen: (c).** These are attestations about what happened in the conversation, which is what `kind: attestation` evidence is for. `required: true` is wrong: per §6.2 that means absence "prevents normal resolution", which would turn a merely-unconfirmed request into `missing-required-evidence` → unresolved → human transfer, contradicting decision #1. Declaring them optional and testing presence explicitly lets absence select `await-user-confirmation` while genuinely *indeterminate* evidence (manifest completeness unknown) still yields `unknown` → human, which is the correct tri-state behaviour.

## 8. The generic "once per order" rule was considered and left out

**Text (outside the assigned section).** "Exchange or modify order tools can only be called once per order."

**Alternatives.** (a) Add a seventh deny exception on an "already exchanged" fact. (b) Omit it.

**Chosen: (b).** Two reasons. First, the assignment scopes the pack to the "Exchange delivered order" section and treats the rest as context. Second, it is *operationally subsumed here*: a successful exchange moves the order out of `delivered` into `exchange requested`, so `x-status-not-delivered` already refuses a second exchange. Adding it would have introduced a fact pointer with no independent effect. Flagged here because a reader could reasonably have expected it.

## 9. Gift-card sufficiency as one signed computed decimal

**Text.** "If the user provides a gift card, it must have enough balance to cover the price difference."

**Alternatives.** (a) Two pointers (`balance`, `priceDifference`) compared to each other; (b) a plain boolean `giftCardCoversPriceDifference`; (c) one signed decimal `balance − priceDifference` compared to the literal `"0"`.

**Chosen: (c).** (a) is not expressible: a JPS ordered `fact` condition compares one pointer against a **literal** decimal string, never against another pointer. (b) would hide the whole test inside an opaque caller-side boolean. (c) keeps the actual threshold ("enough") visible inside the pack as `≥ 0` / `< 0`, uses the §2.2 decimal grammar, and confines the caller to arithmetic. Verified working on the installed evaluator (`"27.50" ≥ "0"` → true, `"-12.00" < "0"` → true).

## 10. "of different product option" read as a requirement

**Text.** "each item can be exchanged to an available new item of the same product but of different product option."

**Alternatives.** (a) Descriptive — it merely explains what variants are; exchanging an item for the identical variant is allowed. (b) Prescriptive — the new item must differ in option, and an identical-variant swap must be refused.

**Chosen: (b),** exception `x-same-product-option`. The sentence is the section's single statement of what an exchange *may* be, phrased with "can be exchanged to", and the parallel "Modify items" section uses the same "but of different product option" wording as a constraint. A same-variant "exchange" also has no coherent meaning under the price-difference machinery. This is a genuine ambiguity: reading (a) is available and would simply drop one exception.

## 11. Price difference in either direction

**Text.** "The user must provide a payment method to pay **or receive refund of** the price difference. If the user provides a gift card, it must have enough balance to cover the price difference."

**Reading.** The payment-method requirement is unconditional in both directions, so `x-no-payment-method` applies regardless of sign. The gift-card balance test is signed by construction (#9): when the exchange produces a refund the price difference is negative, so `balance − priceDifference` is necessarily ≥ 0 and the test passes automatically. This satisfies the literal text without adding an unstated "only when the user owes money" carve-out.

## 12. Universal quantification over the exchange item list

**Text.** "each item can be exchanged to..."

**Alternatives.** (a) Model a fixed number of item slots as separate pointers; (b) push the quantifier into caller-computed aggregate booleans.

**Chosen: (b).** JPS conditions have no iteration or quantifier and the item list is unbounded. Three `all*` pointers carry the AND-over-the-list; the ledger states precisely what must be iterated and looked up. Cost: the pack cannot name *which* item failed.

## 13. Denial versus transfer

**Text.** "You should deny user requests that are against this policy." / "You should transfer the user to a human agent if and only if the request cannot be handled within the scope of your actions."

**Reading.** Every substantive violation of the exchange section yields the `exchange-denied` outcome (agent refuses, in scope). A human transfer is configured *only* for evaluation states in which the pack could not reach an answer — `unknown`, `conflict`, `no-match`. The "if and only if" in the transfer rule is what rules out escalating known-bad requests.

## 14. Authentication and one-user-per-conversation not encoded

**Text (outside the assigned section).** "you have to authenticate the user identity..." / "you can only help one user per conversation... must deny any requests for tasks related to any other user."

**Chosen: omitted.** Conversation-level preconditions that gate every action in the policy, not a rule of the exchange decision; encoding them here would duplicate them into every sibling pack. `facts.example.json` carries `/order/userId` for realism, but no rule reads it.
