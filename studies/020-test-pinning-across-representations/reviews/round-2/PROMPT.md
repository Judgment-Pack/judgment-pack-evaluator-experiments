# Review round 2 — prompt (verbatim)

You are the cross-vendor adversarial reviewer required by this program's interim review
regime (RFC 0009): a non-Anthropic model reviewing a preregistration before its freeze.
Your findings will be committed verbatim and dispositioned one by one in writing; the
freeze cannot happen until a round of this review returns exactly `freezable as written`.

The study is `studies/020-test-pinning-across-representations/` in this repository — an
instrument repair on Study 019, reviewed by you in round 1 (2026-08-24), which returned
`DO NOT FREEZE` with 13 BLOCKER / 9 MAJOR / 1 MINOR (R1-1 … R1-23). **The maintainer has
now written a disposition on every finding and closed the round; this round reviews the
RESPONDED tree.** Your job is threefold: verify each disposition against the bytes it
claims, adjudicate the rulings that were registered prospectively FOR this round, and
review the newly built calibration instrument that R1-17's remedy ordered submitted to
you before any pilot call.

## Read

- `PREREG-REVIEW.md` — the disposition table is the response; read every row.
- `reviews/round-1/REVIEW.md` — your own findings, for what each disposition answers.
- `PREREGISTRATION.md` — the amended draft (second revision, post-round-1), completely.
- The new and rebuilt files this response added: `calibration/derive_floor.py`,
  `harness/pilot_rates.py`, `harness/tests/test_pilot.py`, `CORRECTION-TARGETS-LOG.md`,
  and the amended `harness/batch.py` (the `pilot` mode), `harness/authoring_call.sh`
  (the `PILOT` label), `harness/make_manifest.py` (`calibration_record_problems()`),
  `harness/integrity.py` (`verify_sweep_evidence()`), `harness/e4lib/presence_idiom.py`,
  `harness/e4lib/family.py`, `harness/e4lib/engines.py`, `harness/e4lib/admit.py`,
  `harness/e4lib/reviewer.py`, `harness/e4lib/decision.py`, `harness/e4lib/e4.py`,
  `harness/score.py`, `harness/transcript_check.py`, `harness/counterfactual_shift.py`,
  `harness/sweep_rates.py`, and the whole of `harness/tests/`.
- `harness/PINS.json`, `harness/PORTS.md`, `harness/SCAFFOLD.md`,
  `harness/POWER-PRESENCE-IDIOM.md`, `harness/COUNTERFACTUAL-SHIFT.json`,
  `DEVIATIONS.md`, `CORRECTION-TARGETS.md`, `README.md`.
- Study 019 is beside this study and FROZEN; the sweep evidence is under `sweeps/`.

## Adjudicate — the rulings registered for this round

1. **R1-4 — the hybrid estimand.** §5.2 rules the hybrid (native outcome, shared offset)
   the registered estimand, with alternatives published Tier D. Is the ruling coherent
   with every §5.5 reprint, and is its record complete?
2. **R1-9 — the amended §3.2 registration condition.** The amendment ((i-a) n/n over the
   operating set, (i-b) 40/40 registered authoring codes, (ii) 0/22) postdates the first
   measurement and the text says so; the re-run certification under the repaired
   detector meets it fresh. Bless the criterion or refuse it — §3.2 registers the
   fallback in the same sentence: refusal flips the kill switch and demotes the guard to
   Tier D.
3. **R1-15 — the holdout engine-refusal exemption.** §6 now exempts holdout invocations
   from `engine-execution-clean`, descriptive only, with the reason on the record
   (reviewer-authored bytes must not hold a veto over the attempt). Sound?

## Verify against source, not trust

- **Every disposition row** against the tree: does the claimed fix exist, does the named
  test exist AND discriminate (the response claims mutation-visibility throughout — spot
  check by reading the tests, not the claims), and does anything in the row overstate
  what landed?
- **The R1-17 instrument, end to end.** `calibration/derive_floor.py`'s rule is the
  exact ONE-SIDED 95 % Clopper-Pearson lower bound at §2a.1's alpha — recount the n = 12
  ladder (12→0.779, 11→0.661, 10→0.562) and check the deliberate refusal of
  `stats.lower_bound()`'s two-sided edge is argued where the code makes it.
  `batch.py pilot` under `PIN_LABEL=PILOT`: the §2a.4(2) ordering (refuses while the
  declaration is null), §2a.6's one-pilot refusal, NO effort exemption, the wrapper's
  anchor for `calibration/<UTC date>-pilot/arm-<ARM>/run-NNN`, citable false throughout.
  `pilot_rates.py` publishes the record `validate_record()` accepts, and
  `make_manifest.calibration_record_problems()` validates schema, counts, output digest,
  recomputed floors and the GO verdict at the freeze gate. Find a pilot output the gate
  wrongly accepts, or a lawful one it wrongly refuses.
- **The §2a.4(2) declaration itself**: `calibration.minimumViable = 0.20` on
  `minimumViableBasis = "identityFloor"`, declared 2026-08-25 with its exposure
  rationale in §2a.4's fill. Audit the declaration's stated pricing (the ≥ 6/12
  threshold arithmetic, the ~6 % / ~19 % false-abort figures at 019's identity rates,
  the 0.82 catch probability at a true rate of 1/3) by recomputation, and audit the
  BASIS argument: is identity-floor the right seat given §5.7, and is 0.20 defensible
  as a collapse gate rather than a quality gate?
- **The R1-9/R1-10 re-certification**: the re-run figures in
  `harness/POWER-PRESENCE-IDIOM.md`'s re-certification section against the repaired
  detector's actual behaviour (the three repairs: statically-bound probe flags,
  statically-bound dynamic tails, non-string scalar probes as value-membership), and
  the third measured ceiling.
- **R1-11's identity gate**: `CERTIFIED_FLAGGED_SHA256` against the certified set, and
  the same-arm-substitution test's power.
- **R1-19's evidence pins**: recompute `sweep.evidenceTrees` digests from the trees.
- **R1-22's rewritten `PORTS.md` cells** against the actual diffs — including the new
  change notes this response appended for its own edits.
- **The §1a partition after R1-1**: `engine-invocation-refused` as an apparatus code
  end to end (admission, E1, E6, the §6 gate, `sweep_rates.py`).
- Every count and figure the amended registration asserts, against the artifact that
  carries it.

## Scrutinise

The standing round-1 lenses still apply (the population rule, the eighteen-member
family, the fill as a registration event, gate 5, the guard, the two identities,
cross-arm fairness, the corrections regime, the frozen-reader standard). Apply them to
the AMENDED tree — in particular: can the pilot machinery be made to spend a call the
registration forbids, can a NO-GO state reach the freeze, and does any disposition
quietly change a registered quantity without a marked amendment?

## Holdout

This study's reviewer-authored prospective content is a **fresh sealed mutant set**
(§4.3, §7 delta 9): authored by you in a later round, committed verbatim, first executed
at the primary attempt, scored "as authored". State whether you are prepared to author
it. **Do not author mutants this round.**

## Output

Numbered findings `R2-<n>`: severity BLOCKER / MAJOR / MINOR, file/section, a
one-paragraph failure mode, and a concrete fix. For each round-1 finding whose
disposition you verified, say so in one line each (grouped is fine); a disposition you
could not verify is a finding. Then one line, exactly one of: `freezable as written`,
`freezable after listed fixes`, `DO NOT FREEZE`.
