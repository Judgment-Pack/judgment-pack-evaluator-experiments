# Preregistration — Study 016: the policy-currency anchor, composed over Study 014's binding ceremony

**Status: FROZEN by the squash-merge of PR #55 to `main`; governing thereafter.** The
merge commit of that pull request is the freeze commit — named by reference because a
squash hash cannot exist before the merge; the repository history renders the reference
unambiguous. Five pre-freeze cross-vendor review rounds concluded with `freezable as
written` (`PREREG-REVIEW.md`).

**Nothing has run.** No registered attempt exists; everything executed during harness
development lands under `pilots/`, is labeled harness validation, and supports no claim.
After the freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`registry/SPEC.md`](registry/SPEC.md) (the checkpoint/snapshot schema, the Layer CURRENCY
ceremony, and the exhaustive verdict vocabulary), [`harness/MATRIX.json`](harness/MATRIX.json)
(the machine-readable locked-replication cell registry, including the registered
byte-identity groups and the split-view pair) and
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) (the reviewer-authored holdout
stratum, authored during the review rounds). Where prose here and those artifacts could
diverge, the pinned artifacts govern and the divergence is a deviation.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of PR #55 on `main`.
- **Primary attempt root**: `results/primary-attempt-001` — literal, and it must not exist at
  the freeze. The scorer refuses an existing root, so the first invocation of the governing
  command below is the primary attempt, and it is primary even if it crashes.
- **Governing invocation**:

      JPACK_BIN=<jpack v0.17.0 binary, sha256 42f35f79…22e9, digest-checked>
      OWP_SOURCE=<clone of OpenWorkProof at 8eeca6f, tracked files clean>
      <CPython 3.12.11, the interpreter PINS.json pins>
        harness/score.py --attempt-root results/primary-attempt-001 --include-holdout

  Results land on a separate pull request; the freeze commit carries no `results/`
  directory and no holdout fixtures.

## 1. Question

Study lineage: 013 asked whether the application that acts on a judgment respects it at
runtime (behavior); 014 asked whether a third party can prove, offline, which judgment an
executed action was taken **in reliance on**, under the study's registered downstream
mapping (provenance/binding — Core §3.5/§6.4: an outcome is a declared result, never
authorization); this study asks whether a third party can detect, offline, that a judgment
was carried under a pack version **not in the series' supported set at a pinned registry
snapshot** — membership at one signed, positioned assertion, never "no longer in force"
in any real-time sense (RFC 0011 R-7) — and, with equal weight, what such an anchor
provably cannot detect.

**R1 (primary, retractable):** for every adjudicated **endpoint** cell in the registered
locked-replication matrix, the observed per-layer outcome 4-tuple (OWP / BINDING / REPLAY /
CURRENCY) equals the per-cell registered expectation in `harness/MATRIX.json`. Divergence in
either direction falsifies — a registered-detectable cell that passes, **and a
registered-undetected cell that any layer claims to catch** (decision D-3, rescoped at
round 1: `cur-split-view-a` is the one registered-undetected **endpoint** — a currency
layer that claimed to detect the fork from one view would be defective and must falsify
R1; `cur-workorder-remint-accepted` is **descriptive**, published and never counted,
exactly 014's e22 precedent, per round-1 finding R1-2).

**R2 (secondary, descriptive):** the extended detection-ownership map — what OWP's unchanged
verifier owns, what 014's binding and replay layers own, what the currency step owns, and
what **nothing** owns. The registered-undetected cells confirmed undetected are boundary
results with the same standing as detections; they are the empirical case for
transparency-log-style governance and are reported as findings, never as failures.

The study tries to break the composition, not to demonstrate it. RFC 0011's cross-vendor
review dispositions (spec repo, `rfcs/reviews/0011-round-1.md`) are the registered ceiling on
what any result here may be read to claim.

## 1a. Two strata

The Study 014 remedy, inherited: the locked-replication stratum (`harness/MATRIX.json`,
22 cells) is a conformance suite over behaviour the maintainer observed during harness
development — R1 has exactly the standing of a locked replication, falsifiable by
regression, never a prospective prediction. The **reviewer holdout** stratum
(`harness/MATRIX-HOLDOUT.json`) is authored by the cross-vendor reviewer during the
pre-freeze rounds, committed verbatim with attribution, and never executed before the
freeze; its construction machinery lands together with its cells, inside the attempt that
adjudicates them (`<attempt>/holdout-fixtures/`), following 014's §1a mechanics. The scorer
refuses `--include-holdout` while the preregistration or holdout freeze pin is null, and a
post-freeze invocation that finds registered holdout cells but no construction machinery is
a recorded terminal refusal, never a silent skip. An empty holdout at the freeze would leave
the postdictivity finding open, and the study would say so.

Post-freeze, `--include-holdout` with an **empty** registered holdout stratum is a
recorded terminal refusal, never a locked-only adjudication — an empty holdout is not a
passing holdout and would leave the postdictivity finding open (round-1 R1-11).

Builder and verifier share one registry implementation lineage (`registry/checkpoint.py`
writes, `registry/verify_currency.py` recomputes everything from bytes but was written by
the same author), so the locked stratum has no independent mutation oracle. Recorded as a
standing limitation, exactly as 014 recorded its shared commitment implementation.

## 2. Apparatus and pins

- **Study 014's frozen sources, consumed as a pinned upstream** (decision D-1 — the OWP
  posture applied to 014 itself): `adapter/verify.py` runs layers OWP/BINDING/REPLAY
  unchanged; `adapter/commitment.py` is the commitment implementation; `harness/owpflow.py`
  and `harness/build_fixtures.py` are build-path only. Every consumed file's digest is
  pinned in `harness/PINS.json` (`study014.files`) and enforced by
  `harness/upstream014.py` before anything is imported; 014's own frozen STUDY-MANIFEST
  pins the same bytes from the other side.
- **OpenWorkProof** at commit `8eeca6f`, installed exactly as in Study 014 (hash-checked
  lockfile, mirror index removed, CPython 3.12.11, source unmodified); the installed-package
  digest pin is **byte-identical to 014's** — the same apparatus, re-verified. The offline
  verifier used is `openworkproof.acceptance.verify_acceptance_bundle`, as a library
  function, unchanged.
- **jpack v0.17.0** release binary (maintainer directive): archive `4046a101…d8dc`
  (matches the release `checksums.txt`), binary `42f35f79…22e9`, **reproduced
  byte-for-byte from the v0.17.0 tag before adoption** (go1.26.5, `-trimpath`, goreleaser
  ldflags, VCS stamping on). Verified before adoption: envelope shape and canonical
  disposition bytes on the baseline scenario equal the 014-era v0.16.0 evaluator's;
  `evaluatorSpecVersion` unchanged at `0.2.0-draft`. Consequence: every chain is built by
  this study — Study 014's frozen chain *bytes* are not reusable, because their signed
  commitments carry the v0.16.0 executable digest and Layer REPLAY would correctly refuse
  them (`replay-executable-mismatch`).
- **Packs**: `minimal-expense-approval` 0.1.0, vendored byte-for-byte from the frozen 014
  fixture (`76651c8a…1d60`); 0.2.0, a deterministic transform of it (version bump +
  approval threshold 5000 → 6000, `fc789612…2c70`) — the successor release of the same
  series id.
- **Registry authority**: study-minted fixed-seed Ed25519 keys (`registryAuthority` in
  `PINS.json`, seeds recorded — public deterministic fixtures; nothing depends on their
  secrecy). The authority is the study; nothing about its independence is claimed (§8,
  threats). **Two trust roots are registered** (round-1 R1-10): the expense-series genesis
  head, shared by every expense-series history in the matrix, and the other-policy log's
  genesis head, pinned by `cur-series-unknown`. Trust configurations are per-series
  (`trustconfig.seriesId`); the draft's one-genesis-serves-the-matrix claim is withdrawn.
- **Pins are enforced, not declared** (014 convention): the scorer compares every non-null
  pin before adjudication — freeze-pin digests when filled, the jpack binary digest always,
  both vendored packs always, every `study014.files` digest always, the installed
  `openworkproof` package digest always, the interpreter version exactly, the locked
  dependency set as installed — and refuses to adjudicate on any mismatch. The linear
  anchor order and the `REGISTERED`-requires-every-freeze-pin rule are 014 round-3's,
  restated in `PINS.json`.

## 3. Baseline scenario (deterministic, no models)

Facts `{"expense": {"type": "employee-expense", "amount": "250.00", "category": "travel",
"activeInvestigation": false}}`; evidence `{"receipt": "present", "cost-center":
"present"}`; no supported extensions. Under either pack version the pinned evaluation
yields the canonical disposition `{"kind": "outcome", "outcomeId": "approve", "reasons":
[], "handoff": {"state": "none"}}`.

Five chains serve the whole matrix, all built through 014's frozen flow machinery
(fixed keys, fixed clocks, deterministic nonces, the build-time `secrets.token_hex`
counter patch — all 014's, pinned by digest):

- **baseline** — the v0.1.0 decision, executed and accepted (014's pos-baseline
  construction under the v0.17.0 tuple);
- **successor** — the same scenario decided under pack v0.2.0;
- **remint** — 014's registered e22 construction: the identical judgment commitment
  re-bound under a different, **equally valid** work order (a remint, not a rollback —
  OWP has no contract ordering, round-1 R1-2);
- **neg-replay** — a validly re-signed chain whose commitment forges the executable
  digest (014's e23 construction; the REPLAY aliveness control, round-1 R1-8);
- **neg-owp** — the baseline bundle with one signature character flipped (derived, not
  flowed); its sibling **neg-binding** is the baseline with retained pack bytes drifted
  (014's a01 construction; the BINDING aliveness control).

A Study 016 **cell** is `(chain, retained artifacts, registry snapshot, trust
configuration)`. Most cells share the baseline chain's bytes unchanged and vary only the
signed registry history and the verifier's pins — the design move this study exists to
make: Study 014 §4c registered currency as unobservable because no fixture distinct from
the baseline exists *within a chain*; here the world-that-moved is itself a retained,
signed, pinned artifact, and the boundary becomes a measurable relation between unchanged
chain bytes and varying registry state. Fixture construction is one-time; running the
builder twice yields byte-identical trees (a harness test asserts it).

## 4. Cells

22 cells in `harness/MATRIX.json` (matrixVersion 2, the round-1 revision): 2 positive
controls (`pos-current`, `unchanged` — the within-run control convention), 6 negative
controls (`neg-owp-alive`, `neg-binding-alive`, `neg-replay-alive`,
`neg-snapshot-signature`, `neg-authority-unpinned`, `neg-chain-break` — one aliveness
gate per verification family, so no layer's expectations are satisfiable by a hardcoded
pass, round-1 R1-8), 11 endpoint cells across four registered categories (R
registry-state, S scope-boundary, V verifier-configuration), 1 descriptive row
(`cur-workorder-remint-accepted`, published and never counted), and 2 demonstrations
(`dem-freshness-*`). Every cell carries `role`, `attackerCapability`
(`none` / `tamper` / `authority-key` / `full-keys` — `authority-key` is the
single-operator threat this study exists to bound), `variant`, and `registeredAbsences`
(empty for every cell in this study).

Three registered structures beyond 014's schema:

- **The identity group** (`identityGroups`): deliberate byte-identity, verified by the
  scorer. `cur-retired-reuse` ≡ `dem-freshness-legit` ≡ `dem-freshness-stale` —
  legitimate-use-audited-late and genuine stale reuse differ only in the registry entry's
  scenario label; the verdict provably cannot carry the distinction (RFC 0011 R-7). A
  group divergence is a validity failure on its cells, never a detection. The draft's
  second identity pair is dissolved per round-1 R1-9: `cur-concurrent-set` is **one**
  adjudicated cell carrying **two registered readings** — concurrent-set membership
  (scored), and the freshness-floor reading (analytic, not separately scored: the bytes
  carry no evidence a newer snapshot exists, which is the registered indistinguishability
  and exactly why 014 removed its e18 row). The endpoint denominator counts it once.
- **The split-view pair** (`pairs.split-view`) and its stateful arm: one authority, one
  pinned genesis, two internally valid contradictory continuations. Each half is
  adjudicated as an ordinary cell; the scorer validates the fork **structurally from the
  two snapshot artifacts** (same genesis record, same authority key id, same attested
  position, different heads) and derives the pair report from adjudicated outcomes —
  nothing is asserted by hand (round-1 R1-4). What the pair registers as impossible is
  detection by a **fresh, stateless, per-series-pinned verifier given exactly one view**;
  `cur-split-view-b-stateful` bounds the finding by showing prior-acceptance state
  (provisioned as `minimumHeadPin`) converting the silence into a refusal. The pair is
  the study's most important artifact — the empirical case for transparency-log /
  witness / cross-signing governance — and is preserved as a finding, never "fixed".
- **Registered-undetected rows** (decision D-3, rescoped at round 1): `cur-split-view-a`
  is the one registered-undetected **endpoint** — its all-pass outcome is the registered
  finding and a detection there falsifies R1. `cur-workorder-remint-accepted` carries the
  same flag as a **descriptive** row (014's e22 precedent, round-1 R1-2): its all-pass
  outcome is published as the registered scope boundary and counts toward nothing.

### 4b. Threat model — what each capability reaches

- **`none`**: stale or replayed *signed* artifacts, retained-artifact edits, and verifier
  misconfiguration — the retired-reuse, older-snapshot, unknown-series, unpinned-genesis,
  and binding-aliveness cells. No key and no signed byte is touched; registry state, pins,
  and retained bytes do all the work.
- **`tamper`**: signed bytes changed without re-signing (`neg-owp-alive`,
  `neg-snapshot-signature`) — aliveness gates, not binding evidence.
- **`authority-key`**: the registry operator's own key signs the construction —
  `neg-chain-break` (valid signatures over broken linkage), `cur-rebind-refused` (a valid
  rebinding refused anyway), and the split-view pair (two valid histories). This is the
  study's registered adversary: what the *format* still refuses under a hostile or
  compromised authority, and what it provably cannot refuse (equivocation).
- **`full-keys`**: 014's coherent-remint insider (`cur-workorder-remint-accepted`,
  `neg-replay-alive`) — the chain-side adversary the currency anchor was never scoped to
  catch.

### 4c. Analytic limitations (not empirical rows)

- **Real-time staleness is out of reach by design**, not merely unmeasured: every verdict
  is membership at a pinned snapshot, and no cell can observe "current right now" because
  the ceremony holds no clock (`effectiveFrom` is carried and never compared, D-5). The
  gap between the pinned snapshot and the world above it is exhibited
  (`cur-concurrent-set`'s registered second reading, the freshness identity group) but
  not — and cannot be — measured as a duration.
- **Detection of equivocation is not measured because it is structurally impossible for
  the registered verifier in its fresh, stateless configuration**: the split-view pair
  demonstrates exactly that narrow impossibility, and the stateful arm shows its boundary
  (round-1 R1-4). No cell claims to quantify how often equivocation would occur or be
  noticed by out-of-band means (gossip, witnesses, cross-verifier comparison), all of
  which are outside the registered trust model.
- **Authorization-contract currency** (014's `e22` class) is confirmed out of scope by a
  descriptive row that must *pass* (a remint, not a rollback — nothing in OWP is ordered); nothing here measures what a work-order-currency anchor would
  catch — RFC 0011 Unresolved #6, deliberately untouched.

## 5. Endpoints and decision rule

Per cell the scorer records four independent layer outcomes (`{verdict, code, detail}`,
adjudication on the registered outcome strings alone — detail never enters a comparison)
and the derived combined verdict. Ordered, exhaustive, per registered attempt:

1. Any cell **pipeline-invalid** (§6), or any pin/schema enforcement failure →
   `R1 inconclusive - pipeline-invalid`; terminal; no rerun replaces it.
2. Else, any **control-gate** row diverging → `R1 inconclusive - control gate failed`.
3. Else, zero divergences across the **endpoint** cells → `R1 holds`.
4. Else → `R1 falsified`, with every divergence listed.

`demonstration` rows are adjudicated and published but count toward nothing. The scorer
(`harness/score.py`) is the only thing that publishes; its argument surface is the attempt
root plus `--include-holdout` and nothing else; no output embeds a timestamp or an
absolute path, and scoring twice is byte-identical up to the attempt root's name.

## 6. Validity channel (separate from detection)

**Pipeline-invalid** (excluded from adjudication, never a detection): a cell whose fixture
fails its own manifest; an artifact absent without registration (no cell in this study
registers an absence); a registered identity group whose members' bytes diverge; any pin or
matrix-schema enforcement failure. Such cells are **NOT-ADJUDICATED**. `ATTEMPT.json` is
written before `harness/PINS.json` is parsed under every flag combination; every later
failure path persists a terminal pipeline-invalid `RESULTS.json` (crashes and interrupts
recorded, then re-raised). Validity and detection are independent: permitted absences read
from `registeredAbsences` alone, and identity-group membership is registered in the matrix,
never inferred from outcomes.

## 7. Controls and counting integrity

- `pos-current` and `unchanged`: the positive composition must verify through all four
  layers, twice, from independent directory copies.
- The six negative controls prove, one per verification family (round-1 R1-8): OWP fires
  while currency records independently (`neg-owp-alive`); BINDING fires under this
  toolchain (`neg-binding-alive`); REPLAY fires under this toolchain (`neg-replay-alive`);
  the attestation signature under the pinned key, and the chain linkage, are each
  load-bearing (`neg-snapshot-signature`, `neg-authority-unpinned` — one shared code,
  honestly: a wrong signer and a corrupted signature are indistinguishable to a
  single-pinned-key verifier, round-1 R1-6 — and `neg-chain-break`). Without these, every
  BINDING and REPLAY expectation in the matrix would be `pass` and a hardcoded layer
  could satisfy it.
- No silent exclusions: every registered cell appears in the output with an outcome or
  NOT-ADJUDICATED; the scorer refuses an existing attempt root; the frozen cell-id set is
  asserted so a reduced registry cannot shrink the denominator.

## 8. What is enforced, what is recorded, what is not prevented

**Enforced by machinery**: per-cell fixture manifests; the whole-study exact-set manifest
anchored by `studyManifest.sha256`; every non-null pin (§2 list); the
`REGISTERED`-requires-every-freeze-pin rule; the `study014.files` digests before any 014
import (both directions: 014's frozen manifest pins the same bytes); 014's own
`OWP_SOURCE` pins on the build path (commit, clean tree, per-helper digests, import-shadow
refusals — all 014's frozen machinery, running unmodified); the frozen cell-id set and
per-cell schema; the SPEC §4 / `verify_currency.CODES` / scorer vocabulary sync with
per-code reachability and first-failure ordering; registered identity groups re-verified at
adjudication; builder determinism (build twice, byte-identical).

**Recorded, not enforced**: the registry authority is the study (fixed-seed keys; the
"independent signature" is independence of *mechanism*, not of party); the OWP license
inconsistency, verbatim from 014; 014's build-time entropy patch (build path only);
the shared registry implementation lineage (§1a); `effectiveFrom` as inert carried data.

**Not prevented**: an attacker holding the authority key can mint any internally valid
history — that is the point of the `authority-key` cells, and the split-view pair
registers precisely what that capability buys undetected. An insider holding every chain
fixture key can remint a coherent alternative chain (`cur-workorder-remint-accepted`), as
in 014.

## 9. What this study cannot show

No policy truth and no fact truth — the registry states which versions an authority
asserts in force, never that a policy or fact is true (binding/lineage ceiling, all four
layers). No real-time staleness: every verdict is membership at a pinned snapshot
(RFC 0011 R-7); "fully offline" and "detects staleness in real time" cannot both hold.
No authorization-contract currency: the `e22`-class work-order remint is registered to pass. No
equivocation resistance: the split-view pair exists to prove its absence. No trust from
nothing: the minimal verifier state is two out-of-band pins, and below the genesis it is
trust-on-first-use. No format proposal and no interoperability claim for the registry: one
study-registered schema, one authority, one series, written and consumed by the same
project — RFC 0011's Implementation section names the stronger evidence (a consumer step
built by the receipt protocol's author) and this study is not it. No claim about OWP
beyond 014's, and **no replication claim for 014's mutation stratum** (round-1 R1-8): the
chain layers demonstrate positive compatibility of the pinned adapter on this study's
five chains under v0.17.0, plus one aliveness control per layer; 014's refusal coverage
is 014's evidence, not this study's. Only the CURRENCY column is new evidence. No JPS conformance; no security audit of any
component; no prospective-prediction claim for the locked stratum (§1a); no
runtime-behavior claim (Study 013's question). Trust roots, enumerated: the work order's
six study-minted chain keys, the pinned jpack executable digest, the frozen 014 sources,
the registry authority key and genesis pin, the adapter and registry code, and the
retained artifact store.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence, every
registered-boundary confirmation, the structurally-validated split-view pair report, and
any cell caught by no layer — the last with the same prominence as a pass, because the
precise map of what the composition cannot see (the work-order remint, equivocation
against a fresh stateless verifier, the world above the pinned snapshot) is the study's
most useful possible output, and is the registered input to the governance question
RFC 0011 leaves open (Unresolved #1).
