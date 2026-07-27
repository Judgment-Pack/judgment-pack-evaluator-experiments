# RESIDUE — R4 "Return delivered order"

The assigned section is five sentences (`reference/policy.md`, section "Return delivered order").
Three are fully represented in `pack.json`. Two carry a clause that the format cannot represent as a
decision; both are listed below with what was done instead.

---

## 1. Partially represented — the procedural ordering obligation

> "An order can only be returned if its status is 'delivered', and you should check its status
> before taking the action."

**Represented.** The prohibition. `r-refuse-status-not-delivered` fires on
`/order/status != "delivered"` → `return-refused`, and `r-authorize-return` requires
`/order/status == "delivered"` as a conjunct.

**Not represented.** The clause "and you should check its status **before taking the action**". This
is an instruction about the *order of the agent's operations* — look the status up first, act
second. A Judgment Pack states a condition on facts; it has no vocabulary for sequencing an agent's
tool calls, and §6.4 of the spec is explicit that an outcome "is not an authorization to perform an
external action".

**What I did instead:** *approximated via `onUnknown`.* `r-authorize-return` and
`r-refuse-status-not-delivered` both carry `onUnknown: escalate`, so a facts document in which
`/order/status` is absent or unreadable can never produce `return-authorized` — it produces
`unresolved` with reason `unknown` and a handoff to a human agent. This makes an *unchecked* status
non-actionable, which is the enforceable consequence of the sentence, but it does not and cannot
enforce that the check happened before rather than after the tool call. That guarantee has to come
from the runtime that consumes the pack.

---

## 2. Partially represented — the post-confirmation effects

> "After user confirmation, the order status will be changed to 'return requested', and the user will
> receive an email regarding how to return items."

**Represented.** The gate. "After user confirmation" is read as the explicit-yes requirement (see
DECISIONS §2) and is encoded as `/confirmation/explicitYes`, a required conjunct of
`r-authorize-return` and one of the four prerequisites whose absence yields
`return-not-yet-actionable`.

**Not represented.** The two consequences: the state transition `delivered` → `return requested`, and
the notification email. These are effects of executing the decision, not part of deciding it. Core
0.1.0-draft has no post-condition, effect, or action vocabulary — an outcome is a declared result
only.

**What I did instead:** *left out of the machinery, recorded in prose.* Both effects are written into
the `description` of the `return-authorized` outcome ("On processing, the order status becomes
'return requested' and the user receives an email about how to return the items") and the sentence is
cited as source `s-return-effect`, referenced by `r-authorize-return` and `r-await-user-input`. A
consumer reads them as documentation of what executing the outcome entails; nothing in the pack
verifies that either happened.

---

## Sentences with no residue

| sentence | where it lives in the pack |
| --- | --- |
| "The user needs to confirm the order id and the list of items to be returned." | `/confirmation/orderIdConfirmed` and `/confirmation/returnItemsConfirmed`; conjuncts of `r-authorize-return`, disjuncts of the missing-prerequisite clause of `r-await-user-input`; source `s-return-confirm`. |
| "The user needs to provide a payment method to receive the refund." | `/refund/paymentMethodProvided`; same two rules; source `s-return-payment-method`. |
| "The refund must either go to the original payment method, or an existing gift card." | The `any[...]` disjunction over `/refund/destinationIsOriginalPaymentMethod` and `/refund/destinationIsExistingGiftCard`, positively in `r-authorize-return` and negated in `r-refuse-refund-destination`; source `s-return-refund-destination`. The undefined term "existing" is pushed into the computed fact and flagged in FACTS-LEDGER and DECISIONS §4, but the sentence itself is fully encoded. |

**Residue count: 2** (both partial — one clause of sentence 1, and the two effects of sentence 5).
