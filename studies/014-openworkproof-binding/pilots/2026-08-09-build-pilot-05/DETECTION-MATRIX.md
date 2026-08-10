# Detection matrix — Study 014

## Locked-replication stratum

Per-cell, per-layer outcome adjudicated against `harness/MATRIX.json`
(locked-replication stratum). Every registered cell appears; nothing is
excluded. Only `endpoint` rows count toward R1; `control-gate` rows are
validity gates, `demonstration` and `descriptive` rows count toward nothing.

| Cell | Role | Attacker | OWP | BINDING | REPLAY | Combined | Registered | Divergence |
|---|---|---|---|---|---|---|---|---|
| `pos-baseline` | control-gate | none | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `neg-signature` | control-gate | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-evidence-digest` | control-gate | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-parent-ref` | control-gate | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-action-param` | control-gate | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `a01-pack-bytes-drift` | endpoint | none | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a02-pack-version-substitution` | endpoint | none | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a03-pack-substitution-compatible` | endpoint | none | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a04-commitment-packdigest-tampered` | endpoint | tamper | `fail` | `fail:binding-point-divergence` | `pass` | `fail` | as registered | — |
| `a04-commitment-packdigest-resigned` | endpoint | full-keys | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a05-pack-artifact-missing` | endpoint | none | `pass` | `fail:pack-artifact-missing` | `unavailable` | `fail` | as registered | — |
| `b06-fact-edit-same-disposition` | endpoint | none | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `b07-facts-doc-substituted` | endpoint | none | `pass` | `fail:facts-digest-mismatch` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `b08-same-disposition-different-facts` | endpoint | none | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `b09-factsdigest-field-wrong` | endpoint | full-keys | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `c10-reject-executed` | endpoint | full-keys | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c11-unresolved-executed` | endpoint | full-keys | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c12-handoff-requested-executed` | endpoint | full-keys | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c13-outcome-forged` | endpoint | full-keys | `pass` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `c14-reasons-forged` | endpoint | full-keys | `pass` | `fail:action-map-violation` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `c15-manual-review-unbound-execution` | endpoint | full-keys | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `d15-tool-tampered` | endpoint | tamper | `fail` | `fail:action-tool-mismatch` | `pass` | `fail` | as registered | — |
| `d15-tool-resigned` | endpoint | full-keys | `pass` | `fail:action-tool-mismatch` | `pass` | `fail` | as registered | — |
| `d16-argument-tampered` | endpoint | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `d16-argument-resigned` | endpoint | full-keys | `pass` | `fail:action-arguments-mismatch` | `pass` | `fail` | as registered | — |
| `d17-amount-tampered` | endpoint | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `d17-amount-resigned` | endpoint | full-keys | `pass` | `fail:action-arguments-mismatch` | `pass` | `fail` | as registered | — |
| `d18-approve-extra-execution` | endpoint | selective-keys | `fail` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `e19-decision-rebound` | endpoint | selective-keys | `fail` | `fail:commitment-objective-missing` | `unavailable` | `fail` | as registered | — |
| `e20-execution-point-divergence` | endpoint | full-keys | `pass` | `fail:binding-point-divergence` | `pass` | `fail` | as registered | — |
| `e21-outside-window` | endpoint | selective-keys | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `e22-workorder-rollback` | descriptive | full-keys | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `e23-executable-digest-forged` | endpoint | full-keys | `pass` | `pass` | `fail:replay-executable-mismatch` | `fail` | as registered | — |
| `f23-wrong-parent-decision` | endpoint | selective-keys | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f24-parent-receipt-removed` | endpoint | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f25-extra-parent-inserted` | endpoint | selective-keys | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f26-cross-execution-receipt` | endpoint | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f27-cross-execution-evidence` | endpoint | tamper | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `m28-unsigned-metadata-carriage` | demonstration | none | `pass` | `fail:commitment-objective-missing` | `unavailable` | `fail` | as registered | — |
