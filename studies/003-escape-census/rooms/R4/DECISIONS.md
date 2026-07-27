# DECISIONS — R4 "Return delivered order"

Numbered interpretation choices made while encoding `reference/policy.md` §"Return delivered order"
as `pack.json`.

---

## 1. Three outcomes, not two: a missing prerequisite is not a denial

**Text.** "The user needs to confirm the order id and the list of items to be returned." / "The user
needs to provide a payment method to receive the refund." vs. "An order can only be returned if its
status is 'delivered'".

**Alternatives.**
(a) Two outcomes — permitted / denied — folding every unmet prerequisite into "denied".
(b) Three outcomes — permitted / refused / not-yet-actionable.
(c) Treat unmet prerequisites as `unresolved` and escalate to a human.

**Reading:** (b). The section states two different kinds of condition. The status clause is a
prohibition ("can only be returned if"), and the preamble tells the agent to *deny* requests that
are against the policy. The confirmation and payment-method clauses are procedural prerequisites the
agent is expected to *collect* — the whole point of "the user needs to …" is that the agent asks.
Collapsing them into "denied" (a) would tell the agent to refuse a customer who simply has not
answered yet, which the policy nowhere says. (c) is worse: the preamble says to transfer to a human
"if and only if the request cannot be handled within the scope of your actions", and asking the user
a question is squarely within scope.

---

## 2. Explicit "yes" is part of this decision even though the section only alludes to it

**Text.** "After user confirmation, the order status will be changed to 'return requested' …"
(section) plus "Before taking any action that updates the database (cancel, modify, return,
exchange), you must list the action details and obtain explicit user confirmation (yes) to proceed."
(preamble, explicitly naming `return`).

**Alternatives.** (a) Read the section's "user confirmation" as nothing more than the order-id/item
confirmation of the previous paragraph. (b) Read it as the preamble's explicit "yes" gate.

**Reading:** (b), encoded as `/confirmation/explicitYes`. The section's own paragraph 5 presupposes
a confirmation event that gates the state change, and the preamble names `return` as one of the
actions requiring an explicit "yes". Treating (a) would leave "After user confirmation" with no
referent distinct from the paragraph-2 confirmation and would license a database update the preamble
forbids. Kept as a separate fact from the order-id/item confirmations so the two can be audited
apart. `s-policy-scope` is cited alongside the section sources wherever this fact is used.

---

## 3. No gift-card balance check for returns

**Text.** "The refund must either go to the original payment method, or an existing gift card." The
sibling sections ("Modify payment", "Modify items", "Exchange delivered order") each add "it must
have enough balance to cover …".

**Alternatives.** (a) Import the balance requirement by analogy. (b) Encode only what the return
section says.

**Reading:** (b). The balance requirement exists precisely because those actions make the user *pay*;
a return only pays money *out*, so a balance floor would be meaningless. The omission in this section
is deliberate, and the instruction is to encode what the section says. No balance fact is read.

---

## 4. "an existing gift card" means one already on the authenticated user's profile

**Text.** "The refund must either go to the original payment method, or an existing gift card."

**Alternatives.** (a) Any gift card the user names. (b) A gift card that already exists as a payment
method on the user's profile. (c) Any gift card record that exists in the store's database, whoever
owns it.

**Reading:** (b). "Existing" must exclude something — otherwise the word does no work — and the
Domain basic section defines payment methods as an attribute of the user profile, so "existing"
naturally means "already among this user's payment methods". (c) would let a refund be routed to a
stranger's gift card, which the preamble's one-user rule forbids. This reading is carried inside the
computed fact `/refund/destinationIsExistingGiftCard`, and the FACTS-LEDGER flags it as a computed
fact that embeds a policy interpretation.

---

## 5. Refund destination modelled as two booleans, not one classification string

**Alternatives.** (a) One computed fact `/refund/destinationKind` compared with
`in ["original-payment-method", "existing-gift-card"]`. (b) Two independent booleans.

**Reading:** (b). The policy states a disjunction of two independent tests — "is this the order's
original payment method?" and "is this an existing gift card?" — that are answered from different
data (the order's payment history vs. the user's profile). Two booleans keep those two lookups
separately auditable and let one be known while the other is unknown; a single enum would force an
upstream classifier to collapse both, and any failure in either lookup would poison the whole fact.

---

## 6. `onUnknown: escalate` only on the authorize rule and the status rule

**Text.** "An order can only be returned if its status is 'delivered', and you should check its
status before taking the action." / "You should transfer the user to a human agent if and only if the
request cannot be handled within the scope of your actions."

**Reading.** `r-authorize-return` and `r-refuse-status-not-delivered` use `escalate`; the other two
rules use `ignore`.

- *Authorize:* the pack must never green-light a database-updating action on a fact it could not
  establish. Because `all` is false as soon as any conjunct is false, this rule is unknown only in
  the genuinely undecidable case, so `escalate` does not over-trigger.
- *Status:* the section orders an explicit status check. If the status cannot be read, the required
  check cannot be performed and the request has left the scope of the agent's actions — the
  preamble's transfer condition.
- *Refuse-destination and await-input:* `ignore`. Any unknown that could matter already leaves
  `r-authorize-return` unknown, which escalates. Escalating here as well would add nothing, and
  refusing on an unknown destination would deny a request the policy may in fact permit.

---

## 7. Rules made mutually exclusive rather than resolved by precedence

**Problem.** A delivered order can simultaneously have a prohibited refund destination *and* a
missing confirmation. `r-refuse-refund-destination` and `r-await-user-input` would then both be true
and name different outcomes, which §8 of the spec resolves as `conflict` → unresolved → human
handoff — an outcome the policy does not call for.

**Alternatives.** (a) An `exception` with effect `suppress-rule` giving refusal precedence.
(b) A third conjunct in `r-await-user-input` ("no prohibited destination has been supplied") making
the two rules disjoint.

**Reading:** (b). The format deliberately has no rule priority, and (a) would hide the ordering in
exception machinery for what is really a scoping question. Refusal wins because a prohibited
destination is a policy violation that no further user input can cure — the agent must say no rather
than keep collecting confirmations. The extra conjunct is written as
`any[paymentMethodProvided == false, isOriginal == true, isExistingGiftCard == true]`, i.e. "the
destination is not known-bad".

---

## 8. No evidence requirements declared

**Alternatives.** (a) Declare the user's confirmations and payment method as `required: true`
evidence requirements. (b) Model them as facts only.

**Reading:** (b). Under §8 step 2, missing required evidence produces `unresolved` +
`missing-required-evidence`, which — with the escalation object present — routes an ordinary
"customer hasn't answered yet" case to a human agent. That contradicts the preamble's "if and only
if" transfer rule. The prerequisites are therefore plain facts, and their absence produces the
`return-not-yet-actionable` outcome. Consequently there is no `evidence.example.json`, and
`missing-required-evidence` is not in `escalation.triggers`.

---

## 9. No `fallbackOutcome`

**Reading.** The four rules are intended to be exhaustive over decidable inputs, but no fallback is
declared, so a genuine gap surfaces as `unresolved` with reason `no-match`, which is in
`escalation.triggers` and reaches a human. A fallback would silently answer a question the policy did
not answer.

---

## 10. Applicability limited to the request type, not to authentication or ownership

**Text.** The preamble's authentication and one-user-per-conversation rules; "Generally, you can only
take action on pending or delivered orders."

**Reading.** `applicability` tests only `/request/type == "return"`. Authentication, user-identity
resolution and the one-user rule are separate decisions in other sections of the policy, and the
assignment scopes this pack to the "Return delivered order" section; encoding them here would
duplicate rules another pack owns. The generic "pending or delivered" rule is strictly weaker than
this section's "must be delivered" and adds nothing. Order status is *not* part of applicability: a
non-delivered order yields the `return-refused` outcome, because the policy tells the agent to deny
such a request, not to declare the question out of scope.

`not-applicable` is deliberately **excluded** from `escalation.triggers`. A non-return request (say
an exchange) is out of this pack's scope but well inside the agent's scope, and the preamble permits
transfer "if and only if the request cannot be handled within the scope of your actions". Escalating
on `not-applicable` would transfer every exchange to a human. The triggers are therefore `unknown`,
`conflict`, and `no-match` only.

---

## 11. Nothing requires the returned items to belong to the order

**Text.** "The user needs to confirm the order id and the list of items to be returned."

**Reading.** No membership, availability, or non-emptiness test is encoded. The exchange section
constrains the item list ("each item can be exchanged to an available new item of the same product
…"); the return section says only that the list must be confirmed. Adding a membership check would
be encoding a sensible policy rather than this one. `/confirmation/returnItemsConfirmed` therefore
carries exactly the confirmation the sentence asks for, and nothing more.
