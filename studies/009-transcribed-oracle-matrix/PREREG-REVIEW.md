# Pre-freeze adversarial review — Study 009 preregistration draft

**This review happened BEFORE any freeze, deliberately** — the Study 008 lesson
(its central premise was found false only after freezing) applied as process. The
draft it reviews is the sibling `PREREGISTRATION.md` at this commit. **Verdict:
redesign. The draft is NOT frozen and no fixture, harness, or run exists.**

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`, sandbox `workspace-write`, `mcp_servers={}`, reasoning effort ultra), 2026-08-05.
**Runs:** one, completed; reproduced unedited below. No run discarded.

## Maintainer response

All thirteen findings are accepted for the revision; none is contested. The three
that reshape the study rather than repair it:

- **The draft cannot claim what issue #23 wants claimed** (findings 1, 2): with
  one author constructing policy, packs, defect, and records, the study is a
  *constructed existence witness* for the pipeline — it can show that an
  expectation stream not derived from the evaluator surfaces a planted encoding
  defect the copied stream cannot, and nothing about independently recorded human
  decisions. The revision either says exactly that in its title and endpoints, or
  redesigns for blinded/independent authorship. E1 is relabeled an unscored
  construction check either way.
- **Every channel the review names as smuggling-capable gets a structural gate**
  (findings 4, 5, 6): the derivation rule restricted to a statically checked
  projection normal form; a fabrication gate that recomputes the claim from the
  verified artifact and requires canonical equality of every evaluator input; and
  a real record-source adapter behind the acquisition proxy instead of the
  file-path shortcut the draft hand-waved (`attest.py` proxies MCP tool calls —
  the draft's "attest each record file" misdescribed the component).
- **The freeze discipline tightens to Study 008's own standard** (finding 12):
  everything executable frozen with digests before any scored run, one exact
  runtime binary, first post-freeze attempt primary.

The revised preregistration will be reviewed again before it freezes.

## Prompt (verbatim)

````
You are performing an adversarial cross-vendor review of a study PREREGISTRATION before it is frozen. You are the reviewing model; a Claude model drafted it. Your one job: find the ways this study could produce a result that looks meaningful and is not — circularity, endpoints that cannot fail, predictions that follow necessarily from construction, independence premises that are asserted rather than verified, and scope claims the design cannot support. This review happens BEFORE the freeze precisely so a defective premise dies here instead of in the analysis.

The draft is studies/009-transcribed-oracle-matrix/PREREGISTRATION.md in this working tree. Context worth reading: studies/008-portable-derivation-admission/ (the format, and its ADVERSARIAL-REVIEW.md — Study 008's central premise was found false after freezing, which is the failure this pre-freeze review exists to prevent); docs/adr/0002-trustworthy-input-acquisition-research-line.md; derivation-rule/SPEC.md and derive.py (Arm facts derivation reuses this); acquisition-proxy/SPEC.md and attest.py. The runtime context it depends on: the judgment-pack-runtime repo's ADR-0014 (matrix coverage, the circular-oracle hole) and the new experimental_test_packs MCP tool (runtime PR #77) — described in the prereg itself.

Press hard on:
1. Circularity: Arm A copies the evaluator's output into expectations; Arm B transcribes registered synthetic records derived from POLICY.md by the same author who encodes the packs. Is E1 (Arm A reports 0 mismatches) capable of failing in any world where the harness is correctly built — and if not, is the prereg honest that E1 is a construction check rather than evidence? Is E2 genuinely independent of E4? Which endpoints can only fail together?
2. The defect: is "one registered encoding defect" in pack D well-defined enough to freeze (what counts as the defect class, who decides a mismatching row is defect-class vs something else)? Can the registered record ids and DEFECT.md make E2 tautological?
3. The derivation step: facts come from derive.py under record.rule.json — can the transcription rule smuggle pack knowledge (e.g. thresholds) into the facts, reintroducing the circularity the design forbids? What structural check would catch a rule authored to make the records fit?
4. The wrapping: the registered outcome shape ({kind:"outcome", outcomeId, reasons:[], handoff:{state:"none"}}) — under what evaluator behaviors does a CORRECT pack produce an outcome disposition with non-empty reasons or a handoff, making healthy rows diverge for shape reasons rather than judgment reasons? If any exist, E3's prediction is wrong as written.
5. Scope honesty: does §9 bound the claim tightly enough (synthetic records, one author, one defect), or does any sentence in §1/§7 still promise more than the design can show?
6. Mechanics: FREEZE.json, arms, scoring — anything underspecified enough that the analysis could rationalize after the fact (e.g. "mismatching rows belong to the defect class" — decided how?).

Output format: numbered findings, each with severity (blocking / should-fix / nit / observation), the section it concerns, the concrete way the study could mislead, and the change that would fix it. If a design choice survives your attack, say so explicitly. End with a one-paragraph verdict: freeze as-is, freeze with changes, or redesign.
````

## Complete output (unedited; paths relative to the repo root)

1. **Severity: blocking — §§1, 3, 6, 7, 9; the principal contrast is engineered.**  
   **How it could mislead:** One author writes the policy, both packs, the planted mutation, the synthetic outcomes, the rule, and the records selected to cross the mutation. E2 can therefore show that a deliberately authored disagreement survives transcription; it does not instantiate §1’s motivating case of decisions independently reached by humans, nor sensitivity to an unknown defect. Pre-freezing prevents later edits but does not create oracle independence.  
   **Fix:** Either recast the study throughout as a constructed integration/existence witness, or redesign so outcomes and cases are independently adjudicated and frozen before a separate, blinded pack author sees them. Prefer a preregistered mutation family with the applied mutation selected only after the record matrix is locked.

2. **Severity: blocking — §§2, 5, 7–8; E1 is a self-replay invariant, not evidence.**  
   **How it could mislead:** Arm A evaluates `D(x)`, copies that disposition, then asks the same deterministic runtime to evaluate `D(x)` again. With identical inputs, E1 is `D(x) == D(x)` and cannot substantively fail. If it does fail, §8 is wrong to say the circular oracle “caught the defect”; the causes are input drift, nondeterminism, serialization, or harness failure. Moreover, a pack-level load failure can yield zero row mismatches because no row ran.  
   **Fix:** Relabel E1 as an unscored construction/determinism prerequisite with no evidentiary weight. Require overall status `passed`, exactly `N` rows, the exact frozen ID set, one actual disposition per row, and no load/evaluation errors. Remove “E1 together with E2 is the study’s claim.”

3. **Severity: blocking — §§3, 6–8, 10; the defect class is not operationally defined.**  
   **How it could mislead:** “One edited condition,” “the class it affects,” and an exact ID list do not establish one semantic defect. A one-member edit can interact with exceptions, conflicts, evidence, and fallback behavior. Any mismatch on an allowed ID is currently credited to the defect even if caused by malformed expectations, derivation, or evaluation refusal. If “affected” means “rows D makes mismatch,” E2 is tautological.  
   **Fix:** Freeze a machine-readable defect manifest containing:

   - The exact canonical C→D JSON patch: pointer, old value, and new value.
   - The violated policy clause.
   - An evaluator-independent predicate over case facts.
   - Disjoint defect, control, and healthy ID sets, including boundary negatives.
   - The exact expected C and D full dispositions for every defect row.

   Validate membership and the atomic patch without consulting the scored D report. Exact preregistered IDs are useful against post-hoc relabeling, but only after this semantic definition exists.

4. **Severity: blocking — §4 and E4; `record.rule.json` can be a covert oracle.**  
   **How it could mislead:** The rule DSL may branch on any artifact pointer, including recorded outcome, record ID, or control flags; enumerate records with `equals`; carry thresholds through conditions or parameters; choose different fact sources; and set evidence/status literally. Its facts are copy-only, but branch and source selection are enough to make records fit. Thus E2–E4 could all pass while pack knowledge was smuggled through the allowed rule input. A pack-free command line does not prevent hard-coded mappings or filesystem reads either. See the available condition machinery in [derivation-rule/SPEC.md](derivation-rule/SPEC.md:65).  
   **Fix:** Restrict this study’s rule to a statically checked projection normal form: one `always` clause, `parameters:{}`, no conditional or parameter operations, fixed one-to-one copies from a request-only subtree, and fixed evidence/status. Prohibit outcome, ID, defect, and control metadata paths. Add metamorphic tests proving that changing those metadata fields cannot change any evaluator input, and execute the transcriber in a read-constrained environment.

5. **Severity: blocking — §§1, 4, 10; the claimed fabrication gate is absent.**  
   **How it could mislead:** Nothing registered requires the emitted matrix facts and evidence to equal `derive.py`’s result. The transcriber could ignore or alter the derived claim using the recorded outcome, while A and B would still share the altered facts and all endpoints could pass. `origin` echoing proves only that a string survived. Also, [derive.py](derivation-rule/derive.py:279) copies fact-source pointers outside its recorded condition-read `basis`, so `basis` cannot prove this equality.  
   **Fix:** Make scoring conditional on a frozen gate that independently recomputes the claim from the verified retained artifact and requires canonical exact equality of facts, evidence availability, acquisition status, and every other evaluator input, with no extras. Require record ID and outcome ID to be copied from that same artifact. If portability is claimed, run the clean-room implementation too; agreement still does not cure rule-authoring circularity.

6. **Severity: blocking — §§3–4, 10; the acquisition procedure does not match `attest.py`.**  
   **How it could mislead:** `attest.py` does not attest arbitrary record files. It is an MCP proxy that stamps successful `tools/call` results and retains `canon(result)`, not the original record-file bytes; see [attest.py](acquisition-proxy/attest.py:287). No downstream record-source server, tool arguments, result schema, extraction path, key, or authority is registered. Meanwhile the proposed transcriber accepts record paths, permitting direct access to the originals.  
   **Fix:** Specify and freeze a deterministic record-source MCP adapter, exact request/result schema, tool and arguments, authority configuration, and the precise retained subvalue supplied to derivation. The transcriber should accept verified artifact references, not original record paths. Replace “raw record bytes” with “canonical JSON tool-result value” unless literal byte equality is separately enforced.

7. **Severity: blocking — §10; acquisition verification is incomplete and can pass vacuously.**  
   **How it could mislead:** `attest.verify` returns success for an absent receipt tree, and its specification cannot detect final-tail rollback or whole-session replay without external anchors. All endpoints could pass with zero current-run receipts or an arbitrary digest embedded in `origin`.  
   **Fix:** Before scoring, require a new empty store and the current spawned session, exactly one receipt per record, contiguous call indexes, valid HMAC/chain, expected authority/tool, recomputed arguments digests, `isError:false`, matching artifact digests, and a record-ID/request bijection. Retain a row-to-receipt manifest containing authority, session, call index, result digest, rule digest, and derived-claim digest.

8. **Severity: blocking — §§5, 7; arm isolation and causal attribution are incomplete.**  
   **How it could mislead:** Only fact equality is asserted; evidence availability, supported extensions, runtime options, pack bytes, and row completeness are not. The arms also differ in `origin`, so “differ only” is literally false. A defect-class mismatch might instead be a carrier defect or evaluation refusal. E1+E2 therefore cannot support line 124’s attribution; E3, E4, and successful complete execution are load-bearing prerequisites.  
   **Fix:** Require row-wise canonical equality of IDs, facts, evidence, supported extensions, and all evaluator options across A/B. State that only `expectedDisposition` and the non-evaluative provenance label may differ. Count a defect detection only when both expected and actual are valid dispositions and the actual C→D delta is the preregistered one; score refusals and carrier failures separately.

9. **Severity: should-fix — §7; endpoint dependencies are knowable before analysis.**  
   **How it could mislead:** E4’s byte-equality half is guaranteed by building once; it is an isolation invariant, not corroborating evidence. E2 and E4 can logically fail independently, but E4 is required for attributing E2. If C and D are guaranteed disposition-identical outside defect set F, any unexpected healthy-row mismatch makes the specificity portions of E2 and E3 fail together. If validation also guarantees D changes every F row and E3 establishes that records match C there, E2 follows from those fixture assertions.  
   **Fix:** Register the dependency map now. Separate construction checks, attribution prerequisites, and outcome checks rather than promising to disclose entailments later in `ANALYSIS.md`.

10. **Severity: should-fix — §§4, 7–9; the fixed outcome wrapper survives, but E3’s diagnosis does not.**  
    **How it could mislead:** The specific shape attack fails: under Core §8.3, reasons are empty iff the disposition is an outcome, and requested handoff requires nonempty `triggeredBy ⊆ reasons`. Therefore no conforming evaluator can produce an outcome with nonempty reasons or requested handoff; the registered wrapper is the unique legal outcome shape. See [Core §8.3](reference/judgment-pack-core.md:634). However, a correct C can legitimately return `unresolved` or `not-applicable` if derivation omits facts/evidence or the case reaches conflict, no-match, applicability, or escalation behavior. §8 wrongly assigns every extra E3 mismatch specifically to C.  
    **Fix:** Freeze the complete policy-derived disposition for every healthy record, not just its outcome ID, and treat unexpected non-outcomes initially as fixture/pipeline failures until localized. Either add complete recorded dispositions for non-outcome/reason cases or explicitly bound the study to finalized outcome rows; it cannot claim to close the circular-oracle hole for ADR-0014’s reason probes.

11. **Severity: should-fix — §§6–7; calibration controls are underconstrained.**  
    **How it could mislead:** Controls may overlap the defect class, satisfy the per-outcome/defect quotas, or use impossible or undeclared outcomes. E2 also permits D to accidentally “correct” a control. This could make coverage and calibration look stronger than they are.  
    **Fix:** Make defect, control, and healthy sets disjoint; exclude controls from all policy-correct coverage minima; require each control to use a different but declared and producible outcome; and register exact mismatch sets: `C = controls`, `D = controls ∪ defect`. Controls remain a sound design choice under these constraints.

12. **Severity: blocking — §§3, 10; the freeze and run-selection rules repeat Study 008’s mechanical vulnerability.**  
    **How it could mislead:** The explicit freeze omits the harness, scorer, tests, project configurations, source adapter, gate, and reused `attest.py`/`derive.py`. “Pinned `jpack` ≥ 0.14.0” is not one exact runtime. Keeping the preregistration draft until the all-artifact freeze also permits endpoint changes after unscored study-data runs, and “every run retained” still permits choosing the clean attempt.  
    **Fix:** Commit the reviewed protocol and dispositions before implementation. Then freeze every executable, fixture, config, manifest, dependency, and exact runtime binary/version/digest before any evaluation using the scored C/D/records; unit-test only on disjoint fixtures beforehand. Verify the committed freeze and clean state on every run. Define the first post-freeze attempt as primary, retain all attempts append-only, and preregister any retry rule.

13. **Severity: should-fix — E5; CLI/MCP equality and provenance are underspecified.**  
    **How it could mislead:** MCP wraps the report, JSON text encodings differ, and `configPath` can differ by locator spelling. “Equal modulo `command`” does not say whether it compares wire text, the MCP wrapper, or `structuredContent`. Likewise, echoing `origin` proves report transport, not attestation. E5 is primarily a shared-code-path integration check.  
    **Fix:** Freeze both invocations, working directory, selected pack, and one absolute `JPACK_CONFIG`. Compare parsed CLI JSON to MCP `structuredContent` after deleting an exact registered field list. Keep receipt verification separate from origin echoing.

The strongest surviving choices are the canonical outcome wrapper, reuse of one byte-identical B matrix as a paired C/D isolation control, exact pre-run row IDs, calibration controls once constrained, and §9’s byte-lineage-not-truth and one-defect/no-rate bounds. These are construction controls and honest limitations, not independent efficacy evidence.

**Verdict:** redesign. As written, the meaningful-looking result is largely fixed by fixture construction, while E1 is tautological and the rule can covertly reintroduce the oracle. The study could freeze after substantial changes only if recast as a narrow end-to-end integration witness; retaining the claim that independently recorded decisions close the circular-oracle hole requires independent or blinded outcome/pack authorship and ordering.


---

# Second pre-freeze review — of the first revision

**Verdict: freeze only with the named changes** — the constructed-witness
concept needs no further redesign; the revision must not freeze as written.
The third revision (the sibling `PREREGISTRATION.md` at this commit)
implements every named change; the closure table and new findings below are
the conditions it implements.

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`, sandbox `workspace-write`, `mcp_servers={}`, reasoning effort ultra), 2026-08-05.
**Runs:** one, completed; reproduced unedited below. No run discarded.

## Maintainer response — how each named change landed in the third revision

- Stage-bounded claim (new finding 1): §1's claim statement rewritten — the
  bound is on post-freeze generation, checked by reconstruction; the
  informed-author fact and the probe-evaluation provenance are disclosed
  (§5's provenance note, §10's no-bypass paragraph).
- Closed mapping and rule identity (new findings 2, 3): the record schema is
  closed with one canonical decimal representation; the rule is required to
  be canonically byte-equal to the one registered identity projection; the
  gate loads the freeze-verified rule itself, asserts its digest per row,
  and exposes no rule or params argument.
- Call contract and artifact↔record equality (new finding 4): §7.1 registers
  tool, arguments, result-is-the-record, extraction identity, authority, and
  key procedure; P-ACQ adds recomputed argumentsDigests, the one-session
  requirement, and canonical retained-artifact ≡ frozen-record equality.
- Complete-row admission (new finding 5): the gate reparses the emitted
  matrix and requires exact equality of every member per row, applies the
  wrapper itself, forbids extras, and keeps acquisition status in a gated
  sidecar because `MatrixCase` is strict.
- Load-bearing tables (new finding 6, original 3): DEFECT.json registers
  full C and D dispositions for every id; scoring compares every actual to
  its table entry; mismatch sets are entailed summaries.
- DEFECT strictness and the lexical predicate (new finding 7): strict
  manifest shape with preimage equality and RFC 8785 patched-C ≡ D; one
  canonical risk-score representation makes the lexical predicate safe.
- Dependency DAG (new finding 8, original 9): E4 folded into prerequisites;
  E2 and E3 each depend on all four pipeline prerequisites; the K coupling
  is table-verified; P-A's completeness predicate repaired (original 2).
- Hermetic freeze (new finding 9, original 12): generated configurations
  digested and matrix-bound; exact argv/cwd/JPACK_CONFIG/environment/
  interpreter/import-closure registered; the prereg commit itself named in
  FREEZE.json.
- First-attempt ledger and ordering honesty (new finding 10): the
  development bypass is gone; STARTED markers, append-only attempts, sealed
  outputs; the ordering claim is scoped to the later paths and anchored on
  the named commit; the scratchpad prototypes are disclosed in the status
  header.

## Prompt (verbatim)

````
You are performing the SECOND pre-freeze adversarial review of a study preregistration. You are the reviewing model; a Claude model drafted it. Your first review (PREREG-REVIEW.md in the study directory) rejected the previous draft with a redesign verdict and thirteen findings. The revision is studies/009-transcribed-oracle-matrix/PREREGISTRATION.md in this working tree. Your job now: (1) verify each of your thirteen findings is actually resolved by the revision — resolved in substance, not by softer wording; (2) attack the revision fresh — new circularity, new endpoints that cannot fail, new smuggling channels, mechanics still underspecified enough to rationalize after the fact.

Context: studies/008-portable-derivation-admission/ (format + its harness/study.py freeze mechanics), derivation-rule/SPEC.md + derive.py (the projection-normal-form restriction is defined against this grammar), acquisition-proxy/SPEC.md + attest.py (what wrap/attest/verify actually do — including verify's empty-store vacuous pass), fabrication-gate/gate.py (admit()'s actual checks). The runtime dependency: jpack 0.14.0's packs test / experimental_test_packs payloads (described in the prereg).

Specific pressure points:
1. Finding-by-finding: for each of the 13 original findings, state RESOLVED / PARTIALLY RESOLVED / UNRESOLVED with the revision text that does or does not resolve it.
2. The witness reframe: does §1's claim statement still overreach anywhere? Is the E2 "evidence about the pipeline and the mechanism, not about discovery" framing consistent with the rest of the document?
3. The PNF checker spec (§7.3): is the whitelist complete against derive.py's actual permissiveness? Can a rule passing the stated checks still smuggle (e.g. via the artifact-pointer side of one-to-one copies, via record_source.py itself, via params absent but the transcriber passing params anyway)?
4. The gate (§7.4): does recompute-and-compare actually bind the matrix row to the verified artifact, or is there a gap between what the gate checks and what the row carries (e.g. the wrapper's outcome id — read from the artifact, but who checks the WRAPPED disposition equals the registered wrapper shape)?
5. DEFECT.json (§5): is "C and D differ by exactly the registered patch" well-defined (canonical comparison after applying the patch)? Are the expected-disposition requirements complete enough to prevent post-hoc classification of surprises?
6. The dependency map (§9): is it honest and complete? Is P-A truly unscorable-as-evidence now?
7. Freeze/procedure (§10): any executable or input still outside the freeze? Is "first post-freeze run is primary, no retry rule" actually enforceable from the text?
8. Anything else that could make a meaningful-looking result that is not.

Output format: Part 1 — a 13-row table (# / original finding, compressed / status / where resolved). Part 2 — numbered NEW findings with severity (blocking / should-fix / nit / observation), section, concrete failure scenario, fix. End with a one-paragraph verdict: freeze as-is, freeze with named changes, or redesign again.
````

## Complete output (unedited)

## Part 1 — Closure of the original thirteen findings

Three findings are fully resolved; ten are only partially resolved.

| # | Original finding, compressed | Status | Where resolved—or not |
|---:|---|---|---|
| 1 | The contrast is engineered; it cannot evidence independent human oracles or unknown-defect discovery. | **RESOLVED** | §§1 and 11 now say “**constructed existence witness**,” disclose “every fixture…is authored by one mind” with full knowledge, and exclude real-record fidelity, detection rates, representativeness, and discovery. The remaining overreach in “provably never passes through” is a new, narrower problem below. |
| 2 | E1 is `D(x)=D(x)`, not evidence, and zero mismatches can hide a failed/empty run. | **PARTIALLY RESOLVED** | §9 correctly relabels E1 as unscored **P-A**, a “deterministic self-replay,” whose failure is never evidence. But P-A still requires only “reports 0 mismatches.” It does not require status `passed`, exactly N rows and frozen IDs, N actual dispositions, or no load/evaluation errors. A pack/matrix load failure can still report zero row mismatches. |
| 3 | The defect class was not operationally defined; any allowed mismatch could be credited post hoc. | **PARTIALLY RESOLVED** | §5 now registers the patch, violated clause, independent F predicate, disjoint sets, boundaries, and C/D dispositions for F. However, E2 accepts **any valid D disposition** different from the expectation; it never compares actual D with DEFECT.json’s registered D disposition. The new fields are therefore not yet load-bearing. |
| 4 | `record.rule.json` can be a covert oracle. | **PARTIALLY RESOLVED** | §7.3 removes branching, declared parameters, evidence variation, and status variation. But arbitrary `/vendor` source selection and arbitrary destination pointers remain programmable; the vendor schema and exact projection are not closed, runtime params remain possible, and the requested read-constrained execution is absent. |
| 5 | No fabrication gate bound emitted evaluator inputs to the verified artifact. | **PARTIALLY RESOLVED** | §7.4 adds `admit()`, recomputation, and comparisons for facts/evidence/status plus statements about IDs. It does not bind the complete serialized row—especially `expectedDisposition`, `origin`, `supportedExtensions`, and absence of extras—to a reconstruction from the artifact. Nor does it bind the executed rule object to the PNF-checked frozen rule. |
| 6 | Acquisition misdescribed `attest.py`; no real MCP adapter contract existed. | **PARTIALLY RESOLVED** | §§3 and 7.1 introduce `record_source.py`, retain `canon(result)`, and pass artifact references rather than record paths. Still absent: exact tool name, arguments, result schema, extraction pointer, authority, key procedure, downstream command, and equality between retained result data and `records/<caseId>.json`. |
| 7 | `attest.verify` is vacuous on an empty store and does not establish current-run completeness. | **PARTIALLY RESOLVED** | §7.2 adds a fresh store, non-vacuity, counts, contiguous indexes, authority/tool checks, non-error results, and a case/receipt bijection. It does not require exactly the currently spawned session, recompute each request’s `argumentsDigest`, bind result data to the requested case, or retain the proposed row-to-receipt/rule/claim digest manifest. |
| 8 | Arm isolation and causal attribution omitted carrier fields, completeness, and expected actual deltas. | **PARTIALLY RESOLVED** | §4 adds equality of IDs, facts, evidence, and supported extensions; §8 separates refusals and carrier failures. But configuration/evaluator options and full row completeness remain outside P-ISO, and E2 requires only a valid mismatch rather than the preregistered D disposition or C→D delta. |
| 9 | Endpoint dependencies should be registered; construction invariants must not be double-counted. | **PARTIALLY RESOLVED** | §9 candidly says E2’s F-half follows from fixtures if the pipeline is faithful and is mechanism evidence, not discovery. But E4 remains scored although its components are construction checks, the stated K coupling is not logically valid without C=D on K, and E3’s dependence on acquisition/PNF/gate fidelity is omitted. |
| 10 | The wrapper is valid, but unexpected non-outcomes cannot automatically be blamed on C. | **RESOLVED** | §5 registers complete C dispositions for H/K and C/D dispositions for F; unexpected non-outcomes become fixture/pipeline failures. §11 explicitly limits the study to outcome rows and disclaims ADR-0014 reason probes. |
| 11 | Calibration controls could overlap F, satisfy coverage quotas, or use impossible outcomes. | **RESOLVED** | §§5–6 make H/F/K disjoint, use H alone for coverage minima, require declared/producible wrong K outcomes, and register `C=K`, `D=F∪K`. |
| 12 | Freeze omitted executables/dependencies and allowed tuning or run selection. | **PARTIALLY RESOLVED** | §10 now names the harness, tests, source, gates, reused modules, fixtures, and exact jpack binary; it names the first post-freeze run as primary. But project configuration, invocation/environment, Python runtime, key procedure, imported dependency closure, and protocol/review digests remain outside the freeze. The development bypass permits real-fixture rehearsals, and crash/discarded attempts remain invisible. |
| 13 | E5’s CLI/MCP comparison domain and provenance were underspecified. | **PARTIALLY RESOLVED** | §8 now compares parsed CLI JSON with MCP `structuredContent`, deleting exactly `["command"]`, and keeps receipt verification separate. Exact argv, working directory, selected pack, absolute `JPACK_CONFIG`, and common configuration digest remain unspecified. |

## Part 2 — New findings

1. **Blocking — §§1, 7, E4: “provably never passes through the evaluator or pack” remains too strong.**  
   **Failure scenario:** The same informed author can seed record outcomes from C’s evaluator output before freeze, while `record_source.py` or `transcribe.py` can read the packs or invoke jpack. Every endpoint can still show the registered pattern. Moreover, expectations necessarily enter the evaluator later as `packs test` inputs; the intended claim is about their generation, not whether they ever “pass through” it.  
   **Fix:** State the stage-bounded property: after records are frozen, each emitted `expectedDisposition` is reconstructed solely from the verified record artifact and is not generated from evaluator output during transcription. Enforce output noninterference through the complete-row gate below or use hermetic read/exec allowlists. §§9 and 11’s “mechanism, not discovery” framing is otherwise consistent.

2. **Blocking — §7.3: the proposed PNF remains a programmable transform, not a fixed projection.**  
   **Failure scenario:** With an open `vendor` object, a record can contain `/vendor/oracleRisk` or a duplicate outcome-derived flag, and a PNF-passing rule can copy it to `/vendor/riskScore` or `/vendor/sanctionsHit`. Mutating `/decision/outcome` leaves that duplicate unchanged, so the registered metamorphic test passes. Actual `derive.py` pointer behavior adds further gaps: `/vendorOutcome` can pass a naïve prefix check; `/vendor~1x` addresses a root key named `vendor/x`; `/vendor/a~` and `/vendor/a~0` alias; and injective destinations `/x` then `/x/y` clobber one copy.  
   **Fix:** Freeze a closed vendor schema and the exact complete mapping—apparently `/vendor/sanctionsHit → /vendor/sanctionsHit` and `/vendor/riskScore → /vendor/riskScore`. Require scalar leaves only, canonical RFC 6901 syntax, decoded first token exactly `vendor`, and no aliases or ancestor/descendant destinations.

3. **Blocking — §§7.3–7.4: the whitelist, executed rule, and params channel are not closed.**  
   **Failure scenario:** [`derive.py`](derivation-rule/derive.py:221) accepts ignored extra members, defaults an absent `parameters` member to `{}`, permits undeclared runtime params, and returns an effectively unconstrained `reason`. A transcriber can read an ignored member, `reason`, raw rule whitespace, or params as an oracle map. Separately, P-PNF checks a file, while both `admit()` and `derive_canonical()` accept caller-supplied rule objects; passing the same alternate rule to both makes recomputation agree.  
   **Fix:** Specify exact recursive member sets, require `"parameters": {}`, fix `reason` to one literal, reject duplicate/noncanonical rule bytes, and ban ignored members. The gate must load the freeze-verified PNF rule itself, assert its digest per row, expose no rule/params argument, and pass literal `{}` internally.

4. **Blocking — §§3, 7.1–7.2: attestation does not bind the artifact to the registered record.**  
   **Failure scenario:** [`attest.py`](acquisition-proxy/attest.py:287) retains the entire MCP `result`, not the record file. `record_source.py` can ignore or transform the selected file, add oracle metadata, or return another case; attestation and the derivation gate will faithfully bless those bytes. The unspecified normal MCP result wrapper also makes the assumed top-level `/vendor` path ambiguous.  
   **Fix:** Register one exact tool, exact `{"caseId": id}` arguments, a closed CallToolResult shape and extraction pointer, authority, downstream command, and key procedure. Recompute `argumentsDigest`; require exactly one current session; and require canonical equality between the designated result subvalue and the corresponding frozen record.

5. **Blocking — §§7.4–7.5: P-GATE does not admit the complete emitted row, and one stated comparison is impossible.**  
   **Failure scenario:** [`fabrication-gate/admit()`](fabrication-gate/gate.py:52) knows nothing about row ID, expectation, origin, or extensions. On a K control whose record says `manual-review`, the transcriber can emit `reject`; both remain valid mismatches over C and D, so E2 and E3 pass. Merely “reading” the record outcome does not bind it. Also, jpack 0.14’s strict [`MatrixCase`](judgment-pack-runtime:internal/evaluation/corpus.go:48) has no `acquisitionStatus`; adding that field makes the matrix unloadable.  
   **Fix:** Reparse the emitted matrix and require exact equality for every row: ID, admitted facts/evidence, `supportedExtensions: []`, canonical wrapper of `artifact.decision.outcome`, and registered origin. Reject extras and error expectations. Keep acquisition status and lineage in a gated sidecar. Bind each jpack configuration to the gated matrix digest.

6. **Blocking — §§5, 8: DEFECT.json’s disposition tables are decorative, and D behavior on K is unregistered.**  
   **Failure scenario:** If D produces `reject` on every F row where DEFECT.json predicts `unresolved/no-match`, E2 still passes because `reject` is a valid disposition and differs from `manual-review`. An unexpected C or D disposition on K can likewise remain a mismatch and escape both endpoint predicates.  
   **Fix:** Register complete C and D dispositions for every H/F/K ID and mechanically compare every actual disposition with its table entry. Treat the mismatch sets as derived summaries entailed by those comparisons plus exact record-wrapper binding—not separate evidence.

7. **Should-fix — §5: the patch and defect predicate need a stricter data contract.**  
   **Failure scenario:** RFC 6902 `replace` has `path` and `value`; `old/new` is a custom manifest shape. Current text does not explicitly require the preimage at `path` to equal `old`, reject duplicate members, or name the canonicalizer. The F predicate is also lexical: `"70.0"` is mathematically equal to `"70"` under Core ordered comparison and is affected by `>= → >`, but `riskScore == "70"` excludes it.  
   **Fix:** Freeze a strict DEFECT schema; require exactly one replace, preimage equality with `old`, and RFC 8785 equality of patched C with D. Define F using Core decimal parsing and mathematical equality to 70, or enforce one canonical risk-score representation.

8. **Should-fix — §9: the dependency map still overstates independence.**  
   **Failure scenario:** “A K row failing to mismatch fails both E2 and E3” is false unless C and D are first required to have identical registered behavior on K. E4’s byte reuse and metamorphic tests are construction checks, while E3 depends on P-ACQ/P-PNF/P-GATE just as E2 does. E5 is primarily a shared-code-path integration check.  
   **Fix:** Register a dependency DAG after adding full C/D tables. Move E4 into prerequisites, attach pipeline prerequisites to both E2 and E3, and state which mismatch-set results are entailed. P-A is now genuinely unscored as evidence, but its completeness predicate still needs the repair identified in original finding 2.

9. **Blocking — §§8, 10: executable and runtime inputs remain outside the freeze.**  
   **Failure scenario:** The gate can approve one matrix while a generated `jpack.json` points jpack at another. CLI and MCP can select different configurations through cwd, `--config`, or `JPACK_CONFIG`. Python version, `PYTHONPATH`, helper imports, source launch argv, the key, and environment can also change behavior without violating the enumerated digests.  
   **Fix:** Freeze—or deterministically generate, retain, and digest—every project configuration and its matrix binding. Register exact CLI/MCP requests, cwd, one absolute `JPACK_CONFIG`, selected IDs, sanitized environment, Python interpreter identity, key lifecycle, and the complete imported executable closure.

10. **Blocking — §10: “first post-freeze run” is not enforceable and the proposed ordering proof checks the wrong revision.**  
    **Failure scenario:** `STUDY009_ALLOW_UNCOMMITTED_FREEZE=1` explicitly permits rehearsing the real C/D/records, tuning, refreezing, and then calling the next attempt primary. A crash before output or deletion before commit is invisible. In this history, `git log --diff-filter=A` identifies commit `ba80d5b`, which added the rejected draft—not this revision or its second review. The supplied scratchpad also already contains exact-named C/D prototypes under `../s009-build/packs/`, contradicting the unqualified statement that no fixture exists.  
    **Fix:** Remove real-fixture development runs; pre-freeze tests must use disjoint fixtures. Before any primary work, atomically create and fsync an exclusive `STARTED` marker, never overwrite/delete attempt directories, retain failure/exit metadata, and seal outputs. Record the exact revision-and-second-review commit and blobs in FREEZE.json and verify ancestry. Disclose the existing prototypes and narrow the claim to “no frozen study fixture or scored run.”

**Verdict:** freeze only with the named changes—closed exact PNF mapping and call contract, retained-result-to-record equality, freeze-bound rule with literal empty params, complete serialized-row admission, full C/D disposition scoring, repaired P-A/dependency semantics, and a hermetic freeze plus non-bypassable first-attempt ledger. The constructed-witness concept no longer needs another conceptual redesign, but the current revision should not freeze: its central structural proof can still be bypassed while producing exactly the meaningful-looking E2/E3 pattern it predicts.
