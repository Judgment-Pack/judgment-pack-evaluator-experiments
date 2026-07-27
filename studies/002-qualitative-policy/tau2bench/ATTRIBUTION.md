# τ-bench — third-party policy text, attribution and provenance

The policy encoded in this study is **not our work**. It is used unmodified, pinned to one commit,
and not redistributed here: fetch it from upstream.

| | |
| --- | --- |
| Project | τ-bench / τ²-bench — a benchmark for tool-agent-user interaction in real-world domains |
| Upstream | <https://github.com/sierra-research/tau2-bench> |
| Paper | <https://arxiv.org/abs/2506.07982> |
| Pinned commit | `1d244f5dca42944b67a379b44bfeb9f5748f189d` |
| License | MIT (Copyright Sierra Research) — verbatim copy in [`LICENSE-tau2-bench`](LICENSE-tau2-bench) |
| File used | `data/tau2/domains/airline/policy.md` (166 lines) |

## What we use, and what is ours

We use the **policy text only** — not the benchmark's tasks, gold actions, user simulator, or
scoring. This study measures what a judgment pack can express; it runs none of τ-bench's evaluation
and makes no claim about any model's score on it.

Ours, and clearly labeled as such: the judgment pack, the example facts and evidence documents, the
migration measurement, and the interpretation decisions.

## Fetching

```bash
git clone https://github.com/sierra-research/tau2-bench.git
git -C tau2-bench checkout 1d244f5dca42944b67a379b44bfeb9f5748f189d
# policy: tau2-bench/data/tau2/domains/airline/policy.md
```

## Upstream contribution

Nothing to report: no defect or ambiguity in the policy text was found that warranted an upstream
issue. Where the text was open to more than one reading, the choice is recorded in
[`../DECISIONS.md`](../DECISIONS.md) as our interpretation, not as a fault in the source.

If a later study finds one, it goes upstream first, per the repository's policy.
