# Study 019 — R2 amendment: the descriptive record, published in full

**What this is.** Study 019's registered attempt stopped at decision row 3
(`control-gate-failed: e1-floor`); §5's rule blocked every *inferential* quantity, and R2's
charter — the failure map, published whichever way it lands — was left partly unfilled
because the arm-labelled E4 quantities sat in an ambiguous state after the design phase of
the follow-up brief computed them (the provenance is recorded verbatim in
`../020-test-pinning-across-representations/design/BRIEF.md` §2.2 and
`design/PANEL-FINDINGS.md` finding #1). The maintainer's two-tier ruling (M-1 = BOTH,
2026-08-22) and its M-15 decision resolve that state: **the blocked descriptive content is
R2 content and belongs on the public record**, precisely so that any future design that
knows these numbers is disciplined by a public prior rather than a private one.

**What this is not.** Nothing here is inferential and no decision reads it. Row 3's verdict
stands; no contrast, interval or direction is licensed by anything below. The §5 clause
carries over verbatim: *no decision reads them.*

The two sections below are reproduced from the Study 020 design brief v2 (on `main`,
commit-pinned by this file's own history), where every figure was re-derived from this
study's `results/primary-attempt-001/RESULTS.json`, the mutant manifests and the gold —
the derivations and their cohort labels are part of the reproduction, because the one
prior mis-statement of these figures was a cohort mislabelling.

---



---

#### 4.3.1 The on-019 table — Tier C would not have fired

Arm-labelled **by design**, under Tier D. Unadjusted members: label permutation, B = 20,000, seed 11. Adjusted members: whole-record permutation, B = 4,000, seed 11. Corrected scorer throughout.

| id | level | engine | population | adj | n (A/B/C) | **A−C** | p | **A−B** | p |
|---|---|---|---|---|---|---|---|---|---|
| M1 | L1 | incl | ITT | — | 38/37/39 | **+0.1385** | **0.0137** | +0.1317 | **0.0229** |
| M2 | L1 | incl | PP | — | 34/26/28 | **+0.0408** | **0.0213** | +0.0186 | 0.2957 |
| M3 | L1 | incl | PP | ANCOVA | 34/26/28 | +0.0161 | 0.2309 | +0.0213 | 0.1110 |
| M4 | L1 | excl | ITT | — | 38/37/39 | **+0.1576** | **0.0137** | +0.1498 | **0.0229** |
| M5 | L1 | excl | PP | — | 34/26/28 | **+0.0464** | **0.0213** | +0.0211 | 0.2957 |
| M6 | L1 | excl | PP | ANCOVA | 34/26/28 | +0.0183 | 0.2309 | +0.0243 | 0.1110 |
| M7 | L3 | incl | ITT | — | 38/37/39 | **+0.1438** | **0.0210** | +0.1376 | **0.0319** |
| M8 | L3 | incl | PP | — | 34/26/28 | +0.0346 | 0.1569 | +0.0118 | 0.6133 |
| M9 | L3 | incl | PP | ANCOVA | 34/26/28 | **−0.0026** | 0.8823 | +0.0160 | 0.3077 |
| M10 | L3 | excl | ITT | — | 38/37/39 | **+0.1694** | **0.0165** | +0.1615 | **0.0259** |
| M11 | L3 | excl | PP | — | 34/26/28 | +0.0469 | 0.0871 | +0.0199 | 0.4434 |
| M12 | L3 | excl | PP | ANCOVA | 34/26/28 | +0.0053 | 0.7881 | +0.0245 | 0.1577 |
| M13 | L2c | incl | ITT | — | 38/37/39 | **+0.1463** | **0.0210** | +0.1416 | **0.0296** |
| M14 | L2c | incl | PP | — | 34/26/28 | +0.0314 | 0.1991 | +0.0104 | 0.6570 |
| M15 | L2c | incl | PP | ANCOVA | 34/26/28 | **−0.0036** | 0.8263 | +0.0142 | 0.3779 |
| M16 | L2c | excl | ITT | — | 38/37/39 | **+0.2323** | **0.0008** | +0.2276 | **0.0014** |
| M17 | L2c | excl | PP | — | 34/26/28 | **+0.1275** | **< 0.0001** | +0.1065 | **< 0.0001** |
| M18 | L2c | excl | PP | ANCOVA | 34/26/28 | **+0.0911** | **0.0002** | +0.1105 | **0.0002** |

> **A−C: direction unanimity FAILS (16 positive, 2 negative). Test unanimity FAILS (10 of 18 reject).**
> **Tier C verdict on 019's batch: INDETERMINATE-BY-DISAGREEMENT.**
> A−B is unanimous in direction (18 positive) but only 8 of 18 reject — and it is unreachable anyway, gated behind A−C.

**Robustness of that verdict to the choice of family** (the objection Tier C must answer). Dropping every member carrying a given pole and re-evaluating:

| pole dropped | members left | positive | reject | verdict |
|---|---|---|---|---|
| L1 | 12 | 10 | 6 | INDETERMINATE |
| L3 | 12 | 11 | 8 | INDETERMINATE |
| L2c | 12 | 11 | 6 | INDETERMINATE |
| engine-included | 9 | 9 | 6 | INDETERMINATE |
| engine-excluded | 9 | 7 | 4 | INDETERMINATE |
| ITT | 12 | 10 | 4 | INDETERMINATE |
| **per-protocol** | **6** | **6** | **6** | **CLAIM** |
| adjusted | 12 | 12 | 9 | INDETERMINATE |
| unadjusted | 6 | 4 | 1 | INDETERMINATE |

**Read the one exception.** An ITT-only family would have claimed on 019 — and §4.3.3 shows that ITT members reject **66–68 % of the time** under a null in which coverage is identical and only authoring validity differs. The per-protocol pole is not decoration; it is the guard that keeps an OPA-toolchain failure rate from being reported as a representation effect. This table is registered as a **mandatory reprint** in the preregistration (M-21).

**The single-choice ledger — what a one-member registration could have licensed.** Tier D continuity rows on 019's *own registered* quantity (raw L2, no offset correction), same methods:

| population | engine | adjustment | A−C | p |
|---|---|---|---|---|
| ITT §1a | incl | — | +0.1004 | 0.1068 |
| ITT §1a (`caseCount` = 0 imputed) | incl | ANCOVA | **−0.0805** | **0.0007** |
| ITT §1a | excl | — | **+0.1867** | **0.0050** |
| ITT §1a (`caseCount` = 0 imputed) | excl | ANCOVA | +0.0030 | 0.9205 |
| per-protocol | incl | — | −0.0182 | 0.4578 |
| per-protocol | incl | ANCOVA | **−0.0532** | **0.0012** |
| per-protocol | excl | — | **+0.0783** | **0.0031** |
| per-protocol | excl | ANCOVA | **+0.0419** | **0.0227** |

**Two of these reject at α = 0.05 in opposite directions, one at p = 0.0007.** Any single-member registration drawn from this set is a coin whose face the design phase had already seen — which is panel #1's finding, and what Tier C exists to make impossible. Registered as the second mandatory reprint. **019's registered quantity is published here with its structural offset (−0.0496) attached, never without it.**


---

*Amendment recorded 2026-08-23 under M-15. The Study 020 design (its two-tier registration,
the eighteen-member family, and the operating characteristics) is shelf-ready in
`../020-test-pinning-across-representations/design/`; the maintainer's decision of
2026-08-23 is that no new batch runs unless a concrete reason to know the answer appears.*
