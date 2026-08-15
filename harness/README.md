# Post-hoc agreement harness

NOT part of the clean-room deliverable: this referee tooling knows both
implementations' output shapes and was added after the clean-room session
ended. It runs identical (pack, facts, evidence, supported-extensions)
inputs through the Go reference runtime and an implementation here (pass
its directory, e.g. `python/`, as the implementation argument) and diffs the
dispositions' semantic content (kind, outcomeId, reasons set, handoff
state).

`rfc0008_harness.py` is the same idea for draft RFC 0008's collection
quantifiers, with two differences the RFC forces: every case in
`rfc0008_cases.json` carries its own pack (the rows differ in the condition
under test, not only in the facts), and both implementations must be opted in
to the draft grammar. It also runs the equivalence check RFC 0008's
Conformance section asks for, over the assets in `rfc0008_equivalence/`.
Findings: `RFC0008-AGREEMENT.md`.

Result on 2026-07-27 against judgment-pack v0.2.0 and the
data-request-intake-triage example: 13/13 agreement (the nine RFC 0006
appendix instances plus three probes). One shape divergence recorded, not
counted as semantic: the disposition's handoff serialization
(object-with-target-echo vs bare string enum) is underdetermined by the
RFC -- see python/DECISIONS.md entry 3.

## The runtime pin, and when to move it

`class_agreement.py` takes a Go binary, so CI builds one from a **pinned, immutable
runtime commit** rather than a branch. A moving ref would let a change in another
repository decide, silently, whether this repository's cross-implementation evidence
still holds — and the whole point of the comparison is that a divergence is
adjudicated against the specification text, never by preferring whichever
implementation moved last.

To advance the pin: change the `ref` in the `evaluator-agreement` job to another
reviewed runtime commit, run the harness locally against it, and say in the pull
request what that commit changed about evaluation.

**The shape to refuse is a pin advanced together with a row's expectation in one
commit.** That is indistinguishable from making the evidence agree by moving the
thing it was evidence about.
