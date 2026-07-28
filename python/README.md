# JPS evaluator (Python, experimental)

This standard-library-only Python package evaluates Judgment Pack Core inputs under the
`0.2.0-draft` semantics in `reference/`. It also retains a separately enabled experimental
prototype of RFC 0008's `exists`, `every`, and `uniform` conditions.

This package makes **no evaluator-conformance claim**. Corpus results are reported as test results
only; they do not establish a claim or anything about the truth, authority, safety, or fitness of a
pack or disposition.

## Python API

```python
from jps_evaluator import canonicalize_disposition, evaluate

disposition = evaluate(
    pack,
    facts,
    evidence={
        "intake-form": "present",
        "sponsor-endorsement": "unknown",
    },
    supported_extensions=[],
    evaluation_work_limit=200_000,
)

canonical_bytes = canonicalize_disposition(disposition)
```

`evidence` is optional. Omitting it supplies the implicit empty object; an omitted requirement key
is `"unknown"`. A supplied evidence document must be an object keyed only by declared evidence
requirement ids, with values `"present"`, `"absent"`, or `"unknown"`.

`evaluate()` returns only the §8.3 disposition:

```json
{
  "kind": "outcome",
  "outcomeId": "proceed",
  "reasons": [],
  "handoff": {
    "state": "none"
  }
}
```

`outcomeId` is present exactly for an outcome. `reasons` and `handoff.triggeredBy` are
duplicate-free arrays sorted by Unicode code point. `canonicalize_disposition()` implements the
closed strings/arrays/objects subset of RFC 8785 and returns UTF-8 bytes.

Failures raise an `EvaluationError` subclass. Every error has an `error_class` and `phase`:

| Class | Phase |
| --- | --- |
| `pack-not-conformant` | `preflight` |
| `malformed-input` | `preflight` |
| `unsupported-required-extension` | `preflight` |
| `resource-exhaustion` | `evaluation` |

Preflight is ordered pack, facts, evidence, then supported extensions, and completes before
resolution starts. Errors never return a disposition.

Both `0.1.0-draft` and `0.2.0-draft` packs are accepted. RFC 0008 remains disabled by default;
`enable_rfc0008=True` only enables the local prototype and does not change a pack's status or create
a claim.

## CLI

```console
python -m jps_evaluator \
  --pack pack.json \
  --facts facts.json \
  --evidence evidence.json \
  --supported-extension com.example.capability \
  --evaluation-work-limit 200000
```

On success, stdout contains a compact JSON envelope whose `disposition` member is emitted from its
RFC 8785 canonical bytes:

```json
{"conformanceClaim":"none","disposition":{"handoff":{"state":"none"},"kind":"outcome","outcomeId":"proceed","reasons":[]},"experimental":true}
```

On error, stdout is empty, stderr contains an envelope with separate `class`, `phase`, and `message`
members, and the process exits with status 2. Error envelopes contain no `disposition`.

## Tests

From the repository root:

```console
python3 -m pytest python/tests -q
```

The suite covers Core §§7–8, strict JSON input, full pack structure and semantic references,
preflight precedence, every Core error class and phase, portable disposition invariants, JCS bytes,
the CLI, and the supplied evaluation corpus manifest.

The clean-room corpus snapshot contains the fixture needed by thirteen cases. Those thirteen match
their expected canonical bytes. Three other manifest-declared fixtures are absent, affecting seven
cases; those rows are reported as explicit xfails rather than run against invented inputs. See
decision 26 in `DECISIONS.md`.

## Resource limits

These are implementation limits, not portable Core semantics:

- 16 MiB per JSON text;
- nesting depth 128;
- 200,000 JSON values and object members per input;
- 1 MiB per string or object member name;
- 4,096 characters per JSON-number token;
- 10,000 combined authored evaluation collection items across evidence requirements, outcomes,
  rules, and exceptions; and
- 200,000 evaluation-work units by default, configurable through the Python API and CLI.

A pack that reaches a document/carrier admission limit is `pack-not-conformant`. A facts or evidence
document that reaches one is `malformed-input`. Reaching the collection or work limit after admission
is `resource-exhaustion`. No limit produces a partial disposition.

See `DECISIONS.md` for underdetermined choices and their source text.
