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

## Round 2 — pending

Confirmation pass over R1-1..R1-15 against the revised tree, plus the reviewer-authored
holdout stratum (committed verbatim with attribution, never executed pre-freeze; its
construction machinery lands with the cells).
