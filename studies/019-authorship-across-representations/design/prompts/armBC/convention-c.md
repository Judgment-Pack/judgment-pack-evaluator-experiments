# Result contract and judgment convention (arm C)

This section fixes **how** your policy states its answer. It says nothing about **what** the
answer should be in any case — that is entirely determined by the policy prose you were
given. Follow it exactly; a result that does not conform cannot be scored.

## 1. The result contract

Your entrypoint rule must evaluate to a single **decision object** conforming to this JSON
Schema.

<!-- SCHEMA:result-contract -->

```json title="result-contract.schema.json"
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "decision",
  "type": "object",
  "additionalProperties": false,
  "required": ["disposition", "reasons"],
  "properties": {
    "disposition": {
      "type": "string",
      "enum": ["approve", "review", "enhanced-review", "reject", "unresolved"]
    },
    "reasons": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "missing-required-evidence",
          "unknown",
          "no-match",
          "exception-escalation"
        ]
      }
    }
  },
  "allOf": [
    {
      "if": { "properties": { "disposition": { "const": "unresolved" } } },
      "then": { "properties": { "reasons": { "minItems": 1 } } }
    },
    {
      "if": { "properties": { "disposition": { "not": { "const": "unresolved" } } } },
      "then": { "properties": { "reasons": { "maxItems": 0 } } }
    }
  ]
}
```

The identifiers in the two enumerations are the registered ones from the naming appendix.
Do not invent, abbreviate, re-case, or pluralise any of them.

## 2. Package and entrypoint

Use the package and entrypoint rule name given in the naming appendix, and put the whole
policy in that one package. The entrypoint rule is the only rule that is read; every other
rule you write is a helper and may be named however you like.

## 3. The registered default

Your entrypoint rule must carry exactly this default, verbatim:

```rego
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
```

This is a registered convention, not a hint: it fixes what the entrypoint evaluates to when
every rule defining it is undefined, so that the result is never absent. Write it even if
you believe your rules are exhaustive.

## 4. Precedence: use an `else` ladder in application order

Where the policy prose makes conditions mutually exclusive, or states that one part of the
policy takes precedence over another, encode that precedence as a **single `else` ladder**
whose rungs appear in the order in which the prose says the parts apply. The earlier rung
wins; a later rung is reached only when every earlier rung's body fails.

Do not encode precedence by writing separate same-named rules and relying on the order they
appear in the file — separate rules of the same name are not tried in order, and two of them
producing different values is an evaluation error, not a resolution. Do not encode it by
adding the negation of every earlier condition to each later rule body either; use the
ladder.

If you need a helper that answers the same question for different arguments, a function with
its own `else` ladder is the same construct and is equally acceptable.

## 5. Grounds

- Every `reasons` token you emit must be one of the four registered ground tokens, and each
  must be the ground the prose actually gives for that case.
- Where the prose escalates a case for a human rather than settling it, represent that as
  disposition `unresolved` with reasons exactly `["exception-escalation"]`. Do not invent a
  separate disposition for it, and do not add routing or addressing information of any
  kind: the decision object is the whole result.
- Emit the smallest set of grounds the prose supports for the case — do not accumulate a
  ground from a part of the policy that did not govern the case.

## 6. `unresolved` is not a determination

`unresolved` is a fifth, distinct value of `disposition`. It is never a synonym for, nor a
weaker form of, any of the four determination identifiers, and none of the four ever carries
a reason token. Keep them apart: if a case is unresolved, the disposition is the literal
string `unresolved` and the grounds go in `reasons`; if a case is determined, `reasons` is
the empty array `[]`.
