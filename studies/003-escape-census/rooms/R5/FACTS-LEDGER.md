# Facts ledger — R5 "Exchange delivered order"

Every JSON Pointer that `pack.json` reads, once each.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | What the user is asking for, normalized to a request-kind label. The pack applies only when this equals `exchange-delivered-order`. The user states the request; classifying an utterance into a request kind is routine intake, not application of the exchange rules. | requester |
| `/order/status` | The stored status of the order named by the user (`pending`, `processed`, `delivered`, `cancelled`, `exchange requested`, ...). Read verbatim from the order record — the policy explicitly requires a lookup rather than the user's word: "you should check its status before taking the action." | records |
| `/request/allExchangesWithinSameProduct` | `true` iff, for **every** item in the requested exchange list, the replacement item belongs to the same product as the item it replaces. **Computed.** Requires: (a) resolve each old item id and each requested new item id to its parent product id in the product catalogue; (b) compare the two product ids pairwise; (c) AND the results over the whole list. The AND over the list is required because JPS has no quantifier — the policy says "**each** item can be exchanged to ... the same product" and "There cannot be any change of product types, e.g. modify shirt to shoe." Steps (a)–(c) are lookup plus comparison, not policy judgment; the only interpretive step is deciding that "product type" means the catalogue product id (see DECISIONS #10). | computed |
| `/request/allNewItemsAvailable` | `true` iff **every** requested new item's `availability` attribute is available. **Computed.** Requires: look up the `availability` attribute of each requested new item id in the product catalogue, then AND over the requested list. Needed by "each item can be exchanged to an **available** new item". Pure lookup + aggregation; no policy interpretation. | computed |
| `/request/allNewItemsDifferentOption` | `true` iff **every** requested new item differs in at least one product option value from the item it replaces. **Computed.** Requires: fetch the option values of the old item and of the requested new item from the catalogue and compare them for inequality, then AND over the list. Needed by "each item can be exchanged to an available new item of the same product but **of different product option**". Comparison + aggregation; the interpretive step is reading "of different product option" as a hard requirement rather than description (see DECISIONS #10), which is policy interpretation done outside the pack. | computed |
| `/request/paymentMethodProvided` | `true` iff the user has named a payment method to pay or receive refund of the price difference. Stated directly by the user in the conversation. | requester |
| `/request/paymentMethodType` | The type of the payment method the user named — `gift_card`, `paypal`, or `credit_card`. Read as-is from the authenticated user's stored profile once the named payment method id is matched; no judgment. | records |
| `/request/giftCardBalanceMinusPriceDifference` | Decimal string: the named gift card's balance minus the price difference the user owes, where price difference = (sum of the prices of the requested new items) − (sum of the prices of the items being exchanged away). Negative means the gift card cannot cover what the user owes. **Computed.** Requires: look up each old and new item price in the catalogue, sum both sides, subtract, look up the gift card balance in the profile, subtract again. Needed by "If the user provides a gift card, it must have enough balance to cover the price difference." This is arithmetic and lookup only — no policy interpretation — and it is computed rather than compared in-pack because JPS ordered `fact` conditions compare one pointer against a **literal** decimal, so a balance-vs-difference comparison of two facts cannot be expressed (see DECISIONS #9). | computed |

**Counts:** 8 pointers — requester 2, records 2, computed 4.

## Evidence requirements (not fact pointers)

Supplied through the evaluator's tri-state evidence manifest, not through the facts document.

| requirement | meaning | source |
| --- | --- | --- |
| `ev-user-confirmation` | The agent listed the action details and the user answered "yes". A conversational attestation held by the agent. | requester |
| `ev-item-list-complete` | The agent reminded the customer to confirm they had provided all items to be exchanged, and the customer confirmed. A conversational attestation held by the agent. | requester |

## Example input

`facts.example.json` — a delivered order whose owner asks to swap two items for different options of the same products, paying the price difference with a gift card that has $27.50 more than the shortfall; both confirmations on record (`evidence.example.json`).

## Evaluator output

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json --pretty
```

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
    "outcomeId": "exchange-permitted",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "x-status-not-delivered",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "x-product-type-change",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "x-new-item-unavailable",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "x-same-product-option",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "x-no-payment-method",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "x-gift-card-insufficient",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "r-permit-exchange",
      "condition": "true",
      "outcome": "exchange-permitted"
    },
    {
      "stage": "rule",
      "id": "r-await-confirmation",
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

## Branch check (other inputs, disposition only)

| variation from the example | disposition |
| --- | --- |
| `/order/status` = `pending` | outcome `exchange-denied` |
| `ev-user-confirmation` absent | outcome `await-user-confirmation` |
| `ev-item-list-complete` absent | outcome `await-user-confirmation` |
| gift card short (`-12.00`) | outcome `exchange-denied` |
| `paymentMethodType` = `credit_card`, no gift-card pointer | outcome `exchange-permitted` |
| `paymentMethodProvided` = false | outcome `exchange-denied` |
| `allExchangesWithinSameProduct` = false | outcome `exchange-denied` |
| status `pending` **and** both confirmations absent | outcome `exchange-denied` (denial preempts) |
| `/order/status` missing | unresolved `[unknown]`, handoff requested to Human agent |
| `ev-user-confirmation` = unknown | unresolved `[unknown]`, handoff requested to Human agent |
| `allNewItemsAvailable` = `"no"` (wrong type) | unresolved `[no-match]`, handoff requested to Human agent |
| `/request/type` = `return-delivered-order` | not-applicable, no handoff |
