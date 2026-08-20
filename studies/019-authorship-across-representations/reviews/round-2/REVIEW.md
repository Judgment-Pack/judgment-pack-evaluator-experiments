# Review round 2 — Study 019

Verdict: the executable X1 repair is narrow and sound, but the current tree is not freeze-ready. Seven blocker-class residuals survive green unit tests, and the committed manifest, adequacy gate, and regeneration record are presently red.

All paths below are relative to `studies/019-authorship-across-representations/`.

## Verification record

Using CPython 3.12.11, pinned JPack 0.17.0, pinned OPA 1.19.0, and the filtered capabilities file:

- Full harness: **574 passed, 1 failed**. `tests/test_manifest.py::test_the_committed_manifest_describes_the_tree_it_covers` reports a stale digest for `PREREG-REVIEW.md`; direct `integrity.verify_manifest()` refuses for the same reason. This contradicts the recorded “575 passed, 0 failed” claim (`PREREG-REVIEW.md:25-29`).
- E4/engine/decision/statistics/publication/pipeline subset: **157 passed**.
- Preregistration-currency suite: **22 passed**.
- Partition, transcript, seal, domain, X1, and wrapper-exit focused tests passed, but the residuals below cross seams those tests do not exercise.
- The X1 repair itself reproduced: the change is limited to two rules and four exceptions, changes exactly the 72 retired-region cells, and has zero collateral change over 236,196 cells (`design/reference/refA/PACK-CHANGE-001.md:11-110`; `design/reference/OFFGOLD-CERT.json:25-70,199`). The runtime exclusion registry is empty (`harness/e4lib/e4.py:86-90`).

## Findings

### R2-1 — BLOCKER — The current tree fails its own pre-freeze gates

**File/section:** `PREREGISTRATION.md:364-374`; `design/mutants/ADEQUACY.md:3-37`; `design/mutants/REGENERATION-CHECK.json:1-53`; `harness/STUDY-MANIFEST.sha256`; `harness/tests/test_manifest.py:92`.

**Failure mode:** The preregistration and adequacy artifact explicitly leave the adequacy gate open: JPS kills 146/183 and Rego 150/184, with 37 and 34 undispositioned mutants respectively. The committed regeneration record covers only arm B, has `pass:false`, lacks the adequacy stamp, and lists 34 undispositioned empty-witness mutants. Independently, the current manifest rejects the current `PREREG-REVIEW.md`. Thus the response’s recorded green suite and closure do not describe this tree.

**Concrete fix:** Close adequacy from scratch; regenerate gold, both mutant arms, pairing, cuts, pilot, OC artifact, and preregistration; commit a two-arm passing regeneration record; regenerate the study manifest last; then run the complete pinned suite and integrity command from the resulting clean tree.

### R2-2 — BLOCKER — Primary E4 uses the wrong identity-control denominator

**File/section:** `PREREG-REVIEW.md:33`; `PREREGISTRATION.md:28-44`; `design/mutants/e4_score.py:656-700`; `design/mutants/E4-PILOT-v2.json:4530-4537`; `harness/score.py:1044-1082`; `harness/tests/test_score_attempt.py:740-748`.

**Failure mode:** The disposition and pilot remove identity-failing suites from the E4 denominator and record `highKill:null`. The primary scorer instead uses `len(runs)` and merely prevents the failed run from entering the numerator. A direct two-run probe—one identity-pass/high-kill run and one identity failure—produced primary E4 `1/2`, while the pilot rule produces `1/1`. Existing tests prove the failed run is not “high”; they do not test denominator membership. Per-language cuts themselves are correctly selected and reachable (`harness/e4lib/e4.py:718-778`; `harness/score.py:1723-1776`).

**Concrete fix:** Freeze one identity-failure denominator rule and make the primary scorer, pilot scorer, OC derivation, preregistration, and tests agree. Add an end-to-end mixed identity-pass/fail denominator regression.

### R2-3 — BLOCKER — Rego runtime faults are still credited as mutant kills

**File/section:** `PREREGISTRATION.md:218-228,499-505`; `design/prompts/upstream/opa/docs__docs__policy-testing.md:197-203`; `harness/e4lib/engines.py:435-488`; `harness/e4lib/e4.py:642-658`; `design/mutants/e4_score.py:338-357,575-600`; `design/mutants/E4-PILOT-v2.json:7055-7080,9970-9994`.

**Failure mode:** The retained OPA documentation distinguishes assertion failure from evaluation error, and the preregistration requires runtime faults to refuse. But `opa_test()` maps any JSON result with `fail:true` to `TEST_FAILED`, and `kill_arm_rego()` maps that to `KILLED`. With pinned OPA, a reference-passing test containing `1 / denominator == 1` and valid mutant `m-b-108` makes the denominator zero; OPA reports `fail:true`, and the harness credits a kill. OPA 1.19.0’s `opa test` has no `--strict-builtin-errors` option. The current pilot is worse: arm-B run 1 reports 126 `error` failures and 126 kills; arm-C run 1 reports 137 of each. Those errors therefore constitute the cited pilot kill means.

**Concrete fix:** Use an execution path that machine-distinguishes failed assertions from evaluation faults, or restrict the authored-test surface so evaluation faults cannot be conflated. Runtime errors and timeouts must refuse, and the pilot/OC artifacts must be regenerated through the same primary taxonomy.

### R2-4 — BLOCKER — Rego domain validation accepts explicit nulls and can certify a dynamic bad input with a decoy literal

**File/section:** `PREREGISTRATION.md:323-337`; `harness/e4lib/domain.py:112-123,213-230,303-310,404-468`; `harness/e4lib/e4.py:464-532`; `harness/tests/test_score_domain.py:47-53`.

**Failure mode:** `_literal()` converts AST `null` to Python `None`; `.get()` then collapses explicit null and absence, and `_enum_problem()` treats optional `None` as omitted. A suite using `newVendor:null` passed domain and identity validation and killed paired mutants `m-b-115`, `m-b-116`, `m-b-117`, and `m-b-182`.

The dynamic-input path also validates only an aggregate collection of input-shaped literals. This valid suite supplies an unrelated valid decoy, while the actual tested input contains invalid `newVendor:7`:

```rego
package residual_dynamic_test
import rego.v1

decoy := {"vendor": {"sanctionsStatus": "CLEAR"}}

make_bad(nv) := {
  "vendor": {
    "sanctionsStatus": "CLEAR",
    "countryRisk": "LOW",
    "riskScore": 50,
    "requestedSpend": 50000,
    "newVendor": nv,
    "criticalSupplier": "no",
    "priorEnforcement": "no",
  },
  "evidence": {
    "financial-evidence": "present",
    "insurance-certificate": "present",
  },
}

test_dynamic_case if {
  built := make_bad(7)
  data.study.decision == {"disposition": "approve", "reasons": []}
    with input as built
}
```

The decoy makes `cases` nonempty, so the scorer does not refuse the unresolved indirect input. This suite earned the same four paired kills.

**Concrete fix:** Preserve a distinct presence sentinel and reject explicit null. Resolve and validate every `with input as` expression independently; an unrelated literal must never certify an indirect input. Add both probes as pinned-engine end-to-end tests.

### R2-5 — BLOCKER — Transcript verdicts are sealed but ignored by population scoring

**File/section:** `PREREGISTRATION.md:545-548`; `harness/batch.py:1492-1567,2224-2231`; `harness/score.py:418-482,732-777,1153-1165`; `harness/authoring_call.sh:573-600`; `harness/tests/test_transcript_binding.py`; `harness/tests/test_batch.py`.

**Failure mode:** The driver computes and seals a transcript verdict, but `read_slot()` reads the seal, wrapper result, golden record, and completion only. It never reads or recomputes the transcript verdict. In sealed-slot probes, changing the retained transcript to an extra-turn author violation or a context-mismatch apparatus violation left `code=None`; both slots remained included and scored. The classifier and seal tests pass because neither crosses into population construction.

**Concrete fix:** Recompute the transcript verdict in the scorer from the sealed bytes before population membership, apply its registered author/apparatus code, and add end-to-end tests for every transcript reason branch.

### R2-6 — BLOCKER — The arm-A matrix schema rejects the prompt’s own format and is not total

**File/section:** `design/prompts/ARM-A-INSTRUCTIONS.md:61-74,177-204`; `design/prompts/armA/jps-excerpt.md:642-687`; `design/pilots/2026-08-15-calibration-pilot-01/arm-A/run-008/secondary.json:2`; `harness/e4lib/e4.py:182-202,240-275`; `harness/score.py:1224-1241`; `harness/tests/test_score_e4.py:429-485`.

**Failure mode:** The prompt and real pilot outputs require `"matrixVersion":"2"` as a string. The primary loader registers integer `2`, so a prompt-conforming matrix is rejected as `unparseable-artifact` and earns zero. Existing tests incorrectly use numeric `2`. Separately, a case with `expectedDisposition.reasons:1` passes the enclosing-object check and then raises uncaught `TypeError` in `align_expected()` instead of returning the registered authoring code.

**Concrete fix:** Accept the registered string version, validate every nested member and exactly one expected-result form before alignment, and property-test the loader using the prompt’s examples plus malformed nested values.

### R2-7 — BLOCKER — Reviewer-set failure is nonfatal, and the loader does not enforce the authored schema

**File/section:** `PREREGISTRATION.md:81-88,139-149,381-385`; `harness/e4lib/reviewer.py:69-155`; `harness/score.py:1821-1871`; `harness/tests/test_score_reviewer.py:51-196`.

**Failure mode:** The scorer computes endpoints, gates, contrasts, and the decision before loading/executing the reviewer set. A `ReviewerSetError` is caught as a refusal, but publication still records `pipelineInvalid:false` and exits successfully. Therefore a missing, malformed, or digest-invalid mandatory set can coexist with a registered substantive verdict. The loader also does not enforce 6–10 mutants, both languages, exact record keys, or language-specific extensions. Its containment check accepts absolute paths because `dirname(normpath("/x"))` does not start with `..`, and `os.path.join(root, "/x")` escapes `root`.

**Concrete fix:** Load and fully validate the set before any endpoint calculation; any failure must terminate as pipeline-invalid. Enforce exact schema, cardinality, both languages, filename/extension consistency, and real-path containment. Add an integrated malformed-set attempt test.

### R2-8 — MAJOR — “Integrity before any study-local import” is not true

**File/section:** `PREREGISTRATION.md:523-535`; `harness/score.py:99-113,1588-1602,1625-1659`; `harness/integrity.py:712-739`.

**Failure mode:** `score.py` inserts the local harness path and imports local `integrity` before verification. It then invokes unverified `integrity.study_label()` and `unfilled_pins()`, and the early terminal path binds other study modules before manifest verification. `integrity.py` itself correctly says `-P` is operator discipline, not protection against a hostile tree, because imports precede the check. The preregistration’s stronger root-of-trust statement is therefore false.

**Concrete fix:** Either narrow the claim to an externally trusted freeze commit/operator model, or use an independently pinned minimal bootstrap that authenticates `score.py` and `integrity.py` before importing or invoking study-local code.

### R2-9 — MAJOR — Empty-prefix shortfall declarations cannot round-trip

**File/section:** `harness/batch.py:2663-2695,2763-2844,2931-3027`; `harness/score.py:606-610`; `harness/tests/test_score_attempt.py:531-699`.

**Failure mode:** The declaration schema and driver accept an empty prefix with no ledger and null head/digest. The scorer unconditionally requires `BATCH.json`. A direct round-trip passed `batch.validate` and `batch.verify` for `records=[]`, then failed `score.validate_attempt` solely because no ledger existed. Tests cover only nonempty 9/10 prefixes.

**Concrete fix:** Define and emit a canonical empty ledger, or register and support the no-ledger empty representation in the scorer. Add a zero-prefix driver-to-scorer round-trip test.

### R2-10 — MAJOR — `engineSuppliedKill` manifest validation is not fail-closed

**File/section:** `design/mutants/adequacy_search.py:972-1146`; `harness/e4lib/e4.py:314-352,420-448`; `harness/tests/test_score_e4.py:146-181,258-266`.

**Failure mode:** The current manifests do carry the expected Boolean census—183 JPS records with 27 true, 184 Rego records with zero true—but the consumer accepts partial and mistyped manifests. It refuses only if every record is null. A manifest with one `true` and another missing value is accepted; the string `"false"` is truthy and is counted as engine-supplied. One existing test explicitly accepts a manifest with only two of three records marked.

**Concrete fix:** Require `type(engineSuppliedKill) is bool` on every valid manifest record and reject every missing, null, numeric, or string value. Reverse the partial-manifest test.

### R2-11 — MAJOR — Regeneration closure is neither committed nor checked against the regenerated tree

**File/section:** `design/mutants/regenerate.py:20-54,154-183`; `design/mutants/REGENERATION-CHECK.json:1-53`; `PREREG-REVIEW.md:44`.

**Failure mode:** The committed artifact is B-only and failing, while the disposition claims a complete passing check. More fundamentally, after generating into a scratch copy, `regenerate.py` calls `undispositioned(DESIGN)`, where `DESIGN` is the original committed tree, not the scratch tree. Once the committed tree happens to be green, a newly generated empty-witness mutant can therefore evade the supposed fail-closed check. The script also states that it cannot create the required adequacy stamp.

**Concrete fix:** Evaluate undispositioned records under the regenerated scratch root, require both arms in every record, and make the closure/stamp transition part of a separately auditable command. Add a regression that introduces a new scratch-only empty-witness mutant.

### R2-12 — MAJOR — Failed control gates still produce and publish inferential intervals

**File/section:** `PREREGISTRATION.md:475-495,591-599`; `harness/score.py:1361-1430,1764-1811`; `harness/e4lib/stats.py:201-212`.

**Failure mode:** Section 5 says no inferential quantity is computed or published at rows 1–3. The scorer computes marginal E4 Clopper–Pearson intervals before evaluating gates and always publishes them. A failed-E1-gate probe with E4 `1/2` returned `control-gate-failed` while still printing `[0.0126, 0.9874]`. Contrast and direction suppression do hold, but that is narrower than the preregistered prohibition. Section 10’s commitment to publish all intervals directly contradicts section 5.

**Concrete fix:** Either suppress every interval above row 4, or amend the registration before freeze to prohibit only contrasts/directions while explicitly allowing marginal descriptive intervals. Test a populated failed-gate result.

### R2-13 — MAJOR — Withdrawn exactness and stale pilot-anchor claims remain in the current OC artifact

**File/section:** `PREREGISTRATION.md:419-455`; `design/mutants/OC-TABLE.md:7-52,304-338,396-542`; `design/mutants/oc_table.py:474-529,756-761`.

**Failure mode:** The preregistration now honestly calls the interval an exact-arithmetic mesh-inversion hull and disclaims continuum certification. The artifact it designates for publication still says “exact unconditional confidence interval,” “exact test,” “true worst-case,” and claims 95% coverage for every true rate; the generator will re-emit those statements. A banner acknowledges staleness but leaves live text calling the table pilot-anchored to the old `pC=0.8…1` range, old `pA=.2,pC=1` gap, old C boundary, and old 5/5 identity/X1 proposal, despite its own later section reporting 1/5, 0/5, 0/5 and open adequacy.

**Concrete fix:** Correct the generator and rebuild the artifact as one internally consistent document. Remove—not merely banner—the withdrawn statements, and add currency tests that parse claims from the generated OC output.

### R2-14 — MAJOR — The frozen-reader refresh still teaches the retired X1 gate and obsolete study state

**File/section:** `harness/PINS.json:3,33-80`; `README.md:3-18`; `harness/SCAFFOLD.md:38,63-71,101-115,236-246,328-344`; `harness/tests/E2E-SMOKE.md:24-31,94-100,295-306,447-452`; `harness/score.py:1068-1085,1247-1256`; `PREREGISTRATION.md:99-129,338-348,557-564`; `harness/tests/test_prereg_currency.py:42-241`.

**Failure mode:** PINS still says 76 gold rows, 145 JPS mutants, and that the registered exclusions are exactly X1. README still describes the old policy-reliability/language-investment question and says no review round exists. SCAFFOLD and the smoke document still describe `partition_x1` gating and the old 105/145/41 counts. The scorer still publishes `x1ExcludedCases`, although the preregistration says the retired class has no operational count. The currency tests inspect the preregistration and selected artifacts, but not PINS, README, SCAFFOLD, or the stale OC prose. The executable exclusion registry is empty; the frozen-reader corpus is not.

**Concrete fix:** Systematically remove the retired predicate and obsolete counts from every current-facing document and result schema, clearly archive historical smoke sections, and extend currency tests over every current-status document.

## Disposition verification

| Round-1 finding | Round-2 verification |
|---|---|
| R1-1 | **R2-2** — per-language cuts hold; identity-denominator claim does not. |
| R1-2 | **R2-14** — executable repair and empty registry hold; “retired everywhere” does not. |
| R1-3 | **R2-4** — explicit null and indirect-input decoy bypass symmetric domain validation. |
| R1-4 | **HOLDS** — distinct wrapper statuses and exhaustive non-null partition are enforced by `harness/batch.py:327-464` and the pinned `test_batch.py` exit-path cases. |
| R1-5 | **R2-5** — transcript verdict exists and is sealed, but is not consumed by scoring. |
| R1-6 | **R2-6** — prompt-conforming version is rejected and nested malformed input escapes the total path. |
| R1-7 | **R2-9** — nonempty shortfall paths hold; the registered empty prefix does not round-trip. |
| R1-8 | **R2-3** — real OPA evaluation faults still enter kills, including the current pilot. |
| R1-9 | **R2-1, R2-8** — the current manifest is red, and verification does not precede all local imports. |
| R1-10 | **R2-7** — loader/executor exists, but failure is nonfatal and its schema is weaker than authored. |
| R1-11 | **R2-10** — current census values are right; consumer completeness/type enforcement is not. |
| R1-12 | **R2-1, R2-11** — committed record is B-only/failing and the closure check reads the wrong root. |
| R1-13 | **HOLDS** — exact rates drive direction; the 6/50 versus 5/6 regression passes (`harness/e4lib/decision.py:224-253`; `harness/tests/test_score_decision.py:190-214`). |
| R1-14 | **R2-12** — contrast/direction gating holds; the broader no-inference claim does not. |
| R1-15 | **HOLDS** — §1 and §5 consistently keep δ out of every decision (`PREREGISTRATION.md:104-116`; `harness/tests/test_prereg_currency.py:193-225`). |
| R1-16 | **R2-13** — runtime relabeling holds, but the generator and published OC artifact retain withdrawn exactness. |
| R1-17 | **R2-14** — preregistration defines the bundled estimand; current reader-facing documents still state the superseded question. |
| R1-18 | **R2-3, R2-13** — disclosure exists, but the cited pilot counts engine errors as kills and stale anchors remain published. |
| R1-19 | **R2-13, R2-14** — refresh and currency enforcement omit several current-facing artifacts. |
| R1-20 | **HOLDS** — all seven PORTS rows recompute and the corrected prose no longer says the table must grow (`harness/PORTS.md`; `harness/tests/test_ports.py`). |

## Sealed reviewer mutant set

Base references:

- JPS: `design/reference/refA/pack.json`, SHA-256 `db9776070fbf5e193443ffb1f371b2524b4662f0877868306323b5c9e3701853`
- Rego: `design/reference/refB/policy.rego`, SHA-256 `1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2`

Each payload below is exactly the UTF-8 bytes between the fence lines, with one terminal LF and no additional blank line. All three JPS files returned `status:"valid"` from pinned `jpack spec validate`; all three Rego files passed pinned `opa check --strict --capabilities … --format json`.

### `rm-jps-01.json`

```json
{"specVersion":"0.2.0-draft","id":"https://example.com/judgment-packs/study-019-vendor-approval-reference-a","version":"0.1.0","title":"Vendor approval (contest policy draft v0.1) - arm A reference","description":"Reference implementation of the Study 019 contest policy draft v0.1 (P1, D1-D8, O1-O3, U1) as a Judgment Pack.","decision":{"intent":"Determine how a vendor onboarding spend request is handled under the vendor approval policy.","question":"What determination does this vendor spend request receive?"},"evidenceRequirements":[{"id":"financial-evidence","description":"Audited financial statements on file (P1).","required":true,"kind":"document"},{"id":"insurance-certificate","description":"A current certificate of insurance (consulted by D6b; never required).","required":false,"kind":"document"}],"outcomes":[{"id":"approve","label":"Approve"},{"id":"review","label":"Review"},{"id":"enhanced-review","label":"Enhanced review"},{"id":"reject","label":"Reject"}],"rules":[{"id":"r-d1","description":"D1 - sanctions MATCH is rejected.","when":{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"MATCH"},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d3","description":"D3 - a risk score of 90 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d4","description":"D4 - HIGH country risk with a risk score of 70 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d5","description":"D5 - a recorded prior enforcement action is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d6a","description":"D6a - LOW country, risk below 40, spend up to $500,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-insured","description":"D6b - LOW country, risk below 40, spend $500,000.01-$2,000,000.00 with an insurance certificate available: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-uninsured","description":"D6b - the same band with the insurance certificate absent: enhanced review (D6b decides such requests; D8 does not reach them).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},"outcome":"enhanced-review","onUnknown":"ignore"},{"id":"r-d6c","description":"D6c - LOW country, risk 40-69, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d7","description":"D7 - MEDIUM country, risk below 40, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-o1-review","description":"D8 for the region O1 removes from D6c: a new vendor in D6c's region is referred for review.","when":{"op":"all","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-low","description":"O1 + D8 - a new vendor in D6c's LOW-country risk band is referred for review whatever the requested spend is (D6c is removed by O1 and no other determination clause reaches this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-spend","description":"O1 + D8 - a new vendor in D6c's risk band with spend up to $100,000.00 is referred for review whatever the country risk is (LOW is D6c removed by O1; MEDIUM and HIGH are out of D7's and D4's reach in this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-d8","description":"D8 - every other CLEAR request is referred for review.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"not","condition":{"op":"any","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]}]}}]},"outcome":"review","onUnknown":"escalate"}],"exceptions":[{"id":"x-o1-first-engagement","description":"O1 - for new vendors clause D6c does not apply; such requests fall to D8. An unreported status is treated as no.","when":{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-o2-critical-supplier","description":"O2 - a critical supplier with a CLEAR screening result is never approved or rejected automatically: review. An unreported status is treated as no.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/criticalSupplier","operator":"equals","value":"yes"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"}]},"effect":"force-outcome","outcome":"review","onUnknown":"ignore"},{"id":"x-o3-large-exposure","description":"O3 - HIGH country risk, CLEAR screening, spend above $2,000,000.00 and financial evidence available: escalated for human determination.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"financial-evidence"}]},"effect":"escalate","onUnknown":"escalate"},{"id":"x-d5-suppress-d6a","description":"D5 - a recorded prior enforcement action displaces clause d6a; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6a","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-insured","description":"D5 - a recorded prior enforcement action displaces clause d6b-insured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-insured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-uninsured","description":"D5 - a recorded prior enforcement action displaces clause d6b-uninsured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-uninsured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6c","description":"D5 - a recorded prior enforcement action displaces clause d6c; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-d5-suppress-d7","description":"D5 - a recorded prior enforcement action displaces clause d7; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d7","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-review","description":"D5 - a recorded prior enforcement action displaces clause o1-review; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-review","onUnknown":"ignore"},{"id":"x-d5-suppress-d8","description":"D5 - a recorded prior enforcement action displaces clause d8; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-low","description":"O1 - inside the LOW-country D6c risk band a new vendor's determination is review on every spend, so D8's own catch-all must not re-read the requested spend there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d7","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-spend","description":"O1 - inside D6c's risk band at spend up to $100,000.00 a new vendor's determination is review on every country risk, so D8's own catch-all must not re-read the country risk there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-low","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-low; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-low","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-spend","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-spend; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-spend","onUnknown":"ignore"}],"escalation":{"triggers":["missing-required-evidence","unknown","no-match"],"target":{"kind":"queue","name":"vendor-compliance-desk"}},"metadata":{"authors":["Study 019 reference build, arm A"],"createdAt":"2026-08-15T00:00:00Z"}}
```

Probe: retargeting the repaired LOW/new-vendor suppression from `r-d8` to `r-d7` tests whether suites cover the narrow unreadable-spend part of the retired X1 region.

### `rm-jps-02.json`

```json
{"specVersion":"0.2.0-draft","id":"https://example.com/judgment-packs/study-019-vendor-approval-reference-a","version":"0.1.0","title":"Vendor approval (contest policy draft v0.1) - arm A reference","description":"Reference implementation of the Study 019 contest policy draft v0.1 (P1, D1-D8, O1-O3, U1) as a Judgment Pack.","decision":{"intent":"Determine how a vendor onboarding spend request is handled under the vendor approval policy.","question":"What determination does this vendor spend request receive?"},"evidenceRequirements":[{"id":"financial-evidence","description":"Audited financial statements on file (P1).","required":true,"kind":"document"},{"id":"insurance-certificate","description":"A current certificate of insurance (consulted by D6b; never required).","required":false,"kind":"document"}],"outcomes":[{"id":"approve","label":"Approve"},{"id":"review","label":"Review"},{"id":"enhanced-review","label":"Enhanced review"},{"id":"reject","label":"Reject"}],"rules":[{"id":"r-d1","description":"D1 - sanctions MATCH is rejected.","when":{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"MATCH"},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d3","description":"D3 - a risk score of 90 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d4","description":"D4 - HIGH country risk with a risk score of 70 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d5","description":"D5 - a recorded prior enforcement action is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d6a","description":"D6a - LOW country, risk below 40, spend up to $500,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-insured","description":"D6b - LOW country, risk below 40, spend $500,000.01-$2,000,000.00 with an insurance certificate available: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-uninsured","description":"D6b - the same band with the insurance certificate absent: enhanced review (D6b decides such requests; D8 does not reach them).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},"outcome":"enhanced-review","onUnknown":"ignore"},{"id":"r-d6c","description":"D6c - LOW country, risk 40-69, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d7","description":"D7 - MEDIUM country, risk below 40, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-o1-review","description":"D8 for the region O1 removes from D6c: a new vendor in D6c's region is referred for review.","when":{"op":"all","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-low","description":"O1 + D8 - a new vendor in D6c's LOW-country risk band is referred for review whatever the requested spend is (D6c is removed by O1 and no other determination clause reaches this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-spend","description":"O1 + D8 - a new vendor in D6c's risk band with spend up to $100,000.00 is referred for review whatever the country risk is (LOW is D6c removed by O1; MEDIUM and HIGH are out of D7's and D4's reach in this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-d8","description":"D8 - every other CLEAR request is referred for review.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"not","condition":{"op":"any","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]}]}}]},"outcome":"review","onUnknown":"escalate"}],"exceptions":[{"id":"x-o1-first-engagement","description":"O1 - for new vendors clause D6c does not apply; such requests fall to D8. An unreported status is treated as no.","when":{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-o2-critical-supplier","description":"O2 - a critical supplier with a CLEAR screening result is never approved or rejected automatically: review. An unreported status is treated as no.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/criticalSupplier","operator":"equals","value":"yes"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"}]},"effect":"force-outcome","outcome":"review","onUnknown":"ignore"},{"id":"x-o3-large-exposure","description":"O3 - HIGH country risk, CLEAR screening, spend above $2,000,000.00 and financial evidence available: escalated for human determination.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"financial-evidence"}]},"effect":"escalate","onUnknown":"escalate"},{"id":"x-d5-suppress-d6a","description":"D5 - a recorded prior enforcement action displaces clause d6a; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6a","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-insured","description":"D5 - a recorded prior enforcement action displaces clause d6b-insured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-insured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-uninsured","description":"D5 - a recorded prior enforcement action displaces clause d6b-uninsured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-uninsured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6c","description":"D5 - a recorded prior enforcement action displaces clause d6c; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-d5-suppress-d7","description":"D5 - a recorded prior enforcement action displaces clause d7; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d7","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-review","description":"D5 - a recorded prior enforcement action displaces clause o1-review; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-review","onUnknown":"ignore"},{"id":"x-d5-suppress-d8","description":"D5 - a recorded prior enforcement action displaces clause d8; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-low","description":"O1 - inside the LOW-country D6c risk band a new vendor's determination is review on every spend, so D8's own catch-all must not re-read the requested spend there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-spend","description":"O1 - inside D6c's risk band at spend up to $100,000.00 a new vendor's determination is review on every country risk, so D8's own catch-all must not re-read the country risk there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-low","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-low; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-low","onUnknown":"ignore"}],"escalation":{"triggers":["missing-required-evidence","unknown","no-match"],"target":{"kind":"queue","name":"vendor-compliance-desk"}},"metadata":{"authors":["Study 019 reference build, arm A"],"createdAt":"2026-08-15T00:00:00Z"}}
```

Probe: deleting the D5 suppression of `r-o1-wide-spend` tests the repaired O1-wide composition where prior enforcement must still dominate.

### `rm-jps-03.json`

```json
{"specVersion":"0.2.0-draft","id":"https://example.com/judgment-packs/study-019-vendor-approval-reference-a","version":"0.1.0","title":"Vendor approval (contest policy draft v0.1) - arm A reference","description":"Reference implementation of the Study 019 contest policy draft v0.1 (P1, D1-D8, O1-O3, U1) as a Judgment Pack.","decision":{"intent":"Determine how a vendor onboarding spend request is handled under the vendor approval policy.","question":"What determination does this vendor spend request receive?"},"evidenceRequirements":[{"id":"financial-evidence","description":"Audited financial statements on file (P1).","required":true,"kind":"document"},{"id":"insurance-certificate","description":"A current certificate of insurance (consulted by D6b; never required).","required":true,"kind":"document"}],"outcomes":[{"id":"approve","label":"Approve"},{"id":"review","label":"Review"},{"id":"enhanced-review","label":"Enhanced review"},{"id":"reject","label":"Reject"}],"rules":[{"id":"r-d1","description":"D1 - sanctions MATCH is rejected.","when":{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"MATCH"},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d3","description":"D3 - a risk score of 90 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d4","description":"D4 - HIGH country risk with a risk score of 70 or above is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d5","description":"D5 - a recorded prior enforcement action is rejected.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"}]},"outcome":"reject","onUnknown":"ignore"},{"id":"r-d6a","description":"D6a - LOW country, risk below 40, spend up to $500,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-insured","description":"D6b - LOW country, risk below 40, spend $500,000.01-$2,000,000.00 with an insurance certificate available: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d6b-uninsured","description":"D6b - the same band with the insurance certificate absent: enhanced review (D6b decides such requests; D8 does not reach them).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},"outcome":"enhanced-review","onUnknown":"ignore"},{"id":"r-d6c","description":"D6c - LOW country, risk 40-69, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-d7","description":"D7 - MEDIUM country, risk below 40, spend up to $100,000.00: approved.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},"outcome":"approve","onUnknown":"ignore"},{"id":"r-o1-review","description":"D8 for the region O1 removes from D6c: a new vendor in D6c's region is referred for review.","when":{"op":"all","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-low","description":"O1 + D8 - a new vendor in D6c's LOW-country risk band is referred for review whatever the requested spend is (D6c is removed by O1 and no other determination clause reaches this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-o1-wide-spend","description":"O1 + D8 - a new vendor in D6c's risk band with spend up to $100,000.00 is referred for review whatever the country risk is (LOW is D6c removed by O1; MEDIUM and HIGH are out of D7's and D4's reach in this band).","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"outcome":"review","onUnknown":"ignore"},{"id":"r-d8","description":"D8 - every other CLEAR request is referred for review.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"not","condition":{"op":"any","conditions":[{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"90"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"70"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"500000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"500000.00"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"2000000.00"},{"op":"not","condition":{"op":"evidence-present","evidenceRequirement":"insurance-certificate"}}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"greater-than-or-equal","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]},{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"MEDIUM"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"40"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"}]}]}}]},"outcome":"review","onUnknown":"escalate"}],"exceptions":[{"id":"x-o1-first-engagement","description":"O1 - for new vendors clause D6c does not apply; such requests fall to D8. An unreported status is treated as no.","when":{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-o2-critical-supplier","description":"O2 - a critical supplier with a CLEAR screening result is never approved or rejected automatically: review. An unreported status is treated as no.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/criticalSupplier","operator":"equals","value":"yes"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"}]},"effect":"force-outcome","outcome":"review","onUnknown":"ignore"},{"id":"x-o3-large-exposure","description":"O3 - HIGH country risk, CLEAR screening, spend above $2,000,000.00 and financial evidence available: escalated for human determination.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"HIGH"},{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/requestedSpend","operator":"greater-than","value":"2000000.00"},{"op":"evidence-present","evidenceRequirement":"financial-evidence"}]},"effect":"escalate","onUnknown":"escalate"},{"id":"x-d5-suppress-d6a","description":"D5 - a recorded prior enforcement action displaces clause d6a; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6a","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-insured","description":"D5 - a recorded prior enforcement action displaces clause d6b-insured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-insured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6b-uninsured","description":"D5 - a recorded prior enforcement action displaces clause d6b-uninsured; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6b-uninsured","onUnknown":"ignore"},{"id":"x-d5-suppress-d6c","description":"D5 - a recorded prior enforcement action displaces clause d6c; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d6c","onUnknown":"ignore"},{"id":"x-d5-suppress-d7","description":"D5 - a recorded prior enforcement action displaces clause d7; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d7","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-review","description":"D5 - a recorded prior enforcement action displaces clause o1-review; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-review","onUnknown":"ignore"},{"id":"x-d5-suppress-d8","description":"D5 - a recorded prior enforcement action displaces clause d8; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-low","description":"O1 - inside the LOW-country D6c risk band a new vendor's determination is review on every spend, so D8's own catch-all must not re-read the requested spend there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/countryRisk","operator":"equals","value":"LOW"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-o1-suppress-d8-spend","description":"O1 - inside D6c's risk band at spend up to $100,000.00 a new vendor's determination is review on every country risk, so D8's own catch-all must not re-read the country risk there.","when":{"op":"all","conditions":[{"op":"fact","path":"/vendor/sanctionsStatus","operator":"equals","value":"CLEAR"},{"op":"fact","path":"/vendor/riskScore","operator":"greater-than-or-equal","value":"40"},{"op":"fact","path":"/vendor/riskScore","operator":"less-than","value":"70"},{"op":"fact","path":"/vendor/requestedSpend","operator":"less-than-or-equal","value":"100000.00"},{"op":"fact","path":"/vendor/newVendor","operator":"equals","value":"yes"}]},"effect":"suppress-rule","targetRule":"r-d8","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-low","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-low; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-low","onUnknown":"ignore"},{"id":"x-d5-suppress-o1-wide-spend","description":"D5 - a recorded prior enforcement action displaces clause o1-wide-spend; an unreported status is treated as no and suppresses nothing.","when":{"op":"fact","path":"/vendor/priorEnforcement","operator":"equals","value":"yes"},"effect":"suppress-rule","targetRule":"r-o1-wide-spend","onUnknown":"ignore"}],"escalation":{"triggers":["missing-required-evidence","unknown","no-match"],"target":{"kind":"queue","name":"vendor-compliance-desk"}},"metadata":{"authors":["Study 019 reference build, arm A"],"createdAt":"2026-08-15T00:00:00Z"}}
```

Probe: making optional insurance globally required tests whether suites distinguish evidence availability used by D6b from pack-level required evidence.

### `rm-rego-01.rego`

```rego
# Study 019 — contest policy draft v0.1, Rego reference implementation (arm C shape).
#
# Rego v1. Package `study`, entrypoint `data.study.decision`.
# Result shape: {"disposition": "approve|review|enhanced-review|reject|unresolved",
#                "reasons": [<sorted unresolved reason tokens>]}  (reasons [] for outcomes).
#
# Input projection (registered): vendor facts under /vendor, evidence availability under
# /evidence keyed by requirement id. An OMITTED key means "unreadable" (risk, spend,
# country) or "unreported" (yes/no statuses, evidence availability). Sanctions is always a
# present string; UNKNOWN is a value, not an omission. risk/spend arrive as JSON numbers
# (OPA parses them as exact big rationals, so all six thresholds compare exactly).

package study

# ---------------------------------------------------------------------------
# Registered default: D2's no-match is the fallback value for this entrypoint.
# (This build also names D2 explicitly inside `determine`, so that the U1
# comprehension below can quantify over it; the default is kept as registered
# and as a guard against any uncovered input.)
# ---------------------------------------------------------------------------
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# Readers. `null` / "OMITTED" are sentinels for an omitted key; the projection
# never emits a JSON null, so the sentinels cannot collide with a real value.
# ---------------------------------------------------------------------------
v_risk := object.get(input, ["vendor", "riskScore"], null)

v_spend := object.get(input, ["vendor", "requestedSpend"], null)

v_country := object.get(input, ["vendor", "countryRisk"], null)

v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)

v_new := object.get(input, ["vendor", "newVendor"], null)

v_critical := object.get(input, ["vendor", "criticalSupplier"], null)

v_prior := object.get(input, ["vendor", "priorEnforcement"], null)

fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")

ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")

# ---------------------------------------------------------------------------
# determine(risk, spend, country): the policy's clause ladder evaluated at a
# fully-readable assignment of the three unreadable-capable inputs. Every other
# input (sanctions, the three yes/no statuses, both evidence availabilities) is
# read from `input` directly, because none of them can be "unreadable" in U1's
# sense.
#
# Order inside the ladder mirrors the "Order of application" section:
#   O3, then O2, then D1, D2, then D3-D8 as modified by O1.
# The `else` chain gives exactly that precedence, and it also realizes the
# "earliest clause governs" tie-break: where two clauses yield the same
# determination (D3 and D4 at HIGH/risk>=90; D5 and D3; O1-suspended D6c and
# D8) the earlier rung is the one that fires.
#
# The function is TOTAL: the last rung returns the no-match value, so the U1
# comprehension below can never silently drop a candidate assignment.
# ---------------------------------------------------------------------------

# O3 — large exposure in a high-risk country. Carries the explicit financial-
# evidence conjunct the prose states; P1 has already gated above, so this is
# belt-and-braces, not a behavioural difference. O3 reads country risk,
# requested spend, sanctions and financial evidence; it does not read the risk
# score, so `risk` is deliberately unconstrained in this rung.
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}

# O2 — critical-supplier override. Never applies on MATCH/UNKNOWN.
# (Unreported critical-supplier status is an omitted key, so != "yes" -> treated as no.)
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}

# D1 — sanctions match.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}

# D2 — unreported sanctions: no determination clause applies, no clause matches.
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}

# D3 — critical risk.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}

# D4 — elevated risk in a high-risk country.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}

# D5 — prior enforcement action (unreported treated as no).
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}

# D6a — LOW country, risk < 40, spend <= 500,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}

# D6b — LOW country, risk < 40, 500,000.00 < spend <= 2,000,000.00.
#   insurance available  -> approve
#   insurance absent     -> enhanced-review
#   availability unreported (omitted key) -> unresolved / unknown
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

# Remainder of the D6b region: availability unreported. Written as the region
# without an insurance conjunct so that the branch is region-total (the two
# rungs above have already consumed present/absent), i.e. D6b decides every
# request in its region and D8 never reaches them.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}

# D6c — LOW country, 40 <= risk < 70, spend <= 100,000.00, as modified by O1.
# O1 suspends D6c for new vendors (yes); an unreported new-vendor status is an
# omitted key and is treated as no, so the conjunct is v_new != "yes".
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}

# D7 — MEDIUM country, risk < 40, spend <= 100,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}

# D8 — catch-all review for every remaining CLEAR request, including the
# requests O1 removed from D6c.
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}

# Total-function backstop: a sanctions value outside {CLEAR, MATCH, UNKNOWN},
# or an omitted sanctions key, is governed by no clause of this policy. It
# takes the registered default value. (Not reachable on the canonical grid.)
else := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# U1 — unreadable risk score / requested spend / country risk.
#
# Candidate substitution sets. Each set has one representative per interval of
# the input's domain that the clause set can distinguish, so quantifying over
# the set is equivalent to quantifying over the whole domain:
#
#   risk (integer 0..100). The only risk thresholds anywhere in the policy are
#   40 (D6a/D6b/D7 upper, D6c lower), 70 (D6c upper, D4 lower) and 90 (D3), all
#   read as `< 40`, `>= 40`, `< 70`, `>= 70`, `>= 90`. That partitions 0..100
#   into [0,39], [40,69], [70,89], [90,100]; every clause is constant on each
#   block. Endpoints of each block are used (min and max), which also exercises
#   the boundary literals.
#
#   spend (0.00 .. 10,000,000.00, cents). The only spend thresholds are
#   100,000.00 (D6c/D7 upper, inclusive), 500,000.00 (D6a upper inclusive /
#   D6b lower exclusive), 2,000,000.00 (D6b upper inclusive / O3 lower
#   exclusive). Blocks: [0, 100000], (100000, 500000], (500000, 2000000],
#   (2000000, 10000000]. Representatives are each block's endpoints, using the
#   next representable cent (x.01) as each open lower endpoint.
#
#   country: the domain is exactly {LOW, MEDIUM, HIGH}.
#
# A readable input contributes only its own value, so the comprehension ranges
# over exactly the unreadable inputs. If the collected determination set is a
# singleton, U1 issues it ("every readable value ... would yield the same
# determination"); otherwise the case is unresolved as unknown.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Entrypoint ladder: P1 first; then O3; then O2; then U1 (which subsumes the
# fully-readable case, where the comprehension is a singleton by construction).
# ---------------------------------------------------------------------------

# P1 — financial evidence absent: unresolved for missing required evidence.
# P1 is checked before every other clause and no override displaces it, so it
# is the first rung and nothing below it can contribute a second reason.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}

# P1 — financial-evidence availability unreported: unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}

# O3 — decided here (above O2) whenever country risk and requested spend are
# both readable. When either is unreadable, O3 cannot be settled on its own
# terms and instead takes part in U1's quantification via `determine`.
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}

# O2 is NOT settled at the entrypoint. Adjudication of the one A/B divergence
# (2026-08-15, policy v0.2): U1's counterfactual governs O2 cases like any other
# clause. Where O3's applicability cannot be excluded (country or spend
# unreadable with a critical supplier), the candidate determinations split
# between escalation and review, and the case is unresolved as unknown; where
# O3 is determinately inapplicable, every candidate lands on review and the
# singleton path issues it. O2 therefore lives only inside `determine`.

# U1 — singleton over the candidate substitutions: issue that determination.
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}

# U1 — otherwise unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}

# ---------------------------------------------------------------------------
# Diagnostics (not the scored entrypoint).
# ---------------------------------------------------------------------------
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

Probe: changing the U1 result collection from a set to an array tests whether suites depend on deduplication when several readable substitutions yield the same determination.

### `rm-rego-02.rego`

```rego
# Study 019 — contest policy draft v0.1, Rego reference implementation (arm C shape).
#
# Rego v1. Package `study`, entrypoint `data.study.decision`.
# Result shape: {"disposition": "approve|review|enhanced-review|reject|unresolved",
#                "reasons": [<sorted unresolved reason tokens>]}  (reasons [] for outcomes).
#
# Input projection (registered): vendor facts under /vendor, evidence availability under
# /evidence keyed by requirement id. An OMITTED key means "unreadable" (risk, spend,
# country) or "unreported" (yes/no statuses, evidence availability). Sanctions is always a
# present string; UNKNOWN is a value, not an omission. risk/spend arrive as JSON numbers
# (OPA parses them as exact big rationals, so all six thresholds compare exactly).

package study

# ---------------------------------------------------------------------------
# Registered default: D2's no-match is the fallback value for this entrypoint.
# (This build also names D2 explicitly inside `determine`, so that the U1
# comprehension below can quantify over it; the default is kept as registered
# and as a guard against any uncovered input.)
# ---------------------------------------------------------------------------
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# Readers. `null` / "OMITTED" are sentinels for an omitted key; the projection
# never emits a JSON null, so the sentinels cannot collide with a real value.
# ---------------------------------------------------------------------------
v_risk := object.get(input, ["vendor", "riskScore"], null)

v_spend := object.get(input, ["vendor", "requestedSpend"], null)

v_country := object.get(input, ["vendor", "countryRisk"], null)

v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)

v_new := object.get(input, ["vendor", "newVendor"], null)

v_critical := object.get(input, ["vendor", "criticalSupplier"], null)

v_prior := object.get(input, ["vendor", "priorEnforcement"], "yes")

fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")

ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")

# ---------------------------------------------------------------------------
# determine(risk, spend, country): the policy's clause ladder evaluated at a
# fully-readable assignment of the three unreadable-capable inputs. Every other
# input (sanctions, the three yes/no statuses, both evidence availabilities) is
# read from `input` directly, because none of them can be "unreadable" in U1's
# sense.
#
# Order inside the ladder mirrors the "Order of application" section:
#   O3, then O2, then D1, D2, then D3-D8 as modified by O1.
# The `else` chain gives exactly that precedence, and it also realizes the
# "earliest clause governs" tie-break: where two clauses yield the same
# determination (D3 and D4 at HIGH/risk>=90; D5 and D3; O1-suspended D6c and
# D8) the earlier rung is the one that fires.
#
# The function is TOTAL: the last rung returns the no-match value, so the U1
# comprehension below can never silently drop a candidate assignment.
# ---------------------------------------------------------------------------

# O3 — large exposure in a high-risk country. Carries the explicit financial-
# evidence conjunct the prose states; P1 has already gated above, so this is
# belt-and-braces, not a behavioural difference. O3 reads country risk,
# requested spend, sanctions and financial evidence; it does not read the risk
# score, so `risk` is deliberately unconstrained in this rung.
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}

# O2 — critical-supplier override. Never applies on MATCH/UNKNOWN.
# (Unreported critical-supplier status is an omitted key, so != "yes" -> treated as no.)
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}

# D1 — sanctions match.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}

# D2 — unreported sanctions: no determination clause applies, no clause matches.
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}

# D3 — critical risk.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}

# D4 — elevated risk in a high-risk country.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}

# D5 — prior enforcement action (unreported treated as no).
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}

# D6a — LOW country, risk < 40, spend <= 500,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}

# D6b — LOW country, risk < 40, 500,000.00 < spend <= 2,000,000.00.
#   insurance available  -> approve
#   insurance absent     -> enhanced-review
#   availability unreported (omitted key) -> unresolved / unknown
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

# Remainder of the D6b region: availability unreported. Written as the region
# without an insurance conjunct so that the branch is region-total (the two
# rungs above have already consumed present/absent), i.e. D6b decides every
# request in its region and D8 never reaches them.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}

# D6c — LOW country, 40 <= risk < 70, spend <= 100,000.00, as modified by O1.
# O1 suspends D6c for new vendors (yes); an unreported new-vendor status is an
# omitted key and is treated as no, so the conjunct is v_new != "yes".
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}

# D7 — MEDIUM country, risk < 40, spend <= 100,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}

# D8 — catch-all review for every remaining CLEAR request, including the
# requests O1 removed from D6c.
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}

# Total-function backstop: a sanctions value outside {CLEAR, MATCH, UNKNOWN},
# or an omitted sanctions key, is governed by no clause of this policy. It
# takes the registered default value. (Not reachable on the canonical grid.)
else := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# U1 — unreadable risk score / requested spend / country risk.
#
# Candidate substitution sets. Each set has one representative per interval of
# the input's domain that the clause set can distinguish, so quantifying over
# the set is equivalent to quantifying over the whole domain:
#
#   risk (integer 0..100). The only risk thresholds anywhere in the policy are
#   40 (D6a/D6b/D7 upper, D6c lower), 70 (D6c upper, D4 lower) and 90 (D3), all
#   read as `< 40`, `>= 40`, `< 70`, `>= 70`, `>= 90`. That partitions 0..100
#   into [0,39], [40,69], [70,89], [90,100]; every clause is constant on each
#   block. Endpoints of each block are used (min and max), which also exercises
#   the boundary literals.
#
#   spend (0.00 .. 10,000,000.00, cents). The only spend thresholds are
#   100,000.00 (D6c/D7 upper, inclusive), 500,000.00 (D6a upper inclusive /
#   D6b lower exclusive), 2,000,000.00 (D6b upper inclusive / O3 lower
#   exclusive). Blocks: [0, 100000], (100000, 500000], (500000, 2000000],
#   (2000000, 10000000]. Representatives are each block's endpoints, using the
#   next representable cent (x.01) as each open lower endpoint.
#
#   country: the domain is exactly {LOW, MEDIUM, HIGH}.
#
# A readable input contributes only its own value, so the comprehension ranges
# over exactly the unreadable inputs. If the collected determination set is a
# singleton, U1 issues it ("every readable value ... would yield the same
# determination"); otherwise the case is unresolved as unknown.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Entrypoint ladder: P1 first; then O3; then O2; then U1 (which subsumes the
# fully-readable case, where the comprehension is a singleton by construction).
# ---------------------------------------------------------------------------

# P1 — financial evidence absent: unresolved for missing required evidence.
# P1 is checked before every other clause and no override displaces it, so it
# is the first rung and nothing below it can contribute a second reason.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}

# P1 — financial-evidence availability unreported: unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}

# O3 — decided here (above O2) whenever country risk and requested spend are
# both readable. When either is unreadable, O3 cannot be settled on its own
# terms and instead takes part in U1's quantification via `determine`.
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}

# O2 is NOT settled at the entrypoint. Adjudication of the one A/B divergence
# (2026-08-15, policy v0.2): U1's counterfactual governs O2 cases like any other
# clause. Where O3's applicability cannot be excluded (country or spend
# unreadable with a critical supplier), the candidate determinations split
# between escalation and review, and the case is unresolved as unknown; where
# O3 is determinately inapplicable, every candidate lands on review and the
# singleton path issues it. O2 therefore lives only inside `determine`.

# U1 — singleton over the candidate substitutions: issue that determination.
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}

# U1 — otherwise unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}

# ---------------------------------------------------------------------------
# Diagnostics (not the scored entrypoint).
# ---------------------------------------------------------------------------
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

Probe: changing the omitted `priorEnforcement` default from unreported/no to `yes` tests whether suites include ordinary decisions with that optional key omitted.

### `rm-rego-03.rego`

```rego
# Study 019 — contest policy draft v0.1, Rego reference implementation (arm C shape).
#
# Rego v1. Package `study`, entrypoint `data.study.decision`.
# Result shape: {"disposition": "approve|review|enhanced-review|reject|unresolved",
#                "reasons": [<sorted unresolved reason tokens>]}  (reasons [] for outcomes).
#
# Input projection (registered): vendor facts under /vendor, evidence availability under
# /evidence keyed by requirement id. An OMITTED key means "unreadable" (risk, spend,
# country) or "unreported" (yes/no statuses, evidence availability). Sanctions is always a
# present string; UNKNOWN is a value, not an omission. risk/spend arrive as JSON numbers
# (OPA parses them as exact big rationals, so all six thresholds compare exactly).

package study

# ---------------------------------------------------------------------------
# Registered default: D2's no-match is the fallback value for this entrypoint.
# (This build also names D2 explicitly inside `determine`, so that the U1
# comprehension below can quantify over it; the default is kept as registered
# and as a guard against any uncovered input.)
# ---------------------------------------------------------------------------
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# Readers. `null` / "OMITTED" are sentinels for an omitted key; the projection
# never emits a JSON null, so the sentinels cannot collide with a real value.
# ---------------------------------------------------------------------------
v_risk := object.get(input, ["vendor", "riskScore"], null)

v_spend := object.get(input, ["vendor", "requestedSpend"], null)

v_country := object.get(input, ["vendor", "countryRisk"], null)

v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)

v_new := object.get(input, ["vendor", "newVendor"], null)

v_critical := object.get(input, ["vendor", "criticalSupplier"], null)

v_prior := object.get(input, ["vendor", "priorEnforcement"], null)

fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")

ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")

# ---------------------------------------------------------------------------
# determine(risk, spend, country): the policy's clause ladder evaluated at a
# fully-readable assignment of the three unreadable-capable inputs. Every other
# input (sanctions, the three yes/no statuses, both evidence availabilities) is
# read from `input` directly, because none of them can be "unreadable" in U1's
# sense.
#
# Order inside the ladder mirrors the "Order of application" section:
#   O3, then O2, then D1, D2, then D3-D8 as modified by O1.
# The `else` chain gives exactly that precedence, and it also realizes the
# "earliest clause governs" tie-break: where two clauses yield the same
# determination (D3 and D4 at HIGH/risk>=90; D5 and D3; O1-suspended D6c and
# D8) the earlier rung is the one that fires.
#
# The function is TOTAL: the last rung returns the no-match value, so the U1
# comprehension below can never silently drop a candidate assignment.
# ---------------------------------------------------------------------------

# O3 — large exposure in a high-risk country. Carries the explicit financial-
# evidence conjunct the prose states; P1 has already gated above, so this is
# belt-and-braces, not a behavioural difference. O3 reads country risk,
# requested spend, sanctions and financial evidence; it does not read the risk
# score, so `risk` is deliberately unconstrained in this rung.
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}

# O2 — critical-supplier override. Never applies on MATCH/UNKNOWN.
# (Unreported critical-supplier status is an omitted key, so != "yes" -> treated as no.)
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}

# D1 — sanctions match.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}

# D2 — unreported sanctions: no determination clause applies, no clause matches.
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}

# D3 — critical risk.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}

# D4 — elevated risk in a high-risk country.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}

# D5 — prior enforcement action (unreported treated as no).
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}

# D6a — LOW country, risk < 40, spend <= 500,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}

# D6b — LOW country, risk < 40, 500,000.00 < spend <= 2,000,000.00.
#   insurance available  -> approve
#   insurance absent     -> enhanced-review
#   availability unreported (omitted key) -> unresolved / unknown
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

# Remainder of the D6b region: availability unreported. Written as the region
# without an insurance conjunct so that the branch is region-total (the two
# rungs above have already consumed present/absent), i.e. D6b decides every
# request in its region and D8 never reaches them.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}

# D6c — LOW country, 40 <= risk < 70, spend <= 100,000.00, as modified by O1.
# O1 suspends D6c for new vendors (yes); an unreported new-vendor status is an
# omitted key and is treated as no, so the conjunct is v_new != "yes".
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}

# D7 — MEDIUM country, risk < 40, spend <= 100,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}

# D8 — catch-all review for every remaining CLEAR request, including the
# requests O1 removed from D6c.
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}

# Total-function backstop: a sanctions value outside {CLEAR, MATCH, UNKNOWN},
# or an omitted sanctions key, is governed by no clause of this policy. It
# takes the registered default value. (Not reachable on the canonical grid.)
else := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# U1 — unreadable risk score / requested spend / country risk.
#
# Candidate substitution sets. Each set has one representative per interval of
# the input's domain that the clause set can distinguish, so quantifying over
# the set is equivalent to quantifying over the whole domain:
#
#   risk (integer 0..100). The only risk thresholds anywhere in the policy are
#   40 (D6a/D6b/D7 upper, D6c lower), 70 (D6c upper, D4 lower) and 90 (D3), all
#   read as `< 40`, `>= 40`, `< 70`, `>= 70`, `>= 90`. That partitions 0..100
#   into [0,39], [40,69], [70,89], [90,100]; every clause is constant on each
#   block. Endpoints of each block are used (min and max), which also exercises
#   the boundary literals.
#
#   spend (0.00 .. 10,000,000.00, cents). The only spend thresholds are
#   100,000.00 (D6c/D7 upper, inclusive), 500,000.00 (D6a upper inclusive /
#   D6b lower exclusive), 2,000,000.00 (D6b upper inclusive / O3 lower
#   exclusive). Blocks: [0, 100000], (100000, 500000], (500000, 2000000],
#   (2000000, 10000000]. Representatives are each block's endpoints, using the
#   next representable cent (x.01) as each open lower endpoint.
#
#   country: the domain is exactly {LOW, MEDIUM, HIGH}.
#
# A readable input contributes only its own value, so the comprehension ranges
# over exactly the unreadable inputs. If the collected determination set is a
# singleton, U1 issues it ("every readable value ... would yield the same
# determination"); otherwise the case is unresolved as unknown.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Entrypoint ladder: P1 first; then O3; then O2; then U1 (which subsumes the
# fully-readable case, where the comprehension is a singleton by construction).
# ---------------------------------------------------------------------------

# P1 — financial evidence absent: unresolved for missing required evidence.
# P1 is checked before every other clause and no override displaces it, so it
# is the first rung and nothing below it can contribute a second reason.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}

# P1 — financial-evidence availability unreported: unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}

# O3 — decided here (above O2) whenever country risk and requested spend are
# both readable. When either is unreadable, O3 cannot be settled on its own
# terms and instead takes part in U1's quantification via `determine`.
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}

# O2 is NOT settled at the entrypoint. Adjudication of the one A/B divergence
# (2026-08-15, policy v0.2): U1's counterfactual governs O2 cases like any other
# clause. Where O3's applicability cannot be excluded (country or spend
# unreadable with a critical supplier), the candidate determinations split
# between escalation and review, and the case is unresolved as unknown; where
# O3 is determinately inapplicable, every candidate lands on review and the
# singleton path issues it. O2 therefore lives only inside `determine`.

# U1 — singleton over the candidate substitutions: issue that determination.
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}

# U1 — otherwise unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}

# ---------------------------------------------------------------------------
# Diagnostics (not the scored entrypoint).
# ---------------------------------------------------------------------------
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
```

Probe: removing `HIGH` from unreadable-country candidates tests whether suites cover counterfactual outcomes that exist only in the omitted branch.

### `MANIFEST.json`

```json
{"reviewerSetVersion":1,"mutants":[{"id":"rm-jps-01","language":"jps","file":"rm-jps-01.json","sha256":"4dd159151483f262a347ef488d8027ad5e844b4e7055db937aa4d09504ecaf2f"},{"id":"rm-jps-02","language":"jps","file":"rm-jps-02.json","sha256":"675af7a26c30cdd0996126295c5617527290d9ee2f0253d1726f3a55ad796baf"},{"id":"rm-jps-03","language":"jps","file":"rm-jps-03.json","sha256":"4e6642e9c9dca586b3797cbe1b6ee06044255767e979f9d54bb22cd67408c0c1"},{"id":"rm-rego-01","language":"rego","file":"rm-rego-01.rego","sha256":"3c9d1c8e86789064f323c5604ed384ed544fcd2e140f7b30f7cb880fa48ff44c"},{"id":"rm-rego-02","language":"rego","file":"rm-rego-02.rego","sha256":"2b6761838bc62a5a8c6f8df08950ba9e6c259d3d9f70adce50611b23d121faf3"},{"id":"rm-rego-03","language":"rego","file":"rm-rego-03.rego","sha256":"a00569f9a0b7709c65e6a55813a062de65830c45b77d3ed24951fac8b76afb6f"}]}
```

## Reviewer predictions registered 2026-08-18

These are prospective reviewer statements, separate from eventual observations:

- Arm-A suites are most likely to miss `rm-jps-01` and `rm-jps-02` because both require repaired-X1/D5 composition cases rather than ordinary readable boundary cases.
- `rm-jps-03` should be killed only by a suite containing an otherwise-approving case with insurance omitted.
- Rego suites without unreadable-input cases are likely to miss `rm-rego-01` and `rm-rego-03`.
- `rm-rego-02` should survive whenever a suite never omits `priorEnforcement`; its minimal witness is an otherwise approving D6a request with that key absent.
- Expected witness behavior: `rm-jps-01` turns a repaired LOW/new-vendor unreadable-spend review into unresolved; `rm-jps-02` turns the relevant D5 rejection into conflict/unresolved; `rm-rego-01` changes a U1 singleton-by-deduplication into unknown; `rm-rego-03` turns an unreadable-country unknown into review.

DO NOT FREEZE
