# Analysis — Study 018 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command from
the freeze commit (`b801d00c`, the squash-merge of PR #61), CPython 3.12.11, `cryptography`
49.0.0, `rfc8785` 0.1.4, label `REGISTERED`. Fully offline: no evaluator binary, no external
clone. Every pin, the whole-study manifest, the bytecode-cache bootstrap and the six freeze
pins verified before adjudication; the registered authority bound to every retained trust
configuration; holdout post-adjudication integrity intact across all 67 stamped files. This
document is post-run analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **Locked replication (R1)**: `R1 holds (REGISTERED)` — 22 cells, 22 adjudicated, 11
  endpoint, **0 endpoint-divergent**, 0 registered-undetected divergent, 0 pipeline-invalid,
  every control gate green.
- **Reviewer holdout (first execution)**: **divergent — 10/10 constructed inside the attempt,
  10/10 adjudicated, 3 divergent, and all three were named in writing before the run.** Seven
  cells were genuinely open and all seven landed as the reviewer registered them.

## What the citation buys

The positive result is the four-arm divergence, and it landed as registered. One registry
verdict — `fail:not-current-at-snapshot`, over byte-identical commitment, snapshot and trust
configuration — supports four configured evaluations yielding three exact outcomes:

| Cell | Rule | Transition outcome |
| --- | --- | --- |
| `div-stop-at-retirement` | `stop-at-retirement` | `not-usable-not-in-supported-set` |
| `div-position-window-open` | `position-window`, window 5 | `usable` |
| `div-position-window-elapsed` | `position-window`, window 1 | `not-usable-window-elapsed` |
| `div-grandfather-on-cited-support` | `grandfather-on-cited-support` | `usable` |

The four cells differ **only** in `ruleconfig.json` — asserted structurally, as an exact
difference set across every cell file. So the same evidence does not determine a usability
answer on its own: the rule does. That is RFC 0011 §2a's separation, measured rather than
argued. What follows for a registry's design is not measured here and is not claimed.

## What it does not buy — the registered boundaries, all confirmed

- **The backdated citation** (`bnd-backdated-citation`, registered expected-undetected)
  returned `usable`, as registered. It is **byte-identical** to `div-grandfather-on-cited-support`
  — verified by the scorer as a registered identity group — so honest reliance and backdated
  reliance are the same evidence and no rule over this evidence separates them. Signing the
  citation changes nothing: the party that would sign is the party that chooses what to cite.
  Closing this needs the trusted ordering RFC 0011 Unresolved #3 leaves open.
- **Ordering is absent** (`bnd-duration-window`): a duration window is `transition-unavailable`.
  The only ordering available offline is positional; `effectiveFrom` is carried and never
  compared in the pinned upstream, and nothing here holds a clock. A reader may object that a
  position window is not what an organisation means by "24 hours". That objection is the cell,
  and the study does not defend the model.
- **A rule confers nothing outside its series** (`bnd-foreign-series-rule`): `unavailable`.
- **The citation's value is rule-dependent**: `stop-at-retirement` reads no citation and
  answered `not-usable-not-in-supported-set` without one; `grandfather-on-cited-support` is
  `transition-unavailable` without one. A rule that ignores the citation is unaffected by
  every citation finding above.
- **Mint-time refusal** (`bnd-mint-time-refusal`) is a **counterfactual**, conditional on a
  policy this apparatus does not supply — there is no producer stage and no accepted-head
  policy anywhere in it. Whatever it shows belongs to that hypothetical policy, never to the
  citation.

## The holdout, and what its divergences mean

The holdout is the study's only prospective evidence and it is the reviewer's. Ten cells,
authored at review round 2, committed verbatim with attribution, never executed by anyone
until this run.

**Seven cells were open and all seven landed as registered**: `h01` (a twice-reinstated
binding, all-pass brittleness control), `h02` (the same with a flipped attestation signature —
the currency gate fires first), `h04` (a cited prefix reached by a *second* reinstatement is
supported even after a later departure), `h06` and `h07` (the positional window inclusive at
its bound, 3 permits and 2 refuses on identical evidence), `h09` (a series unknown at the
snapshot — currency withholds), and `h10` (a foreign-series citation — refusal precedes
folding).

**Three cells diverged, and all three were predicted in writing before the run** (PREREG-REVIEW
§R2-H, and the envelope notes of both holdout files):

| Cell | Registered | Observed | Channel |
| --- | --- | --- | --- |
| `h03` | `not-usable-cited-state-not-supported` | `not-usable-never-supported` | `transition` |
| `h05` | `retiredAtPosition: 8` | `null` | `transition:retiredAtPosition` |
| `h08` | `retiredAtPosition: 6` | `null` | `transition:retiredAtPosition` |

`h03` is a vocabulary distinction, not a disagreement about the world: its tuple carries a
digest bound at **no** position, so the layer reports never-supported rather than
cited-state-not-supported — the very split round 2 introduced after the reviewer showed that
Study 016 establishes non-membership and never retirement.

`h05` and `h08` are the substantive one. The reviewer's cells register the **most recent
departure in the whole history**; this layer publishes a departure only **relative to a
supported cited position**, and both cells cite positions where the binding is unsupported, so
it publishes `null`. The reviewer confirmed at round 3 that those values were deliberate, not
authoring slips, and ruled that neither side should be edited to force agreement.

**Neither side was edited.** Fitting the layer to unexecuted holdout answers would have
destroyed the stratum's prospective content; rewriting a reviewer's registered values to match
our output would be the same error inverted. The disagreement is registered, not resolved:
which reading a rule evaluator should publish is a question this study poses and does not
answer. `rule/transition.py` still carries `_left_position`, which computes the reviewer's
reading and is deliberately not on the decide path.

Stated plainly, because it bounds the result: three of ten holdout cells carried an expected
divergence, so the stratum's prospective content is the **seven** genuinely open cells, plus
the correctness of the three predictions. All ten came out as expected.

## Claims and non-claims

Within the registered cells, a citation recording the registry head an artifact validated
against lets a stated transition rule compute usability deterministically from retained
artifacts — and three registered rules disagree about the same evidence, which is what makes
the separation measurable rather than rhetorical. The evidence stops exactly where the
registration said it would: at ordering, at backdating, at series scope, and at any rule that
does not read the citation.

Non-claims, unchanged from the preregistration: **no interoperability claim of any kind** —
nothing here is independently developed, and this study may never be cited as evidence that
citations work between real parties. No claim about who sources or audits a transition rule;
RFC 0011 Unresolved #10 stays open and this study takes no position on it. The three rules are
a **construct**, not a survey of practice. No real-time anything; no policy or fact truth;
everything Study 016 registered as nothing's remains nothing's. Trust roots, enumerated: the
study-minted authority, the pinned Study 016 modules, this study's rule code, the registered
dependencies (whose *contents* are not digest-pinned, and whose distribution roots and origins
are checked live rather than registered), and the retained artifact store. Builder and
evaluator share one implementation lineage — the standing no-independent-oracle limitation.
Binding/lineage, not truth: the registry says which versions an authority asserted in force, a
transition rule says what one stated rule makes of that, and neither says anything is right.

## On the review that produced this

Twelve cross-vendor rounds preceded the freeze, and their arc is recorded in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md) because it bears on how much the result should be
trusted. Rounds 1–2 found two correctness blockers in the evaluator. Rounds 3–6 found four
consecutive sets of dispositions that claimed more than the code did. Rounds 7–8 introduced
the frozen-reader audit and found thirteen statements in the immutable artifacts that were
false or misleading — including a matrix note asserting the opposite of this study's own
result, and an R1 statement contradicting its own scorer. Rounds 9–11 found three safeguards
that could not fail because something upstream already guaranteed the property.

**No registered outcome has been wrong since round 2.** Everything found afterwards was the
apparatus claiming more than it did — which is the failure mode a preregistration exists to
catch, since the claims are what get pinned.

## Two residues the freeze created, found while publishing this

Neither affects a result. Both are recorded here because this document is the only
post-attempt artifact that is **not** manifest-covered, and because the second is a design
defect worth fixing in the next study rather than repeating.

**1. `README.md`'s status banner is frozen, and now reads as stale.** It still says *"Nothing
has run under the freeze; `results/` is absent until the registered primary attempt."* That
was true when written and is false now. The README is covered by
`harness/STUDY-MANIFEST.sha256`, whose digest is pinned as `studyManifest`, so editing it
breaks the pin and fails pin enforcement on every subsequent run. It was **not** updated:
rewriting a manifest-covered file after the freeze to make a sentence read better would trade
the anchor for cosmetics. Study 017 carries the same residue for the same reason.

**2. `DEVIATIONS.md` is manifest-covered too — so the study's own deviation mechanism cannot
be used after the freeze.** The preregistration says corrections go to `DEVIATIONS.md` rather
than by editing frozen files. But `DEVIATIONS.md` is in the manifest's `DOCUMENTS` set, so the
first genuine post-freeze deviation would break `studyManifest` exactly as any other edit
would. This was found by attempting to record residue 1 there and watching pin enforcement
fail.

Nothing here needed recording as a deviation, so the defect cost this study nothing. It would
have cost the next one a great deal: a study that discovered a real problem after its freeze
would have had to choose between leaving it unrecorded and breaking its own anchor. **For
future studies: `DEVIATIONS.md` belongs outside the manifest-covered set**, together with any
status banner that can go stale. The manifest should cover what must not change; a file whose
entire purpose is to be appended to after the freeze is not that.

Inherited from Studies 016 and 017, which have the same arrangement and have not yet needed
it.
