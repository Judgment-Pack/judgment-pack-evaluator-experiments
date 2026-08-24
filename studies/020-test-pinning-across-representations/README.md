# Study 020 — test pinning across representations

**Status: DRAFT preregistration, first revision. Not frozen. Nothing citable has run, and no
review round is on the record.** [`PREREGISTRATION.md`](PREREGISTRATION.md) is the protocol;
[`PREREG-REVIEW.md`](PREREG-REVIEW.md) is the pre-freeze review record and its round-state block
is the single machine-readable source for round counts, verdicts and open state (ADR 0005).

<!-- round-status:begin -->
ROUND STATUS (rendered from PREREG-REVIEW.md's round-state block by harness/render_round_status.py; edit the block, never this sentence): 0 review rounds are on the record, 0 have returned a verdict — none has returned a verdict — and no round is open.
<!-- round-status:end -->

> The sentence above is hand-written to be byte-identical to what the block renders, and is
> **marked for mechanical regeneration at harness-port time**: `render_round_status.py` arrives
> with the harness (`PREREGISTRATION.md` §7, delta 10) and its first act is `--write`.

## The registered question

> Within the registered JPS-expressible policy fragment, under single-shot authorship, does the
> representation a model authors in change **what its accompanying test suite pins down** —
> compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a prescribed
> judgment convention (arm C)?

Carried **verbatim** from Study 019 §1. What has changed is not the question but the honest name
of what the endpoint measures.

**The measured construct is *witness-input coverage against the shared reference***: the fraction
of the shared witness classes a run's authored suite reaches. Study 019's own frozen manifests
prove it — conditional on the identity control passing, `killedPaired` equals exactly the summed
member count of the covered witness classes in **88 of 88** checkable runs, and assertions never
enter. "Test-pinning power" survives in this study only as motivation prose. The endpoint measures
pinning **against the shared reference**, not against the policy each suite accompanies; the new
`ownPolicyIdentity` score is published beside it so that severance is visible rather than merely
disclosed.

**020 is an instrument repair on Study 019**, which froze at `51cae02`, ran 150 slots and stopped
at decision row 3 with `control-gate-failed: e1-floor` — **no contrast was computed by its
registered decision procedure**. Five instrument defects are on 019's record and 020 exists to
repair them.

## The footing, and what it costs

Study 020 registers on a **two-tier footing** (maintainer ruling M-1 = BOTH, 2026-08-22).

- **Tier C** carries the one confirmatory sentence, R1, and claims only where **all eighteen
  members of a pre-declared sensitivity family** agree in the sign of the A−C difference *and*
  each member's own test rejects at α = 0.05. Both poles of every axis are retained; membership is
  append-only after registration. The only two verdicts are **CLAIM** and
  **INDETERMINATE-BY-DISAGREEMENT**, and an INDETERMINATE outcome licenses no negation.
- **Tier D** carries 019's known direction, openly and with its provenance, plus every descriptive
  quantity — each under the standing clause *descriptive; published as an interpretation quantity
  that no decision reads*.

**No direction is registered anywhere in this study**, and the honest test of the footing is
printed in the preregistration rather than argued: **019's own batch could not have passed
Tier C** (16 positive / 2 negative, 10 of 18 rejecting), and an ITT-only family — the one pole
whose removal would have produced a claim — rejects **66–68 % of the time under a null in which
coverage is identical and only authoring validity differs**.

## Layout

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — the draft protocol, with `GATE(pre-freeze)` markers
  for the ceremony's work and `TODO(prereg)` markers for values that cannot exist yet.
- [`PREREG-REVIEW.md`](PREREG-REVIEW.md) — the pre-freeze review record and the round-state block.
- [`DEVIATIONS.md`](DEVIATIONS.md) — empty until something departs from a frozen preregistration;
  nothing is frozen. Outside the freeze set by design.
- [`design/BRIEF.md`](design/BRIEF.md) — the design brief v2, every figure re-derived from 019's
  frozen artifacts with no new model calls.
- [`design/RULINGS.md`](design/RULINGS.md) — the twelve maintainer rulings of 2026-08-23 and the
  M-14 forensic verdict. **Where this study's documents and the brief disagree, the rulings
  govern.**
- [`design/PANEL-FINDINGS.md`](design/PANEL-FINDINGS.md) — the panel findings on brief v1,
  verbatim.

## The ceiling, stated now

This study measures single-shot authorship within a fragment selected by arm A's expressive
envelope. It cannot attribute any part of a bundled A−C contrast to a component of that bundle; it
cannot separate representation from training familiarity; its endpoint is coverage against a shared
reference over a support of **28 of 33** attainable classes; it registers **no author-side control
gate**, because the one 019 used cannot be certified at any affordable n; and if the truth resembles
019, Tier C returns INDETERMINATE with probability approaching 1 — an outcome the study commits in
advance to publishing with a claim's prominence. This program measures **binding, lineage and
expressiveness — never truth.** Nothing here claims any JPS conformance.
