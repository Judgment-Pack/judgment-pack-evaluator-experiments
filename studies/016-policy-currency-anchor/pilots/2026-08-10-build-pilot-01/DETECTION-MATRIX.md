# Detection matrix — Study 016 (PILOT)

Layers: OWP / BINDING / REPLAY are Study 014's frozen adapter, unchanged;
CURRENCY is this study's registry membership step (registry/SPEC.md §3).
Adjudication is on registered outcome strings alone; `≠` marks a divergence.

| Cell | Role | Layer | Expected | Observed |
|---|---|---|---|---|
| pos-current | control-gate | owp | `pass` | `pass` |
| pos-current | control-gate | binding | `pass` | `pass` |
| pos-current | control-gate | replay | `pass` | `pass` |
| pos-current | control-gate | currency | `pass` | `pass` |
| unchanged | control-gate | owp | `pass` | `pass` |
| unchanged | control-gate | binding | `pass` | `pass` |
| unchanged | control-gate | replay | `pass` | `pass` |
| unchanged | control-gate | currency | `pass` | `pass` |
| neg-owp-alive | control-gate | owp | `fail` | `fail` |
| neg-owp-alive | control-gate | binding | `pass` | `pass` |
| neg-owp-alive | control-gate | replay | `pass` | `pass` |
| neg-owp-alive | control-gate | currency | `pass` | `pass` |
| neg-snapshot-signature | control-gate | owp | `pass` | `pass` |
| neg-snapshot-signature | control-gate | binding | `pass` | `pass` |
| neg-snapshot-signature | control-gate | replay | `pass` | `pass` |
| neg-snapshot-signature | control-gate | currency | `fail:snapshot-signature-invalid` | `fail:snapshot-signature-invalid` |
| neg-authority-unpinned | control-gate | owp | `pass` | `pass` |
| neg-authority-unpinned | control-gate | binding | `pass` | `pass` |
| neg-authority-unpinned | control-gate | replay | `pass` | `pass` |
| neg-authority-unpinned | control-gate | currency | `fail:snapshot-authority-unpinned` | `fail:snapshot-authority-unpinned` |
| neg-chain-break | control-gate | owp | `pass` | `pass` |
| neg-chain-break | control-gate | binding | `pass` | `pass` |
| neg-chain-break | control-gate | replay | `pass` | `pass` |
| neg-chain-break | control-gate | currency | `fail:snapshot-chain-inconsistent` | `fail:snapshot-chain-inconsistent` |
| cur-retired-reuse | endpoint | owp | `pass` | `pass` |
| cur-retired-reuse | endpoint | binding | `pass` | `pass` |
| cur-retired-reuse | endpoint | replay | `pass` | `pass` |
| cur-retired-reuse | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |
| cur-successor-current | endpoint | owp | `pass` | `pass` |
| cur-successor-current | endpoint | binding | `pass` | `pass` |
| cur-successor-current | endpoint | replay | `pass` | `pass` |
| cur-successor-current | endpoint | currency | `pass` | `pass` |
| cur-concurrent-set | endpoint | owp | `pass` | `pass` |
| cur-concurrent-set | endpoint | binding | `pass` | `pass` |
| cur-concurrent-set | endpoint | replay | `pass` | `pass` |
| cur-concurrent-set | endpoint | currency | `pass` | `pass` |
| cur-reinstated | endpoint | owp | `pass` | `pass` |
| cur-reinstated | endpoint | binding | `pass` | `pass` |
| cur-reinstated | endpoint | replay | `pass` | `pass` |
| cur-reinstated | endpoint | currency | `pass` | `pass` |
| cur-rebind-refused | endpoint | owp | `pass` | `pass` |
| cur-rebind-refused | endpoint | binding | `pass` | `pass` |
| cur-rebind-refused | endpoint | replay | `pass` | `pass` |
| cur-rebind-refused | endpoint | currency | `fail:binding-rebound` | `fail:binding-rebound` |
| cur-series-unknown | endpoint | owp | `pass` | `pass` |
| cur-series-unknown | endpoint | binding | `pass` | `pass` |
| cur-series-unknown | endpoint | replay | `pass` | `pass` |
| cur-series-unknown | endpoint | currency | `fail:series-unknown-at-snapshot` | `fail:series-unknown-at-snapshot` |
| cur-authz-rollback-accepted | endpoint | owp | `pass` | `pass` |
| cur-authz-rollback-accepted | endpoint | binding | `pass` | `pass` |
| cur-authz-rollback-accepted | endpoint | replay | `pass` | `pass` |
| cur-authz-rollback-accepted | endpoint | currency | `pass` | `pass` |
| cur-split-view-a | endpoint | owp | `pass` | `pass` |
| cur-split-view-a | endpoint | binding | `pass` | `pass` |
| cur-split-view-a | endpoint | replay | `pass` | `pass` |
| cur-split-view-a | endpoint | currency | `pass` | `pass` |
| cur-split-view-b | endpoint | owp | `pass` | `pass` |
| cur-split-view-b | endpoint | binding | `pass` | `pass` |
| cur-split-view-b | endpoint | replay | `pass` | `pass` |
| cur-split-view-b | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |
| cur-older-snapshot-unpinned | endpoint | owp | `pass` | `pass` |
| cur-older-snapshot-unpinned | endpoint | binding | `pass` | `pass` |
| cur-older-snapshot-unpinned | endpoint | replay | `pass` | `pass` |
| cur-older-snapshot-unpinned | endpoint | currency | `pass` | `pass` |
| cur-older-snapshot-pinned | endpoint | owp | `pass` | `pass` |
| cur-older-snapshot-pinned | endpoint | binding | `pass` | `pass` |
| cur-older-snapshot-pinned | endpoint | replay | `pass` | `pass` |
| cur-older-snapshot-pinned | endpoint | currency | `fail:snapshot-older-than-accepted-head` | `fail:snapshot-older-than-accepted-head` |
| cur-genesis-unpinned | endpoint | owp | `pass` | `pass` |
| cur-genesis-unpinned | endpoint | binding | `pass` | `pass` |
| cur-genesis-unpinned | endpoint | replay | `pass` | `pass` |
| cur-genesis-unpinned | endpoint | currency | `unavailable` | `unavailable` |
| dem-freshness-legit | demonstration | owp | `pass` | `pass` |
| dem-freshness-legit | demonstration | binding | `pass` | `pass` |
| dem-freshness-legit | demonstration | replay | `pass` | `pass` |
| dem-freshness-legit | demonstration | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |
| dem-freshness-stale | demonstration | owp | `pass` | `pass` |
| dem-freshness-stale | demonstration | binding | `pass` | `pass` |
| dem-freshness-stale | demonstration | replay | `pass` | `pass` |
| dem-freshness-stale | demonstration | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |

## Registered pairs

- **split-view** (cur-split-view-a, cur-split-view-b): contradictory verdicts: True; fork revealed to either run: False. each run is internally valid under the same two pins; the contradiction exists only across the pair, which no single offline run can observe

## Verdict

**R1 holds (PILOT)**
