You are the deciding officer for one business case under the policy below.
Decide the case exactly as the policy directs — including declining to decide
when the policy says the case is blocked, out of scope, or undecidable.

Report your decision in this fixed vocabulary:
- "kind": "outcome" (the policy produced a definite outcome),
  "not-applicable" (the case is outside the policy's scope), or
  "unresolved" (the policy blocks the decision).
- "outcomeId": the outcome's identifier, ONLY when kind is "outcome".
- "reasons": when kind is not "outcome", the applicable subset of
  ["not-applicable","missing-required-evidence","unknown","conflict",
  "no-match","exception-escalation"]; empty when kind is "outcome".
- "handoff": "requested" if the policy routes this blocked or exceptional
  case to a configured destination (or an exception escalates it directly),
  else "none".
- "target": when handoff is "requested" and the policy configures a
  destination, {"kind": "...", "name": "..."} exactly as the policy names
  it; null when no destination is configured or handoff is "none".

## The policy

# Item acceptance policy (suppressed rule variant)

- The base rule accepts every item unconditionally — but an exception
  (which always applies) suppresses that rule entirely, so it never
  produces an outcome.
- No other rule exists, there is no default outcome, and no escalation
  destination is configured: every item therefore ends undecided, with no
  matching rule and nowhere configured to send it.


## The case

Case handle: case-16

Facts:
```json
{}
```

Evidence availability ("present" / "absent"; anything not listed is unknown):
No evidence availability information was provided.

For reference, the application maps outcomes to actions as:
```json
{
  "accept": "execute:accept-item",
  "reject": "record"
}
```

Respond with ONLY one JSON object, no prose, no code fence:
{"kind": "...", "outcomeId": "... or omit", "reasons": [...], "handoff": "none|requested", "target": {...} or null}
