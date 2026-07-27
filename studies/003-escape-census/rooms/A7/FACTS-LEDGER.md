# Facts ledger — A7 Refunds and Compensation

Every JSON Pointer the pack reads, once each. `source` is one of `requester`, `records`, `computed`.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/compensationExplicitlyRequested` | Boolean. The user has explicitly asked for compensation in this conversation. | requester |
| `/complaint/wantsChangeOrCancel` | Boolean. The user says they want the reservation changed or cancelled. Stated by the user in the same breath as the delay complaint; the pack takes the statement at face value and does not judge whether the change is permissible (that is the Modify/Cancel sections' business, not this one). | requester |
| `/user/membershipLevel` | String, one of `regular`, `silver`, `gold`. Read straight off the user profile's membership level field. | records |
| `/reservation/hasTravelInsurance` | Boolean. Whether the reservation's travel-insurance information records that insurance was purchased. Direct read of a stored reservation field. | records |
| `/reservation/cabinClass` | String, one of `basic economy`, `economy`, `business`. The reservation's cabin class, read as stored. Cabin is uniform across a reservation by the Book/Modify rules, so no reconciliation across segments is needed. | records |
| `/complaint/aboutCancelledFlights` | Boolean. **Computed.** Two things must be done before the pack can read this: (a) classify the user's free-text grievance as a complaint about cancelled flights *in a reservation*, and (b) verify against flight records that flights in that reservation were in fact cancelled. Step (a) is an interpretation of the policy's own phrase — the policy sentence that needs it is *"If the user complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers."* Deciding what counts as "complains about cancelled flights" is applying the policy, not looking anything up; the pack cannot do it and receives the verdict. Step (b) is the records half of the same sentence's "after confirming the facts". | computed |
| `/complaint/aboutDelayedFlights` | Boolean. **Computed.** Same two-part derivation as above but for delays: classify the grievance as a complaint about delayed flights in a reservation, and confirm against flight records that flights in that reservation were delayed. The classification is an application of the policy, not a lookup. Policy sentence needing it: *"If the user complains about delayed flights in a reservation and wants to change or cancel the reservation, the agent can offer a certificate as a gesture after confirming the facts and changing or cancelling the reservation, with the amount being $50 times the number of passengers."* | computed |
| `/reservation/changeOrCancelCompleted` | Boolean. **Computed.** Requires comparing the reservation's state before and after this interaction and concluding that the change or cancellation the user asked for has actually been carried out — no single stored field says "the thing the user wanted was done". This is a conclusion about the session, not a record lookup, though it involves no policy interpretation beyond identifying which modification the user asked for. Policy sentence needing it: *"the agent can offer a certificate as a gesture after confirming the facts **and changing or cancelling the reservation**"* — the word "after" makes the completed modification a precondition of the offer. | computed |
| `/reservation/passengerCount` | Number. **Computed.** The cardinality of the reservation's stored passengers list. This is mere arithmetic (a count of a stored array) with no policy interpretation whatsoever, but it is still a calculation rather than a stored field, hence `computed`. Policy sentences needing it: *"with the amount being $100 times the number of passengers"* and *"with the amount being $50 times the number of passengers"*. The pack only checks that the count is available (an unknown count makes the certificate unsizable and escalates); the multiplication itself is carried in the outcome descriptions and the `io.onword.compensation` extension. | computed |

Counts: **requester 2 · records 3 · computed 4 · total 9**.

## Evidence requirement

| id | meaning | how supplied |
| --- | --- | --- |
| `facts-confirmed` | Agent attestation that the facts behind the complaint were confirmed against reservation and flight records *before* any offer. Declared `required: false` and consumed by `evidence-present` inside the two grant rules only, so an unconfirmed case can still resolve to "no compensation" instead of stalling the whole pack. Cites *"Always confirms the facts before offering compensation."* | `evidence.example.json` — tri-state map `{"facts-confirmed": "present" \| "absent" \| "unknown"}` |

## Evaluator run

Command:

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json \
  --evidence evidence.example.json \
  --format json --pretty
```

Input (`facts.example.json`) — a silver member on a 2-passenger economy reservation with no travel
insurance, complaining about delayed flights, who asked for compensation and whose cancellation has
already been carried out:

```json
{
  "user": {
    "membershipLevel": "silver"
  },
  "reservation": {
    "cabinClass": "economy",
    "hasTravelInsurance": false,
    "passengerCount": 2,
    "changeOrCancelCompleted": true
  },
  "complaint": {
    "aboutCancelledFlights": false,
    "aboutDelayedFlights": true,
    "wantsChangeOrCancel": true
  },
  "request": {
    "compensationExplicitlyRequested": true
  }
}
```

Full JSON output (exit 0):

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
    "outcomeId": "certificate-delayed-flight",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "excluded-regular-uninsured-economy",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-not-requested",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-ineligible",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "deny-other-reason",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "grant-cancelled-flight-certificate",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "grant-delayed-flight-certificate",
      "condition": "true",
      "outcome": "certificate-delayed-flight"
    }
  ],
  "artifact": {
    "specVersion": "0.1.0-draft",
    "bundleDigest": "abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70",
    "provenance": "immutable-git-ref"
  }
}
```

Resulting gesture: a travel certificate of 50 USD x 2 passengers = 100 USD.

## Other scenarios exercised against this pack

| scenario | disposition |
| --- | --- |
| Regular member, economy, no insurance, asks, cancelled-flight complaint | `no-compensation` — exception `excluded-regular-uninsured-economy` is true and forces the outcome; all five rules are skipped |
| Gold member who never asked for compensation, most facts absent | `no-compensation` |
| Gold member, business, complains that the same reservation was both cancelled and delayed | `unresolved`, reasons `["conflict"]`, handoff requested to "Human airline agent" |
| Cancelled-flight complaint with membership level unavailable | `unresolved`, reasons `["unknown"]`, handoff requested |
| Cancelled-flight complaint with `facts-confirmed` explicitly `absent` | `no-compensation` |
| Gold member, business, grievance outside the two enumerated grounds | `no-compensation` |
| Silver member, delayed-flight complaint, change not yet carried out | `no-compensation` |
| Gold member, cancelled-flight complaint, `passengerCount` unavailable | `unresolved`, reasons `["unknown"]`, handoff requested |
