# FACTS LEDGER — R2, `pack.json`

Every JSON Pointer the pack reads, one row each. `source` is one of **requester** (the person making
the request states it directly), **records** (looked up from stored records as-is, no judgment), or
**computed** (must be calculated or concluded from other data before the pack can read it).

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | The kind of change being asked for. The pack applies only when this equals `"modify-order-payment-method"`; anything else yields `not-applicable`. | requester |
| `/order/status` | The order's current status, one of `pending` / `processed` / `delivered` / `cancelled` (and `pending (items modified)` after an item change). Read verbatim from the order record's `status` attribute. | records |
| `/request/newPaymentMethodCount` | How many payment methods the user has asked to settle this order with. `1` satisfies the "single payment method" constraint; `0`, `2`, … do not. A count of the methods the user named, not a lookup of the profile. | requester |
| `/request/newPaymentMethodType` | The type of the requested payment method: `gift_card`, `paypal`, or `credit_card`. Read off the payment-method record in the user's profile once the requested method id is known — a plain attribute lookup, no arithmetic and no judgment. | records |
| `/request/newPaymentMethodDiffersFromOriginal` | Boolean: is the requested payment method a *different* method from the one the order was originally paid with? | **computed** |
| `/request/newGiftCardCoversOrderTotal` | Boolean: does the requested gift card's balance cover the order's total amount? Only consulted when `/request/newPaymentMethodType` is `gift_card`. | **computed** |

**Counts — requester: 2 · records: 2 · computed: 2 (6 total).**

---

## What the two computed facts require

### `/request/newPaymentMethodDiffersFromOriginal`

Needed by: `permit-single-different-funded-method`, `deny-same-as-original-method`.

Policy sentence that needs it — *"The user can only choose a single payment method different from
the original payment method."*

To produce it, a caller must:

1. Resolve the user's stated choice ("put it on my Visa") to a concrete payment-method id in the
   authenticated user's profile.
2. Read the order's `payment history` and take the payment-method id of the original payment entry
   for this order — i.e. the method actually charged when the order was placed, not any later entry.
3. Emit `true` when the two ids are unequal, `false` when they are equal.

This is an identifier equality test over two record lookups: **arithmetic/lookup, not policy
interpretation.** The one place judgment can leak in is step 2's phrase "the original payment
method"; the policy does not define it, and this pack reads it as the payment-history entry that
charged the order (see DECISIONS.md #7). A caller that resolves "original" differently will feed
this pointer a different boolean.

The condition language cannot express this natively: a `fact` condition compares one JSON Pointer
against a literal, so a two-pointer comparison must arrive pre-computed. The raw ingredients
(`/order/originalPaymentMethodId`, `/request/newPaymentMethodId`) appear in `facts.example.json` for
traceability but are read by no condition, so they are not ledger rows.

### `/request/newGiftCardCoversOrderTotal`

Needed by: `permit-single-different-funded-method`, `deny-gift-card-balance-insufficient`.

Policy sentence that needs it — *"If the user wants the modify the payment method to gift card, it
must have enough balance to cover the total amount."*

To produce it, a caller must:

1. Read the current balance of the specific gift card the user named, from that gift card's record
   in the user's profile.
2. Determine the order's total amount — the full order total, not a price difference (see
   DECISIONS.md #9).
3. Emit `true` when `balance >= total`, `false` when `balance < total`. "Enough … to cover" is read
   as inclusive: a balance exactly equal to the total covers it.

This is a decimal comparison of two record lookups: **arithmetic/lookup, not policy
interpretation** — with the caveat that the inclusive-vs-exclusive reading of "cover" and the
identity of "the total amount" are interpretive choices this pack has already fixed, and a caller
computing the boolean differently would silently change the encoded rule.

The comparison cannot be expressed in-pack: JPS ordered operators compare a pointer against a
*literal* decimal string, and the order total is not known at authoring time. JPS §2.2/§7.4 also
decline to assign portable ordering to decimal strings at all.

## Evidence requirement (not a fact pointer)

| id | meaning | source |
| --- | --- | --- |
| `user-confirmation` | The user's explicit "yes" to the listed payment-method change. Declared `required: false`, referenced by the permit rule, and *not* used in any condition — so it never changes the disposition. See DECISIONS.md #4. | requester |

---

## Evaluator run on `facts.example.json`

```
judgment-pack spec validate pack.json
valid: JPS document conformance passed (0.1.0-draft)
artifacts: immutable-git-ref · sha256 abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70
EXIT=0
```

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json --pretty
```

Input (`facts.example.json`): a pending order originally charged to a credit card; the user asks to
move it to a single gift card whose balance covers the $279.32 total.

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
    "outcomeId": "payment-modification-permitted",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "rule",
      "id": "permit-single-different-funded-method",
      "condition": "true",
      "outcome": "payment-modification-permitted"
    },
    {
      "stage": "rule",
      "id": "deny-order-not-pending",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-not-a-single-method",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-same-as-original-method",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-gift-card-balance-insufficient",
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

Exit code 0.

### Additional dispositions checked (facts piped on stdin, not saved as files)

| scenario | disposition |
| --- | --- |
| Order `delivered`, gift-card funding fact absent | `outcome payment-modification-denied` — the decisive denial survives the unrelated unknown (DECISIONS.md #5) |
| Order `pending`, gift card, funding fact absent | `unresolved` reasons `["unknown"]`, handoff **requested** to "Human retail agent" |
| Order `pending`, credit card, funding fact absent | `outcome payment-modification-permitted` — the gift-card test is never consulted for non-gift-card methods (DECISIONS.md #8) |
| Order `pending`, gift card, `coversOrderTotal: false` | `outcome payment-modification-denied` |
| Order `pending`, method same as original | `outcome payment-modification-denied` |
| `/request/type` = `modify-order-address` | `not-applicable`, handoff `none` |
