# Off-gold equivalence certificate — Study 019

**Gate:** `PREREGISTRATION.md` §4 `GATE(pre-freeze)` — *"the two references' agreement is
re-established over the full derived input space, with every divergence point required to
fall inside a registered exclusion class; any other divergence blocks the freeze."*

**Reissued 2026-08-18** against the repaired arm-A reference
(`refA/PACK-CHANGE-001.md`, round-1 finding R1-2). The previous issue of this certificate
reported 72 divergences, all inside the registered exclusion class X1. **X1 is retired and
the registered exclusion set is now empty**, so this issue gates on the strongest form of
the sentence above: no divergence anywhere, excused by nothing.

**Verdict: PASS.** Over the **full** registered derived input space of **236,196 cells**,
the two references diverge on **zero cells**. Every reachable verdict class is reached, and
the two references' verdict censuses are now identical cell-count for cell-count.

Machine-readable companion: `OFFGOLD-CERT.json` (this file is its prose summary; the JSON
is authoritative where they differ).

---

## 1. Headline numbers

| | |
|---|---|
| Cells evaluated (registered space) | **236,196** |
| Divergences | **0** |
| Registered exclusion classes | **0 (empty registry; X1 retired 2026-08-18)** |
| `allDivergencesInRegisteredClasses` | **true** (vacuously — there are none) |
| Cells inside the **retired** X1 predicate, re-checked for agreement | **1,458 / 1,458 agree** |
| The retired class's own 72 cells, re-evaluated on the pinned engine | **72/72 answer `review`** in both references |
| Simulator artefacts (sim said "diverge", engine said "agree") | **0** |
| Validation records, all required to pass | **4/4 pass** |
| Total compute, excluding the supplementary stratum | **182.2 s** |
| Space digest (canonical enumeration) | `5b289515206f07f9…` (unchanged) |

The pattern this certificate used to report — `refA unresolved[unknown]` against
`refB review` on 72 cells — is **gone**, not excused:

```
refA (JPS pack, repaired, pinned jpack 0.17.0)  review
refB (Rego, pinned OPA 1.19.0)                  review
clean-room oracle (third opinion)               review
```

on all 72 of the cells that used to carry it, each one re-run on the **engine**, not the
simulator. The repair is enumerated and justified in `refA/PACK-CHANGE-001.md`; the short
version is that the prose fixes the determination for a whole *region*, the region can be
named without reading the unreadable member, and D8's escalate-on-unknown is suppressed
only inside that region. The claim X1 rested on — that no encoding in the fragment can
express it — was false; the weaker claim, that no `onUnknown` assignment over the
*original* pack shape rescues those cells, still holds and is not what X1 registered.

---

## 2. The space, and why its value sets represent every interval

The registered space is the one the arm-A builder derived (`refA/REPORT.md`,
`mutants/refA/REGISTRY.json` provenance): the full cross product of U1's substitution
representatives plus "unreadable"/"unreported" on every axis that admits it. **Unchanged
by the repair** — same axes, same values, same enumeration order, same digest.

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
both reference texts are short enough to read, and neither carries a seventh threshold. The
repair adds no threshold: `r-o1-wide-low` and `r-o1-wide-spend` read risk through 40 and 70
and spend through 100,000.00, all three already declared.

**Relation to the 2,540-cell design grid.** The grid and this space **overlap but neither
contains the other** — the grid carries risk 20/50/95 and spend 50000.00/3000000.00 which
this space does not, and this space carries U1's representatives which the grid does not.
The grid's `AGREEMENT.md` record is therefore **re-verified here as a control**, not
inherited (validation record 2 below). The repair changes **no** grid cell: `results.jsonl`
regenerates byte-identical from the repaired pack on the pinned engine.

---

## 3. Method — measured first, then chosen, with the numbers recorded

### 3a. Rego side: `opa exec` over a built bundle vs per-cell `opa eval`

Both methods were run on **the same 200 cells** and required to agree cell-for-cell before
either was used at scale.

| Method | ms/cell | Projected, full space | Capabilities enforced at |
|---|---|---|---|
| **`opa exec` over a built bundle** ← **chosen** | **0.310** | **~1.2 min** | **build time** (`opa build --capabilities`) |
| `opa eval` per cell (the `run_grid.py` method) | 21.75 | ~86 min | invocation (`opa eval --capabilities`) |

- **Speedup 70.2×**; both methods **agreed on 200/200 cells** (`methodsAgree: true`).
- `opa exec` does not accept `--capabilities` at v1.19.0 (TOOLCHAIN-NOTES), so the exec path
  enforces the denylist at **build** time — a strictly earlier and harder failure than a
  per-invocation flag. The power of that enforcement is re-checked here, not assumed: the
  `time.now_ns` canary is pushed through the same build path and is **refused**
  (`rego_type_error: undefined function time.now_ns`, exit 1).
- Actual full-space cost of the chosen method: **38.2 s**.

### 3b. JPS side: engine-validated simulator, with every divergence confirmed on the engine

The pinned engine costs ~16 ms/cell — ~63 minutes of subprocess churn for the space. The
sweep therefore runs on `refA/jps_sim.py` (13.6 s for the whole space), admitted **only**
under fresh re-validation, and **every divergence cell it finds is re-evaluated on the pinned
`jpack` binary**. The repair changed the pack, which **voided the previous revalidation
record**: it was re-earned against the repaired pack, not inherited. There are no divergences
left to confirm, so the engine's load in this issue is carried by the three validation
records plus the retired-X1 regression's 72 engine evaluations.

---

## 4. Validation records (all four required to pass; all four passed)

| # | Record | Population | Result |
|---|---|---|---|
| 1 | **simulator-revalidation** | **2,000-cell deterministic stratified subsample of *this* space** — 48 strata (`sanctions × country × riskReadable × spendReadable`), proportional largest-remainder allocation, systematic selection within stratum, **no RNG anywhere** | **0 disagreements / 2,000** between `jps_sim` and the pinned `jpack` on the **repaired** pack |
| 2 | **grid-regression** | the 2,540-cell design grid, re-evaluated by *this program's* two instruments and diffed against the **digest-pinned committed** `refA/results.jsonl` and `refB/results.jsonl` | **0** sim-vs-committed-refA, **0** exec-vs-committed-refB, **0** refA-vs-refB — `AGREEMENT.md`'s 2,540/2,540 reproduced under the repaired pack |
| 3 | **verdict-class-coverage** | up to 100 systematically-selected cells per **distinct refA verdict class** (748 cells over all 8 classes), re-evaluated on the pinned engine | **0 disagreements / 748** |
| 4 | **retired-x1-regression** (new) | every cell the retired X1 predicate names (1,458), plus its 72 registered cells on the pinned engine | **0 disagreements**; **72/72 answer `review`** in both references |

Why record 3 exists: records 1 and 2 bound the simulator on a *stratified-by-input* and a
*different-space* population. A simulator defect that lives in one output class (say, the
conflict path) could in principle dodge both. Record 3 is stratified by **output** and
covers every class the sweep produced.

Why record 4 exists: a repair that removes a divergence must be measured where the
divergence used to be, forever, or the next reader has only this document's word for it.
Record 4 re-derives "the repair moved exactly the cells the retired class named, and they
now carry the prose-correct answer" on every run.

**Toolchain digests** all match their pins (`OFFGOLD-CERT.json.toolchain`): `jpack`
`42f35f79…`, `opa` `1dd5c559…`, **`refA/pack.json` `db977607…` (was `956ceebb…`)**,
`refB/policy.rego` `1f2e1ad1…`, `cells.json` `da4ee85c…`, both committed `results.jsonl`
`d2cbfed2…`.

---

## 5. The zero divergences, and the class that used to be here

There is nothing to classify. What is worth recording is the shape of what was repaired.

| | Cells | Composition |
|---|---|---|
| Retired X1 predicate, coarse (as registered) | 1,458 | the registered sentence's mechanical reading |
| Retired X1, refined (as the builder measured it) | 72 | `sanctions = CLEAR`, `finEvidence = present`, `newVendor = yes`, `prior ≠ yes`, `critical ≠ yes`, risk ∈ {40, 69}, and either LOW with spend unreadable (24) or country unreadable with spend ≤ 100,000.00 (48) |
| Of the coarse 1,458, cells that ever diverged | **72** | the other 1,386 always agreed — the reviewer's R1-2 arithmetic, reproduced |
| Of those 72, cells now answering `review` in both references | **72** | engine-confirmed |

The 1,386-vs-72 gap is why a coarse registered predicate is a bad instrument even when it is
a true one: as an exclusion filter it would have removed 1,386 agreeing cells from arm A's
scored surface for no measured reason. The repair makes the question moot — with an empty
registry nothing is filtered — but the lesson stands for any class a later round proposes:
register the predicate you measured, not the sentence you can write quickly.

**Clean-room oracle.** The oracle is consulted as a third opinion on divergence cells; with
zero divergences it has nothing to arbitrate in this issue. It was consulted directly on the
72 repaired cells (`gold/check_gold.py`, `cleanroom/check_oracle.py`) and backs `review`
there, as it did before the repair — the difference is that it now agrees with **both**
references instead of one.

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

**18,954 divergences**, in a single refA/refB pattern — `unresolved[unknown]` vs
`unresolved[no-match]` — with the oracle landing on a *third* answer
(approve/reject/review/enhanced-review) on 14,706 of them. The repair changes none of this:
it is a different axis, and every one of the two new rules carries an explicit
`sanctionsStatus == CLEAR` conjunct, so an absent member leaves them unknown-and-ignored
exactly as it leaves every other rule.

**Reading:** this is undefined behaviour reported as undefined behaviour, not a reference
defect. An absent sanctions member is an input the prose does not define; refA answers
"no rule condition can be satisfied", refB answers with its total-function backstop, and the
oracle does not gate D3–D8 on CLEAR at all. Three implementations, three answers, on an
input no clause governs. It is precisely why the axis stays out of the registered space.

### What this certificate hands the freeze PR

§4 states the *reason* this gate exists: *"the E4 identity control evaluates author-written
inputs that roam off-gold; a reference defect there voids an arm."* Author-written test cases
can omit **any** member — including `sanctionsStatus`.

* **On the registered space the references now agree everywhere.** The identity control is
  safe there without any filter, which is what retiring X1 buys: no per-arm exclusion, no
  asymmetric filter, no published excluded-case count that only one arm can incur.
* **On sanctions-absent inputs they still do not agree**, and with the exclusion registry
  empty nothing covers it. The design side's position, offered as a recommendation and not a
  decision: this is **input-domain closure, not an exclusion class**. The prose admits no
  unreadable screening result, so an author case that omits the member is outside the
  registered input domain and should be rejected by a *domain validator applied identically
  to every arm* — the same check, in the same place, for A, B and C — with the per-run count
  published. Registering a second exclusion class would re-import the thing R1-2 objected
  to: an arm-shaped filter standing in for a domain rule. Either way the choice belongs in
  the preregistration, and doing neither leaves the identity control able to score an arm on
  an input whose "correct" answer no reference, and no oracle, agrees on.

---

## 7. What this certificate does not show

- It does **not** decide whether either reference is *right*. Gold (109 rows) and the
  clean-room oracle carry that burden; this instrument only establishes **agreement** and
  classifies the disagreements — of which there are now none.
- It is a **design-time gate instrument**. It publishes no study endpoint, adjudicates no
  hypothesis, and nothing in it is a study result.
- The risk/spend representation argument is **sound under a stated premise** (§2), not a
  proof over an arbitrary implementation. It is checked three ways; it is not a theorem.
- **Zero divergences is not proof that the two references mean the same thing.** It is proof
  that they answer the same way on 236,196 enumerated cells. §6 is the standing example of
  an input where they do not.
- The 236,196-cell space is **not** every input either engine can be handed — the
  sanctions-absent stratum (§6) is one measured example of what lies outside it, and the
  space says nothing about malformed documents, out-of-domain enum values, out-of-range
  numerics, or wrong JSON types.
- Agreement between two references is **not** interpretation-independence: both were built
  from the same prose under a shared engine-fact context. The oracle is the
  interpretation-independence instrument, and it is used here in a deliberately narrow role.
- Currency: the certificate is bound to the digests in §4. Any change to `refA/pack.json`,
  `refB/policy.rego`, either binary, or the space definition **voids it** — as the repair
  voided the previous issue — and §6 of the preregistration requires it to be current at the
  freeze commit.

---

## 8. Reproduction

```
reference/cert_offgold.py --stage all [--with-sanctions-omitted]
```

Deterministic and RNG-free: the space digest (`5b289515206f07f9…`) is unchanged from the
previous issue, because the repair changed the pack and not the space. Individual stages run
standalone: `--stage bench-rego`, `--stage validate-sim`, `--stage grid-regression`,
`--stage run`.

Wall-clock on 16 cores: bench 5 s · simulator re-validation 13 s · grid regression 3 s ·
refA sweep 13.6 s · refB sweep 38.2 s · verdict-class coverage ~6 s · retired-X1 regression
~1 s. **Total 182.2 s**, plus ~2 min for the supplementary stratum.

The full 236,196-row per-cell result file (`offgold-results.jsonl.gz`) is **regenerable and
not committed** — the `refB/inputs` precedent from `AGREEMENT.md` — with its uncompressed
digest recorded in `OFFGOLD-CERT.json.fullResults`
(`08aa57f01be2cb97…`; the previous issue's was a different file and a different digest).

Artifacts, all under `design/reference/`: `cert_offgold.py` (the instrument; its module
docstring carries the full space derivation and method rationale), `OFFGOLD-CERT.json`
(authoritative), `OFFGOLD-CERT.md` (this file), `refA/PACK-CHANGE-001.md` (the repair
record), and `refA/jps_sim.py` + `refA/project.py` (copied verbatim from the arm-A builder's
working directory into the study tree, so the certificate's arm-A instrument is committed
rather than referenced from a scratch path).
