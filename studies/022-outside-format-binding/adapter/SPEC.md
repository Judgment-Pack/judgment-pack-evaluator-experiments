# The receipt attestation — binding a gateway receipt into an in-toto attestation

Status: REGISTERED — pinned by the Study 022 preregistration at the freeze (the digest in
`harness/PINS.json` governs). This document is the adapter's contract: how a gateway store is
bound into in-toto attestations, what each layer of verification holds, and what none does.
The adapter modifies neither format; it composes them.

Vocabulary: "the gateway" is the judgment-pack gateway at the pinned commit, whose `SPEC.md`
(§1.1 canonical form, §1.2a the version 3 receipt, §1.4 the verification ladder, §4 the
registry-anchored verification and the two joins) governs every receipt-side term here; "DSSE"
is the Dead Simple Signing Envelope as `securesystemslib` implements it at the pinned version;
"Statement" is the in-toto Statement v1 (`https://in-toto.io/Statement/v1`) as the
`in-toto-attestation` bindings validate it at the pinned version.

## 1. The attestation

For every receipt file `receipts/<session>/<index>.json` the store holds, one attestation
`attestations/<session>/<index>.dsse.json`: a DSSE envelope of payload type
`application/vnd.in-toto+json` whose payload is one Statement, serialized with sorted member
names and no whitespace:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {"name": "artifact",        "digest": {"sha256": "<resultDigest's hex>"}},
    {"name": "decision-record", "digest": {"sha256": "<action.decision.recordDigest's hex>"}},
    {"name": "cites/<session>/<index>", "digest": {"sha256": "<sha256 of the cited receipt file's bytes>"}}
  ],
  "predicateType": "https://judgment-pack.dev/attestation/gateway-receipt/v3",
  "predicate": { ...the receipt, verbatim as stored... }
}
```

The `artifact` subject is on every attestation. The `decision-record` subject and one
`cites/…` subject per citation are on an action receipt's attestation and on no other. The
predicate type is a URI this study registers for the receipt shape and nothing else; it is not
a published in-toto predicate type, and the ceremony pins it (§5) so that an attestation of
another type is not taken for one of these. The predicate is the receipt as the store holds it
— every member the gateway signed, its signature included — so a consumer holding the
gateway's public key can verify the receipt inside the attestation by the gateway's own rule,
which this ceremony does not do.

## 2. The envelope and the adapter's key

The envelope is signed with the **adapter's** Ed25519 key, derived from a fixed seed in
`adapter/bind.py` (its key id is pinned); the key is study-minted, not a secret, and **not the
gateway's key**. The two trust roots stay apart on purpose: the gateway's key vouches for the
receipt, the adapter's key for the attestation, and what the binding does and does not carry
across from one to the other is what the study measures (cell `c01`). The public half is
written beside the attestations as `adapter.pubkey.json` (`securesystemslib`'s key form with
its key id) for a consumer's convenience; **the ceremony does not trust that file**. The in-toto
layer verifies under the pinned adapter key handed in from outside the cell — the study's
fixture copy of that file, held to the pinned key id and key material before any attempt runs
(`harness/pins.py`) — so a key file substituted beside the envelopes changes nothing the layer
trusts (the reviewer's holdout `h01` probes this boundary).

## 3. What the binding asserts

Beyond what DSSE and the Statement assert, the binding asserts, per attestation:

1. the predicate is exactly the receipt the store holds under that session and index — the
   same document, compared by canonical serialization;
2. the `artifact` subject's digest is the predicate's `resultDigest`;
3. for an action: the `decision-record` subject's digest is the predicate's
   `action.decision.recordDigest`, and the `cites/…` subjects are exactly one per entry of the
   predicate's `action.cites`, named by that entry's session and index — one subject per
   citation and no more, by multiplicity, so a second subject under a citation's name breaks
   the rule as a missing one does;
4. no other subject is present.

These are the rules a consumer needs beyond in-toto's own to read an attestation as being
*about* its receipt; without them an attestation can verify as an attestation and vouch for
the wrong thing (cells `b03`, `b08`, `b09`).

### 3a. The binding layer's codes and their precedence

`adapter/verify_binding.py` checks the rules in this order per stored receipt and reports the
first broken as the attestation's code; `pass` when none is:

1. `fail:missing-attestation` — no directory entry at the receipt's attestation path. A path
   that is present but not a plain file — a directory, a symbolic link, a device — is not
   absence and not an outcome: it is an I/O failure on the validity channel. Receipts are
   enumerated as the gateway enumerates them (its `SPEC.md` §3a): per session directory,
   every non-directory `.json` entry, by name;
2. `fail:unreadable` — the envelope does not parse, its payload is not a JSON object, its
   `subject` is not a list, a subject is not an object with a string `name` and a `digest`
   object holding a string `sha256` of 64 lowercase hex characters, the stored receipt is
   not a JSON object, the predicate is not an object, or — for a predicate whose `kind` is
   `action` — its `action` is not an object, its `action.decision` is not an object, or its
   `action.cites` is not a list of objects each with a string `sessionId` and an integer
   `callIndex`. Shapes are checked before any member is read, so a malformed input gets this
   code and never an exception;
3. `fail:predicate-differs-from-store` — rule 1;
4. `fail:artifact-subject-mismatch` — rule 2 (the `artifact` subjects are not exactly one, or
   its digest is not the predicate's `resultDigest`);
5. `fail:decision-subject-mismatch` — rule 3, the record subject (an action only);
6. `fail:cites-subject-set` — rule 3, the citation subjects (an action only);
7. `fail:foreign-subject` — rule 4, a check of names only: multiplicities were settled by
   rules 2 and 3, so a predicate that cites the same receipt twice, with two matching
   subjects, passes (the gateway imposes no uniqueness on citations and neither does the
   binding).

The layer verifies no signature and reads no key: an attestation signed by anyone, or by no
one, is held to the same rules. A file the layer cannot read for an I/O reason is not an
outcome: the exception propagates, the observation aborts, and the attempt is pipeline-invalid
(the validity channel, `PREREGISTRATION.md` §5).

## 4. The three layers

- **gateway** — the pinned `gateway verify` over the store, the registry, the authority and the
  decision-record directory, under the corpus public key on stdin: `ok` and the findings'
  statuses (`SPEC.md` §1.4 per receipt, §4 per session and registry, §4 steps 5–7 the joins).
  It reads no attestation.
- **intoto** — a **study-written consumer ceremony using unmodified DSSE verification and
  unmodified Statement validation** (§5): `securesystemslib` verifies the envelope's
  signature and `in-toto-attestation` validates the Statement's shape, both consumed at pinned
  versions and modified nowhere; everything else in §5 — enumerating the store's receipts,
  requiring an attestation per receipt, pinning the payload type, the statement type and the
  predicate type, resolving each subject and re-digesting it — is this study's consumer
  policy, and §5 marks which step is whose. It reads no gateway key and runs no gateway code;
  what it sees is what an in-toto consumer following this ceremony sees.
- **binding** — §3, checked by `adapter/verify_binding.py`. It verifies no signature and
  resolves no citation; it compares the statement with the store's receipt file and with
  itself.

The combined verdict is `pass` only when all three pass. No layer stands in for another.

## 5. The in-toto layer's ceremony

For every receipt the store holds, in this order, the first failure ending the attestation's
verification. Each step says whose check it is: **[consumer]** is this study's policy,
**[upstream]** is the pinned implementation's own code, called as shipped.

1. **[consumer]** an attestation is present at its path, or `fail:missing-attestation` —
   presence and enumeration exactly as §3a item 1 states them (absence is no directory
   entry; a present non-file is an I/O failure);
2. **[upstream parse, consumer pin]** the envelope parses as a DSSE envelope
   (`Envelope.from_dict`), or `fail:unparseable`; its `payloadType` is
   `application/vnd.in-toto+json`, or `fail:payload-type`;
3. **[consumer selection, upstream verification]** a signature under the pinned adapter key's
   id is present in the envelope, or `fail:untrusted-key` (the key is the one §2 hands in,
   never the cell's file); `securesystemslib` verifies that signature over the PAE of the
   payload type and the payload, or `fail:signature`; then `dsse` is `pass`;
4. **[consumer pins, upstream validation]** the payload is JSON, or `invalid:not-json`; it is a
   JSON object, or `invalid:not-object`; its `_type` is Statement v1, or
   `invalid:statement-type`; its `predicateType` is the registered one, or
   `invalid:predicate-type`; the Statement **as supplied** is converted by the pinned
   protobuf JSON mapping (`google.protobuf.json_format.ParseDict` into the bindings'
   `Statement` message: every member as the mapping defines it, `content` as base64 text
   included; a member the message defines no field for, or a member of the wrong type, is
   refused by the mapping) and the `in-toto-attestation` bindings' own `validate()` runs on
   the result; either refusal is `invalid:bindings`; then `statement` is `valid`;
5. **[consumer]** every subject is re-digested against what it names and every outcome is
   retained, in the statement's order: `artifact` against the file under the store's
   `artifacts/` at that digest (`match`, `mismatch`, or `missing`); `decision-record` against
   the candidates the gateway's rule enumerates under the decision-record directory — every
   regular file whole and, for a `.jsonl` file, additionally each line (`match` or `missing`;
   a consumer needs that rule to place the subject, and this ceremony adopts it);
   `cites/<session>/<index>` — exactly three path segments, the index digits — against that
   receipt file's bytes (`match`, `mismatch`, or `missing`); any other name, or a subject whose
   name is not a string or whose `digest.sha256` is not 64 lowercase hex characters, is
   `unknown-subject` — the digest's syntax is checked before any path is formed from it. A later subject under
   the same name does not replace an earlier outcome: the per-name rule is §6's.

The layer passes when every attestation reaches step 5 with at least one subject and every
subject outcome is `match`. Shapes are checked before members are read at every step, so a
malformed input gets a code and never an exception; a file the layer cannot read for an I/O
reason is not an outcome — the exception propagates, the observation aborts, and the attempt
is pipeline-invalid (`PREREGISTRATION.md` §5).

## 6. The reduced form the registration compares

Per cell, the scorer compares the observed outcome with the registered one in this form:

- `gateway`: `ok` (Boolean) and the sorted set of distinct finding statuses;
- `intoto`: `pass` and, per attestation that did not fully pass, its first failure — the
  `dsse` code if not `pass`, else the `statement` code if not `valid`, else the map from
  subject name to outcome for each name whose outcomes are not all `match`, the outcome being
  **the first that is not `match` in the statement's order** (so a later subject under the
  same name cannot erase an earlier failure — the reviewer's holdout `h02`); a valid
  statement with no subject outcome does not pass and reduces to an empty map (unreachable
  under the bindings, which require a subject; stated so the rule is total);
- `binding`: `pass` and, per attestation that did not pass, its code;
- `combined`: `pass` or `fail`.

Equality of this form is the cell's endpoint.

## 7. What each layer owns, and what none does

The gateway owns everything under its key: receipt signatures, chain, seal, count, the joins.
The in-toto layer owns the attestation's own integrity — its signature under the adapter's
key, its shape — and, by re-digest, the correspondence of each subject with the store; it
owns nothing the attestation does not name (no seal, no chain, no count) and cannot tell a
predicate from a store receipt. The binding owns the correspondence of the attestation with
its receipt. None of them owns the gateway's key from the attestation's side: an attestation
of a receipt signed under another gateway key is as good an attestation as any (`c01`). The
predicate carries the gateway's own members — `keyId`, `prevSignature`, `signature`, the
citations' signatures — as bytes the adapter copied from the store; the in-toto layer and the
binding compare them and interpret none of them, and neither verifies a receipt signature.
