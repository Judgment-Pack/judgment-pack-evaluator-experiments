# Round 6 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit a7ac228. Verdict: DO-NOT-FREEZE
(5 BLOCKER, 2 MAJOR). Dispositions: PREREG-REVIEW.md round-6 section; fixes landed as
commit 3730d0b.

---

1. **R6-1 — BLOCKER — The structural rescope sweep is incomplete.**

   **Offending.** The current living ledger still says an attestation names the call “that produced it” and tests an effect “produced by a different unretained call” (`PREREG-REVIEW.md:154`); `adapter/verify.py:1250-1253` still reasons about an effect “caused by” a call and a deployment recording which call “produced” it; and `test_reachability.py:406-412` calls the case “substituted causation” and the “wrong cause.” `MATRIX.json:685,691` says “the effect happens” and “the queue bypass is real.” Separately, the m02 report asserts that external state is “not retryable” (`fixtures/mutations/m02-ambiguous-commit/report.json:10`), while its builder describes an unretained private row as “failed/non-retryable” (`build_fixtures.py:931-950`); the same claim remains in `PREREGISTRATION.md:436-438` and `PREREG-REVIEW.md:35`.

   **Contradiction.** The load-bearing rescope says effects are “matched, never shown to have been caused” and that private-row “retryability … [is] asserted nowhere” (`PREREGISTRATION.md:396-409`). SPEC limits the join to “agreement between two retained records, not causation” (`adapter/SPEC.md:455-459`), and README says no live-runtime behavior is reported (`README.md:47-54`). The ledger also promises superseded rows receive explicit correction notes (`PREREG-REVIEW.md:8-13`), which R4-4 and the older D5 disposition lack.

   **Proposed fix.** Correct the living-ledger rows explicitly; rename and rewrite the causation regression and verifier comments as claimed-source-identity agreement; rewrite m01’s note as a synthetic modeled construction; remove every retryability assertion from m02, D5, and the builder. Regenerate m02’s report/manifests and account those new bytes in `DEVIATIONS.md`.

2. **R6-2 — BLOCKER — “Green means internally consistent” is not enforced across the retained outcome fields.**

   **Offending.** For report state `applied`, the verifier rejects only `connectorOutcome == "outcome-unknown"` and otherwise returns success (`adapter/verify.py:1378-1391`); SPEC registers the same loose predicate as “not `outcome-unknown`” (`adapter/SPEC.md:494-503`). I reproduced a complete green result by changing baseline only to `connectorOutcome: "rejected"` and `report.execution: "applied"`.

   **Contradiction.** README’s replacement ceiling says green means “the retained store is internally consistent” (`README.md:56-58`). Pinned source makes `rejected` terminal (`CFOS_SOURCE/packages/mcp-shared/src/action-store.ts:201-210`), records successful application separately (`:172-198`), and changes the outer record to `approved` only after `applyAction` returns (`CFOS_SOURCE/packages/workshop-backend/src/overseer.ts:2490-2498`); rejection instead produces outer `rejected` (`:7727-7732`).

   **Proposed fix.** Register and enforce a flattened-outcome/outer-lifecycle/report-state compatibility matrix. At minimum, `applied` and `effect-attested` must require the successful scalar, while `failed`, `rejected`, `pending`, and `outcome-unknown` must be correlated with their compatible outer/report states. Add one regression per scalar.

3. **R6-3 — BLOCKER — Identity uniqueness still has cross-language aliases and an omitted Node-side identity.**

   **Offending.** Binding deduplicates `repr(id)` (`adapter/verify.py:1033-1049`) but resolves gatekeepers with Python equality (`:467-470`). A second JSON gatekeeper with `id: 1.0` therefore survives uniqueness and aliases `id: 1`; binding passes, while Node stringifies both as `"1"` and returns `classification-refused` (`probes/ceremony.ts:170-179`). Boolean/numeric aliases create the inverse normalization hazard. Node also never checks duplicate ledger `(gatekeeperId, action)` identities, although binding does at `verify.py:1059-1067`.

   **Contradiction.** SPEC says both layers refuse duplicate identities and “neither reading may be preferred” (`adapter/SPEC.md:292-299,421-425`); `DEVIATIONS.md:206-210` records that item as closed on both sides.

   **Proposed fix.** Validate every ID and join component as a non-Boolean safe integer on both sides, normalize before lookup and uniqueness checks, and add ledger join identities to `storeAmbiguity()`. Regress `1/1.0`, `true/1`, `-0/0`, and the JavaScript safe-integer boundary.

4. **R6-4 — BLOCKER — Lifecycle/witness closure still permits a contradictory green store.**

   **Offending.** `drainCheck()` returns not-engaged whenever the ledger has no `autoApproved === true` row, before reading retained witnesses (`probes/ceremony.ts:331-343`), making its reverse-accounting check at `:497-523` unreachable. Changing baseline `autoApproved: true` to `false` while leaving witness `appliedActionIds: [1]` yields binding pass, upstream not-engaged, and combined pass under `verify.py:1605-1611`. In addition, lifecycle validation reads `autoApproved` with `.get()` and tests `auto is not None` (`adapter/verify.py:692-695,727-732`), so explicit `autoApproved: null` passes on otherwise valid pending and rejected rows.

   **Contradiction.** SPEC says “a witness claiming an application the ledger does not record” fails (`adapter/SPEC.md:315-316`) and that an `autoApproved` value “of any kind” outside `approved` is refused (`:369-372`); the latter is also recorded as closed in `DEVIATIONS.md:192-193`.

   **Proposed fix.** Read witnesses before the early exit and return not-engaged only when both claims and witnesses are empty. Use key-presence checks for lifecycle-only fields, not `.get()`/null equivalence. Add the contradictory-witness and explicit-null regressions.

5. **R6-5 — BLOCKER — The registered strict time boundary is neither strict nor identical across layers.**

   **Offending.** Node uses a digit-shaped regex followed by permissive, millisecond-resolution `Date.parse` (`probes/ceremony.ts:127-138`). It normalizes invalid dates such as `2026-02-29T00:00:00Z` and collapses `.0004Z` and `.0005Z` to the same instant. In the latter construction, a genuinely earlier resolution is retained in the queue and its witness passes. Python parses fractional seconds through `float` and performs arithmetic outside its `ValueError` guard (`adapter/verify.py:108-132`); an extreme valid-shaped fraction can raise `OverflowError` from `_drain_witness_problem()` at `:510` instead of returning an apparatus result.

   **Contradiction.** SPEC registers exact `resolved < at`, equality as not-yet-resolved, and “strict RFC 3339 … on both sides,” with invalid stamps refused rather than compared (`adapter/SPEC.md:318-327`). `DEVIATIONS.md:173-182` records those acceptances as closed.

   **Proposed fix.** Prefer enforcing the one canonical serialized-JavaScript-Date form (`YYYY-MM-DDTHH:mm:ss.sssZ`) identically on both sides; alternatively implement exact integer date/fraction parsing. Make Python parsing total and add invalid-calendar, sub-millisecond-boundary, overflow, and equality tests.

6. **R6-6 — MAJOR — `governed_inventory()` is resource-only despite the normative tool-and-resource scope.**

   **Offending.** The implementation classifies every approved ledger row on the governed resource as governed without examining its own `description.actionKind.label` (`adapter/verify.py:411-460`). SPEC first says the inventory covers “the tool and resource … and nothing else” (`adapter/SPEC.md:400-413`), then silently defines ledger membership by resource alone (`:415-419`). I reproduced a coherent `tracker_close_work_item` row and matching call on the same resource being counted against the create-work-item authorization and falsely rejected as `binding-reuse`.

   **Contradiction.** The normative scope is explicitly “the governed tool and resource” (`adapter/SPEC.md:401-408`), and `DEVIATIONS.md:211-214` says that wording was corrected to match implementation.

   **Proposed fix.** Classify a ledger row using its own retained action-kind label: retain target-tool rows even when a joined staged call contradicts them, exclude coherently different-tool rows, and refuse unclassifiable or internally contradictory labels. Add the reciprocal coherent-other-tool regression.

7. **R6-7 — MAJOR — The new `EXCLUDED_DOCUMENTS` safeguard and its test are tautological.**

   **Offending.** `README.md` and `DEVIATIONS.md` are absent from `REGISTERED_DOCUMENTS`, and no candidate glob reaches top-level Markdown (`harness/make_manifest.py:28-59`); therefore the filter at `:61-64` never encounters either name. Removing `EXCLUDED_DOCUMENTS` produces the identical manifest. Nevertheless, the test says the files are excluded “by a named constant rather than by omission” and that “the exclusion is the only reason” (`harness/tests/test_study.py:194-211`).

   **Contradiction.** `PINS.json:73-78` promises exclusion “by construction rather than by omission,” while `DEVIATIONS.md:292-297` itself concedes it was already implicit because “no glob reaches a top-level `.md`.”

   **Proposed fix.** Put the appendable top-level documents into the candidate population and then filter them. Add a test showing that disabling the exclusion causes both files to enter the manifest.

do not freeze

Path (a) was taken clearly in PREREGISTRATION §9 and README, and several repairs are genuine: unbound-call refusal, orphan/wrong-tool handling in the reviewed direction, C5’s observation withdrawal, complete resolver comparison, the registered second deployment and byte-for-byte descriptions, effect-source union/G0, and the renamed three-fact test. C1 and C4 are now stated where relied upon and are defensible as accepted history under the explicitly self-asserted-witness ceiling, though R6-5 prevents trusting their implementation yet. Zero-drift discipline otherwise checks out: both matrices’ `{id, expected}` projections are unchanged from `dc4bc91`, the holdout registry is byte-identical, and the 21 platform files, two ledgers, and 23 derived manifests match `DEVIATIONS.md:128-137`; direct binding/replay verdict-code-suppression projections over all 35 cells also showed no drift. The runnable suites passed (58 study tests; 63 non-upstream reachability tests), while the remaining upstream batch was blocked only by the sandbox denying Node’s self-report `git` child. The listed blockers nevertheless leave both the chosen structural rescope and its replacement internal-consistency claim false on current surfaces and executable paths.

CODEX-015-R6-DONE
