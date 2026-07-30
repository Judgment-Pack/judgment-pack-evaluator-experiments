# Study 004 results — composition closure

Computed exactly as preregistered, from the frozen frame
([`frame/adjudicated.json`](frame/adjudicated.json)), the feature labels
([`frame/feature-pass.json`](frame/feature-pass.json)), five audited encoding rooms
([`rooms/`](rooms/)), the mechanical harness ([`harness/`](harness/)), and a two-classifier
measurement pass with adjudication ([`measurement/`](measurement/)). Treatment, digests, audits,
and cluster derivation: [`run-log.md`](run-log.md). Encoders were hypothesis-blind (neutral
briefs, isolated rooms, transcripts audited with zero flags).

## The preregistered numbers

| Metric | Value |
| --- | --- |
| **G1 (primary): closed frame items** | **0 of 5** (Unit F: 0 of 0 — no ratio; Unit R: 0 of 5) |
| G2: primary devices over partial + open | `needs-effect-or-entitlement` 4 · `other (action-completion)` 1 |
| G3: graphs validating / evaluations run / byte-identical repeats | 5/5 · 20/20 · 20/20 |
| G4: new residue sentences (verbatim, deduplicated) | 18 ([`measurement/g4-new-residues.json`](measurement/g4-new-residues.json)) |
| Measurement inter-rater: verdict disagreements | **0** |
| Measurement inter-rater: device disagreements | 2 (adjudicated) |
| Predictor accuracy | 3 of 5 (both misses in the scalar branch) |
| Predictor aggregate (largest device = `needs-effect-or-entitlement`) | hit (4 of 5, strictly largest) |

Per item:

| Item | Clause | Feature label | Predicted | Verdict | Primary device |
| --- | --- | --- | --- | --- | --- |
| A1 3 | "is not refundable" | non-scalar | not closed | **open** ✓ | needs-effect-or-entitlement |
| A1 7 | "enables full refund if the user needs to cancel…" | non-scalar | not closed | **open** ✓ | needs-effect-or-entitlement |
| A3 4 | "should be refunded the difference" | non-scalar | not closed | **open** ✓ | needs-effect-or-entitlement |
| A7 2 | "changing or cancelling the reservation" | scalar-status | closed | **open** ✗ | other (action-completion; fan-in) |
| R3 1 | "will not be able to modify or cancel the order anymore" | scalar-status | closed | **open** ✗ | needs-effect-or-entitlement |

## Finding 1 — the grammar closed nothing, by five independent refusals to declare

Every room produced a **validating graph with zero edges**. No encoder failed to make an edge —
each concluded, blind to the hypothesis and in its own words, that the policy's cross-decision
sentences cannot be *faithfully* declared by an edge that injects an upstream outcome id: the
rooms' residue logs describe decisions related through shared reservation facts rather than
outcome consumption, entitlements that modify a later decision's rules rather than its inputs,
and — twice, independently — the gap between a decision's *permission* and an act's
*performance*. One room went further and demonstrated that the two candidate edges it could
declare **validate at exit 0 while inverting the policy's meaning** (and forging the downstream
pack's confirm-the-facts attestation). Validity is not fidelity, and the verdict procedure's
live-edge requirement is what kept that distinction measurable.

## Finding 2 — the predictor's scalar branch failed for one nameable mechanism

The registered predictor was right about every non-scalar item and wrong about both scalar
ones, and both misses share a mechanism the feature pass itself flagged in advance as a
judgment call: the upstream outcomes are **eligibility findings, while the downstream facts
assert completed acts**. An outcome-id edge injects "permitted" where the pack reads
"performed" — one room probed evaluation and showed the injection *denies cancellation exactly
when a modification was refused*. The aggregate device prediction hit
(`needs-effect-or-entitlement`, 4 of 5), so the predictor's picture of *what* blocks closure
was right; its picture of *when* scalar consumption suffices was not — scalar consumption of a
verdict is not scalar consumption of an act.

## Finding 3 — in this frame, the cross-decision escape is not a dataflow seam

The composition this grammar offers — one decision's outcome feeding another's inputs — is not
the relationship these two policies exhibit between their own decisions. Their cross-decision
sentences are forward entitlements, terminality effects, and act-coupled compensations: they
change what a later decision *may conclude*, not what it *reads*. The screening-style seam the
grammar does express (a verdict consumed as a scalar status) did not occur once inside either
policy's frozen inventory; where it occurs in practice is *between* systems — an upstream
decision recorded for a downstream document — which is the seam the runtime's own demo
dramatizes and which this frame, by construction, cannot contain. The 18 new residue sentences
(G4) are consistent: compensation-eligibility couplings, once-only tool constraints, and
status-lifecycle effects, not consumable verdicts.

## What this licenses, and what it does not

For [RFC 0002](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0002-judgment-graph.md):
measured evidence that an outcome-id edge grammar closes **none** of this frame's cross-decision
residue, with the blocking constructs named and counted — an effect/entitlement device (4 of 5),
action-completion facts, disjunctive fan-in, and outcome-value mapping. That is evidence about
*this grammar over this frame*, exactly as preregistered: neither this zero nor any other G1
licenses a claim about composition as a design class, other grammars the RFC could adopt, other
corpora, authoring efficacy, policy correctness, or operational outcomes. A grammar with
entitlement edges, completion facts, or richer feeds might close more; a different corpus (or
the between-systems seam) might present the dataflow shape this grammar serves. No efficacy
claim, as ever: this measures what a composition format can hold, not whether composing helps.

## Reproducing

Rooms (graphs, residue logs, briefs, re-declared packs): [`rooms/`](rooms/). Harness inputs,
construction logs, and byte-compared evaluations: [`harness/`](harness/). Classifier raw
judgments and the adjudication: [`measurement/`](measurement/). Every graph:
`jpack experimental graph validate rooms/<room>/relationships.graph.json --config
rooms/<room>/jpack.json` → exit 0 under the pinned binary recorded in
[`run-log.md`](run-log.md).
