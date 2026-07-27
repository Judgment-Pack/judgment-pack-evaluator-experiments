# Post-hoc agreement harness

NOT part of the clean-room deliverable: this referee tooling knows both
implementations' output shapes and was added after the clean-room session
ended. It runs identical (pack, facts, evidence, supported-extensions)
inputs through the Go reference runtime and this package and diffs the
dispositions' semantic content (kind, outcomeId, reasons set, handoff
state).

Result on 2026-07-27 against judgment-pack v0.2.0 and the
data-request-intake-triage example: 13/13 agreement (the nine RFC 0006
appendix instances plus three probes). One shape divergence recorded, not
counted as semantic: the disposition's handoff serialization
(object-with-target-echo vs bare string enum) is underdetermined by the
RFC -- see DECISIONS.md entry 3.
