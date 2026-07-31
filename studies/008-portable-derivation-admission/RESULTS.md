# Results — Study 008

Deterministic replay of Study 007's 24 retained cells. No model ran. Every number is recomputed by
`python3 harness/study.py score` from the per-cell files in [`trials/`](trials).

**Read the calibration section before the endpoint table.** The registered endpoints all hit their
predictions, but an adversarial review ([`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md)) established
that four of the five cannot fail once D1 passes, and that D1 itself is far weaker than the
preregistration assumed. The corrected reading is in [`ANALYSIS.md`](ANALYSIS.md).

## Registered endpoints

| id | Endpoint | Result | Predicted | What it actually tests |
|---|---|---:|---:|---|
| **D1** | Arm C admitted by the unchanged Study 007 verifier | 24/24 | 24 (≥22) | Arm C's claim equals `derive_payload`'s and its basis is a **superset** of `derive_payload`'s — see calibration |
| **D2** | Arm C claim equals the registered `expected` | 24/24 | 24 | Entailed by D1: Study 007 pins each cell's `expected` to `derive_payload`'s output |
| **D3** | Arm C basis equals Arm B's hand-curated basis | 24/24 | 24 | **The only endpoint with independent content** (equality, not superset) |
| **D4** | Arm C disposition equals Arm B's, via the real runtime | 24/24 | 24 | Runtime determinism: D1 forces both arms' runtime inputs byte-identical |
| **D5** | Arm A's three losses recovered by Arm C | 3/3 | 3 | Entailed by D1; Arm B recovers the same three |

Reference columns, both derived rather than transcribed: Arm A (model-authored, from Study 007's
`M2`) 21/24; Arm B (study-bespoke host derivation) 24/24.

## Calibration controls — the important table

Not registered endpoints. Added after the adversarial review, and they bound what D1 can mean.

| Control | Basis | Admitted |
|---|---|---:|
| **Wide** | Arm B's claim with an **un-derived kitchen-sink basis** (every top-level pointer) | **24/24** |
| **Short** | Arm B's claim with Arm B's basis **minus one pointer** | **0/24** |

The verifier's basis check is a superset test (`007 harness/study.py:499`). An entirely un-derived,
maximally generous pointer list is admitted just as readily as Arm C's derived one. **D1 therefore
supplies no evidence that a mechanically-derived basis is better than an authored one — it only
rules out lists that are too short.**

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

S02's injected `untrustedRecordText` reached no fact. That is true by construction (a rule reads only
declared pointers), not a measurement of injection resistance — no model was in the loop.

## Probe — the study's substantive finding

The preregistration registered the risk that short-circuit evaluation could read fewer pointers than
the verifier requires. D3 scored 24/24, but the corpus contains **no payload with
`datedRecord: false`**, the one shape that triggers it. `harness/probe.py` constructs it
([`PROBE.json`](PROBE.json)):

| Arm | Basis pointers | Verifier |
|---|---|---|
| B (hand-curated) | `/datedRecord`, `/matchCount`, `/observedAt`, `/screenedLegalName`, `/status` | admitted |
| C (mechanical) | `/datedRecord`, `/observedAt`, `/screenedLegalName`, `/status` | **rejected — `evidence: required basis pointers are missing`** |

Same claim; the envelopes differ only in `basisPointers`, and Arm B's admission on that identical
constructed store shows every other check passes. The rule's `type` clause evaluates
`not(all[isTrue(/datedRecord), isDecimalString(/matchCount)])`; `all` short-circuits on a false
`/datedRecord`, so `/matchCount` never enters the basis.

**D3's 24/24 is corpus-contingent.** The divergence was already recorded in the rule's own frozen
corpus (`derivation-rule/corpus/type-notdated.json`, committed before this preregistration), so the
probe's contribution is confirming that the **unchanged verifier rejects** that basis — not
discovering the divergence.
