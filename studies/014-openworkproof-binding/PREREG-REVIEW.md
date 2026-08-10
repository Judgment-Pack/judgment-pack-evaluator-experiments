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

## Round 2 — 2026-08-09

Reviewer: codex-cli 0.145.0 / gpt-5.6-sol / reasoning effort ultra / read-only sandbox.
Verdict: **freezable after listed fixes**. Verbatim record: `reviews/round-2/PROMPT.md`,
`reviews/round-2/REVIEW.md`. Part-1 tally: R1-1/-5/-7/-10/-12/-14 RESOLVED;
R1-2/-3/-6/-8/-9/-11/-13 PARTIALLY RESOLVED; R1-4 NOT RESOLVED. Every residual maps onto
a numbered round-2 finding and closes with it. The reviewer authored the holdout stratum:
`harness/MATRIX-HOLDOUT.json` landed **byte-for-byte** from the review output (8 cells,
h01–h08, attributed, never executed pre-freeze).

| # | Sev | Disposition | Action |
|---|---|---|---|
| R2-1 | BLOCKER | **Accepted.** The whole-study manifest could be regenerated to launder a drift, and several pins were unverified. | `PINS.json` gains `studyManifest.sha256`, `matrixHoldout.sha256` (both null until freeze — at freeze the manifest digest is pinned inside the registry the scorer already stamps into every attempt), plus an `installedPackageDigest` over the installed `openworkproof` package files, computed now and enforced always; the pack pin is enforced against the vendored bytes; `pin_problems()` covers all of them. |
| R2-2 | BLOCKER | **Accepted.** `--include-holdout` refused correctly but could never adjudicate. | Post-freeze holdout path implemented end to end: loads `MATRIX-HOLDOUT.json`, validates schema and id-disjointness, builds nothing pre-freeze, adjudicates `fixtures/holdout/<id>/` into a separate stratum section of the results (never merged into locked counts, holdout gates handled per-role). Holdout builder hooks for h01–h08 are implemented **unexecuted**; a preregistration rule records that a holdout construction upstream refuses to publish is a constructibility finding + NOT-ADJUDICATED, never a silent drop. |
| R2-3 | MAJOR | **Accepted.** `d18`'s construction text overstated its mechanism (cloned receipt, outer-only re-sign, nested-claim mismatch fires first). | Construction/note corrected to the true mechanism; a focused live-path retry-episode probe (rollback → start_retry → second read → second patch) is added to the upstream probes — its recorded outcome (publishable or dead end) settles before freeze whether a live-path `d18` variant exists; the registered cell is not changed on speculation. |
| R2-4 | MAJOR | **Accepted.** | Every JCS canonicalization error inside commitment parsing maps to `commitment-schema-invalid`; escaped lone surrogates are rejected as non-I-JSON; vector added. This is also what h02 registers. |
| R2-5 | MAJOR | **Accepted.** | Exact `{verdict, code}` pair validation before any normalization (unknown pair → NOT-ADJUDICABLE); competing-defect ordering fixtures per ordered check; the source-grep meta-test replaced with a vocabulary-derived assertion. |
| R2-6 | MAJOR | **Accepted.** | `ATTEMPT.json` written before PINS parsing; provenance hashing, freeze gates, and `write_outputs` inside the terminal catch; all output writes atomic (tmp + rename). |
| R2-7 | MAJOR | **Accepted.** | Grant-window probe rebuilt: instant inside the WorkOrder window but before a later `valid_from` on an internally consistent grant, so the grant-authority branch itself fires. |
| R2-8 | MINOR | **Accepted.** | `supportedExtensions` uniqueness enforced (SPEC §1 states set semantics explicitly); makes h03's registered expectation the implemented behavior. |
| R2-9 | MINOR | **Accepted.** | `e19` re-labeled `selective-keys` per the registry's own taxonomy. |

Round 3 asks: confirm the round-2 closures, confirm the holdout stratum landed verbatim
and unexecuted with a working (but refused) post-freeze path, and state what, if
anything, remains between this draft and a freeze-ready PR.
