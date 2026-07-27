# Preregistration — Study 003: how common is the determination escape in qualitative policy?

**Status: FROZEN on the commit that adds this file.** Written before any encoding agent has run.
Deviations go to [`DEVIATIONS.md`](DEVIATIONS.md), never into this file.

## 1. The question

Studies 001 and 002 established a **mechanism**: when a policy sentence needs an expressive device
the JPS format lacks, the judgment that sentence performs is prepared outside the pack —
([RFC 0007](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0007-determination-boundary.md),
E2/E6). They cannot establish a **rate**: both encoded a single decision, hand-picked by the study
authors — Study 002's partly *because* it looked like a clean fit, which biases any rate estimate
toward zero escapes.

This study estimates the rate by **census**: encode *every* separable decision in two complete,
third-party, qualitative policies, and count.

## 2. Census frame — fixed now

**Corpus:** the airline and retail agent policies from τ-bench (MIT, pinned
`1d244f5dca42944b67a379b44bfeb9f5748f189d`): `data/tau2/domains/airline/policy.md` (166 lines) and
`data/tau2/domains/retail/policy.md` (136 lines). Chosen because they are public, real, written by a
third party for a purpose unrelated to JPS, and qualitative in character.

**What counts as a separable decision (the lumping rule, fixed before enumeration bias can act):**
a policy passage that grants, denies, or routes a *distinct request type* under its own stated
conditions. Agent-procedure rules (authenticate first, confirm before acting, one tool call at a
time) are not decisions and are excluded; the exclusions are listed and anyone may re-derive the
inventory from the rule.

**The frozen inventory — 12 decisions:**

| # | Domain | Decision | Policy section |
| --- | --- | --- | --- |
| A1 | airline | May this booking be made? | "Book flight" |
| A2 | airline | May the flights in this reservation be changed? | "Modify flight" → Change flights |
| A3 | airline | May the cabin be changed? | "Modify flight" → Change cabin |
| A4 | airline | May baggage/insurance be modified? | "Modify flight" → Change baggage and insurance |
| A5 | airline | May the passengers be modified? | "Modify flight" → Change passengers |
| A6 | airline | May this reservation be cancelled? | "Cancel flight" |
| A7 | airline | Is the user owed a refund or compensation, and what kind? | "Refunds and Compensation" |
| R1 | retail | May this pending order be cancelled? | "Cancel pending order" |
| R2 | retail | May this order's payment method be modified? | "Modify pending order" → Modify payment |
| R3 | retail | May these items be modified? | "Modify pending order" → Modify items |
| R4 | retail | May this delivered order be returned? | "Return delivered order" |
| R5 | retail | May this delivered order be exchanged? | "Exchange delivered order" |

Exclusions under the rule: airline "Domain Basic" (definitions), booking-flow mechanics that are
procedure rather than decision, retail "Generic action rules" (authentication and confirmation are
preconditions to *acting*, not grounds for an outcome), and both policies' transfer-to-human
meta-rule (it is the escalation target, not a decision).

A6 deliberately re-encodes Study 002's decision **blind, by a different author** — an intra-study
replication point.

## 3. Design — the blinding fix from Study 002

Study 002's brief told its author what the prior study found. This study separates encoding from
measurement so no encoder needs to know the hypothesis:

- **12 encoding agents, one per decision, mutually isolated.** Each receives: its domain's full
  policy text (context), its assigned decision, the JPS specification and schema, and access to the
  `judgment-pack` CLI. Each must not read anything else — not this repository, not the
  specification repository's RFCs, not the other rooms. **The brief is neutral:** encode the
  decision faithfully; the pack must validate; document every fact the pack reads and where it
  would come from; record interpretation ambiguities; and *"if any policy sentence cannot be
  represented in the format, record it verbatim with what you did instead."* No mention of
  studies 001/002, migration, escapes, or rates.
- **Measurement pass, separate agents.** Classifiers receive the packs, the fact ledgers, the
  residue logs, and the taxonomy below, and classify every fact and residue. Two classifiers work
  independently; disagreements are adjudicated and reported as a count.

## 4. Units, denominators, and taxonomy — fixed now

**A fact is *requester-stated*** if the person making the request supplies it directly;
***prepared-data*** if it must be looked up from records but involves no judgment (a stored cabin
class, an order status); ***prepared-determination*** if something upstream must *conclude* it by
applying policy or inspecting structure the pack cannot (Study 001's exception-selection,
Study 002's any-segment-flown).

- **D1 (primary): decisions with ≥ 1 prepared-determination ÷ 12.**
- **D2 (secondary): prepared-determinations ÷ all prepared facts**, pooled and per decision.
- **D3 (secondary): residue sentences** — policy sentences the encoder recorded as inexpressible —
  per decision, classified by device.

**Device taxonomy for every escape and residue:** `arithmetic` · `date-time` ·
`collection-quantification` · `precedence-ordering` · `materiality` · `state-sequencing` ·
`other (described)`. The open category is mandatory to report: Study 002's key finding
(quantification) was not on anyone's list.

**Predictor hypothesis (registered):** escapes concentrate on sentences requiring arithmetic,
date-time comparison, or quantification over collections; decisions whose conditions are entirely
scalar-fact comparisons encode with **zero** prepared determinations. The deliverable is the
predictor's accuracy over the 12 decisions, not just the rate.

## 5. What will be reported regardless

All 12 packs and their validation status (a pack that cannot be completed is a result, not a
failure); the full fact ledgers and residue logs; both classifiers' raw judgments and every
adjudication; D1–D3 with the taxonomy distribution; the predictor's hits and misses; and this
document unedited.

## 6. Honest limits, stated in advance

Two policies from one benchmark suite, written by one team — the census is exhaustive *within* its
frame and says nothing beyond it. Encoding quality varies by author even at fixed model and effort;
the fact ledger discipline is the control, not a guarantee. The classifier taxonomy embeds RFC 0007's
worldview; the `other` category and the published raw ledgers are the checks on it.
