# Post-run adversarial review

**Cross-vendor** (the preregistration's required post-run pass): drafting
model Anthropic `claude-fable-5`; reviewing model OpenAI `gpt-5.6-sol` via
codex-cli 0.145.0 (`codex exec`, sandbox `workspace-write`, reasoning effort
ultra), 2026-08-05, one run, reproduced unedited below, no run discarded.
It reviewed the state after attempt 2 — and its verdict named the repair:
*"a corrected freeze/ledger/scorer followed by a fresh first attempt is
required to restore the stronger claim."* That condition was implemented
(DEVIATIONS.md §2) and met by attempt 3, the primary.

## Maintainer disposition

| # | Finding | Disposition |
|---|---|---|
| 1 | blocking — the registered freeze was not implemented (no record hashed, no config/import coverage) | **Accepted.** The freeze now covers every record file and 27 inputs; `validate` mirrors POLICY.md and holds records, sets, and RECORDS.md's table to it; the interpreter and prereg-commit ancestry are rechecked at run and score. |
| 2 | blocking — attempt 2 was not the preregistered primary; the replacement rule reopened selection | **Accepted.** Attempts bind to their freeze digest; `score` selects the first `DONE` attempt under the *current committed* freeze with its seal verified; attempt 2 is demoted to an audited demonstration in ANALYSIS.md and DEVIATIONS.md §2. |
| 3 | should-fix — DEVIATIONS §1 understated what attempt 1 exposed | **Accepted.** §2 corrects the record: acquisition and transcription completed and the B matrix was visible; no evaluator output or endpoint was. |
| 4 | blocking — `score` could pass with missing rows, trusted statuses, unchecked expectations | **Accepted.** The scorer now requires the full row set per arm, recomputes every expectation against the gated wrapper and every mismatch from parsed dispositions, cross-checks the runtime's reported statuses, and hardens P-A and E5 (all projects, exact origins). |
| 5 | blocking — no seal, no freeze binding, prose crash note | **Accepted.** Runs seal read-only under a hashed manifest, bind to the freeze digest, and retain structured crash metadata; `score` verifies all three. |
| 6 | should-fix — gate equality was Python-object, refs not consumed | **Accepted.** Canonical-byte comparison; references consumed; leftovers refused. |
| 7 | should-fix — receipt population and proxy exit unchecked; validate misses table/outcome constraints | **Accepted.** Exact receipt count, nonzero proxy exit refused; validate enforces H/F/K outcome constraints against a mirrored policy and RECORDS.md's rows. |
| 8 | should-fix — ANALYSIS overclaims | **Accepted.** Rewritten: attempt-1 history stated, byte-equality now true of the corrected gate, the "nothing leaked" sentence replaced by the internal-consistency claim, E5 scoped to one payload. |
| 9 | should-fix — rerun path does not score a fresh run | **Accepted in part.** Freeze-bound selection means a rerun under an unchanged freeze scores the first sealed attempt, deliberately — reproduction is by isolated checkout of the freeze commit, stated here; the binary arrives by digest. |
| 10 | observation — attacks that did not hold, incl. the independent rescore confirming the pattern | **No change needed** — recorded with gratitude; it is why attempt 3's identical numbers surprised nobody. |

## Prompt (verbatim)

````
You are performing the POST-RUN adversarial review of Study 009 (studies/009-transcribed-oracle-matrix in this working tree). You wrote both pre-freeze reviews (PREREG-REVIEW.md). The study has now frozen, run, and scored: read PREREGISTRATION.md (third revision), DEVIATIONS.md, FREEZE.json, RESULTS.json, ANALYSIS.md, the harness (harness/study.py, gate.py, pnf_check.py, test_study.py), the fixtures (packs/, records/, DEFECT.json, transcription/), and the retained trials/ (ATTEMPT-1 crashed+ledgered, ATTEMPT-2 primary).

Every registered prediction hit. Your job: attack the run and the analysis. Specifically:
1. Implementation-vs-preregistration conformance: does the harness actually enforce what the third revision registered (complete-row admission, rule identity, call contract, one-session accounting, argumentsDigest recompute, artifact-record equality, ledger, freeze coverage)? Name any gap between registered contract and code.
2. The deviation: is DEVIATIONS.md §1's handling of the crashed attempt 1 and re-freeze sound, or does it open the tuning door the prereg closed? Was anything about the scored run knowable from attempt 1's partial outputs?
3. The scoring: does score compute what §8 registered (table conformance per row, entailed mismatch sets, P-A completeness)? Can RESULTS.json say pass while something registered failed?
4. The analysis: does ANALYSIS.md overclaim anywhere, or underclaim the entailment structure? Is the "pipeline faithfulness + existence witness" reading the strongest honest reading?
5. Anything that would change the verdict if a reader re-ran the study from the frozen inputs.

Output: numbered findings with severity (blocking / should-fix / nit / observation), file/section, concrete scenario, evidence. State explicitly which attacks did NOT hold. End with a verdict paragraph: does the study's stated claim stand as stated?
````

## Complete output (unedited)

1. **Blocking — the registered freeze was not implemented.**  
   **File/section:** [PREREGISTRATION.md §10](<studies/009-transcribed-oracle-matrix/PREREGISTRATION.md:260>), [FREEZE.json](<studies/009-transcribed-oracle-matrix/FREEZE.json:2>), [study.py](<studies/009-transcribed-oracle-matrix/harness/study.py:43>).  
   **Scenario:** After freezing, change `f-boundary-1`’s recorded outcome from `manual-review` to `clear`. `verify_freeze` accepts it because none of the 12 record files is hashed; `validate` accepts it because it never compares the files with `RECORDS.md` or enforces F outcomes; acquisition and the gate then faithfully bind the changed file. E3 acquires an extra F mismatch, changing the verdict under a nominally unchanged freeze.  
   **Evidence:** The freeze has only 15 named files. It omits every `records/*.json`, generated project configurations, matrix digests, and the promised import closure. Python implementation/version and `preregistrationCommit` are recorded but never rechecked; ancestry is not verified. Generated `jpack.json` files contain only `"matrix": "matrix.json"`, not the registered gate-approved digest. Arm A’s construction evaluations also run from the attempt directory without the registered per-arm `JPACK_CONFIG`. The frozen `RECORDS.md` is no substitute: [cmd_validate](<studies/009-transcribed-oracle-matrix/harness/study.py:103>) never parses it. This matters particularly because the missing import-closure check is exactly the class of defect that crashed attempt 1.

2. **Blocking — attempt 2 is not the preregistered primary, and the replacement rule reopens run selection.**  
   **File/section:** [PREREGISTRATION.md §10](<studies/009-transcribed-oracle-matrix/PREREGISTRATION.md:285>), [DEVIATIONS.md §1](<studies/009-transcribed-oracle-matrix/DEVIATIONS.md:14>), [primary_attempt](<studies/009-transcribed-oracle-matrix/harness/study.py:388>).  
   **Scenario:** An attempt can run far enough to expose unfavorable evaluator output, then be killed or have `DONE` withheld. `primary_attempt()` skips it and selects the next completed attempt, with no limit, stage restriction, crash classification, or freeze-identity check.  
   **Evidence:** Revision 3 says “attempt 1 is primary,” a failed primary is reported, and “no retry rule … exists.” After the crash, the rule became “first attempt reaching `DONE`.” Strictly, attempt 1 is the registered primary and failed; attempt 2 is a disclosed, post-deviation repaired replication. The narrow repair was committed before attempt 2, but transparency cannot make the new rule preregistered.

3. **Should-fix — DEVIATIONS.md understates what was known after attempt 1.**  
   **File/section:** [DEVIATIONS.md §1](<studies/009-transcribed-oracle-matrix/DEVIATIONS.md:5>), [ATTEMPT-1/matrix-b.json](<studies/009-transcribed-oracle-matrix/trials/ATTEMPT-1/matrix-b.json:1>).  
   **Scenario/evidence:** Attempt 1 completed all 12 acquisitions, `check_acquisition`, manifest writing, and transcription. Its full B matrix exposed every row ID, fact, expectation, origin, and artifact digest. That matrix is byte-identical to attempt 2’s, SHA-256 `37fbf2d5f08950364ad37cf8133befa38975b814fcb61bfa6e21b7ce1a39382f`.  
   What was *not* known was gate success, Arm A/P-A, actual C/D dispositions, packs-test mismatch reports, or CLI/MCP equality. The shadowing failure precedes the first evaluator invocation, and attempt 1 has no projects or `runs.json`. Thus “no evaluator output or scored endpoint was seen” holds; the broader implication that nothing informative was seen does not. Git shows no pack, record, table, rule, transcriber, or gate change, so there is no evidence of actual endpoint-driven tuning.

4. **Blocking — `score` permits an overall pass when registered endpoints or prerequisites failed.**  
   **File/section:** [PREREGISTRATION.md §§8–9](<studies/009-transcribed-oracle-matrix/PREREGISTRATION.md:217>), [rows_of/endpoint](<studies/009-transcribed-oracle-matrix/harness/study.py:380>).  
   **Concrete false-pass scenarios:**

   - E2 can receive only the five F∪K rows, omitting all H rows; E3 can receive only the two K rows. If the present actuals match their tables and statuses name the expected mismatches, both pass. No B/B′ row-set or count check exists.
   - Duplicate IDs are silently overwritten by `rows_of()`.
   - Mismatch entailment is not recomputed. `score` trusts `row.status` and never checks the reported `expected` against the gated wrapper. A contradictory report can have `expected == actual` while saying `"mismatch"` and still pass.
   - P-A’s pass expression checks only top-level `"passed"` plus the unique-ID map. It ignores its own computed mismatch list, duplicates, missing/malformed actual dispositions, and the “exactly one row” requirement.
   - E5 validates only B′/C, although registration says every project; it checks only an origin prefix, not equality to the gated origin; and it ignores B/D origins and row completeness.

   Therefore [RESULTS.json](<studies/009-transcribed-oracle-matrix/RESULTS.json:1>) can say `pass:true` while §8 or P-A failed.

5. **Blocking — the append-only/sealed ledger promise is absent.**  
   **File/section:** [study.py ledger/run writes](<studies/009-transcribed-oracle-matrix/harness/study.py:194>), [score](<studies/009-transcribed-oracle-matrix/harness/study.py:401>).  
   **Scenario:** Edit owner-writable `runs.json` after `DONE`, then run `score`. Scoring does not reverify the freeze, acquisition, gate, lineage, project matrices, or trial hashes.  
   **Evidence:** There is no sealing/chmod or completed-output digest manifest. Trial files are mode `0644` and directories `0755`. `CRASHED` is manually written prose, not harness-retained exit metadata: it lacks exit code, traceback, argv, timestamp, freeze identity, and last completed stage. Attempts are not bound to a freeze. The final Git commit preserves the current snapshot, but that is not the registered pre-score seal.

6. **Should-fix — complete-row admission is strong but not exact.**  
   **File/section:** [gate.py admit_matrix](<studies/009-transcribed-oracle-matrix/harness/gate.py:101>).  
   **Scenario:** Change JSON `false` to `0` in an emitted fact. Python considers `False == 0`, so dictionary equality admits it even though canonical JSON and the evaluator-visible type differ. Alternatively, repeat one correctly reconstructed row 12 times: the length check passes and references are reusable, so omitted IDs are not detected.  
   **Evidence:** The preregistered check was canonical equality plus complete case/reference coverage. The implementation uses ordinary Python equality and does not consume references or enforce unique IDs. Exact extra-member rejection, artifact-derived wrapper/origin, absent `supportedExtensions`, and rule-bound facts otherwise do hold.

7. **Should-fix — acquisition and fixture validation miss smaller registered checks.**  
   **File/section:** [check_acquisition](<studies/009-transcribed-oracle-matrix/harness/study.py:248>), [cmd_validate](<studies/009-transcribed-oracle-matrix/harness/study.py:103>).  
   **Scenario:** Append a valid chained receipt at call index 12. `attest.verify` accepts the contiguous chain, while `check_acquisition` checks only its 12 refs and never rejects the extra receipt. The proxy subprocess’s exit status is also ignored. Separately, malformed decision metadata, a divergent `RECORDS.md`, non-manual-review F outcomes, or non-wrong K outcomes can pass `validate`.  
   **Evidence:** One-session accounting, authority/tool, `isError`, recomputed keyed `argumentsDigest`, and canonical artifact-to-record equality are genuinely implemented for every named ref. The gap is exact population and comparison to *frozen* records.

8. **Should-fix — ANALYSIS.md needs narrower claims, though its central entailment disclosure is honest.**  
   **File/section:** [ANALYSIS.md](<studies/009-transcribed-oracle-matrix/ANALYSIS.md:3>).  
   **Overclaims:**

   - “Every registered prediction hit” ignores that the registered primary crashed.
   - “Every emitted row byte-equal” is literally false; parsed Python-object equality was checked.
   - “Nothing leaked, drifted, or was reinterpreted anywhere” exceeds the evidence given the missing record/config/import freeze and absent trial seal.
   - E5 exercised one B′/C payload. That does not alone establish that runtime issue #74 was generally “closed.”

   **Entailment:** The analysis correctly says F∪K and K are entailed. It could be even sharper: once table conformance and artifact-wrapper binding hold, those mismatch sets contribute zero independent inferential evidence. The K rows show the carrier reports deliberate disagreement; they are not separate evidence of defect detection.

   The strongest honest reading is: **the retained 12-row execution is internally consistent with a faithful fixed-fixture integration pipeline, and it instantiates a constructed existence witness**. It is not general pipeline validation, discovery evidence, record truth, sensitivity, or a rate.

9. **Should-fix — the documented final-tree rerun path does not score the rerun.**  
   **File/section:** [primary_attempt](<studies/009-transcribed-oracle-matrix/harness/study.py:388>).  
   **Scenario:** At final `HEAD`, `run` creates `ATTEMPT-3`; `score` still selects the first `DONE`, attempt 2. A materially different fresh run therefore does not change `RESULTS.json`.  
   A real reproduction must use an isolated checkout of the corrected-freeze commit or independently score the newly created attempt. Supplying the exact jpack binary is also external—the tree retains its digest, not the binary.

10. **Observation — attacks that did not hold against the retained attempt-2 data.**

   - C and D differ by exactly the registered `>=`→`>` patch.
   - The covert-rule attack is closed: `pnf_check.py` hardcodes the exact two-field identity projection, and the gate loads the digest-checked rule with literal `{}` parameters.
   - Attempt 2 has one receipt session, exactly 12 receipts indexed 0–11, valid HMAC chains, recomputed arguments digests, and artifacts canonically equal to the committed record objects.
   - Re-running acquisition and complete-row admission reproduced all 12 saved lineages.
   - Every arm has 12 unique retained rows. Every B/D and B′/C actual disposition matches its full table entry.
   - Independently deriving mismatches from retained expected and actual dispositions gives exactly F∪K and K, matching the runtime statuses.
   - P-A has 12 unique passed rows with actual dispositions.
   - All three retained projects validated; origins exactly match the matrix, not merely the prefix test.
   - B and B′ matrix bytes are identical, and Arm A/B shared evaluator inputs match.
   - CLI and MCP payloads are genuinely equal after removing `command`.
   - Git history shows the record, pack, defect, rule, transcriber, and gate fixtures unchanged after the original freeze. No evidence shows evaluator-result tuning after attempt 1.

**Verdict:** The narrow existential construction is present in the retained artifacts, and a stronger manual rescore confirms its numerical pattern. But the study’s stated status does **not** stand as stated: it was not the preregistered first-attempt result, and the registered freeze, sealing, matrix binding, and scorer completeness were not mechanically enforced. The honest conclusion is that attempt 1 was the failed registered primary and attempt 2 is a post-deviation, post hoc auditable integration/existence demonstration. A corrected freeze/ledger/scorer followed by a fresh first attempt is required to restore the stronger claim.
