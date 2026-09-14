# Pre-freeze review record — Study 022

Cross-vendor review rounds on the preregistration, the binding specification and the
registered matrices, under the interim review regime: each round's prompt verbatim, the
reviewer's findings verbatim, and the maintainer's disposition of every finding. The freeze is
the squash-merge of the pull request this record names once a round returns `freezable as
written`.

## Round 1 — reviewed `60d6409f` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `60d6409f7688eda57b6f9df273570fec70730ce6`. The reviewer had neither the
virtual environment holding the pinned packages nor the gateway binary; the harness tests did
not import for it, and its pinned-library conclusions are deductions from the libraries'
documented contracts, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
**Verdict: `not freezable as written`.**

The strongest finding is reproducible without the gateway or pinned packages: the scorer’s evidence validator accepts synthetic records for all nineteen cells, and its adjudicator returns **19 holds**, despite every gateway findings array being empty and every successful attestation observation being absent.

I reviewed worktree commit `60d6409f7688eda57b6f9df273570fec70730ce6`, the requested Study 022 files, the pinned gateway specification and corpus vector through `git show`, Study 014’s registration and binding, and Study 021’s review rounds 1–3. No primary attempt ran and no files changed.

Execution limits and checks:

- The requested unittest command failed during import: `ModuleNotFoundError: securesystemslib`. No harness test bodies executed.
- The manifest matches **26 files**. The repository freeze-set checker reports **10 studies checked, zero problems**.
- All **eight baseline gateway-input files** match the pinned corpus materialization, authority and public key byte-for-byte.
- Both attestation payloads contain the expected predicates and subjects. Their signatures verify independently over DSSE PAE using the available cryptography package. This does **not** substitute for executing the pinned DSSE or Statement libraries.
- Exact tagged package-source retrieval was unsuccessful. Pinned-library outcomes below are deductions from their documented contracts, not observed executions. DSSE authenticates both payload type and payload; its key identifier is an unauthenticated selection hint. [DSSE protocol](https://github.com/secure-systems-lab/dsse/blob/master/protocol.md)

**Findings**

1. **BLOCKER — incomplete and internally unsupported observations can satisfy every endpoint and both controls.**

   **Locations:** [score.py:99](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/score.py:99), particularly `observation_ok()`, followed by `reduce_observation()` and `adjudicate()`.

   **Registered commitment:** PREREGISTRATION §6 requires complete records of all three layers; §5 makes incomplete evidence pipeline-invalid.

   **What happens:** The validator accepts empty attestation arrays, never derives their required membership from the stored receipts, and does not reconcile:

   - gateway statuses or `ok` with gateway findings;
   - either adapter layer’s `pass` with its individual results;
   - attestation identities, uniqueness, complete subject coverage or permitted codes.

   The reduction then trusts those summaries. A positive control containing these records is accepted:

   ```json
   {
     "gateway": {"ok": true, "statuses": ["ok"], "findings": []},
     "intoto": {"pass": true, "attestations": []},
     "binding": {"pass": true, "attestations": []},
     "combined": "pass"
   }
   ```

   **Probe:** I executed the actual validation, reduction and adjudication functions in memory, extracting them without importing unavailable dependencies. Synthetic records containing only each expectation’s failure entries yielded **19/19 accepted records and 19/19 holds**. With otherwise-valid pins, marker and reconstructed cells, the subsequent decision branch selects `R1 holds`. I did not execute registered scoring.

   Observation provenance is also too weak: the file carries an attempt ID and one gateway digest, but no per-cell input digest checked against the snapshot actually observed.

   **Smallest sufficient edit:** derive the required attestation set from each reconstructed cell; require complete, unique records and valid phase-dependent fields; recompute layer summaries and gateway statuses from retained evidence; bind each observation to the exact input snapshot and execution identity. Missing evidence must invalidate the pipeline before reduction.

   Also fix `run_layers.py:29–38`: it ignores the gateway’s return code. Under gateway §4.1, a nonzero exit means no verdict, even if stdout contains parseable JSON.

2. **BLOCKER — the in-toto layer trusts an attacker-replaceable public key.**

   **Location:** [verify_attestation.py:115](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_attestation.py:115).

   **Source:** Adapter SPEC §5 step 3 requires the pinned adapter key. The implementation instead loads `attestations/adapter.pubkey.json` from the cell and trusts its supplied key ID and material. `pins.adapter_keyid()` checks the independently derived signer, not the key this verifier actually loaded.

   Rebinding both baseline statements with `foreign_signer()` also replaces that public-key file. The gateway and binding pass, and the current in-toto implementation accepts the foreign signatures. The registered key has ceased to be the trust anchor.

   Existing `b02` misses this because it substitutes one envelope while retaining the original public-key file.

   **Smallest edit:** pass the trusted public key into verification from outside the cell, using pinned baseline key material. Do not repair this by comparing only the cell file’s claimed `keyid`; compare or independently supply the actual key material. Holdout `h01` below exercises this boundary.

3. **BLOCKER — duplicate subject names erase failed checks and violate binding cardinality.**

   **Locations:** [verify_attestation.py:110](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_attestation.py:110) and [verify_binding.py:41](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_binding.py:41).

   **Source:** Adapter SPEC §5 step 5 checks every subject; §3 rule 3 requires exactly one citation subject per citation entry.

   Both implementations turn subjects into dictionaries keyed by name. Prepending a bad `cites/s2/0` subject while retaining the original good one produces:

   ```text
   individual checks: cites/s2/0=mismatch, ..., cites/s2/0=match
   retained map:      cites/s2/0=match
   binding code:      pass
   ```

   I reproduced the binding result with DSSE decoding stubbed and executed the actual subject re-digest functions against the baseline. The failed re-digest disappears before the layer verdict is computed.

   **Smallest edit:** preserve individual subject results until all checks are evaluated; enforce citation multiplicity, not merely name-set equality. Reject this extra citation subject with `fail:cites-subject-set`. Define how §6 retains duplicate-name failures so a later match cannot erase one. Holdout `h02` supplies this case.

4. **BLOCKER — installed-distribution hashes do not establish which implementation was imported.**

   **Locations:** [pins.py:36](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:36), the early imports in `cells.py`, `run_layers.py` and `run_attempt.py`, and `make_manifest.py:16`.

   **Registered commitment:** §2 says pinned packages are enforced and patched installations cannot pass as the releases.

   The hash checks inspect distribution metadata and its listed files. They do not verify the origins of imported modules. Meanwhile, adapter and harness directories are prepended to `sys.path`, and nested packages under those directories are outside the manifest’s `adapter/*.py` and `harness/*.py` globs.

   For example, an unmanifested `adapter/in_toto_attestation/` package can shadow the installed distribution while metadata still identifies the genuine installation. A replacement Statement validator that always succeeds would leave all nineteen current outcomes unchanged: none reaches an expected `invalid:bindings` outcome.

   This is the same import-origin distinction Study 014 explicitly addressed. I did not execute a package-shadowing installation here.

   **Smallest edit:** validate imported module origins against the pinned distribution and cover or reject unpinned importable files in prepended roots. State and enforce the necessary dependency/interpreter pins too: `harnessPython` is currently descriptive, while cryptography and protobuf behavior is outside the package pins.

5. **BLOCKER — “byte for byte” reconstruction uses shallow file comparison.**

   **Location:** [score.py:78](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/score.py:78).

   **Source:** PREREGISTRATION §2 and §6 require reconstructed cells to equal retained cells byte-for-byte.

   `filecmp.dircmp().diff_files` uses shallow comparison. Equal file type, size and modification time can establish equality without reading contents. Its default ignored names also weaken exact-tree membership.

   **Probe:** The baseline and retained development `a01` artifacts have different bytes and equal lengths. With equal modification-time metadata supplied in memory, `filecmp.cmp()` returned `True`; `shallow=False` returned `False`.

   **Smallest edit:** enumerate an explicit exact path/type set and compare every regular file’s bytes or cryptographic digest. Reject unexpected symlinks and ignored extras. Use the same strict comparison in the determinism tests.

6. **MAJOR — the two strata have contradictory decision rules and are not separately reported.**

   **Locations:** PREREGISTRATION lines 60–65 versus 78–83; [score.py:168](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/score.py:168).

   **Exact conflict:** R1 includes the holdout with `--include-holdout`; §1a says the locked stratum alone decides R1 and holdout divergences report separately. The scorer concatenates both matrices and lets every endpoint divergence change R1.

   The claimed inherited holdout remedy is also weaker than Study 014’s. Construction has no pre-freeze guard; the pilot runner automatically includes a populated holdout. Adding holdout functions to `CELLS` also breaks the current test equating `CELLS` with the locked matrix alone.

   **Smallest edit:** consistently define locked-only R1, preserve stratum labels, and emit separate holdout concordance. Validate that the two matrices form a disjoint, complete construction registry. If the Study 014 prospective holdout remedy is intended, guard holdout construction from pilots and pre-freeze determinism tests. Otherwise explicitly describe these as potentially pretested reviewer challenge cells.

7. **MAJOR — `c01` achieves its expected outcome without constructing the foreign gateway receipt chain it describes.**

   **Location:** [cells.py:177](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/cells.py:177), especially line 194; `MATRIX.json:538`.

   **Source:** Gateway §1.2a specifies the signature domain prefix:

   ```text
   judgment-pack-gateway/receipt/3:
   ```

   The construction signs:

   ```text
   judgment-pack-gateway-receipt-v3:
   ```

   It also leaves the action’s citation naming the acquisition’s old signature.

   **Independent check of retained development artifacts:** both signatures fail under the specified prefix and verify under the construction’s incorrect prefix. The action’s `prevSignature` is updated, but its citation is stale.

   The expected gateway tuple still follows: both receipts stop at `key-mismatch`, before signature verification or action joins. Thus endpoint agreement cannot establish the stated remint mechanism.

   **Smallest edit preserving the current tuple:** use the correct prefix, update the action citation before signing it, and explicitly describe a coherent foreign receipt chain presented against the unchanged trusted corpus registry. Verify the foreign signatures and citation consistency during construction validation.

   If the intended construction also remints the registry under the foreign key, gateway §4 drops that seal; then add `unregistered-session` to the expected gateway statuses.

8. **MAJOR — post-marker failures do not receive the promised terminal adjudication, and registered roots are unrestricted.**

   **Locations:** [run_attempt.py:31](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/run_attempt.py:31); `score.py:137–167`.

   **Source:** §5 promises every terminal path after the marker is recorded in `ADJUDICATION.json`; the primary root is registered as literal.

   Construction errors, verifier subprocess failures, malformed observation JSON and several scorer refusals exit without adjudication. The root remains spent, which is good, but the terminal record is absent. Both commands also accept arbitrary roots as `REGISTERED`; `marker_problems()` ignores `attemptRoot`.

   **Smallest edit:** enforce the resolved primary root for registered execution/scoring, validate marker-root identity, and add one post-marker terminal handler that exclusively records pipeline-invalid on failures and interruptions. Preserve existing adjudications and report failure to write the terminal record explicitly.

9. **MAJOR — malformed inputs can escape the declared ceremony instead of producing its codes.**

   **Locations:** `verify_attestation.py:97–111`, `check_subject():64`, and `verify_binding.py:38–41`.

   **Source:** Adapter SPEC §5 defines ordered failures, including Statement-type rejection and unknown subjects.

   A correctly signed JSON array payload reaches `statement.get()` and raises `AttributeError`. A descriptor named `cites/x` reaches unpacking and raises `ValueError`. Several binding shape accesses similarly occur outside its unreadable-input handler.

   Additionally, Statement validation is applied to a reconstructed projection containing only subject names/digests, rather than the complete supplied descriptors. The specification should not claim validation of fields the adapter discards first.

   **Probe:** with the DSSE phase stubbed successful, the actual `verify_one()` raised `AttributeError` for payload `[]`.

   **Smallest edit:** check shapes before member access; implement the specified unknown-subject handling; validate the supplied recognized Statement/descriptor fields or explicitly specify the accepted projection. Put the binding code vocabulary and failure precedence into its SPEC, including malformed-input handling. Keep execution/I/O failures on the validity channel.

10. **MAJOR — the ownership account attributes study-written checks to an independently developed verifier.**

    **Locations:** PREREGISTRATION lines 71–73 and 139–141; adapter SPEC §4 and §7.

    **Source/code distinction:** upstream DSSE performs signature verification; the Statement bindings perform structural validation. This study implements receipt enumeration, attestation presence, application type restrictions, subject resolution and file re-digesting.

    Those choices are partly acknowledged in the limits, but the categorical description of the entire in-toto layer as an independently developed verifier is too strong. In particular, `b04`, `b06`, and the non-gateway detection in `a06` exercise consumer policy.

    **Smallest edit:** describe a **study-written consumer ceremony using unmodified DSSE verification and Statement validation**. Distinguish upstream checks from consumer checks in R2 and the ownership reasons.

    Also correct “an attestation carries none of these” at lines 125–128: its signed predicate contains gateway identity and chain fields. The ceremony does not interpret or verify their gateway semantics.

**MINOR wording corrections:** PREREGISTRATION lines 142–144 say the appended receipt is “missed” because an attestation is required; the matrix correctly says **detected**. Line 92’s “Nothing in it was authored for this study” should be restricted to the corpus inputs, excluding study-authored attestations. Lines 9–13 should describe repeated observations as expected under unchanged implementations, rather than guaranteed.

**Audit of every registered cell**

For the **concrete current constructions**, I found no demonstrably incorrect reduced tuple among the nineteen. `c01` has an incorrect construction/reason despite a correctly predicted tuple.

In this table, `0`, `1`, and `2` abbreviate `s2/<index>.dsse.json`. `pass` means `pass:true, failures:{}`. Every combined verdict is `fail` except `pos-baseline`.

| Cell | Gateway: `ok`; distinct statuses | In-toto | Binding | Does each expectation follow? |
|---|---|---|---|---|
| `pos-baseline` | true; `ok` | pass | pass | Yes. Corpus verdict, valid envelopes, matching subjects and predicates. |
| `neg-dsse-signature-flipped` | true; `ok` | 1: `fail:signature` | pass | Yes. The mutation changes decoded signature bytes; binding verifies no signature. |
| `a01-artifact-edited` | false; `artifact-mismatch, ok` | 1: artifact `mismatch` | pass | Yes. Gateway ladder and consumer re-digest reject changed action-result bytes. Remaining passing receipt 0 forms a complete prefix. |
| `a02-cited-receipt-member-edited` | false; `ok, sequence-broken, signature-mismatch` | 1: `cites/s2/0` `mismatch` | 0: `fail:predicate-differs-from-store` | Yes. Gateway citations compare the unchanged signature string, not the cited receipt’s verification result. Excluding receipt 0 breaks the passing sequence. |
| `a03-cited-receipt-removed` | false; `citation-unresolved, ok, sequence-broken, tail-rollback` | 1: `cites/s2/0` `missing` | pass | Yes. Enumeration, count and citation fail as specified. Both adapter layers ignore orphan attestation 0. |
| `a04-decision-record-rewritten` | false; `decision-record-mismatch, ok` | 1: decision-record `missing` | pass | Yes. The original candidate digest disappears. The baseline record contains no `cites` member, so step 7 adds nothing. |
| `a05-registry-seal-removed` | false; `ok, unregistered-session` | pass | pass | Yes. Only the gateway consumes the registry. |
| `a06-receipt-appended-after-seal` | false; `count-exceeds-seal, misfiled, ok` | 2: `fail:missing-attestation` | 2: `fail:missing-attestation` | Yes. The copied receipt retains index 1; its exclusion leaves the original valid chain. Both adapter layers demand its attestation by file enumeration. |
| `a07-action-member-edited` | false; `ok, signature-mismatch` | pass | 1: `fail:predicate-differs-from-store` | Yes. Receipt 1 fails its signature; receipt 0 remains a complete prefix. Attested subjects are unchanged. |
| `b01-envelope-payload-edited` | true; `ok` | 1: `fail:signature` | 1: `fail:predicate-differs-from-store` | Yes. Payload alteration breaks PAE authentication and predicate equality. |
| `b02-envelope-resigned-foreign-key` | true; `ok` | 1: `fail:untrusted-key` | pass | Yes, because this construction retains the original key file. |
| `b03-subject-swapped-resigned` | true; `ok` | pass | 1: `fail:artifact-subject-mismatch` | Yes. The replacement artifact exists and re-digests; only its relationship to the predicate fails. |
| `b04-predicate-type-changed-resigned` | true; `ok` | 1: `invalid:predicate-type` | pass | Yes, by the consumer’s pinned-type rule. |
| `b05-statement-type-changed-resigned` | true; `ok` | 1: `invalid:statement-type` | pass | Yes. The explicit type check runs before binding validation. |
| `b06-attestation-deleted` | true; `ok` | 1: `fail:missing-attestation` | 1: `fail:missing-attestation` | Yes, by per-stored-receipt enumeration. |
| `b07-payload-type-changed` | true; `ok` | 1: `fail:payload-type` | pass | Yes. Type rejection precedes signature verification; PAE would also have changed. |
| `b08-predicate-receipt-edited-resigned` | true; `ok` | pass | 1: `fail:predicate-differs-from-store` | Yes. Valid envelope and unchanged subjects do not establish predicate/store identity. |
| `b09-cited-subject-dropped-resigned` | true; `ok` | pass | 1: `fail:cites-subject-set` | Yes. Remaining subjects satisfy Statement validation; binding requires the missing citation subject. |
| `c01-store-reminted-other-gateway-key` | false; `key-mismatch` | pass | pass | Tuple: yes. Mechanism: defective. All receipts stop before signature verification; the original valid seal still matches file count, and action joins do not run. |

The seven store edits and nine attestation edits otherwise perform their named mutations deterministically on this baseline. The negative control’s base64-character change alters signature bytes without making the envelope unparseable. The extra formatting changes in receipt edits affect raw cited-receipt hashing as intended. I could not execute complete reconstruction or pinned-library determinism tests.

README and DEVIATIONS correctly remain outside the manifest; `.gitignore` excludes pilots and caches while leaving results publishable. The primary root and `results/` are absent. Null freeze hashes and the currently empty holdout are appropriate draft state; they must be completed, together with the named freeze PR, before registered execution.

**Reviewer holdout array**

These are contract-derived expectations. `h01` and `h02` deliberately disagree with the current implementation and require findings 2–3 to be repaired. No holdout construction was materialized or executed through the three-layer pipeline. The array has six unique endpoint IDs and internally consistent combined verdicts.

```json
[
  {
    "id": "h01-foreign-key-file-and-envelopes",
    "role": "endpoint",
    "attackerCapability": "selective-keys",
    "expected": {
      "gateway": {"ok": true, "statuses": ["ok"]},
      "intoto": {
        "pass": false,
        "failures": {
          "s2/0.dsse.json": "fail:untrusted-key",
          "s2/1.dsse.json": "fail:untrusted-key"
        }
      },
      "binding": {"pass": true, "failures": {}},
      "combined": "fail"
    },
    "ownership": "in-toto ceremony: the independently pinned adapter key; gateway and binding are silent",
    "structure": "foreign attestation key substituted together with both envelopes",
    "reason": "Adapter SPEC section 5 step 3 requires the pinned adapter key. Replacing a public-key file beside the envelopes cannot replace that trust anchor. Both foreign key ids are untrusted. Gateway inputs, predicates and subjects remain the baseline.",
    "construction": "Call bind.bind(cell / 'store', cell / 'attestations', signer=foreign_signer()). This overwrites adapter.pubkey.json and both envelopes using the existing deterministic foreign_signer(), without changing any gateway input."
  },
  {
    "id": "h02-duplicate-citation-subject-bad-first",
    "role": "endpoint",
    "attackerCapability": "full-keys",
    "expected": {
      "gateway": {"ok": true, "statuses": ["ok"]},
      "intoto": {
        "pass": false,
        "failures": {
          "s2/1.dsse.json": {"cites/s2/0": "mismatch"}
        }
      },
      "binding": {
        "pass": false,
        "failures": {
          "s2/1.dsse.json": "fail:cites-subject-set"
        }
      },
      "combined": "fail"
    },
    "ownership": "in-toto subject re-digest and binding citation multiplicity; gateway is silent",
    "structure": "two subjects with the same citation name, with the incorrect digest first",
    "reason": "Both descriptors have valid Statement shapes and the DSSE signature is valid. Adapter SPEC section 5 step 5 checks every subject, so the first cites/s2/0 digest mismatches even though the later one matches. Section 3 rule 3 requires exactly one citation subject for the baseline's one citation; two violate cites-subject-set. A map overwrite must not erase either failure.",
    "construction": "Load st = statement_of(cell, 1). Insert {'name': 'cites/s2/0', 'digest': {'sha256': '0' * 64}} at index 0 of st['subject'], retaining all original subjects in their original order. Call resign(cell, 1, st). Change nothing else."
  },
  {
    "id": "h03-unreferenced-record-malformed-cites",
    "role": "endpoint",
    "attackerCapability": "tamper",
    "expected": {
      "gateway": {
        "ok": false,
        "statuses": ["ok", "record-citation-malformed"]
      },
      "intoto": {"pass": true, "failures": {}},
      "binding": {"pass": true, "failures": {}},
      "combined": "fail"
    },
    "ownership": "gateway decision-record join only",
    "structure": "a new unreferenced decision record with malformed citations",
    "reason": "Gateway SPEC section 4 step 7 examines every citing record independently of whether an action names it. A top-level cites value of null is malformed. The baseline decision record remains available, all existing subjects still match, and no predicate or receipt changes.",
    "construction": "Write exactly b'{\"cites\":null}\\n' to the new regular file cell / 'decisions' / 'audit' / 'h03.json'. Retain every baseline file unchanged."
  },
  {
    "id": "h04-action-tail-removed-orphan-kept",
    "role": "endpoint",
    "attackerCapability": "tamper",
    "expected": {
      "gateway": {
        "ok": false,
        "statuses": ["ok", "tail-rollback"]
      },
      "intoto": {"pass": true, "failures": {}},
      "binding": {"pass": true, "failures": {}},
      "combined": "fail"
    },
    "ownership": "gateway seal count only",
    "structure": "valid acquisition prefix retained, action receipt removed, orphan attestation kept",
    "reason": "The remaining receipt 0 verifies and its sequence is a complete prefix, but one stored receipt is below the sealed count of two. No action remains for gateway steps 5 and 6, and the baseline record has no cites member for step 7. Both adapter layers enumerate stored receipts, so only attestation 0 is checked and passes.",
    "construction": "Delete only receipt_path(cell, 1). Retain attestation s2/1.dsse.json, both artifacts, the registry and the decision book unchanged."
  },
  {
    "id": "h05-jsonl-crlf-and-empty-lines",
    "role": "endpoint",
    "attackerCapability": "tamper",
    "expected": {
      "gateway": {"ok": true, "statuses": ["ok"]},
      "intoto": {"pass": true, "failures": {}},
      "binding": {"pass": true, "failures": {}},
      "combined": "pass"
    },
    "ownership": "none: the registered decision-record candidate remains present",
    "structure": "decision-book bytes change while its nonempty record candidate is preserved",
    "reason": "Gateway SPEC section 4 step 6 and adapter SPEC section 5 step 5 split on LF, remove one trailing CR and ignore empty pieces. The original record candidate therefore remains byte-identical despite changed whole-file bytes. No whole-file digest is required by this baseline's action, and all other checks remain unchanged.",
    "construction": "Let p = cell / 'decisions' / 'audit' / 'evaluations.jsonl' and data = p.read_bytes(). Assert data.endswith(b'\\n') and data.count(b'\\n') == 1. Write b'\\r\\n' + data[:-1] + b'\\r\\n\\r\\n' to p. Change nothing else."
  },
  {
    "id": "h06-empty-subject-list-resigned",
    "role": "endpoint",
    "attackerCapability": "full-keys",
    "expected": {
      "gateway": {"ok": true, "statuses": ["ok"]},
      "intoto": {
        "pass": false,
        "failures": {
          "s2/1.dsse.json": "invalid:bindings"
        }
      },
      "binding": {
        "pass": false,
        "failures": {
          "s2/1.dsse.json": "fail:artifact-subject-mismatch"
        }
      },
      "combined": "fail"
    },
    "ownership": "in-toto Statement validation and binding artifact requirement; gateway is silent",
    "structure": "validly signed statement with no subjects",
    "reason": "The payload and predicate types remain pinned and the DSSE signature verifies, but Statement validation requires at least one subject, producing invalid:bindings at adapter SPEC section 5 step 4. The binding first compares the unchanged predicate successfully, then fails section 3 rule 2 because no artifact subject exists.",
    "construction": "Load st = statement_of(cell, 1), set st['subject'] = [], and call resign(cell, 1, st). Change nothing else."
  }
]
```
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 2's prompt
names it as the reviewed SHA). "Mutation" names the entries of the mutation table below that
break the fix and fail the suite.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/score.py` `observation_problems()` replaces `observation_ok()`: the required attestation set is derived from the rebuilt cell's store; one in-toto record and one binding record per stored receipt, in order, with codes from each vocabulary and phase-dependent members (no statement or subjects after a failed envelope, no subjects after an invalid statement, subject outcomes as a list of `[name, outcome]`); the gateway's `statuses` are recomputed from its findings and `ok` by the gateway's own rule (`verify.go`: false exactly when a finding is not `ok`), with a finding per stored receipt at least; each layer's `pass` and the combined verdict are recomputed; the observation carries `cellSha256`, a digest of the cell tree taken before the layers ran and checked again after, compared with the digest of the cell the scorer rebuilt; the observations file is stamped with the attempt id, the gateway's digest, the interpreter version and the trusted-key file's digest, each checked. `harness/run_layers.py` `gateway_layer()` refuses a non-zero exit as no verdict whatever stdout holds (gateway `SPEC.md` §4.1). Any shortfall is a validity failure before reduction (PREREGISTRATION §6). | M5, M6, M6b, M6c, M7, M8, M15, M17 |
| 2 | BLOCKER | accepted | `adapter/verify_attestation.py` `verify()` takes the trusted key as an argument; `trusted_key(path)` reads it from the study's fixture `fixtures/baseline/attestations/adapter.pubkey.json`, never from the cell; `harness/run_layers.py` hands that file in; `harness/pins.py` `trusted_pubkey_problems()` holds the file to the pinned key id **and** the key material recomputed from the seed; the observations record the file's digest. `adapter/SPEC.md` §2 and §5 step 3 say the cell's key file is not trusted. Tests: a binding under `foreign_signer()` (key file and both envelopes replaced) is `fail:untrusted-key` on both attestations; deleting the key file beside the envelopes changes neither adapter layer's result. | M1, M19, M20 |
| 3 | BLOCKER | accepted | `verify_one()` retains every subject outcome in the statement's order as `[name, outcome]`; `per_name()` reduces to the first outcome that is not `match`; `attestation_passes()` requires every retained outcome to match. `adapter/verify_binding.py` compares the citation subjects by multiplicity (`sorted(present) != sorted(cited)`), so a second subject under a citation's name is `fail:cites-subject-set`. `adapter/SPEC.md` §3 rule 3 states the multiplicity, §6 the per-name rule. Test: a duplicated `cites/s2/0` with the bad digest first keeps `mismatch` and breaks the binding. | M2, M3 |
| 4 | BLOCKER | accepted | `harness/pins.py` `import_origin_problems()` requires the module each of `securesystemslib`, `in_toto_attestation`, `cryptography` and `google.protobuf` is imported from to be a file of its pinned distribution; `cryptography` 47.0.0 and `protobuf` 5.29.6 are pinned by version and installed-files digest; `harnessPython.version` 3.8.20 is enforced exactly, and the marker and the observations record the interpreter; `harness/make_manifest.py` covers `adapter/**` and `harness/**` recursively and refuses an unexpected directory or a symbolic link under those roots. PREREGISTRATION §2 states all of it. | M11, M16 |
| 5 | BLOCKER | accepted | `harness/score.py` `tree_map()`/`same_tree()`: the same path set, the same kinds, every regular file by SHA-256, a symbolic link refused; used by the scorer and by the determinism tests. Test: equal size, equal mtime, different bytes is not the same tree; an extra `__pycache__` directory is not. | M4 |
| 6 | MAJOR | accepted | R1 is locked-only (PREREGISTRATION §1, §1a, §5); the scorer decides on the locked rows and reports the holdout in its own section (`holdout.cells`, `holdout.diverging`, `holdout.unconstructed`); it refuses a locked matrix that is not `CELLS`, a holdout matrix that is not `HOLDOUT_CELLS`, or strata that share an id. `harness/cells.py` keeps `HOLDOUT_CELLS` apart from `CELLS`; the pilot runner builds the locked stratum only; the tests build the locked constructions only and check of the holdout that each id has a construction function without calling it; a holdout construction that raises inside the registered attempt is recorded in `HOLDOUT-CONSTRUCTION.json`, its partial tree removed, and reported as `unconstructed` without touching R1. The prospective guard, and the function-level tests of the round-1 fixes that touch the boundaries `h01`/`h02`/`h06` probe, are disclosed in §1a. | M18 |
| 7 | MAJOR | accepted | `c01_store_reminted_other_gateway_key()` signs under the gateway's prefix `judgment-pack-gateway/receipt/3:` over the gateway's canonical form, updates `prevSignature` and the citation's `signature` to the foreign acquisition's before signing the action, and verifies each signature during construction; the registry is unchanged, so the expected statuses stay `["key-mismatch"]`. `harness/MATRIX.json` `c01`'s `structure` and `reason` now describe that chain. Test: both signatures verify under the specification's literal prefix (spelled in the test, not read from the module), the chain and the citation are coherent, the registry is byte-identical to the baseline's. | M12, M13 |
| 8 | MAJOR | accepted | `harness/run_attempt.py` refuses any root but `results/primary-attempt-001` for a registered attempt; the marker records `attemptRoot` and `harness/score.py` `marker_problems()` checks it for `REGISTERED`; a `terminal()` handler records `pipeline-invalid` in `ADJUDICATION.json` exclusively (`open(..., "x")`) on any exception or interruption after the marker and re-raises, printing when even that cannot be written; the scorer refuses an existing adjudication as before. PREREGISTRATION freeze block and §5 say so. | M9, M10 |
| 9 | MAJOR | accepted | Shapes are checked before members are read in both verifiers: a JSON payload that is not an object is `invalid:not-object`; a `subject` that is not a list fails validation; a subject whose name or digest is not of the registered shape, or a `cites/…` name without exactly three segments and a digit index, is `unknown-subject`; the binding layer's `fail:unreadable` covers the envelope, the payload, the subjects and the stored receipt. `descriptor()` hands the bindings every supplied descriptor member (a member the bindings define no field for fails validation), so validation is of the Statement as supplied. `adapter/SPEC.md` §3a gives the binding codes and their precedence, §5 the shape rules per step; an I/O failure propagates to the validity channel in both layers (read before the parse `try`). Tests: malformed payloads get codes, never exceptions; an unreadable path raises. | M14 |
| 10 | MAJOR | accepted | `adapter/SPEC.md` §4 and §5 describe "a study-written consumer ceremony using unmodified DSSE verification and unmodified Statement validation", each step marked `[consumer]` or `[upstream]`; PREREGISTRATION §1 and §4 split the in-toto cells by whose check sees them (neg, b01, b02 upstream; b04, b05, b06, b07 consumer pins); SPEC §7 and PREREGISTRATION §4 correct "an attestation carries none of these": the predicate carries `keyId`, `prevSignature` and the signatures as copied bytes the ceremony does not interpret. | — (wording) |
| minor | — | accepted | PREREGISTRATION §4: a06 is *seen* by in-toto and the binding by the ceremony's rule; §2: only the corpus inputs were not authored for the study; preamble: repeated observations are *expected under unchanged implementations*, not guaranteed. | — (wording) |
| holdout | — | placed | The reviewer's six-cell array is `harness/MATRIX-HOLDOUT.json`, byte for byte (a bare array; `load_matrix()` reads a list or an object with `cells`). The constructions `h01`–`h06` are implemented from the array's `construction` strings as `HOLDOUT_CELLS` in `harness/cells.py` and have not been built anywhere; the registered attempt is their first construction (§1a). The array's dict-form `failures` compare under the per-name rule of §6. | — |

### Mutation table (each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| M1 the in-toto layer loads the key file beside the envelopes when present | FAILED (1) |
| M2 `per_name()` keeps the last outcome | FAILED (3) |
| M3 citation subjects compared as a set, not by multiplicity | FAILED (1) |
| M4 `same_tree()` back to `filecmp.dircmp` | FAILED (2) |
| M5 empty attestation records accepted | FAILED (1) |
| M6 recorded `intoto.pass` trusted | FAILED (1) — survived at first because the combined-verdict check caught the flip; the test now also lies consistently (layer and combined together) |
| M6b recorded `binding.pass` trusted | FAILED (1) |
| M6c recorded gateway `ok` trusted | FAILED (1) |
| M7 recorded gateway `statuses` trusted | FAILED (2) |
| M8 snapshot digest ignored | FAILED (1) |
| M9 marker root unchecked | FAILED (1) |
| M10 runner accepts any registered root | FAILED (1) |
| M11 import origins unchecked | FAILED (1) |
| M12 c01 signs under the old, wrong prefix | FAILED (1) — survived at first because the test verified under the module's constant; it now spells the specification's prefix literally |
| M13 c01 leaves the citation's signature stale | FAILED (1) |
| M14 an unreadable envelope reported as `fail:unparseable` | FAILED (1) |
| M15 gateway exit code ignored | FAILED (1) — survived at first because the real binary prints nothing when it refuses; the test now uses a stand-in that prints a verdict and exits 2 |
| M16 interpreter pin unenforced | FAILED (1) |
| M17 subjects accepted after an invalid statement | FAILED (1) |
| M18 a registered marker accepted over the locked cells alone | FAILED (1) |
| M19 the binding layer consults the key file | FAILED (1) — survived at first (no test removed the file); the test now deletes it |
| M20 the in-toto layer reads the key file unconditionally | FAILED (1 + 1 error) |

No mutation is labeled equivalent: all twenty-two are discriminated. Suite: 31 tests, all
passing, under the virtual environment with `GATEWAY_BIN` set to the pinned binary.

### Pilot after the round

`pilots/r2` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures — the same reduced
tuples as before the round for every cell; the round changed what the harness can accept, not
what the layers see.

## Round 2 — reviewed `c58fad05` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `c58fad05b9647891429bb7a14219cc445889b802`, with the virtual environment and
the pinned gateway binary named in the prompt. The read-only sandbox blocked temporary-file
creation, so 21 of the 31 tests errored for the reviewer and no cell was built; its probes ran
in memory over retained files, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 2. Round 1 (your own review of commit 60d6409f) returned `not freezable as written` with five BLOCKER and five MAJOR findings, three minor wording corrections and a six-cell holdout array; the maintainer accepted every finding. The round-1 record — your prompt and findings verbatim, the maintainer's disposition table naming what changed per finding, a mutation table, and the post-round pilot — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit c58fad05b9647891429bb7a14219cc445889b802 of the study branch (the worktree you are in).

Your job this round:
1. Verify every disposition against the code, not the table: for each of findings 1–10, decide whether the change closes the finding as you stated it, or leaves a residue (say which lines). Pay particular attention to: finding 1 (does `observation_problems()` in harness/score.py now refuse every record that is not a complete, self-consistent, snapshot-bound observation of the rebuilt cell? try to construct one it accepts wrongly); finding 2 (is the trusted key really handed in from outside the cell everywhere, and held to key material, not only key id?); finding 3 (duplicate-name retention and citation multiplicity in both adapter layers, and the per-name rule in adapter/SPEC.md §6); finding 4 (import-origin checks, the cryptography/protobuf/interpreter pins, and manifest coverage of nested directories — can a shadow package still slip in?); finding 6 (is R1 locked-only in every place — preregistration, scorer, runner, tests — and is the holdout guarded from pilots and tests as §1a claims? judge the disclosed function-level tests of the round-1 fixes: is the disclosure sufficient, or does it pretest the holdout?); finding 7 (is c01 now a coherent foreign chain under the specified prefix with the citation updated, and does the expected tuple still follow, registry unchanged?); finding 8 (the literal root, the marker root check, the terminal handler); finding 9 (shape checks and I/O on the validity channel in both verifiers; the binding codes and precedence in SPEC §3a).
2. Confirm that harness/MATRIX-HOLDOUT.json is your round-1 array byte for byte (a bare JSON array), and that the six constructions in harness/cells.py `HOLDOUT_CELLS` implement your construction strings faithfully — by reading, not by running: the preregistration commits that no holdout cell is built before the freeze, so do not build one. If a construction does not implement your string, say exactly how.
3. Re-audit the locked matrix where the round changed anything (c01's structure and reason; the SPEC wording on ownership, the per-name rule, the binding codes) and say whether every expectation still follows from the three specifications.
4. Read the mutation table critically: where a mutation's claimed detection is cheap to check by reading the test, check it; flag any test that would pass under a plausible breakage of its fix.
5. Anything new the round introduced (a regression, an overclaim, an inconsistency between the preregistration, the SPEC, the matrices and the code).

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory:
    GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes; if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-1 dispositions (closed / residue), then an audit line per changed locked cell, then any amendment to your holdout array (an amended or added cell is kept byte for byte, as the original was), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed commit `c58fad05b9647891429bb7a14219cc445889b802`. The scorer still accepts incomplete evidence for **19/19 locked cells**, and a new validation rule would reject h03’s correctly specified gateway finding.

The authorized suite attempted **31 tests: 10 passed, 21 errored** because the read-only sandbox could not create temporary directories. No cell was built. No primary attempt or pilot ran, and no files changed. Subsequent probes used memory and existing files only.

Paths below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — observation completeness remains unenforced.**

   **Locations:** [harness/score.py:143](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/score.py:143), especially lines 164–185.

   Gateway coverage is a count of findings containing `callIndex` or `file`. Duplicate findings, findings naming nonexistent receipts, and additional join findings can satisfy that count. Gateway statuses have no vocabulary check.

   Subject validation checks the format of recorded pairs without comparing their names, order or multiplicity with the snapshot’s Statement. Consequently, replacing the action’s three subject results with either `[["artifact","match"]]` or `[["invented","match"]]` is accepted. Integer `1` also satisfies the supposedly Boolean adapter summaries.

   **Reproduction:** I modified in-memory copies of the retained round-2 locked observations: successful subject evidence became invented names, unsuccessful attestations retained only their failing subjects, and receipt findings were duplicated while preserving status sets. The actual validator accepted **19 records**, and the actual adjudicator returned **19 holds**. This was a scorer probe, not registered scoring.

   **Smallest sufficient edit:** validate gateway finding identities and categories against the reconstructed inputs; require each Statement’s complete ordered subject-result sequence, including duplicates; enforce field types, phase-dependent members and vocabularies before reduction. Matching summaries and snapshot stamps cannot substitute for that coverage.

2. **BLOCKER — legitimate decision-record findings invalidate the pipeline, including h03’s expected result.**

   **Location:** `harness/score.py:158–159`.

   The validator requires a string `sessionId` on **every** gateway finding. Gateway `SPEC.md@03582d9`, §4 step 7, lines 440–463, specifies record findings as `{recordDigest, status}`, without `sessionId`.

   Therefore, if h03 produces its registered `record-citation-malformed` finding, scoring rejects it as “a gateway finding is not a finding.” This prevents ordinary adjudication of the whole attempt. A generic, specification-shaped `record-citation-unresolved` record reproduced the rejection in memory; h03 itself was neither built nor observed.

   **Smallest edit:** validate receipt, session and decision-record findings using their respective schemas. Require `recordDigest` for record findings and validate their applicable status vocabulary.

3. **BLOCKER — execution identity can still differ from the pinned source identity.**

   **Locations:** [harness/pins.py:36](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:36), lines 54–67 and 108–109; `harness/make_manifest.py:29–30`.

   The four checks examine package roots, not the loaded DSSE, Statement, cryptography and protobuf implementation modules. An authentic parent does not establish an authentic child.

   More directly, installed-package hashing excludes `.pyc`, and the manifest excludes bytecode caches. CPython can execute cached code while reporting the genuine source path as `__file__`. The source hash and origin-membership check then both pass.

   **Reproduction:** a read-only `SourceFileLoader` probe supplied replacement cached code with matching source metadata. That code executed under the genuine installed `statement.py` origin; `import_origin_problems()` returned `[]`, and the installed-source digest remained pinned. No installed file or production module was replaced.

   Ordinary new source-package directories under `adapter/` or `harness/` are now rejected. That closes the original example, but not the claimed execution-integrity boundary.

   **Smallest sufficient edit:** establish trusted import locations before study imports, check the implementation modules actually loaded, and prevent execution from unpinned caches or sourceless code. `-B` alone only prevents cache writes. Also enforce the declared interpreter implementation; lines 110–113 currently enforce its version only.

4. **MAJOR — three holdouts are pretested, and construction still has an unrestricted route.**

   **Locations:** [PREREGISTRATION.md:107](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/PREREGISTRATION.md:107); `harness/tests/test_study.py:142–170,205–213`; `harness/cells.py:297–308`.

   The disclosure says the tests touch boundaries “without building or observing those cells.” That distinction is not supported:

   - The h01 test produces the same foreign key file and both foreign envelopes against the baseline store, then checks both adapter layers.
   - The h02 test copies the baseline, performs the exact insertion and re-signing specified by h02, and asserts its decisive outcomes.
   - The h06 test performs the exact empty-subject construction and asserts both expected adapter codes.

   Naming the directory `pos-baseline` does not make those different constructions. The disclosure acknowledges related testing but understates its equivalence.

   Separately, `build()` dispatches through `ALL_CELLS` without a freeze or attempt check. The command-line route accepts an explicit holdout ID before freeze. The pilot runner’s locked-only default is correctly implemented, but it is not the claimed prospective guard.

   **Smallest edit:** describe h01, h02 and h06 explicitly as pretested reviewer challenge cells. Preserve prospectivity claims only for untested constructions, and require a validated registered-attempt context at holdout construction entry points. Remove the unrestricted holdout CLI route.

5. **MAJOR — the scorer checks the marker’s claimed root, not the root being scored.**

   **Locations:** [harness/score.py:226](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/score.py:226), lines 232–233; `marker_problems():74–75`.

   The runner correctly rejects another registered root. The scorer accepts `--attempt-root` elsewhere provided its marker **claims** the literal primary root. No comparison connects the marker’s root with the directory supplying the evidence.

   A copied, otherwise admissible attempt with no adjudication can therefore be scored elsewhere as registered.

   **Smallest edit:** require the actual resolved scoring root to equal the literal primary root, and require `marker.attemptRoot` to equal that actual root. The terminal handler is otherwise a substantive repair: it catches construction/subprocess exceptions and interruptions, writes exclusively, and re-raises.

6. **MAJOR — malformed nested inputs still escape as exceptions, and outer verifiers misclassify unreadable paths.**

   **Locations:** [adapter/verify_binding.py:59](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_binding.py:59), lines 61–64 and 82; `adapter/verify_attestation.py:173–174`; SPEC §3a and §5.

   When predicate and stored receipt agree, an action with `decision: "x"` raises `AttributeError` at line 61. An action with `cites: [null]` raises at line 64. Both were reproduced using memory-backed inputs. These shape accesses remain outside the malformed-input handler.

   The helper functions now propagate read errors correctly. However, both outer `verify()` functions use `is_file()` to decide absence. An envelope path occupied by a directory becomes `fail:missing-attestation`, instead of reaching the promised validity-channel read failure. The I/O test exercises only the helpers.

   Subject digest shape is also checked only for string type: a SHA-256 value `"x"` produces `missing`, despite §5’s reference to the registered digest shape.

   **Smallest edit:** validate nested members before access and specify their malformed-input code in §3a. Distinguish genuine absence from a present nonregular/unreadable path in the outer verifiers. Validate digest syntax before using it in a path.

7. **MAJOR — the final binding check undoes legitimate citation multiplicity.**

   **Location:** `adapter/verify_binding.py:64–71`; SPEC §3 rule 3.

   The new multiset comparison correctly catches an extra citation subject. But after it succeeds, `expected |= set(cited)` discards citation multiplicity, and line 70 compares the complete subject list with that set.

   A predicate containing the same citation twice, accompanied by exactly two corresponding subjects, satisfies “one per entry.” The gateway specification imposes no citation-uniqueness requirement. Nevertheless, the binding returns `fail:foreign-subject`. I reproduced this using memory-backed inputs.

   **Smallest edit:** after enforcing artifact, decision and citation cardinalities, make rule 4 check only whether any subject name is outside the allowed names. Preserve the citation multiset check.

8. **MAJOR — valid supplied descriptor fields can be rejected by the new conversion.**

   **Location:** [adapter/verify_attestation.py:85](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_attestation.py:85), particularly line 94; SPEC §5 step 4.

   JSON descriptor `content` is base64 text. `descriptor()` passes that string directly to the Python constructor’s bytes-valued `content` parameter, producing `TypeError` and then `invalid:bindings`.

   I added `content` containing the actual artifact’s base64 bytes to an in-memory baseline descriptor. The pinned protobuf JSON conversion and complete upstream Statement validation accepted it; the adapter conversion rejected it. Thus validation “as supplied” is still inaccurate.

   **Smallest edit:** use the pinned protobuf JSON conversion, or implement its field conversions explicitly before calling the bindings. Retain the declared unknown-field policy.

9. **MAJOR — the snapshot and tree checks still do not establish the promised exact path/type identity.**

   **Locations:** [harness/run_layers.py:31](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/run_layers.py:31); `harness/score.py:90–103,122–124`.

   `tree_digest()` omits directories. An empty receipt-session directory changes gateway enumeration and can produce `unregistered-session` without changing that digest.

   `tree_map()` rejects descendant symlinks, but does not inspect its root itself. A retained cell root that is a symlink is followed by `kept.is_dir()` and then compared successfully with its target. It also treats every nondirectory entry as a file without requiring a regular-file type.

   **Smallest edit:** use one strict typed-tree representation for reconstruction and observation digests, including directory entries; reject root symlinks and nonregular entries before reading bytes.

10. **MINOR — the mutation tests discriminate the listed edits more narrowly than the disposition suggests.**

    **Locations:** [harness/tests/test_study.py:133](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/tests/test_study.py:133), lines 176–224, 266–305 and 315–345.

    Reading supports the claimed detection of the listed mutations as described, including the corrected consistent-summary, literal-prefix and gateway-exit tests. I could not reproduce their reported execution results.

    Plausible breakages still survive:

    - Removing the trusted-key **material** comparison leaves the current genuine-key assertions passing.
    - Dropping unknown descriptor members survives the “extra member” case because its empty predicate independently causes `invalid:bindings`.
    - Returning the wrong binding failure code for malformed payloads survives assertions that merely require membership in `CODES` and a nonpass result.
    - Counting duplicate receipt findings or dropping subject coverage survives the observation tests.
    - Including holdout divergences in R1, or removing terminal recording, is not exercised by the current suite.

    **Smallest edit:** add targeted assertions isolating these properties. Use synthetic records for stratum and terminal-handler checks so they require no holdout construction.

11. **MINOR — residual ownership wording still misattributes a check and denies carried data.**

    **Locations:** `PREREGISTRATION.md:181–185`; `harness/MATRIX.json:207`; `harness/score.py:9–11`; `README.md:11–20`.

    `b02` is grouped with upstream signature verification, but `verify_one()` returns `fail:untrusted-key` at lines 108–110, before calling upstream verification. This is the consumer’s key-selection rule.

    `a05` still says an attestation has “no session,” although its predicate carries `sessionId`. The scorer’s introductory docstring still says any registered divergence falsifies R1. README retains the older unqualified verifier description.

    **Smallest edit:** attribute b02 to consumer key selection; describe a05 as carrying session identity without validating registry membership; make the scorer docstring locked-only and align README with the revised consumer-ceremony description.

The round-1 dispositions resolve as follows:

| Round-1 finding | Verdict | Code-based assessment |
|---|---|---|
| **1 — observations** | **Residue** | Attestation membership and summary checks improved; findings 1, 2 and 9 remain. |
| **2 — trusted key** | **Closed** | `run_layers.py:28,60` supplies the external fixture key; `pins.py:74–77` compares both ID and actual public material. The cell key is not consulted. |
| **3 — duplicate subjects** | **Residue** | Ordered retention, first-nonmatch reduction and rejection of an extra citation subject are correct. Legitimate repeated citations fail the final check: finding 7. |
| **4 — implementation pins** | **Residue** | All four package/version/digest checks and interpreter-version enforcement are present and currently match. Executed-code provenance remains incomplete: finding 3. |
| **5 — byte comparison** | **Residue** | Shallow comparison is removed; file contents are hashed. Root/type and snapshot-directory gaps remain: finding 9. |
| **6 — strata** | **Residue** | The actual R1 decision uses locked rows only; holdout results report separately. Prospectivity and construction guarding remain defective: finding 4. |
| **7 — c01** | **Closed** | Correct prefix, foreign key ID, chain, citation update and unchanged registry are implemented. Independent checks of retained r2 signatures passed. |
| **8 — root/terminal record** | **Residue** | Runner root restriction and terminal handling are repaired. Actual scoring-root identity is unchecked: finding 5. |
| **9 — shapes/I/O/codes** | **Residue** | Top-level shapes and helper read handling improved; nested shapes, outer presence handling and descriptor conversion remain defective: findings 6 and 8. |
| **10 — ownership** | **Residue** | The main ceremony description is corrected. The narrower wording defects in finding 11 remain. |

The three separately listed round-1 wording corrections are closed: expected repeatability, corpus-only authorship, and a06’s detection through the presence rule.

I re-audited the locked matrix. **Only c01’s construction and matrix text changed directly; every locked expected tuple still follows for its concrete construction.** Below, `0`, `1`, and `2` denote the corresponding `s2/<index>.dsse.json`. Gateway `ok` is true exactly for rows listing only `ok`; combined is `fail` except for the positive control.

| Locked cell | Gateway statuses | In-toto | Binding | Audit |
|---|---|---|---|---|
| `pos-baseline` | `ok` | pass | pass | Valid baseline, complete matching subjects. |
| `neg-dsse-signature-flipped` | `ok` | 1: `fail:signature` | pass | Signature check owns detection. |
| `a01-artifact-edited` | `artifact-mismatch, ok` | 1/artifact: `mismatch` | pass | Both re-digests detect changed bytes. |
| `a02-cited-receipt-member-edited` | `ok, sequence-broken, signature-mismatch` | 1/citation: `mismatch` | 0: predicate differs | Each layer’s distinct check still applies. |
| `a03-cited-receipt-removed` | `citation-unresolved, ok, sequence-broken, tail-rollback` | 1/citation: `missing` | pass | Orphan attestation remains outside enumeration. |
| `a04-decision-record-rewritten` | `decision-record-mismatch, ok` | 1/record: `missing` | pass | Original record candidate disappears. |
| `a05-registry-seal-removed` | `ok, unregistered-session` | pass | pass | Tuple correct; reason needs finding 11’s edit. |
| `a06-receipt-appended-after-seal` | `count-exceeds-seal, misfiled, ok` | 2: missing attestation | 2: missing attestation | Presence policy detects the extra file. |
| `a07-action-member-edited` | `ok, signature-mismatch` | pass | 1: predicate differs | Subjects remain unchanged. |
| `b01-envelope-payload-edited` | `ok` | 1: `fail:signature` | 1: predicate differs | PAE and document comparison detect alteration. |
| `b02-envelope-resigned-foreign-key` | `ok` | 1: `fail:untrusted-key` | pass | External key selection rejects it before verification. |
| `b03-subject-swapped-resigned` | `ok` | pass | 1: artifact mismatch | Replacement artifact exists; predicate relationship fails. |
| `b04-predicate-type-changed-resigned` | `ok` | 1: `invalid:predicate-type` | pass | Consumer type pin. |
| `b05-statement-type-changed-resigned` | `ok` | 1: `invalid:statement-type` | pass | Consumer version pin. |
| `b06-attestation-deleted` | `ok` | 1: missing attestation | 1: missing attestation | Genuine absence follows both presence rules. |
| `b07-payload-type-changed` | `ok` | 1: `fail:payload-type` | pass | Type pin precedes signature verification. |
| `b08-predicate-receipt-edited-resigned` | `ok` | pass | 1: predicate differs | Valid envelope does not establish store identity. |
| `b09-cited-subject-dropped-resigned` | `ok` | pass | 1: citation subject set | Remaining subjects validate; required citation is absent. |
| `c01-store-reminted-other-gateway-key` | `key-mismatch` | pass | pass | Coherent foreign chain; unchanged seal matches count; ladder rejection prevents action joins. |

For c01 specifically, the retained r2 signatures independently verify under the literal prefix `judgment-pack-gateway/receipt/3:`; `prevSignature` and the action citation name the new acquisition signature; the registry is byte-identical to baseline. The revised structure and reason are sound.

The holdout file is a **bare JSON array**, exactly matching the array extracted from the verbatim round-1 findings, including whitespace and final newline:

```text
6638 bytes
SHA-256 10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six implementations faithfully implement their construction strings, by inspection:

| Holdout | Construction audit |
|---|---|
| `h01` — `cells.py:248–250` | Exact foreign-signer rebinding of the key file and both envelopes; gateway inputs untouched. |
| `h02` — `cells.py:253–257` | Exact bad citation descriptor inserted first; originals retained; action re-signed. |
| `h03` — `cells.py:260–262` | Exact requested bytes written to the new audit file. Its expected tuple is correct; scorer handling is defective. |
| `h04` — `cells.py:265–267` | Only action receipt 1 is deleted. |
| `h05` — `cells.py:270–275` | Exact preconditions and CRLF/empty-line transformation. |
| `h06` — `cells.py:278–282` | Action subject list emptied and re-signed; nothing else changed. |

**No amendment to the holdout array.** Its six expectations remain correct. Correct the provenance disclosure for h01, h02 and h06 and retain the array byte for byte.

The current 26-file manifest matches; all non-freeze pins match; all eight baseline gateway-input files match the pinned corpus materialization. The freeze-set checker reports ten studies checked and zero problems. The null freeze hashes are appropriate draft state, and `results/` is absent.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 3's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-2 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/score.py`: `finding_problem()` validates every gateway finding by category against the shapes `verify.go` emits at the pinned commit — receipt findings by call index or by file, chain findings with a null index, session findings (counted for `tail-rollback`/`count-exceeds-seal`), record findings by `recordDigest` — with the status vocabulary of the binary; exactly one receipt-level finding per stored receipt file, each in a stored session; Boolean summaries by type (an integer is refused); in-toto and binding records of exactly the recorded members. Beyond the record's own coherence, `main()` re-runs the three layers over the rebuilt cell (`run_layers.observe`) and refuses any observation not equal to that output — the reviewer's invented-subject record is refused there, and an end-to-end test drives that through the real pipeline. PREREGISTRATION §6 says so. | N1, N16/N16b, N17, N18 |
| 2 | BLOCKER | accepted | Record findings are validated as `{recordDigest, status}` with no session id (gateway SPEC §4 step 7); a test asserts the h03-shaped finding is accepted and a record finding carrying a session id is refused. | N2 |
| 3 | BLOCKER | accepted | Every harness process (runner, layer runner, scorer, tests) sets `sys.dont_write_bytecode` and an empty `sys.pycache_prefix` before any study or package import, and the runner passes both to its children through the environment, so no bytecode beside a source is read; `harness/pins.py` `execution_problems()` checks every loaded module of the four distributions (not their roots) to be a distribution file under a `SourceFileLoader` or `ExtensionFileLoader` with its cache path under the empty prefix (a namespace package only inside the distribution's location; cryptography's deprecation proxy unwrapped to the module it holds), every study module to be from the study tree, the prefix to hold no file, and the interpreter to be the pinned implementation (`platform.python_implementation()`) and version. PREREGISTRATION §2 states the policy and its enforcement. | N3a, N3b, N3c, N3d |
| 4 | MAJOR | accepted | `harness/cells.py`: `build()` refuses a holdout id without a `RegisteredContext`, which is constructed only from a `REGISTERED` marker at the literal primary root; the command-line route refuses holdout ids; the runner builds a holdout cell after writing its marker, the scorer rebuilds one after validating that marker. PREREGISTRATION §1a now states that `h01`, `h02` and `h06` are pretested reviewer challenge cells at the adapter-layer level (the round-1 fix tests perform their edits on a copy of the baseline and assert the adapter layers' outcomes; gateway outcomes and the three-layer observation were not exercised) and that `h03`, `h04` and `h05` are prospective. The tests' docstrings say the same. | N4a, N4c (N4b equivalent: the `build()` guard already refuses the CLI route) |
| 5 | MAJOR | accepted | `harness/score.py` `main()` refuses to score a registered attempt at any root but the literal one; `marker_problems()` takes the actual root and refuses a marker whose `attemptRoot` is not it (and, for `REGISTERED`, not the literal root). PREREGISTRATION freeze block says so. | N5, N6 |
| 6 | MAJOR | accepted | `adapter/verify_binding.py` checks the nested action members (`action` object, `decision` object, `cites` list of objects with string `sessionId` and integer `callIndex`) before access → `fail:unreadable` (SPEC §3a item 2); both layers use `adapter/storewalk.py`: presence by `lstat` (absent = no entry; a present non-file raises, the validity channel) and the gateway's enumeration (per session directory, every non-directory `.json` entry by name); a subject digest must be 64 lowercase hex before a path is formed (`unknown-subject` in the ceremony, `fail:unreadable` in the binding). SPEC §3a and §5 state each. | N8, N11, N12, N19 |
| 7 | MAJOR | accepted | Rule 4 is a check of names only (`any(n not in allowed)`); a predicate citing the same receipt twice with two matching subjects passes, and a missing one is still `fail:cites-subject-set`. SPEC §3a item 7. | N7' |
| 8 | MAJOR | accepted | `validate_statement()` converts the Statement as supplied with `google.protobuf.json_format.ParseDict` into the bindings' message (unknown or mistyped members refused by the mapping; `content` as base64 text accepted) and runs the bindings' `validate()`; `descriptor()` is gone. SPEC §5 step 4. Test cases: a `content` member accepted, an unknown member alone refused with a complete predicate. | N9 |
| 9 | MAJOR | accepted | `harness/trees.py` is the one typed representation for reconstruction comparison and observation digests: directories and plain files by relative path (files by SHA-256), the root and every entry `lstat`-ed, a symbolic link (root included), device or pipe refused before any byte is read; `same_tree`, `tree_digest` and the scorer's `rebuild_cells` use it. PREREGISTRATION §2. | N10a, N10b, N10c |
| 10 | MINOR | accepted | Targeted tests added: key material versus key id (`trusted_pubkey_problems(pins, path)`), an unknown descriptor member with a complete predicate, exact binding codes per malformed case, an extra and an out-of-vocabulary receipt finding as consistent lies, the locked-only decision and separate holdout report on synthetic rows (`assemble`/`decide`), the terminal handler in-process (a construction that raises after the marker) and once-only writing, and the end-to-end tampered-observation run. | the table below |
| 11 | MINOR | accepted | PREREGISTRATION §4 attributes b02 to the ceremony's key-selection rule (consumer, before upstream verification) and says a05's predicate carries `sessionId` uninterpreted; `harness/MATRIX.json` a05 reason and b02 ownership/reason rewritten accordingly; the scorer's docstring is locked-only with the holdout apart; README describes the consumer ceremony. | — (wording) |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` is untouched (SHA-256 `10f87d02…`, as the reviewer measured); the six constructions are unchanged; the provenance disclosure is in §1a as finding 4 asked. | — |

### Mutation table (round 2; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| N1 the scorer's recomputation removed | FAILED (1) — the end-to-end test |
| N2 a record finding required to carry a session id | FAILED (1) |
| N3a loader kind unchecked | FAILED (1) |
| N3b cache-prefix emptiness unchecked | FAILED (1) |
| N3c only package roots checked, not submodules | FAILED (1) |
| N3d interpreter implementation unchecked | FAILED (1) |
| N4a `build()` holdout guard removed | FAILED (1) |
| N4b CLI refusal of holdout ids removed | OK — **equivalent**: `build()` refuses the same call with the same words; the CLI check is a courtesy message, not the safeguard |
| N4c `RegisteredContext` accepts any root | FAILED (1 error) |
| N5 the scorer scores a registered attempt at any root | FAILED (1) |
| N6 marker root not compared with the scored root | FAILED (1) |
| N7 rule 4 as set equality | OK — **equivalent**: at rule 4 every allowed name is already present (rules 2–3), so set equality and the name check coincide |
| N7' rule 4 as the round-1 list-versus-set comparison (the reported defect) | FAILED (1) |
| N8 nested action shapes unchecked | FAILED (1 error) |
| N9 unknown descriptor members ignored by the mapping | FAILED (1) |
| N10a typed tree omits directories | FAILED (1) |
| N10b root symbolic link followed | FAILED (1) |
| N10c non-regular entries read as files | FAILED (1) |
| N11 presence by `is_file()` | FAILED (1) |
| N12 digest syntax unchecked | FAILED (1) |
| N13 holdout divergences included in the R1 decision | FAILED (1) |
| N14 terminal handler removed | FAILED (1 error) |
| N15 key material unchecked | FAILED (1) |
| N16 gateway `ok` accepted as an integer at the type check | OK alone — the combined-verdict identity check still refuses; N16b the combined check by truthiness — OK alone, the type check refuses; **N16 and N16b together: FAILED (1)**. Each is a redundant defence of the other; neither is the sole safeguard |
| N17 receipt-level finding count as a lower bound | FAILED (1) — after the extra-finding case was added |
| N18 status vocabulary unchecked | FAILED (1) — after the out-of-vocabulary case was made a consistent lie |
| N19 receipts enumerated by integer stem instead of the gateway's rule | FAILED (1) |

Two mutations are labeled equivalent, with the reason each time. Suite: 42 tests, all passing,
under the virtual environment with `GATEWAY_BIN` set to the pinned binary and the bytecode
policy in force (the test module sets it before importing the study).

### Pilot after the round

`pilots/r3` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures, with the scorer's
recomputation of every cell in force — the same reduced tuples as before the round for every
cell.

## Round 3 — reviewed `8cb96e1a` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `8cb96e1a42aef1834947c28e7bce440d76fdf0c2`. The read-only sandbox could not
create the bytecode-cache directory the test module makes, so no test body ran for the
reviewer; its probes ran in memory over retained files, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 3. Round 1 (60d6409f) and round 2 (c58fad05) were your own reviews; both returned `not freezable as written`; the maintainer accepted every finding of both. The record of both rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit 8cb96e1a42aef1834947c28e7bce440d76fdf0c2 of the study branch (the worktree you are in).

What changed in the round-2 application, in brief (verify each against the code, not this summary):
- Finding 1 (observations): harness/score.py validates every gateway finding by category against the shapes verify.go emits (receipt by call index or by file, chain with a null index, session findings counted for the two seal-count statuses, record findings by record digest), requires exactly one receipt-level finding per stored receipt file in stored sessions, Boolean summaries by type, and — beyond the record's own coherence — re-runs the three layers over the rebuilt cell and refuses any observation that is not equal to what the pinned apparatus produces.
- Finding 2 (record findings): the record-finding shape `{recordDigest, status}` is accepted without a session id; h03's expected finding is well-formed to the scorer.
- Finding 3 (execution identity): every harness process sets an empty `sys.pycache_prefix` and `sys.dont_write_bytecode` before any study or package import (the runner passes both to its children); harness/pins.py `execution_problems()` checks every loaded module of the four distributions (not only the roots) to be a distribution file under a source or extension loader with its cache path under the empty prefix, every study module to be from the study tree, the prefix empty, and the interpreter the pinned implementation and version.
- Finding 4 (holdout): harness/cells.py builds a holdout cell only under a `RegisteredContext` (the marker of a REGISTERED attempt at the literal primary root); the CLI refuses holdout ids; PREREGISTRATION §1a now states that h01, h02 and h06 are pretested at the adapter-layer level by the round-1 fix tests and that h03, h04 and h05 are prospective.
- Finding 5 (root): the scorer refuses to score a registered attempt at any root but the literal one and refuses a marker whose recorded root is not the directory being scored.
- Finding 6 (shapes, presence, digest syntax): nested action members are shape-checked in the binding layer (`fail:unreadable`, SPEC §3a); both layers use one presence rule (absent = no directory entry; a present non-file is an I/O failure) and the gateway's enumeration rule (adapter/storewalk.py); a subject digest must be 64 lowercase hex before any path is formed.
- Finding 7 (rule 4): the foreign-subject check is a check of names only; a repeated citation with two matching subjects passes.
- Finding 8 (descriptor conversion): the Statement as supplied is converted by `google.protobuf.json_format.ParseDict` into the bindings' message and validated by the bindings' `validate()`; base64 `content` is accepted; unknown or mistyped members are refused.
- Finding 9 (trees): harness/trees.py is one typed representation (directories and plain files; symbolic links including the root, devices and pipes refused before reading) for reconstruction comparison and observation digests alike.
- Findings 10–11: targeted tests (key material, unknown member with a complete predicate, exact binding codes, extra and out-of-vocabulary findings, the locked-only decision on synthetic rows, the terminal handler in-process, an end-to-end tampered-observation run through the real pipeline); b02 attributed to consumer key selection, a05's reason names the carried sessionId, the scorer docstring and README aligned.

Your job this round:
1. Verify every round-2 disposition against the code; for each of findings 1–11 say closed or residue (with lines).
2. Attack the recomputation rule: is there any observation the scorer accepts that the pinned apparatus would not produce over the registered construction? Is the recomputation itself bound to the same binary, key and interpreter as the record? Is there any way the rebuilt cell differs from the retained cell while `same_tree` passes?
3. Attack execution identity again: with the empty cache prefix and the per-module checks, what code could still run that is not the pinned code? Judge whether the residual (the interpreter itself, its standard library, the operating system) is stated honestly as a limit.
4. Re-audit the locked matrix where the round changed anything (a05 and b02 texts; the binding layer's rule 4 and nested-shape codes; the Statement conversion) and say whether every expectation still follows.
5. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…); confirm the six constructions still implement your strings; judge whether the §1a provenance disclosure is now accurate and sufficient. Do not build a holdout cell.
6. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory:
    GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes; if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-2 dispositions (closed / residue), then an audit line per changed locked cell, then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed commit `8cb96e1a42aef1834947c28e7bce440d76fdf0c2`. **Verdict: `not freezable as written`.** The locked expectations remain sound, but recomputation and execution identity still have bypasses.

The authorized unittest command failed during module import at `harness/tests/test_study.py:12`: the sandbox could not create the cache directory. **No test bodies ran.** Subsequent checks used existing files and isolated, in-memory probes. No primary attempt, pilot, or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — recomputation can execute a different gateway from the one whose digest is recorded.**

   **Locations:** [harness/run_layers.py:40](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/run_layers.py:40), `harness/pins.py:165–170`, `harness/run_attempt.py:89–96`, `harness/score.py:376`.

   Pinning hashes `Path(binary)`, whereas `subprocess.run([binary, ...])` searches `PATH` when `binary` is a bare filename. A genuine `./gateway` can therefore supply every recorded digest while another `gateway` on `PATH` supplies both the original observations and their recomputation.

   **Probe:** from the directory containing the supplied binary, `pins.problems(..., "gateway-03582d9")` returned `[]`; with `PATH=/usr/bin:/bin`, launching that same argument raised `FileNotFoundError`. The checked file existed, but execution did not select it.

   This defeats the new evidence safeguard concretely. Duplicating a03’s `citation-unresolved` finding produces a record accepted by `observation_problems()` whose reduced result still equals a03’s expectation. Gateway `verify.go@03582d9:498–505` emits that finding only once per action. A substituted gateway emitting the duplicate consistently would satisfy recomputation and preserve `R1 holds`. I verified the shape acceptance and unchanged reduction in memory; I did not install or run a substituted gateway.

   **Smallest sufficient edit:** resolve the gateway argument to one absolute path before hashing or launching it, and pass that same resolved path through both child processes and recomputation. Add a test with different same-named executables in the working directory and `PATH`.

2. **BLOCKER — the execution checker still admits unpinned implementation code.**

   **Locations:** [harness/pins.py:92](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:92), particularly `99–101` and `145–159`; `harness/make_manifest.py:29–30`; `PREREGISTRATION.md:39–48`.

   Three concrete gaps remain:

   - **The active protobuf backend is omitted.** This environment uses `google._upb._message`, which belongs to the pinned protobuf distribution but falls outside the checked `google.protobuf` prefix. An in-memory proxy at an outside origin was used during protobuf initialization; all non-freeze pin checks and subsequent execution checks returned `[]`.
   - **The cryptography proxy exception applies to arbitrary modules.** Any module can expose `_module` pointing to a genuine module, causing the checker to inspect that inner module and disregard the outer implementation. I supplied an in-memory `in_toto_attestation.v1.statement` proxy before importing the consumer. Its replacement validator accepted an empty predicate; the genuine validator rejected it with `Predicate object required`. All non-freeze pin checks returned `[]`.
   - **Sourceless standard-library shadows remain unchecked.** The manifest excludes every `.pyc`, and the execution checker examines only its named package prefixes and study modules. A memory-backed sourceless loader executed replacement code under `harness/json.pyc`; `execution_problems()` returned `[]`. An ordinary script-directory shadow would be importable independently of `sys.pycache_prefix`.

   **Smallest sufficient edit:** cover every protobuf import namespace, including `google._upb`; restrict proxy unwrapping to the actual pinned cryptography proxy implementation; reject importable sourceless files in study import roots; and establish trusted import resolution before executing those imports. Loader checks should inspect actual loader classes, not merely their class-name strings.

   **Residual limits are not yet stated honestly.** The interpreter check establishes implementation and version, not executable/build identity. The interpreter binary, genuine standard library, startup/import machinery, native system dependencies, and operating system remain trusted. §§7–8 do not disclose that boundary. State it explicitly, including the assumption that files and execution machinery are not concurrently replaced. Those assumptions must not be used to excuse unchecked replacement modules under study-controlled paths.

3. **MAJOR — the new digest validation accepts a trailing newline and returns incorrect binding outcomes.**

   **Locations:** [adapter/verify_attestation.py:36](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/adapter/verify_attestation.py:36), `71`; `adapter/verify_binding.py:31,43,62`; `harness/score.py:58,157`.

   Python’s `$` anchor also matches immediately before a final newline. Consequently, `^[0-9a-f]{64}$` used with `match()` accepts 64 hexadecimal characters followed by `"\n"`.

   **Probes using signed, memory-backed envelopes:**

   | Alteration | Actual in-toto result | Actual binding result | Required by revised SPEC |
   |---|---|---|---|
   | Append newline to artifact subject digest | `missing` | `fail:artifact-subject-mismatch` | `unknown-subject`; `fail:unreadable` |
   | Append newline to citation subject digest | `mismatch` | **`pass`** | `unknown-subject`; `fail:unreadable` |

   `digest_after_prefix()` also accepts the newline, and `finding_problem()` accepts a similarly malformed `recordDigest`.

   **Smallest sufficient edit:** use `fullmatch()` for all three digest validators, with regression assertions for a trailing LF. Retain the existing expected codes in SPEC §3a and §5.

4. **MAJOR — `RegisteredContext` does not establish a validated registered attempt.**

   **Locations:** [harness/cells.py:27](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/cells.py:27), `312–320`; `PREREGISTRATION.md:116–121`.

   The constructor checks the root and only three marker fields. It does not require complete matching freeze pins or the execution identity and cell set required of a registered marker. `build()` subsequently checks only `isinstance`; it never validates the context’s contents.

   **Probe:** with the marker read supplied in memory, `RegisteredContext` accepted:

   ```json
   {
     "label": "REGISTERED",
     "attemptId": "not-a-real-attempt",
     "attemptRoot": "<literal primary root>"
   }
   ```

   All freeze pins were still null. The scorer rejected the same marker for six missing fields. A fieldless `object.__new__(RegisteredContext)` also satisfies the sole type guard. Neither probe called a holdout constructor.

   The normal runner and scorer perform stronger checks before creating their contexts, but the library entry point still does not enforce the claimed boundary.

   **Smallest sufficient edit:** share complete registered-marker and freeze-pin validation with the construction guard, and validate context contents at `build()` before copying anything. Reject incomplete, forged, or stale contexts. Study 014’s registered context explicitly revalidates its contents rather than relying on its type.

5. **MINOR — two surviving sentences contradict the corrected holdout provenance disclosure.**

   **Locations:** [PREREGISTRATION.md:62](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/PREREGISTRATION.md:62), `harness/cells.py:313`.

   Both still describe the registered attempt as the holdouts’ “first construction anywhere.” That conflicts with §1a’s accurate acknowledgement that h01, h02, and h06’s edits were already constructed and tested at the adapter layer.

   **Smallest edit:** replace that phrase with “first construction through the guarded holdout builder; pretesting is disclosed in §1a.”

The round-2 dispositions resolve as follows:

| Round-2 finding | Verdict | Code-based assessment |
|---|---|---|
| **1 — observations** | **Residue** | `score.py:191–262,350–377` adds the promised shape checks and full recomputation. Invented subjects and duplicated receipts differ from genuine output; integer summaries are rejected. The remaining failure is the “pinned apparatus” premise: findings 1–2 above. |
| **2 — record findings** | **Closed** | `score.py:156–160` accepts `{recordDigest,status}` without `sessionId`; h03’s legitimate finding fits. |
| **3 — execution identity** | **Residue** | Cache setup and broader module checks exist, but omitted namespaces, unrestricted proxy unwrapping, and sourceless shadows remain: finding 2. |
| **4 — holdout** | **Residue** | CLI refusal exists at `cells.py:324–327`; §1a’s named pretesting disclosure is accurate. Context validation and two surviving provenance sentences remain defective: findings 4–5. |
| **5 — scoring root** | **Closed** | `score.py:317–318` checks the actual resolved root; `101–104` connects the marker to it. |
| **6 — shapes, presence, digest syntax** | **Residue** | Nested checks at `verify_binding.py:68–74` and shared `storewalk.presence()` correctly repair the reported cases. Digest syntax has finding 3’s newline gap. |
| **7 — rule 4** | **Closed** | `verify_binding.py:90–98` retains citation multiplicity and checks foreign names only. Memory probes confirmed repeated citations pass and a missing corresponding subject fails. |
| **8 — Statement conversion** | **Closed** | `verify_attestation.py:92–97` uses `ParseDict` and the bindings’ validator. Base64 `content` is accepted; an unknown descriptor member with a complete predicate is refused. |
| **9 — trees** | **Closed** | `trees.py:14–45` shares one representation covering directories, regular files, root type, and descendant types. |
| **10 — targeted tests** | **Closed, by inspection** | Requested isolated assertions are present at `test_study.py:177–189,240–310,365–438,441–453,530–540,575–624`. I could not reproduce the reported suite or mutation-table execution because import failed. |
| **11 — ownership wording** | **Closed** | `MATRIX.json:207,320–322`, `PREREGISTRATION.md:184–206`, `score.py:12–17`, and `README.md:11–24` apply the requested corrections. |

For recomputation specifically, I found **no independent static bypass of the full observation comparison when the executing apparatus is genuine**. The Boolean type checks matter: Python equality alone equates `1` with `true`, but the preceding validator rejects that substitution. The trusted adapter key is consistently supplied from the external fixture and checked by material and digest (`pins.py:77–89`, `run_layers.py:36,56`, `score.py:364`). Exact interpreter-build identity is not established.

For `same_tree`, I found no way for stable trees with different relative paths, directory/file kinds, or file bytes to compare equal without a SHA-256 collision. Permissions, ownership, timestamps, and hard-link topology are outside its stated representation. It is not an atomic snapshot against concurrent filesystem mutation.

The changed locked-cell audit is:

| Changed cell | Gateway | In-toto | Binding | Assessment |
|---|---|---|---|---|
| **a05**, `MATRIX.json:184–207`; `cells.py:106–107` | `ok, unregistered-session`; false | pass | pass | Follows. The predicate carries `sessionId`; neither adapter layer checks registry membership. |
| **b02**, `MATRIX.json:298–322`; `cells.py:140–142` | `ok`; true | `s2/1`: `fail:untrusted-key` | pass | Follows. Consumer key selection rejects before upstream signature verification. |

I also checked the shared changes against all nineteen locked expectations. Every expected tuple is unchanged from round 2 and still follows for its concrete construction:

| Cell | Gateway statuses | In-toto failure | Binding failure |
|---|---|---|---|
| pos | `ok` | — | — |
| neg | `ok` | 1: signature | — |
| a01 | `artifact-mismatch, ok` | 1/artifact: mismatch | — |
| a02 | `ok, sequence-broken, signature-mismatch` | 1/citation: mismatch | 0: predicate differs |
| a03 | `citation-unresolved, ok, sequence-broken, tail-rollback` | 1/citation: missing | — |
| a04 | `decision-record-mismatch, ok` | 1/record: missing | — |
| a05 | `ok, unregistered-session` | — | — |
| a06 | `count-exceeds-seal, misfiled, ok` | 2: missing attestation | 2: missing attestation |
| a07 | `ok, signature-mismatch` | — | 1: predicate differs |
| b01 | `ok` | 1: signature | 1: predicate differs |
| b02 | `ok` | 1: untrusted key | — |
| b03 | `ok` | — | 1: artifact mismatch |
| b04 | `ok` | 1: predicate type | — |
| b05 | `ok` | 1: Statement type | — |
| b06 | `ok` | 1: missing attestation | 1: missing attestation |
| b07 | `ok` | 1: payload type | — |
| b08 | `ok` | — | 1: predicate differs |
| b09 | `ok` | — | 1: citation subject set |
| c01 | `key-mismatch` | — | — |

Here, numbers identify `s2/<number>.dsse.json`; “—” means pass. Gateway `ok` is true exactly where its status set is only `ok`; combined passes only for pos. All existing locked action shapes satisfy the new nested checks, and their descriptors survive the new Statement conversion. Rule 4 preserves the existing outcomes while repairing legitimate repeated citations.

The holdout remains **6,638 bytes**, exactly equal—including whitespace and final newline—to the array extracted from the verbatim round-1 findings:

```text
SHA-256 10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

| Holdout | Construction audit |
|---|---|
| h01 — `cells.py:263–265` | Exact foreign-key rebinding of both envelopes and the adjacent key file. |
| h02 — `268–272` | Exact bad-first citation insertion, original subjects retained, action re-signed. |
| h03 — `275–277` | Exact requested bytes written to the new audit file. |
| h04 — `280–282` | Only action receipt 1 removed. |
| h05 — `285–290` | Exact preconditions and CRLF/empty-line transformation. |
| h06 — `293–297` | Action subject list emptied and re-signed. |

**No amendment to the holdout array.** All six expectations remain correct. §1a’s split between pretested h01/h02/h06 and prospective h03/h04/h05 accurately reflects the recorded tests; findings 4–5 concern enforcement and contradictory wording elsewhere.

The 28-file manifest matches, all non-freeze pins match, all eight baseline gateway inputs match the pinned corpus materialization, and the freeze-set checker reports ten studies checked with zero problems. `results/` is absent. Null freeze hashes remain appropriate draft state and correctly prevent registered execution.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 4's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-3 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/run_layers.py` `resolved_gateway()` resolves the argument to one absolute file (refusing a non-file) and `gateway_layer()` launches only that path; the runner and the scorer resolve the argument once (`gateway = str(Path(args.gateway).resolve())`), hash that path, pass it to every child and use it in the recomputation; `harness/pins.py` hashes the resolved path. Tests: the layer with a same-named executable in the working directory and a decoy on PATH; the end-to-end test scores with a relative argument from a directory holding a copy of the pinned binary beside a decoy on PATH and reaches `R1 holds`. | P1a (P1b, P1c equivalent: every process resolves against the same working directory, so the redundant resolutions cannot be told apart by a test — the launch-site resolution is the safeguard) |
| 2 | BLOCKER | accepted | `harness/guard.py` (os and sys alone) establishes trusted import resolution before any other import in every entry script and in the test module: sys.path holds only the study roots, the interpreter's library and the virtual environment (PYTHONPATH refused); the study roots hold no importable non-`.py` file, no directory an import could resolve to, no symbolic link, no `.py` named like a library or pinned module; the cache prefix is set and empty. `harness/pins.py` `execution_problems()` classifies every module in `sys.modules` by origin — built-in/frozen (loader identity, classes and instances); the interpreter's library (trusted; a pinned name from there refused); a pinned distribution file under `SourceFileLoader`/`ExtensionFileLoader` by class identity with its cache under the empty prefix (namespace packages only inside the environment; only cryptography's own `_ModuleWithDeprecations`, after `cryptography.utils` is verified, is unwrapped); a registered study module from its `.py`; two originless modules cryptography's extension creates, pinned by name in `PINS.json`; a non-module object only when its class comes from the library — and refuses anything else. The environment holds exactly seven pinned distributions (cffi, pycparser, typing_extensions added by version and digest; pip, setuptools and the `.pth` hook removed) and the check refuses an unpinned distribution or a `.pth` file. `make_manifest.py` refuses importable non-`.py` files. PREREGISTRATION §2 states the policy and the environment recipe; §7 states the trusted computing base as a limit; §8 disclaims it. The protobuf backend `google._upb._message` is covered (a test asserts it is loaded and passes). | P4a–P4h, P5a–P5e, P6, P7 |
| 3 | MAJOR | accepted | `fullmatch` in `verify_attestation.check_subject`, `verify_binding` (subject digests and `digest_after_prefix`) and `score.finding_problem`; a test appends LF to the artifact and the citation digest and asserts `unknown-subject` / `fail:unreadable`, and to a record digest. | P2a–P2d |
| 4 | MAJOR | accepted | `RegisteredContext(root, gateway)` runs the complete pin check (`require_all=True`, execution identity included) and the shared marker validation (`harness/marker.py`, the function the scorer uses) and raises on any problem, reporting both; `check()` re-reads the marker before any construction and `build()` calls it, so a forged object without contents is refused before anything is copied. The runner records every holdout cell `unconstructed` if the context cannot be established; the scorer records a validity failure if it cannot re-establish one it needs. Tests: an incomplete marker and null freeze pins refused; the positive path with the pins stood in for; a changed marker refused by `check()`; a forged object refused with nothing copied. | P3a–P3d |
| 5 | MINOR | accepted | Both sentences now read "first construction through the guarded holdout builder — pretesting is disclosed in §1a". | — (wording) |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 3; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| P1a the layer launches the gateway argument unresolved | FAILED (1) |
| P1b the scorer recomputes with the unresolved argument | OK — **equivalent**: the layer resolves at launch and the pin check resolves at hashing, both against the same working directory |
| P1c the runner passes the unresolved argument to its children | OK — **equivalent**: the children resolve against the inherited working directory |
| P2a subject digest by `match` (ceremony) | FAILED (1) |
| P2b subject digest by `match` (binding) | FAILED (1) |
| P2c prefixed digest by `match` | FAILED (1) |
| P2d record digest by `match` | FAILED (1) |
| P3a the context skips the pin check | FAILED (1) |
| P3b the context skips the marker validation | FAILED (1) |
| P3c `build()` skips `check()` | FAILED (1) |
| P3d `check()` trusts the object | FAILED (1) |
| P4a any non-module object allowed | FAILED (1) — after the carrier-object case was added |
| P4b any originless module allowed | FAILED (1) — after the ghost-module case was added |
| P4c an unregistered study-tree module allowed | FAILED (1) |
| P4d an unpinned distribution allowed | FAILED (1) |
| P4e any `_module` carrier unwrapped | FAILED (1) |
| P4f a pinned name from the interpreter's library allowed | FAILED (1) |
| P4g outside origins allowed | FAILED (1) |
| P4h loader judged by class name | FAILED (1) |
| P5a the guard ignores importable non-`.py` files | FAILED (1) |
| P5b the guard ignores library-name shadows | FAILED (1) |
| P5c the guard ignores foreign `sys.path` entries | FAILED (1) |
| P5d the guard ignores PYTHONPATH | FAILED (1) |
| P5e the guard ignores directories and links | FAILED (1) |
| P6 the child environment keeps PYTHONPATH | FAILED (1) |
| P7 the manifest skips importable non-`.py` files | FAILED (1) — after the manifest test was added |

Two mutations are labeled equivalent, with the reason each time. Suite: 47 tests, all passing,
under the documented invocation (the bytecode policy in force from the interpreter's start,
`GATEWAY_BIN` set to the pinned binary).

### Pilot after the round

`pilots/r4` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 4 — reviewed `46dc8ecb` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `46dc8ecbbd9c309e776a6c91896f0bbea30fcd11`. The read-only sandbox blocked
`mktemp` and the test module's cache directory, so no test body ran for the reviewer; its
probes ran in memory over retained files, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 4. Rounds 1–3 (60d6409f, c58fad05, 8cb96e1a) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all three rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit 46dc8ecbbd9c309e776a6c91896f0bbea30fcd11 of the study branch (the worktree you are in).

What changed in the round-3 application, in brief (verify each against the code, not this summary):
- Finding 1 (gateway path): the runner, the layer runner and the scorer resolve the gateway argument to one absolute file before hashing or launching it (`run_layers.resolved_gateway`), pass that path to every child and use it in the recomputation; a test runs the layer with a same-named executable in the working directory and a decoy on PATH, and the end-to-end test scores with a relative argument beside a decoy on PATH.
- Finding 2 (execution identity): `harness/guard.py`, using os and sys alone, establishes trusted import resolution before any other import in every entry script and in the test module (sys.path holds only the study roots, the interpreter's library and the virtual environment; PYTHONPATH refused; the study roots hold no importable non-.py file, no directory an import could resolve to, no symbolic link, no .py named like a library or pinned module; the cache prefix set and empty). `harness/pins.py` `execution_problems()` now classifies EVERY module in sys.modules by the file it was loaded from: built-in/frozen; the interpreter's library (trusted, a stated limit — a pinned name loaded from there is refused); a pinned distribution file under the source or extension loader by class identity with its cache path under the empty prefix (namespace packages only inside the environment; only cryptography's own `_ModuleWithDeprecations` unwrapped, after cryptography.utils itself is verified); a registered study module from its .py; two originless modules cryptography's extension creates (`_openssl`, `_openssl.lib`) pinned by name; anything else refused. The environment now holds exactly seven pinned distributions (cffi, pycparser and typing_extensions added; pip and setuptools and the .pth hook removed) and the check refuses an unpinned distribution or a .pth file. The manifest refuses importable non-.py files. PREREGISTRATION §2 states the policy; §7 states the trusted computing base (interpreter build, standard library, import machinery, native libraries, OS; no atomic snapshot) as a limit and §8 disclaims it.
- Finding 3 (digest syntax): every digest validator uses `fullmatch`; tests cover a trailing LF in the ceremony, the binding and the record-finding schema.
- Finding 4 (RegisteredContext): the constructor takes the root and the gateway, runs the complete pin check (`require_all=True`, execution identity included) and the shared marker validation (`harness/marker.py`, the same function the scorer uses) and raises on any problem; `check()` re-reads the marker before any construction and `build()` calls it; a forged object without contents is refused before anything is copied; the runner records every holdout cell unconstructed if the context cannot be established, and the scorer records a validity failure if it cannot re-establish one it needs.
- Finding 5: the two "first construction anywhere" sentences now read "first construction through the guarded holdout builder; pretesting is disclosed in §1a".

Your job this round:
1. Verify every round-3 disposition against the code; for each of findings 1–5 say closed or residue (with lines).
2. Attack execution identity once more with the classification in place: what code could still run that is not the pinned code, within the trusted computing base §7 now names? Judge whether §7's statement of that base is honest and complete, and whether any refusal the checker should make is missing.
3. Attack the gateway resolution and the recomputation: is there any way the file hashed differs from the file launched, in any process?
4. Attack the registered context: can a holdout cell be built through `harness/cells.py` outside a registered attempt at the literal root with all pins non-null and matching?
5. Re-audit the locked matrix where the round changed anything (digest syntax; enumeration and presence are unchanged) and say whether every expectation still follows.
6. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
7. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-3 dispositions (closed / residue), then an audit line per changed locked cell, then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed commit `46dc8ecbbd9c309e776a6c91896f0bbea30fcd11`. **Two BLOCKERs and one MAJOR remain.** The locked expectations and holdout constructions remain sound.

The documented unittest command failed at `mktemp`, then at `test_study.py:16` during import because the filesystem is read-only. **No test bodies ran.** Subsequent verification used source inspection and isolated read-only probes. No primary attempt, pilot, or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — the standard-library-object exception admits a replacement Statement validator.**

   **Locations:** [harness/pins.py:147](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:147), particularly lines 150–154; `adapter/verify_attestation.py:28,92–97`; `PREREGISTRATION.md:53–56,269–278`.

   The checker accepts any non-module object whose `__module__` names a library module. It does not restrict this exception to the two `typing` objects the comment identifies, or prevent such an object from replacing a pinned implementation module.

   **Reproduced:** before importing the consumer, I installed this stand-in:

   ```python
   proxy = Mock(wraps=genuine_statement_module)
   proxy.Statement.copy_from_pb.return_value.validate.return_value = None
   sys.modules["in_toto_attestation.v1.statement"] = proxy
   ```

   Its class is the genuine `unittest.mock.Mock`, with owner `unittest.mock`. The complete **non-freeze** pin check returned `[]`, as did the subsequent execution check. The consumer’s replacement validation accepted a baseline Statement with `predicate = {}`; the genuine validator rejected it with `Predicate object required`.

   This preserves the original wrong-reason risk: none of the nineteen locked expectations requires `invalid:bindings`, so disabling upstream Statement validation need not disturb their concordance. Trusting the standard library does not establish that a configured mock is the pinned Statement implementation.

   **Smallest sufficient edit:** restrict the non-module exception to the exact legitimate `typing.io` and `typing.re` objects under those names, after validating their owner. Refuse other stand-ins, including under pinned names. Add this Mock-based regression.

2. **BLOCKER — unrecorded package code can be imported after the last execution check.**

   **Locations:** [harness/pins.py:40](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:40), lines 45–48, 103–127; `harness/guard.py:48–73`; `harness/score.py:304,336,363–374`; `harness/run_layers.py:83–95`.

   Distribution hashing reads only files listed by distribution metadata. The environment check rejects extra *distributions* and `.pth` files, but does not reject unrecorded importable files inside existing package directories. Classification examines only modules already loaded.

   **Observed timing:** after importing the scoring apparatus and obtaining `pins.problems(...) == []`, verification of the existing baseline newly imported:

   ```text
   google.protobuf.descriptor_pb2
   ```

   The scorer performs no subsequent execution check before adjudication.

   **Concrete static route:** a pre-existing, unrecorded file at:

   ```text
   <venv>/lib/python3.8/site-packages/google/protobuf/descriptor_pb2/__init__.py
   ```

   leaves all distribution digests and the seven-distribution count unchanged. CPython’s ordinary `FileFinder` checks a package directory before the same-named module file (`_bootstrap_external.py:1519–1540`), so this package wins over the pinned `descriptor_pb2.py` when verification triggers the import. Its initializer can execute additional code while supplying the genuine descriptor definitions. No concurrent file replacement or altered interpreter machinery is necessary.

   I established the import timing and resolution rule; I did **not** create or execute that filesystem package.

   **Smallest sufficient edit:** before verifier imports, reject unowned importable files and packages throughout the environment’s import roots, including nested package directories; apply that check to each process. Also check execution identity after verification so classification includes late imports. Add a regression requiring refusal of an extra `descriptor_pb2` package before its initializer executes.

   **§7 assessment:** the environmental trust list now adequately names the interpreter build, standard library, import machinery, native dependencies, gateway dependencies, OS/filesystem, and absence of atomic snapshots. However, its assertion that the checks hold executing study/package code to pinned files remains false because of findings 1–2. These routes operate using the stated trusted machinery; they are missing enforcement, not undisclosed failures of that machinery.

3. **MAJOR — a populated forged context still bypasses registration validation.**

   **Locations:** [harness/cells.py:47](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/cells.py:47), lines 50–54 and 335–343; `harness/tests/test_study.py:119–122,144–182`.

   The constructor now validates fully. `check()`, however, only requires `root` and `marker`, then compares the latter with disk. It does not establish that the constructor ran, validate the marker’s contents, or check any pins.

   **Reproduced without construction:**

   ```python
   forged = object.__new__(RegisteredContext)
   forged.root = PRIMARY_ROOT.resolve()
   forged.marker = {}
   ```

   With only the marker read stood in for as `"{}"`, `forged.check()` returned `None`. Shared marker validation rejected that document for nine missing fields; all five freeze pins remained null. Neither `build()` nor a holdout function was called.

   By inspection, `build()` would proceed from that successful check to copying the baseline and dispatching the holdout construction. A subclass can also override the dynamically invoked `check()`.

   **Smallest sufficient edit:** have construction re-run the complete shared pin and marker validation using the context’s required contents, rather than trusting stored equality. Invoke that validation directly from the builder and reject overriding stand-ins. Test populated forged contexts as well as fieldless ones.

The round-3 dispositions resolve as follows:

| Round-3 finding | Verdict | Code-based assessment |
|---|---|---|
| **1 — gateway path** | **Closed** | `run_attempt.py:71,112–119`, `run_layers.py:49–60,90–95`, `score.py:302–305,363`, and `pins.py:188–191` consistently resolve, hash and launch the absolute file. Both requested decoy tests exist at `test_study.py:705–726,780–794`; execution was blocked. |
| **2 — execution identity** | **Residue** | The guard, complete module enumeration, `_upb` coverage, loader-class checks, restricted cryptography unwrapping, seven package pins and `.pth` refusal are present (`guard.py:34–97`; `pins.py:84–183`). Findings 1–2 above remain. |
| **3 — digest syntax** | **Closed** | `verify_attestation.py:71`, `verify_binding.py:43,62`, and `score.py:138` use `fullmatch`. Memory-backed signed-envelope probes returned `unknown-subject` and `fail:unreadable` for trailing-LF artifact/citation digests; prefixed and record digests were also refused. Tests cover these at `test_study.py:329–346`. |
| **4 — RegisteredContext** | **Residue** | Complete constructor validation and shared marker validation exist (`cells.py:29–45`; `marker.py:12–44`). Runner containment and scorer validity handling exist (`run_attempt.py:91–107`; `score.py:334–338`). Finding 3 above defeats the builder’s remaining guard. |
| **5 — provenance wording** | **Closed** | Both sentences now scope the claim to the guarded builder and disclose pretesting (`PREREGISTRATION.md:79–80`; `cells.py:333–334`). |

For gateway resolution specifically, I found **no remaining static path-selection mismatch under §7’s stable-filesystem assumption**. Absolute launch arguments prevent `PATH` substitution in every process. Repeated path reads are not an atomic executable snapshot, which §7 now explicitly acknowledges. Full observation recomputation remains intact; its unresolved weakness is execution identity, not gateway argument resolution.

Neither matrix nor the adapter SPEC changed this round. I nevertheless rechecked all nineteen locked expectations against the shared digest changes. All supplied digests remain valid lowercase hexadecimal strings; enumeration and presence behavior are unchanged. Every expected tuple still follows:

| Cell (`MATRIX.json` line) | Gateway statuses | In-toto failure | Binding failure |
|---|---|---|---|
| pos (`7`) | `ok` | — | — |
| neg (`32`) | `ok` | 1: `fail:signature` | — |
| a01 (`59`) | `artifact-mismatch, ok` | 1/artifact: `mismatch` | — |
| a02 (`89`) | `ok, sequence-broken, signature-mismatch` | 1/citation: `mismatch` | 0: `fail:predicate-differs-from-store` |
| a03 (`122`) | `citation-unresolved, ok, sequence-broken, tail-rollback` | 1/citation: `missing` | — |
| a04 (`154`) | `decision-record-mismatch, ok` | 1/record: `missing` | — |
| a05 (`184`) | `ok, unregistered-session` | — | — |
| a06 (`210`) | `count-exceeds-seal, misfiled, ok` | 2: `fail:missing-attestation` | 2: `fail:missing-attestation` |
| a07 (`242`) | `ok, signature-mismatch` | — | 1: `fail:predicate-differs-from-store` |
| b01 (`269`) | `ok` | 1: `fail:signature` | 1: `fail:predicate-differs-from-store` |
| b02 (`298`) | `ok` | 1: `fail:untrusted-key` | — |
| b03 (`325`) | `ok` | — | 1: `fail:artifact-subject-mismatch` |
| b04 (`352`) | `ok` | 1: `invalid:predicate-type` | — |
| b05 (`379`) | `ok` | 1: `invalid:statement-type` | — |
| b06 (`406`) | `ok` | 1: `fail:missing-attestation` | 1: `fail:missing-attestation` |
| b07 (`435`) | `ok` | 1: `fail:payload-type` | — |
| b08 (`462`) | `ok` | — | 1: `fail:predicate-differs-from-store` |
| b09 (`489`) | `ok` | — | 1: `fail:cites-subject-set` |
| c01 (`516`) | `key-mismatch` | — | — |

Numbers identify `s2/<number>.dsse.json`; “—” means that layer passes. Gateway `ok` is true exactly where its status set is only `ok`; combined passes only for pos. No locked cell emits a record-scoped finding, so the stricter record-digest validator changes none of these expectations.

**No amendment to the holdout array: kept byte for byte.** It remains 6,638 bytes, exactly equal—including whitespace and final newline—to the array extracted from the verbatim round-1 findings:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six construction functions are source-identical to round 3 and still implement the construction strings: h01 foreign rebinding (`cells.py:283`); h02 bad-first citation insertion (`288`); h03 exact malformed-record bytes (`295`); h04 action receipt deletion (`300`); h05 CRLF/empty-line transformation (`305`); h06 emptied subjects and re-signing (`313`). Their expectations remain justified. None was constructed.

The 30-file manifest matches, all seven installed-package pins match, the gateway digest matches `aaa16fec…`, all eight baseline gateway inputs match the pinned corpus materialization, and the freeze-set checker reports ten studies with zero problems. `results/` remains absent. Null freeze pins correctly prevent ordinary registered execution.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 5's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-4 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/pins.py` `execution_problems()`: the non-module exception is exactly the two objects the library's `typing` registers under `typing.io` and `typing.re`, by identity (`mod is typing.io`), after `typing` itself is verified as a library file; every other non-module object in `sys.modules` is refused whatever its class or name. The reviewer's `Mock(wraps=…)` stand-in under a pinned name is a regression test, and so is a `Mock` under the name `typing.io`. | Q1a, Q1b |
| 2 | BLOCKER | accepted | `harness/guard.py` `environment_problems()` (os alone, before any other import) walks every import root of the virtual environment and refuses any entry an installed distribution's `RECORD` does not list — an unrecorded file, an unrecorded package directory (which the import system prefers to a same-named module), a path hook, a symbolic link (a recorded path that has become a link included) — skipping `__pycache__` directories, unreachable under the empty prefix; `site_problems()` refuses a run in which `sitecustomize`/`usercustomize` was imported. `pins.execution_problems()` repeats the whole guard at check time, and the check runs again after the layers have run: in the layer runner before observations are written (a failure raises; no observations exist), in the scorer after the recomputation (a validity failure before adjudication), in the runner after the cells are built. Tests: a temporary site tree with a `descriptor_pb2`-style package directory shadowing a recorded module, an unrecorded module, a path hook, a loose `.pyc`, a directory link and a recorded path turned into a link, each refused by the guard and (the package-directory case) at check time through the pins; the layer runner refusing to write observations when the late check fails; the real environment passing. PREREGISTRATION §2 states all of it; §7 adds site initialization to the stated base and qualifies the claim as holding within that base. | Q2a–Q2g |
| 3 | MAJOR | accepted | `harness/cells.py` `validate_registered_attempt(root, gateway)` is a module-level function (the complete pin check with `require_all=True` and the shared marker validation, from disk); `RegisteredContext.__init__` calls it; `build()` requires the exact type (no subclass), reads `root` and `gateway` from the object and calls `validate_registered_attempt` directly — never a method of the object — before copying anything. Tests: a fieldless forged object, a populated forged object (root = the literal root, marker = `{}`), the same object carrying an instance-level `check` stand-in, and a subclass overriding `check()`, each refused with nothing copied. | Q3a–Q3d |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 4; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| Q1a any non-module object of a library class allowed | FAILED (1) |
| Q1b typing's objects admitted by name, not identity | FAILED (1) — after the `Mock` under `typing.io` case was added |
| Q2a the environment scan removed from the guard | FAILED (1) — after the refusal message was asserted |
| Q2b unrecorded package directories allowed | FAILED (1) |
| Q2c unrecorded files allowed | FAILED (1) |
| Q2d a recorded path that is a symbolic link allowed | FAILED (1) — after the linked-recorded-path case was added |
| Q2e site customization unchecked | FAILED (1) |
| Q2f the late check dropped in the layer runner | FAILED (1) |
| Q2g the environment scan dropped at check time | FAILED (1) — after the pins-level assertion was added |
| Q3a the builder calls the object's `check()` instead of the module function | FAILED (1) — after the instance-level stand-in case was added |
| Q3b the builder accepts subclasses | FAILED (1) |
| Q3c the builder skips the validation | FAILED (1) |
| Q3d the validation skips the marker | FAILED (1) |

No mutation is labeled equivalent. Suite: 49 tests, all passing, under the documented
invocation.

### Pilot after the round

`pilots/r5` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 5 — reviewed `e1099309` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `e10993094db269c88db60350fed8a214dc67fcc7`. The read-only sandbox blocked
`mktemp` and the test module's cache directory, so no test body ran for the reviewer; its
probes ran in memory and over an in-memory file-system view, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 5. Rounds 1–4 (60d6409f, c58fad05, 8cb96e1a, 46dc8ecb) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all four rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit e10993094db269c88db60350fed8a214dc67fcc7 of the study branch (the worktree you are in).

What changed in the round-4 application, in brief (verify each against the code, not this summary):
- Finding 1 (non-module objects): the exception in `harness/pins.py` `execution_problems()` is exactly the two objects the library's `typing` module registers under `typing.io` and `typing.re`, by identity, after `typing` itself is verified as a library file; every other non-module object in `sys.modules` is refused, whatever its class or name. Your Mock-based stand-in is a regression test.
- Finding 2 (unrecorded package code, late imports): `harness/guard.py` `environment_problems()` (os alone, before any other import) walks every import root of the virtual environment and refuses any entry an installed distribution's RECORD does not list — an unrecorded file, an unrecorded package directory (which the import system prefers to a same-named module), a path hook, a symbolic link — skipping `__pycache__` directories, which the empty cache prefix makes unreachable; `site_problems()` refuses a run in which `sitecustomize`/`usercustomize` was imported. `pins.execution_problems()` repeats the whole guard at check time, and the check now runs AGAIN after the layers have run: in the layer runner before observations are written (a failure raises, so no observations exist), in the scorer after the recomputation (a validity failure before adjudication), in the runner after the cells are built. A regression test builds a temporary site tree with a `descriptor_pb2`-style package directory shadowing a recorded module and asserts refusal; another asserts the layer runner refuses to write observations when the late check fails. PREREGISTRATION §2 states all of it; §7 adds site initialization to the stated trusted base and qualifies the claim as holding within that base.
- Finding 3 (forged contexts): `harness/cells.py` `validate_registered_attempt(root, gateway)` is a module-level function (the complete pin check with `require_all=True` and the shared marker validation, from disk); `RegisteredContext.__init__` calls it; `build()` requires the exact type (no subclass), reads `root` and `gateway` from the object and calls `validate_registered_attempt` directly — trusting nothing the object holds, and not any method of it — before copying anything. Tests: a fieldless forged object, a populated forged object (root = the literal root, marker = {}), and a subclass overriding `check()` are each refused with nothing copied.

Your job this round:
1. Verify every round-4 disposition against the code; for each of findings 1–3 say closed or residue (with lines).
2. Attack execution identity within the trusted computing base §7 names: with the environment scan (RECORD ownership of every entry under the environment's import roots), the module classification, the late re-check and the site check, what code could still run that is not the pinned code, and is §7 honest about what remains?
3. Attack the holdout builder: can a holdout cell be built through `harness/cells.py` without a registered attempt at the literal root whose pins are all non-null and matching?
4. The locked matrix and the adapter SPEC are unchanged this round; say so if you confirm it, or say what changed.
5. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
6. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-4 dispositions (closed / residue), then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed `e10993094db269c88db60350fed8a214dc67fcc7`. **Two BLOCKERs and one MAJOR remain.**

The documented test command failed at `mktemp`, then at `test_study.py:16` during import because the filesystem is read-only. **No test bodies ran.** Verification below used source inspection and isolated probes without filesystem writes. No primary attempt, pilot, or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — non-module stand-ins still bypass execution classification through two routes.**

   **Locations:** [harness/pins.py:139](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:139), especially lines 139–155; `adapter/verify_attestation.py:28,92–97`; `PREREGISTRATION.md:61–62`.

   The namespace-package and pinned-originless branches return **before** the non-module check. A Mock wrapping the genuine Statement module passes the namespace branch when given:

   ```python
   proxy.__file__ = None
   proxy.__spec__ = ModuleSpec(genuine.__name__, loader=None, is_package=True)
   proxy.__spec__.submodule_search_locations = [str(Path(genuine.__file__).parent)]
   ```

   **Reproduced:** installing that proxy under `in_toto_attestation.v1.statement`, with its validation replaced by a no-op, produced `[]` from both the complete non-freeze pin check and the late execution check. The consumer accepted a Statement with `predicate = {}`; the genuine validator rejected it with `Predicate object required`.

   Independently, `Mock(spec=genuine, wraps=genuine)` satisfies `isinstance(proxy, type(sys))`. Giving it the genuine module’s origin, loader, spec and cache attributes also produced `[]` from both checks. Moving the existing `isinstance` check earlier therefore does not suffice.

   **Smallest sufficient edit:** classify the object’s actual type before any namespace/originless acceptance, using a check that cannot be spoofed through `__class__`. Admit necessary non-module exceptions by verified-owner identity. This includes the genuine `_openssl.lib`: inspection shows it is a `_cffi_backend.Lib`, so the current “only two typing objects” claim is itself inaccurate. Add regressions for both demonstrated Mock routes and arbitrary objects under the originless names.

2. **BLOCKER — duplicate distribution names separate RECORD ownership from the distribution whose bytes are hashed.**

   **Locations:** [harness/guard.py:111](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/guard.py:111), lines 111–136; `harness/pins.py:40–49,104–120`; `PREREGISTRATION.md:38–52,281–295`.

   The guard trusts every discovered `.dist-info/RECORD`. Hashing selects `metadata.distribution(name)`, while execution classification builds a dictionary keyed by metadata `Name`, silently retaining the **last** distribution bearing that name.

   A concrete filesystem arrangement is:

   - Retain the genuine `protobuf-5.29.6.dist-info`.
   - Add `zz_review_overlay-0.dist-info`, whose `METADATA` says `Name: protobuf`.
   - Give its RECORD all genuine protobuf paths, its own metadata files, and `google/protobuf/descriptor_pb2/__init__.py`.
   - Arrange discovery so this duplicate follows the genuine distribution.

   Named lookup still selects the genuine protobuf metadata; unrestricted discovery selects the duplicate for ownership. The seven-name set remains unchanged. The additional package initializer can then take precedence over `descriptor_pb2.py` and run code absent from the checked digest.

   **Reproduced through an in-memory filesystem view:** genuine metadata remained the hashing selection; two protobuf distribution instances were discovered; the environment scan returned `[]`; the protobuf digest remained pinned; and the complete non-freeze check accepted a module attributed to the additional initializer. No directory or initializer was actually created or executed.

   **Smallest sufficient edit:** reject distinct metadata directories claiming the same normalized distribution name, and derive hashing and ownership from the same verified distribution inventory. Authenticate that inventory before verifier imports; a self-declared RECORD must not establish ownership by itself. Add the duplicate-distribution regression alongside the unrecorded-package test.

3. **MAJOR — a JSON `null` marker bypasses the builder’s shared validation once pins are valid.**

   **Locations:** [harness/cells.py:35](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/cells.py:35), lines 35–42 and 337–349; `harness/marker.py:16–19`; `PREREGISTRATION.md:142–148`.

   Reading a file containing `null` succeeds and produces `None`. The `if marker is not None` condition then skips shared marker validation without adding a problem.

   **Reproduced without construction:** with passing pins simulated and only the marker read supplied as `"null"`, `validate_registered_attempt()` returned `None`. The actual shared marker validator returned `["no attempt marker"]` for that same value. The pin-check invocation retained `require_all=True`.

   Consequently, after freeze with matching pins, an exact-type object created through `object.__new__(RegisteredContext)` and populated with the literal root and gateway reaches the builder’s copy and dispatch despite having no valid registered marker. The constructor’s later indexing of `marker["attemptId"]` does not protect this route: `build()` ignores the validator’s return value.

   **Smallest sufficient edit:** invoke `marker_problems()` unconditionally after the read handling; it already rejects `None`. Add a `null` regression with otherwise passing pins and assert refusal before copying. The currently null freeze pins still prevent construction in this checkout.

The round-4 dispositions resolve as follows:

| Round-4 finding | Verdict | Code-based assessment |
|---|---|---|
| **1 — non-module objects** | **Residue** | The exact typing-identity condition and original Mock regressions are present (`pins.py:147–155`; tests:599–615). Earlier acceptance branches and spoofable `isinstance` leave finding 1 above. |
| **2 — unrecorded code and late imports** | **Residue** | Recursive RECORD ownership checks, symlink refusals, cache skipping and site checks are implemented (`guard.py:99–164`). The full guard repeats at `pins.py:98`. Late checks occur before observation writing (`run_layers.py:93–99`), before adjudication (`score.py:366–377`), and after construction (`run_attempt.py:112–114`). The original unrecorded-package route is closed with genuine metadata; finding 2 defeats the ownership premise. |
| **3 — forged contexts** | **Residue** | Module-level validation, `require_all=True`, exact context type and direct builder invocation are present (`cells.py:23–56,337–344`). Fieldless, populated and overriding stand-ins are covered by tests:109–137. The extracted validator’s `null` path leaves finding 3. |

**§7 assessment:** the named environmental limits accurately identify the interpreter build, standard library/import machinery, native dependencies, OS/filesystem, startup initialization and non-atomic checks. They do not excuse the demonstrated acceptance paths. In particular, the duplicate-metadata arrangement uses ordinary trusted import machinery and requires no concurrent replacement. The claim that executing study/package code is held to pinned files remains false. Moreover, mutable module-origin attributes should not be described as authentication against arbitrary in-process replacement.

The locked matrix and adapter SPEC are **byte-identical to round 4**. All nineteen locked construction functions are unchanged, and their expected tuples still follow. The baseline’s store files, decision book, registry and authority match the pinned corpus vector; the ordinary non-freeze pin check also confirms the package digests and current study manifest.

**No amendment to the holdout array: kept byte for byte.** It is exactly equal, including whitespace and final newline, to the array extracted from the verbatim round-1 findings: **6,638 bytes**, SHA-256:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six holdout functions are source-identical to round 4 and faithfully implement their construction strings (`cells.py:285,290,297,302,307,315`). None was constructed.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 6's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-5 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/pins.py` `execution_problems()` reads every object's real type with `type()` — never `isinstance()`, which a spoofed `__class__` satisfies — before any acceptance by namespace, origin or name; an object that is not exactly a module is refused unless it is one of the two objects the library's `typing` registers or the OpenSSL binding table, each admitted by identity to what a verified owner holds: `typing.io`/`typing.re` to the attributes of the verified library `typing`; `_openssl.lib` to the `lib` attribute of the `_openssl` module that the verified pinned extension `cryptography.hazmat.bindings._rust` holds as `_openssl`, and by exact type to the `Lib` type the verified pinned extension `_cffi_backend` exports (the reviewer is right that `_openssl.lib` is a `_cffi_backend.Lib`, and the earlier "two typing objects" statement was inaccurate: it is corrected in PREREGISTRATION §2 and `PINS.json`); the originless `_openssl` module is admitted only by identity to that extension's attribute. Both demonstrated Mock routes (a namespace-package pose; `Mock(spec=…)` with the genuine origin, loader, spec and cache) and arbitrary objects under the two originless names are regression tests. PREREGISTRATION §7 now states the exact scope of the execution checks: what code runs in a process the harness starts; not authentication against code already running in the process before the harness begins, which is inside the stated base — the regressions exercise the refusals of demonstrated routes and are not claimed to be more. | R1a–R1d |
| 2 | BLOCKER | accepted | `harness/guard.py` reads each metadata directory's declared name (PEP 503-normalized) and refuses a second directory claiming a name already claimed, or one declaring none; such a directory's record grants nothing. `harness/pins.py` `inventory()` takes one inventory of the environment — one distribution per normalized name, a duplicated name refused and used for nothing — from which `package_digest()` (the hashed bytes) and the ownership of files both derive; `metadata.distribution(name)` is no longer used anywhere. The duplicate-metadata arrangement (an overlay directory declaring `Name: Pkg` with a record listing the genuine files plus a shadowing package) is a regression test at the guard and at check time. PREREGISTRATION §2 states the one-inventory rule. | R2a–R2c |
| 3 | MAJOR | accepted | `validate_registered_attempt()` runs the shared marker validation unconditionally (it refuses `None`) and refuses a marker that is not an object; a marker file holding `null`, and a populated exact-type forged object over it, are regression tests with nothing copied. | R3 |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 5; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| R1a the real type read after the namespace branch | FAILED (1) |
| R1b `isinstance` instead of the real type | FAILED (1 + 2 errors) |
| R1c `_openssl.lib` admitted by name | FAILED (1) |
| R1d `_openssl` admitted by name | FAILED (1) |
| R2a duplicate names allowed by the guard | FAILED (1) |
| R2b duplicate names allowed at check time | FAILED (1) |
| R2c a duplicated name still supplies a distribution | FAILED (1) |
| R3 marker validation conditional on not-`None` | FAILED (1) |

No mutation is labeled equivalent. Suite: 49 tests, all passing, under the documented
invocation.

### Pilot after the round

`pilots/r6` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 6 — reviewed `a2786b18` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `a2786b18975ef7a785e9f88a7c20356b8a9a906a`. A first launch of this round,
whose prompt phrased its questions adversarially, was refused by the reviewer vendor's content
filter after reading most of the study and produced no output; the prompt below is the
rephrased one that ran, with the same substance. The read-only sandbox blocked `mktemp` and
the test module's cache directory, so no test body ran for the reviewer; its probes were
read-only import traces and in-memory checks, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 6. Rounds 1–5 (60d6409f, c58fad05, 8cb96e1a, 46dc8ecb, e1099309) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all five rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit a2786b18975ef7a785e9f88a7c20356b8a9a906a of the study branch (the worktree you are in). This is a methodological review of a preregistered software study's harness: the question throughout is whether the harness's validity checks are complete and whether the registration states honestly what they establish.

What changed in the round-5 application, in brief (verify each against the code, not this summary):
- Finding 1 (objects in the module table that are not modules): `harness/pins.py` `execution_problems()` now reads every object's real type with `type()` (never `isinstance()`) BEFORE any acceptance by namespace, origin or name; an object that is not exactly a module is refused unless it is one of the two objects the library's `typing` registers or the OpenSSL binding table (`_openssl.lib`, a `_cffi_backend.Lib`), each admitted by identity to what a verified owner holds (`typing.io`/`typing.re` to the verified library `typing`; `_openssl.lib` to the `lib` attribute of the `_openssl` module that the verified pinned extension `cryptography.hazmat.bindings._rust` holds, and by exact type to the `Lib` type the verified pinned extension `_cffi_backend` exports); the originless `_openssl` module is admitted only by identity to that extension's attribute. Both stand-in constructions you demonstrated, and arbitrary objects under the two originless names, are regression tests. PREREGISTRATION §7 now states the exact scope of the execution checks: they establish what code runs in a process the harness starts (a fresh interpreter over the environment's import roots as they are on disk); they are not, and the registration does not claim them to be, a guarantee about code already running in the process before the harness begins, which is inside the stated trusted base.
- Finding 2 (two metadata directories with one distribution name): `harness/guard.py` reads each metadata directory's declared name (PEP 503-normalized) and refuses a second directory claiming a name already claimed, or one declaring none, and such a directory's record grants no ownership; `harness/pins.py` `inventory()` takes one inventory of the environment (one distribution per normalized name, a duplicated name refused and used for nothing) from which both `package_digest` (the hashed bytes) and the ownership of files derive — `metadata.distribution(name)` is no longer used. The duplicate-metadata arrangement is a regression test at the guard and at check time.
- Finding 3 (a marker file holding `null`): `validate_registered_attempt()` runs the shared marker validation unconditionally (it refuses `None`) and refuses a marker that is not an object; a `null` marker file and a populated forged context over it are regression tests, with nothing copied.

Your job this round:
1. Verify every round-5 disposition against the code; for each of findings 1–3 say closed or residue (with lines).
2. Judge PREREGISTRATION §7's statement of what the execution checks establish (a process the harness starts) and what they do not cover (code already running in the process before the harness begins): is it honest, and is it the right claim for this study to make? If you find a way in which code other than the pinned code could run in a process the harness starts — a fresh interpreter over the environment's import roots as they are on disk — report it as a finding; a way that requires code already running in the process before the harness begins is inside the stated base and is not a finding unless §7 misstates it.
3. Re-examine the inventory rule and the holdout builder's validation for completeness.
4. The locked matrix and the adapter SPEC are unchanged this round; say so if you confirm it.
5. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
6. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-5 dispositions (closed / residue), then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed `a2786b18975ef7a785e9f88a7c20356b8a9a906a`. **One BLOCKER and one MINOR remain.**

The documented test command failed at `mktemp`, then during test-module import because the sandbox is read-only. **No test bodies ran.** Read-only probes confirmed matching package digests, gateway digest and study manifest. No primary attempt, pilot or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — recorded package code executes before its bytes are authenticated, and can disable subsequent validation.**

   **Locations:** [harness/guard.py:119](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/guard.py:119), particularly 134–167; `harness/run_attempt.py:36–37,73`; `harness/cells.py:17`; `adapter/bind.py:23–25`; `harness/pins.py:241–262`; `PREREGISTRATION.md:303–306`.

   The guard establishes membership in self-declared RECORDs without checking recorded files’ bytes. The runner then imports `cells → bind → cryptography` before calling `pins.problems()`.

   **Confirmed by an import-only trace:** `guard.establish` ran, then `cryptography.__init__` executed; neither `pins.problems` nor `package_digest` had run. The governing `main()` was not called.

   A concrete static arrangement is to append this to the existing, recorded `cryptography/__init__.py`, leaving its metadata and RECORD unchanged:

   ```python
   import pins as _study_pins
   _study_pins.problems = lambda *args, **kwargs: []
   _study_pins.execution_problems = lambda *args, **kwargs: []
   ```

   The guard accepts the recorded path. Ordinary source loading executes the addition, which disables both the subsequent full check and the late execution checks. The same installed initializer is available to the child processes.

   This counterexample follows from the import order; **I did not plant or execute that modified file**. Its code first runs through the harness’s imports after the harness begins. It therefore falls within §7’s claimed fresh-process guarantee.

   Round 5 finding 2 explicitly required authenticating the inventory **before verifier imports**. That portion remains unimplemented.

   **Smallest sufficient edit:** introduce a trusted bootstrap that authenticates package bytes and the remaining study modules before importing them. Restrict bootstrap imports to the trusted standard library while checking; derive ownership and hashing from one validated inventory passed onward. Explicitly identify the bootstrap’s trust anchor in §7. Add a fresh-process regression requiring refusal of an altered, already-recorded initializer before its payload executes.

2. **MINOR — the new distribution-name checks do not implement their stated normalization and nameless-directory rules.**

   **Locations:** [harness/pins.py:40](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:40), 48–63; `harness/guard.py:101–116,137–144`; `PREREGISTRATION.md:52–56`.

   PEP 503 requires every consecutive run of `.`, `_` and `-` to collapse to one hyphen. [PEP 503 normalization](https://peps.python.org/pep-0503/#normalized-names)

   Both new loops instead append the original separator when the output already ends in `-`. Read-only probes returned:

   | Input | Actual result | Required result |
   |---|---|---|
   | `Foo.Bar` | `foo-bar` | `foo-bar` |
   | `foo--bar` | `foo--bar` | `foo-bar` |
   | `foo__bar` | `foo-_bar` | `foo-bar` |

   With two supplied metadata objects declaring `Foo.Bar` and `foo--bar`, the actual `inventory()` retained both and returned no problems.

   Additionally, `Name:` with an empty value returns `""`; the guard tests only `declared is None`, so that directory’s RECORD grants ownership. The later extra-distribution check can reject these entries, limiting their independent impact, but the claimed early inventory rule is false.

   **Smallest sufficient edit:** correctly collapse separator runs in both paths, reject absent or empty names before granting ownership, and add equivalent-name and empty-name regressions.

The round-5 dispositions resolve as follows:

| Round-5 finding | Verdict | Code-based assessment |
|---|---|---|
| **1 — non-module stand-ins** | **Closed** | `pins.py:144–184` checks exact real types before namespace/origin acceptance. Verified-owner identity checks cover typing’s objects, `_openssl` and `_openssl.lib` (`146–165,179–191`). Both demonstrated Mock routes were refused in read-only probes. The requested regressions are present at `tests/test_study.py:617–642`. |
| **2 — duplicate distribution metadata** | **Residue** | The original same-name overlay is refused, and duplicated inventory entries are removed (`guard.py:137–144`; `pins.py:54–62`). Findings 1–2 above remain. Also, hashing and ownership call the shared inventory implementation separately (`pins.py:241` and `128`); they do not consume one shared inventory object. Under the stated stable-filesystem assumption, that duplication alone is not a demonstrated bypass. |
| **3 — null marker** | **Closed** | `cells.py:39` invokes shared validation unconditionally; `marker.py:16–19` rejects null and non-object markers. `build()` directly revalidates before copying (`cells.py:339–350`). Isolated marker-read probes rejected null, arrays, Booleans, numbers and strings, while retaining `require_all=True`. The populated-forgery regression is present at `tests/test_study.py:193–200`. |

**§7 assessment:** excluding arbitrary code already executing before the harness begins is honest and appropriate for this study. The positive fresh-process claim remains unsupported because of finding 1. Keep installed package code within the enforced boundary and explicitly identify the minimal trusted bootstrap. I found no additional independent bypass in the holdout builder’s marker/context validation.

The locked matrix and adapter SPEC are **byte-identical to round 5**. All nineteen locked construction functions are unchanged, and their expected layer tuples remain supported by the specifications. All eight baseline gateway-input files match the pinned corpus materialization.

**No amendment to the holdout array: kept byte for byte.** It matches the array extracted from the verbatim round-1 findings, including whitespace and final newline: **6,638 bytes**, SHA-256:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six constructions remain source-identical to round 5 and implement their construction strings (`cells.py:287–321`). None was built.

**Verdict: `not freezable as written`.**
````

### Disposition

Both findings were accepted. Fixing commit: the commit that adds this record (round 7's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-6 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | `harness/guard.py` — using `os`, `sys`, `json` and `hashlib` from the interpreter's library and nothing else — now authenticates bytes before any pinned distribution or any other study module is imported. `package_problems()`: the environment holds exactly the distributions `harness/PINS.json` pins and each one's recorded files hash to the pinned digest, by the guard's own computation of the digest `harness/pins.py` computes (RECORD paths in string order, path, NUL, bytes, NUL; `.pyc` and RECORD skipped) — a test asserts the two computations agree for every real distribution. `study_module_problems()`: every file `harness/STUDY-MANIFEST.sha256` lists hashes to its listed digest, every `.py` under the study roots is listed, and, once the freeze pin is set, the manifest itself hashes to the pin. `establish()` runs the layout checks first and the byte checks only over an environment whose layout passed. The round-6 arrangement (a recorded initializer altered in place, metadata and RECORD unchanged) is a regression at the function and through `establish` over an environment holding only that distribution. At check time `harness/pins.py` computes the inventory once and hands the same object to `execution_problems()`. PREREGISTRATION §2 states the byte authentication; §7 names the trust anchor explicitly — the entry script, `harness/guard.py`, the four library modules and `harness/PINS.json` (anchored by the freeze commit, verifiable from inside by nothing) — with everything imported afterwards hashed by the guard before it is imported. | S1–S7 |
| 2 | MINOR | accepted | Both normalizers collapse every run of `-`, `_` and `.` to one hyphen (PEP 503); an absent or empty name is refused and grants nothing, in the guard's environment scan and in `pins.inventory()`. Tests: `Foo.Bar`, `foo--bar`, `foo__bar`, `FOO_.-bar` normalize to `foo-bar`; two directories declaring `Foo.Bar` and `foo--bar` are a duplicate, and an empty `Name:` grants nothing, at the guard and in the inventory. | S8–S11 |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 6; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| S1 the byte checks dropped from `establish()` | FAILED (1) |
| S2 a digest mismatch not reported | FAILED (1) |
| S3 an unpinned distribution admitted at bootstrap | FAILED (1) |
| S4 a listed study file's bytes unchecked | FAILED (1) |
| S5 an unlisted study module admitted | FAILED (1) |
| S6 the manifest's freeze pin unchecked | FAILED (1) |
| S7 the guard's digest computed differently from the pins' (`.pyc` entries included) | FAILED (1 error) |
| S8 the guard's normalization keeps the original separator | FAILED (1) |
| S9 the pins' normalization keeps the original separator | FAILED (1) |
| S10 an empty name grants ownership | FAILED (1) |
| S11 an empty name enters the inventory | FAILED (1) |

No mutation is labeled equivalent. Suite: 52 tests, all passing, under the documented
invocation.

### Pilot after the round

`pilots/r7` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 7 — reviewed `5d2afb3a` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `5d2afb3a8cb1624e78a515737774ade239728480`. The read-only sandbox blocked
`mktemp` and the test module's cache directory, so no test body ran for the reviewer; its
counterexamples are static arrangements inferred from the harness and the interpreter's
source, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 7. Rounds 1–6 (60d6409f, c58fad05, 8cb96e1a, 46dc8ecb, e1099309, a2786b18) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all six rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit 5d2afb3a8cb1624e78a515737774ade239728480 of the study branch (the worktree you are in). This is a methodological review of a preregistered software study's harness: the question throughout is whether the harness's validity checks are complete and whether the registration states honestly what they establish.

What changed in the round-6 application, in brief (verify each against the code, not this summary):
- Finding 1 (package bytes authenticated before import): `harness/guard.py` — now using `os`, `sys`, `json` and `hashlib` from the interpreter's library and nothing else — authenticates, before any pinned distribution or any other study module is imported: (a) `package_problems()`: the environment holds exactly the distributions `harness/PINS.json` pins, and each one's recorded files hash to the pinned digest, by the guard's own computation of the digest `harness/pins.py` computes (RECORD paths in string order, path, NUL, bytes, NUL; `.pyc` and RECORD skipped) — a test asserts the two computations agree for every real distribution, and the round-6 arrangement (a recorded initializer altered in place, metadata and RECORD unchanged) is a regression at the function and through `establish`; (b) `study_module_problems()`: every file `harness/STUDY-MANIFEST.sha256` lists hashes to its listed digest, every `.py` under the study roots is listed, and, once the freeze pin is set, the manifest itself hashes to the pin. `establish()` runs the layout checks first and the byte checks only over an environment whose layout passed. PREREGISTRATION §2 states it; §7 now names the trust anchor explicitly: the entry script, `harness/guard.py`, the four library modules, and `harness/PINS.json` (anchored by the freeze commit, verifiable from inside by nothing). At check time `harness/pins.py` computes the inventory once and hands the same object to `execution_problems()`.
- Finding 2 (normalization, empty names): both normalizers collapse every run of `-`, `_` and `.` to one hyphen (PEP 503); an absent or empty name is refused and grants nothing, in the guard and in `pins.inventory()`; equivalent-name and empty-name regressions are present.

Your job this round:
1. Verify both round-6 dispositions against the code; say closed or residue (with lines).
2. Judge whether the trust anchor §7 names is the minimal one and is stated honestly, and whether the fresh-process claim is now supported by the bootstrap order (what runs before what). If code other than the pinned code could run in a process the harness starts before the guard has refused it, report it; a way that requires code already running in the process before the harness begins is inside the stated base.
3. The locked matrix and the adapter SPEC are unchanged this round; say so if you confirm it.
4. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
5. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-6 dispositions (closed / residue), then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed `5d2afb3a8cb1624e78a515737774ade239728480`. **Three BLOCKER findings remain.**

The prescribed test command failed at `mktemp`, then during test-module import because the sandbox is read-only. **No test bodies ran.** Read-only checks confirmed the seven package digests, agreement between both digest implementations, the manifest’s listed hashes, and the gateway digest. No primary attempt, pilot, or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`. The counterexamples are static filesystem arrangements inferred from the harness and the installed CPython source; I did not plant or execute them.

1. **BLOCKER — the guard’s new imports execute before import resolution is protected.**

   **Locations:** `harness/guard.py:31–34,306–313`; `harness/run_attempt.py:23–25`; `harness/run_layers.py:24–26`; `harness/score.py:35–37`; `PREREGISTRATION.md:309–317`.

   The actual order is: prepend `harness/` → import `guard` → import `hashlib` and `json`, including their dependencies → call `establish()` → check layout and bytes.

   Consequently, a planted `harness/hashlib.py` executes before `shadow_problems()` can refuse it. Even leaving all four named library modules untouched, a planted `harness/_hashlib.py` executes through the genuine standard-library `hashlib.py:167`. A fresh-interpreter read-only probe confirmed that neither `hashlib` nor `_hashlib` was already loaded at entry.

   There is also an earlier resolution gap: `harness/guard/__init__.py` takes precedence over `harness/guard.py`. The named trust anchor is therefore not necessarily the file executed.

   These arrangements first execute foreign code **after the harness begins**. They are outside §7’s exception for code already running beforehand.

   **Smallest sufficient edit:** load the exact trusted `guard.py` source without ordinary module-name resolution, and restrict bootstrap dependency imports—including transitive imports—to the trusted interpreter library before loading them. Preserve the original search path for subsequent validation. Add fresh-process regressions asserting refusal before a planted initializer or dependency payload executes.

   The new regression at `harness/tests/test_study.py:845–853` does not exercise this boundary: the guard is already imported. It also uses the real study pins against an unpinned synthetic `pkg`, allowing the asserted refusal for reasons independent of altered bytes.

2. **BLOCKER — recorded sourceless bytecode passes the new pre-import authentication.**

   **Locations:** `harness/guard.py:158–168,256–280`; `harness/pins.py:73–80,218–222`; `adapter/verify_attestation.py:27`; `PREREGISTRATION.md:54–59,317`.

   Add this file beneath the virtual environment’s `site-packages`:

   ```text
   in_toto_attestation/v1/statement_pb2/__init__.pyc
   ```

   Add its relative path to the existing in-toto-attestation distribution’s RECORD, leaving all previously hashed files unchanged.

   The layout check grants ownership to both the new file and its directory. Both digest implementations skip `.pyc` entries and RECORD itself, so every package digest remains unchanged. The study manifest is unaffected.

   CPython checks package initializers before same-named module files. Its `SourcelessFileLoader` therefore loads this initializer instead of the pinned `statement_pb2.py`. **An empty `sys.pycache_prefix` does not prevent standalone `.pyc` imports.** The installed implementation establishes this at `importlib/_bootstrap_external.py:1111–1125,1519–1540,1627–1635`.

   The later loader check can report the substitution, but only after its code has executed and could disable that check. Thus authenticating the current digest does not establish the claimed execution identity.

   **Smallest sufficient edit:** reject standalone `.pyc` files outside the ignored ordinary cache directories during the environment layout check, even when RECORD lists them. Add a regression with a recorded bytecode package initializer, unchanged package digests, and refusal before payload execution.

3. **BLOCKER — an inherited cache prefix is checked only after potentially executing its contents.**

   **Locations:** `harness/run_attempt.py:13–25`; `harness/run_layers.py:14–26`; `harness/score.py:25–37`; `harness/guard.py:289–311`; `PREREGISTRATION.md:42–45,313–315`.

   Each entry script creates a fresh prefix only when `sys.pycache_prefix` is unset. An existing `PYTHONPYCACHEPREFIX` is used immediately; its emptiness is checked later, inside the imported guard.

   A prefix containing a valid timestamp-and-size-matching cache for the unchanged `guard.py` can therefore execute substituted bytecode before `cache_problems()` runs. The attacker need not provide caches for startup modules or execute anything before the entry script.

   CPython reads matching bytecode before considering `dont_write_bytecode`; that flag controls writes (`importlib/_bootstrap_external.py:923–973,978`). The registration’s assertion that the guard is compiled from its source is consequently unsupported.

   **Smallest sufficient edit:** establish or validate an empty cache prefix using the already loaded `os` and `sys` **before any further import**. Do this in every entry point, and explicitly prevent cache use when loading the trusted guard source. Add a fresh-process regression with a prepopulated guard cache.

The round-6 dispositions resolve as follows:

| Round-6 finding | Verdict | Assessment |
|---|---|---|
| **1 — authenticate bytes before import** | **Residue** | The original altered recorded `.py` initializer is now covered: layout precedes byte checks (`guard.py:306–311`), distribution hashing is implemented (`158–196`), and manifest/file/module coverage is implemented (`199–239`). Both digest computations agree for all seven real distributions. `pins.problems()` now passes the same inventory object to `execution_problems()` (`pins.py:250–271`). Findings 1–3 above prevent closure of the broader guarantee. |
| **2 — normalization and empty names** | **Closed** | Both normalizers correctly collapse separator runs (`guard.py:111–120`; `pins.py:40–49`). Absent/empty names grant nothing (`guard.py:123–155`; `pins.py:58–69`). The requested equivalent-name and empty-name regressions are present (`tests/test_study.py:788–814`). |

**Trust-anchor assessment:** the entry source, guard source, and externally anchored `PINS.json` are appropriate study-specific trust anchors. The exclusion of arbitrary code already executing before entry is honest. However, the four-module description is not the executable dependency closure: genuine `hashlib` and `json` import additional modules, and `sys` is not compiled from a source file. Those dependencies belong to the already stated interpreter-library base. Qualify §7’s “Everything imported afterwards” to mean study and distribution code, and enforce the bootstrap boundary above. The fresh-process claim is presently unsupported.

The locked matrix and adapter SPEC are **byte-identical to round 6**. All nineteen locked constructions are unchanged; their registered layer outcomes remain supported by the three specifications. All eight baseline gateway-input files match the pinned corpus materialization.

**Holdout amendment: none; kept byte for byte.** The file matches the JSON array extracted from the verbatim round-1 findings, including whitespace and final newline: **6,638 bytes**, SHA-256:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six construction functions (`harness/cells.py:287–321`) remain source-identical to their round-1 implementation and implement the unchanged construction strings. None was built.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 8's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-7 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | Every entry script begins, only when it is the entry point of a process (`__name__ == "__main__"`; imported as a module by another harness process it does not re-bootstrap), with a bootstrap block using `os` and `sys` alone: a fresh, empty cache prefix of its own, bytecode writing disabled, the import path the process started with recorded, `sys.path` restricted to the interpreter's library and the virtual environment (nothing under the study roots resolvable by name), `types` imported from the library, `harness/guard.py` compiled from its bytes by exact path (`compile` + `exec` into a fresh module object: no module-name resolution, no cache) and `guard.establish(study, original_path)` called; the guard judges the original path and refuses foreign entries, then the roots (the shadow rule now knows the interpreter's extension modules too), the environment and the bytes, and only then puts the study roots on `sys.path`. `pins.execution_problems()` recognises the bootstrap-loaded guard by its exact file and manner of loading and refuses to run under any other. Fresh-process regressions run the runner from a copy of the study tree with a payload-writing module planted at `harness/hashlib.py`, `harness/_hashlib.py`, `harness/types.py` and `adapter/json.py`, and with a `harness/guard/__init__.py` directory, and assert refusal with the payload never executed and no root spent. The earlier in-process regression the reviewer judged weak is superseded by these. PREREGISTRATION §2 states the order; §7 qualifies the trust anchor (the bootstrap block and the guard compiled from their bytes; the interpreter's library, the bootstrap's dependency closure inside it; `PINS.json`) and the claim ("every study module and every distribution file imported afterwards" — the interpreter's own modules are trusted as the base says). | T2, T3, T6, T8, T10 (T7, the roots not restored, is fatal to every import and was not run) |
| 2 | BLOCKER | accepted | The environment layout check refuses any standalone `.pyc`/`.pyo` outside a `__pycache__` directory and any `.pth`, recorded or not (the import system would load the one without its source; the digests skip bytecode). A regression records a `pkg/mod2/__init__.pyc` in a temporary distribution, asserts the package digest is unchanged by it, and asserts the layout refuses it and a recorded `.pth`. PREREGISTRATION §2 says so. | T4, T5 |
| 3 | BLOCKER | accepted | The bootstrap never uses an inherited prefix: a fresh one is made before any further import, whatever `PYTHONPYCACHEPREFIX` says; the runner strips `PYTHONPYCACHEPREFIX` from its children, which make their own. A fresh-process regression prepopulates an inherited prefix with timestamp-and-size-valid caches for `guard.py` and for the library's `types.py`, both carrying a payload, runs the runner with that prefix inherited, and asserts the payload never executed and the pilot completed. The test module — imported by unittest, not an attempt process — keeps an inherited prefix only if it holds no file (README's invocation supplies an empty one so that the module itself is compiled from source), which §2 states. | T1, T9 |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 7; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| T1 an inherited cache prefix used when set | FAILED (1) |
| T2 the import path not restricted before the bootstrap's imports | FAILED (1) |
| T3 the guard imported by name | FAILED (2) |
| T4 recorded standalone bytecode allowed | FAILED (1 error) |
| T5 a recorded path hook allowed | FAILED (1 error) |
| T6 extension-module names not treated as shadows | FAILED (1) |
| T8 the current path judged instead of the original | FAILED (1) |
| T9 children inherit the cache prefix | FAILED (1) |
| T10 the pins do not recognise the bootstrap-loaded guard | FAILED (3 + 2 errors) |

No mutation is labeled equivalent (T7 — the study roots never put back on the path — makes
every harness import fail and was not run). Suite: 56 tests, all passing, under the documented
invocation.

### Pilot after the round

`pilots/r8` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 8 — reviewed `d5319e78` — verdict: `not freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `d5319e78a5a87a9cddf0e00ffe1a8e85eb6ceb26`. The read-only sandbox blocked
`mktemp` and the test module's cache directory, so no test body ran for the reviewer; its
counterexamples are static arrangements and read-only control-flow probes, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 8. Rounds 1–7 (60d6409f, c58fad05, 8cb96e1a, 46dc8ecb, e1099309, a2786b18, 5d2afb3a) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all seven rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit d5319e78a5a87a9cddf0e00ffe1a8e85eb6ceb26 of the study branch (the worktree you are in). This is a methodological review of a preregistered software study's harness: the question throughout is whether the harness's validity checks are complete and whether the registration states honestly what they establish.

What changed in the round-7 application, in brief (verify each against the code, not this summary):
- Finding 1 (the bootstrap's own imports and resolution): every entry script (`run_attempt.py`, `run_layers.py`, `score.py`) now begins, only when it is the entry point of a process, with a bootstrap block that uses `os` and `sys` alone: it makes a fresh, empty cache prefix of its own unconditionally, disables bytecode writing, records the import path the process started with, restricts `sys.path` to the interpreter's library and the virtual environment (so nothing under the study roots can be resolved by name), imports `types` from the library, compiles `harness/guard.py` from its bytes by exact path (`compile` + `exec` into a fresh module object; no module-name resolution, no cache) and calls `guard.establish(study, original_path)`; the guard judges the original path, refuses foreign entries, then the roots, the environment, the bytes, and only then puts the study roots on `sys.path`. Imported as a module by another harness process (score imports run_layers), a script does not re-bootstrap. The shadow rule also refuses `.py` files named like the interpreter's extension modules (lib-dynload). `pins.execution_problems()` recognises the bootstrap-loaded guard by its exact file and its manner of loading (no spec, no loader), and refuses to run if the guard in the module table is not that. Fresh-process regressions run `run_attempt.py` from a copy of the study tree with a payload-writing module planted at `harness/hashlib.py`, `harness/_hashlib.py`, `harness/types.py`, `adapter/json.py`, and with a `harness/guard/__init__.py` directory, and assert refusal with the payload never executed and no root spent.
- Finding 2 (recorded sourceless bytecode): the environment layout check refuses any standalone `.pyc`/`.pyo` outside a `__pycache__` directory and any `.pth`, recorded or not; a regression records a `pkg/mod2/__init__.pyc` in a temporary distribution, asserts the package digest is unchanged by it, and asserts the layout refuses it.
- Finding 3 (inherited cache prefix): the bootstrap never uses an inherited prefix (a fresh one is made before any further import) and the runner strips `PYTHONPYCACHEPREFIX` from its children, which make their own; a fresh-process regression prepopulates an inherited prefix with timestamp-and-size-valid caches for `guard.py` and for the library's `types.py`, both carrying a payload, runs the runner with that prefix inherited, and asserts the payload never executed and the pilot completed. The test module (imported by unittest, not an attempt process) keeps an inherited prefix only if it holds no file, as README's invocation supplies; PREREGISTRATION §2 states the bootstrap order and §7 the trust anchor as the entry script's bootstrap block and `harness/guard.py` compiled from their bytes, the interpreter's library (with the bootstrap's dependency closure inside it), and `harness/PINS.json`.

Your job this round:
1. Verify every round-7 disposition against the code; for each of findings 1–3 say closed or residue (with lines).
2. Judge whether the bootstrap order now supports the fresh-process claim as §7 states it, and whether §7's trust anchor is stated honestly and minimally.
3. The locked matrix and the adapter SPEC are unchanged this round; say so if you confirm it.
4. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
5. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-7 dispositions (closed / residue), then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed `d5319e78a5a87a9cddf0e00ffe1a8e85eb6ceb26`. **Two BLOCKER findings and one MINOR discrepancy remain.**

The prescribed test command failed at `mktemp`, then during test-module import because the sandbox is read-only. **No test bodies ran.** Read-only checks confirmed all seven package digests, agreement between both digest implementations, the manifest, and the gateway digest. No primary attempt, pilot, or holdout construction ran; no files changed.

Locations below are relative to `studies/022-outside-format-binding/`.

1. **BLOCKER — the bootstrap still permits unchecked environment paths to supply its dependencies.**

   **Locations:** [harness/run_attempt.py:30](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/run_attempt.py:30), `harness/run_layers.py:31–43`, `harness/score.py:42–54`; `harness/guard.py:37–38,56–66,319–324`; `PREREGISTRATION.md:43–66,317–328`.

   The filter retains **every descendant of `sys.base_prefix` or `sys.prefix`, in its original order**. It does not restrict bootstrap imports to authenticated library locations.

   A concrete counterexample is an unrecorded `hashlib.py` placed in the virtual environment’s `site-packages`, with `PYTHONPATH` set to that directory. The bootstrap retains that entry ahead of the standard library. Executing the exact, genuine `guard.py` then imports the planted module **before** `path_problems()` rejects `PYTHONPATH`, before the environment layout check, and before package hashing.

   A fresh-interpreter, read-only probe confirmed that this directory remains first after the exact filter and that `types`, `hashlib`, `_hashlib`, and `json` are not already loaded at entry. Payload execution is inferred from this order; I did not plant a file.

   The filter also retains a study root when the study resides beneath either accepted prefix, contradicting the unconditional assertion that nothing under the study roots can resolve by name before verification.

   These are replacements under environment-controlled paths that first execute **after entry**, outside §7’s exception for previously executing code.

   **Smallest sufficient edit:** give bootstrap imports an explicit search path containing only trusted interpreter-library locations, including its extension directory. Preserve the original environment roots separately and audit them as data; restore environment and study import roots only after authentication. Add fresh-process regressions for an injected path beneath the environment prefix and a study located beneath an accepted prefix.

2. **BLOCKER — cache-directory exhaustion silently restores the inherited-cache vulnerability.**

   **Locations:** [harness/run_attempt.py:18](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/run_attempt.py:18), `harness/run_layers.py:19–33`, `harness/score.py:30–44`, `harness/tests/test_study.py:15–28`; `PREREGISTRATION.md:43–45`.

   All three entry scripts try 10,000 directory names. If every `mkdir` raises `FileExistsError`, execution falls through without assigning a fresh prefix or refusing.

   A read-only control-flow probe executed each exact allocation loop with a collision-only `mkdir` stand-in. **All three exhausted 10,000 attempts and continued with the inherited prefix unchanged.**

   This corresponds to a static filesystem arrangement: precreate every candidate name for the launching process’s PID under `TMPDIR`, then execute Python with an inherited prefix containing a timestamp-and-size-valid cache for `types.py`. The subsequent `import types` can execute that cache before the guard checks emptiness. CPython’s installed `importlib/_bootstrap_external.py:923–973,978` confirms that disabling bytecode writes does not disable cache reads.

   The unused helper `guard.fresh_cache_prefix()` correctly raises on exhaustion (`guard.py:331–341`); its inlined counterparts omit that branch.

   **Smallest sufficient edit:** add a `for … else: raise SystemExit(...)` exhaustion branch before any subsequent import in each bootstrap, including the test bootstrap. Add an exhaustion regression with a populated inherited prefix and assert refusal before payload execution.

3. **MINOR — the new guard-loader exception is not an exclusive requirement, contrary to the disposition.**

   **Locations:** [harness/pins.py:127](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/exp-022/studies/022-outside-format-binding/harness/pins.py:127), `harness/pins.py:107–108,227–235`; `PREREG-REVIEW.md:1717`.

   The disposition says the check recognizes the guard’s exact loading manner and “refuses to run under any other.” The implementation accepts the intended no-spec/no-loader case, but an ordinary `SourceFileLoader` import of the same `guard.py` falls through to the generic registered-study-module allowance, which includes `"guard"`.

   A read-only differential probe classified the exact-path bootstrap module and a normally source-loaded, unchanged guard. Both produced the identical problem list, containing only the deliberately nonexistent cache-prefix directory; **the normal loader elicited no guard refusal**.

   This is a discrepancy in the promised discriminator, not a demonstrated fresh-process authentication bypass.

   **Smallest sufficient edit:** exclude `guard` from the generic study-module fallback and explicitly require its bootstrap case. Add a regression distinguishing that case from an ordinary source import.

The round-7 dispositions resolve as follows:

| Round-7 finding | Verdict | Assessment |
|---|---|---|
| **1 — bootstrap imports and resolution** | **Residue** | Exact-path source compilation, entry-point-only bootstrapping, preservation of the original path, extension-module shadow detection, and restoration of study roots after successful checks are implemented (`run_attempt.py:14–42`; `guard.py:70–97,319–328`). The planted-study-module and guard-directory regressions are present (`tests/test_study.py:1032–1053`). Findings 1 and 3 above remain. |
| **2 — recorded sourceless bytecode** | **Closed** | The layout check rejects standalone `.pyc`/`.pyo` and `.pth` independently of RECORD ownership (`guard.py:276–293`). The regression demonstrates unchanged digest plus specific refusal of the recorded initializer and path hook (`tests/test_study.py:756–767`). |
| **3 — inherited cache prefix** | **Residue** | Successful allocation replaces the inherited prefix before further imports; children receive neither `PYTHONPATH` nor `PYTHONPYCACHEPREFIX` (`run_attempt.py:63–68`). The populated-prefix regression is present (`tests/test_study.py:1055–1088`), and the test module retains an inherited prefix only when empty (`:10–22`). Finding 2 leaves the unconditional guarantee false. |

**Bootstrap and trust-anchor assessment:** §7 now correctly names the interpreter-library dependency closure and limits the hashing claim to study and distribution files. The bootstrap source, exact guard source, interpreter base, and externally anchored `PINS.json` form an appropriately narrow declared anchor. However, the implemented bootstrap can still execute dependencies from unchecked search locations or an inherited cache after allocation exhaustion. **The fresh-process claim remains unsupported.** These routes should be closed without expanding the declared trust base to excuse them.

The locked matrix and adapter SPEC are **byte-identical to the reviewed round-7 commit**. All nineteen locked constructions are unchanged; their registered layer expectations remain supported by the three specifications. All eight baseline gateway-input files match the pinned corpus materialization, and both baseline attestation payloads match the specified binding.

**Holdout amendment: none; kept byte for byte.** The file exactly matches the array in the verbatim round-1 record, including whitespace and final newline: **6,638 bytes**, SHA-256:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six construction functions (`harness/cells.py:287–321`) remain source-identical to their round-1 implementation and faithfully implement the unchanged construction strings. None was built.

**Verdict: `not freezable as written`.**
````

### Disposition

Every finding was accepted. Fixing commit: the commit that adds this record (round 9's prompt
names it as the reviewed SHA). "Mutation" names the entries of the round-8 mutation table.

| # | Severity | Disposition | What changed | Mutation |
|---|---|---|---|---|
| 1 | BLOCKER | accepted | The bootstrap no longer filters the inherited path: it replaces `sys.path` with the interpreter's own library directories alone (the pure-Python directory and its extension directory, located from the `os` module the interpreter loaded at start-up), in no inherited order, before importing `types` and executing the guard. The guard's `path_problems()` judges the original path against exact directories — the study roots, `library_dirs()`, `environment_dirs()` — not anything beneath a prefix; `environment_dirs()` locates the environment's site-packages from `sys.prefix` rather than reading it from the path; after every check passes the guard sets the canonical path (study roots, library, environment), never the inherited order. Fresh-process regressions: a payload `hashlib.py` on an injected `PYTHONPATH` directory beneath the environment's prefix, and a study copy beneath the environment's prefix with a planted `harness/hashlib.py`; in both the payload never runs. Unit regressions: an entry beneath either prefix is refused; the path after the checks puts the library before the environment whatever the inherited order. PREREGISTRATION §2 states it. | U1, U4, U5 (U6 equivalent: reading the environment root from the inherited path, with the located directory as fallback, scans a superset and refuses nothing less — the change is for independence from the path, not a stricter refusal) |
| 2 | BLOCKER | accepted | Every bootstrap (the three entry scripts and the test module) refuses to start if no fresh prefix can be made (`for … else: raise SystemExit`). A regression pre-creates every candidate name for the process, supplies an inherited prefix holding a timestamp-and-size-valid `hashlib` cache carrying a payload, runs the runner in that process through `runpy`, and asserts refusal with the payload never executed. The unused `fresh_cache_prefix()` helper is removed. §2 states the refusal. | U2 |
| 3 | MINOR | accepted | `guard` is removed from the generic study-module allowance; it is admitted only as the bootstrap loaded it (exact file, no spec, no loader). A regression loads the same file the ordinary way under the name `guard` and asserts refusal. | U3 |
| holdout | — | unchanged | `harness/MATRIX-HOLDOUT.json` untouched (SHA-256 `10f87d02…`); constructions unchanged. | — |

### Mutation table (round 8; each breaks one fix; the suite must fail)

| Mutation | Result |
|---|---|
| U1 the bootstrap keeps every inherited entry beneath a prefix | FAILED (2) |
| U2 exhaustion falls through to the inherited prefix | FAILED (1) |
| U3 the guard admitted through the generic fallback | FAILED (1) |
| U4 the original path judged by prefix, not exact directory | FAILED (1) |
| U5 the inherited order kept after the checks | FAILED (1) — after the canonical-order case was added |
| U6 the environment root read from the inherited path (located directory as fallback) | OK — **equivalent**: a superset of the scan, refusing nothing less |

One mutation is labeled equivalent, with the reason. Suite: 59 tests, all passing, under the
documented invocation.

### Pilot after the round

`pilots/r9` (harness validation, `--pilot`, locked stratum only, holdout not built): `R1 holds`
over the nineteen locked cells, zero validity failures, zero gate failures.

## Round 9 — reviewed `3d18ede3` — verdict: `freezable as written`

Reviewer: Codex (GPT-6 Astra), `codex exec -s read-only`, run 2026-09-14 over the study branch
worktree at commit `3d18ede3a5f3f952f1f4df3673bbfe477222829a`. The read-only sandbox blocked
`mktemp` and the test module's cache directory, so no test body ran for the reviewer; its
checks were read-only, as its report says.

### Prompt (verbatim)

````text
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). This is ROUND 9. Rounds 1–8 (60d6409f, c58fad05, 8cb96e1a, 46dc8ecb, e1099309, a2786b18, 5d2afb3a, d5319e78) were your own reviews; each returned `not freezable as written`; the maintainer accepted every finding of every round. The record of all eight rounds — your prompts and findings verbatim, the maintainer's disposition tables naming what changed per finding, mutation tables, and the post-round pilots — is studies/022-outside-format-binding/PREREG-REVIEW.md. You are reviewing commit 3d18ede3a5f3f952f1f4df3673bbfe477222829a of the study branch (the worktree you are in). This is a methodological review of a preregistered software study's harness: the question throughout is whether the harness's validity checks are complete and whether the registration states honestly what they establish.

What changed in the round-8 application, in brief (verify each against the code, not this summary):
- Finding 1 (the bootstrap's search path): the bootstrap no longer filters the inherited path; it replaces `sys.path` with the interpreter's own library directories alone — the pure-Python directory and its extension directory, located from the `os` module the interpreter loaded at start-up — in no inherited order, before importing `types` and executing the guard; the guard's `path_problems()` judges the original path against exact directories (the study roots, `library_dirs()`, `environment_dirs()`), not anything beneath a prefix; `environment_dirs()` locates the environment's site-packages from `sys.prefix` rather than reading it from the path; after every check passes the guard sets a canonical path (study roots, library, environment), never the inherited order. Fresh-process regressions: a payload `hashlib.py` on an injected `PYTHONPATH` directory beneath the environment's prefix, and a study copy placed beneath the environment's prefix with a planted `harness/hashlib.py` — in both the payload never runs.
- Finding 2 (cache-prefix exhaustion): every bootstrap (the three entry scripts and the test module) refuses to start if no fresh prefix can be made (`for … else: raise SystemExit`); a regression pre-creates every candidate name for the process, supplies an inherited prefix holding a timestamp-and-size-valid `hashlib` cache carrying a payload, runs the runner in that process, and asserts refusal with the payload never executed.
- Finding 3 (the guard's loading manner): `guard` is no longer in the generic study-module allowance; it is admitted only as the bootstrap loaded it (exact file, no spec, no loader); a regression loads the same file the ordinary way under the name `guard` and asserts refusal.

Your job this round:
1. Verify every round-8 disposition against the code; for each of findings 1–3 say closed or residue (with lines).
2. Judge whether the bootstrap order now supports the fresh-process claim as §7 states it, and whether §7's trust anchor is stated honestly and minimally.
3. The locked matrix and the adapter SPEC are unchanged this round; say so if you confirm it.
4. The holdout: confirm harness/MATRIX-HOLDOUT.json is still your round-1 array byte for byte (SHA-256 10f87d02…) and the six constructions unchanged. Do not build a holdout cell.
5. Anything new the round introduced.

This round you MAY execute: the virtual environment holding the pinned packages is at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv (python: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python) and the pinned gateway binary at /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 (SHA-256 aaa16fec…; harness/PINS.json pins it). Run the harness tests from the study directory exactly as README.md states:
    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/bin/gateway-03582d9 /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/da38d36e-3eb2-4207-88ac-9dbd20248df1/scratchpad/intoto-venv/bin/python -W ignore -m unittest discover -s harness/tests
Your sandbox is read-only and may block temporary-file writes (mktemp and the tests' temporary directories); if the tests cannot run, say so and reason from the code. Do NOT run the primary attempt, do NOT run a pilot, do NOT build a holdout cell. Do not modify any file.

Output: findings numbered and severity-tagged (BLOCKER / MAJOR / MINOR) with file:line locations and the smallest sufficient edit, then per-finding verdicts on the round-8 dispositions (closed / residue), then any amendment to your holdout array (kept byte for byte), then a verdict: `freezable as written` or `not freezable as written`. A clean pass on an item is a finding only if you can defend it.

The round-1 prompt follows for reference; its reading list and its standards apply unchanged.

----- ROUND-1 PROMPT (reference) -----
You are the pre-freeze cross-vendor reviewer for Study 022 in the judgment-pack-evaluator-experiments repository, under the interim review regime (a model from a different vendor than the one that drafted; Claude drafted). The study is NOT frozen; your job is to find where the preregistration or the binding specification overclaims, where a registered cell's expectation does not follow from the three specifications it rests on (the gateway's SPEC.md; DSSE and the in-toto Statement v1 as the pinned reference implementation realizes them; the adapter's own SPEC.md), where the harness could produce a result the registration would misread, and where the design lets a favourable outcome be reached for the wrong reason. A clean pass is a finding only if you can defend it. Do not run the primary attempt; you may read everything and run the harness tests (the virtual environment holding the pinned packages is not available to you; the gateway binary is not available to you; reason from the documents and say what you could not execute).

Read, in the study directory studies/022-outside-format-binding/ of the current worktree:
- PREREGISTRATION.md — the registration: question, R1 and R2, the two strata, apparatus and pins, the scenario and threat model, the cells and the structures their reasons rest on, the decision rule, validity and enforcement, limits.
- adapter/SPEC.md — the binding: the attestation's shape (subjects, predicate type, predicate), the adapter's key, what the binding asserts (section 3), the three layers (4), the in-toto layer's ceremony (5), the reduced form the registration compares (6), the ownership map (7).
- harness/MATRIX.json — nineteen registered cells with exact per-layer expectations, ownership and reasons. Verify EVERY cell against the sources: the gateway's SPEC.md at commit 03582d9 of /home/onword/repo/judgment-pack/judgment-pack-gateway (read with `git -C <path> show 03582d9:SPEC.md`; sections 1.2a, 1.4, 3, 4 including steps 5-7, and the status vocabulary), the DSSE and in-toto Statement v1 contracts as securesystemslib 1.3.1 and in-toto-attestation 0.9.3 implement them (reason from their documented behaviour: PAE over payload type and payload, key id matching, Statement validation), and adapter/SPEC.md. Say per cell whether the expected outcome of each layer follows, and name any cell whose expectation you can show does not.
- adapter/bind.py, adapter/verify_attestation.py, adapter/verify_binding.py — the binding and the two non-gateway layers; check them against adapter/SPEC.md clause by clause (the ceremony's order, the codes, the subject re-digest rules, the binding's rules), and look for a way a layer could pass for the wrong reason.
- harness/cells.py — the nineteen constructions; check each does what its registered cell says and nothing else, deterministically.
- harness/run_layers.py, harness/score.py, harness/run_attempt.py, harness/pins.py, harness/make_manifest.py, harness/PINS.json, harness/tests/test_study.py — enforcement: pins held before a registered attempt and before adjudication; the exclusive root and the marker; cells rebuilt and compared; observations bound and complete; the reduction; the decision rule. Look for any path to "R1 holds" without the registered evidence.
- fixtures/baseline/ — the corpus vector v3-action-valid materialized (compare with `git -C <gateway path> show 03582d9:corpus/v3/stores/v3-action-valid.json`) and the attestations the adapter bound from it.
- README.md, DEVIATIONS.md, .gitignore — status banners and the freeze-set discipline (README.md and DEVIATIONS.md outside the manifest; tools/check_freeze_sets.py at the repository root says why).
- For precedent, studies/014-openworkproof-binding/PREREGISTRATION.md and its adapter/SPEC.md (the same shape of study: an external receipt protocol, a binding layer, a locked stratum and a reviewer's holdout), and studies/021-history-replay-catch/PREREG-REVIEW.md rounds 1-3 (the enforcement standard this repository's reviews have held harnesses to).

Then, as the reviewer's holdout stratum: propose at least four holdout cells — new constructions, each described precisely enough for the maintainer to implement as a function of the baseline in harness/cells.py before the freeze (you may name store edits, attestation edits with or without the adapter's key, and combinations) — each with YOUR expected outcome of all three layers in the reduced form of adapter/SPEC.md section 6 and your reason. Give them as a JSON array in the schema of harness/MATRIX.json (id, role "endpoint", attackerCapability, expected, ownership, structure, reason) plus a `construction` string per cell; the maintainer implements the constructions verbatim and keeps your array byte-for-byte as harness/MATRIX-HOLDOUT.json.

For each finding give: severity (BLOCKER / MAJOR / MINOR), the exact sentence, cell or line, what the source says, and the smallest edit that would make the registration true. Then a verdict: `freezable as written`, `freezable after fixes` (list them), or `not freezable as written`.
````

### Findings (verbatim)

````markdown
Reviewed **`3d18ede3a5f3f952f1f4df3673bbfe477222829a`**. I found **no remaining BLOCKER, MAJOR, or MINOR methodological findings**. No corrective edit is required.

The prescribed test command failed at `mktemp`, then during test-module import because the filesystem is read-only. **No test bodies ran.** Separate read-only checks confirmed the manifest, all seven package versions and digests, agreement between both digest implementations, and the gateway digest. No primary attempt, pilot, or holdout construction ran; no files changed.

Paths below are relative to `studies/022-outside-format-binding/`.

**Round-8 dispositions:**

| Finding | Verdict | Evidence |
|---|---|---|
| **1 — BLOCKER: bootstrap search path** | **Closed** | The three entry scripts replace the inherited path before importing `types` or executing the guard: `harness/run_attempt.py:28–46`, `harness/run_layers.py:29–47`, `harness/score.py:40–58`. The test bootstrap does likewise at `harness/tests/test_study.py:25–39`. `guard.library_dirs()` and `environment_dirs()` locate the permitted roots independently of inherited ordering (`harness/guard.py:53–62`); `path_problems()` requires exact directory membership (`:70–83`); successful establishment installs the canonical path (`:335–344`). The two requested fresh-process regressions and the exact-path/order assertions are present (`harness/tests/test_study.py:728–744,1071–1097`). |
| **2 — BLOCKER: cache-prefix exhaustion** | **Closed** | Exhaustion raises before further imports in every allocation loop: `harness/run_attempt.py:18–27`, `harness/run_layers.py:19–28`, `harness/score.py:30–39`, `harness/tests/test_study.py:15–24`. A read-only control-flow probe of each exact loop confirmed refusal after 10,000 collisions. The regression supplies a valid poisoned `hashlib` cache and exhausts the launching process’s candidates (`harness/tests/test_study.py:1099–1132`). The unused helper is removed. |
| **3 — MINOR: guard-loading discriminator** | **Closed** | `guard` is excluded from `STUDY_MODULES` (`harness/pins.py:107–108`); its bootstrap case requires the exact source path, no spec, and no loader (`:227–228`). An ordinary source import falls into the refusing study-module branch (`:229–235`). The regression is present (`harness/tests/test_study.py:675–685`). My read-only differential probe independently confirmed the additional refusal for an ordinarily imported, unchanged guard and its disappearance when the bootstrap module was restored. |

**Bootstrap and trust-anchor assessment:** the order now supports §7’s fresh-process claim within its stated base. A fresh cache prefix precedes further imports; bootstrap dependencies resolve through the interpreter’s library alone; the exact guard source executes; layout checks precede package and manifest authentication; study and environment import paths become available only after those checks pass (`harness/guard.py:335–344`).

The anchor in `PREREGISTRATION.md:323–340` is appropriately narrow for this design: the entry bootstrap, exact guard source, externally anchored `PINS.json`, and the interpreter-library dependency closure. The interpreter build, library/import machinery, native dependencies, operating system, startup exception, and absence of concurrent replacement remain explicit assumptions (`:307–340`). The registration correctly distinguishes these guarantees from authentication against arbitrary code already executing inside the process. No expansion of that trust base is needed to excuse the former round-8 routes.

**The locked matrix and adapter SPEC are byte-identical to the reviewed round-8 commit.** All nineteen constructions are also unchanged. Rechecking against gateway `03582d9:SPEC.md`, the installed pinned DSSE/Statement implementations, and the adapter contract supports every registered layer expectation:

| Cell | Gateway / in-toto / binding expectations | Decisive basis |
|---|---|---|
| `pos` | All follow | Valid corpus inputs and the specified binding. |
| `neg` | All follow | Changed signature fails DSSE; neither other layer checks it. |
| `a01` | All follow | Both artifact re-digests fail; receipt correspondence remains intact. |
| `a02` | All follow | Receipt signature and passing sequence fail; action citation re-digest and acquisition binding detect different changes. |
| `a03` | All follow | Missing receipt affects sequence, count and citation resolution; its orphan attestation is outside receipt-driven enumeration. |
| `a04` | All follow | The claimed decision-record digest has no matching candidate. |
| `a05` | All follow | Only the gateway consults the seal registry. |
| `a06` | All follow | Copied receipt is misfiled and exceeds the seal; both ceremonies require its missing attestation. |
| `a07` | All follow | Gateway signature and predicate/store correspondence fail; attestation subjects remain valid. |
| `b01` | All follow | Unsigned payload alteration fails DSSE and predicate/store correspondence. |
| `b02` | All follow | Consumer key selection rejects the foreign key before verification. |
| `b03` | All follow | Swapped artifact exists and re-digests; binding detects the wrong correspondence. |
| `b04` | All follow | Consumer predicate-type pin rejects it. |
| `b05` | All follow | Consumer Statement-version pin rejects it. |
| `b06` | All follow | Both non-gateway layers require the deleted attestation. |
| `b07` | All follow | Payload-type rejection precedes signature verification. |
| `b08` | All follow | Re-signed predicate remains valid as an attestation but differs from the stored receipt. |
| `b09` | All follow | Remaining subjects validate and match; binding requires the omitted citation subject. |
| `c01` | All follow | Coherent foreign receipt chain fails gateway key selection; freshly bound attestations and correspondence pass. |

All eight baseline gateway-input files match the pinned corpus materialization. Both baseline attestation payloads match the specified binding. I found no new methodological defect introduced by this round.

**Holdout amendment: none; kept byte for byte.** `harness/MATRIX-HOLDOUT.json` exactly matches the array in the verbatim round-1 record, including whitespace and final newline: **6,638 bytes**, SHA-256:

```text
10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1
```

All six construction functions (`harness/cells.py:287–321`) remain source-identical to their first implementation and implement the unchanged construction strings. None was built.

**Verdict: `freezable as written`.**
````

### Disposition

No finding. The round closed all three round-8 findings and returned `freezable as written`.

### The freeze

The freeze is the squash-merge of the pull request this record names below. Between the
reviewed commit `3d18ede3` and the freeze commit, the study directory changes only in these
ways, none of them substantive: this round-9 section is added to `PREREG-REVIEW.md`; the
status lines of `PREREGISTRATION.md` and `README.md` say frozen instead of draft; the freeze
pins in `harness/PINS.json` are filled with the digests of `PREREGISTRATION.md`,
`harness/MATRIX.json`, `harness/MATRIX-HOLDOUT.json`, `adapter/SPEC.md` and the regenerated
`harness/STUDY-MANIFEST.sha256`; and the two repository indexes gain a row for this study.
`harness/MATRIX-HOLDOUT.json` is byte for byte the reviewer's round-1 array (SHA-256
`10f87d02a06cb91e32ab47c9477331c90068b49dcc33711cea8a276ae951b9f1`). No holdout cell has been
built through the harness; the registered attempt will be their first construction through
it (§1a of the preregistration discloses the adapter-layer pretesting of `h01`, `h02` and
`h06`).

Pull request: see the final line of this file.

