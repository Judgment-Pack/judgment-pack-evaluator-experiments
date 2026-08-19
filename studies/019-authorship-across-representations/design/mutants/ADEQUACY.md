# Adequacy gate — the 47 JPS + 60 Rego empty-witness mutants

> ## SUPERSEDED, 2026-08-18 — read [the round-3 section](#round-3-gate-closure--the-37-jps--34-rego-empty-witness-mutants-of-the-repaired-corpus) at the foot of this file for the current gate
>
> This document is the verbatim record of the **2026-08-15** run against the **pre-repair**
> corpus. Its ids are not the current corpus's ids and its counts are not the current
> counts. The gate it reports was re-opened by the arm-A reference repair and **re-closed on
> 2026-08-18 by the round-3 section below** (review finding R3-2): 37 JPS + 34 Rego
> empty-witness mutants disposed of, 8 gold rows added, gold at **117 rows**, JPS
> **157/183** and Rego **150/184** killed, **0 undispositioned in either arm**.
>
> The arm-A reference was repaired (`reference/refA/PACK-CHANGE-001.md`, round-1 finding
> R1-2): X1 is retired and `refA/pack.json` gained two rules and four exceptions. **A mutant
> corpus is a function of its reference**, so the JPS corpus was regenerated from the
> repaired pack and the Rego corpus was re-witnessed against the grown gold suite. What
> that changed, measured (the right-hand column is the state the round-3 section then
> disposed of, not the current one):
>
> | | this document (2026-08-15) | after the repair (2026-08-18) |
> |---|---|---|
> | gold rows | 105 | **109** |
> | JPS mutants generated / valid | 145 / 145 | **183 / 183** |
> | JPS killed by gold | 128 | **146** |
> | JPS empty-witness, **undispositioned** | 0 | **37** |
> | Rego mutants generated / valid | 185 / 184 | 185 / 184 (reference unchanged) |
> | Rego killed by gold | 150 | **150** |
> | Rego empty-witness, **undispositioned** | 0 | **34** |
>
> **The adequacy gate was therefore NOT satisfied at this moment**, and nothing downstream
> could say it was — the round-3 section below is where it is closed again. Mutant **ids do
> not carry across the repair**: the two new rules insert
> ordered comparisons in the middle of the deterministic enumeration, so `m-a-NNN` in this
> document and `m-a-NNN` in the current manifest are different edits. Every drop mechanism
> recorded below was written against the pre-repair ids and must be re-derived, not
> re-keyed; `adequacy_search.py`'s `DROPS` table is pre-repair data and the manifest-stamp
> step (`--manifests`, `--registry`) is fail-closed until it is rewritten.
>
> What survives the repair unchanged: the method (dense 419,904-cell search, engine
> confirmation of every witness, two independent transcriptions for the negative verdicts),
> the drop-mechanism taxonomy, and the finding that the arm-A corpus contains kills only the
> engine's structural conflict detection can supply — that last one now measured properly
> over the whole domain rather than over gold witnesses (round-1 R1-11; see
> `adequacy_engine_supplied.json`, and note the exclusion registry is empty, so "outside X1"
> now means "anywhere").
>
> Everything below is left verbatim as the record of the 2026-08-15 gate run.

**Status: design-time gate run, 2026-08-15. Not a freeze artifact yet; every number here is
reproducible from `mutants/adequacy_search.py` and the two MANIFESTs it writes.**

The registered rule (PREREGISTRATION.md §4): *every mutant is either killed by gold (witness
set non-empty) or registered as dropped with its mechanism.* The work list was the
empty-witness remainder of the two generators — 47 of 145 JPS mutants, 60 of 184 valid Rego
mutants. This document is the disposition of all 107.

## Result

| | JPS (arm A) | Rego (arm B) |
|---|---|---|
| valid mutants | 145 | 184 |
| killed by gold **before** this gate | 98 | 124 |
| work list (empty witness) | 47 | 60 |
| → killed by a row added here | **30** | **26** |
| → registered as dropped, with mechanism | **17** | **34** |
| killed by gold **after** this gate | **128** | **150** |
| empty witness sets remaining | 0 | 0 |

**The gate is satisfied: no mutant in either arm is left undisposed.** Gold grew from 76 to
**105 rows** (29 added). Every added row was authored from the policy prose with a clause
citation; the search says only *where* to look.

Kill counts with and without the engine-supplied kills §4 requires reported separately:
arm A's conflict-only mutants (killed only through the engine's structural `unresolved
{conflict}`, which arm B has no counterpart for) go from **35 of 98** to **41 of 128** —
assertion-only kills 63 → 87. Nine of the 30 newly killed arm-A mutants are conflict-only
**by construction**: `adequacy_search.py --killcensus` enumerated every cell of the dense
space at which they differ from the reference, and at all of them the mutant's output is
`unresolved{conflict}`. No gold row anywhere can kill those nine any other way; this is a
property of the arm-A encoding (D8's negation cascade duplicates each approval rule's
literals, so widening one of those rules always produces a same-region overlap of two
different outcomes), not of the gold suite, and it belongs in the asymmetry ledger.

## Method

**Search space.** 419,904 cells, the dense derived space the work list prescribes:
sanctions ∈ {CLEAR, MATCH, UNKNOWN}; country ∈ {LOW, MEDIUM, HIGH, omitted}; risk at every
band boundary (40/70/90) minus one, at, plus one, plus the domain endpoints 0 and 100, plus
omitted (12); spend at every boundary (100,000.00/500,000.00/2,000,000.00) minus a cent, at,
plus a cent, plus 0.00 and 10,000,000.00, plus omitted (12); all tri-state combinations of
the three yes/no statuses and both evidence axes (3⁵). The space carries no malformed or
out-of-range values, matching the registered projection.

*Why those representatives suffice.* Every clause and every rung reads risk and spend only
through comparisons against the six declared thresholds, and one mutation edits one operator
or shifts one threshold by one representable step, so the reachable comparison boundaries lie
between consecutive members of {38|39, 39|40, 40|41, 41|42, 68|69, …} and their spend
analogues. Every reachable boundary is straddled by two adjacent representatives above, so a
cell strictly inside an interval (risk 50, say) cannot distinguish a single-edit mutant that
its interval's representatives do not. A *two*-edit mutant could escape this argument; the
generators register one edit per mutant.

**Candidacy.** The registered X1 exclusion is applied to candidacy, not to evaluation: X1
cells are swept and counted, but a witness inside X1 cannot become a gold row (check_gold.py
asserts the exclusion), so it cannot kill. No mutant in either arm turned out to be
distinguishable *only* inside X1 — the X1-only count is 0 in both arms, which is worth
recording because it means the exclusion cost the adequacy gate nothing.

**Arm B is searched by the pinned engine itself.** Reference and mutant are loaded into one
OPA process (the mutant's `package study` textually renamed to `package study_mut` for the
search only) and one comprehension reports every row where the two entrypoint values differ.
No model of Rego is involved anywhere in arm B's results.

**Arm A is searched by a transcription of JPS Core 0.2.0-draft §7–§8**, because the pinned
`jpack` CLI evaluates one facts document per process (~19 ms) and the sweep is 419,904 cells
per mutant. The transcription is not trusted on its own word:

1. `--validate`: 2,076 checked evaluations against the pinned binary (all 76 v0 gold rows plus
   a seeded random sample of the dense space on the reference pack; 40 sampled cells on each
   of the 47 work-list mutants) — **0 disagreements**.
2. `--confirm`: every witness the transcription reported (240 = 30 mutants × 8 recorded
   witnesses) re-run on the pinned binary against both the mutant and the reference — **0
   unconfirmed**; the engine reproduces the predicted output on both sides at every one.
3. `--drops`: for the 17 arm-A mutants the sweep found nowhere distinguishable, the cells
   where the *edit is live* (the mutant's rule/exception condition vector differs from the
   reference's) were enumerated and a deterministic sample of them (120 per mutant, 720 in
   total) was handed to the pinned binary on both packs — **0 differences**. Five of the 17
   have **zero** live-edit cells: their edit never changes any rule's value anywhere.
4. `--mechanisms`: the two mechanisms the six `onUnknown` drops rest on are checked
   directly over the whole space, because an `onUnknown` edit is invisible to a condition
   vector (see the mechanism table).
5. `--crosscheck`: all 17 arm-A drop verdicts re-run over the whole 419,904-cell space with
   the **second, independently written §7/§8 transcription** that the reference build left in
   `reference/refA/jps_sim.py` (a different author-side artifact, written for the onUnknown
   enumeration and itself validated cell-for-cell against the pinned engine) — **0
   disagreements**. Two independently written transcriptions, each engine-validated, is what
   a negative claim over 419,904 cells can be given short of 419,904 process launches.

Every arm-A killing row was additionally re-derived on the pinned binary by
`check_gold.py`'s floor gate after the rows were authored. **What remains transcription-borne
is only the negative claim** for arm A — "no cell of the dense space distinguishes this
mutant" — backed by (1)–(4) above. Arm B's negative claims are engine-borne.

## The agreement chain, re-run after the additions

| check | result |
|---|---|
| `gold/check_gold.py` — structure, X1 exclusion, clause coverage, boundary witnesses | 105 rows, **0 failures** |
| …its floor gate: pinned jpack 0.17.0 over `reference/refA/pack.json` | reproduces **105/105** |
| …its floor gate: pinned OPA 1.19.0 over `reference/refB/policy.rego` | reproduces **105/105** |
| `cleanroom/check_oracle.py` — clean-room second oracle vs gold | **105/105 agree** |
| `cleanroom/check_oracle.py` — oracle vs refA over the 2,540-cell design grid | 2,540/2,540, 0 unexpected divergences |

**No oracle disagreement arose, so nothing had to be retained verbatim.** All 29 additions
were reproduced by both engines and by the clean-room oracle on the first run, with zero
adjudicated corrections — the same standing as the v0 rows.

## Rows added (gold v0 → v0.1)

All 29 live in a clearly marked `==== gold v0.1 — ADEQUACY-GATE ADDITIONS ====` section of
`gold/gold_author.py`, each with the sentence it was derived from in its note. The base cell
is the file's `BASE` (CLEAR, LOW, risk 20, spend 50,000.00, all statuses "no", both evidence
documents present); "—" means the key is omitted (unreadable / unreported). "kills A/B" is
the number of arm-A / arm-B mutants for which this row is a witness.

| row | inputs (delta from the base cell) | expectation | cites | kills A/B |
|---|---|---|---|---|
| `d8-low-40-500k01-ins-present` | risk=40, spend=500000.01 | **review** | D8 | 5/23 |
| `d8-low-40-500k01-ins-absent` | insurance=absent, risk=40, spend=500000.01 | **review** | D8 | 5/23 |
| `d8-low-40-500k01-ins-unreported` | insurance=—, risk=40, spend=500000.01 | **review** | D8 | 5/20 |
| `d6b-39-500k01-present` | risk=39, spend=500000.01 | **approve** | D6b | 6/22 |
| `d6b-39-500k01-absent` | insurance=absent, risk=39, spend=500000.01 | **enhanced-review** | D6b | 7/26 |
| `d6b-39-500k01-unreported` | insurance=—, risk=39, spend=500000.01 | **unresolved{unknown}** | D6b | 2/19 |
| `d6a-500k-ins-absent` | insurance=absent, spend=500000.00 | **approve** | D6a | 8/21 |
| `d6a-500k-ins-unreported` | insurance=—, spend=500000.00 | **approve** | D6a | 6/21 |
| `d6b-2m-absent` | insurance=absent, spend=2000000.00 | **enhanced-review** | D6b | 6/25 |
| `d6b-2m-unreported` | insurance=—, spend=2000000.00 | **unresolved{unknown}** | D6b | 1/18 |
| `d8-2m01-low-absent` | insurance=absent, spend=2000000.01 | **review** | D8 | 3/24 |
| `d8-2m01-low-unreported` | insurance=—, spend=2000000.01 | **review** | D8 | 3/22 |
| `d6b-500k01-absent` | insurance=absent, spend=500000.01 | **enhanced-review** | D6b | 5/25 |
| `d6b-500k01-unreported` | insurance=—, spend=500000.01 | **unresolved{unknown}** | D6b | 2/18 |
| `d8-med-500k01-present` | country=MEDIUM, spend=500000.01 | **review** | D8 | 1/20 |
| `d8-med-500k01-absent` | country=MEDIUM, insurance=absent, spend=500000.01 | **review** | D8 | 1/20 |
| `d8-med-500k01-unreported` | country=MEDIUM, insurance=—, spend=500000.01 | **review** | D8 | 1/19 |
| `o1-nv-40-0` | newVendor=yes, risk=40, spend=0.00 | **review** | O1, D8 | 6/20 |
| `o1-nv-40-100k` | newVendor=yes, risk=40, spend=100000.00 | **review** | O1, D8 | 8/20 |
| `o1-nv-69-100k` | newVendor=yes, risk=69, spend=100000.00 | **review** | O1, D8 | 5/18 |
| `d6a-nv-39-0` | newVendor=yes, risk=39, spend=0.00 | **approve** | D6a | 5/20 |
| `d8-nv-70-100k` | newVendor=yes, risk=70, spend=100000.00 | **review** | D8 | 3/18 |
| `d8-nv-40-100k01` | newVendor=yes, risk=40, spend=100000.01 | **review** | D8 | 6/18 |
| `u1-country-2m01` | country=—, risk=50, spend=2000000.01 | **unresolved{unknown}** | U1 | 2/9 |
| `u1-country-2m` | country=—, risk=50, spend=2000000.00 | **review** | U1, D8 | 3/23 |
| `u1-country-39-500k01-absent` | country=—, insurance=absent, risk=39, spend=500000.01 | **unresolved{unknown}** | U1 | 4/15 |
| `u1-country-39-500k01-present` | country=—, risk=39, spend=500000.01 | **unresolved{unknown}** | U1 | 4/15 |
| `u1-country-2m-absent` | country=—, insurance=absent, spend=2000000.00 | **unresolved{unknown}** | U1 | 4/15 |
| `d1-match-o3-region` | country=HIGH, risk=50, sanctions=MATCH, spend=2000000.01 | **reject** | D1 | 1/11 |

Two regions carried almost all of it, and both were regions the v0 grid probed at one point
rather than at its edges: **D6b's band** ($500,000.01–$2,000,000.00 in LOW) at its own three
edges, at the risk-40 edge, across all three insurance states, and in a MEDIUM country where
it does not exist; and **the region O1 removes from D6c** (new vendor, 40 ≤ risk < 70, spend
≤ $100,000.00) at its four edges. The rest is U1 against those regions with the country
unreadable, plus one MATCH cell inside O3's region.

## Disposition table — arm A (JPS), the 47 work-list mutants

Edits are abbreviated: `r-x.cond[i]` is condition *i* of rule `r-x`'s `all`, `r-d8.cascade[j]`
is disjunct *j* inside r-d8's `not(any …)`. ⚠conflict-only marks a mutant whose every witness
cell (gold row) yields `unresolved{conflict}` — an engine-supplied kill.

| mutant | class | edit | disposition | killing row (witnessing cells) / drop mechanism |
|---|---|---|---|---|
| `m-a-005` | operator-flip | r-d6b-insured.cond[2].operator: less-than -> less-than-or-equal | killed | `d8-low-40-500k01-ins-present` (36 cells) ⚠conflict-only |
| `m-a-006` | operator-flip | r-d6b-insured.cond[3].operator: greater-than -> greater-than-or-equal | **dropped** | same-outcome-overlap |
| `m-a-008` | operator-flip | r-d6b-uninsured.cond[2].operator: less-than -> less-than-or-equal | killed | `d8-low-40-500k01-ins-absent` (36 cells) ⚠conflict-only |
| `m-a-009` | operator-flip | r-d6b-uninsured.cond[3].operator: greater-than -> greater-than-or-equal | killed | `d6a-500k-ins-absent` (24 cells) ⚠conflict-only |
| `m-a-010` | operator-flip | r-d6b-uninsured.cond[4].operator: less-than-or-equal -> less-than | killed | `d6b-2m-absent` (24 cells) |
| `m-a-016` | operator-flip | r-o1-review.cond[0][2].operator: greater-than-or-equal -> greater-than | killed | `o1-nv-40-0` +1 (36 cells) |
| `m-a-017` | operator-flip | r-o1-review.cond[0][3].operator: less-than -> less-than-or-equal | **dropped** | same-outcome-overlap |
| `m-a-018` | operator-flip | r-o1-review.cond[0][4].operator: less-than-or-equal -> less-than | killed | `o1-nv-40-100k` +1 (36 cells) |
| `m-a-023` | operator-flip | r-d8.cond[1].cascade[3][2].operator: less-than -> less-than-or-equal | killed | `d8-low-40-500k01-ins-present` +1 (144 cells) |
| `m-a-024` | operator-flip | r-d8.cond[1].cascade[3][3].operator: greater-than -> greater-than-or-equal | **dropped** | shadowed-cascade-branch |
| `m-a-026` | operator-flip | r-d8.cond[1].cascade[4][2].operator: less-than -> less-than-or-equal | killed | `d8-low-40-500k01-ins-absent` +1 (144 cells) |
| `m-a-027` | operator-flip | r-d8.cond[1].cascade[4][3].operator: greater-than -> greater-than-or-equal | **dropped** | shadowed-cascade-branch |
| `m-a-028` | operator-flip | r-d8.cond[1].cascade[4][4].operator: less-than-or-equal -> less-than | killed | `d6b-2m-absent` +1 (48 cells) |
| `m-a-041` | boundary-shift | r-d6a.cond[3].value: 500000.00 -> 500000.01 (+1) | killed | `d6b-39-500k01-absent` +1 (24 cells) ⚠conflict-only |
| `m-a-043` | boundary-shift | r-d6b-insured.cond[2].value: 40 -> 41 (+1) | killed | `d8-low-40-500k01-ins-present` (36 cells) ⚠conflict-only |
| `m-a-044` | boundary-shift | r-d6b-insured.cond[2].value: 40 -> 39 (-1) | killed | `d6b-39-500k01-present` (36 cells) |
| `m-a-046` | boundary-shift | r-d6b-insured.cond[3].value: 500000.00 -> 499999.99 (-1) | **dropped** | same-outcome-overlap |
| `m-a-049` | boundary-shift | r-d6b-uninsured.cond[2].value: 40 -> 41 (+1) | killed | `d8-low-40-500k01-ins-absent` (36 cells) ⚠conflict-only |
| `m-a-050` | boundary-shift | r-d6b-uninsured.cond[2].value: 40 -> 39 (-1) | killed | `d6b-39-500k01-absent` (36 cells) |
| `m-a-051` | boundary-shift | r-d6b-uninsured.cond[3].value: 500000.00 -> 500000.01 (+1) | killed | `d6b-39-500k01-absent` +1 (24 cells) |
| `m-a-052` | boundary-shift | r-d6b-uninsured.cond[3].value: 500000.00 -> 499999.99 (-1) | killed | `d6a-500k-ins-absent` (24 cells) ⚠conflict-only |
| `m-a-053` | boundary-shift | r-d6b-uninsured.cond[4].value: 2000000.00 -> 2000000.01 (+1) | killed | `d8-2m01-low-absent` (24 cells) ⚠conflict-only |
| `m-a-054` | boundary-shift | r-d6b-uninsured.cond[4].value: 2000000.00 -> 1999999.99 (-1) | killed | `d6b-2m-absent` (24 cells) |
| `m-a-056` | boundary-shift | r-d6c.cond[2].value: 40 -> 39 (-1) | **dropped** | same-outcome-overlap |
| `m-a-065` | boundary-shift | r-o1-review.cond[0][2].value: 40 -> 41 (+1) | killed | `o1-nv-40-0` +1 (36 cells) |
| `m-a-066` | boundary-shift | r-o1-review.cond[0][2].value: 40 -> 39 (-1) | killed | `d6a-nv-39-0` (36 cells) ⚠conflict-only |
| `m-a-067` | boundary-shift | r-o1-review.cond[0][3].value: 70 -> 71 (+1) | **dropped** | same-outcome-overlap |
| `m-a-068` | boundary-shift | r-o1-review.cond[0][3].value: 70 -> 69 (-1) | killed | `o1-nv-69-100k` (36 cells) |
| `m-a-069` | boundary-shift | r-o1-review.cond[0][4].value: 100000.00 -> 100000.01 (+1) | **dropped** | same-outcome-overlap |
| `m-a-070` | boundary-shift | r-o1-review.cond[0][4].value: 100000.00 -> 99999.99 (-1) | killed | `o1-nv-40-100k` +1 (36 cells) |
| `m-a-077` | boundary-shift | r-d8.cond[1].cascade[2][3].value: 500000.00 -> 500000.01 (+1) | killed | `d6b-39-500k01-unreported` +1 (24 cells) |
| `m-a-079` | boundary-shift | r-d8.cond[1].cascade[3][2].value: 40 -> 41 (+1) | killed | `d8-low-40-500k01-ins-present` +1 (144 cells) |
| `m-a-080` | boundary-shift | r-d8.cond[1].cascade[3][2].value: 40 -> 39 (-1) | killed | `d6b-39-500k01-present` +1 (72 cells) |
| `m-a-082` | boundary-shift | r-d8.cond[1].cascade[3][3].value: 500000.00 -> 499999.99 (-1) | **dropped** | shadowed-cascade-branch |
| `m-a-085` | boundary-shift | r-d8.cond[1].cascade[4][2].value: 40 -> 41 (+1) | killed | `d8-low-40-500k01-ins-absent` +1 (144 cells) |
| `m-a-086` | boundary-shift | r-d8.cond[1].cascade[4][2].value: 40 -> 39 (-1) | killed | `d6b-39-500k01-absent` +1 (72 cells) |
| `m-a-087` | boundary-shift | r-d8.cond[1].cascade[4][3].value: 500000.00 -> 500000.01 (+1) | killed | `d6b-39-500k01-absent` +2 (48 cells) |
| `m-a-088` | boundary-shift | r-d8.cond[1].cascade[4][3].value: 500000.00 -> 499999.99 (-1) | **dropped** | shadowed-cascade-branch |
| `m-a-089` | boundary-shift | r-d8.cond[1].cascade[4][4].value: 2000000.00 -> 2000000.01 (+1) | killed | `d8-2m01-low-absent` +1 (48 cells) |
| `m-a-090` | boundary-shift | r-d8.cond[1].cascade[4][4].value: 2000000.00 -> 1999999.99 (-1) | killed | `d6b-2m-absent` +1 (48 cells) |
| `m-a-092` | boundary-shift | r-d8.cond[1].cascade[5][2].value: 40 -> 39 (-1) | **dropped** | shadowed-cascade-branch |
| `m-a-103` | onUnknown-flip | r-d1.onUnknown: ignore -> escalate | **dropped** | never-unknown-rule |
| `m-a-107` | onUnknown-flip | r-d6a.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-108` | onUnknown-flip | r-d6b-insured.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-109` | onUnknown-flip | r-d6b-uninsured.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-110` | onUnknown-flip | r-d6c.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-111` | onUnknown-flip | r-d7.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |


## Disposition table — arm B (Rego), the 60 work-list mutants

| mutant | class | edit | disposition | killing row (witnessing cells) / drop mechanism |
|---|---|---|---|---|
| `m-b-006` | operator-flip | D6b: `risk < 40` -> `risk <= 40` | killed | `d8-low-40-500k01-ins-present` (72 cells) |
| `m-b-007` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-009` | operator-flip | D6b: `risk < 40` -> `risk <= 40` | killed | `d8-low-40-500k01-ins-absent` (72 cells) |
| `m-b-010` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-011` | operator-flip | D6b: `spend <= 2000000` -> `spend < 2000000` | killed | `d6b-2m-absent` (24 cells) |
| `m-b-012` | operator-flip | D6b: `risk < 40` -> `risk <= 40` | killed | `d8-low-40-500k01-ins-absent` +2 (216 cells) |
| `m-b-013` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-014` | operator-flip | D6b: `spend <= 2000000` -> `spend < 2000000` | killed | `d6b-2m-unreported` (48 cells) |
| `m-b-022` | boundary-shift | O3: spend threshold 2000000 +0.01 -> 2000000.01 | killed | `u1-country-2m01` (828 cells) |
| `m-b-030` | boundary-shift | D6a: spend threshold 500000 +0.01 -> 500000.01 | killed | `d6b-39-500k01-absent` +3 (48 cells) |
| `m-b-031` | boundary-shift | D6b: risk threshold 40 -1 -> 39 | killed | `d6b-39-500k01-present` (36 cells) |
| `m-b-032` | boundary-shift | D6b: risk threshold 40 +1 -> 41 | killed | `d8-low-40-500k01-ins-present` (72 cells) |
| `m-b-033` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-037` | boundary-shift | D6b: risk threshold 40 -1 -> 39 | killed | `d6b-39-500k01-absent` (36 cells) |
| `m-b-038` | boundary-shift | D6b: risk threshold 40 +1 -> 41 | killed | `d8-low-40-500k01-ins-absent` (72 cells) |
| `m-b-039` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-040` | boundary-shift | D6b: spend threshold 500000 +0.01 -> 500000.01 | killed | `d6b-39-500k01-absent` +1 (24 cells) |
| `m-b-041` | boundary-shift | D6b: spend threshold 2000000 -0.01 -> 1999999.99 | killed | `d6b-2m-absent` (24 cells) |
| `m-b-042` | boundary-shift | D6b: spend threshold 2000000 +0.01 -> 2000000.01 | killed | `d8-2m01-low-absent` (24 cells) |
| `m-b-043` | boundary-shift | D6b: risk threshold 40 -1 -> 39 | killed | `d6b-39-500k01-unreported` (72 cells) |
| `m-b-044` | boundary-shift | D6b: risk threshold 40 +1 -> 41 | killed | `d8-low-40-500k01-ins-absent` +2 (216 cells) |
| `m-b-045` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-046` | boundary-shift | D6b: spend threshold 500000 +0.01 -> 500000.01 | killed | `d6b-39-500k01-unreported` +1 (48 cells) |
| `m-b-047` | boundary-shift | D6b: spend threshold 2000000 -0.01 -> 1999999.99 | killed | `d6b-2m-unreported` (48 cells) |
| `m-b-049` | boundary-shift | D6c: risk threshold 40 -1 -> 39 | **dropped** | ladder-order-masked |
| `m-b-060` | boundary-shift | O3: spend threshold 2000000 +0.01 -> 2000000.01 | **dropped** | duplicated-test |
| `m-b-062` | unknown-guard-flip | O3/P1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-083` | unknown-guard-flip | O3 (evidence-availability tri-state): invert `fin_state == "present"` | **dropped** | duplicated-test |
| `m-b-084` | unknown-guard-flip | O3 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-085` | unknown-guard-flip | O3 (unreadable-input sentinel (omitted key)): invert `v_spend != null` | **dropped** | duplicated-test |
| `m-b-086` | unknown-guard-flip | O3 (unreadable-input sentinel (omitted key)): delete `v_spend != null` | **dropped** | entailed-guard |
| `m-b-088` | unknown-guard-flip | U1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-090` | unknown-guard-flip | U1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-124` | default-swap | registered default: reasons no-match -> unknown | **dropped** | unreachable-default |
| `m-b-125` | default-swap | registered default: disposition unresolved -> review (reasons left as authored) | **dropped** | unreachable-default |
| `m-b-132` | guard-deletion | D3: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-134` | guard-deletion | D4: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-137` | guard-deletion | D5: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-138` | guard-deletion | D6a: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-142` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-143` | guard-deletion | D6b: delete scoping conjunct `country == "LOW"` | killed | `d8-med-500k01-present` +1 (216 cells) |
| `m-b-144` | guard-deletion | D6b: delete scoping conjunct `risk < 40` | killed | `d8-low-40-500k01-ins-present` +1 (360 cells) |
| `m-b-145` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-147` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-148` | guard-deletion | D6b: delete scoping conjunct `country == "LOW"` | killed | `d8-med-500k01-absent` +2 (216 cells) |
| `m-b-149` | guard-deletion | D6b: delete scoping conjunct `risk < 40` | killed | `d8-low-40-500k01-ins-absent` (360 cells) |
| `m-b-150` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-151` | guard-deletion | D6b: delete scoping conjunct `spend <= 2000000` | killed | `d8-2m01-low-absent` (48 cells) |
| `m-b-152` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-153` | guard-deletion | D6b: delete scoping conjunct `country == "LOW"` | killed | `d8-med-500k01-absent` +2 (432 cells) |
| `m-b-154` | guard-deletion | D6b: delete scoping conjunct `risk < 40` | killed | `d8-low-40-500k01-ins-absent` +3 (1080 cells) |
| `m-b-155` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-157` | guard-deletion | D6c: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-159` | guard-deletion | D6c: delete scoping conjunct `risk >= 40` | **dropped** | ladder-order-masked |
| `m-b-162` | guard-deletion | D7: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-166` | guard-deletion | D8: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-167` | guard-deletion | O3: delete scoping conjunct `v_sanctions == "CLEAR"` | killed | `d1-match-o3-region` (3888 cells) |
| `m-b-171` | guard-deletion | U1: delete scoping conjunct `count(u1_determinations) != 1` | **dropped** | entailed-guard |
| `m-b-174` | rung-deletion | delete `determine` ladder rung 3 (D2) | **dropped** | equivalent-fallthrough |
| `m-b-185` | rung-deletion | delete `determine` ladder rung 14 (D2) | **dropped** | unreachable-rung |


## Drop mechanisms

Every mutant below was found **nowhere** distinguishable from its reference on the scored surface over all 419,904 cells (X1 cells included; none is X1-only). The mechanism states why the edit cannot change the scored surface, in terms of the pack or the policy — never in terms of what gold happens to contain. Per-mutant text is in each MANIFEST's `adequacy.dropMechanism`.

### `same-outcome-overlap` — 6 mutants (arm A)

Members: `m-a-006`, `m-a-017`, `m-a-046`, `m-a-056`, `m-a-067`, `m-a-069`

r-d6b-insured's lower spend edge is relaxed onto $500,000.00. The only cells it newly admits (CLEAR, LOW, risk<40, spend exactly $500,000.00) are already r-d6a's, and both rules name `approve`, so the candidate set is unchanged (§8 step 9: multiple true rules naming one outcome are compatible). The one exception that suppresses r-d6a (D5) suppresses r-d6b-insured too, so no cell suppresses one without the other.  *(canonical statement, `m-a-006`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `shadowed-cascade-branch` — 5 mutants (arm A)

Members: `m-a-024`, `m-a-027`, `m-a-082`, `m-a-088`, `m-a-092`

The edit relaxes the D6b-insured COPY inside r-d8's `not(any ...)` onto spend exactly $500,000.00. At every such cell the D6a copy in the same `any` is already true, so the disjunction is true either way (§7.2), the negation is false either way, and r-d8's condition value is unchanged on all 419,904 cells (live-edit cells: 0).  *(canonical statement, `m-a-024`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `never-unknown-rule` — 1 mutant (arm A)

Members: `m-a-103`

Kleene-monotone onUnknown flip. r-d1's condition reads only /vendor/sanctionsStatus, which the registered projection always supplies as a present string (UNKNOWN is a value, not an omission), so the condition is never `unknown` and `onUnknown` is never consulted: 0 unknown cells of 419,904 (adequacy_mechanisms.json).  *(canonical statement, `m-a-103`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `reason-set-idempotence` — 5 mutants (arm A)

Members: `m-a-107`, `m-a-108`, `m-a-109`, `m-a-110`, `m-a-111`

onUnknown flip on r-d6a. Wherever r-d6a's condition is unknown AND the rule stage is reached at all (no evidence/exception block, no forced outcome, not suppressed), r-d8 is unknown and unsuppressed too, because its negation cascade carries a copy of the same conjuncts: 972 such cells, 0 uncovered. r-d8 already carries `onUnknown: escalate`, and §8 keeps reasons as a de-duplicated set, so the flip can only re-record `unknown`.  *(canonical statement, `m-a-107`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `ladder-order-masked` — 11 mutants (arm B)

Members: `m-b-007`, `m-b-010`, `m-b-013`, `m-b-033`, `m-b-039`, `m-b-045`, `m-b-049`, `m-b-145`, `m-b-150`, `m-b-155`, `m-b-159`

D6b's lower spend edge is relaxed onto $500,000.00, but the D6a rung above it consumes spend <= $500,000.00 with risk < 40 in LOW first, so the widened rung is never reached.  *(canonical statement, `m-b-007`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `duplicated-test` — 3 mutants (arm B)

Members: `m-b-060`, `m-b-083`, `m-b-085`

Inverting `v_spend != null` makes the entrypoint O3 rung unsatisfiable (a null spend never exceeds 2,000,000 under OPA's total value ordering), so control falls to U1, whose `determine` re-tests O3 over the spend candidate list and issues the same disposition.  *(canonical statement, `m-b-085`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `entailed-guard` — 16 mutants (arm B)

Members: `m-b-062`, `m-b-084`, `m-b-086`, `m-b-088`, `m-b-090`, `m-b-132`, `m-b-134`, `m-b-137`, `m-b-138`, `m-b-142`, `m-b-147`, `m-b-152`, `m-b-157`, `m-b-162`, `m-b-166`, `m-b-171`

`v_sanctions == "CLEAR"` deleted from a rung BELOW the D1 and D2 rungs of the same `else` chain: control reaches it only when sanctions is neither MATCH nor UNKNOWN, and the registered projection admits exactly {CLEAR, MATCH, UNKNOWN} as a present string, so the deleted conjunct is entailed there.  *(canonical statement, `m-b-132`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

This group has three sub-forms, each entailed by a different thing above it, and each is
written out per mutant in the MANIFEST:
* **the sanctions guard** (`m-b-132`, `134`, `137`, `138`, `142`, `147`, `152`, `157`, `162`,
  `166`) — entailed by the D1/D2 rungs above plus the registered three-state domain;
* **the financial-evidence guard** (`m-b-062`, `084`, `088`, `090`) — entailed by the two P1
  rungs above, which return for `absent` and for `OMITTED`. This is the asymmetry ledger's
  *inert O3 conjunct* row, now measured: the sentence that makes a correct JPS pack reachable
  in arm A leaves four unkillable mutants in arm B;
* **the U1 count guard** (`m-b-171`) — entailed by being the ladder's final `else`;
* and `m-b-086`, whose guard is entailed by OPA's total value ordering rather than by the
  ladder (see caveat C3).

### `unreachable-default` — 2 mutants (arm B)

Members: `m-b-124`, `m-b-125`

`default decision` swap. The decision ladder ends in an unconditional `else`, so the registered default is never consulted. The default is a registered arm-C convention (the only default preserving D2); in a build whose ladder is total, its mutants are unkillable by construction.  *(canonical statement, `m-b-124`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `equivalent-fallthrough` — 1 mutant (arm B)

Members: `m-b-174`

Deleting `determine`'s D2 rung leaves sanctions UNKNOWN to fall past every CLEAR-guarded rung to the ladder's backstop, which carries the same value, unresolved{no-match}.  *(canonical statement, `m-b-174`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*

### `unreachable-rung` — 1 mutant (arm B)

Members: `m-b-185`

Deleting `determine`'s backstop rung is inert: D1, D2 and D8 are jointly total over the registered three-state sanctions domain, so the backstop is unreachable.  *(canonical statement, `m-b-185`; the other members are the same mechanism at a sibling rung or by the threshold form of the same edit — per-mutant text is in the MANIFEST.)*


## Prose ambiguities hit while authoring — flagged, not resolved

These are **ambiguity-stratum candidates**. Each is recorded here and left open; none was
silently settled, and no gold row was written that depends on settling one.

**A1 — D6c's spend ceiling beside D6a's, at risk exactly 40.** Four of the added rows
(`d8-low-40-500k01-ins-{present,absent,unreported}`, `d8-nv-40-100k01`) sit in the hole the
two ceilings leave. In a LOW country, risk 39 with spend $2,000,000.00 is
approvable (D6b), while the same request at risk 40 can only be reviewed, because D6c's
ceiling is $100,000.00 — a twentyfold drop in permitted spend across one point of risk. The
*text* is unambiguous (both engines and the clean-room oracle reproduce every one of these
rows), and gold says review. What is ambiguous is whether the drafter meant it: a run author
reading for intent rather than for text may write "approve" or "enhanced review" here, and
would be wrong against the text and arguably right about the policy. **Class:
drafting-intent. Do not resolve in the design phase — this is exactly the material the
ambiguity stratum is for.**

**A2 — one sentence carries eight rows.** The four added rows with an *unreported* certificate
outside D6b's band (`d8-low-40-500k01-ins-unreported`, `d8-2m01-low-unreported`,
`d8-med-500k01-unreported`, `d6a-500k-ins-unreported`) and the four with an *absent* one
(`d8-low-40-500k01-ins-absent`, `d8-2m01-low-absent`, `d8-med-500k01-absent`,
`d6a-500k-ins-absent`) all turn on the Inputs-list sentence "It is never required (P1); it is
consulted only by D6b". Without it, D6b's third limb reads as a general rule about the
certificate and an unreported certificate would leave cases unresolved far outside D6b's
band, and an absent one would pull them into D6b's enhanced-review limb. The sentence is
v0.3's; it is now load-bearing in gold as well as in the references. **Flag: single-sentence
dependency. If the freeze edits that sentence, these eight rows move.**

**A3 — citation granularity for a vacuous O1.** `d8-nv-70-100k` (risk 70) and
`d8-nv-40-100k01` (spend $100,000.01) are new-vendor cells D6c never reached, so O1 suspends
nothing. The prose gives no way to say whether O1 "applies" vacuously there: the citation
could read O1+D8 or D8 alone, and the verdict is review either way. Gold cites D8 alone.
**Flag for V7**, whose completeness argument asserts exactly one governing clause per cell —
the earliest-clause tie-break is defined over determinations, not over vacuous suspensions.

**A4 — the v0.3 "outcome" sentence is now exercised by gold.** `u1-country-2m01` is the first
gold row whose U1 completions straddle a *determination* (review, D8) and an *escalation*
(O3): it is unresolved only because v0.3 says an escalation counts as an outcome for U1's
test. `u1-country-2m` is its neighbour on the other side of O3's exclusive edge and is
uniform. Not an open ambiguity — clean-room decisions D-3/D-6 dispositioned it — but the
sentence now has gold rows depending on it and should not be edited casually at freeze.

## Scope caveats — what "dropped" does and does not mean

**C1 — ten arm-B drops hold only because the sanctions domain is closed.** Every
`entailed-guard` drop of a `v_sanctions == "CLEAR"` conjunct (and `m-b-166`, `m-b-185`)
depends on the registered projection admitting exactly three present-string states. A fourth
value, or an omitted key, distinguishes those mutants immediately — which is precisely what
the `determine` ladder's backstop rung exists for. The drops are sound *relative to the
registered input domain*, which the admission layer enforces, and would not survive a domain
change.

**C2 — two arm-B drops are of a registered convention.** `default decision` is prescribed by
arm C's convention as the only default preserving D2, but the reference ladder is total, so
`default-swap` mutants (`m-b-124`, `m-b-125`) cannot be killed in this build by construction.
The class is not degenerate in general; it is degenerate against a total ladder. **Ledger
row: a prescribed convention that the shape the same prescription produces makes untestable**
— the mirror image of arm A's inert-O3-conjunct row, and two more genuinely unpairable
mutants for §4's unpairable count.

**C3 — one arm-B drop is a language artifact.** `m-b-086` (delete `v_spend != null` from the
entrypoint O3 rung) is inert only because OPA's total value ordering already makes
`null > 2000000` false. The guard is documentation, not behaviour; the policy text has no
view on it.

**C4 — arm A's five `reason-set-idempotence` drops are relative to the reference's shape.**
They are unkillable because r-d8 carries `onUnknown: escalate` and its negation cascade is
unknown wherever those rules are unknown — a consequence of the S1 cascade encoding the
reference build selected over S2. Under a different admissible encoding they might be
killable. Every witness set in this study is relative to its reference; these drops are no
different, and the fact is recorded rather than smoothed.

**C5 — arm A's negative claims are transcription-borne.** See Method: validated on 2,076
engine evaluations, every positive witness re-confirmed on the engine, every live-edit drop
sampled on the engine, the `onUnknown` mechanisms checked over the whole space, and all 17
drop verdicts reproduced by a second, independently written transcription. The positive
claims (kills) are engine-borne through `check_gold.py`'s floor gate. What no artifact here
provides is 419,904 × 17 process launches of the pinned binary; that is the residual.

## Consequences for the rest of the pre-freeze package

- **Pairing moved, and grew.** §4 pairs mutants by identical sorted witness sets. Recomputed
  from the updated MANIFESTs by `e4_score.py`'s own loader: **29 → 39 shared witness keys**,
  covering **76 → 81 JPS** and **65 → 73 Rego** mutants. The paired adequate subset E4 scores
  over is therefore larger and different; the pairing and kill numbers quoted in
  `E4-NOTES.md` / `E4-PILOT.json` predate this gate and must not be quoted as current.
- **The conflict-only list moved: 35 → 41** (`refA/REGISTRY.json`), and three mutants left it
  (`m-a-081`, `m-a-141`, `m-a-142` are now killed by a differing determination). §4's
  "reported both included and excluded" applies to the new list.
- **Not performed here:** §4's *off-gold equivalence check* between the two references. This
  gate compared each mutant to *its own* reference, never refA to refB. A sibling pre-freeze
  task produced `reference/OFFGOLD-CERT.md` while this one ran (verdict PASS: 72 divergences
  over 236,196 cells, all 72 inside X1); this document neither performs nor certifies that
  check, and the two runs used different spaces — 236,196 registered derived cells there,
  419,904 dense boundary cells here — so neither subsumes the other.
- `mutants/v0_row_ids.json` records the 76 pre-gate row ids so "added at this gate" stays
  computable after later additions.

## Reproduction

```
cd design/mutants
python3 adequacy_search.py --validate     # transcription vs pinned jpack (2,076 evals)
python3 adequacy_search.py --search       # both arms over 419,904 cells -> adequacy_search.json
python3 adequacy_search.py --confirm      # pinned binaries at every reported witness
python3 adequacy_search.py --drops        # engine adjudication of the arm-A no-witness verdicts
python3 adequacy_search.py --mechanisms   # the two onUnknown drop mechanisms, whole-space
python3 adequacy_search.py --killcensus   # which kills are only reachable as unresolved{conflict}
python3 adequacy_search.py --crosscheck   # drop verdicts re-run with reference/refA/jps_sim.py
cd ../gold && python3 gold_author.py && python3 check_gold.py
cd ../cleanroom && python3 check_oracle.py
cd ../mutants && python3 adequacy_search.py --witnesses --manifests --registry
```

Artifacts written by the gate: `adequacy_search.json` (per-mutant differing-cell counts and
up to 8 witnesses each), `adequacy_validation.json`, `adequacy_confirm.json`,
`adequacy_drops.json`, `adequacy_mechanisms.json`, `adequacy_killcensus.json`,
`adequacy_crosscheck.json`,
`adequacy_witnesses.json` (the recomputed witness sets), and the `adequacy` block now carried
by every mutant in both MANIFESTs.

---

## A1 disposition (maintainer, 2026-08-15)

**Confirmed: the risk-40 spend cliff is intended.** At risk exactly 40 in a LOW-risk
country the approval ceiling drops from $500,000 (D6a; insured to $2,000,000 under D6b)
to $100,000 (D6c) by design — realistic policies carry such cliffs, and the boundary
sensitivity it creates is exactly what the mutant classes probe. The prose stands as
written; the four dependent gold rows stand; A1 is closed and carried into the review
record as confirmed intent, not an open question.

---

# Round-3 gate closure — the 37 JPS + 34 Rego empty-witness mutants of the repaired corpus

**This section is the CURRENT gate. Everything above it is the verbatim record of the
2026-08-15 run against the pre-repair corpus, and its ids are not this corpus's ids.**

Review round 3, finding **R3-2**: the round-2 disposition "adequacy: accepted, both halves"
over-claimed. The arm-A reference repair (`reference/refA/PACK-CHANGE-001.md`, round-1
finding R1-2) regenerated the JPS mutant corpus and re-witnessed the Rego one, and **71
mutants — 37 JPS and 34 Rego — were left with an empty witness set and no disposition**.
The regeneration record said so in its own field (`REGENERATION-CHECK.json`, `pass: false`)
and nothing downstream read it. This section disposes of all 71 by the round-1 discipline,
unchanged: dense mechanical search for a witnessing input; a gold row authored **from the
prose with a clause citation** wherever a witness exists; a registered drop with its
mechanism where none exists anywhere.

## Result

| | JPS (arm A) | Rego (arm B) |
|---|---|---|
| valid mutants | 183 | 184 |
| killed by gold **before** this gate | 146 | 150 |
| work list (empty witness) | 37 | 34 |
| → killed by a row added here | **11** | **0** |
| → registered as dropped, with mechanism | **26** | **34** |
| killed by gold **after** this gate | **157** | **150** |
| empty witness sets remaining | 0 | 0 |
| undispositioned | **0** | **0** |

**The gate is satisfied again: no mutant in either arm is left undisposed.** Gold grew from
**109 to 117 rows** (8 added). Every added row was authored from POLICY-DRAFT.md v0.3 with a
clause citation; the search says only *where* to look, never what the policy requires there,
and every row's note names the sentence it was derived from.

Each of the eight rows is load-bearing and none is redundant: every one is the *first*
witness for at least one of the eleven newly killed mutants, and the eleven are covered
between them with no mutant left to a coincidence — `d8-med-nv-40-100k` kills `m-a-021` and
`m-a-085`, `d4-high-nv-70-100k` kills `m-a-022` and `m-a-087`, `x1r-country-unreadable-40`
kills `m-a-042` and `m-a-127`, and the remaining five rows each kill one (`m-a-088`,
`m-a-124`, `m-a-128`, `m-a-130`, `m-a-131` in the table's order).

## What the work list turned out to be, and the warning it carries

**Twenty-three of the 37 JPS mutants sit in machinery the repair introduced or made
redundant — and all eleven that gold can kill are among them.** The repair added two derived
"region lemma" rules (`r-o1-wide-low`, `r-o1-wide-spend`) and two D8 suppressions scoped to
them; 14 of the 37 edit one of those four and 9 edit `r-o1-review`, the O1 companion rule the
repair *subsumed*. The other 14 are D6b/D6c, cascade and `onUnknown` edits whose round-1
counterparts were already drops for the same mechanisms. Gold v0.1
probed that region only in a **LOW** country, because before the repair the arm-A reference
could not answer it anywhere else. The eight rows added here are its edges in a MEDIUM,
HIGH and unreadable country.

**The ids do not carry across the repair, and two of them prove it.** `m-a-056` was
`r-d6c`'s lower risk edge on 2026-08-15 and is `r-d6b-insured`'s lower spend edge now;
`m-a-088` was a shadowed cascade branch and is now `r-o1-wide-spend`'s upper risk edge —
**a mutant a gold row kills**. Re-keying the 2026-08-15 table onto this corpus would have
registered a drop for a killable mutant and called the gate closed. It is not a
re-derivation hazard in the abstract: 12 of the old table's 17 arm-A entries name mutants
that are not empty-witness in this corpus at all, and of the 5 whose ids survive, 3 name a
different edit. **The registry is now checked in both directions before anything is
stamped** (`adequacy_search.py --check-drop-registry`, and the same check refuses at the
head of `--manifests`): unregistered empty-witness mutants and stale registry entries are
both blocking, and the stamp step is inside the regeneration chain so the check runs on the
tree it is stamping.

**Measured, and recorded rather than repaired: `r-o1-review` is behaviourally redundant in
the repaired reference.** Its region is a strict subset of `r-o1-wide-low`'s, both name
`review`, and the D5 family suppresses them together — so **deleting the whole rule changes
nothing anywhere** (`m-a-183`: 0 live-edit cells of 419,904, and the corpus's own
cascade-deletion probe for it is a drop). Twelve mutants in the corpus touch this rule and
**nine of them are unkillable**: every edit that moves its *boundaries* is invisible, because
`r-o1-wide-low` answers the same cells with the same outcome. The three that gold does kill
change what the rule *says* rather than what it contributes — its outcome (`m-a-169`, review
→ approve, which conflicts with `r-o1-wide-low`'s review), its `onUnknown` (`m-a-142`), and
the one widening that reaches down into D6a's approval region (`m-a-076`, risk 40 → 39).
That distinction is the honest one: a redundant rule contributes nothing while it is correct
and can still do damage when it is wrong.

This is a property of the repair, not of gold — no gold suite can see through a rule another
rule subsumes. It belongs in the asymmetry ledger (V8) beside the region-lemma cost row, and
the reference is **not** being changed for it: changing the reference again would re-open
this gate, the off-gold certificate and the corpus. Recorded here so the freeze reader knows
the nine drops are the repair's price and not a thin spot in gold.

## Method

Identical to the 2026-08-15 method above — same 419,904-cell dense derived space, same
engine-borne arm-B search, same transcription-plus-validation for arm A — with one change
of registry and one of chain:

* **The registered exclusion registry is EMPTY.** X1 was retired with the repair, so
  `excluded()` is false everywhere: every cell of the dense space is candidate ground, and
  the `diffCellsInX1` counters read 0 against `diffCells` throughout. No mutant in either
  arm is "distinguishable only inside an excluded region", because there is no such region.
* **The adequacy stamp is inside the regeneration chain** (round-3 change to
  `regenerate.py`). It used to be a separate hand-run command, which is why the stamp was
  never byte-compared and the pre-repair drop table could survive a corpus regeneration
  unnoticed. `regenerate.py --arm both --check` now regenerates the corpora, the witness
  sets, both stamped MANIFESTs, arm A's REGISTRY and the pairing report into a scratch copy
  and byte-compares all of it.

| check | this round |
|---|---|
| `--validate`: transcription vs pinned jpack (117 gold rows + 120 sampled cells on the reference; 40 sampled cells on each of the 37 work-list mutants) | **1,717 checked evaluations, 0 disagreements** |
| `--search`: dense sweep over the work list | armA **11/37** distinguishable, armB **0/34** |
| `--confirm`: every reported witness re-run on the pinned binary, mutant side and reference side | **88 witnesses, 0 unconfirmed** |
| `--drops`: for the 26 arm-A no-witness mutants, the cells where the edit is LIVE enumerated and a deterministic sample handed to the pinned engine | **1,800 live-edit cells adjudicated, 0 differences**; 11 of the 26 have **zero** live-edit cells |
| `--mechanisms`: the two mechanisms the six `onUnknown` drops rest on, re-measured **on the repaired pack** | r-d1 **0 unknown cells**; r-d6a 972, r-d6b-insured 432, r-d6b-uninsured 432, r-d6c 456, r-d7 540 unknown-and-evaluated cells, **0 uncovered by r-d8** |
| `--crosscheck`: all 26 arm-A drop verdicts re-run over the whole space with the **second, independently written** §7/§8 transcription (`reference/refA/jps_sim.py`) | **0 disagreements** |

The `--mechanisms` re-run is not a formality this round. The repair gave `r-d8` two
region-scoped suppressions, and the reason-set-idempotence argument needs `r-d8` to be
unknown **and unsuppressed** wherever the flipped rule is unknown. The check tests exactly
that conjunction, on the repaired pack, and the five flips still hold with 0 uncovered
cells.

## The agreement chain, re-run after the additions

| check | result |
|---|---|
| `gold/check_gold.py` — structure, empty exclusion registry, clause coverage, boundary witnesses | 117 rows, **0 failures** |
| …its floor gate: pinned jpack 0.17.0 over `reference/refA/pack.json` | reproduces **117/117** |
| …its floor gate: pinned OPA 1.19.0 over `reference/refB/policy.rego` | reproduces **117/117** |
| …the retired-X1 census (non-gating, must be non-empty) | **5 rows** now inside the region the retired class forbade (was 3 + 1 adjacency control) |
| `cleanroom/check_oracle.py` — clean-room second oracle vs gold | **117/117 agree** |
| `cleanroom/check_oracle.py` — oracle vs refA over the 2,540-cell design grid | 2,540/2,540, **0 unexpected divergences** |

**No oracle disagreement arose, so nothing had to be retained verbatim.** All eight
additions were reproduced by both pinned engines and by the clean-room oracle on the first
run, with zero adjudicated corrections — the same standing as every row before them. Had one
diverged it would have been kept as authored and reported, not edited.

## Rows added (gold v0.1 -> v0.2)

All eight live in a clearly marked `==== gold v0.2 — ROUND-3 ADEQUACY-GATE ADDITIONS ====`
section of `gold/gold_author.py`, each with the sentence it was derived from in its note.
The base cell is the file's `BASE` (CLEAR, LOW, risk 20, spend 50,000.00, all statuses "no",
both evidence documents present); "—" means the key is omitted (unreadable / unreported).
"kills A/B" is the number of arm-A / arm-B mutants for which this row is a witness, over the
whole corpus and not only over this work list.

| row | inputs (delta from the base cell) | expectation | cites | kills A/B |
|---|---|---|---|---|
| `d8-med-nv-40-100k` | country=MEDIUM, newVendor=yes, risk=40, spend=100000.00 | **review** | D8 | 7/18 |
| `d8-med-nv-69-100k` | country=MEDIUM, newVendor=yes, risk=69, spend=100000.00 | **review** | D8 | 4/16 |
| `d8-med-nv-40-100k01` | country=MEDIUM, newVendor=yes, risk=40, spend=100000.01 | **review** | D8 | 2/15 |
| `d4-high-nv-70-100k` | country=HIGH, newVendor=yes, risk=70, spend=100000.00 | **reject** | D4 | 8/19 |
| `d8-high-nv-39-100k` | country=HIGH, newVendor=yes, risk=39, spend=100000.00 | **review** | D8 | 2/22 |
| `d6b-nv-39-500k01-unreported` | insurance=—, newVendor=yes, risk=39, spend=500000.01 | **unresolved{unknown}** | D6b | 3/19 |
| `x1r-country-unreadable-40` | country=—, newVendor=yes, risk=40, spend=100000.00 | **review** | O1, D8, U1 | 12/26 |
| `x1r-country-unreadable-69` | country=—, newVendor=yes, risk=69, spend=100000.00 | **review** | O1, D8, U1 | 10/23 |

## Disposition table — all 71

Arm-A edits are abbreviated: `r-x.cond[i]` is condition *i* of rule `r-x`'s `all`,
`r-d8.cascade[j]` is disjunct *j* inside r-d8's `not(any …)`. "(N cells)" is the number of
cells of the 419,904-cell dense space at which the mutant differs from its reference.
⚠conflict-only marks a mutant whose every differing cell over the domain yields
`unresolved{conflict}` — an engine-supplied kill, which arm B has no counterpart for. Two of
the eleven new kills are conflict-only, so this round's assertion-only kill count is **9**.

### Arm A (JPS) — the 37 empty-witness mutants of the repaired corpus

| mutant | class | edit | disposition | killing row (differing cells) / drop mechanism |
|---|---|---|---|---|
| `m-a-006` | operator-flip | r-d6b-insured.cond[3].op: greater-than -> greater-than-or-equal | **dropped** | same-outcome-overlap |
| `m-a-016` | operator-flip | r-o1-review.cond[0][2].op: greater-than-or-equal -> greater-than | **dropped** | subsumed-region-lemma |
| `m-a-017` | operator-flip | r-o1-review.cond[0][3].op: less-than -> less-than-or-equal | **dropped** | subsumed-region-lemma |
| `m-a-018` | operator-flip | r-o1-review.cond[0][4].op: less-than-or-equal -> less-than | **dropped** | subsumed-region-lemma |
| `m-a-020` | operator-flip | r-o1-wide-low.cond[3].op: less-than -> less-than-or-equal | **dropped** | same-outcome-overlap |
| `m-a-021` | operator-flip | r-o1-wide-spend.cond[1].op: greater-than-or-equal -> greater-than | killed | `d8-med-nv-40-100k` +1 (108 cells) |
| `m-a-022` | operator-flip | r-o1-wide-spend.cond[2].op: less-than -> less-than-or-equal | killed | `d4-high-nv-70-100k` (36 cells) ⚠conflict-only |
| `m-a-029` | operator-flip | r-d8.cascade[3].conditions[3].op: greater-than -> greater-than-or-equal | **dropped** | shadowed-cascade-branch |
| `m-a-032` | operator-flip | r-d8.cascade[4].conditions[3].op: greater-than -> greater-than-or-equal | **dropped** | shadowed-cascade-branch |
| `m-a-042` | operator-flip | x-o1-suppress-d8-spend.cond[1].op: greater-than-or-equal -> greater-than | killed | `x1r-country-unreadable-40` (36 cells) |
| `m-a-056` | boundary-shift | r-d6b-insured.cond[3]: 500000.00 -> 499999.99 (-1 at scale) | **dropped** | same-outcome-overlap |
| `m-a-066` | boundary-shift | r-d6c.cond[2]: 40 -> 39 (-1 at scale) | **dropped** | same-outcome-overlap |
| `m-a-075` | boundary-shift | r-o1-review.cond[0][2]: 40 -> 41 (+1 at scale) | **dropped** | subsumed-region-lemma |
| `m-a-077` | boundary-shift | r-o1-review.cond[0][3]: 70 -> 71 (+1 at scale) | **dropped** | subsumed-region-lemma |
| `m-a-078` | boundary-shift | r-o1-review.cond[0][3]: 70 -> 69 (-1 at scale) | **dropped** | subsumed-region-lemma |
| `m-a-079` | boundary-shift | r-o1-review.cond[0][4]: 100000.00 -> 100000.01 (+1 at scale) | **dropped** | subsumed-region-lemma |
| `m-a-080` | boundary-shift | r-o1-review.cond[0][4]: 100000.00 -> 99999.99 (-1 at scale) | **dropped** | subsumed-region-lemma |
| `m-a-083` | boundary-shift | r-o1-wide-low.cond[3]: 70 -> 71 (+1 at scale) | **dropped** | same-outcome-overlap |
| `m-a-085` | boundary-shift | r-o1-wide-spend.cond[1]: 40 -> 41 (+1 at scale) | killed | `d8-med-nv-40-100k` +1 (108 cells) |
| `m-a-087` | boundary-shift | r-o1-wide-spend.cond[2]: 70 -> 71 (+1 at scale) | killed | `d4-high-nv-70-100k` (36 cells) ⚠conflict-only |
| `m-a-088` | boundary-shift | r-o1-wide-spend.cond[2]: 70 -> 69 (-1 at scale) | killed | `d8-med-nv-69-100k` +1 (108 cells) |
| `m-a-089` | boundary-shift | r-o1-wide-spend.cond[3]: 100000.00 -> 100000.01 (+1 at scale) | **dropped** | same-outcome-overlap |
| `m-a-102` | boundary-shift | r-d8.cascade[3].conditions[3]: 500000.00 -> 499999.99 (-1 at scale) | **dropped** | shadowed-cascade-branch |
| `m-a-108` | boundary-shift | r-d8.cascade[4].conditions[3]: 500000.00 -> 499999.99 (-1 at scale) | **dropped** | shadowed-cascade-branch |
| `m-a-112` | boundary-shift | r-d8.cascade[5].conditions[2]: 40 -> 39 (-1 at scale) | **dropped** | shadowed-cascade-branch |
| `m-a-124` | boundary-shift | x-o1-suppress-d8-low.cond[2]: 40 -> 39 (-1 at scale) | killed | `d6b-nv-39-500k01-unreported` (48 cells) |
| `m-a-127` | boundary-shift | x-o1-suppress-d8-spend.cond[1]: 40 -> 41 (+1 at scale) | killed | `x1r-country-unreadable-40` (36 cells) |
| `m-a-128` | boundary-shift | x-o1-suppress-d8-spend.cond[1]: 40 -> 39 (-1 at scale) | killed | `d8-high-nv-39-100k` (72 cells) |
| `m-a-130` | boundary-shift | x-o1-suppress-d8-spend.cond[2]: 70 -> 69 (-1 at scale) | killed | `x1r-country-unreadable-69` (36 cells) |
| `m-a-131` | boundary-shift | x-o1-suppress-d8-spend.cond[3]: 100000.00 -> 100000.01 (+1 at scale) | killed | `d8-med-nv-40-100k01` (108 cells) |
| `m-a-133` | onUnknown-flip | r-d1.onUnknown: ignore -> escalate | **dropped** | never-unknown-rule |
| `m-a-137` | onUnknown-flip | r-d6a.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-138` | onUnknown-flip | r-d6b-insured.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-139` | onUnknown-flip | r-d6b-uninsured.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-140` | onUnknown-flip | r-d6c.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-141` | onUnknown-flip | r-d7.onUnknown: ignore -> escalate | **dropped** | reason-set-idempotence |
| `m-a-183` | cascade-deletion | r-o1-review deleted (the O1 companion review rule; dangling targetRule references dropped with it: x-d5-suppress-o1-review) | **dropped** | subsumed-region-lemma |

### Arm B (Rego) — the 34 empty-witness mutants

| mutant | class | edit | disposition | drop mechanism |
|---|---|---|---|---|
| `m-b-007` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-010` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-013` | operator-flip | D6b: `spend > 500000` -> `spend >= 500000` | **dropped** | ladder-order-masked |
| `m-b-033` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-039` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-045` | boundary-shift | D6b: spend threshold 500000 -0.01 -> 499999.99 | **dropped** | ladder-order-masked |
| `m-b-049` | boundary-shift | D6c: risk threshold 40 -1 -> 39 | **dropped** | ladder-order-masked |
| `m-b-060` | boundary-shift | O3: spend threshold 2000000 +0.01 -> 2000000.01 | **dropped** | duplicated-test |
| `m-b-062` | unknown-guard-flip | O3/P1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-083` | unknown-guard-flip | O3 (evidence-availability tri-state): invert `fin_state == "present"` | **dropped** | duplicated-test |
| `m-b-084` | unknown-guard-flip | O3 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-085` | unknown-guard-flip | O3 (unreadable-input sentinel (omitted key)): invert `v_spend != null` | **dropped** | duplicated-test |
| `m-b-086` | unknown-guard-flip | O3 (unreadable-input sentinel (omitted key)): delete `v_spend != null` | **dropped** | entailed-guard |
| `m-b-088` | unknown-guard-flip | U1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-090` | unknown-guard-flip | U1 (evidence-availability tri-state): delete `fin_state == "present"` | **dropped** | entailed-guard |
| `m-b-124` | default-swap | registered default: reasons no-match -> unknown | **dropped** | unreachable-default |
| `m-b-125` | default-swap | registered default: disposition unresolved -> review (reasons left as authored) | **dropped** | unreachable-default |
| `m-b-132` | guard-deletion | D3: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-134` | guard-deletion | D4: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-137` | guard-deletion | D5: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-138` | guard-deletion | D6a: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-142` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-145` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-147` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-150` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-152` | guard-deletion | D6b: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-155` | guard-deletion | D6b: delete scoping conjunct `spend > 500000` | **dropped** | ladder-order-masked |
| `m-b-157` | guard-deletion | D6c: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-159` | guard-deletion | D6c: delete scoping conjunct `risk >= 40` | **dropped** | ladder-order-masked |
| `m-b-162` | guard-deletion | D7: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-166` | guard-deletion | D8: delete scoping conjunct `v_sanctions == "CLEAR"` | **dropped** | entailed-guard |
| `m-b-171` | guard-deletion | U1: delete scoping conjunct `count(u1_determinations) != 1` | **dropped** | entailed-guard |
| `m-b-174` | rung-deletion | delete `determine` ladder rung 3 (D2) | **dropped** | equivalent-fallthrough |
| `m-b-185` | rung-deletion | delete `determine` ladder rung 14 (D2) | **dropped** | unreachable-rung |


## Drop mechanisms — arm A, re-derived (26)

Every mutant below was found **nowhere** distinguishable from the repaired reference on the
scored surface over all 419,904 cells, by the transcription, by a second independent
transcription, and — wherever the edit is live at all — by the pinned engine itself. The
mechanism states why the edit cannot change the scored surface in terms of the pack and the
policy, never in terms of what gold happens to contain. Per-mutant text is in
`refA/MANIFEST.json`'s `adequacy.dropMechanism`.

### `subsumed-region-lemma` — 9 mutants (arm A) — NEW CLASS

Members: `m-a-016`, `m-a-017`, `m-a-018`, `m-a-075`, `m-a-077`, `m-a-078`, `m-a-079`,
`m-a-080`, `m-a-183`

`r-o1-review`'s region (CLEAR, LOW, 40 ≤ risk < 70, spend ≤ $100,000.00, newVendor=yes) is a
**strict subset** of `r-o1-wide-low`'s (the same without the spend conjunct), which the X1
repair added; both name `review`, both carry `onUnknown: ignore`, and the D5 family
suppresses them together. So a single edit inside `r-o1-review` can only move cells another
rule already answers `review`: narrowings drop cells `r-o1-wide-low` still admits, and the
two widenings past the band (risk exactly 70) land where `r-d8` already fires — its D6c
cascade disjunct needs risk < 70 and is false, `x-o1-suppress-d8-low` needs risk < 70 and
does not suppress it, and no approval or rejection rule reaches a LOW country at risk 70
below 90. `m-a-183` deletes the rule outright, with 0 live-edit cells.

**This class exists only because of the repair**, and it is the sharpest measurement of the
repair's redundancy the corpus can make.

### `same-outcome-overlap` — 6 mutants (arm A)

Members: `m-a-006`, `m-a-020`, `m-a-056`, `m-a-066`, `m-a-083`, `m-a-089`

A rule is relaxed onto cells another rule already claims with the **same** outcome, so the
candidate set is unchanged (§8 step 9: multiple true rules naming one outcome are
compatible). Three forms here: D6b-insured's lower spend edge onto $500,000.00, which is
D6a's `approve` (`m-a-006`, `m-a-056`); D6c's lower risk edge onto 39, which is also D6a's
`approve` (`m-a-066`); and the two region-lemma rules relaxed onto a cell `r-d8` already
reviews (`m-a-020`, `m-a-083` at risk 70; `m-a-089` a cent above D6c's ceiling, where the
**unedited** companion suppression still reads $100,000.00 and so leaves `r-d8` live).

### `shadowed-cascade-branch` — 5 mutants (arm A)

Members: `m-a-029`, `m-a-032`, `m-a-102`, `m-a-108`, `m-a-112`

The edit relaxes a COPY of an approval rule inside `r-d8`'s `not(any …)` onto cells where
another copy in the same `any` is already true, so the disjunction is true either way
(§7.2), the negation is false either way, and `r-d8`'s condition value is unchanged on all
419,904 cells. Live-edit cells: 0 for all five.

### `never-unknown-rule` — 1 mutant (arm A)

Members: `m-a-133`

`r-d1`'s condition reads only `/vendor/sanctionsStatus`, which the registered projection
always supplies as a present string (UNKNOWN is a value, not an omission), so the condition
is never `unknown` and `onUnknown` is never consulted: **0 unknown cells of 419,904**.

### `reason-set-idempotence` — 5 mutants (arm A)

Members: `m-a-137`, `m-a-138`, `m-a-139`, `m-a-140`, `m-a-141`

Wherever the flipped rule's condition is unknown AND the rule stage is reached at all,
`r-d8` is unknown and unsuppressed too, because its negation cascade carries a copy of the
same conjuncts; `r-d8` already carries `onUnknown: escalate` and §8 keeps reasons as a
de-duplicated set, so the flip can only re-record `unknown`. Re-measured on the repaired
pack: 972 / 432 / 432 / 456 / 540 unknown-and-evaluated cells, **0 uncovered**.

## Drop mechanisms — arm B, unchanged (34)

The Rego reference was **not** touched by the repair (`refB/policy.rego` is byte-identical
since 2026-08-15) and neither were the 185 mutant payloads, so arm B's drops are the same
edits, with the same mechanisms, re-verified rather than re-derived: this round's sweep
re-ran all 34 against the reference in the pinned OPA itself and found **0 differing cells
anywhere for every one of them**. The classes and members are exactly the arm-B rows of the
2026-08-15 mechanism sections above: `ladder-order-masked` (11), `entailed-guard` (16),
`duplicated-test` (3), `unreachable-default` (2), `equivalent-fallthrough` (1),
`unreachable-rung` (1). Their scope caveats **C1–C3 stand unchanged**.

What did change for arm B is only its *witness sets*: the eight new gold rows are witnesses
for many already-killed Rego mutants, which moves the pairing keys (below). No Rego mutant
moved between killed and dropped in either direction.

## The regeneration record — green, and green for the first time

`regenerate.py --arm both --check`, 2026-08-19, with the pinned executables:

| field | value |
|---|---|
| `filesCompared` / `identical` | **375 / 375** |
| `byteIdentical` | **true** |
| `armsCovered` | A true, B true |
| `adequacyStampPresent` | **A true, B true** |
| `undispositionedEmptyWitnessMutants` | **A [], B []** |
| `pass` | **true** |

Three of those 375 files are new to the comparison — `adequacy_witnesses.json`,
`adequacy_drop_registry.json`, `adequacy_pairing.json` — and both MANIFESTs are compared
**stamped** for the first time. Every previous record in this command's history reads
`pass: false`, structurally: the stamp step sat outside the chain, so a regenerated manifest
never carried it and `adequacyStampPresent` could never be true. That is the same gap that
let a pre-repair drop table survive a corpus regeneration unread. Both are closed by moving
the tail inside the chain.

## Pairing and the per-language cuts

Recomputed from the stamped manifests by `adequacy_search.py --pairing`
(`adequacy_pairing.json`), which imports `e4_score.build_pairing` so that the registered
pairing rule has exactly one implementation. This is a **design-time** recomputation: no
pilot was run for it, and none is needed — pairing and the cuts are functions of the
manifests alone.

| | JPS (arm A) | Rego (arm B) |
|---|---|---|
| valid mutants | 183 | 184 |
| adequate (non-empty witness set) | **157** (was 146) | **150** (unchanged) |
| paired adequate — the E4 denominator | **69** (was 75) | **62** (was 65) |
| unpairable adequate | **88** (was 71) | **88** (was 85) |
| integer cut ⌈τ·N⌉ at τ = 0.95 | **66** (was 72) | **59** (was 62) |
| cut as a fraction of its own denominator | 0.956522 | 0.951613 |
| cut ≤ denominator (asserted) | yes | yes |

Witness groups: **157 in total** (was 145), of which **34 are shared** across the two
languages (was 36) and **33 are shared and non-degenerate** (was 35). The one degenerate
group is the empty-witness key — 26 JPS and 34 Rego mutants that pair only on the absence of
a discriminating row — and it is excluded from every paired subset, as registered.

**Both paired denominators went DOWN when gold grew, and that is not a defect.** Pairing is
equality of witness *sets*: a new row that kills a JPS mutant and a Rego mutant that were
already killed by different rows can split a group that used to coincide. Gold got more
discriminating, so fewer sets are identical across languages — 69/62 paired adequate against
75/65 before, and the cuts fall with them. The quantity to watch is not the denominator's
size but the assertion beside it (each cut is reachable within its own language's
denominator), which holds at 66 ≤ 69 and 59 ≤ 62.

**Everything downstream of these four numbers was stale when this section was written, and
has since been re-read from it.** The pilot issues up to `E4-PILOT-v3.json` computed their
high-kill fractions at the old cuts 72/62; `E4-PILOT-v4.json` is scored against this
corpus, at **66 (JPS) and 59 (Rego)**, and `OC-TABLE.md` §7 and
PREREGISTRATION §4 and §5 quote it and these counts. This section is the source they are
read from; `adequacy_pairing.json` is the machine-readable form and it is regenerated and
byte-compared by `regenerate.py --arm both --check`, and
`harness/tests/test_prereg_currency.py` recomputes every one of those quoted numbers from
the committed manifests at test time.

## Prose ambiguities hit while authoring — flagged, not resolved

**A5 — O1 suspends D6c, and only D6c.** The sentence is "For new vendors (yes), clause D6c
does not apply; such requests fall to D8", and D6c is named on its own, so the reading is
the literal one. The flag is that a reader who takes "D6 — Approval, LOW-risk country" as
the clause and a/b/c as its limbs could read O1 as suspending the whole family.

Exactly **one** of the eight added rows turns on the difference:
`d6b-nv-39-500k01-unreported` gives a NEW vendor D6b's unresolved-as-unknown limb, and under
the wider reading it would be **review** instead. It is the sole witness for one kill
(`m-a-124`), so one of the eleven kills rests on this reading. The other seven rows are
unaffected either way, because they sit in a MEDIUM, HIGH or unreadable country and D6 is
LOW-only. Both pinned engines and the
clean-room oracle reproduce the literal reading. **Flag for V7 and for the freeze reader**,
not an amendment: the prose is not being edited this round.

**A6 — the region lemma is not in the prose, and gold now pins its edges.** The two rules
the repair added are sound consequences of the prose that an author must *derive*; the prose
states no such region. The seven rows at the region's MEDIUM/HIGH/unreadable edges therefore
test something the prose entails but never says, which is exactly the asymmetry-ledger cost
row PACK-CHANGE-001 §4.2 already records. Recorded here because it is now *witnessed* by
gold rather than argued.

## Scope caveats added this round

**C6 — nine arm-A drops are a property of the reference's shape, not of the fragment.** The
`subsumed-region-lemma` class would disappear if `r-o1-review` were deleted from the
reference (it is behaviourally inert). It is deliberately **not** deleted: the reference is
frozen for this study's purposes and a second repair would re-open the corpus, the
certificate, the pairing and this gate. The consequence for the E4 endpoint is stated
plainly: arm A carries nine mutants no suite in any arm can kill, and they are in the
denominator only if they pair, which they do not (an empty witness set never pairs).

## Reproduction

```
cd design/gold      && python3 gold_author.py && python3 check_gold.py
cd design/cleanroom && python3 check_oracle.py
cd design/mutants   && python3 adequacy_search.py --validate --search --confirm \
                                                  --drops --mechanisms --crosscheck
cd design/mutants   && python3 regenerate.py --arm both          # corpora + adequacy tail
cd design/mutants   && python3 regenerate.py --arm both --check   # byte-compare, writes the record
```

with `JPACK_BIN`, `OPA_BIN` and `OPA_CAPS` pointed at the pinned executables.

**The search commands read the CURRENT manifest's empty-witness set**, which is what makes
them a work-list sweep. Run now, after the gate is closed, they sweep the **26** remaining
drops rather than the 37-mutant work list, and `--search` would overwrite
`adequacy_search.json` with the smaller set. The committed `adequacy_search.json`,
`adequacy_confirm.json` and `adequacy_validation.json` are the snapshot taken **while the
gate was open**, which is the only moment at which the work list exists; that is why the
`--validate` line reports 1,717 evaluations (37 mutants × 40 cells plus the reference) and a
re-run today would report 1,277 (26 × 40 plus the reference). Neither number is wrong; they
are measurements of different sets, and this file states which.

The last command is the one that has to be green: it reproduces every payload, both stamped
MANIFESTs, arm A's REGISTRY, the witness sets and the pairing report byte-for-byte, and its
`pass` is true only if the drop registry also covers the corpus's empty-witness census
exactly.
