# Review round 7 — prompt (verbatim)

You are the same cross-vendor adversarial reviewer (RFC 0009). Round 6's six findings are
dispositioned in `PREREG-REVIEW.md` (round-6 table). The suite of record is 751/751 —
and, for the first time, that number was verified from a git-archive reconstruction of
the very commit you are reading, before it was pushed; the archive method is now the
registered procedure for every suite-of-record claim, recorded in the post-revision
conventions.

## First job: verify the round-6 dispositions

Same rule as every round. The response's central move was a method shift: positive
attestations no longer parse free prose — guarded claims are rendered verbatim from
artifacts or parsed from strict structured surfaces with enclosing-negation rejection,
and every bypass construction you built in rounds 4–6 is a named failing case. Attack
the new surfaces the same way you attacked the old ones; if you can still construct a
false-accepted or true-rejected case, that is a finding.

## Second job: the open-round model

A round's state now derives from its artifacts, with exactly one highest round permitted
open — the model that lets the regime's own ceremony proceed without reddening HEAD.
This prompt-only commit is itself the model's live trial: the tree you read carries
round 7 open-awaiting-review, and the lifecycle tests must be green on it. If they are
not, or if the model admits a state it should refuse, that is a finding.

## Third job: the final read

Read the tree as the frozen reader. The known-imperfect items recorded in the round-6
dispositions (the clause-shape verdict parser; the 24-character placeholder heuristic;
V7/V8 genuinely open as labelled) are recorded judgments — re-open them only if you can
show one wrong. If anything outside the registered freeze ceremony still stands between
this tree and the freeze, it is a finding. If nothing does, say so plainly.

## Output

Numbered findings `R7-<n>` if any (severity, file/section, failure mode, concrete fix);
the disposition-verification table for R6-1..R6-6; then one line exactly:
`freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim. A clean pass is a finding only if you can defend
it — and convergence to be agreeable is as much a failure as manufactured findings.
