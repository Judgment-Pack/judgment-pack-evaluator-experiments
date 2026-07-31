# Preregistration — Study 008: portable-derivation admission

**Status: FROZEN on the commit that adds this file.** Written before the Study 008 harness, adapter,
runner, scorer, or result exists or runs. Deviations go to [`DEVIATIONS.md`](DEVIATIONS.md), never
into this file.

## 1. Why this study exists

Study 007's adversarial review states the strongest contrary interpretation of its own result:

> Study 007 is evidence that the model should not author the lineage envelope at all. […] A
> deterministic host could insert the two digests without error and derive all registered pointers
> without AI.

That reading is already partly built: Study 007's harness contains `candidate_from_gateway`, a
host-side envelope assembler over a hand-written Python derivation (`derive_payload`) whose evidence
**basis pointers are hand-curated per branch**. Replacing a model with bespoke per-study Python is
not portability; it relocates the authoring problem into code that only this study can run.

The trustworthy-input-acquisition line ([ADR-0002](../../docs/adr/0002-trustworthy-input-acquisition-research-line.md))
proposed the portable alternative: a **derivation rule** expressed as *data*
([`derivation-rule/`](../../derivation-rule)), where the claim comes from ordered first-match clauses
of declared typed checks, and the evidence **basis is computed mechanically from the pointers the
evaluation actually read** — not curated by an author.

Study 008 asks one question:

> Does the portable derivation rule, whose basis is mechanically derived from its own read set,
> produce lineage envelopes that a verifier authored by a *different* study admits — on all 24 of
> Study 007's retained cells, with no per-cell special-casing?

This is a cross-artifact test in the anti-circularity pattern the line uses elsewhere: the rule
(`derivation-rule/`) and the verifier (Study 006/007 `study.py`) were built separately, for different
purposes, without either being written against the other. Agreement is therefore informative;
disagreement is the more useful outcome, because it localizes an unspecified part of the contract.

## 2. Zero model calls

Study 008 runs **no model, no hosted API call, and no network access**. It replays Study 007's
retained, content-addressed trial artifacts byte-for-byte. It consumes no API budget and adds no
prompt, scenario, or model treatment. It therefore makes **no new claim about model behaviour** and
is never pooled with Study 006 or Study 007 model endpoints.

## 3. Frozen inputs

Study 008 reads, and never modifies, the following Study 007 artifacts at experiment commit
`8ed6aa6` (the commit this preregistration's parent points to):

| Input | Role |
|---|---|
| `studies/007-…/trials/<cell>/gateway/receipts/*.json` | the attested receipt (digests come from here, never from a claim) |
| `studies/007-…/trials/<cell>/gateway/artifacts/*.json` | the retained canonical artifact the derivation reads |
| `studies/007-…/trials/<cell>/cell.json` | the cell's registered `expected` mapping and binding digest |
| `studies/007-…/trials/<cell>/final.json` | Arm A's model-authored envelope (reference only, not re-run) |
| `studies/007-…/fixtures/binding-lock.json`, `fixtures/gateway.key` | binding and attestation key |
| `studies/007-…/harness/study.py` verifier + `candidate_from_gateway` | the **unchanged** admission authority and Arm B |
| `derivation-rule/rules/screening.rule.json` | the portable rule under test |
| `derivation-rule/derive.py` | the portable rule evaluator |

The verifier is used **unchanged**. If Study 008 requires any edit to Study 007's verifier semantics
to admit an Arm C envelope, that is a **registered failure of Arm C**, recorded as such, not a fix.
The frozen SHA-256 of `screening.rule.json`, `derive.py`, and the verifier are recorded in
`FREEZE.json` before the first scored cell.

## 4. Arms

- **Arm A — model-authored.** Study 007's completed result (21/24 admitted). Carried over as a
  reference column. **Not re-run**; no new model call is made.
- **Arm B — study-bespoke host derivation.** Study 007's existing `candidate_from_gateway` over
  `derive_payload`, with hand-curated per-branch basis sets. Re-run deterministically over the
  retained artifacts.
- **Arm C — portable rule derivation.** The same envelope assembly (same digests-from-receipt, same
  `sourceRef`, same fact-claim shape) but the claim and the **basis** come from evaluating
  `screening.rule.json` with `derive.py`. One rule for all 24 cells. No per-cell branching, no
  per-cell basis authoring, no edit to the rule after the first scored cell.

Arms B and C differ in exactly one respect — where the claim and basis come from — so any admission
difference is attributable to that.

## 5. Registered endpoints

| id | Endpoint | Denominator |
|---|---|---|
| **D1** | Arm C envelopes admitted by the unchanged Study 007 verifier | 24 |
| **D2** | Arm C claim (`facts`, `evidenceAvailability`, `acquisitionStatus`) equals the cell's registered `expected` | 24 |
| **D3** | Arm C basis pointer set equals Arm B's hand-curated basis pointer set | 24 |
| **D4** | Arm C disposition, evaluated by the real runtime, equals Arm B's disposition | cells both arms admit |
| **D5** | Arm C admits every cell Arm A lost (`r02-s07`, `r03-s02`, `r03-s05`) | 3 |

D3 is the study's centre. D1 can pass while D3 fails only if the verifier's sufficiency check is
weaker than Arm B's curation; that combination is itself a registered finding about the verifier.

## 6. Registered predictions and thresholds

Registered before implementation:

- **D1 ≥ 22/24** is the success threshold (it must strictly beat Arm A's 21/24 to support the
  contrary interpretation). **Predicted: 24/24.**
- **D2 = 24/24 predicted.** Below 24 falsifies "the portable rule reproduces the registered
  mappings" for this source.
- **D3 = 24/24 predicted**, with a stated mechanism that is the actual object of interest: the rule's
  guard clauses are ordered so that reaching a later clause *requires* evaluating the earlier
  discriminating checks, so the mechanical cumulative read set is expected to coincide with the
  hand-curated load-bearing set — sufficiency emerging from rule **structure** rather than from an
  author's judgement. **The registered risk is that short-circuit evaluation reads strictly fewer
  pointers than the verifier requires** (e.g. a `resolved` cell whose matched clause reads only
  `/status` and `/matchCount` while the verifier requires the subject, freshness, and dated-record
  pointers as well). If that occurs, D1 and D3 fail together and the finding is that **basis
  sufficiency is not derivable from a short-circuit read set** — a real limit on the derivation
  sub-contract, to be reported as the study's result rather than repaired.
- **D5 = 3/3 predicted**, since none of Arm A's three losses (digest transcription, nonexistent
  pointer namespace, incomplete basis) is reachable when the host supplies digests from the receipt
  and pointers from evaluation.

A failure of D2 with a pass of D1 would be the worst outcome and is registered as such: it would mean
removing the model **silently admits a wrong mapping**, which is a stronger argument against Arm C
than any admission-rate gain is for it.

## 7. Scoring

Deterministic and re-runnable. `harness/study.py score` recomputes every endpoint from the retained
per-cell artifacts; no endpoint is computed by hand. Every cell writes its Arm B envelope, Arm C
envelope, verifier findings, and (where admitted) the runtime disposition, so a third party can
recheck each number from the committed files without re-running anything.

Cells are scored all-or-nothing: an envelope is admitted only if the unchanged verifier returns zero
errors.

## 8. What this study cannot establish

Registered in advance, in the Study 007 style:

- Nothing about model behaviour, source discovery, prompt injection, or authoring ergonomics — no
  model runs.
- Not that the portable rule generalizes beyond one source, one fact/evidence pair, one binding, and
  the eight Study 007 scenarios.
- Not independent validation: the rule, the verifier, and this study were all produced by the same
  project, so at best this is **cross-artifact agreement within one project**, which is weaker than
  the independent third-party review the evidence bar requires. The clean-room Go implementation of
  the rule is not exercised here.
- Not that a mechanically-derived basis is *semantically* sufficient for any policy other than the
  one this verifier encodes. Sufficiency is policy-specific (Study 007, challenge 3).
- Not that HMAC receipts, a checked-in fixture key, or a synthetic gateway model production issuer
  identity, key custody, or a real upstream source.
- Not that any admitted envelope is factually correct. The ceiling remains byte-lineage, not truth.
