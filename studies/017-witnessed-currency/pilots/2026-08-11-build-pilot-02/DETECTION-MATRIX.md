# Detection matrix — Study 017 (PILOT)

Layers: CURRENCY is Study 016's frozen verifier, unchanged; WITNESS is
this study's sighting-comparison step (witness/SPEC.md §2).

| Cell | Role | Layer | Expected | Observed |
|---|---|---|---|---|
| pos-consistent | control-gate | currency | `pass` | `pass` |
| pos-consistent | control-gate | witness | `pass` | `pass` |
| unchanged | control-gate | currency | `pass` | `pass` |
| unchanged | control-gate | witness | `pass` | `pass` |
| neg-relabel-attack | control-gate | currency | `pass` | `pass` |
| neg-relabel-attack | control-gate | witness | `fail:snapshot-conflicts-with-witnessed-head` | `fail:snapshot-conflicts-with-witnessed-head` |
| neg-sighting-malformed | control-gate | currency | `pass` | `pass` |
| neg-sighting-malformed | control-gate | witness | `fail:witness-sighting-invalid` | `fail:witness-sighting-invalid` |
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
| wit-suppression-omitted | endpoint | currency | `pass` | `pass` |
| wit-suppression-omitted | endpoint | witness | `pass` | `pass` |
| wit-suppression-corrupted | endpoint | currency | `pass` | `pass` |
| wit-suppression-corrupted | endpoint | witness | `pass` | `pass` |
| wit-required-witness-absent | endpoint | currency | `pass` | `pass` |
| wit-required-witness-absent | endpoint | witness | `fail:witness-required-absent` | `fail:witness-required-absent` |
| wit-zero-sightings-vacuous | endpoint | currency | `pass` | `pass` |
| wit-zero-sightings-vacuous | endpoint | witness | `pass` | `pass` |
| wit-zero-sightings-enforced | endpoint | currency | `pass` | `pass` |
| wit-zero-sightings-enforced | endpoint | witness | `unavailable` | `unavailable` |
| wit-prefix-coverage | endpoint | currency | `pass` | `pass` |
| wit-prefix-coverage | endpoint | witness | `pass` | `pass` |
| wit-recency-refused | endpoint | currency | `pass` | `pass` |
| wit-recency-refused | endpoint | witness | `fail:snapshot-behind-witnessed-head` | `fail:snapshot-behind-witnessed-head` |
| wit-historical-audit | endpoint | currency | `pass` | `pass` |
| wit-historical-audit | endpoint | witness | `pass` | `pass` |
| cur-retired-interplay | endpoint | currency | `fail:not-current-at-snapshot` | `fail:not-current-at-snapshot` |
| cur-retired-interplay | endpoint | witness | `pass` | `pass` |

## Registered pairs

- **collusion** (wit-collusion-a, wit-collusion-b): witness equivocation structurally validated from bytes: True. derived, not asserted: the equivocation is recomputed from the two cells' retained sightings under the pinned colluding key. Each run is internally valid and satisfies its enforcement clause; the witness's contradiction exists only across the pair — the independence clause of the witness contract, exhibited

## Verdict

**R1 holds (PILOT)**
