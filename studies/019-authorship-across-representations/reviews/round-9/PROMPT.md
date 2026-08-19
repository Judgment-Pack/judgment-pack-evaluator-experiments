# Review round 9 — prompt (verbatim)

You are the same cross-vendor adversarial reviewer (RFC 0009). Round 8's eight findings
are dispositioned in `PREREG-REVIEW.md` (round-8 table; suite of record 780/780, working
tree and archive reconstruction both, the reconstruction's tree hash byte-identical to
the index; thirteen mutation checks run, one deliberate redundancy recorded as
non-discriminable by single-point mutation rather than claimed otherwise).

## First job: verify the round-8 dispositions

Same rule as every round: verify each cited enforcement, run it where it is a test,
construct the residual where you can. The heart of the round: the freeze path now calls
the sealed set's own loader (R8-2), the block machinery refuses everything readable two
ways (R8-3/4), the liveness helper serves both readers (R8-5/7), the marker span has one
reading (R8-6), and `harness/grid_gate.py` wires the brief's freeze-time grid assertion
(R8-8) — attack each with constructions as you always have.

## Second job: the final read

You upheld the descope on its merits in round 8; its structural replacement was this
response. Read the tree as the frozen reader one final time. The freeze ceremony's
obligations are enumerated by the gate itself — fifteen pending, three of them registered
documents not yet authored, every one named by `make_manifest.py --check`. If anything
OUTSIDE that enumerated ceremony still stands between this tree and the freeze, it is a
finding. If nothing does, your verdict line should say so in the regime's exact words.

## Output

Numbered findings `R9-<n>` if any (severity, file/section, failure mode, concrete fix);
the disposition-verification table for R8-1..R8-8; then one line exactly:
`freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim. A clean pass is a finding only if you can defend
it — and convergence to be agreeable is as much a failure as manufactured findings.
