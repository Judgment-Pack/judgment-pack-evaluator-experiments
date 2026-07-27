# Facts ledger — A2 "May the flights in this reservation be changed?"

Every JSON Pointer the pack reads, one row each. `source` is exactly one of `requester`,
`records`, `computed`.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | What the user is asking the agent to do, normalised to a request-kind token. The pack is applicable only when this equals `change-flights`. The user states what they want; no lookup and no judgment beyond classifying the ask. | requester |
| `/reservation/cabinClass` | The cabin class recorded on the reservation, one of `basic economy`, `economy`, `business`. Read from the stored reservation as-is. The policy guarantees a single reservation-level value ("Cabin class must be the same across all the flights in a reservation"), so no aggregation over segments is needed; if a record ever violated that invariant this pointer would become `computed`. | records |
| `/request/preservesOrigin` | Boolean: does the itinerary the user is proposing start from the same origin as the reservation on file? **Computed.** Someone must (a) read the reservation's segments and decide which segment defines the trip's origin, (b) read the proposed segments and do the same, and (c) compare the two airports. Step (a)/(b) is not arithmetic: for a round trip the policy word "origin" is not the origin of any single segment record but the start of the outbound leg, and for a multi-segment one-way it is the origin of the first segment rather than of any connection — deciding which is which **is an application of the policy term itself**, not a lookup. Needed by: "Other reservations can be modified without changing the origin, destination, and trip type." | computed |
| `/request/preservesDestination` | Boolean: does the proposed itinerary end at the same destination as the reservation on file? **Computed**, and the most interpretation-heavy of the three. For a one-way trip the destination is the arrival airport of the last segment. For a round trip the final arrival airport equals the origin, so the policy's "destination" must mean the turnaround point — the arrival airport of the outbound leg. Choosing that reading, locating the turnaround in both the stored and the proposed segment lists, and comparing them **requires interpreting the policy, not merely reading a field**. Needed by: "Other reservations can be modified without changing the origin, destination, and trip type." | computed |
| `/request/preservesTripType` | Boolean: is the proposed itinerary the same trip type (`one way` / `round trip`) as the reservation on file? **Computed.** The reservation's trip type is stored, but the proposed itinerary has no stored trip type — it must be derived from the proposed segments (does the passenger return to the origin airport?) and then compared with the stored value. The derivation is a classification of a proposed segment list against the policy's two-value trip-type vocabulary, so it applies the policy's definitions rather than looking anything up. Needed by: "Other reservations can be modified without changing the origin, destination, and trip type." | computed |

Counts: **requester 1, records 1, computed 3** (5 pointers total).

## Evidence requirements

| id | meaning | how it is supplied |
| --- | --- | --- |
| `verified-reservation-record` | Required, kind `fact`. The agent has pulled the reservation from the booking system and compared the proposed itinerary against it, rather than taking the user's word for cabin class, origin, destination, or trip type. Encodes "The API does not check these for the agent, so the agent must make sure the rules apply before calling the API!" | tri-state evidence input (`present` / `absent` / `unknown`), see `evidence.example.json` |

## Evaluator run

Command:

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json --pretty
```

`facts.example.json` — an economy round trip whose owner wants different dates on the same
city pair:

```json
{
  "request": {
    "type": "change-flights",
    "preservesOrigin": true,
    "preservesDestination": true,
    "preservesTripType": true
  },
  "reservation": {
    "cabinClass": "economy"
  }
}
```

`evidence.example.json`:

```json
{
  "verified-reservation-record": "present"
}
```

Full JSON output (exit code 0):

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
    "outcomeId": "change-permitted",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "basic-economy-not-modifiable",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "permit-shape-preserving-change",
      "condition": "true",
      "outcome": "change-permitted"
    },
    {
      "stage": "rule",
      "id": "deny-itinerary-shape-change",
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

## Other branches exercised (not deliverables, recorded for confidence)

| facts | disposition |
| --- | --- |
| `cabinClass: "basic economy"`, everything preserved | `outcome change-denied` (forced by the exception, rules not evaluated) |
| `cabinClass: "business"`, `preservesOrigin: false` | `outcome change-denied` |
| `preservesOrigin` pointer absent | `unresolved [unknown]`, handoff requested |
| `cabinClass` pointer absent | `unresolved [unknown]`, handoff requested |
| evidence `absent` | `unresolved [missing-required-evidence]`, handoff requested |
| `request.type: "cancel-flight"` | `not-applicable`, no handoff |
