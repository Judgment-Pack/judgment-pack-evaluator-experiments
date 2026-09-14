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
its key id); the in-toto layer verifies under that key alone.

## 3. What the binding asserts

Beyond what DSSE and the Statement assert, the binding asserts, per attestation:

1. the predicate is exactly the receipt the store holds under that session and index — the
   same document, compared by canonical serialization;
2. the `artifact` subject's digest is the predicate's `resultDigest`;
3. for an action: the `decision-record` subject's digest is the predicate's
   `action.decision.recordDigest`, and the set of `cites/…` subjects is exactly one per entry
   of the predicate's `action.cites`, named by that entry's session and index;
4. no other subject is present.

These are the rules a consumer needs beyond in-toto's own to read an attestation as being
*about* its receipt; without them an attestation can verify as an attestation and vouch for
the wrong thing (cells `b03`, `b08`, `b09`).

## 4. The three layers

- **gateway** — the pinned `gateway verify` over the store, the registry, the authority and the
  decision-record directory, under the corpus public key on stdin: `ok` and the findings'
  statuses (`SPEC.md` §1.4 per receipt, §4 per session and registry, §4 steps 5–7 the joins).
  It reads no attestation.
- **intoto** — the reference implementation's ceremony (§5). It reads no gateway key and runs
  no gateway code; what it sees is what an in-toto consumer sees.
- **binding** — §3, checked by `adapter/verify_binding.py`. It verifies no signature and
  resolves no citation; it compares the statement with the store's receipt file and with
  itself.

The combined verdict is `pass` only when all three pass. No layer stands in for another.

## 5. The in-toto layer's ceremony

For every receipt the store holds, in this order, the first failure ending the attestation's
verification:

1. an attestation is present at its path, or `fail:missing-attestation`;
2. the envelope parses, or `fail:unparseable`; its `payloadType` is
   `application/vnd.in-toto+json`, or `fail:payload-type`;
3. a signature by the pinned adapter key is present — the signature's key id is the pinned
   one, or `fail:untrusted-key` — and `securesystemslib` verifies it over the PAE of the
   payload type and the payload, or `fail:signature`; then `dsse` is `pass`;
4. the payload is JSON, or `invalid:not-json`; its `_type` is Statement v1, or
   `invalid:statement-type`; its `predicateType` is the registered one, or
   `invalid:predicate-type`; the `in-toto-attestation` bindings validate it, or
   `invalid:bindings`; then `statement` is `valid`;
5. each subject is re-digested against what it names: `artifact` against the file under the
   store's `artifacts/` at that digest (`match`, `mismatch`, or `missing`); `decision-record`
   against the candidates the gateway's rule enumerates under the decision-record directory —
   every regular file whole and, for a `.jsonl` file, additionally each line (`match` or
   `missing`; a consumer needs that rule to place the subject, and this ceremony adopts it);
   `cites/<session>/<index>` against that receipt file's bytes (`match`, `mismatch`, or
   `missing`); any other name is `unknown-subject`.

The layer passes when every attestation reaches step 5 and every subject matches.

## 6. The reduced form the registration compares

Per cell, the scorer compares the observed outcome with the registered one in this form:

- `gateway`: `ok` (Boolean) and the sorted set of distinct finding statuses;
- `intoto`: `pass` and, per attestation that did not fully pass, its first failure — the
  `dsse` code if not `pass`, else the `statement` code if not `valid`, else the map of
  subjects that did not `match` to their outcome;
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
of a receipt signed under another gateway key is as good an attestation as any (`c01`).
