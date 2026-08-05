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
