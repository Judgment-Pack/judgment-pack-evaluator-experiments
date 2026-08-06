# Analysis — Study 010: the blinded oracle

Committed with `RESULTS.json`; every reported value recomputes from the
retained artifacts. Corrected after the post-run adversarial review, whose
ten findings are recorded verbatim with their dispositions in
[`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md). `DEVIATIONS.md` §1 is a
prerequisite for reading this: pilot runs of the registered prompt
preceded the registered one, so the operator knew the likely coverage
before executing. That is why the coverage profile leads and the single
sampled draw follows.

## The headline: the registered records covered all six affected classes

Sixteen vendor records from one operator-retained Codex transcript naming
`gpt-5.6-sol`, with no tool-use events and exact completion binding,
generated without access to either pack's bytes, `FAMILY.json`, or the
sampled mutation. The prompt itself disclosed the Study 010 and pack-bug
framing — `POLICY.md`, inlined verbatim, says it is a synthetic policy for
this study and that a divergence between a pack and the text is a pack
bug. So the author knew a pack existed; it never saw one.

Against the six pre-committed affected classes:

| # | The class a defect would hide in | H records reaching it |
| --- | --- | --- |
| 0 | no sanctions hit, non-embargoed, risk exactly 70 | 2 |
| 1 | no sanctions hit, non-embargoed, 70 ≤ risk < 71 | 2 |
| 2 | no sanctions hit, non-embargoed, handles personal data, 40 ≤ risk < 41 | 2 |
| 3 | no sanctions hit, non-embargoed, 40 ≤ risk < 70, either personal-data value | 4 |
| 4 | no sanctions hit and registered in SY | 1 |
| 5 | no sanctions hit, non-embargoed, handles personal data, 39 ≤ risk < 40 | 1 |

**Six of six covered.** Every record was policy-concordant (H = 16,
Q = 0): the model's own recorded outcome agreed with the policy mirror on
all sixteen, so none had to be excluded as mislabelled. The classes are
not disjoint — 0 and 1 have identical members here, and index 2's members
recur in index 3 — because coverage was registered as non-emptiness per
predicate, not as six disjoint record sets.

Two cells are worth reading carefully, and one of them less generously
than the first draft of this analysis read it:

- **Index 5** moves the clearance cutoff to the otherwise unnamed value
  39. `cedar-analytics` sits at 39.99. But the prompt expressly asks for
  borderline cases and the policy names 40 twice, including "a vendor that
  does handle personal data clears only below 40" — so 39.99 is a directly
  prompted just-below-40 case. It validly covers the registered mutation,
  and it is **not** evidence that the author independently targeted an
  un-signposted region.
- **Index 4** required a vendor registered specifically in SY with no
  sanctions hit. Two SY records exist; only `levant-medical-data`
  satisfies the full predicate, because `damascus-export-consortium`
  carries a sanctions hit and is caught by P1 first.

The registered transcript-bound output was 6/6. Two additional retained
completion datasets, identified by the operator as same-prompt and
same-model pilots, also recompute to 6/6 with counts (1, 2, 1, 5, 1, 1)
against the registered run's (2, 2, 2, 4, 1, 1). Their invocation
provenance, independence, and exhaustiveness are **not**
transcript-verifiable — `DEVIATIONS.md` §1 inventories exactly what each
retains.

## The registered primary endpoint

**E1 = `caught`.** The beacon selected index 4 — P2's embargo list
silently losing SY — and the record that caught it was
`levant-medical-data`, a Syrian medical-data vendor at risk score 88.75
that the office rejected:

```json
{ "caseId": "levant-medical-data",
  "vendor": { "legalName": "Levant Medical Data LLC", "sanctionsHit": false,
              "registeredCountry": "SY", "handlesPersonalData": true,
              "riskScore": "88.75" },
  "decision": { "outcome": "reject", "decidedBy": "Priya Nwosu",
                "decidedAt": "2026-06-15T17:05:00Z" } }
```

This is not a table artifact — the retained run output shows the
evaluator's own dispositions: under D, actual `unresolved/no-match`
against expected `reject`, status mismatch; under C, actual and expected
`reject`, status passed; and the MCP surface independently carries the
same disposition. A defect that a matrix written from the pack itself
could never see, seen by a record whose author had not seen the pack
bytes.

**What the beacon actually selected.** Because every family predicate
already contained an H record, once the registered records were fixed the
beacon no longer selected caught versus coverage-miss; conditional on
pipeline validity, it selected which already-covered defect would
demonstrate the catch. The pilots made `caught` anticipated, and the
registered 6/6 profile then made it entailed for every possible index.
E1 is therefore reported as confirmatory, and its interest lies in the
coverage profile that made it entailed, not in the draw.

Every prerequisite passed: the circular arm replayed itself with zero
mismatches (P-A); both transcribed arms' actual dispositions equalled
their reference tables exactly, with mismatch sets derived rather than
asserted (E2); and the CLI and MCP payloads agreed after removal of the
preregistered surface-specific `command` field (E5). `pipelineValid: true`.

## Why the selection is checkable, not asserted

The chain a reader can re-verify from the retained bytes:

1. The authenticated Rekor entry at index **2359064909** binds commit
   `f285fad…`, whose git tree carries the exact `PROTOCOL-LOCK.json` and
   every locked input at its registered digest.
2. The records commit `0739fab…` is bound by the authenticated entry at
   index **2359076917**, timestamp **1786014431** — a time the log signs,
   not one the operator can write.
3. The drawn round is arithmetic on that timestamp: T = 1786014731, round
   6352790 is scheduled at 1786014720 and round **6352791** at
   **1786014750**, so 6352791 is the first eligible round. The records
   were logged **319 seconds before** the selected round's scheduled
   release.
4. The retained responses for the two registered relay endpoints carry
   identical signature and previous-signature values, and the signature
   verifies under the locked drand public key. (The bytes show two
   URL-labelled responses agreeing; they do not authenticate the relays'
   organizational independence.)
5. `sha256(signature)` = `ef317786…`; the registered preimage hashes to
   `3a89b1ff…`; modulo six is **4**.

## What this does not establish

- **Not a rate.** One registered sample plus two operator-identified
  pilots, of one prompt against one model on one synthetic policy. This is
  an existence result about achievable coverage, not a frequency.
- **Not a claim about real business records.** These are invented case
  files from a model asked to imagine a diligent office, and explicitly
  asked for borderline cases. The production distribution is unknown and
  untested here; it may differ substantially from deliberately authored
  synthetic files.
- **Not blinding proof against an adversarial operator.** §9 of the
  preregistration states the ceiling: within this published branch the
  index is unsteerable, but a single operator could in principle have
  prepared several branches with different keys and retained a favourable
  one. Closing that needs an external party designating the branch before
  publication.
- **Not provider-signed authorship.** The evidence is one operator-retained
  transcript whose turn context names the model. The golden comparison
  covers normalized `response_item` messages and does not hash
  `session_meta` or `world_state`; those retained fields appear benign.
- **E1 was confirmatory and, given the registered profile, entailed.**

## What follows

The result this line needs next is a distribution, not another draw.
Running the registered authoring call across many independent sessions and
reporting per-class coverage rates would turn an existence result into
something a product can calibrate against — which matrix rows deserve
light human review and which deserve full review. That study needs none of
this one's machinery: the beacon, the transparency log, and the
single-attempt rule all exist to make **one unrepeatable draw**
trustworthy, and a study reporting rates over many runs needs sample size
and a preregistered analysis instead.

The finding that transfers today is narrower and still useful: when
expectations come from records authored without sight of the pack, they
can catch encoding defects that a pack-derived matrix structurally cannot
— including a mutation introducing a threshold the policy does not name.
