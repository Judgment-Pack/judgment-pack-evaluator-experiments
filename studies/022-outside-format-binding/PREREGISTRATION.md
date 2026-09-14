# Preregistration — Study 022: a gateway receipt bound into an in-toto attestation — what each verifier sees, and what neither does

**Status: DRAFT, not frozen.** Pre-freeze cross-vendor review rounds are recorded in
`PREREG-REVIEW.md`; the freeze is the squash-merge of the pull request that record names, and
after it this file is never edited — corrections go to `DEVIATIONS.md`.

**Nothing has run under a freeze.** Everything executed during harness development lands under
`pilots/`, is labeled harness validation, and supports no claim. The apparatus is deterministic
end to end — a committed baseline, nineteen registered constructions, three verifiers — so the
pilots necessarily produced the same observations the registered attempt will; what the
registration adds is the expectation per cell **derived from the three specifications before
the attempt**, with the pilots as the check that the derivation read them right, and the
registered attempt as the check that the pinned artifacts behave as the development ones did.
Every cell's reason says which clause of which specification it follows from.

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (the binding, the three layers, the in-toto ceremony, the
reduced form, the ownership map), `harness/MATRIX.json` (the registered cells) and
`harness/MATRIX-HOLDOUT.json` (the reviewer's holdout cells, authored during review and kept
byte-for-byte). Where prose here and those artifacts could diverge, the artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of the pull request named in `PREREG-REVIEW.md`.
- **Gateway verifier**: the judgment-pack gateway at commit `03582d9` (the executor merge),
  built reproducibly (`cd go && CGO_ENABLED=0 go build -trimpath -buildvcs=false`, Go 1.26.5,
  linux/amd64) and pinned by the binary's SHA-256 in `harness/PINS.json`; the runner and the
  scorer refuse another binary. The gateway has no release channel at the time of writing (its
  tags stop at `v0.2.0`), which is why a commit and a build recipe are pinned rather than an
  asset.
- **The external component**: the in-toto reference implementation — `securesystemslib` 1.3.1
  (DSSE) and `in-toto-attestation` 0.9.3 (Statement v1 bindings) — installed with pip into a
  virtual environment and pinned by version and by a digest over each distribution's installed
  files; a patched installation does not pass as the release.
- **Primary attempt root**: `results/primary-attempt-001` — literal, must not exist at the
  freeze; the runner refuses an existing root, and the first invocation of the governing
  command is the primary attempt, crash and all.
- **Governing invocation** (offline; the pinned gateway binary and the virtual environment):

      python harness/run_attempt.py --attempt-root results/primary-attempt-001 --gateway <the pinned binary>

  The runner holds the pins first (every pin non-null and matching), creates the root
  exclusively, writes `ATTEMPT.json` before anything else — an attempt id, the label, the
  gateway's digest, the raw digest of `harness/PINS.json`, the adapter key id, the cell set —
  then builds every registered cell from the baseline, runs the three layers over every cell,
  and scores with the holdout. A crash after the marker leaves the marker: the root is spent.

## 1. Question

The gateway's receipts (version 3) name what was read and what was done, and its verifier
resolves them against the store, the seal registry and the decision-record directory. Outside
formats exist for the same purpose — in-toto attestations bind a signed predicate to subjects
named by digest, and a consumer verifies the envelope and re-digests the subjects. The plan asks
whether a receipt can be **bound** to such a format so that a consumer of either reads the
other, and what is lost in the binding. This study binds every receipt of a store into one
in-toto Statement in a DSSE envelope (`adapter/SPEC.md`) and measures, over nineteen
constructions of a tampered store or a tampered attestation, what each of three verifiers sees:
the gateway's own, the in-toto reference implementation's, and the binding's rules.

**R1 (primary, retractable):** for every registered **endpoint** cell in `harness/MATRIX.json`
(and, with `--include-holdout`, the holdout matrix), the observed outcome of every layer, in
the reduced form `adapter/SPEC.md` §6 defines, equals the registered expectation. Divergence in
any cell falsifies R1 — a detection on a layer registered as undetected as much as a miss: an
in-toto layer that saw a seal it has no concept of, or a binding that missed a swapped subject,
would each be a defect in the registration's account of the mechanism.

**R2 (descriptive):** the ownership map — which constructions each layer's own checks see,
which layers are silent on which constructions, and which constructions no layer sees except
by a rule the binding itself adds. R2 restates the matrix by category and decides nothing.

This **is** an interoperability study in the sense of Studies 013–016: the in-toto layer is an
independently developed verifier the study does not modify, consumed at a pinned version. It is
not a study of any real deployment: the store is a corpus vector, the adapter key is minted
here, and nothing was fetched from anywhere.

## 1a. Two strata

The 014/016 remedy, inherited: the locked stratum (`harness/MATRIX.json`, nineteen cells) is a
conformance suite over behaviour the maintainer derived from the three specifications and
checked in pilots; the holdout stratum (`harness/MATRIX-HOLDOUT.json`) is authored by the
reviewer during review — constructions the maintainer implements on request before the freeze,
with the reviewer's own expectations kept byte-for-byte — and reports separately. The locked
stratum decides R1; the holdout stratum's divergences are published as such.

## 2. Apparatus and pins

- **Baseline** (D-1): the gateway corpus vector `v3-action-valid` at the pinned commit — an
  acquisition receipt and an action receipt that cites it and names one line of a `.jsonl`
  decision book, sealed, signed under the corpus test key — materialized as
  `fixtures/baseline/` (store, registry, decision records, authority, the corpus public key) and
  bound by the adapter into `fixtures/baseline/attestations/`. Nothing in it was authored for
  this study.
- **Three verifiers**, none modifying the others (D-2): the pinned gateway binary; the pinned
  reference implementation, driven by `adapter/verify_attestation.py` exactly as `adapter/SPEC.md`
  §5 states; the binding's rules in `adapter/verify_binding.py` (§3).
- **Pins are enforced, not declared**: before a registered attempt starts and before any
  adjudication, `harness/pins.py` compares the gateway binary's digest, the corpus public key's
  digest, each package's version and installed-files digest, the adapter key id, each freeze
  pin and the manifest against the tree and the environment, and refuses on any mismatch; a
  registered adjudication further requires every pin non-null, the holdout included and
  non-empty, and the attempt marker parsed and matched.
- **Determinism**: every construction is a function of the committed baseline; the scorer
  rebuilds every cell from the baseline and compares byte for byte before reading an
  observation, and a harness test builds cells twice and compares.

## 3. Scenario and the threat model

A store with two receipts: an acquisition (`s2/0`) and an action (`s2/1`) that cites it and
names a decision record, sealed at two. One attestation per receipt. A party who can reach the
store, the decision book or the attestations changes one thing (§4). What they hold is the
cell's `attackerCapability`: `none`; `tamper` — bytes changed with no key; `selective-keys` — a
key that is not the adapter's; `full-keys` — the adapter's own key, so an attestation can be
rebuilt validly. No cell holds the gateway's key: the study does not model a compromised
gateway, which is out of its scope as it is out of the gateway's (`SECURITY.md`).

## 4. Cells

Nineteen cells in `harness/MATRIX.json`: a positive control, a negative control (a flipped
signature byte, proving the reference implementation exercises the check), seven constructions
on the store with the attestations untouched (a01–a07), nine on the attestations with the store
untouched (b01–b09), and one store re-minted under another gateway key and bound afresh (c01).
Each registers the exact reduced outcome of all three layers, an `ownership` line, and a reason
naming the clauses it follows from. The structures the reasons rest on:

- **What the gateway's key covers and in-toto's does not** (a05, a06, c01): the seal, the
  chain, the count, and the gateway's own identity. An attestation carries none of these; a
  store re-minted under another gateway key binds and verifies as attestations exactly as the
  genuine one does — the binding carries no gateway-key trust.
- **What re-digest sees** (a01, a03, a04, a02 from the action's side): a subject named by digest
  is checked against the store, so an edited artifact, a removed cited receipt and a rewritten
  record are visible to an in-toto consumer — through the action's attestation, whose subjects
  name the cited receipt's bytes and the record's digest; the acquisition's own attestation
  names only its artifact and is silent about its own receipt's bytes (a02).
- **What only the binding sees** (a07, b03, b08, b09): a self-consistent attestation whose
  predicate is not the store's receipt, whose artifact subject is not the predicate's
  `resultDigest`, or whose subjects do not cover the predicate's citations verifies as an
  attestation; the binding's rules (§3 of the specification) are what make it about its
  receipt. These are the study's registered limits of the outside format alone.
- **What in-toto's own checks see** (neg, b01, b02, b04, b05, b06, b07): the envelope's
  signature and key, the payload type, the statement's type and predicate type as the ceremony
  pins them, the attestation's presence.
- **Where a non-gateway layer sees a store change only by the ceremony's rule** (a06): an
  appended receipt is missed by in-toto and the binding not because they read the seal but
  because the ceremony requires one attestation per stored receipt.

## 5. Endpoints and decision rule

The 014–018 regime, inherited: an ordered exhaustive decision rule (pipeline-invalid — the
pins, the marker, the cells or the observations not as registered — → control-gate failure —
the positive control not passing all three layers, or the negative control not failing exactly
where registered — → zero divergence among endpoint cells, which is `R1 holds` → otherwise
`R1 falsified`). An unobserved registered cell is pipeline-invalid. Every terminal path after
the marker is recorded in `ADJUDICATION.json`, written once.

## 6. Validity, controls, enforcement

`harness/score.py` refuses an existing adjudication, an unpinned or mismatching gateway,
package, key or freeze file, a marker whose label, gateway digest, pins digest, key id or cell
set is not this attempt's, cells that are not the registered constructions byte for byte,
observations not stamped with the attempt and the pinned gateway, observations not covering
exactly the registered cells once each, and any observation that is not a complete record of
all three layers with a combined verdict that follows from them. The negative control holds the
reference implementation to its signature check; the positive control holds all three layers
to the baseline.

## 7. Analytic limitations

One baseline store, from a corpus vector; nineteen constructions the maintainer chose from the
three specifications, plus the reviewer's. The ceremony is one consumer's — it pins the
predicate type and the statement version, and adopts the gateway's candidate rule to place a
decision-record subject; a consumer that did less would see less (b04 says how). DSSE and
Statement v1 are the in-toto family's; OpenLineage, the plan's other example, is not bound
here, and nothing about it follows.

## 8. What this study cannot show

No claim about any deployment, any real store, or any consumer but the one the ceremony
describes. No claim that the binding is the right one — it is one the plan's rules admit (the
signer never holds data credentials; the attestation's key is not the gateway's). No claim
about a compromised gateway. No claim that a passing attestation means the receipt is true:
byte-lineage, not truth, on both sides of the binding.

## 9. Publication commitment

The full matrix — every cell, every layer, every registered silence — is published whichever
way it lands, because a precise map of what an outside format's consumer can and cannot see of
a receipt is the registered input to RFC 0014's Unresolved 3 and to the plan's Phase 5, and the
silences are the useful part.
