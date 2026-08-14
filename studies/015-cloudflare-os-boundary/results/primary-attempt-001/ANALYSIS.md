# Analysis — Study 015, registered primary attempt

Written after the scorer published, over the frozen tree at `968a9f8`. The published record is
[`RESULTS.json`](RESULTS.json) (the scorer's own output, both strata),
[`DETECTION-MATRIX.md`](DETECTION-MATRIX.md) (every registered cell of both strata, nothing
excluded) and [`ATTEMPT.json`](ATTEMPT.json) (written before the pin registry was parsed). This
file recomputes nothing; where it and those disagree, those govern, and where it and
[`../../PREREGISTRATION.md`](../../PREREGISTRATION.md) disagree, the preregistration governs.

The attempt carries `attemptLabel: "REGISTERED"` and `includeHoldout: true`, and neither is a
choice made here: the label is `REGISTERED` only because `harness/PINS.json` carries a non-null
preregistration digest, and a `REGISTERED` attempt that omitted the holdout is refused
mechanically (`harness/score.py`; PREREGISTRATION §1a). Provenance is pinned in `RESULTS.json`:
the four protocol digests, the study manifest, the `jpack` binary, the clone commit
`b2a51b5426398c8353d9d4dd984bd525121ab5f2` with a clean tracked tree, the toolchain identities,
every probed file's digest, and `fixtureTypecheck: "clean"`.

## R1, at its registered width

**R1 holds.**

The decision rule is ordered and exhaustive over the locked stratum (§5). Step 1 is not reached:
zero locked cells are pipeline-invalid, the validity channel carries zero records, and no
freeze-integrity or pin mismatch fired. Step 2 is not reached: all six control-gate rows land as
registered — the positive control passes all three layers, the two `classifyTool` controls refuse
on the trust-tier and annotation branches, `neg-drain-skip` refuses on the replayed drainer, and
the two scorer-route layer-liveness controls refuse in the binding and replay layers. Step 3
applies: of the 19 endpoint cells, all 19 are adjudicated and **zero** diverge from the registered
per-layer expectation. `m01` (demonstration) and `m02` (descriptive) land as registered and count
toward nothing.

What that is worth is fixed in advance and is not enlarged here. R1's standing is exactly that of
a locked regression suite over behaviour the maintainer has already observed: expectations were
corrected freely against pilot observations *before* the freeze — every correction named in
[`../../DEVIATIONS.md`](../../DEVIATIONS.md) — so the registered run is a conformance replication,
falsifiable by regression and **never** readable as a prediction (§1a, and R1's own wording in
§1). Three further limits ride with it, restated once: the fixture builder and the binding
verifier share one commitment implementation (`adapter/commitment.py`), so the locked stratum has
no independent mutation oracle (§1a, §8, inherited knowingly from Study 014); no cell's detection
may be read as holding against a more capable adversary than its own `mutationConstraint` faced
(§4b); and a party who rewrites the entire unsigned retained store coherently presents a history
this ceremony accepts (§4b, the registered ceiling).

The upstream column is mostly `not-engaged` — 20 of 27 locked rows and 6 of 8 holdout rows — and
that is registered content rather than a result. `not-engaged` is a distinct outcome from `pass`
precisely so it cannot be read as platform endorsement (decision register D-1), the per-cell
`upstreamChecksReplayed` field registers in advance which pinned functions each construction
reaches, and R2's central claim is exactly this: for most semantic cells the platform's policy
functions have nothing to decide, because no field of theirs carries a disposition. The one
descriptive row makes the same point from the other side: `m02-ambiguous-commit` passes all three
layers, and the registered reading of that row is "no offline layer can prove commit", never "an
effect occurred" (§7; SPEC §5, report vocabulary).

## The holdout — the only prospective content

`RESULTS.json` reports the holdout as its own object with its own verdict: **`holdout
divergent`**, 8 cells adjudicated, **7 divergent**, `h01` concordant, zero pipeline-invalid, zero
validity records. Nothing in it enters R1's arithmetic — that guarantee is structural and a
harness test asserts it — and it is stated at exactly the width §1a registers, which is not a
claim that nothing in the holdout could have affected R1's publication.

The reviewer's own instruction governs the reading, and it is the reason seven divergences are not
seven errors: these expectations predict the **round-1 reviewed** apparatus and were never revised
to follow a fix. Five of them (`h02`–`h05`, `h08`) were authored as predicted blind spots that the
post-round-1 repairs were intended to close, and `h06`/`h07` were authored as the two unsoundness
directions of the drain replay (§1a; `PREREG-REVIEW.md`, "Holdout"). Only the mechanical schema
migration touched the authored file, which is preserved byte-for-byte at
`reviews/round-1/MATRIX-HOLDOUT.authored.json`.

| Cell | Authored expectation (upstream / binding / replay) | Observed | Direction | What moved it |
|---|---|---|---|---|
| `h01-clarify-bound-execution` | `not-engaged` / `fail:action-map-violation` / `pass` | as authored | concordant | nothing — the reviewed apparatus already refused it |
| `h02-approval-digest-laundered-as-artifact` | `not-engaged` / `pass` / `pass` | `fail:evidence-backing-invalid` | blind spot closed | round 1, finding 2 — retained artifacts and the preimage requirement |
| `h03-coherent-argument-substitution` | `not-engaged` / `pass` / `pass` | `fail:action-derivation-mismatch` | blind spot closed | round 1, finding 1 — the derivation oracle |
| `h04-coherent-target-and-kind-substitution` | `not-engaged` / `pass` / `pass` | `fail:commitment-schema-invalid`, replay `unavailable` | refused, at a gate | the §1 schema gate, on a literal set by round 2's scenario re-render — **not** the mechanism the cell targets |
| `h05-phantom-staged-report` | `not-engaged` / `pass` / `pass` | `fail:report-state-unsupported` | blind spot closed | round 1, finding 11 — closed predicates for every report state |
| `h06-autoapproval-rule-removed-after-apply` | `fail:drain-order-violation` / `pass` / `pass` | `pass` / `pass` / `pass` | **refusal withdrawn** | round 1, finding 4 — the stage-time witness (see below) |
| `h07-drain-final-state-erases-manual-gate` | `pass` / `pass` / `pass` | `fail:drain-order-violation` | blind spot closed | round 1, finding 4 — the queue rebuilt from the ledger's own timestamps |
| `h08-outcome-unknown-reported-applied` | `not-engaged` / `pass` / `pass` | `fail:report-state-unsupported` | blind spot closed | round 6, R6-2 — the retained-outcome compatibility matrix |

### Cell by cell

**`h01` — concordant.** The reviewer's clarify-with-bound-execution construction was already
refused by the reviewed apparatus and still is: the commitment carries an action object under a
non-executable disposition, which is `action-map-violation` (SPEC §5, binding step 9). It is one
of two cells the reviewer authored as a refusal rather than as a blind spot, and it is the only
cell of the eight where the authored 4-tuple and the observed 4-tuple agree.

**`h02` — a blind spot closed on one of its two halves, and the study registered the other half in
advance.** Observed `evidence-backing-invalid`: "backing for sponsor-endorsement names no retained
artifact — a backing digest with no preimage is an assertion, not lineage". The repair is round 1,
finding 2 (blocker): `evidence-artifacts.json` joined the retained-record model and
`evidence-backing-invalid` now requires a retained preimage that hashes to the committed digest
(`PREREG-REVIEW.md` round-1 row 2; decision register D-3; SPEC §1 `evidenceBacking`, §5 binding
step 7). The reviewer's note named two defects — "checks the artifact label and digest shape but
not existence or preimage" — and the repair closed **existence and preimage**, which is what the
frozen fixture trips: it carries a `sponsor-endorsement` backing digest computed over an approval
record's bytes and retains no artifact under that requirement id at all. It did **not** close the
laundering the cell's own name points at, and no reading of this divergence should suggest
otherwise: a bridge that retains an approval record's own bytes under an evidence requirement and
labels them an artifact passes every check here, and both §9 and SPEC §1 say so in those words.
What `evidenceBacking` establishes is retained-preimage consistency and nothing more.

**`h03` — a blind spot closed, and the cell that exercises the oracle.** Observed
`action-derivation-mismatch`, on `argumentsDigest`. The repair is round 1, finding 1 (blocker):
`derived_action` applies the §4 map to the retained judgment alone, the map names its target
explicitly so the derivation is possible at all, and the check runs ahead of the map and target
checks (`PREREG-REVIEW.md` round-1 row 1; decision register D-2; SPEC §1 "Derived members", §5
binding step 8). `h03` is the coherent rebuild in which every downstream record agrees with every
other — commitment, both binding points, staged call and approved ledger row all carry the
substituted arguments — and the refusal comes from outside that agreement, which is the registered
claim in §4b that a derivation oracle is what a coherent rebuild does not escape.

**`h04` — a divergence, but at a gate, and not on the mechanism the cell was authored against.**
Observed binding `commitment-schema-invalid`, detail "action.toolName is not the executable tool
literal"; observed replay `unavailable`, detail "commitment is not replayable: action.toolName is
not the executable tool literal". Three things have to be said plainly.

*What fired.* `commitment-schema-invalid` is a **gate**, not a numbered check: it is one of three
conditions that abort the binding layer before any check runs (SPEC §5, binding-layer preamble).
It fires because the frozen commitment's `action.toolName` is `other_create_work_item` where §1
registers the executable literal `tracker_create_work_item`
(`adapter/commitment.py:42`, `:489-490`).

*Why the fixture carries that name.* The literal is a product of round 2's scenario re-render,
which put every registered identifier at the shape the pinned portal's source defines, including
the `<upstream server id>_<tool>` wire form (DEVIATIONS, "Round-2 corrections"). The reviewer
authored `h04` against the round-1 scenario, whose registered tool was the bare
`create_work_item`, and the cell's forged second deployment was rendered at the post-round-2 shape
when the fixture was built (DEVIATIONS, round-5 decisions D1/D3). The authored expectations were
not touched, and the authored file is byte-preserved.

*What it does not show.* The reviewer's note targets a different mechanism: "target and
action-kind semantics are checked only for downstream self-consistency, not derived from the
unchanged facts or upstream scope rule". The check that would answer that is the derivation oracle
at binding step 8, and on this cell it **never ran**, because the gate aborts the layer ahead of
it. No claim is made here about what step 8 would have returned on `h04`. The cell that does put
a coherent rebuild in front of the oracle is `h03`, and it is the evidence for that proposition.
The replay outcome is downstream of the same gate and is likewise not a detection: `layer_replay`
validates the commitment before anything else and returns `unavailable` when it does not parse to
§1's schema (`adapter/verify.py:1875-1883`), and SPEC §5 registers `unavailable` as an apparatus
verdict — apparatus absent — never a detection. `h04` is honestly read as one refusal plus one
apparatus verdict that follows from it, not as two detections.

**`h05` — a blind spot closed, by round 1 rather than by the compatibility matrix.** Observed
`report-state-unsupported`: "the report claims execution state 'staged' with no staged call bound
to this commitment". The fixture retains `platform.json` and `ledger.json` as present files with
empty staged-call, action-record and effect arrays, and reports `staged` anyway. The clause that
fires is the first conjunct of the `staged` predicate — exactly one bound staged call — and that
predicate exists because of round 1, finding 11 (major), which found four of five report states
unchecked free text and gave every execution state a closed predicate over the retained store
(`PREREG-REVIEW.md` round-1 rows 1 and 11; SPEC §5 report vocabulary, which records that round 1
found only `effect-attested` correlated with anything). This is **not** the rounds 6–7
compatibility matrix. That matrix correlates the flattened connector-outcome scalar with the outer
lifecycle state and the report claim, and it is what refuses `h08`. Two cells return one verdict
code through two different registered repairs and two different clauses, and collapsing them would
overstate what the later work closed.

**`h06` — see below.**

**`h07` — a blind spot closed, in the upstream layer.** Observed `fail:drain-order-violation`:
"pass 1 on gatekeeper 1: the witness claims [2] were auto-applied, but replaying the pinned
drainer over the queue as it stood at 2026-08-01T00:32:00.000Z applies []". The registered change
that moved it is round 1, finding 4 (blocker) — the same repair that moved `h06`, in the opposite
direction. The queue for a witnessed pass is reconstructed from the ledger's **own immutable
timestamps** (`createdAt <= t`, not yet resolved at `t`) rather than from the store's final
states, which is sound because `appliedAt` is a resolution stamp written on both the approve and
the reject path and is never read as evidence of application (SPEC §5, upstream step 2;
`PREREG-REVIEW.md` round-1 row 4). In the frozen fixture the obstruction is ledger row 1 — the
manual `tracker_close_work_item` gate — whose resolution stamp is `00:50:00`, later than the
witness instant `00:32:00`, so it was not yet resolved at the pass and stays in the queue; the
pinned drainer applies nothing, and the witness's claim of one application is the divergence. The
reviewer predicted a reset-and-redrain over final state, in which that row's `rejected` end state
removes it and the pass replays clean — which is precisely what the study's own record calls the
false-negative direction. The boundary the exclusion turns on is registered independently:
DEVIATIONS C1 registers a record resolved before the witness instant as legitimate history rather
than a refusal, and C4 registers the boundary as strict `resolved < at`. Rounds 6 to 8 hardened
the same check without moving this cell — R6-4 (witnesses read before the early exit), R6-5 and
R7-3 (one instant grammar, spelled identically on both sides), R7-4 (the reverse accounting as one
list comparison), R8-3 (every identity a witness claims validated before anything sorts, keys or
replays on it) — and each of those rounds recorded a before/after snapshot over all 35 cells
showing zero drift.

**`h08` — a blind spot closed by the rounds 6–7 compatibility matrix.** Observed
`report-state-unsupported`, and the diagnostic names its own authority: "the report claims
execution state 'applied' while the bound staged call retains connector outcome 'outcome-unknown';
that state is supported only by committed (SPEC section 5, retained outcome compatibility)". The
repair is round 6, R6-2: the flattened `connectorOutcome` scalar, the admissible outer lifecycle
state and the admissible report claim are registered as one matrix derived from the pinned source
and enforced under the existing `ledger-lifecycle-invalid` and `report-state-unsupported` codes,
with no new verdict code (DEVIATIONS, "Round-6 fixes"; SPEC §5, *Retained outcome compatibility*).
Round 7's R7-1 grew the same table by adding `rejected` to the report's execution vocabulary; that
is not this cell's mechanism. Two procedural facts belong beside it: `h08`'s fixture was repaired
at the pre-freeze self-audit for a fidelity defect it shared with `m02` — it carried
`autoApprovable: false` on a tool the pinned `classifyTool` makes `true` — a construction repair
with the authored expectations untouched; and round 8 ruled that `h08`'s authored *note* must not
be edited even though it carries a phrase the study withdrew elsewhere, because it is reviewer
prose promised verbatim (DEVIATIONS, "Round-8 fixes").

## `h06` — the registered apparatus accepts what the reviewer expected refused

Authored: `upstream: fail:drain-order-violation`, `binding: pass`, `replay: pass`, combined
`fail`. Observed: `pass` / `pass` / `pass`, combined `pass`, with both pinned functions engaged
(`upstreamReplayed: ["classifyTool", "AutoApprovalDrainer"]`). This is the one cell where the
reviewer predicted a refusal and the frozen apparatus accepts, and it is reported here at the same
prominence as every refusal above. It is a divergence. It is not an expectation that was met.

**Verdict: the acceptance lands on a registered acceptance**, stated in SPEC and recorded in
DEVIATIONS and in the review ledger, and the divergence is therefore attributable to a documented
semantic choice made after the expectations were authored. The tracing, in full:

*The construction.* The mutation is confined to what the reviewer specified: the frozen
`platform.json` carries `autoApproveTags: []` — the matching rule removed from the retained final
snapshot — while the tool catalog, the approved ledger row with `autoApproved: true`, the staged
call, the commitment, the effect attestation and the report are unchanged. The store also retains
one drain witness for gatekeeper 1 at `2026-08-01T00:31:00.000Z`, `appliedActionIds: [1]`, whose
`rules` array carries the matching rule with its complete enabler tuple.

*What the ceremony reads.* The drain replay is seeded from the **witness's** rule set, not from the
retained final snapshot: `probes/ceremony.ts:546-548` puts `witness.rules` into the mock storage,
and no adjudicated check reads `platform.autoApproveTags` at all — its only other consumer in the
tree is the fixture typecheck, which holds retained rules to the pinned server-side
`AutoApproveTagRecord` and is a validity precondition rather than a detection
(`harness/typecheck.py:114`). So the cell's mutation edits a field the drain check does not
consult.

*Why that is the registered design.* SPEC §5, upstream step 2 registers it in the same sentence
that names this exact history: "The replay is against a **stage-time witness**, not a final
snapshot, because two facts make a final-snapshot replay unsound in both directions: an
auto-approval rule is hard-deleted with no tombstone when a user withdraws it (a lawful historical
apply would replay as a violation), and an obstruction that was pending at drain time may be
resolved later (an unlawful apply would replay clean)." The first clause is `h06`; the second is
`h07`. The change is round 1, finding 4, disposed in `PREREG-REVIEW.md` as "Fixed, with a sounder
design than proposed" with the rule set identified as the one drain input with no residue
(`overseer.ts:7762`). The reviewer's own authored note frames the expected refusal the same way —
"A legitimate historical approval becomes a replay failure because the ceremony uses current rule
state rather than stage-time state" — that is, as a **false positive of the reviewed apparatus**,
not as a detection the repaired apparatus lost. `h06` and `h07` are the two halves of one
mechanism, and one registered repair flipped both, in opposite directions, which is what the study
recorded in advance that it would do (`PREREG-REVIEW.md`, "Holdout": "`h06`/`h07` predict the drain
replay's two unsoundness directions").

*The equality boundary is load-bearing here and is separately registered.* The frozen row's
`appliedAt` is `2026-08-01T00:31:00.000Z` — exactly the witness instant. Under the registered
boundary the row therefore reads as not yet resolved at that instant and stays in the queue
(`pendingAt`, `probes/ceremony.ts:428-431`), the pinned drainer applies it, and the replay's `[1]`
equals the witness's `[1]`. Had the boundary been non-strict the row would have been excluded, the
replay would have applied nothing, and this cell would have refused for an unrelated reason.
DEVIATIONS registers both halves as pre-freeze decisions: C1 (a record resolved before the witness
instant is registered as legitimate history, not refused) and C4 (the boundary is strict
`resolved < at`, with equality keeping the row in the queue, "which is the reading the registered
baseline relies on"). Neither was authored for this cell.

*The price of the acceptance, registered in the same place.* Because the rule set comes from the
witness, the ceremony has no view of rule-state withdrawal at all, and it cannot separate `h06`'s
lawful history from the laundering case the study registers beside it: the witness is
self-asserted, supplied by the same retained store under examination, unsigned and anchored
nowhere outside it, so "a writer who adds a matching rule to the witness launders an auto-approval
that no rule ever authorized, and no residue in stock platform state contradicts them" (SPEC §5,
upstream step 2, *What this verdict does and does not establish, normatively*; decision register
D-7). `drain-order-violation` is therefore a claim about consistency with a self-asserted witness
and never about historical lawfulness. The witness itself is instrumentation a retaining
deployment could keep and stock Cloudflare OS does not (SPEC §0a), so `h06`'s acceptance rests on
a modeled record. All of that was registered before the attempt ran; none of it is discovered
here.

*What `h06` therefore adds, stated exactly.* It is prospective evidence that the round-1 finding-4
repair does what it was registered to do on the false-positive direction, adjudicated once against
an expectation authored by another party against the apparatus before the repair. It is not
evidence that the acceptance is safe, and the study's registered position is that a store writer
with witness access is inside the ceiling either way.

## What this attempt does not show

PREREGISTRATION §9 is restated by reference, in full and unmodified: no policy truth and no fact
truth; no authorization from a judgment; no claim about Cloudflare OS runtime behaviour, since the
Durable Object, the submit gate, the apply chokepoint, sharing, observers and the agent loop never
execute; no claim that the platform performs no validation; no security audit and no endorsement;
no JPS conformance claim; no prospective-prediction claim for the locked stratum; no coverage
claim beyond the registered cells; no "zero trust"; and no claim that a detection here would have
*prevented* anything at runtime. The four §9 limits added at round 5 apply to every row above: no
source-reachability for retained histories, no effect causation, no closed inventory, no real
private connector record. Nothing in this file may be read as narrowing any of them.

Three limitations bear directly on how the two strata above should be weighed, and are named here
so a reader does not have to reconstruct them:

- **No independent mutation oracle in the locked stratum.** The fixture builder and the binding
  verifier share `adapter/commitment.py`, so an error common to both is invisible to R1 by
  construction. Registered in §1a and §8, inherited knowingly from Study 014, and unchanged by
  this attempt.
- **The holdout's *adjudication* is post-freeze; its per-layer outcomes were not novel to the
  maintainer.** The authored expectations are pre-freeze, reviewer-authored from static inspection,
  never revised, and asserted byte-equal to `reviews/round-1/MATRIX-HOLDOUT.authored.json` by a
  harness test; `--include-holdout` was refused mechanically while the preregistration digest was
  null. But the rounds 5, 6, 7 and 8 fix blocks each recorded a before/after snapshot of all three
  layer outcomes over **all 35 cells** — the holdout's eight included — by direct layer calls, to
  show those repairs moved nothing. The study registered exactly this qualification in advance:
  the pre-freeze refusal "guards the official publication route… it is not a claim that no one
  could invoke a layer function directly; it is a claim about what this study publishes" (§6).
  What the holdout buys is therefore stated narrowly: expectations authored by another party
  against a different apparatus, never revised to follow a fix, adjudicated once. It is not a
  blind prediction of outcomes the maintainer had never computed.
- **`not-engaged` is not endorsement, and a green row is not a proof of effect.** Twenty-six of
  the thirty-five adjudicated rows carry `not-engaged` at the upstream layer, which the registry
  registered cell by cell in advance; `m02`'s all-pass row means no offline layer can prove commit;
  and `m01` is a disclosed demonstration of the platform's own documented annotation-trust
  tradeoff. None of the three is a finding about the platform (decision register D-1; §7).

One residue of this document's own status, recorded rather than left implicit: `results/` is
outside the study manifest's covered set and outside the phrase guard's derived population, both
of which reach top-level documents and the apparatus but do not recurse into an attempt directory.
This file is therefore held to §9 by its author and by review, not by machinery.
