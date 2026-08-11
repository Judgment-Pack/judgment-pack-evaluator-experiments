# Pre-freeze review record — Study 017

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here.

## Round 1 — 2026-08-11

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
sandbox. Verdict: **DO NOT FREEZE** (4 BLOCKER, 6 MAJOR, 5 MINOR). Prompt and findings
verbatim in [`reviews/round-1/`](reviews/round-1/). The reviewer states it is prepared to
author the holdout stratum at the next round.

All fifteen findings **accepted**. R1-4 is the round's centre: the reviewer falsified the
draft's central safety argument with a construction the maintainer then reproduced before
accepting it, and the fix changed the study's shape rather than its wording.

| # | Sev | Disposition |
| --- | --- | --- |
| R1-1 | BLOCKER | **Accepted.** A pinned `.py` digest does not describe the bytes that ran if cached bytecode is loaded instead. The pinned upstream is now compiled from the exact source bytes hashed at load (never through ordinary import machinery), and the scorer refuses when the cache a plain import *would* accept — exactly `importlib.util.cache_from_source(...)`, so another tag's rewritten copy is out of scope — unmarshals to code differing from `compile()` of its source. Mere existence is not the hazard and is not treated as one. |
| R1-2 | BLOCKER | **Accepted.** `PINS.json` claimed `cryptography` and `rfc8785` were "pinned transitively by the 016 apparatus"; this study consumes no lockfile of 016's, so the claim was false. Withdrawn, and replaced by a registered `dependencies.versions` map the scorer enforces by name, version and origin-outside-the-studies-tree before adjudication. |
| R1-3 | BLOCKER | **Accepted.** The attempt stamped one registry's bytes while every upstream check re-read the live file, so the trust inputs could differ from what the attempt records. `upstream016.bind_pins()` now freezes the mapping extracted from the stamped bytes for the process, and the loader never re-reads; binding a different mapping refuses. |
| R1-4 | BLOCKER | **Accepted — and reproduced before accepting.** The draft routed records by their unauthenticated `witnessKeyId` label, and D-3's safety argument ("the label can only cause refusal, never acceptance") was simply wrong: relabelling the honest conflicting record in `wit-one-honest` with a well-formed unpinned id turned `fail:snapshot-conflicts-with-witnessed-head` into `pass` while the colluding record still satisfied the floor. Confirmed locally on the committed fixtures. Attribution is now **by signature verification against every pinned key**; the label is descriptive and routes nothing; the reviewer's construction is kept as the standing control `neg-relabel-attack`. The residue this exposes — whoever controls delivery can still omit, corrupt, or re-sign a record — is registered rather than hidden, as the new `S-delivery-control` family, with `requiredWitnesses` as the arm that bounds it. |
| R1-5 | MAJOR | **Accepted.** The study does not replay Study 016's split-view cells (different series, no receipt layers, both branches add rather than retire) and said so nowhere. It now says the same *threat class*, disclaims replication explicitly, and makes the "one attributed record is the difference" comparison against its own internal control `wit-zero-sightings-vacuous`. |
| R1-6 | MAJOR | **Accepted.** The collusion check verified a signature, equal position and unequal heads — not series equality, not that the key was pinned in each configuration, not that it counted toward each floor, not that each head matched its own presented view — and `decide()` ignored the result entirely, so `validated: false` could coexist with `R1 holds`. All five invariants are now enforced, attribution inside the check is by verification like the layer's, and a pair that does not validate makes the attempt **pipeline-invalid**. |
| R1-7 | MAJOR | **Accepted.** "Independence measured as a diff" contradicted the study's own non-claim, and `wit-one-honest` changes both the pinned key set and the delivered evidence. Everywhere: the cells *illustrate why a non-collusion clause may be required*; the diff is "one additional pinned conflicting record reaching the comparator"; and a colluding witness satisfies every **implemented** clause except non-collusion, which nothing here implements. |
| R1-8 | MAJOR | **Accepted.** An empty or unattributable record cannot distinguish partition from non-production, withholding, discovery failure, or retention loss, and the "retention horizon" cell only compared a genesis both branches contain. Cells renamed for what they represent — `wit-zero-sightings-vacuous`/`-enforced`, `wit-prefix-coverage` — R2 restated in those terms, and §4c now says plainly that no result here may be read as measuring those causes. |
| R1-9 | MAJOR | **Accepted.** A pass after zero comparisons was machine-indistinguishable from a sighting-backed pass, with the difference only in unregistered free text that the published matrix dropped. The layer now returns registered structured fields — `comparisonPerformed`, `validSightings`, `unattributedSightings` — which the scorer records per cell and prints in the detection matrix. |
| R1-10 | MAJOR | **Accepted.** `snapshot-behind-witnessed-head` promoted every record to prior-acceptance state, though a sighting carries no proof its history extends the presented one, and Study 016 refuses the analogous case only under an explicitly provisioned `minimumHeadPin`. Recency is now the configured `recencyPolicy`, and both arms are registered over the same bytes: `wit-recency-refused` and `wit-historical-audit` — which is also the historical-audit control the finding asked for. |
| R1-11 | MINOR | **Accepted.** The unsigned retained order decided the code when two records would fire different ones. The layer now examines every attributed sighting and applies a registered precedence (conflict outranks behind), with a reversed-order test asserting identity. |
| R1-12 | MINOR | **Accepted.** Non-bytes inputs and a scalar `judgment` raised outside the vocabulary. All conversions are type-checked and exception-bounded; a vector covers each shape and additionally asserts that a malformed input never silently passes. |
| R1-13 | MINOR | **Accepted.** The scorer derived keys from hard-coded constants, so changing every registered `*SeedLabel` left enforcement clean. It now derives from the **registered** labels and additionally requires them to equal the builder's constants. |
| R1-14 | MINOR | **Accepted.** `load(build=False)` preflighted only one reserved name. Every reserved upstream name is now preflighted before any module executes. |
| R1-15 | MINOR | **Accepted.** "An exchanged accepted head IS a sighting", and the claim that one apparatus models witnessing and gossip alike, overstated a schema resemblance as mechanism equivalence. Narrowed to: the schema *could* encode an exchanged head under a separately specified authentication, role, acceptance and delivery contract this study does not define. |

Post-revision state: 18 cells (matrixVersion 2), 39 harness tests green, build pilot 02
(`pilots/2026-08-11-build-pilot-02`, non-citable) adjudicates 18/18 with all control gates
green, zero endpoint divergence, the collusion pair structurally validated, and the seven
registered-undetected cells confirmed undetected.

## Round 2 — 2026-08-11

Same reviewer. Verdict: **freezable after listed fixes** — 5 RESOLVED, 9 PARTIALLY
RESOLVED (each with a precise residual), 1 new **BLOCKER** and 1 new MINOR — plus the
reviewer-authored **9-cell holdout set**, landed verbatim with attribution. Prompt and
findings verbatim in [`reviews/round-2/`](reviews/round-2/). Every item **accepted**.

R2-1 is the round's centre and the second reproduced defect in this study: the reviewer
found that `attributed_keys` was updated *before* series scoping, so a required witness's
record for an unrelated series satisfied `requiredWitnesses`. Reproduced locally, fixed by
moving attribution inside the same-series branch, and confirmed
(`fail:witness-required-absent`). The reviewer's own `h09` is the mirror image of that
bug — a pinned witness's foreign-series record where the floor is zero — so the holdout
now guards the fix from both directions.

| # | Disposition |
| --- | --- |
| R2-1 (BLOCKER) | **Accepted, reproduced, fixed.** Attribution for enforcement is now series-scoped: a verifying record for another series is skipped before it can satisfy a per-series named-witness floor. |
| R2-2 (MINOR) | **Accepted.** The governing document said 14 cells while the matrix said 18, and still named `neg-sighting-forged`, `neg-unpinned-conflict` and `wit-retention-horizon`. All reconciled against the pinned 18-cell matrix. |
| R1-1 residual | **Accepted.** Two gaps: Study 017's own modules executed before the check, and an **unchecked** hash-based cache — which CPython uses without validating anything — was being skipped as harmless. The check now runs as a stdlib **bootstrap at the top of `score.py`, before any study or third-party import** (`__main__` is never loaded from a cache, so the entry point is exempt by construction), and unchecked-hash caches are always compared. |
| R1-2 residual | **Accepted.** The origin of the module *actually imported* is now authenticated against its distribution root, so a shadowing copy cannot satisfy a version check while other code runs. Package **contents** remain undigested; that residue is now stated in the preregistration rather than left implied. |
| R1-3 residual | **Accepted.** `bind_pins()` and `pinned_files()` returned a mutable mapping. Both now hand out an immutable `MappingProxyType` over a private copy. |
| R1-4 residual | **Accepted** (see R2-1) — the reviewer confirmed the association loop itself is sound in both the layer and the pair check, with only the foreign-series path outstanding. |
| R1-6 residual | **Accepted.** Cross-cell series equality is now checked, and "satisfies the enforcement floor" now means the cell's own retained same-series records meet its configured floor, not merely that the floor is ≥ 1. |
| R1-8 residual | **Accepted.** The last retired identifiers are gone from the governing document (see R2-2). |
| R1-9 residual | **Accepted.** Structured fields were published but not adjudicated and not printed. Cells that turn on the distinction now register `expectedComparisonPerformed`, the scorer adjudicates it as its own divergence channel (`witness:comparisonPerformed`), and the detection matrix prints the three fields per row. |
| R1-13 residual | **Accepted.** A mutation regression over every registered label is added. |
| R1-15 residual | **Accepted.** The registered SPEC still carried the "an exchanged head IS a sighting" wording the finding was about — the earlier edit reached only the module docstring. Now narrowed in both. |
| R1-5, R1-7, R1-10, R1-11, R1-12, R1-14 | **Confirmed RESOLVED** by the reviewer against the revised files. |

The reviewer's nine cells (`h01`–`h09`) are committed byte-for-byte in
`harness/MATRIX-HOLDOUT.json` with attribution, together with their construction
machinery: hooks reachable only through a `HoldoutAttemptContext` that the scorer mints
after its freeze gates pass, each hook verifying the context itself, construction inside
the attempt under `<attempt>/holdout-fixtures/`, digest stamps re-hashed after
adjudication, and a separate report that can never touch the locked stratum's R1 verdict.
**Nothing has executed the stratum**: the pilots' `holdout` member is null and the harness
tests assert only the refusal gates and static properties.

Post-revision state: 18 locked cells, 42 harness tests green, build pilot 03
(`pilots/2026-08-11-build-pilot-03`, non-citable) adjudicates 18/18 with all control gates
green, zero endpoint divergence, and the collusion pair structurally validated.

## Round 3 — 2026-08-11

Same reviewer. Verdict: **freezable after listed fixes**. Two results matter most and both
are confirmations rather than findings: the reviewer's nine cells are **byte-identical** to
what they authored in round 2, and — the check this round added — **all nine construction
hooks MATCH their registered constructions**, so no registered expectation was made
unfalsifiable by an implementation that built something else. Prompt and findings verbatim
in [`reviews/round-3/`](reviews/round-3/). Every item **accepted**.

| # | Disposition |
| --- | --- |
| R3-1 (BLOCKER) | **Accepted.** The holdout adjudicated only the two layer outcome strings, so a regression that reached the registered outcome by *different evidence* — precisely the R2-1 series-scoping class `h09` exists to guard — would have been reported concordant. The reviewer's block is untouched; a separate `harness/MATRIX-HOLDOUT-EVIDENCE.json` registers the structured values read off each cell's own construction text, it is a freeze pin (`matrixHoldoutEvidence`), and every field is adjudicated as its own `witness:<field>` divergence channel. |
| R3-2 (MINOR) | **Accepted.** "witness-3 is never pinned by any cell" was false once the reviewer's cells landed: `h03`/`h04` pin it deliberately. Narrowed everywhere to "never pinned in the locked-replication stratum". |
| R2-1 residual | **Accepted, and a claim withdrawn.** The combined regression is now committed (a required witness's foreign-series record satisfies neither the count floor nor the named floor and is never compared). My round-2 disposition also over-claimed that `h09` "guards the fix from both directions": `h09` requires no witnesses, so it guards the comparison path, not the named-floor path. The record says so. |
| R1-1 residual | **Accepted.** The governing prose still said any cache is refused, while equivalent caches are deliberately accepted. Corrected to describe what the bootstrap actually does, including why `__main__` is exempt. |
| R1-2 residual | **Accepted.** The origin check failed open when a module exposed no `__file__` and treated shared `site-packages` as the distribution root. It now refuses a missing module or missing `__file__`, and requires the imported file to appear in that distribution's own file inventory. |
| R1-6 residual | **Accepted.** The pair's floor check counted every same-series payload. It now counts only records that are schema-shaped, verify under a pinned key, and name the cell's series — the same test the layer applies. |
| R1-9 residual | **Accepted.** The detection matrix gained a witness-evidence column, and §5's "outcome strings alone" is corrected to name the structured channels. |
| R1-13 residual | **Accepted.** A mutation regression now covers every registered seed label individually. |

Post-revision state: 18 locked cells, 45 harness tests green.

## Round 4 — pending

Confirmation of R3-1, R3-2 and the six residual closures.
