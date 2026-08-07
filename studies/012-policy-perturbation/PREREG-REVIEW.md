# Pre-freeze adversarial review — Study 012

This file is the complete pre-freeze review record for Study 012. It records
every adversarial round the preregistration and the five arm texts are put
through before any freeze decision: who reviewed, by what method, the verdict
verbatim where one exists, every finding faithfully summarized, and what was
done about each one. Nothing is discarded. It follows Study 011's per-round,
per-finding disposition format.

**Status: OPEN. One round complete. Nothing is frozen and nothing has run.**

**Why this file also carries digests.** Round 1 found that nothing bound the
arm texts a review round saw to the arm texts that get pinned: the sequencing
is right — review settles the authored artifacts, then the port fills the
digests, then the freeze — but between the last review round and the freeze a
clause of arm E could change with Appendix A updated to match, and the
registered-illustration check (Appendix A bytes == `POLICY.md` bytes) would
pass either way, because both would have moved together. So **every round below
records the sha256 of each of the five arm texts as that round reviewed them**,
and `harness/integrity.py` refuses unless each frozen `arms/<X>/POLICY.md`
digest equals the digest recorded in the **final** round. That makes "the texts
that were reviewed are the texts that ran" a checked relation instead of a
sequencing convention. `PREREGISTRATION.md` §8 and §10 register it.

**Drafting model:** Anthropic Claude Opus (Claude Code), 2026-08-07.

---

# Round 1 — internal adversarial review (this model lineage)

**Basis:** the first draft of `PREREGISTRATION.md` and `README.md`, before any
commit that pins an artifact. **Date:** 2026-08-07. **Reviewer:** Anthropic
Claude Opus (Claude Code subagent), running as an adversarial reviewer against
the committed draft, required to reproduce every claim from bytes rather than
assert it. **Same model lineage as the drafter — this round is an internal
pass, not a cross-vendor round, and it is recorded as such.** Its value is that
it re-derived every number independently; its limit is that a shared prior is
not an independent one, and the cross-vendor rounds have not yet run.

**Result: NOT READY for the cross-vendor rounds — 23 findings (7
blocking-for-freeze, 14 should-fix, 2 nits).**

## Verdict (verbatim, opening and closing)

> NOT READY for the cross-vendor rounds as it stands — but the gap is
> authored-artifact quality, not method. The machinery is in very good shape: I
> recomputed every Clopper–Pearson vector at n=25 and n=50, the perfect-arm
> bounds at n∈{16,17,20,25,30,50}, the half-covered widths, the HIGH/LOW cut
> locations (HIGH iff k≥23, LOW iff k≤2), the whole §5.4 operating-
> characteristics table, the n=20/n=30 comparisons, and the 0.919 three-of-four
> figure — all exact, to the digit. The port tables' digests check against
> 010's PROTOCOL-LOCK.json and 011's files, the §2.6 prompt equation holds on
> the real 011 prompt bytes (2706 = 948 header + 1758 policy-minus-LF), the
> class schema at (40,70) reproduces 010's family, arm B's digit-run multiset
> is right, and D's unstated-edge analogue (44 = T_low−1) is correctly carried
> through §2.3, §4.5 and C4.

> What blocks the freeze is that the intervention artifacts — the part no
> digest can check and the part the study's own §7 names as its structural
> conflict — are weaker than the harness around them.

> Recommended sequence: fix the seven blocking items and findings 8–14 in a
> round-2 internal pass; commission the clean-room readers for the five texts
> (finding 5) in parallel, since their verdict may itself force a re-authoring
> of arm E; then send the revised file plus the five arm texts to the
> cross-vendor rounds as one package.

## What the round confirmed rather than assumed

Recorded because it bounds what the findings mean. The reviewer recomputed,
from source bytes and with its own exact-rational implementation: every
Clopper–Pearson vector at n = 25 and n = 50; the perfect-arm lower bounds at
n ∈ {16, 17, 20, 25, 30, 50}; the half-covered interval widths; the cut
locations (HIGH iff k ≥ 23, LOW iff k ≤ 2 at n = 25); the whole §5.4 operating-
characteristics table; the n = 20 and n = 30 comparisons; and the three-of-four
figure. It verified the port digests against
`studies/010-blinded-oracle/PROTOCOL-LOCK.json` and against Study 011's files;
the §2.6 prompt equation against the real prompt bytes; the class schema at
(40, 70) against 010's locked `FAMILY.json`; and arm D's unstated-edge analogue
(44 = `T_low` − 1) through §2.3, §4.5 and C4. **No numerical error was found in
the interval arithmetic, the operating characteristics, or the digest chain.**

## Method

The reviewer read the draft, then re-derived each numeric and byte-level claim
against the predecessor studies' committed bytes rather than against the
draft's own restatements: 010's `PROTOCOL-LOCK.json` and `policy/POLICY.md`,
011's `harness/PINS.json`, `harness/PORTS.md`, `DIVERSITY.md`,
`MIRROR-AGREEMENT.md` and `PREREGISTRATION.md`. It attacked the study's own
stated structural conflict — that the perturbations are authored by the team
holding the prediction — by asking what an independent author of arm E would
have written differently.

## Findings and dispositions

**All 23 findings accepted; none disputed.** Where a finding offered options,
the maintainer's choice is recorded as a maintainer decision and the option not
taken is registered in `PREREGISTRATION.md` §10 as that decision's alternative.
Five new register entries were opened: **D-14** through **D-18**.

| # | sev | finding | disposition |
|---|---|---|---|
| 1 | blocking | Arm D's mirror is an unregistered, unpinned artifact, yet it is the arbiter of every one of D's labels. §2.2 ported `policy_mirror.py` byte-identically (`276b5f73…`), which encodes 40/70 and cannot serve D; §2.6 registered four files per arm and none was a mirror; §2.10's registry omitted it | **FIXED — maintainer decision: option (b).** One 010-locked module parameterized by (`T_low`, `T_high`) read from the arm's registered `ARM.json`, so one pinned mirror serves all five arms and D's behaviour is keyed to an artifact already pinned before any call. The §2.2 row moves from the byte-identical table to the enumerated-change table, bound to 010's lock on the source side and to `PORTS.md` on the destination side; the module's digest is pinned in §2.10 and checked by C8 clause 1; C8 clause 6 runs the grid against it at its registered digest. **Registered as [D-14], with option (a) — a fifth per-arm file `arms/<X>/MIRROR.py` — as the alternative** |
| 2 | blocking | The registered digit-free property of arm E is **false of arm E's own file**, and the check as written would refuse the study's own artifact: the preamble reads "Synthetic policy for Study 010" and the digit-run `010` is inside `POLICY.md`, not the prompt header. Worse than bookkeeping: "Study 010" is a name-keyed pointer to a public repository whose policy states 40 and 70, so arm E is not denamed | **FIXED, both halves.** (1) The property is corrected to the truth in §2.5, C8 clause 5 and A.5: the only digit-runs in arm E's `POLICY.md` are the clause labels, in-body clause-label references, the token `ISO 3166-1 alpha-2`, and the preamble's study reference, and none equals 40 or 70 — verified exhaustively against the assembled bytes. (2) The recall channel is registered: §5.3 (i) now carries a **third** pre-registered reading of an E-maintains-coverage outcome (recall keyed to the named study), with X3 dispersion named as the discriminator and the honest statement that this design **cannot separate recall from derive-then-hug**. The reviewer's "better still" — a digit-free, name-free preamble in all five arms — is registered as **[D-16]**'s alternative rather than adopted, because it would be a second registered delta from 010's text beyond D-15's |
| 3 | blocking | Arm E's reference wording carries three authored difficulties that are not the intervention, each of which alone can manufacture the predicted collapse: the pronoun "it" nearest-resolving to *the review threshold* (two fifths of 70 = 28); "clearance threshold" as the wrong name for `T_low`, which §2.3 calls the personal-data threshold; and two different denominators making one derivation strictly harder than the other | **FIXED — the reviewer's rewrite adopted verbatim.** A.5 now reads "The **review threshold** is seven tenths of that full range; the **personal-data threshold** is four tenths of that same full range." One denominator, no pronoun, §2.3's own names. D-3 records the rewrite and states that the round-1 wording is **not** an option. The plausible-misderivation audit the finding asks for is registered as a new named census output **§4.5 X6**, listing 70/40 (correct), 0.7/0.4, 7/4 and 28, with per-value counts at and within 0.01 |
| 4 | blocking | Arm E applies **two** interventions: its "The office's risk scale runs from zero to one hundred" is new semantic information no other arm carries. Neither 011's header nor A's conventions bounds `riskScore`; 011's corpus contains scores authored with no stated scale; and the mirror cannot catch it because the mirror encodes no domain | **FIXED — maintainer decision: option (a).** The identical scale sentence goes in **all five** arms' conventions paragraphs as the registered `CONVENTIONS_DELTA` (55 bytes, published verbatim, pinned by its own sha256). §2.1's arm-A byte-equality is relaxed to *equals 011's pinned text plus exactly the registered conventions delta*, with the reasoning stated: §2.1 already declares 011's runs historical and every contrast within-batch, so the prompt digest was load-bearing only for the §4.7 drift report, which gates nothing. 011's prompt digest is still pinned and verified — as the source of `HEADER`. **Registered as [D-15]**, with (b) a sixth arm A′ and (c) E-only-accepting-the-confound as the alternatives |
| 5 | blocking | The clean-room second-mirror instrument Study 011 built one day earlier for exactly this circularity (`MIRROR-AGREEMENT.md`, PR #44) is dropped without mention. 012 has five policy texts, two authored by the team holding the prediction, and it ports no analogue — the one cheap, model-call-free, pre-data check that can answer "is E's wording derivable, or was it written to be hard" | **ACCEPTED FULLY.** New control **C10**: per arm, an independent author receives that arm's `POLICY.md` bytes and nothing else and writes `analysis/mirror2_<arm>.py`; **every clean-room mirror must agree with that arm's registered mirror elementwise on the §2.4 landmark grid before any call**, enforced by `integrity.py` rather than reported post-hoc. The failure consequence is registered in advance: if the clean-room reader cannot derive (40, 70) from arm E's text, **arm E is an ambiguity arm rather than a denaming arm and is re-authored and re-registered before the freeze rather than run**. `MIRROR-AGREEMENT.md` is added to §8's publication list and to the README's reading order |
| 6 | blocking | C1 as specified **refuses the study's own inputs**. It bound every 011-file-that-011-ported-from-010 to 010's lock on the source side — but 011 *adapted* three of them (`records_compile.py` `6de92175…` vs `e58edce3…`, `transcript_check.py` `0c9d7c79…` vs `42d977c4…`, `authoring_call.sh` `6e1239f3…` vs `3b8909aa…`) — and it bound the byte-identical set to 010's lock on the destination side, but that set includes `PROBE-PROMPT.txt` (`128aaa9a…`), which 011 introduced and which appears in no `lockedInputs` of 010 | **FIXED.** C1 is rewritten as a **three-tier table keyed to the authority each row actually has**, matching §2.2's own authority column rather than the file's port kind: tier 1 bound to 010's lock, tier 2 (`PROBE-PROMPT.txt`) to 011's `PINS.json`, tier 3 (the three adapted files) to their 011-side digest and to 011's `PORTS.md` provenance row and **never** to 010's lock. §2.2's tables gained an authority column. All six digests re-verified against `PROTOCOL-LOCK.json` and 011's files |
| 7 | blocking | Arm C violates its own stated principle: (P2, P4, P1, P5, P3) creates further forward references of exactly the kind the registered P4-before-P5 constraint exists to prevent, so §5.3 (iii)'s reading of a C-collapse would be over-claimed | **FIXED — the reviewer's permutation adopted, its arithmetic independently re-verified, and one correction made.** (P2, P1, P4, P5, P3) is registered. Verified by exhaustive enumeration of all 120 permutations: it **is** a derangement (P1 1→2, P2 2→1, P3 3→5, P4 4→3, P5 5→4), it keeps P4 before P5, and it is the **unique** permutation that is a derangement *and* resolves every explicit label reference *and* every three-part "absent a sanctions hit or an embargoed registration" precondition backward. **Two corrections to the finding, recorded rather than passed over** — see "What the review got wrong" below. §2.6 and A.3 state the generalized constraint, the residual, and the enumeration; D-5 records the alternative |
| 8 | should-fix | The decision rule is crisp on falsification and silent on confirmation and on the all-MID outcome that N = 25 makes likely, so a motivated analyst could call 2 COLLAPSE + 2 MID "confirmed" after the fact | **FIXED.** §5.3 (i) registers both directions symmetrically as a table: CONFIRMED iff COLLAPSE on ≥ 3 of 4; FALSIFIED iff HIGH on ≥ 3 of 4; every other pattern INDETERMINATE, published as INDETERMINATE, with R1 recorded as neither confirmed nor falsified. **All-MID is named explicitly** as an INDETERMINATE outcome and as the design's expected outcome for any partial anchoring effect. D-10 restated |
| 9 | should-fix | §5.4 computes only marginal operating characteristics and omits the joint figures the headline needs; §2.1 then mis-attributes the most likely way the design fails. At p = 0.95 — inside 011's own interval, lower bound 0.9275 — P(arm A HIGH on all six) is 0.4424 and P(all four narrow) is 0.5806, so ~42% of the time a falsifier-relevant class yields no contrast verdict from sampling alone; yet §2.1 registered that outcome as "the contemporaneous baseline has moved" and as the headline finding | **FIXED.** §5.4 gains a joint table at p ∈ {1.00, 0.98, 0.95} for P(all four narrow HIGH), P(all six HIGH) and P(all twelve HIGH), plus P(all four COLLAPSE) = 0.3370 at p_A = 0.95 / p_E = 0.05 — **all recomputed independently and matching the reviewer to the digit**. §2.1 is rewritten: an arm-A class below HIGH is at least as likely to be sampling noise as drift and is reported as an **unresolved baseline for that class, not a drift finding**. D-1 gains the joint case for N = 30 (P(all six) 0.4424 → 0.6865) and for N = 20 (→ 0.1587) |
| 10 | should-fix | The contrast rule discards information for no registered reason and is itself not in the §10 register, though it is the study's second-most consequential registered choice after the level cuts | **FIXED.** New **[D-17]**: a second contrast, **COLLAPSE-DISJOINT iff `U_X < L_A`**, reported beside the level-gated verdict and **never substituted for it**; §5.3's predictions and falsification conditions remain stated on the level-gated COLLAPSE alone. Both computable from the same integers, neither adding a distribution for a difference of proportions. The alternative — the level-gated rule alone — is registered |
| 11 | should-fix | The shortfall path has an unregistered floor and contradicts a control: a perfect arm's lower bound is 0.6915 at V = 10 and 0.7151 at V = 11, so below eleven valid runs no arm can read HIGH and the study produces no verdict — and C5 required slot indices to be exactly 1…N, which is false under a declared shortfall | **FIXED, both halves, and generalized.** §2.8 registers the floor: a shortfall at R < 11 rounds leaves the level rule unable to return HIGH for any arm; the batch is published as slots and rates with **every verdict `UNRESOLVED-BY-DESIGN`** and **no contrast reported**. Generalized beyond the finding: the floor is registered **per arm on `V_X`**, because pipeline-invalid runs reduce `V_X` below the slot count independently of R. C5 now reads 1…R where R is the declared round count, and exactly 1…N with no declaration. Both bounds re-verified |
| 12 | should-fix | Two numbers about the predecessor do not survive checking. (i) "four of the six classes rest on one or two distinct probes" — `DIVERSITY.md` table C gives 2, 6, 2, 24, 26, 2, so **three** classes rest on two probes; the census's "four of six" sentence is about classes containing a probe present in every one of the 49 runs. (ii) The README says 011's runs are "months old"; they were produced and merged 2026-08-07, and §2.1 correctly says so | **FIXED, both.** §1 and the README now say "three of the six classes rest on two distinct probes each, and four of six contain a probe that appears in every one of the 49 runs" — verified against table C. The README's "months old" is replaced by §2.1's own correct reasoning: the runs are historical, produced against a model snapshot whose drift since is uncontrolled and unmeasurable from here, so every contrast is within-batch. §4.5 X1 restated to match |
| 13 | should-fix | The falsifier's target is never written as one retractable proposition, so §8's retraction commitment cannot be checked afterwards; and the prediction is attributed to a venue nothing in the repository carries | **FIXED.** §1 states the proposition once, as **R1**, and §5.3 (i), §5.4 and §8 refer to it by name. `CLAIM.md` is added to the study directory, pinned in `PINS.json`, carrying R1's verbatim published wording, venue, URL and retrieval date. §8's prominence list gains a **correction banner at the head of `studies/011-authorship-coverage-rates/DIVERSITY.md`**, and states explicitly that the census's descriptive sentence about its own corpus **stands regardless** — it is R1 that is retracted |
| 14 | should-fix | Arm A's `POLICY.md` is 010's locked `policy/POLICY.md` at `e46f8c48…`, yet §2.6 left it "(port time)" and §2.2 had no row for it at all — the baseline intervention itself was outside the three-level chain | **FIXED, and superseded in form by D-15.** `arms/A/POLICY.md` is now a **row in §2.2's enumerated-change table** with 010's lock as its source-side authority at `e46f8c48…` (read out of `PROTOCOL-LOCK.json` and re-verified here) and `CONVENTIONS_DELTA` as its enumerated change, and it is in C1's tier 1. Because of D-15 it is a *derivation* from the locked bytes rather than an equality — a stronger relation than the digest was, since the residue is published and pinned. Under D-15's alternative (c) it collapses back to the equality the finding asked for |
| 15 | should-fix | (45, 72) is an authored choice with two unaddressed confounds and no §10 entry: 40/70 are decade-round and 45/72 are not, and the unequal shift makes arm D's class 3 27 wide where the draft repeatedly calls it "a 30-wide band" | **FIXED — maintainer decision: keep (45, 72) as the proposal.** New **[D-18]** with (50, 80) as the salience-matched, width-preserving alternative **and the trade stated honestly: (50, 80) is exactly a +10 additive shift, which is the confound (45, 72) exists to exclude.** §5.3 (ii) registers the **third** D outcome — new-keyed LOW *with* old-keyed LOW is neither tracking nor contamination but a general degradation, published as one. Every "30-wide band" is qualified with the arm it describes (§2.3, §5.3 (i), §5.3 (ii), A.4, D-11) |
| 16 | should-fix | B's literal census holds the digit multiset but nothing holds the boundary-inclusivity phrasing, which 011's census identifies as the most anchoring-relevant feature of the text — so a B-collapse would be read as prompt-shape anchoring when "the paraphrase weakened the inclusivity cue" explains it at least as well, and a B-collapse disarms arm E under §5.3's own dependency | **FIXED.** §2.6 and C8 clause 5 register a clause-level invariant the census cannot express: in every arm at (40, 70), each numeric bound carries an explicit inclusivity word immediately adjacent to its literal, and **B's adjacency pattern matches A's clause for clause**. The clause-by-clause A ↔ B substitution table is published under D-4 in A.2, with the one asymmetry the table exposes (P4's lower bound: "40 or above" puts the word after the literal, "from 40 up to" puts it before) flagged as the review's to adjudicate. Verified mechanically against both texts |
| 17 | should-fix | `arm-mismatch` is the one new admission code and the arm-specific terminal-prompt gate is the one changed admission check, and neither has a registered fixture — and here **five** prompts first meet that gate on a real slot, where 011 could note that its one prompt met it on batch slot 1 | **FIXED.** C4's minimum fixture list gains all three the finding names: a synthetic slot carrying arm B's prompt bytes inside arm A's tree, required to score `arm-mismatch` and not `context-mismatch` or `transcript-refused`; a synthetic slot whose `CALL.json` arm stamp and `armPromptSha256` disagree; and **one admissible slot per arm**, so the gate is exercised at all five prompt digests in CI before the batch |
| 18 | should-fix | The 180-cell landmark grid does not probe the family's own class edges: it contains no value at or near `T_low + 1` or `T_high + 1`, the exclusive upper bounds of classes 2 and 1, so a family encoding class 2 as [45, 47) would pass the class-membership half unchanged — while the grid is advertised as the check that carries the whole claim about arm D. And C9's role is asserted twice without saying whether it is structural or extensional | **FIXED, both.** The landmark set gains `T_low+1−0.01`, `T_low+1`, `T_high+1−0.01`, `T_high+1`: **13 landmarks, 260 cells** (2 × 5 × 2 × 13, re-verified), updated in §2.4, C8 clause 6, §7 and the README. C9 now states that the family comparison is **structural equality of the six predicate encodings**, not merely extensional agreement, and says which failure each bounds and that C8 clause 6 runs in addition rather than instead |
| 19 | should-fix | The verdict surface is undercounted where it is acknowledged, and §5.3 (iii)'s dependency reads twelve control-arm verdicts jointly without saying how many classes must track or computing that P(all twelve HIGH) is 0.1957 at p = 0.95 | **FIXED.** §4's opening states the full surface as a table — 30 level + 24 contrast + up to 30 S10 level verdicts + 5 census expectation patterns, all marginal, no simultaneous claim. §5.3 (iii)'s dependency becomes a **registered count**: TRACKING on at least five of six classes in each of arms B and C, with P(all twelve HIGH) = 0.1957 in §5.4's joint table and the reason five-of-six was chosen over six-of-six stated |
| 20 | should-fix | A ceiling 011 stated explicitly is dropped by 012, in a design that makes it worse: 011 §2.4 recorded the in-process library route, and here the operator holds a directional prediction, the schedule is interleaved, and §2.8 permits a shortfall at any round. The three facts are individually recorded and their interaction is not | **FIXED.** §7 restores the ceiling with the interaction named in the finding's own terms: the registered command is the only publisher, nothing prevents a library caller computing an arm's rate in process, and combined with the interleaved schedule and the shortfall path an operator could in principle read arm E early and stop at a favourable round — nothing here prevents it. The bounds are named. **`SHORTFALL.json` now records the UTC wall clock of the last completed slot** (§2.8, README). Added beyond the finding: below R = 11 an early stop buys nothing, because finding 11's floor means no arm can read HIGH there |
| 21 | should-fix | Nothing binds the arm texts the cross-vendor rounds reviewed to the arm texts that get pinned: between the last round and the freeze a clause can change with Appendix A updated to match, and the registered-illustration check passes either way | **FIXED.** §8 and §10's preamble register that `PREREG-REVIEW.md` carries, **per round, the sha256 of each of the five arm texts as reviewed**, and that `harness/integrity.py` refuses unless each frozen `arms/<X>/POLICY.md` digest equals the digest the **final** round recorded. §2.10 lists those digests among the registry's members. Appendix A gains the **assembly rule** that makes each digest reproducible from the appendix's own bytes, and this round's five digests are recorded below |
| 22 | nit | §1's restatements of the census are slightly stronger than its bytes: the census's distance is the minimum to {39, 40, 70} and 39 is the *unstated* edge, which §4.5 of the same draft correctly registers; and table B's far side of 40 is 40.01 ×3 — two decimal places, not three | **FIXED.** §1 now says "sit on one of the family's three edges or within 0.01 of one" and "hugged to **two or three** decimal places from both sides", matching §4.5's own registered distance set and table B. Re-verified against table B: 181 + 84 + 145 = 410 of 784 |
| 23 | nit | Port bookkeeping a reader coming from 011 will trip on: the S-numbers silently diverge (011's S8 is the pipeline-invalid rate and its S9 the wall clock), and 011 §5's per-row composition rule is dropped without being named as a drop | **FIXED.** §4.6 gains the S-number mapping sentence. §8's out-of-scope list gains: "Study 011 §5's per-row composition rule is not ported — no row is scored here, and the per-class tiers are reported as S9 only because 011 registered them", stated as a *different thing* from the existing exclusion of validating that tier mapping |

## What the review got wrong, recorded rather than passed over

Two corrections to finding 7, both found while re-verifying the reviewer's
arithmetic before writing it in, and both now reflected in §2.6 and A.3:

1. **The forward-reference count was over-stated by one.** The finding says the
   draft's (P2, P4, P1, P5, P3) creates "three further forward references" and
   names P2 (position 1), P4 (position 2) and P5 (position 4). P5 at position 4
   is preceded by both P1 (position 3) and P2 (position 1), so **P5's
   precondition already resolved backward** under the draft's own permutation.
   The real count is two under the strictest reading (P2's bare "Absent a
   sanctions hit" needing P1, and P4's three-part opener needing P1) and one
   under the reading the study registers. **The finding stands** — the draft's
   permutation did break its own stated principle, and the replacement is
   right — but the file now states the count that is true.
2. **The generalized constraint the finding proposes is unsatisfiable as
   worded.** "Every explicit label reference and every 'absent …' precondition
   resolves backward" would require P1 before P2, which with the derangement
   requirement admits **no permutation at all** — verified by exhaustive
   enumeration of all 120. The replacement (P2, P1, P4, P5, P3) does not
   satisfy it either: P2's own two-part opener at position 1 precedes P1 at
   position 2. §2.6 and A.3 therefore register the constraint in the form that
   is satisfiable, name the residual explicitly, and record that of the
   permutations resolving *every* reference backward the maximum-movement one
   is **(P1, P2, P4, P5, P3)** at three of five clauses moved — now D-5's
   alternative (a).

## Found while re-verifying, not raised by the review

One defect of the same class as finding 2, in a different place, and blocking
by the same standard:

- **Arm E's clause bodies are not digit-free either.** P5's body contains
  "unless P4 applies", and the `4` in that token is a digit character inside a
  clause body. §2.6's "**E**: the five bodies contain no digit character", C8
  clause 5's identical clause, and A.5's opening line were all false of arm E's
  own drafted text, and the check as written would have refused the artifact —
  exactly the failure mode finding 2 identified, one level down. **Fixed by
  registering the census definition rather than by editing the text**: §2.6
  defines the clause-body digit-run census as running over each body **with
  clause-label tokens `P1`–`P5` masked out first**, because those are
  structural cross-references present identically in all five arms and counting
  them would make every arm's census carry a `4` that says nothing about the
  intervention. Under that definition arm E's census is **empty**, A's and B's
  are `{40, 40, 70, 70, 70, 70}`, and D's is `{45, 45, 72, 72, 72, 72}` — all
  verified mechanically. Editing P5's cross-reference away was rejected: it
  would have been a further authored difference between arm E and arm A that
  the intervention does not require, which is precisely what finding 3 objects
  to.
- **A.2's printed digit-run multiset was wrong under the naive reading.** The
  draft printed "{70, 40, 70, 70, 70, 40}" for arm B's bodies; an unmasked
  `\d+` scan of those bodies returns seven runs, the seventh being the `4` of
  "P4". The masked definition above makes the printed six-element multiset
  correct as printed, and A.2 and A.4 now state which definition they are
  under.

## Arm text digests, as reviewed in this round

Per finding 21. Computed over the five arm texts **as they stand after this
round's fixes**, assembled from Appendix A by the registered assembly rule
(`PREREGISTRATION.md` Appendix A). These are the digests `harness/integrity.py`
will bind the frozen `arms/<X>/POLICY.md` files to, if this is the final round;
each subsequent round records its own.

| arm | bytes | sha256 of the arm text as reviewed in round 1 |
|---|---|---|
| **A** | 1814 | `982fb02356ec83e9fef0dd52697b1342a7f15b9fd2ffe9a76e8f113ee88e8220` |
| **B** | 1883 | `3dc5bcce96a4be4550b5d9e5b69e6316d91285ef6359a7f08ccf5aabbe5974ed` |
| **C** | 1814 | `c66505094b61b2a4c207c77fe22c92eb9e9441fb6eb7f63af0cf0615735c59ef` |
| **D** | 1814 | `dc4a19eb63fbcb0dbd0ad8e3487c448fbf922ccbe20eeb7b536d83a6385c7c47` |
| **E** | 2081 | `3fe4987fcb7bfaac3a9e33480b93772e4e88939cba7f65de4a1f1fd1c52f68a3` |

**These are digests of drafts, and they are recorded as such.** No
`arms/<X>/POLICY.md` exists yet; the harness does not exist yet; nothing is
frozen. What the table fixes is *which bytes this round reviewed*, so that a
later round's table, and the freeze, can be compared against it.

For reference, the prompts those texts produce under §2.6's equation — derived,
not authored, and recorded here because the prompt is what the model actually
receives:

| arm | prompt bytes | sha256 |
|---|---|---|
| **A** | 2761 | `7d47729076167ad0670719717bb1249398b9b86bb1ab14082b1b7510413df338` |
| **B** | 2830 | `37fc57555f0468a539c75c35989904540b0d70054b8868ec22b7f1fa8c3c169c` |
| **C** | 2761 | `cd821aab31a1651f097629b20bca4300fe4a019f5dce2de07b7daf12647e6994` |
| **D** | 2761 | `0a0992b85f8ae07a5590044eeaae5a46d809b17cc3f26cb2782bc225e9a2c456` |
| **E** | 3028 | `112a1a38e16f97bcf1b4f884aa1ddaa197b6aa0bf6d09bcc36d72a7303c10c91` |

Arm A's is 948 + 1813 = 2761, which is 011's pinned 2706 plus
`CONVENTIONS_DELTA`'s 55 bytes — the arithmetic §2.1 registers.

## Re-verification performed while applying the fixes

Every number this round put into the file was re-derived here, from source
bytes, with an exact-rational implementation, before it was written in. What
was checked and matched:

- **Clopper–Pearson**: all nine registered vectors at n = 25; the six port-
  control vectors at n = 50; the perfect-arm lower bounds at n ∈ {10, 11, 16,
  17, 20, 25, 30, 50} — including the two new ones this round registers,
  0.6915 at V = 10 and 0.7151 at V = 11.
- **Cut locations**: HIGH iff k ≥ 23 and LOW iff k ≤ 2 at n = 25; k ≥ 27 / k ≤
  3 at n = 30; k ≥ 19 / k ≤ 1 at n = 20.
- **Operating characteristics**: the whole twelve-row marginal table; the joint
  figures 0.9481 / 0.9231 / 0.8522 at p = 0.98 and 0.5806 / 0.4424 / 0.1957 at
  p = 0.95; P(all four COLLAPSE) = 0.3370; P(≥ 3 of 4 HIGH | p = 0.95) =
  0.9187; P(LOW) = 0.8129 at p = 0.06 and 0.7466 at 0.07.
- **Digests**: 010's `PROTOCOL-LOCK.json` `lockedInputs` for `POLICY.md`,
  `FAMILY.json`, `PROMPT.txt`, `policy_mirror.py`, `records_compile.py`,
  `transcript_check.py` and `authoring_call.sh`; 011's on-disk digests for all
  of them; 011's `PINS.json` for the probe prompt. Every tier assignment in
  C1's new table was checked against the artifact that carries the authority.
- **Byte arithmetic**: 2706 = 948 + 1758; `CONVENTIONS_DELTA` = 55 bytes; arm
  A = 1759 + 55 = 1814 bytes and equals 010's locked policy with the delta
  inserted, byte for byte.
- **Grid size**: 2 × 5 × 2 × 13 = 260.
- **Permutations**: all 120 enumerated against the derangement and
  backward-resolution constraints.
- **Arm-text properties**: 46 registered properties of the five assembled arm
  texts — preamble and conventions equalities, clause structure and order,
  C's byte-identity to A per label, E's P1/P2 byte-identity to A, all five
  digit-run censuses, arm E's exhaustive whole-file digit-run set, the
  permutation properties and uniqueness, and the A ↔ B inclusivity-adjacency
  pattern clause by clause — **46 pass, 0 fail**.
- **Predecessor claims**: `DIVERSITY.md` table C (2, 6, 2, 24, 26, 2), its
  headline sentence about four-of-six versus three-of-two-probes, table A's
  181 + 84 + 145 = 410 of 784, and table B's far-side values at 40 (40.01 ×3).

## What this round does not establish

- It is **not** a cross-vendor round. Same model lineage as the drafter; a
  shared prior is not an independent one. §8's commitment is to cross-vendor
  adversarial review of this file **and of the five arm texts** before the
  freeze, and that has not happened.
- **C10 has not run.** The five clean-room mirrors do not exist. Finding 5's
  registered consequence — that an arm E whose clean-room reader cannot derive
  (40, 70) is re-authored before the freeze — is a commitment, not a result,
  and the reviewer's own recommendation is to commission the readers in
  parallel with the next round because their verdict may force a re-authoring.
- **No harness exists**, so nothing in §6 has been executed. Every check
  described in this file as "checked in code" is specified, not implemented.
- The **maintainer decisions** recorded above (findings 1, 4, 7, 15) are
  choices, not findings, and each one's alternative is live in §10 for the
  cross-vendor rounds to move.
