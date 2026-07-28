# Core 0.2.0-draft evaluator-class agreement — Go vs Python over the frozen corpus

Date: 2026-07-28. Corpus: `conformance/evaluation/manifest.json` at spec tag `v0.2.0-draft`
(suiteVersion 0.2.0-draft, 20 rows, seed label). Implementations:

- Go reference runtime, branch `evaluator-class-alignment` (ADR-0010): `experimental evaluate`
  with §8.2 preflight, §8.3 canonical dispositions (internal/jcs), §8.4 typed errors.
- Python `jps_evaluator` (this repository), clean-room lineage, aligned in an isolated room from
  the v0.2.0-draft text alone (import commit `15c7762`; room record there).

Method: every corpus row run through BOTH CLIs; the §8.3 canonical disposition bytes compared to
each other (not merely each to the manifest). Driver: `class_agreement.py`.

## Result

**20 / 20 rows byte-agree between the implementations**, and each also matches the manifest's
expected disposition byte-for-byte (each implementation's own 20/20 corpus runs are recorded in
their respective changes). Every §8.3 serialization rule that could diverge — member ordering,
reasons sortedness, handoff shape, outcomeId presence — produced identical bytes across lineages.

## What this does and does not establish

Both implementations trace to one maintainer's direction: agreement corroborates the text's
precision, it does not independently confirm it (RFC 0006's recorded caveat, carried forward).
The corpus's own gap list (conformance/evaluation/README.md at the tag) bounds what 20 rows
exercise. **No conformance claim is made by this document**; it is the evidence a §3.4.1 claim
would cite, prepared for the maintainer's decision (runtime ADR-0011, forthcoming).
