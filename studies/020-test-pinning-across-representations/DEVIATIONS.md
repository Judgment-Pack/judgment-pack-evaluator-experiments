# Deviations — Study 020

Deviations from the frozen preregistration land here with a reason and a date — never by editing
the preregistration or any frozen artifact. **Nothing is frozen yet**, so nothing here is a
deviation: before the freeze, a change is a revision of a draft and belongs in the document
itself, under review.

This file is **outside the freeze set** by design, per ADR 0004's appendable-files rule and Study
018's lesson (018's `DEVIATIONS.md` was inside its freeze set and had to move out). It is excluded
from the exact-set manifest by named constant in `harness/make_manifest.py`, with an asserting
test, precisely so that recording a deviation can never stale the manifest.

**Freeze commit:** *(not yet — named by reference in `PREREGISTRATION.md` as the squash-merge
commit of the freeze PR on `main`)*.

## Entries that this study's registered rules will route here

Named in advance so a reader knows what a silent absence would mean. Each is registered in
`PREREGISTRATION.md` at the section cited.

| Trigger | Registered at | What the entry must carry |
|---|---|---|
| Adding a member to the eighteen-member sensitivity family after registration (removal is forbidden) | §5.2 | the member, the arm-blind reason, and **the pre-addition verdict published beside the post-addition one** |
| ~~A second calibration pilot~~ — struck (round 2, R2-12): there is no second pilot | §2a.6 | — |
| An arm short of 12 apparatus-clean calls at the 21/arm attempt cap | §2a.2 (as amended, R2-10) | the reason and the per-arm attempted / clean counts; no rates are published and under M-9 the study aborts |
| Abandoning a pilot label under which no call completed | §2a.6 (as amended, R2-12) | the label, the cause of the refusals, and the `batch.py abandon` invocation; the tree is retained under `calibration/abandoned-<label>/` |
| Raising the pre-pilot sweep's 27-call cap | §2.1 | the reason and the republished price |
| A post-freeze registry re-pin | §1a | the halt-and-restart record and the abandoned slots with their codes |
| Moving the identity gate from `referenceIdentity` to the conjunction with `ownPolicyIdentity` | §1.2, §11.10 | the obligation to re-derive every per-protocol member's population and §5.6's dispersion |
| Reinstating an author-side control gate | §2a.4, §5.7 | the stimulus degradation's computed per-arm miss-count shift **published before the pilot runs**, the authoring-call budget, and the realised-n arithmetic gap |
| Crossing the registered batch window | §2 | the window actually used and the cause |
| A corrected or retracted R1 | §10 | the entry, plus a banner at the head of `ANALYSIS.md`, per `CORRECTION-TARGETS.md` |

*(No entries.)*

## Operational record — pre-freeze, not deviations

Recorded here because the sweep driver's single-sweep gate names this file as the place a
re-invocation is explained. Nothing below changed any registered text, and no model call was
made or token spent in either refused attempt.

- **2026-08-24, sweep attempt 1** (`sweeps/refused-attempt-01-leak-tokens/`): all 27 calls
  preflight-refused by the wrapper's leak-token screen — the operator passed a `--scratch-parent`
  under the session scratchpad, whose absolute path carries the study's own name. Zero spend.
- **2026-08-24, sweep attempt 2** (`sweeps/refused-attempt-02-unregistered-label/`): all 27 calls
  preflight-refused by the wrapper's slot anchor — the operator passed `--label
  2026-08-24-effort-sweep-02`, which does not match the registered `<UTC date>-effort-sweep`
  shape. Zero spend.
- **2026-08-24, sweep attempt 3**: run under the registered label `2026-08-24-effort-sweep` from
  a token-free scratch parent outside every worktree (`/tmp/s020sw`), after moving the two
  refused records to the names above so the single-sweep gate sees a clear registered label.
  Both refusals were the apparatus working as registered against operator error; neither
  consumed the §2.1 cap, which counts calls made under the registered label's tree.
  **Completed 27/27, zero apparatus codes, zero timeouts, zero aborts**; §2.1's fill carries
  the table, the chosen condition and the witness branch (`gate-5-extension`). *(Marked
  2026-08-24, round-1 finding R1-16: this sentence first read "N = 50" — written before the
  fill's verification pass corrected the registered N to 60, and left standing unmarked; the
  registered condition is `low`, N = 60, and the correction entry below is the authority.)*
- **2026-08-24, the rates the driver may not compute**: §2.1's fill obligation names per-arm
  perfect and identity rates in the published sweep table, and the driver's registered
  self-description forbids it computing any rate. `harness/sweep_rates.py` (registered,
  covered, tested) scored the 27 slots through the registered components and appended the
  rates section to `SWEEP.md` with `SWEEP-RATES.json` beside it. No kill quantity was
  computed, by registered scope.
- **2026-08-24, the §2.1 fill and its pre-commit adversarial verification**: the fill (chosen
  condition `low` / N = 60, the witness branch, the gate-5 extension, the schedule re-derivation)
  was verified by a four-lens adversarial pass before commit, which (a) refuted the fill's first
  N-justification (it claimed §5.6's operating characteristics live at N = 50; they are stated at
  N = 60, and the registered N was corrected to 60 with the order re-derived), (b) found two
  errors in PRE-SWEEP registered text, both now corrected in place with marked notes — the
  dual-pricing table's sweep and smoke rows divided calls by nine instead of three
  (understating the pilot-like total as ~64.8 h where it is ~71.2 h against the 72 h budget),
  and the catalog paragraph's `max` availability and default-tier counts — and (c) hardened the
  gate-5 extension against malformed `turn_context` payloads with the driver seat made
  mutation-visible. All findings and their dispositions are visible in the fill's own text and
  the round-1 reviewer sees this entry.
- **2026-08-24, a stale line citation inside published sweep bytes**: `SWEEP.json`'s
  witness-resolution note cites `transcript_check.py:603-608`, which is the correct span in
  STUDY 019's copy and stale for 020's (the port note shifted the module by nine lines; the
  clause is gate 5's `turn-context-mismatch` membership idiom). The published ledger's bytes
  stand as published; the living carriers of the citation (`PREREGISTRATION.md`,
  `harness/batch.py`, `harness/tests/test_sweep.py`) now name the clause instead of a line
  span.
- **2026-08-26, the pilot instrument rebuilt under round 2 (R2-7, R2-8, R2-10, R2-12), before
  any pilot call**: `calibration/derive_floor.py` — registered "sealed before the pilot runs"
  (§2a.4(1)) — was edited pre-pilot to carry the row-reconciliation half of the record contract
  (each per-arm cell equals its own slot rows recounted; an embedded verdict equals its own
  recomputation), the amended population shape (12 apparatus-clean scored calls drawn from at
  most 21 attempts, `attempted`/`calls`/`apparatusExcluded` one partition), the declaration's
  validation (type, finiteness, range, vocabulary — `NaN` had made every `floor < minimum`
  comparison False), and the terminal-pilot rule replacing the struck maximum-over-pilots
  paragraph. The edit is lawful because the pilot has not run, and it is recorded here so the
  sealed file's history is visible. Landed with it: `batch.py pilot` now runs the batch's own
  per-slot finalization (refusal record → schedule stamps → transcript binding → seal → chained
  `PILOT.json`, written atomically) under an A-first round robin that replaces wrapper-refused
  attempts; the golden capture is a pilot precondition; `harness/pilot_rates.py` reads the sealed
  slots through the primary path's pre-scoring order; the freeze gate authenticates the ledger
  (replay, chain, per-slot seals, `CALL.json` pin state, no unnamed slot, rates/ledger
  agreement); and `batch.py abandon --label` retains a label under which no call completed. No
  pilot call has been made; `calibration/` still holds only `derive_floor.py`.
- **2026-08-26, the two post-pilot instruments and the calibration freeze pins (round 2,
  R2-11, R2-13, and the completeness review's finding beside them)**: the transfer gate C4 —
  registered in §2a.5 and required by `decision.CONTROL_GATES` — had no producer, so every
  attempt would have failed as "not evaluated"; and §2a.6's dispersion re-derivation had no
  producer, schema, pin or gate. Both landed in one shared pass, `harness/pilot_analysis.py`,
  which walks the sealed pilot slots once and publishes `C4-REFERENCE.json` and
  `PILOT-DISPERSION.json` under `calibration/<label>/`, each a freeze pin. Two maintainer
  rulings are recorded here because they moved registered quantities: (a) C4 has TWO band rows
  (duration, completion bytes), the reasoning-token band struck as a gating row because §2a.5
  and §2.1's M-24 fill contradicted each other about it — the token median stays published,
  descriptive only; (b) the dispersion table is BUILT (not withdrawn) and its σ stands BESIDE
  §5.6's 019 prior rather than replacing it. And one finding of the response's own review: §2a.6
  said "label, N and output digest go into `PINS.json` before the primary attempt" and NO label
  rule read those members — `integrity.study_label()` returned REGISTERED with every calibration
  pin null. The five calibration members are freeze pins now (eighteen → twenty-three). No
  pilot call has been made; neither artifact exists yet, and `--freeze` names both pins.
