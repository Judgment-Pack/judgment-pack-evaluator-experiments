# Pre-freeze review record — Study 021

Cross-vendor review rounds on the preregistration and the registered matrices, under the
interim review regime: each round's prompt verbatim, the reviewer's findings verbatim, and the
maintainer's disposition of every finding. The freeze is the squash-merge of the pull request
this record names once a round returns `freezable as written`.

## Round 1 — 2026-09-14

Reviewer: codex-cli 0.153.4, model gpt-6-astra (OpenAI), read-only sandbox, on worktree commit `ba15fe11`; different vendor than the model that drafted (Claude). Verdict: **not freezable as written** (3 BLOCKER, 7 MAJOR); eight holdout cells authored.

> Note: the reviewer's worktree paths are normalized here. The finding prose is otherwise verbatim.

### Round 1 — prompt (verbatim)

```
You are the pre-freeze cross-vendor reviewer for Study 021 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration overclaims, where a registered cell's expectation does not follow from the pack's text and the runtime's documented semantics, where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may run the harness tests and the pilot scorer (JPACK=<path> is not set for you; treat the runtime as unavailable and reason from the documents).

Read, in the study directory studies/021-history-replay-catch/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, apparatus, strata, defect classes, the line-moved signature (section 5), the structures S1–S7 and the registered cells (section 6), gates (section 7), limits (8–10).
- harness/MATRIX.json — 123 registered cells, each with its structure and reason. Verify a sample of at least twenty cells across all four policies and both endpoints against the vendored packs under fixtures/policies/ (the four *.pack.json and their *.base.json) and the runtime's semantics as the JPS Core specification states them (the spec repository is checked out read-only at /home/onword/repo/judgment-pack/judgment-pack-spec; read `git -C <path> show origin/main:spec/judgment-pack-core.md`, sections 7 and 8: conditions, rule and exception resolution, conflicts, onUnknown, evidence requirements). Say for each sampled cell whether the reason is sound, and name any cell whose expectation you can show does not follow.
- harness/*.py — jp.py (the runtime runner), build_ledgers.py (the two strata), plant.py (nine defect classes), replay.py (the replay and the signature rule), score.py (aggregation, Clopper–Pearson intervals, adjudication, gates), make_manifest.py, PINS.json, and harness/tests/test_study.py. Look for: a way the random generator can produce a ledger that is not "decisions made under the pack"; a defect class applied at a site the registration does not describe; the signature computed differently from section 5's words; an adjudication that could report "R1 holds" without the gates having run; a seed-reservation defect (pilots drew seeds 1–30; the registered attempt draws 101–130).
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md must stay outside the manifest; tools/check_freeze_sets.py at the repository root states why).
- For precedent on what this repository's preregistrations must contain and how they were reviewed, read studies/018-transition-rules/PREREGISTRATION.md and studies/018-transition-rules/PREREG-REVIEW.md (rounds 1–3 suffice).
- The runtime's ADR-0034 (the profile the study reads) is at /home/onword/repo/judgment-pack/judgment-pack-runtime, `git -C <path> show origin/main:docs/adr/0034-profile-a-matrix-against-its-history.md`; verify that the registration's account of `profile.thresholds` (below/at/above per origin, one entry per literal) matches it.

Then, as the reviewer's holdout stratum (the 014/016/017/018 remedy): author at least six holdout cells in the schema of harness/MATRIX.json — new (policy, defect, stratum, endpoint) combinations NOT already registered, each with your own expectation derived from the same structures and your own stated reason — and give them as a JSON array the maintainer will place byte-for-byte in harness/MATRIX-HOLDOUT.json. Choose cells that would falsify the registration's account if it is wrong (e.g. random-stratum catch rates at n = 20 the registration left descriptive, or literal-stratum signature cells the registration deliberately did not register).

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence or cell, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
```

### Round 1 — findings and holdout (verbatim)

**Verdict: `not freezable as written`.**

The strongest finding is reproducible without the runtime: the scorer can report **`REGISTERED: R1 holds` with no replay observations and no executed controls**.

I reviewed worktree HEAD `ba15fe11dc55e013f6479bd819d334947e1fad03`, Core §§7–8 at spec `origin/main` `587ebc5e…`, runtime ADR-0034 at `0c8a4b63…`, and Study 018’s registration and review rounds 1–3. I ran no primary attempt and no runtime evaluations. Harness tests: **14 passed, 2 skipped**. The 20-file manifest matches; `check_freeze_sets.py` reports no problems. Files remain unchanged.

1. **BLOCKER — missing observations and unexecuted controls can produce “R1 holds.”**

   Exact commitment: §7 promises **“pipeline-invalid — no cells read — → control-gate failure → zero divergence … → otherwise R1 falsified.”**

   [score.py:147](<worktree>/studies/021-history-replay-catch/harness/score.py:147) accepts empty gate arrays, does not require `INDEX.json`, and does not require the four policies or their expected ledger/defect sets. `unobserved` endpoints do not falsify R1. `allowsNoCaught` also accepts *missing observations*, rather than only a completed set of uncaught replicates. G3 is not executed or recorded by the scorer.

   An entirely in-memory test of `score.main()`, with an empty `p/cells.json`, empty gate record and absent index, returned:

   ```text
   REGISTERED: R1 holds (123 registered cells, 0 diverge)
   gateFailures: []
   cell verdicts: 86 unobserved, 37 holds
   ```

   Related failure paths compound this: `replay()` defaults a missing mismatch count to zero and ignores failure status; `random_ledger()` returns a short ledger after `10*n` refusals. A mocked refusal-exhaustion test returned **zero rows under n=20**, without an error.

   **Smallest sufficient fix:** require complete, unique policy/defect/ledger sets, registered row counts, successful replay records, complete G1/G2 evidence and recorded G3 success before adjudication. Missing observations must be pipeline-invalid. Restrict `allowsNoCaught` to complete observations with zero catches. Refusal exhaustion must fail construction.

2. **BLOCKER — freeze pins and holdout participation are not enforced.**

   Exact commitment: §2 says **“the preregistration, matrix and manifest digests are all pinned and match; any null makes it a PILOT.”** `PINS.json` likewise claims every non-null member is enforced.

   [score.py:140](<worktree>/studies/021-history-replay-catch/harness/score.py:140) checks only the *truthiness* of three freeze values. It never hashes those artifacts or validates the manifest. It omits `matrixHoldout`, permits a null runtime digest, and permits `REGISTERED` without `--include-holdout`. A requested but missing holdout file is silently skipped; an empty holdout is accepted.

   The synthetic test above used three `"wrong"` freeze hashes, null runtime/holdout pins, and no holdout.

   There is also an integration failure for the requested deliverable: a top-level holdout **array** reaches `matrix["cells"]` and raises `TypeError`. The current placeholder is an object envelope.

   **Smallest sufficient fix:** compare every required digest, validate the manifest’s exact covered set and contents, and require the nonempty holdout for `REGISTERED`. Normalize the supplied top-level array in memory so its file bytes can remain unchanged. Check and record the runtime identity when producing results, not merely when later scoring them.

3. **BLOCKER — the primary-attempt and seed reservation rules are not executable safeguards.**

   Exact commitments: the primary root **“must not exist”**, the scorer **“refuses an existing root”**, and the first invocation counts **“crash and all.”**

   Builders use `mkdir(..., exist_ok=True)` and overwrite files. The scorer refuses only an existing `ADJUDICATION.json`. A failed attempt before adjudication can therefore be replaced. There is no first-invocation marker.

   Seed reservation has the same gap: `stratum_of()` discards the seed, and the scorer accepts any seed set or replicate count. Pilot results using seeds 1–30 can be scored as the registered random stratum. The builder also has no reservation check preventing a pilot from drawing 101–130.

   **I found no retained pilot files using reserved seeds:** the files inspected used 1–30. This is an enforcement defect, not evidence of actual contamination.

   **Smallest sufficient fix:** add one governing runner that exclusively creates and marks the primary root before construction, records its configuration, and rejects reuse. Require precisely seeds 101–130, thirty distinct replicates per n, and their corresponding input records. Guard those seeds from pilot construction.

4. **MAJOR — the random distribution is not the distribution used to justify the cells.**

   Exact sentence: S3 gives boundary probability **“1/(2L+1) per row.”**

   [build_ledgers.py:110](<worktree>/studies/021-history-replay-catch/harness/build_ledgers.py:110) samples a continuous uniform value and rounds it. It does not sample uniformly from the discrete lattice. Ignoring negligible floating-point effects:

   - Sanctions values `{0,1,2}` have probabilities `{1/4,1/2,1/4}`, not thirds.
   - Expense value `75` has probability `1/150`, not `1/151`.
   - Vendor value `250000` has probability `1/500000`, not `1/500001`.

   Some reasons also omit evidence/domain restrictions. Sanctions rule mutations require present evidence. Expense `D6-03/random-50/caught` says changed cases are “about a fifth of draws”; the actual per-row probability is approximately **0.0629**, yielding approximately **0.9612** catch probability at n=50.

   **Smallest fix:** retain the generator and correct the distribution and affected derivations. Alternatively, implement discrete-uniform sampling and rederive every affected registration before freezing.

5. **MAJOR — some exact signature expectations confuse possible cases with cases present in each ledger.**

   Exact cells:

   - `sanctions-screening/D4-04/random-50/lineMovedWhenCaught`: `[0,0]`
   - `sanctions-screening/D5-06/random-50/lineMovedWhenCaught`: `[0,0]`
   - `vendor-onboarding/D8-23/random-50/lineMovedWhenCaught`: `[1,1]`

   Their structural arguments do not establish those certainties.

   For sanctions D4, a ledger containing changed zero-match cases but no changed two-match cases carries the signature. Under the implemented distribution, the probability that at least one of thirty n=50 replicates has this signature is approximately **7.29%**. For sanctions D5-06, a caught ledger containing changed twos but no changed ones also carries it, although much less frequently.

   Conversely, vendor D8-23 changes the case exactly at `250000`; a caught replicate containing that case lacks the signature. Its small probability does not establish signature=1.

   S7 also needs a qualification: an at-row at **one** literal does not necessarily break §5’s signature. Vendor D2-17 retains the `250000` mirror, below which every changed case lies; that other literal can satisfy the existential condition.

   **Smallest fix:** distinguish structural invariants from finite-sample predictions. Retain exact intervals only as explicitly probabilistic predictions with their failure probabilities, or register suitably justified intervals. Correct S7’s account of multiple literals. I am not claiming that the reserved seeds actually diverge.

6. **MAJOR — R2 uses a different signature denominator from its registration.**

   Exact commitment: R2 reports **“the fraction of caught cells carrying the line-moved signature.”**

   `aggregate()` instead divides by caught cells with `signature.applicable`. Caught cases without thresholds disappear. This omits triage entirely from the signature table and excludes expense D6-03 catches from their class denominator.

   An isolated aggregation test with one caught, threshold-free cell returned **no signature row**, rather than rate zero.

   **Smallest fix:** use all caught cells as the denominator, count absent signatures as zero, and publish the threshold-free count separately. This also aligns R2 with `observe()`.

7. **MAJOR — the pooled Clopper–Pearson intervals are not exact 95% intervals for the registered estimand.**

   Exact commitment: R2 promises **“exact 95% Clopper–Pearson intervals”** by defect class.

   The numerical routine passes its known-value tests. The problem is its inputs: `aggregate()` pools different mutation sites tested against the **same ledgers**. These indicators have different catch probabilities and are dependent within a ledger. They are not independent identically distributed Bernoulli trials. The deterministic literal stratum is not a sample of independent mutation trials either.

   **Smallest fix:** report class aggregates descriptively without an exact-binomial coverage claim; provide binomial intervals per defect instance across independently seeded ledgers where justified. Alternatively, explicitly label the pooled intervals as binomial reference intervals without nominal coverage guarantees.

8. **MAJOR — the literal stratum silently removes the generator’s absence probe.**

   Exact description: §3 calls these the runtime’s own `packs suggest` candidates, decided under the pack.

   ADR-0024 states that a run without `--base` emits an absence candidate containing no facts. `literal_ledger()` requests exactly that mode, then deep-merges every candidate over the complete base. The absence candidate consequently becomes the base case. It does not test missing facts or their `onUnknown` paths.

   **Smallest fix preserving current outcomes:** describe the actual transformation explicitly: sparse candidates are overlaid on the base, the absence candidate becomes a baseline duplicate, and fact-absence behavior is outside this stratum. If absence coverage is intended, preserve it during construction and review the resulting ledger afresh.

9. **MAJOR — §5 needs to distinguish all mismatches from placeable mismatches.**

   Exact words: **“every disagreeing row lies strictly on one side.”**

   ADR-0034 excludes absent/noncomparable facts from all three threshold buckets. [replay.signature()](<worktree>/studies/021-history-replay-catch/harness/replay.py:26) examines only those buckets.

   A profile with two mismatches—one below the threshold and one unplaceable—returns `lineMoved: true`. Thus the implementation satisfies “every **placeable** disagreeing row,” not an unrestricted reading of the sentence.

   **Smallest fix:** state that restriction explicitly, or require complete placement of mismatched rows before granting the signature. This is a contract ambiguity; I did not demonstrate an unplaceable mismatch in the current generated ledgers.

10. **MAJOR — three cells can succeed for the wrong registered reason.**

    Exact cells: `expense-approval/D7-00/literal/caught`, `D7-01/literal/caught`, and `D7-02/literal/caught`.

    Each says the prohibited-category row **“was denied and is now reimbursed.”**

    The mutation changes only the deny rule’s list. The reimbursement rule’s separate exclusion remains intact. Consequently, neither rule fires and Core §8 selects fallback **`review`**, not `reimburse`.

    **Smallest fix:** replace the reason with “deny → fallback review.” The registered catch value `[1,1]` remains correct. This is precisely the kind of mechanism error a catch-only success cannot expose.

The requested sample audit covers **30 distinct registered cells** below. `L` means literal; `R50` means random at n=50; `C` means `caught`; `M` means `lineMovedWhenCaught`. “Plausible” distinguishes a finite-sample prediction from a structural consequence.

| Policy | Defect / stratum / endpoint | Registered interval | Reason audit |
|---|---|---:|---|
| Vendor | D7-00 / L / C | [0,0] | Sound: stopping the information rule exposes the same fallback; approval cannot coexist on these inputs. |
| Vendor | D6-02 / L / C | [1,1] | Sound: the incomplete candidate newly fires approval beside request-info, producing conflict. |
| Vendor | D6-05 / R50 / C | [0,0] | Sound: required evidence blocks normal rules when absent. |
| Vendor | D1-11 / L / C | [0,0] | Sound: committee escalation masks the newly admitted spend band. |
| Vendor | D3-18 / L / C | [1,1] | Sound: at 250000, removing committee escalation exposes request-info fallback. |
| Vendor | D2-17 / R50 / M | [1,1] | Expectation sound; explanation incomplete: the unchanged 250000 boundary also guarantees one-sidedness. |
| Vendor | D8-23 / R50 / M | [1,1] | Unsupported as certainty: a changed at-row breaks it. |
| Vendor | D7-15 / R50 / M | [1,1] | Sound: committee escalation masks changes at/above the line. |
| Expense | D7-00 / L / C | [1,1] | Catch sound; reason wrong: deny → review. |
| Expense | D7-01 / L / C | [1,1] | Catch sound; reason wrong: deny → review. |
| Expense | D7-02 / L / C | [1,1] | Catch sound; reason wrong: deny → review. |
| Expense | D6-03 / R50 / C | [0.8,1] | Plausible interval; “about a fifth” derivation is wrong. |
| Expense | D6-04 / L / C | [1,1] | Sound: removing the exclusion creates conflicting deny/reimburse rules. |
| Expense | D6-05 / R50 / C | [0,0] | Sound: required receipt makes the redundant guard unobservable. |
| Expense | D1-06 / R50 / M | [1,1] | Sound: changed amounts are in [75,94), strictly below the retained threshold 94. |
| Expense | D3-08 / R50 / C | [0,0.25] | Plausible interval; exact boundary probability is misstated. |
| Expense | D9-15 / R50 / M | [0.8,1] | Sound mechanism and plausible interval: at-75 fallback catches break the signature. |
| Sanctions | D7-00 / L / C | [1,1] | Sound: zero loses its only candidate outcome and produces no-match. |
| Sanctions | D1-01 / R50 / M | [1,1] | Sound: only present-evidence ones change, below the new threshold 2. |
| Sanctions | D2-02 / L / C | [1,1] | Sound: zero newly fires conflicting clear/match rules. |
| Sanctions | D3-03 / R50 / C | [0.9,1] | Plausible interval; “one third” ignores the actual rounding distribution and evidence. |
| Sanctions | D4-04 / R50 / M | [0,0] | Unsupported certainty: a caught replicate need not contain both changed sides. |
| Sanctions | D5-06 / R50 / M | [0,0] | Unsupported certainty: a caught replicate need not contain a changed at-row. |
| Triage | D7-01 / L / C | [1,1] | Sound: incomplete/hard-fail loses clarify, resolving conflict to decline. |
| Triage | D7-02 / R50 / C | [0,0] | Sound for generated inputs: the removed pending branch exposes the same fallback. |
| Triage | D6-05 / L / C | [0,0] | Sound under the actual base overlay: complete candidates remain pass; non-pass candidates remain incomplete. |
| Triage | D6-06 / R50 / C | [0,0] | Sound: required intake evidence blocks rules before this guard matters. |
| Triage | D5-10 / L / C | [0,0] | Sound: incomplete/hard-fail remains a conflict after decline becomes proceed. |
| Triage | D8-13 / R50 / C | [0.9,1] | Sound: every embargoed case changes, including missing-evidence cases, because exception-escalation is added to retained reasons. |
| Triage | D9-14 / L / C | [0,0] | Sound for the current literal construction: no candidate reaches fallback. |

Two requested checks do **not** support additional accusations. All **63 planted instances** fit §4’s site/edit definitions; I found no out-of-scope planting in these fixtures. The current four packs’ applicability domains are also isolated correctly by the random generator. Its general implementation is weaker: it pools applicability and rule literals for a pointer and never rejects a returned `not-applicable` disposition. A future shared-pointer pack could therefore admit non-applicable rows. The existing “deterministic and applicable” test uses sanctions, which has no applicability condition, and asserts no applicability property.

ADR-0034 supports the registration’s basic profile account: counts are per origin and per distinct pointer/decimal boundary, with coincident sites grouped. The defects are in interpretation and omitted placement, not a mistaken assumption that each rule site receives independent row counts.

README and DEVIATIONS correctly remain outside the generated manifest. Their current banners match the draft state. The mutable “Nothing has run” banner in the preregistration should, however, be made permanently time-qualified before freezing, as its opening already does.

The eight holdout cells below use **new four-part combinations even without counting n**. I validated their IDs, defect existence and non-overlap; I did not execute their outcomes. The literal cells are independent reviewer expectations over an already-piloted deterministic stratum, not newly unseen inputs. The random cells concern the reserved attempt.

The loader fix in finding 2 is necessary to accept this array byte-for-byte as `harness/MATRIX-HOLDOUT.json`.

```json
[
  {
    "id": "h01-expense-d7-00-literal-signature",
    "policy": "expense-approval",
    "defect": "D7-00",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 1, "max": 1},
    "structure": "S6",
    "reason": "Replacing alcohol only in the deny rule leaves the reimbursement exclusion intact. The receipted alcohol candidate at the base amount 42.50 changes from deny to fallback review; every changed literal-stratum case remains below 75, so the signature is present."
  },
  {
    "id": "h02-expense-d6-03-literal-no-threshold",
    "policy": "expense-approval",
    "defect": "D6-03",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 0, "max": 0},
    "structure": "S5",
    "reason": "Dropping the amount guard changes the permitted, receipted candidates at 75 and 76 from review to reimburse and removes the pack's only ordered comparison. The ledger is caught but has no threshold signature."
  },
  {
    "id": "h03-vendor-d8-23-literal-at-row",
    "policy": "vendor-onboarding",
    "defect": "D8-23",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 0, "max": 0},
    "structure": "S5",
    "reason": "Changing committee escalation to force approve changes the spend candidates at 250000 and 250001. The unchanged approval guard and committee condition both use the sole boundary 250000; the disagreeing at-row prevents a signature."
  },
  {
    "id": "h04-vendor-d2-17-literal-mirror",
    "policy": "vendor-onboarding",
    "defect": "D2-17",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 1, "max": 1},
    "structure": "S7",
    "reason": "Moving committee escalation down to 187500 changes the clean candidate at 249999 from approve to unresolved. All changed candidates lie in [187500,250000), strictly below the unchanged approval boundary 250000. Section 5 needs one qualifying literal, so that mirror suffices even if another literal has an at-row."
  },
  {
    "id": "h05-triage-d8-13-literal-no-threshold",
    "policy": "data-request-intake-triage",
    "defect": "D8-13",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 0, "max": 0},
    "structure": "S5",
    "reason": "The embargoed candidate changes from forced decline-redirect to unresolved with exception-escalation. This pack contains no ordered comparison, so a caught ledger cannot carry the threshold signature."
  },
  {
    "id": "h06-sanctions-d4-04-literal-two-sides",
    "policy": "sanctions-screening",
    "defect": "D4-04",
    "stratum": "literal",
    "endpoint": "lineMovedWhenCaught",
    "expected": {"min": 0, "max": 0},
    "structure": "S6",
    "reason": "Reversing matchCount >= 1 to <= 1 makes the present-evidence candidate at 0 conflict and the candidate at 2 yield no-match. Both sides of the retained boundary 1 disagree, while 1 itself is unchanged; the signature is absent."
  },
  {
    "id": "h07-triage-d6-05-random-20-catch",
    "policy": "data-request-intake-triage",
    "defect": "D6-05",
    "stratum": "random",
    "n": 20,
    "endpoint": "caught",
    "expected": {"min": 0.25, "max": 0.75},
    "structure": "S2/S6",
    "reason": "Removing appropriateness=pass permits proceed on complete, non-embargoed requests with both required evidence items present and appropriateness hard-fail, pending, not-evaluable, or an outside value. Those cases change from decline, clarify, or fallback to conflict or proceed. Their per-row probability is (1/3)*(1/2)*(1/4)*(4/5)=1/30, giving ledger catch probability 1-(29/30)^20, approximately 0.4924. The interval predicts the observed fraction of thirty ledgers; it is not a structural certainty."
  },
  {
    "id": "h08-vendor-d6-04-random-20-catch",
    "policy": "vendor-onboarding",
    "defect": "D6-04",
    "stratum": "random",
    "n": 20,
    "endpoint": "caught",
    "expected": {"min": 0, "max": 0.25},
    "structure": "S5",
    "reason": "Dropping sanctions status=clear changes only complete, tax-received cases below 250000 with both required evidence items present and an outside-domain status. A match is still forced to reject and a clear status is unchanged. Under the registered generator this event has probability approximately (1/3)^3*(1/2)*(1/4)=1/216 per row, giving approximately 0.0886 catch probability at n=20. The interval predicts the observed fraction of thirty ledgers."
  }
]
```

## Round 1 — maintainer disposition

Every finding is applied; the reviewer's eight holdout cells are placed byte-for-byte in
`harness/MATRIX-HOLDOUT.json` (a top-level array, which the scorer now loads as such).

| # | Severity | Disposition |
|---|---|---|
| 1 | BLOCKER | **Applied.** The scorer now requires, per policy, a defect index with no dropped instance, a cell for every valid instance against every ledger, a gate record covering every ledger with a clean verdict, and the exact registered ledger set for a REGISTERED attempt; a registered cell whose complete ledger set is not present is `unobserved`, and any unobserved cell makes the decision `pipeline-invalid`; `allowsNoCaught` holds only over the complete set with none caught; G3 is executed by the scorer (one random ledger per policy rebuilt under the pinned runtime and compared byte for byte) and recorded; `replay()` fails the construction on a replay that reaches no verdict or reads fewer rows than the ledger holds; `random_ledger()` raises on refusal exhaustion instead of returning a short ledger. §7 says all of this. |
| 2 | BLOCKER | **Applied.** The scorer hashes the preregistration, the matrix, the holdout and the manifest against their pins where filled and refuses a mismatch, recomputes the manifest against the tree, requires a non-null and matching runtime digest for REGISTERED, requires `--include-holdout` with a non-empty holdout for REGISTERED, and refuses `--include-holdout` on an empty file; the runner records the runtime's version and digest in `ATTEMPT.json` when the ledgers are built. A holdout given as a top-level array loads as cells, so the reviewer's bytes stand unchanged. §2 says so. |
| 3 | BLOCKER | **Applied.** `harness/run_attempt.py` is the one governing command: it creates the root exclusively (an existing root is refused, whatever it holds), writes `ATTEMPT.json` before anything else, builds with `--reserved`, plants, replays with the gate, and scores with the holdout. The builder refuses seeds 101–130 without `--reserved` and refuses `--reserved` with any other seed set; the scorer requires exactly that seed set at every n for REGISTERED. The governing invocation in the preregistration is the runner. |
| 4 | MAJOR | **Applied.** The generator draws discrete-uniform over the lattice at the literal's precision, so a lattice value has probability exactly 1/(2L+1) in units; §3 says so, and the affected reasons are rewritten with the correct arithmetic (`expense-approval` D6-03: about 0.063 per row, 0.96 at n = 50; the sanctions cells now state the evidence factor). |
| 5 | MAJOR | **Applied.** `sanctions-screening` D4-04 and D5-06 register [0, 0.1] with the stated per-ledger probability of an all-one-side catch; `vendor-onboarding` D8-23 registers [0.95, 1] with the at-row probability; S7 and §5 now say the one-side condition is existential over the pointer's literals, and D2-17's reason names the retained 250000 guard. |
| 6 | MAJOR | **Applied.** The signature table's denominator is every caught cell, a caught cell without a threshold counts as carrying none and is counted separately as threshold-free; R2 says so. |
| 7 | MAJOR | **Applied.** Exact Clopper–Pearson intervals are reported per instance (thirty independent seeded ledgers at one n); class-level pooling reports a reference interval with no nominal coverage claim, labelled as such in the file and in R2. |
| 8 | MAJOR | **Applied.** §3 describes the overlay: sparse candidates on the base row, the absence candidate a duplicate of the base, fact absence and `onUnknown` paths outside this stratum. Outcomes unchanged. |
| 9 | MAJOR | **Applied.** §5 adds the placement condition — every mismatched row placed on the pointer — and the signature implements it (`signature(profile, mismatched)`); a harness test holds an unplaced mismatch to no signature. |
| 10 | MAJOR | **Applied.** The three `expense-approval` D7 literal reasons now say deny → fallback review. |

Further notes taken: the "Nothing has run" banner is time-qualified to the freeze commit; the generator's pooling of applicability and rule literals for a shared pointer is stated as a bound of the generator in §3; the random-ledger determinism test now also asserts no `not-applicable` row for a pack with an applicability condition.

### After round 1 — a pilot check of the corrected generator (maintainer note)

The harness was re-run as a pilot under the corrected generator (`pilots/r2`, seeds 1–30, labelled PILOT, supporting no claim). Every gate held, every holdout cell held, and one registered cell diverged: `expense-approval/D7-01/random-50/lineMovedWhenCaught`, registered [0, 0.1], observed 0.2. The registration's reason was right about the mechanism (the changed cases sit on both sides of 75) and wrong about the count: only a receipted case changes, so a ledger of 50 changes about six rows, and with so few rows all on one side happens by chance — about 0.08 of caught ledgers from the generator's arithmetic, whose observed fraction over thirty ledgers runs to 0.2 one time in a hundred. The three `expense-approval` D7 cells and D4-09, which share that count, now register [0, 0.35] with the computed probability in their reasons; D5-13, whose changed rows number about nineteen, keeps [0, 0.1]. The correction is to the derivation, not to the pilot's number, and is recorded here rather than silently.

## Round 2 — 2026-09-14

Reviewer: codex-cli 0.153.4, model gpt-6-astra (OpenAI), read-only sandbox, on worktree commit `8c06202a`; different vendor than the model that drafted (Claude). Verdict: **not freezable as written** (3 BLOCKER, 3 MAJOR, 1 MINOR); the round-1 fixes audited, four closed and six partial; the eight holdout cells confirmed valid under the corrected generator.

> Note: the reviewer's worktree paths are normalized here. The finding prose is otherwise verbatim.

### Round 2 — prompt (verbatim)

```
You are the pre-freeze cross-vendor reviewer for Study 021 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 2. Round 1 (recorded verbatim with the maintainer's disposition in studies/021-history-replay-catch/PREREG-REVIEW.md) returned three blockers and seven majors, all applied in the commit under review (`git log -1`), and authored eight holdout cells, now placed byte-for-byte as a top-level array in harness/MATRIX-HOLDOUT.json.

First, verify each round-1 fix against the harness and the registration: say per finding whether the edit makes the registration true and enforceable, and whether it introduced a new defect. In particular: run `python -m unittest discover -s harness/tests` from the study directory (the pinned runtime is not available to you, so the two ledger tests skip; say so); read harness/score.py end to end for any path that still reaches "R1 holds" without complete observations, executed gates, matching pins and the reserved ledger set; read harness/run_attempt.py for the exclusive root and the marker; read harness/build_ledgers.py for the discrete-uniform draw, the not-applicable drop, the refusal-exhaustion failure and the reserved-seed guard; read harness/replay.py for the placement condition and the verdict check. Then re-read PREREGISTRATION.md and harness/MATRIX.json whole for anything round 1 missed, and check that every cell the round-1 disposition says was changed (expense-approval D7-00/01/02 reasons and D6-03; sanctions-screening D4-04, D5-06, D3-03 and the six random caught cells; vendor-onboarding D8-23 and D2-17) reads as the disposition says. Verify your own holdout cells still fit the schema the scorer loads and that their reasons survive the corrected generator (discrete-uniform: sanctions {0,1,2} at one third each; expense lattice of 151 values; vendor lattice of 500001).

The study directory is studies/021-history-replay-catch/ of the current worktree; the spec and runtime checkouts are at /home/onword/repo/judgment-pack/judgment-pack-spec and /home/onword/repo/judgment-pack/judgment-pack-runtime, read via `git -C <path> show origin/main:<file>`.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
```

### Round 2 — findings (verbatim)

**Verdict: `not freezable as written`.** Round 1’s empty-observation failure is closed, but a scorer path still permits `REGISTERED: R1 holds` with incomplete observations and mismatching attempt provenance.

I reviewed commit `8c06202a4c673c3d80a71443ddd1529880e11d52`, all requested harness files, the complete registration and matrix, Core §§7–8 at spec `origin/main` `587ebc5e…`, and runtime sources/ADRs at `origin/main` `0c8a4b63…`.

The requested unittest command ran from the study directory: **19 passed, 2 skipped, 2 errored**. The two ledger tests skipped because the pinned runtime is unavailable. Both errors came from `tempfile.mkdtemp()` in the read-only sandbox; those two tests passed when I substituted an existing directory for that fixture, without changing files. The 21-file manifest matches, and the freeze-set checker reports no problems. No primary attempt, runtime evaluations, or reserved draws ran; the worktree remains unchanged.

The round-1 dispositions resolve as follows:

| R1 finding | Verification against registration and implementation | New defect introduced? |
|---|---|---|
| **1 — BLOCKER: observations/gates** | **Partial.** Empty/missing observations now fail; `allowsNoCaught` requires 30 records; G3 executes. Replay rejects missing verdicts and short reads; refusal exhaustion raises. However, record counts do not establish unique observations, valid replay records, or retained inputs. Finding 1 below remains blocking. | No new defect in the replay/exhaustion changes; scorer enforcement remains incomplete. |
| **2 — BLOCKER: pins/holdout** | **Partial.** Current artifact hashes and manifest contents are checked; nonempty holdout participation and runtime digest are required for the registered label. The bare array loads correctly. Production identity is recorded but never checked against scoring identity. | The new marker is accepted by existence alone; finding 2. |
| **3 — BLOCKER: attempt/seeds** | **Partial.** The runner exclusively creates the root and refuses reuse. Builder seed-range checks work. Neither runner provenance nor a pinned registered configuration is required to consume reserved seeds. | The new default runner can consume reserved seeds with null pins; finding 3. |
| **4 — MAJOR: distribution** | **Partial.** The three numeric domains now use the correct discrete-uniform draws. Expense D6-03 is corrected. Two sanctions catch derivations remain wrong. | Yes: the shared replacement reason incorrectly assigns the one-value probability to two-value mutations. |
| **5 — MAJOR: signature predictions** | **Partial.** The three intervals changed as promised, and §5 correctly states the existential literal condition. §6 still contains the rejected generalizations. | Vendor D8-23’s new per-ledger probability is wrong. |
| **6 — MAJOR: denominator** | **Closed.** Both instance and class signature tables use every caught cell; threshold-free catches count as zero and are separately counted. | None found. |
| **7 — MAJOR: intervals** | **Partial.** Random per-instance intervals and pooled reference intervals are distinguished correctly. Deterministic literal results still receive `ci95exact`. | The literal-stratum defect remains. |
| **8 — MAJOR: absence overlay** | **Closed.** §3 now accurately describes the overlay, baseline duplicate, and excluded fact-absence coverage. | None found. |
| **9 — MAJOR: placement** | **Closed.** `signature(profile, mismatched)` requires complete placement and preserves the existential test across literals. This agrees with ADR-0034’s comparable-value buckets. | None found. |
| **10 — MAJOR: expense reasons** | **Closed.** All three literal D7 reasons now correctly say deny → fallback review. | None found. |

The remaining findings are:

1. **BLOCKER — counts still substitute for complete, valid observations.**

   **Exact commitment:** §7: “every valid instance has a cell against every ledger,” with missing observations making the result pipeline-invalid.

   **Implementation:** [score.py](<worktree>/studies/021-history-replay-catch/harness/score.py:180), especially lines 190–218, checks the union of ledger names, defect sets, and total counts. It never requires each `(defect, ledger)` pair exactly once. `observe()` likewise counts records, not distinct seeds. The scorer does not validate mutant replay `status`, `rows`, or `mismatched`; G1 even accepts an absent mismatch count. It checks no ledger inputs beyond G3’s four selected files, and trusts the supplied index rather than checking it against the planter’s complete expected instances.

   **Reproduction:** replacing expense D7-00’s `random-50-130` record with a second `random-50-129` left `gate_checks(..., registered=True)` empty and made its complete-set `allowsNoCaught` adjudication hold.

   A separate in-memory test of the real scoring/adjudication code returned:

   ```text
   REGISTERED: R1 holds (131 registered cells, 0 diverge, 0 gate failures)
   ```

   Its synthetic records had failed replay statuses, zero row counts, absent G1 mismatch counts, a duplicate pair, only four retained ledger inputs, and a mismatching marker. Runtime calls used by G3 were mocked; this demonstrates scorer acceptance, not a study result.

   **Smallest sufficient edit:** validate the exact four-policy set, canonical defect index, unique defect–ledger Cartesian product, every corresponding input and required row count, and complete internally consistent replay/G1 records before aggregation or adjudication. Reject missing or malformed evidence as pipeline-invalid.

2. **BLOCKER — matching current pins do not establish matching production pins.**

   **Exact commitment:** §2 says pins are enforced and that the runner records runtime identity “when the ledgers are built, not only when they are scored.”

   **Implementation:** `score.py:267` tests only `(root / "ATTEMPT.json").exists()`. It never parses the marker’s runtime digest, raw pins digest, label, seeds, sizes, or policies. [run_attempt.py:42](<worktree>/studies/021-history-replay-catch/harness/run_attempt.py:42) records these fields, but they have no enforcement effect.

   The adversarial marker explicitly said `PILOT`, seeds `[1,30]`, and wrong runtime/pins digests; the scorer still labelled the supplied records `REGISTERED`. Current artifact-hash checks were retained in that probe.

   **Smallest edit:** require and validate the marker’s schema and configuration; compare its runtime and raw pins digests with the current pinned identities; bind the generated inputs and replay records to that attempt. A production-identity mismatch must refuse registered adjudication.

3. **BLOCKER — reserved seeds remain accessible outside a registered attempt.**

   **Exact sentence:** §3 says seeds 101–130 are those “which the builder refuses outside the runner.”

   **Implementation:** [build_ledgers.py:198](<worktree>/studies/021-history-replay-catch/harness/build_ledgers.py:198) requires only `--reserved` plus the correct range. An arbitrary output root needs no marker. An in-memory probe reached construction with exactly that configuration and no runner provenance. Existing output files can also be overwritten.

   Separately, the default runner selects reserved seeds before validating any pins. With the currently null pins, it can consume the holdout seeds and only subsequently obtain a PILOT label.

   **Smallest edit:** make reserved construction require a validated active registered-attempt context; check complete matching pins before any reserved draw; reject existing generated outputs. Keep exclusive root creation. The current flags alone do not implement the stated reservation.

4. **MAJOR — deterministic literal results still carry an exact-binomial coverage claim.**

   **Exact commitment:** R2 promises exact intervals “per stratum,” justified because an instance has thirty independently seeded ledgers.

   **Implementation:** `score.py:123–130` emits `ci95exact` for `literal` as well as `random`. A literal threshold-free catch produces `ci95exact: [0.0, 0.975]` for its signature. That single deterministic ledger is not the repeated random experiment used by the justification.

   **Smallest edit:** restrict exact intervals to random, per-instance results at a fixed n. Publish literal counts/rates descriptively, and explicitly qualify R2.

5. **MAJOR — §6 still states generalizations that the corrected cells reject.**

   **Exact locations in [PREREGISTRATION.md](<worktree>/studies/021-history-replay-catch/PREREGISTRATION.md:235):**

   - S5, lines 243–245: a site whose changed cases include the literal “registers **signature = 0**.”
   - S6, lines 250–255: two-sided sites have random signature rate “[0, 0.1]”.
   - S7, lines 256–262: landing at the new literal “breaks the signature.”

   **Source comparison:** possible changed cases are not necessarily observed cases; the expense D7/D4 matrix now permits `[0,0.35]`; and vendor D2-17 can retain its signature despite an observed at-row at 187500 because 250000 also qualifies. §5 now explains that last point correctly, but S7 does not contain the qualification claimed by the disposition.

   **Smallest edit:** distinguish support-level statements from finite-ledger predictions, give the policy-specific intervals, and say an at-row defeats the signature only when no other literal qualifies.

6. **MAJOR — several numerical reasons remain incorrect.**

   These are exact cells in [MATRIX.json](<worktree>/studies/021-history-replay-catch/harness/MATRIX.json:1496):

   | Cell / location | What it says | Source-derived correction and smallest edit |
   |---|---|---|
   | Sanctions D4-04 and D5-06, `random-50/caught`, IDs at lines 1496 and 1526 | Catch probability `1-(5/6)^50` | D4 changes `{0,2}`; D5 changes `{1,2}`. With present evidence, each union has per-row probability **1/3**, giving **`1-(2/3)^50`**. Replace those two reasons; `[0.9,1]` can remain. |
   | Vendor D8-23, `random-50/lineMovedWhenCaught`, ID at line 653 | At-row probability means “about one ledger in three hundred” | Per ledger it is **`1-(500000/500001)^50 ≈ 0.000100`**, about **one in 10,000**. Approximately 0.003 is the probability across thirty ledgers. Correct the unit; `[0.95,1]` can remain. |
   | Expense D2-07, `random-50/lineMovedWhenCaught`, ID at line 971 | An at-56 draw occurs in “about a quarter of ledgers” and changes there | A changed at-row also requires permitted category and receipt: **1/1208 per row**, giving **0.04056 per ledger**. Conditional signature probability is approximately **0.92590**. State those restrictions; `[0.5,1]` can remain. |

7. **MINOR — a few descriptions still name the wrong actor, boundary, or outcome.**

   - Registration line 32 says **“the scorer refuses an existing root.”** The runner does; the scorer refuses an existing adjudication. Replace “scorer” with “runner.”
   - Vendor D4-14’s literal reason says its reversed guard fires **“at and above 250000.”** D4 changes `<` to `>`. Replace with “strictly above.”
   - Vendor D4-19’s reasons include the at-row among changes. Reversing `>=` to `<=` leaves equality true in both packs. State that the at-row is unchanged.
   - S5 calls sanctions literal 1 **“reimbursed.”** Its outcome is `match`; correct the word.

I also checked every specifically named matrix edit:

| Requested cells | Result |
|---|---|
| Expense D7-00/01/02 literal reasons | All correctly say deny → fallback review. |
| Expense D6-03 | Correct literal mechanism; random per-row probability **76/1208 = 0.062914**, catch probability **0.961187**. |
| Sanctions D4-04 and D5-06 signatures | Both now `[0,0.1]`; conditional signature probabilities are approximately **0.00021977** and **0.00010988**, consistent with their approximate reasons. |
| Sanctions D3-03 catch | Correctly includes evidence: **1/6 per row**, `1-(5/6)^50`. |
| Six sanctions random caught cells | All received the promised text. Four are correct; D4-04 and D5-06 need finding 6’s correction. |
| Vendor D8-23 | Interval changed as promised; per-ledger arithmetic needs correction. |
| Vendor D2-17 | Retained-250000 explanation is sound; exact signature expectation survives the at-row. |
| Additional post-pilot expense edits | D7-00/01/02 and D4-09 now use `[0,0.35]`. Their conditional signature probabilities are approximately **0.07520** and **0.07859**, supporting “about 0.08.” |

Finally, all eight holdout cells remain valid. The file is **byte-for-byte identical** to the review’s JSON array, all IDs and combinations are unique, every defect exists, and all fields fit `load_matrix()` and adjudication.

| Holdout | Reason audit |
|---|---|
| h01 | Deny → review at base amount 42.50; signature present. |
| h02 | Amount guard removed; caught with no threshold. |
| h03 | Changed literal at-row at 250000 prevents the signature. |
| h04 | Retained 250000 boundary establishes the signature. |
| h05 | Embargo exception changes the disposition; no ordered threshold exists. |
| h06 | Changed zero and two cases occupy both sides; no signature. |
| h07 | Unaffected by numeric-lattice correction: per-row **1/30**, n=20 catch probability **0.492385**. |
| h08 | Vendor lattice gives per-row **`(1/108) × (250000/500001)`**, n=20 catch probability **0.088631**. |

The generator now uses inclusive integer draws over **0–2**, **0–150**, and **0–500000**, so the holdout derivations survive the corrected sanctions, expense, and vendor distributions without edits.

### Round 2 — maintainer disposition

Every finding is applied.

| # | Severity | Disposition |
|---|---|---|
| 1 | BLOCKER | **Applied.** The scorer loads the records only through `evidence()`: the four policies exactly; each defect index equal to the planter's canonical instance set (recomputed from the vendored pack) with every instance valid; every registered ledger present with its row count and no unregistered one; the gate record covering every ledger exactly once, `passed` with zero mismatches, bound to the ledger's bytes and to the policy pack's; the cells exactly the Cartesian product of valid instances and ledgers with no pair twice, each bound by digest to its ledger and its defect pack, each with a verdict, a row count equal to the ledger's, a mismatch count within it and `caught` equal to `mismatched > 0`. Anything short is named and the decision is pipeline-invalid. `observe()` counts distinct ledgers. |
| 2 | BLOCKER | **Applied.** The marker is parsed and matched — label, runtime digest against the scorer's runtime and the pin, pins digest against the current `harness/PINS.json`, seeds, sizes, policies, a 32-hex attempt id — and a registered adjudication refuses on any mismatch rather than falling back to PILOT; a pilot adjudication requires a `PILOT` marker. Every record carries the attempt id (`attemptId` in the index, the gate record and the cells) and `evidence()` holds it. |
| 3 | BLOCKER | **Applied.** `--reserved` is allowed only when the output root holds a valid `REGISTERED` marker under complete, matching pins (`attempt.registered_context_problems`); the runner holds the pins before creating a registered root, so no reserved seed is drawn under a null pin, and a pilot marker says `PILOT` with seeds 1–30. Ledger, defect and record files are opened for exclusive creation and never overwritten. |
| 4 | MAJOR | **Applied.** The literal stratum reports counts and rates with no interval; exact intervals are emitted for random per-instance results only; R2 says so. |
| 5 | MAJOR | **Applied.** S5, S6 and S7 now distinguish the support of the changed cases from the finite-ledger prediction, give the policy-specific intervals, and say an at-row defeats the signature only when no other literal of the pointer qualifies (`vendor-onboarding` D2-17 named). |
| 6 | MAJOR | **Applied.** `sanctions-screening` D4-04 and D5-06 catch reasons say one third per row and 1 − (2/3)^50; `vendor-onboarding` D8-23 says about one ledger in ten thousand and about 0.003 over thirty; `expense-approval` D2-07 states the permitted-and-receipted restriction (1/1208 per row, about 0.04 of ledgers) and the resulting 0.93. |
| 7 | MINOR | **Applied.** "Runner" refuses an existing root; D4-14 fires strictly above 250000; D4-19's reasons say the at-row is unchanged; S5 says the literal 1 is matched. |

## Round 3 — 2026-09-14

Reviewer: codex-cli 0.153.4, model gpt-6-astra (OpenAI), read-only sandbox, on worktree commit `9fe2d6bb`; different vendor than the model that drafted (Claude). Verdict: **not freezable as written** (2 BLOCKER, 1 MAJOR, 4 MINOR); the round-2 fixes audited, the pin, marker and reserved-seed bypasses confirmed closed; the holdout confirmed byte-for-byte.

> Note: the reviewer's worktree paths are normalized here. The finding prose is otherwise verbatim.

### Round 3 — prompt (verbatim)

```
You are the pre-freeze cross-vendor reviewer for Study 021 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 3 on commit 9fe2d6bb (`git log -1`). Rounds 1 and 2 (recorded verbatim with the maintainer's dispositions in studies/021-history-replay-catch/PREREG-REVIEW.md) returned six blockers and ten majors in all, every one applied; round 1 authored eight holdout cells, placed byte-for-byte as a top-level array in harness/MATRIX-HOLDOUT.json.

First, verify each round-2 fix against the harness and the registration — in particular harness/attempt.py (the marker and pin checks), score.py's evidence() (the complete, unique, bound record set), run_attempt.py (pins held before a registered root; the attempt id; the stamps), build_ledgers.py (reserved draws under a validated registered context; outputs written once), replay.py (digest binding), and the changed matrix reasons and §6 structures. Say per round-2 finding whether the edit makes the registration true and enforceable, and whether it introduced a new defect. Then say per finding whether the edit makes the registration true and enforceable, and whether it introduced a new defect. In particular: run `python -m unittest discover -s harness/tests` from the study directory (the pinned runtime is not available to you, so the two ledger tests skip; say so); read harness/score.py end to end for any path that still reaches "R1 holds" without complete observations, executed gates, matching pins and the reserved ledger set; read harness/run_attempt.py for the exclusive root and the marker; read harness/build_ledgers.py for the discrete-uniform draw, the not-applicable drop, the refusal-exhaustion failure and the reserved-seed guard; read harness/replay.py for the placement condition and the verdict check. re-read PREREGISTRATION.md and harness/MATRIX.json whole for anything the earlier rounds missed. If nothing that would let a favourable outcome be reached for the wrong reason remains, say so plainly and return `freezable as written`; note that the runtime pin (harness/PINS.json jpack.sha256) is null by design until the runtime's v0.21.0 release publishes, and the freeze pins are filled at the freeze commit — say whether anything in the design depends on their being filled earlier. Verify your own holdout cells still fit the schema the scorer loads and that their reasons survive the corrected generator (discrete-uniform: sanctions {0,1,2} at one third each; expense lattice of 151 values; vendor lattice of 500001).

The study directory is studies/021-history-replay-catch/ of the current worktree; the spec and runtime checkouts are at /home/onword/repo/judgment-pack/judgment-pack-spec and /home/onword/repo/judgment-pack/judgment-pack-runtime, read via `git -C <path> show origin/main:<file>`.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
```

### Round 3 — findings (verbatim)

**Verdict: `not freezable as written`.** The round-2 changes close the pin, marker and reserved-seed bypasses, but the scorer still accepts incomplete signature evidence and inputs that do not implement the registered experiment.

I reviewed commit `9fe2d6bbc5c09805ad8ce64c56b1d309fd4dd02f`, the complete registration and both matrices, and all harness sources. Source comparisons used spec `origin/main` at `587ebc5e…` and runtime `origin/main` at `0c8a4b63…`, through the requested `git show` commands.

The requested unittest command ran from the study directory: **21 passed, 2 skipped, 4 errored**. The two ledger tests skipped because the pinned runtime is unavailable. All four errors arose at `tempfile.mkdtemp()` because the sandbox is read-only. The interpreter here is CPython 3.8.20, not the registered 3.12. The 22-file manifest matches; the freeze-set checker reports zero problems. No primary attempt, runtime evaluation or reserved draw ran. Files remain unchanged.

The round-2 findings resolve as follows:

| Round-2 finding | Does the edit make the registration true and enforceable? | New defect introduced? |
|---|---|---|
| **1 — BLOCKER: complete observations** | **Partial.** Unique defect–ledger pairs, retained random-ledger counts, canonical index metadata, G1 coverage, digests and attempt stamps are checked. Signature completeness and registered input construction remain insufficiently checked. | The new failure branch also misclassifies incomplete evidence; finding 3 below. |
| **2 — BLOCKER: production pins** | **Closed for provenance.** Runtime and raw pins digests, label, policies, sizes and seeds are matched before scoring. A mismatch refuses registered adjudication. Index, gate and cell-file envelopes must carry the matching attempt ID. | Minor new validation discrepancy: the claimed hexadecimal ID check only checks length. |
| **3 — BLOCKER: reserved seeds** | **Closed for reserved construction.** Pins are checked before exclusive root creation; the builder requires a matching registered context; ledger, mutant and replay-record files use exclusive creation. | No new seed defect found. The broader promise that *every output* is written once remains unenforced for scorer outputs. |
| **4 — MAJOR: literal intervals** | **Exact-coverage defect closed; prose only partially implemented.** Literal per-instance intervals are null, but pooled literal reference intervals remain. | No new coverage claim; a residual reporting discrepancy remains. |
| **5 — MAJOR: §6 generalizations** | **Substantially corrected.** Support and finite-ledger predictions are distinguished; expense intervals and the retained vendor literal are explained. | S5 newly groups sanctions D2 under `[0,0.1]`, contradicting its exact-zero matrix cell and S7. |
| **6 — MAJOR: numerical reasons** | **Closed.** Both sanctions unions use `1−(2/3)^50`; vendor D8-23 distinguishes per-ledger and thirty-ledger probabilities; expense D2-07 includes permitted category and receipt. | None found. |
| **7 — MINOR: actor/boundary/outcome wording** | The requested replacements were applied. The vendor D4-19 random reason still overstates the resulting outcome. | No new endpoint defect; residual wording is detailed below. |

The remaining findings are:

1. **BLOCKER — missing signature observations can still count as observed zero.**

   **Exact implementation:** [score.py:273](<worktree>/studies/021-history-replay-catch/harness/score.py:273) requires a signature dictionary and Boolean `applicable`, but does not require or validate `lineMoved`, `placed` or the supporting counts. Line 166 treats a missing `lineMoved` as false. Meanwhile, `replay.py:43–44,73` converts a missing profile into `{"applicable": false}`.

   **Source:** §§5 and 7 require the signature to be observed from the profile and missing observations to invalidate the pipeline. ADR-0034 provides a profile when rows declare origins; these generated rows do.

   **Reproduction:** In memory, I replaced all thirty sanctions D3-03/random-50 signatures in retained pilot records with `{"applicable": true}`. `evidence()` returned **no failures**, and adjudication returned **131/131 holds**, including observed signature rate zero for that cell. Separately, the real replay adapter accepted a mocked mismatch report with no profile as a threshold-free catch.

   **Smallest sufficient edit:** require the expected profile and its complete signature evidence; validate Boolean results and counts; recompute the signature from retained evidence. Missing profile data must not mean “no threshold.” Also enforce status/count consistency: the present checks accept `passed` with positive mismatches and `mismatch` with zero.

2. **BLOCKER — digest binding does not establish that the inputs are the registered inputs.**

   **Exact implementation:** `score.py:185–188` recomputes only mutant **metadata**, discarding the expected mutated document. Lines 272–278 accept whichever pack occupies that filename when its recorded digest matches. Lines 229–233 require only that the literal ledger be nonempty.

   **Source:** §4 registers a particular mechanical edit at each site; §3 registers the complete literal candidate construction, including evidence-present/absent/unknown probes.

   **Two independent in-memory reproductions:**

   - Replacing vendor `D1-11.pack.json` with the **unplanted original**, and updating its recorded digest, produced no evidence failures and **131/131 holds**. This masked defect’s registered nondetection therefore succeeds without the registered defect being present.
   - Removing expense’s absent-receipt and unknown-receipt literal probes, updating row counts and digests, likewise produced no failures and **131/131 holds**. The ledger had 15 rows instead of 17.

   These probes used retained pilot data; they are scorer acceptance demonstrations, not study results.

   **Smallest sufficient edit:** compare each retained mutant with its corresponding document from `plant.instances()`. Rebuild and compare each literal ledger, or validate an equivalently complete registered candidate set. Matching a file’s digest and accepting any positive literal row count are insufficient.

3. **MAJOR — incomplete evidence is classified as a control failure and aggregated.**

   **Exact implementation:** `score.py:329–332` chooses `control-gate-failed` whenever all four policy dictionaries exist, even when `evidence()` reports missing observations, and then calls `aggregate()`.

   **Source:** §7 gives pipeline invalidity precedence for incomplete observations. The scorer’s own lines 23–26 promise the same.

   **Reproduction:** Removing one expense replay record produced `control-gate-failed` and attempted to write both aggregate files. Output writes were intercepted in memory.

   **Smallest edit:** distinguish evidence-validity failures from executed control failures. Missing, duplicate, malformed or unbound evidence must produce `pipeline-invalid` before aggregation or endpoint adjudication.

4. **MINOR — pooled literal intervals contradict the revised exclusion.**

   **Exact implementation:** `score.py:142,147` still calculates `referenceInterval` for literal class aggregates.

   **Source:** R2, registration lines 79–88, specifies literal counts and rates with **“no interval”**, including the signature table.

   A deterministic threshold-free catch still produces a pooled signature interval `[0.0, 0.975]`. It is now explicitly a reference interval without coverage, so the original exact-coverage error is resolved.

   **Smallest edit:** apply the `stratum == "random"` condition to both pooled interval calculations.

5. **MINOR — scorer outputs can still be overwritten.**

   **Exact sentence:** registration lines 48–49: **“an output is written once and never overwritten.”**

   **Implementation:** `score.py:347–351` uses `write_text()`. Existing aggregate files are overwritten when no adjudication exists—for example, after a crash between aggregate publication and adjudication.

   **Smallest edit:** use exclusive creation for all three scorer outputs. The runner’s exclusive root and the builder/planter/replayer’s exclusive writes are otherwise correctly implemented.

6. **MINOR — the attempt-ID check does not enforce hexadecimal format.**

   **Exact implementation:** [attempt.py:92](<worktree>/studies/021-history-replay-catch/harness/attempt.py:92) checks string type and length, while its error and the round-2 disposition promise a **“32-hex”** token.

   A matching marker with `"z" * 32` returns no problems. The runner itself correctly generates hexadecimal IDs.

   **Smallest edit:** validate against `[0-9a-f]{32}`.

7. **MINOR — three remaining prose discrepancies.**

   | Exact location/text | What the source establishes | Smallest edit |
   |---|---|---|
   | Registration S5, line 260, groups sanctions D2 with `[0,0.1]` | Its changed cases all sit at zero; S7 and `sanctions-screening/D2-02/random-50/lineMovedWhenCaught` correctly specify `[0,0]`. | Separate D2’s exact-zero statement from D5-06’s finite-ledger interval. |
   | `MATRIX.json:744`, vendor D4-19/random-50/signature: **“above it every case falls to request-info”** | Under Core §§8–8.3, present-evidence matches can instead be forced to reject; missing-evidence cases remain unresolved. Adding/removing `exception-escalation` can itself change the full disposition. | Describe the added/removed escalation reason and conditional outcomes; retain the unchanged-at-row statement and interval. |
   | `PINS.json:3`: **“any null makes it a PILOT”** | The revised runner/scorer refuse registered execution with null pins. Pilot execution requires the explicit pilot mode and matching marker. | Replace the automatic-demotion description with the actual refusal rule. |

The corrected generator uses inclusive `randint` bounds **0–2**, **0–150** and **0–500000**, giving the requested uniform lattices. In-memory checks confirmed not-applicable redraws and failure after refusal exhaustion. The replay’s complete-placement and existential-literal calculation agrees with §5 **when complete profile evidence is supplied**. G3 executes on the admissible scoring path and must succeed before “R1 holds”; the findings above concern evidence that incorrectly reaches that path.

All eight holdouts remain byte-for-byte identical to the round-1 array. They load correctly, name valid defects, and introduce no duplicate IDs or combinations: **123 main cells + 8 holdouts = 131 unique cells**.

| Holdout | Reason survives? |
|---|---|
| h01 | Yes: deny → review below 75; signature present. |
| h02 | Yes: amount guard removed; no threshold. |
| h03 | Yes: changed at-250000 row prevents the signature. |
| h04 | Yes: retained 250000 literal establishes one-sidedness. |
| h05 | Yes: embargo exception changes disposition; no threshold. |
| h06 | Yes: changed zero and two occupy both sides. |
| h07 | Yes: per-row probability `1/30`; n=20 catch probability **0.492385**. |
| h08 | Yes: per-row probability `(1/108) × (250000/500001)`; n=20 catch probability **0.088631**. |

The intentionally null runtime digest is **not a review blocker**. Nothing requires it, or the freeze hashes, to be filled earlier than their stated release/freeze milestones. Complete matching pins are required **before registered construction begins**. An in-memory check confirmed that null pins cause refusal before root creation or any child command.

**Final verdict: `not freezable as written`.** Findings 1–3 require correction; findings 4–7 identify the remaining smaller discrepancies.

### Round 3 — maintainer disposition

Every finding is applied.

| # | Severity | Disposition |
|---|---|---|
| 1 | BLOCKER | **Applied.** A replay whose report carries no profile fails the construction (`replay.signature` raises); a signature record carries the profile's threshold count and, where a threshold exists, the bucket counts per pointer and literal with the recorded `lineMoved` and `placed`; the scorer (`signature_evidence_ok`) requires the complete record and recomputes the verdict from the retained counts through the same rule (`replay.signature_from_buckets`), refusing any disagreement; `applicable: false` is accepted only with `thresholdEntries: 0` and nothing else. Status and count are held consistent (`mismatch` iff mismatched > 0) at replay and again at scoring. A note on the runtime's contract, found by the pilot that followed: the runtime omits the profile's `thresholds` member for a pack that draws no line (`omitempty`), so "no thresholds" is a legitimate report for such a pack and not missing evidence. The rule therefore reads the profile against the pack: `replay.expected_thresholds` counts the replayed pack's distinct (pointer, literal) ordered comparisons, the replay fails unless the profile reports exactly that many entries, and the scorer recomputes the expectation from the retained mutant and holds the record to it. |
| 2 | BLOCKER | **Applied.** `registered_inputs_ok` compares every retained mutant document with the planter's document for its site (JSON equality, not digest) and rebuilds every literal ledger under the pinned runtime, comparing bytes; a difference is a validity failure. §7 says so. |
| 3 | MAJOR | **Applied.** Validity is held first and any shortfall is `pipeline-invalid` with nothing aggregated or adjudicated; only the executed controls (G1 as bound clean gate records inside the validity check, G3 after it) produce `control-gate-failed`. The adjudication file records validity failures and gate failures separately. |
| 4 | MINOR | **Applied.** Pooled literal aggregates carry no interval, in both tables. |
| 5 | MINOR | **Applied.** The scorer's three files are opened for exclusive creation. |
| 6 | MINOR | **Applied.** The attempt id is held to `[0-9a-f]{32}`. |
| 7 | MINOR | **Applied.** S5 states `sanctions-screening` D2 as exactly 0 (as S7 and the cell do) apart from D5-06's interval; the D4-19 random reason describes the gained and lost escalation and the conditional outcomes above the line; the pins note states the refusal rule in place of an automatic demotion. |

## Round 4 — 2026-09-14

Reviewer: codex-cli 0.153.4, model gpt-6-astra (OpenAI), read-only sandbox, on worktree commit `b9eb0e6a`; different vendor than the model that drafted (Claude). Verdict: **not freezable as written** (2 BLOCKER, 1 MAJOR, 1 MINOR); the round-3 fixes audited, four closed, three partial; the holdout confirmed byte-for-byte.

> Note: the reviewer's worktree paths are normalized here. The finding prose is otherwise verbatim.

### Round 4 — prompt (verbatim)

```
You are the pre-freeze cross-vendor reviewer for Study 021 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 4 on commit b9eb0e6a (`git log -1`). Rounds 1 to 3 (recorded verbatim with the maintainer's dispositions in studies/021-history-replay-catch/PREREG-REVIEW.md) returned eight blockers, eleven majors and five minors in all, every one applied; round 1 authored eight holdout cells, placed byte-for-byte as a top-level array in harness/MATRIX-HOLDOUT.json.

First, verify each round-3 fix against the harness and the registration — in particular score.py's signature_evidence_ok (complete signature evidence recomputed from retained counts through replay.signature_from_buckets), registered_inputs_ok (every mutant compared with the planter's document, every literal ledger rebuilt), the validity-before-gates precedence in main(), the exclusive scorer outputs, the hexadecimal attempt id, and the three prose corrections. Say per round-3 finding whether the edit makes the registration true and enforceable, and whether it introduced a new defect. Then say per finding whether the edit makes the registration true and enforceable, and whether it introduced a new defect. In particular: run `python -m unittest discover -s harness/tests` from the study directory (the pinned runtime is not available to you, so the two ledger tests skip; say so); read harness/score.py end to end for any path that still reaches "R1 holds" without complete observations, executed gates, matching pins and the reserved ledger set; read harness/run_attempt.py for the exclusive root and the marker; read harness/build_ledgers.py for the discrete-uniform draw, the not-applicable drop, the refusal-exhaustion failure and the reserved-seed guard; read harness/replay.py for the placement condition and the verdict check. re-read PREREGISTRATION.md and harness/MATRIX.json whole for anything the earlier rounds missed. If nothing that would let a favourable outcome be reached for the wrong reason remains, say so plainly and return `freezable as written`; note that the runtime pin (harness/PINS.json jpack.sha256) is null by design until the runtime's v0.21.0 release publishes, and the freeze pins are filled at the freeze commit — say whether anything in the design depends on their being filled earlier. Verify your own holdout cells still fit the schema the scorer loads and that their reasons survive the corrected generator (discrete-uniform: sanctions {0,1,2} at one third each; expense lattice of 151 values; vendor lattice of 500001).

The study directory is studies/021-history-replay-catch/ of the current worktree; the spec and runtime checkouts are at /home/onword/repo/judgment-pack/judgment-pack-spec and /home/onword/repo/judgment-pack/judgment-pack-runtime, read via `git -C <path> show origin/main:<file>`.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
```

### Round 4 — findings (verbatim)

**Verdict: `not freezable as written`.** Two remaining acceptance gaps let incomplete signature evidence or substituted random replicates satisfy all 131 endpoints.

I reviewed commit `b9eb0e6aed54d4f6e1641b761932687a15283e10`, the complete registration and matrices, and every harness source. Source comparisons used the requested `git show origin/main:<file>` commands: spec `587ebc5e…`, runtime `0c8a4b63…`.

The requested unittest command ran from the study directory: **25 passed, 2 skipped, 4 errored**. The two ledger tests skipped because the pinned runtime is unavailable. All four errors occurred during temporary-directory creation in the read-only sandbox. This interpreter is CPython 3.8.20, not the registered 3.12. The 22-file manifest matches; the freeze-set checker reports zero problems. No runtime evaluation, primary attempt or reserved draw ran. Files remain unchanged.

The round-3 findings resolve as follows:

| Round-3 finding | Does the edit make the registration true and enforceable? | New defect introduced? |
|---|---|---|
| **1 — BLOCKER: signature evidence** | **Partial.** Missing profiles, incorrect threshold counts, missing flags and status/count contradictions are rejected. Flags are recomputed through `signature_from_buckets`, but retained bucket completeness and boundary identities remain unchecked. | The new checks are insufficient; the original missing-evidence failure survives. Finding 1 below. |
| **2 — BLOCKER: registered inputs** | **Closed for the reported mutant and literal-ledger substitutions.** Every mutant document is compared with `plant.instances()`; every literal ledger is rebuilt and compared byte-for-byte before aggregation. | None identified in those edits. Random-ledger provenance remains a separate gap, finding 2. |
| **3 — MAJOR: validity precedence** | **Partial.** Removing a replay record now produces `pipeline-invalid`, with no aggregation or endpoint adjudication. | **Yes:** completed G1 failures are now classified as pipeline invalidity. G2 failures have the same problem. Finding 3. |
| **4 — MINOR: literal intervals** | **Closed.** Both pooled literal tables now have null intervals, matching R2. | None found. |
| **5 — MINOR: exclusive scorer outputs** | **Closed.** All three output files use exclusive creation, `"x"`. | None found. |
| **6 — MINOR: hexadecimal ID** | **Closed.** Validation uses `re.fullmatch(r"[0-9a-f]{32}", …)`, matching `token_hex(16)`. | None found. |
| **7 — MINOR: three prose corrections** | S5’s sanctions D2 statement and the pins refusal note are corrected. Vendor D4-19 remains inaccurate. | **Yes:** its replacement reason newly permits `approve` above the unchanged approval boundary. Finding 4. |

The remaining findings are:

1. **BLOCKER — a declared threshold count still substitutes for complete threshold evidence.**

   **Exact commitment:** registration §7 requires “every signature record complete” and “the bucket counts per pointer and literal.” See [PREREGISTRATION.md:310](<worktree>/studies/021-history-replay-catch/PREREGISTRATION.md:310).

   **Implementation:** [score.py:195](<worktree>/studies/021-history-replay-catch/harness/score.py:195) checks the declared count but never reconciles it with the retained entries. An empty `disagreeing` dictionary passes when both flags are false. Pointer/literal identities are not compared with the mutant’s boundaries. Meanwhile, [replay.py:91](<worktree>/studies/021-history-replay-catch/harness/replay.py:91) accepts an empty `origins` array and sums it to zero.

   **Source:** runtime ADR-0034 reports each boundary against each declared origin. Its implementation retains those entries, including zero counts. All generated study rows declare origins.

   **Reproductions, entirely in memory:**

   - Removing the bucket evidence from all thirty sanctions D3-03/random-50 records, retaining `thresholdEntries: 1` and setting both flags false, produced **no `evidence()` failures and 131/131 endpoint holds**.
   - A record claiming two thresholds but retaining one entry at `/unrelated`, literal `999`, was accepted.
   - A profile containing the expected threshold but `origins: []` passed the replay adapter and scorer as a zero signature.

   **Smallest sufficient edit:** retain explicit evidence for every expected boundary, including zero-count entries; validate the exact boundary and origin sets and bounded counts before reducing them to the signature. Missing evidence must fail independently of whether its absence happens to produce the registered Boolean.

2. **BLOCKER — the scorer does not establish that random replicates came from their declared seeds.**

   **Exact commitments:** §2 specifies `random.Random("021:<policy>:<n>:<seed>")`; §3 requires thirty seeds; R2’s interval justification depends on independent replicate draws.

   **Implementation:** [score.py:270](<worktree>/studies/021-history-replay-catch/harness/score.py:270) checks filenames, row counts and matching digests. `registered_inputs_ok()` checks mutants and literal ledgers. [G3:342](<worktree>/studies/021-history-replay-catch/harness/score.py:342) rebuilds only the first n=5 ledger per policy.

   **Reproduction:** in memory, I replaced all thirty sanctions n=50 replicates with seed-1 facts, evidence and dispositions, assigning each recipient its correct row IDs and origins. The files therefore had **thirty distinct digests**. Matching donor replay observations and G1 bindings were supplied. `evidence()` returned **no failures**, and adjudication returned **131/131 holds**. Mutants, literal ledgers and every G3-selected input were untouched.

   This is an acceptance demonstration using pilot data, not evidence that actual reserved seeds were contaminated.

   **Smallest sufficient edit:** verify every retained random ledger against its declared seed’s construction. Rebuilding and comparing every random ledger under the pinned runtime is sufficient; checking labels or duplicate digests alone is not.

3. **MAJOR — executed G1/G2 failures are classified as pipeline invalidity.**

   **Exact commitment:** §7 distinguishes validity failures from control failures and explicitly says a nonempty dropped-mutant set “is a control failure.” See [PREREGISTRATION.md:301](<worktree>/studies/021-history-replay-catch/PREREGISTRATION.md:301).

   **Implementation:** `evidence()` puts both invalid-mutant results at line 266 and completed unplanted replay mismatches at line 298 into the same failures list. `main()` treats that entire list as validity failures.

   **Reproduction:** a complete, bound G1 record reporting `status: "mismatch", mismatched: 1` produced:

   ```json
   {
     "decision": "pipeline-invalid",
     "gateFailures": []
   }
   ```

   **Smallest edit:** separate malformed, missing or unbound evidence from completed control results. After validity passes, recorded G1 mismatches and properly documented G2 drops must produce `control-gate-failed`.

4. **MINOR — two vendor reasons still misdescribe the mechanism.**

   | Exact cell/text | What the source establishes | Smallest edit |
   |---|---|---|
   | D4-19/random-50/signature, [MATRIX.json:744](<worktree>/studies/021-history-replay-catch/harness/MATRIX.json:744): above the boundary, “approve, request-info, or reject” | D4-19 changes only the committee comparison. The approval rule still requires spend **strictly below 250000**, so approval above it is impossible. | Delete `approve` from the listed outcomes. |
   | D2-12/random-50/signature, [MATRIX.json:728](<worktree>/studies/021-history-replay-catch/harness/MATRIX.json:728): “the same band, above the new guard” | The changed band is `[187500,250000)`, including an at-row at the new guard. The retained committee boundary at 250000 establishes strict one-sidedness. | State that band and the retained-boundary explanation. |

   Both intervals can remain unchanged.

The remaining requested checks passed on inspection or isolated probes. The runner checks pins before exclusive root creation and writes its marker before construction. The CLI reserved-seed guard requires a validated registered context. The generator uses inclusive integer draws over **0–2, 0–150 and 0–500000**; not-applicable draws are redrawn, and refusal exhaustion raises rather than returning a short ledger. With complete evidence, the replay’s placement and existential-literal rule agree with §5. Matching pins, marker configuration, complete observation pairs and successful G3 remain necessary before “R1 holds”; findings 1–2 concern inadequate evidence that can pass those checks.

The eight holdouts remain **byte-for-byte identical** to the round-1 array. All load correctly, reference existing defects, and yield **131 unique IDs and combinations** with the main matrix.

| Holdout | Reason survives? |
|---|---|
| h01 | Yes: deny → fallback review below 75; signature present. |
| h02 | Yes: amount guard removed; no threshold remains. |
| h03 | Yes: changed at-250000 row prevents the signature. |
| h04 | Yes: retained 250000 boundary establishes one-sidedness. |
| h05 | Yes: embargo exception changes disposition; no threshold exists. |
| h06 | Yes: changed zero and two occupy both sides. |
| h07 | Yes: per-row probability `1/30`; n=20 catch probability **0.492385**. |
| h08 | Yes: per-row probability `(1/108) × (250000/500001)`; n=20 catch probability **0.088631**. |

The intentionally null runtime digest is **not a review blocker**. Nothing requires the runtime or freeze pins earlier than the stated release/freeze milestones. Complete matching pins are required before registered construction; an isolated preflight check confirmed refusal before root creation under the current null pins.

**Final verdict: `not freezable as written`.** Close the signature-evidence and random-replicate acceptance gaps, separate control failures from validity failures, and correct the two vendor reasons.

### Round 4 — maintainer disposition

Every finding is applied.

| # | Severity | Disposition |
|---|---|---|
| 1 | BLOCKER | **Applied.** The signature record retains the profile's threshold entries whole — every boundary, every origin, zero counts included — and the scorer (`signature_evidence_ok`) holds them to exactly the replayed mutant's boundaries (`replay.threshold_boundaries`) and exactly the ledger's origins, with each count bounded by its rows and the origin's buckets by the ledger; the bucket sums, `lineMoved` and `placed` are recomputed from those entries and must agree with the record. The replay itself refuses an entry whose origins are empty or not the ledger's. A declared count with no entries, a foreign boundary, a foreign origin, or counts beyond the ledger are each refused by a test. |
| 2 | BLOCKER | **Applied.** `registered_inputs_ok` rebuilds every random ledger at its declared seed under the pinned runtime and compares bytes, as it does the literal ledger; a ledger that is not its seed's construction is a validity failure. §7 says so. |
| 3 | MAJOR | **Applied.** `evidence()` returns validity failures and control results separately: a malformed, missing or unbound record is a validity failure (pipeline-invalid); a completed, bound unplanted replay that mismatched is G1 failing and a documented dropped instance is G2 failing, both `control-gate-failed` after validity passes. §7 names the three executed controls. |
| 4 | MINOR | **Applied.** D4-19's random reason no longer lists `approve` above the line; D2-12's states the band [187500, 250000) and the retained 250000 boundary. |
