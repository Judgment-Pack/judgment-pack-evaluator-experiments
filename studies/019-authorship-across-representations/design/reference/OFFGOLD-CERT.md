# Off-gold equivalence certificate — Study 019

**Gate:** `PREREGISTRATION.md` §4 `GATE(pre-freeze)` — *"the two references' agreement is
re-established over the full derived input space, with every divergence point required to
fall inside a registered exclusion class (currently exactly X1); any other divergence
blocks the freeze."*

**Verdict: PASS.** Over the **full** registered derived input space of **236,196 cells**,
the two references diverge on **exactly 72 cells**, and **all 72 fall inside X1**. Zero
divergences outside a registered exclusion class. This is a *complete* run, not an interim
one: the whole space, plus every validation record and the supplementary stratum, fits
in **248 s** of compute (4m08s wall on 16 cores), against the task's 90-minute budget.

Machine-readable companion: `OFFGOLD-CERT.json` (this file is its prose summary; the JSON
is authoritative where they differ).

---

## 1. Headline numbers

| | |
|---|---|
| Cells evaluated (registered space) | **236,196** |
| Divergences | **72** |
| Divergences in registered class X1 | **72 (100%)** |
| Divergences outside a registered class | **0** |
| `allDivergencesInRegisteredClasses` | **true** |
| Divergences also matching the tighter `refA/REPORT.md` description | **72/72** |
| Simulator-found divergences confirmed on the pinned engine | **72/72** |
| Simulator artefacts (sim said "diverge", engine said "agree") | **0** |
| Validation records, all required to pass | **3/3 pass** |
| Total compute, including the supplementary stratum | **248.0 s** |
| Space digest (canonical enumeration) | `5b289515206f07f9…` |

Divergence pattern — one pattern, 72 cells:

```
refA (JPS pack, pinned jpack 0.17.0)  unresolved[unknown]
refB (Rego, pinned OPA 1.19.0)        review
clean-room oracle (third opinion)     review        → backs refB on 72/72
```

This independently reproduces, cell-for-cell, the 72-cell inexpressibility class the arm-A
reference builder reported off-grid (`reference/refA/REPORT.md`) — reproduced here by a
different program, over an independently enumerated space, with the Rego reference (not the
builder's `prose_model.py`) as the comparison side. X1 was registered on the strength of
that report; it now has a second, independent measurement behind it.

---

## 2. The space, and why its value sets represent every interval

The registered space is the one the arm-A builder derived (`refA/REPORT.md`,
`mutants/refA/REGISTRY.json` provenance): the full cross product of U1's substitution
representatives plus "unreadable"/"unreported" on every axis that admits it.

```
sanctions x country x risk x spend x newVendor x critical x prior x finEvidence x insurance
    3     x    4    x   9  x   9   x     3     x    3     x   3   x      3      x     3      = 236,196
```

| Axis | Values | Why these represent every value |
|---|---|---|
| `sanctions` | CLEAR, MATCH, UNKNOWN | 3-valued enum, **exhaustive**. `UNKNOWN` is a *value* (governed by D2), not an absence; U1's parenthetical excludes the screening result from the counterfactual. No omitted member — see §6. |
| `country` | LOW, MEDIUM, HIGH, *omitted* | Readable domain is exactly the enum: **exhaustive**, no representation argument needed. *omitted* = member absent from the input document = "unreadable". |
| `risk` | 0, 39, 40, 69, 70, 89, 90, 100, *omitted* | Readable domain 0..100. Every clause reads risk **only** through the thresholds 40 (D6a/D6b/D7 `<40`, D6c `>=40`), 70 (D6c `<70`, D4 `>=70`), 90 (D3 `>=90`), which cut the domain into `[0,39] [40,69] [70,89] [90,100]`. Every clause is **constant on each block**, so the determination depends on risk only through *which block*. **Both endpoints of every block** are used, not one interior point: a mis-stated inclusivity (`>=` written `>`) then surfaces as a disagreement *between an interval's two endpoints* instead of being silently skipped. 39/40, 69/70, 89/90 are the three band boundaries ±1; 0 and 100 are the outer blocks' representatives. |
| `spend` | 0.00, 100000.00, 100000.01, 500000.00, 500000.01, 2000000.00, 2000000.01, 10000000.00, *omitted* | Readable domain 0.00..10,000,000.00 at cents = 1,000,000,001 values, not enumerable. Every clause reads spend **only** through 100,000.00 (D6c/D7 `<=`), 500,000.00 (D6a `<=`, D6b `>`), 2,000,000.00 (D6b `<=`, O3 `>`), cutting `[0,100000.00] (100000.00,500000.00] (500000.00,2000000.00] (2000000.00,10000000.00]`. Same constancy argument; both endpoints of every block, with the next representable cent (`x.01`) as each open lower endpoint — that is the "every boundary ±0.01" set. The pair (2000000.00, 2000000.01) exercises D6b-inclusive *and* O3-exclusive on the one threshold whose two senses differ. |
| `newVendor`, `critical`, `prior` | yes, no, *omitted* | Declared domain is exactly {yes,no}: **exhaustive**. *omitted* = "unreported", which the prose governs directly (D5/O1/O2 "treated as no"). |
| `finEvidence`, `insurance` | present, absent, *omitted* | **Exhaustive** over the tri-state the evidence channel admits: available / unavailable / availability unreported. |

**Where the representation argument can fail, stated plainly.** Only `risk` and `spend` are
represented rather than enumerated. The argument is exact for any implementation whose
risk/spend sensitivity is confined to the six declared thresholds; an implementation that
invented a *seventh* threshold could hide a divergence strictly between two representatives.
That premise is checked rather than assumed, three ways: refB's own `crosscheck.py` re-runs
U1 over all 101 risk values and a 17-point dense spend sample and requires agreement with
the sparse set; the clean-room oracle quantifies U1 over the full 101-value risk domain; and
both reference texts are short enough to read, and neither carries a seventh threshold.

**Relation to the 2,540-cell design grid.** The grid and this space **overlap but neither
contains the other** — the grid carries risk 20/50/95 and spend 50000.00/3000000.00 which
this space does not, and this space carries U1's representatives which the grid does not.
The grid's `AGREEMENT.md` record is therefore **re-verified here as a control**, not
inherited (validation record 2 below).

---

## 3. Method — measured first, then chosen, with the numbers recorded

### 3a. Rego side: `opa exec` over a built bundle vs per-cell `opa eval`

Both methods were run on **the same 200 cells** and required to agree cell-for-cell before
either was used at scale.

| Method | ms/cell | Projected, full space | Capabilities enforced at |
|---|---|---|---|
| **`opa exec` over a built bundle** ← **chosen** | **0.316** | **~1.2 min** | **build time** (`opa build --capabilities`) |
| `opa eval` per cell (the `run_grid.py` method) | 23.03 | ~91 min | invocation (`opa eval --capabilities`) |

- **Speedup 72.9×**; both methods **agreed on 200/200 cells** (`methodsAgree: true`).
- `opa exec` does not accept `--capabilities` at v1.19.0 (TOOLCHAIN-NOTES), so the exec path
  enforces the denylist at **build** time — a strictly earlier and harder failure than a
  per-invocation flag. The power of that enforcement is re-checked here, not assumed: the
  `time.now_ns` canary is pushed through the same build path and is **refused**
  (`rego_type_error: undefined function time.now_ns`, exit 1).
- Actual full-space cost of the chosen method: **36.6 s**.

### 3b. JPS side: engine-validated simulator, with every divergence confirmed on the engine

The pinned engine costs ~16 ms/cell — ~63 minutes of subprocess churn for the space. The
sweep therefore runs on `refA/jps_sim.py` (13.5 s for the whole space), admitted **only**
under fresh re-validation, and **every divergence cell it finds is re-evaluated on the pinned
`jpack` binary**. Every `refA` verdict printed in this certificate for a divergence cell is an
**engine** verdict, never a simulated one.

---

## 4. Validation records (all three required to pass; all three passed)

| # | Record | Population | Result |
|---|---|---|---|
| 1 | **simulator-revalidation** | **2,000-cell deterministic stratified subsample of *this* space** — 48 strata (`sanctions × country × riskReadable × spendReadable`), proportional largest-remainder allocation, systematic selection within stratum, **no RNG anywhere** | **0 disagreements / 2,000** between `jps_sim` and the pinned `jpack` (13.2 s) |
| 2 | **grid-regression** | the 2,540-cell design grid, re-evaluated by *this program's* two instruments and diffed against the **digest-pinned committed** `refA/results.jsonl` and `refB/results.jsonl` | **0** sim-vs-committed-refA, **0** exec-vs-committed-refB, **0** refA-vs-refB — `AGREEMENT.md`'s 2,540/2,540 reproduced |
| 3 | **verdict-class-coverage** | up to 100 systematically-selected cells per **distinct refA verdict class** (748 cells over all 8 classes), re-evaluated on the pinned engine | **0 disagreements / 748** |

Why record 3 exists: records 1 and 2 bound the simulator on a *stratified-by-input* and a
*different-space* population. A simulator defect that lives in one output class (say, the
conflict path) could in principle dodge both. Record 3 is stratified by **output** and
covers every class the sweep produced, including the two the divergence sits between.

Records 1 and 3 together are what make the "sim says agree" direction safe; engine
confirmation covers the "sim says diverge" direction (0 artefacts retracted).

**Toolchain digests** all match their pins (`OFFGOLD-CERT.json.toolchain`): `jpack`
`42f35f79…`, `opa` `1dd5c559…`, `refA/pack.json` `956ceebb…`, `refB/policy.rego`
`1f2e1ad1…`, `cells.json` `da4ee85c…`, both committed `results.jsonl` `d2cbfed2…`.

---

## 5. The 72 divergences

All 72 satisfy the **registered** X1 predicate, transcribed from
`cleanroom/check_oracle.py` so the two instruments cannot drift:

> **X1** = {new vendor yes; risk in [40,70); LOW country with spend unreadable, **or**
> country unreadable with spend ≤ 100,000.00}

Two readings the registered sentence does not fix, pinned here: *"risk in [40,70)"* requires
a **readable** risk in that band (an unreadable risk score is not a value in an interval),
and *"spend ≤ 100,000.00"* requires a **readable** spend.

Shape of the class as measured (exhaustive over the 72):

| Branch | Cells | Composition |
|---|---|---|
| LOW country, spend unreadable | 24 | risk ∈ {40, 69} × critical ∈ {no, omitted} × prior ∈ {no, omitted} × insurance ∈ {present, absent, omitted} |
| country unreadable, spend ≤ 100,000.00 | 48 | spend ∈ {0.00, 100000.00} × the same 2×2×2×3 |
| | **72** | every cell: `sanctions = CLEAR`, `finEvidence = present`, `newVendor = yes` |

All 72 also satisfy the **tighter** description `refA/REPORT.md` publishes for the same class
(CLEAR, financial evidence present, `prior != yes`, `critical != yes`) — reported because it
is the stronger, more falsifiable statement. It is **not** the gate: the gate is the
registered predicate.

**Mechanism** (from `refA/REPORT.md`, and consistent with what is measured here): the O1
companion rule is unknown because its D6c-region conjuncts read the unreadable input, so it
contributes no candidate; D8's cascade is unknown for the same reason; `r-d8: escalate`
therefore retains `unknown` and §8 step 5 returns `unresolved` **before** any candidate is
collected. An unknown-escalate rule poisons the cell regardless of what else fires. The
builder checked all 2,048 onUnknown assignments against these cells: **0 rescued**. The
prose-correct `review` is inexpressible in the fragment, which is exactly what X1 registers.

**Clean-room oracle, third opinion only.** The oracle was consulted on the 72 divergence
cells and **backs refB (`review`) on 72/72**. That is recorded, not acted on — the oracle is
never substituted for either reference, because a certificate that let it stand in would be
measuring two things and reporting one. What the agreement adds: the divergence is a
*JPS-fragment expressiveness* boundary, not a Rego bug, and two independent readings of the
prose (refB, oracle) land on the same side of it.

---

## 6. Supplementary stratum — the one axis the registered space does not cover

The registered space has **no omitted `sanctions` member**: the prose treats the screening
result as always reported, with `UNKNOWN` as a value governed by D2, and both reference
projections say so in their own words. An input document with `/vendor/sanctionsStatus`
physically absent is therefore **outside** the registered space.

A declared gap a reviewer cannot size is worth less than a measured one, so the 78,732-cell
extension was run and is reported **separately, gating nothing**:

| | refA | refB | oracle |
|---|---|---|---|
| 78,732 sanctions-absent cells | `unresolved[unknown]` 45,198 · `no-match` 7,290 · `missing-required-evidence` 26,244 | `no-match` 26,244 · `unknown` 26,244 · `missing-required-evidence` 26,244 | spread across ordinary determinations |

**18,954 divergences (18,846 outside X1)**, in a single refA/refB pattern —
`unresolved[unknown]` vs `unresolved[no-match]` — with the oracle landing on a *third*
answer (approve/reject/review/enhanced-review) on 14,706 of them.

**Reading:** this is undefined behaviour reported as undefined behaviour, not a reference
defect. An absent sanctions member is an input the prose does not define; refA answers
"no rule condition can be satisfied", refB answers with its total-function backstop, and the
oracle does not gate D3–D8 on CLEAR at all. Three implementations, three answers, on an
input no clause governs. It is precisely why the axis stays out of the registered space.

### What this certificate hands the freeze PR

§4 states the *reason* this gate exists: *"the E4 identity control evaluates author-written
inputs that roam off-gold; a reference defect there voids an arm."* Author-written test cases
can omit **any** member — including `sanctionsStatus`. On the registered space the references
agree everywhere outside X1, so the identity control is safe there. On sanctions-absent
inputs they do not agree, and no exclusion class currently covers it. Two options, offered as
a **recommendation, not a decision**, for the freeze PR to settle:

1. declare absent-sanctions outside the input domain and filter such author-written cases the
   way X1 cases are filtered, with the per-run excluded count published; **or**
2. register a second exclusion class alongside X1.

Doing neither leaves the identity control able to score an arm on an input whose "correct"
answer no reference, and no oracle, agrees on.

---

## 7. What this certificate does not show

- It does **not** decide whether either reference is *right*. Gold (76 rows) and the
  clean-room oracle carry that burden; this instrument only establishes **agreement** and
  classifies the disagreements.
- It is a **design-time gate instrument**. It publishes no study endpoint, adjudicates no
  hypothesis, and nothing in it is a study result.
- The risk/spend representation argument is **sound under a stated premise** (§2), not a
  proof over an arbitrary implementation. It is checked three ways; it is not a theorem.
- The 236,196-cell space is **not** every input either engine can be handed — the
  sanctions-absent stratum (§6) is one measured example of what lies outside it, and the
  space says nothing about malformed documents, out-of-domain enum values, out-of-range
  numerics, or wrong JSON types.
- Agreement between two references is **not** interpretation-independence: both were built
  from the same prose under a shared engine-fact context. The oracle is the
  interpretation-independence instrument, and it is used here in a deliberately narrow role.
- Currency: the certificate is bound to the digests in §4. Any change to `refA/pack.json`,
  `refB/policy.rego`, either binary, or the space definition **voids it**, and §6 of the
  preregistration requires it to be current at the freeze commit.

---

## 8. Reproduction

```
reference/cert_offgold.py --stage all [--with-sanctions-omitted]
```

Deterministic and RNG-free: three independent full runs produced identical space digest
(`5b289515206f07f9…`) and identical results digest (`78671e9ecd58700b…`). Individual stages
run standalone: `--stage bench-rego`, `--stage validate-sim`, `--stage grid-regression`,
`--stage run`.

Wall-clock on 16 cores: bench 8 s · simulator re-validation 13 s · grid regression 2 s ·
refA sweep 14 s · refB sweep 37 s · divergence engine-confirmation 0.7 s · verdict-class
coverage ~6 s · supplementary stratum ~2 min. **Total 248.0 s.**

The full 236,196-row per-cell result file (`offgold-results.jsonl.gz`, 3.2 MB) is
**regenerable and not committed** — the `refB/inputs` precedent from `AGREEMENT.md` — with
its uncompressed digest recorded in `OFFGOLD-CERT.json.fullResults`.

Artifacts, all under `design/reference/`: `cert_offgold.py` (the instrument; its module
docstring carries the full space derivation and method rationale), `OFFGOLD-CERT.json`
(authoritative), `OFFGOLD-CERT.md` (this file), and `refA/jps_sim.py` + `refA/project.py`
(copied verbatim from the arm-A builder's working directory into the study tree, so the
certificate's arm-A instrument is committed rather than referenced from a scratch path).
