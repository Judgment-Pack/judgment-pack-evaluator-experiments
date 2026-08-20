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
