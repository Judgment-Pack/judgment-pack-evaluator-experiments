# Attestation core

A general trusted component for the trustworthy-input-acquisition line
([ADR-0002](../docs/adr/0002-trustworthy-input-acquisition-research-line.md), item 1). It sits
between an MCP client and one downstream MCP server, forwards every message **unaltered**, and for
each `tools/call` result it content-addresses the bytes, issues an attested receipt, and retains the
bytes — so a later gate can prove that a fact the pack evaluated derives from bytes a named authority
attested at a known time. It replaces studies 006/007's bespoke synthetic gateway with one component
that attests **any** downstream MCP server, and its contract lives in [`SPEC.md`](SPEC.md) so a second
implementation can be built clean-room and agreement-tested — the discipline those studies lacked.

It guarantees **byte-lineage, not truth**: that the retained canonical result is the one the named
downstream returned for that request, unaltered since. It says nothing about whether that result is
true, complete, current, or from a genuine source, and the recorded `serverInfo`, `command`, and
`tool` name are self-reported assertions, not authenticated identities.

This is the *inline* deployment shape (a stdio proxy). The same contract governs a hosted gateway for
scale — one signing identity, many sources, network transport, central binding policy — which ADR-0002
records as the deployment target. The guarantee is identical in both shapes, which is why it is
established here in the smallest trusted base.

## Trust boundary — wire-level here, OS-level in the gateway

The inline shape assumes the **operator**, not the downstream or the client, controls the key and the
store. Under that assumption it proves a **wire-level** property: the model neither computes nor carries the proof — the receipt records the requested tool and a keyed digest of its arguments as what was *requested*, not as proof — and nothing it emits enters the
proof, and every successful tools/call result forwarded to the client is attested or the run fails
closed. It does **not** isolate the key or store from a same-UID downstream at the OS level — that,
along with one protected attestation authority, is the hosted gateway's job (ADR-0002). The claim here
is model-exclusion on the wire, not structural OS isolation.

The result forwarded to the client is byte-identical to the downstream's; the component adds nothing
the model sees. The model neither authors nor carries the proof — the receipt records what the model
*requested* (the tool name, a keyed digest of the arguments), but the proof itself (the result
digest, the chain, the HMAC) is computed by the component, never supplied by the model. This is the
operative form of the studies' finding that the model classifies well but carries digests and pointers
un-trustably (Study 007: facts exact 24/24, every failure a lineage-authoring slip).

Receipts are hash-chained (`prevHmac`) and their signed `(sessionId, callIndex)` must match where they
are stored, so `verify` rejects a receipt tampered, forged, relabeled, reordered, cross-position
replayed, or interior-deleted. Two residuals it cannot catch alone, both needing an external anchor
that is the gateway's job: truncation of a session's *final* receipts, and replay of a whole genuine
past session under its own directory (`verify` proves each present receipt's integrity, not that the
store is the complete, current set a gate expected). See [`SPEC.md`](SPEC.md).

## Use

```bash
# Wrap any downstream MCP server. The client speaks to this process's stdio;
# it speaks to the downstream. Every tools/call result is attested.
python3 attest.py wrap ./store ./key --authority "acquisition-proxy:local" -- jpack mcp

# Verify every receipt against the key and the retained artifacts.
python3 attest.py verify ./store ./key
```

`./key` is raw key bytes (`head -c 32 /dev/urandom > key`). `--authority` names who holds the key —
the trust root recorded in every receipt (ADR-0002 requires it be nameable and auditable).

The store is append-only: `store/artifacts/<hexdigest>` holds the exact canonical result bytes, and
`store/receipts/<sessionId>/<callIndex>.json` holds the attested receipt. A result the component
cannot attest is not forwarded as if it were — it fails closed.

## Test

```bash
python3 -m unittest test_attest -v
```

Tests cover canonicalization known-answer vectors and domain rejection, the keyed arguments digest,
the append-only store, every verifier finding (`hmac-mismatch`, `misfiled`, `authority-mismatch`,
`artifact-missing`, `artifact-mismatch`, `sequence-broken`, `chain-broken`), receipt replay / rename /
interior-deletion / relink, weak-key refusal, and — driving a live stub server — raw-byte-identical
forwarding, the two-call chain, a JSON-RPC error response producing no receipt, an MCP `isError:true`
result being attested, and a batch failing closed without being forwarded. One integration test wraps
the real `jpack mcp` and skips when no `jpack` is on PATH.

## Standard library only

Like the agreement track's `python/`, no third-party dependency, so a clean-room second implementation
from `SPEC.md` faces the same surface and their agreement is real evidence rather than shared code.
