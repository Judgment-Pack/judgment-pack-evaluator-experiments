<!--
DESIGN DRAFT, NOT REGISTERED. Study 019 arms B and C, shared task head.
This file is BYTE-IDENTICAL in both arms' prompts. The arms differ only in the block
inserted between this file and REGO-TASK-TAIL.md (arm B: the prose result contract;
arm C: the same contract as a JSON Schema plus the prescribed judgment convention).
Fairness rule: teaches the LANGUAGE and the REQUIRED OUTPUT FORM only. No example from
the policy's domain, no threshold from the policy, no clause name, no hint about how the
policy's clauses should be structured. Every example here is a toy in an unrelated domain.
-->

# Your task

You are given, above: a written policy, a naming appendix that fixes the identifiers you must
use, and the Rego language documentation for the pinned version of OPA you will be run under.

Write, in one reply, an executable implementation of that policy as a **Rego policy**,
together with a **test suite** for it.

Working conditions, stated plainly so you can plan:

- **One attempt.** You have no tools, no file access, and no way to run either artifact
  before you answer. Nothing will be run for you and handed back. Do not ask questions.
- **Nothing is repaired for you.** Your reply is read exactly as written. A policy that does
  not parse, or that the checker rejects, is the answer you gave.
- Your policy will be checked with `opa check --strict` under a restricted capabilities file
  and then evaluated against inputs you have not seen, drawn from the same policy. Aim for a
  policy whose behaviour matches the policy text on **every** input the policy describes, not
  only on the cases you happen to think of.
- Read the policy as a lawyer would: the order in which its clauses apply, which clause
  governs where two could, and what it says happens when an input cannot be read, are all
  part of what you must implement.

## What the two artifacts are

**1. The policy.** One self-contained Rego file. Its package and its decision entrypoint are
fixed by the naming appendix. It is evaluated once per input document, and the value of that
entrypoint is the whole of what your policy is judged on.

**2. The test suite.** One separate Rego file of `test_`-prefixed rules, run with `opa test`
alongside your policy. Write the rows you would want run against a policy of this kind.

## Rules for this task

- **Rego v1** (the pinned OPA 1.x default dialect). Policies written in the v0 dialect are
  rejected.
- The package name and the entrypoint rule name are the naming appendix's, exactly. The
  entrypoint is evaluated as the appendix states.
- The policy must be **one self-contained file**: no imports of other packages you define, no
  external data documents, no `data.` references other than your own package's rules.
- Only the built-in functions listed in the "Built-in functions admitted by this environment"
  section above may be used. Any other built-in is refused when the policy is checked.
- The checker runs with `--strict`: unused imports and unused local variables are errors, not
  warnings.
- Inputs reach your policy on the `input` document in the shape the naming appendix fixes,
  with numeric fields as JSON numbers. A member that is unreadable or unreported is **absent**
  from the input document — never null, never a sentinel value.
- Your test file may use its own package name and may reference your policy's package.

## Toy example (unrelated domain — shape only)

The example below is about renewing a library loan. It exists to show you the *shape* of the
two files and nothing else: its domain, its identifiers, its thresholds and its structure have
no relationship to the policy you were given.

```rego
package toy

# A tiny example in an unrelated domain, shown only to fix the shape of the answer.

decision := {"disposition": "renew", "reasons": []} if {
	input.loan.daysOverdue < 14
}

decision := {"disposition": "refer-to-desk", "reasons": []} if {
	input.loan.daysOverdue >= 14
}
```

A test file for that toy policy:

```rego
package toy_test

import data.toy

test_recent_loan_renews if {
	toy.decision == {"disposition": "renew", "reasons": []} with input as {"loan": {"daysOverdue": 3}}
}

test_long_overdue_loan_goes_to_the_desk if {
	toy.decision.disposition == "refer-to-desk" with input as {"loan": {"daysOverdue": 14}}
}
```
