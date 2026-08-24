<!--
DESIGN DRAFT, NOT REGISTERED. Study 019 arm A suffix (instructions half).
Assembled prompt = [policy prose] + [NAMING-APPENDIX.md] + [generated/JPS-EXCERPT.md] + [this file].
Fairness rule this file is written under: it teaches the LANGUAGE and the REQUIRED OUTPUT
FORM only. It must never contain a worked example from the policy's own domain, any
threshold from the policy, any clause name, or any hint about how the policy's clauses
should be structured. Every example here is a toy in an unrelated domain.
-->

# Your task

You are given, above: a written policy, a naming appendix that fixes the identifiers you must
use, and the complete Judgment Pack Specification (JPS Core `0.2.0-draft`) with its normative
JSON Schema.

Write, in one reply, an executable implementation of that policy as a **Judgment Pack**,
together with a **test matrix** for it.

Working conditions, stated plainly so you can plan:

- **One attempt.** You have no tools, no file access, and no way to run either artifact
  before you answer. Nothing will be run for you and handed back. Do not ask questions.
- **Nothing is repaired for you.** Your reply is read exactly as written. A document that
  does not parse, or that the specification's validator rejects, is the answer you gave.
- Your pack will be checked with the specification's validator and then evaluated against
  inputs you have not seen, drawn from the same policy. Aim for a pack whose behaviour
  matches the policy text on **every** input the policy describes, not only on the cases you
  happen to think of.
- Read the policy as a lawyer would: the order in which its clauses apply, which clause
  governs where two could, and what it says happens when an input cannot be read, are all
  part of what you must implement.

## What the two artifacts are

**1. The pack.** One JSON document conforming to the JPS Core `0.2.0-draft` schema above. It
declares the decision, the evidence requirements, the outcomes, the rules, the exceptions and
the escalation configuration. The specification above is the whole language: the resolution
model (section 8) is what your pack will actually be run under, and the disposition it
produces (section 8.3) is what your pack is judged on.

**2. The test matrix.** One JSON document of instance rows for your pack: the inputs you would
want tested and the disposition you expect each to produce. The matrix is not part of the
specification — it is a runtime convention — so its format is given in full below.

## Pack rules for this task

- `specVersion` MUST be exactly `"0.2.0-draft"`.
- Use the identifiers in the naming appendix exactly: outcome ids, fact pointer paths,
  evidence requirement ids, escalation target kind and name, and the escalation trigger list.
- Do **not** declare an `applicability` member. (Stated in the naming appendix; repeated here
  because it is a refusal, not a preference.)
- Do **not** declare a `fallbackOutcome`.
- Facts reach your pack as the document described in the naming appendix; the availability of
  each evidence requirement reaches it as the separate evidence-availability document of
  specification section 8.2.
- Ordered comparisons (`greater-than`, `greater-than-or-equal`, `less-than`,
  `less-than-or-equal`) are defined over decimal strings — see section 7.4 and the naming
  appendix's wire forms.
- The pack must be self-contained: no extensions, no external references.

## The test-matrix format

A matrix is one JSON object:

- `matrixVersion`: the string `"2"`.
- `cases`: an array of rows. Each row has
  - `id` — unique within the matrix, named so a failure can be pointed at;
  - `facts` — the facts document for that row (**required**);
  - `evidenceAvailability` — optional; maps evidence requirement ids to `"present"` or
    `"absent"`. An omitted id means the availability is unknown;
  - exactly **one** of
    - `expectedDisposition` — an object with `kind` (`"outcome"` or `"unresolved"`),
      `outcomeId` when the kind is `outcome`, `reasons` (an array, empty for an outcome), and
      `handoff` (`{"state": "none"}`, or `{"state": "requested", "triggeredBy": [...]}`), or
    - `expectedErrorClass` — the evaluation-error class the row expects, optionally beside
      `expectedErrorPhase`;
  - `expectedHandoffTarget` — optional, and only beside `expectedDisposition`: an object with
    `kind` and `name` asserting that exact escalation target, or the literal `null` asserting
    that the evaluation reports no target.
  - `focus` — optional, one line saying what the row probes.

A row passes when the disposition produced is byte-identical (RFC 8785 canonical form) to the
row's `expectedDisposition`. Unknown members are rejected, and a misspelled member is an
error rather than a row that silently expects nothing.

## Toy example (unrelated domain — shape only)

The example below is about renewing a library loan. It exists to show you the *shape* of the
two documents and nothing else: its domain, its identifiers, its thresholds and its structure
have no relationship to the policy you were given.

```json
{
  "specVersion": "0.2.0-draft",
  "id": "https://example.org/judgment-packs/toy-library-loan-renewal",
  "version": "0.1.0",
  "title": "Library loan renewal (toy example, unrelated domain)",
  "description": "A deliberately tiny pack, shown only to fix the shape of the document.",
  "decision": {
    "intent": "Decide how a request to renew a library loan is handled.",
    "question": "May this loan be renewed?"
  },
  "evidenceRequirements": [
    {
      "id": "current-address",
      "description": "A confirmed current address for the member.",
      "required": true,
      "kind": "attestation"
    }
  ],
  "outcomes": [
    { "id": "renew", "label": "Renew the loan" },
    { "id": "refer-to-desk", "label": "Refer to the front desk" }
  ],
  "rules": [
    {
      "id": "r-not-overdue",
      "description": "A loan less than 14 days overdue renews.",
      "when": {
        "op": "fact",
        "path": "/loan/daysOverdue",
        "operator": "less-than",
        "value": "14"
      },
      "outcome": "renew",
      "onUnknown": "ignore"
    },
    {
      "id": "r-overdue",
      "description": "A loan 14 or more days overdue goes to the desk.",
      "when": {
        "op": "all",
        "conditions": [
          {
            "op": "fact",
            "path": "/loan/daysOverdue",
            "operator": "greater-than-or-equal",
            "value": "14"
          },
          {
            "op": "not",
            "condition": {
              "op": "fact",
              "path": "/member/status",
              "operator": "equals",
              "value": "staff"
            }
          }
        ]
      },
      "outcome": "refer-to-desk",
      "onUnknown": "escalate"
    }
  ],
  "exceptions": [
    {
      "id": "x-guest-card",
      "description": "A guest card is always handled at the desk.",
      "when": {
        "op": "fact",
        "path": "/member/status",
        "operator": "equals",
        "value": "guest"
      },
      "effect": "force-outcome",
      "outcome": "refer-to-desk",
      "onUnknown": "ignore"
    }
  ],
  "escalation": {
    "triggers": ["missing-required-evidence", "unknown"],
    "target": { "kind": "human-role", "name": "Front desk" }
  }
}
```

A matrix for that toy pack:

```json
{
  "matrixVersion": "2",
  "cases": [
    {
      "id": "renewed-when-recent",
      "facts": { "loan": { "daysOverdue": "3" }, "member": { "status": "member" } },
      "evidenceAvailability": { "current-address": "present" },
      "expectedDisposition": {
        "kind": "outcome",
        "outcomeId": "renew",
        "reasons": [],
        "handoff": { "state": "none" }
      },
      "expectedHandoffTarget": null
    },
    {
      "id": "address-absent-blocks-everything",
      "facts": { "loan": { "daysOverdue": "3" }, "member": { "status": "member" } },
      "evidenceAvailability": { "current-address": "absent" },
      "expectedDisposition": {
        "kind": "unresolved",
        "reasons": ["missing-required-evidence"],
        "handoff": { "state": "requested", "triggeredBy": ["missing-required-evidence"] }
      },
      "expectedHandoffTarget": { "kind": "human-role", "name": "Front desk" }
    },
    {
      "id": "overdue-day-14-is-the-boundary",
      "facts": { "loan": { "daysOverdue": "14" }, "member": { "status": "member" } },
      "evidenceAvailability": { "current-address": "present" },
      "expectedDisposition": {
        "kind": "outcome",
        "outcomeId": "refer-to-desk",
        "reasons": [],
        "handoff": { "state": "none" }
      }
    }
  ]
}
```

## Required output form

Think and explain as much as you like first; only the blocks below are read. End your reply
with **exactly** these two blocks, in this order:

    PACK:
    ```json
    <the complete pack document>
    ```

    MATRIX:
    ```json
    <the complete test matrix document>
    ```

- The marker is a line on its own containing exactly `PACK:` (and exactly `MATRIX:`),
  immediately followed by a fenced block.
- The fence may be ```` ```json ```` or a bare ```` ``` ````.
- If a marker appears more than once, **the last one is the one read**. Everything outside
  these two blocks is ignored.
- Each block must contain one complete JSON document and nothing else — no prose, no comments,
  no ellipsis, no placeholder.
