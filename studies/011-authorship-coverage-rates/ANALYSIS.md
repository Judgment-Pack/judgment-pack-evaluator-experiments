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

Two reports §3.2 and S9 register for this document:

- **The recaptured golden against Study 010's.** They differ first at the
  first developer entry — this environment's is length 4024 (normalized
  hash `029b…`) against 010's 4010 (`a17b…`) — and agree on entries 1–3.
  That is the expected shape: the golden pins one environment's codex
  boilerplate, and this study recaptured its own for exactly that reason.
- **S9, the wall clock.** All 50 calls carry clocks (N − M = 0): durations
  39–73 seconds, mean 42.08 seconds, batch span 36 minutes 19 seconds.

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
V = 49 valid runs the study cannot distinguish "always" from "at least
92.75% of the time" (a full 50/50 would have put the bound at 0.9289), and
does not try to. The six predicates are marginal and non-disjoint by
design — class 0 nests inside class 1, class 2 inside class 3 — so the six
rows are six views of the record set, not a partition of it.

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
  49/49 with the same [0.9275, 1.0000] bound. Every **valid** run produced
  exactly 16 accepted records with no drops (run-026's records were never
  compiled — an inadmissible slot has no acceptance to count).
- **Output distinctness — which is not independence:** all 49 completions
  are pairwise distinct (largest identical group: 1) and every slot carries
  a distinct session identity, so the rates are not one output counted many
  times. That is all distinctness can show. Whether the 49 runs are
  statistically independent draws — the premise the binomial reading of
  every Clopper–Pearson interval rests on — is exactly what §7 records as
  unclosed: provider-side cross-session state is not observable from the
  retained bytes, and the drift table can hint at correlation, never rule
  it out.
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
  coverage here may well be a property of the policy's smallness and its
  boundary-forward prose — and the class-5 bytes say so rather than
  otherwise: every one of the 49 valid runs reached the 39 ≤ r < 40 band
  with exactly one record, and its score is `39.99` in 28 runs and
  `39.999` in 21. Those are deliberately authored just-below-40 borderline
  cases, answering the prompt's own instruction about the *stated* 40
  threshold; nothing in the retained bytes shows the author probing the
  family's unstated lower edge at 39. Class-5 coverage is real and counted,
  and it is the prompt-deflation case, not a counterexample to it.
- The mirror is the reference semantics, not ground truth; "correctly
  labelled" means agreement with it — and the agreement is more internal
  than the phrase suggests: the mirror implements the same small policy
  whose full text the authoring prompt supplies, so 784/784 measures how
  reliably the model applies a policy it was just handed, not any
  independent validation of the labels. Coverage means a record fell in a
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

And the ceiling §7 promised this document would repeat: nothing in the
retained artifacts proves these 50 slots are ALL the invocations that
occurred. An operator could run a batch, dislike it, discard it, and
restart — the ledger and the clocks record what this batch did, not that
no other batch existed. The study's integrity rests on ledger discipline
and re-runnability, which is the registered ceiling, stated rather than
implied.

Byte-lineage, not truth: these are frequencies of reaching registered
classes with mirror-concordant labels, counted from retained bytes anyone
can re-score.
