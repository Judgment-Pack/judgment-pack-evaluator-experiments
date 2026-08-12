# Round-1 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for a study preregistration in the
judgment-pack-evaluator-experiments repository (RFC 0009's regime: an independent
cross-vendor review recorded verbatim with a written maintainer disposition per finding,
before the preregistration is frozen). You are a model from a different vendor than the one
that drafted the study. Find where it overclaims, misregisters an expectation, hides a
weakness behind a registered boundary, or builds an apparatus that cannot support the
conclusion it will later state. A clean pass is a finding only if you can defend it.

The study is Study 018 (transition rules over cited registry state), DRAFT, at:
  <study worktree>/

Read: README.md, PREREGISTRATION.md, rule/SPEC.md, rule/transition.py, rule/citation.py,
harness/PINS.json, harness/MATRIX.json (all 18 cells), harness/MATRIX-HOLDOUT.json,
harness/upstream016.py, harness/build_fixtures.py, harness/run_verify.py, harness/score.py,
harness/tests/*.py, and spot-check fixtures/cells/ and pilots/.

Cross-references to verify against source, not trust:
- Study 016's frozen tree two directories over (studies/016-policy-currency-anchor/): the
  pinned upstream modules, and what its currency layer actually reports.
- Study 017 (studies/017-witnessed-currency/): this study inherits its harness discipline;
  its PREREG-REVIEW.md records seven rounds of findings that this study should not
  re-introduce.
- Spec RFC 0011 at <spec worktree>/rfcs/0011-judgment-currency-anchor.md — especially §2a (the
  separation this study measures), Unresolved #3 (ordering), #10 (where transition rules
  live) and #11 (what a cited head buys), plus rfcs/reviews/0011-round-5.md whose
  dispositions bound what may be claimed about a citation.

Scrutinise, at minimum:
1. The central claim: that four registered cells share commitment, snapshot and trust
   configuration byte-for-byte and differ only in rule configuration, so the differing
   outcomes are the rule's doing. Verify it from the fixture bytes, not the test.
2. `bnd-backdated-citation` is registered byte-identical to `div-run-to-expiry`. Is that a
   fair exhibit of "honest and backdated reliance are the same evidence", or does calling
   the same bytes two cells inflate the endpoint count with one adjudication? Study 017
   faced this question (its R1-9) and resolved it one way; is this study's answer right?
3. The three rules are a construct. Does any sentence treat them as more than that? Is the
   position-window model defensible given that RFC 0011 Unresolved #3 says no ordering
   exists offline, or does the study lean on it while disclaiming it?
4. Layer separation: does the transition layer ever recompute membership rather than
   consuming Layer CURRENCY's verdict? Does any registered expectation make the two layers
   agree by construction rather than by measurement?
5. The transition vocabulary and ceremony (rule/SPEC.md §§3–4 vs rule/transition.py): any
   input where first-failure ordering misattributes a code; any registered code unreachable;
   the fold's position semantics against the pinned upstream's set semantics.
6. `registeredAbsences` and the five citation-less cells: is the validity/detection
   separation honest here, or does a registered absence do work an expectation should?
7. `expectedRuleEvidence` (citedPosition, retiredAtPosition): are the registered values
   correct against the built fixtures, and is adjudicating them as separate divergence
   channels sound?
8. Inherited discipline: does the bootstrap cache check, the stamped pin binding, the
   dependency enforcement and the upstream loader actually work here, or were they copied
   without being retargeted?
9. Any cell whose registered expectation you can argue is WRONG before a registered run.

Also state, one line at the end, whether at the next round you are prepared to author a
reviewer holdout set (cells you register, never run before the freeze, committed verbatim
with attribution). Do not author cells this round.

Output, exactly:
- Numbered findings R1-<n>: severity BLOCKER / MAJOR / MINOR, file/section, a one-paragraph
  failure mode, and a concrete fix.
- Then one line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Cite the file you read for every claim.
```
