---
status: proposed
date: 2026-07-30
deciders: maintainer
---

# Open a trustworthy-input-acquisition research line: the trust decomposition and build order

## Context and problem statement

Studies 005–007 pivoted the experiments repository away from the *representation* question
(001–004: can a policy be expressed as a pack?) toward an *acquisition* question: **where do a
pack's inputs come from, and what makes them trustworthy?** They produced three real results and one
methodological flaw, and this record is written before the next artifact so the flaw is not
repeated.

What the three studies established, in their own careful language:

- **Source selection is not the weak link.** Study 005's MCP source-call correctness was 24/24 in
  both arms; the registered composite difference (23/24 vs 20/24) came entirely from downstream
  mapping, and the study's own conclusion is "evidence against implementing the proposal now"
  (005 ANALYSIS.md). The question "which source did the agent pick" turned out already solved.
- **The weak link is what the agent *claims the source said*.** In both of 005's arms, exactly one
  cell converted a `not_found` result into the fabricated fact `matchCount: "0"`. Study 006 promoted
  this to a standing threat-model item and built a deterministic lineage gate against it: a
  syntax-only policy accepted 8/8 registered tampers, the gate accepted 0/8.
- **Classification competence and transcription competence dissociate.** Study 007 had the model
  author the lineage envelope: facts, evidence availability, acquisition status, and source
  reference were exact in **24/24**, while all three admission failures were *lineage authoring*
  errors — one hex-digit digest typo and two JSON-pointer slips. The model reads the source and
  decides the fact well; it carries bytes, digests, and pointers un-trustably. The study's own
  reading: "the model should not author the lineage envelope at all."

The methodological flaw, which this line exists to correct: in 006/007 a single hand-written function
(`derive_payload`) is simultaneously the ground-truth oracle, the control-candidate builder, the
grader, and the source of the stage labels — and the prompt states its rules to the model verbatim.
Study 006's D3 therefore tests that a pure function equals itself; Study 007's model score grades
the model on reproducing a private classifier it was handed the rules to. Every high-value objection
to these studies traces to the same root: **there was no independent specification the artifact could
be checked against.** The correction is not a faster next artifact; it is a reviewable decomposition
first, so each build has an external contract to conform to — the same discipline the project already
applies as preregistration, spec-before-implementation, and two-independent-implementation agreement.

## Decision drivers

- The project's own two-track split (README): conformance/agreement evidence is something a
  specification project is the *right* author of; efficacy evidence it is the *wrong* author of, and
  the only remedy is method. This line's artifacts must fall cleanly on one side or the other.
- The runtime's arm's-length posture is correct and load-bearing: it holds no credential, opens no
  connection, resolves no source (ADR-0004, ADR-0006), and its evidence model is an identifier plus a
  tri-state with no data reference at all (ADR-0012). Nothing here may erode that.
- The spec already reserves the seams this touches: RFC 0003 (evidence reference, Draft) proposes "a
  requirement identifier plus an optional typed selector" and states "a reference is an identifier,
  not a URL to auto-dereference"; Core §13 defers "content identity, canonicalization, and
  signatures" and "content-addressed dependencies." This line supplies evidence those seams can weigh,
  never a change it makes.

## The guarantee ceiling

Stated first, because it disciplines everything downstream. From Study 006: "SHA-256 proves byte
identity. The study HMAC proves that the fixture gateway issued a receipt. Neither proves factual
truth." **You cannot guarantee a fact is true. You can guarantee byte-lineage**: that the fact the
pack evaluated derives, by a checkable rule, from bytes a named party attested at a known time. That
ceiling is not a limitation to apologize for — byte-lineage is exactly what kills the three failures
that actually occur: fabrication (`not_found → "0"`), tampering (a byte changed after acquisition),
and stale substitution (a current pointer over an expired artifact). No document in this line may let
"trustworthy" drift to "correct."

## Decision outcome

Adopt a trustworthy-input-acquisition research line built on one principle and one decomposition.

**The principle: structurally exclude the model from the proof path.** Study 007 is the evidence.
The model gathers and narrates (labor, non-normative, best-effort); a deterministic component produces
and verifies the proof. This is stronger than "the model authors an envelope we then check" — that is
precisely what 007 showed failing 3/24. The model never touches the chain.

**The decomposition: five distinct guarantees, three owners.** The studies conflated these under one
gate; naming them is the first advance, because they have different owners and different evidence
standards.

| # | Guarantee | What it asserts | Owner |
| --- | --- | --- | --- |
| 1 | **Binding** | This input pointer/requirement is authorized to be sourced from source S, before any fetch | Portable (RFC 0003 seam) + product |
| 2 | **Acquisition proof** | Bytes B were returned by S at time T (receipt: who, when, digest(B)) | Product-side, experimental |
| 3 | **Retention** | B is kept, content-addressed, so the derivation is auditable | Product-side, experimental |
| 4 | **Derivation fidelity** | Fact F = d(B) by a *declared, deterministic* rule d | **Portable + independently implementable** |
| 5 | **Admission** | The pack evaluates F only if 1–4 verify | Product-side gate → the runtime evaluates the admitted value |

The runtime owns only admission's downstream half — it evaluates a value already verified, upstream of
nothing. Acquisition, credentials, retention, and the gate are product-side and experimental, exactly
where Study 006 put them and exactly where the studies concluded they should stay ("do not yet add its
bytes to JPS Core or make the stable runtime resolve source identifiers").

**Layer 4 is the high-value item, and the anti-circularity requirement lives here.** If the
bytes→claim rule is *coded once* (as `derive_payload` is), it can only ever be checked against itself.
If it is *declared portably*, a second implementation can be written clean-room from the declaration
alone and tested for agreement — which breaks the circularity by construction and makes derivation
fidelity conformance-testable the way the evaluator already is (the `python/` agreement track is the
standing precedent). A portable, independently-implementable derivation rule is what converts this
whole line from "we built a thing and checked it against itself" into evidence.

**On mechanisms, including MCP skills.** A skill is context, not control — the same trust category as a
`jpack.json` hint or a prompt, model-invoked and model-interpreted (the operator's own Codex skills
leaked into the model's context in roughly a third of the study cells, which is the point: a skill is
context the model sees, not a boundary it obeys). A skill can reliably *drive* the model toward the
attested path; it can never *be* the guarantee. The deterministic proof layer must be one of:

- a **receipt-stamping MCP proxy** — a generic shim wrapping any MCP tool with transparent,
  content-addressed attestation, invisible to model and source, replacing the bespoke per-domain
  gateway with one general trusted component;
- **signed evidence bundles** — the gateway signs {digest, timestamp, claim} and the gate verifies
  (Core §13's deferred "content identity … and signatures");
- **content-addressed artifacts surfaced as MCP resources** — the retained bytes read-only at a
  hash-named URI, so the artifact store is the resource layer.

**Deployment shape: inline first, gateway as target.** The attestation core is the same mechanism
whether it runs *inline* — a stdio proxy wrapping one downstream MCP server, one process per client,
a key per instance — or *hosted* — a gateway fronting many sources over the network, one signing
identity, central binding policy. The gateway is the deployment target for scale, and its single
attestation authority is a cleaner trust root than a fleet of per-proxy keys; but it is not item 1.
A network gateway adds attack and operational surface the byte-lineage guarantee does not need in
order to be established, and because the guarantee is identical in both shapes, it is established
most cheaply inline. Two requirements bind whichever shape ships, and neither is about scale: the
attestation boundary MUST sit at the point of source contact — a hop that carries bytes before they
are stamped is exactly where tampering re-enters — and the attestation authority MUST be nameable
and auditable. Establish the guarantee inline; host it as a gateway once it holds.

**Build order.** Deliberately not a re-run of Study 005 first: 005 is an honest null on a question that
turned out to be the wrong one, and polishing it advances nothing.

1. **The attestation core — content-address, attest, retain, exclude the model — built
   deployment-shape-agnostic** (product artifact). Established inline as a stdio proxy because that
   is the smallest testable trusted base, and designed to be hosted as a gateway (above) once the
   guarantee holds. Replaces the synthetic per-domain gateway with one general trusted component and
   makes every later study's trust boundary real rather than a fixture. This is the largest single
   strengthening available.
2. **The portable derivation-rule declaration + a clean-room second implementation** (spec seam +
   agreement track). Breaks the 006/007 circularity and makes layer-4 fidelity conformance-testable.
3. **A focused study: does receipt-required admission eliminate fabrication?** The `not_found → "0"`
   fabrication is the only observed failure that produces a confident wrong *decision* rather than a
   rejected envelope. The property to test: a fact cannot be `present` unless a receipt exists for an
   artifact that contains it. If it holds, it is the strongest demonstration this line can make — and
   it rests on the proxy of item 1, which is why the proxy comes first.

The rigor cleanups on 005–007 (paired statistics beside every bolded outcome, the unlogged
skills-context contamination, the D1/D2 decompositions, the gitignored `0.0.0-dev` evaluator binary)
are worth doing but are corrections to existing evidence, not advances on the question; they are
tracked separately and do not gate this line.

## Consequences

- The next artifacts have an external contract (this decomposition) to conform to, so a later study's
  ground truth is no longer allowed to be its own grader.
- Item 2 puts a genuinely portable, independently-testable claim (derivation fidelity) into the
  agreement track, where the project is the right author — distinct from the efficacy claims it is the
  wrong author of.
- The interim-review requirement the studies impose on themselves ("any material runtime ADR or
  specification RFC amendment informed by it requires the repositories' own commit-relative,
  cross-vendor adversarial review") applies to anything this line eventually informs, and is currently
  undischarged for 005–007; this record does not discharge it and cites nothing normative on that
  evidence.

## What this does not do

It standardizes nothing, changes no stable-runtime behavior, and adds no member to any format. It does
not claim byte-lineage implies truth, completeness, currency, or legal sufficiency — only that an
admitted fact derives from attested bytes. It licenses no JPS or RFC change on its own; it is a
research direction and a build order, and the studies it schedules are efficacy/expressiveness
evidence the specification project is the wrong author of, run under method or not run at all.

## More information

Builds on studies 005 (semantic source discovery), 006 (evidence lineage gate), and 007 (evidence
lineage model replication). Relates to spec RFC 0003 (evidence reference) and Core §13's deferred
content-identity work. The runtime's non-acquisition posture: ADR-0004, ADR-0006, ADR-0012.
