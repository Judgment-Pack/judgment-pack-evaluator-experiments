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

Verbatim: [`reviews/round-3/REVIEW-run-b.md`](reviews/round-3/REVIEW-run-b.md) — this is the
run these dispositions answer; see [`reviews/round-3/README.md`](reviews/round-3/README.md)
and [`REVIEW-run-a.md`](reviews/round-3/REVIEW-run-a.md) for the other run and why there are
two. Verdict: **not freezable**,
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

### A defect the mutation check found, that no review had

Round 3 asked whether the newly added tests fail when the property they name is broken.
Checking that against a scratch copy — rather than answering from memory — turned up a live
defect the reviews had not reached: **`_holdout_h03` passed `registry` where `context`
belongs**, a leftover from threading the context through the constructors for blocker 5.

It was invisible to everything. The stratum is never executed before the freeze, so no test
runs the hook; the direct-bypass test calls it with `None` and the gate raises
`HoldoutRefused` before the bad call is ever reached; and the static name audit written when
the cells landed checks that every called name *exists*, not that the call *binds*. At the
attempt it would have raised `TypeError`, recorded h03 as `harness-error`, and reported the
whole holdout **inconclusive — validity problem**: one reviewer cell lost, and with it the
h03 outcome prediction registered above, for a stray argument.

Fixed, and the gap closed properly: `test_holdout_call_sites_bind_statically` binds every
holdout call site against its callee's real signature via `inspect.Signature.bind` over the
AST, and additionally requires the context argument to be the name `context` rather than any
local that happens to sit in that position. It fails on the exact defect when reintroduced.

The lesson is recorded because it generalises: **a gate that raises early hides every error
behind it.** Defence in depth bought correctness at the door and cost observability inside
the room, and the only thing that surfaced it was deliberately breaking the safeguards to
see whether the tests noticed. Mutation-checked results for the other four new tests: the
freeze-pin gate, authority binding, rendered output and count derivation tests each fail
under a targeted mutation.

**Recorded deviation on bytes reviewed.** Round 3's reviews ran against the working tree
while the R2-2 count fixes were being committed, and round 4's ran while the `_holdout_h03`
fix above was being made. Neither is over a single frozen snapshot, and saying so is cheaper
than pretending otherwise. Round 4 states the clean HEAD it read (`71ebf14d`), and every
round-4 finding below was re-checked against the current bytes before disposition.

## Round 4

Verbatim: [`reviews/round-4/REVIEW.md`](reviews/round-4/REVIEW.md). Verdict: **not freezable**,
six blockers. Confirmed closed: the amended R2-H (blocker 6 of round 3), and the
implementations behind the formal-R1/renderer and authority-binding blockers. Everything
else came back partial — and one came back as never dispositioned at all.

### The round-3 record was not the review that was dispositioned

Round 4's first finding is a record-integrity failure, and it is the most serious thing in
this document.

Round 3 was launched twice. The first launch printed nothing and its output file was empty
when checked, so it was treated as failed and a second launch was started over the same bytes
with the same reviewer configuration. The first launch had not failed. It was still running,
and it later wrote its output to the same path — **overwriting the second launch's review
after that review had already been read and dispositioned**. The blocker table above answers
the second run; the file committed as the round-3 record was the first.

Round 4 caught it by reading the record against the dispositions: row 1 answers the committed
review's blocker *2*, and the committed review's blocker *1* — add a never-seen-version
control — appears nowhere. It was never dispositioned, and would have gone into the freeze
unaddressed.

Both reviews are now kept, at [`reviews/round-3/REVIEW-run-a.md`](reviews/round-3/REVIEW-run-a.md)
and [`reviews/round-3/REVIEW-run-b.md`](reviews/round-3/REVIEW-run-b.md), with the collision
explained in [`reviews/round-3/README.md`](reviews/round-3/README.md). Run B was recovered
verbatim from the session transcript, since the bytes on disk no longer held it. Neither is
treated as authoritative; both were addressed. Review output now goes to a run-specific path,
so two runs can no longer write the same file.

Worth stating rather than burying: two runs of the same reviewer over the same bytes produced
**different blocker sets**. That is a fact about the review instrument, not only about this
incident, and it argues against reading any single round as exhaustive.

### Round-4 blockers — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted — the omission above.** `neg-never-supported-version` is registered and built: version `9.9.9`, which the registry never bound at any digest, under `grandfather-on-cited-support` with a citation of position 2. Round 5 corrected the mechanism claimed for it: it does **not** take a different path through the pinned fold, which is given only the history and the series and returns a version-to-digest map — the key-miss versus digest-mismatch distinction happens afterwards in `_supported_at`. What makes it non-redundant is the inverse of the existing controls: its digest **is** in the supported set, bound to another version, so it fails any implementation treating membership as a digest question rather than a `(version, digest)` binding. It reports `not-usable-never-supported` with `citedPosition: 2, retiredAtPosition: null`, as registered. A unit vector covers the same tuple under all three rules. Counts updated: 22 cells, 5 negative controls. |
| 2 | **Accepted.** Three residual contradictions between SPEC and code, all real: the ceremony is now numbered from step **0** (the currency gate refuses before any configuration is parsed); `stop-at-retirement` no longer claims to consume the verdict "alone", since it folds history to choose between its two refusals; and `citedPosition` is defined by whether the layer *reaches* the citation step, with the duration-window case named explicitly — it refuses first and publishes no evidence however good the retained citation is. |
| 3 | **Accepted.** The explicit claims were fixed in round 3 while equivalent ones survived in the module title, the SPEC's configuration section, a matrix cell note, the README headline and R2's own summary sentence. All now say *stated* or *configured* rule. The only surviving mention of a relying party is the §4c limitation that disclaims exactly this. |
| 4 | **Accepted.** The regression checked substrings, so wrong values would have passed. It now parses every rendered row, reconciles role, expected, observed and both structured fields against `RESULTS.json`, requires the row count to cover every cell and layer, requires each identity group to render, and exercises both mismatch markers by rendering a fabricated divergent record — since the locked stratum is correctly all-concordant and cannot produce one. |
| 5 | **Accepted.** "Some mismatch appears" would have passed a scorer checking one fixture, so the test now requires the mutated label to flag **every** cell by id. Banning one literal spelling proved nothing about the builder reading the label, so a second test points `PINS_PATH` at a mutated registry, rebuilds, and asserts every fixture's `authorityPublicKey` follows the new label — and that an absent, empty or non-string label is refused rather than defaulted. |
| 6 | **Accepted.** The six pins are now asserted literally, so dropping one from `FREEZE_PINS` fails here instead of silently shrinking the test. A tripwire on the upstream loader proves refusal precedes any key derivation or byte, and that nothing is written under the working directory. The static call-site audit listed callees by hand and so skipped hook-to-hook calls — exactly the ones most likely to drift — and now covers every holdout callable. The count test derives the negative-control breakdown too, so editing "two never-bound-digest controls" no longer passes. |

## Round 5

Verbatim: [`reviews/round-5/REVIEW.md`](reviews/round-5/REVIEW.md), at clean HEAD `014de8e8`.
Verdict: **not freezable**. Blocker 1 substantively implemented; 2–6 partial. Every finding
accepted, and one of them corrects a claim rather than a defect.

### The new control was right for the wrong reason

Round 4's blocker 1 was closed with a mechanism that is **false**:
`neg-never-supported-version` was described — in the matrix note and in the disposition — as
taking "a different path through the pinned fold". It does not. `fold_supported` receives
only the history and the series and returns a version-to-digest map; the key-miss versus
digest-mismatch distinction happens afterwards, in this study's own `_supported_at`.

The reviewer also supplied the reason the cell *is* non-redundant, which is better than the
one claimed: version `9.9.9` carries `DIGEST_A`, a digest this registry **did** bind — to
`1.0.0`. So the cell is the inverse of the other two controls. Their digest is absent from
the supported set; this one's is present, under another version. It therefore fails any
implementation that treats membership as a digest question rather than a `(version, digest)`
binding — a defect class no other cell covers. Both statements of the mechanism are corrected.

This is worth recording as a pattern rather than a slip: the cell was correct, its outcome
was correct, its evidence was correct, and the *explanation attached to it* was wrong. A
registered artifact carries its rationale into the freeze, and a wrong rationale is a wrong
registration even when every observable value is right.

### Round-5 findings — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted.** See above. The matrix note and this record now state what the cell actually exercises, and explicitly deny the fold-path claim so it cannot be re-derived from the old wording. |
| 2 | **Accepted.** The module synopsis still defined `stop-at-retirement` by "once the version has left" and `position-window` by "the position at which the version left" — the single-departure model round 2 removed from the code and round 3 removed from the SPEC, surviving in the docstring a reader meets first. Rewritten to the exact `(version, digest)` fold, the never-supported split, and the first departure **after the citation**. SPEC §3a also gained the null case it was missing: a citation can be located and the fold then fail, returning `transition-unavailable` with **no** fields — so a located citation is necessary but not sufficient for a non-null `citedPosition`, and a null must never be read as "no citation was retained". |
| 3 | **Accepted.** The disposition claimed only §4c still mentioned a relying party; the governing SPEC's closing ceiling paragraph still said a transition rule "says what one relying party does". That is exactly the assertion §4c disclaims, in the document that gets pinned. Fixed. The record also still linked `reviews/round-3/REVIEW.md`, which no longer exists after the two runs were separated — now points at run B, with the README and run A alongside. |
| 4 | **Accepted, and the flaw was in how the test was constructed.** Expected evidence was matched as an unbound substring, so registered values could be swapped between fields; each field is now checked inside its own rendered clause, and a field with no registration must render none. Worse, the fabricated divergence broke the outcome **and** the evidence at once and the assertion asked only whether some victim row contained `≠` — so deleting either marker still passed. There are now two fabrications, one per marker, each asserting the marker appears in its own column and **not** in the other. Concordant rows are also asserted to carry no structured marker. |
| 5 | **Accepted, both halves.** "Every cell was flagged" was derived from ids appearing in error strings, which a scorer re-reading the first fixture while reporting the loop id would satisfy; a new test corrupts exactly one trust configuration in a copied tree and requires exactly that cell to be flagged. And checking only the emitted trust keys would pass a builder that advertised the label-derived authority while still **signing** with a hard-coded one — producing fixtures that cannot verify. The mutated-label rebuild now runs Layer CURRENCY over every rebuilt cell and requires a clean authority result. |
| 6 | **Accepted.** The tripwire omitted `_holdout_cell` itself. The call-site audit enforced context identity for three named functions, so `_holdout_h05` calling `_holdout_h04(None, …)` bound cleanly and stayed hidden behind the gate until the attempt — the rule is now derived from the **callee**: anything whose first parameter is `context` must receive the caller's `context` by name. Verified against the reviewer's exact mutation. The count test's "every count" claim did not cover the registered rule count; it now derives that from `transition.RULES` and requires each rule name in the prose. |

## Round 6

Verbatim: [`reviews/round-6/REVIEW.md`](reviews/round-6/REVIEW.md), at clean HEAD `94a4bef6`.
Verdict: **not freezable**. Round-5 finding 3 confirmed closed; 1, 2, 4, 5 and 6 partial.
All accepted.

### The pattern the last four rounds have found

Rounds 3, 4, 5 and 6 have each found that the previous round's dispositions were written as
complete while residuals were live — and round 6 named the mechanism precisely: the
dispositions **over-claim**. "Every rebuilt cell" skipped one. "Every holdout call site"
skipped dynamic dispatch. "Every count" covered the cell table only. Each was written after
fixing the specific thing the reviewer pointed at, and each generalised the fix in prose
beyond what the code did.

That is a failure mode worth naming in the record, because it is not carelessness about the
fix — it is carelessness about the *claim*, and the claim is what gets pinned. The response
this round was to make each claim true where that was possible, and to narrow it where it was
not: the tripwire test is now called
`test_holdout_refusal_precedes_any_upstream_load_or_write`.

**Round 7 falsified the rest of that sentence.** The docstring did not state exactly what
the test does not prove: it claimed no route writes before refusing, while the test only
looked for surviving files under `tmp_path` afterwards — blind to a write-then-delete or a
write anywhere else. Correcting an over-claim with another over-claim is the same defect,
and it is left visible here rather than edited away.

### Round-6 findings — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted.** The repudiated "different path through the pinned fold" survived in the builder comment and the unit test's docstring after being corrected in the matrix and this record — the correction was applied where the reviewer pointed and nowhere else. Both now carry the accurate mechanism and explicitly deny the old one. The cell's scope is also stated fully rather than by its most interesting property: it pins unknown-tuple classification as never-supported, the registered `citedPosition: 2, retiredAtPosition: null`, **and** that TRANSITION's prefix predicate compares the binding rather than the digest. It does **not** catch a digest-only defect confined to Layer CURRENCY at the final snapshot, where `DIGEST_A` has departed. |
| 2 | **Accepted.** The same "the version" shorthand the ceremony had shed for `stop-at-retirement` was still in the synopsis for `grandfather-on-cited-support`, and had been reintroduced into SPEC §3.3 by round 5's own rewrite. Both now say the exact `(version, digest)` binding, and both name the counterexample: a known version at the wrong digest. |
| 4 | **Accepted.** Three separate weaknesses: `startswith` let `citedPosition: 20 (registered 20)` satisfy a registered `2`; `dict(zip(...))` silently discarded any third clause; and both marker fabrications left `divergent`/`divergentLayers` at concordant values, so a renderer leaking a marker *conditional on the real divergence state* passed. Clause lists are now length-checked and compared for exact equality, and each fabrication carries the divergence state a genuine record of its kind would carry. |
| 5 | **Accepted.** The corruption test exercised two of 22 victims, leaving a scorer free to read those two and reuse the first fixture for the other twenty; it now corrupts **every** cell in turn. And the mutated-label rebuild skipped `neg-currency-unauthenticated` while the disposition claimed every rebuilt cell — it is now included, asserted to be exactly `snapshot-signature-invalid`, with the reason it cannot demonstrate signer-follows-label stated inline rather than by omission. |
| 6 | **Accepted, and this one was a live hole.** The tripwire never called the gated wrappers in `HOLDOUT_HOOKS` — the routes the scorer actually uses. The call-site audit missed `_gated` entirely, fired its identity check only when a *positional* argument existed (so `_holdout_h04(context=None, cited=5)` passed), and could not see dynamic `hook(context)` dispatch at all, which names no callee. All three are closed: wrappers exercised, keyword contexts checked, and a literal `None` banned outright anywhere inside holdout scope. Verified against both of the reviewer's exact bypasses. The count test's "every count" claim now covers both statements of the rule count and the companion-artifact count, each mutation-checked. |

## Round 7 — pending

Confirmation of the round-6 dispositions.

## Round 7

Verbatim: [`reviews/round-7/REVIEW.md`](reviews/round-7/REVIEW.md), at clean HEAD `a9fbd012`,
with `46 passed`, the manifest check green and the worktree clean under the registered
interpreter. Verdict: **not freezable**. Round-6 findings 2, 4 and 5 confirmed closed; 1 and
6 partial; and — the reason this round matters most — a **frozen-reader audit** that found
three statements which would mislead someone holding only the five pinned artifacts and the
results.

### The frozen-reader audit is the finding

Every previous round examined the apparatus. This one asked what the *frozen* files say to a
reader who cannot see the tests, the record, or the code — and three of them said something
untrue:

| Where | Claimed | Actually |
| --- | --- | --- |
| `MATRIX.json` note | `combined` is usable only when **both layers permit it** | `combined` is usable when TRANSITION permits and CURRENCY returned an **adjudicable** answer. Cells where currency *fails* compose to `usable` — that is the entire subject of the study, contradicted by its own matrix note |
| `PREREGISTRATION.md` §3 | CURRENCY reports `not-current-at-snapshot` for **every full-history cell** | `neg-currency-unauthenticated` is a full-history cell reporting `snapshot-signature-invalid` — the control exists precisely to show that |
| `MATRIX.json` cell note | `stop-at-retirement` reaches its answer **from the registry's verdict** | it also folds the retained history to choose between its two refusals, as the SPEC has said since round 3 |

The first is the sharpest: the matrix note asserted the opposite of the study's own result.
Nothing in the outcomes or the evaluator is affected — every registered expectation and every
observed value was already correct — but a reader restricted to the frozen artifacts would
have drawn the wrong conclusion from them, and those artifacts are the ones that become
immutable. All three are corrected, along with the same "both layers permit" wording in the
composing code's comment.

### Round-7 findings — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted.** The corrected mechanism reached the builder comment and the unit test but not `MATRIX.json`, which still claimed the cell defeats "any implementation that treats membership as a digest question" — and the honest limitation lived only in this record, which is not frozen. The matrix note now carries both the claim and its bound: the cell reaches TRANSITION's prefix predicate, and does **not** catch a digest-only defect confined to Layer CURRENCY at the final snapshot. |
| 6a | **Accepted.** The call-site audit still could not see dynamic dispatch: `hook(context, 5)` bound cleanly, since the literal-`None` ban does not catch a spurious *extra* argument. A dynamic call inside holdout scope must now pass exactly `context` and nothing else positionally. Verified against that mutation. |
| 6b | **Accepted.** "Every count" still omitted the `div-*` count, so raising "the four `div-*` cells" to five passed. Derived now, like the rest. |
| — | **Accepted.** The tripwire inferred "nothing was written" from surviving files, which a write-then-delete defeats. Both writers are now trapped directly, and the docstring says plainly that pure in-memory work touching neither the upstream nor a writer is undetected — with the argument for why no registry byte can be produced that way marked as an argument rather than folded into the test's name. |

**Self-reported, not found by the reviewer:** the same loose phrasing sits in R1-1's
disposition above, which says "the composed verdict requires both layers". It is left
standing as written — a historical disposition edited after the fact is worse than an
imprecise one — and corrected here: the composed verdict requires TRANSITION's permission and
an **adjudicable** CURRENCY answer, not CURRENCY's permission. The frozen artifacts, which are
what bind, now say so exactly.

The reviewer also recorded what does **not** block: the three registered holdout divergences,
the alternative `retiredAtPosition` reading, the backdating limit, the positional-window
limitation, the shared builder/evaluator lineage, and the non-digest-pinned dependency
contents. All are registered in the text and evaluable by a reader, which is the standard
this study is trying to meet.


## Round 8

Verbatim: [`reviews/round-8/REVIEW.md`](reviews/round-8/REVIEW.md), at clean HEAD `5eb1dbfa`,
`46 passed`, manifest green, worktree clean. Verdict: **not freezable**. Round-7 findings 1,
2, 4 and 5 confirmed closed; three residuals; and **ten independent frozen-reader findings**
from an audit run without reference to round 7's list. All accepted.

### The primary hypothesis contradicted its own scorer

Finding 1 is the most serious defect any round has produced, and it sat in the governing
sentence of the study. R1 says divergence falsifies "including a refusal on a
`registeredUndetected` cell". The only such cell, `bnd-backdated-citation`, is
**descriptive** — reclassified in round 1 precisely because it is byte-identical to an
endpoint — and `decide()` counted endpoints alone. The reviewer constructed the synthetic
case: that row alone divergent returns **`R1 holds`**, contradicting the preregistration that
governs the run.

It was arguably harmless in practice, since the cell is byte-identical to an endpoint that
would diverge with it, and identity-group divergence is a validity failure besides. That is
not a defence. **The registered text is the commitment**, so `decide()` now falsifies on a
divergent `registeredUndetected` cell whatever its role, with a regression asserting both
directions — the rule widened by exactly one class and not generally. Narrowing R1's wording
instead would have been the easier fix and the wrong one: it would have quietly reduced what
the study promises after the promise was made.

### The registered label did not require the registered stratum

Finding 6: `--include-holdout` is optional, so a fully pinned run could be labelled
`REGISTERED` with `holdout: null` — while `harness/MATRIX-HOLDOUT.json` states that the
stratum's first execution **is** the registered primary attempt. Nothing enforced the
connection. `REGISTERED` now requires every freeze pin *and* the stratum; a pinned run without
it is a `PILOT` and says so. This also means the harness's own determinism tests, which pass
no such flag, remain pilots after the freeze — as they should be.

### Round-8 findings — disposition

| # | Disposition |
| --- | --- |
| 1 | **Accepted**; see above. Code brought to the registered claim, not the reverse. |
| 2 | **Accepted.** Round 7's correction to the composition note over-corrected: "never a membership answer" reads as *combined never refuses one*, when combined is `not-usable` whenever TRANSITION refuses. The note now names the **composition gate** as its subject and states plainly that the gate can only take `usable` away, never grant it. |
| 3 | **Accepted.** The SPEC said TRANSITION "never recomputes membership" while it folds prefix membership constantly — it never recomputes the *verdict*, which is a different claim, and the distinction is now drawn. The fold was said to answer two questions; it answers three, the third being the first post-citation departure. R1's input tuple omitted the retained history entirely, though every refusal below `usable` is chosen by the fold. |
| 4 | **Accepted.** "Each gate refuses before the next input is read" is true of the layer and false of the harness: `run_verify` parses the snapshot and reads citation and configuration before calling TRANSITION at all, so a non-adjudicable cell has had its bytes parsed outside Layer CURRENCY's resource limits by the time the refusal returns. Stated as a property of the layer, with the harness's actual behaviour named. |
| 5 | **Accepted.** "Cells differ in the rule and the cited head rather than in the world" is true of the endpoints and false of the matrix: the control gates vary snapshot prefix and authenticity, the commitment tuple, citation presence and series — which is what they are for. Scoped to the endpoints. |
| 6 | **Accepted**; see above. |
| 7 | **Accepted.** The `not-usable-window-elapsed` row said "since the version left the set", losing both qualifiers that matter: the exact binding, and *first departure after the cited position* rather than most recent. That is precisely the distinction the three registered holdout divergences turn on, so the vocabulary table was undercutting the study's own registered disagreement. |
| 8 | **Accepted.** The preregistration called `bnd-mint-time-refusal` a registered producer policy; its own matrix note says no producer stage or accepted-head policy exists anywhere in the apparatus. It is a **counterfactual demonstration** conditional on a policy this study does not supply, and now says so. |
| 9 | **Accepted, without touching the cells.** Several reviewer-authored notes explain their expected position by the most-recent-departure rule, and h04's names `_left_position` — a helper that exists and is not on the decide path. Where they agree with the layer (h04, h06, h07 all at position 8) they agree by coincidence, because the two readings converge in those histories. The cells are verbatim and stay verbatim; the envelope note now says exactly this and points at SPEC §3a as governing. |
| 10 | **Accepted, all three.** "One adjudication" and "count toward nothing" understated the aliases, which are separately executed, included in 22/22, able to invalidate the pipeline, and — post-finding-1 — able to falsify R1. The decision rule omitted `R1 holds` and claimed "every terminal path" when the guarantee begins at the attempt marker. And dependency distribution roots and origins are checked **live**, not registered or pinned, so a reader cannot reconstruct them from the frozen files; the preregistration implied otherwise. |
| 6a/6b/tripwire residuals | **Accepted.** `hook(context, spurious=5)` passed every audit and would have failed only at the attempt as `harness-error` — dynamic calls now admit no keywords either. "Every count" still omitted the strata count. The tripwire claimed "any write" while trapping two named writers; it now names them and says a direct `Path.write_bytes` would not be detected. |


## Round 9

Verbatim: [`reviews/round-9/REVIEW.md`](reviews/round-9/REVIEW.md), at clean HEAD `e7fbea2e`,
`48 passed`, every manifest green, worktree clean, no holdout cell executed. Verdict: **not
freezable** — one blocker, two majors, and eight round-8 items rejected as incompletely
closed. All accepted.

### The composition gate did nothing at all

`run_verify` computed `usable if transition is usable AND currency is adjudicable else
<the transition outcome>`. In the one case the gate exists for — a rule permitting over a
currency verdict that is *not* adjudicable — the transition outcome **is** `usable`, so the
`else` handed back exactly the value the gate was written to withhold. It was algebraically
a no-op, and had been since round 1's R1-1, whose disposition claims it as the fix.

The apparatus was never wrong: `layer_transition` refuses a non-adjudicable currency verdict
itself, so the combination can't arise. That is precisely why no test caught it — **every
test drove composition through the layer, which can never produce the input that exposes the
defect.** A second line of defence that cannot be reached by the tests is indistinguishable
from no second line at all, and the frozen matrix note claimed it as an "extra condition".

`compose()` is now a named function that refuses on its own authority, and a regression calls
it directly with combinations the layer cannot emit — the isolation is the point. On every
registered cell it returns exactly what it returned before, so no expectation moves; what
changes is that the registered claim is true independently of the layer. Verified: the test
fails against the original expression.

### Round-9 findings — disposition

| # | Disposition |
| --- | --- |
| Blocker 1 | **Accepted**; see above. |
| Major 2 | **Accepted.** `RESULTS.json` carried `"pipelineInvalid": false` unconditionally on the success path, so a run whose verdict is `R1 inconclusive - pipeline-invalid` published a flag saying it was not. Derived from the verdict now. |
| Major 3 | **Accepted.** The widened audit still could not see `HOLDOUT_HOOKS[cell_id](...)`, because a subscript is not an `ast.Name` — the same defect one level up from round 8's. Any callee that is neither a known module function nor a builtin is now treated as a dynamic dispatch, and `*sequence`/`**mapping` expansions are refused outright since they hide arguments from the audit. Verified against both. |
| Minor 4 | **Accepted.** `make_manifest`'s docstring claimed coverage of a `registry/` tree, upstream records and two vendored pack fixtures — none of which exist in this study; the wording was inherited from Study 016. `build_payloads` claimed to build "every registered cell" when the holdout is built by `construct_holdout` inside the attempt. |
| R8-1 residual | **Accepted.** Widening `decide()` made `endpointDivergences = len(causes)` wrong: causes can now include the descriptive registered-undetected row. Counted by role, with a separate `registeredUndetectedDivergences`. |
| R8-3 residual | **Accepted.** "Every refusal below `usable` is chosen by the fold" is false — currency, configuration, duration and citation refusals precede it. And the fold's third question is asked for `grandfather-on-cited-support` too, which publishes `retiredAtPosition` without depending on it. |
| R8-6 residual | **Accepted.** The behaviour was closed but `PINS.json`'s `registeredLabelRule` and the scorer's own module docstring still stated only the pin requirement — the two places a reader looks for the label rule. |
| R8-8 residual | **Accepted.** "Producer policy" survived in `README.md` and a builder comment after being corrected in the preregistration. Same fix-where-pointed-at pattern as rounds 6 and 7. |
| R8-10 residual | **Accepted.** "Counted toward nothing" and "every terminal path" survived in the preregistration and one matrix cell. |
| R8-6a residual | **Accepted**; see Major 3. |
| Tripwire residual | **Accepted.** The docstring was honestly scoped but the test's **name** still said "any write". Renamed to `test_holdout_refusal_precedes_the_upstream_loader_and_this_modules_writers` — long, and exactly what it proves. |

The reviewer confirmed closed: the `decide()` precedence (pipeline-invalid → control gates →
endpoints and registered-undetected), the absence of any successful path to `REGISTERED`
without an executed holdout, the layer-versus-harness ordering scope, the endpoint-scoped
scenario, the window-elapsed definition, the holdout envelope, and the strata count.


## Round 10

Verbatim: [`reviews/round-10/REVIEW.md`](reviews/round-10/REVIEW.md), at clean HEAD
`9258bf91`, worktree clean, no holdout cell executed. The reviewer states it could not rerun
the pinned suite under its read-only environment and therefore claims no fresh test count —
recorded because a review that says what it did *not* verify is worth more than one that
implies it verified everything.

Verdict: **not freezable**, three surgical blockers — and, asked directly, a judgement on
stopping. All accepted.

### The same shape again, twice

Round 9's blocker was a safeguard that could not fail because something upstream guaranteed
the property. Round 10 was asked to hunt that shape and found two more:

- **The composed gate's fourth quadrant.** `compose(non-adjudicable, refusal)` returns
  `unavailable`, but the frozen note said a TRANSITION refusal survives "adjudicable currency
  or not". Both the test and the note skipped exactly the quadrant Layer TRANSITION makes
  unreachable. The note now states what `compose` does — an unauthenticated registry answer
  leaves no basis for a reasoned refusal either, so the composed verdict withholds the reason
  along with the permission — and the test covers all four quadrants.
- **The fold-failure contract.** `rule/SPEC.md` promises `transition-unavailable` on a history
  that will not fold. It was false standalone: `_ever_supported` stopped at the first supported
  prefix, so a later failure went unseen, and `_departure_after` returned `None` for both "no
  departure" and "could not read the history" — so a layer that had failed to read the history
  could answer `usable`. Composed, Layer CURRENCY folds everything first and refuses, which is
  why nothing observable was ever wrong. Fixed in code rather than in the SPEC: every prefix is
  folded, and `FOLD_FAILED` is a distinct sentinel. A regression drives the layer with a fold
  that fails partway and **no currency layer at all**.

### Round-10 findings — disposition

| # | Disposition |
| --- | --- |
| Blocker 1 | **Accepted**; see above. |
| Blocker 2 | **Accepted.** The audit skipped `ast.Attribute` callees wholesale, so `registry.build_registry(..., spurious=5)` bound cleanly and would have surfaced only at the attempt as `harness-error` on a reviewer cell. Calls into the pinned upstream's API are now bound against its real signatures, and `hook.__call__(...)` is treated as dynamic dispatch. Verified against both. The docstring's "every holdout call site" is replaced by what the audit actually resolves, with the reason stdlib calls are out of scope: they fail loudly in every pre-freeze run, which is not the hazard. |
| Blocker 3 | **Accepted**; see above. |
| R9 Major 2, R8-1 | **Closed in code, regressions noted as absent.** The reviewer flags that neither the `pipelineInvalid` serialization nor the endpoint/registered-undetected split has an isolating test. Recorded rather than papered over: both are correct and both are currently proved only by the aggregate suite. |

### On stopping

Asked whether further rounds would fix or churn, the reviewer's answer is on the record:
the three blockers are "surgical and isolation-testable", while "exhaustively chasing every
redundant guard or AST spelling would be churn" — and, after these corrections, it would
"stop broad review rather than begin another open-ended sabotage audit".

It also answered the question that matters most for a freeze: **no remaining defect changes
any of the 22 locked outcomes, the registered evidence, or what the primary attempt reports.**
The holdout still carries exactly the three preregistered divergences. Ten rounds have found
no registered-outcome error since round 2.

The maintainer's position is the same. The remaining known-imperfect items are named here
rather than fixed: three deletion-undetectable safeguards (`_gated`, the `frozen` conjunct in
the label predicate, the output-containment guard), each redundant with a check that is
tested, and two correct behaviours proved only in aggregate. They are recorded so a reader can
weigh them, which is the standard this study has been held to throughout.

## Round 11 — confirmation only

The next round confirms these three corrections and nothing else. If it is clean, the study
freezes.
