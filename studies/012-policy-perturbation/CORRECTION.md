# CORRECTION.md — Study 012

Written in every outcome, from the decision row `RESULTS.json` records. The
first line names that row. This study's README links here from the block that
states the publication commitment.

**The scorer computed §5.3 (i) row 4: `R1-UNSUPPORTED`.**

---

# R1 is withdrawn. The prediction failed its own test.

**We published a directional prediction and it is wrong.** Study 011's
`MIRROR-AGREEMENT.md` registered, before this study existed, that removing the
stated numerals from a policy would collapse the blinded author's coverage of
the numeric classes — *"coverage of the denamed classes collapses, because
placement follows named numbers."* Issue #45 restated it and called it an IOU
this study would pay.

It is paid, and the answer is no. Arm E — the same rules with every numeral
removed, thresholds described only as "the review threshold" and "the
personal-data floor" — covered **all six semantic classes in all 27 of its valid
runs**, reading HIGH on every one. `nH = 4` of the four narrow numeric classes,
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
| **E** denamed | **states no numerals** | 27 of 30 | 6 of 6 | HIGH |

Per-protocol coverage is 100% in every arm on every class. The differences in
the intention-to-treat column are pipeline-invalid runs, not missed classes.

## The part that survives, and the part that does not

**Does not survive: the anchoring reading.** Arm E was never shown `40` or `70`,
and it placed **107 records exactly on an edge** — the same count as arm A's
107 — with the same hugging shape one and two decimal places out. Whatever put
those values there, it was not the numerals being printed in the text.

**Does not survive: misderivation as an explanation.** §4.5's X6 sentinels were
registered in advance to catch an arm E that derived the thresholds *wrongly* —
mass at 0.7 and 0.4, at 7 and 4, at 28. Every one of those sentinels is **empty**.
Arm E did not approximate the thresholds. It produced 40 and 70 exactly.

**Survives, and is now the more interesting finding: the unstated edge is still
invisible.** The policy implies a boundary at 39 that its text never prints. In
Study 011's corpus nothing sat below it. Here, in **every arm including the
baseline**, `belowCount` at the 39 edge is **zero** — 0 of 464 records in arm A,
0 of 432 in arm E. The blind spot that motivated this study is real and is
reproduced. What this study refutes is only our explanation of *why*: it is not
caused by the numerals being present, because removing them changed nothing.

## What this correction is not

No re-cutting of §5's thresholds. No "the effect was smaller than expected." No
relegation to a limitations section. The registered rule was that arm E reading
HIGH on three or more of the four narrow numeric classes publishes `R1` as
UNSUPPORTED with the same prominence as the claim, and it read HIGH on four.

The census's own descriptive sentence about its corpus — that Study 011's
records hug the stated thresholds and never approach the unstated one — stands.
It is R1, the causal reading placed on it, that does not.
