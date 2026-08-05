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
