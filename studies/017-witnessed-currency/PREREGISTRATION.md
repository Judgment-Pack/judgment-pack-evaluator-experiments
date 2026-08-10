# Preregistration — Study 017: the witness contract, measured over Study 016's registry

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing
thereafter.**

**Nothing has run.** No registered attempt exists; everything executed during harness
development lands under `pilots/`, is labeled harness validation, and supports no claim.
After the freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`witness/SPEC.md`](witness/SPEC.md) (the sighting schema, the witness configuration, the
Layer WITNESS ceremony, and the exhaustive verdict vocabulary),
[`harness/MATRIX.json`](harness/MATRIX.json) and
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json). Where prose here and those
artifacts could diverge, the pinned artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of this study's freeze pull request on `main`.
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

**R2 (secondary, descriptive):** the witness-contract map — which registered
non-detection isolates which contract clause: `wit-collusion-*` → independence;
`wit-partition-vacuous` (against its `-enforced` arm) → comparison and enforcement;
`wit-retention-horizon` → coverage/retention. The registered-undetected cells confirmed
undetected are boundary results with a detection's standing.

This is **not an interoperability study**: no external component exists anywhere in the
apparatus, and the README says so. It measures a governance mechanism's floor,
study-internal end to end; its claims are correspondingly narrow (§9).

## 1a. Two strata

The 014/016 remedy, inherited: the locked-replication stratum
(`harness/MATRIX.json`, 14 cells) is a conformance suite over behaviour the maintainer
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

- **Study 016's frozen registry modules, consumed as a pinned unmodified upstream**
  (decision D-2 — the 016→014 posture applied to 016 itself): `registry/verify_currency.py`
  IS Layer CURRENCY, unchanged; `registry/checkpoint.py` is build-path only (views and
  trust configurations). `harness/upstream016.py` loads both by authenticated absolute
  path only — no `sys.path` additions, no bare imports, pre-existing `sys.modules`
  entries refused, per-load identity/origin/bytes re-verification — and every digest is
  pinned in `harness/PINS.json` (`study016.files`), with 016's own frozen STUDY-MANIFEST
  pinning the same bytes from the other side.
- **No evaluator binary, no external clone, no chains** (decision D-1): a cell is
  `(commitment tuple, snapshot, trust configuration, witness configuration, sightings)`
  with synthetic commitment tuples — exactly the surface 016's own unit suite pinned.
  The apparatus is fully deterministic and offline; the only third-party dependencies
  are `cryptography` and `rfc8785`.
- **Witness authority**: study-minted fixed-seed Ed25519 keys (`witnessAuthority` in
  `PINS.json`, seeds recorded, every member mechanically recomputed before adjudication).
  witness-1 is the **colluding role**, witness-2 the honest role, witness-3 is never
  pinned by any cell. **Nothing here claims witness independence** — the collusion pair
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

14 cells in `harness/MATRIX.json`: 2 positive controls, 3 negative controls
(`neg-sighting-forged` — fail-closed on tampered pinned evidence;
`neg-unpinned-conflict` — the ignore rule's cost made visible, a registered PASS that is
never a detection; `neg-limits`), 9 endpoints. Registered structures:

- **The collusion pair** (`pairs.collusion`): the same pinned witness key attests
  contradictory heads at the same position across the two cells, each run internally
  valid and satisfying its enforcement clause. The scorer validates the equivocation
  **structurally from retained bytes** (both sightings verified under the pinned
  colluding key, same position, different heads) — derived, never asserted. This is the
  study's most important artifact: the empirical case for witness **independence**, the
  contract clause nothing in the mechanism enforces. Preserved as a finding, never fixed.
- **Registered-undetected endpoints** (D-5): `wit-collusion-a`, `wit-collusion-b`,
  `wit-partition-vacuous`, `wit-retention-horizon` — all-pass expectations whose
  confirmation is the registered finding, and whose false detection falsifies R1.
- **Arms that decide design points**: `wit-partition-vacuous` vs `wit-partition-enforced`
  (`minimumSightings` 0 vs 1 — the enforcement clause); `wit-split-view-caught` vs 016's
  registered silence (one honest sighting is the whole difference);
  `wit-one-honest` vs `wit-collusion-b` (one honest, comparing witness is the whole
  difference — independence measured as a diff).

### 4b. Threat model

- **`none`**: registry state, pins, and sightings vary; no key misused.
- **`tamper`**: signed bytes changed without re-signing (`neg-sighting-forged`).
- **`authority-key`**: the registry authority's key signs the fork
  (`wit-split-view-caught`, `wit-retention-horizon` — 016's single-operator adversary).
- **`witness-key`**: a pinned witness key's own signing *behavior* is the construction —
  the collusion threat (`wit-collusion-*`, `wit-one-honest`). This is the study's
  registered adversary: what the sighting mechanism still cannot refuse when the witness
  itself equivocates.

### 4c. Analytic limitations (not empirical rows)

Transport, discovery, and retention *policies* are out of reach by design: sightings are
retained bytes, and how they travel, how a verifier finds witnesses, and how long
witnesses keep history are contract clauses this study names but cannot measure (no
protocol exists). Witness *incentives* and real-world independence are likewise
unmeasurable here — all keys are study-minted, and the collusion pair demonstrates the
consequence of dependence, not its probability. Prevention is out of scope everywhere:
witnessing makes equivocation observable at best, and nothing here stops a split view
from being served.

## 5. Endpoints and decision rule

Per cell the scorer records two independent layer outcomes (`{verdict, code, detail}`,
adjudication on registered outcome strings alone) and the derived combined verdict.
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

`pos-consistent`/`unchanged` gate the positive composition; `neg-sighting-forged` proves
fail-closed on tampered pinned evidence; `neg-unpinned-conflict` proves the D-3 ignore
rule is measured rather than assumed (its registered PASS may never be cited as anything
but the rule's cost); `neg-limits` proves the resource cap. No silent exclusions; the
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
