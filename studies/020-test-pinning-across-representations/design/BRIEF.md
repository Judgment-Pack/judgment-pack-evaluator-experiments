# Study 020 design brief — test-pinning power across representations (JPS vs OPA/Rego), instrument repair

**Status: DRAFT design brief v1, pre-preregistration. Nothing here is registered.** This document
responds to Study 019's registered attempt, which reached §5's decision row 3
(`control-gate-failed: e1-floor`) and computed no contrast
(`results/primary-attempt-001/RESULTS.md`). It was assembled from three adversarial design lenses
(endpoint design; gold/stratification; calibration transfer) over 019's retained artifacts, and every
figure below was re-derived by this brief from `results/primary-attempt-001/RESULTS.json`,
`mutants/MANIFEST-jps.json`, `mutants/MANIFEST-rego.json`, `gold/GOLD.json`, `harness/PINS.json` and
the retained `CALL.json` files unless the text says otherwise. **No new model calls were made.**
Proposed slug: `020-test-pinning-across-representations` (naming the mechanism 019's preregistration
actually registered as primary; deliberately not a near-collision with `019-authorship-across-representations`).

All paths are relative to `studies/019-authorship-across-representations/` unless stated.

---

## 0. Where 019 left the program

- **The question was never answered.** 019 froze (`51cae02`, PR #69), ran 150 slots, and stopped at
  `PREREGISTRATION.md` §5's row 3. Cause: `e1-floor`. The registered contrasts (fixed sequence A−C,
  then A−B) were **not computed and not published**, under §5's rule that *"no inferential quantity is
  computed, let alone published, at or above row 3"* and R2's refusal text — *"a direction computed and
  then withheld is a direction published"* (`RESULTS.md` §"R2").
- **The primary endpoint had already pivoted.** 019's `design/BRIEF.md` §5 registered E1
  (perfect gold agreement) as primary; `PREREGISTRATION.md` "Design provenance" item 1 pivoted the
  primary to **E4 (test-pinning power)** on the strength of the pilot — *"correctness is at ceiling for
  well-specified prose at this scale, in all three representations"* — leaving E1 as *"a reported control
  expected at ceiling"*. **020 inherits the prereg's construct, not the v3 brief's.**
- **Both endpoint arms of that decision failed, for different reasons.** E1 was not at ceiling anywhere
  (A 0/38, B 8/37, C 14/39 against a 0.60 floor). E4 returned 0 high-kill runs in every arm at
  τ = 19/20 — and §3.2 below shows that cut was **unattainable**, not merely stringent.
- **The stimulus controls all held**: `references-reproduce-gold` 117/117 both references,
  off-gold certificate current, capabilities canary refused, golden-context gate with assent,
  `engine-execution-clean` with 0 refusals, 0 timeouts in all three arms
  (`RESULTS.json.controlGates`, `population.*.timeoutRate`). Nothing in the record says the stimulus
  regressed. The gate that fired was not measuring the thing it was registered to measure.

**020 is an instrument-repair study. It does not change the question, the policy prose, the gold bytes,
the arms, the references, or the mutant corpora.** What it changes is which quantities gate, which
quantity is primary, and how the difficulty calibration is produced.

---

## 1. The question, unchanged — and the five instrument defects 020 fixes

> **Within the registered JPS-expressible policy fragment, under single-shot authorship, does the
> representation a model authors in change what its accompanying test suite pins down — with gold
> agreement (E1) as a control that is actually passable?**

Scope qualifiers ride inside the question exactly as in 019 §1: the fragment is arm A's expressive
envelope, selected by no other criterion (`V8-ASYMMETRY-LEDGER.md` **V8-30**, `A-favorable` by
construction), and Study 003's census (12/12 surveyed real decisions escape the pack) bounds
generalization. Nothing in 020 relaxes those.

| # | Defect in 019's instrument | Evidence | §
|---|---|---|---|
| **I1** | The control gate read an **outcome the primary does not read**. E1 scores the authored *policy*; E4 scores the authored *suite* against mutants of the *reference*. Nothing couples them. | Among identity-passing runs, arm B's collapsed-policy runs (≥50 gold misses) kill paired mutants at **0.683** vs **0.677** for non-collapsed; arm C **0.633** vs **0.684**. A policy wrong on 86–104 of 117 rows kills at the same rate as a perfect one. | §3 |
| **I2** | The primary's cut was **outside the empirical support**. `cutReachable: true` only asserts *cut ≤ denominator*. | Union of all 34 identity-passing arm-A suites kills **61** of 69 (cut 66). Union of all 54 identity-passing Rego suites kills **54** of 62 (cut 59). No merger of every suite in the study reaches either cut. | §4 |
| **I3** | The difficulty calibration measured **a different condition** from the batch. | Prompt bytes identical (verified: `sha256sum arms/{A,B,C}/PROMPT.txt` equals `design/pilots/2026-08-15-calibration-pilot-01/prompt-{A,B,C}.txt`, three matched pairs). Pilot arm-A completed calls **1559–2408 s** with five 900 s timeouts; registered arm-A calls median **199 s**, max **273 s**, `timeoutRate` 0.0. `harness/PINS.json` pins model, CLI version and binary digest and contains **no reasoning-effort member** (grep: no `reasoning` key). | §6 |
| **I4** | The endpoint was **dichotomised on a distribution ~0.10 wide** and is substantially a measure of suite size. | Pooled ITT paired-kill quantiles q25 0.419 / median 0.667 / q75 0.710 / max 0.806. r(caseCount, kill fraction) = **0.664 / 0.836 / 0.804** by arm; within-arm slope **+0.033 kill fraction per test case** (+0.0233 at group level). Suites are 16–25 cases (medians 21 / 20.5 / 20). | §4 |
| **I5** | The post-attempt diagnosis (**issue #88**) was **not re-derived** and does not reproduce. | #88's `/48` denominator exists nowhere in `RESULTS.json` (ITT 38/37/39; artifact-bearing 36/30/30; identity-passing 34/26/28). Its "5/48 perfect on the remaining 110" recomputes to **25** of 96 artifact-bearing runs (A 3, B 8, C 14). | §2.3 |

---

## 2. What the 019 batch may and may not be used for

### 2.1 Registered: the arm-blindness rule for design inputs

019's batch is **not a non-citable pilot**. It is a completed registered attempt whose primary contrast
§5 forbade computing. Choosing 020's τ, trim, endpoint or floor by looking at which choice separates
019's arms would (a) re-import the withheld direction into 020's registration and (b) select 020's
estimand on the outcome it exists to test.

**Proposed registered rule.** Every quantity 020 uses to *design* an endpoint must be derivable
without arm labels: pooled distributions, per-language corpus structure (witness sets, groups, union
ceilings), within-arm dispersion with arm means removed, and rules anchored on the *reference-derived*
suite rather than on run outcomes. Everything in §3–§5 of this brief was derived under that rule and
is re-derivable from three retained files.

### 2.2 The disclosure this brief owes (lens disagreement, adjudicated)

The gold/stratification lens **did** compute and print arm-labelled E4 means from 019's batch
(reported as A 0.606 / B 0.590 / C 0.616). Two things follow, and both are disclosed rather than
managed:

1. **They do not re-derive.** Among identity-passing runs the paired kill-fraction means are *different
   numbers in every arm* than that lens reported. Like #88, a stated figure without its derivation.
2. **The quantities exist and anyone can recompute them** from `RESULTS.json`. A design brief written
   while privately knowing them, that then hides them, is precisely the failure mode 019's own refusal
   text names. This brief therefore **uses none of them to choose anything** and puts their disposition
   to the maintainer.

> **Decision M-1 — may 020 read arm labels from 019's batch, and what happens to the arm-labelled E4
> quantities that a design lens already computed?**
> Options: (a) arm-blind calibration only, and 019's per-arm E4 kill fractions published as part of
> 019's R2 disposition (an amendment to the 019 results document) so that 020's design provenance rests
> on published, not privately-held, knowledge; (b) arm-blind calibration only, quantities withheld;
> (c) full arm-labelled re-analysis permitted, with the A−C direction published as a 019 amendment first.
> **Recommendation: (a).** §3–§5 were all derived arm-blind, so (a) costs nothing analytically, and it
> resolves the "computed then withheld" problem in the only direction 019's own standard allows.
> (c) reopens a registered refusal and is a larger act than it looks. **(b) is the option this brief
> considers indefensible** now that the computation has happened.

### 2.3 Registered: issue #88 is corrected before it is cited

Re-derived from `RESULTS.json.perArmRuns[].goldFailures`, over the 96 artifact-bearing runs
(A 36 / B 30 / C 30):

| Row | #88 | A | B | C | pooled |
|---|---|---|---|---|---|
| `p1-absent-escalation-region` | 47/48 | **35** | 6 | 2 | **43** |
| `p1-unreported-escalation-region` | 47/48 | **35** | 0 | 0 | **35** |
| `x1r-country-unreadable-{100k,40,69}` | 34–35/48 | 28 each | 20 | 13 | 61 each |
| `x1r-low-spend-unreadable-{40,69}` | 34–35/48 | 27 each | 20 | 13 | 60 each |
| perfect on the remaining 110 | 5/48 (10.4%) | **3** | **8** | **14** | **25** |

#88's *qualitative* diagnosis survives and is sharper than stated: restricted to non-collapsed runs
(<50 misses), **no arm-B and no arm-C run misses any of the seven** — they are an arm-A-only failure
mode in this batch, exactly as `V8-ASYMMETRY-LEDGER.md` V8-09 and V8-10 predict (both `B/C-favorable`).
And arm A's residual is not "scattered": it concentrates in the unknown-propagation family
(`u1-two-unreadable-uniform` 14/36, `u1-risk-prior` 13/36, `u1-country-2m` 8/36, `u1-ex1` 7/36, then
`o1-nv-*` at 4–6), a named mechanism, not noise.

> **Decision M-11 — correct issue #88 (re-derive against `RESULTS.json`, or state the cohort it used)
> before any 020 document cites it.** Recommendation: correct it. Do not carry "10.4% vs the 0.6 floor"
> forward. This is `derive-scope-dont-enumerate` in its usual clothes.

---

## 3. E1 — the control that was not a control

### 3.1 Three mechanisms, one floor

| Arm | ITT | No scorable artifact | Collapsed (≥50 misses)¹ | Near-gold | Perfect |
|---|---|---|---|---|---|
| A | 38 | 2 (`no-marker-block`) | 0 | 36 (2–15 misses of 117) | **0** |
| B | 37 | 7 (`opa-check-failed` 4, `unparseable-artifact` 3) | 20 | 10 | 8 |
| C | 39 | 9 (`opa-check-failed`) | 13 | 17 | 14 |

¹ "Collapsed" is a **cohort label introduced by this brief**, not a registered category. Arm A is
unimodal and never perfect (miss counts 2…15); arms B and C are bimodal — perfect or 86–104 misses,
answering `unresolved` on essentially every row. One confirmed mechanism, `arms/B/authoring/run-011/`
(86 misses, `identityPass: true`, `checkExit: 0`): the policy gates U1 candidate enumeration on
`"riskScore" in input.vendor`; in Rego v1 `in` over an object tests **values**, not keys, so the guard
is always false and the ladder never resolves. The arm-C shape is the mirror — `unresolved:[no-match]`
from the *prescribed* `default decision` (V8-12).

**These are not one failure and one floor cannot govern both.**

### 3.2 No member of the candidate criterion family clears 0.60

Every 019 run re-scored under each candidate, on the registered ITT denominators 38/37/39:

| Criterion (per run) | A | B | C | 0.60 floor holds? |
|---|---|---|---|---|
| perfect 117/117 (**as registered**) | 0.000 | 0.216 | 0.359 | no |
| agreement ≥ 0.99 (≤1 miss) | 0.000 | 0.216 | 0.359 | no |
| agreement ≥ 0.95 (≤5) | 0.079 | 0.243 | 0.385 | no |
| agreement ≥ 0.90 (≤11) | 0.763 | 0.243 | 0.385 | no |
| agreement ≥ 0.85 (≤17) | 0.947 | 0.270 | 0.436 | no |
| trimmed-gold perfect (110/110) | 0.079 | 0.216 | 0.359 | no |
| trimmed ≥ 0.90 (≤11 of 110) | 0.921 | 0.243 | 0.385 | no |

Read the B and C columns: they stop at **0.270** and **0.436** and never rise, because those are the
non-collapsed counts. Loosening a row criterion cannot recover a run that is `unresolved` everywhere,
nor the 7 and 9 runs with no scorable artifact. **A rate floor repairs arm A and does nothing for
B/C; a trim repairs arm A less and does nothing for B/C.** The only floors this batch could clear are
≤ 0.27. A gate three-quarters of runs may fail is not a control.

### 3.3 Registered (proposed): replace the floor with an existence gate

> **Per-arm gold-attainability.** Each arm's admitted runs must contain **at least one** run agreeing
> with gold on **≥ 0.95** of adjudicated rows (untrimmed, all 117).

Rationale: a regressed stimulus — corrupted prose, broken prompt assembly, wrong naming appendix — is
**common-mode**: it makes the task impossible for every run in every arm. An authoring finding is
arm-specific and leaves the best run near ceiling. On 019's batch this gate holds in all three arms
(A 115/117 = 0.983; B and C 117/117) and the study would have reached its primary. Its honest weakness
is stated in §6.4: at N = 60 a single lucky run clears it, so **it must be shown to have power against
a deliberately degraded stimulus** before it counts as a control (the program's standing
*mutation-check every safeguard test* lesson).

**Descriptive, published, never gating** (preserving 019 §10's publication commitment): per-run perfect
agreement rate; the full row-agreement distribution; the same two on the 110-row support with the
strata named; and the E3 taxonomy with `u1-*` and the two `p1-*` region rows as **named categories**.
019's actual finding — *arm A never achieves perfect gold agreement, and the mechanism is a derived
lemma the prose never states* — becomes a reported result instead of a study-killer.

**Kept as gates, unchanged:** `references-reproduce-gold`, off-gold certificate currency, capabilities
canary, golden-context + isolation negative, `engine-execution-clean`, timeout-rate cap, all digest and
registry pins. These are the stimulus controls; `RESULTS.json.controlGates` shows they work.

> **Decision M-2 — E1's kind.** Options: rate floor at a lower level / trimmed perfection / two-tier
> (rate gates, perfection descriptive) / **existence gate** / no author-side gate at all.
> **Recommendation: existence gate + fully descriptive E1.** §3.2 disqualifies the first three at any
> floor worth registering; "no gate at all" gives up a real (if weak) common-mode check that costs
> nothing to run.

---

## 4. E4 — the primary, re-specified

### 4.1 τ = 19/20 was unattainable, not stringent

| | registered cut | best single run | **union of all identity-passing runs** | denominator |
|---|---|---|---|---|
| JPS | 66 | 52 | **61** | 69 |
| Rego | 59 | 50 | **54** | 62 |

Exactly **8 paired mutants per language** survived every identity-passing run:
JPS `m-a-008, -012, -046, -057, -059, -063, -067, -092`; Rego `m-b-009, -016, -023, -036, -038, -042,
-052, -151`. All sixteen have `witnessCount: 1`, and the two sets of eight are witnessed by **the same
five gold inputs** — `d8-low-40-500k01-ins-absent`, `d8-70-low`, `d8-low-89`, `d8-2m01-low`,
`d8-2m01-low-absent` (they pair *because* their witness sets are identical, `PREREGISTRATION.md` §4).
They are 5 of the 33 shared groups; the union ceiling is **28/33 in both languages**.

Why nobody reaches them: suites are 16–25 cases and **28 of 69 paired JPS mutants and 20 of 62 paired
Rego mutants are single-witness**. The dichotomised endpoint is substantially a lottery on whether an
author happened to write five particular `d8` boundary inputs. A null at an unattainable cut carries
**no information about pinning power at all**; the published `0 / 0 / 0` is a fact about the cut.

**Registered (proposed): an attainability gate with teeth.** `cutReachable` is a vacuous arithmetic
check (66 ≤ 69). 020 registers, asserted before the freeze and refusing rather than publishing an
unattainable endpoint: *any* cut used anywhere must be ≤ the union-kill ceiling attained by the
**reference-derived gold suite** or by a registered attainability probe.

### 4.2 Registered (proposed): a continuous, group-level, size-adjusted primary

> **R1 (primary, retractable), difference form, scope inside the claim:**
> *Within the registered JPS-expressible fragment, under single-shot authorship, arm A's mean
> shared-witness-group kill fraction differs from arm C's: the exact permutation interval on the
> difference in means excludes 0 at two-sided α = 0.05, with the registered δ published as an
> interpretation quantity that no decision reads (019 §5's R1-15 discipline, verbatim). An
> INDETERMINATE or unsupported outcome licenses no negation.* Fixed sequence A−C then A−B, as 019.

- **Denominator: the 33 shared non-degenerate witness groups.** Re-derived here from the two manifests
  by identical sorted witness set: **33 shared groups, 69 paired JPS, 62 paired Rego** — reproducing
  `RESULTS.md` §E4 and `RESULTS.json.pairing` exactly, which is this brief's check that the
  reconstruction is faithful. Observed per-run group kills across the batch: **12–25 of 33**.
- **This retires V8-22.** V8-22 registers as irreconcilable that *"the two arms' kill denominators are
  different sizes and their rates are quantised on different lattices"* (1/69 = 0.0145 vs 1/62 = 0.0161).
  At group level both languages carry **the same denominator, the same lattice (1/33 = 0.0303) and the
  same union ceiling (28/33)**. This is the pairing construction being used for what it was built for.
- **It contradicts a registered 019 sentence, and 020 must say so.** `PREREGISTRATION.md` §5:
  *"A group-level pairing does **not** equalise the per-arm denominators."* That sentence is true of a
  *mutant-level rate scored over paired groups*; it is not true of a *group-level estimand*, which is a
  different quantity 019 chose not to register. 020 states the change and its reason in its own §5
  rather than quietly scoring a different thing.
- **Registered covariate: `caseCount`.** Within-arm slope **+0.0233 group-kill fraction per test case**
  (mutant level +0.033, ≈ 2.3 of 69). A 25-case suite differs from a 16-case suite by ~0.21 at group
  level — larger than any representation effect this study could plausibly seek. On 019's batch the arms
  were size-balanced (medians 21 / 20.5 / 20), so this is a **variance** problem, not a bias problem —
  adjustment cuts pooled within-arm SD from **0.0682 → 0.0495** (group) and **0.0888 → 0.0591**
  (mutant). If a future batch's arms differ in verbosity it becomes bias, and *"the arm whose format
  invites more test rows wins"* is not the registered question. Registered: ANCOVA adjustment, a
  pre-specified size-balance check, the unadjusted difference published beside the adjusted one under
  the same publication commitment, and a registered non-claim if the arms are size-imbalanced.
- **Precision, at 80% power / two-sided α = 0.05:**

| n per arm | group-level (33) | size-adjusted group |
|---|---|---|
| 34 (019's realised arm A) | 0.046 | 0.034 |
| 45 | 0.040 | 0.030 |
| 48 | 0.039 | 0.029 |
| 60 | 0.035 | 0.026 |

  Compare the registered dichotomy: power **0.49–0.82 for a true 0.20 gap**, with a true 0.25 gap still
  able to return INDETERMINATE (`PREREGISTRATION.md` §5; `design/mutants/OC-TABLE.md`). **The same runs
  buy roughly an order of magnitude more resolution once the dichotomy is dropped.**

- **Two registration details that must not be left implicit:** (i) the **any/all rule** — a run kills a
  group iff it kills *all* of that group's members in its own language (the definition used for every
  figure in this brief) or iff it kills *at least one*; these are different estimands and one must be
  registered; (ii) whether the primary is a **mean difference with a permutation interval**
  (recommended: it is the quantity the program would act on, and the interval is exact without a
  normality premise) or a **Hodges–Lehmann rank shift** (acceptable; the brief would not object).

- **Secondary, descriptive only, never gating:** the high-kill run rate at a τ fixed by an **arm-blind
  attainability rule** registered before the batch — recommended: cut = ⌈0.75 × union-kill ceiling of
  the reference-derived suite⌉, published with the ceiling it came from, refusing if the cut exceeds it.
  On 019's corpus that lands near 21/33 groups — inside the observed support (12–25) rather than 5 above
  its maximum.

- **Registered corpus-structure publications** (findings 019's row 3 blocked): single-witness fraction
  of the paired subset (28/69 JPS, 20/62 Rego); the identity of every group no run kills; the union
  ceiling per language.

> **Decision M-5 — E4 primary form.** Continuous group-level mean difference with permutation interval
> and `caseCount` ANCOVA (**recommended**) / Hodges–Lehmann shift / mutant-level fraction / keep a
> dichotomy at a lower τ. Sub-decisions: the any/all group-kill rule; whether δ is registered at all.
>
> **Decision M-6 — if any dichotomy survives (descriptive), what fixes τ?** Recommendation: the
> attainability rule above, never a number chosen against observed arm rates.
>
> **Decision M-7 — `caseCount`: registered covariate (recommended) / stratifier / descriptive-only / or
> fix suite size in the prompt.** Flagged because fixing suite size is *tempting and is a treatment
> change*: how many cases a representation leads an author to write is part of the construct
> "what the suite pins down". Recommendation: covariate, do not fix suite size.

---

## 5. The seven construct rows — registered disposition

### 5.1 They are two classes, not one (lens disagreement, adjudicated)

The endpoint lens treated the seven as a block; the gold/stratification lens split them. **The split is
correct, verified against source:**

- **S1 — five rows, derived-encoding cost.** `verification/V7-COMPLETENESS.md` §3.4 assertion **A6**
  names exactly **5 rows** in the retired-X1 region, and `design/gold/check_gold.py::retired_x1`
  (lines 58–63) is the predicate that defines it. Mechanism: `V8-09` — *"expressing it costs a derived
  region lemma the prose never states. Arms B/C need no such lemma"* (`B/C-favorable`, a **cost row,
  not a fragment boundary**).
- **S2 — two rows, reason accumulation.** `p1-absent-escalation-region` and
  `p1-unreported-escalation-region` carry `newVendor: "no"`, `risk: "50"` and readable country/spend
  (`gold/GOLD.json`), so `retired_x1` is **false** on both — they are outside S1's region and cannot
  require the region lemma. Their arm-A signature is exact and unanimous: expected
  `unresolved:[missing-required-evidence]`, got `unresolved:[exception-escalation,missing-required-evidence]`
  on 35/35 failing runs. That is `V8-10`'s inert O3 conjunct, and O3's guarding conjunct **is stated in
  the prose**. No prose sentence is missing for these two.

Treating seven rows as one class would be the enumerate-don't-derive error with a mechanism attached.

### 5.2 The three options, costed

**(a) State the region lemma in the prose.** Rejected as a repair. It buys at most **five of the
seven** (S2's guard is already in the prose); it is **untested** — stating the *answer* does not supply
the *encoding* (arm A must still suppress D8 inside the region, which the reference does with four
members — `r-o1-wide-low`, `r-o1-wide-spend`, `x-o1-suppress-d8-low`, `x-o1-suppress-d8-spend` —
corresponding to no prose clause); it **re-derives V7 wholesale**, including §4.4's *pinch 2* proof,
which is built on these five rows and is what registered the governing-clause-first cite convention; it
**edits the byte-identical shared header**, so it edits the treatment in all three arms and deletes a
`B/C-favorable` ledger row by fiat (the ledger runs 11 `B/C-favorable` : 6 `A-favorable` : 9 unsigned);
and it moves `harness/leak_tokens.py`'s R1/R2/R3 derivation, forcing `check_power()`,
`check_rederivation()`, the golden-context re-capture and the negative-corpus re-proof. **Above all it
changes the estimand**: it answers *"does prose completeness help?"*, a different study.

**(b) Keep all 117 rows; split the seven into two mechanically-defined strata, published per arm,
outside the E1 gate.** *Recommended.* This is not a new mechanism — `design/BRIEF.md` §4.3 already
registers an **ambiguity stratum** with the three properties needed: membership is *mechanical, not
declared*; frozen before any pilot artifact is opened; and E1 published **both with and without** the
stratum. In 019 that stratum was empty (the two oracles agreed 117/117), so it never bound.
Membership rules that are derivable at freeze time and do **not** name the rows:

- **S1**: a cell enters iff the arm-A reference reproduces it only with the participation of a pack
  member carrying **no prose-clause provenance**. Requires one new freeze-pinned artifact — a
  per-member provenance table over `reference/refA/pack.json` with `derived: true` where no clause
  exists. On 019's reference it selects exactly the five `x1r-*` rows.
- **S2**: a cell enters iff the arm-A reference's answer depends on an exception conjunct **entailed by
  another clause's guard** — the predicate `design/mutants/ADEQUACY.md` already mechanizes on the Rego
  side as `entailed-guard`. It selects exactly the two `p1-*` rows.

Costs, stated: **nothing in the frozen artifact chain moves** (gold bytes untouched → mutant corpora,
witness tables, pairing 33/69/62, both cuts, `check_gold.py`'s census, V7's six assertions and §4.4, and
E5's stimulus all stand — verified by recomputing pairing with gold held fixed). The E1 *descriptive*
support narrows to 110 rows on grounds known in advance to favour one arm's profile, so both strata
rates are published per arm **with E1's prominence**, and §9 says plainly that the support was chosen on
a known arm asymmetry. And it is **necessary, not sufficient**: perfect-on-110 is A 0.079 / B 0.216 /
C 0.359, so under a 0.60 floor row 3 fires again — which is why §3.3 replaces the floor rather than the
support.

**(c) Delete the seven from gold.** Rejected. Nine JPS mutants go empty-witness (`m-a-040, -042, -044,
-084, -123, -126, -127, -130, -132`; zero Rego), reopening §4's adequacy gate whose last reopening cost
a full review round. `check_gold.py` lines 69–72 errors by design — *"no gold row covers the region the
retired X1 class used to forbid; the repair … is unwitnessed"* — reinstating the epistemic hole round-1
finding R1-2 closed. V7 §4.4's proof is destroyed. And the **E4 denominator moves**: although no shared
group touches any of the seven (verified: 0), pairing is by witness-set *identity*, so deleting rows
**coarsens** the equivalence — re-derived counterfactual **38 shared groups / 78 paired JPS / 71 paired
Rego, cuts 75 and 68** (verified). The primary's denominator, both cuts and the pairing census would all
have to be re-derived.

> **Decision M-3 — keep the seven in gold (recommended), split into S1/S2 by freeze-pinned mechanical
> rules, scored and published per arm, outside the E1 gate.** Sub-decision: are S1/S2 rates gates or
> descriptive-only? Recommendation: **descriptive-only.** A reader may read them as an arm-A penalty;
> that is what they are, and the ledger already signs both rows.
>
> **Decision M-4 — does 020 repair the stimulus (state the region lemma)?** **Recommendation: no.**
> All three design lenses reached this independently. The lemma cost is the finding; repairing it
> silently changes the estimand. If the maintainer wants it, it is a *separate registered study* with
> its own pilot, not a repair bolted onto 020's control.

---

## 6. Calibration under registered conditions

### 6.1 The finding: 019's pilot measured a different population

`design/pilot/pilot_run.py` (lines 130–132) calls codex with **no `env=`**, no `-m`, no
`--ignore-user-config` — inheriting the operator's `$HOME`, `~/.codex/config.toml` and `$HOME/.agents`
skills, none of which are recorded. The same file passes `env=clean_env(workdir)` to *every* jpack and
OPA call (lines 217–388): **the engines were isolated; the model call was not.**
`harness/authoring_call.sh` (lines 44–55) states the channel explicitly — *"skills load from
`$HOME/.agents` and DO reach the model — `--ignore-user-config` alone does not stop them"*.
`design/pilot/NOTE.md` already declared the pilot had no isolation proof; the design phase shipped the
difficulty calibration anyway.

| Observable | Pilot | Registered | Ratio |
|---|---|---|---|
| Arm-A call duration | 1559, 1580, 1660, 1707, 2408 s (+ five slots at the 900 s ceiling, exit 124) | median **199 s**, max **273 s**, `timeoutRate` 0.0 | ~8.5× |
| Arm-B / arm-C duration | B 581–1101 s; C 443–1054 s | B median **74 s**; C median **72.5 s** | ~8–11× |
| Arm-A test rows | 35–49 per run (`design/pilots/…/NOTE.md`) | `caseCount` 16–25, median 21 | 1.7–2.3× |

The sharpest tell: a condition where **every** arm-A call exceeded 900 s cannot be the condition where
**no** arm-A call reached 273 s. Duration fell ~10× while completion bytes fell ~1.5×, which points at
**reasoning budget**, not output volume — and `harness/PINS.json` pins model, CLI version and binary
digest while containing **no reasoning-effort member at all** (verified). The mechanism is a *tight
inference from converging observables, not a measurement*: the pilot's `CALL.json` records no `model`,
no `binarySha256`, no `cli`, so its condition is **unrecoverable**. Model drift over 2026-08-15 →
2026-08-20/21 also cannot be excluded, for the same reason.

Two eliminations matter for the design. **Prompt bytes are not the cause** (three matched sha256 pairs,
verified). **N is not the cause**: under the registered per-arm perfect rates, P(pilot 5/5) is
≤ 3 × 10⁻⁶ (A), 4.7 × 10⁻⁴ (B), 6.0 × 10⁻³ (C). The pilot did not under-sample; it sampled a different
population. Gold's growth 76 → 117 rows explains part of arm A's *depth* of failure and none of its
*existence* (on the piloted 76 rows alone, the registered batch is perfect in A 0/36, B 8/30, C 14/30 —
identical to the all-117 counts in every arm).

### 6.2 An independent second defect: 5/5 never licensed 0.60

`PREREGISTRATION.md` §5 justifies the E1 floor with *"Expected at ceiling in every arm (pilot 15/15)"*.
15/15 is the **pooled** figure; the floor is applied **per arm**, where the evidence was 5/5, whose exact
one-sided 95% Clopper–Pearson lower bound is **0.549 — below the 0.60 it was cited to support**. Even
taking the pilot entirely at face value, the floor was never licensed by its own evidence. Two
independent calibration errors, either sufficient on its own to produce a `control-gate-failed` attempt.

| n | clean sweep | one miss | two misses |
|---|---|---|---|
| 5 | **0.549** | 0.343 | 0.189 |
| 8 | 0.688 | 0.529 | 0.400 |
| 10 | 0.741 | 0.606 | 0.493 |
| **12** | **0.779** | **0.661** | 0.562 |
| 15 | 0.819 | 0.721 | 0.637 |

### 6.3 Registered (proposed): the calibration protocol

- **C1 — one driver.** `design/pilot/pilot_run.py` is **deleted, not ported**. The pre-freeze pilot runs
  through `harness/authoring_call.sh` and `harness/batch.py` under a `--calibration` mode differing from
  the primary batch in exactly three registered ways: output under `calibration/<label>/`, the pilot
  slot count, and `citable: false`. Scoring is `harness/score.py`, unchanged. This makes *"the pilot
  measured the registered condition"* checkable rather than asserted.
  **Freeze-gate consequence (fold in from day one):** 019's `DEVIATIONS.md` D-2 records that
  `manifest_problems()` refused any tree containing prior authoring. 020's freeze gates must **permit
  and require** a `calibration/` subtree at freeze while still refusing any `results/primary-attempt-*`
  — written into the gate *and its test* before the first pilot call, or the pilot becomes un-runnable
  at freeze time and gets moved back outside the harness, which is the 019 failure exactly.
- **C2 — pin the compute condition and bind it.** `harness/PINS.json` gains `codex.reasoningEffort`
  beside `model` / `version` / `binarySha256`; the wrapper passes it explicitly (resolve the exact flag
  empirically at pin time, as `design/BRIEF.md` §4.1 already requires for OPA); `CALL.json` stamps it;
  `harness/transcript_check.py` gate 5 — which already refuses `turn-context-mismatch` on the model
  (lines 603–608) — is extended to the effort field with the same reason tag and the same
  **apparatus-side** classification.
- **C3 — derive the floor, do not choose it, and show it has power.** The house precedent is SCAFFOLD
  item **G3**: `leak_tokens.py` derives the leak screen mechanically *and then proves the derived list
  has power* (`harness/PORTS.md` item 5). Applied here: (i) a committed `calibration/derive_floor.py`,
  sealed before the pilot runs, emitting any threshold from the pilot's own per-arm counts by an exact
  CP rule, with **no human number entering**; (ii) a **minimum viable value declared in advance**, below
  which the study **does not freeze** (descope, repair, or abandon — never register the weaker gate and
  proceed); (iii) a **degradation control**: a deliberately weakened arm run at the same pilot N through
  the same wrapper, which the registered gate **must** fail.
- **C4 — the transfer gate, at decision row 1 (`pipeline-invalid`), not row 3.** A condition mismatch is
  an apparatus fact, not evidence about the arms, and 019's `control-gate-failed: e1-floor` verdict
  actively misleads on this — it reads as *the arms are bad at the task*. Compared against the sealed
  pilot, on observables already captured:

| Observable | Source | Tolerance |
|---|---|---|
| model, CLI version, binary sha256, reasoning effort | `CALL.json`, `session.jsonl` `turn_context` | exact equality |
| sandbox policy, `codexHomeIsolated`, `environmentScrubbed`, isolation inventory | `CALL.json` | exact equality |
| per-arm median call duration | `CALL.json` `startedAt`/`endedAt` | within [0.5×, 2.0×] of the pilot's |
| per-arm median completion bytes | `completion.txt` | within [0.6×, 1.7×] |
| per-arm median `reasoning_output_tokens` | `session.jsonl` | within [0.5×, 2.0×] |

  Bands are set **before** the pilot, from the design brief's own budget model, never after seeing the
  pilot's numbers. Applied to 019, this gate fires on duration alone in every arm (8–11×) and refuses
  the batch at row 1.
- **C5 — one pilot, sealed, append-only re-pilot rule.** The pilot runs once; label, N and output digest
  go into `harness/PINS.json` before the primary attempt. A second pilot requires a `DEVIATIONS.md`
  entry naming the reason, and then **the derived threshold is the maximum over all pilots**, with every
  pilot's rates published side by side — re-piloting is monotone in strictness, removing the incentive
  to shop.

### 6.4 Adjudication: derived floor vs. existence gate (lenses conflict)

The calibration lens wants a **derived per-arm floor** as the registered control gate; §3.2 shows no
per-arm floor on a 019-shaped batch gates anything. **Adjudication: both, at different seats.**

- The **existence gate** (§3.3) is the *registered control gate on the batch*: common-mode, arm-blind in
  intent, immune to the collapse and validity mechanisms that have nothing to do with the stimulus.
- The **derived threshold** (C3) is the *pre-freeze go/no-go on the pilot*: it decides whether 020
  freezes at all, not whether the primary is computed. Deriving-then-proceeding-anyway is result-shopping
  with extra steps, which is why the minimum viable value and the abort/descope branch are registered
  **before** the pilot runs.
- The **degradation control** applies to whichever gate is registered — including the existence gate,
  whose weakness (one lucky run clears it) is exactly what a negative control exists to bound.

### 6.5 Adjudication: pinning effort undermines the dispersion calibration (lenses conflict)

If 020 pins a **higher** reasoning effort to recover pilot-like behaviour, then 019's batch is no longer
condition-matched, and **the MDE table in §4.2 becomes a prior, not a calibration** — the within-arm SDs
(0.068 group / 0.089 mutant) were measured under the *registered* condition. The calibration lens's C2
and the endpoint lens's power table cannot both be taken at face value.

**Adjudication:** pin the effort explicitly, and **re-derive the dispersion from the pilot at the pinned
effort**; use 019's SDs only as a fallback prior and say so in the preregistration. Add a **pre-pilot
effort sweep**, n = 3/arm across two or three settings (~18 calls), published in full — because the
value is the one thing the retained evidence genuinely cannot decide (§8, residual 1).

> **Decision M-8 — pin reasoning effort, and at what value?** Recommendation: **pin it**; choose the
> value from the published pre-pilot sweep. This is the decision the evidence cannot make for the
> maintainer, and it interacts with M-10 (cost) multiplicatively.
>
> **Decision M-9 — calibration protocol C1–C5 as registered machinery**, including: the minimum viable
> derived value; whether a below-minimum pilot **aborts** (recommended) or **descopes**; and what the
> degradation control degrades. Recommendation for the last: the X1-repair-removed reference, whose
> behaviour `design/reference/refA/PACK-CHANGE-001.md` already measures exactly (72 cells changed, 0
> divergences vs refB after repair) — a control whose expected effect is known before it runs.

---

## 7. What carries over unchanged

**Ported by digest (PORTS.md two-sided table), no design change**, all pre-paid by 019's twelve review
rounds: `harness/batch.py`'s ledger, chaining, sealing and `reconcile_ledger()` crash rule; the
arm-interleaved carryover-balanced schedule; `integrity.py`; `transcript_check.py` with its §1a
author-vs-apparatus reason partition; the golden-context capture with two agreeing probes and the
isolation negative control under recorded operator assent; `leak_tokens.py` with its G3
derivation-plus-power discipline; the E4 mutant machinery, both generators, the pairing rule and the
witness-set computation; the sealed reviewer mutant set with its `--include-reviewer-set` two-sided
rule and its "moves nothing" clause; `PINS.json`'s linear anchor order and `registeredLabelRule`
(any null freeze pin ⇒ PILOT ⇒ supports no claim); the exact-set STUDY-MANIFEST scoped per ADR-0004;
`make_manifest.py`'s freeze ceremony; the §1a closed fail-shut partition; the terminality/shortfall
schema; the identity control and the registered per-case input-domain check; §5's **ordered decision
rule structure** (gates above substantive rows; no inferential quantity computed at or above the gate
row; an absent contrast is not a straddling one).

**The 019 deviations, folded in as day-one design requirements:**

| 019 deviation | 020 requirement |
|---|---|
| **D-1** — argv cannot carry a 200 KiB prompt (`MAX_ARG_STRLEN` = 128 KiB); B/C prompts are 204,333 / 206,686 B | **stdin delivery (`< "$PROMPT_FILE"`) from the first commit**, and the pre-freeze smoke drives a **real** exec with the registered prompt sizes, never a stand-in CLI |
| **D-2** — freeze-moment validators wired inside `manifest_problems()` made resume impossible | **gate seats registered from day one**: freeze-moment validators called only from `--check` / `--freeze` / `--freeze-gates`, never from `integrity.verify()`; plus C1's `calibration/` allowance |
| **D-3** — the operator's scratch janitor deleted live slots (the wrapper makes **two** directories per slot) | the **four-newest-entries** janitor rule registered from the start, and the wrapper's directory count documented where the runbook can see it |
| **D-4** — the batch crossed the UTC day | register a **multi-day window up front** (see M-10); crossing is not a stopping rule and should not need an entry |

**What must not carry over:**
1. `design/pilot/pilot_run.py` as a second driver — deleted (C1).
2. `design/BRIEF.md` §4.2 step 3's *"the frozen policy's own pilot rate is registered as not an estimate
   of anything"* — under C3 the pilot rate is the derived threshold's sole input; **that sentence must
   be rewritten**.
3. `PREREGISTRATION.md` §5's *"Expected at ceiling in every arm (pilot 15/15)"* — pooled evidence
   quoted for a per-arm gate.
4. The E1 floor as a bare a-priori constant, and the dichotomised high-kill rate as the decision rule.
5. `cutReachable` as an attainability check (§4.1).

**The asymmetry 019 nearly caught, and 020's single most transferable lesson.**
`PREREGISTRATION.md` §5 says of E4: *"The OC's pilot anchor is not a located operating point any more"*
— the design phase explicitly refused to treat the E4 pilot fractions (A 1/5, B 0/5, C 0/5) as an
operating point, and the E4 outcome was consequently unsurprising and honestly reported. **The same
skepticism was never applied to E1.** 020 applies the E4 anchor rule to every pilot-derived quantity,
or to none.

---

## 8. Cost, and what N buys

Per-call medians from 019's retained `CALL.json` files, registered condition: **A 199 s, B 74 s,
C 72.5 s** — one arm-triple ≈ 5.75 min. Prompt sizes 84,289 / 204,333 / 206,686 B (≈ 4 B/token).
Registered per-call ceiling `callTimeoutSeconds` = **2700**, `timeoutRateCap` = 0.1
(`harness/PINS.json`).

| Component | Calls | Wall clock, sequential, **registered** condition |
|---|---|---|
| Pre-pilot effort sweep (3/arm × 2 settings) | 18 | ~35 min |
| Calibration pilot, 12/arm | 36 | ~69 min |
| Degradation control, 12/arm | 36 | ~69 min |
| Primary batch, 50/arm (019 scale) | 150 | ~4.8 h |
| Primary batch, **60/arm** | 180 | ~5.8 h |
| Golden probes + isolation negative | 3 | minutes |

**The compute-condition decision multiplies this.** At *pilot-like* durations (completed-call medians
A 1660 s, B ~818 s, C ~757 s) one arm-triple is ~51 min, so 60/arm is **~51 h sequential — over two
days** — and 12/arm pilot is ~10 h. The registered 2700 s ceiling still covers the pilot's slowest
observed call (2408 s), but the batch window does not. **M-8 and M-10 must be decided together.**

**Realised n, from 019's actual loss profile.** Apparatus loss was **24% / 26% / 22%** of slots
(A: 9 `registry-mismatch`, 2 `slot-shape`, 1 `transcript-refused`; B: 11 `slot-shape`, 1
`post-call-failure`, 1 `transcript-refused`; C: 11 `slot-shape`) — the `slot-shape` mass is D-1/D-3 and
is pre-paid. Authoring invalidity is **not** repairable and is real: B lost 11/37 and C 9/39 to
`opa-check-failed` / `unparseable-artifact`. Identity failures: A 2/36, B 4/30, C 2/30. E4-scoreable n
in 019 was **34 / 26 / 28** from 50 attempted.

At **N = 60/arm** with D-1/D-3 fixed, expect realised E4-scoreable n ≈ **50 / 35 / 40**, i.e. a group-level
MDE of roughly **0.038–0.043** unadjusted and **0.028–0.032** size-adjusted — ~1.3 groups of 33. At
019's N = 50 it is ~0.043 / 0.032. **Recommendation: N = 60/arm, pilot 12/arm.** If the maintainer
keeps 019's scale, the MDE table (§4.2) is registered in the preregistration so the coarseness is
stated rather than discovered.

> **Decision M-10 — N per arm (recommendation 60), pilot N (recommendation 12, which matches the gate's
> per-arm denominator and tolerates one miss at CP-lower 0.661), and the registered batch window
> (recommendation: 3 UTC days, decided up front rather than by deviation).** Under a high-effort pin,
> reconsider N: 60/arm may be a ~2.5-day batch.

---

## 9. Where the lenses disagreed, and how this brief ruled

| Question | Positions | Ruling |
|---|---|---|
| Are the seven rows one class? | endpoint lens: one block; gold lens: S1 (5, region lemma) + S2 (2, inert O3) | **Gold lens.** V7 §3.4 A6 names **five** rows; the two `p1-*` rows fail `retired_x1` on their own inputs (verified) and carry V8-10's signature. §5.1 |
| E1's replacement | endpoint: existence gate, no rate floor ever; gold: strata + re-specify (or move the gate to the identity control); calibration: derived per-arm floor with power check | **Layered.** Existence gate registers on the batch; the derived threshold governs the pre-freeze go/no-go; the degradation control applies to whichever gate registers. §6.4 |
| E4 primary form | endpoint: continuous group-level, permutation, ANCOVA; gold: "decide between dichotomy and kill rate"; calibration: silent | **Endpoint lens**, with two disclosures the lens did not make: the any/all group-kill rule must be registered, and §5's registered sentence *"a group-level pairing does not equalise the per-arm denominators"* is contradicted and must be addressed in 020's own text. §4.2 |
| Repair the prose? | endpoint: no; gold: defer to a pilot, don't couple to E1; calibration: re-measure before re-authoring | **Unanimous: no.** §5.2(a) |
| Does 019 calibrate 020's power? | endpoint: yes (SDs, MDEs); calibration: 019's condition is itself suspect | **Conditional.** Valid only if 020 runs at 019's compute condition. If effort is pinned higher, §4.2's SDs are a prior and dispersion is re-derived from the pilot. §6.5 |
| Arm-labelled E4 quantities | endpoint: withheld deliberately; gold: printed them | **Neither.** The printed figures do not re-derive, and withholding after computing is what 019's refusal text forbids. Disclosed here; disposition is M-1. §2.2 |
| Issue #88's counts | endpoint and gold and calibration all: do not reproduce, by three independent recomputations | **Unanimous, and confirmed here.** §2.3 |

---

## 10. What this brief does not decide

Every open decision, in one place. Defaults are taken at preregistration time unless the maintainer
objects; nothing below is registered by this document.

| # | Decision | Recommendation |
|---|---|---|
| **M-1** | May 020 read arm labels from 019's batch, and what happens to the arm-labelled E4 quantities a design lens already computed? | Arm-blind design inputs; **publish** the arm-labelled E4 kill fractions as part of 019's R2 disposition |
| **M-2** | E1's kind: rate floor / trimmed perfection / two-tier / **existence gate** / no author-side gate | Existence gate (≥1 run ≥0.95 agreement per arm) + fully descriptive E1 |
| **M-3** | Keep the seven rows in gold and split them into S1/S2 strata outside the gate? Gates or descriptive-only? | Keep, split, **descriptive-only** |
| **M-4** | Repair the stimulus (state the derived region lemma)? | **No** — separate study, own pilot |
| **M-5** | E4 primary form; the any/all group-kill rule; whether δ is registered at all | Continuous group-level (33), permutation interval, `caseCount` ANCOVA with the unadjusted difference beside it |
| **M-6** | If a dichotomy survives descriptively, what fixes τ? | Attainability rule: cut = ⌈0.75 × union-kill ceiling of the reference-derived suite⌉, refusing if it exceeds the ceiling |
| **M-7** | `caseCount`: covariate / stratifier / descriptive-only / fix suite size in the prompt | Registered covariate + size-balance check + registered non-claim if imbalanced; **do not** fix suite size |
| **M-8** | Pin reasoning effort — and at what value? | Pin it; choose from a published pre-pilot sweep (n=3/arm × 2–3 settings). **The one decision the evidence cannot make.** |
| **M-9** | Calibration protocol C1–C5; the minimum viable derived value; abort vs descope below it; what the degradation control degrades | Adopt C1–C5; **abort-and-repair** with the pilot published; degrade via the X1-repair-removed reference |
| **M-10** | N per arm; pilot N; batch window; interaction with M-8 | 60/arm, pilot 12/arm, 3 UTC days registered up front |
| **M-11** | Correct issue #88 before it is cited anywhere | Correct it; §2.3 carries the reproducible figures |
| **M-12** | Publish 019's blocked descriptive content (union ceilings, single-witness fractions, never-killed group identities, the E1 mechanism split, the B/C collapse mechanism) as **019 R2 content**, or fold it into 020's design record? | **Publish as 019 R2** under §10's commitment — row 3 blocked *inferential* quantities, not the failure map |
| **M-13** | Strengthen the identity control to run the author's tests against the author's **own** policy? Nothing in 019 did this, which is how `run-011` reached `identityPass: true` with 86/117 rows wrong | Worth a decision. Adds one engine invocation per run and **changes what "identity" means** — a registered change, not a repair |
| **M-14** | Is the B/C collapse (20/30 and 13/30 runs at 86–104 misses) an **input-shape contract miss in the prompt** (fix it) or a **U1 comprehension failure** (the study's actual finding)? | **Read this before the 020 brief is registered**: one focused pass over `arms/B/authoring/run-011/` (86 misses) against a perfect arm-B run. If it is a contract miss, 020 fixes a prompt defect; if it is comprehension, 020 must not |

---

## 11. What 020 will not be able to show

Everything 019 §9 registers still binds and is carried verbatim: fidelity and pinning power are
measured **within the JPS-expressible fragment, selected by arm A's expressive envelope and no other
criterion** (V8-30, `A-favorable` by construction); Study 003's census says that fragment does not
cover real business decisions. Single-shot authorship only — no outcome is evidence about tooled
authoring workflows. One model, one policy family, one prompt per arm. Unless a prevalence gradient is
measured, no direction separates representation from training familiarity, and both directions are
reported as confounded. The joint-reading prohibition holds: no tradeoff statement combining the
expressiveness census with any rate is licensed. An INDETERMINATE or unsupported contrast licenses no
negation. The gold suite is two authors deep, not independent of the program.

Three ceilings are **new to 020** and must be registered in its own §9:

1. **The E1 support is chosen on a known arm asymmetry.** S1/S2 exist because arm A pays for them.
   That is disclosed, published per arm, and it bounds every statement made on the 110-row support.
2. **The primary's estimand changed from 019's**, and it changed after 019's outcome was known. The
   change is defended on **arm-blind** grounds (attainability, lattice equalisation, dispersion,
   suite-size confounding) — but a reader is entitled to know it happened, and 020 says so where the
   endpoint is defined, not in a footnote.
3. **019's pilot condition is unrecoverable.** No `model`, `binarySha256` or `cli` member exists in any
   pilot `CALL.json`. C2 closes this prospectively for 020; nothing can close it retrospectively for
   019, and the reasoning-budget mechanism in §6.1 remains a tight inference from four converging
   observables, **not a measurement**.