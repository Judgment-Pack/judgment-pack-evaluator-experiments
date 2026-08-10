# Analysis — RQ3, the model-mediated Arm A

Executed under AMENDMENT-RQ3.md (registered by commit `9cb597d` before any
model call): codex-cli 0.145.0 (binary digest pinned), `gpt-5.6-sol`,
reasoning effort ultra, each call in an empty read-only working directory —
the model saw only the policy prose, the facts, the evidence availability,
the action map, and an opaque case handle. 63 calls (21 cases × 3
repetitions), zero transport failures, zero schema failures, all slots
retained. Machine-readable result: `RESULTS-RQ3.json`.

## What this does not establish

Everything the frozen preregistration and the amendment already exclude: no
efficacy claim, no model ranking, no accuracy claim (the endpoint is
agreement with the pinned evaluator, which is not an independent truth), no
generalization beyond these 21 cases, these prose renderings, one model at
one effort. The prose was authored by the maintainer; rendering fidelity was
a registered threat and, as reported below, it materialized in one field.

## Results

| Endpoint | rep 1 | rep 2 | rep 3 | pooled |
|---|---|---|---|---|
| Primary agreement (kind, outcomeId, reasons, handoff) | 20/21 | 21/21 | 21/21 | **62/63**, CP95 [0.9147, 0.9996] |
| Target agreement (secondary) | 20/21 | 20/21 | 20/21 | 60/63, CP95 [0.8671, 0.9901] |
| False approvals | 0 | 0 | 0 | **0/63** |
| Correct abstention (of 11) / correct handoff (of 8) | 11, 8 | 11, 8 | 11, 8 | perfect |
| Model failures | 0 | 0 | 0 | 0 |

Arm B reference: 21/21 by construction (it is the evaluator). No protected
action ever fired wrongly in either arm; the model abstained and routed
every blocked case correctly, including p02 (blocked with no configured
destination — the registered silent-approval risk) in all three repetitions.

## The two divergences, both on registered cells of prior interest

**f01 — the silent tie-break (1 of 63, the only primary disagreement).**
At the exact threshold, the policy's ordered rule and its exact-declaration
exemption both apply; the evaluator's disposition is `unresolved {conflict}`
— JPS Core forbids tie-breaking a conflict. In repetition 1 the model
resolved it anyway, to `outcome: exempt`, presumably by the familiar
more-specific-rule-wins heuristic; in repetitions 2 and 3 the same prompt
produced the correct conflict recognition. So the single disagreement in 63
trials is (a) exactly the failure class the determination contract exists to
prevent — a plausible, confident, silently tie-broken boundary decision —
and (b) nondeterministic across repetitions at fixed effort. The mapped
action stayed on the safe side (exempt maps to record, not execute), so no
false approval resulted; the divergence is visible only against the golden.

**f05 target — configured precision degrades through prose (3 of 3).**
The model's disposition was perfect in every repetition (`unresolved
{unknown}`, handoff requested). But the configured destination — the pack
says `{"kind": "queue", "name": "Fee review queue"}` — came back as
`{"kind": "queue", "name": "Fee review"}` all three times: the prose
"escalated to the Fee review queue" is genuinely ambiguous about where the
name ends and the kind begins. This is the registered rendering-fidelity
threat materializing, and it rhymes with holdout h02 from the deterministic
phase: the configured handoff target is the field that every non-structural
carrier degrades — the instance matrix doesn't project it (h02), and prose
doesn't preserve it (here). Structured configuration is load-bearing
precisely where routing is concerned.

## Reading

On these 21 well-formed cases a strong model at high effort agrees with the
deterministic evaluator almost always, never fires a protected action
wrongly, and abstains everywhere the policy blocks — and the two places it
diverged are the two places the study registered in advance as the sharp
edges: exact-boundary conflict semantics and configured-destination
precision. The divergences are small in count and precisely located, which
is the most useful shape a result like this can take: it says where prose
judgment is brittle (tie-breaks under rule conflict, nondeterministically;
configured names), not that it is generally unreliable — a claim 63 trials
could not support and this study does not make.
