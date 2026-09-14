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

