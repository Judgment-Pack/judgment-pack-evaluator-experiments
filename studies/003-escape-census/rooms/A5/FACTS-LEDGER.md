# FACTS LEDGER — A5 "May the passengers be modified?"

Every JSON Pointer that `pack.json` dereferences in a condition. Three pointers; no others are read.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/action` | What the user is asking the agent to do with an existing booking. The pack only applies when this is `"modify-reservation"`; anything else (book, cancel, refund) yields `not-applicable`. Read by `applicability`. | requester |
| `/request/subject` | Which part of the reservation the modification targets. The pack only applies when this is `"passengers"`; a cabin, flight, baggage or insurance change yields `not-applicable`. Read by `applicability`. | requester |
| `/derived/changesPassengerCount` | Boolean. `true` iff carrying out the request as stated would leave the reservation with a **different number** of passengers than it has now. Read by both rules and by the exception — it is the only fact that decides the outcome. See the expansion below: this is **computed**, and part of the computation is applying the policy itself. | computed |

## Why `/derived/changesPassengerCount` is `computed`, not `records`

Nothing in the reservation store answers this question. Producing it takes four steps, and only the
second is a lookup:

1. **Construct the post-change passenger roster from what the user said.** Requests are almost never
   phrased as a roster. "Take my brother off the booking", "my daughter is coming too", "Aarav can't
   make it, send Noah instead" all have to be turned into a concrete list of passengers before any
   count exists. The user does not state a count and cannot be asked for one without prejudging the
   answer.
2. **Look up the current roster.** `reservation.passengers` from the booking record, as-is. This
   sub-step alone would be `records`.
3. **Count both lists and compare.** Arithmetic.
4. **Decide what "modifying the number of passengers" means for the case at hand.** This is
   **applying the policy, not looking anything up.** The sentence that needs it is:

   > "The user can modify passengers but cannot modify the number of passengers."

   The sentence draws a line between a modification of *passengers* (permitted) and a modification of
   the *number of passengers* (forbidden), and leaves the classifier to whoever computes this fact.
   The pack cannot make that call itself: JPS fact conditions compare one pointer against a literal
   and cannot compare two pointers to each other, so `len(requested) != len(current)` is not
   expressible as a condition. Concretely, step 4 has to settle at minimum:
   - **Substitution.** Replacing one traveller with a different human being keeps the count at three.
     Per DECISIONS.md §2 this pack reads that as *not* a count modification, so it is permitted. A
     stricter reading ("that is really a removal plus an addition") would flip the same request from
     allow to refuse. Whoever computes this fact is choosing between those readings.
   - **Add-then-remove in one request.** "Drop Aarav, add Noah" nets to zero. Same call, same
     consequence.
   - **Infants, lap children, and no-shows.** Anyone the reservation counts as a passenger counts
     here; anyone it does not, does not. The policy's own *Book flight* section says a reservation
     has "at most five passengers" and that the agent collects a name and date of birth for each,
     which is the only handle on who is a passenger.

   Because step 4 is policy application rather than arithmetic or retrieval, the caller supplying
   this fact is exercising the substantive judgment the pack appears to be making. It is the single
   place where a wrong reading silently produces a wrong, confident answer.

## Not read by the pack

`facts.example.json` also carries `/request/requestedPassengers`, `/reservation/passengers`,
`/reservation/cabin`, `/request/statedChange`, the two ids and `/request/userId`. No condition
dereferences any of them. They are present because they are the **inputs to step 1–3 above** and to
make the worked example auditable — a reviewer can recompute `changesPassengerCount` from the same
document and check the caller's arithmetic. `/reservation/cabin` is `"basic_economy"` on purpose:
per DECISIONS.md §7 this pack applies no cabin-class restriction to passenger changes, and the
example proves that behaviour rather than asserting it.

Fact counts by source: **requester 2 · records 0 · computed 1**.

Note the shape of that distribution: this pack reads **zero** pointers straight from the booking
records. The record data it depends on (`reservation.passengers`) reaches it only after being folded
into the computed fact.

---

## Worked example

`facts.example.json` — a three-passenger basic-economy round trip on which the user wants to swap
one traveller for another. Command:

```
judgment-pack experimental evaluate pack.json --facts facts.example.json --format json
```

Full output (exit 0):

```json
{"outputVersion":"1","tool":{"name":"judgment-pack","version":"0.2.0"},"command":"experimental evaluate","status":"evaluated","experimental":true,"conformanceClaim":"none","specVersion":"0.1.0-draft","disposition":{"kind":"outcome","outcomeId":"allow-passenger-modification","reasons":[],"handoff":{"state":"none"}},"trace":[{"stage":"exception","id":"count-change-not-overridable","condition":"false"},{"stage":"rule","id":"allow-detail-change","condition":"true","outcome":"allow-passenger-modification"},{"stage":"rule","id":"deny-count-change","condition":"false"}],"artifact":{"specVersion":"0.1.0-draft","bundleDigest":"abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70","provenance":"immutable-git-ref"}}
```

`judgment-pack spec validate pack.json` also exits 0:

```
valid: JPS document conformance passed (0.1.0-draft)
artifacts: immutable-git-ref · sha256 abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70
```

### The other three paths

Checked with throwaway fact documents (deleted afterwards), to confirm the encoding behaves as
DECISIONS.md claims:

| facts | disposition | handoff |
| --- | --- | --- |
| `changesPassengerCount: true` | `outcome` → `refuse-passenger-count-change`, forced by the exception; both rules reported `not-evaluated / skipped` (§8 step 6) | `none` — the refusal is terminal, exactly as the second policy bullet requires |
| `/derived/changesPassengerCount` absent | `unresolved`, reasons `["unknown"]` | `requested` → "Human airline support agent", carrying the message that the human may clarify the roster but still cannot change the count |
| `/request/subject: "cabin"` | `not-applicable` | `none` — a sibling pack owns that request |
