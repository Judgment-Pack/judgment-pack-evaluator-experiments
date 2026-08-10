# Detection matrix — Study 015

Per-cell, per-layer outcome adjudicated against the registered expectations.
Every registered cell appears; nothing is excluded. Only `endpoint` rows of the
locked stratum count toward R1; `control-gate` rows are validity gates, and
`demonstration` and `descriptive` rows count toward nothing.

`not-engaged` means the replayed upstream policy functions had nothing in that
construction to decide — it is not an endorsement. `Suppressed` lists every
further binding code that also fired; adjudication is on the first one alone.

## Locked replication

| Cell | Role | Attacker | Replayed | UPSTREAM | BINDING | REPLAY | Combined | Registered | Divergence | Suppressed |
|---|---|---|---|---|---|---|---|---|---|---|
| `pos-baseline` | control-gate | none | classifyTool, AutoApprovalDrainer | `pass` | `pass` | `pass` | `pass` | as registered | — | — |
| `neg-mcp-byo-autoapply` | control-gate | bridge | classifyTool | `fail:classification-refused` | `fail:target-mismatch` | `pass` | `fail` | as registered | — | — |
| `neg-mcp-nonidempotent-autoapply` | control-gate | bridge | classifyTool | `fail:classification-refused` | `pass` | `pass` | `fail` | as registered | — | — |
| `neg-drain-skip` | control-gate | bridge | classifyTool, AutoApprovalDrainer | `fail:drain-order-violation` | `pass` | `pass` | `fail` | as registered | — | — |
| `neg-binding-control` | control-gate | store | — | `not-engaged` | `fail:commitment-schema-invalid` | `pass` | `fail` | as registered | — | — |
| `neg-replay-control` | control-gate | store | — | `not-engaged` | `fail:judgment-identity-mismatch` | `fail:replay-refused` | `fail` | as registered | — | — |
| `a01-pack-bytes-drift` | endpoint | store | — | `not-engaged` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — | — |
| `a02-disposition-forged` | endpoint | store | — | `not-engaged` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — | — |
| `a03-evaluator-digest-forged` | endpoint | store | — | `not-engaged` | `pass` | `fail:replay-executable-mismatch` | `fail` | as registered | — | — |
| `a04-judgment-identity-forged` | endpoint | store | — | `not-engaged` | `fail:judgment-identity-mismatch` | `pass` | `fail` | as registered | — | — |
| `s01-conflict-as-rejected` | endpoint | bridge | — | `not-engaged` | `fail:report-misattribution` | `pass` | `fail` | as registered | — | — |
| `s02-unknown-auto-applied` | endpoint | bridge | classifyTool, AutoApprovalDrainer | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — | — |
| `s03-opfail-as-unknown` | endpoint | store | — | `not-engaged` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — | — |
| `s04-approval-as-evidence` | endpoint | bridge | — | `not-engaged` | `fail:evidence-backing-invalid` | `pass` | `fail` | as registered | — | — |
| `s05-handoff-dropped` | endpoint | bridge | — | `not-engaged` | `fail:handoff-dropped` | `pass` | `fail` | as registered | — | `report-misattribution` |
| `s06-not-applicable-executed` | endpoint | bridge | — | `not-engaged` | `fail:action-map-violation` | `pass` | `fail` | as registered | — | — |
| `o01-observation-as-evidence` | endpoint | bridge | — | `not-engaged` | `fail:evidence-backing-invalid` | `pass` | `fail` | as registered | — | — |
| `b01-commitment-reuse` | endpoint | bridge | — | `not-engaged` | `fail:binding-reuse` | `pass` | `fail` | as registered | — | `report-state-unsupported` |
| `b02-argument-drift` | endpoint | store | — | `not-engaged` | `fail:argument-drift` | `pass` | `fail` | as registered | — | — |
| `b03-revision-drift` | endpoint | environment | — | `not-engaged` | `fail:revision-drift` | `pass` | `fail` | as registered | — | — |
| `b04-gatekeeper-substituted` | endpoint | bridge | — | `not-engaged` | `fail:target-mismatch` | `pass` | `fail` | as registered | — | — |
| `b05-actionkind-substituted` | endpoint | bridge | — | `not-engaged` | `fail:target-mismatch` | `pass` | `fail` | as registered | — | `argument-drift` |
| `b06-unbound-execution` | endpoint | out-of-band | — | `not-engaged` | `fail:unbound-execution` | `pass` | `fail` | as registered | — | `report-state-unsupported` |
| `b07-stage-revision-mismatch` | endpoint | store | — | `not-engaged` | `fail:stage-revision-mismatch` | `pass` | `fail` | as registered | — | — |
| `d02-simulated-as-committed` | endpoint | bridge | — | `not-engaged` | `fail:commit-overclaim` | `pass` | `fail` | as registered | — | — |
| `m01-readonly-bypass` | demonstration | out-of-band | classifyTool | `pass` | `fail:unbound-execution` | `pass` | `fail` | as registered | — | `report-state-unsupported` |
| `m02-ambiguous-commit` | descriptive | environment | — | `not-engaged` | `pass` | `pass` | `pass` | as registered | — | — |

## Reviewer holdout

Not run in this attempt (`--include-holdout` was not passed, or the preregistration is not yet frozen).
