# Pre-freeze adversarial review — Study 012

This file is the complete pre-freeze review record for Study 012. It records
every adversarial round the preregistration and the five arm texts are put
through before any freeze decision: who reviewed, by what method, the verdict
verbatim where one exists, every finding faithfully summarized, and what was
done about each one. Nothing is discarded. It follows Study 011's per-round,
per-finding disposition format.

**Status: OPEN. Eighteen rounds complete, rounds 2 through 18 cross-vendor. Nothing
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
records the sha256 of each of the five arm texts as that round reviewed them**.
Round 2 superseded that binding (next paragraph) and no code reads these tables:
they stay as the record of the bytes each round read. What `harness/integrity.py`
enforces is the whole-tree manifest; the frozen arm digests answer to
`harness/PINS.json` through `integrity.verify_arms()`, not to this file, and the
one line of this file the code does read is the **last** tree-manifest
attestation, which the freeze pin must equal.

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

## Round 10 — the seventh post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-09; drafting as recorded in rounds 1-9
- Reviewed commit: `14725fb`
- Tree manifest, the reviewer's computation:
  `4c677eba037a75bae242c42ceb4d5ed57363ccbefd55d42a99773e4e79f339df` — 85
  entries, identical to the maintainer's own computation recorded in round 9's
  dispositions
- Runs: one review run, completed; no run discarded, and no classifier refusal
  (the one refusal signature in the transcript is the reviewer *reading* round
  9's discarded-run record). Run as round 9's second commissioning was, with
  the same deviation recorded there
- Reviewer's verification first: integrity exit 0; 253 passed in 275.47s;
  worktree clean. **Round 9's dispositions 4, 5, 7, 8, 10 and 12 fully
  implemented**; 9's central implementation present; 11's artifact and prose
  correction right but its named test weaker than claimed. Independent
  re-derivations all matched: artifact assembly, all twenty arm hashes, digit
  censuses, arm-C enumeration, the 280-cell grids, the five schedule balances,
  interval vectors, cuts and table encodings, `CLAIM.md` against its Study 011
  source, and all five retained C10 attempts

### Prompt (verbatim)

```
You are performing a verification review — round 10 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 14725fb on branch study-012-perturbation

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Verify round 9's twelve dispositions.** `PREREG-REVIEW.md`'s round-9 section lists twelve findings and, beneath them, the maintainer's dispositions. For each: is the disposition genuinely implemented in the bytes at this commit? Report any that is partial, mis-implemented, or implemented only in prose.

Round 9's blocking finding 2 was answered in two halves, and both are yours to judge:

- **The weakening.** §4.6's two reading cells no longer name a mental state, a new registered paragraph states what `|Q| = 0` establishes and what it does not, and §5.3 and §5.5 follow. Does the registration now claim only what its rules see? Is there any remaining sentence — in `PREREGISTRATION.md`, `README.md`, `harness/score_rates.py`'s docstrings, or `CLAIM.md` — that still reads the ceiling as comprehension evidence?
- **The strengthening.** [D-10] gained a fifth conjunct: arm E must not read COLLAPSE on class 3. The registered argument is that class 3 is the only class whose members are scored *between* the thresholds, so it cannot be covered by a record the mirror decides before it reads `riskScore`; the conjunct is registered as excluding a degenerate case and explicitly **not** as establishing comprehension, on the ground that no conjunct available to this design could. Judge both claims. Is the class-3 argument sound on the family's own predicates? Is the impossibility argument sound, or is there a conjunct this design could carry that would establish more? Is the conjunct's own registered weakness stated fully enough?

Two further dispositions took a position the maintainer flagged for your judgment:

- **Finding 3.** The C7 gate admits all three registered outcomes — `refused`, `matched` and `no-context` — rather than only a "completed" one, because §6 C7 registers `no-context` as reported-but-undemonstrated and the control refuses to rewrite an existing record. Is that reading of §6 C7 right, and does the implemented gate refuse everything it should?
- **Finding 6.** The wrapper now anchors the slot to this study's own `arms/<ARM>/authoring/run-NNN` rather than to a four-component suffix, and the harness tests reach it through a stand-in study rather than by weakening the wrapper. §2.7 still registers exactly three permitted differences. Does the implemented form add a fourth, and does the anchor hold for the commands the README's procedure actually runs?

**2. The registered content — a fresh sweep.** Round 9's first duty was the study rather than the harness, and it found its blocking result there. Keep that priority.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it. Round 9's dispositions edited §2.4, §2.6, §2.8, §2.10, §4.6, §5.3, §5.4, §5.5, §6 C7/C8/C9/C10, §7 and §10 — read the amended sections against what they now govern, and read the untouched ones as if for the first time.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two of these independently (a digit census, arm C's permutation by enumeration, the HEADER byte arithmetic).
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**3. The forty-five new tests.** Round 9's dispositions grew the suite from 208 to 253. New coverage is where a study is most likely to assert more than it checks. Read the added tests — `EntryFileOrdering` in `test_batch.py`, the C7 gate tests, the prefix-0-through-5 scoring tests, all of `test_manifest.py`, the `FAMILY.json` member tests in `test_controls.py`, the landmark straddle test in `test_mirror.py`, and the new §5.4 lints and table diffs in `test_verdict_parity.py` — and ask of each: would it fail if the thing it names stopped being true? Name any that would not.

**4. Run the suite and the verification command**, and report both results.

**5. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe, including its amended exact-path-versus-tree exclusion rule.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line;
- the line `Reviewed commit: 14725fb`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R10-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The reviewer's own `## Findings` heading is demoted to keep this record's
section structure; no other byte of the message is altered, and the absolute
paths its markdown links carried are rendered as the `file:line` anchors they
point at.)

#### Findings

1. **Round-9 disposition 1 remains incomplete. Severity: blocking.** The disposition says the untracked-source tripwire precedes the first study-local import (PREREG-REVIEW.md:1474). In fact, batch.py:194, score_rates.py:309, and integrity.py:63 import standard-library names before their scans. Path invocation puts `harness/` on Python’s import path, so an adjacent untracked source colliding with one of those names can load before the check. The check establishes that ordinary untracked sources are rejected once reached; it does not establish that nothing adjacent loaded first. `EntryFileOrdering` plants only a generic `planted.py`, and its AST checks cover `ast.Import`, not `ImportFrom` (test_batch.py:1932). A complete closure needs `-P`/`PYTHONSAFEPATH` in the registered commands or an external pre-import bootstrap.

2. **Round-9 disposition 2’s weakening still overclaims. Severity: blocking.** The amended table says S1 LOW means “none was placed at the boundary” (PREREGISTRATION.md:1828); score_rates.py:612 publishes the same statement. But LOW permits `k≤3` at N=30 (PREREGISTRATION.md:1913), so one to three slots may contain boundary records. The LOW-plus-degraded branch also remains categorically published as “comprehension collapse,” although the later disclaimer says it names only an available explanation. The new lint rejects only two former phrases and explicitly accepts that label (test_verdict_parity.py:423). Positively, I found no remaining sentence in the requested four files treating the ceiling itself as comprehension evidence; §5.3 and §5.5 correctly disclaim that inference.

3. **Round-9 disposition 2’s strengthening does not reliably exclude the degenerate arm it names. Severity: blocking.** The record says E not reading COLLAPSE on class 3 excludes an arm containing only sanctions/embargo cases (PREREGISTRATION.md:1841). The code checks only that the class-3 contrast is not `COLLAPSE`. If A is not HIGH on class 3, that contrast is unavailable/indeterminate and the conjunct passes vacuously; A may still be HIGH on the other five classes, the B/C gate may pass, and an E with clean embargo records and no numeric coverage can reach row 5. The operating-characteristic code explicitly models the missing-class-3 case this way (score_rates.py:1091). The record admits vacuity at PREREGISTRATION.md:1851, but does not acknowledge that vacuity defeats the claimed exclusion.

   The supporting argument is also unsound: class 2 nests inside class 3 and is likewise between the thresholds (PREREGISTRATION.md:347); a non-personal class-3 record may exercise only the high comparison. Finally, “no conjunct available” is too broad: LOW permits up to three covering slots, so the design could require actual correctly labelled straddles around both thresholds while remaining LOW. Such evidence would establish threshold-sensitive behavior, though still not an internal mental state or freedom from memorization.

4. **§5.4’s joint operating-characteristic model is logically incompatible with the registered classes. Severity: blocking.** The registration states `0` nests in `1` and `2` nests in `3` (PREREGISTRATION.md:369), but then assigns equal nondegenerate `p=.95` to all A/B/C classes and treats the six indicators as independent (PREREGISTRATION.md:2286, score_rates.py:1001). Containment plus equal marginals forces each nested pair’s indicators to be equal almost surely, so the independence scenario cannot arise from these endpoints. Consequently `q⁶`, `q¹⁸`, 0.7658 gate power, and 0.7359 row-5 coverage do not describe a possible study population, yet those quantities justify N at PREREGISTRATION.md:2417. Round-9 disposition 9’s printed “independent primary/S1” alternative is similarly impossible because primary HIGH implies S1 HIGH. The new tests reproduce the algebra but never test model coherence (test_verdict_parity.py:971). The joint model and N justification need recomputation under a distribution respecting deterministic containment, or valid dependence bounds.

5. **The C7 outcome interpretation is right, but the implemented gate validates only a truncated marker. Severity: should-fix.** The amended C7 expressly permits `refused`, `matched`, and `no-context`; admitting all three is therefore correct, including reporting `no-context` as undemonstrated (PREREGISTRATION.md:2715). However, batch.py:837 and score_rates.py:2825 require only an object, registered outcome, matching assent, and matching golden digest. They do not validate the writer-produced members, stripped `CALL.json`, deletion evidence, or context presence consistent with outcome (batch.py:2083). The C7 damage tests mirror that smaller schema (test_batch.py:1129); the scorer test merely expects some `ScoreError` while several earlier preconditions are null (test_admission.py:1969). Also, the `no-context` writer says “neither registered outcome occurred,” although `no-context` is itself registered.

6. **The wrapper anchor works for the README procedure, but disposition 6 is still partial. Severity: should-fix.** The exact lexical anchor to this study’s `arms/<ARM>/authoring/run-NNN` is implemented and is naturally part of §2.7 difference 1; the README’s batch command supplies that canonical path. Nevertheless, the wrapper now also adds a new explicit `git rev-parse` failure behavior at authoring_call.sh:88, which is a fourth behavioral difference from Study 011 not among §2.7’s exact three (PREREGISTRATION.md:841).

   In addition, the physical-anchor guard calls `mkdir -p` before resolving the anchor (authoring_call.sh:257). A replaced earlier component can therefore cause missing descendants to be created outside the physical study before refusal, contrary to PORTS.md:155. The new test uses an already-existing target at the final `authoring` component and cannot see that earlier-component write gap (test_batch.py:669).

7. **S10 is registered as a placement measure but implemented as correctly-labelled coverage. Severity: should-fix.** S10 says “Every arm’s records,” “class membership only,” and asks where records land in the baseline coordinate system (PREREGISTRATION.md:1796). The scorer intersects the old-edge predicates only with `high`, excluding Q (score_rates.py:2621). Thus D records placed at 40/70 but labelled according to remembered old thresholds can be invisible to `OLD-EDGE-PREFERENCE`. Add a raw old-edge endpoint for the placement claim, or narrow the registration and outcome language to correctly-labelled old-edge coverage.

8. **S5’s empty-denominator case contradicts the registered iff and can emit a false sentence. Severity: should-fix.** The registration defines “at the ceiling iff `|Q|=0`” (PREREGISTRATION.md:1820). score_rates.py:1206 adds a nonempty-denominator condition and classifies `H=Q=0` as degraded. `reading_verdict()` can then publish “at least one accepted record was mislabelled” when there were none. Register and implement an undefined/no-accepted-records branch, or explicitly define the ceiling as `H+Q>0 and Q=0`.

9. **The one-UTC-calendar-day rule is not operationalized. Severity: should-fix.** The registration requires all 150 slots to begin and finish on one UTC date and makes crossing midnight a deviation (PREREGISTRATION.md:967). No scorer or batch check compares retained timestamps’ UTC dates, and the README run procedure gives no explicit manual check. The scorer should at least publish the observed date set/deviation flag, or the procedure must require and verify the manual review.

10. **The manifest implementation is correct, but §8 and Appendix A still overstate what it binds. Severity: should-fix.** Section 2.10 correctly says `PREREG-REVIEW.md` is excluded and its honesty remains external (PREREGISTRATION.md:1165). Yet §8 says `integrity.py` prevents even “the review record’s own digest table” from changing (PREREGISTRATION.md:3250), and Appendix A credits per-round arm digests with closing co-moving edits (PREREGISTRATION.md:3437). The code excludes that carrier and checks only the last attestation digest (integrity.py:1003, integrity.py:1092). Those two passages should adopt §2.10’s narrower, accurate residual.

11. **The new landmark-straddle test can pass after the family stops straddling the 40 edge. Severity: should-fix.** test_mirror.py:137 combines the mirror verdict and family-class tuple, and accepts a change in either as proof that the family predicates changed. At 40, the mirror alone can supply the difference; the later explicit family assertions omit that edge. Compare family-class columns separately for every named edge. The current committed family does straddle correctly; this is a test-coverage defect.

12. **The prefix-0-through-5 test does not exercise publication despite its name. Severity: nit.** test_admission.py:2153 thoroughly checks `score()`’s in-memory descriptive result and rendered headline, but never invokes `score_registered()` or `_write_outputs()`. It would remain green if incomplete-prefix `RESULTS.json`/`RATES.md`/`CENSUS.md` publication failed. The underlying prefix-scoring disposition itself is implemented.

13. **Several status/control sentences are stale. Severity: nit.** PREREGISTRATION.md:15 says the harness does not yet exist; README.md:12 says eight rounds are recorded although round 9 is present; and C4 says `arm-mismatch` is the only new admission code (PREREGISTRATION.md:2633), whereas §3.3 correctly registers three new codes.

Round-9 dispositions 4, 5, 7, 8, 10, and 12 are fully implemented. The central implementation in 9 is present, but its added alternative is impossible; disposition 11’s artifact/prose correction is right but its named test is weaker than claimed.

Verification results:

- Pinned suite: `253 passed, 6 subtests passed`, 49,268 deprecation warnings, exit 0 in 275.47 seconds.
- Pinned `harness/integrity.py`: exit 0; 11 ported files, five correct threshold pairs, HEADER 948 bytes, all five clean-room mirrors, and expected pre-freeze “tree manifest unbound.”
- Independent artifact assembly, all twenty arm hashes, digit censuses, arm-C enumeration, 280-cell grids, five schedule balances, interval vectors, cuts, and table encodings otherwise matched.
- `CLAIM.md` matches its cited Study-011 source; all five retained C10 attempts, extracted mirrors, prompt equations, and 280-cell agreements match their record.
- My manifest contained 85 sorted entries including the 6,653-byte normalized registry projection. Its digest matches `integrity.tree_manifest()`, whose amended exact-file versus trailing-slash-tree exclusion rule implements the registered recipe.
- Reviewed commit/branch were correct and the worktree remained clean.

Overall verdict: BLOCKING — Study 012 is not freeze-ready; round-9 dispositions 1 and 2 remain materially incomplete, and §5.4’s sample-size rationale uses an impossible joint model.

Reviewed commit: 14725fb

Tree manifest (my computation): 4c677eba037a75bae242c42ceb4d5ed57363ccbefd55d42a99773e4e79f339df

CODEX-012-R10-DONE

### Dispositions

All thirteen findings **ACCEPTED**. Three were verified as only partly right and
are dispositioned on corrected grounds. As in round 9, every finding was
independently re-verified against the bytes at `14725fb` before a disposition
was written — each claim checked, each anchor confirmed or corrected, each
proposed remedy priced. That verification refuted one of the reviewer's
prescriptions outright and sharpened three others, and it found two places where
**round 9's own record overclaimed**. Those are corrected here rather than
quietly narrowed.

**Finding 3 is the round's most serious result, and it is a defect in round 9's
own work.** The fifth [D-10] conjunct was written as a *contrast* — arm A versus
arm E on class 3 — and a contrast does not exist when arm A is not HIGH there.
So the conjunct passes **vacuously** in exactly the case it was added to catch.
Demonstrated end to end with the scorer's own API on the real arms: an arm E
that covered class 3 in **zero** of thirty runs published row 5 CONFIRMED, under
a `why` string asserting "arm E does not read COLLAPSE on class 3". §5.4's own
scenario puts 3.16% of row-5 mass at N = 30 through that door, and no test could
see it because every decision fixture leaves unnamed arms perfect. Round 9's
record stated the exclusion **unconditionally in five places** and named the
vacuity six lines later without ever noticing the two are the same case — a
self-contradicting record, not an incomplete one. The conjunct now reads arm E's
**own level**: `arm E does not read LOW on class 3`. It is uniformly at least as
strong, strictly stronger exactly in the vacuity case, and **moves no published
figure at all** — row 5 stays 0.0364 / 0.3536 / 0.7359 to full double precision,
so `REGISTERED_JOINT_ROW5` and the §5.4 lint stand untouched. The registered
weakness sentence — "a class 3 covered in as few as four of thirty runs
satisfies it" — was already written as an arm-E level; the contrast form was the
implementation slip, and the code now says what the registration always said.
Two further round-9 claims go with it. The uniqueness claim ("the one class
whose members are scored between the two thresholds") is **false** — class 2
nests strictly inside class 3 — and the true reason class 3 is the only
*available* class is that 0, 1, 2 and 5 are the four the prediction says will
collapse and class 4 has no numeric content. And the impossibility argument is
narrowed: correct labels bound the threshold pair to an interval and never to a
point, but the reviewer is right that a **straddle** conjunct is satisfiable by
the arm R1 predicts, so "no conjunct available" was too broad. The straddle is
**conceded as logic and declined as a fix**, with the reason registered: it
needs a straddle *width* this file never registered (a straddle of two or more
evades all four one-wide bands), it has no §5.4 model, and it would make a §5
decision read record-level values §4.5 registers as gating nothing.

**Finding 4 is new, it is mathematical, and its own remedy is refuted by
computation.** Class 0 nests in class 1 and class 2 in class 3 as predicates —
verified over all 280 cells at both threshold pairs — and correctness is a
property of the *record*, so the coverage indicators are ordered pathwise on
both endpoints. Independence across a nested pair is therefore unavailable at
**any** nondegenerate marginals, not merely doubtful: §5.4's layer 1 is
arithmetically impossible. This is the same argument round 9 registered for
layer 4; nobody noticed it also demolishes layer 1. But the reviewer's
prescription — recompute N — is wrong, because **the direction is not uniform**.
Collapsing the nested pairs makes conjunctions *more* likely and tolerances
*less* likely: all-six rises 0.6865 → 0.7782 while the control gate falls
0.7658 → 0.6702 and row 5 falls 0.7359 → 0.6253 at N = 30. So the quantities
that carry N move the unfavourable way — and **N = 30 still stands on its own
registered criterion**, "a dependency that usually fails is not a control":
0.6702 against N = 25's 0.4010, with the half-way line still between them. §5.4
now registers the containment as a named impossibility, corrects its direction
sentence (which asserted the opposite and is false for the gate), sharpens the
Fréchet floor to max(0, 4q − 3) and caps the top at min q, names the cells that
fall below their floors, publishes the containment-respecting figures beside the
independence ones rather than replacing them, and retains N = 30 on arithmetic
that can actually occur. The independence figures stay published, now labelled
as the incoherent approximation they are. Three things the verification found
that the reviewer did not: the infeasibility is worse in the p = 0.98 row
(three cells, not two); the tolerance direction **reverses at N = 20**, where
five-of-six is effectively a conjunction; and §2.1's DRIFT-SUSPECTED
false-positive rate moves twenty-fold, 0.0002 → 0.0041, because the rule counts
classes and one group now carries two. All three are registered rather than
smoothed. The nesting itself — asserted in §2.3 and checked nowhere for ten
rounds — is now a computed fact over the grid.

**Finding 1 is downgraded to should-fix, and the closure round 9 declined is
taken anyway.** BLOCKING is not warranted: round 9 recorded this residual and
declined its closure *by name*, the reviewer neither quotes nor rebuts that
decline, and a second tree-wide untracked-source refusal runs inside every
ceremony command's preflight. But the finding names a mechanism sharper than
what was conceded — the tripwire's own `subprocess` is resolvable from the very
directory the tripwire exists to police — and declining twice in the same words
would be the wrong answer to a reviewer who found a better argument. The
ceremony now runs under `PYTHONSAFEPATH=1` and every path-invoked entry file
refuses without it. The `ImportFrom` hole in round 9's own ordering test is
closed too: it was an emptiness assertion a `from policy_mirror import …` would
have satisfied silently, and it is now live — verified by planting one.

**Findings 2 and 8 are both consequences of round 9's own weakening, which is
the honest thing to record about them.** Round 9 replaced a vague reading cell
with a concrete one, and concreteness made two falsehoods visible. "None was
placed at the boundary" is false under a LOW verdict, which permits the class to
be reached up to three times in thirty; the cell now says what LOW means —
**LOW bounds placement, it does not zero it** — reusing §5.1's own registered
gloss so no new number enters the file. And "at least one accepted record was
mislabelled" would be published for an arm with **no accepted records at all**,
because the code adds a non-empty-denominator condition the registered `iff`
never had. The ceiling is now registered as the conjunction the code implements
— at least one accepted record, and `|Q| = 0` — in §4.6's own S2 idiom, and the
row-2 cell is true in both of its sub-cases. No decision-table row moves either
way, which is stated so the disposition is not read as fixing a verdict bug.

**Findings 5, 6, 7, 9, 10, 11, 12 and 13, each on the narrower ground the
verification established.** The C7 gate keeps all three registered outcomes and
gains only the shape checks that cannot make it brittle; what was genuinely
wrong is that its scorer-side test refused on a missing golden file and never
reached its own subject while two places cited it as that gate's coverage —
proved by deleting the gate and watching the old test still pass. The wrapper's
`mkdir -p` followed a replaced component and could create directories **outside**
the physical study before refusing, under a comment asserting it created
nothing outside; it now descends component by component, resolving before
creating, and the sentence is true. The round-9 `GIT_ROOT` repair is
**registered rather than reverted** — a defensive refusal that fires only when
the study is not in a worktree is outside §2.7's subject matter, which
enumerates arguments, stamps and naming — and the diff against Study 011's
wrapper is recorded so round 11 need not re-derive it. S10 is registered as
placement and was implemented as correctly-labelled coverage, losing sensitivity
in **both** directions at once and making the outcome depend on an unregistered
nuisance variable; it is now raw, as §4.6 always said, and a record placed at an
old edge but labelled by the old thresholds is visible to it for the first time.
The one-UTC-day rule is asserted in [D-10]'s confirmation sentence, §9's bounds
and `RESULTS.json`'s own cell note, and nothing computed it; the observed date
set and a crossing flag are now published per batch, and **nothing refuses** —
§2.8 registers a midnight crossing as a recorded deviation, not a stop. §8,
Appendix A and this file's own header asserted that the manifest binds the
review record, which round 5 refuted; all three now quote §2.10's accurate
residual. Round 9's straddle test folded the mirror verdict into the class
column, so at two of its five edges the verdict alone supplied the difference
and the class fact was vacuous — split, and verified to fail on a family that
stops straddling. The prefix test now exercises all three published bodies.
§2's "the harness does not exist yet" is re-tensed before it can be frozen into
a file that is never edited after the freeze, and C4 stops contradicting §3.3's
three admission codes.

**What this round did not do.** `verify_mirror2()` still has no direct unit
test; `verify_tree()` and `normalized_pins()` remain uncovered; `_write_outputs()`
is pinned only at its override gate. One residual is named rather than closed:
§5.3 (ii) row 3's gloss is still false for an arm D that placed correctly at its
own pair and mislabelled, because the new-keyed side of rows 2 and 3 reads the
labelled primary — whether it should read S1 placement is a separate registered
question, named here so round 11 does not rediscover it rather than inherit it.

Verification after the dispositions: `harness/integrity.py` exit 0 (tree
manifest unbound, pre-freeze); the pinned suite **271 passed** (253 at the
reviewed commit, plus 18 added by these dispositions), run the way README step 0
now specifies; tracked status clean; `arms/`, `analysis/` and `CLAIM.md`
untouched by every disposition above. The post-disposition tree manifest, the
maintainer's computation, is
`f000000d67ac9fd2ce080834276160305a2c10f55827c464a31f4ad04a17470a` — round 11
attests it independently, and under §2.10 rule 3 that round is required, because
these dispositions changed bytes.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above — no
disposition in this round touches a file under `arms/`:

| arm | bytes | sha256 of the arm text as reviewed in round 10 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 11 — the eighth post-disposition review

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-09; drafting as recorded in rounds 1-10
- Reviewed commit: `60afba4`
- Tree manifest, the reviewer's computation:
  `f000000d67ac9fd2ce080834276160305a2c10f55827c464a31f4ad04a17470a` — 85
  entries, matching the maintainer's own computation recorded in round 10's
  dispositions
- Runs: one review run, completed; no run discarded, and no classifier refusal
  anywhere in the transcript. Run as rounds 9 and 10 were, with the same
  deviation recorded in round 9
- Reviewer's verification first: integrity exit 0; 271 passed in 328.93s;
  worktree clean. **Round 10's dispositions 1, 3, 5, 6, 7, 8, 11, 12 and 13
  fully implemented**; 2, 4, 9 and 10 partial as its findings describe.
  **Both of round 10's flagged calls were validated in the reviewer's own
  words**: the class-3 conjunct is "nowhere weaker and strictly stronger
  exactly in the old vacuity case"; declining the straddle rule is
  "defensible"; retaining N = 30 is "justified" and publishing both arithmetic
  layers is "honest". Independent reconstruction reproduced all five Appendix
  policies byte for byte, the 948-byte HEADER, all five prompt equations, all
  twenty arm hashes, the 280-cell grids with class counts (4, 12, 6, 20, 28, 4)
  and containments exactly (0, 1) and (2, 3), the five schedule balances,
  §3.3's partition, the interval vectors, the decision-table encodings,
  `CLAIM.md` against its Study 011 source, and all five retained C10 attempts.
  The four coverage gaps round 10 left open on purpose were confirmed
  accurately recorded

### Prompt (verbatim)

```
You are performing a verification review — round 11 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 60afba4 on branch study-012-perturbation

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony now runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Verify round 10's thirteen dispositions.** `PREREG-REVIEW.md`'s round-10 section lists thirteen findings and, beneath them, the maintainer's dispositions. For each: is the disposition genuinely implemented in the bytes at this commit? Report any that is partial, mis-implemented, or implemented only in prose.

Round 10's two hardest findings were answered in ways the maintainer flags for your judgment:

- **Finding 3, the fifth [D-10] conjunct.** It was a contrast (arm A against arm E on class 3) that passed vacuously whenever arm A was not HIGH there; it now reads arm E's own level — `arm E does not read LOW on class 3`. The registered claims that went with it were narrowed: the "one class scored between the thresholds" uniqueness claim was withdrawn (class 2 nests inside class 3), and the impossibility argument was narrowed after conceding that a **straddle** conjunct is satisfiable by the arm R1 predicts. The straddle was declined as a fix, on the ground that it would need a registered straddle *width*, has no §5.4 model, and would make a §5 decision read record-level values §4.5 registers as gating nothing. **Judge the new conjunct** — does it close the vacuity completely, is it really no weaker anywhere, and is the decline of the straddle sound or is it declining the better rule?
- **Finding 4, the joint model.** Layer 1's independence is now registered as arithmetically unavailable across the two nested class pairs, the direction sentence is corrected (conjunctions rise, tolerances fall), the Fréchet floor is sharpened, and the containment-respecting figures are published beside the independence ones rather than replacing them — with **N = 30 retained** on the corrected arithmetic (gate 0.6702 against N = 25's 0.4010). **Judge that retention**: is the corrected arithmetic right, is publishing both sets the honest choice or does it leave a reader unable to tell which governs, and does any remaining figure in the tree still stand on the incoherent model without saying so?

**2. The registered content — a fresh sweep.** Rounds 9 and 10 both found their sharpest results in the study rather than the harness. Keep that priority.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it. Round 10's dispositions edited §2.1, §2.2, §2.3, §2.7, §2.8, §4.6, §4.7, §5.3, §5.4, §5.5, §6 C4, §7, §8, §10 and Appendix A — read the amended sections against what they now govern, and read the untouched ones as if for the first time.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two of these independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**3. The suite, at 271, and what it does not reach.** Rounds 9 and 10 grew it from 208 to 271. The maintainer's round-10 record names four gaps left open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are uncovered; `_write_outputs()` is pinned only at its override gate; and §5.3 (ii) row 3's gloss is recorded as still false for an arm D that placed correctly and mislabelled. Confirm each is as described — and then ask what **else** the suite asserts less than it appears to. A test that passes for a reason unrelated to its subject is this round's standing target: round 10 found one such test cited in two places as a gate's coverage.

**4. Run the suite and the verification command**, and report both results.

**5. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line;
- the line `Reviewed commit: 60afba4`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R11-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The reviewer's own `## Findings` heading is demoted to keep this record's
section structure; no other byte of the message is altered, and the absolute
paths its markdown links carried are rendered as the `file:line` anchors they
point at.)

#### Findings

1. **Blocking — class 4 retains the baseline-vacuity defect repaired for class 3.** The registration says confirmation requires an intact/non-collapsing class 4 and that class-4 collapse overrides every other reading (PREREGISTRATION.md:2114, PREREGISTRATION.md:2324). The scorer checks only the A-vs-E contrast (score_rates.py:4338). If A is not HIGH on class 4, E may be LOW while the contrast is INDETERMINATE; B and C can TRACK the other five classes, and E can still reach CONFIRMED. Existing tests leave A perfect in their class-4-collapse case (test_admission.py:989). The minimal complete rule is analogous to the class-3 repair: fire row 2 when E itself is LOW on class 4, making row 5 require E not LOW there.

2. **Should-fix — the “coherent” containment model still violates containment in row 5.** The registration and function call the companion one coherent model (PREREGISTRATION.md:2550, score_rates.py:1208). The code nevertheless multiplies E’s class-3-not-LOW factor independently of the `nP` calculation containing E class-2 LOW (score_rates.py:1253, score_rates.py:1280). Because class 2 nests in class 3, `K₂≤K₃` pathwise and `{K₃ LOW}⊂{K₂ LOW}`. A complete computation must jointly enumerate or condition those ordered counts. The discrepancy is below printed precision, so 0.6253, the 0.6702 gate, and N=30 remain numerically unchanged.

3. **Should-fix — the registered placement-to-primary implication is false, and its test passes for an unrelated reason.** The record and scorer docstring claim PLACEMENT-COLLAPSE implies primary COLLAPSE because `H⊆raw` (PREREGISTRATION.md:2057, score_rates.py:1499). A raw-HIGH baseline can have non-HIGH primary coverage through mislabelling, making the placement contrast collapse while the primary contrast is INDETERMINATE. The scorer correctly computes `nP` and `nC` independently. The purported test of `nP≤nC` always makes A PERFECT, so it passes because its fixture supplies the missing premise (test_admission.py:1276).

4. **Should-fix — round-10 finding 2 remains partially implemented.** The false “no placement” LOW gloss is repaired, but the LOW-plus-degraded case is still categorically published as “comprehension collapse — published as one” (PREREGISTRATION.md:1892, score_rates.py:689). This conflicts with the nearby disclaimer that the name is merely an available explanation, not an established proposition. Tests explicitly pin the categorical label (test_verdict_parity.py:389).

5. **Should-fix — LABEL-COLLAPSE-ONLY overstates mixed cases.** The record and scorer publish “the records are still at the boundary; the labels are not” for `nC≥3, nP<3` (PREREGISTRATION.md:2328, score_rates.py:622). But `nP<3` permits one or two genuine placement collapses. It proves label failure contributed to at least one primary collapse, not that placement remained intact generally. Tests cover only `nP=0,nC=4`.

6. **Should-fix — the UTC-day disposition incorrectly establishes the property for incomplete prefixes.** The registration requires all 150 slots to have readable start/end dates before one day is established (PREREGISTRATION.md:1006). `utc_day(rows)` only checks the rows supplied and never checks completeness or 150 slots (score_rates.py:1799). The test publishes five slots and asserts `oneDayEstablished=True` (test_batch.py:2299). `_epoch()` also validates punctuation but not calendar/time ranges. This is descriptive and non-gating.

7. **Should-fix — C7’s narrowed shape gate still establishes less than its error and control prose imply.** C7 says retention is by code: stripped CALL, outcome-consistent context, and digest/delete evidence (PREREGISTRATION.md:2998). The shared checker validates only exact `registeredOutcomes`, an arbitrary string-to-string deletion map, and a non-boolean integer exit status (score_rates.py:3149). Thus many records the writer could not produce pass despite the error saying otherwise. A complete shape check would require the canonical CALL/VERDICT members, deletion-name whitelist and digest grammar, and outcome-consistent context evidence. It still could not establish provenance, which is openly impossible because the control directory is freeze-excluded.

8. **Should-fix — the disclosed arm-D row-3 gloss is indeed false.** The record says new-keyed LOW plus old-keyed LOW means records were placed at neither threshold pair (PREREGISTRATION.md:2243). The new-keyed side reads labelled primary coverage, while old-keyed S10 is raw placement (score_rates.py:773). Correct new-edge placement with wrong labels can therefore receive “placed at neither pair.” Existing fixtures set both new-keyed H and raw coverage to zero and miss the divergence.

9. **Should-fix — every arm’s actual stimulus contains stale process assertions.** Each policy tells the author that every other study artifact is checked against that policy, that divergence from a pack is a pack bug, and that this is everything “the two sides” share (arms/A/POLICY.md:3). Study 012 intentionally has five policy texts, evaluates no pack, and expressly says D’s pack-side check is unavailable (PREREGISTRATION.md:2866). The prose is common across arms, so it is not a differential confound, but it is false inherited text inside the registered prompts.

10. **Should-fix — round-10 manifest wording remains partially stale.** Appendix A first correctly says no code reads the per-round review digests, then says those digests “are what `integrity.py` binds the frozen artifacts to” (PREREGISTRATION.md:3819). Integrity binds PINS and the tree manifest, not the review table.

11. **Nit — two control tests claim stronger assertions than they make.** The “byte-exact” C2 comparison says it distinguishes dictionary member order, but uses `sort_keys=True`, which erases order (test_controls.py:133). Its index-contiguity assertion would accept JSON `false` as zero (test_controls.py:151); runtime integrity correctly adds an exact-int check, so the live control is sound.

Round-10 disposition status: 1, 3, 5 as expressly narrowed, 6, 7, 8, 11, 12 as expressly narrowed, and 13 are fully implemented. Dispositions 2, 4, 9, and 10 are partial as described above.

The new class-3 [D-10] conjunct is sound: old pass was `(A≠HIGH) or (E≠LOW)`; new pass is `E≠LOW`. It is nowhere weaker and is strictly stronger exactly in the old vacuity case. Declining a straddle rule is defensible: it would support a stronger threshold-sensitivity claim, but is not a drop-in repair for the registered placement claim and would require a width, operating-characteristic model, and promotion of descriptive record values into the gate.

The corrected containment gate is 0.4010 at N=25 and 0.6702 at N=30, so retaining N=30 is justified. Publishing both arithmetic layers is honest: the independence layer is explicitly labelled unavailable and the containment layer is identified as governing N. Finding 2 is the sole remaining figure advertised as coherent that is not fully so.

Independent reconstruction reproduced all five Appendix policies byte-for-byte, the 948-byte HEADER and all five prompt equations, and all 20 arm hashes. The 280-cell grids reproduce counts `(4,12,6,20,28,4)` and exactly containments `(0,1)` and `(2,3)`. The five schedule balances, §3.3 partition, interval vectors, and decision-table encodings match. `CLAIM.md` matches Study 011’s cited source; all five retained C10 attempts, prompts, extracted modules, and agreement records match.

The deliberately open coverage gaps are accurately recorded: `verify_mirror2()` has only indirect happy-path execution; `verify_tree()` and `normalized_pins()` lack direct tests; `_write_outputs()` is reached only at its override refusal; and the arm-D gloss is finding 8.

Verification results:

- Suite: `271 passed, 53360 warnings, 9 subtests passed in 328.93s (0:05:28)`.
- Integrity ceremony: exit 0; 11 ported files, correct five threshold pairs, 948-byte HEADER, five agreeing clean-room mirrors, expected pre-freeze unbound manifest.
- Independent manifest: 85 entries, including the 6,653-byte normalized PINS projection. `integrity.tree_manifest()` implements the same exclusions, normalization, sorting, trailing newline, and hashing recipe.
- Commit and branch matched; worktree remained clean.

Overall verdict: BLOCKING — not freeze-ready because CONFIRMED can bypass a LOW class-4 nonnumeric control when A’s class-4 baseline is unresolved.

Reviewed commit: 60afba4

Tree manifest (my computation): f000000d67ac9fd2ce080834276160305a2c10f55827c464a31f4ad04a17470a

CODEX-012-R11-DONE

### Dispositions

All eleven findings **ACCEPTED**, two of them on corrected grounds and one at a
**lower** severity than filed. As in rounds 9 and 10, every finding was
independently re-verified against the bytes at `60afba4` before a disposition
was written. That verification confirmed the blocking finding and priced it
higher than the reviewer did, refuted two of the three charges inside finding 7,
and corrected the prescribed remedy for findings 1 and 9 — in both cases toward
a *narrower* claim than the reviewer proposed.

**Finding 1 is the round's blocker, and it is the same defect class round 10
repaired one class over. I fixed the instance and left the class.** Round 10's
finding 3 was that the class-3 conjunct was written as a *contrast* — arm A
against arm E — and so passed vacuously whenever arm A was not HIGH there.
Class 4's gate has exactly that shape and exactly that hole. Demonstrated on
the real arms at their pinned digests, in the realistic form rather than a
corner: arm A at **26 of 30** on class 4 — one short of the HIGH cut, `L =
0.6928` — and arm E at **3 of 30**, the LOW cut exactly, published **row 5
CONFIRMED**. Under §5.4's own scenario that door carries 3.16% of row-5 mass at
N = 30, digit for digit the figure round 10 quoted for class 3, because it is
the same shape.

Three things make this worse than a repeat, and the disposition records each.
**It is symmetric across the R1 verdict**: row 2 gates row 4 as well as row 5,
so R1-UNSUPPORTED was equally exposed — which is why the fix is at **row 2** and
not, as the reviewer's own last sentence proposes, a sixth [D-10] conjunct on
row 5. A row-5-only fix would protect CONFIRMED and not its falsifier, which is
precisely the asymmetry §5.3 registers as the mark of "a study with a preferred
answer", and it would publish INDETERMINATE where §5.3 (iv) registers an
override. **The record's fault is a different one from round 10's, and blurring
them would be the easy mistake**: class 3 was an implementation slip *against*
its registration, whose weakness sentence was already written on arm E's own
level; class 4's code matched its registration exactly, because every registered
statement of it uses §5.2's defined term "collapse". Here the **registration**
was wrong — together with the §4.6 gloss "CONFIRMED therefore means … an intact
class 4", which is false of the arm the demonstration confirms and is
machine-pinned as `CEILING_LIMIT`. And **round 10 wrote the class-4 vacuity into
§5.4 as a known property in the same commit that repaired class 3** ("drops out
of the pattern in which arm A is not HIGH on class 4"), which makes the round-10
record self-contradicting rather than merely incomplete.

Row 2 now fires on arm E's own level, with arm A's level named in the published
`why` so a reader can see whether the attribution is established — the level
form is uniformly at least as strong for the job that *gates* (a refusal to
adjudicate R1 in either direction, which is a statement about arm E alone) and
honest about the job that only *diagnoses*. Free at every pinned precision:
rows 4 and 5 move by less than 1e-24 at every N and the gate carries no class-4
term at all, so `REGISTERED_JOINT_ROW4` at seven significant figures, all five
`REGISTERED_CONTAINMENT` pins and the 1e-12 identity all stand.

**The class is now closed, and that is the part worth recording.** A sweep of
the whole decision path found row 2 was the last permissive contrast. Rows 3, 5
and 6 read contrasts in the **conservative** direction — an unresolved baseline
can only refuse a verdict, never manufacture one — row 4 and the §4.6 branch are
already levels, and arm D was closed in round 4. One form-mismatch remains and
is **registered rather than repaired**: §4.6's table keys its rows on the S1
placement level while the scorer keys them on `nP`/`nC`, which are contrasts —
conservative in the same way, and named here in both the registration and
`reading_verdict()`'s docstring so round 12 does not re-find it as a defect.

**Finding 2 lands on the exact word round 10's disposition was sold with.** The
"coherent" containment companion left layer-1 independence standing between arm
E's class 2 and class 3 — the same nested pair, in the same arm, that round 10's
own argument condemns. Narrowing the word would have cost the same manifest
cascade as fixing the arithmetic, because the overclaim lives in a docstring in
the same file, so there was no cheap way out and no reason to take one.
Containment fixes the pair's two-by-two table from its marginals alone, so
computing the joint properly **adds** no assumption and **removes** one the
registration forbids. The two exact rationals collapse to the same IEEE double
at all three N; the fix was verified three ways, including a brute-force
enumeration over the coupled table.

**Findings 3, 5 and 6 are each a claim that outran its own arithmetic, and two
of the three are mine.** `nP ≤ nC` is not an invariant: a raw-HIGH baseline can
have non-HIGH primary coverage through mislabelling, and the test that
"asserted" it passed only because its fixture made arm A perfect and supplied
the missing premise. The true conditional is registered instead, and the
corrected test now goes red on one of eight batches under the old assertion.
`LABEL-COLLAPSE-ONLY` published "the records are still at the boundary" when
`nP < 3` permits one or two genuine placement collapses — the same correction
round 10 made one row up, which that round's sweep had scoped to the row-1 cells
rather than the table. And `oneDayEstablished` could be established on a partial
prefix, though the registration requires all 150 slots; the flag now reads the
population's completeness. The §2.8 edit is a **sharpening**, not a reversal:
"established only when" is a necessary condition, so adding another never
contradicted the registered sentence. `_epoch`'s calendar-range looseness is
named and deferred, with its three reasons, rather than fixed in the same
breath.

**Finding 7 is ACCEPTED at nit, below the severity filed, because two of its
three charges are refuted by the bytes.** §6 C7's sentence is accurate and
already narrower than the code, and both error strings are true on the only path
that emits them; `PORTS.md` had pre-conceded the incompleteness point in round
10. What survives is one **false sentence in a docstring** — the three checked
members were called the ones "written unconditionally on every path", when the
writer writes all eleven on every path, so presence discriminates nothing. That
sentence is corrected and a direction clause added; the gate, the messages and
the registration are untouched. Downgrading a reviewer's severity is recorded
here rather than quietly applied.

**Finding 8 was disclosed in round 10's record so it would not be rediscovered;
round 11 confirmed it, so it is decided now.** The arm-D row-3 gloss claimed
records were placed at neither threshold pair when the new-keyed side reads
labelled coverage and the old-keyed side reads raw placement. Of the two
remedies the narrower one is taken — the gloss is corrected to what the mixed
keying supports — and the wider one is **declined with its reason**: making rows
2 and 3 read S1 placement would contradict §5.3 (ii)'s registered asymmetry,
give "new-keyed" two referents inside one four-row table, and change which
populations receive which registered outcome, which is a post-hoc design change
on a table that adjudicates nothing.

**Finding 9 is the one that could not be fixed at all, only registered — and the
prescribed remedy was wrong.** Every arm's `POLICY.md` preamble tells the record
author that other artifacts are checked against the policy and that a divergence
from a pack is a pack bug. Neither is true of this study, and this prose is **in
the stimulus**, seen in all 150 calls. Editing it is spec-unlawful three ways:
§2.2 and `PORTS.md` register arm A's derivation from Study 010's locked bytes as
exactly two deltas and nothing else; C8 clause 4 checks the preamble across arms
both ways; and all five C10 commission prompts inline it, so §7 would require
re-commissioning every clean-room mirror. So it is registered — but **not as
"inert"**, which is what the parallel with round 9's `FAMILY.json` members would
have suggested and what the round-9 idiom made tempting. Those members are inert
because nothing reads them and nobody sees them; this prose is read by C8 *and*
by the author in every call the study scores. Calling it inert would be a fresh
overclaim of exactly the kind rounds 10 and 11 have been punishing. It is
registered as **inherited and non-differential**: byte-identical in all five arms
and pinned, so it enters no contrast and can confound none — with the
external-validity cost stated in §9 rather than argued away.

**Findings 4, 10 and 11 as verified.** The "comprehension collapse" outcome
keeps its registered name — renaming it would put ten rounds of review prose out
of step with the file they describe — but its travelling gloss now carries the
disclaimer that had been living only in the registration, which matters because
round 10's own empty-arm sub-case made the row fire on an arm with zero accepted
records. Appendix A contradicted itself two sentences apart about what
`integrity.py` binds; my round-10 fix was incomplete inside the same passage,
and the re-sweep confirms the remaining sites are historical records that
"Nothing is discarded" forbids rewriting. And two control tests claimed more
than they asserted: `sort_keys=True` erases the member order one docstring
claimed to distinguish — the **docstring** was the overclaim, since §6 C2
registers the control as running unchanged and Study 011 sorts too, so
tightening the comparison would have silently strengthened a registered control
— and the index-contiguity assertion would have accepted JSON `false` as zero,
round 8's house rule reaching a test instead of production code. All three sites
of that second hole are closed.

Verification after the dispositions: `harness/integrity.py` exit 0 (tree
manifest unbound, pre-freeze); the pinned suite **283 passed**, run twice
independently and green both times, the way README step 0 now specifies; tracked
status clean; `arms/`, `analysis/` and `CLAIM.md` untouched by every disposition
above. One anomaly is recorded rather than dropped: a single run made while
heavy concurrent work was in flight reported one failure in
`test_no_retained_byte_and_no_leftover_carries_the_credential`; that test then
passed six consecutive times in isolation and in both clean full runs, so it is
recorded as load-sensitivity observed once and not reproduced, not as a green
suite. The post-disposition tree manifest, the maintainer's computation, is
`5ea1deb972d3eb0e9b430501f97e9bcbda6af54eef9aedd7e349dd7e752ccc25` — round 12
attests it independently, and under §2.10 rule 3 that round is required, because
these dispositions changed bytes.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above — no
disposition in this round touches a file under `arms/`, and finding 9 is
registered rather than corrected precisely because it could not:

| arm | bytes | sha256 of the arm text as reviewed in round 11 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 12 — the ninth post-disposition review, and the first with no blocking finding

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-09; drafting as recorded in rounds 1-11
- Reviewed commit: `ac93d12`
- Tree manifest, the reviewer's computation:
  `5ea1deb972d3eb0e9b430501f97e9bcbda6af54eef9aedd7e349dd7e752ccc25` — 85
  entries, matching the maintainer's own computation recorded in round 11's
  dispositions
- Runs: one review run, completed; no run discarded, no classifier refusal
- **Verdict: SHOULD-FIX. No blocking finding — the first round without one.**
  Two should-fix, seven nits
- Reviewer's verification first: integrity exit 0; 283 passed in 336.06s;
  worktree clean. **All five judgment calls round 11 flagged were validated in
  the reviewer's own words**: the class-4 defect class "is closed for R1
  adjudication ... no remaining contrast can manufacture CONFIRMED or
  R1-UNSUPPORTED"; the §4.6 level/contrast mismatch is "honestly registered and
  conservative - it can withhold confirmation, not create it"; round 11's
  finding-7 downgrade is "justified"; finding 9's inherited/non-differential
  register and its §9 limitation are "adequate"; the containment coupling is
  "correct and no other containment-ordered indicators remain independently
  multiplied"; and declining finding 8's wider rewrite is "defensible".
  Independent reconstruction matched all five policies, the 948-byte header,
  all twenty artifact hashes, the 280-cell vectors with counts (4, 12, 6, 20,
  28, 4) and containments (0, 1) and (2, 3), all schedule balances, the
  partition, the interval vectors and the scorer tables; C1-C10 live;
  `CLAIM.md` matches Study 011; all five retained mirror attempts agree
  280/280; the five named coverage residuals are accurately described

### Prompt (verbatim)

```
You are performing a verification review — round 12 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: ac93d12 on branch study-012-perturbation

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Verify round 11's eleven dispositions.** `PREREG-REVIEW.md`'s round-11 section lists eleven findings and, beneath them, the maintainer's dispositions. For each: is the disposition genuinely implemented in the bytes at this commit? Report any that is partial, mis-implemented, or implemented only in prose.

Five of those dispositions took a position the maintainer flags for your judgment. Each is a place where the maintainer chose something *other* than what the round-11 reviewer proposed:

- **The blocker, and the claim that its defect class is now closed.** Round 11 found that class 4's gate was a contrast between arm A and arm E, so it passed vacuously whenever arm A was not HIGH there. The repair puts the condition on arm E's own level, and it was made at **row 2** rather than as a sixth [D-10] conjunct on row 5 — because row 2 gates R1-UNSUPPORTED as well as CONFIRMED, and a row-5-only fix would protect one verdict and not its falsifier. The disposition further claims the whole defect class is now closed: that every remaining contrast in the decision path reads in the **conservative** direction, where an unresolved baseline can only refuse a verdict and never manufacture one. **Test that claim independently.** Is row 2 the right place? Is any remaining contrast permissive? One form-mismatch is deliberately registered rather than repaired (§4.6's table keys on the S1 placement level while the scorer keys on `nP`/`nC`) — judge whether "conservative and known" is an honest register for it or whether it is a defect wearing a label.
- **Finding 7, accepted at a *lower* severity than filed.** The maintainer downgraded it to a nit on the ground that two of its three charges are refuted by the bytes. Judge the downgrade: are §6 C7's sentence and the two error strings in fact accurate, and was the one surviving docstring sentence the whole of the defect?
- **Finding 9, registered rather than corrected — and deliberately *not* as "inert".** Every arm's `POLICY.md` preamble asserts process facts that are not true of this study, inside the stimulus the record author sees in all 150 calls. The arm bytes cannot be edited. The maintainer registered the prose as **inherited and non-differential** and explicitly declined the word "inert" (which round 9 used for `FAMILY.json`'s legacy members) on the ground that this prose *is* read — by C8 and by the author. Judge that register, and judge whether §9's external-validity statement says enough about what its presence costs.
- **Finding 8's wider remedy, declined.** The arm-D row-3 gloss was corrected rather than making rows 2 and 3 read S1 placement. Judge the decline.
- **Finding 2, computed rather than narrowed.** The containment companion's row-5 term now couples arm E's class-2 and class-3 LOW indicators instead of multiplying them. Judge whether the coupling is the one containment forces, and whether anything else in either operating-characteristic function still multiplies indicators the registration orders.

**2. The registered content — a fresh sweep.** Rounds 9, 10 and 11 all found their sharpest results in the study rather than the harness. Keep that priority.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it. Round 11's dispositions edited §2.6, §2.8, §4.6, §5.2, §5.3, §5.4, §5.5, §9, §10 and Appendix A — read the amended sections against what they now govern, and read the untouched ones as if for the first time.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**3. The suite, at 283, and the residuals the record names.** Rounds 9 through 11 grew it from 208 to 283. The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are uncovered; `_write_outputs()` is pinned only at its override gate; `_epoch()` validates punctuation but not calendar ranges; and the §4.6-reading form-mismatch above. Confirm each is as described — and then ask what **else** the suite asserts less than it appears to. A test that passes for a reason unrelated to its subject is this round's standing target: round 10 found one cited in two places as a gate's coverage, and round 11 found one whose fixture supplied its own premise.

**4. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**5. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line;
- the line `Reviewed commit: ac93d12`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R12-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The absolute paths the reviewer's markdown links carried are rendered as the
`file:line` anchors they point at; no other byte of the message is altered.)

1. **Should-fix — row 2 publishes an attribution the registration says is unavailable.** Record: PREREGISTRATION.md:2362 says E’s LOW level always warrants withdrawal, but when A is below HIGH it does not establish that denaming caused general degradation. Code: score_rates.py:601 and the table at PREREGISTRATION.md:2399 still publish `E-DEGRADED-GENERALLY — the denamed text degraded authoring generally` unconditionally. decision_row():4554 correctly gates on E and merely adds A’s level to `why`; that does not retract the rendered diagnosis. The row-2 placement is otherwise correct and protects both decisive R1 outcomes. **Severity: should-fix.**

2. **Should-fix — arm D row 3 still equates LOW with zero.** Record: PREREGISTRATION.md:2295 calls the row “no correctly-labelled coverage” at D’s pair and “no placement” at A’s pair, although §5.1:2033 defines LOW as 0–3 hits and the row constrains only three of four classes. Code: score_rates.py:817 publishes the same zero-overclaim. Tests at test_admission.py:1510 use zero/extreme populations and miss 1–3-hit cases. Declining the wider S1-based rewrite is defensible; the gloss should instead state the registered LOW bounds. **Severity: should-fix.**

3. **Nit — the joint row-4 parity test permits the registered row to disappear.** Record: §5.4 now definitively carries row 4 at PREREGISTRATION.md:2653. Test: test_verdict_parity.py:968 still says the row is transitional, asserts `len(joint_rows) <= 1`, and loops over it; deletion therefore passes vacuously. It should require exactly one row. **Severity: nit.**

4. **Nit — the schedule tests do not actually bind the registration text.** Record: PREREGISTRATION.md:989 registers the sequence blocks and five derived properties. Tests: test_schedule.py:21 manually transcribes those constants, and test_schedule.py:160 compares the driver only with that transcription. Current values match, but registration-only drift would remain green. **Severity: nit.**

5. **Nit — one registered interface sentence still says the scorer takes a batch root.** Record: PREREGISTRATION.md:1141 says the command takes the batch root. Code and the later authoritative surface derive it internally and accept no such argument: PREREGISTRATION.md:1301, score_rates.py:4593. **Severity: nit.**

6. **Nit — §5.1 undercounts its level endpoints.** Record: PREREGISTRATION.md:2028 says every level verdict names one of three endpoints. Code correctly has four, including `oldEdge`, at score_rates.py:536; §4’s own verdict census also counts it. **Severity: nit.**

7. **Nit — the prose definition of Q is narrower than its equation and implementation.** Record: PREREGISTRATION.md:1578 correctly defines `Q=A\H` but glosses it as wrong-labelled records “reaching a class.” Code: score_rates.py:2075 puts every accepted label mismatch in Q, including records matching none of the six classes. **Severity: nit.**

8. **Nit — the class-4 explanatory witness omits a necessary premise.** Record: PREREGISTRATION.md:1922 and score_rates.py:4462 say an all-sanctions-or-embargo population keeps class 4 clear of LOW. Artifact/code: class 4 specifically requires a non-sanctioned SY vendor; sanctions, KP, and IR records do not cover it. The intended witness needs enough non-sanctioned SY records. **Severity: nit.**

9. **Nit — README’s review count is stale.** README.md:12 says ten rounds and rounds 2–10 cross-vendor, while PREREG-REVIEW.md:1938 contains the completed round-11 review and dispositions. **Severity: nit.**

Round-11 disposition audit: F1’s executable gate repair is complete but its published gloss is partial (finding 1); F8’s narrower repair is partial (finding 2). F2–F7 and F10–F11 are fully implemented; F7’s downgrade is justified. F9’s inherited/non-differential register and §9 external-validity limitation are adequate. The containment coupling is correct and no other containment-ordered indicators remain independently multiplied.

The class-4 defect class is closed for R1 adjudication: row 2 is correctly placed before both decisive outcomes, and no remaining contrast can manufacture CONFIRMED or R1-UNSUPPORTED. The §4.6 level/contrast mismatch is honestly registered and conservative—it can withhold confirmation, not create it.

Independent reconstruction matched all five policies, the 948-byte header, all 20 artifact hashes, the 280-cell vectors with counts `(4,12,6,20,28,4)` and containments `(0,1)` and `(2,3)`, all schedule balances, the partition, interval vectors, and scorer tables. `CLAIM.md` matches Study 011; all five retained mirror attempts match their records and agree 280/280. C1–C10 are live. The five named coverage residuals are accurately described.

Suite: `283 passed, 53360 warnings, 9 subtests passed in 336.06s`; exit 0. Integrity ceremony: exit 0 with the expected pre-freeze unbound manifest. Worktree remained clean. My 85-entry manifest used the registered 6,653-byte normalized PINS projection, and `integrity.tree_manifest()` implements the same recipe.

Overall verdict: SHOULD-FIX — no blocking finding; the R1 gate is sound, but two machine-published claims should be corrected before freeze.

Reviewed commit: ac93d12

Tree manifest (my computation): 5ea1deb972d3eb0e9b430501f97e9bcbda6af54eef9aedd7e349dd7e752ccc25

CODEX-012-R12-DONE

### Dispositions

All nine findings **ACCEPTED**, and one at a **higher** severity than filed.
Every finding was independently re-verified against the bytes at `ac93d12`
before a disposition was written; all nine were confirmed, and the verification
raised finding 8 from nit to should-fix and refuted the reviewer's own
escalation hypothesis about it.

**This round found no blocking finding, and it tested the claim that mattered.**
Round 11's dispositions asserted that the vacuity defect class was closed — a
claim the maintainer had an interest in believing — so round 12's brief asked
the reviewer to test it independently rather than accept it. It did, and its
answer is recorded above in its own words: row 2 is correctly placed before both
decisive outcomes, no remaining contrast can manufacture either R1 verdict, and
the one form-mismatch left deliberately unrepaired is "honestly registered and
conservative". The four other flagged calls — the finding-7 downgrade, the
inherited-and-non-differential register, the containment coupling, and the
declined S1 rewrite — were validated on the same terms.

**Findings 1 and 2 share one shape, and it is the shape of my own repairs: the
gate was fixed and the published sentence did not follow.** Row 2's executable
condition has read arm E's own level since round 11 and is correct. But the row
still *rendered* `E-DEGRADED-GENERALLY — the denamed text degraded authoring
generally` unconditionally, so a real `RATES.md` line read "…arm A reads MID
there. the denamed text degraded authoring generally" — the disconfirming fact
sitting beside the claim it disconfirms, as an uninterpreted datum. Naming arm
A's level in `why`, which is what round 11 did, does not retract a diagnosis
printed next to it. **The round-11 record overclaimed in one clause**: "honest
about the job that only diagnoses" is false of the name-plus-gloss pair, and
"so a reader can see whether the attribution is established" is true only of a
reader who also holds §5.3 (iv). All four places the caveat lived —
registration prose, a docstring, a `PORTS.md` note, test comments — are
unpublished. The sharpest evidence is one the reviewer missed and the
verification found: §5.3 (iv)'s own closing sentence, "nothing is asserted here
that the level cannot carry", was **false while the gloss stood**. The fix makes
that sentence true rather than editing it, and it is now linted. The precedent
was in the same commit that left this unrepaired — round 11's finding-4 fix
moved §4.6's disclaimer into the travelling gloss for exactly this reason, one
table over. The published outcome **name** stands, consistent with rounds 9-11.

Finding 2 is the same correction a third time, and the count is worth saying
plainly: "a bound is not a zero" has now been fixed in round 10 (the S1 LOW
gloss), round 11 (`LABEL-COLLAPSE-ONLY`) and here (arm D's row 3), each time in
a cell a previous round had edited for a different reason. Round 11's finding-8
disposition corrected this cell's *keying* mismatch and left the zero-overclaim
standing in the same sentence. The gloss now states the registered bound — LOW
is at most 3 of 30, on at least three of the four narrow classes, with the
fourth free to read HIGH — and a 1-3-hit fixture pins it, where the tests had
used only zero and extreme populations.

**Finding 8 is raised from nit to should-fix, and the raise is recorded as
round 11 recorded its downgrade.** The registered witness for the degenerate arm
E said an all-sanctions-or-embargo population "keeps class 4 clear of LOW".
Class 4's predicate is `¬S ∧ country = SY`, so a sanctions hit or a KP or IR
registration matches it in **no** run: that arm reads LOW on class 4, and since
round 11 made row 2 a level test it is stopped there and never reaches row 5.
The sentence was therefore not merely under-stated but **false of the
sub-population a reader will most naturally instantiate** — and it is the
registered justification for row 5's fifth conjunct, the one conjunct round 9
added and rounds 10 and 11 twice re-derived. It is the argument, not decoration,
and it was duplicated in the scorer's docstring, so both registered statements
were wrong the same way. The escalation the reviewer floated is **refuted**: the
corrected witness — an arm E of non-sanctioned SY registrations — is reachable,
demonstrated to reach row 5, and refused there by the fifth conjunct alone. So
the conjunct still does the work it was registered to do, and the two repairs
interlock: the arm row 2 stops is not the arm row 5's conjunct is for.

**Finding 7 is a nit that was fixed because of its direction, not its size.**
The code puts every accepted mislabel in Q, class-reaching or not; the prose
glossed Q as records "reaching a class". The code's reading is the **stricter**
one for CONFIRMED, and the prose's is the looser one — so the ambiguity was
resolvable post hoc in the confirming direction, which is precisely the
asymmetry §5.3 registers as the mark of a study with a preferred answer, and the
same principle that refused a row-5-only fix in round 11. One clause closes it,
and §4.6's S2 is now named as the class-restricted quantity so the two stop
being confusable.

**Findings 3, 4, 5, 6 and 9 as verified.** A parity test asserted `len(rows) <=
1` and looped, so deleting the registered row-4 rule passed vacuously — the
standing target of this round's brief, now required to be exactly one and
demonstrated to fail on a deleted row. The schedule tests transcribed the
registered constants instead of binding them; the verification established that
the blocks *are* machine-parseable from the registration as it already stands —
three unique anchors, each parser asserting its own uniqueness — so the parse
was taken and no registration format was invented to manufacture it, with the
transcription kept beside it so a one-sided edit names its own drift site. One
interface sentence still said the scorer takes a batch root, which [D-23]
removed. §5.1 counted three level endpoints where there are four, and the sweep
found exactly one companion site.

And **the README round count, stale in rounds 10, 11 and 12, is fixed
structurally rather than a fourth time.** Round 10's own verification predicted
this recurrence in as many words. A new test derives the count from this file's
round headings and holds README's two sentences *and* this file's status line to
it, naming the obligatory value at edit time — demonstrated to fail on a record
appended without the counts advanced, which is exactly how the last three
happened.

Verification after the dispositions: `harness/integrity.py` exit 0 (tree
manifest unbound, pre-freeze); the pinned suite **291 passed**, run the way
README step 0 specifies; tracked status clean; `arms/`, `analysis/` and
`CLAIM.md` untouched by every disposition above. Two residuals are named rather
than closed: the corrected §4.1 sentence about Q is registered prose with no
test holding the code to it, and §2.2's two digest cells are hand transcriptions
no assertion covers. The post-disposition tree manifest, the maintainer's
computation, is
`539b481e2e53332fd68b88bd4de1ebd15ce1bbbe40d29b93de7f33f9291292e2` — round 13
attests it independently, and under §2.10 rule 3 that round is required, because
these dispositions changed bytes.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 12 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 13 — the freeze-readiness round, and the livelock it found

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-09; drafting as recorded in rounds 1-12
- Reviewed commit: `830984b`
- Tree manifest, the reviewer's computation:
  `539b481e2e53332fd68b88bd4de1ebd15ce1bbbe40d29b93de7f33f9291292e2` — 86
  entries, matching the maintainer's own computation recorded in round 12's
  dispositions
- Runs: one review run, completed; no run discarded, no classifier refusal
- **Commissioned because §2.10 rule 3 requires it** — round 12's nine
  dispositions changed bytes, and no tree may be frozen that a review round has
  not seen. Its brief therefore asked the freeze question directly, and told the
  reviewer plainly that manufacturing a finding to justify the round would be
  worse than finding nothing
- **Verdict: NOT READY TO FREEZE**, on one blocking finding: a livelock the
  maintainer created in round 12 while fixing a recurring nit
- Reviewer's verification first: integrity exit 0; 291 passed in 329.74s;
  worktree clean. Round 12's dispositions 1 and 3-7 fully implemented; row 2's
  rendered name-plus-gloss now makes only the withdrawal unconditional and
  expressly conditions its attribution, so §5.3 (iv)'s closing sentence is true
  of the published bytes; Q and the S5 ceiling are implemented over every
  accepted record. Artifact assembly, the prompt equation, the 280-cell grids,
  the schedule balances, the partition, the interval vectors, the scorer tables,
  C1-C10, `CLAIM.md` and all retained mirror attempts reconciled independently.
  **"No additional test passing for an unrelated reason was found"** — the
  standing target of rounds 10, 11 and 12 came up empty for the first time

### Prompt (verbatim)

```
You are performing a verification review — round 13 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 830984b on branch study-012-perturbation

**Round 12 returned no blocking finding — the first round that did.** This round exists because §2.10 rule 3 requires it: round 12's nine dispositions changed bytes, and no tree may be frozen that a review round has not seen. So the question in front of you is narrower and sharper than in earlier rounds: **is this tree ready to freeze?** A clean verdict is the expected outcome if the bytes earn one, and saying so plainly is the most useful thing you can do. Manufacturing a finding to justify the round would be worse than finding nothing.

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Verify round 12's nine dispositions.** `PREREG-REVIEW.md`'s round-12 section lists nine findings and, beneath them, the maintainer's dispositions. For each: is the disposition genuinely implemented in the bytes at this commit? Report any that is partial, mis-implemented, or implemented only in prose.

Three of them are the ones to press on, because each is a maintainer judgment rather than a mechanical repair:

- **The row-2 gloss (finding 1).** Rounds 9 through 12 have held that published outcome *names* are not renamed and that honesty must travel in the *gloss*. Row 2's gloss now says the withdrawal is established by arm E's level whatever arm A read, while the name's attribution holds only where arm A reads HIGH on class 4. Read the rendered `RATES.md` line, not just the table cell. Does the published pair — name plus gloss — now assert only what the rule establishes? Is §5.3 (iv)'s closing sentence ("nothing is asserted here that the level cannot carry") true of the published bytes?
- **The corrected class-4 witness (finding 8).** The registered justification for row 5's fifth conjunct now says the degenerate arm is one of *non-sanctioned SY registrations*, because an all-sanctions arm reads LOW on class 4 and row 2 stops it. Check that against §2.3's predicates and the scorer: is the corrected witness reachable, does it reach row 5, and is it refused there by the fifth conjunct alone? Do the two repairs interlock as the record claims, or does one of them now make the other unreachable?
- **The Q definition (finding 7).** §4.1 now registers Q as every accepted record whose label is wrong, class-reaching or not, and names §4.6's S2 as the class-restricted quantity. Confirm the code matches, and confirm the S5 ceiling `|Q| = 0` is over all of A — the record concedes this sentence has no test holding the code to it.

**2. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 12 found their sharpest results in the study rather than the harness. Keep that priority, and read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it. Round 12's dispositions edited §2.8, §4.1, §5.1, §5.3 and §4.6 — read those against what they now govern, and read the untouched sections as if for the first time.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**3. The suite, at 291, and the residuals the record names.** Rounds 9 through 12 grew it from 208 to 291. The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are uncovered; `_write_outputs()` is pinned only at its override gate; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's corrected Q sentence has no test; and §2.2's two digest cells are hand transcriptions no assertion covers. Confirm each is as described. Then ask what **else** the suite asserts less than it appears to — the standing target across rounds 10, 11 and 12 has been a test that passes for a reason unrelated to its subject, and each of those rounds found one.

**4. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**5. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**6. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: 830984b`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R13-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The absolute paths the reviewer's markdown links carried are rendered as the
`file:line` anchors they point at; no other byte of the message is altered.)

1. **Blocking — the round-count test makes a clean final review impossible.** test_review_status.py:50 derives the count from the excluded `PREREG-REVIEW.md` carrier and requires manifest-covered README.md:12 to match. Recording Round 13 therefore makes the suite fail until README changes 12→13; that byte change invokes §2.10 rule 3 at PREREGISTRATION.md:1282, requiring Round 14, and the cycle repeats. The test also hard-codes carrier status `OPEN` at line 79, preventing an accurate closed status. This contradicts the round-12 claim that disposition 9 was structurally fixed. The moving count must be removed from the covered README or otherwise decoupled, while carrier-internal consistency remains checked.

2. **Should-fix — the corrected class-4 witness still lacks its frequency premise.** PREREGISTRATION.md:1934 and score_rates.py:4491 say that having only non-sanctioned SY accepted records keeps class 4 clear of LOW. The record type is reachable, correctly labelled, and reaches class 4 alone, but one through three such scheduled runs still read LOW and are stopped by row 2. At least four distinct runs are required. With 30 such runs in an otherwise qualifying synthetic population, row 2 is bypassed and row 5 is refused solely by its class-3 conjunct; changing class 3 alone moves the result to row 5. Thus the repairs interlock, but only with the omitted “at least four distinct runs” premise.

3. **Nit — the arm-D explanatory arithmetic is wrong.** score_rates.py:775 and PORTS.md:45 say the repaired population may reach 36/120 narrow class-slots. The actual exemplar is `3+3+3+30 = 39`. The registered and machine-published gloss correctly states the bound, so verdicts are unaffected.

Round-12 dispositions 1 and 3–7 are fully implemented. Disposition 2’s published repair is correct apart from finding 3’s commentary arithmetic; disposition 8 is partial as above; disposition 9 is blocking. In particular, row 2’s rendered name-plus-gloss now makes only the withdrawal unconditional and expressly conditions its attribution on arm A being HIGH, so §5.3(iv)’s closing sentence is true. Q and the S5 ceiling are implemented over every accepted record, including wrong-label records reaching no class.

The artifact assembly, prompt equation, 280-cell grids, schedule balances, partition, interval vectors, scorer tables, C1–C10, `CLAIM.md`, and all retained mirror attempts reconciled independently. The named coverage residuals are accurately described; no additional test passing for an unrelated reason was found.

- Suite: `291 passed, 53360 warnings, 9 subtests passed in 329.74s`; exit 0.
- Verification: exit 0; all port, arm, and mirror checks passed; expected pre-freeze tree status was `unbound`.
- Independent manifest: 86 sorted entries, including the 6,653-byte normalized PINS projection. `integrity.tree_manifest()` implements the same recipe.

Overall verdict: **NOT READY TO FREEZE** — the review-count lifecycle defect is blocking.

Reviewed commit: 830984b  
Tree manifest (my computation): 539b481e2e53332fd68b88bd4de1ebd15ce1bbbe40d29b93de7f33f9291292e2  
CODEX-012-R13-DONE

### Dispositions

All three findings **ACCEPTED**. Every one was independently re-verified against
the bytes at `830984b`; all three confirmed, and the verification found the
blocking one to be **worse** than filed.

**Finding 1 is mine, and it is the worst kind: a remedy that was worse than the
defect it replaced.** Round 12 fixed a round-count staleness that had recurred
in rounds 10, 11 and 12 by adding a test that derives the count from this file —
which §2.10 **excludes** from the tree manifest as a carrier — and binds it to
`README.md`, which the manifest **covers**. So recording round 13 fails the
suite until README's count advances; that advance is a change to covered bytes;
§2.10 rule 3 then requires round 14 to attest the new manifest; and recording
round 14 is the same edit again. **The study could never be frozen.** The
verification measured it rather than arguing it: appending round 13's heading to
a copy failed 2 tests, and bumping README to match moved the manifest from
`539b481e…` to `f995c233…` — invalidating, in the very commit that records round
13, the attestation round 13 had just written.

Two things make it worse than the reviewer said, and both are recorded because
the round-12 disposition claimed this was "fixed structurally". There were
**two** README bindings, not one, so repairing the cited line would have left
the livelock fully intact. And the hard-coded `OPEN` status is the same trap a
second time: the only way to record a closed study was to edit a
manifest-covered test file, which is itself a rule-3 trigger — so the ceremony
had no exit in either direction.

The remedy inverts what round 12 built. The moving count leaves the covered
`README.md` entirely, replaced by a pointer that registers *why* it is not
copied there; the consistency round 12 actually wanted — this file's status line
against this file's own round headings — is kept, and it is free, because both
sides are carrier bytes; and the status word becomes the registered set
`("OPEN", "CLOSED")` rather than a literal. §2.10 gains the invariant as a
registered sentence, so the property is stated where the rule that needs it
lives rather than resting on a test's shape. The acceptance test is the whole
point of the round and was demonstrated rather than asserted: on the patched
tree, appending a round-13 record with status OPEN and appending a round-14
record with status CLOSED both leave the tree manifest **identical** to the
patched tree with no round appended —
`9084fd650920e155b81fd7421331117213aa6b6d3a80e0288164e5219aa65aa0` in all three
— with the suite green in each. Round 12's real goal survives: appending a
heading without advancing the status line still fails, on carrier bytes only.

The general lesson is registered with the fix, because it is the one worth
keeping: **a rule that requires review of every byte change makes any
self-updating value in a covered file unfreezable.** The record-keeping act must
touch only carriers.

**Finding 2 is round 12's finding-8 fix, still incomplete.** Round 12 corrected
the degenerate-arm witness from "all sanctions or embargo" to "non-sanctioned
SY" — right, and still missing a premise: LOW is registered as at most 3 of 30,
so a witness covering class 4 in only one to three runs *still* reads LOW there
and is stopped at row 2 before row 5 is reached. At least four distinct runs are
required for the witness to do the work it is registered to do. The premise is
now stated at all three loci the sweep found. That is the second round running
in which this witness was corrected and left short; the disposition says so.

**Finding 3** is a genuine nit — an explanatory comment counting 36 narrow
class-slots where the exemplar is 39 — with the published gloss unaffected.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **291 passed**, unchanged in count (two README-binding tests deleted, two
carrier-side tests added, one rewritten in place); tracked status clean;
`arms/`, `analysis/` and `CLAIM.md` untouched. Two hazards are named rather than
closed: `README.md`'s DRAFT status lines must read correctly for the *frozen*
tree before the final round begins, since rule 3 forbids editing them after; and
the §4.6 clause's other consequent still needs an arm-labelling premise the
record type alone does not supply. The post-disposition tree manifest, the
maintainer's computation, is
`9084fd650920e155b81fd7421331117213aa6b6d3a80e0288164e5219aa65aa0` — round 14
attests it, and under §2.10 rule 3 that round is required, because these
dispositions changed bytes. **Recording round 14 will not require another**: that
is what this round's fix bought.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 13 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 14 — the freeze question, asked of the tree the pre-freeze repair left

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-09; drafting as recorded in rounds 1-13
- Reviewed commit: `bfbfdb6`
- Tree manifest, the reviewer's computation:
  `ed58300605bd2101026fa7b26c39babef01137ba86c510f75959338bfd5b8f5e` — 86
  entries, matching the maintainer's own computation
- Runs: one review run, completed; no run discarded, no classifier refusal
- **Verdict: NOT READY TO FREEZE**, on two blocking findings
- **What this round was given to review, stated plainly in its own brief.**
  Round 13 named two hazards to close before the final round, since rule 3
  forbids editing a covered byte afterward. Closing them was maintainer-initiated
  work between rounds, and no reviewer had seen any of it — so the brief put that
  unreviewed surface first and said so
- Reviewer's verification first: integrity exit 0; 294 passed in 346.99s;
  worktree clean. Round 13's three dispositions genuinely implemented. The five
  sentences the pre-freeze repair deliberately left untouched are **confirmed
  correctly classified** as conditional, historical, role-defining or pinned
  quotations. Independent rederivations reconciled all five Appendix assemblies
  and prompt equations, the 948-byte header, all twenty pinned artifacts, all
  five 280-cell grids, arm C's permutation, the complete schedule and its five
  balances, §3.3's partition, §4's vectors, §5's tables and C1-C10; `CLAIM.md`
  matches its pinned Study 011 source; the retained C10 attempts reconcile
  through prompt, extraction, mirror, chronology and reported grids
- The reviewer's own summary of what is and is not at stake: **"The scientific
  rates and decision machinery do not presently claim an unearned result. What
  the frozen-and-published study would not have earned is its claimed
  review-to-publication byte binding"**

### Prompt (verbatim)

```
You are performing a verification review — round 14 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: bfbfdb6 on branch study-012-perturbation

**The question in front of you is: is this tree ready to freeze?** A clean verdict is a real outcome, and saying so plainly is the most useful thing you can do if the bytes earn it. Manufacturing a finding to justify the round would be worse than finding nothing.

**What has happened since the last round, stated plainly because it changes what you should look at.** Round 13 answered NOT READY on one blocking finding: a livelock the maintainer had created in round 12 while fixing a recurring nit — a test bound a manifest-covered file to a round count that had to advance every round, so recording a round changed covered bytes, §2.10 rule 3 then required another round, and the study could never be frozen. Round 13's dispositions removed it and registered the lesson in §2.10: *a rule requiring review of every byte change makes any self-updating value in a covered file unfreezable; the record-keeping act must touch only carriers.*

Round 13 also named two hazards to close **before** the final round, since rule 3 forbids editing a covered byte afterward. Closing them was maintainer-initiated work between rounds, and **no reviewer has seen any of it** — it is the largest untested surface at this commit and deserves your attention first. Sweeping the first hazard turned it into a defect *class* with a blocking member:

- Manifest-covered files asserted **where the study stands** — `DRAFT`, `freeze pending`, `Nothing has run`, `none of it is frozen`, `None exists yet`, `no arm artifact has been frozen`. Every one goes false at the freeze or at the run, and rule 3 then locks it false permanently. This is round 12's livelock one act later: the recording act was fixed and the freezing act was not. All are now read from the registry's four lifecycle members, which are carrier bytes nulled in the manifest's normalized projection.
- The blocking member was **executable, not prose**: a test asserted a refusal message the tree stops producing at README step 4 (the golden capture, which is *after* the freeze), so CI would go red on the commit that registers the capture, with the fix rule-3-locked. A twelfth instance of the same shape was then found in `test_batch.py`, where a stand-in registry inherited the very member its null case was about.
- Three tests were added to close the class rather than its instances: the tree manifest asserted invariant under every registered lifecycle act; a lint forbidding lifecycle-status idioms in covered files (which registers honestly that a phrase list cannot be complete); and the rule that no test expectation may be a function of the study's stage.
- Five sentences that resemble the same defect were deliberately **left untouched** as registration-time statements, correct as written — including `CLAIM.md`'s pinned quotation, whose correction §1 forbids.
- Separately, §4.6's witness gained the arm-labelling premise round 13 had named and left open.

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. The unreviewed pre-freeze repair — the priority of this round.** Nothing above has been through a review. Judge it:

- **Is the lifecycle-staleness class actually closed?** Sweep every manifest-covered file yourself for any sentence, status, count, date or claim that is true now and false after the freeze, after the batch runs, or after publication. The maintainer's sweep found eleven prose hits and two executable ones; find what it missed, in either direction. Say explicitly whether any *further* covered byte is a function of the study's own stage.
- **Are the five untouched sentences correctly classified?** They were judged registration-time statements that must not be "fixed". If any is in fact a live self-updating value, that is a finding; if any was fixed that should not have been, that is also a finding.
- **Do the three new tests do what they claim?** The manifest-invariance test, the lifecycle-status lint, and the two rewritten stage-dependent tests. Would each fail if the property it names stopped holding? The lint is a blacklist and says so — judge whether its registered statement of its own strength is honest.
- **Verify the freeze and run really move no covered byte.** Take the registry's four lifecycle members and `freeze.excluded`, and satisfy yourself that no registered act — freeze, golden capture, C7, the 150-call batch, scoring, publication — changes anything the manifest covers. This is the property rule 3's termination depends on, so check it from the registration rather than from the maintainer's summary.

**2. Verify round 13's three dispositions**, listed in `PREREG-REVIEW.md`'s round-13 section: the livelock removal, the class-4 witness frequency premise, and the arm-D arithmetic correction. Is each genuinely implemented?

**3. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 13 found their sharpest results in the study rather than the harness. Read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**4. The suite, at 294, and the residuals the record names.** The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are covered only for `tree_manifest()`; `_write_outputs()` is pinned only at its override gate; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's Q sentence has no test; §2.2's two digest cells are hand transcriptions no assertion covers; and after README step 5 the tree stops producing the C7 refusal message with no test asserting it. Confirm each is as described, then ask what **else** the suite asserts less than it appears to.

**5. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**6. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**7. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: bfbfdb6`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R14-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The absolute paths the reviewer's markdown links carried are rendered as the
`file:line` anchors they point at; no other byte of the message is altered.)

1. **Required compiled records invalidate the frozen manifest — severity: blocking.**

   - **Record:** README.md:303 registers `score --emit-records records`; PREREGISTRATION.md:3715 requires those compiled trees to be published.
   - **Code:** score_rates.py:4632 invokes `_emit_records()`, which writes `<out>/<arm>/<slot>/...` at score_rates.py:5108. The exclusions at PINS.json:159 omit `records/`. Once those files are tracked for required publication, the manifest changes.
   - test_manifest.py:244 simulates only five excluded documents, so its “every registered lifecycle act” claim is false of the registered scoring command. Closure requires binding the actual record destination to an excluded tree, or forcing emission outside the study, and testing that real destination.

2. **The conditional R1 correction requires editing manifest-covered README bytes — severity: blocking.**

   - **Record:** PREREGISTRATION.md:3669 and README.md:106 require an observed R1-UNSUPPORTED result to be published as a correction in this README, not merely in generated outputs.
   - **Code/tree:** README is manifest-covered, and rule 3 forbids changing it after the final review. The lifecycle test again models publication solely through excluded files at `test_manifest.py:244-247`; it never models the required correction.
   - A row-4 result therefore forces a choice between changing covered bytes after freeze and violating the registered publication commitment. The publication mechanism or commitment must be made freeze-compatible before review.

3. **§4.6 overstates what one wrong class-4 label does — severity: should-fix.**

   - **Record:** PREREGISTRATION.md:1974 and score_rates.py:4500 say any one mislabel removes that run’s primary class-4 coverage and makes row 2 stop the arm.
   - **Code:** Coverage is existential within a run—any correctly labelled class-4 record preserves it at score_rates.py:3215. Even if the run is lost, row 2 fires only when aggregate class-4 coverage is LOW at score_rates.py:4593. A public-API check confirmed 29/30 remains HIGH and degraded labels can route to row 7, not row 2.
   - test_verdict_parity.py:584 changes both synthetic records together and never calls the level or decision functions, so it does not establish its claimed consequence. The operative decision table is correct; the explanatory witness and test are not.

4. **The lifecycle-status lint silently omits normalized PINS — severity: should-fix.**

   - **Record/test:** test_review_status.py:143 removes both carriers and therefore skips all of `harness/PINS.json`. Its stated exclusions at lines 171–173 mention only `arms/` and the test itself.
   - **Code:** integrity.py:1031 binds normalized PINS with everything except four lifecycle values byte-significant. A stale-status phrase in a PINS note would therefore evade the lint.
   - The lint honestly discloses that its phrase blacklist is incomplete; this separate scope omission is not disclosed. Current normalized PINS contains no stale assertion, so this is not itself blocking. A complete lint must also scan the normalized projection.

Verification summary:

- The five untouched statements are correctly classified as conditional, historical, role-defining, or pinned quotations: `PREREGISTRATION.md:3-4`, `:22-28`, `README.md:16-18`, `PREREGISTRATION.md:3950-3956`, and `CLAIM.md:53-56`.
- Round 13’s livelock removal, four-of-thirty frequency premise, and arm-D `39/120` correction are genuinely implemented.
- Independent rederivations reconciled all five Appendix assemblies and prompt equations, the 948-byte header, all 20 pinned artifacts, all five 280-cell grids, arm C’s permutation, the complete schedule and five balances, §3.3’s partition, §4 vectors, §5 tables, and C1–C10.
- `CLAIM.md` matches its pinned Study 011 source; the retained C10 attempts reconcile through prompt, extraction, mirror, chronology, and reported grids.
- All named residuals are accurately described. The additional cases where tests assert less than they appear are findings 1, 3, and 4.
- Suite: `294 passed, 54050 warnings, 9 subtests passed in 346.99s (0:05:46)`.
- Verification command: exit 0; it verified 11 ports, all arms, the 948-byte header, mirrors A–E, CPython 3.12.11, and reported the expected pre-freeze unbound manifest.
- My independent recipe produced 86 sorted entries including normalized PINS; `integrity.tree_manifest()` returned the identical digest.
- The scientific rates and decision machinery do not presently claim an unearned result. What the frozen-and-published study would not have earned is its claimed review-to-publication byte binding: required `records/` publication moves the manifest, and a row-4 result requires a locked README edit.

**Overall verdict: NOT READY — I do not judge this tree ready to freeze.**

Reviewed commit: bfbfdb6

Tree manifest (my computation): ed58300605bd2101026fa7b26c39babef01137ba86c510f75959338bfd5b8f5e

CODEX-012-R14-DONE

### Dispositions

All four findings **ACCEPTED**, all four independently confirmed against the
bytes at `bfbfdb6`. This is the same defect class at its **third act** —
recording (round 12), freezing (the pre-round-14 repair), and now **publishing**
— and the disposition records that pattern rather than the three instances,
because the pattern is the finding.

**Finding 2 is the sharpest result of the whole sequence: the study could not
publish the one outcome it exists to be able to publish.** §8 commits that if
arm E maintains coverage, R1 is published as UNSUPPORTED "with the same
prominence as the claim" — and one of the four named venues is this study's
README, which §2.10's manifest covers and rule 3 forbids editing after the final
review. So the **falsification** path — the entire point of a study built as a
falsifier — ran through a byte the study's own integrity rule locks. The
maintainer would have faced three bad horns, and the verification named a third
the reviewer had missed and which is the worst: re-pinning after publication is
**manifest-neutral**, because `freeze.treeManifestSha256` is nulled in the
normalized projection, so the binding would silently re-anchor to a post-data
tree. That is exactly the self-authenticating binding round 2 killed. A defect
whose most convenient remedy is invisible is worse than one whose remedy is
merely wrong.

The fix had one governing constraint: **the commitment must not weaken.** Moving
a falsification to a quieter venue, making it conditional, or dropping one would
be precisely the post-hoc softening §8 exists to prevent, and a later reader
would be right to read it that way. So: all four venues kept; "with the same
prominence as the claim" byte-identical in all three registered statements;
§8's "No re-cutting … no relegation to a limitations section" byte-identical;
the two-part correction — the withdrawal and *this study does not thereby
establish the opposite*, same paragraph, not a footnote — byte-identical.
Nothing deleted; both files grew. Only one venue's **mechanism** changed: the
README now carries a **frozen, pre-data pointer** to `CORRECTION.md`, a new
top-level document in `freeze.excluded`.

Two things make the pointer *stronger* than the sentence it replaces, and both
are registered so the change cannot be read as convenience. `CORRECTION.md` is
written in **every** outcome, naming the row the scorer computed — so the link
is permanent and an absent `CORRECTION.md` is a visible failure to publish
rather than a legitimate outcome. And the pointer is frozen bytes written before
the data: dropping the venue now moves the attested digest, where a
post-hoc-edited README venue could simply never be written. A lint fails if the
link is removed, before any digest moves.

**Finding 1 is the same class, and it caught a test I wrote to close that very
class.** `records/` — the destination the registered `score --emit-records
records` command writes, whose compiled trees §8 *requires* published — was
absent from `freeze.excluded`, so publishing them would move the frozen manifest
and make `integrity.py` refuse permanently. The lifecycle-invariance test added
in the pre-round-14 repair claimed to cover "every registered lifecycle act"
while modelling five excluded documents and never the registered scoring
command: it asserted less than its name claimed, which is the standing target of
five rounds. The corrected test now reads the destination **out of the README's
own command literal** and writes the real emitted layout, so it models the act
rather than a stand-in — and it fails on the pre-fix bytes at exactly that act.
A registered sentence was also false and is now true without being edited:
§2.10's claim that every act from the freeze to publication moves carrier or
excluded bytes only became true the moment `records/` entered the exclusion list.

**Finding 3 is the pre-round-14 repair overshooting.** Closing round 13's named
residual, the added labelling premise claimed that one wrong class-4 label
removes that run's coverage and lets row 2 stop the arm. Coverage is
**existential** within a run — any correctly labelled class-4 record preserves it
— and row 2 fires only on the **aggregate** level. The premise closes row 5's
ceiling, not row 2's gate, and now says so at all four loci, one of which the
reviewer missed. Its test asserted a consequence it never exercised, calling
neither the level nor the decision functions; the replacement calls both, and
was shown to fail under two separate mutations that would each have made the old
false sentence true.

**Finding 4** is the lint from the same repair disclosing one weakness and not
another: it registered honestly that a phrase blacklist cannot be complete, and
silently skipped the normalized PINS projection, which is manifest-bound with
note fields byte-significant. It now scans the projection, and the disclosure
names **both** weaknesses.

Two process notes worth keeping. The verification again **contradicted a report
this round relied on** — two of the four claimed no ported executable moves;
`score_rates.py` is ported, and the cascade was run. And a garbled registered
sentence in §4.6, predating this round and covered by no finding, was repaired
rather than carried into a freeze: it had two finite verbs and no antecedent,
and shipping ungrammatical registered prose because no reviewer filed it would
be the wrong kind of discipline.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **297 passed**; tracked status clean; `arms/`, `analysis/`, `CLAIM.md` and
`MIRROR-AGREEMENT.md` untouched. Demonstrated rather than asserted: emitting the
**real** registered record destination and staging it now leaves the manifest
identical where it previously moved, and writing `CORRECTION.md` — in the row-4
outcome and in every other — leaves it identical too. The post-disposition tree
manifest, the maintainer's computation, is
`77f1e1fb1a90cd547b949b19aff6d6689d89d5db812871958f86e6f370b51223` — round 15
attests it, and under §2.10 rule 3 that round is required, because these
dispositions changed bytes.

Two residuals are named rather than closed: `_emit_records()` and
`_check_records_target()` still have no direct suite coverage, which is why the
destination went unmodelled for fourteen rounds; and `CORRECTION.md` is
deliberately **not** created now, because it is a post-data excluded output and
writing it before the data would be a covered-byte lie of the same family as the
one this round closed.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 14 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 15 — the class reopens in a test fixture

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-10; drafting as recorded in rounds 1-14
- Reviewed commit: `c221dbb`
- Tree manifest, the reviewer's computation:
  `77f1e1fb1a90cd547b949b19aff6d6689d89d5db812871958f86e6f370b51223` — 86
  entries, matching the maintainer's own computation
- Runs: one review run, completed; no run discarded, no classifier refusal
- **Verdict: NOT READY TO FREEZE**, on one blocking finding
- Reviewer's verification first: integrity exit 0; 297 passed in 330.38s;
  worktree clean. **Round 14's four dispositions hold**, and the one the brief
  asked it to judge for post-hoc softening was cleared in its own words: the
  four correction venues remain, the same-prominence language, the
  no-recut/no-relegation sentence and both correction clauses are intact, and
  **"the mechanism does not make correction easier to avoid: the pointer is
  frozen, `CORRECTION.md` is mandatory in every outcome, and omission leaves a
  visible dangling commitment."** On the fourth-instance sweep the brief asked
  for: every current lifecycle writer — freeze, golden capture, C7, batch,
  scoring, record emission, publication, correction, deviations and review
  recording — writes only carriers or excluded destinations, and **no fourth
  output-path writer exists**. The scientific registration re-derived cleanly:
  all twenty arm hashes and Appendix assemblies, every prompt against the
  948-byte header equation, all five 280-cell grids, the five schedule
  balances, the partition, the interval vectors, the level/contrast tables, the
  decision rows and the operating figures; `CLAIM.md` matches its Study 011
  source and all five retained C10 attempts reconcile at 280/280
- The reviewer's own statement of what freezing here would cost: the rate and
  decision machinery **"would publish no scientific result it has not earned"**;
  what it would publish unearned is **"durable stage-independent batch-golden
  coverage and a functioning CI C1 run"**

### Prompt (verbatim)

```
You are performing a verification review — round 15 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: c221dbb on branch study-012-perturbation

**The question in front of you is: is this tree ready to freeze?** A clean verdict is a real outcome, and saying so plainly is the most useful thing you can do if the bytes earn it. Manufacturing a finding to justify the round would be worse than finding nothing.

**What changed since round 14, and what it means for where you should look.** Round 14 answered NOT READY on two blocking findings, both instances of one defect class this study has now hit at three separate acts: a self-updating value living in a manifest-covered file. Round 12 hit it at the **recording** act (a round count), a pre-round-14 repair hit it at the **freezing** act (status prose), and round 14 hit it at the **publishing** act, twice:

- `records/` — the destination the registered `score --emit-records records` command writes, whose compiled trees §8 *requires* published — was not in `freeze.excluded`, so publishing them would have moved the frozen manifest and made `integrity.py` refuse permanently.
- §8 commits that an R1-UNSUPPORTED result is published "with the same prominence as the claim" in four venues, one of which was this study's manifest-covered README. **The falsification outcome could not be published without breaking the study's own freeze pin.**

Round 14's dispositions closed both. `records/` and a new top-level `CORRECTION.md` are now in `freeze.excluded`; the README venue became a **frozen, pre-data pointer** to `CORRECTION.md`, which is registered as written in **every** outcome so the link is permanent and an absent `CORRECTION.md` is a visible failure to publish rather than a legitimate outcome. **Judge that repair hard, and judge it specifically for post-hoc softening**: the maintainer's constraint was that the commitment must not weaken, and a later skeptical reader is exactly who the check is for. All four venues, the "same prominence" clause, §8's no-re-cutting sentence and the two-part correction text were required to survive byte-identical — verify they did, and say plainly whether the mechanism change makes the correction easier to avoid in any way at all.

Two further things round 14 changed, both of which caught the maintainer's own work: the lifecycle-invariance test claimed to cover "every registered lifecycle act" while modelling only five documents and never the registered scoring command (it now reads the destination out of README's own command literal); and the §4.6 labelling premise added one round earlier had overshot — coverage is existential within a run, and row 2 reads the aggregate level. A garbled registered sentence in §4.6, covered by no finding, was also repaired rather than carried into a freeze.

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Round 14's four dispositions — the priority of this round.** Judge each, and press hardest on the two blocking repairs:

- **Is the lifecycle-staleness class actually closed?** Sweep every manifest-covered file yourself for any sentence, status, count, date or claim that is true now and false after the freeze, after the batch runs, or after publication. The maintainer's sweep found eleven prose hits and two executable ones; find what it missed, in either direction. Say explicitly whether any *further* covered byte is a function of the study's own stage.
- **Are the five untouched sentences correctly classified?** They were judged registration-time statements that must not be "fixed". If any is in fact a live self-updating value, that is a finding; if any was fixed that should not have been, that is also a finding.
- **Do the three new tests do what they claim?** The manifest-invariance test, the lifecycle-status lint, and the two rewritten stage-dependent tests. Would each fail if the property it names stopped holding? The lint is a blacklist and says so — judge whether its registered statement of its own strength is honest.
- **Verify the freeze and run really move no covered byte.** Take the registry's four lifecycle members and `freeze.excluded`, and satisfy yourself that no registered act — freeze, golden capture, C7, the 150-call batch, scoring, publication — changes anything the manifest covers. This is the property rule 3's termination depends on, so check it from the registration rather than from the maintainer's summary.

**2. The defect class itself, at every act.** Three acts have been repaired. Sweep for a fourth: take every registered act in the study's lifecycle — the freeze, the golden capture, §6 C7, the 150-call batch, scoring, `--emit-records`, publication, the correction, `DEVIATIONS.md`, and the recording of a review round — and satisfy yourself from the registration and the exclusion list that each moves only carrier or excluded bytes. If any act still moves a covered byte, that is this round's blocking finding. Say explicitly whether the class is now closed or whether you found a fourth instance.

**3. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 13 found their sharpest results in the study rather than the harness. Read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**4. The suite, at 297, and the residuals the record names.** The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are covered only for `tree_manifest()`; `_write_outputs()` is pinned only at its override gate; `_emit_records()` and `_check_records_target()` have no direct suite coverage, which is why the record destination went unmodelled for fourteen rounds; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's Q sentence has no test; §2.2's two digest cells are hand transcriptions no assertion covers; and after README step 5 the tree stops producing the C7 refusal message with no test asserting it. Confirm each is as described, then ask what **else** the suite asserts less than it appears to.

**5. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**6. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**7. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: c221dbb`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R15-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(The absolute paths the reviewer's markdown links carried are rendered as the
`file:line` anchors they point at; its own `## Findings` heading is demoted to
keep this record's section structure; no other byte is altered.)

#### Findings

1. **Blocking — the lifecycle-staleness class is not closed: the batch fixture still inherits live golden/C7 state.**

   - **Record:** PREREGISTRATION.md:1307 says no manifest-covered test expectation may depend on the study’s stage.
   - **Code:** test_batch.py:188 copies the committed registry but does not reset `golden.sha256` or `isolationNegative.assent`. Consequently, after README step 4, test_batch.py:491 no longer tests an unregistered golden: it tests a missing or mismatching temporary capture. After step 5, test_batch.py:226 falsely says the helper deliberately does not grant assent.
   - Both golden tests assert only exit 1 while C7 is unmet, so the downstream C7 refusal can mask removal of the named batch golden check. The explicit scorer fixture tests a separate gate and does not cover `batch.require_golden()`.
   - A complete repair must explicitly set the fixture’s lifecycle members, advance them only through fixture acts, and assert the named batch refusal.
   - **Severity: blocking.** The mandatory golden and C7 acts make covered test prose and test meaning false after freeze. This is another instance of the lifecycle defect class.

2. **The manifest-invariance test is not coupled to the executable writers it claims to cover.**

   - **Record:** PREREGISTRATION.md:1315 and test_manifest.py:208 say every registered lifecycle act is applied and any future unexcluded output will fail.
   - **Code:** test_manifest.py:249 hand-models fixed destinations. Its scoring simulation writes six named documents plus the README-parsed `records/` layout; it never invokes or introspects `score_registered()`, `_write_outputs()`, `_emit_records()`, or the batch writers. It would remain green if one of those writers added an unexcluded `SUMMARY.md`.
   - The current writer inventory is correct and entirely excluded, so this is a regression-strength defect rather than a present manifest violation. A complete test must bind the real writers’ destination inventory to the exclusions.
   - **Severity: should-fix.**

3. **The carrier-only review-status check has an unregistered twenty-round ceiling.**

   - **Record:** PREREGISTRATION.md:1296 says recording another review round remains free because only carrier bytes move; no review-count maximum is registered.
   - **Code:** test_review_status.py:51 defines number words only through twenty, and test_review_status.py:152 indexes that tuple by the live round count. Round 21 raises `IndexError` and requires a covered test edit.
   - **Severity: should-fix.**

4. **The registered Study-012 CI verification step unconditionally refuses.**

   - **Record:** README.md:198 and PREREGISTRATION.md:3055 say C1 and the deterministic suite run in CI.
   - **Code:** .github/workflows/ci.yml:71 runs `python harness/integrity.py` without `-P` or `PYTHONSAFEPATH=1`; integrity.py:1380 therefore refuses before verification. I reproduced exit 2 with the exact safe-path refusal. The following pytest step is skipped.
   - The local ceremony and batch/scorer gates remain sound, and the workflow is outside the study manifest, so I follow the earlier CI precedent rather than treating this as scientific blocking.
   - **Severity: should-fix.**

5. **C10 carries a malformed Markdown delimiter.**

   - **Record:** C10’s second clause says the clean-room author receives only the arm policy and fixed interface.
   - **Bytes:** PREREGISTRATION.md:3356 closes the intended bold span before carrying an unmatched `**` after `else` at line 3361. The substantive rule remains intelligible and the retained attempts satisfy it.
   - **Severity: nit.**

Round 14’s four dispositions otherwise hold:

- `records/` and `CORRECTION.md` are correctly excluded, and every current lifecycle writer—freeze, golden capture, C7, batch, scoring, record emission, publication, correction, deviations, and review recording—writes only carriers or excluded destinations. No fourth output-path writer exists.
- The four correction venues remain; outside the expressly registered README-to-linked-`CORRECTION.md` mechanism change, the same-prominence language, no-recut/no-relegation sentence, and both correction clauses remain intact. The mechanism does **not** make correction easier to avoid: the pointer is frozen, `CORRECTION.md` is mandatory in every outcome, and omission leaves a visible dangling commitment.
- The five untouched statements are correctly retained as conditional, historical, role-defining, or pinned quotations. None is a live status value.
- The lifecycle lint honestly calls itself a blacklist and now scans normalized PINS. The rewritten scorer and C7 null-state tests are stage-independent. The separate batch fixture in finding 1 is what the sweep missed.
- The §4.6 repair is correct: mixed labelling loses the S5 ceiling but does not erase existential within-run coverage; 29/30 remains HIGH and routes from row 5 to row 7, while 3/30 routes to row 2.

The scientific registration re-derived cleanly: all 20 arm hashes and Appendix assemblies match; every prompt satisfies the 948-byte-header equation; all five 280-cell grids agree with the registered mirror; the schedule has all five registered balances; the partition, interval vectors, level/contrast tables, decision rows, and operating figures match the scorer. `CLAIM.md` matches its Study-011 source, and all five retained C10 attempts reconcile through prompt, extraction, chronology, and 280/280 agreement.

The named coverage residuals are accurately described, with one nuance: `normalized_pins()` is now directly exercised by the projection lint, although its complete four-member normalization contract and `verify_tree()`’s frozen branch remain without direct tests. No additional scientific claim or arithmetic defect was found.

- Suite: `297 passed, 54050 warnings, 9 subtests passed in 330.38s`; exit 0.
- Verification command: exit 0; 11 ports, five arms, 948-byte header, and mirrors A–E verified; expected pre-freeze manifest status `unbound`.
- Independent manifest: 86 entries, including a 7,031-byte normalized registry projection. `integrity.tree_manifest()` returned the identical digest.
- Worktree remained clean.

If frozen and run tomorrow, the rate and decision machinery would publish no scientific result it has not earned. It would, however, publish verification claims it has not earned: durable stage-independent batch-golden coverage and a functioning CI C1 run.

**Overall verdict: NOT READY TO FREEZE — finding 1 is blocking; the lifecycle-staleness class remains open.**

Reviewed commit: c221dbb

Tree manifest (my computation): 77f1e1fb1a90cd547b949b19aff6d6689d89d5db812871958f86e6f370b51223

CODEX-012-R15-DONE

### Dispositions

All five findings **ACCEPTED**, all five independently confirmed against the
bytes at `c221dbb`.

**Finding 1 is blocking, and the verification changed what it is blocking
*for*. The disposition must not overstate it.** The reviewer framed it as a
fourth instance of the lifecycle-livelock class. It is an instance of the
registered rule — a covered test expectation that is a function of the study's
stage — but it is **not a livelock**: the suite is 297 green at the base stage,
green after the golden capture, and green after §6 C7. Nothing turns red at any
act. The harm is **silent coverage loss**, which is worse in one respect and
better in another, and both belong in the record: worse because a red suite
announces itself and this does not; better because freezing with it open would
not have stopped the study running.

What makes it blocking is the fact the verification established by doing it
rather than arguing it: **with `batch.require_golden()`'s preflight call
removed, the entire suite still passed — 297 of 297.** Not merely the two
golden cases. Nothing anywhere in the harness caught deletion of §3.2's golden
gate from the batch path, because the stand-in registry inherited a live
`golden.sha256` and a live `isolationNegative.assent` from the committed
registry, and both golden cases asserted only `exit 1` while a downstream C7
refusal supplied it. The fixture now writes all four post-freeze members
explicitly — including `freeze.treeManifestSha256`, which the verification
added to the repair — advances them only through fixture acts, and the cases
assert the **named** refusal rather than a bare exit code. With the fix, that
same deletion turns the suite red on the two tests that name the gate.

Two things the reviewer had imprecise, corrected here because the record is the
thing a later reader gets. The golden case's *first* assertion never changed
meaning — `require_golden` checks file existence before the pin — so only the
second degenerated, into a byte-for-byte duplicate of the mismatch test beside
it, leaving §3.2's "the null must be replaced" refusal with no test at all. And
a **third** affected case the reviewer did not name: the test whose subject is
the C7 *record* gate was in fact exercising the *assent* member, and its subject
would have flipped at step 5. The sweep the brief demanded found no others:
`stand_in_registry` was the only fixture inheriting any lifecycle member.

**Finding 4 is mine, and it is the one I would least like to have found late.**
CI has run `python harness/integrity.py` without `PYTHONSAFEPATH=1` since round
10's disposition added the safe-path refusal — so the registered C1 verification
step has exited 2 before verifying ever since, with the pytest step skipped
behind it. Measured while fixing it: the pytest step as written fails 61 of 301
for the same reason. §7 and the README say C1 and the deterministic suite run in
CI. Those sentences have been false for five rounds, and no round caught it
because every round ran the ceremony locally, where it passes. The workflow is
outside the study manifest, so this could have been fixed after the freeze —
which is exactly why it is worth saying that it was **not** deferred: a
registered sentence being false is not less false for being cheaply fixable.

**Findings 2, 3 and 5 as verified.** The manifest-invariance test hand-modelled
its destinations, so it would have stayed green if a writer grew an unexcluded
output; it now scans the writing modules and binds every destination they name
to the exclusion list, and its own docstring states the four things that scan
still does not reach — it reads rather than runs, does not follow a parameter to
its callers, is Python-only, and fails closed. The round-count check carried an
unregistered twenty-round ceiling that would have raised `IndexError` at round
21 and forced a covered-byte edit — a latent instance of precisely the class the
round-13 livelock fix closed, sitting inside that fix. And C10's malformed
delimiter is repaired.

**One repair beyond the findings**, taken because this was the last free moment:
a `+ ` at the start of a continuation line in [D-5] splits that paragraph under
CommonMark and orphans two italic delimiters. It is strictly worse than the
delimiter finding 5 named, no finding covered it, and shipping it into a freeze
because no reviewer filed it would be the wrong kind of discipline — the same
reason round 14 repaired a garbled sentence no finding covered.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **301 passed** (297 + 4: the stage guard, the writer-destination scan, its
scope check, and the round-ceiling test); tracked status clean; `arms/`,
`analysis/`, `CLAIM.md` and `MIRROR-AGREEMENT.md` untouched. Demonstrated rather
than asserted: the suite's *meaning* is now stable across the base, post-golden
and post-C7 stages — a probe recording which refusal each case actually asserts
prints the same three lines at all three, where before the second silently
became a duplicate and the third flipped gate. The post-disposition tree
manifest, the maintainer's computation, is
`e4f15954c87373e2f885bde8ea0382d78feb208c9157a5f5244a0c5d501369db` — round 16
attests it, and under §2.10 rule 3 that round is required, because these
dispositions changed bytes.

Residuals named rather than closed: `_emit_records()` and
`_check_records_target()` still have no direct coverage; the writer scan is
Python-only, so `authoring_call.sh`'s writes are outside it; and the four
registered sentences about CI become true only when a pull request actually runs
`study-012-harness` green, which has never happened — the publication PR should
be tied to an observed-green job rather than to an absence of failures.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 15 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 16 — the gate-coverage class, measured

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-10; drafting as recorded in rounds 1-15
- Reviewed commit: `60b1445`
- Tree manifest, the reviewer's computation:
  `e4f15954c87373e2f885bde8ea0382d78feb208c9157a5f5244a0c5d501369db` — 86
  entries, matching the maintainer's own computation
- **Runs: four commissionings, three discarded to vendor capacity.** Attempts 1,
  2 and 3 died on `ERROR: Selected model is at capacity`, at roughly 218,000,
  46,000 and 16,000 tokens — the depth falling each time, so capacity was
  tightening rather than clearing. No classifier refusal in any of them; this is
  unrelated to round 9's discarded run. All three transcripts are retained
  beside the completed one. The maintainer declined to substitute a different
  model, because rounds 2-15 are each recorded against `gpt-5.6-sol` and
  changing the reviewer mid-sequence is a change to the instrument that belongs
  in the record as a deliberate choice rather than as an outage workaround
- **Verdict: NOT READY TO FREEZE**, on two blocking findings
- Reviewer's verification first: integrity exit 0; 301 passed; worktree clean.
  Round 15's five dispositions hold. The scientific registration re-derived
  cleanly once more — all twenty artifacts and prompt equations, the six
  semantic classes and 280-cell grids, the schedule balances, the interval
  vectors, the verdict tables, the Study 011 census, the claim source and the
  five retained mirror attempts. The five untouched lifecycle sentences are
  correctly static; the round-count repair is total; **no registered act moves a
  manifest-covered byte**; no fourth output-path instance and no rendering
  defect remain
- The reviewer's statement of what freezing here would cost: **"the scientific
  outputs would not overclaim their data, but the tree would overclaim durable
  test coverage of two mandatory pre-call gates"**

### Prompt (verbatim)

```
You are performing a verification review — round 16 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 60b1445 on branch study-012-perturbation

**The question in front of you is: is this tree ready to freeze?** A clean verdict is a real outcome, and saying so plainly is the most useful thing you can do if the bytes earn it. Manufacturing a finding to justify the round would be worse than finding nothing.

**What round 15 found, and what it means for where you should look.** Round 15 answered NOT READY on one blocking finding, and the maintainer's verification changed its character: it was filed as a fourth livelock, but the suite is green at every lifecycle stage, so the harm was **silent coverage loss** rather than a red suite. The decisive fact was established by doing it: with `batch.require_golden()`'s preflight call removed, the whole suite still passed, 297 of 297 — nothing anywhere caught deletion of §3.2's golden gate from the batch path, because the stand-in registry inherited a live `golden.sha256` and a live `isolationNegative.assent` while both golden cases asserted only `exit 1`.

Round 15's dispositions changed these things. **Press hardest on the first two, and prefer doing to reading — the last two rounds each turned on a fact that only surfaced when someone executed the check rather than reasoning about it:**

- The batch fixture now writes all four post-freeze registry members explicitly, advances them only through fixture acts, and its cases assert the **named** refusal rather than a bare exit code. **Judge whether the coverage hole is really closed**: can you still remove a registered gate from the batch path and keep the suite green? Try it against gates other than the golden one. And check the sweep's claim that `stand_in_registry` was the only fixture inheriting a lifecycle member.
- The manifest-invariance test now scans the writing modules and binds every destination they name to the exclusion list, rather than hand-modelling destinations. Its docstring states four things the scan does not reach (it reads rather than runs; it does not follow a parameter to its callers; it is Python-only; it fails closed). **Judge whether that disclosure is complete and honest**, and whether a writer could still add an unexcluded output the scan would miss.
- A twenty-round ceiling inside the round-13 livelock fix would have raised `IndexError` at round 21 and forced a covered-byte edit — a latent instance of the class inside the fix for that class. Check the repair, and check the rest of that fix for further instances.
- CI ran `integrity.py` without `PYTHONSAFEPATH=1`, so the registered C1 step had refused before verifying since round 10, with the pytest step skipped behind it; the workflow is now corrected. **Note that this was never caught by fifteen rounds because every round ran the ceremony locally, where it passes.** Ask what else the registration asserts about environments no round has actually exercised.
- Two markdown repairs no finding covered were taken because this was the last free moment: C10's unmatched delimiter, and a `+ ` opening a continuation line in [D-5] that splits the paragraph under CommonMark. **Sweep the registration for any other rendering defect that changes what a reader sees**, since this is the last round before a freeze that makes them permanent.

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Round 15's five dispositions — the priority of this round.** Judge each against the bytes:

- **Is the lifecycle-staleness class actually closed?** Sweep every manifest-covered file yourself for any sentence, status, count, date or claim that is true now and false after the freeze, after the batch runs, or after publication. The maintainer's sweep found eleven prose hits and two executable ones; find what it missed, in either direction. Say explicitly whether any *further* covered byte is a function of the study's own stage.
- **Are the five untouched sentences correctly classified?** They were judged registration-time statements that must not be "fixed". If any is in fact a live self-updating value, that is a finding; if any was fixed that should not have been, that is also a finding.
- **Do the three new tests do what they claim?** The manifest-invariance test, the lifecycle-status lint, and the two rewritten stage-dependent tests. Would each fail if the property it names stopped holding? The lint is a blacklist and says so — judge whether its registered statement of its own strength is honest.
- **Verify the freeze and run really move no covered byte.** Take the registry's four lifecycle members and `freeze.excluded`, and satisfy yourself that no registered act — freeze, golden capture, C7, the 150-call batch, scoring, publication — changes anything the manifest covers. This is the property rule 3's termination depends on, so check it from the registration rather than from the maintainer's summary.

**2. The defect class itself, at every act.** Three acts have been repaired. Sweep for a fourth: take every registered act in the study's lifecycle — the freeze, the golden capture, §6 C7, the 150-call batch, scoring, `--emit-records`, publication, the correction, `DEVIATIONS.md`, and the recording of a review round — and satisfy yourself from the registration and the exclusion list that each moves only carrier or excluded bytes. If any act still moves a covered byte, that is this round's blocking finding. Say explicitly whether the class is now closed or whether you found a fourth instance.

**3. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 13 found their sharpest results in the study rather than the harness. Read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**4. The suite, at 301, and the residuals the record names.** The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are covered only for `tree_manifest()`; `_write_outputs()` is pinned only at its override gate; `_emit_records()` and `_check_records_target()` have no direct suite coverage, which is why the record destination went unmodelled for fourteen rounds; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's Q sentence has no test; §2.2's two digest cells are hand transcriptions no assertion covers; and after README step 5 the tree stops producing the C7 refusal message with no test asserting it. Confirm each is as described, then ask what **else** the suite asserts less than it appears to.

**5. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**6. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**7. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: 60b1445`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R16-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(Absolute paths in the reviewer's markdown links are rendered as the
`file:line` anchors they point at; no other byte is altered.)

1. **The batch freeze gate is silently removable — blocking.** Record: PREREGISTRATION.md:3476 requires the freeze digest before calls. Code: batch.py:733 calls the gate correctly, but test_batch.py:586 asserts only exit 1 while C7 remains unmet. In an isolated, internally re-pinned copy, deleting only this call left the entire suite green: **301 passed, 9 subtests passed**. The test must satisfy later gates and assert the named freeze refusal.

2. **The batch registry-consistency gate is also silently removable — blocking.** Record: PREREGISTRATION.md:932 fixes N=30 and PREREGISTRATION.md:1333 requires registry enforcement per run. Code: batch.py:761 calls `check_registry()`, but its unit tests call that function directly; the only command-path case, test_batch.py:541, again accepts an unnamed exit 1 supplied by C7. Removing only the preflight call, with internal digests re-pinned and integrity green, also produced **301 passed, 9 subtests passed**. This needs a named command-path refusal and mutation-to-red coverage.

3. **The writer scan is neither exhaustive nor fail-closed as recorded — should-fix.** Record: test_manifest.py:499 claims every file-creating write is found and unresolved writers fail closed. Code: its finite vocabulary at line 347 silently ignores unknown APIs, aliases, nonliteral `open()` modes, async or non-function scopes, and helper-body writes. It already misses batch.py:464 using `tempfile.mkstemp()` for an unexcluded `arms/BATCH.json.*.partial`. This is not currently a covered-byte mover because that file is transient and untracked. A complete repair must inventory all creation APIs and unresolved calls, move temporary output under a dedicated exclusion, or narrow the test’s claim honestly.

4. **The fixture-inheritance sweep claim is false — should-fix.** Record: PREREG-REVIEW.md:3155 says the batch `stand_in_registry` was the only fixture inheriting any lifecycle member. Code: test_admission.py:2687 copies live PINS and overwrites only three of the four members, inheriting `freeze.treeManifestSha256`. That member is inert in the current scorer path, so no expectation presently changes by stage. The fixture should explicitly write all four members and receive the same guard as the batch fixture.

5. **The D-19 operating-characteristic check implements only half the registered rule — nit.** Record: PREREGISTRATION.md:216 defines drift as four classes below HIGH **or any class LOW**. Code: score_rates.py:1180 and line 1414 compute only the first limb, while test_verdict_parity.py:1409 checks only four-decimal rendering. The omitted probability is about \(10^{-31}\) at N=30, so the published `0.0041` and every outcome remain unchanged.

The scientific content otherwise re-derived cleanly: all 20 artifacts and prompt equations, six semantic classes and 280-cell grids, schedule balances, interval vectors, verdict tables, Study-011 census, claim source, and five retained mirror attempts reconcile. The five untouched lifecycle sentences are correctly static; the round-count repair is total; no registered act currently moves a manifest-covered byte; no fourth output-path instance or rendering defect remains. Golden and C7 gate deletion now turn the suite red, but the broader gate-wiring coverage class is still open.

Official verification exited 0. The first official suite run was **301 passed, 54,050 warnings, 9 subtests passed**. The worktree remained clean. My independent 86-entry manifest recipe produced the same digest as `integrity.tree_manifest()`.

If frozen tomorrow, the scientific outputs would not overclaim their data, but the tree would overclaim durable test coverage of two mandatory pre-call gates.

Overall verdict: **NOT READY TO FREEZE** — findings 1 and 2 are blocking.

Reviewed commit: 60b1445

Tree manifest (my computation): e4f15954c87373e2f885bde8ea0382d78feb208c9157a5f5244a0c5d501369db

CODEX-012-R16-DONE

### Dispositions

All five findings **ACCEPTED**, all five independently confirmed — and the
verification found the blocking pair to be **far larger than filed**. That
enlargement, not the two named gates, is what this round is about.

**Findings 1 and 2 are one defect, and the honest measurement is worse than the
report.** The reviewer found two pre-call gates in `batch.py` whose call could be
deleted with the suite still green. The verification enumerated the whole
pre-call region and mutated every gate in isolation, re-pinning digests each time
so `integrity.py` stayed green and nothing was masked by the port chain. The
result: **ten of fourteen gates were silently removable**, and `require_freeze`
could be neutered at **all five of its call sites at once** with the suite
unmoved at 301 passed. §7 registers the freeze digest as a precondition of the
calls; nothing in the pinned suite could tell whether that sentence was still
true.

**Why this kept happening is the part worth recording.** This is the same class
repaired per-instance three times — the class-3 conjunct, then class-4, then
round 15's golden gate — and each time the next round found it one gate over.
Round 15's sweep is the clearest diagnosis: it swept for *fixtures inheriting
lifecycle members*, which was the shape of the instance in front of it, and not
for *gates without named coverage*, which was the shape of the defect. A sweep
scoped to the instance finds instances.

So the repair is a **derived ledger**, not a fourth hand-written test. The gate
set is parsed out of `batch.py` by AST — the callees of `preflight()` and of each
command entry that can raise, plus `preflight`'s own inline refusals — and three
tests hang off it: **A**, that the derived set equals the ledger's keys, so a new
gate or a newly-reaching command fails *by name*; **B**, that each ledgered
refusal substring actually occurs in a `raise` literal inside that gate, so a
silent rewording fails; and **C**, that driving the real command with every other
gate satisfied and this one broken exits 1, names the refusal, spends no call,
writes no artifact — and exits 0 once satisfied, so an inverted predicate cannot
pass. A `SATISFY` ladder carries its own completeness assertion, so a new gate
must arrive with a way to satisfy it. The mechanism proved itself during the work:
a new gate added for finding 3 arrived as a named test-A failure.

**Measured, not asserted.** All ten previously silent gates now turn the suite
red — 34 mutant runs, each in its own full-tree copy with digests re-pinned and
integrity verified at 0. The whole-function neuters go red too, including the
five-call-site `require_freeze` case that was the sharpest escalation.

**And the limits are registered rather than glossed**, because an overclaimed
closure is precisely this round's subject. The ledger is **author-visible, not
author-proof**: deleting a gate, its ledger row *and* its ladder entry is green —
what it converts is a silent deletion into an edit of the two tables whose only
job is to record the gate set. It says nothing about a gate being *correct*
beyond the admitting half. It sees only statically resolved calls in `batch.py`,
so the wrapper's own gates are outside it. **Thirty-one of fifty-seven derived
cells are residual** — named, reasoned, caught by A and the ladder, but with no
message pinned and no behaviour driven. And **`score_rates.verify_preconditions`
was deliberately not mirrored**: its ordered table is still hand-written and
retains the identical silent-omission property, with three scorer gates measured
as silently removable. That is disclosed in the new class's own docstring so the
next round inherits it as a named gap instead of rediscovering it as a defect.

**Finding 4 is a false sentence in my own round-15 record**, and it is the second
time this sequence that a sweep I reported was narrower than I claimed. The
record said `stand_in_registry` was the only fixture inheriting a lifecycle
member. It was not: a second helper inherited `freeze.treeManifestSha256`. Inert
— no driver or scorer path reads it from a supplied registry, so no expectation
changed by stage — but the claim was wrong. Both helpers now derive from
`POST_FREEZE_MEMBERS` and write every member, and a source rule holds any future
stand-in to the same discipline.

**Findings 3 and 5.** The writer scan claimed to find every file-creating write
while its vocabulary was finite and silently ignored what it did not recognise —
and it had a real miss, a `tempfile.mkstemp` temporary under `arms/`. It now fails
closed on anything unclassified, walks module and class and lambda scopes, and
the temporary is a named exclusion written through an `O_EXCL` path with a
preflight gate refusing a stale residue. A false §8 sentence, that nothing in the
tree is `.gitignore`d, was corrected in the same pass. And [D-19]'s drift rule had
two limbs registered and one implemented; both are now computed exactly, with the
second worth about 1e-31 at N = 30, so no published figure moves — a false
registered sentence in a document about to be frozen permanently, which is the
only reason a nit of that size was worth the round.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **309 passed** with 123 subtests (301 + 8, and the subtest count is the
ledger doing its work); tracked status clean; `arms/`, `analysis/`, `CLAIM.md`
and `MIRROR-AGREEMENT.md` untouched. The post-disposition tree manifest, the
maintainer's computation, is
`fb24e3b802fa948dea916f6aff1711a84f1b699236d7fb0c0da090af4e433927` — round 17
attests it, and under §2.10 rule 3 that round is required, because these
dispositions changed bytes.

One residual found while cascading and left open: `PREREGISTRATION.md`'s
restatement of `PORTS.md`'s own digest is checked by nothing, and was re-pinned
by hand after a cascade script missed it. The §2.2 destination-digest table has
the same property. Cheap to close, not closed here, and named so it is inherited
rather than rediscovered.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 16 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## Round 17 — the mechanism against scope-overclaim, overclaiming its scope

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-10; drafting as recorded in rounds 1-16
- Reviewed commit: `62054fd`
- Tree manifest, the reviewer's computation:
  `fb24e3b802fa948dea916f6aff1711a84f1b699236d7fb0c0da090af4e433927` — 86
  entries, matching the maintainer's own computation
- Runs: two commissionings, the first discarded. It died at the planning stage
  on a Codex-internal error (`failed to renew cache TTL: missing field
  base_instructions`) having spent nothing — a different failure from round 16's
  three capacity deaths, and neither a classifier refusal nor anything the study
  did. The transcript is retained beside the completed one
- **Verdict: NOT READY TO FREEZE**, on two blocking findings
- Reviewer's verification first: integrity exit 0; 309 passed, 123 subtests;
  worktree clean. **Round 16's ledger performed exactly as claimed within its
  reach** — deleting all fourteen original preflight sites, two sampled residual
  sites, and whole-function neuters of all five gate functions each turned it
  red, and the author-visible limitation the record registered was confirmed
  exact. The scientific registration re-derived cleanly once more: all twenty
  arm artifacts and prompt equations, the six classes and 280-cell grids, the
  schedule balances, §3.3's partition, the interval vectors, the
  level/contrast/decision tables, C1-C10, the claim source and the five retained
  mirror attempts
- The reviewer's statement of the cost of freezing here: **"the scientific
  results would not overclaim the data, but the tree would overclaim lifecycle
  immutability and completeness of its batch-gate ledger"**

### Prompt (verbatim)

```
You are performing a verification review — round 17 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 62054fd on branch study-012-perturbation

**The question in front of you is: is this tree ready to freeze?** A clean verdict is a real outcome, and saying so plainly is the most useful thing you can do if the bytes earn it. Manufacturing a finding to justify the round would be worse than finding nothing.

**What round 16 found, and what the maintainer did about it.** Round 16 reported that two mandatory pre-call gates in `batch.py` could have their call deleted with the whole suite still green. Measuring the whole pre-call region found it was **ten of fourteen**, and that `require_freeze` could be neutered at all five of its call sites at once with the suite unmoved at 301 passed. §7 registers the freeze digest as a precondition of the calls, and nothing in the pinned suite could tell whether that was still true.

The maintainer's diagnosis, recorded in the round-16 dispositions, is that this class had been repaired per-instance three times and kept reappearing one gate over, because each sweep was scoped to the shape of the instance rather than the shape of the defect. So round 16's repair is a **derived ledger**: the gate set is parsed out of `batch.py` by AST, and three tests hang off it — the derived set must equal the ledger's keys (a new gate fails by name), each ledgered refusal substring must occur in a real `raise` inside that gate (a rewording fails), and each gate is driven on the real command path with every *other* gate satisfied, so it must refuse by name, spend no call, and admit once satisfied.

**Your first job is to attack that mechanism the way round 16 attacked the gates — by doing, not reading.** Round 16's result came from mutating and measuring, and the last three rounds have each turned on a fact that only surfaced when someone executed the check. So:

- **Can you still remove a gate and keep the suite green?** Try it. Try gates the ledger drives, gates it marks residual, and the whole-function neuters. Try adding a plausible new gate and see whether it is really caught by name.
- **Is the ledger's own honesty accurate?** The maintainer registered three limits explicitly: it is *author-visible, not author-proof* (deleting a gate plus its ledger row plus its ladder entry is green); **31 of 57 derived cells are residual** — named and reasoned but not behaviourally driven; and `score_rates.verify_preconditions`'s equivalent table is **deliberately not mirrored** and is stated to retain the same silent-omission property, with three scorer gates measured as removable. Verify each of those three claims. If any is understated, that is a finding. If the scorer's hole is worse than disclosed, say so.
- **Was anything overclaimed?** The round-16 record says all ten previously-silent gates now turn the suite red. Check it.

Then judge the other three round-16 dispositions: the writer scan that now fails closed on anything it cannot classify (and the `O_EXCL` temporary and its new preflight gate), the stand-in-registry rule derived from `POST_FREEZE_MEMBERS`, and [D-19]'s second limb.

**One residual the maintainer named and did not close**, so it is yours to weigh rather than rediscover: `PREREGISTRATION.md`'s restatement of `PORTS.md`'s own digest is checked by nothing, and the §2.2 destination-digest table has the same property — both are hand transcriptions no assertion covers.

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Round 16's five dispositions — the priority of this round, and the attack described above comes first.** Judge each against the bytes:

- **Is the lifecycle-staleness class actually closed?** Sweep every manifest-covered file yourself for any sentence, status, count, date or claim that is true now and false after the freeze, after the batch runs, or after publication. The maintainer's sweep found eleven prose hits and two executable ones; find what it missed, in either direction. Say explicitly whether any *further* covered byte is a function of the study's own stage.
- **Are the five untouched sentences correctly classified?** They were judged registration-time statements that must not be "fixed". If any is in fact a live self-updating value, that is a finding; if any was fixed that should not have been, that is also a finding.
- **Do the three new tests do what they claim?** The manifest-invariance test, the lifecycle-status lint, and the two rewritten stage-dependent tests. Would each fail if the property it names stopped holding? The lint is a blacklist and says so — judge whether its registered statement of its own strength is honest.
- **Verify the freeze and run really move no covered byte.** Take the registry's four lifecycle members and `freeze.excluded`, and satisfy yourself that no registered act — freeze, golden capture, C7, the 150-call batch, scoring, publication — changes anything the manifest covers. This is the property rule 3's termination depends on, so check it from the registration rather than from the maintainer's summary.

**2. The defect class itself, at every act.** Three acts have been repaired. Sweep for a fourth: take every registered act in the study's lifecycle — the freeze, the golden capture, §6 C7, the 150-call batch, scoring, `--emit-records`, publication, the correction, `DEVIATIONS.md`, and the recording of a review round — and satisfy yourself from the registration and the exclusion list that each moves only carrier or excluded bytes. If any act still moves a covered byte, that is this round's blocking finding. Say explicitly whether the class is now closed or whether you found a fourth instance.

**3. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 13 found their sharpest results in the study rather than the harness. Read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**4. The suite, at 309 (123 subtests), and the residuals the record names.** The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are covered only for `tree_manifest()`; `_write_outputs()` is pinned only at its override gate; `_emit_records()` and `_check_records_target()` have no direct suite coverage, which is why the record destination went unmodelled for fourteen rounds; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's Q sentence has no test; §2.2's two digest cells are hand transcriptions no assertion covers; and after README step 5 the tree stops producing the C7 refusal message with no test asserting it. Confirm each is as described, then ask what **else** the suite asserts less than it appears to.

**5. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**6. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**7. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: 62054fd`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R17-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(Absolute paths in the reviewer's markdown links are rendered as the
`file:line` anchors they point at; no other byte is altered.)

1. **The registered record-emission surface can move manifest-covered bytes — blocking.** Record: PREREGISTRATION.md:1381 permits `--emit-records DIR` anywhere outside `arms/`, while README.md:9 says no registered act moves covered bytes. Code: _check_records_target():5076 rejects only population overlap, and _emit_records():5155 writes below any other target; PINS.json:159 excludes only `records/`. Another in-study sibling is therefore accepted but becomes covered when published/staged. test_manifest.py:199 checks only README’s literal destination. Restrict the interface to canonical `records/`, or reject every in-study target not wholly covered by an exclusion. This is the fourth lifecycle-output instance; the class is not closed.

2. **The derived batch-gate ledger omits command-helper gates — blocking.** Record: PREREGISTRATION.md:1335 and test_batch.py:2897 say a gate added to a command entry becomes a named ledger failure. Code: gate_functions():2245 derives helpers only from `preflight()`; _sites_in():2314 ignores any other helper name. Current omitted refusal-capable pre-call helpers include `load_ledger`, `verify_prefix`, `reconcile_ledger`, `capture_slots`, and `require_distinct_sessions`. In a re-pinned disposable copy, adding a plausible module-level gate only to `run_batch()` left the derived set unchanged at 58 and all `PreCallGates` tests green: 5 passed, 114 subtests. The derivation must traverse refusal-capable calls from every command entry up to its first invocation.

3. **The scorer’s silent-omission surface is broader than the three measured examples — should-fix.** Record: PREREG-REVIEW.md:3398 discloses a hand-written table and three removable scorer gates. Code: verify_preconditions():3447 has many more gates, while test_admission.py:2563 covers four staged refusals only. I jointly neutered eight distinct checks—mirror pin, order object, Williams row, block orders, equal arm allocation, N, slot count, and arm set—then re-pinned the copy. Integrity exited 0 and the full suite remained **309 passed, 123 subtests**. The disclosure is directionally honest but materially incomplete.

4. **The writer scan still does not fail closed on every shape it claims — should-fix.** Record: test_manifest.py:700 and PREREG-REVIEW.md:3413 claim unclassifiable writers fail closed. Code: _flag_names():451 treats an unresolved flags variable as readable and therefore non-creating unless its spelling contains `O_CREAT`; import_offenders():515 misses ordinary assignment aliases of modules and writer functions. Current writer sites reconcile correctly, including the fixed `O_EXCL` ledger temporary, but the stated regression guarantee is too strong.

5. **The stand-in-registry rule recognizes syntax without proving the lifecycle members are written — should-fix.** Record: PREREGISTRATION.md:1331 says future stand-ins cannot inherit lifecycle values. Code: stand_in_offenders():893 exempts a builder upon merely seeing any loop over `POST_FREEZE_MEMBERS` or any call whose name ends in `stand_in_registry`, without proving the loaded object is rewritten or that the result is used. A direct return without assignment is skipped too. The current shared constructor and both current builders are correct and stage-independent; the source rule is not as strong as recorded.

6. **D-19’s two-limb helper is tested, but its public call-site is not — should-fix.** Record: PREREGISTRATION.md:239 says tests pin both limbs. Code: score_rates.py:1459 currently calls the correct helper, but converts it to float at line 1478. test_verdict_parity.py:1421 proves the helper exactly; its call-site assertion compares floats that are identical for the one- and two-limb forms. Restoring the old one-limb expression at line 1459 would therefore remain green. Bind the call with a visible sentinel or an AST assertion.

7. **D-19’s new magnitude sentence is false at N=25 — nit.** Record: PREREGISTRATION.md:231 says the second limb adds less than \(10^{-30}\) “at either N.” Exact increments are \(1.1763955632844822\times10^{-27}\) at N=25 and \(1.0042175564733368\times10^{-31}\) at N=30. The implementation is correct; all printed figures and IEEE values remain unchanged.

8. **The residual accounting is stale in conservative directions — nit.** PREREG-REVIEW.md:3396 records 31 residual cells of 57; the actual derived ledger is **58 cells: 30 residual, 25 command-driven, 3 preflight-driven**. It overstates, rather than understates, the residual. The older statement that `normalized_pins()` is exercised only through `tree_manifest()` is also no longer literal: test_review_status.py:142 calls it directly for the lifecycle projection lint.

The round-16 ledger otherwise performed as claimed: deletion of all 14 original preflight sites, two sampled residual sites, and whole-function neuters of all five gate functions turned its tests red. Its author-visible limitation is exact: deleting a gate together with its ledger and ladder entries left the full suite at 309 passed.

The scientific registration re-derived cleanly: all twenty arm artifacts and prompt equations, six classes and 280-cell grids, schedule balances, §3.3 partition, interval vectors, level/contrast/decision tables, C1–C10, claim source, and five retained mirror attempts reconcile. The five untouched lifecycle sentences are correctly static. The hand-transcribed §2.2 and own-PORTS digests are currently correct, though still unasserted. The other named residuals are accurately bounded, subject to finding 8.

Official verification exited 0. The first official suite run was **309 passed, 70,760 warnings, 123 subtests passed in 418.71s**. The original worktree remained clean. My independent 86-entry manifest computation matches `integrity.tree_manifest()` exactly.

If frozen and run tomorrow, the scientific results would not overclaim the data, but the tree would overclaim lifecycle immutability and completeness of its batch-gate ledger.

Overall verdict: **NOT READY TO FREEZE** — findings 1 and 2 are blocking.

Reviewed commit: 62054fd

Tree manifest (my computation): fb24e3b802fa948dea916f6aff1711a84f1b699236d7fb0c0da090af4e433927

CODEX-012-R17-DONE

### Dispositions

All eight findings **ACCEPTED**, all eight independently confirmed. This round's
subject is not any of the eight. It is that **three rounds running, this record
has claimed a mechanism reached further than it did** — and round 16's ledger,
built expressly to end that, was itself an instance.

**Finding 2 is the one that matters.** Round 16's record says a gate added to a
*command entry* becomes a named ledger failure. The derivation walked
`preflight()` only. Round 17 added a plausible gate to `run_batch()`: derived set
unchanged, all `PreCallGates` tests green. Five refusal-capable helpers sat
outside its reach entirely. So the fix for "the sweep was scoped to the instance"
was itself scoped one level too narrow, and its record described the wider scope
it did not have. The derivation now runs from **every command entry and from
`main()`**, and the measured result is the honest form of what round 16 asserted:
the ledger goes from **58 cells to 82** — 40 command-driven, 3 preflight-driven,
39 residual — over a gate set that grew from 5 functions to 14. Adding that same
`run_batch` gate now fails test A by name.

**Finding 1 is the same disease at the output surface, and its fourth instance.**
`--emit-records DIR` accepted any target outside `arms/`; only `records/` is
excluded, so pointing it at an in-study sibling moved the manifest — demonstrated,
not argued. The class was declared closed after round 14 and again after the
pre-round-14 sweep. The repair is therefore **general rather than fourth**: a
single lawful-destination rule — outside the study, or wholly inside a registered
exclusion tree — applied to every operator-supplied destination at once,
including the two `--out` flags nobody had asked about.

**And the verification caught the fix reproducing the defect it fixes.** Its
steps 1-4 add a real runtime gate and leave the suite at 309 passed — meaning the
new gate could itself have been deleted with the suite green, which is round 16's
finding exactly. Its own words: *"the 'still 309' is the point, not a
reassurance."* So every new check in this round ships with a case that turns red
when the check is removed, proved by mutation: each of the three destination call
sites, the D-19 call site, the scorer's mirror-pin gate, the writer-scan limbs,
the stand-in escape rule, and a deliberately miscounted census.

**Finding 6 is round 16's shape once more** — the function covered, the wiring
not. [D-19]'s two-limb helper was pinned exactly while its call site compared
floats identical under both forms, so restoring the one-limb expression stayed
green. It is now bound by sentinel, and so is round 11's row-5 product form.

**Where I narrowed instead of extending, and why**, since the standing rule this
round was to prefer reach. Three places, each recorded with its reason. The
reviewer's "transitive closure" for finding 2 reaches fourteen functions and
double-counts six already owned by a ledgered caller; depth-one-per-host is the
symmetric rule and is registered *with its depth* rather than left implied. A
proposed order-of-magnitude assertion for finding 7 would have passed vacuously —
a `%.0f` ratio string is not distinctive in a 300 KB document — so the magnitudes
are bound per N and per layer instead. And finding 5's escape rule initially fired
on a helper that returns a string; it is narrowed back to the three registered
ways out, with the false positive recorded in the rule's own limits rather than
tuned away silently.

**The corrections to this record, stated plainly because they are the round's
substance.** Round 16 wrote "thirty-one of fifty-seven residual cells"; the true
figures at that commit were **30 of 58**, and are **39 of 82** now — and the count
is now derived by a census test rather than transcribed. Round 16 wrote that the
derivation covers "the callees of `preflight()` and of each command entry that can
raise"; that sentence was false when written and is true now. Round 16 disclosed
"three scorer gates measured as silently removable"; the surface is **twelve**, and
the reviewer neutered eight jointly with the suite still green. The scorer now
carries its own 25-cell ledger sharing one derivation helper with the driver's, so
a third site is cheap. Commit `62054fd`'s message carries the same wrong pair and
cannot be corrected; this entry is the correction.

**What remains out of reach, measured rather than estimated.** Twenty-one of the
scorer's twenty-five cells are residual — named and omission-proof, but not
driven — including the gate §2.10 leans on and eight C7 rows whose shared needle
can name none of them. `score()`'s other pre-read region, roughly twenty more
sites, is named and uncovered. The two new `--out` gates are attribute-spelled and
so derive no ledger cell; they are held by behavioural pairs instead, and the
ledger's limits say so. Gate depth is one. The pre-call bound is textual, not
executional. And `--emit-records controls/recapture` is **accepted** — that tree is
excluded, so it moves no covered byte; refusing it would be a second rule needing
its own registration, and it is left accepted deliberately.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **315 passed** with 177 subtests (309 + 6, and the subtest growth is the two
ledgers working); tracked status clean; `arms/`, `analysis/`, `CLAIM.md` and
`MIRROR-AGREEMENT.md` untouched. The post-disposition tree manifest, the
maintainer's computation, is
`cf9c57383d9108ab79965c2943e06762814df98ebaf430de657bbb63d2a6e821` — round 18
attests it, and under §2.10 rule 3 that round is required, because these
dispositions changed bytes.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 17 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |

## The stopping rule, registered before round 18 was commissioned

**Registered 2026-08-10, over commit `477b702`, with the tree manifest at
`cf9c57383d9108ab79965c2943e06762814df98ebaf430de657bbb63d2a6e821` — before
round 18 was commissioned and therefore before its findings were known.** The
ordering is the point and it is checkable: the commit carrying this section
precedes the commit carrying round 18's record in this repository's history.

**The rule. The freeze binds to the manifest of the first review round that
returns no finding the reviewer assigns the severity `blocking`.** Severity is
the reviewing round's to assign, not the maintainer's to argue down; a round
that returns should-fix and nit findings and no blocking finding ends clean for
this purpose.

**At that round, non-blocking findings are recorded as accepted residuals and
are not fixed.** This is not laxity, it is the only terminating form: a
disposition changes bytes, §2.10 rule 3 answers a covered-byte change with
another round, and that round's own dispositions would do the same. Rounds 13
through 15 made the record and the registry carriers precisely so the closing
acts — writing this record, filling `freeze.preregistrationSha256` and
`freeze.treeManifestSha256` — move no covered byte. The freezing round's
attested manifest is therefore still the manifest of the frozen tree.

**Why this bar rather than zero findings.** Nine rounds ran between 2026-08-08
and 2026-08-10 with blocking counts 2, 4, 1, 0, 1, 2, 1, 2, 2. Across all nine,
every independent re-derivation of the scientific instrument reconciled — the
twenty arm artifacts and prompt equations, the six classes and 280-cell grids,
the schedule balances, §3.3's partition, the interval vectors, the level,
contrast and decision tables, C1-C10, `CLAIM.md` against its source, and the
five retained clean-room mirrors — and every round from 12 onward said in its
own words that the study's results would not overclaim their data if frozen.
What kept failing was one layer up: whether the suite proves the harness's gates
work, and whether this record described the suite's strength accurately.

That is a real defect class and it is also unbounded. Round 17 demonstrated why:
the mechanism built in round 16 to end scope-overclaim was itself found to
overclaim its scope. "This check does not reach as far as its docstring says" is
available at every level, including the checks that check the checks, so a
zero-findings bar has no reason to terminate by iteration.

**Two costs of not stopping, recorded so the choice is legible.** The policy
family's clause wording, country codes and outcome vocabulary have been public
in this repository since 2026-08-06. §9 registers contamination as a bound on
interpretation: if arm E maintains coverage, "the author recognises this policy
family" competes with "the author derives boundaries," and that competitor
strengthens with every day the corpus stays public and unread. Polishing
verification strength while the study's central ambiguity widens is the wrong
trade. And each round costs roughly 400,000 to 650,000 reviewer tokens plus its
verification; rounds 16 and 17 together needed six commissionings because of
vendor failures unrelated to the study.

**What is being accepted, named rather than implied.** The residuals stand as
this record measures them: 21 of the scorer's 25 ledger cells derived and
omission-proof but not behaviourally driven, including the gate §2.10 leans on;
`score()`'s other pre-read region, roughly twenty sites, named and uncovered;
the driver ledger's gate depth of one and its textual rather than executional
pre-call bound; both ledgers author-visible rather than author-proof; the writer
scan Python-only; `verify_mirror2()`, `verify_tree()` and `normalized_pins()`
without full direct tests; §2.2's digest restatements checked by nothing; and
§4.6's reading keyed on levels where the scorer keys on contrasts, registered as
conservative. A reader who objects to freezing over any of these can object to a
sentence that is written down.

**If round 18 returns a blocking finding**, it is dispositioned as every round
has been and the rule carries to round 19 unchanged. **If a blocking finding
touches the arms, the endpoints, the decision rules or the claim** — the
scientific instrument rather than the verification of it — this rule does not
apply to it and the study does not freeze on that round whatever the count says.

## Round 18 — the first round run under the registered stopping rule

- Reviewing model: OpenAI Codex CLI v0.145.0, model `gpt-5.6-sol`, reasoning
  effort ultra, 2026-08-10; drafting as recorded in rounds 1-17
- Reviewed commit: `8e93689`
- Tree manifest, the reviewer's computation:
  `cf9c57383d9108ab79965c2943e06762814df98ebaf430de657bbb63d2a6e821` — 86
  covered files plus the normalized registry entry, matching the maintainer's
  own computation
- Runs: one review run, completed; no run discarded, no classifier refusal
- **This is the first round commissioned under the stopping rule registered
  above.** Its brief told the reviewer what its severity assignments now cost —
  that a blocking finding sends the study round again and its absence freezes
  the tree — and named both failure modes: softening a genuine blocker because
  the process is tired, and inflating a should-fix to appear rigorous or to keep
  the process alive. The instruction was to call each finding what it is
- **Verdict: NOT READY TO FREEZE**, on one blocking finding. **The reviewer
  applied the rule correctly and said so in its own verdict line**: the blocker
  "is not a scientific-instrument finding, so the ordinary stopping rule carries
  to round 19"
- Reviewer's verification first: integrity exit 0; 315 passed, 177 subtests;
  worktree clean. Both censuses the round-17 record published reconciled
  independently — driver 82 = 40 + 3 + 39 over 14 gate functions, scorer
  25 = 4 + 21. The lifecycle sweep found no further covered byte whose value
  depends on stage. The scientific instrument re-derived cleanly once more: the
  six semantic classes and five 280-cell grids, arm-D's substitution, twenty
  artifact pins and prompt equations, the schedule balances, §3.3's partition,
  the intervals, the level/contrast/decision tables, C1-C10, `CLAIM.md`'s
  provenance and all five retained mirror attempts. **"No blocking finding
  touches the arms, endpoints, decision rules, or claim."**

### Prompt (verbatim)

```
You are performing a verification review — round 18 — of Study 012, a preregistered research study in a repository we own and maintain. This is documentation-and-code auditing of our own work before we freeze it and run it. Prior rounds' records, findings and maintainer dispositions are in `PREREG-REVIEW.md` in the study directory.

Repository root: <worktree root>
Study directory: <worktree root>/studies/012-policy-perturbation
Reviewed commit: 8e93689 on branch study-012-perturbation

**This round may be the last one.** A stopping rule was registered before this round was commissioned — you can read it at the end of `PREREG-REVIEW.md`, and its commit precedes this one in the history. It says the freeze binds to the manifest of the first round that returns **no finding the reviewer assigns severity `blocking`**, and that at that round the non-blocking findings are recorded as accepted residuals rather than fixed, because fixing them would change bytes and require yet another round.

**What that means for you, stated plainly so it cannot distort your judgment.** Your severity assignments now carry consequence: a blocking finding sends the study round again, and its absence freezes this tree. Two failure modes follow, and they are opposite. Do not soften a genuine blocking finding because the study is tired — nine rounds of care are worth nothing if the tenth waves something through. And do not manufacture or inflate one to keep the process going or to appear rigorous; a should-fix labelled blocking is as much a misreport as the reverse, and it would spend hundreds of thousands of tokens and delay a study whose contamination bound worsens with time. **Call each finding what it is.** If nothing is blocking, say so plainly — that is a real outcome and this round is the one where it counts.

The rule also carves out one exception you should know: if a blocking finding touches the **arms, the endpoints, the decision rules or the claim** — the scientific instrument rather than the verification of it — the stopping rule does not apply and the study does not freeze regardless of counts. So weigh that class especially carefully.

**What round 17 changed.** Its subject was that three rounds running, the maintainer's record claimed a mechanism reached further than it did — and round 16's gate ledger, built to end exactly that, was itself an instance. The repairs: the ledger derivation now runs from every command entry and from `main()`, growing from 58 cells to a measured 82 (40 command-driven, 3 preflight, 39 residual) over a gate set grown from 5 functions to 14; a general lawful-destination rule (outside the study, or wholly inside a registered exclusion tree) now gates every operator-supplied destination including two `--out` flags; the scorer carries its own 25-cell ledger sharing one derivation helper; the writer scan's fail-closed holes and the stand-in rule's syntax-only exemption are closed; and [D-19]'s call site is bound by sentinel where only its helper had been pinned. Every new check in that round shipped with a mutation that turns it red — because the verification caught the first draft of the destination gate leaving the suite green, which was round 16's own defect reproduced by its fix.

**Attack all of that by doing, not reading** — the last four rounds each turned on a fact that only surfaced when someone executed a check. Can you still add a gate that no ledger names? Remove one and keep the suite green? Point a registered destination flag somewhere that moves the manifest? Is the measured census (82 cells, 39 residual; scorer 25 cells, 21 residual) accurate? And the standing target across five rounds: **a test that passes for a reason unrelated to its subject.**

## How to work

Read the files and reason about them. Run the study's own test suite and its own verification command. You may write small scratch scripts **outside** the repository (under your working directory) to recompute a digest, re-derive a table, or check arithmetic independently. Driving the scorer's own public API on synthetic per-class integers is ordinary use of the study's instrument, not attack tooling.

**Do not write, generate, or run code that imitates hostile software** — no files designed to defeat a check, no code that hides its own presence, no simulated attacker tooling. If you judge that a check is incomplete, **say so in prose**: name the file and line, state what the check currently establishes, state what it does not, and state what a complete check would have to do. A described gap is the deliverable; a working demonstration of one is not, and is out of scope for this review.

Environment notes: modify no tracked file in the repository. The ceremony runs under `PYTHONSAFEPATH=1` (README step 0) and every path-invoked entry file refuses without it. Run the suite with the pinned interpreter `~/.pyenv/versions/3.12.11/bin/python3`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no cache is written into the tree.

## Scope, in order

**1. Round 17's eight dispositions — the priority of this round, and the attack described above comes first.** Judge each against the bytes:

- **Is the lifecycle-staleness class actually closed?** Sweep every manifest-covered file yourself for any sentence, status, count, date or claim that is true now and false after the freeze, after the batch runs, or after publication. The maintainer's sweep found eleven prose hits and two executable ones; find what it missed, in either direction. Say explicitly whether any *further* covered byte is a function of the study's own stage.
- **Are the five untouched sentences correctly classified?** They were judged registration-time statements that must not be "fixed". If any is in fact a live self-updating value, that is a finding; if any was fixed that should not have been, that is also a finding.
- **Do the three new tests do what they claim?** The manifest-invariance test, the lifecycle-status lint, and the two rewritten stage-dependent tests. Would each fail if the property it names stopped holding? The lint is a blacklist and says so — judge whether its registered statement of its own strength is honest.
- **Verify the freeze and run really move no covered byte.** Take the registry's four lifecycle members and `freeze.excluded`, and satisfy yourself that no registered act — freeze, golden capture, C7, the 150-call batch, scoring, publication — changes anything the manifest covers. This is the property rule 3's termination depends on, so check it from the registration rather than from the maintainer's summary.

**2. The defect class itself, at every act.** Three acts have been repaired. Sweep for a fourth: take every registered act in the study's lifecycle — the freeze, the golden capture, §6 C7, the 150-call batch, scoring, `--emit-records`, publication, the correction, `DEVIATIONS.md`, and the recording of a review round — and satisfy yourself from the registration and the exclusion list that each moves only carrier or excluded bytes. If any act still moves a covered byte, that is this round's blocking finding. Say explicitly whether the class is now closed or whether you found a fourth instance.

**3. The registered content — a fresh sweep, with freeze in view.** Rounds 9 through 13 found their sharpest results in the study rather than the harness. Read as though the next act is the freeze.

- `PREREGISTRATION.md` in full. It is the registration; everything else answers to it.
- §2.3's six semantic classes, §2.4's arm-D substitution and 280-cell landmark grid, §2.6's document structure and the prompt equation, Appendix A's assembly rule against the twenty committed arm artifacts. Re-derive at least two independently.
- §2.8's schedule and its five balance properties; §3.3's partition; §4's endpoints and the §4.3 interval vectors; §5's level, contrast and decision tables against `harness/score_rates.py`'s encodings; §6's controls C1-C10 against `harness/integrity.py` and the test suite.
- `CLAIM.md` against its cited source in `studies/011-authorship-coverage-rates/MIRROR-AGREEMENT.md`; `MIRROR-AGREEMENT.md` against the retained attempts under `analysis/mirror2-attempts/`.
- Ask the question no checklist covers: **is there a registered sentence that no code makes true, a control that cannot fail, a test that asserts less than it appears to, or a claim in the records that the artifacts do not support?**

**4. The suite, at 315 (177 subtests), and the residuals the record names.** The record names these as open on purpose: `verify_mirror2()` has no direct unit test; `verify_tree()` and `normalized_pins()` are covered only for `tree_manifest()`; `_write_outputs()` is pinned only at its override gate; `_emit_records()` and `_check_records_target()` have no direct suite coverage, which is why the record destination went unmodelled for fourteen rounds; `_epoch()` validates punctuation but not calendar ranges; §4.6's reading keys on levels while the scorer keys on contrasts (registered as conservative); §4.1's Q sentence has no test; §2.2's two digest cells are hand transcriptions no assertion covers; and after README step 5 the tree stops producing the C7 refusal message with no test asserting it. Confirm each is as described, then ask what **else** the suite asserts less than it appears to.

**5. The freeze question, asked directly.** §2.10 registers what the freeze binds and §7 registers what is mechanically enforced against what is merely recorded. Read both against the tree as it stands and answer: **if this tree were frozen at this commit and the batch run tomorrow, what would the study publish that it has not earned?** If the answer is nothing, say so.

**6. Run the suite and the verification command**, and report both results. If any test fails, report it with its output rather than re-running until it passes; one test has shown load-sensitivity once and the record says so.

**7. Compute the tree manifest yourself**, as §2.10 registers it: over every git-tracked regular file under the study directory, excluding the paths in `harness/PINS.json` `freeze.excluded` and the two carriers (`harness/PINS.json`, `PREREG-REVIEW.md`), build the sorted list of lines `<path> <bytes> <sha256>` with paths relative to the study directory; then append the registry's normalized-projection entry — `PINS.json` parsed, `freeze.treeManifestSha256`, `freeze.preregistrationSha256`, `golden.sha256` and `isolationNegative.assent` set to null, serialized with `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",",":"))` plus a newline, hashed and listed as `harness/PINS.json#normalized <bytes> <sha256>` — sort all lines together, join with newlines plus a trailing newline, and take the sha256 of that text. Confirm `integrity.tree_manifest()` implements the same recipe.

## Final message

A numbered findings list — each with file:line, what the record says, what the code does, and severity (blocking, should-fix, nit) — then:

- an overall verdict line, which must state explicitly whether you judge the tree **ready to freeze**;
- the line `Reviewed commit: 8e93689`;
- the line `Tree manifest (my computation): <hex digest>`;
- then the single line `CODEX-012-R18-DONE`.

If you find nothing blocking, say so plainly — a clean verdict is a real outcome and this study is ready to be frozen when it earns one.
```

### Complete unedited final message

(Absolute paths in the reviewer's markdown links are rendered as the
`file:line` anchors they point at; its two `##` headings are demoted to keep
this record's structure; no other byte is altered.)

#### Findings

1. **Ungated `capture --captures DIR` can move manifest-covered bytes.**  
   PREREGISTRATION.md:3552 says every operator-named destination obeys the lawful-destination rule; PREREG-REVIEW.md:3608 records that rule as general. But batch.py:2472 passes `--captures` unchecked into `run_capture()`, which creates attempts beneath it at lines 2052–2058; the probe wrapper then creates and fills those slots at `authoring_call.sh:297–310,398,408,421–422`. PINS.json:159 excludes only the default `controls/recapture/`. An in-study sibling therefore becomes covered when the retained attempts are staged for the publication required by §8. The destination table has only three roots at `test_manifest.py:1026–1035`; adding the missing attribute-spelled gate in a disposable copy left its four relevant ledger/writer tests green. A complete repair must gate `captures_dir` before `next_attempt()` or any side effect, classify and behaviorally drive that root through the command entry, bind the configured destination in the lifecycle model, and make deletion mutation-red. This is the fifth lifecycle-output instance; the class is not closed. **Severity: blocking.**

2. **The score destination test bypasses the production wiring it claims to test.**  
   test_manifest.py:954 says `_drive_emit_records()` drives the real entry and that deleting the call turns it red. Instead it calls `_check_records_target()` directly; production invokes that helper at score_rates.py:4711. Removing only the production call in a re-pinned disposable copy left integrity and all 13 manifest tests green. This contradicts `PREREG-REVIEW.md:3617–3624`’s mutation-red claim. The runtime call is currently correct; the regression guarantee is not. **Severity: should-fix.**

3. **“A deleted gate call is a red suite” is broader than the ledger actually provides.**  
   PREREGISTRATION.md:1361 and `test_batch.py:3148–3151` make that claim. `_add_cell()` at `test_batch.py:2437–2455` deliberately merges repeated calls of the same gate in one host. Removing the post-recovery `verify_prefix()` at batch.py:1740 left a re-pinned full suite at 315 passed and 177 subtests. The call appears redundant, so this is a reach/wording defect rather than a current control failure. **Severity: should-fix.**

4. **The writer scan overclaims coverage of “any binding form.”**  
   test_manifest.py:622 describes every name-binding statement, and lines 860–883 claim filesystem aliases through any binding form are rejected. `_bindings()` handles ordinary assignments and simple-name `for`/`with` targets, but not tuple/list `for` or `with` targets, exception bindings, comprehension targets, or pattern captures. No current writer uses such an alias, so no present destination is unsafe. The scan must cover those AST binding contexts or narrow its stated guarantee. **Severity: should-fix.**

#### Verification

- Official suite: **315 passed, 77,952 warnings, 177 subtests passed in 394.62s**.
- Standalone `harness/integrity.py`: **exit 0**; 11 ported files, all five arms and mirrors verified, HEADER 948 bytes, tree correctly reported unbound pre-freeze.
- Worktree remained clean.
- Driver census independently reconciled: **82 = 40 command + 3 preflight + 39 residual**, over 14 gate functions.
- Scorer census independently reconciled: **25 = 4 command + 21 residual**.
- Bare module-level gate additions/removals were detected; the missing attribute-spelled capture gate and repeated-call deletion were not.

The lifecycle-staleness sweep found no further covered byte whose value depends on review, freeze, batch, scoring, or publication stage. The five untouched sentences are correctly conditional, historical, role-defining, or verbatim quoted text. The lifecycle lint honestly describes itself as a blacklist; the two rewritten stage-dependent tests are genuinely stage-independent. The manifest-invariance test honestly says it models rather than executes the acts, but its model omits configurable `--captures`.

Apart from finding 1, freeze, golden capture at its default, C7, batch, scoring, record emission, publication, correction, `DEVIATIONS.md`, and review recording map to carriers, registered exclusions, or an external study. There is no separate sixth destination instance.

The scientific instrument re-derived cleanly: all six semantic classes and five 280-cell grids, arm-D substitution, twenty artifact pins and prompt equations, schedule balances, partition, intervals, level/contrast/decision tables, C1–C10, `CLAIM.md` provenance, and all five retained mirror attempts agree with the registration and code. No blocking finding touches the arms, endpoints, decision rules, or claim.

The named residuals remain accurate with two nuances: `normalized_pins()` now has direct projection-lint use, though no complete focused test; `_check_records_target()` has direct helper coverage, but not production-call coverage. The other recorded residuals remain as described.

My independent manifest contained 86 covered tracked regular files plus the normalized registry entry. The normalized entry was 7,506 bytes with SHA-256 `471897704b386ecdee60d2ab8d26911185f2596d4739eedaf3c43a1264d59f63`; the final 8,862-byte manifest text produced the digest below. `integrity.tree_manifest()` implements the same recipe and returned the same digest.

If the literal default ceremony ran tomorrow, it would publish no unearned scientific conclusion. The tree would nevertheless publish unearned claims of universal lifecycle immutability and mutation-red destination wiring.

Overall verdict: **NOT READY TO FREEZE** — finding 1 is blocking. It is not a scientific-instrument finding, so the ordinary stopping rule carries to round 19.

Reviewed commit: 8e93689

Tree manifest (my computation): cf9c57383d9108ab79965c2943e06762814df98ebaf430de657bbb63d2a6e821

CODEX-012-R18-DONE

### Dispositions

All four findings **ACCEPTED**, all four independently confirmed — and the
verification found the blocking one materially worse than filed.

**Finding 1 is the fifth instance of a class this record has twice called
closed, and the diagnosis is a habit rather than a bug.** `--captures` was
ungated: pointed at an in-study sibling it moves the manifest once the retained
attempts are staged for the publication §8 requires, measured at
`cf9c5738…` → `2bce35f1…`, with the default target leaving it unchanged. Round
17's repair was recorded as a **general** lawful-destination rule applied to
"every operator-supplied destination at once." It was applied to three call
sites chosen by hand. The predicate was general; its application was a list.
Four rounds running I have fixed a class by enumerating its members and had the
next round find the one I missed.

**Two measurements made that undeniable.** Adding the missing gate left all 25
gate, ledger, writer and destination tests green and the full suite at 315 — so
the new gate could have been deleted again with nothing noticing, which is round
16's finding reproduced at the fourth destination. And worse, the derived ledger
carried **zero** cells for the lawful-destination rule at *any* of its three
existing call sites, because `classify()` and `gatescan` filtered on
`isinstance(call.func, ast.Name)` and an attribute-spelled callee is invisible
to that. The rule that was supposed to be the general answer was held entirely
by three hand-listed behavioural pairs.

**So the repair is a derivation, and the test of it is that it finds this round's
finding by itself.** A flag→write taint analysis walks every command-line
argument in the driver and the scorer through to every path-consuming call,
keyed on (flag, entry, formal) because `--out` names three different
destinations through three commands. Run against pristine `8e93689` — the tree
the reviewer read — it prints the finding unprompted: `(--captures, run_capture,
captures_dir) UNGATED`, and `(--scratch-parent, …) UNGATED` beside it. A fifth
destination flag added ungated now fails by name; so does one whose only write
is the shell wrapper's slot, which the writer scan cannot see at all. The
`ast.Name` blindness is fixed in both ledgers, and the census moves
**82 → 89 cells** over **105 → 112 sites**, with the three lawful-destination
call sites appearing as driven cells where there were none.

**Mutation-redness is now run rather than asserted.** Finding 2 is the standing
target found inside the mechanism built to prevent it: a test whose docstring
said it drives the real entry, which called the helper directly, so deleting the
production call stayed green — and the round-17 record's mutation-red claim was
therefore false one round after it was made. There is now a derived call chain
and an in-memory one-edge mutant, so "deleting X turns this red" is executed.
Deleting that production call now fails three independent ways.

**Three record overclaims are corrected in place**, quoted by the verification
and named here because the record is what a later reader gets: §7's "every
destination the operator names" followed by a three-item list; the test comment
saying "what stops a fifth is that the rule is general"; and the claim that the
parameter-to-callers gap "is not the permanent residual here any more" — it
still was. §7 now names the derivation rather than a list, and the gate rule is
registered per call site.

**Findings 3 and 4** took the exhaustive-by-construction form the round's
instruction asked for: the ledger counts call sites rather than merging repeats,
and the writer scan's hand-listed binding forms are replaced by `symtable` and
`callable()` rules — nineteen gap spellings measured caught, six correct shapes
silent, all eight harness modules clean.

**What the derivation still cannot see, measured against synthetic sources
rather than reasoned about**: an attribute-spelled callee on the *propagation*
path, a value stored in and read from a container, `os.environ`, and a
positional `argv[2]`. Also outside it: destinations named positionally, a module
with no `main()`, and path-insensitivity — reaching the gate somewhere is not
the gate dominating every write, which the behavioural pairs cover instead. **A
sixth instance escapes only by being one of those shapes**, and that sentence is
the first in this sequence I can support by having tried to break it.

Verification after the dispositions: `harness/integrity.py` exit 0; the pinned
suite **317 passed** with 190 subtests; tracked status clean; `arms/`,
`analysis/`, `CLAIM.md` and `MIRROR-AGREEMENT.md` untouched. The
post-disposition tree manifest, the maintainer's computation, is
`9fa37a514a8ca7ac45078cc0574c714f0706eb5d91b58bdf17b35e7a391270cc` — round 19
attests it, and under §2.10 rule 3 that round is required.

Residuals unchanged except where named above, plus two new ones recorded rather
than closed: the scorer's third gate region (`collect_slots`, `terminality`,
`load_ledger`, `check_population`, roughly twenty refusal sites) remains outside
both ledgers, and `pathlib`-style filesystem objects pass both new writer rules —
no module imports `pathlib` today, verified by `symtable`.

## Arm text digests, as reviewed in this round

Unchanged since round 2, and unchanged by every disposition above:

| arm | bytes | sha256 of the arm text as reviewed in round 18 |
|---|---|---|
| **A** | 1815 | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` |
| **B** | 1880 | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` |
| **C** | 1815 | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` |
| **D** | 1815 | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` |
| **E** | 2082 | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` |
