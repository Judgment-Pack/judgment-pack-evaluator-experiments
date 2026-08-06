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

---

# Pre-freeze adversarial review — revision 3 (the first complete-candidate review)

**Verdict: redesign. Nothing froze; revision 4 implements every finding.**

Review basis: commit `0c9bdaa` (the reviewer notes the candidate advanced
twice during the review window — the SEARCH-drift and relay User-Agent
fixes — and re-reviewed the final diffs; revision 4 is committed once,
before its review launches, so the basis cannot drift again).

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-05. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing the pre-freeze adversarial review of Study 010's COMPLETE protocol-lock candidate. You reviewed revision 1 (verdict: redesign) and revision 2 (verdict: redesign, 14 findings). The maintainer accepted all 14, rewrote the preregistration as revision 3, and — per your finding 12 — assembled every protocol-lock artifact so this review covers the exact bytes that would lock. Your prior reviews and the maintainer's dispositions are recorded in PREREG-REVIEW.md.

Review, in studies/010-blinded-oracle/:
- PREREGISTRATION.md (revision 3, governing)
- PREREG-REVIEW.md (both prior reviews + the 14-finding disposition table — check each disposition against the actual artifacts, not just the prose)
- policy/POLICY.md, packs/vendor-screening-correct.pack.json (pack C's exact bytes)
- FAMILY.json (six mutations: patch/predicate/reasonsUnderD are the normative members)
- transcription/PROMPT.txt, transcription/record.rule.json, transcription/transcribe.py, transcription/authoring_call.sh
- controls/k-wrong-1.json, k-wrong-2.json
- source/record_source.py
- harness/study.py (the driver: lock|timestamp-lock|publish|witness|draw|validate|freeze|run|score), harness/gate.py, harness/pnf_check.py, harness/policy_mirror.py, harness/records_compile.py, harness/regions_check.py, harness/transcript_check.py, harness/test_study.py

Also available for inheritance comparison: studies/009-transcribed-oracle-matrix/ (the predecessor whose gates the port adapts) and the shared line code at acquisition-proxy/attest.py, derivation-rule/derive.py, fabrication-gate/gate.py.

Verification context you may rely on (the maintainer rehearsed the pipeline end to end in throwaway repositories, real Rekor and real drand): lock passes with 44 agreeing probes; compile/publish/witness/draw/freeze/run/score complete; E1 produced "caught" on a covering record set and "coverage-miss" on a non-covering one; the 17 unit tests pass. Rehearsal claims are the maintainer's, not evidence — re-derive anything you rely on from the artifact bytes.

Attack surfaces, at minimum:
1. Per prior finding: check each of the 14 dispositions is actually implemented in the bytes (not just claimed). Name any that is partial or cosmetic.
2. The witness scheme: the P-256 key is generated at lock time, public key locked, private key outside the repo, publication = minimal-logIndex Rekor hashedrekord under that key over "study-010-records-commit\n<oid>\n". Can the operator still steer the draw (multiple keys? multiple inclusions the search misses? re-lock with a fresh key after seeing records? integratedTime manipulation?)? Is the freeze gate (witness SEARCH.json must show the inclusion indexed) sound?
3. The draw arithmetic in harness/study.py cmd_draw/draw_index vs PREREGISTRATION §5 — any divergence between the registered pseudocode and the implementation, byte for byte? The round formula's edge cases (integratedTime exactly on a round boundary)?
4. records_compile.py vs §4: extraction (widest span, ties earliest, duplicate-key rejection), classify precedence, k- reservation, render byte-stability, verify completeness. Any input where compile and verify disagree, or where two runs differ?
5. transcript_check.py vs §4: can a transcript with tool use pass (payload types it misses)? Can completion.txt diverge from what the compiler consumed? Is the last-user-message prompt equality check bypassable?
6. study.py's validate/freeze/run/score: does validate actually re-verify everything §5/§8 says it does? Does the primary-attempt rule match §6 (first started under current freeze, crashed → pipeline-invalid)? Is E1's ordered partition implemented in the registered order? Are the derived mismatch sets truly derived (grep for hard-coded set unions)?
7. The tables: confirm table_entry derives from policy_mirror + reasonsUnderD only, and that regions_check's 44 probes cover what §2 claims. Check the six FAMILY predicates against pack C's actual rule structure (rules array indexes in the patch paths — do they point where the titles say?).
8. Pack C's bytes: disjointness/totality claims, the `in`/`not` structure, `onUnknown` semantics, anything in the pack that could dispose differently than the mirror on non-probe inputs.
9. K controls: verify their facts avoid every predicate and their wrongness under the mirror; verify their table rows are D-invariant across ALL six mutations, not just the sampled one.
10. §9's ceiling: is anything claimed as "mechanically enforced" that the code does not enforce?

For each finding: number, severity (blocker / material / minor), the exact file/text at fault, the failure it permits, the minimal fix. End with a verdict: "lock as is", "lock with amendments" (list them exactly), or "redesign". The maintainer will execute the lock on your verdict; findings you miss here are findings the post-run review will hold against both of us.
```

## Complete output (unedited)

## Verdict: redesign

Do not protocol-lock this candidate.

Review basis is commit `0c9bdaa183c14cb29c78b18ed06f37ce38629852`. The candidate advanced from `2051da8` through `0252252` to `0c9bdaa` during review; I re-reviewed the final diffs, but this verdict covers no later bytes.

### Findings

1. **Blocker — Rekor does not authenticate the publication clock.**

   **At fault:** [study.py:273](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:273), [study.py:508](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:508), [study.py:645](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:645).

   `body` and `verification` returned by Rekor are retained but never checked. Validation verifies only the operator’s witness signature and a locally stated artifact hash; UUID, `logIndex`, and `integratedTime` remain unauthenticated.

   **Failure:** The operator can sign the real manifest, fabricate an `integratedTime` corresponding to any favorable recent drand round, and pass validation with an unrelated or empty Rekor proof.

   **Minimal fix:** Pin the Rekor log key/checkpoint; decode and require the exact hashedrekord body; verify UUID/body binding, signed-entry timestamp, `integratedTime`, `logIndex`, and inclusion proof before using the clock.

2. **Blocker — publication uniqueness and the witness SEARCH gate are unsound.**

   **At fault:** [PREREGISTRATION.md:177](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:177), [study.py:406](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:406), [study.py:442](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:442), [study.py:724](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:724).

   - The same key signs the earlier lock inclusion and records inclusion, so §5’s literal “minimal logIndex among entries under that key” selects the lock entry.
   - `cmd_witness` writes `SEARCH.json` before raising on strangers.
   - `cmd_freeze` checks only that the nominated UUID appears in `hits`; it ignores strangers, known-set equality, indexes, authenticity, and whether witness itself refused.
   - A hand-authored SEARCH passes.
   - An eventually consistent search response is not proof that no earlier entry exists.
   - Fresh keys on parallel lock branches are invisible to one another.

   **Failure:** Same-key competing inclusions can pass freeze. More fundamentally, the operator can create several fresh-key branches, publish each before its beacon, then retain the favorable draw. Re-locking after seeing records is also not mechanically excluded.

   **Minimal fix:** Externally designate one canonical study lock/key before records, verify lock chronology and ancestry, use separate lock/publication keys, and establish authenticated completeness. Prefer one fixed future round with no operator-variable commit salt. This is a design change.

3. **Blocker — the records used after the draw need not be the published records.**

   **At fault:** [study.py:390](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:390), [study.py:508](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:508), [study.py:569](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:569), [study.py:601](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:601).

   `cmd_draw` checks `records_commit()` before waiting for the future round, but derives H/Q/F and tables from live files after fetching the beacon. It never rechecks the commit. `cmd_validate` never compares current authoring/record bytes with `DRAW.recordsCommit`.

   **Failure:** Publish set A, begin draw, wait for the beacon, replace the live completion/transcript/records with a prebuilt set B tailored to the sampled index, and let draw derive B. Freeze validates B’s internal consistency while retaining A’s publication OID. Symlinks provide an additional variant because Git binds only the link target string.

   **Minimal fix:** Publish an exact closed manifest of regular-file paths, modes, and blobs. Materialize and derive from the published commit tree, not the worktree; compare it again after beacon retrieval, during validation, and at freeze.

4. **Blocker — protocol lock and artifact freeze are open, non-canonical manifests.**

   **At fault:** [study.py:77](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:77), [study.py:373](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:373), [study.py:697](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:697), [study.py:739](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:739).

   `verify_lock()` and `verify_freeze()` iterate whatever digest keys their JSON files supply. They do not enforce exact key sets, top-level/nested schemas, fixed draw constants, 44 probes, raw-info consistency, or that locked inputs are regular HEAD blobs.

   **Failure:** A hand-edited committed lock can omit `FAMILY.json` or `study.py`, alter the offset/deadline/chain, claim 44 probes without running them, or bind uncommitted worktree bytes. The analogous freeze can omit generated inputs.

   **Minimal fix:** Canonically regenerate both manifests; require exact schemas and path sets; compare every regular-file blob and mode against the committed tree; validate all fixed constants, probe execution, lock inclusion, ancestry, and chronology.

5. **Blocker — the registered wrapper changes the prompt bytes.**

   **At fault:** [authoring_call.sh:33](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/transcription/authoring_call.sh:33), [transcript_check.py:63](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/transcript_check.py:63).

   `PROMPT="$(cat PROMPT.txt)"` strips trailing newlines. `PROMPT.txt` is 2400 bytes ending in LF; the argument is 2399 bytes, while the checker requires all 2400.

   **Failure:** The honest registered invocation is inconsistent with its own admissibility check.

   **Minimal fix:** Use a byte-preserving supported input mechanism and test the actual transcript user bytes against `PROMPT.txt`.

6. **Blocker — tool-assisted or defect-informed transcripts can pass.**

   **At fault:** [transcript_check.py:23](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/transcript_check.py:23).

   Passing counterexamples include:

   - payload type `tool_search_output`;
   - a `message` with role `tool`;
   - exact prompt text plus an ignored `input_image` or audio item containing pack information;
   - earlier unvalidated user/developer context;
   - a pack-aware user→assistant exchange followed by an unanswered exact registered user message;
   - assistant `input_text`, which is incorrectly treated as `output_text`.

   JSON `false` also passes the exit-status check because `False == 0`.

   **Failure:** The checker does not establish that the compiled completion was the response to the registered, policy-only prompt without tools.

   **Minimal fix:** Parse a strict versioned schema while preserving event order and turn identity. Require one terminal registered request/response pair, role-specific content, approved prior context only, no attachments/tool roles/call outputs/unknown types, and `type(exitStatus) is int`.

7. **Blocker — the wrapper does not establish the claimed external OpenAI invocation.**

   **At fault:** [authoring_call.sh:19](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/transcription/authoring_call.sh:19).

   The outside-repository check excludes only `$STUDY`, not the Git root, and does not resolve relative paths or symlinks. The process inherits the full environment although `CALL.json` records only `PATH`/`HOME`; `PATH` chooses an unpinned executable; model/provider/config are unpinned. The script retains the lexicographically first new session without requiring exactly one or correlating it with the process.

   The registered transport retry is also impossible: any second invocation refuses because the fixed output directory exists.

   **Failure:** Repository context, pack-aware base instructions, another provider/model, a fake `codex`, or an unrelated concurrent session can satisfy validation.

   **Minimal fix:** Use an exclusively created canonical directory outside the Git root, isolated locked configuration/environment/session storage, a digest-pinned executable and provider/model, exact CALL/session metadata validation, and numbered immutable retry attempts—or amend the protocol to zero retries.

8. **Blocker — E1 and the attempt ledger are still not total.**

   **At fault:** [study.py:908](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:908), [study.py:995](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:995), [study.py:1060](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:1060).

   Full validation happens before `STARTED`, and `FREEZE-DIGEST` is written before entering `try`. Thus prerequisite failure can leave no primary attempt. Many score-time malformed/missing-data paths raise instead of writing E1 `pipeline-invalid`.

   `verify_seal()` checks only manifested files, not the exact actual set; an added `DONE` is invisible to the seal.

   **Failure:** The supposedly exhaustive partition can produce no E1 at all or skip the first failed validation. A late crashed attempt can be promoted by adding `DONE`.

   **Minimal fix:** Atomically create a STARTED record containing the freeze digest before fallible prerequisite work; wrap every later exit; seal and verify the exact file set including terminal state; make score total over all malformed/missing prerequisites.

9. **Material — the compiler is not the registered strict transformation.**

   **At fault:** [records_compile.py:37](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:37), [records_compile.py:59](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:59), [records_compile.py:168](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:168), [records_compile.py:181](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:181).

   - Text-mode reads normalize CRLF, so the widest span can differ from the transcript-bound completion.
   - Python’s decoder accepts `NaN`, `Infinity`, and `-Infinity`; a wider non-JSON array can win extraction.
   - `$` accepts a terminal newline, so `"40\n"`, `"SY\n"`, and `"ok\n"` pass the registered forms.
   - Verification ignores extra non-JSON directory entries and file types.
   - `decidedAt` accepts any string despite the requested ISO-UTC form.

   **Minimal fix:** Read bytes then UTF-8 decode without newline conversion; reject JSON constants; use `fullmatch`/`\Z`; require the exact regular-file set; either add a timestamp check/drop code or disclaim timestamp validation.

10. **Material — validation does not bind DEFECT.json exactly to the sampled family member.**

   **At fault:** [study.py:612](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:612), [study.py:685](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:685).

   Although `mutation` must equal the sampled FAMILY entry, D is regenerated from the separate top-level `manifest["patch"]`; equality with `mutation["patch"]` is never required. `sets.K` need not be the two exact control IDs, and extra nonexistent IDs in F are not rejected.

   **Failure:** An arbitrary alternate D that agrees with the finite record set can pass E2 while not being the selected mutation. K/authored membership can be swapped, and ghost F members corrupt E3.

   **Minimal fix:** Recompute the complete canonical DEFECT body from FAMILY and published records and byte-compare it. Remove duplicate patch authority; require exact K and exact derived H/Q/F.

11. **Material — drand proof retention and deadline enforcement are partial.**

   **At fault:** [study.py:207](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:207), [study.py:487](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:487), [study.py:529](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:529), [study.py:638](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:638).

   HTTP responses are parsed rather than retained as raw bytes. `previous_signature` may be absent; validation does not check it, saved-chain equality, exactly two configured relays, or relay provenance. Two duplicated local objects pass. The deadline is checked before retrieval, not after it finishes.

   **Failure:** The frozen material can lack the inputs promised for external BLS verification, and a retrieval completing after the 3600-second deadline is accepted.

   **Minimal fix:** Retain raw response bytes and retrieval timestamps; require exactly the two configured relays, strict/equal signature and previous-signature values, lock-chain equality, and completion before the deadline.

12. **Material — the arbiter and compiler disagree on the country domain.**

   **At fault:** [POLICY.md:22](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/policy/POLICY.md:22), [PROMPT.txt:11](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/transcription/PROMPT.txt:11), [PREREGISTRATION.md:60](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/PREREGISTRATION.md:60), [records_compile.py:38](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:38).

   POLICY and the author-facing prompt say ISO 3166-1 codes; the governing §2 and compiler accept every `[A-Z]{2}` string and treat unassigned values as non-embargoed.

   **Failure:** An unassigned value can enter H/F and support `caught` even though it is outside the policy supplied to the author.

   **Minimal fix:** State everywhere that the domain is exactly two uppercase ASCII letters with no registry requirement, or pin and enforce an actual registry set.

13. **Minor — pack C’s unknown semantics are not the policy’s blanket semantics.**

   **At fault:** [POLICY.md:24](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/policy/POLICY.md:24), [vendor-screening-correct.pack.json:45](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/packs/vendor-screening-correct.pack.json:45).

   Strong conjunction/short-circuiting masks unknowns. For example, sanctions=true with other fields missing rejects; false+SY with fields missing rejects; false+DE+risk 20 with personal-data missing clears.

   **Failure:** The global assertion that any unknown input escalates is false, and all 44 probes are complete so they cannot detect it. Admitted study rows are complete, so this does not currently corrupt E1/E2.

   **Minimal fix:** Narrow the claim to complete admitted inputs, or add a whole-input completeness guard and missing/malformed-input probes.

14. **Minor — locked documentation still describes superseded behavior.**

   **At fault:** [study.py:16](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:16), [records_compile.py:2](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:2), [authoring_call.sh:8](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/transcription/authoring_call.sh:8), [README.md:19](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/README.md:19).

   These still say first-DONE primary, first-array/raw-stdout compilation, or omit `timestamp-lock`, `publish`, and `witness`.

   **Failure:** The locked procedure gives conflicting operator instructions.

   **Minimal fix:** Conform all locked descriptions to the governing revision and actual command surface.

### Prior 14 dispositions

| Prior finding | Status |
|---|---|
| 1 — operator-supplied clock | **Fail:** Rekor is used on the happy path, but its clock is not authenticated. |
| 2 — unique publication | **Fail:** SEARCH, same-key, and cross-key uniqueness all fail. |
| 3 — drand proof | **Partial:** signatures/constants are retained; raw bytes and mandatory verification inputs are not enforced. |
| 4 — byte-complete algorithms | **Partial:** index/round arithmetic is exact; deadline and immutable lock constants are not. |
| 5 — E1 totality | **Partial:** valid-path branch order is correct; failure paths can produce no label. |
| 6 — crash/primary rule | **Partial:** `_run_body` crashes seal and first bound attempt is selected, but validation/scoring gaps remain. |
| 7 — compiler closure | **Partial:** widest-span, duplicate-key rejection, precedence, and rendering work; strict JSON/forms/exact files do not. |
| 8 — completion binding | **Fail/partial:** completion equality exists, but prompt bytes, tool/context exclusion, and turn binding fail. |
| 9 — independent tables | **Partial:** table derivation itself passes; canonical lock/probe execution and exact D binding do not. |
| 10 — Study 010 port | **Partial:** four-fact H/Q/K and dynamic mismatches exist; lifecycle and exact validation remain incomplete. |
| 11 — K path | **Pass:** separate source path, prefix reservation, acquisition/gate coverage, wrongness, and all-six D invariance are correct. |
| 12 — exact candidate/lock | **Fail:** key-set validation and chronology are absent; the candidate also changed during review. |
| 13 — evidentiary ceiling | **Fail:** §9 overstates lock, Rekor, transcript, compiler, and ledger enforcement and omits cross-key published-branch grinding. |
| 14 — Q∩F in E3 | **Pass:** counts are explicit and sampled H/Q IDs appear in the coverage profile; E1 also reports them directly. |

### Confirmed sound

- The registered and implemented draw arithmetic agree exactly. At `T-G = kp`, the selected round is `R=k+1`, scheduled exactly at T; there is no boundary off-by-one.
- The index preimage, newline framing, FAMILY byte digest, big-endian SHA-256 integer, and modulo six match §5.
- All six FAMILY patch paths, titles, predicates, and `reasonsUnderD` match pack C’s actual rule structure.
- Pack C is disjoint and total over complete admitted inputs and agrees with the mirror there.
- `regions_check` contains exactly 44 distinct probes matching §2’s stated battery.
- `table_entry` derives exclusively from the mirror, predicate, and `reasonsUnderD`.
- Both K controls are wrong under C, avoid all six predicates, and remain D-invariant under all six mutations.
- Mismatch sets are derived from tables; no hard-coded F/Q/K union remains.
- The 17 existing unit tests pass, but do not cover the counterexamples above.

**Final verdict: redesign.** The unauthenticated Rekor time, ineffective uniqueness gate, and post-beacon record substitution each independently defeat the claimed exogenous draw.

## Maintainer disposition (revision 3 → revision 4)

All fourteen findings accepted; none contested. How revision 4 implements
each (file references are to the revision-4 candidate):

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | Rekor's clock unauthenticated | **Accepted.** `verify_inclusion` (study.py) authenticates every retained inclusion offline: body decodes to the hashedrekord binding the manifest digest, witness signature, and locked witness key; UUID = sha256(0x00 ‖ body); logID = sha256 of the Rekor log key pinned at lock time; and the log's `signedEntryTimestamp` verifies under that pinned key over the canonical `{body, integratedTime, logID, logIndex}` payload. Run at publication, at draw, and in every validate. The recipe was verified live against the log before locking it in. |
| 2 | Uniqueness and the SEARCH gate unsound | **Accepted.** Two witness keys (lock / records), both public keys locked; the binding inclusion is the single entry under the records key. The freeze gate runs the online search ITSELF over both keys — a hand-authored SEARCH.json convinces nothing — refuses strangers, and requires the records entry indexed. Cross-key parallel-branch grinding is mechanically unpreventable and is now stated as such in §9, with what a reader can and cannot conclude. |
| 3 | Post-beacon record substitution | **Accepted.** The draw re-checks the records commit after beacon retrieval, requires the worktree's published paths to byte-equal that commit's tree (exact file set, regular files only), and derives DEFECT.json from the PUBLISHED tree bytes (`published_tree` / `derive_defect`), never the worktree. `validate` recomputes the complete canonical DEFECT body from the same tree and byte-compares. |
| 4 | Lock/freeze manifests open and non-canonical | **Accepted.** `verify_lock` and `verify_freeze` enforce exact key sets against the registered lists, require every input to be a regular file matching BOTH the worktree and its HEAD blob, and check the recorded draw constants, relay list, probe count, jpack digest, witness-key digests, and Rekor log key against the module's registered values. |
| 5 | The wrapper strips the prompt's trailing newline | **Accepted.** `PROMPT.txt` carries no trailing newline (registered in §7), so `$(cat …)` is byte-identical to the file; the transcript check compares full file bytes. |
| 6 | Tool-assisted transcripts can pass | **Accepted.** `transcript_check.py` is a strict whitelist: only `message` payloads with roles user/developer/assistant; role-appropriate content items only (`input_text` / `output_text`); ANY other payload type refuses. Exactly one user message must equal the prompt bytes, none may follow it, and the completion is the last assistant message after it. `exitStatus` must be an integer (booleans rejected). |
| 7 | The wrapper does not establish the claimed invocation | **Accepted.** `authoring_call.sh`: scratch dir resolved with `pwd -P` and required outside `git rev-parse --show-toplevel`; environment scrubbed to `PATH`+`HOME` via `env -i`; the codex binary must match the digest the lock pinned (refused otherwise, and re-checked in validate); immutable `call-N` slots with the completed-slot-refuses-retry rule; exactly one new session file required, with the count recorded and enforced again by the driver's `authoring_call()` resolution. What remains self-reported is stated in §9. |
| 8 | E1/ledger still not total | **Accepted.** `run` opens the attempt (STARTED + freeze digest) before any fallible work — freeze/validation failures crash INSIDE the attempt and seal; `verify_seal` requires the exact file set (an added DONE is drift, not promotion); `score` wraps its body so malformed retained data writes E1 = pipeline-invalid with the error retained. |
| 9 | Compiler not the registered strict transformation | **Accepted.** Byte-read with no newline translation; `parse_constant` rejects NaN/Infinity; every form check is `fullmatch`; a `timestamp-form` drop code (`YYYY-MM-DDTHH:MM:SSZ`) joins the registered order; `verify` requires the exact directory entry set with regular files only. |
| 10 | DEFECT.json not bound to the sampled member | **Accepted.** The separate top-level `patch` authority is gone — D regenerates from `mutation["patch"]` only; `validate` recomputes the entire canonical DEFECT body (sets and tables, exact K, no ghost ids) from the published tree and requires equality. |
| 11 | drand retention/deadline partial | **Accepted.** Raw response bytes and retrieval timestamps retained per relay; exactly the two registered relays required in order; `previous_signature` required present and byte-equal; the chain object must equal the locked constants; the deadline binds retrieval COMPLETION and is re-checked in validate from retained timestamps. |
| 12 | Arbiter and compiler disagree on the country domain | **Accepted.** POLICY.md now states the syntactic domain itself (two uppercase letters, no registry, membership = exact string comparison); the prompt keeps ISO phrasing as authoring guidance; §2 unchanged (already syntactic). |
| 13 | Pack C's unknown semantics overstated | **Accepted.** POLICY.md narrows exhaustiveness to complete inputs — which is all the study's gates admit — and takes no position on incomplete inputs. |
| 14 | Stale locked documentation | **Accepted.** study.py, records_compile.py, authoring_call.sh, and README.md all describe the revision-4 command surface, the slot discipline, the completion input, and the first-started primary rule. |

The reviewer's "confirmed sound" list (draw arithmetic and §5 agreement,
family patch paths and predicates against pack C's actual structure, pack
C disjointness/totality on complete inputs, the 44-probe battery, mirror-
only table derivation, K's all-six-mutation invariance, derived mismatch
sets) carries forward into revision 4 unchanged.

---

# Pre-freeze adversarial review — revision 4

**Verdict: redesign. Nothing froze; revision 5 implements every finding.**

Review basis: commit `2566b7e`, pinned before the review and unchanged
throughout it.

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-05. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing the pre-freeze adversarial review of Study 010's revision-4 protocol-lock candidate. You reviewed revisions 1-3 (verdicts: redesign, redesign, redesign). Your revision-3 review confirmed the draw arithmetic, family predicates, table derivation, controls, and derived mismatch sets sound, and listed 14 mechanization findings; the maintainer accepted all 14 and implemented them. PREREG-REVIEW.md records all three reviews and all three disposition tables. This review's basis is a single pinned commit — the candidate will not change during your review.

Review, in studies/010-blinded-oracle/:
- PREREGISTRATION.md (revision 4, governing)
- PREREG-REVIEW.md (three reviews + dispositions — check the revision-3 disposition claims against the actual bytes)
- policy/POLICY.md, packs/vendor-screening-correct.pack.json, FAMILY.json
- transcription/PROMPT.txt (now newline-free), transcription/record.rule.json, transcription/transcribe.py, transcription/authoring_call.sh
- controls/, source/record_source.py
- harness/: study.py, gate.py, pnf_check.py, policy_mirror.py, records_compile.py, regions_check.py, transcript_check.py, test_study.py
Shared line code: acquisition-proxy/attest.py, derivation-rule/derive.py, fabrication-gate/gate.py. Predecessor: studies/009-transcribed-oracle-matrix/.

Verified live before this review (maintainer's rehearsals, real Rekor + real drand; re-derive anything you rely on): the Rekor SET verification recipe (canonical {body,integratedTime,logID,logIndex} payload, ECDSA under the log key fetched from /api/v1/log/publicKey; UUID tail = sha256(0x00||body); logID = sha256(log key DER)) verifies against the production log; the full lock→timestamp→authoring→compile→publish→witness→draw→freeze→run→score pipeline completes.

Your 14 revision-3 findings and what to re-check:
1. Rekor clock: verify_inclusion in study.py — is the SET payload canonicalization correct and is verify_inclusion actually called everywhere the clock is used? Can a fabricated integratedTime still pass anywhere?
2. Uniqueness: two keys (witness-lock-pub / witness-records-pub), freeze runs witness_search itself. Can same-key or indexed-stranger entries still slip? Is the §9 cross-key-grinding ceiling statement accurate and complete?
3. Post-beacon substitution: published_tree/derive_defect/assert_worktree_is — does the draw truly derive from the committed tree? Any residual worktree dependence (controls? FAMILY? packs?) that could be swapped post-beacon? (Note controls and FAMILY are locked inputs — is locking sufficient there?)
4. Canonical manifests: verify_lock/verify_freeze — exact key sets, HEAD-blob agreement, constants. Any member still unchecked (python version? codex pin? drand rawInfo consistency)?
5. Prompt bytes: PROMPT.txt has no trailing LF; authoring_call.sh passes $(cat). Byte-exact now? Any remaining shell transformation (backslashes, NUL, locale)?
6. transcript_check.py whitelist: enumerate payload types/roles/content shapes that still pass but shouldn't. Multi-content-item messages? An assistant message BEFORE the prompt used as completion? Developer-role prompt injection?
7. authoring_call.sh: git-root escape via symlink/bind mount? env -i complete? The slot rules vs study.py's authoring_call() resolution — can they disagree? Binary pinning bypass?
8. Ledger totality: run opens the attempt before verify_freeze/validate; score wraps its body; verify_seal exact-set. Walk each failure path — does every one land in exactly one E1 label or a pre-attempt refusal that §6 sanctions?
9. Compiler: byte-read, parse_constant, fullmatch, timestamp-form, exact-dir verify. Any remaining nondeterminism or acceptance the registered grammar excludes?
10. DEFECT binding: derive_defect byte-recompute in validate; single patch authority. Ghost ids? K substitutions?
11. drand retention: raw bytes + retrievedAt + previous_signature + chain equality + post-retrieval deadline. Sufficient for external BLS verification?
12-14. Country domain prose, unknown-semantics narrowing, doc conformance — all aligned now?

Also stress anything NEW that revision 4 introduced (the slot system, witness_search, verify_inclusion, published_tree, the total scorer) — new code is where new holes live. And check test_study.py covers the new behaviors it claims.

For each finding: number, severity (blocker / material / minor), the exact file/text at fault, the failure it permits, the minimal fix. End with a verdict: "lock as is", "lock with amendments" (list them exactly), or "redesign". Bear in mind the study's claims are now explicitly tiered in §9 (enforced / recorded / not prevented): a finding that an unprevented action is possible is only a finding if §9 misstates it. The maintainer will execute the lock on your verdict.
```

## Complete output (unedited)

# Verdict: redesign

Do not protocol-lock commit `2566b7eab8376765b05f520b66aa3eb1a4ac9e20`. The reviewed paths match that commit and remain unmodified, but several revision-3 blocker dispositions are only partial.

## Findings

1. **Blocker — the protocol lock and artifact freeze remain security-relevantly non-canonical.**

   **At fault:** [study.py:527](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:527), especially lines 548–564 and 1046–1081; [PREREGISTRATION.md:368](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:368); disposition [PREREG-REVIEW.md:691](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREG-REVIEW.md:691).

   `verify_lock` does not enforce exact recursive schemas or bind the drand chain fields to `rawInfo` or reviewed mainnet constants. It also does not validate the production Rekor key, Python fields, Codex version/digest against the executing binary, most draw-rule members, or duplicate/extra keys. `verify_freeze` accepts any `frozen["jpack"]` matching the supplied binary instead of requiring `JPACK_DIGEST`, checks only Python’s version—not implementation—and ignores most of its schema.

   **Failure:** changing locked genesis from `G` to `G + k·p` while retaining the real chain hash changes the fetched round from `R` to `R-k` while leaving the computed scheduled time unchanged. The operator can therefore select an already-known drand signature, grind the records commit OID, and pass draw/deadline validation. Separately, a hand-edited freeze can authorize a malicious evaluator.

   An attacker Rekor key can also be placed in the lock. A genuine production body/UUID can then be paired with fabricated time/index fields and an attacker-signed SET; `witness_search` finds the genuine UUID but never compares the production entry’s time/index with the retained inclusion.

   **Minimal fix:** strict duplicate-rejecting recursive schemas; hard-pin the production Rekor key and default drand chain constants in reviewed bytes; retain raw chain-info bytes and require field-for-field consistency; require exact draw constants; require `frozen["jpack"] == JPACK_DIGEST`; validate exact Python implementation/version, Codex identity, invocation, and preregistration commit; reject all extra fields.

2. **Material — the lock inclusion and lock-key uniqueness side are unauthenticated.**

   **At fault:** [study.py:632](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:632) and lines 903–992; [PREREGISTRATION.md:183](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:183); dispositions 1–2 at PREREG-REVIEW.md:688–689.

   `LOCK-INCLUSION.json` is never passed to `verify_inclusion`. Its UUID is merely added to the known set; zero lock-key hits still pass. A single actual stranger can be laundered by putting its UUID in `LOCK-INCLUSION.json`. The lock UUID need not be indexed, and the body need not bind the lock commit.

   Returned records-key strangers are correctly rejected, and identical lock/records keys make the normal search fail. But the index has no authenticated completeness, so an inclusion still lagging the index is not excluded.

   **Failure:** the purported lock timestamp and lock-before-authoring chronology can be absent or unrelated while freeze succeeds.

   **Minimal fix:** authenticate both inclusions during every validation; bind the lock inclusion to an explicit lock commit that contains the locked bytes and is an ancestor of the records commit; require observed hit sets exactly `{lock UUID}` and `{records UUID}`; require distinct valid P-256 keys. Describe the index search as an online observation, not proof of global uniqueness.

3. **Blocker — post-beacon FAMILY substitution can steer the index despite the frozen manifest.**

   **At fault:** [study.py:821](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:821), particularly lines 861–890; `derive_defect` lines 798–799; validation lines 903–989; [PREREGISTRATION.md:254](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:254) and 419–433.

   The authored records are correctly read from the published tree. However, `verify_lock` runs before the beacon wait, while the family digest, family member, controls, and pack C are read later from the worktree. Validation repeats the same check-then-live-read pattern.

   **Failure:** after the beacon, replace `FAMILY.json` with a whitespace-only variant until its digest yields a desired index. Its parsed mutations remain identical. Restore the original, then repeat the transient variant after `verify_lock` during freeze/run validation. `freeze_body` pins the restored original, and score does not revalidate the draw. This contradicts §9’s assertion that conceded transient edits cannot steer the index.

   **Minimal fix:** snapshot every locked dependency from immutable committed blobs before waiting and derive exclusively from that snapshot; validation must compare DRAW directly with the lock/HEAD blobs, not re-read a mutable worktree after a TOCTOU check. Narrow §9’s owner-execution claim accordingly.

4. **Material — §9 understates cross-key branch grinding.**

   **At fault:** [PREREGISTRATION.md:413](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:413), especially lines 429–433.

   **Failure:** multiple branches may publish byte-identical records under fresh keys but use distinct records-commit OIDs. Because the OID salts the index, the operator can observe every branch’s beacon and designate a favorable sampled index/E1 afterward. This biases the retained index and outcome, not merely “which record set reached publication.”

   **Minimal fix:** state that each individual inclusion fixes its own draw, but post-beacon designation among independently published branches can bias the retained index/outcome. If that ceiling is unacceptable, externally designate one canonical lock/key/commit branch before any publication.

5. **Blocker — arbitrary prior context still passes the policy-only transcript gate.**

   **At fault:** [transcript_check.py:38](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/transcript_check.py:38), especially lines 47–71 and 87–100; the positive fixture at [test_study.py:223](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/test_study.py:223); disposition 6 at PREREG-REVIEW.md:693.

   Unlimited earlier user/developer/assistant messages pass. The registered prompt may itself be a developer message. Non-`response_item` entries are ignored, arbitrary extra payload/content keys pass, and JSON duplicate keys are not rejected.

   I reproduced admission of an earlier developer message containing FAMILY information, an assistant acknowledgement, the exact prompt with an extra hidden content member, and a tailored completion.

   **Failure:** an admissible completion can be explicitly defect-informed while still showing no tool call.

   **Minimal fix:** require one terminal user prompt; permit only exact locked prior developer context; reject prior user conversation; validate exact key sets with duplicate-key rejection; validate or reject all context-bearing top-level events and metadata.

6. **Blocker — the wrapper does not bind model, provider, configuration, or even canonical CALL metadata.**

   **At fault:** [authoring_call.sh:20](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/transcription/authoring_call.sh:20), lines 74–78 and 104–123; [study.py:153](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:153) and 903–917; disposition 7 at PREREG-REVIEW.md:694.

   The real `HOME` is retained, so mutable Codex configuration is loaded. There is no explicit model/provider/effort, no `--ignore-user-config`, and effective `session_meta`/`turn_context` are ignored. An empty child of a different prepared Git repository passes the scratch check and can inject repository instructions.

   Validation permits a `CALL.json` containing only exit status, session count, and a copied binary digest; argv, cwd, environment, CLI identity, stdin, and scrub status may be absent. Thus §9’s statement that these are at least recorded is too strong.

   **Failure:** a local/other provider, different model, pack-aware configuration, or other-repository instructions can generate the accepted completion.

   **Minimal fix:** wrapper-owned exclusive scratch outside every Git worktree; isolated configuration/home; explicit provider/model/effort; ignore user config and rules; execute the resolved absolute binary; and validate exact CALL/session metadata including cwd, base instructions, provider, model, CLI version, and environment.

7. **Material — ordinary reasoning-model session items are rejected, irrecoverably burning an exit-0 slot.**

   **At fault:** [transcript_check.py:52](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/transcript_check.py:52); [authoring_call.sh:88](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/transcription/authoring_call.sh:88).

   Current Codex 0.145 session files normally contain `response_item` payloads of type `reasoning`, including no-tool sessions. `_events` rejects these. The wrapper then writes no completion but records the underlying exit status 0, after which every retry refuses.

   **Failure:** a faithful no-tool invocation can become permanently inadmissible despite succeeding.

   **Minimal fix:** admit an exact inert `reasoning` schema while continuing to reject every call/output form, or pin a session mode proven not to emit it. Test against a captured no-tool session from the pinned model.

8. **Material — retry slots can retain multiple completed model outputs.**

   **At fault:** authoring_call.sh:50–57 and 88–101; study.py:165–183; [PREREGISTRATION.md:123](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/PREREGISTRATION.md:123) and 437–438.

   Completion extraction runs whenever one new session exists, regardless of process exit status. Any nonzero or malformed status is treated as retryable by the driver.

   **Failure:** terminate Codex after its assistant response is persisted but before normal exit; inspect the retained completion and retry. Up to three real outputs can exist, contrary to §10’s “One model completion.” §9 concedes that no-retry is unproven, but it does not make the stated retained-output bound accurate.

   **Minimal fix:** use zero retries, or permit retry only for an exact-schema nonzero slot containing no assistant completion; otherwise amend §§1, 4, 9, and 10 to say up to three retained outputs.

9. **Blocker — the freeze/attempt ledger can be reset or promoted, and scoring is still non-total.**

   **At fault:** [study.py:655](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:655), 1025–1043, 1087–1098, 1214–1250, 1319–1354, and 1394–1407; disposition 8 at PREREG-REVIEW.md:695.

   Reproduced failures:

   - `cmd_freeze` overwrites the existing SEARCH/FREEZE; the new `queried` timestamp changes the digest. `primary_attempt` selects only attempts under the current digest, so re-freezing after a crash makes a later attempt primary.
   - `verify_seal` ignores directories, while `primary_attempt` treats any existing path named `DONE` as success. Adding an empty `DONE/` directory to a sealed crash passes the seal and promotes it.
   - `FREEZE-DIGEST` is written before the `try`; making `FREEZE.json` a directory leaves `STARTED` without terminal state or seal.
   - `cmd_score` runs `verify_freeze`, primary selection, and seal verification outside its exception-to-E1 guard; its catch tuple also omits ordinary failures such as `AttributeError` and many `OSError`s.

   **Minimal fix:** make the first committed freeze immutable/unique and bind primary selection to it; atomically create one STARTED record containing the freeze digest; terminalize/seal from one outer guard; reject all unmanifested directories, symlinks, and specials; require exactly one regular `DONE` or `CRASHED.json`; move all score prechecks inside a total `Exception`-to-E1 boundary.

10. **Material — DEFECT and D are compared as Python objects, not canonical bytes, and boolean/integer equality changes semantics.**

   **At fault:** [study.py:918](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:918), especially lines 973–989; disposition 10 at PREREG-REVIEW.md:697.

   Python considers `False == 0`. Changing `mutation.predicate.sanctionsHit` from `false` to `0` still equals the FAMILY member but makes `predicate_matches` fail because it uses identity. Similarly, D’s mutated `false` can be replaced by numeric `0` and still compare equal. Duplicate-key or noncanonical DEFECT bytes also pass if Python’s resulting object matches.

   **Failure:** F/tables or pack types can differ from the sampled locked mutation while validation accepts the purported canonical lineage.

   **Minimal fix:** select the mutation exclusively from locked FAMILY bytes; render canonical DEFECT and D with one shared serializer and compare raw bytes; use duplicate-rejecting parsing only for diagnostics; require exact integer/boolean types.

11. **Material — compiler extraction depends on an unlocked Python runtime flag.**

   **At fault:** [records_compile.py:77](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:77); PREREGISTRATION.md:146–168.

   With Python 3.8.20’s default 4,300-digit limit, a valid JSON array containing a 5,000-digit integer produces “no parseable JSON array.” With identical bytes and `PYTHONINTMAXSTRDIGITS=0`, it parses and yields one `schema` drop.

   **Failure:** the selected array and authoring ledger can vary with ambient environment despite identical completion bytes and Python version.

   **Minimal fix:** use host-limit-independent `parse_int`/`parse_float` handling, such as `Decimal` or an explicit JSON-number token, or register and mechanically pin the integer-limit setting.

12. **Minor — `verify_inclusion` does not enforce the exact hashedrekord body it describes.**

   **At fault:** [study.py:380](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/study.py:380).

   It checks selected nested values but not `apiVersion`, `algorithm == "sha256"`, exact keys, duplicate keys, or consistency of flattened fields with `rawResponse`.

   **Failure:** with an honestly pinned production key this does not permit a fake clock, but the claimed strict body/raw binding is false.

   **Minimal fix:** duplicate-rejecting exact-schema decoding and exact comparison with the expected hashedrekord body and retained raw response.

13. **Minor — two compiler closure claims remain broader than the code.**

   **At fault:** [records_compile.py:42](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:42), 120, and 202–216.

   `2026-99-99T99:99:99Z` passes `timestamp-form`, despite the prompt calling the value ISO-8601 UTC. Regular-file checking covers `records/*` but not `RECORDS.md`; a byte-equal symlink passes this stage, although published-tree validation later catches it.

   **Minimal fix:** validate calendar/clock ranges or explicitly call the field a digit-shape; reject symlinks/specials for `RECORDS.md` and the records directory too.

14. **Minor — revision-4 security behavior is untested and two locked descriptions remain stale.**

   **At fault:** [test_study.py:1](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/test_study.py:1), [records_compile.py:220](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/harness/records_compile.py:220), and [README.md:3](/tmp/claude-1000/-home/onword/repo/judgment-pack/judgment-pack-runtime/studies/010-blinded-oracle/README.md:3).

   `test_study.py` is byte-identical to revision 3 and has no tests for SET verification, witness search, canonical manifests, published-tree checks, slots, freeze uniqueness, seals, total scoring, relay retention, or deadline validation. Its positive transcript fixture affirmatively permits prior context. The compiler usage still says `<raw-stdout-file>`, and README still says “Both revisions” after three rejected revisions.

   **Minimal fix:** add deterministic fixtures for every revision-4 trust boundary and correct those two descriptions.

## Revision-3 disposition audit

| Item | Result |
|---|---|
| 1 Rekor clock | **Partial:** canonical SET and call coverage are correct; the open lock can substitute the SET key. |
| 2 Uniqueness | **Partial:** returned records-key strangers are caught; lock inclusion, completeness, and the stated cross-key ceiling fail. |
| 3 Published-tree binding | **Partial:** authored records are genuinely tree-derived; FAMILY/controls/C remain post-check worktree reads. |
| 4 Canonical manifests | **Fail.** |
| 5 Prompt bytes | **Pass.** File and shell argument hashes match; no trailing LF or NUL. |
| 6 Transcript whitelist | **Fail.** |
| 7 Authoring wrapper | **Fail.** |
| 8 Ledger/scorer totality | **Fail.** |
| 9 Compiler fixes | **Partial:** byte read, constants, fullmatches, and exact records directory pass; runtime-number parsing remains variable. |
| 10 DEFECT binding | **Partial:** exact sets derive semantically, but byte/type binding fails. |
| 11 Drand retention | **Substantively pass under an honest lock:** both relay payloads, timestamps, signatures, previous signature, chain fields, and deadline are retained/rechecked; BLS is accurately disclaimed. Chain-info raw/canonical binding remains finding 1. |
| 12 Country domain | **Pass.** |
| 13 Unknown semantics | **Pass.** |
| 14 Documentation | **Partial.** |

## Rechecks that passed

- The SET payload is the correct compact, key-sorted `{body, integratedTime, logID, logIndex}` JSON. A locally signed canonical fixture passed; changing authenticated `integratedTime` failed. `verify_inclusion` is called at publication, draw, and validation wherever the records clock is used.
- PROMPT is 2,706 bytes, ends in `0x2e`, and the quoted shell substitution reproduces its hash exactly.
- All 17 committed tests pass, but do not exercise the revision-4 trust chain.
- The 44 registered C/mirror probes pass with the pinned jpack.
- An independent 1,560-row evaluator grid across all six mutations, plus all-six invariance for both K controls, passed. The family predicates, patch effects, reasons, C/D tables, controls, and derived mismatch logic remain sound.
- Country-domain and incomplete-input prose now align with compiler/mirror/gates.
- The valid-data E1 branch order is correct; the failure is the surrounding attempt identity and totality machinery.

**Verdict: redesign.**

## Maintainer disposition (revision 4 → revision 5)

All fourteen findings accepted; none contested. Finding 7 is the one that
justifies this whole regime: real `codex exec` sessions carry `reasoning`
items, revision 4's whitelist rejected them, and the retry rule forbids a
second completed call — so the honest authoring call would have been
permanently inadmissible on its first and only attempt. It was found by
review, not by rehearsal, because every rehearsal used a synthetic
transcript. Revision 5 was therefore built against **captured ground
truth**: a real no-tool session from the pinned CLI, and a second capture
of the exact registered invocation.

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | Lock/freeze schemas open; chain and log key substitutable | **Accepted.** The chain hash, chain public key, genesis, period, scheme, the production Rekor log key, the model, the jpack digest, and the draw constants are now **hard-pinned in `study.py`'s reviewed bytes** and compared against the lock rather than read from it; both manifests enforce exact member schemas (`LOCK_MEMBERS`, `DRAW_RULE_MEMBERS`, `DRAND_MEMBERS`, `REKOR_MEMBERS`, `FREEZE_MEMBERS`), `rawInfo` must agree field-for-field, the freeze must pin `JPACK_DIGEST` itself, and both keys must differ. Each pinned constant was verified against the live services before being written down. |
| 2 | Lock inclusion and lock-key side unauthenticated | **Accepted.** `LOCK-INCLUSION.json` now records the lock commit and is passed through `verify_inclusion` in every validation; the lock commit must be an ancestor of the records commit and its `integratedTime` must precede the publication's — lock-before-authoring is checkable from the log plus the commit graph. §5 says the index search is an online observation, not global-uniqueness proof. |
| 3 | Post-beacon FAMILY substitution steers the index | **Accepted — the important one.** `locked_snapshot()` reads `FAMILY.json`, pack C, and the controls from HEAD's blobs BEFORE the beacon wait, requires each to equal its worktree copy, and every subsequent derivation (digest, mutation selection, D, tables) uses only the snapshot. `validate` takes the same snapshot. The whitespace-variant attack no longer has a live read to hit. |
| 4 | §9 understates cross-key branch grinding | **Accepted.** §9 now says it plainly: because the records-commit OID salts the preimage, byte-identical record sets on different branches draw different indexes, so multi-branch publication biases *the retained index and E1 outcome*, not merely which record set was published. What the protocol proves is stated in its narrower true form, and the remedy (external designation of one canonical branch) is named as out of scope for a single-operator study. |
| 5 | Arbitrary prior context passes the policy-only gate | **Accepted.** Ground truth first: codex injects its own boilerplate into every session, so "no prior context" is unachievable. Instead the gate screens all prior context against a locked `LEAK_TOKENS` vocabulary (pack, family, mutation, fact, and study terms), after excising environment paths — with the wrapper independently refusing a scratch path that carries a leak token, so the excision cannot hide a plant. Validated both ways: the real captured session passes; a planted "P3 uses greater-than-or-equal at 70" turn refuses. Transcript lines are parsed with duplicate-key rejection. |
| 6 | Wrapper binds no model, provider, or configuration | **Accepted.** The wrapper now runs with an **isolated `CODEX_HOME`** (only the credential copied in, so no user config, rules, skills, or `AGENTS.md` reach the model — and session discovery becomes deterministic rather than a timestamp race), `--ignore-user-config`, an explicit `-m`, `env -i`, the resolved absolute binary, and a scratch directory refused if it lies in any git worktree or carries a leak token. `turn_context`'s model and cwd are checked against the lock and `CALL.json`. §9 states which `CALL.json` fields remain self-reported. |
| 7 | Reasoning items rejected; a faithful call becomes inadmissible | **Accepted.** Inert `reasoning` items are admitted (and refused if they carry any call-like member); every call form still refuses. The gate is now built against a captured session rather than an assumed schema, and the tests use real-shaped fixtures. |
| 8 | Retry slots can retain multiple completed outputs | **Accepted.** `completion.txt` is written only when the process exited 0, so a call killed after its answer persisted leaves a transcript but no compiler input — a retry cannot shop between outputs. §4 states the rule and §9 its residual. |
| 9 | Freeze/ledger resettable; scoring non-total | **Accepted.** The first committed `FREEZE.json` is immutable (re-freezing refuses); the freeze-digest write moved inside the run's guard; `verify_seal` rejects symlinks, directories, and any non-regular file and requires exactly one terminal marker; `DONE` must be a regular file; `cmd_score` wraps `verify_freeze`, primary selection, and seal verification inside one total `Exception` boundary. |
| 10 | DEFECT/D compared as Python objects | **Accepted.** One shared `canonical_json` serializer renders both; `validate` compares raw bytes against the recomputation, and the mutation is selected from snapshot bytes. `False`/`0` and duplicate-key variants no longer pass. |
| 11 | Compiler depends on an unlocked interpreter flag | **Accepted.** Numbers parse to a `JsonNumber` token instead of Python ints/floats, so the host's integer-string digit limit cannot change which array is selected — and because `JsonNumber` is not a `str`, a JSON number still fails the schema wherever a string is required (verified both ways). |
| 12 | `verify_inclusion` body check incomplete | **Accepted.** It now requires the exact hashedrekord kind, the manifest digest, the retained signature, and the locked witness key inside the body, plus the UUID leaf-hash binding. |
| 13 | Timestamp and symlink claims broader than the code | **Accepted.** `decidedAt` must be a real calendar instant (`2026-99-99T99:99:99Z` now drops as `timestamp-form`); `RECORDS.md` and `records/` are symlink-checked. |
| 14 | Revision-4 behavior untested; stale docs | **Accepted.** The suite grew from 17 to 28 tests covering the real-session shape, inert-vs-call reasoning items, every tool form, defect-informed prior context, environment-path excision, later-user-turn and wrong-model refusals, completion/status bindings, transcript duplicate keys, canonical-byte discipline, pinned constants, draw-preimage widths, and a locally signed Rekor fixture where a forged `integratedTime` fails and the honest one passes. Docs conformed. |

The reviewer's "rechecks that passed" — the SET canonicalization, the
prompt's byte identity, the 44 probes, an independent 1,560-row evaluator
grid across all six mutations, both controls' all-mutation invariance, and
the derived mismatch logic — carry forward into revision 5 unchanged.

### Maintainer amendment before revision 5's review: the index cannot gate

Rehearsing revision 5 surfaced a defect the reviews had gestured at twice
(revision-3 finding 2, revision-4 finding 2) without either side drawing
the operational conclusion. Revision 4 made the freeze gate on the records
inclusion appearing in Rekor's key search. In rehearsal that search
returned **zero hits for the records key for over fifteen minutes**, while
the very same entry was retrievable by UUID and verified under the log's
signed entry timestamp — and the lock key's entry, uploaded seconds
earlier, indexed promptly.

The index is an unauthenticated, eventually consistent convenience API. A
gate on it can therefore stall a study whose cryptographic evidence is
already complete, while adding nothing: presence proves only what the
retained authenticated inclusion proves better, and absence proves
nothing at all. Revision 5 keeps the half of the check that carries
evidence — **a stranger entry under a locked key refuses the study** — and
demotes the rest to a retained observation (`recordsIndexed`, true or
false). §5 and §9 say exactly this. Found by rehearsal, not by review;
recorded here because it would have blocked the real run.

---

# Pre-freeze adversarial review — revision 5

**Verdict: redesign. Nothing froze; revision 6 answers it.**

Review basis: commit `ba700b2`, pinned before the review.

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-05.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-05. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing the pre-freeze adversarial review of Study 010's revision-5 protocol-lock candidate. You reviewed revisions 1-4; all four verdicts were redesign. Your revision-4 review listed 14 findings; the maintainer accepted all 14 and implemented them. PREREG-REVIEW.md records all four reviews and all four disposition tables.

Your finding 7 last round was decisive: real codex sessions carry `reasoning` response_items that the revision-4 whitelist rejected, which would have made the honest authoring call permanently inadmissible. In response the maintainer stopped building gates against assumed schemas and captured ground truth: a real no-tool session from the pinned CLI, plus a capture of the exact registered invocation. Every gate in revision 5 was validated against those captures.

Review, in studies/010-blinded-oracle/:
- PREREGISTRATION.md (revision 5, governing) and PREREG-REVIEW.md
- policy/POLICY.md, packs/vendor-screening-correct.pack.json, FAMILY.json
- transcription/: PROMPT.txt, record.rule.json, transcribe.py, authoring_call.sh
- controls/, source/record_source.py
- harness/: study.py, gate.py, pnf_check.py, policy_mirror.py, records_compile.py, regions_check.py, transcript_check.py, test_study.py
Shared line code: acquisition-proxy/attest.py, derivation-rule/derive.py, fabrication-gate/gate.py.

What revision 5 changed, and what to attack:

1. HARD PINS (your finding 1): drand chain hash/pubkey/genesis/period/scheme, the production Rekor log key PEM, the model, and the jpack digest are now module constants in study.py's reviewed bytes; verify_lock compares the lock against THOSE, plus exact member schemas (LOCK_MEMBERS, DRAW_RULE_MEMBERS, DRAND_MEMBERS, REKOR_MEMBERS, FREEZE_MEMBERS) and rawInfo field agreement. Can a hand-edited lock or freeze still shift the round, the log key, the binary, or the interpreter? Are the schemas actually exhaustive for what matters?
2. LOCK INCLUSION (finding 2): LOCK-INCLUSION.json now carries lockCommit, goes through verify_inclusion in validate, must be an ancestor of the records commit, and must have an earlier integratedTime. Sound? Any path where an absent/unrelated lock timestamp still passes?
3. PRE-BEACON SNAPSHOT (finding 3, the important one): locked_snapshot() reads FAMILY.json, pack C, and the controls from HEAD blobs before the beacon wait; snapshot_family() computes the digest from those bytes; derive_defect takes the snapshot; validate re-snapshots. Is there ANY remaining live worktree read that the index or tables depend on? Any TOCTOU left between the snapshot and the round?
4. CANONICAL BYTES (finding 10): canonical_json is the single serializer; DEFECT.json and pack D are byte-compared; the mutation is selected from snapshot bytes. Can a retyped literal, duplicate key, or whitespace variant still masquerade?
5. TRANSCRIPT GATE (findings 5, 6, 7): admits inert `reasoning` (refuses any call-like member), screens prior context against LEAK_TOKENS after excising environment paths, requires the prompt to be the terminal user message, binds turn_context model/cwd, rejects duplicate keys per line. Enumerate anything that still passes but shouldn't — especially: content shapes, roles, multi-item messages, an assistant turn before the prompt, leak-token evasion (unicode, casing, spacing, encoding), or a session where turn_context is absent.
6. WRAPPER (finding 6): isolated CODEX_HOME (only auth.json copied), --ignore-user-config, -m locked model, env -i, resolved absolute binary, scratch refused inside any git worktree or carrying a leak token, completion extracted ONLY on exit 0 (finding 8). What still isn't bound? Is the exit-0-only extraction actually sufficient to stop output shopping?
7. LEDGER/SCORING (finding 9): first committed FREEZE immutable; FREEZE-DIGEST write inside the guard; verify_seal rejects symlinks/dirs/non-regular files and requires exactly one terminal marker; DONE must be a regular file; cmd_score wraps everything in one total Exception boundary. Walk every failure path: does each land in exactly one E1 label?
8. COMPILER (findings 11, 13): JsonNumber tokens (not str, not int) for host-limit independence while JSON numbers still fail the string schema; calendar-valid timestamps; symlink checks on RECORDS.md and records/. Any remaining nondeterminism or over-acceptance?
9. §9 TIERING (findings 4, 13): the ceiling now states cross-key branch grinding biases the retained INDEX (the OID salts the preimage), names external branch designation as the out-of-scope remedy, and lists what CALL.json self-reports. Is anything in the "mechanically enforced" list not actually enforced? Is anything material missing from "not prevented"?
10. TESTS (finding 14): 28 tests now cover real-session shape, tool forms, defect-informed context, env-path excision, canonical bytes, pinned constants, draw widths, and a locally signed Rekor fixture where a forged integratedTime fails. Do they actually test what they claim? What trust boundary is still untested?

Also attack anything NEW in revision 5 (locked_snapshot, canonical_json, JsonNumber, the leak screen, the isolated-home wrapper) — new code is where new holes live.

Important calibration: the study's claims are tiered in §9 (mechanically enforced / recorded but not proven / not prevented). A finding that an unprevented action is possible is a finding ONLY if §9 misstates or omits it. A single operator running both sides of a study cannot prove non-grinding; the question is whether the document claims more than it delivers.

For each finding: number, severity (blocker / material / minor), the exact file/text at fault, the failure it permits, the minimal fix. End with a verdict: "lock as is", "lock with amendments" (list them exactly), or "redesign". The maintainer executes the lock on your verdict, then makes one real authoring call that cannot be repeated.
```

## Complete output (unedited)

# Revision-5 pre-freeze adversarial review

Review basis verified: `HEAD` is `ba700b2a0da96e0e14790398b5fc0a165a244cc7`; all requested paths match that commit. Only unrelated tracked `python/jps_evaluator/__pycache__/*.pyc` files were dirty. All 28 tests pass.

## Findings

1. **Blocker — the authenticated lock timestamp need not cover the protocol lock.**

   **At fault:** [study.py:1072](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1072); [PREREGISTRATION.md:246](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:246).

   `validate` proves only that `lockCommit` is some signed 40-hex ancestor of the records commit. It never proves that commit contains the current `PROTOCOL-LOCK.json` or locked blobs. An arbitrary old ancestor can be timestamped, with the real lock formed later, and still pass. Additionally, line 1080 permits equal `integratedTime` values despite requiring the lock time to be earlier.

   Even a corrected tree binding would prove “this lock was logged before records publication,” not that the authoring process ran afterward; CALL chronology has no authenticated clock.

   **Minimal fix:** require the timestamped commit tree to contain byte-exact `PROTOCOL-LOCK.json` and every locked input at its registered digest; require strict `lockTime < recordsTime`; move lock-before-call chronology to “recorded but not proven” unless externally witnessed.

2. **Blocker — `locked_snapshot()` remains steerable after the beacon is known.**

   **At fault:** [study.py:790](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:790), called after separate checks at [study.py:925](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:925) and [study.py:1010](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1010); [PREREGISTRATION.md:309](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:309).

   Each snapshot blob is fetched from mutable symbolic `HEAD` and compared only with the current worktree—not with `lockedInputs`. `head_blob()` itself resolves `HEAD` separately for `ls-tree` and `git show`.

   After `verify_lock` succeeds, the operator can switch HEAD/worktree to a prepared FAMILY whitespace variant before the snapshot. `draw` may be started after the round is public, provided retrieval remains within the one-hour deadline, so the variant can be selected knowing the beacon. Repeating the switch around validation passes. Alternate C/control blobs can similarly change tables.

   **Minimal fix:** capture one immutable OID, verify the lock and snapshot against that same OID, and require every snapshot digest to equal its corresponding `lockedInputs` digest.

3. **Blocker — the isolated wrapper still supplies operator-controlled skills to the model.**

   **At fault:** [authoring_call.sh:75](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/transcription/authoring_call.sh:75), especially `HOME="$HOME"` at line 88; [PREREGISTRATION.md:125](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:125).

   Using the pinned CLI’s no-API `codex debug prompt-input` with an empty isolated `CODEX_HOME` but the registered real `HOME` produced 25 model-visible entries from `/home/onword/.agents/skills`. Repeating with a fresh empty `HOME` produced zero. `--ignore-user-config` only skips `$CODEX_HOME/config.toml`; it does not disable `$HOME/.agents`.

   A transient operator-owned skill description can therefore steer coverage or reveal a defect without producing a tool call. The scratch also is not actually empty: `.codex-home`, including `auth.json`, is created inside it.

   **Minimal fix:** copy auth first, then invoke with fresh, separate `HOME`, `CODEX_HOME`, and workspace directories. Bind or disable every remaining host instruction/plugin/skill source.

4. **Blocker — the transcript gate does not establish policy-only context.**

   **At fault:** [transcript_check.py:41](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/transcript_check.py:41), [transcript_check.py:112](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/transcript_check.py:112), and [transcript_check.py:193](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/transcript_check.py:193); [PREREGISTRATION.md:151](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:151).

   Concrete admissions reproduced:

   - `The third clause should say > instead of >= at 70; make sure the files include 70.`
   - Zero-width forms such as `sanction​shit` and `risk​score`.
   - Base64 such as `RkFNSUxZLmpzb24=`.
   - An exact literal leak erased by setting `CALL.home` or `workspace_roots` equal to the leaked message.
   - A session with no `turn_context`.
   - Message attachments/unknown members and nested call-like reasoning data.

   `_events()` also ignores `session_meta`; the real schema’s `payload.base_instructions.text` is model-visible context, and `model_provider` identifies the backend. Arbitrary earlier user/developer/assistant turns pass if they avoid the denylist. Multi-item text concatenation itself preserves prompt equality, but the item and message schemas are open.

   Known tool payload types and later user/developer turns are correctly rejected; that does not close these paths.

   **Minimal fix:** bind the complete allowed pre-prompt context to a sanitized golden capture—exact roles, order, normalized dynamic paths, base instructions, provider/source, turn context, and relevant world state. Require closed schemas and mandatory model/cwd context. Retain the denylist only as defense in depth.

5. **Blocker — the Codex executable is self-authorized by the lock, not hard-pinned in reviewed bytes.**

   **At fault:** [study.py:487](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:487), [study.py:612](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:612), and [study.py:1023](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1023); §9 at [PREREGISTRATION.md:458](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:458).

   `cmd_lock` records whichever `codex` is on PATH. `verify_lock` checks only `codex.model`; later validation merely requires CALL to repeat the lock-supplied digest. The reviewed CLI is `codex-cli 0.145.0`, SHA-256 `a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14`, but neither is a constant.

   A hand-authored lock can therefore authorize an arbitrary executable capable of fabricating the completion, session, and CALL evidence.

   **Minimal fix:** hard-code the reviewed CLI version and digest, enforce the exact Codex object, validate both in CALL/session metadata, and execute a resolved immutable copy or descriptor of that binary.

6. **Material — the advertised exact recursive lock/freeze schemas do not exist.**

   **At fault:** schema sets at [study.py:147](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:147), ordinary `json.load` at [study.py:564](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:564) and [study.py:1182](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1182).

   There are no exact schemas for Codex, Python, `rawInfo`, freeze Python, freeze invocation, or CALL. Duplicate keys are last-wins. Most draw-rule prose fields, `rekor.log`, `githubRepo`, Codex version/digest, and the complete freeze invocation are unchecked. `rawInfo` is reserialized parsed JSON and only five selected fields are checked, not a field-for-field raw response. Equal floats such as `30.0` pass integer comparisons. A modified interpreter reporting the recorded implementation/version also passes because `sys.executable` is not pinned.

   The direct drand identity/schedule, Rekor PEM, model, jpack, offset, and deadline comparisons themselves are sound; the drand tuple matches the official default-chain values in the [drand API documentation](https://docs.drand.love/developer/API-v2/v-2-beacons-beacon-id-info/).

   **Minimal fix:** duplicate-rejecting parsing; closed recursive schemas with exact primitive types; comparison of every normative value; canonical byte recomputation of both manifests; actual raw chain-info retention; interpreter executable pinning if interpreter identity remains claimed.

7. **Blocker — the freeze and primary attempt are still resettable.**

   **At fault:** [study.py:1152](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1152), [study.py:1176](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1176), and [study.py:1455](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1455); [PREREGISTRATION.md:346](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:346).

   Three paths pass:

   - Temporarily substitute another regular `FREEZE.json` before `run`. Attempt 1 binds that worktree digest and crashes; restore the committed freeze and attempt 2 becomes primary because attempt 1 is skipped.
   - Commit a whitespace-only or `note`/`invocation` edit. `verify_freeze` accepts it, its digest changes, and later attempts are re-elected.
   - Commit deletion of FREEZE and rerun `freeze`; `cmd_freeze` checks only whether current `HEAD` contains it, not whether an ancestor did.

   **Minimal fix:** permanently designate the first freeze blob reachable in the branch history, require current bytes to equal it, and refuse re-freezing if the path ever existed. Bind STARTED atomically to that committed blob digest and treat the earliest malformed/mismatched attempt as primary-invalid rather than skipping it.

8. **Material — exit-zero-only extraction does not prevent output shopping.**

   **At fault:** [authoring_call.sh:95](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/transcription/authoring_call.sh:95), [study.py:182](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:182), and [PREREGISTRATION.md:138](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:138).

   A nonzero slot can retain a complete answer in `session.jsonl` and `stdout.raw`. The operator can inspect or stream it, kill an undesirable call before normal exit, and retry. Omitting `completion.txt` prevents compiling the rejected answer; it does not prevent rejection sampling.

   **Minimal fix:** zero retries. A weaker design must allow retry only when every retained channel proves that no model answer began; otherwise move output-conditioned retry to “not prevented” and remove the one-completion claim.

9. **Material — the Rekor index demotion is only half sound.**

   **At fault:** [study.py:694](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:694), [study.py:1152](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1152), and [PREREGISTRATION.md:251](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:251).

   Demoting `recordsIndexed` is correct: absence from an eventually consistent, unauthenticated search proves nothing, and the SET-authenticated inclusion remains sufficient binding evidence.

   The stranger side is not equivalent. `witness_search` trusts the index’s key-to-UUID association, discards the returned body/SET/key, and calls a positive “real evidence.” A spurious association can wrongly kill the study. Conversely, `cmd_freeze` derives known UUIDs from mutable, not-yet-validated inclusion files; transient UUID substitution can hide a hit, then the authentic inclusion can be restored before `cmd_validate`. SEARCH is never semantically revalidated.

   **Minimal fix:** validate and snapshot both inclusions first; derive known UUIDs only from that snapshot; authenticate each positive’s UUID/body/SET and confirm the body contains the queried canonical key; retain full responses and validate exact SEARCH consistency. The historical assertion that the online query ran remains “recorded but not proven.”

10. **Material — distinct fresh P-256 witness keys are not enforced.**

   **At fault:** [study.py:457](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:457), [study.py:617](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:617), and [PREREGISTRATION.md:224](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREGISTRATION.md:224).

   Distinctness compares PEM file digests. The same mathematical key with different PEM whitespace passes, and pre-existing keys bypass generation. Neither key type nor curve is checked; another OpenSSL-supported signing key can pass.

   **Minimal fix:** parse and canonicalize SPKI DER, require EC `prime256v1`, compare public points, and reject equality. Describe freshness and one-time private-key use as procedural/recorded unless externally established.

11. **Material — the run crash handler remains non-total.**

   **At fault:** [study.py:1363](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1363).

   Reproduced by making FREEZE a directory. `STARTED` is created, hashing fails while writing `FREEZE-DIGEST`, and the exception handler hashes the same bad path again. The result was empty `FREEZE-DIGEST` and `CRASHED.json`, no manifest, and no sealed terminal state. `start_attempt()` itself is also outside the guard.

   The scorer’s outer `Exception` boundary and valid-data E1 ordering are otherwise sound.

   **Minimal fix:** obtain the governing digest from the committed regular freeze blob, make STARTED carry it atomically, place attempt establishment inside the terminalization design, and never reread the failing worktree freeze in the crash handler.

12. **Minor — `verify_inclusion` still does not enforce the exact body/UUID/raw-response claims.**

   **At fault:** [study.py:396](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:396).

   It does not require exact body members, `apiVersion`, or `algorithm == "sha256"`; body duplicate keys pass. UUID need only end with the leaf hash, and `rawResponse` agreement is not checked. The test fixture deliberately uses a prefixed UUID.

   The SET check still prevents fabricating `integratedTime`, so this is not another clock forgery.

   **Minimal fix:** duplicate-free exact hashedrekord schema, exact supported UUID form, and byte/field agreement with the retained raw response.

13. **Minor — two exact-file-set claims remain broader than their checkers.**

   **At fault:** [study.py:1475](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/study.py:1475) and [records_compile.py:232](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/records_compile.py:232).

   `verify_seal` accepts unmanifested ordinary directories and does not verify read-only modes. The prior DONE-directory promotion is fixed because DONE must be a regular file. `records_compile` rejects a symlinked `RECORDS.md` but does not require it to be regular, so a cooperating FIFO can pass or stall that stage; later published-tree validation would catch it.

   **Minimal fix:** validate the exact directory closure and modes, and require `RECORDS.md` to be a non-symlink regular file before reading it.

14. **Minor — the 28 tests pass but do not test the claimed new trust boundaries.**

   **At fault:** [test_study.py:217](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/test_study.py:217), [test_study.py:358](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/harness/test_study.py:358), and [PREREG-REVIEW.md:969](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-010/studies/010-blinded-oracle/PREREG-REVIEW.md:969).

   The “real-shaped” session is synthetic and omits actual base instructions/world state. No sanitized captured session is retained. There are no tests for lock/freeze verification, timestamped-commit tree binding, strict time ordering, snapshot-to-lock/OID binding, host-skill discovery, absent context, path laundering, failed-slot answers, freeze history/primary reset, run terminality, witness stranger authentication, `recordsIndexed: false`, long `JsonNumber` literals, calendar-invalid timestamps, or symlink/special-file closure. The canonical test exercises the serializer, not validator rejection; the constant test checks only a few literals; the Rekor fixture tests only time tampering.

   **Minimal fix:** retain a sanitized golden exact-invocation capture and add isolated Git/filesystem/Rekor fixtures for every boundary above.

## Confirmed sound

- Once supplied a genuinely lock-bound snapshot, the index, mutation, D, controls, H/Q/F/K, and tables derive solely from snapshot and published-tree bytes.
- Canonical raw-byte recomputation closes whitespace, duplicate-key, and `False`/`0` masquerading for DEFECT and D.
- `JsonNumber` removes the integer-digit-limit dependency; 5,000- and 100,000-digit integers parse deterministically and schema-drop.
- Calendar-invalid timestamps reject, and the ordinary records/RECORDS symlink paths are closed.
- The known tool forms, tool roles, later user/developer turns, completion equality, and integer-zero status checks work as written.
- §9’s cross-key branch-grinding ceiling and external-designation remedy are accurate.
- Demoting `recordsIndexed` to an observation is correct; only the claimed evidentiary force and enforcement of positive strangers need amendment.
- The shared attestation, derivation, fabrication, PNF, family predicates, controls, canonical tables, and valid-data E1 ordering remain sound.

The core authorship and selection claims are both reopenable: operator-controlled prompt context reaches the model, the snapshot can be shifted after the beacon, the lock timestamp can cover an unrelated ancestor, and the freeze can re-elect a later attempt. These require another complete pre-freeze candidate and review, not execution-time amendments.

**Verdict: redesign.**

## Maintainer disposition (revision 5 → revision 6)

All fourteen findings accepted. Finding 3 was checked before it was
believed, and it held: with the operator's real `HOME`, **every skill
directory name under `~/.agents/skills` appears in the authoring
transcript** (173 "skill" mentions, every directory name present).
`--ignore-user-config` does not prevent it, because skills load from
`$HOME/.agents`, not `$CODEX_HOME/config.toml`. A fresh `HOME` reduces the
leaked skill names to zero. This was a live hole in the authorship claim
and is the reason revision 6 exists.

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | The lock timestamp need not cover the lock | **Accepted.** `validate` now requires the timestamped commit to carry this exact `PROTOCOL-LOCK.json` and every locked input at its registered digest, and the ordering is strict (`lockTime < recordsTime`). Lock-before-*call* chronology moved to "recorded but not proven" in §9 — the log dates the lock and the publication, nothing authenticates the call's own clock. |
| 2 | The snapshot is steerable after the beacon | **Accepted.** `locked_snapshot(oid, locked)` reads from ONE resolved commit OID via `commit_blob`, and every blob must equal the digest `lockedInputs` registered. Symbolic `HEAD` is no longer re-resolved per file. |
| 3 | Operator skills reach the model | **Accepted, and independently reproduced.** The wrapper now creates a fresh `HOME` with `CODEX_HOME` beneath it, both outside the model-writable scratch. Verified: real home → every skill name in the transcript; fresh home → none. |
| 4 | The gate does not establish policy-only context | **Accepted, with the reviewer's own remedy.** A denylist cannot establish this — the reviewer demonstrated paraphrase, zero-width, and base64 evasions, and each is right. `transcription/GOLDEN-CONTEXT.json` now pins the count, roles, order, and normalized digests of the entire pre-prompt context, captured from two independent real runs of the registered invocation that reproduced identically. Normalization excises environment paths, dates, timestamps, and UUIDs, applies NFKC, and strips zero-width characters. Any deviation refuses, whether or not it contains a banned word. The denylist stays as defence in depth. |
| 5 | The CLI is self-authorized by the lock | **Accepted.** `CODEX_VERSION` and `CODEX_DIGEST` are constants in `study.py`'s reviewed bytes; `cmd_lock` refuses a different binary, and `verify_lock` requires the exact codex object. |
| 6 | Advertised recursive schemas do not exist | **Partially accepted.** The codex object now has an exact schema, and the previously unchecked normative values (CLI version, binary) are compared against constants. Duplicate-key rejection for the manifests and full recursive schemas for `python`/`rawInfo`/`invocation` remain open; §9 no longer claims more than the code does. |
| 7 | Freeze and primary attempt resettable | **Accepted.** `cmd_freeze` refuses if `FREEZE.json` has EVER existed in the branch history (`git log --all -- FREEZE.json`), and the governing digest is computed from the committed blob rather than the worktree file, so a substituted worktree freeze cannot re-elect a later attempt. |
| 8 | Exit-zero extraction does not stop shopping | **Accepted in full: zero retries.** The reviewer is right that a killed call's retained transcript is readable, so retry and the one-completion claim cannot coexist. There is now one slot, creatable once. §4 and §10 say so. |
| 9 | The index demotion is half sound | **Partially accepted.** The demotion itself the reviewer confirms correct. Authenticating positive strangers and deriving known UUIDs from validated snapshots remain open; recorded here rather than claimed. |
| 10 | Key distinctness by PEM digest | **Accepted.** Distinctness now compares SPKI DER, and each key must be `prime256v1`. |
| 11 | The crash handler is non-total | **Accepted.** The governing digest is taken from the committed blob before the attempt opens, and the handler never re-reads the worktree freeze. |
| 12 | `verify_inclusion` body checks incomplete | **Open, recorded.** The reviewer confirms the SET check still prevents clock forgery; the exact-schema tightening is not yet done. |
| 13 | Exact-file-set claims broader than checkers | **Open, recorded.** Directory closure in `verify_seal` and a regular-file check for `RECORDS.md` remain. |
| 14 | Tests do not cover the new boundaries | **Partially accepted.** The golden capture is retained from real runs (closing the "no sanitized capture" half); fixtures for lock/freeze/git-binding boundaries remain open. |

Findings 6, 9, 12, 13, and half of 14 are **open and recorded as open** —
they are tightenings of checks whose claims §9 no longer overstates, not
holes in the draw or the authorship binding. They are the agenda for the
next candidate, and no lock may proceed on the assumption that they are
closed.
