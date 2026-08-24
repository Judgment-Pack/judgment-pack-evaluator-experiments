# V7 — the completeness argument, re-derived mechanically over the gold grid

**Status: DERIVED AND CLEAN.** All six assertions pass over all 117 gold cells:
every cell is governed by **exactly one** clause under the ladder's earliest-clause
tie-break, no cell is left ungoverned, every derived outcome equals the gold row's own
expectation, every derived governing clause is the first entry of that row's `cite`
list, and the former X1 region is **covered** rather than excluded — five named rows.
`verification/derive_v7.py` exits **0**.

**This artifact failed first, and §4 is the record of it.** The first derivation, run
2026-08-19 against gold `6a41174b…`, returned **104/117** on the cite-agreement
assertion and exited 1. It was not reconciled: the thirteen disagreements were
reported, two structural proofs were derived from the gold suite's own rows, the
maintainer adjudicated, and thirteen `cite` lists were reordered. The clean run below
is the run *after* that correction, and §4 names the correction, the rows, the
decision and the rule so that the passing status cannot be read as a first-try
success.

**This document is the registered artifact.** The reference build's 236,196-cell
derived-space sweep (`design/POLICY-DRAFT.md`, "Reference-build results") is
EVIDENCE — it is an implementation's sweep of a derived space, and it was the
instrument that retired X1 — but it is not the artifact the freeze gate names.
`harness/make_manifest.py`'s `REGISTERED_DOCUMENTS` names this file; `--check`
reports it while it is absent and `--freeze` refuses on it.

---

## Provenance

| What | Path | SHA-256 |
|---|---|---|
| Gold grid (117 rows) | `design/gold/gold.json` | `1ca1e5dd86fc2c7766db126cc51a792ab1a9aa5c8c6831321c932ad249361ab8` |
| Gold grid, frozen copy | `gold/GOLD.json` | `1ca1e5dd86fc2c7766db126cc51a792ab1a9aa5c8c6831321c932ad249361ab8` |
| Gold grid, **superseded** by §4's correction | (was `design/gold/gold.json`) | `6a41174bc6765781d4eae6eec610994240173fcdf97d442c8aeef6ce63bb9cc3` |
| Gold authoring transport (carries the correction note) | `design/gold/gold_author.py` | `06c234a1bd3cd5ec488d7cb48b426f2092318a61c10b54be5322e94d8531709f` |
| Policy prose (draft v0.3) | `design/POLICY-DRAFT.md` | `c4a533cab4dc6b6fa5e5f3b92d999ebf130cfbfaa5811ace49087c16612173bc` |
| Policy prose, frozen copy | `policy/POLICY.md` | `c4a533cab4dc6b6fa5e5f3b92d999ebf130cfbfaa5811ace49087c16612173bc` |
| Retired X1 predicate | `design/gold/check_gold.py::retired_x1` (source segment) | `242ef6becdf766cc5d0eed2084f2712f98a926ee84f884d3ce3dbd7fa44c594c` |
| Gold checker (whole file) | `design/gold/check_gold.py` | `cec45fa5bca1fef2e6cb50e40e620a21d1e2e222a7c81e2b88531129b3116b56` |
| This document's deriver | `verification/derive_v7.py` | `201cabfc50bd88e4d0709d42cf0c0f51e9cb3ad739d62f6b3cdf22e1bf8b4802` |

`gold/GOLD.json` and `policy/POLICY.md` — the two registered documents the freeze
step 2 lands — are **byte-identical** to the design sources this derivation read
(verified with `cmp`, not by digest transcription), so the derivation describes the
frozen tree and not only the design one. `goldVersion` is `0.2-draft`; the grid's own
`policy` member says `POLICY-DRAFT.md v0.3`. The deriver is unchanged across the
failing and the passing run — same file, same digest, different gold.

Run of record:

```
PYTHONDONTWRITEBYTECODE=1 <the pinned 3.12.11 interpreter> verification/derive_v7.py
```

117 cells and 11,947 ladder evaluations — the 90 fully readable cells once each, and
11,857 readable completions of the 27 cells carrying an unreadable input. No engine
invoked, no reference read, no subprocess started. **Exit status 0**, on a run
performed for this issue of the document and not transcribed from an earlier one.

---

## 1. What V7 asserts

`design/POLICY-DRAFT.md`, "Still open at this revision", registers V7 in these
words: *"re-derive the completeness argument mechanically over the gold grid (the
reference build's 236,196-cell derived-space sweep is evidence, not the registered
artifact), asserting exactly one governing clause per cell under the earliest-clause
tie-break. **There is no exclusion left to assert**: X1 is retired and the registered
exclusion set is empty, so V7 must instead assert that the former X1 region is
*covered* — an exclusion that once existed stays falsifiable."* `harness/SCAFFOLD.md`
step 2b names the same obligation as a freeze-fill step.

The derivation asserts six things. A1–A3 and A6 are the registered content; A4 is the
control that makes A5 readable; A5 tests the gold suite's citation convention, now
registered by the 2026-08-19 decision recorded in §4.

| | Assertion | Outcome |
|---|---|---|
| **A1** | 117 rows, ids unique, every cite entry a known clause, the spend quotient used by the U1 test checked rather than argued | **PASS** |
| **A2** | **Coverage.** Every cell — and every readable completion of every cell carrying an unreadable input — has at least one clause whose stated conditions hold: 117/117 cells over 11,947/11,947 ladder evaluations | **PASS** |
| **A3** | **Determinacy.** The order of application selects exactly one governing clause per cell: **117/117** | **PASS** |
| **A4** | **Reproduction.** The derived disposition and reason set equal the gold row's own expectation: **117/117** | **PASS** |
| **A5** | **Cite agreement.** The derived governing clause equals the row's first cite entry: **117/117** | **PASS** |
| **A6** | **X1 covered.** The region the retired X1 exclusion used to forbid carries gold rows, named below: **5 rows** | **PASS** |

Two further quantities are reported and gate nothing:

| | Reported | Outcome |
|---|---|---|
| **B1** | The derived governing clause appears **somewhere** in the row's cite list | **117/117** |
| **B2** | Purely lexical, no semantics: is `cite[0]` the earliest **cited** clause under the registered ladder? | **105/117** |

B2 is retained from the failing run, where it read 110/117, and it **falls** as the
artifact becomes correct. That is the registered convention working, not a
regression: a cite list now leads with the clause that GOVERNS, and the clauses
retained after it — the modifier O1, and contributing clauses such as O3, D5 and the
U1 meta-clause — may sit earlier in the ladder than the governing clause does. The
twelve rows where the two differ are the four `o1-nv-*` rows, the five `x1r-*` region
rows, `x1r-adjacent-both-unreadable`, `u1-risk-prior` and `u1-two-unreadable-uniform`.
§4.4 is why "earliest cited clause" is not the convention.

---

## 2. Method

### 2.1 What the tracer reads, and what it refuses to read

`verification/derive_v7.py` implements the **policy prose's own order of
application** — `design/POLICY-DRAFT.md`'s stimulus sections "Order of application",
"Precondition", "Determination clauses", "Overrides" and "Unreadable inputs" — and
nothing else. It does not consult, load, parse, execute or import:

- the arm-A reference implementation (`reference/refA/pack.json`, on the pinned jpack),
- the arm-B reference implementation (`reference/refB/policy.rego`, on the pinned OPA),
- the clean-room second oracle,
- or the gold **authoring transport** (`design/gold/gold_author.py`).

It makes no engine call and no subprocess call of any kind, and imports nothing
outside the Python standard library. This is the whole point of the exercise: a
completeness argument re-derived from an implementation asserts only that the
implementation agrees with itself, and the three instruments that already agree on
this grid (both references and the clean-room oracle) do not settle whether the PROSE
covers its own input space. The tracer is a fourth reading, taken from the text the
other three were built from — and §4 is what that independence bought.

One thing is taken from another file's code: the **retired X1 predicate**. It is
lifted as source out of `design/gold/check_gold.py`'s `retired_x1` with `ast` and
executed in an isolated namespace — the rest of that module, which does shell out to
both pinned engines, is never imported and never runs. Transcribing the predicate by
hand would put a second spelling of a registered region into the tree; lifting it
keeps one, and its source digest is in the provenance table.

### 2.2 The ladder, and the registered dependence rule

> "Clauses apply in this order: **P1** first; then the overrides **O3**, then **O2**;
> then the determination clauses **D1–D8**, as modified by **O1**. **U1** governs
> cases the clauses above leave undetermined because an input cannot be read; a
> determination issued by a clause that does not depend on the unreadable input
> stands (U1 states the test). Where more than one clause yields the same
> determination, the earliest clause in this order governs."

The tracer evaluates each clause's own sentence independently, producing the set of
clauses whose stated conditions hold on a cell (the CANDIDATES), and then applies the
order of application to that set. Splitting it this way is what makes A2 ("at least
one") and A3 ("exactly one, after the tie-break") two assertions rather than one
tautology. The order of application resolves unequal determinations as well as equal
ones — O2 "displaces every determination D1–D8 would issue", O3 "takes precedence
over every clause except P1" — so one rule serves both cases and the prose's
tie-break sentence is its equal-determination limb.

Three commitments are made explicitly, each anchored to the text. The third was this
document's interpretive choice on the failing run; the 2026-08-19 decision (§4.5)
**registered** it, so all three are now the study's convention rather than one
reading of it:

1. **O1 is not a rung.** It is a modifier of D6c's scope — "clause D6c does not
   apply; such requests fall to D8" — and D8's own sentence claims the region it
   vacates: "including requests removed from D6c by O1". O1 issues no determination,
   so it is never a candidate governor. (This is also the ladder as the freeze
   ceremony states it: *P1, O3, O2, D1..D8 as modified by O1, U1*.)
2. **U1 is the last rung**, and its counterfactual varies only the unreadable inputs
   — risk score, requested spend, country risk — with every other input keeping its
   reported state, comparing whole OUTCOMES (disposition plus reason set), exactly as
   U1's own sentence and its four worked examples prescribe.
3. **The standing-clause dependence rule.** "A determination issued by a clause that
   does not depend on the unreadable input stands" — registered wording: *a clause
   whose readable conjuncts already decide it stands*. The deriver operationalises it
   as **clause invariance** across the readable completions: if one clause governs
   every completion, that clause does not depend on the unreadable input on this cell
   and it governs; if the outcome is uniform but the issuing clause is not, no single
   clause issues the determination and U1 does; if the outcome is not uniform, U1
   governs and the case is unresolved as unknown. The registered wording and this
   operationalisation select the same clause on every cell of this grid — A5 is
   117/117 against cite lists that were reordered under the registered wording by a
   different hand.

The twelve cells on the `stands` route are exactly the cells the rule speaks about,
and the deriver prints them row by row (`READING EVIDENCE` block) so that the rule's
application is inspectable rather than asserted.

### 2.3 The completion domain

Risk is enumerated **exhaustively** over its registered domain, 0…100. Country is
enumerated over LOW, MEDIUM, HIGH. Spend is enumerated over a **quotient** of its
registered domain: the prose compares requested spend with exactly three literals
($100,000.00, $500,000.00, $2,000,000.00), so its domain splits into four intervals
on which every spend predicate is constant, each represented by both endpoints and an
interior point. The tracer does not argue that quotient — `spend_quotient_problems()`
asserts the constancy and the pairwise distinctness of the four predicate vectors, and
A1 fails if either breaks. 11,857 readable completions were evaluated across the 27
cells that need one, which with the 90 fully readable cells is 11,947 evaluations of
the ladder in all.

---

## 3. Result

### 3.1 Coverage and determinacy — the completeness argument itself

Every one of the 117 cells has at least one clause whose conditions hold, and so does
every readable completion of the 27 cells carrying an unreadable input — 11,947
ladder evaluations in all, 11,947 of them with a candidate. **There is no gap**: the
space is closed by P1 on the evidence axis, by D1/D2 on the non-CLEAR screening
results, and by D8's residual limb on everything CLEAR that D3–D7 do not determine —
including, by D8's own words, the region O1 removes from D6c.

Determinacy is not vacuous. 24 cells have more than one clause whose conditions hold,
and the earliest-clause tie-break resolves every one of them to a single governing
clause:

| Clauses whose conditions hold | Cells |
|---|---|
| 1 | 93 |
| 2 | 17 |
| 3 | 6 |
| 4 | 1 |
| **exactly one governing clause after the tie-break** | **117 / 117** |

By route:

| Route | Cells | Meaning |
|---|---|---|
| `readable` | 90 | nothing unreadable; the ladder decides directly |
| `stands` | 12 | one clause governs every readable completion — the determination stands |
| `u1-uniform` | 2 | uniform outcome, non-uniform issuing clause — U1 issues it |
| `u1-unknown` | 13 | outcomes differ across completions — unresolved as unknown |

### 3.2 Reproduction

The tracer reproduces **117/117** gold expectations — disposition and reason set,
exactly — reading only the prose. Both pinned engines and the clean-room oracle
already reproduce the same 117 (`design/gold/GOLD-NOTES.md`); this is a fourth,
implementation-free reproduction. It reproduced 117/117 **before** the §4 correction
as well, on the superseded gold: the correction touched no expectation, which is why
the correction is a citation repair and not a policy one.

### 3.3 Rows per governing clause

| Clause | Derived | Gold `cite[0]` | |
|---|---:|---:|---|
| P1 | 6 | 6 | |
| O3 | 6 | 6 | |
| O2 | 6 | 6 | |
| D1 | 4 | 4 | |
| D2 | 3 | 3 | |
| D3 | 6 | 6 | |
| D4 | 3 | 3 | |
| D5 | 3 | 3 | |
| D6a | 10 | 10 | |
| D6b | 13 | 13 | |
| O1 | 0 | 0 | never governs — see below |
| D6c | 4 | 4 | |
| D7 | 3 | 3 | |
| D8 | 35 | 35 | |
| U1 | 15 | 15 | |
| **total** | **117** | **117** | |

Every clause in the registered clause set governs at least one gold cell **except
O1**, which governs none and cannot: it issues no determination. O1's coverage in the
suite is real but indirect — nine rows cite it, and those nine are governed by D8
*because* O1 removed D6c. `check_gold.py`'s clause-coverage check reads the union of
the cite lists, so O1 remains covered; a check that read `cite[0]` alone would find O1
uncoverable by construction, which is a property of the clause and not a defect of the
suite.

### 3.4 A6 — the former X1 region is covered

The registered exclusion set is empty (`check_gold.py`, clause 2). The retired
predicate is kept as a non-gating census so that "gold now covers the region the
retired class used to forbid" is measured rather than asserted, and V7 asserts that
census non-empty. **Five gold rows are inside the region**, and each derives a
governing clause like any other cell:

| Row | Derived governing clause | Outcome | Gold cite |
|---|---|---|---|
| `x1r-low-spend-unreadable-40` | D8 | review | D8, O1, U1 |
| `x1r-low-spend-unreadable-69` | D8 | review | D8, O1, U1 |
| `x1r-country-unreadable-100k` | D8 | review | D8, O1, U1 |
| `x1r-country-unreadable-40` | D8 | review | D8, O1, U1 |
| `x1r-country-unreadable-69` | D8 | review | D8, O1, U1 |

`x1r-adjacent-both-unreadable` is the adjacency control and is **outside** the
region, as designed: with both country risk and requested spend unreadable the
determinations differ — a HIGH country above $2,000,000.00 escalates under O3 — so
U1 governs and the case is unresolved as unknown. The derivation confirms the
control's discriminating power from the prose alone: it derives U1/unknown, not
review, so a region rule written wider would be caught.

What the region means, re-derived: for a new vendor in the 40–69 risk band, O1
removes D6c and no other determination clause reaches the band, so every readable
value of the unreadable input lands on D8's review limb. The prose's answer is
review, uniformly, and the five rows witness it. The claim that this class was
**inexpressible in arm A** was retired on 2026-08-18 (round-1 finding R1-2,
`reference/refA/PACK-CHANGE-001.md`); V7's contribution is narrower and is the one
that stays falsifiable: the class is **covered by gold**, and the region's five
members and its adjacency control are named here so that a future edit that empties
the region fails a written census rather than passing unnoticed.

---

## 4. Corrections this artifact forced

### 4.1 The first derivation's finding, as it was reported

The first run of `verification/derive_v7.py` (same deriver, digest
`201cabfc…`; gold `6a41174b…`) reported:

```
A1 structure       PASS  117 rows, ids unique, cites well formed, spend quotient checked
A2 coverage        PASS  117/117 cells carry at least one clause, over 11947 ladder evaluations (90 fully readable cells once each; 11857 readable completions of the 27 cells carrying an unreadable input)
A3 determinacy     PASS  exactly one governing clause per cell; 24 cells have >1 candidate clause, all resolved by the earliest-clause tie-break
A4 reproduction    PASS  117/117 derived outcomes equal the gold expectation
A5 cite agreement  FAIL  104/117 derived governing clauses equal cite[0]
A6 X1 covered      PASS  5 gold rows inside the retired X1 region

B1 membership      117/117 derived governing clauses appear SOMEWHERE in the row's cite list
B2 ladder order    110/117 cite lists open with the earliest CITED clause under the registered ladder
                   not ladder-first: u1-ex1, u1-ex3, u1-risk-prior, u1-spend-med-95, u1-two-unreadable-uniform, u1-country-2m, x1r-adjacent-both-unreadable
```

with exit status 1 and the standing instruction obeyed: *"the disagreements above are
for the maintainer to adjudicate — this program reconciles nothing."* The registered
content of V7 (A2, A3, A6) passed then as it passes now; what failed was the claim
that the governing clause is each row's first cite entry.

### 4.2 The thirteen rows

| Row | Derived | Cite, before | Cite, after |
|---|---|---|---|
| `o1-nv-d6c` | D8 | O1, D8 | **D8**, O1 |
| `o1-nv-40-0` | D8 | O1, D8 | **D8**, O1 |
| `o1-nv-40-100k` | D8 | O1, D8 | **D8**, O1 |
| `o1-nv-69-100k` | D8 | O1, D8 | **D8**, O1 |
| `x1r-low-spend-unreadable-40` | D8 | O1, D8, U1 | **D8**, O1, U1 |
| `x1r-low-spend-unreadable-69` | D8 | O1, D8, U1 | **D8**, O1, U1 |
| `x1r-country-unreadable-100k` | D8 | O1, D8, U1 | **D8**, O1, U1 |
| `x1r-country-unreadable-40` | D8 | O1, D8, U1 | **D8**, O1, U1 |
| `x1r-country-unreadable-69` | D8 | O1, D8, U1 | **D8**, O1, U1 |
| `u1-ex1` | D3 | U1, D3 | **D3**, U1 |
| `u1-ex3` | O2 | U1, O2 | **O2**, U1 |
| `u1-spend-med-95` | D3 | U1, D3 | **D3**, U1 |
| `u1-country-2m` | D8 | U1, D8 | **D8**, U1 |

Nine rows opened with the **modifier O1**, which issues no determination while D8's
own sentence claims exactly those cells. Four opened with **U1** where a single clause
governs every readable completion: D3 rejects at risk 95 whatever the country
(`u1-ex1`) and whatever the spend (`u1-spend-med-95`); O2 reviews a critical supplier
whatever the risk (`u1-ex3`); D8 reviews at risk 50 with spend exactly $2,000,000.00
whatever the country (`u1-country-2m`, where O3's limb needs spend *above* the
literal).

### 4.3 Pinch 1 — the same situation, cited both ways

The finding was not an artifact of §2.2's third commitment. Compare two rows of the
suite as it then stood. Both carry unreadable inputs; in both, exactly one clause
governs every readable completion; and in both, the only higher-ranked clause that
reads an unreadable input (O3) is excluded by a conjunct that is *readable on the
cell*:

| Row | Unreadable | O3 excluded by | One clause governs every completion | `cite[0]`, before |
|---|---|---|---|---|
| `d1-match-bare` | country, risk, spend | its `screening result is CLEAR` conjunct (`MATCH`) | D1 | **D1** |
| `u1-ex1` | country | its `spend above $2,000,000.00` conjunct (`1,000,000.00`) | D3 | **U1** |

Any rule for "does this clause depend on the unreadable input?" that short-circuits a
definitely-false readable conjunct treats these two cells alike and yields the
standing clause in both (D1 and D3). Any rule that does not short-circuit treats them
alike and yields U1 in both. The suite cited them oppositely, so **no dependence test
that reads a readable conjunct the same way in both places reproduced both rows** —
whatever this document had committed to. `d2-unknown-bare` (D2) and
`o3-risk-unreadable` (O3) sat on the D1 side of the same pinch: unreadable inputs,
citing the standing clause rather than U1. Three rows on one side, four on the other;
the majority convention was the standing-clause one, and it is the one that was
registered.

### 4.4 Pinch 2 — no total order on clauses fits

If `cite[0]` were the earliest cited clause under some precedence order ≺, then
`u1-ex3` (`U1, O2`) required U1 ≺ O2, while the five `x1r-*` rows (`O1, D8, U1`)
required O1 ≺ U1 — hence **O1 ≺ U1 ≺ O2**. The registered ladder puts O2 before the
determination block and O1 inside it, i.e. **O2 ≺ O1**. The two are contradictory, so
no precedence order reproduced both families, and "reorder the cite lists to be
ladder-sorted" was not available as a repair. This is the proof that settled the
adjudication. Its shadow is B2's fall from 110/117 to 105/117 (§1): the surviving
convention is *governing clause first*, which is deliberately not *ladder-earliest
cited clause first*.

One row was further contradicted by the prose's own worked example. `u1-ex3` is
worked example 3, whose text reads: *"O2 determines the case without the risk score,
and no readable risk value changes it → review."* The example names O2 as the clause
that determines the case; the row cited U1 first.

### 4.5 The decision, and the rule it registered

**Taken and executed 2026-08-19, freeze ceremony: OPTION 1 — reorder the thirteen
cite lists.** The registered convention is the ladder's earliest-clause tie-break
under the **standing-clause dependence rule**: *a clause whose readable conjuncts
already decide it stands*, which is Pinch 1's D1-side and the convention the majority
of rows already followed. Pinch 2's cycle proof is what settled it, by eliminating the
alternative. Each of the thirteen lists was reordered to lead with the derived
governing clause, retaining the contributing clauses after it; a marked
`CITE-ORDER CORRECTION` note sits at the head of `design/gold/gold_author.py`, and
`gold.json` was regenerated from the transport and copied to `gold/GOLD.json`.

The two options not taken are recorded because a decision is only legible beside them:
amending the prose's order of application to make O1 a rung and U1 govern whenever its
counterfactual runs (Pinch 1 then bites the other way, moving `d1-match-bare`,
`d2-unknown-bare` and `o3-risk-unreadable` instead, and it edits the frozen stimulus);
or registering only the weaker B1 assertion and demoting `cite[0]` to documentation.

### 4.6 What moved, what did not, and what still binds the old digest

**Moved:** thirteen `cite` arrays, in `design/gold/gold_author.py` and the regenerated
`design/gold/gold.json` — 21 inserted and 21 deleted lines in the grid, all inside
`cite` arrays, and nothing else.

**Did not move:** every `inputs` object, every `expect` object, every `note`, the row
count, the row order, and the clause SET of all 117 cite lists. B1 was 117/117 before
the correction as well — the derived governing clause was already in each list, one
position later — so the repair moved position, not membership. A4 was 117/117 before
and after.

**Nothing downstream reads what moved.** `cite` is read in exactly one place in the
whole harness — `harness/score.py:1452`, which copies it into a failure report — so no
kill, no rate, no adequacy count and no published number depends on cite ORDER. What
does depend on the gold suite is its DIGEST, and the digest moved from `6a41174b…` to
`1ca1e5dd…`. At the time this document was re-issued the superseded digest was still
carried by:

| Artifact | Occurrences |
|---|---|
| `mutants/MANIFEST-jps.json` (registered document) | 183 |
| `mutants/MANIFEST-rego.json` (registered document) | 186 |
| `design/mutants/refA/MANIFEST.json` | 183 |
| `design/mutants/refB/MANIFEST.json` | 186 |
| `design/mutants/adequacy_pairing.json` | 1 |
| `design/gold/GOLD-NOTES.md` ("Gold sha256: …") | 1 |
| `PREREGISTRATION.md` line 371 (registered document, short form `6a41174b…`) | 1 |
| `harness/PINS.json` `goldSuite.sha256` | still `null`, to be filled at freeze step 5 with the NEW digest |

These are named here rather than repaired here: this document derives, it does not
edit the tree it describes. Because cite order feeds no computation, re-stamping them
is a digest refresh and not a re-derivation of any mutant, kill or adequacy result —
but that judgement, and the re-stamp, belong to the maintainer, and until it happens
the study's own currency tests are the place the staleness will surface.

---

## 5. Reproducing this document

```
PYTHONDONTWRITEBYTECODE=1 <the pinned 3.12.11 interpreter> verification/derive_v7.py
PYTHONDONTWRITEBYTECODE=1 <the pinned 3.12.11 interpreter> verification/derive_v7.py --full
```

The first prints every number in this document — the six assertions, the per-clause
table, the candidate multiplicities, the X1 census and the `READING EVIDENCE` block
that shows the standing-clause rule applied row by row. The second adds the whole
117-row derivation. Exit status is 0 iff A1–A6 all pass; it is **0** as this document
is issued, and it was 1 on the run recorded in §4.1.

Two things a reader should know about the derivation's place in the tree:

- **`verification/derive_v7.py` is not in the study manifest** as this document is
  issued. `manifest_entries()` covers the registered documents, the registered payload
  sets, and `harness/*.py`, `harness/*.sh`, `harness/e4lib/*.py`,
  `harness/tests/*.py`. A `.py` under `verification/` matches none of those globs, so
  the source that produced this registered document is uncovered while the document is
  covered. That is round-1 finding **R1-9**'s shape — a manifest that covered the prose
  and not the bytes that produce it — one level over. The maintainer is registering
  coverage separately; this paragraph stays until the glob or the registered set
  actually names the file, because the gap belongs on the record and not in a memory.
- The derivation writes nothing, reads five files, and starts no process, so it is
  safe to run against the frozen tree at any time — including after the freeze, which
  is when a completeness argument is worth re-running.

## 6. Scope and limits

- V7 is an argument about the **gold grid**, 117 cells, not about the whole input
  space. The 236,196-cell derived-space sweep behind the X1 retirement is a wider
  instrument and remains evidence; it is an implementation's sweep, which is why it is
  not this artifact.
- The completion domain for U1 is exhaustive in risk and country and a **checked
  quotient** in spend (§2.3). A policy edit that introduced a fourth spend literal
  would invalidate the quotient, and A1 would fail rather than the answer silently
  drifting.
- A4's reproduction is a strong control but not an independence claim: the prose, the
  gold suite and both references share an author side (`design/gold/GOLD-NOTES.md`).
  The independence instrument in this study is the clean-room oracle. What V7 adds is
  narrower and different in kind: the argument is re-derived from the TEXT, by a
  program that cannot see any implementation. No instrument in this study has ever
  disagreed with a gold EXPECTATION, and V7 did not either — before or after the
  correction, A4 was 117/117. It disagreed with the ORDER of thirteen cite lists, a
  field no instrument before it read, and §4 is what came of that.
