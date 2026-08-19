# Review round 3 — prompt (verbatim)

You are the same cross-vendor adversarial reviewer (RFC 0009). Round 2's fourteen findings
are dispositioned in `PREREG-REVIEW.md` (round-2 table, each citing its enforcing test);
the response also records one defect it found beyond your review (opa test result
ordering) and one your R2-5 surfaced en route (protocol violations mis-filed as
apparatus). Suite of record: 669 passing with the pinned engines.

## First job: verify the round-2 dispositions

Same rule as last round: for each of the fourteen, verify the cited enforcement, run it
where it is a test, and construct the residual if you can. One line per disposition that
holds; a numbered finding for one that over-claims. Note in particular the R2-3
disposition's factual claim — that the corrected kill semantics leave `E4-PILOT-v3.json`
numerically identical to v2 — and check it against the artifacts rather than the prose.

## Second job: repair your own sealed set

Your round-2 sealed set is committed byte-for-byte under `controls/reviewer-mutants/`,
including two defects the record attributes to your side (PREREG-REVIEW.md, round-2
sealed-set section): `rm-jps-03.json` neither hashes to your manifest digest nor validates
(`JPS-STRUCTURE-DECIMAL-OPERAND` — the emitted bytes appear to be a pre-final draft), and
`rm-rego-01.rego` is valid but does not hash to your attested digest. The maintainer has
touched nothing. Re-issue now, in your output: the corrected `rm-jps-03.json` payload as a
fenced block (validate it against the pinned jpack before emitting), and a corrected
`MANIFEST.json` fenced block re-attesting all six digests over the exact bytes you emit or
previously emitted. State for the record whether `rm-jps-03`'s corrected payload preserves
the probe intent you registered for it in round 2.

## Third job: the frozen-reader audit

This program's late rounds deliberately ask: what do the immutable-candidate files say to
a reader holding only them? Read `PREREGISTRATION.md`, `design/POLICY-DRAFT.md`, the
README, `PREREG-REVIEW.md`, and the OC table as that reader. Find any sentence the
artifacts contradict, any count that no longer recomputes, any claim a superseded artifact
still makes without a banner, and any safeguard asserted without a test. The response
swept these once; your job is to find what the sweep missed.

## Output

Numbered findings `R3-<n>` (severity, file/section, failure mode, concrete fix); the
disposition-verification table for R2-1..R2-14; the re-issued set materials; then one line
exactly: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`. If
your verdict is `freezable after listed fixes`, list the fixes in dependency order. Cite
the file you read for every claim. A clean pass is a finding only if you can defend it.
