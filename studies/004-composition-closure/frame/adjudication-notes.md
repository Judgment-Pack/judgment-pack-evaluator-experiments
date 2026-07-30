# Frame-pass adjudication — Study 004

Two classifiers applied the frame rule of [`../PREREGISTRATION.md`](../PREREGISTRATION.md) §2
independently (classifier 1: OpenAI Codex; classifier 2: a Claude agent; raw outputs beside this
file). Agreement: 39/40 on Unit F, 51/55 on Unit R. Five membership disagreements and two
clause-span differences were adjudicated against the rule's letter; agreements stand unreviewed,
as the protocol requires.

## Membership disagreements (5)

1. **Unit F — A6 `/cancellation/reasonCoveredByInsurance` → out.** Classifier 2 marked it in
   because the A6 ledger says insurance coverage is defined only in the Book-flight section.
   The rule's operative test is that the fact is a different inventory decision's *answer*.
   A1's decision question is "may this booking be made?" — it never answers "is this reason
   covered?". Applying policy text *housed in* another decision's section is a shared-source
   dependency, not consumption of that decision's verdict. This distinction — shared
   definitions versus outcome references — recurs below and is worth carrying into the study's
   discussion: the frame rule deliberately captures only the latter.
2. **Unit R — A3 index 4 ("…the user is should be refunded the difference") → in.**
   Classifier 2 read it as A3's own arithmetic. The sentence creates a refund entitlement that
   the refunds decision (A7) adjudicates — structurally identical to the canonical A1 insurance
   item ("enables full refund if…"), which both classifiers marked in. Consistency with the
   rule's "entitlement from … the outcome of a different inventory decision" requires the same
   verdict for the same shape.
3. **Unit R — A6 index 4 ("The refund will go to original payment methods within 5 to 7
   business days") → out.** Execution mechanics of this decision's own permitted outcome —
   routing and timing — reference no inventory decision's outcome. The room's remark that
   encoding refund routing "would need a second pack" is real composition pressure, but it is
   outside this rule; recorded here so it is not lost.
4. **Unit R — A7 index 4 (the "Refunds and Compensation" heading) → out.** The note records
   that A7's refund rules live in other policy sections — a statement about text location, not
   about consuming another decision's outcome. A7's operational dependency on the cancellation
   outcome is already in the frame as A7 index 2.
5. **Unit R — R2 index 1 ("…but nothing else") → out.** A closed-world enumeration of other
   decisions' *subjects* (which request types exist), not a reference to any decision's
   *outcome*.

## Clause-span adjudications (2)

- **A1 index 3:** "is not refundable" (classifier 2's span) — the minimal span carrying the
  refund-decision reference; the subject (the certificate's remaining amount) is this
  decision's own content and binds from the sentence.
- **A7 index 2:** "changing or cancelling the reservation" (classifier 2's span) — the minimal
  span referencing the change/cancel decisions; the confirmation duty around it is A7's own
  procedure.

## The frozen membership

**Unit F: 0 of 40. Unit R: 5 of 55** — A1 3, A1 7, A3 4, A7 2, R3 1
([`adjudicated.json`](adjudicated.json) carries every per-item marking).

The zero on Unit F is a result the preregistration anticipated by requiring membership be
reported at any size: under the rule's letter, none of the census's 40 prepared determinations
is a frozen inventory decision's transcribed verdict. They are sub-decision preparations —
quantifications, lifecycle mappings, coverage judgments against shared definitions — upstream
*of* inventory decisions but not themselves the answer *to* one. The cross-decision escape this
study can measure lives in the residue sentences: forward entitlements, act-coupling, and
cross-decision terminality.
