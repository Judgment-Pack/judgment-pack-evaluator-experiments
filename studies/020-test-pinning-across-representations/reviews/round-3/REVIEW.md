# Review round 3 — review (verbatim)

The responded tree is not freezable: 8 BLOCKER, 6 MAJOR, and 1 MINOR findings.

## Findings

1. **R3-1 — BLOCKER — R2-1; `harness/e4lib/engines.py::opa_check()` and `harness/e4lib/admit.py::admit_arm_rego()`.** The claimed typed no-answer boundary remains incomplete. `opa_check()` raises only for exit 124; any other non-answer exit, including 2 or 127, can return parsed diagnostic codes and then be filed by admission as the authoring outcomes `opa-check-failed` or `unparseable-artifact`. This contradicts the disposition’s express rule that exits 0/1 are answers and every other invocation failure raises. The shared `_refuse_no_answer()` exists but `opa_check()` never calls it, and the tests cover exit 1 and unreadable output rather than a parseable-output exit 2/127 mutation. Fix: call `_refuse_no_answer("opa check", …, answer_exits=(0, 1))` before diagnostic parsing for both normal and v0-compatible checks, and drive exit 2/127 through real admission to `engine-invocation-refused`. `PREREG-REVIEW.md:211`; `harness/e4lib/engines.py:283-322,362-385`; `harness/e4lib/admit.py:168-222`; `harness/tests/test_score_admit.py:99-141`.

2. **R3-2 — BLOCKER — R2-10; `PREREGISTRATION.md` §2a.2; `harness/batch.py::pilot_next_entry()` / `run_pilot()`; `harness/pilot_rates.py`.** The 21-attempt repair replaces wrapper refusals only, not every apparatus refusal in §1a’s registered population. The scheduler declares a call clean solely when the ledger’s wrapper `code` is null and stops after twelve such calls per arm. Scoring-time `engine-invocation-refused` is discovered only afterward; `pilot_rates.py` then immediately raises `PILOT-SHORT` instead of spending attempt 13 through the same pilot. Thus an arm with eleven apparatus-clean calls after twelve wrapper-clean calls aborts before the registered cap, contrary to “12 apparatus-clean calls … from at most 21 attempts.” Fix: make the pilot state machine classify scoring-time apparatus before declaring an arm complete, then append same-label replacements until twelve fully §1a-clean calls or attempt 21; add mutations where attempt 12 is a scoring refusal and 13 is clean, and where the arm remains short only at 21. `PREREGISTRATION.md:782-802`; `harness/batch.py:4613-4671,4947-5029`; `harness/pilot_rates.py:180-213`; `harness/tests/test_pilot.py:782-812,1109-1136`.

3. **R3-3 — BLOCKER — R2-12; `PREREGISTRATION.md` §2a.6; `harness/batch.py::abandon_pilot()`; `harness/make_manifest.py::_abandoned_tree_problems()`.** The terminal-first-pilot ruling is coherent, but abandonment can hide spent model calls. Wrapper status 1 means the model was never invoked; statuses 10, 12, and 13 mean respectively a nonzero model call, a timed-out model call, and a post-call failure. Nevertheless abandonment accepts every non-null code and even accepts a missing ledger, while the freeze check does the same. The test explicitly blesses an abandoned timeout record. This makes “every attempt wrapper-refused, or no ledger at all — spent nothing” false and permits up to 63 invoked attempts to be renamed away before another pilot. Fix: require an authenticated ledger, admit only never-invoked preflight status 1, refuse statuses 10–13, verify the absence of `CALL.json`, sessions and completions, and refuse a missing ledger unless an independently chained preflight receipt proves no invocation. `harness/batch.py:543-568,5126-5167`; `harness/make_manifest.py:961-977`; `harness/tests/test_pilot.py:915-943,1472-1484`; `PREREGISTRATION.md:940-967`.

4. **R3-4 — BLOCKER — R2-7/R2-11/R2-13; `harness/make_manifest.py::calibration_record_problems()` / `analysis_artifact_problems()`; `calibration/derive_floor.py`; `harness/tests/pilot_fixture.py`.** The sealed ledger is genuinely authenticated, but none of the three derived pilot documents is authenticated to the sealed slot outcomes. For `PILOT-RATES.json`, the freeze gate validates internal counters and compares only its set of slot-path strings with the ledger; it never re-scores those paths. A coordinated edit to a row, its counters, embedded result, derived-floor pin, and digest therefore passes. `C4-REFERENCE.json` and `PILOT-DISPERSION.json` receive digest and internal-shape validation only. The accepted fixture demonstrates the latter defect by fabricating every dispersion row with σ = 0.1, `[0.08, 0.13]`, and arbitrary MDEs without scoring anything. Fix: at freeze, canonically regenerate all three artifacts from the authenticated sealed slots through the registered scoring/analysis producers and byte-compare them before accepting their pins; add coordinated row-plus-summary-plus-pin mutations for rates, C4 medians, and dispersion. `harness/make_manifest.py:1054-1135,1139-1208`; `calibration/derive_floor.py:165-271`; `harness/tests/pilot_fixture.py:299-348`; `harness/tests/test_pilot.py:1312-1433`; `harness/tests/test_pilot_analysis.py:291-345`.

5. **R3-5 — BLOCKER — R2-6/R2-13; `harness/pilot_analysis.py::dispersion_table()`; SCAFFOLD S10.** The promised S10 fill conditions away the apparatus attrition it is supposed to measure. `score_pilot_runs()` deletes apparatus-refused attempts; `dispersion_table()` then divides each member’s retained n by `len(scored["runs"][arm])`. For every ITT member, numerator and denominator are therefore identical and `realisedNAtRegisteredN` is always 60, whether twelve clean calls required twelve attempts or twenty-one. PP projections likewise estimate identity retention conditional on apparatus success instead of the full analysis-set fraction. Fix: carry each arm’s attempted count from the authenticated ledger and compute registered analysis-set n as `registeredN × member_n / attempted`, with explicit rounding; test identical twelve clean outcomes obtained in twelve versus eighteen attempts. `harness/pilot_analysis.py:214-249,275-313`; `harness/SCAFFOLD.md:50`; `PREREGISTRATION.md:1508-1523`.

6. **R3-6 — BLOCKER — R2-2; `PREREGISTRATION.md` §§2.1, 5.4, 5.6; `design/BRIEF.md`.** Native-for-both is a coherent estimand and its observed-family arithmetic is correct, but the dependent operating characteristics required by R2-2 were not recomputed. The active size, power, and N=60 justification still use `oc18.py` under shared offset weights; §5.6 explicitly says the simulation “is not re-run here.” Pilot dispersion supplies σ and MDE, not the joint eighteen-member intersection–union size/power distribution, and no `oc18.py` producer is tracked—the only provenance points to an uncommitted `scratchpad/v2oc/`. Fix: commit a reproducible producer, rerun all size/power scenarios under pinned native/native weights, and update the N justification and every dependent headline; alternatively withdraw those simulations as governing support and prospectively replace the N rationale. `reviews/round-2/REVIEW.md:15`; `PREREGISTRATION.md:540-548,1570-1574,1689-1735,1772-1780`; `design/BRIEF.md:720`.

7. **R3-7 — BLOCKER — `PREREGISTRATION.md` §4.2 and §5.1 E1; `harness/score.py::e1_control()` / `results_markdown()`.** A further preregistration event remains explicitly owed: S2’s JPS mechanical membership predicate is still marked `TODO(prereg)`, with a registered fallback to drop S2. Yet active E1 promises the 117- and 110-row supports, S1/S2 strata, and exclusive dispositions. Production `e1_control()` computes only whole-support perfect/runs/rate, and Markdown prints only that one table; no JPS S2 predicate or stratum publisher exists. Fix: implement, certify, publish, and mutation-test the JPS S2 predicate plus both supports and exclusive disposition rows, or execute the registered S2-drop fallback and update every 110-support-dependent statement before freeze. `PREREGISTRATION.md:1164-1195,1259-1274,2082-2088`; `harness/score.py:1237-1261,2062-2073`.

8. **R3-8 — BLOCKER — `harness/SCAFFOLD.md` R1; `PREREG-REVIEW.md`.** The response says only S10 and the sealed reviewer set remain owed, but the scaffold expressly says Study 020 has no freeze runbook yet. Its following inventory names obligations; it is not the required step-numbered, executable freeze-fill procedure. The tests merely search that inventory for selected gate names and payload globs, so they do not establish an ordering that can actually be followed. Fix: author the exact ordered runbook, including pilot derivation, canonical artifact verification, S10/S2 fills, reviewer-set pinning, all freeze gates, `ownPorts`, manifest-last ordering, and the freeze commit; bind the step sequence rather than keyword presence. `PREREG-REVIEW.md:204-207`; `harness/SCAFFOLD.md:3-7,56-67`; `harness/tests/test_manifest.py:1278-1305,1373-1388`.

9. **R3-9 — MAJOR — R2-10 currency; `PREREGISTRATION.md` §2.1; `harness/SCAFFOLD.md` S5.** The attempt-cap amendment says the budget moved from 36 to 63 pilot calls and from 1.34 h to approximately 2.35 h, but both live pricing tables still say 36 pilot calls and approximately 249 calls total; SCAFFOLD S5 still describes “12/arm = 36 calls.” The correct maximum count is 27 + 63 + ~6 + 180 = ~276, and at the selected low-condition means the printed total becomes about 10.73 h. Applying the document’s own pilot-like round triple to 21 rather than 12 pilot rounds makes that branch about 78.9 h total, not 71.2 h, so its stated 72 h headroom also disappears. Fix: update both pricing tables, total-call and disk projections, S5, and every dependent budget/headroom statement, with tests deriving the pilot row from the registered cap. `PREREG-REVIEW.md:220`; `PREREGISTRATION.md:429-432,447-468,562-568,782-797`; `harness/SCAFFOLD.md:45`.

10. **R3-10 — MAJOR — R2-4 currency; `PREREGISTRATION.md` §3.2.** The governing criterion and executable pin are correct, but the disposition overstates the prose repair. Active text still labels the amended criterion “PENDING round-2 review,” says the switch awaits round-2 blessing, and says “only round 2’s blessing remains outstanding,” while later active text says the amendment was blessed and the guard is registered. Those phrases are neither struck nor marked historical. Fix: strike and mark the pending/outstanding language, leave one current criterion statement, and add a currency test that rejects those exact stale clauses once the round is closed. `PREREG-REVIEW.md:214`; `PREREGISTRATION.md:1069-1107,1122-1134`; `harness/PINS.json:97-106`.

11. **R3-11 — MAJOR — R2-2 currency; `harness/e4lib/family.py` F-1; `harness/PINS.json`.** Executable family behavior is native/native, but the module’s reader-facing findings record still says the registered estimand is the round-1 hybrid, that round 2 verifies it, and that `PINS.json` carries no family member. The registry note also promises “two single-universe alternatives and the superseded hybrid,” although the registered native/native report is not an alternative; the report correctly contains only shared/shared and the superseded hybrid as alternatives. These are governing provenance comments explicitly cited by the registration, not harmless stale implementation notes. Fix: mark the hybrid ruling superseded throughout the module, remove the false no-family-pin statements, and describe exactly the registered report plus its two Tier-D alternatives. `harness/e4lib/family.py:80-145,173-182,622-630,1393-1422`; `harness/PINS.json:97-103`; `PREREGISTRATION.md:1429-1454`.

12. **R3-12 — MAJOR — R2-16; `CORRECTION-TARGETS.md` T5.** Manifest coverage of `COUNTERFACTUAL-SHIFT.json` now holds, but the correction venue does not. T5’s claim column includes the JSON’s figures while its Venue and URL name only `POWER-PRESENCE-IDIOM.md`; this violates the register’s own same-file/same-prominence rule and leaves incorrect JSON cells without a registered in-file correction seat. The test checks manifest membership, not the venue. Fix: add `harness/COUNTERFACTUAL-SHIFT.json` and its URL as a T5 venue, specify how an immutable JSON result carries a same-prominence correction, and bind the exact venue set in a mutation test. `CORRECTION-TARGETS.md:3-23,26-34`; `harness/tests/test_counterfactual_shift.py:248-255`.

13. **R3-13 — MAJOR — R2-15; `harness/integrity.py::_evidence_lines()` / `verify_sweep_evidence()`.** Descendant symlinks, special files, and empty directories are now refused and the three digests remain unchanged, but the named evidence root itself is not `lstat`-checked. `verify_sweep_evidence()` first calls `os.path.isdir(root)`, which follows a symlink, then `_evidence_lines()` walks its target. Replacing a whole named root with a symlink to an identical external clone therefore preserves the pinned digest. Existing mutations cover only descendants. Fix: `lstat` each named root and require a real directory before `os.walk()`, with a root-symlink mutation. `harness/integrity.py:1237-1315`; `harness/tests/test_sweep_rates.py:393-474`.

14. **R3-14 — MAJOR — R2-11(A); `harness/e4lib/transfer.py::observables()`.** Exact-row routing and the two-band precedence are correct, but the completion-byte band silently changes cohort. After selecting executed calls, `median()` independently drops `None` completion sizes. An executed, wrapper-clean author-protocol violation can lawfully have no `completion.txt`, so its duration remains in the executed cohort while its byte observation disappears. The registered text says completion bytes use the same cohort, and the cohort test covers only an unexecuted call. Fix: define missing completion bytes on an executed call as a registered value—normally zero—or mark the entire arm’s byte band unevaluable; in either case assert that the duration and completion cohorts have identical cardinality. `PREREGISTRATION.md:897-903,913-938`; `harness/e4lib/transfer.py:147-188`; `harness/tests/test_pilot.py:814-841`; `harness/tests/test_score_transfer.py:154-167`.

15. **R3-15 — MINOR — R2-9; registry readers in `harness/counterfactual_shift.py`, `harness/integrity.py`, and `harness/e4lib/capabilities.py`.** The critical pilot declaration path rejects duplicate and non-finite JSON, but the disposition’s claim that the strict decoder is wired into every registry reader is false. `counterfactual_shift.load_pins()`, standalone `verify_sweep_evidence()`, and `capabilities.registry()` still use ordinary `json.loads`; `calibration_record_problems()` also reads `PILOT-RATES.json` non-strictly. Fix: centralize the duplicate/non-finite rejecting loader and use it at every `PINS.json` and registered JSON read, with NaN/Infinity and duplicate-key mutations for each public reader. `PREREG-REVIEW.md:219`; `harness/counterfactual_shift.py:138-140`; `harness/integrity.py:1293-1295`; `harness/e4lib/capabilities.py:569-572`; `harness/make_manifest.py:1066-1069`.

## Ruling adjudication and independent recomputation

1. **R2-2 — NATIVE-FOR-BOTH:** coherent. Included native and shared denominators coincide at JPS 69 / Rego 62. Excluded native denominators are JPS 57 / Rego 62; excluded shared denominators are JPS 57 / Rego 55. Native minus shared excluded offsets are exactly +0.043551719541 PP and +0.042583903552 ITT per subtracted unit, agreeing with the printed +0.043552 / +0.042584. Independent six-member reconstruction:

| member | native/native A−C / A−B | shared/shared A−C / A−B | hybrid native/shared A−C / A−B |
|---|---:|---:|---:|
| M13 | .146332 / .141638 | .146332 / .141638 | .146332 / .141638 |
| M14 | .031364 / .010361 | .031364 / .010361 | .031364 / .010361 |
| M15 | −.003648 / .014243 | −.003648 / .014243 | −.003648 / .014243 |
| M16 | **.191971 / .187276** | .171993 / .166701 | .232313 / .227619 |
| M17 | **.083921 / .062918** | .043455 / .019779 | .127473 / .106469 |
| M18 | **.047569 / .066949** | .004338 / .024116 | .091121 / .110500 |

These reproduce Reprint 1b to its printed digits. The hybrid alternative reproduces Reprint 1’s point estimates, n values, unadjusted p-values, and every decision under the registration’s disclosed adjusted-p Monte Carlo scope. Retaining moved historical rows as a visibly SUPERSEDED Reprint 1 and placing Reprint 1b beside them is the correct frozen-reader treatment. `family_report()` supplies complete alternatives, while `score.py` passes only registered `verdict` and `members` into `decision.py`; no decision reads `alternatives`. R3-6 remains because the operating characteristics were not rerun. `PREREGISTRATION.md:1429-1454,1615-1647`; `harness/e4lib/family.py:665-692,1393-1422`; `harness/score.py:1598-1635`; `harness/e4lib/decision.py:177-225`; `harness/tests/test_family.py:1248-1325`.

2. **R2-10 — pilot denominator:** the 0.20 declaration on `identityFloor` was not the defect. The registered 6/12 passing boundary and 5/12 failure are consistent with the apparatus-success population. The amended record vocabulary—`attempted`, `calls`, `apparatusExcluded`, `apparatusCodes`—is reconciled as one partition by the sealed validator, and primary scoring correctly combines batch-time and scoring-time apparatus and raises `ScoreError` on denominator disagreement. The remaining failure is the scheduler in R3-2 and its S10 consequence in R3-5. `PREREGISTRATION.md:840-869`; `calibration/derive_floor.py:202-270,301-353`; `harness/score.py:2420-2472`; `harness/tests/test_score_publication.py:402-450`.

3. **R2-12 — terminal first pilot:** sound as a lifecycle ruling. Removing the unreachable re-pilot promise and making `calibration-invalid` terminal is coherent. The abandonment exception is not sound as implemented, for R3-3’s spent-call reason. `PREREGISTRATION.md:905-911,940-967`; `harness/e4lib/decision.py:155-162`.

4. **R2-13 — dispersion:** the exact σ interval multipliers independently reproduce as `[0.7387048578, 1.5476912227]` at df 15 and `[0.8065765647, 1.3162777439]` at df 33. The producer uses `score.score_run()`, never calls `score_member()` or `family_report()`, and its recursive no-peek screen rejects directional/test members. The 019 table is properly retained as a labelled prior with the pilot table intended beside it. R3-4 and R3-5 prevent accepting the resulting artifact/fill as implemented. `harness/e4lib/dispersion.py:80-106`; `harness/pilot_analysis.py:110-144,214-331`; `harness/tests/test_pilot_analysis.py:208-255`; `PREREGISTRATION.md:1742-1780`.

5. **R2-11(A) — two band rows:** the routing holds. The exact set contains eight rows; the gate contains only duration and completion-byte bands `[0.80, 1.25]`; reasoning tokens are descriptive. Ratios are pilot ÷ batch with closed endpoints. An exact mismatch wins row 1 even when a band also fails; a band-only miss or unevaluable cell reaches row 3. R3-14 is the residual cohort defect. `harness/e4lib/transfer.py:59-79,251-330`; `harness/score.py:418-466,2836-2889`; `harness/tests/test_score_transfer.py:85-199`.

## Other verified source claims

- The ledger gate accepts the lawful sealed fixture and rejects the former two-counter fake, deletion, duplication, reordering, post-seal mutation and re-sealing. Those checks discriminate; R3-4 concerns the separately authored derived rows, not the chained ledger itself. `harness/make_manifest.py:1211-1375`; `harness/tests/test_pilot.py:1312-1379`.
- `score.reconciled_population()` correctly publishes both apparatus phases over attempted calls and refuses any population/E2/E4 disagreement. `harness/score.py:2420-2472`; `harness/tests/test_score_publication.py:402-450`.
- The regenerated counterfactual names native/native/single. M18’s A−C adjusted shift is exactly +0.014699155746 and is correctly reported descriptively as +0.015. The source constant and registry authority agree on `759b0ddcf8c5eb23b4bd3a8a98d927ca0b73f43873480fa5168a4afc6a25b2da`. `harness/COUNTERFACTUAL-SHIFT.json:518-524,934-956`; `harness/PINS.json:215`; `harness/tests/test_counterfactual_shift.py:212-245,257-325`.
- The three evidence-tree digests reproduce unchanged: `96c36b794c9c0f7ed4e240342eb6f12b6c55077e000947d441eac617ce1768ea`, `3bf31aaa9b473ba1de1a0d58a205a2a6c87c0891dc9f734be465c105346ae573`, and `732c5054680788c1b2df31d79f5a8af9ef03f64af3d4f470ea45da5a2911ed03`. R3-13 concerns only the unchecked root type. `harness/PINS.json` `sweep.evidenceTrees`; `harness/integrity.py:1237-1315`.
- Static counts reconcile: 117 gold rows; 183 JPS and 185 Rego manifest entries; off-gold PASS over 236,196 cells with zero divergences; pairing 33 / 69 / 62; batch 60/arm and 180 slots; 46 port destinations and 382 ported artifacts; 18 `NEW_IN_020` files; and 23 freeze pins. R2-17’s named changed-line totals also reproduce as 148, 195, 28, 4, 8, and 150. `PREREGISTRATION.md:1149-1159`; `controls/off-gold-equivalence.json`; `mutants/MANIFEST-jps.json`; `mutants/MANIFEST-rego.json`; `harness/tests/test_prereg_currency.py:145-188,2104-2188`; `harness/PORTS.md:105,130-166`; `harness/integrity.py:284-317`; `harness/tests/test_pins.py:89-114`.
- Honest NO-GO, short-pilot, pipeline-invalid and calibration-invalid states are prevented from reaching inferential rows. R3-4 matters because a coordinated derived-record forgery can falsely manufacture the GO premise those guards trust. `harness/make_manifest.py:1096-1135`; `harness/pilot_analysis.py:123-144`; `harness/score.py:2871-2908`.

Full-suite pytest execution was unavailable in this read-only review checkout because its temporary-directory creation failed. The family/counterfactual-focused tests and the pinned binary validation of the reviewer payloads were executed; every other claimed discriminator above was checked directly against its mutation docstring and guarded mechanism.

## Round-2 disposition verification

- R2-1 → R3-1.
- R2-2 → R3-6 and R3-11; the native/native ruling and arithmetic themselves HOLD.
- R2-3 → HOLDS.
- R2-4 → R3-10.
- R2-5 → HOLDS.
- R2-6 → R3-5.
- R2-7 → R3-4.
- R2-8 → HOLDS for sealing/finalization.
- R2-9 → R3-15; declaration/date validation itself HOLDS.
- R2-10 → R3-2, R3-5, and R3-9.
- R2-11 → R3-4 and R3-14; exact/band routing itself HOLDS.
- R2-12 → R3-3.
- R2-13 → R3-4 and R3-5; χ²/no-peek producer logic itself HOLDS.
- R2-14 → HOLDS.
- R2-15 → R3-13.
- R2-16 → R3-12; manifest coverage itself HOLDS.
- R2-17 → HOLDS.
- R2-18 → HOLDS for its named currency repairs; R3-8 is the separately omitted owed runbook.
- R2-19 → HOLDS.

## Sealed reviewer mutant set

The following is the authored sealed set. Each payload is UTF-8, LF-only, no BOM, with exactly one final LF. Whitespace/comment normalization is non-semantic; each mutant makes exactly one semantic edit to `reference/refA/pack.json` or `reference/refB/policy.rego`. No registered generator class was copied mechanically. The JPS payload was reported semantically valid by pinned jpack v0.17.0; every Rego payload passed pinned OPA 1.19.0 `check --strict --capabilities controls/opa-capabilities.json --format json` with exit 0. The suites were not executed, preserving first execution for the primary attempt. The loader contract is `harness/e4lib/reviewer.py:96-107,143-303`.

Dated prediction, 2026-09-02: `rm-rego-01` is the likeliest survivor because disposition-only assertions miss its reason token; `rm-rego-03` and `rm-rego-05` should survive suites lacking the corresponding omitted-input cases; `rm-jps-01` and `rm-rego-02` should be killed primarily by explicit evidence-state cases; `rm-rego-04` should be killed by any U1 test that expects deduplication across agreeing candidate assignments.

`rm-jps-01` retargets the negated D6b-uninsured evidence test from the insurance certificate to required financial evidence, probing suites that exercise the insured path but never distinguish absent insurance.

```json
{"specVersion":"0.2.0-draft","id":"https://example.com/judgment-packs/study-019-vendor-approval-reference-a","version":"0.1.0","title":"Vendor approval (contest policy draft v0.1) - arm A reference","description":"Reference implementation of the Study 019 contest policy draft v0.1 (P1, D1-D8, O1-O3, U1) as a Judgment Pack.","decision":{"intent":"Determine how a vendor onboarding spend request is handled under the vendor approval policy.","question":"What determination does this vendor spend request receive?"},"evidenceRequirements":[{"id":"financial-evidence","description":"Audited financial statements on file (P1).","required":true,"kind":"document"},{"id":"insurance-certificate","description":"A current certificate of insurance (consulted by D6b; never required).","required":false,"kind":"document"}],"outcomes":[{"id":"approve","label":"Approve"},{"id":"review","label":"Review"},{"id":"enhanced-review","label":"Enhanced review"},{"id":"reject","label":"Reject"}],"rules":[{"id":"r-d1","description":"D1 - sanctions MATCH is rejected.","when":{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"MATCH"},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d3","description":"D3 - a risk score of 90 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d4","description":"D4 - HIGH country risk with a risk score of 70 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d5","description":"D5 - a recorded prior enforcement action is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d6a","description":"D6a - LOW country, risk below 40, spend up to $500,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-insured","description":"D6b - LOW country, risk below 40, spend $500,000.01-$2,000,000.00 with an insurance certificate available: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-uninsured","description":"D6b - the same band with the insurance certificate absent: enhanced review (D6b decides such requests; D8 does not reach them).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"financial-evidence"}}]},"outcome":"enhanced-review","onUnknown":"ignore"},{"id":"r-d6c","description":"D6c - LOW country, risk 40-69, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d7","description":"D7 - MEDIUM country, risk below 40, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-o1-review","description":"D8 for the region O1 removes from D6c: a new vendor in D6c's region is referred for review.","when":{"op":"all","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-low","description":"O1 + D8 - a new vendor in D6c's LOW-country risk band is referred for review whatever the requested spend is (D6c is removed by O1 and no other determination clause reaches this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-spend","description":"O1 + D8 - a new vendor in D6c's risk band with spend up to $100,000.00 is referred for review whatever the country risk is (LOW is D6c removed by O1; MEDIUM and HIGH are out of D7's and D4's reach in this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-d8","description":"D8 - every other CLEAR request is referred for review.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"not","condition":{"op":"any","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]}]}}]},"outcome":"review","onUnknown":"escalate"}],"exceptions":[{"id":"x-o1-first-engagement","description":"O1 - for new vendors clause D6c does not apply; such requests fall to D8. An unreported status is treated as no.","when":{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-o2-critical-supplier","description":"O2 - a critical supplier with a CLEAR screening result is never approved or rejected automatically: review. An unreported status is treated as no.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/criticalSupplier","operator":"equals","value":"yes"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"}]},"effect":"force-outcome","outcome":"review","onUnknown":"ignore"},{"id":"x-o3-large-exposure","description":"O3 - HIGH country risk, CLEAR screening, spend above $2,000,000.00 and financial evidence available: escalated for human determination.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"financial-evidence"}]},"effect":"escalate","onUnknown":"escalate"},{"id":"x-d5-suppress-d6a","description":"D5 - a recorded prior enforcement action displaces clause d6a; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6a","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-insured","description":"D5 - a recorded prior enforcement action displaces clause d6b-insured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-insured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-uninsured","description":"D5 - a recorded prior enforcement action displaces clause d6b-uninsured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-uninsured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6c","description":"D5 - a recorded prior enforcement action displaces clause d6c; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-d5-suppress-d7","description":"D5 - a recorded prior enforcement action displaces clause d7; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d7","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-review","description":"D5 - a recorded prior enforcement action displaces clause o1-review; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-review","onUnknown":"ignore"},{"id":"x-d5-suppress-d8","description":"D5 - a recorded prior enforcement action displaces clause d8; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-low","description":"O1 - inside the LOW-country D6c risk band a new vendor's determination is review on every spend, so D8's own catch-all must not re-read the requested spend there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-spend","description":"O1 - inside D6c's risk band at spend up to $100,000.00 a new vendor's determination is review on every country risk, so D8's own catch-all must not re-read the country risk there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-low","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-low; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-low","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-spend","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-spend; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-spend","onUnknown":"ignore"}],"escalation":{"triggers":["missing-required-evidence","unknown","no-match"],"target":{"kind":"queue","name":"vendor-compliance-desk"}},"metadata":{"authors":["Study 019 reference build, arm A"],"createdAt":"2026-08-15T00:00:00Z"}}
```

SHA-256: `506ebd3cb742c25b480e2ef87af127276cb00a67383a357182ae81771aa68a04`

`rm-rego-01` preserves O3’s unresolved disposition but changes its directly emitted reason from `exception-escalation` to `unknown`, probing disposition-only assertions.

```rego
package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]
u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

SHA-256: `51ae3a77289c906aef954cd1a7a40483180f3f14726372498cc849748f4062a3`

`rm-rego-02` aliases the insurance reader to financial evidence, probing whether suites independently vary the two evidence requirements.

```rego
package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]
u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

SHA-256: `aace36bcb1bdaaaf26e9483c8dc2255baf0e8cd22ee513711cdea52c2afc7794`

`rm-rego-03` makes risk candidate selection depend on spend presence, probing omitted risk with readable spend.

```rego
package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_spend != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]
u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

SHA-256: `0927e2f93d8866e69b461e4650285740543a5f74dbb192d334f6e1b780590eec`

`rm-rego-04` changes U1’s determination collection from a set to an array, probing whether suites rely on deduplication when many candidate assignments agree.

```rego
package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]
u1_determinations := [d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
]
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

SHA-256: `861cbf1ede05672ee5bc146e5dcc03a4136ff6c1cf99f81675bf1659f6112d3e`

`rm-rego-05` removes `HIGH` from U1’s unreadable-country candidate domain, probing omitted country where LOW/MEDIUM agree but HIGH is the sole counterexample.

```rego
package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM"]
u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

SHA-256: `ab340098ff375fdacbf402cbc3b2a89ecd40c39aa0402ee09416e0587f66db1c`

`MANIFEST.json`

```json
{"reviewerSetVersion":1,"mutants":[{"id":"rm-jps-01","language":"jps","file":"rm-jps-01.json","sha256":"506ebd3cb742c25b480e2ef87af127276cb00a67383a357182ae81771aa68a04"},{"id":"rm-rego-01","language":"rego","file":"rm-rego-01.rego","sha256":"51ae3a77289c906aef954cd1a7a40483180f3f14726372498cc849748f4062a3"},{"id":"rm-rego-02","language":"rego","file":"rm-rego-02.rego","sha256":"aace36bcb1bdaaaf26e9483c8dc2255baf0e8cd22ee513711cdea52c2afc7794"},{"id":"rm-rego-03","language":"rego","file":"rm-rego-03.rego","sha256":"0927e2f93d8866e69b461e4650285740543a5f74dbb192d334f6e1b780590eec"},{"id":"rm-rego-04","language":"rego","file":"rm-rego-04.rego","sha256":"861cbf1ede05672ee5bc146e5dcc03a4136ff6c1cf99f81675bf1659f6112d3e"},{"id":"rm-rego-05","language":"rego","file":"rm-rego-05.rego","sha256":"ab340098ff375fdacbf402cbc3b2a89ecd40c39aa0402ee09416e0587f66db1c"}]}
```

Manifest SHA-256: `f445442ac547f63a390441c2c230e96ce453c4cb856e3507109a454624a8ce7a`

DO NOT FREEZE
