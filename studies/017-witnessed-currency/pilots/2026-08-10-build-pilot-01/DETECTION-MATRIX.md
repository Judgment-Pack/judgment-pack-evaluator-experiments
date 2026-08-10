# Detection matrix — Study 017 (PILOT)

Layers: CURRENCY is Study 016's frozen verifier, unchanged; WITNESS is
this study's sighting-comparison step (witness/SPEC.md §2).

| Cell | Role | Layer | Expected | Observed |
|---|---|---|---|---|
| pos-consistent | control-gate | currency | `pass` | `pass` |
| pos-consistent | control-gate | witness | `pass` | `pass` |
| unchanged | control-gate | currency | `pass` | `pass` |
| unchanged | control-gate | witness | `pass` | `pass` |
| neg-sighting-forged | control-gate | currency | `pass` | `pass` |
| neg-sighting-forged | control-gate | witness | `fail:witness-sighting-invalid` | `fail:witness-sighting-invalid` |
| neg-unpinned-conflict | control-gate | currency | `pass` | `pass` |
| neg-unpinned-conflict | control-gate | witness | `pass` | `pass` |
| neg-limits | control-gate | currency | `pass` | `pass` |
| neg-limits | control-gate | witness | `fail:witness-limits-exceeded` | `fail:witness-limits-exceeded` |
| wit-split-view-caught | endpoint | currency | `pass` | `pass` |
| wit-split-view-caught | endpoint | witness | `fail:snapshot-conflicts-with-witnessed-head` | `fail:snapshot-conflicts-with-witnessed-head` |
| wit-collusion-a | endpoint | currency | `pass` | `pass` |
| wit-collusion-a | endpoint | witness | `pass` | `pass` |
| wit-collusion-b | endpoint | currency | `pass` | `pass` |
| wit-collusion-b | endpoint | witness | `pass` | `pass` |
| wit-one-honest | endpoint | currency | `pass` | `pass` |
| wit-one-honest | endpoint | witness | `fail:snapshot-conflicts-with-witnessed-head` | `fail:snapshot-conflicts-with-witnessed-head` |
| wit-partition-vacuous | endpoint | currency | `pass` | `pass` |
| wit-partition-vacuous | endpoint | witness | `pass` | `pass` |
| wit-partition-enforced | endpoint | currency | `pass` | `pass` |
| wit-partition-enforced | endpoint | witness | `unavailable` | `unavailable` |
| wit-retention-horizon | endpoint | currency | `pass` | `pass` |
| wit-retention-horizon | endpoint | witness | `pass` | `pass` |
| wit-recency-behind | endpoint | currency | `pass` | `pass` |
| wit-recency-behind | endpoint | witness | `fail:snapshot-behind-witnessed-head` | `fail:snapshot-behind-witnessed-head` |
| cur-retired-interplay | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |
| cur-retired-interplay | endpoint | witness | `pass` | `pass` |

## Registered pairs

- **collusion** (wit-collusion-a, wit-collusion-b): witness equivocation structurally validated from bytes: True. derived, not asserted: the equivocation is recomputed from the two cells' retained sightings under the pinned colluding key. Each run is internally valid and satisfies its enforcement clause; the witness's contradiction exists only across the pair — the independence clause of the witness contract, exhibited

## Verdict

**R1 holds (PILOT)**
