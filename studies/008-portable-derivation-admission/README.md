# Study 008 — portable-derivation admission

Study 007's adversarial review argued that its own result is evidence the model should not author the
lineage envelope, because a deterministic host could supply the digests and derive the pointers
without error. Study 008 tested the *portable* form of that counterfactual: the derivation rule
expressed as data ([`derivation-rule/`](../../derivation-rule)), whose evidence basis is computed
mechanically from the pointers its evaluation actually read.

**Read [`ANALYSIS.md`](ANALYSIS.md) before the numbers.** All five registered endpoints hit their
predictions, and that is the weakest part of the study. An adversarial pass
([`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md)) established that the preregistration's central
premise was false — Study 007's verifier re-derives with `derive_payload`, which *is* the arm the rule
was being compared against, and the rule was itself authored from that function. Four of the five
endpoints cannot fail once the first passes, and a calibration control shows an entirely un-derived
basis is admitted just as readily.

What survives is narrow and worth having: the rule reproduces the hand-written derivation's claim and
basis **exactly** on 24 cells with no per-cell authoring, and the probe shows a derivation's *read
set* is not in general a *sufficient basis* — the unchanged verifier rejects it on a payload shape the
corpus never contained.

**No model runs.** Study 007's retained content-addressed artifacts are replayed byte-for-byte; no API
budget, no network, and no claim about model behaviour.

The protocol was frozen before implementation in [`PREREGISTRATION.md`](PREREGISTRATION.md) and is
never edited; corrections live in [`DEVIATIONS.md`](DEVIATIONS.md).

From this directory:

```bash
python3 harness/study.py validate
python3 -m unittest -v harness/test_study.py
python3 harness/study.py freeze     # commit FREEZE.json before running
python3 harness/study.py run
python3 harness/study.py score
python3 harness/probe.py
```

Arms over the same cells: **A** the model-authored envelope (Study 007's completed result, derived
from its `M2`, not re-run), **B** Study 007's hand-written derivation with hand-curated basis sets,
**C** the portable rule — plus two unregistered calibration controls that bound what admission can
mean.
