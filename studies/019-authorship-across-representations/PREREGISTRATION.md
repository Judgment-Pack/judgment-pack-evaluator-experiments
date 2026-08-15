# Preregistration — Study 019: authorship across representations

**Status: DRAFT, second major revision (post-design-phase). Not frozen. Nothing citable has
run. No review round has read this draft. Every freeze pin is null; every execution before
the freeze is a PILOT and supports no claim. Items marked `GATE(pre-freeze)` are work that
must land before any review round can return `freezable as written`.**

## Design provenance (disclosed, because it shaped the registered claims)

This draft was preceded by a design phase whose artifacts live under `design/` and whose
non-citable calibration pilot (`design/pilots/2026-08-15-calibration-pilot-01/`) shaped two
registered choices, disclosed here rather than discovered in review:

1. **The primary endpoint pivoted from policy correctness to test-pinning power.** In the
   pilot, every completed authoring run in every arm produced a policy artifact in perfect
   agreement with all 76 gold rows (5/5 per arm): correctness is at ceiling for
   well-specified prose at this scale, in all three representations. The dimension with
   variance is what the run-authored test suites catch: pilot mean paired-mutant kill rates
   of 0.90 (arm A, range 0.84–1.00) vs 0.97–0.98 (arms B/C). R1 is therefore registered
   over E4 (kill rates), with E1 (gold agreement) as a reported control expected at
   ceiling — the ceiling itself being a finding this study commits to publishing.
2. **The high-kill threshold τ and the minimum meaningful difference δ (§5) were chosen
   after seeing pilot data.** The mitigation is structural: pilot runs are non-citable, the
   registered batch is 150 fresh runs, and the choice is disclosed here with the pilot
   numbers that motivated it.

The design phase also produced, and this preregistration inherits by reference: the contest
policy (`design/POLICY-DRAFT.md` v0.3 — panel-reviewed, twice engine-verified, clean-room
checked; frozen copy lands at `policy/POLICY.md` at freeze), two reference implementations
in cell-for-cell agreement over a 2,540-cell grid, a 76-row gold suite with clause
citations whose expectations both engines and a clean-room oracle reproduce exactly, two
deterministic mutant generators with witness sets, prompt materials with full-verbatim
language references, and two registered inexpressibility results (X1, and the census's
output-side rows).

## The freeze and the primary attempt

The freeze commit is the squash-merge commit of the freeze PR on `main` — named by
reference because a squash hash cannot exist before the merge. At the freeze, every pin in
`harness/PINS.json` is filled; `results/primary-attempt-001` must not exist, and the scorer
refuses if it does. The governing invocation, run once from the freeze commit under the
pinned interpreter, is:

    <the CPython PINS.json pins> harness/score.py --attempt-root results/primary-attempt-001

The first invocation of that command is the primary attempt, crash and all. The scorer is
the only publisher; its outputs embed no timestamp and no absolute path.
`GATE(pre-freeze)`: `harness/` is the ported and extended Study 012 machinery (§7) — it
does not exist yet; this section binds its shape.

## 1. Question

Within the registered JPS-expressible policy fragment, under single-shot authorship, does
the representation a model authors in change **what its accompanying test suite pins
down** — compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a
prescribed judgment convention (arm C)?

**R1 (primary, retractable), two-sided difference form:** in the registered batch, the
per-arm **high-kill run rates** (§5, E4: fraction of admitted runs whose suite kills at
least τ of the paired adequate mutant subset) differ between arm A and arm C: the exact
two-proportion difference interval for A−C excludes zero, at the registered δ. The A−B
contrast is tested second under the same machinery (hierarchical order registered in §5).
An interval straddling zero is **INDETERMINATE** and licenses nothing — not equivalence,
not either direction's negation. Direction is reported as observed; the design-phase pilot
pointed B/C above A, and this registration deliberately does not presuppose it.

**R2 (secondary, descriptive):** the failure map — where each representation's suites are
blind (per-mutant-class kill profiles, engine-supplied vs assertion kills), the E1 ceiling
report, authoring latency and validity profiles, and the interpretive-spread census. R2 is
never adjudicated and never falsifies.

**Why A−C is first:** C is the live alternative architecture (Rego plus a small prescribed
judgment convention); A−C is the comparison the program would act on. B is the floor.

## 1a. Population and prospective content

No locked-replication stratum and no reviewer-holdout stratum: this is an authorship-rate
study in the 011/012 line, and its prospective content is the 150 post-freeze runs — no
authoring run exists at freeze time. Reviewer-authored prospective content lives in the
**sealed reviewer mutant set** (§4): authored during review rounds, committed verbatim,
first executed at the primary attempt, scored "as authored", reported separately, moving
nothing. The calibration pilots are non-citable and outside every population.

**Population rule, enforced in code (the Study 001/011 lesson).** The denominator of every
per-arm rate is attempted runs whose **apparatus** succeeded. Apparatus failures — slot
shape, call nonzero-exit, **call timeout at the registered ceiling**, golden-context
mismatch, binary digest mismatch, transcript refusal — are pipeline-invalid, excluded, and
reported with their own rate and interval. Every failure attributable to what the author
emitted — no extractable marker block, unparseable artifact, schema-invalid pack,
`opa check` failure, v0-syntax, unreadable output shape — is an **authoring outcome**:
valid, counted, and scoring zero on every endpoint it reaches. The E4 population adds one
further registered step: the **identity control** (§5), whose exclusions are reported, not
silent. A harness test diffs the prose partition table against the scorer's code partition
and against every code `admit()` can return. (Design-phase lesson, recorded: the pilot
driver mis-filed timeouts as an authoring code; the registered table must make that
impossible.)

## 2. Apparatus and pins

All pins null until the freeze; the scorer labels any run PILOT while any pin is null.
Resolved values below were verified empirically on 2026-08-14/15
(`design/TOOLCHAIN-NOTES.md`) and are re-verified fail-closed at run time.

- **jpack** v0.17.0: archive `judgment-pack_0.17.0_linux_amd64.tar.gz` sha256 `4046a101…`
  verified against the release `checksums.txt`; binary sha256 `42f35f79…`;
  reproducible-build attestation at freeze (jpack supports it). Verdicts and §8.4 error
  classes read from the JSON payload only; exit codes distinguish invocation failure
  (3/4/5 — apparatus) from an evaluator answer (0/1/2). Harness runs outside any
  `jpack.json` declaring an `audit` member. The operator PATH binary is v0.10.0 and must
  never be invoked.
- **OPA** v1.19.0: asset `opa_linux_amd64_static` sha256 `1dd5c559…` verified against the
  published per-asset checksum; **no reproducible-build claim exists** (official builds
  embed timestamp/hostname) — the pin is against the published artifact, stated here.
  License Apache-2.0 per `LICENSE` at the tag. Rego v1 pinned in prompt and invocation.
  Capabilities file generated from the pinned binary with the registered denylist;
  **the `time.now_ns` canary must be refused** (verified; re-verified at attempt time as a
  control gate). `opa exec` does not accept `--capabilities` (verified): scored
  invocations use per-row `opa eval --format json --fail --strict-builtin-errors
  --capabilities … --timeout …` under `env -i` with `TZ=UTC`, per-run exclusive
  directories. `opa test` failure exits 2; undefined-without-`--fail` prints `{}` exit 0
  (both verified — the harness relies on neither exit-code family for verdicts).
- **Authoring stack**: codex-cli 0.145.0, binary sha256 `a2a05daf…` — byte-identical to
  the Study 012 pin (baseline continuity). Model named by explicit flag at batch time; a
  model name is not a digest. Full 011/012 isolation discipline: fresh HOME/CODEX_HOME,
  `env -i`, golden pre-prompt-context capture from two agreeing probes, isolation negative
  control under recorded operator assent, credential copy deleted on seal and traps.
- **Interpreter**: CPython, implementation and series pinned, exact version recorded;
  runbooks name it by absolute path.
- **Prompts**: assembled deterministically (`design/pilot/assemble_prompt.py` lineage) from
  the frozen policy prose, the naming appendix, and the arm materials; each arm's
  assembled prompt pinned by sha256 at freeze. The call wrapper refuses on prompt digest
  mismatch. Byte sizes published (pilot values: A 84,289; B 204,333; C 206,686 — the
  asymmetry is the registered cost of full-page parity, §3).
- **Batch shape**: N = 50 runs/arm, 150 slots, sequential, never parallel; arm-interleaved
  first-order carryover-balanced schedule for three arms, re-derived and asserted by a
  harness test. **Registered batch window: three consecutive UTC calendar days** (pilot
  call durations: arm A 26–40 min, B/C 10–18 min; a one-day window is arithmetically
  impossible and is not registered). Crossing the window is a deviation. **Per-call
  timeout ceiling: 2700 s**, an apparatus bound; timeouts are pipeline-invalid, and a
  per-arm timeout rate above the registered cap (10% of slots) is a control-gate failure
  adjudicating R1 in neither direction.

## 3. Arms and prompt materials

| Arm | Artifact pair | Suffix materials |
|-----|---------------|------------------|
| A | Judgment Pack (specVersion 0.2.0-draft) + matrixVersion-2 test matrix | full spec + schema verbatim; task instructions |
| B | Rego v1 policy + opa test file | full OPA doc pages verbatim; **informal contract** (mechanical de-formalization of C's schema); task instructions |
| C | Rego v1 policy + opa test file | same doc pages; **prescribed judgment convention** (result JSON Schema + `default decision := {"disposition":"unresolved","reasons":["no-match"]}` + exclusion/precedence and unresolved-result conventions); task instructions |

- Shared header, byte-identical: the policy prose and the naming appendix (registered
  identifiers: outcome ids, ground tokens, pointer paths, evidence ids, Rego
  package/entrypoint, tri-state encodings, wire forms, the arm-A escalation
  trigger/target pin, the `applicability` prohibition).
- **Excerpt parity is full-verbatim, not curated** (panel rule): arm A receives the entire
  spec + schema (the prose spec alone was shown insufficient — it omits member names the
  schema carries); arms B/C receive twelve named official OPA doc pages in full at the
  pinned tag, fetched bytes retained under `design/prompts/upstream/` with per-source
  digests, plus a builtin signature list generated from the pinned capabilities file. One
  recorded derivation deviation: at v1.19.0 the docs live under `docs/docs/`, not
  `docs/content/`. Sufficiency (every construct a reference uses is documented) and
  policy-content prohibition (no clause names, thresholds, domain nouns in language
  materials) are asserted by committed checkers, both shown to have power on mutated
  inputs.
- B and C differ in **formality only**: `deformalize.py` generates B's prose contract from
  C's schema; byte-equality of the committed artifact with the generator's output is a
  freeze test.
- Authoring is **single-shot, no tools, no repair**. Artifact extraction is the registered
  marker rule (`PACK:`/`MATRIX:` for A, `POLICY:`/`TESTS:` for B/C; fenced block
  immediately following; last occurrence governs). Prompt iteration during design was
  governed by a symmetric disclosed budget; the design-phase materials were built by
  parallel builders under a shared fairness rule and are committed with their fairness
  notes.
- System boundary: in-system = what the pinned binary does at evaluation time;
  out-of-system = anything requiring an authoring loop. No outcome of this study is
  evidence about tooled authoring workflows (registered follow-up).

## 4. Oracle, references, mutants, and the X1 boundary

- **Gold**: 76 rows, hand-authored from the prose with per-row clause citations under the
  earliest-clause tie-break; structure, X1 exclusion, boundary witnesses, and clause
  coverage asserted by `check_gold.py`; both engines reproduce every row (floor gate); the
  clean-room oracle (different vendor from the arms' stack; process-isolated; six numbered
  decisions dispositioned in `design/cleanroom/DISPOSITION.md`) agrees 76/76 and
  2,540/2,540 on the design grid. `GATE(pre-freeze)`: the registered clean-room build
  re-runs against the frozen prose; divergences get written dispositions; unsettleable
  rows route to the ambiguity stratum mechanically.
- **References**: one per language, in cell-for-cell agreement over the design grid.
  `GATE(pre-freeze)`: **off-gold equivalence check** — the two references' agreement is
  re-established over the full derived input space, with every divergence point required
  to fall inside a registered exclusion class (currently exactly X1); any other divergence
  blocks the freeze. (Design-phase lesson: the E4 identity control evaluates
  author-written inputs that roam off-gold; a reference defect there voids an arm — this
  gate is what makes the identity control safe.)
- **X1 (registered exclusion class and census row)**: {new vendor yes; risk in [40,70);
  LOW country with spend unreadable, or country unreadable with spend ≤ 100,000.00} — the
  prose-correct outcome (review) is inexpressible in the fragment (0 of 2,048 onUnknown
  assignments; irreducible). Gold contains no X1 row, and **every authored test case whose
  inputs fall in X1 is excluded from identity and kill evaluation, with the per-run
  excluded-case count published**.
- **Mutants**: two deterministic generators (`design/mutants/*/gen_mutants.py`), 145 JPS /
  184 valid Rego single-edit mutants over the registered classes, each with its witness
  set over gold. **Pairing** is observable: identical sorted witness sets; the empty
  witness set is degenerate and never pairs. Cross-arm E4 runs over the paired adequate
  subset only; unpairable counts are published as a finding about the defect spaces.
  Kills achievable only through engine-supplied conflict detection (35 JPS mutants,
  listed) are reported both included and excluded. `GATE(pre-freeze)`: the **adequacy
  gate** — every mutant either killed by gold (witness set non-empty) or registered as
  dropped with its mechanism (several are provably unkillable — Kleene-monotone onUnknown
  flips on rules never unknown); the current work list is 47 JPS + 60 Rego empty-witness
  mutants; resolving it may add gold rows, and any added row re-runs the full agreement
  chain (engines, oracle).
- **Reviewer mutant set**: sealed, authored in review rounds, first executed at the
  primary attempt, scored "as authored", reported separately.

## 5. Endpoints and decision rule

Scored surface: **kind + outcomeId + reasons (as sorted sets)** under the registered
alignment map (two axes: run-level admission; row-level
APPROVE/REVIEW/ENHANCED-REVIEW/REJECT/UNRESOLVED(reason-set)/ROW-ERROR(class)). `handoff`
(state, triggeredBy, target) and `trace[]` are outside every endpoint; `applicability` is
forbidden by the appendix and asserted at admission.

- **E4 (primary): high-kill run rate.** Per admitted run: the suite passes the **identity
  control** (every non-X1 case agrees with the arm's unmutated reference on the scored
  surface; for B/C, `opa test` against the reference exits 0) — identity failures are
  reported per arm as a first-class rate; then the suite's **paired-subset kill rate** =
  killed / paired adequate mutants (kill = at least one non-X1 case disagrees on the
  mutant; for B/C, `opa test` nonzero with class recorded). A run is **high-kill** iff its
  paired kill rate ≥ **τ = 0.95** (chosen from pilot; disclosed in Design provenance).
  Per-arm high-kill rates carry exact Clopper–Pearson intervals; the registered contrasts
  are exact two-proportion difference intervals, **A−C first, then A−B** (hierarchical:
  A−B is confirmatory only if A−C is decided), each at **δ = 0.20** on the difference of
  high-kill rates, with an explicit INDETERMINATE row (interval straddles zero) that
  triggers nothing. Operating characteristics of (τ, δ, N=50) published in this document
  before the freeze. `GATE(pre-freeze)`: the OC table.
- **E1 (control, reported): per-run perfect gold agreement** on the policy artifact, ITT
  denominator. Expected at ceiling in every arm (pilot 15/15); reported with intervals; a
  per-arm E1 rate below the registered floor (0.60) is a **control-gate row** adjudicating
  R1 in neither direction (it would mean the stimulus regressed, not that testing skill
  differs).
- **E2: authoring-validity profile** — the ordered code table (apparatus codes separated;
  §1a), same denominator, headline not footnote.
- **E3: row-level failure taxonomy** on E1 failures and identity failures (categories as
  registered in the design brief; arm-structural categories within-arm-only, enforced in
  the scorer).
- **E5: interpretive-spread census** — per-arm distinct structural encodings and
  pairwise-disagreement profiles (012's census machinery, ported).
- Latency and artifact-size distributions per arm: descriptive, published (pilot showed a
  2–3× authoring-time asymmetry; it is data, not noise).

**Ordered, exhaustive decision rule** (first matching row; last row always matches):
1. Any pin/schema/manifest failure, or apparatus failure making the batch non-terminal →
   R1 inconclusive — pipeline-invalid.
2. Any control-gate failure (reference-vs-gold imperfect at attempt time; capabilities
   canary passes; golden-context gate; per-arm timeout rate > cap; E1 floor breached) →
   R1 inconclusive — control gate failed.
3. A−C interval excludes zero at δ → R1 decided, direction as observed; then A−B likewise.
4. Otherwise → INDETERMINATE; no claim in any direction is licensed.

## 6. Validity channel (separate from detection)

Control gates, above every substantive row: both references reproduce gold 100% at attempt
time; the off-gold equivalence certificate is current at the freeze commit; the OPA
capabilities canary is refused; the golden-context gate holds with the isolation negative
control on record; every binary digest matches its pin; the schedule matches the
registered plan. Manifest failures, unregistered absences, and enforcement failures are
NOT-ADJUDICATED — never detections.

## 7. Harness, controls, and counting integrity — `GATE(pre-freeze)`

The harness is the Study 012 machinery ported by digest (two-sided `PORTS.md` table;
`integrity.py` verifies the source study's lock first): call wrapper, batch driver
(three-arm schedule re-derived + tested), golden-context capture, transcript binding,
scorer skeleton (admit + ordered codes + exact rational Clopper–Pearson with registered
test vectors + terminality). New builds, already prototyped in `design/`: the per-language
admission layer, the two-engine execution layer, the alignment map, the mutant/kill
machinery with identity control and X1 filter, the E4 scorer (`design/mutants/e4_score.py`
lineage — deterministic, byte-identical reruns). The manifest is scoped per ADR 0004:
`DEVIATIONS.md` and `README.md` excluded by named constant with an asserting test; the
appendable-files rule is honored from day one. Pins registry: linear anchor order,
REGISTERED-vs-PILOT label rule, `--include-reviewer-set` refusing while any pin is null.
CI runs the deterministic controls only; the batch never runs in CI.

## 8. What is enforced, what is recorded, what is not prevented

Enforced: pins, digests, population membership, the X1 filter, the identity control, the
extraction rule, the schedule. Recorded: durations, token counts if reported by the CLI,
per-case diagnostics, every completion verbatim. Not prevented, stated plainly:
provider-side cross-session state (the independence premise behind every interval is
unclosable from retained bytes); an operator running and discarding an unrecorded batch;
the model having seen public Rego corpora at pretraining (§9). Nothing in the retained
artifacts proves the published slots are all the invocations that occurred; integrity
rests on ledger discipline and re-runnability.

## 9. What this study cannot show

Everything is measured **within the JPS-expressible fragment, selected by arm A's
expressive envelope and no other criterion** (Study 003: 12/12 real decisions escape the
pack); nothing generalizes to business judgments at large. Single-shot authorship only; no
outcome speaks to tooled authoring workflows (`packs test`/`suggest`, `opa` iteration),
the registered follow-up — nor to the fourth-arm prevalence control (JSON Logic/DMN),
deferred by decision 2026-08-14. One model, one prompt per arm, one policy family, one
batch window. **No direction of any result separates representation quality from training
familiarity**: the public Rego corpus is vast, the JPS corpus is this program, and no
gradient measurement is registered — both directions are reported as confounded. E1 at
ceiling in all arms is an expected finding about well-specified prose at this scale, not
evidence the representations are interchangeable. Kill rates measure agreement-anchored
mutation detection over registered single-edit mutants — not test quality at large, not
defect rates in production, and (for the 35 listed mutants) partly the engine's structural
checks rather than authored assertions, reported both ways. The gold suite is two authors
deep plus a clean-room check that shares the gold author's model lineage (registered;
third vendor declined 2026-08-15). The census's expressiveness rows and these rates live
on different stimuli: **no tradeoff statement combining them is licensed** (pinned as a
CORRECTION.md target). An INDETERMINATE outcome licenses nothing. Numeric outputs are a
JPS roadmap item (2026-08-14): census rows so marked describe the pinned spec version, not
JPS's future, and a spec change landing pre-freeze does not widen the fragment. Nothing
here measures whether any policy or fact is true, and nothing claims JPS conformance.

## 10. Publication commitment

All rates, all arms, all intervals, the full decision table, every identity-failure,
X1-exclusion, timeout, and unpairable-mutant count, the E1 ceiling report, and the latency
distributions are published whichever way they land, with a pass's prominence.
`CORRECTION.md` targets (verbatim wording, venue, URL, retrieval date) are pinned before
the freeze. A failed or INDETERMINATE R1 is reported with the same prominence as a decided
one.

## 11. What we would do with each outcome (NOT a registered commitment)

Discussion only; no observed result obligates any of it. If arm A's suites decisively
out-pin C's, the pack-plus-matrix format has evidence behind its testing story and the
evaluator line continues with the census as its boundary statement. If C (or B) decisively
out-pins A — the direction the pilot hints at — the natural next artifact is the
runtime/spec ADR exploring a JPS semantic profile over OPA, taking this study's census,
asymmetry ledger, and X1 as inputs; the gateway line is untouched either way, by design.
If INDETERMINATE, the result is a measured null at the registered δ and the program
decides whether a larger batch is worth the spend — outside this document.
