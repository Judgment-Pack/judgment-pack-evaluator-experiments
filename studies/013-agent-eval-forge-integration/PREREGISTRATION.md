# Preregistration — Study 013: the judgment/integration boundary under an external regression harness

**Status: DRAFT. Not frozen. Governs nothing yet.** Per repository convention
this document becomes governing when frozen by merge after cross-vendor
adversarial review (PREREG-REVIEW.md will hold the rounds and dispositions).
Everything executed before the freeze is pilot work, retained under `pilots/`
and citable only as harness validation. This draft is written with the pilot
machinery already built and exercised; the freeze re-runs everything from the
pinned state and the first post-freeze attempt is primary even if it crashes.

## 1. Research questions and the retractable proposition

**RQ1 (primary, deterministic).** For each registered fault in
`scenarios/mutations/MATRIX.json` — six judgment-semantic pack mutations, nine
integration mutations, one version-staleness mutation — which detection layers
catch it: **J** (the judgment layer's own tooling: `jpack packs test` on the
study's 21-row instance matrix, or a pinned-evaluator refusal), **F** (Agent
Eval Forge's deterministic scorers at commit `8925cac`, reached through the
study driver, detection counted at metric level), **G** (the study gate:
disposition-vs-golden diff, action-vs-expectation diff, integrity refusals)?

**R1 — the registered proposition, stated to be retractable:** the observed
detected-by sets match the registered expectations in MATRIX.json exactly —
in particular, (a) every judgment-semantic mutation is caught by J without any
integration machinery involved; (b) no integration mutation is caught by J;
(c) every mutation that lets a protected action fire against a non-actionable
disposition is caught by F through blocking scorers; and (d) the three cells
registered as invisible to every layer (m02/f01, m08/t04, m08/t08) stay
invisible. Any divergence in any direction falsifies R1 as stated and is
reported as the result.

**RQ2 (secondary, descriptive, already fixed by authorship).** The
applicability census of the 28 upstream scenarios (CLASSIFICATION.md):
0 applicable / 12 integration_only / 14 not_applicable / 2 uncertain. The
registered claim is only that the census was produced before any run and that
no upstream scenario was rewritten to change its category.

**RQ3 (gated, paid, not part of the deterministic freeze).** With a real model
as the Arm A decider (policy prose + facts in context) against Arm B (the
pinned evaluator) on the same 21 cases, same fixtures, same scorers: final
decision accuracy, false-approval count, correct-abstention and correct-handoff
counts, per-arm. This phase runs only after the freeze AND explicit maintainer
approval of the spend, with its own registered analysis added by amendment
BEFORE any model call. Until then this study makes no claim in RQ3's direction,
and the scripted-decider pilots must not be quoted as evidence about models.

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
- Full pin registry: `harness/PINS.json`. Both pilot-phase caveats recorded in
  pilot-01 are resolved in pilot-02: the evaluator is the released v0.16.0
  linux_amd64 binary, archive verified against the release `checksums.txt` —
  and a local build from the tag reproduced the identical binary digest, which
  is recorded as evidence the build is reproducible; harness scripts run under
  CPython 3.12.11 (Study 011's interpreter). Pilot-01 is retained under its
  original toolchain; both pilot batches produced identical endpoints.

## 4. Procedure (deterministic phase)

1. `integrity.py` — refuse on any pin drift.
2. Arms: arm_b, arm_a_oracle, arm_a_adversary over all 21 cohort-2 scenarios.
3. Mutations: one run per MATRIX entry, tag-scoped, one mutation at a time;
   judgment-semantic mutations evaluate mutated pack bytes through the
   unmutated shell; integration mutations evaluate pristine packs through a
   single flipped hook; m15a evaluates a byte-frozen pack re-declared under
   `0.1.0-draft`.
4. J-layer: `jpack packs test` on the pristine project (must pass 21/21) and
   on a temp project per pack mutation (failing row ids = J detections).
5. Cohort 1: both upstream packs, unchanged, under `upstream_baseline`;
   endpoint is integration validation only (all artifacts complete, zero
   scorer errors), never scenario pass rates.
6. `repeat_check.py`: three fresh Arm B runs; the retained evaluator output
   bytes and the structured actions must be identical across runs.
7. `gate.py` adjudication writes `ADJUDICATION.json`; the run is analyzed
   intent-to-treat: every scheduled case appears, pipeline-invalid states are
   counted and never silently excluded.

## 5. Decision rule for R1 (ordered, exhaustive)

1. Any integrity refusal, incomplete artifact, or scorer error in a registered
   run → that run is **pipeline-invalid**; rerun only by recorded deviation.
2. Otherwise, if `ADJUDICATION.json` has zero divergences → **R1 holds**.
3. Otherwise → **R1 falsified**; the divergence list is the result, reported
   per layer and per case, with no post-hoc reclassification of MATRIX.json.

## 6. What this study cannot show

No efficacy (Study 001's negative result stands; scripted deciders say nothing
about models). No JPS conformance under §3.4 (the corpus and claims machinery
are not engaged). No claim about Agent Eval Forge's overall quality beyond the
defects and behaviors actually measured (UPSTREAM.md). No caller obligation
under JPS Core (I1 is study-defined). No statistical independence of upstream
scenarios (single-author, single-drop provenance recorded). No generalization
beyond: these six packs, these 21 cases, this mutation family, one machine,
one Forge commit, one evaluator build.

## 7. Deviations

None yet. Departures land in DEVIATIONS.md and never edit this file after
freeze.
