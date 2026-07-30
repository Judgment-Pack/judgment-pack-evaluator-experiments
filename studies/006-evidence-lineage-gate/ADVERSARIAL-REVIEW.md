# Preliminary adversarial review — Study 006

## Review status

This is an internal red-team pass by the same OpenAI-assisted project that designed and ran the
study. It is not the independent, cross-vendor, commit-relative review required for a material JPS
or stable-runtime change.

## Strongest contrary interpretation

The study demonstrates a conventional authenticated data pipeline, not a general proof of
evidence. Phase A is deterministic and uses attacks chosen by the implementation author. Passing
those fixtures can show that the registered checks work, but not that the attack set is complete or
that the trusted gateway deserves trust. Phase B produced no model observation. Therefore the
study cannot support claims about real MCP reliability, AI authoring success, OFAC provenance, or
factual correctness.

## Attacks that still cross the boundary

- The trusted gateway is compromised or signs fabricated bytes.
- Valid receipts are replayed where cell, tenant, purpose, nonce, or expiry checks are incomplete.
- The gateway authenticates a server but not the exact upstream query or response semantics.
- A source omits records while returning a syntactically valid and freshly signed response.
- Two individually valid artifacts are combined through an unverified transformation.
- Canonicalization differs across languages, numeric types, Unicode normalization, or duplicate
  JSON keys.
- A content-addressed artifact is verified and then a different file descriptor is consumed
  through a time-of-check/time-of-use error.
- A key is leaked, shared across environments, insufficiently rotated, or not bound to an issuer
  and algorithm.
- An approved source id is rebound after approval without invalidating old locks and receipts.
- A downstream system accepts a naked disposition and discards its evaluation receipt.

## Architecture challenges

1. **MCP is transport, not provenance.** A tool-call transcript proves what the client observed
   only to the extent that the MCP server and transcript recorder are trusted. The gateway must
   attest the exact returned bytes and binding.
2. **The model must not be the verifier.** A model can select a tool and propose claims, but it
   cannot be trusted to decide that its own lineage is valid.
3. **The evaluator must receive admitted bytes directly.** Serializing verified values back
   through an editable agent message reopens the handoff.
4. **Receipts need a consumption policy.** Cryptographic validity without subject, tenant,
   freshness, purpose, and replay checks is insufficient.
5. **Evidence availability is not evidentiary sufficiency.** `present` says the registered item is
   available; it does not prove that the item supports the legal or factual conclusion.
6. **One-source JSON Pointer mapping is the easy case.** Joins, OCR, fuzzy entity resolution,
   ranking, human attestations, and probabilistic extraction need explicit transformation records
   and possibly independent verification.

## Method threats

- One synthetic domain, one pack, one fact, one evidence requirement, and eight mutations.
- The trusted components and attacks were authored together.
- The fixed HMAC key and filesystem do not model production identity, isolation, or key custody.
- No concurrency, replay, race, multi-tenant, multi-source, key-rotation, or crash-recovery tests.
- No malicious gateway or valid-but-incomplete source response.
- No source-native signature and no actual OFAC integration.
- D4 was computed by a post-Phase-A reporting repair over retained artifacts.
- The hosted model phase never began because the response schema failed service validation twice.

## Minimum bar for implementation

- Threat-model and test issuer identity, key custody, replay, tenant/purpose binding, expiry, key
  rotation, canonicalization, crash consistency, and time-of-check/time-of-use behavior.
- Define receipt versioning and algorithm agility.
- Keep raw artifacts immutable and address them by verified digest.
- Make evaluator invocation consume the verifier's in-memory or sealed output, not an agent-edited
  copy.
- Require downstream receipt verification and fail closed when the receipt is missing.
- Add multi-source and transformation manifests before claiming general evidence lineage.
- Add source-authentication evidence before naming a real institution as origin.
- Complete a newly preregistered model-authoring replication with a hosted-compatible schema.
- Obtain an independent review against exact repository commits.

## Recommendation

Do not standardize the full envelope now. Preserve Study 006 as evidence for an experimental
product-layer pattern: semantic source identifier, deployment binding, authenticated acquisition
receipt, immutable artifact, deterministic verifier, sealed evaluator handoff, and authenticated
evaluation receipt. Standardize only after production threat-model work, successful replication,
and independent adversarial review.
