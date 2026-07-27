# Residue — sentences of "Cancel pending order" not (fully) represented in `pack.json`

The assigned section has three sentences (policy.md lines 88, 90, 92). All three are represented;
two carry a remainder that the pack cannot itself hold. Each entry quotes the sentence verbatim and
says what was done with the part that did not fit.

## 1. Temporal ordering of the status check

> "An order can only be cancelled if its status is 'pending', and you should check its status before taking the action."

- **Represented:** the "only if pending" condition — `deny-status-not-pending` (status `not-equals`
  `"pending"` → `deny-cancellation`) and the `status equals "pending"` conjunct in both cancel
  rules and in `await-confirmation-of-order-id-and-reason`.
- **Remainder:** *"before taking the action"*. A Judgment Pack reads a facts document; it has no way
  to observe *when* the status was read or that the read preceded the mutation. **Pushed into the
  required evidence requirement** `order-status-check`, whose description carries the ordering
  obligation and whose absence produces `missing-required-evidence` plus a handoff request. The
  runtime, not the pack, attests to the ordering. The pack also sets `onUnknown: escalate` on every
  rule that reads `/order/status`, so an undeterminable status never resolves silently.

## 2. Execution of the cancellation and the refund

> "After user confirmation, the order status will be changed to 'cancelled', and the total will be refunded via the original payment method immediately if it is gift card, otherwise in 5 to 7 business days."

- **Represented:** the precondition ("after user confirmation") is the
  `orderIdConfirmedByUser` / `reasonConfirmedByUser` conjuncts; the gift-card / not-gift-card
  branch is represented as **outcome identity** — `cancel-refund-immediately` versus
  `cancel-refund-in-five-to-seven-business-days` — rather than as prose only.
- **Remainder:** the *effects themselves* — writing status `cancelled`, issuing the refund, and the
  "immediately" / "5 to 7 business days" service timing. JPS Core §6.4 is explicit that "an outcome
  is a declared result, not an authorization to perform an external action". **Approximated into the
  two outcome `label`/`description` strings**; performing the mutation and honouring the timing is
  left to the caller. Nothing in the pack can verify that a refund happened or how fast.

## 3. Acceptable reasons

> "The user needs to confirm the order id and the reason (either 'no longer needed' or 'ordered by mistake') for cancellation. Other reasons are not acceptable."

- **Fully represented.** The confirmation acts are two booleans, the reason enum is an `in`
  condition over exactly the two policy strings, "other reasons are not acceptable" is
  `deny-unacceptable-reason`, and "needs to confirm" (not yet done) is the
  `request-user-confirmation` outcome rather than a denial. No remainder.

---

**Residue count: 2 partial** (items 1 and 2). No sentence of the assigned section was left out
entirely.
