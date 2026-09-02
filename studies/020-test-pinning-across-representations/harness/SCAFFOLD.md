# SCAFFOLD — what the harness port leaves owed, by name

**This file is the register of open work, and it exists so that "owed" is a
list rather than a memory.** Study 019 kept one for the same reason and closed
every item but one before its freeze; every item below is a `GATE(pre-freeze)`
unless it says otherwise, and `harness/PORTS.md` cites this file wherever a
ported cell carries a deliberate non-change.

The rule this file is written under, from Study 019's own experience: **an
obligation declared in a document and enforced nowhere lets the ceremony
complete without it** (019's round-7 finding R7-9). So an item here is not
merely written down — where the obligation can be enforced by a constant, it
is, and the enforcing site is named in the item's own row.

---

## A — the study artifacts (§4.1's port by digest)

| item | what is owed | enforced by |
|---|---|---|
| **A1** | ~~**The registered artifact trees.**~~ **CLOSED.** §4.1's port by digest is IN THIS TREE: `gold/GOLD.json`, both mutant corpora (183 JPS + 185 Rego payloads) and their manifests, both reference implementations and their payloads, `controls/off-gold-equivalence.json`, `verification/V7-COMPLETENESS.md`, `verification/V8-ASYMMETRY-LEDGER.md`, the frozen `policy/POLICY.md` and the carried `design/` tree. The `…AtSource` members that recorded the ABSENCE are gone with it: the bytes are bound directly, on both sides, by `integrity.verify_ported_artifacts()` against Study 019's frozen lock — 382 artifacts, checked in BOTH directions over the payload trees — and the three arm prompts against 019's own registry. | `integrity.verify_ported_artifacts()`, called from `verify()`; `tests/test_ports_chain.py` drives an edited artifact, a missing payload, a payload 019 never had, and an edited arm prompt |
| **A2** | ~~**The three arm prompts**~~ **CLOSED.** `arms/A|B|C/PROMPT.txt` are in this tree, ported by digest, and `arms.<ARM>.promptSha256` / `promptBytes` carry 019's own registry values. | the wrapper's prompt-digest gate; `integrity.verify_ported_artifacts()` binds each prompt to 019's REGISTRY (019's manifest does not cover `arms/`) |
| **A3** | **The golden pre-prompt capture and the isolation negative control.** Study 019's do NOT carry: a golden context is a fact about the environment and the CLI at capture time, and §2a.1 records that the one condition 019's evidence cannot recover is exactly this one. | `golden.sha256` and `isolationNegative.assent` are freeze pins; `integrity.CEREMONY_LIFECYCLE_PINS` exempts them at the driver's pre-ceremony gate and nowhere else |
| **A4** | **A fresh sealed reviewer mutant set** (§4.3, §7 delta 9). 019's is SPENT. | `reviewerMutantSet.sha256` is a freeze pin with its source named in `integrity.PIN_SOURCES`; `make_manifest.reviewer_load_problems()` runs the non-executing loader from `--freeze` |
| **A5** | **The OPA capabilities file is here and its pin is not.** `controls/opa-capabilities.json` was generated into this tree from the pinned binary and the registered denylist by `e4lib/capabilities.py`, and it reproduces Study 019's digest `7cbfe97d…` byte for byte — which is recorded as `opa.capabilitiesSha256AtSource`, an EXPECTATION the generation met, not a pin inherited without generating. `opa.capabilitiesSha256` is filled at the freeze. | `capabilities.check_committed()` re-derives and compares; the pin is a freeze pin |

---

## S — the registered deltas: what each one still owes

**All THIRTEEN of §7's deltas have landed** — see `harness/PORTS.md`'s delta
table for which file holds each and which test enforces it. The apparatus port
carried the ones that rewrite the analysis (1, 2, 5, 7, 8, 9, 10, 11, 12, 13),
the sweep-driver line carried the ones that rewrite the calling surface (3, 4,
6, and §2.1's sweep mode), and the union carries both. What remains below is the
work each landed delta still owes — a value the sweep has to produce, a document
that has to be written, a mode that has to be built — never the delta itself.

| item | delta | what is owed |
|---|---|---|
| **S1** | §7 delta 2 | ~~Remove the threshold arm.~~ **LANDED.** `e4lib/e4.py` carries no `is_high_kill()`, no `tau_cut()` consumer and no `highKill` member; `paired_denominators()` and `shared_classes()` keep both languages' denominators and lattices separate, which is 019's R1-1 lesson kept structurally. `tests/test_score_decision.py` asserts by name that no registered decision path reads a cut. |
| **S2** | §7 delta 2 | ~~The same removal in the registry and the published report.~~ **LANDED** — `score.results_markdown()` prints the eighteen-member family table where the high-kill section was, and `tests/test_score_publication.py` drives it. |
| **S3** | §7 delta 7 | ~~Re-derive the batch schedule at 020's registered round count.~~ **THE DERIVATION LANDED; THE NUMBER IS STILL OWED.** `batch.py` holds no round count of its own: `_registered_batch_shape()` reads `harness/PINS.json`'s `batch` block at import, `derive_order(rounds)` is the authority at any N, `schedule()` asserts the expansion attains the spreads the REGISTRY publishes rather than 019's (1, 1), and `batch.py derive-schedule --rounds N` prints the block a person then edits in. ~~STILL OWED: 020's own N.~~ **PAID, 2026-08-24.** §2.1's fill registered **N = 60** from the sweep's output — the branch §5.6's Tier C size simulation and power ladder, the dual-pricing table and §5.2's realised-n arithmetic all price — so `batch.n` = 60, `batch.slots` = 180 and `batch.order` re-derived by `derive-schedule --rounds 60` (ten whole Williams blocks, no tail, attained spreads (0, 1)); the registry's note records the flip and keeps the 50-round port carry as history. (The fill's first draft said N = 50 on a claim about §5.6 the verification pass refuted; corrected before commit.) |
| **S4** | §7 delta 5 | ~~The family scorer.~~ **LANDED.** `e4lib/family.py` carries §5.2's eighteen members, L2c's offset estimator, the two permutation schemes with their pinned B and seed, the intersection–union verdict, the drop-a-pole table, `e4lib/stats.py`'s BCa intervals, and the refusal-rather-than-fallback on the ITT × ANCOVA cell; `e4lib/decision.py`'s rows 4 and 5 are §1.3's closed vocabulary — CLAIM and INDETERMINATE-BY-DISAGREEMENT — and `score.registered_family()` is the one place the publisher reads a verdict it did not derive. ~~STILL OWED: §3.2(iv)'s counterfactual per-member shift.~~ **PAID.** `harness/counterfactual_shift.py` computes it through `family_report()` over the detector-derived, count-gated flagged set (32/60 — B 19, C 13; the gate refused the power analysis's first unmeasured split and the correction is recorded there), publishes the four reports and the 36-row distillation at `harness/COUNTERFACTUAL-SHIFT.json`, and `harness/tests/test_counterfactual_shift.py` pins the adapter equivalence, the gate's discrimination and the published figures. The registry member and both documents now carry the computed state. |
| **S5** | §2.1, §2a.2 | **The driver's `--calibration` mode.** ~~and `--sweep`~~ — **the SWEEP half LANDED**: `batch.py sweep` (section D9) runs §2.1's 27 calls, sequential and arm-interleaved with A first, under `PIN_LABEL=SWEEP` with the per-call setting threaded in `SWEEP_EFFORT`, into `SWEEP_ROOT` (`sweeps/<UTC date>-effort-sweep/<setting>/arm-<ARM>/run-NNN`, outside `arms/` so R10-1's occupancy gate cannot see it), with the per-setting abort rule's two clauses, the derived 27-call cap, M-24's witness resolution as step zero, and `SWEEP.json`/`SWEEP.md` published after every call, `citable: false` throughout. The swept SET is registered — `low`, `medium`, `high`, the maintainer's dated 2026-08-24 decision (§2.1) — and the effort flag's spelling is resolved (`-c model_reasoning_effort=<tier>`; the pinned CLI has no reasoning-effort flag). `tests/test_sweep.py` drives all of it. **The CALIBRATION half LANDED too (round 1, R1-17)**: `batch.py pilot` runs §2a.2's 12/arm = 36 calls, sequential and arm-interleaved with A first, under `PIN_LABEL=PILOT` (no exemption — the registry's own `codex.reasoningEffort`, all design-time pins checked) into `calibration/<UTC date>-pilot/arm-<ARM>/run-NNN`, publishing `PILOT.json`/`PILOT.md` after every call, `citable: false` throughout; it refuses while `calibration.minimumViable`/`minimumViableBasis` are undeclared (§2a.4(2)'s ordering) and refuses a second pilot (§2a.6). `harness/pilot_rates.py` computes the per-arm counts afterwards through `sweep_rates.score_slot()`'s one scoring mirror and publishes `PILOT-RATES.json`, validated by the sealed deriver at publication. `tests/test_pilot.py` drives all of it. The sweep itself RAN 2026-08-24 (27/27 under the registered label, two operator-error invocations preflight-refused in full first — `DEVIATIONS.md`'s operational record) and §2.1's fill closed its outputs. The §2a.4(2) declaration is REGISTERED (0.20 on the identity floor, 2026-08-25, provenance in `PINS.json`). **Round 2 (R2-7, R2-8, R2-10, R2-12) rebuilt the pilot as an instrument with a state machine**: 12 apparatus-clean scored calls per arm drawn from at most 21 attempts under an A-first round robin (`pilot_next_entry()`, replayable from the ledger's own codes); every attempt finalized through the batch's own `refuse_slot` → `stamp_slot` → `bind_transcript` → `seal_slot` → chained `ledger_record` path with `PILOT.json` written atomically; the golden capture a pilot precondition; `pilot_rates.py` reading the sealed slots through `score.read_slot()`'s pre-scoring order (an author protocol violation is COUNTED and scores zero, never `slot-shape`); the freeze gate authenticating the ledger (replay, chain, per-slot seals, `CALL.json` pin state, no unnamed slot, rates/ledger agreement); one pilot, TERMINAL, with `batch.py abandon --label` for a label under which no call completed. The pilot has NOT run — the rebuilt instrument goes to round 3 before any pilot call. |
| **S6** | §2a.4 | **`calibration/derive_floor.py` LANDED (round 1, R1-17)**: sealed before the pilot runs, emitting BOTH per-arm floors (perfect and identity-passing) by the exact Clopper–Pearson rule through `e4lib/stats.py`'s certified implementation, with **no human number entering** — the go/no-go compares the DERIVED floors against the DECLARED `calibration.minimumViable` on the DECLARED `minimumViableBasis`, and its `validate_record()` is the ONE reading of the pilot-record contract, consumed by `pilot_rates.py` at publication and by `make_manifest.calibration_record_problems()` at the freeze gate (which now validates the record's schema, counts, digest, recomputed floors and GO verdict rather than merely finding a labelled subtree). The §2a.4(2) declaration LANDED at round 1's close (0.20 on `identityFloor`). Round 2 (R2-7, R2-9, R2-10) added to the sealed file, pre-pilot and recorded in `DEVIATIONS.md`'s operational record: `validate_declaration()` (type, finiteness, range, vocabulary — no study number enters it), the amended population shape (`attempted`/`calls`/`apparatusExcluded` reconciled as one partition, cap 21), each cell reconciled to its own slot rows, and an embedded verdict checked against its recomputation. Nothing on this line is owed. |
| **S7** | §7 delta 13 | **The D-1 smoke, restated** as "a real exec at the registered prompt bytes, stand-in binary permitted", with D-2's stand-in-study smoke preserved. Study 019's `tests/E2E-SMOKE.md` is DELETED rather than carried: a document describing another study's runbook is worse than none, and the restatement lands with the smoke it describes. |
| **S8** | §10 | ~~`CORRECTION-TARGETS.md`~~ **LANDED, 2026-08-24**: T1–T7 in Study 019's pattern, including the guard's power analysis (T5, already carrying its first recorded correction) and the pre-pilot sweep's table with its chosen condition (T6). Uncovered by design; `make_manifest.py` names it only while absent, which it no longer is. |
| **S9** | §2.1, M-24 | ~~The witness-resolution step at pin time.~~ **CLOSED, 2026-08-24.** The sweep's step zero took branch `gate-5-extension` over the first sweep call's own transcript (two non-null `turn_context` spellings, zero nulls); `codex.reasoningEffortWitness` records it, `transcript_check.py`'s gate 5 now binds the effort pin beside the model and the cwd (by path, both spellings, present-and-null a non-witness), and its ports cell records the one registered design change. The self-report branch was NOT taken and stands in the registration as the branch that would have fired. |
| **S10** | §5.2 | **The per-member analysis-set arithmetic**, and each member's registered per-arm n. A function of N (S3) and of the realised-n arithmetic. |

---

## R — the runbook and the ceremony

| item | what is owed |
|---|---|
| **R1** | **The freeze runbook.** Study 019's `SCAFFOLD.md` carried a step-numbered freeze-fill procedure (F1…F8, G1…G3); 020 has none yet. What the ORDER must be is already fixed and is written in `harness/PORTS.md` under "Reconciliation order": the ported files, then `PORTS.md`, then `PINS.json`'s `ownPorts`, then the manifest LAST, then the freeze commit. **What the runbook must NAME is fixed too, and it is written out below rather than left to the round that writes the steps** — because an operator's procedure that does not name a gate is a procedure that walks past it, which is what Study 019's R5-6, R9-2 and R10-1 each found in turn. |

### R1's obligations, named now so the runbook cannot be written without them

The freeze-fill procedure, when it lands, must carry a step for each of these
and name the artifact each one checks. `harness/tests/test_manifest.py` asserts
the names against `harness/make_manifest.py`'s own constants, so a gate added to
the code without a step here fails the suite rather than the ceremony.

* **R5-6 — the registered payload sets, by glob and not by manifest.** Study
  019's step listed the two top-level mutant MANIFESTs and not the payload trees
  they point at, so a tree with both manifests present and both payload roots
  absent froze successfully. The sets are `mutants/jps/*.json` and
  `mutants/rego/*.rego`; `controls/reviewer-mutants` is committed during the
  review rounds (item A4) and is not a freeze-fill step.
* **R9-2 — no prior attempt root.** `results/primary-attempt-001` must not
  exist, under that name or any other, on disk or in the INDEX.
  `prior_attempt_problems()` is the gate.
* **R10-1 — no pre-existing authoring state.** No `arms/<ARM>/authoring` slot
  tree and no ledger: `arms/BATCH.json`, its atomic-write temporary, or a
  shortfall declaration. `prior_authoring_problems()` is the gate, and it reads
  the driver's own constants so it cannot go on checking a spelling the driver
  has stopped writing.
* **NEW IN 020 — the calibration subtree is PERMITTED and REQUIRED.**
  `calibration/` must exist and hold a pilot label; `calibration_problems()` is
  the gate, and 019's `DEVIATIONS.md` D-2 is why both halves are named.
| **R2** | **The review record.** `PREREG-REVIEW.md` is open with **zero** rounds — a registered shape in 020, which is §7's delta 10 and the reason `render_round_status.py`'s `parse_block()` permits an empty-of-rounds block. The status sentence in both front doors is RENDERED, not hand-written, from the first act of this port onward. |
| **R3** | **Archive-verified suite claims** (ADR 0005, decision 1). A "N passed" claim is made only of a commit, after `git archive <commit> \| tar -x` into a fresh directory, `git init && git add -A` inside it, then the full suite under the registered interpreter — before push, ceremony and prompt-only commits included. |

---

## What is NOT owed, and is recorded so nobody re-opens it

* **`design/pilot/pilot_run.py` is deleted, not ported** (§2a.2, §7 delta 12).
  019's pilot driver called codex with no `env=`, no `-m` and no
  `--ignore-user-config`; a second calling path is what made 019's pilot measure
  a compute condition its registered batch never reproduced. The pre-freeze
  pilot runs through `harness/authoring_call.sh` and `harness/batch.py` under
  the landed calibration mode `batch.py pilot`, `PIN_LABEL=PILOT` (S5).
* **`DEVIATIONS.md` is outside the freeze set** (§7 delta 11, ADR 0004), with
  `make_manifest.EXCLUDED_DOCUMENTS` naming it and its reason and
  `tests/test_manifest.py` asserting it while the file exists.
* **The presence-idiom guard is registered** (§3.2). Its power analysis is
  published at `harness/POWER-PRESENCE-IDIOM.md`, `harness/PINS.json`'s
  `presenceIdiomGuard` block carries the verdict as data, and the two measured
  ceilings are in the document rather than here.

---

## M — raised by the merge of the two parallel lines

| item | what is owed |
|---|---|
| **M1** | **The detector's parse was UNREACHABLE and is now repaired; the repair needs a review round.** `e4lib/engines.py` carried two functions named `opa_parse` — Study 019's, returning `(exit, stdout)` and read that way by `e4lib/e4.py`, and §3.2's new one returning `(exit, stdout, stderr)`. The later `def` replaced the earlier at import, so `presence_idiom.parse_policy()` unpacked two values into three and `scan()` raised `ValueError` on its first REAL call. No test on either line saw it: every unit case monkeypatches the parse with a three-tuple stub, and the one case that uses the pinned binary calls `subprocess.run` directly and then `memberships()`. The merge renames the new one `opa_parse_tree()` and adds two cases — `test_the_detectors_parse_is_not_the_suites_parse` and `test_the_detector_runs_end_to_end_against_the_pinned_binary`. **What is owed: whether `harness/POWER-PRESENCE-IDIOM.md`'s measurements were produced through `scan()` or around it.** If around it, the certification's numbers are not the numbers this code path produces and the analysis must be re-run through the repaired entry point before §3.2's kill switch stays `true`. |
| **M2** | **A candidate advisory: the function-parameter ceiling is closable.** `presenceIdiomGuard.measuredCeilings` publishes "a presence test over a FUNCTION PARAMETER is not detected (2 runs, B run-023 and C run-040)". The apparatus line's own detector resolved exactly that construction — `parameter_bindings()` over six rounds, following a parameter through its call sites and through two helpers, dropping a parameter with two kinds of call site and reporting a cycle rather than hanging. Measured on the merged tree against the pinned binary: a policy whose only membership is `k in collection` inside `has_member(collection, key)`, called once with `input.evidence`, is **flagged by the apparatus detector and classified LAWFUL by the certified one**. The certified bytes are kept (they are what the published analysis binds); this is recorded as a candidate advisory, not applied, because swapping the implementation would invalidate the certification. |
