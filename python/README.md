# JPS evaluator (Python, experimental)

This is the second independent implementation built to supply the evidence requested by draft
RFC 0006. It was derived only from the RFC, Judgment Pack Core `0.1.0-draft`, and the Core JSON
Schema in `reference/`. It also contains a clean-room prototype of RFC 0008’s `exists`, `every`,
and `uniform` aggregate conditions.

This package makes **no evaluator-conformance claim**. Core `0.1.0-draft` defines no evaluator
conformance class, and nothing produced here evaluates as a standard. Every serialized output
payload therefore contains:

```json
{
  "experimental": true,
  "conformanceClaim": "none"
}
```

It is an offline, keyless Python 3.10+ package with no runtime dependencies outside the standard
library. It does not validate full Judgment Pack document conformance; a fully conformant pack is
an input precondition. It does perform evaluation-focused sanity checks and rejects malformed
runtime inputs, unsupported required extensions, duplicate JSON members at the text boundary, and
resource-limit failures as errors rather than dispositions.

## Python API

```python
from jps_evaluator import evaluate

disposition = evaluate(
    pack,
    facts,
    evidence={
        "intake-form": "present",
        "sponsor-endorsement": "unknown",
    },
    supported_extensions=[],
    enable_rfc0008=False,
    evaluation_work_limit=200_000,
)
```

`evidence` is optional. Its keys must be declared evidence-requirement ids and each value must be
`"present"`, `"absent"`, or `"unknown"`; omitted keys are unknown. `evaluate()` returns only a
successful disposition. Invalid inputs raise an `EvaluationError` subclass.

RFC 0008 is disabled by default. A pack using any of its operators remains structurally invalid
under JPS `0.1.0-draft`; setting `enable_rfc0008=True` only opts this experimental evaluator into
the local draft prototype. It does not change the pack’s conformance status or create a conformance
claim. When enabled, aggregate depth is at most two, counted structurally through `all`, `any`, and
`not`.

The disposition has `kind`, `reasons`, `handoff`, and the two markers above. `outcomeId` is present
exactly when `kind` is `"outcome"`. The JSON `reasons` array represents an unordered,
deduplicated set; its stable serialization order carries no priority.

## CLI

```console
python -m jps_evaluator \
  --pack pack.json \
  --facts facts.json \
  --evidence evidence.json \
  --supported-extension com.example.capability \
  --enable-rfc0008 \
  --evaluation-work-limit 200000
```

One `--supported-extension` accepts one or more names and the option may be repeated.
`--evidence`, all supported extensions, and RFC 0008 opt-in are optional. The positive-integer work
limit defaults to 200,000 units. A disposition is printed as JSON to stdout. An evaluation error is
printed as a distinct JSON error envelope to stderr, includes the same experimental/no-claim
markers, and exits with status 2.

## Tests

```console
python3 -m pytest python/tests -q
```

`tests/test_appendix.py` walks all ten input rows in the RFC appendix (the RFC calls them nine
logical instances because 7a and 7b are two variants of instance 7). The remaining tests cover
the three-valued operator tables, exact JSON equality, decimal grammar and ordering, RFC 6901
pointer resolution, evidence tri-state behavior, resolution precedence, extensions, errors, the
CLI, and every RFC 0008 Conformance row named by the clean-room brief.

## Resource limits

These are implementation limits, not Judgment Pack semantics:

- 16 MiB per CLI JSON text;
- nesting depth 128;
- 200,000 JSON values and object members per input;
- 1 MiB per string or object member name;
- 4,096 characters per JSON-number token; and
- 200,000 preflight evaluation-work units per disposition by default, configurable through the
  Python API or CLI.

Crossing a limit is an explicit `resource-limit` error, never an incomplete or partial
disposition. RFC 0008 work is precharged per condition before any predicate in that condition
runs. The measure includes all Boolean branches; actual ragged members at each nesting level;
successful and failed pointer attempts; runtime-sized deep comparisons; all sibling aggregates;
and `uniform`’s member pointers and unordered resolved-value pairs. Element order cannot change the
charge. The exact unit formula and alternatives are recorded in decision 22 of `DECISIONS.md`.

See `DECISIONS.md` for every underdetermined choice and the exact reference text used to resolve
it.
