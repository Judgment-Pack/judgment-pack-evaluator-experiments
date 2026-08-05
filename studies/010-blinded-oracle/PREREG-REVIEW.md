# Pre-freeze adversarial review — Study 010 draft

**Verdict: redesign. Nothing froze; nothing was built or run.**

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-05. One run,
reproduced unedited below; no run discarded.

## Maintainer response

All findings accepted; none contested. The redesign pillars the revision
must implement, in the reviewer's structure:

1. **An exogenous draw.** A commit hash the operator constructs is not a
   public coin — the nonce space (message, timestamp, whitespace) is a
   free re-roll. The revision needs an external randomness beacon with a
   preregistered future round, the records manifest published to an
   immutable log before it, and a retained `DRAW.json`.
2. **Two locks.** A pre-data protocol lock (prereg, policy, C, ordered
   family, prompt procedure, stdout-to-records compiler, controls, scorer)
   before any authoring; an artifact freeze after, adding only generated
   output. The current single freeze leaves the protocol editable after
   the result is knowable.
3. **A hermetic authoring call.** `codex exec` in the repository is agentic
   and not structurally blinded; the revision needs a stateless call in a
   hermetic environment with the exact prompt bytes and full transcript
   frozen — or the claim narrows to "one retained, operator-selected
   completion".
4. **A frozen stdout compiler.** Transcription and drops are an
   uncontrolled selection step (and each choice re-rolls the current
   coin); the parser, grammars, no-repair policy, and drop codes freeze
   before authoring, and validation regenerates records and drops exactly.
5. **A four-way always-scoreable primary endpoint** (caught /
   coverage-miss / authoring-label failure / pipeline-invalid), with
   schema-valid policy-wrong records kept as a separate set Q and mismatch
   sets derived from full C/D tables — E1 as drafted could not fail in the
   state where it was scoreable.
6. **A disjoint policy encoding.** P1–P5 as drafted produce Core conflicts
   (embargo × risk, personal-data × embargo); the revision registers the
   explicit disjoint decision function the reviewer wrote out, plus an
   exhaustive truth-region validator.

Two of these — the beacon choice and whether a genuinely independent
executor is available — are infrastructure decisions for the maintainer,
not drafting work, which is the second reason this stops at the recorded
draft rather than a same-day revision.

## Prompt (verbatim)

````
You are performing the pre-freeze adversarial review of the Study 010 preregistration draft: studies/010-blinded-oracle/PREREGISTRATION.md in this working tree. You reviewed Study 009 through three revisions (studies/009-transcribed-oracle-matrix/PREREG-REVIEW.md and ADVERSARIAL-REVIEW.md — read them; 010 incorporates 009's repaired mechanics by reference). Your one job: find the ways this study could produce a meaningful-looking result that is not — this time with special attention to the two NEW mechanisms: (a) the blinding scheme (different-vendor record authorship from the policy text alone, prompt registered verbatim) and (b) the public-coin mutation selection (family committed before records; applied mutation = sha256(records commit) mod 6 after records lock).

Press hardest on:
1. The coin: can the pack author influence which mutation is sampled (by choosing WHEN to commit records, by re-running the record authoring, by transcription choices that change the commit hash, by the family's ordering)? The records-locking commit is made by the same operator who knows the family — is "one commit containing only records/ and RECORDS.md" enough, or does the scheme need a commitment to the transcription procedure too? Is mod-6 on a hash the operator constructs actually a public coin?
2. The blinding: the prompt contains the full policy — a diligent model will probe stated boundaries (70, 40, the embargo list), so most family members sit exactly where records cluster. Does that make E1 nearly certain to catch, quietly collapsing back toward entailment? Which family members could realistically be missed? Is the family diverse enough for a miss to be informative rather than an artifact of one weird mutation? Conversely: can the transcription/drop step (records failing the schema are dropped) be used to prune exactly the records that would catch the sampled defect?
3. E1's scoreability: "only scoreable when F ≠ ∅" — who decides F? (the sampled predicate over records — mechanical, good — but check the two-sided risk: predicate satisfied by a record whose recorded outcome is WRONG under the policy; Codex may author inconsistent records; does a wrong-outcome record in F break E2's table conformance and therefore void the run rather than measure anything?) What is the registered handling of Codex records whose outcome disagrees with the policy — dropped? kept as accidental controls? This seems underspecified.
4. The richer policy: are P1-P5 as stated actually decidable and non-overlapping (P3 vs P4 both fire at risk 80 + personal data → same outcome, fine; P1 vs P2 both reject, fine)? Any case where two clauses give DIFFERENT outcomes (conflict) or none applies? The pack must encode mutually exclusive rules — is that achievable for this policy without a fallback?
5. Everything you'd check anyway: freeze coverage of the new pieces (FAMILY.json, the authoring transcript), the appended-controls mechanism, E3's descriptive profile (post-hoc rationalization risk), incorporation-by-reference soundness.

Output: numbered findings with severity (blocking / should-fix / nit / observation), section, concrete failure scenario, fix. State what survived. End with a verdict: freeze as-is, freeze with named changes, or redesign.
````

## Complete output (unedited)

Review corpus: [Study 010 draft](studies/010-blinded-oracle/PREREGISTRATION.md:1), [Study 009 third revision](studies/009-transcribed-oracle-matrix/PREREGISTRATION.md:1), [pre-freeze reviews](studies/009-transcribed-oracle-matrix/PREREG-REVIEW.md:1), [post-run review](studies/009-transcribed-oracle-matrix/ADVERSARIAL-REVIEW.md:1), and [deviations](studies/009-transcribed-oracle-matrix/DEVIATIONS.md:1).

1. **Blocking — §§1, 3.4, 5: the records commit is not a public coin.**

   **Concrete failure scenario:** After seeing the records and their six-member coverage profile, the operator creates otherwise equivalent Git commits while varying the commit message, timestamp/timezone, signature, parent metadata, JSON whitespace, file modes, or `RECORDS.md` formatting. Each changes the commit OID. Selecting any desired residue takes six candidates on average; only the winning history need survive. Waiting another second before committing is itself another draw. “One commit containing only `records/` and `RECORDS.md`” constrains the visible diff, not the commit-object nonce space. Hashing that operator-made OID with SHA-256 adds no independent entropy.

   **Fix:** Publish one canonical Codex-record manifest to an externally immutable log before a preregistered future randomness-beacon round. Fix the publication deadline, exact beacon round, late/missing-beacon rule, byte encoding, and selection procedure in advance. Use the record root and family digest only as binding salts. Retain a `DRAW.json` containing the commitment, beacon output/proof, family digest, selected index, and all recomputation inputs. A privately constructed Git hash may remain an identifier, but not the entropy source.

2. **Blocking — header and §5: the protocol remains editable after the result becomes knowable.**

   **Concrete failure scenario:** The header says DRAFT until the final freeze, but step 5 freezes only after the model output, transcription/drops, sampled mutation, D, and `DEFECT.json` exist. The endpoint, drop rule, family interpretation, or E3 language could be revised in response and still become the final “frozen” preregistration. A docs-only commit in step 1 is not stated to be immutable.

   **Fix:** Introduce two locks. The pre-data protocol lock must include the reviewed preregistration, policy, C, exact ordered family, expanded-prompt procedure, call contract, parser/drop algorithm, controls, reference semantics, and scorer before authoring begins. Any subsequent change invalidates that authoring attempt. A later artifact freeze may add only mechanically generated output, records, D, tables, configurations, and digests.

3. **Blocking — §§1–2, 5: “one run; no run discarded” and the claimed chronology are promises, not structural controls.**

   **Concrete failure scenario:** The operator can make several off-ledger Codex calls, inspect each completion’s family-wide coverage, and retain the preferred one. They can also author records first and later manufacture a local Git ancestry showing family → transcript → records. The final repository proves that one selected transcript was retained, not that it was the first call or that the family preceded every candidate output.

   **Fix:** Externally publish the pre-data anchor, then use an independent executor or provider-audited wrapper that binds the first registered request to its response. Retain every attempt and failure, with provider request ID, timestamps, exit state, and a content-independent retry rule registered beforehand. If this cannot be externally witnessed, narrow the claim to “one retained, operator-selected completion” and stop calling the ordering structural.

4. **Blocking — §§1–2, 6: `codex exec` is not structurally blinded by a policy-only user prompt.**

   **Concrete failure scenario:** `codex exec` is agentic. If launched inside the repository after C and `FAMILY.json` exist, it may read them through workspace tools, inherited instructions, or MCPs even though the user prompt contains only policy text. Retaining stdout does not reveal all system/developer context or tool activity.

   **Fix:** Use a stateless call or hermetic environment exposing only the exact registered prompt bytes. Disable repository access, tools, MCP, network, prior conversation, and unrelated instructions. Freeze exact model/CLI identity, argv, cwd, environment, sandbox roots, instruction context, full JSONL event transcript, stdout/stderr, exit status, and provider request ID.

5. **Blocking — §§3.5, 5.3: the raw-output-to-records transformation is an uncontrolled selection step.**

   **Concrete failure scenario:** The response contains the only risk-70 case as `"70.0"`, a duplicate ID, or one member needing trivial extraction from fenced JSON. “Transcription” leaves the operator free to repair, normalize, omit, or drop it while retaining other cases. `RECORDS.md` can accurately report the chosen drop without proving that the choice followed a registered procedure. These choices also redraw the current coin.

   **Fix:** Before authoring, freeze an executable stdout-to-records compiler and closed contract: single-array parsing, duplicate-key/ID handling, exact ID/timestamp/decimal grammars, member ordering, no-repair policy, filenames, canonical serialization, whole-response failure behavior, and stable drop codes. Retain raw bytes and an index-by-index manifest mapping every source element to an accepted file or rejection. Validation must regenerate both retained records and drops exactly. One records commit alone is not enough; the transcription procedure must be committed first.

6. **Blocking — §§1, 4: E1 cannot fail in the state where it is declared scoreable.**

   **Concrete failure scenario:** If a family predicate denotes the exact C→D semantic delta and an F record’s outcome is policy-correct, then `F ≠ ∅`, table conformance, and wrapper binding mechanically entail a B/D mismatch. Yet when `F = ∅`—the substantive miss—the draft calls E1 unscoreable. Thus the only uncertain quantity is eligible record coverage, while every scoreable E1 is a catch. “E1 is not entailed by anything” is false conditionally.

   **Fix:** Make the primary endpoint always scoreable. For example:

   - `caught`: at least one Codex-authored, non-K record satisfies the sampled semantic predicate, passes under C, and mismatches under D;
   - `coverage-miss`: no eligible C-concordant Codex record intersects the predicate;
   - `authoring-label failure`: facts intersect, but no intersecting record passes under C;
   - `pipeline-invalid`: a gate, table, refusal, or completeness prerequisite fails.

   The D mismatch is confirmatory machinery. The empirical uncertainty is usable record coverage.

7. **Blocking — §§3.5, 4: schema-valid policy-wrong Codex outcomes have no registered handling.**

   **Concrete failure scenario:** For a P3 `>=`→`>` mutation, Codex produces an otherwise affected risk-70 record but labels it `clear`. D may match that wrong record while C mismatches it: F is nonempty, E1 misses, and the promised C mismatch set gains a non-K row. If Codex labels it `reject`, D can mismatch and E1 can claim a “catch” caused entirely by record error. Actual C/D dispositions may still conform to their tables; it is the claimed mismatch sets and oracle interpretation that break.

   **Fix:** Keep schema-valid semantic errors as data in a separate authoring-error set Q; do not silently drop them. Operationally require a catch row to pass under C and mismatch under D. Generate full C/D tables for every retained record, but derive mismatch sets from those tables and recorded outcomes rather than hard-coding C = K and D = F ∪ K. Report raw predicate coverage, C-concordant coverage, and Q separately.

8. **Blocking — §3.1: P1–P5 do not presently define one Core disposition.**

   **Concrete failure scenario:** With no sanctions hit, an embargoed country, and risk 80, P2 says `reject` while P3 says `manual-review`; with personal data P4 also fires. At risk 40–69.99 with personal data, P2 and P4 conflict. Core evaluates every true rule, provides no array-order priority, and returns `unresolved/conflict` when distinct outcomes are nominated.

   P1/P2 overlap survives because both say `reject`; P3/P4 overlap survives because both say `manual-review`. The cross-outcome P2 overlaps do not.

   **Fix:** Register an explicit decision function. One strictly disjoint form is:

   - P1: `S` → reject.
   - P2: `!S && E` → reject.
   - P3: `!S && !E && r >= 70` → manual review.
   - P4: `!S && !E && personal && 40 <= r < 70` → manual review.
   - P5: `!S && !E && r < 70 && (!personal || r < 40)` → clear.

   Alternatively use a genuine `fallbackOutcome: clear` after disjoint reject/review conditions. Freeze an exhaustive truth-region validator. Also require canonical country codes and exact case-sensitive embargo membership.

9. **Blocking — §§1, 3.3, 6–7: the family cannot yet support the claimed interpretation, and the prompt nearly targets it.**

   **Concrete failure scenario:** The exact family is absent, so mutation directions, threshold replacement values, membership literals, masking, and predicate breadth cannot be reviewed. Meanwhile “include the borderline cases” is itself a boundary hint; the inserted policy names 70, 40, the embargo list, and the booleans. Exact-70/exact-40 mutations and clause/boolean mutations are therefore likely covered by construction.

   Realistic misses are concentrated in qualitatively different members: a mutation to one embargo-list member the 16 cases omit; a threshold-value change whose affected interval lies away from the named boundary; or a nominal P3 boundary case masked because P4 still yields manual review. A sampled miss may therefore mean “one narrow or masked mutation was odd,” not a general boundary-coverage gap.

   **Fix:** Put final C and exact `FAMILY.json` through adversarial review before authoring. Require each predicate to equal the complete semantic C→D disposition-difference set, including masking and conflict/no-match states. Call these “six selected mutations,” unless every comparison site is actually represented. Reframe the estimand as coverage from one boundary-seeking synthetic-fixture prompt, or add a separately preregistered neutral/naturalistic record arm. Remove the analogy to ordinary organizational case files.

10. **Blocking — §§3.5, 4–5: appended K controls have no coherent provenance or gate path.**

   **Concrete failure scenario:** If K is appended after Study 009’s complete-row gate, it bypasses P-ACQ/P-GATE. If added to `records/`, it changes the locked record set and coin input. If chosen after the draw, its facts can overlap F or be accidentally corrected by D. A Codex-authored `k-` ID can also collide with the reserved control namespace.

   **Fix:** Precommit exact controls—or a deterministic generator—with the family in a separate `controls/` namespace. Route K through the same acquisition and complete-row gate. Require K to lie outside every family predicate, require `C == Dᵢ` on K for all six mutations, and require its recorded outcome to be wrong under all of them. Exclude controls mechanically from the Codex record commitment, F, E1, and E3; reserve the prefix in the Codex schema.

11. **Blocking — §§3.4, 4: expected-disposition generation is not a registered independent algorithm.**

   **Concrete failure scenario:** After selecting D, the harness can populate `DEFECT.json` tables by querying the same jpack runtime later scored by E2, making table conformance a replay. Alternatively, the operator can hand-author tables after seeing unexpected conflicts. “Derived per Study 009’s provenance discipline” does not choose between these. It also conflicts with the incorporated rule that C, D, and real study records are not evaluated before freeze.

   **Fix:** Prelock an independent policy/reference-semantics implementation capable of deriving C and every Dᵢ disposition from facts, or include exact semantic disposition functions in the family entries. Mechanically generate the record-specific tables from that frozen reference without invoking the scored runtime. If runtime probes are used instead, retain them and label E2 evaluator self-consistency rather than external table conformance.

12. **Blocking — §3 and freeze mechanics: incorporation by reference is neither closed nor version-pinned.**

   **Concrete failure scenario:** “Third revision verbatim, as repaired through DEVIATIONS §2” points to conflicting authorities. Study 009 §10 says the first started attempt is primary with no retry; its deviations/final harness select the first `DONE` attempt under the corrected freeze. Study 009 assumes policy-correct H/F records and exactly three F records, while Study 010 permits empty F and leaves Codex outcome errors unresolved. Study 010 also repurposes E3. A future scorer can choose whichever inherited interpretation fits.

   Study 009’s explicit freeze list also does not automatically cover `FAMILY.json`, exact rendered prompt, invocation transcript, raw output, parser, drop manifest, control artifacts, record-lock identity, or draw proof.

   **Fix:** Pin exact reused code blobs and digests, not “repaired through” prose. Restate a complete Study 010 ledger, validation contract, retry rule, endpoint definitions, and closed delta table locally. Explicitly add every new artifact above, plus the pre-data anchor and external draw proof, to `FREEZE.json`.

13. **Should-fix — E3: “would have caught” is underspecified and can rescue the sampled result post hoc.**

   **Concrete failure scenario:** E3 can count raw predicate matches, accepted matches, family members with any match, or policy-concordant paired C/D detections; these differ when records are dropped or outcomes are wrong. After a sampled miss, “five of six would have caught” can become a favorable sensitivity narrative over a heterogeneous, hand-picked family despite the no-rate bound.

   **Fix:** Freeze a six-row reporting schema. For each stable family ID report: raw-output predicate matches, accepted Codex-only matches, C-concordant matches, paired C-pass/Dᵢ-mismatch IDs, and attrition/error counts. Exclude K. Report the vector descriptively without treating `x/6` as a rate or allowing E3 to rescue E1.

14. **Should-fix / nit — §3.4: selection encoding and family indexing are ambiguous.**

   **Concrete failure scenario:** The draft does not say whether `sha256(records_commit_hash_hex)` hashes lowercase ASCII, decoded OID bytes, or command output with a newline; nor whether residue indexes source-array order, sorted IDs, or object iteration order. Different conforming implementations can select different mutations.

   **Fix:** Give every family member an immutable `selectionIndex` 0–5 and stable ID; require exact contiguous indices and unique patches. Specify domain-separated input bytes, Git object format, casing, endianness, and recomputation. `2^256 mod 6 = 4`, so raw modulo has a negligible bias; rejection sampling can remove it, but operator control of the input is the real defect.

### What survived

- Family-before-records, records-before-draw is the correct causal skeleton once both locks are externally anchored and the draw is exogenous.
- Evaluator-independent semantic predicates are much better than classifying defect rows from observed evaluator mismatches.
- A genuinely hermetic different-vendor, policy-only call would create useful separation from exact pack authorship.
- Study 009’s repaired artifact↔record equality, fixed projection, complete-row gate, paired byte-identical C/D matrix, full-disposition checks, and sealed attempt ledger remain strong mechanics when explicitly ported.
- P1/P2 and P3/P4 same-outcome overlaps are compatible, and the richer policy can be made exhaustive without a fallback if its complements are encoded explicitly.
- Separate synthetic K controls remain sound carrier calibration once precommitted, disjoint, and gate-admitted.
- The one-family/no-rate and byte-lineage-not-truth bounds are directionally honest.
- Once an independent uniform draw and immutable index mapping exist, family ordering itself does not bias selection.

**Verdict: redesign.** Do not freeze this draft. The present “coin” is an operator-grindable commit hash, the model call is neither structurally blind nor first-call verifiable, and the only uncertain quantity is not represented by an always-scoreable endpoint. Replace the coin with externally unpredictable entropy, create a true pre-data protocol lock and witnessed hermetic authoring call, freeze deterministic transcription, repair the policy and family predicates, and redefine E1 around Codex-only C-concordant coverage. Only after those changes—and a second review of the exact C/FAMILY/parser/control artifacts—would the Study 009 mechanics be safe to freeze.
