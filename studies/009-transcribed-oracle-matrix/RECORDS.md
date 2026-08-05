# The registered record table

Synthetic records, derived from POLICY.md by the reasoning in the last
column — never from either pack and never from the evaluator. Sets:
H healthy, F defect class (`sanctionsHit == false AND riskScore == "70"`),
K calibration controls (recorded outcome deliberately wrong). The sets are
pairwise disjoint by id and by predicate.

| caseId | sanctionsHit | riskScore | recorded outcome | set | POLICY.md reasoning |
|---|---|---|---|---|---|
| `h-clear-low` | false | "12.5" | clear | H | P3: no hit, 12.5 < 70. |
| `h-clear-mid` | false | "40" | clear | H | P3: no hit, 40 < 70. |
| `h-clear-boundary-below` | false | "69.99" | clear | H | P3 boundary negative: 69.99 < 70. |
| `h-review-boundary-above` | false | "70.01" | manual-review | H | P2 boundary negative: 70.01 >= 70. |
| `h-review-high` | false | "85" | manual-review | H | P2: no hit, 85 >= 70. |
| `h-reject-plain` | true | "90" | reject | H | P1: sanctions hit. |
| `h-reject-boundary-70` | true | "70" | reject | H | P1 boundary negative: a hit at exactly 70 is rejected under both packs. |
| `f-boundary-1` | false | "70" | manual-review | F | P2: no hit, 70 >= 70. Pack D's greater-than drops exactly this class. |
| `f-boundary-2` | false | "70" | manual-review | F | P2, as f-boundary-1. |
| `f-boundary-3` | false | "70" | manual-review | F | P2, as f-boundary-1. |
| `k-wrong-reject` | false | "10" | reject | K | POLICY says clear (P3); recorded reject on purpose — a suite that cannot fail is not a suite. |
| `k-wrong-clear` | true | "95" | clear | K | POLICY says reject (P1); recorded clear on purpose. |
