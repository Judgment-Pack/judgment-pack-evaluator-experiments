# V8 — the asymmetry ledger, re-derived from the two reference implementations

**Registered obligation** (`design/POLICY-DRAFT.md`, verification row V8; enforced by
`harness/make_manifest.py` since round 7, finding R7-9): re-derive the asymmetry ledger
from the two reference implementations and state its final balance. An asymmetry-ledger
row records a cost one representation pays that the other does not — a cost row, not a
correctness boundary; nothing in this ledger changes any cell's answer.

## The rows

**1. The former X1 region — expressing it costs arm A a derived region lemma.** The prose
never states the lemma; the arm-A reference expresses the region's `review` answer through
`r-o1-wide-low`, a rule derived from the region's shape rather than transcribed from a
clause (`reference/refA/PACK-CHANGE-001.md`). Arm B pays no such cost — the Rego reference
reaches the same answers from the prose's own conditions. Cost row for A.

**2. A1's uniform-U1 burden.** The unreadable-input clause U1 governs uniformly after the
v0.2 adjudication of the one cross-engine divergence the reference build surfaced (O2
under an indeterminate O3). Arm A carries U1 as explicit per-input machinery in the pack;
arm B's projection makes the unreadable case structural. Cost row for A, adjudicated at
design time and carried since v0.2.

**3. The inert O3 conjunct.** The O3 override's condition carries a conjunct that no cell
of the registered space can make decisive; both references retain it because the prose
states it, and deleting it changes no cell's answer. A faithfulness cost paid by both
arms, recorded so a suite that "kills" an edit of it is understood to be measuring the
trace, not the outcome.

**4. The subsumption row — the round-3 adequacy repair's measured price.** Re-stated from
the mechanical derivation in `design/mutants/adequacy_region_lemma_price.json` (sha256
`6f058f765f3fd67384288cd1d39d0467c832d4ae1c4050bd05da4c5cf04a6e2f`), whose figures the
harness suite rebuilds rather than trusts (round-6 finding R6-2). The region lemma
`r-o1-wide-low` strictly contains the O1 companion rule `r-o1-review`; both name `review`,
and D5 suppresses them together — so `r-o1-review` is behaviourally inert in the repaired
reference: deleting it changes no cell's answer, though the deletion is live on the trace
at all 419,904 dense cells. Of the mutants editing it, in the labelled form every
registered surface carries verbatim: **Gross class size: 9; marginal to the X1 repair: 6;
already unkillable before it: 3** (`class: subsumed-region-lemma`; members and the
edit-level derivation in the artifact — matched by edit, never by id, because ids do not
carry across the arm-A reference repair). Not every boundary edit of the rule is
invisible: `m-a-076`, which widens outside the containing region, is killed. A redundant
rule contributes nothing while it is correct and can still do damage when it is wrong.

## The final balance

Three rows are costs arm A pays (1, 2, 4 — the fourth being the measured price of
repairing the first); one is a faithfulness cost both arms pay (3). No row is a
correctness asymmetry: both references agree cell-for-cell over the full derived input
space (`controls/off-gold-equivalence.json`), so every row above is about what the
representation *costs to write and to test*, which is the study's subject, and not about
what it answers — which is the point of keeping the ledger beside the contest rather than
inside it.
