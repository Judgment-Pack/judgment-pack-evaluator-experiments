# Clean-room brief: second JPS evaluator (Python)

You are building the **second, independent implementation** of the evaluator proposed by
RFC 0006 — the evidence its acceptance requires. Independence is the entire point: this
implementation must be **derived from the reference texts in `reference/` and nothing else**.

## Hard rules

1. **Read only `reference/`** — the RFC (`0006-evaluator-conformance.md`), the Core specification
   (`judgment-pack-core.md`, especially §§2.2, 7, 8), and the JSON Schema. Do **not** open, read,
   grep, or consult `judgment-pack-runtime` (the Go reference implementation), its repository, its
   tests, or its documentation — anywhere on this machine or online. A port inherits the first
   implementer's silent resolutions and proves nothing about the prose.
2. **Where the text underdetermines a choice, do not guess silently.** Make the most defensible
   reading, implement it, and record it as a numbered entry in `DECISIONS.md` (the text you relied
   on, the alternatives you saw, the reading you chose, and why). These notes are first-class
   evidence for the RFC — divergences between implementations are how spec ambiguity gets found.
3. **No conformance claim, anywhere.** Core §3.4 forbids evaluator-conformance claims. Every
   output payload must carry `"experimental": true` and `"conformanceClaim": "none"`; the README
   must say the same. Nothing here evaluates as a standard.

## What to build

A small Python package (`jps_evaluator/`, stdlib only, Python 3.10+) that applies the RFC's pinned
semantics to one pack:

- **Inputs:** a pack JSON document (precondition: full document conformance, established
  externally — you may sanity-check the shape against `reference/judgment-pack-core.schema.json`
  but need not reimplement document validation); one JSON facts document; an optional tri-state
  evidence-availability object as the RFC defines it; a supported-extension list.
- **Semantics:** exactly what the RFC's Specification sketch pins, over §§7–8 as the RFC makes
  them normative — three-valued conditions, the restated required-evidence step, ordered decimal
  comparison as pinned, exception effects and their precedence, the never-tie-broken conflict, the
  fallback rules, and §8.1 handoff.
- **Output:** the RFC's disposition (`kind`, `outcomeId`, `reasons` as a deduplicated set,
  `handoff`), plus the experimental/no-claim markers. Errors are not dispositions — refuse bad
  inputs explicitly, as the RFC requires.
- **CLI:** `python -m jps_evaluator --pack FILE --facts FILE [--evidence FILE]
  [--supported-extension NAME ...]` printing the result as JSON to stdout.
- **Tests:** derive the nine walked instances from the RFC's appendix table into a test suite
  (`tests/test_appendix.py`) — the appendix rows are inputs *and* expected dispositions. Add unit
  tests for whatever the texts define precisely (three-valued operator tables, the decimal
  grammar, pointer resolution, evidence tri-state).
- **`DECISIONS.md`:** every interpretation decision, numbered (rule 2 above).
- **`README.md`:** what this is (second independent implementation for RFC 0006's evidence bar),
  the no-claim statement, how to run the CLI and tests.

Offline, keyless, no network access at runtime, no third-party dependencies.

## Definition of done

`python -m pytest tests/` passes, the CLI produces a disposition for an appendix instance, and
`DECISIONS.md` honestly records every judgment call. Do not compare against, or attempt to match,
any other implementation — agreement is measured *afterwards*, by someone else. If your reading of
the text disagrees with the appendix table's expected disposition for some instance, **say so in
DECISIONS.md rather than bending your implementation to match** — that disagreement is exactly the
evidence this exercise exists to produce.
