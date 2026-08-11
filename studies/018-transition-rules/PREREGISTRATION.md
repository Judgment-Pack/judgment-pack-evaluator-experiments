# Preregistration — Study 018: transition rules over cited registry state

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing
thereafter.**

**Nothing has run.** Everything executed during harness development lands under `pilots/`,
is labeled harness validation, and supports no claim. After the freeze this file is never
edited; corrections go to [`DEVIATIONS.md`](DEVIATIONS.md).

Four companion artifacts are registered *with* this document and pinned at the freeze:
[`rule/SPEC.md`](rule/SPEC.md), [`harness/MATRIX.json`](harness/MATRIX.json),
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) and
[`harness/MATRIX-HOLDOUT-EVIDENCE.json`](harness/MATRIX-HOLDOUT-EVIDENCE.json).

## 1. Question

Study 016 measured that a signed registry can report membership at a snapshot and nothing
more. [RFC 0011 §2a](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md)
then states that membership does **not** determine continued reliance: that second question
is a **transition rule**. Its Unresolved #10 asks where such a rule is sourced and audited
and stays open here — this study takes no position on who owns the question. #11 asks what a
**cited registry head** — an artifact recording the registry state it validated against —
would be good for, and answers narrowly: one possible input, with no ordering. That is the
question this study measures.

**R1 (primary, retractable):** for every adjudicated endpoint cell, the observed
`{currency, transition}` outcomes **and every registered `expectedRuleEvidence` field**
equal the registered expectations — where Layer CURRENCY is Study 016's frozen verifier
reporting membership only, and Layer TRANSITION evaluates one of three registered rules
(`stop-at-retirement`, `position-window`, `grandfather-on-cited-support`) over
`(cited head, membership, rule)`. The adjudicated channels are exactly `currency`,
`transition`, `transition:citedPosition` and `transition:retiredAtPosition`; a cell that
reaches its registered outcome from the wrong position diverges on the structured channel
and falsifies R1 just as an outcome divergence does. Divergence in either direction
falsifies, including a refusal on a `registeredUndetected` cell.

**R2 (descriptive):** the evidence map — which registered facts each rule needs, which it
computes deterministically from retained artifacts, and which it cannot compute at all.

## 1a. Two strata

The locked-replication stratum (`harness/MATRIX.json`, 21 cells) is a conformance suite over
behaviour the maintainer observed during development; R1 has a locked replication's standing,
never a prospective prediction. The **reviewer holdout** is authored by the cross-vendor
reviewer during the pre-freeze rounds, committed verbatim with attribution, never executed
before the freeze; its construction machinery and its structured-evidence expectations land
together with its cells, and post-freeze the scorer refuses an empty stratum. Builder and
evaluator share one implementation lineage — the standing no-independent-oracle limitation.

## 2. Apparatus and pins

- **Registry-and-rule only** (D-1): no receipt protocol, no evaluator binary, no external
  clone. A cell is `(commitment tuple, snapshot, trust configuration, citation, rule
  configuration)`; the suite is fully offline and deterministic.
- **Study 016's frozen registry modules as a pinned unmodified upstream** (D-2), loaded by
  authenticated absolute path, compiled from hashed source bytes, with every reserved module
  name preflighted and per-load identity/origin/bytes verification — Study 017's hardened
  loader, inherited including its unchecked-hash bytecode case.
- **Executed bytes, not just source digests**: a stdlib bootstrap runs before any study or
  third-party import and refuses when the cache a plain import *would* accept differs from
  `compile()` of its source. An equivalent cache is accepted; `__main__` is exempt by
  construction.
- **Registered dependencies**: `cryptography` and `rfc8785` by version, distribution root and
  imported-module origin. Their **contents are not digest-pinned**, and that residue is stated
  rather than claimed closed.
- **Pins are enforced, not declared**, and the mapping the loader trusts is bound from the
  stamped registry bytes the attempt records.

## 3. Scenario

One history serves the matrix, so cells differ in the rule and the cited head rather than in
the world:

    1 add 1.0.0   2 add 2.0.0   3 retire 1.0.0   4 retire 2.0.0   5 reinstate 2.0.0

The committed decision names `(1.0.0, digest-A)` — in the supported set from position 1,
out of it from position 3, never reinstated. Layer CURRENCY therefore reports
`not-current-at-snapshot` for every full-history cell, and every difference in the
transition column is the rule's doing. A harness test asserts that structurally: the four
`div-*` cells share commitment, snapshot and trust configuration byte-for-byte and differ
only in the rule configuration.

## 4. Cells

21 cells (matrixVersion 2, the round-1/2 revision): 4 positive controls, 4 negative controls
(an unregistered rule; an unauthenticated snapshot; and two never-bound-digest controls), 11
endpoints across divergence (D), citation value (C) and boundaries (B), 1 descriptive row and
1 demonstration — the last two byte-identical to endpoints they re-read, registered as identity
groups and counted toward nothing. A harness test derives these counts from the matrix.
`registeredAbsences` names the six cells that deliberately retain no citation, so an
unregistered absence stays a validity failure rather than a finding. Cells that turn on
*where* the artifact sits in the history additionally register `expectedRuleEvidence`
(`citedPosition`, `retiredAtPosition`), adjudicated as their own `transition:<field>`
divergence channels, so a cell cannot reach its registered outcome from the wrong position.

### 4a. The registered boundaries

- **`bnd-backdated-citation`** (registered expected-undetected) is **byte-identical** to
  `div-grandfather-on-cited-support`, verified by the scorer as a registered identity group. Honest
  reliance and backdated reliance are the same evidence, so no rule over this evidence
  separates them; the citation attests the state an author *claims*, never when the artifact
  was created. Signing the citation changes nothing — the party that would sign is the party
  that chooses what to cite. Closing this needs the trusted ordering RFC 0011 Unresolved #3
  leaves open.
- **`bnd-duration-window`**: a duration window is `transition-unavailable`. The only ordering
  available offline is positional; `effectiveFrom` is inert in the pinned upstream and nothing
  holds a clock. A reader may object that a position window is not what an organisation means
  by "24 hours" — that objection is the cell, and the study does not defend the model.
- **`bnd-mint-time-refusal`**: exhibited as what a producer's own check would have returned,
  registered as a **separately chosen producer policy**, never a property of the citation.
- **`bnd-foreign-series-rule`**: a rule is stated per series and confers nothing outside it.

### 4b. Threat model

`none` — registry state, citation and rule configuration vary. `tamper` — a retained artifact
edited. `full-keys` — an author who chooses what its own artifact cites, which is the study's
registered adversary and the one the citation cannot resist.

### 4c. Analytic limitations

The three rules are a **construct**, not a survey of practice: no claim that organisations
hold these, or only these. Ordering is out of reach by construction, so no cell measures
elapsed time and the window rule is positional by necessity. Nothing here measures who
sources a rule, how a rule is audited, or whether a relying party applied its own rule
consistently — RFC 0011 Unresolved #10's questions, which this study can pose evidence to but
not answer.

## 5–8. Endpoints, validity, controls, enforcement

The 016/017 regime, inherited: an ordered exhaustive decision rule (pipeline-invalid → control
gates → zero endpoint divergence → falsified); validity separated from detection, with
`registeredAbsences` read from the registry alone and identity-group divergence a validity
failure; `ATTEMPT.json` written before the registry is parsed and carrying `pinsRawSha256`
over the exact bytes then parsed; every terminal path recorded; the scorer refusing an existing
attempt root; the frozen cell-id set and per-cell schema asserted; the SPEC/code vocabulary
diffed against the evaluator; and builder determinism (build twice, byte-identical).

## 9. What this study cannot show

No interoperability claim of any kind — nothing here is independently developed. No claim that
the registered rules are the rules organisations hold. No ordering, and therefore no ability to
distinguish an honest citation from one chosen after the fact — that is a registered boundary,
not a gap in the harness. No policy or fact truth; no claim that a `usable` verdict means a
decision is correct, only that it is usable under a stated rule on the evidence retained.
Everything Studies 016 and 017 registered as nothing's remains nothing's. Trust roots: the
study-minted registry authority, the pinned Study 016 modules, this study's rule code, the
registered dependencies, and the retained artifact store. Binding/lineage, not truth.

## 10. Publication commitment

The decision matrix is published in full whichever way it lands — every divergence, every
registered boundary, and the identity group that carries the study's sharpest limit — because
a precise map of what a citation buys a relying party, and where it stops, is the study's most
useful possible output and the registered input to RFC 0011 Unresolved #10 and #11.
