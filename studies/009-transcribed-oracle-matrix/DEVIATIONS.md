# Deviations from PREREGISTRATION.md, recorded as they occurred

The preregistration itself is never edited.

## 1. Attempt 1 crashed on a harness defect before any evaluation

**What.** The first post-freeze `run` created `trials/ATTEMPT-1`, acquired
and gate-checked nothing beyond the acquisition store, and crashed with an
`AttributeError`: `harness/study.py` imported its sibling gate module by the
bare name `gate`, which Python resolved to `fabrication-gate/gate.py` after
the path inserts reordered — a module-shadowing defect in the harness, not a
result of any kind. No evaluator ran; no endpoint was computed.

**Scope.** The fix (an explicit `importlib` load of the sibling, plus this
same scoring change: the primary is the first attempt reaching `DONE`)
changes two frozen inputs, so the freeze was regenerated and recommitted.
`trials/ATTEMPT-1` is retained as the ledger requires, with its exit
metadata in `CRASHED`.

**Bearing on endpoints.** None were computed from attempt 1. The primary run
is the first attempt to reach `DONE` under the corrected freeze — attempt 2
— and `RESULTS.json` names the attempt it scored. No prediction was seen,
no fixture changed, and no scored output existed before the fix.

## 2. The post-run adversarial review found the registered enforcement unimplemented

**What.** The post-run review (ADVERSARIAL-REVIEW.md) confirmed attempt 2's
numerical pattern by independent manual rescore — and found the *enforcement*
the third revision registered was not mechanically real: the freeze hashed no
record file, the scorer trusted reported statuses without recomputing
entailment or checking row-set completeness, attempts were unsealed and not
bound to a freeze, the gate compared Python objects rather than canonical
bytes, and `RECORDS.md` was never held to the record files. It also
corrected the record: attempt 1 completed acquisition and transcription
before crashing, so the B matrix's rows were visible (though no evaluator
output or endpoint was), and attempt 2 is a post-deviation demonstration,
not the preregistered first-attempt result.

**Scope.** The harness was repaired to enforce what was registered: the
freeze covers every record; `validate` mirrors POLICY.md and holds records,
sets, and `RECORDS.md`'s table to it; the gate compares canonical bytes and
consumes references; acquisition requires the exact receipt population and a
clean proxy exit; runs bind to their freeze digest, retain structured crash
metadata, and seal read-only under a hashed manifest; `score` verifies
freeze, binding, and seal, requires the full row set everywhere, recomputes
every expectation against the gated wrapper and every mismatch from parsed
dispositions, and scores E5 over all three projects with exact origins. The
freeze was regenerated and recommitted.

**Bearing on endpoints.** Attempts 1 and 2 are retained and demoted:
attempt 2's result stands only as an audited post-hoc demonstration. The
primary result of this study is the first attempt to reach `DONE` under the
corrected freeze, scored by the corrected scorer.
