# Preregistration — Study 022: a gateway receipt bound into an in-toto attestation — what each verifier sees, and what neither does

**Status: DRAFT, not frozen.** Pre-freeze cross-vendor review rounds are recorded in
`PREREG-REVIEW.md`; the freeze is the squash-merge of the pull request that record names, and
after it this file is never edited — corrections go to `DEVIATIONS.md`.

**Nothing has run under a freeze.** Everything executed during harness development lands under
`pilots/`, is labeled harness validation, and supports no claim. The apparatus is deterministic
end to end — a committed baseline, nineteen locked constructions, three verifiers — so under
unchanged implementations the registered attempt is expected to reproduce the pilots'
observations of the locked stratum; what the registration adds is the expectation per cell
**derived from the three specifications before the attempt**, with the pilots as the check that
the derivation read them right, and the registered attempt as the check that the pinned
artifacts behave as the development ones did. The holdout stratum (§1a) has no pilot. Every
cell's reason says which clause of which specification it follows from.

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (the binding, the three layers, the in-toto ceremony, the
reduced form, the ownership map), `harness/MATRIX.json` (the registered cells) and
`harness/MATRIX-HOLDOUT.json` (the reviewer's holdout cells: the reviewer's expectations and
construction strings, kept byte-for-byte). Where prose here and those artifacts could diverge,
the artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of the pull request named in `PREREG-REVIEW.md`.
- **Gateway verifier**: the judgment-pack gateway at commit `03582d9` (the executor merge),
  built reproducibly (`cd go && CGO_ENABLED=0 go build -trimpath -buildvcs=false`, Go 1.26.5,
  linux/amd64) and pinned by the binary's SHA-256 in `harness/PINS.json`; the runner and the
  scorer refuse another binary. The gateway has no release channel at the time of writing (its
  tags stop at `v0.2.0`), which is why a commit and a build recipe are pinned rather than an
  asset.
- **The external component**: the in-toto reference implementation — `securesystemslib` 1.3.1
  (DSSE) and `in-toto-attestation` 0.9.3 (Statement v1 bindings) — with the libraries their
  checks run on, `cryptography` 47.0.0 (the Ed25519 primitive) and `protobuf` 5.29.6 (the
  message runtime the bindings validate with), and cryptography's declared dependencies `cffi`
  1.17.1, `pycparser` 2.23 and `typing_extensions` 4.13.2 — installed with pip into a virtual
  environment under CPython 3.8.20 that then holds **exactly those seven distributions and no
  path hook** (`pip` and `setuptools` removed after installation), each pinned by version and by
  a digest over its installed files; a patched installation does not pass as the release, and a
  distribution in the environment that is not pinned is refused. **The executing code is held
  to the pinned code, not only the installed files.** Every harness process, with `os` and
  `sys` alone and before any other import, disables bytecode writing and sets an empty
  bytecode-cache prefix of its own (the runner passes both to its children and strips
  `PYTHONPATH`), then `harness/guard.py` establishes trusted import resolution before anything
  else is imported: the import path holds only the study roots, the interpreter's library and
  the virtual environment; the study roots hold no importable file that is not a `.py` module,
  no directory an import could resolve to, no symbolic link, and no `.py` named like a module
  of the interpreter's library or a pinned package; the virtual environment's import roots hold
  nothing an installed distribution does not record in its `RECORD` — no unrecorded module, no
  unrecorded package directory (which the import system would prefer to a same-named module),
  no path hook, no symbolic link — and no two metadata directories claim one distribution name
  (PEP 503-normalized; an absent or empty name grants nothing); no site customization module
  was imported at start-up; and — **before any pinned distribution or any other study module is
  imported** — every distribution the environment holds is pinned and its recorded files hash
  to the pinned digest (the guard computes the digest `harness/pins.py` computes, independently,
  from the RECORD and the bytes), every file the manifest lists hashes to its listed digest,
  every `.py` under the study roots is listed, and, once the freeze pin is set, the manifest
  itself hashes to the pin. At check time `harness/pins.py` repeats all of that, takes one
  inventory of the environment's distributions (one per normalized name, a duplicated name
  refused and used for nothing) that both the hashing and the ownership of files consume, and
  classifies
  every module in `sys.modules` by the file it was loaded from — built-in or frozen; the
  interpreter's own library; a file of a pinned distribution, under the source or extension
  loader by class identity with its cache path under the empty prefix (a namespace package only
  inside the environment; cryptography's own deprecation proxy, and no other stand-in, unwrapped
  to the module it holds); a registered study module from its `.py`; or one of two modules
  cryptography's pinned extension creates in memory with no file of their own (`_openssl`,
  `_openssl.lib`), pinned by name in `harness/PINS.json` — and refuses anything else, whatever
  its name. The object's real type (`type()`, never `isinstance()`, which a spoofed `__class__`
  satisfies) is read before any acceptance by namespace, origin or name; an object that is not
  a module is refused unless it is one of the two objects the library's `typing` registers or
  the OpenSSL binding table cryptography's verified extension exposes, each admitted by
  identity to what its verified owner holds. The check runs before the marker and
  **again after the layers have run** — in the layer runner before the observations are
  written, in the scorer after the recomputation and before adjudication, in the runner after
  the cells are built — so a module imported late is classified too. The manifest covers every
  file under `adapter/` and `harness/` recursively and refuses an unexpected directory, a
  symbolic link or an importable non-`.py` file there. What this does not establish is a stated
  limit (§7).
- **Primary attempt root**: `results/primary-attempt-001` — literal, must not exist at the
  freeze; the runner and the scorer refuse any other root for a registered attempt (the scorer
  refuses to read registered evidence from any other directory, and refuses a marker whose
  recorded root is not the directory being scored), the runner refuses an existing root, and
  the first invocation of the governing command is the primary attempt, crash and all.
- **Governing invocation** (offline; the pinned gateway binary and the virtual environment):

      python harness/run_attempt.py --attempt-root results/primary-attempt-001 --gateway <the pinned binary>

  (the harness tests, which are not part of the attempt, run as
  `PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=<the pinned binary>
  python -m unittest discover -s harness/tests` from the study root, so that the test module
  itself is compiled from its source; the gateway path is resolved to one absolute file before
  it is hashed or launched, in the runner, in each child and in the scorer's recomputation)

  The runner holds the pins first (every pin non-null and matching), creates the root
  exclusively, writes `ATTEMPT.json` before anything else — an attempt id, the root, the label,
  the gateway's digest, the raw digest of `harness/PINS.json`, the adapter key id, the
  interpreter version, the cell set (locked and holdout) — then builds every locked cell from
  the baseline, then each holdout cell (their first construction through the guarded holdout
  builder — pretesting is disclosed in §1a; a holdout construction that raises is recorded in
  `HOLDOUT-CONSTRUCTION.json`, its partial tree removed, and the locked stratum is unaffected), runs the three layers over every cell, scores
  the locked stratum and reports the holdout beside it. A crash after the marker leaves the
  marker: the root is spent, and the runner's terminal handler records `pipeline-invalid` in
  `ADJUDICATION.json` when the scorer wrote nothing (a failure to write even that is printed).

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

**R1 (primary, retractable):** for every **endpoint** cell of the locked stratum
(`harness/MATRIX.json`), the observed outcome of every layer, in the reduced form
`adapter/SPEC.md` §6 defines, equals the registered expectation. Divergence in any locked
endpoint cell falsifies R1 — a detection on a layer registered as undetected as much as a
miss: an in-toto layer that saw a seal it has no concept of, or a binding that missed a swapped
subject, would each be a defect in the registration's account of the mechanism. The holdout
stratum (§1a) is adjudicated by the same comparison and reported in its own section of
`ADJUDICATION.json`; it decides nothing.

**R2 (descriptive):** the ownership map — which constructions each layer's own checks see,
which layers are silent on which constructions, and which constructions no layer sees except
by a rule the binding itself adds. R2 restates the matrix by category and decides nothing.

This **is** an interoperability study in the sense of Studies 013–016, with one precision: the
in-toto layer is a **study-written consumer ceremony using unmodified DSSE verification and
Statement validation** — the signature check and the Statement's structural validation are an
independently developed implementation the study does not modify, consumed at a pinned
version; the enumeration of receipts, the presence rule, the type pins, the subject resolution
and the re-digests are this study's consumer policy (`adapter/SPEC.md` §4–§5 mark which step is
whose, and §4 below says which cells exercise which). It is not a study of any real deployment:
the store is a corpus vector, the adapter key is minted here, and nothing was fetched from
anywhere.

## 1a. Two strata

The 014/016 remedy, inherited: the locked stratum (`harness/MATRIX.json`, nineteen cells) is a
conformance suite over behaviour the maintainer derived from the three specifications and
checked in pilots; the holdout stratum (`harness/MATRIX-HOLDOUT.json`, six cells) is authored
by the reviewer during review — the reviewer's expectations and construction strings kept
byte-for-byte, the constructions implemented by the maintainer from those strings in
`harness/cells.py` (`HOLDOUT_CELLS`) — and reports separately. The locked stratum decides R1;
the holdout stratum is adjudicated by the same comparison in its own section, deciding nothing.

The holdout's construction is guarded, and its provenance is split and disclosed:

- **Construction.** `harness/cells.py` builds a holdout cell only under a validated
  registered-attempt context (`RegisteredContext`): the builder accepts that exact type only
  and, trusting nothing the object holds, re-runs the whole validation from disk on the
  context's root and gateway — every pin non-null and matching, the executing code included,
  and the marker of a `REGISTERED` attempt at the literal primary root, complete and matched —
  before copying anything; the pilot runner, the tests and the command-line route never
  establish one, and the command-line route refuses a holdout id.
  Through `harness/cells.py` no holdout cell was built before the freeze, and the registered
  attempt is their first construction through the harness.
- **Provenance.** Three holdout cells are **pretested reviewer challenge cells at the
  adapter-layer level**, and no claim of prospectivity is made for them: the function-level
  tests of the round-1 verifier fixes (`harness/tests/test_study.py`, class `Verifiers`)
  perform, on a copy of the baseline, the same edit `h01` (a foreign-key rebinding of the key
  file and both envelopes), `h02` (a duplicated citation subject with the bad digest first) and
  `h06` (an emptied subject list, re-signed) specify, and assert the two adapter layers'
  outcomes on it. Their gateway outcomes and their observation through the runner and the
  scorer were not exercised. The other three — `h03`, `h04`, `h05` — are prospective: no
  construction of theirs, under any name, was executed before the freeze.
- **Containment.** A holdout construction that raises inside the registered attempt is recorded
  as `unconstructed` in the holdout section, and neither invalidates the pipeline nor touches
  R1. The two matrices are disjoint and together are exactly the constructions the harness
  registers; the scorer refuses otherwise.

## 2. Apparatus and pins

- **Baseline** (D-1): the gateway corpus vector `v3-action-valid` at the pinned commit — an
  acquisition receipt and an action receipt that cites it and names one line of a `.jsonl`
  decision book, sealed, signed under the corpus test key — materialized as
  `fixtures/baseline/` (store, registry, decision records, authority, the corpus public key) and
  bound by the adapter into `fixtures/baseline/attestations/`. The corpus inputs were not
  authored for this study; the attestations and the adapter's key were, by the adapter.
- **Three verifiers**, none modifying the others (D-2): the pinned gateway binary; the pinned
  reference implementation, driven by `adapter/verify_attestation.py` exactly as `adapter/SPEC.md`
  §5 states; the binding's rules in `adapter/verify_binding.py` (§3).
- **Pins are enforced, not declared**: before a registered attempt starts and before any
  adjudication, `harness/pins.py` compares the gateway binary's digest, the corpus public key's
  digest, each package's version, installed-files digest and import origin, the interpreter
  version, the adapter key id and the fixture's trusted-key file (key id and key material),
  each freeze pin and the manifest against the tree and the environment, and refuses on any
  mismatch; a registered adjudication further requires every pin non-null, the holdout
  included and non-empty, and the attempt marker parsed and matched.
- **Determinism**: every construction is a function of the committed baseline; the scorer
  rebuilds every cell from the baseline and compares byte for byte — one typed tree for
  comparison and for observation digests alike: every directory and every plain file by
  relative path, files by SHA-256; a symbolic link (the root included), a device or a pipe
  refused before any byte is read — before reading an observation, and a harness test builds
  the locked cells twice and compares the same way.
- **Observations are bound to what was observed**: each cell's observation carries a digest of
  the cell tree taken before the layers ran and checked again after, and the scorer compares it
  with the digest of the cell it rebuilt; the observations file carries the attempt id, the
  gateway's digest, the interpreter version and the trusted-key file's digest, each checked.

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
  chain, the count, and the gateway's own identity. The attestation's predicate carries the
  gateway's identity, session and chain members (`keyId`, `sessionId`, `prevSignature`, the
  signatures) as copied bytes, and the ceremony interprets none of them — it never consults the
  registry, so it cannot tell a registered session from an unregistered one (a05); the seal
  and the count it does not carry at all. A store re-minted under another gateway key binds and verifies as attestations exactly
  as the genuine one does — the binding carries no gateway-key trust.
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
- **What the in-toto layer sees** (neg, b01, b02, b04, b05, b06, b07), split by whose check it
  is: the envelope's signature is the upstream DSSE verification (neg, b01); a signature under
  a key id that is not the pinned one is refused by the ceremony's own key-selection rule
  before upstream verification runs (b02 — consumer policy, §5 step 3); the attestation's
  presence (b06), the payload type (b07), the statement type (b05) and the predicate type
  (b04) are the ceremony's own pins — consumer policy, which a consumer that pinned less would
  not see.
- **Where a non-gateway layer sees a store change only by the ceremony's rule** (a06): an
  appended receipt is seen by in-toto and the binding not because they read the seal but
  because the ceremony requires one attestation per stored receipt (`fail:missing-attestation`).

## 5. Endpoints and decision rule

The 014–018 regime, inherited: an ordered exhaustive decision rule (pipeline-invalid — the
pins, the marker, the cells or the observations not as registered — → control-gate failure —
the positive control not passing all three layers, or the negative control not failing exactly
where registered — → zero divergence among endpoint cells, which is `R1 holds` → otherwise
`R1 falsified`). An unobserved registered cell is pipeline-invalid; a holdout cell whose
construction raised is `unconstructed` in the holdout section and is not (§1a). Every terminal
path after the marker is recorded in `ADJUDICATION.json`, written once: the scorer's record, or
the runner's terminal record of `pipeline-invalid` when the scorer wrote none.

## 6. Validity, controls, enforcement

`harness/score.py` refuses an existing adjudication, an unpinned or mismatching gateway,
package, import origin, interpreter, key or freeze file, a registered root other than the
literal one, a marker whose root, label, gateway digest, pins digest, key id, interpreter or
cell set is not this attempt's, cells that are not the registered constructions byte for byte,
observations not stamped with the attempt, the pinned gateway, the interpreter and the
trusted-key file, observations not covering exactly the registered cells once each, and any
observation that is not a complete record of all three layers: the gateway's `ok` and statuses
recomputed from its findings (the gateway's rule) with a finding per stored receipt, one
in-toto record and one binding record per stored receipt in order with codes from the
vocabulary and phase-dependent members, each layer's `pass` recomputed from its records, the
combined verdict recomputed from the layers, the cell's snapshot digest equal to the rebuilt
cell's — and, beyond the record's own coherence, **equal to what the pinned apparatus produces
when the scorer runs the three layers again over the rebuilt cell**, so a record that is
well-formed but not the apparatus's is refused. A shortfall is a validity failure before any
reduction. The negative control
holds the reference implementation to its signature check; the positive control holds all
three layers to the baseline.

## 7. Analytic limitations

One baseline store, from a corpus vector; nineteen constructions the maintainer chose from the
three specifications, plus the reviewer's. The ceremony is one consumer's — it pins the
predicate type and the statement version, and adopts the gateway's candidate rule to place a
decision-record subject; a consumer that did less would see less (b04 says how). DSSE and
Statement v1 are the in-toto family's; OpenLineage, the plan's other example, is not bound
here, and nothing about it follows.

**The trusted computing base, stated.** The pins and the execution-identity checks (§2) hold
the pinned distributions and the study's own code to their pinned files. They do not establish
the identity of the interpreter's executable build (only its implementation and version), of
its standard library and import machinery, of the native libraries it and the pinned
extensions link, of the gateway binary's own dependencies beyond its digest, or of the
operating system and file system; all of these are trusted, and the checks assume that files
and the import machinery are not replaced concurrently with their being checked (no check here
is an atomic snapshot). Site initialization runs before any check can: a customization module
(`sitecustomize`, `usercustomize`), if one were present, would have run by the time the guard
looks; the guard refuses a run in which one was imported, but cannot undo its having run.
These assumptions are the environment's; they excuse no unchecked replacement under a path
the study or the environment controls, which is why every module the interpreter loaded is
classified, every entry under the environment's import roots is held to a distribution's
record, and anything outside the trusted places is refused — within this base, and not
beyond it.

**What the execution checks establish, and what they cannot.** They establish what code runs
in a process the harness starts: a fresh interpreter over the environment's import roots as
they are on disk, with no code of anyone else's running in it before the harness begins
(site initialization excepted, as above). **The trust anchor** of that claim is the entry
script, `harness/guard.py` and the four library modules the guard uses (`os`, `sys`, `json`,
`hashlib`), each compiled from its file as it is on disk — the manifest lists the script and
the guard, and the freeze commit pins the manifest through `harness/PINS.json` — together with
`harness/PINS.json` itself, which the freeze commit anchors and no check can verify from
inside. Everything imported after the guard runs is hashed by the guard before it is imported. They are not authentication against code that
already runs inside the process before the harness starts: such code can replace, wrap or
spoof any object and any attribute the checks read — the module table, a module's origin,
its loader, its type's name — and it is inside the trusted base by definition. The regression
tests that install in-process stand-ins exercise the classification's refusals of the routes a
reviewer demonstrated; they do not, and cannot, show that every in-process stand-in is
refused, and the registration claims no such thing.

## 8. What this study cannot show

No claim about any deployment, any real store, or any consumer but the one the ceremony
describes. No claim that the binding is the right one — it is one the plan's rules admit (the
signer never holds data credentials; the attestation's key is not the gateway's). No claim
about a compromised gateway. No claim that a passing attestation means the receipt is true:
byte-lineage, not truth, on both sides of the binding. No claim about the trusted computing base
§7 names: the interpreter build, its library, the native libraries, the operating system.

## 9. Publication commitment

The full matrix — every cell, every layer, every registered silence — is published whichever
way it lands, because a precise map of what an outside format's consumer can and cannot see of
a receipt is the registered input to RFC 0014's Unresolved 3 and to the plan's Phase 5, and the
silences are the useful part.
