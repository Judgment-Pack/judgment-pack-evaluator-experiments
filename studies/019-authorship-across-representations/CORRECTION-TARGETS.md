# CORRECTION-TARGETS.md — where a correction would have to land, pinned before the freeze

`PREREGISTRATION.md` §10 commits this file: the verbatim published wording of every claim
this study may have to correct, its venue, its URL and its retrieval date, pinned before
the freeze so the correction target cannot drift after the data (round-7 finding R7-9 made
it a registered document; `make_manifest.py --freeze` refuses while it is absent). The
pattern is Study 012's `CLAIM.md`, which bound that study's retraction target the same way.

## Target 1 — the design-phase pilot's directional read

**Venue:** `design/mutants/E4-NOTES.md` in this repository — a committed design record on
`main` of `Judgment-Pack/judgment-pack-evaluator-experiments`, which is a published venue
in exactly the sense Study 012's first target was: public, attributable, and quotable by a
reader who never opens the harness.

**URL (commit-pinned):**
<https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/c7ce3269c3d57d29da957b2c2e3556dcbf7e80df/studies/019-authorship-across-representations/design/mutants/E4-NOTES.md>

**Retrieved:** 2026-08-19, from the working tree at that commit.

**Verbatim wording:**

> **E4 discriminates, and in this pilot the direction is B/C above A.** The earlier surface
> read (35–49 authored rows vs 1–4 test rules) was misleading: the Rego test rules are
> table-driven and carry many assertions. Small N; non-citable; but the endpoint has
> headroom and variance, which is what the pivot needed.

**What would require correcting it:** the sentence already labels itself small-N and
non-citable, so a divergent registered result does not falsify it — but a registered result
in the SAME direction must not be reported as confirming a prediction, because the
preregistration (§11) states the anchor "no longer supports either way" after the reference
repair. The correction this file binds is therefore about *use*, in either direction: if
any post-freeze surface cites the pilot direction as evidence — for A or against A — the
correction lands at the head of `CORRECTION.md`, in this venue, quoting this wording.

## The recorded decision: no external venue carries a bound claim

Searched before the freeze: the maintainer's external posts on the program (dev.to,
retrieved 2026-08-19) concern the evaluator's authorship-coverage line (Studies 009–012)
and the trust-input line; none asserts a claim about what a representation's authored test
suite pins — this study's subject. Study 012's own published claim has its own correction
machinery (`studies/012-policy-perturbation/CORRECTION.md`) and is not re-bound here. If a
reviewer of the freeze PR knows an external claim this list misses, adding it is a one-line
edit to this file **before** the squash-merge; after the freeze, a missed target is a
DEVIATIONS.md entry, not a quiet edit.
