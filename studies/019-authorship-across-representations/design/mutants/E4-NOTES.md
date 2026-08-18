# E4 pilot notes (2026-08-15) — NON-CITABLE

> **SUPERSEDED 2026-08-18 (round-1 R1-2, R1-18). Read this file as a record of what was
> believed on 2026-08-15, not as a current reading.** Three of its claims are now measured
> to be wrong, and one of its recommendations must not be adopted:
>
> * **"the prose-correct expectation (review) is exactly what no JPS pack can produce"** —
>   false. A pack in the same fragment produces it; the arm-A reference was repaired and now
>   answers `review` on all 72 cells (`reference/refA/PACK-CHANGE-001.md`).
> * **The proposed design amendment — "E4's identity control and kill evaluation exclude any
>   authored case whose inputs fall in the registered X1 class" — is WITHDRAWN.** X1 is
>   retired; the registered exclusion set is empty; there is nothing to filter, and filtering
>   would have been an arm-shaped patch over a reference defect.
> * **The identity-control anomaly is resolved at its cause.** The same five arm-A suites,
>   byte-unchanged, now pass the identity control **5/5** against the repaired reference, and
>   refA/refB disagree on **0 of the 135** authored input points (was 3).
> * **The pilot read below (A 0.92/0.90 vs B/C 0.98) is stale on both counts**: it was
>   computed off-protocol and against a mutant corpus that no longer exists. Current, from
>   `E4-PILOT-v2.json`: mean paired kill **A 0.888, B 0.902, C 0.855**; high-kill fractions
>   at per-language cuts **A 1/5, B 0/5, C 0/5**. **"the direction is B/C above A" does not
>   reproduce.**
> * The adequacy work-list section is likewise pre-repair: the corpus is now 183 JPS / 184
>   Rego, the gate is **open** (37 + 34 undispositioned), and the engine-supplied-kill count
>   is **27**, measured over the whole domain rather than over gold witnesses (R1-11).

## The identity-control anomaly, and what it actually was

All five arm-A pilot suites failed the identity control as registered (suite must pass the
unmutated reference), on 8 case failures across exactly 3 distinct input points. The scorer
triangulated those points against refA, refB, and the clean-room oracle: refA vs refB
disagree on exactly 3 of the 135 authored input points; the oracle backs refB on all 3 and
refA on none. Every one is a new-vendor case with an unreadable numeric in the O1-suspended
region — **the registered X1 inexpressibility class**. The pilot authors' matrices probed
inputs the gold grid deliberately excludes, and there the prose-correct expectation
(review) is exactly what no JPS pack can produce. The authors were right; the reference is
as right as the fragment allows; the identity control as registered turns a registered
fragment boundary into a void of the entire arm.

**Design amendment for the preregistration (to ratify in review):** E4's identity control
and kill evaluation exclude any authored case whose inputs fall in the registered X1 class
(mechanically detectable per case); the per-run excluded-case count is a published
quantity. The two references' equivalence must be checked off-gold before freeze, with
divergence points required to coincide with the registered exclusion classes.

## The E4 pilot read (with X1-region case failures set aside — labelled off-protocol in
E4-PILOT.json, becomes the protocol under the amendment above)

- Arm A: mean kill 0.92 over adequate own-language mutants (range 0.84–1.00); paired 0.90.
- Arm B: mean kill 0.98 (identity 5/5 clean); paired 0.98.
- Arm C: mean kill 0.98 (identity 5/5 clean); paired 0.97.

**E4 discriminates, and in this pilot the direction is B/C above A.** The earlier surface
read (35–49 authored rows vs 1–4 test rules) was misleading: the Rego test rules are
table-driven and carry many assertions. Small N; non-citable; but the endpoint has
headroom and variance, which is what the pivot needed.

## Adequacy work list (pre-freeze)

Gold kills 98/145 JPS and 124/184 Rego mutants. The empty-witness remainder (47 + 60) is
the registered work list: killing rows where reachable, registered drops where provably
unkillable (e.g. Kleene-monotone onUnknown flips on rules that are never unknown; both
manifests carry the analysis). 35 JPS mutants are killed only via the engine's structural
conflict detection (unresolved{conflict} — a fifth reason token reachable only under
mutation); they are listed in refA/REGISTRY.json so kill rates can be reported with and
without engine-supplied kills.
