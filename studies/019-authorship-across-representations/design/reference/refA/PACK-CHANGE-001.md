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
