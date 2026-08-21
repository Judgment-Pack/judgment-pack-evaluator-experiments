# Study 019 — REGISTERED

R1: R1 inconclusive - control gate failed

## Decision

| Row | Registered text | Matched |
|---|---|---|
| 1 pipeline-invalid | Any pin/schema/manifest failure, or apparatus failure making the batch non-terminal | no |
| 2 shortfall-declared | A declared short batch: every level verdict is UNRESOLVED-BY-DESIGN and no contrast is computed | no |
| 3 control-gate-failed | Any control-gate failure (reference-vs-gold imperfect at attempt time; capabilities canary passes; golden-context gate; per-arm timeout rate > cap; E1 floor breached) | **yes** |
| 4 decided | A-C interval excludes zero -> R1 decided, direction as observed; then A-B likewise | no |
| 5 indeterminate | Otherwise -> INDETERMINATE; no claim in any direction is licensed | no |

Causes: e1-floor

## E4 — high-kill run rate (primary)

The high-kill cut is PER LANGUAGE, each from its own paired adequate denominator: jps a run is high-kill iff it kills at least 66 of the 69 paired adequate mutants (tau = 19/20); rego a run is high-kill iff it kills at least 59 of the 62 paired adequate mutants (tau = 19/20)

Pairing: 157 witness groups in total, of which 33 are shared and non-degenerate (1 degenerate), covering 69 paired adequate JPS and 62 paired adequate Rego mutants.

| Arm | Language | Cut | High-kill | Denominator | Rate | 95% CI | Identity pass | Out-of-domain cases |
|---|---|---|---|---|---|---|---|---|
| A | jps | 66 | 0 | 38 | 0.0000 | — | 34 | 0 |
| B | rego | 59 | 0 | 37 | 0.0000 | — | 26 | 0 |
| C | rego | 59 | 0 | 39 | 0.0000 | — | 28 | 0 |

## E1 — gold agreement (control, expected at ceiling)

| Arm | Perfect | Runs | Rate | Floor held |
|---|---|---|---|---|
| A | 0 | 38 | 0.0000 | **no** |
| B | 8 | 37 | 0.2162 | **no** |
| C | 14 | 39 | 0.3590 | **no** |

## The registered contrasts (fixed-sequence: A−C, then A−B)

**Not computed and not published.** 1 gating row(s) matched above §5's substantive rows, and each adjudicates R1 in NEITHER direction — so no contrast, no interval and no direction exists for this attempt:

- control-gate-failed: e1-floor

## E2 — authoring-validity profile

| Arm | Code | Side | Count |
|---|---|---|---|
| A | no-marker-block | authoring | 2 |
| A | unparseable-artifact | authoring | 0 |
| A | v0-syntax | authoring | 0 |
| A | schema-invalid-pack | authoring | 0 |
| A | opa-check-failed | authoring | 0 |
| A | unreadable-output-shape | authoring | 0 |
| B | no-marker-block | authoring | 0 |
| B | unparseable-artifact | authoring | 7 |
| B | v0-syntax | authoring | 0 |
| B | schema-invalid-pack | authoring | 0 |
| B | opa-check-failed | authoring | 4 |
| B | unreadable-output-shape | authoring | 0 |
| C | no-marker-block | authoring | 0 |
| C | unparseable-artifact | authoring | 2 |
| C | v0-syntax | authoring | 0 |
| C | schema-invalid-pack | authoring | 0 |
| C | opa-check-failed | authoring | 9 |
| C | unreadable-output-shape | authoring | 0 |

## E5 — interpretive-spread census (descriptive)

Stimulus: the gold-row input set (117 gold inputs). No tradeoff statement combining these rows with the E4 rates is licensed (section 9).

| Arm | Runs | Distinct encodings | Minimal covering set |
|---|---|---|---|
| A | 36 | 28 | 28 |
| B | 30 | 9 | 9 |
| C | 30 | 9 | 9 |

## The sealed reviewer mutant set (§1a, reported separately)

Manifest sha256:6bff7f950b132505d1034fe7d993a8920f028647b35dc1f48d9072884fedaa0e; 6 reviewer mutants. §1a: scored as authored, reported separately, moving nothing. No number in this block enters E1-E5, any control gate, any contrast, or the decision rule.

| Arm | Language | Reviewer mutants | Scored runs |
|---|---|---|---|
| A | jps | 3 | 34 |
| B | rego | 3 | 26 |
| C | rego | 3 | 28 |

## R2 — refusals published rather than estimated

- **contrast** — not computed: 1 gating row(s) matched above the substantive rows (control-gate-failed: e1-floor). §5's row 2 adjudicates R1 in neither direction, and a direction computed and then withheld is a direction published
- **intervals** — §5: no inferential quantity is computed at or above row 3; 1 gating row(s) matched (control-gate-failed: e1-floor)
