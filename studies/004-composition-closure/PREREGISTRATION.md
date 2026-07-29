# Preregistration — Study 004: does declared composition close the cross-decision escape?

**Status: FROZEN on the commit that adds this file.** Written before any frame-pass, feature-pass,
encoding, or measurement agent has run. Deviations go to [`DEVIATIONS.md`](DEVIATIONS.md), never
into this file.

## 1. The question

Study 003's data records two escape routes that a *composition* of packs claims to address.
Among its 40 adjudicated prepared-determination facts, some are another inventory decision's
verdict transcribed by hand rather than a lookup or a computation; among its 55 adjudicated
residue sentences, some reference another inventory decision's outcome or entitlement —
the *forward entitlements / cross-decision references* family Finding 4 named narratively.
Study 003 measured neither route's item-level rate; **this study constructs both frames
retrospectively, by registered rule, and that construction is itself a reported result.**

A graph format now exists concretely: the reference runtime's experimental composition surface
(its ADR-0015 — nodes reference packs; an edge feeds one decision's outcome downstream as a fact
at an RFC 6901 pointer and/or as a tri-state evidence contribution). The specification's RFC 0002
remains a Draft sketch; this study does not evaluate the RFC. It measures **one concrete edge
grammar's closure rate over the cross-decision escape in Study 003's frame**, and names what that
grammar cannot carry — evidence for RFC 0002 to weigh, produced before the RFC settles anything.

## 2. Census frame — the rule fixed now, the membership derived, not picked

**Corpus:** Study 003's published, adjudicated artifacts exactly as committed —
[`../003-escape-census/measurement/adjudicated.json`](../003-escape-census/measurement/adjudicated.json)
and the room packs in [`../003-escape-census/rooms/`](../003-escape-census/rooms/) — over the same
τ-bench policies at the same pinned commit. No new policy text and no re-encoding of any single
pack.

**Why the membership is not listed here:** a hand-picked list would let the author choose items
the grammar flatters. Membership is derived by a **frame pass** under the fixed rule below, by two
classifiers working independently, before any composition is authored.

**The frame rule (fixed now):**

- **Unit F (facts):** an adjudicated prepared-determination fact is *in* iff its ledger entry or
  adjudication note describes concluding the fact by applying the policy of a *different* decision
  in Study 003's frozen 12-decision inventory — the fact is that decision's answer. Preparations
  that are lookups, computations, or quantifications over the *same* decision's inputs are out.
- **Unit R (residues):** an adjudicated residue sentence is *in* iff the sentence or its
  adjudication note states a dependency on, entitlement from, or reference to the outcome of a
  *different* inventory decision. Sentences whose inexpressibility is unrelated to another
  decision's outcome are out; no category of residue is excluded a priori — an agent-procedure
  obligation is out only because it references no inventory decision's outcome, not by rule.

Classifiers receive the full adjudicated data and the frozen inventory, mark every one of the
40 + 55 items in/out with one sentence each, and disagreements are adjudicated and reported as a
count. **Both error directions are possible and neither is claimed as expected:** notes that never
mention another decision can hide a dependency (under-inclusion), and broad readings of
"reference" or "entitlement" can sweep in items whose cross-decision content is incidental
(over-inclusion). The published per-item markings are the check. **The membership is frozen
before encoding begins and reported at any size — zero included**, which would itself be the
study's primary result: the family Finding 4 named would be smaller than its prose suggested.

For **Unit R items only**, the frame pass also extracts the *cross-decision clause*: the minimal
quoted span of the sentence whose content references the other decision. Scoring (§5) is over
that clause, not the whole sentence — the known insurance sentence also carries a price and a
per-passenger computation, and this study measures none of that.

## 3. The treatment, frozen

- **Runtime:** one binary, built once from runtime commit
  `a3058cbadee993306d2f8bc9184cd6d9191a9143` exactly (ADR-0015, adversarially reviewed at that
  commit; no release-tag substitution — a later tag could carry evaluator changes outside the
  graph code), its SHA-256 recorded in the run log before any room opens, used unchanged for
  every room and every harness step.
- **Pack admissibility, the one permitted pack change:** all 12 census packs declare
  `specVersion` `0.1.0-draft`, which the evaluator refuses under Core §11. §11's own remedy is
  one edit — the `specVersion` string, nothing else. The study harness (never a room) re-declares
  each cluster's packs to `0.2.0-draft` before rooms open, records each file's before/after
  digest, and verifies with `spec validate` that every re-declared pack still validates at
  exit 0. No other member of any pack may change, and rooms are barred from editing packs
  entirely. A pack that fails validation after re-declaration is reported as a result and its
  cluster still runs (validation-only closure remains measurable; §5).
- **One room per cluster, one encoder, one run.** Frame items are grouped by the set of inventory
  decisions they connect; each cluster gets one room, one encoder session, no reruns and no
  selection among outputs. A room is voided and re-run with a fresh encoder only for a recorded
  protocol failure (agent crash, barrier breach), logged in `DEVIATIONS.md`. Encoder model and
  configuration are recorded per room.
- **Project configuration:** the graph surface resolves packs through a `jpack.json`. The
  harness writes each room's configuration before the room opens — `configVersion` `"1"`, one
  entry per cluster pack whose decision id is the frozen inventory id (lowercased, e.g. `a6`)
  and whose path is the re-declared pack file — and records it verbatim. Rooms may read it and
  must not modify it.

## 4. Design — passes in order, encoding blind to the hypothesis

**Frame pass** (§2), then **feature pass**, then **encoding**, then **measurement**.

**Feature pass — predictor labels before any graph exists.** After membership freezes and before
any room opens, one classifier labels every frame item by this total rule: **scalar-status** iff
the downstream use consumes only *which outcome* the upstream decision produced (an outcome
identity, compared for equality or membership); **non-scalar** otherwise (the reference carries
parameters, magnitudes, per-item entitlements, or needs the upstream decision's facts rather than
its verdict). The labels are committed before encoding begins.

**Encoding pass.** Each room receives **only**: the domain's full policy text; its cluster's
re-declared packs, verbatim; the pinned runtime binary, its `--help` texts, and the graph schema
it prints. Rooms run under the repository's clean-room controls
([`CLEAN-ROOM-PROTOCOL.md`](../../CLEAN-ROOM-PROTOCOL.md) §§1–3, applied to composition): a fresh
directory outside every project repository, network and MCP disabled, no access to this
repository, Study 003's ledgers, residue logs, or results, the specification repository, or the
RFCs; the full session transcript is audited before the room's output is accepted, and a breach
voids the room. **The brief is neutral:** "These packs encode decisions from this policy. Using
the graph format this tool provides, declare the relationships the policy states between these
decisions; the graph must validate against these packs. For any policy sentence relating these
decisions that you cannot represent as a declared relationship, record the sentence verbatim
with what you did instead. You may not modify the packs." No mention of Study 003's findings,
closure, rates, or this study's hypothesis. What the barrier withholds is results and labels —
it cannot hide provenance: the packs' own metadata names census rooms, their structure carries
Study 003's encoding choices, and the cluster's composition tells the encoder which decisions
are related. That is disclosed here, not claimed away.

**Harness step — mechanical, after each room closes.** The harness (not the room) runs, with the
pinned binary: `graph validate` on the room's graph; and `graph evaluate` **twice per input
set** on two input sets it constructs by the fixed procedure below, byte-comparing each pair of
repeated runs. The study never hand-tunes inputs: if a constructed set fails to produce the
disposition its name suggests, the refusal or disposition actually produced *is* the recorded
result.

- **Resolving set:** per node, evidence maps every declared requirement id to `"present"`, and
  facts are derived from the pack by walking, in document order, first the `applicability`
  condition (when present) and then the first rule's `when` condition, writing a value at each
  `op: fact` leaf by this total table — `equals` → the compared value; `in` → the array's first
  element; `greater-than-or-equal` / `less-than-or-equal` → the compared value; `greater-than`
  → the compared value with `"0"` appended; `less-than` → `"0"`, or `"-1"` when the compared
  value is `"0"`; `all` → every child; `any` / `not` and any operator outside this table → the
  leaf is skipped and recorded as unconstructed. The first write at a pointer wins; later
  writes to the same pointer are recorded and skipped.
- **Unresolvable set:** per node, facts are the empty object and evidence maps every declared
  requirement id to `"present"`, so any failure to resolve comes from the facts alone.

A room that produced no graph file is recorded as such and scored: all its frame items are
**open** (§5).

**Measurement pass.** Two classifiers independently receive the frozen membership with
cross-decision clauses, the feature-pass labels, the produced graphs and residue logs, and the
harness results, and score every frame item under §5. Disagreements are adjudicated and reported
as a count.

## 5. Scoring and metrics — fixed now

**Per-item verdicts — a decision procedure, applied in order, so the three verdicts are
mutually exclusive and exhaustive:**

1. If the room produced no graph file, or the graph does not validate at exit 0 → **open**.
2. Otherwise, find the item's *live carrying edges*: declared edges whose fact pointer is,
   byte-for-byte, a pointer the downstream pack's conditions read, or whose evidence id is one
   the downstream pack declares (both checkable against the pack documents), and which carry
   some of the item's cross-decision content — for Unit F the transcribed verdict, for Unit R
   the extracted clause. If there are none → **open**.
3. If the live carrying edges carry all of the item's cross-decision content with nothing
   lost → **closed**. Otherwise — some content uncarried, or carried with a stated loss (an
   entitlement's magnitude dropped, a condition flattened) → **partial**. Any loss at all means
   partial, never closed; an edge to a target nothing reads is not a carrying edge and
   contributes to no verdict but open's.

**Device, for every partial and open item — one primary, by this precedence order (secondary
observations go to notes):** `needs-effect-or-entitlement (the reference changes a later
decision's rules, not its facts)` → `needs-outcome-payload (parameters beyond the outcome id)` →
`needs-conditional-edge (the feed applies only under a condition)` → `needs-upstream-facts (the
inputs, not the verdict)` → `needs-shared-evidence-context` → `needs-cycle-or-mutual-reference` →
`other (described)`. The open category is mandatory to report: Study 003's key finding was not on
anyone's list.

**Metrics:**

- **G1 (primary):** closed ÷ frame size, overall and per unit type, reported as counts beside
  every ratio; a zero denominator is reported as counts with no ratio, and an empty frame makes
  §2's zero-membership result the study's primary outcome.
- **G2:** counts of partial and open items per primary device, per unit type. Counts only, no
  proportions.
- **G3:** per cluster: pack re-declaration digests and validation results; whether a graph file
  was produced; `graph validate` status; both `graph evaluate` input sets' outcomes and whether
  each pair of repeated runs was byte-identical.
- **G4:** every room-recorded residue sentence not in the frame, verbatim, deduplicated by exact
  string after whitespace normalization, attributed to every cluster that recorded it; the
  adjudicator may note semantic near-duplicates without merging them.

**Predictor (registered; its epistemic status stated plainly):** this predictor is written
knowing Study 003's published results and the two A1 items whose notes explicitly name the
family; it is registered before the frame membership, the feature labels, and any graph exist,
and it is scored only against those later artifacts. Prediction: every **scalar-status** item is
**closed**; every **non-scalar** item is **not closed** (partial or open). Accuracy = correctly
predicted items ÷ frame size; the feature rule is total, so there are no abstentions. Separately:
the most frequent primary device among partial + open items will be
`needs-effect-or-entitlement`; a tie for most frequent, or zero partial + open items, scores this
aggregate prediction as a miss. An empty frame leaves the predictor unscored — reported as
unscored, with the zero-membership result standing alone (§2), and no accuracy ratio is formed.

## 6. What will be reported regardless

The frame pass's full per-item markings, extracted clauses, and disagreement count (membership of
any size, zero included); the feature-pass labels; every re-declaration digest; every produced
graph, residue log, and audited-room disposition; the harness's validate/evaluate results and
byte-comparisons; both measurement classifiers' raw judgments and every adjudication; G1–G4; the
predictor's per-item hits and misses; and this document unedited.

## 7. Honest limits, stated in advance

This measures **one grammar** — the runtime's experimental outcome-as-fact / outcome-as-evidence
edge — over **one frame** derived from one census of two policies by one benchmark team.
**Neither a low nor a high G1 licenses any claim about composition as a design class, about
other grammars RFC 0002 could adopt, about other corpora, or about authoring efficacy, policy
correctness, or operational outcomes.** A low G1 is evidence about this grammar's reach; a high
G1 is evidence that this frame's items are the easy kind. The frame inherits Study 003's
adjudications and taxonomy, and its notes were written about single packs, not about
composition — the registered rule reads what they say, and its published per-item markings are
the control, not a guarantee. The tool's help text names the RFC it prototypes; the barrier
withholds results and labels, not provenance (§4). Same maintainer, same machine, and likely the
same model family throughout: internally produced evidence under a barrier, not independent
validation.
