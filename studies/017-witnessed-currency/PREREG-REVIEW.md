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

## Round 2 — pending

Confirmation of R1-1..R1-15, plus the reviewer-authored holdout stratum (committed verbatim
with attribution, never executed pre-freeze; its construction machinery lands with the
cells).
