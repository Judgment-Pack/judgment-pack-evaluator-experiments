# Facts ledger — A6 "May this reservation be cancelled?"

Every JSON Pointer the pack reads from the runtime facts document, one row each.

| pointer | meaning | source |
| --- | --- | --- |
| `/reservation/anySegmentFlown` | Boolean. True when any flight segment of the reservation has already been flown. Read by the `portion-already-flown` escalate exception. | computed |
| `/reservation/hoursSinceBooking` | Decimal **string** (e.g. `"63.5"`). Whole-and-fractional hours elapsed between the reservation's created time and the current time. Compared with `less-than "24"` by `booked-within-24-hours` and by the closure rule. | computed |
| `/reservation/anySegmentCancelledByAirline` | Boolean. True when any flight segment of the reservation has been cancelled by the airline. | computed |
| `/reservation/cabinClass` | String, one of `basic economy` / `economy` / `business`. The cabin class of the reservation, which the policy requires to be uniform across all its flights. Compared with `equals "business"`. | records |
| `/reservation/hasTravelInsurance` | Boolean. Whether the reservation carries travel insurance. | records |
| `/cancellation/reasonCoveredByInsurance` | Boolean. Whether the reason the user gave for cancelling is a reason the reservation's travel insurance covers. | computed |

## Why each computed fact is computed

### `/reservation/anySegmentFlown`
Policy sentence that needs it: *"If any portion of the flight has already been flown, the agent
cannot help and transfer is needed."*

What must be done first: for every flight segment on the reservation, decide from the stored
per-date flight status and scheduled times whether that segment has *already been flown*, then
take the disjunction over segments. The stored statuses are `available`, `delayed`, `on time`,
and `flying`; none of them is "flown". A segment counts as flown only once it has landed, so the
determination requires comparing the segment's scheduled arrival against the current time
(2024-05-15 15:00:00 EST) and, for a `flying` segment, deciding that a taken-off-but-not-landed
flight is not yet "flown". **That last step is an interpretation of the policy itself, not
arithmetic or lookup**: the policy never defines "flown" against the status vocabulary it
supplies. See DECISIONS.md #8.

### `/reservation/hoursSinceBooking`
Policy sentence that needs it: *"The booking was made within the last 24 hrs"*.

What must be done first: subtract the reservation's stored `created time` from the current time
and express the difference in hours as a decimal string. Pure arithmetic plus a timezone
normalisation (the policy fixes the current time as 2024-05-15 15:00:00 EST while reservation
times are stored per the booking record); no policy judgment is involved. The 24-hour threshold
and the strictness of the comparison stay inside the pack, not inside the fact. It must be
supplied as a decimal string rather than a JSON number: the reference evaluator returns `unknown`
for an ordered comparison against a JSON number, matching Core §2.2's decimal-grammar operand
requirement.

### `/reservation/anySegmentCancelledByAirline`
Policy sentence that needs it: *"The flight is cancelled by airline"*.

What must be done first: take the disjunction, over all flight segments of the reservation, of
"this segment was cancelled by the airline". Mechanical aggregation of per-segment records — no
arithmetic beyond the quantifier and no policy judgment about *which* segment counts, beyond the
any-segment reading logged in DECISIONS.md #3. Note that the airline-cancellation status is not
one of the four per-date flight statuses listed in Domain Basic, so in a real deployment this is a
lookup against whatever record carries airline-initiated cancellations.

### `/cancellation/reasonCoveredByInsurance`
Policy sentence that needs it: *"The user has travel insurance and the reason for cancellation is
covered by insurance."*

What must be done first: take the reason the user stated (which the agent must obtain as one of
change of plan, airline cancelled flight, or other reasons) and decide whether it falls inside
what the insurance covers. The only definition of coverage in the whole policy is in the Book
flight section: *"enables full refund if the user needs to cancel the flight given health or
weather reasons."* Those two coverage categories do not line up with the three reason categories
the cancel section asks for — health and weather both land in "other reasons" — so the decision
cannot be made by table lookup. **This fact requires interpreting and applying the policy itself**:
someone must judge whether the user's narrative reason is a health or weather reason. See
DECISIONS.md #5.

## Facts and evidence not read as fact pointers

The three identification inputs the section demands — user id, reservation id, and the stated
reason for cancellation — are modelled as **required evidence requirements** (`user-id`,
`reservation-id`, `cancellation-reason`) rather than fact pointers, because the policy requires
that they be *obtained*, not that they take any particular value. They therefore have no row above.
Their sources would be: `user-id` — requester (the policy says the user must provide it);
`reservation-id` — requester, or records when the user does not know it and the agent looks it up;
`cancellation-reason` — requester.

## Evaluator run

Command:

```
judgment-pack --pretty experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json
```

Scenario: a two-passenger economy round trip booked 63.5 hours ago, nothing flown yet, no
airline cancellation, travel insurance purchased at booking, and the user is cancelling because a
passenger is ill — a health reason, so the coverage judgment resolves to true.

Full output (exit code 0):

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
    "outcomeId": "cancellation-permitted",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "portion-already-flown",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "booked-within-24-hours",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "airline-cancelled-flight",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "business-cabin",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "insured-and-reason-covered",
      "condition": "true",
      "outcome": "cancellation-permitted"
    },
    {
      "stage": "rule",
      "id": "no-permitted-ground",
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

`judgment-pack spec validate pack.json` also exits 0
(`valid: JPS document conformance passed (0.1.0-draft)`).

### Other scenarios checked against the same pack

| facts | disposition |
| --- | --- |
| booked 3.5 h ago, basic economy, uninsured | `cancellation-permitted` (24-hour ground) |
| booked 48 h ago, basic economy, uninsured, nothing else true | `cancellation-denied` |
| booked exactly 24 h ago, economy, uninsured | `cancellation-denied` (boundary is exclusive) |
| a segment already flown, business cabin, booked 1 h ago | `unresolved` / `exception-escalation`, handoff requested to Human airline agent — the escalate exception outranks the permitting grounds |
| insurance facts absent from the document | `unresolved` / `unknown`, handoff requested — the closure rule escalates rather than guessing |
| `user-id` evidence marked absent | `unresolved` / `missing-required-evidence`, **no handoff** — the agent must go collect it, not transfer |
