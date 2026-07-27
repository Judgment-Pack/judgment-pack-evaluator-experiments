# Facts ledger — A1 "Book flight"

Every JSON Pointer that `pack.json` reads, one row each. 16 pointers total.

`source` legend:
- **requester** — the person making the request states it directly
- **records** — looked up from stored records as-is (no judgment involved)
- **computed** — must be calculated or concluded from other data before the pack can read it

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | Which agent workflow this request is; the pack applies only when it equals `book-flight`. | requester |
| `/user/membershipLevel` | Membership level of the booking user: `regular`, `silver`, or `gold`. Read straight from the user profile ("Each user has a profile containing: ... membership level"). | records |
| `/booking/cabinClass` | The single cabin class of the proposed reservation: `basic economy`, `economy`, or `business`. Chosen by the user. | requester |
| `/booking/cabinClassUniformAcrossFlights` | True when every flight segment in the proposed reservation carries the same cabin class. **Computed:** collect the cabin class of each proposed segment and test that the set has exactly one member. Needed by "Cabin class must be the same across all the flights in a reservation." Mechanical comparison; no policy interpretation beyond it. | computed |
| `/booking/passengerCount` | Number of passengers on the proposed reservation. **Computed:** count the entries in the passenger list the user gave. Needed by "Each reservation can have at most five passengers." Pure arithmetic. | computed |
| `/booking/allPassengersOnSameFlightsAndCabin` | True when every passenger is on the identical set of flight segments in the identical cabin. **Computed:** build the per-passenger itinerary from the proposed reservation and test all itineraries for equality. Needed by "All passengers must fly the same flights in the same cabin." Mechanical comparison. | computed |
| `/booking/payment/travelCertificateCount` | How many travel certificates the proposed reservation charges. **Computed:** classify each proposed payment method by looking its id up in the user profile ("There are three types of payment methods: credit card, gift card, travel certificate") and count the travel certificates. Lookup plus counting; no policy interpretation. Needed by "Each reservation can use at most one travel certificate." | computed |
| `/booking/payment/creditCardCount` | How many credit cards the proposed reservation charges. **Computed:** same classify-then-count over the proposed payment methods. Needed by "at most one credit card". | computed |
| `/booking/payment/giftCardCount` | How many gift cards the proposed reservation charges. **Computed:** same classify-then-count over the proposed payment methods. Needed by "at most three gift cards". | computed |
| `/booking/payment/allMethodsInUserProfile` | True when every payment method on the proposed reservation is already stored on the user's profile. **Computed:** set-membership test of each proposed payment-method id against the profile's stored payment methods. Needed by "All payment methods must already be in user profile for safety reasons." Lookup plus comparison; no policy interpretation. | computed |
| `/booking/baggage/onlyBagsUserRequested` | True when the reservation contains no checked bag beyond what the user needs. **Computed, and it requires applying the policy itself:** somebody must decide what the user "needs" from the conversation and compare it with the bags entered on the reservation. "Do not add checked bags that the user does not need" gives no test for need, so this fact carries a judgment the pack cannot make. | computed |
| `/booking/baggage/freeCheckedBagsPerPassenger` | Number of free checked bags per passenger that the proposed reservation grants. **Computed:** the agent must settle this number on the proposed reservation before the pack can compare it against the nine-row allowance table encoded in `deny-free-checked-bag-allowance-mismatch`. If it is produced by applying the table rather than read off the draft reservation, the check is vacuous — it is meant to be the draft's value, checked against the table. | computed |
| `/booking/baggage/extraCheckedBags` | Number of checked bags on the reservation beyond the free allowance. **Computed:** total checked bags minus (free bags per passenger × passenger count), floored at zero. Pure arithmetic; needed to know whether "Each extra baggage is 50 dollars" bites. | computed |
| `/booking/baggage/extraBaggageFeePerBagUsd` | US dollars the proposed reservation charges for each extra checked bag. **Computed:** read off the priced draft reservation (the per-bag charge the agent is about to record). Only checked when `extraCheckedBags` is non-zero. Needed by "Each extra baggage is 50 dollars." | computed |
| `/booking/travelInsurance/purchased` | Whether the user wants to buy travel insurance on this reservation. Stated by the user in answer to the agent's question. | requester |
| `/booking/travelInsurance/pricePerPassengerUsd` | US dollars per passenger the proposed reservation charges for travel insurance. **Computed:** read off the priced draft reservation. Only checked when insurance is purchased. Needed by "The travel insurance is 30 dollars per passenger." | computed |

**Counts: requester 3 · records 1 · computed 12.**

## Evidence requirements (not fact pointers, listed for completeness)

All four are `required: true`, so an absent one produces `unresolved / missing-required-evidence`
rather than a denial. The evaluator takes them as a tri-state map (`present` / `absent` /
`unknown`), see `evidence.example.json`.

| id | what must be supplied | analogous source |
| --- | --- | --- |
| `user-id` | The user id, obtained from the user first. | requester |
| `trip-parameters` | Trip type, origin, destination, asked of the user. | requester |
| `passenger-details` | First name, last name, date of birth for every passenger. | requester |
| `travel-insurance-offer` | Attestation that the agent asked whether the user wants insurance. | requester (agent attestation) |

## Evaluator output for `facts.example.json` + `evidence.example.json`

Command:

```
judgment-pack experimental evaluate pack.json --facts facts.example.json \
  --evidence evidence.example.json --format json --pretty
```

Exit code 0. Full output:

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
    "outcomeId": "book-allowed",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "rule",
      "id": "allow-when-book-flight-requirements-met",
      "condition": "true",
      "outcome": "book-allowed"
    },
    {
      "stage": "rule",
      "id": "deny-cabin-class-not-uniform",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-more-than-five-passengers",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-passengers-not-on-same-flights-and-cabin",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-more-than-one-travel-certificate",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-more-than-one-credit-card",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-more-than-three-gift-cards",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-payment-method-not-in-user-profile",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-unrequested-checked-bags",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-free-checked-bag-allowance-mismatch",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-extra-baggage-fee-not-fifty",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-travel-insurance-price-not-thirty",
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

The example is a gold member booking two economy passengers with one travel certificate, one credit
card, seven checked bags (6 free + 1 extra at $50) and insurance at $30 per passenger: every
requirement of the section is met, so the disposition is `book-allowed`.

### Behaviour on variants (run during authoring, not shipped as fixtures)

| variant | disposition |
| --- | --- |
| `passengerCount: 6` | outcome `book-denied` |
| `passengerCount: 6` **and** `allMethodsInUserProfile` absent | outcome `book-denied` (a definite violation still denies) |
| `allMethodsInUserProfile` absent only | unresolved, reasons `["unknown"]`, handoff requested |
| `passenger-details: absent` | unresolved, reasons `["missing-required-evidence"]`, handoff requested |
| `freeCheckedBagsPerPassenger: 2` for gold/economy | outcome `book-denied` |
| `request.type: cancel-flight` | not-applicable, no handoff |
