# Study 015 — the judgment/staged-action boundary under a governed-agent platform

**Status: DRAFT. Nothing is frozen and nothing has run under a freeze.** Round 1 of
cross-vendor review returned **DO-NOT-FREEZE** with 7 blockers; every one is dispositioned
in [`PREREG-REVIEW.md`](PREREG-REVIEW.md) and the apparatus was rebuilt around them —
including withdrawing one of the study's own recorded findings that source verification
refuted. Anything executed before the freeze is harness validation under `pilots/`, labeled
as such, and supports no claim beyond "the machinery works".

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
six families — judgment-artifact forgery and carried-but-unchecked identity, the boundary
analysis's five semantic collapses (unresolved→rejected, unknown auto-applied, operational
failure retconned as epistemic unknown, approval-as-evidence, plus observation-as-evidence),
handoff dropped, not-applicable executed, binding integrity (reuse, argument drift,
stage-time and apply-time revision mismatch, target and action-kind substitution, unbound
execution), and the callback-versus-commit overclaim — plus 6 controls, 1 disclosed
demonstration (the `readOnlyHint` queue bypass, upstream's own documented tradeoff), and 1
descriptive boundary (the at-most-once ambiguous commit, which **no offline layer can
resolve** and which is published as exactly that).

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
consistent, the action it records is the one the registered map derives from the recorded
judgment, and the judgment itself recomputes.** It is not a claim that any effect physically
happened (the platform's `approved` state covers its callback returning; MCP delivery is
at-most-once), not a claim that the judgment is correct, and not a claim that a JPS
disposition authorizes anything — the disposition→action map is the adapter's contract,
never a platform capability. The store is unsigned because the platform signs nothing; a
party that rewrites the *entire* store coherently around a disposition the retained
inputs genuinely produce presents a history this ceremony accepts — the registered
ceiling, stated up front.

Neither system is modified. Cloudflare OS is consumed as a read-only clone at a pinned
commit with upstream's own lockfile (probes are bundled by the clone's own esbuild; the
one injected seam is an inert `cloudflare:workers` tracing stub on the observability
path); jpack as a pinned release binary. The registered deployment is the pinned **MCP
Portal** connector with `MCP_PORTAL_TRUST_ANNOTATIONS=true` — the only pinned connector
that can be `vetted`, and therefore the only one on which an auto-approvable write exists
at all — and every identifier in the fixtures is the shape that connector actually emits.
Every retained **ledger record and auto-approval rule** is held to the pinned server-side
`ActionRecord` and `AutoApproveTagRecord` by the clone's own TypeScript compiler (the
modeled gatekeeper-side store has no upstream type to be held to), and `adapter/SPEC.md`
§0a publishes a field-by-field provenance table saying, for every datum the ceremony reads,
whether stock Cloudflare OS retains it at all.

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
| [`PREREGISTRATION.md`](PREREGISTRATION.md) | The registered protocol (DRAFT until frozen by merge) |
| [`adapter/SPEC.md`](adapter/SPEC.md) | Retained-record model, commitment schema, ceremony, verdict codes, disposition→action map |
| [`adapter/commitment.py`](adapter/commitment.py) / [`adapter/verify.py`](adapter/verify.py) | Commitment construction; the three-layer ceremony |
| [`harness/MATRIX.json`](harness/MATRIX.json) | 27 registered cells (locked-replication stratum) |
| [`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) | 8 reviewer-authored holdout cells (constructed but never adjudicated pre-freeze; scorer refuses) |
| [`PREREG-REVIEW.md`](PREREG-REVIEW.md) | Round-1 dispositions: what changed and why |
| [`harness/PINS.json`](harness/PINS.json) | Every pin, enforced before adjudication |
| [`harness/score.py`](harness/score.py) | The only thing that publishes |
| [`harness/build_fixtures.py`](harness/build_fixtures.py) | One-time fixture construction (real evaluator runs; upstream identity functions) |
| [`harness/cf_runner.py`](harness/cf_runner.py) / [`probes/`](probes/) | The upstream layer: pinned platform functions, bundled by the clone's own esbuild |
| [`harness/typecheck.py`](harness/typecheck.py) | Every retained record held to the pinned server-side types; a scorer precondition |
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

# a full attempt (PILOT until the freeze fills the digests)
python harness/score.py --attempt-root /tmp/attempt
```
