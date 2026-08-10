# Round-1 prompt (verbatim)

```
You are the interim-review-regime adversarial reviewer for a study preregistration in the
judgment-pack-evaluator-experiments repository (the regime RFC 0009 in the spec repo
mandates: a cross-vendor review recorded verbatim with per-finding maintainer dispositions
before any freeze). You are a model from a different vendor than the one that drafted the
study; your job is to find where it overclaims, misregisters an expectation, hides a
weakness behind a registered boundary, or builds an apparatus that cannot support the
claim it will later make — BEFORE it freezes. A clean pass is a finding of its own only if
you can defend it.

The study under review is Study 016 (policy-currency anchor), DRAFT, at:

  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/wt016/studies/016-policy-currency-anchor/

Read, at minimum: README.md, PREREGISTRATION.md (the governing draft), registry/SPEC.md
(the registered schema/ceremony/vocabulary), registry/checkpoint.py,
registry/verify_currency.py, harness/PINS.json, harness/MATRIX.json (all 20 registered
cells), harness/MATRIX-HOLDOUT.json, harness/upstream014.py, harness/build_fixtures.py,
harness/run_verify.py, harness/score.py, harness/make_manifest.py, harness/tests/*.py,
and spot-check fixtures/cells/ (built bytes) and pilots/2026-08-10-build-pilot-01/
(labeled non-citable harness validation).

Cross-references you MUST verify against source rather than trust:

- Study 014's frozen artifacts, one directory up:
  .../wt016/studies/014-openworkproof-binding/ — PREREGISTRATION.md (especially section 4c
  and the e22 row's registered status), adapter/SPEC.md, harness/MATRIX.json,
  harness/PINS.json, harness/build_fixtures.py (the e22 construction Study 016 claims to
  rebuild), ANALYSIS.md and DEVIATIONS.md (the corrected e18/e22 wording).
- Spec RFC 0011 and its review record, at:
  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/spec-main/rfcs/0011-judgment-currency-anchor.md
  and .../spec-main/rfcs/reviews/0011-round-1.md — the R-1..R-13 dispositions are the
  registered ceiling on what any Study 016 result may be read to claim; check the
  preregistration and SPEC against them line by line.

Toolchain, if you want to execute anything (read-only sandbox; execution is optional and
findings from reading alone are fine):
  JPACK_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/jpack-0.17.0/jpack
  OWP_SOURCE=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/OpenWorkProof
  Python venv: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/fb61ba24-87d5-4854-b18b-5977006cda4c/scratchpad/venv/bin/python

Attack, at minimum:

1. Decision D-3: the three registered-undetected cells are ENDPOINTS with all-pass
   expectations (cur-authz-rollback-accepted, cur-older-snapshot-unpinned,
   cur-split-view-a), deliberately strengthening 014's descriptive-e22 precedent. Does
   this hold water, or does it launder non-detection into R1 credit / make R1 trivially
   satisfiable? Is the R1 wording in PREREGISTRATION section 1 sound in both directions?
2. The split-view pair: is the construction genuinely an equivocation exhibit, or is it
   trivial (two registries that simply differ, dressed as a fork)? Is "no code in either
   run reveals the fork" a property of the registered verifier or an artifact of not
   looking? Is the impossibility framing ("no single offline run can observe it")
   overstated anywhere relative to what the cells actually show?
3. The registered byte-identity groups (cur-concurrent-set == cur-older-snapshot-unpinned;
   cur-retired-reuse == both dem-freshness cells): honest exhibit, or double-counting that
   inflates the endpoint denominator with copies of one adjudication? Should identical
   bytes be one cell with registered multiple readings instead?
4. The Layer CURRENCY ceremony (SPEC section 3, verify_currency.py): any input where the
   first-failure ordering misattributes a code? The authority-unpinned vs signature-invalid
   distinction rests on comparing the record's authorityKeyId string before signature math —
   is that sound, or can a construction that lies about its key id shift its code? Is the
   fold's strictness (retire-of-non-current refused, re-add-of-current refused,
   binding-rebound across retirement) consistent with RFC 0011 R-8's event model, and does
   it refuse any legitimate lifecycle?
5. persistedMinimumHead: does prefix containment actually deliver the claimed same-length
   fork refusal? Does optional verifier state contradict any "offline, two pins only"
   claim made elsewhere in the documents?
6. Decision D-1 (Study 014 sources as digest-pinned upstream, harness/upstream014.py):
   are the digests enforced on EVERY path that imports 014 code (build, run_verify, score,
   tests)? Any sys.path shadowing or module-name collision that could substitute code
   without tripping a pin? Does 016 consuming 014's build machinery retroactively weaken
   any 014 claim?
7. The jpack v0.17.0 pivot: chains are rebuilt, and PREREGISTRATION section 9 frames the
   three chain layers as "replicating 014's result under a new evaluator release". Is that
   framing right, or does any sentence still borrow 014's frozen evidence for bytes 014
   never saw?
8. The e22-analog (cur-authz-rollback-accepted): is the construction in
   harness/build_fixtures.py actually equivalent to 014's registered e22 construction, and
   does the all-pass expectation across all four layers actually follow from it?
9. The claim/non-claim ceiling versus RFC 0011's R-1..R-13 dispositions: any residual
   overclaim, especially R-7 (membership-at-snapshot only), R-9 (equivocation and the
   isolated-verifier limit), R-6 (the digest prerequisite is unmet and the study uses an
   expedient), R-2 (nothing may read as a format landing anywhere)?
10. harness/PINS.json and score.py enforcement: gaps between what the note claims is
    enforced and what the code enforces; the genesis-head-constancy claim; the fixed-seed
    authority keys (seeds are public strings - does anything anywhere depend on their
    secrecy?); the frozen cell-id set; the manifest anchor order.
11. Any cell in harness/MATRIX.json whose registered expectation you can argue is WRONG
    before a registered run - that is exactly the kind of finding this round exists for.

Also state - one line, at the end - whether at the next round you are prepared to author a
reviewer holdout stratum (cells registered by you, never executed pre-freeze, committed
verbatim with attribution), per Study 014's round-2 precedent. Do not author cells this
round.

Output, exactly:
- Numbered findings R1-<n>, each: severity BLOCKER / MAJOR / MINOR, the file/section, a
  one-paragraph failure mode, and a concrete fix.
- Then a one-line verdict: `freezable as written`, `freezable after listed fixes`, or
  `DO NOT FREEZE`.
Findings only. Cite the file you read for every claim; if you could not verify a
cross-reference, say so explicitly rather than guessing.
```
