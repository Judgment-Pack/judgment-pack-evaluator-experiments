# Analysis — Study 006

## Decision

Keep the evidence-lineage design as an experimental product-side harness. Do not yet add its bytes
to JPS Core or make the stable runtime resolve source identifiers.

Phase A gives useful implementation evidence: a closed candidate shape alone accepted every
registered tamper, while the binding/receipt/artifact/claim/evaluation chain rejected all eight and
localized each failure. Phase B gives no model-usability evidence because no model inference
started.

## What closes the weak handoff

An MCP or CLI call is not itself the guarantee. The guarantee comes from preserving and verifying
one digest-linked chain:

```text
approved binding
  → authenticated acquisition receipt
  → exact raw artifact digest
  → claim pointers and prepared-input digest
  → evaluator executable + pack + input digests
  → disposition digest
  → authenticated evaluation receipt
```

The evaluator does not infer provenance from prose. A trusted product gate verifies the chain,
constructs the evaluator input from the admitted envelope, and records the exact output. A
downstream consumer accepts the output only with a valid evaluation receipt. If an agent changes a
fact, evidence state, subject, binding, artifact, stale record, or output, a recomputed digest or
semantic relationship fails.

This design works behind an MCP gateway, a sidecar CLI, or an in-process adapter. The transport is
replaceable; the non-replaceable parts are the approved binding, authenticated receipt, retained
content-addressed bytes, deterministic derivation checks, and verified handoff.

## What remains unproved

- The gateway's upstream was really OFAC rather than an impostor.
- The upstream response was complete, truthful, current, or legally sufficient.
- The query semantics covered aliases, ownership rules, or every relevant list.
- A model can author acceptable envelopes with the frozen prompt and schema.
- HMAC with a checked-in fixture key is suitable production authentication.
- JSON Pointer derivation covers unstructured, probabilistic, or multi-source evidence.

SHA-256 proves byte identity. The study HMAC proves that the fixture gateway issued a receipt.
Neither proves factual truth. A stronger origin claim requires source-native signatures or a
production gateway that authenticates and audits its upstream.

## Source-reference boundary

`org.example.input-source.us-ofac.entity-screening` remains a semantic identifier that an AI can
use for matching. It is not an MCP URI, connector, endpoint, credential, query, or authorization.
Deployment configuration binds that id to an already-authorized MCP tool, CLI adapter, API, saved
record, or human workflow.

The source supplies observations such as `/screening/matchCount` and the dated record supporting
it. The pack determines `clear` or `match`. Fetching
`/vendor/sanctionsScreening/status` as if it were an OFAC fact would collapse observation and policy
determination.

## Model-phase infrastructure lesson

Local JSON Schema validity was insufficient to establish compatibility with the hosted
structured-output subset. The replacement model study should freeze a response schema using only
the service-supported subset and validate it through a registered pre-treatment compatibility
probe. That probe must be separate from efficacy cells and must not consume or replace model
results.

## Recommendation

Implement, if needed now, only behind an experimental product flag:

1. keep the semantic source id portable and non-executable;
2. keep the binding lock deployment-local;
3. require the acquisition gateway to persist artifact and receipt before returning;
4. make the deterministic verifier, not the model, admit evaluator inputs;
5. attach an authenticated evaluation receipt to every downstream handoff;
6. reject unverifiable candidates instead of repairing them silently;
7. run a newly preregistered model replication before claiming authoring usability; and
8. require independent commit-relative adversarial review before a material RFC/ADR or stable
   runtime change.
