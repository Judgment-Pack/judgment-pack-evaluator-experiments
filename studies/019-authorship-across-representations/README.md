# Study 019 — authorship across representations

**Status: DESIGN DRAFT. Nothing is preregistered, nothing is frozen, and nothing has run.
No review round has read this study. This directory exists so the design can be argued with
in the open before a preregistration is put to the interim review regime.**

## The question

Within the registered JPS-expressible policy fragment, does a constrained judgment
representation (JPS) change how reliably a model authors an executable policy — compared with
raw Rego (the floor) and with Rego plus a prescribed judgment convention (the live
alternative)?

Three arms author the same policy from the same prose, 50 independent single-shot runs per
arm, graded against an externally authored gold suite that neither arm's artifacts helped
build. The comparison the study exists for is A vs C: if a small prescribed convention over
OPA delivers what the JPS language delivers, that is a finding about what the language
investment buys.

## Provenance

The study responds to an external advisory note (2026-08) proposing a JPS-vs-Rego authorship
experiment. The note was adopted in substance and corrected against source in three places
(output-side expressiveness; the gating behavior of derived boundary probes; oracle/facts
asymmetries across engines). The design brief was then put through a three-lens adversarial
panel before this scaffold was cut; the brief and the panel's verbatim findings are under
[`design/`](design/). The panel is design provenance, not an RFC 0009 review round — the
cross-vendor review regime applies to the preregistration and has not begun.

## Layout

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — the draft protocol (registered structure,
  settled decisions, and explicit `TODO(prereg)` markers for everything still open).
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
representation from training familiarity unless the registered gradient measurement runs, and
it says nothing about whether any policy or fact is true. Nothing in this repository claims
any JPS conformance.
