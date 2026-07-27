# Facts ledger — R3 "May these items be modified?"

Every fact pointer read by `pack.json`, one row each.

`source` legend:
- **requester** — the person making the request states it directly
- **records** — looked up from stored records as-is (no judgment involved)
- **computed** — must be calculated or concluded from other data before the pack can read it

## Fact pointers

| pointer | meaning | source |
| --- | --- | --- |
| `/request/action` | The action the user is asking for. The pack is applicable only when this equals `"modify-order-items"`. Read by `applicability`. | requester |
| `/order/status` | The stored status of the order named in the request (`pending`, `processed`, `delivered`, `cancelled`, or `pending (items modifed)`). Read by the allow rule and by `deny-when-order-not-pending` / `deny-when-items-already-modified`. Verbatim read of the order record's status field — no interpretation. | records |
| `/modification/allNewItemsSameProduct` | `true` iff, for **every** (original item → new item) pair in the request, the new item is a variant of the same product as the item it replaces. **Computed:** for each pair, resolve `originalItemId` → its `product_id` and `newItemId` → its `product_id` (two catalog lookups per pair, because "Product ID and Item ID have no relations"), test equality, then conjoin the per-pair results across the whole request. The pack has no array iteration or quantifier, so the universal quantification must be discharged outside the pack. Needed by: *"For a pending order, each item can be modified to an available new item of the same product but of different product option. There cannot be any change of product types, e.g. modify shirt to shoe."* Applying the "same product / no product-type change" test is applying the policy itself, not mere lookup: it requires deciding that "same product" means "same product id" rather than, e.g., same product name or same category. | computed |
| `/modification/allNewItemsDifferentOption` | `true` iff, for **every** pair, the new item's option values differ from the original item's option values. **Computed:** for each pair, fetch both variants' option maps from the catalog, compare them for inequality, then conjoin across pairs. Needed by: *"each item can be modified to an available new item of the same product but of different product option."* This is policy application, not lookup: the policy does not define whether "different product option" means *any* differing option value or a *wholly* different option set, so the computation must commit to a reading (see DECISIONS #8) before the pack can read a boolean. | computed |
| `/modification/allNewItemsAvailable` | `true` iff **every** requested new item is currently available. **Computed:** the per-item `availability` flag is a plain record lookup, but the pack reads one aggregated boolean, so the conjunction across all requested new items must be performed first. Needed by: *"each item can be modified to an available new item of the same product but of different product option."* Arithmetic/aggregation only — no policy interpretation beyond the aggregation itself. | computed |
| `/modification/customerConfirmedItemListComplete` | `true` iff the customer has affirmatively said they have provided all the items they want to modify. Stated by the customer in the conversation after the agent's reminder. Needed by: *"In particular, remember to remind the customer to confirm they have provided all the items they want to modify."* | requester |
| `/payment/isGiftCard` | `true` iff the payment method the user supplied for the price difference is a gift card. Read from the payment method's type in the authenticated user's stored profile once the user names the method — no judgment. | records |
| `/payment/giftCardBalanceCoversPriceDifference` | `true` iff the supplied gift card's balance is enough to cover the price difference (and vacuously `true` when the price difference is zero or negative, i.e. the user is receiving a refund). **Computed:** (a) price out every original item and every new item from the catalog, (b) sum the new prices and subtract the sum of the original prices to obtain the price difference across the whole modification, (c) read the gift card's `balance` from the user profile, (d) compare. The pack cannot do this itself: fact conditions compare a pointer to a *literal*, never to another pointer, and the price difference is not a stored field. This also requires interpreting the policy: *"If the user provides a gift card, it must have enough balance to cover the price difference"* is silent about the refund direction, so the computation must decide that a non-positive difference imposes no balance requirement (see DECISIONS #7). | computed |

## Evidence requirements

The pack also declares one evidence requirement, supplied via the evaluator's tri-state `--evidence` input rather than through a fact pointer.

| requirement id | meaning | source |
| --- | --- | --- |
| `payment-method-for-difference` | Whether the user has supplied a payment method to pay, or receive a refund of, the price difference. Needed by: *"The user must provide a payment method to pay or receive refund of the price difference."* | requester |

## Counts

- requester: **2** fact pointers (+1 evidence requirement)
- records: **2** fact pointers
- computed: **4** fact pointers

## Example evaluation

Inputs: `facts.example.json`, `evidence.example.json`.

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json \
  --evidence evidence.example.json \
  --format json --pretty
```

Full output:

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
    "outcomeId": "allow-item-modification",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "rule",
      "id": "allow-when-all-conditions-met",
      "condition": "true",
      "outcome": "allow-item-modification"
    },
    {
      "stage": "rule",
      "id": "deny-when-order-not-pending",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-items-already-modified",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-product-type-changes",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-option-not-different",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-new-item-unavailable",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-no-payment-method-provided",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-gift-card-balance-insufficient",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-when-item-list-not-confirmed-complete",
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

### Spot checks on other inputs (not deliverables, recorded for review)

| variation from the example | disposition |
| --- | --- |
| `allNewItemsSameProduct: false` (shirt → shoe) | outcome `deny-item-modification` |
| `isGiftCard: true`, coverage fact absent | unresolved, reasons `["unknown"]`, handoff requested to the human retail agent |
| `order.status: "pending (items modifed)"` | outcome `deny-item-modification` |
| evidence `payment-method-for-difference: "absent"` | outcome `deny-item-modification` |
| evidence `payment-method-for-difference: "unknown"` | unresolved, reasons `["unknown"]`, handoff requested |
| `request.action: "cancel-order"` | `not-applicable` |
