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

## Round 2 — pending

Confirmation of the thirteen dispositions, plus the reviewer-authored holdout stratum.
