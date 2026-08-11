# Pre-freeze review record — Study 018

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here.

## Round 1 — 2026-08-11

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
sandbox. Verdict: **DO NOT FREEZE** (3 BLOCKER, 6 MAJOR, 4 MINOR). Prompt and findings
verbatim in [`reviews/round-1/`](reviews/round-1/). The reviewer is prepared to author the
holdout stratum next round.

All thirteen findings **accepted**. Two blockers are correctness defects in the evaluator,
not wording — the kind a draft's own author does not find because the matrix was built
around the case that works.

| # | Sev | Disposition |
| --- | --- | --- |
| R1-1 | BLOCKER | **Accepted.** The claimed layer separation was false: the transition layer ran even when Layer CURRENCY had *rejected* the snapshot, `stop-at-retirement` mapped every non-`pass` outcome — including `unavailable` and signature or chain failures — to "version retired", and `combined` was the transition result alone. A snapshot with an invalid attestation could therefore compose to `usable`. Now a rule is evaluated **only** over an authenticated membership answer (`pass` or exactly `fail:not-current-at-snapshot`); every other currency outcome is `transition-unavailable`; the composed verdict requires both layers; and `neg-currency-unauthenticated` is a standing control with unit vectors for five rejected outcomes. |
| R1-2 | BLOCKER | **Accepted.** `_fold_positions` was a hand-rolled lifecycle tracker and was **not** equivalent to the pinned upstream: it kept one interval, overwrote the entry on reinstatement, and did not check the digest, so a correct `2.0.0/digest-B` cited at position 2 was refused after reinstatement while a never-bound digest cited at position 5 became `usable`. The matrix hid it by targeting a version that is never reinstated. Membership at every cited prefix is now computed by **the upstream's own `fold_supported`** over that prefix — the semantics are the upstream's by construction — with `_left_position` defined over the same fold and multi-cycle behaviour (the most recent departure) stated. A regression asserts both previously-wrong cases. |
| R1-3 | BLOCKER | **Accepted.** The reviewer-holdout path was copied from Study 017 and still demanded `comparisonPerformed`/`validSightings`/`unattributedSightings` and indexed `outcome["witness"]`, which this study never produces — so any transition-shaped evidence map would have failed schema and a witness-shaped one would have hit `KeyError`. Retargeted to nullable `citedPosition`/`retiredAtPosition` with the same exact-field validation, before any cells are authored. |
| R1-4 | MAJOR | **Accepted.** The rule was not literal `run-to-expiry`: the inputs carry neither creation ordering nor expiry data, and the branch only asked whether an author-selected citation fell inside a support interval. Renamed **`grandfather-on-cited-support`** throughout, and its permissive result narrowed to "this rule does not block reliance on that ground", explicitly establishing nothing about when the artifact was created. |
| R1-5 | MAJOR | **Accepted.** `not-usable-created-after-retirement` asserted a creation-time fact the evidence cannot establish, and the catch-all also emitted it for pre-add and wrong-digest citations. Renamed **`not-usable-cited-state-not-supported`**, which is what the fold actually decides. |
| R1-6 | MAJOR | **Accepted.** The study had reintroduced governance conclusions RFC 0011's round-5 review removed — "belongs to the relying party", "picking is not its job", and a claim to measure Unresolved #10. Narrowed to the measurable statement: **membership alone does not determine reliance**, with source, ownership, placement and evaluation left open, and the result described as able to inform but not answer #10. |
| R1-7 | MAJOR | **Accepted.** A `position-window` carrying both window forms silently used the position count and bypassed the duration boundary, and the other rules accepted and ignored windows. Now exactly one form is required for `position-window` and none for the others, with rejection vectors. The "configuration, not code paths" claim is withdrawn as written: rule *selection* is configured, while the vocabulary and semantics are code requiring a registered patch. |
| R1-8 | MINOR | **Accepted.** `bnd-backdated-citation` is byte-identical to the honest cell, so counting both as endpoints reported one adjudication twice. It is now **descriptive**, excluded from R1 credit and from the endpoint count, with the identity itself retained as the finding. |
| R1-9 | MAJOR | **Accepted.** A second, *unregistered* duplicate: `bnd-mint-time-refusal` was byte-identical to `cite-absent-stop-unaffected` while counted as another endpoint, and no producer stage, accepted-head policy or freshness rule exists to make the mint-time reading anything but prose. Registered as an identity group and reclassified **demonstration**, published and never counted. |
| R1-10 | MAJOR | **Accepted.** R1's wording named only the two layer outcomes while `decide()` also let a structured-evidence divergence falsify it, and the published matrix still checked for a `"witness"` layer so every rule-evidence cell rendered `—`. R1 now includes the structured channels explicitly; the renderer emits `citedPosition`/`retiredAt`; the stale "Study 017" title is corrected. |
| R1-11 | MINOR | **Accepted.** "Four different usability answers" overstated three exact outcomes and two binary answers, and two of the four cells are the same rule under different parameters. Restated as "four configured evaluations yielding three exact outcomes — two permits and two refusals". |
| R1-12 | MINOR | **Accepted.** The reviewer verified the central invariant holds in the fixture bytes, and found the *test* omitted `citation.json` from the comparison. The test now asserts the exact difference set is `{ruleconfig.json}` across all cell files, and `div-stop-at-retirement` retains the citation its siblings carry even though its rule never reads it. |
| R1-13 | MINOR | **Accepted in part, and the residue recorded.** `authoritySeedLabel` was decorative; the builder now derives from the registered label. The reviewer also noted the scorer executes `checkpoint.py` via `load(build=True)` despite PINS calling it build-path-only — the claim is corrected rather than the behaviour, since the scorer legitimately needs the writer to recompute authority pins. |

Post-revision state: 19 cells (11 endpoints, matrixVersion 2), 34 harness tests green, build
pilot `R1 holds`.

## Round 2 — 2026-08-11

Same reviewer. 3 RESOLVED, 9 PARTIALLY RESOLVED, 1 NOT RESOLVED, one new MAJOR and one new
MINOR — plus a 10-cell holdout set authored. Prompt and findings verbatim in
[`reviews/round-2/`](reviews/round-2/). All **accepted**.

The round's substance is one finding wearing several numbers: **the rule branches still
contradicted the fold they had been made to call.** Round 1 replaced the hand-rolled
lifecycle tracker with the pinned upstream's `fold_supported`, but the branches around it
still reasoned from a single departure position, so a never-bound digest reached `usable`
under `position-window` (never-entered read as still-supported), a reinstated binding was
refused at a position the fold calls supported, and every non-membership — including a
wrong digest and an unknown version — was reported as a *retirement* Study 016 never
establishes (R2-1).

Every branch now decides from the fold's own answers over prefixes:

| # | Disposition |
| --- | --- |
| R1-1 / R1-2 residuals, R2-1 | **Accepted.** New codes `not-usable-not-in-supported-set` (departed) and `not-usable-never-supported` (never bound anywhere in the history) replace the single retirement code; `position-window` measures from the first departure **after** the cited position, so reinstatement is handled by the fold rather than by arithmetic; and two never-bound-digest control gates are registered. Verified: never-bound is `never-supported` under all three rules, the reinstated binding is `usable` at position 5, and the window case reports its true departure at position 4. |
| R1-4, R1-5 residuals | **Accepted.** The stale `div-run-to-expiry` usage example is gone and the SPEC now defines each code by what the fold establishes rather than by an at/after-departure condition. |
| R1-6 residual | **Accepted.** The ownership, placement and "picking is not its job" conclusions are removed from the remaining documents, and the claim to measure Unresolved #10 is narrowed to informing it. |
| R1-7 residual | **Accepted.** The "configuration, not code paths" claim is withdrawn in the SPEC: selection is configured, semantics and vocabulary are code requiring a registered patch. |
| R1-10 residual | **Accepted.** R1's wording now names the structured channels `decide()` actually counts, and the renderer publishes `citedPosition`/`retiredAt` instead of stale witness triples. |
| R1-11 residual | **Accepted.** The README headline now matches the matrix: four configured evaluations, three exact outcomes. |
| R1-13 (NOT RESOLVED) | **Accepted.** The builder derives the authority from the registered label, and the PINS text no longer claims the writer is off the scoring path — the scorer legitimately loads it to recompute authority pins, so the claim was corrected rather than the behaviour. |
| R2-2 | **Accepted.** The preregistration's cell and role counts were stale against the matrix; reconciled, with the counts derived from the matrix by a harness test. |
| R1-3, R1-8, R1-9, R1-12 | **Confirmed RESOLVED** by the reviewer. The endpoint set was additionally scanned for hidden duplication and found unique. |

A note on the apparatus catching itself: after the semantics change, two cells' registered
`retiredAtPosition` values were stale, and the run reported `R1 falsified` on
`transition:retiredAtPosition` — the structured-evidence channel added in round 1 doing
exactly what it was added for. The registrations were corrected to what the layer now
reports, and the reason is recorded here rather than silently amended.

Post-revision state: 21 cells (11 endpoints), 36 harness tests green, build pilot
`R1 holds`. The reviewer's 10 cells are **not yet landed** — that is the next step, together
with their construction hooks and structured-expectation map.

## Round 3 — pending

Confirmation of the round-2 dispositions, and of the holdout landing once it is made.
