# Detection matrix — Study 017 (PILOT)

Layers: CURRENCY is Study 016's frozen verifier, unchanged — membership at
snapshot; TRANSITION is this study's rule evaluator (rule/SPEC.md §3), which
consumes that verdict as a fact and answers usability under a stated rule.

| Cell | Role | Layer | Expected | Observed | Rule evidence |
|---|---|---|---|---|---|
| pos-current-stop | control-gate | currency | `pass` | `pass` | — |
| pos-current-stop | control-gate | transition | `usable` | `usable` | — |
| pos-current-window | control-gate | currency | `pass` | `pass` | — |
| pos-current-window | control-gate | transition | `usable` | `usable` | — |
| pos-current-run | control-gate | currency | `pass` | `pass` | — |
| pos-current-run | control-gate | transition | `usable` | `usable` | — |
| unchanged | control-gate | currency | `pass` | `pass` | — |
| unchanged | control-gate | transition | `usable` | `usable` | — |
| neg-ruleconfig-malformed | control-gate | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| neg-ruleconfig-malformed | control-gate | transition | `unavailable` | `unavailable` | — |
| div-stop-at-retirement | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-stop-at-retirement | endpoint | transition | `not-usable:not-usable-version-retired` | `not-usable:not-usable-version-retired` | — |
| div-position-window-open | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-position-window-open | endpoint | transition | `usable` | `usable` | — |
| div-position-window-elapsed | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-position-window-elapsed | endpoint | transition | `not-usable:not-usable-window-elapsed` | `not-usable:not-usable-window-elapsed` | — |
| div-run-to-expiry | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| div-run-to-expiry | endpoint | transition | `usable` | `usable` | — |
| cite-absent-stop-unaffected | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-absent-stop-unaffected | endpoint | transition | `not-usable:not-usable-version-retired` | `not-usable:not-usable-version-retired` | — |
| cite-absent-run-unavailable | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-absent-run-unavailable | endpoint | transition | `unavailable` | `unavailable` | — |
| cite-after-retirement-run | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-after-retirement-run | endpoint | transition | `not-usable:not-usable-created-after-retirement` | `not-usable:not-usable-created-after-retirement` | — |
| cite-after-retirement-window | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-after-retirement-window | endpoint | transition | `not-usable:not-usable-created-after-retirement` | `not-usable:not-usable-created-after-retirement` | — |
| cite-foreign-history | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| cite-foreign-history | endpoint | transition | `unavailable` | `unavailable` | — |
| bnd-backdated-citation | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-backdated-citation | endpoint | transition | `usable` | `usable` | — |
| bnd-duration-window | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-duration-window | endpoint | transition | `unavailable` | `unavailable` | — |
| bnd-mint-time-refusal | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-mint-time-refusal | endpoint | transition | `not-usable:not-usable-version-retired` | `not-usable:not-usable-version-retired` | — |
| bnd-foreign-series-rule | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` | — |
| bnd-foreign-series-rule | endpoint | transition | `unavailable` | `unavailable` | — |

## Registered pairs


## Verdict

**R1 holds (PILOT)**
