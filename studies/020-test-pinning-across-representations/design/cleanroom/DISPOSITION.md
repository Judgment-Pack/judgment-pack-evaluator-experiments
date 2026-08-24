# Clean-room disposition (design draft, 2026-08-15)

## Runs of record

- Oracle vs gold suite: **76/76 agree** (2026-08-15); re-run **105/105** after the adequacy
  gate and **109/109** on 2026-08-18 after the X1 repair added four rows.
- Oracle vs the reference implementations over the full 2,540-cell design grid:
  **2,540/2,540 agree**. Script: `check_oracle.py`.
- **Update 2026-08-18 (round-1 R1-2).** X1 is retired
  (`reference/refA/PACK-CHANGE-001.md`); `check_oracle.py` now carries an **empty**
  registered-exclusion registry and exits nonzero on *any* divergence — no class of cell is
  excused. Re-run of record: **109 gold rows, 2,540 grid cells, 0 excused divergences, 0
  unexpected divergences.** Three of the four new gold rows live in the region the retired
  class forbade, and the oracle reproduced all four expectations on the first run, with the
  two pinned engines, without adjudication.
- **Zero divergences to dispose.** The disposition below therefore covers only the
  oracle's six numbered decisions, per the registered rule that a decision flagging a
  governing clause as underdetermined routes dependent rows to the ambiguity stratum
  unless the underdetermination is closed.

## Disposition of the decisions

- **D-1** (does a uniformly-escalating U1 sweep issue escalation or unknown?) —
  **Closed in prose (v0.3)**: U1 now defines the test over each assignment's *outcome*
  (determination, escalation, or an unresolved limb). Also noted: the underdetermined case
  is only reachable when O3 does not depend on the unreadable input, where the
  order-of-application sentence already settles it.
- **D-2** (interval decomposition for the spend sweep) — implementation technique, not a
  reading; differentially validated by the implementer; consistent with both references.
  **Recorded, no action.**
- **D-3** (O2 displaces D6b's enhanced-review and unreported-insurance limbs) — **Closed
  in prose (v0.3)**: O2 now says so in terms. The oracle's chosen reading matches both
  engines (force-outcome precedes rule evaluation).
- **D-4** (unresolved grounds are never unioned) — **judged text-determined**: U1 names a
  single ground ("unresolved as unknown") and worked examples 2 and 4 report one token
  with escalation present in the sweep. **Recorded, no edit.**
- **D-5** (no input validation) — matches the registered grid discipline (the canonical
  grid carries no malformed or out-of-range values, asserted at freeze). **Recorded.**
- **D-6** (the sweep holds non-numeric inputs at their reported states) — **Closed in
  prose (v0.3)**.

## Ambiguity stratum

**Empty at this stage.** No row's verdict is left resting on an unclosed decision.

## Standing notes

The v0.3 clarifications change no cell's verdict (both engines and the oracle are
unchanged and re-verified). This clean-room build ran against the v0.2 prose and serves as
a pilot of the instrument; the registered clean-room build for the study runs against the
frozen prose at freeze time, per the preregistration. Ceiling: isolation is a process
claim, and the implementer shares the gold author's model lineage (registered; the
third-vendor option was declined 2026-08-15).
