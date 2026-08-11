# Decision matrix — Study 018 (PILOT)

Layers: CURRENCY is Study 016's frozen verifier, unchanged — membership at
snapshot; TRANSITION is this study's rule evaluator (rule/SPEC.md §3), which
consumes that verdict as a fact and answers usability under a stated rule.

| Cell | Role | Layer | Expected | Observed | Rule evidence |
|---|---|---|---|---|---|
| pos-current-stop | control-gate | currency | `pass` | `pass` | — |
| pos-current-stop | control-gate | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| pos-current-window | control-gate | currency | `pass` | `pass` | — |
| pos-current-window | control-gate | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| pos-current-grandfather | control-gate | currency | `pass` | `pass` | — |
| pos-current-grandfather | control-gate | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| unchanged | control-gate | currency | `pass` | `pass` | — |
| unchanged | control-gate | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| neg-ruleconfig-malformed | control-gate | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| neg-ruleconfig-malformed | control-gate | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| neg-currency-unauthenticated | control-gate | currency | `fail:snapshot-signature-invalid` | `fail:snapshot-signature-invalid` | — |
| neg-currency-unauthenticated | control-gate | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| div-stop-at-retirement | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-stop-at-retirement | endpoint | transition | `not-usable:not-usable-not-in-supported-set` | `not-usable:not-usable-not-in-supported-set` | compared=None, attributed=None, unattributed=None |
| div-position-window-open | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-position-window-open | endpoint | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| div-position-window-elapsed | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-position-window-elapsed | endpoint | transition | `not-usable:not-usable-window-elapsed` | `not-usable:not-usable-window-elapsed` | compared=None, attributed=None, unattributed=None |
| div-grandfather-on-cited-support | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-grandfather-on-cited-support | endpoint | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| cite-absent-stop-unaffected | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-absent-stop-unaffected | endpoint | transition | `not-usable:not-usable-not-in-supported-set` | `not-usable:not-usable-not-in-supported-set` | compared=None, attributed=None, unattributed=None |
| cite-absent-grandfather-unavailable | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-absent-grandfather-unavailable | endpoint | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| cite-unsupported-grandfather | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-unsupported-grandfather | endpoint | transition | `not-usable:not-usable-cited-state-not-supported` | `not-usable:not-usable-cited-state-not-supported` | compared=None, attributed=None, unattributed=None |
| cite-unsupported-window | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-unsupported-window | endpoint | transition | `not-usable:not-usable-cited-state-not-supported` | `not-usable:not-usable-cited-state-not-supported` | compared=None, attributed=None, unattributed=None |
| cite-foreign-history | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-foreign-history | endpoint | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| bnd-backdated-citation | descriptive | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-backdated-citation | descriptive | transition | `usable` | `usable` | compared=None, attributed=None, unattributed=None |
| bnd-duration-window | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-duration-window | endpoint | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| bnd-mint-time-refusal | demonstration | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-mint-time-refusal | demonstration | transition | `not-usable:not-usable-not-in-supported-set` | `not-usable:not-usable-not-in-supported-set` | compared=None, attributed=None, unattributed=None |
| bnd-foreign-series-rule | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-foreign-series-rule | endpoint | transition | `unavailable` | `unavailable` | compared=None, attributed=None, unattributed=None |
| neg-never-supported-digest | control-gate | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| neg-never-supported-digest | control-gate | transition | `not-usable:not-usable-never-supported` | `not-usable:not-usable-never-supported` | compared=None, attributed=None, unattributed=None |
| neg-never-supported-window | control-gate | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| neg-never-supported-window | control-gate | transition | `not-usable:not-usable-never-supported` | `not-usable:not-usable-never-supported` | compared=None, attributed=None, unattributed=None |

## Registered pairs


## Verdict

**R1 holds (PILOT)**
