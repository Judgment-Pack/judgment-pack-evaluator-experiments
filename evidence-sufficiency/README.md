# Present vs. sufficient — the evidence-sufficiency case set

The evidence for specification issue #47, built under
[ADR-0003](../docs/adr/0003-answer-evidence-sufficiency-with-a-frozen-case-set.md) and answering the
question it fixed in advance: **is Core §8.2's tri-state enough?** `present` says an item of evidence
*exists*. Nothing anywhere says it is *sufficient for what the pack asks* — a partial contract, a
contract with the wrong counterparty, and a superseded contract are all `present`.

ADR-0003 fixed the measurement and the stopping rule before any case was written, because the
outcome is computable by hand and would otherwise be easy to write around afterwards. Both are
reproduced below, and [the verdict](#the-verdict) is reported against them in the words the ADR
committed to.

## The two arms

One small pack whose decision turns on a required, signed agreement, and two ways of telling that
pack whether the agreement is there:

| Arm | What it is |
| --- | --- |
| **Naive** | [`naive.py`](naive.py) — artifact existence mapped straight to an availability state. It reads the one field that says a document came back and no field of the document's content, so nothing about the agreement's subject, currency, completeness, or terms can change the answer. It comes in two variants, because the practices it models do: a **plain** variant that emits an availability document and no facts, and a **credulous** variant that also asserts the fact the pack asks about, from existence alone. |
| **Convention** | [`rules/agreement.rule.json`](rules/agreement.rule.json) run through the shipped portable derivation rule ([`../derivation-rule/`](../derivation-rule/), ADR-0002 item 2). The arm **is** the mechanism this project ships, not a re-implementation of it. |

Both arms feed the same pack, and the disposition comes from the clean-room Python evaluator in
[`../python/`](../python/). Given a pack, a facts document and an availability document, Core §8
fixes the answer, and every other number reported here is computed from the frozen bytes too — see
[what the requirement demands](#what-the-requirement-demands), which is the one place a reader could
reasonably disagree and where that disagreement is spelled out.

### Where the naive arm comes from

The naive arm has to be a practice, not a straw man. Three shipped in-project instances, strongest
first, each with its bound stated — and note which variant each one grounds, because they do not all
have the same facts behaviour:

1. **The runtime's graph composition seam.** `internal/graph/document.go`'s `EvidenceFeed.State`
   returns `"present"` for *any* upstream disposition of kind `outcome`, whichever outcome it was,
   and `internal/graph/coverage.go` narrows an edge-fed requirement's state set to exactly
   `{"present", onUnresolved}`. A downstream requirement therefore reads `present` because a
   determination exists upstream — including an upstream denial. This is the cleanest mechanical
   existence→`present` mapping the project ships. **Bound, and it matters:** the runtime's own
   doc comment says this is the intended reading ("`present` for an outcome"), and the mitigation is
   that a pack author who cares *which* outcome also authors the fact edge and writes a rule over
   the upstream outcome id. It is recorded here as a mapping worth testing with its mitigation
   named, **not** as a runtime defect, and no issue is opened off it. *Grounds the plain variant*
   for an edge that declares only an `evidence` feed — an `Edge` "feeds one upstream node's
   disposition … as a fact, as evidence availability, or both", and the availability-only edge is
   the one with no facts.
2. **The Slack demo's drafting contract**, where a model emits the availability document directly,
   with no sufficiency step at all. **Bound:** that is a demo scenario generator, not a production
   acquisition layer. It evidences how cheap the mapping is to reach for, not a field failure.
   *Grounds the credulous variant*, and this is the correction that matters: `DRAFT_CONTRACT` asks
   for `"facts": { … the nested facts document for that scenario … }` and
   `"evidence": {"<id>": "present"|"absent"|"unknown"}` **in the same JSON object**. The strongest
   cited practice emits facts, so a claim that the naive arm never emits facts would be false of it.
3. **Hand-authored availability fixtures** across the demo projects and their scenario matrices.
   *Grounds the plain variant*: an availability fixture is an availability document by construction.

`naive.py` therefore carries both, and both are probed. Nothing in this directory claims the naive
arm as a whole emits no facts; the claim is about `naive_facts`, and `credulous_facts` is the arm
that models the practice which does.

## The case set

Seven frozen cases in [`cases/`](cases/), each carrying its artifact, the derivation parameters, the
availability document each arm produces, the derived claims, the requirement-demand table, and every
disposition — regenerated and diffed by [`replay.py`](replay.py), and asserted cell by cell against a
second, hand-written oracle in [`test_replay.py`](test_replay.py).

| # | Case | Naive arm | Convention arm | What the requirement demands | Unsupported release? | Catching clause |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | **Control — complete** | `outcome:release` | `outcome:release` | executed, current, right counterparty, onward transfer granted — all met | — | none |
| C1 | **Partial document** | `outcome:release` | `unresolved{unknown}` + handoff requested | an agreement **executed by both parties** | naive only | pack-independent |
| C2 | **Wrong subject** | `outcome:release` | `unresolved{unknown}` + handoff requested | an agreement **with this counterparty** | naive only | pack-independent |
| C3 | **Stale document** | `outcome:release` | `unresolved{unknown}` + handoff requested | an agreement that is **current** | naive only | pack-independent |
| C4 | **Right document, wrong clause** | `outcome:release` | `outcome:release` | a schedule that grants **onward transfer** | **both arms** | pack-coupled |
| C5 | **Control — genuinely absent** | `unresolved{missing-required-evidence}` + handoff requested | `unresolved{missing-required-evidence}` + handoff requested | an agreement to exist at all | — | none |
| C6 | **Control — authority ceiling** | `outcome:release` | `outcome:release` | an agreement **executed by both parties** — which an unauthorised signature does not achieve | **both arms** | unattested |

*Unsupported release* means a disposition of `outcome:release` on an artifact the requirement's own
description does not cover. That, not bare divergence between the arms, is what makes a row a
failure — and "does not cover" is computed, not asserted; see below.

The **Catching clause** column reports the coupling verdict on whatever clause would catch the row.
`unattested` is C6 and is not a coupling verdict: a clause *can* catch that fixture
(`isTrue /signatoryHadDelegatedAuthority`, pack-independent in shape, and a test in this directory
writes it and shows it catching). What no clause reaches is whether the field it reads is *true*.
The catch is available; the truth is not.

Three probes run over the same cases, all using mechanisms that exist today:

| # | + one pack-coupled clause | The clause stated as a Core fact condition | The fact-conditioned pack, plain naive arm | The fact-conditioned pack, credulous naive arm |
| --- | --- | --- | --- | --- |
| C0 | `outcome:release` | `outcome:release` | `unresolved{unknown}` + handoff requested | `outcome:release` |
| C1 | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `outcome:release` |
| C2 | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `outcome:release` |
| C3 | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `unresolved{unknown}` + handoff requested | `outcome:release` |
| C4 | `unresolved{unknown}` + handoff requested | `unresolved{no-match}` + handoff requested | `unresolved{unknown}` + handoff requested | `outcome:release` |
| C5 | `unresolved{missing-required-evidence}` + handoff requested | `unresolved{missing-required-evidence}` + handoff requested | `unresolved{missing-required-evidence}` + handoff requested | `unresolved{missing-required-evidence}` + handoff requested |
| C6 | `outcome:release` | `outcome:release` | `unresolved{unknown}` + handoff requested | `outcome:release` |

The first probe adds one clause to the derivation rule
([`rules/agreement-coupled.rule.json`](rules/agreement-coupled.rule.json)); the second states the
same predicate inside the pack instead ([`pack/release-clause-fact.json`](pack/release-clause-fact.json)),
which is the only difference between the two packs; the third runs that pack against the two naive
variants — the plain one, which omits the fact, and the credulous one, which asserts it.

### What the requirement demands

Both packs carry one evidence requirement whose description reads: *"The data-sharing agreement with
this counterparty, executed by both parties and current, whose executed schedule grants onward
transfer of the requested dataset to this counterparty."* That sentence decomposes into five checks,
and `replay.py` computes every one of them from the artifact's own bytes and the acquisition
parameters. `requirementSatisfied` is their conjunction, and the *Unsupported release?* column above
is that conjunction and nothing else — the headline measure has no hand-set input.

| # | on file | with this counterparty | executed by both parties | current | grants onward transfer | Requirement satisfied? |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | yes | yes | yes | yes | yes | yes |
| C1 | yes | yes | **no** | yes | yes | **no** |
| C2 | yes | **no** | yes | yes | yes | **no** |
| C3 | yes | yes | yes | **no** | yes | **no** |
| C4 | yes | yes | yes | yes | **no** | **no** |
| C5 | **no** | yes | **no** | **no** | **no** | **no** |
| C6 | yes | yes | **no** | yes | yes | **no** |

**What would make a reader disagree.** The decomposition is a reading of an English sentence, and
two of the five checks are readings a careful person could take differently:

- **"executed by both parties"** is read here as *an execution block is present **and** the
  counterparty's signatory could bind the counterparty*. A reader who holds that two signatures
  execute a contract regardless of authority would score C6 as satisfied, which would remove C6 from
  the unsupported-release column — and would also make the C6 control say something weaker.
- **"current"** is read here as *inside the acquisition's freshness window* (`asOf`,
  `maxAgeSeconds`), because that is the only currency signal the artifact carries. A reader who
  holds that currency is the pack's demand rather than the acquisition's parameter would want the
  window stated in the pack, and would score C3 differently if the pack chose a different window.

The other three (`on file`, `with this counterparty`, `grants onward transfer`) are unambiguous from
the bytes. **C4's result is robust to both disagreements**: C4 fails only `grants onward transfer`,
which the requirement states in words, and neither reading touches it.

## The measurement

ADR-0003 fixed the reported number as **the count of pack-coupled catches, not the count of
divergences** — a divergence count would be inflated by exactly the cases shipped practice already
handles.

- **Divergences between the arms: 3** (C1, C2, C3), every one caught by a **pack-independent** clause
  — a required-section check, a subject match, a freshness window. The shipped
  [`../derivation-rule/rules/screening.rule.json`](../derivation-rule/rules/screening.rule.json)
  already carries all three clause shapes, mapping each failed content check to `unknown`. These
  cases re-demonstrate a convention this repository shipped; on their own they justify nothing.
- **Pack-coupled catches: 1** (C4), out of the four divergence-capable cases.

### The coupling verdict, stated and checked per clause

Coupling is a property of a **clause**, not of a rule, so every sentence below is about one clause
and is asserted at that granularity. A derived claim's `basis` is cumulative over clauses
`0 … matchIndex` ([SPEC.md](../derivation-rule/SPEC.md)), so no statement about a whole rule can be
read off it; `replay.clause_reads()` instead runs each clause on its own and unions the pointers it
resolves over every case in the set, which is what the tests assert.

- **The clauses that catch C1, C2 and C3 are pack-independent.** Their `when` conditions resolve
  `/sections/executionBlock`, `/counterpartyLegalName` and `/observedAt` (plus `/status`) and nothing
  else: a required-section check over the document type, a subject match parameterised by the
  acquisition, a freshness window parameterised by the acquisition. Each is reusable across every
  pack that consumes this artifact type.
- **No clause of [`rules/agreement.rule.json`](rules/agreement.rule.json) resolves or names
  `/executedGrants/onwardTransfer`** — not in a `when` condition, and not as a fact entry's `from`.
  The string `onwardTransfer` does not occur anywhere in the file, and a test asserts that too,
  because it is the claim a reader actually wants and it is strictly stronger than any argument from
  `basis`. (An argument from `basis` alone would be *unsound* here: `basis` records only the pointers
  a leaf op resolved in a `when` condition, so a rule can read a field through `claim.facts` without
  it ever appearing there. That is why the fact transport is stated separately below rather than
  folded into this bullet.) What the rule does do is carry that field's *value* onward — it carries
  every field's value onward, because it copies the artifact whole.
- **Its `resolved` clause transports the artifact whole.** The single facts entry is
  `{"pointer": "/agreement", "from": ""}` — an RFC 6901 empty pointer, so the projection copies the
  acquired artifact and names no field of it. The acquisition author does not have to know which
  field this pack, or any pack, will ask about.
- **Exactly one clause of [`rules/agreement-coupled.rule.json`](rules/agreement-coupled.rule.json)
  reads it** — the added clause, `reason: "grant"`. Which grant matters is a function of *this*
  pack's question: a sibling pack over the same agreement (may we invoice under it, may we retain
  past termination) needs a different pointer. That is one clause per requirement per pack, and an
  acquisition author who has not read the pack cannot write it.

**The residue of coupling that remains, stated rather than claimed away.** The whole-artifact
projection lands under one name, `/agreement`, and the pack's fact condition addresses
`/agreement/executedGrants/…`. So the acquisition author and the pack author do share one thing: a
name for the artifact type. That is a namespace convention over *artifact types*, not knowledge of
*questions*, and it is the kind of convention this project already expects. It also has a price
worth naming: a projection that hands over the whole artifact discloses more than a pointed one
would. Coarser and pack-blind is the trade, and it is deliberate.

## The verdict

**C4 reproduces — and a caveat changes what it licenses.**

**It reproduces.** Under the naive mapping *and* under the pack-independent convention arm, the pack
reaches `outcome:release` on an agreement whose executed schedule does not grant the transfer the
requirement's own description demands. It is the only such row among the divergence-capable cases,
and its catching clause is pack-coupled. The first half of the claim ADR-0003 set out to test holds:
there is a failure the shipped screening-rule pattern does not reach, and a convention author cannot
fix it without reading the pack.

**The caveat, demonstrated rather than asserted.** That predicate is expressible today, in Core, with
**no vocabulary change** — as a fact condition in the pack. Under the same convention arm, the
fact-conditioned pack refuses C4 (`unresolved{no-match}` + handoff) where the evidence-only pack
releases. And the fact route is better in one direction and not in another; both halves are frozen
cells rather than arguments about them:

- **The pack-coupled knowledge really does move from the acquisition author into the pack.** The
  `conventionClauseFact` column is produced by `rules/agreement.rule.json` — the rule whose clauses
  read no pointer this pack chose, whose fact transport is a whole-artifact projection, and which
  never names the grant. So the refusal of C4 is reached by a derivation authored without reading
  the pack: the knowledge of which grant matters lives in the pack's `fact` condition and nowhere
  else. That is the cell, and `test_the_fact_route_needs_no_pack_knowledge_in_the_acquisition_layer`
  asserts both halves together.
- **The failure mode inverts for one of the two ways an acquisition layer gets this wrong, and only
  one.** Under the evidence-only pack, an acquisition layer that never checks sufficiency fails
  **open** — a silent release, and nothing in the evaluator can see it. Under the fact-conditioned
  pack the same **omission** fails **closed**: the plain naive arm supplies no such fact, the pointer
  does not resolve, and every row it released on becomes `unresolved{unknown}` + handoff (the third
  probe column). But an acquisition layer that **asserts** the fact it never checked fails open
  again: the fourth probe column runs the credulous naive arm — the shape the Slack demo's drafting
  contract already permits — and it releases on every row the plain naive arm released on, C4
  included. Safety against *omission* no longer depends on the acquisition author having read the
  pack. Safety against *assertion* never did, and cannot: §3.5 forbids reading conformance as proof
  that evidence is sufficient, and a fourth availability token would be asserted exactly as freely
  as this fact is.

So what C4 demonstrates is a pack that has **under-specified its own question** — an authoring
failure with a shipped remedy — rather than a missing value in §8.2's tri-state. The fabrication mode
the fourth probe column shows is the same ceiling a new token would hit, which strengthens rather
than weakens the reading. Against ADR-0003's stopping rule ("if the pack-coupled catch turns out to
be writable inside a mechanism this project already ships"), the rule fires, and the recorded reading
is the guidance outcome: a §7.5 informative note citing this directory, and issue #47 closed as
*answered* rather than deferred.

**Three residuals, stated so they can be weighed rather than dismissed.** All are asserted as tests,
not as prose:

1. **The fact route is safe but coarse.** It cannot distinguish "the sufficiency fact was never
   supplied" from "the agreement is genuinely unknown" — both are `unresolved{unknown}`. That
   collapse is exactly the distinction issue #47 asks for, and Core still cannot make it. Nothing in
   this case set shows the distinction is *needed*; it shows only that it is *absent*.
2. **§8 step 2 is untouched.** Nothing lets a pack *demand* that a sufficiency check happened. The
   fact-conditioned pack is safe because its author chose to write the condition; a pack that writes
   only `evidence-present` gets C4's silent release, and no evaluator flags it. That is an
   authoring-discipline residual, which is why the deliverable it supports is guidance.
3. **The fact route closes omission and not assertion.** The fourth probe column is that residual as
   a row. It is not a reason to prefer the evidence-only pack — that one is open to both modes — but
   it does bound how much the fact route buys.

This directory supplies the number and the counter-example. It does not decide whether those
residuals, weighed against a breaking change to a conformance vocabulary in two implementations plus
a frozen corpus, are worth an RFC — and it cannot, because the second consumer that would settle it
is the one thing a case set cannot manufacture.

## A finding recorded, not fixed

Both C1 and C4 are expressible **only because the acquired artifact is already a structured
extraction** (`sections`, `executedGrants`). `../derivation-rule/SPEC.md`'s condition table admits
`always`, `exists`, `equals`, `equalsParam`, `isTrue`, `isDecimalString`, `freshWithin`, `all`, `any`
and `not` — and **no content predicate over text**. On a PDF or a prose agreement the *convention*
arm cannot run at all: every clause that could catch anything reads a field the extraction created.
The naive arm, by contrast, runs unchanged — it reads only `/status` — and answers `present`, which
is the worse half of the problem: the sufficiency judgment relocates into an extraction hop outside
the attested chain, which is precisely the "model in the proof path" failure ADR-0002 forbids, and
nothing downstream can see that it happened.

Two exits, neither taken here: extend the rule vocabulary with a content predicate, or attest the
extractor's output as the artifact. `SPEC.md` is deliberately **not** amended — a clean-room second
implementation in Go is built from it, and editing it would invalidate the agreement result for no
benefit to this question. A test in this directory asserts that no rule here uses an op outside the
shipped vocabulary, so the finding cannot be quietly papered over.

## Two authorship notes

Both are here because the frozen-oracle rule binds *published* bytes, and authorship before the first
commit is authorship — so corrections made in that window are disclosed rather than hidden.

- **A fixture was corrected before the first commit.** C3's stale document was originally observed
  (`2026-03-01`) two months *before* its own execution block said it was signed (`2026-05-04`) — a
  row that cannot exist. It was regenerated with possible dates (signed `2026-01-15`, observed
  `2026-03-01`) preserving its stale-window semantics exactly: still outside the 30-day window as of
  `2026-08-06`, still caught by the same `freshWithin` clause, same disposition in every column.
  `test_no_fixture_is_internally_impossible` now asserts the property for every case.
- **The case bytes were regenerated once, and never to paper over a result.** `replay.py` ships with
  no `--freeze` or `--write` mode by design, so the frozen bytes cannot be rewritten from a failing
  run. Every regeneration in this directory's history was accompanied by the hand-written oracle in
  `test_replay.py` being updated by hand and independently derived from Core §8 — which is the point
  of having two oracles.

## What this does not show

- **Not efficacy, and not a field failure.** Of the three triggers issue #47 names, a frozen case set
  can satisfy only the first (adversarial cases). No second, independent consumer is claimed: the
  closest thing available is the runtime's own composition seam, which is the same maintainer's
  runtime and therefore weak on independence exactly as the [repository README](../README.md) says
  such evidence is.
- **Not evidence that a richer vocabulary would be used correctly.** No evaluator can check that a
  stronger token was earned — Core §3.5 forbids the claim outright and §8.2 admits whatever the
  caller writes. A caller who maps existence to `present` will map existence to whatever is stronger,
  and the credulous probe column is that sentence made mechanical for facts.
- **The ceiling is unchanged: byte-lineage, not truth** (ADR-0002). C6 is that ceiling as a row: the
  agreement is complete, current, with the right counterparty, and the grant the question turns on
  *is* present — signed by someone who could not bind the counterparty. A clause could catch this
  fixture, because the fixture states the answer as a field; nothing can establish that the field is
  true. Every arm and every probe that receives an asserted availability state still releases. No
  lever demonstrated here reaches it, and neither would a fourth availability state.
- **No conformance claim.** Nothing in this repository claims JPS conformance, and a disposition is
  data — not an authorization, a decision, or an executed action.
- **Every fixture is synthetic.** Invented counterparties, invented agreements, pack ids under
  `example.test`. A test asserts it.

## Layout

| Path | What it is |
| --- | --- |
| [`pack/release-evidence-only.json`](pack/release-evidence-only.json) | The pack as an acquisition author would most plausibly meet it: one required requirement, one rule over its availability |
| [`pack/release-clause-fact.json`](pack/release-clause-fact.json) | The same decision with the grant stated as a Core fact condition — the probe |
| [`rules/agreement.rule.json`](rules/agreement.rule.json) | The convention arm: pack-independent clauses, and a fact transport that names no field |
| [`rules/agreement-coupled.rule.json`](rules/agreement-coupled.rule.json) | The same rule plus the one pack-coupled clause |
| [`naive.py`](naive.py) | The naive arm in both variants, with the practices each one models named |
| [`cases/`](cases/) | The seven frozen cases: artifact, parameters, requirement demands, derived claims, every disposition |
| [`replay.py`](replay.py) | Recomputes everything and diffs it against the frozen bytes |
| [`test_replay.py`](test_replay.py) | Every table cell hand-written from Core §8 and from the requirement's description, the per-clause coupling measurement, the controls, and the README's tables |

## Run

```bash
python3 replay.py            # verify every frozen cell (exit 1 on any diff)
python3 replay.py --table    # print the three tables above from the frozen cases
python3 -m unittest test_replay -v
```

Standard library only, offline, no model, no API budget. Imports the derivation rule from
[`../derivation-rule`](../derivation-rule/) and the evaluator from [`../python`](../python/); both
must be present (they are, on `main`).
