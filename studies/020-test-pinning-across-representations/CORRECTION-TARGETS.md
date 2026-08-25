# Correction targets — Study 020 (registered before the freeze)

Preregistration §10 pins, before the freeze, where a correction must land and what it must
correct — verbatim wording, venue, URL, retrieval date — so that a failed, corrected, or
retracted claim has a pre-committed place to be corrected IN, with the same prominence as
the claim (Study 019's pattern; 019 round-7 finding R7-9 is why this is a registered,
freeze-gated artifact rather than a declared intention). **This file FREEZES with the tree
(round-1 finding R1-18):** its first form claimed appendability by design, and a target
register the maintainer may rewrite after the freeze precommits nothing — the amendment the
reviewer forced. `harness/make_manifest.py` registers it in the covered set and refuses
`--freeze` while it is absent; post-freeze venue moves or target status changes are APPENDED
to `CORRECTION-TARGETS-LOG.md` with their dates, and the corrections themselves land in the
target files exactly as each row registers.

The study publishes in-repository. Every venue below is a file in
`Judgment-Pack/judgment-pack-evaluator-experiments`, referenced at `main`; URLs retrieved
2026-08-24. A correction to any target lands in the SAME file, at the SAME prominence
(head-of-file banner for documents; the row itself for index rows), and — for a corrected
or retracted R1 — additionally as a banner at the head of `ANALYSIS.md` and an entry in
`DEVIATIONS.md`, which is freeze-excluded precisely so it can receive one. **A correction
is written in every branch of the outcome space, including "no correction needed" being
visibly audited**: if the primary attempt publishes without incident, `CORRECTION.md` is
still created stating that no target required correction — an absent file is a failure to
publish, never an outcome.

| # | Claim that may need correction | Venue | URL (retrieved 2026-08-24) |
|---|---|---|---|
| T1 | The R1 verdict sentence `ANALYSIS.md` will publish — quoted verbatim from the scorer's published `verdict` member, whose vocabulary is the closed CLAIM / INDETERMINATE-BY-DISAGREEMENT pair plus §5.9's gate rows (`harness/e4lib/decision.py` rows 4 and 5; `score.registered_family()` is the one place the publisher reads a verdict it did not derive) | `studies/020-test-pinning-across-representations/ANALYSIS.md` (does not exist until the attempt; the target binds the file by registered path) | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/020-test-pinning-across-representations/ANALYSIS.md |
| T2 | The study-index row — Question, Theme, Status columns — whose Status cell will carry the R1 verdict | `studies/README.md`, the Study 020 row | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/README.md |
| T3 | The repo-root index row for Study 020 (same Status discipline) | `README.md`, the Study 020 row | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/README.md |
| T4 | The study README's rendered round-status sentence (`render_round_status.py --write` from the ROUND-STATE-BLOCK) and its verdict history, should any round's record require correction | `studies/020-test-pinning-across-representations/README.md` | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/020-test-pinning-across-representations/README.md |
| T5 | **The presence-idiom guard's published power analysis (§3.2)** — the five certified quantities (i)–(v), including (iv)'s counterfactual per-member shift and its published figures in `harness/COUNTERFACTUAL-SHIFT.json` | `studies/020-test-pinning-across-representations/harness/POWER-PRESENCE-IDIOM.md` | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/020-test-pinning-across-representations/harness/POWER-PRESENCE-IDIOM.md |
| T6 | **The pre-pilot sweep's published table and the compute condition chosen from it (§2.1)** — the per-setting durations, outcome profile, the named rule that chose the condition, and the re-priced batch | `studies/020-test-pinning-across-representations/sweeps/2026-08-24-effort-sweep/SWEEP.md`, and the §2.1 filled entry in `PREREGISTRATION.md` | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/020-test-pinning-across-representations/sweeps/2026-08-24-effort-sweep/SWEEP.md |
| T7 | The Tier D reprints of §5.5 (Reprints 1–3), quoted from a superseded study's batch — correctable only by a `DEVIATIONS.md` entry once frozen | `studies/020-test-pinning-across-representations/PREREGISTRATION.md`, §5.5 | https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/blob/main/studies/020-test-pinning-across-representations/PREREGISTRATION.md |

The verbatim wording of T1 cannot exist before the attempt; what is pinned is its closed
vocabulary — the decision table's row strings as implemented by `harness/e4lib/decision.py`
and published by `harness/score.py`, which are freeze-covered bytes — and the rule that
`ANALYSIS.md` quotes the published string unedited. T6's wording exists as of 2026-08-24: the sweep's
table is published and §2.1's fill names the condition (`low`, N = 60) with the rule that
chose it; the target binds the registered paths and now their published content. For T2–T4 the current wording is whatever those files carry at the freeze
commit; the correction obligation attaches to the row/sentence, not to a snapshot of it.

## Corrections already recorded against these targets (pre-freeze)

**T5, corrected 2026-08-24, pre-freeze.** The power analysis's first printing carried an
unmeasured per-arm split of the flagged set ("arm B 15 of 30, arm C 17 of 30"). The
registered script `harness/counterfactual_shift.py` re-derived the set, its
certified-counts gate refused the printed split, and the measured split is **arm B 19 of
30, arm C 13 of 30** (same certified total, 32). The correction stands in the target file
at the claim's own prominence — a marked correction note in §(iv) — and the refusal that
caught it is kept firing in CI
(`harness/tests/test_counterfactual_shift.py::test_the_certified_gate_refused_the_first_printed_split`).
Because this landed before the freeze, no `DEVIATIONS.md` entry attaches; it is recorded
here so the audit trail shows the target's correction machinery working before it was
needed in anger.

**PREREGISTRATION.md §2.1, corrected 2026-08-24, pre-freeze (two registered-text errors,
found by the fill's verification pass).** The dual-pricing table's sweep and smoke rows
divided calls by nine instead of three (corrected totals ~8.05 h / ~71.2 h; the observed
sweep corroborates the corrected basis), and the swept-set catalog paragraph miscounted
`max`'s availability (4/8, not absent-from-five) and the default tiers (`medium` ×6 +
`high` ×1). Both corrections stand in the document at the claims' own prominence with
marked notes; neither touches the swept set or the rule's load-bearing input. Round-1
finding R1-21 extended the dual-pricing correction to `design/BRIEF.md` §8 (the same table,
appended correction, historical bytes untouched), and R1-20 CORRECTED THE CORRECTION on the
catalog counts: the pre-sweep figures were true of the build-owned `--bundled` catalog, the
first "correction" had recounted a mutable post-call cache, and the original figures are
restored with the provenance lesson marked in §2.1.
