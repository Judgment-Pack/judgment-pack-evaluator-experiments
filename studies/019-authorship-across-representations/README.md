# Study 019 — authorship across representations

**Status: PREREGISTRATION DRAFT, ninth major revision. Not frozen, and nothing citable has
run — every freeze pin is null and every execution so far is a non-citable pilot. The
cross-vendor review rounds under the RFC 0009 interim review regime are recorded in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md), with each round verbatim under
[`reviews/`](reviews/). The rendered sentence below is this file's ONLY statement of how
many rounds have run, what each returned, and which round is open: it comes from that
record's round-state block through `harness/render_round_status.py`, and the currency suite
requires it here verbatim. Round 4's verdict was the first of the regime that was not a
refusal, and round 5 took it back on a blocker that was the maintainer's own commit hygiene:
a bytecode cache committed with the round-4 response, which made `integrity.py` refuse the
committed tree and the round-4 suite claim describe a tree that HEAD was not. Round 6 found
that class one level up, and round 7 found it a third time — the round-opening commit itself
was red — beside a fourth consecutive round of currency-guard bypasses, which the registered
maintainer decision of 2026-08-19 answers by DESCOPING the English-semantics guard layer
back to this program's baseline rather than escalating it again. The freeze requires a round
verdict of exactly `freezable as written`, which no round has returned.**

<!-- round-status:begin -->
ROUND STATUS (rendered from PREREG-REVIEW.md's round-state block by harness/render_round_status.py; edit the block, never this sentence): 8 review rounds are on the record, 8 have returned a verdict — rounds 1-3 and 5-8 returned DO NOT FREEZE; round 4 returned FREEZABLE AFTER LISTED FIXES — and no round is open.
<!-- round-status:end -->


## The question

Within the registered JPS-expressible policy fragment, under single-shot authorship, does
the representation a model authors in change **what its accompanying test suite pins
down** — compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a
prescribed judgment convention (arm C)?

That is the registered question, and it is narrower than the one this file used to state.
The primary endpoint is **test-pinning power**, not policy correctness: in the calibration
pilot every completed run in every arm agreed with every gold row then authored, so
correctness is at ceiling for well-specified prose at this scale and the dimension with
variance is what the run-authored suites catch. Correctness survives as a reported control
(E1), and the ceiling itself is a finding the study commits to publishing.

Three arms author the same policy from the same prose, 50 independent single-shot runs per
arm, graded against an externally authored gold suite that no arm's artifacts helped build.

**What A−C compares, and what it does not license.** Arm C is *not* arm B plus formality —
that reading is withdrawn (round-1 finding R1-17). Arm B receives a result-shape-only floor
contract, mechanically de-formalized from C's schema. Arm C receives the full prescribed
judgment convention: the same result shape as a JSON Schema *plus* five substantive
conventions. **A−C therefore contrasts the pack format against Rego-plus-the-full-convention
as bundles**, the registered estimand is the bundle's effect, and **no attribution of any
part of an A−C result to any component of the bundle is licensed.** No result here says
what "the language investment" buys, and the preregistration prohibits the claim in §1, §5
and §9.

**No direction is registered.** The design-phase pilot pointed arms B and C above A; that
reading did not survive the arm-A reference repair, and the current pilot points weakly the
other way on five runs per arm. R1 is registered two-sided with no expected direction.

## Provenance

The study responds to an external advisory note (2026-08) proposing a JPS-vs-Rego authorship
experiment. The note was adopted in substance and corrected against source in three places
(output-side expressiveness; the gating behavior of derived boundary probes; oracle/facts
asymmetries across engines). The design brief was then put through a three-lens adversarial
panel before this scaffold was cut; the brief and the panel's verbatim findings are under
[`design/`](design/). The panel is design provenance, not an RFC 0009 review round.

One design-phase claim did not survive review: the inexpressibility class **X1** was
registered as a region the pack format could not express, was tested rather than argued in
round 1, and **is retired** — the arm-A reference was repaired
(`design/reference/refA/PACK-CHANGE-001.md`), the two references now agree on the full
236,196-cell derived space, and the registered exclusion registry is empty. Any document in
this tree that still treats X1 as a live exclusion is stale, and the currency suite
(`harness/tests/test_prereg_currency.py`) exists to catch that class of drift.

## Layout

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — the draft protocol (registered structure,
  settled decisions, and the `GATE(pre-freeze)` markers for everything still open).
- [`PREREG-REVIEW.md`](PREREG-REVIEW.md) — the pre-freeze review record: rounds, verdicts,
  and a written maintainer disposition per finding.
- [`reviews/`](reviews/) — each round's prompt and review, verbatim.
- [`design/BRIEF.md`](design/BRIEF.md) — the panel-reviewed design brief (v3, with the
  maintainer's three design decisions of 2026-08-14 recorded).
- [`design/PANEL-FINDINGS.md`](design/PANEL-FINDINGS.md) — the three-lens panel findings on
  brief v1, verbatim, with the lens prompts summarized.
- [`DEVIATIONS.md`](DEVIATIONS.md) — empty until something departs from a frozen
  preregistration; nothing is frozen.

## The ceiling, stated now

This study measures single-shot authorship reliability within a fragment selected by arm A's
expressive envelope. It cannot show that any representation is better for business judgments
in general (Study 003: 12/12 surveyed real decisions escape the pack), it cannot separate
representation from training familiarity unless the registered gradient measurement runs, it
cannot attribute any part of a bundled contrast to a component of that bundle, and it says
nothing about whether any policy or fact is true. Nothing in this repository claims any JPS
conformance.
