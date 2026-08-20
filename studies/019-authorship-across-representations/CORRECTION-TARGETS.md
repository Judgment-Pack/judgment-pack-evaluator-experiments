# Correction targets — Study 019 (registered before the freeze)

Preregistration §10 pins, before the freeze, where a correction must land and what it must
correct — verbatim wording, venue, URL, retrieval date — so that a failed, corrected, or
retracted claim has a pre-committed place to be corrected IN, with the same prominence as
the claim (the Study 012 `CLAIM.md` discipline; round-7 finding R7-9 is why this document
is a registered, freeze-gated artifact rather than a declared intention).

The study publishes in-repository. Every venue below is a file in
`Judgment-Pack/judgment-pack-evaluator-experiments`, referenced at `main`; URLs retrieved
2026-08-19. A correction to any target lands in the SAME file, at the SAME prominence
(head-of-file banner for documents; the row itself for index rows), and — for a corrected
or retracted R1 — additionally as a banner at the head of `ANALYSIS.md` and an entry in
`DEVIATIONS.md`, which is freeze-excluded precisely so it can receive one.

| # | Claim that may need correction | Venue | URL (retrieved 2026-08-19) |
|---|---|---|---|
| T1 | The R1 verdict sentence `ANALYSIS.md` will publish — one of the §5 decision table's registered rows, quoted verbatim from `RESULTS.json`'s `verdict` member at the primary attempt | `studies/019-authorship-across-representations/ANALYSIS.md` (does not exist until the attempt; the target binds the file by registered path) | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/019-authorship-across-representations/ANALYSIS.md |
| T2 | The study-index row — Question, Theme, Status columns — whose Status cell will carry the R1 verdict | `studies/README.md`, the Study 019 row | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/README.md |
| T3 | The repo-root index row for Study 019 (same Status discipline) | `README.md`, the Study 019 row | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/README.md |
| T4 | The study README's rendered round-status sentence and its verdict history, should any round's record require correction | `studies/019-authorship-across-representations/README.md` | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/019-authorship-across-representations/README.md |
| T5 | The pilot readings quoted in the preregistration's Design provenance (A 0.878, B 0.897, C 0.806; high-kill 1/5, 0/5, 0/5) — non-citable, but published in a frozen document and correctable only by `DEVIATIONS.md` entry once frozen | `studies/019-authorship-across-representations/PREREGISTRATION.md`, Design provenance | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/019-authorship-across-representations/PREREGISTRATION.md |

The verbatim wording of T1 cannot exist before the attempt; what is pinned is its closed
vocabulary — the §5 decision table's row strings as implemented by
`harness/e4lib/decision.py` and published by `harness/score.py`, which are freeze-covered
bytes — and the rule that ANALYSIS.md quotes the published string unedited. For T2–T4 the
current wording is whatever those files carry at the freeze commit; the correction
obligation attaches to the row/sentence, not to a snapshot of it. A correction is written
in every branch of §5's outcome space, including "no correction needed" being visibly
distinguishable from "correction owed and absent": if the primary attempt publishes
without incident, `CORRECTION.md` is still created, stating that no target required
correction — an absent file is a failure to publish, never an outcome.

## Target bound by the parallel ceremony line (merged 2026-08-19, both lines' work kept)

The parallel fill line searched for claims beyond the T1–T5 in-repo surfaces and bound one
this table lacked, kept here verbatim:

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
