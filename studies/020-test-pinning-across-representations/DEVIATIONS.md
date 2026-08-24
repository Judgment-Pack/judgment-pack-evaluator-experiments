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
| A second calibration pilot | §2a.6 | the reason; thereafter the derived threshold is the **maximum** over all pilots and the transfer bands the **tightest**, with every pilot's rates side by side |
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
  the table, the chosen condition (`low`, N = 50 by the operable-condition-match rule) and the
  witness branch (`gate-5-extension`).
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
