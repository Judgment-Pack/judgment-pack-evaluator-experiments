# The staged-action commitment — binding a JPS judgment to a Cloudflare OS action queue

Status: DRAFT, registered by the Study 015 preregistration when frozen. This document is the
adapter's external contract: the commitment schema, the retained-record model, the verification
ceremony with its exact verdict codes, and the disposition→action map. The adapter modifies
neither system; it composes them — and, unlike Study 014's counterpart, one of the two systems
ships **no offline bundle verifier and no signature over its own records**, so most of this
contract is what the platform's published TODO calls a "richer action description plus a future
policy engine", built adapter-side and said to be adapter-side.

Vocabulary: "JPS" is Judgment Pack Core 0.2.0-draft as implemented by the pinned jpack release;
"the platform" is Cloudflare OS at the pinned commit (`harness/PINS.json`) — specifically the
Gatekeeper/action-queue contract of `packages/workshop-shared/src/gatekeeper.ts`, the workspace
action-record model of `packages/workshop-backend/src/overseer.ts`, the auto-approval drain of
`packages/workshop-backend/src/auto-approval.ts`, and the MCP tool-trust policy of
`packages/mcp-shared/src/tools.ts`. "JCS" is RFC 8785 canonical JSON, computed by the `rfc8785`
package on the Python side — the canonicalization JPS Core §8.3 defines for dispositions.

## 0. The retained-record model (what an offline verifier is given)

The platform persists action records inside a Durable Object and exposes them to clients as an
action log; it does not sign them, does not digest them, and ships no verifier over them
(`overseer.ts:424` `ActionRecord`; no runtime schema exists — the contract is TypeScript types
only). The study therefore fixes a retained-record model: one directory per cell containing the
exact bytes an offline third party is assumed to have been handed.

| File | What it is | Whose shape |
|---|---|---|
| `pack.json` | The Judgment Pack evaluated | JPS (vendored spec corpus bytes) |
| `facts.json` | The §8.2 facts document | JPS |
| `evidence.json` | The §8.2 evidence-availability document | JPS |
| `evaluation.json` | The pinned evaluator's compact `--format json` envelope | jpack |
| `commitment.json` | This SPEC's §1 object, canonical JCS bytes | adapter |
| `ledger.json` | The workspace action log: an ordered list of platform `ActionRecord`-shaped entries (Date fields as RFC 3339 strings) | platform (held to the pinned published contract — `ActionLogEntry` and its member types, server-only `action`/`caller` stripped and stated — by the clone's own compiler: `harness/typecheck.py`) |
| `platform.json` | The modeled platform-side store: gatekeepers (id, resource URL, `ServerTrust` tier, MCP tool catalog with annotations), `autoApproveTags` rules, gatekeeper-side staged calls (action key → tool name, arguments, resource revision at staging, simulation basis), simulations, the external resource's revision timeline, and external effect attestations | **modeled** (see honesty note) |
| `report.json` | The bridge's published claim: what was decided and what was done | adapter |
| `MANIFEST.sha256` | Exact-set digest manifest over the above | study |

**Honesty note — what is modeled and why.** The platform's own `ActionRecord` carries prose, a
resolver, timestamps, and an opaque per-gatekeeper `action` key (`overseer.ts:441`); the tool
name, arguments, and resource state live inside each Gatekeeper's private storage and never
appear in the log. A post-hoc verifier that sees only the log can bind nothing to arguments or
state. `platform.json` models the gatekeeper-side store an *instrumented* Gatekeeper could
retain; every claim adjudicated over it is a claim about what a retaining deployment could
prove, never a claim about what today's platform records. `ledger.json` is the platform's own
published record shape, held to the pinned types mechanically. The external-effect attestations
in `platform.json` model a third-party record of what the external system says happened; the
platform's `approved` state deliberately does not prove dispatch (`mcp-shared/README.md`
at-most-once), and this study never treats it as if it did.

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
    "resourceUrl": "https://tracker.example/mcp",
    "serverTrust": "vetted",
    "toolName": "create_work_item",
    "actionKindTag": "<upstream actionKindFor(...).tag>",
    "argumentsDigest": "<64 lowercase hex, no prefix>",
    "boundResourceRevision": "<opaque string>",
    "simulationBasis": []
  }
}
```

Field semantics and digest conventions:

- The eleven `judgment` digest/replay fields carry Study 014's semantics unchanged: exact
  retained bytes for `packDigest`/`factsDigest`/`evidenceDigest` (`sha256:`-prefixed, no
  canonicalization; `evidenceDigest` null iff no evidence document was supplied), the
  `evaluatorRelease` + `executableDigest` + `evaluatorSpecVersion` replay tuple, the sorted
  `supportedExtensions` input set, and `dispositionDigest` over the §8.3 canonical disposition
  bytes — the JCS serialization of the `disposition` member of `evaluation.json`.
- `judgment.evidenceBacking` is new in this study and exists because two of the boundary's
  known confusions live exactly here. One entry per evidence requirement whose availability the
  bridge claims as `present`. The only registered `kind` is `"artifact"`: the SHA-256 of the
  captured evidence artifact's bytes as retained by the acquiring system. A backing that
  references an approval record ("a human approved, therefore the evidence is good") or an
  observation record ("the resource was read, therefore the evidence is present") is not an
  artifact digest and does not satisfy this field — that is the point. Requirements claimed
  `absent` or `unknown` must not appear. The map may be empty. The backing digests are
  adapter-carried assertions of lineage, not truth: nothing here inspects the artifact.
- `action` is `null` iff the disposition authorizes no action under the §4 map. A null action
  commits to *inaction*: the retained ledger may carry no action-class record bound to this
  commitment, and the retained effect attestations may carry no effect matching the judged
  subject (§5 codes `action-map-violation`, `unbound-execution`).
- `action.gatekeeperId` / `resourceUrl` / `serverTrust`: the exact mediating Gatekeeper, the
  exact external resource, and the deployment's trust tier for that endpoint
  (`mcp-shared/src/tools.ts:27` `ServerTrust`). The tier is bound because the platform's own
  auto-approval policy branches on it.
- `action.toolName`: the MCP tool the staged call names. `action.actionKindTag`: the platform's
  own stable policy key for the action (`gatekeeper.ts:971` `ActionKind.tag`), computed by the
  pinned `actionKindFor` at fixture-build time and bound because auto-approval rules and the
  platform's anticipated policy engine key on it.
- `action.argumentsDigest`: SHA-256 hex over
  `JCS({"domain": "jps-cloudflare-os-binding/arguments/1", "toolName": ..., "arguments": ...})`.
  **Adapter-owned by necessity, and the asymmetry with Study 014 is deliberate content**: OWP
  ships a native request-arguments digest that the receipt itself binds; this platform's action
  record carries prose and an opaque integer. There is no native field for this digest to reuse.
- `action.boundResourceRevision`: the external resource's revision identifier at the moment the
  action was staged, as retained in the gatekeeper-side store. Bound so a delayed approval
  against a moved world is detectable (§5 `revision-drift`). Opaque to the adapter.
- `action.simulationBasis`: the ids (ascending, unique) of every simulated-but-unapproved
  effect whose fictional state this action was staged against — the platform's deferred-approval
  protocol lets a Gatekeeper show an agent simulated results and queue dependent actions
  (`gatekeeper.ts:617-630`, `README.md` deferred approval). Empty when the action depends on
  nothing fictional. Bound so a dependent action whose premise was later rejected is detectable
  (§5 `simulation-basis-invalid`). The platform itself tracks no such basis; this field is the
  adapter's record of what the bridge knew.

Deliberately absent: timestamps and windows (the platform owns operational time; JPS has none);
`reasons` in the clear (inside the canonical disposition bytes); approver identity (workspace
authority is the platform's, and binding it here would imply the adapter can vouch for it);
a single-use nonce (`commitmentDigest` itself is the one-time key — §5 `binding-reuse`);
`catalogRevision` (upstream-computable over the tool catalog, exercised as an upstream probe,
but not bound: binding it would duplicate `boundResourceRevision`'s role with a value the
attacker-controlled catalog fixes).

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

1. **Staging-time** — the gatekeeper-side staged call (`platform.json`, `stagedCalls`) carries
   `commitmentDigest` on the one staged call the §4 map authorizes. Dependent and unrelated
   calls carry none.
2. **Report-time** — `report.json` carries the same `commitmentDigest`, so the published claim
   and the staged call bind to the same decision or visibly diverge.

An offline verifier trusts the retained store the way it trusts any unsigned evidence store:
as-retained. What the ceremony proves is *internal consistency* of that store against the
commitment; what it cannot prove — absent signatures, which the platform does not provide — is
that the store was not coherently rewritten wholesale. Stated in the preregistration as the
study's ceiling, mirroring Study 014 §4b's full-keys remint.

## 4. The disposition→action map

Total over the disposition space of the pinned pack, by construction of the §1 `action` rule:

| Disposition | Authorized action |
|---|---|
| `outcome` / `proceed`, handoff `none` | exactly one staged call of `create_work_item` on the bound Gatekeeper, arguments a deterministic function of the retained facts (`adapter/commitment.py`) |
| `outcome` / `clarify-return` or `decline-redirect` | none (communications are not queue effects; the bridge may *report* them but stages nothing) |
| `not-applicable` | none |
| `unresolved` (any reason set) | none |
| any disposition with handoff `requested` | none, and `report.json` must carry the handoff (§5 `handoff-dropped`) |

The map executes exactly one outcome, deliberately: every other row commits to inaction, so
every cell that stages or applies anything under those rows is adjudicable without a
counterfactual ("would this deployment have staged it?") entering the ceremony.

## 5. The verification ceremony

Three layers, each returning `{verdict, code, detail}`; adjudication reads the code alone.
Verdicts: `pass`, `fail` (with a code below), `unavailable` (apparatus absent — never a
detection). First failure wins within a layer, in the exact order listed; the reachability
tests construct a minimal condition for every code *and* assert the first-failure ordering, so
no registered code can be unreachable prose.

### Layer `cf` — the platform's own executable policy surface

Real pinned upstream code, imported from the clone (`CFOS_SOURCE`), never vendored, never
reimplemented; run by the node probe runner (`probes/`, invoked via `harness/cf_runner.py`).
Per cell the runner reports which checks engaged; a cell whose construction touches no
platform-owned check passes vacuously and says so (`platformChecksEngaged: []` in the registry
— the vacuity is R2 content, not a defect).

Order and codes:

1. `classification-refused` — some ledger action record claims `autoApproved: true` whose
   tool, classified by the pinned `classifyTool(tool, trust)` (`tools.ts:62`) over the retained
   catalog and trust tier, comes out `autoApprovable: false` or `mode: "read"`. The platform's
   own policy would never have auto-applied it.
2. `drain-order-violation` — replaying the pinned `AutoApprovalDrainer` (`auto-approval.ts:25`)
   over the retained records — claimed-auto records reset to `pending`, manual-pending records
   kept, rules from the retained `autoApproveTags`, upstream's own mock-storage pattern — does
   not reproduce exactly the claimed set of auto-applied records in ascending-id order. The
   drain stops at the first non-eligible pending action and never skips a human gate
   (`auto-approval.ts:58-73`); a ledger claiming otherwise is claiming the platform did
   something its own code refuses to do.

The runner also self-reports node version, clone HEAD, tracked-tree cleanliness, and the
digests of the probed upstream source files; mismatches against `harness/PINS.json` are
pipeline-validity problems (the apparatus is wrong), never cf detections.

### Layer `binding` — the adapter ceremony

Order and codes:

1. `commitment-missing` — no `commitment.json`.
2. `commitment-schema-invalid` — the bytes are not UTF-8 JSON without duplicate keys, not the
   canonical JCS encoding of their own content, or not §1's exact field set, closed
   vocabularies, and digest shapes.
3. `pack-artifact-missing` / `pack-digest-mismatch` — retained pack bytes absent, or their
   digest differs from `judgment.packDigest`.
4. `facts-digest-mismatch` / `evidence-digest-mismatch` — same rule for the other two §8.2
   documents (evidence: null field ⇔ absent document).
5. `disposition-digest-mismatch-retained` — the retained envelope's canonical disposition bytes
   do not digest to `judgment.dispositionDigest`.
6. `evidence-backing-invalid` — the claims in `evidence.json` and `judgment.evidenceBacking`
   disagree (a `present` claim without a backing entry, a backing entry for a non-`present`
   claim), or a backing entry is not an artifact digest — including the two designed
   confusions: a reference to an approval record and a reference to an observation record.
7. `action-map-violation` — the commitment's `action` member contradicts the §4 map for the
   committed disposition (an action object under a non-executable disposition, null under
   `proceed`); or an action-class ledger record binds to this commitment while the map says
   inaction; or the bound staged call was applied with no ledger approval at all.
8. `binding-reuse` — more than one applied ledger record (or staged call) binds to one
   `commitmentDigest`.
9. `target-mismatch` — the bound staged call's gatekeeper, resource URL, trust tier, tool
   name, or action-kind tag differs from the commitment's `action`.
10. `argument-drift` — the staged call's arguments do not digest to
    `action.argumentsDigest` under §1's arguments domain.
11. `revision-drift` — the resource revision recorded at apply time differs from
    `action.boundResourceRevision`.
12. `simulation-basis-invalid` — some id in `action.simulationBasis` names a simulation whose
    underlying action is not `approved` in the retained ledger at the bound action's apply
    time (rejected, still pending, or absent).
13. `unbound-execution` — a retained external-effect attestation matches the judged subject
    (same resource, tool, and arguments digest) with no approved action-class ledger record
    bound to this commitment authorizing it — the read-path bypass and the out-of-band effect
    land here.
14. `handoff-dropped` — the committed disposition carries handoff `requested` and
    `report.json` carries no handoff, or reports the case closed.
15. `commit-overclaim` — `report.json` claims `effect-attested` (or equivalent committed
    language) while the retained effect attestations carry no matching effect; the platform's
    `approved` state (Gatekeeper callback returned) is registered as *not* satisfying the
    claim, per the platform's own at-most-once contract.
16. `report-misattribution` — `report.json`'s decision does not equal the committed
    disposition verbatim (kind, outcomeId, reasons, handoff state) — the "unresolved became
    rejected" collapse and its relatives.

### Layer `replay` — the pinned evaluator

Study 014's ceremony unchanged: `replay-unavailable`, `replay-executable-mismatch` (live
binary digest vs `judgment.executableDigest`), `replay-refused` (evaluator error on retained
inputs), `replay-spec-version-mismatch`, `replay-disposition-mismatch` (recomputed §8.3
canonical disposition bytes vs the commitment's `dispositionDigest`).

### Report vocabulary

`report.json` is
`{"commitmentDigest": ..., "decision": {"kind", "outcomeId", "reasons", "handoffState"},
"execution": one of "none" | "staged" | "applied" | "applied-unproven" | "effect-attested",
"note": string}`.
The five execution states are the boundary the assessment requires a bridge to preserve:
*staged* (queued, undecided), *applied* (the platform callback returned — not proof of
dispatch), *applied-unproven* (dispatched into ambiguity — the at-most-once case),
*effect-attested* (an external attestation exists), *none*. `m02-ambiguous-commit` registers
the honest bridge (`applied-unproven`, all layers pass) as a descriptive boundary;
`d02-simulated-as-committed` registers the dishonest one (`effect-attested` with no
attestation) as `commit-overclaim`.
