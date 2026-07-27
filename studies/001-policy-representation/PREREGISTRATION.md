# Preregistration — Study 001: does representing a policy as a judgment pack change how reliably a model applies it?

**Status: FROZEN on merge of the pull request that adds this file.** No arm has been run against a
real model at the time of writing. The commit that merges this document is the timestamp; everything
after it is either a result or a declared deviation. Deviations are appended to
[`DEVIATIONS.md`](DEVIATIONS.md) with a reason and a date — never by editing this file.

Rationale for the substrate and for what comes next:
[ADR-0001](../../docs/adr/0001-evaluate-on-rulearena-first.md).

---

## 1. The question

The Judgment Pack Specification claims that decisions an AI agent makes under a written policy should
be represented as an explicit, testable artifact rather than left to a policy document in a prompt.
Nothing has tested that. This study tests it on third-party data, with the format's own experimental
evaluator, and reports the answer whichever way it comes out.

**It does not test** whether JPS is the *best* such representation, whether it helps on multi-turn
agentic tasks, or whether it helps at deriving facts. See §9 for what a positive result would and
would not license.

## 2. Hypotheses

- **H1 (primary — reliability).** Arm B produces the same decision across repeated trials more often
  than Arm A on the same instances.
- **H2 (escalation).** On redacted instances, where a fact required by a governing rule has been
  removed, Arm B correctly declines to decide more often than Arm A **without** a corresponding rise
  in false escalation on the answerable twins.
- **H3 (citation).** Arm B's cited rules match RuleArena's `relevant_rules` better than Arm A's.
- **H4 (accuracy).** Arm B's decisions agree with gold at least as often as Arm A's.
- **H5 (the honest control).** Any advantage of B over A survives comparison with **A′** — the pack's
  semantic content rendered as prose in the prompt. If B beats A but ties A′, the finding is
  "careful policy analysis helps", not "judgment packs help", and the report says exactly that.

**Primary endpoint (one, chosen in advance): H1 measured as pass^k on answerable instances,
comparing Arm B against Arm A, pooled across both model backends.** Everything else is secondary and
will be labelled secondary in every table, abstract, and summary.

## 3. Design

Three arms × two model families, fully paired: every arm sees the **byte-identical facts document**
for every instance.

| Arm | Policy representation | Facts |
| --- | --- | --- |
| **A** | The CBA text (461 lines) verbatim in the prompt — the benchmark's own condition | identical |
| **A′** | The pack's semantic content rendered as prose in the prompt — same disambiguation work, no pack machinery | identical |
| **B** | A judgment pack consulted through `judgment-pack experimental evaluate` | identical |

Backends: **Anthropic (Claude)** and **OpenAI (Codex CLI)**. Exact model identifiers, snapshot dates,
temperature, max tokens, and any sampling parameters are recorded in every result row and reported.
Both families run every arm; a finding that holds on one family only is reported as such.

All arms are required to return the same strict output contract —
`{"decision": "legal"|"illegal"|"cannot_decide", "cited_rules": [...], "reason": "..."}` — and a
response that cannot be parsed into it is recorded as a parse failure, never coerced into a decision.

**Arm B failures count against arm B.** If the runtime refuses a pack, an input, or an evidence key,
that instance is scored as an arm-B failure. It is never silently skipped.

## 4. Instances

- Source: RuleArena NBA `annotated_problems/comp_{0,1,2}.json`, 216 problems, pinned commit
  `3b9e2256294644beca66732babc5e1055855a576`. Not vendored; fetched (see
  [`rulearena/ATTRIBUTION.md`](rulearena/ATTRIBUTION.md)).
- **Eligibility gate, declared now:** an instance enters the primary analysis only if (a) the
  deterministic parser reads it with no unparsed residue, and (b) every rule its gold
  `relevant_rules` names is within the pack's declared coverage. Both gates are computed and frozen
  **before** any model is called, and the excluded set is published with counts and reasons.
- **Redacted twins:** for every eligible instance, one paired twin with exactly one load-bearing fact
  removed, chosen by seeded RNG from a published rule→required-fact table, never by author judgment.
  Equal numbers of answerable and redacted instances, so an always-escalate strategy scores at chance
  and a never-escalate strategy likewise.
- **Trials:** k = 5 per (instance, arm, backend), fixed seeds recorded per trial.
- If cost forces a reduction, it is done by seeded random subsampling **declared before the runs
  begin** and reported with the seed — never by dropping instances after seeing results.

## 5. Metrics

All computed by [`harness/score.py`](harness/score.py) from raw JSONL logs, paired across arms.

- **pass^k** (primary): the fraction of instances where all k trials produced the correct decision.
- **Accuracy:** per-trial agreement with gold `answer`.
- **Escalation 2×2:** should-escalate (redacted) × did-escalate, reported as precision, recall, and
  F1. **Recall is never reported alone** — an always-escalate agent must look bad.
- **Citation precision / recall / F1** of returned `cited_rules` against gold `relevant_rules`.
- **Parse-failure and engine-refusal rates**, reported per arm.

Uncertainty: paired bootstrap confidence intervals (fixed seed, published) and McNemar's test for
paired binary outcomes. No metric is reported without an interval.

## 6. Falsification — what would make us say the format did not help

Committed in advance:

- **H1 fails** if arm B's pass^k does not exceed arm A's by at least 5 percentage points with a
  confidence interval excluding zero.
- **H5 fails, and the headline claim fails with it,** if B does not also exceed **A′** by an interval
  excluding zero. In that case the reported finding is that the *analysis*, not the *artifact*,
  carried the benefit.
- **H2 fails** if arm B's escalation F1 does not exceed arm A's, or if B's improvement in escalation
  recall is accompanied by a false-escalation rate on answerable twins that wipes out the F1 gain.
- If the pack cannot be authored to cover a usable fraction of instances at all, **that is the
  study's result** and it is published as an expressiveness finding, not quietly rescoped.

We commit to publishing the report if any of these fail.

## 7. Exposure and contamination disclosure

Honesty about what the authors saw before authoring, because pack-fitting is the insider form of
cherry-picking.

**Seen before the pack was authored:**
- `nba/reference_rules.txt` in full — intended and necessary.
- The **vocabulary of 61 `relevant_rules` identifiers and their frequency distribution**, used to
  align pack rule ids to the benchmark's citation taxonomy so H3 is measurable at all. This is a
  deliberate, disclosed choice: without id alignment there is no objective citation metric. It leaks
  which rule families are common; it does not leak any instance's answer.
- **Three `comp_0` instances' situation and operation strings**, viewed by the study author to
  determine whether the prose was template-generated and therefore deterministically parseable. The
  substrate choice depended on that check.
- **One gold answer** (`comp_0[0]`: `answer: true`, `illegal_operation: "A"`), visible incidentally in
  the same inspection.

**Not seen by the pack author:** the instances, their gold answers, or the answer distribution. The
pack-authoring agent was instructed to read the CBA text and the rule-name list only.

**Mitigations:** the pack is hashed (SHA-256, recorded in [`packs/`](packs/)) and committed **before**
the first model run; it is never iterated against results. Any change to the pack after the freeze
starts a new study id, and both results are reported.

**Benchmark contamination:** RuleArena is public since December 2024 and may be in training corpora.
This cuts *against* the pack arm if anything, since memorised answers help the prompt arms too. We
report a contamination check and publish canary GUIDs in every derived artifact.

## 8. Fairness commitments for the baseline

A weak baseline would make the result worthless, so:

- Arm A uses the benchmark's own policy text and prompt structure; we do not degrade it.
- Prompt-iteration budget is **symmetric and disclosed**: every arm receives the same number of
  prompt revisions, and the count is reported.
- Same model, same snapshot, same temperature, same token budget, same retry policy across arms.
- We cross-check our arm-A accuracy against RuleArena's published figures for a comparable model. **A
  materially lower arm-A number means we have a harness bug, not a finding**, and we chase it before
  reporting anything.

## 9. Scope limits — what a positive result would *not* license

- **The format cannot compute.** Derived quantities come from a published deterministic preprocessor
  and are given identically to all arms. This study measures **policy representation, not fact
  derivation**.
- **The abstention labels are ours.** RuleArena has no native abstention condition; see
  [`pipeline/REDACTION.md`](pipeline/REDACTION.md). Study 2 (τ-bench) exists to test the same
  hypothesis where escalation gold is externally authored.
- **Single-turn only.** Nothing here generalises to multi-turn agentic settings.
- **One domain.** NBA transaction legality is adversarially precise, rule-dense text; a result there
  does not transfer to vaguer policy without further study.
- **The evaluator is experimental.** JPS `0.1.0-draft` §3.4 forbids evaluator-conformance claims; this
  is a result about one implementation on one date, not about a standard.

## 10. What will be published, regardless of outcome

1. This preregistration, unedited, with any deviations appended separately.
2. The full report — including negative and null results.
3. The complete artifact set: packs and their hashes, the parser, the redaction script and seeds, all
   prompts, all raw JSONL logs, and the scoring code.
4. A separately DOI'd corpus with a datasheet and a contribution path.

Not published: a leaderboard, and not the word "benchmark" for any of it.
