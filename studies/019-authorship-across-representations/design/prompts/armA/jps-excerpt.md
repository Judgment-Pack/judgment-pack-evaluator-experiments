# Judgment Pack Core `0.2.0-draft` — language reference

This is a reference for the Judgment Pack document format and its evaluation semantics. It
describes the language only. Every example below is a throwaway illustration from an unrelated
domain (a lending-library renewal desk, a greenhouse) and none of it is a template for the task
you have been given.

Section numbers (§) refer to the Judgment Pack Core `0.2.0-draft` specification, from which this
reference is derived, together with its normative JSON Schema. Where this reference and the
specification could be read differently, the specification controls.

---

## 1. Document skeleton

The carrier is a single JSON text (RFC 8259). The root MUST be an object. Object member names
MUST be unique. Only the members the specification defines for a given object may appear: an
unrecognized member makes the document non-conforming rather than being ignored.

Root members (§4):

| Member                 | Required | Meaning                                                |
| ---------------------- | -------: | ------------------------------------------------------ |
| `specVersion`          |      yes | Exact string `"0.2.0-draft"`                            |
| `id`                   |      yes | Stable absolute URI identifying the pack series         |
| `version`              |      yes | Three-component `MAJOR.MINOR.PATCH` revision string     |
| `title`                |      yes | Non-empty human-readable title                          |
| `description`          |       no | Human-readable overview                                 |
| `decision`             |      yes | Decision intent and question                            |
| `applicability`        |       no | Optional condition delimiting the pack's scope          |
| `evidenceRequirements` |       no | Declared inputs or proof obligations                    |
| `sources`              |       no | Located source material                                 |
| `outcomes`             |      yes | At least two possible outcomes                          |
| `rules`                |      yes | One or more rules                                       |
| `exceptions`           |       no | Typed exceptions to rules or normal resolution          |
| `fallbackOutcome`      |       no | Candidate outcome when normal rules yield no candidate  |
| `escalation`           |       no | Optional handoff configuration, not a decision outcome  |
| `metadata`             |       no | Authorship, license, creation, and review information   |
| `extensions`           |       no | Namespaced extension values                             |

Collection order is preserved for authoring and display but MUST NOT determine rule priority.
There is no priority field anywhere in the format (§4, §6.5).

A minimal, complete document:

```json
{
  "specVersion": "0.2.0-draft",
  "id": "https://example.org/packs/toy-renewal",
  "version": "0.1.0",
  "title": "Toy renewal example",
  "description": "Illustration only.",
  "decision": {
    "intent": "Show the smallest shape a document can take.",
    "question": "May this loan be renewed?"
  },
  "outcomes": [
    { "id": "renew", "label": "Renew" },
    { "id": "refer-to-staff", "label": "Refer to staff" }
  ],
  "rules": [
    {
      "id": "r-clean-loan",
      "description": "A loan with no holds is renewed.",
      "when": { "op": "fact", "path": "/loan/holds", "operator": "equals", "value": "none" },
      "outcome": "renew",
      "onUnknown": "ignore"
    }
  ]
}
```

### 1.1 Identifiers, versions, URIs

- The pack `id` MUST be an absolute URI (RFC 3986).
- `version` matches `MAJOR.MINOR.PATCH`, each component a non-negative integer without leading
  zeroes, e.g. `"0.1.0"`.
- Every local identifier — outcome, rule, exception, evidence-requirement, source — is a non-empty
  ASCII string matching `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`: lowercase kebab-case, e.g.
  `r-clean-loan`, `refer-to-staff`. Underscores, capitals, and trailing hyphens are refused.
- Identifiers are unique within their collection and are scoped to the pack version. **Meaning
  MUST NOT be inferred from the spelling of an identifier** (§5): an id is a label, and nothing an
  evaluator does depends on how it reads.
- There are no imports and no remote references. Every reference resolves inside one document
  (§5).

### 1.2 `decision`

```json
"decision": {
  "intent": "Explain the organizational purpose of the decision.",
  "question": "State the question this document is intended to resolve."
}
```

Both members are required non-empty strings (§6.1). The object MUST NOT embed prompts or
executable host-language code.

### 1.3 `metadata`

Optional (§6.8). Recognized members are `authors` (non-empty array of non-empty strings),
`createdAt` (RFC 3339 date-time, e.g. `"2026-01-31T00:00:00Z"`), `license`,
`requiredExtensions`, `reviews`, and `extensions`. These are author assertions and confer nothing.

```json
"metadata": {
  "authors": ["Toy example"],
  "createdAt": "2026-01-31T00:00:00Z"
}
```

### 1.4 `applicability`

An optional root-level **condition** (§4, §8 step 1) delimiting the pack's scope. An omitted
`applicability` is treated as the literal `true`. When it is present and false, evaluation
produces a terminal `not-applicable` result and no rule or exception is evaluated; when it is
unknown, evaluation produces `unresolved` with reason `unknown` and stops. Whether a pack in this
study may declare it is governed by the shared naming appendix, not by this reference.

### 1.5 `extensions` and `sources`

`extensions` is an object whose keys use reverse-domain naming (`com.example.some-capability`);
values may be any JSON. An optional extension MUST NOT change Core semantics. A capability named
in `metadata.requiredExtensions` must also appear as an `extensions` key, and an evaluator that
does not support it refuses the evaluation rather than producing a result (§9, §8.4).

`sources` records author-supplied provenance (`id`, `title`, a typed `locator`, optional
publisher, `publishedAt` date, `citation`, rights). Nothing in evaluation reads a source; Core
does not verify that a source exists or that an excerpt is accurate (§6.3).

---

## 2. `outcomes`

An array of at least two outcome objects (§6.4). Each has `id` (local identifier), `label`
(non-empty string), and optional `description`.

```json
"outcomes": [
  { "id": "renew", "label": "Renew" },
  { "id": "refer-to-staff", "label": "Refer to staff", "description": "A person decides." }
]
```

An outcome is a declared result, not an authorization to perform an external action. Every rule
outcome, exception outcome, and fallback outcome MUST name one of these declared ids (§3.3).

---

## 3. `evidenceRequirements`

An array of evidence-requirement objects (§6.2). Members:

- `id` — local identifier;
- `description` — what must be provided;
- `required` — boolean: whether absence prevents normal resolution;
- `kind` — optional, one of `document`, `fact`, `measurement`, `attestation`; descriptive only.

```json
"evidenceRequirements": [
  {
    "id": "borrower-card",
    "description": "A current borrower card on file.",
    "required": true,
    "kind": "document"
  },
  {
    "id": "damage-note",
    "description": "A condition note for the returned item.",
    "required": false,
    "kind": "document"
  }
]
```

The two settings of `required` behave very differently:

- **`"required": true`** — the requirement is inspected by §8 step 2 before any rule or exception
  effect can produce an outcome. Its availability can block resolution outright, and it does so
  with a reason that says which of the two blocking states it was in (see §5 below).
- **`"required": false`** — the requirement is never inspected by step 2. It affects evaluation
  only where some condition mentions it with `evidence-present` (§4.5). A pack may declare an
  optional requirement and consult it in a rule, or declare it and never consult it.

Availability is supplied per evaluation, not by the pack: see the evidence-availability document
in §6.1.

---

## 4. Conditions (§7)

A condition evaluates to **`true`, `false`, or `unknown`** — three-valued logic throughout. Six
condition shapes exist. Each is an object with an `op` member and exactly the further members its
shape defines; no other member may appear.

### 4.1 `literal`

```json
{ "op": "literal", "value": true }
```

Returns its Boolean `value`.

### 4.2 `all` — strong three-valued conjunction

```json
{
  "op": "all",
  "conditions": [
    { "op": "fact", "path": "/loan/holds", "operator": "equals", "value": "none" },
    { "op": "fact", "path": "/loan/daysOverdue", "operator": "less-than", "value": "8" }
  ]
}
```

- `false` if **any** child is false;
- `true` if **every** child is true;
- `unknown` otherwise.

Note the first clause: one false child makes the whole condition false even when another child is
unknown.

### 4.3 `any` — strong three-valued disjunction

```json
{
  "op": "any",
  "conditions": [
    { "op": "fact", "path": "/plot/zone", "operator": "equals", "value": "north" },
    { "op": "fact", "path": "/plot/zone", "operator": "equals", "value": "south" }
  ]
}
```

- `true` if **any** child is true;
- `false` if **every** child is false;
- `unknown` otherwise.

`conditions` is a non-empty array in both `all` and `any`, and may nest to any depth.

### 4.4 `not`

```json
{
  "op": "not",
  "condition": { "op": "fact", "path": "/plot/zone", "operator": "equals", "value": "north" }
}
```

`true` becomes `false`, `false` becomes `true`, and **`unknown` remains `unknown`** (§7.3). A
negation therefore does not convert missing information into a decision; it propagates it. The
single child member is named `condition` (singular), unlike `all`/`any`'s `conditions`.

### 4.5 `evidence-present`

```json
{ "op": "evidence-present", "evidenceRequirement": "damage-note" }
```

`true` when the evaluation input records the named requirement as available, `false` when it
records it as absent, and `unknown` when the input cannot say — that is, `present` → `true`,
`absent` → `false`, and `unknown`, **including an omitted key**, → `unknown` (§7.5, §6.1 below).
`evidenceRequirement` MUST name a declared requirement, required or not.

### 4.6 `fact`

```json
{ "op": "fact", "path": "/loan/daysOverdue", "operator": "greater-than-or-equal", "value": "8" }
```

Members: `path`, `operator`, `value`, all required.

`path` is RFC 6901 **JSON Pointer** syntax evaluated against the one runtime-supplied facts
document. `/loan/daysOverdue` selects member `daysOverdue` of member `loan`. The empty string
`""` selects the document root. **A syntactically valid pointer that does not resolve — an absent
member, an out-of-range or non-numeric array index — produces `unknown`** (§7.4). This is how an
omitted input reaches the logic: not as `null` and not as a sentinel, but as an unresolved
pointer, and therefore as `unknown`.

The admitted operators are `equals`, `not-equals`, `greater-than`, `greater-than-or-equal`,
`less-than`, `less-than-or-equal`, and `in`.

---

## 5. Operators in detail (§2.2, §7.4)

### 5.1 `equals` / `not-equals`

Type-preserving JSON equality, **with no coercion between JSON types**: null equals null;
Booleans and strings compare by value; JSON numbers compare by mathematical value; arrays compare
recursively in order; objects compare recursively by member name and value, member order
disregarded. `not-equals` is the Boolean inverse of `equals` wherever equality can be determined.

The string `"3"` and the number `3` are **not** equal — different JSON types, no coercion.

### 5.2 `in`

`value` is a non-empty array. The selected fact value is compared for equality (as above) with
each item; a match produces `true`, no match `false`.

```json
{ "op": "fact", "path": "/plot/zone", "operator": "in", "value": ["north", "south"] }
```

### 5.3 Ordered comparisons over decimal strings

`greater-than`, `greater-than-or-equal`, `less-than`, and `less-than-or-equal` are defined **only
over decimal strings**. The schema requires the operand to be a string matching:

```text
decimal = [ "-" ] ( "0" / non-zero-digit *DIGIT ) [ "." 1*DIGIT ]
```

So `"8"`, `"12.50"`, `"0"`, `"0.75"`, `"-3.5"` are decimals; `"08"` (leading zero), `"1e3"`
(exponent), `"+1"`, `"1."`, `"NaN"`, `""`, and the JSON number `12.5` are not.

An ordered comparison is **defined if and only if both the selected fact value and the operand are
JSON strings satisfying that grammar**; the two are then compared by mathematical value, so
`"12.50"` is greater than `"8"`. Any other selected value — **a JSON number**, a Boolean, null, an
array, an object, or a string outside the grammar — makes the comparison undefined and produces
**`unknown`**. A JSON number is deliberately *not* coerced: the grammar exists because a number's
decimal identity is not preserved, and silently accepting one would let two implementations
disagree (§7.4).

Consequences worth stating plainly:

- a quantity intended for ordered comparison must arrive in the facts document as a decimal
  **string**, and a value not in that form cannot be read — it yields `unknown`, not `false`;
- ordered comparison reads by mathematical value, so `"12.50"` and `"12.5"` compare as equal in
  magnitude and neither is greater than the other;
- but `equals` is **string** equality and is deliberately not decimal-aware, so `"12.50"` does not
  equal `"12.5"` and `not-equals` is correspondingly `true`. The two operator families answer
  different questions and Core defines no reconciliation between them; a pack needing decimal-aware
  equality must normalize scale in the pack and in the facts (§7.4);
- units, quantities carrying units, and date or time values have **no** ordered comparison here.

Within evaluator conformance, `unknown` from a fact condition comes from exactly three things: a
path that is absent or does not resolve; a selected value or operand whose shape the operator does
not admit; and a value the implementation cannot compare exactly (confined to JSON numbers outside
its exact range). It is not available anywhere else (§7.4).

---

## 6. Evaluation inputs (§8.2)

An evaluation takes the pack, **one JSON facts document**, **at most one evidence-availability
document**, and the implementation's supported-extension set.

```json
{ "loan": { "holds": "none", "daysOverdue": "3" } }
```

### 6.1 Evidence availability

A JSON object whose member names are declared `evidenceRequirements[].id` values and whose values
are exactly one of `"present"`, `"absent"`, `"unknown"`.

```json
{ "borrower-card": "present", "damage-note": "absent" }
```

- **An omitted key means `unknown`.** An omitted document as a whole is the implicit empty object,
  which makes every declared requirement `unknown`; that is not an error.
- A value that is not a JSON object, a member name that is not a declared requirement id, or a
  value outside those three strings is an **evaluation error**, not a result (§8.4).

Inputs are admitted in a preflight — pack, then facts, then evidence availability, then required
extensions — which completes before step 1 of the algorithm below, so no result can outrace an
input error.

---

## 7. The resolution model (§8)

Resolution produces one of three result kinds:

- an **`outcome`** result naming exactly one declared outcome;
- a **`not-applicable`** result carrying reason `not-applicable`, which is not an outcome;
- an **`unresolved`** result carrying one or more reasons.

The generated reason vocabulary is `not-applicable`, `missing-required-evidence`, `unknown`,
`conflict`, and `no-match`, matching the `escalation.triggers` vocabulary. A true exception with
effect `escalate` adds the separate reason `exception-escalation`, which is a direct request rather
than a trigger-selected one. Reasons are a **de-duplicated set** and a result may retain several;
their order carries no priority.

### 7.1 The algorithm, in order

1. **Applicability.** Omitted `applicability` is the literal `true`. False → terminal
   `not-applicable` with reason `not-applicable`, and neither exceptions nor rules are evaluated.
   Unknown → `unresolved` with reason `unknown`, and stop.
2. **Evidence step.** Inspect every requirement whose `required` is `true`, using the presence
   values of §4.5. Record `missing-required-evidence` **if and only if** at least one such
   requirement's presence is `false`. Record `unknown` **if and only if** at least one is `unknown`
   **and none is `false`**. (So the two reasons are mutually exclusive at this step, and absent
   dominates unknown.) Optional requirements are not inspected here.
3. **Exceptions are evaluated next.** Evaluate every exception condition and collect its effects.
   An unknown exception with `onUnknown: ignore` contributes no effect but remains unknown in a
   trace. An unknown exception with `onUnknown: escalate` records reason `unknown`.
4. **Combine true exception effects.**
   - all `suppress-rule` effects are compatible and suppress the union of their target rules;
   - `force-outcome` effects are compatible when they all name the same outcome and **conflict**
     when they name different outcomes;
   - suppression is compatible with a forced outcome;
   - one or more `escalate` effects are mutually compatible, record reason `exception-escalation`,
     and form a direct escalation request that **takes precedence over suppression and forced
     outcomes**.
5. **Blocking check.** Record `conflict` for incompatible forced outcomes. If step 2 recorded
   either of its reasons, or an exception is unknown with `onUnknown: escalate`, or exception
   effects conflict, or a true exception directly requests escalation, produce `unresolved` after
   all exception effects have been inspected, and **do not evaluate normal rules**. Every reason
   discovered at this stage is retained — so, for example, a missing-evidence reason and an
   `exception-escalation` reason can appear in the same result set.
6. **Forced outcome.** If one compatible forced outcome remains and no blocking state from step 5
   exists, produce that outcome **without evaluating normal rules**. Otherwise remove every
   suppressed rule and evaluate all remaining rules.
7. **Rules.** A true rule contributes its outcome as a candidate. A false rule contributes none.
   An unknown rule with `onUnknown: ignore` contributes no candidate and does not block
   resolution. An unknown rule with `onUnknown: escalate` records reason `unknown` and blocks both
   a candidate outcome and the fallback.
8. **Rule conflict.** Record `conflict` when true rules name more than one **distinct** outcome.
   If both an escalate-on-unknown rule and conflicting true rules are present, retain both
   `unknown` and `conflict`. Produce `unresolved` whenever either reason is present.
9. **Outcome.** If no blocking reason exists and true rules name one distinct outcome, produce it.
   Multiple true rules naming that same outcome are compatible — same-outcome overlap is not a
   conflict.
10. **Fallback / no match.** If no true rule contributes an outcome, use `fallbackOutcome` when
    present. False rules and unknown rules with `onUnknown: ignore` do not prevent this fallback.
    **If no fallback is present, produce `unresolved` with reason `no-match`.**

Thus `onUnknown: escalate` has blocking precedence over otherwise compatible outcomes at the same
resolution stage, while `onUnknown: ignore` never turns an unknown condition into false and does
not erase the unknown from a trace. **Array order, lexical id order, and implementation-defined
priority MUST NOT select among rule outcomes, and a conflict MUST NOT be tie-broken: it is an
`unresolved` result** (§8).

Two consequences of the step order are easy to miss and are stated in the specification:

- suppressing a rule removes that rule from evaluation; it does **not** change how any condition
  evaluates. A condition written in some other rule is unaffected by the suppression, whatever it
  tests;
- a compatible forced outcome is produced in step 6 **without evaluating normal rules at all**, so
  whatever the rules would have said, including whatever they would have found unknown, does not
  arise.

---

## 8. `rules` (§6.5)

`rules` is a non-empty array. A rule object requires `id`, `description`, `when`, `outcome`, and
`onUnknown`, and may carry `evidenceRequirementRefs`, `sourceRefs`, `rationale`, and `extensions`.

```json
{
  "id": "r-overdue-referral",
  "description": "A loan overdue by 8 days or more is referred to staff.",
  "when": {
    "op": "all",
    "conditions": [
      { "op": "fact", "path": "/loan/holds", "operator": "equals", "value": "none" },
      { "op": "fact", "path": "/loan/daysOverdue", "operator": "greater-than-or-equal", "value": "8" }
    ]
  },
  "outcome": "refer-to-staff",
  "onUnknown": "ignore"
}
```

- `when` is any condition of §4.
- `outcome` names a declared outcome id.
- `onUnknown` is exactly one of `"ignore"` or `"escalate"` and is **required on every rule**. Its
  meaning is step 7 above: `ignore` — an unknown rule contributes no candidate and blocks nothing;
  `escalate` — an unknown rule records reason `unknown` and blocks both a candidate outcome and
  the fallback. The choice is per rule; different rules in one pack may choose differently.
- The format has **no rule-priority field**, and array order carries no priority meaning. If two
  true rules name different outcomes the result is `conflict`, never the first or the "more
  specific" one. Mutual exclusion, if it is wanted, is written into the conditions.

---

## 9. `exceptions` (§6.6)

An exception object requires `id`, `description`, `when`, `effect`, and `onUnknown`, and may carry
`sourceRefs` and `extensions`. `effect` is exactly one of three, each with its own shape rule:

**`suppress-rule`** — `targetRule` is required, `outcome` MUST be absent. The named rule is
removed before rules are evaluated (step 6).

```json
{
  "id": "x-staff-hold",
  "description": "While a staff hold is recorded, the overdue-referral rule does not apply.",
  "when": { "op": "fact", "path": "/loan/staffHold", "operator": "equals", "value": "yes" },
  "effect": "suppress-rule",
  "targetRule": "r-overdue-referral",
  "onUnknown": "ignore"
}
```

**`force-outcome`** — `outcome` is required and names a declared outcome, `targetRule` MUST be
absent. A single compatible forced outcome is produced without evaluating normal rules (step 6);
two true force-outcome exceptions naming different outcomes are a `conflict` (steps 4–5).

```json
{
  "id": "x-frozen-account",
  "description": "A frozen account is always referred to staff.",
  "when": { "op": "fact", "path": "/loan/accountState", "operator": "equals", "value": "frozen" },
  "effect": "force-outcome",
  "outcome": "refer-to-staff",
  "onUnknown": "ignore"
}
```

**`escalate`** — both `targetRule` and `outcome` MUST be absent. A true escalate exception records
reason `exception-escalation`, produces `unresolved`, and takes precedence over suppression and
forced outcomes (steps 4–5).

```json
{
  "id": "x-disputed-item",
  "description": "A disputed item is escalated for a human determination.",
  "when": { "op": "fact", "path": "/loan/disputed", "operator": "equals", "value": "yes" },
  "effect": "escalate",
  "onUnknown": "escalate"
}
```

`onUnknown` is **required on every exception** and is `"ignore"` or `"escalate"`, with the meaning
of step 3: an unknown exception with `ignore` contributes no effect at all; an unknown exception
with `escalate` records reason `unknown`, which blocks resolution at step 5 before rules are ever
evaluated. Note that `onUnknown: escalate` records `unknown` — it does **not** record
`exception-escalation`, which only a *true* `escalate` effect produces.

Nothing prevents several exceptions from sharing a `when` condition, from targeting different
rules, or from combining a suppression with a forced outcome; step 4 says which combinations are
compatible.

---

## 10. `fallbackOutcome`

An optional root member naming a declared outcome id:

```json
"fallbackOutcome": "refer-to-staff"
```

It is consulted only at step 10, when no true rule contributed a candidate and nothing is
blocking. A pack may declare it or omit it; both are conforming, and step 10 defines both cases —
with it, the named outcome is produced; without it, the result is `unresolved` with reason
`no-match`. It is not a default for blocked resolutions: an unresolved result from steps 2, 5, 7,
or 8 is never converted into the fallback.

---

## 11. `escalation` (§6.7, §8.1)

Optional handoff configuration. It is **not** an outcome, and it cannot turn an unresolved result
into one.

```json
"escalation": {
  "triggers": ["missing-required-evidence", "unknown"],
  "target": { "kind": "human-role", "name": "Duty librarian" }
}
```

- `triggers` is a non-empty, duplicate-free set drawn from `not-applicable`,
  `missing-required-evidence`, `unknown`, `conflict`, `no-match`. Note that `exception-escalation`
  is **not** a member of this vocabulary.
- `target` requires `kind` — one of `human-role`, `queue`, `system` — and a non-empty display
  `name`. (This study's naming appendix pins the values a pack must use here; the example above is
  a throwaway.)
- optional `message` and `extensions` may also appear.

For a generated reason, the configured target is requested when `escalation` is present and at
least one retained reason appears in `triggers`. When several reasons match, exactly one handoff
request is created and it carries the complete retained reason set. A true `escalate` exception is
a **direct** request and uses the configured target regardless of the trigger list; made when the
pack carries no `escalation` object at all, it is still a requested handoff, with no Core-defined
destination.

When `escalation` is omitted there are no default triggers and no default target, and an
unresolved result simply stays unresolved.

---

## 12. The portable disposition (§8.3)

Each evaluation produces exactly one *disposition* — a JSON object with these members and no
others — or exactly one evaluation error and no disposition.

| Member      | Present                 | Value                                              |
| ----------- | ----------------------- | -------------------------------------------------- |
| `kind`      | always                  | `outcome`, `not-applicable`, or `unresolved`        |
| `outcomeId` | iff `kind` is `outcome` | the `id` of exactly one declared outcome            |
| `reasons`   | always                  | the retained reason set, serialized as a sorted array |
| `handoff`   | always                  | an object carrying the handoff state and its trigger |

- `not-applicable` and `unresolved` are not outcomes and MUST NOT be mapped onto one, defaulted to
  one, or flattened into the same field as `outcomeId`.
- `outcomeId` is present exactly when `kind` is `outcome` — **absent** otherwise, not `null` and
  not an empty string.
- `reasons` is a **set**: unordered, duplicate-free, drawn from `not-applicable`,
  `missing-required-evidence`, `unknown`, `conflict`, `no-match`, `exception-escalation`, and
  nothing else. It is empty **if and only if** `kind` is `outcome`. When `kind` is
  `not-applicable`, its one member is `not-applicable`.
- `handoff` is an object with `state` — `requested` when §8.1 makes a request (trigger-selected or
  a direct exception request, including one made with no `escalation` object), `none` otherwise;
  always present — and `triggeredBy`, present **if and only if** `state` is `requested`: a
  non-empty set holding every retained reason that appears in `escalation.triggers`, plus
  `exception-escalation` when a true `escalate` exception made a direct request. `triggeredBy` is
  always a subset of `reasons`, and is smaller than `reasons` whenever the trigger list does not
  name every retained reason.
- The disposition **does not** echo the configured escalation target.

Serialization: both sets are JSON arrays sorted ascending by Unicode code point with no
duplicates; an absent member is omitted, never `null`; member order carries no meaning; byte
comparison canonicalizes with RFC 8785. Two conforming implementations given the same inputs
produce byte-identical canonicalized dispositions.

Two illustrative canonicalized dispositions:

```json
{"handoff":{"state":"none"},"kind":"outcome","outcomeId":"renew","reasons":[]}
```

```json
{"handoff":{"state":"requested","triggeredBy":["missing-required-evidence"]},"kind":"unresolved","reasons":["missing-required-evidence"]}
```

### 12.1 Evaluation errors (§8.4)

An evaluation error is not a disposition, and an implementation MUST NOT substitute `unresolved`,
`not-applicable`, or a fallback outcome for one. Every error carries exactly one class, evaluated
in this fixed order: `pack-not-conformant`, `malformed-input`, `unsupported-required-extension`,
`resource-exhaustion`.

---

## 13. The test matrix (`matrixVersion` `"2"`)

A **matrix** is a separate JSON document that states, per case, what a disposition should be. It
is a project convention of the runtime rather than part of Core, and its rows share with the
bundled evaluation corpus the fields the comparator reads, so a row is judged by the same §8.3
byte comparison.

```json
{
  "matrixVersion": "2",
  "cases": [
    {
      "id": "clean-loan-renews",
      "facts": { "loan": { "holds": "none", "daysOverdue": "3" } },
      "evidenceAvailability": { "borrower-card": "present" },
      "expectedDisposition": {
        "kind": "outcome",
        "outcomeId": "renew",
        "reasons": [],
        "handoff": { "state": "none" }
      }
    },
    {
      "id": "card-unreported-is-unknown",
      "facts": { "loan": { "holds": "none", "daysOverdue": "3" } },
      "expectedDisposition": {
        "kind": "unresolved",
        "reasons": ["unknown"],
        "handoff": { "state": "requested", "triggeredBy": ["unknown"] }
      }
    },
    {
      "id": "undeclared-evidence-key-is-refused",
      "facts": { "loan": { "holds": "none" } },
      "evidenceAvailability": { "not-a-requirement": "present" },
      "expectedErrorClass": "malformed-input",
      "expectedErrorPhase": "preflight"
    }
  ]
}
```

Document members:

- `matrixVersion` — optional; when present it must be `"1"` or `"2"`, and an omitted version is
  read as `"1"`. Version `"2"` is what admits the `expectedHandoffTarget` member below.
- `cases` — the array of rows.

Row members:

- `id` — required, unique within the matrix, and named so a mismatch can be pointed at;
- `facts` — **required**: the facts document for this case, exactly as §6 describes it (an input
  that is meant to be absent is simply not written);
- `evidenceAvailability` — optional: the evidence-availability object of §6.1. Omitting it is the
  implicit empty object, i.e. every declared requirement `unknown`; omitting a single key is that
  key `unknown`;
- exactly **one** of `expectedDisposition` and `expectedErrorClass` — a disposition and an
  evaluation error are never both produced, so a row stating both is refused;
- `expectedDisposition` — the §8.3 disposition object the evaluation must produce: `kind`,
  `outcomeId` (present iff `kind` is `outcome`), `reasons`, `handoff` with `state` and, iff
  `state` is `requested`, `triggeredBy`. The row passes when the produced disposition
  canonicalizes to the same bytes as the row's, so `reasons` and `triggeredBy` are written as
  sorted, duplicate-free arrays;
- `expectedErrorClass` — one of the §8.4 classes; the row passes when the evaluation is refused
  with that class;
- `expectedErrorPhase` — optional beside a class: `preflight` or `evaluation`;
- `expectedHandoffTarget` — optional, and only beside `expectedDisposition` (it needs
  `matrixVersion: "2"`). An **object** with required non-empty `kind` and `name` asserts exactly
  that configured target; the literal **`null`** asserts that the evaluation reports no target;
  **absent** asserts nothing. It exists because §8.3 keeps the configured target out of the
  disposition;
- `supportedExtensions`, `origin`, `focus`, `specSection` — optional and decide nothing.

Unknown members are rejected rather than ignored, and so is a member spelled in another case:
`Facts` and `expectedDispositon` are refused, not read as the members they resemble.
