# Post-run adversarial review

**Verdict: accept with corrections.** The registered result stands; all ten
corrections to how it was reported were applied exactly as specified.

This is a separate file because `PREREG-REVIEW.md` is a **locked input** —
the pre-freeze reviews are part of what the protocol lock pins, and
appending to it after the lock is exactly the drift the lock exists to
refuse (see `DEVIATIONS.md` §2, where trying it is recorded).

Review basis: the study as run and scored, commit `1577071`.

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-06.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-06. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing the POST-RUN adversarial review of Study 010, which has now been locked, run, and scored. You reviewed its preregistration five times (all five verdicts: redesign); those reviews and their dispositions are in studies/010-blinded-oracle/PREREG-REVIEW.md. The maintainer accepted your findings across revisions 2-6, then locked and executed against the ceiling stated in PREREGISTRATION.md §9 rather than continuing to harden.

This review is NOT about whether the protocol could have been stronger — that argument is recorded and closed. It is about whether the REPORTED RESULT is supported by the RETAINED EVIDENCE.

Read, in studies/010-blinded-oracle/:
- ANALYSIS.md (the claims under review), RESULTS.json, README.md
- DEVIATIONS.md (especially §1, the pilot disclosure)
- PREREGISTRATION.md (what was registered) and PREREG-REVIEW.md
- PROTOCOL-LOCK.json, FREEZE.json, DRAW.json, DEFECT.json
- transcription/authoring/call-1/ (CALL.json, session.jsonl, completion.txt, context.json), transcription/GOLDEN-CONTEXT.json, transcription/witness/
- records/, RECORDS.md, packs/, trials/ATTEMPT-1/
- pilots/ (the two disclosed pilot samples)
- harness/ (the locked code that produced all of it)

Verify, independently and from the bytes:

1. **Is E1 = caught actually entailed?** Re-derive it. Does levant-medical-data pass under C and mismatch under D? Is it genuinely in H (policy-concordant) and in F (the sampled predicate)? Could the label be an artifact of the tables rather than the evaluator's real dispositions?
2. **Is the coverage profile (6/6) correct?** Recompute each class from the record bytes and the family predicates. Are any of the "covered" cells wrong, double-counted, or dependent on a predicate that does not mean what ANALYSIS.md says it means?
3. **Is the selection chain re-verifiable?** Check the lock inclusion, the records inclusion, the SET signatures, the round arithmetic from the authenticated integratedTime, the dual-relay agreement, and the index recomputation. Does the published-before-the-round claim hold from the retained bytes alone?
4. **Is the ordering claim true in the commit graph?** lock -> lock timestamp -> authoring -> records commit -> publication -> round -> draw -> freeze -> run. Any commit out of order, or any artifact whose content predates what it claims to follow?
5. **Does the authoring evidence support the authorship claim?** Read session.jsonl. Any tool use? Does the pre-prompt context match GOLDEN-CONTEXT.json? Is the completion the last assistant message? Does anything in the transcript suggest the model knew about the pack, the family, or the defect?
6. **Does ANALYSIS.md overclaim anywhere?** This is the core question. Check every sentence against the evidence. In particular: is the "not a rate / not real records / not blinding proof / E1 confirmatory" section adequate, or does some claim elsewhere in the document quietly exceed it? Is the DEVIATIONS §1 disclosure sufficient, or does the pilot foreknowledge damage something the analysis does not acknowledge?
7. **Anything the run itself revealed** that the analysis should report and does not — a suspicious artifact, an unexplained value, a check that passed vacuously.

For each finding: number, severity (blocker / material / minor), the exact file and text, what is wrong, and the minimal correction to the reported claims. A "blocker" here means the reported result is not supported and must be retracted or restated, not that the protocol could have been better.

End with a verdict: "accept as reported", "accept with corrections" (list them exactly), or "retract". The maintainer will apply your corrections to ANALYSIS.md and record this review verbatim before merging.
```

## Complete output (unedited)

No blocker. The retained bytes support `E1 = caught` and the registered 6/6 coverage profile. The result should not be retracted, but several interpretations in `ANALYSIS.md` require correction.

## Independent re-derivation

`levant-medical-data` has `sanctionsHit:false`, country `SY`, score `88.75`, and recorded outcome `reject`.

- It is in H: POLICY P2 requires `reject`.
- It is in F: sampled predicate 4 is exactly `sanctionsHit:false ∧ country=SY`.
- Under C, P2 contains `["KP","IR","SY"]`, so the evaluator returns `reject`.
- Under D, P2 contains only `["KP","IR"]`; P3–P5 still exclude SY, so no rule matches.

This is not merely a `DEFECT.json` table artifact. The retained v0.15.0 run output shows:

- D: actual `unresolved/no-match`, expected `reject`, status `mismatch` (`trials/ATTEMPT-1/runs.json:491-499`).
- C: actual and expected `reject`, status `passed` (`runs.json:806-813`).
- MCP C independently carries the same disposition (`runs.json:1061-1068`).
- Circular D also records `unresolved/no-match`.

The trial’s 54-file seal and all hashes verify; its C/D project packs equal the frozen pack hashes.

The independently recomputed registered coverage is:

| Index | H records satisfying the exact predicate |
|---|---|
| 0 | `alpine-benefits-platform`, `solstice-industrial-parts` |
| 1 | `alpine-benefits-platform`, `solstice-industrial-parts` |
| 2 | `iberia-payroll-support`, `lumen-customer-systems` |
| 3 | `blue-harbor-logistics`, `iberia-payroll-support`, `lumen-customer-systems`, `maple-records-processing` |
| 4 | `levant-medical-data` |
| 5 | `cedar-analytics` |

All 16 records are policy-concordant: H=16, Q=0. The classes overlap—0 and 1 have identical members here, and index-2 members also occur in index 3—but coverage was registered as non-emptiness per predicate, not six disjoint record sets. Thus 6/6 and counts `(2,2,2,4,1,1)` are correct.

The selection chain also verifies independently:

- Both witness signatures and Rekor SET signatures verify.
- Lock SET: `integratedTime=1786014352`, binding `f285fad…`.
- Records SET: `integratedTime=1786014431`, binding `0739fab…`.
- `T=1786014731`; round 6352790 is scheduled at 1786014720 and round 6352791 at 1786014750, so 6352791 is the first eligible round.
- Both retained relay responses contain the same signature and previous signature.
- The BLS signature verifies under the locked drand public key.
- `sha256(signature)=ef317786…`; the exact preimage hashes to `3a89b1ff…`; modulo six is 4.
- The commit graph is correctly ordered through lock, timestamp, records, publication, draw, freeze, and run. The authoring transcript’s clock falls between lock and records but remains self-reported, as §9 discloses.

The registered authoring transcript has no tool/call item, one assistant answer after the exact prompt, byte-identical `completion.txt`, matching model/cwd turn context, and a normalized pre-prompt message sequence matching `context.json` and `GOLDEN-CONTEXT.json`.

## Findings

1. **Material — the purported three-sample series is neither fully retained nor shown to be exhaustive.**

   **At fault:** `ANALYSIS.md:36-40`, “Across three independent samples of the same prompt … coverage was 6/6 every time”; `DEVIATIONS.md:12-15`, “twice … Both are retained in full.”

   Each pilot retains only `completion.txt` and derived records—no `CALL.json`, transcript, context, stdout/stderr, or model/prompt binding. Their bytes do recompute to H=16 and `(1,2,1,5,1,1)`, but independence and provenance are operator-reported.

   Moreover, `PREREGISTRATION.md:168-172`, `GOLDEN-CONTEXT.json:25`, and `PREREG-REVIEW.md:951-952,1227` document real captures of the exact registered invocation. Their source sessions are absent and are not identified with `dry7`/`dry8`; the evidence therefore does not establish that the three retained outputs were the exhaustive sample series.

   **Minimal correction:** Replace the claim with:

   > The registered transcript-bound output was 6/6. Two additional retained completion datasets, identified by the operator as same-prompt/model pilots, also recompute to 6/6 with counts `(1,2,1,5,1,1)`. Their invocation provenance, independence, and exhaustiveness are not transcript-verifiable.

   Amend `DEVIATIONS.md` to inventory every exact-prompt capture, whether assistant output began or was seen, and replace “retained in full” with an exact list of retained files. Until then, withdraw “every time” and “three independent samples.”

2. **Material — the 39–40 novelty interpretation is false or materially misleading.**

   **At fault:** `ANALYSIS.md:22`, “a band the policy never names”; lines 28–31, “Nothing in the text points at 39–40”; lines 127–130, “a boundary the policy never names.”

   The prompt expressly requests “borderline cases,” and P4/P5 repeatedly name 40, including “handles personal data clears only below 40.” Cedar is `39.99`, an obvious just-below-40 case. Both pilot index-5 records are also exactly `39.99`.

   Only the mutant’s new lower endpoint 39 is unnamed. The record’s presence is directly cued by the named 40 boundary.

   **Minimal correction:** Replace the interpretation with:

   > Index 5 moves the clearance cutoff to the otherwise unnamed value 39. Cedar’s 39.99 record is a directly prompted just-below-40 borderline case; it validly covers the registered mutation, but its presence is not evidence that the author independently targeted an un-signposted region.

   Change the conclusion to “including a mutation introducing a threshold the policy does not name.” Remove the unmeasured claim that KP or IR was “more salient” than SY.

3. **Material — the authorship paragraph exceeds and partly contradicts the transcript.**

   **At fault:** `ANALYSIS.md:11-13`, “from the policy prose alone, with no knowledge of the pack”; lines 61–62, “someone who had never heard of the pack.”

   `PROMPT.txt:22-25`, reproduced verbatim in the transcript, says “Synthetic policy for Study 010” and “a divergence between a pack and this text is a pack bug.” The model did not see either pack’s bytes, `FAMILY.json`, or the sampled defect, but it explicitly knew that a pack and pack-bug comparison existed.

   Also, the evidence is one operator-retained Codex transcript whose turn context names `gpt-5.6-sol`, not provider-signed authorship proof. The Golden comparison covers normalized `response_item` messages; it does not hash `session_meta` or `world_state`. Those ignored retained fields appear benign.

   **Minimal correction:** Use:

   > Sixteen records from one operator-retained Codex transcript naming `gpt-5.6-sol`, with no tool-use events and exact completion binding, generated without access to either pack’s bytes, `FAMILY.json`, or the sampled mutation. The prompt itself disclosed the Study 010/pack-bug framing.

   Replace “never heard of the pack” with “had not seen the pack bytes.”

4. **Material — after registered 6/6 coverage, the beacon selected the exemplar, not caught versus miss.**

   **At fault by omission:** `ANALYSIS.md:42-47,70-90,111-113`, especially “E1 was confirmatory … `caught` was the expected result.”

   Once the registered records were fixed, every possible family index had an H record. Conditional on pipeline validity and E2 behaving as registered, the beacon could no longer produce `coverage-miss` or `authoring-label-failure`; it selected which already-covered defect demonstrated the catch.

   **Minimal correction:** Add:

   > Because every family predicate already contained an H record, once the registered records were fixed the beacon no longer selected caught versus coverage-miss; conditional on pipeline validity, it selected the defect exemplar. The pilots made caught anticipated, and the registered 6/6 profile then made it entailed for every possible index.

5. **Minor — the coverage table misdescribes two predicates and calls all six “boundary classes.”**

   **At fault:** heading `ANALYSIS.md:9`; table lines 20–21.

   Index 3 permits either personal-data value; its count of four includes `blue-harbor-logistics` with `handlesPersonalData:false`. Index 4 additionally requires no sanctions hit; there are two SY records, but only Levant satisfies the full predicate. The family also includes a boolean flip and membership literal, not only boundaries.

   **Minimal correction:** Use “all six precommitted affected classes.” Change row 3 to “no sanctions hit, non-embargoed, 40 ≤ risk < 70, either personal-data value,” and row 4 to “no sanctions hit and registered in SY.”

6. **Minor — E5 was not literal byte-for-byte equality.**

   **At fault:** `ANALYSIS.md:67`, “CLI and MCP surfaces agreed byte for byte.”

   The complete payloads differ in `command`: `packs test` versus `mcp experimental_test_packs`. E5 removes that registered surface-specific field before comparing.

   **Minimal correction:** “The CLI and MCP payloads agreed after removal of the preregistered surface-specific `command` field.”

7. **Minor — selection prose attributes or proves slightly too much.**

   **At fault:** `ANALYSIS.md:74-76`, “that entry’s tree carries…”; lines 84–90, “two independent relays” and “before the randomness … existed.”

   Rekor binds a manifest naming the Git commit; the Git commit’s tree carries the locked files. The bytes prove two registered URL-labelled responses agree and that the authentic round signature verifies, but do not authenticate relay organizational independence. Literal pre-round non-existence uses the ordinary drand threshold-beacon assumption.

   **Minimal correction:** Say:

   > The authenticated Rekor entry binds commit `f285fad…`, whose Git tree carries the exact lock and locked inputs. The retained responses for the two registered relay endpoints carry identical signature and previous-signature values, and the signature verifies under the locked drand key. The records were logged 319 seconds before the selected round’s scheduled release.

8. **Minor — retained Git history does not establish the claimed final-file creation order.**

   **At fault:** `ANALYSIS.md:3`, “Written after `RESULTS.json`”; `README.md:26-32`, saying the commit graph shows attempts → results → analysis.

   The attempt, `RESULTS.json`, and `ANALYSIS.md` were introduced together in commit `1577071`; Git cannot establish their internal write order. No commit is out of sequence, but this finer chronology is merely asserted.

   **Minimal correction:** “Committed with `RESULTS.json`; all reported values recompute from the retained artifacts.” Make the same distinction in `README.md`.

9. **Minor — README miscounts the preregistration reviews.**

   **At fault:** `README.md:5-6`, “four adversarial pre-freeze reviews.”

   `PREREG-REVIEW.md` contains five reviews, all redesign.

   **Minimal correction:** Change “four” to “five.”

10. **Minor — the production-distribution statement is unsupported speculation.**

   **At fault:** `ANALYSIS.md:102-103`, “The honest expectation is that production files cluster in the easy middle.”

   The study contains no production records or distribution evidence.

   **Minimal correction:** “The production distribution is unknown and untested here; it may differ substantially from deliberately authored synthetic files.”

## Verdict

**accept with corrections** — apply findings 1–10 exactly as specified. The registered `E1 = caught`, H=16/Q=0, 6/6 coverage profile, sampled index 4, selection authentication, and commit ordering stand; the three-sample, novelty, absolute authorship, and beacon-interpretation claims must be restated.
2026-08-06T11:32:20.535200Z ERROR codex_core::session: failed to record rollout items: thread 019fd6c8-3dc6-7851-b0e0-aeab1fbd34c1 not found
2026-08-06T11:32:20.535404Z ERROR codex_core::session: failed to record rollout items: thread 019fd6c8-3dc6-7851-b0e0-aeab1fbd34c1 not found

## Maintainer disposition

All ten corrections applied verbatim; none contested. The review
independently re-derived `E1 = caught` from the run's own dispositions
rather than the tables, recomputed the coverage profile from the record
bytes, verified both Rekor signed entry timestamps, verified the BLS
beacon signature under the locked drand key, recomputed the round
arithmetic and the index preimage, and confirmed the commit ordering. All
of that stands as reported.

What did not stand was interpretation, and two corrections matter enough
to name here rather than bury in a table.

**The novelty claim was wrong** (finding 2). The first analysis called
39–40 "a band the policy never names" and read `cedar-analytics` as
evidence the author had independently probed an un-signposted region. But
the policy names 40 twice — including "clears only below 40" — and the
prompt expressly asks for borderline cases. Cedar sits at 39.99: a
directly prompted just-below-40 case. It validly covers the mutation; it
is not evidence of independent boundary-seeking. Only the mutant's new
endpoint 39 is unnamed, and the corrected text says exactly that.

**The beacon's role was overstated** (finding 4). Once the registered
records covered every family predicate, the draw could no longer produce
`coverage-miss` for any index. Conditional on pipeline validity it
selected which already-covered defect would demonstrate the catch — so
`caught` was not merely anticipated from the pilots, it was **entailed by
the registered profile for every possible index**. That makes the coverage
profile the finding and the draw an illustration of it.

| # | Correction | Applied |
| --- | --- | --- |
| 1 | Three-sample series not transcript-verifiable | `ANALYSIS.md` restated to the reviewer's exact wording; `DEVIATIONS.md` §1 inventories every registered-prompt capture and what each retains, withdrawing "retained in full", "every time", and "three independent samples" |
| 2 | 39–40 novelty false or misleading | Interpretation replaced verbatim; the unmeasured "more salient" claim about KP/IR removed; conclusion changed to "a mutation introducing a threshold the policy does not name" |
| 3 | Authorship paragraph exceeds the transcript | Replaced with the reviewer's wording; "never heard of the pack" → "had not seen the pack bytes"; the prompt's own Study 010 and pack-bug disclosure now stated |
| 4 | Beacon selected the exemplar, not caught-vs-miss | Added verbatim |
| 5 | Two predicates misdescribed; "boundary classes" too narrow | Table rows 3 and 4 corrected; heading changed to "affected classes" |
| 6 | E5 not literal byte equality | Restated as agreement after removal of the preregistered `command` field |
| 7 | Selection prose proves slightly too much | Replaced verbatim: Rekor binds a manifest naming the commit whose tree carries the inputs; relay organizational independence not authenticated; "319 seconds before the selected round's scheduled release" |
| 8 | Final-file creation order not established by git | "Written after RESULTS.json" → "Committed with `RESULTS.json`; every reported value recomputes from the retained artifacts", in `ANALYSIS.md` and `README.md` |
| 9 | README miscounts the reviews | Four → five reviews, six revisions |
| 10 | Production-distribution statement unsupported | Replaced with "The production distribution is unknown and untested here" |

Finding 1 also surfaced an imprecision in a **locked** file that therefore
cannot be corrected in place: `GOLDEN-CONTEXT.json`'s note and
`PREREGISTRATION.md` §4 both say the golden capture came from "two
independent real runs of the registered invocation", which reads as though
the registered prompt was used. It was not — those two captures used
trivial probe prompts. The pre-prompt context precedes the prompt and does
not depend on it, which is why it can be pinned at all, and all three
registered-prompt runs reproduced it exactly. The claim is sound; the
wording is loose. Correcting it would break the lock, so it is corrected
here and in `DEVIATIONS.md` §2 instead, which is what a frozen document
requires.
