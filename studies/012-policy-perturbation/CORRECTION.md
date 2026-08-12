# CORRECTION.md — Study 012

Written in every outcome, from the decision row `RESULTS.json` records. The
first line names that row. This study's README links here from the block that
states the publication commitment.

**The scorer computed §5.3 (i) row 4: `R1-UNSUPPORTED`.**

---

> ## This correction was itself corrected, on 2026-08-11
>
> The retraction below was published, and then checked claim by claim against
> `RESULTS.json` and the frozen registration. **Eight material errors were
> found in it.** The decision row, the arm table's counts, and
> `R1-UNSUPPORTED` all survived that check unchanged. What did not survive was
> the supporting narrative, in three places:
>
> 1. **"In every arm including the baseline, `belowCount` at the 39 edge is
>    zero" was false.** Arm C's `belowCount` is **1** — a record at 38, printed
>    in this study's own `CENSUS.md`. Arm D has no 39 edge at all. The zero
>    holds for A, B and E.
> 2. **"0 of 464 records in arm A, 0 of 432 in arm E" stated a proportion that
>    is not true.** `belowCount` is windowed over `[38, 39)` only. Against the
>    full record set, **117 of arm A's 464 records and 101 of arm E's 432 are
>    strictly below 39.**
> 3. **"Arm E — every numeral removed" overstated the manipulation, and
>    dropped a caveat the frozen preregistration said the reader is owed.**
>    Arm E defines both thresholds in words, as fractions of a stated range.
>
> Corrected sentences are in place below. Nothing was deleted to make the
> result look better; every changed claim is named here. This file is
> `freeze.excluded`, so these edits move no manifest-covered byte and
> `harness/integrity.py` still verifies `sha256:9fa37a51…`.
>
> That the first correction needed a second one is itself the finding §8 exists
> to publish: the false sentence was a universal asserted over a class instead
> of derived from it, and the counterexample was already sitting in our own
> published census.
>
> ### And a third round, on 2026-08-12
>
> Two further problems, neither of them arithmetic — which is why two passes of
> number-checking missed both:
>
> 4. **The published narrative asserted R1's negation**, which §5.5 registers as
>    not licensed: *"an R1-UNSUPPORTED row does not license its negation."*
>    Sentences to the effect of "the numerals were not the cause" stood in this
>    file, twice in `ANALYSIS.md`, and in Study 011's banner. A failed causal
>    prediction is not evidence for the opposite cause. Struck and replaced with
>    what the verdict does support: *this denaming did not move coverage.*
> 5. **A confirmed prediction was missing.** §5.3 (ii)'s arm-D result —
>    `COVERAGE-FOLLOWS-THE-NUMBERS` — appeared in `RATES.md` and in no narrative
>    file. Reporting the failed prediction and silently omitting the confirmed
>    one distorts the study even when every individual sentence is true. Added
>    below and to `ANALYSIS.md`.
>
> The first two rounds fixed claims that were false. This one fixes a claim that
> was *unlicensed* and an omission that was *flattering to the drama* — the two
> failure modes a numeric check cannot see.

---

# R1 is withdrawn. The prediction failed its own test.

**We published a directional prediction and it is wrong.** Study 011's
`MIRROR-AGREEMENT.md` registered, before this study existed, that removing the
stated numerals from a policy would collapse the blinded author's coverage of
the numeric classes — *"coverage of the denamed classes collapses, because
placement follows named numbers."* Issue #45 restated it and called it an IOU
this study would pay.

It is paid, and the answer is no. Arm E — the same rules with the threshold
**literals** removed, the clauses naming them only as "the review threshold" and
"the personal-data threshold", and a conventions paragraph defining those as
seven tenths and four tenths of a stated zero-to-one-hundred scale — covered
**all six semantic classes in all 27 of its valid runs**, reading HIGH on every
one.

*(The registered caveat, which an earlier version of this file dropped:
`PREREGISTRATION.md` §2.5 states that "E denames the *threshold literals*, it
does not remove numeric information … A reader who expected 'no numbers at all'
is owed that sentence." Arm E's values are recoverable by arithmetic from words,
and its `POLICY.md` is not digit-free — clause labels P1–P5 and "ISO 3166-1
alpha-2" survive, none of them equal to 40 or 70. What arm E measures is the
cost of **indirection**, not of **absence**.)* `nH = 4` of the four narrow numeric classes,
against a registered confirmation threshold that required arm E to read LOW on
three of them. Not a smaller effect than expected. No effect: arm E's coverage
is indistinguishable from the baseline's.

**And this study does not thereby establish the opposite.** Maintained coverage
in arm E is compatible with the author deriving the boundaries from the prose,
and it is equally compatible with the author recognising this policy family from
its training data and reproducing boundaries it was never told — the corpus has
been public in this repository since 2026-08-06. **This design cannot separate
those two explanations**, §9 registered that limit before the data existed, and
any write-up asserting the first is a claim this study did not earn.

## What the numbers were

| arm | policy text | valid runs | classes covered | primary level, all six classes |
|---|---|---|---|---|
| **A** baseline | states 40 and 70 | 29 of 30 | 6 of 6 | HIGH |
| **B** reworded | states 40 and 70 | 28 of 30 | 6 of 6 | HIGH |
| **C** reordered | states 40 and 70 | 28 of 30 | 6 of 6 | HIGH |
| **D** renamed | states 45 and 72 | 30 of 30 | 6 of 6 | HIGH |
| **E** denamed | **states neither literal — both thresholds defined in words, as fractions of a stated zero-to-one-hundred scale** | 27 of 30 | 6 of 6 | HIGH |

Per-protocol coverage is 100% in every arm on every class. The differences in
the intention-to-treat column are pipeline-invalid runs, not missed classes.
Arm E carries a registered stated caution over the whole arm
(`arms.E.population.pipelineCaution` is `true`, rendered in `RATES.md` as
"ρ_X ≥ 0.10"), as does the cross-arm valid count; the caution is about how many
runs survived the pipeline, not about what the surviving runs covered.

## The other registered verdict, omitted from this file until 2026-08-12

R1 is not the only prediction this study registered, and it is the only one
earlier versions of this file reported. §5.3 (ii)'s arm-D prediction landed on
**row 1**, published by the scorer as **`COVERAGE-FOLLOWS-THE-NUMBERS`**: when
the thresholds moved to 45 and 72, placement moved with them — **61 records
exactly on 45, 50 exactly on 72, and none of arm D's 480 records on 40 or 70.**

It belongs in a correction because omitting a *confirmed* prediction from the
document that announces a *failed* one distorts the study in the direction of
drama, even though no individual sentence was false. `RATES.md` has carried it
since the run.

## The part that survives, and the part that does not

**Does not survive: the anchoring reading.** Arm E was never shown the literals
`40` or `70`, and it placed **107 records exactly on an edge** — the same count
as arm A's 107. Whatever put those values there, it was not the numerals being
printed in the text. *(An earlier version added "with the same hugging shape one
and two decimal places out." That gloss is withdrawn: the aggregate within-0.01
counts are comparable, but the split is not — arm A is 36 within 0.001 and 89
within 0.01, arm E is 59 and 61.)*

**Does not survive: misderivation as an explanation.** §4.5's X6 sentinels were
registered in advance to catch an arm E that derived the thresholds *wrongly* —
mass at 0.7 and 0.4, at 7 and 4, at 28. **All five of those misderivation
sentinels are empty.** Arm E did not approximate the thresholds; it produced 40
and 70 exactly. *(X6's registered list has seven rows, not five: the first two
record the **correct** derivation, and are populated by design — 70 exactly in
49 records, 40 in 54. An earlier version of this file said "every sentinel is
empty," which is wrong about those two.)*

**Survives, but is narrower than first published: the unstated edge is still
barely probed.** The policy implies a boundary at 39 that its text never prints.
`belowCount` — the count of records in the window `[38, 39)` — is **zero in arms
A, B and E**, and **1 in arm C** (a single record at 38). Arm D has no 39 edge
at all; its thresholds are 45 and 72, and at its own unstated edge of 44 the
windowed count is likewise zero.

Two things an earlier version of this passage got wrong, both in the direction
of making the finding look stronger:

- It said **"every arm including the baseline"**. Arm C is a counterexample, and
  it was printed in this study's own `CENSUS.md` when the claim was published.
- It paired `belowCount` with the arm's total record count — "0 of 464 records
  in arm A, 0 of 432 in arm E" — which reads as *no record anywhere below 39*.
  That is false. **117 of arm A's 464 records and 101 of arm E's 432 are
  strictly below 39.** They simply sit further down the scale than the window.

Study 011's original observation was the *empty approach band* `(23.75, 39)`.
**That band reproduces in arm B only.** It is occupied in A (27.6, 32, 35), in
C (25 ×2, 25.5, 35 ×2, 38) and in E (25, 27.5, 35). So the honest statement is
the weaker one: across five arms the immediate approach to the unstated edge is
close to unpopulated, but it is not empty, and it was not empty in the baseline
either.

**Corrected again, 2026-08-12 — and this one is about what a verdict licenses,
not about a number.** An earlier version of this paragraph ended: *"the pattern
is not caused by the numerals being present, because removing them changed
nothing."* That is the inference §5.5 registered a rule against — **"an
R1-UNSUPPORTED row does not license its negation"** — and it appeared in this
file, twice in `ANALYSIS.md`, and in Study 011's banner. R1 asserted a cause;
its failure does not establish the opposite cause, because a snapshot that has
seen this policy family can reproduce 40 and 70 without deriving them, and
because arm E is **one** denaming of **one** family at **one** snapshot on
**one** day (§5.5, §9).

What the study is entitled to say, and all it is entitled to say: **this
denaming did not move coverage.** That is compatible with derivation and with
recall, and the design cannot separate them. Anything stronger — including the
comfortable-sounding "so it wasn't the numerals" — is a claim this study did not
earn, and stating it was the same failure as the ones above, in a register where
no arithmetic check would ever have caught it.

## What this correction is not

No re-cutting of §5's thresholds. No "the effect was smaller than expected." No
relegation to a limitations section. The registered rule was that arm E reading
HIGH on three or more of the four narrow numeric classes publishes `R1` as
UNSUPPORTED with the same prominence as the claim, and it read HIGH on four.

The census's own descriptive sentence about its corpus — that Study 011's
records hug the stated thresholds and never approach the unstated one — stands.
It is R1, the causal reading placed on it, that does not.
