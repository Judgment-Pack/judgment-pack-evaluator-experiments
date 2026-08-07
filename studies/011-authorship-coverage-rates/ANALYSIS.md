# Analysis — Study 011: coverage rates for blinded record authorship

**The registered question was "how often"; the answer, for this cell, is
"every time."** In 49 of 49 valid runs, the authoring call produced a
correctly-labelled record in **every one** of the six pre-committed defect
classes: every per-class coverage rate is 49/49 = 1.000 with an exact
Clopper–Pearson 95% interval of [0.9275, 1.0000], and the mapping registered
before any data assigns every class **LIGHT** review on its single criterion
(lower bound ≥ 0.80). One run of fifty was pipeline-invalid; nothing else
deviated, and `DEVIATIONS.md` is still the empty table.

Every number below recomputes from the retained slots; `RATES.md` is the
scorer's own rendering and `RESULTS.json` carries the integers.

## What ran

The preregistration was frozen by merge `e52925ec` after six review rounds
(`PREREG-REVIEW.md`). The registered pre-batch sequence then ran exactly as
README orders it: the frozen file's digest into the registry; the golden
recapture — two probe calls from fresh isolated homes, contexts agreeing
after normalization on the first attempt — pinned as
`a8a2a735…`; the §6 C7 isolation negative control, under the assent the
registry records, which **failed the golden match at its first context
item** — the registered expectation, demonstrating the gate has power
against home leakage in this environment. The batch then ran 50 sequential
calls, every one exit 0, and the registered scorer admitted 49.

One repository-process error occurred between the freeze and the batch and
is recorded where it happened rather than here: the pre-batch PR merged
while the study's CI job was red (a test that used "the study's golden does
not exist" as its proxy for "a refused derivation writes nothing", broken
by the golden legitimately arriving). The fix asserts the property itself —
bytes unchanged across the refusal — and the operator errors (merging on
no-pending rather than on green; not re-running the suite after the golden
commit) are stated in that PR. No preregistered rule was touched: the test
is not a locked artifact, and the deviation table remains empty.

## The primary endpoint

| class | description (mirror predicate) | c_i | 95% CI | registered tier |
|---|---|---|---|---|
| 0 | boundary: risk exactly 70 | 49/49 | [0.9275, 1.0000] | LIGHT |
| 1 | off-by-one band: 70 ≤ r < 71 | 49/49 | [0.9275, 1.0000] | LIGHT |
| 2 | off-by-one band: P ∧ 40 ≤ r < 41 | 49/49 | [0.9275, 1.0000] | LIGHT |
| 3 | interior band: 40 ≤ r < 70 | 49/49 | [0.9275, 1.0000] | LIGHT |
| 4 | membership literal: registered in SY | 49/49 | [0.9275, 1.0000] | LIGHT |
| 5 | **unstated** interior band: P ∧ 39 ≤ r < 40 | 49/49 | [0.9275, 1.0000] | LIGHT |

Study 010 predicted its plausible misses at indexes 1, 2, 4 and 5 (§10) and
then observed 6/6 coverage in its single draw-protected call. This study's
result says that observation was not luck: for this prompt × this model ×
this policy, blind coverage of every class — including the band the policy
text never states — is the typical outcome, not the fortunate one. At
N = 50 the study cannot distinguish "always" from "at least 92.75% of the
time," and does not try to.

## The one invalid run

`run-026` was admitted by nothing: its pre-prompt context differed from the
locked golden at its first developer item, and the allowlist refuses any
deviation without asking what it means. That is the gate working as
registered — the batch retained the slot, scoring excluded it and named it,
and the pipeline-invalid rate is published: 1/50 = 0.020, 95% CI
[0.0005, 0.1065]. The likely cause is service-side boilerplate variation on
one call; the study deliberately does not look inside a refused transcript
to adjudicate, because an allowlist that starts making exceptions is a
denylist.

## Secondaries, all of them at or about the ceiling

- **Labels:** 784 accepted records, 784 policy-concordant — |H| = 784,
  |Q| = 0, pooled label accuracy 1.000, per-run accuracy 1.000 at min,
  mean, and max. Study 010's authoring-label-failure mode (a class reached
  only by mislabelled records) occurred zero times in any class.
- **Breadth:** every valid run covered all six classes; the all-six rate is
  49/49 with the same [0.9275, 1.0000] bound. Every run produced exactly 16
  accepted records with no drops.
- **Independence of samples:** all 49 completions are pairwise distinct
  (largest identical group: 1) and every capture and slot carries a
  distinct session identity — the rates are not one output counted many
  times.
- **Drift:** class coverage is 1 in every valid run in both batch halves
  (24/24 and 25/25); no order effect is visible, and none is tested for —
  the drift table is descriptive, as registered.

## What this answers, and what it does not

Issue #23's product question was which independently authored matrix rows
need which depth of human review. For this cell, the registered mapping's
answer is LIGHT everywhere, and the scarce resource is plainly **not**
blind boundary coverage — it is the things the intervals still leave room
for: the 2% observed pipeline-invalid rate (upper bound 10.65%), and
whatever a richer policy does to these ceilings.

Stated with the bounds this study registered and no further:

- One prompt, one model, one small synthetic policy whose text names two of
  the three thresholds and whose prompt asks for borderline cases. Ceiling
  coverage here may be a property of the policy's smallness and its
  boundary-forward prose; class 5 — the band the policy never states — being
  covered every time is the one number that resists that deflation.
- The mirror is the reference semantics, not ground truth; "correctly
  labelled" means agreement with it. Coverage means a record fell in a
  class — no pack was evaluated, and nothing here measures defect
  *detection*; Study 010 did that once, by draw.
- The intervals are marginal per class; no simultaneous claim is made. The
  §5 tiers are a registered sketch, not a validated instrument, and the
  operating-characteristics table in §5 says what N = 50 can and cannot
  resolve.
- The rates transfer to nothing outside this cell. A confidence score
  built on them holds for this policy shape and this authoring
  configuration, and the next study on this line, if wanted, varies the
  policy or the model — not this one's conclusions.

Byte-lineage, not truth: these are frequencies of reaching registered
classes with mirror-concordant labels, counted from retained bytes anyone
can re-score.
