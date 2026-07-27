# Facts ledger — `pack.json` (Cancel pending order)

Every JSON Pointer the pack reads, once each. `source` is one of `requester`, `records`, `computed`.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/action` | The action the user is asking for, as a canonical action token. Read by `applicability` (`equals "cancel_order"`) so the pack is inert for return/exchange/modify requests. The user states what they want; the deployment supplies the token for the action it is about to take. | requester |
| `/order/status` | The order's current status as stored on the order record (`pending`, `processed`, `delivered`, `cancelled`, or any other value the record carries, e.g. `pending (items modified)`). Read verbatim from the order record with no interpretation; the pack compares it to the literal `"pending"`. | records |
| `/request/orderIdConfirmedByUser` | Boolean: the user has confirmed the order id that this cancellation applies to. Stated by the user in the conversation ("The user needs to confirm the order id ... for cancellation"). `false` means "not confirmed yet", which is a different state from the pointer being absent. | requester |
| `/request/reasonConfirmedByUser` | Boolean: the user has confirmed a cancellation reason. Stated by the user in the conversation. `false` means "no reason confirmed yet". | requester |
| `/request/cancellationReason` | The cancellation reason the user confirmed, as one of the two canonical policy strings `"no longer needed"` / `"ordered by mistake"`, or any other string (or `null`) when the user gave something else. Treated as requester-stated because the policy expects the user to assent to one of the two enumerated reasons the agent offers. Caveat: if a deployment lets the user speak freely and then maps free text onto the enum, that mapping is a classification step and the fact becomes `computed` for that deployment (see DECISIONS.md #9). | requester |
| `/order/originalPaymentMethod/type` | The payment-method type of the **original** payment for this order (`gift_card`, `paypal`, `credit_card`). Not a stored field: the order record stores a `payment history`, so before the pack can read this the runtime must (a) select the original payment transaction from that history — the initial charge, not later refunds or adjustments — and (b) resolve its payment-method id against the user's profile payment methods to obtain the method's type. Step (a) is an interpretation of what "the original payment method" means for an order with multiple payment-history entries; it is not mere arithmetic or a single lookup. Required by: "the total will be refunded via the original payment method immediately if it is gift card, otherwise in 5 to 7 business days." | computed |

Counts: **requester 4**, **records 1**, **computed 1** (6 pointers total).

## Evidence requirement (not a fact pointer)

| id | meaning | supplied by |
| --- | --- | --- |
| `order-status-check` | Attestation that the order's status was actually retrieved from the order record *before* the cancellation action is taken ("you should check its status before taking the action"). Tri-state: `present` / `absent` / `unknown`. `absent` yields `missing-required-evidence` and a handoff request; the pack cannot itself observe that the lookup happened. | runtime / records lookup |

## Evaluator run

Command:

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json --pretty
```

Input `facts.example.json`: a pending order paid by credit card, order id and the reason
"no longer needed" both confirmed by the user.

Full output (exit 0):

```json
{
  "outputVersion": "1",
  "tool": {
    "name": "judgment-pack",
    "version": "0.2.0"
  },
  "command": "experimental evaluate",
  "status": "evaluated",
  "experimental": true,
  "conformanceClaim": "none",
  "specVersion": "0.1.0-draft",
  "disposition": {
    "kind": "outcome",
    "outcomeId": "cancel-refund-in-five-to-seven-business-days",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "rule",
      "id": "cancel-pending-original-gift-card",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "cancel-pending-original-not-gift-card",
      "condition": "true",
      "outcome": "cancel-refund-in-five-to-seven-business-days"
    },
    {
      "stage": "rule",
      "id": "deny-status-not-pending",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-unacceptable-reason",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "await-confirmation-of-order-id-and-reason",
      "condition": "false"
    }
  ],
  "artifact": {
    "specVersion": "0.1.0-draft",
    "bundleDigest": "abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70",
    "provenance": "immutable-git-ref"
  }
}
```

`judgment-pack spec validate pack.json` exits 0
(`valid: JPS document conformance passed (0.1.0-draft)`).

## Behaviour spot-checks (same pack, other inputs)

| input | disposition |
| --- | --- |
| status `delivered`, everything else confirmed | `deny-cancellation` |
| pending, reason `"found it cheaper elsewhere"` confirmed | `deny-cancellation` |
| pending, nothing confirmed, reason `null` | `request-user-confirmation` |
| pending, confirmed, original method `gift_card` | `cancel-refund-immediately` |
| pending, confirmed, `/order/originalPaymentMethod/type` absent | `unresolved` — `["unknown"]`, handoff requested |
| `/order/status` absent | `unresolved` — `["unknown"]`, handoff requested |
| `order-status-check` evidence `absent` | `unresolved` — `["missing-required-evidence"]`, handoff requested |
| `/request/action` = `"return_order"` | `not-applicable` (no handoff — see DECISIONS.md #12) |
