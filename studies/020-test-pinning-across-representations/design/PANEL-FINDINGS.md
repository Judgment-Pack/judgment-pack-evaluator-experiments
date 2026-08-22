# Panel findings on Study 020 design brief v1 (verbatim)

Three adversarial lenses (statistics; construct validity; operational feasibility) read
`design/BRIEF.md` v1 on 2026-08-21, each instructed to recompute every figure from 019's
retained records rather than trust the brief's own derivations. Their findings are
reproduced verbatim below, deduplicated across lenses, renumbered globally, and ordered
[BLOCKER] → [MAJOR] → [MINOR]; where two lenses reached the same defect the stronger
statement is kept and the agreeing lens is named with whatever additional evidence it
carried.

---

## BLOCKERS

**[BLOCKER] #1 (§2.2, §9 ruling row "Arm-labelled E4 quantities", M-1) — The brief's central disclosure claim is false: the gold lens's figures re-derive exactly, and by asserting they do not, the brief has published the arm-labelled A−C direction while telling the maintainer it has not.**

*Lens: STATISTICS. CONSTRUCT (CV#3) reached the same finding independently, computing the same triple and adding that §2.2 uses "they do not re-derive" to soften M-1, so the maintainer is being asked to dispose of quantities the brief has mischaracterised as unreliable when they are the registered endpoint computed on the registered denominator — and they point A **below** C, the direction 019 refused to publish.*

Evidence: the brief says "**They do not re-derive.** Among identity-passing runs the paired kill-fraction means are *different numbers in every arm* than that lens reported." I recomputed the mean of `kill.killedPaired / kill.paired` over the **artifact-bearing** cohort (every run carrying a `kill` block, n = 36 / 30 / 30 — 019's own `e2.*.artifactAdmitted` cohort):

```
A 0.60627   B 0.59032   C 0.61613
```

which is the gold lens's "A 0.606 / B 0.590 / C 0.616" to three decimals. The brief compared against the identity-passing cohort (A 0.6419 / B 0.6811 / C 0.6601), found different numbers, and concluded non-reproducibility. This is the same defect the brief convicts issue #88 of, in §2.3, one page earlier.

Worse, the consequence is not cosmetic. The figures are correct, so §2.2 has printed A−C = −0.0098 and A−B = +0.0159 into the design record. And the endpoint choice §4.2 recommends **flips that sign**: group-level A−C is **+0.0065** (artifact-bearing) and **+0.0409** (identity-passing) against mutant-level A−C of **−0.0098** / **−0.0182**. So M-1's premise — "§3–§5 were all derived arm-blind, so (a) costs nothing analytically" — is untrue: the brief selected between two endpoint forms that disagree in sign on the registered primary contrast, after the arm-labelled quantities existed.

Cure: withdraw the "do not re-derive" sentence and the §9 ruling row; state the cohort and the reproduced figures; and re-pose M-1 as what it now is — the primary contrast's *direction* is known to the design phase under one endpoint form and its *sign reverses* under the other, so either (c) with a published 019 amendment, or an independent arm-blind justification of group-vs-mutant level that does not depend on any 019 run outcome.

---

**[BLOCKER] #2 (§4.2, "Registered (proposed): a continuous, group-level, size-adjusted primary")** — The move from a mutant-level to a group-level estimand is presented as a technical repair ("the pairing construction being used for what it was built for"), but on 019's own batch it reverses the sign of the registered primary contrast and flips its verdict from null to significant, so the brief's central design choice is outcome-determinative and was made after the outcome was knowable.

*Lens: CONSTRUCT. STATISTICS #1 records the same sign reversal from the design-record side.*

*Evidence.* Reconstructing the 33 shared witness groups from `mutants/MANIFEST-{jps,rego}.json` (reproduces 33 / 69 / 62 exactly) and scoring the 88 identity-passing runs from `RESULTS.json.perArmRuns[].kill.survivorsPaired`:

| estimand | A | B | C | A−C | exact permutation p (20k) |
|---|---|---|---|---|---|
| mutant-level paired kill fraction (019's scored quantity) | 0.6419 | 0.6811 | 0.6601 | **−0.0182** | 0.460 |
| group-level kill fraction (020's proposal) | 0.6176 | 0.5991 | 0.5768 | **+0.0408** | **0.0195** |

The re-weighting alone — 69 JPS mutants collapsed into 33 groups, 62 Rego into the same 33 — moves A−C by 0.059 and carries it across the α = 0.05 boundary. §11 ceiling 2 concedes only that "the estimand changed after 019's outcome was known… defended on arm-blind grounds"; it does not disclose that the two estimands disagree in direction and in decision on the only batch in evidence, which is a ten-line computation over retained files.

*Cure.* Register the level (mutant vs group) as a **pre-declared, published sensitivity pair**: R1 is decided on one, both are reported, and the preregistration prints the 019 disagreement above as the reason the choice is load-bearing. If the group level is chosen, §11 must state that the choice, not the treatment, supplies the sign observed in 019.

---

**[BLOCKER] #3 (§4.2, "Registered covariate: `caseCount`"; §4.2 R1)** — R1's registered sentence names "the difference in means" without saying whether the decision reads the ANCOVA-adjusted or the unadjusted difference, and on 019's batch the two give opposite verdicts.

*Lens: CONSTRUCT. STATISTICS #11 reached the same finding ("Two co-primary quantities, no precedence rule"), adding that nothing in §4.2, §4.2's R1 statement, or M-5 says which one R1 reads if one excludes 0 and the other does not, and that 019's §5 discipline ("an absent contrast is not a straddling one") gives no answer here; its independent adjustment put A−C at +0.0149 against the +0.0161 below.*

*Evidence.* Within-arm `caseCount` slope re-derived at +0.0233 group-kill fraction per case (matches the brief). Applying that slope as an ANCOVA adjustment to the same 88 runs: adjusted means A 0.6106 / B 0.5893 / C 0.5945, so **adjusted A−C = +0.0161** against **unadjusted A−C = +0.0408**. The brief's own precision table puts the size-adjusted MDE at n≈34 at 0.034: the unadjusted difference clears it and the adjusted one does not. R1's text says only "differs from arm C's"; the covariate bullet says "the unadjusted difference published beside the adjusted one" — two estimands, one claim sentence, and a live disagreement. (At the mutant level the split is wider still: adjusted A−C = −0.0532 vs unadjusted −0.0182.)

*Cure.* Put the adjusted-vs-unadjusted choice **inside R1's sentence**, not in a covariate bullet, and register the other as descriptive with an explicit "no decision reads it" clause of the R1-15 kind the brief already invokes for δ.

---

**[BLOCKER] #4 (§4.2 "Registered covariate: `caseCount`", M-7) — The primary adjusts away a post-treatment variable the brief itself defines as part of the construct, and the "size-balanced, so this is variance not bias" defence is refuted by the brief's own slope.**

*Lens: STATISTICS.*

Evidence: M-7 states *"how many cases a representation leads an author to write is part of the construct 'what the suite pins down'"* and recommends not fixing suite size. `caseCount` is measured on the authored artifact — strictly post-treatment. ANCOVA on it estimates a **controlled direct effect** holding suite size fixed, not the total effect the question asks about; adjusting a post-treatment mediator is a standard bias mechanism, not a precision device.

The empirical claim is also wrong. The brief cites medians (21 / 20.5 / 20) for balance. The **means** are A 20.94 / B 21.00 / C 19.82. With the brief's own slope b = +0.0233 group-kill fraction per case, the adjustment moves the A−C contrast by 0.0233 × 1.116 = **0.026** — 57% of the brief's n = 34 MDE (0.046) and **74% of its n = 60 MDE (0.035)**. On the identity-passing batch, unadjusted A−C = +0.0409 and adjusted A−C = +0.0149, a 63% change in the primary quantity. That is a bias problem in the very batch cited as balanced.

Cure: either register the unadjusted total-effect difference as the primary and `caseCount` as descriptive/mechanistic (with the mediation decomposition published), or register the direct effect explicitly as a *different* estimand from the question in §1 and rewrite §1 to match. Register balance on means with a stated test and threshold, not on medians. Do not register both under one R1.

---

**[BLOCKER] #5 (§4.2 precision table, §8, §7 "What carries over unchanged") — The MDE table is computed on a cohort the brief simultaneously registers out of existence; on the denominator rule §7 carries over verbatim the MDE is 3.7× larger, and the primary as written has no defined value on 26 of 114 runs.**

*Lens: STATISTICS. CONSTRUCT (CV#9) and OPERATIONAL (OP-5) reached the same finding independently. CV#9 adds the per-arm group-level SDs on the registered denominator (A 0.1528 / B 0.2148 / C 0.1603 — 2.2–2.9× the identity-passing figures, so the registered-population MDE at n = 60 is roughly 0.09, not 0.035) and notes that §8's "realised E4-scoreable n ≈ 50/35/40" quietly adopts the narrower population without registering it as a change to 019's denominator rule. OP-5 adds that beyond the 18 runs with no `kill` record at all (A 2 / B 7 / C 9), a further 6 (B run-026/027/032/036, C run-035/050) carry `killedPaired`/`paired` with **no `survivorsPaired`**, so they have no group vector even in principle, and that zero-filling rather than dropping shifts an arm's mean by ≈ 0.11 (arm B) and ≈ 0.14 (arm C) against a registered MDE of 0.035 — hence its cure also requires the scorer to emit a per-mutant survivor vector for every run that has any kill record at all.*

Evidence: §7 ports "§5's **ordered decision rule structure**" and 019's §1a partition unchanged, and 019's registered E4 denominator rule is explicit (`RESULTS.json.e4.A.denominatorRule`): *"admitted runs (attempted runs whose apparatus succeeded). Authoring outcomes stay in as not-high-kill and **identity-control exclusions stay in** and are reported; only apparatus codes leave"* — hence `e4.{A,B,C}.denominator` = 38 / 37 / 39, and `OC-TABLE.md` §8 restates it. The brief's SDs are from the identity-passing cohort (n = 88). Pooled within-arm SD of the group-kill fraction, by cohort:

| analysis set | n | pooled within-arm SD (group) | MDE, n=34 | MDE, n=60 |
|---|---|---|---|---|
| identity-passing (brief's, unbiased) | 88 | 0.0694 | 0.047 | 0.035 |
| admitted **with** a `kill` block | 90 | 0.1140 | 0.077 | 0.058 |
| registered §1a/§5 denominator (114; no-artifact = 0) | 114 | **0.2543** | **0.173** | **0.130** |

The brief's own "Observed per-run group kills across the batch: 12–25 of 33" is likewise the identity-passing range; on the registered denominator it is **0–25**.

And the deeper problem: 019 gave every non-identity-passing run `highKill: null` (verified — `null` for all 26, `false` for all 88) while keeping it in the denominator. A dichotomy can absorb that; **a mean cannot**. The brief never registers an analysis set for the continuous primary at all.

Cure: register the E4 analysis set explicitly and state the deviation from §1a if it narrows to identity-passing; recompute the entire §4.2 precision table and §8's N recommendation on whatever set is registered; if the §1a rule is kept, say so and publish MDE ≈ 0.13 at N=60 rather than 0.035.

---

**[BLOCKER] #6 (§4.1 "an attainability gate with teeth") — The proposed replacement for `cutReachable` is vacuous in exactly the same way, and would have passed 019's unattainable cut.**

*Lens: STATISTICS. CONSTRUCT (CV#5) reached the same finding independently, noting that the brief's own §4.1 evidence (union of all identity-passing runs: 61/69 and 54/62) is a fact about* authored *suites, which the gate as worded does not read; its cure specifies the probe concretely — a registered attainability probe of a fixed size drawn from the reference (a k-case suite, k = the design's expected `caseCount` median), with the probe's realised union ceiling published, and any τ above it refused.*

Evidence: the rule is *"any cut used anywhere must be ≤ the union-kill ceiling attained by the **reference-derived gold suite**"*. But the adequacy gate defines adequacy as killed-by-gold: `adequacy.disposition` is `killed-by-gold` for **157/157** adequate JPS mutants and **150/150** adequate Rego mutants. The reference-derived gold suite therefore has union-kill ceiling 69/69, 62/62, and 33/33 groups **by construction**. τ = 19/20 gives 66 ≤ 69 and 59 ≤ 62 — the new gate passes. It is arithmetically identical to the `cutReachable: true` check (66 ≤ 69) the brief calls vacuous.

Cure: anchor attainability on something an *authored* suite can reach — e.g. a registered pre-freeze attainability probe of k independent suites with the cut required ≤ their observed union ceiling, or a cut derived from the size-constrained coverage bound (see #14), and register the refusal branch with its own N.

---

**[BLOCKER] #7 (§4.2 secondary τ, M-6) — The recommended descriptive τ rule and the number it is illustrated with are two different rules; the rule as written produces a cut reached by 1 of 88 runs, and the illustrated number is derived from the batch the rule forbids reading.**

*Lens: STATISTICS. CONSTRUCT (CV#8) reached the same finding independently, adding that at τ = 21 the arm-labelled high-kill rates on 019 are A 20/34, B 10/26, C 8/28 — precisely the kind of separation §2.1 forbids using to fix a cut — and that the 21 figure must be withdrawn along with the run-derived ceiling it used.*

Evidence: the rule is `⌈0.75 × union-kill ceiling of the reference-derived suite⌉`. By #6 that ceiling is 33/33, so the rule yields **⌈24.75⌉ = 25** groups. The brief says "On 019's corpus that lands near **21/33** groups — inside the observed support (12–25)". 21 = ⌈0.75 × **28**⌉, i.e. the ceiling of the *019 identity-passing batch's union*, not of the reference-derived suite — and the same bullet requires the rule be "registered **before** the batch". Recomputed group-kill distribution over the 88 identity-passing runs: `{12:1, 13:2, 15:1, 16:3, 17:6, 18:8, 19:12, 20:17, 21:21, 22:9, 23:7, 25:1}` — **exactly one run reaches 25**, and 38 reach 21. So the rule as literally written recreates 019's near-unattainable cut; the illustrated 21 is only attainable because it was read off the batch.

Cure: pick one. If the anchor is the reference-derived suite, publish 25/33 and its 1/88 attainment; if the anchor is an attainability probe, register the probe and its N. Do not carry a rule whose worked example uses a different ceiling than the rule names.

---

**[BLOCKER] #8 (§6.3 C3(iii) and M-9, the degradation control)** — The recommended degradation control provably cannot fail the gate it exists to bound: under the X1-repair-removed reference, the §3.3 existence gate still holds in all three arms.

*Lens: CONSTRUCT. OPERATIONAL (OP-3) reached the same finding by independent arithmetic: recomputing `check_gold.py`'s `retired_x1` over `gold/GOLD.json` selects exactly **5 of 117 rows**, so a run that is perfect against the true prose scores **112/117 = 0.957 ≥ 0.95** and clears the gate the control "**must** fail". OP-3 adds that the reference is not in the stimulus at all — a reference-only rule id appears 5 times in `reference/REFERENCE-A.md` and **0 times in `arms/A/PROMPT.txt`** — so removing the repair regresses gold, not the prose/prompt-assembly channel §3.3 names, and it needs no model calls, so §8's 36-call / ~69-min line buys a re-scoring.*

*Evidence.* `refA/PACK-CHANGE-001.md` records 72 of 236,196 cells changed, "72/72 inside" the retired-X1 predicate; `V7-COMPLETENESS.md` §3.4 A6 puts exactly **5** gold rows inside that region. Removing the repair therefore moves at most 5 of 117 gold rows, and moves them to `unresolved:[unknown]` (PACK-CHANGE §2: the un-repaired pack's D8 negation cascade is UNKNOWN there). Re-scoring every run's `goldFailures` against repair-removed gold gives the per-arm **best** run:

| arm | min misses now | min misses under the degraded reference | agreement | gate (≥0.95 ⇒ ≤5 misses) |
|---|---|---|---|---|
| A | 2 | **2** | 0.9829 | holds |
| B | 0 | **5** | 0.9573 | holds |
| C | 0 | **5** | 0.9573 | holds |

Arm A is unchanged because the degradation makes arm A's dominant failure mode (27 of 36 runs answer `unresolved:[unknown]` on all five `x1r-*` rows) *correct*: a run that misses 7 rows today misses 2 under the degraded reference. The control is not merely weak, it is anti-correlated with the gate in the arm the gate is least able to protect. This is exactly the failure the program's standing *mutation-check every safeguard test* lesson names, committed inside the paragraph that invokes it.

*Cure.* Register a degradation that acts on the **stimulus** (the shared prose header, the prompt assembly, or the naming appendix) — the common-mode threat §3.3 actually claims to detect — and require the preregistration to publish the computed miss-count shift the degradation induces, per arm, before the pilot runs.

---

**[BLOCKER] #9 (§6.3 C1; §7 "carries over unchanged")** — The pre-freeze calibration pilot cannot run through the registered wrapper at all, because the wrapper refuses while `codex.model` is null and `codex.model` is a freeze pin filled *after* the pilot.

*Lens: OPERATIONAL.*

*Evidence.* `harness/authoring_call.sh:203` — `if [ -z "$PINNED_MODEL" ] || [ "$PINNED_MODEL" = "None" ] || [ "$PINNED_MODEL" = "null" ]; then` → refuse; its header at lines 23–24 registers this ("a NULL registry model refuses"). `PINS.json`'s `registeredLabelRule` lists `codex.model (model)` among the eighteen freeze-set members. C1 requires the pilot to run "through `harness/authoring_call.sh` and `harness/batch.py`"; C2 adds `codex.reasoningEffort`, whose value comes from a pre-pilot sweep that must itself run through the same wrapper before that pin exists. §7 meanwhile lists "`PINS.json`'s linear anchor order and `registeredLabelRule`" among the items ported with **no design change**. C1's claim of "exactly three registered ways" the calibration mode differs is false: the pin state is a fourth, and it is load-bearing.

*Cure.* Register which pins are `resolvedAtDesignTime` (model, reasoningEffort) versus freeze pins; restate `registeredLabelRule` with the new member and its null-⇒-PILOT test; move `registeredLabelRule` out of §7's unchanged list; make the pilot's pin state the registered fourth difference.

---

**[BLOCKER] #10 (§6.3 C2)** — The reasoning-effort pin has no transcript witness at the pinned CLI, so gate 5's extension is either vacuous or refuses every call.

*Lens: OPERATIONAL.*

*Evidence.* `turn_context.payload` in `arms/A/authoring/run-001/session.jsonl` carries exactly `[approval_policy, approvals_reviewer, collaboration_mode, comp_hash, current_date, cwd, file_system_sandbox_policy, model, multi_agent_mode, multi_agent_version, permission_profile, personality, realtime_active, sandbox_policy, summary, timezone, turn_id, workspace_roots]` — no effort member. The only occurrence in the whole transcript is `collaboration_mode.settings.reasoning_effort: null`, an override slot, null in the registered batch. `transcript_check.py:604-608` is `named = {context.get("model") for context in contexts if "model" in context}` / `if named and named != {model}`: transcribed to a present-but-null field it yields `{None} != {"high"}` → `turn-context-mismatch` on every call; transcribed to an absent field the guard never fires. Either way the pin is a CALL.json self-report with no independent witness — the brief registers the empirical resolution step for the *flag* ("resolve the exact flag empirically at pin time") and not for the *witness*.

*Cure.* Register the witness resolution as its own pin-time step that refuses if no non-null transcript member exists after the flag is set, and register explicitly what `CALL.json` alone may be taken to prove if none does.

---

## MAJORS

**[MAJOR] #11 (§4.2 "roughly an order of magnitude more resolution") — The headline justification for dropping the dichotomy compares two incommensurable scales; on a common scale the gain is ~1.1–1.4×.**

*Lens: STATISTICS.*

Evidence: 0.20–0.30 is a gap in the **high-kill run rate** (`OC-TABLE.md` §4/§6); 0.035–0.046 is a difference in **mean group-kill fraction**. Converting the dichotomy's registered middle-of-range MDE to a mean shift under the batch's own dispersion (σ = 0.0694, τ at arm C's median so p_C = 0.5):

| dichotomy run-rate gap | equivalent mean shift |
|---|---|
| 0.20 | 0.0364 |
| 0.25 | 0.0468 |
| 0.30 (OC §6, N=50 middle) | 0.0584 |

against the continuous MDE of 0.0419 (n = 43/43) or 0.0412 (n = 50/40). Ratio ≈ **1.1–1.4×**, and near the unit-interval boundaries `OC-TABLE.md` §6 shows the dichotomy doing *better* (gap 0.20 at p_C = 0.95). 019's E4 failure was the unattainable τ (#6), not the dichotomy.

Cure: replace the claim with the common-scale comparison, or drop the resolution argument and defend the continuous endpoint on the grounds that actually hold (no τ to make unattainable; no information discarded).

---

**[MAJOR] #12 (§2.1) — The arm-blindness rule is not enforceable as stated and §3–§5 violate it, contrary to the sentence that says they do not.**

*Lens: STATISTICS. CONSTRUCT (CV#7) reached the same finding on the §3.3 threshold specifically: arm A's minimum miss count is 2, at ≥0.99 (≤1 miss) the gate fails arm A, at ≥0.95 (≤5) it clears with 3 misses of headroom — "the threshold sits in the only interval that admits arm A, and the disqualification table in §3.2 that motivates it is entirely arm-labelled." Its cure: derive the threshold arm-blind (from the pooled miss distribution, or from the sealed pilot under C3's `derive_floor.py` with no human number entering) and publish the arm-labelled check as a post-hoc verification, explicitly marked as not having chosen the value.*

Evidence: §2.1 claims "Everything in §3–§5 of this brief was derived under that rule." It was not.
- §3.2 is a fully arm-labelled A/B/C table and is the sole basis for M-2's disqualification of every floor variant.
- §3.3 justifies the existence gate by "On 019's batch this gate holds in all three arms (A 115/117 = 0.983; B and C 117/117)" and picks the 0.95 threshold against arm A's tail. Arm A's miss counts are `[2, 5, 5, 7, 7, ...]`: 0.95 (≤5 misses) is cleared by **3 of 36**; 0.96 (≤4) by **1**; 0.98 by **1**. The threshold sits in the only window with more than one clearing run.
- §4.1's "union of all identity-passing **arm-A** suites" is arm-labelled outright, and the carve-out for "per-language corpus structure" cannot help: JPS ≡ arm A, so *every* per-language quantity is an arm-A quantity by construction.
- §4.2's size-balance claim uses per-arm medians.

Cure: either restate the rule as "no quantity that is a function of the **primary outcome** may be arm-labelled" (which still excludes §4.1's per-run unions) and re-derive §3.3's threshold from a source outside the batch, or drop the claim in §2.1 that §3–§5 satisfied it and disclose each place they did not.

---

**[MAJOR] #13 (§3.3, §6.4, C3(iii)) — The existence gate's operating characteristics are never computed, and the degradation control is run at an N where it cannot certify the gate at batch N.**

*Lens: STATISTICS.*

Evidence: the gate is a max statistic, so its stringency is monotone in realised n — which differs by arm (34 / 26 / 28 in 019). At arm A's observed per-run clear rate (3/36 = 0.083 → 0.079 on the ITT denominator):

| per-run clear rate | P(gate fires), n=12 | n=43 | n=50 |
|---|---|---|---|
| 0.079 (019 arm A, undegraded) | 0.372 | **0.029** | **0.016** |
| 0.040 (2× degradation) | 0.613 | 0.173 | **0.130** |
| 0.020 (4× degradation) | 0.785 | 0.419 | **0.364** |
| 0.010 (8× degradation) | 0.886 | 0.649 | 0.605 |

Two unstated facts: (a) the gate spuriously refuses arm A with probability 1.6–6.1% at 019-scale N even with a perfect stimulus; (b) C3(iii)'s degradation control at 12/arm fires at 61–79% for degradations against which the gate at 43–50/arm fires at 13–36%. **A degradation the control catches will be missed by the registered gate**, so "the degradation control must fail the gate" does not establish the gate has power — it establishes the opposite unless the control is run at batch N.

Cure: register the gate's OC table (clear-rate × n), register the degradation control at the batch's realised n or state the arithmetic gap explicitly, and register the minimum degradation the gate is claimed to detect at the registered N.

---

**[MAJOR] #14 (§4.2, sub-decision (i)) — The any/all rule is not a choice: it is provably degenerate, and what that reveals is that the proposed primary measures test-input coverage, not pinning power.**

*Lens: STATISTICS. CONSTRUCT (CV#10) independently confirmed that the any-rule and all-rule group counts are identical on all 88 scored runs; see #15 for its distinct finding about what that coincidence hides.*

Evidence: `gall != gany` in **0 of 114** runs. This is structural, not empirical: a group is an equivalence class under *identical witness set*, and for an identity-passing run every case carries the reference answer, so a suite kills every member of a group or none. The primary therefore reduces exactly to "what fraction of the 33 witness-set classes does the suite contain an input for" — assertions never enter. Two consequences the brief should register rather than leave as an open sub-decision:

- Registering the any/all rule as a live estimand choice signals it was not checked; and the reduction is conditional on identity-pass, which is precisely the cohort question left open in #5.
- Greedy set cover over the 51 distinct witness inputs needs **21 specific gold inputs** to reach 33/33, against suites of 16–25 cases. So the endpoint is a near-deterministic function of suite size and input choice — the I4 confound is not a nuisance to adjust away, it *is* the endpoint. This is why #4's ANCOVA cannot separate the two.

Cure: state the equivalence and its condition; drop sub-decision (i); and either re-derive an endpoint that reads assertions (so "pinning" is measured, not coverage) or rename the construct in §1 and the study slug to what is actually measured.

---

**[MAJOR] #15 (§4.2, "This retires V8-22"; M-5 sub-decision (i))** — Group-level scoring equalises the denominator but not the unit, so V8-22's asymmetry is relocated rather than retired, and the any/all rule that determines its direction cannot be calibrated on 019's batch because the two rules coincide on every run.

*Lens: CONSTRUCT. STATISTICS #18 reached the same finding and adds two facts its cure needs: the retirement holds only under the condition that kill ⇔ witness coverage, which is true* for identity-passing runs *(see #14) — a condition #5 leaves unregistered — and §4.2 still registers for publication the single-witness fractions (28/69 vs 20/62) and I4's mutant-level slope (+0.033), both on the unequal lattices V8-22 names, so V8-22 must stay live for those quantities.*

*Evidence.* Of the 33 shared groups, **20 have unequal member counts across languages** — 13 JPS-heavier, 7 Rego-heavier (extremes: `d7-39-100k` 6 JPS vs 3 Rego; `d1-match|…` 1 JPS vs 4 Rego). Under the **all** rule arm A must kill six mutants to score a unit where arms B/C kill three; under the **any** rule the advantage inverts. Neither rule is language-neutral, so "the same denominator, the same lattice and the same union ceiling" does not entail the same estimand for both languages. And the sub-decision cannot be settled empirically here: on all 88 scored runs the any-rule and all-rule group counts are **identical**, so groups die atomically in this batch and it supplies no evidence about a rule whose asymmetry only appears when they do not.

*Cure.* Register the group-kill rule together with a published per-group member-count table for both languages and an explicit statement of which arm the chosen rule favours; add the group-size imbalance as a ledger row rather than recording V8-22 as retired.

---

**[MAJOR] #16 (§4.2 ANCOVA) — `caseCount` is missing for 6 admitted runs and the missingness is differential by arm; no missing-data rule is registered.**

*Lens: STATISTICS.*

Evidence: admitted runs carrying a `kill` block but no `caseCount`: B `run-026`, `run-027`, `run-032`, `run-036`; C `run-035`, `run-050` — all `unparseable-artifact`; **arm A has zero**. Under a complete-case ANCOVA these 6 leave the analysis, which changes the analysis set arm-differentially and interacts with #5.

Cure: register the rule (complete-case with the loss published per arm, or a defined `caseCount` for unparseable suites, or exclusion at the admission stage), and register the resulting per-arm n before the freeze.

---

**[MAJOR] #17 (§4.2 R1) — "The exact permutation interval on the difference in means" is not exact under the design as specified.**

*Lens: STATISTICS.*

Evidence: two distinct problems. (a) With a post-treatment covariate in the model, the sharp null of no effect on the outcome does not imply exchangeability of the joint (Y, `caseCount`) under arm-label permutation, so permuting labels does not preserve the null distribution — no covariate-adjusted permutation scheme (Freedman–Lane, residual permutation, or otherwise) is named. (b) Inverting a permutation test into an *interval* on a difference in means requires a location-shift model; the outcome here is k/33, bounded and lattice-valued, with per-arm SDs that differ by 24% in the batch (0.0602 / 0.0749 / 0.0744), so the shift model is not innocuous. `OC-TABLE.md` §1 records that 019 already had to withdraw an "exact ... nominal coverage" claim once (R1-16); the same wording is back.

Cure: name the permutation scheme and its null; state whether the interval is a shift-model inversion and what it assumes; do not use the word "exact" without the coverage statement `OC-TABLE.md` §1 requires.

---

**[MAJOR] #18 (§3.1 table and footnote 1) — The table's rows do not sum to their own ITT counts; the "Near-gold" column double-counts "Perfect", and the bimodality footnote is contradicted by the data.**

*Lens: STATISTICS.*

Evidence: arm B row sums to 7 + 20 + 10 + 8 = **45** against ITT **37**; arm C to 9 + 13 + 17 + 14 = **53** against ITT **39**. (Arm A sums correctly.) Recomputed mutually exclusive counts over the artifact-bearing cohort:

| Arm | ITT | no artifact | collapsed ≥50 | **near-gold (1–49)** | perfect |
|---|---|---|---|---|---|
| A | 38 | 2 | 0 | 36 (2–15) | 0 |
| B | 37 | 7 | 20 (86–104) | **2** (2–13) | 8 |
| C | 39 | 9 | 13 (86–104) | **3** (2–13) | 14 |

The brief's 10 and 17 are `artifactAdmitted − collapsed`, i.e. near-gold + perfect. Footnote 1's "arms B and C are bimodal — **perfect or** 86–104 misses" is false for those 5 runs.

Cure: publish the exclusive table; restate the footnote as "strongly bimodal, with 2 / 3 intermediate runs". §3.2's ceilings (0.270 = 10/37, 0.436 = 17/39) are unaffected and correct.

---

**[MAJOR] #19 (§3.3 / M-2, and M-13)** — I1's finding is that E1 and E4 are uncoupled; §3.3 does not couple them, it removes the control's teeth and silently redefines what the control measures, while the actual source of the uncoupling — E4 scoring the suite against the *reference*, not against the policy it accompanies — is demoted to an unrecommended open decision.

*Lens: CONSTRUCT.*

*Evidence.* I1's numbers reproduce (arm B, identity-passing: collapsed ≥50 misses 0.6835 vs non-collapsed 0.6774; arm C 0.6328 vs 0.6839). What they show is that a run's *suite* score is independent of its *policy* score — a property of E4's operationalisation, since the suite is run against reference mutants under an identity control that is also against the reference (`RESULTS.json.perArmRuns[].identityPass`). 019's registered question is verbatim "does the representation a model authors in change **what its accompanying test suite pins down**" (`PREREGISTRATION.md` §1); "accompanying" is precisely the binding that E4 severs and that arm B's `run-011` (86/117 rows wrong, `identityPass: true`) exhibits. §3.3's replacement gate is still a *policy*-agreement gate — it changes the E1 construct from per-arm authoring competence to common-mode stimulus integrity and lowers the bar from 60% of runs to one run, leaving the primary measuring reference-pinning. M-13, the only item that would restore accompaniment, carries no recommendation.

*Cure.* Either register the suite-against-own-policy score (M-13) as a reported quantity that R1's construct statement is conditioned on, or state plainly in §1 and in the new §9 that the endpoint measures **pinning power against the shared reference**, not against the policy the suite accompanies, and re-word the registered question to match.

---

**[MAJOR] #20 (§5.2(b), S1's membership rule)** — The S1 stratum's "mechanical, not declared" membership rule, as worded, selects the empty set on 019's reference, not the five `x1r-*` rows the brief asserts.

*Lens: CONSTRUCT.*

*Evidence.* The rule is "a cell enters iff the arm-A reference reproduces it only with the participation of a pack member carrying **no prose-clause provenance**." Every rule and exception in `design/reference/refA/pack.json` carries an explicit clause id in its description, including all four repair members the brief names: `r-o1-wide-low` — *"O1 + D8 - a new vendor in D6c's LOW-country risk band…"*, `r-o1-wide-spend` — *"O1 + D8 - …"*, `x-o1-suppress-d8-low` and `x-o1-suppress-d8-spend` — both *"O1 - …"*. `V7-COMPLETENESS.md` §3.4 further records that each of the five rows "derives a governing clause like any other cell," with gold cites D8, O1, U1. The distinguishing property of the four members is that they are *derived consequences* of clauses rather than transcriptions — which is not decidable from `pack.json`. The brief's "On 019's reference it selects exactly the five `x1r-*` rows" is an assertion about an artifact that does not yet exist, made about a target set the brief has already enumerated.

*Cure.* Build the provenance table before the brief is registered and publish its extension, or replace the rule with one that is decidable from committed bytes (e.g. membership by `check_gold.py::retired_x1`, which V7 already certifies selects exactly 5), and drop the "not declared" claim if the predicate has to be tuned to hit a named row set.

---

**[MAJOR] #21 (§6.3 C4, the transfer gate's seat)** — C4 is one-sided by construction: a pilot/batch mismatch can only invalidate the batch, and 019 is a worked example where the pilot was the corrupted side.

*Lens: CONSTRUCT.*

*Evidence.* §6.1 establishes that 019's pilot ran with **no** environment isolation (`design/pilot/pilot_run.py` lines 130–132, no `env=`) while the batch ran isolated, and that the pilot's condition is unrecoverable (no `model`, `binarySha256` or `cli` in any pilot `CALL.json`) — §11 ceiling 3 repeats this. C4 nonetheless registers the pilot as the reference and places the mismatch at decision row 1 `pipeline-invalid`, and the brief states that on 019 it "fires on duration alone in every arm." Under the recommended N that discards 180 isolated calls on the authority of a 36-call reference, and C5's monotone re-pilot rule covers only the derived floor, not the transfer bands.

*Cure.* Make the mismatch adjudicable in both directions: register the observables that identify **which** side moved (exact `PINS.json` equality holds ⇒ the pilot is suspect; a pin differs ⇒ the batch is suspect), and register a `calibration-invalid` outcome that requires a re-pilot rather than refusing a batch whose pins match.

---

**[MAJOR] #22 (§7 D-1 row; §8 realised-n)** — Arm A's largest apparatus loss — 9 of 50 slots — is a second-order consequence of repairing a frozen wrapper mid-batch; the brief neither names it, nor turns it into a requirement, nor accounts for it in the N = 60 projection.

*Lens: OPERATIONAL.*

*Evidence.* `RESULTS.json.population.A.apparatusCodes` = `registry-mismatch: 9`. It is a scoring-time code (`score.py:524`) comparing each `CALL.json.pinsSha256` against the attempt's `pinsRawSha256` (`sha256:0596acde…`). Exactly nine arm-A `CALL.json` files carry the pre-repair digest `sha256:36912ee3…`, and D-1 records "9 arm-A calls clean" in the false-start slots 1–29 — so all nine are D-1 fallout. The ledger confirms the brief's other attribution (all 24 `slot-shape` = D-1's 20 + D-3's 4), but the brief says only "the `slot-shape` mass is D-1/D-3 and is pre-paid" and then projects arm A from 34/50 (0.68) to 50/60 (0.83) with no stated apparatus-loss assumption. (For reference, the live `PINS.json` digest today is `9ba6394d…`, matching neither recorded value — the registry moved again after the batch.)

*Cure.* Register the coupling as its own day-one requirement — any post-freeze registry re-pin invalidates every slot recorded before it, so either the scorer's registry check reads a semantic subset rather than the raw file digest, or a repair halts and restarts rather than resumes — and print the assumed per-arm apparatus-loss rate behind 50 / 35 / 40.

---

**[MAJOR] #23 (§4.1, §4.2)** — The group-level respecification silently drops 019's registered engine-supplied-kill dual reporting, which is 5% of kills and which makes the "same denominator, same lattice" claim true under only one column.

*Lens: OPERATIONAL.*

*Evidence.* `RESULTS.json.e4.A.engineSuppliedKill`: `killsIncluded` 1506/2484 vs `killsExcluded` 1431/2052, `listedMutants: 27`, `registered: true`, note — "the DECISION reads the included column; the excluded column and its reduced cut are R2, descriptive" (`reducedIntegerCut: 55`). At run level, `paired: 69` vs `pairedExcludingEngineSupplied: 57`, i.e. the excluded denominator is **run-varying and language-varying**, which is exactly V8-22's objection returning. Every §4.1/§4.2 figure I reproduced (61/69, 54/62, the 8+8 survivor ids, 28/33, 12–25) recomputes under the **included** column only.

*Cure.* State which column the group primary reads, label the brief's ceilings and τ recommendation accordingly, and re-derive the union ceiling under both.

---

**[MAJOR] #24 (§8; §6.5; M-8)** — The pre-pilot effort sweep — the one budget line whose entire purpose is to vary the compute condition — is priced at the registered condition's durations.

*Lens: OPERATIONAL.*

*Evidence.* §8 prices "3/arm × 2 settings | 18 calls | ~35 min", i.e. 18 × the registered triple (199 + 74 + 72.5 s). If one swept setting is the pilot-like one, those 9 calls cost ≈ 9 × 3220 s ≈ **8 h**, not 17 minutes; M-8 says "2–3 settings" while the table prices 2. The degradation control (36 calls, "~69 min") is priced the same way although it runs at whatever M-8 pins. §8's own paragraph concedes the multiplier for the pilot and the batch and never applies it to these two rows — and §8 never states a total call count (the recommended plan is 273 calls vs 019's 171).

*Cure.* Price each sweep setting at its own hypothesised duration, give the sweep its own per-call ceiling and abort rule, print the total, and present §8 as a range across the M-8 branches rather than one column plus a caveat.

---

**[MAJOR] #25 (§8; §6.1 table)** — The pilot-like cost branch mixes two admission cohorts inside a single table row, and understates its own arithmetic.

*Lens: OPERATIONAL.*

*Evidence.* Recomputed from the pilot `CALL.json` files: arm A completed 1559.081 / 1580.262 / 1660.184 / 1707.263 / 2407.773 s (median **1660** — the brief's figure, completed-only, plus five exit-124 slots at 900 s). Arm B completed 581.062 / 649.560 / 803.042 / 833.178 / 1101.012 → median **803**; the brief's "~818" is the median over all six B calls *including* the censored 900.048 s timeout. Arm C's "~757" is likewise the all-six median (completed-only is **624**). So one row uses completed-only for A and censored-inclusive for B/C. Even on the brief's own medians the triple is 1660 + 818 + 757 = 3235 s = **53.9 min**, not "~51 min", and 60/arm is **53.9 h**, not "~51 h". The registered-condition medians have the mirror defect: A 199 / B 74 / C 72.5 are taken over all `CALL.json` including 19 exec-failure records with `endedAt == startedAt` (B 10, C 9, `exitStatus: 126`); on real calls they are A 199 / B 75 / C 74.

*Cure.* Register one admission cohort for every duration figure — the same cohort C4's gate will read — and recompute the table under it.

---

**[MAJOR] #26 (§6.3 C4)** — The transfer gate's five tolerance bands are undefended constants; only one row has demonstrated power, and three cannot be exercised against the only known positive case.

*Lens: OPERATIONAL.*

*Evidence.* The brief says bands are "set before the pilot, from the design brief's own budget model" — no such model appears anywhere in the brief, and neither [0.5×, 2.0×] nor [0.6×, 1.7×] is derived. Recomputed pilot→batch completion-byte ratios: A 53,931 → 36,155 (**0.67**, inside the band), B 18,173 → 10,935 (**0.60**, on the boundary), C 18,403 → 9,789 (0.53). So on the one known condition mismatch, the byte row passes outright in the arm with the largest duration shift. The rows for reasoning tokens, sandbox policy / `codexHomeIsolated` / isolation inventory, and model/CLI/digest cannot be evaluated against 019's pilot at all: its `CALL.json` carries only `[argv, arm, completionBytes, completionSha256, durationSeconds, endedAt, exitCode, harness, promptBytes, promptFile, promptSha256, slot, startedAt, timedOut]` and no `session.jsonl` exists — "on observables already captured" is false on the pilot side. Sampling noise is not the binding constraint either: bootstrapping medians-of-12 from the batch gives 2.5–97.5% spans of 0.93–1.08× (duration), 0.85–1.18× (reasoning tokens), 0.92–1.10× (completion bytes), so the bands would pass a genuine 1.9× condition shift while the noise floor is ±10%.

*Cure.* Derive each band from that retained within-condition dispersion, state each row's power against the 019 mismatch, and demote to descriptive any row that has none.

---

**[MAJOR] #27 (§7, D-4 row; M-10)** — The D-4 requirement cures a defect 019 did not have; the real defect is a contradiction between two registered artifacts, and 020 inherits it.

*Lens: OPERATIONAL.*

*Evidence.* `PREREGISTRATION.md` §2 already reads: "**Registered batch window: three consecutive UTC calendar days** (pilot call durations: arm A 26–40 min, B/C 10–18 min; a one-day window is arithmetically impossible and is not registered)", and `PINS.json` `batch.window` = "three consecutive UTC calendar days". D-4 nonetheless opens "§2 registers all slots within one UTC calendar day" and files a deviation against it. The brief's requirement ("register a multi-day window up front") and M-10's recommendation ("3 UTC days registered up front") restate what 019 had. The surviving one-day sentences are in the pilot notes (`design/pilots/…/NOTE.md`: "The one-UTC-day batch rule cannot hold at N=50/arm"; `design/pilot/NOTE.md`: "the one-UTC-day rule"), i.e. a duplicated constant, not a window length.

*Cure.* Correct D-4 the way M-11 corrects #88, and restate the requirement as "one registered statement of the window, with a test that no other document states a different one".

---

**[MAJOR] #28 (§7 "ported by digest, no design change"; M-10)** — The carryover-balanced schedule is not N-independent, so the recommended N = 60 changes a file §7 promises is unchanged.

*Lens: OPERATIONAL.*

*Evidence.* `harness/batch.py:308-317` hard-codes `BLOCKS`, `SEQUENCES = 6`, a two-element `TAIL`, `ROUNDS = 50`, `RUNS_PER_ARM = 50`, `REGISTERED_SLOTS = 150`; `derive_order()`'s docstring (664–681) says the registered `BLOCK_ORDER`/`TAIL` are the cached answer to a search *at 50 rounds* and that "the harness test requires that minimum to be (1, 1) and to be attained by the constants above". At 60 rounds there is no tail (60 = 10 × 6) and 60 divides over 3 positions, so position spread 0 becomes attainable and the registered floor (1,1) is no longer the floor — `test_schedule.py`'s assertion is wrong by construction. `REGISTERED_SLOTS = 150` is also read at `batch.py:3089` and `:3316`, and pinned at `PINS.json` `batch.n` / `batch.slots` / `batch.order`.

*Cure.* Move the schedule row out of the "no design change" list, register the re-derivation and the new attained floor as a day-one work item, and re-pin `batch.order`.

---

**[MAJOR] #29 (§7)** — The sealed reviewer mutant set is listed as pre-paid carryover, but it was executed and published in 019 and is therefore spent.

*Lens: OPERATIONAL.*

*Evidence.* `PINS.json` `reviewerMutantSet.note`: "Sealed … committed verbatim, **first executed at the primary attempt**, scored as authored, reported separately, moving nothing." `RESULTS.json.reviewerSet.perArm` publishes the outcome per run — `rm-jps-01` and `rm-jps-02` survive in every listed arm-A run, `rm-jps-03` is killed in every one. Porting it "unchanged, by digest" hands 020 a reviewer control whose answers are already in the published record, under a §7 sentence claiming the whole list is "pre-paid by 019's twelve review rounds".

*Cure.* Register a fresh sealed reviewer set for 020; keep 019's only as a published comparison.

---

**[MAJOR] #30 (§7 D-3 row; §8)** — The D-3 requirement fixes the janitor's off-by-one and leaves the capacity problem that made a janitor necessary, while raising the slot count 82%.

*Lens: OPERATIONAL.*

*Evidence.* D-3's own account: "the machine's root filesystem twice approached full (D-2's resume was itself preceded by an ENOSPC crash at run-018 B)" and the operator's cleanup loop was the *response*. The brief's requirement is only "the four-newest-entries janitor rule registered from the start, and the wrapper's directory count documented". The recommended plan is 273 model calls (18 + 36 + 36 + 180 + 3) against 019's 171; each retained slot is ~0.7 MB in-tree (measured: `arms/A/authoring/run-001` 660 KiB, `arms/` 86 MB) plus **two** scratch directories per slot holding a fresh HOME, CODEX_HOME and a credential copy. The working volume reports 251 G, 1.5 G free, 100% used as I write this.

*Cure.* Register a free-space precondition checked at driver start and before each slot, a retention rule for the scratch parent, and a total call and disk budget in §8 — which currently never sums its own table.

---

## MINORS

**[MINOR] #31 (§4.2 precision table) — SDs are maximum-likelihood (÷n), and the ANCOVA MDE omits the imbalance inflation and the df penalty.**

*Lens: STATISTICS. OPERATIONAL (OP-14) reached the same finding independently, recomputing the per-arm group-level SDs as 0.0602 (n = 34), 0.0749 (n = 26), 0.0744 (n = 28) and the (N − k) pooled figure as 0.0694 against the brief's 0.0682.*

Evidence: the brief's 0.0682 / 0.0888 / 0.0495 / 0.0591 are exactly my unbiased 0.0694 / 0.0904 / 0.0507 / 0.0605 scaled by √(85/88) and √(84/88) — the within-arm sum of squares was divided by n, not by n−3 (residuals n−4). Every MDE in the table is optimistic by ~1.8%. Separately, `Var(adjusted difference) = σ²[2/n + (x̄₁−x̄₂)²/S_xx,within]`; the table drops the second term, which by #4 is not negligible here.

Cure: use n−k; add the imbalance term or state the balance assumption the table is computed under.

---

**[MINOR] #32 (§8 "expect realised E4-scoreable n ≈ 50 / 35 / 40") — Not reproducible from the brief's own loss accounting.**

*Lens: STATISTICS.*

Evidence: the brief pre-pays only the `slot-shape` mass (D-1/D-3). Arm A's apparatus loss is `registry-mismatch` 9, `slot-shape` 2, `transcript-refused` 1 (`RESULTS.json.population.A.apparatusCodes`), so repairing slot-shape moves arm A's ITT rate 38/50 → 40/50 = 0.80; times artifact 36/38 times identity 34/36 gives 0.715, i.e. **~43 at N=60**, not 50. Same arithmetic gives B ~**40** (brief: 35) and C ~**43** (brief: 40). MDE impact is small (0.042 at 43/43 vs the brief's 0.041 at 50/40), which is why this is MINOR — but the projection as printed is not derivable.

Cure: show the arithmetic per arm, or state that registry-mismatch is also assumed repaired and why.

---

**[MINOR] #33 (I4) — The quantiles quoted do not reproduce under any standard convention, and they are from a different cohort than the sentence they support.**

*Lens: STATISTICS. CONSTRUCT (CV#9) reached the same cohort finding, recomputing the ITT-114 IQR at 0.283 against the identity-passing 0.1015 and noting that the printed max 0.806 belongs to the identity-passing cohort while the printed median/q75 track the ITT one.*

Evidence: the brief's "Pooled ITT paired-kill quantiles q25 0.419 / median 0.667 / q75 0.710". Recomputed over the ITT set (114 runs, no-artifact scored 0): exclusive q25 0.4113 / median 0.6594 / q75 0.7097; inclusive 0.4232 / 0.6594 / 0.7062. The brief's q25 = 0.419 ≈ 26/62 and median = 0.667 ≈ 46/69 are raw order statistics, i.e. a nearest/lower quantile method that is not named. More substantively: the same row's headline is "dichotomised on a distribution **~0.10 wide**", but the ITT IQR is **0.28–0.30**; only the artifact-bearing (0.113) or identity-passing (0.101–0.111) IQR is ~0.10. The sentence mixes cohorts.

Cure: name the quantile convention and use one cohort per sentence.

---

**[MINOR] #34 (§6.1) — "P(pilot 5/5) is ≤ 3 × 10⁻⁶ (A)" cannot come from the source the sentence names.**

*Lens: STATISTICS.*

Evidence: the text says "under the registered per-arm perfect rates". Arm A's registered perfect rate is **0/38**, which gives P = 0. The figure is (3/38)⁵ = 3.07 × 10⁻⁶ — a rule-of-three upper bound substituted silently. B (8/37)⁵ = 4.72 × 10⁻⁴ and C (14/39)⁵ = 5.96 × 10⁻³ do come from the stated rates.

Cure: say "using the rule-of-three 95% upper bound 3/38 for arm A, whose observed rate is 0", and note that a bound-plugged probability is not a p-value.

---

**[MINOR] #35 (§1, "The question, unchanged")** — The question is presented as carried verbatim but has been materially re-worded: `PREREGISTRATION.md` §1 ends "…compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a prescribed judgment convention (arm C)?", where §1 here substitutes "with gold agreement (E1) as a control that is actually passable" — an instrument-repair commitment moved inside the research question, and the three-arm comparison clause dropped. *Cure:* quote 019 §1 verbatim under the "unchanged" heading and put the E1 clause in §3 where it is argued.

*Lens: CONSTRUCT.*

---

**[MINOR] #36 (§8 cost table vs M-9)** — The cost table budgets 36 model calls ("Degradation control, 12/arm, ~69 min") for a degradation that M-9 recommends implementing as a **reference** edit, which requires no authoring calls at all — the existing 019 runs can be re-scored against the degraded gold, as #8 does in seconds. Either the budget or the recommendation is wrong, and the two together conceal that the recommended control is not a re-authoring experiment. *Cure:* state which object is degraded, and budget accordingly.

*Lens: CONSTRUCT. OPERATIONAL (OP-3) independently made the same budget point.*

---

**[MINOR] #37 (§4.2, "Denominator: the 33 shared non-degenerate witness groups")** — Five of the primary's 33 units are structural constants: the eight-plus-eight always-surviving mutants are witnessed by the same five `d8` inputs, so 5 groups are killed by no run in either language (union ceiling 28/33, recomputed and confirmed). The primary's effective support is 28 units, its floor is displaced downward by a fixed 5/33 = 0.152 in both arms, and the reported range "12–25 of 33" is bounded above by 28 rather than 33. *Cure:* publish the five group identities with the denominator (the brief already registers this as a corpus-structure publication) and state the effective support alongside the nominal 33 wherever the estimand is defined.

*Lens: CONSTRUCT.*

---

**[MINOR] #38 (§6.1; §6.5)** — The recorded pilot-vs-batch invocation difference is larger than the brief's list, and the omitted member is the one most directly tied to the test-row gap the brief cites as evidence.

*Lens: OPERATIONAL.*

*Evidence.* `design/pilot/pilot_run.py:69-76` fixes `CODEX_ARGV = codex exec --skip-git-repo-check --sandbox read-only --color never -c mcp_servers={} -`. The registered wrapper's recorded argv (`arms/A/authoring/run-001/CALL.json`) is `codex exec --ignore-user-config -m gpt-5.6-sol --sandbox workspace-write -c mcp_servers={}`. §6.1 names `$HOME`, `~/.codex/config.toml` and `$HOME/.agents`, and omits **read-only vs workspace-write** — the difference most plausibly connected to §6.1's third row (pilot arm-A 35–49 test rows vs registered `caseCount` 16–25), since a read-only sandbox cannot write or execute the suite it is drafting. §6.5 then contemplates pinning "a **higher** reasoning effort to recover pilot-like behaviour", i.e. targeting a condition whose defining property was that isolation was absent; C1 alone removes four of the five recorded differences without any effort pin, which the brief never says.

*Cure.* Print both argv vectors side by side in §6.1, drop "recover pilot-like behaviour" as an objective, and state which of M-8's cost multipliers survive once C1 lands.

---

**[MINOR] #39 (§7 D-1 row; §8)** — "Never a stand-in CLI" is the wrong strengthening of D-1's lesson, and it is unbudgeted.

*Lens: OPERATIONAL.*

*Evidence.* D-1's failure was `/usr/bin/env: Argument list too long` — at `exec`, before codex started; a real exec of a *stand-in* binary at the registered 204,333 / 206,686-byte prompt sizes reproduces it exactly. The design phase's other driver could not have caught it either: `pilot_run.py:130-131` already delivered by stdin (`subprocess.run(CODEX_ARGV, input=prompt, …)`), the very fix D-1 adopted. §8's table budgets no smoke calls of any kind, and D-2's account depends on the smoke driving a *stand-in study*.

*Cure.* Require "a real exec at the registered prompt bytes" (stand-in binary permitted), preserve D-2's stand-in-study smoke, and add whatever real calls the smoke does need to §8's table.

---

## What a v2 brief must resolve before the preregistration drafts

Four things, in order. **First, the disclosure**: §2.2's "they do not re-derive" is false (#1) — the arm-labelled A−C direction is on the record under both endpoint forms, with opposite signs, so M-1 cannot be answered as a formality and must be re-posed as a choice between publishing a 019 amendment and producing a genuinely arm-blind justification of the group-vs-mutant level (#2). **Second, the estimand must be closed rather than left as sub-decisions**: v2 must name the analysis population for a continuous primary and the disposition of artifact-less, identity-failing and `survivorsPaired`-less runs (#5), name whether R1 reads the adjusted or the unadjusted difference (#3), settle whether a post-treatment mediator may sit in the primary at all (#4), state the permutation scheme and drop the word "exact" or defend it (#17), and either re-derive an endpoint that reads assertions or rename the construct, since the proposed primary is provably witness-input coverage and not pinning (#14, #15). **Third, every gate the brief adds must be shown capable of failing**: the attainability gate (#6), the τ rule (#7), the existence gate's OC table (#13) and above all the degradation control, which under recomputation cannot fail the gate it certifies and is anti-correlated with it in arm A (#8) — each needs its mutation check published, per the program's standing lesson, before it is registered. **Fourth, the apparatus plan must be made runnable and honestly priced**: the pilot cannot execute through the registered wrapper as pinned (#9), the effort pin has no transcript witness (#10), the carryover schedule and the sealed reviewer set do not in fact carry over at N = 60 (#28, #29), and §8's table mixes cohorts, under-prices the sweep it exists to fund, and never sums itself against a volume that is currently full (#24, #25, #30). Until those four are closed the brief will not survive a freeze round, and the §2.1 arm-blindness claim should be withdrawn or restated as a narrower rule that §3–§5 actually satisfy (#12).