# Pre-freeze cross-vendor review — rounds and dispositions

Reviewer identity, prompts, and verbatim outputs live under `reviews/round-N/`. This file
holds the maintainer dispositions. The preregistration cannot freeze while any round's
verdict stands unresolved.

## Round 1 — 2026-08-09

Reviewer: codex-cli 0.145.0 / gpt-5.6-sol / reasoning effort ultra / read-only sandbox.
Verdict: **not freezable as written** (4 BLOCKER, 10 MAJOR). Verbatim record:
`reviews/round-1/PROMPT.md`, `reviews/round-1/REVIEW.md`.

| # | Sev | Disposition | Action |
|---|---|---|---|
| R1-1 | BLOCKER | **Accepted.** The fixture chains bypassed OWP's canonical patch executor; a chain a real deployment could not have produced flatters the verifier. | Rebuild the flow through the upstream patch path with a real candidate workspace and canonical Git-style patch bytes; the executor-produced results become the fixture oracle. Every divergence that remains (if any) is recorded per-file. |
| R1-2 | BLOCKER | **Accepted.** Marker-based executing-receipt selection let a negative disposition execute by omitting the marker — the exact class of failure the study exists to catch, sitting in the study's own ceremony. | SPEC §5 reworked to structural discovery + exact-set totality over action-class receipts (null action → zero `owp.apply_patch` receipts; non-null → exactly one, marker-bound, tool/args matched; extras are violations). New cells: `c15` (manual-review + unbound execution), `d18` (approve + extra unbound execution). `c14` re-registered — under the totality rule its chain now fires binding *and* replay. |
| R1-3 | BLOCKER | **Accepted.** The 37 rows are a locked replication after the a04 correction; R1 as stated was postdictive. | Preregistration restructured into two strata: the registered matrix as **locked replication**, plus **reviewer-authored holdout cells** (`harness/MATRIX-HOLDOUT.json`, committed verbatim with attribution, never executed pre-freeze; the scorer mechanically refuses `--include-holdout` while the prereg is DRAFT). Round 2 invites the reviewer to author them, per the Study 013 pattern. |
| R1-4 | BLOCKER | **Accepted.** Freeze integrity was declarative. | `score.py` now hard-fails on any non-null pin mismatch (prereg/matrix/SPEC digests, jpack digest, interpreter version, installed-OWP version + pip-freeze digest), asserts the frozen cell-id set and schema, and a `harness/STUDY-MANIFEST.sha256` covers protocol, pins, adapter/harness code (including the entropy implementation), and fixture manifests. |
| R1-5 | MAJOR | **Accepted in part.** The differential claim for the second binding point is withdrawn rather than proven: two-point binding is re-described as defense-in-depth (SPEC, README). `e20` reworked to an execution-side mismatch so the request-level binding check is actually exercised. Full ablation arms are declined this round as scope — recorded here as an open limitation, revisitable if the reviewer holds the line. |
| R1-6 | MAJOR | **Accepted via relabel + probes.** `e21`/`f23`/`f25` are re-registered as generic upstream-corruption cells (their OWP-fail expectations stand); the named refusal mechanisms (window replay, exact-parent equality) get focused upstream probe tests in `harness/tests/` that invoke the pinned package's own functions directly. |
| R1-7 | MAJOR | **Accepted.** Replay now passes `supportedExtensions` through to the evaluator and cross-checks `evaluatorSpecVersion` against the replayed envelope. New cell `e23` (forged executable digest → `replay-executable-mismatch`). `supportedExtensions` materiality is bounded by the pack's requirements (baseline requires none) — recorded in the matrix note rather than pretended away. |
| R1-8 | MAJOR | **Accepted.** Commitment parsing is now strict (duplicate keys refused, UTF-8 required) and the check is byte-level: signed objective bytes and retained commitment bytes must equal the canonical JCS bytes exactly. Canonicalization vectors added to the tests. |
| R1-9 | MAJOR | **Accepted.** `registeredAbsences` is now a per-cell matrix field independent of expected verdicts; unknown/out-of-vocabulary verdicts make the attempt non-adjudicable rather than divergent; the scorer writes an attempt marker first and persists a terminal pipeline-invalid record on every failure path. |
| R1-10 | MAJOR | **Accepted.** `e18` leaves the matrix and becomes an analytic limitation in the preregistration (no fixture distinct from baseline can observe currency). `e22` stays as a descriptive row, relabeled "alternative valid WorkOrder remint accepted", excluded from R1 credit. |
| R1-11 | MAJOR | **Accepted.** Per-cell `attackerCapability` field (tamper / selective-keys / full-keys / none) added to the matrix; a threat-model section added to the preregistration distinguishing stale tampering, selective compromise, and coherent full reminting (the last is out of reach without an external anchor, stated plainly); README/claim language narrowed to receipted lineage — not truth, physical execution, or JPS-as-authorization. |
| R1-12 | MAJOR | **Accepted.** Missing `OWP_SOURCE`/`JPACK_BIN` now fails the determinism tests instead of skipping; the rebuild test rebuilds **all** cells and byte-compares against committed manifests; the scorer runs twice and its outputs are byte-compared; CI stages `OWP_SOURCE` and pins the exact interpreter (3.12.11); the builder/entropy code is inside `STUDY-MANIFEST.sha256`. |
| R1-13 | MAJOR | **Accepted.** Layers return structured `{verdict, code, detail}`; adjudication is on `code` alone; registered codes are exact (`replay-unavailable`, `replay-refused`); per-code reachability tests added (first-failure behavior demonstrated for every registered code). |
| R1-14 | MAJOR | **Accepted.** Per-cell `role` field (`endpoint` / `control-gate` / `demonstration` / `descriptive`); the decision rule evaluates control-gates first (a gate failure voids the attempt as inconclusive), R1 counts endpoint cells only, and every raw row is still published. |

Decision-register answers adopted as dispositioned above: **D-1** two-point binding kept
as defense-in-depth, differential claim withdrawn (R1-5). **D-2** map kept; totality
enforced structurally; `c15` added (R1-2). **D-3** fully consistent re-decision confirmed
as an analytic out-of-scope ceiling, not a green cell (R1-10). **D-4** the four controls
become validity gates outside R1; M28 stays descriptive (R1-14).

Round 2 asks: verify the round-1 dispositions landed as described, author the holdout
cells (R1-3), and re-issue a verdict.
