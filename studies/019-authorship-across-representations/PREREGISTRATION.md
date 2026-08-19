# Preregistration — Study 019: authorship across representations

**Status: DRAFT, eighth major revision (post-round-7). Not frozen. Nothing citable has
run. The cross-vendor review rounds are recorded in [`PREREG-REVIEW.md`](PREREG-REVIEW.md),
each verbatim under [`reviews/`](reviews/), and that record's round-state block is the
single machine-readable source for round counts, verdicts and open state. The rendered
sentence below is this header's ONLY statement of them — produced from the block by
`harness/render_round_status.py` and required here verbatim by the currency suite — so the
per-round detail lives in the record rather than being restated in a covered document. A
round is CLOSED when a written maintainer disposition per finding lands there, and a round
whose prompt is committed while its review has not landed is open in the other direction:
the lifecycle is a state read from the round's own artifacts (round-6 findings R6-1 and
R6-3; round-7 findings R7-3 and R7-4 moved the declaration of that state into the block and
the cross-check onto the tree). Every freeze pin is null; every execution before the freeze
is a PILOT and supports no claim. Items marked `GATE(pre-freeze)` are work that must land
before any review round can return `freezable as written` — which no round has returned, so
this header does not describe a freezable study. (The revision ordinal is stated honestly
rather than continuously: the fourth revision — the round-2 response — left this header
naming the third revision and the first review round, which is the drift round-3 finding
R3-10 caught. Rounds 4, 5 and 6 each found the repaired headers stale again in a way the
previous round's tests could not see, and round 7 defeated the header parser for the fourth
consecutive round. The maintainer decision registered on 2026-08-19 is that a status header
states nothing a test parses out of English: it carries a rendered sentence, the data behind
it is the record's block, and the truth of the surrounding prose rests on review.)**

<!-- round-status:begin -->
ROUND STATUS (rendered from PREREG-REVIEW.md's round-state block by harness/render_round_status.py; edit the block, never this sentence): 7 review rounds are on the record, 7 have returned a verdict — rounds 1-3 and 5-7 returned DO NOT FREEZE; round 4 returned FREEZABLE AFTER LISTED FIXES — and no round is open.
<!-- round-status:end -->


## Design provenance (disclosed, because it shaped the registered claims)

This draft was preceded by a design phase whose artifacts live under `design/` and whose
non-citable calibration pilot (`design/pilots/2026-08-15-calibration-pilot-01/`) shaped two
registered choices, disclosed here rather than discovered in review:

1. **The primary endpoint pivoted from policy correctness to test-pinning power.** In the
   pilot, every completed authoring run in every arm produced a policy artifact in perfect
   agreement with every gold row then authored (5/5 per arm, against the 76-row gold suite
   as it stood on 2026-08-15; the suite is 117 rows now): correctness is at ceiling for
   well-specified prose at this scale, in all three representations. The dimension with
   variance is what the run-authored test suites catch. R1 is therefore registered
   over E4 (kill rates), with E1 (gold agreement) as a reported control expected at
   ceiling — the ceiling itself being a finding this study commits to publishing.
2. **The high-kill threshold τ and the minimum meaningful difference δ (§5) were chosen
   after seeing pilot data.** The mitigation is structural: pilot runs are non-citable, the
   registered batch is 150 fresh runs, and the choice is disclosed here with the pilot
   numbers that motivated it.

**The pilot's arm-A identity-control episode, and what the quoted kill rates were
conditioned on (round-1 finding R1-18, disclosed here rather than in a design note).** In
the pilot as first scored, **all five arm-A suites failed the registered identity control**
— the control requires every non-excluded authored case to agree with the arm's own
unmutated reference, and 8 case failures fell on 3 distinct input points. Under the
registered rule arm A therefore had **no E4 denominator at all** in the pilot, and the
arm-A kill rates quoted in the second revision of this document were **off-protocol**:
computed after setting the failing cases aside, from a diagnostic block that the registered
rule excluded in full. That conditioning was not stated where the numbers were quoted, and
it is stated here now.

The cause was a reference defect, not an authoring defect, and it has been repaired: the
three divergent points were in the region this document used to register as the
inexpressibility class **X1**, the arm-A reference has been repaired
(`design/reference/refA/PACK-CHANGE-001.md`) so that it answers the prose-correct outcome
there, and the same five suites, byte-unchanged, now pass the identity control **5/5** with
refA and refB divergent on **0 of the 135** authored input points. X1 is retired (§4).

**The current pilot anchor is `design/mutants/E4-PILOT-v4.json`, and it is the only pilot
read this document cites.** `design/mutants/E4-PILOT.json`, `E4-PILOT-v2.json`,
`E4-PILOT-v3.json` and the pilot section of `design/mutants/E4-NOTES.md` are bannered
SUPERSEDED, each naming its successor, so the chain from the first issue to the current one
can be walked and is walked by a test: `design/mutants/E4-PILOT-v2.json` is the file whose
numbers the second and third revisions of this document quoted, and it was computed against
the pre-repair reference, a 145-mutant arm-A corpus and a 105-row gold suite, none of which
exist now. On current artifacts the pilot means on the paired subset are
**A 0.878, B 0.897, C 0.806**, and the high-kill fractions at the two registered integer
cuts are **A 1/5, B 0/5, C 0/5**. Two consequences are registered rather than glossed: the
pilot no longer places B/C above A at this endpoint, so **R1 registers no expected
direction**; and **τ = 0.95 is an openly pilot-chosen threshold with no surviving empirical
anchor** — the OC table's power grid (`design/mutants/OC-TABLE.md`) must be read as
covering the whole grid rather than a located operating point. The OC table itself now says
so in its own voice (round-2 finding R2-13): its §7 is titled *pilot fractions*, not *pilot
anchor*, it reads this file's named pilot and no other, and its §5 tabulates two named
regions of the grid with neither claimed to be where the study will land.

**What the round-3 re-score changed, stated prominently rather than folded into a mean
(round-3 findings R3-4 and R3-5).** Two re-scores were owed and both have landed.
`E4-PILOT-v3.json` corrected round-2 finding R2-3's fault-as-kill path and moved no kill
vector on these inputs. `E4-PILOT-v4.json` then applied something no pilot issue had ever
applied: **§4's registered per-case domain check**, called in the harness rather than
reimplemented, with the prototype refusing to score at all without it. It moved an arm.
**Arm C's identity control is 1 of 5, not 5 of 5**: four of its five admitted runs carry
exactly one case outside the registered input domain, which §4 makes an identity failure
categorised `out-of-domain-case`. All four omit the screening result, which the registered
domain admits no unreadable state for (§4's input-domain closure, and the certificate's
supplementary stratum is the reason it is closed); three of the four additionally pass a
`with input as` term with no `vendor` member at all. Arms A and B have none. Two quantities move in opposite directions and both are published:
**the high-kill denominator does not move** — §1a/§5 register admitted runs, an
identity-failing run stays in the denominator carrying `highKill: null`, so arm C is 0/5
and not 0/1 — while **arm C's descriptive mean paired kill rate rests on the one
identity-PASSING run of the five admitted** and is a one-run number wearing a mean's
clothes. (Admitted and identity-passing are different cohorts and round-4 finding R4-4
found several sentences of this package treating them as one: five arm-C runs are
admitted, one of them passed. Every identity count is over the five; every kill rate is
over the one.) Against the
superseded issue, the arms read A 0.888 → 0.878, B 0.902 → 0.897, C 0.855 → 0.806, with
C's move driven by the domain check and all three also carrying the round-3 adequacy
repair's larger gold suite and re-witnessed corpora. No high-kill fraction changed. The
currency suite fails while this section, `design/mutants/oc_table.py`'s `PILOT_FILE`
constant and the supersession chain on disk disagree — and, since round-3 finding R3-5,
agreement on a stale file is itself a failure, because the named file must be the END of
the chain and not merely the file all three happen to spell.

The design phase also produced, and this preregistration inherits by reference: the contest
policy (`design/POLICY-DRAFT.md` v0.3 — panel-reviewed, twice engine-verified, clean-room
checked; frozen copy lands at `policy/POLICY.md` at freeze), two reference implementations
in cell-for-cell agreement over a 2,540-cell design grid **and over the full 236,196-cell
derived space**, a 117-row gold suite with clause citations whose expectations both engines
and a clean-room oracle reproduce exactly, two deterministic mutant generators with witness
sets, prompt materials with full-verbatim language references, and one registered
inexpressibility result (the census's output-side rows — the second, X1, was tested rather
than argued in round 1 and did not survive).

## The freeze and the primary attempt

The freeze commit is the squash-merge commit of the freeze PR on `main` — named by
reference because a squash hash cannot exist before the merge. At the freeze, every pin in
`harness/PINS.json` is filled; `results/primary-attempt-001` must not exist, and the scorer
refuses if it does. The governing invocation, run once from the freeze commit under the
pinned interpreter, is:

    <the CPython PINS.json pins> harness/score.py --attempt-root results/primary-attempt-001 --include-reviewer-set

The first invocation of that command is the primary attempt, crash and all. The scorer is
the only publisher; its outputs embed no timestamp and no absolute path.

**`--include-reviewer-set` is part of the governing invocation and is mandatory for a
REGISTERED attempt** (round-1 finding R1-10). The flag used to be optional and the governing
command omitted it, so the sealed reviewer mutant set's registered property — "first
executed at the primary attempt" — could not occur at all. The rule is now two-sided and
enforced in `harness/score.py`: a REGISTERED label without the flag **refuses**, and the
flag while any freeze pin is null also refuses, `reviewerMutantSet.sha256` being one of
those pins. There is exactly one primary attempt, so there is exactly one execution of the
set (§4).

`harness/` is the ported and extended Study 012 machinery (§7) and **exists**: the wrapper,
the three-arm driver, the golden-context capture, the isolation negative control, the
transcript binding, the integrity chain and the single-publisher scorer are all built and
under test, and the whole apparatus has been driven end to end against the real pinned
engines with the authoring CLI stood in (`harness/tests/E2E-SMOKE.md`). No authoring call
has been made: every freeze pin is null and `integrity.study_label()` returns `PILOT`.

## 1. Question

Within the registered JPS-expressible policy fragment, under single-shot authorship, does
the representation a model authors in change **what its accompanying test suite pins
down** — compared across a Judgment Pack (arm A), raw Rego (arm B), and Rego under a
prescribed judgment convention (arm C)?

**R1 (primary, retractable), two-sided difference form:** in the registered batch, the
per-arm **high-kill run rates** (§5, E4: fraction of admitted runs whose suite kills at
least the registered integer cut of its own language's paired adequate mutant subset)
differ between arm A and arm C: **the A−C difference interval excludes zero at two-sided
α = 0.05**. The A−B contrast is tested second under the same machinery (hierarchical order
registered in §5). An interval straddling zero is **INDETERMINATE** and licenses nothing —
not equivalence, not either direction's negation. **δ = 0.20 is a registered interpretation
and power quantity and is not part of the decision rule** (§5); no decision anywhere in
this document reads δ. Direction is reported as observed, from the two arms' **rates** and
never from their raw counts, and this registration presupposes no direction: the design
phase's pilot pointed B/C above A, that reading did not survive the reference repair, and
the current pilot anchor (Design provenance) points weakly the other way on five runs per
arm.

**What A−C is a contrast between (the registered estimand; maintainer's decision of
2026-08-18, closing round-1 finding R1-17).** Arm C is not arm B plus formality. Arm B
receives a **result-shape-only floor contract**: a prose inventory of the result fields and
their permitted values, mechanically de-formalized from C's schema, and nothing else. Arm C
receives **the full prescribed judgment convention**: that same result shape as a JSON
Schema, plus five substantive conventions — a registered default decision, totality,
explicit precedence, unresolved handling, and grounds behaviour (§3). **A−C therefore
compares the pack format against Rego-plus-the-full-convention, as bundles.** The registered
treatment is the bundle, the estimand is the bundle's effect, and **no attribution of any
part of an A−C result to any component of the bundle — representation, result schema, or
any individual convention — is licensed** by this design (§9). A−B is the same comparison
against the floor contract, and B−C is not a registered contrast at all.

**R2 (secondary, descriptive):** the failure map — where each representation's suites are
blind (per-mutant-class kill profiles, engine-supplied vs assertion kills), the E1 ceiling
report, authoring latency and validity profiles, and the interpretive-spread census. R2 is
never adjudicated and never falsifies.

**Why A−C is first:** C is the live alternative architecture (Rego plus the full prescribed
judgment convention); A−C is the comparison the program would act on. B is the floor.

## 1a. Population and prospective content

No locked-replication stratum and no reviewer-holdout stratum: this is an authorship-rate
study in the 011/012 line, and its prospective content is the 150 post-freeze runs — no
authoring run exists at freeze time. Reviewer-authored prospective content lives in the
**sealed reviewer mutant set** (§4): authored during review rounds, committed verbatim,
first executed at the primary attempt, scored "as authored", reported separately, moving
nothing. Its bytes are freeze-pinned (`reviewerMutantSet.sha256`), it is loaded and
schema-checked before the attempt **without any engine being invoked on it**, it is executed
exactly once, and the decision (§5) is computed from members no part of it can reach. The
calibration pilots are non-citable and outside every population.

**Population rule, enforced in code (the Study 001/011 lesson).** The denominator of every
per-arm rate is attempted runs whose **apparatus** succeeded. Apparatus failures — slot
shape, call nonzero-exit, **call timeout at the registered ceiling**, pre-call refusal,
post-call wrapper failure, golden-context
mismatch, binary digest mismatch, transcript refusal — are pipeline-invalid, excluded, and
reported with their own rate and interval. Every failure attributable to what the author
emitted — no extractable marker block, unparseable artifact, schema-invalid pack,
`opa check` failure, v0-syntax, unreadable output shape — is an **authoring outcome**:
valid, counted, and scoring zero on every endpoint it reaches. One further authoring
outcome is registered here and is not an admission code — author protocol violation — the
transcript binding's author-side verdict: a run whose retained transcript shows the author
using a tool or taking a turn after the registered prompt is valid, counted, and scores
zero exactly as the six admission codes above do. The E4 population adds one
further registered step: the **identity control** (§5), whose exclusions are reported, not
silent. A harness test diffs the prose partition table against the scorer's code partition
and against every code `admit()` can return. (Design-phase lesson, recorded: the pilot
driver mis-filed timeouts as an authoring code; the registered table must make that
impossible.)

**The partition is closed over what the harness can emit, and closed fail-shut.** Every
wrapper exit status maps to a complete slot or to one apparatus code above; every refusal
of the transcript binding maps to one code above, by cause; and a code the partition does
not name — or an exit status the wrapper does not register — **refuses the whole attempt as
pipeline-invalid** rather than being materialized, sealed, ledgered and then silently
counted. (Round-1 lesson, recorded: the driver emitted two codes, `preflight-refused` and a
`wrapper-error` sentinel, that the partition named on neither side; the scorer excluded
only codes it recognised as apparatus, so both entered every per-arm denominator as
ordinary authoring runs. Exhaustiveness is therefore checked at import and enforced at
every write, not asserted in this paragraph.)

**Terminality, and what a declared shortfall costs.** The registered batch is 150 slots and
the registered population is that batch. A batch that does not complete may be **declared
short**, and the declaration is a schema carrying evidence rather than a note: it names the
registered prefix it stopped at, the ledger's own digest and chain head, and one row per
slot with its place in the registered call order, its seal digest, its wrapper exit and its
§1a code. The scorer **re-validates that declaration against the batch on disk** — schema,
registered constants, prefix property, hash chain, slot/seal bijection, and every count
derived from the inventory — and refuses a declaration that does not describe this batch.
A validated declaration is **terminal and not scored**: every level verdict is
`UNRESOLVED-BY-DESIGN`, **no endpoint, no rate and no contrast is computed**, and §5's
ordered rule reaches that row above every substantive one. (Round-1 lesson, recorded: the
declaration used to be fail-open — any JSON object, `{}` included, made an arbitrary
incomplete set terminal while the scorer went on to publish ordinary endpoints and
contrasts over it, which is outcome-selective deletion with a file as its only cost.)

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
  directories. **The `opa test` exit taxonomy, re-verified against the pinned binary at
  round 1 (finding R1-8): exit 0 every test passed; exit 2 at least one test FAILED; exit 1
  the invocation never got as far as running tests — a load, parse, compile or capability
  error.** This registration had it right and the harness had it reversed, counting every
  nonzero status as a mutant kill; the correction is in the code, and the taxonomy is
  written here in all three branches so that a two-branch reading is not available.
  Undefined-without-`--fail` prints `{}` exit 0 (verified). **No verdict and no kill is read
  from an exit code**: `opa test --format json` is parsed, a kill is an assertion failure on
  a named test, and a load/parse/compile/runtime/timeout failure is an apparatus refusal
  routed to the `engine-execution-clean` control gate (§5, §6) rather than counted as a kill
  in one direction and an identity failure in the other.
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
  asymmetry is the registered cost of full-page parity, §3). The B→C delta is prompt
  material, not formatting: it is part of the registered bundle A−C contrasts against (§1,
  §3), and it is published beside every result for that reason.
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
| B | Rego v1 policy + opa test file | full OPA doc pages verbatim; **result-shape-only floor contract** (a prose inventory of the result fields and their permitted values, mechanically de-formalized from C's schema, and nothing else); task instructions |
| C | Rego v1 policy + opa test file | same doc pages; **the full prescribed judgment convention** (the same result shape as a JSON Schema, PLUS five substantive conventions: a registered default decision `default decision := {"disposition":"unresolved","reasons":["no-match"]}`, totality, explicit precedence, unresolved handling, and grounds behaviour); task instructions |

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
- **B and C differ in two things, and the difference is substantive** (round-1 finding
  R1-17; maintainer's decision of 2026-08-18). `deformalize.py` generates B's contract from
  C's *schema* and byte-equality of the committed artifact with the generator's output is a
  freeze test — that is the **formality** half, and it covers the result shape alone. The
  second half is **content**: C additionally prescribes a default decision, totality,
  explicit precedence, unresolved handling and grounds behaviour, which B does not receive
  in any form. C's conventions can also change how often a run's policy passes the identity
  control, which is upstream of whether its suite can be high-kill at all. **No
  formality-only claim about the B/C difference appears anywhere in this registration**, and
  the second revision's claim to that effect is withdrawn. What is registered instead is §1's bundle: A−C
  compares the pack format against Rego-plus-the-full-convention, A−B against
  Rego-plus-the-floor-contract, and neither result attributes anything to a component.
  The alternative repair — giving B a de-formalized version of the *complete* convention
  and re-running calibration — was considered and **not adopted**: it would make B a second
  convention arm and delete the floor the design exists to measure against.
- Authoring is **single-shot, no tools, no repair**. Artifact extraction is the registered
  marker rule (`PACK:`/`MATRIX:` for A, `POLICY:`/`TESTS:` for B/C; fenced block
  immediately following; last occurrence governs). Prompt iteration during design was
  governed by a symmetric disclosed budget; the design-phase materials were built by
  parallel builders under a shared fairness rule and are committed with their fairness
  notes.
- System boundary: in-system = what the pinned binary does at evaluation time;
  out-of-system = anything requiring an authoring loop. No outcome of this study is
  evidence about tooled authoring workflows (registered follow-up).

## 4. Oracle, references, mutants, and the input domain

- **Gold**: **117 rows** (sha256 `6a41174b…`), hand-authored from the prose with per-row
  clause citations under the earliest-clause tie-break; structure, boundary witnesses, and
  clause coverage asserted by `check_gold.py`; both engines reproduce every row (floor
  gate); the clean-room oracle (different vendor from the arms' stack; process-isolated;
  six numbered decisions dispositioned in `design/cleanroom/DISPOSITION.md`) agrees
  **117/117** on gold and **2,540/2,540** on the design grid. The suite grew from 109 rows
  when the round-3 adequacy repair closed §4's gate: eight rows authored by hand from
  `design/POLICY-DRAFT.md` v0.3 with clause citations, each note naming the deriving
  sentence, and the mechanical search contributing cell coordinates only. `check_gold.py`
  carries an
  exclusion registry that is **empty**, and additionally fails if no gold row sits inside
  the former X1 region — an exclusion that once existed must stay falsifiable.
  `GATE(pre-freeze)`: the registered clean-room build re-runs against the frozen prose;
  divergences get written dispositions; unsettleable rows route to the ambiguity stratum
  mechanically.
- **References**: one per language, in cell-for-cell agreement over the design grid.
  **Off-gold equivalence: SATISFIED at design time and re-issued at the freeze commit** —
  the full 236,196-cell registered derived space evaluated on both references
  (`design/reference/OFFGOLD-CERT.md`): **exactly 0 divergences**, status PASS. (This gate
  is what makes the identity control safe: author-written inputs roam off-gold.)
  **Input-domain closure, registered**: the screening result is always reported — the
  Inputs section admits no unreadable state for it, the canonical grid and the admission
  layer assert it, and the certificate's labelled supplementary stratum shows why the
  closure matters: on sanctions-absent inputs no clause governs, and three correct-on-gold
  implementations give three different answers. Undefined behavior stays outside every
  registered space by domain closure, not by luck.
- **The registered input domain is common to all three arms, and is enforced symmetrically**
  (round-1 finding R1-3). The domain is the nine registered axes with their readable values
  plus, on the axes that admit it, the registered omitted-member encoding of
  "unreadable/unreported"; the two wire forms the naming appendix assigns (arm A's decimal
  strings, arms B/C's JSON numbers) are the same domain in two encodings and are checked as
  such. **Every arm's case inputs are enumerated mechanically from the artifact the author
  emitted** — arm A's from the matrix, arms B/C's from the `opa test` file's own syntax tree
  under `opa parse --format json`, with a second registered mode that recovers table-driven
  points by evaluating the suite's own package under the pinned binary — and each enumerated
  case is validated against the registered domain **before** identity and mutation
  execution, identically in A, B and C. An out-of-domain case is an identity failure
  categorised `out-of-domain-case` and published per arm; a case structure that cannot be
  enumerated is the registered authoring code `unparseable-artifact`. **The registered
  exclusion registry is EMPTY**, and an unclassified divergence blocks the freeze rather
  than being filtered.
- **X1: RETIRED (round-1 finding R1-2).** The second revision registered X1 —
  {new vendor yes; risk in [40,70); LOW country with spend unreadable, or country
  unreadable with spend ≤ 100,000.00} — as an inexpressibility class and excluded every
  authored case falling in it from identity and kill evaluation. **That claim was tested
  rather than argued and did not survive**: a pack in the same fragment produces the
  prose-correct `review` there, the arm-A reference was repaired
  (`design/reference/refA/PACK-CHANGE-001.md`, digest `956ceebb…` → `db977607…`), and the
  two references now agree on all 236,196 cells. There is no exclusion class, no per-case
  X1 filter and no per-run excluded-case count; the region is instead **covered by gold**
  (six rows — five inside the region and one adjacency control just outside it, the
  narrowness check) and re-measured on every certificate run as
  a permanent `retired-x1-regression` validation record. The inexpressibility census keeps
  its output-side rows, which are untouched by this repair.
- **Mutants**: two deterministic generators (`design/mutants/*/gen_mutants.py`), **183 JPS**
  and **185 generated / 184 valid Rego** single-edit mutants over the registered classes,
  each with its witness set over gold. **Pairing** is observable: identical sorted witness
  sets; the empty witness set is degenerate and never pairs. On the current manifests:
  **157 witness groups in total, of which 33 are shared and non-degenerate** (1 degenerate
  group excluded), covering **69 JPS and 62 Rego** paired adequate mutants; **88 adequate
  JPS and 88 adequate Rego mutants are unpairable**. Both the total and the shared group
  counts are published, because they answer different questions and a single "groups"
  number has been read as either. Cross-arm E4 runs over the paired adequate subset only;
  unpairable counts are published as a finding about the defect spaces. Kills achievable
  only through engine-supplied conflict detection — **27 JPS mutants**, marked on every
  manifest record and measured over the whole registered domain rather than over gold
  witnesses, against a **registered EMPTY class for Rego** stated with its reason — are
  reported both included and excluded.
- **Adequacy gate: `GATE(pre-freeze)` — CLOSED, and the artifact says so rather than this
  sentence** (`design/mutants/ADEQUACY.md`). The gate was satisfied on 2026-08-15, was
  **re-opened by the arm-A reference repair** — a mutant corpus is a function of its
  reference, so the JPS corpus was regenerated and the Rego corpus re-witnessed, and mutant
  ids do not carry across the repair — and round-3 finding R3-2 found it still open with 37
  JPS and 34 Rego empty-witness mutants undispositioned while the round-2 response reported
  it accepted. It is now re-closed, by the round-1 discipline and not by re-keying: dense
  mechanical search for a witnessing input, a gold row authored from the prose with a clause
  citation wherever a witness exists, a registered drop with its mechanism where none
  exists. Current census: **157/183 JPS and 150/184 Rego killed by gold**; the remaining
  **26 JPS and 34 Rego are registered as dropped with their mechanisms**, and **0 JPS and 0
  Rego empty-witness mutants undispositioned**. Eleven of the 37 JPS mutants were killed by
  the eight rows gold grew by; the drop registry is checked in **both** directions before
  anything is stamped, so an unregistered empty-witness mutant and a stale registry entry
  are each blocking. Re-closing the gate moved gold, the pairing and both integer cuts, and
  every artifact that quotes them (`design/mutants/OC-TABLE.md` §7, the current pilot, and
  this section) was regenerated with it. (Recorded with its attribution kept separate from
  its size, round-4 finding R4-2: **nine** of the 26 JPS drops are the new
  `subsumed-region-lemma` class — `r-o1-review`'s region is a strict subset of
  `r-o1-wide-low`'s, both name `review`, and D5 suppresses them together, so a gold suite
  cannot see an edit that moves cells *within* the containing region — but only **six** of
  the nine are the repair's marginal price; the other three were already unkillable in the
  pre-repair corpus. In the labelled form every registered surface carries verbatim, rebuilt
  by the harness suite from the derived artifact (round-6 finding R6-2):
  **Gross class size: 9; marginal to the X1 repair: 6; already unkillable before it: 3**.
  The one boundary edit that leaves the containing region, `m-a-076`, is
  killed. The split is derived in `design/mutants/adequacy_region_lemma_price.json`, not
  asserted. The reference is **not** changed for it; a second repair would re-open this
  gate, the off-gold certificate and the corpus.)
- **Review flag A1: CONFIRMED, not live.** At risk exactly 40 in a LOW country the
  permitted spend ceiling drops twentyfold across one point; the text is unambiguous, four
  gold rows depend on it, and the drafter's intent was put and confirmed on 2026-08-15
  (`design/mutants/ADEQUACY.md`, "A1 disposition") — the cliff is intended and the prose is
  not amended. The remaining dispositions carry
  their scope caveats (C1–C5) as recorded.
- **Reviewer mutant set**: sealed, authored in review rounds, freeze-pinned by digest,
  validated without execution before the attempt, first executed at the primary attempt
  under the mandatory `--include-reviewer-set`, executed exactly once, scored "as authored"
  through the same kill machinery, published in its own section, and reaching no member the
  decision reads. No reviewer mutant is paired, enters a witness group, or moves a cut.

## 5. Endpoints and decision rule

Scored surface: **kind + outcomeId + reasons (as sorted sets)** under the registered
alignment map (two axes: run-level admission; row-level
APPROVE/REVIEW/ENHANCED-REVIEW/REJECT/UNRESOLVED(reason-set)/ROW-ERROR(class)). `handoff`
(state, triggeredBy, target) and `trace[]` are outside every endpoint; `applicability` is
forbidden by the appendix and asserted at admission.

- **E4 (primary): high-kill run rate.** Per admitted run: the suite passes the **identity
  control** (every case whose inputs are in the registered domain agrees with the arm's
  unmutated reference on the scored surface; for B/C, `opa test` against the reference
  exits 0) — identity failures are reported per arm as a first-class rate, with
  out-of-domain cases named as their own category; then the suite's **paired-subset kill
  rate** = killed / that language's paired adequate mutants (kill = at least one in-domain
  case disagrees on the mutant; for B/C, a named test's assertion fails under
  `opa test --format json`, never an exit code). **Two integer cuts, one per language.**
  A run is **high-kill** iff it kills at least ⌈τ·N_lang⌉ of **its own language's** paired
  adequate subset, at **τ = 0.95**; each cut is derived at run time from that language's own
  denominator and **asserted reachable** (a cut above its denominator refuses rather than
  making the endpoint unattainable). At the current manifests those cuts are **66 of 69 for
  JPS (arm A) and 59 of 62 for Rego (arms B and C)**, and both are published beside every
  rate. (Round-1 lesson, recorded: one cut was derived from the JPS count and applied to
  every arm while each arm's denominator stayed language-specific, so a perfect Rego suite
  could not be high-kill and the primary endpoint was impossible for two of the three
  arms.) A group-level pairing does **not** equalise the per-arm denominators; the two arms'
  rates are quantised on different lattices, and both denominators and both cuts are
  published rather than reconciled. Runs carrying **authoring-outcome codes remain in the E4
  denominator as not-high-kill** (no-marker included); only apparatus codes leave it, and
  identity-control exclusions are reported, never silently dropped. **The E4 denominator of
  each arm in a computed contrast must be positive**; a contrast over an empty arm is not
  INDETERMINATE, it is not computed at all, and the outcome falls to the rows above.
  Per-arm high-kill rates carry exact Clopper–Pearson intervals.
- **The registered contrast, and what it is honestly called.** The construction is the
  **general unequal-N Farrington–Manning score inversion** with the nuisance parameter
  eliminated by maximisation over the registered rational mesh `M = {k/1000}`, in exact
  integer arithmetic, at nominal two-sided α = 0.05 — construction and calibration pinned
  in `design/mutants/OC-TABLE.md` (whose equal-N closed form is the N_A = N_C slice), tested
  **A−C first, then A−B** as fixed-sequence gatekeeping (FWER controlled at α, no further
  adjustment). **What this study publishes is named an `exact-arithmetic mesh-inversion
  hull`, and it is not claimed to be an exact 95% confidence interval over the continuous
  parameter space** (round-1 finding R1-16). Two approximations are registered and travel
  inside every published record with the direction each errs in: the nuisance supremum over
  `M` is a **lower** bound on the continuum supremum, so the procedure may be
  anti-conservative by at most a published, exactly computed slack bound
  (`levelCertifiedOverContinuum: false`, `nuisanceMeshSlackBound`); and the Δ₀ inversion
  over the registered mesh **Δ₀ mesh denominator 100** (every attainable rate difference at
  N = 50 is a mesh point), with **48 exact-integer bisections** for the constrained MLE,
  yields the hull of accepted mesh points — an **inner** approximation, never wider than the
  continuum interval. A certified continuum supremum was costed and **declined** (a mesh of
  denominator ~50,000 inside a binary search inside the sweep); relabelling is the registered
  response, and nothing is adjusted by the slack bound. The decision reads the Δ₀ = 0
  inversion, which is an exact mesh point.
- **The decision, stated once.** **A contrast is decided iff the A−C difference interval
  excludes zero at two-sided α = 0.05** — §1's R1 sentence and this one carry that clause in
  the same words, and it is the whole of the rule. **δ = 0.20 is the registered minimum
  meaningful difference — an interpretation and power quantity, not part of the decision
  rule**; no decision reads it, the code that carries it reads it nowhere, and **no decision
  statement in this document qualifies zero-exclusion by δ** (round-1 finding R1-15: the two
  readings — exclusion of zero, versus exclusion of the whole ±δ band — are materially
  different procedures, they disagree on every interesting cell of the OC grid, and only the
  first is registered). **Direction is derived
  from the two arms' rates**, never from their raw counts, because apparatus exclusions can
  leave unequal denominators and a count comparison reverses on them. INDETERMINATE
  (interval straddles zero) triggers nothing. OC table: **published**
  (`design/mutants/OC-TABLE.md`) — at N = 50, power for a true 0.20 gap runs 0.49–0.82 by
  position, and a true 0.25 gap can still return INDETERMINATE, stated so no reader mistakes
  δ for a detectability promise. **The OC's pilot anchor is not a located operating point
  any more**: the current pilot high-kill fractions on the paired subset are A 1/5, B 0/5,
  C 0/5 (Design provenance), so the power grid is to be read whole. Those three
  denominators are **admitted** runs and are unaffected by arm C's four identity failures,
  which is this section's denominator rule with a live witness rather than a hypothetical
  (round-3 finding R3-6, closing the OC table's D3 denominator-in): the identity-failing
  runs are in the five, carrying `highKill: null`, and the primary scorer, the pilot scorer
  and `design/mutants/OC-TABLE.md` §7 all read that one published block.
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
  pairwise-disagreement profiles (012's census machinery, ported). **Registered census
  stimulus: the gold-row input set** (the frozen gold suite's inputs — 117 at this revision,
  and the freeze pins the count in `harness/PINS.json`'s `goldSuite.rows`; disagreement
  profiles are computed over exactly these cells, closing the §9 joint-reading concern about
  unstated stimuli).
- Latency and artifact-size distributions per arm: descriptive, published (pilot showed a
  2–3× authoring-time asymmetry; it is data, not noise).

**Ordered, exhaustive decision rule** (first matching row; last row always matches):
1. Any pin/schema/manifest failure, or apparatus failure making the batch non-terminal →
   R1 inconclusive — pipeline-invalid.
2. A validated shortfall declaration (§1a) → UNRESOLVED-BY-DESIGN — the batch was declared
   short; every level verdict is UNRESOLVED-BY-DESIGN and no contrast is computed.
3. Any control-gate failure (reference-vs-gold imperfect at attempt time; capabilities
   canary passes; golden-context gate; engine-execution-clean; per-arm timeout rate > cap;
   E1 floor breached) → R1 inconclusive — control gate failed.
4. The A−C difference interval excludes zero at two-sided α = 0.05 → R1 decided, direction
   as observed from the rates; then A−B likewise.
5. Otherwise → INDETERMINATE; no claim in any direction is licensed.

**No inferential quantity is computed, let alone published, at or above row 3.** A
control-gate failure "adjudicates R1 in neither direction", and computing a contrast and
then discarding it is not that rule: the gate rows are evaluated first, the contrast is
computed only for an outcome that would reach row 4, and no direction and no A−B result is
exposed otherwise. An **absent** primary contrast is not a straddling one and never reaches
row 5. (Round-1 lesson, recorded: an outcome with a failed gate and a rejecting A−C reached
row 2 correctly and still printed "Decided yes" and a direction, and an arm with zero
admitted runs passed the E1 floor by definition and was published as a substantive
INDETERMINATE with no interval in existence.)

## 6. Validity channel (separate from detection)

Control gates, above every substantive row: both references reproduce gold 100% at attempt
time; the off-gold equivalence certificate is current at the freeze commit; the OPA
capabilities canary is refused; the golden-context gate holds with the isolation negative
control on record; **every scored engine invocation of the attempt returned an answer**
(`engine-execution-clean` — a pinned engine that timed out, failed to compile or refused on
a *frozen* study artifact is an apparatus failure, and it is neither a kill nor an identity
failure); every binary digest matches its pin; the schedule matches the registered plan.
**A gate the scorer did not evaluate fails**: an absent gate is not a gate that held.
Manifest failures, unregistered absences, and enforcement failures are NOT-ADJUDICATED —
never detections.

## 7. Harness, controls, and counting integrity

**The harness exists and is under test.** It is the Study 012 machinery ported by digest
(two-sided `PORTS.md` table; `integrity.py` verifies the source study's lock first): call
wrapper, batch driver (three-arm schedule re-derived + tested), golden-context capture,
isolation negative control, transcript binding, and the single-publisher scorer (admit +
ordered codes + exact rational Clopper–Pearson with registered test vectors + terminality).
Built here and prototyped in `design/`: the per-language admission layer, the two-engine
execution layer, the alignment map, the mutant/kill machinery with the identity control,
the registered input domain with its symmetric per-arm case enumeration, the E4 scorer
(`design/mutants/e4_score.py` lineage — deterministic, byte-identical reruns), the ordered
decision table, and the sealed reviewer set's loader/executor.

**Integrity is a gate against drift, not a root of trust, and the bootstrap is stated
rather than glossed** (round-3 finding R3-7). The honest property, and the one under test,
is this: `integrity` is **the only study-local module the scorer imports at module scope**,
it imports no study-local module itself, and `integrity.verify()` is the **first
study-local call** the scorer makes — so exactly one module of this harness, the one doing
the verifying, is bound before verification, and a pre-verification failure binds nothing
else. What that cannot be is a proof that the checker is the checker the manifest
describes: code that must run in order to check itself cannot check itself first. The
earlier revisions of this sentence claimed integrity ran before the scorer bound any study
module at all, which was false of `score.py`'s own import list; that claim is
withdrawn and replaced by the three assertions above, each of them a test
(`tests/test_score_attempt.py`, by AST over the source and by measurement in a fresh
interpreter). The exact-set manifest
covers every byte the scorer executes and every payload it reads — the scorer's own package,
both reference implementations, every mutant payload with a per-file hash, the off-gold
certificate and the sealed reviewer set — and the port chain, the interpreter check, the
untracked-source and unreviewed-bytecode scan and the manifest verification all run and are
fatal before any of those modules is bound. The manifest is scoped per ADR 0004:
`DEVIATIONS.md`, `README.md` and — since round-3 finding R3-1 — **`PREREG-REVIEW.md`** are
excluded by named constant (`make_manifest.EXCLUDED_DOCUMENTS`, a mapping of path to
reason), each with an asserting test; the appendable-files rule is honored from day one and
now honored for the file that most obviously needed it. Pins registry: linear anchor order,
REGISTERED-vs-PILOT label rule over the **whole freeze set** — the freeze pins include the
capabilities digest, the reproducible-build attestation, the model, the probe prompt, the
golden context, the isolation assent and the reviewer mutant set, so `REGISTERED` is not
reachable while any of them is null — and `--include-reviewer-set` refusing while any pin is
null, while a REGISTERED attempt without it also refuses. CI runs the deterministic controls
only; the batch never runs in CI, and the tests that invoke the pinned engines skip by name
there.

**The manifest is regenerated LAST, a stale one fails the suite twice, and the file that
kept staling it is out of the covered set** (round-2 finding R2-1; round-3 finding R3-1).
The manifest used to cover `PREREG-REVIEW.md`, so writing a review disposition after
regenerating it left the committed manifest describing a tree that no longer existed. That
happened three rounds running — between rounds 1 and 2, between 2 and 3, and inside the
round-2 response, which reported a green suite while three enforcement tests were red.
Round 2's answer was a procedure and a second failing test; **a procedure that must be
remembered every round is not a safeguard**, and the third recurrence is the evidence. The
root fix is ADR 0004's own decision, applied to the file it plainly describes: the review
record is appendable by design and leaves the covered set by named constant, so appending a
disposition can no longer stale anything. Two tests still fail on a genuinely stale
manifest, under two different names, so that failure cannot be mistaken for one test's
flakiness (`tests/test_manifest.py` compares the exact set; `tests/test_prereg_currency.py`
carries manifest currency alongside the counts), and two more assert the exclusion itself —
including that re-covering the review record fails. **The order is still fixed: every
artifact and document edit first, `harness/make_manifest.py` last, then the full pinned
suite from the resulting tree.**

**Deterministic regeneration of the mutant corpora** is claimed by
`design/mutants/regenerate.py --arm both --check`, which regenerates into a scratch copy
and byte-compares every committed artifact. Three properties are registered: the record it
commits (`design/mutants/REGENERATION-CHECK.json`) must cover **both** arms — a single-arm
record is not written at all — the fail-closed adequacy census is evaluated **under the
regenerated tree**, never under the committed one, so a newly generated empty-witness
mutant cannot evade it (round-2 finding R2-11), and the **adequacy stamp is inside the
regeneration chain** rather than beside it (round-3 finding R3-2). The third is the one the
repair needed: while stamping was a separate hand-run step, regenerating the corpus rewrote
each MANIFEST without a stamp, so `pass` was structurally unreachable and the stamp was
never byte-compared — which is how a pre-repair drop table survived a corpus regeneration
unread. `byteIdentical` is the reproducibility claim; `pass` additionally requires both
arms and both adequacy stamps. At this revision the check is **376/376 byte-identical with
`pass: true`** (round-5 finding **R5-7**: this sentence said 375, the count before the
round-4 response added the derived `adequacy_region_lemma_price.json` to the chain, and the
count is now read out of the record by `tests/test_prereg_currency.py` rather than typed).
Enforced by `tests/test_design_regeneration.py`.

`GATE(pre-freeze)` in this section is now **closed**, and closing it is what round-5
finding **R5-1** cost. The `design/` sources it used to name are committed (scaffold item
T3, round-4 finding R4-6). Compiled bytecode is the other half and it is not a thing to be
committed but a thing that must not be: a `.pyc` beside a reviewed source is a byte that
runs unreviewed, so `integrity.verify_bytecode()` refuses any cache the running sources did
not produce **and refuses a tracked one outright**, `make_manifest.py` reports it as a
manifest problem and refuses `--freeze` on it, the study root carries the repository's
house `.gitignore`, and a currency test reads `git ls-files` so the property binds the
INDEX rather than the working tree. The round-4 response committed one and reported a green
suite over a tree that `integrity.py` refused on the next checkout; that is the whole
reason the enforcement is now in four places rather than one. §4's adequacy gate, which
this sentence used to name beside them, is re-closed.

## 8. What is enforced, what is recorded, what is not prevented

Enforced: pins, digests, population membership, the registered input-domain check on every
arm's enumerated cases, the identity control, the extraction rule, the schedule, the
transcript binding on every completed slot. Recorded: durations, token counts if reported by the CLI,
per-case diagnostics, every completion verbatim. Not prevented, stated plainly:
provider-side cross-session state (the independence premise behind every interval is
unclosable from retained bytes); an operator running and discarding an unrecorded batch;
the model having seen public Rego corpora at pretraining (§9). Nothing in the retained
artifacts proves the published slots are all the invocations that occurred; integrity
rests on ledger discipline and re-runnability.

## 9. What this study cannot show

**A−C is a bundled treatment and nothing inside the bundle is separable** (§1, §3). Arm C
differs from arm B in representation-adjacent *formality* (the result shape as a schema
rather than as prose) **and** in substantive *content* (a default decision, totality,
explicit precedence, unresolved handling, grounds behaviour), and the arms' prompt exposures
differ in bytes as well. **No A−C or A−B result licenses any statement about which component
of the bundle produced it** — not "the pack format wins", not "the schema is what matters",
not "the convention is doing the work". The registered claim is about the bundles as
authored, and a component-attribution study is a different design.

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
defect rates in production, and (for the 27 JPS mutants the manifest marks
`engineSuppliedKill`) partly the engine's structural checks rather than authored assertions,
reported both ways. **The mutant space also inherits the arm-A reference's shape, and the
round-3 adequacy re-closure measured one instance of it**: `r-o1-review`'s region is a
strict subset of `r-o1-wide-low`'s, both say `review`, and D5 suppresses them together, so
nine mutants of that rule change no cell's answer and no test suite in any arm can detect
them — six of the nine marginally because of the repair, three of them already before it,
and its one edit that widens *out* of the containing region is killed (§4;
`design/mutants/ADEQUACY.md`, `subsumed-region-lemma`;
`design/mutants/adequacy_region_lemma_price.json`). They are registered
drops rather than a thin spot in gold, and the general statement is the one that
generalises: a kill rate is bounded by what the reference makes observable, not by what a
suite could in principle notice. The two arms' kill denominators are different sizes and
their rates are quantised on different lattices; the two integer cuts are published side by
side and nothing reconciles them. The gold suite is two authors
deep plus a clean-room check that shares the gold author's model lineage (registered;
third vendor declined 2026-08-15). The census's expressiveness rows and these rates live
on different stimuli: **no tradeoff statement combining them is licensed** (pinned as a
CORRECTION.md target). An INDETERMINATE outcome licenses nothing. Numeric outputs are a
JPS roadmap item (2026-08-14): census rows so marked describe the pinned spec version, not
JPS's future, and a spec change landing pre-freeze does not widen the fragment. Nothing
here measures whether any policy or fact is true, and nothing claims JPS conformance.

## 10. Publication commitment

All rates, all arms, all intervals — published under their registered name, the
**exact-arithmetic mesh-inversion hull**, with `levelCertifiedOverContinuum: false`, the
nuisance-mesh slack bound and the direction each approximation errs in travelling inside
every record (§5) — the full decision table, every identity-failure, out-of-domain-case,
timeout, and unpairable-mutant count, both group counts, both integer cuts, the E1 ceiling
report, and the latency
distributions are published whichever way they land, with a pass's prominence.

**What "all intervals" means, and the one thing this commitment does not promise**
(round-3 finding R3-8). Every quantity that EXISTS is published whichever way it lands, and
nothing is withheld for being unflattering — that is the whole of the commitment. It is not
a promise that a contrast interval exists in every outcome, because §5 forbids computing
one above row 3: an outcome that reaches a gate row has **no** A−C or A−B interval to
publish, and the record says so by naming the row and the cause rather than by printing an
endpoint. A blocked contrast is published as blocked, with its cause, in the same record
and with the same prominence. The rule is ordered rather than conditional, so it holds for
a gate failure discovered LATE as well as early: if the secondary contrast fails after the
primary has been evaluated, the primary's interval is settled to the decided row it
actually reached and no partially computed secondary quantity is emitted. Publishing a
number the registered rule says must not be computed is not a stronger publication
commitment; it is a violation of §5 wearing one.
`CORRECTION.md` targets (verbatim wording, venue, URL, retrieval date) are pinned before
the freeze, in the registered document **`CORRECTION-TARGETS.md`** — round-7 finding
**R7-9**: this obligation was declared here and enforced nowhere, so the ceremony could
complete without it. It is a registered document in `harness/make_manifest.py`, which names
it while it is absent and refuses `--freeze` on it, and the freeze runbook carries the step
that lands it. A failed or INDETERMINATE R1 is reported with the same prominence as a
decided one.

## 11. What we would do with each outcome (NOT a registered commitment)

Discussion only; no observed result obligates any of it. If arm A's suites decisively
out-pin C's, the pack-plus-matrix format has evidence behind its testing story and the
evaluator line continues with the census as its boundary statement. If C (or B) decisively
out-pins A — the direction the design-phase pilot pointed at before the reference repair,
which the current anchor no longer supports either way — the natural next artifact is the
runtime/spec ADR exploring a JPS semantic profile over OPA, taking this study's census, its
asymmetry ledger and the retired-X1 episode as inputs; the gateway line is untouched either
way, by design. If INDETERMINATE, the result is a measured null — an interval straddling
zero, which licenses nothing about a gap of any size, δ included — and the program decides
whether a larger batch is worth the spend, outside this document. In every branch, the
bundled estimand (§1, §9) means the next artifact cannot start from a component
attribution this study did not make.
