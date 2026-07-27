# RESIDUE — A5 "Change passengers"

The assigned section is two sentences. Both appear below: one is fully represented, one is only
approximated. Residue count: **1**.

---

## 1. Fully represented (no residue)

> "The user can modify passengers but cannot modify the number of passengers."

Represented by rule `allow-detail-change` (count unchanged -> `allow-passenger-modification`) and
rule `deny-count-change` (count changed -> `refuse-passenger-count-change`), both citing
`policy-change-passengers-user`.

The one thing the pack cannot do itself is *decide whether the count changes* — JSON-Pointer fact
conditions compare a pointer against a literal and cannot compare two pointers to each other, so
"len(requested roster) == len(current roster)" cannot be written as a condition. That comparison is
pushed into the computed fact `/derived/changesPassengerCount` and is documented as such in
FACTS-LEDGER.md. This is a mechanical relocation of a comparison, not lost meaning, so it is not
counted as residue.

## 2. Approximated — RESIDUE

> "Even a human agent cannot modify the number of passengers."

**What this sentence does.** It is not a decision rule. It is a statement about the *futility of
escalation*: it forecloses the handoff route that the document's own transfer rule ("transfer the
user to a human agent if and only if the request cannot be handled within the scope of your
actions") would otherwise open for a request the automated agent must refuse.

**Why it cannot be fully represented.** JPS `0.1.0-draft` has no construct for "this outcome is
terminal" or "never hand this case to a human". The `escalation` object (§6.7) is a *trigger list*
keyed to generated reasons — `not-applicable`, `missing-required-evidence`, `unknown`, `conflict`,
`no-match`. There is no reason code for "a rule produced a refusal", so there is no trigger to
withhold, and therefore no machine-checkable way to assert that a refusal must not be escalated. §8
even runs the other way: a true exception with effect `escalate` reaches the configured target
"regardless of the trigger list", so the format is built to make escalation easier to add than to
forbid.

**What was done instead — three partial measures, none of them enforcement:**

1. **Structural.** Encoded as the exception `count-change-not-overridable` with effect
   `force-outcome`. Under §8 step 6 a forced outcome is produced "without evaluating normal rules",
   so the refusal preempts ordinary resolution rather than merely competing with it. This is the
   closest the format comes to "absolute".
2. **By omission.** No escalation trigger can fire on this path: when the count fact is known the
   result is an `outcome`, and an `outcome` result generates no reason at all, so
   `escalation.triggers` is never consulted. Correct behaviour, but it holds by construction rather
   than by an assertion a validator could check.
3. **Prose.** The `refuse-passenger-count-change` outcome description says the refusal "must not be
   transferred to a human agent for approval, because a human agent cannot modify the number of
   passengers either", and `escalation.message` repeats the bar for the one path that *does* reach a
   human (the `unknown` path, where the human is being asked to clarify the roster, not to approve a
   count change). Both are human-readable text with no evaluator semantics.

**Residual risk.** A runtime that adds its own "offer transfer on refusal" behaviour, or an operator
who wires a manual override on top of the pack, would violate this sentence and nothing in the
document would detect it.
