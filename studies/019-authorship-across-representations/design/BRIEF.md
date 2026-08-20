# Study 019 design brief — authorship across representations (JPS vs OPA/Rego)

**Status: DRAFT design brief v3, pre-preregistration. Nothing here is registered. v1 was put
through a three-lens adversarial panel (methodology/circularity, fairness/confounds, program
fit); v2 absorbed 11 blockers and ~20 majors. v3 records the maintainer's three design
decisions (2026-08-14): N=50/arm, arm C at full convention, fourth arm deferred to a
registered follow-up. This document seeds the PREREGISTRATION.md.**

Responds to an external advisory note proposing "JPS vs OPA/Rego: does a constrained judgment
representation improve AI policy authorship reliability?" The note is adopted in substance and
corrected where its premises fail against the runtime, and the design is restructured where the
program's own record showed v1's measurement spine was unsound.

---

## 0. Reconciliation with the program's actual state

- The note proposes this as "Study 014" ("Study 013 is already running"). Studies 013–018 are
  all closed (015 closed last, after 12 review rounds: frozen 7797a77, R1 holds, merged #68).
  This slots in as **Study 019**. Proposed slug: `019-authorship-across-representations`
  (naming the mechanism; deliberately not a near-collision with `001-policy-representation`).
- **Study 001 reconciliation (required, missing from v1).** 001 is the program's one prior
  head-to-head efficacy comparison touching JPS representation, and its registered primary
  endpoint (H1) was **not supported**, with H4/H5 also failing. 019 differs in kind: 001 measured
  a model *applying* a policy through a pack at evaluation time; 019 measures models *authoring*
  the representation itself, on one policy, with a C arm 001 never had. The prior negative does
  not answer 019's question — but the preregistration must say so by name, or round 1 will read
  019 as re-running a failed comparison until a favorable comparator was found.
- `docs/adr/0001-evaluate-on-rulearena-first.md` records OPA/Gatekeeper libraries as surveyed and
  **rejected — as a benchmark corpus**, partly on licensing. Adopting OPA as a *comparison arm*
  is a different decision; the preregistration states the distinction. OPA is Apache-2.0
  (verified from the repository LICENSE at pin time, not from memory) and enters the studies
  index's third-party projects table (repo, pinned release tag + asset sha256, license) plus a
  study-local `upstream/` record.
- Proposed index row: № 019 | "Does a constrained judgment representation change how reliably a
  model authors an executable policy, compared with a general policy language?" | Theme:
  Blinded authorship / Efficacy track | External source: Open Policy Agent | Status:
  Preregistered, not yet run.
- Study 018's design decision D-1 (no evaluator binary; fully offline adjudication) is
  deliberately reversed: this study's point is executing two engines. Stated trade: adjudication
  is exactly as reproducible as two binary pins, one of which (OPA) cannot carry a
  reproducible-build attestation (§4.1).
- Study 015 — not 012 — is the nearest precedent in *shape* (pinned external system, adapter
  layer, execution); its 12-round review record is cost evidence for §7. Studies 011/012 are the
  precedent in *kind* (authorship-rate studies) and govern the population and endpoint idioms.

## 1. The question

**Within the registered JPS-expressible policy fragment, does a constrained judgment
representation (JPS) change how reliably a model authors an executable policy — compared with
raw Rego (floor) and with Rego plus a prescribed judgment convention (the live alternative)?**

The scope qualifier lives inside the question, not in a footnote: the contest policy is selected
on arm A's expressive envelope (§2.1), and the program's own record (Study 003: 12/12 surveyed
real decisions escape the pack; ADR-0001: "the format cannot compute") says that envelope does
not cover real business decisions in general. No result of this study licenses a claim at the
advisory note's full generality. What the constraint *costs* is measured separately (§2.1).

## 2. Corrections to the advisory note (verified against source, 2026-08-14)

### 2.1 The proposed benchmark is not expressible in JPS — on its output side

Input side: fully expressible (numeric thresholds as decimal strings; all four ordered
operators, so inclusive/exclusive boundaries are exact; tri-state evidence as a first-class
third input document; required evidence; exceptions with suppress-rule / force-outcome /
escalate; per-rule `onUnknown`; unresolved outcomes with a closed reason vocabulary). Output
side, feature by feature with §8.3 cited per row in the census document:

| Proposed output            | JPS 0.2.0-draft                                                        |
|----------------------------|------------------------------------------------------------------------|
| disposition (4 values)     | PARTIAL — outcome cardinality is unbounded, but UNRESOLVED is a distinct disposition *kind*; §8.3 forbids mapping it onto an outcome |
| approved spend (numeric)   | NO — no arithmetic anywhere in Core; the disposition carries `kind` + `outcomeId` only |
| review level (2nd channel) | PARTIAL — `handoff.state` ∈ {requested, none} is a genuine second channel, but it means "escalation requested", not an arbitrary label; anything richer needs outcome-id products |
| reason codes (authored)    | NO — `reasons` is a closed six-value spec vocabulary, empty iff kind is `outcome` |
| unresolved evidence (list) | ABSENT — spec permits ids outside the disposition; this runtime discards them |

Scoring these cells head-to-head would make JPS fail **by construction** and call it author
error. One row's status is time-qualified: **numeric outputs are a maintainer roadmap item
(stated 2026-08-14) for a later JPS version** — the census records it as "not in 0.2.0-draft,
planned", distinct from deliberate Core refusals, and each census row states which of the two
it is. The study measures the *pinned* spec version regardless; and as a registered design
rule, a spec change landing before the freeze does **not** silently expand the contest
fragment — expanding it re-opens the design and its review (a fragment widened mid-design to
meet a benchmark cell would read as the spec being tuned against the study). The enriched
output side belongs to a follow-up against the version that ships it.

Design consequence — the benchmark splits:

- **The contest policy** (head-to-head fidelity): confined to the JPS-expressible fragment,
  sized to escape the ceiling that saturated 011 (49/49) and 012 (all arms HIGH). The fragment
  is chosen by arm A's expressiveness boundary and by no other criterion; that selection is a
  registered construct-validity limit (§9), and the fidelity population it defines is why R1's
  claim carries the scope qualifier inside it.
- **An expressiveness census** (descriptive, never adjudicated): the full vendor-approval
  policy, feature by feature, each cell citing spec clauses. A **joint-reading prohibition** is
  registered in §9, repeated in the census document, and pinned as a CORRECTION.md target:
  no fidelity number in this study speaks to the outputs the census marks inexpressible, and no
  tradeoff statement combining the two instruments is licensed. (012's retraction is the cost of
  letting a descriptive census acquire a comparative reading.)

### 2.2 The mutation-resistance story the note imagines does not exist in JPS tooling

Verified empirically against a binary built from runtime main: ADR-0023's derived boundary
probes carry **no expectations** (three string fields; the operator is deliberately excluded
from probe identity). Mutating `greater-than-or-equal "70"` to `greater-than` produced a
character-identical `covered` line for the correct pack and the mutant; detection came 100% from
the authored matrix row, and deleting that row left the mutant **passing with exit 0**. Probes
never move status, summary, or exit code. `packs suggest` (ADR-0024) withholds expectations by
design (its refused option E is "the circular oracle, stated plainly").

Consequence: in both systems, mutation kill comes from *authored* expectations. The mutation
endpoint (E4, §5) measures whether the representation leads authors to write tests that pin the
semantics — with the identity control and naming contract that make that measurable (§5),
neither of which v1 had. Coverage probes are excluded from the instrument list: they look like
tests, they name exactly the defect class this study cares about, and they detect nothing.

### 2.3 "Same policy, same gold suite" hides registered asymmetries — kept in a ledger

- **Facts shape.** JPS §7.4 defines ordered comparisons over decimal *strings*; a JSON number
  yields `unknown` (verified). Rego compares native numbers. The canonical grid is authored as
  **decimal strings** with a registered fixed scale per numeric field (string→number is total
  and lossless; number→string is where decimal identity dies — `"70.10"` must never round-trip
  to `"70.1"`). The Rego projection is `to_number` over those exact bytes, with a freeze-time
  round-trip assertion over the full grid (project → re-serialize → byte-equal, exit nonzero
  otherwise). The gold suite is authored against the canonical form only.
- **Outcome alignment, split by sort.** Two axes, not one flat domain:
  - *Run-level* (admission): admitted / refused-at-load — jpack pack-level §8.4 refusals and
    `opa check` failures alike. These are authoring outcomes (§5 E2), never silent exclusions.
  - *Row-level* (adjudication): APPROVE / REVIEW / REJECT / UNRESOLVED(reason-set) /
    ROW-ERROR(class). Rego's `eval_conflict_error` and any per-input runtime error are
    ROW-ERROR — a row failure against gold, the same treatment `unresolved:conflict` gets in
    arm A. The scorer asserts in code that no row-level error can remove a run from the E1
    denominator. The map is registered cell by cell with a worked conflict-row example in all
    three arms.
- **The asymmetry ledger (registered, pre-freeze).** Every construct in the contest policy where
  one representation supplies engine behavior the other must hand-author, with direction:
  A-favorable — engine-supplied conflict detection (two true rules → `unresolved:conflict`);
  the §8.2 evidence document's tri-state semantics ("omitted key = unknown").
  B/C-favorable — `else`/`default` give ordered precedence for free while Core forbids rule
  priority, so arm A hand-writes a negation cascade (counted as a covariate); native numerics.
  A registered balance criterion over the ledger, or the imbalance stated as a non-claim
  bounding R1. E3 failure categories that are structurally arm-specific (e.g.
  evidence-mechanism confusion exists only where two mechanisms exist) are marked
  within-arm-only **in the scorer**, and cross-arm comparison on them is refused in code.
- **Endpoint scope rule (one rule, applied consistently).** Endpoints score the §8.3 portable
  disposition under the alignment map — nothing outside it. This excludes `trace[]` (v1 already
  did) and **also** `expectedHandoffTarget`/escalation-target content from E1 and E4 (v1 did
  not; the target is outside the portable disposition by §8.3 and ADR-0025's own reasoning, and
  it has no Rego counterpart to align). The contest policy still exercises escalation; the
  target is reported descriptively.

## 3. Arms

| Arm | Representation | Prompt = shared header + arm suffix |
|-----|----------------|-------------------------------------|
| A   | JPS pack + test matrix (matrixVersion 2) | JPS reference excerpt + pack/matrix instructions |
| B   | Rego v1 + opa tests, **informal contract** | Rego reference excerpt + B's prose contract |
| C   | Rego v1 + opa tests + **prescribed judgment convention** | Rego reference excerpt + C's contract + convention |

- **Shared header** (byte-identical across arms): the contest policy prose **and the naming
  appendix** — outcome-id vocabulary, fact pointer paths, evidence-requirement ids, and the Rego
  package path + entrypoint rule name. Names are not the treatment, and pinning them is what
  makes E4 measurable and the artifacts bindable to the references.
- **Arm C is the honest "strongest alternative"**: not a result schema alone but a small
  prescribed judgment convention — the result contract (JSON Schema) **plus** conventions for
  mutual exclusion/precedence discipline and an explicit unresolved/conflict result. v1 withheld
  exactly the contested mechanism from C while calling it the existential rival; that read as
  motivated. **Decided 2026-08-14: full convention.**
- **Arm B's prose contract is a first-class freeze artifact**: produced by a registered
  mechanical de-formalization of C's JSON Schema (same field/value inventory, machine-checkable
  structure stripped), own digest. B and C then differ in *formality only*, which is the
  registered reading of the B-vs-C contrast. An E2 code `output-shape-unreadable` (distinct from
  static-check failures) covers B runs that check clean but emit unreadable shapes; the shape
  canonicalizer is a closed, pre-frozen set of accepted shapes, never amended after pilots.
- **System boundary rule, stated once and applied to all arms**: in-system = anything the pinned
  binary does at evaluation time; out-of-system = anything requiring an authoring loop. So
  engine-supplied semantics count (both directions — see ledger), and `packs test`/`packs
  suggest`/`opa fmt` iteration loops are all out. §9 states plainly that this study measures
  **single-shot authorship**, not tooled authoring workflows; no outcome here is evidence about
  the tooled-authoring question, which is the registered follow-up.
- Authoring is single-shot, no tools, no repair (the program's compilers do no repair of any
  kind). Artifact extraction from the completion is deterministic and registered (fenced-block
  rule). Prompt-iteration during design is governed by a **symmetric, disclosed iteration
  budget** across arms (001 §8 verbatim).
- **Excerpt parity is a sufficiency criterion, not a size criterion**: every language construct
  used by that arm's frozen reference implementation must appear in that arm's excerpt, and the
  reference may use no construct absent from the excerpt — asserted by a freeze test. The Rego
  excerpt is derived by a registered rule from the official OPA docs at a pinned commit (named
  pages in full, not maintainer-curated slices); the cross-vendor reviewer holds an explicit
  veto over both excerpts, recorded as a review round.
- Authoring toolchain: the program's standing pinned stack (012's codex pins as the default;
  re-pin at design time). One model; single-model ceiling in §9.

## 4. Apparatus

### 4.1 Engines, pinned
- **jpack**: current release (v0.17.0 line) pinned in the 013 shape (releaseTag, releaseAsset,
  archiveSha256 vs checksums.txt, binarySha256, reproducible-build attestation — jpack supports
  it). The PATH binary is v0.10.0 and predates ADR-0023/24/25; the harness refuses on digest
  mismatch (010's fail-closed pattern). **Verdicts and error classes are read from the JSON
  payload only.** Exit codes serve one purpose: separating "the invocation itself failed"
  (invocation/IO/internal = 3/4/5 — harness-error terminal, outside the drop-code table) from
  "the evaluator answered" (0/1/2). E2's ordered drop-code table is registered over the **four
  Core §8.4 classes** (pack-not-conformant, malformed-input, unsupported-required-extension,
  resource-exhaustion, in their fixed evaluation order) plus documented implementation-defined
  classes. Harness runs outside any jpack.json declaring an `audit` member.
- **OPA**: current stable 1.x pinned as `opa_linux_amd64_static` + published per-asset sha256,
  version resolved from the release page at pin time. **No reproducible-build claim** (official
  builds embed timestamp/hostname); stated in the preregistration, not left for review. Rego v1
  pinned in prompt and command line; v0 emission is an authoring outcome with its own code.
  Capabilities file generated from the pinned binary with a registered denylist (clock, network,
  rand, uuid, opa.runtime, print/trace, tz-taking time forms, net.cidr_expand) + a **canary
  negative control** (`time.now_ns` policy must be refused) so the gate is shown to have power.
  `--strict`, `--strict-builtin-errors`, `--fail`, `--timeout`, `env -i` + `TZ=UTC`, per-run
  exclusive directories. Score on error codes, never message prose; `opa test` JSON normalized
  (strip `duration`, sort by package/name). Verify empirically at pin time: exact exit-code
  behavior, whether `opa exec` accepts `--capabilities`, checksum artifact shape.

### 4.2 The contest policy and its calibration
Vendor-approval domain, JPS-expressible fragment: three outcomes + unresolved semantics;
~8–12 rules over risk score, requested spend, country risk, sanctions status (fact strings) and
financial evidence (the §8.2 evidence document); 4–6 numeric thresholds with mixed
inclusive/exclusive boundaries; 2–3 exceptions exercising all three effects; precedence via
mutual exclusion (negation count = registered covariate); `fallbackOutcome` absent over part of
the space so `no-match` is reachable; escalation present (target scored descriptively only, per
the §2.3 scope rule). Both tri-state mechanisms present, semantics stated exactly in prose;
the asymmetry ledger records that confusing them is only possible in arm A.

**Ordering and contamination control** (v1 contradicted itself here):
1. Draft prose → ambiguity audit (§4.3) → **author gold v0, every row citing its governing
   clause(s)** → freeze the ambiguity stratum → only then run calibration pilots.
2. Calibration pilots (labelled, non-citable, all arms) tune difficulty. Edits to the prose are
   allowed only where a mechanical check shows no unchanged gold row cites an edited clause;
   an edited clause forces re-derivation of its dependent rows with a recorded diff.
3. Every piloted-and-discarded candidate policy is published with its pilot rates; the frozen
   policy's own pilot rate is registered as not an estimate of anything.
4. The calibration target is stated in terms of the region where the **difference endpoints are
   decidable** (no arm saturated at 0 or 1), not in terms of one arm's mid-range band — v1's
   target contradicted its own primary claim. The stopping rule is registered.

### 4.3 The gold suite (the oracle)
- Maintainer-authored from the prose alone, per the ordering above; every row cites clauses
  (derive-scope-don't-enumerate).
- **Clean-room second oracle, bound to `CLEAN-ROOM-PROTOCOL.md` by name**: implemented from the
  POLICY.md bytes and nothing else, by a **different vendor from the arms' authoring stack —
  hard requirement, not an option** (a shared misreading between oracle and artifacts produces
  perfect agreement and is invisible; same-vendor doubles that risk). Deliverables the protocol
  demands: room brief, numbered DECISIONS.md for every underdetermined reading, transcript
  audit recorded in the import commit, void-on-violation rule. Ceiling stated: isolation is a
  process claim, not a proof.
- **Disagreement disposition, not a zero-disagreement gate** (v1's gate would have forced
  reconciliation until the independent reader rubber-stamped the maintainer): every divergence
  is retained verbatim with the builder's notes, adjudicated in writing against cited prose
  clauses, adjudication published. A divergence the prose cannot settle routes its rows to the
  ambiguity stratum automatically.
- **Ambiguity stratum membership is mechanical**, not declared: a row enters iff the two
  oracles disagree on it or the clean-room DECISIONS.md flags its governing clause as
  undetermined by the text. Frozen before any pilot artifact is opened; post-freeze additions
  are DEVIATIONS entries naming row and clause. E1 is published both with and without the
  stratum; the stratum's variance is registered as measuring interpretive spread, not error.
- **Adequacy gate**: the gold suite must kill 100% of the maintainer *adequacy* mutant set
  applied to the references; a surviving mutant blocks the freeze until a killing row is added.
- **No reviewer-holdout-gold stratum.** v1 imported 017/018's holdout convention; it does not
  transfer — there, the reviewer predicts the behavior of the thing under test; here, a
  reviewer gold row would be part of the *measuring instrument*, and one reviewer misreading
  would either abort the primary attempt (if gated) or sit unvalidated inside the oracle. The
  prospective content of an authorship-rate study is the post-freeze runs themselves (011/012
  precedent — neither had a holdout stratum; the preregistration says why in one sentence, and
  uses arm vocabulary, not strata vocabulary). Reviewer-authored prospective content lives in
  the **sealed reviewer mutant set** instead (§4.4), plus reviewer-vs-maintainer gold
  disagreement reported as an ambiguity diagnostic that can never move E1.

### 4.4 References and mutants
One correct reference implementation per language (maintainer-authored, verified against gold
and both oracles, frozen; conforming to the shared naming appendix). Two disjoint mutant sets:
- **Adequacy set** (maintainer-authored, executed pre-freeze, gates the freeze via §4.3).
- **Reviewer set** (cross-vendor reviewer-authored, sealed, first executed at the primary
  attempt, scored "as authored", reported separately, moves nothing).

**Pairing is an observable criterion, not an intent claim** (v1's "symmetric in intent" was
unfalsifiable and §2.3's own ledger refutes it): mutants M_A and M_B are *paired* iff the set of
gold-grid rows on which each disagrees with its own unmutated reference is identical under the
alignment map. Witness sets computed and published at freeze (011 DIVERSITY §I pattern).
Cross-arm E4 comparisons run over the paired subset only; unpaired mutants are used within-arm,
with the per-language unpairable count published as a finding: the representations do not have
the same defect space, and that is data, not noise.

## 5. Endpoints

**Population rule (the Study 001/011 lesson, enforced in code).** The denominator for every
per-arm rate is **attempted runs whose apparatus succeeded** (ITT-style). Apparatus/transport
failures (slot shape, call exit, golden-context mismatch, binary digest, transcript refusal)
are pipeline-invalid and excluded. Every failure attributable to what the author emitted —
unparseable artifact, schema-invalid pack, `opa check` failure, v0 syntax, no extractable
fenced block, unreadable output shape — is an **authoring outcome: valid, counted, scoring zero
gold agreement**. v1 routed these into pipeline-invalid, which both conditioned E1 on authoring
success and biased directionally in arm A's favor (the arm expected to fail validity most
often would have had its E1 inflated most). E1 and E2 are computed on the same denominator; a
harness test diffs the prose partition table against the scorer's code partition and against
every code `admit()` can return.

- **E1 (primary quantity): per-run perfect gold agreement** — the artifact agrees with gold on
  every adjudicated row (portable-disposition scope, alignment map), zero repair, ITT
  denominator. Reported per arm with exact Clopper–Pearson intervals.
- **Primary contrasts: registered difference endpoints, not band comparisons.** Exact
  two-proportion difference intervals for **A−B** and **A−C**, each with a registered minimum
  meaningful difference δ and an explicit **INDETERMINATE** verdict row (interval contains 0
  and is wider than δ) that licenses nothing and triggers nothing. v1's banded machinery is
  arithmetic nonsense for this endpoint shape at any feasible N (at N=30, HIGH ⇔ ≥27/30, so
  "same band" spans a 73-point observed gap, and the primary claim could flip on one run);
  012's cuts were derived for per-class rates and its own D-2 refused to inherit cuts across
  endpoint shapes. Multiplicity: hierarchical — A−B is tested first; A−C is interpreted
  confirmatorily only if A−B is decided.
- **E2: authoring-validity profile** per arm — the ordered code table over the §2.3 run-level
  axis (four Core §8.4 classes; opa check codes; v0-syntax; output-shape-unreadable), same
  denominator as E1, headline not footnote.
- **E3: row-level failure taxonomy** — pre-registered categories (boundary off-by-one,
  unknown-handling, evidence-mechanism confusion, precedence/exclusion, missing-rule,
  outcome-mapping, contract-shape); arm-structural categories marked within-arm-only in the
  scorer. Descriptive.
- **E4: run-authored test kill rate**, redefined (v1's version was uninterpretable in every
  arm): a run's suite is admitted to E4 only if it **passes its language's unmutated reference**
  (identity control — registered as a mutant-set member); a kill = passes reference AND fails
  the mutant. The per-arm identity-failure rate is its own published quantity. Cross-arm
  comparison over the paired mutant subset only. Portability is real because the shared naming
  appendix pins outcome ids, pointer paths, evidence ids, and the Rego package/entrypoint in
  all three arms.
- **E5: interpretive-spread census** — 012's registered census machinery: pairwise disagreement
  profiles across runs over the gold grid per arm; distinct structural encodings per clause
  ("20/20 passing" must not be one structure counted twenty times).
- Non-endpoints, with registered reasons: coverage probes (detect nothing — §2.2);
  `trace[]` and escalation-target content (outside the §8.3 portable disposition — one scope
  rule, applied consistently); repair count (no-repair discipline); LOC (census only).

**R1 (primary, retractable), difference form, scope inside the claim:**
*Within the registered JPS-expressible fragment, under single-shot authorship, arm A's per-run
perfect-gold-agreement rate exceeds arm B's: the exact A−B difference interval lies strictly
above 0, with the registered δ. An INDETERMINATE or unsupported outcome licenses neither
"constraint doesn't help" nor any A-vs-C conclusion.* (012's negation lesson, registered.)

**The A-vs-C contrast** is reported with the same machinery (difference interval, δ,
INDETERMINATE row). **No registered action table.** v1's D1 pre-committed program strategy
("open the OPA-profile ADR", "program-level review") to banded verdicts — the program has no
precedent for registering *actions*, an action table cannot be falsified, and at feasible N the
registered strategy could flip on one run. What each outcome would mean for the program moves to
a clearly-labelled, non-registered discussion section ("What we would do with each outcome"),
and the only registered commitment is the 017-§10 kind: **all rates, all arms, published
whichever way they land**, with CORRECTION.md targets pinned pre-freeze.

**N and power — decided 2026-08-14: N=50/arm** (150 calls — exactly 012's batch scale), R1
confirmatory as stated, with δ sized to what that N actually delivers (roughly 25-point gaps at
conventional power; the working assumption A≈0.9 vs B≈0.7 sits at the edge of resolvability and
the preregistration says so). The registered δ and the full operating-characteristic table are
published in the preregistration (012 §5.4 pattern) so the claim's coarseness is stated, not
left to a reader's intuition.

## 6. Registered threats

- **Training-prevalence confound — measured, not assumed.** v1 registered an asymmetric reading
  rule ("A win is strong evidence; a Rego win is ambiguous") on an *asserted* gradient
  direction. The direction is genuinely unestablished: public-corpus mass favors Rego, but at
  least three mechanisms run the other way — the JPS excerpt can be a near-complete in-context
  contract for a small language while any Rego excerpt is a fragment of a large one; arm A's
  artifact is schema-validated JSON, a shape models are massively trained on, while Rego v1
  syntax is idiosyncratic; and prompt, prose, gold, and reference all issue from one author's
  idiom in arm A. A heads-I-win-tails-you-tie rule will not survive review. Instead:
  (1) a pre-freeze, labelled, non-citable **external calibration**: the pinned model against a
  published Rego authoring task with published figures (001 §8: a materially sub-published
  baseline means a harness/prompt bug, not a finding); (2) unless a gradient is measured, the
  registered reading is: **no direction of this result separates representation from
  familiarity; both directions are reported as confounded**; (3) the fourth-arm instrument — a
  **high-prevalence constrained representation** (JSON Logic / DMN-shaped decision table with a
  pinned engine), which holds constraint fixed while flipping prevalence, the actual contrast —
  is **deferred to a registered follow-up (decided 2026-08-14)**; a synthetic DSL confounds
  constraint with novelty and costs more.
- **Ceiling** (§4.2 calibration; the most likely uninformative outcome per 011/012).
- **Home-field selection** (§1, §2.1): the fidelity population is arm A's envelope; named in §9.
- **Memorization/overfit**: gold rows never appear in any prompt; a structural check over
  `opa parse --format json` for grid-shaped enumeration, descriptive.
- **Oracle circularity**: doubled here (one oracle, two target languages); §4.3 mitigations;
  ceilings stated.
- **Executing model-authored code** (new risk class for the program — 012 validated JSON, never
  ran generated code): capabilities file + canary, timeout, memory bound, exclusive scratch,
  `env -i`; registered as the study's largest operational novelty.
- **Excerpt authorship by the interested party**: §3's sufficiency criterion + registered
  derivation rule for the Rego excerpt + reviewer veto round.

## 7. Process plan

Canonical document set per 016/017 (fully spelled-out §5–§8 **plus** `## The freeze and the
primary attempt` with the literal governing invocation — not 018's compressed form, per the
frozen-reader standard): README, PREREGISTRATION, PREREG-REVIEW, DEVIATIONS, `policy/SPEC.md`,
harness/ (PINS.json with linear anchor order and REGISTERED-vs-PILOT label rule; canonical
grid; gold; mutant sets; STUDY-MANIFEST scoped per **ADR 0004** — DEVIATIONS.md and README.md
excluded by named constant with an asserting test, the 014 `REGISTERED_DOCUMENTS`/
`EXCLUDED_DOCUMENTS` shape), `upstream/` (OPA license + pin record), pilots/ (non-citable,
NOTE.md), results/primary-attempt-001 absent at freeze; first invocation of the governing
command is the primary attempt, crash and all. Cross-vendor review to `freezable as written`
(plan for 7–12+ rounds including a deliberate frozen-reader audit round and a
safeguards-that-cannot-fail round; every disposition asserting a safeguard cites the test that
enforces it). Runs sequential, never parallel; batch within one UTC day (crossing midnight is a
DEVIATIONS entry); golden-context capture with two agreeing probes + isolation negative control
under recorded operator assent.

**Budget, itemized (012's own review caught the omission v1 repeated):** 3N authoring calls
+ 2 golden probes + 1 isolation negative + calibration-pilot calls (counted, labelled) + the
clean-room oracle build (different vendor). Per-call time: 012's mean was 42.4 s for a
*transcription* task; 019 asks for a full policy + test suite per completion, so assume
90–180 s/call and check the one-UTC-day rule at the top of the range (N=50/arm: 150 calls ≈
4–7.5 h — fits; N=100/arm needs the two-day registration). Grading compute is separate and
first-class: runs × grid × 2 engines + admitted suites × mutants, per-run exclusive scratch;
disk = transcripts (~75 KB/slot) **plus** per-run artifacts and grading outputs. Read Study
015's open blocker set as cost evidence for the execution/adapter layer; 012 alone
under-predicts it.

**Reuse** (port by digest, PORTS.md two-sided table): 012's `authoring_call.sh`, `batch.py`
(schedule re-derived for 3 arms, balance re-tested), `integrity.py`, `transcript_check.py`,
`arm_assembly.py`, census machinery, `score_rates.py` skeleton (admit + ordered codes +
exact intervals + terminality); 010/013 PINS shapes; repo-root `agreement_harness.py` structure
for the two-engine loop; 001's `backends.py` for the second-vendor oracle build (now required,
not optional).

**New builds**: per-language admission layer (ordered drop codes, no repair); two-engine
execution layer; alignment map (two axes); mutant generator + witness-set computation + kill
scorer with identity control; C's convention document + JSON Schema; B's mechanical
de-formalization; OPA capabilities tooling + canary; asymmetry ledger.

## 8. Decisions

**Decided 2026-08-14 (maintainer):**
1. **N = 50/arm**, confirmatory registration at the δ that N delivers (§5).
2. **Arm C = full judgment convention** (§3).
3. **Fourth arm deferred** to a registered follow-up (§6).

**Still open (defaults will be taken at prereg time unless the maintainer objects):**
4. **Authoring toolchain**: default — continue the standing codex pin (continuity with the
   011/012 baselines); re-opening the model choice breaks baseline comparability.
5. **ADR 0004 promotion** from `proposed` to `accepted` as part of 019's landing (default: yes,
   proposed in the landing PR).
6. **Scope split** (§2.1) is treated as settled by this brief unless challenged in review: the
   cartesian outcome-id alternative multiplies rules and makes the artifacts non-comparable.

## 9. What this study cannot show

Fidelity is measured **within the JPS-expressible fragment, selected by arm A's expressive
envelope and no other criterion** — the program's own census (Study 003: 12/12 real decisions
escape the pack) says this fragment does not cover real business decisions; no result here
generalizes to "evidence-driven business judgments" at large. Single-shot authorship only: no
outcome is evidence about tooled authoring workflows (`packs test`/`suggest`, `opa` loops) —
that is the registered follow-up. One model, one day, one policy family, one prompt per arm.
Unless the prevalence gradient is measured (§6), no direction of the result separates
representation from training familiarity. The joint-reading prohibition (§2.1): no tradeoff
statement combining the census and the fidelity rates is licensed. An INDETERMINATE or
unsupported contrast licenses no negation. The gold suite is two authors deep, not independent
of the program. The census describes spec 0.2.0-draft as pinned: gaps recorded as roadmap items
(numeric outputs) are statements about the pinned version, not about JPS's future, and are not
scored. Nothing here measures whether any policy or fact is true — the standing ceiling — and
nothing claims JPS conformance.
