# Preregistration — Study 013: the judgment/integration boundary under an external regression harness

**Status: DRAFT. Not frozen. Governs nothing yet.** Per repository convention
this document becomes governing when frozen by merge after cross-vendor
adversarial review (PREREG-REVIEW.md will hold the rounds and dispositions).
Everything executed before the freeze is pilot work, retained under `pilots/`
and citable only as harness validation. This draft is written with the pilot
machinery already built and exercised; the freeze re-runs everything from the
pinned state and the first post-freeze attempt is primary even if it crashes.

## 1. Research questions and the retractable proposition

**RQ1 (primary, deterministic).** For each registered fault — the sixteen
maintainer-authored cells in `scenarios/mutations/MATRIX.json` (six
judgment-semantic pack mutations, nine integration mutations, one
version-staleness mutation) plus the four reviewer-authored holdout cells in
`scenarios/mutations/MATRIX-HOLDOUT.json` — which detection layers catch it:
**J** (the judgment layer's own tooling: `jpack packs test` on the study's
21-row instance matrix, or a pinned-evaluator refusal recorded in the
artifact), **F** (Agent Eval Forge's deterministic scorers at commit
`8925cac`, reached through the study driver, detection counted at metric
level, blocking-filtered where registered), **G** (the study gate:
disposition-vs-golden diff and action-vs-expectation diff on completed
artifacts — integrity and completeness are a separate global validity
channel, never a G detection)?

**Two epistemic strata, reported separately under one validity result:**
the sixteen original cells are a **locked replication** (piloted pre-freeze;
see "Epistemic status" below); the four holdout cells (h01–h04) are
**prospective**: authored by the round-2 cross-vendor reviewer with the
reviewer's own registered expectations, committed verbatim with attribution,
never executed before the freeze (the gate mechanically refuses
`--include-holdout` while this document is a DRAFT), and first executed in
the post-freeze registered run.

**R1 — the registered proposition, stated to be retractable:** for every
adjudicated cell, the observed detected-by set equals the per-cell registered
expectation in MATRIX.json and MATRIX-HOLDOUT.json. **The per-cell
registrations govern; the tendencies below are descriptive summaries only and
are deliberately NOT universal claims** — the reviewer-authored h02
(judgment-semantic, registered J-false because the instance matrix does not
project the handoff target) and h04 (negative control: unreachable authored
bytes, registered undetected everywhere) are registered exceptions that the
blanket forms would misstate. Descriptive tendencies: (a) judgment-semantic
mutations are typically caught by J with no integration machinery involved;
(b) no integration mutation is caught by J; (c) every cell where a protected
action fires against a non-actionable disposition is caught by F through a
BLOCKING scorer, adjudicated by the blocking flag on the failed metric
(`F_requires_blocking` cells) with both the unfiltered and counted metric
lists retained; (d) the three cells registered as masked under the
disposition/action projection (m02/f01, m08/t04, m08/t08) stay masked — their
raw evaluator traces differ from the golden traces and are retained; the
masking is a property of the registered projection, not a blind spot of the
artifacts. Any divergence from any per-cell registration, in any direction,
falsifies R1 as stated and is reported as the result; holdout divergences are
additionally reported in their own stratum.

**Epistemic status of the post-freeze run (registered honestly):** this exact
deterministic endpoint has already been observed in pre-freeze pilots on this
same fixed cell set, and MATRIX.json, this document, and the pilot artifacts
enter repository history together. The post-freeze registered run is therefore
a **locked replication under the frozen protocol and pinned toolchain**, not
fresh prospective discovery, and its result is claimed only as such. R1 is
fixed-cell signal concordance on a registered mutation set; it supports no
sensitivity, detection-rate, or coverage generalization beyond those cells.

**RQ2 (descriptive, a pre-specified author judgment).** The applicability
census of the 28 upstream scenarios (CLASSIFICATION.md): 0 applicable /
12 integration_only / 14 not_applicable / 2 uncertain. This is registered as
an author-judgment record, not an adjudicated empirical endpoint: its
chronology (authored before any run, categories never edited to fit results)
is recorded here and in CLASSIFICATION.md but is not independently
enforceable from repository history, since the census and the pilots first
enter history together. No upstream scenario was rewritten.

**RQ3 (gated, paid, not part of the deterministic freeze).** With a real model
as the Arm A decider (policy prose + facts in context) against Arm B (the
pinned evaluator) on the same 21 cases, same fixtures, same scorers:
**final-decision agreement with the pinned evaluator's disposition** (which
the goldens verified against the registered expected outcomes) — named as
agreement, not "accuracy," because the reference is the evaluator, not an
independent truth — plus false-approval, correct-abstention, and
correct-handoff counts per arm. This phase runs only after the freeze AND
explicit maintainer approval of the spend, with its own registered analysis
added by amendment BEFORE any model call. The amendment MUST pin: the model
and provider, the rendered policy-prose fixtures (by digest), sampling
parameters, SDK and retry policy, and the failure-handling rule — and it MUST
define an opaque-identifier mapping: the model decider receives an opaque,
non-answer-bearing case handle (never ids like `d01-approve` or caseType
labels like `9-exception-overrides-rule`, which are answer proxies), the
fetched facts and evidence availability, and the action map — never the
registered expectation or any golden. The expectation boundary is enforced in
agents/shell.py; the scripted oracle (which reads the registry by design) is
a disclosed tautological positive control, never a model stand-in. Until
the amendment lands, this study makes no claim in RQ3's direction, and the
scripted-decider pilots must not be quoted as evidence about models.

## 2. Arms and the integration contract

Both arms run the identical shell (`agents/shell.py`): fetch facts fixture →
fetch evidence-availability fixture → judgment stage → execution mapper →
action tool. The judgment stage is the only difference: Arm B calls the pinned
evaluator (`jpack experimental evaluate`, facts on stdin, evidence file only
when non-empty); Arm A calls a decider (offline: `oracle`, `adversary`;
gated phase: a model). The execution mapper is the study-defined integration
contract (JPS Core binds no caller):

1. `handoff.state == "requested"` → `open_review` (target from `handoffTarget`,
   else `"unspecified"`);
2. `kind == "outcome"` → the per-pack action map: `execute:<name>` →
   `execute_decision` (the protected tool) or `record` → `record_decision`;
3. otherwise → `record_decision` carrying kind and reasons (abstention);
4. an evaluation error is never a disposition and never an action: it records
   `kind: "error"` and abstains.

**Invariant I1:** the protected tool must not fire unless the disposition is an
outcome with handoff `none` whose action map says execute. Expressed in Forge
as `disallowed_tools` on every non-execute scenario (blocking scorer) plus the
study-registered `approval_boundary_adherence` scorer (blocking; also checks
claimed-vs-executed action). Registered scope limitation: for outcome+none
dispositions whose map says record, an override is caught by
`zero_disallowed_actions` and the trace scorers, not by the invariant scorer.

**Disclosure — what is and is not independent here.** The goldens are the
pinned evaluator's own output: a self-regression reference, not external
truth. The oracle decider reads the registered expectations by design: a
tautological positive control, nothing more. And F's trace expectations and
G's action expectations both derive from the same study-owned execution
mapper, so F+G agreement is shared-source concordance, not independent
corroboration. Agent Eval Forge contributes externally authored scoring
machinery and an externally authored scenario surface; it does not supply an
independent action oracle, and no claim in this study treats it as one.

## 3. Materials, all pinned

- Packs used unchanged (bytes from runtime v0.16.0, digests in
  `packs/MANIFEST.sha256`): data-request-intake-triage, decimal-threshold-fee,
  direct-exception-escalation, partial-trigger-conflict,
  exception-force-outcome, exception-suppress-rule.
- 21 cases (`scenarios/jps/cases.json`) covering the ten required case types
  (approval; hard stop; exact threshold — which for this corpus pack is a
  designed rule conflict; just-below/above; required evidence absent; evidence
  unknown; facts unknown; conflict with and without a configured trigger;
  direct exception escalation with no Core destination; exception force and
  suppress; not-applicable; JSON-number-vs-decimal-string).
- Goldens: the pinned evaluator's full output bytes per case
  (`goldens/`), with `EXPECT-CHECK.json` recording 21/21 agreement with the
  hand-derived expectations. The evaluator governs; the hand derivation is a
  registered prediction only.
- Upstream harness pinned at `8925cacc2abb26198e3cd74de3d1e916a719811e`
  (MIT), vendored scenario/fixture bytes under `upstream/`. Upstream code is
  never modified; the driver (`harness/run_forge.py`) uses its library layers
  and owns exit codes, completeness assertions, and scorer-error refusals.
- Reviewer-authored holdouts: `scenarios/mutations/MATRIX-HOLDOUT.json`,
  committed verbatim with attribution (round-2 cross-vendor reviewer);
  fixture bytes derive mechanically from the registered `mutation_spec`
  pointer edits (`harness/mutate_packs.py`), which is static generation —
  no evaluator, packs-test, Forge, or gate execution of h01–h04 may occur
  before the freeze, and `pilots/` must contain no h-cell artifact.
- Full pin registry: `harness/PINS.json`. Both pilot-phase caveats recorded in
  pilot-01 are resolved since pilot-02: the evaluator is the released v0.16.0
  linux_amd64 binary, archive verified against the release `checksums.txt` —
  and a local build from the tag reproduced the identical binary digest, which
  is recorded as evidence the build is reproducible; harness scripts run under
  CPython 3.12.11 (Study 011's interpreter). Three pilot batches are retained:
  pilot-01 (original toolchain), pilot-02 (final toolchain, pre-rework
  harness), pilot-03 (first batch under the round-1-reworked harness); all
  three produced identical endpoints on the sixteen original cells.

## 4. Procedure (deterministic phase — one orchestrated `gate.py` invocation)

`gate.py --pilot-root <nonexistent dir>` runs the entire batch and refuses a
pre-existing root: attempt directories are immutable, a rerun never reuses or
overwrites an earlier attempt's output, ATTEMPT.json marks the root before
anything else runs, and there is no partial-rerun mode. The three
protocol-facing verdict literals are defined once in gate.py and quoted
exactly in §5.

1. `integrity.py` — the FIRST recorded validity row (an integrity failure
   produces a terminal, recorded, pipeline-invalid adjudication — never a
   pre-record crash). It refuses on any pin drift: pack and upstream
   manifests, mandatory `JPACK_BIN` / `FORGE_VENV_PY` / `FORGE_CLONE`
   identities (binary digest; venv freeze byte-for-byte with its interpreter
   version; checkout at the pinned commit with a clean tree),
   jpack binary digest, Forge venv freeze (bytes retained in
   `harness/forge-freeze.txt`; the freeze line pins the editable install's
   commit), harness interpreter series, mutated packs byte-equal to a fresh
   temp-directory derivation, goldens agreement, and the 106-entry
   `STUDY-MANIFEST.sha256` over every causal study file.
2. Arms: arm_b, arm_a_oracle, arm_a_adversary over all 21 cohort-2 scenarios.
3. Mutations: one run per MATRIX entry, tag-scoped, one mutation at a time;
   judgment-semantic mutations evaluate mutated pack bytes through the
   unmutated shell; integration mutations evaluate pristine packs through a
   single flipped hook; m15a evaluates a byte-frozen pack re-declared under
   `0.1.0-draft` (registered refusal class `pack-not-conformant`, parsed from
   the evaluator's `evaluationError.class` and retained in the artifact).
4. J-layer: `jpack packs test` on the pristine project (must pass 21/21) and
   on a temp project per pack mutation (failing row ids = J detections);
   an artifact-recorded evaluator refusal is the second J source.
5. Cohort 1: both upstream packs, unchanged, under `upstream_baseline`. The
   endpoint is a **Forge load/run/artifact/score smoke test**, nothing wider:
   the artifact AND score sets must equal the exact upstream scenario id sets
   (20 + 8), every artifact completed, and the errored (scenario, metric)
   pairs must be exactly the declared judge metrics (the registered
   `JUDGE_METRICS` set in gate.py, including the two offline-dead hybrids)
   with the "judge not configured" error — zero deterministic scorer errors,
   zero silently unscored judge metrics, and scenario pass rates are not an
   endpoint.
6. Repeat check: EXACTLY three fresh Arm B runs (the cardinality is enforced
   in both repeat_check.py and the gate's validation of REPEAT.json), each
   required to contain the exact 21 scheduled, completed artifacts with an
   acceptable driver exit and zero scorer errors before digesting; retained
   evaluator output bytes and structured actions must be identical across
   runs.
7. Adjudication writes `ADJUDICATION.json` with two separated channels: a
   global VALIDITY section (per-run scheduled-set equality, completeness,
   scorer errors, driver-exit consistency — exit 4 iff safety violations,
   exits 3/5 always invalid — plus the pristine-Arm-B-clean-per-case
   precondition and the pristine packs test) and the per-mutation DETECTION
   section. Detection is adjudicated only against completed artifacts; a cell
   whose artifact is missing or incomplete is recorded NOT-ADJUDICATED —
   never a true or false detection — and completeness failures live in the
   validity channel, never as G detections. On `F_requires_blocking` cells
   the adjudication retains both the unfiltered failed-metric list and the
   blocking-counted list with each metric's {name, passed, blocking}, so the
   filter is auditable from the record. The attempt's provenance (evaluator
   digest, Forge commit, freeze digest, interpreter, PINS and manifest
   digests) is stamped into ADJUDICATION.json. Every scheduled case appears;
   nothing is silently excluded.

## 5. Decision rule for R1 (ordered, exhaustive)

1. If the primary post-freeze attempt is not pipeline-valid (any validity row
   fails, including the pristine precondition), the verdict is
   **"R1 inconclusive — pipeline-invalid"** and it is terminal for that
   attempt: every computable divergence is still reported descriptively, the
   attempt is retained unchanged, and no rerun replaces it. A rerun happens
   only by recorded deviation, in a new attempt directory, labeled
   non-primary.
2. Otherwise, if `ADJUDICATION.json` has zero divergences → **R1 holds**, as
   a locked replication under the frozen protocol (§1).
3. Otherwise → **R1 falsified**; the divergence list is the result, reported
   per layer and per case, with no post-hoc reclassification of MATRIX.json.

## 6. What this study cannot show

No model or operational efficacy (Study 001's negative result stands; scripted
deciders say nothing about models; R1 is fixed-cell signal concordance and
supports no sensitivity, detection-rate, or safety generalization). No JPS
conformance under §3.4 (the corpus and claims machinery are not engaged). No
claim about Agent Eval Forge's overall quality beyond the properties actually
measured (UPSTREAM.md). No independent corroboration from F+G agreement (§2
disclosure: shared-source concordance). No caller obligation under JPS Core
(I1 is study-defined). No statistical independence of upstream scenarios
(single-author, single-drop provenance recorded). No probe-diversity or
detection-power claim may ever be synthesized from the shared Study 009/010
defect-family lineage (standing non-claim, adopted from the round-1 review).
No generalization beyond: these six packs, these 21 cases, this mutation
family plus the four reviewer-authored holdout cells, one machine, one Forge
commit, one evaluator build.

## 7. Deviations

None yet. Departures land in DEVIATIONS.md and never edit this file after
freeze.
