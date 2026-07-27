# FACTS-LEDGER — R4 "Return delivered order"

Every JSON Pointer that `pack.json` reads from the runtime facts document. Eight pointers total:
5 `requester`, 1 `records`, 2 `computed`. No evidence requirements are declared, so there is no
`evidence.example.json` and no `evidence-present` condition.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | The kind of action the user is asking for. The pack applies only when this is the string `"return"`. | requester |
| `/order/status` | The `status` attribute of the order named in the request, one of `pending`, `processed`, `delivered`, `cancelled` (or a post-action value such as `return requested`). Read verbatim from the stored order record; the pack does the comparison to `"delivered"` itself. | records |
| `/confirmation/orderIdConfirmed` | `true` when the user has confirmed the order id that the return applies to. | requester |
| `/confirmation/returnItemsConfirmed` | `true` when the user has confirmed the list of items to be returned. | requester |
| `/refund/paymentMethodProvided` | `true` when the user has named a payment method that is to receive the refund. Records only whether a method was supplied, not whether it is permitted. | requester |
| `/confirmation/explicitYes` | `true` when the user has given the explicit "yes" that authorizes the database update, after the agent listed the action details. | requester |
| `/refund/destinationIsOriginalPaymentMethod` | `true` when the payment method the user named for the refund is the same payment method the order was originally paid with. **Computed:** retrieve the order's `payment history`, identify the payment method used for the original charge (as opposed to any later refund or price-difference entry), and test it for identity against the payment method the user named. This is lookup plus identity comparison — no policy interpretation — but it is not a stored field: no order attribute holds "is X the original payment method". Needed by: "The refund must either go to the original payment method, or an existing gift card." | computed |
| `/refund/destinationIsExistingGiftCard` | `true` when the payment method the user named for the refund is a gift card that already exists on the authenticated user's profile. **Computed:** resolve the named payment method against the user profile's `payment methods` list, and test both that it is of type `gift card` and that it was already present before this request. **This computation embeds an interpretation of the policy itself**, not just a lookup: the section says "an existing gift card" without defining "existing", so whoever produces this fact must decide what the word excludes. The pack's reading (DECISIONS §4) is "already among this authenticated user's payment methods" — which rules out a gift card number the user merely asserts, and rules out a gift card belonging to another user. A different reading of "existing" changes this fact's value without changing the pack. Needed by: "The refund must either go to the original payment method, or an existing gift card." | computed |

## Notes on the source classification

- `/order/status` is the only pure `records` fact: it is a stored attribute copied through as-is.
- The five `requester` facts are all Booleans recording that the user said something. They are
  "stated directly" in the sense that the user's own words supply them; the agent only has to notice
  that the statement was made, not judge whether it was correct. `/confirmation/returnItemsConfirmed`
  deliberately does **not** assert that the named items belong to the order — the policy never asks
  for that check (DECISIONS §11).
- Both `computed` facts exist because the policy compares one thing to another. Neither the order
  record nor the user profile stores the answer.
- The two computed facts differ in kind, and the difference matters for auditing:
  `destinationIsOriginalPaymentMethod` is mechanical (an equality test between two stored values), so
  two careful implementers will always agree on it. `destinationIsExistingGiftCard` requires applying
  the policy's undefined term "existing", so two careful implementers can legitimately disagree, and
  the pack's answer changes with them.

## Example evaluation

`facts.example.json` — a delivered order whose owner has confirmed the order id and the single item
being returned, has asked for the refund on a gift card already on their profile, and has said yes.

```json
{
  "request": {
    "type": "return",
    "orderId": "#W5565470"
  },
  "order": {
    "orderId": "#W5565470",
    "userId": "yusuf_rossi_9620",
    "status": "delivered",
    "originalPaymentMethodId": "credit_card_9513926",
    "returnItemIds": ["1631806422"]
  },
  "confirmation": {
    "orderIdConfirmed": true,
    "returnItemsConfirmed": true,
    "explicitYes": true
  },
  "refund": {
    "providedPaymentMethodId": "gift_card_7773485",
    "paymentMethodProvided": true,
    "destinationIsOriginalPaymentMethod": false,
    "destinationIsExistingGiftCard": true
  }
}
```

(`request.orderId`, `order.orderId`, `order.userId`, `order.originalPaymentMethodId`,
`order.returnItemIds` and `refund.providedPaymentMethodId` are carried for realism and traceability;
the pack does not read them. They are the inputs from which the two computed facts are derived.)

Command:

```
judgment-pack experimental evaluate pack.json --facts facts.example.json --format json --pretty
```

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
    "outcomeId": "return-authorized",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "rule",
      "id": "r-authorize-return",
      "condition": "true",
      "outcome": "return-authorized"
    },
    {
      "stage": "rule",
      "id": "r-refuse-status-not-delivered",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "r-refuse-refund-destination",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "r-await-user-input",
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

### Additional evaluations run to check for rule conflicts and gaps

| variation on the example | disposition |
| --- | --- |
| `order.status = "pending"`, everything else as above | outcome `return-refused` |
| delivered, no explicit yes, refund to a payment method that is neither the original nor an existing gift card | outcome `return-refused` (refusal wins over the missing confirmation; no `conflict`) |
| delivered, item list not yet confirmed, no refund payment method named yet | outcome `return-not-yet-actionable` |
| `/order/status` absent from the facts document | unresolved, reasons `["unknown"]`, handoff requested to "Human agent (transfer_to_human_agents)" |
| `request.type = "exchange"` | not-applicable, handoff `none` (an exchange is still within the agent's scope, so it is not transferred) |
