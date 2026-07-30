# Preliminary adversarial review — Study 005 and the source-reference proposal

## Review status

This is an internal red-team pass by the same OpenAI-assisted project that designed and ran the
study. It is not the commit-relative, cross-vendor adversarial review required by specification
RFC 0009 for a material JPS or runtime change.

## Strongest contrary interpretation

The experiment is evidence against implementing the proposal now.

The prose arm selected the correct source in all 24 cells, including unavailable, ambiguous,
permission-denied, injected, alias, and mutating-decoy cases. Adding the semantic id improved no
tool call. The registered aggregate win arose from three status/fact-mapping differences in a
sample too small to distinguish a representation effect from ordinary model variance. Calling
this a “source discovery” win would overstate the result.

## Blocking design questions

1. **Identity is not authority.** Any tool can claim that it provides an id. The study supplied
   truthful metadata and did not test a malicious exact claimant. The spec needs no trust illusion:
   authorization, provenance, and binding policy remain application responsibilities.
2. **No universal kind catalog exists.** A closed list of databases, documents, people, APIs,
   MCP tools, queues, and future sources will either reject valid systems or evolve into connector
   configuration. The portable contract should standardize reference mechanics, not all source
   kinds.
3. **Observation and determination can be confused.** Naming a source
   `vendor.sanctions-status` encourages agents to fetch a policy conclusion. OFAC returns
   observations; the pack determines status.
4. **Binding cardinality is unresolved.** Zero, one, and many candidate integrations need explicit
   client behavior. Selecting a convenient fallback can silently change evidentiary authority.
5. **Version and freshness are unresolved.** A stable id can bind to a stale snapshot, a live
   service, or a saved dated record. Those are not interchangeable even if they concern OFAC.

## Security abuse cases

- A malicious MCP tool falsely advertises the exact semantic id.
- Two plugins claim the same id and one wins by ordering, name, or description injection.
- A source description contains instructions that override acquisition policy.
- A read-looking tool has an undeclared write side effect.
- Permission denial triggers fallback to a less authoritative but available source.
- A namespace owner changes the meaning of an existing id.
- A source id leaks a tenant, case, person, or confidential system name into prompts or telemetry.
- A resolver treats an id as authorization and invokes a tool the application did not expose for
  the current user.
- A record-store binding is mistaken for a current live search, or the reverse.
- “Not found” is converted to a zero-valued fact, as happened in two study cells.

The production threat model must treat the id, description, tool metadata, and retrieved content as
untrusted. Tool authorization and side-effect policy must be enforced outside the model.

## Method threats

- One model family, one client, three repetitions, and eight synthetic scenarios.
- The shared prompt taught the desired safety and absence rules explicitly.
- Distractors often said what they were *not*, making prose selection easy.
- Treatment arms differed in length and salience, not only in an abstract semantic capability.
- Exact `Provides semantic input source identifier` declarations made matching unrealistically
  clean and did not test spoofed declarations.
- Opaque tool names remove helpful cues that real integrations often have.
- Fixed interleaving and backend prompt caching are not a randomized population sample.
- `sourceId` was returned but was not part of registered E1–E7 scoring.
- The strict output schema constrained representable facts to this one study domain.
- All first launches required a documented schema repair. No treatment reached the model in those
  attempts, but the study is less pristine than one that passed its first launch.

## Minimum bar before implementation

- A follow-up study shows a reproducible E2 call-selection advantage, not only mapping changes.
- The experimental schema separates a reusable declaration from references to it and defines
  zero/one/many resolution behavior.
- Names are extensible and non-secret; connector and credential fields are explicitly forbidden.
- Authoring validation detects unresolved references, duplicate local declarations, unsafe ids,
  observation/determination confusion, and accidental executable configuration.
- Runtime/client receipts expose the chosen binding and side-effect class without claiming the id
  authenticated the result.
- Adversarial tests cover false id claimants, description injection, stale/live confusion,
  permission fallback, namespace collision, and undeclared mutation.
- A material spec/runtime proposal receives an independent cross-vendor review against exact
  commits.

## Recommendation

Keep the candidate and harness in the experiments repository. Do not change JPS Core or the stable
runtime yet. If product work needs the idea sooner, expose it behind an explicitly experimental,
client-side authoring convention: the runtime carries the descriptor and receipts but does not
open connections or dereference the id. Revisit standardization only after the discovery-focused
follow-up and external adversarial review.
