# Study 001 — Does representing a policy as a judgment pack change how reliably a model applies it?

A preregistered, three-arm experiment on a third-party benchmark. **No results yet.**

| | |
| --- | --- |
| Rationale | [ADR-0001](../../docs/adr/0001-evaluate-on-rulearena-first.md) — why RuleArena, what comes next, why run this at all |
| Preregistration | [PREREGISTRATION.md](PREREGISTRATION.md) — frozen at merge; hypotheses, primary endpoint, falsification conditions |
| Deviations | [DEVIATIONS.md](DEVIATIONS.md) |
| Substrate | [rulearena/](rulearena/) — third-party, MIT, pinned, fetched not vendored; attribution and upstream-contribution policy |
| Status | [PIPELINE-STATUS.md](PIPELINE-STATUS.md) — what runs today, what is stubbed, how to reproduce |

## The design in one table

| Arm | Policy representation | Facts |
| --- | --- | --- |
| A | The Collective Bargaining Agreement text verbatim in the prompt | identical |
| A′ | The pack's semantic content as prose in the prompt | identical |
| B | A judgment pack via `judgment-pack experimental evaluate` | identical |

Two model families (Claude, OpenAI Codex), k=5 trials, paired instances, judge-free scoring against
RuleArena's gold answers and its `relevant_rules` citation ground truth.

**A′ is the arm that matters.** Without it, a win for B confounds "structured representation" with
"a human spent hours disambiguating this policy."

## Three things stated up front, not in an appendix

1. **The abstention labels are ours by construction.** RuleArena has no "cannot decide" condition; we
   manufacture one by mechanically deleting a load-bearing fact ([pipeline/REDACTION.md](pipeline/REDACTION.md)).
2. **The format cannot compute.** Derived quantities come from a published deterministic preprocessor
   and go identically to every arm. This measures policy *representation*, not fact derivation.
3. **The evaluator is experimental and claims no conformance.** JPS 0.1.0-draft §3.4 forbids
   evaluator-conformance claims.

## Reproducing

```bash
rulearena/fetch.sh                 # clone the benchmark at the pinned commit
python pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts
python pipeline/derive.py   --facts pipeline/out/facts
python pipeline/redact.py   --facts pipeline/out/facts --out pipeline/out/twins --seed 20260727
python harness/run.py --arm B --backend mock --instances pipeline/out/twins --trials 1 --seed 1 --out results/smoke.jsonl
python harness/score.py results/*.jsonl
```
