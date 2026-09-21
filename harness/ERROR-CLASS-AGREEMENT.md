# Core 0.2.0-draft §8.4 error-class agreement — Go vs Python over the staged rows

Date: 2026-09-21. Rows: the specification's five **staged** evaluation rows (RFC 0013), vendored
under `reference/conformance-evaluation-staged/` from judgment-pack-spec `4a650a8`. They are in no
corpus: no `suiteVersion` contains them and no claim may cite them. Implementations:

- Go reference runtime at the commit this repository's CI pins, `2cc4f04`, and again at release
  0.22.0: `experimental evaluate`, which writes an `evaluationError` member to stdout.
- Python `jps_evaluator` (this repository, `854653ea`), clean-room lineage, which writes an `error`
  member to stderr.

Method: every staged row run through BOTH CLIs, and three classes compared — the Go class, the
Python class, and the class the row expects — because a staged row may itself be what is wrong. A
row passes only if both implementations refuse without a disposition, report the same class, and
that class is the row's. Driver: `error_class_agreement.py`; its verdict logic and the vendored
rows' digests are tested in `test_error_class_agreement.py`.

## Why this exists

`CLASS-AGREEMENT.md` records 20 / 20 byte-agreement on **dispositions**. `class_agreement.py`
treats any nonzero exit as a non-result, so it has never compared an error class, and the frozen
corpus could not have asked it to: none of its twenty rows expects an error. Core §8.4 fixes four
classes and one order between them "so that two conforming implementations report the same class for
the same inputs", and until the specification staged these rows nothing exercised that sentence
across two implementations.

## Result

**5 / 5 staged rows: both implementations refuse, agree on the class, and agree with the row**, at
both runtime commits.

| Row | Class (row = Go = Python) | Note |
| --- | --- | --- |
| `error-pack-not-conformant` | `pack-not-conformant` | |
| `error-malformed-input-undeclared-evidence` | `malformed-input` | the facts make applicability false, so an evaluator that resolved applicability before admitting the evidence document would answer `not-applicable`; neither does |
| `error-unsupported-required-extension` | `unsupported-required-extension` | |
| `error-precedence-pack-over-malformed-input` | `pack-not-conformant` | `malformed-input` also applies |
| `error-precedence-malformed-input-over-extension` | `malformed-input` | `unsupported-required-extension` also applies; an implementation that checks extension support while reading the pack reports the wrong class here |

Both implementations also report the phase `preflight` on all five. That is printed and not
compared to an expectation: §8.4 requires a class to be reported and not a phase, and the staged
rows assert none.

## What the comparison had to learn

§8.4 leaves "the transport, exit status, and wire format of an evaluation error" undefined, and the
two implementations differ on all three: member name, stream, and exit status. The driver is told,
per implementation, where a result would appear, where an error would appear, and what the error
member is called; it compares the class identifier and nothing else. The first version of the
driver read both implementations' stdout and found no Python error at all. That is a fact about
transport, which §8.4 does not standardize, and not a disagreement; it is recorded here because a
third implementation will meet it too, and §13 keeps a machine-readable diagnostic contract open.

## What this does and does not establish

Both implementations trace to one maintainer's direction: agreement corroborates the text's
precision, it does not independently confirm it (RFC 0006's recorded caveat, carried forward).
Both already carried unit tests of this order, so agreement was the expected result; the value of
the rows is for an implementation that has not been written yet. Five rows exercise three of the
four Core classes and two of the orderings between them. `resource-exhaustion` is not among them,
nor is any malformed input the carrier cannot yet express — a malformed JSON document, a
non-object evidence input, an invalid evidence state. The rows are staged and may still change in
the specification; the vendored copy is held to recorded digests, and re-vendoring is a deliberate
act that names a specification commit.

**No conformance claim is made by this document, and none could be**: a §3.4.1 claim is made
against a released corpus, and these rows are in none.
