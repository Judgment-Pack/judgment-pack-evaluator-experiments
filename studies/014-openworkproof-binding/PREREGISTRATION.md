# Preregistration — Study 014: decision-to-execution binding under an external receipt protocol

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing thereafter.**

**Nothing has run.** At the time of this draft no registered attempt exists; everything
executed during harness development lands under `pilots/`, is labeled harness validation,
and supports no claim. After the freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (the commitment schema, binding points, verification
ceremony, and disposition→action map), [`harness/MATRIX.json`](harness/MATRIX.json) (the
machine-readable locked-replication cell registry the scorer adjudicates against) and
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) (the reviewer-authored holdout
stratum). Where prose here and those artifacts could diverge, the pinned artifacts govern
and the divergence is a deviation.

## 1. Question

**R1 (primary, retractable):** for every adjudicated **endpoint** cell in the registered
locked-replication matrix, the observed per-layer detection outcome (OWP verifier / adapter
binding / JPS replay, plus the derived combined verdict) equals the per-cell registered
expectation in `harness/MATRIX.json`. Control-gate, demonstration and descriptive rows are
published in full and count toward nothing (§5).

**R2 (secondary, descriptive):** the detection-ownership map — which failures belong to
the judgment layer, which to the authorization/receipt layer, which to the adapter's
binding, and which to nothing. R2 is a restatement of the matrix by category, not an
independent endpoint.

The study attempts to falsify the binding, not to demonstrate compatibility. A cell
caught by no layer that was registered as detectable falsifies R1 and is reported with
the same prominence as a pass.

## 1a. Two strata (the postdictivity remedy)

Round 1 established that the registered matrix is **not** a prospective test: the `a04`
expectation was corrected after pilot-01 observed it, and pilot-02 then recorded full
concordance over the same artifacts. A rerun of those rows can only reproduce
already-observed behaviour. The registry is therefore stratified, and both strata are
registered here:

- **Locked replication** (`harness/MATRIX.json`, 39 cells). A conformance suite over
  behaviour the maintainer has already observed. It is what R1 adjudicates, and R1's
  standing is exactly that of a locked replication: it can be falsified by a regression,
  and it cannot be read as a prospective prediction.
- **Reviewer holdout** (`harness/MATRIX-HOLDOUT.json`). Cells authored by the cross-vendor
  reviewer, committed verbatim with attribution, and **never executed before the freeze**.
  `harness/score.py --include-holdout` and `harness/build_fixtures.py --holdout` both
  refuse mechanically while `harness/PINS.json`'s `preregistration.sha256` is null (the
  scorer additionally refuses while `matrixHoldout.sha256` is null, so the stratum it
  adjudicates is the one the freeze pinned), and harness tests assert both refusals.
  **Holdout results are reported separately**, in their own section of `RESULTS.json` and
  `DETECTION-MATRIX.md`, with their own control gates and their own concordance summary:
  no holdout outcome enters a locked-stratum count and none can change the R1 verdict.

The reviewer authored eight cells (`h01`–`h08`) at round 2 and they landed byte-for-byte
with attribution; `h08` is the holdout's own control gate. Builder hooks for all eight
exist in `harness/build_fixtures.py`, unexecuted.

**A holdout construction that upstream refuses to publish is a constructibility finding,
not a silent drop**: the builder reports the refusal as a record rather than crashing, no
fixture is written, and the scorer reports that cell **NOT-ADJUDICATED** on the validity
channel with the constructibility note attached — never a detection, never a miss, and
never quietly absent from the published stratum.

**An empty holdout is not a passing holdout**: a round-2 verdict that adopted the round-1
dispositions without authoring cells there would have left the postdictivity finding open,
and this study says so rather than counting the locked replication as if it were a
prediction.

Builder and verifier still share one commitment/digest implementation
(`adapter/commitment.py`), so the locked stratum also has no independent mutation oracle.
Recorded as a standing limitation, not repaired this round.

## 2. Apparatus and pins

- **OpenWorkProof** at commit `8eeca6fff4a246374f9d64f4dc1af6ace42118d5`, installed as a
  package (hash-checked lockfile; index overridden to python.org PyPI — the upstream
  lockfile pins a mirror), **source unmodified**. The offline verifier used is
  `openworkproof.acceptance.verify_acceptance_bundle`, called as a library function; the
  upstream demo script is not used (it discards several of its own check results — recorded
  in §8).
- **jpack** v0.16.0 release binary, archive `sha256 1a12503c…ed59` (matches the release
  `checksums.txt`), binary `sha256 7c11ebef…9325` — the same pins Study 013 froze,
  including its reproducible-build corroboration. Located via `JPACK_BIN`, digest-checked
  before every use.
- **Baseline pack**: `minimal-expense-approval` — spec conformance fixture, vendored
  byte-for-byte (`sha256 76651c8a…1d60`), id
  `https://example.com/judgment-packs/expense-approval`, version `0.1.0`,
  specVersion `0.2.0-draft`.
- Interpreter, venv, and every other pin: `harness/PINS.json`.
- **Pins are enforced, not declared.** Before any cell is adjudicated the scorer compares
  every non-null pin against the live artefact — preregistration, matrix, holdout-matrix,
  study-manifest and SPEC digests when filled; the `jpack` binary digest always; the
  vendored pack bytes always; `openworkproof.installedPackageDigest`, a SHA-256 over the
  installed package's own files as `importlib` resolves them, always; the interpreter
  version exactly; the installed dependency set through `pip freeze` — and verifies
  `harness/STUDY-MANIFEST.sha256`, an exact-set manifest covering the protocol documents,
  the pin registry, both matrix strata, every adapter and harness source file (including
  `harness/owpflow.py`, where the build-time entropy algorithm lives) and every per-cell
  fixture manifest. It also asserts the frozen cell-id set and the per-cell schema of the
  loaded matrix, so a reduced registry cannot satisfy zero divergence by shrinking the
  denominator. Any mismatch is terminal: the attempt is pipeline-invalid and nothing is
  adjudicated. `studyManifest.sha256` is the anchor **outside** the regenerable set —
  `harness/make_manifest.py` can rewrite the manifest, but after the freeze it cannot
  rewrite the digest this registry pins it at, so editing covered code and regenerating no
  longer satisfies the scorer.

## 3. Baseline scenario (deterministic, no models)

Facts: `{"expense": {"type": "employee-expense", "amount": "250.00", "category":
"travel", "activeInvestigation": false}}`. Evidence availability: `{"receipt": "present",
"cost-center": "present"}`. Supported extensions: none. Pinned evaluation yields
`{"kind": "outcome", "outcomeId": "approve", "reasons": [], "handoff": {"state": "none"}}`.

The adapter builds the judgment commitment (SPEC §1–§2), a deterministic OWP work-order
flow executes the one authorized action, and the run terminates in an accepted OWP evidence
bundle. Retained per cell: the bundle, pack/facts/evidence bytes, the evaluator envelope,
and the commitment document, all manifested by SHA-256.

**The execution goes through OpenWorkProof's own patch executor.** A real source archive
is written with `repo_tools.write_source_archive` (two files: the upstream m2 candidate
`src/wrap.py`, and `decision-actions/.keep`, because `apply_patch_phase_b` refuses to
create a file whose immediate parent directory does not exist), the work order is bound to
that archive's commit and digest, `repo_tools.initialize_candidate_workspace` recreates a
real Git candidate workspace under a private runtime root, and
`repo_tools.apply_patch_in_candidate_workspace` parses the canonical Git-style patch bytes
(SPEC §4), applies them, commits the Git checkpoint and derives the `PatchResultEvidence`.
That executor-produced evidence is what the receipt commits, and the post-patch replay
checkpoint is the executor's own candidate commit and workspace manifest. The fixture
oracle is upstream's, not the harness's. The receipt *envelope* is still assembled by the
harness because upstream ships no `execute_apply_patch` entry point — its own delivery
suite hand-builds the same envelope — and it is published through the unmodified
`evidence.complete_receipt_publication`.

Fixture construction is a one-time act: fixed Ed25519 seeds for the six work-order roles,
fixed injected clocks and nonces (upstream seams), and — the one thing upstream provides
no seam for — `receipt_id` entropy pinned at build time by patching `secrets.token_hex`
with a counter-derived generator **in the build harness only** (recorded in §8; upstream
source untouched; nothing on any verification path involves entropy). The frozen fixture
bytes, not the builder, are what the study scores. The builder is inside
`harness/STUDY-MANIFEST.sha256`, so the entropy implementation is pinned by digest and not
only by prose.

## 4. Cells

39 cells in `harness/MATRIX.json`: 1 positive control, 4 negative controls (signature,
evidence digest, parent reference, action parameter — proving the OWP verifier exercises
the relevant checks), 33 mutation cells across six registered categories
(A judgment-artifact, B facts, C disposition, D action, E replay/drift, F causal-chain),
and 1 demonstration control (M28: commitment carried only in the unsigned bundle
metadata). Six D/A cells run in two variants — *tampered* (bytes changed after signing)
and *resigned* (rebuilt validly with the fixture keys, an insider with all six work-order
keys) — because the resigned variants are the ones only the binding layer can see.

Every cell carries three registered fields beyond its expectation: `role`
(`endpoint` / `control-gate` / `demonstration` / `descriptive`, §5),
`attackerCapability` (`none` / `tamper` / `selective-keys` / `full-keys`, §4b), and
`registeredAbsences` (artifact names whose absence the registry authorizes, §6). Only
`a05` registers an absence, `["pack"]`. `m28`'s fixture lacks nothing — an earlier draft of
this document said `m28` registered an absence and was wrong.

### 4a. Constructions upstream refuses

Four registered constructions proved impossible to produce through OWP's live publication
path; publication itself replays windows and causality and refuses them. Those cells are
built as post-hoc substitutions of validly re-signed records, as their construction strings
describe, and each refusal is recorded as a protocol finding in its own right:

- **out-of-window execution** (`e21`): every delegated grant must expire exactly at the
  work-order deadline and publication requires `occurred_at == clock() <= deadline`.
- **wrong or extra causal parents** (`f23`, `f25`): publication replays causality and
  demands the exact protocol parent set.
- **a second execution on one chain** (`d18`): refused three independent ways — publication
  demands the ledger tip be among the new receipt's parents; causal replay demands the
  apply-patch parent set be exactly {authorizing grant issuance, latest prior repo_read on
  that grant}; and causal replay refuses a second allow/succeeded apply-patch outright
  ("a second active patch is not allowed") absent a full needs_rework → rollback → retry
  episode. OWP's own single-active-patch rule therefore already bounds a work order to one
  execution — which is why the surplus-execution attack has to leave the live path, and why
  `d18` is registered with an OWP-layer refusal rather than an OWP-layer pass. A round-2
  live-path probe settled the deferred retry question: rollback and `start_retry` publish,
  but a second `repo_read` fails tip extension, and a second `apply_patch` that does name
  the retry tip publishes and then fails exact causal replay — the retry route dead-ends
  too (probe retained in `harness/tests/test_upstream_probes.py`; it widens only the
  fixture's developer quota so the answer is the protocol's, not the fixture's).

`e21`, `f23` and `f25` are additionally **relabeled as generic upstream-corruption cells**.
Round 1 established that they do not reach the mechanisms they are named for: `e21` trips
grant identity/digest consistency against the issuance receipt before any window logic, and
`f23`/`f25` trip prefix adjacency (re-signing one receipt leaves downstream
`previous_receipt_digest` links stale) before any exact-parent logic. Their OWP-fail
expectations stand as generic corruption detections. The named mechanisms — grant-window
replay refusal, exact-parent-set refusal against both a wrong parent and a superset, and
out-of-window publication refusal — are exercised directly instead by focused probe tests
that call the pinned package's own functions (`harness/tests/test_upstream_probes.py`).

OWP's bundle verifier reports bundle-level failures as a single composite verdict, so
OWP-layer attribution in the matrix is pass/fail, not per-check.

### 4b. Threat model — what each attacker capability can and cannot reach

The registered `attackerCapability` per cell is the capability the construction actually
requires, and the three levels are not interchangeable:

- **`none` / stale artifacts.** The retained artifact store is edited or an artifact is
  deleted; no signed byte and no key is touched. The A- and B-family artifact cells live
  here. The binding layer's digest commitments are what see them.
- **`tamper` / stale signatures.** Signed bytes are changed without re-signing, so the
  attacker chose not to re-sign or could not. Every negative control and every *tampered*
  variant lives here. OWP's own signature and model-integrity checks are what see them;
  these cells test that the verifier is alive, not that binding is necessary.
- **`selective-keys`.** One key, one record re-signed, the rest of the chain left stale
  (`e21`, `f23`, `f25`, `d18`). These are bounded by what the still-fixed artifacts allow,
  which is exactly why they surface as generic corruption rather than as the specific
  mechanism they are named for.
- **`full-keys` / coherent remint.** An insider holding all six fixture keys rebuilds the
  whole chain — WorkOrder, commitment, receipts, reports and the embedded key bindings —
  consistently. This is the interesting adversary, and the honest statement is that the
  study's two binding points do **not** stop it in general: a fully coherent remint under a
  different but equally valid WorkOrder is accepted (`e22`, registered descriptive), and
  decision currency is not observable at all (§4c). What the binding layer catches at this
  level is *internal inconsistency* — a remint that keeps some artifact, digest or receipt
  from the original decision. Catching a fully coherent remint requires an anchor outside
  the chain (an externally trusted pack allowlist, a transparency timestamp, or a monotonic
  decision high-water mark), which changes the trust model and is out of scope here.

All fixture role keys are deterministically derivable from fixed seeds, and the adapter
takes its public keys from the candidate WorkOrder's own bindings (OWP's TOFU root). Both
facts are properties of the study apparatus, and both are stated rather than presented as
independence.

### 4c. Analytic limitations (not empirical rows)

**Decision currency** — "the pack series has since published a newer version, so this
otherwise-valid decision is stale" — is not chain-internal and, unlike every other boundary
here, admits **no fixture distinct from the baseline**. The earlier `e18-stale-decision-currency`
row was the baseline verbatim with a scenario attached to it: it observed the apparatus, not
the boundary. It is removed from the matrix and recorded here as an analytic limitation.
Detecting currency requires an externally trusted anchor (reviewed-set lock / registry
analogue, transparency timestamp, monotonic high-water mark); a cheap additional field
inside the attacker-controlled commitment would not cure it, because an all-key coherent
remint updates that field too.

**Fully consistent re-decision** — an insider re-runs the entire decision over different
facts and rebuilds coherently — is the same ceiling and is likewise out of scope, confirmed
rather than registered as a green cell.

`e22-workorder-rollback` remains in the matrix as a **descriptive** row relabeled
"alternative valid WorkOrder remint accepted", excluded from R1 credit: OWP has no policy
version ordering, so an alternative WorkOrder is a different, equally valid contract. Its
all-pass outcome is published as a boundary and counted as neither a detection nor a miss.

## 5. Endpoints and decision rule

Per cell, the scorer records three independent layer outcomes and the derived combined
verdict (pass iff all pass), then compares the 4-tuple against the registered expectation.
Adjudication is on the registered **code** alone: each layer returns
`{verdict, code, detail}` and the detail string never enters a comparison. Divergence in
either direction — a registered-detectable cell that passes, a registered-pass layer that
fails, or a different failure code than registered — is a divergence.

Ordered, exhaustive, per registered attempt:

1. Any cell **pipeline-invalid** (§6), or any freeze-integrity mismatch (§2) →
   `R1 inconclusive — pipeline-invalid`; terminal for that attempt; no rerun replaces it.
2. Else, any **control-gate** row diverging → `R1 inconclusive — control gate failed`. The
   five control rows are validity gates on the apparatus, evaluated before any endpoint
   row; a gate failure voids the attempt rather than falsifying R1.
3. Else, zero divergences across the **endpoint** cells → `R1 holds`.
4. Else → `R1 falsified`, with every divergence listed.

`demonstration` (`m28`) and `descriptive` (`e22`) rows are adjudicated and published but
count toward nothing: M28 is a disclosed designed demonstration and cannot be cited as a
detection, and `e22` is a registered boundary.

The scorer (`harness/score.py`) is the only thing that publishes; its argument surface is
the attempt root plus `--include-holdout` and nothing else. Adjudication is deterministic
recomputation from frozen fixture bytes; no output embeds a timestamp or an absolute path,
so running it twice must be byte-identical.

## 6. Validity channel (separate from detection)

**Pipeline-invalid** (excluded from adjudication, counted separately, never a detection):
a cell whose fixture fails its own manifest check; an artifact absent when the cell's
`registeredAbsences` did not authorize it, or present when it did; a layer outcome outside
the registered vocabulary; a crash of the harness itself as opposed to an outcome from a
layer; any freeze-integrity mismatch under §2. A cell in any of these states is
**NOT-ADJUDICATED** — never a true or false detection.

Two properties round 1 required, both mechanical:

- **Validity and detection are independent.** Permitted absences are read from the cell's
  own `registeredAbsences` field and from nothing else. They are never inferred from the
  expected verdict, so one registry entry can never both authorize a missing artifact and
  award its detection.
- **Nothing fails silently.** `ATTEMPT.json` is written before any cell runs, and every
  failure path — including a crash inside a cell and a crash during finalization —
  persists a terminal pipeline-invalid `RESULTS.json`.

The exhaustive verdict-code vocabulary lives in `adapter/SPEC.md` §5. Harness tests diff
the SPEC table against the codes `verify.py` declares and the codes `score.py` classifies,
**and** construct a minimal condition for every registered code, asserting the exact code
and the first-failure ordering — so the vocabulary cannot drift from the counting and no
registered code can be unreachable prose.

## 7. Controls and counting integrity

- Positive control: the untouched baseline must pass all three layers (validity gate).
- Negative controls: the four named controls must fail OWP; they prove the verifier is
  alive on exactly the check families the mutation categories lean on (validity gates).
- M28 is a disclosed designed demonstration, not a discovery: OWP verifies green while the
  judgment reference sits in the unsigned envelope — the reason the signed binding points
  exist. Registered `demonstration`; cannot be cited as a detection.
- One mutation family sits entirely outside the JPS boundary (F, causal-chain: expected
  OWP-only) and one entirely inside the binding boundary (D-resigned: expected
  adapter-only), per the design's layer-attribution requirement.
- No silent exclusions: every registered cell appears in the output with an outcome or
  NOT-ADJUDICATED. The scorer refuses an attempt directory that already exists.

## 8. What is enforced, what is recorded, what is not prevented

Enforced by machinery: fixture manifests; the whole-study exact-set manifest, itself
anchored by `studyManifest.sha256` in the pin registry; every non-null pin
(prereg/matrix/holdout-matrix/study-manifest/SPEC digests, `jpack` binary digest, vendored
pack bytes, installed-`openworkproof` package digest, interpreter version, `pip freeze`
digest); the frozen cell-id set and per-cell schema; the SPEC/code verdict-vocabulary sync,
the registered `{verdict, code}` pair table **and** per-code reachability tests with
competing-defect ordering; the holdout refusals (scorer and builder) before the freeze;
upstream OWP bytes never imported into the repo (package install only); missing
`OWP_SOURCE` or `JPACK_BIN` failing the determinism tests rather than skipping them.

Recorded, not enforced: the build-time `secrets.token_hex` patch (the single deliberate
intervention in upstream behavior, build path only); the OWP license inconsistency
(LICENSE Apache-2.0 vs packaging metadata MIT); the upstream demo verifier discarding
check results (why the library function is called directly); OWP's TOFU key model (the
six work-order keys are study-minted fixture keys — the verifier's independence is from
the executing system, not from the study); that the builder and verifier share one
commitment implementation, so the locked stratum has no independent mutation oracle.

Not prevented: an insider holding all six fixture keys can construct any *resigned*
variant — that is the point of the D/C-resigned cells, not a leak — and, per §4b, can
remint an entire alternative chain that the study's binding points do not distinguish.

## 9. What this study cannot show

No policy truth and no fact truth (binding/lineage, not truth — both layers assert
lineage over asserted inputs). No authorization from judgment: an approve disposition is
not an OWP capability grant, and nothing here converts one into the other. No claim that a
receipted execution physically happened — a receipt is an attestation by the signing
system, and the study's claim is about receipted lineage. No JPS conformance (§3.4
machinery not engaged). No security audit of OpenWorkProof and no endorsement — the
registered soft spots are load-bearing context, not findings. No demonstration that the
execution-time binding point is *necessary*: it is registered as defense in depth, no
ablation arm establishes a differential over OWP's own receipt-to-WorkOrder association,
and the differential claim is withdrawn. No coverage claim beyond the 39 registered cells;
no general interoperability claim beyond: this protocol at this commit, this pack, this
action encoding, this machine, one adapter written by the JPS side. No "zero trust": the
verifier trusts the work order's pinned keys, the pinned jpack binary digest, the adapter
code, and the retained artifact store — enumerated, finite, and honest. No runtime-behavior
claim (that is Study 013's question); detection here is post-hoc provability from retained
artifacts. And, per §1a, no prospective-prediction claim for the locked stratum.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence,
every registered-boundary confirmation, and any cell caught by neither system —
the last with the same prominence as a pass, because a precise map of what the
composition cannot bind is the study's most useful possible output.

## Decision register (answered at round 1; see `PREREG-REVIEW.md`)

- [D-1] Two-point binding — **answered:** kept as defense in depth, differential-necessity
  claim withdrawn; `e20` reworked to exercise the execution-side check. Full ablation arms
  declined this round and recorded as an open limitation.
- [D-2] The map executes only `approve`; `manual-review` is registered non-executable —
  **answered:** map kept, totality re-implemented as structural discovery plus exact-set
  equality over the action class, and `c15` added (manual-review with an unbound execution).
- [D-3] Fully consistent re-decision — **answered:** confirmed as an analytic out-of-scope
  ceiling (§4c), not a green cell.
- [D-4] The four negative controls — **answered:** kept, as validity gates outside R1 (§5).
