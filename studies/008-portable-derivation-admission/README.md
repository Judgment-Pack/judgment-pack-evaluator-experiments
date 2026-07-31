# Study 008 — portable-derivation admission

Study 007's adversarial review argued that its own result is evidence the model should not author the
lineage envelope at all, because a deterministic host could supply the digests and pointers without
error. Study 008 tests the *portable* form of that counterfactual: not bespoke per-study Python, but
the derivation rule expressed as data ([`derivation-rule/`](../../derivation-rule)), whose evidence
basis is computed mechanically from the pointers its evaluation actually read.

The question is whether that mechanically-derived basis satisfies a verifier authored by a **different
study**, on all 24 of Study 007's retained cells, with one rule and no per-cell special-casing.

**No model runs.** Study 008 replays Study 007's retained content-addressed artifacts byte-for-byte,
consumes no API budget, and makes no claim about model behaviour.

The protocol was frozen before implementation in [`PREREGISTRATION.md`](PREREGISTRATION.md).

From this directory:

```bash
python3 harness/study.py validate
python3 -m unittest -v harness/test_study.py
python3 harness/study.py freeze
python3 harness/study.py run
python3 harness/study.py score
```

Three arms over the same cells: **A** the model-authored envelope (Study 007's completed result,
carried as a reference column, not re-run), **B** Study 007's existing host-side assembler with
hand-curated basis sets, and **C** the portable rule. Arms B and C differ in exactly one respect —
where the claim and basis come from — so any admission difference is attributable to that.

Results land in [`RESULTS.md`](RESULTS.md); [`ANALYSIS.md`](ANALYSIS.md) reads them against the
registered predictions.
