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
  `null` action commits to *inaction* over the whole chain: the chain may carry no
  action-class receipt at all (§5), marked or unmarked.
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

The executing receipt is located **structurally**, by tool, and never by the marker: the
action class is every `event_type="tool_call"` receipt whose `tool_name` is
`owp.apply_patch`. `owp.create_pr_proposal` is deliberately outside the action class —
the §4 map never authorizes it, so a chain carrying one is not carrying an execution of a
judged action. Marker-based selection was the round-1 blocker: a chain that simply omitted
`context_source_digest` presented an empty selected set, and a negative disposition could
execute by declining to mark its own receipt.

**Defense in depth, not demonstrated necessity.** OWP already associates every receipt
with its signed WorkOrder cryptographically, so the second point's marginal contribution
over that authenticated lineage is not established by this study: no coherent
objective-only / execution-only ablation arm is registered. The two points are described
as defense in depth and `e20` exercises the execution-side check; a differential-necessity
claim is withdrawn.

## 4. The disposition→action map (registered)

The map is total over the disposition space and is the study's integration contract —
JPS Core binds no caller, exactly as Study 013's execution mapper was study-defined:

| Replayed disposition | Authorized action |
|---|---|
| `kind=outcome`, `outcomeId="approve"`, `handoff.state="none"` | `owp.apply_patch` with the canonical action document (below) |
| any other disposition (any other outcome — including `manual-review` — `unresolved`, `not-applicable`, or any `handoff.state="requested"`) | **no autonomous action** — *any* action-class receipt in the chain is a violation, marked or not (§5) |

Canonical action document: the file `decision-actions/disburse.json`, whose content is the
JCS bytes of

```json
{"action": "disburse-expense", "amount": <facts /expense/amount>,
 "category": <facts /expense/category>, "currency": "USD"}
```

plus one terminating newline. The patch that creates it is OWP's **canonical create-file
patch**, which is the only shape `repo_tools.parse_patch_phase_a` accepts:

```
diff --git a/decision-actions/disburse.json b/decision-actions/disburse.json
new file mode 100644
index 0000000000000000000000000000000000000000..<git blob oid of the content>
--- /dev/null
+++ b/decision-actions/disburse.json
@@ -0,0 +1 @@
+<JCS bytes of the action document>
```

Every line is load-bearing upstream: the Git file header (the old `--- /dev/null` unified
diff without it is refused as "patch file header is not canonical"), the `new file mode`
line, the zero-to-blob `index` line whose right object id must equal
`repo_tools.git_blob_oid` of the created content, and a hunk whose ranges are exactly
`-0,0 +1`. The created file carries its terminating newline because
`repo_tools._canonical_patch_text` refuses a touched file without one — which is why the
old template's `\ No newline at end of file` trailer is gone. The patch's own derived
paths must equal the declared `target_paths` exactly, so a cell that moves the target
moves the header, the blob object id and the hunk with it. The candidate source therefore
also carries `decision-actions/.keep`: `apply_patch_phase_b` refuses to create a file
whose immediate parent directory does not already exist.

The diff bytes are a deterministic function of the retained facts and the target path
(exact byte template in `adapter/commitment.py`). The patch **is** the executed action:
OWP binds its bytes by SHA-256 into `ApplyPatchArguments.patch_digest` under both the
actor's and the Sidecar's signatures, which is what makes argument substitution (mutations
D16/D17) a digest mismatch rather than a semantic dispute. Every registered chain applies
its patch through `repo_tools.apply_patch_in_candidate_workspace` against a real Git
candidate workspace, and the executor's own `PatchResultEvidence` — not a harness-built
stand-in — is what the receipt commits.

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

**Layer BINDING** — adapter checks over the raw bundle JSON, in this exact order, first
failure wins. Every layer returns `{verdict, code, detail}`; adjudication is on the
`code` alone and `detail` never enters a comparison.

| Code | Check |
|---|---|
| `commitment-objective-missing` | `WorkOrder.objective` is absent, is not a string, or does not decode to a version-1 commitment at all |
| `commitment-schema-invalid` | the objective *is* a version-1 commitment but violates §1 (unknown fields refused), or violates the encoding rule below — duplicate member names, invalid UTF-8, or bytes that are not the canonical JCS encoding of their own content |
| `binding-point-divergence` | the retained commitment document is absent or is a *different* commitment from the objective's; or the single action-class receipt's request does not carry the commitment digest; or the receipt's `CorrelationFactors` do not mirror the request binding |
| `executing-receipt-missing` | with a non-null `action`: the chain carries no action-class receipt at all |
| `action-map-violation` | the §4 map is violated: a null `action` with any action-class receipt or any receipt carrying the commitment digest; a non-null `action` with more than one action-class receipt; or an executable disposition whose derived action document differs from the committed and executed one |
| `action-tool-mismatch` | a receipt carrying the commitment digest names a tool other than `action.toolName` — the chain claims something the map cannot authorize is the executing call |
| `pack-artifact-missing` / `pack-digest-mismatch` | retained pack bytes absent / SHA-256 ≠ `packDigest` (with `packId`/`packVersion`/`specVersion` cross-checked against the retained bytes) |
| `facts-artifact-missing` / `facts-digest-mismatch` | same, facts |
| `evidence-artifact-missing` / `evidence-digest-mismatch` | same, evidence (respecting the `null` case) |
| `disposition-digest-mismatch-retained` | retained evaluator envelope's canonical disposition bytes do not hash to `dispositionDigest` |
| `action-arguments-mismatch` | the action-class receipt's `arguments_digest` ≠ `action.argumentsDigest` |

Outcome: `pass` | `fail:<code>`.

**The JCS boundary is byte-level, not object-level.** The commitment is parsed from exact
bytes, refusing duplicate member names (`object_pairs_hook`) and non-UTF-8 input, and the
signed objective bytes MUST equal `JCS(parsed commitment)` exactly. The retained
`commitment.json` bytes MUST equal those same canonical bytes. The two failure codes are
distinguished by *what* differs, and the rule is exact:

- retained bytes ≠ canonical bytes, but the retained bytes parse to the **same** object →
  `commitment-schema-invalid` (a non-canonical encoding of the right commitment);
- retained bytes parse to a **different** object → `binding-point-divergence`.

Comparing parsed Python objects would let two conforming consumers assign different
semantics to the same signed duplicate-key document while Python reported equality; that
is the hole this rule closes.

**Exact-set totality over the action class.** With a `null` action the chain must carry
**zero** action-class receipts *and* zero receipts carrying the commitment digest. With a
non-null action it must carry **exactly one** action-class receipt, that receipt's nested
request must carry the commitment digest, its `CorrelationFactors` must mirror it, and its
`tool_name`/`arguments_digest` must match the commitment. Any surplus action-class receipt
is an `action-map-violation` whichever one carries the marker: one commitment authorizes
one execution.

**Layer REPLAY** — deterministic recomputation under the recorded tuple. The committed
`supportedExtensions` are passed to the evaluator as `--supported-extension` (completing
the §8.2 input tuple rather than committing a field nothing reads), and the replayed
envelope's `evaluatorSpecVersion` is cross-checked against the committed one.

| Code | Check |
|---|---|
| `replay-unavailable` | no conforming commitment at the signed binding point, the pinned evaluator is unavailable, or retained pack/facts/evidence bytes are absent |
| `replay-executable-mismatch` | SHA-256 of the `jpack` binary ≠ `executableDigest`, or its reported version ≠ `evaluatorRelease` (the harness refuses to substitute a different evaluator — replay means the recorded binary) |
| `replay-refused` | the evaluator returned an error envelope (the §8.4 class is recorded as detail, never as part of the code; a refusal is never a disposition) |
| `replay-spec-version-mismatch` | the replayed envelope's `evaluatorSpecVersion` ≠ the committed `evaluatorSpecVersion` — the contract applied is not the contract committed |
| `replay-disposition-mismatch` | recomputed canonical disposition bytes do not hash to `dispositionDigest` |

Outcome: `pass` | `fail:<code>` | `unavailable`, where `unavailable` is definitionally the
outcome of the pair (verdict `unavailable`, code `replay-unavailable`).

Interpretation rules, load-bearing for the registered matrix:

- Both adapter layers source the commitment from the **signed** binding point
  (`WorkOrder.objective`). A chain with no commitment there yields Layer REPLAY
  `unavailable` — nothing committed, nothing to recompute.
- The retained-commitment-vs-objective comparison runs before receipt discovery.
  Consequence: *any* tamper inside the objective commitment surfaces as
  `binding-point-divergence`; the artifact-level codes (`pack-digest-mismatch`, …) are
  reachable only when the commitment itself is consistently carried (the resigned
  variants).
- Receipt discovery is structural (by tool); the marker is then *checked* against the
  discovered receipt rather than used to select it. `action-tool-mismatch` is what a
  marker pointing somewhere else produces, and it is checked before the action-class
  count so a mis-pointed marker is attributed to the marker.
- A `null` action is conforming only in a chain that executed nothing at all — the map's
  commitment to inaction is a commitment about the whole chain, not about marked receipts.
- Two executable-digest checks exist and are distinct: the harness checks `JPACK_BIN`
  against the **registry pin** (`PINS.json`) — a mismatch is pipeline-invalid, validity
  channel; Layer REPLAY checks the binary against the **commitment's** `executableDigest`
  — a mismatch is the cell outcome `replay-executable-mismatch`.
- Every registered code is *reachable*: a harness test constructs a minimal condition for
  each one and asserts the exact code and the first-failure ordering.
  `executing-receipt-ambiguous` left the registry at round 1 because structural discovery
  makes it unreachable — two marked action-class receipts are now a surplus
  `action-map-violation`.

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
  chain (reviewed-set lock / registry analogue). Currency is registered as an analytic
  limitation (no fixture distinct from the baseline can observe it); alternative-WorkOrder
  remint is registered as a descriptive boundary row, excluded from R1 credit. An attacker
  holding every fixture key can remint the whole chain coherently and nothing chain-internal
  distinguishes the remint — stated plainly rather than papered over with another
  self-declared commitment field.

Ceiling, both layers, stated once and meant: binding/lineage, not truth.
