# Review round 11 — prompt (verbatim)

You are the same cross-vendor adversarial reviewer (RFC 0009). Round 10's three findings
are dispositioned in `PREREG-REVIEW.md` (round-10 table; suite of record 829/829 both
ways; fifteen mutation checks). R10-1 was adopted IN FULL, including both halves of your
proposed depth that the first response had deferred: the scorer now requires every
admitted slot's wrapper-stamped registry digest to equal the attempt's own, and the
freeze refuses pre-existing authoring state derived from the driver's constants.

## First job: verify the round-10 dispositions

The usual way — constructions welcome. The substitute-registry attack now has three
layers to test: the argument surface, the load surface, and the scoring comparison; the
freeze has two occupancy gates (prior attempts, prior authoring state).

## Second job: the verdict, on the registered surface

Under §4b as registered. The registered surface's finding history is now: three findings
in round 10, all closed within the round; nothing else since round 4's record-keeping.
Read it as the frozen reader. New advisories are welcome and recorded; they do not gate.
If anything on the registered surface, outside the enumerated freeze ceremony, still
stands between this tree and the freeze, it is a finding. If nothing does, your final
line should be the exact words.

## Output

Numbered findings `R11-<n>` if any (severity, file/section, failure mode, concrete fix;
mark intended advisories explicitly); the disposition-verification table for
R10-1..R10-3; then one line exactly: `freezable as written`,
`freezable after listed fixes`, or `DO NOT FREEZE`. Cite the file you read for every
claim. A clean pass is a finding only if you can defend it — and convergence to be
agreeable is as much a failure as manufactured findings.
