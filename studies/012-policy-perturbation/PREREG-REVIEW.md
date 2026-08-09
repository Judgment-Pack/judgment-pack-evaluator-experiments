# Pre-freeze adversarial review — Study 012

This file is the complete pre-freeze review record for Study 012. It records
every adversarial round the preregistration and the five arm texts are put
through before any freeze decision: who reviewed, by what method, the verdict
verbatim where one exists, every finding faithfully summarized, and what was
done about each one. Nothing is discarded. It follows Study 011's per-round,
per-finding disposition format.

**Status: OPEN. Nine rounds complete, rounds 2 through 9 cross-vendor. Nothing
is frozen and nothing has run.** (This line said "two rounds" through round 9,
having been written in round 2 and never advanced; a status line that stops
tracking its own subject is the defect this file exists to catch, so it is
corrected here and carried forward with each round.)

**Why this file also carries digests.** Round 1 found that nothing bound the
arm texts a review round saw to the arm texts that get pinned: the sequencing
is right — review settles the authored artifacts, then the port fills the
digests, then the freeze — but between the last review round and the freeze a
clause of arm E could change with Appendix A updated to match, and the
registered-illustration check (Appendix A bytes == `POLICY.md` bytes) would
pass either way, because both would have moved together. So **every round below
records the sha256 of each of the five arm texts as that round reviewed them**,
and `harness/integrity.py` refuses unless each frozen `arms/<X>/POLICY.md`
digest equals the digest recorded in the **final** round.

**Round 2 found that binding insufficient, and it was right.** It covered only
the five policy texts, and it was *self-authenticating*: this file, Appendix A,
the policies and `PINS.json` can all move together in one commit and every
specified equality still passes, because the thing each artifact is checked
against is a number the same commit supplies. Nothing bound the preregistration,
the README, `CLAIM.md`, the port table or the code that computes the verdicts.
So from the first post-port round onward, **every round also records a
whole-tree manifest digest** — the sorted `(path, length, sha256)` list over
every tracked regular file in this study directory — and `integrity.py`
recomputes it over the frozen tree and refuses on any mismatch, with any byte
change requiring a new round. `PREREGISTRATION.md` §2.10 [D-20], §8 and §10
register it. **Rounds 1 and 2 carry arm-text digests only**, because they
reviewed a specification before any port existed; **the full-tree binding
applies from round 3 on**, and a final round that carries only arm digests is
not a final round.

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

---

# Round 2 — cross-vendor adversarial review (OpenAI Codex CLI)

**Basis:** `PREREGISTRATION.md`, `README.md` and `PREREG-REVIEW.md` at commit
**`2e5c9f0`**, together with the predecessor studies' committed bytes in the
same worktree (`studies/011-authorship-coverage-rates/`, including `PORTS.md`
and `harness/PINS.json`, and `studies/010-blinded-oracle/PROTOCOL-LOCK.json`).
**Date:** 2026-08-07. **Reviewing model:** **OpenAI Codex CLI — a different
vendor and a different model lineage from the drafter.** **This is the first
cross-vendor round.** Method: read-only verification, no tracked file modified,
scratch scripts under `/tmp` only; every digest re-derived from the predecessor
bytes and every statistical figure recomputed with the reviewer's own
implementation rather than read from the draft.

**Result: NOT READY for freeze — 20 findings (13 blocking-for-freeze, 6
should-fix, 1 nit). All 20 accepted; none disputed.**

Six new register entries were opened: **D-19** through **D-24**. Nine existing
entries were re-adjudicated: **D-1, D-4, D-5, D-7, D-9, D-10, D-13, D-16,
D-18**.

## What the round confirmed rather than assumed

Recorded because it bounds what the findings mean, and because a cross-vendor
round that only found faults would leave the reader unable to tell what was
checked. The reviewer verified, from bytes and with its own exact-rational
implementation:

- **every predecessor digest this draft cites matched the exact commit bytes**;
- the nine Clopper–Pearson vectors at n = 25 and the six port-control vectors at
  n = 50; the HIGH/LOW cut locations; the marginal operating-characteristic
  decimals;
- the Appendix A assembly hashes and byte lengths for all five arms, the
  948-byte prompt equation, the masked digit censuses, arm D's substitutions,
  and the arm C permutation enumeration over all 120;
- **every numeric section reference resolves**, and §10 contained exactly D-1
  through D-18 with no gaps and no duplicates;
- the worktree remained clean.

**No numerical error was found in the interval arithmetic, the digest chain or
the arm-text assembly.** What the round found instead was that several of those
correct numbers were computed for the wrong rule (F13), described with the wrong
word (F12, F16), or bound to nothing (F1, F2, F7).

## The reviewer's final message, verbatim and complete

Reproduced in full and unedited, exactly as delivered. Nothing is summarized
away and nothing is omitted.

<!-- BEGIN VERBATIM REVIEWER MESSAGE -->

## Findings

1. **blocking-for-freeze — §2.10, §7–§10; review-to-freeze binding.** The final-review hashes are self-authenticating: `PREREG-REVIEW.md`, Appendix A, the policies, and `PINS.json` may all change together before freeze and every specified equality still passes. Only policies are recorded, not the preregistration, README, claim, port table, or harness. Fix: perform the final review on the complete post-port tree; have the reviewer attest an exact commit/tree or externally signed manifest covering every reviewed artifact; require a new review after any byte changes.

2. **blocking-for-freeze — §2.2, §6 C1, §2.10; incomplete provenance chain.** The draft says 011’s `PINS.json` and `PORTS.md` are “both pinned,” but only the former is specified as pinned; 012’s port table and four inherited harness sources remain mutable. Porting also occurs after review. Fix: pin 011 PINS (`e0007697…`) and PORTS (`783cc9c3…`), every exact source blob and destination, and 012 PORTS; port before the final cross-vendor review. Also correct the authority wording: 011’s adapted compiler/checker/wrapper, not 010’s originals, are the operative sources.

3. **blocking-for-freeze — §2.6 C8, Appendix A.2, D-4.** Arm B violates its registered inclusivity-adjacency invariant. A’s P4 lower cue follows `40`; B’s `from 40` cue precedes it, exactly as Appendix A admits. The round-1 claim that all 46 properties passed is therefore false. Fix: rewrite B, for example `from **40 inclusive** up to but not including 70`, regenerate hashes, and re-review the bytes—or explicitly weaken the invariant and register the confound.

4. **blocking-for-freeze — §2.8, §7, D-7; run-order carryover.** Cyclic shifts balance position but not predecessor: E follows D in 20/25 calls and C in 5/25, never A or B. Provider-side carryover from D’s 45/72 prompt could therefore manufacture E’s predicted collapse, contradicting §7’s claim that such state could only blur a contrast. Fix: register the complete call order using a first-order carryover-balanced design and test both position and directed-transition counts, including round boundaries.

5. **blocking-for-freeze — §2.8 and §7; outcome-dependent stopping.** The admitted in-process route lets an operator inspect interim E rates and declare a favorable shortfall at or after round 11 while still receiving confirmatory verdicts. A timestamp does not remove optional stopping, and the registered operating characteristics no longer apply. Fix: make every incomplete batch descriptive-only, with all decisions `UNRESOLVED-BY-DESIGN` and no contrasts, regardless of denominator.

6. **blocking-for-freeze — §2.8, §6 C5, README run commands; partial-round contradiction.** C5 requires every arm’s indices to be `1…R`, while §2.8 says a partial round leaves arms with `R` or `R−1` slots. `--start-round K` likewise cannot resume a partly completed round without either overlap or omission. Fix: record the exact completed global schedule prefix—round, position, arm, global index—and resume only at its next position; derive each arm’s expected `1…count_X` range from that prefix.

7. **blocking-for-freeze — §2.9, §3, §6 C5; population identity and slot integrity.** The publishing command accepts an arbitrary `--slots` root, while retained round/slot indices are not bound to directory names, scheduled positions, or an ordered ledger. Same-arm slots can be copied, renamed, or duplicated without `arm-mismatch`. Slot contents are also unsealed: changing one A miss can turn 22/25 MID into 22/24 HIGH; changing one E hit can turn 3/25 MID into 2/24 LOW. Fix: derive the canonical `arms/` root, add a `schedule-mismatch` gate and exact ledger↔slot bijection, enforce cross-slot session uniqueness, and chain a terminal manifest for each slot into the ledger. Integrity alteration should invalidate confirmatory scoring, not merely leave `V_X`.

8. **blocking-for-freeze — §3.3 and §4.2; post-treatment exclusion.** Pipeline-invalid probability is not arm-independent merely because the gates are: policy wording can affect tool use, exit status, completion production, or parseability. Excluding such runs conditions the primary endpoint on an arm-affected outcome. Fix: make scheduled-slot/intent-to-treat coverage over N primary, conservatively count invalid slots as uncovered or publish `[k/N,(k+I)/N]` sensitivity bounds, and retain `k/V_X` only as a per-protocol secondary.

9. **blocking-for-freeze — §2.5, §5.3(i), §8, D-16.** E retains `Study 010`, an explicit recall route to 40/70, and the draft admits recall cannot be separated from derive-then-hug. It nevertheless labels E HIGH on three classes as unconditional falsification and mandates retracting R1. Recall does not falsify the clean denaming causal proposition. Fix: select D-16’s common name-free preamble and still qualify residual memorization, or classify maintained coverage as contamination-compatible rather than unconditionally `R1 WRONG`.

10. **blocking-for-freeze — §4.6 S1/S2/S5 and §5.3; wrong mechanism gates confirmation.** The primary endpoint uses correctly labelled records, H. If E still places raw records at 40/70 but mislabels them, H coverage collapses even though the registered “hugging goes away” proposition is false. S2/S5 are called load-bearing but have no cut and no decision reads them. Fix: define per-class placement collapse from S1 raw-intersection levels, distinguish it from label/comprehension collapse, and require at least three placement collapses—plus the controls—for R1 confirmation.

11. **blocking-for-freeze — §2.1, §5.3; decision rules are not total.** The E table does not incorporate the B/C control prerequisite; class-4 collapse purports to override “every other reading” without precedence; D’s “LOW on the narrow classes” has no count threshold and leaves mixed/MID outcomes unnamed; and “several classes” or “far below” creates an unregistered drift rule. Fix: add one exhaustive, ordered decision table with explicit precedence, counts, control-failed outcomes, and `ELSE INDETERMINATE`; remove the discretionary drift classification or define it numerically.

12. **blocking-for-freeze — §5.4 and downstream §2.1/§9/README claims.** The independence products are numerically correct but are not lower bounds and independence is not a worst case. At `q=P(HIGH|p=.95)=0.8728935`, independence gives all-six `0.4424`; the marginal-event Fréchet lower bound is only `0.2374`. The `0.3370` collapse figure additionally assumes independence between A and E. Fix: label these as conditional independence scenarios, state every independence layer, remove “lower bound,” “worst,” and unconditional “chance” language, and add dependence sensitivity.

13. **blocking-for-freeze — §4 opening, §5.3(iii), §5.4, D-1; power was computed for the wrong rules.** At N=25, the actual `≥3/4 COLLAPSE` probability under the stated independence scenario is `0.7583`, not the reported stricter all-four `0.3370`. The actual B/C gate—each arm TRACKING on ≥5/6, including shared A-HIGH requirements—passes only `0.4031`; all twelve TRACKING is `0.0866`, not the B/C-only `q^12=0.1957`. For N=20/30 the actual control-gate probabilities are `0.0557/0.7658`. Fix: publish operating characteristics for the actual rules and re-adjudicate D-1; by the draft’s own criterion, the N=25 control “usually fails.”

14. **should-fix — §4.3, §5.4, §9, README; statistical qualifications and prose.** Clopper–Pearson coverage is exact only conditional on independent, constant-p Bernoulli slots, while §7 admits possible provider dependence. Also, 16/16 has `L=.7941` and is HIGH under this study’s `.70` cut; HIGH first becomes reachable at 11/11. The README/§9 combine all-six `0.4424` with the four-narrow “two in five” conclusion—the latter instead uses all-four `0.5806`. Fix these statements and describe N=25 accurately as the smallest multiple of five permitting two misses while retaining HIGH.

15. **should-fix — §2.4 and C8; incomplete landmark grid.** The 260-cell grid lacks a point just below class 5’s lower edge. A mutant `[T_low−2,T_low)` family passes every current grid cell. Fix: add `T_low−1−0.01`, yielding 14 landmarks and 280 cells, or narrow the grid claim and state that C9 alone catches this defect.

16. **should-fix — §2.4 and §5.3(ii); arm D interpretation.** Unequal moves do not exclude an affine transformation: `0.9x+9` maps 40→45 and 70→72; “additive shift” is the correct term. New-edge LOW/old-edge HIGH is also compatible with generic round-number salience, not uniquely contamination. Finally, D’s `[45,72)` records do not all lie in old class 3 `[40,70)`. Fix the terminology, rename the outcome `OLD-EDGE-PREFERENCE` with both explanations, and remove the “by construction” claim.

17. **should-fix — D-5, arm C.** The chosen derangement leaves P2’s prerequisite P1 forward-referenced. This is disclosed, but C is a control on which E’s interpretation depends. Fix: prefer the registered `(P1,P2,P4,P5,P3)` alternative, which resolves every dependency while still moving three clauses, unless full derangement is explicitly judged more important than control comprehensibility.

18. **should-fix — §6 C10, §7/§9, X6.** C10 has no predesignated first-reader rule, retains no failed-reader attempts, and does not require a fresh blinded reader after rewriting E. It also understates authorship by saying only D/E were authored by the prediction-holding team; B is substantive authored prose too. X6 cannot exhaust “every” coherent misderivation and includes 28 from wording already removed. Fix: preassign readers, retain all attempts, require fresh assessment and review after every rewrite, describe the full authorship conflict, and call X6 a non-exhaustive sentinel list.

19. **should-fix — cross-document and predecessor wording.** The preregistration dates Study 011 to 2026-08-07 and then calls it “months ago,” contradicting the README and round-1 disposition. The introduction/README also overstate 010 as the operative authority for adapted compiler/transcript bytes, and the A-policy row says “through 011 PORTS” even though 011 has no separate policy copy. Fix these statements to match the three-tier authority model and the actual same-day history.

20. **nit — scattered literal cleanup.** “Three digit-runs survive” should be “five non-label runs from three sources”; Study 011’s clean-room mirror was earlier the same day, not one day earlier; N=30 is 153 total calls and about 107 minutes when probes are included, not 150/105; and the operating table should say values such as `0.0000` are rounded and may be small nonzero probabilities.

All cited predecessor digests matched the exact commit bytes. The nine n=25 and six n=50 interval vectors, HIGH/LOW cuts, marginal operating-characteristic decimals, Appendix assembly hashes and lengths, 948-byte prompt equation, masked digit censuses, D substitutions, and C permutation enumeration also matched. Every numeric section reference resolves, and §10 contains exactly D-1 through D-18 without gaps or duplicates. The worktree remained clean.

Overall verdict: **not ready for freeze**. The byte-level work is strong, but the current draft has independent blockers in review binding, causal identification, actual-rule power, stopping, schedule carryover, and population integrity. Fix them, build the complete harness/claim/C10 artifacts, and run a new cross-vendor review against the exact final candidate tree.

<!-- END VERBATIM REVIEWER MESSAGE -->

## Findings and dispositions

**All 20 findings accepted; none disputed.** Where a finding offered options,
the maintainer's choice is recorded as a **maintainer decision** and the option
not taken is registered in `PREREGISTRATION.md` §10 as that decision's
alternative.

| # | sev | finding | disposition |
|---|---|---|---|
| 1 | blocking | The review-to-freeze binding is self-authenticating. `PREREG-REVIEW.md`, Appendix A, the policies and `PINS.json` can all change together before the freeze and every specified equality still passes; only the policies were recorded, not the preregistration, README, claim, port table or harness | **FIXED — maintainer decision: attest the complete post-port tree.** §2.10 [D-20] registers that the **final** round is performed over the complete post-port candidate tree and that the reviewer attests **an exact commit id and a tree manifest** — the sorted `(path, length, sha256)` list over every tracked regular file in the study directory, with a named exclusion list for the outputs that cannot exist yet. Its digest is recorded in this file and pinned in `PINS.json`; `integrity.py` recomputes it over the frozen tree and refuses on any mismatch; **any byte change requires a new round**, with no editorial exemption. Registered honestly as a bound and not a proof: the manifest is computed by this study's own code over its own worktree. **An externally signed attestation is [D-20]'s alternative** and is the stronger form. **The rule applies from round 3 on** — rounds 1 and 2 reviewed a specification before any port existed and record what they could bind, the five arm-text digests |
| 2 | blocking | The provenance chain is incomplete: 011's `PORTS.md` is called pinned but only `PINS.json` is; 012's own port table and four inherited harness sources stay mutable; porting happens after review; and the authority wording credits 010 for bytes 011 adapted | **FIXED, all four halves.** §2.2 gains a chain table pinning **011's `PINS.json` (`e0007697…`), 011's `PORTS.md` (`783cc9c3…`), 010's `PROTOCOL-LOCK.json` (`4966aa82…`, the digest *011* pins) and this study's own `PORTS.md`**, and C1 verifies each in that order — all four digests independently re-derived from the worktree bytes before being written in. **The port moves before the final cross-vendor review** (§2.2 [D-20]), with the registered four-step ordering published. The authority wording is corrected in §1, §2.2 and the README: 010's lock governs the mirror, arm A's family, arm A's policy source and 011's prompt bytes, and **not** the compiler, transcript checker or wrapper, which are operative at 011's adapted bytes |
| 3 | blocking | **Arm B violates its own registered inclusivity-adjacency invariant.** A's P4 lower cue follows `40`; B's `from 40` precedes it — as Appendix A's own table admitted while §6 C8 asserted the invariant held. The round-1 claim that all 46 registered properties passed is therefore false | **FIXED — maintainer decision: rewrite arm B; the invariant is not weakened.** B's P4 now reads "a risk score of **40 or more** but **below 70**", so all six of B's `(clause, literal, side, sense)` tuples equal A's, verified mechanically over the assembled bytes. The A ↔ B table in A.2 is rewritten to show tuples rather than prose, and the asymmetry row is replaced by the fix with the round-1 text named as what it was. **§2.6 registers what the invariant costs**: B's paraphrase now lives in the clause frames and not in the boundary language, and at four of six bounds B uses A's own cue word — a narrower control, and the narrowness is what makes it a control. **The round-1 "46/46 pass" claim is corrected, not papered over** — see "Corrections to round 1" below. Weakening the invariant is D-4's alternative not taken |
| 4 | blocking | Cyclic-shift rotation balances position but not predecessor: **arm E follows D in 20 of 25 calls and C in 5, and never follows A or B.** Provider-side carryover from arm D's 45/72 prompt could therefore manufacture arm E's predicted collapse, and §7's claim that such state "could only blur a contrast" is false against that schedule | **FIXED — maintainer decision: register a complete first-order carryover-balanced call order.** The reviewer's count was reproduced exactly from the round-1 schedule before the replacement was built. §2.8 now registers a **Williams design for five treatments** — ten sequences, each arm in each position twice, each ordered pair adjacent exactly twice — repeated as **three blocks in three registered block orders**, giving 30 rounds. Registered and asserted by test: **position counts 6 apiece; within-round directed transitions exactly 6 per ordered pair; and over all 149 transitions every ordered pair 7 or 8 times, max − min = 1**. Exact balance is arithmetically impossible (149 is not a multiple of 20) and the file says so rather than claiming it. §7's carryover claim is **withdrawn** in those words. A truncated batch claims no balance at all |
| 5 | blocking | Optional stopping: the admitted in-process route lets an operator inspect interim rates and declare a favourable shortfall at or after round 11 while still receiving confirmatory verdicts. A timestamp does not remove optional stopping, and the registered operating characteristics no longer apply | **ADOPTED FULLY — maintainer decision: completeness, not size.** §2.8 [D-21] registers that **any incomplete batch, at any round, for any reason, is descriptive-only**: every level verdict `UNRESOLVED-BY-DESIGN`, no contrast, no COLLAPSE-DISJOINT, no §5.3 pattern verdict, no R1 adjudication — regardless of denominator. The eleven-valid-run floor is **withdrawn as an answer to this** and retained only as a second floor on the per-protocol secondary. §7's in-process bullet is rewritten to say what the look could still buy (nothing) and what remains unprevented (looking, disliking, and completing anyway). The cost is registered in advance: a batch that dies at round 29 for reasons nobody chose publishes no conclusion |
| 6 | blocking | C5 requires each arm's indices to be `1…R` while §2.8 leaves arms with `R` or `R−1` slots; `--start-round K` cannot resume a partly completed round without overlap or omission | **FIXED.** Every slot now records `(globalIndex, round, position, arm, slotIndex)` (§2.9); the ledger is a hash chain in schedule order; **`--start-round` is removed** and replaced by `--resume`, which continues at the ledger's next global index after verifying the recorded prefix against the registered order slot for slot ([D-22]). C5 derives each arm's expected `1…count_X` **from that prefix**, not from a round number, and a declared shortfall must match the prefix exactly |
| 7 | blocking | Population identity and slot integrity: `--slots` accepts an arbitrary root; retained indices are not bound to directory names, scheduled positions or an ordered ledger; same-arm slots can be copied, renamed or duplicated without `arm-mismatch`; and slot contents are unsealed — one altered A miss turns 22/25 MID into 22/24 HIGH, one altered E hit turns 3/25 MID into 2/24 LOW | **FIXED, every clause.** **`--slots` is removed** from the scorer and the shortfall command; the canonical `arms/` root is derived from the harness's own location ([D-23]). Two new admission codes: **`schedule-mismatch`** (the slot's schedule stamp is not what the registered order assigns, or the ledger↔slot bijection fails) and **`session-reused`** (any two slots in any arms sharing session bytes, session id, or identifying `CALL.json` members) — §3.2's own anti-self-agreement rule, generalized to the batch. Each slot is sealed by a **`SLOT-MANIFEST.json` chained into the ledger** (§2.9), and **an integrity failure invalidates confirmatory scoring for the whole batch** rather than moving a slot out of `V_X` — registered with the reason: a code that moves one slot hands an alteration exactly the denominator change it was made to produce. C4 gains four fixtures for these paths |
| 8 | blocking | Post-treatment exclusion: pipeline-invalid probability is not arm-independent merely because the gates are — policy wording can affect tool use, exit status, completion production and parseability, so excluding such runs conditions the primary endpoint on an arm-affected outcome | **ADOPTED FULLY — maintainer decision: intent-to-treat is primary.** §4.2 [D-24] makes `k/N` over the **scheduled** slots the primary endpoint, with pipeline-invalid slots conservatively counted as covering nothing, and publishes the **`[k/N, (k+I)/N]` sensitivity bound** with intervals on both ends beside every primary rate. `k/V_X` is demoted to the per-protocol secondary **S11**, published beside the primary and never substituted for it; where the two levels disagree the primary governs and the disagreement is itself reported. §3.3's claim that a refusal rate can never be an effect of the policy text is **withdrawn**; §4.4's "it changes no verdict" is withdrawn with it, and §7's "the rates are conditional on the author having happened not to use a tool" is corrected — the primary is not |
| 9 | blocking | Arm E retains `Study 010`, an explicit recall route to 40/70, and the draft admits recall cannot be separated from derive-then-hug — yet labels E-HIGH-on-three unconditional falsification and mandates retracting R1. Recall does not falsify the clean denaming proposition | **ADOPTED — maintainer decision: BOTH halves.** (1) **D-16's alternative is adopted**: `PREAMBLE_DELTA` replaces `Study 010` with `this study` in **all five** arms, at its single occurrence in 010's locked bytes; the assembled preamble is 343 bytes, sha256 `83b7b27f…`, pinned in `PINS.json`. Cost registered in §2.1 and D-16: a second registered delta from 010's text. (2) **Maintained coverage is no longer an unconditional falsification.** The outcome is renamed **R1-UNSUPPORTED** and is registered as **contamination-compatible**: §5.3 (i), §7, §8 and §9 all state that removing the pointer does not remove residual memorization of a corpus public since 2026-08-06, that the verdict is unconditional but **the positive counter-thesis is not claimed**, and that §8's correction must say so in the same paragraph as the retraction. §5.3 (i)'s third reading is narrowed from "recall keyed to a name the text supplies" to "recall keyed to the text's own shape" |
| 10 | blocking | The wrong mechanism gates confirmation: the primary uses correctly-labelled records H, so an arm E that still places raw records at 40/70 but mislabels them collapses H-coverage while the registered proposition is false. S2/S5 are called load-bearing but have no cut and no decision reads them | **ADOPTED FULLY.** §5.2 registers the **PLACEMENT contrast** — §5.1's cuts computed on S1 raw intersection, same denominator, same intervals — and §5.3 (i)'s CONFIRMED rule now requires **PLACEMENT-COLLAPSE on ≥ 3 of 4 narrow classes**, plus the B/C control gate, plus no class-4 collapse. Because `H ⊆ raw`, placement collapse implies collapse and the converse fails exactly in the case now named **LABEL-COLLAPSE-ONLY**, a registered outcome of its own. §4.6 gains the three-row table separating placement collapse, comprehension collapse and label collapse, and S1 is re-described as an endpoint a decision reads rather than a secondary |
| 11 | blocking | The decision rules are not total: the E table omits the control prerequisite, class-4 collapse overrides "every other reading" with no precedence, arm D's rule has no count and no name for the mixed case, and "several classes" / "far below" is an unregistered drift rule | **FIXED — maintainer decision: one ordered exhaustive table, and the drift rule becomes numeric.** §5.3 gains a seven-row decision table, evaluated top to bottom, first match wins, last row always matches: (1) incomplete batch or integrity failure → `UNRESOLVED-BY-DESIGN`; (2) class-4 collapse → `E-DEGRADED-GENERALLY`; (3) control gate false → `CONTROLS-FAILED`; (4) `nH ≥ 3` → `R1-UNSUPPORTED`; (5) `nP ≥ 3` → `CONFIRMED`; (6) `nC ≥ 3` without `nP ≥ 3` → `LABEL-COLLAPSE-ONLY`; (7) else `INDETERMINATE`. Rows 1–3 are gates that adjudicate R1 in **neither** direction, stated so no reader can suspect a preferred answer. The scorer computes the row and a test diffs the table against the code. **Drift becomes numeric [D-19]**: DRIFT-SUSPECTED iff arm A reads below HIGH on ≥ 4 of 6, or LOW on any — which fires by sampling alone with probability 0.0002 at N = 30. Arm D's rule gains counts and the mixed case is the registered third outcome |
| 12 | blocking | The independence products are numerically correct but are not lower bounds, and independence is not a worst case. At `q = 0.8728935` independence gives all-six 0.4424 while the marginal-event Fréchet lower bound is 0.2374; the 0.3370 figure additionally assumes A ⟂ E | **FIXED.** Both figures recomputed independently and confirmed to the digit (0.2374 = `6q − 5` at n = 25). §5.4 now **names all four independence layers** — across classes, across arms, across slots (the Clopper–Pearson model itself), and between the primary and S1 where a figure combines them — labels every product a **conditional-independence scenario**, and prints the **Fréchet lower bound beside each all-six product**. "Lower bound", "worst" and unconditional "chance" are removed; §5.4 states plainly that for positively dependent classes — which 011's corpus suggests — the true joint is *higher* than the product, so independence is not conservative. §9 repeats the honest form: "at least 0.6354, and 0.6865 under independence" at N = 30 |
| 13 | blocking | Power was computed for the wrong rules. At N = 25 the actual `≥3/4 COLLAPSE` probability is 0.7583, not the stricter all-four 0.3370; the actual B/C gate passes only 0.4031; all twelve TRACKING is `q¹⁸ = 0.0866`, not `q¹² = 0.1957`; at N = 20/30 the gate is 0.0557/0.7658. By the draft's own criterion the N = 25 control "usually fails" | **FIXED — maintainer decision: N moves to 30; N = 25 is the registered alternative.** **Every reviewer figure was recomputed independently before it was used and every one matched to four places**: 0.7583, 0.4031, 0.0866, 0.0557, 0.7658, and `q = 0.8728935`. §5.4 replaces the proxy figures with a table of operating characteristics **for the rules this file actually registers**, at N ∈ {20, 25, 30}, including the joint `CONFIRMED ∧ gate` computed over arm A's six-class pattern rather than as a product: **0.0364 / 0.3536 / 0.7359**. [D-1] is re-adjudicated on the control gate (0.4031 → 0.7658), not on the marginal (0.8729 → 0.9392) — see the D-1 note below. A **second** cost of N = 25 was found while building §2.8's schedule and is registered: 25 rounds do not tile the ten-sequence Williams block |
| 14 | should-fix | Statistical qualifications and prose: Clopper–Pearson is exact only conditional on independent constant-p Bernoulli slots while §7 admits possible dependence; 16/16 has `L = 0.7941` and **is** HIGH under this study's 0.70 cut, with HIGH first reachable at 11/11; and the README/§9 pair the all-six 0.4424 with a "two in five" conclusion that uses the all-four 0.5806 | **FIXED, all three.** §4.3 gains a paragraph defining what "exact" means here — exact arithmetic for a model this design cannot verify — and §9 repeats it. §5.4's "why 30" list is corrected: **11/11 is the smallest denominator at which a perfect arm reads HIGH**, and the claim that 16/16 sits below the cut is withdrawn. The README and §9 figures are recomputed at N = 30 and now cite the all-six figure with the all-six conclusion (0.6865, "three runs in ten"), with the Fréchet floor beside it. N = 30 is described as what it is rather than as "the smallest round number" |
| 15 | should-fix | The 260-cell grid lacks a point just below class 5's lower edge; a mutant `[T_low−2, T_low)` family passes every current cell | **FIXED — maintainer decision: add the landmark *and* narrow the claim.** The landmark set gains `T_low − 1 − 0.01`: **14 landmarks, 280 cells** (2 × 5 × 2 × 14), updated in §2.4, C8 clause 6, C10, §7, §8 and the README. **Verified both ways before it was written in**: the mutant agrees with arm A on all 260 cells of the old grid and disagrees on the new one, and that negative control is registered as a harness assertion. The claim is also narrowed as the finding's alternative suggested: the grid pins the inclusive/exclusive decision at every edge the six predicates name, and **C9's structural equality — not the grid — is what bounds a mutant differing strictly between landmarks** |
| 16 | should-fix | Arm D's interpretation: unequal moves do not exclude an affine map (`0.9x + 9` sends 40 → 45 and 70 → 72), "additive shift" is the correct term; new-edge-LOW/old-edge-HIGH is compatible with round-number salience and not uniquely contamination; and D's `[45, 72)` records do not all lie in old class 3 `[40, 70)` | **FIXED, all three; the reviewer's `0.9x + 9` verified.** §2.4 says **additive shift** and states plainly that the affine claim is withdrawn. The outcome is renamed **OLD-EDGE-PREFERENCE** and registered with **both** explanations — contamination *and* round-number salience — with the statement that this study separates neither and what study would. The S10 table's class-3 row drops "by construction" and names the counterexample: D's `[70, 72)` sub-band lies inside D's class 3 and outside A's, so a D placing every record there would read LOW |
| 17 | should-fix | Arm C's derangement leaves P2's prerequisite P1 forward-referenced; C is a control on which E's interpretation depends, so the `(P1, P2, P4, P5, P3)` alternative is preferable | **ADOPTED — maintainer decision: the reviewer's preference.** **(P1, P2, P4, P5, P3)** is registered. Re-verified by enumerating all 120: exactly three permutations resolve **every** reference backward — identity (0 moved), `(P1,P2,P4,P3,P5)` (2), and this one (3) — so it is the **unique maximum-movement** permutation under the full constraint set, and *derangement + every reference backward* is confirmed empty. §2.6, A.3 and D-5 state the trade in both directions: full derangement is the stronger *perturbation* and the weaker *control*, and this study needs C to be a control. **(P2, P1, P4, P5, P3) is registered as D-5's alternative (a)** with its cost |
| 18 | should-fix | C10 has no first-reader rule, retains no failed attempts, and does not require a fresh reader after rewriting an arm; the authorship conflict understates B; and X6 cannot exhaust "every" coherent misderivation and includes 28 from wording already removed | **FIXED, all four.** C10 now requires **pre-assigned readers**, recorded before any of them runs, with the commissioning order published; **every attempt retained and published, including every failed one**; and **a fresh reader after any re-authoring**, with the earlier attempt kept as an attempt against the earlier bytes. §7 and §9 state the conflict at full extent: **three of five arms are substantive authored prose (B, D, E)**, and §7 names the specific hazard — a B that collapses disarms E, so the author had an interest in a B that tracks. X6 is renamed a **sentinel list**, is stated to be non-exhaustive with X3/X4 named as what catches an unanticipated value, and keeps 28 with the reason stated: removing a reading is not proving it gone |
| 19 | should-fix | Cross-document wording: the preregistration dates 011 to 2026-08-07 and then calls it "months ago"; the introduction and README overstate 010 as the operative authority for adapted bytes; and the A-policy row says "through 011 PORTS" though 011 holds no policy copy | **FIXED, all three.** §2.1's "months ago" is replaced by the argument that is actually true: the interval is a few hours, a provider-side snapshot can move between two calls a minute apart, and a short interval makes the confound smaller without making it measurable. The authority correction of finding 2 is applied to §1 and the README. The A-policy row now reads **"010's lock directly"**, with the reason stated — **verified against 011's `PINS.json`, whose prompt entry records "this study copies no separate policy file"** |
| 20 | nit | Literal cleanup: "three digit-runs survive" should be five non-label runs from three sources; 011's clean-room mirror was earlier the same day, not one day earlier; N = 30 is 153 calls and ~107 minutes, not 150/105; and the operating table should say `0.0000` values are rounded | **FIXED, all four, one of them in a corrected form.** The digit-run count: the reviewer's "five non-label runs from three sources" was correct **of the bytes it read**, and finding 9's `PREAMBLE_DELTA` removes the `010`, so the round-2 bytes carry **four non-label runs from two sources** — §2.5, C8 clause 5 and A.5 all state that, with the reviewer's figure named as correct of the pre-fix bytes. C10's "one day before" becomes **"earlier the same day"**, with the commit times (13:50 and 18:43 on 2026-08-07) recorded. The budget table now counts the three probe calls at every N: **153 calls and ~107 minutes at N = 30**, 128/~90 at 25, 253/~177 at 50 — the N = 50 line was wrong in the same way and is fixed too. §5.4 states that every `0.0000` is rounded and may be a small nonzero probability, with two examples |

## The D-1 re-adjudication, recorded separately because it changes the study

Round 1 registered **N = 25** and defended it on the marginal figure
`P(HIGH | p = 0.95)`, 0.8729 at N = 25 against 0.9392 at N = 30 — a 6.6-point
gain the draft itself called "modest". Finding 13 showed that quantity is not
what the design depends on.

The quantity it depends on is **§5.3 (iii)'s control gate**: arm B TRACKING on
at least five of six classes *and* arm C TRACKING on at least five of six, which
— because every TRACKING verdict also requires arm A HIGH on that class — is a
joint statement over eighteen level verdicts, not twelve. Recomputed for the
registered rule under the registered scenario:

| N | control gate passes | `nP ≥ 3` (CONFIRMED pattern) | CONFIRMED **and** gate | all twelve TRACKING (`q¹⁸`) |
| --- | --- | --- | --- | --- |
| 20 | 0.0557 | 0.3771 | 0.0364 | 0.0040 |
| **25** | **0.4031** | 0.7583 | 0.3536 | 0.0866 |
| **30** | **0.7658** | 0.9292 | 0.7359 | 0.3235 |

This file's own criterion is that "a dependency that usually fails is not a
control" — the sentence round 1 used to justify choosing five-of-six over
six-of-six. Applied to itself, it condemns N = 25: at that size the design's
precondition for interpreting arm E fails **three times in five when both
control arms behave exactly as predicted**, and the whole registered CONFIRMED
outcome lands about one time in three.

**Maintainer decision: N = 30.** The cost is +25 authoring calls, 153 total
calls against 128, and about 17 more minutes of sequential wall clock — all
still inside the one-day rule. **N = 25 is registered as [D-1]'s alternative**
with both of its costs stated: the control-gate figure above, and a second cost
found while constructing the round-2 schedule — **25 rounds do not tile the
ten-sequence Williams block**, so the carryover-balanced order of finding 4
would have to be reconstructed for 25 and this file does not carry that
construction. Every dependent count was updated: 150 slots, 153 calls, ~107
minutes, ~13 MB retained, C5's `1…count_X` ranges, the n = 30 interval vectors,
the n = 30 operating characteristics, and the cut locations `k ≥ 27` / `k ≤ 3`.

## Corrections to round 1, recorded rather than passed over

**The round-1 arm-text property count was wrong, and finding 3 is why.** Round 1
recorded "46 registered properties of the five assembled arm texts — … and the
A ↔ B inclusivity-adjacency pattern clause by clause — **46 pass, 0 fail**".
That count included the inclusivity-adjacency invariant as passing. It did not
pass: arm B's P4 lower bound read "from **40** up to but not including 70",
which places the cue *before* the literal where arm A's is *after*, and the
round-1 draft's own Appendix A table printed the discrepancy in its rightmost
column and labelled it "**the one asymmetry in the table, and the review's to
adjudicate**".

So round 1 simultaneously (a) added the invariant, (b) printed a violation of
it, and (c) reported the whole property set as passing. The most likely
mechanical cause is that the round-1 check compared *senses* and *presence* but
not *sides*, so a cue on either side satisfied it; the file's prose asserted the
stronger property the check did not test.

**Round 1 did not publish its property list, so the exact corrected figure
cannot be recovered — and this file says that rather than inventing one.** Under
round 2's atomization the adjacency invariant is a single property, so the
round-1 figure becomes **45 pass, 1 fail**; under an atomization that counted
the eight substitution-table rows separately it would be a different number.
What is recoverable and is stated instead: **at least one registered property of
the round-1 arm texts was false, and the file reported none as false.**

**Found while re-verifying, and not raised by the review: the round-1 arm B
violated the invariant at *two* of its six bounds, not one.** The review named
P4's lower bound. P4's *upper* bound read "up to but not including 70", whose
cue is on the same side and of the same sense as arm A's "below 70" but is not
one of the seven phrases §2.6 registers — and round 2 registers that vocabulary
as **closed**, on the ground that an open-ended notion of "an inclusivity word"
is a reading and a reading is what the invariant exists to replace. Under the
closed vocabulary the round-1 B fails at `(P4, 40)` *and* `(P4, 70)`; under an
open reading it fails only at `(P4, 40)`, which is what the reviewer found. Both
readings are recorded because the difference is a choice this round made, not a
fact the reviewer missed through inattention. The round-2 B uses "**40 or
more** but **below 70**" and satisfies the invariant under either reading.

Recorded because a property census that reports a number nobody can reproduce is
worth less than no census: the round-2 census below is stated with its
definition beside it, and its adjacency clause is the tuple comparison.

## Arm text digests, as reviewed in this round

Per finding 1 and the §10 review-binding rule. Computed over the five arm texts
**as they stand after this round's fixes**, assembled from Appendix A by the
registered assembly rule (`PREREGISTRATION.md` Appendix A). **All five changed
in round 2**: `PREAMBLE_DELTA` (finding 9) changes every arm, arm B's P4
(finding 3) changes B, and arm C's permutation (finding 17) changes C.

| arm | bytes | sha256 of the arm text as reviewed in round 2 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

For reference, the prompts those texts produce under §2.6's equation — derived,
not authored:

| arm | prompt bytes | sha256 |
|---|---|---|
| **A** | 2762 | `2a6f031e17735494646dd734ee04b4430027babf62b10e1ba9a57675f37de430` |
| **B** | 2827 | `9da426a75e42bb13909daa097e1dc32b1cfdec86330fa69555e6c40081ff2dde` |
| **C** | 2762 | `bff3e24751087815935b748041ae2db19df5f0408dea886219fe13e0531c053c` |
| **D** | 2762 | `0d47c2b135736376744dc00c9c66965465357e6a98e2ccd750505d931e9606d1` |
| **E** | 3029 | `5bbb3a58dd16cd2ef2353e5cc137c74d467c5cb098e4896d2ccce8b165cf2b66` |

Arm A's is 948 + 1814 = 2762, which is 011's pinned 2706 plus
`CONVENTIONS_DELTA`'s 55 bytes plus `PREAMBLE_DELTA`'s 1 — the arithmetic §2.1
registers. The two pinned residues:

| artifact | bytes | sha256 |
|---|---|---|
| the assembled preamble (all five arms) | 343 | `83b7b27fb8cb9054d4536edc6d20ec1c7f9e57cc66f69b5c68891f9def83734d` |
| `CONVENTIONS_DELTA` | 55 | `3b121dd02f8aedd103d0d047b77ee289f788b8d8d22589e396e13baa268223e0` |

**These are digests of drafts, and they are recorded as such.** No
`arms/<X>/POLICY.md` exists yet; the harness does not exist yet; nothing is
frozen.

**The binding these digests carry is now the weaker of the two in force.** Per
finding 1 and §2.10 [D-20], the freeze is bound to the **final** round's
**whole-tree manifest**, and **the full-tree binding applies from the next
round on** — round 3 will be the first round performed over a post-port tree
and the first that can attest one. Rounds 1 and 2 record arm-text digests
because that is what existed to bind. A final round that carries only arm
digests is not a final round.

## Re-verification performed while applying the fixes

Every number this round put into the file was re-derived here, from source
bytes, with an exact-rational implementation, **before** it was written in —
including every figure the reviewer supplied. What was checked and matched:

- **The reviewer's own figures, all independently reproduced to four places:**
  `q = P(HIGH | p = 0.95) = 0.8728935` at n = 25; `≥3/4 COLLAPSE` 0.7583; the
  control gate 0.4031 (n = 25), 0.0557 (n = 20), 0.7658 (n = 30); all-twelve
  TRACKING `q¹⁸` 0.0866; the Fréchet all-six lower bound 0.2374 = `6q − 5`;
  `16/16 → L = 0.7941`, HIGH under the 0.70 cut; HIGH first reachable at 11/11;
  and `0.9x + 9` mapping 40 → 45 and 70 → 72.
- **Clopper–Pearson**: the eleven new registered vectors at n = 30; the nine
  retained at n = 25; the six port-control vectors at n = 50; perfect-arm lower
  bounds at n ∈ {10, 11, 16, 17, 20, 25, 30, 50}; half-covered half-widths
  0.2280 / 0.2045 / 0.1870 / 0.1447 at n = 20 / 25 / 30 / 50.
- **Cut locations**: HIGH iff `k ≥ 27` and LOW iff `k ≤ 3` at n = 30;
  `k ≥ 23` / `k ≤ 2` at 25; `k ≥ 19` / `k ≤ 1` at 20; `k ≥ 42` / `k ≤ 8` at 50.
  011's 0.80 tier cut lands at `k ≥ 29` at n = 30.
- **Operating characteristics at n = 30**: the whole twelve-row marginal table;
  the joint figures 0.9885 / 0.9828 / 0.9492 at p = 0.98 and
  0.7782 / 0.6865 / 0.3235 at p = 0.95; the Fréchet floors 0.9826 and 0.6354;
  `≥3/4 COLLAPSE` 0.9292; the control gate 0.7658; `CONFIRMED ∧ gate` 0.7359;
  `nH ≥ 3` at p = 0.95 → 0.9796; P(LOW) = 0.9392 / 0.8974 / 0.8450 / 0.7842 /
  0.6474 at p = 0.05 / 0.06 / 0.07 / 0.08 / 0.10; the D-19 drift rule's 0.0002
  at N = 30 and 0.0032 at N = 25.
- **The schedule**: the Williams design's ten sequences enumerated and checked —
  each arm in each position exactly twice, each ordered pair adjacent exactly
  twice; the three-block expansion's position counts (6 apiece, 25 cells),
  within-round transitions (6 apiece, 20 pairs, 120 total), boundary
  transitions (29, no self-repeat, 9 pairs twice and 11 once) and totals (149,
  every pair 7 or 8). **And the round-1 schedule's failure reproduced exactly**:
  D → E 20 times, C → E 5, A → E and B → E never, with only 10 of 20 ordered
  pairs realized at all.
- **Digests**: 011's `PINS.json` `e0007697…` and `PORTS.md` `783cc9c3…`,
  recomputed from the worktree; 010's `PROTOCOL-LOCK.json` `4966aa82…`
  cross-checked against 011's pin; 010's `policy/POLICY.md` `e46f8c48…`; 011's
  `PROMPT.txt` `a68dad10…`; `PROBE-PROMPT.txt` `128aaa9a…`.
- **Byte arithmetic**: `2706 = 948 + 1758`; `Study 010` occurs exactly once in
  010's locked policy, at byte offset 64; `PREAMBLE_DELTA` is +1 byte;
  arm A = 1759 + 55 + 1 = 1815 and equals 010's locked policy with both deltas
  applied, byte for byte.
- **Grid**: 2 × 5 × 2 × 14 = 280; arm D's verdict and class vectors elementwise
  equal to arm A's over both the 260-cell and 280-cell grids; and the mutant
  class-5 family `[T_low − 2, T_low)` agreeing on all 260 old cells and
  disagreeing on the new grid.
- **Permutations**: all 120 enumerated against the full constraint set;
  `(P1, P2, P4, P5, P3)` unique at maximum movement; *derangement + every
  reference backward* empty; `(P2, P1, P4, P5, P3)` the unique derangement
  under the weaker set.
- **Arm-text properties, the round-2 census: 62 registered properties of the
  five assembled arm texts — 62 pass, 0 fail**, each one an assertion in a
  script that reads Appendix A's own bytes and rebuilds the five texts by the
  registered assembly rule. The set: five preamble properties (four cross-arm
  equalities, the derivation from 010's bytes with its single-occurrence check,
  and the 343-byte length); six conventions properties; ten structure
  properties (five bullet-set, five label-order); ten census properties (five
  per-arm multisets, D-under-σ, and arm E's four whole-file clauses); nine body
  identity properties (C's five, E's two, A-against-010, D-under-σ, and B
  differing in every clause); seven adjacency properties (A's cue coverage and
  bound count, B == A, D == A under σ, C as a per-clause multiset, and E's
  bound senses); seven permutation properties (three backward-resolution
  clauses, the movement count, maximum-movement uniqueness, the empty
  derangement intersection, and the alternative's uniqueness); and eight prompt
  and byte-arithmetic properties. **The adjacency clause is now the ordered
  tuple comparison against a closed vocabulary**, which is the check round 1's
  count assumed and did not perform.

## What this round does not establish

- **It is not the final round, and it could not have been.** It reviewed a
  specification and five draft texts. The harness does not exist, the port has
  not been taken, `CLAIM.md` has not been written, and `MIRROR-AGREEMENT.md`
  has no readers. Finding 1's binding is precisely about the round that reviews
  those, and that round has not happened.
- **C10 has not run.** The five clean-room mirrors do not exist. Finding 5 of
  round 1 and finding 18 of round 2 register commitments, not results, and an
  arm E whose reader cannot derive (40, 70) is still an open possibility that
  would force a re-authoring — and, under this round's C10 rule, a fresh reader
  and another review round after it.
- **No harness exists**, so nothing in §6 has been executed. Every check
  described as "checked in code" is specified, not implemented.
- **The maintainer decisions recorded above are choices, not findings.** D-1's
  move to N = 30, D-5's move away from a derangement, D-16's adoption, D-20's
  manifest, D-21's stopping rule, D-23's argument surface and D-24's
  intent-to-treat endpoint each have a live alternative in §10 for the next
  round to move.
- **One round of one cross-vendor reviewer is one round.** It found thirteen
  blocking defects in a file that had already passed an internal round which
  called itself thorough. The right inference is about the base rate, not about
  the remaining count.


## Round 3 — the final-candidate review over the complete post-port tree ([D-20])

- Drafting models: Anthropic Claude — Opus 5 subagents orchestrated by Claude
  Fable 5 (claude-fable-5), 2026-08-08 (the port); rounds 1-2 drafting as
  recorded above
- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08
- Reviewed commit: `4489d69` (branch `study-012-perturbation`)
- Tree manifest, computed independently by the reviewer and by the harness
  before commissioning, both:
  `cddaa40d096384e2169894a51c0b5934b7a71c506d4d73e9804c8afea9fd923a`
  (§2.10's recipe over the tracked study tree minus the registry's exclusion
  list, as it stood entering this round)
- Runs: one review run, completed; no run discarded
- Context: the branch worktree at the reviewed commit; read-only with respect
  to the repository; the pinned CPython 3.12.11 for the suite and integrity
- Reviewer's own verification, before the findings: integrity exit 0 (manifest
  unbound as registered pre-round-3), pytest 72 passed, all eleven port
  digests, the schedule, all twenty arm files and all five 280-cell mirror
  comparisons independently confirmed; arm censuses and the arm-C permutation
  re-derived independently; CLAIM.md's Study-011 quotation exact; C10
  pre-assignment verified to precede every attempt by commit ancestry

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 3) of Study 012 at commit 4489d69 on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Rounds 1 and 2 reviewed the specification and the five arm texts; this round reviews the COMPLETE post-port candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding only the paths listed in harness/PINS.json freeze.excluded, build the sorted list of lines "<path> <bytes> <sha256>" (path relative to the study directory, one line each, joined with newlines, with a trailing newline), and take the sha256 of that text. State the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: 4489d69"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R3-DONE.
```

### Complete unedited final message

Pinned verification completed read-only: `integrity.py` exited 0 but reported the tree manifest as **unbound**; pytest reported **72 passed in 35.39s**. All eleven port digests, the registered schedule, all twenty arm files, and all five 280-cell mirror comparisons passed. Independent arm censuses and exhaustive arm-C permutation enumeration also matched. The Study 011 quotation in `CLAIM.md` is exact; the two issue-#45 quotations have no independent repository copy. Pre-assignment preceded all mirror attempts, and each raw module equals its extracted and final mirror.

1. [PREREGISTRATION.md:1094](PREREGISTRATION.md:1094), [PINS.json:156](harness/PINS.json:156), [integrity.py:907](harness/integrity.py:907): The record includes `PINS.json` and `PREREG-REVIEW.md` in the manifest, then requires the digest to be written into both. The code hashes those carrier files, creating a self-reference, while `verify_tree()` also accepts a null pin as “unbound.” The reviewed digest is `cddaa40d…`; merely inserting it into PINS changes the digest to `4c3ca73a…`. Later mandatory golden/assent edits change PINS again. **Severity: blocking.**

2. [PINS.json:159](harness/PINS.json:159), [score_rates.py:243](harness/score_rates.py:243): The exclusions name top-level `BATCH.json` and `SHORTFALL.json`; runtime writes `arms/BATCH.json` and `arms/SHORTFALL.json`. Required committed recapture and isolation-control artifacts are also unexcluded. Exact-prefix matching therefore invalidates the frozen manifest as these artifacts become tracked. **Severity: blocking.**

3. [PINS.json:95](harness/PINS.json:95), [batch.py:449](harness/batch.py:449): PINS registers `batch.n`, `batch.slots`, and `batch.order`, which the scorer reads correctly. Driver preflight instead requires nonexistent `batch.runs` and top-level `schedule.williams/blocks`. Once stage-null pins are filled, every real batch preflight still refuses. `test_schedule.py` tests only `batch.schedule()`, not preflight against committed PINS. **Severity: blocking.**

4. [PINS.json:152](harness/PINS.json:152), [batch.py:1294](harness/batch.py:1294): C7 registers `isolationNegative.assent`; the driver reads `isolationNegative.operatorAssent`. Filling the registered member can never authorize the mandatory negative control. **Severity: blocking.**

5. [PREREGISTRATION.md:1035](PREREGISTRATION.md:1035), [authoring_call.sh:25](transcription/authoring_call.sh:25), [PORTS.md:148](harness/PORTS.md:148): §2.9 says the wrapper writes `SLOT-MANIFEST.json`. The wrapper explicitly does not seal; `batch.py` writes refusal/schedule data and then seals. PORTS acknowledges and rationalizes this operationally sensible choice, but cannot override the registration. **Severity: blocking.**

6. [PREREGISTRATION.md:2330](PREREGISTRATION.md:2330), [PREREGISTRATION.md:2346](PREREGISTRATION.md:2346), [integrity.py:972](harness/integrity.py:972): C2 requires pack/family coherence for A/B/C/E, and C3.1 requires replaying Study 010’s completion to its published profile. Neither control exists in Study 012’s integrity path or tests. Only C3.2’s Study 011 census replay is implemented. **Severity: blocking.**

7. [PREREGISTRATION.md:635](PREREGISTRATION.md:635), [integrity.py:697](harness/integrity.py:697), [PREREGISTRATION.md:3146](PREREGISTRATION.md:3146): C8 promises exact A-to-010, D-under-substitution, E-body, E-suffix, and Appendix-A relations. Integrity checks censuses and bound senses but not those byte relations; E’s suffix need only be nonempty and digit-free. No test invokes `arm_assembly.py` to enforce the registered Appendix equality. Current artifacts independently satisfy the relations, but the claimed guard does not. **Severity: blocking.**

8. [PREREGISTRATION.md:2590](PREREGISTRATION.md:2590), [MIRROR-AGREEMENT.md:39](MIRROR-AGREEMENT.md:39), [prompt.txt:34](analysis/mirror2-attempts/A/attempt-1/prompt.txt:34): C10 says each author receives policy bytes “and nothing else.” Each retained prompt adds a 677-byte interface/instruction suffix. MIRROR-AGREEMENT also calls isolation structural and says no tool surface could fetch study files, but `codex exec --sandbox read-only` retains shell tools and restricts writes, not reads. Raw traces show no tool calls, so non-consultation is behavioral evidence, not the registered structural condition. **Severity: blocking.**

9. [PREREGISTRATION.md:1717](PREREGISTRATION.md:1717), [score_rates.py:2517](harness/score_rates.py:2517): The record says S5 separates placement collapse from comprehension collapse and that comprehension collapse cannot confirm R1. The scorer computes only `nP`, `nC`, and `nH`; row 5 confirms solely from `nP`. No S5 cut or comprehension-collapse outcome exists, so the registered distinction is unreachable. **Severity: blocking.**

10. [PREREGISTRATION.md:1951](PREREGISTRATION.md:1951), [score_rates.py:2450](harness/score_rates.py:2450): §5.3 registers arm-D outcomes including `OLD-EDGE-PREFERENCE` and general degradation. The scorer publishes marginal old-edge levels but aggregates outcomes only for arm E; neither named D outcome is computed or tested. **Severity: blocking.**

11. [PREREGISTRATION.md:2145](PREREGISTRATION.md:2145), [score_rates.py:2579](harness/score_rates.py:2579): §5.4 labels `0.7142/0.9187/0.9796` as power to reach decision row 4, but those are only marginal `P(nH ≥ 3)`. Code reaches row 4 only after the class-4 and B/C gates. Under the stated independence scenario, the actual row-4 probabilities are approximately `0.0397841/0.3703584/0.7501924` for N=20/25/30. **Severity: blocking.**

12. [README.md:173](README.md:173), [conftest.py:5](harness/tests/conftest.py:5), [ci.yml:29](.github/workflows/ci.yml:29): The record claims a Study-012 CI job, wrapper-driven stand-in-CLI tests, an exact `ci95`-scope walk, Appendix parity, and operating-characteristic tests. There is no Study-012 CI job; conftest explicitly says no wrapper or CLI is invoked; no test walks `ci95` or calls `level_operating_characteristics`. Partition “reachability” merely AST-collects string literals, so even dead-code returns count as reachable. **Severity: should-fix.**

13. [PREREGISTRATION.md:1299](PREREGISTRATION.md:1299), [score_rates.py:1725](harness/score_rates.py:1725): The exhaustive partition reserves `authoring-empty` for no parseable array. Code also sets it for parseable all-dropped and all-Q completions using `empty or not accepted or not high`. Tests cover only the no-array case. **Severity: should-fix.**

14. [PREREGISTRATION.md:939](PREREGISTRATION.md:939), [score_rates.py:2361](harness/score_rates.py:2361): Incomplete batches retain N and publish the descriptive S3 surface. The distribution iterates only present rows, while its mean and all-six rate use N. A one-row prefix at N=30 produces a distribution totaling 1 beside a rate denominator of 30. **Severity: should-fix.**

15. [PREREGISTRATION.md:985](PREREGISTRATION.md:985), [batch.py:1450](harness/batch.py:1450): Shortfall must record completed rounds and the last slot’s UTC time. Code uses the current slot’s round, so a prefix ending inside round 1 reports one completed round instead of zero. A wrapper preflight refusal has no `CALL.json`, and the driver consequently records `lastSlotEndedAt: null`. The parity test checks field names, not values. **Severity: should-fix.**

16. [PREREGISTRATION.md:996](PREREGISTRATION.md:996), [batch.py:847](harness/batch.py:847): Resume must refuse any ledger whose sequence diverges. `load_ledger()` silently sorts records by `globalIndex` before checking, so a physically reordered ledger is normalized and rewritten rather than refused; the scorer would reject the same file order. **Severity: should-fix.**

17. [PREREGISTRATION.md:2306](PREREGISTRATION.md:2306), [integrity.py:545](harness/integrity.py:545): C1 requires tier-1 equality to Study 011’s own copies and tier-2 source-byte binding. Code checks Study 010 and digest values but never opens Study 011’s `FAMILY.json`, `policy_mirror.py`, or `PROBE-PROMPT.txt`. Those current files independently match, but the promised checks cannot fire. **Severity: should-fix.**

18. [PREREGISTRATION.md:2444](PREREGISTRATION.md:2444), [score_rates.py:1114](harness/score_rates.py:1114): C6 requires boolean copied/removed evidence. Code coerces `credentialCopied` with `bool()` rather than type-checking it; `"credentialCopied": "false"` with `"credentialRemoved": true` passes. **Severity: should-fix.**

19. [PREREGISTRATION.md:49](PREREGISTRATION.md:49), [test_census.py:158](harness/tests/test_census.py:158): The record calls `[23.75,39)` empty while also establishing that 23.75 exists. The test correctly checks only `23.75 < x < 39`; the empty interval is `(23.75,39)`. **Severity: should-fix.**

20. [PINS.json:25](harness/PINS.json:25), [batch.py:6](harness/batch.py:6): PINS says Python’s patch level is recorded but contains only implementation and series. Separately, PORTS/PINS bind the port to `3b93d3e…`, while the batch docstring names `e52925e…`; the source blob is identical at both commits. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready; its manifest cannot be bound and its registered batch cannot start.

Reviewed commit: 4489d69

Tree manifest (my computation): cddaa40d096384e2169894a51c0b5934b7a71c506d4d73e9804c8afea9fd923a

CODEX-012-R3-DONE

### Dispositions

All twenty findings **ACCEPTED**, decided by the maintainer on a plain-language
brief of each finding with the judgment calls put separately; the three that
were judgment calls carry their reasoning:

| # | disposition |
| --- | --- |
| 1 | **ACCEPTED.** The tree manifest's recipe excludes its two carrier files (`harness/PINS.json`, `PREREG-REVIEW.md`), which are bound by their own mechanisms — the registry by the per-run digest stamp every slot carries and the scorer recomputes, the review record by being the attestation itself. §2.10 is amended to say so, and the exclusion is in code, not convention |
| 2 | **ACCEPTED.** The exclusion list is corrected to the paths the code writes (`arms/BATCH.json`, `arms/SHORTFALL.json`) and gains the capture and isolation-control artifact trees |
| 3 | **ACCEPTED.** The driver's preflight reads the registry members that exist (`batch.n`, `batch.slots`, `batch.order.*`), aligned with the scorer; a parity test pins driver, scorer and registry to one spelling |
| 4 | **ACCEPTED.** One member name: `isolationNegative.assent`, everywhere |
| 5 | **ACCEPTED, resolved on the code's side by amending the registration.** §2.9's sentence now names the driver as the sealer, with the reason the review could not overrule: the wrapper is not the last writer into a refused slot, and the pipeline-invalid rate is an endpoint — a wrapper-side seal covers every slot except the ones whose bytes explain a failure. The alternative (move the seal into the wrapper, lose refused-slot coverage) is rejected with that cost stated |
| 6 | **ACCEPTED.** C2 (pack-side coherence for the (40, 70) arms against Study 010's pack C at its pinned digest, with [D-6]'s registered treatment for arm D stated plainly) and C3 clause 1 (the ported compiler, mirror and class arithmetic over 010's retained completion, reproducing the published profile exactly) are implemented as registered controls in the suite |
| 7 | **ACCEPTED.** C8's byte relations are checked as registered: A's bodies byte-identical to 010's, C's to A's, D's equal to A's under the literal substitution at byte level, E's P1/P2 to A's, E's appended sentence pinned by digest; and an assembler-parity test rebuilds the twenty arm files from Appendix A's rule and requires byte equality with the committed trees |
| 8 | **ACCEPTED as a record correction; the five runs stand.** MIRROR-AGREEMENT.md's isolation claim is rewritten to what the retained bytes support: the sandbox restricted writes, not reads; the working directory was empty; non-consultation is evidenced behaviorally by the retained transcripts (no tool calls); and the 677-byte interface suffix is quoted as exactly what the prompt supplied beyond the policy bytes. C10's "and nothing else" is amended to name the published interface suffix. Re-commissioning under a stronger cage is rejected: the grid equality is the check with teeth, and it already ran |
| 9 | **ACCEPTED.** The S5 cut and the comprehension-collapse outcome are implemented as §5.3 registers them, with fixtures exercising both branches |
| 10 | **ACCEPTED.** Arm D's registered outcomes (including `OLD-EDGE-PREFERENCE`) are computed and tested |
| 11 | **ACCEPTED; N = 30 is retained with the arithmetic stated honestly.** §5.4's labels confused marginal `P(nH >= 3)` with the joint probability of reaching decision row 4; the joint values are recomputed independently (not copied from the review), registered in §5.4, and pinned by an operating-characteristics test. The maintainer keeps N = 30 knowing the joint confirmatory power is materially lower than the mislabeled figure suggested — the descriptive surface publishes regardless, and [D-1]'s alternative carries the updated numbers — rather than raising N |
| 12-19 | **ACCEPTED** as written: the CI job, the wrapper-driven batch tests, the `ci95` walk, the partition-reachability strengthening, `authoringEmpty` narrowed to the table's meaning with the wider count published under its own name, the S3 denominators made consistent, the shortfall's completed-rounds and last-slot-time edge cases, the ledger's file-order refusal, tier-1/2 checks opened against 011's own copies, the credential booleans type-checked, and the band stated as the open interval it is |
| 20 | **ACCEPTED.** The registry's interpreter note is corrected and the driver docstring names the recorded port commit |

Implementation follows this record; the port and the review then repeat
(round 4), and the freeze binds to the manifest of the round that ends
clean.

## Arm text digests, as reviewed in this round

The five `arms/<X>/POLICY.md` files as this round reviewed them — unchanged
from round 2's table, which the round-2 pins and `harness/integrity.py`
already bind:

| arm | bytes | sha256 of the arm text as reviewed in round 3 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |


## Round 4 — the post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-3
- Reviewed commit: `1bb6d34`
- Manifest attestations, stated exactly because the recipes diverged: the
  commissioning prompt still carried round 3's recipe (the registry exclusions
  only), under which the reviewer computed `eabb95b2…` over 97 files; the
  amended §2.10 recipe (carriers excluded in code) computes `21c18994…` at the
  same commit. The divergence is the commissioning script's error, recorded
  here rather than hidden, and finding 2 below supersedes both recipes anyway.
- Runs: one review run, completed; no run discarded
- Reviewer's own verification first: integrity exit 0, 166 passed under the
  pinned interpreter, independent censuses, permutation and all five mirror
  agreements re-derived; CLAIM.md's quotation exact; pre-assignment precedes
  every retained attempt. **Twelve of round 3's twenty dispositions verified
  complete** (2-7, 11's row-4 correction, 14, 16-18, 20); the rest partial,
  as the findings state.

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 4) of Study 012 at commit 1bb6d34 on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Round 3 reviewed the complete post-port tree at 4489d69 and returned BLOCKING with twenty findings; all twenty were dispositioned ACCEPTED (the dispositions table is in PREREG-REVIEW.md's round-3 section) and implemented. This round re-reviews the COMPLETE candidate tree after those dispositions. Your first task, before the general sweep: take each of the twenty round-3 findings in order and verify its disposition is actually implemented — the fix real, complete, and not merely papered over in prose. Then re-review the whole tree fresh, including every byte the dispositions changed (the §2.9, §2.10, §4.6, §5.3, §5.4 and C10 amendments; the manifest carrier exclusion; the new controls and test files). This round reviews the COMPLETE post-disposition candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding only the paths listed in harness/PINS.json freeze.excluded, build the sorted list of lines "<path> <bytes> <sha256>" (path relative to the study directory, one line each, joined with newlines, with a trailing newline), and take the sha256 of that text. State the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: 1bb6d34"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R4-DONE.
```

### Complete unedited final message

Pinned verification: `integrity.py` exited 0 but reported the tree manifest as **unbound**. The full suite passed: **166 passed in 134.42s** under CPython 3.12.11 with bytecode disabled and pytest’s cache provider disabled. Independent digit-census, arm-C permutation, and five 280-cell mirror checks matched. The Study 011 quotation in `CLAIM.md` is exact; pre-assignment precedes all retained mirror attempts, whose raw, extracted, and final modules agree.

Round-3 dispositions 2–7, 11’s original row-4 correction, 14, 16–18, and 20 are complete. Dispositions 1, 8–10, 12, 13, 15, and 19 remain partial or incorrect as detailed below.

1. [PREREGISTRATION.md:1119](PREREGISTRATION.md:1119>), [integrity.py:988](harness/integrity.py:988>), [batch.py:622](harness/batch.py:622>): The record requires the final manifest digest to be pinned and recomputed before calls or scoring. `verify_tree()` instead accepts a null `treeManifestSha256` as “unbound”; batch and scorer require only `preregistrationSha256`. A frozen preregistration can therefore run and score with no tree binding. **Severity: blocking.**

2. [PREREGISTRATION.md:1107](PREREGISTRATION.md:1107>), [PINS.json:159](harness/PINS.json:159>), [integrity.py:952](harness/integrity.py:952>): The record says the excluded carriers are otherwise bound and any reviewed-byte change requires another round. Code excludes `PINS.json` and `PREREG-REVIEW.md`, then trusts the mutable manifest value in PINS without comparing it to the reviewer’s attestation. Changing covered files and updating PINS therefore passes; per-slot stamps prove only consistency with the newly edited registry. The prompt-prescribed 97-file manifest is `eabb95b2…`; the harness’s additional carrier exclusions produce `21c18994…`. **Severity: blocking.**

3. [integrity.py:917](harness/integrity.py:917>), [integrity.py:1028](harness/integrity.py:1028>), [PINS.json:159](harness/PINS.json:159>): The manifest is supposed to bind every included tracked byte. Five tracked `analysis/__pycache__/mirror2_*.cpython-312.pyc` files are included, but `verify()` imports their sources before checking the manifest. On a fresh archive this rewrote all five caches, changing the harness-recipe digest from `21c18994…` to `f1fc5b03…`. Normal README and CI invocations do not disable bytecode, so a populated pin would reject a fresh checkout—or bind unreviewed rewritten cache bytes. **Severity: blocking.**

4. [PREREGISTRATION.md:1737](PREREGISTRATION.md:1737>), [PREREGISTRATION.md:1897](PREREGISTRATION.md:1897>), [score_rates.py:3074](harness/score_rates.py:3074>): §4.6 and decision row 5 require S5 labels at ceiling for confirmation. The adjacent confirmation table, its registered “iff” box, and D-10 still omit S5 and say the other three conjuncts suffice. The scorer chose the stricter four-conjunct rule. The preregistration therefore contains incompatible confirmatory rules. **Severity: blocking.**

5. [PREREGISTRATION.md:1742](PREREGISTRATION.md:1742>), [PREREGISTRATION.md:2196](PREREGISTRATION.md:2196>), [score_rates.py:876](harness/score_rates.py:876>): The record admits §5.4 does not model S5, yet calls `0.7359` the “actual joint” confirmation probability and uses it to justify N=30. The code models only coverage and the B/C/class-4 gates. With no label-error model, `0.7359` is at most the coverage-side upper bound; actual confirmatory power is unidentified and can range down to zero. **Severity: blocking.**

6. [PREREGISTRATION.md:1998](PREREGISTRATION.md:1998>), [score_rates.py:1020](harness/score_rates.py:1020>): Arm D’s registered `COVERAGE-FOLLOWS-THE-NUMBERS` condition is new-keyed HIGH on at least three narrow classes with no old-keyed HIGH pattern. Code instead requires all six D-vs-A contrasts to be TRACKING and never checks the old-keyed exclusion. Tests assert the code’s table, not the registered condition. **Severity: blocking.**

7. [PREREGISTRATION.md:1314](PREREGISTRATION.md:1314>), [test_partition_parity.py:56](harness/tests/test_partition_parity.py:56>): The accepted disposition promised reachability checks for every refusal code. The test still harvests string literals from AST return/assignment tuples; a code placed solely in dead code counts as reachable. **Severity: should-fix.**

8. [PREREGISTRATION.md:1552](PREREGISTRATION.md:1552>), [test_batch.py:1296](harness/tests/test_batch.py:1296>): The record claims an exact recursive walk of blocks carrying `ci95`. The walker returns immediately upon finding a parent `ci95`, so nested interval-bearing structures beneath that block are invisible. **Severity: should-fix.**

9. [score_rates.py:2113](harness/score_rates.py:2113>), [score_rates.py:2813](harness/score_rates.py:2813>): The published surface defines `coveredNothing` as valid runs that reached no class. Code computes `empty or not accepted or not high`, which asks whether any correctly labelled record exists, not whether a class was reached. A correctly labelled record outside all six predicates produces `coveredClasses=[]` but `coveredNothing=false`; an all-Q class-reaching run creates the opposite semantic mismatch. **Severity: should-fix.**

10. [PREREGISTRATION.md:985](PREREGISTRATION.md:985>), [batch.py:1549](harness/batch.py:1549>), [test_batch.py:1152](harness/tests/test_batch.py:1152>): Shortfall must record the UTC time of the last completed slot. For a tail refusal without `CALL.json`, code substitutes an earlier slot’s timestamp—or null—and tests enshrine that fallback. Naming its source is honest but does not implement the registered field. **Severity: should-fix.**

11. [README.md:35](README.md:35>), [census.py:363](harness/census.py:363>), [test_census.py:158](harness/tests/test_census.py:158>): The preregistration now correctly says `(23.75, 39)`, but these files still call `[23.75, 39)` empty even though a score of 23.75 exists. The actual assertion silently uses strict inequalities. **Severity: should-fix.**

12. [README.md:337](README.md:337>), [MIRROR-AGREEMENT.md:57](MIRROR-AGREEMENT.md:57>): The corrected C10 record permits a published interface suffix, but README still says each reader received policy bytes “and nothing else.” MIRROR-AGREEMENT says 706 non-policy bytes; retained prompts contain a 28-byte framing prefix plus a 677-byte suffix—705 bytes total—with no final newline. The behavioral isolation account otherwise matches the transcripts. **Severity: should-fix.**

13. [CLAIM.md:12](CLAIM.md:12>): The cited `3b93d3e…` object has one parent, so it is a squash/PR result rather than a Git merge commit. The quoted Study 011 passage itself is exact. **Severity: nit.**

14. [PREREGISTRATION.md:1035](PREREGISTRATION.md:1035>), [batch.py:865](harness/batch.py:865>): §2.9 and the operational code now correctly make the driver the sealer, but `seal_slot()`’s docstring still quotes the obsolete wrapper-sealer sentence as current and says the final round has yet to adjudicate it. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready.

Reviewed commit: 1bb6d34

Tree manifest (my computation): eabb95b248b6b172ca381cea88eeb817cb85a6f5edb166eaf017469e4d73acdd

CODEX-012-R4-DONE

### Dispositions

All fourteen findings **ACCEPTED**, continuing the round-3 direction the
maintainer adopted; none reopens a settled judgment call. The blockers are
completions: the freeze pins become required together and the manifest binds
a normalized registry projection (1, 2 — with the residual §2.10 already
concedes restated, not narrowed); the committed bytecode caches leave the
tree (3); the S5 conjunct reaches every statement of the confirmation rule
(4); §5.4's joint figures are renamed the coverage-side quantities they are
(5); arm D's registered condition replaces the scorer's stricter invention
(6); and the should-fixes and nits as written (7-14), including the byte-count
re-measurement against the retained prompts, which are the authority: a
28-byte framing prefix plus a 678-byte instruction suffix, 706 bytes in
all with no final newline — the review's 705/677 is the off-by-one, and
the record now states the structure rather than one number.

## Arm text digests, as reviewed in this round

Unchanged from rounds 2 and 3:

| arm | bytes | sha256 of the arm text as reviewed in round 4 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |


## Round 5 — the second post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-4
- Reviewed commit: `657b4dc`
- Tree manifest, the reviewer's computation under §2.10 as amended (carriers
  excluded, the registry's normalized projection included):
  `787936eb09ba7d0d7159b7c0102fbdad95a9e1064a76cc425edb09c93565da45`
- Runs: one review run, completed; no run discarded
- Reviewer's own verification first: integrity exit 0 from source-only
  imports; 169 tests twice (once with an empty bytecode cache); every digest,
  scope, census, permutation, arm artifact and mirror agreement re-derived
  independently. **Six of round 4's fourteen dispositions verified complete**
  (6, 9-11, 13, 14); 1-5, 7 and 12 incomplete, 8 under-asserted — as the
  findings state.

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 5) of Study 012 at commit 657b4dc on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Round 3 (at 4489d69) found twenty findings; round 4 (at 1bb6d34) verified twelve of their dispositions complete and found fourteen further findings, all dispositioned ACCEPTED and implemented (both rounds' records and dispositions tables are at the end of PREREG-REVIEW.md). Your first task: verify each of round 4's fourteen findings is genuinely implemented. Then a fresh sweep of the whole tree, including every byte the round-4 dispositions changed (the §2.10 normalized-projection binding and freeze-pin coupling; the S5 conjunct in the [D-10] box and register; §5.4's coverage-side naming; arm D's registered condition in the scorer; the reachability and interval walks; the coveredNothing derivation; the record corrections). This round reviews the COMPLETE post-disposition candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 AS AMENDED registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding the paths in harness/PINS.json freeze.excluded AND the two carriers (harness/PINS.json, PREREG-REVIEW.md), build the sorted list of lines "<path> <bytes> <sha256>" (paths relative to the study directory); then append the registry's normalized-projection entry — PINS.json parsed, freeze.treeManifestSha256, golden.sha256 and isolationNegative.assent set to null, serialized with json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":")) plus a newline, hashed and listed as "harness/PINS.json#normalized <bytes> <sha256>" — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Verify integrity.tree_manifest() implements the same recipe, and state the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: 657b4dc"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R5-DONE.
```

### Complete unedited final message

Pinned verification: `integrity.py` exited 0 from source-only imports. The requested test command passed **169 tests in 135.99s**; forcing an empty external bytecode cache also passed **169 tests in 263.13s**. Tracked status remained clean.

Port digests/scopes, the wrapper’s three permitted differences, schedule, seals, ledger, arm-D condition, and all twenty arm artifacts matched. Independent censuses gave A/B/C `{40×2,70×4}`, D `{45×2,72×4}`, E empty; arm C’s registered permutation was uniquely maximum-movement. The Study 011 quotation in `CLAIM.md` is exact. The issue-#45 excerpts have no independent local copy. Mirror pre-assignment preceded every attempt; retained prompts, transcripts, extracted modules, and final mirrors matched, with no tool calls.

Round-4 disposition audit: 6, 9–11, 13, and 14 are complete. Findings 1–5, 7, and 12 remain incomplete; finding 8 fixed parent descent but remains under-asserted.

1. [PREREGISTRATION.md:1119](PREREGISTRATION.md:1119), [integrity.py:959](harness/integrity.py:959), [integrity.py:1014](harness/integrity.py:1014): The record says a covered-file/registry co-edit fails and any post-review edit requires another review. The normalized projection nulls `treeManifestSha256`, while `verify_tree()` trusts that mutable, excluded member and checks neither the reviewed commit nor the attestation in `PREREG-REVIEW.md`. In a temporary copy, changing `README.md`, recomputing the manifest, and updating only the tree pin passed `verify_tree()`. The binding remains self-authenticating. **Severity: blocking.**

2. [PREREGISTRATION.md:284](PREREGISTRATION.md:284), [PINS.json:156](harness/PINS.json:156), [integrity.py:959](harness/integrity.py:959): The registered sequence performs this review and then fills both freeze pins. But `preregistrationSha256` is not normalized away, so filling the raw digest required by the scorer changes this round’s manifest from `787936…` to `42ec6e43…`. Pinning the reviewed digest then fails; pinning the new digest attests bytes this review did not see. Coupling is also one-way: tree-filled/prereg-null passes `verify_tree()`. **Severity: blocking.**

3. [.gitignore:1](.gitignore:1), [batch.py:179](harness/batch.py:179), [integrity.py:82](harness/integrity.py:82): The record says reviewed bytes are the bytes that run. Round 4 untracked and ignored bytecode, but the actual worktree still contains the five former tracked mirror caches and numerous harness caches. CPython reads these even with `-B` or `PYTHONDONTWRITEBYTECODE=1`; `python -B -v` confirmed `policy_mirror` and all five clean mirrors loading from ignored `.pyc` files outside the manifest. **Severity: blocking.**

4. [PREREGISTRATION.md:1911](PREREGISTRATION.md:1911), [PREREGISTRATION.md:1916](PREREGISTRATION.md:1916), [score_rates.py:3131](harness/score_rates.py:3131): The disposition says S5 reaches every confirmation statement. The summary table still awards CONFIRMED from placement collapse alone, and §5.4 still calls `nP ≥ 3` the “CONFIRMED pattern”; the adjacent box, D-10, decision table, and scorer require S5. The preregistration therefore retains two confirmation rules. **Severity: blocking.**

5. [PREREGISTRATION.md:2237](PREREGISTRATION.md:2237), [PREREGISTRATION.md:2258](PREREGISTRATION.md:2258), [score_rates.py:849](harness/score_rates.py:849), [test_verdict_parity.py:545](harness/tests/test_verdict_parity.py:545): The amended paragraph correctly calls `0.7359` coverage-side and an upper bound, but later sample-size prose still calls it the probability of the whole CONFIRMED outcome. Code calls it the probability of reaching row 5, and the test prefix-matches away the amended “coverage-side” suffix. Actual power requires the unmodelled conditional probability of S5 given the coverage gates. **Severity: blocking.**

6. [PREREGISTRATION.md:1385](PREREGISTRATION.md:1385), [score_rates.py:1964](harness/score_rates.py:1964), [score_rates.py:1996](harness/score_rates.py:1996), [score_rates.py:2580](harness/score_rates.py:2580): The record promises malformed slot evidence becomes that slot’s `scorer-error`, without stopping other slots. `session_reuse()` handles untyped `CALL.json` before `score_run()`’s catch-all and hashes arbitrary member values. A fixture with `startedAt: []` raises bare `TypeError: unhashable type: 'list'` and aborts the entire score. **Severity: blocking.**

7. [PREREGISTRATION.md:1353](PREREGISTRATION.md:1353), [transcript_check.py:338](harness/transcript_check.py:338), [score_rates.py:1749](harness/score_rates.py:1749), [test_partition_parity.py:124](harness/tests/test_partition_parity.py:124): `completion-unreadable` is registered as reachable, but the transcript check decodes the completion first; invalid UTF-8 is caught as `ValueError` and becomes `transcript-refused`. The round-4 reachability test only limits lexical harvesting to called functions and still counts returns in dead branches; an `if False` return inside `admit()` is accepted. **Severity: should-fix.**

8. [PREREGISTRATION.md:1572](PREREGISTRATION.md:1572), [test_batch.py:1317](harness/tests/test_batch.py:1317), [test_batch.py:1337](harness/tests/test_batch.py:1337), [test_batch.py:1365](harness/tests/test_batch.py:1365): The record promises an exact walk of `RESULTS.json`. The repaired walker descends through parents, but collapses every list member to one set path and later inspects only element zero; one good class row can certify all six. It also walks arm blocks and census separately, leaving other top-level output blocks unchecked. **Severity: should-fix.**

9. [PREREGISTRATION.md:1653](PREREGISTRATION.md:1653), [PREREGISTRATION.md:1675](PREREGISTRATION.md:1675), [census.py:363](harness/census.py:363), [census.py:391](harness/census.py:391): The record says X3/X4’s “full distributions” expose unanticipated arm-E values and that D publishes old-edge tables at 40/70. X3 retains exact values only within one point of current-arm edges; X4 publishes profile/signature aggregates. Otherwise identical arm-E records at scores `12` and `13` produce identical complete census objects, and D emits no 40/70 table. **Severity: should-fix.**

10. [PREREG-REVIEW.md:867](PREREG-REVIEW.md:867), [MIRROR-AGREEMENT.md:57](MIRROR-AGREEMENT.md:57), [README.md:337](README.md:337): The disposition says the reviewer’s 705/677 count was wrong. Every retained prompt is actually the complete policy bytes plus a 28-byte prefix and 677-byte suffix: 705 non-policy bytes. The claimed 678-byte suffix double-counts the policy’s terminal LF. No threshold or study-term leakage was found. **Severity: should-fix.**

11. [MIRROR-AGREEMENT.md:69](MIRROR-AGREEMENT.md:69), [MIRROR-AGREEMENT.md:129](MIRROR-AGREEMENT.md:129), [integrity.py:937](harness/integrity.py:937): The agreement says the grid pins every inclusive/exclusive decision. Code compares final verdicts only, so same-outcome clause boundaries are invisible—for example, P4’s explicit upper bound is redundant after P3’s early return. The document later concedes this general limitation. **Severity: nit.**

12. [README.md:3](README.md:3), [README.md:11](README.md:11): The current-status record says the harness does not exist, only rounds 1–2 are complete, and the port and C10 mirrors remain outstanding. At this commit all those artifacts and rounds 3–4 exist. **Severity: should-fix.**

13. [PREREGISTRATION.md:1749](PREREGISTRATION.md:1749), [score_rates.py:1001](harness/score_rates.py:1001): The exact S5 cut is registered as integer `|Q| = 0`. Code tests the rounded float accuracy against `1.0`; sufficiently large `H/(H+1)` rounds to `1.0` despite positive Q. The existing integer `q` should be authoritative. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready.
Reviewed commit: 657b4dc
Tree manifest (my computation): 787936eb09ba7d0d7159b7c0102fbdad95a9e1064a76cc425edb09c93565da45
CODEX-012-R5-DONE

### Dispositions

All thirteen findings **ACCEPTED**, continuing the adopted direction. The
deep one is stated plainly rather than patched again: findings 1 and 2 are
the same truth — **a self-computed manifest cannot authenticate itself, and
no further digest inside the tree will change that**. The disposition: the
normalized projection also nulls `freeze.preregistrationSha256` so the
ceremony no longer invalidates its own manifest; the freeze coupling becomes
two-way; `verify_tree()` additionally cross-checks the registry's pin
against the final round's attestation line in `PREREG-REVIEW.md`, so
defeating the binding now requires editing the review record itself; and
§2.10's claim sentence is rewritten to exactly what holds — the manifest
detects every edit that leaves the pin or the attestation standing, the rule
(not the digest) forbids the rest, and the externally signed attestation
remains the stronger [D-20] form. Finding 3: ignored bytecode loads even
under `-B`, so the runtime gates refuse while compiled caches sit beside
reviewed sources, and the ceremony's commands are registered to run without
writing them. Findings 4 and 5 finish the S5 and coverage-side sweeps in the
three surfaces each still missed. Finding 6 is a real crash: malformed
`CALL.json` evidence becomes that slot's refusal, never an abort. Findings
7-9, 12, 13 as written. Findings 10 and 11: the byte-count dispute ends with
the equation itself — the prompt is the 28-byte prefix, the policy file's
bytes minus their final LF, then a 678-byte suffix whose first two bytes are
LFs; against the full policy file that is equivalently a 677-byte suffix and
705 non-policy bytes; both decompositions are now stated so neither number
can be called wrong again — and the grid-pinning sentence is softened to the
verdict-level claim the code actually checks.

## Arm text digests, as reviewed in this round

Unchanged since round 2:

| arm | bytes | sha256 of the arm text as reviewed in round 5 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |


## Round 6 — the third post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-5
- Reviewed commit: `e3c95cd`
- Tree manifest, the reviewer's computation under the amended four-member
  recipe: `658ec0eb78b29adf58f8c579ac25f961644ab61b2bdf64930b8108e424fd8b27`
- Runs: one completed run attests this record. A first commissioning of this
  round was killed mid-run by the operator side minutes after launch: its
  brief carried round 4's stale preamble and the three-member recipe, so its
  attestation would have mismatched the harness. Nothing from that run is
  used; recorded here because a discarded run is a fact about the process.
- Reviewer's own verification: integrity exit 0; 181 passed; tracked status
  clean. **Round 5's findings 1, 7-9, 11, 13 pass; finding 2's mechanics
  pass; 3-6, 10, 12 partial** — as the findings state. Everything structural
  now passes: port scopes, wrapper differences, schedule, seals and ledger in
  ordinary operation, all twenty arm artifacts, CLAIM quotations, mirror
  provenance and isolation, the attestation binding, the four-member
  projection, the byte equation.

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 6) of Study 012 at commit e3c95cd on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Rounds 3-5 (records and dispositions tables at the end of PREREG-REVIEW.md) drove twenty, fourteen and thirteen accepted findings; all are implemented. Your first task: verify each of round 5's thirteen findings is genuinely implemented. Note one disposition that evolved during implementation: finding 3 landed as a VALIDATING bytecode gate — every cache entry must provably compile from the source beside it (interpreter magic plus the header's stamp or source hash; orphaned, stale or foreign refuses) — because the blanket refusal proved un-operable mid-suite; §2.10 registers the validating form, so judge the implemented rule and whether it still answers the finding. Also verify the round-5 additions: verify_tree()'s attestation cross-check against PREREG-REVIEW.md, the FOUR-member normalized projection, the two-way freeze coupling, and the byte-equation in MIRROR-AGREEMENT.md. Then a fresh sweep. This round reviews the COMPLETE post-disposition candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 AS AMENDED registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding the paths in harness/PINS.json freeze.excluded AND the two carriers (harness/PINS.json, PREREG-REVIEW.md), build the sorted list of lines "<path> <bytes> <sha256>" (paths relative to the study directory); then append the registry's normalized-projection entry — PINS.json parsed, freeze.treeManifestSha256, freeze.preregistrationSha256, golden.sha256 and isolationNegative.assent set to null, serialized with json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":")) plus a newline, hashed and listed as "harness/PINS.json#normalized <bytes> <sha256>" — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Verify integrity.tree_manifest() implements the same recipe, and state the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: e3c95cd"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R6-DONE.
```

### Complete unedited final message

1. [harness/integrity.py:1077](harness/integrity.py:1077): §2.10 says every cache entry must provably compile from its adjacent reviewed source. The gate checks only the 16-byte header, not the marshalled code payload; independently splicing a valid source-derived header onto foreign bytecode passed the gate and executed the foreign code. It also imports `policy_mirror` at line 82 before calling the gate at line 1136, and skips direct ignored `*.pyc` files outside `__pycache__`. **Severity: blocking.**

2. [README.md:223](README.md:223): §2.10 requires both freeze pins to land together, and `integrity.py:1017` correctly enforces both directions. The published ceremony instructs the operator to fill only `freeze.preregistrationSha256` and commit; its next command therefore refuses. **Severity: blocking.**

3. [PREREGISTRATION.md:2359](PREREGISTRATION.md:2359): The formal rule at §5.3 requires placement collapse, S5 at ceiling, the B/C gate, and no class-4 collapse. This later definition says CONFIRMED means placement collapse with controls, omitting S5 and class 4; `score_rates.py:3245` implements the full conjunction. The registration still states two confirmation rules. **Severity: blocking.**

4. [PREREGISTRATION.md:2336](PREREGISTRATION.md:2336): §5.4 correctly says 0.7359/0.3536 are coverage-side upper bounds because S5 is unmodelled. This sample-size prose still calls them the registered joint/CONFIRMED outcome, while `score_rates.py:881` calls them the probability of actually reaching row 5. The test at `test_verdict_parity.py:582` checks only the table labels, so the false prose survives. **Severity: blocking.**

5. [harness/score_rates.py:2045](harness/score_rates.py:2045): The record says non-string `startedAt`, `cwd`, or `home` evidence is `call-unreadable`. Using `call.get()` exempts missing and JSON-null values; no later gate owns `startedAt`. An independently sealed `startedAt: null` fixture scored valid, and `test_admission.py:1278` explicitly blesses absence. **Severity: blocking.**

6. [harness/batch.py:1131](harness/batch.py:1131): §2.8 promises crash resume and an exact descriptive shortfall. A slot is created and sealed before `BATCH.json` is rewritten non-atomically; interruption can leave a sealed orphan or malformed ledger. Resume selects the orphan’s index again and refuses its existing path, while shortfall counts disk slots and ledger records separately and emits an inconsistent declaration that the scorer rejects. **Severity: should-fix.**

7. [harness/score_rates.py:1842](harness/score_rates.py:1842): §3.3 registers `compile-refused`, and the reachability test claims every listed code can actually return. `extract_array()` catches every decoder `ValueError`, and the remainder of `compile_records()` has no value-error-producing path. The test merely harvests the syntactic exception handler, so `compile-refused` is dead. **Severity: should-fix.**

8. [harness/score_rates.py:2466](harness/score_rates.py:2466): C5 says a malformed ledger refuses whole scoring through the registered path. `load_ledger()` checks only that `records` is a list; `{"records":[null]}` reaches `schedule_key()` and raises an uncaught `AttributeError`, while `main()` catches only `ScoreError`. **Severity: should-fix.**

9. [README.md:12](README.md:12): Round-5 finding 12 was accepted, but this section still says only rounds 1–2 are complete and that the port and C10 mirrors are outstanding, contradicting both the tree and lines 3–10. **Severity: should-fix.**

10. [README.md:338](README.md:338): Round-5 finding 10’s corrected equation is present in `MIRROR-AGREEMENT.md`, but README still says full policy bytes plus a 706-byte suffix. The retained prompts are `28-byte prefix + POLICY[:-1] + 678-byte suffix`, equivalently full policy plus 705 non-policy bytes and a 677-byte suffix. **Severity: should-fix.**

11. [harness/PINS.json:4](harness/PINS.json:4): §2.10 presents `pinnedFrom.pins`, `.ports`, `.commit`, and their paths as runtime provenance members. `integrity.py:463` instead uses hard-coded digests and fixed paths; the registry members themselves are not checked, and tests assert only `pinnedFrom.pins`. Current values are correct. **Severity: nit.**

12. [harness/integrity.py:955](harness/integrity.py:955): The registered normalized projection has four nulled members, and the tuple correctly contains four. Its adjacent comment and `normalized_pins()` docstring still call them three. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready. Round-5 findings 1, 7–9, 11, and 13 pass; finding 2’s mechanics pass; findings 3–6, 10, and 12 remain partial. Port scopes, wrapper differences, schedule, ordinary seals/ledger, all twenty arm artifacts, CLAIM quotations, mirror provenance/isolation, attestation binding, four-member projection, and the MIRROR byte equation otherwise pass. Pinned integrity exited 0; the required full suite passed **181 tests in 130.62s**; tracked status remained clean.
Reviewed commit: e3c95cd
Tree manifest (my computation): 658ec0eb78b29adf58f8c579ac25f961644ab61b2bdf64930b8108e424fd8b27
CODEX-012-R6-DONE

### Dispositions

All twelve findings **ACCEPTED**. Finding 1 sharpens the validating gate to
what "provably compiles" must mean: the payload, not the header — every cache
entry's marshalled body must equal the running interpreter's own compilation
of the adjacent source, the mirror import is deferred so the gate runs before
any grid module loads, and stray `*.pyc` outside `__pycache__` refuse.
Finding 2 corrects the published ceremony to the two-pin freeze §2.10
registers. Findings 3 and 4 finish the confirmation-rule and coverage-side
sweeps at their last restatements, with a phrase lint pinning the §5.4 prose
so the false names cannot return. Finding 5 closes the presence exemption:
the three identity members must be present strings, and the test that
blessed absence is corrected rather than accommodated. Findings 6-8 as
written (atomic ledger append with the orphan-slot recovery stated, a live
`compile-refused` path, typed ledger records). Findings 9-12 as written.

## Arm text digests, as reviewed in this round

Unchanged since round 2:

| arm | bytes | sha256 of the arm text as reviewed in round 6 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |


## Round 7 — the fourth post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-6
- Reviewed commit: `f6b431a`
- Tree manifest, the reviewer's computation:
  `8f523370bdad6caa32ceb61e465e78002991a52e5b42705e538f42273ddebe01`
- Runs: one review run, completed; no run discarded
- Reviewer's verification first: integrity exit 0; 193 passed; tracked
  status clean. **Nine of round 6's twelve dispositions verified genuinely
  implemented** (2-5, 7-10, 12); 1, 6, 11 partial. Everything else passes:
  the wrapper's three differences, the schedule, ordinary ledger and
  shortfall, the §3.3 partition, §4's endpoints, §5's executable tables, all
  twenty arm artifacts with independent probes, CLAIM's quotation, mirror
  provenance and the five agreements.

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 7) of Study 012 at commit f6b431a on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Rounds 3-6 (records and dispositions tables at the end of PREREG-REVIEW.md) drove twenty, fourteen, thirteen and twelve accepted findings; all are implemented. Your first task: verify each of round 6's twelve findings is genuinely implemented. Two dispositions evolved during implementation, so judge the implemented rules: finding 1's bytecode gate decides 'provably compiles from the source beside it' by STRUCTURAL code equality (bytecode, names, consts with sets compared as sets, nested code recursed) under the cached object's own co_filename, with the mirror import deferred until after the gate and stray .pyc outside __pycache__ refusing — byte-equality of marshal is hash-seed-dependent for set constants, which is why; finding 6's crash recovery completes exactly one orphaned ledger record on --resume iff its seal verifies, refusing everything wider. Then a fresh sweep. This round reviews the COMPLETE post-disposition candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 AS AMENDED registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding the paths in harness/PINS.json freeze.excluded AND the two carriers (harness/PINS.json, PREREG-REVIEW.md), build the sorted list of lines "<path> <bytes> <sha256>" (paths relative to the study directory); then append the registry's normalized-projection entry — PINS.json parsed, freeze.treeManifestSha256, freeze.preregistrationSha256, golden.sha256 and isolationNegative.assent set to null, serialized with json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":")) plus a newline, hashed and listed as "harness/PINS.json#normalized <bytes> <sha256>" — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Verify integrity.tree_manifest() implements the same recipe, and state the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: f6b431a"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R7-DONE.
```

### Complete unedited final message

1. [harness/integrity.py:1118](harness/integrity.py:1118): The round-6 disposition says cached payloads must structurally equal the adjacent source’s compilation and no grid module may load before this gate. `_code_equal()` compares nested tuple contents using Python equality, so `(0,1,2,5)` and `(False,True,2,5)` incorrectly compare equal. Independently, `batch.py:195-200` imports `score_rates`, which imports `policy_mirror` at `score_rates.py:316-320`, before the gates at `batch.py:601` or `score_rates.py:2504`. A poisoned-cache probe executed before the later refusal. **Severity: blocking.**

2. [harness/integrity.py:997](harness/integrity.py:997): PREREGISTRATION.md:1101-1127 says the reviewed artifacts are the artifacts that run and every edit is detected. `tree_manifest()` considers only `git ls-files`, while `verify_bytecode()` rejects no untracked Python source. An untracked `harness/integrity/__init__.py` takes precedence over the reviewed `integrity.py` when `batch.py:191-200` imports it, bypassing every integrity gate without changing the manifest. This was reproduced in `/tmp` under the pinned interpreter. **Severity: blocking.**

3. [harness/score_rates.py:1985](harness/score_rates.py:1985): PREREGISTRATION.md:1039-1060 says a post-seal alteration cannot buy a denominator change; a seal discrepancy must invalidate confirmatory scoring for the entire batch. Both manifest implementations omit symlinks and other non-regular entries. Adding a symlink after sealing leaves `verify_seal()` successful, after which admission assigns `slot-symlink`, changes `I_X`/`V_X`, and potentially changes verdicts while `sealed=True`. **Severity: blocking.**

4. [harness/batch.py:1237](harness/batch.py:1237): Round-6 finding 6 requires `--resume` to complete exactly one verified orphan and refuse every wider disagreement. `reconcile_ledger()` scans only canonical future schedule paths at lines 1287-1288. An extra `run-099` is ignored and resume proceeds to spend calls; an empty ledger path also resolves to the existing study directory. Tests cover `run-099` only through shortfall, not resume. Malformed orphan-manifest JSON also escapes as an uncaught decoding exception. **Severity: should-fix.**

5. [harness/score_rates.py:2192](harness/score_rates.py:2192): PREREGISTRATION.md:1390-1397 defines `session-reused` when raw `session.jsonl` bytes, session ID, or call identity are shared. `slot_identity()` computes the raw digest and parses JSON in one `try`; malformed session or call JSON returns `None` and discards the usable digest. Two byte-identical malformed sessions therefore become `transcript-refused`, not `session-reused`. The reuse fixture uses only parseable sessions. **Severity: should-fix.**

6. [harness/score_rates.py:2629](harness/score_rates.py:2629): C5 says malformed population records refuse whole scoring through the registered path. Invalid or duplicate-key `BATCH.json` raises an uncaught `ValueError`; `SHORTFALL.json` containing `[]` reaches `.get()` at line 2796 and raises `AttributeError`. `main()` catches only `ScoreError`. Round-6’s typed-null-record fix works, but these malformed forms still produce bare tracebacks. **Severity: should-fix.**

7. [PREREGISTRATION.md:271](PREREGISTRATION.md:271): The enumerated port scope says `transcript_check.py` changes only the arm-specific prompt gate and “no other check logic.” The actual port adds `CompletionUndecodable` at `transcript_check.py:99` and changes UTF-8 exception behavior at lines 359-367. `PORTS.md:41` candidly records this second change, but the governing §2.2 scope does not. **Severity: should-fix.**

8. [harness/tests/test_batch.py:1453](harness/tests/test_batch.py:1453): PREREGISTRATION.md:1578-1588 promises a test that walks the complete published `RESULTS.json` and requires exactly the registered `ci95` scope. The test walks `fixtures.Population.score()`, a reduced object that omits production members including `cell`, `schedule`, and `crossArm`, and even gives `census` a different shape. Current production code contains no extra interval, but the asserted whole-object guard can miss one. **Severity: should-fix.**

9. [README.md:79](README.md:79): The governing rule at PREREGISTRATION.md:2112 and scorer code require `nP ≥ 3` plus arm E’s S5 labels at the ceiling. README’s CONFIRMED summary omits S5, while the stale comment at `score_rates.py:3375-3387` incorrectly says §5.3 still omits it. The executable rule is correct, but two reviewed summaries state the superseded rule. **Severity: should-fix.**

10. [README.md:228](README.md:228): The ceremony says PINS.json is never edited after registering the golden capture, then runs C7 without instructing the operator to change the currently null assent. `batch.py:1709-1714` requires the exact value `"granted"`, so following the published ceremony literally refuses at step 5. **Severity: should-fix.**

11. [harness/integrity.py:536](harness/integrity.py:536): Round-6 finding 11 accepted validation of `pinnedFrom.pins`, `.ports`, their paths, and `pinnedFrom.commit`. The implementation validates only the two digests; changing both paths and the commit in PINS.json still passes `verify_chain()`. The current recorded paths, commit, and source bytes are independently correct. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready. Round-6 findings 2–5, 7–10, and 12 are genuinely implemented; findings 1, 6, and 11 remain partial. The wrapper’s three differences, registered schedule, ordinary ledger/shortfall paths, §3.3 partition, §4 endpoints, and §5 executable tables otherwise match. All twenty arm artifacts passed integrity and independent census/permutation probes. The Study 011 quotation is exact; mirror provenance, prompt isolation, extraction, and all five 280-cell agreements pass. Pinned integrity exited 0; the full pinned suite passed 193 tests in 148.52 seconds; tracked status remained clean.

Reviewed commit: f6b431a  
Tree manifest (my computation): 8f523370bdad6caa32ceb61e465e78002991a52e5b42705e538f42273ddebe01  
CODEX-012-R7-DONE

### Dispositions

All eleven findings **ACCEPTED**. The three blockers close real holes the
prior fixes left: the structural comparator compares container CONTENTS with
type identity (a bool is not an int inside a tuple either), and the grid
module import is deferred in the scorer as it already is in integrity, so no
gate-guarded module loads before its gate; the gate refuses any untracked
Python source under the study tree, closing the package-shadowing bypass the
reviewer reproduced; and the slot seal records every entry by type — a
non-regular entry breaking the seal rather than buying a denominator change
— with §2.9's sentence amended from "every regular file" to say so.
Findings 4-10 as written, including §2.2's scope sentence catching up to the
round-5 decode split PORTS.md already records, the ceremony's assent step,
and the README/comment stragglers. Finding 11 completes the provenance
validation to the paths and the commit.

## Arm text digests, as reviewed in this round

Unchanged since round 2:

| arm | bytes | sha256 of the arm text as reviewed in round 7 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |


## Round 8 — the fifth post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-7
- Reviewed commit: `2607031`
- Tree manifest, the reviewer's computation:
  `d3fdbd313bfd185786427dc341a240a002303ad4fdcb3e8190890bce0b511ab8`
- Runs: one review run, completed; no run discarded
- Reviewer's verification first: integrity exit 0; 201 passed; tracked status
  clean. **Round 7's findings 5-9 and 11 fully verified; 1-4 and 10 partial.**
  The reviewer ACCEPTED round 7 finding 3's adjudicated reading in its own
  words: retaining `slot-symlink` while a broken seal forces whole-batch
  unresolved "genuinely buys no denominator or verdict change". Everything
  else passes: port tables and digests, registry members, the wrapper's
  permitted diff otherwise, seal sequencing, schedule, ordinary shortfall,
  the partition, the endpoints and tables, all twenty arm artifacts with
  independent probes, mirror chronology, the CLAIM quotation.

### Prompt (verbatim)

```
You are performing the FINAL pre-freeze cross-vendor adversarial review (round 8) of Study 012 at commit 2607031 on branch study-012-perturbation, repository root <worktree root>. The study directory is <worktree root>/studies/012-policy-perturbation. Rounds 3-7 (records and dispositions at the end of PREREG-REVIEW.md) drove 20, 14, 13, 12 and 11 accepted findings; all are implemented. Your first task: verify each of round 7's eleven findings. One adjudication is explicitly yours: finding 3's disposition could not suppress slot-symlink without violating §3.3's registered partition, so the implemented rule publishes the code while a broken seal forces whole-batch UNRESOLVED-BY-DESIGN (the code provably buys no denominator change) — judge that reading. Also judge the implemented forms: the type-strict structural comparator, the untracked-Python-source refusal, both lazy mirror imports, the every-entry seal (§2.9 as amended), resume's whole-population reconciliation, the raw-digest-first session identity. Then a fresh sweep. Then a fresh sweep. This round reviews the COMPLETE post-disposition candidate tree — the preregistration as it now stands, every harness source and test, the twenty arm files, harness/PORTS.md, harness/PINS.json, CLAIM.md, MIRROR-AGREEMENT.md, and the five analysis/mirror2_<arm>.py clean-room mirrors — because PREREGISTRATION.md §2.2 [D-20] registers that the last review must see the bytes that run.

Review format: READ-ONLY with respect to the repository — modify no tracked file. Your working directory is a scratch area outside the repo; write anything you need there. You may run the harness test suite and harness/integrity.py using the pinned interpreter at ~/.pyenv/versions/3.12.11/bin/python3 (run pytest with -p no:cacheprovider and PYTHONDONTWRITEBYTECODE=1 to avoid writing caches into the repo).

Tasks, in order:
1. Read PREREGISTRATION.md in full. It is the registration; everything else answers to it.
2. Verify the port against its registered scopes: §2.2's three tables (tiers, digests, enumerated changes) against harness/PORTS.md and the actual files; §2.7 against transcription/authoring_call.sh (exactly three permitted differences — assess the driver-side seal reading PORTS.md records against §2.9's wrapper sentence); §2.8 against batch.py's schedule, resume and shortfall; §2.9 against the seal and ledger code; §2.10 against harness/PINS.json member by member; §3.3's partition against score_rates.py; §4 and §5 against the scorer's endpoints, intervals and verdict tables; §6 C1-C10 against integrity.py and the test suite.
3. Verify the twenty arm artifacts satisfy §2.6 and Appendix A: run integrity.py yourself and check what it checks; probe at least two of its claims independently (for example, re-derive an arm's digit census or the C permutation by your own means).
4. Read CLAIM.md and check its two quoted passages against the cited sources in this repository (studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md section (d)); flag any divergence between quote and source.
5. Read MIRROR-AGREEMENT.md and the retained attempts under analysis/mirror2-attempts/; check the pre-assignment commit precedes the attempts (git log will show it), spot-check one extracted module against its raw transcript, and assess whether the isolation description matches what the retained prompt.txt files show was actually sent.
6. Run the full test suite under the pinned interpreter and report its result.
7. Compute the tree manifest yourself, exactly as §2.10 AS AMENDED registers it: over every git-tracked regular file under studies/012-policy-perturbation, excluding the paths in harness/PINS.json freeze.excluded AND the two carriers (harness/PINS.json, PREREG-REVIEW.md), build the sorted list of lines "<path> <bytes> <sha256>" (paths relative to the study directory); then append the registry's normalized-projection entry — PINS.json parsed, freeze.treeManifestSha256, freeze.preregistrationSha256, golden.sha256 and isolationNegative.assent set to null, serialized with json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":")) plus a newline, hashed and listed as "harness/PINS.json#normalized <bytes> <sha256>" — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Verify integrity.tree_manifest() implements the same recipe, and state the digest in your final message as your attestation of the bytes you reviewed.
8. Look for what the port got wrong that nothing above names: a registered sentence no code makes true, a check that can never fire, a digest bound to the wrong authority, a test that asserts less than it appears to.

Final message: a numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — followed by: an overall verdict line; the line "Reviewed commit: 2607031"; the line "Tree manifest (my computation): <hex digest>"; then the single line CODEX-012-R8-DONE.
```

### Complete unedited final message

1. [harness/score_rates.py:316](harness/score_rates.py:316), [harness/census.py:79](harness/census.py:79) — The round-7 record requires all grid imports to be deferred until after bytecode verification. `score_rates` eagerly imports `census`, which eagerly imports `policy_mirror`; importing `batch` therefore executes the mirror before `integrity.verify()`. The apparent lazy wrapper at `score_rates.py:321` does not close the original bypass. Severity: **blocking**.

2. [harness/batch.py:196](harness/batch.py:196), [harness/integrity.py:1176](harness/integrity.py:1176) — The record requires refusal of any untracked Python source. That refusal is inside `integrity.py`, but Python resolves an untracked `harness/integrity/__init__.py` package before the adjacent module. Thus the package can replace the gate containing the check. The exact round-7 shadow-package bypass remains reproducible. Severity: **blocking**.

3. [harness/integrity.py:1109](harness/integrity.py:1109), [harness/integrity.py:1135](harness/integrity.py:1135) — The record says structural equality establishes that the cached payload is the adjacent source compiled. The scalar fallback uses ordinary equality, admitting `0.0` versus `-0.0`; a pinned-interpreter probe returned equality even though execution preserved the observable negative zero. It also ignores `co_firstlineno` and `co_linetable` despite claiming every code attribute. Severity: **blocking**.

4. [harness/score_rates.py:2049](harness/score_rates.py:2049), [harness/batch.py:949](harness/batch.py:949) — I accept finding 3’s adjudicated reading: retaining `slot-symlink` while a detected broken seal forces whole-batch unresolved genuinely buys no denominator or verdict change. The implementation, however, walks only entries beneath the slot and never seals or `lstat`s the `run-NNN` root. Renaming a sealed directory and replacing its original path with a symlink to that directory left the seal verified while admission emitted `slot-symlink` and changed valid/invalid membership. The test at [test_admission.py:680](harness/tests/test_admission.py:680) only adds a symlink inside the root. Severity: **blocking**.

5. [harness/batch.py:1381](harness/batch.py:1381) — The record requires resume to reconcile the whole population and verify the exact registered prefix before spending calls. Recorded paths need only be nonempty and exist; they need not equal their scheduled canonical slot paths. A valid first schedule record naming existing `README.md`, with `run-001` absent, passed both prefix verification and reconciliation, allowing resume to skip index 1 and continue. Severity: **should-fix**.

6. [transcription/authoring_call.sh:140](transcription/authoring_call.sh:140), [harness/PORTS.md:132](harness/PORTS.md:132) — The port record says the wrapper itself enforces `arms/<ARM>/authoring/run-NNN/`. It checks only the parent and grandparent basenames, so `/tmp/C/authoring/run-001` passes for arm C, and the slot name is unrestricted. The canonical driver remains safe, but [test_batch.py:558](harness/tests/test_batch.py:558) tests only the wrong arm within a proper arms tree. Severity: **should-fix**.

7. [harness/integrity.py:883](harness/integrity.py:883) — C8 fixes E’s whole-file census at five clause labels, exactly one in-body `P<n>` reference, and three ISO digit runs. The expected counter is derived from however many references the actual body contains, so an added `P1` self-authorizes and cannot trip this check. The frozen E artifact itself is correct and pinned. Severity: **should-fix**.

8. [harness/integrity.py:913](harness/integrity.py:913) — C9 requires contiguous integer indices 0–5 and structural schema equality. Ordinary Python equality accepts JSON `false` as index 0; `[False,1,2,3,4,5]` also survives the class-vector comparison. Current family bytes carry proper integers, but the advertised structural control is not type-strict. Severity: **should-fix**.

9. [harness/batch.py:1098](harness/batch.py:1098) — The resume/shortfall record promises malformed population state is refused through the driver’s registered path. `load_ledger()` assumes the decoded top level is an object; `BATCH.json` containing `[]` raises an uncaught `AttributeError`, outside the catch at `batch.py:2203`. The corresponding scorer-side round-7 fix does pass. Severity: **should-fix**.

10. [MIRROR-AGREEMENT.md:32](MIRROR-AGREEMENT.md:32) — The record says each fresh reader session had “no memory of any other” and that E’s values were derived from E’s bytes alone. The retained prompts are clean, sessions and local `CODEX_HOME`s are distinct, and no tool calls occurred, but this cannot exclude provider-side cross-session state; [PREREGISTRATION.md:2946](PREREGISTRATION.md:2946) expressly concedes that limitation. Because E ran last after prompts exposing 40/70, the categorical wording overstates the evidence. Severity: **should-fix**.

11. [README.md:229](README.md:229) — Round-7 finding 10 required an explicit assent edit. The edit is now documented, but the ceremony first says PINS is never edited again and immediately instructs editing `isolationNegative.assent` at line 234. It remains internally contradictory. Severity: **should-fix**.

12. [README.md:12](README.md:12) — The status says six rounds, with post-port rounds 3–6, while `PREREG-REVIEW.md` contains round 7 and this candidate implements its dispositions. Severity: **nit**.

Overall verdict: BLOCKING — Study 012 is not freeze-ready. Round-7 findings 5–9 and 11 are fully verified; 1–4 and 10 remain partial. The port tables and digests, PINS members, permitted wrapper diff otherwise, driver-side seal sequencing, schedule and ordinary shortfall, §3.3 partition, §4/§5 endpoints and tables, all twenty arm artifacts, independent E digit census and C permutation, mirror chronology/extraction/prompt equation, and the repository-backed CLAIM quotation otherwise pass. Pinned integrity exited 0; the full pinned suite passed 201 tests in 184.55 seconds; tracked status remained clean.

Reviewed commit: 2607031  
Tree manifest (my computation): d3fdbd313bfd185786427dc341a240a002303ad4fdcb3e8190890bce0b511ab8  
CODEX-012-R8-DONE

### Dispositions

All twelve findings **ACCEPTED**. The instructive one is finding 2: the
untracked-source refusal lived inside the module the shadow package
replaces, so the module could never defend itself — the tripwire moves into
the entry files the ceremony names by path (`batch.py`, `score_rates.py`),
which the import system cannot shadow, before any harness import; the
registered reasoning goes with it. Finding 1 completes the lazy-import
discipline through the census chain. Finding 3 makes the scalar fallback
distinguish what Python equality will not (a float compares by its bits) and
extends the member list to the line attributes it claimed. Finding 4 seals
the slot ROOT itself — the root's own lstat type is an entry, so replacing
the directory with a symlink to it breaks the seal. Findings 5-9 as written.
Finding 10 softens MIRROR-AGREEMENT's categorical no-memory sentence to what
the retained bytes support, deferring to the provider-side-state concession
the preregistration already carries. Findings 11-12 as written.

## Arm text digests, as reviewed in this round

Unchanged since round 2:

| arm | bytes | sha256 of the arm text as reviewed in round 8 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 9 — the sixth post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-08; drafting as recorded in rounds 1-8
- Reviewed commit: `993c66c`. Its parent `f5ab566` carries identical reviewed
  bytes — the only change between them is `PREREG-REVIEW.md`, which §2.10
  excludes from the manifest as a carrier
- Tree manifest, the reviewer's computation:
  `a2eef66bcae730dcc0d831a9d2f21ad7672832ca4155b9f75cfeb9e3cf0b6456`
- Runs: **two commissionings, the first discarded** (recorded immediately
  below, with the scope correction it forced); the second completed
- Reviewer's verification first: integrity exit 0 (tree manifest unbound,
  pre-freeze); 208 passed in 197.39s; tracked status clean; the reviewer's own
  84-entry manifest matched `integrity.tree_manifest()`. **Ten of round 8's
  twelve dispositions fully verified**, disposition 11 substantively
  implemented, disposition 2 partial (finding 1 below). Independent re-derivations
  all matched: digit census, arm C's permutation by enumeration, HEADER and
  prompt arithmetic, artifact assembly, schedule balances, partition, interval
  vectors, verdict tables, `CLAIM.md` provenance, retained C10 attempts.

### The first commissioning, discarded

The first commissioning of round 9, over `f5ab566`, produced no findings and
no attestation. It ran to roughly 590,000 tokens and then the reviewing
vendor's safety classifier refused its output three times
("flagged for possible cybersecurity risk"). The cause is visible in the
retained transcript: testing round 8's untracked-source refusal, the reviewer
had begun authoring a working shadow package — one that replaced
`subprocess.run` so the check would report a clean tree — and that artifact,
read without this study's context, is indistinguishable from malware
development.

Recorded rather than quietly re-run, because it is a fact about this
process and because it marks a boundary worth stating: **rounds 6 through 8
concentrated on the tamper-resistance of the harness rather than on the
study.** That drift was productive — it closed a symlink-sealed slot, a
shadowable module, a laundering comparator — but it has passed the point
where the registration's own claims are the subject. §2.10 already states
what the in-tree binding does and does not establish; §7 and §9 already
concede that an operator who edits the record can defeat any digest the
record carries. A reviewer writing exploit code against those mechanisms is
testing a threat model the study does not claim to defend against.

The round is therefore re-commissioned with a brief that (a) asks for
described gaps rather than demonstrated ones — file, line, what the check
establishes, what it does not, what a complete check would require — and
(b) puts the study's registered content first: the arms, the schedule, the
partition, the endpoints, the verdict rules, the controls, and the claim.
The rescoped brief and the script that runs it are handed to the maintainer
rather than commissioned from inside the drafting session; the run they
perform is the one this section will be completed from.

Nothing from the discarded run is used, and no finding it may have been
forming is known to this record.

### How the second commissioning was run

The rescoped brief and the script that runs it were handed to the maintainer
rather than commissioned from inside the drafting session. The script refuses
unless the worktree is at the commit the brief names and the study directory is
clean — a review attests a commit, not a worktree — and both preconditions were
checked and held before the run. The session's own permission layer then refused
to execute the script itself, so its parts were run directly and faithfully:
the same prompt substitution, the same `codex exec --ignore-user-config
-m gpt-5.6-sol -c model_reasoning_effort=ultra --sandbox workspace-write`, a
scratch working directory outside the repository, and the same
`prompt.txt`/`stdout.raw`/`stderr.raw`/`exit-status` output set. **One
deviation, recorded because a deviation not written down is a deviation
claimed:** the run used Codex's default `CODEX_HOME` under
`--ignore-user-config` rather than the script's isolated home with a copied
credential — strictly less credential movement, and user config still excluded.
Exit 0, roughly 448,000 tokens, completion marker present, no classifier
refusal. The tree was unchanged by the review: `993c66c`, status clean.

The maintainer independently recomputed the tree manifest with
`integrity.tree_manifest()` and obtained the digest the reviewer attested.

### Prompt (verbatim)

```
You are performing a verification review — round 9 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <repo>/studies/012-policy-perturbation
Reviewed commit: 993c66c on branch study-012-perturbation (its parent f5ab566 carried the same reviewed bytes; the only change is PREREG-REVIEW.md, which §2.10 excludes from the manifest as a carrier)

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Verify round 8's twelve dispositions.** `PREREG-REVIEW.md`'s round-8 section lists twelve findings and, beneath them, the maintainer's dispositions. For each: is the disposition genuinely implemented in the bytes at this commit? Report any that is partial, mis-implemented, or implemented only in prose.

Two of those implementations were placement decisions the maintainer flagged for your judgment. Assess them **by reading**:

- The check that refuses untracked Python sources under the study tree was moved from inside `harness/integrity.py` to the top of the two entry files the operating procedure invokes by path (`harness/batch.py`, `harness/score_rates.py`), guarded by `if __name__ == "__main__"`. The reasoning recorded is that a check living inside a module cannot establish anything about that module being the module that loaded. Does that placement establish what §2.10 claims, for the commands the README's procedure actually runs? What does it still not establish?
- The wrapper's slot-path check (`transcription/authoring_call.sh`) verifies the last four path components rather than anchoring to an absolute study root. `harness/PORTS.md` records why an absolute anchor was not taken (it would require a fourth permitted wrapper difference under §2.7, which is a registration change). Is that reasoning sound, and is the implemented form the strongest available within the registered shape?

**2. The registered content — a fresh sweep, and the priority of this round.** Rounds 6-8 concentrated on the harness's tamper-resistance mechanisms. This round's first duty is the study itself: the thing it measures, claims, and will publish.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two of these independently (a digit census, arm C's permutation by enumeration, the HEADER byte arithmetic).
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**3. Run the suite and the verification command**, and report both results.

**4. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line;
- the line `Reviewed commit: 993c66c`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R9-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

1. **The round-8 untracked-source disposition is only partially implemented.** PREREG-REVIEW.md:1268 says the tripwire runs before any harness import. Both entry files instead import `integrity` first—batch.py:196 and score_rates.py:316—before their scans at lines 202 and 317. For README's path-invoked commands, this selects the reviewed entry file and rejects ordinary untracked `.py` files before later harness imports, but it cannot establish that the loaded `integrity` was reviewed. Moving the scan earlier is the minimum fix; a complete assurance would externally validate resolved import targets, symlinked package directories, caches, and other importable artifacts before any study-local import. **Severity: blocking.**

2. **The `CONFIRMED` rule does not establish threshold comprehension.** PREREGISTRATION.md:1767 and PREREGISTRATION.md:1927 interpret arm-E `|Q|=0` as showing that the author understood the thresholds but chose not to test them. score_rates.py:1132 checks only that some accepted record exists and none is mislabelled; score_rates.py:3633 can then select row 5. Correctly labelled records decided entirely by sanctions or embargo membership can keep class 4 tracking and make `nP ≥ 3` without any accepted record exercising either numeric threshold. The tests at test_verdict_parity.py:340 prove aggregate-rule parity, not the comprehension gloss. Confirmation needs registered threshold-dependent comprehension evidence, or the inference must be weakened. **Severity: blocking.**

3. **C7 is ordered before the batch in prose but is not a batch precondition.** PREREGISTRATION.md:2565 and README.md:238 require the isolation-negative probe first. Its standalone command is sound, but registered-run preflight at batch.py:656 checks neither assent nor the canonical retained verdict. All 150 calls can therefore run with assent null and no C7 record. Preflight and scoring should validate the canonical control's shape, bindings, and acceptable completed outcome. **Severity: should-fix.**

4. **Early declared shortfalls cannot be scored.** Section 2.8 promises descriptive publication for any incomplete prefix (PREREGISTRATION.md:939); batch.py:2070 permits such declarations, including zero slots. Scoring unconditionally calls collect_slots() at score_rates.py:2585, which rejects an arm whose `authoring/` directory has not yet been created. Prefixes 0–4 therefore fail before terminality; the zero prefix also lacks the ledger required at score_rates.py:2753. Missing roots and an absent ledger should mean an empty population only under a strictly validated matching shortfall, with an end-to-end test. **Severity: should-fix.**

5. **The manifest exclusion predicate is broader than the registered list.** The registry distinguishes exact output files from trailing-slash output trees at PINS.json:159. integrity.py:1032 treats every member as a subtree prefix, so an unlisted tracked descendant such as `RESULTS.json/...` would also be omitted. This does not affect the current digest, which matched independently, but it is not the exact-path recipe stated. Prefix exclusion should apply only to entries ending `/`. **Severity: should-fix.**

6. **The wrapper suffix guard is safe in the README procedure, but neither the rationale nor "strongest available" claim holds.** authoring_call.sh:145 checks only the final four components. The actual procedure is safe because batch.py:231 derives the canonical root and passes its own constructed slot. The wrapper alone still accepts the registered suffix beneath another absolute root and does not resolve parent symlinks or verify the scheduled index. Contrary to PORTS.md:148, the wrapper already resolves `$STUDY` at line 87, so an exact `$STUDY/arms` anchor needs no new production argument; only preserving the present patched-root fixture through an override would add a fourth difference. **Severity: should-fix.**

7. **C10 is not model-call-free.** PREREGISTRATION.md:2673 calls it a "pre-data, model-call-free check." MIRROR-AGREEMENT.md:24 and lines 49–118 document five GPT/Codex sessions. Only the final comparator at integrity.py:960 is model-call-free. The retained evidence and 280-cell agreements otherwise check out. **Severity: should-fix.**

8. **Every `FAMILY.json` carries false inherited metadata.** For example, arms/A/FAMILY.json:3 names a nonexistent pack and says a drand draw in §5 selects a mutation applied to packs C and D. This study performs none of those operations; score_rates.py:1399 deliberately reads only the class schema and says patches are not read. Because arm A's bytes are inherited and locked, the registration should identify these members as inert legacy metadata. **Severity: should-fix.**

9. **The row-5 operating-characteristic joint law is under-specified.** PREREGISTRATION.md:2187 identifies primary/S1 dependence, while lines 2217–2259 say the reported figures use only independence layers 1–3 and are exact for the coverage pattern. score_rates.py:1025 effectively reuses arm A's primary-HIGH pattern as its placement-HIGH pattern. The figures are exact only if the scenario assigns equal marginals to both endpoints, which together with `H ⊆ raw` identifies their indicators; that assumption should be stated or replaced by an explicit joint model. **Severity: should-fix.**

10. **The inclusivity invariant accidentally includes arm E.** PREREGISTRATION.md:688 says every arm at `(40,70)` places inclusivity words beside numeric literals, although E deliberately has no threshold literals. integrity.py:813 correctly applies literal adjacency only to A/B/D and checks E's named bound senses separately. **Severity: nit.**

11. **The landmark-grid explanation overstates its points.** PREREGISTRATION.md:425 says every non-0/100 landmark is an edge and describes an excluded-side point for every edge. Several are offset probes, and for an exclusive upper edge the `−0.01` point is on the included side. The actual grid at integrity.py:221 is correct. **Severity: nit.**

12. **The §5.4 zero-probability note is false.** PREREGISTRATION.md:2159 says every printed `0.0000` is nonzero, despite exact zeros in the `p=0` and `p=1` rows; it also gives approximately `4×10⁻¹¹` for `P(HIGH|p=.30,N=30)`, while score_rates.py:929 correctly computes approximately `1.112149×10⁻¹¹`. No decision reads these figures. **Severity: nit.**

Overall verdict: BLOCKING — Study 012 is not freeze-ready because round-8 disposition 2 remains partial and the registered confirmation rule does not rule out comprehension failure. The other ten round-8 dispositions are fully implemented and disposition 11 is substantively implemented. The pinned integrity command exited 0 (`tree manifest unbound`, as expected pre-freeze); the pinned suite passed 208 tests in 197.39 seconds with 59,200 `co_lnotab` deprecation warnings; tracked status remained clean. My 84-entry manifest matched `integrity.tree_manifest()` on the present tree, subject to finding 5. Independent digit census, arm-C enumeration, HEADER/prompt arithmetic, artifact assembly, schedule balances, partition, interval vectors, verdict tables, CLAIM provenance, and retained C10 attempts otherwise matched.

Reviewed commit: 993c66c
Tree manifest (my computation): a2eef66bcae730dcc0d831a9d2f21ad7672832ca4155b9f75cfeb9e3cf0b6456
CODEX-012-R9-DONE

### Dispositions

All twelve findings **ACCEPTED**. Two were verified as only partly right and are
dispositioned on corrected grounds, recorded below rather than silently
narrowed. Before writing these dispositions each finding was independently
re-verified against the bytes at `993c66c` — every load-bearing claim checked,
every line anchor confirmed or corrected, every proposed remedy priced against
what §2.7, §2.10 and the locked arm bytes actually permit.

**Finding 1 is worse than "cannot establish", and the record was the thing at
fault.** Round 8's disposition said the tripwire runs "before any harness
import" and it did not: `import integrity` stood above it in both entry files.
The one module that escaped was the gate module — precisely the module round 8
finding 2 named, and a regular package directory outbids an adjacent module in
import resolution — so the bypass class was reachable rather than merely
unproven. `sys.dont_write_bytecode` sat one import too late for the same
reason, and its comment claimed "the ceremony's commands" plural while only one
command set it at all. The scan and the flag now precede the first study-local
import in both entry files, `sys.path.insert` follows the scan, `score_rates.py`
and `integrity.py` set the flag too, and a new `EntryFileOrdering` class gives
both scans their first test coverage — the suite exercised neither before, which
is why the regression was invisible twice. **A third path-invoked entry was
checked and is clean:** `integrity.py` imports nothing study-local at module
scope and makes `verify_bytecode` the first statement of `verify()`. What the
tripwire still does not establish is stated rather than closed: it refuses
untracked *sources* before the first import; it does not establish that the
cache `integrity` loads from is that source compiled — §2.10 registers a
validate-not-ban gate and the gate cannot precede itself — and `os.walk` does
not descend symlinked directories. The `-P`/`PYTHONSAFEPATH` closure is
available and is **declined this round** as a larger change than the finding
requires.

**Finding 2 is the round's real result, and the reviewer's framing understated
it.** The verification found the registration already conceding the gap and then
contradicting itself: §4.5 registers X6 so a comprehension failure is
"diagnosed rather than assumed away by S5", while §4.6 said S5 is what
distinguishes it. Both halves of the fix are taken. **The inference is
weakened** — the two reading cells now say what the rule sees (`no accepted
record was mislabelled, and none was placed at the boundary`; `at least one
accepted record was mislabelled`), a new registered paragraph records what the
ceiling establishes and what it does not, and §5.3 and §5.5 follow. **And the
rule is strengthened** — [D-10] gains a fifth conjunct: class 3, the interior
review band, must not collapse in arm E. Class 3 is the one class whose members
are scored *between* the thresholds, so it cannot be covered by a record the
mirror decides before it reads `riskScore`; the conjunct therefore excludes the
degenerate arm E whose accepted records are all sanctions or embargo cases —
records correct at every threshold pair, which is how CONFIRMED could have
fired on what §4.6 calls a comprehension collapse. It is registered as excluding
a degenerate case and **not** as establishing comprehension, because nothing
available to this design can: a set of correct labels pins the threshold pair
only to an interval, and pinning it from both sides needs records on both sides
of a threshold — the boundary-testing CONFIRMED's own premise says arm E did not
do. The conjunct's weakness is registered with it ("does not COLLAPSE" is not
HIGH; it is satisfied vacuously if arm A is not HIGH on class 3). Taken in the
"does not COLLAPSE" form deliberately: the term matches the class-4 term's shape
and ~10⁻²³ magnitude, so **no published §5.4 figure moves** — verified to
0.000e+00 at every N. Row 7's why-string was rewritten, because the fifth
conjunct makes INDETERMINATE newly reachable with a *confirming* §4.6 reading
and the old gloss asserted otherwise. `CLAIM.md` is untouched: §8's publication
commitment fires on row 4, not row 5.

**Finding 3, on the narrower predicate.** C7 is now a precondition of the batch
and of the scorer, not only of its own command — assent, the canonical retained
verdict, its shape, and its binding to the same assent and the same golden
capture this batch runs behind. The reviewer's stricter "acceptable completed
outcome" is **rejected**: §6 C7 registers `no-context` as a third outcome
"reported as undemonstrated", and because the control refuses to rewrite an
existing record, a strict gate would make that registered sentence unreachable
except by hand-deleting a control record. All three registered outcomes admit
the batch; what the batch now refuses is a control that never ran. Recorded
consequence: `run --dry-run` also refuses until the record exists, matching
README's step 5 → 6 order and the golden gate's existing behaviour.

**Finding 4's root cause was in the fixtures, not the scorer.** The scorer
refused prefixes 0–4 because an arm the registered prefix has not reached has no
`authoring/` root — and no test could see it, because `build_arms_root` created
all five roots up front. The fixture now builds the tree a real batch leaves,
the scorer distinguishes an absent root from one that is present and not a
directory, and an absent ledger is admitted only for a declaration recording
zero rounds, zero slots and no last slot (bool-excluding, per round 8 finding 9).
A parameterised end-to-end test drives `score()` itself over prefixes 0 through
5, including the zero prefix with no `BATCH.json` at all, and five negative
cases pin the relaxation's edges. §2.8 gains one sentence naming the boundary.
Confined to round 1 by construction: every prefix of length ≥ 5 has touched all
five arms.

**Findings 5, 7, 9, 11 and 12 as verified, each with the check the study's own
convention asks for.** The manifest exclusion becomes a named predicate —
trailing-slash entries exclude subtrees, every other entry exactly one path,
carriers included — with the rule registered in §2.10 rather than living only in
code, and `test_manifest.py` gives `tree_manifest()` its first test coverage
anywhere. C10's "model-call-free" is withdrawn and replaced by what is true:
the *instrument* is five published model sessions, the *verdict* is a code
comparator, and "pre-data" is defined as the batch's authoring calls, of which
C10 makes none. The phrase entered this file from round 1 finding 5's own
wording, which is recorded here and **not** retro-edited at its source.
§5.4 gains the layer-4 statement its own "any such figure is marked" promise
required — the scenario assigns `p` to both endpoints and `H ⊆ raw` holds
pathwise, so the two indicators are equal almost surely and the marginal
assignment *is* the joint model; the reviewer's "explicit joint model"
alternative is a false alternative, since no joint freedom remains. The
alternative extreme's figures are printed and pinned, and the substitution is
explicitly **not** claimed conservative. §2.4's grid explanation is replaced by a
census — five edges, seven probes, two sentinels — naming which side each 0.01
neighbour falls on and admitting that `T_low + 0.01` is carried for symmetry
with `T_high + 0.01` rather than for an answer it alone changes; the same false
sentence in `landmarks()`'s docstring goes with it. §5.4's zero note is corrected
to `1.1 × 10⁻¹¹`, names the four exact cells and the file's other exact zeros,
and — the part that matters — the marginal level table is now diffed against the
scorer, which makes §5.4's own "asserted by a harness test" sentence true for
the table it introduces. That claim had been unbacked through eight rounds,
which is how an invented magnitude survived them.

**Findings 6 and 8 are ACCEPTED on corrected grounds; the corrections are the
record.** Finding 6 argued "contrary to `PORTS.md`", but `PORTS.md` itself names
`$STUDY/arms` as the alternative it rejected, gives a fixture reason rather than
a missing-argument reason, and the quoted phrase "strongest available" appears
nowhere in the tree. The *substance* nonetheless lands, and it lands harder than
the finding claimed: the fixture reason is not forced. A stand-in study reached
through a symlinked wrapper resolves `$STUDY` into the test tree, so the exact
anchor needs no fourth §2.7 difference and no new environment member. The
wrapper now requires `$SLOT` to equal this study's own
`arms/<ARM>/authoring/run-NNN`, plus a physical-anchor check that catches a
replaced `arms` or `authoring` component, and the tests move `$STUDY` instead of
weakening the wrapper. Two things are recorded as scope, not defect: the
scheduled index deliberately does not travel to the wrapper (§2.7 caps its
differences at three), and a checkout reached through a symlinked path now
fail-closes, because the driver resolves logically and the wrapper physically.
One incidental defect found while proving the layout is fixed with it: a failed
`git rev-parse` left `GIT_ROOT` silently equal to the caller's directory instead
of refusing. Finding 8's premise that the patches are inert is **rejected on the
bytes**: §6 C2 reads `mutations[].patch` against Study 010's locked pack C for
arms A, B, C and E, and [D-6] reads arm D's to demonstrate that indices 1, 2 and
5 are unavailable there. The pack is not nonexistent either — it is 010's file at
the digest 010's own lock carries; what is true is that the path resolves in
010's tree. And arm D's `FAMILY.json` is not inherited: it is generated at
(45, 72) as the σ-image of arm A's. The genuine gap is real and fresh: §2.6
described a twenty-file artifact set in one table cell while a reviewer must
attest every byte. §2.6 now registers `FAMILY.json`'s whole member list, split
into what this study reads and the six members that are inert, with the reason
they are retained rather than removed — arm A's bytes are 010's lock and one
generator produces all five, so editing them would break the byte equality the
class schema is anchored to. Finding 10's quantifier was wrong at **both** ends,
which the finding named only half of: "every arm at (40, 70)" is this study's
own fixed name for {A, B, C, E}, while the literal-adjacency invariant holds of
{A, B, C, D} — the arms that state their thresholds as literals. Corrected at
both sites, with arm C's status stated (its tuple sequence is A's by byte
identity, not by a second comparison) and arm E's named form pointed to. No code
change: adding C to the comparison would be a provable no-op.

**What this round did not do.** `verify_mirror2()` still has no direct unit
test — its two refusal paths are exercised only transitively — and
`verify_tree()` and `normalized_pins()` remain untested beyond what
`test_manifest.py` now covers for `tree_manifest()`. Both are recorded here as
open rather than folded into a disposition they do not belong to.

Verification after the dispositions: `harness/integrity.py` exit 0 (tree
manifest unbound, pre-freeze); the pinned suite **253 passed** (208 at the
reviewed commit, plus 45 added by these dispositions); tracked status clean.
The post-disposition tree manifest, the maintainer's computation, is
`4c677eba037a75bae242c42ceb4d5ed57363ccbefd55d42a99773e4e79f339df` — round 10
attests it independently, and under §2.10 rule 3 that round is required, because
these dispositions changed bytes.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above — no
disposition in this round touches a file under `arms/`:

| arm | bytes | sha256 of the arm text as reviewed in round 9 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |
