# Analysis — Study 008

## Decision

All five registered endpoints hit their predictions. That is the weakest part of the study, and the
headline it invites is wrong.

The preregistration's central premise — that the rule and the verifier "were built separately …
without either being written against the other" — is **false**, and the adversarial review
established it from the repository. Study 007's `verify_candidate` re-derives the claim by calling
`derive_payload` (007 `harness/study.py:465-467`) and grades the candidate against that output
(`:473-497`), with a **superset** test on the basis (`:499`). `derive_payload` is Arm B. And the rule
under test was authored from `derive_payload` in the first place: `derivation-rule/README.md:26-27`
describes its corpus as cross-checked to reproduce that function's claim on every case.

So D1 does not mean "an independent authority admitted the portable rule." It means "Arm C's claim
equals `derive_payload`'s claim, and Arm C's basis contains `derive_payload`'s basis." From there D2
is entailed (Study 007 pins each cell's registered `expected` to `derive_payload`'s output), D4 is a
runtime-determinism check (the verifier has already forced both arms' runtime inputs byte-identical),
and D5 is a subset of D1 that Arm B satisfies equally.

The calibration controls make the ceiling concrete. An **un-derived kitchen-sink basis** — Arm B's
claim with every top-level pointer listed, no derivation involved — is admitted **24/24**. A basis
one pointer short is admitted **0/24**. The verifier's basis check discriminates "too short" from
"long enough" and nothing else. D1 = 24/24 is therefore compatible with the rule contributing
nothing, and cannot be cited as evidence that a derived basis beats an authored one.

## What the study does establish

Two things, both narrow.

**1. Faithful transcription, including the basis (D3).** On 24 cells, `derive.py` +
`screening.rule.json` reproduce `derive_payload`'s claim triple and `reason` with zero disagreements,
and their cumulative short-circuit read set equals its hand-curated basis **exactly** — equality, not
the superset the verifier settles for. D3 is the one endpoint with independent content, because it is
the only one the verifier does not already force. That a decision procedure of this shape, including
its basis, can be carried as data with no per-cell authoring is a real if modest result for the
derivation sub-contract (RFC 0003).

**2. The read set is not a sufficient basis (the probe).** Construct a payload with
`datedRecord: false` — a shape Study 007's eight scenarios never contain — and the `type` clause
short-circuits inside `all[isTrue(/datedRecord), isDecimalString(/matchCount)]`, never reads
`/matchCount`, and the unchanged verifier rejects for missing required basis pointers on an otherwise
identical claim. Arm B is admitted on that same constructed store, so the rejection is attributable
to the basis alone.

This separates two notions the design had conflated:

- **Read set** — what the derivation's *conditions* touched. Minimal, evaluation-order-dependent,
  and what `derive.py` returns as `basis`.
- **Sufficient basis** — what a policy demands as load-bearing justification. Policy-specific, and
  what the verifier enforces.

The first does not cover the second, and there is a second independent way it fails:
`derive.py:279-285` resolves a fact's source pointer with a bare `get()` that never touches the read
set, so `/matchCount` enters the resolved basis only because `isDecimalString` happened to test it. A
rule extracting a fact from an untested pointer would omit the very pointer the fact came from.

Note what this finding is *not*: a discovery. `derivation-rule/corpus/type-notdated.json` already
pinned the four-pointer basis before this study was preregistered. The probe's contribution is
showing the unchanged verifier **rejects** it.

## Implication for the derivation sub-contract (RFC 0003)

The rule emits `basis` as a read set and says nothing about sufficiency. That gap is now demonstrated
rather than argued. Three candidate repairs, none implemented and none preferred:

1. **Declare the basis per clause.** Decouples basis from evaluation order; costs the "derived, not
   authored" property.
2. **Read set without short-circuit.** Keeps basis derived and widens it; makes it depend on rule
   structure rather than payload shape. Does not fix the fact-pointer gap.
3. **Policy states sufficiency; derivation proves coverage.** Keeps the two notions separate, which
   is what the probe says they are.

Choosing needs a corpus that exercises the divergence and a verifier the rule was not transcribed
from. Both are absent here. Any rule change made now would tune the artifact under test to the
verifier it is supposed to be tested against — the exact circularity this line exists to avoid, and
the one this study fell into at the framing level.

## Method lesson

This study was designed as a cross-artifact test and was not one. The check that would have caught it
before running — read the verifier's body and ask what it compares against, and read the artifact
under test for a provenance claim — costs minutes, and neither was done at preregistration time. The
preregistration's freeze discipline was sound and its registered risk was right; its premise was
unverified. Freezing a protocol does not make its premises true, and an endpoint that cannot fail
looks exactly like an endpoint that passed.

## What this study does not establish

- Not that an independent authority admitted the portable rule (see Decision).
- Not that D1, D2, D4 or D5 tested anything D1 did not.
- Not that a mechanically-derived basis outperforms an authored one — the wide control refutes that
  reading directly.
- Nothing about model behaviour, authoring ergonomics, or source discovery: no model ran. S02's
  injected text reached no fact, but that is structural (a rule reads only declared pointers), not a
  measurement of injection resistance.
- No generalization beyond one source, one fact/evidence pair, one binding, eight scenarios.
- Not independent validation: rule, verifier, study and adversarial review share one author. The
  clean-room Go implementation was not exercised; running it against these cells would be a stronger
  test and is not claimed.
- Not that any admitted envelope is factually correct. The ceiling remains byte-lineage, not truth: a
  valid receipt over a fabricated upstream response still yields an admitted envelope.
- Arm B's 24/24 and Arm A's 21/24 come from different processes (deterministic replay vs. live model
  authoring) and are not a controlled comparison of anything but who assembles the envelope.
