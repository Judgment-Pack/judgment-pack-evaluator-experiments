# FACTS LEDGER — A4 `pack.json`

Every JSON Pointer the pack reads, once each. Four pointers total: 2 `requester`, 2 `computed`,
0 `records`.

| pointer | meaning | source |
| --- | --- | --- |
| `/request/phase` | Which policy phase the request belongs to: `"post-booking-modification"` (the user is changing a reservation that already exists) or `"initial-booking"` (the reservation is still being created). Read by `applicability`; anything other than `post-booking-modification` makes the pack not-applicable. | requester |
| `/request/target` | What the user is asking to change: `"checked-bags"` or `"travel-insurance"`. Read by `applicability` and guarded in every rule and in the exception, so that the other target's `effect` pointer being absent cannot make a rule unknown. | requester |
| `/request/checkedBags/effect` | Direction of the requested checked-bag change: `"increase"`, `"decrease"`, or `"no-change"`. Drives `add-checked-bags-permitted` and `remove-checked-bags-denied`. | computed |
| `/request/insurance/effect` | Direction of the requested travel-insurance change: `"add"`, `"remove"`, or `"no-change"`. Drives `add-insurance-denied` and the `insurance-removal-out-of-scope` escalate exception. | computed |

## What the two computed facts require

### `/request/checkedBags/effect`

Not a lookup. Before the pack can read it, someone must:

1. retrieve the stored reservation record and read its current checked-bag counts — the
   reservation-wide total and the count attributed to each passenger (evidence requirement
   `current-reservation-record`);
2. resolve the user's phrasing into a concrete requested end-state per passenger ("add two bags",
   "make it three bags", "put one of Aarav's bags on Mei's ticket" all have to become numbers);
3. compare requested to recorded and emit `"decrease"` if the reservation-wide total **or any
   individual passenger's count** would go down, `"increase"` if nothing goes down and something
   goes up, `"no-change"` otherwise.

**Step 3 applies the policy, it is not arithmetic.** The policy sentence that forces the judgment is:

> "The user can add but not remove checked bags."

The sentence does not say whether "remove" is measured per reservation or per passenger, and it does
not say what a request that both adds and removes counts as. The classifier answers both questions
before the pack ever sees a value: a per-passenger reduction is a removal even when the total is
flat, and a mixed add-and-remove request collapses to `"decrease"` and is denied. Those two readings
are argued in DECISIONS.md §2 and §3. A different but defensible classifier would send the same
request to a different outcome without changing a single line of `pack.json`.

The compare-two-numbers part is unavoidable in this format: a `fact` condition compares one pointer
against a literal, so "requested > recorded" cannot be written as a condition at all.

### `/request/insurance/effect`

Also not a lookup:

1. read the reservation's stored travel-insurance information (same evidence requirement);
2. read what the user wants the insurance state to be;
3. emit `"add"` only when the reservation currently has **no** travel insurance and the user wants
   it; `"remove"` when the reservation has insurance and the user wants it gone; `"no-change"`
   otherwise — including the case where the user asks to "add" insurance the reservation already
   carries.

**Step 3 embeds a policy reading.** The sentence at stake:

> "The user cannot add insurance after initial booking."

Whether asking for insurance you already hold counts as "adding insurance" is not settled by the
text. Emitting `"no-change"` there (rather than `"add"`) is the reading defended in DECISIONS.md §7,
and it changes the result from a denial to a human handoff.

Note that the *temporal* half of that sentence — "after initial booking" — is **not** inside this
computed fact. It is carried structurally by `/request/phase` in `applicability`, so it stays
visible in the pack.

## Why no `records` row

The reservation's stored baggage counts and insurance flag are pure record lookups, but the pack
never reads them directly: a condition can only compare one pointer to a constant, and every
question the policy asks ("is this an addition?", "is this a removal?") is a *relation* between the
request and the record. The record therefore enters the pack only through the two computed facts
above, and is declared as the evidence requirement `current-reservation-record` so the obligation
stays on the page. Anyone auditing this pack should audit the classifier that produces those two
strings — that is where the policy is actually being applied.

---

## Evaluator run

Command:

```
judgment-pack experimental evaluate pack.json \
  --facts facts.example.json --evidence evidence.example.json --format json --pretty
```

`facts.example.json` is a silver member with reservation HG7ZP2 (economy, two passengers, one
checked bag on record) asking to go from one checked bag to three — a pure addition.

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
    "outcomeId": "permit-add-checked-bags",
    "reasons": [],
    "handoff": {
      "state": "none"
    }
  },
  "trace": [
    {
      "stage": "exception",
      "id": "insurance-removal-out-of-scope",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "add-checked-bags-permitted",
      "condition": "true",
      "outcome": "permit-add-checked-bags"
    },
    {
      "stage": "rule",
      "id": "remove-checked-bags-denied",
      "condition": "false"
    },
    {
      "stage": "rule",
      "id": "add-insurance-denied",
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

### Other scenarios exercised (same pack, facts via stdin)

| facts | disposition | reasons | handoff |
| --- | --- | --- | --- |
| bags, `effect: decrease` | outcome `deny-remove-checked-bags` | — | none |
| insurance, `effect: add` | outcome `deny-add-insurance` | — | none |
| insurance, `effect: remove` | unresolved | `exception-escalation` | requested → human agent |
| bags, `checkedBags` pointer absent | unresolved | `unknown` | requested → human agent |
| bags, `effect: no-change` | unresolved | `no-match` | requested → human agent |
| `phase: initial-booking`, insurance add | not-applicable | `not-applicable` | none (Book flight governs) |
