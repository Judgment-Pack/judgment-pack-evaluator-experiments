# Judgment Pack evaluator experiments

Clean-room implementations of the evaluator proposed by the Judgment Pack Specification's
[RFC 0006](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0006-evaluator-conformance.md)
(Draft), built to generate the evidence its acceptance requires: independent implementations,
derived from the specification text alone, whose agreement tests whether the prose actually pins
the semantics — and whose divergences locate the places it does not.

**Nothing in this repository claims any JPS conformance.** JPS `0.1.0-draft` defines no evaluator
conformance class and forbids evaluator-conformance claims outright (Core §3.4). Every
implementation here is experimental, may change or be removed without compatibility promise, and
evaluates nothing normatively: a disposition is data, not an authorization, a decision, or an
executed action.

## Layout

| Path | What it is |
| --- | --- |
| [`CLEAN-ROOM-PROTOCOL.md`](CLEAN-ROOM-PROTOCOL.md) | The reusable recipe every implementation must follow to count as evidence |
| [`reference/`](reference/) | Pinned snapshots of the specification texts the rooms are built from |
| [`harness/`](harness/) | The post-hoc referee: runs identical inputs through implementations and diffs dispositions |
| [`python/`](python/) | Implementation #2 (the first lives in [`judgment-pack-runtime`](https://github.com/Judgment-Pack/judgment-pack-runtime)): stdlib-only Python, written clean-room by a coding agent from the reference texts, with its interpretation log in [`python/DECISIONS.md`](python/DECISIONS.md) |

Future implementations (TypeScript, Rust, …) get sibling directories — but the clean room itself
never happens inside this repository: an implementer working here could read the existing
implementations. See the protocol.

## Results so far

- **13/13 semantic agreement** between the Go reference runtime's experimental evaluator
  (v0.2.0) and `python/` on RFC 0006's nine appendix instances plus three probes — identical
  kind, outcome, reason set, and handoff state ([`harness/README.md`](harness/README.md)).
- **Two specification gaps found** and recorded as RFC 0006 unresolved questions: number
  representability, and the disposition's concrete JSON serialization (the two implementations
  agreed on all semantics while serializing `handoff` incompatibly — see
  [`python/DECISIONS.md`](python/DECISIONS.md) entry 3).

## License

Apache-2.0. This repository is maintained alongside, but is not part of, the normative
specification; the specification repository owns the standard and its conformance corpus.
