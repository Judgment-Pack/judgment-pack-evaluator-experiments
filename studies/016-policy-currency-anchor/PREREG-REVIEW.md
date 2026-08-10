# Pre-freeze review record — Study 016

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here.

## Round 1 — 2026-08-10

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra,
read-only sandbox. Verdict: **DO NOT FREEZE** (4 BLOCKER, 8 MAJOR, 3 MINOR). Prompt and
findings verbatim in [`reviews/round-1/`](reviews/round-1/). The reviewer states they are
prepared to author the holdout stratum at the next round.

All fifteen findings **accepted**; several with a narrowed remedy the finding itself
offered. The revision is matrixVersion 2 (22 cells), a strictly fail-closed verifier
vocabulary, and rescoped claims throughout.

| # | Sev | Disposition |
| --- | --- | --- |
| R1-1 | BLOCKER | **Accepted.** Bare-name imports could execute unpinned code while the file digests reported clean. `harness/upstream014.py` now refuses pre-existing `sys.modules` entries for the shared names, and on EVERY `load()` — cached loads included — verifies each loaded module's resolved `__file__` against the exact pinned path and its bytes against the pinned digest. |
| R1-2 | BLOCKER | **Accepted.** The cell was a remint, not a rollback: OWP has no contract ordering, so nothing is "older", and 014 registered exactly this as descriptive e22 while RFC 0011 R-1 removed it as evidence. Renamed `cur-workorder-remint-accepted`, role `descriptive` (published, never counted), prose rewritten everywhere; the CURRENCY-layer acceptance stands as the registered scope boundary. |
| R1-3 | BLOCKER | **Accepted.** The verifier now parses with duplicate-member-rejecting strict JSON, checks exact closed schemas (types, member sets, digest formats, integer-not-boolean) before any canonicalization or signature math, bounds canonicalization with registered codes, checks the attestation payload's own `snapshotVersion`, and refuses a malformed `minimumHeadPin` as `currency-unavailable` rather than degrading to "no pin". Adversarial vectors added for each. |
| R1-4 | BLOCKER | **Accepted.** The scorer now validates the fork STRUCTURALLY from the two snapshot artifacts (same genesis record, same authority key id, same attested position, different heads) and derives the pair report from adjudicated outcomes; the hardcoded reveal field is gone. Impossibility wording narrowed everywhere to "a fresh, stateless, per-series-pinned verifier given exactly one view", and the sequential stateful arm is registered as its own endpoint (`cur-split-view-b-stateful`): view A's head provisioned as the minimum head pin refuses view B by prefix containment. |
| R1-5 | MAJOR | **Accepted (rename remedy).** The layer holds no storage and returns no state update, so the field is renamed `minimumHeadPin` and registered as caller-provisioned prior-acceptance state — the state a sequential production verifier would have persisted. A durable high-water lifecycle (atomic persistence, update-on-accept) is explicitly not claimed and named future work. |
| R1-6 | MAJOR | **Accepted (collapse remedy).** `authorityKeyId` is outside the signed payload, so signer-identity attribution from it was unsound. The vocabulary now carries ONE code, `snapshot-signature-invalid` — "does not verify under the pinned authority key" — covering both a corrupted signature and a different signer, which are indistinguishable to a single-pinned-key offline verifier; the unauthenticated label appears in `detail` only, and the SPEC records the indistinguishability as a trust-model property. `snapshot-authority-unpinned` is removed. |
| R1-7 | MAJOR | **Accepted.** Registered limits added (RFC 0011 R-13): `MAX_SNAPSHOT_BYTES` 1 MiB before parse, `MAX_CHECKPOINTS` 1024, `MAX_SUPPORTED_SET` 512 — values chosen so each limit is independently reachable — with the new code `snapshot-limits-exceeded` and at-limit/past-limit vectors. |
| R1-8 | MAJOR | **Accepted.** Two aliveness controls added under the v0.17.0 tuple — `neg-binding-alive` (014's a01 construction) and `neg-replay-alive` (014's e23) — so no layer's expectations are satisfiable by a hardcoded pass. The "chain layers replicate 014's result" sentence is replaced: the chain layers demonstrate positive compatibility of the pinned adapter on this study's five chains; 014's refusal coverage is 014's evidence. |
| R1-9 | MAJOR | **Accepted.** The byte-identical endpoint pair was one adjudication counted twice, and the "withholding" reading was e18's flaw returning (bytes carry no evidence a newer snapshot exists). `cur-older-snapshot-unpinned` is removed; `cur-concurrent-set` is one endpoint carrying two registered readings — concurrent-set membership (scored) and the freshness-floor reading (analytic, not separately scored). The freshness demonstration group (`dem-*`) is unchanged: demonstrations were never counted. |
| R1-10 | MAJOR | **Accepted.** Trust is per-series: `trustconfig.seriesId` binds which series the pins confer authority over, and a commitment for a different series refuses as `currency-unavailable`. The second trust root is registered (`registryAuthority.otherSeriesGenesisHead`, enforced) and the one-genesis-serves-the-matrix claim is withdrawn; `cur-series-unknown` is reclassified `config`-variant with the construction stated honestly. |
| R1-11 | MAJOR | **Accepted.** A post-freeze `--include-holdout` with an EMPTY registered holdout is now a recorded terminal refusal ("an empty holdout is not a passing holdout"), never a locked-only adjudication; a nonempty holdout without construction machinery remains a recorded terminal refusal. The machinery lands together with the reviewer-authored cells before the freeze. |
| R1-12 | MAJOR | **Accepted.** The marker now carries `pinsRawSha256` — SHA-256 of the RAW registry bytes, computed before the parse — and every terminal and successful record repeats it, so even an attempt that dies on a malformed registry is tied to the exact registry bytes it saw. Post-marker `SystemExit` is terminal-recorded and then re-raised. |
| R1-13 | MINOR | **Accepted.** `add` never reactivates: a later add of an already-bound version is `binding-rebound` on a different digest and an inconsistent history on the same digest; `reinstate` is the only re-entry event. SPEC §1 states the lifecycle rules and a vector covers the same-digest re-add. |
| R1-14 | MINOR | **Accepted.** Every `registryAuthority` member is now mechanically recomputed before adjudication — both keys re-derived from their seed labels, both genesis heads rebuilt from the registered genesis events — and any mismatch refuses. The seeds are public deterministic fixtures; nothing depends on their secrecy, and the pins note says so. |
| R1-15 | MINOR | **Accepted.** The research question now asks about membership in the supported set at a pinned snapshot (never "no longer in force"); the lineage sentence says an action was taken in reliance on a judgment under the registered downstream mapping (Core §3.5/§6.4, RFC 0011 R-12); "dated assertion" is gone — the attestation carries a position, not a time. |

Post-revision state: 52 harness tests green; build pilot 02 (`pilots/2026-08-10-build-pilot-02`,
non-citable) adjudicates 22/22 with all control gates green, zero endpoint divergence, the
fork structurally validated, and the two registered-undetected rows confirmed undetected.

## Round 2 — 2026-08-10

Same reviewer (codex-cli 0.145.0 / gpt-5.6-sol / ultra / read-only). Verdict:
**freezable after listed fixes** — 8 RESOLVED, 7 PARTIALLY RESOLVED (each with a precise
residual), 1 new MINOR (R2-1), and the 10-cell holdout stratum authored. Prompt and
findings verbatim in [`reviews/round-2/`](reviews/round-2/).

Every residual **accepted and closed**; R2-1 **accepted**; the holdout **landed verbatim**:

| Item | Disposition |
| --- | --- |
| R1-1 residual | **Closed.** No 014 directory ever enters `sys.path` and no bare import of a 014 name occurs: every module is loaded by `spec_from_file_location` from its authenticated absolute path, digest-checked immediately before execution, with the shared names pre-seeded (after collision refusal) so the frozen modules' own imports resolve to verified instances. Per-load identity/origin/bytes verification kept. |
| R1-2 residual | **Closed.** The stale `cur-authz-rollback-accepted` reference and "e22-class rollback" wording purged from the preregistration; the builder's `rollback` identifier and salt renamed (`workorder-remint-016`), chains rebuilt. Remaining "rollback" strings are OWP's own `owp.rollback_patch` tool name and explanatory "not a rollback" prose. |
| R1-3 residual | **Closed.** `layer_currency` now takes the trust-configuration BYTES and parses them with the same duplicate-member-rejecting strict reader; a malformed configuration is `currency-unavailable`. Vector added (holdout h01's premise, tested independently at the unit level). |
| R1-4 residual | **Closed.** Fork validation is authenticated: both head attestations must verify cryptographically under the ENFORCED `registryAuthority` pinned key (never the snapshots' unauthenticated labels), with identical per-series trust pins, identical genesis record, same position, different heads. |
| R1-7 residual | **Closed.** Exact-at-limit vectors added for all three limits: a snapshot at exactly `MAX_SNAPSHOT_BYTES` (inclusive boundary), a supported set at exactly 512, a checkpoint list at exactly 1024 — each must verify, with the one-past siblings refusing. |
| R1-11 residual | **Closed.** The construction machinery landed WITH the authored cells: `HoldoutAttemptContext` minted only by the scorer and verified against live digests (any null freeze pin refuses, so pre-freeze execution is impossible); in-attempt construction under `<attempt>/holdout-fixtures/`; per-cell `CONSTRUCTION.json` (`built`/`harness-error` — no construction drives an upstream OWP path, so 014's `refused` class is inapplicable and the registry note says so); adjudication against the reviewer's expectations; digest stamps plus post-adjudication re-hash; a separate report section whose outcomes never touch R1. The empty-stratum refusal stands. Nothing has executed: harness tests assert only the refusal gates and static properties. |
| R1-12 residual | **Closed.** The scorer reads the pin registry ONCE: the marker hashes exactly the bytes that are then parsed — no second read, no hash/parse divergence window. The `PINS.json` prose now names `pinsRawSha256` accurately, and the redundant post-parse `pinsSha256` stamp is dropped. |
| R1-15 residual | **Closed.** README now says an executed action was taken in reliance on a judgment under the registered downstream mapping, and the research question asks about membership in the supported set at a pinned snapshot. |
| R2-1 (MINOR) | **Accepted.** §1a now says 22 cells, matching §4 and the matrix. |
| Holdout stratum | **Landed verbatim** in `harness/MATRIX-HOLDOUT.json` with attribution (`codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2`): h01–h10, including three at-limit boundary cells (h07–h09) and the all-pass brittleness control (h10). Registered expectations untouched; first-ever execution is the registered primary attempt. |

Post-revision state: 59 harness tests green; build pilot 03 (non-citable) adjudicates
22/22, control gates green, zero endpoint divergence, the fork report authenticated, and
the holdout member of `RESULTS.json` null — the stratum is untouched pre-freeze by
construction.

## Round 3 — pending

Confirmation of the seven residual closures, R2-1, and the verbatim holdout landing.
