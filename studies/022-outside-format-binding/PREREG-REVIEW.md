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

