# Attestation core — external contract

This is the specification a second implementation is built from, clean-room, without reading the
reference implementation in this directory. It exists because studies 006 and 007 checked their
attestation code only against themselves (one hand-written function was oracle, control, grader, and
label at once); the correction, per [ADR-0002](../docs/adr/0002-trustworthy-input-acquisition-research-line.md),
is an external contract two implementations can agree on. Agreement between an implementation built
from this document and the one in this directory is the evidence that the attestation is real and
not self-referential.

The component realizes ADR-0002's item 1: **the attestation core** — content-address, attest, retain,
and exclude the model from the proof path — in its inline (stdio proxy) deployment shape. The same
contract governs a hosted gateway; only the transport and the number of downstream servers change.

## What it guarantees, and what it does not

It guarantees **byte-lineage**: that for every downstream tool result admitted, a receipt records
which tool produced which result at what time, attested by a nameable authority, with the result
retained content-addressed in its canonical form (below) so any later derivation is auditable. It
does **not** guarantee the result is true, complete, current, or from a genuine source — only that
the retained canonical result is the one the named downstream returned for that request, unaltered
since. "SHA-256 proves byte identity … it does not prove factual truth" (Study 006). The self-reported
`serverInfo`, the `command`, and the requested `tool` name are recorded as correlated assertions,
not authenticated identities: the receipt binds the result to a *request for* that tool, not to proof
that a genuine server executed it.

## Trust boundary

The inline shape assumes the **operator**, not the downstream server or the client, controls the key
and the store. Under that assumption it proves a wire-level property: the model neither computes nor carries the
proof — the receipt records the requested tool and a keyed digest of its arguments as what was
*requested*, not as proof — and every successful tools/call result forwarded to the client is
attested or the run fails closed. It does **not** provide OS-level isolation of the key or store from a same-UID
downstream — a downstream running under the proxy's identity could read the key or alter the store.
Structural isolation (a separate identity for the signer, protected append-only storage, one nameable
attestation authority) is the hosted **gateway's** responsibility (ADR-0002). The `authority` field
names the trust root so a verifier configured with the expected authority→key binding can reject
receipts signed by anything else.

## Role

The component is an MCP server to a client and an MCP client to one downstream MCP server, over the
stdio transport (newline-delimited JSON-RPC 2.0, one message per line, no embedded newlines). It
forwards every message in both directions **unaltered**, with two departures from pure forwarding.
First, for each **successful** `tools/call` result flowing downstream→client — a JSON-RPC response
carrying a `result` member, correlated as in *Request correlation* below — before that result is
forwarded, it stamps a receipt and retains the result. Second, on an input it cannot safely attest —
a batch, a duplicate object member name, a duplicate outstanding request id, or any error while
stamping — it **fails the run closed** without forwarding the offending message. A
JSON-RPC *error* response (an `error` member, no `result`) carries nothing to attest and is forwarded
untracked; an MCP application error (`result.isError == true`) is a successful response and IS
attested, with `isError` recorded. A **JSON-RPC batch** (a top-level array) is not supported: it
could carry a tools/call whose result would have to be attested, so the component refuses it and
fails closed rather than forward it unattested. MCP over stdio does not batch.

### Request correlation — normative

Attestation binds a downstream response to the client `tools/call` it answers, by JSON-RPC id.
Because ids are direction-scoped and a stream carries requests and responses both ways, the rule is
exact:

- A **client request** is a client→downstream message with a `method` member **and** an `id` member
  — both by member *presence*, not value. An explicit `method: null` still occupies its id (it is a
  malformed request, but it must be duplicate-checked, not skipped); an absent `method` (a client
  response to a server→client request) is not a request. An explicit `id: null` is an id and is
  recorded; an absent `id` (a notification) is not.
- Ids are compared **by JSON type and value**: `1` (number), `true` (boolean), `1.0` (number), and
  `"1"` (string) are four distinct ids, and none retires another. (The reference tags each id by its
  JSON type before use as a correlation key, so a host language that conflates `true`/`1`/`1.0`
  cannot merge them.)
- A **duplicate outstanding id** — a second client request whose id equals one already outstanding
  under that typed comparison — is a protocol violation the component cannot attest safely, and it
  **fails the run closed**. An id is retired (no longer outstanding) when its response is observed,
  after which the same id may be used again.
- A **downstream response** is a downstream→client message with **no** `method` member, an `id`
  member, and a `result` or `error` member. Only such a message retires the matching outstanding id.
  A server→client request/notification (it has a `method`) and a malformed method-less object with
  neither `result` nor `error` retire nothing — so a later genuine response is still correlated and
  attested.
- The retired request's kind decides what happens: a `tools/call` with a `result` is attested (a
  stamped receipt); an `initialize` result supplies the `downstream.serverInfo`; a `tools/call`
  `error` response and any other request kind are forwarded without a receipt.

A conforming implementation MUST reproduce these correlation decisions; they are as load-bearing as
the receipt format, because a wrong one lets a result reach the client unattested.

### The model is excluded from the proof path — normative

The tool result forwarded to the client MUST be byte-identical to the downstream's result. The
component adds nothing to what the client (and therefore the model) sees. The proof — receipts and
retained artifacts — is written only to the store, and is correlated to downstream tool calls by
`(sessionId, callIndex)`, never by any value the model emits. A verifier or gate reads the store
directly. This is the operative form of ADR-0002's principle: the model gathers and narrates; it
never carries, and cannot corrupt, the proof.

## Canonicalization (`canon`)

Digests and the HMAC are computed over a canonical serialization, so two implementations reproduce
the same bytes. `canon` is defined over a **restricted JSON domain** so it is reproducible; a value
outside the domain is not attestable and MUST fail the run closed rather than be stamped.

The domain is defined on the JSON **wire syntax**, not on a particular parser's typing, so
implementations in different languages agree without depending on int-vs-float distinctions their
parsers may not preserve.

- **Numbers:** the only admissible number token is an integer literal — an optional `-`, then either
  `0` or a non-zero digit followed by digits — whose value is in −(2^53−1) … 2^53−1. A token
  containing `.`, `e`, or `E`, a leading zero, `NaN`/`Infinity`, or an out-of-range value is
  **outside the domain**: `canon` MUST raise and the caller MUST fail closed. (MCP tool results are
  text and small integers; the JPS fact convention carries numbers as decimal *strings*. Non-integer
  canonicalization is deferred to a future RFC 8785 adoption — a `receiptVersion` change.)
- **Strings** are sequences of Unicode scalar values; a lone surrogate is outside the domain.
- **Duplicate member names:** an object with a repeated member name is outside the domain and MUST
  be **rejected** — the run fails closed. Last-value-wins is forbidden, because the ambiguous bytes
  are still forwarded to the client and a reader parsing first-value-wins would then see a different
  value from the one attested; rejecting is the only choice two implementations cannot disagree on.
  (The reference parses with a hook that raises on a repeated name. MCP results do not carry
  duplicate names.)
- **Serialize** with: object members ordered by ascending Unicode code point of the member name; no
  insignificant whitespace (item separator `,`, key/value separator `:`); non-ASCII emitted as raw
  UTF-8, not `\u` escapes; strings escaped minimally (only `"`, `\`, and U+0000–U+001F, the last as
  `\uXXXX` lowercase, except `\b \t \n \f \r` for those five); integers in shortest decimal form
  with no leading zeros, no `+`, `-` only for negatives; `true`, `false`, `null` literal.
- The result is UTF-8 bytes. `canon(v)` denotes those bytes.

Known-answer vectors (a conforming `canon` MUST reproduce these exactly). Byte counts are of the
whole `canon(value)`:

| value | `canon(value)` | bytes |
| --- | --- | --- |
| `{"b":1,"a":2}` | `{"a":2,"b":1}` | 13 |
| `{"k":"é"}` | `{"k":"é"}` — the string `"é"` is the 4 bytes `22 C3 A9 22` | 10 |
| `{"z":[3,2,1],"a":{}}` | `{"a":{},"z":[3,2,1]}` | 20 |
| `{"t":true,"n":null,"x":-5}` | `{"n":null,"t":true,"x":-5}` | 26 |
| `"line\nbreak"` | `"line\nbreak"` — the `\n` is the two bytes `5C 6E` | 13 |

## Digest

`digest(bytes)` = `"sha256:" + lowercase-hex(SHA-256(bytes))`.

An artifact's digest is `digest(canon(result))`, where `result` is the JSON value of the JSON-RPC
`result` member of the downstream's `tools/call` response.

## Receipt

One receipt per successful `tools/call` response observed downstream→client. Fields:

| field | value |
| --- | --- |
| `receiptVersion` | `"1"` |
| `sessionId` | a per-process identifier fixed at startup (≥ 64 bits of entropy, lowercase hex) |
| `callIndex` | 0-based, incremented once per successful `tools/call` response stamped, in the order responses are observed |
| `prevHmac` | the `hmac` of this session's receipt at `callIndex − 1`, or `null` for `callIndex 0`. Chains the receipts so an interior deletion, a reorder, or a receipt replayed into another position is caught at verify time |
| `tool` | the `name` member of the originating `tools/call` request's `params` |
| `argumentsDigest` | `keyedDigest("args", canon(arguments))` of the originating request's `params.arguments` (the `{}` object if absent). It is keyed (below), not a bare digest, so a recorded digest of guessable arguments cannot be reversed by offline guessing without the key; and it is a digest, never the arguments, so a secret in the arguments is not retained |
| `resultDigest` | the artifact digest defined above |
| `isError` | the boolean `result.isError` if present, else `false` |
| `servedAt` | RFC 3339 UTC timestamp, second precision or finer, taken when the response is observed |
| `authority` | the attestation authority identifier (see below) |
| `downstream` | `{ "command": [<argv of the downstream server>], "serverInfo": <the `serverInfo` object from the downstream `initialize` result, or null if not yet seen> }` — self-reported, recorded as an assertion, not authenticated |

`keyedDigest(domain, bytes)` = `"hmac-sha256:" + lowercase-hex(HMAC-SHA256(key, ascii(domain) + ":" + bytes))`.

The receipt object above is `receiptCore`. The stored receipt is `receiptCore` plus one field:

- `hmac` = lowercase-hex(HMAC-SHA256(key, `canon(receiptCore)`)).

`key` is the attestation key: raw bytes read from a keyfile named at startup. `authority` is a
caller-supplied string naming who holds that key (e.g. `"acquisition-proxy:local"` inline, a service
identity when hosted). The pair (`authority`, `hmac`) is what a verifier checks: the authority names
the trust root, the HMAC proves that root issued the receipt. ADR-0002 requires the authority be
nameable and auditable; `authority` is that name, recorded in every receipt.

## Store layout

Rooted at a caller-named directory `store`. The store path and the key are the operator's to
protect (see Trust boundary); the layout below is what this component writes, not a defence against
an external actor with write access to the store.

- `store/artifacts/<hexdigest>` — the exact `canon(result)` bytes, where `<hexdigest>` is the
  `resultDigest` with its `sha256:` prefix removed. Written to a unique temporary name, fsynced, and
  atomically renamed into place; idempotent, since the same bytes reproduce the same digest.
- `store/receipts/<sessionId>/<callIndex>.json` — the stored receipt, `canon(storedReceipt)` bytes
  plus a trailing newline, written to a unique temporary name, fsynced, and hard-linked into place so
  a reader never sees a partial file. **Append-only**: the component MUST refuse to overwrite an
  existing receipt (the link fails if the path exists), and MUST fail closed — stop, surface a
  non-zero result, and NOT forward the result — rather than proceed if it cannot write the receipt.
  A result the component cannot attest MUST NOT be forwarded as if attested.

The key MUST be at least 32 bytes; a shorter key is rejected before any downstream is launched.

## Verification (`verify`)

Given a `store`, the `key`, and optionally an expected `authority`, verification checks every receipt
under `store/receipts/`. Per receipt:

1. Parse the stored receipt; split `hmac` from `receiptCore`.
2. Recompute HMAC-SHA256(key, `canon(receiptCore)`); it MUST equal `hmac` (`hmac-mismatch` otherwise).
3. The receipt's signed identity MUST match where it is stored: `receiptCore.sessionId` equals the
   containing directory name and `receiptCore.callIndex` equals the file's stem, so a valid receipt
   copied or renamed into another slot is rejected (`misfiled`).
4. If an expected `authority` was given, `receiptCore.authority` MUST equal it (`authority-mismatch`).
5. Read `store/artifacts/<resultDigest without prefix>`; `digest(those bytes)` MUST equal
   `receiptCore.resultDigest` (`artifact-missing` / `artifact-mismatch`).

Per session, over the receipts that verified individually:

6. `callIndex` MUST be the contiguous range `0 .. n−1` (`sequence-broken` otherwise). Duplicate
   indices cannot occur, since the index is the filename and step 3 binds it.
7. The `prevHmac` chain MUST link: receipt `0` has `prevHmac == null`, and each receipt `i` has
   `prevHmac == hmac(i−1)` (`chain-broken` otherwise). This catches interior deletion, reordering,
   and a receipt replayed into another position within the session.

A store verifies iff every receipt is `ok` and every session's sequence and chain are intact. Per-receipt
statuses: `ok`, `hmac-mismatch`, `misfiled`, `authority-mismatch`, `artifact-missing`,
`artifact-mismatch`, `malformed`; per-session: `sequence-broken`, `chain-broken`.

**Residuals, stated plainly.** The chain and location binding reject a receipt that is tampered,
forged without the key, copied or renamed into another slot, reordered, or interior-deleted — within
the sessions present in the store. Two attacks by an actor with store write access are **not** caught
and need an external anchor the inline shape does not have:

- **Final-tail rollback** — deleting the last *k* receipts of a session leaves a shorter prefix that
  is itself intact and chained, and verifies. Detecting it needs an external anchor on the session's
  final count.
- **Whole-session replay / mixing** — an entire genuine past session (or a genuine prefix of one),
  copied verbatim under its own signed directory, is internally consistent and verifies. `verify`
  has no registry of which sessions are expected, and an empty or absent receipts directory verifies
  as vacuously true. A gate MUST therefore confirm that the sessions and count it expected are
  present; `verify` proves each present receipt's integrity, not that the store is the complete and
  current set.

Both anchors — an expected-session registry and a final-count seal — are the hosted gateway's
responsibility (ADR-0002), not the inline shape's.

## Conformance

Two implementations conform iff, over the same downstream server, the same sequence of client
messages, and the same key and authority, their stores agree after **normalization**. For each
receipt, form the normalized core by replacing `sessionId` with a fixed placeholder, dropping
`servedAt`, and dropping `prevHmac` — all three are per-run: `sessionId` and `servedAt` obviously,
and `prevHmac` because it is the HMAC of the *previous* run-specific core and so differs between runs
even when the content is identical. Then: the normalized cores MUST canonicalize identically across
the two implementations; each store MUST independently pass `verify` under the shared key (which
checks the *un-normalized* chain within its own run); and the artifacts MUST be byte-identical under
identical `resultDigest`s. Stored `hmac`s are NOT compared directly across runs — each is re-verified
within its own store. A conformance harness drives both implementations with a recorded client
transcript and a stub downstream returning fixed results, and diffs the normalized stores.
