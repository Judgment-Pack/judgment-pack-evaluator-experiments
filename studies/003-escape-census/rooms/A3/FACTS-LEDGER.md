# FACTS LEDGER — A3 "May the cabin be changed?"

Every fact pointer `pack.json` reads, one row each. Five pointers: 2 `requester`, 0 `records`,
3 `computed`.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/type` | What modification the user is asking for. The pack applies only when this is the string `"change-cabin"`; anything else yields `not-applicable`. | **requester** — the user states what they want changed; the agent classifies the ask into the policy's own vocabulary of book / modify flights / change cabin / change baggage / change passengers / cancel. |
| `/request/changesFlights` | Whether the same request also alters the flight segments (and not only the cabin class). `true` makes the pack `not-applicable`, because "Change cabin" governs a cabin change made "without changing the flights"; such a request belongs to the *Change flights* subsection. | **requester** — read directly off what the user asked for; no reservation data is needed to see whether the user also asked to move a flight. |
| `/request/appliesToAllFlightsInReservation` | Whether the requested cabin change covers **every** flight in the reservation. `false` forces the `deny` outcome. | **computed** — the request scope must be resolved against the reservation before it can be compared. Take the flight segments the user named (e.g. "upgrade my outbound"), look up the full flight list on the reservation identified by `reservation-id`, and test whether the named set equals the full set. It is set comparison plus a records lookup, not policy interpretation; the policy sentence that needs it is: "Cabin class must remain the same across all the flights in the same reservation; changing cabin for just one flight segment is not possible." Note the degenerate case: a one-segment one-way reservation makes a single-segment request trivially whole-reservation, so a bare "which segments did they name?" reading of the request is not sufficient. |
| `/reservation/anyFlightFlown` | Whether at least one flight in the reservation has already been flown. `true` forces the `deny` outcome. | **computed** — and it **requires interpreting the policy itself, not merely arithmetic or lookup**. Records hold a per-date status for each flight (`available`, `delayed`, `on time`, `flying`) plus scheduled departure/arrival times; there is no stored "flown" flag. To produce this fact you must (1) enumerate every flight segment on the reservation, (2) read each segment's status for its booked date, and (3) decide what the policy's word "flown" denotes. This pack fixes that meaning as **has taken off** — status `flying` (the domain section says "the flight has taken off but not landed") or already landed — and *not* merely `delayed` or a departure time that has passed while the status is still `available` / `delayed` / `on time`. That third step is an interpretation of the policy term and is recorded as DECISIONS #1. The policy sentence that needs it: "Cabin cannot be changed if any flight in the reservation has already been flown." |
| `/pricing/priceDifferenceDirection` | The direction of the price difference the cabin change would produce: `"higher"`, `"lower"`, or `"equal"`. Selects between `allow-collect-difference`, `allow-refund-difference`, and `allow-no-money-movement`. | **computed** — arithmetic over two looked-up figures. Price the whole reservation in the requested cabin (per-cabin prices are listed per flight per date, summed over every segment and every passenger, since "All passengers must fly the same flights in the same cabin"), compare that total against the original price recorded on the reservation, and reduce the comparison to one of the three labels. The comparison is deliberately done outside the pack rather than with an ordered `fact` condition, because JPS `0.1.0-draft` §7.4 assigns no portable ordering to decimal strings (DECISIONS #10). The policy sentences that need it: "If the price after cabin change is higher than the original price, the user is required to pay for the difference." and "If the price after cabin change is lower than the original price, the user is should be refunded the difference." |

## Evidence requirements (not fact pointers)

Supplied through the evaluator's tri-state evidence manifest rather than the facts document, so they
are listed separately and are not counted in the table above.

| requirement | meaning | source |
| --- | --- | --- |
| `user-id` | The user id, obtained before any modification is considered. | **requester** — "The user must provide their user id." |
| `reservation-id` | The reservation whose cabin is to be changed. | **requester**, with a records fallback — the user gives it, or, "If the user doesn't know their reservation id, the agent should help locate it using available tools." |

---

## Example input

`facts.example.json` — a user on a not-yet-departed round trip asking to move the whole reservation
up a cabin, where the new total is higher than what they paid:

```json
{
  "request": {
    "type": "change-cabin",
    "changesFlights": false,
    "appliesToAllFlightsInReservation": true
  },
  "reservation": {
    "anyFlightFlown": false
  },
  "pricing": {
    "priceDifferenceDirection": "higher"
  }
}
```

`evidence.example.json`:

```json
{
  "user-id": "present",
  "reservation-id": "present"
}
```

## Evaluator output

```
judgment-pack --pretty experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json
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
    "outcomeId": "allow-collect-difference",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "refuse-when-a-flight-has-been-flown",
      "condition": "false"
    },
    {
      "stage": "exception",
      "id": "refuse-when-change-does-not-cover-all-segments",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "collect-difference-when-new-price-higher",
      "condition": "true",
      "outcome": "allow-collect-difference"
    },
    {
      "stage": "rule",
      "id": "refund-difference-when-new-price-lower",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "no-money-movement-when-price-equal",
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

`judgment-pack spec validate pack.json` → `valid: JPS document conformance passed (0.1.0-draft)`,
exit 0.

## Other scenarios checked against the same pack

| facts varied from the example | disposition |
| --- | --- |
| `anyFlightFlown: true`, price `lower` | `outcome` → `deny` (the forced outcome wins without evaluating the price rules) |
| `anyFlightFlown: true` **and** `appliesToAllFlightsInReservation: false` | `outcome` → `deny` (two `force-outcome` exceptions naming the same outcome are compatible, not a `conflict`) |
| `priceDifferenceDirection` absent | `unresolved`, reasons `["unknown"]`, handoff requested to *Human airline agent* |
| `changesFlights: true` | `not-applicable`, no handoff (belongs to the *Change flights* subsection) |
| `priceDifferenceDirection: "equal"` | `outcome` → `allow-no-money-movement` |
| evidence `reservation-id: "absent"` | `unresolved`, reasons `["missing-required-evidence"]`, handoff requested |
