# Review round 1 — prompt (verbatim)

You are the cross-vendor adversarial reviewer required by this program's interim review
regime (RFC 0009): a non-Anthropic model reviewing a preregistration before its freeze.
Your findings will be committed verbatim and dispositioned one by one in writing; the
freeze cannot happen until a later round of this review returns exactly `freezable as
written`.

The study is `studies/020-test-pinning-across-representations/` in this repository. It is
an **instrument repair on Study 019**, which ended `R1 inconclusive - control gate failed
(e1-floor)`. Its question: within the same registered fragment, under single-shot
authorship at a pinned-and-witnessed compute condition, does the authoring representation
(JPS vs raw Rego vs Rego under the prescribed convention) change **witness-input coverage
against the shared reference** — an eighteen-member sensitivity family under two-sided
Tier C unanimity, with no registered direction, no τ, no δ, and no cut anywhere. The
harness is Study 019's, inherited whole by digest-bound port with thirteen registered
deltas (§7). This is the FIRST round on a filled draft: the pre-pilot effort sweep has
run, §2.1 is filled (condition `low`, N = 60), and the fill's own pre-commit verification
pass left marked corrections in the text — `DEVIATIONS.md`'s operational record and
`CORRECTION-TARGETS.md` carry that history and are part of what you are reviewing.

## Read

- `PREREGISTRATION.md` — the governing draft. Read it first and completely.
- `PREREG-REVIEW.md`, `DEVIATIONS.md`, `CORRECTION-TARGETS.md`, `README.md` — the record
  machinery and both registers.
- `policy/POLICY.md` — the frozen stimulus prose, ported byte-for-byte.
- `design/BRIEF.md`, `design/PANEL-FINDINGS.md` — the design-phase record; where these
  disagree with the preregistration, the rulings in the preregistration govern, and part
  of your job is to check that every such disagreement is marked rather than silent.
- `harness/` — `PINS.json`, `PORTS.md`, `SCAFFOLD.md`, `ADVISORIES.md` if present,
  `score.py`, `batch.py`, `authoring_call.sh`, `transcript_check.py`, `integrity.py`,
  `make_manifest.py`, `leak_tokens.py`, `render_round_status.py`, `grid_gate.py`,
  `sweep_rates.py`, `counterfactual_shift.py`, `e4lib/` (all of it, `family.py` and
  `presence_idiom.py` with particular care), `tests/` (all of it), and the two published
  analyses `POWER-PRESENCE-IDIOM.md` and `COUNTERFACTUAL-SHIFT.json`.
- `sweeps/2026-08-24-effort-sweep/` — `SWEEP.md`, `SWEEP.json`, `SWEEP-RATES.json`, and
  slot records as needed; `sweeps/refused-attempt-0*/` — the two zero-spend refused
  invocations.
- `gold/GOLD.json`, `mutants/`, `reference/`, `controls/`, `verification/` — the §4.1
  artifacts, ported by digest.
- Study 019 is beside this study and is FROZEN; read into it wherever a ported claim
  needs its source checked.

## Verify against source, not trust

- Every `PORTS.md` row, two-sided, against Study 019's own lock
  (`studies/019-authorship-across-representations/harness/STUDY-MANIFEST.sha256`) and
  each destination file's actual bytes — including the rows that record registered
  design changes (`transcript_check.py`'s gate-5 extension above all).
- Every figure in §2.1's fill — the per-arm means, round triples, batch projections, the
  re-pricing table, the operability sentence — against
  `sweeps/2026-08-24-effort-sweep/SWEEP.json`'s full-precision bytes, and every
  perfect/identity cell against `SWEEP-RATES.json` AND a recount of its per-slot records.
- The N = 60 justification against §5.6's own text: which N its size simulation and power
  ladder actually price.
- The three marked corrections (the dual-pricing table's basis error, the catalog counts,
  the power analysis's per-arm flagged split) against their primary sources — recount
  them yourself; the maintainer's corrections have been wrong once already this study.
- §5.5's Reprints against `harness/e4lib/family.py`, `harness/tests/test_family.py` and
  Study 019's frozen `RESULTS.json`; the counterfactual shift's published figures
  against `harness/counterfactual_shift.py`'s actual path.
- Every count the preregistration asserts (gold rows, mutants, pairs, classes, members,
  flagged runs) against the artifact that carries it.

## Scrutinise

1. **The §1a population rule against the driver/scorer partition**: construct an
   authoring failure that leaves the denominator, or an apparatus failure that stays in
   it — including through the sweep's slots and the new `presence-idiom-unsound` code.
2. **The eighteen-member family end to end** (`e4lib/family.py`, `score.py`): the two
   populations, the offset (finding F-1's two denominators — is the maintainer ruling it
   demands actually on the record, and if not, is its absence marked?), the permutation
   schemes and their pins, the IU verdict, the refused ITT × ANCOVA cell, the drop-a-pole
   table. Find a way the verdict vocabulary can be escaped or a member silently dropped.
3. **The §2.1 fill as a registration event**: the operable-condition-match rule is named
   AFTER the sweep by the registration's own design — does any part of the fill do more
   than its stated inputs license? Is the N = 60 choice's stated basis true and
   sufficient? Does anything in the fill read the n = 3 rates into a decision despite the
   disclaimers — including §2a.4(2)'s declared-value exposure, which the fill names?
4. **The gate-5 extension** against its registered obligation (same reason tag, same
   apparatus side, by path, null-is-not-a-witness, before the primary batch): find a
   transcript that should refuse and passes, or should pass and refuses — malformed
   payloads included. Check the driver seat is actually bound (the mutation-visibility
   test) and that the ported-unchanged claims in §7 and the module's own docstring are
   consistent with the diff.
5. **The presence-idiom guard**: the admission-level semantics, the kill switch as data,
   the power analysis's five certified quantities, the counterfactual shift's recode
   semantics and its certified-counts gate. Find a policy the detector misclassifies in
   either direction beyond the two measured ceilings, or a way the guard's effect on the
   family is mis-stated.
6. **The two identity relations** (§1.2): `referenceIdentity` gating, `ownPolicyIdentity`
   reported — find a place the wrong relation gates or the reported one leaks into a
   population.
7. **Cross-arm fairness under the port**: the prompts are 019's bytes; the guard is
   arm-asymmetric by construction (§11.11); the E1-support narrowing (§4.2) — find an
   asymmetry the registered ceilings do not already carry.
8. **The corrections regime itself**: `DEVIATIONS.md`'s operational record,
   `CORRECTION-TARGETS.md`'s targets and recorded corrections, the marked notes in
   §2.1 and `POWER-PRESENCE-IDIOM.md` — is any correction incomplete, any stale statement
   still standing anywhere in the tree, any published byte silently rewritten where an
   append or a marked note was required?
9. **The frozen-reader standard**: a reader holding only the immutable-candidate files
   after the freeze — find a sentence they would read that the artifacts contradict.

## Holdout

This study's reviewer-authored prospective content is a **fresh sealed mutant set**
(§4.3, §7 delta 9; Study 019's is spent): authored by you in a later round, committed
verbatim, first executed at the primary attempt, scored "as authored". State whether you
are prepared to author it. **Do not author mutants this round.**

## Output

Numbered findings `R1-<n>`: severity BLOCKER / MAJOR / MINOR, file/section, a
one-paragraph failure mode, and a concrete fix. Cite the file you read for every claim. A
clean pass on an area is a finding only if you can defend having actually worked it. Then
one line, exactly one of: `freezable as written`, `freezable after listed fixes`,
`DO NOT FREEZE`.
