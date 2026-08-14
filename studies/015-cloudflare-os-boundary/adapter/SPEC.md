# The staged-action commitment — binding a JPS judgment to a Cloudflare OS action queue

Status: DRAFT, registered by the Study 015 preregistration when frozen. This document is the
adapter's external contract: the retained-record model, the commitment schema, the binding
points, the disposition→action map, and the verification ceremony with its exact verdict codes
and ordering. The adapter modifies neither system; it composes them — and, unlike Study 014's
counterpart, one of the two systems ships **no offline verification of a retained record**, so
most of this contract is what the platform's own published TODO calls "richer action
descriptions plus a future policy engine", built adapter-side and said to be adapter-side.

Vocabulary: "JPS" is Judgment Pack Core 0.2.0-draft as implemented by the pinned jpack release;
"the platform" is Cloudflare OS at the pinned commit (`harness/PINS.json`) — specifically the
Gatekeeper/action-queue contract of `packages/workshop-shared/src/gatekeeper.ts`, the workspace
action-record model of `packages/workshop-backend/src/overseer.ts`, the auto-approval drain of
`packages/workshop-backend/src/auto-approval.ts`, and the MCP tool-trust policy of
`packages/mcp-shared/src/tools.ts`. "JCS" is RFC 8785 canonical JSON, computed by the `rfc8785`
package on the Python side — the canonicalization JPS Core §8.3 defines for dispositions.

## 0. The retained-record model (what an offline verifier is given)

The platform validates at its live RPC boundary — `ApprovalQueueImpl` carries `@validateRpc()`
(`overseer.ts:9428`), so `submitAction`'s arguments, including the declared structure of an
`ActionDescription`, are checked on arrival by validators generated from its own TypeScript
types at build time. What it ships no part of is **offline verification of a retained or
exported action record**: those validators are inline closures inside the built Worker, bound to
a live service method and structural only (every semantic commitment — which tag, which prose,
which gatekeeper — is an unconstrained string). The platform does expose its log to authorized
clients — `listActions()` (`workshop-shared/src/api.ts:1422`, implemented at
`overseer.ts:7548`) projects the stored records — but that projection is neither signed nor
digested, and it deliberately strips the fields that would let a holder join to a connector's
private store. What is absent is a **signed, complete, offline-verifiable record export**: a
third party handed a workspace's records has nothing from the platform with which to check them.
That last sentence is this study's load-bearing claim about the platform, and the only one.

The study therefore fixes a retained-record model: one directory per cell holding the exact
bytes an offline third party is assumed to have been handed.

| File | What it is | Whose shape |
|---|---|---|
| `pack.json` | The Judgment Pack evaluated | JPS (vendored spec corpus bytes) |
| `facts.json` | The §8.2 facts document | JPS |
| `evidence.json` | The §8.2 evidence-availability document | JPS |
| `evidence-artifacts.json` | The bytes retained under each evidence requirement id, base64 — the preimages a backing digest must actually have (retained-preimage consistency only; nothing here establishes that they *are* the captured evidence) | acquiring system (**instrumentation**) |
| `evaluation.json` | The pinned evaluator's compact `--format json` envelope | jpack |
| `commitment.json` | This SPEC's §1 object, canonical JCS bytes | adapter |
| `ledger.json` | The workspace action log: an ordered list of platform `ActionRecord` entries (Date fields as RFC 3339 strings) | platform (held to the pinned **server-side** `ActionRecord` by the clone's own compiler: `harness/typecheck.py`) |
| `platform.json` | The modeled platform-side store (see the provenance table below) | mixed; **mostly instrumentation** |
| `report.json` | The bridge's published claim: what was decided and what was done | adapter |
| `MANIFEST.sha256` | Exact-set digest manifest over the above | study |

### 0a. Provenance — what stock Cloudflare OS actually retains

Every datum the ceremony reads, and where a real deployment would get it. "OUTER" is the stock
workspace action log (`ActionRecord`, `overseer.ts:424`, projected to clients by
`actionRecordToLog`, `overseer.ts:610`); "MCP store" is the concrete connector's private action
store (`mcp-shared/src/action-store.ts`). This table is the study's answer to "does the
composition flatter the stock platform?" — it does not, and here is the ledger of exactly where
it does not.

| Datum | Stock OUTER log | Stock MCP store | Study's use |
|---|---|---|---|
| Tool name | **stock**: prose in `description`, exact in `description.actionKind.label`, and encoded in `.tag` (`tools.ts:94`) | yes, exact (`tool_name`) | bound structurally; a *canonical digest* over it is instrumentation |
| Call arguments | prose only, JSON-stringified, fence-defused, truncated at 4000 chars (`tools.ts:208-234`) | yes, exact (`args_json`) | `argumentsDigest` over canonical args — **instrumentation** |
| Resource revision at stage | not retained | not retained | **instrumentation** (some non-MCP connectors keep an analogue privately and destroy it at apply) |
| Resource revision at apply | not retained | not retained | **instrumentation** |
| Commitment carrier | none — no digest or signature over any record | none | **instrumentation**, wholly |
| Simulation basis | not retained; `awaitDecision` is an inverted advisory hint | not retained (MCP hardcodes `awaitDecision: true`) | **removed from the schema** — unreachable for this connector (§4b) |
| Connector outcome / retryability | not retained; the outer log has no failure state at all | yes (`error`, `retryable`), within a 100-record window | **instrumentation**, and flattened: one `connectorOutcome` scalar at the outer layer, never the private row, its retryability or its error detail |
| External effect attestation, **and the provenance its writer claims for it** | none — `approved` means an in-process call returned | first-party response only | **instrumentation**, wholly. The provenance is a closed union — `staged-call` (with the `gatekeeperId` and `action` of the call claimed to have produced the effect), `read-path`, or `out-of-band` — validated for shape at store load and read at step 15. It is a *claim by the store about itself*: unsigned, uncorroborated by any private connector result, and matched rather than shown to be true (PREREGISTRATION §9, "no effect causation") |
| Drain witness (stage-time rule set, pass identity, pass instant, applied ids, gatekeeper presence) | not retained; rules are hard-deleted with no tombstone (`overseer.ts:7762`) | n/a | **instrumentation, and self-asserted** — supplied by the same store under examination, so the verdict is consistency-with-the-witness, never historical lawfulness (§5) |
| Record timestamps (`createdAt`, `appliedAt`) | **yes**, stock; `appliedAt` is stamped on approve *and* reject | n/a | the queue reconstruction; never read as evidence of application |
| `autoApprovable`, action-kind tag/label | **yes**, stock, frozen in the persisted description | n/a | drain eligibility, read as-is |
| Catalog annotations and trust tier | **yes**, stock, but **untimestamped** | n/a | classification replay uses the *current* values; later drift could launder or falsely reject a historical classification — a registered limitation |
| Approval identity, auto-approval attribution | **yes**, stock (`resolvedBy`, `autoApproved`) | not retained | `autoApproved` selects the drain replay; `resolvedBy` is compared against the enabler the pinned drainer attributes |
| Action lifecycle state | **yes**, stock, three values | five values, divergent | read as-is |
| Observed read-path routing (which tool a read-path call named) | not retained — `ObservationDescription` carries only title, description and policy hints (`gatekeeper.ts:911`) | not retained structurally | **instrumentation**; it is what the upstream layer classifies for `m01` |
| Evidence artifacts | n/a | n/a | **instrumentation** (the acquiring system's, not the platform's) |

Two structural facts the table implies and the study relies on. First, **the join key is
withheld by the platform itself**: the gatekeeper's opaque `action` key (`overseer.ts:439`) is
stripped from the published log deliberately ("should NOT be provided to the client",
`overseer.ts:613`), so a holder of the published log alone cannot even join to a connector's
private store. `ledger.json` keeps the key because it models what the *server* retains, and the
typecheck holds it to the server-side type for exactly that reason. Second, **retention windows
disagree**: the outer log has no delete path while the MCP store keeps only the newest 100
settled rows, so the two layers become unjoinable over time even with the key.

Everything marked instrumentation is a claim about what a *retaining* deployment could prove,
never a claim about what today's platform records. Per-cell, `modeledDependencies` in the
registry names exactly which of these each construction leans on.

## 1. The commitment object

One JSON object, serialized with JCS. Field order below is documentation order; JCS decides byte
order.

```json
{
  "commitmentVersion": "1",
  "judgment": {
    "packId": "https://example.invalid/judgment-packs/data-request-intake-triage",
    "packVersion": "0.1.0",
    "packDigest": "sha256:<64 lowercase hex>",
    "specVersion": "0.2.0-draft",
    "evaluatorSpecVersion": "0.2.0-draft",
    "evaluatorRelease": "0.16.0",
    "executableDigest": "sha256:<64 lowercase hex>",
    "factsDigest": "sha256:<64 lowercase hex>",
    "evidenceDigest": "sha256:<64 lowercase hex>",
    "supportedExtensions": [],
    "dispositionDigest": "sha256:<64 lowercase hex>",
    "evidenceBacking": { "<requirement id>": { "kind": "artifact", "digest": "sha256:<64 hex>" } }
  },
  "action": {
    "gatekeeperId": 1,
    "resourceUrl": "https://tracker.example/mcp#server=tracker",
    "serverTrust": "vetted",
    "toolName": "tracker_create_work_item",
    "actionKindTag": "mcp-portal%3Ahttps%253A%252F%252Ftracker.example%252Fmcp%3Aportal-tracker:tracker_create_work_item",
    "argumentsDigest": "<64 lowercase hex, no prefix>",
    "boundResourceRevision": "<opaque string>"
  }
}
```

Field semantics and digest conventions:

- The eleven `judgment` digest/replay fields carry Study 014's semantics unchanged: exact
  retained bytes for `packDigest`/`factsDigest`/`evidenceDigest` (`sha256:`-prefixed, no
  canonicalization; `evidenceDigest` null iff no evidence document was supplied), the
  `evaluatorRelease` + `executableDigest` + `evaluatorSpecVersion` replay tuple, the sorted
  `supportedExtensions` input set, and `dispositionDigest` over the §8.3 canonical disposition
  bytes. Every identity field is **corroborated against the artifact it names** (§5,
  `judgment-identity-mismatch`) — carrying a field and checking it are different things.
- `judgment.evidenceBacking`: one entry per evidence requirement whose availability the bridge
  claims `present`. The only registered `kind` is `"artifact"`, and its `digest` must be the
  digest of an artifact **actually retained in `evidence-artifacts.json`**. A backing that
  references an approval record ("a human approved, therefore the evidence is good") or an
  observation record ("the resource was read, therefore the evidence is present") is not an
  artifact digest; and a digest with no retained preimage is a bare assertion, which the
  ceremony refuses just as firmly. Requirements claimed `absent` or `unknown` must not appear.
  **What this establishes is retained-preimage consistency and nothing more**: that the store
  holds bytes under the requirement id which hash to the committed digest. It is not proof of
  capture, not lineage, not authenticity, and not sufficiency — a bridge that stores an approval
  record's own bytes under an evidence requirement and calls them an artifact passes every check
  here, and the study says so rather than implying otherwise.
- `action` is `null` iff the disposition authorizes no action under the §4 map.
- **Derived members** — `gatekeeperId`, `resourceUrl`, `serverTrust`, `toolName`,
  `actionKindTag`, `argumentsDigest` — are determined by the §4 map from the judgment alone, and the verifier
  re-derives them rather than trusting them (§5, `action-derivation-mismatch`).
  `actionKindTag` is derived by reproducing the platform's own rule (`actionKindFor`,
  `tools.ts:94`) over the portal's scope tag; a harness test calls the pinned function itself
  over adversarial inputs and asserts the reproduction agrees with it.
- **Contextual member** — `boundResourceRevision` alone — is staging state no map can
  determine. It is never derived; it is checked against the retained store
  (`stage-revision-mismatch`, `revision-drift`). Round 2 found `serverTrust` was wrongly
  contextual (the map fixes the tier) and that `simulationBasis` could only ever be empty for
  the registered connector, so the field is gone from the schema entirely and its verdict code
  with it — a code that cannot fire is the unreachable prose this study forbids.
- `action.argumentsDigest`: SHA-256 hex over
  `JCS({"domain": "jps-cloudflare-os-binding/arguments/1", "toolName": ..., "arguments": ...})`.
  Adapter-owned by necessity, and the asymmetry with Study 014 is deliberate content: OWP ships
  a native request-arguments digest that its receipt binds; this platform's action record
  carries prose and an opaque integer, so there is no native field to reuse.

Deliberately absent: timestamps and windows (the platform owns operational time; JPS has none);
`reasons` in the clear (inside the canonical disposition bytes); approver identity (workspace
authority is the platform's, and binding it here would imply the adapter can vouch for it); a
single-use nonce (`commitmentDigest` itself is the one-time key — §5 `binding-reuse`).

## 2. The commitment digest

```
commitmentDigest = sha256hex( JCS({ "domain": "jps-cloudflare-os-binding/commitment/1",
                                    "payload": <commitment object> }) )
```

## 3. The binding points

The platform gives the adapter no signed carrier — a `WorkOrder.objective` equivalent does not
exist, and action records are unsigned rows in a Durable Object. The commitment is therefore
bound at two **retained-store** points, and the trust statement is honest and weaker than
Study 014's:

1. **Staging-time** — the gatekeeper-side staged call carries `commitmentDigest` on the one
   staged call the §4 map authorizes. Dependent and unrelated calls carry none.
2. **Report-time** — `report.json` carries the same `commitmentDigest`, so the published claim
   and the staged call bind to the same decision or visibly diverge.

An offline verifier trusts the retained store the way it trusts any unsigned evidence store: as
retained. What the ceremony proves is *internal consistency* of that store against a commitment
whose action is independently re-derived; what it cannot prove — absent signatures, which the
platform does not provide — is that the store was not coherently rewritten wholesale.

## 4. The disposition→action map

Total over the disposition space of the pinned pack:

| Disposition | Authorized action |
|---|---|
| `outcome` / `proceed`, handoff `none` | exactly one staged call of `tracker_create_work_item` on Gatekeeper 1 at `https://tracker.example/mcp#server=tracker`, arguments a deterministic function of the retained facts (`adapter/commitment.py`) |
| `outcome` / `clarify-return` or `decline-redirect` | none (communications are not queue effects; the bridge may *report* them but stages nothing) |
| `not-applicable` | none |
| `unresolved` (any reason set) | none |
| any disposition with handoff `requested` | none, and `report.json` must carry the handoff (§5 `handoff-dropped`) |

The map names its target explicitly, which is what makes the derivation oracle possible: the
authorized action is not "whatever the bridge staged on some gatekeeper" but one exact tool on
one exact resource through one exact mediator, computable from the judgment.

The map executes exactly one outcome, deliberately: every other row commits to inaction, so
every cell that stages or applies anything under those rows is adjudicable without a
counterfactual ("would this deployment have staged it?") entering the ceremony. The map is
**adapter-owned policy**, not a property of JPS or of the platform; a different deployment could
map differently, and every S- and B-family attribution is a claim about *this* map.

### 4a. Which connector, and what it forecloses

The registered deployment is the pinned **MCP Portal** connector
(`packages/gatekeeper-mcp-portal/`) configured with `MCP_PORTAL_TRUST_ANNOTATIONS=true`. Round 2
established that no other choice is possible: the generic MCP connector hardwires
`const TRUST: ServerTrust = "byo"` (`gatekeeper-mcp/src/mcp.ts:77`) with no deployment knob, and
`classifyTool` requires `vetted` for auto-approval (`mcp-shared/src/tools.ts:66-69`), so a
vetted, auto-approvable write is producible **only** through the portal
(`gatekeeper-mcp-portal/src/config.ts:34-36`; the repository says so itself at
`gatekeeper-mcp/README.md:165-167`).

Every registered identifier is therefore **synthetically reconstructed at the shape that
connector's source defines**, not a scenario-local placeholder and not a captured emission: the
resource is `https://tracker.example/mcp#server=tracker`, tool
names carry the portal's `<upstream server id>_<tool>` wire form, and the action-kind tag is
`actionKindFor("mcp-portal:<encoded endpoint>:portal-tracker", tool)` — which double-encodes,
giving the deliberately ugly
`mcp-portal%3Ahttps%253A%252F%252Ftracker.example%252Fmcp%3Aportal-tracker:tracker_create_work_item`.
Every action record carries the exact field set `mcp-shared/src/session.ts:126-135` submits:
`describeCall`-generated title and description, `implementsRevert: false`, `awaitDecision: true`
(always), an explicit `autoApprovable` boolean, and the connector-derived action kind. An earlier
draft used invented short prose, a bare endpoint, an invented `jps-tracker` scope and an omitted
`awaitDecision`; none of that was producible, and it is corrected.

What the reconstruction establishes is **coherence between a retained row's prose and the
deployment it names** — the description bytes and the action-kind tag are regenerated by the
pinned functions from registered inputs and compared byte-for-byte, in both strata. It does not
establish that the deployment is real, that any of it was observed, or that the pinned platform's
own execution paths would have written this history (PREREGISTRATION §9, "no source-reachability
claim for retained histories").

### 4b. What the pinned connector forecloses

The generic Gatekeeper contract suggests, but does not require, that a gatekeeper simulate
unapproved actions so an agent can queue dependent work (`gatekeeper.ts:624-629`). The pinned
MCP connector takes the contract's own opt-out instead: it simulates nothing and sets
`awaitDecision: true` on every write (`mcp-shared/src/session.ts:131-133`). That flag suspends
the agent's turn only when the action is **not** auto-eligible at submit time
(`overseer.ts:2905`): the registered baseline — vetted, rule enabled, `autoApprovable: true` — is
precisely the case that does not suspend. Suspension is therefore not what forecloses the
dependent-write hazard; the absence of simulation is. A dependent write staged against a fictional premise is
therefore **not constructible in this study's registered scenario**, in either direction. Five
other pinned connectors (Home Assistant, Notion, Confluence, Linear, Spotify) do implement
simulation, so the hazard is real for the platform and simply absent from this deployment.
Because the basis could only ever be empty here, `simulationBasis` is **not** in the commitment
schema at all and there is no verdict code for it: a field with one reachable value carries no
information, and a code that cannot fire is unreachable prose. PREREGISTRATION §4c records the
hazard analytically instead.

## 5. The verification ceremony

Three layers, each returning `{verdict, code, detail}`; adjudication reads the code alone.
Verdicts: `pass`, `fail` (with a code below), `not-engaged` (upstream only — the replayed policy
functions had nothing to decide), `unavailable` (apparatus absent — never a detection).

Within the binding layer **every check runs**. The first failure in the registered order below
is the adjudicated code; every other failing code is published alongside it as `suppressed`.
"Exactly one layer" is therefore a statement about what was observed, not an artifact of
returning early. The reachability tests construct a minimal condition for every code, assert the
exact code, and assert that this document's numbered order is the order the implementation runs.

### Layer `upstream` — the platform's own policy functions, replayed

`classifyTool` and `AutoApprovalDrainer` are the pinned upstream functions, imported from the
read-only clone and never reimplemented. Everything around them — which records to feed them,
how to join a ledger row to a staged call, how to reconstruct a queue, the apply callback, and
the verdict codes — is study-authored, and the Durable Object enforcement path never runs. A
`pass` here means "the platform's replayed policy functions did not object"; it is not the
platform endorsing anything. When a construction gives them nothing to decide the verdict is
`not-engaged`, and the registry records per cell which functions a construction reaches.

1. `classification-refused` — some ledger record claims `autoApproved: true` whose tool,
   classified by the pinned `classifyTool(tool, trust)` over the retained catalog and trust
   tier, comes out `autoApprovable: false` or `mode: "read"`; or a call claimed to have taken
   the read path classifies as an action. The platform's own policy would not have done it.
   This step also refuses a store that has **more than one reading**: two retained
   gatekeepers sharing an id, two ledger records sharing an id, two staged calls sharing a
   `(gatekeeperId, action)` join identity, or two ledger action records sharing one.
   Upstream assigns both ids from monotonic counters, so a duplicate is a state it cannot
   write, and round 5 found the two sides silently disagreed about which duplicate wins
   (this runner's maps kept the last, the binding layer's lookups the first). Neither
   reading may be preferred, so the classifier is given nothing and the layer refuses; the
   binding layer refuses the same stores under `binding-reuse`.

   **What an identity is, registered, and settled before uniqueness is asked.** Every id
   and join component — a gatekeeper's `id`, a ledger record's `id`, an action row's
   `gatekeeperId` and `action`, a staged call's `gatekeeperId` and `action` — must be a
   non-Boolean integer in `[1, 2^53-1]`: the counters start at 1 (`overseer.ts:418-422`)
   and every value crosses the wire as a JSON number read back through V8. Round 6 found
   the two layers disagreeing about the question itself rather than about an answer: a
   second gatekeeper carrying `id: 1.0` was a distinct key on the Python side (which
   deduplicated `repr`) and the same key here (which stringified both to `"1"`), so one
   store passed binding and was refused upstream. Floats, Booleans, `-0`, zero, negatives
   and anything past the safe-integer boundary are refused on **both** sides before either
   looks an identity up or counts one.
2. `drain-order-violation` — replaying the pinned `AutoApprovalDrainer` does not reproduce the
   claimed applications. The replay is against a **stage-time witness**, not a final snapshot,
   because two facts make a final-snapshot replay unsound in both directions: an auto-approval
   rule is hard-deleted with no tombstone when a user withdraws it (a lawful historical apply
   would replay as a violation), and an obstruction that was pending at drain time may be
   resolved later (an unlawful apply would replay clean). The witness retains only what the
   platform destroys — the rule set in force at that instant, the pass identity, and that the
   gatekeeper resolved. The queue itself is reconstructed from the ledger's own immutable
   timestamps (`createdAt <= t` and not yet resolved at `t`), which is sound because `appliedAt`
   is stamped on both approve (`overseer.ts:2495`) and reject (`overseer.ts:7730`) — it is a
   *resolution* stamp, never read here as evidence of application. A row whose state and
   resolution stamp disagree is refused outright rather than excluded, and a witnessed
   auto-approval whose `resolvedBy` is not the **whole** author tuple the pinned drainer
   passed — actor type, id and display name, the complete `AiChatAuthorInfo`
   (`api.ts:1777`) — fails, because upstream always attributes one and round 5 found only
   the id was compared. A ledger that claims an auto-approval with no witness fails; so does
   a witness claiming an application the ledger does not record — and the second half of
   that sentence is reachable only because **the retained witnesses are read before this
   check decides it has nothing to do**. The verdict is `not-engaged` when the ledger claims
   no auto-approval *and* no witness is retained; a retained witness is a record about this
   gatekeeper's drain and is replayed whatever the ledger claims. Round 6 found the early
   exit taken on the ledger alone, which made the reverse accounting unreachable: a store
   whose witness claimed an application while every row recorded `autoApproved: false` was
   never examined here and came out combined-green.

   **The queue boundary is `resolved < at`, registered.** A row already resolved *before*
   the witness instant is legitimate history and is excluded from that pass's queue — the
   platform resolves records between passes, and the lifecycle clause above is what makes
   the exclusion checkable rather than convenient. Equality is the other way: a row whose
   resolution stamp is exactly the witness instant reads as **not yet resolved** at that
   instant and stays in the queue, which is the reading the registered baseline relies on.

   **One serialized form, registered, identical on both sides.** Every retained instant —
   `createdAt`, `appliedAt`, a witness's `at` — must be exactly `YYYY-MM-DDTHH:mm:ss.sssZ`,
   the output of `Date.prototype.toISOString()`, over a calendar-valid date. That is the
   only form the platform can write, because every one of those fields is a serialized JS
   `Date`. The registered grammar was "strict RFC 3339" until round 6, which found it
   neither strict nor identical across the layers: RFC 3339 admits offsets, lowercase
   separators and any fraction width; the Python side read the fraction through `float`, so
   a valid-shaped extreme fraction raised out of a check instead of returning a verdict;
   and the node side finished with `Date.parse`, which normalizes an impossible calendar
   date such as `2026-02-29` and collapses `.0004Z` and `.0005Z` onto one millisecond —
   enough to keep a genuinely earlier resolution in a queue and have its witness pass. Both
   sides now apply the same fixed-width grammar and the same integer calendar check, and
   compare the validated **strings**: the form is fixed-width and UTC, so lexicographic
   order is chronological order and neither side does arithmetic that can fail. A row or
   witness carrying anything else is refused rather than compared.

   **What this verdict does and does not establish, normatively.** The witness is
   *self-asserted*: it is supplied by the same retained store the ceremony is examining, is
   unsigned, and is not anchored outside that store. A writer who adds a matching rule to the
   witness launders an auto-approval that no rule ever authorized, and no residue in stock
   platform state contradicts them. The verdict is therefore **consistency with the
   self-asserted witness**, never "the drain was historically lawful". The replay is also not a
   general simulation of upstream: it models one pass per witness with one static rule set and
   an always-successful apply callback, so it reproduces neither a throwing apply, nor a
   mid-pass rule change, nor the `fresh`-recheck `continue` branch, nor single-flight reruns.
   Constructions that depend on those are outside its scope. What it does buy is that the
   *queue* is reconstructed from the ledger's own records rather than from the witness, so an
   obstruction cannot be erased by resolving it later.

   The witness's own shape is **validated at store load**, not assumed: its field set is
   closed exactly as the commitment's is (`gatekeeperId`, `pass`, `at`, `appliedActionIds`,
   `rules`, `gatekeeperPresent`, each with its registered type, every rule carrying a
   gatekeeper id, an action kind and a complete author record as its enabler). Round 5 found
   the witness was cast rather than checked, so a malformed one could reach the replay and
   slip past the attribution comparison the replay rests on. A witness that is not that
   shape makes the retained store unreadable (`retained-store-unreadable`), which is an
   apparatus verdict about the store, never a detection about the bridge.

### Layer `binding` — the adapter ceremony

**Three** gate conditions abort the layer before any check runs, because nothing downstream is
evaluable without them: `commitment-missing`; `commitment-schema-invalid` (bytes that are not
UTF-8 JSON without duplicate keys, not the canonical JCS encoding of their own content, or not
§1's exact field set, closed vocabularies and digest shapes); and `retained-store-unreadable`,
which is where the store itself is resolved — an absent or unparseable ledger or platform store,
a drain witness that is not the closed shape step 2 registers, or an effect attestation that is
not the closed shape step 15 registers. Round 5 (finding 5) found this document naming two gates
while the implementation had three. Nothing else happens at context load: every reading that can
fail on its inputs, the §4 derivation included, happens inside a check and under the per-check
guard below. Then, in order:

1. `ledger-lifecycle-invalid` — some action record's lifecycle tuple is one the platform cannot
   write. Upstream sets `state`, `appliedAt` and `resolvedBy` together at the approve chokepoint
   (`overseer.ts:2493-2498`) and at the reject path (`:7727-7732`), and `autoApproved` only
   alongside an approval (there is no automatic rejection), so: a `pending` row carrying a
   resolution stamp or a resolver; an `approved`/`rejected` row missing a
   stamp or a resolver; an out-of-vocabulary state; an `approved` row carrying **no**
   `autoApproved` boolean, since the chokepoint takes it as a required argument and persists
   it either way; an `autoApproved` value of any kind in any state but `approved`, since
   nothing else ever writes the flag; a `resolvedBy` that is not a complete `AiChatAuthorInfo`
   (`api.ts:1777`) — actor type in vocabulary, non-empty id and non-empty name; a `createdAt`
   or `appliedAt` that is not the serialized-`Date` form registered under upstream step 2;
   or a row resolved before it was created. This runs for **every** cell in the
   binding layer — round 4 found lifecycle validity was enforced only inside an engaged drain
   replay, so a cell claiming no auto-approval was never checked at all.

   The three resolution-only members — `appliedAt`, `resolvedBy`, `autoApproved` — are read
   by **key presence**, not by value. Round 6 found them read with `.get()` against a `None`
   comparison, so an explicit `autoApproved: null` on an otherwise valid `pending` or
   `rejected` row passed a check whose entire subject is that the chokepoint never writes
   that member there. A member the platform does not write is refused whatever it carries.

   This step also holds each row against the **flattened connector outcome** the staged call
   sharing its identity retains, because the two are not independent — see *Retained outcome
   compatibility* under the report vocabulary below.
2. `pack-artifact-missing` / `pack-digest-mismatch` — retained pack bytes absent, or their
   digest differs from `judgment.packDigest`.
3. `judgment-identity-mismatch` — a committed identity or release field is not the one its
   artifact carries (`packId`, `packVersion`, `specVersion` against the retained pack;
   `evaluatorSpecVersion`, `evaluatorRelease` against the retained envelope), the retained pack
   does not parse at all, or `supportedExtensions` carries duplicates.
4. `facts-digest-mismatch` — retained facts absent or not the committed digest.
5. `evidence-digest-mismatch` — same rule for the evidence-availability document (null field ⇔
   absent document).
6. `disposition-digest-mismatch-retained` — the retained envelope's canonical disposition bytes
   do not digest to `judgment.dispositionDigest`.
7. `evidence-backing-invalid` — a `present` claim with no backing entry; a backing entry for a
   claim that is not `present`; a backing that is not an `artifact` reference; a backing whose
   digest has no retained preimage; a retained artifact whose bytes do not hash to their backing
   digest; or a retained artifact with no backing entry.
8. `action-derivation-mismatch` — the commitment's action diverges, in any derived member, from
   the action the §4 map derives from the **retained** judgment; or the retained facts or
   disposition are unreadable, so no action can be derived.
9. `action-map-violation` — the commitment's `action` contradicts the map for the committed
   disposition (an action object under a non-executable disposition, null under `proceed`); an
   action-class record binds to a commitment to inaction; or a bound staged call took effect
   with no approved ledger record.
10. `binding-reuse` — more than one staged call, applied record, or ledger record claims one
   `commitmentDigest`; **or** the governed inventory does not match the authorization exactly: more staged calls or
   approved records on the governed tool and resource than the map authorizes, a governed call
   that is not the one bound to this commitment, or an approved governed record that is not the
   bound one. Counting alone is insufficient — round 5 found a single unbound governed call
   satisfying the cap while every downstream check skipped it.

   **Two identities, kept apart.** The *inventory scope* — what the decision is answerable
   for — is the tool and resource the map governs, and nothing else; arguments never narrow it,
   because an attacker chooses those, and round 3 found an exact-arguments filter let a
   changed-argument twin sit outside the count. What the **bound call's** arguments must be is a
   separate question, answered by digest at step 12 (`argument-drift`) and, for effects, at
   step 15. Round 2 found that counting only digest-labelled calls let an unlabelled twin
   execute a second time invisibly, which is why the scope is labelling-independent.

   **The inventory is closed, and ambiguity refuses rather than discards.** An approved
   ledger row is governed when two things hold of the row's own retained record: its
   denormalized resource — or, absent one, the resource of the gatekeeper it names — is the
   governed resource, **and** its `description.actionKind.label` is the governed tool. The
   tool named by a staged call sharing its join identity decides nothing either way, because
   round 5 found a wrong-tool call was enough to erase an otherwise governed approval — so a
   target-tool row stays governed however a joined call contradicts it, and a *coherently*
   different-tool row is out of scope exactly as a different-resource row is. Round 6 found
   this half missing: membership was resource-only, so a coherent `tracker_close_work_item`
   approval on the governed resource was counted against the create-work-item authorization
   and refused as `binding-reuse`, although the scope registered two paragraphs above is the
   governed tool **and** resource and nothing else.

   A row that cannot be classified at all — an unretained gatekeeper, no resource anywhere,
   a denormalized resource its own gatekeeper contradicts, no retained action-kind label, or
   a label the row's own action-kind tag contradicts — is refused here, not dropped. So is a
   store with more than one reading: two retained gatekeepers sharing an id, two ledger
   records sharing an id, or two staged calls or ledger records sharing a
   `(gatekeeperId, action)` join identity — and, before any of that is asked, an id or join
   component that is not an identity the platform assigns (upstream step 1). The upstream
   layer refuses the same stores under `classification-refused`, and neither side prefers a
   duplicate.
11. `target-mismatch` — the bound staged call's gatekeeper, resource URL, trust tier, tool name,
    or the record's action-kind tag differs from the commitment's `action`.
12. `argument-drift` — the staged call's arguments do not digest to `action.argumentsDigest`.
13. `stage-revision-mismatch` — the revision recorded at staging is not the committed
    `boundResourceRevision`.
14. `revision-drift` — the revision recorded at apply time is not the committed one.
15. `unbound-execution` — over the **governed inventory** (every attested effect on the tool
    and resource the map governs, whatever arguments it carries): an effect exists with no
    approved bound application; or more effects than approved bound applications; or an effect
    that names no staged call at all where the commitment authorizes an executable action; or an
    effect whose claimed staged call is not the approved call bound to this commitment; or an
    effect on the bound call whose arguments are not the authorized ones. Round 4 demonstrated
    that a correct count can coexist with an effect produced by a different, unretained call with
    the same tuple, so an attestation carries a `source` — the **provenance the writer claims**.

    **The provenance is a closed union**, validated for shape at store load: `staged-call`
    (naming a `gatekeeperId` and `action`), `read-path`, or `out-of-band`. Only a
    `staged-call` source can be joined to the bound call, because only it names one. The
    other two arms name none, and inside the governed inventory that is itself the failure:
    where the map authorizes an executable action, every approved bound application is
    already spoken for by the cap, so an effect the store's own attestation sources
    elsewhere is unaccounted for and refuses; where the map authorizes none, the
    no-approved-bound-application clause above has already refused it. Round 5 found the
    earlier schema fabricating a staged identity for every effect, including on `m01`,
    whose effect reaches the resource through the read path, and on `b06`, whose store
    retains no staged call at all — `b06` still *claims* one, and that contradiction
    between the claim and the store is the cell. Both are inaction cells, so both refuse on
    the missing authorization, ahead of anything the union decides.

    What the join establishes is **agreement between two retained records**, not causation:
    the source is written by the same store under examination, is unsigned, and is
    corroborated by no private connector result (§0a; PREREGISTRATION §9, "no effect
    causation"). Like the attestation itself, it is instrumentation — stock Cloudflare OS
    retains neither.
16. `handoff-dropped` — the committed disposition carries handoff `requested` and `report.json`
    carries no handoff.
17. `commit-overclaim` — `report.json` claims `effect-attested` while no matching effect
    attestation is retained. The platform's `approved` state (its callback returned) is
    registered as *not* satisfying the claim, per its own at-most-once contract.
18. `report-state-unsupported` — the report's execution state is out of vocabulary, or is not
    supported by the retained store under the closed predicates below.
19. `report-misattribution` — no report is retained, the report does not bind this commitment,
    or its decision is not the committed disposition verbatim (kind, outcomeId, reasons, handoff
    state).

A check that raises is reported as `retained-store-unreadable` rather than taking the layer
down silently; the same code covers a ledger or platform store that is absent or unparseable,
a retained drain witness that is not the closed shape step 2 registers, and an effect
attestation that is not the closed shape step 15 registers. All four are statements about the
apparatus's inputs, never detections.

### Layer `replay` — the pinned evaluator

Study 014's ceremony unchanged: `replay-unavailable`, `replay-executable-mismatch` (live binary
digest vs `judgment.executableDigest`), `replay-refused` (the evaluator does not evaluate the
retained inputs), `replay-spec-version-mismatch`, `replay-disposition-mismatch` (recomputed §8.3
canonical disposition bytes vs the commitment's `dispositionDigest`).

### Report vocabulary

`report.json` is
`{"commitmentDigest": ..., "decision": {"kind", "outcomeId", "reasons", "handoffState"},
"execution": <state>, "note": string}`.

The five execution states are the boundary the composition must preserve, and each is a **closed
predicate over the retained store** rather than a free-text claim — round 1 found only
`effect-attested` was correlated with anything:

| State | Supported only when |
|---|---|
| `none` | no staged call binds this commitment and no matching effect is attested |
| `staged` | exactly one bound staged call, its ledger record (if any) still `pending`, its retained connector outcome `pending` or `failed`, no matching effect |
| `applied` | one bound staged call with an `approved` ledger record and retained connector outcome `committed` |
| `applied-unproven` | one bound staged call whose retained connector outcome **is** `outcome-unknown`, with no matching effect — the ambiguity state, never a default |
| `effect-attested` | an approved bound record with retained connector outcome `committed`, **and** a matching retained effect attestation (§5 step 17) |

The connector outcome vocabulary is `pending`, `committed`, `failed`, `rejected`, `outcome-unknown`. The
last is the platform's own at-most-once ambiguity: when an MCP dispatch's result is never
observed, the **outer** workspace record stays `pending`, because the platform transitions it
only after the gatekeeper call returns. What the cell retains for that history is the
flattened `connectorOutcome` scalar and nothing else — the private connector row, its
retryability and its error detail are not retained, and no join to a private store exists here
(SPEC §0a; round 5 asked that this be said where readers rely on it rather than only in the
retrospective review). `m02-ambiguous-commit` registers that trace (all three layers pass, and
the row is descriptive: pass here does not mean an effect occurred).

### Retained outcome compatibility

Round 6 found the predicates above correlating the flattened scalar with nothing at all except
one forbidden value under `applied`, so a store carrying `connectorOutcome: "rejected"` beside
an `approved` ledger row and an `applied` report came out completely green — against a README
that says a green ceremony means the retained store is internally consistent. The scalar, the
outer lifecycle state and the report state are therefore registered as **one matrix**, derived
from the pinned source, and enforced under the existing `ledger-lifecycle-invalid` (the store
half, for every action row of every cell) and `report-state-unsupported` (the claim half, for
the bound call) — no new verdict code.

| flattened `connectorOutcome` | admissible outer lifecycle state | admissible report state for the **bound** call |
|---|---|---|
| `pending` | `pending` | `staged` |
| `failed` | `pending` | `staged` |
| `outcome-unknown` | `pending` | `applied-unproven` |
| `committed` | `approved`, and `pending` only through the crash window below | `applied`, `effect-attested` |
| `rejected` | `rejected` | none — see the registered gap below |

Where each row comes from:

- **`approved` admits `committed` and nothing else.** The outer state is written at one
  chokepoint, *after* `await gatekeeper.applyAction(...)` returns
  (`overseer.ts:2490-2497`). The connector's `apply` reaches its success tail — `state =
  "applied"` at `action-store.ts:172-173` — only when the dispatch returned; every other path
  throws (`:136-144`'s pre-state guards; `:155-169`'s catch, which writes `failed` and
  rethrows), and a throw propagates out of `applyAction`, so `record.state = "approved"` is
  never reached.
- **`rejected` admits `rejected` and nothing else.** It is written at one path, after `await
  gatekeeper.rejectAction(...)` (`overseer.ts:7707-7732`); the connector's `reject` proceeds
  only from `pending` and throws for `applying`, `applied` and `failed`
  (`action-store.ts:201-211`).
- **`pending` is every history where the outer transition never happened**: an undispatched
  call (`pending`), a determinate failure (`failed`, `retryable: true` — `action-store.ts:157-158`
  with `callMayHaveTakenEffect` false), and the at-most-once ambiguity (the same lines with it
  true). It admits `committed` too, and only here: the connector persists `applied` at
  `action-store.ts:196` before `apply` returns, so a Durable Object that dies before the outer
  `put` at `overseer.ts:2497` leaves exactly that pair retained. Refusing it would refuse a
  producible history; what is refused instead is any *claim* about it — `applied` requires the
  approved row the workspace never wrote, and no other state names `committed`.
- **A registered gap, stated rather than papered over.** A bound call whose scalar is
  `rejected` has no supportable report state: it is not `none` (a call is bound), not `staged`
  (its record is not `pending`), and neither applied nor attested. The five-state vocabulary
  has no state for "staged, then refused", every predicate already refused each of them before
  round 6, and inventing a sixth state would be an unregistered vocabulary change. A `rejected`
  scalar on a call that is **not** the bound one is untouched by this — the obstruction calls
  of `neg-drain-skip` and `h07` are exactly that.
