# Results — Study 001, first execution of the prompt arms

Arms A and A′ had never been run against a real model beyond a
two-instance pilot, so the project's central claim — that representing a
policy as a judgment pack changes how reliably a model applies it — rested
on a design rather than a result. All three arms have now run over the
full corpus at k = 5.

**On the preregistered endpoint, the pack arm loses.** An earlier draft of
this document reported the opposite; it scored the wrong population and
was corrected by the post-run adversarial review
([`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md), five blockers). The
error and its correction are recorded in `DEVIATIONS.md` §2 rather than
silently fixed.

## Setup

| | |
| --- | --- |
| Instances | 432 twins (216 answerable, 216 redacted), byte-identical facts across arms |
| Trials | k = 5, all conditions; 2,160 rows per arm; 0 errors, parse-ok 1.000 |
| Arms | A (CBA text in prompt), A′ (pack prose in prompt), B (pack via evaluator) |
| Model | `gpt-5.6-sol` via Codex, arms A and A′ |
| Runtime | `judgment-pack 0.2.0`, arm B |
| Bootstrap | 2000 paired resamples, seed 20260806 |

## The registered primary endpoint — H1 — is **not supported**

§2 of the preregistration registers exactly one primary endpoint: **H1
measured as pass^k on answerable instances**, arm B against arm A, pooled
across both model families. On that population:

| Arm | pass^5 | 95% CI |
| --- | ---: | --- |
| A — policy text in the prompt | **0.727** | [0.667, 0.787] |
| A′ — pack prose in the prompt | **0.778** | [0.718, 0.833] |
| B — pack through the evaluator | 0.579 | [0.509, 0.644] |

**Δ pass^5, B − A = −0.148, 95% CI [−0.213, −0.088].** Exact two-sided
McNemar on the 56 discordant instances (12 favouring B, 44 favouring A):
**p = 2.09 × 10⁻⁵, favouring A.**

The result is **opposite in sign** to the hypothesis. §6 required B to
exceed A by at least 5 points with an interval excluding zero; B trails by
nearly 15 points with an interval excluding zero in A's favour.

**H5 is not supported either.** B − A′ = −0.199 [−0.255, −0.148]. §6 makes
the headline claim fail when B does not exceed A′, and it does not. A′
does exceed A on this endpoint (+0.051 [0.009, 0.093]) while their
accuracy difference is not distinguishable from zero.

**And the registered endpoint was never completed.** It is defined as
pooled across Claude and Codex. Only Codex ran, and `score.py` produces
separate `arm::backend::model` conditions with no cross-backend pooling
operation — so the pooled endpoint is not merely deviated but not
estimable from this execution. Everything above is a Codex-only deviated
analysis.

### What the earlier draft got wrong

It reported **B − A = +0.130** and "H1 passes". That number is
reproducible, but only by scoring **all 432 twins** — pooling the 216
answerable instances with the 216 manufactured-redaction ones. The
decomposition:

| Population | B − A, pass^5 |
| --- | ---: |
| Answerable (the registered population) | **−0.148** [−0.213, −0.088] |
| Redacted (manufactured abstention labels) | +0.407 [0.343, 0.472] |
| All twins (the unregistered composite) | +0.130 [0.076, 0.181] |

The manufactured stratum changes the sign. `score.py` intersects all
shared twin ids and never filters to `variant == "answerable"`; the
scorer does not enforce the registered population, and the author did not
either.

## Accuracy against RuleArena's own gold — H4 **not supported**

§5 defines accuracy as agreement with the benchmark's gold `answer`. On
answerable instances, against that gold:

| Arm | Accuracy | 
| --- | ---: |
| A | **0.781** |
| A′ | 0.778 |
| B | 0.579 |

**B − A = −0.202 [−0.262, −0.146].** The pack arm is about twenty points
worse on the benchmark's actual labels. The +0.100 reported earlier is
reproducible only after adding author-constructed abstention labels for
the redacted half.

## Why: the expressiveness gap, which is the real finding

**Arm B returns `cannot_decide` on 60 of 216 answerable instances**
because the benchmark omits the minimum-salary schedule the CBA needs
(`PIPELINE-STATUS.md` §7 G-1). Those 60 instances are *all* 300 of B's
false-escalation trials. The pack is not deciding wrongly on them; it
cannot decide at all, because a constant it requires does not exist
anywhere in the benchmark.

§6 of the preregistration anticipated exactly this: *"If the pack cannot
be authored to cover a usable fraction of instances at all, that is the
study's result and it is published as an expressiveness finding, not
quietly rescoped."* That is the finding. On the 156 answerable instances
the pack can decide, its accuracy is 80.1%; the endpoint loss is driven by
the 60 it cannot reach.

A second, undiagnosed error concentration (G-3): B calls **18 of 37**
gold-legal answerable instances illegal. The cause is unknown.

## Escalation — H2 **holds** on its registered criterion

| Arm | TP | FP | FN | TN | precision | recall | F1 | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 26 | 12 | 1054 | 1068 | 0.684 | 0.024 | 0.047 | [0.014, 0.087] |
| A′ | 67 | 51 | 1013 | 1029 | 0.568 | 0.062 | 0.112 | [0.062, 0.171] |
| B | 460 | 300 | 620 | 780 | 0.605 | 0.426 | **0.500** | [0.436, 0.561] |

Δ F1, B − A = +0.453; pair-clustered over the 216 source pairs the
interval is [0.397, 0.505]. H2 meets its registered F1 rule.

The cost §6 names explicitly is the false-escalation **rate**, and it is
large: **1.1% of answerable trials for A (12/1080) versus 27.8% for B
(300/1080)** — plus 26.7 points, a 25× rise. Of B's 92 redacted
abstentions, 60 were already abstentions on the answerable twin; only 32
of 216 pairs newly switched from a decision to an abstention.

So B's escalation advantage and its endpoint loss have **the same cause**:
it abstains on the 60 instances it cannot express. That is right behaviour
on the redacted twins and wrong behaviour on the answerable ones, and the
manufactured-label design rewards it for the former.

## Citation — H3 **fails**

| Arm | precision | recall | F1 | 95% CI |
| --- | ---: | ---: | ---: | --- |
| A | 0.780 | 0.217 | **0.302** | [0.284, 0.322] |
| A′ | 0.679 | 0.164 | 0.239 | [0.225, 0.253] |
| B | 0.597 | 0.117 | 0.186 | [0.174, 0.199] |

B − A = −0.116 [−0.142, −0.092]. The pack cites the benchmark's relevant
rules worse than either prompt arm.

## What this execution does and does not compare

- **Arm B's within-instance decision agreement is 1.0 by construction** —
  the evaluator is deterministic. So its pass^5 *equals* its accuracy
  (0.579), which removes B's repeat-variation penalty and structurally
  favours it on pass^k. It does **not** make pass^k 1.0, and it does not
  guarantee B wins: here B loses the endpoint anyway.
- **The design does not hold the decision mechanism fixed.** It compares a
  prompted language model against a deterministic evaluator executing a
  pack. Representation is not varied in isolation.
- **The pack does not do the arithmetic.** 124 `/facts/derived/*` values
  are supplied by a preprocessor, 13 of them legal characterisation rather
  than computation. Every arm received the identical derived block, so the
  comparison is even-handed, but the result is about the
  pack-plus-preprocessor pipeline, not the pack alone.
- **Escalation gold is ours by construction.** RuleArena has no "cannot
  decide" condition; the redaction operator manufactures one. 213 of 216
  pairs are classified strong and 3 weak, and only 90 redactions alter the
  derived block the evaluator consumes — on 126 pairs the inputs B sees
  are unchanged (G-4).
- **One model family, one benchmark, one policy domain, one pack author.**

## Reproduction note

Arm B reproduced the recorded 2026-07-27 result exactly — 235 `illegal`,
45 `legal`, 152 `cannot_decide`, 217/432 — from twins regenerated
byte-identically from the pinned benchmark commit.

## Deviations

`DEVIATIONS.md` records: one model family rather than two; arm B on
`judgment-pack 0.2.0`; the wrong-population error corrected here; the
preregistered McNemar test absent from `score.py` and computed by hand for
this document; and bootstrap resampling over twins rather than pair
clusters in the shipped scorer.
