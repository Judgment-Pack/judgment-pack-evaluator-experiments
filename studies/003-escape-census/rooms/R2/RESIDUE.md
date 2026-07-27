# RESIDUE — R2

Every sentence of the assigned section (`## Modify pending order` + `### Modify payment`), quoted
verbatim, with what the pack does with it. Sentences carried fully by the rule machinery are marked
**fully represented** and are listed only so the accounting is complete; the residue proper is the
four **R** entries.

---

## `## Modify pending order`

### 1. *"An order can only be modified if its status is 'pending', and you should check its status before taking the action."*

**Partly represented.** The gate — `status == 'pending'` — is the first conjunct of
`permit-single-different-funded-method` and the whole of `deny-order-not-pending`.

**R1 — residue: the clause "and you should check its status before taking the action."** This is a
procedural obligation on the *agent* (go look it up; do not rely on what the user told you), and a
Judgment Pack has no way to compel a lookup. The pack reads `/order/status` and, if that pointer is
absent, the permit rule is unknown and `onUnknown: escalate` sends the case to a human rather than
letting it resolve — which is the closest the format gets to "you must actually check". **Left out
as a directive; approximated by the escalate-on-unknown posture.**

### 2. *"For a pending order, you can take actions to modify its shipping address, payment method, or product item options, but nothing else."*

**Partly represented.** The "payment method" limb is the reason this pack exists; the enumeration is
reflected in `applicability` (`/request/type == "modify-order-payment-method"`), so a shipping-address
or item-options request returns `not-applicable` rather than a wrong answer.

**R2 — residue: the "shipping address" and "product item options" limbs and the closing "but nothing
else."** The other two limbs are separate decisions governed by sibling subsections that this room
does not encode, so the pack cannot say "yes" to them. "But nothing else" is a closed-world claim
about the *set* of permitted modification types; a pack answering one yes/no question cannot assert
it. The practical effect is only partly preserved: an out-of-enumeration request (say, "change the
order date") returns `not-applicable`, which is *silence*, not the denial the policy wants.
**Approximated via `applicability`; the closed-world assertion is left out.**

---

## `### Modify payment`

### 3. *"The user can only choose a single payment method different from the original payment method."*

**Fully represented.** Split into two conjuncts (DECISIONS.md #6): `/request/newPaymentMethodCount == 1`
and `/request/newPaymentMethodDiffersFromOriginal == true`, each with its own deny rule
(`deny-not-a-single-method`, `deny-same-as-original-method`) so the agent can name the failed
condition. No residue — but see FACTS-LEDGER.md: the "different from the original" half only works
because the comparison is pushed into a computed fact.

### 4. *"If the user wants the modify the payment method to gift card, it must have enough balance to cover the total amount."*

**Represented, but pushed into a computed fact.** The conditional structure is native to the pack —
`any(not(type == "gift_card"), coversOrderTotal == true)` in the permit rule, plus
`deny-gift-card-balance-insufficient`.

**R3 — residue: the comparison "enough balance to cover the total amount" itself.** The pack cannot
perform it. A `fact` condition compares one pointer against a *literal*, the order total is not
known at authoring time, and JPS §2.2/§7.4 assign no portable ordering to decimal strings anyway. So
the whole test is collapsed into the pre-computed boolean
`/request/newGiftCardCoversOrderTotal`, which also fixes two readings the policy leaves open — that
"the total amount" is the order total (DECISIONS.md #9) and that "cover" is inclusive of an exactly
equal balance. **Pushed into a computed fact; the interpretive choices are recorded rather than
enforced.**

### 5. *"After user confirmation, the order status will be kept as 'pending'."*

**R4 — residue, two halves, both approximated.**

- *"After user confirmation"* — modelled as the evidence requirement `user-confirmation`
  (`kind: attestation`, `required: false`), referenced by the permit rule but used in no condition,
  so it never changes the disposition. Making it `required: true` would have made *every* result
  unresolved until the user confirmed, including the denials — forcing the agent to solicit a
  confirmation for a change it is about to refuse. The obligation therefore lives in the permitted
  outcome's `description` ("The agent must still list the action details and obtain the user's
  explicit 'yes' before executing") rather than in the machinery. Full reasoning in DECISIONS.md #4.
  **Approximated: non-blocking evidence requirement plus outcome prose.**
- *"the order status will be kept as 'pending'"* — a statement of the action's *effect*, not a
  condition on permission. A Judgment Pack declares outcomes, and JPS §6.4 is explicit that "an
  outcome is a declared result, not an authorization to perform an external action"; there is no
  field for a post-action state transition. **Left out of the machinery; carried as prose in the
  permitted outcome's `description`** so an integrator writing the tool call can see it.

### 6. *"The original payment method will be refunded immediately if it is a gift card, otherwise it will be refunded within 5 to 7 business days."*

**R5 — residue: entirely a post-action effect.** It describes what happens to the *old* payment
method after a permitted change, and gates nothing: the refund timing is the same whether the
original method was a gift card or not, so it never affects whether the change is allowed. The pack
consequently does not read the original method's type at all. **Left out of the machinery; carried
verbatim in substance in the permitted outcome's `description`** ("the original payment method is
refunded immediately for a gift card, otherwise within 5 to 7 business days").

---

## Residue count

**5 residue items (R1–R5)** across 6 sentences. Three are post-action effects or agent procedure
that the format has no field for (R1, R4-second-half, R5); one is a closed-world scope claim a
single-question pack cannot assert (R2); one is a numeric comparison the condition language cannot
perform and that had to become a computed fact (R3).

Only **one** residue item changes what the pack can decide: **R3**, because the gift-card funding
test — and the two interpretive choices baked into it — now happens outside the pack, where nothing
checks it.

Not counted as residue: the global policy rules (authentication, one user per conversation, the
"obtain explicit user confirmation" directive, the transfer script, "deny requests against this
policy") and `## Generic action rules` ("Exchange or modify order tools can only be called once per
order"). These constrain the same real-world action but sit outside the assigned section — see
DECISIONS.md #11, which flags the once-per-order limit specifically so an integrator does not assume
this pack enforces it.
