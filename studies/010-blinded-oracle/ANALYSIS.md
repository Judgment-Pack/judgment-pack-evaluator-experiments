# Analysis — Study 010: the blinded oracle

Written after `RESULTS.json`, and structured so the number that matters
comes first. `DEVIATIONS.md` §1 is a prerequisite for reading this: two
pilot runs of the registered prompt preceded the registered one, so the
operator knew the likely coverage before executing. That is why the
coverage profile leads and the single sampled draw follows.

## The headline: independently authored records covered every boundary class

Sixteen vendor records, authored by a different vendor's model from the
policy prose alone, with no knowledge of the pack, the defect family, or
that any defect existed. Against the six pre-committed mutation classes:

| # | The class a defect would hide in | Records reaching it |
| --- | --- | --- |
| 0 | risk score exactly at the stated threshold (70) | 2 |
| 1 | at or just above 70, below 71 | 2 |
| 2 | at the stated lower bound 40, below 41 | 2 |
| 3 | the whole personal-data mid-band, 40 to 70 | 4 |
| 4 | registered in SY — one embargo literal of three | 1 |
| 5 | **39 to 40 — a band the policy never names** | 1 |

**Six of six classes covered.** Every record was policy-concordant
(H = 16, Q = 0): the model's own recorded outcome agreed with the policy
mirror on all sixteen, so none had to be excluded as mislabelled.

The interesting cell is index 5. The policy text names 70 and 40 out loud,
so a diligent author has an obvious reason to write cases at those
numbers. Nothing in the text points at 39–40 — it exists only as an
interaction between P4's floor and P5's clearance arm. A record landed
there anyway. The same holds for index 4: the policy lists three embargoed
countries, and covering the class required writing a vendor in
specifically SY rather than the more salient KP or IR.

Across three independent samples of the same prompt — the registered run
and the two pilots — coverage was 6/6 every time, with per-class counts
varying (registered 2,2,2,4,1,1; both pilots 1,2,1,5,1,1). Different
records, same completeness. This is three samples, not a rate; §"What this
does not establish" says what that does and does not license.

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

Under correct pack C it disposes as `reject` and the row passes. Under the
mutated pack D — where P2 checks only KP and IR — it matches no rule at
all and disposes `unresolved/no-match`, so the row fails. A defect that a
matrix written from the pack itself could never see, seen by a record
written by someone who had never heard of the pack.

Every prerequisite passed: the circular arm replayed itself with zero
mismatches (P-A), both transcribed arms' actual dispositions equalled
their reference tables exactly, with mismatch sets derived rather than
asserted (E2), and the CLI and MCP surfaces agreed byte for byte (E5).
`pipelineValid: true`.

## Why the selection is checkable, not asserted

The chain a reader can re-verify without trusting the operator:

1. The protocol lock was committed and entered the public Sigstore Rekor
   log at index **2359064909**, and that entry's tree carries this exact
   `PROTOCOL-LOCK.json` and every locked input at its registered digest.
2. The sixteen records were committed (`0739fab4`) and entered the same
   log at index **2359076917**, timestamp **1786014431** — a time the log
   signs, not one the operator can write.
3. The drawn round is arithmetic on that timestamp: the first drand
   mainnet round scheduled at least 300 seconds later, which is round
   **6352791** at **1786014750**. That round had not occurred when the
   records were published.
4. Its signature was fetched from two independent relays by chain hash and
   was byte-identical from both; the index is
   `sha256("study-010-draw-v1\n" + randomness + "\n" + commit + "\n" +
   family digest + "\n") mod 6` = **4**.

The one-sentence version: the records were in a public log before the
randomness that chose the defect existed.

## What this does not establish

- **Not a rate.** Three samples of one prompt against one model on one
  synthetic policy. "6/6 three times" is an existence result about
  achievable coverage, not a frequency anyone should quote.
- **Not a claim about real business records.** These are invented case
  files from a model asked to imagine a diligent office, and such an
  office is exactly the kind that writes boundary cases. Records that fall
  out of an actual operational system have no such motive, and §10 of the
  preregistration keeps real records out of scope for good reason. The
  honest expectation is that production files cluster in the easy middle;
  this study does not test that.
- **Not blinding proof against an adversarial operator.** §9 of the
  preregistration states the ceiling exactly: within this published
  branch the index is unsteerable, but a single operator could in
  principle have prepared several branches with different keys and
  retained a favourable one. Closing that needs an external party
  designating the branch before publication, which a single-operator study
  cannot supply.
- **E1 was confirmatory, not exploratory.** Per `DEVIATIONS.md` §1 the
  operator had seen two prior samples covering all six classes, so
  `caught` was the expected result before the beacon ran.

## What follows

The result this line actually needs next is a distribution, not another
draw. Running the registered authoring call across many independent
sessions and reporting per-class coverage rates would turn "six of six,
three times" into something a product can calibrate against — which
matrix rows deserve light human review and which deserve full review. That
study needs none of this one's machinery: the beacon, the transparency
log, and the single-attempt rule all exist to make **one unrepeatable
draw** trustworthy, and a study that reports rates over fifty runs needs
sample size and a preregistered analysis instead.

The finding that transfers today is narrower and still useful: when
expectations come from records authored independently of the pack, they
can catch encoding defects that a pack-derived matrix structurally cannot
— including at a boundary the policy never names.
