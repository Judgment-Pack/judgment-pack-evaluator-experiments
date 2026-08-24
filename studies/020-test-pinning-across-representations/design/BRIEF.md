# Study 020 design brief — v2

## Test-pinning power across representations (JPS vs OPA/Rego), instrument repair

**Status: design brief v2 — SHELF-READY, not proceeding (maintainer decision 2026-08-23). Nothing in this document is registered.** The M-blocks below were resolved in principle (bundle-A recommendations accepted; the §1 construct renaming to coverage stands); no preregistration drafts and no batch runs unless a concrete reason to know the answer appears. The R2 amendment M-15 required is published at `../../019-authorship-across-representations/R2-AMENDMENT.md`. Written for the maintainer to rule on. Every figure was re-derived for v2 from `results/primary-attempt-001/RESULTS.json`, `mutants/MANIFEST-jps.json`, `mutants/MANIFEST-rego.json`, `gold/GOLD.json`, `harness/PINS.json`, `design/reference/refA/pack.json`, the retained `CALL.json` / `session.jsonl` / `completion.txt` files, `design/pilots/2026-08-15-calibration-pilot-01/`, and `git show a5bb49f:…/design/gold/gold.json` — paths relative to `studies/019-authorship-across-representations/`. **No new model calls were made.** Where a v1 figure, a panel figure, or a v2-draft figure did not reproduce, this document says so in the text rather than fixing it silently.

---

**The footing, stated first.** On 2026-08-22 the maintainer ruled **M-1 = BOTH**. Study 020 registers on a two-tier footing. **Tier C (confirmatory-by-robustness)** carries the study's one confirmatory sentence, R1, and decides only where **every member of a pre-declared sensitivity family** agrees in the sign of the A−C difference *and* each member's own test excludes zero. The family spans exactly the analytic choices that were still open at the moment 019's arm-labelled quantities entered the design record — estimand level, engine-supplied-kill column, analysis population, and covariate adjustment — with **both poles of every axis retained**. Because the verdict requires unanimity across the whole family, no single choice made after the direction became known can manufacture it. **Tier D (direction-aware)** carries everything else: 019's known direction, stated openly with its provenance, used for power planning, apparatus design and interpretation, and every descriptive quantity, each under 019 §5's standing clause — *no decision reads them*.

**The honesty test this footing has to pass, also stated first.** 019's own batch **could not have passed Tier C**. On the eighteen registered members the A−C contrast splits 16 positive / 2 negative and only 10 of 18 reject at α = 0.05 (§4.3.1). That verdict is robust: dropping *any single pole* of *any axis* still yields INDETERMINATE — with one exception, which this brief prints rather than hides. Dropping the per-protocol pole, leaving an ITT-only family, would have produced a **CLAIM** on 019 — and §4.3.3 shows that an ITT-only family rejects **66–68 % of the time under a null in which coverage is identical and only authoring validity differs**. The per-protocol pole is what stops Tier C from calling an OPA-toolchain failure rate a representation effect. That is the single most load-bearing fact in this brief, and it is why family membership is registered before the batch and is append-only afterwards.

---

## 0. Where 019 left the program, and what v2 changes

019 froze at `51cae02`, ran 150 registered slots, and stopped at decision row 3 with `control-gate-failed: e1-floor`. **No contrast was computed by the registered decision procedure.** Five instrument defects are on the record and 020 exists to repair them: an unattainable primary cut (E4 τ = 19/20), a control floor calibrated on a population the registered condition never reproduced (E1), a pilot that measured a different compute condition, an author-side gate whose power was never computed, and a scorer schema that encodes "nothing evaluated" and "everything killed" with the same token.

**What v2 changes relative to v1 and relative to the two v2 drafts.** v1's §2.2 claim that the arm-labelled E4 figures "do not re-derive" was false and is withdrawn (§2.2). v1's attainability gate, τ rule, median-based balance claim, ÷n dispersion figures, 50/35/40 realised-n projection, "order of magnitude more resolution" claim, and "exact permutation interval" are all withdrawn. The two v2 drafts additionally carried, between them, two incompatible families, two verdict labels, two permutation schemes, two scorer semantics and a colliding M-numbering; this document registers **one** of each. Six numeric errors introduced by those drafts are corrected in place and named in §9.

---

## 1. The question, unchanged — and what the endpoint actually measures

`PREREGISTRATION.md` §1 is carried **verbatim** and is not the place to register an instrument repair (panel #35); the E1 repair commitment lives in §3, where it is argued.

One substantive qualification must attach to §1 before the freeze, and it is not cosmetic. §4.2.2 Fact 1 establishes that, conditional on the identity control passing, a run's E4 score is a **deterministic function of which witness inputs its suite reaches**: `killedPaired` equals exactly the summed member count of the witness classes the run covers in **88 of 88** checkable runs. Assertions never enter. Greedy hitting-set over the 51 distinct witness inputs behind the 33 shared classes reaches 33/33 with **21** gold inputs, against authored suites of 16–25 cases. The construct the primary measures is therefore **witness-input coverage against the shared reference**, not pinning power in the sense §1's prose suggests, and not pinning against the policy each suite accompanies (panel #19). **M-18** and **M-26** ask the maintainer to decide between renaming and disclosing; this brief refuses to leave the wording as it stands.

---

## 2. What the 019 batch may and may not be used for

### 2.1 Arm-blindness, demoted from guarantee to reporting discipline

v1 §2.1 registered an arm-blindness rule and v1 §2.2 asserted that "everything in §3–§5 was derived under it." That assertion is **withdrawn** (panel #12). Each violation is named:

- v1 §3.2's disqualification table is arm-labelled outright.
- v1 §3.3's 0.95 threshold sits in the only window that admits more than one arm-A run: arm-A clear rates are **0/36** at ≤ 1 miss, **1/36** at ≤ 2, **1/36** at ≤ 4, **3/36** at ≤ 5 (re-derived from `perArmRuns[].goldFailures`).
- v1 §4.1's "union of all identity-passing **arm-A** suites" is an arm-A quantity by construction, since JPS ≡ arm A.
- v1 §4.2's balance claim read medians of an arm-labelled covariate.

**020 does not rest on arm-blindness.** It rests on the two-tier footing. Arm-blindness survives as a **reporting discipline** — every design quantity is published with the cohort it was computed on — and as a **membership rule**: the sensitivity family's composition is derived without reading arm-labelled outcomes (§4.2.1), which is a checkable property of the admission test, not a claim about anyone's state of knowledge.

### 2.2 What leaked, when, and the figures themselves

**v1's sentence "They do not re-derive" is withdrawn. It was false.** The gold/stratification lens's arm-labelled E4 means reproduce to five decimals on the cohort that lens used; v1 concluded non-reproducibility because it recomputed on a *different* cohort and named neither — the same defect v1 convicts issue #88 of one page earlier.

Mean of `kill.killedPaired / kill.paired` and of the shared-class coverage fraction, **corrected scorer throughout** (§4.2.2's empty-survivor rule):

| cohort | level | A | B | C | A−C | A−B |
|---|---|---|---|---|---|---|
| artifact-bearing, all (36/30/30) | mutant | **0.60628** | **0.59032** | **0.61613** | **−0.00985** | +0.01596 |
| identity-passing (34/26/28) | mutant | 0.64194 | 0.68114 | 0.66014 | −0.01819 | −0.03920 |
| identity-passing (34/26/28) | group, 33 shared | 0.61765 | 0.59907 | 0.57684 | **+0.04081** | +0.01858 |
| identity-passing (34/26/28) | symmetrised mutant | 0.67333 | 0.66148 | 0.63877 | +0.03456 | +0.01185 |
| §1a admitted, ITT-114 (38/37/39) | group, 33 shared | 0.55263 | 0.42097 | 0.41414 | **+0.13849** | +0.13167 |

Row 1 is the gold lens's "A 0.606 / B 0.590 / C 0.616". Row 2 is what v1 computed and mislabelled a failure to reproduce.

**The direction is known to the design phase, and it is not one direction.** At the mutant level — the level 019 registered and scored — **A is below C**. At the group level — the level the primary now uses — **A is above C**, and on the identity-passing cohort that difference clears α = 0.05 (exact two-sided label permutation, 20,000 draws, seed 11: **p = 0.0213**) while the mutant-level one does not (**p = 0.4578**). Re-weighting 69 JPS and 62 Rego mutants into 33 shared witness classes moves the contrast by 0.059 and carries it across the boundary. Panel #2's reconstruction is confirmed in full.

**Panel #1's "+0.0065 (artifact-bearing)" reproduces exactly, and the v2 draft that proposed withdrawing it was wrong.** Group-level A−C on the artifact-bearing complete-case cohort (n = 36/28), with the two arm-A empty-survivor runs correctly scored as coverage 0, is **+0.00649, p = 0.8601**. The draft's "+0.06205 (drop the six) / +0.10051 (zero-fill)" are the *uncorrected* values — the draft failed to find the panel's figure for precisely the scorer defect the other half of the same document had discovered. **Nothing is withdrawn here; the panel's number stands.**

**Procedurally.** The arm-labelled primary contrast, in every candidate form, is on the record. Per 019's own R2 text — *"a direction computed and then withheld is a direction published"* — it may not be held privately while a brief written on top of it claims blindness. **M-15** proposes publishing it as an amendment to 019's R2 disposition before 020's preregistration is drafted.

### 2.3 Issue #88, corrected before it is cited

Re-derived from `perArmRuns[].goldFailures` over the 96 artifact-bearing runs (A 36 / B 30 / C 30). Every v1 figure reproduces.

| Row | #88's claim | A | B | C | pooled |
|---|---|---|---|---|---|
| `p1-absent-escalation-region` | 47/48 | **35** | 6 | 2 | 43 |
| `p1-unreported-escalation-region` | 47/48 | **35** | 0 | 0 | 35 |
| `x1r-country-unreadable-{100k,40,69}` | 34–35/48 | 28 each | 20 | 13 | 61 each |
| `x1r-low-spend-unreadable-{40,69}` | 34–35/48 | 27 each | 20 | 13 | 60 each |
| perfect on the remaining 110 | 5/48 (10.4 %) | **3** | **8** | **14** | **25** |

#88's `/48` denominator exists nowhere in `RESULTS.json` (ITT 38/37/39; artifact-bearing 36/30/30; identity-passing 34/26/28). Its qualitative diagnosis survives and is sharper: restricted to non-collapsed runs (< 50 misses), **35 of 36 arm-A runs miss at least one of the seven, and 0 of 10 non-collapsed arm-B and 0 of 17 non-collapsed arm-C runs miss any of them** — the x1r counts (20 in B, 13 in C) are exactly the collapsed-run counts. Arm A's residual outside the seven is a named family: `u1-two-unreadable-uniform` 14/36, `u1-risk-prior` 13/36, `u1-country-2m` 8/36, `u1-ex1` 7/36, then `o1-nv-*` at 4–6 — unknown propagation. **M-11**: correct #88 before any 020 document cites it; do not carry "10.4 % vs the 0.6 floor" forward.

### 2.4 Tier D's charter

**The prior, stated once, in full.** From 019's registered batch: at the mutant level arm A's paired kill fraction is **below** arm C's; at the group level and the symmetrised-mutant level it is **above**. All are in §2.2's table; none was produced by 019's registered decision procedure, which stopped before computing any contrast. Provenance: **the design phase, not the study.**

**Tier D MAY use the direction for:** (1) **power planning** — N, pilot N, effort pin, against magnitudes and dispersions honestly informed by 019; (2) **interpretation** — after Tier C reports, saying per member whether 020's directions agree with 019's, with both sets of figures printed; (3) **apparatus design** — analysis-set disposition, missing-data rule, the scorer's survivor-vector requirement, all functions of *how many runs score*, not of which arm wins; (4) **naming the risk** — every place a design choice is known to move the contrast is disclosed with its magnitude: the estimand level (0.059 at identity-passing), the adjustment (0.0247 at group level), the population (0.098 at group level between identity-passing and the §1a denominator), the engine column (0.0056 at group level, per-protocol).

**Tier D MAY NOT:** (1) **write any confirmatory sentence** — no Tier D quantity adjudicates R1 or enters the decision table; 019 §5's R1-15 discipline is carried verbatim onto every Tier D quantity, and an INDETERMINATE Tier C outcome licenses no negation; (2) **select a Tier C family member** — membership is fixed by §4.2.1's arm-blind admission test and is append-only; (3) **fix a threshold, cut, floor or trim** — any threshold in 020 is derived by a committed rule or an attainability probe, never chosen against an arm-labelled rate; (4) **be reported without its tier label** — every Tier D table carries *"descriptive; no decision reads this."*

**M-12 (revised):** publish 019's blocked descriptive content — union ceilings, single-witness fractions, never-covered class identities, the E1 mechanism split, the B/C collapse mechanism, and §2.2's arm-labelled quantities — as 019 R2 content. Row 3 blocked *inferential* quantities, not the failure map. Under the two-tier footing this is no longer optional: Tier D's charter is unenforceable if the prior it disciplines is not on the public record.

### 2.5 Why the leak does not reach Tier C

Tier C's integrity argument is **structural, not epistemic**. Three properties carry it, and all three are registered:

1. **Intersection–union.** Requiring every member to reject at α = 0.05 is an IU test; its size is **≤ α** over the union null, with **no multiplicity correction** (§4.2.5). Adding members can only reduce size.
2. **Membership is derived arm-blind and is append-only.** The admission test (§4.2.1) reads the design record's chronology and the frozen corpus's structure, never an arm-labelled outcome. After the freeze a maintainer may **add** a member — monotone toward INDETERMINATE — never remove one; an addition requires a `DEVIATIONS.md` entry and the pre-addition verdict is published beside the post-addition one.
3. **Every member is published whatever the verdict.** Unanimity is not a filter over what gets reported.

**What the argument does and does not cover, stated plainly.** Unanimity neutralises a leaked-influenced choice made *inside* the family. It does not, by itself, neutralise the choice *of* family — which is why criterion (i) of the earlier draft ("the axis is outcome-determinative on 019's batch") is **withdrawn**: it read arm-labelled outcomes to decide membership, and under the IU logic *removing* members is the anti-conservative direction. §4.3.1 then shows empirically that on 019 the INDETERMINATE verdict survives dropping any single pole except the per-protocol one, and §4.3.3 shows why that one exception is the pole that must never be dropped.

---

## 3. E1 — the control that was not a control

**The mutually exclusive picture** (v1's §3.1 table double-counted "Perfect" inside "Near-gold" and its rows did not sum to their ITT counts — panel #18; the v2 draft's replacement corrupted the code annotations — see §9):

| Arm | ITT | no scorable artifact | collapsed ≥ 50 misses | intermediate 1–49 | perfect |
|---|---|---|---|---|---|
| A | 38 | 2 (`no-marker-block` 2) | 0 | **36** (2–15) | **0** |
| B | 37 | 7 (`opa-check-failed` 4 + `unparseable-artifact` 3) | **20** (86–104) | **2** (2–13) | 8 |
| C | 39 | 9 (`opa-check-failed` 9) | **13** (86–104) | **3** (2–13) | 14 |

Codes re-derived from `perArmRuns[].code` over runs with no `kill` block; they sum to their column exactly. (`unparseable-artifact` also appears on 4 arm-B and 2 arm-C runs that *do* carry a `kill` block — those are the six survivor-vector-less runs of §4.2.3, and they are not in this column.) Footnote 1's "arms B and C are bimodal — **perfect or** 86–104 misses" is false for those five runs; restate as *strongly bimodal, with 2 and 3 intermediate runs*. §3.2's ceilings (0.270 = 10/37, 0.436 = 17/39) are unaffected and correct. **"Collapsed" is a cohort label introduced by this brief, not a registered category.**

019's actual finding — *arm A never achieves perfect gold agreement, and the mechanism is a derived lemma the prose never states* — becomes a reported result under §5's disposition rather than a study-killer.

**The gate question is re-opened, on arithmetic.** §6.3 C3(iv) shows that an existence gate ("at least one admitted run reaches agreement ≥ x") is a max statistic whose stringency runs the wrong way in n, that it spuriously refuses arm A with probability **1.3–6.1 %** at 019-scale N even with a perfect stimulus, and that certifying it at P(fire) ≥ 0.95 would need **~2,926 degraded runs** at N = 50. **M-23** re-opens v1's M-2 on that basis.

---

## 4. E4 — the primary, re-specified

### 4.1 Withdrawn from v1, and what replaces it

v1 §4.1's "attainability gate with teeth" and v1 §4.2's secondary τ rule are **withdrawn, not repaired** (panel #6, #7). Tier C registers **no cut, no threshold and no dichotomy**, so it has no attainability problem: there is no τ that can be unattainable, which is the property that killed 019's E4 (`e4.*.highKillRate.count` = 0 in all three arms at cuts of 66/69 and 59/62, against union-kill ceilings of 61/69 and 54/62 over every identity-passing run). **No replacement attainability machinery is registered** — no probe, no refusal branch, no τ anywhere, including in Tier D, where the full coverage distribution is published instead of any dichotomy. The argument for a continuous endpoint is *not* v1's "order of magnitude more resolution" (panel #11: incommensurable scales) and *not* the v2 draft's "ratio ≈ 1.1–1.4×" restatement of the same comparison; it is that a continuous endpoint has no cut to place, discards no information, and cannot produce 019's `0 / 0 / 0`. **No cross-scale comparison is made anywhere in §4.**

### 4.2 The sensitivity family

#### 4.2.1 The admission test (arm-blind by construction)

An analytic choice becomes a **family axis** iff:

| | Criterion |
|---|---|
| **(i)** | **Openness.** The choice was still open at the moment 019's arm-labelled quantities entered the design record. |
| **(ii)** | **Both poles defensible.** Each pole is a defensible answer to §1's question. An axis with one indefensible pole is a correctness question, not a robustness question. |
| **(iii)** | **No known structural bias.** Neither pole is provably biased under a true null by a quantity computable from the frozen corpus alone. Where one is, it enters **in its de-biased form**, and the raw form is published in Tier D. |

All three read the design record's chronology, §1's wording, and the frozen manifests. **None reads an arm-labelled outcome.** The earlier draft's fourth criterion — *"the panel demonstrated the axis is outcome-determinative on 019's batch"* — is **withdrawn**: it selected family membership from the leaked direction, and under §4.2.5's own logic dropping members raises size. Its two consequences (rejecting the native mutant level, refusing the engine axis) are both reversed here.

#### 4.2.2 Two structural facts, both derived from the manifests

**Fact 1 — kill reduces to witness-class coverage, conditional on identity-pass.** For every one of the **88** runs that carry a non-degenerate survivor vector, `killedPaired` equals **exactly** the summed member count of the witness classes the run covers (88/88, zero mismatches), and `gall == gany` in 88 of 88. A run is therefore fully described, language-neutrally, by the subset S of the 33 shared classes its suite reaches; every candidate endpoint is a weighted count over S and members differ only in weights. **The checkable denominator is 88, not the 114 the panel and both v2 drafts asserted**: only 90 runs carry a survivor vector at all, and two of those are degenerate (below).

> **The empty-survivor trap — a scorer defect not in the panel's list.** Two arm-A runs (`run-025`, `run-046`, both `identityPass: false`) carry `survivorsPaired: []` **with `killedPaired: 0`**. Read naively — "no survivors ⇒ everything killed" — they score a perfect 33/33 when they killed nothing. On 019 this single schema trap moves the group-level ITT A−C contrast from **+0.19112 (naive) to +0.13849 (corrected)** — magnitude **0.0526**, a 38 % shift, and note the direction: correcting the trap **lowers** A−C. (The earlier draft reported this as "+0.1161 → +0.1385, a 19 % shift"; that gap is entirely the drop-vs-zero-fill of a *different* six runs, and the trap's own effect was understated 2.4× and given the wrong sign.) It is also what made the panel's +0.0065 irreproducible to that draft. **020's scorer must emit an explicit per-mutant survivor vector for every admitted run and must never encode "nothing evaluated" and "everything killed" with the same token.** Registered as a day-one requirement. Every figure in this document uses the corrected reading.

**Fact 2 — the native mutant-level estimand is structurally biased between languages.** Of the 33 shared classes, **20 have unequal member counts across languages** (13 JPS-heavier, 7 Rego-heavier; extremes `d7-39-100k` 6 JPS vs 3 Rego, and the four-input `d1-match|…` class 1 JPS vs 4 Rego). Under a true null for the construct — both arms drawing coverage sets from the same distribution — the expected A−C contrast of a candidate level with weights w^A, w^C is

  offset = Σ_g π_g · ( w^A_g − w^C_g ),  π_g = pooled coverage marginal of class g.

| level | weights w^A_g / w^C_g | offset at 019's pooled coverage profile | worst case |
|---|---|---|---|
| **L2 — native mutant** (019's registered quantity) | \|J_g\|/69 vs \|R_g\|/62 | **−0.0496** (per-protocol) / −0.0485 (ITT) | 0.5400 |
| **L2, engine-excluded** | \|J^ex_g\|/57 vs \|R_g\|/55 | **−0.0492** / −0.0481 | 0.5046 |
| **L1 — group**, weight 1/33 each | 1/33 vs 1/33 | **0 by construction** | 0 |
| **L3 — symmetrised mutant**, w_g = (\|J_g\|+\|R_g\|)/131 | identical in both arms | **0 by construction** | 0 |

−0.0496 is larger than any representation effect the study plausibly seeks. So L2 fails criterion (iii) in its raw form — and by criterion (iii) it enters **de-biased**, not removed:

> **L2c, registered definition.** Per-run outcome = the native-denominator paired kill fraction; then **off̂ is subtracted from every *scoreable* arm-A run's outcome**, where off̂ = Σ_g π̂_g(w^A_g − w^C_g) and π̂ is the pooled, arm-label-free coverage marginal over the scoreable runs of that member's own analysis population. Unscoreable runs score 0 in both arms and take no offset. On 019: off̂ = −0.04956 (per-protocol, engine-included), −0.04846 (ITT), −0.04922 / −0.04813 excluded-column.

Three limitations of L2c are registered as ceilings rather than discovered later: π̂ on the per-protocol population is estimated on a post-treatment-selected cohort (arm-label-free, but not treatment-free); off̂'s estimation variance is not propagated into the member's test; and for the adjusted members the offset is subtracted from unit outcomes *before* the ANCOVA, so the adjusted contrast inherits it linearly. **M-16(d)** puts these to the maintainer. L3 needs no estimated offset at all and is unbiased for *any* π — which is the reason it is in the family beside L2c rather than instead of it.

> **What this does *not* fix — panel #15 is not closed.** L3 repairs the **weighting** asymmetry. It does not repair the **attainability** asymmetry #15 actually names: under the all-members rule, an arm-A suite must kill six mutants to score the `d7-39-100k` unit where an arm-C suite kills three. The offset formula above assumes π_g is common to both arms, which unequal member counts and unequal per-class difficulty deny. **V8-22 stays live in the asymmetry ledger, and a new ledger row is registered for group-size imbalance.** The per-class member-count table is a mandatory Tier D publication.

#### 4.2.3 The eighteen registered members

The family is the crossing **{L1, L3, L2c} × {engine-included, engine-excluded} × {ITT-unadjusted, PP-unadjusted, PP-adjusted}**.

- **Level axis, three poles.** L1 group (a class is one unit); L3 symmetrised mutant (a class weighing 6 JPS + 3 Rego is a bigger unit than one weighing 1 + 4); L2c de-biased native mutant (019's registered quantity, made unbiased). All three are defensible answers to §1 and they are genuinely different estimands.
- **Engine-supplied-kill axis, two poles.** Excluding engine-supplied kills drops **12 of 69 paired JPS mutants and 0 of 62 paired Rego**, taking the shared class set from **33 to 29** and the JPS/Rego paired totals to 57/55. The exclusion is entirely one-sided, which is an arm-blind reason it could matter; the earlier draft's refusal of this axis was argued from 019's arm-labelled contrasts and is reversed. Both columns are members.
- **Population × adjustment, three cells.** ITT = every §1a admitted run (38/37/39 in 019), a run with no scorable suite scoring 0. Per-protocol = identity-passing runs (34/26/28). Adjustment = ANCOVA on `caseCount`, pinned form below.

**The two cells registered *out* of the family, argued.**

1. **ITT × ANCOVA.** `caseCount` is undefined for a run with no parseable suite. Imputing 0 makes the covariate a near-deterministic function of the ITT-vs-per-protocol distinction itself, so adjusting for it partially undoes the very zero-filling the ITT pole exists to impose — a covert change of population, not an adjustment. Re-derived: with `caseCount = 0` imputed, the ITT group-level A−C moves from **+0.1385 to −0.0201** and pooled within-arm SD collapses from **0.25427 to 0.09652**. The six quantities are published in Tier D with this sentence attached. *A naive implementation instead silently drops the covariate-less runs and reproduces the artifact-bearing complete-case cell exactly — a hidden collapse of the family. The scorer must refuse rather than fall back.*
2. **Artifact-bearing complete-case as a third population pole.** A population defined by "carries a survivor vector" admits runs that *failed* the identity control — which the per-protocol pole exists to exclude and the ITT pole includes wholesale. It is neither, and it is registered out on that ground (criterion ii). Its composition on 019 is disclosed in Tier D: it is the per-protocol set plus exactly the two empty-survivor runs.

**Definitions pinned before the freeze.**

1. **Coverage rule.** A run covers class g iff its suite kills **all** of g's members in the run's own language. Panel #14's sub-decision (i) is **withdrawn, not decided**: `gall == gany` in 88 of 88 checkable runs, and Fact 1 shows this is structural for identity-passing runs. The equivalence **and its condition** are registered as a stated fact.
2. **ANCOVA pinned to the byte.** Pooled *within-arm* slope estimated over **all three arms** jointly; adjusted difference evaluated at the grand covariate mean. Re-derived on 019 at L1/per-protocol: slope **b = +0.02332**, arm covariate means A **20.882** / B **21.000** / C **19.821**, adjusted means A 0.6106 / B 0.5893 / C 0.5945 — reproducing panel #3 to four decimals. The two-arm-only slope variant gives A−C = +0.0185 against the three-arm +0.0161; immaterial here, decisive as a registration matter. **Pin the three-arm form; publish the pairwise variant in Tier D.**
3. **Balance registered on means with a test** (panel #4), with a stated threshold and a registered non-claim if it fails. v1's median-based balance claim (21 / 20.5 / 20) is **withdrawn**.
4. **`caseCount = 0`** for a suite that parses to no cases, with the per-arm count of such runs published before the freeze and the complete-case variant published beside it. 020's scorer emits `caseCount` for every admitted run with a suite — the six 019 runs `B run-026/027/032/036`, `C run-035/050` that carried a `kill` block with neither `survivorsPaired` nor `caseCount` (arm A: zero) cannot recur. **These are exactly the same six runs under both defects**, a fact panel #16 and panel #5 did not connect.
5. **Analysis-set arithmetic registered per member** before the freeze; each member's per-arm n published whether or not R1 fires.

#### 4.2.4 R1 — the decision sentence

> **R1 (primary, retractable; confirmatory-by-robustness).**
> *Within the registered JPS-expressible policy fragment, under single-shot authorship, arm A's mean shared-witness-class coverage differs from arm C's — **claimed if and only if all eighteen registered family members agree in the sign of the A−C difference and each member's own two-sided permutation test rejects H₀ at α = 0.05.** The claimed direction is that common sign.*
>
> *If the members do not agree in sign, or if any member's test fails to reject, R1 returns **INDETERMINATE-BY-DISAGREEMENT** and the study makes no confirmatory statement about A vs C. An INDETERMINATE outcome licenses no negation (019 §5, verbatim). The registered δ is published as an interpretation quantity that **no decision reads** (019 §5's R1-15 discipline, verbatim). All eighteen point estimates, all eighteen p-values, all eighteen per-arm n and the full agreement table are published in every outcome.*
>
> *Fixed sequence: A−C, then A−B. The A−B step is evaluated under the identical eighteen-member unanimity rule and is reached only if the A−C step returns a claim.*

**There is exactly one verdict vocabulary: CLAIM or INDETERMINATE-BY-DISAGREEMENT.** The word **UNSUPPORTED is not used anywhere in 020** for this rule; it reads as evidence of no effect, which INDETERMINATE explicitly is not.

**The per-member test, one scheme, stated precisely** (panel #17).

- **Unadjusted members.** Exact two-sided permutation test on the difference in means, permuting arm labels within the two-arm subset. Exact under the sharp null of no unit-level effect. **20,000 permutations**, seed pinned in `PINS.json`, Monte-Carlo p in the (count+1)/(B+1) form.
- **Adjusted members.** The unit's **whole record** (outcome and `caseCount`) travels with the permuted label; **4,000 permutations**, same seed rule. This is exact under the **strong** sharp null — the arm changes neither the suite's coverage nor its size — and 020 must say so plainly: it is *not* an exact test of "no effect on Y given `caseCount`". **Freedman–Lane residual permutation is not registered and is not a cure**: no covariate-adjusted permutation scheme achieves exactness for that null with a treatment-affected covariate, and registering two schemes in one document was itself the defect. The family contains the unadjusted members precisely so that the weaker guarantee is never load-bearing alone.
- **Every table names its method and its B.** Where a normal-theory surrogate is used (only in §4.3.3–§4.3.4's simulation) it is labelled as such; on 019 the two agree closely (L1/per-protocol: permutation p = 0.0213 at B = 20,000, Welch p = 0.0232).
- **The word "exact" is used only of a permutation null distribution, never of an interval.** v1's "exact permutation interval on the difference in means" is **withdrawn** — inverting to an interval needs a location-shift model, and the outcome is bounded, lattice-valued (1/33 = 0.0303), with per-arm SDs differing by 24 % on 019 (0.0602 / 0.0749 / 0.0744). `OC-TABLE.md` §1 records that 019 already had to withdraw an "exact … nominal coverage" claim once (R1-16). **Intervals are Tier D**: BCa bootstrap, per member, coverage stated as approximate, no decision reads them.

#### 4.2.5 α handling — intersection–union

1. **No multiplicity correction is applied, and none is needed.** The claim's alternative is H₁⁺ = {every member's difference > 0} (symmetrically H₁⁻); its null is a **union**. An IU test requiring every member to reject at level α has size **≤ α**, attained only in the least-favourable configuration where one member sits exactly at zero. For a *directional* claim, two-sided p < 0.05 plus a sign is a one-sided level-0.025 test, so the family-wise type-I rate for a signed R1 is **≤ 0.025**. Bonferroni would be not merely unnecessary but wrong.
2. **Realised size is far below the bound** — §4.3.3 puts it at **0.002** at N = 60/arm under a global null.
3. **The price is paid entirely in power**: power ≤ min over members. §4.3.4 gives the numbers and they are not small.
4. **The fixed sequence A−C → A−B spends no α.**

### 4.3 Operating characteristics

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

#### 4.3.2 Dispersion and minimum detectable effect, per member

Pooled within-arm SD, unbiased (N − k; residual N − 4 for the adjusted members) — v1's ÷n figures are withdrawn (panel #31). All arm-blind. MDE = 2.8016 · σ · √(1/n_A + 1/n_C) at two-sided α = 0.05, 80 % power.

| id | σ | MDE @ 019 n | MDE @ N=60, D-1/D-3 cured | MDE @ N=60, + registry cure | MDE @ N=100 |
|---|---|---|---|---|---|
| M1 L1/incl/ITT | **0.25427** | 0.1624 | 0.1379 | **0.1306** | 0.1013 |
| M4 L1/excl/ITT | 0.28934 | 0.1848 | 0.1570 | 0.1486 | 0.1152 |
| M7 L3/incl/ITT | 0.28439 | 0.1816 | 0.1543 | 0.1461 | 0.1133 |
| M10 L3/excl/ITT | **0.32159** | **0.2054** | **0.1745** | **0.1652** | **0.1281** |
| M13 L2c/incl/ITT | 0.28966 | 0.1850 | 0.1571 | 0.1488 | 0.1153 |
| M16 L2c/excl/ITT | 0.29826 | 0.1905 | 0.1618 | 0.1532 | 0.1188 |
| M2 L1/incl/PP | 0.06938 | 0.0496 | 0.0419 | 0.0399 | 0.0309 |
| M5 L1/excl/PP | 0.07895 | 0.0564 | 0.0477 | 0.0454 | 0.0352 |
| M8 L3/incl/PP | 0.09397 | 0.0672 | 0.0568 | 0.0540 | 0.0418 |
| M11 L3/excl/PP | 0.10516 | 0.0752 | 0.0635 | 0.0605 | 0.0468 |
| M14 L2c/incl/PP | 0.09040 | 0.0646 | 0.0546 | 0.0520 | 0.0402 |
| M17 L2c/excl/PP | 0.09479 | 0.0678 | 0.0573 | 0.0545 | 0.0422 |
| M3 L1/incl/PP/anc | **0.05068** | 0.0362 | 0.0306 | 0.0291 | 0.0226 |
| M6 L1/excl/PP/anc | 0.05767 | 0.0412 | 0.0348 | 0.0332 | 0.0257 |
| M9 L3/incl/PP/anc | 0.06114 | 0.0437 | 0.0369 | 0.0352 | 0.0272 |
| M12 L3/excl/PP/anc | 0.06849 | 0.0490 | 0.0414 | 0.0394 | 0.0305 |
| M15 L2c/incl/PP/anc | 0.06049 | 0.0432 | 0.0365 | 0.0348 | 0.0269 |
| M18 L2c/excl/PP/anc | 0.06420 | 0.0459 | 0.0388 | 0.0369 | 0.0286 |

n's: ITT members 38/39 (019), 48/60, 59/60, 98/100. Per-protocol members 34/28 (019), 43/43, 53/43, 88/72. The realised-n branches are derived from `population.*.apparatusCodes` (A: `registry-mismatch` 9, `slot-shape` 2, `transcript-refused` 1; B: `slot-shape` 11, `post-call-failure` 1, `transcript-refused` 1; C: `slot-shape` 11) and the conditional artifact-plus-identity rates A 34/38 = 0.895, B 26/37 = 0.703, C 28/39 = 0.718. The "D-1/D-3 cured" branch pre-pays only `slot-shape` and reproduces panel #32's ≈ **43 / 40 / 43** scoreable at N = 60 (**v1's 50 / 35 / 40 is withdrawn**); "+ registry cure" additionally pre-pays panel #22's coupling, giving ≈ 53 / 40 / 43.

> **The number that governs the design.** σ across the family spans **0.0507 to 0.3216 — a factor of 6.3** (the earlier draft's "3.7–4.6×" was a selected pair). ITT members run 0.2543–0.3216; per-protocol members 0.0507–0.1052. **Tier C's precision is the ITT members' precision**: at N = 60/arm with every apparatus repair the binding MDE is **≈ 0.165** — for the group-level member M4 that is **≈ 4.9 of 33 witness classes**; for M10 (L3) the units are mutant-multiplicity weights and **must not be multiplied by 33** to yield a class count. Panel #5's cure is implemented, and the reason is not conservatism: the ITT members' variance is dominated by a point mass of exact zeros (arms B and C lost 7 and 9 of their §1a admitted runs to `opa-check-failed` / `unparseable-artifact`), a real property of the treatment that no apparatus repair removes.

#### 4.3.3 Size — the integrity argument, quantified and auditable

**The simulation is supplied, not asserted** (this was the earlier draft's only unauditable figure set, and it carried the whole integrity argument). Script: `oc18.py`, seed **20200822**, and the registered specification is:

> Pool = the 88 identity-passing 019 runs with arm labels destroyed, each contributing (coverage set over the 33 shared classes, `caseCount`). A replicate draws N runs iid with replacement per arm. Each drawn run is scoreable with probability p_arm; otherwise it scores 0 on the ITT members and is dropped from the per-protocol members. An effect is imposed as **θ additional covered classes** for arm A's scoreable runs, drawn without replacement from that run's uncovered classes with probability proportional to the pooled coverage marginal π — so the five classes no 019 run ever covered (π = 0) are unreachable and the attainable ceiling stays 28/33. The suite-size-only alternative instead tilts arm A's draws toward larger `caseCount` (weights ∝ exp(0.8·(c − c̄)), which raises mean `caseCount` from 20.58 to 23.43 and mean coverage from 19.77 to 21.38 classes) with θ = 0. Tests are normal-theory surrogates for the registered permutation tests (Welch t; pooled-slope ANCOVA t, df = n − 3). L2c's offset is recomputed from each replicate's own pooled marginal. Tier C fires iff all eighteen agree in sign and all eighteen have p < 0.05. N = 60/arm, 2,000 replicates.

| scenario | per-member rejection | **Tier C** |
|---|---|---|
| **Global null** — equal validity 0.80, θ = 0 | all eighteen 0.036–0.052 | **0.002** |
| **Authoring-validity-only null** — A 0.895 vs C 0.718, coverage identical, θ = 0 | **ITT members 0.660–0.678**; per-protocol 0.036–0.051 | **0.001** |
| **Suite-size-only alternative** — equal validity, size tilt, θ = 0 | **PP-unadjusted 0.986–0.998**; PP-adjusted 0.019–0.067; ITT 0.138–0.165 | **0.000** |
| **True coverage effect** θ = 3, equal validity | PP members 0.999–1.000; ITT 0.251–0.351 | 0.248 |

This is the integrity argument in numbers, and it holds in both directions the panel worried about:

- **The authoring-validity channel alone cannot produce a Tier C claim.** It rejects on two-thirds of ITT members and 3.6–5.1 % of per-protocol ones; unanimity collapses it to **0.001**. An ITT-only registration would have called this a representation effect — and §4.3.1 shows an ITT-only family *would* have claimed on 019.
- **The suite-size channel alone cannot produce a Tier C claim.** It rejects on 98.6–99.8 % of unadjusted per-protocol members; unanimity collapses it to **0.000**. An unadjusted-per-protocol-only registration would have called this a representation effect — and that is exactly the member on which 019 rejects.
- **Realised size under a global null is 0.002**, far under the ≤ 0.025 bound of §4.2.5.

This is also the demonstration panel #4's second horn asks for: the difference must be present **both** as a total effect and holding suite size fixed, and the guarantee is 0.000, not an assertion.

#### 4.3.4 Power, and what unanimity costs

Same simulation, 1,000 replicates per cell; IU rejection rate.

**Under equal authoring validity (0.80 in both arms):**

| θ (extra classes for arm A) | group-fraction shift | N=60 | N=120 | N=200 |
|---|---|---|---|---|
| 2 | 0.061 | 0.129 | 0.236 | 0.315 |
| 4 | 0.121 | 0.368 | 0.610 | 0.836 |
| 6 | 0.182 | 0.578 | 0.860 | 0.976 |
| 8 | 0.242 | 0.720 | 0.956 | 0.996 |

**Under 019's observed authoring-validity gap (A 0.895 / C 0.718):**

| θ | N=40 | N=60 | N=80 |
|---|---|---|---|
| 1 | 0.127 | 0.246 | 0.356 |
| 2 | 0.581 | **0.797** | 0.918 |
| 3 | 0.821 | **0.955** | 0.985 |
| 4 | 0.908 | 0.987 | 1.000 |

Four consequences the preregistration must **state**, not discover:

1. **Which member binds depends on the regime.** Under equal validity the ITT members bind (θ = 3: PP members 0.999–1.000, ITT 0.251–0.351, Tier C 0.248). Under 019's gap the ITT members become the *easiest* — they reject two-thirds of the time under a null — and the per-protocol members bind. The earlier draft's "the binding members are always F1/F2" is wrong in both directions.
2. **Power under the gap is partly spurious and must be labelled so.** Tier C's 0.797 at θ = 2, N = 60 is a conjunction in which six of eighteen members are near-automatically satisfied by a channel that is **not** the construct. The honest reading is that in that regime Tier C is effectively a twelve-member test on the per-protocol members — and the *size* under that same gap is still 0.001, because those twelve hold it.
3. **The honest headline for N.** At N = 60/arm with all apparatus repairs, Tier C is 80 %-powered against a coverage effect of roughly **2 classes if 019's validity gap persists** and roughly **9 classes (θ ≈ 0.27 in group-fraction units) if it does not**. **020 cannot know in advance which regime it is in.** v1's "N = 60 buys a group-level MDE of 0.028–0.032" is **withdrawn**: that was one member's MDE on the narrower population, and no confirmatory sentence in v2 reads one member.
4. **Against 019's own observed configuration, Tier C is unpowered at every N.** M9 and M15 are negative point estimates with the family's other sixteen positive; if that configuration is the truth, P(all eighteen agree in sign) → 0 as N grows. The correct planning statement is *"if the truth resembles 019, Tier C returns INDETERMINATE with probability → 1"*, and 020 must be willing to publish that.

### 4.4 What Tier C can and cannot conclude

**When the family is unanimous (claim).** R1 asserts: *within the registered fragment, under single-shot authorship, arm A's suites cover a different fraction of the shared witness classes than arm C's — and the difference is present whether or not authoring failures are counted, whether or not suite size is held fixed, whether classes are weighted equally, by mutant multiplicity, or by de-biased native denominators, and whether or not engine-supplied kills are excluded.* That conjunction **is** the claim; it is stronger than any single-member claim and it is the only thing the tier licenses.

Three further ceilings bind any claim:

- The endpoint is **witness-input coverage**, not assertion strength (Fact 1). Whether §1 and the slug must be renamed is **M-18**.
- The effective support is **28 of 33 classes**. Five classes — witnessed by `d8-2m01-low`, `d8-2m01-low-absent`, `d8-70-low`, `d8-low-40-500k01-ins-absent`, `d8-low-89`, each a single gold input — were covered by **no run in either language** across all 88 identity-passing runs. Both arms' floors are displaced downward by a fixed 5/33 = 0.1515 and no member can exceed 28/33. The sixteen mutants they carry (JPS `m-a-008, -012, -046, -057, -059, -063, -067, -092`; Rego `m-b-009, -016, -023, -036, -038, -042, -052, -151`) are published wherever the estimand is defined.
- The endpoint measures pinning **against the shared reference**, not against the policy each suite accompanies (**M-26**).

**When the family splits (no claim).** R1 returns INDETERMINATE-BY-DISAGREEMENT and:

1. **No negation is licensed.** A split is not evidence of no effect.
2. **No member is promoted after the fact.** There is no primary specification; there is a family. The study may not report "on the primary specification the effect was significant."
3. **The split is published as a Tier D finding**, with the arm-blind diagnosis of *which axis carries it*. That diagnosis is informative: a split on the adjustment axis means the difference is mediated by suite size; a split on the population axis means it is carried by authoring validity, not by pinning; a split on the level axis means it is carried by mutant multiplicity. Neither is R1.
4. **The published quantity set is identical in every branch** — eighteen point estimates, eighteen p-values, eighteen per-arm n, eighteen BCa intervals, the raw-L2 continuity ledger with its offset, and the drop-a-pole table. Registered so the outcome cannot change what is reported.

**What Tier C cannot do at all.** It cannot rescue a design whose members answer materially different questions — unanimity across incoherent members is a conjunction of unrelated claims. Criterion (ii) is the only guard, and it is a judgement, not an arithmetic. The maintainer should read the eighteen members as a set and satisfy themselves that a reader who believed all eighteen would believe one thing.

---

## 5. The seven construct rows

### 5.1 They are two classes, not one (verified against source)

- **S1 — five rows, derived-encoding cost.** Re-running `design/gold/check_gold.py::retired_x1` over `gold/GOLD.json` selects exactly **five** rows: `x1r-low-spend-unreadable-40`, `x1r-low-spend-unreadable-69`, `x1r-country-unreadable-100k`, `x1r-country-unreadable-40`, `x1r-country-unreadable-69` — matching `verification/V7-COMPLETENESS.md` §3.4 assertion A6. Mechanism V8-09: expressing it costs a derived region lemma the prose never states; arms B/C need no such lemma. Signed `B/C-favorable`. **A cost row, not a fragment boundary.**
- **S2 — two rows, reason accumulation.** `p1-absent-escalation-region` and `p1-unreported-escalation-region` both return **false** under `retired_x1`, so they are outside S1's region and cannot require the region lemma. Their arm-A signature is exact and unanimous over the 36 artifact-bearing runs: expected `unresolved:[missing-required-evidence]`, got `unresolved:[exception-escalation,missing-required-evidence]` on **35/35** failing runs; expected `unresolved:[unknown]`, got `unresolved:[exception-escalation,unknown]` on **35/35**. That is V8-10's inert O3 conjunct, whose guarding conjunct **is** stated in the prose.

### 5.2 The three options, costed

**(a) State the region lemma in the prose. Rejected as a repair.** It buys at most five of the seven; it is untested (stating the *answer* does not supply the *encoding* — arm A must still suppress D8 inside the region, which the reference does with four members); it re-derives V7 wholesale including §4.4's *pinch 2* proof; it edits the byte-identical shared header and therefore the treatment in all three arms, deleting a `B/C-favorable` ledger row by fiat; and it moves `harness/leak_tokens.py`'s R1/R2/R3 derivation. Above all it changes the estimand to *"does prose completeness help?"* — a different study.

**(b) Keep all 117 rows; split the seven into two mechanically-defined strata, published per arm, outside any gate.** *Recommended.* `design/BRIEF.md` §4.3 already registers an ambiguity stratum with the three properties needed: mechanical membership, frozen before any pilot artifact is opened, E1 published both with and without.

> **v1's S1 membership rule is withdrawn: it selects the empty set** (panel #20, confirmed here against `design/reference/refA/pack.json` — **all 13 rules and all 14 exceptions carry a leading clause id in their `description`**, including every member v1 named: `r-o1-wide-low` and `r-o1-wide-spend` open `"O1 + D8 - …"`, `x-o1-suppress-d8-low` and `x-o1-suppress-d8-spend` open `"O1 - …"`). The property v1 was reaching for — that these four are derived *consequences* rather than transcriptions — is not decidable from `pack.json` bytes.

**Registered instead, decidable from committed bytes today:** S1's membership is `check_gold.py::retired_x1` — committed, V7-certified, verified to select exactly the five `x1r-*` rows. S2's membership is *the arm-A reference's answer depends on an exception conjunct entailed by another clause's guard* — the predicate `design/mutants/ADEQUACY.md` already mechanizes on the Rego side as `entailed-guard`. **This one still requires the predicate to be lifted to the JPS side and its extension published before freeze**; until that lands, S2 is *declared*, not mechanical, and v2 says so.

**Costs, stated.** Nothing in the frozen artifact chain moves: gold bytes untouched, so the mutant corpora, witness tables, the pairing (**33 shared classes / 69 paired JPS / 62 paired Rego**, re-derived from the two manifests by identical sorted witness set and reproducing `RESULTS.json.pairing` exactly), `check_gold.py`'s census, V7's six assertions and §4.4, and E5's stimulus all stand. What narrows is the E1 *descriptive* support, to 110 rows, on grounds known in advance to favour one arm's profile — so **both strata rates are published per arm with E1's prominence**, and §11 says plainly that the support was chosen on a known arm asymmetry. It is necessary, not sufficient: perfect-on-110 is **A 3/36, B 8/30, C 14/30**, so a 0.60 floor fires again on the 110-row support exactly as it did on 117.

**(c) Delete the seven from gold. Rejected, cost re-derived.** Nine JPS mutants go empty-witness (`m-a-040, -042, -044, -084, -123, -126, -127, -130, -132`; **zero Rego**), reopening the adequacy gate; `check_gold.py` errors by design; V7 §4.4's proof is destroyed. And **the primary's denominator moves**: although 0 shared classes touch any of the seven, pairing is by witness-set *identity*, so deleting rows **coarsens** the equivalence — counterfactually **38 shared classes / 78 paired JPS / 71 paired Rego**. Pairing census, both cuts and the denominator would all have to be re-derived.

> **M-3 (revised) — keep the seven in gold, split into S1 (`retired_x1`, committed and certified) and S2 (`entailed-guard`, to be lifted to the JPS side and published before freeze), scored and published per arm, outside every gate.** Sub-decision: **if S2's predicate cannot be lifted before freeze, S2 is dropped and the two `p1-*` rows stay in the undifferentiated support** — a declared stratum must not be registered as a mechanical one.
>
> **M-4 — does 020 repair the stimulus? Recommendation: no.** The lemma cost is the finding; repairing it silently changes the estimand. If the maintainer wants it, it is a separate registered study with its own pilot.

---

## 6. Calibration under registered conditions

### 6.1 019's pilot measured a different population — and the differences are five, not three

`design/pilot/pilot_run.py` calls codex with **no `env=`**, no `-m`, no `--ignore-user-config` — inheriting the operator's `$HOME`, `~/.codex/config.toml` and `$HOME/.agents` skills, none of which are recorded. The same file passes `env=clean_env(workdir)` to *every* jpack and OPA call: **the engines were isolated; the model call was not.** `harness/authoring_call.sh` states the channel explicitly — *"skills load from `$HOME/.agents` and DO reach the model — `--ignore-user-config` alone does not stop them."*

```
pilot      (design/pilot/pilot_run.py:69-76, and each pilot CALL.json.argv):
  codex exec --skip-git-repo-check --sandbox read-only --color never -c mcp_servers={} -
registered (arms/A/authoring/run-001/CALL.json.argv):
  codex exec --ignore-user-config -m gpt-5.6-sol --sandbox workspace-write -c mcp_servers={} <prompt bytes>
```

Five recorded differences: `--ignore-user-config` (absent → present); `-m <model>` (absent → pinned); sandbox (**read-only → workspace-write**); `--skip-git-repo-check`/`--color never` (present → absent); environment isolation (none → fresh `$HOME`, `env -i`, isolated `CODEX_HOME`, recorded `isolatedHomeInventory`). **The sandbox difference is the one most directly tied to the test-row gap** — a read-only sandbox cannot write or execute the suite it is drafting — and v1 omitted it while citing that very gap as evidence.

**The observables, one admission cohort each** (panel #25; v1 mixed cohorts inside single rows):

| Observable | Pilot | Registered | Ratio |
|---|---|---|---|
| Arm-A duration, **calls that completed** | 1559.081 / 1580.262 / **1660.184** / 1707.263 / 2407.773 s | median **199 s**, max 273 s | 8.3× |
| Arm-B duration, same cohort | 581.062 / 649.560 / **803.042** / 833.178 / 1101.012 s | median **75 s** | 10.7× |
| Arm-C duration, same cohort | 443.417 / 476.343 / **624.114** / 889.933 / 1054.051 s | median **75 s** | 8.3× |
| Completion bytes, same cohort | A **53,931** / B **18,173** / C **18,403** | A **36,155** / B **10,935** / C **9,789** | 0.67 / 0.60 / 0.53 |
| Arm-A test rows | 35–49 per run (`design/pilots/…/NOTE.md`) | `caseCount` 16–25, median 21 | 1.7–2.3× |

Three corrections to figures both v1 and the v2 drafts carried. Registered medians over **all** `CALL.json` records are 199 / 74 / 72.5 s; the 20 records with `exitStatus: 126` carry `durationSeconds: null` and 19 of the 20 have `startedAt == endedAt` (B 10, C 10 — **not** B 10 / C 9). **On executed calls only the triple is 199 / 75 / 75 s**, so the registered condition's slot-triple is **349 s = 5.82 min**; the draft's "199 / 75 / 74 → 348 s" does not reproduce for arm C. And v1's pilot triple "1660 + 818 + 757" mixes arm A's completed-only median with arms B/C's all-six medians (which include a censored 900 s timeout each); on the completed cohort throughout it is **1660.184 + 803.042 + 624.114 = 3087.34 s = 51.46 min**, i.e. **8.85×** the registered triple.

The sharpest tell stands: a condition where **every** arm-A call exceeded 900 s cannot be the condition where **no** arm-A call reached 273 s. Duration fell ~8–11× while completion bytes fell ~1.5×, which points at **reasoning budget**, not output volume — and `harness/PINS.json` pins model, CLI version and binary digest while containing **no reasoning-effort member**. The mechanism is a tight inference from converging observables, **not a measurement**: the pilot's `CALL.json` carries 14 fields (`argv, arm, completionBytes, completionSha256, durationSeconds, endedAt, exitCode, harness, promptBytes, promptFile, promptSha256, slot, startedAt, timedOut`) — no `model`, no `binarySha256`, no `cli` — and **no `session.jsonl` exists on the pilot side at all**. Its condition is unrecoverable, and service-side drift over 2026-08-15 → 2026-08-20/21 cannot be excluded for the same reason.

**Three eliminations.**
- **Prompt bytes are not the cause.** `sha256sum arms/{A,B,C}/PROMPT.txt` equals `design/pilots/…/prompt-{A,B,C}.txt` — three matched pairs.
- **N is not the cause.** Under the registered per-arm perfect rates, P(pilot 5/5) is **4.72 × 10⁻⁴** (B, 8/37) and **5.96 × 10⁻³** (C, 14/39). For arm A the registered rate is **0/38**, giving P = 0; v1's "≤ 3 × 10⁻⁶" is `(3/38)⁵`, the **rule-of-three 95 % upper bound substituted silently** (panel #34) — and a bound-plugged probability is not a p-value. The pilot did not under-sample; it sampled a different population.
- **Gold growth is not the cause.** The pilot scored 76 rows (`goldVersion: "0-draft"`); the registered suite is 117. Recovering the 76-row suite from `git show a5bb49f:…/design/gold/gold.json`: the 76 ids are a **strict subset** of the 117 and **not one shared row's expected answer changed**. Restricting every registered run to those 76 rows gives perfect counts **A 0/36, B 8/30, C 14/30** — identical to the all-117 counts in every arm. Gold's growth explains part of arm A's *depth* of failure and **none** of its existence.

### 6.2 An independent second defect: 5/5 never licensed 0.60

`PREREGISTRATION.md` §5 justifies the E1 floor with *"Expected at ceiling in every arm (pilot 15/15)"*. 15/15 is the **pooled** figure; the floor is applied **per arm**, where the evidence was 5/5, whose exact one-sided 95 % Clopper–Pearson lower bound is **0.549 — below the 0.60 it was cited to support.**

| n | clean sweep | one miss | two misses |
|---|---|---|---|
| 5 | **0.549** | 0.343 | 0.189 |
| 8 | 0.688 | 0.529 | 0.400 |
| 10 | 0.741 | 0.606 | 0.493 |
| **12** | **0.779** | **0.661** | 0.562 |
| 15 | 0.819 | 0.721 | 0.637 |

Two independent calibration errors, either sufficient alone to produce a `control-gate-failed` attempt.

### 6.3 Registered (proposed): the calibration protocol C1–C5

**C1 — one driver, and the pilot's pin state registered as a difference.** `design/pilot/pilot_run.py` is **deleted, not ported**. The pre-freeze pilot runs through `harness/authoring_call.sh` and `harness/batch.py` under a `--calibration` mode. v1 claimed the pilot differs from the primary batch "in exactly three registered ways"; that was false, and the fourth is load-bearing (panel #9): `authoring_call.sh:203` refuses while `codex.model` is null, and `registeredLabelRule` lists `codex.model (model)` among its eighteen freeze-set members — so a pilot that must run *before* the pin exists cannot run at all.

The cure is half-built in 019: `PINS.json`'s `codex` block already carries `"resolvedAtDesignTime": true`, and `registeredLabelRule` already states that *"a design-time resolved toolchain digest is checked whether or not the freeze has happened."* v2 registers `codex.model` and the new `codex.reasoningEffort` as **design-time-resolved pins, not freeze pins**, restates `registeredLabelRule` with the new member and its null-⇒-PILOT test, **moves `registeredLabelRule` out of §7's "ported with no design change" list**, and drives the change in `harness/tests/test_pins.py` pin by pin as that rule already requires. **The registered differences are four:** output under `calibration/<label>/`, the pilot slot count, `citable: false`, and the pin state.

> **The residue panel #9's cure leaves open, and #9 is therefore not closed.** The same rule says design-time-resolved pins are checked *whether or not the freeze has happened*, and `authoring_call.sh:203` refuses on a null model **regardless of label**. The **pre-pilot effort sweep** (§6.4) exists precisely to *choose* the effort value, so it must run before that value exists. Making `codex.reasoningEffort` design-time-resolved therefore either refuses the sweep or leaves the effort unenforced during it. **M-25** decides the sweep's pin state; the pilot's is not enough.

Freeze-gate consequence, folded in from day one: 019's `DEVIATIONS.md` D-2 records that `manifest_problems()` refused any tree containing prior authoring. 020's freeze gates must **permit and require** a `calibration/` subtree at freeze while still refusing any `results/primary-attempt-*` — written into the gate *and its test* before the first pilot call, or the pilot becomes un-runnable at freeze time and gets moved back outside the harness, which is the 019 failure exactly.

**C2 — pin the compute condition, bind it, and register what the binding can and cannot prove.** `PINS.json` gains `codex.reasoningEffort` beside `model` / `version` / `binarySha256`; the wrapper passes it explicitly (resolve the exact flag empirically at pin time, as `design/BRIEF.md` §4.1 already requires for OPA); `CALL.json` stamps it.

v1 proposed extending `transcript_check.py` gate 5 to the effort field. **There is no witness to extend it to** (panel #10, verified): `arms/A/authoring/run-001/session.jsonl` contains exactly one `turn_context` record, whose payload carries `turn_id, cwd, workspace_roots, current_date, timezone, approval_policy, approvals_reviewer, sandbox_policy, permission_profile, …, model, …` — **no effort member**. The only occurrence anywhere in the transcript is `collaboration_mode.settings.reasoning_effort: null`, an override slot. `transcript_check.py:603-608` is `named = {context.get("model") for context in contexts if "model" in context}` / `if named and named != {model}`: pointed at a present-but-null field it yields `{None} != {"high"}` and refuses **every** call; pointed at an absent field it never fires.

**Registered instead:** a **witness-resolution step at pin time**, run before the sweep, which sets the flag and inspects the resulting `session.jsonl` for a non-null member naming the effort. If one exists, gate 5 is extended to it with the same `turn-context-mismatch` reason tag and the same **apparatus-side** classification. **If none exists, the pin is recorded as a `CALL.json` self-report and registered as such** — the preregistration states in terms that the effort condition is *asserted by the wrapper and not independently witnessed*, and `reasoning_output_tokens` (medians **A 2067.5** over 48 runs / **B 502.5** over 38 / **C 696** over 39 — the draft's "703.5 over 38" for arm C does not reproduce) is registered as the **only** transcript-side observable that varies with effort, entering C4 as a band rather than an equality. A pin nobody can check is a recorded intention; v2 calls it that. **M-24.**

**C3 — derive the floor, do not choose it, and show it has power.** House precedent is SCAFFOLD item G3: `leak_tokens.py` derives the leak screen mechanically *and then proves the derived list has power*. Applied here: (i) a committed `calibration/derive_floor.py`, sealed before the pilot runs, emitting any threshold from the pilot's own per-arm counts by an exact CP rule, with **no human number entering**; (ii) a **minimum viable value declared in advance**, below which the study does not freeze; (iii) a **degradation control**, retargeted below.

**C3(iii) — v1's recommended degradation control provably cannot fail the gate it certifies** (panel #8, confirmed by re-derivation). `refA/PACK-CHANGE-001.md` records 72 of 236,196 cells changed, all inside the retired-X1 predicate, and `retired_x1` selects exactly 5 of 117 gold rows. Re-scoring every artifact-bearing run's `goldFailures` against repair-removed gold:

| arm | min misses, true gold | min misses, repair-removed | agreement | existence gate (≥ 0.95 ⇒ ≤ 5 misses) |
|---|---|---|---|---|
| A | 2 | **2** | 0.9829 | **holds** |
| B | 0 | **5** | 0.9573 | **holds** |
| C | 0 | **5** | 0.9573 | **holds** |

The gate the control "must fail" **holds in all three arms**, and arm A is *unchanged* because the degradation makes arm A's dominant failure mode correct — the control is **anti-correlated** with the gate in the arm the gate is least able to protect. And the reference is not in the stimulus: a reference-only rule id appears 5 times in `reference/REFERENCE-A.md` and 0 times in `arms/A/PROMPT.txt`, so removing the repair regresses *gold*, not the prose/prompt-assembly channel the gate names — and it needs no model calls, so v1 §8's 36-call budget line bought a re-scoring (panel #36).

**Registered: the degradation acts on the stimulus** — the shared prose header, the prompt assembly, or the naming appendix — the common-mode threat the gate actually claims to detect; the preregistration publishes the computed per-arm miss-count shift the degradation induces **before** the pilot runs; and it is budgeted as **authoring calls** (§8).

**C3(iv) — the certification arithmetic, and what it kills.** The existence gate is a **max statistic**: it fires (refuses) iff *no* admitted run clears, so P(fire) = (1 − p)ⁿ in the per-run clear rate p, and its stringency is monotone in realised n, which differs by arm (34 / 26 / 28 in 019). At arm A's observed undegraded clear rate 3/36 = 0.0833:

| per-run clear rate | n=12 | n=34 | n=43 | n=50 | n=60 |
|---|---|---|---|---|---|
| 0.0833 (019 arm A, **undegraded**) | 0.352 | **0.052** | **0.024** | **0.013** | **0.005** |
| 0.040 (2× degradation) | 0.613 | 0.250 | 0.173 | 0.130 | 0.086 |
| 0.020 (4×) | 0.785 | 0.503 | 0.419 | 0.364 | 0.298 |
| 0.010 (8×) | 0.886 | 0.711 | 0.649 | 0.605 | 0.547 |

Two facts v1 never computed. **(a)** The gate spuriously refuses arm A with probability 1.3–6.1 % at 019-scale N even with a perfect stimulus. **(b)** A degradation control at 12/arm fires at 61–79 % against degradations the registered gate at 43–60/arm catches only 9–36 % of the time — so "the degradation control must fail the gate" establishes the *opposite* of what it is invoked for unless the control runs at batch N (panel #13). And running it at batch N does not rescue the gate: to certify **P(fire) ≥ 0.95** at N = 50 the degraded per-run clear rate must be ≤ **0.001025**, and bounding a rate that low by observation needs, by rule of three, **~2,926 degraded runs** (~162 h at 199 s/call); at N = 60, ~3,511.

> **The existence gate cannot be empirically certified at any affordable n.** That is not a criticism of the control; it is a property of a max statistic over a stochastic authoring process.

The program's standing *mutation-check every safeguard test* lesson says a safeguard that cannot be shown to fail must be labelled as one. **The common-mode threat the existence gate names is a byte threat, and byte threats are caught deterministically.** 019 already pins `arms.<arm>.promptSha256`, the policy prose, the golden context and the reference digests, and `references-reproduce-gold` held 117/117 on both references. Those gates fire with probability 1 against corrupted prose, broken prompt assembly and a wrong naming appendix. The existence gate adds a 1.3–6.1 % spurious-refusal risk and no certified detection power on top of them. **M-23.**

**C4 — the transfer gate, at decision row 1 (`pipeline-invalid`), two-sided, with derived bands.** A condition mismatch is an apparatus fact, not evidence about the arms, and 019's `control-gate-failed: e1-floor` verdict actively misleads on this — it reads as *the arms are bad at the task*.

v1's five tolerance bands were undefended constants (panel #26). v2 derives them from the retained **within-condition** dispersion: bootstrapping medians-of-12 from the registered batch (4,000 resamples, seed 3, executed calls only) gives 2.5–97.5 % ratio spans of **[0.930, 1.083] / [0.960, 1.080] / [0.920, 1.067]** for duration (A/B/C), **[0.926, 1.106] / [0.917, 1.059] / [0.941, 1.043]** for completion bytes, and **[0.857, 1.169] / [0.846, 1.193] / [0.727, 1.177]** for `reasoning_output_tokens`. The noise floor is ±10 % for duration and bytes and ±18–27 % for reasoning tokens; v1's [0.5×, 2.0×] and [0.6×, 1.7×] would have passed a genuine 1.9× condition shift.

| Observable | Source | Band | Power against the 019 mismatch |
|---|---|---|---|
| model, CLI version, binary sha256, reasoning effort | `CALL.json`; `session.jsonl` `turn_context` where a witness exists (C2) | exact equality | **none** — the pilot `CALL.json` records none of them |
| sandbox policy, `codexHomeIsolated`, `environmentScrubbed`, isolation inventory | `CALL.json` | exact equality | **none** — not recorded pilot-side; **descriptive** for any 019 comparison, gating for 020's own pilot |
| per-arm median call duration | `CALL.json` `startedAt`/`endedAt`, executed calls only | [0.80×, 1.25×] | **fires**: 8.3–10.7× |
| per-arm median completion bytes | `completion.txt`, same cohort | [0.80×, 1.25×] | **fires**: 0.53–0.67× |
| per-arm median `reasoning_output_tokens` | `session.jsonl` | [0.65×, 1.55×] | **cannot be evaluated against 019** (no pilot `session.jsonl`); registered for 020 |

Bands are ~2.5× the measured within-condition span for the two rows with demonstrated power and ~2.7× for the reasoning-token row, set **before** the pilot from this dispersion, never after seeing the pilot's numbers. Applied to 019, the gate fires on duration and bytes in every arm.

**C4 is two-sided** (panel #21). v1 registered the pilot as the reference and could only invalidate the batch — which, at the recommended N, discards 180 isolated calls on the authority of a 36-call reference whose own condition §6.1 shows was the corrupted side. **Registered adjudication: if every exact-equality row holds and only band rows differ, the pilot is suspect and the outcome is `calibration-invalid`, requiring a re-pilot under C5; if any exact-equality row differs, the batch is suspect and the outcome is `pipeline-invalid`.** Both outcomes are recorded with the rows that produced them.

**C5 — one pilot, sealed, append-only re-pilot rule.** The pilot runs once; label, N and output digest go into `PINS.json` before the primary attempt. A second pilot requires a `DEVIATIONS.md` entry naming the reason, and then **the derived threshold is the maximum over all pilots** and **the transfer bands are the tightest over all pilots**, with every pilot's rates published side by side. Re-piloting is monotone in strictness.

### 6.4 Pinning effort undermines the dispersion calibration

If 020 pins a **higher** reasoning effort, 019's batch is no longer condition-matched and §4.3.2's dispersion figures become a **prior, not a calibration** — the within-arm SDs were measured under the *registered* condition. **Adjudication:** pin the effort explicitly, and **re-derive the dispersion from the pilot at the pinned effort**; use 019's SDs only as a fallback prior and say so in the preregistration.

One correction to v1's framing (panel #38): **"recover pilot-like behaviour" is withdrawn as an objective.** The pilot's defining property was that isolation was absent; C1 alone removes four of the five recorded invocation differences without any effort pin, and targeting a condition characterised by missing isolation is not a coherent goal. The **pre-pilot effort sweep** stands — n = 3/arm across two or three settings, published in full — because the value is the one thing the retained evidence cannot decide; but it is a sweep over a *registered* apparatus, not an attempt to reproduce an unrecoverable one.

**The sweep must be priced at the durations it is sweeping** (panel #24). On one admission cohort throughout, the registered slot-triple is **349 s = 5.82 min** and the pilot-like triple is **3087 s = 51.46 min**, so a swept setting at pilot-like durations costs **8.85×** its registered-condition line. **M-8 and M-20 must be decided together**, and §8 prints a range across the branches with a total call count and a per-setting abort rule, not one column plus a caveat.

> **M-8 — pin reasoning effort, and at what value? Recommendation: pin it**; choose the value from the published pre-pilot sweep, priced per setting at that setting's hypothesised duration. **The one decision the retained evidence cannot make.**
>
> **M-9 (revised) — calibration protocol C1–C5 as registered machinery**, including the minimum viable derived value; whether a below-minimum pilot **aborts** (recommended) or **descopes**; and — replacing v1's recommendation, which panel #8 disproved — **a stimulus-side degradation** (shared prose header / prompt assembly / naming appendix), with its per-arm computed miss-count shift published before the pilot runs, budgeted as authoring calls, and run at the batch's realised n **or** its arithmetic gap to batch n stated explicitly per C3(iv).

---

## 7. What carries over unchanged, and what does not

Ported by digest, no design change: gold bytes and `check_gold.py`'s census; both reference packs and `references-reproduce-gold` (117/117); the mutant corpora and `ADEQUACY.md`; the witness tables and the pairing rule; `leak_tokens.py`; the transcript gates other than gate 5; the identity control; `DEVIATIONS.md` machinery.

**Five rows leave the "unchanged" list, each with a day-one work item:**

- **`registeredLabelRule`** — restated with `codex.reasoningEffort` and the null-⇒-PILOT test (§6.3 C1), driven in `test_pins.py` pin by pin.
- **The batch schedule.** `batch.py:308-317` hard-codes `SEQUENCES = 6`, `ROUNDS = 50`, `RUNS_PER_ARM = 50`, `REGISTERED_SLOTS = 150` and a two-element `TAIL`, and `derive_order()`'s docstring records that the registered floor (1, 1) is the cached answer to a search **at 50 rounds**. At 60 rounds there is no tail and position spread 0 becomes attainable, so `test_schedule.py`'s assertion is wrong by construction. Re-derive the order, publish the new attained floor, re-pin `batch.order` / `batch.n` / `batch.slots` (panel #28).
- **The reviewer mutant set.** `PINS.json` `reviewerMutantSet.note` says "first executed at the primary attempt," and `RESULTS.json.reviewerSet.perArm` publishes the outcome per run (`rm-jps-01`/`rm-jps-02` survive every listed arm-A run; `rm-jps-03` is killed in every one). The set is **spent**. 020 registers a **fresh sealed reviewer set**; 019's is kept only as a published comparison (panel #29).
- **The registry-digest coupling (D-1/D-3).** `population.A.apparatusCodes` records `registry-mismatch: 9`, and the stale digest `sha256:36912ee3…` appears on **9 arm-A, 10 arm-B and 10 arm-C** `CALL.json` files — 29 of 149 — but **all 20 B/C ones carry `exitStatus: 126`** (19 of the 20 with `startedAt == endedAt`), so only arm A's nine survived to reach the scorer's registry check. **Any post-freeze registry re-pin invalidates every slot recorded before it**, so either the scorer's registry check reads a semantic subset rather than the raw file digest, or a repair halts and restarts rather than resumes (panel #22).
- **D-4 is corrected, not carried.** `PREREGISTRATION.md` line 319 registers *"Registered batch window: three consecutive UTC calendar days"* and `PINS.json` `batch.window` says the same, so D-4 filed a deviation against a rule 019 did not have. Restated as **"one registered statement of the window, with a test that no other document states a different one"**; the surviving one-day sentences are duplicated constants in the pilot notes (panel #27).
- **D-1's smoke** is restated as *"a real exec at the registered prompt bytes, stand-in binary permitted"* — D-1's failure was `/usr/bin/env: Argument list too long` at `exec`, which a stand-in binary reproduces exactly — with D-2's stand-in-**study** smoke preserved, and whatever real calls the smoke needs added to §8's table (panel #39).
- **`DEVIATIONS.md` moves out of the freeze set** (carried from Study 018's lesson).

---

## 8. Cost, and what N buys

Priced on one admission cohort — every executed call at the registered 2700 s ceiling. Registered slot-triple **349 s = 5.82 min**; pilot-like slot-triple **3087 s = 51.46 min** (8.85×).

| line | calls | wall clock, registered condition | wall clock, pilot-like durations |
|---|---|---|---|
| pre-pilot effort sweep, 3 settings × 3/arm | 27 | 0.29 h | 2.57 h |
| pilot, 12/arm (C1–C5) | 36 | 1.16 h | 10.29 h |
| D-1/D-2 smoke (real exec, stand-in binary permitted) | ~6 | ~0.06 h | ~0.51 h |
| primary batch, N = 60/arm | 180 | **5.82 h** | **51.46 h (2.14 d)** |
| stimulus degradation control, if M-23 = (b) or (c), at batch n | +180 | +5.82 h | +51.46 h |
| **total under M-23 = (a) (recommended)** | **~249** | **~7.3 h** | **~64.8 h** |

The sweep is the branch point: a swept setting priced at pilot-like durations costs 8.85× its registered line, so §8 must be read jointly with M-8 and M-20, with a **per-setting per-call ceiling and an abort rule**.

**Disk and retention, registered** (panel #30): a free-space precondition checked at driver start **and before each slot**; a retention rule for the scratch parent (the wrapper makes **two** directories per slot); and a total budget — 019's 149 retained slots occupy **86 MB** in-tree (arm-A slots ~660 KB, arm-B/C ~20 KB), so ~249 slots project to roughly 140–160 MB plus scratch.

**The realised-n arithmetic is shown, not asserted** (panel #32): at N = 60 with `slot-shape` pre-paid, arm A's admitted rate is 1 − (9 + 1)/50 = 0.80 → 48 admitted → 48 × 0.895 ≈ **43** scoreable; arm B 1 − 2/50 = 0.96 → 57.6 → × 0.703 ≈ **40**; arm C 1.00 → 60 → × 0.718 ≈ **43**. With `registry-mismatch` also repaired (§7's day-one item), arm A is 0.98 → 58.8 → ≈ **53**. **Without that repair arm A projects to ~43, not 50**, and §4.3.2's "+ registry cure" column does not apply.

---

## 9. Where this brief ruled, and on what evidence

v1's §9 ruling row asserting that the arm-labelled quantities do not re-derive is **withdrawn** (§2.2). The remaining contested points, with the evidence that settled each:

| # | Contest | Ruling |
|---|---|---|
| R-1 | Do 019's arm-labelled E4 figures re-derive? | **Yes**, on the artifact-bearing cohort, to five decimals (A 0.60628 / B 0.59032 / C 0.61613). v1's contrary claim compared cohorts without naming either. |
| R-2 | Is panel #1's "+0.0065 (artifact-bearing)" reproducible? | **Yes: +0.00649, p = 0.8601**, once the empty-survivor trap is corrected. The v2 draft's proposal to withdraw it, and its replacement figures +0.06205 / +0.10051, are themselves the uncorrected values and are withdrawn. |
| R-3 | What is the empty-survivor trap worth? | **0.0526 on the ITT group contrast (38 %), and correcting it *lowers* A−C** (+0.19112 → +0.13849). The draft's "+0.1161 → +0.1385, 19 %" conflated it with the drop-vs-zero-fill of six other runs and had the sign backwards. |
| R-4 | Is the native mutant level removed from the family? | **No.** Removal was argued from arm-labelled contrasts and is anti-conservative under IU. It enters **de-biased** (L2c) by criterion (iii); the raw form is a published Tier D continuity row with its offset. |
| R-5 | Is the engine-supplied-kill column a family axis? | **Yes.** Refusing it was argued from 019's arm-labelled contrasts. It is one-sided in the corpus (12/69 JPS, 0/62 Rego; 33 → 29 classes), which is an arm-blind reason it can matter. |
| R-6 | Which permutation scheme for the adjusted members? | **Whole-record permutation**, exactness limited to the strong sharp null and said so. **Freedman–Lane is not registered**; it does not achieve exactness for the adjusted null either, and two schemes in one document was the defect. |
| R-7 | Which verdict vocabulary? | **CLAIM / INDETERMINATE-BY-DISAGREEMENT.** "UNSUPPORTED" is not used; it reads as evidence of no effect. |
| R-8 | Is the `gall == gany` equivalence 114/114? | **No — 88 of 88.** Only 90 runs carry a survivor vector and two of those are degenerate. Both drafts and the panel inherited 114 uncritically. |
| R-9 | Does any attainability machinery replace v1's gate? | **No.** No τ, no cut, no probe, no refusal branch, anywhere — including Tier D. |
| R-10 | Registered executed-call duration triple? | **199 / 75 / 75 s = 349 s.** The draft's 199 / 75 / 74 does not reproduce for arm C. |
| R-11 | Is panel #15 fixed by symmetrisation? | **No.** L3 fixes weights, not the all-rule attainability asymmetry. V8-22 stays live and a group-size-imbalance ledger row is added. |
| R-12 | Do the eighteen members disagree on 019 for a robust reason? | **Yes for eight of nine poles; no for one.** Dropping the per-protocol pole yields a CLAIM. That exception is printed, and §4.3.3 shows why that pole is the one that must never be dropped. |

---

## 10. Tier D — the descriptive battery

**Standing clause on every table in this section, carried verbatim from 019 §5's R1-15 discipline: *descriptive; published as an interpretation quantity that no decision reads.*** All of it is published whatever Tier C returns.

### 10.1 The full estimand grid

Per-arm means, corrected scorer, 019 as the worked example and the power-planning input:

| analysis set | level | adjustment | A | B | C |
|---|---|---|---|---|---|
| identity-passing (34/26/28) | group (33) | none | 0.61765 | 0.59907 | 0.57684 |
| identity-passing | group | ANCOVA, b = +0.02332 | 0.6106 | 0.5893 | 0.5945 |
| identity-passing | symmetrised mutant | none | 0.67333 | 0.66148 | 0.63877 |
| identity-passing | native mutant | none | 0.64194 | 0.68114 | 0.66014 |
| identity-passing | native mutant | ANCOVA, b = +0.03300 | 0.6320 | 0.6673 | 0.6852 |
| artifact-bearing complete-case (36/26/28) | group | none | **0.58333** | 0.59907 | 0.57684 |
| artifact-bearing, all (36/30/30) | native mutant | none | 0.60628 | 0.59032 | 0.61613 |
| §1a admitted ITT-114 (38/37/39) | group | none | **0.55263** | 0.42097 | 0.41414 |
| §1a admitted ITT-114 | symmetrised mutant | none | 0.60245 | 0.46482 | 0.45860 |
| §1a admitted ITT-114 | native mutant | none | 0.57437 | 0.47864 | 0.47395 |

*(The three group-level arm-A entries in bold are the cells the v2 draft printed at their uncorrected values 0.63889 and 0.60526.)* Contrasts and p-values for every cell are in §4.3.1 and the single-choice ledger. Both slope-pooling conventions are published: three-arm pooled (above) and contrast-pairwise (identity-passing group: adjusted A−C = +0.0185 rather than +0.0161; no direction changes).

The **artifact-bearing complete-case** set is published with its composition: it is the per-protocol set plus exactly the two arm-A empty-survivor runs (`run-025`, `run-046`), which is why it is not a third population pole. Its group-level contrasts, corrected: unadjusted **+0.0065, p = 0.8601**; ANCOVA (b = +0.01942) **−0.0153, p = 0.6233** — a group-level cell that turns **negative** under adjustment, which the draft printed as +0.03366 (A > C).

### 10.2 Dispersion corrections carried forward

The three SD rows the v2 draft got wrong, re-derived: group / artifact-bearing complete-case = **0.11396** (not 0.0888; this is panel #5's 0.1140); native mutant / artifact-bearing complete-case (n = 90) = **0.13012** (0.2047 is the artifact-bearing-*all* n = 96 figure); group / admitted-96 with unscoreable = 0 = **0.17946** (not 0.1656). And **"0.2543 or 0.2486 depending on which runs are zeroed" is not an analysis option** — under the corrected scorer both dispositions give **0.25427**; 0.2486 was a trap artefact. Per-arm group-level SDs, identity-passing: A 0.0602 (34) / B 0.0749 (26) / C 0.0744 (28). ANCOVA imbalance term: `S_xx,within = 355.6`, A−C `caseCount` gap 1.061, inflation factor **1.034** at n = 43 — registered rather than dropped by fiat (panel #31).

### 10.3 `caseCount`, published as a construct quantity rather than adjusted away

Panel #4 is accepted in full: `caseCount` is measured on the authored artifact and is therefore **post-treatment**, and M-7 itself says *"how many cases a representation leads an author to write is part of the construct."* An ANCOVA on it estimates a controlled direct effect, not the total effect §1 asks about.

- Means, identity-passing: **A 20.882 / B 21.000 / C 19.821**; artifact-bearing: A 20.944. Medians 21 / 20.5 / 20; ranges A 16–25, B 16–25, C 16–24. **Balance is registered on means with a stated test and threshold, never on medians.**
- With b = +0.02332 the adjustment moves A−C by 0.02332 × 1.061 = **+0.0247** — 61 % of the unadjusted +0.0408 and 70 % of the n = 60 unadjusted MDE. A bias-sized movement in the batch v1 called balanced.
- **Published:** the mediation decomposition (total effect, the `caseCount` path, the residual direct effect), the per-arm distribution, and the within-arm slope at all three estimand levels.
- **Missing-data rule:** `caseCount` is absent for exactly six admitted runs (B `run-026/027/032/036`, C `run-035/050`, all `unparseable-artifact`; **arm A zero**) — the same six that lack a survivor vector. Registered: `caseCount = 0` for a suite that parses to no cases, per-arm counts published before freeze, complete-case variant published beside it.

> **M-7 (revised) — `caseCount` is a registered family dimension (adjusted and unadjusted both required to agree), a published Tier D construct quantity, and a registered balance check on means. Do not fix suite size in the prompt.**

### 10.4 Corpus-structure publications (the findings 019's row 3 blocked)

- **Pairing:** 33 shared non-degenerate witness classes, 69 paired adequate JPS, 62 paired adequate Rego — reproducing `RESULTS.json.pairing` exactly from the two manifests by identical sorted witness set.
- **Single-witness fractions of the paired subset:** **28 of 69** JPS, **20 of 62** Rego — on the unequal lattices V8-22 names.
- **Union ceilings:** exactly **8 paired mutants per language survive every identity-passing run** (JPS `m-a-008, -012, -046, -057, -059, -063, -067, -092`; Rego `m-b-009, -016, -023, -036, -038, -042, -052, -151`), so union kill is 61/69 and 54/62 and the union **class** ceiling is **28/33 in both languages**.
- **The five classes no run covers, with identities:** `d8-2m01-low`, `d8-2m01-low-absent`, `d8-70-low`, `d8-low-40-500k01-ins-absent`, `d8-low-89` — all single-witness `d8` boundary inputs. **Effective support 28, not 33**, stated wherever the estimand is defined.
- **Coverage distribution, identity-passing (88 runs):** `{12:1, 13:2, 15:1, 16:3, 17:6, 18:8, 19:12, 20:17, 21:21, 22:9, 23:7, 25:1}` — range 12–25, **exactly one run reaches 25**, 38 reach ≥ 21. On the §1a denominator with unscoreable runs at 0 the range is 0–25.
- **Class member-count imbalance:** 20 of 33 classes unequal (13 JPS-heavier, 7 Rego-heavier; extremes `d7-39-100k` 6 vs 3, and `d1-match|d1-match-bare|d1-match-critical|d1-match-o3-region` 1 vs 4). Full table published; group-size imbalance registered as a new V8 ledger row.
- **The any/all rule is not a live choice:** `gall ≠ gany` in **0 of 88** checkable runs, structurally so for identity-passing runs.
- **What the endpoint therefore measures:** greedy hitting-set over the 51 distinct witness inputs reaches 33/33 with **21** gold inputs, against suites of 16–25 cases. Near-deterministic in suite size and input choice; assertions do not enter.
- **Engine-supplied-kill column:** excluded, **12 of 69 paired JPS and 0 of 62 paired Rego** leave; shared classes 33 → **29**, paired totals 57 / 55. "Same denominator, same lattice, same union ceiling" holds under the **included** column only, and every figure in this brief is labelled accordingly.

### 10.5 E1's descriptive battery

The exclusive table of §3, plus: per-run perfect agreement rate; the full row-agreement distribution; the same two on the 110-row support with S1 and S2 named (perfect-on-110: A 3/36, B 8/30, C 14/30); and the E3 taxonomy with `u1-*` and the two `p1-*` region rows as **named categories**. Also the Lee-style trimming bounds of M-17 (trim fraction (0.895 − 0.718)/0.895 = 19.8 %, k = 7 of 34 arm-A runs): A−C bound **[+0.0236, +0.0629]** at L1 and **[+0.0166, +0.0672]** at L3.

---

## 11. What 020 will not be able to show (registered ceilings)

Every §9 ceiling of 019 continues to bind verbatim. These bind further:

1. **The endpoint is witness-input coverage against the shared reference**, not pinning power and not pinning against the accompanying policy (Fact 1; panel #14, #19). Unless M-18/M-26 land, §1 and the slug overstate it.
2. **Effective support is 28 of 33 classes**, and both arms' floors are displaced downward by 5/33 = 0.1515.
3. **Tier C is conservative against a real total effect that runs through suite size.** Requiring the adjusted member to agree means that if the representation effect operates *through* `caseCount` — which panel #4 establishes is part of the construct — Tier C returns INDETERMINATE. That is deliberate; the alternative hands the verdict back to a single contaminated choice. **M-22** asks the maintainer to accept and print it.
4. **Tier C's power depends on a quantity 020 cannot know in advance** (the per-arm authoring-validity rate), and in the regime where it looks powered, six of eighteen members are near-automatically satisfied by a channel that is not the construct.
5. **The reasoning-effort pin may be a recorded intention, not a verified condition** (C2, M-24).
6. **The 019 pilot's compute condition is unrecoverable**, so no transfer gate can be evaluated against it on model, isolation or reasoning-token rows; service-side drift over 2026-08-15 → 2026-08-21 cannot be excluded.
7. **The E1 descriptive support was narrowed to 110 rows on grounds known in advance to favour one arm's profile.** Both strata rates are published per arm with E1's prominence.
8. **The all-rule attainability asymmetry is not repaired** — only the weighting asymmetry is (V8-22 stays live).
9. **L2c's offset is estimated**, on a coverage marginal computed over a post-treatment-selected cohort, with its estimation variance not propagated.
10. **If M-13 lands, `identityPass` changes meaning and every per-protocol member's population changes with it**, so §4.3.2's dispersion figures must be re-derived.

---

## 12. Panel dispositions

**FIXED** = the defect is cured and the section carrying the cure is named. **ACCEPTED-DISCLOSED** = real, not curable in 020's scope, carried into §11. **REJECTED** = not accepted, with the evidence. No finding is silently dropped.

### Blockers

| # | Disposition |
|---|---|
| **#1** | **FIXED (§2.2, §2.4, §2.5, §9 R-1/R-2).** The "do not re-derive" sentence and v1's §9 ruling row are **withdrawn**. §2.2 prints the gold lens's figures to five decimals on the named artifact-bearing cohort (A 0.60628 / B 0.59032 / C 0.61613), plus identity-passing figures at three levels, and states that **the direction is known to the design phase** — in opposite signs under the mutant and group forms. Tier D holds it under a charter; Tier C's integrity does not rest on it being unknown. **Panel #1's "+0.0065 (artifact-bearing)" reproduces exactly (+0.00649, p = 0.8601); the v2 draft's proposal to withdraw it is itself withdrawn.** |
| **#2** | **FIXED (§4.2.1–§4.2.3).** The level is a registered family axis with **three** poles retained. Going further: §4.2.2 shows the sign reversal is a **structural offset of −0.0496** derivable from the manifests without arm labels, and 019's registered level enters **de-biased** rather than being removed — removal was argued from arm-labelled contrasts and is anti-conservative under IU. §11 states that on 019 the *choice*, not the treatment, supplied the observed sign. |
| **#3** | **FIXED (§4.2.3, §4.2.4).** Both adjustment poles are members; R1 names the unanimity rule, not a quantity. The ANCOVA form is pinned to the byte (three-arm pooled within-arm slope at the grand covariate mean) and reproduces panel #3 exactly: b = +0.02332, adjusted means 0.6106 / 0.5893 / 0.5945, adjusted A−C +0.0161 (p = 0.2309) against unadjusted +0.0408 (p = 0.0213). |
| **#4** | **REJECTED-WITH-REASON on the cure's letter; FIXED on its substance; ACCEPTED-DISCLOSED on the residue.** The cure ended "do not register both under one R1", and R1 does register both — the reason is the IU argument of §4.2.5 and the demonstration of §4.3.3, where a suite-size-only alternative rejects 98.6–99.8 % of unadjusted per-protocol members and Tier C **0.000**. The mediator objection is accepted in full: the unadjusted total-effect member's agreement is *required*, so no confirmatory sentence rests on the direct effect alone, and §1 stays the total-effect question. Balance re-registered on means (20.882 / 21.000 / 19.821). The conservatism this imposes is **M-22** and is printed in §11, not discovered in the results. §1 is not rewritten here — that is **M-18/M-26**. |
| **#5** | **FIXED (§4.2.3, §4.3.2, §10.2).** The analysis population is a registered axis with both poles explicit and every per-member n registered before the freeze. The §1a-denominator SD is published: **0.25427** at the group level. Tier C's MDE at N = 60 is published as **≈ 0.165** (binding member), not 0.035. The six survivor-vector-less runs are zero-filled on the mechanical ground that all six carry `killedPaired: 0`; 020's scorer must emit a survivor vector for every admitted run. **Extended:** the empty-survivor trap (§4.2.2) is a second instance of the same schema defect, worth **0.0526** on the ITT contrast — 2.4× the v2 draft's figure and in the opposite direction. |
| **#6** | **FIXED by removal.** Tier C registers no cut, so there is no attainability gate to make vacuous. The finding stands as recorded — `adequacy.disposition = killed-by-gold` on 157/157 adequate JPS and 150/150 adequate Rego, so the reference-derived gold suite's union-kill ceiling is 69/69, 62/62, 33/33 by construction and v1's rule was arithmetically identical to `cutReachable`. **No replacement machinery is registered**; the v2 draft's pre-freeze attainability probe and refusal branch are withdrawn along with the gate they were meant to anchor. |
| **#7** | **FIXED by removal.** The τ rule and the illustrative 21/33 are withdrawn entirely. The 28/33 union ceiling and the 12–25 per-run range are published as **corpus structure in Tier D**, with the cohort named and **no threshold derived from them**. (For the record: `⌈0.75 × 28⌉ = 21` was read off the 019 batch's union, which the same bullet forbade; the reference-derived anchor would have given 25, reached by exactly 1 of 88 runs.) |
| **#8** | **FIXED (§6.3 C3(iii)), and escalated by C3(iv).** Confirmed by re-derivation: `retired_x1` selects exactly 5 of 117 rows; under repair-removed gold the per-arm best runs score 2 / 5 / 5 = 0.9829 / 0.9573 / 0.9573 and **the gate holds in all three arms**, with arm A unchanged because the degradation makes its dominant failure mode correct. The degradation is retargeted to the **stimulus**, its per-arm miss-count shift is published before the pilot, and it is budgeted as authoring calls. C3(iv) adds what the panel did not reach: the gate cannot be certified at any affordable n. |
| **#9** | **FIXED-IN-PART; a named residue remains open.** The cure uses machinery 019 already has (`resolvedAtDesignTime: true`; `registeredLabelRule`'s design-time-resolved clause), registers `codex.model` and `codex.reasoningEffort` as design-time-resolved, restates the rule with the null-⇒-PILOT test, drives it in `test_pins.py`, moves the rule out of §7's unchanged list, and registers the pin state as C1's fourth difference. **Residue:** the rule checks design-time-resolved pins *whether or not the freeze has happened*, and `authoring_call.sh:203` refuses on a null model regardless of label — so the **pre-pilot effort sweep**, which must run before the effort value exists, is either refused or unenforced. The draft addressed the pilot's pin state and never the sweep's. **M-25.** |
| **#10** | **FIXED + ACCEPTED-DISCLOSED (§6.3 C2, M-24, §11.5).** Confirmed: one `turn_context` record, no effort member in its payload, and the only `reasoning_effort` occurrence anywhere is `null`. Registered: a **witness-resolution step at pin time**; if no non-null member appears after the flag is set, the pin is registered explicitly as a `CALL.json` self-report with `reasoning_output_tokens` (medians A 2067.5 / B 502.5 / **C 696**) as its only transcript-side proxy, entering C4 as a band. |

### Majors

| # | Disposition |
|---|---|
| **#11** | **FIXED (§4.1).** "Order of magnitude more resolution" is withdrawn. The continuous endpoint is defended only on the two grounds that hold — no τ to make unattainable, no information discarded — and **§4 makes no cross-scale comparison at all**, including the v2 draft's "ratio ≈ 1.1–1.4×", which is the same incommensurable comparison restated. |
| **#12** | **FIXED (§2.1).** v1 §2.1's claim is **withdrawn** and every violation is named with figures (clear rates 0/36, 1/36, 1/36, 3/36 at ≤1/≤2/≤4/≤5 misses; §4.1's per-run arm-A unions; the median-based balance claim). Arm-blindness is demoted to a **reporting discipline** plus a checkable **membership rule** (§4.2.1); it is not offered as a guarantee about anyone's knowledge. The earlier draft's narrow claim that "every quantity used to specify or size R1 is arm-blind" was false while criterion (i) stood, and is true now that criterion (i) is withdrawn. |
| **#13** | **FIXED AND ESCALATED (§6.3 C3(iv), M-23).** The OC table is computed and published. Beyond the finding: at N = 50 the degraded per-run clear rate must be ≤ 0.001025 to certify P(fire) ≥ 0.95, needing ~2,926 degraded runs — so *no* affordable degradation control certifies this gate. Honest options are (a) no author-side gate, (b) register it labelled uncertified, (c) replace the max statistic with a median-type statistic. **Recommendation: (a)**, since the threat it names is caught deterministically by the prompt/prose/reference digest pins. |
| **#14** | **FIXED, sharpened, and its denominator corrected (§1, §4.2.2, §10.4).** Sub-decision (i) is withdrawn, not decided: `gall == gany` in **88 of 88** checkable runs — **not 114 of 114**, which both drafts inherited from the panel; only 90 runs carry a survivor vector and two are degenerate. Fact 1 proves the equivalence structurally, **with its condition** (identity-pass) registered. §1 and §11 state the construct is witness-input coverage; greedy hitting-set needs 21 of the 51 distinct inputs. Renaming is **M-18**. |
| **#15** | **FIXED-IN-PART / ACCEPTED-DISCLOSED — V8-22 is NOT retired, and not for the reason either draft gave.** The weighting asymmetry is quantified (offset −0.0496 at 019's profile; worst case 0.5400) and repaired by symmetrisation (L3, unbiased for any π) and by de-biasing (L2c). **The attainability asymmetry #15 actually names is not repaired**: under the all rule arm A must kill six mutants to score the unit where arm C kills three, and the offset formula assumes π_g is common to both arms, which unequal member counts and unequal difficulty deny. V8-22 stays live; a group-size-imbalance ledger row is added; the full per-class member-count table is a mandatory Tier D publication. |
| **#16** | **FIXED (§4.2.3, §10.3).** The six `caseCount`-less runs are **exactly** the six `survivorsPaired`-less runs (B `run-026/027/032/036`, C `run-035/050`; arm A zero) — a fact the panel's two findings did not connect. They are zero-filled in the ITT members and excluded from the per-protocol members by the identity-pass rule, so no member carries differential complete-case loss. 020's scorer emits `caseCount` for every admitted run with a suite. |
| **#17** | **FIXED (§4.2.4).** **One** scheme is registered: label permutation for unadjusted members (B = 20,000), whole-record permutation for adjusted members (B = 4,000), with the adjusted members' exactness explicitly limited to the strong sharp null and the unadjusted members registered as the reason that limitation is not load-bearing. **Freedman–Lane is explicitly not registered** — it does not achieve exactness for that null either, and registering two schemes in one document was the defect. The word "exact" no longer attaches to any interval; intervals are approximate-coverage BCa bootstraps in Tier D. |
| **#18** | **FIXED (§3).** Exclusive table published and verified against `perArmRuns[].code`: A 38 ITT / 2 no artifact (`no-marker-block` 2) / 0 collapsed / 36 intermediate / 0 perfect; B 37 / 7 (`opa-check-failed` 4 + `unparseable-artifact` 3) / 20 / 2 / 8; C 39 / 9 (`opa-check-failed` 9) / 13 / 3 / 14. **The v2 draft's annotations were wrong** — it printed B as "7 (`unparseable-artifact` 7 … `opa-check-failed` 4)" and C as "9 (`opa-check-failed` 9, `unparseable-artifact` 2)", both summing to 11 against columns of 7 and 9, by mixing the no-artifact column with runs that do carry a `kill` block. Footnote 1 restated. §3.2's ceilings unaffected. |
| **#19** | **FIXED-IN-PART / ACCEPTED-DISCLOSED (§1, §11, M-13, M-26).** The diagnosis is accepted: E4 scores the authored suite against mutants of the **reference**, under an identity control also against the reference, so "accompanying" is exactly what the endpoint severs. **M-13 now carries a recommendation** — register the suite-against-own-policy score as a reported quantity R1's construct statement is conditioned on (one extra engine invocation per run; it changes what "identity" means, which is a registered change). Whether or not it lands, §1 and §11 state that the endpoint measures pinning against the shared reference. |
| **#20** | **FIXED (§5.2).** Confirmed against source: **all 13 rules and all 14 exceptions carry a leading clause id**, so v1's S1 rule selects the empty set. Replaced by `check_gold.py::retired_x1` — committed, V7-certified, verified to select exactly the five `x1r-*` rows. The "mechanical, not declared" claim is retained for S1 and **withdrawn for S2** until `entailed-guard` is lifted to the JPS side; if it cannot be, S2 is dropped (M-3). |
| **#21** | **FIXED (§6.3 C4).** Two-sided: exact-equality rows hold and only band rows differ ⇒ **`calibration-invalid`** and a re-pilot; any exact-equality row differs ⇒ `pipeline-invalid`. C5's monotone rule extended to cover the transfer bands, not only the derived floor. |
| **#22** | **FIXED AND EXTENDED (§7, §8).** Confirmed and enlarged: `registry-mismatch: 9` on arm A, and the stale digest `36912ee3` on 9 arm-A, 10 arm-B, 10 arm-C `CALL.json` files — 29 of 149 — with **all 20 B/C ones carrying `exitStatus: 126`** (19 with `startedAt == endedAt`; the draft's "all 20 zero-duration" overstates by one). Day-one requirement: any post-freeze registry re-pin invalidates every slot recorded before it, so either the scorer's check reads a semantic subset or a repair halts and restarts. §8 prints the assumed per-arm apparatus-loss rate behind its projection. |
| **#23** | **FIXED as an axis, not as a reporting footnote — reversing the earlier draft.** Under the excluded column **12 of 69 paired JPS and 0 of 62 paired Rego** leave and shared classes fall 33 → **29** (paired totals 57 / 55) — an entirely one-sided change, which is an arm-blind reason it can matter. The earlier draft refused it as an axis on the strength of 019's arm-labelled contrasts; that is exactly the move criterion (i)'s withdrawal forbids. **Both columns are family members** (M4/M5/M6/M10/M11/M12/M16/M17/M18), and every figure in this brief is labelled included- or excluded-column. |
| **#24** | **FIXED (§6.4, §8).** The sweep is priced per setting at that setting's hypothesised duration: registered triple **349 s = 5.82 min**, pilot-like triple **3087 s = 51.46 min** (8.85×). §8 is a range across the M-8 branches with a total call count, a per-setting per-call ceiling and an abort rule. |
| **#25** | **FIXED (§6.1).** One admission cohort for every duration and byte figure. Pilot completed medians A 1660.184 / B 803.042 / C 624.114 (v1's "~818 / ~757" were all-six medians including a censored 900 s timeout); registered executed-only medians **199 / 75 / 75** (all-record medians 199 / 74 / 72.5 include 20 `exitStatus: 126` records with null duration, B 10 and C **10** — the v2 draft's "B 10 and C 9" and its arm-C executed median of 74 do not reproduce). |
| **#26** | **FIXED (§6.3 C4).** Bands derived from retained within-condition dispersion, re-derived here (bootstrap medians-of-12, 4,000 resamples, seed 3): duration [0.930–1.083] / [0.960–1.080] / [0.920–1.067]; bytes [0.926–1.106] / [0.917–1.059] / [0.941–1.043]; reasoning tokens [0.857–1.169] / [0.846–1.193] / [0.727–1.177]. Registered bands ~2.5× that span. Each row's power against the 019 mismatch is stated, and the three rows with no pilot-side witness are **demoted to descriptive** for any 019 comparison. |
| **#27** | **FIXED (§7).** Confirmed: `PREREGISTRATION.md` line 319 and `PINS.json` `batch.window` both register three consecutive UTC days, so D-4 filed a deviation against a rule 019 did not have. Corrected the way M-11 corrects #88, and restated as "one registered statement of the window, with a test that no other document states a different one." |
| **#28** | **FIXED (§7).** The schedule row leaves the ported-by-digest list. `batch.py:308-317` hard-codes the 50-round shape and `derive_order()`'s docstring records the cached floor as the answer *at 50 rounds*; at 60 rounds there is no tail and spread 0 becomes attainable, so `test_schedule.py`'s assertion is wrong by construction. Day-one work item. |
| **#29** | **FIXED (§7).** The reviewer mutant set is **spent** (`reviewerMutantSet.note`; `reviewerSet.perArm` publishes the per-run outcome). 020 registers a fresh sealed set; 019's is kept only as a published comparison. |
| **#30** | **FIXED (§8).** Free-space precondition at driver start and before each slot; retention rule for the scratch parent (two directories per slot); total call and disk budget summed — ~249 calls under the recommended plan, 019's 149 slots occupying 86 MB in-tree. |
| **#31** | **FIXED (§4.3.2, §10.2).** All SDs are N − k (residuals N − 4). The per-protocol group SD 0.06938 reproduces the panel's 0.0694; the v2 draft's 0.0888 / 0.2047 / 0.1656 for three Tier D rows are corrected to **0.11396 / 0.13012 / 0.17946**, and the "0.2486 alternative" is a trap artefact, not an analysis option. The imbalance term is added, not dropped: `S_xx,within = 355.6`, gap 1.061, inflation 1.034 at n = 43. |
| **#32** | **FIXED (§8).** Two realised-n branches with their arithmetic — D-1/D-3 cured (≈ 43/40/43 at N = 60, reproducing the panel) and + registry cure (≈ 53/40/43) — and every MDE labelled with the n it was computed at. v1's 50/35/40 withdrawn. |
| **#33** | **FIXED (§4.1, §10.1).** The dichotomy and v1's I4 quantile sentence are withdrawn together. Where dispersion is quoted, it is a pooled within-arm SD with cohort and divisor named, and no sentence mixes cohorts. |
| **#34** | **FIXED (§6.1).** Restated as *"using the rule-of-three 95 % upper bound 3/38 for arm A, whose observed rate is 0"*, with the note that a bound-plugged probability is not a p-value. B (8/37)⁵ = 4.72 × 10⁻⁴ and C (14/39)⁵ = 5.96 × 10⁻³ stand. |
| **#35** | **FIXED (§1, §3).** `PREREGISTRATION.md` §1 is quoted verbatim under the "unchanged" heading, including its closing three-arm comparison clause; the E1 instrument-repair commitment moves to §3 where it is argued. |
| **#36** | **FIXED (§6.3 C3(iii), §8).** The degraded object is named — the **stimulus** — and budgeted with authoring calls. v1's reference-side recommendation needed no model calls, which is why its 36-call line concealed that the recommended control was not a re-authoring experiment. |
| **#37** | **FIXED (§4.4, §10.4).** The five never-covered classes are named with their `d8` witness inputs and their sixteen mutants, and **effective support 28** is stated wherever the estimand is defined. The observed range 12–25 is bounded above by 28, not 33. |
| **#38** | **FIXED (§6.1, §6.4).** Both argv vectors printed side by side; the omitted **read-only vs workspace-write** difference named and connected to the test-row gap; *"recover pilot-like behaviour"* withdrawn as an objective; §6.1 states that C1 alone removes four of the five recorded differences without any effort pin. |
| **#39** | **FIXED (§7, §8).** Restated as *"a real exec at the registered prompt bytes, stand-in binary permitted"* — D-1's failure was `/usr/bin/env: Argument list too long` at `exec`, which a stand-in binary reproduces exactly — with D-2's stand-in-**study** smoke preserved and its real calls added to §8's table. |

**Reproduction note.** Every figure in this brief was computed by scripts under `scratchpad/v2check/` and `scratchpad/v2oc/` — `family18.py` (the eighteen members, per-member SDs, the drop-a-pole table), `tierd_rows.py` (the single-choice ledger, ITT × ANCOVA cells, per-arm means), `oc18.py` (§4.3.3–§4.3.4, seed 20200822) — from `RESULTS.json`, the two manifests, `GOLD.json`, `pack.json`, the retained `CALL.json` / `session.jsonl` / `completion.txt` files, the pilot directory, and `git show a5bb49f`. Independent cross-checks against the panel's recomputations agree to the digit where both exist: pairing 33/69/62; artifact-bearing mutant means 0.60628 / 0.59032 / 0.61613; identity-passing mutant A−C −0.01819 and group A−C +0.04081; ANCOVA slope +0.02332 and adjusted means 0.6106 / 0.5893 / 0.5945; pooled within-arm group SD 0.06938 (identity-passing) and 0.25427 (§1a denominator); union ceiling 28/33; coverage range 12–25; 20 of 33 unequal classes; Lee bounds [+0.0236, +0.0629] and [+0.0166, +0.0672]; 2,926 and 3,511 degraded runs; CP bounds 0.549 and 0.779. **New to this brief, not in the panel's record:** the structural offsets and their worst cases; the empty-survivor trap and its corrected magnitude; the 88-run denominator for the `gall == gany` equivalence; the eighteen-member family and its drop-a-pole robustness; the supplied operating-characteristics simulation; and the six numeric corrections to the v2 drafts recorded in §9.

---

## 13. What this brief does not decide

Nothing in this document is registered. The following are put to the maintainer, in one numbering sequence (M-1 to M-14 keep v1's meanings; M-15 onward are new to v2).

**Answered.** **M-1 — may 020 read arm labels from 019's batch? ANSWERED BY THE MAINTAINER, 2026-08-22: BOTH.** The two-tier footing is implemented throughout. What remains is M-15.

**Carried from v1, revised here.** **M-3** (keep the seven; S1 by `retired_x1`; S2 conditional on lifting `entailed-guard`). **M-4** (no stimulus repair — recommended). **M-7** (`caseCount` as a family dimension, a construct quantity and a balance check on means; do not fix suite size in the prompt). **M-8** (pin reasoning effort; value from a per-setting-priced sweep — the one decision the evidence cannot make). **M-9** (C1–C5 as registered machinery, with a stimulus-side degradation). **M-11** (correct #88 before citing it). **M-12** (publish 019's blocked descriptive content — now forced by Tier D's charter). **M-13** (suite-against-own-policy control — now **recommended**). **M-14** (the B/C collapse mechanism: input-shape contract miss or U1 comprehension failure — **still open, still unread**; one focused pass over `arms/B/authoring/run-011/` against a perfect arm-B run, before the brief is registered).

**Superseded.** **M-2** is re-opened as M-23. **M-5** and **M-6** are answered by §4's family and the removal of every dichotomy; there is no primary form left to choose and no τ left to fix. **M-10** is folded into M-20.

**New in v2.**

> **M-15 — publish the 019 R2 amendment before 020's preregistration is drafted?** It would carry §2.2's three cohorts, §4.3.1's eighteen-member table and the single-choice ledger — not the single row a reader might mistake for "the answer." **Recommendation: yes.** Tier D's charter is unenforceable if the prior it disciplines is not on the public record.

> **M-16 — the four residual family-membership questions.** (a) Does the **raw** native mutant level enter as a fourth level pole beside L2c, or stay a Tier D continuity row? *Recommendation: stay Tier D, with its offset attached — a member with a known −0.05 structural bias would make Tier C partly a test of the bias.* (b) Do the six **ITT × ANCOVA** cells enter under a `caseCount = 0` convention? *Recommendation: no — the imputation makes the covariate a proxy for artifact production and flips the ITT group contrast from +0.1385 to −0.0201; publish them in Tier D.* (c) Does **artifact-bearing complete-case** enter as a third population pole? *Recommendation: no — it is the per-protocol set plus whatever identity-failing runs happen to carry a survivor vector.* (d) On what basis is **L2c's offset** estimated — pooled marginal over the member's own population (as registered), over the frozen corpus, or by a worst-case bound? And is its estimation variance propagated? *Recommendation: as registered, with the three limitations printed in §11.* Every one of these is a choice to **narrow** the family, so each needs an arm-blind reason on the record.

> **M-17 — is the ITT pole the right guard against differential selection, or should Lee-style bounds replace it?** The ITT members carry Tier C's precision (σ 0.254–0.322 against 0.051–0.105) and their variance is irreducible. Lee bounds address the same threat far more cheaply: on 019, trimming arm A by 19.8 % gives A−C bounds **[+0.0236, +0.0629]** at L1 and **[+0.0166, +0.0672]** at L3 — entirely positive under both levels. But the bounds need a monotonicity assumption the ITT pole does not, a proper test needs an Imbens–Manski interval, and — decisively — the trim fraction is read off **arm-labelled validity rates**, which Tier D's charter forbids as an input to a Tier C quantity. **Options:** (a) keep the ITT pole as registered; (b) replace it with Lee-bound members and register both the monotonicity assumption and the arm-labelled trim as ceilings; (c) keep it **and** publish the bounds in Tier D. **Recommendation: (c).** It costs nothing, gives the reader the diagnosis when the family splits on the population axis, and keeps an arm-labelled quantity out of the confirmatory tier.

> **M-18 — must §1 and the study slug be renamed to name coverage?** Fact 1 proves the endpoint is a function of which witness classes a suite reaches; assertions never enter. **Options:** (a) rename, keep §4's family and its OCs — *recommended; everything in §4.3 survives*; (b) design an assertion-reading endpoint and accept that Tier C ships unpowered-by-construction, with a pilot to re-derive dispersion (§4.3 would become a prior, not a calibration); (c) keep the present wording and disclose in §11 — **this brief considers (c) indefensible**.

> **M-19 — α = 0.05 per member, or a stricter common level?** Because IU size is bounded by the *single-member* level (≤ 0.025 for a signed claim), there is no statistical reason to lower α, and lowering it costs power multiplicatively across eighteen members. **Recommendation: α = 0.05 per member, two-sided, no correction**, with §4.2.5's size argument printed in full so the absence of a correction is visibly deliberate.

> **M-20 — N, given that Tier C's power depends on a quantity 020 cannot know in advance** (and folding in v1's M-10 on pilot N). At N = 60/arm Tier C is 80 %-powered at θ ≈ 2 classes if 019's validity gap persists and θ ≈ 9 if it does not. This interacts multiplicatively with M-8. **Options:** (a) fix N = 60, register the two-regime power statement verbatim, and accept INDETERMINATE as a likely outcome — *recommended; it is the only option that does not require knowing the answer first*; (b) an interim-free two-stage design with N chosen from the pilot's observed per-arm validity rates — new machinery this brief has not costed; (c) N = 100+, at which the binding MDE falls to 0.128 — a ~9.7 h batch at registered durations and ~86 h at pilot-like ones. Pilot N: **12/arm recommended** (CP lower bound 0.779 on a clean sweep).

> **M-21 — must the preregistration reprint §4.3.1's three tables?** (the eighteen-member table, the drop-a-pole table, the single-choice ledger). **Recommendation: yes, all three, verbatim, in the body and not an appendix.** The ledger is the evidence that a single-member registration would have been a coin whose face was already visible; the eighteen-member table is the evidence that the registered family does not ratify 019's answer; the drop-a-pole table is the evidence that the second claim is robust — and it is also where the one exception is printed. Omitting any of the three leaves the footing asserted rather than shown.

> **M-22 — accept and print the conservatism unanimity imposes when the effect runs through the `caseCount` mediator?** If the representation effect operates through suite size, the adjusted members will not agree and Tier C returns INDETERMINATE on a real total effect. **Recommendation: accept and disclose in §11**; the alternative — dropping the adjusted members — hands the verdict back to a single contaminated choice.

> **M-23 (re-opens M-2) — given C3(iv), does 020 register an author-side control gate at all?** **Options:** (a) **no author-side gate** — the deterministic stimulus-integrity pins are the control, E1 is fully descriptive, and the OC table is published as the reason (**recommended**); (b) an existence gate registered with the OC table and an explicit "uncertified, disclosed-weak" label and no claim of power — defensible only if the label is in §11's ceilings, not a footnote; (c) replace the max statistic with one certifiable at affordable n (a per-arm median, or "≥ half the admitted runs reach agreement ≥ x") and register its OC table with x from `derive_floor.py`. The derived threshold's seat as a **pre-freeze go/no-go** survives in every branch; only the existence gate's seat as *the registered control gate on the batch* is at issue.

> **M-24 — C2's witness branch.** If no non-null transcript member names the effort after the flag is set: (a) register the pin as a recorded self-report with `reasoning_output_tokens` as its band-checked proxy (**recommended**), or (b) treat the effort as unpinnable, leave it at the CLI default and record the default's identity. Not deciding before pin time means discovering it during the sweep.

> **M-25 — the pre-pilot effort sweep's pin state (#9's residue).** The sweep must run before the effort value exists, but `authoring_call.sh:203` refuses on a null design-time-resolved pin regardless of label. **Options:** (a) a distinct `--sweep` label that exempts `codex.reasoningEffort` alone from the null check, with each sweep call's setting stamped into `CALL.json` and the sweep's outputs `citable: false`; (b) resolve the effort pin to the CLI default before the sweep and treat each swept setting as an explicit per-call override recorded as a deviation from the pin; (c) run the sweep outside the harness — **rejected on sight; that is the 019 failure exactly.** *Recommendation: (a), written into the gate and its test before the first sweep call.*

> **M-26 — does Tier C's claim sentence carry the "against the shared reference, not against the accompanying policy" qualifier, or does M-13's control land first?** Panel #19 asks for one of the two. If M-13 lands, `identityPass` changes meaning and **every per-protocol member's population changes with it**, so §4.3.2's dispersion figures and §4.3.3–§4.3.4's operating characteristics would all have to be re-derived. This brief has no basis to prefer either and takes no position.

**Not decided anywhere in this document, and not by an M-block:** whether the study is worth running at all if the maintainer's answer to M-20 is (a) and the truth resembles 019 — in which case Tier C returns INDETERMINATE with probability approaching 1, and the study's entire yield is Tier D's descriptive battery plus a repaired instrument. That is a programme judgement, and it belongs to the maintainer, not to the brief.