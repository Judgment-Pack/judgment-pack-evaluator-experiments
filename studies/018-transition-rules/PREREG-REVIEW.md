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
| R2-2 | **Accepted**, but this disposition was itself wrong when written — see the correction below. |
| R1-3, R1-8, R1-9, R1-12 | **Confirmed RESOLVED** by the reviewer. The endpoint set was additionally scanned for hidden duplication and found unique. |

A note on the apparatus catching itself: after the semantics change, two cells' registered
`retiredAtPosition` values were stale, and the run reported `R1 falsified` on
`transition:retiredAtPosition` — the structured-evidence channel added in round 1 doing
exactly what it was added for. The registrations were corrected to what the layer now
reports, and the reason is recorded here rather than silently amended.

Post-revision state: 21 cells (11 endpoints), 36 harness tests green, build pilot
`R1 holds`.

### Correction to R2-2 — a disposition that claimed a safeguard it never built

R2-2's disposition said the counts were "reconciled, with the counts derived from the matrix
by a harness test." **No such test existed.** It was written as if it did, and nothing
enforced the claim, so the document drifted again immediately: by the time the holdout
landed, `PREREGISTRATION.md` §1a said the locked stratum held **18 cells** against a
**21-cell** matrix, and §4 said `registeredAbsences` named **five** cells when it named
**six**. Both numbers are in the document that gets pinned at the freeze and governs the
attempt.

This is the same defect class the reviewer raised as R1-13 — a safeguard asserted in prose
rather than in code — reappearing in the disposition written to close a different finding.
It is recorded here rather than quietly fixed, because a review record whose dispositions
are themselves unverified is worth less than no record.

Fixed now, in this order: both counts corrected against the matrix, and
`test_preregistration_counts_are_derived_from_the_matrix` written to recompute every stated
count — total cells, positive and negative control gates, endpoints, the descriptive and
demonstration rows, and the registered-absence count in words — from `MATRIX.json`, plus a
check that the two holdout files describe the same cell set. The test was mutation-checked
against all three of the wrong numbers and fails on each.

### R2-H — the reviewer's holdout stratum, landed

The round-2 reviewer authored ten cells (h01–h10). They are committed **verbatim with
attribution** in [`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json); their
construction hooks land in `harness/build_fixtures.py` gated on a `HoldoutAttemptContext`
that only the scorer mints after all six freeze pins are non-null, and their structured
expectations are kept **separate** in
[`harness/MATRIX-HOLDOUT-EVIDENCE.json`](harness/MATRIX-HOLDOUT-EVIDENCE.json) so the
authored block stays byte-for-byte (the 017 round-3 R3-1 discipline). Nothing in the
stratum has been executed, here or anywhere: two new harness tests assert every registered
cell has a hook, that every hook and `construct_holdout` refuse outside a valid post-freeze
context, and that the gate refuses while **each** of the six pins is null in turn.

**A registered disagreement, deliberately left unresolved.** Reading the reviewer's ten
constructions, their `retiredAtPosition` expectations decode to a single consistent rule:
*the most recent departure of the committed binding in the full history, reported whenever
that binding is not supported at the snapshot* — h01's twice-reinstated binding is supported
at position 7 and registers `null`, while h05 (cited position 5, unsupported) and h08 (cited
position 2, unsupported) register `8` and `6`. This study's `rule/transition.py` publishes a
departure only **relative to a supported cited position**, so it is expected to report `null`
for h05 and h08 — and h03, also cited-unsupported, registers `null` and agrees.

Neither side was adjusted, and the reasoning is the disposition:

- **The layer was not changed to match.** The round-2 review raised no finding on this
  field — the differing semantics appears *only* inside the holdout's own notes. Fitting the
  implementation to the answers of cells that have never been run would destroy the only
  prospective content the study has. That is training on the test set, and the stratum would
  afterwards be worth nothing.
- **The expectations were not changed to match the layer either.** Rewriting a reviewer's
  registered values to whatever the maintainer's code happens to emit is the same error
  wearing the opposite sign, and it is the failure the separate evidence file exists to make
  impossible to commit quietly.

So both outcomes are named in advance. If the first execution reports `null` where the
reviewer registered `8` and `6`, the holdout is **divergent on the
`transition:retiredAtPosition` channel for h05 and h08** — a genuine finding that
`rule/SPEC.md` under-specifies what the evidence field means when the cited state is not
supported, reportable as such and not as a defect discovered late. If it instead matches,
the two semantics coincide on these cells and the field is better pinned than the SPEC
text alone establishes. Either way the outcome is reported separately and cannot move R1.

## Round 3

Verbatim: [`reviews/round-3/REVIEW.md`](reviews/round-3/REVIEW.md). Verdict: **not freezable**,
six blockers. The reviewer confirmed R1-1/R1-2/R2-1, R1-11, R1-3, R1-8, R1-9, R1-12 and the
R2-2 correction, and **rejected five dispositions** whose residuals were still live in bytes.

On R2-H the reviewer ruled that the maintainer "was right not to rewrite either side merely
to force agreement after seeing the holdout", and confirmed that **h05 and h08 were
intentional, not authoring slips**. R2-H was, however, **incomplete**, which is blocker 6.

### R2-H (amended) — a third divergence, also determined in advance

h03 registers `not-usable:not-usable-cited-state-not-supported`, but its committed tuple
carries a digest that is in the supported set at **no** position of the history, so the layer
necessarily returns `not-usable-never-supported` — the very distinction round 2's R2-1
disposition introduced. That is an **outcome** divergence, not merely an evidence-channel
one, and unlike h05/h08 it was not visible from the evidence map alone.

All three are now registered in advance, in `harness/MATRIX-HOLDOUT.json`'s envelope note,
in `harness/MATRIX-HOLDOUT-EVIDENCE.json`, and here:

| Cell | Registered by the reviewer | What this layer will report | Channel |
| --- | --- | --- | --- |
| h03 | `not-usable-cited-state-not-supported` | `not-usable-never-supported` | `transition` |
| h05 | `retiredAtPosition: 8` | `null` | `transition:retiredAtPosition` |
| h08 | `retiredAtPosition: 6` | `null` | `transition:retiredAtPosition` |

The reviewer's expectations stay **verbatim** — h03's included — and the layer stays
unchanged. Predicting a divergence is not the same as fitting to it: the prediction is
falsifiable, it is recorded before the stratum has ever run, and if any of the three does not
land as predicted then this reasoning about the layer was itself wrong, which is worth more
than a stratum quietly edited into agreement.

What this costs is stated plainly: three of ten holdout cells now carry an expected
divergence, so the stratum's prospective content is the **seven** cells whose outcome is
genuinely open, plus the correctness of these three predictions.

### Round-3 blockers — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted.** `rule/SPEC.md` §3.3 promised the deleted `not-usable-version-retired` and §3.5–3.6 described a single-departure algorithm the layer abandoned; both rewritten to what the code does. New **§3a** defines `citedPosition` and `retiredAtPosition` exactly, including that the latter is citation-relative and `null` when the cited state is unsupported. `_left_position`'s docstring claimed `position-window` is measured from it — false, and corrected; it is retained, unwired, precisely because it computes the reviewer's alternative reading. The `div-run-to-expiry` example named a cell that does not exist. |
| 2 | **Accepted.** "Belongs to the relying party" is gone from `PREREGISTRATION.md`, `rule/SPEC.md` and `rule/transition.py`; the README no longer claims to measure Unresolved #10 (it measures #11) and no longer concludes what a registry "would have to" do. `transition.py`'s "configuration rather than code paths" is withdrawn in the module itself, matching the SPEC. Historical review files untouched. |
| 3 | **Accepted.** R1 now names all four adjudicated channels including `transition:citedPosition` and `transition:retiredAtPosition`. The renderer published Study 017's witness triple — every row read `compared=None, attributed=None, unattributed=None` — and now publishes observed and registered values of this study's two fields with a divergence marker; the "Registered pairs" section, which this study never populates, is replaced by the identity groups it actually verifies. A regression asserts the rendered output. Two further 017 residues found while fixing it: a `sys.path` insert for a `witness/` directory that does not exist, and a scorer docstring claiming a collusion pair is structurally validated. Both removed. |
| 4 | **Accepted.** The locked builder derived its authority from a hard-coded literal; it now reads the registered label, and a test asserts the literal is absent. Pin enforcement derived *a* key from any non-empty label without ever comparing it to anything, so the pin described the fixtures rather than binding them; it now requires the derived public key to equal the `authorityPublicKey` in **every** retained trust configuration, under a mutation test. `checkpoint.py` is no longer called "BUILD PATH ONLY": the scorer loads it on both paths, and the note says so. |
| 5 | **Accepted, and this one was a real hole.** `_gated` wrapped only the `HOLDOUT_HOOKS` mapping, so `build_fixtures._holdout_h01(None)` would have constructed genuine registry bytes before the freeze — the gate was on the door, not on the room. `_require_context` now runs inside every raw constructor and inside both innermost primitives (`_authority`, `_holdout_cell`) before any key or payload exists. Direct-bypass tests cover all twelve routes, and a signature audit requires every holdout callable to take `context` first. |
| 6 | **Accepted.** See the amended R2-H above. |

## Round 4 — pending

Confirmation of the round-3 dispositions over stable bytes.
