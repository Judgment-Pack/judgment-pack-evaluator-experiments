# Clean-room oracle — numbered decisions (verbatim from the room)

Implementer: Claude (process-isolated room; input = the policy prose plus the
registered interface conventions, nothing else). Transcript: workflow wf_3c5e5675-690.
Ceiling: isolation is a process claim, not a proof; the implementer shares the gold
author's model lineage (registered, with the third-vendor option declined 2026-08-15).

## Decisions (underdetermined readings)

- D-1 — U1's "same determination" test is applied over complete outcomes (disposition plus unresolved ground), not only over the four determinations. Concretely: a sweep in which every readable assignment escalates under O3 issues unresolved/exception-escalation, and a sweep whose assignments split between review and escalation (worked examples 2 and 4) issues unresolved/unknown. Text is underdetermined because U1 speaks of "the same determination" while the policy elsewhere insists escalation is *not* a determination ("no automated determination is issued"), which leaves open what happens when the unreadable input never changes an escalation. Rejected alternative A: only the four determinations can be uniform, so any sweep containing an escalation or other non-determination outcome collapses to unresolved/unknown — this would erase the escalation ground (and its `vendor-compliance-desk` routing) from cases where no readable value avoids O3. Rejected alternative B: hold escalation-uniform sweeps as escalation but treat a uniform D6b-unreported-insurance sweep as a different ground — arbitrary asymmetry. Note the readings are extensionally close: a uniformly-escalating sweep is only reachable when country is readable HIGH and spend is readable above $2M, i.e. when O3 does not depend on the unreadable input, which the Order-of-application sentence ("a determination issued by a clause that does not depend on the unreadable input stands") independently supports.

- D-2 — Requested spend is quantified by interval decomposition rather than exhaustive cents enumeration (1,000,000,001 values). Justification implemented and documented in the module: every clause reads spend only through the comparisons `<= $100,000.00` (D6c, D7), `<= $500,000.00` (D6a), and `<= $2,000,000.00` / `> $2,000,000.00` (D6b, O3), so the outcome is constant on the four cells [0.00, 100000.00], (100000.00, 500000.00], (500000.00, 2000000.00], (2000000.00, 10000000.00]. I probe both endpoints of each cell (8 values: 0.00, 100000.00, 100000.01, 500000.00, 500000.01, 2000000.00, 2000000.01, 10000000.00) rather than one representative, so a mis-signed threshold comparison would still be exercised. Rejected alternative: single midpoint per cell (would not exercise boundary inclusivity). Validated differentially against a dense sample (all thresholds ±2 cents plus 3,000 random cents-precision values) across 5,832 combinations of the remaining inputs — zero outcomes outside the 8-probe set.

- D-3 — O2 (critical supplier yes + CLEAR → review) displaces D6b's *enhanced-review* limb and D6b's *unresolved-as-unknown* limb, not merely approvals and rejections. So critical=yes, CLEAR, LOW, risk 10, spend $1,000,000.00 with insurance absent → review (not enhanced review), and with insurance unreported → review (not unresolved). Underdetermined because O2's rationale sentence is stated narrowly ("is never approved or rejected automatically") while its operative clauses are broad ("the determination is review"; "O2 takes precedence over every determination clause D1–D8") and the Order of application runs O2 before D1–D8 wholesale. Rejected alternative: read the rationale as the scope limit, letting D6b's enhanced review and D6b's unknown survive O2 — rejected because it would make O2 apply *after* D6b in cases where O2 is ordered before it, and because worked example 3 shows O2 deciding the case outright without consulting the risk-score-dependent limbs at all.

- D-4 — Unresolved outcomes always carry exactly one ground token; grounds are never unioned. In particular a U1 sweep whose assignments yield differing unresolved grounds (e.g. some escalation under O3, some unknown under D6b) returns ["unknown"] alone, not ["unknown", "exception-escalation"]. Rejected alternative: accumulate every ground encountered in the sweep. U1's "otherwise ... unresolved as unknown" names a single ground, and worked examples 2 and 4 report only unknown despite escalation appearing in the sweep.

- D-5 — No input validation. Readable values are taken as given and parsed with decimal.Decimal; a risk outside 0–100, a spend outside 0.00–10,000,000.00, or an unlisted literal is neither rejected nor normalised, it simply flows through the comparisons. Missing dict keys are read as None (unreadable/unreported) via `cell.get`. The policy states each input "is reported in exactly one of the listed states", so out-of-domain values are outside its scope; the alternative (raise, or return unresolved) would invent a ground the token list does not contain.

- D-6 — The U1 counterfactual sweeps only the risk score, requested spend, and country risk; every other input is held fixed at its reported state inside the sweep, including unreported insurance availability, which therefore reaches D6b as "unreported" on each assignment rather than being counterfactually varied. Licensed by U1's parenthetical ("The screening result, evidence availability, and the yes/no statuses are never 'unreadable' in this sense") but recorded because the interaction — a numeric sweep running over a clause limb whose own outcome is unresolved — is not worked through in the text. Rejected alternative: vary insurance too, which would make D6b's unreported limb unreachable whenever any numeric is unreadable.

## Readings judged text-determined

- P1 outranks D1: financial evidence absent with sanctions MATCH is unresolved/missing-required-evidence, not reject. "No determination of any kind — including a rejection — may be issued without financial evidence: no other clause of this policy applies unless financial evidence is available." (Reinforced by "No override in this policy displaces P1.")

- P1 is decided before U1 is consulted, and is never subject to the counterfactual sweep. "Clauses apply in this order: P1 first; then the overrides O3, then O2; then the determination clauses D1–D8..." plus U1's "...evidence availability... [is] never 'unreadable' in this sense".

- O3 outranks O2: critical=yes, CLEAR, HIGH, spend $2,000,000.01 → unresolved/exception-escalation, not review. "O3 takes precedence over every clause except P1, including O2 and rejection under D3, D4, and D5."

- O2 outranks D5 and D3/D4: critical=yes with prior enforcement yes, or with risk 95, is review. "O2 takes precedence over every determination clause D1–D8, including rejection under D3, D4, and D5."

- O2 does not fire on a non-CLEAR screening: critical=yes with MATCH is reject, with UNKNOWN is unresolved/no-match. "...but O2 never applies when the screening result is MATCH or UNKNOWN (D1 and D2 stand)..."

- O3 does not fire on a non-CLEAR screening: UNKNOWN + HIGH + $3,000,000.00 is unresolved/no-match, not escalation. "Where country risk is HIGH, the screening result is CLEAR, requested spend is above $2,000,000.00, and financial evidence is available (P1)..."

- Threshold strictness: O3 needs spend strictly above $2,000,000.00, so HIGH + exactly $2,000,000.00 + risk 95 rejects under D3. "...requested spend is above $2,000,000.00..." against D6b's "up to and including $2,000,000.00".

- Risk boundaries: reject at exactly 90 (D3), reject at exactly 70 in HIGH (D4), D6a/D6b/D7 exclude exactly 40, D6c includes exactly 40 and excludes 70. "A risk score of 90 or above is rejected"; "country risk is HIGH and the risk score is 70 or above"; "Risk score below 40"; "Risk score of at least 40 and below 70".

- D6c is LOW-only: MEDIUM country, risk 40–69, spend $100,000.00 is review under D8, not approve. "D7 — Approval, MEDIUM-risk country. Where country risk is MEDIUM: risk score below 40 and requested spend up to and including $100,000.00: approved." (D6's limbs sit under "Where country risk is LOW".)

- O1 suspends D6c only: a new vendor at risk 39 with spend $100,000.00 in a LOW country still approves under D6a. "For new vendors (yes), clause D6c does not apply; such requests fall to D8."

- Unreported yes/no statuses default to no: prior unreported does not reject, critical unreported does not force review, new-vendor unreported does not suspend D6c. "An unreported prior-enforcement status is treated as no."; "An unreported critical-supplier status is treated as no."; "An unreported new-vendor status is treated as no."

- D6b's absent-insurance branch terminates at enhanced review and is not re-routed to D8. "If the certificate is absent, the request receives enhanced review (D6b decides such requests; D8 does not reach them)."

- LOW country, risk below 40, spend above $2,000,000.00 falls to D8 review — no D6 limb covers it and O3 needs HIGH. "Every request with a CLEAR screening result that is not determined by D3–D7 — including requests removed from D6c by O1 — is referred for review."

- Ordering among D3, D4 and D5 is unobservable because all three reject, so no tie-break is implemented. "Where more than one clause yields the same determination, the earliest clause in this order governs."

- D6 and D7 cannot fire for a vendor with prior enforcement action, so D5's rejection is checked before them. "The approval clauses D6 and D7 apply only to vendors with no recorded prior enforcement action."

- A clause that does not read the unreadable input still decides the case: MATCH with risk, spend and country all unreadable is reject. "D1 depends on no input but the screening result (subject always to P1)", plus "a determination issued by a clause that does not depend on the unreadable input stands".

## Implementer notes

Implementation shape: `verdict` applies P1 directly (it depends on no sweepable input), then runs U1 as a counterfactual quantifier around a single `_core` function that evaluates a fully readable case in policy order — O3, O2, D1, D2, then D3, D4, D5, D6a/b/c (with O1 suspending D6c), D7, D8. Readable inputs collapse each sweep axis to a singleton, so the readable case and the unreadable case run through exactly one code path; there is no separate "readable" branch that could drift from the U1 branch.

Cost: worst case 3 countries x 101 risk values x 8 spend probes = 2,424 `_core` evaluations, with early exit as soon as two outcomes disagree. Measured at ~0.34 ms per fully-unreadable call with no early exit; stdlib only, Decimal throughout, no float anywhere.

Verification performed in this room (scratch files, all derived from the policy text alone):
- /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad/test_oracle.py — 36 cases, 36 passing. Includes all four worked examples reproduced exactly (rejected / unknown / review / unknown), P1 over D1, O3 over O2 and over D3+D5, O2 over D3/D5/D6b, every threshold boundary at and one cent or one point either side, O1 on and off D6c, and the three unreported-status defaults.
- /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad/test_interval.py — differential validation of D-2: for 5,832 combinations of the non-spend inputs, the outcome set produced by the 8 spend probes is a superset of the outcome set produced by a dense spend sample (all thresholds ±2 cents plus 3,000 random cents-precision draws) — 0 mismatches. A second pass recomputes the full `verdict` for spend-unreadable cells against a brute-force U1 reference over the dense sample — 0 mismatches.

Residual exposure a reviewer should look at first: D-3 (whether O2 swallows D6b's enhanced-review and unknown limbs) is the reading with the widest behavioural footprint — it changes the disposition of every critical-supplier case in the D6b band. D-1 is the reading most likely to be contested but has the narrowest footprint, since the escalation-uniform sweeps it governs are exactly the ones where O3 does not read the unreadable input, which the Order-of-application sentence decides the same way.
