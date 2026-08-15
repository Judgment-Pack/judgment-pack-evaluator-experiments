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
