# Analysis — the registered primary attempt

Primary attempt `results/primary-attempt-001`, executed from the freeze
commit `c4cfb3fe` (the squash-merge of PR #46) by the governing invocation,
`--include-holdout`, under the pinned toolchain. Machine-readable result:
`RESULTS.json`. Verdict under the frozen decision rule, §5 step 2:
**"R1 holds" — in both strata.**

## What this result does not establish

No model or operational efficacy: no model made any decision anywhere in this
study, and Study 001's negative efficacy result stands untouched. No JPS
conformance under §3.4. No detection rates, sensitivity, or coverage beyond
the twenty registered mutations and 125 adjudicated cells. No independent
corroboration from F+G agreement (shared-source concordance, §2 disclosure).
No probe-diversity or detection-power claim from the 009/010 defect-family
lineage. The replication stratum is exactly what §1 says it is: a locked
replication of an endpoint already observed in five pre-freeze pilots, now
reproduced once under the frozen protocol.

## The result

Pipeline validity: 31/31 rows valid — integrity, per-run scheduled-set
equality for artifacts and scores, completeness, driver-exit consistency, the
exact registered cohort-1 judge-unscored pairs, three byte-identical Arm B
repeats, the pristine-Arm-B precondition, and the pristine 21/21 instance
matrix. Provenance stamped and equal to the pins.

- **Replication stratum (16 maintainer-authored mutations, 118 cells):
  118/118 adjudicated, 0 divergences.** Every judgment-semantic mutation was
  caught by the judgment layer's own tooling; no integration mutation was;
  every protected-action firing was caught by a blocking scorer; the three
  projection-masked cells stayed masked.
- **Holdout stratum (4 reviewer-authored mutations, 7 cells, first-ever
  execution): 7/7 adjudicated, 0 divergences from the reviewer's own
  registered expectations.**

## The holdout stratum, cell by cell

- **h01 (exception predicate miswired, `flagged` → `ready`):** d01 flipped
  from approve/execute to a direct escalation with no Core destination —
  caught by all three layers, exactly as registered; d02 and d03 stayed
  superficially correct, and every layer correctly stayed silent.
- **h02 (handoff target corrupted; the reviewer's deliberate layer-model
  challenge):** the disposition stayed `conflict/requested`; only the
  configured destination changed. The judgment layer's instance matrix —
  which projects kind, reasons, and handoff state, but not the target —
  **could not see it (J false), and that was the registered expectation,
  authored adversarially by the reviewer before execution.** Forge's
  `argument_correctness` (the corrupted target reaches the `open_review`
  arguments) and the gate's golden diff both caught it. The registered layer
  model survived the probe designed to break it, and the probe documents a
  real projection limit of the matrix surface: **an instance matrix that
  does not project the handoff target cannot regression-test the handoff
  target.**
- **h03 (force-outcome exception disabled):** a protected false approval on
  a pack absent from the original mutation set — caught by the **blocking**
  scorer, satisfying the reviewer's `F_requires_blocking` registration, and
  by J and G.
- **h04 (negative control: outcome of an unconditionally suppressed rule
  changed):** valid-but-unreachable authored bytes. No layer fired — the
  registered expectation. No layer manufactures a detection out of a change
  that cannot alter any disposition.

## What the study, now complete on its deterministic claims, adds up to

An independently developed agent-regression harness, pinned and unmodified,
can distinguish failures inside the deterministic judgment contract from
failures in the surrounding integration — on these twenty mutations, under
this study's integration contract, with the layer attribution adjudicated
per cell and the boundary's known blind spots registered in advance and
confirmed (three projection-masked replication cells; the h02 matrix
projection limit). The applicability census stands as a pre-specified author
judgment: none of the 28 upstream scenarios contains a judgment question;
the census was not adjudicated and the upstream suite served as a smoke
test of the pinned substrate only.

## Follow-ups

- The h02 projection limit is CLOSED upstream: runtime ADR-0025 ("assert
  the handoff target in the matrix", runtime PR #104, merged) adds an
  optional `expectedHandoffTarget` assertion to packs-test matrix rows
  (matrix v2), after a ten-round cross-vendor review recorded on that PR.
  RQ3's f05 finding (the configured destination degrading through prose)
  independently motivated the same fix.
- RQ3 was subsequently executed under its registered amendment
  (AMENDMENT-RQ3.md; ANALYSIS-RQ3.md): 62/63 agreement, 0/63 false
  approvals; both divergences on pre-registered cells. Nothing in THIS
  analysis depends on it, and its non-claims are its own.
