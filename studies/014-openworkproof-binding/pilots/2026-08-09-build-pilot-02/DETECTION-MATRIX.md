# Detection matrix — Study 014

Per-cell, per-layer outcome adjudicated against `harness/MATRIX.json`.
Every registered cell appears; nothing is excluded.

| Cell | Category | OWP | BINDING | REPLAY | Combined | Registered | Divergence |
|---|---|---|---|---|---|---|---|
| `pos-baseline` | control-positive | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `neg-signature` | control-negative | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-evidence-digest` | control-negative | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-parent-ref` | control-negative | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `neg-action-param` | control-negative | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `a01-pack-bytes-drift` | A-judgment-artifact | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a02-pack-version-substitution` | A-judgment-artifact | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a03-pack-substitution-compatible` | A-judgment-artifact | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a04-commitment-packdigest-tampered` | A-judgment-artifact | `fail` | `fail:binding-point-divergence` | `pass` | `fail` | as registered | — |
| `a04-commitment-packdigest-resigned` | A-judgment-artifact | `pass` | `fail:pack-digest-mismatch` | `pass` | `fail` | as registered | — |
| `a05-pack-artifact-missing` | A-judgment-artifact | `pass` | `fail:pack-artifact-missing` | `unavailable` | `fail` | as registered | — |
| `b06-fact-edit-same-disposition` | B-facts | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `b07-facts-doc-substituted` | B-facts | `pass` | `fail:facts-digest-mismatch` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `b08-same-disposition-different-facts` | B-facts | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `b09-factsdigest-field-wrong` | B-facts | `pass` | `fail:facts-digest-mismatch` | `pass` | `fail` | as registered | — |
| `c10-reject-executed` | C-disposition | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c11-unresolved-executed` | C-disposition | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c12-handoff-requested-executed` | C-disposition | `pass` | `fail:action-map-violation` | `pass` | `fail` | as registered | — |
| `c13-outcome-forged` | C-disposition | `pass` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `c14-reasons-forged` | C-disposition | `pass` | `pass` | `fail:replay-disposition-mismatch` | `fail` | as registered | — |
| `d15-tool-tampered` | D-action | `fail` | `fail:action-tool-mismatch` | `pass` | `fail` | as registered | — |
| `d15-tool-resigned` | D-action | `pass` | `fail:action-tool-mismatch` | `pass` | `fail` | as registered | — |
| `d16-argument-tampered` | D-action | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `d16-argument-resigned` | D-action | `pass` | `fail:action-arguments-mismatch` | `pass` | `fail` | as registered | — |
| `d17-amount-tampered` | D-action | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `d17-amount-resigned` | D-action | `pass` | `fail:action-arguments-mismatch` | `pass` | `fail` | as registered | — |
| `e18-stale-decision-currency` | E-replay-drift | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `e19-decision-rebound` | E-replay-drift | `fail` | `fail:commitment-objective-missing` | `unavailable` | `fail` | as registered | — |
| `e20-mismatched-decision-pairing` | E-replay-drift | `pass` | `fail:binding-point-divergence` | `pass` | `fail` | as registered | — |
| `e21-outside-window` | E-replay-drift | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `e22-workorder-rollback` | E-replay-drift | `pass` | `pass` | `pass` | `pass` | as registered | — |
| `f23-wrong-parent-decision` | F-causal-chain | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f24-parent-receipt-removed` | F-causal-chain | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f25-extra-parent-inserted` | F-causal-chain | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f26-cross-execution-receipt` | F-causal-chain | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `f27-cross-execution-evidence` | F-causal-chain | `fail` | `pass` | `pass` | `fail` | as registered | — |
| `m28-unsigned-metadata-carriage` | M-control-demonstration | `pass` | `fail:commitment-objective-missing` | `unavailable` | `fail` | as registered | — |
