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

---

# Pre-freeze adversarial review — revision 2

**Verdict: redesign. Nothing froze; revision 3 implements every finding and
is reviewed together with the complete protocol-lock candidate.**

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-05. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing an adversarial pre-freeze review of a REVISED study preregistration. You previously reviewed the first draft and returned verdict "redesign". The maintainer accepted all findings and rewrote the design. Your job now: check the revision actually closes each hole, and hunt for new ones.

Read these files:
- studies/010-blinded-oracle/PREREGISTRATION.md — the revision under review (revision 2)
- studies/010-blinded-oracle/PREREG-REVIEW.md — your prior review of the superseded draft, plus the maintainer's response listing six redesign pillars
- studies/009-transcribed-oracle-matrix/PREREGISTRATION.md — the predecessor study whose machinery (gates, freeze, ledger, scorer) revision 2 inherits "verbatim"
- studies/009-transcribed-oracle-matrix/DEVIATIONS.md — the hardening the inherited machinery received
- studies/009-transcribed-oracle-matrix/harness/study.py, harness/gate.py — the inherited implementation

Context the maintainer fixed by decision (do not relitigate the choices themselves, but DO attack their execution):
1. Randomness beacon = drand (League of Entropy), default chain, 30s period. The draw rule and proof retention are in §5.
2. Authoring executor = same-machine codex CLI, narrowed claim: "one retained completion whose transcript shows no tool use", full session transcript retained, no-retry rule. §1 and §4 state the narrowing explicitly.

Attack surfaces to probe, at minimum:
- §5 draw: is the target-round rule actually operator-unsteerable? Is any residual choice left (e.g., WHEN to push, WHICH commit counts, what happens if the API's committer.date disagrees with git's, leap seconds, round already elapsed at push+300s)? Is the index formula well-defined (byte-level: what exactly is hashed)? Is the proof material sufficient for third-party verification without trusting the operator?
- §2/§3: is the P1-P5 encoding really disjoint and total (24 regions)? Do the six mutation predicates actually characterize the affected classes correctly, including mutation 3's conflict semantics and mutation 5's interaction with P4 (39<=r<40 records: P4 does not match them since r<40; what does D actually do)? Is any predicate wrong or evaluator-dependent?
- §4 compiler: is "first [ to its matching ]" well-defined against adversarial or malformed output? Are the drop codes exhaustive? Can the no-repair rule be violated silently? Is the retained-raw-stdout byte-equality check sufficient?
- §6 E1: is the four-way endpoint really total (every execution path lands in exactly one)? Note "authoring-label-failure" overlaps "coverage-miss" as written (both have H∩F=∅) — is the precedence stated? Are Q and K handled coherently in the tables and mismatch sets?
- §8 ordering: can the operator peek (e.g., generate D before the draw, run records through C before publication, choose among transcripts)? Which of these does the protocol actually PREVENT vs merely record? Is the prereg honest about which is which?
- Inheritance debt: "Study 009's repaired gates verbatim" — identify anything in 009's harness that does NOT transfer cleanly to the four-fact schema (P-PNF projection, decimal mirror for the country/bool facts, record-source adapter, gate equality) and whether the prereg registers the needed deltas or hand-waves them.

For each finding: number, severity (blocker / material / minor), the exact text at fault, the failure it permits, and the minimal fix. End with a verdict: "freeze as is", "freeze with amendments" (list them), or "redesign". Be adversarial: the maintainer will freeze this document and the study's credibility rests on your review.
```

## Complete output (unedited)

# Adversarial review — revision 2

**Verdict: redesign.** Revision 2 repairs the policy logic and the six prose predicates, but the draw remains steerable, E1 is not four-way/always-scoreable, and Study 009’s implementation cannot be inherited as described.

Reviewed: [revision 2](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:1), [prior review](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREG-REVIEW.md:1), [Study 009 preregistration](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/PREREGISTRATION.md:1), [deviations](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/DEVIATIONS.md:1), [study.py](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:1), and [gate.py](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/gate.py:1).

1. **Blocker — the target round is still operator-steerable.**

   **Text at fault:** “the GitHub API’s `committer.date` … plus 300 seconds” and “Delaying the push delays the round.”

   **Failure:** `committer.date` is operator-supplied commit metadata, not GitHub’s publication time; GitHub explicitly allows callers to supply it in its [commit API](https://docs.github.com/en/enterprise-cloud%40latest/rest/git/commits). The operator can backdate a commit—or simply wait over five minutes before pushing—so the target round is already known. Holding the date fixed while varying the commit message or other metadata then grinds the commit salt until the desired index appears. This directly contradicts §1’s claim that the round had not occurred at publication.

   **Minimal fix:** Derive the target from an externally witnessed, append-only inclusion timestamp for the exact records manifest, or precommit a fixed future round and publication deadline. Fail closed if the target was available at inclusion.

2. **Blocker — no unique immutable records publication is defined.**

   **Text at fault:** “The records commit … is pushed to the public repository: the publication”; later, `DRAW.json` simply names “the records commit hash.”

   **Failure:** A Git commit object is immutable, but its ref and first-publication time are not an append-only log. No repository/ref, parent, topology, or “first qualifying commit” rule is fixed. Several commits can be pushed on different branches, allowed to acquire their beacon results, and one favorable commit later nominated in `DRAW.json`; alternatives can be force-pushed away.

   **Minimal fix:** Publish one canonical manifest digest into a designated transparency-log namespace. The first valid inclusion after the protocol lock must irrevocably bind the attempt; later candidates either are ignored or invalidate it. Retain the inclusion proof, manifest bytes, commit OID, ref, and ancestry.

3. **Material — the retained drand proof is insufficient.**

   **Text at fault:** `DRAW.json` retains “randomness,” “signature,” and “chain info (hash, genesis, period)”—said to be “everything needed.”

   **Failure:** `default` is an alias, not the cryptographic chain identity, and the default scheme is chained. Independent verification needs the pretrusted chain hash/public key, scheme, round, and `previous_signature`. Drand’s specification distinguishes the alias from the chain hash and identifies the public key, scheme, and previous signature as verification inputs. [Official drand specification](https://docs.drand.love/docs/specification/)

   **Minimal fix:** Protocol-lock the exact chain hash, public key, scheme ID, genesis, and period. Retain the raw `/info` and `/public/<round>` responses, including `previous_signature`; verify the chain-info hash, BLS signature, round, and `randomness == SHA-256(signature)` with a pinned verifier.

4. **Material — the index and round algorithms are not byte-complete.**

   **Text at fault:** `int(sha256(randomness_hex || records_commit_hash_hex || family_digest_hex), 16) mod 6`, plus “the round number is arithmetic anyone can redo.”

   **Failure:** Undefined details include:

   - the algorithm and exact source bytes of `family_digest`;
   - Git object format and OID width;
   - prefixes, separators, and field widths;
   - digest bytes versus hexdigest and integer byte order;
   - array position versus the entry whose `index` equals the residue;
   - the exact round-1/genesis formula;
   - UTC/POSIX, fractions, leap seconds, and Git/API disagreement;
   - missing, late, or invalid beacon behavior.

   Adjacent-round disagreement selects unrelated entropy.

   **Minimal fix:** Register normative pseudocode using integer POSIX seconds, fixed-width validated inputs, a version/domain tag and length prefixes, `int.from_bytes(SHA256(preimage).digest(), "big") % 6`, and selection by a unique contiguous `index` field. Define `scheduled(r)=genesis+(r-1)×period`; fetch only the fixed round, never substitute latest/next, and map a fixed retrieval-deadline failure to `pipeline-invalid`. Retain the exact preimage and digest.

5. **Blocker — E1’s four labels overlap and are not demonstrably total.**

   **Text at fault:** “coverage-miss — `H ∩ F = ∅`” and “authoring-label-failure — `H ∩ F = ∅` but `Q ∩ F ≠ ∅`.”

   **Failure:** Every authoring-label failure is simultaneously a coverage-miss. `pipeline-invalid` can also coexist with every data condition because no precedence is stated. Further, if the registered predicate is not exactly the actual C→D disposition delta, `H∩F` can be nonempty without `caught`, while neither miss label applies.

   **Minimal fix:** Define this ordered partition:

   1. Any call/compiler/beacon/prerequisite/table/semantic failure → `pipeline-invalid`, suppressing all other labels.
   2. Else `H∩F ≠ ∅` → `caught`.
   3. Else `Q∩F ≠ ∅` → `authoring-label-failure`.
   4. Else → `coverage-miss`.

   Lock assertions that accepted records equal `H ⊔ Q`, K is excluded, every H row passes under C, and predicate membership is equivalent to a full canonical C/D disposition difference.

6. **Blocker — inherited crash paths never receive an E1 value.**

   **Text at fault:** “always scoreable” and “first sealed attempt is primary.”

   **Failure:** Study 009’s runner writes `CRASHED.json` and rethrows without sealing when acquisition, transcription, gate, or evaluation fails. Its scorer then selects the first attempt reaching `DONE` under the current freeze, not the first started attempt. See [exception path](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:368) and [primary selection](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:455). Thus a failed prerequisite can be skipped and a later run made primary—the opposite of `pipeline-invalid`.

   The local “seal” is also only `chmod 0444`; the owner can remove or rewrite attempt directories and reuse their numbers.

   **Minimal fix:** The first `STARTED` attempt under the artifact freeze is primary. Every exit, including exceptions, must receive a structured terminal state, be sealed, and score as either the appropriate valid result or `pipeline-invalid`. Externally anchor the STARTED marker and terminal-manifest hash if the ledger is claimed to be append-only.

7. **Material — the compiler is not a closed deterministic transformation.**

   **Text at fault:** “first `[` to its matching `]`” and drop codes `schema`, `decimal-form`, `country-form`, `duplicate-id`, `outcome-value`.

   **Failure:** “Matching” is undefined around brackets inside strings, escapes, nested arrays, an earlier Markdown link, multiple arrays, missing closure, malformed JSON, or invalid UTF-8. There is no whole-stream result. Duplicate object keys can silently last-win; multi-defect elements have no drop-code precedence; duplicate-ID treatment is unclear when the earlier occurrence was itself rejected. “ISO 3166-1” also lacks a pinned registry snapshot. Identical stdout can therefore yield different H/Q/F.

   **Minimal fix:** Require stdout to decode as exactly one top-level array, or fully specify a JSON-aware extraction algorithm and ignored-span inventory. Reject duplicate keys; define stream-level results, drop-code precedence, duplicate-ID reservation, exact timestamp/ID grammars, a pinned country-code set, filenames, serialization, and empty/malformed-output handling. Validation must compare the complete generated file-name set and bytes, rejecting extras.

8. **Material — raw stdout is not bound to the retained completion.**

   **Text at fault:** the call retains “the full session transcript (JSONL), stdout,” while validation only regenerates from “the retained raw stdout.”

   **Failure:** The operator can retain a no-tool transcript but edit or substitute the compiler-input stdout. Regeneration will faithfully reproduce the substituted records, silently violating no-repair and the claimed provenance. Nor is absence of tool use itself declared as a mechanical prerequisite.

   **Minimal fix:** Define the exact CLI output channel used as compiler input. Validation must reconstruct the unique completed assistant message from the JSONL transcript, apply a specified UTF-8/newline transformation, and require byte equality with compiler input. It must also reject tool events, multiple completions, prompt-byte mismatch, or an inadmissible exit state as `pipeline-invalid`.

9. **Blocker — predicate/delta equality and expected tables remain circular.**

   **Text at fault:** `regions_check.py` uses “one probe per region”; after the draw the harness “derives the full C and D disposition tables … (Study 009’s provenance discipline).”

   **Failure:** One outcome probe per coarse region cannot validate exact rule structure, open/closed boundaries, every country literal, or hidden same-outcome rules. For example, an unintended P4 match at `r=70` can leave C’s outcome correct while masking mutation 0.

   More seriously, Study 009’s stated provenance was same-runtime probe evaluation, not an independent table generator; its validator never recomputes table semantics. Generating post-draw tables by querying the scored evaluator makes E2 evaluator self-replay and permits unexpected conflict/no-match behavior to be normalized into the table.

   **Minimal fix:** Protocol-lock an independent reference semantics for C and all six D variants, including exact conflict/no-match dispositions. Structurally validate C, generate tables only from that reference, and assert for every accepted/control record that predicate membership iff `table_C != table_D`. Otherwise relabel E2 as same-runtime consistency.

10. **Blocker — Study 009’s harness is incompatible with the four-fact/Q-aware design.**

   **Text at fault:** “Study 009’s repaired gates verbatim … P-PNF adjusted to the four-pointer projection … same freeze/ledger/scorer discipline.”

   **Failure:** The actual implementation hard-codes:

   - the three-field vendor schema ([lines 67–69](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:67));
   - the old two-fact F predicate and policy mirror ([line 134](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:134));
   - a disjoint, exhaustive `F/K/H` partition ([line 114](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:114));
   - D mismatches as `F∪K` and C mismatches as `K` ([line 551](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/009-transcribed-oracle-matrix/harness/study.py:551));
   - one freeze containing C, D, DEFECT and records, with no pre-data protocol lock.

   Proper four-fact records are rejected; if only the schema is loosened, embargo/personal-data verdicts are misclassified, overlapping F is rejected, Q is absent, and mismatch sets are wrong.

   **Minimal fix:** Register and review a closed Study 010 delta contract: four-fact schema/projection/mirror, accepted `H⊔Q`, overlapping sampled F, separate K, all six predicates, Q-aware dynamic mismatch derivation, four-way E1, E3, and genuine protocol-lock/artifact-freeze commands with tests.

11. **Blocker — K still has no coherent acquisition/gate path.**

   **Text at fault:** K is “two synthetic … controls the harness appends,” while the compiler emits one file per accepted record.

   **Failure:** Study 009 enumerates and serves one `records/` directory. If K remains in a protocol-locked `controls/` directory, it bypasses P-ACQ/P-GATE; if copied into `records/`, compiler regeneration and the authored-record publication become ambiguous. The model may also emit `k-wrong-1` or `k-wrong-2`, because kebab-case IDs do not reserve that namespace.

   **Minimal fix:** Keep authored records and controls in separate locked manifests; reserve the exact K IDs or a prefix with a stable compiler disposition; protocol-lock a deterministic union source adapter; and require the acquisition/reference/gate bijection across both while F/H/Q/E3 consume authored records only.

12. **Blocker — the exact protocol-lock candidate has not received this review.**

   **Text at fault:** §8 proposes locking this review together with future C, `FAMILY.json`, `PROMPT.txt`, compiler, region checker, mirror, controls, harness, and scorer.

   **Failure:** None of those Study 010 artifacts currently exists. §7 also incorporates the superseded draft’s prompt rather than presenting the current byte-exact prompt. Implementations can therefore be added after this review and frozen under its apparent approval, despite the prior review explicitly requiring review of exact C/FAMILY/parser/control bytes.

   The lock list also leaves the derivation rule, transcriber, source adapter, shared attest/derive/gate code, and pre-authoring jpack digest unclear. `PROTOCOL-LOCK.json` cannot literally digest itself, and no exact-key-set/canonical-manifest validation is specified.

   **Minimal fix:** Assemble the complete protocol-lock candidate first, then adversarially review those exact bytes. The lock must define its exact closed key set, exclude itself from its digest map while binding its committed bytes, regenerate its canonical body during validation, pin the runtime before `regions_check`, and bind the eventual artifact freeze back to the protocol-lock digest and publication proof.

13. **Material — §8 records chronology but does not prevent peeking.**

   **Text at fault:** “The harness generates D … after the round” and the authoring → publication → round → D arrow.

   **Failure:** Because C and all six patches are public, the operator can privately generate every D, evaluate records under C/all D variants, compute the complete coverage profile before publication, transiently edit and restore tools, or abandon an unfavorable attempt. None is detected by final digests. Pre-generating candidate D files does not itself steer a genuinely future beacon; the problem is that the document presents procedural order without stating its evidentiary ceiling.

   **Minimal fix:** State explicitly:

   - mechanically enforced: exact locked bytes and, once repaired, mutation selection after the first immutable records publication;
   - recorded but not proved: retained call, tool absence, and no retry;
   - not prevented: off-ledger calls, C/all-D peeks, transient edits, and selective abandonment/publication.

   Externally timestamp the protocol lock before the call if its chronology is to be stronger than operator attestation.

14. **Minor — E3 omits `Q∩F`.**

   **Text at fault:** E3 reports `|F|`, `|H∩F|`, `|Q|`, and H-only per-family coverage.

   **Failure:** `authoring-label-failure` depends on `Q∩F`, which aggregate Q does not establish.

   **Minimal fix:** Report IDs and counts for F, `H∩F`, and `Q∩F`, plus per-family H/Q intersections, always excluding K.

## What revision 2 genuinely fixes

- P1–P5 are disjoint and total over all 24 stated regions.
- All six prose predicates are correct under the stated local patches:

  - 0, 1, and 2 produce D `unresolved/no-match` on their stated classes.
  - 3 produces no-match for P=true and conflict for P=false throughout `40≤r<70`.
  - 4’s P2-only removal makes every non-sanctioned SY record no-match while the unchanged P3–P5 `¬E` guards continue excluding SY.
  - 5 produces no-match for P=true throughout `39≤r<40`; P4 does not match below 40, and the ¬P arm masks the mutation for P=false.

- Q and table-derived mismatch sets are the correct design direction.
- The narrowed “one retained completion whose transcript shows no tool use” claim is appropriately candid; the required transcript/stdout binding is an execution repair, not an objection to that chosen scope.
- Study 009’s canonical full-row gate comparison transfers cleanly once the four-pointer PNF rule and combined authored-record/control source are properly locked. The added string and boolean facts require no weakening of gate equality.

**Verdict: redesign.** Do not protocol-lock revision 2. Repair the publication clock and unique commitment, make E1 and the attempt ledger genuinely total, implement the explicit four-fact/Q/K/two-lock port, and then conduct another pre-freeze review against the complete exact protocol-lock artifact set.

## Maintainer disposition (revision 2 → revision 3)

All fourteen findings accepted; none contested. How revision 3 and the
assembled protocol-lock candidate implement each:

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | `committer.date` is operator-supplied; the round is steerable | **Accepted.** The publication clock is no longer git metadata: publication is a Sigstore Rekor `hashedrekord` inclusion over the records-commit manifest, and the round derives from Rekor's `integratedTime` (§5). Backdating is out of the operator's hands; delaying only moves the round later. |
| 2 | No unique immutable publication | **Accepted.** A fresh P-256 witness keypair is generated at lock time, the public key locked; the binding inclusion is the minimal-`logIndex` Rekor entry under that key, checked online (`witness`, retried past the log's index lag, gating the freeze) and offline from retained proof material. Any unknown entry under the key refuses the study. |
| 3 | Retained drand proof insufficient | **Accepted.** The lock pins chain hash, chain public key, scheme, genesis, period, with the raw `/info` response retained. The draw addresses both relays by chain hash — `api.drand.sh` and `drand.cloudflare.com` — requires byte-identical signatures, retains both raw responses and `previous_signature`, and recomputes `randomness = sha256(signature)`. BLS pairing verification is delegated to the external reader with all inputs retained; §9 states this ceiling explicitly. |
| 4 | Index/round algorithms not byte-complete | **Accepted.** §5 registers normative pseudocode: integer POSIX seconds, `scheduled(R) = G + (R-1)·p`, fixed-width validated preimage fields with a domain tag (`study-010-draw-v1`), `int.from_bytes(sha256(preimage).digest(), "big") mod 6`, selection by the contiguous `index` member, fixed-round-only fetch, and a 3600 s retrieval deadline mapping to `pipeline-invalid`. `validate` recomputes all of it from retained bytes. |
| 5 | E1 labels overlap; not total | **Accepted.** §6 registers the ordered partition exactly as proposed: pipeline-invalid → caught → authoring-label-failure → coverage-miss, evaluated top to bottom, one label. The scorer implements the same order and can only demote to pipeline-invalid. |
| 6 | Crashed attempts skipped; primary selection wrong | **Accepted.** The primary attempt is the first started under the current freeze, whatever its terminal state; every exit path writes a terminal state and seals (the exception path seals before re-raising); a primary without `DONE` scores E1 = `pipeline-invalid`. The seal's ceiling (tamper-evidence, not owner-proof) is stated in §6/§9 — no append-only claim is made. |
| 7 | Compiler not a closed transformation | **Accepted.** The extraction is registered normatively (§4): widest-span parseable array, ties earliest, strict decoder rejecting duplicate object keys anywhere, span offsets retained in `RECORDS.md`; drop-code precedence is the registered check order; a dropped occurrence reserves no id; the `k-` prefix is reserved (`id-form`); the country domain is registered as syntactic `[A-Z]{2}` — no registry membership is consulted, so no snapshot exists to pin; no parseable array → `pipeline-invalid`; `validate` compares the complete file-name set and bytes. |
| 8 | stdout not bound to the completion | **Accepted.** The compiler input is `completion.txt` = the transcript's last assistant message, extracted mechanically; `transcript_check.py` (locked) requires zero tool events, prompt-byte equality on the last user message, completion-byte equality, and exit 0 — violations are `pipeline-invalid` (§4). |
| 9 | Predicate/delta equality and tables circular | **Accepted.** Tables derive from the locked reference semantics only (`policy_mirror.py` + the family's registered `reasonsUnderD`) — no evaluator call in derivation; the evaluator's agreement with the tables is what E2 tests, and divergence is `pipeline-invalid`, never a table amendment. `regions_check` grows the locked boundary battery (44 probes: all 24 regions plus both-sided threshold probes at 39/39.5/40/41/69.9/70/70.5/71 × P, each embargo literal, SY high-band). The residual (a defect invisible to all 44 probes and to the byte review of pack C) is stated in §2/§9. |
| 10 | 009 harness incompatible; "verbatim" false | **Accepted.** The inheritance claim is withdrawn; §6 names the Study 010 port as its own reviewed artifact. The port exists in the candidate: four-fact schema and projection, H ⊔ Q split, overlapping F, separate K, Q-aware derived mismatch sets, four-way E1, E3 with Q∩F, and the two-lock commands, with unit tests. |
| 11 | K has no coherent acquisition path | **Accepted.** Controls live in a separate locked manifest (`controls/`); the record source serves the union of both directories deterministically (`RECORDS_DIRS`); acquisition and gate cover H ⊔ Q ⊔ K with a receipt bijection; F/H/Q/E3 consume authored records only; the compiler's `id-form` check reserves the `k-` prefix. |
| 12 | The exact lock candidate was not reviewed | **Accepted.** This disposition accompanies the assembled candidate — policy, pack C bytes, `FAMILY.json` with machine members, `PROMPT.txt` bytes (inlined in §7), compiler, checkers, controls, driver, tests — and revision 3 is submitted to a further pre-freeze review against those exact bytes before anything locks. `PROTOCOL-LOCK.json` does not digest itself; its bytes are bound by the lock commit and its key set is validated; the lock also pins the shared line code and the jpack digest, and is itself Rekor-timestamped before authoring (§8). |
| 13 | Chronology recorded, peeking not prevented | **Accepted.** §9 states the three tiers explicitly — mechanically enforced, recorded but not proven, not prevented — including private C/all-D evaluation, transient tool edits, and unpublished-attempt abandonment, and why none of them steers the sampled index after publication. |
| 14 | E3 omits Q∩F | **Accepted.** E3 reports ids and counts for F, H∩F, Q∩F and the per-family H and Q intersections, K always excluded (§6). |

Additional maintainer-initiated amendments recorded here: the extraction
rule changed from revision 2's "first `[` to its matching `]`" to the
widest-span rule (finding 7 made the first-position rule's fragility
concrete); the drop-code list gained `id-form`; the compiler input moved
from raw stdout to the transcript-bound completion (finding 8). Each is a
strictly tighter registration than revision 2's text.
