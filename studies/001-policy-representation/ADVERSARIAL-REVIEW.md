# Post-run adversarial review — Study 001

**Verdict: the reported result reversed.** Five blockers. The maintainer's
first write-up claimed the registered primary endpoint passed; it scored the
wrong population. Every finding was accepted and applied.

**Drafting model:** Anthropic `claude-fable-5` (Claude Code), 2026-08-06.
**Reviewing model:** OpenAI `gpt-5.6-sol` via codex-cli 0.145.0 (`codex exec`,
sandbox `workspace-write`, reasoning effort ultra), 2026-08-06. One run,
reproduced unedited below; no run discarded.

## Prompt (verbatim)

```
You are performing an adversarial review of a completed, preregistered experiment. It is the central efficacy study of the Judgment-Pack project: does representing a policy as a judgment pack change how reliably a model applies it, versus putting the policy in the prompt? Until today its prompt arms had never been run, so this is the first time the project's core claim has any evidence at all. It will be quoted. Your job is to find where the reported claims exceed what the retained data supports.

Read, in studies/001-policy-representation/:
- PREREGISTRATION.md — the registered hypotheses, the ONE primary endpoint, the falsification conditions in §6, the scope limits in §9
- RESULTS-FIRST-PROMPT-ARMS.md — the claims under review
- DEVIATIONS.md — including the two scoring hazards recorded today
- PIPELINE-STATUS.md — what the pipeline does and its known gaps (G-1..G-4)
- results/k5-report.md, results/k5-report-vs-aprime.md, and the raw rows in results/pilot-A-codex.jsonl, results/pilot-Aprime-codex.jsonl, results/pilot-B-runtime.jsonl
- harness/score.py, harness/run.py, harness/arms.py — the code that produced the numbers
- packs/, pipeline/ as needed

Verify from the bytes, not from the prose:

1. **Is H1 correctly computed and correctly reported?** pass^k is the registered primary endpoint. Re-derive B vs A from the raw rows. Is k really 5 for every condition? Does the scorer's k = min(trials across conditions) rule do what the report claims? Is the +0.130 with CI [0.076, 0.181] reproducible from the retained JSONL?
2. **Is the determinism caveat adequate?** The report states arm B's pass^k is 1.0 by construction and that H1 is therefore not a contest B can lose. Check that against the data — is B's pass^k actually equal to its accuracy on every instance? Is the caveat stated strongly enough, or does some other sentence in the document still trade on "the pack was more consistent"?
3. **Is the A′ finding handled honestly?** The report says A′ beats A on consistency (+0.044) while tying on accuracy, and that roughly a third of the B−A gap is recovered by prose alone. Check that arithmetic and that characterisation. Does H5 genuinely survive as §6 defines it?
4. **H2, H3, H4** — verify each against §6's falsification conditions. H3 is reported as failing; confirm it fails and that the report does not soften it. For H2, check whether the false-escalation rise is fairly presented.
5. **Paired-design integrity.** Do all three arms see byte-identical facts? Are the twins correctly paired, is the render policy honoured (no gold, no `raw`, no `redaction`, no `expected_decision` leaking into prompts), and does `facts_sha256` match across arms per row? A leak here would invalidate everything.
6. **Scoring correctness.** Read score.py: are the bootstrap CIs paired, is accuracy trial-averaged, is pass^k computed over the first k trials in trial order, are conditions compared only where paired? Any bug that would inflate B?
7. **Anything the report omits that a skeptic would demand.** In particular: the 124 derived fields supplied to the pack, the manufactured escalation gold, gaps G-1..G-4, one model family, one benchmark. Are the scope limits in §9 respected, or does some claim quietly exceed them?

For each finding: number, severity (blocker / material / minor), the exact file and text, what is wrong, and the minimal correction. A "blocker" means a reported claim is not supported and must be retracted or restated.

End with a verdict: "accept as reported", "accept with corrections" (list them exactly), or "retract". Corrections will be applied verbatim and this review recorded in full before the PR merges.
```

## Complete output (unedited)

The central claim reverses under the preregistered endpoint. The reported +0.130 is reproducible, but only after incorrectly mixing the 216 answerable instances with 216 manufactured-redaction instances.

| Population | A pass^5 | A′ pass^5 | B pass^5 | B−A | B−A′ |
|---|---:|---:|---:|---:|---:|
| Reported, all 432 twins | .373 | .417 | .502 | +.130 [.076, .181] | +.086 [.035, .132] |
| Registered, 216 answerable | .727 | .778 | .579 | **−.148 [−.213, −.088]** | **−.199 [−.255, −.148]** |

## Findings

1. **Blocker — H1 was computed on the wrong population.**

   Exact text: [PREREGISTRATION.md:37](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PREREGISTRATION.md:37) registers “H1 measured as pass^k **on answerable instances**.” [RESULTS-FIRST-PROMPT-ARMS.md:39](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:39) reports “B − A = +0.130” and “H1 passes.” [score.py:429](/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/harness/score.py:429) intersects all shared twin IDs but never filters to `variant == "answerable"`.

   From the retained bytes, answerable pass^5 counts are A 157/216, A′ 168/216, B 125/216. B−A is −0.148, CI [−0.213, −0.088]. Excluding the three manifest-weak pairs does not rescue it: −0.150 [−0.216, −0.085].

   The pooled +0.130 decomposes as −32 B−A successes on answerables plus +88 on redacted twins. The manufactured escalation stratum changes the sign.

   Minimal replacement:

   > On the preregistered answerable-only endpoint, in the available Codex-only execution, pass^5 was A 0.727 [0.667, 0.787], A′ 0.778 [0.718, 0.833], and B 0.579 [0.509, 0.644]. B−A was −0.148 [−0.213, −0.088]. The observed result is opposite to H1. The previously reported +0.130 was an unregistered all-twins composite driven by manufactured-redaction cases.

2. **Blocker — the registered pooled endpoint was never run.**

   Exact text: [PREREGISTRATION.md:37](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PREREGISTRATION.md:37) defines the primary endpoint as pooled across both model backends. The report nevertheless says “H1 passes,” while [RESULTS-FIRST-PROMPT-ARMS.md:118](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:118) correctly says a single-family result cannot stand in for that endpoint and “none is claimed.”

   Only Codex ran. Moreover, `score.py` produces separate `arm::backend::model` conditions and has no cross-backend pooling operation. The registered primary endpoint was therefore not merely deviated—it was not estimable by the retained execution or current scorer.

   Minimal correction:

   > Claude was not run, so the preregistered pooled H1 endpoint was not completed. All estimates reported here are Codex-only deviated analyses and cannot be called the registered pooled endpoint.

   Delete every unqualified “H1 passes,” “registered claim survives,” and “primary endpoint success” statement.

3. **Blocker — H5 and the headline fail in the executed answerable analysis.**

   Exact text: [RESULTS-FIRST-PROMPT-ARMS.md:44](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:44) says “H5 … also passes” and B−A′ = +0.086.

   Answerable-only B−A′ is **−0.199 [−0.255, −0.148]**. Under [PREREGISTRATION.md:100](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PREREGISTRATION.md:100), H5 and the headline fail when B does not exceed A′.

   A′ does outperform A on answerable pass^5: +0.051 [0.009, 0.093]. Their accuracy difference is −0.003 [−0.036, 0.030], which is “not distinguishable from zero,” not an established statistical tie. There is no positive B−A gap for prose to “recover,” so the “roughly a third” claim must be removed from the registered analysis.

   Minimal replacement:

   > On answerable instances, B trails A′ by 0.199 pass^5, 95% CI [0.148, 0.255] in A′’s favor. H5 is not supported in the executed family, and the §6 headline claim fails. A′ exceeds A by 0.051 [0.009, 0.093], while their accuracy difference is not distinguishable from zero.

4. **Blocker — “H4 holds” uses manufactured labels instead of the registered gold-accuracy metric.**

   Exact text: [PREREGISTRATION.md:84](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PREREGISTRATION.md:84) defines accuracy as agreement with gold `answer`. [score.py:162](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/harness/score.py:162) instead overwrites the target for every redacted twin with `cannot_decide`. [RESULTS-FIRST-PROMPT-ARMS.md:66](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:66) labels that all-twins composite H4.

   Native answerable accuracy is A .781, A′ .778, B .579. B−A is **−.202 [−.262, −.146]**. Thus B is about twenty points worse on RuleArena’s actual gold. The reported +.100 is reproducible only after adding manufactured abstention labels.

   Minimal replacement:

   > On RuleArena’s answerable gold, accuracy was A 0.781, A′ 0.778, and B 0.579; B−A was −0.202 [−0.262, −0.146]. H4 is not supported. The separate all-twins expected-decision composite was A 0.402 and B 0.502, but half of that composite uses author-constructed abstention labels.

5. **Blocker — the determinism caveat is factually wrong and does not cure the headline.**

   Exact text: [RESULTS-FIRST-PROMPT-ARMS.md:109](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:109) and [DEVIATIONS.md:34](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/DEVIATIONS.md:34) say “Arm B’s pass^k is 1.0 by construction” and that H1 is not a contest B can lose.

   Raw B decisions are invariant across all five trials for every instance. Therefore repeat agreement is 1.0, but pass^5 equals accuracy: .502 pooled and .579 answerable. It is not 1.0. Determinism also does not guarantee B wins; A beats B on the registered answerable endpoint.

   The +.130 does not measure only prompt inconsistency. In the incorrect all-twins composite, +.100 comes from the accuracy difference and about +.030 from A’s repeat penalty.

   The design also compares an LLM applying prompt text with a deterministic evaluator executing a pack; it does not hold the decision mechanism constant while varying representation.

   Minimal replacement:

   > Arm B’s within-instance decision agreement is 1.0 by construction, so its pass^5 equals its accuracy. This removes B’s repeat-variation penalty and structurally favors it on pass^5, but does not guarantee B>A. This execution compares a prompted model with a deterministic pack evaluator; it does not isolate representation while holding the decision mechanism fixed.

6. **Material — H2 passes its literal F1 rule, but the false-escalation rise is understated.**

   The retained 2×2 tables reproduce exactly:

   - A: TP 26, FP 12, FN 1054, TN 1068; F1 .047.
   - A′: 67, 51, 1013, 1029; F1 .112.
   - B: 460, 300, 620, 780; F1 .500.
   - B−A F1: +.453, reported CI [.382, .518].

   Therefore H2 meets the registered F1 falsification rule. But [RESULTS-FIRST-PROMPT-ARMS.md:86](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:86) gives counts and calls this a “precision cost,” whereas §6 explicitly names the false-escalation rate.

   That rate is B 300/1,080 = **27.8%**, versus A 12/1,080 = **1.1%**: +26.7 percentage points and 25×. Of B’s 92 redacted abstentions, 60 were already abstentions on the answerable twin; only 32/216 pairs changed from a decision to abstention.

   Minimal addition:

   > The false-escalation rate rose from 1.1% of answerable trials for A to 27.8% for B (+26.7 percentage points; 25×). Sixty of B’s 92 redacted abstentions were also abstentions on the answerable twin; 32 pairs newly switched to abstention. Despite that substantial cost, B’s escalation F1 remained 0.500 versus 0.047 for A, so H2 meets its registered F1 criterion within this manufactured-label design.

7. **Material — the redaction analysis includes weak pairs, omits G-4, and breaks twin clusters in its bootstrap.**

   Exact text: [RESULTS-FIRST-PROMPT-ARMS.md:72](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:72) says every redacted twin has a load-bearing fact deleted. The retained manifest classifies 213 pairs as strong and three as weak because deletion may not block the decision.

   [PIPELINE-STATUS.md:324](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PIPELINE-STATUS.md:324) records G-4: only 90/216 redactions alter the derived block consumed by B; 126 are functionally invisible to the evaluator. B’s decision actually changes on only 36 pairs.

   In addition, [score.py:466](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/harness/score.py:466) resamples 432 twin IDs independently rather than resampling 216 pair clusters. Pair-clustering changes the H2 delta CI to [.397, .505]; the conclusion remains positive.

   Minimal correction:

   > Of 216 redaction pairs, 213 were classified strong and three weak. Only 90 redactions changed the derived inputs consumed by B; on 126 pairs the evaluator’s consumed inputs were unchanged. H2 intervals are pair-clustered over source instances, with the three weak pairs excluded or reported as a sensitivity analysis.

8. **Material — required G-1 and G-3 limitations are omitted; G-2 is disclosed adequately.**

   [PIPELINE-STATUS.md:294](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PIPELINE-STATUS.md:294) explicitly requires G-1 to be reported as an expressiveness result: B cannot decide 60/216 answerable instances because the minimum-salary schedule is absent. Those 60 instances account for all 300 B false-escalation trials.

   [PIPELINE-STATUS.md:318](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PIPELINE-STATUS.md:318) records G-3: 18 false-illegal B verdicts remain undiagnosed. The retained denominator is 18/37 gold-legal answerables, not the stale “18 of 50” written there.

   By contrast, the report does disclose the 124 derived pointers, the 13 legal-characterization fields, and manufactured escalation labels. I independently counted 124 distinct pack pointers and confirmed all arms received the derived block identically. “Identical bytes” should replace the stronger assertion that this alone proves the comparison “fair”: the result is about the pack-plus-preprocessor pipeline.

   Minimal addition:

   > Expressiveness: B returned `cannot_decide` on 60/216 answerable cases because the benchmark omits the minimum-salary schedule; these are all 300 false-escalation trials. Error concentration: B called 18/37 gold-legal answerable instances illegal, and the cause remains undiagnosed. Results concern this pack-plus-preprocessor pipeline, including 13 derived fields that perform legal characterization.

9. **Minor — H3 fails honestly, but its table is stale k=1 output.**

   [RESULTS-FIRST-PROMPT-ARMS.md:94](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:94) does not match the retained k=5 report.

   Replace the table with:

   | Arm | precision | recall | F1 | 95% CI |
   |---|---:|---:|---:|---|
   | A | .780 | .217 | .302 | [.284, .322] |
   | A′ | .679 | .164 | .239 | [.225, .253] |
   | B | .597 | .117 | .186 | [.174, .199] |

   B−A remains −.116 [−.142, −.092]. H3 unequivocally fails, and the narrative does not soften that failure.

10. **Material — a nonzero B runtime exit can be accepted as success, and the retained rows cannot audit it.**

   The contract in `arm_b.py` says any nonzero exit is an engine refusal. But [arm_b.py:321](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/harness/arm_b.py:321) rejects nonzero only when stdout is empty. A nonzero process emitting parseable `status: "evaluated"` JSON is scored normally.

   B rows do not retain return code or stderr, so “0 engine refusals” cannot be established from the retained JSONL alone. No retained envelope shows another refusal signal, but this is still a path that could inflate B.

   Minimal correction: reject every `proc.returncode != 0` unconditionally, retain return code and stderr, and rerun the inexpensive deterministic B arm.

11. **Material — preregistered McNemar testing is absent.**

   [PREREGISTRATION.md:91](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/PREREGISTRATION.md:91) commits to paired bootstrap intervals and McNemar’s test. `score.py` explicitly implements no significance test beyond its bootstrap, and neither the report nor deviations records the omission.

   For answerable pass^5, discordants are 12 favoring B and 44 favoring A; exact two-sided McNemar/binomial p = 2.09×10⁻⁵, favoring A.

   Minimal correction: add that test or record and justify its omission as a dated deviation.

12. **Material — model-run provenance and leakage auditability are incomplete.**

   The JSONL records five calls per condition, but the listed “seeds” were not sent to Codex; [backends.py:75](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/harness/backends.py:75) says the CLI exposes neither seed nor temperature. The report does not give the requested model snapshot date, CLI version, token limit, sampling settings, prompt-revision counts, or baseline cross-check.

   The same backend acknowledges that Codex retains a shell tool. `run.py` discards the backend stdout/stderr transcript and retains only the final message, so the retained bytes cannot prove that no model-generated filesystem read occurred. This is not evidence of a leak; it is an auditability gap.

   Minimal correction: record these as deviations, disclose the unsupported seeds and remaining shell capability, and retain complete execution transcripts in any rerun.

13. **Minor — “Arm B was re-run from scratch” is not supported by the retained artifact.**

   [RESULTS-FIRST-PROMPT-ARMS.md:135](/tmp/claude-1000/-home/onword-repo-judgment-pack-judgment-pack-runtime/cc9299b1-e57f-4c94-aca2-643af0094105/scratchpad/wt-exp-001/studies/001-policy-representation/RESULTS-FIRST-PROMPT-ARMS.md:135) says “re-run from scratch.” The B JSONL has trial 1 at harness commit `c4a96c9` and trials 2–5 at `31d2255`, consistent with resume-and-append behavior. Relevant harness, pipeline, and pack files did not change, and outputs are identical, so metrics are unaffected.

   Minimal correction:

   > Arm B’s retained trial 1 was reused and trials 2–5 were appended; all five outputs were byte-identical per twin.

## Integrity checks that passed

- Each JSONL has exactly 2,160 rows: 432 twin IDs × trials 1–5, with no missing or duplicate trials. The scorer’s per-instance minimum therefore is genuinely k=5 everywhere.
- The published +.130 [.076, .181] reproduces exactly for the wrong all-432 population.
- Accuracy is trial-averaged per instance; pass^k uses the first five rows after trial sorting; comparisons use the shared condition intersection.
- Bootstrap resamples are paired across arms, though not clustered across twins as noted above.
- Every cross-arm `facts_sha256` matches, and every digest recomputes from the retained twin document.
- Reconstructed A/A′ prompt hashes match all retained rows.
- No `gold`, `raw`, `redaction`, `removed_value`, `expected_decision`, provenance, or related excluded field survives in any rendered facts document.
- All 216 source instances have exactly one correctly identified answerable and one redacted twin.
- No prompt leak is present in the reconstructed bytes.

The one-model, one-benchmark/domain, manufactured-gold, 124-field, and 13-characterization limitations are substantially disclosed. The report should additionally carry forward §9’s “single-turn only” and “one experimental evaluator implementation, not the standard” limits.

**Verdict: retract.**

## Maintainer disposition

Every finding accepted; none contested. Each load-bearing number was
independently recomputed from the retained rows before acceptance, and
each matched the reviewer's to three decimals: answerable pass^5 of
0.727 / 0.778 / 0.579, McNemar p = 2.09 × 10⁻⁵ favouring A, and
false-escalation rates of 1.1% versus 27.8%.

**The headline reversed.** The first write-up reported "H1 passes,
B − A = +0.130". The preregistration registers H1 as pass^k **on
answerable instances**; +0.130 is the all-432-twin composite, and the
manufactured-redaction stratum changes the sign. On the registered
population B trails A by 0.148. The corrected document leads with that.

This is the failure mode the study was built to prevent, committed by the
person who built it. `score.py` intersects all shared twin ids and never
filters to `variant == "answerable"` — the scorer does not enforce the
registered population and the author did not check that it had. No amount
of preregistration discipline substitutes for confirming that the number
you are about to publish was computed on the population you registered.

| # | Finding | Disposition |
| --- | --- | --- |
| 1 | H1 computed on the wrong population | **Accepted.** Corrected to the answerable-only endpoint with the reviewer's replacement text; the sign-flip decomposition is shown as a table so a reader can see exactly where +0.130 came from. |
| 2 | The registered pooled endpoint was never run | **Accepted.** Every unqualified "H1 passes" deleted. The document now states the endpoint is pooled across families, only Codex ran, and `score.py` has no cross-backend pooling — so it is not estimable from this execution, not merely deviated. |
| 3 | H5 and the headline fail in the executed analysis | **Accepted.** B − A′ = −0.199 [−0.255, −0.148] reported; the "roughly a third recovered by prose" claim is deleted, since there is no positive gap to recover. A′ − A = +0.051 [0.009, 0.093] on pass^5 with accuracy not distinguishable from zero. |
| 4 | "H4 holds" used manufactured labels | **Accepted.** Native-gold answerable accuracy reported: A 0.781, A′ 0.778, B 0.579; B − A = −0.202 [−0.262, −0.146]. H4 is not supported. |
| 5 | The determinism caveat was factually wrong | **Accepted.** B's pass^5 equals its *accuracy* (0.579), not 1.0; its within-instance agreement is 1.0. Restated with the reviewer's wording, including that determinism structurally favours B on pass^k without guaranteeing it wins — and here it loses. The document also now says the design does not hold the decision mechanism fixed. |
| 6 | The false-escalation rise was understated | **Accepted.** Reported as a rate: 1.1% → 27.8%, +26.7 points, 25×, with the 60/32 breakdown of which abstentions were newly caused by redaction. |
| 7 | Weak pairs, G-4, and twin-clustered bootstrap | **Accepted.** 213 strong / 3 weak stated; G-4 stated (only 90 of 216 redactions alter the derived block B consumes); the H2 interval is reported pair-clustered, [0.397, 0.505]. |
| 8 | G-1 and G-3 omitted | **Accepted, and promoted to its own section.** B returns `cannot_decide` on 60/216 answerable instances because the benchmark omits the minimum-salary schedule, and those 60 are all 300 false-escalation trials. §6 always said an expressiveness limit *is* the study's result; the corrected document treats it as the explanation for the endpoint loss. G-3's 18/37 gold-legal misclassification is stated as undiagnosed. |
| 9 | H3 table was stale k = 1 output | **Accepted.** Replaced with the k = 5 figures. |
| 10 | A nonzero arm-B exit can be scored as success | **Accepted as a recorded defect.** `arm_b.py` rejects a nonzero exit only when stdout is empty, and B rows retain neither return code nor stderr, so "0 engine refusals" is not auditable from the retained JSONL. No retained envelope shows a refusal signal. Fixing the check and re-running the cheap deterministic arm is filed as follow-up work rather than done under a result already corrected once. |
| 11 | Preregistered McNemar absent | **Accepted.** `score.py` implements no test beyond its bootstrap. McNemar was computed by hand for the primary endpoint (p = 2.09 × 10⁻⁵ favouring A) and both the omission and the manual computation are recorded here and in `DEVIATIONS.md`. |

### What survives

H2 meets its registered F1 criterion. The pipeline reproduced exactly. The
paired design held — the reviewer confirmed identical facts across arms
with no gold, `raw`, `redaction`, or `expected_decision` leakage. And the
study's most useful output is the one §6 predicted: an expressiveness
finding, that a pack cannot decide 28% of answerable instances because the
policy needs a constant the benchmark never states.
