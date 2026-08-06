# Results — Study 001, first execution of the prompt arms

Arms A and A′ had never been run against a real model beyond a
two-instance pilot. Arm B's 57.9% therefore stood alone and
uninterpretable, and the project's central claim — that representing a
policy as a judgment pack changes how reliably a model applies it — rested
on a design rather than a result. All three arms have now been run over
the full corpus at k = 5.

**Read §"What this does not license" before quoting any number.** Two
limits are structural, not incidental: one model family, and arm B's
determinism.

## Setup

| | |
| --- | --- |
| Instances | 432 twins (216 pairs), byte-identical facts across arms |
| Trials | k = 5, all conditions |
| Rows | 2,160 per prompt arm, 2,160 for arm B; 0 errors, parse-ok 1.000, 0 engine refusals |
| Arms | A (CBA text in prompt), A′ (pack prose in prompt), B (pack via evaluator) |
| Model | `gpt-5.6-sol` via the Codex CLI backend, arms A and A′ |
| Runtime | `judgment-pack 0.2.0`, arm B |
| Bootstrap | 2000 paired resamples, seed 20260806 |

## Primary endpoint — H1, pass^k, B vs A

The preregistration names one primary endpoint chosen in advance: H1
measured as pass^k, comparing arm B against arm A. §6 commits it to fail
unless B exceeds A by **at least 5 percentage points with a confidence
interval excluding zero**.

| Arm | pass^k | 95% CI |
| --- | ---: | --- |
| A — policy text in the prompt | 0.373 | [0.326, 0.419] |
| A′ — pack prose in the prompt | 0.417 | [0.370, 0.465] |
| B — pack through the evaluator | **0.502** | [0.456, 0.549] |

**Δ pass^k, B − A = +0.130, 95% CI [0.076, 0.181], P(Δ>0) = 1.000.**

Thirteen percentage points, interval excluding zero. **H1 passes** against
the threshold registered before any prompt arm had been run.

**H5 — the honest control — also passes.** §6 commits the headline claim
to fail if B does not also exceed A′ by an interval excluding zero:
**Δ pass^k, B − A′ = +0.086, 95% CI [0.035, 0.132]**.

But k = 5 shows something the k = 1 pass could not, and it cuts against the
simplest reading: **A′ beats A on consistency**, Δ pass^k = +0.044,
95% CI [0.021, 0.069]. On accuracy the two prompt arms are statistically
tied (Δ = +0.018, CI [−0.003, 0.040]); on repeat-consistency the prose
restatement measurably helps. So part of the reliability gain *is*
attributable to the policy analysis, not the artifact — roughly a third of
the B − A gap is recovered by A′ alone. The registered claim survives
because B still exceeds A′ by an interval excluding zero, but "the pack
does it, the analysis does nothing" would be the wrong summary.

## Secondary endpoints

| Arm | Accuracy | 95% CI |
| --- | ---: | --- |
| A | 0.402 | [0.356, 0.450] |
| A′ | 0.420 | [0.373, 0.468] |
| B | **0.502** | [0.456, 0.549] |

Δ accuracy: B − A = +0.100 [0.047, 0.151]; B − A′ = +0.082 [0.031, 0.129].
**H4 holds** — B agrees with gold more often than A, which exceeds the
"at least as often" the hypothesis asked for.

### Escalation on redacted twins — H2

Each redacted twin has a load-bearing fact deleted, so the correct answer
is "cannot decide".

| Arm | correctly declined | falsely declined | missed | precision | recall | F1 | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 26 | 12 | 1054 | 0.684 | 0.024 | 0.047 | [0.014, 0.087] |
| A′ | 67 | 51 | 1013 | 0.568 | 0.062 | 0.112 | [0.062, 0.171] |
| B | 460 | 300 | 620 | 0.605 | **0.426** | **0.500** | [0.436, 0.561] |

This remains the largest gap in the study, and it is about declining to
answer. Given a case with a required fact removed, the prompt arms
answered anyway almost every time — arm A declined 26 times out of 1,080
opportunities. The pack declined 460.

H2 asked for that rise **without** a false-escalation rise that wipes out
the gain. B does decline falsely far more often in absolute terms (300 vs
12), and its precision (0.605) sits below A's (0.684). The F1 gain
(+0.453, CI [0.382, 0.518]) is nowhere near wiped out. **H2 holds**, with
the precision cost stated rather than buried.

### Citation quality — H3: **fails**

| Arm | precision | recall | F1 | 95% CI |
| --- | ---: | ---: | ---: | --- |
| A | 0.777 | 0.216 | **0.300** | [0.280, 0.321] |
| A′ | 0.682 | 0.161 | 0.237 | [0.221, 0.253] |
| B | 0.597 | 0.117 | 0.186 | [0.174, 0.199] |

H3 predicted B's cited rules would match RuleArena's `relevant_rules`
better than A's. They match **worse**: Δ citation F1, B − A = −0.116, CI
[−0.142, −0.092]. The pack reports the rules that actually fired, and that
set is smaller and narrower than the benchmark's notion of a relevant
rule. A registered hypothesis failed; §6 committed to publishing that, and
this is it.

## What this does not license

- **Arm B's pass^k is 1.0 by construction.** The evaluator is
  deterministic: every repeat of the same facts against the same pack
  returns the same disposition, so B's pass^k equals its accuracy exactly
  and cannot fall below it. H1 is therefore **not** a contest B could
  lose. What the +0.130 measures is how *inconsistent the prompt arms are*
  across repeats — arm A gives a different answer on 12.9% of instances it
  would otherwise have got right. That is the real finding, and stating it
  as "the pack was more consistent" would dress a structural property as
  an empirical victory.
- **One model family.** No Anthropic credential was available, so arms A
  and A′ ran on Codex only. The registered design pools across Claude and
  Codex; a single-family result cannot stand in for the pooled endpoint,
  and none is claimed.
- **One benchmark, one policy domain, one pack.** RuleArena's NBA
  collective bargaining agreement, encoded by one author.
- **The 124 derived fields.** The pack needs 124 `/facts/derived/*` values
  supplied to it because JPS has no arithmetic; 13 of those are legal
  characterisation rather than computation (`PIPELINE-STATUS.md` §7 G-2).
  Every arm received them identically, so the comparison is fair, but the
  pack arm is not doing that work and the accuracy figures should not be
  read as though it were.
- **Gold escalation labels are ours by construction.** RuleArena has no
  "cannot decide" condition; the redaction operator manufactures one.

## Reproduction note

Arm B was re-run from scratch and reproduced the recorded 2026-07-27
result exactly — 235 `illegal`, 45 `legal`, 152 `cannot_decide`, 217/432
correct — from twins regenerated byte-identically from the pinned
benchmark commit.

## Deviations

Recorded in `DEVIATIONS.md`: one model family rather than two; arm B on
`judgment-pack 0.2.0` because the current `jpack 0.15.0` refuses the
pack's declared `specVersion 0.1.0-draft` against its 0.2.0-draft
evaluator contract. The k = 1 first pass is superseded by this document.
