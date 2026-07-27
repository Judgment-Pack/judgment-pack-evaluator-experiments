# Migration measurement

## Counting boundary

This measurement covers the policy decision “given a cancellation request, may it be cancelled?” It
counts a fact only when a condition in `pack.json` reads it. The requester-supplied user id,
reservation id, and cancellation reason are required evidence, but are not M1 when the requester
states them directly. The example uses that direct-supply path. The refund destination/timing and
the mechanics of updating the booking are downstream of the decision and are not silently counted
as migrated decision logic. Likewise, the pack configures the required transfer target and exact
message, but the tool-call-then-message execution sequence is downstream handoff execution rather
than part of the asked eligibility decision:

> “To transfer, first make a tool call to transfer_to_human_agents, and then send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.”

M2 is a subset of M1, not an additional set. Therefore the five M1 facts comprise four
prepared-data-only facts and one prepared judgment.

| Measure | Count | Counting interpretation |
| --- | ---: | --- |
| M1 — prepared facts | 5 | All looked-up or computed facts read by the pack |
| M2 — prepared determinations | 1 | Judgment-like subset of M1 |
| Prepared data only (M1 minus M2) | 4 | Measurements/lookups that do not apply a policy classification |
| M3 — format cannot express | 2 | Missing executable devices |
| M4 — architectural constraints | 1 | Resolution-driven structural choice |
| M5 — fit cleanly | 7 | Policy clauses/devices represented directly |

## M1 — prepared facts (5)

1. `reservation.anyPortionAlreadyFlown` — an aggregate Boolean prepared from the reservation's
   flight-segment history. It is looked up/derived rather than stated by the requester.

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”

2. `reservation.bookingAgeHours` — elapsed hours computed from the reservation's creation time and
   the policy's current time. It is a decimal string so the experimental evaluator can perform the
   ordered comparison.

   > “The booking was made within the last 24 hrs”

3. `reservation.airlineCancelled` — verified airline cancellation status looked up from reservation
   or flight data; the requester's stated reason is not used as proof of this ground.

   > “The flight is cancelled by airline”

4. `reservation.cabinClass` — the booked cabin class looked up from the reservation record.

   > “It is a business flight”

5. `reservation.hasTravelInsurance` — the presence of travel insurance looked up from the
   reservation record.

   > “The user has travel insurance and the reason for cancellation is covered by insurance.”

Total M1: **5**.

Not counted as M1 in this example are `request.userId`, `request.reservationId`, and
`request.cancellationReason`, because the requester states all three. If the reservation id were
instead located with a tool, that particular evaluation would add one M1 prepared-data fact:

> “If the user doesn't know their reservation id, the agent should help locate it using available tools.”

That conditional path is disclosed here but is not included in the reported count for the supplied
evaluation.

## M2 — prepared determinations (1)

1. `reservation.anyPortionAlreadyFlown` — this is not merely one stored value such as a timestamp or
   cabin code. Something upstream must inspect a variable-length set of flight segments and decide
   whether at least one meets “already been flown.” For this pack, a segment counts once it has
   departed/taken off, including a currently flying segment. The Core pack receives only the
   conclusion.

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”

Total M2: **1**. This leaves **4 prepared-data-only facts** in M1.

The insurance reason is deliberately not an M2 input. The pack reads the requester's reason and
itself tests membership in `health` or `weather`, using the policy's stated categories:

> “The travel insurance is 30 dollars per passenger and enables full refund if the user needs to cancel the flight given health or weather reasons.”

## M3 — things the format cannot say at all (2)

1. Core has no quantifier or collection predicate for “any” element of a runtime array. Its `any`
   condition combines a fixed authored list of conditions; it cannot iterate the reservation's
   variable-length flight list. The pack therefore cannot derive the flown-portion conclusion and
   needs the M2 Boolean above.

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”

2. Core has no date/time subtraction or unit-bearing quantity with portable ordering semantics.
   The pack cannot directly compare the reservation's creation timestamp with the stated current
   time. It instead consumes `bookingAgeHours`, while the ordered condition is only part of the
   draft's informative experimental evaluation model.

   > “The booking was made within the last 24 hrs”

Total M3: **2**.

## M4 — architectural constraints hit (1)

1. The resolution model has no rule priority, and a direct escalation exception blocks normal rule
   resolution. The pack therefore represents the flown-portion clause as an `escalate` exception,
   combines all four positive grounds into one `any` rule, and uses `may-not-cancel` only as the
   fallback. This arrangement preserves the policy's “if … otherwise” precedence without creating
   competing cancellation and denial candidates.

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”
   >
   > “Otherwise, flight can be cancelled if any of the following is true:”

Total M4: **1**.

## M5 — what fit cleanly (7)

1. Required user-id evidence maps directly to a required evidence requirement.

   > “The user must provide their user id.”

2. Required reservation-id evidence maps directly to a required evidence requirement.

   > “First, the agent must obtain the user id and reservation id.”

3. Required cancellation-reason evidence maps directly to a required evidence requirement.

   > “The agent must also obtain the reason for cancellation (change of plan, airline cancelled flight, or other reasons)”

4. The four alternative eligibility grounds map directly to a single `any` condition.

   > “Otherwise, flight can be cancelled if any of the following is true:”

5. The insurance ground's conjunction maps directly to an `all` condition nested inside that
   `any`, while `in` carries the stated health/weather categories.

   > “The user has travel insurance and the reason for cancellation is covered by insurance.”

6. The flown-portion transfer maps directly to an escalation exception and a human-agent target;
   it is not invented as a third decision outcome.

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”

7. Missing decision facts block the rule or exception with `onUnknown: escalate`, matching the
   instruction that the agent, rather than the API, must ensure the rule applies.

   > “The API does not check that cancellation rules are met, so the agent must make sure the rules apply before calling the API!”

Total M5: **7**.

## Validation and real evaluation

Validation command:

```console
$ judgment-pack spec validate pack.json
valid: JPS document conformance passed (0.1.0-draft)
artifacts: immutable-git-ref · sha256 abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70
```

The command exited **0**. The evaluator was then run against `facts.example.json` with all four required
evidence items marked present:

```console
$ judgment-pack experimental evaluate pack.json --facts facts.example.json --evidence evidence.example.json --format json
```

Evaluation output:

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
    "outcomeId": "may-cancel",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "flown-portion",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "eligible-cancellation",
      "condition": "true",
      "outcome": "may-cancel"
    }
  ],
  "artifact": {
    "specVersion": "0.1.0-draft",
    "bundleDigest": "abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70",
    "provenance": "immutable-git-ref"
  }
}
```

In this input, the booking is older than 24 hours, the airline has not cancelled it, and the cabin
is economy. The policy still permits cancellation because the reservation has travel insurance and
the requester states the covered reason `health`; no portion has been flown.
