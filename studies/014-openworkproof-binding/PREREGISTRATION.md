# Preregistration — Study 014: decision-to-execution binding under an external receipt protocol

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing thereafter.**

**Nothing has run.** At the time of this draft no registered attempt exists; everything
executed during harness development lands under `pilots/`, is labeled harness validation,
and supports no claim. After the freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

Two companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (the commitment schema, binding points, verification
ceremony, and disposition→action map) and [`harness/MATRIX.json`](harness/MATRIX.json)
(the machine-readable cell registry the scorer adjudicates against). Where prose here and
those artifacts could diverge, the pinned artifacts govern and the divergence is a
deviation.

## 1. Question

**R1 (primary, retractable):** for every adjudicated cell in the registered matrix, the
observed per-layer detection outcome (OWP verifier / adapter binding / JPS replay, plus
the derived combined verdict) equals the per-cell registered expectation in
`harness/MATRIX.json` — including the two cells registered as expected-undetected.

**R2 (secondary, descriptive):** the detection-ownership map — which failures belong to
the judgment layer, which to the authorization/receipt layer, which to the adapter's
binding, and which to nothing. R2 is a restatement of the matrix by category, not an
independent endpoint.

The study attempts to falsify the binding, not to demonstrate compatibility. A cell
caught by no layer that was registered as detectable falsifies R1 and is reported with
the same prominence as a pass.

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
- Interpreter, venv, and every other pin: `harness/PINS.json`
  (011 convention; `preregistration.sha256` is null until the freeze and the scorer
  refuses to run while it is null).

## 3. Baseline scenario (deterministic, no models)

Facts: `{"expense": {"type": "employee-expense", "amount": "250.00", "category":
"travel", "activeInvestigation": false}}`. Evidence availability: `{"receipt": "present",
"cost-center": "present"}`. Supported extensions: none. Pinned evaluation yields
`{"kind": "outcome", "outcomeId": "approve", "reasons": [], "handoff": {"state": "none"}}`.

The adapter builds the judgment commitment (SPEC §1–§2), a deterministic OWP work-order
flow executes the one authorized action (`owp.apply_patch`; the patch bytes *are* the
canonical action document, SPEC §4), and the run terminates in an accepted OWP evidence
bundle. Retained per cell: the bundle, pack/facts/evidence bytes, the evaluator envelope,
and the commitment document, all manifested by SHA-256.

Fixture construction is a one-time act: fixed Ed25519 seeds for the six work-order roles,
fixed injected clocks and nonces (upstream seams), and — the one thing upstream provides
no seam for — `receipt_id` entropy pinned at build time by patching `secrets.token_hex`
with a counter-derived generator **in the build harness only** (recorded in §8; upstream
source untouched; nothing on any verification path involves entropy). The frozen fixture
bytes, not the builder, are what the study scores.

## 4. Cells

37 cells in `harness/MATRIX.json`: 1 positive control, 4 negative controls (signature,
evidence digest, parent reference, action parameter — proving the OWP verifier exercises
the relevant checks), 31 mutation cells across six registered categories
(A judgment-artifact, B facts, C disposition, D action, E replay/drift, F causal-chain),
and 1 demonstration control (M28: commitment carried only in the unsigned bundle
metadata). Six D/A cells run in two variants — *tampered* (bytes changed after signing)
and *resigned* (rebuilt validly with the fixture keys, an insider with all six work-order
keys) — because the resigned variants are the ones only the binding layer can see.

Three registered constructions proved impossible to produce through OWP's live
publication path (out-of-window execution; wrong or extra causal parents): publication
itself replays windows and causality and refuses them. Those cells are built as post-hoc
substitutions of validly re-signed records, as their construction strings now describe,
and the constructibility refusal is recorded as a protocol finding in its own right.
OWP's bundle verifier reports bundle-level failures as a single composite verdict, so
OWP-layer attribution in the matrix is pass/fail, not per-check.

Two cells are **registered expected-undetected** (`e18-stale-decision-currency`,
`e22-workorder-rollback`): decision currency and policy rollback are not chain-internal
properties; detecting them requires an anchor outside the chain. Their all-pass outcome
is the registered finding. Patching the harness to catch them would falsify the study's
own boundary claim.

## 5. Endpoints and decision rule

Per cell, the scorer records three independent layer verdicts and the derived combined
verdict (pass iff all pass), then compares the 4-tuple against the registered expectation.
Divergence in either direction — a registered-detectable cell that passes, a
registered-pass layer that fails, or a different failure code than registered — is a
divergence.

Ordered, exhaustive, per registered attempt:

1. Any cell **pipeline-invalid** (§6) → the attempt is
   `R1 inconclusive — pipeline-invalid`; terminal for that attempt; no rerun replaces it.
2. Else, zero divergences across all 33 cells → `R1 holds`.
3. Else → `R1 falsified`, with every divergence listed.

The scorer (`harness/score.py`) is the only thing that publishes; its argument surface is
the pilot/attempt root and nothing else. Adjudication is deterministic recomputation from
frozen fixture bytes; running it twice must be byte-identical.

## 6. Validity channel (separate from detection)

**Pipeline-invalid** (excluded from adjudication, counted separately, never a detection):
a cell whose fixture fails its own manifest check; a missing artifact that the matrix did
not register as missing (`a05` and `m28` register their absences); a crash of the harness
itself as opposed to a verdict from a layer; a `JPACK_BIN` digest mismatch. A cell whose
artifacts are incomplete in an unregistered way is **NOT-ADJUDICATED** — never a true or
false detection. The exhaustive verdict-code vocabulary lives in `adapter/SPEC.md` §5;
a harness test diffs the SPEC table against the codes `verify.py` can actually return and
the codes `score.py` can classify, so the vocabulary cannot drift from the counting.

## 7. Controls and counting integrity

- Positive control: the untouched baseline must pass all three layers; the study is void
  otherwise (this is an apparatus precondition, not an endpoint).
- Negative controls: the four named controls must fail OWP; they prove the verifier is
  alive on exactly the check families the mutation categories lean on.
- M28 is a disclosed designed demonstration, not a discovery: OWP verifies green while the
  judgment reference sits in the unsigned envelope — the reason the signed binding points
  exist. It is registered as such and cannot be cited as a detection.
- One mutation family sits entirely outside the JPS boundary (F, causal-chain: expected
  OWP-only) and one entirely inside the binding boundary (D-resigned: expected
  adapter-only), per the design's layer-attribution requirement.
- No silent exclusions: every registered cell appears in the output with a verdict or
  NOT-ADJUDICATED. The scorer refuses an attempt directory that already contains results.

## 8. What is enforced, what is recorded, what is not prevented

Enforced by machinery: fixture manifests; `JPACK_BIN` digest check; the pinned-registry
stamp (`PINS.json` digest recorded in every attempt); the SPEC/code verdict-vocabulary
sync test; upstream OWP bytes never imported into the repo (package install only).

Recorded, not enforced: the build-time `secrets.token_hex` patch (the single deliberate
intervention in upstream behavior, build path only); the OWP license inconsistency
(LICENSE Apache-2.0 vs packaging metadata MIT); the upstream demo verifier discarding
check results (why the library function is called directly); OWP's TOFU key model (the
six work-order keys are study-minted fixture keys — the verifier's independence is from
the executing system, not from the study).

Not prevented: an insider holding all six fixture keys can construct any *resigned*
variant — that is the point of the D/C-resigned cells, not a leak.

## 9. What this study cannot show

No policy truth and no fact truth (binding/lineage, not truth — both layers assert
lineage over asserted inputs). No authorization from judgment: an approve disposition is
not an OWP capability grant, and nothing here converts one into the other. No JPS
conformance (§3.4 machinery not engaged). No security audit of OpenWorkProof and no
endorsement — the registered soft spots are load-bearing context, not findings. No
coverage claim beyond the 33 registered cells; no general interoperability claim beyond:
this protocol at this commit, this pack, this action encoding, this machine, one adapter
written by the JPS side. No "zero trust": the verifier trusts the work order's pinned
keys, the pinned jpack binary digest, the adapter code, and the retained artifact store —
enumerated, finite, and honest. No runtime-behavior claim (that is Study 013's question);
detection here is post-hoc provability from retained artifacts.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence,
every registered-undetected confirmation, and any cell caught by neither system —
the last with the same prominence as a pass, because a precise map of what the
composition cannot bind is the study's most useful possible output.

## Decision register (open choices for the pre-freeze review)

- [D-1] Two-point binding (WorkOrder.objective + context_source_digest) — is one point
  demonstrably insufficient, or should e20 carry a companion single-point arm?
- [D-2] The disposition→action map executes only `approve`; `manual-review` (an outcome
  with handoff none) is registered non-executable. Reviewer challenge welcome: is the
  map's totality clause the right boundary for C-cell attribution?
- [D-3] b08's fully-consistent re-decision variant (insider re-runs the entire decision
  over different facts) is registered as out of scope (indistinguishable by design, needs
  an external anchor, same family as e18/e22). Confirm or demand a cell.
- [D-4] The four negative controls overlap mechanically with mutation cells; they are
  retained as named controls per the design review. Drop or keep?
