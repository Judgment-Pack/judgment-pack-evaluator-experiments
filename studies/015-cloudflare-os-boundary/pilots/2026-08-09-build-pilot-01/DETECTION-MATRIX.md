# Detection matrix — Study 015

Per-cell, per-layer outcome adjudicated against the registered expectations
(locked-replication stratum). Every registered cell appears; nothing is
excluded. Only `endpoint` rows count toward R1; `control-gate` rows are
validity gates, `demonstration` and `descriptive` rows count toward nothing.

| Cell | Role | Attacker | Engaged | CF | BINDING | REPLAY | Combined | Registered | Divergence |
|---|---|---|---|---|---|---|---|---|---|
| `pos-baseline` | control-gate | none | classifyTool, AutoApprovalDrainer | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `neg-mcp-byo-autoapply` | control-gate | bridge | classifyTool | `fail:classification-refused` | `pass` | `pass` | `fail` | as registered | — |
| `neg-mcp-nonidempotent-autoapply` | control-gate | bridge | classifyTool | `fail:classification-refused` | `pass` | `pass` | `fail` | as registered | — |
| `neg-drain-skip` | control-gate | bridge | classifyTool, AutoApprovalDrainer | `fail:drain-order-violation` | `pass` | `pass` | `fail` | as registered | — |
| `a01-pack-bytes-drift` | endpoint | store | — | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a02-disposition-forged` | endpoint | store | — | `pass` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `a03-evaluator-digest-forged` | endpoint | store | — | `pass` | `pass` | `fail:replay-executable-mismatch` | `fail` | as registered | — |
| `s01-conflict-as-rejected` | endpoint | bridge | — | `pass` | `fail:report-misattribution` | `pass` | `fail` | as registered | — |
| `s02-unknown-auto-applied` | endpoint | bridge | classifyTool, AutoApprovalDrainer | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `s03-opfail-as-unknown` | endpoint | store | — | `pass` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `s04-approval-as-evidence` | endpoint | bridge | — | `pass` | `fail:evidence-backing-invalid` | `pass` | `fail` | as registered | — |
| `s05-handoff-dropped` | endpoint | bridge | — | `pass` | `fail:handoff-dropped` | `pass` | `fail` | as registered | — |
| `s06-not-applicable-executed` | endpoint | bridge | — | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `o01-observation-as-evidence` | endpoint | bridge | — | `pass` | `fail:evidence-backing-invalid` | `pass` | `fail` | as registered | — |
| `b01-commitment-reuse` | endpoint | bridge | — | `pass` | `fail:binding-reuse` | `pass` | `fail` | as registered | — |
| `b02-argument-drift` | endpoint | store | — | `pass` | `fail:argument-drift` | `pass` | `fail` | as registered | — |
| `b03-revision-drift` | endpoint | environment | — | `pass` | `fail:revision-drift` | `pass` | `fail` | as registered | — |
| `b04-gatekeeper-substituted` | endpoint | bridge | — | `pass` | `fail:target-mismatch` | `pass` | `fail` | as registered | — |
| `b05-actionkind-substituted` | endpoint | bridge | — | `pass` | `fail:target-mismatch` | `pass` | `fail` | as registered | — |
| `b06-unbound-execution` | endpoint | out-of-band | — | `pass` | `fail:unbound-execution` | `pass` | `fail` | as registered | — |
| `d01-dependent-simulated-write` | endpoint | bridge | — | `pass` | `fail:simulation-basis-invalid` | `pass` | `fail` | as registered | — |
| `d02-simulated-as-committed` | endpoint | bridge | — | `pass` | `fail:commit-overclaim` | `pass` | `fail` | as registered | — |
| `m01-readonly-bypass` | demonstration | out-of-band | classifyTool | `pass` | `fail:unbound-execution` | `pass` | `fail` | as registered | — |
| `m02-ambiguous-commit` | descriptive | environment | — | `pass` | `pass` | `pass` | `pass` | as registered | — |
