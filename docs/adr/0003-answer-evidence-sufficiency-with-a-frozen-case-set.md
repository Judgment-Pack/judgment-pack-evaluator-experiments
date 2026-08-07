---
status: proposed
date: 2026-08-06
deciders: maintainer
---

# Answer the evidence-sufficiency question with a frozen case set before any RFC

## Context and problem statement

Specification issue #47 asks whether Core §8.2's evidence tri-state is enough: `present` says an
item of evidence *exists*, and nothing anywhere says it is *sufficient for what the pack asks*. A
partial contract, a contract with the wrong counterparty, and a superseded contract are all
`present`. The issue's own framing is careful — "not an RFC yet, deliberately" — and it names three
things that would justify one: adversarial cases, a second consumer that independently needs the
distinction, or an observed field failure.

The question is not homeless in the specification, and that constrains any answer. Core §7.5 states
the gap in its own words ("no evidence-manifest interchange format beyond the tri-state of §8.2");
§13 defers "an interchange form for evidence … and whether §8.2 grows into it"; and §3.5 forbids
describing conformance as proof that evidence is authentic **or sufficient** — the line every
candidate design has to hold, and also the strongest argument against a new state. RFC 0003 does not
carve this space; its Compatibility section forecloses it ("no change to the meaning of a
requirement's presence or absence"), so a sufficiency proposal would be a sibling that amends
RFC 0003, not something RFC 0003 absorbs.

So the decision in front of us is not *what to propose*. It is **what would have to be true for a
proposal to be worth drafting, and what is the cheapest honest way to find out**.

## Decision drivers

- **The interesting claim is much narrower than the issue's headline.** That a naive
  artifact-exists-therefore-`present` mapping produces dispositions a careful reader would refuse is
  already known, and this repository already ships the fix:
  [`derivation-rule/rules/screening.rule.json`](../../derivation-rule/rules/screening.rule.json)
  carries subject, freshness, and type clauses, each mapping a failed content check to `unknown`
  rather than to `present`. Re-demonstrating that justifies no change to anything.
- **Only one shape could justify an RFC: requirement-relative sufficiency.** A case whose catching
  predicate is a function of *the pack's own question*, so that an acquisition author who has not
  read the pack cannot write it. That is the one thing a pack-side lever could supply and an
  acquisition-layer convention could not. Everything else is convention, and convention is guidance.
- **The result is deterministic and known by construction.** Given a pack, an availability document,
  and a facts document, the disposition follows mechanically from Core §8. There is no model, no
  encoder, no grader, and no judgment call to blind.
- **The repository's two artifact grammars sort this cleanly.** Numbered studies carry
  preregistration, a freeze, a run log, deviations, and adversarial review because a study's result
  can surprise and its grader can become its own oracle — the circularity
  [ADR-0002](0002-trustworthy-input-acquisition-research-line.md) exists to break. Component
  directories (`acquisition-proxy/`, `derivation-rule/`, `fabrication-gate/`) carry a README, a
  frozen corpus, and a deterministic test wired into CI. Preregistering an outcome computable by
  hand would be theatre; a frozen corpus is the honest form.
- **This is not item 4 of ADR-0002's build order.** That line's three items — attestation core,
  portable derivation rule, receipt-required admission — are complete, and they establish layer 4's
  *fidelity*: the claim is a deterministic function of attested bytes. Issue #47 asks about layer 4's
  *adequacy*: whether the claim's vocabulary can say the thing the pack needs said. Different
  question, so it gets its own record rather than an amendment.

## Considered options

- **A. Draft the RFC and let review find the evidence.** Rejected. RFC 0000's Evidence section wants
  real examples and known implementation experience; drafting first inverts the order the issue
  itself set, and spends a mandatory cross-vendor adversarial review cycle on a question nobody has
  measured. It also drags RFC 0003 into scope, since amending its Compatibility line makes it
  acquire the interim-review debt.
- **B. A numbered study.** Rejected. Preregistration, a freeze digest, blinded grading and an
  adversarial-review record are machinery for a subject that could surprise. Here the outcome is a
  pure function of published semantics. The lightest existing study is still heavier than this needs.
- **C. A component directory with a frozen case set.** Chosen; see below.
- **D. Answer from reading alone and close the issue.** Rejected. The decision variable identified
  below is cheap to measure and expensive to assert, and an issue closed on an assertion reopens.

## Decision outcome

Build `evidence-sufficiency/` at the repository root, in the `fabrication-gate`/`derivation-rule`
grammar: a README, one small realistic pack, a derivation rule, a frozen set of cases, a
deterministic replay, a unittest, and one CI job — plus whatever probe variants of the pack and the
rule the measurement turns out to need, each differing from the original in exactly one thing so the
difference is the finding. Two arms over the same seven cases:

- a **naive arm** — artifact existence mapped straight to `present`, grounded in shipped in-project
  practice rather than invented, with the practices named and each one's bound stated. Where those
  practices disagree about what else the acquisition layer emits, the arm carries a variant per
  shape rather than averaging them, because the disagreement is load-bearing; and
- a **convention arm** — the shipped portable derivation rule
  ([`derivation-rule/`](../../derivation-rule/)) applied to the same artifacts, so the arm is the
  mechanism this project actually ships and not a re-implementation of it.

The case set is fixed before it is built, and it is seven: four divergence-capable cases — a partial
document, a wrong-subject document, a stale document, **right-document-wrong-clause** — plus three
controls — a complete and correct document (so the set cannot be read as rigged toward divergence), a
genuinely absent document, and a complete and correct document signed by someone without authority.

### The measurement, fixed before any case is written

For each case that diverges, a **coupling verdict** on the clause that catches it:

- **pack-independent** — reusable across every pack that consumes this artifact type (a subject
  match, a freshness window, a required-section check); or
- **pack-coupled** — one clause per requirement per pack, whose predicate is a function of *this*
  pack's question.

Coupling is a property of a **clause**, not of a rule, so it must be stated and checked per clause.
A control case that produces no divergence takes the verdict **none**, and a case where a clause
could catch the fixture but nothing can establish that the field it reads is true takes
**unattested** — a label about the ceiling rather than about coupling, kept in the same closed set
so no case can be left unlabelled.

**The reported number is the count of pack-coupled catches, not the count of divergences.** A
divergence count would be inflated by exactly the cases shipped practice already handles, and would
make a foregone conclusion look like a finding.

### The stopping rule, fixed before any case is written

If **right-document-wrong-clause does not reproduce** — if every divergence is caught by a
pack-independent clause, or if the pack-coupled catch turns out to be writable inside a mechanism
this project already ships — then the acquisition convention plus guidance is the complete answer.
The deliverable is then a §7.5 informative note with the case set as its citation, and issue #47
closes as **answered**, not deferred.

That outcome is a result, not a failure, and this record commits in advance to reporting it in those
words rather than as a hedge. It is also the outcome that would be easiest to write around after the
fact, which is why the rule is written down first.

**Two disclosures about this rule, since a pre-registration that overstates itself is worse than
none.** *First*, the second disjunct — "or if the pack-coupled catch turns out to be writable inside
a mechanism this project already ships" — is a **broadening**. The plan this record follows names
only the first disjunct as its stopping point, and grounds the second in a differently-worded
Option-0 condition that points at one specific mechanism (receipt-required admission). Written as it
is here, the disjunct covers any shipped mechanism, and it is the disjunct that actually fires. That
widening is deliberate — a catch writable in *any* shipped mechanism is a catch that needs no new
vocabulary, which is the question — but it is a widening, and reading the outcome as a clean
pre-registered hit would overstate it. *Second*, this record's ordering claim rests on nothing
stronger than file modification times: there is no freeze digest and no commitment ceremony, because
the outcome is a pure function of published semantics and this is a component directory rather than
a numbered study. A reader who wants a checkable freeze should read the result as a derivation from
the bytes, which it is, rather than as a prediction that was sealed.

## What this component deliberately does not show

- **Not efficacy.** Nothing here measures whether anyone decides better, faster, or more correctly.
  Efficacy is a question this project is the wrong author of (repository README; ADR-0002).
- **Not a second consumer, and not a field failure.** Of the issue's three triggers, a frozen case
  set can satisfy only the first. A second, independent consumer cannot be manufactured; the closest
  thing available is the runtime's own graph composition seam, which is the same maintainer's
  runtime and therefore weak on independence exactly as the repository README says such evidence is.
  It is recorded as a mapping with its mitigation named, **never** as a runtime defect report.
- **Not evidence that a new state would be used correctly.** No evaluator can check that a stronger
  token was *earned* — §3.5 forbids the claim outright, and §8.2 admits whatever the caller writes.
  A caller who maps existence to `present` will map existence to whatever is stronger. Any value such
  a token has is interface value: it makes a pack's demand explicit and a caller's mistake nameable.
- **The ceiling is unchanged: byte-lineage, not truth** (ADR-0002). The authority control exists so
  the case set cannot be read as claiming a richer vocabulary buys correctness.
- **No conformance claim.** As with everything in this repository, nothing here claims JPS
  conformance and no disposition is an authorization, a decision, or an executed action.

## Consequences

- The decision to draft or not draft an RFC becomes a reading of one mechanical number against one
  written-down rule, instead of an argument.
- The case set is worth having whichever way it lands: as a regression surface over the clean-room
  Python evaluator's §8 behaviour — the only implementation this repository executes; the Go runtime
  lives in another repository and neither this directory nor its CI job runs it — and as the citation
  an informative note would need.
- Two boundaries are accepted deliberately. **First**, `derivation-rule/SPEC.md` is not amended here.
  Its condition vocabulary has no content predicate over text, so a content-sensitive case is
  expressible only where the acquired artifact is already a structured extraction — which relocates
  the sufficiency judgment into an extraction hop outside the attested chain, precisely the "model in
  the proof path" failure ADR-0002 forbids. That is a **finding to record with its exits**, not a gap
  to patch: a clean-room second implementation in Go is built from that document, and editing it
  would invalidate the agreement result for no benefit to this question. **Second**, this phase needs
  no cross-vendor adversarial review — it creates no RFC and changes no runtime behaviour — but any
  RFC it eventually informs carries that review mandatorily, and must budget it to cover the RFC 0003
  amendment as well.
- Cost if the stopping rule fires: one directory and one CI job, which stay useful. Cost if it does
  not: the same directory, plus a drafting phase entered with evidence instead of an intuition.

## More information

Specification issue #47; Core §3.5, §7.5, §8.2, §8 step 2, §13; RFC 0003 (evidence reference, Draft)
and its Compatibility section; RFC 0000's Evidence and Implementation sections; GOVERNANCE's decision
principles. Builds on [ADR-0002](0002-trustworthy-input-acquisition-research-line.md) and the three
components its build order produced.

**Revision note.** This record was written before any case, and then revised before its first commit
in response to an adversarial read of the finished directory. Four sentences the directory did not
keep were brought back into line: the case-set enumeration (six items under a "seven cases" heading,
missing the complete-and-correct control); the regression-surface claim (narrowed to the one
implementation this repository actually executes); the closed set of coupling verdicts (which the
directory needed two more labels for); and the description of the deliverable (which acquired probe
variants of the pack and the rule). The two disclosures on the stopping rule were added in the same
pass. Authorship before the first commit is authorship — the frozen-oracle discipline binds published
bytes — so the revision is recorded here rather than left to be inferred from the absence of a diff.
