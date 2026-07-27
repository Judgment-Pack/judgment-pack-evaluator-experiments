# RuleArena — third-party benchmark, attribution and provenance

This study's instances, policy text, and citation ground truth come from **RuleArena**, which is
**not our work**. We use it unmodified, pinned to one commit, and we do not redistribute it: the
[`fetch.sh`](fetch.sh) script clones it from the upstream repository at the pinned commit.

| | |
| --- | --- |
| Project | RuleArena: A Benchmark for Rule-Guided Reasoning with LLMs in Real-World Scenarios |
| Upstream | <https://github.com/skyriver-2000/RuleArena> |
| Paper | ACL 2025 · <https://arxiv.org/abs/2412.08972> |
| Pinned commit | `3b9e2256294644beca66732babc5e1055855a576` (see [`PINNED_COMMIT`](PINNED_COMMIT)) |
| License | MIT — verbatim copy in [`LICENSE-RuleArena`](LICENSE-RuleArena) |

## What we use, and what we changed

We use the **NBA transaction-legality** slice: `nba/reference_rules.txt` (461 lines of NBA
Collective Bargaining Agreement text) and `nba/annotated_problems/comp_{0,1,2}.json` (216
human-annotated problems; 81 / 89 / 46).

Each annotated problem carries a boolean `answer`, an `illegal_operation`, a `problematic_team`,
and — the reason we chose this benchmark — a `relevant_rules` list naming which rules govern that
instance. That list is objective, third-party citation ground truth, which lets us measure whether
a judgment pack cites the right rules instead of asserting auditability by fiat.

**We change nothing upstream.** Our pipeline reads the fetched files and writes derived artifacts
into `../pipeline/out/`. Two derived artifacts are ours, not RuleArena's, and are clearly labeled
as such wherever they appear:

1. **Parsed facts documents** — a deterministic, LLM-free re-expression of each problem's templated
   prose into structured JSON addressable by JSON Pointer. The parse is lossless with respect to
   the fields we consume and is verified against all 216 problems.
2. **Redacted twins** — instances with exactly one load-bearing fact removed, used to create the
   "cannot decide, escalate" condition RuleArena does not natively contain. RuleArena's authors did
   not design for abstention; the abstention labels in this study are **ours by construction**, and
   we say so in the report's abstract, not only in an appendix.

## Citing RuleArena

Any report from this study cites the RuleArena paper as the source of the benchmark, states the
pinned commit, and distinguishes RuleArena's contributions (policy text, instances, gold answers,
`relevant_rules`) from ours (facts parser, redaction operator, judgment packs, arms, metrics).

## Contributing corrections upstream

If our parser or pack authoring surfaces an error in RuleArena itself — a mis-annotated
`relevant_rules` entry, an unparseable template variant, an instance whose gold answer the CBA text
does not support — the correction goes **upstream first**, as an issue or pull request on
`skyriver-2000/RuleArena`, before we depend on any local workaround. Anything we cannot get
upstream is recorded in [`UPSTREAM-NOTES.md`](UPSTREAM-NOTES.md) with the exact instance ids
affected and how the study treats them, so a reader can tell our judgments apart from the
benchmark's.
