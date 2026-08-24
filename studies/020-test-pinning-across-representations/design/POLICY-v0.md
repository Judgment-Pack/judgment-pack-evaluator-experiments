# Contest policy — draft v0 (design artifact, not frozen)

**Status: DRAFT v0. This is the candidate stimulus. It has not been through the ambiguity
audit's second oracle, the calibration pilots, or any review round. Clause numbers (C1–C12)
exist so gold rows can cite their governing clause; the frozen version will live at
`policy/POLICY.md` and this draft will remain here as provenance.**

---

## Vendor Approval Policy

This policy governs vendor onboarding spend requests. Each request receives exactly one
determination: **approve**, **review**, or **reject** — or the case is **unresolved** where
this policy states that no determination can be issued.

### Inputs

- **Risk score**: an integer from 0 to 100, from the vendor risk assessment.
- **Requested spend**: a US-dollar amount from 0 to 10,000,000.00, in cents precision.
- **Sanctions screening result**: exactly one of CLEAR, MATCH, or UNKNOWN (unreported).
- **Country risk**: exactly one of LOW, MEDIUM, or HIGH.
- **New vendor**: yes or no — whether this is the group's first engagement with the vendor.
- **Critical supplier**: yes or no — whether the vendor is on the group critical-supplier
  register.
- **Financial evidence**: audited financial statements on file. Availability is reported as
  available, absent, or unknown.
- **Insurance certificate**: a current certificate of insurance. Availability is reported the
  same way. It is never required (C1); it is consulted only where C6b says so.

### Determination clauses

**C1 — Financial evidence precondition.** No determination of any kind — including a
rejection — may be issued without financial evidence. If financial evidence is **absent**,
the case is unresolved for missing required evidence. If its availability is **unknown**, the
case is unresolved as unknown. C1 is checked before every other clause; C2–C11 apply only
when financial evidence is available.

**C2 — Sanctions match.** If the sanctions screening result is MATCH, the request is
**rejected**. C2 does not depend on any input other than the screening result.

**C3 — Unreported sanctions.** If the sanctions screening result is UNKNOWN, no
determination clause of this policy applies, and the case is unresolved because no clause
matches. C3 does not depend on any input other than the screening result.

*Clauses C4–C11 apply only when the sanctions screening result is CLEAR.*

**C4 — Critical risk.** A risk score of 90 or above is **rejected**, whatever the requested
spend and country risk.

**C5 — Elevated risk in a high-risk country.** Where country risk is HIGH and the risk score
is 70 or above, the request is **rejected**. (Together with C4: in a HIGH-risk country,
rejection begins at risk 70.)

**C6 — Approval, LOW-risk country.** Where country risk is LOW:
- **C6a.** Risk score below 40 and requested spend up to and including $500,000.00:
  **approved**.
- **C6b.** Risk score below 40 and requested spend above $500,000.00 but not above
  $2,000,000.00: **approved** only if an insurance certificate is available. If the
  certificate is absent, or its availability is unreported, the request is instead referred
  for **review** under C8.
- **C6c.** Risk score of at least 40 and below 70, and requested spend up to and including
  $100,000.00: **approved**. (Subject to suspension under C9.)

**C7 — Approval, MEDIUM-risk country.** Where country risk is MEDIUM: risk score below 40
and requested spend up to and including $100,000.00: **approved**.

**C8 — Review.** Every request with a CLEAR screening result that is not decided by C4–C7 —
including requests removed from C6c by C9 — is referred for **review**. C8 never overrides
an approval or rejection produced by C4–C7; it decides exactly the CLEAR cases none of them
decides.

### Overrides

**C9 — First-engagement suspension.** For new vendors (new vendor: yes), clause C6c does not
apply; such requests fall to C8. An unreported new-vendor status is treated as **no**.

**C10 — Critical-supplier override.** A critical supplier (critical supplier: yes) with a
CLEAR screening result is never approved or rejected automatically: the determination is
**review**, and this override takes precedence over every determination clause above,
including rejection on risk grounds under C4 and C5. C10 never applies when the screening
result is MATCH (C2 stands) or UNKNOWN (C3 stands). An unreported critical-supplier status
is treated as **no**.

**C11 — Large exposure in a high-risk country.** Where country risk is HIGH, the screening
result is CLEAR, and requested spend is above $2,000,000.00, no automated determination is
issued: the case is **escalated for human determination** and is unresolved on that ground.
C11 takes precedence over every other clause except C1, including C10. Escalated cases are
directed to the vendor compliance desk (queue `vendor-compliance-desk`).

**C12 — Unavailable facts.** Where the risk score, requested spend, or country risk needed
by the clauses above cannot be read, no determination is issued and the case is unresolved
as unknown. (C2 and C3 need only the screening result; a request with a MATCH screening
result is rejected even if every other input is unavailable. Unreported new-vendor and
critical-supplier statuses are handled by C9 and C10, not by C12.)

---

## Design notes (not part of the stimulus)

### Feature-coverage matrix

| Design feature (brief §4.2) | Clause(s) |
|---|---|
| 3 outcomes + unresolved kinds | C2/C4–C8 (outcomes); C1, C3, C11, C12 (unresolved: missing-required-evidence, unknown, no-match, escalation) |
| 6 numeric thresholds, mixed boundaries | 40 (exclusive-below), 70 (inclusive-at), 90 (inclusive-at) on risk; 100,000.00 (inclusive-at), 500,000.00 (inclusive-at / exclusive-above), 2,000,000.00 (inclusive-at / exclusive-above) on spend |
| Tri-state evidence (§8.2 document) | C1 (required financial-evidence: absent → missing-required-evidence; unknown → unknown); C6b (optional insurance-certificate consulted by a rule) |
| Tri-state as ordinary fact string | sanctions CLEAR/MATCH/UNKNOWN (C2/C3); UNKNOWN is just a third value |
| Exception: force-outcome | C10 (force review; `when` excludes MATCH/UNKNOWN so C2/C3 stand) |
| Exception: suppress-rule | C9 (suppresses the C6c rule) |
| Exception: escalate + handoff target | C11 (queue `vendor-compliance-desk`; target scored descriptively only) |
| Precedence via mutual exclusion | C8's "exactly the CLEAR cases none of them decides" forces the negation cascade; C4/C5/C6/C7 region overlaps must be hand-excluded |
| `fallbackOutcome` absent / no-match reachable | C3 (sanctions UNKNOWN matches no clause → no-match; therefore the pack must NOT declare a fallback) |
| Per-rule/exception `onUnknown` | C12 (risk/spend/country unknown → escalate-unknown); C9/C10 (status unknown → ignore, "treated as no"); C6b (insurance unknown → the approve rule does not fire; C8 catches) |
| §8 fixed ladder pinned in prose | C1 before everything; C11 > C10 > determination clauses; C2 > C10 |

### Input-space completeness argument (to be re-derived mechanically at gold time)

Partition: evidence {available, absent, unknown} × sanctions {MATCH, UNKNOWN, CLEAR} ×
country {LOW, MEDIUM, HIGH} × risk bands {<40, 40–69, 70–89, ≥90} × spend bands
{≤100k, (100k, 500k], (500k, 2M], >2M} × overrides {new-vendor, critical-supplier} ∈
{yes, no, unknown}².
- Evidence absent/unknown → C1 decides every cell (unresolved), regardless of the rest.
- Evidence available, MATCH → C2 (reject); UNKNOWN → C3 (no-match) — both total.
- Evidence available, CLEAR: C11 first (HIGH ∧ >2M → escalation), then C10
  (critical=yes → review), then C4/C5 (reject regions), then C6a/C6b/C6c (as modified by
  C9) and C7 (approve regions), then C8 (everything else → review). Every (country, band,
  band) cell lands in exactly one of these by construction; the C6b insurance tri-state
  splits its cell into approve/review/review.
- Risk, spend, or country unreadable where needed → C12 (unknown).

### Registered scales

Risk score: decimal strings of scale 0 ("0" … "100"). Requested spend: decimal strings of
scale 2 ("0.00" … "10000000.00"). Boundary literals: "40", "70", "90", "100000.00",
"500000.00", "2000000.00".

### Ambiguity audit v0 — closed by construction (first pass, single-author; the second
oracle and the panel decide what I missed)

1. C1-before-C2 ordering stated outright (MATCH + no evidence → missing-required-evidence,
   not reject) — pins JPS §8's evidence-before-rules order; Rego must reproduce it.
2. C10-overrides-C4/C5 stated outright (critical + CLEAR + risk 95 → review, not reject) —
   pins the §8 force-outcome-over-rules ladder.
3. C11-overrides-C10 stated outright (HIGH + >2M + critical + CLEAR → escalation) — pins
   escalate-over-force-outcome.
4. C3 is no-match, not review — stated as "no clause applies," and C8 is scoped to CLEAR.
5. Every "up to and including" / "above" / "below" / "of at least" is explicit; no bare
   "over"/"under."
6. Unknown-handling is total: every input's unknown case is assigned (C1, C3, C9, C10, C12,
   C6b).

### Open verification items (for the expressibility critic and the reference pack)

- **V1**: confirm from spec §8 that the evidence step precedes exception evaluation — C1's
  "before every other clause" must mirror the engine's actual order, including C1-vs-C11.
- **V2**: confirm the §8 ladder's behavior when a compatible force-outcome exists while some
  rule reads unknown (C10 with risk unavailable: prose says review — the engine must agree).
- **V3**: confirm Core's condition grammar can express C8's negation cascade (a `not` /
  `all` / `any` combinator set, or not-equals over enum strings) and the negation of
  `evidence-present` for C6b's review side, with three-valued semantics that match the
  prose.
- **V4**: confirm C9 (suppress-rule) composes with C10/C11 as prose states when several
  overrides are simultaneously live.
- **V5**: the "needed by" dependency language in C12 must be checked against how a JPS pack
  actually produces unknown (pointer fails to resolve → condition unknown → onUnknown) so
  prose and engine agree on *which* cells are unknown-unresolved.
