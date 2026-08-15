# Contest policy — draft v0.2 (design artifact, not frozen)

**Status: DRAFT v0.2, post-panel and post-reference-build. Both reference implementations
(JPS pack on the pinned jpack 0.17.0; Rego on the pinned OPA 1.19.0) agree with this text
cell-for-cell over the 2,540-cell design grid ([`reference/AGREEMENT.md`](reference/AGREEMENT.md)).
v0.2 adjudicates the one cross-engine divergence the build surfaced (O2 under an
indeterminate O3 — U1 now governs uniformly) and registers one narrow arm-A
inexpressibility class the gold grid must exclude. v0, v0.1's panel findings, and the
reference artifacts are retained beside this file. Not yet through: the clean-room second
oracle, the calibration pilots, or any review round. The frozen version will live at
`policy/POLICY.md`.**

Three panel discoveries reshaped v0, all verified against a built runtime: (1) "unreported
insurance → review" was inexpressible in Core's three-valued logic (a condition true on
`unknown` is true on `present` — Kleene monotonicity), so that branch is now unresolved;
(2) the engine accumulates reason *sets*, and an escalation firing beside a missing-evidence
gate leaks both reasons unless the escalation itself requires evidence — the prose now says
so; (3) "needed by the clauses above" named nothing the engine computes — replaced by an
operational counterfactual rule with worked examples.

---

## Vendor Approval Policy

This policy governs vendor onboarding spend requests. Each request receives exactly one
determination — **approve**, **review**, **enhanced review**, or **reject** — or the case is
**unresolved** where this policy states that no determination can be issued.

### Inputs

Each input is reported in exactly one of the listed states.

- **Risk score**: an integer from 0 to 100, or unreadable.
- **Requested spend**: a US-dollar amount from 0 to 10,000,000.00 (cents precision), or
  unreadable.
- **Sanctions screening result**: CLEAR, MATCH, or UNKNOWN (screening ran but returned no
  result).
- **Country risk**: LOW, MEDIUM, or HIGH, or unreadable.
- **New vendor**: yes, no, or unreported.
- **Critical supplier**: yes, no, or unreported.
- **Prior enforcement action**: yes, no, or unreported.
- **Financial evidence** (audited financial statements on file): available, absent, or
  unreported availability.
- **Insurance certificate**: available, absent, or unreported availability. It is never
  required (P1); it is consulted only by D6b.

### Order of application

Clauses apply in this order: **P1** first; then the overrides **O3**, then **O2**; then the
determination clauses **D1–D8**, as modified by **O1**. **U1** governs cases the clauses
above leave undetermined because an input cannot be read; a determination issued by a clause
that does not depend on the unreadable input stands (U1 states the test). Where more than
one clause yields the same determination, the earliest clause in this order governs.

### Precondition

**P1 — Financial evidence.** No determination of any kind — including a rejection — may be
issued without financial evidence: no other clause of this policy applies unless financial
evidence is available. If financial evidence is **absent**, the case is unresolved for
missing required evidence. If its availability is **unreported**, the case is unresolved as
unknown. No override in this policy displaces P1.

### Determination clauses

**D1 — Sanctions match.** If the screening result is MATCH, the request is **rejected**. D1
depends on no input but the screening result (subject always to P1).

**D2 — Unreported sanctions.** If the screening result is UNKNOWN, no determination clause
of this policy applies, and the case is unresolved because no clause matches. D2 depends on
no input but the screening result (subject always to P1).

*Clauses D3–D8 apply only when the screening result is CLEAR.*

**D3 — Critical risk.** A risk score of 90 or above is **rejected**, whatever the other
inputs, subject to the overrides O2 and O3.

**D4 — Elevated risk in a high-risk country.** Where country risk is HIGH and the risk
score is 70 or above, the request is **rejected**. (With D3: in a HIGH-risk country,
rejection begins at risk 70.)

**D5 — Prior enforcement action.** A vendor with a recorded prior enforcement action (yes)
is **rejected**, whatever the risk score, requested spend, or country risk, subject to the
overrides O2 and O3. An unreported prior-enforcement status is treated as **no**.

*The approval clauses D6 and D7 apply only to vendors with no recorded prior enforcement
action.*

**D6 — Approval, LOW-risk country.** Where country risk is LOW:
- **D6a.** Risk score below 40 and requested spend up to and including $500,000.00:
  **approved**.
- **D6b.** Risk score below 40 and requested spend above $500,000.00 and up to and
  including $2,000,000.00: **approved** if an insurance certificate is available. If the
  certificate is **absent**, the request receives **enhanced review** (D6b decides such
  requests; D8 does not reach them). If its availability is **unreported**, the case is
  unresolved as unknown.
- **D6c.** Risk score of at least 40 and below 70, and requested spend up to and including
  $100,000.00: **approved**. (Subject to suspension under O1.)

**D7 — Approval, MEDIUM-risk country.** Where country risk is MEDIUM: risk score below 40
and requested spend up to and including $100,000.00: **approved**.

**D8 — Review.** Every request with a CLEAR screening result that is not determined by
D3–D7 — including requests removed from D6c by O1 — is referred for **review**. D8 never
determines a case D3–D7 determines.

### Overrides

**O1 — First-engagement suspension.** For new vendors (yes), clause D6c does not apply;
such requests fall to D8. An unreported new-vendor status is treated as **no**.

**O2 — Critical-supplier override.** A critical supplier (yes) with a CLEAR screening
result is never approved or rejected automatically: the determination is **review**. O2
takes precedence over every determination clause D1–D8, including rejection under D3, D4,
and D5 — but O2 never applies when the screening result is MATCH or UNKNOWN (D1 and D2
stand), and never displaces P1 or O3. Where the risk score, requested spend, or country
risk cannot be read, U1 governs O2 cases like any other clause (worked examples 3 and 4).
An unreported critical-supplier status is treated as **no**.

**O3 — Large exposure in a high-risk country.** Where country risk is HIGH, the screening
result is CLEAR, requested spend is above $2,000,000.00, and financial evidence is
available (P1), no automated determination is issued: the case is escalated for human
determination and is unresolved on the ground of escalation. O3 takes precedence over every
clause except P1, including O2 and rejection under D3, D4, and D5. Escalated cases are
directed to the vendor compliance desk (queue `vendor-compliance-desk`).

### Unreadable inputs

**U1.** Where the risk score, requested spend, or country risk cannot be read, the case is
determined as follows: **if every readable value the unreadable input(s) could take would
yield the same determination under the clauses above, that determination is issued;
otherwise no determination is issued and the case is unresolved as unknown.** (The
screening result, evidence availability, and the yes/no statuses are never "unreadable" in
this sense: their unreported states are governed by D2, P1, O1, O2, and D5 directly.)

Worked examples:
1. CLEAR, risk 95, country unreadable, spend 1,000,000.00, no prior action, not critical:
   every country value rejects (D3 alone at LOW/MEDIUM; D3 and D4 at HIGH) → **rejected**.
2. CLEAR, HIGH, risk 50, spend unreadable, not critical: spend up to $2,000,000.00 gives
   review (D8) but above it gives escalation (O3) → **unresolved as unknown**.
3. CLEAR, critical supplier yes, risk unreadable, LOW, spend 100.00: O2 determines the
   case without the risk score, and no readable risk value changes it → **review**.
4. CLEAR, critical supplier yes, country risk and requested spend unreadable, financial
   evidence available: a readable HIGH country with spend above $2,000,000.00 would
   escalate (O3), while every other assignment gives review (O2) — the determinations
   differ → **unresolved as unknown**.

---

## Design notes (not part of the stimulus)

### Clause map v0 → v0.1

C1→P1, C2→D1, C3→D2, C4→D3, C5→D4, C6→D6, C7→D7, C8→D8, C9→O1, C10→O2, C11→O3, C12→U1.
New: D5 (prior enforcement — genuine cross-outcome exclusion), enhanced review (fourth
outcome, D6b's absent branch). Changed semantics: D6b's unreported branch is now unresolved
(v0's "review" was inexpressible — panel jpsExpr #1 / regoFair #2); O3 carries an explicit
evidence conjunct (v0 leaked a two-reason set — regoFair #1); U1 is an operational
counterfactual test (v0's "needed by" admitted two readings — three findings).

### Scored surface (carries into the preregistration)

- E1 scores **kind + outcomeId + reasons only**, as reason **sets**. The `handoff` member
  (state, triggeredBy, and the target) is excluded from every endpoint: the target is not
  in the §8.3 disposition at all, and `handoff.state` is a function of the pack's
  `escalation.triggers` choice, which the prose does not constrain (panel regoFair #5/#13,
  jpsExpr #8/#9). O3's queue name in the prose is routing information, scoreable only at
  the document level, and is not scored.
- The four reachable unresolved reason tokens, verbatim (`missing-required-evidence`,
  `unknown`, `no-match`, `exception-escalation`), are pinned in the shared naming appendix,
  as are the outcome ids (`approve`, `review`, `enhanced-review`, `reject`).
- `applicability` is forbidden by the naming appendix and asserted by the admission layer,
  so the `not-applicable` kind is unreachable and needs no alignment cell.
- Arm C's prescribed convention registers `default decision := UNRESOLVED{no-match}` — the
  only default preserving D2 in all arms; arm A's counterpart is the *prohibition* on
  declaring `fallbackOutcome` (asymmetry-ledger row, B/C-favorable).
- Tri-state encodings, registered in the naming appendix: sanctions is a **present string**
  (UNKNOWN is a value); evidence/insurance availability ride the §8.2 evidence document;
  yes/no statuses and unreadable numerics are **omitted keys**. The canonical grid carries
  no malformed or out-of-range values, asserted at freeze. Wire forms are stated per arm
  suffix: arm A receives decimal strings (risk scale 0, spend scale 2, no leading zeros —
  a value not in that form cannot be read); arms B/C receive JSON numbers via the
  registered projection.

### Feature-coverage matrix (v0.1)

| Design feature | Clause(s) |
|---|---|
| 4 outcomes + unresolved kinds | D1/D3–D8 (outcomes incl. enhanced review); P1, D2, D6b-unreported, O3, U1 (unresolved: missing-required-evidence, unknown, no-match, exception-escalation) |
| 6 numeric thresholds, mixed boundaries | 40, 70, 90 (risk); 100,000.00, 500,000.00, 2,000,000.00 (spend). 2,000,000.00 is inclusive in D6b and exclusive in O3 — the same numeral in both senses |
| Tri-state evidence (§8.2 document) | P1 (required; absent/unreported → two different reasons); D6b (optional, consulted by a rule; its unknown branch is unresolved — the only branch Core admits) |
| Tri-state as ordinary fact string | sanctions CLEAR/MATCH/UNKNOWN (D1/D2) |
| Exception: force-outcome | O2 (`when` excludes MATCH/UNKNOWN; stands under unreadable numerics) |
| Exception: suppress-rule | O1 (suppresses D6c; the correct arm-A encoding needs a second review rule scoped to the suppressed region — panel regoFair #10) |
| Exception: escalate | O3 (with the evidence conjunct; reason `exception-escalation`) |
| Cross-outcome exclusion | D5 vs D6/D7 (approvals must exclude prior=yes or conflict); D8's catch-all cascade |
| no-match reachable / no fallback | D2 (pack must NOT declare `fallbackOutcome`) |
| Unknown-handling | U1's counterfactual rule; D6b-unreported; P1-unreported; unreported statuses treated as "no" (O1/O2/D5) |
| Ladder pinned in prose | Order-of-application section: P1 > O3 > O2 > D1–D8 (as modified by O1); U1; earliest-clause tie-break |

### Panel-verified engine facts the reference build must honor

- §8 evaluates the evidence step, then every exception, then rules; a true `escalate`
  exception fires beside a missing-evidence gate and both reasons are retained — O3's
  evidence conjunct is what restores P1's "no other clause applies" (verified; regoFair #1).
- A compatible forced outcome is produced *without evaluating normal rules* — O2 with
  unreadable risk correctly yields review (verified; jpsExpr #5).
- Suppressing a rule does not falsify its condition inside another rule's negation cascade —
  the naive D8 encoding turns the O1 region into no-match (verified; jpsExpr #4).
- Same-outcome rule overlap is not a conflict (D3∩D4 needs no exclusion); conflict detection
  is neutral-to-A-unfavorable on this policy and the ledger signs it accordingly
  (verified; jpsExpr #10, regoFair #3).
- `onUnknown` assignments are non-uniform (O3 escalate; O1/O2 ignore; the D-rule and D8
  assignments that realize U1's counterfactual rule are fixed at reference-build time — the
  two panel encodings disagree on D8's value, recorded as open item V6).
- Ordered comparisons are defined only over decimal strings; a JSON number or a
  leading-zero string yields `unknown` (verified) — hence the per-arm wire-form statements.

### Reference-build results (2026-08-15; artifacts under `reference/`)

- **V6 RESOLVED.** The D8 catch-all rule carries `onUnknown: escalate`; **every other rule
  carries `ignore`**; exception O3 is `escalate`, O1/O2 and the D5-exclusion suppressions
  `ignore`. Basis: all 2^11 rule assignments enumerated against a §7/§8 simulator validated
  cell-for-cell against the pinned engine (15,240 checked evaluations, 0 disagreements);
  the reference assignment scores 0 mismatches on the grid; the panel's split is explained —
  D8's `onUnknown` is entailed by D8's *structure*, and the negation-cascade shape (S1)
  strictly beats the positive-union shape (S2, 24 grid mismatches). D8 is the single place
  U1's "otherwise" is realized.
- **Registered exclusion X1 (arm-A inexpressibility, census row).** In the class
  {newVendor = yes, 40 ≤ risk < 70, and either country LOW with spend unreadable, or
  country unreadable with spend ≤ $100,000.00}, the prose (via U1) says review but no
  `onUnknown` assignment can make a pack say it (72/236,196 derived cells, 0 rescued by any
  of the 2,048 assignments): the O1 companion rule and D8's cascade both read the
  unreadable input, and an unknown-escalate rule poisons the cell before any candidate is
  collected. **The gold grid must not contain cells of this class**; the exclusion is
  registered, and the class enters the expressiveness census as a measured fragment
  boundary (U1's counterfactual is not fully realizable when a suppression's region-scoped
  companion depends on the unreadable input).
- **Adjudication A1 (the one cross-engine divergence).** v0.1's O2 sentence ("its
  determination stands even where … cannot be read") collided with O3's precedence exactly
  where O3's applicability is indeterminate. v0.2 deletes the sentence; U1 governs
  uniformly (worked example 4). After the one-rung Rego fix, **both references agree
  2,540/2,540** with zero engine errors on either side.
- **Ledger row (B/C-favorable, from the build):** O3's "financial evidence is available
  (P1)" conjunct — the sentence that restores P1's reason purity in arm A — is
  *behaviorally inert* in a Rego ladder (the P1 rung short-circuits first): a prose
  sentence that exists solely to make a correct JPS pack reachable.

### Still open for gold authoring

- **V7**: re-derive the completeness argument mechanically over the gold grid (the
  reference build's 236,196-cell derived-space sweep is evidence, not the registered
  artifact), asserting exactly one governing clause per cell under the earliest-clause
  tie-break, and asserting the X1 exclusion.
- **V8**: re-derive the asymmetry ledger from the two reference implementations (three new
  rows so far: X1, A1's uniform-U1 burden, the inert O3 conjunct; the panel re-signed two
  of v0's rows).
- Gold rows are authored as reason sets, cite governing clauses under the earliest-clause
  tie-break, and deliberately include: every boundary literal in every band; the three U1
  worked examples plus at least one more per unreadable input; D6b's three insurance
  states; the O1-unreported cell; the O2/O3 interaction cells; P1×O3; D5-vs-D6 exclusion
  cells; and the MATCH-with-everything-else-missing cell (P1 first, then D1).
