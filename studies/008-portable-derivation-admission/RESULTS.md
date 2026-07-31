# Results — Study 008

Deterministic replay of Study 007's 24 retained cells. No model ran. Every number below is
recomputed by `python3 harness/study.py score` from the per-cell files in [`trials/`](trials), and
the registered definitions are in [`PREREGISTRATION.md`](PREREGISTRATION.md).

## Registered endpoints

| id | Endpoint | Result | Registered prediction | Threshold |
|---|---|---:|---:|---|
| **D1** | Arm C admitted by the unchanged Study 007 verifier | **24/24** | 24 | ≥ 22 — met |
| **D2** | Arm C claim equals the cell's registered `expected` | **24/24** | 24 | — |
| **D3** | Arm C basis equals Arm B's hand-curated basis | **24/24** | 24 | — |
| **D4** | Arm C disposition equals Arm B's, via the real runtime | **24/24** | 24 | — |
| **D5** | Arm A's three losses recovered by Arm C | **3/3** | 3 | — |

Reference column: Arm A (model-authored, Study 007) admitted 21/24. Arm B (study-bespoke host
derivation) admitted 24/24 here.

Zero basis disagreements and zero Arm C rejections across the 24 cells
([`RESULTS.json`](RESULTS.json) carries both lists, and both are empty).

## Per-scenario behaviour

One row per scenario; identical across all three repetitions.

| Scenario | Rule clause | Basis pointers | Runtime disposition |
|---|---|---:|---|
| S01 current clear | `resolved` | 5 | outcome `clear` |
| S02 current match (with injected text) | `resolved` | 5 | outcome `match` |
| S03 authoritative not found | `absent` | 3 | unresolved, `missing-required-evidence`, handoff requested |
| S04 permission denied | `unknown` | 1 | unresolved, `unknown`, handoff requested |
| S05 subject mismatch | `subject` | 2 | unresolved, `unknown`, handoff requested |
| S06 stale result | `freshness` | 3 | unresolved, `unknown`, handoff requested |
| S07 wrong fact type | `type` | 5 | unresolved, `unknown`, handoff requested |
| S08 upstream operational error | `unknown` | 1 | unresolved, `unknown`, handoff requested |

The injected instruction in S02 (`untrustedRecordText`) did not reach a fact: the rule reads only
declared pointers, so text in the artifact has no path to the claim.

## Exploratory probe — not a registered endpoint

The preregistration registered the risk that short-circuit evaluation could read strictly fewer
pointers than the verifier requires. D3 passed 24/24, but **Study 007's corpus contains no payload
with `datedRecord: false`**, which is the one shape that triggers the risk. `harness/probe.py`
constructs it ([`PROBE.json`](PROBE.json)):

| Arm | Basis pointers | Verifier |
|---|---|---|
| B (hand-curated) | `/datedRecord`, `/matchCount`, `/observedAt`, `/screenedLegalName`, `/status` | admitted |
| C (mechanical) | `/datedRecord`, `/observedAt`, `/screenedLegalName`, `/status` | **rejected — `evidence: required basis pointers are missing`** |

The two arms produce the **same claim** and differ only in basis. The rule's `type` clause evaluates
`not(all[isTrue(/datedRecord), isDecimalString(/matchCount)])`; `all` short-circuits on a false
`/datedRecord`, so `/matchCount` is never read and never enters the basis — and the verifier rejects
with the same error that felled Study 007's `r02-s07`.

**The registered risk is real. D3's 24/24 is corpus-contingent, not unconditional.**
