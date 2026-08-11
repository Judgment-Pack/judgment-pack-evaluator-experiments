# Round-1 prompt (verbatim)

```
You are the interim-review-regime peer reviewer for a research preregistration in the
judgment-pack-evaluator-experiments repository (RFC 0009's regime: an independent
cross-vendor review, recorded verbatim with a written maintainer disposition per finding,
before the preregistration is frozen). You are a model from a different vendor than the
one that drafted the study. Your job is to find where the study overclaims, misregisters
an expected result, hides a weakness behind a registered boundary, or builds an apparatus
that cannot support the conclusion it will later state. A clean pass is itself a finding
only if you can defend it.

The study is Study 017 (witnessed currency), a determinism-and-cryptography experiment
about the LIMITS of a signed version-history "witness" mechanism. It is DRAFT, at:

  <study worktree>/

Read: README.md, PREREGISTRATION.md, witness/SPEC.md, witness/sighting.py,
witness/verify_witness.py, harness/PINS.json, harness/MATRIX.json (all 14 cells),
harness/MATRIX-HOLDOUT.json, harness/upstream016.py, harness/build_fixtures.py,
harness/run_verify.py, harness/score.py, harness/make_manifest.py, harness/tests/*.py,
and spot-check fixtures/cells/ and pilots/2026-08-10-build-pilot-01/ (labeled
non-citable). Optional: the venv at
<scratchpad>/venv/bin/python
runs the whole suite offline.

Verify these cross-references against source rather than trust them:
- Study 016's FROZEN tree, one directory up (.../016-policy-currency-anchor/): the pinned
  upstream modules registry/verify_currency.py and registry/checkpoint.py, and its
  PREREG-REVIEW.md, whose "registered-undetected endpoint with an all-pass expectation"
  convention this study reuses.
- Spec RFC 0011 with its merged amendment at
  <scratchpad>/spec-wt/rfcs/0011-judgment-currency-anchor.md
  (Unresolved #8/#9) and its review record rfcs/reviews/0011-round-3.md — those
  dispositions bound what any claim about a witness mechanism may say: observability not
  prevention, always conditional on the specific contract clause a cell isolates, and no
  blanket "the mechanism detects X" language.

Scrutinize, at minimum:
1. Dropping the receipt chains (design decision D-1, registry-and-witness only): does it
   quietly weaken a conclusion the study still states? Is the synthetic identity tuple a
   faithful stand-in, and does any sentence read as though a full multi-layer run happened?
2. The routing decision D-3: an unpinned witness's record is ignored-and-counted, while a
   record naming a PINNED witness that fails signature verification returns a hard code —
   and the routing is by the record's own UNAUTHENTICATED key-id label. Study 016's round
   1 (finding R1-6) removed exactly this kind of label-based code attribution. Is this
   study's version sound because the label can only cause refusal and never acceptance, or
   is there an input where the label routing changes an outcome dishonestly? Try to build one.
2b. Study 016's `verify_currency.py` (Layer CURRENCY) is consumed unmodified but ALSO given
   inputs 016 never designed for — 017's own synthetic snapshots and trust configs. Does
   any 017 cell drive that frozen verifier into a state its own tests never covered, such
   that a currency-layer expectation here is actually unverified against 016's contract?
3. The "collusion" pair (wit-collusion-a/b): is the structural check in score.py
   (_collusion_structure) sufficient to establish that one witness signed two conflicting
   records, or can it pass vacuously / by construction error? Is the
   "independence-as-a-difference" framing (wit-one-honest minus wit-collusion-b) valid?
4. wit-partition-vacuous registers a PASS on an empty comparison. Honest, or does the
   layer then read as "consistent/witnessed" when nothing was compared? Is putting the
   distinction only in the detail string enough?
5. wit-retention-horizon: the retained record names the SHARED genesis, which both fork
   branches contain, so consistency is trivially true. Is the cell measuring the
   retention/coverage clause, or is it a tautology dressed as a boundary?
6. snapshot-behind-witnessed-head: refusing a SHORTER presented history than a retained
   record — is that sound in general (a verifier auditing a deliberately old snapshot
   would trip it), or does it conflate recency with consistency? Check against 016's
   minimum-head-pin semantics and RFC 0011 R-7 (membership-at-snapshot, not real-time).
7. Ceremony order (SPEC section 2/3 vs verify_witness.py): any input where the
   first-failure order reports the wrong code; any registered code unreachable; the
   retained-order iteration over records as a determinism or attribution hazard when two
   records would each trigger a different code.
8. upstream016.py: are the digests enforced on every load path, with no sys.path or
   sys.modules window? Does using 016's build-path writer for fixtures undercut the claim
   that Layer CURRENCY is unchanged?
9. The claim ceiling vs the RFC 0011 amendment's dispositions: any residual blanket
   detection language, any "witnessing gives X" not tied to the clause a cell isolates,
   any independence claim slipped in where the study says it makes none.
10. harness/PINS.json wording vs what score.py actually enforces; the frozen cell-id set;
    the manifest anchor and its freshness assertion; the two-state pins test.
11. Any cell in MATRIX.json whose registered expectation you can argue is WRONG before a
    registered run — the central purpose of this round.

Also state, one line at the end, whether at the next round you are prepared to author a
reviewer holdout set (cells you register, never run before the freeze, committed verbatim
with attribution), per the 014/016 precedent. Do not author cells this round.

Output, exactly:
- Numbered findings R1-<n>, each: severity BLOCKER / MAJOR / MINOR, the file/section, a
  one-paragraph description of the failure mode, and a concrete fix.
- Then one line: `freezable as written`, `freezable after listed fixes`, or `DO NOT FREEZE`.
Findings only. Cite the file you read for every claim; if a cross-reference could not be
verified, say so rather than guessing.
```
