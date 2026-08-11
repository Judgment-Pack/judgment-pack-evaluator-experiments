# Preregistration — Study 017: the witness contract, measured over Study 016's registry

**Status: FROZEN by the squash-merge of PR #57 to `main`; governing thereafter.** The
merge commit of that pull request is the freeze commit — named by reference because a
squash hash cannot exist before the merge; the repository history renders the reference
unambiguous. Seven pre-freeze cross-vendor review rounds concluded with `freezable as
written` (`PREREG-REVIEW.md`).

**Nothing has run.** No registered attempt exists; everything executed during harness
development lands under `pilots/`, is labeled harness validation, and supports no claim.
After the freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

Four companion artifacts are registered *with* this document and pinned at the freeze:
[`witness/SPEC.md`](witness/SPEC.md) (the sighting schema, the witness configuration, the
Layer WITNESS ceremony, and the exhaustive verdict vocabulary),
[`harness/MATRIX.json`](harness/MATRIX.json) and
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json), and
[`harness/MATRIX-HOLDOUT-EVIDENCE.json`](harness/MATRIX-HOLDOUT-EVIDENCE.json) (the
structured-evidence expectations for the reviewer's cells, kept separate so their authored
block stays byte-for-byte, and gating execution exactly as the other pins do). Where prose here and those
artifacts could diverge, the pinned artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of PR #57 on `main`.
- **Primary attempt root**: `results/primary-attempt-001` — literal, must not exist at the
  freeze; the scorer refuses an existing root, and the first invocation of the governing
  command is the primary attempt, crash and all.
- **Governing invocation** (fully offline — no evaluator binary, no external clone):

      <CPython 3.12.11, the interpreter PINS.json pins>
        harness/score.py --attempt-root results/primary-attempt-001 --include-holdout

## 1. Question

Study 016 measured that a single-operator signed currency registry is silent to a fresh,
stateless verifier shown one view of a split history, and that the silence is exactly
statelessness. This study measures the *next* mechanism: what does a minimal witness /
cross-view-comparison step — a **sighting**, one witness key's signature over a head it
has observed — actually buy, and which clause of the witness contract named by
RFC 0011 Unresolved #9 (retention, cross-view comparison, verifier enforcement, witness
independence and non-collusion) does each remaining silence isolate?

**R1 (primary, retractable):** for every adjudicated **endpoint** cell in the registered
locked-replication matrix, the observed `{currency, witness}` layer outcomes equal the
per-cell registered expectations. Divergence in either direction falsifies — including a
detection on any `registeredUndetected` row (016's decision D-3, upheld by its review):
a witness layer that claimed to see collusion, a vacuous comparison, or a fork above the
sighted horizon would be defective, and must be able to falsify R1.

**R2 (secondary, descriptive):** the map of what each registered non-detection isolates,
stated as the condition the apparatus actually represents rather than a cause it cannot
observe (round-1 R1-8): `wit-collusion-*` → a witness signing per audience, which no
implemented clause refuses; `wit-suppression-omitted` / `-corrupted` → control over which
records reach the verifier; `wit-zero-sightings-vacuous` (against its `-enforced` arm) →
zero-sighting enforcement; `wit-prefix-coverage` → positional prefix coverage;
`wit-historical-audit` (against `wit-recency-refused`) → the configured recency policy's
cost. No cell attributes an empty or missing record to partition, retention loss,
withholding, or discovery failure: those conditions are indistinguishable here, and the
draft's causal wording is withdrawn.

This is **not an interoperability study**: no external component exists anywhere in the
apparatus, and the README says so. It measures a governance mechanism's floor,
study-internal end to end; its claims are correspondingly narrow (§9).

## 1a. Two strata

The 014/016 remedy, inherited: the locked-replication stratum
(`harness/MATRIX.json`, 18 cells) is a conformance suite over behaviour the maintainer
observed during harness development; R1 has a locked replication's standing, never a
prospective prediction. The **reviewer holdout** stratum is authored by the cross-vendor
reviewer during the pre-freeze rounds, committed verbatim with attribution, never
executed before the freeze; its construction machinery lands together with its cells, and
post-freeze the scorer refuses an empty stratum and refuses registered cells without
machinery — recorded terminal refusals, never silent skips. Builder and verifier share
one sighting implementation lineage (`witness/sighting.py` writes,
`witness/verify_witness.py` recomputes from bytes but was written by the same author) —
the standing no-independent-mutation-oracle limitation, recorded as in 014/016.

## 2. Apparatus and pins

- **Executed bytes, not just source digests** (round-1 R1-1): the pinned upstream is
  compiled from the exact source bytes hashed at load, and a stdlib bootstrap — running before
  any study or third-party import — refuses to adjudicate when the cache a plain import *would*
  accept unmarshals to code differing from `compile()` of its source. An equivalent cache is
  accepted, and mere existence is not the hazard (round-3 R1-1 residual); `__main__` is never
  loaded from a cache, so the entry point is exempt by construction.
- **Registered third-party dependencies** (round-1 R1-2): `cryptography` and `rfc8785` are
  registered by version in `harness/PINS.json` and enforced before adjudication by name,
  version, distribution root outside the studies tree, and the origin of the module
  actually imported (so a shadowing copy cannot satisfy a version check while other code
  runs). Their **contents are not digest-pinned**: same-version modified package bytes
  would pass, and that residue is stated here rather than claimed closed. The draft's claim that they were "transitively pinned by the 016
  apparatus" was false — this study consumes no lockfile of 016's — and is withdrawn.
- **Study 016's frozen registry modules, consumed as a pinned unmodified upstream**
  (decision D-2 — the 016→014 posture applied to 016 itself): `registry/verify_currency.py`
  IS Layer CURRENCY, unchanged; `registry/checkpoint.py` is build-path only (views and
  trust configurations). `harness/upstream016.py` loads both by authenticated absolute
  path only — no `sys.path` additions, no bare imports, pre-existing `sys.modules`
  entries refused **for every reserved name before any module executes**, per-load
  identity/origin/bytes re-verification — and every digest is pinned in `harness/PINS.json`
  (`study016.files`), with 016's own frozen STUDY-MANIFEST pinning the same bytes from the
  other side. The mapping the loader trusts is extracted once from the **stamped** registry
  bytes the attempt records, never re-read (round-1 R1-3), so the trust inputs cannot differ
  from what the attempt commits to.
- **No evaluator binary, no external clone, no chains** (decision D-1): a cell is
  `(commitment tuple, snapshot, trust configuration, witness configuration, sightings)`
  with synthetic commitment tuples — exactly the surface 016's own unit suite pinned.
  The apparatus is fully deterministic and offline; the only third-party dependencies
  are `cryptography` and `rfc8785`.
- **Witness authority**: study-minted fixed-seed Ed25519 keys (`witnessAuthority` in
  `PINS.json`, seeds recorded, every member mechanically recomputed before adjudication).
  witness-1 is the **colluding role**, witness-2 the honest role, and witness-3 is never
  pinned in the **locked-replication** stratum — the reviewer's holdout deliberately leaves it
  unpinned in `h02` and pins it in `h03`/`h04` (round-3 R3-2). **Nothing here claims witness independence** — the collusion pair
  is the argument for independence, not a simulation of it.
- **Pins are enforced, not declared** (014/016 convention): the scorer enforces the
  interpreter version, every `study016.files` digest, every `witnessAuthority` member,
  the witness layer's checkpoint-domain constant against the pinned upstream's, the
  freeze-pin digests when filled, the whole-study manifest when pinned (its freshness is
  a standing suite assertion — 016's round-3 lesson), and the frozen cell-id set and
  per-cell schema. Any mismatch is terminal.

## 3. Baseline scenario (deterministic, no models)

One synthetic series (`…/witnessed-policy`), commitment tuple
`(series, 1.0.0, digest-A)`. The **fork pair** shares its genesis and diverges at
position 2 with *both* branches keeping the committed version current — view A adds
`1.1.0`, view C adds `2.0.0` — so the split-view cells isolate the witness layer: Layer
CURRENCY passes on either branch and only the sighting comparison distinguishes them. A
retiring history exercises the interplay cell. All registry artifacts are built through
the pinned 016 writer; all sightings through `witness/sighting.py`; fixture construction
is one-time and byte-reproducible (a harness test rebuilds and byte-compares).

## 4. Cells

18 cells in `harness/MATRIX.json` (matrixVersion 2, the round-1 revision): 2 positive
controls, 3 negative controls (`neg-relabel-attack` — the reviewer's own falsifying
construction kept as a standing control; `neg-sighting-malformed`; `neg-limits`), and 13
endpoints across what a sighting buys (W), what delivery control still hides (S),
enforcement (E), recency policy (R), and layer composition (X). Registered structures:

- **The collusion pair** (`pairs.collusion`): the same pinned witness key attests
  contradictory heads at the same position across the two cells, each run internally
  valid and satisfying its enforcement clause. The scorer validates the equivocation
  **structurally from retained bytes** (both sightings verified under the pinned
  colluding key, same position, different heads) — derived, never asserted. This is the
  study's most important artifact: the empirical case for witness **independence**, the
  contract clause nothing in the mechanism enforces. Preserved as a finding, never fixed.
- **Registered-undetected endpoints** (D-5): `wit-collusion-a`, `wit-collusion-b`,
  `wit-suppression-omitted`, `wit-suppression-corrupted`, `wit-zero-sightings-vacuous`,
  `wit-prefix-coverage`, `wit-historical-audit` — all-pass expectations whose confirmation
  is the registered finding, and whose false detection falsifies R1.
- **Arms that decide design points**: `wit-zero-sightings-vacuous` vs `-enforced`
  (`minimumSightings` 0 vs 1); `wit-suppression-omitted` vs `wit-required-witness-absent`
  (a count floor vs a named-witness floor over the same bytes); `wit-recency-refused` vs
  `wit-historical-audit` (the same bytes under both recency policies — the policy's cost,
  measured); and `wit-split-view-caught` vs `wit-zero-sightings-vacuous`, whose bytes
  differ only in the sighting set, which is the study's internal "one attributed record is
  the difference" comparison (round-1 R1-5: this study does **not** replay Study 016's
  cells — different series, no receipt layers, both fork branches add rather than retire,
  and no claim of replicating 016's run is made anywhere).
- **Structured witness evidence** (round-1 R1-9): every adjudicated cell publishes
  `comparisonPerformed`, `validSightings` and `unattributedSightings` alongside the
  outcome, in both `RESULTS.json` and the published detection matrix. Cells that turn on
  the distinction additionally **register** `expectedComparisonPerformed`, which the
  scorer adjudicates: a cell whose comparison did not happen as registered diverges on
  `witness:comparisonPerformed`, so the field governs rather than decorates.

### 4b. Threat model

- **`none`**: registry state, pins, and sightings vary; no key misused.
- **`tamper`**: retained bytes changed without re-signing (`neg-sighting-malformed`).
- **`authority-key`**: the registry authority's key signs the fork
  (`wit-split-view-caught`, `wit-prefix-coverage` — 016's single-operator adversary).
- **`witness-key`**: a pinned witness key's own signing *behaviour* is the construction —
  a witness signing per audience (`wit-collusion-*`, `wit-one-honest`).
- **`delivery`**: control over which retained records reach the verifier, touching no key
  the party does not hold — omission, corruption, or relabelling
  (`wit-suppression-*`, `wit-required-witness-absent`, `neg-relabel-attack`). Round 1
  established this as the study's sharpest adversary: the draft's routing let a *label*
  suppress evidence, and closing that channel leaves omission and corruption open by
  construction.

### 4c. Analytic limitations (not empirical rows)

Transport, discovery, and retention *policies* are out of reach by design: sightings are
retained bytes, and how they travel, how a verifier finds witnesses, and how long
witnesses keep history are contract clauses this study names but cannot measure (no
protocol exists). Consequently no result here may be read as measuring partition,
withholding, discovery failure, or retention loss: an absent or unattributable record is
one condition to this verifier, and the cells are named for what they represent
(zero-sighting enforcement, positional prefix coverage, delivery control) rather than for
causes the apparatus cannot distinguish. Witness *incentives* and real-world independence are likewise
unmeasurable here — all keys are study-minted, and the collusion pair demonstrates the
consequence of dependence, not its probability. Prevention is out of scope everywhere:
witnessing makes equivocation observable at best, and nothing here stops a split view
from being served.

## 5. Endpoints and decision rule

Per cell the scorer records two independent layer outcomes (`{verdict, code, detail}`,
adjudication on registered outcome strings, plus the registered structured-evidence
fields where a cell registers them — `expectedComparisonPerformed` in the locked stratum and
`harness/MATRIX-HOLDOUT-EVIDENCE.json` for the reviewer's cells, each adjudicated as its own
`witness:<field>` divergence channel) and the derived combined verdict.
Ordered, exhaustive: (1) any pipeline-invalid cell or pin/schema failure →
`R1 inconclusive - pipeline-invalid`, terminal; (2) any control-gate divergence →
`R1 inconclusive - control gate failed`; (3) zero endpoint divergence → `R1 holds`;
(4) else `R1 falsified`, every divergence listed. The scorer is the only publisher; its
outputs embed no timestamp and no absolute path; scoring twice is byte-identical up to
the attempt root's name.

## 6. Validity channel (separate from detection)

As in 014/016: manifest failures, unregistered absences, and enforcement failures are
NOT-ADJUDICATED, never detections. `ATTEMPT.json` precedes the registry parse and carries
`pinsRawSha256` over the exact bytes then parsed (single read); every terminal record
repeats it; `SystemExit`/`KeyboardInterrupt` are terminal-recorded and re-raised.

## 7. Controls and counting integrity

`pos-consistent`/`unchanged` gate the positive composition; `neg-relabel-attack` keeps the
round-1 falsifying construction as a standing control, so a regression to label-based
association fails a gate rather than a boundary cell; `neg-sighting-malformed` proves the
closed schema is fail-closed before any signature math; `neg-limits` proves the resource
cap. No silent exclusions; the
scorer refuses an existing attempt root; the frozen cell-id set is asserted.

## 8. What is enforced, what is recorded, what is not prevented

**Enforced**: per-cell manifests; the whole-study exact-set manifest and its standing
freshness assertion; every non-null pin (§2 list); the frozen cell-id set and schema;
the SPEC §3 / `verify_witness.CODES` vocabulary sync with per-code reachability and
first-failure ordering; the collusion pair's structural validation; builder determinism.
**Recorded**: the witness keys are the study's (no independence); the shared sighting
implementation lineage; D-3's ignore asymmetry and its measured cost. **Not prevented**:
a pinned witness can equivocate (that is the point of the collusion pair); the registry
authority can fork above any sighted horizon; nothing stops a split view from being
served.

## 9. What this study cannot show

No interoperability of any kind — nothing here is independently developed, and the study
must never be cited as evidence that witnessing "works" between real parties. No witness
independence — the collusion pair is the case *for* requiring it, established by
exhibiting its absence. No prevention: observability at best, under every clause of a
contract this study names and only partially instantiates. No transport, discovery,
retention-policy, or incentive claims (§4c). No real-time anything; no policy or fact
truth; everything Study 016 registered as nothing's remains nothing's. Trust roots,
enumerated: the study-minted authority and witness keys, the pinned 016 modules, this
study's witness code, and the retained artifact store. Binding/lineage, not truth.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence,
every registered-boundary confirmation, the structurally validated collusion exhibit,
and any cell caught by neither layer — with a pass's prominence, because the precise map
of which contract clause each silence isolates is the study's most useful possible
output, and is the registered input to RFC 0011's governance question (Unresolved #1/#9)
and to any future RFC on witnessing.
