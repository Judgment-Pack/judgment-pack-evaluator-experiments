# Study 015 — the judgment/staged-action boundary under a governed-agent platform

**Status: FROZEN at `7797a77 (pre-DCO-rebase 968a9f8)`, and the registered primary attempt has run.** Eleven rounds of
cross-vendor review preceded the freeze: rounds 1–10 returned **DO-NOT-FREEZE** and round 11
returned **freezable after listed fixes**, with that fix landed. The freeze was taken on that
verdict, and **round 12 ran only after it** — which supersedes the preregistration's own banner
and is recorded in [`DEVIATIONS.md`](DEVIATIONS.md) — returning *mergeable after listed fixes*,
whose four fixes are landed and recorded here. The apparatus was rebuilt around every finding of
every round, all dispositioned in [`PREREG-REVIEW.md`](PREREG-REVIEW.md) — including one of the
study's own findings, refuted by source verification. The preregistration is never edited again.

**R1 holds.** All 27 locked cells adjudicated, zero endpoint-divergent, zero validity records,
`attemptLabel: REGISTERED`, both strata published. R1's standing is that of a locked regression
suite over behaviour observed before the freeze: falsifiable by regression, never a prediction.

**The reviewer holdout diverges, 7 of 8 cells.** It carries the study's prospective content and
is reported with equal prominence — prospective in one exact respect: its expectations were
authored by another party against the reviewed apparatus, never revised, and adjudicated only
after the freeze, while the outcomes themselves were computed pre-freeze by direct layer calls.
Six divergences run one way — the reviewer predicted acceptance and the repaired apparatus
refuses, the intended primary result — and one runs the other way: `h06` predicted a refusal
the frozen apparatus does not make, on the stage-time witness the round-1 finding-4 repair
registered. Cell by cell, in [`ANALYSIS.md`](results/primary-attempt-001/ANALYSIS.md).

The rounds, one line each: round 5 rescoped the claims to what the apparatus is; round 6 found
the rescope's surfaces lagging and its replacement claim outrunning the code; round 7 found four
of round 6's repairs derived on one side of a symmetry and enforced only there; round 8 found
the withdrawn-claim class back for a third time and made it a test rather than another sweep;
round 9 walked around that test in four ways and caught the tree failing its own manifest gate;
round 10 found the licences inside it counting occurrences rather than identifying them; round
11 found the sentence about those fingerprints claiming more than they hold, and it was cut to
the mechanism's own terms ([`DEVIATIONS.md`](DEVIATIONS.md), "Round-5 rescope" through the
round-12 corrections). `pilots/` remains harness validation and supports no claim.

## What it is

An interoperability falsification study between two independently designed layers:

- **JPS** owns the judgment: given this exact pack and these exact inputs, what
  disposition follows (deterministic, byte-portable under Core §8.3).
- **Cloudflare OS** (Apache-2.0, pinned commit — an open governed-agent platform:
  Gatekeeper-mediated resources, an action approval queue, human and automatic approval,
  deferred effects, MCP tool-trust classification, an unsigned per-workspace action log) owns capability, staging, approval, and effect execution.
- A **thin adapter** (`adapter/SPEC.md`) owns exactly one thing: a *staged-action
  commitment* — the judgment digest tuple `{pack bytes, input bytes, evidence backing,
  canonical disposition, replay tuple}` bound to one exact staged platform action
  `{gatekeeper, resource, trust tier, tool, action-kind tag, arguments digest, stage-time
  resource revision}` — and a verification ceremony that recomputes everything
  from retained artifacts.

The study then tries to break the composition: 19 registered endpoint mutations across
five endpoint categories — A judgment-artifact forgery and carried-but-unchecked identity
(×4); S the boundary analysis's semantic collapses (unresolved→rejected, unknown
auto-applied, operational failure retconned as epistemic unknown, approval-as-evidence)
with handoff dropped and not-applicable executed completing the disposition space (×6);
O observation-as-evidence, the fifth collapse (×1); B binding integrity (reuse, argument
drift, stage-time and apply-time revision mismatch, target and action-kind substitution,
unbound execution) (×7); and D the callback-versus-commit overclaim (×1) — plus 6 controls,
1 disclosed demonstration (the `readOnlyHint` queue bypass, upstream's own documented
tradeoff), and 1 descriptive boundary (the at-most-once ambiguous commit, which **no
offline layer can resolve** and which is published as exactly that).

Three layers adjudicate every cell: **upstream** — the platform's own policy *functions*
(`classifyTool`, `AutoApprovalDrainer`), imported from the pinned clone and replayed
offline by this harness, never reimplemented; **binding** — the adapter ceremony, which
re-derives the authorized action from the judgment rather than trusting the commitment;
**replay** — the pinned evaluator recomputing the disposition from retained bytes. The
upstream layer is deliberately *not* called the platform's enforcement: the Durable Object
never runs, and when a construction gives those functions nothing to decide the verdict is
`not-engaged`, not `pass`. That distinction carries the central R2 fact cell by cell: the
platform's policy reads an author Boolean, a user rule, and a server's self-annotations —
no field of it carries a disposition, so a bridge that stages an action under an unresolved
judgment passes both offline-replayed policy functions without objection, and only the
binding layer can say why that is wrong. (The live Durable Object path never runs here, so
nothing in this study reports what the platform would do at runtime.)

What a green ceremony means, stated narrowly: **the retained store is internally
consistent — including the registered compatibility of each action row's lifecycle state,
the flattened connector outcome its staged call retains, and what the report claims of it
(`adapter/SPEC.md` §5) — the action it records is the one the registered map derives from
the recorded judgment, and the judgment itself recomputes.** It is not a claim that any effect physically
happened (the platform's `approved` state covers its callback returning; MCP delivery is
at-most-once), not a claim that the judgment is correct, and not a claim that a JPS
disposition authorizes anything — the disposition→action map is the adapter's contract,
never a platform capability. The store is unsigned because the platform signs nothing; a
party that rewrites the *entire* store coherently around a disposition the retained
inputs genuinely produce presents a history this ceremony accepts — the registered
ceiling, stated up front. Nor is a green ceremony a claim that the retained history is
source-reachable: the cells adjudicate selected, mostly synthetic constructions of the
retained store, and nothing here shows the pinned platform's own execution paths would
produce a given retained history. An attested effect is matched to a bound call's
identity, never shown to be caused by it; the inventories the checks close are over what
the store retains, not what the platform would have written; and a connector outcome in a
fixture is the retained flattened `connectorOutcome` scalar, never a recovered private
row (PREREGISTRATION §9).

Neither system is modified. Cloudflare OS is consumed as a read-only clone at a pinned
commit with upstream's own lockfile (probes are bundled by the clone's own esbuild; the
one injected seam is an inert `cloudflare:workers` tracing stub on the observability
path); jpack as a pinned release binary. The registered deployment is the pinned **MCP
Portal** connector with `MCP_PORTAL_TRUST_ANNOTATIONS=true` — the only pinned connector
that can be `vetted`, and therefore the only one on which an auto-approvable write exists
at all — and every identifier in the fixtures follows the shape the pinned connector's source
defines — a synthetic reconstruction from source, not a captured emission.
Every retained **ledger record and auto-approval rule** is held to the pinned server-side
`ActionRecord` and `AutoApproveTagRecord` by the clone's own TypeScript compiler (the
modeled gatekeeper-side store has no upstream type to be held to), and `adapter/SPEC.md`
§0a publishes a field-by-field provenance table saying, for every datum the ceremony reads,
whether stock Cloudflare OS retains it at all.

## Results

The registered primary attempt is published in full at
[`results/primary-attempt-001/`](results/primary-attempt-001/): `RESULTS.json` (the scorer's
own output), `DETECTION-MATRIX.md` (every cell of both strata, nothing excluded),
`ATTEMPT.json`, and [`ANALYSIS.md`](results/primary-attempt-001/ANALYSIS.md) — R1 at its
registered width, the eight holdout cells classified with citations, and what the attempt
does not show.

- **R1 holds** over the locked stratum: 19 endpoint cells and zero divergent, 6 control gates
  as registered, 0 pipeline-invalid cells and 0 validity records, provenance pinned and the
  fixture typecheck clean. It is a conformance replication, not a prediction.
- **The holdout is divergent, 7 of 8.** Six cells the reviewer authored as passes of the
  reviewed apparatus now refuse: a backing digest with no retained preimage, a coherent
  argument rebuild put in front of the derivation oracle, a phantom staged report, an
  outcome-unknown reported as applied, a drain obstruction that a final-state replay would
  have erased, and a forged target — that last one refused at the commitment schema gate
  rather than on the mechanism it was authored against, which `ANALYSIS.md` says in those
  words. The seventh, `h06`, runs the other way: the reviewer expected the ceremony to refuse
  a lawful auto-approval whose rule was withdrawn afterwards, and the frozen apparatus accepts
  it — on the stage-time witness registered for exactly that history, at the registered price
  that the witness is self-asserted.
- What each stratum is worth, and what neither establishes, is stated in `ANALYSIS.md` and
  governed by [`PREREGISTRATION.md`](PREREGISTRATION.md) §9.

## How it relates to what came before

- **Study 014** bound a judgment to an *execution receipt protocol* that ships its own
  offline verifier and signs everything. 015 is the same question against the opposite
  kind of neighbor: a platform with rich *live* controls — it validates its own RPC
  boundary, and exposes its log to authorized clients — but **no signed, complete,
  offline-verifiable record export**: no signature, no digest, and every semantic
  commitment an unconstrained string.
  The asymmetry is the finding: everything 014 could anchor into signed slots, 015's
  adapter must carry itself, and says so.
- **Study 013** asked whether an application *behaves* consistently with the judgment,
  live. 015, like 014, asks what a third party can later *prove* from retained bytes.
  No runtime-behavior claim is made here: the platform's Durable Object never runs.
- The boundary analysis this study operationalizes concluded that this platform class
  owns execution governance while JPS owns portable judgment semantics, and that a bridge
  must not collapse the one into the other. Every "must not" in that analysis is a
  registered cell here.

## Layout

| Path | What it is |
|---|---|
| [`PREREGISTRATION.md`](PREREGISTRATION.md) | The registered protocol — frozen and digest-pinned at `7797a77 (pre-DCO-rebase 968a9f8)`, never edited again; its own status line still says DRAFT and is corrected in [`DEVIATIONS.md`](DEVIATIONS.md) |
| [`adapter/SPEC.md`](adapter/SPEC.md) | Retained-record model, commitment schema, ceremony, verdict codes, disposition→action map — registered and digest-pinned at the same freeze, and likewise still self-labelled DRAFT |
| [`adapter/commitment.py`](adapter/commitment.py) / [`adapter/verify.py`](adapter/verify.py) | Commitment construction; the three-layer ceremony |
| [`harness/MATRIX.json`](harness/MATRIX.json) | 27 registered cells (locked-replication stratum) |
| [`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) | 8 reviewer-authored holdout cells, constructed before the freeze and published by the scorer only after it: `--include-holdout` was refused while the preregistration digest was null and is required now that it is set |
| [`PREREG-REVIEW.md`](PREREG-REVIEW.md) | Dispositions for all twelve review rounds — eleven pre-freeze, round 12 over the results package: what changed and why, the one living ledger |
| [`harness/PINS.json`](harness/PINS.json) | Every pin, each classified SCORER (compared before adjudication), CI, or DESCRIPTIVE |
| [`harness/score.py`](harness/score.py) | The only thing that publishes |
| [`harness/build_fixtures.py`](harness/build_fixtures.py) | One-time fixture construction (real evaluator runs; upstream identity functions) |
| [`harness/cf_runner.py`](harness/cf_runner.py) / [`probes/`](probes/) | The upstream layer: pinned platform functions, bundled by the clone's own esbuild |
| [`harness/typecheck.py`](harness/typecheck.py) | Every retained ledger record and auto-approval rule held to the pinned server-side types; a scorer precondition |
| [`harness/tests/`](harness/tests/) | Vocabulary sync, per-code reachability with first-failure ordering, refusals |
| [`fixtures/`](fixtures/) | Frozen cells: baseline + 26 mutations + 8 holdout, each manifested |
| [`pilots/`](pilots/) | Harness-validation runs (no claims) |
| [`reviews/`](reviews/) | Cross-vendor review rounds, verbatim |

## Running

```sh
# apparatus (see harness/PINS.json for every pin)
git clone https://github.com/cloudflare/cloudflare-os && git -C cloudflare-os checkout b2a51b5
cd cloudflare-os && corepack enable && pnpm install --frozen-lockfile --ignore-scripts && cd ..
export CFOS_SOURCE=$PWD/cloudflare-os
export JPACK_BIN=<pinned v0.16.0 jpack binary>       # digest-checked before every use

# the suite (offline, deterministic)
python -m pytest harness/tests -q

# a full attempt; past the freeze a REGISTERED attempt must adjudicate both strata
python harness/score.py --attempt-root /tmp/attempt --include-holdout
```
