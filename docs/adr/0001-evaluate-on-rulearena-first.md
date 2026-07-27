---
status: accepted
date: 2026-07-27
deciders: Brian Jin
---

# Run the first efficacy study on RuleArena, and treat τ-bench as the confirmatory second

## Context and problem statement

Everything established about the Judgment Pack Specification so far is **internal coherence**:
documents conform, diagnostics are self-sufficient, two independently written evaluators agree 13/13
on the RFC 0006 appendix, and agents can author and repair packs. None of it tests the project's
actual thesis — that an explicit, testable judgment layer beats putting a policy document in a
prompt. That claim has **zero evidence**, and no amount of further conformance work will produce
any: conformance and efficacy are different questions with different evidence standards.

The specification's own roadmap is stalled on precisely this. Stage 1 exit wants five substantive
*external* design reviews; Stage 2 wants ten *external* authors and an independent validator. There
are none of either. Adversarial AI review — which this project has used heavily and to real effect —
is exhausted as a source of new information: it can find defects in what we built, but it cannot
tell us whether anyone should adopt it. A working, honestly-reported result is what makes outside
attention possible.

So: run an experiment. The question this record answers is *on what*, and *why that and not the
alternatives*.

## Decision drivers

- **The extraction confound decides the design.** The JPS evaluator is a pure function over a
  *structured* facts document addressed by JSON Pointer. Any multi-turn substrate forces an LLM step
  that extracts facts from a conversation — and then a loss is extraction failure and a win is partly
  extraction quality. Neither is the thesis. A substrate whose instances are already structured lets
  every arm receive byte-identical inputs so the only manipulated variable is *how the policy is
  represented*.
- **Statistical power we can afford.** Repeated trials are what separate a result from an anecdote.
  A single-turn substrate makes ten trials per instance affordable; a multi-turn one with a simulated
  user costs one to two orders of magnitude more and adds simulator variance to control.
- **Auditability must be measured, not asserted.** "Arm B emits a trace, therefore it is more
  auditable" is definitional, and a reviewer will say so. We need third-party ground truth about
  *which rules govern each instance*.
- **We author the format and run the evaluation.** Every design choice must reduce, not increase,
  what a skeptical reader has to take on trust. Third-party instances, third-party policy text, and
  judge-free scoring all do that; self-built instances do the opposite.
- **Cross-family generalisation.** A result on one model family is a result about that model. Arms
  run on both Claude and OpenAI (Codex) so a finding is not an artifact of one vendor's instruction
  following.

## Considered options

Surveyed roughly forty public benchmarks and corpora across three families — agent policy-adherence,
decision-logic/rules conformance, and abstention/deferral. The serious candidates:

- **A. RuleArena** (ACL 2025, MIT) — 216 human-annotated NBA transaction-legality problems over 461
  lines of real Collective Bargaining Agreement text, plus airline and tax domains over verbatim
  published airline policy.
- **B. τ²/τ³-bench** (Sierra, MIT) — the field's accepted venue for policy-adherence claims: policy
  documents handed to the agent verbatim, `transfer_to_human` scored as a gold action, native
  `pass^k`, and a public leaderboard.
- **C. SPEC** (Stanford RegLab) — 250 real unemployment-insurance adjudication scenarios with a
  deliberate 44% decidable / 56% inconclusive split.
- **D. A self-built instance set** from a real policy document.
- **E. DMN TCK / Catala / OpenFisca** — legally-validated formalisms with machine-checkable cases.

## Decision outcome

**Chosen: A (RuleArena) for study 1, with B (τ-bench) pre-announced as the confirmatory study 2.**

RuleArena wins on the driver that dominates: its instances are **template-generated**, so the facts
document is derived by a deterministic parser with **no LLM anywhere in the extraction path**, and
the identical structured facts go to all three arms. Nothing else on the list offers that. It is
also single-turn (ten trials are affordable), scored by exact match rather than an LLM judge (which
removes an entire class of "the author's judge preferred the author's format" objection), and — the
reason the NBA slice specifically is the primary — every instance carries a `relevant_rules` list
naming which provisions govern it. That is objective, third-party **citation ground truth**, which
converts auditability from an assertion into a measurement.

**τ-bench is the necessary second study, not the first.** It is stronger where RuleArena is weakest
— its escalation gold is externally authored, whereas ours is constructed — but weaker where it
counts first: multi-turn means the extraction confound, and its cost forecloses the repeated trials
that make any result credible. It also has a published leaderboard against which our baseline arm can
be cross-checked, which is worth a great deal *once we have a pipeline worth pointing at it*.

**Rejected, with reasons kept short and on the record:** *C (SPEC)* is the closest published match to
the thesis anywhere and would remove the one axis we must construct — but the repository ships **no
licence** and withholds the adjudication guides its retrieval arm uses. We are writing to the authors;
a permissive answer promotes it to co-primary immediately. *D (self-built)* should be assumed worth
approximately nothing as evidence when the same party authors the format, the encoding, the instances,
and the labels; it has exactly one legitimate role, as a contributed corpus with named external
contributors, and that is not this study. *E* answers a different and cheaper question — can JPS
express what legally-validated formalisms express — and belongs in a separate short note, never mixed
into an LLM experiment. Also surveyed and rejected for study 1: SOP-Bench and CRMArena (non-commercial
licences; CRMArena additionally depends on live shared Salesforce orgs), ST-WebAgentBench, AgentBench,
WorkBench, ToolEmu, AgentHarm, LegalBench cherry-picks, HealthBench, the OPA/Gatekeeper libraries,
and the learning-to-defer corpora — each for a reason recorded in the study's related-work section,
because demonstrating that the space was surveyed pre-empts "why didn't you use X".

### What we accept by choosing this

- **The abstention labels are ours by construction.** RuleArena has no "cannot decide" condition, so
  we manufacture one by deleting a load-bearing fact. This is a real weakness and belongs in the
  report's abstract, not an appendix. It is mitigated by making the construction mechanical, seeded,
  published, and driven by the benchmark's own `relevant_rules` annotations rather than our judgment —
  the same move SQuAD 2.0, AbstentionBench, and HiL-Bench made before us. It is also the reason study
  2 exists.
- **A hard scope limit: the format cannot compute.** JPS compares facts; it has no arithmetic. Derived
  quantities (post-transaction team salary, apron comparisons) are produced once by a published
  deterministic preprocessor and handed identically to every arm. This study therefore measures
  **policy representation, not fact derivation** — stated plainly, up front, everywhere.
- **A null result is a real possibility and is acceptable.** Given who is publishing, a well-run null
  against a pre-committed falsification condition is worth more to this project than a marginal win
  that readers discount to zero.

## Consequences

- Good: the first empirical evidence about the format, on third-party data, with judge-free scoring
  and a baseline that can be cross-checked against published numbers.
- Good: it forces the expressiveness question into the open — encoding real regulatory text as packs
  is itself a finding, whatever the arms show.
- Bad: escalation, the axis the format is most differentiated on, rests on constructed labels until
  study 2 or a licence for SPEC.
- Bad: roughly five to seven weeks to a publishable study 1, and a further six to ten for study 2.
  This is the cost of evidence; the alternative is continuing to build unvalidated surface area.
- Neutral: the study lives in this repository, not in the specification (which owns no executables and
  must stay offline and keyless) and not in the runtime (which is the system under test — a study of
  the runtime hosted inside the runtime is the vendor-benchmark shape we are avoiding).

## What comes next, in order

1. **Study 1 — RuleArena NBA** (this record). Preregistration first, then packs, then runs.
2. **Study 2 — τ-bench airline + retail**, pre-announced here with its date, where escalation gold is
   externally authored and the baseline is leaderboard-checkable.
3. **SPEC**, promoted to co-primary if the authors grant a licence.
4. **A separate expressiveness note** reproducing decision-shaped DMN TCK cases — cheap, and it
   answers "can JPS say what DMN says" without touching the LLM question.
5. **The conformance evaluation corpus** (pack + facts + expected disposition) contributed upstream to
   the specification per RFC 0006's Conformance section — the durable normative artifact, distinct
   from any efficacy claim.

## More information

Substrate survey and publication-norms research conducted 2026-07-27. Publication plan: an evaluation
report plus a separately DOI'd contributed corpus — deliberately **not** a benchmark, and not a model
card, factsheet, system card, or leaderboard. See [`../../studies/001-policy-representation/PREREGISTRATION.md`](../../studies/001-policy-representation/PREREGISTRATION.md).
