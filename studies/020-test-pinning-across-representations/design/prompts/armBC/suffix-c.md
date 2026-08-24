<!-- Study 019 prompt suffix, arm C. Assembled prompt = policy prose + naming appendix + rego-excerpt.md + this file.
    Assembly rule: HTML comments are stripped from every material before the assembled prompt is shown to an author. -->
<!-- SHARED:1:begin -->
# Your task

Working from the policy stated above, author both of the following.

**(a) One Rego v1 policy** that implements that policy. Put the whole policy in the package
`study`, and make the decision entrypoint the rule `decision`, so that the policy's answer
for a case is the value of `data.study.decision` when that case is supplied as `input`. The
shape of `input` is the one given in the naming appendix.

**(b) OPA tests** for that policy, in a separate file. Write them as `test_`-prefixed rules
that supply a case with `with input as {...}` and assert the value of the entrypoint. Cover
the cases you consider decisive for showing that your policy is faithful to the prose; there
is no required number of tests.

Both files are saved side by side in one directory and run with the pinned OPA v1.19.0
binary (Rego v1 is its default dialect): the policy is evaluated per case, and the tests are
run with `opa test .`. Use only ordinary language constructs and built-in functions — no
built-in that reads the clock, the network, or a source of randomness is available.

Everything you need to know about the decision the policy makes is in the prose above. The
material below fixes only the form of the answer.
<!-- SHARED:1:end -->

<!-- EMBED:begin -->
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
<!-- EMBED:end -->

<!-- SHARED:2:begin -->
# Output format

Reply with exactly two blocks, in this order:

1. a line containing only `POLICY:`, immediately followed by a fenced code block tagged
   `rego` containing the complete policy file;
2. a line containing only `TESTS:`, immediately followed by a fenced code block tagged
   `rego` containing the complete test file.

Like this:

    POLICY:
    ```rego
    package study

    # ... your policy ...
    ```

    TESTS:
    ```rego
    package study_test

    # ... your tests ...
    ```

Each fenced block must be a complete, self-contained Rego file, starting with its own
`package` line. You may write whatever explanation you like outside the two blocks; it is
not read. If a marker line appears more than once, **the last occurrence of each marker
governs** — so if you revise your answer, emit the marker and its block again at the end.
<!-- SHARED:2:end -->
