# The judgment commitment — binding a JPS judgment into an OpenWorkProof chain

Status: DRAFT, registered by the Study 014 preregistration when frozen. This document is the
adapter's external contract: the commitment schema, where it binds into the OpenWorkProof
chain, the verification ceremony, and the disposition→action map. The adapter modifies
neither protocol; it composes them.

Vocabulary: "JPS" is Judgment Pack Core 0.2.0-draft as implemented by the pinned jpack
release; "OWP" is OpenWorkProof at the pinned commit (see `harness/PINS.json`); "JCS" is
RFC 8785 canonical JSON, computed by the `rfc8785` package on the Python side — the same
canonicalization OWP signs over and the same one JPS Core §8.3 defines for dispositions.

## 1. The commitment object

One JSON object, serialized with JCS. Field order below is documentation order; JCS decides
byte order.

```json
{
  "commitmentVersion": "1",
  "judgment": {
    "packId": "https://example.com/judgment-packs/expense-approval",
    "packVersion": "0.1.0",
    "packDigest": "sha256:<64 lowercase hex>",
    "specVersion": "0.2.0-draft",
    "evaluatorSpecVersion": "0.2.0-draft",
    "evaluatorRelease": "0.16.0",
    "executableDigest": "sha256:<64 lowercase hex>",
    "factsDigest": "sha256:<64 lowercase hex>",
    "evidenceDigest": "sha256:<64 lowercase hex>",
    "supportedExtensions": [],
    "dispositionDigest": "sha256:<64 lowercase hex>"
  },
  "action": {
    "toolName": "owp.apply_patch",
    "argumentsDigest": "<64 lowercase hex, no prefix>"
  }
}
```

Field semantics and digest conventions:

- `packDigest`, `factsDigest`, `evidenceDigest`: SHA-256 over the **exact retained file
  bytes** given to the evaluator, `sha256:`-prefixed — the judgment-pack runtime's own
  digest convention (audit trail, `packs lock`). No canonicalization: the bytes evaluated
  are the bytes committed. JPS itself digests neither facts nor evidence anywhere; these
  two fields are adapter-owned by necessity, and the study says so.
- `evidenceDigest` is `null` iff no evidence-availability document was supplied
  (Core §8.2's implicit-empty case). The baseline always supplies one.
- `supportedExtensions`: the sorted supported-extension set passed to the evaluator
  (completes the §8.2 input tuple).
- `evaluatorRelease` + `executableDigest` (+ `evaluatorSpecVersion`): the replay tuple of
  `docs/building-with-packs.md` — release that ran, digest of the binary that ran, contract
  applied. Without them the disposition cannot be deterministically recomputed.
- `dispositionDigest`: SHA-256 over the **§8.3 canonical disposition bytes** — the JCS
  serialization of the `disposition` member of the evaluator's compact `--format json`
  envelope. Those bytes are the whole of the JPS portability claim; they are what two
  conforming implementations must agree on, so they are what the commitment binds.
- `action` is `null` iff the disposition authorizes no autonomous action under the §4 map
  (any non-`approve` outcome, `unresolved`, `not-applicable`, or a requested handoff). A
  `null` action commits to *inaction*: no receipt in the chain may carry this commitment's
  digest.
- `action.toolName`: one of OWP's closed tool literals. In this study only
  `owp.apply_patch` is ever executable.
- `action.argumentsDigest`: **OWP's own** request-arguments digest — SHA-256 over
  `JCS({"domain": "openworkproof/agent-arguments/v0.1", "tool_name": ..., "arguments": ...})`
  — bare hex, exactly as `ToolCallReceipt.arguments_digest` carries it. This is the one
  field with a native OWP representation and it is reused byte-for-byte, so the adapter's
  check meets the receipt's own bound field with no translation.

Deliberately absent (bound-because-needed, not because-available): `handoffTarget`
(pack-declared; derivable from `packDigest` + disposition), `trace` (spec-informative,
forbidden from affecting the disposition), timestamps and windows (OWP owns time with
signed-timestamp windows; JPS deliberately has none), `reasons` in the clear (already
inside the canonical disposition bytes), `artifact.bundleDigest` (evaluator-internal),
nonces (OWP's `AgentRequest.nonce` plus ledger uniqueness already own request replay).

## 2. The commitment digest

```
commitmentDigest = sha256hex( JCS({ "domain": "jps-openworkproof-binding/commitment/1",
                                    "payload": <commitment object> }) )
```

Domain separation follows OWP's own digest style so a commitment digest can never collide
with any OWP protocol digest.

## 3. The two binding points

1. **Authorization-time** — the full commitment JSON (compact JCS text) is the value of
   `WorkOrder.objective`. The WorkOrder is Maintainer-signed; OWP never reads `objective`.
   Measured size ~700 bytes against the 4096-byte bound.
2. **Execution-time** — `commitmentDigest` is the value of
   `AgentRequest.context_source_digest` on the **executing tool call only** (the
   `owp.apply_patch` request). That field is signed by the acting agent and mirrored under
   the Sidecar's receipt signature via `CorrelationFactors`. It is bound on the executing
   request only, so OWP's shared-factor independence warnings are never coupled to the
   commitment.

The executing receipt is located by searching the verified chain for tool-call receipts
whose nested request's `context_source_digest` equals the commitment digest recomputed from
`WorkOrder.objective`. Zero such receipts, or more than one, is a binding failure.

## 4. The disposition→action map (registered)

The map is total over the disposition space and is the study's integration contract —
JPS Core binds no caller, exactly as Study 013's execution mapper was study-defined:

| Replayed disposition | Authorized action |
|---|---|
| `kind=outcome`, `outcomeId="approve"`, `handoff.state="none"` | `owp.apply_patch` with the canonical action document (below) |
| any other disposition (any other outcome, `unresolved`, `not-applicable`, or any `handoff.state="requested"`) | **no autonomous action** — an executing receipt bound to the commitment is a violation |

Canonical action document: a unified diff adding one file `decision-actions/disburse.json`
whose content is the JCS bytes of

```json
{"action": "disburse-expense", "amount": <facts /expense/amount>,
 "category": <facts /expense/category>, "currency": "USD"}
```

The diff bytes are a deterministic function of the retained facts (exact byte template in
`adapter/commitment.py`). The patch **is** the executed action: OWP binds its bytes by
SHA-256 into `ApplyPatchArguments.patch_digest` under both the actor's and the Sidecar's
signatures, which is what makes argument substitution (mutations D16/D17) a digest
mismatch rather than a semantic dispute.

## 5. The verification ceremony

Ordered, fail-closed, offline. Inputs: the acceptance bundle, the retained artifact set
(pack bytes, facts bytes, evidence bytes, evaluator envelope, commitment document), the
pinned `jpack` executable, and nothing else. Public keys come from the WorkOrder's own
key bindings (OWP's TOFU root — enumerated as a trust root, not hidden). Each layer runs
and records independently so the detection matrix can attribute; the combined verdict is
pass iff every layer passes.

**Layer OWP** — `openworkproof.acceptance.verify_acceptance_bundle`, unchanged, exactly as
upstream ships it. Verdict: `pass` | `fail` (upstream message recorded) | `unavailable`
(bundle unreadable).

**Layer BINDING** — adapter checks, in order, first failure wins:

| Code | Check |
|---|---|
| `commitment-objective-missing` | `WorkOrder.objective` does not parse as a commitment |
| `commitment-schema-invalid` | parsed object violates §1 (unknown fields refused) |
| `binding-point-divergence` | recomputed `commitmentDigest` ≠ the executing request's `context_source_digest`, or retained commitment document ≠ objective commitment |
| `executing-receipt-missing` / `executing-receipt-ambiguous` | with a non-null `action`: no receipt, or more than one, carries the commitment digest. With a `null` action, a receipt carrying the digest is `action-map-violation` |
| `pack-artifact-missing` / `pack-digest-mismatch` | retained pack bytes absent / SHA-256 ≠ `packDigest` (with `packId`/`packVersion`/`specVersion` cross-checked against the retained bytes) |
| `facts-artifact-missing` / `facts-digest-mismatch` | same, facts |
| `evidence-artifact-missing` / `evidence-digest-mismatch` | same, evidence (respecting the `null` case) |
| `disposition-digest-mismatch-retained` | retained evaluator envelope's canonical disposition bytes do not hash to `dispositionDigest` |
| `action-tool-mismatch` | executing receipt's `tool_name` ≠ `action.toolName` |
| `action-arguments-mismatch` | executing receipt's `arguments_digest` ≠ `action.argumentsDigest` |
| `action-map-violation` | the §4 map, applied to the committed disposition, does not authorize the executed action (including: non-executable disposition with an executing receipt present; executable disposition whose derived action document digest ≠ the committed/executed one) |

Verdict: `pass` | `fail:<code>`.

**Layer REPLAY** — deterministic recomputation under the recorded tuple:

| Code | Check |
|---|---|
| `replay-executable-mismatch` | SHA-256 of the `jpack` binary ≠ `executableDigest`, or its reported version ≠ `evaluatorRelease` (the harness refuses to substitute a different evaluator — replay means the recorded binary) |
| `replay-unavailable` | retained pack/facts/evidence bytes absent |
| `replay-refused:<class>` | the evaluator returned an error envelope (class recorded; a refusal is never a disposition) |
| `replay-disposition-mismatch` | recomputed canonical disposition bytes do not hash to `dispositionDigest` |

Verdict: `pass` | `fail:<code>` | `unavailable`.

Interpretation rules, load-bearing for the registered matrix:

- Both adapter layers source the commitment from the **signed** binding point
  (`WorkOrder.objective`). A chain with no commitment there yields Layer REPLAY
  `unavailable` — nothing committed, nothing to recompute.
- Within `binding-point-divergence`, the retained-commitment-vs-objective comparison runs
  before the executing-receipt search. Consequence: *any* tamper inside the objective
  commitment surfaces as `binding-point-divergence`; the artifact-level codes
  (`pack-digest-mismatch`, …) are reachable only when the commitment itself is
  consistently carried (the resigned variants).
- The executing receipt is located by digest search (§3), never structurally by tool —
  that is what lets a commitment bound to the wrong tool fire `action-tool-mismatch`.
- A `null` action with no receipt carrying the digest is conforming even when the
  committed disposition would have authorized an action; `action-map-violation` requires
  an executing receipt.
- Two executable-digest checks exist and are distinct: the harness checks `JPACK_BIN`
  against the **registry pin** (`PINS.json`) — a mismatch is pipeline-invalid, validity
  channel; Layer REPLAY checks the binary against the **commitment's** `executableDigest`
  — a mismatch is the cell verdict `replay-executable-mismatch`.

The ceremony order (verify the external chain under pinned keys → bind → recompute →
replay → act on the verdict JSON, never on incidental signals) follows the gateway's §5a
consumer ceremony, cited as prior art.

## 6. What each layer owns (and what none does)

- OWP owns: signature validity, causal-chain integrity, authorization (grants, roles,
  windows, quotas, gates), policy-predicate arithmetic over asserted execution facts,
  evidence-set exactness, nonce/replay-of-request protection.
- BINDING owns: the identity between the judgment tuple (pack, inputs, disposition), the
  authorized action, and what the chain actually carries and executed.
- REPLAY owns: that the committed disposition is genuinely what the pinned evaluator
  produces from the committed inputs — JPS §8.3 byte-portability doing real work.
- Nobody owns: policy truth, fact truth, currency ("is this pack still the one to use") or
  policy rollback across otherwise-valid WorkOrders — those need an anchor outside the
  chain (reviewed-set lock / registry analogue) and are registered as expected-undetected.

Ceiling, both layers, stated once and meant: binding/lineage, not truth.
