# RFC 0008 cross-implementation agreement

Run date 2026-07-27. Two independently built prototypes of draft
[RFC 0008](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0008-bounded-collection-quantifiers.md)
(bounded collection quantifiers) are driven over the same inputs and diffed.

- **Implementation A — Go.** The reference runtime's experimental evaluator, `judgment-pack
  0.0.0-dev` built from its RFC 0008 prototype branch, invoked as
  `judgment-pack experimental evaluate <pack> --facts <f> [--evidence <e>] --rfc0008-quantifiers
  --format json`. Its accounting model is documented on `internal/evaluation/quantifier.go`.
- **Implementation B — Python.** The clean-room `jps_evaluator` 0.1.0 in this repository's
  `python/`, invoked as `python -m jps_evaluator --pack <p> --facts <f> [--evidence <e>]
  --enable-rfc0008`. Its accounting model is `python/DECISIONS.md` entry 22.

Both refuse a quantifier pack unless opted in, and the opt-in changes nothing about conformance:
`spec validate` still reports the twin packs here `invalid` with `JPS-STRUCTURE-CONDITION-SHAPE`,
exactly as Compatibility says it must — "a `0.1.0-draft` reader rejects a document containing
`exists` as **structurally non-conforming**".

**This file is referee tooling's output, not a conformance claim.** Core §3.4 forbids
evaluator-conformance claims under `0.1.0-draft` whatever is implemented, and RFC 0006's class does
not exist yet. RFC 0008's own Implementation section states the standing caveat directly: the two
implementations "both trace to one maintainer's direction, so agreement corroborates rather than
independently confirms."

## Reproducing

```console
$ python3 harness/rfc0008_harness.py cases       <go-binary> python harness/rfc0008_cases.json
$ python3 harness/rfc0008_harness.py equivalence <go-binary> python harness/rfc0008_equivalence
```

Every case in `rfc0008_cases.json` carries **its own pack**, because RFC 0008 rows differ in the
condition under test rather than only in the facts. Each probe pack is minimal and shaped so the
disposition *reveals the condition's three-valued value*: one rule fires on the condition and names
`cond-true`; a `fallbackOutcome` of `cond-false` catches the false case; `onUnknown: escalate` turns
unknown into `unresolved`/`unknown`. So

| Condition value | Disposition |
| --- | --- |
| `true` | `outcome` / `cond-true` |
| `false` | `outcome` / `cond-false` (the fallback) |
| `unknown`, rule escalates | `unresolved`, reasons `{unknown}` |
| `unknown`, rule ignores | `outcome` / `cond-false` (the fallback) |

Dispositions are normalized exactly as `agreement_harness.py` normalizes them — `kind`,
`outcomeId`, `reasons` as a set, `handoff` state — because the same RFC 0006 shape divergence
applies (object-with-target-echo versus bare string enum; `python/DECISIONS.md` entry 3). A row
**agrees** when those four match, or when both implementations refuse with the same class of
refusal.

## Result

| | |
| --- | ---: |
| Corpus rows | **82** |
| Agreements | **81** |
| Divergences on rows the RFC pins | **0** |
| Divergences on rows the RFC leaves unpinned | **1** (`L3`, where the limit is drawn) |
| Rows where both agree but land off the RFC's pinned value | **0** |
| Equivalence pairs (room × scenario, four evaluations each) | **9 / 9 equivalent** |

RFC 0008's Implementation section names "the five things they must be made to disagree about before
adoption: the empty-array values, unknown dominance in `every`, non-array `path`, where the limit is
drawn, and whether a short-circuiting and a non-short-circuiting evaluator report the same error at
the limit boundary." Four of the five are exercised and agree (`B1`/`B2`, `C3`/`C4`, `I1`–`I12`,
`L1`/`L2`). The fifth — **where the limit is drawn** — is the single divergence, and the RFC predicts
it in Compatibility rather than being surprised by it.

## Coverage of the Conformance section

| RFC 0008 Conformance paragraph | Rows |
| --- | --- |
| Positive and negative | `A1`–`A7` |
| Boundary — empty array | `B1`, `B2` |
| Boundary — unknown propagation, four directions | `C1`–`C4` |
| Boundary — empty array with `evidence-present`, four combinations | `D1`–`D4` (+ non-empty controls `D5`, `D6`) |
| Boundary — non-array values at `path`, unresolved `path` | `I1`–`I12` (both operators) |
| Boundary — permuted order and duplicated element | `H1`–`H8` |
| Ragged arrays, one row per operator, `unknown` rows run twice | `E1`–`E6` |
| Singleton, with a predicate | `F1`–`F6` |
| Scope and re-rooting | `G1`–`G7` |
| Structural — depth bound | `K1`–`K5` |
| `uniform`, if adopted | `J1`–`J14` |
| Adversarial — above-limit, two permutations, same error | `L1`, `L2` (+ `L3`, below) |
| Adversarial — empty-array `every` gating a permissive outcome | `B2` (that probe's `cond-true` *is* the permissive outcome) |
| Equivalence check over A6 / R3 / R5 | `harness/rfc0008_equivalence/` |

Two Conformance rows are **not** represented and the reason is textual, not an omission:
`uniform`'s limit-accounting rows, which the RFC itself says "cannot be written until the accounting
model exists, since the operator has no `where` for a `where`-shaped budget to charge"; and the
portable above-limit row at a stated threshold, which the RFC makes "explicitly conditional" on the
§10 portability question. See *Untestable at these CLIs* below.

## The matrix

| # | Row | Go | Python | Agree? | `rfc_expectation` | Verdict |
| ---: | --- | --- | --- | :---: | --- | --- |
| 1 | `A1-exists-positive-one-of-three` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 2 | `A2-every-positive-all-match` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 3 | `A3-nested-depth-two-positive` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 4 | `A4-exists-negative-all-false` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 5 | `A5-every-negative-one-false` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 6 | `A6-exists-where-names-member-no-element-carries` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 7 | `A7-every-where-names-member-no-element-carries` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 8 | `B1-exists-empty-array` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 9 | `B2-every-empty-array-gating-permissive-outcome` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 10 | `C1-exists-one-unknown-none-true` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 11 | `C2-exists-one-unknown-one-true` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 12 | `C3-every-one-unknown-rest-true` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 13 | `C4-every-one-unknown-one-false` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 14 | `D1-empty-array-every-evidence-present` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 15 | `D2-empty-array-every-evidence-absent` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 16 | `D3-empty-array-exists-evidence-present` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 17 | `D4-empty-array-exists-evidence-absent` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 18 | `D5-nonempty-exists-evidence-present-control` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 19 | `D6-nonempty-exists-evidence-absent-control` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 20 | `E1-ragged-exists-false-false-missing-escalate` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 21 | `E2-ragged-exists-false-false-missing-ignore` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 22 | `E3-ragged-exists-missing-true-false` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 23 | `E4-ragged-every-true-true-missing-escalate` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 24 | `E5-ragged-every-true-true-missing-ignore` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 25 | `E6-ragged-every-missing-false-true` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 26 | `F1-singleton-ok-true-exists` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 27 | `F2-singleton-ok-true-every` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 28 | `F3-singleton-ok-false-exists` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 29 | `F4-singleton-ok-false-every` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 30 | `F5-singleton-empty-object-exists` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 31 | `F6-singleton-empty-object-every` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 32 | `G1-empty-pointer-every-over-scalars-all-gold` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 33 | `G2-empty-pointer-every-over-scalars-mixed` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 34 | `G3-empty-pointer-exists-over-scalars-mixed` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 35 | `G4-collision-element-value-decides` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 36 | `G5-collision-outer-root-not-consulted` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 37 | `G6-nested-inner-path-resolves-only-at-outer-facts-root` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 38 | `G7-inner-where-re-rooting-restored-not-accumulated` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 39 | `H1-exists-permutation-dominant-first` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 40 | `H2-exists-permutation-dominant-last` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 41 | `H3-exists-duplicated-element` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 42 | `H4-every-permutation-dominant-first` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 43 | `H5-every-permutation-dominant-last` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 44 | `H6-every-duplicated-element` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 45 | `H7-exists-permutation-unknown-then-true` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 46 | `H8-exists-permutation-true-then-unknown` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 47 | `I1-exists-non-array-path-object` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 48 | `I2-exists-non-array-path-string` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 49 | `I3-exists-non-array-path-number` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 50 | `I4-exists-non-array-path-null` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 51 | `I5-exists-non-array-path-true` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 52 | `I6-exists-unresolved-path` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 53 | `I7-every-non-array-path-object` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 54 | `I8-every-non-array-path-string` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 55 | `I9-every-non-array-path-number` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 56 | `I10-every-non-array-path-null` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 57 | `I11-every-non-array-path-true` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 58 | `I12-every-unresolved-path` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 59 | `J1-uniform-empty-array` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 60 | `J2-uniform-singleton-at-resolves` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 61 | `J3-uniform-singleton-at-missing` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 62 | `J4-uniform-1-2-at-missing-clause3-before-clause4` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 63 | `J5-uniform-1-2-at-missing-permuted` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 64 | `J6-uniform-empty-at-whole-elements-equal` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 65 | `J7-uniform-empty-at-whole-elements-unequal` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 66 | `J8-uniform-object-at-member-order-insensitive` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 67 | `J9-uniform-array-at-same-order` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 68 | `J10-uniform-array-at-swapped-order` | `outcome`/`cond-false` | `outcome`/`cond-false` | yes | `outcome:cond-false` | matches-rfc |
| 69 | `J11-uniform-null-at-every-element` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 70 | `J12-uniform-at-missing-one-of-three-others-equal` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 71 | `J13-uniform-non-array-path` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 72 | `J14-uniform-unresolved-path` | `unresolved` unknown | `unresolved` unknown | yes | `unresolved:unknown` | matches-rfc |
| 73 | `K1-depth-two-sibling-aggregates-under-all-valid` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 74 | `K2-depth-three-through-all-wrapper-invalid` | error `JPS-EVALUATION-RFC0008-DEPTH` | error `invalid-input` | yes | `error:structural-refusal` | matches-rfc |
| 75 | `K3-depth-three-through-not-wrapper-invalid` | error `JPS-EVALUATION-RFC0008-DEPTH` | error `invalid-input` | yes | `error:structural-refusal` | matches-rfc |
| 76 | `K4-uniform-at-depth-two-valid` | `outcome`/`cond-true` | `outcome`/`cond-true` | yes | `outcome:cond-true` | matches-rfc |
| 77 | `K5-uniform-at-depth-three-invalid` | error `JPS-EVALUATION-RFC0008-DEPTH` | error `invalid-input` | yes | `error:structural-refusal` | matches-rfc |
| 78 | `L1-over-limit-dominant-element-first` | error `JPS-RESOURCE-EVALUATION-WORK-LIMIT` | error `resource-limit` | yes | `error:resource-limit` | matches-rfc |
| 79 | `L2-over-limit-dominant-element-last` | error `JPS-RESOURCE-EVALUATION-WORK-LIMIT` | error `resource-limit` | yes | `error:resource-limit` | matches-rfc |
| 80 | `L3-between-the-two-default-budgets` | error `JPS-RESOURCE-EVALUATION-WORK-LIMIT` | `outcome`/`cond-true` | **no** | `unpinned` | divergent-unpinned |

## Equivalence check

The check RFC 0008's Conformance section asks any implementation to run: "re-encode
`A6:/reservation/anySegmentCancelledByAirline`, `R3:/modification/allNewItemsAvailable`, and
`R5:/request/allNewItemsAvailable` as quantifiers against facts carrying the arrays, leaving each
room's remaining prepared booleans in place, and confirm the dispositions match the
prepared-boolean packs. That, not a count of new operators, measures whether it expresses them."

Assets are in `harness/rfc0008_equivalence/`. For each room the twin pack differs from
`studies/003-escape-census/rooms/<room>/pack.json` **only** in the condition subtrees that read the
re-encoded fact — every other member, including every other prepared boolean, is byte-identical
(the builder asserts it, and the diffs are 24, 27, and 27 changed lines respectively, all inside
`when`). Where the original reads the boolean positively the twin carries the bare aggregate; where
it reads `equals false` the twin carries `not` over the same aggregate, which is the three-valued
equivalent and not a second encoding choice.

Facts are supplied **both ways**, which is the migration contract the RFC describes: the
original-pack document carries the prepared boolean and no array; the twin-pack document carries the
raw array and no boolean. That is deliberate — a pack "mid-migration must not read a stale boolean
and a fresh array in the same rule", so neither document offers both.

| Room | Re-encoded fact | Op | Scenario | Go original | Py original | Go twin | Py twin | Equivalent? |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: |
| A6 | `/reservation/anySegmentCancelledByAirline` | `exists` | quantified-true | `cancellation-permitted` | `cancellation-permitted` | `cancellation-permitted` | `cancellation-permitted` | yes |
| A6 | `/reservation/anySegmentCancelledByAirline` | `exists` | quantified-false | `cancellation-denied` | `cancellation-denied` | `cancellation-denied` | `cancellation-denied` | yes |
| A6 | `/reservation/anySegmentCancelledByAirline` | `exists` | quantified-unknown | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | yes |
| R3 | `/modification/allNewItemsAvailable` | `every` | quantified-true | `allow-item-modification` | `allow-item-modification` | `allow-item-modification` | `allow-item-modification` | yes |
| R3 | `/modification/allNewItemsAvailable` | `every` | quantified-false | `deny-item-modification` | `deny-item-modification` | `deny-item-modification` | `deny-item-modification` | yes |
| R3 | `/modification/allNewItemsAvailable` | `every` | quantified-unknown | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | yes |
| R5 | `/request/allNewItemsAvailable` | `every` | quantified-true | `exchange-permitted` | `exchange-permitted` | `exchange-permitted` | `exchange-permitted` | yes |
| R5 | `/request/allNewItemsAvailable` | `every` | quantified-false | `exchange-denied` | `exchange-denied` | `exchange-denied` | `exchange-denied` | yes |
| R5 | `/request/allNewItemsAvailable` | `every` | quantified-unknown | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | `unresolved` (unknown) | yes |

Each room yields three distinct dispositions across its three scenarios, so the check is not
satisfied vacuously by a pack that always answers the same way. The `quantified-unknown` scenario
pairs an *absent* prepared boolean against a *ragged* array — an element missing the pointer the
`where` names — and both routes to `unknown` produce the same escalation.

**What this shows and does not show.** It shows the bare quantifier reproduces the prepared boolean
on the three census facts a quantifier reaches, in both implementations, across true, false, and
unknown. It does not show the quantifier reaches anything else: the RFC's own Evidence section puts
the figure at 3 of 25, and R3's and R5's remaining collection-quantification facts are join-shaped
and, as the RFC says, "cannot be part of the check". Note also that the twin packs are **not valid
under `0.1.0-draft`** — `spec validate` rejects them — which is expected and is the whole point of
the two opt-in flags.

## J15/J16 — a disagreement found, resolved, and pinned

Rows J15 and J16 did not exist in the first 80. The cross-vendor review of the RFC's
implementation-experience amendment reproduced a live disagreement no earlier row exercised: on
`1e999999999` vs `2e999999999`, the Go prototype's first reading returned `unknown` (its number
representation could not hold the value) while the Python prototype compared the values and
returned `false`. The RFC resolved it by pinning **determinacy** — numeric equality is decided by
sign/significand/exponent normalization of the tokens, never by materialising the value, and an
implementation unable to decide within its limits errors rather than answering `unknown`. The Go
prototype was repaired to normalized-token equality (its formerly quadratic huge-token `uniform`
case became linear), these two rows were added with `facts_raw` verbatim documents (`json.dump`
cannot re-emit such tokens), and both implementations now agree on both rows. This is the corpus's
second demonstration, after L3, that the rows discriminate rather than confirm.

## Divergences and adjudications

### D-1 (semantic, unpinned) — `L3-between-the-two-default-budgets`

| | |
| --- | --- |
| Go | error `JPS-RESOURCE-EVALUATION-WORK-LIMIT` (budget 100,000 units) |
| Python | `outcome` / `cond-true` (budget 200,000 units) |

The row is an `exists` over 1,500 elements whose `where` is 99 `literal` nodes. Both accounting
models charge a plain condition node one unit, so the two preflight charges land within a few units
of each other (≈150,002 and ≈150,004) — above one default budget and below the other. Neither
implementation is wrong.

**Adjudication against the text: the RFC pins nothing here, and says so.** Compatibility's §10
bullet: "a MUST-*define* is not portability. Two evaluators that both define limits may define
different ones, so no facts document is guaranteed to be above the limit for both, and a portable
'exceeds the mandated limit' error row cannot be written from a MUST-define alone. Closing that needs
one of three things: fix a common limit in the specification; carry the configured limit in the
evaluation-case input so a corpus row can state the threshold it assumes; or scope evaluator
portability to a common guaranteed domain and drop the above-limit row entirely." The Conformance
section then marks its own adversarial row "**explicitly conditional**" on that choice. `L3` is that
paragraph executed against two real implementations: it is evidence *for* the RFC's Unresolved
question, not a defect in either prototype. Until one of the three options is chosen, an above-limit
input is not a portable corpus row; the harness records `L3` as `divergent-unpinned` and does not
fail the run on it.

What *is* pinned, and holds in both: "Exhaustion of the budget is an explicit evaluation error, never
a disposition." Neither implementation ever returned `true`, `false`, or `unresolved` for an
over-budget input.

### D-2 (not semantic) — error vocabulary granularity

Both implementations refuse the same five rows (`K2`, `K3`, `K5`, `L1`, `L2`) and never turn a
refusal into a disposition, but their error identifiers are of different granularity:

| Refusal | Go | Python |
| --- | --- | --- |
| Aggregate depth three | `JPS-EVALUATION-RFC0008-DEPTH` (wrapped in `JPS-EVALUATION-RFC0008-GRAMMAR`) | kind `invalid-input` |
| Work budget exhausted | `JPS-RESOURCE-EVALUATION-WORK-LIMIT` | kind `resource-limit` |

**Adjudication: the RFC underdetermines this, necessarily.** RFC 0008 requires that exhaustion "MUST
produce an explicit evaluation error, never a disposition, per RFC 0006's *errors are not
dispositions*", and it makes depth three a *document*-level invalidity. It defines no error taxonomy,
and cannot: Compatibility records that "Core is not innocent of the concept … What is missing is an
**evaluation-error contract** and the point in §8's algorithm where it interrupts", and that the whole
RFC is "conditional on RFC 0006's error concept landing in Core first". So the harness compares error
rows at a hand-written *class* level (`structural-refusal`, `resource-limit`), and that mapping is
referee judgment rather than something either specification supplies. Python's `invalid-input` is a
broader bucket than Go's dedicated code — within this corpus its only members are the depth refusals,
but the mapping would not survive a wider corpus unchanged. Counted as agreement here; flagged as a
place where a future corpus needs the error contract the RFC is waiting on.

### D-3 (not semantic, inherited) — disposition serialization

Go emits `handoff` as `{"state": …, "target": …}`; Python emits a bare string. Both carry the same
state. Already recorded under RFC 0006 (`python/DECISIONS.md` entry 3) and normalized away by both
harnesses. Noted only because RFC 0008 inherits it rather than fixing it, and because its Security
section observes that RFC 0006's "disposition sketch (`kind` / `outcomeId` / `reasons` / `handoff`)
has **no trace member at all**" — so per-element diagnostics, if they are ever wanted, are a new field
and not a shape question.

## The two accounting models: divergence expected, and informative

RFC 0008 leaves limit accounting undefined and calls producing a model "a **precondition for
accepting this RFC**, not an implementation detail", listing seven things any model must do. The two
implementations wrote **different candidate models independently**, and that is the useful part of
this comparison — not a discrepancy to reconcile.

| | Go (`internal/evaluation/quantifier.go`) | Python (`DECISIONS.md` entry 22) |
| --- | --- | --- |
| Default budget | 100,000 units | 200,000 units |
| CLI knob | **none** | `--evaluation-work-limit UNITS` |
| Work unit | byte-sensitive after adversarial review: a pointer charges `1 + len(path)` to compile (once per authored path, reserved before the scan, compiled form cached) plus per-resolution token bytes; scalar operands charge `1 + len(token)`; object members also pay their name bytes | one condition node; a pointer attempt costs 1 plus `1 + len(token)` per token attempted; JSON size counts *characters* for strings and number tokens |
| Charge point | whole condition tree charged before its first predicate runs; conditions §8 never reaches are never charged | same |
| Ragged nesting | `Σᵢ |Bᵢ|`, never `|A| × |B|` | same |
| Boolean branches | all charged, including short-circuited ones | same |
| Deep equality | charged as the byte-weighted JSON size of the authored operand | charged as `size(left) + size(right)` in characters |
| `uniform` | path + per-member pointer + selected value size, plus an extra pass per value carrying a number §7.4 cannot compare | path + per-member `at` attempt + `size(left)+size(right)` for every unordered pair of resolved values |
| Sibling aggregates | additive | additive |
| Pointer resolution in preflight | yes; a failed lookup still costs the lookup | yes; the failing token is charged too |

A historical note that is itself evidence: the Go model's FIRST candidate charged flat units per
pointer and per scalar, and the cross-vendor review of the runtime branch broke it with a ~1 MiB
unresolved pointer over tens of thousands of elements — tens of gigabytes of processing under a
100,000-unit budget. The byte-sensitive model above is the repaired second candidate, with the
attack committed as a regression (refused in 0.07 s). One implementation cycle produced and killed a
plausible-but-wrong accounting model; the RFC's claim that the model is an acceptance precondition
rather than an implementation detail is not hypothetical. This matrix was re-run in full against the
repaired model: the same 81/82 agreement and the same single unpinned divergence (L3).

Both models satisfy every bullet the RFC's list demands, and both satisfy the settled intent — "the
budget MUST be charged **before any element is evaluated** and **independently of element order**, so
short-circuiting may only reduce *actual* work and can **never** change whether the limit was
exceeded". Rows `L1` and `L2` are the same input with the dominant element first and last; both
implementations produced *the same* error in both permutations, which is the row the RFC says "would
pin order-independent limit accounting".

**No attempt is made to reconcile the numbers.** They are not commensurable: one counts JSON nodes,
the other counts characters, so a "unit" is a different quantity in each. The two facts worth
recording are that **both refuse with an explicit error rather than a disposition**, and that their
**error classes are comparable but not identical** — both are a resource-exhaustion refusal, at
different naming granularity (D-2). What the numeric gap produces is `L3`, and `L3`'s adjudication is
that the RFC pins nothing there.

## Untestable at these CLIs

A work-limit row at a stated threshold was to be run *if both implementations expose a budget control
on their CLIs*. **They do not.** Python exposes `--evaluation-work-limit`; the Go binary's
`experimental evaluate` has no budget flag (`--evidence`, `--facts`, `--format`,
`--rfc0008-quantifiers`, `--supported-extension` only). So:

- A row at a **stated common threshold** — RFC 0008's second closing option, "carry the configured
  limit in the evaluation-case input so a corpus row can state the threshold it assumes" — is
  **untestable at these CLIs**, and is recorded as such rather than forced by editing either
  implementation. `L1`/`L2` are the fallback: an input far above *both* defaults, portable only by
  being extravagant rather than by being specified.
- `uniform`'s limit-accounting rows are untestable for the reason the RFC gives itself: the operator
  has no `where`, and no accounting model exists to charge it portably.

## What the comparison exposes as underdetermined in the RFC text

1. **Where the limit is drawn** — `L3`. Already an Unresolved question; now it has a reproducible
   two-implementation instance instead of an argument.
2. **"Within the mandated minimum limits" has no referent.** The permutation row is
   implementation-independent only "**for inputs within the mandated minimum limits**", and RFC 0006
   says "corpus inputs must fit mandated minimum limits so identical corpus runs cannot diverge on
   limits". Neither document states a number: Core §10 is a SHOULD-define, RFC 0008 raises it to a
   MUST-define, and a MUST-define fixes no minimum. Rows `H1`–`H8` are therefore qualified by a domain
   that does not exist yet. They pass here, but nothing in the text says what input sizes they are
   entitled to assume.
3. **Where the depth bound is enforced.** The RFC says the bound is schema-enforced through
   "depth-indexed, non-recursive definitions … so depth three is unrepresentable", and that "a
   document's structural and semantic conformance status does not depend on which evaluator reads it".
   No such schema exists — the operators have no published `specVersion` — so *both* implementations
   enforce the bound as an evaluator-side grammar check at evaluation time. Rows `K2`, `K3`, `K5`
   therefore agree on the refusal while telling us nothing about the placement the RFC actually
   specifies. The corpus cannot distinguish a validator that rejects the document from an evaluator
   that refuses to run it, and today only the latter exists.
4. **The `onUnknown: ignore` half of the ragged rows is a Core §8 row, not an RFC 0008 row.** The RFC
   says the two `unknown` ragged rows "run twice each, once under `onUnknown: ignore` and once under
   `escalate`, so the divergence is visible", but it does not say what the `ignore` run should
   *produce*. It cannot: the disposition then depends on pack shape the RFC does not fix. `E2` and
   `E5` land on `cond-false` **only because these probe packs declare a `fallbackOutcome`**; the same
   condition in a pack without one yields `unresolved`/`no-match`. The RFC pins a condition value; the
   corpus row has to pin a pack. Worth stating in the row itself, since the point of running it twice
   is to make the Security section's silent-degradation surface visible — "under `onUnknown: ignore`
   the rule then stops contributing without saying so" — and how loudly it fails to say so depends on
   the fallback.
5. **`uniform` agrees on all 14 rows while remaining "Under discussion, not settled".** The five
   ordered clauses are precise enough that two independent readings produced identical behaviour,
   including the two rows the RFC added specifically because an earlier draft got them wrong — clause
   3 before clause 4 (`J4`) and the singleton with a missing `at` (`J3`). That is evidence the
   *specification* of `uniform` is adequate. It is not evidence for the separate question the RFC
   asks, "Does `uniform` earn its keep on 2 cases, one weak?", which no agreement run can answer.
6. **`evidence-present` inside `where` is implementable and agreed, and still a footgun.** `D1`–`D4`
   confirm emptiness overrides element-invariance in all four combinations; `D5`/`D6` confirm the
   non-empty case is a whole-condition constant that ignores every element. Both are exactly what the
   text says. The RFC's own Unresolved question — "should `evidence-present` be forbidden inside
   `where`?" — is untouched by the agreement: two implementations agreeing on a construct says nothing
   about whether authors should be allowed to write it.
7. **The equivalence check's scope is narrower than "does the quantifier express the fact".** It
   confirms disposition equality *given facts the producer shaped*. For R3 and R5 the producer must
   still "attach catalog availability onto the elements", which the RFC calls "data shaping, not
   condition language" — the arrays in `harness/rfc0008_equivalence/R3` and `R5` carry a
   `newItemAvailable` member no source record holds. A6 is the only room where the array is a
   mechanical re-exposure of records that already exist, and it is, as the RFC says, "the strongest
   case in the RFC". 9/9 should not be read as three equally strong cases.
