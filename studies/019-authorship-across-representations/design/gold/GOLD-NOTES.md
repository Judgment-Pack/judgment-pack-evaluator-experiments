# Gold suite v0 — authoring notes (design draft, 2026-08-15)

76 rows, hand-authored from POLICY-DRAFT.md v0.2 by the maintainer side; the authoring
transport is gold_author.py (the script assembles rows, it derives nothing). Coverage:
every clause cited; every numeric literal witnessed at the literal and adjacent to it;
the registered X1 exclusion respected and asserted by the checker.

check_gold.py (the V7 draft) run of record: 76 rows, 0 failures — including the floor
gate: both pinned engines (jpack 0.17.0 over reference/refA/pack.json; OPA 1.19.0 over
reference/refB/policy.rego) reproduce every hand-authored expectation exactly, on the
first run, with zero adjudicated corrections. That agreement is maintainer-lineage
three ways (prose, gold, references share an author side); the independence instrument
is the clean-room second oracle, whose divergences — if any — are dispositioned in
writing, never edited away.

## Row-count history (the paragraph above describes the v0 suite only)

| Date | Rows | What changed |
|---|---|---|
| 2026-08-15 | **76** | v0, hand-authored from POLICY-DRAFT.md v0.2 |
| 2026-08-15 | **105** | adequacy gate (`mutants/ADEQUACY.md`): 29 prose-derived rows added to kill 56 empty-witness mutants |
| 2026-08-18 | **109** | the X1 repair (`reference/refA/PACK-CHANGE-001.md`, round-1 R1-2): 3 rows in the region the retired X1 class used to forbid, plus 1 adjacency control |

**The X1 exclusion is retired.** `check_gold.py`'s clause (2) no longer forbids a region:
it iterates a `REGISTERED_EXCLUSIONS` registry that is **empty**, and it now *requires* at
least one gold row inside the retired X1 predicate, so the repair cannot silently lose its
witness. The four rows added on 2026-08-18 are `x1r-low-spend-unreadable-40`,
`x1r-low-spend-unreadable-69`, `x1r-country-unreadable-100k` (in the region) and
`x1r-adjacent-both-unreadable` (the control that fails if the repair's region rules are
written any wider — with both country and spend unreadable the determinations differ and
U1 says unknown).

check_gold.py run of record, 2026-08-18: **109 rows, 0 failures**, floor gate included —
both pinned engines reproduce every expectation, the repaired arm-A pack included. The
clean-room oracle (`cleanroom/check_oracle.py`, same day) reproduces **109/109 gold rows
and 2,540/2,540 grid cells with 0 divergences and 0 excused divergences**; every one of
the four new expectations was reproduced by all three instruments on the first run, with
no adjudicated correction.

Gold sha256: `dde57ffe1c8a65d3d50ece3eace33cbca9921fdb70bc761e2b1010a749f3800b`
(105-row predecessor: `df5f93f71c5f67539ffb69467814f230609c8d9bceec012c95381d8a64230c13`).
