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
| **A1** | **The registered artifact trees.** §4.1 ports by digest: `gold/GOLD.json`, both mutant corpora and their manifests, both reference implementations and their payloads, `controls/off-gold-equivalence.json`, the witness tables, `verification/V7-COMPLETENESS.md` and `verification/V8-ASYMMETRY-LEDGER.md`, and the design generators `design/gold/check_gold.py` and `design/mutants/regenerate.py`. **None of them is in this tree.** `harness/PINS.json` records each one's 019-side digest under a `…AtSource` member so the port is checkable the moment the bytes land. | `make_manifest.REGISTERED_DOCUMENTS` names them and `--freeze` refuses while any is pending; every harness test that reads one SKIPS by a named reason through `tests/conftest.py`'s `requires_artifact`, so the count of skips is the size of this item |
| **A2** | **The three arm prompts**, assembled deterministically and pinned per arm. `arms/<ARM>/PROMPT.txt` does not exist; `arms.<ARM>.promptSha256` and `promptBytes` are null. | `batch.check_registry()` and the wrapper's prompt-digest gate both refuse; `study_label()` makes the nulls a PILOT |
| **A3** | **The golden pre-prompt capture and the isolation negative control.** Study 019's do NOT carry: a golden context is a fact about the environment and the CLI at capture time, and §2a.1 records that the one condition 019's evidence cannot recover is exactly this one. | `golden.sha256` and `isolationNegative.assent` are freeze pins; `integrity.CEREMONY_LIFECYCLE_PINS` exempts them at the driver's pre-ceremony gate and nowhere else |
| **A4** | **A fresh sealed reviewer mutant set** (§4.3, §7 delta 9). 019's is SPENT. | `reviewerMutantSet.sha256` is a freeze pin with its source named in `integrity.PIN_SOURCES`; `make_manifest.reviewer_load_problems()` runs the non-executing loader from `--freeze` |
| **A5** | **The OPA capabilities file is here and its pin is not.** `controls/opa-capabilities.json` was generated into this tree from the pinned binary and the registered denylist by `e4lib/capabilities.py`, and it reproduces Study 019's digest `7cbfe97d…` byte for byte — which is recorded as `opa.capabilitiesSha256AtSource`, an EXPECTATION the generation met, not a pin inherited without generating. `opa.capabilitiesSha256` is filled at the freeze. | `capabilities.check_committed()` re-derives and compares; the pin is a freeze pin |

---

## S — the registered deltas §7 lists that have NOT landed

Four of §7's thirteen deltas landed with this port (1, 3, 4 and 6 — see
`harness/PORTS.md`'s delta table). These are the rest, and each names the
registration that owes it.

| item | delta | what is owed |
|---|---|---|
| **S1** | §7 delta 2 | **Remove the threshold arm.** The per-language cuts machinery is KEPT — both denominators, both lattices, the shared-class count, and 019's R1-1 lesson that one cut derived from the JPS count and applied to every arm must remain structurally impossible — but no τ, no integer cut, no `highKill` member and no reachability assertion, because there is no cut to assert. `e4.is_high_kill()`, `stats.tau_cut()` and `score.py`'s `highKill` surface are still 019's. **A harness test must assert that no registered decision path reads a cut.** |
| **S2** | §7 delta 2 | The same removal in `harness/PINS.json` and in the published report: `results_markdown()` still prints a high-kill section. |
| **S3** | §7 delta 7 | **Re-derive the batch schedule at 020's registered round count**, publish the attained position spread, and re-pin `batch.order` / `batch.n` / `batch.slots`. `batch.py`'s `SEQUENCES`/`BLOCKS`/`BLOCK_ORDER`/`TAIL`/`ROUNDS`/`RUNS_PER_ARM`/`REGISTERED_SLOTS` are Study 019's and are a **PROVISIONAL planning shape**: §2 registers them as wrong by construction at any other N. The registry carries all three members as NULL and `check_registry()` refuses that state, which is the standing safety property; `tests/test_schedule.py` drives both the refusal and the derivation at more than one round count. N is an output of the pre-pilot sweep (§2.1). |
| **S4** | §7 delta 5 | **The family scorer.** The eighteen members of §5.2, L2c's offset estimator, the two permutation schemes with their pinned B and seed, the intersection–union verdict, the drop-a-pole table, the BCa intervals, and the **refusal rather than fallback** on the ITT × ANCOVA cell. Until it lands, `e4lib/decision.py`'s rows 4 and 5 are Study 019's single-contrast rows and do **not** produce §1.3's closed vocabulary — CLAIM and INDETERMINATE-BY-DISAGREEMENT. `tests/test_score_decision.py::test_the_closed_verdict_vocabulary_is_registered_and_is_NOT_YET_IMPLEMENTED` asserts the gap in both directions, so closing it fails a test rather than passing silently. **This item also owes §3.2(iv)**: the counterfactual per-member shift cannot be computed without it, and `harness/POWER-PRESENCE-IDIOM.md` says so where the number would have gone. |
| **S5** | §2.1 | **The driver's `--sweep` and `--calibration` modes.** The wrapper's half is built and tested (`PIN_LABEL`, the effort flag, the sweep exemption, `citable: false`); `batch.py` carries `PIN_LABELS`, `SWEEP_LABEL` and `CALIBRATION_ROOT` and `invoke()` takes `pin_label`, but the batch COMMANDS that run 27 sweep calls and a 12-per-arm pilot into `calibration/<label>/` are not written. |
| **S6** | §2a.4 | **`calibration/derive_floor.py`**, sealed before the pilot runs, emitting any threshold from the pilot's own per-arm counts by an exact Clopper–Pearson rule with **no human number entering**. It is a registered document already, so `--freeze` refuses while it is absent. |
| **S7** | §7 delta 13 | **The D-1 smoke, restated** as "a real exec at the registered prompt bytes, stand-in binary permitted", with D-2's stand-in-study smoke preserved. Study 019's `tests/E2E-SMOKE.md` is DELETED rather than carried: a document describing another study's runbook is worse than none, and the restatement lands with the smoke it describes. |
| **S8** | §10 | **`CORRECTION-TARGETS.md`**, pinned before the freeze with verbatim wording, venue, URL and retrieval date — including the presence-idiom guard's published power analysis and the pre-pilot sweep's table. Registered while absent, and `--freeze` refuses on it. |
| **S9** | §2.1, M-24 | **The witness-resolution step at pin time.** `codex.reasoningEffortFlag` and `codex.reasoningEffortWitness` are null; the branch taken decides whether transcript gate 5 is extended to the effort or whether the pin is registered as a `CALL.json` self-report. `transcript_check.py` is deliberately unchanged until then, and its ports cell says so. |
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
  pilot runs through `harness/authoring_call.sh` and `harness/batch.py` under a
  `--calibration` mode (S5).
* **`DEVIATIONS.md` is outside the freeze set** (§7 delta 11, ADR 0004), with
  `make_manifest.EXCLUDED_DOCUMENTS` naming it and its reason and
  `tests/test_manifest.py` asserting it while the file exists.
* **The presence-idiom guard is registered** (§3.2). Its power analysis is
  published at `harness/POWER-PRESENCE-IDIOM.md`, `harness/PINS.json`'s
  `presenceIdiomGuard` block carries the verdict as data, and the two measured
  ceilings are in the document rather than here.
