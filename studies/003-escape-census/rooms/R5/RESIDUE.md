# Residue — R5 "Exchange delivered order"

Every sentence of the assigned section, quoted verbatim, with what the pack does with it.
Sentences marked **RESIDUE** are the ones not represented in the pack's logic.

---

1. > "An order can only be exchanged if its status is 'delivered', and you should check its status before taking the action."

   **Represented** — main clause becomes exception `x-status-not-delivered` (`/order/status` `not-equals` `delivered` → force `exchange-denied`) and the first conjunct of `r-permit-exchange`.

   **Partial residue (procedural clause).** "you should check its status before taking the action" is an obligation on the agent to perform a lookup, and JPS has no way to require that a fact came from a tool call rather than from the user's assertion. Approximated: the ledger classifies `/order/status` as **records** and says the value must be read from the order record, and `r-permit-exchange` uses `onUnknown: escalate` so a status that was never looked up (absent pointer) can never yield a permission.

2. > "In particular, remember to remind the customer to confirm they have provided all items to be exchanged."

   **Partial residue (speech act).** The *reminding* is a conversational act the pack cannot perform or verify. Pushed into evidence: requirement `ev-item-list-complete` records that the reminder was given and the customer confirmed completeness; its absence produces the `await-user-confirmation` outcome (rule `r-await-confirmation`) rather than a permission. What is lost is any check that the reminder actually happened as opposed to being asserted.

3. > "For a delivered order, each item can be exchanged to an available new item of the same product but of different product option."

   **Represented via computed facts.** JPS conditions have no quantifier, so "each item" cannot be expressed over a list. Pushed into three aggregate booleans that the caller must compute by iterating the exchange list: `/request/allExchangesWithinSameProduct`, `/request/allNewItemsAvailable`, `/request/allNewItemsDifferentOption` (exceptions `x-product-type-change`, `x-new-item-unavailable`, `x-same-product-option`, and conjuncts of `r-permit-exchange`). Per-item diagnostics ("item 3 is unavailable") are lost.

4. > "There cannot be any change of product types, e.g. modify shirt to shoe."

   **Represented** — exception `x-product-type-change`, sharing the computed fact `/request/allExchangesWithinSameProduct` with sentence 3. The illustrative example ("shirt to shoe") is carried only as citation excerpt text.

5. > "The user must provide a payment method to pay or receive refund of the price difference."

   **Represented** — exception `x-no-payment-method` and a conjunct of `r-permit-exchange`, over `/request/paymentMethodProvided`.

   Note: the pack does not restrict *which* payment methods are acceptable, because this section does not (unlike "Return delivered order", which limits the refund target to the original method or an existing gift card). Encoding that restriction here would be importing a rule the section does not state.

6. > "If the user provides a gift card, it must have enough balance to cover the price difference."

   **Represented via a computed fact.** JPS ordered comparisons compare one pointer against a literal decimal, so "balance ≥ price difference" (two facts) cannot be written. Pushed into the signed computed fact `/request/giftCardBalanceMinusPriceDifference`, tested `less-than "0"` in exception `x-gift-card-insufficient` and `greater-than-or-equal "0"` in `r-permit-exchange`. The individual quantities (balance, price difference) are not visible to the pack.

7. > "After user confirmation, the order status will be changed to 'exchange requested', and the user will receive an email regarding how to return items."

   **RESIDUE — left out of the logic.** This is the *effect* of the action, not a condition on it, and a JPS outcome is "a declared result, not an authorization to perform an external action" (§6.4). The status transition and the email are described in prose in the `exchange-permitted` outcome `description` and cited as source `s-exchange-effect`; nothing in the pack asserts, triggers, or verifies them.

   The clause's precondition half ("After user confirmation") *is* represented, as evidence requirement `ev-user-confirmation` plus rule `r-await-confirmation`.

8. > "There is no need to place a new order."

   **RESIDUE — left out.** Agent guidance about what *not* to do next. It constrains no input and selects no outcome. Carried only as prose inside the `exchange-permitted` outcome description and inside the `s-exchange-effect` citation excerpt.

---

**Residue count: 2 sentences fully left out (7, 8), 3 sentences partially residual (1, 2, and — as quantification/arithmetic — 3 and 6, both fully pushed into computed facts).**
Counting strictly "could not be represented at all": **2**.
