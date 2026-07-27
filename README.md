# Judgment Pack evaluator experiments

Empirical evidence about the evaluator proposed by the Judgment Pack Specification's
[RFC 0006](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0006-evaluator-conformance.md)
(Draft), in two tracks that answer two different questions and are judged by different standards:

- **Agreement — *do independent implementations produce the same result?*** Clean-room evaluators
  derived from the specification text alone. Their agreement tests whether the prose actually pins
  the semantics; their divergences locate the places it does not. Deterministic, offline, CI-verified.
- **Efficacy — *does representing a policy this way actually help?*** Preregistered experiments on
  third-party benchmarks. API-dependent, costly, non-deterministic, and run manually — never in CI.

The two are kept visibly separate on purpose. Conformance evidence is something a specification
project is the right author of; efficacy evidence is something it is the *wrong* author of, and the
only remedy is method: preregistration, public harness and data, and reported negative results.

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
| [`python/`](python/) | **Agreement track.** Implementation #2 (the first lives in [`judgment-pack-runtime`](https://github.com/Judgment-Pack/judgment-pack-runtime)): stdlib-only Python, written clean-room by a coding agent from the reference texts, with its interpretation log in [`python/DECISIONS.md`](python/DECISIONS.md) |
| [`studies/`](studies/) | **Efficacy track.** Preregistered experiments; see [`studies/001-policy-representation/`](studies/001-policy-representation/) |
| [`docs/adr/`](docs/adr/) | Decision records for this repository — why a given study is being run, and what comes next |

Future implementations (TypeScript, Rust, …) get sibling directories — but the clean room itself
never happens inside this repository: an implementer working here could read the existing
implementations. See the protocol.

## Results so far

### Agreement track

- **13/13 semantic agreement** between the Go reference runtime's experimental evaluator
  (v0.2.0) and `python/` on RFC 0006's nine appendix instances plus three probes — identical
  kind, outcome, reason set, and handoff state ([`harness/README.md`](harness/README.md)).
- **Two specification gaps found** and recorded as RFC 0006 unresolved questions: number
  representability, and the disposition's concrete JSON serialization (the two implementations
  agreed on all semantics while serializing `handoff` incompatibly — see
  [`python/DECISIONS.md`](python/DECISIONS.md) entry 3).

### Efficacy track

No results yet. [Study 001](studies/001-policy-representation/) is preregistered and its pipeline is
being built; the rationale for running it on RuleArena, and the ordered list of what to run next, is
[ADR-0001](docs/adr/0001-evaluate-on-rulearena-first.md).

## License

Apache-2.0. This repository is maintained alongside, but is not part of, the normative
specification; the specification repository owns the standard and its conformance corpus.
