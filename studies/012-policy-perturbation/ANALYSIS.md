# Study 012 — is the blinded author's test surface anchored to the policy's surface form?

> **Corrected on 2026-08-11.** This file was published, then checked claim by
> claim against `RESULTS.json`. `R1-UNSUPPORTED`, the decision row and the arm
> table survived unchanged; several supporting sentences did not. The corrected
> passages are marked below, and the full list is at the head of
> [`CORRECTION.md`](CORRECTION.md). The largest error: "in every arm, including
> the baseline, the count of records below that edge is zero" was false — arm C
> has one, and the 464/432 denominators misdescribed a windowed count.

**R1 is UNSUPPORTED. The prediction this study was built to test failed, and it
failed cleanly.** We published, before this study existed, that removing a
policy's stated numerals would collapse the blinded author's coverage of the
numeric classes, because placement follows named numbers. Arm E — the same rules
with the threshold **literals** removed, both values instead defined in words as
fractions of a stated zero-to-one-hundred scale — covered all six semantic
classes in all 27 of its valid runs, reading HIGH on every one, indistinguishable
from the baseline.
§5.3 (i) row 4 fired. **And this study does not thereby establish the opposite:**
maintained coverage is equally compatible with the author deriving the
boundaries from prose and with it recognising this policy family from a corpus
public since 2026-08-06, and this design cannot separate them — §9 said so
before the data existed. The full retraction is at the head of
[`CORRECTION.md`](CORRECTION.md).

## What ran

150 authoring calls, 30 per arm, sequential, all begun and completed within
2026-08-11 UTC (`schedule.utcDay.oneDayEstablished` is true, `crossedMidnight`
false, no slot without a readable stamp). One CLI pinned by digest
(`codex.binarySha256`) and one model pinned by name (`gpt-5.6-sol`) — the
wrapper refuses a binary that does not hash to the digest *and* refuses a run
that does not report that model name, but a model name is not a digest, and an
earlier version of this sentence claimed both were. The preregistration and the
whole tree were frozen at `sha256:9fa37a51…` after nineteen review rounds,
**eighteen of them cross-vendor** — round 1 was an internal adversarial pass by
the drafter's own model lineage and `PREREG-REVIEW.md` labels it as such; an
earlier version of this sentence called all nineteen cross-vendor. 142 runs valid;
8 pipeline-invalid, of which 2 were caused by the host filesystem filling
mid-batch and are recorded in [`DEVIATIONS.md`](DEVIATIONS.md).

## The result

| arm | policy text | valid | classes covered | all six primary levels |
|---|---|---|---|---|
| **A** baseline | states 40 and 70 | 29/30 | 6 of 6 | HIGH |
| **B** reworded | states 40 and 70 | 28/30 | 6 of 6 | HIGH |
| **C** reordered clauses | states 40 and 70 | 28/30 | 6 of 6 | HIGH |
| **D** renamed | states 45 and 72 | 30/30 | 6 of 6 | HIGH |
| **E** denamed | **neither literal — both defined in words as fractions of a stated 0–100 scale** | 27/30 | 6 of 6 | HIGH |

`nP = 0`, `nC = 0`, `nH = 4`. The B/C control gate passed on 6 of 6 classes in
both control arms, so the arms were comparable and the null result is not a
broken pipeline. Per-protocol coverage is 100% everywhere; the ITT column varies
only with pipeline-invalid runs.

## The second registered verdict, which this file omitted until 2026-08-12

The scorer published **two** named outcomes, and every earlier version of this
analysis reported only one. §5.3 (ii) registered a prediction about arm D, and
`RESULTS.json`'s `verdicts.armD` records it landing on **row 1**, published as
**`COVERAGE-FOLLOWS-THE-NUMBERS`**: arm D's new-keyed level verdicts are HIGH on
4 of the four narrow numeric classes, and its old-keyed (S10) verdicts are HIGH
on **0** of them.

In plain terms: when the thresholds moved to 45 and 72, the records moved with
them. **61 records sit exactly on 45 and 50 exactly on 72, and not one of arm D's
480 records sits on 40 or 70.** S10 — old-edge cross-scoring [D-12] — is the
endpoint registered to see precisely this, and it saw nothing left behind.

That result is not decoration on R1's failure; it is the other half of the
instrument. It shows the author tracking the literals the policy states when it
states them, which is what makes arm E's behaviour when they are *not* stated
worth reporting at all. It also bears on [D-18]'s registered salience cost: 45
and 72 are not decade-round, and placement followed them anyway, so an author
merely drawn to round values does not account for arm D.

`RATES.md` has carried this verdict since the run. Its absence here was an
omission in the narrative, not in the data — and, unlike the other corrections
to this file, it ran *against* the study's interest rather than for it.

## Three readings, and which the data support

**The anchoring reading is refuted.** Arm E never saw the literals `40` or `70`
and still put **107 records exactly on an edge** — the same count as arm A. The
exactly-on-edge mass survives denaming intact. **What that licenses is narrow:**
this denaming did not move placement. It does *not* license "the numerals are
not the cause" — §5.5 registers that "an R1-UNSUPPORTED row does not license its
negation", and an earlier version of this sentence asserted exactly that. *(Corrected: an earlier version added that the hugging
shape survived "intact" one and two decimal places out. The aggregate
within-0.01 counts are comparable; the split is not — A is 36 within 0.001 and
89 within 0.01, E is 59 and 61.)*

**Misderivation is refuted.** §4.5's X6 sentinels were registered in advance to
catch an arm E that derived the thresholds *wrongly* — mass at 0.7/0.4, at 7/4,
at 28. **All five misderivation sentinels are empty.** Arm E produced 40 and 70
exactly, in every run, from a stated fraction of a stated range. *(Corrected: an
earlier version said "every sentinel is empty." X6 registers seven rows, and the
first two record the correct derivation — 70 in 49 records, 40 in 54 — which are
populated by design.)*

**The blind spot is not refuted, but it is narrower than first published.** The
policy implies a boundary at 39 that its text never states. The count of records
in the window `[38, 39)` is **zero in arms A, B and E, and 1 in arm C**; arm D
has no 39 edge, and at its own unstated edge of 44 the windowed count is zero.

*(Corrected, and this was the largest error in the first version: it said "in
every arm, including the baseline … zero — 0 of 464 in arm A, 0 of 432 in arm
E." Arm C is a counterexample and was already printed in `CENSUS.md`; and the
464/432 denominators describe the whole arm while the numerator is windowed —
**117 of arm A's 464 records and 101 of arm E's 432 are strictly below 39**.
Study 011's empty approach band `(23.75, 39)` reproduces in **arm B alone**.)*

What this study kills is our *explanation*, not the numerals as a candidate
cause. The immediate approach to the unstated edge is close to unpopulated
whether or not the stated thresholds are printed — so the pattern does not track
the policy's surface, and R1's account of it is withdrawn. *(Corrected
2026-08-12: this sentence previously concluded "so 'it copies the numerals it
sees' cannot be why". That is R1's negation, which §5.5 says the verdict does
not license.)* "The unstated edge is invisible" is also stronger than the data
support, and the baseline was never the clean contrast the first version
implied.

That leaves a question this design was not built to answer and does not: whether
a boundary a policy only implies is invisible because the author reasons from
stated structure and the structure is silent there, or because nothing in its
training data ever probed it. Both predict what we observed. Separating them
needs a policy family the model cannot have seen.

## What a reader should take from this

Not "the model derives boundaries" — that is the claim we did not earn. What the
150 runs do support is narrower and still useful: **on this policy family, this
model's boundary placement is insensitive to whether the boundary is written as
a numeral**, and **coverage of an unstated boundary is zero regardless**. If you
are judging a generated test suite by how many boundaries it hits, both halves
matter: the count will look the same whether or not you spelled the numbers out,
and it will not tell you about the edges you did not spell out at all.

## Everything else

`RESULTS.json` carries every rate as integers plus bounds, the §5 verdicts, the
decision row, and the seal. `RATES.md` renders it; `CENSUS.md` carries §4.5's
descriptive surface including the X2 dispersion buckets and X3 near-edge tables
this section quotes. `PREREG-REVIEW.md` carries all nineteen review rounds, the
stopping rule registered before round 18 ran, and the two findings accepted as
residuals at the freeze.
