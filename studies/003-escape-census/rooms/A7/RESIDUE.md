# Residue — A7 Refunds and Compensation

The assigned section is lines 154-167 of `reference/policy.md`. Every sentence in it is listed
below, with what happened to it. Sentences that are fully represented are marked as such; the
genuine residue is items R1, R2 and R3.

## Fully represented

1. *"Do not proactively offer a compensation unless the user explicitly asks for one."*
   → rule `deny-not-requested`, and the `/request/compensationExplicitlyRequested == true` conjunct
   inside both grant rules. Source `policy-no-proactive-offer`.

2. *"Do not compensate if the user is regular member and has no travel insurance and flies (basic)
   economy."*
   → exception `excluded-regular-uninsured-economy` (`force-outcome: no-compensation`).
   Source `policy-exclusion-regular-economy`.

3. *"Only compensate if the user is a silver/gold member or has travel insurance or flies
   business."*
   → rule `deny-ineligible` for the negative direction, plus the `any` eligibility conjunct inside
   both grant rules and inside `deny-other-reason`. Source `policy-eligibility`.

4. *"Do not offer compensation for any other reason than the ones listed above."*
   → rule `deny-other-reason` plus `fallbackOutcome: no-compensation`, so nothing outside the two
   enumerated grounds can produce a certificate. Source `policy-no-other-reason`.

5. The *"$100 times the number of passengers"* and *"$50 times the number of passengers"* clauses
   → carried on the outcomes as human-readable `description` text and as the optional extension
   `io.onword.compensation` (`amountPerPassengerUsd`, `formula`), with `/reservation/passengerCount`
   read as a gate so the pack refuses to name a certificate outcome it cannot size.
   Note: Core `0.1.0-draft` outcomes are labels, not computed values, so the arithmetic itself is
   not executed by the pack. This is a Core limitation rather than a policy sentence left out; the
   multiplier is fully preserved.

## Residue

### R1 — "Always confirms the facts before offering compensation."

Quoted verbatim: *"Always confirms the facts before offering compensation."*

**What I did instead: pushed into an evidence requirement plus a computed fact, and approximated
the ordering.** The pack declares evidence requirement `facts-confirmed` (`kind: attestation`,
`required: false`) and both grant rules carry `{"op": "evidence-present", "evidenceRequirement":
"facts-confirmed"}`. What survives is a *check that someone attested to having confirmed the
facts*. What does not survive:

- the word **"always"** in its strong sense — the requirement is `required: false`, so a case can
  resolve to `no-compensation` without any confirmation having happened. Making it `required: true`
  would, under §8 step 5, turn every unconfirmed case (including plain refusals) into
  `unresolved`/`missing-required-evidence`, which would be a worse misreading: the policy asks you
  to confirm before *offering*, not before *declining*.
- the word **"before"** — Core has no temporal ordering between an evidence check and an outcome.
  The pack can only require that the attestation is present at evaluation time; it cannot express
  that confirmation preceded the offer.
- **what "the facts" are** — Core cannot enumerate them structurally. They are spelled out in the
  evidence requirement's prose description and are partly absorbed into the computed facts
  `/complaint/aboutCancelledFlights` and `/complaint/aboutDelayedFlights`, both of which already
  require verifying the flight statuses against records.

### R2 — the "refunds" half of the section title

The section is titled **"Refunds and Compensation"** and my assigned decision question is *"Is the
user owed a refund or compensation, and what kind?"*. **The body of the section contains no
sentence about refunds at all** — every one of its seven sentences is about compensation gestures.

**What I did instead: left the refund half out, deliberately, and said so in the pack.** The pack's
`description` states that the section defines only certificate gestures and that the pack therefore
never asserts a refund. The two refund rules that exist in the policy live in sections I was told to
treat as context — *"The refund will go to original payment methods within 5 to 7 business days."*
(## Cancel flight) and *"If the price after cabin change is lower than the original price, the user
is should be refunded the difference."* (## Modify flight) — so encoding them here would be
importing text from outside my assignment. A user who is owed a refund but not a compensation
gesture will get `no-compensation` from this pack; that is the correct answer to the question the
section actually answers, and the pack's description says so, but it is a real gap against the
literal decision question.

### R3 — "the agent can offer" (discretion)

Quoted verbatim, from both grant sentences: *"the agent **can** offer a certificate as a
gesture"*.

**What I did instead: approximated permission as a determination.** Core outcomes are declared
results, and §6.4 is explicit that an outcome "is not an authorization to perform an external
action". So `certificate-cancelled-flight` and `certificate-delayed-flight` should be read as *"a
certificate of this size is permitted here"*, not *"offer it"*. The residual discretion — the agent
may still decline a permitted gesture — is not representable; the pack has no third value between
"permitted" and "refused". This is recorded in the outcome labels ("Offer travel certificate ...")
which overstate the modality slightly, and in DECISIONS.md #6.

## Sentences from the section not otherwise accounted for

None. Lines 154-167 contain exactly the seven substantive sentences addressed above (the heading
itself is R2).
