<!--
DESIGN DRAFT, NOT REGISTERED. Study 019 arm C only: the result contract as a JSON Schema
plus the prescribed judgment convention (BRIEF.md section 3, decided 2026-08-14: full
convention). Inserted between REGO-TASK-HEAD.md and REGO-TASK-TAIL.md.
Fairness rule: the convention is stated GENERICALLY. It names no clause of the policy, no
threshold, and no part of the policy's structure; it would read the same beside any policy.
The JSON Schema below is byte-identical in content to the inventory arm B receives as prose
(RESULT-CONTRACT.schema.json / generated/ARM-B-CONTRACT.md).
-->

## The result your decision rule must produce

The entrypoint's value must satisfy this contract:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/study-019/result-contract.schema.json",
  "title": "Decision result",
  "type": "object",
  "additionalProperties": false,
  "required": ["disposition", "reasons"],
  "properties": {
    "disposition": {
      "description": "The determination issued, or the string unresolved where no determination is issued.",
      "type": "string",
      "enum": ["approve", "review", "enhanced-review", "reject", "unresolved"]
    },
    "reasons": {
      "description": "The grounds on which the case is unresolved. Order is not significant; a value may not repeat.",
      "type": "array",
      "uniqueItems": true,
      "items": {
        "type": "string",
        "enum": ["missing-required-evidence", "unknown", "no-match", "exception-escalation"]
      }
    }
  },
  "allOf": [
    {
      "description": "A determination carries no grounds.",
      "if": {
        "properties": {
          "disposition": { "enum": ["approve", "review", "enhanced-review", "reject"] }
        },
        "required": ["disposition"]
      },
      "then": { "properties": { "reasons": { "maxItems": 0 } } }
    },
    {
      "description": "An unresolved case carries at least one ground.",
      "if": {
        "properties": { "disposition": { "const": "unresolved" } },
        "required": ["disposition"]
      },
      "then": { "properties": { "reasons": { "minItems": 1 } } }
    }
  ]
}
```

## The judgment convention

Write the policy under the five conventions below. They are a house style for policies of
this kind; they say nothing about which determinations your policy should issue, or when.

**C1 — Total.** The entrypoint is defined for **every** input document. A policy that leaves
the entrypoint undefined for some input has not decided that case; it has failed to answer.
Give the entrypoint the default value

```rego
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
```

so that an input no rule reaches is answered as unresolved on the ground that no rule matched,
rather than as nothing at all.

**C2 — Exactly one determination.** For any input, at most one complete definition of the
entrypoint may hold. Where two conditions could hold at once, make the precedence explicit —
by `else`, or by writing the higher-priority condition's negation into the lower-priority
rule — so that the entrypoint never has two competing values. Two definitions holding at once
is an evaluation error, not a decision.

**C3 — Unresolved is a value, not an absence.** Where the policy says no determination can be
issued, produce the `unresolved` disposition with the grounds that apply. Never signal it by
leaving the entrypoint undefined, by returning `null`, by omitting a member, or by inventing
a ground outside the closed list.

**C4 — Grounds are carried, not merged away.** When more than one ground applies to an
unresolved case, carry all of them in `reasons`. When exactly one applies, carry exactly that
one. Order does not matter; repetition is not allowed.

**C5 — The entrypoint's value is the whole answer.** Compute no other output, and do not
depend on anything outside the `input` document and your own rules.
