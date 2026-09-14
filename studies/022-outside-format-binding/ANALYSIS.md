# Analysis — Study 022 primary attempt

**Attempt**: `results/primary-attempt-001`, the first invocation of the governing command from
the freeze commit (`84b35185`, the squash-merge of PR #106); label `REGISTERED`, attempt id
`110ef6ff3c41840d70d1a649621d4403`; the gateway at commit `03582d9` (binary
`aaa16fec…`), CPython 3.8.20, the seven pinned distributions (securesystemslib 1.3.1,
in-toto-attestation 0.9.3, cryptography 47.0.0, protobuf 5.29.6, cffi, pycparser,
typing_extensions). Fully offline: no model, no external service, no fetch. The trusted
bootstrap hashed every pinned distribution and every study module before importing anything;
every freeze pin held; every cell was rebuilt from the baseline and compared byte for byte,
and every observation was recomputed by the scorer over the rebuilt cell and found equal. This
document is post-run analysis; the preregistration and its pinned artifacts govern.

## Verdicts

- **R1 (the locked stratum)**: `R1 holds (REGISTERED)` — 19 locked cells, 19 adjudicated, **0
  divergent**, 0 validity failures, both control gates green (the positive control passes all
  three layers; the negative control fails exactly at the reference implementation's signature
  check).
- **The reviewer's holdout (first construction through the harness)**: **6/6 hold**, 0
  unconstructed. Two of the six — `h01` (the key file beside the envelopes replaced together
  with both envelopes) and `h02` (a duplicated citation subject with the bad digest first) —
  were written by the reviewer against the round-1 implementation, which would have accepted
  both; the frozen implementation refuses them exactly as the reviewer registered. `h05` (the
  decision book's bytes changed while its one record candidate is preserved) passes all three
  layers, as the reviewer predicted from the gateway's candidate rule.

## What each verifier owns — the ownership map (R2)

Every cell's reduced outcome is in the table at the end; grouped by which layer saw the
change, the map the study was run to draw:

| seen by | cells | what the change was |
|---|---|---|
| **the gateway only** | `a05`, `c01`, `h03`, `h04` | the seal registry emptied; the whole store re-minted under another gateway key; a decision record with malformed citations; the action receipt removed below the seal's count |
| **the in-toto layer only** | `neg`, `b02`, `b04`, `b05`, `b07`, `h01` | a signature byte flipped (upstream DSSE); a signature under an unpinned key, with or without the key file beside it (the ceremony's key selection); the predicate type, the statement type, the payload type changed (the ceremony's pins) |
| **the binding only** | `b03`, `b08`, `b09` | a validly re-signed attestation whose artifact subject points elsewhere, whose predicate is not the stored receipt, or whose subjects omit a citation |
| **the gateway and the in-toto layer** | `a01`, `a03`, `a04` | the artifact's bytes changed; the cited receipt removed; the decision record rewritten — each seen by the gateway's own check and by the consumer's re-digest of a subject |
| **the gateway and the binding** | `a07` | a signed member of the action receipt changed in the store: the gateway's signature check, and the binding's predicate-equals-store rule; the attestation itself is untouched and verifies |
| **the in-toto layer and the binding** | `b01`, `b06`, `h02`, `h06` | the payload altered without re-signing; the attestation deleted; a duplicated citation subject; an emptied subject list |
| **all three** | `a02`, `a06` | a cited receipt's member changed; a receipt appended after the seal — the non-gateway layers see the second only by the ceremony's one-attestation-per-receipt rule |
| **none** | `pos`, `h05` | the baseline; the book's bytes changed while its record candidate is preserved |

Read as the registered account said to read it:

- **What an in-toto consumer sees of a receipt is what re-digest reaches**: the artifact, the
  cited receipt's bytes, the decision record — because the binding names them as subjects. It
  is exactly the store's bytes, and nothing about them but their identity.
- **What only the gateway's key covers, no attestation carries**: the seal, the chain, the
  count, and the gateway's own identity. A store re-minted under another gateway key (`c01`)
  attests and verifies exactly as the genuine one does, and a store whose seal is gone (`a05`)
  is as good an attestation as any. The binding carries no gateway-key trust across; a
  consumer that wants it must verify the receipt inside the predicate under the gateway's key
  by the gateway's own rule — which this ceremony, by design, does not.
- **What only the binding's rules see** is a self-consistent attestation about the wrong
  thing (`b03`, `b08`, `b09`): valid as an attestation, vouching for another artifact or for a
  receipt the store does not hold. Without the binding's rules the outside format's consumer
  has no way to tell, and those rules are this study's, not in-toto's.
- **The consumer's pins are policy, not the format's**: `b04`, `b05`, `b07` are caught by what
  this ceremony pins, and a consumer that pinned less would accept them; `b02` and `h01` are
  caught by the ceremony's key selection under a key handed in from outside the cell, and a
  consumer that trusted the key file beside the envelopes would accept `h01` — as the round-1
  implementation did.
- **The joins are the gateway's alone** (`h03`, `h04`): a record that cites, and a session's
  count against its seal, are things no attestation names.

## Claims and non-claims

What is claimed: on this store, under the pinned gateway and the pinned reference
implementation, the map above — every cell's outcome on every layer landing where the
registration derived it from the three specifications, and the reviewer's six cells where the
reviewer wrote them. R1 is a conformance result: 25 registered expectations, all met.

What is not claimed (§7–§8 of the preregistration): nothing about any deployment, any real
store, or any consumer but the one the ceremony describes; nothing about the binding being the
right one — it is one the plan's rules admit; nothing about a compromised gateway; nothing
about a passing attestation meaning the receipt is true (byte-lineage, not truth, on both
sides of the binding); and nothing about the trusted computing base §7 names — the interpreter
build, its library, the native libraries, the operating system.

## What this is the registered input to

RFC 0014's third unresolved point asked what an outside format's consumer can and cannot see
of a receipt. The answer this study registers: by re-digest, the bytes the binding names and
nothing else; the seal, the chain, the count and the gateway's identity never; and what makes
an attestation *about* its receipt is a rule the binding adds, not one the format has.

## The holdout

| cell | the reviewer's expectation | observed | verdict |
|---|---|---|---|
| `h01-foreign-key-file-and-envelopes` | gateway ok; in-toto `fail:untrusted-key` on both; binding pass | as expected | holds |
| `h02-duplicate-citation-subject-bad-first` | gateway ok; in-toto `cites/s2/0` mismatch; binding `fail:cites-subject-set` | as expected | holds |
| `h03-unreferenced-record-malformed-cites` | gateway not ok, `record-citation-malformed`; in-toto pass; binding pass | as expected | holds |
| `h04-action-tail-removed-orphan-kept` | gateway not ok, `tail-rollback`; in-toto pass; binding pass | as expected | holds |
| `h05-jsonl-crlf-and-empty-lines` | all three pass | as expected | holds |
| `h06-empty-subject-list-resigned` | gateway ok; in-toto `invalid:bindings`; binding `fail:artifact-subject-mismatch` | as expected | holds |

## Every cell's reduced outcome

| cell | gateway | in-toto (first failure per attestation) | binding | combined | verdict |
|---|---|---|---|---|---|
| `pos-baseline` | ok ok | pass | pass | pass | holds |
| `neg-dsse-signature-flipped` | ok ok | s2/1.dsse.json: fail:signature | pass | fail | holds |
| `a01-artifact-edited` | not ok artifact-mismatch, ok | s2/1.dsse.json: artifact mismatch | pass | fail | holds |
| `a02-cited-receipt-member-edited` | not ok ok, sequence-broken, signature-mismatch | s2/1.dsse.json: cites/s2/0 mismatch | s2/0.dsse.json: fail:predicate-differs-from-store | fail | holds |
| `a03-cited-receipt-removed` | not ok citation-unresolved, ok, sequence-broken, tail-rollback | s2/1.dsse.json: cites/s2/0 missing | pass | fail | holds |
| `a04-decision-record-rewritten` | not ok decision-record-mismatch, ok | s2/1.dsse.json: decision-record missing | pass | fail | holds |
| `a05-registry-seal-removed` | not ok ok, unregistered-session | pass | pass | fail | holds |
| `a06-receipt-appended-after-seal` | not ok count-exceeds-seal, misfiled, ok | s2/2.dsse.json: fail:missing-attestation | s2/2.dsse.json: fail:missing-attestation | fail | holds |
| `a07-action-member-edited` | not ok ok, signature-mismatch | pass | s2/1.dsse.json: fail:predicate-differs-from-store | fail | holds |
| `b01-envelope-payload-edited` | ok ok | s2/1.dsse.json: fail:signature | s2/1.dsse.json: fail:predicate-differs-from-store | fail | holds |
| `b02-envelope-resigned-foreign-key` | ok ok | s2/1.dsse.json: fail:untrusted-key | pass | fail | holds |
| `b03-subject-swapped-resigned` | ok ok | pass | s2/1.dsse.json: fail:artifact-subject-mismatch | fail | holds |
| `b04-predicate-type-changed-resigned` | ok ok | s2/1.dsse.json: invalid:predicate-type | pass | fail | holds |
| `b05-statement-type-changed-resigned` | ok ok | s2/1.dsse.json: invalid:statement-type | pass | fail | holds |
| `b06-attestation-deleted` | ok ok | s2/1.dsse.json: fail:missing-attestation | s2/1.dsse.json: fail:missing-attestation | fail | holds |
| `b07-payload-type-changed` | ok ok | s2/1.dsse.json: fail:payload-type | pass | fail | holds |
| `b08-predicate-receipt-edited-resigned` | ok ok | pass | s2/1.dsse.json: fail:predicate-differs-from-store | fail | holds |
| `b09-cited-subject-dropped-resigned` | ok ok | pass | s2/1.dsse.json: fail:cites-subject-set | fail | holds |
| `c01-store-reminted-other-gateway-key` | not ok key-mismatch | pass | pass | fail | holds |
| `h01-foreign-key-file-and-envelopes` | ok ok | s2/0.dsse.json: fail:untrusted-key; s2/1.dsse.json: fail:untrusted-key | pass | fail | holds |
| `h02-duplicate-citation-subject-bad-first` | ok ok | s2/1.dsse.json: cites/s2/0 mismatch | s2/1.dsse.json: fail:cites-subject-set | fail | holds |
| `h03-unreferenced-record-malformed-cites` | not ok ok, record-citation-malformed | pass | pass | fail | holds |
| `h04-action-tail-removed-orphan-kept` | not ok ok, tail-rollback | pass | pass | fail | holds |
| `h05-jsonl-crlf-and-empty-lines` | ok ok | pass | pass | pass | holds |
| `h06-empty-subject-list-resigned` | ok ok | s2/1.dsse.json: invalid:bindings | s2/1.dsse.json: fail:artifact-subject-mismatch | fail | holds |
