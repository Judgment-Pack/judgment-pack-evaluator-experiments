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
