# REFERENCE-A — the frozen arm-A reference record

Frozen copy set, landed at the freeze ceremony (2026-08-19). The executable reference is
[`reference/refA/pack.json`](refA/pack.json); this document carries its build and repair
record verbatim from the design tree.

---

# Arm A reference build report (from builder final output)

> **CORRECTION, 2026-08-18 — one claim in this report is false, and the pack it describes
> is no longer the committed one.** Round-1 finding R1-2 challenged the inexpressibility
> claim; it was tested and it did not survive. The committed `pack.json` has been repaired
> (`PACK-CHANGE-001.md`, new sha256 `db977607…`; the pack this report describes is
> `956ceebb…`), it answers the prose-correct `review` on all 72 off-grid cells below, and
> the registered exclusion class X1 is **retired**.
>
> Specifically, in "Mismatches" below: *"Irreducible under every onUnknown assignment"* is
> **true and unchallenged** — the 2,048-assignment enumeration stands. *"Structurally
> reducible only by an encoding no author would write: a probe rule carrying two
> contradictory ordered comparisons…"* is **false twice over**. The probe cannot work at
> all (every JPS connective is monotone in the information order, `not(unknown) = unknown`
> included, so a contradictory pair is FALSE when the fact is readable and UNKNOWN when it
> is not — *never TRUE* — and a rule that is never true can neither fire nor suppress;
> measured on the full space, the probe variant changes 0 cells with `onUnknown: ignore`
> and makes things worse with `escalate`). And a repair that *does* work exists inside the
> fragment: two region-scoped `review` rules plus two region-scoped suppressions of
> `r-d8`, which move exactly these 72 cells and nothing else in 236,196.
>
> Everything else below — the V6 answer, the per-assignment mismatch counts, the encoding
> decisions, the result-surface facts, the grid coverage gap — is unaffected and is left
> verbatim. The corrected general statement is: *the natural encoding cannot express this
> region under any `onUnknown` assignment, and expressing it costs a derived region lemma
> the prose never states* — which is an asymmetry-ledger row, not an inexpressibility
> result.

## V6 answer

SETTLED: r-d8 (the D8 negation-cascade catch-all) = escalate; EVERY other rule = ignore (r-d1, r-d3, r-d4, r-d5, r-d6a, r-d6b-insured, r-d6b-uninsured, r-d6c, r-d7, r-o1-review). Exceptions: x-o3-large-exposure = escalate; x-o1-first-engagement, x-o2-critical-supplier and the seven x-d5-suppress-* = ignore. Evidence (full grid, 2540 cells, prose_model as target; the 2^11=2048 rule assignments enumerated with a simulator that agrees cell-for-cell with the pinned engine on 15,240 checked evaluations): reference 0 mismatches; 128 assignments score 0 (all agree d4/d5/o1-review=ignore, d8=escalate, differing only on the 7 grid-unobservable rules); best with d8=ignore 12; all-ignore 79; all-escalate 103; worst 163. Single-flip costs off the reference, each re-verified on the pinned engine: d8->ignore 79, d5->escalate 84, d4->escalate 13, o1-review->escalate 12. Reasons per element: d8=escalate because D8's unknown is exactly "the ladder cannot say which clause governs" = U1's "otherwise ... unresolved as unknown"; d4=ignore because U1 worked example 1 (D3 rejects at risk 95 while country is unreadable) requires an undetermined clause not to block a clause that decides without the unreadable input; d5=ignore and o1-review=ignore because an unreported prior-enforcement / new-vendor status is "treated as no" and must not block; d3=ignore is derived off-grid (flipping it costs 540 extra mismatches on a 236,196-cell derived space; engine-verified witness {CLEAR, LOW, spend 50000.00, prior yes, risk unreadable, evidence present}: prose reject, reference reject, d3=escalate gives unresolved[unknown]); the remaining six rules are observationally free on both the grid and the derived space and are set to ignore for the uniform reading "a determination clause's own unknown never blocks by itself; D8 is the single place U1's otherwise is realized". WHY THE PANEL SPLIT: onUnknown is not a free parameter -- D8's value is entailed by D8's structure. Tested head to head: S1 (negation cascade + region-scoped O1 review rule) best = 0 grid / 72 derived with d8=escalate; S2 (positive union of review regions, the shape jpsExpr's "C8 ignore, region rules escalate" implies) best = 24 grid / 240 derived, still with d8=escalate. S1 adopted.

## Mismatches

NONE on the shared grid: 0 of 2540 cells mismatch, engine-verified, with no evaluationError, no unexpected disposition kind and no non-JSON payload.

OFF-GRID (reported for gold authoring, not part of the scored surface): 72 of 236,196 derived cells. Class = sanctions CLEAR, financial evidence present, prior != yes, critical != yes, newVendor = yes, 40 <= risk < 70, and EITHER country = LOW with spend unreadable OR country unreadable with spend <= 100000.00. Prose: outcome review (every substitution lands on review -- D6c's region is O1-suspended and every other spend/country value falls to D8). Reference pack: unresolved {unknown}. Mechanism: the O1 companion rule is unknown because its D6c-region conjuncts read the unreadable input, so it contributes no candidate; D8's cascade is unknown for the same reason; r-d8: escalate therefore retains 'unknown' and SS8 step 5 returns unresolved BEFORE any candidate is collected -- an unknown-escalate rule poisons a cell regardless of what else fires. Irreducible under every onUnknown assignment (each of the 72 cells checked against all 2048 assignments: 0 rescued). Structurally reducible only by an encoding no author would write: a probe rule carrying two contradictory ordered comparisons on one fact ('spend > 100000.00' AND 'spend <= 100000.00') plus not(newVendor == 'yes'), which is false whenever the fact is readable and unknown exactly when it is not -- a hand-built is-unknown predicate the fragment does not offer. Measured alternatives: wide (spend-free) companion 0 grid/72 derived; companion region added to the cascade 0/360-504; extra O1 force-outcome with a not(prior=='yes') conjunct 0/60 (closes two thirds but adds an exception the registered design does not carry and decides the O1 cells twice); S2 positive-union D8 24/240. The current grid contains no cell of this class because its unreadable-numeric cells all carry newVendor = no; gold must not add one unless the inexpressibility is registered (this is the arm-A floor risk regoFair #9 warns about).

## Notes

REPORT.md COULD NOT BE WRITTEN: this session's harness blocks subagents from writing report/summary/findings .md files and instructs that findings be returned as the final message; I did not route around the block with Bash. The complete report (headline, V6 answer with per-assignment mismatch counts, the final onUnknown table, encoding decisions and the irreducible-mismatch analysis) is in my final assistant message and can be saved to refA/REPORT.md verbatim by the caller.

METHOD. prose_model.py is labelled in-file as a DESIGN-TIME TUNING TARGET, not the study oracle. Every reported disposition for the final pack comes from the pinned jpack 0.17.0 binary run outside any jpack.json directory, read from the JSON payload (never exit codes). The 2048-assignment enumeration used a Python re-implementation of SS7/SS8 (jps_sim.py, transcribed from internal/evaluation/{condition,resolve}.go); it was validated against the pinned engine cell-for-cell on 6 x 2540 = 15,240 evaluations with 0 disagreements. results.jsonl was regenerated from pack.json by an independent path (run_engine.py) and is byte-identical to the verify.py output.

ENCODING DECISIONS THE STUDY DESIGN MUST RECORD.
(1) D8 = all(CLEAR, not(any(D3, D4, D6a, D6b-insured, D6b-uninsured, D6c, D7))). Both D6b branches are disjuncts because the enhanced-review branch decides. D5's condition is deliberately NOT a disjunct: /vendor/priorEnforcement is omitted when unreported, so a D5 disjunct makes the cascade unknown on every unreported-prior cell where the prose says "treated as no".
(2) D5 needs SEVEN suppress-rule exceptions, not a conjunct. "D6 and D7 apply only to vendors with no recorded prior enforcement action" is inexpressible as a condition (Kleene monotonicity: a condition true on an omitted key is true on every refinement, so nothing approves on an unreported status while excluding "yes"); not-equals "yes" breaks the unreported case, and omitting the term makes D5's reject co-fire with D6/D7's approve as unresolved{conflict}. Targets: r-d6a, r-d6b-insured, r-d6b-uninsured, r-d6c, r-d7, r-o1-review AND r-d8 (the last because D5 is not in the cascade). This is an arm-A cost the prose does not hint at and is one 'not prior_yes' conjunct in Rego -- an asymmetry-ledger row (B/C-favorable) the notes do not yet carry.
(3) O1 encoded as registered: suppress-rule on r-d6c (ignore) plus r-o1-review = all(D6c-condition, newVendor == "yes") -> review, ignore. Suppression does not falsify the condition inside the cascade, so without the companion the region becomes no-match; escalate on the companion breaks the unreported-new-vendor cell (12 grid rows).
(4) insurance-certificate stays an evidenceRequirement (required:false) read with evidence-present: present->approve, absent->not(evidence-present)=true->enhanced-review, unreported->both D6b rules unknown->unresolved{unknown}. (The probe packs pack2/pack3.json used the other repair, insurance-as-fact-string, which the draft did not take.)
(5) No fallbackOutcome; D2 reaches no-match at step 10 (360 grid rows). O2 = force-outcome review with an explicit CLEAR conjunct (keeps D1/D2 standing; step 6 produces it without evaluating rules, so it stands under unreadable numerics). O3 = escalate with the evidence-present(financial-evidence) conjunct and outranks O2 because a direct escalation is a retained reason at step 5. escalation.triggers = [missing-required-evidence, unknown, no-match], queue vendor-compliance-desk (unscored, recorded rather than derived).

RESULT-SURFACE FACTS WORTH REGISTERING. Grid distribution: reject 560, review 287, approve 127, enhanced-review 12, unresolved{unknown} 607, {missing-required-evidence} 487, {no-match} 360, {exception-escalation} 100. All four outcomes and all four reason tokens are reachable, and EVERY reason set on the grid is a singleton -- O3's evidence conjunct closes the panel's {exception-escalation, missing-required-evidence} leak (P1 x O3: evidence absent -> ["missing-required-evidence"], evidence unreported -> ["unknown"]). All three U1 worked examples reproduce (reject / unknown / review), as do D6b's three insurance states, the O1-unreported cell (approve), the O2xO3 cell (exception-escalation), the D5-vs-D6a cells, MATCH-with-everything-missing (reject; with evidence absent, missing-required-evidence), and the 2,000,000.00 / 2,000,000.01 pair (review / exception-escalation).

TWO INTERPRETIVE READINGS IN THE PROSE MODEL that the clean-room oracle should independently check: (a) U1's "same determination" is generalized to "same RESULT", so a cell whose every substitution is O3 escalation is unresolved{exception-escalation} rather than {unknown} (the engine agrees, since O3 fires at step 5 and rules are never evaluated, but the prose does not say so outright); (b) U1's substitution domain is 8 risk x 8 spend x 3 country representatives, sound because every clause reads risk and spend only through comparisons against the six declared thresholds, so each threshold-cut interval is a constant region, and both endpoints of each interval are substituted so a mis-stated inclusivity shows up as a disagreement rather than being skipped.

GRID COVERAGE GAP (for V7/gold): the grid's unreadable-numeric cells all carry newVendor = no and prior = no, so seven of the eleven rules' onUnknown values are unobservable on it (128 of 2048 assignments score a perfect 0). Only the derived space separates r-d3. If the study wants the onUnknown assignment to be a scored quantity rather than an assumed one, the grid needs cells crossing an unreadable numeric with prior = yes and with newVendor = yes.

---

# refA/pack.json change 001 — the X1 repair (round-1 finding R1-2)

Recorded the way a port is recorded: old digest, new digest, the enumerated edit, and
the measurement that admitted it. Nothing here is a study result; this is a design-time
reference repair, made before the freeze, in response to a review finding.

| | |
|---|---|
| Date | 2026-08-18 |
| Trigger | round-1 **R1-2** (BLOCKER): "X1 is overbroad, and its claimed inexpressibility is not proved over the registered fragment … implement and test the structurally repairing encoding, eliminating X1" |
| Old `refA/pack.json` sha256 | `956ceebbc08886acdc3973b43112e9896f2853b3895243b3b97ff33a910453ee` |
| New `refA/pack.json` sha256 | `db9776070fbf5e193443ffb1f371b2524b4662f0877868306323b5c9e3701853` |
| `refB/policy.rego` | **unchanged** (`1f2e1ad1…`) — the Rego reference was already prose-correct on these cells |
| `refA/results.jsonl` | **byte-identical** (`d2cbfed2…`), engine-regenerated over all 2,540 grid cells |
| Consequence | the registered exclusion-class set is now **empty**; X1 is retired, not narrowed |

## 1. The enumerated edit

Six additions. Nothing was deleted, and no existing rule, exception, condition,
`onUnknown`, outcome, evidence requirement or escalation member was modified.

**Two rules** (inserted immediately before `r-d8`, so the file still reads in clause
order), both `onUnknown: ignore`, both `outcome: review`:

| id | `when` | prose derivation |
|---|---|---|
| `r-o1-wide-low` | `all(sanctions == CLEAR, country == LOW, risk >= 40, risk < 70, newVendor == yes)` | O1 removes D6c for a new vendor, and in the LOW-country 40–69 band nothing else can reach the request: D6a/D6b need risk < 40, D7 needs MEDIUM, D3 needs ≥ 90, D4 needs HIGH, O3 needs HIGH. D8 governs → **review, whatever the requested spend is**. |
| `r-o1-wide-spend` | `all(sanctions == CLEAR, risk >= 40, risk < 70, spend <= 100000.00, newVendor == yes)` | At risk 40–69 with spend ≤ $100,000.00: LOW is D6c, removed by O1 → D8; MEDIUM is out of D7's reach (risk < 40); HIGH is out of D4's reach (risk ≥ 70); O3 needs spend > $2,000,000.00. D8 governs → **review, whatever the country risk is**. |

**Four exceptions**, all `suppress-rule`, all `onUnknown: ignore`:

| id | `when` | effect |
|---|---|---|
| `x-o1-suppress-d8-low` | same condition as `r-o1-wide-low` | suppress `r-d8` |
| `x-o1-suppress-d8-spend` | same condition as `r-o1-wide-spend` | suppress `r-d8` |
| `x-d5-suppress-o1-wide-low` | `priorEnforcement == yes` | suppress `r-o1-wide-low` |
| `x-d5-suppress-o1-wide-spend` | `priorEnforcement == yes` | suppress `r-o1-wide-spend` |

The last two are the eighth and ninth members of the D5 suppression family the build
report's encoding decision (2) already describes: D5 is not a conjunct, so every rule
D5 displaces needs its own suppression, and the two new rules are two such rules.

## 2. Why this works, when the probe the build report named does not

The mechanism X1 rested on is real and unchanged: on those cells `r-d8`'s negation
cascade is UNKNOWN (its D6c disjunct reads the unreadable member), and an
unknown-`escalate` rule returns `unresolved` at §8 step 5 before any candidate is
collected. The 2,048-assignment enumeration in `refA/REPORT.md` is also unchallenged:
no `onUnknown` assignment rescues those cells.

What the build report got wrong is the *structural* claim — that the only repair is "an
encoding no author would write: a probe rule carrying two contradictory ordered
comparisons on one fact … a hand-built is-unknown predicate the fragment does not
offer."

**The probe cannot work, and this is now measured, not argued.** A JPS condition is
built from Kleene-strong connectives (`all`, `any`, `not`, `fact`, `evidence-present`),
and every one of them is monotone in the *information* order (unknown ⊑ true,
unknown ⊑ false) — including `not`, since `not(unknown) = unknown`. So a condition that
evaluates TRUE on a document with a member absent evaluates TRUE on every document that
supplies that member. An is-unknown predicate — true exactly when the member is absent,
false when it is present — is therefore not a condition in this fragment, and no
arrangement of contradictory comparisons changes that. The contradictory pair
`all(spend > 100000.00, spend <= 100000.00)` is FALSE whenever spend is readable and
UNKNOWN when it is not; it is *never TRUE*, so a rule carrying it can never fire, and
an exception carrying it can never suppress. Measured on the full 236,196-cell space:

| candidate | cells changed vs the old pack | divergences vs refB |
|---|---|---|
| probe rule, `onUnknown: ignore` (`v3`) | **0** | 72 (unchanged) |
| probe rule, `onUnknown: escalate` (`v3e`) | 36, none of them an X1 cell | **108** (worse) |
| `not(newVendor == 'yes')` added to D8's D6c disjunct (`v4`) | 552 | **480** (breaks every unreported-new-vendor cell) |
| **region-scoped rules + region-scoped D8 suppression (adopted)** | **72** | **0** |

**What does work is region scoping.** The prose fixes the determination for a whole
*region* — every substitution of the unreadable member lands on `review` — and that
region can be named without reading the unreadable member at all. The two new rules
name it; the two new suppressions remove `r-d8`'s escalate-on-unknown *only inside the
region where the answer does not depend on the unreadable member*, so the catch-all
stops re-reading a member whose value cannot change the outcome. Everywhere else
`r-d8` is untouched and still escalates.

The regions are deliberately narrow, and the narrowness is load-bearing rather than
decorative. A single wider region `all(CLEAR, risk >= 40, risk < 70, newVendor == yes)`
would be **wrong**: with country *and* spend both unreadable, the substitutions HIGH ×
spend > $2,000,000.00 reach O3 (escalation) while LOW × spend ≤ $100,000.00 reaches D8
(review), so U1 requires `unresolved[unknown]` there. `r-o1-wide-low` pins country =
LOW and `r-o1-wide-spend` pins spend ≤ $100,000.00; each conjunct is exactly what puts
O3 out of reach. On the both-unreadable cells both new rules are UNKNOWN, both are
`ignore`, neither suppression fires, `r-d8` escalates, and the answer stays
`unresolved[unknown]` — which the full-space sweep confirms (zero collateral changes)
and which gold row `x1r-adjacent-both-unreadable` now pins.

## 3. What was measured before adopting it

Every number below is from the pinned toolchain (`jpack` `42f35f79…`, OPA `1dd5c559…`),
over `cert_offgold.py`'s registered 236,196-cell derived space, with the certificate's
own simulator-admission protocol re-run **against the candidate pack** (a new pack shape
voids the committed simulator-revalidation record, so it was re-earned, not inherited):

| check | result |
|---|---|
| `jpack spec validate` on the new pack | **pass** (exit 0, JPS 0.2.0-draft conformance) |
| simulator re-validation, 2,000-cell deterministic stratified subsample, candidate sim vs pinned engine | **0 disagreements / 2,000** |
| verdict-class coverage, ≤ 100 systematic cells per candidate verdict class | **0 disagreements / 748** |
| cells whose verdict changes vs the old pack | **72**, every one of them engine-confirmed on both packs |
| those 72 vs the retired X1 predicate | **72/72 inside it**, and 72/72 inside the tighter refined description |
| collateral changes outside the retired class | **0** |
| new pack vs refB over the full space | **0 divergences / 236,196** |
| 2,540-cell design grid, candidate sim and candidate **engine** vs committed `refA/results.jsonl` | **0 / 2,540** each — `results.jsonl` regenerates byte-identical |

## 4. What this costs, stated plainly

1. **The inexpressibility finding is withdrawn.** X1 is retired, not narrowed. The
   census row that reported "the prose-correct outcome is inexpressible in the
   fragment" is false as stated and must not be republished. What survives is a
   weaker, true statement: *the natural encoding* — D8 as a single negation cascade —
   cannot express it under any `onUnknown` assignment, and expressing it takes a
   region lemma the drafter of the prose never states.
2. **The repair encodes derived lemmas, not clauses.** `r-o1-wide-low` and
   `r-o1-wide-spend` are sound consequences of the prose, but they are consequences an
   author has to *derive*. That is a real asymmetry-ledger row against arm A (arm B/C
   need no such lemma: Rego's total function answers the region directly), and it
   belongs in the ledger alongside encoding decision (2)'s seven suppress-rules.
3. **The reference is no longer the most natural pack a careful author would write.**
   It is the most faithful one. The study's arm-A *authors* are not expected to find
   this encoding, and nothing here predicts that they will — which is a finding the
   study can now measure instead of exclude, because the identity control compares an
   author's *cases* against this reference, and this reference now agrees with the
   prose on the cells the filter used to hide.
4. **Everything derived from the pack is stale until regenerated**: the arm-A mutant
   corpus (`mutants/refA/`), its witness sets, the adequacy dispositions, the cross-arm
   pairing, and every count computed from them. See `mutants/ADEQUACY.md` and the
   round-1 disposition table for what was regenerated and what was not.
