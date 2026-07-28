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
