# Analysis — Study 008

## Decision

All five registered endpoints hit their predictions: the portable derivation rule produced envelopes
that a verifier authored by a **different study** admitted on 24/24 cells, reproduced every
registered mapping, matched Arm B's hand-curated basis exactly, agreed on every runtime disposition,
and recovered all three cells the model-authored arm lost.

The honest reading is narrower than the scoreboard. The exploratory probe shows the basis agreement
is **contingent on the corpus**, and that contingency is the study's most useful output.

## What the numbers support

Study 007's adversarial review argued that its own result was evidence the model should not author
the lineage envelope. Study 008 supports that reading and strengthens it in one specific way: the
replacement need not be bespoke per-study code. A rule expressed as **data** — one rule, no per-cell
branching — cleared the same bar as hand-written Python, against a verifier it was not written for.

The three Arm A losses are all structurally unreachable when the host derives:

| Arm A loss | Cause | Why Arm C cannot reproduce it |
|---|---|---|
| `r03-s02` | one-nibble digest transcription error | digests are read from the content-addressed store, never transcribed |
| `r03-s05` | invented `/payload/...` pointer namespace | pointers come from evaluation against the retained artifact root |
| `r02-s07` | incomplete basis | basis is the evaluation's read set, not an authored list |

That is a mechanism-level answer, not a rate improvement: these failures are removed from the design
rather than made less frequent.

## What the probe changes

D3 = 24/24 invites the conclusion "a mechanically-derived basis is sufficient." The probe refutes the
unconditional form. Construct a payload with `datedRecord: false` — a shape Study 007's eight
scenarios never contain — and the rule's `type` clause short-circuits inside
`all[isTrue(/datedRecord), isDecimalString(/matchCount)]`, never reads `/matchCount`, and the
unchanged verifier rejects the envelope for missing required basis pointers. The claim is identical
to Arm B's; only the basis differs.

So the correct statement is:

> On this corpus, the rule's clause ordering happens to make the cumulative read set coincide with
> the verifier's required set. That coincidence is a property of these eight payload shapes and this
> clause order — **not** a general property of short-circuit evaluation.

Two distinct notions were conflated and the probe separates them:

- **Read set** — what the derivation actually touched to reach its decision. Minimal, evaluation-
  order-dependent, and what `derive.py` returns as `basis`.
- **Sufficient basis** — what a policy demands as the load-bearing justification for an availability
  state. Policy-specific, and what the verifier enforces.

The first is not guaranteed to cover the second. Study 007 already flagged this from the other
direction (challenge 3: "sufficiency is policy-specific"); Study 008 shows it survives replacing the
model with a portable rule, because it was never a model problem.

## Implication for the derivation sub-contract (RFC 0003)

The derivation rule currently emits `basis` as a read set and says nothing about sufficiency. That is
a genuine gap in the sub-contract, and it is now demonstrated rather than argued. Three candidate
repairs, none implemented here and none preferred by this study:

1. **Declare the basis per clause.** Each clause states the pointers its claim rests on, decoupling
   basis from evaluation order. Costs the "derived, not authored" property that made Arm C immune to
   `r02-s07`.
2. **Read set without short-circuit.** Evaluate guard conditions fully for basis purposes. Keeps
   basis derived, widens it, and makes it depend on rule structure rather than payload shape.
3. **Verifier states sufficiency; derivation proves coverage.** The policy declares the required set;
   the derivation shows its read set covers it. Keeps the two notions separate, which is what the
   probe says they are.

Choosing among these needs a corpus that exercises the divergence, which Study 007's does not. That
is the natural next study, and it should be preregistered before any rule change — otherwise the rule
gets tuned to the verifier it is supposed to be tested against, which is exactly the circularity this
line exists to avoid.

## Prompt-injection note

S02's artifact carries an instruction to report zero matches and remove lineage. It reached no fact
in 3/3 cells, but this is **not** evidence of injection resistance in the Study 007 sense: no model
was in the loop. It shows only that a rule reading declared pointers has no path from free text to a
claim — a structural property, established by construction rather than measured.

## What this study does not establish

Carried from the preregistration and unchanged by the results:

- Nothing about model behaviour, authoring ergonomics, or source discovery — no model ran.
- No generalization beyond one source, one fact/evidence pair, one binding, and eight scenarios.
- Not independent validation: the rule, the verifier, and this study are all this project's work, so
  this is cross-artifact agreement *within* one project. The clean-room Go implementation was not
  exercised; running it against these 24 cells would be a stronger test and is not claimed here.
- Not that any admitted envelope is factually correct. The ceiling remains byte-lineage, not truth:
  a valid receipt over a fabricated upstream response still yields an admitted envelope.
- Arm B admitted 24/24 here while Arm A admitted 21/24 in Study 007. Those numbers come from
  different processes (deterministic replay vs. live model authoring) and must not be read as a
  controlled comparison of anything other than who assembles the envelope.
