# Review round 2 — prompt (verbatim)

You are the same cross-vendor adversarial reviewer (RFC 0009 regime) that produced round 1
(`reviews/round-1/REVIEW.md`, verdict DO NOT FREEZE, findings R1-1 … R1-20). The study is
`studies/019-authorship-across-representations/`. Since your round, the maintainer landed a
response and wrote one disposition per finding: read `PREREG-REVIEW.md` in full first —
its round-1 table cites, for every finding, the test or artifact said to enforce the fix.

## This round's first job: verify the dispositions

This program's recorded experience is that the dominant late-round failure mode is
dispositions written as complete while residuals are live — fixed exactly where the
reviewer pointed, then generalized in prose beyond what the code does. For EACH of the
twenty dispositions: verify the cited enforcement exists, run it where it is a test, and
try to construct the residual — an input or path on which the original defect survives the
fix. A disposition that holds is one line; a disposition that over-claims is a numbered
finding with the residual demonstrated.

Priority targets, from the dispositions' own known-imperfect list and from what changed
most:
1. The X1 retirement chain (R1-2/R1-3): `design/reference/refA/PACK-CHANGE-001.md`, the
   repaired pack, the reissued `OFFGOLD-CERT`, the empty exclusion registries, the
   adjacency falsifier. Is the repair exactly as narrow as claimed? Does anything still
   read the retired predicate as if it gated?
2. The per-language cut layer and the E4 chain end to end under the current manifests
   (R1-1/R1-8/R1-11): construct a suite or failure mode that scores wrongly.
3. The population/partition/transcript-binding paths (R1-4/R1-5/R1-6): the response says
   fail-closed everywhere — find the leak.
4. The statistics relabeling (R1-16) and the decision layer (R1-13/R1-14): does any
   published artifact still claim what was withdrawn, or compute what a gate forbids?
5. The preregistration's third revision as a frozen-reader document (R1-15/R1-17/R1-18/
   R1-19): read it holding only the tree — find the sentence the artifacts contradict.
   The maintainer's known-imperfect list names three specific items round 2 should read
   with intent; do.

## This round's second job: author the sealed reviewer mutant set

You stated in round 1 that you are prepared. Author it now, in your review output — it
will be committed byte-for-byte with attribution under `controls/reviewer-mutants/` and
sealed (its digest becomes the `reviewerMutantSet` freeze pin; first execution is at the
primary attempt; scored "as authored"; published separately; it moves nothing in R1).

Requirements (the loader `harness/e4lib/reviewer.py` enforces the schema — read it):
- 6–10 mutants total, both languages represented, each a SINGLE semantic edit to the
  frozen reference (`design/reference/refA/pack.json` db977607… / `refB/policy.rego`),
  chosen by YOU for what run-authored suites are likely to miss — do not reuse the
  registered generators' classes mechanically.
- For each: a complete payload file emitted as a fenced block with an exact filename
  (`rm-jps-01.json`, `rm-rego-01.rego`, …), valid under its language's checker (validate
  them yourself with the pinned binaries), plus one sentence in prose on what it probes.
- A `MANIFEST.json` fenced block: `{"reviewerSetVersion": 1, "mutants": [{"id", "language"
  ("jps"|"rego"), "file", "sha256"}]}` with the sha256 you computed over each payload's
  exact bytes.
- Any predictions you wish to register (which suites will miss which mutant, expected
  witness behavior) go in your review prose, dated, as YOUR registered statements — the
  program scores predicted-vs-observed separately and neither side is edited afterward.

## Output

Numbered findings `R2-<n>` (severity, file/section, failure mode, concrete fix), the
disposition-verification table (one line per R1-finding: HOLDS or the R2 finding it
spawned), the sealed set, and one line exactly: `freezable as written`,
`freezable after listed fixes`, or `DO NOT FREEZE`. Cite the file you read for every
claim. A clean pass is a finding only if you can defend it.
