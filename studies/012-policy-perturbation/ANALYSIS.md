# Study 012 — is the blinded author's test surface anchored to the policy's surface form?

**R1 is UNSUPPORTED. The prediction this study was built to test failed, and it
failed cleanly.** We published, before this study existed, that removing a
policy's stated numerals would collapse the blinded author's coverage of the
numeric classes, because placement follows named numbers. Arm E — the same rules
with every numeral removed — covered all six semantic classes in all 27 of its
valid runs, reading HIGH on every one, indistinguishable from the baseline.
§5.3 (i) row 4 fired. **And this study does not thereby establish the opposite:**
maintained coverage is equally compatible with the author deriving the
boundaries from prose and with it recognising this policy family from a corpus
public since 2026-08-06, and this design cannot separate them — §9 said so
before the data existed. The full retraction is at the head of
[`CORRECTION.md`](CORRECTION.md).

## What ran

150 authoring calls, 30 per arm, sequential, all begun and completed within
2026-08-11 UTC (`schedule.utcDay.oneDayEstablished` is true, `crossedMidnight`
false, no slot without a readable stamp). One model, one CLI, both pinned by
digest; the preregistration and the whole tree frozen at
`sha256:9fa37a51…` after nineteen cross-vendor review rounds. 142 runs valid;
8 pipeline-invalid, of which 2 were caused by the host filesystem filling
mid-batch and are recorded in [`DEVIATIONS.md`](DEVIATIONS.md).

## The result

| arm | policy text | valid | classes covered | all six primary levels |
|---|---|---|---|---|
| **A** baseline | states 40 and 70 | 29/30 | 6 of 6 | HIGH |
| **B** reworded | states 40 and 70 | 28/30 | 6 of 6 | HIGH |
| **C** reordered clauses | states 40 and 70 | 28/30 | 6 of 6 | HIGH |
| **D** renamed | states 45 and 72 | 30/30 | 6 of 6 | HIGH |
| **E** denamed | **no numerals** | 27/30 | 6 of 6 | HIGH |

`nP = 0`, `nC = 0`, `nH = 4`. The B/C control gate passed on 6 of 6 classes in
both control arms, so the arms were comparable and the null result is not a
broken pipeline. Per-protocol coverage is 100% everywhere; the ITT column varies
only with pipeline-invalid runs.

## Three readings, and which the data support

**The anchoring reading is refuted.** Arm E never saw `40` or `70` and still put
**107 records exactly on an edge** — the same count as arm A. The hugging shape
survives denaming intact, so it is not produced by the numerals being printed.

**Misderivation is refuted.** §4.5's X6 sentinels were registered in advance to
catch an arm E that derived the thresholds *wrongly* — mass at 0.7/0.4, at 7/4,
at 28. Every sentinel is empty. Arm E produced 40 and 70 exactly, from prose
alone, in every run.

**The blind spot is not refuted, and is now the sharper finding.** The policy
implies a boundary at 39 that its text never states. In **every arm, including
the baseline**, the count of records below that edge is **zero** — 0 of 464 in
arm A, 0 of 432 in arm E. Study 011's original observation reproduces exactly.
What this study kills is our *explanation* of it. The unstated edge is missed
whether or not the stated ones are printed, so "it copies the numerals it sees"
cannot be why.

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
